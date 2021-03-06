import numpy as np
import matplotlib.pyplot as plt
import time

Nlook=60
sigma=1e-4 #1.4
rho=0.1
alpha=1.6
nIter=5
num_sim_timesteps=600

for which_implementation in ['c','python','rory']:
    if which_implementation=='c':
        from python_c_helpers import *
    elif which_implementation=='rory':
        from qpmpc import *
    else:
        from mpc_qp_helpers import *

    ##### START SYSTEM SETUP #####
    if False:
        '''
        For a spring with mass m, spring constant k, damping b,
        positive force u:
        \dot{x}=Ax+Bu for 
        A=[[0,1],[-k/m,-b/m]] B=[0,1/m]
        (see 433 notes)
        For our case of discrete time, we simply multiply 
        A and B by delta_t, and add the identity to A
        '''
        m=1
        k=1
        b=0.1
        delta_t=0.02
        nu=1
        nx=2
        A=np.array([[1,delta_t],[-k/m*delta_t,1-b/m*delta_t]])
        B=np.atleast_2d(np.array([0,1/m*delta_t])).T
        Q=np.array([[1.,0],[0,1]])
        R=np.array([[1.]])

        uref=np.array([0])
        xref=np.array([0,0]) #target position 0, velocity 0
        umin=np.array([-0.005])
        umax=np.array([1])
        delta_umin=np.array([-1])
        delta_umax=np.array([1])

        x=np.array([0,0.01]) #initial position 0, velocity 0
        ##### END SYSTEM SETUP #####
    ##### START SYSTEM SETUP #####
    else:
        '''
        For 2 carts with independent engines, wall on left to spring to first
        cart to second spring to second cart. x-l1 the first variable, y-l2
        the second for l1 and l2 the relaxed spring lengths. 
        '''
        m1=1
        m2=1
        k1=1
        k2=1
        b1=0.1
        b2=0.1
        delta_t=0.02
        nu=2
        nx=4
        A=np.array([[1,              delta_t,         0,              0],
                    [-k1/m1*delta_t, 1-b1/m1*delta_t, 0,              0],
                    [0,              0,               1,              delta_t],
                    [k2/m2*delta_t,  0,               -k2/m2*delta_t, 1-b2/m2*delta_t]])
        B=np.array([[0,            0],
                    [1/m1*delta_t, 0],
                    [0,            0],
                    [0,            1/m2*delta_t]])
        Q=np.eye(nx)
        R=np.eye(nu)

        uref=np.array([0,0])
        xref=np.array([0,0,0,0]) #target position 0, velocity 0
        umin=np.array([-0.005,0])
        umax=np.array([1,0])
        delta_umin=np.array([-1,-1])
        delta_umax=np.array([1,1])

        x=np.array([0.01,0,0,0]) 
        ##### END SYSTEM SETUP #####
    u=np.zeros((nu*Nlook)) #initial guess for best control all 0
    lamb=np.zeros((nu*(2*Nlook-1))) #initial guess for Lagrangian forces 0

    (E,F,P,G,
     Ac,Qhat,Rhat)=mpc_setup(Nlook=Nlook, A=A, B=B, Q=Q, R=R,
                                                  sigma=sigma, rho=rho, dt=delta_t)

    uref_hat=np.tile(uref, (Nlook,))
    xref_hat = np.tile(xref, (Nlook,))
    umin_hat = np.tile(umin, (Nlook,))
    umax_hat = np.tile(umax, (Nlook,))
    delta_umin_hat = np.tile(delta_umin, (Nlook-1,))
    delta_umax_hat = np.tile(delta_umax, (Nlook-1,))

    X_uncontrolled = np.zeros(nx*num_sim_timesteps)
    X_uncontrolled[:nx]=x
    u_uncontrolled=np.zeros(nu*num_sim_timesteps)

    X_MPC = np.zeros(nx*num_sim_timesteps)
    X_MPC[:nx]=x
    u_MPC=np.zeros(nu*num_sim_timesteps)

    runtimes=[]
    for i in range(1,num_sim_timesteps):
        u_uncontrolled[i*nu:(i+1)*nu] = uref
        X_uncontrolled[i*nx:(i+1)*nx] = A@X_uncontrolled[(i-1)*nx:i*nx]+B@u_uncontrolled[i*nu:(i+1)*nu]

        before_time=time.perf_counter()
        (u,lamb)=mpc_action(zk=x, ztarget=xref_hat, 
                            uhat=u, lagrange=lamb,
                            uminhat=umin_hat, duminhat=delta_umin_hat,
                            umaxhat=umax_hat, dumaxhat=delta_umax_hat,
                            urefhat=uref_hat,
                            E=E, F=F, P=P,
                            G=G, Ac=Ac,
                            Qhat=Qhat, Rhat=Rhat,
                            rho=rho, sigma=sigma, alpha=alpha,
                            maxiter=nIter)
        after_time=time.perf_counter()
        runtimes.append(after_time-before_time)
        u_MPC[i*nu:(i+1)*nu]=u[:nu]
        x=A@X_MPC[(i-1)*nx:i*nx]+B@u_MPC[i*nu:(i+1)*nu]
        X_MPC[i*nx:(i+1)*nx]=x

    if True:
        times=np.linspace(0,num_sim_timesteps*delta_t,num_sim_timesteps)
        fig,axes=plt.subplots(nx+nu,sharex=True)
        for i in range(nx):
            axes[i].plot(times,X_uncontrolled[i::nx],label='uncontrolled')
            axes[i].plot(times,X_MPC[i::nx],label='MPC')
            axes[i].axhline(xref[i],linestyle='--',c='k')
        for i in range(nu):
            axes[i+nx].plot(times,u_uncontrolled[i::nu],label='uncontrolled')
            axes[i+nx].plot(times,u_MPC[i::nu],label='MPC')
        axes[0].set_title('States')
        axes[nx].set_title('Controls')
        fig.suptitle(f"{which_implementation} implementation")
        plt.legend()
    if True:
        print(f"Mean {which_implementation} runtime: {np.mean(runtimes):.1e} +/- {np.std(runtimes):.1e}")
plt.show()
