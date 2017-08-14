# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
This module provides functions for integrating the MAT model
"""
from __future__ import division, print_function, absolute_import
import numpy as np

# import random_seed function so user can set seed
from mat_neuron._model import random_seed, lci_poisson, impulse_matrix


def predict(state, params, current, dt, upsample=1, stochastic=False):
    """Integrate model to predict spiking response

    This method uses the exact integration method of Rotter and Diesmann (1999).
    Note that this implementation implicitly represents the driving current as a
    series of pulses, which may or may not be appropriate.

    parameters: 10-element sequence (α1, α2, β, ω, τm, R, τ1, τ2, τV, tref)
    state: 5-element sequence (V, θ1, θ2, θV, ddθV) [all zeros works fine]
    current: a 1-D array of N current values
    dt: time step of forcing current, in ms

    Returns an Nx5 array of the model state variables and a list of spike
    indices (multiply by dt to get times)

    """
    from mat_neuron import _model
    if not stochastic:
        fun = _model.predict
    elif stochastic == "softmax":
        fun = _model.predict_softmax
    else:
        fun = _model.predict_poisson
    return fun(state, params, current, dt, upsample)


def predict_voltage(state, params, current, dt, upsample=1):
    """Integrate just the current-dependent variables.

    This function is usually called as a first step when evaluating the
    log-likelihood of a spike train. Usually there are several trials for each
    stimulus, so it's more efficient to predict the voltage and its derivative
    from the current separately.

    See predict() for specification of params and state arguments.

    Returns an Nx3 array of the model state variables (V, θV, ddθV)

    """
    from mat_neuron import _model
    return _model.predict_voltage(state, params, current, dt, upsample)


def predict_adaptation(state, params, spikes, dt):
    """Predict the voltage-independent adaptation variables from known spike times.

    This function is usually called as a second step when evaluating the
    log-likelihood of a spike train. In order for estimation to work, this
    filter has to be *causal*, so the adaptation variables are not affected
    until the following time bin.

    See predict() for specification of params and state arguments.

    `spikes`: a sequence of times (i.e., int(t / dt)) or an array of 0's and 1's.
    `N`: must be not None if `spikes` is a sequence of times

    """
    from mat_neuron import _model
    return _model.predict_adaptation(state, params, spikes, dt)


def log_intensity(V, H, params):
    """Evaluate the log conditional intensity, (V - H - omega)

    V: 2D array with voltage, current and θV in the first three columns
    H: 2D array with θ1 and θ2 in the first two columns
    params: list of parameters (see predict() for specification)

    """
    from mat_neuron import _model
    return _model.log_intensity(V, H, params)
