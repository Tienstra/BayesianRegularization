#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 11:41:17 2022

@author: maiatienstra

Bayesian Regularization 
Master Thesis Project Modules
28 February 2022
"""


import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import dia_matrix
from scipy.sparse.linalg import cg
import pandas as pd
import seaborn as sns





#see exercise 2.4.4
def getA(x):
    
    """
    Given a function as an array this computes discretized smoothing operator
    Ax(t) = \int_0^1 x(y)/((1+(t-y)^2)^3/2) dy

    Parameters
    ----------
    x : an array (x_0,...,x_n).

    Returns
    -------
    A : a matrix array n by n.
    """
    
    h = x[1] - x[0]
    #xx = yy^T this line create a grid where we have a point at each integer 
    #value between x_0 and x_n in both the x and y directions.
    xx,yy = np.meshgrid(x,x)
    #A then is applied to x by using xx,yy
    A = h/(1 + (xx - yy)**2)**(3/2)

    return A





def getL(x):
    
    """
    Given a function as an array this function computes the second order
    finite difference matrix.      

    Parameters
    ----------
    x : an array (x_0,...,x_n).

    Returns
    -------
    L : a matrix array n by n
    """
    
    h = x[1] - x[0]
    n = len(x)
    ex = np.ones(n)
    #data matrix with r1=1s, r2=-2, r3=1s len(rn)=n
    data = np.array([ex, -2 * ex, ex])
    #one lower diag , main diag ,one upper diag
    offsets = np.array([-1, 0, 1])
    L = (1/h**2)*dia_matrix((data, offsets), shape=(n, n)).toarray()
    
    return L





def J(A,L,x,alpha,beta,y,a_0,a_1,b_0,b_1):
    
    """
    Computes the negative log posterior likelihood. 

    Parameters
    ----------
    x : an array (x_0,...,x_n).
    
    alpha : a real umber > 0.
    
    beta : a real numer > 0.
    
    y : an array (y_0,...,y_n).
    
    a_0 : a real umber > 0.
    
    a_1 : a real umber > 0.
    
    b_0 : a real umber > 0.
    
    b_1 : a real umber > 0.

    Returns
    -------
    Real number value of objective function.

    """
    n = len(y)
    
    
    
    return (1/2)*alpha*np.linalg.norm(A@x - y)**2 -(n/2+a_0-1)*np.log(alpha)+ b_0*alpha + (1/2)*beta*np.linalg.norm(L@x)**2-(n/2+a_1-1)*np.log(beta)+b_1*beta








def compute_gradient(A,L,beta,alpha,x,y,a_0,a_1,b_0,b_1):
    """
    Computes 
    
    ||partial_x J ||_2^2 + ||partial_alpha J ||_2^2 +||partial_beta J ||_2^2
    
    for the stopping conditon in Algo1,2,3,4. 

    Parameters
    ----------
    A : a matrix.
    
    L : a matrix. 

    beta : a real number > 0.
    
    alpha : a real number > 0.
        
    x : array x=(x_1,...x_n).
        
    y : an array (y_0,...,y_n).
        
    a_0 : an integer neq 1.
 
    a_1 : an integer neq 1.
        
    b_0 : an integer neq 0.
       
    b_1 : an integer neq 0.


    Returns
    -------
    sum_of_norms : real number
        The squared norm of the gradient of the objective function.

    """
    n = len(y)
    partial_x = (A.T@A+(beta/alpha)*L.T@L)@x-A.T@y
    partial_alpha = (1/2*np.linalg.norm(A@x-y)**2)-((n/2+a_0-1)/alpha)+b_0
    partial_beta = (1/2*np.linalg.norm(L@x)**2)-((n/2+a_1-1)/beta)+b_1
                   
    sum_of_norms = np.linalg.norm(partial_x)**2+np.linalg.norm(partial_alpha)**2+np.linalg.norm(partial_beta)**2

    return sum_of_norms








def Algorithm1(A,L,y_delta,hyper_priors = [1 + 1e-6, 1e-6, 1 + 1e-6, 1e-6], niter=10000,tol=1e-5, print_res=False):
    
    """
    Implements method 1. 

    Parameters
    ----------
    A : a matrix.
    
    L : a matrix. 
    
    y_delta : an array (y_0,....,y_n).
    
    hyper_priors : array, optional.length 4 in order of a0, b0, a1,b1
        DESCRIPTION. The defualt is [1 + 1e-6, 1e-6, 1 + 1e-6, 1e-6].
    
    niter : integer, optional
        DESCRIPTION. The default is 100000.
    
    tol : integer, optional
        DESCRIPTION. The default is 1e-5.
        
    print_res : Boolean, optional
        DESCRIPTION. The default FALSE. 

    Returns
    -------
    x : an array. 
        DESCRIPTION. An estimate for x_bar.
    
    alpha : a real number > 0.
    
    beta : a real number > 0.
    
    data : a pandas data frame.        

    """
    # parameters for algorithm 1
 
    n = len(y_delta)
    # hyperparameters
    #a_0 = 1 + 1e-6
    #b_0 = 1e-6
    #a_1 = 1 + 1e-6
    #b_1 = 1e-6
    
    a_0 = hyper_priors[0]
    b_0 = hyper_priors[1]
    a_1 = hyper_priors[2]
    b_1 = hyper_priors[3]

    # initial guess
    alpha =10
    beta = 1
    c = np.linalg.norm(A.T@y_delta)**2 / np.linalg.norm(A@A.T@y_delta)**2
    x = c*A.T@y_delta
    
    #lists
    alpha_list  = [alpha]
    beta_list   = [beta] 
    lmbd_list = [beta/alpha]
    x_norm_list = [np.linalg.norm(x)**2]
    x_list      =[x]
    obj_list = [J(A,L,x,alpha,beta,y_delta,a_0,b_0,a_1,b_1)]
    J_x = [np.linalg.norm((A.T@A+(beta/alpha)*L.T@L)@y_delta-A.T@x)**2]
    J_alpha = [np.linalg.norm((1/2*np.linalg.norm(A@x-y_delta)**2)-((n/2+a_0-1)/alpha)+b_0)**2]
    J_beta = [np.linalg.norm((1/2*np.linalg.norm(L@x)**2)-((n/2+a_1-1)/beta)+b_1)]

    # iterate
    
 
    for k in range(niter):
        print(k, end = "\r")
        x     = np.linalg.solve(A.T@A + (beta/alpha)*(L.T@L), A.T@y_delta)
        alpha = ((n/2)+a_0-1) / (((1/2)*(np.linalg.norm(y_delta-A@x)**2)  + b_0)) 
        beta  = ((n/2)+a_1-1) / (((1/2)*(np.linalg.norm(L@x)**2) + b_1))
        obj = J(A,L,x,alpha,beta,y_delta,a_0,b_0,a_1,b_1)
        
        
        partial_x = (A.T@A+(beta/alpha)*L.T@L)@x-A.T@y_delta
        partial_alpha = (1/2*np.linalg.norm(A@x-y_delta)**2)-((n/2+a_0-1)/alpha)+b_0
        partial_beta = (1/2*np.linalg.norm(L@x)**2)-((n/2+a_1-1)/beta)+b_1
        
        
        #save all itterates
        J_x.append(np.linalg.norm(partial_x)**2)
        J_alpha.append(np.linalg.norm(partial_alpha)**2)
        J_beta.append(np.linalg.norm(partial_beta)**2)

      
        x_norm_list.append(np.linalg.norm(x)**2)
        x_list.append(x)
        alpha_list.append(alpha)
        beta_list.append(beta)
        lmbd_list.append(beta/alpha)
        obj_list.append(obj)
        
        grad = compute_gradient(A,L,beta,alpha,x,y_delta,a_0,a_1,b_0,b_1) 

        if grad < tol:
            if print_res:
                print('Successful')
                print('Iterations:',k+1)
                print('Gradient:',grad)
            break 
        elif k == niter-1:
            print('Maximum number of iterations reached.')
            print('Gradient:',grad)
       
           


    data_dict = {"x_norm": x_norm_list, "alpha": alpha_list, "beta": beta_list, 
                 "lambda": lmbd_list, "obj": obj_list, 
                 '$||\nabla_x J||$':J_x,'$||\nabla_{a} J||$': J_alpha, 
                 '$||\nabla_{B} J||$':J_beta }
    data = pd.DataFrame.from_dict(data_dict)

    return x,alpha,beta,obj_list,data
 
    



def Algorithm2(A,L,y_delta, mu_a = 1e-3,mu_b=1e-3, niter=10000,tol=1e-5,print_res=False):
    
    """
    Implements method 2. 
    
    Parameters
    ----------
    A : a matrix.
    
    L : a matrix. 
    
    y_delta : an array (y_0,....,y_n).
    
    mu : integer, optional
        DESCRIPTION. The default is 1e-3.
    
    niter : integer, optional
        DESCRIPTION. The default is 100000.
    
    tol : integer, optional
        DESCRIPTION. The default is 1e-5.
        
    print_res : Boolean, optional
        DESCRIPTION. The default FALSE. 

    Returns
    -------
    x : an array. 
        DESCRIPTION. An estimate for x_bar.
    
    alpha : a real number > 0.
    
    beta : a real number > 0.
    
    data : a pandas data frame.       
  
    """
    # parameters for algorithm 2

    #mu=1e-3
    
    n = len(y_delta)

    # hyperparameters
    a_0 = 1 + 1e-6
    b_0 = 1e-6
    a_1 = 1+ 1e-6
    b_1 = 1e-6
    
    # initial guess
    alpha =10
    beta = 1
    c = np.linalg.norm(A.T@y_delta)**2 / np.linalg.norm(A@A.T@y_delta)**2
    x = c*A.T@y_delta
   
    
    #lists
    alpha_list  = [alpha]
    beta_list   = [beta] 
    lmbd_list = [beta/alpha]
    x_norm_list = [np.linalg.norm(x)**2]
    x_list      =[x]
    obj_list = [J(A,L,x,alpha,beta,y_delta,a_0,b_0,a_1,b_1)]
    J_x = [np.linalg.norm((A.T@A+(beta/alpha)*L.T@L)@y_delta-A.T@x)**2]
    J_alpha = [np.linalg.norm((1/2*np.linalg.norm(A@x-y_delta)**2)-((n/2+a_0-1)/alpha)+b_0)**2]
    J_beta = [np.linalg.norm((1/2*np.linalg.norm(L@x)**2)-((n/2+a_1-1)/beta)+b_1)]
 
    

    # iterate
    obj = np.zeros(niter+1)
    for k in range(niter):
        print(k, end = "\r")
        x      = np.linalg.solve(A.T@A + (beta/alpha)*(L.T@L), A.T@y_delta)
        #mu = 1/np.linalg.norm((A.T@A) + (beta/alpha)*(L.T@L),ord=2)**2
        alpha -= mu_a * ((1/2)*np.linalg.norm(y_delta-A@x)**2 + b_0 - ((n/2+a_0-1)/alpha))
        beta  -= mu_b * ((1/2)*np.linalg.norm(L@x)**2 + b_1 - ((n/2+ a_1 - 1)/beta))
        obj = J(A,L,x,alpha,beta,y_delta,a_0,b_0,a_1,b_1)
        
        partial_x = (A.T@A+(beta/alpha)*L.T@L)@x-A.T@y_delta
        partial_alpha = (1/2*np.linalg.norm(A@x-y_delta)**2)-((n/2+a_0-1)/alpha)+b_0
        partial_beta = (1/2*np.linalg.norm(L@x)**2)-((n/2+a_1-1)/beta)+b_1
        
        
        #save all itterates
        J_x.append(np.linalg.norm(partial_x)**2)
        J_alpha.append(np.linalg.norm(partial_alpha)**2)
        J_beta.append(np.linalg.norm(partial_beta)**2)

      
        x_norm_list.append(np.linalg.norm(x)**2)
        x_list.append(x)
        alpha_list.append(alpha)
        beta_list.append(beta)
        lmbd_list.append(beta/alpha)
        obj_list.append(obj)
        
        grad = compute_gradient(A,L,beta,alpha,x,y_delta,a_0,a_1,b_0,b_1)

        if grad < tol:
            if print_res:
                print('Successful')
                print('Iterations:',k+1)
                print('Gradient:',grad)
            break
        elif k == niter-1:
            print('Maximum number of iterations reached.')
            print('Gradient:',grad)


        
    data_dict = {"x_norm": x_norm_list, "alpha": alpha_list, "beta": beta_list, 
                  "lambda": lmbd_list,"obj": obj_list, 
                 '$||\nabla_x J||$':J_x,'$||\nabla_{a} J||$': J_alpha, '$||\nabla_{B} J||$':J_beta }
    data = pd.DataFrame.from_dict(data_dict)

    return x,alpha,beta,obj_list,data
 
    




def Algorithm3(A, L, y_delta, mu=1e-3, niter=10000,tol=1e-5,print_res=False):
    
    """
    Implements method 3. 

    Parameters
    ----------
    A : a matrix.
    
    L : a matrix. 
    
    y_delta : an array (y_0,....,y_n).
    
    mu : integer, optional
        DESCRIPTION. The default is 1e-5.
    
    niter : integer, optional
        DESCRIPTION. The default is 100000.
    
    tol : integer, optional
        DESCRIPTION. The default is 1e-8.
        
    print_res : Boolean, optional
        DESCRIPTION. The default FALSE. 

    Returns
    -------
    x : an array. 
        DESCRIPTION. An estimate for x_bar.
    
    alpha : a real number > 0.
    
    beta : a real number > 0.
    
    data : a pandas data frame.  
    
    """
    # parameters for algorithm 3
  
    n = len(y_delta)

    # hyperparameters
    a_0 = 1 + 1e-6
    b_0 = 1e-6
    a_1 = 1+ 1e-6
    b_1 = 1e-6
    
    # initial guess
    alpha =10
    beta = 1
    c = np.linalg.norm(A.T@y_delta)**2 / np.linalg.norm(A@A.T@y_delta)**2
    x = c*A.T@y_delta
    
   
    #lists
    alpha_list  = [alpha]
    beta_list   = [beta] 
    lmbd_list = [beta/alpha]
    
    x_norm_list = [np.linalg.norm(x)**2]
    x_list      =[x]
    
    obj_list = [J(A,L,x,alpha,beta,y_delta,a_0,b_0,a_1,b_1)]
    
    J_x = [np.linalg.norm((A.T@A+(beta/alpha)*L.T@L)@y_delta-A.T@x)**2]
    J_alpha = [np.linalg.norm((1/2*np.linalg.norm(A@x-y_delta)**2)-((n/2+a_0-1)/alpha)+b_0)**2]
    J_beta = [np.linalg.norm((1/2*np.linalg.norm(L@x)**2)-((n/2+a_1-1)/beta)+b_1)]
 
    
     # iterate
    obj = np.zeros(niter)
    for k in range(niter):
        print(k, end = "\r")
        alpha = ((n/2)+a_0-1) / (((1/2)*(np.linalg.norm(y_delta-A@x)**2)  + b_0)) 
        beta  = ((n/2)+a_1-1) / (((1/2)*(np.linalg.norm(L@x)**2) + b_1))
        #mu = 1/np.linalg.norm((A.T@A) + (beta/alpha)*(L.T@L),ord=2)**2
        #g  = alpha*(A.T@(A@x - y_delta)) + beta*(L.T@(L@x))
        g=(A.T@A+(beta/alpha)*L.T@L)@x-A.T@y_delta
        x -= mu * g
        obj = J(A,L,x,alpha,beta,y_delta,a_0,b_0,a_1,b_1)
        partial_x = (A.T@A+(beta/alpha)*L.T@L)@x-A.T@y_delta
        partial_alpha = (1/2*np.linalg.norm(A@x-y_delta)**2)-((n/2+a_0-1)/alpha)+b_0
        partial_beta = (1/2*np.linalg.norm(L@x)**2)-((n/2+a_1-1)/beta)+b_1
        
     #save all itterates
        J_x.append(np.linalg.norm(partial_x)**2)
        J_alpha.append(np.linalg.norm(partial_alpha)**2)
        J_beta.append(np.linalg.norm(partial_beta)**2)

      
        x_norm_list.append(np.linalg.norm(x)**2)
        x_list.append(x)
        alpha_list.append(alpha)
        beta_list.append(beta)
        lmbd_list.append(beta/alpha)
        obj_list.append(obj)
        
        grad = compute_gradient(A,L,beta,alpha,x,y_delta,a_0,a_1,b_0,b_1)

        if grad < tol:
            if print_res:
                print('Successful')
                print('Iterations:',k+1)
                print('Gradient:',grad)
            break 
        elif k == niter-1:
            print('Maximum number of iterations reached.')
            print('Gradient:',grad)

            

    data_dict = {"x_norm": x_norm_list, "alpha": alpha_list, "beta": beta_list, 
                 "lambda": lmbd_list, "obj": obj_list, 
                 '$||\nabla_x J||$':J_x,'$||\nabla_{a} J||$': J_alpha, 
                 '$||\nabla_{B} J||$':J_beta }
    data = pd.DataFrame.from_dict(data_dict)

    return x,alpha,beta,obj_list,data






def Algorithm4(A,L, y_delta,niter=10000,tol=1e-5,print_res=False):
    
    """  
    Implements a modified method 1, where instead of using closed form soltuion
    for x, we use a graident method.
    
    Parameters
    ----------
    A : a matrix.
    
    L : a matrix. 
    
    y_delta : an array (y_0,....,y_n).
    
    niter : integer, optional
        DESCRIPTION. The default is 100000.
    
    tol : integer, optional
        DESCRIPTION. The default is 1e-5.
        
    print_res : Boolean, optional
        DESCRIPTION. The default FALSE. 

    Returns
    -------
    x : an array. 
        DESCRIPTION. An estimate for x_bar.
    
    alpha : a real number > 0.
    
    beta : a real number > 0.
    
    data : a pandas data frame.  
    
    """

    # parameters for algorithm 4
 
    n = len(y_delta)
    # hyperparameters
    a_0 = 1 + 1e-6
    b_0 = 1e-6
    a_1 = 1 + 1e-6
    b_1 = 1e-6

    # initial guess
    alpha =10
    beta = 1
    c = np.linalg.norm(A.T@y_delta)**2 / np.linalg.norm(A@A.T@y_delta)**2
    x = c*A.T@y_delta
    
    #lists
    alpha_list  = [alpha]
    beta_list   = [beta] 
    lmbd_list =[beta/alpha]
    x_norm_list = [np.linalg.norm(x)**2]
    x_list      =[x]
    obj_list = [J(A,L,x,alpha,beta,y_delta,a_0,b_0,a_1,b_1)]
    J_x = [np.linalg.norm((A.T@A+(beta/alpha)*L.T@L)@y_delta-A.T@x)**2]
    J_alpha = [np.linalg.norm((1/2*np.linalg.norm(A@x-y_delta)**2)-((n/2-a_0-1)/alpha)+b_0)**2]
    J_beta = [np.linalg.norm((1/2*np.linalg.norm(L@x)**2)-((n/2-a_1-1)/beta)+b_1)]

    # iterate
    
    div =0
    
    for k in range(niter):
        print(k, end = "\r")
        x_array     = cg(A.T@A + (beta/alpha)*(L.T@L), A.T@y_delta)
        x = x_array[0]
        if x_array[1]!= 0:
            div = div +1 
        alpha = ((n/2)+a_0-1) / (((1/2)*(np.linalg.norm(y_delta-A@x)**2)  + b_0)) 
        beta  = ((n/2)+a_1-1) / (((1/2)*(np.linalg.norm(L@x)**2) + b_1))
        obj = J(A,L,x,alpha,beta,y_delta,a_0,b_0,a_1,b_1)
        
        
        partial_x = (A.T@A+(beta/alpha)*L.T@L)@x-A.T@y_delta
        partial_alpha = (1/2*np.linalg.norm(A@x-y_delta)**2)-((n/2+a_0-1)/alpha)+b_0
        partial_beta = (1/2*np.linalg.norm(L@x)**2)-((n/2+a_1-1)/beta)+b_1
        
        
        #save all itterates
        J_x.append(np.linalg.norm(partial_x)**2)
        J_alpha.append(np.linalg.norm(partial_alpha)**2)
        J_beta.append(np.linalg.norm(partial_beta)**2)

      
        x_norm_list.append(np.linalg.norm(x)**2)
        x_list.append(x)
        alpha_list.append(alpha)
        beta_list.append(beta)
        lmbd_list.append(beta/alpha)
        obj_list.append(obj)
        
        grad = compute_gradient(A,L,beta,alpha,x,y_delta,a_0,a_1,b_0,b_1)

        if grad < tol:
            if print_res:
                print('Successful')
                print('Iterations:',k+1)
                print('Gradient:',grad)
            break 
        elif k == niter-1:
            print('Maximum number of iterations reached.')
            print('Gradient:',grad)

    print(div)        
        
    data_dict = {"x_norm": x_norm_list, "alpha": alpha_list, "beta": beta_list, 
                 "lambda": lmbd_list, "obj": obj_list, '$||\nabla_x J||$':J_x,
                 '$||\nabla_{a} J||$': J_alpha, '$||\nabla_{B} J||$':J_beta }
    data = pd.DataFrame.from_dict(data_dict)

    return x,alpha,beta,obj_list,data





def plot_results(obj, t,A, x_bar, x_hat,alpha_hat, beta_hat, y_delta,name, log=False):
    """
    

    Parameters
    ----------
    obj : an array.
        DESCRIPTION. The values of the objective function durring all iterations.
    t : an array.
        
    A : a matrix.
        
    x_bar : a array.
        DESCRIPTION. The ground thruth.
        
    x_hat : an array. 
        DESCRIPTION. The estimate of the ground truth.
        
    alpha_hat : an array.  
        DESCRIPTION. The values of the alpha estimates function durring all iterations.
        
    beta_hat : an array.
        DESCRIPTION. The values of the beta estimates function durring all iterations.
        
    y_delta : an array. 
        
    name : string.
       
    log : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    None.

    """
    
    err = np.linalg.norm(x_bar-x_hat)**2
    fig,ax = plt.subplots(1,3)
    ax[0].plot(obj)
    if log:
        ax[0].set_xscale('log')
    ax[0].set_title('J')
    ax[1].plot(t,x_bar,label=r'$\overline{x}$')
    ax[1].plot(t,x_hat,label=r'$\widehat{x}$')
    ax[1].legend()
    ax[1].set_title('$\overline{x}$ vs $\widehat{x}$')
    ax[2].plot(t,y_delta,label=r'$y^\delta$')
    ax[2].plot(t,A@x_hat,label=r'$A\widehat{x}$')
    ax[2].legend()
    ax[2].set_title('$y^\delta$ vs $A\widehat{x}$')
    fig.tight_layout()
    
    plt.savefig(name+'results.jpeg',dpi=500)   
    plt.show()

    print('Lambda:', beta_hat/alpha_hat)
    print('Error:', err)
    print('Obj val:',obj[-1])





def plot_estimates(df,name):
    
    """
    

    Parameters
    ----------
    df : pandas dataframe
        DESCRIPTION. Dataframe containing all values of estimates during iteration.
    name : string.
    

    Returns
    -------
    None.

    """
    fig,ax = plt.subplots(2,2)
    ax[0,0].plot(np.arange(len(df['alpha'].to_numpy())),df['alpha'].to_numpy())
    ax[0,0].set_title('alpha')
    
    ax[0,1].plot(np.arange(len(df['beta'].to_numpy())),df['beta'].to_numpy())
    ax[0,1].set_title('beta')
    # ax[0,1].set_xscale('log')
    
    ax[1,0].plot(np.arange(len(df['lambda'].to_numpy())),df['lambda'].to_numpy())
    ax[1,0].set_title('lambda')
    # ax[1,0].set_xscale('log')
    
    ax[1,1].plot(np.arange(len(df['x_norm'].to_numpy())),df['x_norm'].to_numpy())
    ax[1,1].set_title('x_norm')
    # ax[1,1].set_xscale('log')
    
    
    
    
    if (df.shape[0]-1) > 10:
        ax[0,0].set_xscale('log')
        ax[0,1].set_xscale('log')
        ax[1,0].set_xscale('log')
        ax[1,1].set_xscale('log')
    
    
    fig.tight_layout()
    
    plt.savefig(name+'_estimates.jpeg',dpi=500)
    
    plt.show()  
    



def getObj(A,L,y_delta,alpha, beta):
    
    """
    Returns objective function. 

    Parameters
    ----------
    A : a matrix.
    
    L : a matrix. 
    
    y_delta : an array (y_0,....,y_n).
    
    alpha : a real number > 0.
        
    beta : a real number > 0.

    Returns
    -------
    obj_func : a real number. 
        DESCRIPTION. The value of the objective function given alpha, beta, fixing x.

    """
    
    # hyperparameters
    a_0 = 1 + 1e-6
    b_0 = 1e-6
    a_1 = 1 + 1e-6
    b_1 = 1e-6

    #x_hat(alpha, beta) = (A^*A + beta/alpha L^*L)^-1 A*y_delta
    x_hat = np.linalg.solve(A.T@A + (beta/alpha)*L.T@L, A.T@y_delta)
    
    
    obj_func = J(A,L,x_hat,alpha,beta,y_delta,a_0,a_1,b_0,b_1)

    return obj_func



# =============================================================================
# def plot_contour(A,L, y_delta,alpha_hat, beta_hat, name, ranges=[10,100,1,4],ns=20, log=False):
#     
#     """
#     Plots the contour lines of J(x(alpha,beta),alpha,beta)=z. Can also plot
#     on log-scale. 
# 
#     Parameters
#     ---------- 
#     A : a matrix
#     
#     L : a matrix 
#     
#     y_delta : an array (y_0,....,y_n).
#     
#     alpha_hat : a real number > 0.
#         
#     beta_hat : a real number > 0.
#         
#     name : string
#         
#     ns : integer, optional
#         DESCRIPTION. The default is 20.
#         
#     log : Boolean, optional
#         DESCRIPTION. The default is False.
# 
#     Returns
#     -------
#     None.
# 
#     """
#     if log: 
#         #theta = [alpha, beta]
#         obj = lambda theta : getObj(A,L,y_delta, theta[0], theta[1])
#         
#         
#         alphas = np.logspace(1,3,ns)
#         betas = np.logspace(-1,1,ns)
#         
#         
#         objs = np.zeros((ns,ns))
#         
#         #solves for x_hat by using the previous alpha[i], beta[j]
#         for i in range(ns):
#             for j in range(ns):
#                 objs[i,j] = obj([alphas[i],betas[j]])
#     
#     
#         fig, axs = plt.subplots(1,1)
#     
#         axs.contourf(np.log10(betas),np.log10(alphas),objs,levels=30)
#         axs.set_xlabel(r'$\log_{10} \beta$')
#         axs.set_ylabel(r'$\log_{10} \alpha$')
#         axs.plot(np.log10(beta_hat),np.log10(alpha_hat),'ro',label='optimal parameter')
#         axs.plot(np.log10(betas),np.log10(alpha_hat*(betas/beta_hat)),'w--')
#         axs.set_xlim(np.log10(betas[0]),np.log10(betas[-1]))
#         axs.set_ylim(np.log10(alphas[0]),np.log10(alphas[-1]))
#         axs.set_aspect(1)
#         axs.legend()
#         fig.tight_layout()
#     else:
#         obj = lambda theta : getObj(A,L,y_delta, theta[0], theta[1])
#         
#         
#         alphas = np.linspace(ranges[0],ranges[1],ns)
#         betas = np.linspace(ranges[2],ranges[3],ns)
#         
#         
#         objs = np.zeros((ns,ns))
#         
#         #solves for x_hat by using the previous alpha[i], beta[j]
#         for i in range(ns):
#             for j in range(ns):
#                 objs[i,j] = obj([alphas[i],betas[j]])
#         
#         
#         fig, axs = plt.subplots(1,1)
#         
#         axs.contourf(betas,alphas,objs,levels=10)
#         axs.set_xlabel(r'$\beta$')
#         axs.set_ylabel(r'$\alpha$')
#         axs.plot(beta_hat,alpha_hat,'ro',label='optimal parameter')
#         axs.legend()
#         fig.tight_layout()
#         
#         
#     fig.savefig(name+'_contour.jpeg',dpi=300)
# 
# =============================================================================



def plot_contour(A,L, y_delta, df, name ,ns=50, ranges=[0.5,150,0.01,10],save=True ):
   

    alpha_hat = df['alpha'].to_numpy()
    beta_hat = df['beta'].to_numpy()
    
    
    #ranges=[0.5,150,0.01,10]
    #ranges=[5,150,0.5,4]
    
    obj = lambda theta : getObj(A,L,y_delta, theta[0], theta[1])
    
    
    alphas = np.linspace(ranges[0],ranges[1],ns)
    betas = np.linspace(ranges[2],ranges[3],ns)
    
    
    objs = np.zeros((ns,ns))
    
    #solves for x_hat by using the previous alpha[i], beta[j]
    for i in range(ns):
        for j in range(ns):
            objs[i,j] = obj([alphas[i],betas[j]])
    
    
    fig, axs = plt.subplots(1,1)
    
    axs.contourf(betas,alphas,objs,levels=30)
    axs.set_xlabel(r'$\beta$')
    axs.set_ylabel(r'$\alpha$')
    
    if len(alpha_hat) < 50:
        col = sns.color_palette("rocket", len(alpha_hat))
        for i in range(len(alpha_hat)):
            axs.plot(beta_hat[i],alpha_hat[i], marker ='o', color = col[i],label='$\lambda_{}$'.format(str(i)))
            axs.legend()
            fig.tight_layout()
    else:
        col = sns.color_palette("rocket", ns)
        j = 0
        for i in np.unique(np.logspace(0, np.log10(df.shape[0]-1), ns).astype(np.int)):
            
            axs.plot(beta_hat[i],alpha_hat[i], marker ='o', color = col[j],label='$\lambda_{}$'.format({str(i)}))
            j +=1
            #print(beta_hat[i], alpha_hat[i])
        #axs.legend()
        fig.tight_layout()
        
    if save:
        fig.savefig(name+'_contour.jpeg',dpi=300)
    
    
