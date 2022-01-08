import numpy as np
import scipy
import ctypes
import os
from helpers import *

"""problem dimensions"""
n = 5 # number of variables
m = 4 # number of constraints

"""Uncomment below to try new inputs"""

# P = np.random.random((n,n))
# P = P.T @ P
# A = np.eye(m,n)
# q = np.random.random(n)
# l = -np.random.random(m)
# u = np.random.random(m)

# print(P)
# print(A)
# print(q)
# print(l)
# print(u)


"""or use these hard-coded values"""

P = np.array([[1.63729889, 1.49800623, 0.66972223, 1.16520369, 1.00871733],
 [1.49800623, 2.30753699, 1.00125695, 1.29220823, 1.59194631],
 [0.66972223, 1.00125695, 1.16973938, 0.60180993, 0.81632789],
 [1.16520369, 1.29220823, 0.60180993, 1.33521535, 1.24619392],
 [1.00871733, 1.59194631, 0.81632789, 1.24619392, 1.4141925 ]])
A = np.array([[1., 0., 0., 0., 0.],
 [0., 1., 0., 0., 0.],
 [0., 0., 1., 0., 0.],
 [0., 0., 0., 1., 0.]])
q = np.array([0.87613838, 0.7393823,  0.55419765, 0.59420561, 0.26704384])
l = np.array([-0.37471228, -0.80018154, -0.47095637, -0.11762543])
u = np.array([0.21614515, 0.50421568, 0.35092037, 0.95366794])

x0 = np.zeros(n)
y0 = np.zeros(m)

"""Solver parameters"""
sigma = 1e-6
rho = 6
alpha = 1.6
maxiter=1000

G = qp_setup(P,A,rho,sigma)
print("Python implementation of qp_setup:")
print("G:")
print(G)

libname=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     "libqp_solver.so")
c_lib=ctypes.CDLL(libname)

c_lib.qp_setup.argtypes = [
    ctypes.c_size_t, #N
    ctypes.c_size_t, #M
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), #P
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), #A
    ctypes.c_float, #sigma
    ctypes.c_float, #rho
    # we want to change the value of an input array, so have to 
    # convert to a pointer (C passes by value, so we need to supply
    # an address to copy rather than an array of data)
    ctypes.POINTER(ctypes.c_double)] #G

G_C=np.zeros_like(P).astype(np.float32)
c_lib.qp_setup(len(P),len(A),
               P.astype(np.float32),A.astype(np.float32),
               sigma,rho,
               G_C.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))

print("C implementation of qp_setup:")
print("G:")
print(G_C)

print("\n\n\n\n")
try:
    import osqp
    qp=osqp.OSQP()
    qp.setup(P=scipy.sparse.csc_matrix(P),
             q=q,
             A=scipy.sparse.csc_matrix(A),
             l=l,
             u=u,
             verbose=False)
    print("OSQP implementation of qp_solve: ")
    results = qp.solve()
    print("x=", results.x)
    print("y=", results.y)    
    print()
except:
    pass

xf, yf, k, r_prim, r_dual = qp_solve(G,P,A,rho,sigma,alpha,q,l,u,x0,y0,maxiter)
print("Python implementation of qp_solve: ")
print("x=", xf)
print("y=", yf)
print()

c_lib.qp_solve.argtypes = [
    ctypes.c_size_t, #N
    ctypes.c_size_t, #M
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), #G
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), #P
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), #A
    ctypes.c_float, #rho    
    ctypes.c_float, #sigma
    ctypes.c_float, #alpha
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'), #q
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'), #l
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'), #u
    ctypes.c_size_t, #maxiter
    # we want to change the value of an input array, so have to 
    # convert to a pointer (C passes by value, so we need to supply
    # an address to copy rather than an array of data)
    ctypes.POINTER(ctypes.c_double), #xOut
    ctypes.POINTER(ctypes.c_double), #yOut
    ctypes.POINTER(ctypes.c_double)] #residual
c_lib.qp_solve.restype = ctypes.c_void_p #void return (answer goes into xOut)

xout=x0.copy().astype(np.float32)
yout=y0.copy().astype(np.float32)
residual=np.zeros(len(yout)).astype(np.float32)
c_lib.qp_solve(len(q),
               len(A),
               G.astype(np.float32),
               P.astype(np.float32),
               A.astype(np.float32),
               rho, sigma, alpha,
               q.astype(np.float32),
               l.astype(np.float32),
               u.astype(np.float32),
               maxiter,
               xout.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
               yout.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
               residual.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))

print("C implementation of qp_solver: ")
print("x=", xout)
print("y=", yout)
print("residual=", residual)
