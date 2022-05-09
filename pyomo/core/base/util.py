#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2008-2022 National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

#
# Utility functions
#
import inspect

from pyomo.common.deprecation import relocated_module_attribute
from pyomo.core.base.indexed_component import normalize_index

relocated_module_attribute(
    'disable_methods', 'pyomo.core.base.disable_methods.disable_methods',
    version='6.1')
relocated_module_attribute(
    'Initializer', 'pyomo.core.base.initializer.Initializer',
    version='6.1')
relocated_module_attribute(
    'IndexedCallInitializer', 'pyomo.core.base.initializer.Initializer',
    version='6.1')
relocated_module_attribute(
    'CountedCallInitializer', 'pyomo.core.base.initializer.Initializer',
    version='6.1')
relocated_module_attribute(
    'flatten_tuple', 'pyomo.common.indexing',
    version='TBD')


def is_functor(obj):
    """
    Returns true iff obj.__call__ is defined.
    """
    return inspect.isfunction(obj) or hasattr(obj,'__call__')
