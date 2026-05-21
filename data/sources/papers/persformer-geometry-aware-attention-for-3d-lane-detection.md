# PersFormer Geometry-aware Attention for 3D Lane Detection

**Source**: arxiv PDF, 15 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Exponential decay for Constrained-degree percolation
Diogo C. dos Santos1 and Roger W. C. Silva 2
Abstract
We consider the Constrained-degree percolation model in random environment (CDPRE) on the
square lattice. In this model, each vertex v has an independent random constraint κv which takes
the value j ∈{0, 1, 2, 3} with probability ρj. The dynamics is as follows: at time t = 0 all edges
are closed; each edge e attempts to open at a random time Ue ∼U(0, 1], independently of all other
edges. It succeeds if at time Ue both its end-vertices have degrees strictly smaller than their respec-
tive constraints. We obtain exponential decay of the radius of the open cluster of the origin at all
times when its expected size is finite. Since CDPRE is dominated by Bernoulli percolation, such
result is meaningful only if the supremum of all values of t for which the expected size of the open
cluster of the origin is finite is larger than 1/2. We prove this last fact by showing a sharp phase
transition for an intermediate model.
Keywords: exponential decay; dependent percolation, random environment; infinite range
AMS 1991 subject classification: 60K35; 82B43; 82B26
1
Introduction
Let L2 = (Z2, E) be the usual square lattice. To each site v ∈Z2 we associate independently
a random variable κv which takes the value j ∈{0, 1, 2, 3} with probability ρj. Denote by Pρ the
corresponding product measure on {0, 1, 2, 3}Z2. Consider the following dependent continuous time
percolation process: let {Ue}e∈E be a collection of i.i.d. random variables with uniform distribution
on the interval (0, 1]. At time t = 0 all edges are closed; each edge e = ⟨u, v⟩opens at time Ue if
|{z ∈Z2 −{u}: ⟨z, u⟩is open at time Ue}| < κu and |{z ∈Z2 −{v}: ⟨z, v⟩is open at time Ue}| < κv.
In words, at the random time Ue the edge e attempts to open. It succeeds if both its endpoints have
degrees smaller than their respective attached constraints. Once an edge is open, it remains open.
The model described above draws inspiration from its deterministic constraint version introduced
in [5]. In the deterministic model, constraints are fixed to a constant value κ for every vertex. The
authors of [5] prove a non-trivial phase transition for the model on L2 when κ = 3. In contrast, they
show absence of percolation when κ = 2, even at time t = 1. In a recent paper, see [12], the authors
extend some of the results of [5], proving a phase transition for the model on Ld, d ⩾2, for several
values of a constant deterministic κ. See [8, 10, 11, 14] for other models with some type of constraint.
The random constraint version we approach in this work was initially introduced in [16]. In that
work, the authors show a non-trivial phase transition for the model on L2 when ρ3 is sufficiently large,
thus extending the main result of [5].
1Instituto de Matem´atica, Universidade Federal de Alagoas, Brazil, diogo.santos@im.ufal.br.
2Corresponding Author - Departamento de Estat´ıstica, Universidade Federal de Minas Gerais, Brazil, roger-
wcs@est.ufmg.br.
arXiv:2111.05233v5  [math.PR]  3 Apr 2024
### Page 2

A formal definition of the CDPRE model reads as follows. To each edge e ∈E we assign indepen-
dently a random variable Ue ∼U(0, 1], independent of {κv}v∈Z2. The corresponding product measure
is denoted by P. We think of Ue as the time when edge e attempts to open and usually refer to {Ue}e∈E
as a configuration of clocks. Given a collection of constraints κ = {κv}v∈Z2 and a clock configuration
U = {Ue}e∈E, let
ωt : {0, 1, 2, 3}Z2 × [0, 1]E →{0, 1}E
be the function that associates the pair (κ, U) to a configuration ωt(κ, U) of open and closed edges at
time t. From now on, we use the short notation ωt and denote by ωt,e the status of the edge e in the
configuration ωt. We say an edge e is t-open (t-closed) if ωt,e = 1 (ωt,e = 0). Formally, writing 1A for
the indicator function of the event A and deg(v, t) for the degree of vertex v in ωt, the configuration at
edge e = ⟨u, v⟩is written as
ωt,e = 1{Ue⩽t} × 1{deg(u,Ue)<κu} × 1{deg(v,Ue)<κv}.
Using Harris’ construction, it is straightforward to show that ωt is well defined for almost all se-
quences U = {Ue}e∈E and κ = {κv}v∈Z2 and all t ∈[0, 1]; see discussion after Theorem 2 in [16].
Denote by Pρ,t the pushforward product law governing ωt, that is, for any measurable set A ⊂
{0, 1}E,
Pρ,t(A) = (Pρ × P)(ω−1
t (A)).
What makes this model interesting is that, at any fixed time t > 0, the configurations exhibit
infinite-range dependencies. However, as we will show later, the dependence between the states of
any two edges decays at least exponentially as the distance between them increases (see Proposition 1
in Section 2.1), a fact that will be important in this work.
Remark 1. We stress that the model lacks the FKG property, which makes the analysis significantly harder. For
instance, consider ρ3 = 1 and t > 0. Then, the probability that all four edges incident to some vertex v are open
at time t vanishes, while the probability that any pair of such edges are open at time t remains strictly positive.
1.1
Results and discussion
Before we state our results, let us introduce some notation. A path of L2 is an alternating sequence
v0, e0, v1, e1, . . . , en−1, vn of distinct vertices vj and edges ej = ⟨vj, vj+1⟩. Such a path has length n and
is said to connect v0 to vn. A path is said to be open if all of its edges are open. Write Cv for the open
cluster of v ∈Z2, i.e., the set of vertices connected to v by an open path. By translation invariance of the
probability measure, we take this vertex to be the origin and define the percolation and susceptibility
critical thresholds
tc(ρ) = sup{t ∈[0, 1] : Pρ,t(|C| = ∞) = 0},
¯tc(ρ) = sup{t ∈[0, 1] : Eρ,t(|C|) < ∞},
respectively. Here Eρ,t denotes expectation with respect to Pρ,t. Clearly, ¯tc(ρ) ⩽tc(ρ).
2
### Page 3

Let u, v ∈Z2 and denote by d(u, v) the graph distance between u and v. Write B(n) = [−n, n]2
for the box of side-length 2n centered at the origin. For x ∈Z2, we define B(x, n) = x + B(n). Given
Γ ⊂Z2, we write E(Γ) to denote the set of edges with both endpoints in Γ. We use ∂Γ to denote the
vertex boundary of Γ, being the set of vertices in Γ which are adjacent to some vertex not in Γ. We also
write ∂eΓ for the external edge boundary of Γ, i.e., the set of edges e = ⟨u, v⟩, with u ∈Γ and v /∈Γ.
It is not hard to see that the radius of the open cluster of the CDPRE model decays exponentially
fast when t < 1/2. This follows since the model is stochastically dominated by independent Bernoulli
percolation, and the fact that the radius of the open cluster of the latter model decays exponentially
fast (see [1] and [6]) below its critical threshold (see [13]). Theorem 1 below, whose proof is deferred to
Section 2.2, gives that ¯tc(ρ) (and consequently tc(ρ)) is strictly larger than 1/2. It is therefore natural
to ask: do we have exponential decay for all t smaller than tc(ρ)? We prove exponential decay of
the radius of the open cluster for all t < ¯tc(ρ), giving a partial answer to this question. A nice open
problem consists in proving that the model exhibits a sharp phase transition, i.e., that the radius of the
open cluster decays exponentially fast for all t < tc(ρ). In particular, this would give tc(ρ) = ¯tc(ρ).
Theorem 1. It holds that ¯tc(ρ) > 1
2.
Let θn(t) denote the probability that the origin is connected to ∂B(n) at time t. We omit ρ from the
notation to keep it clean. We will prove the following theorem.
Theorem 2. Let ρ and t < ¯tc(ρ) be given. There exists α > 0 such that
θn(t) ⩽e−αn,
for all n.
In Section 2 we will prove these two theorems. The proof of Theorem 1 is obtained by showing a
sharp phase transition for an intermediate model. The proof of Theorem 2 consists of an application of
a Simon-Lieb type inequality. In Section 3 we present some final remarks and open problems.
2
Proofs
2.1
Proof of Theorem 2
To prove Theorem 2 we will apply a Simon-Lieb type inequality on boxes of several lengths. Ob-
serve that if the origin is connected by an open path to ∂B(4n), then the origin must be connected by
an open path to ∂B(n) and there must exist a vertex w ∈∂B(2n) such that w is connected to ∂B(4n) by
an open path using edges on the complement of B(2n) only. The main difficulty here is to control the
decay of connectivity and the decay of correlations between events whose occurrence depends only
on the state of edges inside B(n) and those depending on the state of edges outside B(2n). We observe
that the decay of correlations obtained in Theorem 2 of [16] is no longer enough here, and we derive a
new decay rate which is improved by a log n factor.
3
### Page 4

In what follows, the notation {w
A
←−−→B} means that the vertex w is connected to some vertex
in B using only edges with both endpoints in A. All constants c1, c2, c3, c4 appearing in this section are
universal and do not depend on n or t.
Proposition 1. Fix m, n ∈N such that 2m < n and w ∈∂B(2m). Then,
Pρ,t

0 ←→∂B(m), w
B(2m)c
←−−→∂B(n)

⩽
Pρ,t(0 ←→∂B(m))Pρ,t (w ←→∂B(n))
+
c1m exp
 −1
2m log m

,
for all ρ = (ρ0, ρ1, ρ2, ρ3) and t ∈[0, 1].
Proof. We follow the argument in Section 2.1 of [3]. Fix t > 0 and let Mt(x) be the set of vertices y such
that there is a path x, e1, x1, e2, x2 . . . , ek, y with t > U(e1) > U(e2) > · · · > U(ek). This gives, with the
aid of Stirling’s formula,
Pρ,t(Mt(x) ∩{x + ∂B(m)} ̸= ∅) ⩽4 × 3m−1
m!
⩽1
2 exp

−m log
 m
3e

.
(1)
The first inequality in (1) holds since, if {Mt(x) ∩{x + ∂B(m)} ̸= ∅)} occurs, then there must exist
a self-avoiding path of length m starting at x such that all clocks ring in order before time t.
Write Mt(∂B(n)) = S
x∈∂B(n) Mt(x) and let w ∈∂B(2m). Union bound and (1) yields
Pρ,t (Mt(∂B(m)) ∩Mt(w) ̸= ∅) ⩽2Pρ,t (Mt(∂B(m)) ∩∂B(⌊3m/2⌋) ̸= ∅)
⩽c1m exp
 −1
2m log m

,
for m > 9e2. Note that on {Mt(∂B(m)) ∩Mt(w) = ∅}, the events {0 ←→∂B(m)} and {w
B(2m)c
←−−→
∂B(n)} are determined by disjoint sets of edges and hence the covariance vanishes. Therefore, we
obtain
Cov

1{0 ←→∂B(m)},1{w
B(2m)c
←−−→∂B(n)}

⩽c1m exp
 −1
2m log m

.
The proof follows by observing that
Pρ,t

0 ←→∂B(m), w
B(2m)c
←−−→∂B(n)

⩽Pρ,t(0 ←→∂B(m))Pρ,t (w ←→∂B(n))
+ Cov

1{0 ←→∂B(m)},1{w
B(2m)c
←−−→∂B(n)}

.
Proof of Theorem 2. Fix ρ, t < ¯tc(ρ), and write θn(t) ≡θn. Following the discussion at the beginning of
this section, let us consider boxes of side length 2⌊√n⌋. We have
θn ⩽Pρ,t

0 ←→∂B(⌊√
n⌋), ∃w ∈∂B(2⌊√
n⌋) s.t. {w
B(2⌊√n⌋)c
←−−→∂B(n)}

.
4
### Page 5

Applying union bound and then Proposition 1, we have
θn ⩽θ⌊√n⌋


∑
w∈∂B(2⌊√n⌋)
Pρ,t(w ←→∂B(n))

+ c1n exp
 −1
2⌊√
n⌋log⌊√
n⌋

.
(2)
By translation invariance it holds
Pρ,t(w ←→∂B(n)) ⩽θn−2⌊√n⌋,
for any w ∈∂B(2⌊√n⌋). Hence
θn ⩽16⌊√
n⌋θ⌊√n⌋θn−2⌊√n⌋+ c1n exp
 −1
2⌊√
n⌋log⌊√
n⌋

.
Iterating the above 1
2⌊√n⌋times and using the same argument for θn−2j⌊√n⌋, j ∈{1, 2, . . . , 1
2⌊√n⌋}, we
obtain
θn ⩽

c2⌊√
n⌋θ⌊√n⌋
 1
2 ⌊√n⌋
+ c1n exp
 −1
2⌊√
n⌋log⌊√
n⌋
 ⌊√n⌋−1
∑
i=0

c2⌊√
n⌋θ⌊√n⌋
i
.
(3)
It is easy to see that, if Eρ,t(|C|) < ∞, then ∑n⩾1 θn(t) < ∞. Since {θn(t)}n is decreasing, an exercise
in analysis gives
lim
n→∞nθn(t) = 0.
(4)
Hence we can find some n0 ∈N such that
c2⌊√
n⌋θ⌊√n⌋< e−2,
for all n ⩾n0. This gives
θn ⩽exp
 −√
n
 + c3n exp
 −1
2⌊√
n⌋log⌊√
n⌋

,
for all n ⩾n0. Note that
c2n exp
 −1
2⌊√
n⌋log⌊√
n⌋

=
exp
(
−
"
⌊√n⌋
2
+
 log⌊√n⌋−1
 ⌊√n⌋
2
−log (c3n)
#)
⩽
exp
 −1
4
√
n

,
for all n large enough, and hence
θn ⩽2 exp

−1
4n
1
2

.
(5)
The same reasoning yields, for any n, k ∈N,
θ2(k+1)n ⩽c4nθnθ2kn + c4n exp

−1
2n log n

.
5
### Page 6

We claim that
θ2kN ⩽
1
2kαkc4Nk ,
(6)
for several but finitely many k = 1, 2, . . . , kmax. Here α > 1 can be taken any fixed number, e.g. α = 2.
Also, the number kmax will be established below, but it suffices that kmax ⩾7.
Equation (5) implies the existence of a large fixed N ∈N, and of some constant c3 such that
θN ⩽
1
4αc4N2 .
Since θn is non-increasing, we have θ2N ⩽θN, and (6) follows when k = 1. For all such k that
c4N exp

−1
2 N log N

⩽1
2 ×
1
2k+1αk+1c3Nk+1 ,
(solving this we find kmax) we obtain
θ2(k+1)N ⩽
c4N
(4αc4N2)(2kαkc4Nk) + c4N exp

−1
2 N log N

⩽
1
2k+1αk+1c4Nk+1 .
In particular, loosening on the upper bound θ2kN ⩽1/(2kαkc4Nk), we have that
i) for m ∈{2N, 4N, . . . , 2kmaxN} we have θm ⩽α−m/(2N),
ii) letting 2kmaxN = N′ and α′ = αkmax, we have θN′ ⩽
1
4α′c4(N′)2 .
Item ii) follows since if kmax ⩾7, then 2kmax Nkmax ⩾4(2kmaxN)2. Repeating the same argument with
N′ and α′ one obtains a new set of values m ∈{2N′, . . . , 2kmaxN′}, for which θm ⩽(α′)−m/(2N′) =
α−m/(2N). Continuing inductively we obtain an infinite subsequence m1, m2, . . . , with the property that
mj+1 ⩽2mj for all j ∈N, such that θmj ⩽α−mj/(2N). Since θn is non-increasing in n, it follows that
θn ⩽α−n/(4N), for all n > N.
2.2
Proof of Theorem 1
In this section we prove Theorem 1. We break the proof in two parts, assuming first that 0 < ρ0 < 1.
Let {U(e)}e∈E and {κv}v∈Z2 be given. Define a new percolation configuration ηt at edge e = ⟨u, v⟩as
ηt,e =
(
1{U(e)⩽t}
if
v = u + (0, 1) ,
1{U(e)⩽t}1{κu̸=0}
if
v = u + (1, 0).
(7)
This corresponds to a percolation model where vertical edges are independently open with probability
t and horizontal edges are independently open with probability t(1 −ρ0).
Let bωt denote an independent Bernoulli bond percolation configuration with parameter t. Then,
according to the terminology used in [2] and [4], ηt is an essential diminishment of bωt, in the sense
that there exists a configuration such that bωt(U) have a doubly-infinite open path but such that a
6
### Page 7

doubly-infinite open path is not present after the diminishment is activated at the origin. To see this,
take a Bernoulli configuration bωt and consider the following rule. To each vertex u ∈Z2, activate a
diminishment at u with probability (1 −ρ0). If the diminishment is activated at u, then delete the edge
v = u + (1, 0). This is clearly an essential diminishment and the diminished configuration has the
same law as ηt. Consequently, based on the results in [2] and [4], the critical threshold for the model
(7) strictly increases and is therefore larger than 1/2. Moreover, due to the stochastic dominance of
the random variable ωt,e by ηt,e, the desired result can be derived from the sharpness of the phase
transition observed for independent inhomogeneous Bernoulli percolation (see [1]).
We turn to the case ρ0 = 0. Based on ideas from [5], we construct an intermediate model that
dominates the CDPRE process when ρ0 = 0 and is dominated by independent Bernoulli percolation.
We will show that the intermediate model phase transition is sharp, which will give us the desired
result.
Let Λ = {(x1, x2) ∈Z2 : x1 = 0, 1, 2, 3, 4, 5 and x2 = 0, 1, 2, 3, 4} and Λ = {(x1, x2) ∈Z2 : x1 =
1, 2, 3, 4 and x2 = 1, 2, 3}. For each (r, s) ∈Z2, define Λr,s = Λ + (6r, 5s) and Λr,s = Λ + (6r, 5s).
Consider the following sets of edges in E(Λr,s):
gr,s = ⟨(6r + 2, 5s + 2), (6r + 3, 5s + 2)⟩,
Ar,s = {e ∈E(Λr,s) : |e ∩∂Λr,s| = 1}.
Br,s = E(Λr,s) \ (gr,s ∪Ar,s).
(r, s)
gr,s
Figure 1: Λr,s (larger box), Λr,s (gray box) and the edge gr,s. Ar,s consists of the dashed edges.
The intermediate model is constructed as follows: let {Ue}e∈E be an independent collection of
uniform random variables on [0, 1] with corresponding product measure P and define the event
Cr,s =

U ∈[0, 1]E : max
e∈Ar,s
U(e) <
min
e∈E(Λr,s)\Ar,s
U(e)

.
See Figure 1 for a sketch of the boxes and edges involved in the construction.
7
### Page 8

A configuration of the intermediate model is a function
eωt : [0, 1]E −→{0, 1}E
such that
eωt,e =
(
1{U(e)⩽t}
if
e /∈∪r,s{gr,s} ,
1{U(e)⩽t}1Ccr,s
if
e = gr,s.
(8)
Note that this has the effect of ”diminishing” the percolation configuration by changing the state of
some edges from t-open to t-closed. We note that there are no constraints in the intermediate model.
Write ˆtc and ˜tc for the susceptibility critical thresholds (the supremum of t ∈[0, 1] such that the mean
size of the open cluster is finite a.s.) of Bernoulli percolation and the intermediate model, respectively.
Note that eωt,e can be obtained through a standard coupling (using the same variables U(e)) with the
CDPRE model. In particular, we obtain eωt,e ⩾ωt,e for all t ∈[0, 1] and for all e ∈E, whenever ρ0 = 0.
Denoting an independent Bernoulli configuration of parameter t by bωt, we observe that eωt is an
essential diminishment of bωt. More precisely, let W = {x ∈Z2 : x = (4r + 1, 3s + 1) for some (r, s)},
that is, W consists of those vertices that are left-end points of some gr,s, and consider making a dimin-
ishment at each vertex x ∈W. Let η = (η(x) : x ∈W) be a vector lying in the space Ξ = {0, 1}W,
where we interpret the value η(x) = 1 as meaning that the diminishment at x is activated. Assuming
that the random variables {η(x)}x∈W are i.i.d. Bernoulli with mean γ = 1, then, when activated, the
diminishment acts on Λr,s by deleting the edge gr,s ,whenever Cr,s occurs. Therefore, a second applica-
tion of the main result in [2] and [4] gives that the critical threshold of the intermediate model is strictly
larger than 1/2.
Assuming that the intermediate model phase transition is sharp, we have the inequality
1
2 = ˆtc < ˜tc.
Since the CDPRE model is dominated by the intermediate model, this gives
1
2 < ˜tc ⩽¯tc(ρ),
for all ρ with ρ0 = 0.
Remark 2. We observe that the domination argument described above does not hold when ρ0 > 0. For instance,
suppose κ(2,3) = 0 and κ(2,2) = κ(3,2) = 3. If C0,0 occurs, then eωt(g0,0) = 0 whilst ωt,g0,0 = 1.
Based on the ideas developed in [7], we will prove sharpness of the phase transition for the in-
termediate model with an application of the OSSS inequality for boolean functions and a suitable
randomized algorithm.
Let us introduce further notation. Assume I is a countable set, and let (ΩI, π⊗I) be a product
probability space with elements denoted by ω = (ωi)i∈I. Consider a boolean function f : ΩI →{0, 1}.
An algorithm T determining f takes a configuration ω as an input, and reveals the value of ω in
8
### Page 9

different coordinates, one by one. At each step, the next coordinate to be revealed depends on the
values of ω revealed so far. This process keeps going until the value of f is the same no matter the
values of ω on the remaining coordinates. For a formal description of a randomized algorithm we
refer the reader to [15].
Denote by δi(T) and Infi( f ) the revealment and the influence of the i-th coordinate, respectively,
which are defined by
δi(T) := π⊗I(T reveals the value of ωi),
Infi( f ) := π⊗I( f (ω) ̸= f (ω∗)),
where ω∗is equal to ω in every coordinate, except the i-th coordinate which is resampled indepen-
dently. The OSSS inequality, introduced in [15] by O’Donnel, Saks, Schramm and Servedio, gives a
bound on the variance of f in terms of the influence and the computational complexity of an algorithm
for this function. It says that, for any function f : ΩI →{0, 1} and any algorithm T determining f,
Var( f ) ⩽∑
i∈I
δi(T)Infi( f ).
(9)
The intermediate model is a 5-dependent percolation process and the OSSS inequality can not be
directly applied. To overcome this difficulty, we introduce a suitable product space to encode the
measure of the intermediate model. We take Ω= [0, 1], I = E and π⊗I = P. Writing Bn = {0 ←→
∂B(n)}, we are interested in bounding the variance of the boolean function 1 eω−1
t
(Bn) considered as a
function from [0, 1]E onto {0, 1}.
2.2.1
Bound on the revealment
Recall the definition of eωt in (8) and denote by ePt the law of the intermediate model, that is,
ePt(A) = P(U ∈[0, 1]E : eωt(U) ∈A),
for all A ⊂{0, 1}E. Write eθn(t) = ePt(Bn) and Sn(t) = ∑n
k=1 eθk(t). The next lemma shows the existence
of an algorithm determining the boolean function 1 eω−1
t
(Bn) and gives an upper bound on its revealment.
For each (r, s) ∈Z2, write gr,s = ⟨ur,s, vr,s⟩.
Lemma 1. For any k ∈{0, . . . , n}, there exists an algorithm Tk determining 1 eω−1
t
(Bn) with the property that,
for each e = ⟨x1, x2⟩∈E,
δe(Tk) ⩽∑
i=1,2
ePt(xi ↔∂B(k)) + 1Λr,s(e)
h
ePt(ur,s ↔∂B(k)) + ePt(vr,s ↔∂B(k))
i
.
(10)
Once Lemma 10 is proved, observe that, for any x ∈B(n), by summing (10) over k, we get
n
∑
k=1
ePt(xi ↔∂B(k)) ⩽
n
∑
k=1
ePt(xi ←→∂B(xi, d(xi, ∂B(k)))) ⩽2Sn(t),
(11)
9
### Page 10

where the last inequality follows by translation invariance. Plugging (11) in (10) yields
n
∑
k=1
δe(Tk) ⩽βSn(t),
(12)
for some constant β > 0.
Let Fn denote the set of edges between two vertices within distance n of the origin. We define our
algorithm using two growing sequences ∂B(k) = Z0 ⊂Z1 ⊂· · · ⊂Z2 and ∅= F0 ⊂F1 ⊂· · · ⊂Fn. At
step m, we see Zm as representing the set of vertices that the algorithm found to be connected to ∂B(k),
and Fm as the set of edges explored by the algorithm.
Definition 1 (Algorithm Tk). The algorithm Tk is defined as follows. Let e1, e2, . . . be a fixed ordering of the
edges in En. Write F0 = ∅and Z0 = ∂B(k). Assume Zm ⊂Z2 and Fm ⊂En are given.
1. If there is an edge e = ⟨x, y⟩∈En \ Fm with x ∈Zm and y /∈Zm, choose the earliest one according to the
fixed ordering, set Fm+1 = Fm ∪{e} and write
Zm+1 =
(
Zm ∪{y}
if
ωt,e = 1,
Zm
otherwise.
2. If such e does not exist, write Zm+1 = Zm and Fm+1 = Fm ∪{e}.
Note that, as long as we are in the first case, we are still discovering the connected component of
∂B(k). On the other hand, as soon as we are in the second case, we remain at it. Also, observe that the
event where the origin is connected to the boundary of B(n) is already determined before we leave the
first case. We are ready to prove Lemma 1.
Proof of Lemma 1. First, note that the algorithm Tk discovers the union of all open components of ∂B(k)
at time t, in particular it determines the function 1 eω−1
t
(Bn). Observe that e = ⟨x, y⟩∈Λr,s is revealed
if and only if either x, y, ur,s or vr,s are connected by a t-open path to ∂B(k). Indeed, to determine the
status of gr,s all egdes in Λr,s must be revealed. If e /∈Λr,s for all (r, s), then e is revealed if and only if
x or y are connected to ∂B(k). This completes the proof.
2.2.2
A Russo’s type formula
As before, let Bn be the event that the origin is connected to the boundary of the box B(n). We have
the following Russo’s type formula.
Lemma 2. Let 0 < α1 < α2 < 1. There exists a constant q > 0 such that, for all t ∈[α1, α2],
d
dt
ePt(Bn) ⩾q
∑
e∈E(B(n))
ePt (e is pivotal for Bn) .
10
### Page 11

Proof. Let δ > 0. Then,
ePt+δ(Bn) −ePt(Bn) = P ( eωt+δ ∈Bn, eωt /∈Bn)
= P( eωt+δ ∈Bn, eωt /∈Bn, ∃e ∈E(Bn) s.t. t < U(e) ⩽t + δ).
(13)
Let Wt,δ be the random set of edges f such that t < U( f ) ⩽t + δ. Clearly,
P(|Wt,δ| ⩾2) = o(δ).
(14)
From (13) and (14) we obtain
ePt+δ(Bn) −ePt(Bn) = P( eωt+δ ∈Bn, eωt /∈Bn, |Wt,δ| = 1) + o(δ)
=
∑
e∈E(B(n))
P ( eωt+δ ∈Bn, eωt /∈Bn, Wt,δ = {e}) + o(δ).
We now consider three cases. Remember that E(Λr,s) = {gr,s} ∪Ar,s ∪Br,s. First, let e ∈E(B(n)) −
S
r,s E(Λr,s). Then,
P ( eωt+δ ∈Bn, eωt /∈Bn, Wt,δ = {e}) = P( e is pivotal for Bn in eωt, Wt,δ = {e}) + o(δ)
= δ × P( e is pivotal for Bn in eωt) + o(δ)
= δ × ePt( e is pivotal for Bn) + o(δ).
Now let e = gr,s = ⟨ur,s, vr,s⟩for some pair (r, s). Consider the event X = {U(⟨vr,s, vr,s + (1, 0)⟩) >
t + δ}. This gives the inclusion
{ eωt+δ ∈Bn, eωt /∈Bn, Wt,δ = {e}} ⊃{X, e is pivotal for Bn in eωt, Wt,δ = {e}} .
Note that the event X ∩{ e is pivotal for Bn in eωt} depends only on the variables U( f ) with f ̸= gr,s.
Hence
P(X, e is pivotal for Bn in eωt, Wt,δ = {e}) = P(X, e is pivotal for Bn in eωt)P(Wt,δ = {e}).
Since P(X| e is pivotal for Bn in eωt) > 0 for all t ∈[α1, α2], and since the function t →P( eωt ∈A) is
continuous for any local event A, Weierstrass Theorem implies the existence of a constant M1 > 0 such
that
P(X, e is pivotal for Bn in eωt, Wt,δ = {e}) ⩾M1δ × ePt( e is pivotal for Bn).
Finally, let e ∈Ar,s ∪Br,s and denote Y = {U(gr,s) > t}. Note that
{ eωt+δ ∈Bn, eωt /∈Bn, Wt,δ = {e}} = { e is pivotal for Bn in eωt, Wt,δ = {e}}
⊃{Y, e is pivotal for Bn in eωt, Wt,δ = {e}} .
11
### Page 12

Note that the event Y ∩{ e is pivotal for Bn in eωt} depends only on the variables U( f ) with f ̸= e.
Therefore, as in the previous case, there exists a constant M2 > 0 such that
P (Y, e is pivotal for Bn in eωt, Wt,δ = {e}) = P(Y, e is pivotal for Bn in eωt)P(Wt,δ = {e})
⩾M2δ × ePt(e is pivotal for Bn).
Taking q = min{M1, M2} we obtain
ePt+δ(Bn) −ePt(Bn) ⩾δq
∑
e∈E(B(n))
ePt(e is pivotal for Bn) + o(δ).
The result follows by dividing both sides by δ and taking the limit when δ goes to zero.
2.2.3
A bound on the influences
We now seek for a bound on the influence of an edge e ∈E(B(n)) on 1Bn, that is, we seek for a
bound on
Infe(1Bn) := P (U : 1Bn( eωt(U)) ̸= 1Bn( eωt(U∗))) ,
where U is equal to U∗in every edge, except edge e which is resampled independently. We do this
in two steps. First, assume e ∈E(Γ) −S
r,s E(Λr,s) or e = gr,s for some pair (r, s). In this case, the
probability that the state of the indicator function change is
Infe(1Bn) = P (U(e) > t, U∗(e) < t, e is pivotal for Bn) + P (U(e) < t, U∗(e) > t, e is pivotal for Bn)
⩽2 ePt(e is pivotal for Bn).
Now let e ∈E(Λr,s) \ gr,s. In this case,
Infe(1Bn) ⩽P
 U : 1Bn( eωt(U)) ̸= 1Bn( eωt(U∗)), Ugr,s > t

+ P (U : 1Bn( eωt(U)) ̸= 1Bn( eωt(U∗)), U(gr,s) ⩽t) .
If U(gr,s) > t and the indicator of Bn is changed, then e must be pivotal for Bn. If U(gr,s) ⩽t and the
indicator of Bn is changed, then either e or gr,s must be pivotal for Bn. Putting all together, we obtain
∑
e∈B(n)
Infe(1Bn) ⩽γ ∑
e∈B(n)
ePt(e is pivotal for Bn),
(15)
for some constant γ > 0.
Let t∗
c denote the percolation critical threshold for the intermediate model. By stochastic dominance
and the results of [5] we know that 1/2 < t∗
c < 1. We now prove that the intermediate model undergoes
a sharp phase transition, a fact from which Theorem 1 is a corollary.
12
### Page 13

Theorem 3. Consider the intermediate model on Z2.
1. For t < t∗
c, there exists ct > 0 such that for all n ⩾1, eθn(t) ⩽exp(−ctn).
2. There exists c > 0 such that for t > t∗
c, ePt(0 ←→∞) ⩾c(t −t∗
c).
Proof. Applying the OSSS inequality (9) for each k and then summing on k, Equation (12) gives
eθn(t)(1 −eθn(t)) ⩽βSn(t)
n
∑
e∈B(n)
Infe(1Bn).
Equation (15) and Lemma 2 give
∑
e∈E(B(n))
Infe(1Bn) ⩽γq−1 d
dt
eθt(n).
Hence, there is a constant ν > 0 such that
d
dt
eθn(t) ⩾
νn
Sn(t)
eθn(t)(1 −eθn(t)).
Fix t0 ∈(t∗
c, α2). Since eθn(t) is increasing in t and n, we have 1 −eθn(t) ⩾1 −eθ1(t0) for all t ⩽t0. The
result follows with an application of Lemma 3 in [7] to the function fn =
eθn(t)
ν(1−eθ1(t0)).
3
Final remarks
We finish this paper with a few remarks and also with some unanswered questions.
1. Does tc(ρ) = ¯tc(ρ) hold for any ρ = (ρ0, ρ1, ρ2, ρ3)?
One could tackle this problem by showing a sharp phase transition for the CDPRE model, meaning
that the radius of the open cluster decays exponentially fast for all t < tc(ρ). The OSSS method of H.
Duminil-Copin, A. Raoufi and V. Tassion (see [7] for example) emerges as a promising tool to prove
such decay. On one hand, there is a small and well-controlled probability that one needs to look at
a far away edge to see what the state of a fixed edge f is (because the sequence of U(e) needs to be
decreasing; see also Proposition 1). Hence, when exploring, it should not be difficult to explore the
cluster plus what we need to explore to determine f. On the other hand, proving a Margulis-Russo
type formula seems problematic, given that events of interest are not even monotone in the uniform
variables and that the 0-1 variables do not vary nicely in terms of the parameter.
2. Does the statement of Theorem 2 hold for d > 2?
13
### Page 14

If we take d > 2, then there would be an entropy factor of order nd−1 in the first term on the r.h.s.
of (3). In this case we would not have (4), which is crucial for our estimate.
3. Assume ρ stochastically dominates ˜ρ. Does tc(ρ) ⩽tc( ˜ρ) hold?
Acknowledgements
We are grateful to R´emy Sanchis for several valuable discussions. Diogo C. dos Santos was par-
tially supported by PNPD/CAPES. Roger Silva was partially supported by FAPEMIG (Universal APQ-
00774-21). This study was financed in part by the Coordenac¸˜ao de Aperfeic¸oamento de Pessoal de
N´ıvel Superior – Brasil (CAPES) – Finance Code 001.
References
[1] Aizenman, M. and Barsky, D.J.: Sharpness of the phase transition in percolation models. Commun.
Math. Phys. 108, (1987), 489–526.
[2] Aizenman, M. and Grimmett, G: Strict monotonicity for critical points in percolation and ferro-
magnetic models. Journal of Statistical Physics 63, (1991), 817–835.
[3] Amir, G. and Baldasso, R.: Percolation in majority dynamics. Electron. J. Probab. 25, (2020), 1–18.
[4] Balister, P., Bollob´as, B. and Riordan, O.: Essential enhancements revisited. arxiv:1402.0834v1.
[5] de Lima, B.N.B, Sanchis, R., dos Santos, D.C., Sidoravicius, V. and Teodoro, R.: The Constrained-
degree percolation model. Stoch Process Their Appl. 130, (2020), 5492–5509.
[6] Duminil-Copin, H. and Tassion, V.: A new proof of the sharpness of the phase transition for
Bernoulli percolation on Zd. L’enseignement math´ematique 62, (2016), 199–206.
[7] Duminil-Copin, H., Raoufi, A. and Tassion, V.: Exponential decay of connection probabilities for
subcritical Voronoi percolation in Rd. Probab. Theory Relat. Fields 173, (2019), 479–490.
[8] Garet, O., Marchand, R. and Marcovici, I.: Does Eulerian percolation on Z2 percolate? ALEA 15,
(2018), 279–294.
[9] Grimmett, G.: Percolation, 2nd ed., Springer, Berlin (1999).
[10] Grimmett, G. and Janson, S.: Random graphs with forbidden vertex degrees. Random Struct. Alg.
37, (2010), 137–175.
[11] Grimmett, G. and Li, Z.: The 1-2 model. Contemp. Math. 969, (2017), 139–152.
[12] Hartarsky, I. and de Lima, B.N.B.: Weakly constrained-degree percolation on the hypercubic lat-
tice. Stoch Process Their Appl. 153, (2022), 128–144.
14
### Page 15

[13] Kesten, H.: The critical probability of bond percolation on the square lattice equals 1/2. Commun.
Math. Phys. 74, (1980), 41–59.
[14] Li, Z.: Constrained percolation, Ising model, and XOR Ising model on planar lattices. Random
Struct. Alg. 57, (2020), 474–525.
[15] O‘Donnell, R., Saks, M., Schramm, O. and Servedio, R.A.: Every decision tree has an influential
variable. In: 46th Annual IEEE Symposium on Foundations of Computer Science, IEEE, (2005), 31–39.
[16] Sanchis, R., dos Santos, D.C. and Silva, R.W.C.: Constrained-degree percolation in random envi-
ronment. Ann. inst. Henri Poincare (B) Probab. Stat. 58, (2022), 1887–1899.
15