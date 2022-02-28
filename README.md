# Bayesian Tikhonov Regularization
## A Bayesian Hierarchical Model for Estimating the Regularization Parameters in Tikhonov Regularization

In this thesis we discuss the theory behind the regularizing Tikhonov functional proposed by Jin and Zou in the paper *Augmented Tikhonov regularization*, 2008. We reimplement their Alternating Iterative Algorithm. The role of the hyper-priors in the Alternating Iterative Algorithm is reexamined, and we find cases in which convergence to a minimum is not guaranteed. Furthermore, their method depends on the existence to the closed form solutions. We, therefore, extend their algorithms by proposing two additional iterative methods that do not depend on the closed form solutions. The convergence of the two methods is proven. We analyze the properties of the two novel methods through a simple simulation.

### Remarks

- The paper can be found in the Thesis directory. 
- The Notebook displaying the results discussed in section 6 of the thesis can be found in the Notebooks directory.
- The Python code used in the simulation study can be found in the Code directory. 
