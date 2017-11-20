python3 setup.py build_ext -inplace
rm -rf build/*
rm -f mul.cpython-35m-x86_64-linux-gnu.so
mkdir -p build/temp.linux-x86_64-3.5/
gcc -pthread -B /opt/anaconda3/compiler_compat -Wl,--sysroot=/ -Wsign-compare -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes -fPIC -I/opt/anaconda3/lib/python3.5/site-packages/numpy/core/include -I/opt/anaconda3/include/python3.5m -c mul.c -o build/temp.linux-x86_64-3.5/mul.o -fopenmp
gcc -pthread -shared -L/opt/anaconda3/lib -B /opt/anaconda3/compiler_compat -Wl,-rpath=/opt/anaconda3/lib -Wl,--no-as-needed -Wl,--sysroot=/ build/temp.linux-x86_64-3.5/mul.o -L/opt/anaconda3/lib -lpython3.5m -o /home/lcty/hipsternet/ops/mul.cpython-35m-x86_64-linux-gnu.so -fopenmp

