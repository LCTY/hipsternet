from ops.mul import mul
import numpy as np

a = np.array([[4,4],[4,4]],dtype=np.float64)
print(a.shape)
b = np.array([[1,2],[4,1]],dtype=np.float64)
out,max,min =mul(a,b,4,4)
print(out,max,min)