# StreamMapNet Streaming Mapping Online HD Map

**Source**: arxiv PDF, 10 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

arXiv:2308.10116v2  [math.CV]  23 Aug 2023
LIPSCHITZ CONTINUITY FOR HARMONIC FUNCTIONS
AND SOLUTIONS OF THE ¯α-POISSON EQUATION
MIODRAG MATELJEVI´C, NIKOLA MUTAVDˇZI´C, ADEL KHALFALLAH
Abstract. We study Lipschitz continuity for solutions of the ¯α-Poisson
equation in planar cases. We also review some recently obtained results.
As corolary we can restate results for harmonic and gradient harmonic
functions.
1. Introduction and preliminaries
The weighted Laplacian operator Lρ is deﬁned by Lρ = Dz(ρDz) and
L∗
ρ = Dz(ρDz). If the weight function ρ is chosen to be ρα(z) = (1 −|z|2)−α
(α > −1) in the unit disk U, we call Lρ the standard weighted Laplacian
operator and write it by Lα for simplicity, and Lα will be notation for L∗
ρ.
Our main result is:
Theorem 8. Assume that g ∈C(D) is such that (1−|z|2)αg is bounded and
u ∈VD→Ω[g] with the representation u(w) = v(w) + Gα[g](w). If α > 0, and
v is Lipshitz, then u is also Lipshitz continuous on D.
We can restate this result by means of certain solutions to α−Poisson’s
equation. First we consider some basic properties of α−harmonic mappings.
In particular, we improve Chen and Kalaj result [6]. Behm [2] found Green
function and solved the Dirichlet boundary value problem of the α-Poisson
equation. Our method is based on Theorem 7 which gives estimate of the
Green potential Gα of g and the local C2-coordinate method ﬂattering the
boundary [23].
At the begining of this paper we will introduce basic notation together
with deﬁnition of so called α−Laplacian and α−harmonic functions. Also,
deﬁnition and properties of α−Poisson’s kernel and α−Poisson’s integral are
stated, as a very important technical assets used in our research. More in-
formation about this notion can be found in Olofsson’s and Wittsten’s paper
[29]. In the proceeding we recall deﬁnition of Green function for α−Laplacian
which is thoroughly invesigated in Behm [2]. Formulation and solution of
Dirichlet boundary value problem for α−Poisson’s equation, proven in Chen
and Kalaj paper [3], is shown in Theorem 1. In paper [7] Chen used this
1 Mathematics Subject Classiﬁcation 2010 Primary 42B15, Secondary 42B30.
2 Key words and phrases: Poisson kernel, harmonic functions.
1
### Page 2

2
result to prove the boundary characterizations of a Lipschitz continuous α-
harmonic mappings, and proved Theorem 2.
As an introductory result of this paper, we loose assumption on boundary
value of α-harmonic mapping v, which is written in part (d) of Theorem
2 and attain Theorem 5. Proof of this theorem is based on Hardy space
technique which can be found in the ﬁrst author’s monography [27], and
Theorem 6 proven in ﬁrst author’s and A. Khalfallah’s paper [13].
The
second improvement of Theorem 2 consider the condition on g = −Lαu.
This result is proven in Theorem 7, and uses various estimates which we
establish in Sunsection 2.3.
1.1. α−harmonic mappings. Linear and semilinear equations can be tre-
ated together.
We take a(x, y)ux + b(x, y)uy = c(x, y, u), where a, b, c
are C1 functions of their arguments. The operator a(x, y)ux + b(x, y)uy on
the left hand side of this equation represents diﬀerentiation in a direction
(a, b) at the point (x, y) in (x, y)-plane.
Let us consider a curve, whose
tangent at each point (x, y) has the direction (a, b). Coordinates (x(s), y(s))
of a point on this curve satisfy (1) dx/ds = a(x, y), dy/ds = b(x, y) or (2)
dy/dx = b(x, y)/a(x, y).
Two complex derivatives
∂
∂z = Dz and
∂
∂z = Dz of u are written by
∂
∂z u = Dzu = 1
2(ux −iuy)
and
∂
∂z u = Dzu = 1
2(ux + iuy)
respectively, where z = x + iy.
The weighted Laplacian operator Lρ is deﬁned by
Lρ = Dz(ρDz)
and
L∗
ρ = Dz(ρDz).
If the weight function ρ is chosen to be ρα(z) = (1 −|z|2)−α in the unit disk
U, we call Lρ the standard weighted Laplacian operator and write it by Lα
for simplicity, here α is a real number with α > −1. It is clear that
L∗
ρu = Lαu = DzρDzu + ρDzzu = α(1 −|z|2)−α−1zuz + (1 −|z|2)−αuzz
Lαu = α(1 −|z|2)−α−1zuz + (1 −|z|2)−αuzz
First we can see that L∗
αu = 0 iﬀ
(1 −|z|2)uzz + αzuz = 0
(1)
It can be easily checked that Lαu = 0 iﬀL∗
αu = 0.
Set p = uz and q = uz. Since uz = uz and uz = uz, we ﬁnd
zuz and zuz are conjugate, and also
uzz = qz and uzz = qz = qz and therefore uzz and uzz are conjugate.
If we set d(z) = 1 −|z|2, then ρα = d−α and by easy computation we ﬁnd
ρz = αd−αz,
ρz = αd−α−1z,
ρx = 2αd−α−1x
and
ρy = 2αd−α−1y.
### Page 3

3
Since, 2ρDzu = ρ(ux −iuy), we ﬁnd
4Lρ = Dx[ρ(ux−iuy)]+iDy[ρ(ux−iuy)] = Dx(ρux)+Dy(ρuy)+i(ρyux−ρxuy).
Hence
4Lρ = ρ∆u + ρxux + ρyuy + i(ρyux −ρxuy).
If u is real-valued function then Lρu = 0 iﬀρ∆u + ρxux + ρyuy = 0 and
yux −xuy = 0, that is
∆u + 2αρ1(xux + yuy) and yux −xuy = 0.
By [38], solutions of yux −xuy = 0 is u = f(x2 + y2). Since ρuz = ρg(r)z,
we ﬁnd ρg(r)r2 = zF(z) = c and hence F = 0 and uz = 0. Thus u = c.
If a function u ∈C2(U) satisﬁes the α-harmonic equation
Lα(u) = 0,
then we call it an α-harmonic mapping.
In the case α = 0, α-harmonic
mappings are just Euclidean harmonic mappings. For Lα notation ∆α is
also used in the literature.
1.2. α-Poisson’s integral. In [29], Olofsson and Wittsten showed that if
an α-harmonic function f satisﬁes
lim
r→1−fr = f ∗∈D′(T) (α > −1),
then it has the form of a Poisson type integral
f(z) = Pα[f ∗](z) = 1
2π
Z 2π
0
Pα(ze−iθ)f ∗(eiθ)dθ
in D, where
Pα(z) =
(1 −|z|2)α+1
(1 −z)(1 −z)α+1
is the α-harmonic (complex valued) Poisson kernel in D. In the case α = 0
we have classiacal Poisson’s kernel for harmonic function and we write it as
P instead of P0. Also, we write P[f ∗] instead of P0[f ∗] for Piosson’s integral
of the function f ∗.
2. Lipschitz continuity for solutions of the ¯α-Poisson equation
2.1. An introductory result.
As a starting point of our investigation we used Theorem 2 which can be
found in Chen’s paper [7]. This theroem gives some rather strong assumption
on g = −Lαu (g ∈C(D)) as well as for boundary values of u (condition (d)
of Theorem 2), which are proven to be suﬃcient for Lipshitz continuity of u.
### Page 4

4
In order to formulate basic result we need to introduce some preliminary
notes. Let VD→Ω[g] denote the family of solutions of v : D →Ω, v ∈C2(D)
of the α-Poisson equation
 v(z) = f(z),
if z ∈T,
−(Lα)v(z) = g,
if z ∈D,
(2)
where g ∈C(D), f ∈L1(D) is the limit of v(reiθ) as r tends to 1−, and v is
a sense-preserving diﬀeomorphism.
For the case wherein the boundary function f vanishes, Behm [2] solved
the above Dirichlet boundary value problem of the α−Poisson equation. In
paper [3], Chen and Kalaj combined the representation theorem given by
Olofsson and Wittsten [29] with the one given by Behm. They obtained the
following theorem.
Theorem 1 ([3]). Let g ∈C(D) be such that (1−|z|2)α+1g belongs to L1(D),
wherein α > −1. If u ∈C2(D) is a solution of the equation −Lαu = g
satisfying the condition u(reit) converges to a function f ∈L1(T) as r →1−,
then for every w ∈D we have
u(w) = v(w) + Gα[g](w),
where
v(w)= 1
2π
Z
T
(1−|w|2)α+1
(1−zw)(1−zw)α+1 f(z) dθ,
Gα[g](w)=
ZZ
D
Gα(z, w)g(z) dx dy,
and the Green function Gα(z, w) of the adjoint Laplacian Lα is given by
Gα(z, w) = (1 −zw)αh(q(z, w))
2π
, with z ̸= w,
h(r) = 1
2
Z 1−r2
0
tα
1 −t dt, q(z, w) =

z −w
1 −wz
 .
In [7] Chen provided the boundary characterizations of a Lipschitz con-
tinuous α-harmonic mapping as follows
Deﬁne f(t) = f(eit) and
S[f](w) = 1
π
Z 2π
0
(1 −|w|2)α
(1 −zw)α
Im(wz)
|z −w|2 f(t)dt
(3)
where z = eit.
Theorem 2 ([7]). Assume that g ∈C(D) and u ∈VD→Ω[g] with the repre-
sentation u(w) = v(w) + Gα[g](w). If α ⩾0, then the following conditions
are equivalent:
(a) u is a (K, K’)-quasiconformal mapping and | ∂
∂rv| ≤L on D, and L
is a constant.
(b) u is Lipschitz continuous with the Euclidean metric.
(c) v is Lipschitz continuous with the Euclidean metric.
### Page 5

5
(d) f is absolutely continuous on T, f ′ ∈L∞and S[f′] is bounded on D.
In order to prove the main result of this paper we will need to prove two
reﬁnement of the result above.
2.2. Reﬁnement of part (d) in Theorem 2.
As we can see in [13], for p ∈(0, ∞], the generalized Hardy space Hp
G(D)
consists of all measurable functions from D to C such that Mp(r, f) exists
for all r ∈(0, 1), and ∥f∥p < ∞, where
Mp(r, f) =
 1
2π
Z 2π
0
|f(reiθ)|p dθ
 1
p
and
∥f∥p =
(
sup{Mp(r, f) : 0 < r < 1}
if p ∈(0, ∞),
sup{|f(z)| : z ∈D}
if p = ∞.
The classical Hardy space Hp(D) (resp. hp(D)) is the set of all elements
of Hp
G(D) which are analytic (resp. harmonic) on D.
Deﬁnition 3 ([27]). Let ψ ∈L1([0, 2π]). Then
H(ψ)(ϕ) = −1
2π
π
Z
0+
ψ(ϕ + t) −ψ(ϕ −t)
tan t/2
dt,
denotes the Hilbert transformations of ψ.
Recall that h(t) = h(eit). The following property of the Hilbert transform
is also sometimes taken as the deﬁnition:
Theorem 4 ([27]). If u = P[ψ] and v is the harmonic conjugate of u, then
v(t) = H(ψ)(t) a.e.
Note that, if ψ is 2π-periodic, absolutely continuous on [0, 2π] (and there-
fore ψ′ ∈L1[0, 2π]), then
∂h
∂θ = P[ψ′].
Hence, since r ∂
∂rh is the harmonic conjugate of
∂
∂θh, we ﬁnd
r∂h
∂r = P[H(ψ′)],
(4)
∂h
∂r
∗
(eiθ) = H(ψ′)(θ)
a.e.
(5)
Using the above outline we can derive:
### Page 6

6
Theorem 5. Let h be harmonic on U and h ∈h1(U). Then h is Lip iﬀ
h′ ∈L∞and H(h′) ∈L∞.
Let h be gradient harmonic or α-harmonic, α > 0, on U and h ∈h1(U).
Then h is Lip iﬀh′ ∈L∞.
The second part of the last theorem is a direct consequence of the ﬁrst
author’s result, together with A. Khalfallah, which is stated below.
Theorem 6 ([13]). Let α ∈(−1, ∞) with α ̸= 0 and let f = Pα[F] and F
is absolute continuous such that ˙F ∈Lp with 1 ⩽p ⩽∞.
(1) If α > 0, then
∂
∂zf and
∂
∂zf are in Hp
G(D) ⊂Lp(D).
(2) If α ∈(−1, 0), then
∂
∂zf and
∂
∂zf are in Lp(D) for p < −1
α.
(3) For α ∈(−1, 0) and p ⩾−1
α there exists f an α-harmonic function
such that
∂
∂zf and
∂
∂zf ̸∈Lp(D). Moreover,
∂
∂zf and
∂
∂zf ̸∈H1
G(D).
2.3. Reﬁnement of the condition on g = −Lαu in Theorem 2.
In this subsection we will prove that instead of g ∈C(D) we can use
assume that g ∈C(D) can be such that |g(z)| ⩽M(1 −|z|2)−α, z ∈D, in
oreder to prove Lipshitz continuity of α-Green integral Gα[g] of function g.
This fact will play an important part in the proof of our main result.
The following two estimates can be obtained by direct investigation of the
Green function Gα, and can be found in [7].
2π

∂
∂wGα(z, w)
 ⩽αCα|1 −zw|α−1
 
1−

z−w
1−wz

2!α+1  
1−log

z−w
1−wz

2!
+ (1 −|z|2)α+1(1 −|w|2)α
2|1 −zw|α+1|z −w|
,
(6)
2π

∂
∂wGα(z, w)
 ⩽(1 −|z|2)α+1(1 −|w|2)α
2|1 −zw|α+1|z −w|
.
(7)
In order to start with our work, we will prove the following two tehnical
lemmas.
Lemma 1. If β > 1 then
Z 2π
0
dt
|1 −rρeit|β ⪯
1
|1 −rρ|β−1
for 0 < r, ρ < 1.
### Page 7

7
Proof.
Z 2π
0
dt
|1 −rρeit|β = 2
Z π
0
dt
((1 −rρ)2 + 4rρ sin2 t
2)β/2
⩽
Z π
0
dt
((1 −rρ)2 + c1t2)β/2 ⩽|t = (1 −rρ)u|
⩽
Z π/(1−rρ)
0
(1 −rρ) du
(1 −rρ)β(1 + c1u2)β/2
⩽
1
(1 −rρ)β−1
Z ∞
0
du
(1 + c1u2)β/2 .
since the last integral converges, we have desired result.
□
Lemma 2. There exists c2 > 0 such that
M1(r) =
ZZ
D
dx dy
|z −r| ⩽c2
for every 0 < r < 1.
Proof. Let us use the supsitution z −r = ρeit, where 0 ⩽t < 2π, 0 < ρ <
ρ(t) = |r −eit| ⩽r + 1. Then
ZZ
D
dx dy
|z −r| =
Z 2π
0
dt
Z ρ(t)
0
ρ dρ
ρ
⩽
Z 2π
0
(r + 1) dt ⩽4π.
(8)
□
Let |w| = r,
I1(w) =
ZZ
D
(1 −|z|2)α+1(1 −|w|2)α
2|1 −zw|α+1|z −w|
dx dy,
I2(w) =
ZZ
D
|1−zw|α−1
 
1−

z−w
1−wz

2!α+1  
1−log

z−w
1−wz

2!
dx dy.
Also, inequalities
|1 −wζ| ⩾1 −|w|
and
|1 −wζ| ⩾1 −|ζ|
(9)
can easily be veryﬁed.
The following two lemmas are crucial for the main result of this section:
Lemma 3. There exists c3 > 0 such that
I1(w) ⩽c3(1 −|w|2)α
(10)
for every |w| < 1.
### Page 8

8
Proof. Using (9) we get
I1(w) ⪯(1 −|w|2)α
ZZ
D
dx dy
|z −w|.
Since we can use coordinate change s =
w
|w|z, we can use Lemma 2 to get
our result.
□
Let ζ = ϕw(z) = w−z
1−wz. Then, for each w ∈D, ϕw is a conformal mapping
of D satisfying the following identities:
z = w −ζ
1 −wζ , 1 −|z|2 = (1 −|z|2)(1 −|w|2)
|1 −wζ|2
,
(11)
1 −wz = 1 −|w|2
1 −wζ , dz = −1 −|w|2
(1 −wζ)2 dζ
Lemma 4. There exists c4 > 0 such that
I2(w) ⩽c4(1 −|w|2)α
(12)
for every |w| < 1.
Proof. By using supstitution s =
w
|w|ζ, and s = ρeit we get
I2(w) = I2(r) =
ZZ
D
(1 −|w|2)α+1(1 −|ζ|2)α+1
|1 −wζ|α+3
(1 −log |ζ|2) dξ dη
= (1−|w|2)α
Z 1
0
(1−ρ2)α+1(1−r2)(1−log ρ2)
Z 2π
0
dt
|1−rρeit|α+3 ρ dρ.
Using Lemma 1 we get
I2(r) ⪯(1 −|w|2)α
Z 1
0
(1 −ρ2)α+1(1 −r2)(1 −log ρ2)
|1 −rρ|α+2
ρ dρ.
Since 1 −rρ ⩾1 −r and 1 −rρ ⩾1 −ρ we have that
I2(r) ⪯(1 −|w|2)α
Z 1
0
ρ(1 −log ρ2) dρ ⩽c4(1 −|w|2)α
for some c4 > 0 which does not depent of 0 ⩽r < 1.
□
We are now ready to formulate the main result of this section, which is
generalisation of Lemma 3.4 in Chen’s paper [7]. The proof of this result
follows directly from Lemma 3 and Lemma 4.
Theorem 7. Let g ∈C(D) be such that |g(z)| ⩽M(1 −|z|2)−α, z ∈D for
some M > 0 and let α > 0 be arbitrary. Assume that Gα[g] is the Green
potential of g given by
Gα[g](w) =
ZZ
D
Gα(z, w)g(z) dx dy.
### Page 9

9
Then
∂
∂wGα[g] and
∂
∂wGα[g] are both bounded in the unit disc D.
As a ditect consequence of Theorem 7 and Theorem 5 we have the main
result of this paper.
Theorem 8. Assume that g ∈C(D) is such that (1−|z|2)αg is bounded and
u ∈VD→Ω[g] with the representation u(w) = v(w) + Gα[g](w). If α > 0, and
v is Lipshitz, then u is also Lipshitz continuous on D.
References
[1] M. Arsenovi´c, M. Mateljevi´c, Modulus of continuity of normal derivative of a harmonic
functions at a boundary point preprint 2022, accepted in Filomat, March 2023.
[2] Behm G. Solving Poisson equation for the standard weighted Laplacian in the unit
disc. arXiv:1306.2199v2, 2013.
[3] X. D. Chen, D. Kalaj, Representation theorem of standard weighted harmonic map-
pings in the unit disk. Https:// www.researchgate.net/publication/330243622, 2018.
[4] A. Gjokaj, D. Kalaj, QCH mappings between unit ball and domain with C1,α boundary,
2021, arXiv:2005.05667 [math.AP].
[5] A. Dall’Acqua, G. Sweers, Estimates for Green function and Poisson kernels of higher
order Dirichlet boundary value problems, Journal of Diﬀerential Equations, 205, no. 2,
2004, p. 466–487.
[6] X. Chen, D. Kalaj, A representation theorem for standard weighted harmonic map-
pings with an integer exponent and its applications, J. Math. Anal. Appl. 444, 2 (2016),
1233–1241.
[7] X. Chen, Lipschitz continuity for solutions of the ¯α-Poisson equation, Sci. China,
Math. 62, 10 (2019), 1935–1946.
[8] J. Chen, M. Huang, A. Rasila, X. Wang, On Lipschitz continuity of solutions of
hyperbolic Poisson’s equation, Calc. Var. Partial Diﬀer. Equ., 57, no. 1, 2018, p. 1–32.
[9] S. L. Chen and S. Ponnusamy, Schwarz’s lemmas for mappings satisfying Poisson’s
equation, Indag. Math., New Ser., 30 (2019), 1087-1098.
[10] S. L. Chen, S. Ponnusamy, X. T. Wang,Remarks on ’Norm estimates of the partial
derivatives for harmonic mappings and harmonic quasiregular mappings, J. Geom.
Anal. 31, 11051-11060 (2021).
[11] S. L. Chen, The Heinz type inequality, Bloch type theorem and Lipschitz characteristic
of polyharmonic mappings, to appear, March 2023.
[12] D. Gilbarg and N. Trudinger, Elliptic partial Diﬀerential Equation of Second Order,
Springer-Verlag, Berlin, Second Edition, 1983.
[13] A. Khalfallah, M. Mateljevi´c, Norm estimates of the partial derivatives and Schwarz
lemma for α-harmonic functions, Accepted in Complex Variables and Elliptic Equa-
tions.
[14] B. Hollenbeck and I. E. Verbitsky, Best Constants for the Riesz Projection, J. Fun.
Anal., 175 (2), 370-392. (2000)
[15] D. Kalaj, On Riesz type inequalities for harmonic mappings on the unit disk, Trans.
Am. Math. Soc. 372, No. 6, 4031-4051 (2019).
[16] P. Li, L. Tam, Uniqueness and Regularity of Proper Harmonic Maps II, Indiana Uni-
versity Mathematics Journal, 42 (2), 591–635 (1993).
[17] M. Mateljevi´c, The Lower Bound for the Modulus of the Derivatives and Jacobian
of Harmonic Injective Mappings. - Filomat 29:2, 2015, 221-244.
[18] M. Mateljevi´c, V. Boˇzin, M. Kneˇzevi´c: Quasiconformality of harmonic mappings
between Jordan domains, Filomat, Vol 24, No 3, 2010, 111-124.
### Page 10

10
[19] M. Mateljevi´c, N. Mutavdˇzi´c, On Lipschitz continuity and smoothness up to the bound-
ary of solutions of hyperbolic Poisson’s equation, arXiv:2208.06197v1 [math.CV] 12
Aug 2022.
[20] L. Ma, H¨older continuity of hyperbolic Poisson integral and hyperbolic Green integral,
Monatshefte f¨ur Mathematik, 199, 2022,
[21] M. Mateljevi´c, N. Mutavdˇzi´c, On Lipschitz continuity and smoothness up to the bound-
ary of solutions of hyperbolic Poisson’s equation, submitted for publication, September
2022.
[22] M. Mateljevi´c, N. Mutavdˇzi´c, The Boundary Schwarz lemma for harmonic and pluri-
harmonic mappings and some generalizations, accepted in Bulletin of the Malaysian
Mathematical Sciences Society, June 2022.
[23] M. Mateljevi´c, Boundary behaviour of partial derivatives for solutions to certain
Laplacian-gradient inequalities and spatial qc maps, Springer Proceedings in Math-
ematics & Statistics, 357, 2021, p. 393-418.
[24] M. Mateljevi´c, Boundary Behaviour Of Partial Derivatives For Solutions To Certain
Laplacian-Gradient Inequalities And Spatial Qc Maps 2, Preprint, Comunicated at
XII Symposium Mathematics and Applications, Mathematical Faculty, Belgrade, 2,3,
2022.
[25] M. Mateljevi´c, R. Salimov, E. Sevost’yanov, H¨older and Lipschitz continuity in Orlicz-
Sobolev classes, distortion and harmonic mappings, Filomat, 32 no. 16 p. 5361–5392.
[26] M. Mateljevi´c, E. Sevost’yanov, On the behavior of Orlicz-Sobolev mappings with
branching on the unit sphere, Ukr. Math. Bull 19(2022), No 4, 542-584; Journal of
Mathematical Sciences volume 270, pages 467-499 (2023).
[27] M. Mateljevi´c, Topics in Conformal, Quasiconformal and Harmonic maps, Zavod za
udzbenike, Beograd, 2012.
[28] C. A. Nodler, D. M. Oberlin, Moduli of continuity and a Hardy-Littlewood theorem,
Lecture Notes in Math. 1351, p. 265-272, Springer-Verlag, Berlin etc., 1988.
[29] A. Olofsson and J. Wittsten, Poisson integrals for standard weighted Laplacians in
the unit disc J. Math. Soc. Japan, 65 (2013), 447–486.
[30] M. Riesz, Sur les fonctions conjug´ees, Math. Zeit. 27, 218-244 (1927).
[31] W. Rudin, Real and complex analysis, McGraw-Hill Book Co, 1966.
[32] W. Rudin, Function Theory in the Unit Ball, Springer-Verlag, New York, 1980.
[33] E. M. Stein, Singular Integrals and Diﬀerentiability Properties of Functions,, Prince-
ton University Press, 1970.
[34] E. M. Stein, G. Weiss. Introduction to Fourier analysis on Euclidean spaces, Princeton
University Press, 1971.
[35] M. Stoll, Harmonic and Subharmonic Function Theory on the Hyperbolic Ball (London
Mathematical Society Lecture Note Series), Cambridge: Cambridge University Press
(2016).
[36] J. F. Zhu, Norm estimates of the partial derivatives for harmonic mappings and har-
monic quasiregular mappings, J. Geom. Anal., 31, 5505-5525 (2021)
[37] W. Kjell-Ove, Inequalities for the Green Function and Boundary Continuity of the
Gradient of Solutions of Elliptic Diﬀerential Equations, Mathematica Scandinavica,
21, No. 1 , 1967, p. 17–37.
[38] https://en.wikipedia.org/wiki/First-order partial diﬀerential equation
Faculty of mathematics, University of Belgrade, Studentski Trg 16, 11000
Belgrade, Serbia
Email address: miodrag@matf.bg.ac.rs, nikola.math@gmail.com