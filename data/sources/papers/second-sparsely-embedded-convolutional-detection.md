# SECOND Sparsely Embedded Convolutional Detection

**Source**: arxiv PDF, 6 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

arXiv:1803.05958v1  [gr-qc]  15 Mar 2018
Description of gravity in the model with independent
nonsymmetric connection
N. V. Kharuk∗, S. A. Paston†, A. A. Sheykin ‡
Saint Petersburg State University, Saint Petersburg, Russia
Abstract
A generalization of General Relativity is studied. The standard Einstein-Hilbert ac-
tion is considered in the Palatini formalism, where the connection and the metric are
independent variables, and the connection is not symmetric. As a result of variation with
respect to the metric Einstein equations are obtained. A variation with respect to the
connection leads to an arbitrariness in the determination of connection, i.e. the presence
of gauge invariance. Then a matter in a form of point particle which interacts with ﬁeld
of connection is introduced. Also the action is complemented by a kinetic term for ﬁeld
of the connection to avoid incompatible equation of motion.
Thus after the variation
procedures we obtain the Einstein equations, the geodesic equation and the Maxwell’s
equations for electromagnetism, where some components of the connection play the role
of the electromagnetic potential. Thereby the electromagnetic potential is obtained from
the geometry of space-time.
∗natakharuk@mail.ru
†s.paston@spbu.ru
‡a.sheykin@spbu.ru
1
### Page 2

1
Introduction
Nowadays the General Relativity is a modern theory of gravity. It is described by curved
4-dimential pseudo-Riemannian space-time. Usually in the framework of this theory the
main objects are the symmetric metric gµν and the connection Γξ
µν, which also symmetric
and depends on the metric. The equivalent approach is the so-called Palatini formalism
in which the metric and the connection are considered as independent variables, but both
are still symmetric.
In this work we consider a generalization of this theory. The connection is considered
as nonsymmetric and independent of the metric object. The metric is symmetric as usual.
In these assumptions connection Γα
ρν is not equal to the Christoﬀel symbol. It leads to
the fact that such theory is more extensive. For example, the contraction Rααµν is not
equal to zero and the Ricci curvature tensor Rβν ≡Rαβαν is not symmetric anymore.
Such approach with the Einstein-Hilbert action for the ﬁrst time was proposed only
in 1978 in the paper [1], which was published only in Russian and remained practically
unknown to the scientiﬁc community. The authors noticed that this theory can be inter-
preted as uniﬁed theory of gravity and electromagnetism, however they did not introduce
an action for the matter. Instead the authors have to used some ad hoc physical assump-
tions to obtain correct equations of motions of test particles. In the same year a very
similar theory was considered in the paper [2]. However the purpose of the authors was
diﬀerent: they did not try to connect their theory with electromagnetism. Nowadays the
studies of Palatini formalism with nonsymmetric connection have been continuing, see.
e.g. [3].
In the present paper we generalize the approach proposed in [1] by including a matter
in the form of point particles into the action. We obtain a correct form of the action term
for the interaction of such a matter with the connection and discover that it is necessary
to identify the electromagnetic potential with the trace of the connection rather with the
trace of the torsion (as it was done in [1]).
2
Theory without matter
To begin with, let us consider the Einstein-Hilbert action without matter in a standard
form:
S1 = −1
2κ
Z
d4x√−ggµνRµν(Γ),
(1)
where Rβν = Rαβαν = ∂αΓα
νβ −∂νΓα
αβ +Γα
αξΓξ
νβ −Γα
νξΓξ
αβ is the Ricci tensor which depends
only on connection.
To obtain equations of motion it is necessary to vary the action. It is easy task to vary
with respect to the metric gµν because now action does not depend on the derivative of
metric. Thereby one can get
Rνµ + Rµν −Rgµν = 0.
(2)
These equations diﬀer from Einstein equations without matter because here Rµν is not a
symmetric tensor, so it contains an additional symmetrization.
Variation with respect to the connection gives more interesting result:
Dρgσν = 1
3gσνSα
ρα + 1
3gσξSα
ξαδν
ρ + gξσSν
ρξ,
(3)
2
### Page 3

where Sρ
µν = Γρ
µν −Γρ
νµ is a torsion. This equation is solved by
Γρ
µν = ¯Γρ
µν + 1
4Aµδρ
ν,
(4)
where ¯Γρ
µν = 1
2gασ(∂ρgσν +∂νgρσ −∂σgνρ) is the Christoﬀel symbols and Aµ is an arbitrary
vector. This formula can be rewritten in a form:
Γρ
µν −1
4Γα
µαδρ
ν = ¯Γρ
µν −1
4
¯Γα
µαδρ
ν,
(5)
by substitution trace of relation (4). Now it is clear that the trace of the connection has
not any restrictions. In this sense, this theory has additional gauge symmetry.
Taking (4) into account the explicit form of the curvature tensor is
Rµνλρ = ¯Rµνλρ + 1
4(∂λAρ −∂ρAλ)δµ
ν ,
(6)
where ¯Rµνλρ is the usual Riemann curvature tensor which depends on the Christoﬀel
symbols ¯Γρ
µν and thus can be expressed through metric. Taking trace of (6) one can ﬁnd
that
Rµµλρ = ∂λAρ −∂ρAλ
(7)
and
Rµλµρ ≡Rλρ = ¯Rλρ + 1
4(∂λAρ −∂ρAλ),
(8)
where ¯Rλρ is a Riemannian and therefore symmetric Ricci tensor. The scalar curvature:
R ≡Rλρgλρ = ¯Rλρgλρ
(9)
does not change. Thereby the equation (2) can be rewritten as:
¯Rνµ −1
2Rgµν = 0.
(10)
So it is exactly the vacuum Einstein’s equations.
3
Addition of matter
The next step is an addition of a matter in the theory. We will consider it in the form of
a set of relativistic point particles. For the sake of simplicity we will write the formulas
for a single particle. This particle with a world line xµ(τ) in the gravitational ﬁeld with
the metric gµν is described by standard action:
S2 = −m
Z
dτ
q
˙xµ(τ) ˙xν(τ)gµν(x(τ)),
(11)
where m is a mass of particle.
In order to get a more general theory the interaction of classical particles with the
connection is introduced. One of the most simplest way is
S3 = −q
Z
dτ ˙xµ(τ)Γν
µν(x(τ)),
(12)
3
### Page 4

where q is just a parameter1.
Thus the theory consists of three terms S1 +S2 +S3. But it turns out that such theory
is self-inconsistent. Indeed, after a variation with respect to the connection the following
equations of motion arise:
˙xµ(τ) = 0
(13)
which are incompatible with the normalization of four-velocity. This result is connected
with the presence of gauge invariance in S1 (see after (5)). To avoid this problem one
can add one more term to the total action. It is the kinetic term which can be written in
diﬀerent ways, but again the most simple case is chosen:
S4 = −1
16π
Z
d4x√−gRµµαβRµµδγgαδgβγ,
(14)
where the constant
1
16π is chosen for convenience. It is worth noting that the same term
was proposed in [1], but without above motivation since the action of matter was not
considered in their work.
As a result the total action consists of four terms:
S = S1 + S2 + S3 + S4 = −1
2κ
Z
d4x√−gR −m
Z
dτ
q
˙xµ(τ) ˙xν(τ)gµν(x(τ))−
−q
Z
dτ ˙xµ(τ)Γν
µν(x(τ)) −
1
16π
Z
d4x√−gRµµαβRµµδγgαδgβγ.
(15)
This is the ﬁnal view of the action. It depends on three independent variables: the metric
gµν, the connection Γα
βγ and the coordinate of the particle xµ(τ).
Let us obtain the complete set of ﬁeld equations by varying with respect to these
variables. Firstly, let us consider the variation with respect to the metric. Only terms S1,
S2 and S4 depend on gµν. The contribution of S1 is already found in (10). The variation
of S2 and S4 can be easily calculated. Finally equations of motion corresponding to the
variation of the metric are:
¯Rµν −1
2Rgµν = κ(T µν
1
+ T µν
2 ),
(16)
where
T µν
1
= ρmuµuν
(17)
is a stress-energy tensor of a relativistic particle,
T µν
2
= −1
4π (RξξµαRββνα −1
4gµνRξξαβRϕϕαβ),
(18)
uµ = ˙xµ
1
√
˙xα ˙xβgαβ is a four-velocity and ρm = m
R
dsδ(x −x(s))
1
√
−g(x(s)) is a mass
density.
The expression for T µν
2
can be rewritten in a more recognizable form using
notation Rϕϕαβ ≡Fαβ:
T µν
2
= −1
4π(F µαF να −1
4gµνF αβFαβ).
(19)
In this form T2 reproduces the stress-energy tensor of electromagnetic ﬁeld with electro-
magnetic tensor Fαβ.
1Another simple combination is the contraction of ˙xµ with the trace of torsion Sν
µν instead of the trace of
connection Γν
µν. We will discuss it in the section 4.
4
### Page 5

Next the connection Γα
µν is varied. The term S2 does not depend on the connection.
The result for S1 is already found in (3). After calculations for S3 and S4 the following
equation is obtained:
Γρ
µν = ¯Γρ
µν + 1
4Aµδρ
ν,
(20)
¯DµF µν = 4πjν,
(21)
where ¯Dµ is a covariant derivative with the Riemannian connection and jν = q
R
dsuνδ(x−
x(s))
1
p
−g(x(s))
is a four-current of relativistic particles if q is considered as an electric
charge. The equation (21) is nothing but the Maxwell’s equation. According to (20) and
its consequence (7) the role of electromagnetic potential corresponding to F µν is played
by the quantity Aρ.
Finally, the variation with respect to the particle coordinate is calculated. It is neces-
sary to vary only S2 and S3. The result is already known since S2 has a standard view
and S3 can be treated as interaction term for a particle with electromagnetic potential
Γα
βα. So the corresponding equation of motion is
muµ ¯Dµuα = −quξF ξα.
(22)
Thus this equation reproduces the equations of motion of relativistic particle in the grav-
itational ﬁeld with metric gµν and the electromagnetic ﬁeld again deﬁned by the quantity
Aρ in (7) as a potential.
As a result we conclude that the system of ﬁeld equations (16), (20), (21), (22) corre-
sponding to action (15) reproduce Einstein-Maxwell equations.
4
Discussion
Thereby only geometric objects were introduced such as the metric gµν and the connec-
tion Γα
µν. The standard Einstein-Hilbert action was complemented by additional terms,
which corresponding to a relativistic point-like particle (11), an interaction (12) and a
kinetic term (14). The additional degrees of freedom of the connection Aµ were treated
as an electromagnetic potential. As a result, the electrodynamics in gravitational ﬁeld is
constructed. Despite the simplicity of the above theory, is had not been discovered at the
times of the most intense search of uniﬁed ﬁeld theory (for the detailed historical survey
see [4] and the references therein).
As we said above, for the ﬁrst time a similar approach was proposed in 1978 [1].
However, they treated the trace of the torsion as the electromagnetic potential. If we
restrict ourselves to consideration of the matter-free action consisting only of S1 and S4,
the diﬀerence between identiﬁcation of electromagnetic potential with the trace of the
torsion and with the trace of connection (as in our approach) turns out to be negligible.
However, the addition of matter changes the picture drastically. While the matter can
be coupled with the trace of connection without any troubles, coupling with the trace of
torsion
S′
3 = −q
Z
dτ ˙xµ(τ)Sν
µν(x(τ))
(23)
leads to the appearance of matter in the expression for the connection. Instead of (20)
we have
Γρ
µν = ¯Γρ
µν + 1
3Aµδρ
ν + κ
4
 3jρgµν −jµδρ
ν −jνδρ
µ

.
(24)
5
### Page 6

Note that the authors of [1] did not consider the variational principle for the matter.
Instead they used some additional physical assumptions in order to obtain the equations
of motion of test particles which are identical to (22). It is worth noting that the paper [1]
was published in the obscure Soviet journal which is almost completely unavailable to
the scientiﬁc community, so the result remained unknown. The theory proposed in [1]
was later rediscovered many times, e.g. in [2], where the authors did not consider the
interpretation of the Aµ as an electromagnetic potential, and in [5], where it served as the
base for the possible extension of GR.
In the present work the role of matter is played by point particles. The generalization
on the case of ideal ﬂuid (i. e. continuous medium consisting on classical particles) is
quite simple. The corresponding interaction term was proposed in [4] for a variant of
description of ideal ﬂuid which was studied in [6]. However, the interpretation of the
Aµ as an electromagnetic potential is possible only for the purely classical description of
matter. The generalization such theory for the more physical interesting case, where a
matter is considered as a ﬁeld, is a one way of the further development. For this purpose
one could consider the approach of frame bundles. Such attempts, for example, was made
by Horie [7].
Acknowledgements. The work was supported by SPbGU grant N 11.38.223.2015.
References
[1] Yu. N. Obukhov, V. G. Krechet, V. N. Ponomarev, Gravitaciya i teoriya otnositelnosti
[Gravitation and theory of relativity, in Russian], 14-15 (1978), 121–127.
[2] F. W. Hehl, G. D. Kerlick, General Relativity and Gravitation, 9: 8 (1978), 691–710.
[3] A. N. Bernal, B. Janssen, A. Jimenez-Cano, J. A. Orejuela, M. Sanchez, P. Sanchez-
Moreno, Physics Letters B, 768 (2017), 280–287, arXiv:1606.08756.
[4] N. V. Kharuk, A. A. Sheykin, S. A. Paston, “Classical electromagnetic potential as a
part of gravitational connection: ideas and history”, 2017, arXiv:1709.02284.
[5] R. W. Tucker, C. Wang, Classical and Quantum Gravity, 12:
10 (1995), 2587,
arXiv:gr-qc/9509011.
[6] S. A. Paston, Phys.Rev.D, 96 (2017), 084059, arXiv:1708.03944.
[7] K. Horie, “Geometric Interpretation of Electromagnetism in a Gravitational Theory
with Torsion and Spinorial Matter”, 1996, arXiv:hep-th/9601066.
6