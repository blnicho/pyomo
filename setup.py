#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2008-2024
#  National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________

import os
import platform
import sys
import toml
from setuptools import setup, find_packages, Command

def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as README:
        # Strip all leading badges up to, but not including the COIN-OR
        # badge so that they do not appear in the PyPI description
        while True:
            line = README.readline()
            if 'COIN-OR' in line:
                break
            if line.strip() and '[![' not in line:
                break
        return line + README.read()

def import_pyomo_module(*path):
    _module_globals = dict(globals())
    _module_globals['__name__'] = None
    _source = os.path.join(os.path.dirname(__file__), *path)
    with open(_source) as _FILE:
        exec(_FILE.read(), _module_globals)
    return _module_globals

def get_version():
    # Source pyomo/version/info.py to get the version number
    return import_pyomo_module('pyomo', 'version', 'info.py')['__version__']

def check_config_arg(name):
    if name in sys.argv:
        sys.argv.remove(name)
        return True
    if name in os.getenv('PYOMO_SETUP_ARGS', '').split():
        return True
    return False

CYTHON_REQUIRED = "required"
if not any(
    arg.startswith(cmd)
    for cmd in ('build', 'install', 'bdist', 'wheel')
    for arg in sys.argv
):
    using_cython = False
elif sys.version_info[:2] < (3, 11):
    using_cython = "automatic"
else:
    using_cython = False
if check_config_arg('--with-cython'):
    using_cython = CYTHON_REQUIRED
if check_config_arg('--without-cython'):
    using_cython = False

ext_modules = []
if using_cython:
    try:
        if platform.python_implementation() != "CPython":
            raise RuntimeError("Cython is only supported under CPython")
        from Cython.Build import cythonize
        import shutil

        files = [
            "pyomo/core/expr/numvalue.pyx",
            "pyomo/core/expr/numeric_expr.pyx",
            "pyomo/core/expr/logical_expr.pyx",
            "pyomo/core/util.pyx",
            "pyomo/repn/standard_repn.pyx",
            "pyomo/repn/plugins/cpxlp.pyx",
            "pyomo/repn/plugins/gams_writer.pyx",
            "pyomo/repn/plugins/baron_writer.pyx",
            "pyomo/repn/plugins/ampl/ampl_.pyx",
        ]
        for f in files:
            shutil.copyfile(f[:-1], f)  # Copy .pyx files from .py files
        ext_modules = cythonize(files, compiler_directives={"language_level": 3})
    except Exception as e:
        if using_cython == CYTHON_REQUIRED:
            print(
                """
ERROR: Cython was explicitly requested with --with-cython, but cythonization
       of core Pyomo modules failed.
"""
            )
            raise
        using_cython = False

class DependenciesCommand(Command):
    """Custom setuptools command to list dependencies."""
    description = "list the dependencies for this package"
    user_options = [('extras=', None, 'extra targets to include')]

    def initialize_options(self):
        self.extras = None

    def finalize_options(self):
        if self.extras is not None:
            self.extras = [e.strip() for e in self.extras.split(',')]

    def run(self):
        # Load the pyproject.toml file
        pyproject_data = toml.load("pyproject.toml")
        project = pyproject_data.get("project", {})
        install_requires = project.get("dependencies", [])
        extras_require = project.get("optional-dependencies", {})

        deps = list(self._print_deps(install_requires))
        if self.extras is not None:
            for e in self.extras:
                if e in extras_require:
                    deps.extend(self._print_deps(extras_require[e]))
                else:
                    print(f"Warning: Extra '{e}' not found in optional dependencies.")
        print(' '.join(deps))

    def _print_deps(self, deplist):
        for entry in deplist:
            yield entry.strip()

setup_kwargs = dict(
    name='pyomo',
    version=get_version(),  # Note: the release number is set in pyomo/version/info.py
    cmdclass={'dependencies': DependenciesCommand},
    packages=find_packages(exclude=("scripts",)),
    package_data={
        "pyomo.contrib.ampl_function_demo": ["src/*"],
        "pyomo.contrib.appsi.cmodel": ["src/*"],
        "pyomo.contrib.mcpp": ["*.cpp"],
        "pyomo.contrib.pynumero": ['src/*', 'src/tests/*'],
        "pyomo.contrib.viewer": ["*.ui"],
        "pyomo.contrib.simplification.ginac": ["src/*.cpp", "src/*.hpp"],
    },
    entry_points="""
    [console_scripts]
    pyomo = pyomo.scripting.pyomo_main:main_console_script

    [pyomo.command]
    pyomo.help = pyomo.scripting.driver_help
    pyomo.viewer=pyomo.contrib.viewer.pyomo_viewer
    """,
)

if __name__ == "__main__":
    setup(**setup_kwargs)
