import numpy as np
import time
from ops.mul import mul
from pycuda import driver, compiler, gpuarray, tools

# -- initialize the device
import pycuda.autoinit


np.random.seed(1)
a = np.zeros((1000, 90), dtype=np.float64)
a[:] = np.random.randn(*a.shape)
b = np.zeros((90, 100), dtype=np.float64)
b[:] = np.random.randn(*b.shape)


ts = time.time()
gpu_result = mul(a, b,8,8)
te = time.time()
print(te - ts)

ts = time.time()
cpu_result = np.dot(a, b)
te = time.time()
print(te - ts)
# print(gpu_result[0][0])
print(cpu_result[0][0])
# print(np.allclose(gpu_result, cpu_result))
