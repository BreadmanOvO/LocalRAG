# RCBEV Radar-Camera Fusion BEV 3D Object Detection

**Source**: arxiv PDF, 18 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Fairness in Multi-Task Learning
via Wasserstein Barycenters
François Hu1[0009−0000−6093−6175], Philipp Ratz2[0000−0002−0966−5493], and
Arthur Charpentier2[0000−0003−3654−6286]
1 Université de Montréal, Montréal, Québec, Canada francois.hu@umontreal.ca
2 Université du Québec à Montréal, Montréal, Québec, Canada
ratz.philipp@courrier.uqam.ca, charpentier.arthur@uqam.ca
Abstract. Algorithmic Fairness is an established field in machine learn-
ing that aims to reduce biases in data. Recent advances have proposed
various methods to ensure fairness in a univariate environment, where the
goal is to de-bias a single task. However, extending fairness to a multi-
task setting, where more than one objective is optimised using a shared
representation, remains underexplored. To bridge this gap, we develop
a method that extends the definition of Strong Demographic Parity to
multi-task learning using multi-marginal Wasserstein barycenters. Our
approach provides a closed form solution for the optimal fair multi-task
predictor including both regression and binary classification tasks. We
develop a data-driven estimation procedure for the solution and run
numerical experiments on both synthetic and real datasets. The empirical
results highlight the practical value of our post-processing methodology
in promoting fair decision-making.
Keywords: Fairness · Optimal transport · Multi-task learning
1
Introduction
Multi-task learning (MTL) is a loosely defined field that aims to improve model
performance by taking advantage of similarities between related estimation
problems through a common representation [36,45]. MTL has gained traction
in recent years, as it can avoid over-fitting and improve generalisation for task-
specific models, while at the same time being computationally more efficient
than training separate models [6]. For these reasons, the usage of MTL is likely
to grow and spread to more disciplines, thus ensuring fairness in this setting
becomes essential to overcome historical bias and prevent unwanted discrimination.
Indeed, in many industries, discriminating on a series of sensitive features is even
prohibited by law [1]. Despite the apparent importance of fairness, it remains
challenging to incorporate fairness constraints into MTL due to its multivariate
nature.
Algorithmic fairness refers to the challenge of reducing the influence of a
sensitive attribute on a set of predictions. With increased model complexity,
simply excluding the sensitive features in the model is not sufficient, as complex
arXiv:2306.10155v2  [stat.ML]  6 Jul 2023
### Page 2

2
F. Hu, P. Ratz and A. Charpentier
models can simply proxy for omitted variables. Several notions of fairness have
been considered [5,43] in the literature. In this paper, we focus on the Demographic
Parity (DP) [8] that requires the independence between the sensitive feature
and the predictions, while not relying on labels (for other notions of fairness,
see Equality of odds or Equal opportunity [23]). This choice is quite restrictive
in the applications, but provides a first stepping stone to extend our findings to
other definitions. In single-task learning problems, the fairness constraint (such
as DP) has been widely studied for classification or regression [4,8,13,16,42,44],
but to extend fairness to multiple tasks, we first need to study the effects of
learning tasks jointly on the potential outcomes. In line with a core advantage
of MTL, the approach we propose is based on post-processing which results in
faster computations than other approaches discussed below. The contributions of
the present article can hence be summarised as follows:
Contributions We consider multi-task problems that combine regression and
binary classification, with the goal of producing a fair shared representation
under the DP fairness constraint. More specifically:
– We transform the multi-task problem under Demographic Parity fairness to
the construction of multi-marginal Wasserstein-2 barycenters. Notably, we
propose a closed form solution for the optimal fair multi-task predictor.
– Based on this optimal solution, we build a standard data-driven approach
that mimics the performance of the optimal predictor both in terms of risk
and fairness. In particular, our method is post-processing and can be applied
to any off-the-shelf estimators.
– Our approach is numerically illustrated on several real data sets and proves
to be very efficient in reducing unfairness while maintaining the advantages
of multi-task learning.
Related work Algorithmic fairness can be categorised into: 1) pre-processing
methods which enforce fairness in the data before applying machine learning
models [2,9,34]; 2) in-processing methods, who achieve fairness in the training
step of the learning model [3,4,18]; 3) post-processing which reduces unfairness
in the model inferences following the learning procedure [12,14,15]. Our work
falls into the latter. This comes with several computational advantages, not least
the fact that even partially pre-trained models can be made fair, which extends
our findings to multi-task transfer learning.
Within standard, single-task classification or regression problems, the DP
constraint has been extensively studied before. In particular, the problem of
integrating algorithmic fairness with the Wasserstein distance based barycenter
has been an active area of research [12, 15, 21, 25] but most studies focus on
learning univariate fair functions. Our work differs from the aforementioned work
by enforcing the DP-fairness in multi-task learning, involving learning a fair
vector-valued function based on a shared representation function. To the best of
our knowledge, there is only a limited body of research concerning fairness in
### Page 3

Fairness in Multi-Task Learning via Wasserstein Barycenters
3
MTL settings. For instance, Zhao et al. [46] introduced a method for fair multi-
task regression problems using rank-based loss functions to ensure DP-fairness,
while [35] and [39] independently achieve fairness for multi-task classification
problems in the Equal Opportunity or Equalised Odds sense. However, our
approach offers a flexible framework for achieving fairness by simultaneously
training fair predictors including binary classification and regression. Oneto et
al. [31,32] suggested a DP-fair multi-task learning approach that learns predictors
using information from different groups. They proposed this for linear [32] and
1-hidden layer networks [31] predictors. Our work extends this approach to
arbitrary multivariate distributions and proposes a post-processing method that
keeps additional computations to a minimum.
Outline of the paper The remainder of this article is structured as follows:
Section 2 introduces MTL, DP-fairness and the objective in rendering multi-task
problems fair. Section 3 introduces our fair multi-task predictor which is then
translated to an empirical plug-in estimator in Section 4. Section 5 evaluates the
estimator on synthetic and real data and we conclude in Section 6.
2
Problem Statement
In machine learning, one often encounters two types of prediction tasks: regression
and binary classification. In regression, the goal is to predict a real-valued output
in R while in binary classification, the goal is to predict one of two classes {0, 1}.
Although the definitions and our approach can be applied to any number of finite
tasks, for ease of presentation we focus this section on these two sub-cases.
2.1
Multi-Task Learning
There are several definitions and goals that can be achieved through MTL. As
our applications are centered on similar tasks, we focus on one aspect referred
to as parameter sharing between the tasks (for a more comprehensive survey,
we recommend Zhang and Yang’s survey [45]). Parameter sharing is especially
useful in the case where there are missing labels in one of the tasks, as MTL
can exploit similarities among the tasks to improve the predictive performance.
Formally, we let (X, S, Y ) be a random tuple with distribution P. Here, X
represents the non-sensitive features, S a sensitive feature, considered discrete,
across which we would like to impose fairness and Y represents the tasks to
be estimated. In theory, there are no restrictions on the space of X, Y , or S.
Throughout the article, to ease the notational load, we assume that X ∈X ⊂
Rd, S = {−1, 1} where −1 represents the minority group and 1 the majority
group and Y = (Y1, Y2) ∈Y1 × Y2 where Y1 ⊂R and Y2 = {0, 1} (or [0, 1] if we
consider score function). That is, we consider problems where the columns of Y
represent regression-binary classification problems. More specifically, we consider
for g∗
1 : X × S →R the general regression problem
Y1 = g∗
1(X, S) + ζ
(1)
### Page 4

4
F. Hu, P. Ratz and A. Charpentier
with ζ ∈R a zero mean noise. g∗
1 is the regression function that minimises
the squared risk RL2(g) := E (Y1 −g(X, S))2. For the second task, recall that a
classification rule c2 : X ×S →{0, 1} is a function evaluated through the misclassi-
fication risk R0−1(c) := P (c(X, S) ̸= Y2). We denote g∗
2(X, S) := P(Y2 = 1|X, S)
the conditional probability (or score) of belonging to class 1. Recall that the
minimisation of the risk R0−1(·) over the set of all classifiers is given by the
Bayes classifier
c∗
2(X, S) = 1 {g∗
2(X, S) ≥1/2} .
(2)
The modelling of the two columns of Y is then referred to as the tasks, denoted
T = {1, 2}. Here we adopt the general notation the two tasks Y1 and Y2 are
modelled on the same input space X × S such that they are independent of each
other conditionally on (X, S). In line with the notion of related tasks, we suppose
that the tasks share a common representation of the features hθ : X × S →Z
where Z ⊂Rr and the marginal task models can be represented by gt(·) = ft◦hθ(·)
for a given task-related function ft : Z →Yt. The representation can then be
approximated via a neural network. We denote H the set of all representation
functions. To appropriately weigh each of the tasks in the estimation problem, we
use trade-off weights λ = (λ1, λ2) where we assume λt > 0 for all t. This yields
the simple multi-task estimator defined as:
θ∗
λ = argmin
θ
E
" 2
X
t=1
λtRt
 Yt, ft ◦hθ(X, S)

#
(3)
with Rt the risk associated to task t. Restricting each task to use the same
representation hθ might seem overly simplistic, but given that under mild con-
ditions the universal approximation theorem [24] is applicable, a large variety
of problems can still be modelled. A thorough discussion of the advantages of
multi-task learning would go beyond the scope of this article and we refer the
interested reader instead to [36,45] for a comprehensive survey. The empirical
estimation of Eq.(3) will be further discussed in Section 4.2.
Notations Assuming that the following density exists, for each s ∈S and for any
task predictor g, we denote νg the probability measure of g(X, S) and νg|s the
probability measure of g(X, S)|S = s. Fg|s : R →[0, 1] and Qg|s : [0, 1] →R are,
respectively, its CDF function defined as Fg|s(u) := P (g(X, S) ≤u|S = s) and
its corresponding quantile function defined as Qg|s(v) := inf{u ∈R : Fg|s(u) ≥v}.
2.2
Demographic Parity
We introduce in this section the fairness under Demographic Parity (DP) con-
straint in both single-task and multi-task problems.
### Page 5

Fairness in Multi-Task Learning via Wasserstein Barycenters
5
S
Xd
X1
...
...
hθ(X, S)
...
g2(X, S)
...
...
g1(X, S)
(X, S)
ft ◦hθ(X, S)
Input layer Hidden layer Output layer
Fig. 1: Representation function sharing in a neural network for multi-task learn-
ing. The goal in DP-fairness is to construct a set of predictors {gfair
t
(X, S)}t
independent from the sensitive feature S. Xi refers to the i-th feature of X.
Fairness in single-task problems For a given task t ∈T = {1, 2}, we denote
by Gt the set of all predictors gt : X × S →Yt of the form gt(·) = ft ◦hθ(·). In
particular for the binary classification, G2 represents the set of all score functions
in Y2 = [0, 1] and additionally we denote Gclass
2
the set of all classifiers in {0, 1}.
With a provided score function g2 ∈G2, a class prediction c2 ∈Gclass
2
is generated
using a threshold τ ∈[0, 1], expressed as c2(·) = 1{g2(·) ≥τ}. Most work
aims to ensure that sensitive information S (such as race) does not influence the
decisions c2, i.e. c2(X, S) ⊥⊥S. This fairness criterion is called weak Demographic
Parity [23,27] and verifies
| P(c2(X, S) = 1 | S = −1) −P(c2(X, S) = 1 | S = 1) | = 0 .
However, enforcing DP fairness for a given threshold does not imply enforcing DP
fairness for other thresholds. Therefore we need to enforce the score function g2
instead, i.e. g2(X, S) ⊥⊥S. This definition, called strong Demographic Parity [4,
25], will be formally defined below in Definition 1.
Remark 1 (Misclassification risk and squared risk). In binary task {0, 1}, given
τ = 1/2 the misclassification risk can be rewritten as
P (Y2 ̸= c∗
2(X, S)) = E
h
(Y2 −c∗
2(X, S))2i
with g∗
2(X, S) = P (Y2 = 1|X, S) = E [Y2|X, S]. Since our goal is to enforce
fairness w.r.t. the sensitive feature S in a score function g2 ∈G2, we are interested
in minimising the risk E (Y2 −g2(X, S))2 instead. Notably, for any given task
t ∈{1, 2}, the (unconstrained) single-task objective becomes:
g∗
t ∈argmin
gt∈Gt
E
h
(Yt −gt(X, S))2i
.
### Page 6

6
F. Hu, P. Ratz and A. Charpentier
We now formally define the (strong) Demographic Parity notion of fairness
and the associated unfairness measure.
Definition 1 (Strong Demographic Parity). Given a task t ∈T (regression
or score function), a predictor gt : X × S →Yt ⊂R is called fair under
Demographic Parity (or DP-fair) if for all s, s′ ∈S
sup
u∈Yt
| P(gt(X, S) ≤u | S = s) −P(gt(X, S) ≤u | S = s′) | = 0 .
Definition 2 (Unfairness). The unfairness of gt ∈Gt is quantified by
U(gt) := max
s,s′∈S sup
u∈Yt
 Fgt|s(u) −Fgt|s′(u)
 .
(4)
Hence, by the above definition, a predictor gt is fair if and only if U(gt) = 0.
We use Gfair
t
:= {g ∈Gt : g is DP-fair} to denote the set of DP-fair predictors
in Yt for a given task t ∈T . In single-task learning for regression and binary
classification, the aim in DP fairness is to minimise the squared risk over Gfair
t
to
find a fair predictor
g∗(fair)
t
∈argmin
gt∈Gfair
t
E
h
(Yt −gt(X, S))2i
.
(5)
Note that the estimator of the optimal regression for this optimisation problem (5)
can be identified as the solution of the Wasserstein barycenter problem [15,22,25].
In binary classification, [20] show that maximising accuracy under DP fairness
constraint is the same as solving a corresponding score function with the threshold
at level τ = 1/2. Here, we extend this notation as suggested in Remark 1.
Fairness in multi-task problems Given trade-off weight λ = (λt)t∈T and
multi-task problem Y = (Yt)t∈T , an optimal multi-task predictor takes a feature
set (X, S) as input and outputs a set of predictions denoted (g∗
t,λ)t∈T . The t-th
marginal prediction is given by g∗
t,λ(·) = ft ◦hθ∗
λ(·). Alternatively, through a
slight abuse of notation, we can express it as g∗
t,λ(·) = ft ◦θ∗
λ(·), where the
representation function yields
θ∗
λ ∈argmin
θ∈H
E
"X
t∈T
λt (Yt −ft ◦θ(X, S))2
#
.
For the sake of simplicity in presentation, we will represent the function hθ as
θ from this point forward. A multi-task predictor is DP-fair if its associated
marginal predictor satisfies DP fairness in Definition 1 for every task t ∈T . We
use Hfair := {θ ∈H : ft ◦θ is DP-fair for each task t ∈T } to denote the subset
of all representations where each task is DP-constrained. The constrained multi-
objective optimisation of Y = (Yt)t∈T is given by the fair optimal representation
function
θ∗(fair)
λ
∈argmin
θ∈Hfair E
"X
t∈T
λt (Yt −ft ◦θ(X, S))2
#
.
(6)
### Page 7

Fairness in Multi-Task Learning via Wasserstein Barycenters
7
Notably, for each task t ∈T , the associated marginal fair optimal predictor is
naturally denoted g∗(fair)
t,λ
(X, S) = ft ◦θ∗(fair)
λ
(X, S). (f1, . . . , f|T |) is predeter-
mined to match the output type of each task in (Y1, . . . , Y|T |). For instance, one
can use linear activation functions for regression problems, and sigmoid functions
for binary classification.
3
Wasserstein fair multi-task predictor
We describe in this section our proposed post-processing approach for constructing
a fair multi-task learning. To derive a characterisation of the optimal fair predictor,
we work under the following assumption.
Assumption 1 (Continuity assumption) For any (s, t, λ) ∈S × T × Λ, we
assume that the measure νg∗
t,λ|s has a density function. This is equivalent to
assuming that the mapping u 7→Fg∗
t,λ|s(u) is continuous.
Driven by our goal to minimise the squared risk defined in Eq.(6) and building
upon previous research in the univariate case [15,22], we introduce the Wasserstein-
2 distance. We then demonstrate that fairness in the multi-task problem can be
framed as the optimal transport problem involving the Wasserstein-2 distance.
The relationship between these concepts is established in Thm. 1.
Definition 3 (Wasserstein-2 distance). Let ν and ν′ be two univariate prob-
ability measures. The Wasserstein-2 distance between ν and ν′ is defined as
W2
2(ν, ν′) =
inf
γ∈Γν,ν′
Z
R×R
|y −y′|2dγ(y, y′)

where Γν,ν′ is the set of distributions on R × R having ν and ν′ as marginals.
The proof of the following theorem is based on results from [15] or [22].
Although their work is not immediately applicable to our case due to the depen-
dence of the tasks, they provide valuable insights on the use of optimal transport
theory in the context of Demographic Parity. We provide a sketch of a proof but
relegate the rigorous version to the Appendix.
Theorem 1 (Optimal fair predictions). Let Assumption 1 be satisfied. Recall
that πs = P(S = s).
1. A representation function θ∗(fair)
λ
satisfies Eq.(6), i.e.,
θ∗(fair)
λ
∈argmin
θ∈Hfair E
"X
t∈T
λt (Yt −ft ◦θ(X, S))2
#
.
if and only if, for each t ∈T this same representation function satisfies
νft◦θ∗(fair)
λ
∈argmin
ν
X
s∈S
πsW2
2(νg∗
t,λ|s, ν) .
### Page 8

8
F. Hu, P. Ratz and A. Charpentier
2. Additionally, the optimal fair predictor g∗(fair)
t,λ
(·) = ft ◦θ∗(fair)
λ
(·) can be
rewritten as
g∗(fair)
t,λ
(x, s) =
X
s′∈S
πs′Qg∗
t,λ|s′ ◦Fg∗
t,λ|s
 g∗
t,λ(x, s)

,
(x, s) ∈X × S .
(7)
Proof (sketch). Recall Eq.(1) and g∗
2(X, S) = E (Y2|X, S), the multi-objective
described in Eq.(6) can be easily rewritten
min
θ∈Hfair E
"X
t∈T
λt (g∗
t (X, S) −ft ◦θ(X, S))2
#
.
Using Prop.1 in [19] together with A.1, there exists a function Vt : X ×S ×Λ →Yt
(or g∗
t,λ(x, s) by abuse of notation) such that the optimisation is equivalent to
min
θ∈Hfair Eλ∼PλE
"X
t∈T
λt
 g∗
t,λ(X, S) −ft ◦θ(X, S)
2
#
.
We assume in this proof that the vector λ is sampled from the distribution Pλ.
Given a task t ∈T we denote ν∗
t ∈argminν
P
s∈S πsW2
2(νg∗
t,λ|s, ν) where there
exists (θ∗
t )t∈T such that ν∗
t = ft ◦θ∗
t . Adapted from the work in [15] and the
universal approximation theorem [24] we deduce,
min
θ∈Hfair Eλ∼PλE
"X
t∈T
λt
 g∗
t,λ(X, S) −ft ◦θ(X, S)
2
#
= Eλ∼Pλ
X
t∈T
s∈S
λtπsW2
2(νg∗
t,λ|s, ν∗
t ) ,
which concludes the sketch of the proof, for details see the Appendix ■
Thm. 1 provides a closed form expression for the optimal fair predictor
g∗(fair)
λ
=

g∗(fair)
t,λ

t∈T for the multi-task Y = (Yt)t∈T . Our method is a post-
processing approach, so we don’t directly retrieve the parameters θ∗(fair)
λ
. A direct
result of Thm. 1 indicates that our post-processing approach preserves the rank
statistics [7,38] conditional on the sensitive feature.
Corollary 1 (Group-wise rank statistics). If g∗
t,λ(x1, s) ≤g∗
t,λ(x2, s) for any
instances (x1, s) and (x2, s) in X × S, then the fair optimal predictor will also
satisfy g∗(fair)
t,λ
(x1, s) ≤g∗(fair)
t,λ
(x2, s).
To obtain the optimal fair classifier for the original two-task problem (Y1, Y2),
we can derive the final optimal fair classifier from the expression in Thm. 1. Given
an instance (x, s) ∈X × S and a threshold τ ∈[0, 1], the optimal fair classifier
becomes
c∗(fair)
2,λ
(x, s) = 1
n
g∗(fair)
2,λ
(x, s) ≥τ
o
.
The finding in [20] is applicable to our case, where setting the threshold at
τ = 1/2 corresponds to optimising accuracy while adhering to the DP constraint.
### Page 9

Fairness in Multi-Task Learning via Wasserstein Barycenters
9
4
Plug-in estimator
To employ the results on real data, we propose a plug-in estimator for the optimal
fair predictor g∗(fair)
λ
.
4.1
Data-driven approach
The estimator is constructed in two steps in a semi-supervised manner since it
depends on two datasets: one labeled denoted Dtrain
n
= {(Xi, Si, Yi,1, Yi,2)}n
i=1
n i.i.d. copies of (X, S, Y1, Y2) and the other unlabeled one, denoted Dpool
N
=
{(Xi, Si)}N
i=1, N i.i.d. copies of (X, S). For the regression-classification problem,
i) We train simultaneously the estimators bg1,λ and bg2,λ of respectively the
regression function g∗
1,λ and the score function g∗
2,λ (optimal unconstrained
functions) on a labeled dataset Dtrain
n
via a multi-task learning model (see Sec-
tion 2). To ensure the continuity assumption, we use a simple randomisation
technique called jittering on the predictors. For each t ∈T , we introduce
¯gt,λ(Xi, Si, ζi,t) = bgt,λ(Xi, Si) + ζi,t
with ζi,t some uniform perturbations in U(−u, u) where u is set by the
user (e.g. u = 0.001). This trick is often used for data visualisation for tie-
breaking [10,15]. The trade-off weight λ can be predetermined or generated
during training (refer to Section 4.2 below).
ii) Empirical frequencies (bπs)s∈S, CDF bF¯gt,λ|s and quantile function bQ¯gt,λ|s are
calibrated via the previously estimators ¯gt and the unlabeled data set Dpool
N
.
The (randomised) Wasserstein fair estimator for each t ∈T is defined by plug-in
bg(fair)
t,λ
(x, s) =
X
s′∈S
bπs′ bQ¯gt,λ|s′ ◦bF¯gt,λ|s (¯gt,λ(x, s, ζt))
(8)
with (ζt)t∈T
i.i.d.
∼U(−u, u). We present the associated pseudo-code in Alg.1.
Remark 2 (Data splitting). The procedure requires unlabeled data. If we do not
have any in practice, we can split the labeled data in two and remove the labels
in one of the two sets. As demonstrated in [16], splitting the data is essential to
avoid overfitting and to get the right level of fairness.
4.2
Empirical Multi-Task
This section outlines how we build each marginal predictor ˆgt,λ using the training
set Dtrain
n
= (xi, si, yi)n
i=1 where each (xi, si, yi) is a realisation of (Xi, Si, Y i) ∼
P. Given a set of task-related loss functions Lt, we define the empirical multi-task
problem from Eq.(3) as
ˆθλ = argmin
θ
n
X
i=1
2
X
t=1
λtLt(yi,t, ft ◦θ(xi, si)).
### Page 10

10
F. Hu, P. Ratz and A. Charpentier
Algorithm 1 Fairness calibration
Input: new data point (x, s), base estimators (ˆgt,λ)t∈T , unlabeled sample Dpool
N
, and
i.i.d uniform perturbations (ζs
k,i)k,i,s.
Step 0. Split Dpool
N
to construct (Si)N
i=1 and {Xs
i }Ns
i=1 ∼PX|S=s given s ∈S;
Step 1. Compute the empirical frequencies (ˆπs)s based on (Si)N
i=1;
Step 2. Compute the empirical CDF bF¯gt,λ|s and quantile b
Q¯gt,λ|s′ from {Xs
i }Ns
i=1;
Step 3. Compute ˆg1,λ, . . . , ˆg|T |,λ thanks to Eq.(8);
Output: fair predictors ˆg1,λ(x, s), . . . , ˆg|T |,λ(x, s) at point (x, s).
As the values for different loss functions Lt are situated on different scales,
issues arise during training when using gradient based methods (see for example
[28,29,40,41] for discussions about the issue). The λ parameter can alleviate this
issue but is difficult to find in practice. Since there is no a priori optimal choice,
we use the "You Only Train Once" (YOTO) approach of [19], initially developed
for regression-regression problems. As the name of their approach suggests, the
model is only trained once for a host of different λ values by conditioning the
parameters of the neural network directly on the task weights λ. The key idea is
that different values for λ are sampled from a distribution and included directly
in the estimation process. Rewritten, Eq.(4.2) then becomes:
ˆθλ = argmin
θ
n
X
i=1
2
X
t=1
λtLt(yi,t, ft ◦θ(xi, si; λ)),
λ ∼Pλ
(9)
where Pλ is a sampling distribution. For our purposes, we use uniform distribution.
As in the original article [19], we employ FiLM conditioning developed by [33]
to condition each layer of θ(·) directly on the sampled λ. Once the model is
fitted, the optimal λ is chosen via a problem specific calibration method on a
calibration set. Precise details on the implementation can be found in Alg. 2.
Algorithm 2 λ-calibrated MTL
Input: Training data Dtrain
n
, bounds bl, bu for U(bl, bu), model, validation grid
while training do
Step 1. Draw nb λt ∼U(bl, bu);
Step 2. FiLM Condition [33] each layer in neural network using λ;
Step 3. Condition loss as in YOTO [19] t with λt;
Step 4. Adjust model parameters given x, s, λ;
end while
for λv in validation grid do
Step 1. Predict ˆyt for all t with x, s, λv;
Step 2. Evaluate ˆyt, yt for all t
end for
Output: Grid of task-wise error metrics given all λv in validation grid, choose
optimal λv
### Page 11

Fairness in Multi-Task Learning via Wasserstein Barycenters
11
5
Numerical evaluation
To evaluate the numerical performance, we conduct experiments on different
datasets3. All data sets used are publicly available and are described in the next
subsection. We also describe each of the separate tasks and the variable on which
we want to achieve demographic parity (the S in the equations above).
5.1
Datasets
We focus on applications with tabular data, the first data set we consider stems
from the folktables package [17], which was constructed to enable bench
marking of machine learning models4. Instead of a single task, we consider the
simultaneous prediction of both Mobility (Binary) and Income (Regression) using
a set of 19 features. Here, we consider gender the binary sensitive variable. In
total, we use 58,650 observations from the state of California.
As a second benchmark, we consider the compas data set [26]. It was con-
structed using a commercial algorithm which is used to assess the likelihood
of reoffending for criminal defendants. It has been shown that its results are
biased in favour of white defendants, and the data set has been used to assess
the efficacy of other fairness related algorithms [30]5. The data set collected has
two classification targets (recidivism and violent recidivism), that are predicted
using 18 features. In total, we use 6,172 observations from the data set and, in
the spirit of the initial investigation, we consider race as the sensitive attribute.
5.2
Methods
For the simulations, we split data into 80/20 train/test set. All estimators are
based on neural networks with a fixed architecture and 10% dropout in the
layers. We compare the performance and fairness of the optimal predictor and
the optimal fair predictor across a MTL model and two single-task (STL) models,
across 20 bootstrap iterations. We refrain from an in-depth architecture and
hyper-parameter search to keep the insights comparable among the simulations.
Our goal is to exemplify two distinct features of MTL under fairness con-
straints. A standard application in MTL is to leverage similarities in tasks to
improve performance in the case where labels in one of the tasks are scarce. As
our method is valid for any trade-off weight λ, we can achieve fairness even
in the case where one task is more important than the other. To simulate this
environment, we successively remove [0,25,50,75,95]% of the regression labels in
the training of the folktables data set and calibrate the λ vector to optimise
performance on the regression task. Intuitively, we would expect the predictive
performance of the models to degrade with a higher proportion of missing data,
3 All sourcecode and data links can be found on github.com/phi-ra/FairMultitask
4 github.com/socialfoundations/folktables
5 Although available publicly, we believe the usage of the data needs to undergo some
ethical considerations. Please read our separate ethical statement regarding this
### Page 12

12
F. Hu, P. Ratz and A. Charpentier
Fig. 2: Left, the performance as measured by MSE for MTL and STL, here the
λ parameter was chosen to optimise the regression task. This leads to better
outcomes, especially in the case of missing values in the regression labels. Right,
regression estimates before versus after the optimal transport.
but MTL should perform better than STL, if it is able to extract knowledge from
the related classification task. A second use for MTL arises when we are interested
in the joint distribution of several tasks. This is of particular importance for the
second case, as one of the tasks in the compas data set is actually a subset of
the other. To illustrate this, we optimise the λ parameter for the compas tasks
in order to maximise performance in both. To measure the performance we use
the mean-squared error (MSE) of the log-predictions for the regression task and
area under the ROC curve (AUC) for the classification tasks. To calculate the
unfairness, we compare the predictions made on the two sub-populations specified
by the presence (Protected) or absence (Unprotected) of the sensitive attribute
using the empirical counterpart ˆU(gt) of the unfairness given in Definition 4
which corresponds to a two-sample Kolmogorov-Smirnov (KS) test
ˆU(gt) := sup
u∈Yt
 ˆFgt|1(u) −ˆFgt|−1(u)
 .
5.3
Results
The numeric results for the folktables data set are summarised in Table 1 and
highlights visualised in Figure 2. Especially the Income variable (the regression
task) suffers from unfairness (as indicated by a higher value in the KS test). The
advantage of using a second task to help the predictions is also clearly visible in
the numerical results and the left pane of Figure 2. Although the performance of
MTL deteriorates with more missing labels, it suffers less than the STL estimation.
The classification task performs less well, as the λ was calibrated to optimise the
regression task. Additionally, as there are no missing labels in the classification
task, we would expect only marginal gains from using MTL even in the case
### Page 13

Fairness in Multi-Task Learning via Wasserstein Barycenters
13
Data
Model
MTL
MTL, Post-processed
STL
Performance
Unfairness
Performance
Unfairness
Performance
Unfairness
regression - all data
0.548 ± 0.02
0.109 ± 0.01
0.558 ± 0.02
0.018 ± 0.00
0.559 ± 0.02
0.107 ± 0.01
regression - 25% missing
0.558 ± 0.02
0.109 ± 0.02
0.572 ± 0.02
0.018 ± 0.00
0.570 ± 0.02
0.105 ± 0.02
regression - 50% missing
0.577 ± 0.02
0.109 ± 0.02
0.593 ± 0.03
0.018 ± 0.01
0.587 ± 0.02
0.099 ± 0.01
regression - 75% missing
0.612 ± 0.05
0.101 ± 0.02
0.627 ± 0.06
0.019 ± 0.01
0.632 ± 0.04
0.098 ± 0.01
regression - 95% missing
0.678 ± 0.05
0.105 ± 0.02
0.687 ± 0.05
0.018 ± 0.01
0.738 ± 0.06
0.108 ± 0.03
classification - all data
0.576 ± 0.01
0.080 ± 0.03
0.577 ± 0.01
0.018 ± 0.01
0.640 ± 0.03
0.042 ± 0.02
Table 1: Performance and unfairness for MTL and Single Task Learning (STL)
models on the folktables data. Each model was also post-processed and
evaluated on performance and unfairness.
where λ is calibrated to serve both tasks well. This is in line with what was found
in the literature of MTL [37]. Here, the specification using the YOTO approach
allows the user to chose the optimal trade-off weight for the problem at hand in
a specific calibration step which will lead to different outcomes using the same
trained weights. The advantage of our result is that it will be valid for any λ. We
can also see across the board that the imposing fairness among the predictions
reduces slightly the predictive performance and almost exactly satisfies the DP
condition. We also visualise the effect of the optimal transport as specified by the
Wasserstein fair estimator in Eq.(8), as suggested in [11]. Because our operations
preserve the group-wise rank (Cor. 1), we can directly represent the changes in
the predictions for each group. The predicted income distribution is shifted in a
way such that the upper tail for the sensitive group is shifted up, but the lower
tail is shifted downwards.
The results from the compas data set mirror in large parts the ones of the
folktables but here we want to optimise the performance across both tasks
at once. Results are summarised in Table 2 and visualised in Figure 3. The
effect of the optimal transport on the distributions can be seen in the marginal
distributions in 3. The colors indicate whether a given individual is identified
as belonging to a protected group. Clearly a bias can be seen in the marginal
distributions, the protected group has both a higher recidivism score and a slightly
higher violent recidivism score, which mirrors the findings from [26]. In the right
pane, we show the post-processed version, where the marginal distributions are
almost congruent, enforcing the DP condition. The resulting fairness is also
assessed numerically using the KS test. As expected this also leads to a small
performance decrease as measured by AUC. The tuning of the λ parameter
allows to have a predictive performance that is almost equivalent to the STL
specification, with the advantage that we can jointly predict the scores and
enforce the DP condition for this joint representation.
6
Conclusion
As multi-task learning grows in popularity, ensuring fairness among the predic-
tions becomes a new challenge as the precise effects of MTL are still poorly
### Page 14

14
F. Hu, P. Ratz and A. Charpentier
Data
Model
MTL
MTL, Post-processed
STL
STL, Post-processed
Performance
Unfairness
Performance
Unfairness
Performance
Unfairness
Performance
Unfairness
task 1 - all data
0.742 ± 0.01
0.289 ± 0.02
0.727 ± 0.01
0.052 ± 0.02
0.745 ± 0.01
0.291 ± 0.02
0.730 ± 0.01
0.055 ± 0.02
task 2 - all data
0.686 ± 0.02
0.289 ± 0.04
0.649 ± 0.01
0.053 ± 0.02
0.671 ± 0.01
0.290 ± 0.03
0.638 ± 0.03
0.053 ± 0.02
Table 2: Performance in AUC and unfairness for MTL and Single Task Learning
(STL) models on the compas data. Each model was also post-processed and
evaluated on performance and unfairness.
Fig. 3: Joint distribution for scores under unconstrained and DP-fair regimes.
Color indicates the presence of the sensitive feature. Note that the joint distribu-
tion appears more mixed and the marginal distributions overlap in the DP fair
case.
understood. In this paper, we investigated the general effects of parameter shar-
ing on the marginal tasks. We proposed a method to integrate fairness into
MTL through a post-processing procedure which keeps a key advantage of MTL,
shorter computational expenses, largely intact. This also opens a host of new
directions for further research. As we focused on tabular data, we were less
restricted by possible model architectures. In other related areas where MTL is
becoming more popular, such as computer vision, pre-trained models akin to our
hθ are often used to ease the computational burden. A thorough investigation
into the precise effects of the combination of the triple Transfer-Multitask-Fair
learning would hence be a natural extension. A further extension of our results
would be to consider fairness in a general multivariate setting. This would mean
shifting the parameters of the embedding hθ simultaneously for all tasks. This
will likely not be possible with a similar closed-form solution, as our approach
relies on the estimation of quantiles. As MTL is generally used in the case where
there is a rather strong (and exploitable) relationship between the two tasks, the
marginal approach we propose here seems apt, but a theoretical discussion would
nevertheless be interesting.
### Page 15

Fairness in Multi-Task Learning via Wasserstein Barycenters
15
Ethics statement
Our work is centered around fairness, which is a goal we sincerely believe all
model should strive to achieve. Nevertheless, to ensure fairness in models, one
needs to define unfairness as its counterpart. This naturally leads to a conundrum
when performing research on this topic. On one hand, we would like our models
to be fair, but to analyse the differences and show an improvement, we first need
to create an unfair outcome. As has been shown in the past, simply ignoring the
sensitive attributes does not solve the problem of bias in the data. Further, as
more flexible methods make their way into practical modelling, this issue is only
bound to increase. Hence it is our conviction that estimating intentionally unfair
models (by for example including sensitive variables explicitly in the training
phase) is ethically justifiable if the goal is to provide a truly fair estimation. In
that sense our work contributes to achieving fairness, and does not create new
risks by itself.
In our empirical application, we consider data which was used in a predictive
algorithm in the criminal justice system. This is particularly concerning as there
have been numerous instances where racial, ethnic or gender bias was detected
in such systems (indeed the data from compas were collected to show precisely
that) and the criminal justice system is supposed to be egalitarian. Further,
existing biases within the justice system may be further reinforced. Although the
above mentioned weaknesses are well documented, such algorithms continue to
be used in practice. Our work does not contribute to these algorithms directly
but rather uses them as an example to show unequal treatment. Whereas the
usage of other, biased data sets, such as the well-known Boston Housing data
set is discouraged, we believe that in order to show the effectiveness of fairness
related algorithms, the use of such a data set is justified.
### Page 16

16
F. Hu, P. Ratz and A. Charpentier
References
1. Association belge des consommateurs test-achats asbl and others v conseil
des ministres., https://curia.europa.eu/juris/liste.jsf?language=en&num=
C-236/09
2. Adebayo, J., Kagal, L.: Iterative orthogonal feature projection for diagnosing bias
in black-box models. In: Conference on Fairness, Accountability, and Transparency
in Machine Learning (2016)
3. Agarwal, A., Beygelzimer, A., Dudík, M., Langford, J., Wallach, H.: A reductions
approach to fair classification. In: Proceedings of the 35th International Conference
on Machine Learning (2018)
4. Agarwal, A., Dudik, M., Wu, Z.S.: Fair regression: Quantitative definitions and
reduction-based algorithms. In: International Conference on Machine Learning
(2019)
5. Barocas, S., Hardt, M., Narayanan, A.: Fairness and Machine Learning. fairml-
book.org (2018)
6. Baxter, J.: A model of inductive bias learning. Journal of artificial intelligence
research 12, 149–198 (2000)
7. Bobkov, S., Ledoux, M.: One-dimensional empirical measures, order statistics and
kantorovich transport distances. Memoirs of the American Mathematical Society
(2016)
8. Calders, T., Kamiran, F., Pechenizkiy, M.: Building classifiers with independency
constraints. In: IEEE international conference on Data mining (2009)
9. Calmon, F., Wei, D., Vinzamuri, B., Ramamurthy, K.N., Varshney, K.R.: Optimized
pre-processing for discrimination prevention. In: Neural Information Processing
Systems (2017)
10. Chambers, J.M.: Graphical methods for data analysis. CRC Press (2018)
11. Charpentier, A.: Insurance, Biases, Discrimination and Fairness. Springer (2023)
12. Chiappa, S., Jiang, R., Stepleton, T., Pacchiano, A., Jiang, H., Aslanides, J.: A
general approach to fairness with optimal transport. In: AAAI (2020)
13. Chzhen, E., Denis, C., Hebiri, M., Oneto, L., Pontil, M.: Leveraging labeled and
unlabeled data for consistent fair binary classification. In: Advances in Neural
Information Processing Systems (2019)
14. Chzhen, E., Denis, C., Hebiri, M., Oneto, L., Pontil, M.: Fair regression via plug-
in estimator and recalibrationwith statistical guarantees. In: Advances in Neural
Information Processing Systems (2020)
15. Chzhen, E., Denis, C., Hebiri, M., Oneto, L., Pontil, M.: Fair regression with
wasserstein barycenters. In: Advances in Neural Information Processing Systems
(2020)
16. Denis, C., Elie, R., Hebiri, M., Hu, F.: Fairness guarantee in multi-class classification.
arXiv preprint arXiv:2109.13642 (2021)
17. Ding, F., Hardt, M., Miller, J., Schmidt, L.: Retiring adult: New datasets for fair
machine learning. Advances in Neural Information Processing Systems 34 (2021)
18. Donini, M., Oneto, L., Ben-David, S., Shawe-Taylor, J.S., Pontil, M.: Empirical
risk minimization under fairness constraints. In: Neural Information Processing
Systems (2018)
19. Dosovitskiy, A., Djolonga, J.: You only train once: Loss-conditional training of deep
networks. In: International conference on learning representations (2020)
20. Gaucher, S., Schreuder, N., Chzhen, E.: Fair learning with wasserstein barycenters
for non-decomposable performance measures. arXiv preprint arXiv:2209.00427
(2022)
### Page 17

Fairness in Multi-Task Learning via Wasserstein Barycenters
17
21. Gordaliza, P., Del Barrio, E., Fabrice, G., Loubes, J.M.: Obtaining fairness using
optimal transport theory. In: International Conference on Machine Learning (2019)
22. Gouic, T., Loubes, J., Rigollet, P.: Projection to fairness in statistical learning.
arXiv preprint arXiv:2005.11720 (2020)
23. Hardt, M., Price, E., Srebro, N.: Equality of opportunity in supervised learning. In:
Neural Information Processing Systems (2016)
24. Hornik, K., Stinchcombe, M., White, H.: Multilayer feedforward networks are
universal approximators. Neural networks 2(5), 359–366 (1989)
25. Jiang, R., Pacchiano, A., Stepleton, T., Jiang, H., Chiappa, S.: Wasserstein fair clas-
sification. In: Adams, R.P., Gogate, V. (eds.) Proceedings of The 35th Uncertainty
in Artificial Intelligence Conference. Proceedings of Machine Learning Research,
vol. 115, pp. 862–872. PMLR (22–25 Jul 2020), https://proceedings.mlr.press/
v115/jiang20a.html
26. Larson, J., Angwin, J., Kirchner, L., Mattu, S.: How we analyzed the com-
pas recidivism algorithm (May 2016), https://www.propublica.org/article/
how-we-analyzed-the-compas-recidivism-algorithm
27. Lipton, Z., McAuley, J., Chouldechova, A.: Does mitigating ml’s impact disparity
require treatment disparity? Advances in neural information processing systems 31
(2018)
28. Liu, B., Liu, X., Jin, X., Stone, P., Liu, Q.: Conflict-averse gradient descent for multi-
task learning. Advances in Neural Information Processing Systems 34, 18878–18890
(2021)
29. Navon, A., Shamsian, A., Achituve, I., Maron, H., Kawaguchi, K., Chechik, G.,
Fetaya, E.: Multi-task learning as a bargaining game. In: Chaudhuri, K., Jegelka,
S., Song, L., Szepesvari, C., Niu, G., Sabato, S. (eds.) Proceedings of the 39th
International Conference on Machine Learning. Proceedings of Machine Learning
Research, vol. 162, pp. 16428–16446. PMLR (17–23 Jul 2022)
30. Oneto, L., Donini, M., Elders, A., Pontil, M.: Taking advantage of multitask learning
for fair classification. In: AAAI/ACM Conference on AI, Ethics, and Society (2019)
31. Oneto, L., Donini, M., Luise, G., Ciliberto, C., Maurer, A., Pontil, M.: Exploiting
mmd and sinkhorn divergences for fair and transferable representation learning.
Advances in Neural Information Processing Systems 33, 15360–15370 (2020)
32. Oneto, L., Donini, M., Pontil, M., Maurer, A.: Learning fair and transferable repre-
sentations with theoretical guarantees. In: 2020 IEEE 7th International Conference
on Data Science and Advanced Analytics (DSAA). pp. 30–39. IEEE (2020)
33. Perez, E., Strub, F., De Vries, H., Dumoulin, V., Courville, A.: Film: Visual
reasoning with a general conditioning layer. In: Proceedings of the AAAI Conference
on Artificial Intelligence. vol. 32 (2018)
34. Plečko, D., Meinshausen, N.: Fair data adaptation with quantile preservation. The
Journal of Machine Learning Research 21(1), 9776–9819 (2020)
35. Roy, A., Ntoutsi, E.: Learning to teach fairness-aware deep multi-task learning. In:
Machine Learning and Knowledge Discovery in Databases: European Conference,
ECML PKDD 2022, Grenoble, France, September 19–23, 2022, Proceedings, Part I.
pp. 710–726. Springer (2023)
36. Ruder, S.: An overview of multi-task learning in deep neural networks. arXiv
preprint arXiv:1706.05098 (2017)
37. Standley, T., Zamir, A., Chen, D., Guibas, L., Malik, J., Savarese, S.: Which tasks
should be learned together in multi-task learning? In: International Conference on
Machine Learning. pp. 9120–9132. PMLR (2020)
38. Van der Vaart, A.W.: Asymptotic statistics, vol. 3. Cambridge university press
(2000)
### Page 18

18
F. Hu, P. Ratz and A. Charpentier
39. Wang, Y., Wang, X., Beutel, A., Prost, F., Chen, J., Chi, E.H.: Understanding and
improving fairness-accuracy trade-offs in multi-task learning. In: Proceedings of
the 27th ACM SIGKDD Conference on Knowledge Discovery & Data Mining. pp.
1748–1757 (2021)
40. Wang, Z., Tsvetkov, Y., Firat, O., Cao, Y.: Gradient vaccine: Investigating and im-
proving multi-task optimization in massively multilingual models. In: International
Conference on Learning Representations
41. Yu, T., Kumar, S., Gupta, A., Levine, S., Hausman, K., Finn, C.: Gradient surgery
for multi-task learning. Advances in Neural Information Processing Systems 33,
5824–5836 (2020)
42. Zafar, M.B., Valera, I., Gomez Rodriguez, M., Gummadi, K.P.: Fairness beyond
disparate treatment & disparate impact: Learning classification without disparate
mistreatment. In: International Conference on World Wide Web (2017)
43. Zafar, M.B., Valera, I., Gomez-Rodriguez, M., Gummadi, K.P.: Fairness constraints:
A flexible approach for fair classification. Journal of Machine Learning Research
20(75), 1–42 (2019)
44. Zemel, R., Wu, Y., Swersky, K., Pitassi, T., Dwork, C.: Learning fair representations.
In: International Conference on Machine Learning (2013)
45. Zhang, Y., Yang, Q.: A survey on multi-task learning. IEEE Transactions on
Knowledge and Data Engineering 34(12), 5586–5609 (2021)
46. Zhao, C., Chen, F.: Rank-based multi-task learning for fair regression. In: 2019
IEEE International Conference on Data Mining (ICDM). pp. 916–925. IEEE (2019)