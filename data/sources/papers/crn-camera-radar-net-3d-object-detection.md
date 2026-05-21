# CRN Camera Radar Net 3D Object Detection

**Source**: arxiv PDF, 18 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

arXiv:2209.09826v2  [cond-mat.stat-mech]  28 Nov 2023
Thermalization without eigenstate thermalization
Aram W. Harrow∗1 and Yichen Huang (黄溢辰)†1,2
1Center for Theoretical Physics, Massachusetts Institute of Technology,
Cambridge, Massachusetts 02139, USA
2Department of Physics, Harvard University, Cambridge, Massachusetts
02138, USA
November 30, 2023
Abstract
In an isolated quantum many-body system undergoing unitary evolution, we study
the thermalization of a subsystem, treating the rest of the system as a bath. In this
setting, the eigenstate thermalization hypothesis (ETH) was proposed to explain ther-
malization. Consider a nearly integrable Sachdev-Ye-Kitaev model obtained by adding
random all-to-all 4-body interactions as a perturbation to a random free-fermion model.
When the subsystem size is larger than the square root of but is still a vanishing frac-
tion of the system size, we prove thermalization if the system is initialized in a random
product state, while almost all eigenstates violate the ETH. In this sense, the ETH is
not a necessary condition for thermalization.
Preprint number: MIT-CTP/5467
1
Introduction
1.1
Background
Thermalization is a fundamental process in nature. It says that a system in contact with
a bath tends to evolve to a Gibbs state described by the canonical ensemble. Suppose an
isolated quantum many-body system is initialized in a pure state. Under unitary evolution
the system stays in a pure state and never thermalizes. To study thermalization, we divide
the system into two parts A and ¯A such that subsystem A is much smaller than ¯A. We
view ¯A as a bath of A and consider the thermalization of A, i.e., whether physical properties
measured on A evolve to those of a Gibbs state.
An important goal of statistical mechanics is to understand the mechanism of thermal-
ization. One proposal is the eigenstate thermalization hypothesis (ETH) [1–4].
∗aram@mit.edu
†yichenhuang@fas.harvard.edu
1
### Page 2

Deﬁnition 1. A state is A-thermal if its reduced density matrix for subsystem A is approx-
imately equal to1 that of a Gibbs state with the same energy.
Deﬁnition 2 (eigenstate thermalization hypothesis). An eigenstate obeys the ETH with
respect to subsystem A if it is A-thermal.
An important feature of this deﬁnition is the size of subsystem A. If a state is A-thermal
for all subsystems A of size L, then its L-point correlation functions are approximately equal
to those of the Gibbs state. In the literature, the ETH is often deﬁned only for L = O(1).
However, even some simple and experimentally accessible observables require considering L’s
that grow with the system size N. The scaling of L with N will be discussed in the context
of the ETH in Subsection 1.3.
Deﬁnition 2 refers only to individual eigenstates, but one might also want to discuss the
ETH for systems (i.e., Hamiltonians). In the literature, the term “strong ETH” or “weak
ETH” [5–7], respectively, refers to systems where all or almost all eigenstates (possibly within
some energy interval) obey the ETH. In this paper, unless otherwise noted, statements about
the ETH refer to individual eigenstates.
For a Hamiltonian H, let |Ψ0⟩and |Ψt⟩:= e−iHt|Ψ0⟩be the initial and time-evolved
states, respectively.
Deﬁnition 3 (thermalization). Thermalization means that |Ψt⟩becomes A-thermal as t
grows.
We present a well-known argument [8–10] for “ETH implies thermalization” based on
two assumptions.
Assumption 1. The spectrum of H is non-degenerate (all eigenvalues are distinct).
Remark. Intuitively, this assumption is usually valid if H does not have any symmetry.
Rigorously, it holds with probability 1 if H is a random Hamiltonian from the Gaussian
unitary ensemble. It also holds for almost every local Hamiltonian on a lattice [6].
Let |1⟩, |2⟩, . . . be a complete set of eigenstates of H with corresponding energies E1, E2, . . ..
Assumption 2. The energy distribution of |Ψ0⟩is sharply peaked around the mean E :=
⟨Ψ0|H|Ψ0⟩in the sense that
X
j: Ej≈E
pj ≈1,
pj :=
⟨j|Ψ0⟩
2.
(1)
Remark. If H is a local Hamiltonian on a lattice, (1) with explicit error bounds was proved
for any |Ψ0⟩with exponential decay of correlations [11].
Assumption 1 implies that the time-averaged state
¯Ψ := lim
τ→∞
1
τ
Z τ
0
|Ψt⟩⟨Ψt| dt =
X
j
pj|j⟩⟨j|
(2)
1More precisely, “approximately equal to” means that the trace distance between the two reduced density
matrices vanishes in the thermodynamic limit.
2
### Page 3

is obtained by dephasing |Ψ0⟩in the energy eigenbasis. Then, Assumption 2 implies that
¯Ψ ≈
X
j: Ej≈E
pj|j⟩⟨j|.
(3)
If every |j⟩in the sum on the right-hand side is A-thermal, then ¯Ψ is A-thermal.
To establish thermalization, it is necessary that ¯Ψ is A-thermal. Furthermore, one needs
to prove equilibration, i.e., the temporal ﬂuctuation of the reduced density matrix of |Ψt⟩
for subsystem A is small. This can be done under mild additional assumptions [12–14].
Question 1. Is the ETH a necessary condition for thermalization?
A positive answer to this question would further justify the essence of the ETH as an
explanation for the emergence of the canonical ensemble from unitary evolution.
If the
answer is negative, then it is time to call for other mechanisms of thermalization. Either
way Question 1 is illuminating.
The answer to Question 1 depends on the set of initial states under consideration. If
the initial state is an eigenstate, then the system does not evolve and thus thermalization
trivially implies the ETH. However, eigenstates of local Hamiltonians typically have very high
complexity and cannot be eﬃciently prepared; they could also be considered “ﬁne tuned”
since they form a discrete set.
De Palma et al. [15] considered initial states of the form |ΨA⟩⊗|Ψ ¯
A⟩, where |ΨA⟩is an
arbitrary pure state of subsystem A; |Ψ ¯
A⟩has a sharply peaked energy distribution but is
otherwise arbitrary. If all such initial states thermalize, the ETH was proved under some
assumptions, one of which is that the Hilbert space dimension of A is much smaller than
the heat capacity of ¯A. In a system of N qubits, if the heat capacity is extensive, this
assumption implies that L ≲ln N, where L is the number of qubits in A. This means that
almost all qubits are in ¯A. Since the states |Ψ ¯
A⟩are so general, they typically have very
high complexity.
The results of Ref. [15] can be rephrased as saying that a system violating the ETH must
fail to thermalize for at least one initial state of the form |ΨA⟩⊗|Ψ ¯
A⟩, where the size of A
is small and |Ψ ¯
A⟩has a sharply peaked energy distribution. This leaves open the question
of whether typical low-complexity initial states thermalize.
We will analyze initial states that are product across all cuts, not only the cut between
A and ¯A. This choice is because these states are more relevant to experiments and are more
plausible models of naturally occurring states.
1.2
Results (informal)
In this paper, we consider a nearly integrable complex Sachdev-Ye-Kitaev (SYK) model in
a system of N (Dirac) fermionic modes. The model has fermion number conservation and
is obtained by adding random all-to-all 4-body interactions as a perturbation to a random
free-fermion model.
If the perturbation is suﬃciently small, the eigenstates are close to
random Gaussian states with deﬁnite fermion number. We prove that they obey and violate
the ETH with overwhelming probability for L ≪
√
N and L ≳
√
N, respectively, where L
is the number of fermionic modes in subsystem A. (We write x ≪y if x/y →0 as N →∞;
3
### Page 4

Table 1: Summary of results in the thermodynamic limit N →∞. L is the subsystem size.
While eigenstate thermalization is a static property of the Hamiltonian, thermalization and
entanglement thermalization are dynamic processes, in which the initial state is a (random)
product state. Smiley (frown) means that the phenomenon in the column occurs (does not
occur) when N and L satisfy the relation in the row. “Thermalization without eigenstate
thermalization” is proved for
√
N ≲L ≪N/ ln N.
eigenstate
thermalization
entanglement
thermalization
thermalization
(Deﬁnition 2)
(Deﬁnition 3)
(Deﬁnition 4)
L ≪
√
N
, Theorem 1
, Theorem 4
√
N ≲L ≪N/ ln N
, [17]
cN < L ≤N/2
/ Theorems 2, 3 / Theorem 5
for arbitrarily small constant c > 0
x ≳y if x/y ≥c for some constant c > 0.) Previously, Mag´an [16] showed that random
Gaussian states with deﬁnite fermion number obey the ETH in an average sense for L ≤2.
For L ≳
√
N, since the ETH fails, there is an observable (on subsystem A) that distin-
guishes an eigenstate from the thermal state. Measuring this observable does not require
many-body entangling operations. It can be done by measuring the occupation numbers of L
individual modes, in a basis chosen based on the eigenstate in question, and then classically
processing the measurement results. We describe this in more detail in Subsection 3.1.
Let the initial state |Ψ0⟩be a (random) product state, where each fermionic mode is either
vacant or occupied. No matter how small the perturbation is, its eﬀect on the dynamics
becomes signiﬁcant at suﬃciently long times when the time is greater than the inverse of
the perturbation strength. Previously, we proved entanglement thermalization with high
probability [17].
Deﬁnition 4 (entanglement thermalization [18]). For L ≤N/2 and to leading order in L,
the entanglement entropy of subsystem A evolves to the thermodynamic entropy of A at the
same energy.
Here we prove thermalization (Deﬁnition 3) with high probability when L ≪N/ ln N.
However, thermalization never occurs when L ≥cN for an arbitrarily small constant c > 0.
Table 1 summarizes our results. “Thermalization without eigenstate thermalization” (the
title of this paper) is proved for
√
N ≲L ≪N/ ln N. Although the subsystem size L is not
upper bounded by a constant, it is still a vanishing fraction of the system size N.
“Thermalization without eigenstate thermalization” can be understood as follows. ¯Ψ is
A-thermal if every |j⟩in the sum on the right-hand side of (3) is A-thermal. However, this
gives only a suﬃcient condition for ¯Ψ being A-thermal. It could be possible that while most
|j⟩’s are not A-thermal, ¯Ψ (a mixture of many |j⟩’s) is A-thermal because the deviations of
diﬀerent |j⟩’s from A-thermality cancel. This possibility provably occurs in our model.
4
### Page 5

1.3
Eigenstate thermalization hypothesis
ETH for systems.
Deﬁnition 2 is the deﬁnition of the ETH for individual eigenstates.
Previous work has also deﬁned the ETH for systems: A Hamiltonian obeys the strong or
weak ETH (in an energy interval) if all or almost all2 eigenstates (in the energy interval)
obey the ETH, respectively.
Our results on the ETH (summarized in the second column of Table 1) apply to random
eigenstates of random Hamiltonians. If we view them as statements about Hamiltonians,
they imply that the weak ETH holds and fails with overwhelming probability for L ≪
√
N
and L ≳
√
N, respectively.
Previous work by Mori and Shiraishi [19] showed evidence of thermalization in a model
that obeys the weak ETH but not the strong ETH.3 In their model, for a generic initial
state, the total weight of ETH-violating eigenstates in the sum on the right-hand side of (3)
is negligible. Thus, the thermalization observed in Ref. [19] could be explained by the weak
ETH. By contrast, in our model, for
√
N ≲L ≪N/ ln N, we observe thermalization without
even the weak ETH, so ¯Ψ is A-thermal even though most eigenstates on the right-hand side
of (3) are not.
Subsystem size in ETH.
The idea behind the ETH is that eigenstates should look
thermal with respect to “simple” observables. Since we lack a general proof of when the
ETH holds, we cannot precisely determine which observables should be included here. One
plausible approach is to consider all observables that act non-trivially only on a suﬃciently
small subsystem. Indeed, Ref. [21] provided evidence that in systems with spatially local
interactions, the ETH fails if the subsystem size is a constant fraction of the system size.
In our model, we observe a sharp threshold in the subsystem size L: If L ≪
√
N then the
ETH holds for almost all eigenstates and if L ≳
√
N then it fails for almost all eigenstates.
Our model (9) has non-local interactions and has the same set of eigenstates as an integrable
Hamiltonian. In the future, it would be interesting to study the validity of the ETH with
respect to the subsystem size in systems that are non-integrable and/or have spatially local
interactions.
Higher values of L are relevant for more complicated observables such as L-point cor-
relation functions. They can also control the probability of large ﬂuctuations for simpler
observables [22]. For example, in an N-mode fermionic system, let Q be the total fermionic
number operator (7). For k ≤N, the expectation

Qk
depends on k-point correlation
functions. While k = 1 and k = 2 give the expectation and variance of Q, higher values of
k can yield sharper bounds on the probability of large ﬂuctuations in Q.
The scaling of L with N can be interpreted as the important question of how large the
bath needs to be. In an isolated system of size N, (eigenstate) thermalization with respect
to subsystem A of size L means that a bath ¯A of size N −L suﬃces. In our model, the
threshold for the validity of the ETH is L ∼
√
N. Thus, the bath size must be ≫L2 for
the ETH to hold. This is unrealistic when L ∼1023 is macroscopically large. By contrast,
2“Almost all” means that the fraction of ETH-violating eigenstates (in the energy interval) vanishes in
the thermodynamic limit.
3Using a combination of analytical and numerical methods, it was shown [20] that an exponentially small
(in the system size) fraction of the eigenstates of the model violate the ETH.
5
### Page 6

thermalization occurs when L ≪N/ ln N or as long as the bath size is ≫L ln L. The ratio
of the bath size to L is not huge even if L ∼1023.
2
Results (formal)
2.1
Model and deﬁnitions
The real (complex) SYKq model [23–27] is a quantum mechanical model of Majorana (Dirac)
fermions with random all-to-all q-body interactions (“q-body” means that each term in the
Hamiltonian acts non-trivially only on q fermionic modes).
Consider an N-mode (Dirac) fermionic system with creation and annihilation operators
a†
j, aj indexed by j = 1, 2, . . . , N. Let A be an arbitrary subsystem of L fermionic modes
and ¯A be the complement of A (rest of the system).
Deﬁnition 5 (complex SYK2 model). Let h be a random matrix of order N from the
Gaussian unitary ensemble. The Hamiltonian of the complex SYK2 model is
HSYK2 = a†ha,
(4)
where a := (a1, a2, . . . , aN)T is a column vector of N annihilation operators.
Deﬁnition 6 (complex SYK4 model [25, 27]). Let
I :=

(j, k, l, m) ∈{1, 2, . . . , N}×4 : (j < k) and (l < m) and (jN + k ≤lN + m)
	
(5)
and J := {Jjklm}(j,k,l,m)∈I be a collection of |I| independent complex Gaussian random
variables with zero mean Jjklm = 0 and unit variance |Jjklm|2 = 1. The Hamiltonian of the
complex SYK4 model is
HSYK4 =
X
(j,k,l,m)∈I
Jjklma†
ja†
kalam + H.c.,
(6)
where “H.c.” means Hermitian conjugate.
The complex SYKq model is also known as the embedded Gaussian unitary ensemble
[28, 29] and has been studied under this name for decades.
Let
Q :=
N
X
j=1
a†
jaj
(7)
be the fermion number operator. Let ǫ1, ǫ2 be inﬁnitesimal and
HSYK := HSYK2 + ǫ2HSYK4.
(8)
Our model is
H = Q + ǫ1HSYK = Q + ǫ1HSYK2 + ǫ1ǫ2HSYK4.
(9)
6
### Page 7

Both HSYK and H are nearly integrable as both HSYK2 and Q+ǫ1HSYK2 are integrable models
of free fermions. By deﬁnition, the complex SYK2 and SYK4 models and hence HSYK and
H conserve fermion number in that
[HSYK2, Q] = [HSYK4, Q] = [HSYK, Q] = [H, Q] = 0.
(10)
Let
σβ := e−βH/ tr
 e−βH
(11)
be a thermal state at inverse temperature β. Neglecting inﬁnitesimal quantities, the reduced
density matrix of subsystem A is
σβ,A := tr ¯
A σβ = e−βQA/ tr
 e−βQA
,
(12)
where
QA :=
X
j∈A
a†
jaj
(13)
is the restriction of Q to A. Let |Φ⟩be such that that Q|Φ⟩= n|Φ⟩. If σβ and |Φ⟩have the
same energy, then
tr(σβH) = ⟨Φ|H|Φ⟩= n =⇒β = ln(N/n −1).
(14)
Let ∥B∥1 := tr
√
B†B denote the trace norm of a linear operator B. The trace distance
T(ρ1, ρ2) := ∥ρ1 −ρ2∥1/2 = max
∥B∥≤1 | tr(ρ1B) −tr(ρ2B)|/2,
0 ≤T(ρ1, ρ2) ≤1
(15)
and the ﬁdelity
F(ρ1, ρ2) := tr2 q√ρ1ρ2
√ρ1,
0 ≤F(ρ1, ρ2) ≤1
(16)
are measures of distinguishability between two density operators. It is well known that
1 −
p
F(ρ1, ρ2) ≤T(ρ1, ρ2) ≤
p
1 −F(ρ1, ρ2).
(17)
The trace distance is directly related to the success probability of the optimal protocol
for distinguishing two states [30, Chap. 9]. Speciﬁcally, consider the following state inference
problem. We are given a random state ρ, which is either ρ1 or ρ2 with equal probability. We
are allowed to perform a measurement on a single copy of ρ. From the measurement results,
we must predict whether ρ is ρ1 or ρ2. Let
ρ1 −ρ2 =
X
j
µj|Φj⟩⟨Φj|
with
X
j
µj = 0
(18)
be the eigendecomposition of ρ1−ρ2. The optimal protocol is to measure ρ in the orthonormal
basis {|Φj⟩}. If the post-measurement state is |Φj⟩, then we predict ρ1 if µj ≥0 and predict
ρ2 if µj < 0. The success probability of this protocol is
1
2 + 1
2
X
j
|µj| = 1 + T(ρ1, ρ2)
2
.
(19)
7
### Page 8

We use standard asymptotic notation. Let f, g : R+ →R+ be two functions. One writes
f(x) = O(g(x)) if and only if there exist constants M, x0 > 0 such that f(x) ≤Mg(x) for all
x > x0; f(x) = Ω(g(x)) if and only if there exist constants M, x0 > 0 such that f(x) ≥Mg(x)
for all x > x0; f(x) = Θ(g(x)) if and only if there exist constants M1, M2, x0 > 0 such that
M1g(x) ≤f(x) ≤M2g(x) for all x > x0; f(x) = o(g(x)) if and only if for any constant
M > 0 there exists a constant x0 > 0 such that f(x) < Mg(x) for all x > x0.
2.2
Eigenstate thermalization
The spectrum of HSYK2 is non-degenerate with probability 1 [17]. Then, due to fermion
number conservation (10) and since the perturbation ǫ2HSYK4 is inﬁnitesimal, H, HSYK,
HSYK2, and Q+ ǫ1HSYK2 have the same set of eigenstates (up to an inﬁnitesimal error), each
of which has a deﬁnite fermion number.
Let |ψ⟩be an eigenstate of HSYK2 with fermion number n and ν := n/N be the ﬁlling
fraction. We write |ψ⟩∼PN,n if |ψ⟩is randomly sampled using the following procedure:
1. Let h be a random matrix of order N from the Gaussian unitary ensemble.
2. |ψ⟩is chosen uniformly at random from the
 N
n

eigenstates of a†ha with fermion
number n.
Let ψA := tr ¯
A |ψ⟩⟨ψ| be the reduced density matrix. Recall the deﬁnition (12) of σβ,A, where
β is given by (14).
Theorem 1 (eigenstate thermalization). Suppose that 1/2 ≥ν = Ω(1). For L = o(
√
N)
and any ∆such that Ω(L2) = ∆= o(N),
Pr
|ψ⟩∼PN,n
 F(ψA, σβ,A) = 1 −O(∆/N)

= 1 −O(e−∆),
(20)
Pr
|ψ⟩∼PN,n
 T(ψA, σβ,A) = O(
p
∆/N)

= 1 −O(e−∆).
(21)
Theorem 2 (failure of ETH). Suppose that 1/2 ≥ν = Ω(1). For L = Ω(
√
N),
Pr
|ψ⟩∼PN,n
 F(ψA, σβ,A) = e−Ω(L2/N)
= 1 −e−Ω(L2),
(22)
Pr
|ψ⟩∼PN,n
 T(ψA, σβ,A) = 1 −e−Ω(L2/N)
= 1 −e−Ω(L2).
(23)
Theorem 3 (failure of ETH). Suppose that ν ≤1/2. For L > n,
F(ψA, σβ,A) ≤(1 −ν)L−n,
T(ψA, σβ,A) ≥1 −(1 −ν)L−n.
(24)
These results on the ETH are for individual eigenstates. To interpret Theorems 1, 2 as
statements about Hamiltonians, recall the deﬁnition of the weak ETH in an energy interval
in Subsection 1.3.
Corollary 1. Let n be a positive integer such that N/2 ≥n = Ω(N). For L = o(
√
N), the
probability (with respect to the randomness of h) that Q + ǫ1a†ha obeys the weak ETH in
the energy interval (n −1/2, n + 1/2) is 1 −e−∆for any ∆= o(N). For L = Ω(
√
N), the
probability that Q + ǫ1a†ha obeys the weak ETH in the energy interval (n −1/2, n + 1/2) is
e−Ω(L2).
8
### Page 9

Near the end of Subsection 2.1, we said that 1
2(1 + T(ψA, σβ,A)) is the success probability
of the optimal protocol for predicting whether a given state of subsystem A is ψA or σβ,A
by performing a measurement on a single copy of the given state. The measurement in this
protocol is in the eigenbasis of ψA −σβ,A. Since both ψA and σβ,A are Gaussian states, each
of them can be written as a tensor product of single-mode states with an appropriate choice
of modes. Furthermore, since the correlation matrices of ψA and σβ,A commute, the same
set of modes works for both states. Thus, we can measure the observable ψA −σβ,A by
measuring L single-mode operators and classically combining the results. Complete details
of the measurement will be given in Subsection 3.1.
2.3
Thermalization
We initialize the system in a product state with fermion number n and let ν = n/N. Since
the ensemble of SYKq Hamiltonians is invariant with respect to permutations of indices, we
may assume without loss of generality that the initial state is
|φ⟩:= a†
1a†
2 · · ·a†
n|0⟩,
(25)
where |0⟩is the vacuum state with no fermions. Since |φ⟩has a deﬁnite fermion number, H
and HSYK generate the same dynamics in the sense that
e−iHt|φ⟩= e−inte−iHSYKǫ1t|φ⟩= e−inte−iǫ1HSYK2t−iǫ1ǫ2HSYK4t|φ⟩.
(26)
Let L, m be positive integers such that Lm is a multiple of N. Let A1, A2, . . . , Am be
m possibly overlapping subsystems, each of which has exactly L fermionic modes. Suppose
that each fermionic mode in the system is in exactly Lm/N out of these m subsystems. Let
φ(t) := e−iHt|φ⟩⟨φ|eiHt,
φ(t)Aj := tr ¯
Aj φ(t)
(27)
be the state and its reduced density matrix at time t, respectively.
Let τ be suﬃciently large4 and t be uniformly distributed in the interval [0, τ]. Recall
the deﬁnition (12) of σβ,A, where β is given by (14).
Theorem 4 (thermalization). For 1/2 ≥ν = Ω(1), subsystems of size
L = o(N/ ln N)
(28)
thermalize in the sense that (poly(N) denotes a polynomial of suﬃciently high degree in N)
Pr
h
 
Pr
J
 
Pr
t∈[0,τ]
 
1
m
m
X
j=1
∥φ(t)Aj −σβ,Aj∥2
1 = O(L ln N)
N
!
= 1 −e−Ω(N)
!
= 1
!
≥1 −1/poly(N).
(29)
4Conceptually, τ needs to be suﬃciently large such that the eﬀect of the SYK4 term in Eq. (26) is
signiﬁcant at most time t ∈[0, τ]. At a technical level, Theorem 4 follows from Theorem 6. The proof of the
latter theorem in Ref. [17] approximates the inﬁnite-time average limτ ′→∞Et∈[0,τ ′] by the long-time average
Et∈[0,τ]. τ needs to be suﬃciently large such that the approximation error is negligible.
9
### Page 10

For any linear operator Bj on subsystem Aj with ∥Bj∥≤1, Eq. (15) implies that
tr
 φ(t)Bj

−tr(σβBj)
 ≤∥φ(t)Aj −σβ,Aj∥1.
(30)
Thus, (29) implies thermalization of physical properties measured on o(N/ ln N) fermionic
modes.
In contrast to Eq. (28), reduced density matrices do not thermalize if the subsystem size
is a constant fraction of the system size. Let E|A|=L denote averaging over all subsystems of
L fermionic modes. There are
 N
L

such subsystems.
Theorem 5 (failure of thermalization). Suppose that 1/2 ≥ν = Ω(1). For L = Ω(N) and
any h, J, t,
E
|A|=L ∥φ(t)A −σβ,A∥1 = Ω(1).
(31)
3
Proof sketches
In this section, we give intuitive sketches of the proofs of our results. Full calculations are
deferred to Appendix A.
3.1
Eigenstate thermalization
For a density operator ρ, let ⟨B⟩:= tr(ρB) denote the expectation value of an operator B.
Let C be the correlation matrix with its elements given by
Cjk := ⟨a†
jak⟩.
(32)
It is easy to see that C is a Hermitian matrix of order N.
Lemma 1 ([17, 31]). |ψ⟩∼PN,n means that |ψ⟩is a uniformly random Gaussian state with
fermion number n in the sense of Deﬁnition 7.
Deﬁnition 7 (uniformly random pure Gaussian state with deﬁnite fermion number). A pure
Gaussian state with fermion number n is uniformly random if its correlation matrix is given
by
C = U† diag(1, 1, . . . , 1
|
{z
}
n ones
, 0, 0, . . . , 0
|
{z
}
N −n zeros
)U,
(33)
where U is a unitary matrix chosen uniformly at random with respect to the Haar measure.
Assume without loss of generality that the indices of the L fermionic modes in subsystem
A are 1, 2, . . . , L. Let CA = (Un×L)†Un×L be the L × L upper left submatrix of C, where
Un×L is the n × L upper left submatrix of U.
We can interpret CA as the overlap of two projectors, as follows. Let Pn and PL be pro-
jectors of ranks n and L, respectively, such that Un×L = PnUPL. Then, CA = PL(U†PnU)PL.
We can view this as the overlap between a ﬁxed projector PL and a random projector U†PnU.
Let
CA = V diag(λ1, λ2, . . . , λL)V †
(34)
10
### Page 11

be the eigendecomposition of the Hermitian matrix CA, where V is a unitary matrix of order
L. Deﬁne a row of annihilation operators
(b1, b2, . . . , bL) = (a1, a2, . . . , aL)V.
(35)
Then, Eq. (32) implies that
⟨b†
jbk⟩= λjδjk,
(36)
where δjk is the Kronecker delta. Since the reduced density matrix ψA is a Gaussian state,
it is fully determined by Eq. (36) so that
ψA =
L
Y
j=1
 λjb†
jbj + (1 −λj)bjb†
j

.
(37)
In the eigenbasis of b†
1b1, b†
2b2, . . . , b†
LbL, ψA has the matrix representation
L
O
j=1
diag(λj, 1 −λj).
(38)
In the same basis,
σβ,A =
L
O
j=1
diag(ν, 1 −ν)
(39)
is also a product state. Since the ﬁdelity is multiplicative,
F(ψA, σβ,A) =
L
Y
j=1
p
νλj +
q
(1 −ν)(1 −λj)
2
.
(40)
The optimal protocol described near the end of Subsection 2.1 for predicting whether a
given state of subsystem A is ψA or σβ,A proceeds as follows. Measure the occupation numbers
b†
1b1, b†
2b2, . . . , b†
LbL and let m1, m2, . . . , mL be the corresponding measurement results. Each
mj is a binary random variable with Pr(mj = 1) = λj or Pr(mj = 1) = ν if the given state
is ψA or σβ,A, respectively. We predict ψA if
L
Y
j=1
(λj/ν)mj ≥1
(41)
and predict σβ,A otherwise. This can be thought of as a likelihood-ratio test, in which we
predict the state that makes our measurement outcomes more likely. It is also the optimal
Helstrom measurement with success probability 1
2(1 + T(ψA, σβ,A)).
Proof of Theorem 3. For L > n, CA is singular, and the multiplicity of the eigenvalue 0 is
at least L −n. Using Eqs. (37), (39) and since the ﬁdelity (trace distance) is non-decreasing
11
### Page 12

(non-increasing) under partial trace,
F(ψA, σβ,A) ≤F
 L−n
O
j=1
diag(0, 1),
L−n
O
j=1
diag(ν, 1 −ν)
!
= (1 −ν)L−n,
(42)
T(ψA, σβ,A) ≥T
 L−n
O
j=1
diag(0, 1),
L−n
O
j=1
diag(ν, 1 −ν)
!
= 1 −(1 −ν)L−n.
(43)
For L ≤min{n, N −n}, the joint probability distribution of λ1, λ2, . . . , λL is the Jacobi
unitary ensemble with parameters r = N −n −L and s = n −L [31–33].
Deﬁnition 8 (Jacobi unitary ensemble). The probability density function of the Jacobi
unitary ensemble with parameters r, s > −1 is
J (λ1, λ2, . . . , λL) ∝
Y
1≤j<k≤L
(λj −λk)2
L
Y
j=1
(1 −λj)rλs
j,
0 ≤λj ≤1.
(44)
We explain why the ETH holds and fails with high probability for L = o(
√
N) and
L = Ω(
√
N), respectively. To this end, consider the limit L →∞with L = o(N). In this
case, Theorem 2.1 in Ref. [34] says that the empirical distribution of
s
N
ν(1 −ν)L(λj −ν)
(45)
converges weakly to the semicircle distribution with radius 2 almost surely. Thus,
λj = ν ± Θ(
p
L/N)
(46)
for almost all j with high probability. Since L = o(N), by Taylor expansion,
p
νλj +
q
(1 −ν)(1 −λj) = 1 −Θ(λj −ν)2.
(47)
Substituting this into Eq. (40),
F(ψA, σβ,A) =
L
Y
j=1
 1 −Θ(L/N)

=
(
1 −o(1),
L = o(
√
N),
1 −Ω(1),
L = Ω(
√
N).
(48)
Proofs of the probabilistic bounds in Theorems 1, 2 without assuming L →∞or L =
o(N) are given in Appendix A.1. There we do not use Theorem 2.1 in Ref. [34] but instead
rely on a recent concentration result [35] for the second moment of the Jacobi ensemble.
12
### Page 13

3.2
Thermalization
Proof sketch of Theorem 4.
In a previous paper [17], we proved entanglement thermal-
ization: With high probability, the von Neumann entropies of φ(t)Aj and σβ,Aj are equal to
leading order in L. So are the free energies of φ(t)Aj and σβ,Aj. Since the thermal state
minimizes the free energy [36], the free energy of φ(t)Aj is only slightly higher than the
minimum. Pinsker’s inequality [37] implies that any state of low free energy is close to a
thermal state in trace distance.
Condition (28) ensures that with high probability, the free energy of φ(t)Aj is suﬃciently
low so that the trace distance between φ(t)Aj and σβ,Aj from the above analysis is o(1).
Proof sketch of Theorem 5.
φ(t) for any t ∈R has a deﬁnite fermion number, but σβ
does not. This diﬀerence has its footprint in the reduced density matrices. If the fermion
number operator (13) is measured on a random subsystem A of L fermionic modes, we
obtain a probability distribution on the integers 0, 1, 2, . . . , L. For φ(t), the distribution is
hypergeometric corresponding to drawing L balls without replacement from a pool of n white
and N −n black balls. For σβ, the distribution is binomial corresponding to drawing L balls
with replacement from the same pool.
Note added.
Very recently, we became aware of related work by Yu, Gong, and Cirac [38].
They studied the entanglement of random Gaussian states with deﬁnite fermion number.
Their Theorem 1 is conceptually similar to our Lemma 3 but gives diﬀerent bounds and is
proved using diﬀerent methods.
Acknowledgments
This material is based upon work supported by the U.S. Department of Energy, Oﬃce
of Science, National Quantum Information Science Research Centers, Quantum Systems
Accelerator. AWH was also supported by NSF grants CCF-1729369 and PHY-1818914 and
NTT (Grant AGMT DTD 9/24/20).
A
Proofs
A.1
Eigenstate thermalization
Lemma 2. For any x, y ∈R+ such that x + y ≤1,
1 −(x −y)2/ max{x, y} ≤
 √xy +
p
(1 −x)(1 −y)
2 ≤1 −(x −y)2.
(49)
Proof. Let
x = cos2 θ + α
2
,
y = cos2 θ −α
2
,
0 ≤θ ± α ≤π
(50)
so that
 √xy +
p
(1 −x)(1 −y)
2 = cos2 α = 1 −sin2 α,
(x −y)2 = sin2 θ · sin2 α.
(51)
13
### Page 14

The condition x + y ≤1 implies that θ ≥π/2 so that
max{x, y} ≤
max
α∈[0,π−θ] cos2 θ −α
2
= sin2 θ ≤1.
(52)
We complete the proof by combining (51), (52).
Let
M :=
L
X
j=1
(λj −ν)2
(53)
be the shifted second moment of the Jacobi ensemble.
Lemma 3 ([35]). For any δ > 0,
Pr
 |M −ν(1 −ν)L2/N| > δ

= O(e−Ω(Nδ) min{Nδ/L2,1}).
(54)
Proof of Theorem 1. Using Eq. (40) and Lemma 2,
F(ψA, σβ,A) ≥
L
Y
j=1
max{1 −(λj −ν)2/ν, 0} ≥1 −M/ν.
(55)
Then, Eq. (20) follows from Lemma 3. Equation (21) follows from (17) and Eq. (20).
Proof of Theorem 2. Using Eq. (40) and Lemma 2,
F(ψA, σβ,A) ≤
L
Y
j=1
 1 −(λj −ν)2
≤e−M.
(56)
For L ≤n, Eq. (22) follows from (56) and Lemma 3.
For L > n = Ω(N), let A′ be an (arbitrary) subsystem of n fermionic modes in A. We
have proved that
Pr
|ψ⟩∼PN,n
 F(ψA′, σβ,A′) = e−Ω(N)
= 1 −e−Ω(N2).
(57)
Equation (22) follows the fact that the ﬁdelity is non-decreasing under partial trace.
Equation (23) follows from (17) and Eq. (22).
A.2
Proof of Theorem 4
Let
S(ρ) := −tr(ρ ln ρ)
(58)
be the von Neumann entropy of a density operator and
Hb(ν) := −ν ln ν −(1 −ν) ln(1 −ν)
(59)
be the binary entropy function.
14
### Page 15

Theorem 6 ([17]). Suppose that 1/2 ≥ν = Ω(1). For L ≤N/10,
Pr
h
 
Pr
J
 
Pr
t∈[0,τ]
 
1
m
m
X
j=1
S(φ(t)Aj) ≥Hb(ν)L −O(L ln N)
N
!
= 1 −e−Ω(N)
!
= 1
!
≥1 −1/poly(N).
(60)
Recall the deﬁnition (13) of QA. It is easy to see that
1
m
m
X
j=1
QAj = LQ
N
=⇒
1
m
m
X
j=1
tr
 φ(t)AjQAj

= νL.
(61)
Using Pinsker’s inequality [37] between the trace distance and quantum relative entropy,
1
2∥φ(t)A −σβ,A∥2
1 ≤S
 φ(t)A∥σβ,A

:= −tr
 φ(t)A ln σβ,A

−S(φ(t)A)
= β tr
 φ(t)AQA

+ ln tr
 e−βQA
−S(φ(t)A)
(62)
so that
1
2m
m
X
j=1
∥φ(t)Aj −σβ,Aj∥2
1 ≤Hb(ν)L −1
m
m
X
j=1
S(φ(t)Aj).
(63)
Theorem 4 follows from this inequality and Theorem 6.
A.3
Proof of Theorem 5
Let i1 < i2 < · · · < iL be the indices of the L fermionic modes in A. Deﬁne
P >l
A =
X
(n1,n2,...,nL)∈{0,1}×L
PL
j=1 nj>l
L
Y
j=1
 nj + (1 −2nj)aija†
ij

.
(64)
Let [N] := {1, . . . , N} and
[N]
n

:= {R ⊆[N] : |R| = n}
(65)
be the set of size-n subsets of [N]. Let {|φR⟩}R∈([N]
n ) be the complete set of computational
basis states with n fermions, where
|φR⟩:=
 Y
j∈R
a†
j
!
|0⟩.
(66)
By construction, P >l
A = (P >l
A )2 is a projector such that
P >l
A |φR⟩= |φR⟩or 0
(67)
15
### Page 16

if |φR⟩contains > l or ≤l fermions in A, respectively. Hence,
E
|A|=L ∥P >l
A |φR⟩∥=
N
L
−1{R′ ⊆[N] : |R′| = L and |R ∩R′| > l}

=
N
L
−1 X
j>l
n
j
N −n
L −j

.
(68)
The time-evolved state can be expanded as
e−iHt|φ⟩=
X
R∈([N]
n )
cR(t)|φR⟩
(69)
so that
E
|A|=L tr
 φ(t)AP >l
A

=
E
|A|=L ∥P >l
A e−iHt|φ⟩∥2 =
E
|A|=L
X
R∈([N]
n )
|cR(t)|2∥P >l
A |φR⟩∥
=
X
R∈([N]
n )
|cR(t)|2
E
|A|=L ∥P >l
A |φR⟩∥=
N
L
−1 X
j>l
n
j
N −n
L −j

,
∀t ∈R.
(70)
Equations (12), (14) imply that
tr
 σβ,AP >l
A

=
1
tr(e−βQA)
X
j>l
L
j

e−βj =
X
j>l
L
j

νj(1 −ν)L−j.
(71)
Equations (70) and (71) are the tails of the hypergeometric and binomial distributions,
respectively. The distributions have the same mean νL but diﬀerent variances: ν(1−ν)LN−L
N−1
for the hypergeometric distribution and ν(1−ν)L for the binomial distribution. Furthermore,
both distributions are well approximated by Gaussians matching those moments. Thus, their
tails are distinguishable in the sense of (72) for l = νL + Θ(
√
L).
The total variation distance between the hypergeometric and binomial distributions has
been studied in the context of de Finetti theorem. The theorem states that for a permutation-
invariant probability distribution of N random variables, the marginal distribution of L ≪N
variables is close to a mixture of distributions, each of which represents L independent and
identically distributed random variables [39]. From either the Gaussian approximation or
(in the ν = 1/2 case) Theorem 35 and Lemmas 45, 46 in Ref. [39], we have
0 <
E
|A|=L tr
 σβ,AP >l
A

−
E
|A|=L tr
 φ(t)AP >l
A

= Ω(1)
(72)
for L = Ω(N). We complete the proof by noting that
E
|A|=L ∥φ(t)A −σβ,A∥1 ≥
E
|A|=L
tr
 φ(t)AP >l
A −σβ,AP >l
A
 ≥
 E
|A|=L tr
 φ(t)AP >l
A −σβ,AP >l
A
 .
(73)
16
### Page 17

References
[1]
J. M. Deutsch. Quantum statistical mechanics in a closed system. Physical Review A, 43(4):2046–
2049, 1991.
[2]
M. Srednicki. Chaos and quantum thermalization. Physical Review E, 50(2):888–901, 1994.
[3]
M. Rigol, V. Dunjko, and M. Olshanii. Thermalization and its mechanism for generic isolated
quantum systems. Nature, 452(7189):854–858, 2008.
[4]
A. Dymarsky, N. Lashkari, and H. Liu. Subsystem eigenstate thermalization hypothesis.
Physical Review E, 97(1):012140, 2018.
[5]
G. Biroli, C. Kollath, and A. M. L¨auchli. Eﬀect of rare ﬂuctuations on the thermalization of
isolated quantum systems. Physical Review Letters, 105(25):250401, 2010.
[6]
J. P. Keating, N. Linden, and H. J. Wells. Spectra and eigenstates of spin chain Hamiltonians.
Communications in Mathematical Physics, 338(1):81–102, 2015.
[7]
F. G. S. L. Brand˜ao, E. Crosson, M. B. S¸ahino˘glu, and J. Bowen. Quantum error cor-
recting codes in eigenstates of translation-invariant spin chains. Physical Review Letters,
123(11):110502, 2019.
[8]
C. Gogolin and J. Eisert. Equilibration, thermalisation, and the emergence of statistical
mechanics in closed quantum systems. Reports on Progress in Physics, 79(5):056001, 2016.
[9]
L. D’Alessio, Y. Kafri, A. Polkovnikov, and M. Rigol. From quantum chaos and eigenstate
thermalization to statistical mechanics and thermodynamics. Advances in Physics, 65(3):239–
362, 2016.
[10]
J. M. Deutsch. Eigenstate thermalization hypothesis. Reports on Progress in Physics, 81(8):082001,
2018.
[11]
A. Anshu. Concentration bounds for quantum states with ﬁnite correlation length on quantum
spin lattice systems. New Journal of Physics, 18(8):083011, 2016.
[12]
P. Reimann. Foundation of statistical mechanics under experimentally realistic conditions.
Physical Review Letters, 101(19):190403, 2008.
[13]
N. Linden, S. Popescu, A. J. Short, and A. Winter. Quantum mechanical evolution towards
thermal equilibrium. Physical Review E, 79(6):061103, 2009.
[14]
A. J. Short. Equilibration of quantum systems and subsystems. New Journal of Physics,
13(5):053009, 2011.
[15]
G. De Palma, A. Seraﬁni, V. Giovannetti, and M. Cramer. Necessity of eigenstate thermal-
ization. Physical Review Letters, 115(22):220401, 2015.
[16]
J. M. Mag´an. Random free fermions: An analytical example of eigenstate thermalization.
Physical Review Letters, 116(3):030401, 2016.
[17]
Y. Huang and A. W. Harrow. Quantum entropy thermalization. arXiv:2302.10165.
[18]
L. Zhang, H. Kim, and D. A. Huse. Thermalization of entanglement. Physical Review E,
91(6):062128, 2015.
[19]
T. Mori and N. Shiraishi. Thermalization without eigenstate thermalization hypothesis after
a quantum quench. Physical Review E, 96(2):022153, 2017.
17
### Page 18

[20]
N. Shiraishi and T. Mori. Systematic construction of counterexamples to the eigenstate ther-
malization hypothesis. Physical Review Letters, 119(3):030601, 2017.
[21]
J. R. Garrison and T. Grover. Does a single eigenstate encode the full Hamiltonian? Physical
Review X, 8(2):021026, 2018.
[22]
H. Touchette. The large deviation approach to statistical mechanics. Physics Reports, 478(1-
3):1–69, 2009. eprint: https://arxiv.org/abs/0804.0327.
[23]
S. Sachdev and J. Ye. Gapless spin-ﬂuid ground state in a random quantum Heisenberg
magnet. Physical Review Letters, 70(21):3339–3342, 1993.
[24]
A. Kitaev. A simple model of quantum holography. In KITP Program: Entanglement in
Strongly-Correlated Quantum Matter, 2015. https://online.kitp.ucsb.edu/online/entangled15/kitaev
[25]
S. Sachdev. Bekenstein-Hawking entropy and strange metals. Physical Review X, 5(4):041025,
2015.
[26]
J. Maldacena and D. Stanford. Remarks on the Sachdev-Ye-Kitaev model. Physical Review
D, 94(10):106002, 2016.
[27]
Y. Gu, A. Kitaev, S. Sachdev, and G. Tarnopolsky. Notes on the complex Sachdev-Ye-Kitaev
model. Journal of High Energy Physics, 2020(2):157, 2020.
[28]
V. K. B. Kota. Embedded random matrix ensembles for complexity and chaos in ﬁnite inter-
acting particle systems. Physics Reports, 347(3):223–288, 2001.
[29]
L. Benet and H. A. Weidenm¨uller. Review of the k-body embedded ensembles of Gaussian
random matrices. Journal of Physics A: Mathematical and General, 36(12):3569–3593, 2003.
[30]
M. A. Nielsen and I. L. Chuang. Quantum Computation and Quantum Information: 10th
Anniversary Edition. Cambridge University Press, 2010.
[31]
E. Bianchi, L. Hackl, M. Kieburg, M. Rigol, and L. Vidmar. Volume-law entanglement entropy
of typical pure quantum states. PRX Quantum, 3(3):030201, 2022.
[32]
A. Rouault. Asymptotic behavior of random determinants in Laguerre, Gram and Jacobi
ensembles. ALEA-Latin American Journal of Probability and Mathematical Statistics, 3:181–
230, 2007.
[33]
C. Liu, X. Chen, and L. Balents. Quantum entanglement of the Sachdev-Ye-Kitaev models.
Physical Review B, 97(24):245126, 2018.
[34]
J. Nagel. Nonstandard limit theorems and large deviations for the Jacobi beta ensemble.
Random Matrices: Theory and Applications, 03(03):1450012, 2014.
[35]
Y. Huang and A. W. Harrow. Improved concentration of Laguerre and Jacobi ensembles.
arXiv:2211.11203.
[36]
A. Wehrl. General properties of entropy. Reviews of Modern Physics, 50(2):221–260, 1978.
[37]
K. M. R. Audenaert. Comparisons between quantum state distinguishability measures. Quan-
tum Information and Computation, 14(1-2):31–38, 2014.
[38]
X.-H. Yu, Z. Gong, and J. I. Cirac. Free-fermion Page curve: Canonical typicality and dy-
namical emergence. Physical Review Research, 5(1):013044, 2023.
[39]
P. Diaconis and D. Freedman. Finite exchangeable sequences. Annals of Probability, 8(4):745–
764, 1980.
18