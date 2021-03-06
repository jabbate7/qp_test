#include <stddef.h> //for size_t

/**************************************************
    Solve QP of the form

    min_x  1/2 x^T P x + q^T x
    subject to l <= Ax <= u


    Parameters
    ----------
    G : ndarray (n,n)
        reduced KKT matrix, output of qp_setup
    P : ndarray (n,n)
        hessian matrix
    A : ndarray (m,n)
        constraint matrix
    rho : float
        step size
    sigma : float
        normalization parameter
    alpha : float
        relaxation parameter
    q : ndarray (n,)
        gradient vector
    l, u : ndarray (m,)
        upper and lower bounds on Ax
    x0 : ndarray (n,)
        initial guess for solution
    y0 : ndarray (m,)
        initial guess for lagrange multipliers
    maxiter : int
        maximum number of iterations
    verbose : bool
        whether to display progress

    Returns
    -------
    x : ndarray (n,)
        solution vector
    y : ndarray (m,)
        lagrange multipliers
    r_prim, r_dual : float
        primal and dual residuals
**************************************************/

void qp_setup(size_t const N, size_t const M, float const P[N][N], float const A[M][N], float const sigma, float const rho, float G[N][N]);

void qp_solve(size_t const N, size_t const M,
	      float const G[restrict N][N], float const P[restrict N][N], float const A[restrict M][N],
	      float const rho, float const sigma, float const alpha,
	      float const q[restrict N],
	      float const l[restrict M], float const u[restrict M],
	      size_t const nIter,
	      float xOut[restrict N],
	      float yOut[restrict M],
	      float residual[restrict 2]);

void mpc_setup(size_t const nZ, size_t const nU, size_t const nLook,
	       float const A[nZ][nZ],
	       float const B[nZ][nU],
	       float const Q[nZ][nZ],
	       float const R[nU][nU],
	       float const sigma, float const rho, float const deltaT,
	       float E[nZ*nLook][nZ],
	       float F[nZ*nLook][nU*nLook],
	       float P[nU*nLook][nU*nLook],
	       float G[nU*nLook][nU*nLook],
	       float Ac[nU*(2*nLook-1)][nU*nLook],
	       float QHat[nZ*nLook],
	       float RHat[nU*nLook]);

void mpc_solve(size_t const nZ, size_t const nU, size_t nLook,
	       size_t const nIter,
	       float const rho, float const sigma, float const alpha,
	       float const z[restrict nZ],
	       float const rHat[restrict nZ * nLook],
	       float const uHatMin[restrict nU * nLook],
	       float const uHatMax[restrict nU * nLook],
	       float const uHatMinDelta[restrict nU * (nLook - 1)],
	       float const uHatMaxDelta[restrict nU * (nLook - 1)],
	       float const uHatRef[restrict nU * nLook],
	       float const E[restrict nZ * nLook][nZ],
	       float const F[restrict nZ * nLook][nU * nLook],
	       float const P[restrict nU * nLook][nU * nLook],
	       float const G[restrict nU * nLook][nU * nLook],
	       float const Ac[restrict nU * (2*nLook-1)][nU * nLook],
	       float const QHat[restrict nZ * nLook],
	       float const RHat[restrict nU * nLook],
	       float uHat[restrict nU * nLook],
	       float lambda[restrict nU * (2 * nLook - 1)]);
