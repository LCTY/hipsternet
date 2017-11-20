# from distutils.core import setup
# from Cython.Build import cythonize
# import numpy
#
# setup(
#    ext_modules=cythonize("mul.pyx"),
#    include_dirs=[numpy.get_include()]
# )
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy
ext_modules = [
    Extension(
        "mul",
        ["mul.pyx"],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp'],
    )
]

setup(
    name='hello-parallel-world',
    ext_modules=cythonize(ext_modules),
    include_dirs=[numpy.get_include()]
)