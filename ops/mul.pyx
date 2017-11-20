import cython
from cython.parallel import prange, parallel
from libc.math cimport floor
import numpy as np
cimport numpy as np
ctypedef fused DTYPE_t:
    np.float32_t
    np.float64_t
@cython.boundscheck(False)
def mul(np.ndarray[DTYPE_t, ndim=2] a, np.ndarray[DTYPE_t, ndim=2] b, int add_bit, int mul_bit):
    cdef int row_len = a.shape[0]
    cdef int col_len = b.shape[1]
    cdef int row, col, inner
    cdef np.ndarray[DTYPE_t, ndim=2] product = np.zeros([row_len, col_len])
    with nogil:
        for row in prange(row_len, schedule='static'):
            for col in range(col_len):
                for inner in range(a.shape[1]):
                    product[row, col] = floor((product[row, col]
                                                  + floor(a[row, inner] * b[inner, col] * (2**mul_bit)) / (2**mul_bit))\
                                                    * (2**add_bit)) / (2**add_bit)

    return product
