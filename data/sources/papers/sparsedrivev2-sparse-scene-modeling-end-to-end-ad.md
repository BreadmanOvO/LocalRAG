# SparseDrivev2 Sparse Scene Modeling End-to-End AD

**Source**: arxiv PDF, 24 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Causal-StoNet: Causal Inference for
High-Dimensional Complex Data
Yaxin Fang
Department of Statistics
Purdue University
West Lafayette, IN 47907, USA
fang230@purdue.edu
Faming Liang
Department of Statistics
Purdue University
West Lafayette, IN 47907, USA
fmliang@purdue.edu
Abstract
With the advancement of data science, the collection of increasingly complex
datasets has become commonplace. In such datasets, the data dimension
can be extremely high, and the underlying data generation process can
be unknown and highly nonlinear. As a result, the task of making causal
inference with high-dimensional complex data has become a fundamental
problem in many disciplines, such as medicine, econometrics, and social
science. However, the existing methods for causal inference are frequently
developed under the assumption that the data dimension is low or that
the underlying data generation process is linear or approximately linear.
To address these challenges, this paper proposes a novel causal inference
approach for dealing with high-dimensional complex data. The proposed
approach is based on deep learning techniques, including sparse deep learning
theory and stochastic neural networks, that have been developed in recent
literature. By using these techniques, the proposed approach can address
both the high dimensionality and unknown data generation process in a
coherent way. Furthermore, the proposed approach can also be used when
missing values are present in the datasets. Extensive numerical studies
indicate that the proposed approach outperforms existing ones.
1
Introduction
Causal inference is a fundamental problem in many disciplines such as medicine, econometrics
and social science. The problem can be formulated under the potential outcomes framework
by Rubin (1974). Let X ∈Rp denote a vector of p-dimensional confounders. In this paper,
we consider only the binary treatment A ∈{0, 1}, but discuss extensions to multiple-level
treatments or continuous treatments later. For each subject at each treatment level a, we
assume there exists a potential outcome Y (a) that can be observed under the actual treatment.
We are interested in estimating the average treatment effect (ATE) τ = E[Y (1) −Y (0)]. It is
known that ATE is identifiable if all confounders that influence both treatment and outcome
are observed and the ignorability and overlapping conditions (see Assumption A1) are satisfied.
To estimate ATE, a variety of methods, such as outcome regression, augmented/inverse
probability weighting (AIPW/IPW) and matching, have been developed. See Imbens (2004)
and Rosenbaum (2002) for overviews. These methods often work under the assumptions:
Assumption 1. (Outcome model) The parametric model µa(X, θa) is a correct specification
for the outcome function µa(X) = E[Y (a)|X], a ∈{0, 1}; i.e., µa(X) = µa(X, θ∗
a) and θ∗
a
is the true model parameter.
Assumption 2. (Treatment model) The parametric model p(X, θs) is a correct specification
for the propensity score p(X) = P(A = 1|X); i.e., p(X) = p(X, θ∗
s) and θ∗
s is the true
model parameter.
1
arXiv:2403.18994v1  [stat.ML]  27 Mar 2024
### Page 2

Let ˆθa and ˆθs be consistent estimators of θ∗
a and θ∗
s, respectively. For example, the AIPW
estimator of the ATE is given by
ˆτn = 1
n
n
X
i=1

AiYi
p(Xi, ˆθs)
−Ai −p(Xi, ˆθs)
p(Xi, ˆθs)
µ1(Xi, ˆθ1) −
(1 −Ai)Yi
1 −p(Xi, ˆθs)
−Ai −p(Xi, ˆθs)
1 −p(Xi, ˆθs)
µ0(Xi, ˆθ0)

,
(1)
which is doubly robust (Robins et al. (1994)) in the sense that ˆτn is consistent if either
Assumption 1 or 2 holds and locally efficient if both assumptions hold.
In practice, estimating the ATE often poses two main difficulties: (i) high dimensionality
of covariates, which is common in genomic data (Bühlmann, 2013; Schwab et al., 2020),
environmental and healthcare data (Antonelli et al., 2019), and social media data (Sharma
et al., 2020); and (ii) unknown functional forms of the outcome and propensity score. Various
methods have been proposed to address these challenges but in a separate manner. For
example, Lasso (Tibshirani, 1996) and other regularization methods have been used to select
relevant covariates for high-dimensional problems under the linear model framework (Belloni
et al., 2014; Farrell, 2015). On the other hand, deep neural networks have been employed to
estimate the outcome and propensity score functions for low-dimensional data (Shi et al.,
2019; Farrell et al., 2021). However, none of these methods address both difficulties in a
unified manner. Furthermore, missing values are often present in the datasets, which further
complicates the causal inference problem (Yang et al., 2019; Guan & Yang, 2019).
Building on existing works on stochastic neural networks (Liang et al., 2022; Sun & Liang,
2022) and sparse deep learning (Liang et al., 2018b; Sun et al., 2022), we propose a Causal
Stochastic Neural Network, which is abbreviated as Causal-StoNet in what follows, for
addressing the above difficulties encountered in causal inference for high-dimensional complex
data. The merits of Causal-StoNet are three-folds:
1. A natural forward-modeling framework. As described in Section 2, the StoNet
has been formulated as a composition of multiple simple linear and logistic regres-
sions, providing a natural forward-modeling framework for complex data generation
processes. In Causal-StoNet, we replace a hidden neuron at an appropriate hidden
layer by a visible treatment variable. With its compositional regression structure,
Causal-StoNet easily extends to various causal inference scenarios, e.g. missing
covariates, multi-level or continuous treatments, and mediation analysis, as discussed
in Section 5.
2. Universal approximation ability. We prove that the StoNet possesses a valid
approximation to a deep neural network, thereby enabling it to possess the universal
approximation ability to the outcome and propensity score functions.
3. Consistent sparse learning. By imposing an appropriate sparse penalty/prior on
the structure of the StoNet, relevant variables to the outcome and propensity score
can be identified along with the training of the Causal-StoNet even under the setting
of high-dimensional covariates. As a result, the outcome and propensity score can
be properly estimated even when their exact functional forms are unknown.
In summary, the Causal-StoNet has successfully tackled the issues of high-dimensional
covariates, unknown functional forms, and missing data in a holistic manner, providing a
robust and reliable approach of causal inference for high-dimensional complex data.
Related Works
In the literature, there are quite a few works employing deep neural
networks for causal inference, see e.g., Shi et al. (2019) and Farrell et al. (2021). However, the
consistency of the deep neural network estimator is not established in Shi et al. (2019). This
property has been studied in Farrell et al. (2021) but under the low-dimensional scenario
essentially. Otherwise, it requires the underlying outcome and propensity score functions to
be highly smooth with the smoothness degree even higher than the data dimension p. In
addition, the methods in Shi et al. (2019) or Farrell et al. (2021) cannot perform covariate
selection, and they are hard to apply when the dataset contains missing values. Quite
recently, Chen et al. (2024) proposed some neural network-based ATE estimators, where
only the propensity score or the outcome function is approximated using a neural network.
2
### Page 3

There are also numerous semi-parametric casual estimation methods in the literature. Causal
trees (Athey & Imbens, 2015; Li et al., 2015) develops data-driven approach to estimate
heterogeneous treatment effect for subpopulations. Super learner (van der Laan et al.,
2007) utilizes an ensemble of different models to enhance the causal effect estimation.
Targeted maximum likelihood estimation (van der Laan & Rubin, 2006) proposes a flexible
semi-parametric framework based on targeted regularization. These methods can also be
combined with deep learning or other machine learning models, but the flexibility of the
StoNet in forward modeling of complex data generation processes leads to the uniqueness of
Causal-StoNet. It can function effectively in various data scenarios, as discussed in Section 5.
2
A Brief Review of Stochastic Neural Networks
The StoNet can be briefly described as follows. Consider a DNN model with h hidden layers.
For the sake of simplicity, we assume that the same activation function ψ(·) is used for all
hidden units. By separating the feeding and activation operators of each hidden unit, we
can rewrite the DNN model in the following form:
˜Y1 = b1 + w1X,
˜Yi = bi + wiΨ( ˜Yi−1),
i = 2, 3, . . . , h,
Y = bh+1 + wh+1Ψ( ˜Yh) + eh+1,
(2)
where eh+1 ∼N(0, σ2
h+1Idh+1) is Gaussian random error; ˜Yi, bi ∈Rdi for i = 1, 2, . . . , h;
Y , bh+1 ∈Rdh+1; Ψ( ˜Yi−1) = (ψ( ˜Yi−1,1), ψ( ˜Yi−1,2), . . . , ψ( ˜Yi−1,di−1))T for i = 2, 3, . . . , h + 1,
and ˜Yi−1,j is the jth element of ˜Yi−1; wi ∈Rdi×di−1 for i = 1, 2, . . . , h + 1, and d0 = p
denotes the dimension of X. For simplicity, we consider only the regression problems in (2).
By replacing the third equation in (2) with a logit model, the DNN model can be extended
to classification problems.
The StoNet is a probabilistic deep learning model and constructed by adding auxiliary noise
to ˜Yi’s for i = 1, 2, . . . , h in (2). Mathematically, the StoNet model is given by
Y1 = b1 + w1X + e1,
Yi = bi + wiΨ(Yi−1) + ei,
i = 2, 3, . . . , h,
Y = bh+1 + wh+1Ψ(Yh) + eh+1,
(3)
as a composition of many simple regressions, where Y1, Y2, . . . , Yh can be viewed as latent
variables. Further, we assume that ei ∼N(0, σ2
i Idi) for i = 1, 2, . . . , h + 1. For classification
problems, σ2
h+1 plays the role of temperature for the binomial or multinomial distribution
formed at the output layer, and it works with {σ2
1, . . . , σ2
h} together to control the variation
of the latent variables {Y1, . . . , Yh}.
It has been shown in Liang et al. (2022) that the StoNet is a valid approximator to the
DNN, i.e., asymptotically they have the same loss function as the training sample size n
becomes large. Let θi = (wi, bi), let θ = (θ1, θ2, · · · , θh+1) denote the parameter vector of
the StoNet, let dθ denote the dimension of θ, and let Θ denote the space of θ. Let L : Θ →R
denote the loss function of the DNN as defined in (2), which is given by
L(θ) = −1
n
n
X
i=1
log π(Y (i)|X(i), θ),
(4)
where i indexes the training samples. Under appropriate settings for σi’s, the activation
function ψ, and the parameter space Θ, see Assumption A2 (in Appendix), Liang et al.
(2022) showed that the StoNet and the DNN have asymptotically the same training loss
function, i.e.,
sup
θ∈Θ

1
n
n
X
i=1
log π(Y (i), Y (i)
mis|X(i), θ) −1
n
n
X
i=1
log π(Y (i)|X(i), θ)

p→0,
as
n →∞,
(5)
where Ymis = (Y1, Y2, . . . , Yh) denotes the collection of all latent variables as defined in
(3). The StoNet can work with a wide range of Lipschitz continuous activation functions
3
### Page 4

such as tanh, sigmoid and ReLU. As explained in Liang et al. (2022), Assumption A2 also
restricts the size of the noise added to each hidden unit by setting: σ1 ≤σ2 ≤· · · ≤σh+1,
σh+1 = O(1), and dh+1(Qh
i=k+1 d2
i )dkσ2
k ≺
1
h for any k ∈{1, 2, . . . , h}, where the factor
dh+1(Qh
i=k+1 d2
i )dk can be understood as the amplification factor of the noise ek at the
output layer. In general, the noise added to the first few hidden layers should be small to
prevent large random errors propagated to the output layer.
Further, it is assumed that each θ for the DNN is unique up to some loss-invariant transfor-
mations, such as reordering some hidden units and simultaneously changing the signs of some
weights and biases, see Liang et al. (2018b) and Sun et al. (2022) for similar assumptions
used in the study. Then, under some regularity assumptions for the population negative
energy function Q∗(θ) = E(log π(Y |X, θ)), see Assumption A3, Liang et al. (2022) showed
∥ˆθn −θ∗∥
p→0,
as n →∞,
(6)
where ˆθn = arg maxθ∈Θ{ 1
n
Pn
i=1 log π(Y (i), Y (i)
mis|X(i), θ)}, and θ∗= arg maxθ∈Θ Q∗(θ).
That is, the DNN (2) can be trained by training the StoNet (3); they are asymptotically
equivalent as n →∞, thereby the universal approximation property also holds for the StoNet.
It is worth noting that in forward prediction, the StoNet ignores auxiliary noise added to
hidden neurons and thus performs as the DNN.
3
Causal-StoNet
3.1
The Structure
The StoNet provides a unified solution for the challenges faced in causal inference for high-
dimensional complex data. In this section, we address the challenges of high-dimensional
covariates and unknown functional forms of the outcome and propensity score, leaving the
treatment of missing data to Section 5.
Figure 1 illustrates the structure of the Causal-StoNet, where the treatment variable is
encompassed as a visible unit in an intermediate hidden layer. The compositional regression
architecture of the StoNet ensures seamless computational handling of this setup without
introducing any computational complexities. Let A denote the treatment variable. The
Causal-StoNet is to learn a decomposition of the joint distribution
π(Y , Ymis, A|X, θ) ∝π(Y1|X, θ1)π(Y2|Y1, θ2)π(A|Y1, θ2)π(Y3|Y2, A, θ3)π(Y |Y3, θ4),
(7)
where Ymis = (Y1, Y2, Y3), θ = (θ1, θ2, θ3, θ4), and π(A|Y1, θ2) corresponds to the propensity
score. For the visible binary treatment unit, a sigmoid activation function can be used for
its probability interpretation.
⋯⋯
𝑌!
Input 𝑋
⋯⋯
⋯⋯
⋯⋯
⋯⋯
𝜓(𝑌!)
𝑌"
𝜓(𝑌")
⋯⋯
⋯⋯
𝑌#
𝜓(𝑌#)
Output 𝑌
×
×
missing
treatment
missing
Figure 1: Causal-StoNet Structure: the treatment is included as a visible unit (rectangle)
in a middle layer, and Y2 denotes the latent variable of that layer but with the unit directly
feeding to the treatment rectangle excluded; ‘x’ represents possible missing values.
4
### Page 5

To ensure that a sparse Causal-StoNet can be learned for high-dimensional data, where the
number of covariates p can be much larger than the sample size n, we will follow Sun et al.
(2022; 2021) to impose a mixture Gaussian prior on each component of θ, i.e.,
θ ∼λnN(0, σ2
1,n) + (1 −λn)N(0, σ2
0,n),
(8)
where θ denotes a generic weight and bias of the Causal-StoNet, λn ∈(0, 1) is the mixture
proportion, σ2
0,n is typically set to a very small number, while σ2
1,n is relatively large.
Let µ∗(x, A) denote the true outcome function, and let p∗(x) denote the true propensity
score function. Let ˆµ(x, A; ˆθn) denote the DNN estimator of µ∗(x, A), and let ˆp(x; ˆθn)
denote the DNN estimator of p∗(x). For a given estimator ˆθn, both ˆµ(x, A; ˆθn) and ˆp(x; ˆθn)
are calculated as for the conventional DNN model (2) by ignoring the random errors ei’s.
Let γ∗= {γi : i = 1, 2, . . . , dθ} denote the true sparse structure of the Causal-StoNet,
which is defined through a sparse DNN as in (A5). Here γi is an indicator for the existence
of connection ci. Following Sun et al. (2022), for each i ∈{1, 2, . . . , dθ}, we set ˆγi = 1
if the corresponding weight |ˆθi| >
√
2σ0,nσ1,n
√
σ2
1,n−σ2
0,n
r
log

1−λn
λn
σ1,n
σ0,n

and 0 otherwise. Denote
the estimated sparse Causal-StoNet structure by ˆγ(ˆθn) = {ˆγi : i = 1, 2, . . . , dθ}. Under
appropriate conditions, we can show that the sparse Causal-StoNet leads to consistent
estimates for µ∗(x, A), p∗(x), and γ∗. This can be summarized as the following theorem,
whose proof is given in the appendix.
Theorem 1. Assume that the mixture Gaussian prior (8) is imposed on each connection of
the StoNet, Assumptions A2–A5 hold, and rn ≺n3/16. As n →∞, the following results hold:
(a) (Propensity score function) With probability greater than 1 −exp{cnϵ2
n} for some
constant c,
Ex[(ˆp(x; ˆθn) −p∗(x))2] = O

ϵ2
n + e−cnϵ2
n/16
+ o(n−1/2).
(b) (Outcome function) If µ∗(x) is bounded and the activation function ψ(·) ∈[−1, 1],
then, with probability greater than 1 −exp{cnϵ2
n} for some constant c,
Ex(|ˆµ(x, A; ˆθn) −µ∗(x)|2) = O

(ϵ2
n + e−cnϵ2
n)L
2
n

+ o(n−1/2).
(c) (Structure selection) If Assumption A6 also holds, then P(ˆγ(ˆθn) = γ∗)
p→1.
By Theorem 1, the sparse Causal-StoNet provides consistent estimators for both the propen-
sity score and outcome functions. Therefore, these estimators can be plugged into equation
(1) to get a double robust estimator for ATE. Moreover, the sparse Causal-StoNet also
provides consistent identification for the covariates relevant to the treatment and outcome
variables, which ensures that the covariates selected for the propensity score function are
contained in those selected for the outcome function.
Regarding theoretical properties of the ATE estimator, we have Theorem 2 by following the
theory established in Farrell (2015).
Theorem 2. Suppose Assumptions A1–A5 hold. Additionally, assume that the mixture
Gaussian prior (8) is imposed on each connection of the StoNet, rn ≺n3/16, and n−1+ξ ≺
ϖ2
n ≺n−1
2 −ξ, and specify the network structure such that 0.5+ξ < ε < 1−ξ and Ln = O(nξ)
for some 0 ≤ξ < 1/4. Then the following results hold:
(a) V −1/2
τ
√n(ˆτn −τ ∗)
d→N(0, 1), where Vτ is given in Supplement A.5, and τ ∗denotes
the true value of the ATE.
(b) ˆVτ −Vτ
p→1, where the estimator ˆVτ is given in Supplement A.5.
(c) (Uniformaly valid inference) Let Pn be a set of data-generating process satisfying
Assumption A1. Then for cα = Φ−1(1 −α/2), we have
sup
Pn∈Pn
PPn

τ ∗∈

ˆτn ± cα
q
ˆVτ/n

−(1 −α)
 →0.
5
### Page 6

We note that by the theory of the StoNet, we can also estimate the propensity score
and outcome functions separately by running two sparse DNNs in the way of double
machine learning (Chernozhukov et al., 2018). However, in this double machine learning
implementation, the covariates selected for the propensity score function might not be a
subset of those selected for the outcome function, leading to ambiguity in interpretation for
the role that certain covariates play in the causal system. The Causal-StoNet avoids this
issue by jointly estimating the propensity score and outcome functions.
3.2
Adaptive Stochastic Gradient MCMC for Training Causal-StoNet
As implied by Theorem 1, training the Causal-Stonet can be boiled down to solving a high-
dimensional parameter estimation problem with latent variables present, i.e., maximizing
n
X
i=1
log π(Y (i), Y (i)
mis, A|X(i), θ) + log π(θ).
(9)
To maximize (9), a feasible method is adaptive stochastic gradient Markov chain Monte
Carlo (SGMCMC), which, by the Bayesian version of Fisher’s identity (Song et al., 2020),
converts the optimization problem to a mean-field equation solving problem:
h(θ) :=
Z
H(Ymis, θ)dπ(Ymis|X, Y , A, θ) = 0,
(10)
where H(Ymis, θ) = ∇θ log π(Y , Ymis, A|X, θ) + ∇θ log π(θ).The adaptive SGMCMC algo-
rithm works under the framework of stochastic approximation MCMC (Benveniste et al.,
1990; Liang et al., 2007). It can be briefly described as follows.
For simplicity of notation, we rewrite (10) in the following equation:
h(θ) = E[H(Z, θ)] =
Z
H(z, θ)π(z|θ)dz = 0,
(11)
where Z is a latent variable and π(z|θ) is a probability density function parameterized by
θ ∈Θ. The algorithm works by iterating between the following two steps:
(a) (Sampling) Simulate z(k+1) ∼π(z|θ(k)) via a transition kernel induced by a SGM-
CMC algorithm such as stochastic gradient Langevin dynamics (Welling & Teh,
2011) and stochastic gradient Hamilton Monte Carlo (SGHMC) (Chen et al., 2014).
(b) (Parameter updating) Set θ(k+1) = θ(k) + γk+1H(z(k+1), θ(k)), where γk+1 denotes
the step size used in the stochastic approximation procedure.
This algorithm is called adaptive SGMCMC as the transition kernel used in step (a) changes
along with the working estimate θ(k). Applying the adaptive SGHMC algorithm to (10)
leads to Algorithm 1 (in Appendix A.1), where SGHMC is used for simulation of the latent
variables Ymis at each iteration. The convergence of the adaptive SGHMC algorithm has
been studied in Liang et al. (2022).
Lemma 1. (Liang et al. (2022)) Suppose Assumptions A8-A13 hold. In Algorithm 1, if
we set ϵk,i = Cϵ/(ce + kα) and γk,i = Cγ/(cg + kα) for some constants α ∈(0, 1), Cϵ > 0,
Cγ > 0, ce ≥0 and cg ≥0, then there exists an iteration k0 and a constant λ0 > 0 such that
for any k > k0,
E(∥ˆθ(k) −bθ∗
n∥2) ≤λ0γk,
(12)
where bθ∗
n denotes a solution to equation (10).
In Liang et al. (2022), an explicit expression of λ0 has been given. For simplicity, we have
the expression omitted in this paper. Next, Liang et al. (2022) showed that as k →∞, the
imputed latent variable z(k) converges weakly to the desired posterior distribution π(z|θ∗)
in 2-Wasserstein distance. Similarly, we establish Lemma 2 which can be used in statistical
inference for the problems with missing data being involved.
Lemma 2. Suppose Assumptions A8-A13 hold. Then for any bounded function ϕθ∗(·),
\
EKϕ ˆθ∗(z) −
R
ϕ ˆθ∗(z)dπ(z|ˆθ∗)
p→0 as K →∞, where
\
EKϕ ˆθ∗(z) =
1
K
PK
i=1 ϕ ˆθ(i)(z(i)) and
{(ˆθ(i), z(i)) : i = 1, 2, . . . , K} denotes a set of parameter estimates and imputed latent
variables that are collected in a run of the SGHMC algorithm.
6
### Page 7

4
Numerical Examples
4.1
Setup
Baselines. We compare Causal-StoNet with the following baselines: (1) Designed for average
treatment effect: double selection estimator (DSE)(Belloni et al., 2014), approximate residual
balancing estimator (ARBE) (Athey et al., 2018), targeted maximum likelihood estimator
(TMLE) (van der Laan & Rubin, 2006), and deep orthogonal networks for unconfounded
treatments (DONUT) (Hatt & Feuerriegel, 2021); (2) Designed for heterogeneous treatment
effect: X-learner (Künzel et al., 2017), Dragonnet(Shi et al., 2019), causal multi-task deep
ensemble (CMDE) (Jiang et al., 2023)), causal effect variational autoencoder (CEVAE)
(Louizos et al., 2017), generative adversarial networks (GANITE) (Yoon et al., 2018), and
counterfactual regression net (CFRNet) 1.
Performance metrics. We consider these metrics: (a) estimation accuracy of ATE, which is
measured by the mean absolute error (MAE) of the ATE estimates; (ii) estimation accuracy
of CATE, which is measured by precision in estimation of heterogeneous effect (PEHE); and
(iii) covariate selection accuracy for the treatment and outcome models, which is measured
by false and negative selection rates (FSR and NSR) as defined in Section A.7.2.
4.2
Simulation with Varying Sample Size
We ran simulated experiment with covariate dimension p = 1000 and training sample size
n = 800, 1600, 2400, 3200, 4000, respectively. For each scenario, 10 simulated datasets are
generated as described in Section A.7.1. Both the outcome and treatment effect functions in
this experiment are nonlinear. As DSE and ARBE are formulated under linear assumptions,
we didn’t include them as baselines to ensure a fair comparison.
In each experiment,
Algorithm 1 was executed 10 times, and the best model was selected based on BIC, as
suggested by Sun et al. (2022). This setting will be default for all the experiments unless
otherwise stated.
The results are depicted in Figure 2, demonstrating that Causal-StoNet maintains stable
performance even with high-dimensional covariates and small sample sizes. Additionally,
we conducted further simulations to investigate covariate selection accuracy and address
missing value problems, as detailed in Section A.7.2.
800
1600
2400
3200
4000
Training samples
0.0
0.2
0.4
0.6
0.8
1.0
1.2
In-Sample MAE
800
1600
2400
3200
4000
Training samples
Out-of-Sample MAE
Causal-StoNet
CMDE
CEVAE
GANITE
X-learner-RF
CFRNet-MMD
DONUT
Dragonnet
TMLE-ensemble
Figure 2: In-sample MAE and Out-of-Sample MAE of ATE estimation with varying training
sample sizes. In-sample MAE is calculated over training and validation sets, Out-of-Sample
MAE is calculated over test set
1The code of the experiments is available at: https://github.com/nixay/Causal-StoNet
7
### Page 8

4.3
Atlantic Causal Inference Conference 2019 Data Challenge
The Causal-StoNet is compared with baseline methods on 10 synthetic datasets with ho-
mogeneous treatment effect from the Atlantic Causal Inference Conference (ACIC) 2019
Data Challenge. Each dataset contains 200 covariates with binary treatment variable, and
the outcome variable is continuous. Since they both are synthetic, the true ATE is known.
Results in Table 1 demonstrate that Causal-StoNet consistently provides more accurate
estimates than the competitive methods.
Table 1: ATE estimation across 10 ACIC 2019 datasets, where the number in the parentheses
is the standard deviation of the MAE.
Method
In-Sample
Out-of-Sample
Causal-StoNet
0.0501(0.0118)
0.0542(0.0132)
DSE
0.0776(0.0193)
0.1632(0.0251)
ARBE
0.0729(0.0166)
0.1335(0.0179)
TMLE(Lasso)
0.0869(0.0164)
0.0867(0.0165)
TMLE(ensemble)
0.1140(0.0394)
0.1316(0.0429)
DONUT
0.5294 (0.2640)
0.5290(0.2642)
Table 2: CATE estimation for an ACIC
2019 dataset.
Method
ϵPEHE
ϵATE
Causal-StoNet
0.0893
0.0118
CMDE
0.0823
0.0444
CMGP
0.2156
0.0258
CEVAE
0.0867
0.0358
GANITE
0.1913
0.0485
X-Learner-RF
0.1877
0.0203
X-Learner-BART
0.0873
0.0720
CFRNet-Wass
0.1182
0.0421
CFRNet-MMD
0.1158
0.0849
In addition to ATE, we also consider the condi-
tional average treatment effect (CATE), which
measures the heterogeneous treatment effect for
subpopulations or individuals based on their co-
variates x ∈Rp and is defined by
τ(x) = E[Y (1) −Y (0)|X = x].
We evaluated Causal-StoNet’s performance in
CATE estimation on an ACIC 2019 dataset with
heterogeneous treatment effect, where both the
treatment and the outcome are binary, using
two metrics: ϵPEHE (square root of the Precision
in Estimation of Heterogeneous Effect (PEHE))
and ϵATE (absolute error of estimated ATE). The
results in Table 2 show that while Causal-StoNet slightly lags behind CMDE, CEVAE, and
X-Learner-BART in ϵPEHE, it achieves the lowest ϵATE.
4.4
Twins Data
We analyzed a dataset of twin births from 1989 to 1991 in the United States. The treatment
variable is binary, with a = 1 denoting the heavier twin at birth; and the outcome variable
is binary, with Y = 1 indicating twin mortality within the first year. We regard each
twin-pair’s records as potential outcomes, allowing us to find the true ATE. The dataset
includes 46 covariates. Refer to A.7.3 for data preprocessing steps. After data pre-processing,
we obtained a dataset with 4,821 samples. In this final dataset, mortality rates for lighter
and heavier twins are 16.9% and 14.42%, respectively, resulting in a true ATE of −2.48%.
We conducted the experiment in three-fold cross validation, where we partitioned the dataset
into three subsets, trained the model using two subsets and estimated the ATE using the
remaining one. Table 3 reports the averaged ATE over three folds and the standard deviation
of the average. Causal-StoNet yields a more stable ATE estimate than baseline methods.
Table 3: ATE estimates by different methods for twins data
Causal-StoNet
DSE
ARBE
TMLE(Lasso)
TMLE(ensemble)
DONUT
-0.0232(0.0042)
-0.0405(0.0176)
-0.0096 (0.0201)
-0.1103(0.0599)
-0.1290(0.0779)
-0.0738(0.0128)
Table A2 shows the covariates selected by Causal-StoNet for the propensity score and outcome
models in the three-fold cross-validation experiments. As expected, some covariates that are
known to be relevant to the outcome, such as gestat10, have been selected for both the
treatment and outcome models.
8
### Page 9

5
Some Variants of Causal-StoNet
The proposed Causal-StoNet can be easily extended to various scenarios of causal inference,
such as covariates with missing values, multi-level or continuous treatments, and the presence
of mediation variables. The extensions can be briefly described as follows.
Missing at Random (MAR)
Let Xobs denote the observed covariates, let Xmis denote
the missed covariate values, and let R denote the missing pattern represented as a binary
vector. Under the mechanism of missingness at random, i.e., Xmis
|=
R|(Xobs, A, Y ), the
Causal-StoNet as depicted in Figure 1 is to learn a decomposition of the joint distribution
π(Y , Ymis, Xmis, A|Xobs, R, θ) ∝π(Xmis|Xobs)π(Y1|Xobs, Xmis, θ1)π(Y2|Y1, θ2)
× π(A|Y1, θ2)π(Y3|Y2, A, θ3)π(Y |Y3, θ4),
(13)
where Ymis = (Y1, Y2, Y3), θ = (θ1, θ2, θ3, θ4), π(A|Y1, θ2) corresponds to the propensity
score, and π(Xmis|Xobs) can be formulated in graphical models (see e.g. Liang et al. (2018a))
and will not be detailed here. It is easy to see that in this scenario, the Causal-StoNet can
still be trained using Algorithm 1 by treating Xmis as part of the latent variables. Statistical
inference with imputed missing data can then be made based on Lemma 2.
Missing not at Random (MNAR)
The Causal-StoNet can also be extended to the
scenario of MNAR, where the missing pattern depends on the missing values themselves even
after controlling for observed data. To make the full data distribution identifiable, following
Yang et al. (2019), we will assume that the missing pattern R is independent of the outcome
given the treatment and confounders, i.e., Y
|=
R|(A, Xobs, Xmis). Under this assumption,
π(Y , Ymis, Xmis, A|Xobs, R, θ) ∝π(Xmis|Xobs)π(A|Xobs, Xmis, θ)π(R|Xobs, Xmis, A, θ)
× π(Y |Xobs, Xmis, A, θ).
To accommodate the term π(R|Xobs, Xmis, A, θ) in the decomposition, we can include some
extra visible units for R at some layer between the treatment layer and the output layer.
Note that the R units will not be forwardly connected to the output layer.
Multilevel or Continuous Treatment Variables
The extension of the Causal-StoNet
to this scenario is straightforward. For continuous treatment variable, the Causal-StoNet
as depicted in Figure 1 can be directly applied with an appropriate modification of the
activation function for the treatment neuron. For multilevel treatment variable, we can
simply include multiple visible treatment neurons in the sample hidden layer, with a softmax
activation function being used for them.
Causal Mediation Analysis
In this scenario, we aim to measure how the treatment
effect is affected by intermediate/mediation variables. For example, Pearl (2001) gave an
example where the side effect of a drug may cause patients to take aspirin, and the latter has
a separate effect on the disease that the drug was originally prescribed for. The mediation
analysis can be easily conducted with the Causal-StoNet by including some extra visible
units for mediation variables at some layer between the treatment layer and the output layer.
The mediation units was fed by the treatment unit and other hidden units of the same layer,
and then feeds forward to cast its effect on the outcome layer.
6
Conclusion
We have developed an effective method for causal inference with high-dimensional complex
data, which addresses the difficulties, including high-dimensional covariates, unknown treat-
ment and outcome functional forms, and missing data, that are frequently encountered in the
practice of modern data science. The proposed method does not only possess attractive the-
oretical properties, but also numerically outperforms the existing methods as demonstrated
by our extensive examples.
The Causal-StoNet introduces an innovative deep neural network structure, incorporating
visible neurons in its middle layers. Its stochastic deep learning nature renders Causal-StoNet
essentially a universal tool for causal inference. It can model complex data generation
processes in a forward manner, consistently identify relevant features, and provide accurate
approximation to the underlying functions. Furthermore, the flexibility of adaptive SGMCMC
algorithms, which impute latent variables (and handle missing data) while consistently
estimating model parameters, greatly facilitates the computation of Causal-StoNet.
9
### Page 10

References
Christophe Andrieu, Eric Moulines, and Pierre Priouret. Stability of stochastic approximation
under verifiable conditions. SIAM Journal on Control and Optimization, 44(1):283–312,
2005.
Joseph Antonelli, Giovanni Parmigiani, and Francesca Dominici. High-dimensional confound-
ing adjustment using continuous spike and slab priors. Bayesian analysis, 14 3:805–828,
2019.
Susan Athey and Guido Imbens. Recursive partitioning for heterogeneous causal effects.
Proceedings of the National Academy of Sciences, 113:7353 – 7360, 2015. URL https:
//api.semanticscholar.org/CorpusID:16171120.
Susan Athey, Guido W. Imbens, and Stefan Wager. Approximate residual balancing: De-
biased inference of average treatment effects in high dimensions. Journal of the Royal
Statistical Society. Series B, Statistical methodology, 80(4):597–623, 2018.
Alexandre Belloni, Victor Chernozhukov, and Christian Hansen. Inference on treatment
effects after selection amongst high-dimensional controls. Review of Economic Studies, 81:
608–650, 2014.
Albert Benveniste, Michael Métivier, and Pierre Priouret. Adaptive Algorithms and Stochastic
Approximations. Berlin: Springer, 1990.
Peter Bühlmann. Causal statistical inference in high dimensions. Mathematical Methods of
Operations Research, 77:357–370, 2013.
Tianqi Chen, Emily Fox, and Carlos Guestrin. Stochastic gradient hamiltonian monte carlo.
In International conference on machine learning, pp. 1683–1691, 2014.
Xiaohong Chen, Ying Liu, Shujie Ma, and Zheng Zhang.
Causal inference of general
treatment effects using neural networks with a diverging number of confounders. Journal
of Econometrics, 238(1):105555, 2024. ISSN 0304-4076. doi: https://doi.org/10.1016/j.
jeconom.2023.105555. URL https://www.sciencedirect.com/science/article/pii/
S0304407623002713.
Victor Chernozhukov, Denis Chetverikov, Mert Demirer, Esther Duflo, Christian Hansen,
Whitney Newey, and James Robins. Double/debiased machine learning for treatment and
structural parameters. The Econometrics Journal, 21, 2018.
Hengjian Cui, Runze Li, and Wei Zhong. Model-free feature screening for ultrahigh dimen-
sional discriminant analysis. Journal of the American Statistical Association, 110(510):
630–641, 2015.
Wei Deng, Xiao Zhang, Faming Liang, and Guang Lin. An adaptive empirical bayesian
method for sparse deep learning. Advances in neural information processing systems, 2019:
5563–5573, 2019.
M. Farrell. Robust inference on average treatment effects with possibly more covariates than
observations. Journal of Econometrics, 189:1–23, 2015.
M. Farrell, Tengyuan Liang, and S. Misra. Deep neural networks for estimation and inference.
Econometrica, 89:181–213, 2021.
Xuefeng Gao, Mert Gürbüzbalaban, and Lingjiong Zhu. Global convergence of stochastic
gradient hamiltonian monte carlo for nonconvex stochastic optimization: Nonasymptotic
performance bounds and momentum-based acceleration. Operations Research, 2021.
Qian Guan and Shu Yang. A unified framework for causal inference with multiple imputation
using martingale. arXiv: Methodology, 2019.
Tobias Hatt and Stefan Feuerriegel. Estimating average treatment effects via orthogonal
regularization. In Proceedings of the 30th ACM International Conference on Information
& Knowledge Management, pp. 680–689, 2021.
10
### Page 11

Guido Imbens. Nonparametric estimation of average treatment effects under exogeneity: A
review. The Review of Economics and Statistics, 86:4–29, 2004.
Wenxin Jiang. Bayesian variable selection for high dimensional generalized linear models:
convergence rates of the fitted densities. The Annals of Statistics, 35(4):1487–1511, 2007.
Ziyang Jiang, Zhuoran Hou, Yiling Liu, Yiman Ren, Keyu Li, and David Carlson. Estimating
causal effects using a multi-task deep ensemble. In Proceedings of the 40 th International
Conference on Machine Learning (ICML), PMLR, pp. 680–689, 2023.
Sören R. Künzel, Jasjeet S. Sekhon, Peter J. Bickel, and Bin Yu. Metalearners for estimating
heterogeneous treatment effects using machine learning. Proceedings of the National
Academy of Sciences of the United States of America, 116:4156 – 4165, 2017.
URL
https://api.semanticscholar.org/CorpusID:73455742.
Lihua Lei and Emmanuel J. Candès. Conformal Inference of Counterfactuals and Individual
Treatment Effects. Journal of the Royal Statistical Society Series B: Statistical Methodology,
83(5):911–938, 10 2021. ISSN 1369-7412. doi: 10.1111/rssb.12445. URL https://doi.
org/10.1111/rssb.12445.
Jiuyong Li, Saisai Ma, Thuc Duy Le, Lin Liu, and Jixue Liu.
Causal decision trees.
IEEE Transactions on Knowledge and Data Engineering, 29:257–271, 2015. URL https:
//api.semanticscholar.org/CorpusID:5718772.
F. Liang, C. Liu, and R.J. Carroll. stochastic approximation in monte carlo computation.
Journal of the American Statistical Association, 102:305–320, 2007.
F. Liang, Q. Song, and K. Yu. Bayesian subset modeling for high dimensional generalized
linear models. Journal of the American Statistical Association, 108:589–606, 2013.
F. Liang, Y. Cheng, and G. Lin. Simulated stochastic approximation annealing for global
optimization with a square-root cooling schedule.
Journal of the American Statistical
Association, 109:847–863, 2014.
F. Liang, B. Jia, J. Xue, Q. Li, and Y. Luo. An imputation-regularized optimization algorithm
for high-dimensional missing data problems and beyond. Journal of the Royal Statistical
Society, Series B, 80(5):899–926, 2018a.
F. Liang, Q. Li, and L. Zhou. Bayesian neural networks for selection of drug sensitive genes.
Journal of the American Statistical Association, 113:955–972, 2018b.
Siqi Liang, Yan Sun, and Faming Liang. Nonlinear sufficient dimension reduction with a
stochastic neural network. NeurIPS, 2022.
Christos Louizos, Uri Shalit, Joris Mooij, David Sontag, Richard Zemel, and Max Welling.
Causal effect inference with deep latent-variable models. 31st Conference on Neural
Information Processing Systems (NIPS 2017), 2017.
Judea Pearl. Direct and indirect effects. In Proceedings of the 17th Conference on Uncertainty
in Artificial Intelligence (UAI), pp. 411–420, 2001.
Maxim Raginsky, Alexander Rakhlin, and Matus Telgarsky.
Non-convex learning via
stochastic gradient langevin dynamics: a nonasymptotic analysis.
In Conference on
Learning Theory, pp. 1674–1703. PMLR, 2017.
Herbert Robbins and Sutton Monro. A stochastic approximation method. The annals of
mathematical statistics, pp. 400–407, 1951.
James M. Robins, Andrea Rotnitzky, and Lue Ping Zhao. Estimation of regression coefficients
when some regressors are not always observed. Journal of the American Statistical Associa-
tion, 89:846–866, 1994. URL https://api.semanticscholar.org/CorpusID:120769390.
P. R. Rosenbaum. Observational Studies (2nd edition). Springer, New York, 2002.
11
### Page 12

Donald B. Rubin. Estimating causal effects of treatments in randomized and nonrandomized
studies. Journal of Educational Psychology, 66:688–701, 1974.
Patrick Schwab, Lorenz Linhardt, Stefan Bauer, Joachim M. Buhmann, and Walter Karlen.
Learning counterfactual representations for estimating individual dose-response curves.
ArXiv, abs/1902.00981, 2020.
Ankit Sharma, Garima Gupta, Ranjitha Prasad, Arnab Chatterjee, Lovekesh Vig, and
Gautam M. Shroff. Hi-ci: Deep causal inference in high dimensions. Journal of Machine
Learning Research, 2020.
Claudia Shi, David M. Blei, and Victor Veitch. Adapting neural networks for the estimation
of treatment effects. In NeurIPS, 2019.
Q. Song, Y. Sun, M. Ye, and F. Liang. Extended stochastic gradient mcmc for large-scale
bayesian variable selection. Biometrika, 107(4):997–1004, 2020.
Y. Sun, Q. Song, and F. Liang. Consistent sparse deep learning: Theory and computation.
Journal of the American Statistical Association, 117(540):1981–1995, 2022.
Yan Sun and Faming Liang. A kernel-expanded stochastic neural network. Journal of the
Royal Statistical Society Series B, 84(2):547–578, 2022.
Yan Sun, Wenjun Xiong, and Faming Liang. Sparse deep learning: A new framework immune
to local traps and miscalibration. NeurIPS 2021, 2021.
R. Tibshirani. Regression shrinkage and selection via the lasso.
Journal of the Royal
Statistical Society, Series B, 58:267–288, 1996.
Mark J. van der Laan and Daniel Rubin. Targeted maximum likelihood learning. The
International Journal of Biostatistics, 2(1):11, 2006.
Mark J. van der Laan, Eric C. Polley, and Alan E. Hubbard. Super learner. Statistical Appli-
cations in Genetics and Molecular Biology, 6, 2007. URL https://api.semanticscholar.
org/CorpusID:7162180.
Max Welling and Yee Whye Teh. Bayesian learning via stochastic gradient Langevin dynamics.
In ICML, 2011.
TehYee Whye, H ThieryAlexandre, and J VollmerSebastian. Consistency and fluctuations
for stochastic gradient langevin dynamics. Journal of Machine Learning Research, 2016.
Li Xie, Kun Wang, Haiquan Chen, Yanlong Shi, Yuanqi Zhang, Hao yu Lin, Yuan ke Liang,
Yingsheng Xiao, Zhi-Yong Wu, Zhongyu Yuan, and Si qi Qiu.
Markers associated
with tumor recurrence in patients with breast cancer achieving a pathologic complete
response after neoadjuvant chemotherapy. Frontiers in Oncology, 12, 2022. URL https:
//api.semanticscholar.org/CorpusID:248268528.
Shu Yang, Linbo Wang, and Peng Ding. Causal inference with confounders missing not at
random. Biometrika, 106:875–888, 2019.
Jinsung Yoon, James Jordon, and Mihaela van der Schaar. Ganite: Estimation of individual-
ized treatment effects using generative adversarial nets. In International Conference on
Learning Representations, 2018. URL https://api.semanticscholar.org/CorpusID:
65516833.
A
Appendix
A.1
Adaptive Stochastic Gradient Hamiltonian Monte Carlo Algorithm
Let (Y (s.k)
0,a
, Y (s.k)
h+1,a) = (X(s), Y (s), A(s)) denote a training sample s, and let Y (s.k)
mis,a =
(Y (s.k)
1,a
, . . . , Y (s.k)
h,a
) denote the latent variables imputed for the training sample s at iteration
k, where the subscript a indicates that the imputed values are affected by the treatment
variable A.
12
### Page 13

Algorithm 1: An Adaptive SGHMC algorithm for training StoNet
Input: total iteration number K, Monte Carlo step number tMC, the learning rate
sequence {ϵk,i : k = 1, 2, . . . , K; i = 1, 2, . . . , h + 1}, and the step size sequence
{γk,i : k = 1, 2, . . . , K; i = 1, 2, . . . , h + 1};
and the step size sequence {γk,i : k = 1, 2, . . . , K; i = 1, 2, . . . , h + 1};
Initialization: Randomly initialize the network parameters ˆθ(0) = (ˆθ(0)
1 , . . . , ˆθ(0)
h+1);
for k=1,2,. . . ,K do
STEP 0: Subsampling: Draw a mini-batch of data and denote it by Sk;
STEP 1: Backward Sampling
For each observation s ∈Sk, sample Y (s,k)
i,a
’s, in the order from layer h to layer 1,
from
π(Y (s,k)
i,a
|ˆθ(k−1)
i
, ˆθ(k−1)
i+1
, Y (s,k)
i+1,a, Y (s,k)
i−1,a) ∝π(Y (s,k)
i+1,a|ˆθ(k−1)
i+1
, Y (s,k)
i,a
)π(Y (s,k)
i,a
|ˆθ(k−1)
i
, Y (s,k)
i−1,a),
by running SGHMC in kMC steps:
Initialize v(s,0)
i
= 0, and initialize Y (s,k,0)
i,a
by the corresponding ˜Yi calculated in (2).
for l = 1, 2, . . . , tMC do
for i = h, h −1, . . . , 1 do
v(s,k,l)
i
=(1 −ϵk,iη)v(s,k,l−1)
i
+ ϵk,i∇Y (s,k,l−1)
i,a
log π

Y (s,k,l−1)
i,a
| ˆθ(k−1)
i
, Y (s,k,l−1)
i−1,a

+ ϵk,i∇Y (s,k,l−1)
i,a
log π

Y (s,k,l−1)
i+1,a
| ˆθ(k−1)
i+1
, Y (s,k,l−1)
i,a

+
p
2ϵk,iηe(s,k,l),
Y (s,k,l)
i,a
=Y (s,k,l−1)
i,a
+ ϵk,iv(s,k,l−1)
i
,
(A1)
where es,k,l ∼N(0, Idi), ϵk,i is the learning rate, and η is the friction
coefficient.
end
end
Set Y (s,k)
i,a
= Y (s,k,tMC)
i,a
for i = 1, 2, . . . , h.
STEP 2: Parameter Update
Update ˆθ(k) = (ˆθ(k)
1 , ˆθ(k)
2 , . . . , ˆθ(k)
h+1) by stochastic approximation Robbins & Monro
(1951):
ˆθ(k)
i
= ˆθ(k−1)
i
+ γk,i
 X
s∈Sk
∇θi log π(Y (s,k)
i,a
|ˆθ(k−1)
i
, Y (s,k)
i−1,a) + |Sk|
n ∇θi log π(θ)
!
,
(A2)
for i = 1, 2, . . . , h + 1, where γk,i is the step size used for updating θi.
end
A.2
Assumptions on Data Generating Process
Suppose that the dataset {(yi, ai, xi) : i = 1, 2, . . . , n} is generated from a process Pn, where
ai ∈{0, 1}, Y (a) = µa(X) + U, and U denotes random error. Pn obeys Assumption A1,
with bounds uniformly in n:
Assumption A1.
(a) {(yi, ai, xi) : i = 1, 2, . . . , n} is an i.i.d sample from (Y , A, X).
(b) (Ignorability) {Y (0), Y (1)}
|=
A|X.
(c) (Overlap) 0 < ζ1 ≤P(A = 1|X) ≤ζ2 < 1 almost surely for some ζ1 and ζ2.
(d) E[|U|4|X] ≤U for some U > 0.
(e) For some δ > 0, E[|µa(X)µ1−a(X)|1+δ] and E[|U|4+δ] are bounded.
13
### Page 14

A.3
Assumptions for StoNets
The property of the StoNet as an approximator to the DNN, i.e., asymptotically they have
the same loss function as the training sample size n →∞, has been studied in Liang et al.
(2022). A brief review for their theory is provided as follows, which form the basis for this
work.
Let θ = (w1, b1, . . . , wh+1, bh+1) denote the collection of all weights of the StoNet (3),
let Θ denote the space of θ, let Ymis = (Y1, Y2, . . . , Yh) denote the collection of all la-
tent variables, let π(Y , Ymis|X, θ) denote the likelihood function of the StoNet, and let
πDNN(Y |X, θ) denote the likelihood function of the DNN model (2). Regarding the network
structure, activation function and the variance of the latent variables, they made the following
assumption:
Assumption A2. (i) Θ is compact, i.e., Θ is contained in a dθ-ball centered at 0 with
radius r; (ii) E(log π(Y , Ymis|X, θ))2 < ∞for any θ ∈Θ; (iii) the activation function
ψ(·) is c′-Lipschitz continuous for some constant c′; (iv) the network’s depth h and widths
dl’s are both allowed to increase with n; (v) σ1 ≤σ2 ≤· · · ≤σh+1, σh+1 = O(1), and
dh+1(Qh
i=k+1 d2
i )dkσ2
k ≺1
h for any k ∈{1, 2, . . . , h}.
Assumption A2-(iii) allows the StoNet to work with a wide range of Lipschitz continuous
activation functions such as tanh, sigmoid and ReLU. Assumption A2-(v) constrains the size
of noise added to each hidden neuron, where the factor dh+1(Qh
i=k+1 d2
i )dk can be understood
as the amplification factor of the noise ek at the output layer. In general, the noise added to
the first few hidden layers should be small to prevent large random errors propagated to the
output layer. Under Assumption A2, they proved the result (5).
Further, regarding the equivalence between training the StoNet and the DNN, they
made the following assumption regarding the energy surface of the DNN. Let Q∗(θ) =
E(log πDNN(Y |X, θ)), where the expectation is taken with respect to the joint distribution
π(X, Y ). By Assumption A2-(i)&(ii) and the law of large numbers,
1
n
n
X
i=1
log πDNN(Y (i)|X(i), θ) −Q∗(θ)
p→0
(A3)
holds uniformly over Θ. They assumed Q∗(θ) satisfies the following regularity conditions:
Assumption A3. (i)Q∗(θ) is continuous in θ and uniquely maximized at θ∗; (ii) for any
ϵ > 0, supθ∈Θ\B(ϵ)Q∗(θ) exists, where B(ϵ) = {θ : ∥θ −θ∗∥< ϵ}, and δ = Q∗(θ∗) −
supθ∈Θ\B(ϵ)Q∗(θ) > 0.
Assumption A3 restricts the shape of Q∗(θ) around the global maximizer, which cannot be
discontinuous or too flat. Given nonidentifiability of the neural network model, Assumption
A3 has implicitly assumed that each θ is unique up to the loss-invariant transformations,
e.g., reordering the hidden neurons of the same hidden layer and simultaneously changing
the signs of some weights and biases. Under Assumptions A2 and A3, they proved the result
(6). In summary, we have the following lemma for the StoNet:
Lemma A1. (Liang et al., 2022) Suppose Assumptions A2 and A3 hold, and π(Y , Ymis|X, θ)
is continuous in θ. Then (5) and (6) hold.
A.4
Proof of Theorem 1
To prove Theorem 1, we first give a brief review for the theory of sparse deep learning Sun
et al. (2022). The theory under the context of Bayesian deep neural networks where each
parameter, including the bias and connection weights, is subject to a mixture Gaussian prior
distribution.
Assume that the distribution of y given x is given in a generalized linear model as
p(y, x; θ) = exp{A(µ∗(x))y + B(µ∗(x)) + C(y)},
where µ∗(x) denotes a nonlinear function of x, and A(·), B(·) and C(·) are appropriately
defined functions.
14
### Page 15

Motivated by the universal approximation ability of the DNN, they proposed to approximate
µ∗(x) using a DNN with Hn −1 hidden layers and Lh hidden units at layer h, where LHn = 1
for the output layer and L0 = pn for the input layer. Let wh ∈RLh×Lh−1 and bh ∈RLh×1,
h ∈{1, 2, ..., Hn} denote the weights and bias of layer h, and let ψh : RLh×1 →RLh×1 denote
a coordinate-wise and piecewise differentiable activation function of layer h. The DNN forms
a nonlinear mapping
µ(θ, x) = wHnψHn−1 
· · · ψ1 
w1x + b1
· · ·

+ bHn,
(A4)
where θ = (w, b) =

wh
ij, bh
k : h ∈{1, 2, ..., Hn}, i, k ∈{1, ..., Lh}, j ∈{1, ..., Lh−1}
	
denotes
the collection of all weights and biases, consisting of Kn = PHn
h=1 (Lh−1 × Lh + Lh) elements
in total. To facilitate representation of the sparse DNN, they further introduced an indicator
variable for each weight and bias of the DNN, which indicates the existence of the connection
in the network. Let γwh and γbh denote the matrix and vector of the indicator variables
associated with wh and bh, respectively. Let γ = {γwh
ij , γbh
k
: h ∈{1, 2, ..., Hn}, i, k ∈
{1, ..., Lh} , j ∈{1, ..., Lh−1}} and θγ = {wh
ij, bh
k : γwh
ij
= 1, γbh
k
= 1 ,h ∈{1, 2, ..., Hn}, i, k ∈
{1, ..., Lh}, j ∈{1, ..., Lh−1}}, which specify, respectively, the structure and associated
parameters for a sparse DNN.
Among many DNNs that can provide a good approximation to µ∗(x), they define the true
DNN model as
(θ∗, γ∗) =
arg min
(θ,γ)∈Gn, ∥µ(θ,γ,x)−µ∗(x)∥L2(Ω)≤ϖn
|γ|,
(A5)
where Gn := G(C0, C1, ε, pn, Hn, L1, L2, . . . , LHn) denotes the space of valid sparse DNNs
satisfying condition Assumption A4-(A.2) for the given values of Hn, pn, and Lh’s, and ϖn is
some sequence converging to 0 as n →∞. For any given DNN (θ, γ), the error µ(θ, γ, x) −
µ∗(x) can be generally decomposed as the network approximation error µ(θ∗, γ∗, x) −µ∗(x)
and the network estimation error µ(θ, γ, x) −µ(θ∗, γ∗, x). They generally treated ϖn as
the network approximation error. In addition, they made the following two assumptions.
Assumption A4.
A.1 The input x is bounded by 1 entry-wisely, i.e. x ∈X = [−1, 1]pn,
and the density of x is bounded in its support X uniformly with respect to n.
A.2 The true sparse DNN model satisfies the following conditions:
A.2.1 The network structure satisfies: rnHn log n +rn log Ln + sn log pn ≤C0n1−ε,
where 0 < ε < 1 is a small constant, rn = |γ∗| denotes the connectivity of γ∗,
Ln = max1≤j≤Hn−1 Lj denotes the maximum hidden layer width, sn denotes
the input dimension of γ∗.
A.2.2 The network weights are polynomially bounded: ∥β∗∥∞≤En, where En = nC1
for some constant C1 > 0.
A.3 The activation function ψ is Lipschitz continuous with a Lipschitz constant of 1.
Assumption A5. The mixture Gaussian prior (8) satisfies the conditions:
λn
=
O(1/{Kn[nHn(Lnpn)]τ}) for some constant τ
>
0,
En/{Hn log n + log Ln}1/2
≲
σ1,n ≲nα for some constant α > 0, and σ0,n ≲min

1/{√nKn(n3/2σ1,0/Hn)Hn},
1/{√nKn(nEn/Hn)Hn}
	
.
Based on the two assumptions, Sun et al. (2022) proved the following result on posterior
consistency of the sparse DNN.
Lemma A2. (Theorem 2.1; Sun et al. (2022)) Suppose Assumptions A4-A5 hold. Then there
exists an error sequence ϵ2
n = O(ϖ2
n)+O(ζ2
n) such that limn→∞ϵn = 0 and limn→∞nϵ2
n = ∞,
and the posterior distribution satisfies
P
n
π[d(pθ, pµ∗) > 4ϵn|Dn] ≥2e−cnϵ2
n
o
≤2e−cnϵ2
n,
EDnπ[d(pθ, pµ∗) > 4ϵn|Dn] ≤4e−2cnϵ2
n,
(A6)
for sufficiently large n, where c denotes a constant, Dn denotes a dataset of n i.i.d. obser-
vations, ζ2
n = [rnHn log n + rn log Ln + sn log pn]/n, pµ∗denotes the underlying true data
15
### Page 16

distribution, and pθ denotes the data distribution reconstructed by the Bayesian DNN based
on its posterior samples.
It is known that the DNN model is generally nonidentifiable due to the symmetry of the
network structure. For example, the approximation µ(θ, γ, x) can be invariant if one permutes
the orders of certain hidden nodes, simultaneously changes the signs of certain weights and
biases if tanh is used as the activation function, or re-scales certain weights and bias if Relu
is used as the activation function. To address this issue, Sun et al. (2022) considered a set of
DNNs, denoted by Ω, for which each element can be viewed as an equivalent class of DNN
models. Let ν(γ, θ) ∈Ωbe an operator that maps any neural network to Ωvia appropriate
transformations such as nodes permutation, sign changes, weight rescaling, etc. To serve the
purpose of structure selection in the space Ω, they adopted the marginal posterior inclusion
probability approach (Liang et al., 2013).
For each connection ci, they defined its marginal posterior inclusion probability by
qi =
Z X
γ
ei|ν(γ,θ)π(γ|θ)π(θ|Dn)dθ,
i = 1, 2, . . . , Kn,
(A7)
where ei|ν(γ,θ) is the indicator for the existence of connection ci in the network ν(γ, θ).
Similarly, ei|ν(γ∗,θ∗) denotes the indicator for the connection ci in the true model ν(γ∗, θ∗).
Let pµ∗denote the underlying true data distribution, and let pθ denote the data distribution
reconstructed by the Bayesian DNN based on its posterior samples. Let A(ϵn) = {θ :
d(pθ, pµ∗) ≥ϵn}, where d(p1, p2) denotes the Hellinger distance between two distributions.
Define
ρ(ϵn) =
max
1≤i≤Kn
Z
A(ϵn)c
X
γ
|ei|ν(γ,θ) −ei|ν(γ∗,θ∗)|π(γ|θ)π(θ|Dn)dθ,
which measures the structure difference between the true model and the sampled models on
the set A(ϵn)c. Further, they made the assumption:
Assumption A6. ρ(ϵn) →0, as n →∞and ϵn →0.
That is, when n is sufficiently large, if a DNN has approximately the same probability
distribution as the true DNN, then the structure of the DNN, after mapping into the
parameter space Ω, must coincide with that of the true DNN.
Let ˆγζ = {i : qi > ζ, i = 1, 2, . . . , Kn} as an estimator of γ∗= {i : ei|ν(γ∗,θ∗) = 1, i =
1, . . . , Kn}, where γ∗can be viewed as the uniquenized true model. In summary, they have
the following result regarding network structure selection:
Lemma A3. (Theorem 2.2; Sun et al. (2022)) Suppose Assumptions A4-A6 hold. Then, as
n →∞, we have
(a) (sure screening) P(γ∗⊂ˆγζ)
p→1 for any pre-specified ζ ∈(0, 1).
(b) (Consistency) P(γ∗= ˆγ0.5)
p→1.
As shown by Sun et al. (2022), Lemma A3 implies consistency of covariate selection.
For binary classification problems, the method leads to a predictive distribution ˆp(x) :=
R
p(x; θ)dπ(θ|Dn) as the Bayesian estimator of the true classification distribution p∗(x) :=
P(y = 1|x = 1). Let ˆµA(x) =
R
Aˆp(x)νA(dA) = ˆp(x), and µ∗
A(x) =
R
Ap∗(x)νA(dA) =
p∗(x).
Lemma A4. Suppose Assumptions A4-A5 hold. Then the following inequality holds with
probability greater than 1 −2 exp{cnϵ2
n},
Ex([ˆµA(x) −µ∗
A(x)]2) ≤4ϵ2
n + 16e−cnϵ2
n/16/ξ ≍ϵ2
n,
where ξ ≤π(p > 0.5|Dn) denotes a lower bound of the selection probability of the selection
rule p > 0.5, and Ex[·] denotes expectation with respect to νx, i.e., the probability measure of
x.
16
### Page 17

Proof. The proof of Lemma A4 follows from the arguments of Jiang (2007) (around equations
(23)-(25)), i.e., for binary classification, we have
Ex([ˆµA(x) −µ∗
A(x)]2) ≤4d2(ˆp(x), pµ∗) ≤4ϵ2
n + 8π[d(pθ, pµ∗) > ϵn|Dn]/ξ.
The proof can then be completed by applying the first inequality of (A6) to π[d(pθ, pµ∗) >
ϵn|Dn].
Note that the overlapping condition generally assumed for the treatments ensures that ζ is
bounded away from zero and thus the approximation 4ϵ2
n + 16e−cnϵ2
n/16/ξ ≍ϵ2
n holds.
Regarding the generalization error for regression problems, they proved the following result:
Lemma A5. (Theorem 2.6; Sun et al. (2022)) Suppose Assumptions A4-A5 hold. If Θ is
compact, the activation function ψ(·) ∈[−1, 1], and µ∗(x) is bounded, then the following
inequality holds with probability greater than 1 −2 exp{cnϵ2
n},
Ex(
Z
µ(θ, x)π(θ|Dn)dθ −µ∗(x))2 ≍(ϵ2
n + e−cnϵ2
n)L
2
n,
where ϵn is as defined in Lemma A2, and Ex(·) denotes an expectation with respect to ν(x),
the probability measure of x.
To accelerate computation, Sun et al. (2022) suggested to replace the Bayesian estimators
involved in Lemmas A3-A5 by their Laplace approximators. That is, instead of sampling
from the posterior distribution, they conducted optimization to maximize the objective
function
Ln(θ) = 1
n
n
X
i=1
log(p(yi, xi; θ)) + 1
n log(π(θ)),
(A8)
where π(θ) denotes the mixture Gaussian prior as specified in (8). Denote the resulting
maximum a posteriori (MAP) estimator by
ˆθn = arg max
θ∈Θ Ln(θ).
(A9)
Assumption A7. Assume rn = |γ∗| grows with the sample size n at a rate of o(n1/4), i.e.
rn ≺n1/4.
By invoking the Laplace approximation theorem, they show that the consistency results
established in Lemmas A3-A5 still hold for ˆθn with the approximation error decaying at a
rate of O( r4
n
n ). This leads to the following corollary:
Corollary 1. For sparse DNNs, the consistency results established in Lemmas A3-A5 also
hold for the maximum a posteriori estimator (A9), provided that Assumption A7 also holds.
Moreover, to address the local trap issue possibly encountered in maximizing (A8), Sun et al.
(2022) suggested to run an optimization procedure, such as Adam or SGD, multiple times
and select the solution according to the BIC criterion.
Proof of Theorem 1
Proof. First, we note that these results hold for the sparse DNN following from Lemmas
A3-A5 and the property of Laplace approximation. Specifically, the term o(n−1/2) in parts
(a) and (b) follows from Theorem 2.3 of Sun et al. (2022), where accuracy of the Laplace
approximation for Bayesian sparse DNNs is given as O(r4
n/n). Therefore, for the mean
squared errors in part (a), we have
Ex[(ˆp(x; ˆθn) −p∗(x))2] ≤2Ex[(ˆp(x) −p∗(x))2] + 2Ex[(ˆp(x; ˆθn) −ˆp(x))2]
= O

ϵ2
n + e−cnϵ2
n/16
+ O(r8
n/n2)
17
### Page 18

where ˆp(x) =
R
p(x; θ)dπ(θ|Dn), as defined in Lemma A4, denotes the Bayesian estimator
of p∗(x). Therefore, the result follows under the assumption rn ≺n3/16. For part (b), the
result can be justified in a similar way.
Then, by equation (5), these results can also be achieved by the Causal-StoNet which is
trained by maximizing the penalized log-likelihood function (9). This completes the proof of
the theorem.
A.5
Proof of Theorem 2
For convenience, for any a, a′ ∈{0, 1}, we define the following notations:
pa(x) = E(P(A = a|X = x)),
pa = Ex(pa(x)),
µa(x) = E(Y |A = a, X = x),
µa = E(Y (a)),
σ2
a(x) = E(U 2|A = a, X = x).
With the above notation, we have
Vτ = E
σ2
1(X)
p1(X) + σ2
0(X)
p0(X)

+ E
h
((µ1(X) −µ1) −(µ0(X) −µ0))2i
.
For estimation, we define
ˆµa(x) = ˆµ(X = x, A = a, ˆθn),
ˆpa(x) = ˆp(X = x, A = a, ˆθn),
ˆpa = 1
n
n
X
i=1
I(Ai = a),
ˆµa = 1
n
n
X
i=1
I(Ai = a)(yi −ˆµa(xi)
ˆpa(xi)
+ ˆµa(xi)

,
With the notation, we have
ˆVτ = En
I(Ai = 1)(yi −ˆµ1(xi))2
ˆp1(xi)2
+ I(Ai = 0)(yi −ˆµ0(xi))2
ˆp0(xi)2

+En
h
((ˆµ1(xi) −ˆµ1)) −(ˆµ0(xi) −ˆµ0))2i
,
where E[·] denotes the empirical mean over n samples.
Proof of Theorem 2
Proof. The results directly follow from Theorem 3 and Corollary 2 of Farrell (2015). It is
easy to verify that the conditions n−1+ξ ≺ϖ2
n ≺n−1
2 −ξ, 0.5+ξ < ε < 1−ξ, and Ln = O(nξ)
ensure that
ϵ2
n + e−cnϵ2
n/16 ≺n−1/2,
and
(ϵ2
n + e−cnϵ2
n)L
2
n ≺n−1/2,
and thus Assumption 3 of Farrell (2015) holds. Assumptions 1 and 2 of Farrell (2015) are
given in Assumption A1 of this paper. Therefore, Theorem 3 and Corollary 2 of Farrell
(2015) hold, and the statement of Theorem 2 is implied.
A.6
Convergence of the SGHMC Algorithm
Notations: We let D denote a dataset of n observations, and let Di denote the i-th observation
of D. For StoNet, Di has included both the input and output variables of the observation.
For simplicity of notation, we re-denote the latent variable corresponding to Di by Zi, and
denote by fDi(zi, θ) = −log π(zi|Di, θ) the negative log-density function of Zi. Let z =
(z1, z2, . . . , zn) be a realization of Z = (Z1, Z2, . . . , Zn), and let FD(z, θ) = Pn
i=1 fDi(zi, θ).
To study the convergence of Algorithm 1, we need the following assumptions:
Assumption A8. The function FD(·, ·) takes nonnegative real values, and there exist
constants A, B ≥0, such that |FD(0, θ∗)| ≤A, ∥∇ZFD(0, θ∗)∥≤B, ∥∇θFD(0, θ∗)∥≤B,
and ∥H(0, θ∗)∥≤B.
18
### Page 19

Assumption A9. (Smoothness) FD(·, ·) is M-smooth and H(·, ·) is M-Lipschitz: there
exists some constant M > 0 such that for any Z, Z′ ∈Rdz and any θ, θ′ ∈Θ,
∥∇ZFD(Z, θ) −∇ZFD(Z′, θ′)∥≤M∥Z −Z′∥+ M∥θ −θ′∥,
∥∇θFD(Z, θ) −∇θFD(Z′, θ′)∥≤M∥Z −Z′∥+ M∥θ −θ′∥,
∥H(Z, θ) −H(Z′, θ′)∥≤M∥Z −Z′∥+ M∥θ −θ′∥.
Assumption A10. (Dissipativity) For any θ ∈Θ, the function FD(·, θ∗) is (m, b)-dissipative:
there exist some constants m > 1
2 and b ≥0 such that ⟨Z, ∇ZFD(Z, θ∗)⟩≥m∥Z∥2 −b.
The smoothness and dissipativity conditions are regular for studying the convergence of
stochastic gradient MCMC algorithms, and they have been used in many papers such as
Raginsky et al. (2017) and Gao et al. (2021). As implied by the definition of FD(z, θ), the
values of M, m and b increase linearly with the sample size n. Therefore, we can impose a
nonzero lower bound on m to facilitate related proofs.
Assumption A11. (Gradient noise) There exists a constant ς ∈[0, 1) such that for any Z
and θ, E∥∇Z ˆFD(Z, θ) −∇ZFD(Z, θ)∥2 ≤2ς(M 2∥Z∥2 + M 2∥θ −θ∗∥2 + B2).
Introduction of the extra constant ς facilitates our study. For the full data case, we have
ς = 0, i.e., the gradient ∇ZFD(Z, θ) can be evaluated accurately.
Assumption A12. The step size {γk}k∈N is a positive decreasing sequence such that γk →0
and P∞
k=1 γk = ∞. In addition, let h(θ) = E(H(Z, θ)), then there exists δ > 0 such that for
any θ ∈Θ, ⟨θ −θ∗, h(θ))⟩≥δ∥θ −θ∗∥2, and lim infk→∞2δ
γk
γk+1 + γk+1−γk
γ2
k+1
> 0.
As shown by Benveniste et al. (1990) (p.244), Assumption A12 can be satisfied by setting
γk = ˜a/(˜b + kα) for some constants ˜a > 0, ˜b ≥0, and α ∈(0, 1 ∧2δ˜a). By (A2), δ increases
linearly with the sample size n. Therefore, if we set ˜a = Ω(1/n) then 2δ˜a > 1 can be satisfied,
where Ω(·) denotes the order of the lower bound of a function. In this paper, we simply
choose α ∈(0, 1) by assuming that ˜a has been set appropriately with 2δ˜a ≥1 held.
Assumption A13. (Solution of Poisson equation) For any θ ∈Θ, z ∈Z, and a function
V (z) = 1 + ∥z∥, there exists a function µθ on Z that solves the Poisson equation µθ(z) −
Tθµθ(z) = H(θ, z) −h(θ), where Tθ denotes a probability transition kernel with Tθµθ(z) =
R
Z µθ(z′)Tθ(z, z′)dz′, such that
H(θk, zk+1) = h(θk) + µθk(zk+1) −Tθkµθk(zk+1),
k = 1, 2, . . . .
(A10)
Moreover, for all θ, θ′ ∈Θ and z ∈Z, we have ∥µθ(z) −µθ′(z)∥≤ς1∥θ −θ′∥V (z) and
∥µθ(z)∥≤ς2V (z) for some constants ς1 > 0 and ς2 > 0.
This assumption is also regular for studying the convergence of stochastic gradient MCMC
algorithms, see e.g., Whye et al. (2016) and Deng et al. (2019). Alternatively, one can assume
that the MCMC algorithms satisfy the drift condition, and then Assumption A13 can be
verified, see e.g., Andrieu et al. (2005).
Outline of the Proof of Lemma 1
Lemma 1 can be proved in a similar way to Theorem
3.1 of Liang et al. (2022). Note that in the proof of Lemma 1, the boundedness of Θ is not
assumed.
Outline of the Proof of Lemma 2
Lemma 2 can be proved in a similar way to Theorem
3.3 of Liang et al. (2014) by ignoring the parameter τ used in the proof there and modifying
some notations appropriately.
A.7
More Numerical Results
A.7.1
An Illustrative Example with Varying Sample Size
Data Generation Procedure
10 simulation datasets are generated in the following
procedure, which is inspired by Lei & Candès (2021).
19
### Page 20

• Generate e, z1, · · · , z1000 independently from a truncated standard normal distri-
bution on the interval [−10, 10]. Set xi = e+zi
√
2
for i = 1, · · · , 1000, making the
covariates highly correlated.
• The propensity score e(x) = 1
4(1 + β2,4( 1
3(Φ(x1) + Φ(x3) + Φ(x5)))), where β2,4
is the CDF of the beta distribution with shape parameters (2, 4), and Φ denotes
the CDF of the standard normal distribution. This ensures that e(x) ∈[0.25, 0.5],
thereby providing sufficient overlap. Treatment Ai is hence generated by a Bernoulli
distibution with the probablity of success being e(xi), and resampling from the
treatment and control groups has been performed for ensuring that the dataset
contains balanced samples for treatment group and control group.
• For simulation of observed outcome, we consider
yi = c(xi) + τAi + ηi ∗Ai + σzi,
i = 1, 2, . . . , n,
c(xi) =
5x3
1 + x2
4
+ 2x5
where η(xi) = f(x1)f(x2) −E(f(x1)f(x2)) and f(x) =
2
1+exp(−x+0.5)). In other
words, we set treatment effect τ(xi) = τ + ηi. We generated the data under the
setting τ = 3 and σ = 0.25 with ntrain ∈{800, 1600, 2400, 3200, 4000}, nval ∈
{200, 400, 600, 800, 1000}, ntest ∈{200, 400, 600, 800, 1000}.
Resulsts
For TMLE, we use the ensemble of lasso and XGBoost to estimate the nuisance
functions. For X-Learner, we consider the model with Random Forest (X-Learner-RF) and
the model with Bayesian Additive Regression Trees (X-Learner-BART), but only presents the
result of X-Learner-RF, since the performance of X-Learner-RF is consistently better than
that of X-Learner-BART on our simulation dataset. For CFRNet, we consider the model
with Wasserstein distance (CFRNet-Wass) and the model with Maximum Mean Discrepancy
(CFRNet-MMD), and only presents the result of CFRNet-MMD, following a similiar logic.
For most of the benchmark models, we refer to the code implementation of (Jiang et al.,
2023). The results are summarzed in 2.
A.7.2
An Illustrative Example for Missing Data Problems
Data Generation Procedure
With the following procedure, we simulated 10 datasets
for three scenarios: a) complete data, b) missing at random (MAR), and c) missing not at
random (MNAR). Each dataset consists of 10,000 training samples, 1000 validation samples,
and 1000 test samples. In our setting, only training set contains missing values.
1. Generate x1, · · · , x100 from an auto-regressive process of order 2 with the concentra-
tion matrix given by
Ci,j =







0.5,
if |j −i| = 1, i = 2, · · · , 99.
0.25,
if |j −i| = 2, i = 3, · · · , 98.
1,
if j = i, i = 1, · · · , 100.
0,
otherwise
2. Generate the binary treatment variable A ∈{0, 1} from a Bernoulli distribution with
the success probability given by p(x1, x2, x3, x5) = 1/(1 + e−s(x1,x2,x3,x5)), where
s(x1, x2, x3, x5) = tanh(−x1 −2x5) −tanh(2x2 −2x3),
and resampling from the treatment and control groups has been performed for
ensuring that the dataset contains equal numbers of treatment and control samples.
3. Generate outcome variable Y by
Y = −4 tanh(tanh(−2 tanh(2x1 + x4) + tanh(2x2 −2x3)) −2A)
+ 2 tanh(−A + 2 tanh(tanh(2x2 −2x3) −2 tanh(−2x4 + x5)))
+ 0x6 + · · · + 0x100 + ϵ
where ϵ ∼N(0, 1) and is independent of xi’s.
20
### Page 21

4. For MAR, we randomly deleted 10% of the observations in x1 and x4 as missing
values. For MNAR, we first generate missing pattern R1 and R4, which are binary
vectors with 1 representing observed and 0 representing missing, from Bernoulli
distribution with the success probability given by p1 = 1/(1 + e−s1(x1,··· ,x100)) and
p4 = 1/(1 + e−s4(x1,··· ,x100)), where
s1(x1, · · · , x100) = 4 −2A + (−0.1)j−1x2j−1, where j = 1, · · · , 50
and
s4(x1, · · · , x100) = 4 −2A + (−0.1)jx2j, where j = 1, · · · , 50
then delete the observations based on R1 and R4. The missing rate for MNAR
scenario is roughly 10%.
Definition of the False Selection Rate (FSR) and Negative Selection Rate (NSR)
In this paper, the FSR and NSR are defined based on 10 datasets:
FSR =
P10
i=1 | ˆSi \ S|
P10
i=1 ˆSi
,
NSR =
P10
i=1 |S \ ˆSi|
P10
i=1 S
,
where S is the set of true variables, Si is the set of selected variables for dataset i, and |Si|
is the size of Si.
Results
For this experiment, we assume that we already know the neighborhood structure
of the Gaussian graphical model that represents the correlations between covariates, rendering
the distribution π(Xmis|Xobs) be correctly modeled. For case where the structure is unknown,
estimating the structure is necessary before running the Causal-StoNet. The covariate
selection accuracy and Out-of-Sample MAE of the estimated ATE are summarized in Table
A1, as compared with the result for complete dataset. The result shows that even with
missing values present in the dataset, Causal-StoNet can still correctly identify the true
covariates for the outcome and propensity score models and achieve reasonably accurate
estimates for the ATE.
Table A1:
Covariate selection accuracy and MAE of the ATE estimates for the illustrative
example of missing data.
Out-of Sample MAE
FSRY
NSRY
FSRA
NSRA
Complete
0.0103(0.0024)
0
0
0
0
MAR
0.0797(0.0134)
0
0
0
0
MNAR
0.1687(0.0284)
0
0
0
0
A.7.3
Twins Data
Data Preprocessing
In data preprocessing, we focused on the same-sex twin pairs with
born-weights less than 2 kg and assigned treatments according to ti|xi, zi ∼Bernoulli(σ(wT
o x+
wh(z/10 −0.1))). Here, σ(·) is sigmoid, wo ∼N(0, 0.1 · I), wh ∼N(5, 0.1), z represents
the covariate gestat10 (gestation weeks before birth), and x encompasses the other 45
covariates.
A.7.4
TCGA-BRCA Data
The Breast Cancer dataset from the TCGA database collects clinical data and gene ex-
pression data for breast cancer patients. The gene expression data contains the expression
measurements of 20531 genes. Our goal is to investigate the causal effect of radiation therapy
on patients’ vital status, while accounting for relevant clinical features and genetic covariates.
The treatment variable A is binary (1 for radiation therapy, 0 otherwise), and the outcome
variable Y is also binary (1 for death, 0 otherwise). For genetic covariates, we applied the
sure independence variable screening method (Cui et al., 2015) to reduce the number of
genes from 20531 to 100. After preprocessing, the dataset contains 110 covariates with a
21
### Page 22

Table A2: Covariates selected for the treatment and outcome models by the Causal-StoNet
in a three-fold cross-validation experiment for the twins data, where the number in the
parentheses indicates the times that the covariate was elected.
Treatment
Model
pldel(1), birattnd(1), mager8(3), ormoth(3), mrace(3)
meduc6(3), dmar(1), mpre5(3), adequacy(3), frace(3), birmon(3)
gestat10(3), csex(1), incervix(2), cigar6(3), crace(3), data_year(3)
nprevistq(3), dfageq(3), feduc6(3), dlivord_min(3), dtotord_min(3),
brstate_reg(3), stoccfipb_reg(3), mplbir_reg(3), bord(3)
Outcome
Model
pldel(3), birattnd(3), mager8(3), ormoth(3), mrace(3)
meduc6(3), dmar(2), mpre5(3), adequacy(3), frace(3), birmon(3),
gestat10(3), csex(3), hydra(2), incervix(3), cigar6(3), crace(3), data_year(3)
nprevistq(3), dfageq(3), feduc6(3), dlivord_min(3), dtotord_min(3)
brstate_reg(3), stoccfipb_reg(3), mplbir_reg(3), bord(3)
Table A3: ATE estimates by different methods for BRCA-TCGA data
Causal-StoNet
DSE
ARBE
TMLE(Lasso)
TMLE(ensemble)
DONUT
-0.1243 (0.0058)
-0.0378(0.0243)
-0.1497 (0.1021)
-0.0509 (0.0172)
-0.0468 (0.0153)
-0.0129 ( 0.0088)
sample size of 845. Table A3 reports the ATE estimates by different methods, with the
Causal-StoNet estimate having a smaller standard error. Table A4 summarizes the most
frequently selected covariates for both the treatment and outcome models across the three
cross-validation folds. Our method identified pathology N stage and gene ALDH3A2 as
significant variables. It is exciting to note that clinical N stage and the tumor expression
of ALDH3A2 have been reported by Xie et al. (2022) as potential markers for predicting
tumor recurrence in breast cancer patients who achieve a pathologic complete response after
neoadjuvant chemotherapy.
Table A4: Most frequently selected covariates for both the treatment and outcome models
by the Causal-StoNet in a three-fold cross-validation experiment for the TCGA-BRCA data
Clinical
Features
years to birth, date of initial pathologic diagnosis,
number of lymph nodes, pathology N stage†
Genetic
Features
ACMSD, AKAP2, ALDH3A2†, ALG1, ALMS1P, ANKLE1,
ANKRD54, AQP7P1, AZI1, B4GALT1, B4GALT2,
BCL6B, C10orf47, C10orf72
A.8
Parameters Setting Used in the Experiments
A.8.1
Causal-StoNet
Illustrated Example with Varying Sample Size
The network has 3 hidden layers with
structure 32-16-8-1, where Tanh is used as the activation function. The treatment variable
is set at the second hidden node of the second hidden layer. Variances of latent variables
are σ2
n,1 = 10−3, σ2
n,2 = 10−5, σ2
n,3 = 10−7, σ2
n,4 = 10−9. For the mixture Gaussian prior,
σ2
0 = 10−5, σ2
1 = 0.01, and λn = 10−6. The epochs for pre-training, training, and refining
after sparsification are 50, 200, and 200, respectively.
For SGHMC imputation, tHMC = 1, α = 0.1. Initial imputation learning rate is set as
ϵ1 = 3 × 10−3, ϵ2 = 3 × 10−4, ϵ3 = 5 × 10−7, and decays at training stage and refining stage.
For epoch k in these stages, the imputation learning rate is ϵk,i =
ϵi
1+ϵi×k1.2 .
For parameter update, Initial learning rate for training stage are γ1 = 10−3, γ2 = 10−6,
γ3 = 10−8, γ4 = 5×10−13, and the initial learning rate for refining stage after the sparsification
are γ1 = 10−4, γ2 = 10−7, γ3 = 10−9, γ4 = 5 × 10−14. Learning rate decays for training and
refining stage, and for epoch k in these stages, the learning rate is γk,i =
γi
1+γi×k1.4 .
22
### Page 23

Illustrated Example with Missing Value
The network has 3 hidden layers with
structure 8-6-5-1, where Tanh is used as the activation function. The treatment variable
is set at the second hidden node of the second hidden layer. Variances of latent variables
are σ2
n,1 = 10−3, σ2
n,2 = 10−5, σ2
n,3 = 10−7, σ2
n,4 = 10−9. For the mixture Gaussian prior,
σ2
0 = 3 × 10−3, σ2
1 = 0.3, and λn = 10−6. The epochs for pre-training, training, and refining
after sparsification are 100, 1500, and 200, respectively.
For SGHMC imputation, tHMC = 1, α = 0.1. Initial imputation learning rate for the
network is set as ϵ1 = 3 × 10−3, ϵ2 = 3 × 10−4, ϵ3 = 10−6, and imputation learning rate for
missing covariates imputation ϵmiss = 3 × 10−4. Both imputation learning rates decay at
training stage and refining stage. For epoch k in these stages, the imputation learning rate
is ϵk,i =
ϵi
1+ϵi×k1.2 .
For parameter update, Initial learning rate for training stage are γ1 = 10−3, γ2 = 3 × 10−6,
γ3 = 10−7, γ4 = 10−12, and the initial learning rate for refining stage after the sparsification
are γ1 = 10−4, γ2 = 3 × 10−7, γ3 = 10−8, γ4 = 10−13. Learning rate decays for training and
refining stage, and for epoch k in these stages, the learning rate is γk,i =
γi
1+γi×k1.2 .
ACIC
The network has 2 hidden layers with structure 200-64-32, where Tanh is used as
the activation function. The treatment variable is set at the second hidden node of the
first hidden layer. Variances of latent variables are σ2
n,1 = 10−5, σ2
n,2 = 10−7, σ2
n,2 = 10−9.
For the mixture Gaussian prior, σ2
0 = 2 × 10−4, σ2
1 = 0.1, and λn = 10−6. The number of
epochs for pre-training is 100. The parameters were pruned twice, first after 500 training
epochs, and second after 1000 training epochs. The first pruning can be deemed as another
initialization for the model. After the second pruning, the model was trained for another
200 epochs for refining the network parameters.
For SGHMC imputation, tHMC = 1, α = 1. Initial imputation learning rate is set as
ϵ1 = 3 × 10−4, ϵ2 = 10−6, and decays at training stage and refining stage. For epoch k in
these stages, the imputation learning rate is ϵk,i =
ϵi
1+ϵi×k.
For parameter update, Initial learning rate for training stage are γ1 = 5×10−6, γ2 = 5×10−8,
γ3 = 5 × 10−13, and the initial learning rate for refining stage after the sparsification are
γ1 = 5 × 10−7, γ2 = 5 × 10−9, γ3 = 10−13. Learning rate decays for training and refining
stage, and for epoch k in these stages, the learning rate is γk,i =
γi
1+γi×k2 .
Twins
The network has 3 hidden layers with structure 46-16-8-4, where Tanh is used as
the activation function. The treatment variable is set at the second hidden node of the
second hidden layer. Variances of latent variables are σ2
n,1 = 10−3, σ2
n,2 = 10−4, σ2
n,3 = 10−5,
σ2
n,4 = 10−6. For the mixture Gaussian prior, σ2
0 = 5 × 10−4, σ2
1 = 0.1, and λn = 10−6. The
epochs for pre-training, training, and refining after sparsification are 100, 1500, and 200,
respectively.
For SGHMC imputation, tHMC = 1, α = 1. Initial imputation learning rate is set as
ϵ1 = ×10−2, ϵ2 = 9 × 10−3, ϵ3 = 9 × 10−5, and decays at training stage and refining stage.
For epoch k in these stages, the imputation learning rate is ϵk,i =
ϵi
1+ϵi×k.
For parameter update, Initial learning rate for training stage are γ1 = 10−3, γ2 = 10−4,
γ3 = 10−5, γ4 = 10−9, and the initial learning rate for refining stage after the sparsification
are γ1 = 10−4, γ2 = 10−5, γ3 = 10−6, γ4 = 10−10. Learning rate decays for training and
refining stage, and for epoch k in these stages, the learning rate is γk,i =
γi
1+γi×k1.2 .
TCGA-BRCA
The network has 3 hidden layers with structure 110-64-16-4, where Tanh
is used as the activation function. The treatment variable is set at the second hidden node
of the second hidden layer. Variances of latent variables are σ2
n,1 = 10−3, σ2
n,2 = 10−5,
σ2
n,3 = 10−7, σ2
n,4 = 10−9. For the mixture Gaussian prior, σ2
0 = 10−5, σ2
1 = 0.01, and
λn = 10−6. The epochs for pre-training, training, and refining after sparsification are 100,
1500, and 200, respectively.
23
### Page 24

For SGHMC imputation, tHMC = 1, α = 1. Initial imputation learning rate is set as
ϵ1 = 3 × 10−3, ϵ2 = 3 × 10−4, ϵ3 = 10−6, and decays at training stage and refining stage.
For epoch k in these stages, the imputation learning rate is ϵk,i =
ϵi
1+ϵi×k1 .
For parameter update, Initial learning rate for training stage are γ1 = 10−3, γ2 = 5 × 10−5,
γ3 = 5×10−7, γ4 = 10−12, and the initial learning rate for refining stage after the sparsification
are γ1 = 10−4, γ2 = 10−6, γ3 = 10−8, γ4 = 10−13. Learning rate decays for training and
refining stage, and for epoch k in these stages, the learning rate is γk,i =
γi
1+γi×k1.2 .
24