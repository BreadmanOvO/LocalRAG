# DAD Depth-aware BEV Multi-view 3D Object Detection

**Source**: arxiv PDF, 20 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

INVERSE SCATTERING TRANSFORM FOR THE INTEGRABLE FRACTIONAL DERIVATIVE
NONLINEAR SCHR ¨ODINGER EQUATION∗
LING AN†, LIMING LING‡, AND XIAOEN ZHANG§
Abstract. In this paper, we explore the integrable fractional derivative nonlinear Schr¨odinger (fDNLS) equation by using the
inverse scattering transform. Firstly, we start from the recursion operator and obtain a formal fDNLS equation. Then the inverse
scattering problem is formulated and solved through the matrix Riemann-Hilbert problem. Subsequently, we give the explicit form
of the fDNLS equation according to the properties of squared eigenfunctions, such as squared eigenfunctions are the eigenfunctions
of the recursion operator of the integrable equations. The reﬂectionless potential with a simple pole for the zero boundary condition
is carried out explicitly by means of determinants. Finally, for the fractional one-soliton solution, we analyze the wave propagation
direction and the effect of the small fractional parameter ϵ on the wave. The fractional one-soliton solution has been veriﬁed rigorously.
In addition, we also analyze the fractional rational solution obtained by taking the limit of the fractional one-soliton solution.
Key words. Fractional derivative nonlinear Schr¨odinger equation, recursion operator, inverse scattering transform, fractional
N-soliton solution, fractional rational solution.
MSC codes. 35Q15, 35Q51, 35Q55, 37K10, 37K15, 37K40.
1. Introduction. Fractional calculus has a very long history [29, 25, 31], originating from some con-
jectures of Leibniz and Euler. Fractional differential equations (FDEs) have been widely used to describe
various physical effects, such as abnormal dispersion [12, 39], long-time behavior, subthreshold neural
propagation [24], and so on [19, 34]. Moreover, FDEs have been divided into many types according to the
different deﬁnitions of fractional derivatives. Taking the well-known nonlinear Schr¨odinger (NLS) equation
as an example, there are several fractional forms [7, 20, 21]. While it should be noted that these fractional
equations are not integrable in the sense of inverse scattering transform (IST), which makes the obtained
FDEs not have as good properties as the integrable equations.
In 2022, Ablowitz, Been, and Carr proposed a new type of fractional equation, the fractional NLS equa-
tion and the fractional Korteweg-deVries (KdV) equation which are integrable in the sense of IST [2]. The
authors deﬁned the fractional operator based on the Riesz fractional derivative [6], which also can be called
Riesz transform [32] or fractional Laplacian [23], and a spectral representation for the fractional operator
is then obtained by using the completeness of squared eigenfunctions. Then they claimed that this type
of fractional equation could be applied to the whole Ablowitz-Kaup-Newell-Segur (AKNS) system [3].
Subsequently, the fractional forms of the higher-order modiﬁed KdV equation [41], the higher-order NLS
equation [35], and so on were studied. In [37], the author proposed a new integrable multi-L´evy-index and
mixed fractional nonlinear equations. In [42], the authors studied the integrable fractional equations via
deep learning with Fourier neural operator. In [9], the authors took the fractional coupled Hirota equation
as an example to explore the fractional integrable equation with 3 × 3 Lax equation. In [1], the authors
extended the fractional integrable partial differential equations to the discrete NLS equation. However,
the above integrable fractional equations are all related to the (discrete) AKNS system. Another signiﬁcant
integrable model named the derivative nonlinear Schr¨odinger (DNLS) equation:
(1.1)
iqt + qxx + i(|q|2q)x = 0,
which belongs to the Kaup-Newell (KN) system, plays a crucial role in the ﬁeld of integrable systems. So
the corresponding fractional extension of the KN system will be an interesting and natural problem in the
theory of the fractional integrable system. In the equation (1.1), |q| = (qq∗)
1
2 , q∗is the complex conjugate of
q, and the subscripts stand for partial derivative.
The DNLS equation was ﬁrst proposed in 1971 by Rogister [33], and later derived by Mjolhus [27],
Mio, and others [26] in 1976. This equation has many vital applications in different ﬁelds, such as long-
wavelength dynamics of dispersive Alfv´en waves in the plasma physics ﬁeld [33], the subpicosecond or
∗Funding: Liming Ling is supported by the National Natural Science Foundation of China (Grant No. 12122105); Xiaoen Zhang is
supported by the National Natural Science Foundation of China (Grant No.12101246).
†School of Mathematics, South China University of Technology, Guangzhou, China 510641 (maal@mail.scut.edu.cn).
‡School of Mathematics, South China University of Technology, Guangzhou, China 510641 (linglm@scut.edu.cn).
§School of Mathematics, South China University of Technology, Guangzhou, China 510641 (zhangxiaoen@scut.edu.cn).
1
arXiv:2303.17104v1  [nlin.SI]  30 Mar 2023
### Page 2

femtosecond pulse in a single-mode ﬁber [28], the propagation of nonlinear pulses in optical ﬁbers [5], and
so on. In mathematics, the DNLS equation also received much attention. Kaup and Newell gave the Lax
pair of this equation and solved it using the IST [15]. Furthermore, there are many other methods, such
as the Hirota method [14], the Darboux transformation [36, 13, 18], and so on, are also used to solve the
equation (1.1). Based on these results already obtained for the DNLS equation, we want to explore the
integrable fractional extension of the DNLS equation.
The organization of this paper is as follows. In Sec.2, we associate the KN spectral problem with a
family of integrable nonlinear equations by introducing the recursion operator L. Based on the idea in
[2], we extend the above set of integrable nonlinear equations to contain fractional integrable nonlinear
equations and give the operator function F f d(L) corresponding to the fractional DNLS (fDNLS) equation
by using the dispersion relation. Note that for the fractional integrable equation in the sense of IST, the
spectral matrix V(λ; x, t) related to time t can not be written in a closed form, while some constraints
should be added to it. Then, we use the IST to analyze some properties of eigenfunctions and scattering
matrix, which help us ﬁnd a completeness relation for the squared eigenfunctions of the fDNLS equation.
The completeness relation of the squared eigenfunctions provides a spectral representation of the recursion
operator L, which corresponds to the fDNLS equation, thus allows us to give the explicit form of the fDNLS
equation. In Sec.3, we explore the fractional N-soliton solution of the fDNLS equation. For the fractional
one-soliton solution, we analyze the wave peak, the moving direction of the wave, and the inﬂuence of
the small parameter ϵ in fractional power on wave propagation. We also analyze the fractional rational
solution by taking the limit of the fractional one-soliton solution. More importantly, we provide detailed
and rigorous proof of the fractional one-soliton solution.
2. The fDNLS equation and its IST. In this section, we will give the explicit form of the fDNLS equa-
tion, and solve this equation by IST. The construction of an integrable fractional equation requires three key
elements: the general evolution equation which can be solved by IST, the anomalous dispersion relation,
and the completeness of squared eigenfunctions.
The anomalous dispersion relation is related to the recursion operator, so we need to give the recursion
operator of the DNLS equation ﬁrst. From a matrix spectral problem with arbitrary parameters, we can
construct the generalized DNLS hierarchy [11]. Then the recursion operator of the DNLS equation can be
found. For convenience, we introduce three Pauli’s spin matrices:
σ1 =

0
1
1
0

,
σ2 =

0
−i
i
0

,
σ3 =

1
0
0
−1

.
Now we consider the following spectral problem:
Φx = UΦ,
U(λ; x, t) = −i(λ2 −αqr)σ3 + λQ(x, t),
Q(x, t) =
0
q
r
0

,
Φt = VΦ,
V(λ; x, t) =
"
V1
V2
V3
−V1
#
,
(2.1)
where Φ(λ; x, t) is the wave function, λ ∈C is the spectral parameter, α ∈R, q = q(x, t) and r = r(x, t) are
potential functions, Vj(λ; x, t), j = 1, 2, 3 are the quantities depending on q, r, and their derivatives.
The compatibility condition or the zero curvature equation of (2.1), reads
(2.2)
Ut −Vx + [U, V] = 0,
[U, V] ≡UV −VU,
which implies
iα(qr)t = V1x −λ(qV3 −rV2),
λqt = V2x + 2i(λ2 −αqr)V2 + 2λqV1,
λrt = V3x −2i(λ2 −αqr)V3 −2λrV1.
(2.3)
2
### Page 3

Combining with (2.3), there is
(2.4)
λ
q
r

t
= 2λV10σ3
q
r

+ (L1L2 + 2iλ2L3)σ3
V2
V3

,
where V10 is an integration constant,
L1 = I + 2iασ3
q
r

∂−1 
r,
q

,
L2 = σ3∂x −2iαqrI,
L3 = I + i(2α + 1)σ3
q
r

∂−1 
r,
q

.
We assume V10 = −2i(−λ2)n,
V2
V3

=
n
∑
j=1
(−1)n−j
V2j
V3j

λ2(n−j)+1,
substitute them into (2.4), and group terms according to their power of λ. Then we can get the set of
integrable nonlinear equations through the iterating calculation,
(2.5)
q
r

t
= −4iF(L)
 q
−r

,
F(L) = Ln,
where
L = 1
2iL1L2L−1
3
=1
2σ2σ1∂x −

α + 1
2

ux∂−1u⊤σ1 −

2α + 1
2

uu⊤σ1 + 1
2αu⊤σ1uI
−ασ3u∂−1u⊤
x σ1σ3 + α

2α + 1
2

σ2σ1u∂−1u⊤σ1uu⊤σ1,
u(x, t) =

q,
r
⊤, the superscript ⊤denotes the transpose. The system (2.5) is a generalized system,
which can yield many integrable equations by choosing different parameters n and α. For example, the
generalized DNLS hierarchy can be obtained by choosing n = 2 and r = σq∗(σ = ±1). Moreover, the cases
of α = 0, −1
2, −1
4 correspond to the DNLS equation, the Chen-Lee-Liu equation, and the Gerdjikov-Ivanov
equation, respectively. Note that F(L) can be generalized to the more general form F(λ) by using the
properties of squared eigenfunctions, and the function F(λ) can be associated with the linear dispersion
relation of (2.5). Without loss of generality, we will take the equation related to q(x, t) in (2.5) as an example
to deduce the relation between F(λ) and the linear dispersion relation. The linearized form of the equation
(2.5) can be given by
q
r

t
= −4iF
1
2σ2σ1∂x
  q
−r

,
F
1
2σ2σ1∂x

=
1
2σ2σ1∂x
n
,
then
(2.6)
qt(x, t) = −4i

−i
2∂x
n
q(x, t).
Then we substitute the formal solution q(x, t) ∼ei(λx−ω(λ)t) into (2.6), which yields
(2.7)
F
λ
2

= 1
4ω (λ) .
In this paper, we will study the fractional equation in the KN system based on the DNLS equation (1.1),
in which explicit forms for U(λ; x, t) and V(λ; x, t) are given by
U = −iλ2σ3 + λQ,
V = −2iλ4σ3 + 2λ3Q −iλ2σ3Q2 −λ(iσ3Qx −Q3),
3
### Page 4

where r(x, t) = −q∗(x, t). Let us rewrite the recursion operator L which corresponds to the DNLS equation
L = 1
2σ2σ1∂x −1
2ux∂−1
−u⊤σ1 −1
2uu⊤σ1,
∂−1
−=
Z x
−∞dy.
The DNLS equation corresponds to the operator function Fd(L) = L2. Based on the equation (2.7), there is
ωd = λ2. In [2], we can ﬁnd that the linear dispersion relation of the NLS equation is ωN(λ) = −λ2, then
the fractional NLS equation can be obtained according to ω f N(λ) = −λ2|λ|ϵ, ϵ ∈[0, 1). Following this rule,
we can assume that the anomalous dispersion relation of fDNLS equation is ω f d(λ) = λ2|λ|ϵ, ϵ ∈[0, 1).
Then the linearized form of the fDNLS equation is
iqt + | −∂2
x|
ϵ
2 qxx = 0,
where | −∂2|ϵ, ϵ ∈[0, 1) is called the Riesz fractional derivative [2]. Combining with the relation (2.7),
F f d(λ) = 1
4ω f d(2λ) = λ2|2λ|ϵ, ϵ ∈[0, 1).
This will lead to the operator function F f d(L) which corresponds to the fDNLS equation,
F f d(L) = L2|2L|ϵ, ϵ ∈[0, 1).
We will give the explicit form of the fDNLS equation in section 2.4.
2.1. Direct scattering. In the limit |x| →∞, we assume that the potential function q(x, t) is sufﬁciently
smooth and rapidly tends to zero. It is signiﬁcant that the matrix V(λ; x, t) cannot be written precisely for
the fractional integrable equation. But we need to impose a constraint V→−2iF f d(λ2)σ3, as |x|→∞on it.
The Lax pair of the fDNLS equation is
(2.8)
Φx = UΦ = (−iλ2σ3 + λQ)Φ,
Φt = VΦ,
Q(x, t) =

0
q(x, t)
−q∗(x, t)
0

.
Then we can derive the asymptotic behavior:
(2.9)
Φ± ∼e−iλ2σ3x,
x →±∞,
where Φ±(λ; x, t) =

φ±
1 ,
φ±
2

, the superscripts ± refer to the cases of x →±∞, respectively. Based on
Abel’s formula, we know that the determinants of Φ±(λ; x, t) are independent of x, since trQ(x, t) = 0.
Then we have
(2.10)
det Φ± =
lim
x→±∞det Φ± = 1.
Next we consider the Jost solutions Ψ±(λ; x, t) = Φ±(λ; x, t)eiλ2σ3x. Ψ±(λ; x, t) have the asymptotic prop-
erties: Ψ±(λ; x, t) →I, as x →±∞. Then we can get the equations of Ψ±(λ; x, t), which is equivalent to the
ﬁrst equation in (2.8)
(2.11)
Ψ±
x = −iλ2[σ3, Ψ±] + λQΨ±.
Moreover, the Volterra integral equations for Ψ±(λ; x, t) are given by
(2.12)
Ψ±(λ; x, t) = I + λ
Z x
±∞e−iλ2(x−y)adbσ3Q(y, t)Ψ±(λ; y, t)dy,
where Ψ±(λ; x, t) =

ψ±
1 ,
ψ±
2

, eadbσ3X = eσ3Xe−σ3 with X being a 2 × 2 matrix. The large-λ expansions of
the Jost solutions Ψ±(λ; x, t) are given by
Ψ±(λ; x, t) = exp

−iσ3
2
Z x
±∞|q(y, t)|2dy

+ O(λ−1).
4
### Page 5

ℜ(λ)
ℑ(λ)
•
×λk
×
−λ∗
k
×
−λk
×λ∗
k
Σ1
Σ2
Σ4
Σ3
Σ3
Σ4
Σ2
Σ1
Γ1
Γ4
Γ3
Γ2
× λr
×
−λr
FIG. 1. Complex λ-plane. The grey and white regions represent D+ and D−, respectively. Σ+ = Σ1 + Σ3, Σ−= Σ2 + Σ4. Γ+ =
Γ1 + Γ3, Γ−= Γ2 + Γ4. Discrete spectrum, and the integral path for IST of the fDNLS equation. λr and −λr are the discrete spectrum
corresponding to the fractional rational solution.
According to the Volterra integral equations (2.12), the relevant properties of Ψ±(λ; x, t) or Φ±(λ; x, t) can
be analyzed, which are summarized in the following proposition. Similar results have been reported in
[40], so we will not prove them.
PROPOSITION 2.1. (see Lemma 1 in [30]) Assume that q(x, t) ∈L1(R) ∩L3(R) and ∂xq(x, t) ∈L1(R),
then there exist unique solutions satisfying the Volterra integral equations (2.12) for every λ ∈Σ, and the Jost
solutions Ψ±(λ; x, t) possesses the following properties:
• The column vectors ψ−
1 and ψ+
2 are analytic for λ ∈D+ and continuous for λ ∈D+ ∪Σ,
• The column vectors ψ+
1 and ψ−
2 are analytic for λ ∈D−and continuous for λ ∈D−∪Σ,
where Σ = R ∪iR, D± are shown in Fig.1.
Both Φ±(λ; x, t) are the fundamental solutions of (2.8), then there exists a matrix S(λ; t) =
 sij(λ; t)

i,j=1,2
between them obeying the relation:
(2.13)
Φ−(λ; x, t) = Φ+(λ; x, t)S(λ; t),
λ ∈Σ,
and S(λ; t) is called the scattering matrix, sij(λ; t), i, j = 1, 2 are called the scattering coefﬁcients. Moreover,
det S(λ; t)=1 can be deduced from (2.10). As usual, we deﬁne the reﬂection coefﬁcients ρ1(λ; t) and ρ2(λ; t):
(2.14)
ρ1(λ; t) = s21(λ; t)
s11(λ; t),
ρ2(λ; t) = s12(λ; t)
s22(λ; t),
λ ∈Σ.
In addition, the large-λ expansion of S(λ; t) is
S(λ; t) = exp

−iσ3
2
Z +∞
−∞|q(y, t)|2dy

+ O(λ−1).
By using (2.13), there are
s11(λ; t) = Wr(φ−
1 , φ+
2 ),
s12(λ; t) = Wr(φ−
2 , φ+
2 ),
s21(λ; t) = Wr(φ+
1 , φ−
1 ),
s22(λ; t) = Wr(φ+
1 , φ−
2 ).
(2.15)
Therefore, s11(λ; t) and s22(λ; t) are analytic in D±, respectively. Generally, the off-diagonal scattering
coefﬁcients cannot be extended off the contour Σ.
PROPOSITION 2.2. The fundamental solution Φ(λ; x, t), the Jost solution Ψ(λ; x, t), and the scattering matrix
S(λ; t) all have two symmetry reductions:
• Φ(λ; x, t) = σ2Φ∗(λ∗; x, t)σ2, Ψ(λ; x, t) = σ2Ψ∗(λ∗; x, t)σ2, S(λ; t) = σ2S∗(λ∗; t)σ2.
• Φ(λ; x, t) = σ3Φ(−λ; x, t)σ3,
Ψ(λ; x, t) = σ3Ψ(−λ; x, t)σ3, S(λ; t) = σ3S(−λ; t)σ3.
5
### Page 6

Proof. It is easy to ﬁnd the symmetry reductions of the matrix U(λ; x, t), and therefore the symmetry
reductions of Φ(λ; x, t) can be obtained according to the equation (2.8). And the symmetry reductions of
Ψ(λ; x, t) and S(λ; t) can also be directly deduced via equations (2.11) and (2.13).
According to the symmetry properties of S(λ; t) in proposition 2.2, we can derive s11(λ; t)=s11(−λ; t)
=s∗
22(λ∗; t)=s∗
22(−λ∗; t). Then the zeros of s11(λ; t) appear in pairs, and we can suppose that s11(λ; t) has
simple zeros deﬁned by λn, n=1, 2, · · · , N in the I quadrant, and λn+N= −λn in the III quadrant. That is
to say, s11(λj; t)=0, s
′
11(λj; t)̸=0, j=1, 2, · · · , 2N, the superscript
′ denotes the partial derivative with respect
to λ. Then s22(λ∗
j ; t)=0, s
′
22(λ∗
j ; t)̸=0, j=1, 2, · · · , 2N. So the discrete spectrum can be deﬁned by the set:
Λ =

λk, −λk, λ∗
k, −λ∗
k
	N
k=1,
whose distributions are shown in Fig.1. Based on the equation (2.15), it can be seen that when s11(λj; t) =
0, j = 1, 2, · · · , 2N, φ−
1 (λj; x, t) and φ+
2 (λj; x, t) must be proportional
(2.16)
φ−
1 (λj; x, t) = aj(λj; t)φ+
2 (λj; x, t),
j = 1, 2, · · · , 2N,
where aj(λj; t) := aj ̸= 0. Similarly, when s22(λ∗
j ; t)=0, j=1, 2, · · · , 2N, there is
(2.17)
φ−
2 (λ∗
j ; x, t) = bj(λ∗
j ; t)φ+
1 (λ∗
j ; x, t),
j = 1, 2, · · · , 2N,
where bj(λ∗
j ; t) := bj ̸= 0. Furthermore, the relations aj = −b∗
j , aj+N = −aj can be derived by combining
(2.16), (2.17), together with the symmetry reductions of Φ(λ; x, t) in proposition 2.2.
2.2. Time evolution. The time evolution of the scattering data can be obtained by analyzing the asymp-
totic behavior of the associated time evolution operator V(λ; x, t), which cannot be represented generally.
From the section 2.1, we know V→−2iF f d(λ2)σ3 as |x|→∞, then
s11(λ; t) = s11(λ; 0),
s12(λ; t) = e4iF f d(λ2)ts12(λ; 0),
s22(λ; t) = s22(λ; 0),
s21(λ; t) = e−4iF f d(λ2)ts21(λ; 0).
In addition, there are
aj(λj; t) = e−4iF f d(λ2
j )taj(λj; 0),
bj(λ∗
j ; t) = e4iF f d(λ∗2
j )tbj(λ∗
j ; 0).
2.3. Inverse scattering. Now we consider the inverse problem in terms of the relation (2.13). By re-
viewing the analytic properties of Ψ±(λ; x, t), we can deﬁne a sectional analytic matrix M(λ; x, t):
M+(λ; x, t) =
ψ−
1 (λ; x, t)
s11(λ; t) ,
ψ+
2 (λ; x, t)

,
λ ∈D+,
M−(λ; x, t) =

ψ+
1 (λ; x, t),
ψ−
2 (λ; x, t)
s22(λ; t)

,
λ ∈D−.
(2.18)
Then we can formulate the following Riemann-Hilbert problem.
RIEMANN-HILBERT PROBLEM 1. We can ﬁnd the matrix M(λ; x, t) with the following properties:
• Analyticity : M±(λ; x, t) are sectionally meromorphic in D±\Λ, and have the simple poles in Λ, whose
principal parts of the Laurent series at each simple pole λk or λ∗
k, are determined as
Res
λ=λk
M(λ; x, t) =
"
akψ+
2 (λk; x, t)
s
′
11(λk; t)
exp

2i

λ2
kx + 2F f d(λ2
k)t

,
0
#
,
Res
λ=λ∗
k
M(λ; x, t) =
"
0,
bkψ+
1 (λ∗
k; x, t)
s
′
22(λ∗
k; t)
exp

−2i

λ∗2
k x + 2F f d(λ∗2
k )t
#
,
where the superscript
′ denotes the partial derivative with respect to λ.
6
### Page 7

• Jump condition : M(λ; x, t) satisﬁes the jump condition:
M+(λ; x, t) = M−(λ; x, t) (I −J(λ; x, t)) , λ ∈Σ,
where
J(λ; x, t) = exp

−i
 λ2x + 2F f d(λ2)t

adbσ3
 "
ρ1(λ; t)ρ2(λ; t)
ρ2(λ; t)
−ρ1(λ; t)
0
#
.
• Asymptotic behavior :
M(λ; x, t) = exp
iσ3
2
Z +∞
x
|q(y, t)|2dy

+ O(λ−1),
as λ →∞.
To solve the above Riemann-Hilbert problem, we need to regularize it by subtracting the pole contributions
and the asymptotic behavior. So we deﬁne a new matrix M[1](λ; x, t) as follows:
M[1]
± (λ; x, t)=M±(λ; x, t)−exp
iσ3
2
Z +∞
x
|q(y, t)|2dy

−
2N
∑
k=1



Res
λ=λk
M(λ; x, t)
λ −λk
+
Res
λ=λ∗
k
M(λ; x, t)
λ −λ∗
k


, λ ∈D±.
Note that M[1]
± (λ; x, t) are sectionally meromorphic in D±, and M[1](λ; x, t) = O(λ−1) as λ →∞. Moreover,
(2.19)
M[1]
+ (λ; x, t) −M[1]
−(λ; x, t) = −M−(λ; x, t)J(λ; x, t), λ ∈Σ.
Here we introduce the Cauchy projectors P± over Σ [10] deﬁned by
P±[ f ](λ) =
1
2πi
Z
Σ
f (ζ)
ζ −(λ ± i0)dζ,
where the notation λ ± i0 indicates that the limit is taken from the left/right of λ along the direction. Based
on the Plemelj’s formulae, there are P± f± = ± f±, P+ f−= P−f+ = 0, when f± are analytic in D±, and are
equal to O(λ−1) as λ →∞. And we introduce the notations Σ±, which refer to the integral paths along the
gray area and the white area indicated by arrows in Fig.1. Applying the Cauchy projectors to the equation
(2.19), there is
M[1]
± (λ; x, t) = −1
2πi
Z
Σ±
M−(ζ; x, t)J(ζ; x, t)
ζ −(λ ± i0)
dζ.
Therefore,
M±(λ; x, t) = exp
iσ3
2
Z +∞
x
|q(y, t)|2dy

−
1
2πi
Z
Σ±
M−(ζ; x, t)J(ζ; x, t)
ζ −(λ ± i0)
dζ
+
2N
∑
k=1
"
ckψ+
2 (λk; x, t)
λ −λk
exp

2i
 λ2
kx + 2F f d(λ2
k)t

, dkψ+
1 (λ∗
k; x, t)
λ −λ∗
k
exp

−2i
 λ∗2
k x + 2F f d(λ∗2
k )t
#
,
(2.20)
where ck=ck(λk; t)=
ak
s′
11(λk;t), dk=dk(λ∗
k; t)=
bk
s′
22(λ∗
k;t). Combining with the symmetries of S(λ; t) and the re-
lations of ak and bk, we can deduce
dk(λ∗
k; t) = −c∗
k(λk; t) = −c∗
k(−λk; t),
ck+N(λk+N; t) = ck(λk; t).
Then we can recover the potential function q(x, t) from M+(λ; x, t). Firstly, we expand M+(λ; x, t) at
large-λ as
(2.21)
M+(λ; x, t) = M+,0(x, t) + M+,1(x, t)
λ
+ O(λ−2),
7
### Page 8

and we know
M+,0(x, t) = exp
iσ3
2
Z +∞
x
|q(y, t)|2dy

,
M+,1(x, t) =
1
2πi
Z
Σ+
M−(ζ; x, t)J(ζ; x, t)dζ +
2N
∑
k=1
h
ckψ+
2 (λk; x, t) exp

2i

λ2
kx + 2F f d(λ2
k)t

,
dkψ+
1 (λ∗
k; x, t) exp

−2i

λ∗2
k x + 2F f d(λ∗2
k )t
 i
.
Then the potential function q(x, t) can be recovered by substituting the expansion of M+(λ; x, t) (i.e.(2.21))
into (2.11), and collecting the same powers of λ. We derive
Q(x, t) = i

σ3, M+,1(x, t)
 (M+,0(x, t))−1.
Therefore,
q(x, t) = exp
 i
2
Z +∞
x
|q(y, t)|2dy
  1
π
Z
Σ+

M−(ζ; x, t)J(ζ; x, t)

12dζ
+ 2i
2N
∑
k=1
dkψ+
11(λ∗
k; x, t) exp

−2i
 λ∗2
k x + 2F f d(λ∗2
k )t
 
.
Next we will try to give the explicit expressions for s11(λ; t) and s22(λ; t) by constructing a new analytic
function β(λ; t):
β+(λ; t) = s11(λ; t) exp
 i
2
Z +∞
−∞|q(y, t)|2dy
 2N
∏
k=1
λ −λ∗
k
λ −λk
,
λ ∈D+,
β−(λ; t) = s22(λ; t) exp

−i
2
Z +∞
−∞|q(y, t)|2dy
 2N
∏
k=1
λ −λk
λ −λ∗
k
,
λ ∈D−.
Obviously, β±(λ; t) are analytic in D±, and β±(λ; t) →1 as λ →∞. In addition, we have the relation:
log β+(λ; t) + log β−(λ; t) = −log

1 −ρ1(λ; t)ρ2(λ; t)

,
λ ∈Σ.
Applying the Cauchy projectors to the above equation, we can get
log β±(λ; t) = ∓1
2πi
Z
Σ±
log

1 −ρ1(ζ; t)ρ2(ζ; t)

ζ −(λ ± i0)
dζ.
Then the expressions of s11(λ; t) and s22(λ; t) are as follows:
s11(λ; t) = exp
 
−
1
2πi
Z
Σ+
log

1 −ρ1(ζ; t)ρ2(ζ; t)

ζ −(λ + i0)
dζ −i
2
Z +∞
−∞|q(y, t)|2dy
!
2N
∏
k=1
λ −λk
λ −λ∗
k
,
s22(λ; t) = exp
 
1
2πi
Z
Σ−
log

1 −ρ1(ζ; t)ρ2(ζ; t)

ζ −(λ −i0)
dζ + i
2
Z +∞
−∞|q(y, t)|2dy
!
2N
∏
k=1
λ −λ∗
k
λ −λk
.
2.4. Explicit form of the fDNLS equation. In order to ﬁnd the explicit form of the fDNLS equation,
the ﬁrst question to consider is how the recursion operator function F f d(L) acts on functions. Note that
squared eigenfunctions are eigenfunctions of the recursion operator of integrable equations. So we can let
the recursion operator L act on squared eigenfunctions, and then generalize this to the case of recursion
8
### Page 9

operator function F f d(L). Then we need to consider how to connect squared eigenfunctions with potential
functions, which can be achieved through the completeness of squared eigenfunctions. The completeness
of squared eigenfunctions of the fDNLS equation is closely related to the perturbation theory (or variational
relations) [38], which can be found in detail in the literatures [16, 17], and we will be brieﬂy described below.
Firstly, we introduce squared eigenfunctions Ωj(λ; x, t) =
h
φ2
1j(λ; x, t),
φ2
2j(λ; x, t)
i⊤
, where
Ω+,1 =
"
(φ−
11)2
(φ−
21)2
#
,
Ω+,2 =
"
(φ+
12)2
(φ+
22)2
#
,
Ω−,1 =
"
(φ+
11)2
(φ+
21)2
#
,
Ω−,2 =
"
(φ−
12)2
(φ−
22)2
#
,
the subscripts ± indicate that the functions Ω±,j(λ; x, t) are analytic in D±, respectively. And we can calcu-
late that Ωj(λ; x, t) satisﬁes
(2.22)
Ωj,x(λ; x, t) + 2iλ2σ3Ωj(λ; x, t) = −λ

φj(λ; x, t)
σ3
φj(λ; x, t)

σ1w(x, t),
where w(x, t) =
−q∗,
q
⊤, the “ket” |v⟩represents a usual column vector v = |v⟩=

v1,
v2
⊤, and the
“bra” ⟨v| =
−v2,
v1

is its adjoint raw vector. Through a direct calculation, we can derive L(σ3∂xΩj) =
−λ2σ3∂xΩj, here the recursion operator L corresponds to the DNLS equation. Then we generalize it to
F f d(L)(σ3∂xΩj) = F f d(−λ2)σ3∂xΩj.
Next, we will deduce the variational relations of the fDNLS equation. Let us consider a perturbation
∆Q(x, t) for the ﬁrst equation of (2.1), then the corresponding variation of ∆Φ±(λ; x, t) can be described as
∆Φ±
x (λ; x, t) = U(λ; x, t)∆Φ±(λ; x, t) + λ∆Q(x, t)Φ±(λ; x, t),
∆Φ±(λ; x, t) →0, as x →±∞.
The above equation can be easily solved
(2.23)
∆Φ±(λ; x, t) = Φ±(λ; x, t)
Z x
±∞λ
 Φ±(λ; y, t)
−1∆Q(y, t)Φ±(λ; y, t)dy.
On the other hand, considering the variation of (2.13), we can derive
(2.24)
∆S(λ; t) =

Φ+(λ; x, t)−1  ∆Φ−(λ; x, t) −∆Φ+(λ; x, t)S(λ; t)

.
Then substituting (2.23) into (2.24), and combining the relation (2.13),
∆S(λ; t) =
Z ∞
−∞λ
 Φ+(λ; y, t)
−1∆Q(y, t)Φ−(λ; y, t)dy.
Combining with the above equation, we can obtain
∆ρ1(λ; t) = 1
s2
11
 s11∆s21 −s21∆s11
 =
λ
s2
11(λ; t)
Z +∞
−∞

Ω+,1(λ; y, t)
σ1
∆w(y, t)

dy,
∆ρ2(λ; t) = 1
s2
22
 s22∆s12 −s12∆s22
 = −
λ
s2
22(λ; t)
Z +∞
−∞

Ω−,2(λ; y, t)
σ1
∆w(y, t)

dy.
(2.25)
Equation (2.25) can be regarded as a mapping from ∆q(x, t) to ∆ρj(λ; t). And then we wish to construct its
inverse mapping by discussing two integrals.
The ﬁrst integral is
(2.26)
En(x, t) =
1
2πi
Z
E λndλ
Z ∞
−∞G(λ; x, y, t)v(y, t)dy,
n = 0, 1, 2,
where E is a contour path enclosing the whole region of the λ-plane, v(x, t) is an arbitrary smooth vector
function, G(λ; x, y, t) is called the Green function which will be given bellow. As shown in Fig.1, the path
9
### Page 10

E can be divided into two half-circular paths Γ± or two contour paths Γ± + Σ±, i.e. E = Γ+ −Γ−=
(Γ+ + Σ+) −(Γ−+ Σ−). The Green function G(λ; x, y, t) is deﬁned as follows:
Gx(λ; x, y, t) −U(λ; x, t)G(λ; x, y, t) = δ(x −y)I,
where δ(z) is a Dirac’s δ-function, and we choose the following two kinds of Green functions, whose de-
tailed construction procedure can be found in Appendix-A in [16],
Gp(λ; x, y, t) =







φ+
2 (λ; x, t)

1
s11(λ; t)

φ−
1 (λ; y, t)
,
y ≤x,
φ−
1 (λ; x, t)

1
s11(λ; t)

φ+
2 (λ; y, t)
,
y ≥x,
Gn(λ; x, y, t) =







−
φ+
1 (λ; x, t)

1
s22(λ; t)

φ−
2 (λ; y, t)
,
y ≤x,
−
φ−
2 (λ; x, t)

1
s22(λ; t)

φ+
1 (λ; y, t)
,
y ≥x,
where Gp(λ; x, y, t) and Gn(λ; x, y, t) are deﬁned on D±, respectively. By calculation, we get
(2.27)
E0(x, t) = 0,
E1(x, t) = −iσ3v(x, t),
E2(x, t) = Q(x, t)v(x, t).
And based on the relations (2.13) and (2.14), we can rewrite the integral (2.26) as
(2.28)
En(x, t) =
1
2πi
Z ∞
−∞
 Z
Γ−+Σ−
φ+
1 (λ; x, t)

ρ2(λ; t)

φ+
1 (λ; y, t)
λndλ
+
Z
Γ++Σ+
φ+
2 (λ; x, t)

ρ1(λ; t)

φ+
2 (λ; y, t)
λndλ −
Z
Σ+
φ+(λ; x, t)

ρ(λ; t)

φ+(λ; y, t)
λndλ

v(y, t)dy,
where
(2.29)
φ+(λ; x, t)

ρ(λ; t)

φ+(λ; y, t)
 =
φ+
1 (λ; x, t)

φ+
2 (λ; y, t)
 +
φ+
2 (λ; x, t)

φ+
1 (λ; y, t)

+
φ+
1 (λ; x, t)

ρ2(λ; t)

φ+
1 (λ; y, t)
 +
φ+
2 (λ; x, t)

ρ1(λ; t)

φ+
2 (λ; y, t)
.
Combining with equations (2.27) and (2.28), we can get the completeness of the fundamental solutions
(2.30)
F0(x, y, t) = 0,
F1(x, y, t) = σ3δ(x −y),
F2(x, y, t) = iQ(x, t)δ(x −y),
where
(2.31)
Fn(x, y, t) = 1
2π
 Z
Γ−+Σ−
φ+
1 (λ; x, t)

ρ2(λ; t)

φ+
1 (λ; y, t)
λndλ
+
Z
Γ++Σ+
φ+
2 (λ; x, t)

ρ1(λ; t)

φ+
2 (λ; y, t)
λndλ −
Z
Σ+
φ+(λ; x, t)

ρ(λ; t)

φ+(λ; y, t)
λndλ

.
The second integral is
(2.32)
−1
2π
Z
Σ+
eφ+(λ; x, t)
eρ(λ; t)

φ+(λ; y, t)
λndλ,
n = 0, 1,
where
eφ+(λ; x, t)
eρ(λ; t)

φ+(λ; y, t)
 is deﬁned in the same way as (2.29). To facilitate the discussion of
the above integral, we need to introduce the integral representations of Φ(λ; x, t) and eΦ(λ; x, t), which are
10
### Page 11

the fundamental solutions of the Lax pairs corresponding to the potential functions Q(x, t) and eQ(x, t) =
Q + ∆Q, respectively. By combining these integral representations and their inverse forms, we can get
(2.33)
eφ+
j (λ; x, t)
 = K(x, t)
φ+
j (λ; x, t)
 −
Z +∞
x
 Ld(x, y, t) + λLo(x, y, t)
φ+
j (λ; y, t)

dy, j = 1, 2,
(2.34)

φ+
j (λ; x, t)
 =

eφ+
j (λ; x, t)
eKA(x, t) −
Z +∞
x

eφ+
j (λ; y, t)
 eLA
d (x, y, t) + λeLA
o (x, y, t)

dy, j = 1, 2,
where K and Ld are diagonal, Lo is off-diagonal, the superscript A refers to the adjoint matrix, and
(2.35) K(x, t) = exp
 i
2
Z +∞
x
 | ˜q(y, t)|2 −|q(y, t)|2
dyσ3

, 2Lo(x, x, t) = eQ(x, t)K(x, t) −K(x, t)Q(x, t).
For the case of eQ(x, t), we distinguish all related quantities by marking a “tilde”. Then we discuss the
integral (2.32) when n = 1 from two aspects, the ﬁrst is to substitute (2.33) into (2.32) for simpliﬁcation, the
second is to substitute (2.34) into (2.32), and then combining with (2.30), (2.31), (2.33) for simpliﬁcation. By
comparing the integrals obtained by different simpliﬁcation methods, we can get
(2.36)
Z +∞
x

Ld(x, z, t)
 F1(z, y, t) + W1(z, y, t)
 + Lo(x, z, t)
 F2(z, y, t) + W2(z, y, t)

dz
= K(x, t)
 F1(x, y, t) + W1(x, y, t)

,
x ̸= y,
where ∆ρ(λ; t) = eρ(λ; t) −ρ(λ; t),
Wn(x, y, t) = 1
2π
 Z
Γ+
φ+
2 (λ; x, t)

∆ρ1(λ; t)

φ+
2 (λ; y, t)
λndλ
+
Z
Γ−
φ+
1 (λ; x, t)

∆ρ2(λ; t)

φ+
1 (λ; y, t)
λndλ

.
(2.37)
According to the symmetry properties of Φ(λ; x, t) and S(λ; t) in proposition 2.2, we can ﬁnd that W1 is
diagonal, W0 and W2 are off-diagonal. Based on (2.30), the equation (2.36) can be rewritten as
K(x, t)W1(x, y, t) −
Z +∞
x

Ld(x, z, t)W1(z, y, t) + Lo(x, z, t)W2(z, y, t)

dz
−Ld(x, y, t)σ3 −iLo(x, y, t)Q(y, t) = 0,
x ̸= y,
which is the generalized Gel’fand-Levitan (G-L) equation. Similarly, considering the integral (2.32) when
n = 0, we can deduce another generalized G-L equation:
K(x, t)W0(x, y, t) −
Z +∞
x

Ld(x, z, t)W0(z, y, t) + Lo(x, z, t)W1(z, y, t)

dz −Lo(x, y, t)σ3 = 0, x ̸= y.
Based on the above preparations, we will construct the mapping from ∆ρj(λ; t) to ∆q(x, t). We use the
notation δγ, a quantity related to γ, to represent ∥δγ ∥is sufﬁciently small. Note that for sufﬁciently small
∥∆ρj(λ; t)∥, j = 1, 2, the generalized G-L equations can be reduced to the linear equations,
(2.38)
Ld(x, y, t)σ3 = K(x, t)W1(x, y, t) −iLo(x, y, t)Q(y, t),
Lo(x, y, t)σ3 = K(x, t)W0(x, y, t).
According to (2.35), (2.38) and the deﬁnition of Wn(x, y, t) (i.e.(2.37)), we can get two different expressions
for
 W0(x, x, t)

12,
 W0(x, x, t)

21
⊤. Comparing these two expressions, we can derive
σ1δw(x, t) = −1
π
Z
Γ+
Ω+,2(λ; x, t)δρ1(λ; t)dλ +
Z
Γ−
Ω−,1(λ; x, t)δρ2(λ; t)dλ

+ i
Z +∞
x

w(y, t)
σ3
δw(y, t)

dy σ3σ1w(x, t).
(2.39)
11
### Page 12

A direct calculation yields

φ+
1 (λ; x, t)|σ3|φ+
1 (λ; x, t)
 = −2λ
Z +∞
x

w(y, t)|σ1σ3|Ω−,1(λ; y, t)

dy,

φ+
2 (λ; x, t)|σ3|φ+
2 (λ; x, t)
 = −2λ
Z +∞
x

w(y, t)|σ1σ3|Ω+,2(λ; y, t)

dy.
(2.40)
Based on (2.40), the equation (2.39) can be rewritten as:
(2.41)
Z +∞
x

w(y, t)
σ3
δw(y, t)

dy = 1
2π
 Z
Γ+
δρ1(λ; t)
λ

φ+
2 (λ; x, t)|σ3|φ+
2 (λ; x, t)

dλ
+
Z
Γ−
δρ2(λ; t)
λ

φ+
1 (λ; x, t)|σ3|φ+
1 (λ; x, t)

dλ

.
Substituting (2.22) and (2.41) into (2.39) gives
(2.42)
δw(x, t) = −σ2
2π
Z
Γ+
δρ1(λ; t)
λ2
∂xΩ+,2(λ; x, t)dλ +
Z
Γ−
δρ2(λ; t)
λ2
∂xΩ−,1(λ; x, t)dλ

.
Based on the time evolution of S(λ; t), the time evolution of δρj(λ; t), j = 1, 2 are found to be
(2.43)
δρ1(λ; t) = e−4iF f d(λ2)tδρj(λ; 0),
δρ2(λ; t) = e4iF f d(λ2)tδρ2(λ; 0).
Combining with (2.43) and substituting (2.25) into (2.42),
(2.44)
δw(x, t) = −σ2
2π
 Z
Γ+
1
λs2
11(λ; t) ∂xΩ+,2(λ; x, t)
Z +∞
−∞

Ω+,1(λ; y, t)
σ1
δw(y, t)

dydλ
−
Z
Γ−
1
λs2
22(λ; t) ∂xΩ−,1(λ; x, t)
Z +∞
−∞

Ω−,2(λ; y, t)
σ1
δw(y, t)

dydλ

.
Furthermore,
(2.45)
δw(x, t) =
Z +∞
−∞δ(x −y)δw(y, t)dy.
Then we can get a completeness relation of squared eigenfunctions by comparing (2.44) with (2.45),
σ3δ(x −y) =
1
2πi
 Z
Γ+
1
λs2
11(λ; t)
 ∂x
Ω+,2(λ; x, t)
 
Ω+,1(λ; y, t)
dλ
−
Z
Γ−
1
λs2
22(λ; t)
 ∂x
Ω−,1(λ; x, t)
 
Ω−,2(λ; y, t)
dλ

.
Based on the equation (2.44), we can assume a sufﬁciently smooth and decaying vector function ϑ(x, t) =

ϑ1,
ϑ2
⊤, which can also be expanded in terms of the eigenfunctions. We choose ϑ(x, t) =

q∗,
q
⊤, and
let F f d(L) act on it, then there is
(2.46)
F f d(L)

q∗
q

= −σ2
2π
 Z
Γ+
λ3|2λ2|ϵ
s2
11(λ; t)
"
(φ+
12)2
(φ+
22)2
#
x
Z +∞
−∞
 φ−
11
2q∗−
 φ−
21
2q

dydλ
−
Z
Γ−
λ3|2λ2|ϵ
s2
22(λ; t)
"
(φ+
11)2
(φ+
21)2
#
x
Z +∞
−∞
 φ−
12
2q∗−
 φ−
22
2q

dydλ

,
12
### Page 13

in the integral terms of (2.46), q=q(y, t), q∗=q∗(y, t), φ+
jk=φ+
jk(λ; x, t), φ−
jk=φ−
jk(λ; y, t), j, k=1, 2. Then the
explicit form of the fDNLS equation can be given by combining with the equation (2.5),
qt(x, t) = −2
π
 Z
Γ+
λ3|2λ2|ϵ
s2
11(λ; t) ∂x(φ+
12(λ; x, t))2
Z +∞
−∞
 φ−
11(λ; y, t)
2q∗(y, t) −
 φ−
21(λ; y, t)
2q(y, t)

dydλ
−
Z
Γ−
λ3|2λ2|ϵ
s2
22(λ; t) ∂x(φ+
11(λ; x, t))2
Z +∞
−∞
 φ−
12(λ; y, t)
2q∗(y, t) −
 φ−
22(λ; y, t)
2q(y, t)

dydλ

,
(2.47)
in the integral of the above equation, q = q(y, t), q∗= q∗(y, t), φ+
1k = φ+
1k(λ; x, t), φ−
jk = φ−
jk(λ; y, t), j, k =
1, 2. In particular, the equation (2.47) will degenerate into the classical DNLS equation when ϵ = 0.
3. Fractional N-soliton solution. In this section, we want to explore the fractional N-soliton solution of
the fDNLS equation, which leads us to start with the case of reﬂectionless potential: ρ1(λ; t) = ρ2(λ; t) = 0.
Then there is J(λ; x, t) = 0, so
s11(λ; t)= exp

−i
2
Z +∞
−∞|q(y, t)|2dy
 2N
∏
k=1
λ −λk
λ −λ∗
k
, s22(λ; t)= exp
 i
2
Z +∞
−∞|q(y, t)|2dy
 2N
∏
k=1
λ −λ∗
k
λ −λk
,
and
(3.1)
q(x, t) = 2i exp
 i
2
Z +∞
x
|q(y, t)|2dy
 2N
∑
k=1
dkψ+
11(λ∗
k; x, t) exp

−2i
 λ∗2
k x + 2F f d(λ∗2
k )t

.
Since the equation (3.1) contains the unknown function ψ+
11(λ∗
k; x, t), so we will look for the expression for
this function. Based on the deﬁnitions of M±(λ; x, t) (i.e.(2.18)) and their explicit forms (i.e.(2.20)), we can
derive
(3.2)
ψ+
11(λ; x, t) = exp
 i
2
Z +∞
x
|q(y, t)|2dy

+
2N
∑
k=1
ck
λ −λk
exp

2i
 λ2
kx + 2F f d(λ2
k)t

ψ+
12(λk; x, t),
(3.3)
ψ+
12(λ; x, t) =
2N
∑
k=1
dk
λ −λ∗
k
exp

−2i
 λ∗2
k x + 2F f d(λ∗2
k )t

ψ+
11(λ∗
k; x, t).
Taking λ = λk in (3.3), and substituting it into (3.2). Then taking λ = λ∗
k,
ψ+
11(λ∗
k; x, t) = exp
 i
2
Z +∞
x
|q(y, t)|2dy

−
2N
∑
j=1
2N
∑
l=1

cldj
(λl −λ∗
k)(λl −λ∗
j )ψ+
11(λ∗
j ; x, t)
× exp

2i
 (λ2
l −λ∗2
j )x + 2
 F f d(λ2
l ) −F f d(λ∗2
j )

t

.
Using the method as in [40], the solution to the above equation can be expressed as follows:
(3.4)
ψ+
11(λ∗
k; x, t) = exp
 i
2
Z +∞
x
|q(y, t)|2dy
 det eRk
det R ,
where R = I +
2N
∑
l=1
R0,l, the element at the position (j, k), j, k = 1, · · · , 2N of the matrix R0,l is
(R0,l)j,k =
cldk
(λl −λ∗
j )(λl −λ∗
k) exp

2i
 (λ2
l −λ∗2
k )x + 2
 F f d(λ2
l ) −F f d(λ∗2
k )

t

,
13
### Page 14

eRk is replacing the k-th column of the matrix R with the column vector e = [ 1, 1, · · · , 1
|
{z
}
2N
]⊤. Based on the
equation (3.4), the function q(x, t) in (3.1) becomes
q(x, t) = 2i exp

i
Z +∞
x
|q(y, t)|2dy
 2N
∑
k=1
dk exp

−2i
 λ∗2
k x + 2F f d(λ∗2
k )t
 det eRk
det R .
We denote dk exp

−2i
 λ∗2
k x + 2F f d(λ∗2
k )t

= edk, then the above equation can be rewritten as
(3.5)
q(x, t) = −2i exp

i
Z +∞
x
|q(y, t)|2dy
 det Re
det R ,
Re =

0
ed
e
R

,
ed =
h
ed1,
ed2,
· · · ,
ed2N
i
.
Obviously, the equation (3.5) is an implicit one, and we need further analysis to get an explicit form of
q(x, t). Note that the above analyses were discussed as λ →∞, and we can also consider the expansion of
λ →0 by using the same method. Combining with the idea in [40], we can get another representation of
M(λ; x, t),
M(λ; x, t) = I + λ
2N
∑
k=1




Res
λ=λk
M(λ;x,t)
λ
λ −λk
+
Res
λ=λ∗
k
M(λ;x,t)
λ
λ −λ∗
k




= I+λ
2N
∑
k=1
"
ckψ+
2 (λk; x, t)
λk(λ −λk)
exp

2i

λ2
kx+2F f d(λ2
k)t

, dkψ+
1 (λ∗
k; x, t)
λ∗
k(λ −λ∗
k)
exp

−2i

λ∗2
k x+2F f d(λ∗2
k )t
#
.
(3.6)
Now we based on the deﬁnitions of M±(λ; x, t) (i.e.(2.18)) and their explicit forms (i.e.(3.6)) to reconsider
the explicit form of ψ+
11(λ∗
k; x, t). Similarly, we can obtain another equation related to ψ+
11(λ∗
k; x, t)
ψ+
11(λ∗
k; x, t) = 1 −λ∗
k
2N
∑
j=1
2N
∑
l=1

cldj
(λl −λ∗
k)(λl −λ∗
j )λ∗
j
ψ+
11(λ∗
j ; x, t)
× exp

2i
 (λ2
l −λ∗2
j )x + 2
 F f d(λ2
l ) −F f d(λ∗2
j )

t

,
which can be solved explicitly by
(3.7)
ψ+
11(λ∗
k; x, t) = det eTk
det T ,
where T = I +
2N
∑
l=1
T0,l, the (j, k)-element of the matrix T0,l is given by
(T0,l)j,k =
cldkλ∗
j
(λl −λ∗
j )(λl −λ∗
k)λ∗
k
exp

2i
 (λ2
l −λ∗2
k )x + 2

F f d(λ2
l ) −F f d(λ∗2
k )

t

,
and eTk is the matrix T by replacing the k-th column with the column vector e. Substituting (3.7) into (3.1),
q(x, t) = 2i exp
 i
2
Z +∞
x
|q(y, t)|2dy
 2N
∑
k=1
dk exp

−2i
 λ∗2
k x + 2F f d(λ∗2
k )t
 det eTk
det T .
Similarly, we denote dk exp

−2i
 λ∗2
k x + 2F f d(λ∗2
k )t

= edk, then the above equation can be rewritten as
(3.8)
q(x, t) = −2i exp
 i
2
Z +∞
x
|q(y, t)|2dy
 det Te
det T ,
Te =

0
ed
e
T

.
14
### Page 15

Comparing (3.5) with (3.8), there is
(3.9)
exp
 i
2
Z +∞
x
|q(y, t)|2dy

= det Te det R
det Re det T.
Substituting (3.9) into the equation (3.5) or (3.8), then the explicit form of the fractional N-soliton solution
can be derived
(3.10)
q(x, t) = −2i
det Te
det T
2 det R
det Re .
When N = 1, we choose the spectral parameter λ1 = ξ + iη, which implies λ2 = −ξ −iη. Then the
fractional one-soliton solution can be obtained according to the equation (3.10), which is summarized in the
following proposition. And we will prove this fractional one-soliton solution solves the fDNLS equation.
PROPOSITION 3.1. The expression of the fractional one-soliton solution of the fDNLS equation (2.47) is as fol-
lows:
(3.11)
q[1](x, t) = −2ic1 exp (ω1 + θ∗−2θ) cosh (ω2 + θ∗) sech2 (ω2 + θ) ,
where eθ = c1(ξ −iη)
2ξη
,
ω1(x, t) = −2i

(ξ2 −η2)x + 21+ϵ(ξ4 + η4 −6ξ2η2)(ξ2 + η2)ϵt

,
ω2(x, t) = −4ξη

x + 22+ϵ(ξ2 −η2)(ξ2 + η2)ϵt

.
Proof. For convenience, we assume θ = θR + iθI. By observing the equation (2.47), it can be found that
we ﬁrst need to give the functions φ±
jk(λ; x, t), j, k = 1, 2, which correspond to the solution q[1](x, t). After
careful consideration, we believe that it is most convenient to ﬁnd the expression of φ±
jk(λ; x, t) by using the
Darboux transform method. By modifying the form of the Darboux matrix in [13] properly, we obtain the
one-fold Darboux matrix corresponds to the Lax pair of (2.47)
D = I −λλ∗
1

A
λ −λ∗
1
+ σ3Aσ3
λ + λ∗
1

,
where
A = λ2
1 −λ∗2
1
2|λ1|2
"
α1
0
0
α2
#
ϕ1ϕ†
1,
α−1
1
= ϕ†
1
"
λ1
0
0
λ∗
1
#
ϕ1,
α−1
2
= ϕ†
1
"
λ∗
1
0
0
λ1
#
ϕ1,
ϕ1 =

−i exp

−iλ2
1
 x + 2λ2
1|2λ2
1|ϵt
 −θR+3iθI
2

exp

iλ2
1
 x + 2λ2
1|2λ2
1|ϵt
 + θR+3iθI
2


,
the superscript † denotes the complex conjugation and vector transpose. And the transformation between
the potential function q(x, t) and the new potential function q[1](x, t) is
(3.12)
q[1] = q + (A −σ3Aσ3)12,x.
Note that the fractional one-soliton solution q[1](x, t) obtained by Darboux transform method (i.e.(3.12)
is consistent with the solution obtained by IST (i.e.(3.11)). Then the new eigenfunctions Φ±[1](λ; x, t) :=
bΦ±(λ; x, t) which correspond to the solution q[1](x, t) can be derived by applying the asymptotic behavior
15
### Page 16

(2.9) and the relation bΦ± = DΦ±
0 ,
bΦ =
(ξ−iη)
(ξ + iη)(λ + ξ −iη)(λ −ξ + iη)
×


 λ2 cosh(ω2+θ∗)sech(ω2+θ)−(ξ2+η2)

eδ
c1λ exp(ω1−θR−3iθI)sech(ω2+θ)e−δ
c1λ exp(−ω1−θR+3iθI)sech(ω2+θ∗)eδ
 λ2 cosh(ω2+θ)sech(ω2+θ∗)−(ξ2+η2)

e−δ

,
bΦ+=bΦ


(ξ + iη)2(λ + ξ −iη)(λ −ξ + iη)
(ξ −iη)2(λ −ξ −iη)(λ + ξ + iη)
0
0
1

, bΦ−=bΦ


1
0
0
(ξ + iη)2(λ + ξ −iη)(λ −ξ + iη)
(ξ −iη)2(λ −ξ −iη)(λ + ξ + iη)

,
(3.13)
where Φ0(λ; x, t) = diag(eδ, e−δ), δ = −iλ2(x + 2λ2|2λ2|ϵt).
Next, we will prove that q[1](x, t) (i.e.(3.11)) is a solution of the equation (2.47). Firstly, we want to
calculate the integral part of the equation (2.47) on Γ+, i.e.,
Z
Γ+
λ3|2λ2|ϵ
s2
11(λ; t) ∂x
 bφ+
12(λ; x, t)
2 Z +∞
−∞
 bφ−
11(λ; y, t)
2 
q[1](y, t)
∗
−
 bφ−
21(λ; y, t)
2 q[1](y, t)

dydλ
:=
Z
Γ+
g(λ; x, t)
s2
11(λ; t) dλ,
(3.14)
where g(λ; x, t) = g1(λ; x, t) R +∞
−∞g2(λ; y, t)dy,
g1(λ; x, t) = λ3|2λ2|ϵ∂x
 bφ+
12(λ; x, t)
2 ,
g2(λ; y, t) =
 bφ−
11(λ; y, t)
2 
q[1](y, t)
∗
−
 bφ−
21(λ; y, t)
2 q[1](y, t).
Combining with the residue theorem, we can decompose (3.14) into continuous and discrete parts. The
function g(λ; x, t) is analytic in D+, so the residues in (3.14) come from the zeros of s11(λ; t), which occur at
λ1 = ξ + iη and λ2 = −ξ −iη. Then we have
Z
Γ+
g(λ; x, t)
s2
11(λ; t) dλ = −
Z
Σ+
g(λ; x, t)
s2
11(λ; t) dλ + 2πi
2
∑
j=1
Res
λ=λj
g(λ; x, t)
s2
11(λ; t)
= −
Z
Σ+
g(λ; x, t)
s2
11(λ; t) dλ + 2πi
2
∑
j=1
 
g
′(λj; x, t)
s
′2
11(λj; t) −g(λj; x, t)s
′′
11(λj)
s
′3
11(λj; t)
!
,
(3.15)
here the superscript
′ also denotes the partial derivative with respect to λ. Through some analyses and
calculations, we ﬁnd that the above equation only needs to calculate the ﬁrst part of the discrete spectrum,
which comes from R +∞
−∞g2(λ; y, t)dy = 0 for all λ. In fact, based on (3.11) and (3.13),
g2(λ; y, t) =2ic1(ξ −iη)2 exp(−θR + 3iθI −ω1 + 2δ)
 (ξ + iη)(λ + ξ −iη)(λ −ξ + iη)
2

λ4sech(ω2 + θ) −2λ2(ξ2 + η2)sech(ω2 + θ∗)
+ (ξ2 + η2)2 cosh(ω2 + θ)sech2(ω2 + θ∗) + c2
1λ2e−2θRsech(ω2 + θ∗)sech2(ω2 + θ)

.
We introduce the transformation z = ω2 + θR, then the above equation can be rewritten as
g2(λ; z, t) = 2ic1(ξ −iη)2 exp(−θR + 3iθI + bδ)
 (ξ + iη)(λ + ξ −iη)(λ −ξ + iη)
2

λ4sech(z + iθI) −2λ2(ξ2 + η2)sech(z −iθI)
+ (ξ2 + η2)2 cosh(z + iθI)sech2(z −iθI) + c2
1λ2e−2θRsech(z −iθI)sech2(z + iθI)

,
bδ = i22+ϵ 
2λ2(ξ2 −η2)(ξ2 + η2)ϵ −(ξ2 + η2)2+ϵ −|λ2|ϵλ4
t + i(ξ2 −η2 −λ2)θR
2ξη
.
16
### Page 17

ℜ(z)
ℑ(z)
0
•
−R
R
R + iπ
−R + iπ
CB
CT
CL
CR
iπ
2
•
iπ
2 −iθI×
iπ
2 + iθI
×
•
•
•
•
FIG. 2. z-plane
Therefore,
Z +∞
−∞g2(λ; y, t)dy =
−ic1(ξ −iη)2 exp(−θR + 3iθI + bδ)
2ξη
 (ξ + iη)(λ + ξ −iη)(λ −ξ + iη)
2
Z +∞
−∞
bg2(λ; z, t)dz,
bg2(λ; z, t) = exp
i(λ2 −ξ2 + η2)z
2ξη
 
λ4sech(z + iθI) −2λ2(ξ2 + η2)sech(z −iθI)
+ (ξ2 + η2)2 cosh(z + iθI)sech2(z −iθI) + c2
1λ2e−2θRsech(z −iθI)sech2(z + iθI)

.
We consider bg2(λ; z, t) on the matrix contour in Fig.2, there is
Z
CB
bg2(z)dz +
Z
CR
bg2(z)dz +
Z
CT
bg2(z)dz +
Z
CL
bg2(z)dz = 2πi
 
Res
z= iπ
2 +iθI
bg2(z) +
Res
z= iπ
2 −iθI
bg2(z)
!
.
By observation, we can ﬁnd the integral over CL and CR vanish as R →∞, and the integral over CT can be
written in terms of the integral over CB as
Z
CT
bg2(z)dz = exp
−(λ2 −ξ2 + η2)π
2ξη
 Z
CB
bg2(z)dz,
then

1 + exp
−(λ2 −ξ2 + η2)π
2ξη
 Z
CB
bg2(z)dz = 2πi
 
Res
z= iπ
2 +iθI
bg2(z) +
Res
z= iπ
2 −iθI
bg2(z)
!
.
While the residues of bg2(z) vanish at z = iπ
2 ± iθI. Thus, R
CB bg2(z)dz = 0, which leads to R +∞
−∞g2(λ; y, t)dy =
0. Combining with the expression for s11(λ; t), we can rewrite (3.15) as
Z
Γ+
g(λ; x, t)
s2
11(λ; t) dλ = 2πi
2
∑
j=1
g′(λj; x, t)
s
′2
11(λj; t) = −16iπξ2η2(ξ + iη)2
(ξ −iη)4
g′(λ1; x, t).
So we only need to calculate g′(λ1; x, t), and in fact, g′(λ1; x, t) = g1(λ1; x, t) R ∞
−∞g
′
2(λ1; x, t)dy. Through
calculations, we can get
g′(λ1; x, t) =
i(ξ2 + η2)2(ξ −iη)2eω1−3iθI
4ξ3η3 (ξ −iη)eω2+θR + (ξ + iη)e−ω2−θR

c2
1(ξ2 + η2)2e2ω2 + 4ξ2η2(ξ2 −6iξη −η2)

.
Therefore,
(3.16)
Z
Γ+
g(λ; x, t)
s2
11(λ; t) dλ=2ϵ(ξ2+η2)ϵsech3(ω2+θ)eω1
 
πc2
1(ξ+iη)6
2ξη(ξ−iη) e2ω2+2πξη(ξ+iη)4(ξ2−6iξη−η2)
(ξ−iη)3
!
.
17
### Page 18

Using the same method as in calculating the integral on Γ+, we can also calculate the integral part of
the equation (2.47) on Γ−, and here we give the result directly,
Z
Γ−
λ3|2λ2|ϵ
s2
22(λ; t) ∂x
 bφ+
11(λ; x, t)
2 Z +∞
−∞
 bφ−
12(λ; y, t)
2 
q[1](y, t)
∗
−
 bφ−
22(λ; y, t)
2 q[1](y, t)

dydλ
= −2ϵ(ξ2 + η2)ϵsech3(ω2 + θ)eω1 ×
 
8πξ3η3(ξ −iη)
c2
1
e−2ω2 + 2πξη(ξ −iη)(ξ2 + 6iξη −η2)
!
.
(3.17)
In addition, according to the equation (3.11), we can directly obtain the derivative of q[1](x, t) with
respect to t,
q[1]
t (x, t) = −2ϵ(ξ2 + η2)ϵsech3(ω2 + θ)eω1
c2
1(ξ + iη)6
ξη(ξ −iη) e2ω2 + 16ξ3η3(ξ −iη)
c2
1
e−2ω2
+ 8ξη(ξ2 −η2)(ξ4 + 18ξ2η2 + η4)
(ξ −iη)3

.
(3.18)
By substituting (3.16), (3.17), and (3.18) into the equation (2.47), it can be found that the left and right sides
are equal. This proves that q[1](x, t) (i.e.(3.11)) satisﬁes the equation (2.47).
Next, we will analyze the properties of the solution q[1](x, t). In terms of (3.11), we can easily obtain the
expression for the modular square of the solution q[1](x, t),
|q[1](x, t)|2 =
32ξ2η2
(ξ2 + η2) cosh(2ω2 + 2θR) + ξ2 −η2 .
Furthermore, we can derive the maximum value of |q[1](x, t)| is 4η. By selecting appropriate parameters,
we give the relevant ﬁgures corresponding to |q[1](x, t)| in Fig.3. From the left column in Fig.3, we can
ﬁnd that the soliton is a left-going traveling-wave soliton. And with the increase of ϵ, the velocity of the
traveling wave will be faster, which can be observed from the right column in Fig.3.
-40
-20
0
20
40
x
0
0.2
0.4
0.6
0.8
1
=0.4
 t=-25
 t=0
 t=25
10
20
30
x
0
0.2
0.4
0.6
0.8
1
t=-25
=0
=0.4
=0.8
FIG. 3. The direction of wave propagation. Choosing the parameters: ξ = 0.5, η = 0.2, c1 = 1.
In addition, if we take the limit of the soliton solution, we can also obtain the rational solution [36,
13]. By considering ξ →0 in the fractional one-soliton solution (3.11), we ﬁnd that the fractional rational
solution q[1]
r (x, t) will occur when c1 = ±2ξ →0. Then we have
(3.19)
q[1]
r (x, t) = ∓4iη exp

2iη2 
x −(2η2)1+ϵt

4η2  x −2(2η2)1+ϵt
 + i
(4η2 (x −2(2η2)1+ϵt) −i)2 ,
with the arbitrary real constants ϵ and η. Obviously, the fractional rational solution (3.19) is a linear soliton
with the center along the line x=2(2η2)1+ϵt. The amplitude of |q[1]
r (x, t)| is 4η as well as |q[1](x, t)|. Here we
18
### Page 19

choose the same parameter η=0.2 as in Fig.3. In Fig.4, we can observe that unlike the fractional one-soliton
solution q[1](x, t), this linear soliton is a right-going traveling-wave soliton. At the same time, the velocity
of the traveling wave will also be faster as the increase of ϵ. Note that when |x|→∞, |q[1]
r (x, t)| will tend to
zero for arbitrary ﬁxed t.
-50
0
50
x
0
0.2
0.4
0.6
0.8
1
=0.4
t=-100
t=0
t=100
-50
0
50
x
0
0.2
0.4
0.6
0.8
1
t=-100
=0
=0.4
=0.8
FIG. 4. The direction of wave propagation. Choosing the parameter: η = 0.2.
4. Conclusion. In conclusion, based on the fractional integrable equation of the AKNS system pro-
posed by Ablowitz, Been, and Carr, we extend it to the KN system in the sense of the Riesz fractional
derivative. We study the fractional DNLS equation in detail and obtain the fractional N-soliton solution ac-
cording to the IST method. In addition, we give the explicit form of the fractional one-soliton solution and
provide rigorous proof by combined with the Darboux transformation in [13]. And from the right panel
in Fig.3, we ﬁnd that the fractional solitons propagate without dissipating or spreading out. Moreover, we
discuss the limitations of the fractional one-soliton solution and get the fractional rational solution of the
fDNLS equation. These phenomena will signiﬁcantly enrich the dynamic properties of integrable systems
and help predict the superdispersive transport of nonlinear waves in fractional nonlinear media.
Note that we only proved the fractional one-soliton solution. The fractional two-soliton solution and
even the fractional N-soliton solution can also be veriﬁed via a similar method, but the computations will
become more complicated. Therefore, ﬁnding a more convenient method to prove the solution is necessary.
In addition, the nonlocal equation is also a hot research topic in the integrable system [4, 8, 22]. It is worth
considering whether the nonlocal and fractional integrable equations can be studied together.
REFERENCES
[1] M. J. ABLOWITZ, J. B. BEEN, AND L. D. CARR, Fractional integrable and related discrete nonlinear Schr¨odinger equations, Phys. Lett.
A, 452 (2022), p. 128459.
[2]
, Fractional Integrable Nonlinear Soliton Equations, Phys. Rev. Lett., 128 (2022), p. 184101.
[3]
, Integrable Fractional Modiﬁed Korteweg-de Vries, Sine-Gordon, and Sinh-Gordon Equations, J. Phys. A, 55 (2022), p. 384010.
[4] M. J. ABLOWITZ AND Z. H. MUSSLIMANI, Integrable nonlocal nonlinear equations, Stud. Appl. Math., 139 (2016), pp. 7–59.
[5] G. AGRAWAL, Applications of nonlinear ﬁber optics, Elsevier, 2001.
[6] O. P. AGRAWAL, Fractional variational calculus in terms of Riesz fractional derivatives, J. Phys. A, 40 (2007), p. 6287.
[7] U. AL KHAWAJA, M. AL-REFAI, G. SHCHEDRIN, AND L. D. CARR, High-accuracy power series solutions with arbitrarily large radius
of convergence for the fractional nonlinear Schr¨odinger-type equations, J. Phys. A, 51 (2018), p. 235201.
[8] L. AN, C. LI, AND L. ZHANG, Darboux transformations and solutions of nonlocal Hirota and Maxwell-Bloch equations, Stud. Appl.
Math., 147 (2021), pp. 60–83.
[9] L. AN, L. LING, AND X. ZHANG, Nondegenerate solitons in the integrable fractional coupled Hirota equation, Phys. Lett. A, 460 (2023),
p. 128629.
[10] G. BIONDINI AND G. KOVA ˇCI ˇC, Inverse scattering transform for the focusing nonlinear Schr¨odinger equation with nonzero boundary
conditions, J. Math. Phys., 55 (2014), p. 031506.
[11] E. FAN, Integrable systems of derivative nonlinear Schr¨odinger type and their multi-Hamiltonian structure, J. Phys. A, 34 (2001), p. 513.
[12] R. K. GAZIZOV, A. A. KASATKIN, AND S. Y. LUKASHCHUK, Symmetry properties of fractional diffusion equations, Phys. Scr., 2009
(2009), p. 014016.
[13] B. GUO, L. LING, AND Q. P. LIU, High-order solutions and generalized Darboux transformations of derivative nonlinear Schr¨odinger
equations, Stud. Appl. Math., 130 (2013), pp. 317–344.
[14] S. KAKEI, N. SASA, AND J. SATSUMA, Bilinearization of a generalized derivative nonlinear Schr¨odinger equation, J. Phys. Soc. Jpn., 64
19
### Page 20

(1995), pp. 1519–1523.
[15] D. J. KAUP AND A. C. NEWELL, An exact solution for a derivative nonlinear Schr¨odinger equation, J. Math. Phys., 19 (1978), pp. 798–
801.
[16] T. KAWATA AND J. SAKAI, Generalized Gel’fand-Levitan Equation and Variational Relations of the Kaup-Newell Equation, Res. Rep.,
463 (1980), pp. 1–27.
[17]
, Linear problems associated with the Derivative Nonlinear Schr¨odinger equation, J. Phys. Soc. Jpn., 49 (1980), pp. 2407–2414.
[18] C. M. KHALIQUE, K. PLAATJIE, AND O. D. ADEYEMO, First integrals, solutions and conservation laws of the derivative nonlinear
Schr¨odinger equation, Partial Differ Equ Appl Math, 5 (2022), p. 100382.
[19] A. A. KILBAS, H. M. SRIVASTAVA, AND J. J. TRUJILLO, Theory and applications of fractional differential equations, Elsevier, 2006.
[20] P. LI, B. A. MALOMED, AND D. MIHALACHE, Vortex solitons in fractional nonlinear Schr¨odinger equation with the cubic-quintic
nonlinearity, Chaos Solitons Fractals, 137 (2020), p. 109783.
[21]
, Symmetry-breaking bifurcations and ghost states in the fractional nonlinear Schr¨odinger equation with a PT-symmetric potential,
Opt. Lett., 46 (2021), pp. 3267–3270.
[22] L. LING AND W. X. MA, Inverse scattering and soliton solutions of nonlocal complex reverse-spacetime modiﬁed Korteweg-de Vries
hierarchies, Symmetry, 13 (2021), p. 512.
[23] A. LISCHKE, G. PANG, M. GULIAN, F. SONG, C. GLUSA, X. ZHENG, Z. MAO, W. CAI, M. M. MEERSCHAERT, M. AINSWORTH,
ET AL., What is the fractional Laplacian? A comparative review with new results, J. Comput. Phys., 404 (2020), p. 109009.
[24] R. MAGIN, Fractional calculus in bioengineering, Crit. Rev. Biomed. Eng., 32 (2004), pp. 1–104.
[25] K. S. MILLER AND B. ROSS, An introduction to the fractional calculus and fractional differential equations, Wiley, 1993.
[26] K. MIO, T. OGINO, K. MINAMI, AND S. TAKEDA, Modiﬁed nonlinear Schr¨odinger equation for Alfv´en waves propagating along the
magnetic ﬁeld in cold plasmas, J. Phys. Soc. Japan, 41 (1976), pp. 265–271.
[27] E. MJØLHUS, On the modulational instability of hydromagnetic waves parallel to the magnetic ﬁeld, J. Plasma Phys., 16 (1976), pp. 321–
334.
[28] K. OHKUMA, Y. H. ICHIKAWA, AND Y. ABE, Soliton propagation along optical ﬁbers, Opt. Lett., 12 (1987), pp. 516–518.
[29] K. B. OLDHAM AND J. SPANIER, Application of Fractional Calculus for Dynamic Problems of Solid Mechanics: Novel Trends and Recent
Results the Fractional Calculus, Academic Press, New York, (1974).
[30] D. E. PELINOVSKY AND Y. SHIMABUKURO, Existence of global solutions to the derivative NLS equation with the inverse scattering
transform method, Int. Math. Res. Not. IMRN, 2018 (2018), pp. 5663–5728.
[31] I. PODLUBNY, Fractional differential equations, Math. Sci. Eng., 198 (1999), pp. 41–119.
[32] M. RIESZ, L’int´egrale de Riemann-Liouville et le probl`eme de Cauchy, Acta Math., 81 (1949), pp. 1–222.
[33] A. ROGISTER, Parallel propagation of nonlinear low-frequency waves in high-β plasma, Phys Fluids, 14 (1971), pp. 2733–2739.
[34] V. E. TARASOV, Fractional dynamics: applications of fractional calculus to dynamics of particles, ﬁelds and media, Springer, 2011.
[35] W. WENG, M. ZHANG, G. ZHANG, AND Z. YAN, Dynamics of fractional N-soliton solutions with anomalous dispersions of integrable
fractional higher-order nonlinear Schr¨odinger equations, Chaos, 32 (2022), p. 123110.
[36] S. XU, J. HE, AND L. WANG, The Darboux transformation of the derivative nonlinear Schr¨odinger equation, J. Phys. A, 44 (2011),
p. 305203.
[37] Z. YAN, New integrable multi-L´evy-index and mixed fractional nonlinear soliton hierarchies, Chaos Solitons Fractals, 164 (2022),
p. 112758.
[38] J. YANG, Nonlinear waves in integrable and nonintegrable systems, SIAM, 2010.
[39] X. J. YANG AND J. A. T. MACHADO, A new fractional operator of variable order: application in the description of anomalous diffusion,
Phys. A, 481 (2017), pp. 276–283.
[40] G. ZHANG AND Z. YAN, The derivative nonlinear Schr¨odinger equation with zero/nonzero boundary conditions: inverse scattering
transforms and N-double-pole solutions, J. Nonlinear Sci., 30 (2020), pp. 3089–3127.
[41] M. ZHANG, W. WENG, AND Z. YAN, Interactions of fractional N-solitons with anomalous dispersions for the integrable combined
fractional higher-order mKdV hierarchy, Phys. D, 444 (2023), p. 133614.
[42] M. ZHONG AND Z. YAN, Data-driven soliton mappings for integrable fractional nonlinear wave equations via deep learning with Fourier
neural operator, Chaos Solitons Fractals, 165 (2022), p. 112787.
20