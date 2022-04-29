#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2008-2022 National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

from pyomo.common.numeric_types import native_types

from collections.abc import Sequence

sequence_types = {tuple, list}
def normalize_index(x):
    """Normalize a component index.

    This flattens nested sequences into a single tuple.  There is a
    "global" flag (normalize_index.flatten) that will turn off index
    flattening across Pyomo.

    Scalar values will be returned unchanged.  Tuples with a single
    value will be unpacked and returned as a single value.

    Returns
    -------
    scalar or tuple

    """
    if x.__class__ in native_types:
        return x
    elif x.__class__ in sequence_types:
        # Note that casting a tuple to a tuple is cheap (no copy, no
        # new object)
        x = tuple(x)
    else:
        x = (x,)

    x_len = len(x)
    i = 0
    while i < x_len:
        _xi_class = x[i].__class__
        if _xi_class in native_types:
            i += 1
        elif _xi_class in sequence_types:
            x_len += len(x[i]) - 1
            # Note that casting a tuple to a tuple is cheap (no copy, no
            # new object)
            x = x[:i] + tuple(x[i]) + x[i + 1:]
        elif issubclass(_xi_class, Sequence):
            if issubclass(_xi_class, str):
                # This is very difficult to get to: it would require a
                # user creating a custom derived string type
                native_types.add(_xi_class)
                i += 1
            else:
                sequence_types.add(_xi_class)
                x_len += len(x[i]) - 1
                x = x[:i] + tuple(x[i]) + x[i + 1:]
        else:
            i += 1

    if x_len == 1:
        return x[0]
    return x

# Pyomo will normalize indices by default
normalize_index.flatten = True


def flatten_tuple(x):
    """
    This wraps around normalize_index. It flattens a nested sequence into 
    a single tuple and always returns a tuple, even for single
    element inputs.
    
    Returns
    -------
    tuple

    """
    x = normalize_index(x)
    if isinstance(x, tuple):
        return x
    return (x,)
