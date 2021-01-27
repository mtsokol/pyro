# Copyright (c) 2017-2019 Uber Technologies, Inc.
# SPDX-License-Identifier: Apache-2.0

import torch
from torch.distributions.constraints import *  # noqa F403
from torch.distributions.constraints import Constraint
from torch.distributions.constraints import __all__ as torch_constraints


# TODO move this upstream to torch.distributions
class _Integer(Constraint):
    """
    Constrain to integers.
    """
    is_discrete = True

    def check(self, value):
        return value % 1 == 0

    def __repr__(self):
        return self.__class__.__name__[1:]


class _Sphere(Constraint):
    """
    Constrain to the Euclidean sphere of any dimension.
    """
    event_dim = 1
    reltol = 10.  # Relative to finfo.eps.

    def check(self, value):
        eps = torch.finfo(value.dtype).eps
        try:
            norm = torch.linalg.norm(value, dim=-1)  # torch 1.7+
        except AttributeError:
            norm = value.norm(dim=-1)  # torch 1.6
        error = (norm - 1).abs()
        return error < self.reltol * eps * value.size(-1) ** 0.5

    def __repr__(self):
        return self.__class__.__name__[1:]


class _OrderedVector(Constraint):
    """
    Constrains to a real-valued tensor where the elements are monotonically
    increasing along the `event_shape` dimension.
    """
    event_dim = 1

    def check(self, value):
        if value.ndim == 0:
            return torch.tensor(False, device=value.device)
        elif value.shape[-1] == 1:
            return torch.ones_like(value[..., 0], dtype=bool)
        else:
            return torch.all(value[..., 1:] > value[..., :-1], dim=-1)


integer = _Integer()
ordered_vector = _OrderedVector()
sphere = _Sphere()
corr_cholesky_constraint = corr_cholesky  # DEPRECATED

__all__ = [
    'integer',
    'ordered_vector',
    'sphere',
]

__all__.extend(torch_constraints)
__all__ = sorted(set(__all__))
del torch_constraints


# Create sphinx documentation.
__doc__ = """
    Pyro's constraints library extends
    :mod:`torch.distributions.constraints`.
"""
__doc__ += "\n".join([
    """
    {}
    ----------------------------------------------------------------
    {}
    """.format(
        _name,
        "alias of :class:`torch.distributions.constraints.{}`".format(_name)
        if globals()[_name].__module__.startswith("torch") else
        ".. autoclass:: {}".format(_name if type(globals()[_name]) is type else
                                   type(globals()[_name]).__name__)
    )
    for _name in sorted(__all__)
])
