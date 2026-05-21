# Changan 3D Multi-Object Tracking

**Source**: arxiv PDF, 60 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

SEGMENTATION OF HIGH DIMENSIONAL MEANS OVER
MULTI-DIMENSIONAL CHANGE POINTS AND CONNECTIONS TO
REGRESSION TREES
BY ABHISHEK KAUL1,
1Department of Mathematics and Statistics
Washington State University
Pullman, WA 99164, USA
abhishek.kaul@wsu.edu
This article is motivated by the objective of providing a new analyti-
cally tractable and fully frequentist framework to characterize and implement
regression trees while also allowing a multivariate (potentially high dimen-
sional) response. The connection to regression trees is made by a high di-
mensional model with dynamic mean vectors over multi-dimensional change
axes. Our theoretical analysis is carried out under a single two dimensional
change point setting. An optimal rate of convergence of the proposed esti-
mator is obtained, which in turn allows existence of limiting distributions.
Distributional behavior of change point estimates are split into two distinct
regimes, the limiting distributions under each regime is then characterized,
in turn allowing construction of asymptotically valid conﬁdence intervals for
2d-location of change. All results are obtained under a high dimensional scal-
ing slog2 p = o(TwTh), where p is the response dimension, s is a sparsity
parameter, and Tw,Th are sampling periods along change axes. We charac-
terize full regression trees by deﬁning a multiple multi-dimensional change
point model. Natural extensions of the single 2d-change point estimation
methodology are provided. Two applications, ﬁrst on segmentation of Infra-
red astronomy satellite (IRAS) data and second to segmentation of digital
images are provided. Methodology and theoretical results are supported with
monte-carlo simulations.
1. Introduction.
Consider the following model that describes high dimensional realiza-
tions with dynamic mean vectors observed on a two-dimensional space,
x(w,h) =











θ0
(1) + ε(w,h)
w > τ 0
w, & h > τ 0
h,
θ0
(2) + ε(w,h)
w ≤τ 0
w, & h > τ 0
h,
θ0
(3) + ε(w,h)
w ≤τ 0
w, & h ≤τ 0
h,
θ0
(4) + ε(w,h)
w > τ 0
w, & h ≤τ 0
h.
=
4
X
j=1
θ0
(j)1

(w,h) ∈Qj(τ 0)

+ ε(w,h),
(1.1)
w = 1,...,Tw, h = 1,...,Th,
Th
Tw
Width (w)
Height (h)
(τ0w,τ0
h)
Q1(τ0)
Q2(τ0)
Q3(τ0)
Q4(τ0)
where Qj(τ 0) represents the collection of indices in the jth quadrant with the origin shifted to
τ 0 = (τ 0
w,τ 0
h) ∈{1,...,Tw} × {1,...,Th}i. The notation 1[·] represents an indicator function.
Keywords and phrases: Multi-dimensional change points, Regression trees, High dimensions, Rate of conver-
gence, Limiting distributions, Image processing.
iThe ordering of quadrants is per usual convention, i.e., Q1(τ0) = {(w,h); w > τ0w, & h > τ0
h}, Q2(τ0) =
{(w,h); w ≤τ0w, & h > τ0
h}, Q3(τ0) = {(w,h); w ≤τ0w, & h ≤τ0
h}, and Q4(τ0) = {(w,h); w >
τ0w, & h ≤τ0
h}.
1
arXiv:2105.10017v1  [stat.ME]  20 May 2021
### Page 2

2
(w,h)
w ≤τ0w
w > τ0w
h ≤τ0
h
h > τ0
h
h ≤τ0
h
h > τ0
h
θ0
3
θ0
2
θ0
4
θ0
1
Ex(w,h) ∈Rp
FIG 1. 2d change point model with HD means (1.1) expressed equivalently as a decision tree
Here the observed variable is x(w,h) ∈Rp, 1 ≤w ≤Tw, 1 ≤h ≤Th. The variables ε(w,h) ∈
Rp are unobserved zero mean random variables. The unknown parameters of interest are
the change point τ 0 = (τ 0
w,τ 0
h)T and the mean vectors θ0
(j) ∈Rp, j = 1,...,4, with p being
potentially high dimensional, i.e., where p may diverge exponentially with respect to the
number of realizations TwTh, under a sparsity assumption to be speciﬁed later.
A main motivation to study model (1.1), associated estimators and its generalizations, is
that it provides a parametric framework for a frequentist analysis of regression trees. Figure
1 provides a visualization of the model (1.1) expressed as a decision tree and illustrates this
connection. The equivalence of a full regression tree to generalizations of the model (1.1)
shall be illustrated later in Section 3. The usefulness of regression trees is comprehensively
established in the machine learning literature where it forms arguably one of the most em-
pirically successful and heavily utilized tool, see, e.g. the recent review article [22]. On the
other hand, these models also form one of the least analytically understood learning meth-
ods, wherein, to our knowledge there does not exist a frequentist parametric framework that
allows analysis of statistical properties algorithms proposed for their recovery. The only ana-
lytically tractable methodology available in the literature is for Bayesian variants (BART) of
[11], which has also only recently been recently studied in [32]. Furthermore, existing con-
structions of regression trees are typically limited to a single dimensional response (p = 1),
the model (1.1) on the other hand allows for potential high dimensionality which is of sig-
niﬁcant interest given the nature of the current data rich landscape. We mention here that our
objectives in this article shall be to make ﬁrst analytical inroads to this problem, we do not
attempt to address the rich body of additional problems that shall arise when viewed in its full
generality, in this case we shall only attempt to provide feasible extensions that have clear
analytical paths forward.
A second standalone motivation to study the model (1.1) arises from the ﬁeld of machine
vision, in particular that of image recovery and segmentation. The underlying objective in
this context is of segmenting a digital image into distinct clusters of pixels, each of which
can be described as a vector of primary colors channels (or features) (r,b,g)T , with addi-
tional channels describing ﬁner features of each pixel such as that of texture (or gradient in
each direction) along with interactions of primary and secondary colors. Several other ma-
chine tasks are often built upon this segmentation layer, such as that of image denoising,
object identiﬁcation and classiﬁcation amongst several others. While there are more than one
heuristic techniques available in the computer science literature whose implementations are
often based on computational relaxations which are not guaranteed. Analytically tractable
statistical approaches to these problems are very limited. One such technique for speciﬁc the
purposes of image denoising is that of total variation denoising which has been studied in the
recent article of [29].
### Page 3

HD MEANS OVER 2D CHANGES
3
Change point models have an extensive literature since their inception in [30], with con-
siderable effort in the recent past being devoted to allowing potential high dimensionality
in these models. However, to our knowledge, all of this literature has been in the context of
change on a one dimensional segmenting axis (usually time). To our knowledge, the model
(1.1) has not been described in the literature, consequently, analytically studied estimators for
its parameters are unavailable in either the traditional ﬁxed p framework, diverging p (with
p/T →0) under dense alternatives framework, or high dimensional p (with log p = o(T)) un-
der sparse alternatives framework. Furthermore, even under a one-dimensional segmenting
axis and in the presence of potential high dimensionality, a large proportion of the existing
literature is oriented towards obtaining near-optimal rates of estimation of suitably developed
estimators. The question of inference under this high dimensional framework is far less un-
derstood in the literature in part owing to the until recently unavailable estimates with an
optimal rate of convergence.
Following is a brief review of the recent literature on change point models under a one-
dimensional segmenting axis. Estimation properties at rates slower than optimal by at least
logarithmic factors are by far the most extensively studied facet of the above discussed prob-
lems. For e.g. under a ﬁxed p setting, the results of [21] consider a least squares estimator
together with a total variation regularization. In a sparse high dimensional multiple change
framework the article of [43] provides a projected cusum estimator with a rate of convergence
slower than optimal by a factor of log log T. The article of [12] yields a similar near optimal
rate of estimation of the location parameters. While near optimal rates of the approximation
are informative from an estimation perspective, however from an inference perspective one
requires a change point estimator to obey an optimal rate of convergence in order to allow
the existence of limiting distributions and in turn allow inference on change point location.
In a large p setting this fundamental aspect of post-estimation inference on the change loca-
tion is in fairly nascent stages in the literature, and are only available under single change
points. In a diverging p, p << T ii (under dense alternatives) framework, the articles [8] and
[9] develop limiting distributions for the estimator of the location of the change point, which
in turn allows inference on the unknown location. Under stronger dimensional assumptions,
the article [4] provides a similar limiting distribution result. The article of [41] extends these
inferential results to p << T 2/log T, but require p to be necessarily diverging. Under high
dimensionality, the article of [25] provide an plug-in estimator that yields this optimal rate
of convergence and develops limiting distributions in this framework. The boundary prob-
lem of detection of existence of dynamicity in a diverging or high dimensional setting has
been studied by several authors and different methods have been proposed. This problem has
been addressed by several approaches, for e.g. [23], [42], [17], [13] and [34] amongst others.
This boundary problem has also been approached in a selection sense by means of appro-
priately tuned ℓ0 regularization, see e.g. [26] in a single change point framework, [27], [38]
in a multiple change point framework. This ℓ0 regularization is also in a sense equivalent to
that carried out in the regularization step of Wild Binary Segmentation Algorithm of [19],
which is also utilized in [43] and several other multiple change point methodologies in the
literature. High dimensional change point models have also been studied with several other
data generating processes besides mean shifts, graphical models in [28], [39], [1], stochastic
block models in [40], [8], markov random ﬁelds [33] amongst other settings, all available
article by construction assuming a one-dimensional change axis.
The main analytical contributions of this article shall be to develop algorithmic estimators
for the change point parameter τ 0 under the model (1.1), so that it retains sufﬁcient regularity
iip << T represents p/T →0.
### Page 4

4
despite potential high dimensionality in order to yield an optimal rateiii of estimation. This in
turn shall allow existence of limiting distributions under both vanishing and non-vanishing
jump size regimes whose forms are then derived under high dimensional asymptotics. These
results enable one to perform inference on the change point, or equivalently on the branch-
ing transitions in context of regression trees, by allowing construction of asymptotically valid
conﬁdence intervals under the assumed high dimensional and sparse framework. Further con-
siderations in this development shall be the following, (a) sufﬁcient ﬂexibility in the method-
ology to be directly extendable to multiple change points and regression trees in their full
generality, and (b) scalability of the methodology in both dimension size of the mean param-
eters as well as sampling periods Tw,Th in order to allow applicability towards applications
such as analysis of large images (ﬁxed p, large T) as well as data sets such as those arising
in regression tree contexts such as genetic sequencing studies (large p, small T).
To describe our proposed methodology ﬁrst consider the squared loss,
L(τw,τh,θ) =
1
TwTh
4
X
j=1
X
(w,h)∈Qj(τ)
∥x(w,h) −θ(j)∥2
2,
where τ = (τw,τh)T ,
(1.2)
and deﬁne a component-wise plug-in estimator for τ 0 = (τ 0
w,τ 0
h)T as follows,
˜τw(ˆτh, ˆθ) = arg min
1≤τw<Tw
L(τw, ˆτh, ˆθ),
and
˜τh(ˆτw, ˆθ) = arg min
1≤τh<Th
L(ˆτw,τh, ˆθ),
(1.3)
where ˆτ = (ˆτw, ˆτh) and ˆθ represent some preliminary estimates that are for the time being
assumed to be available. It is evident that the behavior of the estimator ˜τ = (˜τw, ˜τh)T shall be
intertwined with the quality of plug in estimates ˆτ = (ˆτw, ˆτh) and ˆθ utilized in its construction.
To build a feasible and sufﬁciently regular estimator for τ 0, our strategy going forward
shall be somewhat reverse of traditional. Where one usually builds an algorithm and then
attempts to study its properties, instead we shall begin by obtaining statistical properties of
the plug-in estimates ˜τw, ˜τh of (1.3) with respect to assumed properties in estimation of the
preliminary estimates ˆτ and ˆθ used in its construction. These results shall then be aggregated
in order to provide an asymptotically valid and feasible in practice, twice iterative algorith-
mic procedure, where the iterations are between the change point parameters and the mean
parameters with an additional internal iteration in the components of the change point.
To study ˜τ = (˜τw, ˜τh)T we require some more deﬁnitions and additional control parame-
ters. Deﬁne the jump vectors that constitute the change across quadrants of model (1.1),
η0
(1) = θ0
(2) −θ0
(1), η0
(2) = θ0
(3) −θ0
(2), η0
(3) = θ0
(3) −θ0
(4), and η0
(4) = θ0
(1) −θ0
(4).
(1.4)
The direction of η0
(j)’s is inconsequential for the analysis of ˜τ, i.e., one may instead deﬁne
η0
(1) = θ0
(1) −θ0
(2), and similar for η0
(j), j = 2,3,4. The parameters that provide control are
instead the ℓ2 magnitude of these vectors which represent jump sizes across quadrants, i.e.,
ξj = ∥η0
(j)∥2,
j = 1,...,4,
ξ = max
j {ξj},
ξ = min
j {ξj}.
(1.5)
Additionally deﬁne weight parameters that measure the proportion of observations in each
quadrant, as well as those that measure proportions along individual change axes,
ωj = |Qj(τ 0)|

TwTh,
j = 1,2,3,4,
and
ω = minj{ωj}
ωw = (Tw −τ 0
w)

Tw,
and
ωh = (Th −τ 0
h)

Th.
(1.6)
iiiOur use of the word optimal is a slight over-reach. This is made as a natural extension in view of the minimax
optimal rate of estimation in a single change axis framework, which is known in the literature. However, under
the considered setting, the optimal rate is not explicitly known. Based solely on the results of this article, the best
we can claim is instead that we obtain a sharp rate of convergence.
### Page 5

HD MEANS OVER 2D CHANGES
5
Th
Tw
(0,0)
Th
Tw
Width (w)
Height (h)
(τ0w,τ0
h)
TwThω1
TwThω2
TwThω3
TwThω4
Thωh
Twωw
θ0
(1)
θ0
(2)
θ0
(3)
θ0
(4)
η0
(4), ξ4
η0
(2), ξ2
η0
(1), ξ1
η0
(3), ξ3
ξw
ξh
Th
Tw
(0,0)
Th
Tw
Width (w)
Height (h)
FIG 2. Illustration of control parameters. Left panel: weight parameters ωj, j = 1,2,3,4 and ωw and ωh,
measuring proportion of available observations in each segment Right panel: underlying mean parameters θ0
(j),
and change parameters η0
(j), j = 1,2,3,4, as well as the jump sizes ξj, j = 1,2,3,4, and ξw, and ξh.
Next deﬁne width and height-wise proportion weighted jump sizes which shall play a critical
role in our analysis,
ξ2
w = ωhξ2
1 + (1 −ωh)ξ2
3,
ξ2
h = ωwξ2
4 + (1 −ωw)ξ2
2.
and
ξmin = ξw ∧ξh.
(1.7)
We remind the reader here that the above mean, change and weight parameters are allowed
to depend on Tw,Th, either directly or via the dimension p. However, this dependence is
notationally suppressed throughout for clarity of exposition. A visual description of these
control parameters is also provided in Figure 2.
Our ﬁrst task shall be to examine the properties of ˜τ and its relationship to assumed prop-
erties of preliminary estimates ˆτ, ˆθ used in its construction. In accordance to the structure
of this approach, ﬁrst assume the availability of ˆτ = (ˆτw, ˆτh) and ˆθ satisfying mainly the
following requirements,
max
1≤j≤4∥ˆθ(j) −θ0
(j)∥2 ≤cu1ξmin,
|ˆτw −τ 0
w| ≤cu1Tw, and |ˆτh −τ 0
h| ≤cu1Th
(1.8)
with probability at least 1 −o(1), where cu1 > 0 is a suitably chosen small enough constant.
Then our ﬁrst estimation result shall show that ˜τ implemented with estimates satisfying (1.8)
yields a near optimal rates of convergence,
(˜τw −τ 0
w) = Op
 T −1
h ξ−2
w slog2(p ∨TwTh)

and
(˜τh −τ 0
h) = Op
 T −1
w ξ−2
h slog2(p ∨TwTh)

.
(1.9)
Here s is a sparsity parameter that can equivalently be thought of as either sparsity of the
jump vectors η0
(j), j = 1,2,3,4, or that of individual mean vectors θ0
(j), j = 1,2,3,4 (see,
discussion after (2.1) for further details on this equivalence).
While near optimal rates of (1.9) are of independent interest from an estimation perspec-
tive and are comparable to a large proportion of literature in a high dimensional framework
under a single change axis. However, due to the absence of an optimal rate of convergence, it
does not permit existence of limiting distributions and consequently disallows one to perform
inference on the underlying change parameters. The next and more important estimation re-
sult shall show that when quality of preliminary estimates is improved, the corresponding
plug in estimate of the change point can be upgraded from near optimality to optimality.
### Page 6

6
Speciﬁcally, upon assuming the availability of preliminary estimates tightened to,
max
1≤j≤4∥ˆθ(j) −θ0
(j)∥2 ≤ξminrT ,
where
rT =
cu1
s1/2 log(p ∨TwTh)
iv
and,
|ˆτw −τ 0
w| ≤Twr2
T ,
and
|ˆτh −τ 0
h| ≤Thr2
T
(1.10)
with probability at least 1 −o(1). Then we shall obtain the optimal estimation result,
(˜τw −τ 0
w) = Op(T −1
h ξ−2
w )
and
(˜τh −τ 0
h) = Op(T −1
w ξ−2
h ).
(1.11)
The order of each of the two relations in (1.9) and (1.11) are with respect to (w.r.t.) Tw and
Th, respectively. We mention this subtlety to inform that these results in both the near optimal
and optimal case are valid under the asymptotics Tw →∞, Th →∞, additionally the ﬁrst
relation is also valid when Tw →∞, Th < ∞, and symmetrically for the second relation.
The result (1.11) has important consequences. It characterizes the parameters (Thξ2
w and
Twξ2
h) that control the statistical behavior of ˜τ. In context of regression trees, it provides the
order of magnitude of change in means that is sufﬁcient to be detectable by the proposed
approach. It also highlights two important distinctions of model (1.1) in comparison to mean
shift models under a single change axis. First, in a single change axis framework, the single
jump size across a change point is the estimation controlling parameter. On the other hand, in
model (1.1) there are instead four individual jump sizes ξj j = 1,2,3,4 characterizing each
change point, and the estimation controlling parameters are instead weighted combinations
of these individual jumps. Second, note that in each direction (say ˜τw) one is able leverage the
observations in the alternate direction to yield a rate of convergence Op(T −1
h ξ−2
w ). In com-
parison, a model with a one-dimensional change axis yields an optimal rate of Op(ξ−2), (see,
e.g. [25]). As a direct consequence, this leveraging of observations of alternating directions
allows detect jumps which may be smaller by an order of √Th. Further discussions on this
and other aspects of this comparison are provided in Section 2.
The most important consequence of the optimal rate (1.11) along with other peripheral
results is that allows for the existence of limiting distributions of the estimates ˜τw, ˜τh, thereby
enabling inference on the corresponding parameters, despite potential high dimensionality.
As for single change axis settings (see, e.g., [25],and [7]), the distributional behavior of ˜τ is
split into two distinct regimes which are that of the vanishing and non-vanishing jump sizes.
Under the former regime of √Thξw →0, √Twξh →0, we shall obtain,
Thξ2
wσ−2
(w,∞)(˜τw −τ 0
w) ⇒arg max
ζ∈R
 2Ww(ζ) −|ζ|

,
Tw →∞
Twξ2
hσ−2
(h,∞)(˜τh −τ 0
h) ⇒arg max
ζ∈R
 2Wh(ζ) −|ζ|

,
Th →∞
(1.12)
where σ2
(w,∞) and σ2
(h,∞) are estimable variance parameters of these limiting processes.
Here Ww(·) and Wh(·) are both two-sided Brownian motions on R. The distribution
arg maxζ∈R
 2W(ζ) −|ζ|

is well studied in the literature and its cdf and thus its quantiles
are readily available, ([44]).
For the non-vanishing case √Thξw →ξ(w,∞), and √Twξh →ξ(h,∞), where 0 < ξ(w,∞), ξ(h,∞) <
∞, deﬁne a negative drift two sided random walk initializing at the origin.
C∞(ζ,ξ,σ2) =





Pζ
t=1 zt,
ζ ∈N+ = {1,2,3,...}
0,
ζ = 0
P−ζ
t=1 z∗
t ,
ζ ∈N−= {−1,−2,−3,...},
(1.13)
ivThis is a sequence in both Tw and Th, however to ease notation we present it in shorthand as rT
### Page 7

HD MEANS OVER 2D CHANGES
7
where zt,z∗
t are independent copies of a P
 −ξ2,4ξ2σ2
distribution, which are also in-
dependent over all t, for a distribution law Pv that shall be determined by the form of the
underlying distribution in model (1.1) (see, Condition A′). The notation in the arguments of
P(·,·) is representative of the mean and variance of this distribution. Finally, let,
C(w,∞)(ζ) = C∞
 ζ,ξ(w,∞),σ2
(w,∞)

and C(h,∞)(ζ) = C∞
 ζ,ξ(h,∞),σ2
(h,∞)

,
(1.14)
where σ2
(w,∞) and σ2
(h,∞) are variance parameters as deﬁned earlier in context of the vanish-
ing regime. Then, we shall obtain the following results,
(˜τw −τ 0
w) ⇒arg max
ζ∈Z
C(w,∞)(ζ),
Tw →∞
(˜τh −τ 0
h) ⇒arg max
ζ∈Z
C(h,∞)(ζ),
Th →∞,
(1.15)
where Z is the collection of integers. Quantiles of these limiting distribution can be ap-
proximated numerically upon availability of law P of increments of the processes in (1.14),
thereby enabling the construction of asymptotically valid conﬁdence intervals.
The above discussion shall establish the statistical behavior of the plug-in estimator ˜τ,
and provides sufﬁcient properties required of the preliminary estimates used in its con-
struction. However, two important questions remain as yet unanswered. First, since these
theoretical results are established under assumed conditions on the preliminary estimates
ˆτ and ˆθ, thus without this availability, these results remain infeasible to implement. Sec-
ond, all presented results require no explicit restrictions on growth of dimensionality or
the behavior of jump sizes which may appear highly suspect. Both these questions are
inter-related and the following additional notation is necessary for their discussion. For any
τ = (τw,τh)T ∈{1,...,(Tw −1)} × {1,...,(Th −1)}, let,
¯x(j)(τ) =
1
|Qj(τ)|
X
(w,h)∈Qj(τ)
x(w,h),
j = 1,2,3,4.
(1.16)
be the quadrant-wise sample means. Now consider the soft-thresholding operator, kλ(x) =
sign(x)(|x|−λ)+, λ > 0, x ∈Rp, where sign(·), |·|, and (·)+vi are applied component-wise.
Then for any λ1,λ2 > 0, deﬁne ℓ1 regularized quadrant-wise mean estimates,
ˆθ(j)(τ) = kλj
 x(j)(τ)

,
j = 1,2,3,4.
(1.17)
It is well known in the literature ([14], [15]) that the soft-thresholding operation in (1.17) is
equivalent to the following ℓ1 regularization.
ˆθ(j)(τ) = arg min
θ∈Rp
¯x(j)(τ) −θ
2
2 + λj∥θ∥1,
λj > 0,
j = 1,2,3,4.
(1.18)
In view of earlier discussion, the missing links required for feasibility of ˜τ are, (a) con-
struction of preliminary mean estimates ˆθ, and (b) both preliminary estimates ˆτ and ˆθ requir-
ing either the condition (1.8) (milder) to obtain near optimal estimates, or (1.10) (stronger)
to obtain an optimal estimate of τ 0. We shall fulﬁl (a) by utilizing the soft thresholded means
(1.17). In order to fulﬁl (b), we shall exploit the distinctions between the rate conditions (1.8)
and (1.10), by building an twice iterated algorithmic estimator that shall improves a nearly
arbitrarily chosen ˇτ, ﬁrst to a near optimal estimate ˆτ in a ﬁrst iteration, and then to an op-
timal estimate ˜τ in a second iteration. This construction is described as Algorithm 1 below
and is presented visually as Figure 3 in Sub-section 2.2.
vIf one assumes ε(w,h) ∼i.i.d N(0,Σ), then P shall also be a normal distribution.
viFor x ∈R, (x)+ = x, if x ≥0, and x = 0 if x < 0.
### Page 8

8
Algorithm 1 Optimal estimation of τ 0 = (τ 0
w,τ 0
h)T .
Initialize change point ˇτ = (ˇτw, ˇτh),
1: Compute mean estimates ˇθ(j) = ˆθ(j)(ˇτ), j = 1,2,3,4. and update change point estimate componentwise,
ˆτw = arg min
1≤τw<Tw
L(τw, ˇτh, ˇθ)
and
ˆτh = arg min
1≤τh<Th
L(ˇτw,τh, ˇθ)
2: Update mean estimates to ˆθ(j) = ˆθ(j)(ˆτ), j = 1,2,3,4, and update,
˜τw = arg min
1≤τw<Tw
L(τw, ˆτh, ˆθ)
and
˜τh = arg min
1≤τh<Th
L(ˆτw,τh, ˆθ)
Output: ˜τ = (˜τw, ˜τh).
For the validity of Algorithm 1 we shall assume the rate assumption,
cuσ
ξmin
nslog2(p ∨TwTh)
√(TwThω)
o
≤cu1.
(1.19)
Then we shall show that performing the two successive iterations between the change point
and mean parameters of Algorithm 1, shall in each iteration also provide estimates that sat-
isfy (1.8) and (1.10), respectively, which then feed into the following iteration. This process
is designed so as to be able to aggregate the prior developed statistical results which in turn
shall guarantee the analytical validity of the proposed algorithm. In particular, the output ˜τ
of Algorithm 1 shall be shown to satisfy the optimal rate estimation (1.11), and the limiting
distribution results of (1.12) and (1.15), these shall follow as a corollary, by the construction
of the iterative mechanism. Further details of this argument are postponed to Sub-section 2.2.
We note that the speciﬁc choice of soft-thresholding as a regularization mechanism in (1.18)
is superﬁcial, the eventual objective is only to obtain mean estimates that are well behaved
in the high dimensional setting in the ℓ2 norm. Alternatively, our results are derived in sufﬁ-
cient generality to allow one to consider using any other suitable choice of the regularization
mechanism that may also be problem speciﬁc, e.g. group ℓ1 regularization which assumes a
partially known sparsity structure, or non-convex regularizations such as scad and mcp.
While the above results and Algorithm 1 have been developed independently and purely
from a change point perspective, however, fortuitously there are overlapping and interesting
conceptual elements to that of regression trees with four assumed partitions. In regression
trees, the traditional frequentist algorithm, see, Page 308 of [18] proceeds via a greedy it-
erative process with branching transitions estimated in alternating directions via half planar
splits. It may be observed that Algorithm 1 is infact doing something very similar but with
two key reﬁnements. First, it performs quadrant-wise splits instead of half planar splits. Sec-
ond, while Algorithm 1 can also be viewed as being greedy, however, we additionally show
that optimality is achieved in two successive iterations and thus further iterations shall be
statistically redundant, i.e., further iterations will only serve to yield data speciﬁc improve-
ments. Further discussions and generalizations of the model (1.1) allowing multiple hierar-
chical change points that provide an alternative characterization of full and fully-frequentist
regression tress are provided in Section 3.
The remainder of this article is organized as follows. Section 2 provides a rigorous de-
scription of the estimation and inference results discussed above as well as the analytical
behavior of the proposed Algorithm 1. Section 3 shall then provide extensions of model (1.1)
and corresponding methodology to multiple hierarchical changes/full regression trees. Sec-
tion 4 illustrates the proposed methodologies on two distinct real data application, ﬁrst on
performing a segmentation of the Infrared astronomy satellite data and second on digital im-
age segmentation and denoising. Section 5 provides numerical support to our methodology
### Page 9

HD MEANS OVER 2D CHANGES
9
and results via monte-carlo simulations. We conclude this section with a short note on the
notation used throughout the article.
Notation: R represents the real line. For any vector δ ∈Rp, ∥δ∥1, ∥δ∥2, ∥δ∥∞repre-
sent the usual 1-norm, Euclidean norm, and sup-norm respectively. For any set of indices
U ⊆{1,2,...,p}, let δU = (δj)j∈U represent the subvector of δ containing the components
corresponding to the indices in U. Let |U| and Uc represent the cardinality and complement
of U. We denote by a ∧b = min{a,b}, and a ∨b = max{a,b}, for any a,b ∈R. We use a
generic notation cu > 0 to represent universal constants that do not depend on Tw,Th or any
other model parameter. All limits are with respect to the sampling periods Tw, and Th simul-
taneously or individually. The mean and the change parameters are assumed as sequences in
these sampling periods Tw, and Th, however this is notationally suppressed in all to follow.
The notation ⇒represents convergence in distribution.
2. Theoretical Analysis.
This section is divided into two sub-sections. Sub-section 2.1 provides sufﬁcient condi-
tions and main theoretical results regarding the plugin least squares estimator ˜τ of (1.3).
Speciﬁcally, near optimal and optimal rates of convergence of the estimators ˜τw and ˜τh, to-
gether with their limiting distributions in the two regimes described earlier. Sub-section 2.2
aggregates these results recursively to establish the validity of the proposed Algorithm 1.
2.1. Rate of convergence and limiting distributions of ˜τ(ˆτ, ˆθ).
Condition A (on underlying distributions): The vectors ε(w,h) = (ε(w,h,1),...,ε(w,h,p))T ,
w = 1,..,Tw, h = 1,...,Th are independent and identically distributed (i.i.d.) subexponential
random vectors with variance proxy σ2 < ∞(see, Deﬁnition C.1 and C.2)
The class of subexponential distribution is well known in the literature. The distributions
included in this class are the Gaussian, Laplace, mean centered Exponential, mean centered
Chi-square, centered mixtures of these distributions amongst several other well known distri-
butions. We also note that Condition A does not exclude discrete distributions, such as mean
centered Bernoulli, mean centered Poisson, or any centered and bounded distribution. The
monograph [37] provides a detailed study of this large class of distributions. As is appar-
ent, this assumption is signiﬁcantly weaker than assuming a Gaussian distribution which has
commonly been assumed in the change point literature.
Condition B (on model parameters): (i) Covariance Σ := Eε(w,h)εT
(w,h) has bounded
eigenvalues, i.e., 0 < κ2 ≤mineigen(Σ) < maxeigen(Σ) ≤φ2 < ∞, with constants κ2, φ2.
(ii) Assume a change point exists and is separated from the parametric boundary on both
axes, i.e., for some positive sequence ω →0, we have minj{|Qj(τ 0)|} ≥TwThω →∞,
(iii) Let ξ and ξj, j = 1,...,4 be as deﬁned in (1.5) and let ξw,ξh,ξmin be as deﬁned in (1.7).
Then we assume that ξ ≤cuξmin, for some constant cu > 0.
Condition B(i) assumes a positive deﬁnite spatial dependence structure over components
1,...,p. We require the assumption of bounded eigenvalues only from an inference (limiting
distributions) perspective. If the objective is only that of estimation, then these assumptions
can be relaxed. In this case, κ2 may be allowed to converge to zero (or identically zero), i.e.,
potentially rank deﬁcient. The upper bound φ2 may be allowed to diverge with Tw,Th. The
bounds for the localization error of ˜τ and thereby its rate of convergence provided later in
this section are obtained upto universal constants. Consequently the effect of this relaxation
will be directly observable in these bounds.
Condition B(ii) and B(iii) are both separation conditions that ensure the jump signal is not
dominated by noise in order for the estimator to catch this signal. B(ii) ensures that there
### Page 10

10
are a diverging number of observations in each induced quadrant of the model (1.1). An
analogous condition is also typical in a regression tree framework, see, e.g., Deﬁnition 3.1 of
[32]. Condition B(iii) is slightly more technical, although it is still serving a similar purpose
as B(i). This condition can be interpreted as the jump metrics in the horizontal and vertical
direction (ξw,ξh) are not dominated by either individual half planes, for e.g. if one of ξ2 or
ξ4 dominates ξw in its rate of divergence, the method may be unable to detect the change in
the horizontal direction, and symmetrically for the vertical direction.
Next consider the following sets of non-zero indices corresponding to the p-dimensional
mean vectors θ0
(j), j = 1,2,3,4,
Sj =

k ∈{1,2,...,p}; θ0
(j,k) ̸= 0
	
,
j = 1,2,3,4,
(2.1)
and let Sc
j j = 1,2,3,4, be the complement sets. Deﬁne the maximum cardinality max1≤j≤4 |Sj| =
s ≥1. The parameter s measures sparsity in the model (1.1). This sparsity assumption is typ-
ically made on the jump vector, as done in [43] and [17] under a single change axis frame-
work. In contrast we make this assumption directly on the mean vectors θ0
(j)s. This version
of sparsity holds with no loss of generality with respect to the former version. We refer to
Appendix C of [25] for a discussion on this aspect. To allow the viability of this assump-
tion one may center the observed data with component-wise empirical means, i.e., consider
x(w,h) of model (1.1) where instead of the means θ0
(j), the jump η0
(j) are s-sparse, i.e., there
are mean changes in at most s components. Upon centering x(w,h) with empirical means,
x∗
(w,h) = x(w,h) −¯x, with ¯x = P
w,h x(w,h)

(TwTh), the s-sparsity of η0
(j) is transferred onto
the new mean vectors θ∗= Ex∗
(w,h), as 4s-sparsity. Heuristically, this centering operation
is same as that carried out in linear regression models to get rid of the intercept parameter,
which is implicitly assumed in the high dimensional linear regression literature and is known
not to impact rates of estimation.
In keeping with the discussion of Section 1, for our results on the plug-in estimator ˜τ
we are agnostic about the speciﬁc choice of the estimators used to obtain the preliminary
estimates and instead rely on combinations of the following condition that describes these
assumed preliminary estimate properties.
Condition C (on preliminary estimates): Let cu1 > 0 be a suitably chosen small enough
constant and let πT →0 be a positive sequence. Then we assume either of the combinations
of

(i)(a), (ii)(a,b)

or

(i)(b), (ii)(a,c)

below hold with probability at least 1 −πT .
(i) (on preliminary location estimates ˆτ):
(a) Assume that ˆτw, and ˆτh satisfy the absolute error bound of (1.8)
(b) Assume that ˆτw, and ˆτh satisfy the absolute error bound of (1.10)
(ii) (on preliminary mean estimates ˆθ): Assume one of the pairs (a,b) or (a,c) hold.
(a) The estimates ˆθ(j), j = 1,...,4 satisfy ∥(ˆθ(j))Sc
j ∥1 ≤3∥(ˆθ(j) −θ0
(j))Sj∥1, for each j =
1,...,4. Here Sj, are sets of non-zero components as deﬁned in (2.1).
(b) The estimates ˆθ(j), j = 1,...,4 satisfy the ℓ2 bound (1.8)
(c) The estimates ˆθ(j), j = 1,...,4 satisfy the ℓ2 bound (1.10)
Condition C has been carefully constructed while keeping in mind its feasibility. The
second combination of

(i)(b),(ii)(a,c)

is stronger version of the ﬁrst

(i)(a),(ii)(a,b)

.
In Subsection 2.2 we shall exploit this distinction to show that preliminary estimates ob-
tained recursively via Algorithm 1 satisfy the two considered combinations of this condi-
tion, at the two successive iterations, respectively. Condition C(i) and C(ii)(b) are excep-
tionally weak conditions on the quality these estimates. C(i) is satisﬁed by any ˆτw, ˆτh in
o(T)-neighborhood’s of τ 0
w,τ 0
h, respectively, i.e., all that is required is them to be consistent
at any arbitrary rate of estimation. Condition C(ii)(b) requires mean estimates to be of order
### Page 11

HD MEANS OVER 2D CHANGES
11
of the jump size ξmin, and may be weaker than assuming even ordinary consistency, i.e., an
op(1) approximation. Condition C(ii)(a) in a sense provides a restriction on the sparsity level
of the estimated mean parameters and is common in the ℓ1 regularization literature. Further,
other common regularization mechanisms, such as scad, mcp or the Dantzig selector are also
known to induce this property.
We note here that Condition C(ii) allows mean estimates ˆθ(j) to be irregular, in the sense
that they are only required to be in the given ℓ2 neighborhoods of θ0
(j)s. They are not required
to possess oracle properties, i.e., selection mistakes in the identiﬁcation of the signs of these
coefﬁcient do not inﬂuence the eventual change point estimate ˜τ in its rate of convergence
and limiting distribution. Accordingly, we do not require minimum magnitude conditions of
the coefﬁcient vectors θ0
(j), j = 1,2,3,4, which are typically made under high dimensionality
to guarantee selection consistency of signs in the components of these mean vectors.
The tightening of assumptions across combinations

C(i)(a),C(ii)(a,b)

and

C(i)(b),C(ii)(a,c)

has important consequences on the rate of convergence of ˜τ. This aspect shall become appar-
ent after the following estimation results and the discussion thereafter.
THEOREM 2.1.
Suppose the model (1.1) and assume Condition A, B, C(i)(a) and
C(ii)(a,b) hold. Then, we have,
(i) |˜τw −τ 0
w| ≤cuσ2T −1
h ξ−2
w slog2(p ∨TwTh)
(ii) |˜τh −τ 0
h| ≤cuσ2T −1
w ξ−2
h slog2(p ∨TwTh)
with probability at least 1 −2exp{−c1 log(p ∨TwTh)} −πT , for constant c1 > 0 that
does not depend on any model parameters. In other words, we have, (˜τw −τ 0
w) =
O
 T −1
h ξ−2
w slog2(p ∨TwTh)

and (˜τh −τ 0
h) = O
 T −1
w ξ−2
h slog2(p ∨TwTh)

, with proba-
bility at least 1 −o(1), where the orders are w.r.t. Tw and Th, respectively.
This result provides ﬁnite sample localization error bounds that are near-optimal and are
obtained upto universal constants. This is obtained under the weaker condition

C(i)(a),C(ii)(a,b)

on the preliminary estimates. While this result is informative in itself from an estimation per-
spective, however it does not possess the optimality necessary for the existence of limiting
distributions. Next we show the more important result that the rate of convergence can be
improved to optimality by making the sole change of tightening the preliminary estimates to
the combination

C(i)(b),C(ii)(a,c)

.
THEOREM 2.2.
Suppose the model (1.1) and assume Condition A, B, C(i)(b) and
C(ii)(a,c) hold. Then, for any 0 < a < 1 and ca ≥√(1/a), we have,
(i) |˜τw −τ 0
w| ≤cuc2
aσ2T −1
h ξ−2
w
(ii) |˜τh −τ 0
h| ≤cuc2
aσ2T −1
w ξ−2
h
with probability at least 1−a−o(1)−πT . Equivalently, we have, (˜τw −τ 0
w) = Op
 T −1
h ξ−2
w

and (˜τh −τ 0
h) = Op
 T −1
w ξ−2
h

, where the orders are w.r.t. Tw and Th, respectively.
Theorem 2.2 provides the optimal rate of convergence of ˜τ. This is the same rate of con-
vergence one would have obtained for ˜τw if the parameters τ 0
h and θ0
(j),j = 1,2,3,4 used in
its construction were known, and analogous for ˜τh. This observation provides a key insight,
it allows one to conclude that ˜τ statistically behaves as if these preliminary estimates are
known. This property in turn shall allow limiting distributions to exist and be characterized.
This is effectively the adaptation property as described in [10] but is observed here despite
potential high dimensionality of plug-in estimates and in context of change point parameters.
### Page 12

12
We can now proceed to establishing the limiting distributions of ˜τ. To this end, begin by
noting that as a direct consequence of Theorem 2.2 one may observe that when √Thξw →
∞, and √Twξh →∞, then the estimates ˜τw and ˜τh, perfectly identify the corresponding
change point parameters, in probability, i.e., the limiting distribution of ˜τ in these cases are
degenerate. As a result in the following we shall only be concerned with two regimes, ﬁrst of a
vanishing jump √Thξw →0, √Twξh →0, or that of a non-vanishing jump √Thξw →ξ(w,∞),
√Twξh →ξ(h,∞) where 0 < ξ(w,∞), ξ(h,∞) < ∞. We begin here with a mild condition that
shall ensure stability of asymptotic variances of the limiting processes to be characterized.
Condition D (stability of asymptotic variances): Let Σ, η0
(j), j = 1,2,3,4, and ξw,ξh be as
deﬁned in Condition B, (1.4) and (1.7) respectively. Then, assume the following limits exist,
(i)
1
ξ2w
h
ωhη0T
(1)Ση0
(1) + (1 −ωh)η0T
(3)Ση0
(3)
i
→σ2
(w,∞),
and
(ii)
1
ξ2
h
h
ωwη0T
(4)Ση0
(4) + (1 −ωw)η0T
(2)Ση0
(2)
i
→σ2
(h,∞),
with 0 < σ(w,∞), σ(h,∞) < ∞. Here the limit of (i) is with respect to Tw →∞(with Th < ∞
or Th →∞), and symmetrically (ii) is with respect to Th →∞(with Tw < ∞or Tw →∞).
Recall that all limits in the article are w.r.t. sampling periods Tw or Th (either individually
of simultaneously). The limits of Condition D are acting in Tw,Th via the dimension p and
the jump sizes ξw,ξh. The quantities σ2
(w,∞) and σ2
(h,∞) shall serve as variance parameters of
the limiting processes described in (1.12) and (1.15), thus the need for their stability. Note that
ﬁniteness of the limits appearing in Condition D are already guaranteed by prior assumptions,
and this condition only assumes their stability. To see this, consider Part (i) and note that the
assumed convergence is on a sequence that is guaranteed to be bounded, i.e.,
1
ξ2w
h
ωhη0T
(1)Ση0
(1) + (1 −ωh)η0T
(3)Ση0
(3)
i
≥κ2
ξ2w
(ωhξ2
1 + (1 −ωh)ξ2
3) ≥κ2 > 0, and
1
ξ2w
h
ωhη0T
(1)Ση0
(1) + (1 −ωh)η0T
(3)Ση0
(3)
i
≤φ2
ξ2w
(ωhξ2
1 + (1 −ωh)ξ2
3) ≤φ2 < ∞,
and similar for Part (ii). Here the inequalities follow from the bounded eigenvalues assump-
tion on Σ
 Condition B(i)

. An easier to interpret, but stronger sufﬁcient condition for the
ﬁniteness for the limits with respect to the covariance matrix Σ is by assuming absolute
summability of each row or column of Σ. This condition is satisﬁed by large classes of co-
variances such as banded and toeplitz type matrices. We refer to Condition D of [28] for
further details on this argument.
THEOREM 2.3 (Limiting distribution under vanishing jump regime).
Suppose Condi-
tions A, B and D hold. Assume that the jump sizes are vanishing √(Th)ξw →0, and
√(Tw)ξh →0. Let the parameters τ 0
w,τ 0
h and θ0
(j), j = 1,2,3,4, be known and let ˜τ ∗
w =
˜τw(τ 0
h,θ0), ˜τ ∗
h = ˜τh(τ 0
w,θ0). Then, we have,
T −1
h ξ2
w(˜τ ∗
w −τ 0
w) ⇒arg max
ζ∈R

2σ(w,∞)Ww(ζ) −|ζ|},
Tw →∞,
T −1
w ξ2
h(˜τ ∗
h −τ 0
h) ⇒arg max
ζ∈R

2σ(h,∞)Wh(ζ) −|ζ|},
Th →∞,
(2.2)
### Page 13

HD MEANS OVER 2D CHANGES
13
where Ww(ζ), and Wh(ζ) are both two sided Brownian motionsvii. Alternatively, when τ 0
w,
τ 0
h and θ0
(j), j = 1,2,3,4, are unknown, suppose ˜τw = ˜τw(ˆτh, ˆθ), ˜τh = ˜τh(ˆτw, ˆθ). assume
Condition C(i)(b) and C(ii)(a,c) are satisﬁed with rT = o(1)

{s1/2 log(p ∨T)}. Then, the
convergence (2.2) also holds when ˜τ ∗
w, ˜τ ∗
h are replaced with ˜τw, ˜τh, respectively.
The limiting distributions of ˜τw and ˜τh can be utilized to construct asymptotically valid
component-wise conﬁdence intervals for the change parameters in the horizontal and vertical
directions under the assumed vanishing jump regime. It can be observed that a change of vari-
able to ζ = σ2
∞ζ′, yields that arg maxζ∈R

2σ∞W(ζ)−|ζ|} =d σ2
∞arg maxζ′∈R

2W(ζ′)−
|ζ′|}, which in turn yields the relations in (1.12) provided in Section 1. This distribution is
well studied in the literature and its cdf is available in [44].
Next we consider non-vanishing regime of √(Th)ξw →ξ(w,∞), and √(Tw)ξh →ξ(h,∞).
The literature on distributional properties of ˜τ in this case is quite sparse. The only arti-
cles that provide an examination of this regime under high dimensional asymptotics are [25]
and [28], under a single change axis framework. In the same framework, the articles of [7]
and [9] consider the diverging p case with p << T. We require an additional distributional
assumption for the analysis of this regime provided below.
Condition A′ (additional distributional assumptions): Suppose Condition A, B and D
hold. Assume the non-vanishing jump size regime, i.e., √(Th)ξw →ξ(w,∞), and √(Tw)ξh →
ξ(h,∞), with 0 < ξ(w,∞),ξ(h,∞) < ∞. For each w = 1,...,Tw and h = 1,...,Th deﬁne,
ψw,Tw =
h
Th
X
h=τ 0
h+1
εT
(w,h)η0
(1) +
τ 0
h
X
h=1
εT
(w,h)η0
(3)
i
,
and
ψh,Th =
h
Tw
X
w=τ 0
w+1
εT
(w,h)η0
(4) +
τ 0
w
X
w=1
εT
(w,h)η0
(2)
i
The we assume that for any constants c1,c2 ∈R, and for some distribution P, which is
continuous and supported in R, we have,
(i) c1 + c2ψw,Tw ⇒P
 c1,c2
2ξ2
(w,∞)σ2
(w,∞)

,
and,
(ii) c1 + c2ψh,Th ⇒P
 c1,c2
2ξ2
(h,∞)σ2
(h,∞)

.
Here σ2
(w,∞) and σ2
(h,∞) are as deﬁned in Condition D.
Note that the only additional requirement imposed by Condition B′, in comparison to
Conditions B and D, is that the random variables under consideration are continuously dis-
tributed, which is trivially true in the typically assumed Gaussian framework. To see this,
note that the mean Eψw,Tw = c1 follows directly from deﬁnition of ψw,Tw and by the zero
mean assumption of ε(w,h). The variance var(ψw,Tw) →c2
2ξ(w,∞)σ2
(w,∞) follows from Con-
dition D together with the considered non-vanishing jump regime. Consequently, the limiting
distribution of the sequence ψw,Tw (in Tw via p and ξw) is well deﬁned, i.e. i.e., supported
in R. Consequently, Condition B′ simply provides a notation P to whatever distribution this
may be. Analogously for the sequence ψh,Th. We also note there that the arguments in the
notation P(µ,σ2) are used to represent the mean and variance of the distribution P, i.e,
EP(µ,σ2) = µ, and var
 P(µ,σ2)

= σ2. Further note that the representation P(µ,σ2) is
viiA two-sided Brownian motion W(ζ) is deﬁned as W(0) = 0, W(ζ) = W1(ζ), ζ > 0 and W(ζ) =
W2(−ζ), ζ < 0, where W1(ζ), W2(ζ) are two independent Brownian motions deﬁned on the non-negative
half real line
### Page 14

14
only for ease of presentation and does not imply that P is characterized by only its mean and
variance. If one assumed ε(w,h) ∼N(0,Σ) on the data generating process of (1.1), then it is
straightforward to observe that P =d N.
The two-sided random walk deﬁned in (1.13) can now be utilized in order to charac-
terize the limiting distribution of the change point estimators ˜τw and ˜τh, in the current
non-vanishing jump size regime. For the width change parameter this stochastic process
shall have the increments as zt ∼i.i.d P
 −ξ2
(w,∞), 4ξ2
(w,∞)σ2
(w,∞)

and z∗
t ∼i.i.d P
 −
ξ2
(w,∞), 4ξ2
(w,∞)σ2
(w,∞)

, and zt and z∗
t are also independent of each other over all t, with
an analogous construction for the height change parameter. The only additional assumption
of Condition B′, of continuity of the distribution law P is assumed for the regularity of the
argmax of this two sided random walk.
THEOREM 2.4 (Limiting distribution under non-vanishing jump regime).
Suppose Con-
ditions A′, B, D hold. Assume that the jump sizes are non-vanishing √(Th)ξw →ξ(w,∞),
and √(Tw)ξh →ξ(h,∞). Let the parameters τ 0
w,τ 0
h and θ0
(j), j = 1,2,3,4, be known and let
˜τ ∗
w = ˜τw(τ 0
h,θ0), ˜τ ∗
h = ˜τh(τ 0
w,θ0). Then, we have,
(˜τ ∗
w −τ 0
w) ⇒arg max
ζ∈Z
C(w,∞)(ζ),
Tw →∞,
(˜τ ∗
h −τ 0
h) ⇒arg max
ζ∈Z
C(h,∞)(ζ),
Th →∞,
(2.3)
where C(w,∞)(ζ) and C(h,∞)(ζ) are as deﬁned in (1.13) and (1.14). Alternatively, when τ 0
w,
τ 0
h and θ0
(j), j = 1,2,3,4, are unknown, suppose ˜τw = ˜τw(ˆτh, ˆθ), ˜τh = ˜τh(ˆτw, ˆθ). assume
Condition C(i)(b) and C(ii)(a,c) are satisﬁed with rT = o(1)

{s1/2 log(p ∨T)}. Then, the
convergence (2.2) also holds when ˜τ ∗
w, ˜τ ∗
h are replaced with ˜τw, ˜τh, respectively.
The only distinction between the assumptions of Theorem 2.3 and Theorem 2.4 is the
change of regime from a vanishing jump size to the non-vanishing jump size regime, respec-
tively. Since the analytical form of the distribution arg maxζ∈Z C(w,∞)(ζ) and arg maxζ∈Z C(h,∞)(ζ)
are unavailable, one may resort to obtaining quantiles of these distributions via monte-carlo
simulations, i.e., simulating the two sided random walk process and in turn obtaining real-
izations from the distribution under consideration.
While the above discussion provides the statistical properties of ˜τ, however note that it
is not as yet implementable in practice since its construction requires preliminary estimates
that have so far not been explicitly deﬁned. Nonetheless, one may perhaps be surprised to
note that thus far we have not assumed any conditions on the rate of divergence of the model
dimensions (s,p) or on the jump size ξmin, w.r.t the sampling periods Tw,Th. The reason for
this observation is that, effectively, the burden of these assumptions have been pushed to the
preliminary nuisance estimates through Condition C. These conditions shall materialize in the
following sub-section where we provide a feasible methodology along with the construction
of nuisance estimates. Some intuition into the origination of these rate assumptions and their
inter-relationship to Condition C are discussed below.
In order to aggregate our theoretical results into a feasible twice iterative algorithm, we
shall utilize the near optimal change point estimates of Theorem 2.1 as preliminary nuisance
estimates feeding into Theorem 2.2. Consequently we shall require the near optimal rate
yielded by Theorem 2.1 to satisfy the assumed requirement of Condition C(i)(b) for Theorem
2.2. Accordingly, for this relation to be maintained, we must have,
cuσ
ξmin
nslog2(p ∨TwTh)
√(TwTh)
o
≤cu1,
(2.4)
### Page 15

HD MEANS OVER 2D CHANGES
15
for a suitably chosen small enough constant cu1 > 0. This aspect provides the strongest re-
quirement on the rate of divergence of model dimensions and the jump size that we shall
require for the validity of all results to follow. The preliminary mean estimates shall also be
feasible to obtain under the same requirement. To see this, note that the sharpest ℓ2 rate of
estimation of mean parameters ˆθ(j) is known to be,
max
j
∥ˆθ(j) −θ0
(j)∥2 ≤rT = cuσ
slog(p ∨TwTh)
TwThω
 1
2 ,
(2.5)
with probability 1−o(1). Now Comparing (2.5) with Condition C(ii)(c) one can observe that
in order to maintain viability of Condition C(ii)(c), we must have, cuslog3/2(p ∨TwTh) ≤
cu1ξmin
√(TwThω). Finally observe that this rate requirement is weaker than (2.4) in all but
the weight parameter ω. Thus in the interest of notational simplicity, we shall be utilizing
the condition (1.19) described in Section 1. The following sub-section provides a detailed
examination of this discussion.
2.2. Preliminary estimates ˆτ, ˆθ and validity of Algorithm 1.
The main purpose of this sub-section is to ﬁll gaps that remain to allow the feasibility
of ˜τ, i.e., to develop preliminary estimates ˆτ, ˆθ in a principled manner so that results of
Theorem’s 2.2 - 2.4 can be appealed to in context of the output of Algorithm 1. To this
end, recall that these preliminary estimates require either condition’s

C(i)(a),C(ii)(a,c)

(milder) to obtain a near optimal estimate, or condition’s

C(i)(b),C(ii)(a,c)

(stronger)
to obtain an optimal estimate of τ 0. Algorithm 1 utilizes the soft thresholded means (1.17)
and the distinctions between the pairs of assumed conditions to provide an estimator that
improves a nearly arbitrarily chosen ˇτ, to a near optimal estimate ˆτ in a ﬁrst iteration, and
then to an optimal estimate ˜τ in a second iteration. To further describe the idea and constraints
behind the validity of Algorithm 1 we require the following two additional conditions.
Condition E (on dimensional and jump size rate restrictions): Let ξmin be as deﬁned in
(1.7) and let s,p be the sparsity parameter (see, (2.1)) and dimension size, respectively. Then,
for an appropriately chosen small enough constant cu1 > 0, assume the following relation
holds.
 cuσ
ξmin
nslog2(p ∨TwTh)
√(TwThω)
o
≤cu1.
Additionally, assume that slog(p ∨TwTh) ≤cuTwThω, for some constant cu > 0.
The purpose of Condition E is chieﬂy to ensure that the near optimal estimates obtained
from the ﬁrst iteration of Algorithm 1 satisfy the sharper conditions of

C(i)(b), C(ii)(c)

.
This allows Algorithm 1 to proceed to step 2 with these as the preliminary estimates.
Next recall that condition C(i)(a) is very mild, in particular, all it requires are any τw,τh
in o(Tw) or o(Th) neighborhood’s of the change parameters τ 0
w,τ 0
h, respectively. Following
is an almost equivalent version of this condition and a discussion on the utility, requirement
and viability of both of them immediately thereafter.
Condition F (initializer of Algorithm 1): Let ψ = max1≤j≤4 ∥η0
(j)∥∞, and assume that the
initializer ˇτ = (ˇτw, ˇτh)T of Algorithm 1 satisﬁes the relations.
(i) |ˇτw −τ 0
w| ≤
cu1Twω
 √sψ

ξmin
,
and
|ˇτh −τ 0
h| ≤(ii)
cu1Thω
 √sψ

ξmin
.
Additionally assume (iii) min1≤j≤|Qj(ˇτ)| ≥cuTwThω. Here ω is as deﬁned in Condition
B, cu > 0 is any constant and cu1 > 0 is an appropriately chosen small enough constant.
### Page 16

16
Requirement (iii) of Condition F is clearly innocuous, all it requires is a marginal separa-
tion of the chosen ˇτ from the parametric boundary of the 2d change point. It is satisﬁed with
ˇτ = (⌊Twkw⌋, ⌊Thkh⌋)T =, with any (kw,kh)T ∈[cu1,cu2] × [cu1,cu2] ⊂(0,1) × (0,1).
Requirement (i) and (ii) are symmetrical versions in the horizontal and vertical directions,
respectively. Thus we only discuss the mildness of (i), ﬁrst from a theoretical and then fol-
lowed by a practical perspective, these arguments shall also symmetrically hold for (ii). We
begin by illustrating the near equivalence of F(i) to Condition C(i)(a). Consider the case
when ω ≥cu, i.e., the true change point in the fractional scale is in some bounded subset of
(0,1) × (0,1), and that
 √sψ

ξ

= O(1), i.e., the entries of the change vectors η0
w,η0
h are
roughly evenly spread across its non-zero components and not with uneven diverging spikes,
this is also satisﬁed if one assumes ψ ≤cu, i.e., when all mean parameters are bounded above.
Both of these restrictions are common to the change point literature. Then, requirement F(i)
becomes identical to C(i)(a), moreover, both are satisﬁed for all ˇτw in an o(Tw) neighborhood
of τ 0
w, i.e., any ˇτw satisfying |ˇτw −τ 0
w| = o(Tw). The reason for these conditions to appear
separately despite their near equivalence is that Condition F ensures weak regularity of the
initializing mean estimates ˇθ(j), j = 1,2,3,4 and Condition C(i)(a) ensures a weak regularity
of the Step 1 (of Algorithm 1) change point estimate ˆτ. One may interpret both Condition
C(i)(a) and Condition F as ordinary consistency of the initializer ˇτ, while also recalling that
this property under bounded a parametric space is a very weak statement.
We can now describe the working mechanism of Algorithm 1 in its entirety. Any nearly
arbitrarily (Condition F) chosen ˇτ = (ˇτw, ˇτh)T , yields Step 1 means ˇθ(j) = ˆθ(j)(ˇτ), j =
1,2,3,4, of (1.17) that satisfy the weaker Condition C(ii)(a,c). Theorem 2.1 now guarantees
that update ˆτ = (ˆτw, ˆτh)T , where ˆτw = ˜τw
 ˇτh, ˇθ), and similar for ˆτh, shall be a near optimal
estimate of τ 0. Under the rate assumption of Condition D, this near optimal ˆτ together with
the updated mean estimates ˆθ(j) = ˆθ(j)(ˆτ), j = 1,2,3,4, satisfy the stronger requirements
of Condition C(i)(b) and C(ii)(a,c). This allows us to perform another update ˜τ = (˜τw, ˜τh),
with ˜τw = ˜τ(ˆτh, ˆθ), and similar for ˆτh. Theorem 2.2 now guarantees optimality of this Step
2 updated estimate ˜τ, moreover, its limiting distributions can also be characterized as per
Theorem 2.3 and Theorem 2.4. Thus, in performing these updates (two each of the change
point and the mean, with internal iterations on the components of τ) we have taken a ˇτ from
a nearly arbitrary neighborhood of τ 0, and deposited it in an optimal neighborhood of τ 0,
with an intermediate ˆτ that lies in a near optimal neighborhood, i.e. o(Tw)-nbd.−→Step1
near optimal-nbd., Op(T −1
h ξ−2
w slog2 p) −→Step2 optimal-nbd., Op(T −1
h ξ−2
w ), in context of
the width change parameter τw, and symmetrically for τh. This is the process stated as Algo-
rithm 1 and described visually in Figure 3.
From a practical perspective, robustness w.r.t choice of initializer ˇτ has also been illus-
trated in [26, 25] in other dynamic contexts through extensive numerical experiments. We
note that this initializer question also arise in the traditional regression tree algorithm where
the same robustness has been observed in innumerable studies. While we have characterized
the initializing Condition F, similar conditions have also been implicitly assumed in the lit-
erature, e.g., [1]. Nevertheless, one may choose a theoretically valid initializer ˇτ satisfying
Condition F by utilizing a preliminary coarse grid search, e.g. one may choose any slowly
diverging sequence (say log(·) ) and choose log Tw equally separated values in {1,...,Tw},
and log Th equally separated values in {1,...,Th}, forming a coarse grid of log Tw log Th pos-
sible 2d-initializer values. Upon choosing the best ﬁtting value ˇτ = (ˇτw, ˇτh) for Algorithm
1 from this coarse initializer grid and assuming that the best ﬁtting value is component-
wise closest to τ 0, amongst the chosen grid points. Then by the pigeonhole principle the
choice of ˇτw and ˇτh must be in an Tw/log Tw = o(Tw) and Th/log Th = o(Th) neighbor-
hoods of τ 0
w and τ 0
h, respectively. Thereby this ˇτ shall form a theoretically valid initializer.
A similar preliminary coarse grid search has also been heuristically utilized in [33] in a
### Page 17

HD MEANS OVER 2D CHANGES
17
ˇτw
ˇτh
ˇθj = ˆθj(ˇτ)
j = 1,2,3,4.
ˆτw = ˜τ(ˇτh, ˇθ)
ˆτh == ˜τ(ˇτw, ˇθ)
ˆθj = ˆθj(ˆτ)
j = 1,2,3,4.
˜τw = ˜τ(ˆτh, ˆθ)
˜τh == ˜τ(ˆτw, ˆθ)
Condition
F satisﬁed
(nearly
arbitrary
choice)
Condition
C(ii)(b) satisﬁed
Near optimal,
Condition
C(i)(b) satisﬁed
Condition
C(ii)(c) satisﬁed
Optimal,
Op
 T −1ξ−2
Step 1
Step 2
Initialize
FIG 3. A schematic of the underlying working mechanism of Algorithm 1.
different model setting, where it also points towards an implicit need for an assumption sim-
ilar to Condition F. In applications of Section 4 and simulation experiments of Section 5
we consider a preliminary grid search of (ˇτw, ˇτh) ∈{⌊0.25·Tw⌋,⌊0.5·Tw⌋,⌊0.75·Tw⌋} ×
{⌊0.25·Th⌋,⌊0.5·Th⌋,⌊0.75·Th⌋} to choose the initializer.
The following corollary provides a precise description of the above discussion, in partic-
ular, it aggregates the results of Sub-section 2.1 to provide the validity of Algorithm 1, in
context of its estimation and inference properties.
COROLLARY 2.1.
Suppose Condition A, B, E and F hold and assume the regularizers
for mean estimates of Step 1 of Algorithm 1 are chosen as in (A.49), Then,
(a) the Step 1 estimate ˆτ = (ˆτw, ˆτh)T satisﬁes the near optimal bounds of Theorem 2.1.
Additionally, suppose the regularizers for mean estimates of Step 2 are chosen as in (A.53)
and assume (ψ/ξmin

≤cu
√{log(p ∨T)}. Then,
(b) the Step 2 estimate ˜τ = (˜τw, ˜τh)T satisﬁes the optimal error bounds of Theorem 2.2.
Furthermore, suppose the rate assumption of Condition E is slightly tightened to {slog2(p ∨
TwTh)} = o
 ξmin
√(TwThω)
viii, and assume Condition A′ and D holds. Then,
(c) the Step 2 estimate ˜τ = (˜τw, ˜τh)T satisﬁes the limiting distributions of Theorem 2.3 and
Theorem 2.4, in the vanishing and non-vanishing jump size regimes, respectively.
The above result completes the description of Algorithm 1. Following are two observa-
tions regarding minor additional assumptions that have thus far not been discussed. First
on tightening the dimensional rate requirement from O(1) in the r.h.s. of Condition E, to
o(1) for Part (c) of Corollary 2.1. This can be viewed as price paid to obtain existence of
limiting distributions in comparison to only the availability of optimal rates of estimation.
This slight tightening is also in coherence with classical results in the ﬁxed dimensional
and single change axis framework, see, e.g., [2, 3]. The second additional assumption here
is (ψ/ξmin

≤cu
√{log(p ∨T)}, made for Part (b). Some insight into this assumption was
provided after Condition F. It can be viewed as restriction stating the jump vectors in both
viiiWe do not necessarily require the order o(1) here to hold simultaneously w.r.t Tw,Th. If this order holds
w.r.t. Tw →∞(Th < ∞or Th →∞) then it is sufﬁcient in context of the width change parameter τ0w, and
symmetrically for the height change parameter.
### Page 18

18
the horizontal and vertical directions are somewhat evenly spread across its non-zero com-
ponents, with control of order log(p ∨TwTh) on the rate of divergence on individual spikes
within these components. The sufﬁcient condition ψ ≤cu, i.e., bounded components of all
mean vectors, can also be made to ensure this assumption. Such boundedness of mean vectors
has also been prevalent assumption in the existing change point literature.
The remainder of this sub-section provides two important remarks, ﬁrst on a comparison
with change point models with a single change axis. Followed by one on weakening the
assumption of existence of a change point (Condition B(ii)) and extending the methodology
to allow for selection in this context.
REMARK 1 (Comparison with dynamic mean models with a one-dimensional change
axis).
The deﬁning advantage of model (1.1) over a conventional 1d-change axis frame-
work is the ability to recover this simultaneous change with guaranteed statistical properties.
This ability from a jump size perspective can be viewed as being able to leverage observed
data in a secondary direction to detect much ﬁner changes in a either directions. More pre-
cisely, model (1.1) and Algorithm 1 leads to the ability to detect a change in the horizontal
direction with a jump size magnitude that may be smaller by an order of √Th, and vice-
versa. This can be observed from the assumed Condition E, where under ﬁxed p we have
ξ ≥cu
 1
√(TwTh)

, as opposed to the 1d-change axis framework where one will require at
the very least ξ ≥cu
 1
√Tw

, see, e.g., [43] and [25].
REMARK 2 (Boundary cases of τ 0 = (Tw,τ 0
h)T , τ 0 = (τ 0
w,Th)T or τ 0 = (Tw,Th)T ix).
Recall that Condition B(ii) assumes that the 2d-change point is separated from parametric
boundaries. This assumption can be relaxed by utilizing a conventional 0-norm regularization
technique in order to allow selection of the change point at boundary values. This can be
achieved by replacing Step 1 of Algorithm 1 with a regularized version,
ˆτ ∗
w = arg min
1≤τw≤Tw

L(τw, ˇτh, ˇθ) + γw1[τw ̸= Tw]
	
,
γw > 0,
ˆτ ∗
h = arg min
1≤τh≤Th

L(ˇτw,τh, ˇθ) + γh1[τh ̸= Th]
	
,
γh > 0.
Here γw,γh are tuning parameters. It can be observed that the 0-regularized ˆτ ∗can also be
equivalently represented as,
ˆτ ∗
w =
(
Tw
if {L(Tw, ˇτh, ˇθ) −L(ˆτw, ˇτh, ˇθ)} < γw,
ˆτw
else,
ˆτ ∗
h =
(
Th
if {L(ˇτw,Th, ˇθ) −L(ˇτh, ˆτh, ˇθ)} < γh,
ˆτh
else,
(2.6)
where ˆτw and ˆτh are the un-regularized versions under the restricted search space obtained in
Step 1 of Algorithm 1. Representation (2.6) is more common to change point literature, see,
e.g. [19] and [43], where it is utilized to extend a single axis and single change point method
to multiple change points via variants of binary segmentation. A version of Algorithm 1
obtained by introducing this relaxation is described as Algorithm 2.
ixWhile boundary values can be equivalently characterized as either,

τ0 = (Tw,τ0
h)T , τ0 = (τ0w,Th)T or
τ0 = (Tw,Th)T 
or

τ0 = (0,τ0
h)T , τ0 = (τ0w,0)T or τ0 = (0,0)T ,

. However, clearly both these character-
izations are not simultaneously identiﬁable since at these boundary values, realizations from two or three of the
underlying distributions are not observed.
### Page 19

HD MEANS OVER 2D CHANGES
19
Algorithm 2 Optimal estimation of τ 0 = (τ 0
w,τ 0
h)T with boundary selection
Initialize change point ˇτ = (ˇτw, ˇτh),
1: Compute mean estimates ˇθ(j) = ˆθ(j)(ˇτ), j = 1,2,3,4. and change point estimate ˆτ = (ˆτw, ˆτh)T as Step 1
of Algorithm 1. Additionally perform selection by obtaining ˆτ∗= (ˆτ∗w, ˆτ∗
h)T as (2.6).
2: If ˆτ∗w = Tw, then set ˜τw = Tw. Else update mean estimates to ˆθ(j) = ˆθ(j)(ˆτ), j = 1,2,3,4, and update,
˜τw = arg min
1≤τw<Tw
L(τw, ˆτ∗
h, ˆθ).
Similarly, if ˆτ∗
h = Th, then set ˜τh = Th. Else, update,
˜τh = arg min
1≤τh<Th
L(ˆτ∗w,τh, ˆθ)
Output: ˜τ = (˜τw, ˜τh).
Selection consistency
 pr(˜τw = Tw) →1, Tw →∞, when τ 0
w = Tw and symmetrical for
˜τh.

yielded by this 0-regularization can be additionally veriﬁed via fairly conventional ar-
guments, see, e.g. [26].
3. Generalizations to full regression trees.
Regression trees in the current literature
are limited to a one-dimensional response p = 1. These objects are typically represented as
the following model (see, e.g. Page 307 of [18]),
x(w,h) =
M
X
m=1
θ0
(m)1[(w,h) ∈Ωm] + ε(w,h),
(3.1)
in the case of q = 2x dimensional feature space (or 2d-change axes in our terminology).
Here Ωm, m = 1,...,M represent disjoint partitioning sub-rectangles of the sampling space
{1,...,Tw} × {1,...,Th}, and θ0
(m) are representative of underlying p = 1 dimensional dy-
namic mean parameters. The frequentist approach (see, e.g. Page 307, 308 of [18]) to recov-
ery of the associated tree, i.e., estimation of rectangle Ωm, m = 1,..,M, proceeds via binary
half-plane splits of the sampling space via a greedy algorithm. Despite its prevalent use in the
machine learning landscape, to our knowledge there is no analytical support available in the
current literature towards statistical properties of these estimated transition points. Trees with
a multi-dimensional p > 1 response have not been considered in the literature. Model (1.1)
views the regression tree (3.1) from a 2d-change point perspective under the special case of
M = 4 partitioning sub-rectangles under a high dimensional response p >> (TwTh), further-
more, Algorithm 1 and the results of the previous section provide both estimation and infer-
ential properties of the behavior of the recovered transitioning points under this HD frame-
work with M = 4. The relaxation of Remark 2 extends these results to the M = 1,2 or 4
cases. Conceptual similarities of this algorithm to the proposed Algorithm 1 as discussed
in Section 1 also provides alternative insight into the equivalence of the model (3.1) (under
M = 1,2 or 4) and the change point perspective taken thus far in this article.
The remainder of this section is devoted to characterizing generalizations of the model
(1.1), so as to allow the regression tree model structure (3.1) under any unknown number
M of partitioning rectangles (or hyper-rectangles), and allowing high dimensionality of the
response. Then to provide methodological extensions to recover these underlying HD trees.
We mention here that the methodology extensions to follow shall be heuristic although these
shall be validated numerically in this article. These extensions are motivated by classical
xThe case of q > 2 generalizes to hyper-rectangles Ωm, m = 1,...,M.
### Page 20

20
results in the change point literature with established statistical properties (in a 1d-change
axis and ﬁxed p framework). The important contribution here shall be in the formulation
of the generic regression tree in a change point framework, thereby allowing a clear path
forward toward a statistical examination of the proposed methods as future work. The reason
for our inability to examine these properties is particulary owed to high dimensionality of
the response, where inferential properties under multiple change points are unknown in the
literature even at a more fundamental level of a 1d-change axis framework, which ﬁrst need
addressal before analogous question can be pursued in this framework.
Accommodating regression trees in full generality require the following generalizations of
model (1.1), which shall in turn also require us to deﬁne additional notation and conventions.
G.1 Allow boundary cases of change point parameters, τ 0 = (Tw,τ 0
h)T , τ 0 = (τ 0
w,Th)T or
τ 0 = (Tw,Th)T in order to allow ‘no partition’ and ‘half-plane partition’ cases.
G.2 Generalize model (1.1) to allow multiple 2d-change points that are to be introduced in
a hierarchical manner, i.e., to allow each quadrant/half-plane split by a previous change
point to be further divided into fourths/halfs by new change points.
G.3 Allow feature space to be of q > 2 dimensions, i.e., allow framework of a p-dimensional
response and a q-dimensional feature space (or q-dimensional change points).
The generalization of G.1 has already been considered in Remark 2 and the corresponding
extension described in full in Algorithm 2. Next we proceed to the generalization of G.2.
Recall the collection of indices deﬁned as quadrants Qj(τ) ⊆{1,...,Tw} × {1,...,Th}, j =
1,2,3,4. By convention, the ordering of these j = 1,2,3,4, quadrants is assumed as top
right, tope left, bottom left and bottom right, respectively, with both change axes labeled
in ascending order. We shall retain this ordering in all to follow. Moreover, when τ is in a
boundary condition, then two or three of these quadrants are to be deﬁned as empty sets,
e.g., if τ = (Tw,Th)T , then Qj(τ) = φ, j = 1,2,4, and Q3(τ) = {1,...,Tw} × {1,...,Th}.
Similarly, if τ = (τw,Th)T , τw < Tw, then Qj(τ) = φ, j = 1,2 and Q3(τ) = {1,...,τw} ×
{1,...,Th} and Q4(τ) = {(τw + 1),...,Tw} × {1,...,Th}. Symmetrically, if τ = (Tw,τh)T ,
τh < Th, then Qj(τ) = φ, j = 2,3.
Next, we deﬁne a notion of hierarchical multiple change points where each induced quad-
rant is allowed to further sub-partition. In other words each parent change point gives rise
to four child change points in a hierarchical sense. Following notation is necessary to de-
scribe this precisely. Let τ 0 = (τ 0
w,τ 0
h)T ∈{1,...,Tw} × {1,...,Th} represent the zeroth level
change point as considered in model (1.1). Then for a ﬁrst hierarchical step, deﬁne four chil-
dren change points spawned by τ 0, in same order as the quadrants, i.e.,
τ 0
i1 ∈Qi1(τ 0),
i1 = 1,2,3,4,
(3.2)
Moreover, each new change point induces four sub-quadrants and consequently four new
mean vectors, we represent the means yielded by τi1 as follows, for each i1 = 1,2,3,4, deﬁne,
Ex(w,h) = θ0
(i1i2)1

(w,h) ∈Qi1(τ 0) ∩Qi2(τ 0
i1)

,
i2 = 1,2,3,4.
(3.3)
Continuing this hierarchical construction, i.e., further sub-splitting each partitioning rectan-
gle by children change points, we have from the second to the ℓth hierarchical level,
τ 0
i1i2 ∈Qi1(τ 0) ∩Qi2(τ 0
i1),
i1,i2 = 1,2,3,4
τ 0
i1i2i3 ∈Qi1(τ 0) ∩Qi2(τ 0
i1) ∩Qi3(τ 0
i1i2),
i1,i2,i3 = 1,2,3,4
...
τ 0
i1i2...iℓ∈Qi1(τ 0) ∩Qi2(τ 0
i1) ∩Qi3(τ 0
i1i2)... ∩Qiℓ
 τi1i2...i(ℓ−1)

i1,...,iℓ= 1,2,3,4.
(3.4)
### Page 21

HD MEANS OVER 2D CHANGES
21
(0,0)
Th
Tw
Width (w)
Height (h)
τ0
τ0
1
τ0
2
τ0
3
τ0
4
(0,0)
Th
Tw
Width (w)
Height (h)
θ0
(11)
θ0
(12)
θ0
(13)
θ0
(14)
θ0
(24)
θ0
(23)
θ0
(22)
θ0
(21)
θ0
(34)
θ0
(33)
θ0
(32)
θ0
(31)
θ0
(44)
θ0
(43)
θ0
(42)
θ0
(41)
FIG 4. Visualization of underlying mean and change point parameters of ℓ-hierarchical model (3.5) with ℓ= 1.
In the following we represent the ﬁnest level parametric space of the change point parameters
with a slight misuse of notation as,
ℓ\
j=1
Qij
 τ 0
Πj−1
k=1ik

= Qi1(τ 0) ∩Qi2(τ 0
i1) ∩Qi3(τ 0
i1i2)··· ∩Qil
 τi1i2···i(ℓ−1)

.xi
Now, the corresponding means at the ﬁnest partitioning level (ℓth hierarchical level) become,
Ex(w,h) = θ0
(iii2...i(ℓ+1))1
h
(w,h) ∈
ℓ+1
\
j=1
Qij
 τ 0
Πj−1
k=1ik
i
.
The above notations now allow a parametric description of a ℓ-hierarchical multiple 2d-
change point model as,
x(w,h) =
4
X
i1=1
4
X
i2=1
...
4
X
i(ℓ+1)=1
|
{z
}
ℓ+1 iterated sums
θ0
(i1i2...i(ℓ+1))1
h
(w,h) ∈
ℓ+1
\
j=1
Qij
 τ 0
Πj−1
k=1ik
i
(3.5)
+ ε(w,h),
w = 1,...,Tw, h = 1,...,Th.
Construction (3.5) is a natural 2d-extension of a 1d multiple change point model. Recall that
even under 1d multiple change points, each change point can be viewed hierarchically w.r.t.
prior and post change points, in the sense that each new change point has its parametric space
restricted by the prior and post change points. The additional complications seen above arise
due these parametric spaces being restricted on two axes. A visualization of this construction
is provided in Figure 4. Following is a ﬁnal note on notation. Recall that by construction,
each change point is also allowed to be on its respective parametric boundaries, thus, we
call the model (3.5) as being ℓ-hierarchical if there exists at least one change point at the ℓth
hierarchy which is away from its parametric boundaries (also see Remark 3).
REMARK 3 (On the number of induced partitions).
Observe that when all change points
at all levels of hierarchy are separated from their parametric boundaries, the maximum possi-
ble number of change points induced by the model (3.5) is 1+4+42 +....4l = (4l+1 −1)/3.
Similarly, at this ﬁnest level, the sampling period {1,...,Tw}×{1,...,Th} is segmented into a
xiThe notation Πj
k=1ik only represents the indexing (i1i2,...,ij), and does not represent any actual product.
### Page 22

22
maximum number of 4l+1 distinct p-dimensional mean parameter vectors. On the other hand,
when change point are at boundaries, the model (3.5) allows the number of sampling period
partitions to be much smaller. For e.g., consider the 1-hierarchical model visualized in Figure
4. Suppose the ﬁrst of the ﬁrst level change points is at a boundary, e.g, τ 0
1 = (Tw,Th)T . Then
the number of distinct partitions of the sampling period becomes 3∗4+1 = 13. Another con-
sequence of the boundary change τ 0
1 = (Tw,Th)T is that three of the four sub-quadrants in-
duced by this boundary change are empty sets, in particular Q1(τ 0)∩Qj(τ 0
1 ) = φ, j = 1,2,4.
Thus, no further hierarchical changes can be spawned within these sub-quadrants, in other
words, further change points within these sub-quadrants are all at the same boundary point
(Tw,Th)T . Analogous patterns can be observed at half plane partitioning boundary change
points, e.g., τ 0
1 = (τ 0
1,w,Th)T or τ 0
1 = (Tw,τ 0
1,h)T .
The ℓ-hierarchical construction of model (3.5) allows a natural extension of the method-
ology of Algorithm 1 and 2. Recall that in a 1d-multiple change point framework a well es-
tablished technique that allows a similar extension is that of binary segmentation. Under our
framework, the natural variant of this technique become quarterly segmentation. More specif-
ically, one may apply the regularized version of Algorithm 2 on the entire sampling period to
ﬁrst ﬁnd the zeroth level change point. If this change point is at the boundary ˆτ = (Tw,Th)T
then no change points are observed. Else, one may segment the observed realizations into
the half plane or quarter partitions induced by the estimated change point ˆτ, and again apply
Algorithm 2 within each of these partitions to detect further hierarchical changes. One may
continue these recursions until no further changes are detected in any partition induced by a
change point of the prior hierarchy. This process is described as Algorithm 3.
Algorithm 3 Quarterly segmentation
Initialize: ˜τst = φ (empty matrix (2-rows) collecting all 2d-change points to be estimated over columns);
Implement ˜τ= Alg. 2
 {1,...,Tw} × {1,...,Th}

if ˜τ = (Tw,Th) (simultaneous boundaries on both axes) then
STOP
else ˜τup = cbind(τst, ˜τ) (updated matrix of estimated change points)
Let ℓ= 1 (ﬁrst hierarchical level)
while ncol(˜τup)> ncol(˜τst) do
˜τst = ˜τup
for m ∈1 : 4ℓdo
(i1,i2...,iℓ) = indexFinder(ℓ,m);
partition(i1,i2...,iℓ) = Tℓ
j=1 Qij
 ˜τΠj−1
k=1ik
xii
if |partition(i1,i2,...,iℓ)| > 0 then
˜τi1i2...iℓ=Alg.2
 partition(i1,i2,...,iℓ)

if ˜τi1i2...iℓis away from simultaneous parametric boundary on both axes then
˜τup = cbind(˜τup, ˜τi1i2...iℓ)
ℓ= ℓ+ 1 (next hierarchical level)
Output: All change points ˜τ Πj
k=1ik
, for each i1,...ik ∈{1,2,3,4} and k = 0,1,...ℓ.
REMARK 4 (On notations used in Algorithm 3).
The following shorthand notations
have been utilized in the description of Algorithm 3. First, the function ncol() represents
xiiDeﬁne ˜τ Πj
k=1ik
 = ˜τ at j = 0, i.e., the zeroth level change point estimate.
### Page 23

HD MEANS OVER 2D CHANGES
23
the number of columns of the argument matrix. The function cbind() represents a column-
wise concatenation of a matrix and a vector. Finally, the function indexFinder(ℓ,m) repre-
sents a function providing the 1 −1 mapping between the indexing 1,...,4ℓand the indexing
(i1,i2,...,iℓ), with ij = 1,2,3,4, for each j, in keeping with the ordering convention assumed
in the construction of model (3.5).
As brieﬂy mentioned earlier, Algorithm 3 is the natural extension of binary segmentation,
which is perhaps the most widely used method for estimation of multiple change points and
has well studied statistical properties at least in the ﬁxed p and 1d-change axis framework,
see, e.g., [36] and [19]. We conclude this section with a discussion on the ﬁnal generalization
(G.3) that provide an equivalence to the standard form of regression trees with the additional
complexity layer of a p-dimensional response.
REMARK 5 (On generalization (G.3)).
Model (1.1) and its ℓ-hierarchical version (3.5)
both possess sufﬁcient ﬂexibility to allow extensions to any ﬁnite number of q > 2 change
axes. For e.g., in a 3d-change point setting, all one requires is to ﬁrst consider the single
change point methodology and extend it to 3d by including another internal update in the
change point vector, i.e., all three components shall be updated component-wise while uti-
lizing the remaining two and all preliminary mean estimates as plug-in estimates into the
squared loss. Another consequence of this extension shall be to introduce octants instead
of quadrants, across which the mean parameters are allowed to be dynamic. Consequently,
the for loop of Algorithm 3 shall now be over a total of 8ℓindices. More generally, under
q-dimensional change axis this partitioning number shall inﬂate exponentially as 2q, which
is also the case in regression trees.
4. Applications.
This section considers two distinct applications of models and methods
developed in the previous sections. First we consider an application of the single 2d-change
point model (1.1) and the corresponding Algorithm 1 together with Theorem 2.3 and The-
orem 2.4. The second considers an application of the ℓ-hierarchical multiple change point
model (3.5) together with the proposed Algorithm 2 and 3 (quarterly segmentation).
4.1. Segmenting IRAS data.
The NASA mission of the Infra-Red Astronomy Satellite
(IRAS) was the ﬁrst attempt to map the sky at infra-red wavelengths. This could not be done
from ground observatories because large portions of the infrared spectrum is absorbed by the
atmosphere. This database contains observation vectors of high quality spectra, each on 44
blue band and 49 red band channels of usable ﬂux measurements (p = 93). Moreover, each
observation is made at a point in the sky associated with the equatorial celestial coordinates
system of Right Ascension (RA) and Declination (DE). These coordinates can be viewed
as the analogs of terrestrial longitude and latitude on the celestial sphere, respectively. The
DE coordinate is the angle of view above or below the celestial equator ranging from 90◦
to −90◦. The RA coordinate is measured from the sun at the march equinox (zero point
of RA) and varies between 0 to 24 hours (hr), see, https://solarsystem.nasa.
gov/basics/chapter2-2/ for further details on this coordinate system. The data set
is publicly available at the UCI repository at https://archive.ics.uci.edu/ml/
datasets/Low+Resolution+Spectrometer and consists of observations with RA
between 12hr and 24hr.
It is known that observed spectral types are associated with particular stellar types and
consequently the observed light spectrum may not be uniformly distributed across the sky in
its components. It is thus of interest to perform an unsupervised segmentation of the celestial
sphere into regions of distinct spectra. For this purpose we utilize the single 2d-change model
### Page 24

24
(1.1), the proposed Algorithm 1xiii for estimation, and Theorem 2.3 and Theorem 2.4 for
inferencexiv on location of the partitioning break.
The change axes (w,h) in the notation of model (1.1) shall be representative of the co-
ordinates RA and DE, respectively. A few data pre-processing steps are carried out prior to
implementation, chieﬂy to allow compatibility with the assumed model. Since available ob-
servations are largely clustered around the celestial equator, we limit our analysis to DE
between −50◦and 50◦. Additionally we also restrict RA to between 14h and 22h. This sub-
setting reduces the available observations to 316, and is done in order to yield observations
that are more uniformly spread over the restricted 2d-grid. The coordinate system is then
binned into a uniform grid of size 25 × 25 and the observation vector for each point on this
uniform grid is set as the sample mean of the ﬂux measurements of the 10 nearest neighbors
to each location on the uniform grid. The ﬂux data is mean centered to allow the sparsity as-
sumption as described earlier in (2.1). The binned uniform grid is then re-labeled w.r.t change
axes w = 1,...,Tw and h = 1,...,Th with Tw = Th = 25 in keeping with the construction of
model (1.1). All estimation and inference is carried out under this framework. Estimates and
conﬁdence intervals are then mapped back to the binned uniform coordinate grid to obtain
corresponding values in the RA and DE coordinates.
Upon implementation of Algorithm 1 we obtain estimated change points as (˜τw, ˜τh) =
(8,10). Mapping these break points to the uniform coordinate axes yields coordinates
(RA,DE) = (16.32hr,−12.43◦) as the 2d-partitioning change point. This change point seg-
ments the region under consideration of the celestial sphere into four sub-regions of distinct
spectral ﬂux, speciﬁcally,
Q1(˜τ) = {22hr ≥RA > 16.32hr & 50◦≥DE > −12.43◦},
Q2(˜τ) = {14hr ≤RA ≤16.32hr & 50◦≥DE > −12.43◦},
Q3(˜τ) = {14hr ≤RA ≤16.32hr & −50◦≤DE ≤−12.43◦},
and
Q4(˜τ) = {22hr ≥RA > 16.32hr & −50◦≤DE ≤−12.43◦}.
Next, we perform inference on the change parameters in accordance with Theorem 2.3 and
Theorem 2.4. We set the signiﬁcance level at α ∈{0.05,0.01}. The obtained conﬁdence
intervals are provided in Table 1. It is observed that the estimated jump size ˆξh in the DE
(or horizontal) direction is relatively larger w.r.t the estimated asymptotic variance ˆσ2
(h,∞),
thus leading to the quantile of the limiting distribution under the non-vanishing regime to be
zero at 95% coverage, in turn causing the margin of error to be zero. Thus the corresponding
interval is the single point of the estimated change. This unsupervised analysis can potentially
utilized by a researcher to pre-identify regions of interest in the sky to focus upon in order to
search for speciﬁc spectral signatures. Alternatively, one may potentially utilize this analysis
and build secondary supervised models to aid identiﬁcation of speciﬁc stellar processes.
4.2. Image processing.
A digital image comprises of Tw × Th observational units (pix-
els) where each pixel is a three dimensional vector (p = 3) of intensity of the three primary
color channels (r,g,b). These pixels can often be contaminated with noise due to a variety
of reasons and the primary goal of image denoising is to recover the underlying clean image.
The basic idea utilized in nearly all methods designed for this objective is to perform a local
averaging of pixels, this includes the total variation estimator studied in [29], where the to-
tal variation regularization is designed to locally average pixels driven by gradient changes.
xiiiThe mean regularizers λj for Step 1 and Step 2 are chosen via a BIC-type criteria, see, (5.1)
xivSee, Section 5 and Appendix D for details on all necessary additional estimations such as that of the jump
size, drifts, asymptotic variances and quantiles of limiting distributions
### Page 25

HD MEANS OVER 2D CHANGES
25
α = 0.05
α = 0.01
Vanishing
Non-Vanishing
Vanishing
Non-vanishing
Integer Scale (w)
[6.73,9.26]
[7,9]
[6.28,9.71]
[6,10]
Right Ascension
[15.99hr,16.79hr]
[16.00hr,16.65hr]
[15.85hr,16.93hr]
[15.67hr,16.98hr]
Integer Scale (h)
[9.52,10.47]
[10,10]
[9.35,10.64]
[9,11]
Declination
[−13.84◦,−10.06◦]
[−12.43◦,−12.43◦]
[−14.52◦,−9.38◦]
[−16.58◦,−8.28◦]
TABLE 1
Conﬁdence intervals under vanishing and non-vanishing regimes at 95% and 99% coverage. Intervals presented
in integer level coordinates (w,h) and corresponding RA and DE coordinates. CI’s under the vanishing jump
regime obtained by mapping integer level coordinates to RA, DE coordinates via associated quantiles.
Fundamentally our approach also pursues the same idea of local averaging, however, we in-
stead utilize model (3.5) and the proposed quarterly segmentation methodology of Algorithm
3 to perform an explicit identiﬁcation of ‘local’ pixels as identiﬁed by underlying changes in
means, in turn induced by hierarchical 2d-change points.
The ﬁrst example below are synthetic images that provide a visual proof of principle of
our methodology. Speciﬁcally, we create images with atmost one 2d simultaneous change.
Recovery of these shall illustrate the working mechanism of the regularized Algorithm 2,
which also performs selection of change parameters. The second example shall then consider
two real images.
Additional computations details: Imaging applications utilizing the raw (r,g,b) data is
p = 3 dimensional problem, i.e., high dimensionality of the response does not arise here.
Thus, soft-thresholding of (1.17) is in this case redundant. Accordingly, we utilize sample
means ¯x(ˇτ), and ¯x(ˆτ) to serve as mean estimates ˇθ and ˆθ, respectively, for Algorithm 2.
Doing so only leaves two tuning parameters γw and γh arising from Step 1 of Algorithm 2.
These tuning parameters are chosen via a BIC type criteria as follows.
BIC
 τw(γw),τh(γh)

=
4
X
j=1
X
(w,h)∈Qj(τ(γ))
x(w,h) −¯x(j)(τ(γ))
2
2
+cbic
 | ˆS| + 1[τw(γw) ̸= Tw] + 1[τh(γh) ̸= Th]

log TwTh.
(4.1)
Here ˆS = ∪4
j=1 ˆSj, with ˆSj =

k; ¯x(j)k(τ) ̸= 0
	
. When τw and τh are within parametric
boundaries then | ˆS| = 12 (each quadrant with p = 3 dim. means). The tuning parameters
γw,γh are chosen componentwise as maximizer values of (4.1), i.e., γw is chosen as the value
such that ˆτ(γw) maximizes BIC(ˆτw(γw), ˇτh) and symmetrically for ˆτh. The constant cbic is
introduced to allow for additional control on the tuning process, with the classical BIC criteria
requiring cbic = 1. The ﬁnite and discrete nature of the optimization of Step 1 of Algorithm
2 provides a signiﬁcant simpliﬁcation. Here tuning with BIC criteria (4.1) is equivalent to
choosing γw and γh of Algorithm 2 as γw = γh = 7cbic(log TwTh)

(TwTh). This can be
observed by noting that when τw is at the parametric boundary, the quadrants Q1(τ) and
Q4(τ) are empty sets, consequently the underlying degrees of freedom in this case is 7 (3+3
for mean, 1 for the height parameter), analogously when τw is within the parametric boundary
the degrees of freedom is 14. Symmetrically for the height change parameter.
EXAMPLE 1 (Synthetic images).
To provide a visual proof of principle, we construct
synthetic images under the following cases. I(a) Simultaneous change in both horizontal and
vertical directions, I(b) change in only the horizontal direction I(c) change in only the vertical
direction, and I(d) no change in either direction. The construction in all four cases of (I) is in
direct equivalence to the model (1.1), with the relaxation of boundary valued change points
### Page 26

26
FIG 5. Image denoising with Algorithm 3. Image is 50 × 50 pixels with one 2d-change point. Left panel: True im-
age (unobserved), Center panel: Noisy image (observed), Right panel: Recovered image. Change point estimated
as ˜τ = (14,18)T . Noise set to Σ = I3×3, and tuning constant cbic = 1.
FIG 6. Image denoising with Algorithm 3. Image is 250×200 pixels with multiple hierarchical 2d-change points.
Left panel: True images (unobserved), Center panel: Noisy images (observed), Right panel: Recovered image.
Estimated model recovered with ℓ= 5 hierarchical change points inducing a total of 32 disjoint partitions of the
sampling space. Noise set to Σ = I3×3, and tuning constant cbic = 1.
as discussed in Remark 2. (II) Additional images are constructed with multiple hierarchical
change points as described by model (3.5). Algorithm 3 is implemented in all cases to esti-
mate the underlying 2d-transition and in turn the induced disjoint partitions. A clean image
is recovered by replacing each pixel with the sample mean of the partition in which it lies.
The true, noisy and the recovered images are illustrated in Figure 5 for case I(a) and Fig-
ure 6 for case (II). All remaining cases are provided in Figure 9 and Figure 10 in Appendix
D. The results of these cases are visually self explanatory. The proposed method success-
fully estimates transition points as well as boundary valued cases and consequently recovers
underlying images in all cases, despite a signiﬁcant amount of noise.
EXAMPLE 2 (Real images).
In this example we considered two real images. First is
an image of Lena which has traditionally been utilized as a benchmark example for image
denoising techniques. A second image of Charlie Chaplin has also been considered. The ℓ-
hierarchical change model (3.5) and proposed Algorithm 3 is utilized to ﬁt the observed p = 3
dimensional realizations (pixels) of each considered image. A large number of disjoint par-
titions are expected in any realistic image. Consequently, the noise added to these images is
set lower in comparison to the previous example. i.e., we set Σ = 0.05·I3×3. Implementation
is performed for three cases of the tuning constant cbic ∈{0.25,0.5,1}.
Figure 7 provides the true, noisy and recovered images for the Lena image with cbic =
0.25. Figure 8 provides these images for the Charlie Chaplin image with cbic = 0.5. The
remaining cases are provided in Figure 11 and Figure 12.
To conclude this sub-section we mention that denoising is perhaps the simplest applica-
tion of the proposed model and methods. The segmenting process being carried out prior to
### Page 27

HD MEANS OVER 2D CHANGES
27
FIG 7. Image denoising with Algorithm 3. Image is 600 × 400 pixels. Left panel: True image (unobserved),
Center panel: Noisy image (observed), Right panel: Recovered image. Estimated model recovered with ℓ= 13
hierarchical change points inducing a total of 7254 disjoint partitions of the sampling space. Noise set to Σ =
0.05·I3×3, and tuning constant cbic = 0.25.
FIG 8. Image denoising with Algorithm 3. Image is 600 × 600 pixels. Left panel: True image (unobserved),
Center panel: Noisy image (observed), Right panel: Recovered image. Estimated model recovered with ℓ= 13
hierarchical change points inducing a total of 4201 disjoint partitions of the sampling space. Noise set to Σ =
0.05·I3×3, and tuning constant cbic = 0.5.
denoising is of a much larger consequence, in particular, this segmentation layer produced
by the proposed methodology has several other potential applications such as that of object
identiﬁcation via a secondary layer of supervised model(s).
5. Numerical experiments.
This section considers the single 2d-change model (1.1)
and provides numerical support to the proposed estimation method of Algorithm 1 and the
inference results of Theorem 2.3 and Theorem 2.4. In all simulations to follow, no under-
lying parameter is assumed to be known. We begin with a description of the simulation de-
sign. In all cases considered, the mean vectors are set as θ0
(1) = θ0
(3) =
 θT
s×1,0...,0
T
p×1,
where θ = (0.75,...,0.25)s×1, contains evenly spaced s = 5 entries. The remaining two
means are set to zero, i.e., θ0
(2) = θ0
(4) = 0p×1. The covariance matrix Σ is chosen to be
a toeplitz type matrix deﬁned as Σij = ρ|i−j|, i,j = 1,...,p and ρ = 0.5. We consider
all combinations of the sampling periods Tw,Th ∈{30,35,40,45}, model dimension p ∈
{10,50,100,250}. The 2d-change point τ 0 = (τ 0
w,τ 0
h)T chosen as all combinations of τ 0
w ∈∈

⌊0.2·Tw⌋,⌊0.4·Tw⌋,⌊0.6·Tw⌋,⌊0.8·Tw⌋
	
and τ 0
h ∈∈

⌊0.2·Th⌋,⌊0.4·Th⌋,⌊0.6·Th⌋,⌊0.8·Th⌋
	
.
The unobserved noise variables ε(w,h) ∈Rp are generated as i.i.d. Gaussian r.v.’s, more pre-
cisely we set ε(w,h) ∼i.i.d N(0,Σ), w = 1,...,Tw, h = 1,...,Th.
We construct conﬁdence intervals using both the limiting distributions of Theorem 2.3 and
Theorem 2.4. The signiﬁcance level is set to α = 0.05. Conﬁdence intervals are constructed
component-wise, i.e., for the width change parameter as,

(˜τw −MEw), (˜τw + MEw)

,
### Page 28

28
where ˜τw is the width component of the output of Algorithm 1.The margin of error (MEw)
is computed as MEw = qv
ασ2
(w,∞)
 Thξ2
w

or ME = qnv
α based on the results of Theorem
2.3 and Theorem 2.4, respectively. Here qv
α represents the
 1−α/2
th quantile of the argmax
of two sided negative drift Brownian motion of Theorem 2.3. This critical value is evaluated
as cα = 11.03 by using its distribution function provided in [44]. The
 1 −α/2
th quantile
qnv
α of the argmax of the two sided negative drift random walk is computed as its monte carlo
approximation by simulating 4000 realizations of this distribution. As per the assumed data
generating process, the distribution P here is Gaussian. For implementation of the conﬁdence
interval, we utilize plugin estimates of σ2
(w,∞) and ξ2
w, whose computational details of which
are provided in Appendix D of the supplementary materials. Symmetrical computations are
carried out for the height change parameter τh.
Choice of tuning parameters: The regularizers λj, j = 1,2,3,4 used to obtain soft thresh-
olded mean estimates in Step 1 and Step 2 of Algorithm 1 are tuned via a BIC type criteria.
Speciﬁcally we set λj = λ, j = 1,2,3,4, and evaluate ˆθ(j)(λ), j = 1,2,3,4 over an equally
spaced grid of twenty ﬁve values in the interval (0,0.5). Upon letting ˆS =

k;
∪4
j=1ˆθ(j)k ̸=
0} we evaluate the criteria,
BIC(λ,τw,τh) =
4
X
j=1
X
(w,h)∈Qj(τ)
x(w,h) −ˆθ(j)(λ)
2
2 + | ˆS|log TwTh.
(5.1)
For Step 1 of Algorithm 1 we set λ as the minimizer of BIC(λ, ˇτw, ˇτh), and for Step 2 of
Algorithm 1 we choose λ as the minimizer of BIC(λ, ˆτw, ˆτh).
To present our results we report the following metrics, bias (|E(ˆτw −τ 0
w)|) and root mean
squared error (E1/2(ˆτw −τ 0
w)2) measure estimation performance. Coverage (relative fre-
quency of the number of times τ 0
w lies in the conﬁdence interval), and the average margin
of error (average over replications of the margin of error of each conﬁdence interval) mea-
sure inference performance. Symmetrical metrics are also presented w.r.t the height change
parameter τh. All approximations are made based on 500 monte carlo replications. Partial
results regarding estimation of the width change parameter are provided in Tables 2 - Table
5. Corresponding results for the height change parameter are provided in Table 6 - Table 9 in
Appendix D of the Supplement.
Change point estimates in both directions are largely observed to exhibit little bias with an
expected deterioration with larger dimension sizes p. The proposed inference methodology
is observed to provide good control on the nominal signiﬁcance level if one provides a slight
leeway given the discrete nature of the underlying problem and conﬁdence intervals. The
cases where coverage is observed to be signiﬁcantly away from nominal are again the larger
values of p, or where change points are near the parametric boundary (see, Table 3, case:
p = 250, τ 0 = 0.8). It can be observed that this deviation from nominal coverage is primarily
due to bias in estimation and not the computation of margin of error (the margin of error as
expected remains stable for all values of Tw). Importantly, bias is observed to diminish and
coverage to catchup to nominal as the effective sample size of TwThω increases, i.e., when
the sampling periods increase or the change point move away from parametric boundaries.
6. Discussion.
Regression trees are amongst the most heavily utilized and perhaps the
least analytically understood modelling techniques. We illustrate that viewing regression
trees via multidimensional change points provides an analytically tractable construction
which allows for a multivariate response, and more importantly allows for fundamental sta-
tistical properties of rates of estimation and limiting distributions to be established, despite
potential high dimensionality. The purpose of this article is only to make ﬁrst inroads into
### Page 29

HD MEANS OVER 2D CHANGES
29
Th = 30,
τ0
h/Th = 0.2
p = 10
p = 50
bias (rmse)
coverage (av. ME)
bias (rmse)
coverage (av. ME)
τ0w/Tw
Tw
Vanishing
Non-Vanishing
Vanishing
Non-Vanishing
0.2
30
0.008 (0.155)
0.976 (0.468)
0.978 (0.018)
0.01 (0.148)
0.978 (0.394)
0.978 (0)
0.2
35
0.02 (0.2)
0.96 (0.508)
0.966 (0.04)
0.022 (0.195)
0.968 (0.401)
0.968 (0)
0.2
40
0.016 (0.21)
0.962 (0.514)
0.964 (0.032)
0.02 (0.2)
0.96 (0.409)
0.96 (0)
0.2
45
0.032 (0.253)
0.958 (0.516)
0.96 (0.02)
0.006 (0.214)
0.972 (0.418)
0.972 (0)
0.4
30
0.02 (0.228)
0.954 (0.476)
0.956 (0.02)
0.034 (0.344)
0.964 (0.471)
0.964 (0.004)
0.4
35
0.028 (0.268)
0.958 (0.522)
0.958 (0.02)
0.064 (0.477)
0.954 (0.472)
0.954 (0.002)
0.4
40
0.006 (0.224)
0.966 (0.528)
0.968 (0.018)
0.05 (0.293)
0.962 (0.48)
0.962 (0.002)
0.4
45
0.02 (0.228)
0.96 (0.523)
0.964 (0.012)
0.008 (0.141)
0.98 (0.482)
0.982 (0.004)
0.6
30
0.06 (0.358)
0.948 (0.495)
0.95 (0.028)
0.078 (0.361)
0.936 (0.504)
0.938 (0.014)
0.6
35
0.008 (0.245)
0.97 (0.522)
0.972 (0.02)
0.056 (0.303)
0.954 (0.501)
0.954 (0.008)
0.6
40
0.006 (0.265)
0.958 (0.533)
0.96 (0.026)
0.054 (0.326)
0.946 (0.507)
0.946 (0.004)
0.6
45
0.034 (0.224)
0.962 (0.535)
0.966 (0.02)
0.048 (0.228)
0.948 (0.515)
0.952 (0.01)
0.8
30
0.118 (0.882)
0.944 (0.529)
0.948 (0.064)
0.212 (0.976)
0.876 (0.474)
0.886 (0.036)
0.8
35
0.036 (0.237)
0.968 (0.521)
0.974 (0.054)
0.13 (0.65)
0.916 (0.475)
0.916 (0.014)
0.8
40
0.024 (0.179)
0.97 (0.513)
0.972 (0.022)
0.092 (0.42)
0.932 (0.488)
0.932 (0.012)
0.8
45
0.046 (0.265)
0.958 (0.519)
0.966 (0.034)
0.066 (0.319)
0.938 (0.488)
0.94 (0.006)
TABLE 2
Simulation results for estimation of τ0w based on 500 replications. All reported metrics rounded to three
decimals. Other data generating parameters: Th = 30, τ0
h = ⌊0.2·Th⌋and p ∈{10,50}.
Th = 30,
τ0
h/Th = 0.2
p = 100
p = 250
bias (rmse)
coverage (av. ME)
bias (rmse)
coverage (av. ME)
τ0w/Tw
Tw
Vanishing
Non-Vanishing
Vanishing
Non-Vanishing
0.2
30
0.032 (0.738)
0.966 (0.352)
0.966 (0.002)
0.024 (0.74)
0.968 (0.306)
0.968 (0.002)
0.2
35
0.016 (0.167)
0.972 (0.362)
0.972 (0)
0.008 (0.19)
0.964 (0.325)
0.964 (0)
0.2
40
0.008 (0.167)
0.972 (0.375)
0.972 (0)
0.01 (0.173)
0.97 (0.342)
0.97 (0)
0.2
45
0.026 (0.173)
0.97 (0.381)
0.97 (0)
0.01 (0.615)
0.964 (0.35)
0.964 (0.002)
0.4
30
0.048 (0.29)
0.952 (0.457)
0.952 (0.002)
0.104 (0.544)
0.938 (0.438)
0.938 (0)
0.4
35
0.04 (0.303)
0.962 (0.463)
0.962 (0)
0.086 (0.546)
0.932 (0.451)
0.932 (0)
0.4
40
0.038 (0.224)
0.95 (0.47)
0.95 (0)
0.044 (0.261)
0.956 (0.455)
0.956 (0)
0.4
45
0.024 (0.245)
0.962 (0.481)
0.962 (0)
0.028 (0.228)
0.97 (0.463)
0.97 (0.002)
0.6
30
0.142 (0.801)
0.922 (0.49)
0.922 (0.01)
0.122 (0.852)
0.928 (0.467)
0.93 (0.01)
0.6
35
0.068 (0.346)
0.94 (0.491)
0.94 (0)
0.114 (0.68)
0.934 (0.481)
0.934 (0.008)
0.6
40
0.068 (0.696)
0.954 (0.498)
0.954 (0.004)
0.072 (0.369)
0.942 (0.485)
0.942 (0.004)
0.6
45
0.046 (0.272)
0.958 (0.505)
0.96 (0.004)
0.066 (0.387)
0.948 (0.49)
0.954 (0.008)
0.8
30
0.276 (1.31)
0.856 (0.444)
0.858 (0.022)
0.568 (2.416)
0.776 (0.424)
0.78 (0.034)
0.8
35
0.12 (0.639)
0.928 (0.456)
0.93 (0.01)
0.27 (0.838)
0.82 (0.433)
0.82 (0.018)
0.8
40
0.176 (0.699)
0.884 (0.468)
0.892 (0.018)
0.168 (0.593)
0.88 (0.431)
0.882 (0.01)
0.8
45
0.094 (0.377)
0.928 (0.466)
0.928 (0.006)
0.294 (1.599)
0.866 (0.445)
0.866 (0.014)
TABLE 3
Simulation results for estimation of τ0w based on 500 replications. All reported metrics rounded to three
decimals. Other data generating parameters: Th = 30, τ0
h = ⌊0.2·Th⌋and p ∈{100,250}.
this connection. Clearly there is a rich body of further questions that need analytical ad-
dressal particularly in Section 3 above, these are however beyond the scope of this article.
Moreover, solutions to these questions still require considerable development of the change
point literature at a more fundamental level of one dimensional change points, particularly in
context of inference.
### Page 30

30
Th = 30,
τ0
h/Th = 0.4
p = 10
p = 50
bias (rmse)
coverage (av. ME)
bias (rmse)
coverage (av. ME)
τ0w/Tw
Tw
Vanishing
Non-Vanishing
Vanishing
Non-Vanishing
0.2
30
0.028 (0.219)
0.958 (0.464)
0.962 (0.028)
0.106 (1.093)
0.954 (0.421)
0.954 (0.02)
0.2
35
0.056 (0.303)
0.936 (0.517)
0.948 (0.048)
0.054 (0.88)
0.964 (0.443)
0.964 (0.012)
0.2
40
0.02 (0.19)
0.97 (0.512)
0.972 (0.03)
0.008 (0.155)
0.976 (0.441)
0.976 (0.004)
0.2
45
0.028 (0.237)
0.956 (0.519)
0.958 (0.036)
0.004 (0.19)
0.964 (0.442)
0.964 (0)
0.4
30
0.002 (0.279)
0.964 (0.467)
0.964 (0.022)
0.02 (0.219)
0.968 (0.443)
0.968 (0.006)
0.4
35
0.01 (0.272)
0.96 (0.524)
0.96 (0.03)
0.002 (0.195)
0.968 (0.445)
0.968 (0.004)
0.4
40
0.01 (0.214)
0.96 (0.534)
0.962 (0.032)
0.002 (0.161)
0.974 (0.456)
0.974 (0.004)
0.4
45
0.014 (0.272)
0.964 (0.531)
0.964 (0.016)
0.014 (0.184)
0.966 (0.459)
0.966 (0.002)
0.6
30
0.026 (0.205)
0.964 (0.471)
0.964 (0.012)
0.04 (0.522)
0.968 (0.474)
0.97 (0.012)
0.6
35
0.022 (0.326)
0.948 (0.523)
0.952 (0.024)
0.016 (0.179)
0.974 (0.466)
0.974 (0.006)
0.6
40
0.022 (0.232)
0.968 (0.521)
0.97 (0.01)
0.018 (0.195)
0.968 (0.476)
0.968 (0.004)
0.6
45
0.008 (0.21)
0.962 (0.529)
0.966 (0.016)
0.01 (0.184)
0.966 (0.49)
0.968 (0.006)
0.8
30
0.028 (0.261)
0.95 (0.486)
0.952 (0.034)
0.146 (1.15)
0.926 (0.46)
0.926 (0.016)
0.8
35
0.028 (0.253)
0.954 (0.505)
0.96 (0.034)
0.076 (0.927)
0.956 (0.465)
0.956 (0.008)
0.8
40
0.022 (0.224)
0.968 (0.519)
0.972 (0.042)
0.028 (0.19)
0.964 (0.472)
0.966 (0.004)
0.8
45
0.048 (0.253)
0.948 (0.523)
0.956 (0.036)
0.038 (0.3)
0.962 (0.475)
0.962 (0.006)
TABLE 4
Simulation results for estimation of τ0w based on 500 replications. All reported metrics rounded to three
decimals. Other data generating parameters: Th = 30, τ0
h = ⌊0.4·Th⌋and p ∈{10,50}.
Th = 30,
τ0
h/Th = 0.4
p = 100
p = 250
bias (rmse)
coverage (av. ME)
bias (rmse)
coverage (av. ME)
τ0w/Tw
Tw
Vanishing
Non-Vanishing
Vanishing
Non-Vanishing
0.2
30
0.09 (1.122)
0.968 (0.4)
0.968 (0.008)
0.076 (0.908)
0.966 (0.357)
0.966 (0.008)
0.2
35
0.03 (0.488)
0.966 (0.412)
0.966 (0.004)
0.008 (0.179)
0.968 (0.367)
0.968 (0)
0.2
40
0.01 (0.195)
0.962 (0.418)
0.962 (0)
0.046 (0.866)
0.97 (0.387)
0.97 (0.006)
0.2
45
0.006 (0.161)
0.974 (0.425)
0.974 (0)
0.014 (0.173)
0.976 (0.397)
0.976 (0)
0.4
30
0.002 (0.224)
0.956 (0.438)
0.962 (0.008)
0.008 (0.2)
0.966 (0.421)
0.966 (0.008)
0.4
35
0.032 (0.316)
0.976 (0.434)
0.976 (0.002)
0.03 (0.392)
0.97 (0.432)
0.97 (0)
0.4
40
0.01 (0.205)
0.97 (0.438)
0.97 (0)
0.002 (0.214)
0.96 (0.437)
0.96 (0.002)
0.4
45
0.01 (0.148)
0.978 (0.441)
0.978 (0)
0.004 (0.11)
0.988 (0.445)
0.988 (0)
0.6
30
0.018 (0.173)
0.97 (0.459)
0.97 (0.004)
0.014 (0.173)
0.976 (0.46)
0.976 (0)
0.6
35
0.038 (0.605)
0.97 (0.471)
0.97 (0.004)
0.018 (0.195)
0.968 (0.479)
0.968 (0.004)
0.6
40
0.006 (0.118)
0.986 (0.482)
0.986 (0.002)
0.006 (0.148)
0.978 (0.475)
0.978 (0)
0.6
45
0.022 (0.232)
0.958 (0.484)
0.96 (0.004)
0.002 (0.184)
0.978 (0.487)
0.978 (0)
0.8
30
0.14 (1.103)
0.94 (0.434)
0.942 (0.01)
0.138 (1.127)
0.94 (0.403)
0.94 (0.016)
0.8
35
0.052 (0.486)
0.954 (0.437)
0.954 (0.002)
0.06 (0.54)
0.954 (0.417)
0.954 (0.004)
0.8
40
0.034 (0.214)
0.96 (0.45)
0.96 (0)
0.04 (0.253)
0.954 (0.426)
0.954 (0.004)
0.8
45
0.052 (1.083)
0.978 (0.463)
0.978 (0.002)
0.02 (0.2)
0.966 (0.433)
0.966 (0)
TABLE 5
Simulation results for estimation of τ0w based on 500 replications. All reported metrics rounded to three
decimals. Other data generating parameters: Th = 30, τ0
h = ⌊0.4·Th⌋and p ∈{100,250}.
### Page 31

HD MEANS OVER 2D CHANGES
1
Supplementary Materials.
SEGMENTATION OF HIGH DIMENSIONAL MEANS OVER
MULTI-DIMENSIONAL CHANGE POINTS AND CONNECTIONS TO
REGRESSION TREES
APPENDIX A: PROOFS OF RESULTS IN SECTION 2
To present the arguments of this section we require additional notation. In all to follow
let ˆη(j) represent estimates of the jump parameters η0
(j), j = 1,2,3,4 respectively. For any
non-negative sequences 0 ≤vTw ≤uTw ≤1, in Tw and 0 ≤vTh ≤uTh ≤1, in Th, deﬁne the
following collections,
Gw(uTw,vTw) =
n
τw ∈{1,2,...,Tw}; TwvTw ≤|τw −τ 0
w| ≤TwuTw
o
, and
Gh(uTh,vTh) =
n
τh ∈{1,2,...,Th}; ThvTh ≤|τh −τ 0
h| ≤ThuTh
o
.
Finally, we deﬁne,
Uw(τw,τh,θ) = TwTh

L(τw,τh,θ) −L(τ 0
w,τh,θ)

, and
Uh(τw,τh,θ) = TwTh

L(τw,τh,θ) −L(τw,τ 0
h,θ)

,
where L(·,·,·) is the squared loss deﬁned in (1.2). Clearly, the plug-in estimates ˜τw(ˆτh, ˆθ)
and ˜τh(ˆτw, ˆθ) of (1.3) can then equivalently be written as,
˜τw(ˆτh, ˆθ) = arg min
1≤τw<Tw
Uw(τw, ˆτh, ˆθ),
and
˜τh(ˆτw, ˆθ) = arg min
1≤τh<Th
Uh(ˆτw,τh, ˆθ)
(A.1)
The change of representation of estimates to (A.1) is made solely for notational convenience
in the proofs to follow. We begin this section with Lemma A.1-A.4, which are all closely
related. These lemma’s shall serve as critical tools that upon which our arguments for Theo-
rem 2.1 and Theorem 2.2 rely. Lemma A.1 and Lemma A.2 shall serve towards the argument
for the near optimal rate of Theorem 2.1 for the estimates ˜τw, and ˜τh, respectively. Lemma
A.3 and Lemma A.4 shall sever towards Theorem 2.2 for ˜τw, and ˜τh, respectively. All four
of lemma’s provide uniform lower bounds over the collections Gw and Gh, under different
conditions of preliminary nuisance estimates.
LEMMA A.1.
Suppose the model (1.1) and assume that Condition A, B, C(i)(a) and
C(ii)(a,b) hold. Let 0 ≤vTw ≤uTw ≤1, be any non-negative sequences. Then,
inf
τw∈Gw(uTw,vTw)Uw(τw, ˆτh, ˆθ) ≥TwThξ2
w
2
h
vTw −cu log(p ∨TwTh) σ
ξw
n suTw
TwTh
o 1
2 i
(A.2)
with probability at least 1 −2exp{−c1 log(p ∨T)} −πT , for constant c1 > 0 that does not
depend on any model parameters.
Proof of Lemma A.1. The proof of this result is fairly long and is thus broken up into the
following three steps for the convenience of the reader.
Step 1 Utilize Condition B, Condition C and results of Appendix B to obtain upper and
lower bounds on some stochastic quantities of interest.
Step 2 Perform an algebraic decomposition of Uw(τw, ˆτh, ˆθ) to obtain a manageable expres-
sion in terms of jump sizes (1.5) and additional noise terms.
### Page 32

2
Step 3 Apply bounds of Step 1 to expression of Step 2 to obtain the desired uniform lower
bound of the statement of this lemma.
We begin with Step 1 that provides a few observations that shall be required to obtain the
desired lower bound. Using Condition C(ii)(a,b) we have the following relations,
∥ˆη(1) −η0
(1)∥2 ≤∥ˆθ(1) −θ0
(1)∥2 + ∥ˆθ(2) −θ0
(2)∥2 ≤2cu1ξmin
and similarly,
∥ˆη(1) −η0
(1)∥1 ≤4√s∥ˆθ(1) −θ0
(1)∥2 + 4√s∥ˆθ(2) −θ0
(2)∥2 ≤8cu1
√sξmin
(A.3)
with probability at least 1 −πT . Here the third inequality follows from Condition C(ii)(a).
Next, consider,
∥ˆη(1)∥2 ≤∥ˆη(1) −η0
(1)∥2 + ∥η0
(1)∥2 ≤ξ1 + 2u1ξmin ≤cuξmin,
and similarly,
∥ˆη(1)∥1 ≤∥ˆη(1) −η0∥1 + ∥η0
(1)∥1 ≤8cu1
√sξmin + √sξ1 ≤cu
√sξmin,
(A.4)
which holds with probability at least 1 −πT . Here the second inequality for the ℓ2 bound
follows from (A.3) and the third follows from Condition B(ii). The ℓ1 bound follows analo-
gously. Expression (A.4) provides an upper bound for ∥ˆη(1)∥2 that holds with probability at
least 1 −πT , below we show that this quantity can also be bounded from below. Consider,
∥ˆη(1)∥2
2 = ∥η0
(1) + (ˆη(1) −η0
(1))∥2
2 ≥∥η0
(1)∥2
2 + 2(ˆη(1) −η0
(1))T η0
(1)
≥ξ2
1 −2∥ˆη(1) −η0
(1)∥2ξ1 ≥ξ2
1 −2cu1ξminξ
(A.5)
with probability at least 1 −πT . Here the second inequality follows by an application of the
Cauchy-Schwarz inequality. The ﬁnal inequality follows from (A.3). Analogous arguments
can be utilized to obtain versions of the above bounds for ∥ˆη(3)∥2, speciﬁcally,
∥ˆη(3) −η0
(3)∥2 ≤2cu1ξmin,
∥ˆη(3) −η0
(3)∥1 ≤8cu1
√sξmin,
(A.6)
∥ˆη(3)∥2 ≤cuξmin,
∥ˆη(3)∥1 ≤cu
√sξmin,
and
∥ˆη(3)∥2
2 ≥ξ2
3 −2cu1ξminξ
with probability 1 −πT . Additional residual terms that shall require control are as follows,
2ωh(ˆθ(1) −θ0
(1))T ˆη(1) + 2(1 −ωh)(ˆθ(4) −θ0
(4))T ˆη(3)
−2(ˆτh −τ 0
h)
Th
(ˆθ(1) −θ0
(1))T ˆη(1) + 2(ˆτh −τ 0
h)
Th
(ˆθ(4) −θ0
(1))T ˆη(3)
+(ˆτh −τ 0
h)
Th
∥ˆη(3)∥2
2 −(ˆτh −τ 0
h)
Th
∥ˆη(1)∥2
2
≤2∥ˆθ(1) −θ0
(1)∥2∥ˆη(1)∥2 + 2∥ˆθ(4) −θ0
(4)∥2∥ˆη(3)∥2
+2|ˆτh −τ 0
h|
Th
∥ˆθ(1) −θ0
(1)∥2∥ˆη(1)∥2 + 2|ˆτh −τ 0
h|
Th
∥ˆθ(4) −θ0
(1)∥2∥ˆη(3)∥2
+|ˆτh −τ 0
h|
Th
∥ˆη(3)∥2
2 + |ˆτh −τ 0
h|
Th
∥ˆη(1)∥2
2
≤cu1ξ2
min + cu1ξξmin
(A.7)
with probability at least 1 −πT . Here the ﬁrst inequality follows from several applications of
the Cauchy-Schwarz inequality. The second inequality follows by utilizing Condition C(i)(a),
C(ii)(b) as well as (A.4). Here we have also utilized the triangle inequality ∥ˆθ(4) −θ0
(1)∥≤
∥ˆθ(4) −θ0
(4)∥+∥η0
(4)∥. The above inequalities provide bounds on terms where the randomness
### Page 33

HD MEANS OVER 2D CHANGES
3
is induced solely due to the plug-in preliminary estimates ˆτh and ˆθ. The following provides
upper bounds on stochastic terms where randomness is induced via the noise terms ε′
(w,h)s.
These shall follow mainly as a consequence of results of Appendix B. Consider,
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w

τw
X
w=τ 0
w+1
Th
X
h=τ 0
h+1
εT
(w,h)ˆη(1)
 ≤
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w

τw
X
w=τ 0
w+1
Th
X
h=τ 0
h+1
ε(w,h)

∞∥ˆη(1)∥1
≤cuξminσ log(p ∨TwTh)√(TwThuTw)√s
(A.8)
with probability at least 1−2exp{c1 log(p∨TwTh)}−πT , for some c1 > 0. Here the second
inequality follows from Lemma B.1 and (A.4). The same argument also yields the same
uniform bounds on other similar residual terms,
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w

τw
X
w=τ 0
w+1
τ 0
h
X
h=1
εT
(w,h)ˆη(3)
 ≤cuξminσ log(p ∨TwTh)√(TwThuTw)√s
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w

τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)ˆη(1)
 ≤cuξminσ log(p ∨TwTh)√(TwThuTw)√s
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w

τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)ˆη(3)
 ≤cuξminσ log(p ∨TwTh)√(TwThuTw)√s
(A.9)
with probability at least 1 −2exp{c1 log(p ∨TwTh)} −πT . Here we have also utilized Con-
dition C(i)(a) which provides |ˆτh −τ 0
h| ≤cu1Th, w.p. 1 −πT . These bounds complete Step
1 of our argument and provide the necessary groundwork to proceed to the next step.
Step 2: We shall prove the statement of this lemma for the case τw ≥τ 0
w and ˆτh ≥τ 0
h. The
remaining three permutations of the ordering of τw ≤τ 0
w and ˆτh ≥τ 0
h, or τw ≥τ 0
w and ˆτh ≤
τ 0
h, or τw ≤τ 0
w and ˆτh ≤τ 0
h shall follow symmetrical arguments. Consider,
Uw(τw, ˆτh, ˆθ) = L(τw, ˆτh, ˆθ) −L(τ 0
w, ˆτh, ˆθ)
=
Tw
X
w=τw+1
Th
X
h=ˆτh+1
∥x(w,h) −ˆθ(1)∥2
2 +
τw
X
w=1
Th
X
h=ˆτh+1
∥x(w,h) −ˆθ(2)∥2
2
+
τw
X
w=1
ˆτh
X
h=1
∥x(w,h) −ˆθ(3)∥2
2 +
Tw
X
w=τw+1
ˆτh
X
h=1
∥x(w,h) −ˆθ(4)∥2
2
−
Tw
X
w=τ 0
w+1
Th
X
h=ˆτh+1
∥x(w,h) −ˆθ(1)∥2
2 −
τ 0
w
X
w=1
T
X
h=ˆτh+1
∥x(w,h) −ˆθ(2)∥2
2
−
τ 0
w
X
w=1
ˆτh
X
h=1
∥x(w,h) −ˆθ(3)∥2
2 −
T
X
w=τ 0
w+1
ˆτh
X
h=1
∥x(w,h) −ˆθ(4)∥2
2
(A.10)
An algebraic manipulation of (A.10) yields the following expression.
Uw(τw, ˆτh, ˆθ) = (τw −τ 0
w)
"
(Th −τ 0
h)
n
∥ˆη(1)∥2
2 + 2(ˆθ(1) −θ0
(1))T ˆη(1)
o
### Page 34

4
+τ 0
h
n
∥ˆη(3)∥2
2 + 2(ˆθ(4) −θ0
(4))T ˆη(3)
o#
+(τw −τ 0
w)(ˆτh −τ 0
h)
"
∥ˆη(3)∥2
2 −∥ˆη(1)∥2
2
−2(ˆθ(1) −θ0
(1))T ˆη(1) + 2(ˆθ(4) −θ0
(1))T ˆη(3)
#
−2
τw
X
w=τ 0
w+1
Th
X
h=τ 0
h+1
εT
(w,h)ˆη(1) −2
τw
X
w=τ 0
w+1
τ 0
h
X
h=1
εT
(w,h)ˆη(3)
+2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)ˆη(1) −2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)ˆη(3)
(A.11)
The calculations yielding (A.11) from the deﬁning equality (A.10) are fairly tedious and in
order to maintain continuity of the main argument of this lemma, these algebraic manipula-
tions are presented as Remark 6 after the proof of this lemma. We can now proceed to the ﬁnal
step of the argument where we shall apply the bounds obtained in Step 1 to the expression
(A.11) in order to obtain the desired uniform lower bound.
Step 3: It shall be important in this step to recall that all constants in Step 1 above represented
by cu1 arise from the Condition C, where it is assumed as chosen to be suitably small enough.
Now recalling the construction of the set Gw(uTw,vTw) from (A.1) and applying the bounds
(A.4), (A.6), (A.7), (A.8) and (A.9) to the expression (A.11) we obtain,
inf
τw∈Gw(uTw,vTw);
τw≥τ 0
w
Uw(τw, ˆτh, ˆθ) ≥TwThvTw
h
ωhξ2
1 + (1 −ωh)ξ2
3 −cu1ξminξ −cu1ξ2
min
i
−cuξminσ log(p ∨TwTh)√(TwThuTw)√s
≥TwThξ2
w
2
h
vTw −cu log(p ∨TwTh) σ
ξw
 suTw
TwTh
 1
2 i
(A.12)
with probability at least 1 −2exp{c1 log(p ∨TwTh)} −πT . To obtain the second inequality
we have used that by deﬁnition ωhξ2
1 + (1 −ωh)ξ2
3 = ξ2
w, and ξmin ≤ξw, additionally from
Condition B(ii) we have ξ ≤cuξmin and that the constant cu1 arises from Condition C where
it is chosen to be suitable small enough. Repeating symmetrical arguments for the mirroring
permutations of the ordering of τw,τh with respect to τ 0
w, ˆτh shall yield the same uniform
lower bound (A.12). This completes the proof of this lemma.
REMARK 6.
This remark provides the decomposition (A.11) of (A.10) described in Step
2 of the proof of Lemma A.1. A note of interest here is that the calculations below become
much more intuitive when viewed w.r.t. to a 2d-visualization such as that illustrated in (1.1).
Let,
ˆε(w,h) =
(
x(w,h) −ˆθ(1)
τ 0
w < w ≤τw, ˆτh < h ≤T
x(w,h) −ˆθ(4)
τ 0
w < w ≤τw, 1 ≤h < ˆτh
### Page 35

HD MEANS OVER 2D CHANGES
5
Then picking up from the expression (A.10), a simpliﬁcation now yields,
U(τw, ˆτh, ˆθ) = −
τw
X
w=τ 0
w+1
T
X
h=ˆτh+1
∥x(w,h) −ˆθ(1)∥2
2 +
τh
X
w=τ 0
w+1
T
X
ˆτh+1
∥x(w,h) −ˆθ(2)∥2
2
+
τw
X
w=τ 0
w+1
ˆτh
X
h=1
∥x(w,h) −ˆθ(3)∥2
2 −
τw
X
w=τ 0
w+1
ˆτh
X
h=1
∥x(w,h) −ˆθ(4)∥2
2
=
τw
X
w=τ 0
w+1
T
X
h=ˆτh+1
∥ˆθ(2) −ˆθ(1)∥2
2 −2
τw
X
w=τ 0
w+1
T
X
h=ˆτh+1
ˆεT
(w,h)(ˆθ(2) −ˆθ(1))
+
τw
X
w=τ 0
w+1
ˆτh
X
h=1
∥ˆθ(3) −ˆθ(4)∥2
2 −2
τw
X
w=τ 0
w+1
ˆτh
X
h=1
ˆεT
(w,h)(ˆθ(3) −ˆθ(4))
= R1 −R2 + R3 −R4.
(A.13)
Next we consider these remainder terms R1, and R3, where we have,
R1 + R3 =
τw
X
w=τ 0
w+1
T
X
h=ˆτh+1
∥ˆθ(2) −ˆθ(1)∥2
2 +
τw
X
w=τ 0
w+1
ˆτh
X
h=1
∥ˆθ(3) −ˆθ(4)∥2
2
=
τw
X
w=τ 0
w+1
T
X
h=τ 0
h+1
∥ˆθ(2) −ˆθ(1)∥2
2 +
τw
X
w=τ 0
w+1
τ 0
h
X
h=1
∥ˆθ(3) −ˆθ(4)∥2
2
−
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
∥ˆθ(2) −ˆθ(1)∥2
2 +
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
∥ˆθ(3) −ˆθ(4)∥2
2
= (τw −τ 0
w)
h
(T −τ 0
h)∥ˆθ(2) −ˆθ(1)∥2
2 + τ 0
h∥ˆθ(3) −ˆθ(4)∥2
2
i
+(τw −τ 0
w)(ˆτh −ˆτ 0
h)
h
∥ˆθ(3) −ˆθ(4)∥2
2 −∥ˆθ(2) −ˆθ(1)∥2
2
i
(A.14)
In order to simplify the terms R2 and R4, the double sums under consideration are split at
the underlying change point parameters τ 0
w,τ 0
h, leading to the following decompositions.
R2 = 2
τw
X
w=τ 0
w+1
T
X
h=ˆτh+1
ˆεT
(w,h)(ˆθ(2) −ˆθ(1))
= 2
τw
X
w=τ 0
w+1
T
X
h=τ 0
h+1
ˆεT
(w,h)(ˆθ(2) −ˆθ(1)) −2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
ˆεT
(w,h)(ˆθ(2) −ˆθ(1))
= 2
τw
X
w=τ 0
w+1
T
X
h=τ 0
h+1
εT
(w,h)(ˆθ(2) −ˆθ(1)) −2
τw
X
w=τ 0
w+1
T
X
h=τ 0
h+1
(ˆθ(1) −θ0
(1))(ˆθ(2) −ˆθ(1))
−2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)(ˆθ(2) −ˆθ(1)) + 2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
(ˆθ(1) −θ0
(1))(ˆθ(2) −ˆθ(1))
(A.15)
### Page 36

6
Similarly, we have,
R4 = 2
τw
X
w=τ 0
w+1
ˆτh
X
h=1
ˆεT
(w,h)(ˆθ(3) −ˆθ(4))
= 2
τw
X
w=τ 0
w+1
τ 0
h
X
h=1
ˆεT
(w,h)(ˆθ(3) −ˆθ(4)) + 2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
ˆεT
(w,h)(ˆθ(3) −ˆθ(4))
= 2
τw
X
w=τ 0
w+1
τ 0
h
X
h=1
εT
(w,h)(ˆθ(3) −ˆθ(4)) −2
τw
X
w=τ 0
w+1
τ 0
h
X
h=1
(θ(4) −ˆθ(4))(ˆθ(3) −ˆθ(4))
+2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)(ˆθ(3) −ˆθ(4)) −2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
(ˆθ(4) −θ0
(1))(ˆθ(3) −ˆθ(4))
(A.16)
Substituting (A.14), (A.15) and (A.16) in (A.13) we obtain,
U(τw, ˆτh, ˆθ) = R1 −R2 + R3 −R4
= (τw −τ 0
w)
"
(T −τ 0
h)
n
∥ˆθ(2) −ˆθ(1)∥2
2 + 2(ˆθ(1) −θ0
(1))T (ˆθ(2) −ˆθ(1))
o
+τ 0
h
n
∥ˆθ(3) −ˆθ(4)∥2
2 + 2(ˆθ(4) −θ0
(4))T (ˆθ(3) −ˆθ(4))
o#
+(τw −τ 0
w)(ˆτh −ˆτ 0
h)
"
∥ˆθ(3) −ˆθ(4)∥2
2 −∥ˆθ(2) −ˆθ(1)∥2
2
−2(ˆθ(1) −θ0
(1))T (ˆθ(2) −ˆθ(1)) + 2(ˆθ(4) −θ0
(1))T (ˆθ(3) −ˆθ(4))
#
−2
τw
X
w=τ 0
w+1
T
X
h=τ 0
h+1
εT
(w,h)(ˆθ(2) −ˆθ(1)) −2
τw
X
w=τ 0
w+1
τ 0
h
X
h=1
εT
(w,h)(ˆθ(3) −ˆθ(4))
+2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)(ˆθ(2) −ˆθ(1)) −2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)(ˆθ(3) −ˆθ(4))
(A.17)
The expression (A.11) now follows from (A.17) with notational changes. This completes this
algebraic part of the proof of Lemma A.1.
LEMMA A.2.
Suppose the model (1.1) and assume that Conditions A, B, C(i)(a) and
C(ii)(a,b) hold. Let 0 ≤vTh ≤uTh ≤1, be any non-negative sequences. Then,
inf
τh∈Gh(uTh,vTh)Uh(ˆτw,τh, ˆθ) ≥TwThξ2
h
2
h
vTh −cu log(p ∨TwTh) σ
ξh
n uThs
TwTh
o 1
2 i
(A.18)
with probability at least 1 −2exp{−c1 log(p ∨T)} −πT , for some constant c1 > 0 that does
not depend on any model parameters.
### Page 37

HD MEANS OVER 2D CHANGES
7
Proof of Lemma A.2. The proof of this result is analogous to Lemma A.1 above, and
is thus omitted. All assumptions are identical to Lemma A.1, the only distinction being the
desired uniform bound is over the collection Gh of the change parameter in the vertical direc-
tion, instead of Gw.
Proof of Theorem 2.1. We begin with Part (i) of this result. The proof shall rely on a
recursive argument using Lemma A.1, where the desired rate of convergence is obtained by
a series of recursions, with this rate being sharpened at each step.
Consider any vTw > 0 and apply Lemma A.1 on the set Gw(1,vTw) to obtain,
inf
τw∈Gw(1,vTw)Uw(τw, ˆτh, ˆθ) ≥TwThξ2
w
2
h
vTw −cu log(p ∨TwTh) σ
ξw
n
s
TwTh
o 1
2 i
with probability at least 1 −2exp{−c1 log(p ∨TwTh)} −πT . Now upon choosing any,
vTw > v∗
Tw = cu log(p ∨TwTh) σ
ξw
n
s
TwTh
o 1
2 ,
we obtain infτw∈G(1,vTw) Uw(τw, ˆτh, ˆθ) > 0, thus implying that ˜τw /∈G(1,v∗
Tw), i.e., |˜τw −
τ 0
w| ≤Twv∗
Tw, with probability at least 1 −2exp{−c1 log(p ∨TwTh)} −πT . xv Now reset
uTw = v∗
Tw and reapply Lemma A.1 for any vTw > 0 to obtain,
inf
τw∈Gw(uTw,vTw)Uw(τw, ˆτh, ˆθ) ≥TwThξ2
w
2
h
vTw −
n
cu log(p ∨TwTh) σ
ξw
o1+ 1
2 n
s
TwTh
o 1
2+ 1
4 i
,
with probability at least 1 −2exp{−c1 log(p ∨TwTh)} −πT .. Again choosing any,
vT > v∗
T =
n
cu log(p ∨TwTh) σ
ξw
o1+ 1
2 n
s
TwTh
o 1
2+ 1
4 ,
we obtain infτw∈G(uTw,vTw) Uw(τw, ˆτh, ˆθ) > 0, thus yielding ˜τw /∈G(uTw,v∗
Tw), i.e.,
|˜τw −τ 0
w| ≤Tw
n
cu log(p ∨TwTh) σ
ξw
oa2n
s
TwTh
ob2,
(A.19)
with probability at least 1 −2exp{−c1 log(p ∨TwTh)} −πT . Where,
a2 = 1 + 1
2 =
1
X
j=0
1
2j ,
and
b2 = 1
2 + 1
4 =
2
X
j=1
1
2j .
Note that the rate of convergence of ˜τw has been sharpened at the second recursion in com-
parison to the ﬁrst. Continuing these recursions by resetting uT to the bound of the previous
recursion, and applying Lemma A.1, we obtain for the mth recursion,
|˜τw −τ 0
w| ≤Tw
n
cu log(p ∨TwTh) σ
ξw
oamn
s
TwTh
obm,
(A.20)
with probability at least 1 −2exp{−c1 log(p ∨TwTh)} −πT . Repeating these recursions an
inﬁnite number of times and noting that a∞= P∞
j=0(1/2j) = 2, and b∞= P∞
j=1(1/2j) = 1
we obtain,
|˜τw −τ 0
w| ≤Tw
n
cu log(p ∨TwTh) σ
ξw
o2n
s
TwTh
o
xvSince by construction of ˜τw, we have Uw(˜τw, ˆτh, ˆθ) ≤0.
### Page 38

8
with probability at least 1 −2exp{−c1 log(p ∨TwTh)} −πT . Finally, note that despite the
recursions in the above argument, the probability of the bound after every recursion is main-
tained to be at least 1 −2exp{−c1 log(p ∨TwTh)} −πT . This follows since the probability
statement of Lemma A.1 arises from stochastic upper bounds of Lemma B.1 applied recur-
sively with a tighter bound at each recursion. This yields a sequence of events such that
the event at each recursion is a proper subset of the event at the previous recursion. This
completes the proof of Part (i) of this theorem. The proof of Part (ii) follows an analogous
recursive argument applied on Lemma A.2 instead of Lemma A.1.
LEMMA A.3.
Suppose the model (1.1) and assume that conditions A, B, C(i)(b) and
C(ii)(a,c) holds. Let 0 ≤vTw ≤uTw ≤1, be any non-negative sequences. Then, for any 0 <
a < 1, choosing ca ≥√(1/a), we have the following uniform lower bound.
inf
τw∈Gw(uTw,vTw)Uw(τw, ˆτh, ˆθ) ≥TwThξ2
w
2
h
vTw −cuca
σ
ξw
n uTw
TwTh
o 1
2 i
(A.21)
with probability at least 1 −a −o(1) −πT .
Proof of Lemma A.3. The broader structure of this proof is similar to that of Lemma A.1.
The distinction being that the availability of a sharper assumption of Condition C(ii)(c) on
the preliminary mean estimates together with a more delicate analysis of the bounds in Step
1 of the proof of Lemma A.1 shall yields this result.
Recall the inequalities of Step 1 of Lemma A.1 and note that analogous to (A.3), one may
obtain that under Condition C(ii)(c) that,
∥ˆη(1) −η0
(1)∥1 ≤
8cu1ξmin
log(p ∨TwTh),
and
∥ˆη(3) −η0
(3)∥1 ≤
8cu1ξmin
log(p ∨TwTh),
(A.22)
with probability at least 1 −πT . Moreover, also observe here that since Condition C(ii)(c)
assumed here is sharper than C(ii)(b) assumed in Lemma A.1 consequently, the bounds (A.4),
(A.5), (A.6) and (A.7) remain valid here as well, with the same probability.
Next we examine the stochastic terms considered in (A.8) and (A.9) more closely. Apply-
ing Lemma B.2, for any 0 < a < 1, choosing ca ≥4√(1/a), we obtain,
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w

τw
X
w=τ 0
w+1

Th
X
h=τ 0
h+1
εT
(w,h)η0
(1) +
τ 0
h
X
h=1
εT
w,hη0
(3)
 ≤caφξw
√(TwThuTw),
(A.23)
with probability at least 1 −a. Additionally, we also have that,
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w

τw
X
w=τ 0
w+1
Th
X
h=τ 0
h+1
εT
(w,h)(ˆη(1) −η0
(1))

≤
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w

τw
X
w=τ 0
w+1
Th
X
h=τ 0
h+1
ε(w,h)

∞
ˆη(1) −η0
(1)

1
≤cucu1ξminσ√(TwThuTw)
,
(A.24)
### Page 39

HD MEANS OVER 2D CHANGES
9
with probability at least 1 −o(1) −πT , here we have utilized Lemma B.1 as well as (A.22)
to obtain the ﬁnal inequality. Similarly, we can also obtain the following bounds,
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w

τw
X
w=τ 0
w+1
τ 0
h
X
h=1
εT
(w,h)(ˆη(3) −η0
(3))
 ≤cucu1ξminσ√(TwThuTw),
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w

τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)ˆη(1)
 ≤cucu1ξminσ√(TwThuTw),
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w

τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)ˆη(3)
 ≤cucu1ξminσ√(TwThuTw),
(A.25)
with probability at least 1 −o(1) −πT . In order to obtain the second and third inequalities
of (A.25), we have utilized the ℓ1 bounds of (A.4), (A.6). Additionally, towards these bounds
we have also utilized Condition C(i)(b) together with Lemma B.1, in particular from Con-
dition C(i)(b) we have that |ˆτh −τ 0
h| ≤ThuTh, where uTh = cu1

{slog2(p ∨TwTh)}, with
probability 1 −πT , Lemma B.1 is then applied with this choice of uTh.
Next we consider Step 2 as described in the proof of Lemma A.1. Consider the decompo-
sition (A.11) and note that it can be further manipulated as the following,
Uw(τw, ˆτh, ˆθ) = (τw −τ 0
w)
"
(Th −τ 0
h)
n
∥ˆη(1)∥2
2 + 2(ˆθ(1) −θ0
(1))T ˆη(1)
o
+τ 0
h
n
∥ˆη(3)∥2
2 + 2(ˆθ(4) −θ0
(4))T ˆη(3)
o#
+(τw −τ 0
w)(ˆτh −τ 0
h)
"
∥ˆη(3)∥2
2 −∥ˆη(1)∥2
2
−2(ˆθ(1) −θ0
(1))T ˆη(1) + 2(ˆθ(4) −θ0
(1))T ˆη(3)
#
−2
τw
X
w=τ 0
w+1

Th
X
h=τ 0
h+1
εT
(w,h)η0
(1) +
τ 0
h
X
h=1
εT
w,hη0
(3)

−2
τw
X
w=τ 0
w+1
Th
X
h=τ 0
h+1
εT
(w,h)(ˆη(1) −η0
(1))
−2
τw
X
w=τ 0
w+1
τ 0
h
X
h=1
εT
(w,h)(ˆη(3) −η0
(3))
+2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)ˆη(1) −2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)ˆη(3)
(A.26)
We are now ready to proceed to Step 3 to obtain the desired lower bound. Utilizing the ℓ2
lower bounds of (A.5) and (A.6), and the upper bounds of (A.7) (A.23), (A.24) and (A.25) to
### Page 40

10
the expression (A.26) yields,
inf
τw∈Gw(uTw,vTw);
τw≥τ 0
w
Uw(τw, ˆτh, ˆθ) ≥TwThvTw
h
ωhξ2
1 + (1 −ωh)ξ2
3 −cu1ξminξ −cu1ξ2
min
i
−cucaξminσ√(TwThuTw)
≥TwThξ2
w
2
h
vTw −cuca
σ
ξw
 uTw
TwTh
 1
2 i
(A.27)
with probability at least 1−a−o(1)−πT . To obtain the second inequality we have used that
by deﬁnition ωhξ2
1 + (1 −ωh)ξ2
3 = ξ2
w, and ξmin ≤ξw, additionally from Condition B(ii) we
have ξ ≤cuξmin and that the constant cu1 arises from Condition C where it is chosen to be
suitable small enough. Repeating symmetrical arguments for the mirroring permutations of
the ordering of τw,τh with respect to τ 0
w, ˆτh shall yield the same uniform lower bound (A.12).
This completes the proof of this lemma.
LEMMA A.4.
Suppose the model (1.1) and assume that conditions A, B, C(i)(b) and
C(ii)(a,c) holds. Let 0 ≤vTh ≤uTh ≤1, be any non-negative sequences. Then, for any 0 <
a < 1, choosing ca ≥√(1/a), we have the following uniform lower bound.
inf
τh∈Gh(uTh,vTh)Uh(ˆτw,τh, ˆθ) ≥TwThξ2
h
2
h
vTh −ca
σ
ξh
n uTh
TwTh
o 1
2 i
with probability at least 1 −a −o(1) −πT .
Proof of Lemma A.4. The proof of this result is analogous to Lemma A.3 above, and
is thus omitted. All assumptions are identical to Lemma A.3, the only distinction being the
desired uniform bound is over the collection Gh of the change parameter in the vertical direc-
tion, instead of Gw.
Proof of Theorem 2.2. The proof of this result follows a recursive argument similar to
that of Theorem 2.1, the distinction being that these recursions are made on Lemma A.3
instead of Lemma A.1. We begin by considering any vTw > 0 and apply Lemma A.1 on the
set Gw(1,vTw) to obtain,
inf
τw∈Gw(1,vTw)Uw(τw, ˆτh, ˆθ) ≥TwThξ2
w
2
h
vTw −cuca
σ
ξw
n
1
TwTh
o 1
2 i
with probability at least 1 −a −o(1) −πT . Upon choosing any,
vTw > v∗
Tw = cuca
σ
ξw
n
1
TwTh
o 1
2 ,
we obtain infτw∈G(1,vTw) Uw(τw, ˆτh, ˆθ) > 0, thus implying that ˜τw /∈G(1,v∗
Tw), with probabil-
ity at least 1 −a −o(1) −πT . Now reset uTw = v∗
Tw and reapply Lemma A.1 for any vTw > 0
to obtain,
inf
τw∈Gw(uTw,vTw)Uw(τw, ˆτh, ˆθ) ≥TwThξ2
w
2
h
vTw −
n
cuca
σ
ξw
o1+ 1
2 n
1
TwTh
o 1
2+ 1
4 i
,
### Page 41

HD MEANS OVER 2D CHANGES
11
with probability at least 1 −a −o(1) −πT .. Again choosing,
vTw > v∗
Tw =
n
cuca
σ
ξw
o1+ 1
2 n
1
TwTh
o 1
2+ 1
4 ,
we obtain infτw∈G(uTw,vTw) Uw(τw, ˆτh, ˆθ) > 0, thus yielding,
|˜τw −τ 0
w| ≤Tw
n
cuca
σ
ξw
oa2n
1
TwTh
ob2,
(A.28)
with probability at least 1 −a −o(1) −πT . Where,
a2 = 1 + 1
2 =
1
X
j=0
1
2j ,
and
b2 = 1
2 + 1
4 =
2
X
j=1
1
2j .
Continuing these recursions by resetting uTw to the bound of the previous recursion, and
applying Lemma A.1, we obtain for the mth recursion,
|˜τw −τ 0
w| ≤Tw
n
cuca
σ
ξw
oamn
1
TwTh
obm,
(A.29)
with probability at least 1 −a −o(1) −πT . Repeating these recursions an inﬁnite number of
times and noting that a∞= P∞
j=0(1/2j) = 2, and b∞= P∞
j=1(1/2j) = 1 we obtain,
|˜τw −τ 0
w| ≤Tw
n
cuca
σ
ξw
o2n
1
TwTh
o
with probability at least 1−a−o(1)−πT . As earlier for Theorem 2.1, despite the recursions
in the above argument, the probability of the bound after every recursion is maintained to be
at least 1 −a −o(1) −πT since each recursion holds on an event that is a proper subset of
the event at the previous recursion. This completes the proof of Part (i) of this theorem. The
proof of Part (ii) follows an analogous recursive argument applied on Lemma A.4 instead of
Lemma A.3.
As the reader may have observed, a change of notation has been carried out for the results
of Theorem 2.3 and Theorem 2.4. These results are presented in more conventional argmax
notation instead of the argmin notation of the problem setup in Section 1. This is purely a
notational change and all results can equivalently be stated in the argmin language. Accord-
ingly we deﬁne the following versions. Let Uw(τw,τh,θ) and Uh(τw,τh,θ) be as in (A.1) and
consider,
Cw(τw,τh,θ) = −Uw(τw,τh,θ)
and,
Ch(τw,τh,θ) = −Uh(τw,τh,θ)
(A.30)
Then, we can re-express the change point estimators ˜τw(τh,θ) and ˜τh(τw,θ) as,
˜τw(τh,θ) = arg max
1≤τw<Tw
Cw(τw,τh,θ),
and
˜τh(τw,θ) = arg max
1≤τh<Th
Ch(τw,τh,θ)
The proofs of Theorem 2.3 and Theorem 2.4 below are applications of the Argmax Theo-
rem (reproduced as Theorem C.9 in Appendix C). The arguments here are largely an exercise
in veriﬁcation of requirements of this theorem.
### Page 42

12
Proof of Theorem 2.3. We begin by proving the ﬁrst part of this result. Here we shall
examine the limiting distribution of the sequence Thξ2
w(˜τw −τ 0
w), consequently the underly-
ing indexing metric space here is Rxvi. Now consider the two cases of known and unknown
plug-in parameters.
Case I
 τ 0
h and θ0 known

: Following is list of requirement of the Argmax theorem that
require veriﬁcation for this case (see, page 288 of [35]).
1. The sequence Thξ2
w(˜τ ∗
w −τ 0
w) is uniformly tight (see, Deﬁnition C.3).
2.

2σ(w,∞)Ww(ζ) −|ζ|} satisﬁes suitable regularity conditionsxvii.
3. For any ζ ∈[−cu,cu] we have
Cw(τ 0
w + ζT −1
h ξ−2
w ,τ 0
h,θ0) ⇒

2σ(w,∞)Ww(ζ) −|ζ|}.
Note that by setting ˆθ(j) = θ0
(j), j = 1,2,3,4 and ˆτh = τ 0
h, Condition C(i)(b) and C(ii)(a,c)
are trivially satisﬁed. Now using Theorem 2.2 we have that Thξ2
w(˜τ ∗
w −τ 0
w) = Op(1). This
directly yields requirement (1). The second requirement follows from well known properties
of Brownian motion’s. The only remaining requirement is (3), which is provided below.
We begin with a couple of observations that shall be useful in the subsequent argument.
For any given w = 1,...,Tw, deﬁne r.v.’s,
ψw =
1
ξw
√(Th)
h
Th
X
h=τ 0
h+1
εT
(w,h)η0
(1) +
τ 0
h
X
h=1
εT
(w,h)η0
(3)
i
,
(A.31)
and note that we have,
var(ψw) =
1
ξ2wTh
h
Thωhη0
(1)Ση0
(1) + Th(1 −ωh)η0
(3)Ση0
(3)
i
→σ2
(w,∞),
where the convergence follows from Condition D. Now let ζ > 0, w.l.o.g. assume ζT −1
h ξ−2
w
is integer valued and let τ ∗
w = τ 0
w + ζT −1
h ξ−2
w > τ 0
w and consider,
Cw(τ ∗
w,τ 0
h,θ0) =
Tw
X
w=τ 0
w+1
Th
X
h=τ 0
h+1
∥x(w,h) −θ0
(1)∥2
2 +
τ 0
w
X
w=1
Th
X
h=τ 0
h+1
∥x(w,h) −θ0
(2)∥2
2
+
τ 0
w
X
w=1
τ 0
h
X
h=1
∥x(w,h) −θ0
(3)∥2
2 +
Tw
X
w=τ 0
w+1
τ 0
h
X
h=1
∥x(w,h) −θ0
(4)∥2
2
−
Tw
X
w=τ ∗
w+1
Th
X
h=τ 0
h+1
∥x(w,h) −θ0
(1)∥2
2 −
τ ∗
w
X
w=1
Th
X
h=τ 0
h+1
∥x(w,h) −θ0
(2)∥2
2
−
τ ∗
w
X
w=1
τ 0
h
X
h=1
∥x(w,h) −θ0
(3)∥2
2 −
Tw
X
w=τ ∗
w+1
τ 0
h
X
h=1
∥x(w,h) −θ0
(4)∥2
2
=
τ ∗
w
X
w=τ 0
w+1
Th
X
h=τ 0
h+1
h
∥x(w,h) −θ0
(1)∥2
2 −∥x(w,h) −θ0
(2)∥2
2
i
xviAlthough ˜τw is a discrete r.v., however Thξ2w˜τw ∈R
xviiAlmost all sample paths ζ →

2σ(w,∞)Ww(ζ) −|ζ|} are upper semicontinuous and posses a unique
maximum at a (random) point arg maxζ∈R

2σ(w,∞)Ww(ζ) −|ζ|}, which as a random map in the indexing
metric space is tight.
### Page 43

HD MEANS OVER 2D CHANGES
13
+
τ ∗
w
X
w=τ 0
w+1
τ 0
h
X
h=1
h
∥x(w,h) −θ0
(4)∥2
2 −∥x(w,h) −θ0
(3)∥2
2
i
= 2
τ ∗
w
X
w=τ 0
w+1
h
Th
X
h=τ 0
h+1
εT
(w,h)η0
(1) +
τ 0
h
X
h=1
εT
(w,h)η0
(3)
i
−(τ ∗
w −τ 0
w)Thξ2
w
= 2ξw
√(Th)
τ 0
w+ζT −1
h ξ−2
w
X
w=τ 0
w+1
ψw −ζ ⇒2σ(w,∞)Ww1(ζ) −ζ
(A.32)
The ﬁnal equality obtained by substituting the deﬁning expressions of τ ∗
w = τ 0
w +ζT −1
h ξ−2
w >
τ 0
w as well as that of ψw from (A.31). The weak convergence here now follows from the
functional central limit theorem. Repeating the same argument with ζ ∈[−cu,0), yields
C(τ 0 + ζT −1
h ξ−2
w ,τ 0
h,θ0) ⇒2σ(w,∞)Ww2(−ζ) −|ζ|. This completes the proof of require-
ment (3) for the Argmax theorem and consequently an application of its results yields
T −1
h ξ2
w(˜τ ∗−τ 0) ⇒arg maxζ∈R

2σ(w,∞)Ww(ζ) −|ζ|}, which completes the proof of this
case of known plug-in parameters.
Case II
 τ 0
h and θ0 unknown

: In this case the applicability of the argmax theorem requires
veriﬁcation of the following conditions.
1. The sequence Thξ2
w(˜τw −τ 0
w) is uniformly tight.
2.

2σ(w,∞)Ww(ζ) −|ζ|} satisﬁes suitable regularity conditions.
3. For any ζ ∈[−cu,cu] we have
Cw(τ 0
w + ζT −1
h ξ−2
w , ˆτh, ˆθ) ⇒

2σ(w,∞)Ww(ζ) −|ζ|}.
Part (i) again follows from the result of Theorem 2.2 under the assumed Condition C(i)(b)
and C(ii)(a,c) on the nuisance estimates ˆτh and ˆθ. Part (2) is identical to the corresponding
requirement of Case I. Finally to prove part (3) note that from Lemma A.5 we have that,
sup
τw∈Gw(cuT −1
w T −1
h ξ−2
w ,0)
|Cw(τw, ˆτh, ˆθ) −Cw(τw,τ 0
h,θ0)| = op(1).
(A.33)
The approximation (A.33) and Part (3) of Case I together imply Part (3) for this case. This
completes the veriﬁcation of all requirements for this case. The statement of ﬁrst limiting
distribution of the theorem now follows by an application of the Argmax theorem. The second
limiting distribution result can be proved by proceeding with symmetrical arguments.
Proof of Theorem 2.4. The proof of this theorem follows a similar structure as that of
Theorem 2.3 in that it is also an application of the Argmax theorem. The distinction here is in
the limiting distributional structure that is induced by the change of regime of the jump size.
We begin by proving the ﬁrst part of this result, for which consider the sequence (˜τw −τ 0
w).
Consequently, the underlying indexing metric space here is Z. Now consider the two cases
of known and unknown plug-in parameters.
Case I
 τ 0
h and θ0 known

: The requirements to be veriﬁed here are as follows.
1. The sequence (˜τ ∗
w −τ 0
w) is uniformly tight.
2. C(w,∞)(ζ) satisﬁes suitable regularity conditions.
3. For any ζ ∈{−cu,−cu + 1,...,−1,0,1,...cu}, we have
Cw(τ 0
w + ζ,τ 0
h,θ0) ⇒C(w,∞)(ζ).
### Page 44

14
As in the proof of Theorem 2.3, requirement (1) follows directly from the result of Theorem
2.2. Requirement (2) of regularity of the argmax of two sided negative drift random walk
C(w,∞)(ζ) has been proved earlier in Lemma A.3 of the supplement of [25]. The requirement
(3) is veriﬁed in the following.
Let ψw be as deﬁned in (A.31), then we begin by noting that under this non-vanishing
regime √(Th)ξw →ξ(w,∞), we have,
var(ψw) =
1
ξ2wTh
h
Thωhη0
(1)Ση0
(1) + Th(1 −ωh)η0
(3)Ση0
(3)
i
→ξ(w,∞)σ2
(w,∞),
where the convergence follows from Condition D and the regime under consideration. Now
for any ζ ∈{1,2,...,cu}, let τ ∗
w = τ 0
w + ζT −1
h ξ−2
w > τ 0
w and note that,
Cw(τ ∗
w,τ 0
h,θ0) = 2
τ ∗
w
X
w=τ 0
w+1
h
Th
X
h=τ 0
h+1
εT
(w,h)η0
(1) +
τ 0
h
X
h=1
εT
(w,h)η0
(3)
i
−(τ ∗
w −τ 0
w)Thξ2
w
= 2
τ 0
w+ζ
X
w=τ 0
w+1
ψw −ζξ2
w ⇒
ζ
X
w=1
P
 −ξ2
(w,∞), 4ξ2
(w,∞)σ2
(w,∞)

.
The equalities here follow by performing a algebraic decomposition as provided in (A.32).
The weak convergence follows from Condition A′. Repeating the same argument with
ζ ∈{−cu,−cu + 1,...,−1}, yields Cw(τ 0
w + ζ,τ 0
h,θ0) ⇒P−ζ
t=1 P(−ξ2
(w,∞),4ξ2
(w,∞)σ2
(w,∞)).
An application the Argmax theorem now yields (˜τ ∗
w −τ 0
w) ⇒arg maxζ∈Z C(w,∞)(ζ), which
completes the proof of this case.
Case II
 τ 0
h and θ0 unknown

: In this case, the applicability of the argmax theorem requires
veriﬁcation of the following.
1. The sequence (˜τw −τ 0
w) is uniformly tight.
2. C(w,∞)(ζ) satisﬁes suitable regularity conditions.
3. For any ζ ∈{−cu,−cu + 1,...,−1,0,1,...cu}, we have
Cw(τ 0
w + ζ, ˆτh, ˆθ) ⇒C(w,∞)(ζ).
Part (1) follows from Theorem 2.2 under the assumed Condition C(i)(b) and C(ii)(a,c) on
the nuisance estimates ˆτh and ˆθ(j), j = 1,2,3,4. Part (2) is identical to the corresponding
requirement of Case I. Finally to prove part (3) note that from Lemma A.5 where we have
under the regime √Thξw →ξ(2,∞) that,
sup
τ∈G(cuT −1
w ,0)
|Cw(τw, ˆτh, ˆθ) −Cw(τw,τ 0
h,θ0)| = op(1).
The approximation (A.34) and Part (3) of Case I together imply Part (3) for this case. This
completes the veriﬁcation of all requirements for this case. The statement of the ﬁrst limiting
distribution of the theorem now follows by an application of the Argmax theorem. The second
limiting distribution can be proved by symmetrical arguments.
LEMMA A.5.
Let Cw(τw,τh,θ) and Ch(τw,τh,θ) be as deﬁned in (A.30) and suppose
Condition A and B hold. Additionally assume that Condition C(i)(b) and Condition C(ii)(a,c)
### Page 45

HD MEANS OVER 2D CHANGES
15
holds with the sequence rT =

o(1)

s1/2 log(p ∨TwTh)
	
. Then, for any cu > 0, we have,
(i)
sup
τw∈Gw
 cuT −1
w T −1
h ξ−2
w ,0

Cw(τw, ˆτh, ˆθ) −Cw(τw,τ 0
h,θ0)
 = op(1),
and
(ii)
sup
τh∈Gh
 cuT −1
w T −1
h ξ−2
h ,0

Ch(ˆτw,τh, ˆθ) −Cw(τ 0
w,τh,θ0)
 = op(1),
where the orders of (i) and (ii) are w.r.t. Tw and Th, respectively.
PROOF OF LEMMA A.5. We only prove Part (i) below, the proof of Part (ii) follows sym-
metrically. This proof relies on a complete algebraic decomposition of the difference of in-
terest and an examination of the rates of residual terms. To this end, we begin with a few
bounds and deﬁnitions of residual terms that shall be required for the said decomposition.
Observing that from Condition C(i)(b) with the assumed choice of rT , we have that,
|ˆτh −τ 0
h| ≤Thr2
T ,
with
rT =
o(1)
s1/2 log(p ∨TwTh),
(A.34)
with probability at least 1 −πT . Also, by proceeding similar to (A.3) and (A.6), we have
under Condition C(ii)(a,c) with the assumed choice of rT , that,
max
1≤j≤4∥ˆθ(j) −θ0
(j)∥1 ≤max
1≤j≤4
√s∥ˆθ(j) −θ0
(j)∥2 ≤o(1)ξmin
log(p ∨T).
(A.35)
with probability at least 1 −πT . Consequently, we also have,
∥ˆη(1) −η0
(1)∥1 ≤o(1)ξmin
log(p ∨T) and ∥ˆη(3) −η0
(3)∥1 ≤
o(1)ξmin
log(p ∨TwTh).
(A.36)
with probability at least 1 −πT . Finally, following (A.4) and (A.6) we have that,
∥ˆη(1)∥1 ≤cu
√sξmin
and∥ˆη(3)∥1 ≤cu
√sξmin
(A.37)
with probability at least 1 −πT . Now consider the case where τw ≥τ 0
w and ˆτh ≥τ 0
h, and
deﬁne the following residual terms,
R1 = 2
τw
X
w=τ 0
w+1
Th
X
h=τ 0
h+1
εT
(w,h)(ˆη(1) −η0
(1))
R2 = 2
τw
X
w=τ 0
w+1
τ 0
h
X
h=1
εT
(w,h)(ˆη(3) −η0
(3))
R3 = 2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)ˆη(1) −2
τw
X
w=τ 0
w+1
ˆτh
X
h=τ 0
h+1
εT
(w,h)ˆη(3)
R4 = ωh
 ∥ˆη(1)∥2
2 −∥η0
(1)∥2
2

+ (1 −ωh)
 ∥ˆη(3)∥2
2 −∥η0
(3)∥2
2

R5 = 2ωh(ˆθ(1) −θ0
(1))T ˆη(1) + 2(1 −ωh)(ˆθ(4) −θ0
(4))T ˆη(3)
−2(ˆτh −τ 0
h)
Th
(ˆθ(1) −θ0
(1))T ˆη(1) + 2(ˆτh −τ 0
h)
Th
(ˆθ(4) −θ0
(1))T ˆη(3)
+(ˆτh −τ 0
h)
Th
∥ˆη(3)∥2
2 −(ˆτh −τ 0
h)
Th
∥ˆη(1)∥2
2
### Page 46

16
Then under the considered orientation τw ≥τ 0
w and ˆτh ≥τ 0
h, we have the following algebraic
expansion,
Cw(τw, ˆτh, ˆθ) −Cw(τw,τ 0
h,θ0) = Uw(τw,τ 0
h,θ0) −Uw(τw, ˆτh, ˆθ)
= −R1 + R2 −R3 −(τw −τ 0
w)Th(R4 + R5)
(A.38)
We now examine each of the residual terms in (A.38) individually. Applying Lemma B.1 we
have that,
sup
τw∈Gw
 cuT −1
w T −1
h ξ−2
w ,0

;
τw≥τ 0
w
|R1| ≤cuσ
ξw
log(p ∨TwTh)∥ˆη(1) −η0
(1)∥1 = o(1)
w.p. 1 −o(1). Here the equality follows from (A.36). An analogous argument yields,
sup
τw∈Gw
 cuT −1
w T −1
h ξ−2
w ,0

;
τw≥τ 0
w
|R2| = op(1).
Applying Lemma B.1 together with the bounds of (A.34) and (A.36) yields,
sup
τw∈Gw
 cuT −1
w T −1
h ξ−2
w ,0

;
τw≥τ 0
w
|R3| ≤cuσξmin
√s
ξw
rT log(p ∨TwTh) = o(1)
(A.39)
with probability 1 −o(1). To bound the remaining two terms R4 and R5, recall from the
construction (A.1) of the set Gw
 cuT −1
w T −1
h ξ−2
w , 0

, that any τw must satisfy, |τw −τ 0
w| ≤
cuT −1
h ξ−2
w . Now consider,
sup
τw∈Gw
 cuT −1
w T −1
h ξ−2
w ,0

;
τw≥τ 0
w
|(τw −τ 0
w)ThR4| ≤cuξ−2
w |
 ∥ˆη(1)∥2
2 −∥η0
(1)∥2
2| + ∥ˆη(3)∥2
2 −∥η0
(3)∥2
2

≤cuξ−2
w
∥ˆη(1) −η0
(1)∥2
2 + 2(ˆη(1) −η0
(1))T η0
(1)

+cuξ−2
w
∥ˆη(3) −η0
(3)∥2
2 + 2(ˆη(3) −η0
(3))T η0
(3)

≤cuξ−2
w ∥ˆη(1) −η0
(1)∥2
2 + cuξ−1
w ∥ˆη(1) −η0
(1)∥2
+cuξ−2
w ∥ˆη(3) −η0
(3)∥2
2 + cuξ−1
w ∥ˆη(3) −η0
(3)∥2 = op(1).
Here the third inequality follows from applications of the Cauchy Schwarz inequality and
the equality follows from the bounds in (A.36). The only remaining residual term now is R5
which is examined below.
sup
τw∈Gw
 cuT −1
w T −1
h ξ−2
w ,0

;
τw≥τ 0
w
|(τw −τ 0
w)ThR5| ≤cuξ−2
w
h
∥ˆθ(1) −θ0
(1)∥2∥ˆη(1)∥2 + ∥ˆθ(4) −θ0
(4)∥2∥ˆη(3)∥2
i
+cuξ−2
w r2
T ∥ˆθ(1) −θ0
(1)∥2∥ˆη(1)∥2 + cuξ−2
w r2
T ∥ˆθ(4) −θ0
(1)∥2∥ˆη(3)∥2
+cur2
T ∥ˆη(3)∥2
2 + cur2
T ∥ˆη(1)∥2
2 = op(1)
The inequality here follows from several applications of the Cauchy Schwarz inequality and
the equality follows by substituting the choice of rT from (A.34), as well as the available
### Page 47

HD MEANS OVER 2D CHANGES
17
bounds for the mean estimates. Substituting the uniform bounds for R1,R2,R3,R4 and R5
obtained above into the expression (A.38) yields,
sup
τw∈Gw
 cuT −1
w T −1
h ξ−2
w ,0

;
τw≥τ 0
w
Cw(τw, ˆτh, ˆθ) −Cw(τw,τ 0
h,θ0)
 = op(1)
(A.40)
Repeating symmetrical arguments on the remaining three orientations of the ordering of
(τw, ˆτh) w.r.t (τ 0
w,τ 0
h), in particular, τw ≤τ 0
w, ˆτh ≥τ 0
h, and τw ≤τ 0
w, ˆτh ≤τ 0
h, and τw ≥τ 0
w,
ˆτh ≤τ 0
h, shall yield the same op(1) approximation. This completes the proof of Part (i) and
the statement of the lemma.
The proof of Corollary 2.1 requires some preliminary work, in particular we ﬁrst need to
examine the behavior of the estimates ˜θ(j)(τ), j = 1,2,3,4, and uniformly over a collection
of values of τ. This is provided in the following theorem.
THEOREM A.6.
Let 0 ≤uTw, uTw ≤1, be non-negative sequences and let ψ =
maxj ∥η0
(j)∥∞. Additionally, for any constants cu,cu1 > 0, and each j = 1,2,3,4, let,
λ := λj = 8max
n
σ
n2cu1 log(p ∨TwTh)
cuTwThω
o 1
2 , 3ψ
cuω(uTw ∨uTh)
o
.
(A.41)
Suppose Condition A and B holds and that cuTwThω ≥log(p ∨TwTh). Then, ˆθ(j)(τ), j =
1,2,3,4 of (1.17) satisfy the following two results with probability at least 1 −πT .
(i) For any j = 1,2,3,4, and any τ = (τw,τh)T ∈Gw(uTw,0) × Gh(uTh,0), with |Qj(τ)| ≥
cuTwThω, we have
 ˆθ(j)(τ)

Sc
j

1 ≤3
 ˆθ(j)(τ) −θ0
(j)

Sj

1.
(ii) The following bound is satisﬁed,
max
1≤j≤4
sup
τ∈Gw(uTw,0)×Gh(uTh,0)
|Qj(τ)|≥cuTwThω
∥ˆθ(j)(τ) −θ0
(j)∥2 ≤6√sλ.
Here πT = 8exp

−
 cu2 −2

log(p ∨TwTh)
	
, where cu2 = cu1 ∧√(cucu1/2).
PROOF OF THEOREM A.6. Consider j = 1 and any (τw,τh)T ∈Gw(uTw,0)×Gw(uTh,0),
such that τ = (τw,τh)T satisﬁes |Q1(τ)| ≥cuTwThω. Without loss of generality assume
τw ≤τ 0
w, τh ≤τ 0
h The remaining permutations of the ordering of τ w.r.t. τ 0 can be proved
using symmetrical arguments.
An algebraic rearrangement of the elementary inequality
¯x(1)(τ)−ˆθ(1)(τ)
2
2+λ1∥ˆθ(1)(τ)∥1 ≤
¯x(1)(τ) −θ0
(1)
2
2 + λ1∥θ0
(1)∥1 yields,
ˆθ(1)(τ) −θ0
(1)
2
2 + λ1
˜θ(1)(τ)

1 ≤λ1
θ0
(1)

1
+
2
|Q1(τ)|
Tw
X
w=τw+1
Th
X
h=τh+1
˜εT
(w,h)(ˆθ(1)(τ) −θ0
(1)).
= λ1
θ0
(1)

1 +
2
|Q1(τ)|
Tw
X
w=τw+1
Th
X
h=τh+1
εT
(w,h)(ˆθ(1)(τ) −θ0
(1))
−
2
|Q1(τ)|(τ 0
w −τw)(τ 0
h −τh)(θ0
(1) −θ0
(3))T (ˆθ(1)(τ) −θ0
(1))
### Page 48

18
−
2
|Q1(τ)|(τ 0
w −τw)(Th −τ 0
h)(θ0
(1) −θ0
(2))T (ˆθ(1)(τ) −θ0
(1))
−
2
|Q1(τ)|(Tw −τ 0
w)(τ 0
h −τh)(θ0
(1) −θ0
(3))T (ˆθ(1)(τ) −θ0
(1)).
= λ1
θ0
(1)

1 + 2R1 −2R2 −2R3 −2R4
(A.42)
Here ˜ε(w,h) =
 x(w,h) −ˆθ(1)(τ)

. Next we consider the residual terms R1,R2,R3,R4 on the
r.h.s of (A.42). For this purpose, ﬁrst note from Lemma B.3 we have,
2
|Q1(τ)|

Tw
X
w=τw+1
Th
X
h=τh+1
ε(w,h)

∞≤2σ
n2cu1 log(p ∨TwTh)
cuTwThω
o 1
2 ,
(A.43)
with probability at least 1 −8exp{−(cu2 −2)log(p ∨TwTh)}. Additionally recall we have
ψ = maxj ∥η0
(j)∥, and |Q1(τ)| ≥cuTwThω thus,
2|R2 + R3 + R4| ≤6ψ
cuω(uTw ∨uTh)∥ˆθ(1)(τ) −θ0
(1)∥1.
(A.44)
Consequently, upon choosing,
λ∗= max
n
4σ
n2cu1 log(p ∨TwTh)
cuTwThω
o 1
2 , 12ψ
cuω (uTw ∨uTh)
o
,
and substituting these bounds in (A.42) we obtain,
ˆθ(1)(τ) −θ0
(1)
2
2 + λ1
ˆθ(1)(τ)

1 ≤λ1
θ0
(1)

1 + λ∗ˆθ(1)(τ) −θ0
(1)

1,
(A.45)
with probability at least 1 −8exp{−(cu2 −2)log(p ∨TwTh)}. Now choosing λ1 = 2λ∗,
leads to ∥
 ˆθ(1)(τ)

Sc
1∥1 ≤3∥
 ˆθ(1)(τ) −θ0
(1)

S1∥1, which proves part (i) of this theorem for
j = 1. From inequality (A.45) we also have that,
∥ˆθ(1)(τ) −θ0
(1)∥2
2 ≤3
2λ1∥ˆθ(1)(τ) −θ0
(1)∥1 ≤6λ1
√s∥ˆθ(1)(τ) −θ0
(1)∥2
(A.46)
This directly implies that ∥ˆθ(1)(τ) −θ0
(1)∥2 ≤6λ1
√s, where we have used ∥ˆθ(1)(τ) −
θ0
(1)∥1 ≤4√s∥ˆθ(1)(τ) −θ0
(1)∥2, which follows in turn from ∥
 ˆθ(1)(τ)

Sc
1∥1 ≤3∥
 ˆθ(1)(τ) −
θ0
(1)

S1∥1. To supply uniformity over τ, recall that the only stochastic bound used here is
Lemma B.3 which holds uniformly over τ, consequently the ﬁnal bound also holds uniformly
over the given collection. A symmetrical argument can be replicated for each j = 2,3,4 and
recalling that Lemma B.3 also holds uniformly over these j’s. This ﬁnishes the proof of the
Theorem. This result can alternatively be proved using the properties of the soft-thresholding
operator kλ(·), by building uniform versions of arguments such as those in [24].
Following is another preliminary result required to prove Corollary 2.1. This results uses
Theorem A.6 to provide the rate of convergence of Step 1 mean estimates of Algorithm 1.
LEMMA A.7.
Assume Condition A, B and F holds and that the model dimensions to-
gether with the least jump size are restricted by the following condition,
cuσ
ξmin
nslog(p ∨TwTh)
TwThω
o 1
2 ≤cu1,
(A.47)
### Page 49

HD MEANS OVER 2D CHANGES
19
for an appropriately chosen small enough constant cu1 > 0. Additionally assume that
cuTwThω ≥log(p ∨TwTh). Then with a suitably chosen regularizer λ, the Step 1 mean
estimates of Algorithm 1, ˇθ(j) = ˆθ(j)(ˇτ), j = 1,2,3,4, satisfy the following, w.p. 1 −o(1).
(i)
 ˇθ(j)

Sc
j

1 ≤3
 ˇθ(j) −θ0
(j)

Sj

1, for any j = 1,2,3,4.
(ii) The following bound is satisﬁed,
max
1≤j≤4∥ˇθ(1) −θ0
(1)∥2 ≤cu1ξmin.
Consequently, the mean estimates ˇθ(j), j = 1,2,3,4 satisfy Condition C(ii)(a,b).
PROOF OF LEMMA A.7. From Condition F, the initializer ˇτ = (ˇτw, ˇτh)T is assumed
to satisfy, (i) |ˇτw −τ 0
w| ≤TwuTw, (ii) |ˇτh −τ 0
w| ≤ThuTh and (iii) min1≤j≤4 |Qj(ˇτ)| ≥
cuTwThω, where,
uTw = uTh = cu1ωξmin

(√sψ),
(A.48)
i.e., ˇτ ∈Gw(uT ,0) × Gh(uT ,0). Now applying Theorem A.6 while choosing,
λ as prescribed in (A.41) with uTw, uTh as given in (A.48),
(A.49)
we obtain the following two results that hold with probability 1 −o(1). First,
 ˇθ(j)

Sc
j

1 ≤
3
 ˇθ(j) −θ0
(j)

Sj

1, for any j = 1,2,3,4. Second,
max
1≤j≤4∥ˇθ(j) −θ0
(j)∥2 ≤max
h
cuσ
nslog(p ∨TwTh)
TwThω
o 1
2 , cu
(uTw ∨uTh)√sψ
ω
i
,
= ξmin max
h cuσ
ξmin
nslog(p ∨TwTh)
TwThω
o 1
2 , cu
(uTw ∨uTh)√sψ
ξminω
i
= ξmin
h
R1,R2
i
(A.50)
Here the ﬁrst equality is simply an algebraic manipulation. Now for a suitable chosen cu1 > 0,
we have from assumption (A.47) that,
cuσ
ξmin
nslog(p ∨TwTh)
TwThω
o 1
2 ≤cu1,
which provides a bound for term R1 on the RHS of (A.50). Next we bound term R2 of the
same expression. Substituting the choice of uT from (A.48) in term R2, together with the
earlier bound for R1, we obtain,
max
1≤j≤4∥ˇθ(1) −θ0
(1)∥2 ≤ξmin
h
R1,R2
i
≤cu1ξmin,
with probability 1 −o(1). Thereby the requirement Condition C(ii)(a,b) are met and this
completes the proof of the lemma.
Proof of Corollary 2.1. The logical progression of the argument to follow is as described
in Figure 3, effectively, we show that once Algorithm 1 is initialized under Condition F, then,
under the assumed rate conditions on model parameters all remaining conditions fall in line
for Step 1 and Step 2, thereby allowing applicability of the main results of Sub-section 2.1.
We begin by noting that Lemma A.7 establishes that ˇθ(j) = ˜θ(j)(ˇτ), j = 1,2,3,4, of Step 1
of Algorithm 1 satisﬁes Condition C(ii)(a,c), under the dimensional rate assumption (A.47),
### Page 50

20
which is weaker than Condition E, and therefore this result continues to hold. Also observe
that Condition C(i)(a) is weaker than assumed Condition F on initializer ˇτ. Thus, a direct
application of Theorem 2.1 yields the rate of convergence of ˆτ of Step 1 of Algorithm 1 as,
|ˆτw −τ 0
w| ≤cuσ2T −1
h ξ−2
w slog2(p ∨TwTh),
and
|ˆτh −τ 0
h| ≤cuσ2T −1
w ξ−2
h slog2(p ∨TwTh),
(A.51)
with probability at least 1 −o(1). This completes the proof of Part (a) of this theorem.
Moving onto Part (b), ﬁrst observe that the bounds (A.51) together with rate assumption
of Condition E implies that ˆτ = (ˆτw, ˆτh)T of Step 1 satisﬁes the stronger Condition C(i)(b).
Next we show that the updated mean estimates ˆθ(j), j = 1,2,3,4, satisfy Condition C(ii)(a,c).
For this purpose, note that from (A.51) we have that ˆτw ∈Gw(uTw,0), and ˆτh ∈Gh(uTh,0)
with probability 1 −o(1), where,
(uTw ∨uTh) ≤cuσ2T −1
w T −1
h ξ−2
minslog2(p ∨TwTh),
(A.52)
Moreover, (A.51) and Condition E also imply that with the same probability as above, we
have |Qj(ˆτ)| ≥cuTwThω. Now applying Theorem A.6 with,
λ asprescribed in (A.41) with (uTw ∨uTh) as in (A.52),
(A.53)
we obtain ˆθ(j) = ˜θ(j)(ˆτ), j = 1,2,3,4, of Step 2 of Algorithm 1 satisﬁes Condition C(ii)(a).
Furthermore,
max
1≤j≤4
ˆθ(j) −θ0
(j)

2 ≤max
h
σ
ncuslog(p ∨TwTh)
TwThω
o 1
2 , cu
√sψ
ω
(uTw ∨uTh)
i
.
=
ξmin
s1/2 log(p ∨TwTh) max
h
σ
ncuslog3/2(p ∨TwTh)
ξmin
√(TwThω)
o
,
cuslog(p ∨TwTh)ψ
ωξmin
(uTw ∨uTh)
i
=
ξmin
s1/2 log(p ∨TwTh) max

R1,R2

(A.54)
with probability at 1−o(1). Here the ﬁrst equality is simply an algebraic manipulation. From
Condition E we have that R1 ≤cu1, where cu1 > 0, is an appropriately chosen small enough
constant. Next consider term R2 of (A.54). Substituting (uTw ∨uTh) from (A.52) in term R2
we obtain,
cuslog(p ∨TwTh)
ψ
ωξmin
(uTw ∨uTh) ≤cuσ2 ψ
ξmin
ns2 log3(p ∨TwTh)
ξ2
minTwThω
o
,
≤cu
n σ
ξmin
slog2(p ∨TwTh)
√(TwThω)
o2
≤cu1.
Here the second inequality follows from the assumption (ψ

ξ) ≤log(p ∨TwTh). The third
inequality follows from Condition E. Substituting the bounds for terms R1 and R2 back in
(A.54) yields,
max
1≤j≤4
ˆθ(j) −θ0
(j)

2 ≤
cu1ξmin
s1/2 log(p ∨TwTh)
(A.55)
with probability at 1 −o(1). Thus, the estimates ˆθ1 and ˆθ2 of Step 2 of Algorithm 1 satisfy
all requirement of Condition C(ii)(a,c). We now appeal to Theorem 2.2 which yields Part (b)
of this theorem.
### Page 51

HD MEANS OVER 2D CHANGES
21
Nearly all ingredients for Part (c) are already available above. The only observation
required here is that repeating the above arguments under the tightened rate assumption

{slog2(p∨TwTh)}
√(TwThω)

= o(1), yields that Step 2 estimates ˆτ and ˆθ satisfy Condi-
tion C(i)(b) and C(ii)(a,c) with the additional requirement of Theorem 2.3 and Theorem 2.4.
The statement of Part (c) is now a direct consequence of these theorem’s under respective
jump size regimes. This completes the proof of this corollary.
APPENDIX B: DEVIATION BOUNDS
LEMMA B.1.
Suppose Condition A and B(i) holds and let 0 ≤vTw ≤uTw ≤1, and 0 ≤
vTh ≤uTh ≤1, be any non-negative sequences. Then for any cu ≥1, we have,
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w
sup
τh∈Gh(uTh,vTh);
τh≥τ 0
h

τw
X
w=τ 0
w+1
τh
X
h=τ 0
h+1
ε(w,h)

∞≤2cuσ log(p ∨TwTh)√ TwuTwThuTh

with probability at least 1 −2exp{−(cu −2)log(p ∨TwTh)}.
PROOF OF LEMMA B.1. Without loss of generality assume vTw ≥(1/Tw), and vTh ≥
(1/Th), else, the sum of interest is over an empty set and is thus trivially zero. Now consider
any k ∈{1,2,...,p} and any τw > τ 0
w, τh > τ 0
h and apply the Bernstein’s inequality (Lemma
C.7) for any d > 0 to obtain,
pr

τw
X
w=τ 0
w+1
τh
X
h=τ 0
h+1
ε(w,h,k)
 > d(τw −τ 0
w)(τh −τ 0
h)

≤
2exp
n
−1
2(τw −τ 0
w)(τh −τ 0
h)
 d2
σ2 ∧d
σ
o
.
(B.1)
Choose d = 2cuσ{log2(p ∨TwTh)
 (τw −τ 0
w)(τh −τ 0
h)

}1/2, and note that,
(τw −τ 0
w)(τh −τ 0
h) d2
2σ2 = 2c2
u log2(p ∨TwTh),
and,
(τw −τ 0
w)(τh −τ 0
h) d
2σ ≥cu log(p ∨TwTh),
(B.2)
where we have used (τw −τ 0
w) ≥TwvTw ≥1, (τh −τ 0
h) ≥ThvTh ≥1, to obtain the ﬁrst
inequality. Thus, substituting this choice of d in (B.1) and recalling that by choice cu ≥1, we
obtain,

τw
X
w=τ 0
w+1
τh
X
h=τ 0
h+1
ε(w,h,k)
 ≤2cuσ(τw −τ 0
w)1/2(τh −τ 0
h)1/2{log2(p ∨TwTh)}1/2
≤2cuσ{TwuTwThuTh log2(p ∨TwTh)}1/2,
with probability at least 1−2exp{−cu log(p∨TwTh)}. The statement of this lemma follows
by applying a union bound over k = 1,...,p, τw = 1,...,Tw, and τh = 1,...Th.
REMARK 7.
Lemma B.1 provides a uniform bound over a collection with the restriction
τw ≥τ 0
w and τh ≥τ 0
h. This restriction is considered for clarity of presentation of the proof.
### Page 52

22
A more general result without this restriction can be obtained following identical arguments,
speciﬁcally,
sup
τw∈Gw(uTw,vTw)
sup
τh∈Gh(uTh,vTh)

XX
(w,h)∈Q(τ,τ 0)
ε(w,h)

∞≤2cuσ log(p ∨TwTh)√ TwuTwThuTh

with probability at least 1 −2exp{−(cu −2)log(p ∨TwTh)}. Here Q(τ,τ 0) represents the
quadrant of observations bounded by τ = (τw,τh)T and τ 0 = (τ 0
w,τ 0
h)T , i.e.,
Q(τ,τ 0) =

(w,h) ∈{τw ∧τ 0
w,...,τw ∨τ 0
w} × {τh ∧τ 0
h,...,τh ∨τ 0
h}
	
.
(B.3)
To prove this more general result one may proceed case by case based on the permutations
of the orientation between τ = (τw,τh)T and τ 0 = (τ 0
w,τ 0
h)T , and follow the same argument
as the proof of Lemma B.1.
LEMMA B.2.
Suppose Condition A and B(i) hold and let uTw,vTw be any non-negative
sequences satisfying 0 ≤vTw ≤uTw ≤1. Then for any 0 < a < 1, choosing ca ≥4√(1/a),
we have,
sup
τw∈Gw(uTw,vTw);
τw≥τ 0
w

τw
X
w=τ 0
w+1

Th
X
h=τ 0
h+1
εT
(w,h)η0
(1) +
τ 0
h
X
h=1
εT
w,hη0
(3)
 ≤caφξw
√(TwThuTw),
with probability at least 1 −a.
PROOF. Begin by deﬁning for any w the r.v.,
ψw =
Th
X
h=τ 0
h+1
εT
(w,h)η0
(1) +
τ 0
h
X
h=1
εT
(w,h)η0
(3)
Then from Lemma C.6 we have ψw ∼subE(λ2), where λ2 = φ2
(Th −τ 0
h)ξ2
1 + τ 0
hξ2
3} =
φ2Thξ2
w. Consequently from Lemma C.5 we also have varψw ≤16λ2. Next, we note that
there are at most TwuTw values of τw in the set Gw(uTw,vTw), and then apply the Kol-
mogorov’s inequality (Theorem C.8) for any d > 0 to obtain,
pr

sup
τw∈Gw(uTw,vTw)

τw
X
w=τ 0
w+1
ψw
 > d

≤16TwuTw
d2
λ2.
choosing d = caφξw
√(TwThuTw), with ca ≥4√(1/a) yields the result of the lemma.
LEMMA B.3.
Assume Condition A and B(i) holds. Additionally assume for cu > 0 that
cuTwThω ≥log(p ∨TwTh). Then for any cu1 > 0, we have,
max
1≤j≤4
sup
τw∈{1,.....,T};
τh∈{1,.....,T};
|Qj(τ)|≥cuTwThω

1
|Qj(τ)|
XX
(w,h)∈Qj(τ)
ε(w,h)

∞≤σ
n2cu1 log(p ∨TwTh)
cuTwThω
o 1
2
with probability at least 1 −8exp

−(cu2 −2)log(p ∨TwTh)
	
, where cu2 = cu1 ∧
√(cucu1/2).
### Page 53

HD MEANS OVER 2D CHANGES
23
PROOF OF LEMMA B.3. First consider the case of j = 1, where Q1(τ) =

(w,h) ∈
{τw+1,...Tw}×{τh+1,...,Th}
	
, then we have PTw
w=τw+1
PTh
h=τh+1 ε(w,h,k) ∼subE
 |Q1(τ)|σ2
.
Now, applying Bernstein’s inequality (Lemma C.7) for any d > 0, we have,
pr

Tw
X
w=τw+1
Th
X
h=τh+1
ε(w,h,k)
 > d|Q1(τ)|

≤2exp
n
−|Q1(τ)|
2
 d2
σ2 ∧d
σ
o
.
(B.4)
Choose d = σ{2cu1 log(p ∨TwTh)

|Q1(τ)|}1/2, and due to the assumption |Q1(τ)| ≥
cuTwThω ≥log(p ∨TwTh), we have,
|Q1(τ)| d2
2σ2 = cu1 log(p ∨TwTh),
and,
|Q1(τ)| d
2σ ≥√(cu1/2)(cuTwThω)1/2{log(p ∨TwTh)}1/2 ≥√(cucu1/2)log(p ∨TwTh).
Now substituting this choice of d in (B.4), we obtain,
1
|Q1(τ)|

Tw
X
w=τw+1
Th
X
h=τh+1
ε(w,h,k)
 ≤σ{2cu1 log(p ∨TwTh)

|Q1(τ)|}1/2 ≤σ
n2cu1 log(p ∨TwTh)
cuTwThω
o1/2
with probability at least 1 −2exp{−cu2 log(p ∨TwTh)}, where cu2 = cu1 ∧√(cucu1/2).
Uniformity of the inner collection in the lemma follows by applying union bounds over all
values of τw,τh and k. Uniformity over j = 1,2,3,4 can be obtained by proceeding with
identical arguments as above for each respective quadrant to obtain the same upper bound
and ﬁnally applying a union bound to obtain the statement of the lemma.
APPENDIX C: DEFINITIONS AND AUXILIARY RESULTS
The following deﬁnition’s and results provide basic properties of subexponential distribu-
tions. These are largely reproduced from [37] and [31]. Theorem C.8 and C.9 below repro-
duce the Kolmogorov’s inequality and the argmax theorem. We also refer to Appendix B and
Appendix F of [25] and [28], respectively, where these results and some additional proofs
have been compiled.
DEFINITION C.1.
[Subexponential r.v.] A random variable X ∈R is said to be sub-
exponential with parameter σ2 > 0
 denoted by X ∼subE(σ2)

if E(X) = 0 and its moment
generating function
E(etX) ≤et2σ2/2,
∀|t| ≤1
σ
DEFINITION C.2.
A random vector X ∈Rp shall said to be subexponential with param-
eter σ2, if the inner product ⟨X,v⟩∼subE(σ2), respectively, for any v ∈Rp with ∥v∥2 = 1.
Following is the elementary deﬁnition of uniform tightness of a sequence of random vari-
ables reproduced from Page 166, Chapter 2 of [16].
DEFINITION C.3.
A sequence of random variables Xn is said to be uniformly tight if for
every ϵ > 0, there is a compact set K such that pr(Xn ∈K) > 1 −ϵ.
### Page 54

24
LEMMA C.4.
[Tail bounds] If X ∼subE(σ2), then
pr(|X| ≥λ) ≤2exp
n
−1
2
λ2
σ2 ∧λ
σ
o
.
LEMMA C.5 (Moment bounds).
If X ∼subE(σ2), then
E|X|k ≤4σkkk,
k > 0.
LEMMA C.6.
Assume that X ∼subE(σ2), and that α ∈R, then αX ∼subE(α2σ2).
Moreover, assume that X1 ∼subE(σ2
1) and X2 ∼subE(σ2
2), then X1+X2 ∼subE((σ1 + σ2)2),
additionally, if X1 and X2 are independent, then X1 + X2 ∼subE(σ2
1 + σ2
2).
LEMMA C.7 (Bernstein’s inequality).
Let X1,X2,...,XT be independent random vari-
ables such that Xt ∼subE(λ2). Then for any d > 0 we have,
pr(| ¯X| > d) ≤2exp
n
−T
2
d2
λ2 ∧d
λ
o
The next result is the Kolmogorov’s inequality reproduced from [20]
THEOREM C.8 (Kolmogorov’s inequality).
If ξ1,ξ2,... is a sequence of mutually inde-
pendent random variables with mean values E(ξk) = 0 and ﬁnite variance var(ξk) = D2
k
(k = 1,2,...), we have, for any ε > 0,
pr

max
1≤k≤m
ξ1 + ξ2 + ... + ξk
 > ε

≤1
ε2
m
X
k=1
D2
k
Following is the well known ‘Argmax’ theorem reproduced from Theorem 3.2.2 of [35].
THEOREM C.9 (Argmax Theorem).
Let Mn,M be stochastic processes indexed by a
metric space H such that Mn ⇒M in ℓ∞(K) for every compact set K ⊆H. Suppose that
almost all sample paths h →M(h) are upper semicontinuous and posses a unique maximum
at a (random) point ˆh, which as a random map in H is tight. If the sequence ˆhn is uniformly
tight and satisﬁes Mn(ˆhn) ≥suph Mn(h) −op(1), then ˆhn ⇒ˆh in H.
APPENDIX D: ADDITIONAL DETAILS AND RESULTS
This section contains is divided in three subsections. Sub-section D.1 provides additional
results of image denoising carried out in Section 4. Sub-section D.2 provides remaining sim-
ulation results of Section 5. Finally, sub-section D.3 provides details pertaining to estimation
of additional parameters such as drifts and asymptotic variances, as well as on computation
of quantiles which are in turn necessary for computation of conﬁdence intervals presented in
Section 4 and Section 5.
D.1. Additional results of Section 4.
Here we provide the remaining results of image
denoising application described in sub-Section 4.2. These are provided in Figure 9 (single
change point synthetic examples), Figure 10 (multiple change point synthetic examples),
Figure 11 (lena image) and Figure 12 (Chaplin image).
### Page 55

HD MEANS OVER 2D CHANGES
25
FIG 9. Image denoising with Algorithm 3. Images are 50 × 50 pixels with at most one 2d-change point. Left
panels: True images (unobserved), Center panels: Noisy images (observed), Right panels: Recovered images.
Noise set to Σ = I3×3, and tuning constant cbic = 1.
FIG 10. Image denoising with Algorithm 3. Image is 250 × 200 pixels with one 2d-change point. Left panel: True
image (unobserved), Center panel: Noisy image (observed), Right panel: Recovered image. Estimated model
recovered with ℓ= 2 hierarchical change points inducing a total of 8 disjoint partitions of the sampling space.
Noise set to Σ = I3×3, and tuning constant cbic = 1.
FIG 11. Image denoising with Algorithm 3. Image is 600 × 400 pixels. Left panel: Recovered image with cbic =
0.5, estimated model recovered with ℓ= 11 hierarchical change points inducing a total of 2569 disjoint partitions
of the sampling space. Right panel: Recovered image with cbic = 1, estimated model recovered with ℓ= 11
hierarchical change points inducing a total of 1278 disjoint partitions of the sampling space. Noise set to Σ =
0.05·I3×3, see, Figure 7 for true and noisy images.
### Page 56

26
FIG 12. Image denoising with Algorithm 3. Image is 600 × 600 pixels. Left panel: Recovered image with
cbic = 0.25, estimated model recovered with ℓ= 15 hierarchical change points inducing a total of 15952 disjoint
partitions of the sampling space. Right panel: Recovered image with cbic = 1, estimated model recovered with
ℓ= 13 hierarchical change points inducing a total of 1401 disjoint partitions of the sampling space. Noise set to
Σ = 0.05·I3×3, see, Figure 8 for true and noisy images.
D.2. Additional simulation results of Section 5.
Below are the additional results of
the simulation designs described in Section 5. Table 6 -Table 9 provide results in context of
estimation of the height change parameter τh, these results are under symmetrical designs to
those provided in context of the width change parameter τw in Section 5. A large number of
other cases were also evaluated the results of which were in accordance to the discussion of
Section 5 and these are omitted to avoid redundancy.
Tw = 30,
τ0w/Tw = 0.2
p = 10
p = 50
bias (rmse)
coverage (av. ME)
bias (rmse)
coverage (av. ME)
τ0
h/Th
Th
Vanishing
Non-Vanishing
Vanishing
Non-Vanishing
0.2
30
0.122 (0.574)
0.912 (0.527)
0.926 (0.07)
0.142 (0.581)
0.9 (0.465)
0.904 (0.018)
0.2
35
0.03 (0.205)
0.958 (0.514)
0.968 (0.05)
0.168 (1.251)
0.916 (0.483)
0.922 (0.018)
0.2
40
0.012 (0.126)
0.984 (0.515)
0.984 (0.028)
0.116 (0.429)
0.912 (0.486)
0.916 (0.018)
0.2
45
0.032 (0.268)
0.952 (0.529)
0.956 (0.038)
0.078 (0.366)
0.936 (0.498)
0.936 (0.016)
0.4
30
0.042 (0.293)
0.95 (0.5)
0.954 (0.03)
0.138 (0.76)
0.928 (0.505)
0.932 (0.012)
0.4
35
0.018 (0.205)
0.964 (0.518)
0.966 (0.014)
0.076 (0.663)
0.95 (0.502)
0.954 (0.01)
0.4
40
0.004 (0.179)
0.968 (0.532)
0.968 (0.02)
0.04 (0.228)
0.966 (0.511)
0.966 (0.008)
0.4
45
0.008 (0.219)
0.958 (0.529)
0.962 (0.022)
0.036 (0.2)
0.96 (0.506)
0.962 (0.006)
0.6
30
0.012 (0.245)
0.956 (0.487)
0.958 (0.024)
0.052 (0.329)
0.946 (0.458)
0.946 (0)
0.6
35
0.018 (0.241)
0.96 (0.522)
0.96 (0.022)
0.048 (0.261)
0.956 (0.463)
0.956 (0)
0.6
40
0 (0.253)
0.958 (0.526)
0.96 (0.012)
0.05 (0.3)
0.95 (0.478)
0.954 (0.004)
0.6
45
0.022 (0.338)
0.94 (0.53)
0.948 (0.022)
0.028 (0.237)
0.95 (0.482)
0.952 (0.002)
0.8
30
0.016 (0.502)
0.988 (0.483)
0.988 (0.036)
0.022 (0.784)
0.968 (0.384)
0.968 (0.004)
0.8
35
0.042 (0.241)
0.96 (0.516)
0.962 (0.022)
0.034 (0.911)
0.968 (0.408)
0.968 (0.002)
0.8
40
0.04 (0.303)
0.942 (0.517)
0.956 (0.036)
0.014 (0.148)
0.978 (0.415)
0.978 (0)
0.8
45
0.03 (0.249)
0.966 (0.522)
0.97 (0.032)
0 (0.19)
0.97 (0.422)
0.97 (0)
TABLE 6
Simulation results for estimation of τ0
h based on 500 replications. All reported metrics rounded to three
decimals. Other data generating parameters: Tw = 30, τ0w = ⌊0.2·Tw⌋and p ∈{10,50}.
### Page 57

HD MEANS OVER 2D CHANGES
27
Tw = 30,
τ0w/Tw = 0.2
p = 100
p = 250
bias (rmse)
coverage (av. ME)
bias (rmse)
coverage (av. ME)
τ0
h/Th
Th
Vanishing
Non-Vanishing
Vanishing
Non-Vanishing
0.2
30
0.276 (1.346)
0.854 (0.444)
0.854 (0.018)
0.514 (2.32)
0.808 (0.422)
0.81 (0.03)
0.2
35
0.212 (1.397)
0.896 (0.457)
0.904 (0.02)
0.17 (0.828)
0.892 (0.415)
0.892 (0.01)
0.2
40
0.158 (0.553)
0.884 (0.464)
0.884 (0.01)
0.28 (1.114)
0.86 (0.443)
0.86 (0.022)
0.2
45
0.124 (1.043)
0.926 (0.473)
0.928 (0.012)
0.144 (0.678)
0.898 (0.441)
0.898 (0.006)
0.4
30
0.134 (0.677)
0.918 (0.492)
0.92 (0.016)
0.216 (0.984)
0.894 (0.469)
0.896 (0.012)
0.4
35
0.074 (0.564)
0.94 (0.489)
0.94 (0.006)
0.078 (0.387)
0.938 (0.474)
0.938 (0)
0.4
40
0.05 (0.319)
0.952 (0.498)
0.952 (0)
0.108 (0.756)
0.94 (0.483)
0.94 (0.004)
0.4
45
0.052 (0.261)
0.954 (0.509)
0.954 (0.002)
0.09 (0.332)
0.908 (0.486)
0.908 (0)
0.6
30
0.05 (0.307)
0.948 (0.455)
0.948 (0.002)
0.048 (0.303)
0.966 (0.438)
0.966 (0)
0.6
35
0.09 (0.553)
0.94 (0.465)
0.94 (0.006)
0.06 (0.385)
0.948 (0.449)
0.948 (0)
0.6
40
0.038 (0.214)
0.966 (0.469)
0.966 (0)
0.048 (0.31)
0.948 (0.46)
0.948 (0)
0.6
45
0.034 (0.286)
0.954 (0.475)
0.954 (0.002)
0.056 (0.322)
0.95 (0.467)
0.95 (0)
0.8
30
0.032 (0.93)
0.958 (0.353)
0.958 (0.006)
0.002 (0.504)
0.972 (0.303)
0.972 (0.002)
0.8
35
0.02 (0.932)
0.948 (0.362)
0.948 (0.002)
0.028 (0.268)
0.946 (0.317)
0.946 (0)
0.8
40
0.006 (0.118)
0.986 (0.377)
0.986 (0)
0.02 (0.2)
0.96 (0.334)
0.96 (0)
0.8
45
0.016 (0.21)
0.968 (0.387)
0.968 (0.002)
0.082 (1.477)
0.952 (0.354)
0.952 (0.006)
TABLE 7
Simulation results for estimation of τ0
h based on 500 replications. All reported metrics rounded to three
decimals. Other data generating parameters: Tw = 30, τ0w = ⌊0.2·Tw⌋and p ∈{100,250}.
Tw = 30,
τ0w/Tw = 0.4
p = 10
p = 50
bias (rmse)
coverage (av. ME)
bias (rmse)
coverage (av. ME)
τ0
h/Th
Th
Vanishing
Non-Vanishing
Vanishing
Non-Vanishing
0.2
30
0.122 (0.574)
0.912 (0.527)
0.926 (0.07)
0.142 (0.581)
0.9 (0.465)
0.904 (0.018)
0.2
35
0.03 (0.205)
0.958 (0.514)
0.968 (0.05)
0.168 (1.251)
0.916 (0.483)
0.922 (0.018)
0.2
40
0.012 (0.126)
0.984 (0.515)
0.984 (0.028)
0.116 (0.429)
0.912 (0.486)
0.916 (0.018)
0.2
45
0.032 (0.268)
0.952 (0.529)
0.956 (0.038)
0.078 (0.366)
0.936 (0.498)
0.936 (0.016)
0.4
30
0.042 (0.293)
0.95 (0.5)
0.954 (0.03)
0.138 (0.76)
0.928 (0.505)
0.932 (0.012)
0.4
35
0.018 (0.205)
0.964 (0.518)
0.966 (0.014)
0.076 (0.663)
0.95 (0.502)
0.954 (0.01)
0.4
40
0.004 (0.179)
0.968 (0.532)
0.968 (0.02)
0.04 (0.228)
0.966 (0.511)
0.966 (0.008)
0.4
45
0.008 (0.219)
0.958 (0.529)
0.962 (0.022)
0.036 (0.2)
0.96 (0.506)
0.962 (0.006)
0.6
30
0.012 (0.245)
0.956 (0.487)
0.958 (0.024)
0.052 (0.329)
0.946 (0.458)
0.946 (0)
0.6
35
0.018 (0.241)
0.96 (0.522)
0.96 (0.022)
0.048 (0.261)
0.956 (0.463)
0.956 (0)
0.6
40
0 (0.253)
0.958 (0.526)
0.96 (0.012)
0.05 (0.3)
0.95 (0.478)
0.954 (0.004)
0.6
45
0.022 (0.338)
0.94 (0.53)
0.948 (0.022)
0.028 (0.237)
0.95 (0.482)
0.952 (0.002)
0.8
30
0.016 (0.502)
0.988 (0.483)
0.988 (0.036)
0.022 (0.784)
0.968 (0.384)
0.968 (0.004)
0.8
35
0.042 (0.241)
0.96 (0.516)
0.962 (0.022)
0.034 (0.911)
0.968 (0.408)
0.968 (0.002)
0.8
40
0.04 (0.303)
0.942 (0.517)
0.956 (0.036)
0.014 (0.148)
0.978 (0.415)
0.978 (0)
0.8
45
0.03 (0.249)
0.966 (0.522)
0.97 (0.032)
0 (0.19)
0.97 (0.422)
0.97 (0)
TABLE 8
Simulation results for estimation of τ0
h based on 500 replications. All reported metrics rounded to three
decimals. Other data generating parameters: Tw = 30, τ0w = ⌊0.4·Tw⌋and p ∈{10,50}.
### Page 58

28
Tw = 30,
τ0w/Tw = 0.4
p = 100
p = 250
bias (rmse)
coverage (av. ME)
bias (rmse)
coverage (av. ME)
τ0
h/Th
Th
Vanishing
Non-Vanishing
Vanishing
Non-Vanishing
0.2
30
0.276 (1.346)
0.854 (0.444)
0.854 (0.018)
0.514 (2.32)
0.808 (0.422)
0.81 (0.03)
0.2
35
0.212 (1.397)
0.896 (0.457)
0.904 (0.02)
0.17 (0.828)
0.892 (0.415)
0.892 (0.01)
0.2
40
0.158 (0.553)
0.884 (0.464)
0.884 (0.01)
0.28 (1.114)
0.86 (0.443)
0.86 (0.022)
0.2
45
0.124 (1.043)
0.926 (0.473)
0.928 (0.012)
0.144 (0.678)
0.898 (0.441)
0.898 (0.006)
0.4
30
0.134 (0.677)
0.918 (0.492)
0.92 (0.016)
0.216 (0.984)
0.894 (0.469)
0.896 (0.012)
0.4
35
0.074 (0.564)
0.94 (0.489)
0.94 (0.006)
0.078 (0.387)
0.938 (0.474)
0.938 (0)
0.4
40
0.05 (0.319)
0.952 (0.498)
0.952 (0)
0.108 (0.756)
0.94 (0.483)
0.94 (0.004)
0.4
45
0.052 (0.261)
0.954 (0.509)
0.954 (0.002)
0.09 (0.332)
0.908 (0.486)
0.908 (0)
0.6
30
0.05 (0.307)
0.948 (0.455)
0.948 (0.002)
0.048 (0.303)
0.966 (0.438)
0.966 (0)
0.6
35
0.09 (0.553)
0.94 (0.465)
0.94 (0.006)
0.06 (0.385)
0.948 (0.449)
0.948 (0)
0.6
40
0.038 (0.214)
0.966 (0.469)
0.966 (0)
0.048 (0.31)
0.948 (0.46)
0.948 (0)
0.6
45
0.034 (0.286)
0.954 (0.475)
0.954 (0.002)
0.056 (0.322)
0.95 (0.467)
0.95 (0)
0.8
30
0.032 (0.93)
0.958 (0.353)
0.958 (0.006)
0.002 (0.504)
0.972 (0.303)
0.972 (0.002)
0.8
35
0.02 (0.932)
0.948 (0.362)
0.948 (0.002)
0.028 (0.268)
0.946 (0.317)
0.946 (0)
0.8
40
0.006 (0.118)
0.986 (0.377)
0.986 (0)
0.02 (0.2)
0.96 (0.334)
0.96 (0)
0.8
45
0.016 (0.21)
0.968 (0.387)
0.968 (0.002)
0.082 (1.477)
0.952 (0.354)
0.952 (0.006)
TABLE 9
Simulation results for estimation of τ0
h based on 500 replications. All reported metrics rounded to three
decimals. Other data generating parameters: Tw = 30, τ0w = ⌊0.4·Tw⌋and p ∈{100,250}.
D.3. Estimation of drifts, asymptotic variances and quantiles.
We begin with a dis-
cussion on the estimation of ξw, ξh, and σ2
(w,∞),σ2
(h,∞) which utilized for the computation
of conﬁdence intervals for τ 0 = (τ 0
w,τ 0
h)T using the result of Theorem 2.3 and Theorem 2.4.
To avoid redundancy, we only describe part of this estimation process in context of the width
change parameter τ 0
w, the procedure for the height change parameter is symmetrical.
First, in order to alleviate ﬁnite sample regularization biases we utilize reﬁtted mean esti-
mates computed as ˘θ(j) =

¯x(j)(˜τ)

ˆSj j = 1,2,3,4, where ˜τ = (˜τw, ˜τh)T is the change point
estimate of Algorithm 1. Here ˆSj = {k ˆθ(1k) ̸= 0}, j = 1,2,3,4, are the estimated sparsity
sets, where ˆθ(j), j = 1,2,3,4 are the Step 2 mean estimates of Algorithm 1. It is well known
in the literature that reﬁtted mean estimates preserve the rate of convergence of the regular-
ized version while reducing ﬁnite sample biases, see, e.g. [5] and [6]. The jump vector and
individual jump size are then evaluated as ˘η(j) and ˘ξj, j = 1,2,3,4, as plug-in estimates as
per the relations (1.5). The width and height-wise proportions are estimated as the observed
versions, i.e., ˘ωw = (Tw −˜τ 0
w)/Tw and ˘ωh = (Th −˜τh)/Th. The directional jump sizes are
obtained as ˘ξw = ˘ωh˘ξ2
1 + (1 −˘ωh)˘ξ2
4 and symmetrically for ˘ξh.
Next consider the asymptotic variance σ2
(w,∞) of Condition D. Note the ﬁnite sample rep-
resentation of this parameter, ξ−2
w

ωhη0
(1)Ση0
(1) +(1−ωh)η0
(3)Ση0
(3)

. A plug in version ˘σ2
w,∞
is computed by utilizing the above described estimated parameters. The covariance matrix Σ
is estimated as the sample covariance ˘Σ computed by utilizing the entire data set with center-
ing done in correspondence with the estimated mean parameters over quadrants. We note that
since we are not interested in the estimation of the covariance itself but instead the quadratic
form described above, thus utilizing the sample covariance here is effectively identical to
utilizing reﬁtted covariance on the adjacency matrix estimated by the jump vectors ˘η(1), and
˘η(3), in turn making this shortcut valid despite potential high dimensionality.
Finally, regarding quantiles of limiting distributions characterized in Theorem 2.3 and
Theorem 2.4 in the vanishing and non-vanishing regimes, respectively. For the quantiles of
the former case, we utilize the cdf of the underlying distributions which was ﬁrst presented in
[44]. For the latter case, we assume in all calculations that underlying distribution is Gaussian
and consequently the distribution of the increments P of Condition A′ is also Gaussian.
The above estimated parameters are then utilized to produce realizations of this incremental
### Page 59

HD MEANS OVER 2D CHANGES
29
distribution, which are then used to produce realizations of the two-sided random walk and in
turn those of its argmax. The quantiles are then estimated as a monte-carlo approximation.
REFERENCES
[1] ATCHADE, Y. and BYBEE, L. (2017). A Scalable Algorithm for Gaussian Graphical Models with Change-
Points. arXiv preprint arXiv:1707.04306.
[2] BAI, J. (1994). Least squares estimation of a shift in linear processes. Journal of Time Series Analysis 15
453–472.
[3] BAI, J. (1997). Estimation of a change point in multiple regression models. Review of Economics and
Statistics 79 551–563.
[4] BAI, J. (2010). Common breaks in means and variances for panel data. Journal of Econometrics 157 78–92.
[5] BELLONI, A., CHERNOZHUKOV, V. and WANG, L. (2011). Square-root lasso: pivotal recovery of sparse
signals via conic programming. Biometrika 98 791–806.
[6] BELLONI, A., KAUL, A. and ROSENBAUM, M. (2017). Pivotal Estimation via Self-Normalization for High-
Dimensional Linear Models with Error in Variables. arXiv preprint arXiv:1708.08353.
[7] BHATTACHARJEE, M., BANERJEE, M. and MICHAILIDIS, G. (2017). Common change point estima-
tion in panel data from the least squares and maximum likelihood viewpoints. arXiv preprint
arXiv:1708.05836.
[8] BHATTACHARJEE, M., BANERJEE, M. and MICHAILIDIS, G. (2018). Change point estimation in a dy-
namic stochastic block model. arXiv preprint arXiv:1812.03090.
[9] BHATTACHARJEE, M., BANERJEE, M. and MICHAILIDIS, G. (2019). Change Point Estimation in Panel
Data with Temporal and Cross-sectional Dependence. arXiv preprint arXiv:1904.11101.
[10] BICKEL, P. J. (1982). On adaptive estimation. The Annals of Statistics 647–671.
[11] CHIPMAN, H. A., GEORGE, E. I., MCCULLOCH, R. E. et al. (2010). BART: Bayesian additive regression
trees. The Annals of Applied Statistics 4 266–298.
[12] CHO, H. and FRYZLEWICZ, P. (2015). Multiple-change-point detection for high dimensional time series via
sparsiﬁed binary segmentation. Journal of the Royal Statistical Society: Series B (Statistical Method-
ology) 77 475–507.
[13] CHO, H. et al. (2016). Change-point detection in panel data via double CUSUM statistic. Electronic Journal
of Statistics 10 2000–2038.
[14] DONOHO, D. L. (1995). De-noising by soft-thresholding. IEEE transactions on information theory 41 613–
627.
[15] DONOHO, D. L., JOHNSTONE, I. M., KERKYACHARIAN, G. and PICARD, D. (1995). Wavelet shrinkage:
asymptopia? Journal of the Royal Statistical Society: Series B (Methodological) 57 301–337.
[16] DURRETT, R. (2010). Probability: theory and examples. Cambridge university press.
[17] ENIKEEVA, F. and HARCHAOUI, Z. (2013). High-dimensional change-point detection with sparse alterna-
tives. arXiv preprint arXiv:1312.1900.
[18] FRIEDMAN, J., HASTIE, T., TIBSHIRANI, R. et al. (2001). The elements of statistical learning 1. Springer
series in statistics New York.
[19] FRYZLEWICZ, P. (2014). Wild binary segmentation for multiple change-point detection. The Annals of
Statistics 42 2243–2281.
[20] HÁJEK, J. and RÉNYI, A. (1955). Generalization of an inequality of Kolmogorov. Acta Mathematica Hun-
garica 6 281–283.
[21] HARCHAOUI, Z. and LÉVY-LEDUC, C. (2010). Multiple change-point estimation with a total variation
penalty. Journal of the American Statistical Association 105 1480–1493.
[22] HILL, J., LINERO, A. and MURRAY, J. (2020). Bayesian additive regression trees: a review and look for-
ward. Annual Review of Statistics and Its Application 7 251–278.
[23] JIRAK, M. (2015). Uniform change point tests in high dimension. The Annals of Statistics 43 2451–2483.
[24] KAUL, A., DAVIDOV, O. and PEDDADA, S. D. (2017). Structural zeros in high-dimensional data with
applications to microbiome studies. Biostatistics 18 422–433.
[25] KAUL, A., FOTOPOULOS, S. B., JANDHYALA, V. K., SAFIKHANI, A. et al. (2020). Inference on the change
point under a high dimensional sparse mean shift. Electronic Journal of Statistics 15 71–134.
[26] KAUL, A., JANDHYALA, V. K. and FOTOPOULOS, S. B. (2019). An Efﬁcient Two Step Algorithm for High
Dimensional Change Point Regression Models Without Grid Search. Journal of Machine Learning
Research 20 1–40.
[27] KAUL, A., JANDHYALA, V. K. and FOTOPOULOS, S. B. (2019). Detection and estimation of parameters
in high dimensional multiple change point regression models via L1/L0 regularization and discrete
optimization. arXiv preprint arXiv:1906.04396.
### Page 60

30
[28] KAUL, A., ZHANG, H., TSAMPOURAKIS, K. and MICHAILIDIS, G. (2021). Inference on the Change Point
for High Dimensional Dynamic Graphical Models.
[29] ORTELLI, F. and VAN DE GEER, S. (2020). Adaptive Rates for Total Variation Image Denoising. Journal
of Machine Learning Research 21 1–38.
[30] PAGE, E. (1955). A test for a change in a parameter occurring at an unknown point. Biometrika 42 523–527.
[31] RIGOLLET, P. (2015). 18. s997: High dimensional statistics. Lecture Notes), Cambridge, MA, USA: MIT
Open-CourseWare.
[32] ROCKOVA, V., VAN DER PAS, S. et al. (2020). Posterior concentration for Bayesian regression trees and
forests. Annals of Statistics 48.
[33] ROY, S., ATCHADÉ, Y. and MICHAILIDIS, G. (2017). Change point estimation in high dimensional Markov
random-ﬁeld models. Journal of the Royal Statistical Society: Series B (Statistical Methodology) 79
1187–1206.
[34] STELAND, A. (2018). Inference and change detection for high-dimensional time series. In 9th International
Workshop on Simulation 129 130.
[35] VAART, A. W. and WELLNER, J. A. (1996). Weak convergence and empirical processes: with applications
to statistics. Springer.
[36] VENKATRAMAN, E. S. (1993). Consistency results in multiple change-point problems.
[37] VERSHYNIN, R. (2019). High-Dimensional Probability. Cambridge, UK: Cambridge University Press.
[38] WANG, D., LIN, K. and WILLETT, R. (2019). Statistically and computationally efﬁcient change point
localization in regression settings. arXiv preprint arXiv:1906.11364.
[39] WANG, D., YU, Y. and RINALDO, A. (2017). Optimal covariance change point localization in high dimen-
sion. arXiv preprint arXiv:1712.09912.
[40] WANG, D., YU, Y. and RINALDO, A. (2018). Optimal change point detection and localization in sparse
dynamic networks. arXiv preprint arXiv:1809.09602.
[41] WANG, R. and SHAO, X. (2020). Dating the break in high-dimensional data. arXiv preprint
arXiv:2002.04115.
[42] WANG, R., VOLGUSHEV, S. and SHAO, X. (2019). Inference for Change Points in High Dimensional Data.
arXiv preprint arXiv:1905.08446.
[43] WANG, T. and SAMWORTH, R. J. (2018). High dimensional change point estimation via sparse projection.
Journal of the Royal Statistical Society: Series B (Statistical Methodology) 80 57–83.
[44] YAO, Y.-C. (1987). Approximating the distribution of the maximum likelihood estimate of the change-point
in a sequence of independent random variables. The Annals of Statistics 15 1321–1328.