# -*- coding: utf-8 -*-
# -*- mode: python -*-

from nose.tools import assert_equal, assert_true, assert_almost_equal
import numpy as np

from mat_neuron import core
dt = 1.0
state = [0, 0, 0, 0, 0, 0]


def test_impulse_matrix():
    params = [10, 2, 0, 5, 10, 10, 11, 200, 5, 2]
    Aexp = core.impulse_matrix(params, dt)
    assert_equal(Aexp.shape, (5, 5))
    Adiag = np.diag(Aexp)
    assert_almost_equal(Adiag[0], np.exp(- dt / params[5]))
    assert_almost_equal(Adiag[1], np.exp(- dt / params[6]))
    assert_almost_equal(Adiag[2], np.exp(- dt / params[7]))
    assert_almost_equal(Adiag[3], np.exp(- dt / params[8]))
    assert_almost_equal(Adiag[4], np.exp(- dt / params[8]))


def test_step_response():
    params = [10, 2, 0, 5, 10, 10, 10, 200, 5, 2]
    I = np.zeros(1000, dtype='d')
    I[200:] = 0.55
    Y, S = core.predict(state, params, I, dt)

    assert_almost_equal(Y[-1,0], I[-1] * params[5], msg="incorrect steady-state voltage")
    T = np.asarray([231, 510, 833])
    assert_true(all(T == S))


def test_phasic_response():
    params = np.asarray([10, 2, -0.3, 5, 10, 10, 10, 200, 5, 2])
    I = np.zeros(2000, dtype='d')
    I[200:] = 0.5
    Y, S = core.predict(state, params, I, dt)
    assert_almost_equal(Y[-1,0], I[-1] * params[5], msg="incorrect steady-state voltage")
    assert_equal(len(S), 1)
    assert_true(S[0] == 213)


def test_poisson_spiker():
    params = [10, 2, 0, 5, 10, 10, 10, 200, 5, 2]
    I = np.zeros(2000, dtype='d')
    I[500:1500] = 0.5
    core.random_seed(1)
    Y, S1 = core.predict(state, params, I, dt, stochastic=True)
    core.random_seed(1)
    Y, S2 = core.predict(state, params, I, dt, stochastic=True)
    assert_almost_equal(S1, S2)


def test_softmax_spiker():
    params = [10, 2, 0, 5, 10, 10, 10, 200, 5, 2]
    I = np.zeros(2000, dtype='d')
    I[500:1500] = 0.5
    core.random_seed(1)
    Y, S1 = core.predict(state, params, I, dt, stochastic="softmax")
    core.random_seed(1)
    Y, S2 = core.predict(state, params, I, dt, stochastic="softmax")
    assert_almost_equal(S1, S2)


def test_predict_voltage():
    params = np.asarray([10, 2, 0, 5, 10, 10, 10, 200, 5, 2])
    I = np.zeros(2000, dtype='d')
    I[500:1500] = 0.5
    Y, S = core.predict(state, params, I, dt)
    V = core.predict_voltage(state, params, I, dt)

    assert_true(all(np.abs(Y[:,0] - V[:,0]) < 1e-6))
    assert_true(all(np.abs(Y[:,3] - V[:,1]) < 1e-6))
    assert_true(all(np.abs(Y[:,4] - V[:,2]) < 1e-6))


def test_predict_adaptation_sparray():
    params = np.asarray([10, 2, 0, 5, 10, 10, 10, 200, 5, 2])
    I = np.zeros(2000, dtype='d')
    I[500:1500] = 0.5
    Y, S = core.predict(np.asarray(state), params, I, dt)
    spk = np.zeros(I.size, dtype='i')
    spk[S] = 1
    H = core.predict_adaptation(state, params, spk, dt)

    # have to blank out the bins with spikes because predict_adaptation is a
    # causal filter, and the normal prediction operation is not

    assert_true(all(np.abs(Y[~spk,1] - H[~spk,0]) < 1e-6))
    assert_true(all(np.abs(Y[~spk,2] - H[~spk,1]) < 1e-6))


def test_likelihood():
    I = np.zeros(2000, dtype='d')
    I[500:1500] = 0.5

    params_true = np.asarray([10, 2, 0, 5, 10, 10, 10, 200, 5, 2])
    Y_true, S_obs = core.predict(state, params_true, I, dt)

    V_true = core.predict_voltage(state, params_true, I, dt)
    H_true = core.predict_adaptation(state, params_true, S_obs, dt, I.size)
    lci_true = core.log_intensity(V_true, H_true, params_true)

    params_guess = np.asarray([-50, -5, -5, 0, 10, 10, 10, 200, 5, 2])
    V_guess = core.predict_voltage(state, params_guess, I, dt)
    H_guess = core.predict_adaptation(state, params_guess, S_obs, dt, I.size)
    lci_guess = core.log_intensity(V_guess, H_guess, params_guess)

    ll_true = np.sum(lci_true[S_obs]) - np.sum(np.exp(lci_true))
    ll_guess = np.sum(lci_guess[S_obs]) - np.sum(np.exp(lci_guess))

    assert_true(ll_true > ll_guess)
