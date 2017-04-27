"""
Implementation of the Dirichlet distribution prior.

Copyright (C) 2017, Lucas Ondel

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

"""

import theano
import theano.tensor as T
import numpy as np
from .efd import EFDPrior


def _log_partition_symfunc():
    natural_params = T.matrix()
    log_Z = T.sum(T.gammaln(natural_params + 1.), axis=1) -\
        T.gammaln(T.sum(natural_params + 1, axis=1))

    func = theano.function([natural_params], log_Z)
    grad_func = theano.function([natural_params],
                                T.grad(T.sum(log_Z), natural_params))
    return func, grad_func



_log_partition_func, _grad_log_partition_func = _log_partition_symfunc()


class Dirichlet(EFDPrior):
    """Dirichlet Distribution."""

    def __init__(self, prior_counts):
        self._natural_params = np.asarray(prior_counts - 1, dtype=float)
        self._build()

    def _build(self):
        natp_mat = self._natural_params[np.newaxis, :]
        self._log_partition = _log_partition_func(natp_mat)[0]
        self._grad_log_partition = \
            _grad_log_partition_func(natp_mat)[0]

    # PersistentModel interface implementation.
    # -----------------------------------------------------------------

    def to_dict(self):
        return {'natural_params': self._natural_params}

    @staticmethod
    def load_from_dict(model_data):
        model = Dirichlet.__new__(Dirichlet)
        model._natural_params = model_data['natural_params']
        model._build()
        return model

    # EFDPrior interface implementation.
    # -----------------------------------------------------------------

    @property
    def natural_params(self):
        return self._natural_params

    @natural_params.setter
    def natural_params(self, value):
        self._natural_params = value
        natp_mat = self._natural_params[np.newaxis, :]
        self._log_partition = _log_partition_func(natp_mat)[0]
        self._grad_log_partition = \
            _grad_log_partition_func(natp_mat)[0]

    @property
    def log_partition(self):
        return self._log_partition

    @property
    def grad_log_partition(self):
        return self._grad_log_partition

    def evaluate_log_partition(self, natural_params):
        return _log_partition_func(natural_params)

    # ------------------------------------------------------------------

