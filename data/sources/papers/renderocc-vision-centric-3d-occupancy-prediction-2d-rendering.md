# RenderOcc Vision-centric 3D Occupancy Prediction 2D Rendering

**Source**: arxiv PDF, 28 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

LA-UR-23-24761
QCD resummation of dijet azimuthal decorrelations in
pp and pA collisions
Mei-Sen Gaoa , Zhong-Bo Kangb,c,d , Ding Yu Shaoa,e,f , John Terryg and Cheng
Zhanga
aDepartment of Physics and Center for Field Theory and Particle Physics, Fudan University,
Shanghai, China
bDepartment of Physics and Astronomy, University of California, Los Angeles, CA 90095, USA
cMani L. Bhaumik Institute for Theoretical Physics, University of California, Los Angeles, CA
90095, USA
dCenter for Frontiers in Nuclear Science, Stony Brook University, Stony Brook, NY 11794, USA
eKey Laboratory of Nuclear Physics and Ion-beam Application (MOE), Fudan University, Shang-
hai, China
fShanghai Research Center for Theoretical Nuclear Physics, NSFC and Fudan University, Shanghai
200438, China
gTheoretical Division, Los Alamos National Laboratory, Los Alamos, NM 87545, USA
E-mail:
msgao@fudan.edu.cn,zkang@ucla.edu,dingyu.shao@cern.ch,jdterry@lanl.gov,
chengzhang phy@fudan.edu.cn
Abstract: We study the azimuthal angular decorrelations of dijet production in both
proton-proton (pp) and proton-nucleus (pA) collisions. By utilizing soft-collinear effective
theory, we establish the factorization and resummation formalism at the next-to-leading
logarithmic accuracy for the azimuthal angular decorrelations in the back-to-back limit in
pp collisions. We propose an approach where the nuclear modifications to dijet production
in pA collisions are accounted for in the nuclear modified transverse momentum dependent
parton distribution functions (nTMDPDFs), which contain both collinear and transverse
dynamics. This approach naturally generalizes the well-established formalism related to
the nuclear modified collinear parton distribution functions (nPDFs).
We demonstrate
strong consistency between our methodology and the CMS measurements in both pp and
pA collisions, and make predictions for dijet production in the forward rapidity region in pA
collisions at LHC kinematics and for mid-rapidity kinematics at sPHENIX. Throughout
this paper, we focus on the application of this formalism to a simultaneous fit to both
collinear and transverse momentum dependent contributions to the transverse momentum
dependent distributions.
arXiv:2306.09317v2  [hep-ph]  19 Oct 2023
### Page 2

Contents
1
Introduction
1
2
Factorization and resummation formula
4
2.1
Factorization in SCET for pp collisions
4
2.2
RG evolution and resummation formula
8
2.3
Nuclear modified formalism for pA collisions
11
3
Numerical parameterization and results
12
3.1
Parameterization
12
3.2
Numerical results
13
4
Summary
19
A Anomalous dimension
20
1
Introduction
The investigation of high-energy proton-proton (pp) and proton-nucleus (pA) collisions is
a crucial area of study in particle and nuclear physics, as it provides valuable insight into
the fundamental structure of matter and the strong interaction among its constituents [1–
4]. Jet production is a crucial observable in these collisions, where collimated sprays of
particles produced by the strong force, described by quantum chromodynamics (QCD), are
observed. One of the key features of jet production in proton-proton and proton-nucleus
collisions is the azimuthal angular distribution, or the difference in the azimuthal angle
between the two jets. In the perturbative region, this decorrelation is a result of emissions
from both the initial and final states that can alter the direction of the jets. The study of
azimuthal decorrelation is critical for a deeper understanding of QCD jets and for testing
QCD predictions and searching for new physics.
When one studies the dijet pseudorapidity spectrum while integrating over the full
range of the azimuthal angle, the observable can be studied within the usual collinear
factorization [5] and such a pseudorapidity spectrum is directly sensitive to the collinear
parton distribution functions (PDFs), allowing us to constrain longitudinal motion of par-
tons inside a free nucleon [6–8]. When going from pp to pA collisions, there have been
two approaches to deal with the nuclear modification [1], especially at the kinematic region
where one probes the small-x parton physics. One is a DGLAP-based approach, while
the other one is the saturation-based or color glass condensate (CGC) approach. In the
DGLAP-based approach, one replaces the usual proton PDFs with the nuclear modified
PDFs (nPDFs) [9–14] and follows the exact same collinear factorization. In this approach,
– 1 –
### Page 3

the nuclear modification is included in the parameterization of the initial conditions for the
DGLAP evolution of the nPDFs. On the other hand, in the saturation/CGC approach,
gluon mergers and interactions dynamically lead to the nonlinear BK-JIMWLK evolu-
tion equations [15–21]. For the theoretical formalism of the dijet production in the CGC
framework, see for example Refs. [22, 23]. See also other work [24–28] along this direction.
Alternatively, when one studies more differential dijet observables, e.g. dijet azimuthal
decorrelation, the conventional pQCD collinear factorization could be impaired. In the
nearly back-to-back region where δϕ = π −∆ϕ →0, the perturbative expansion of the
azimuthal angle decorrelation diverges due to logarithmic singularities at δϕ →0 [29, 30].
The pioneering work in this field has highlighted the necessity of all-order resummation
for accurately describing hadronic radiation, leading to a TMD-like factorization as shown
below.
This conclusion has been supported by numerous studies that have performed
all-order resummation for various processes [31–54]. In Fig. 1 we depict this back-to-back
configuration for a narrow jet radius (R ≪1), where R is the radius of the jet. Fortunately,
the azimuthal decorrelation of QCD jets in the nearly back-to-back region is sensitive to
the intrinsic motion of the bound partons, allowing us to perform three-dimensional (3D)
quantum imaging of the proton at high-energy facilities such as the Relativistic Heavy Ion
Collider (RHIC) and the Large Hadron Collider (LHC). This three dimensional structure
is encoded in the transverse momentum dependent parton distribution functions (TMD-
PDFs), which contain both collinear and transverse momentum degrees of freedom.
While studying the nuclear modification to the inclusive dijet pseudorapidity spectrum
in pA collisions, in the DGLAP-based approach, one encodes nuclear modification inside
the nPDFs within the collinear factorization formalism. The natural question is how one
handles the nuclear modification of the dijet production in the nearly back-to-back region
when going from pp to pA collisions. As a natural generalization, we could encode nuclear
modification of back-to-back dijet production inside nuclear modified TMDPDFs (nTMD-
PDFs) within the TMD-like factorization formalism. Following such an approach, a recent
global extraction of nuclear-modified TMDPDFs has successfully described world data for
semi-inclusive electron-nucleus deep inelastic scattering and Drell-Yan processes in proton-
nucleus collisions in Ref. [55]. Furthermore, an independent cross check of this analysis was
performed in Ref. [56], verifying the results of Ref. [55]. However, the applicability of nT-
MDPDFs to other processes, such as dijet production, is yet to be determined. Finally, the
study of QCD jet production in forward rapidity regions where one probes small-x parton
dynamics is crucial for investigating the phenomenon of gluon saturation or CGC. Just like
nPDF vs CGC approaches, to confirm saturation effects, it is important to have a proper
understanding of the impact of nTMDPDFs vs CGC approaches in the back-to-back dijet
production. For recent studies that deal with the back-to-back dijet production within the
CGC formalism, see for example Refs. [57–59].
Experimental measurements of the azimuthal angular decorrelations in proton-proton
and proton-lead (pPb) collisions at the LHC were performed in [60, 61], respectively; while
in [61, 62] the integrated dijet azimuthal angle decorrelation in the region ∆ϕ > 2π/3
was measured. The first phenomenological studies of these data have been used to further
constrain the nuclear modified collinear PDFs, see for instance in [12, 63, 64], by ap-
– 2 –
### Page 4

j2
y
x
j1
δϕ
Figure 1. Definition of the azimuthal angular δϕ of dijet pair production in the x-y plane, where
the transverse momentum of the leading jet j1 is chosen to be aligned with the −y direction for
convenience.
proximating the integrated azimuthal angular decorrelations with the dijet pseudorapidity
spectrum within a next-to-leading order (NLO) collinear factorization formalism. How-
ever, in the back-to-back region, which is encapsulated by ∆ϕ > 2π/3, the TMD effects,
such as non-perturbative corrections and resummation can also be explored. Due to the
sensitivity of these data to both collinear and transverse momentum contributions, these
data can serve as a window into a simultaneous extraction of both collinear and transverse
momentum effects in bound nucleons inside the heavy nucleus, which has so far not been
performed.
In this study, we investigate the azimuthal angular decorrelation of dijet production
in proton-proton collisions using the soft-collinear effective theory (SCET) framework [65–
69]. The utilization of the SCET framework enables us to perform QCD resummation
of the large logarithmic terms in the azimuthal angle and jet radius at next-to-leading
logarithmic (NLL) accuracy. Additionally, we examine the effects of nuclear modification on
the azimuthal angular distribution in proton-nucleus collisions through the incorporation of
nTMDPDFs and comment on the implications of our formalism to measuring nTMDPDFs
as well as understanding nuclear modification of both collinear and transverse motions of
the partons inside the nucleus.
Two predominant approaches are typically utilized for calculating the resummation
formula in azimuthal decorrelation, known as the indirect [32] and the direct [29] methods.
The indirect strategy focuses on the extraction of an all-order factorization and resum-
mation formula for the two-dimensional transverse momentum imbalance qT of dijet pairs
and the subsequent development of the azimuthal decorrelation ∆ϕ distribution originat-
ing from the qT distribution. In contrast, the direct method underpins the derivation of
a factorization formula for the azimuthal angular distribution in the back-to-back limit,
followed by the direct computation of all-order resummation results. While the association
between these two methods is explicit for Drell-Yan-like procedures, it becomes increasingly
intricate for processes implicating jet production, necessitating the resummation of sizable
– 3 –
### Page 5

logarithms from final-state QCD radiation. Historically, it has been demonstrated that the
indirect method could induce divergences in the azimuthal integral for a narrow jet radius
[37, 38]. To mitigate these issues, various regularization schemes have been recommended
[37, 38, 46]. In this study, to evade such complexities, we have opted for the application of
the direct method.
The rest of this paper is organized as follows. In section 2 we first discuss the factoriza-
tion and resummation formula for nearly back-to-back dijet production in proton-proton
collisions. Then we present the nuclear modified resummation formula in proton-nucleus
collisions. In sub-section 3.1, we provide information for the numerical parameterization
of the non-perturbative physics as well as the non-global logarithms (NGLs). We present
the numerical results using the theoretical formula, enumerate all theoretical uncertainties
and compare our predictions with the LHC experimental data in sub-section 3.2. We also
make predictions for the azimuthal decorrelation of dijet production at the LHC, as well
as for the sPHENIX kinematics region at the RHIC. We summarize our paper in section
4. The details of anomalous dimensions are provided in the appendix.
2
Factorization and resummation formula
In this section, we present our factorization and resummation formalism for the azimuthal
decorrelation of dijet production in pp and pA collisions in the back-to-back limit.
2.1
Factorization in SCET for pp collisions
In the back-to-back limit and with the narrow jet approximation, the QCD modes which
contribute to the dijet cross section are given by
hard : pµ
h ∼pT (1, 1, 1),
(2.1)
na,b-collinear : pµ
ci ∼pT (δϕ2, 1, δϕ)ni¯ni,
(2.2)
soft : pµ
s ∼pT (δϕ, δϕ, δϕ),
(2.3)
nc,d-collinear : pµ
ci ∼pT (R2, 1, R)ni¯ni,
(2.4)
nc,d-collinear-soft : pµ
csi ∼pT δϕ
R
(R2, 1, R)ni¯ni,
(2.5)
where the momentum pµ is expressed in light-cone coordinates as pµ ≡(ni·p, ¯ni·p, pni⊥)ni¯ni,
and nµ
i are light-like vectors associated with the initial-state proton beams (na,b) or final-
state jets (nc,d). The na,b-collinear, nc,d-collinear-soft and soft modes all have the same
invariant mass and will result in rapidity divergences in the factorization formula. We ad-
dress these divergences using the standard Collins-Soper-Sterman (CSS) treatment [70, 71]
and collinear anomaly [72, 73] method, as explained in the next subsection. The contri-
bution from the Glauber modes, which would result in the breaking of TMD factorization
[74–77], is neglected in this study. The magnitude of factorization breaking effects from
the Glauber mode can be explored by comparing theoretical predictions with future high-
precision experimental data.
– 4 –
### Page 6

Based on the assumption of the above kinematic modes, we follow the standard steps
in SCET [78–80] to obtain the following factorization formula 1
d4σpp
dyc dyd dp2
T dqx
=
X
abcd
xaxb
16πˆs2
1
1 + δcd
Cx
h
funsub
a/p
funsub
b/p
Sunsub
ab→cd,IJ Scs
c Scs
d
i
(2.6)
× Hab→cd,JI(ˆs, ˆt, µ) Jc(pT R, µ) Jd(pT R, µ) ,
where we have taken the short-hand
Cx
h
funsub
a/p
funsub
b/p
Sunsub
ab→cd,IJ Scs
c Scs
d
i
=
Z
dkax dkbx dkcx dkdx dλx Sunsub
ab→cd,IJ(λx, µ, ν)
× funsub
a/p
(xa, kax, µ, ζa/ν2) funsub
b/p
(xb, kbx, µ, ζb/ν2) Scs
c (kcx, R, µ, ν) Scs
d (kdx, R, µ, ν)
× δ (qx −kax −kbx −kcx −kdx −λx) .
(2.7)
The cross section is differential with respect to: the x component of the transverse momen-
tum imbalance of the jet pair (|qx| = pT δϕ), the outgoing rapidities of jets c and d (yc,d), the
jet transverse momentum (pT ). In this expression, a, b, c, d represent parton flavors which
are summed over in the cross section. The Kronecker delta symbol δcd in the prefactor on
the right side of this expression arises from the symmetry factor due to identical partons in
the final state. Additionally, in this expression we introduced the partonic center-of-mass
energy reads ˆs = xaxbs, and ˆt = −xapT
√se−yc, where s is the hadronic CM energy and
xa and xb represent the Bjorken variables which are defined in terms of our phase space
variables through the relations
xa = pT
2Ep
(eyc + eyd) ,
xb = pT
2Ep
 e−yc + e−yd
,
(2.8)
where Ep is the energy of the incoming protons in the lab frame. The functions funsub
a,b/p
represent the one-dimensional unsubtracted TMDPDFs for the incoming parton of flavor
a, b [81]. For these distributions, µ and ν are standard renormalization scale and rapidity
scales, while ζa,b represent the Collins-Soper parameters [82, 83].
The function Hab→cd and Sab→cd are the hard and soft functions. In our formalism, we
follow the work of [84, 85] to organize the hard and soft functions into matrices, denoted by
the bold characters. In this formalism, the IR divergent, UV finite scattering amplitudes
for the 2 →2 process can be written as vectors in color space
Mab→cd
 ˆs, ˆt, ˆu, µ, ϵ

=
X
I
1
⟨CICI⟩MI
ab→cd
 ˆs, ˆt, ˆu, µ, ϵ

|CI⟩,
(2.9)
where |CI⟩denote basis vectors in the color space while I is an index that runs over the
dimensionality of the color space, which is determined purely through the species and the
number of the external particles in the hard partonic process. The prefactors of the color
basis vectors contain the kinematic contributions and the IR divergences of the amplitudes.
1A comprehensive description of the TMD factorization formula in the context of SCET for jet production
can be found in the literature, for instance, in Refs. [38, 43, 48].
– 5 –
### Page 7

Following the work of [85], the basis vectors are absorbed into the soft sector. We now
note that the integration of the virtual partons in the amplitudes of Eq. (2.9) contain
interactions at the hard scale as well as interactions at scales associated with the IR modes
in Eqs. (2.2), (2.3), (2.4), and (2.5). To define a purely hard scattering amplitude, one needs
to subtract off the virtual loop contributions from these IR modes. As the virtual loop
integrals of the IR modes are scaleless, this subtraction scheme swaps the IR divergences
in the scattering amplitudes of Eq. (2.9) to UV ones. Thus we can define the purely hard
scattering amplitudes through the subtraction
MH
ab→cd
 ˆs, ˆt, ˆu, µ, ϵ

=
Mab→cd
 ˆs, ˆt, ˆu, µ, ϵ

−
X
i
Mi
ab→cd
 ˆs, ˆt, ˆu, µ, ϵ

,
(2.10)
where i runs over the IR modes in (2.2), (2.3), (2.4) and (2.5). The divergences entering into
the hard scattering amplitude are now UV and can therefore be handled in a multiplicative
renormalization procedure. Thus we can define UV subtracted amplitudes as
MH sub
ab→cd
 ˆs, ˆt, ˆu, µ
E
= ZH
 ˆs, ˆt, ˆu, µ, ϵ
 MH
ab→cd
 ˆs, ˆt, ˆu, µ, ϵ

,
(2.11)
where ZH is the hard multiplicative renormalization factor and is a matrix in color space.
From this expression, the evolution of the subtracted scattering amplitudes is given by the
expression
∂
∂ln µ
MH sub
ab→cd
 ˆs, ˆt, ˆu, µ
E
= ΓH
 ˆs, ˆt, ˆu, µ
 MH sub
ab→cd
 ˆs, ˆt, ˆu, µ
E
(2.12)
where the hard anomalous dimension is defined as
ΓH
 ˆs, ˆt, ˆu, µ

=

∂
∂ln µZH
 ˆs, ˆt, ˆu, µ

Z−1
H
 ˆs, ˆt, ˆu, µ

.
(2.13)
In the following section, we will provide the hard anomalous dimension matrix, while we
will further summarize the formalism in this section.
In SCET, the soft contributions enter as vacuum matrix elements. In our formalism,
we define a b-space unsubtracted global soft function as
˜Sunsub
ab→cd(λx, µ, ν) =
Z db
2πeiλxb
0
 ¯T

O†
nanbncnd(bµ)

T

Onanbncnd(0)
0

,
(2.14)
with Onanbncnd(bµ) = [SnaS†
nbS†
ncSnd](xµ). In this expression, bµ = (0, b, 0, 0), nµ
i are the
light-like vectors defined below Eq. (2.5), and T (¯T) represents (anti-) time ordering. The
soft Wilson line is given by
Sni(x) = P exp

igs
Z 0
−∞
dt ni · As(x + tni)

,
(2.15)
where P denotes path ordering. We stress that, since we derive the factorization formal-
ism in the direct method, the transverse vector bµ points along the x-direction, which is
perpendicular to all vectors na,b,c,d. This differs from the TMD soft function which was de-
rived in [42], where the TMD factorization was derived for the two-dimensional transverse
– 6 –
### Page 8

momentum imbalance of dijet pairs. As a result, the operator definition of the TMD soft
function in this paper is different from that in [42]. The soft function in Eq. (2.14) also
enters into the factorization in the transverse energy-energy correlator event shape in [86].
To define the color matrix, we follow the work of Ref. [87] to absorb the color vectors into
the soft function as
˜Sunsub
ab→cd,IJ(λx, µ, ν) =
D
CI
 ˜Sunsub
ab→cd(λx, µ, ν)
 CJ
E
,
(2.16)
where the SU(3) generators in the Wilson lines beyond tree level modify the color structure
of the soft color matrices.
Aside from these complications associated with the hard and soft color matrices, to
describe this observable, we must account for two final-state radiative effects. Firstly, in
the narrow jet approximation (R ≪1), radiative corrections of the final-state partons are
encoded in the jet and collinear-soft functions, Ji and ˜Scs
i . The one loop exclusive jet func-
tion is well-known, see for instance [88], while the one-loop calculation of the collinear-soft
function can be found in the appendix of [53]. In addition to the standard ϵ divergences
in dimensional regularization, the collinear-soft function that enters into our factorization
also contains rapidity poles. We stress that these rapidity poles enter into the direct com-
putation of the azimuthal angle decorrelation. However these poles do not enter into the
collinear-soft function for the two dimension dijet transverse momentum imbalance in [42].
Secondly, as the observable is insensitive to radiative emissions within the jet, this observ-
able is non-global and is thus sensitive to NGLs [89]. Such NGLs modify the factorization
structure of the jet and collinear-soft function at two loops. The full factorization formula
can be obtained by introducing the multi-Wilson structure in SCET [90, 91]. For simplicity,
we do not write down the full formula in this paper, and in the resummation calculation,
we use the fitting function [89, 92] to include their contribution at the NLL accuracy.
After taking these effects into account, we note that the convolution in the cross section,
Cx, can be simplified by working in b-space, the conjugate space to qx. After performing
the Fourier transform, the convolutional integral can be written as
Cx
h
funsub
a/p
funsub
b/p
Sunsub
ab→cd,IJ Scs
c Scs
d
i
=
Z db
2πeibpT δϕ ˜Sunsub
ab→cd,IJ(b, µ, ν)
× ˜funsub
a/p
(xa, b, µ, ζa/ν2) ˜funsub
b/p
(xb, b, µ, ζb/ν2) ˜Scs
c (b, R, µ, ν) ˜Scs
d (b, R, µ, ν) ,
(2.17)
where the b-space functions are defined as
˜funsub
a/p
(xa, b, µ, ζa/ν2) =
Z
dkax e−ikaxb ˜funsub
a/p
(xa, kax, µ, ζa/ν2) ,
(2.18)
˜Sunsub
ab→cd,IJ(b, µ, ν) =
Z
dλx e−iλxb ˜Sunsub
ab→cd,IJ(λx, µ, ν) ,
(2.19)
˜Scs
c (b, R, µ, ν) =
Z
dkcx e−ikcxb ˜Scs
c (kcx, R, µ, ν) .
(2.20)
– 7 –
### Page 9

After taking into consideration the simplification when working in b-space, the expression
for the factorized cross section is given by the expression
d4σpp
dyc dyd dp2
T dqx
=
X
abcd
xaxb
16πˆs2
1
1 + δcd
Hab→cd,JI(ˆs, ˆt, µ) Jc(pT R, µ) Jd(pT R, µ)
(2.21)
×
Z db
2πeibpT δϕ ˜Sunsub
ab→cd,IJ(b, µ, ν) ˜Scs
c (b, R, µ, ν) ˜Scs
d (b, R, µ, ν)
× ˜funsub
a/p
(xa, b, µ, ζa/ν2) ˜funsub
b/p
(xb, b, µ, ζb/ν2) .
In the following sections, we will summarize the expressions for the evolution and resum-
mation of each contribution in this cross section.
2.2
RG evolution and resummation formula
In the above subsection, we have obtained a factorization formula for azimuthal angular
distribution in the joint back-to-back and small jet radius region. To achieve the resum-
mation formula, one solves the RG equations for each of the ingredients in (2.21).
In
this section, we begin by performing resummation for pp scattering and then discuss our
treatment for the pA scattering.
The hard functions for all 2 →2 processes in massless QCD are given up to next-to-
next-to-leading order (NNLO) in Ref. [93]. To ensure consistency in the expressions for
the hard anomalous dimensions between this study and our work, we choose to use the
same color basis as this reference. Using these bases, the hard function satisfies the RG
equation as
d
d ln µH = ΓHH + H Γ†
H
(2.22)
where the anomalous dimension takes the form
ΓHab→cd =
CH
2 γcusp(αs)

ln ˆs
µ2 −iπ

+ γH(αs)

1 + γcusp(αs)Mab→cd,
(2.23)
with CH = nqCF + ngCA and γH = nqγq + ngγg. Here nq and ng indicate the number of
quark and gluon, respectively. The matrix M reads
Mab→cd = (ln r + iπ) M1,ab→cd + ln
r
1 −rM2,ab→cd,
where the dimensionless parameter r is defined as r = −ˆt/ˆs. The expressions for M1,2 can
be found in Ref. [93]. In this work, we consider QCD resummation at NLL accuracy, thus,
we include the double logarithms anomalous dimension up to two-loop order and the single
logarithms anomalous dimension up to one-loop order. The coefficients of all anomalous
dimensions used in our calculation are given in the appendix A and we remark that the
anomalous dimensions for quadrupole color and kinematic entanglement have been ignored
in (2.23), since they contribute at three-loop order and beyond [94, 95]. Lastly, we remark
that information associated with solving the RG equations in color space is provided in
[85].
– 8 –
### Page 10

The jet functions in Eq. (2.21) fulfill the RG equation
d
d ln µJi (pT R, µ) = ΓJi(αs)Ji (pT R, µ) ,
(2.24)
where the anomalous dimension of the jet is given by
ΓJi(αs) = −Ciγcusp(αs) ln p2
T R2
µ2
+ γJi(αs) .
(2.25)
In this expression, Ci = CF or CA is the Casimir of the parton i.
It is worth noting
that our analysis here does not account for the non-global structures in the factorization
formula (2.21). As shown in [38], to obtain a complete description, the contribution of
non-global structures must also be incorporated. In our current study, we do not take
into consideration these structures in the factorization formula.
However, the leading
logarithmic (LL) NGLs are resummed by a fitting function, which is explained later in the
paper.
In addition to the hard and jet function, all other terms in (2.21) also depend on the
rapidity scale ν. For the TMDPDFs, we resum the large logarithms using the Collins-
Soper equation.
Specifically, in the Collins-11 treatment [82, 83], the properly-defined
TMDPDFs are obtained by absorbing the standard TMD soft function in the Dell-Yan
process, ˜Sab(b, µ, ν), and we have
˜funsub
a/p
 xa, b, µ, ζa/ν2 ˜funsub
b/p
 xb, b, µ, ζb/ν2 ˜Sab(b, µ, ν)
(2.26)
≡˜fa/p (xa, b, µ, ζa) ˜fb/p (xb, b, µ, ζb) ,
where the rapidity divergences cancel and no explicit ν-dependence in the arguments any-
more. For each TMDPDF, the CSS evolution equation for the ζ-dependence is given by
p
ζa
d
d√ζa
˜fa/p(xa, b, µ, ζa) = ˜κa(b, µ) ˜fa/p(xa, b, µ, ζa),
(2.27)
where ˜κa(b, µ) represents the Collins-Soper kernel.
In the perturbative region, one has
˜κa(b, µ) = −Caγcusp(αs) ln µ2/µ2
b + O(α2
s) with µb = 2e−γE/b. The solution reads
˜fa/p(xa, b, µ, ζa,f) = ˜fa/p(xa, b, µ, ζa,i)
 s
ζa,f
ζa,i
!˜κa(b, µ)
,
(2.28)
where we choose the standard Collins-Soper parameter as ζa,i = ζb,i = µ2
b and ζa,f = ζb,f =
ˆs. In addition, the RG equation of TMDPDFs reads
d
d ln µ
˜fa/p(xa, b, µ, ζa,f) =

Caγcusp(αs) ln µ2
ζa,f
−2γa(αs)

˜fa/p(xa, b, µ, ζa,f) ,
(2.29)
where Ca denote the color of the incoming parton. In comparison to the two-dimensional
transverse momentum resummation formula [42], the presence of rapidity divergence in the
collinear-soft functions represents a new property. This divergence arises from the small
– 9 –
### Page 11

jet approximation [53] and requires resummation of the corresponding rapidity logarithms.
Two commonly used approaches to achieve this resummation are the rapidity RG [96, 97]
and collinear anomaly [72, 73] framework. In this study, we choose to use the collinear
anomaly framework.
In our study, we re-factorize the product of the global soft function and two collinear-
soft functions. Using the collinear anomaly framework, we define a novel soft function W
as
Wab→cd(b, µ)R2Fcd(b,µ) ≡˜Sunsub
ab→cd(b, µ, ν) ˜Scs
c (b, R, µ, ν) ˜Scs
d (b, R, µ, ν)/ ˜Sab(b, µ, ν),
(2.30)
where the rapidity logarithms arising from the narrow jet approximation in the collinear-
soft functions are refactorized through the collinear anomaly exponent Fcd = αs/(2π)(Cc +
Cd) ln
 µ2/µ2
b

+O(α2
s). Notice that in this expression, we have subtracted the back-to-back
soft function, which has already been included in the properly-defined TMDPDFs as in
Eq. (2.26). This subtraction is required to avoid double counting of the soft modes in the
final factorization formalism. Their renormalization group equations have the form as
d
d ln µFcd(b, µ) = (Cc + Cd)γcusp(αs),
(2.31)
d
d ln µW (b, µ) = Γ†
W W (b, µ) + W (b, µ)ΓW ,
(2.32)
where ΓW is expressed as
ΓW =
X
i<j
Ti · Tjγcusp (αs) ln ni · nj
2
(2.33)
+
Cc
2 γcusp(αs) ln sech2yc
4
+ Cd
2 γcusp(αs) ln sech2yd
4

1 + O(α2
s),
A rigorous test of our formalism is that we can obtain the RG invariance of the cross
section as
d
d ln µTr [Hab→cdWab→cd] R2Fcd ˜fa/p ˜fb/pJcJd = 0 .
(2.34)
At NLL accuracy, the TMDPDF matches onto the collinear PDF through the relation
˜fa/p(xa, b, µ, ζa,f) = fa/p (xa, µb∗)
(2.35)
× exp
(Z µ
µb∗
dµ′
µ′
"
Caγcusp(αs) ln µ′2
ζa,f
−2γa(αs)
#)
exp
h
−Sa
NP(b, Q0,
√
ˆs)
i
,
where we have used the fact that the rapidity anomalous dimension vanishes at the scale
µb, ˜κa(b, µb) = 0 at NLL accuracy and the f on the right hand side denotes the collinear
PDF. Additionally, to circumvent the issue of the Landau pole in the large b limit, we
have introduced the b∗prescription that will be discussed in more detail in Sec. 3. Lastly
in Eq. (2.35), we have introduced the non-perturbative Sudakov, which parameterizes the
intrinsic motion of the bound partons and depends on the initial TMD scale Q0.
– 10 –
### Page 12

Combining the results for the hard, jet, TMDPDFs, and soft functions at NLL accu-
racy, our final resummed expression for azimuthal angular distribution is
d4σpp
dyc dyd dp2
T dδϕ =
X
abcd
pT
16πˆs2
1
1 + δcd
Z ∞
0
2db
π cos(bpT δϕ)xa ˜fa/p(xa, µb∗)xb ˜fb/p(xb, µb∗)
× exp
(
−
Z µh
µb∗
dµ
µ

γcusp (αs) CH ln ˆs
µ2 + 2γH (αs)
)
×
X
KK′
exp
"
−
Z µh
µb∗
dµ
µ γcusp (αs) (λK + λ∗
K′)
#
HKK′  ˆs, ˆt, µh

WK′K (b∗, µb∗)
× exp
"
−
Z µj
µb∗
dµ
µ ΓJc (αs) −
Z µj
µb∗
dµ
µ ΓJd (αs)
#
Uc
NG (µb∗, µj) Ud
NG (µb∗, µj)
× exp
h
−Sa
NP(b, Q0,
√
ˆs) −Sb
NP(b, Q0,
√
ˆs)
i
.
(2.36)
In this expression, the quantity λK represents the eigenvalue of the matrices M1,2. In the
small jet radius regime, the resummation of NGLs is achieved through a non-linear RG
evolution between the jet and collinear-soft functions [38] that is contained in the Ui
NG
functions. Lastly, µh and µj are the hard and jet scales which will be discussed in Sec. 3.1.
2.3
Nuclear modified formalism for pA collisions
Having established the factorization and resummation for dijet production in pp collisions
in the previous section, in this section we extend this formalism to incorporate the nuclear
modifications in pA collisions.
As we mentioned in the Introduction, for observables that can be described by the
collinear factorization formalism, a DGLAP-based approach can be used to deal with the
nuclear modification when going from pp to pA collisions. In this approach, one assumes
the same collinear factorization while replacing the proton PDFs with the nuclear modified
PDFs [9–13]. Now for the azimuthal decorrelation of dijet production in the nearly back-
to-back region, a TMD factorization and resummation in Eq. (2.6) is derived. Thus, as
a natural generalization of the idea implemented in nPDFs, when going from pp to pA
collisions, we assume that the same factorization and resummation formalism in Eq. (2.6)
holds for pA collisions, while replacing the proton TMDPDF ˜fb/p with the nuclear modified
TMDPDF ˜fb/A for the target nucleus.
The nTMDPDF ˜fb/A(xb, b, µ, ζb,f) contains the
nuclear modification of both collinear (associated with x) and transverse (associated with
b) motions for the partons inside the nucleus. Follow the assumptions made in Ref. [55],
these nuclear modification will be absorbed into the non-perturbative parameterizations
for the collinear PDF and the non-perturbative Sudakov. Thus under this assumption the
nTMDPDF ˜fb/A(xb, b, µ, ζb,f) can be matched onto the nPDF through the NLL relation
˜fb/A(xb, b, µ, ζb,f) = fb/A (xb, µb∗)
(2.37)
× exp
(Z µ
µb∗
dµ′
µ′
"
Cbγcusp(αs) ln µ′2
ζb,f
−2γb(αs)
#)
exp
h
−Sb,A
NP(b, Q0,
√
ˆs)
i
.
– 11 –
### Page 13

Here, besides the collinear nPDF fb/A (xb, µb∗), we have introduced the medium modified
non-perturbative Sudakov Sb,A
NP(b, Q0,
√
ˆs), whose parameterization will be discussed in the
next section. Note that we only keep the leading power term in the OPE matching in
Eq. (2.37) where the nTMDPDF is matched onto the collinear nPDF. In principle, there
could be power corrections O
 b2Q2
s(A)

in the expansion which are associated with higher-
twist nuclear matrix elements [98]. Here Qs(A) is a dynamical scale, often referred to as
the saturation scale [99], associated with multiple scattering in the nuclear medium. We
do not consider the effect of such power corrections in this paper.
With this replacement for nTMDPDF and following the same resummation procedure,
the factorization and resummation formalism for back-to-back dijet production at NLL
accuracy in pA collisions is given by
d4σpA
dyc dyd dp2
T dδϕ =
X
abcd
pT
16πˆs2
1
1 + δcd
Z ∞
0
2db
π cos(bpT δϕ)xa ˜fa/p(xa, µb∗)xb ˜fb/A(xb, µb∗)
× exp
(
−
Z µh
µb∗
dµ
µ

γcusp (αs) CH ln ˆs
µ2 + 2γH (αs)
)
×
X
KK′
exp
"
−
Z µh
µb∗
dµ
µ γcusp (αs) (λK + λ∗
K′)
#
HKK′  ˆs, ˆt, µh

WK′K (b∗, µb∗)
× exp
"
−
Z µj
µb∗
dµ
µ ΓJc (αs) −
Z µj
µb∗
dµ
µ ΓJd (αs)
#
Uc
NG (µb∗, µj) Ud
NG (µb∗, µj)
× exp
h
−Sa
NP(b, Q0,
√
ˆs) −Sb,A
NP(b, Q0,
√
ˆs)
i
.
(2.38)
In the next section, we will discuss our parameterization for both the collinear nPDFs
˜fb/A(xb, µb∗) and our nuclear modified Sudakov factor Sb,A
NP(b, Q0,
√
ˆs).
3
Numerical parameterization and results
3.1
Parameterization
To capture the resummation of the NGLs, we follow the prescription of Ref. [89] to param-
eterize the U function as
Ui
NG (µb∗, µj) = exp

−CiCA
π2
3 u2 1 + (au)2
1 + (bu)c

,
(3.1)
where u = ln[αs(µb∗)/αs(µj)]/β0, a = 0.85 CA, b = 0.86 CA and c = 1.33 [89].
Since
the factorized formula (2.6) involves two jet functions, the square of UNG is required to
incorporate the NGL resummation associated with each jet.
In previous work on CSS resummation, the b∗-prescription was introduced along with
non-perturbative Sudakov factors, which were modeled through various functional forms
– 12 –
### Page 14

and obtained by fitting to experimental data [100–106]. In this work, we follow the standard
b∗-prescription where
b∗≡b/
p
1 + b2/b2max ,
µb∗= 2e−γE/b∗,
(3.2)
as in [71].
Since we also need to study the impact of the nuclear modification on the
azimuthal angular distribution in proton-nucleus collisions, we adopt the same functional
form used in Refs. [102, 107] which was employed in the extraction of nTMDPDFs [55].
Specifically, the non-perturbative Sudakov factors in the last line of Eq. (2.36) are given
by
Sa,b
NP(b, Q0, Q) = gf
1b2 + g2
2
Ca,b
CF
ln Q
Q0
ln b
b∗
,
(3.3)
with gf
1 = 0.106 GeV−2, g2 = 0.84 and Q2
0 = 2.4 GeV2. Finally, in our numerical calcula-
tions the intrinsic scales in the resummation formula (2.36) are chosen as
µh = pT ,
µj = pT R.
(3.4)
To obtain numerical results for the pA collisions, we need a parameterization for nT-
MDPDF in Eq. (2.37), which contains both the collinear and transverse motion for partons
inside the nucleus. To describe the medium modifications to the collinear PDF, specifically
fb/A (xb, µb∗), we follow the parameterization in [55] to use the EPPS16 parameterization
given in [63] while describing the collinear PDF for the proton, we use CT14nlo parame-
terization [108]. On the other hand, for the nuclear modification to the transverse motion
in nTMDPDFs, we follow the parameterization of Ref. [55] to have a nuclear modified Su-
dakov factor Sb,A
NP(b, Q0,
√
ˆs). Specifically, we replace the g1 parameter in Eq. (3.3), which
accounts for the broadening effects of transverse momentum within the nucleus. Adopting
the functional form obtained from the global extraction in [55], we take
gA
1 = gf
1 + aNL,
with
aN = 0.016 GeV−2 and L = A1/3 −1,
(3.5)
where gA
1 characterizes the transverse momentum width of partons inside the nucleus and
is also proportional to the saturation scale in the small-x region [109]. Thus the nuclear
modified non-perturbative Sudakov factor is defined as
Sb,A
NP(b, Q0, Q) = gA
1 b2 + g2
2
Cb
CF
ln Q
Q0
ln b
b∗
.
(3.6)
3.2
Numerical results
In this section, we present our numerical results for the pp and pA resummation formulas
derived in the previous section. Specifically, we apply the theory formalisms in Eqs. (2.36)
and (2.38) for pp and pA collisions, respectively and compare them with the existing exper-
imental data. We discuss applications of this formalism to measuring nuclear modifications
to collinear and transverse motions of partons in nTMDPDFs. We also provide predictions
for the dijet production in the forward rapidity region in pPb collisions at the LHC, as well
as in pAu collisions for the sPHENIX kinematics at the RHIC.
– 13 –
### Page 15

2.0
2.2
2.4
2.6
2.8
3.0
∆φ
100
101
102
103
104
105
1/σ × dσ/d∆φ
LHC pp
√s = 7 TeV
anti-kT R = 0.5
|y| < 1.1
300 < pT < 1000 GeV(×104)
200 < pT < 300 GeV(×103)
140 < pT < 200 GeV(×102)
110 < pT < 140 GeV(×10)
80 < pT < 110 GeV
2.5
2.6
2.7
2.8
2.9
3.0
3.1
∆φ
10−1
100
101
1/σ × dσ/d∆φ
LHC pPb
√s = 5.02 TeV
anti-kT R = 0.3
|y| < 3
pT > 120 GeV
nPDFs uncert.
CMS Data
Theory
Figure 2. Left: Comparison between theoretical calculations of the azimuthal decorrelation with
the CMS data [60], where ∆ϕ is the difference in the azimuthal angle between two leading jets.
The solid curves are the theoretical distributions, which are normalized by dividing the LO cross
section. The black dots are the CMS results, and the uncertainties of the data are smaller than
the symbol size used in the plot. The colored bands indicate theoretical uncertainties from the
variation of hard and jet scales. Right: A comparison of the dijet azimuthal angle decorrelation in
pPb collisions from the CMS collaboration at the LHC [61].
A comprehensive investigation into the QCD resummation of azimuthal decorrelation
in dijet production in pp collisions was carried out in [32] using the indirect method, as out-
lined in the introduction. The analysis successfully resummed the large logarithmic terms
of azimuthal angle and jet radius at NLL and LL accuracy, respectively, while ignoring the
contribution from NGLs. In our work, we present a resummation formula for azimuthal
decorrelation in the direct method. This approach accounts for both the large logarithmic
terms of the azimuthal angle and jet radius at NLL accuracy, including the contribution
from NGLs. As a verification of the formula, we compare its theoretical predictions to mea-
surements of dijet production in proton-proton collisions taken by the CMS collaboration
at the LHC with √s = 7 TeV, as presented in the left panel of Fig. 2. The QCD jets were
reconstructed using the anti-kT algorithm [110] with a radius of R = 0.5 and the rapidities
of each jet were limited to |yc,d| < 1.1. Additionally, to construct the denominator of the
normalized ∆ϕ distribution, we use the LO expression for the cross section. The data,
shown as black dots, covers five bins ranging from 80 GeV to 1 TeV for the jet transverse
momentum pT . The theoretical results, displayed as lines of different colors, are found to
agree well with the measurements in the back-to-back region across all pT bins. Besides,
we also show the uncertainties from scale variations, which are given by the colored bands.
Here we vary the hard and jet scales by a factor of two around their default values as
defined in Eq. (3.4), and the total uncertainty bands are obtained by the envelope of all
the variations. Since the non-perturbative Sudakov factor in Eq. (3.3) is fitted at the
canonical scale µb∗, we do not include uncertainties from its variations. It is noteworthy
that the contribution of Glauber modes, which can potentially violate TMD factorization,
is not considered in this analysis. Therefore, the magnitude of naive factorization breaking
– 14 –
### Page 16

0.0
0.1
0.2
0.3
0.4
1/σ × dσ/dη
55 < pT < 75 GeV
75 < pT < 95 GeV
LHC pp
√s = 5.02 TeV
anti-kT R = 0.3
∆φ > 2π/3
CT14nlo
CMS Data
−3
−2
−1
0
1
2
3
η
0.0
0.1
0.2
0.3
0.4
1/σ × dσ/dη
95 < pT < 115 GeV
−3
−2
−1
0
1
2
3
η
115 < pT < 150 GeV
−3
−2
−1
0
1
2
3
η
pT > 150 GeV
Figure 3.
Theoretical calculations for the dijet integrated angular decorrelation plotted as a
function of the pseudorapidity η are compared with the CMS data [62] in proton-proton collisions
for different kinematic cuts. The spectra were shifted by +0.465 to match the dijet pseudorapidity
η range of the corresponding proton-lead collisions.
due to Glauber modes can be evaluated by comparing theoretical predictions with future
high-precision experimental measurements.
On the right side of Fig. 2, we plot the azimuthal angle decorrelation in pPb collisions at
√s = 5.02 TeV from the CMS collaboration [61]. The data is integrated within the region
|yc,d| < 3 and the jets were reconstructed using an anti-kT algorithm with R = 0.3. In
the theory calculation, we implement nTMDPDFs which encode the nuclear modification
to the collinear (as in nPDFs fb/A(x, µb∗)) and transverse motion (as in the broadening
parameter aN) in Eqs. (2.37) and (3.6). The dashed blue theory curve is computed with
the central fit of nPDFs in the EPPS16 parametrization and the broadening parameter
aN in Eq. (3.5). The red band is the uncertainty from the nPDFs fit. Our calculations
agree with the experimental data in the back-to-back region ∆ϕ ∼π. We also observed in
both plots of Fig. 2 that our theoretical prediction starts to deviate from the experimental
data points away from the back-to-back region, i.e. when ∆ϕ moves away from π. This is
expected since our formalism applies only to the resummation region. Such a discrepancy
can be corrected by including the fixed order calculation for the dijet azimuthal angular
decorrelation, see for instance [33].
In Fig. 3, we present a comparison between the NLL pQCD calculations of the di-
jet integrated angular decorrelation plotted as a function of the dijet pseudorapidity η =
(yc + yd)/2 in pp collisions, respectively, and corresponding experimental measurement
– 15 –
### Page 17

0.0
0.1
0.2
0.3
0.4
1/σ × dσ/dη
55 < pT < 75 GeV
75 < pT < 95 GeV
LHC pPb
√s = 5.02 TeV
anti-kT R = 0.3
∆φ > 2π/3
EPPS16nlo CT14nlo
Isospin symmetry
nPDFs uncert.
aN uncert.
CMS Data
−3
−2
−1
0
1
2
3
η
0.0
0.1
0.2
0.3
0.4
1/σ × dσ/dη
95 < pT < 115 GeV
−3
−2
−1
0
1
2
3
η
115 < pT < 150 GeV
−3
−2
−1
0
1
2
3
η
pT > 150 GeV
Figure 4. Theoretical calculations for dijet integrated angular decorrelation plotted as a function
of the pseudorapidity η are compared with the CMS data [62] in proton-lead collisions for different
kinematic cuts.
taken by CMS [62]. The data are categorized based on the transverse momentum (pT ) of
the dijet system where the jet radius is R = 0.3. To enable an extensive comparison of
the two datasets, the experimental measurements are superimposed onto the theoretical
predictions, allowing us to evaluate the compatibility between the model and the experi-
mental data. In the theoretical calculation, we integrate ∆ϕ from 2π/3 to π using (2.36)
and to form the σ in the denominator of the integrated azimuthal angle decorrelation, we
integrate over the pseudorapidity coverage of both jets following the experimental cuts.
We observe that our theory calculations describes the experimental data quite well.
In Fig. 4, we present our NLL calculation of the integrated angular decorrelation
plotted as a function of the pseudorapidity in pPb collisions and the CMS experimental
data in [62]. To demonstrate the importance of nuclear modification to parton dynamics in
the nucleus, we include a calculation where one only takes into account the isospin effect.
In other words, going from pp to pA collisions, one only replaces the PDFs in the proton
by the PDFs that include the isospin effect
fi/A (x, µ) = Z
Afi/p (x, µ) + A −Z
A
fi/n (x, µ) ,
(3.7)
where Z is the atomic number of the nucleus while fi/p and fi/n denote the PDFs of the
proton and neutron. We find that the calculations with the isospin effect alone undershoots
the data rather significantly, especially in the mid-rapidity region 0 ≲η ≲1 where an
antishadowing effect is evident from the data [12, 63]. On the other hand, the central blue
– 16 –
### Page 18

0.6
0.8
1.0
1.2
1.4
RpA
55 < pT < 75 GeV
75 < pT < 95 GeV
LHC pPb, pp
√s = 5.02 TeV
anti-kT R = 0.3
∆φ > 2π/3
EPPS16nlo CT14nlo
aN uncert.
nPDFs uncert.
Isospin symmetry
CMS Data
−2
−1
0
1
2
η
0.6
0.8
1.0
1.2
1.4
RpA
95 < pT < 115 GeV
−2
−1
0
1
2
η
115 < pT < 150 GeV
−2
−1
0
1
2
η
pT > 150 GeV
Figure 5. Theoretical calculations for the nuclear modification factor RpA plotted as a function of
the pseudorapidity η are compared with the CMS data [62] for different jet transverse momentum
cuts.
theory curve is computed with the central fit of nPDFs in the EPPS16 parametrization
and the broadening parameter aN in Eq. (3.5). We further considered the uncertainty
band associated with the collinear nPDFs as well as the broadening parameter aN. It is
evident that our formalism with nuclear modification implemented in nTMDPDFs describe
the CMS pPb collision data well though the size of the uncertainties from the broadening
parameter aN is very small. This behavior is expected as the aN parameter acts to broaden
the intrinsic width of the partons. At the large pT values of the CMS data, this broadening is
small compared to the large transverse momentum that is generated from the resummation.
Experimental data at smaller values of pT , which should be measurable at RHIC, will then
depend more strongly on this parameter. However, the small dependence on aN indicates
that both the integrated and unintegrated azimuthal angle decorrelation can be used to
measure the collinear contribution to the nTMDPDFs.
To quantify the nuclear modification, we adopt the usual definition for the nuclear
modification factor
RpA = 1
A
d4σpA
dyc dyd dp2
T d∆ϕ

d4σpp
dyc dyd dp2
T d∆ϕ.
(3.8)
In Fig. 5, we present the nuclear modification factor RpA as a function of dijet rapidity η
between our theory calculations and corresponding experimental data taken by the CMS
collaboration at the LHC [62]. In this plot, we have included a central curve as well as
considered the uncertainty band associated with the nPDF and the broadening parameter
– 17 –
### Page 19

0.50
0.75
1.00
1.25
dσ/d∆φ [µb]
nPDFs uncert.
aN uncert.
pp
pPb
2.6
2.7
2.8
2.9
3.0
3.1
∆φ
0.7
0.8
0.9
1.0
RpA
LHC 8.16 TeV
28 < pT < 35 GeV, 2.7 < y ⋆< 4.0
10
15
20
25
30
dσ/d∆φ [µb]
nPDFs uncert.
aN uncert.
pp
pPb
2.6
2.7
2.8
2.9
3.0
3.1
∆φ
0.6
0.8
1.0
1.2
RpA
LHC 8.16 TeV
pT > 10 GeV, 3.8 < y ⋆< 5.1
1
2
3
dσ/d∆φ [µb]
nPDFs uncert.
aN uncert.
pp
pAu
2.6
2.7
2.8
2.9
3.0
3.1
∆φ
1.0
1.1
RpA
sPHENIX 200 GeV
pT > 10 GeV, |y ⋆| < 0.7
Figure 6. Top: The azimuthal angular distribution in pp (red curve) and pA (black curve) collisions
for ATLAS (Left), ALICE (Middle), and sPHENIX (Right). In the lower panel, we plot the nuclear
modification factor RpA.
aN in nTMDPDFs. We have also included a prediction taking into account the isospin effect
alone. The nuclear modification factor RpA with the isospin effect alone is almost unity as
indicated by the dashed green curve. This is because the dijet production at this energy is
mostly sensitive to the gluon distribution inside the nucleus and thus the isospin symmetry
applied to u and d flavors does not play an important role here. On the other hand, we
observe a strong consistency between the central curve of the NLL pQCD prediction with
nTMDPDFs and the experimental data. However, we find that our calculations do not
describe the strong suppression in the CMS data in the proton’s forward region where
η ≳2 and the probed parton momentum fraction x ∼10−2 inside the nucleus. Since this
modification in our nTMDPDFs formalism is mainly driven by the collinear nPDFs in the
EPPS16 parametrization, as commented in [12, 63], this remains an open question. As
our formalism neglects all final-state interactions associated with Glauber interaction with
the jets [111–113], we suspect that the cause of these discrepancies lies in these final-state
effects [114]. Addressing this discrepancy is vitally important for understanding the gluon
distribution of the bound nucleons at this relatively small x region.
In the left and middle panels of Fig. 6 we present the results of our calculation for the
azimuthal angular distribution in pp and pA collisions in forward rapidity regions at the
ATLAS and ALICE kinematics at the LHC. In the right panel, we present the results of
the decorrelation for the sPHENIX kinematics at the RHIC. In our study, we adopt the
same kinematic cuts at the LHC as used in Ref. [115] and at the RHIC in Ref. [4], which
are defined as follows:
1. 28 GeV < pT < 35 GeV and 2.7 < y∗
c,d < 4.0 for the FCal calorimeter of the ATLAS
at the LHC ,
2. pT > 10 GeV and 3.8 < y∗
c,d < 5.1 for the upgraded FoCal of the ALICE at the LHC ,
– 18 –
### Page 20

3. pT > 10 GeV and |y∗
c,d| < 0.7 for sPHENIX at the RHIC ,
where y∗denotes the jet rapidity in both the pp and pA center of mass frame.
The
upper panels in Fig. 6 show the azimuthal angular distributions in proton-proton (red
curves) and proton-nucleus (black curves) collisions, while the lower panels display the
nuclear modification factor RpA. Our results indicate that in the back-to-back region, the
suppression from the nTMDPDFs is substantial, with a reduction of around 20% for the
ATLAS and 30% for the ALICE kinematics, similar to the nuclear modification reported
in Ref. [115] where a saturation-based formalism is used. This is due to the shadowing
effect in the small-x region where the probed x ∼10−4. On the other hand, our calculation
predicts a small enhancement ∼5% for the sPHENIX kinematics because of the anti-
shadowing effect at x ∼0.1 probed in the sPHENIX experiment. Once again in the left
two panels, we see that the size of the broadening parameter aN is small in comparison to
the uncertainty of the nPDFs. This behavior is once again expected as the LHC produces
jets with large values of pT . In the right panel, we see that the size of the uncertainty from
the broadening parameter aN grows larger, indicating that lower pT jets serve as a better
probe of the transverse dynamics of the bound nucleons.
4
Summary
In this paper, we derived a new resummation formula for the azimuthal decorrelation in
dijet production in proton-proton collisions using SCET. By utilizing the direct method,
we were able to account for both large logarithmic terms of the azimuthal angle and jet
radius. We compared our theoretical predictions with experimental data from the CMS
collaboration and found a strong agreement. We further proposed an approach to deal
with the nuclear modification for nearly back-to-back dijet production in proton-nucleus
collisions by introducing nuclear modified transverse momentum dependent parton distri-
bution functions (nTMDPDFs). The nTMDPDFs contain nuclear modification to both
the collinear and transverse motions for the partons inside the nucleus. Following a simple
model for nTMDPDFs in our previous work that encodes nuclear modification to collinear
dynamics in collinear nPDFs while nuclear modification to transverse motion in a broad-
ening parameter, we present theoretical calculations for dijet production in proton-nucleus
collisions and show good agreement with the existing experimental data at the LHC. Ad-
ditionally, we presented our results for the forward rapidity region at the LHC and for the
mid-rapidity region for sPHENIX at the RHIC. We applied the formula to two kinematic
cuts relevant to the FCal calorimeter of the ATLAS and the upgraded FoCal of the AL-
ICE. The results showed significant suppression of about 20% for the ATLAS and 30% for
the ALICE in the back-to-back limit, due to the shadowing effect in the small-x ∼10−4
region. This suppression is of the same order as previous results within the saturation-
based model. On the other hand, our calculation predicts a small enhancement ∼5%
for the sPHENIX kinematics because of the anti-shadowing effect with x ∼0.1 probed
in the sPHENIX experiment. Overall, this study represents an important step towards a
more complete understanding of azimuthal decorrelation in dijet production and the role
– 19 –
### Page 21

of nuclear modification effects. In future work, we see important applications of our for-
malism, e.g. in performing a simultaneous fit to both collinear and transverse momentum
dependent contributions to the transverse momentum dependent distributions in nuclei. It
would also be interesting to extend our results to other kinematic regions and incorporate
the contributions from higher-order corrections, as well as to generalize our formalism to
describe dijet production in the polarized scattering [116].
Acknowledgments
M.G. and D.Y.S. are supported by the National Science Foundations of China under Grant
No. 12275052 and No. 12147101 and the Shanghai Natural Science Foundation under Grant
No. 21ZR1406100.
Z.K. is supported by the National Science Foundation under grant
No. PHY-1945471.
J.T. is supported by the Department of Energy at LANL through
the LANL/LDRD Program under project number 20220715PRD1. C.Z. is supported by
the National Science Foundations of China under Grant No. 12147125, No. 12275052 and
No. 12147101 and the Shanghai Natural Science Foundation under Grant No. 21ZR1406100.
A
Anomalous dimension
The QCD β-function and the cusp and non-cusp anomalous dimensions are expanded as
β(αs) = −2αs
∞
X
n=0
βn
αs
4π
n+1
,
γ(αs) =
∞
X
n=0
γn
αs
4π
n+1
.
(A.1)
The two-loop coefficients of the β-function and the cusp anomalous dimensions, and the
one-loop coefficient of the non-cusp anomalous dimensions read,
β0 = 11
3 CA −4
3TF nf,
β1 = 34
3 C2
A −20
3 TF CAnf −4TF CF nf,
γcusp
0
= 4,
γcusp
1
=
268
9
−4π2
3

CA −80
9 TF nf,
γJi
0 = −2γi
0,
γq
0 = −3CF ,
γg
0 = −β0,
(A.2)
with TF = 1/2, CA = 3, CF = 4/3, nf = 5.
References
[1] A. Accardi et al., Electron Ion Collider: The Next QCD Frontier: Understanding the glue
that binds us all, Eur. Phys. J. A 52 (2016) 268, [1212.1701].
[2] J. L. Albacete et al., Predictions for p+Pb Collisions at √sNN = 5 TeV , Int. J. Mod. Phys.
E 22 (2013) 1330007, [1301.3395].
[3] E.-C. Aschenauer et al., The RHIC Cold QCD Plan for 2017 to 2023: A Portal to the EIC,
1602.03922.
[4] R. Belmont et al., Predictions for the sPHENIX physics program, in RBRC
Workshop: Predictions for sPHENIX, 5, 2023, 2305.15491.
– 20 –
### Page 22

[5] J. C. Collins, D. E. Soper and G. F. Sterman, Factorization of Hard Processes in QCD,
Adv. Ser. Direct. High Energy Phys. 5 (1989) 1–91, [hep-ph/0409313].
[6] A. D. Martin, W. J. Stirling, R. S. Thorne and G. Watt, Parton distributions for the LHC,
Eur. Phys. J. C 63 (2009) 189–285, [0901.0002].
[7] H.-L. Lai, M. Guzzi, J. Huston, Z. Li, P. M. Nadolsky, J. Pumplin et al., New parton
distributions for collider physics, Phys. Rev. D 82 (2010) 074024, [1007.2241].
[8] NNPDF collaboration, R. D. Ball et al., Parton distributions for the LHC Run II, JHEP
04 (2015) 040, [1410.8849].
[9] K. J. Eskola, H. Paukkunen and C. A. Salgado, A perturbative QCD study of dijets in p+Pb
collisions at the LHC, JHEP 10 (2013) 213, [1308.6733].
[10] M. Hirai, S. Kumano and T. H. Nagai, Determination of nuclear parton distribution
functions and their uncertainties in next-to-leading order, Phys. Rev. C 76 (2007) 065207,
[0709.3038].
[11] D. de Florian and R. Sassot, Nuclear parton distributions at next-to-leading order, Phys.
Rev. D 69 (2004) 074028, [hep-ph/0311227].
[12] K. J. Eskola, P. Paakkinen, H. Paukkunen and C. A. Salgado, EPPS21: a global QCD
analysis of nuclear PDFs, Eur. Phys. J. C 82 (2022) 413, [2112.12462].
[13] I. Helenius, M. Walt and W. Vogelsang, NNLO nuclear parton distribution functions with
electroweak-boson production data from the LHC, Phys. Rev. D 105 (2022) 094031,
[2112.11904].
[14] S. Shen, P. Ru and B.-W. Zhang, Imaging nuclear modifications on parton distributions
with triple-differential dijet cross sections in proton-nucleus collisions, Phys. Rev. D 105
(2022) 096025, [2112.11819].
[15] I. Balitsky, Operator expansion for high-energy scattering, Nucl. Phys. B 463 (1996)
99–160, [hep-ph/9509348].
[16] Y. V. Kovchegov, Small−x F2 structure function of a nucleus including multiple pomeron
exchanges, Phys. Rev. D 60 (1999) 034008, [hep-ph/9901281].
[17] Y. V. Kovchegov, Unitarization of the BFKL pomeron on a nucleus, Phys. Rev. D 61
(2000) 074018, [hep-ph/9905214].
[18] J. Jalilian-Marian, A. Kovner, A. Leonidov and H. Weigert, The Wilson renormalization
group for low x physics: Towards the high density regime, Phys. Rev. D 59 (1998) 014014,
[hep-ph/9706377].
[19] J. Jalilian-Marian, A. Kovner, A. Leonidov and H. Weigert, Unitarization of gluon
distribution in the doubly logarithmic regime at high density, Phys. Rev. D 59 (1999)
034007, [hep-ph/9807462].
[20] J. Jalilian-Marian, A. Kovner and H. Weigert, The Wilson renormalization group for low x
physics: Gluon evolution at finite parton density, Phys. Rev. D 59 (1998) 014015,
[hep-ph/9709432].
[21] E. Iancu, A. Leonidov and L. D. McLerran, Nonlinear gluon evolution in the color glass
condensate. 1., Nucl. Phys. A 692 (2001) 583–645, [hep-ph/0011241].
[22] C. Marquet, Forward inclusive dijet production and azimuthal correlations in pA collisions,
Nucl. Phys. A 796 (2007) 41–60, [0708.0231].
– 21 –
### Page 23

[23] P. Kotko, K. Kutak, C. Marquet, E. Petreska, S. Sapeta and A. van Hameren, Improved
TMD factorization for forward dijet production in dilute-dense hadronic collisions, JHEP
09 (2015) 106, [1503.03421].
[24] W. Ke, Y.-Y. Zhang, H. Xing and X.-N. Wang, eHIJING: an Event Generator for Jet
Tomography in Electron-Ion Collisions, 2304.10779.
[25] P. Ru, Z.-B. Kang, E. Wang, H. Xing and B.-W. Zhang, Global extraction of the jet
transport coefficient in cold nuclear matter, Phys. Rev. D 103 (2021) L031901,
[1907.11808].
[26] P. Ru, Z.-B. Kang, E. Wang, H. Xing and B.-W. Zhang, Probing the jet transport coefficient
of cold nuclear matter in electron-ion collisions, 2302.02329.
[27] F. Arleo and C.-J. Na¨ım, Nuclear p⊥-broadening of Drell-Yan and quarkonium production
from SPS to LHC, JHEP 07 (2020) 220, [2004.07188].
[28] Z.-B. Kang and J.-W. Qiu, Nuclear modification of vector boson production in proton-lead
collisions at the LHC, Phys. Lett. B 721 (2013) 277–283, [1212.6541].
[29] A. Banfi, M. Dasgupta and Y. Delenda, Azimuthal decorrelations between QCD jets at all
orders, Phys. Lett. B 665 (2008) 86–91, [0804.3786].
[30] F. Hautmann and H. Jung, Angular correlations in multi-jet final states from k⊥-dependent
parton showers, JHEP 10 (2008) 113, [0805.1049].
[31] A. Banfi and M. Dasgupta, Dijet rates with symmetric Et cuts, JHEP 01 (2004) 027,
[hep-ph/0312108].
[32] P. Sun, C. P. Yuan and F. Yuan, Soft Gluon Resummations in Dijet Azimuthal Angular
Correlations in Hadronic Collisions, Phys. Rev. Lett. 113 (2014) 232001, [1405.1105].
[33] P. Sun, C. P. Yuan and F. Yuan, Transverse Momentum Resummation for Dijet
Correlation in Hadronic Collisions, Phys. Rev. D 92 (2015) 094007, [1506.06170].
[34] L. Chen, G.-Y. Qin, L. Wang, S.-Y. Wei, B.-W. Xiao, H.-Z. Zhang et al., Study of
Isolated-photon and Jet Momentum Imbalance in pp and PbPb collisions, Nucl. Phys. B933
(2018) 306–319, [1803.10533].
[35] P. Sun, B. Yan, C. P. Yuan and F. Yuan, Resummation of High Order Corrections in Z
Boson Plus Jet Production at the LHC, 1810.03804.
[36] X. Liu, F. Ringer, W. Vogelsang and F. Yuan, Lepton-jet Correlations in Deep Inelastic
Scattering at the Electron-Ion Collider, Phys. Rev. Lett. 122 (2019) 192003, [1812.08077].
[37] M. G. A. Buffing, Z.-B. Kang, K. Lee and X. Liu, A transverse momentum dependent
framework for back-to-back photon+jet production, 1812.07549.
[38] Y.-T. Chien, D. Y. Shao and B. Wu, Resummation of Boson-Jet Correlation at Hadron
Colliders, JHEP 11 (2019) 025, [1905.01335].
[39] X. Liu, F. Ringer, W. Vogelsang and F. Yuan, Lepton-jet Correlation in Deep Inelastic
Scattering, Phys. Rev. D 102 (2020) 094022, [2007.12866].
[40] X. Liu, F. Ringer, W. Vogelsang and F. Yuan, Factorization and its Breaking in Dijet
Single Transverse Spin Asymmetries in pp Collisions, 2008.03666.
[41] Y.-T. Chien, R. Rahn, S. Schrijnder van Velzen, D. Y. Shao, W. J. Waalewijn and B. Wu,
Recoil-free azimuthal angle for precision boson-jet correlation, Phys. Lett. B 815 (2021)
136124, [2005.12279].
– 22 –
### Page 24

[42] Z.-B. Kang, K. Lee, D. Y. Shao and J. Terry, The Sivers Asymmetry in Hadronic Dijet
Production, JHEP 02 (2021) 066, [2008.05470].
[43] R. F. del Castillo, M. G. Echevarria, Y. Makris and I. Scimemi, TMD factorization for dijet
and heavy-meson pair in DIS, JHEP 01 (2021) 088, [2008.07531].
[44] Y. Hatta, B.-W. Xiao, F. Yuan and J. Zhou, Anisotropy in Dijet Production in Exclusive
and Inclusive Processes, Phys. Rev. Lett. 126 (2021) 142001, [2010.10774].
[45] M. I. Abdulhamid et al., Azimuthal correlations of high transverse momentum jets at
next-to-leading order in the parton branching method, Eur. Phys. J. C 82 (2022) 36,
[2112.10465].
[46] R. F. del Castillo, M. G. Echevarria, Y. Makris and I. Scimemi, Transverse momentum
dependent distributions in dijet and heavy hadron pair production at EIC, JHEP 03 (2022)
047, [2111.03703].
[47] Y. Hatta, B.-W. Xiao, F. Yuan and J. Zhou, Azimuthal angular asymmetry of soft gluon
radiation in jet production, Phys. Rev. D 104 (2021) 054037, [2106.05307].
[48] Y.-T. Chien, R. Rahn, D. Y. Shao, W. J. Waalewijn and B. Wu, Precision boson-jet
azimuthal decorrelation at hadron colliders, JHEP 02 (2023) 256, [2205.05104].
[49] H. Bouaziz, Y. Delenda and K. Khelifa-Kerfa, Azimuthal decorrelation between a jet and a
Z boson at hadron colliders, JHEP 10 (2022) 006, [2207.10147].
[50] H. Yang et al., Back-to-back azimuthal correlations in Z+jet events at high transverse
momentum in the TMD parton branching method at next-to-leading order, Eur. Phys. J. C
82 (2022) 755, [2204.01528].
[51] A. B. Martinez and F. Hautmann, Azimuthal di-jet correlations with parton branching
TMD distributions, in 29th International Workshop on Deep-Inelastic Scattering and
Related Subjects, 8, 2022, 2208.08446.
[52] W.-L. Ju and M. Sch¨onherr, Projected transverse momentum resummation in top-antitop
pair production at LHC, JHEP 02 (2023) 075, [2210.09272].
[53] C. Zhang, Q.-S. Dai and D. Y. Shao, Azimuthal decorrelation for photon induced dijet
production in ultra-peripheral collisions of heavy ions, JHEP 23 (2023) 002, [2211.07071].
[54] D. Y. Shao, C. Zhang, J. Zhou and Y. J. Zhou, Lepton pair production in UPCs: towards
the precision test of the resummation formalism, 2306.02337.
[55] M. Alrashed, D. Anderle, Z.-B. Kang, J. Terry and H. Xing, Three-dimensional imaging in
nuclei, Phys. Rev. Lett. 129 (2022) 242001, [2107.12401].
[56] P. C. Barry, L. Gamberg, W. Melnitchouk, E. Moffat, D. Pitonyak, A. Prokudin et al.,
Tomography of pions and protons via transverse momentum dependent distributions,
2302.01192.
[57] A. H. Mueller, B.-W. Xiao and F. Yuan, Sudakov double logarithms resummation in hard
processes in the small-x saturation formalism, Phys. Rev. D 88 (2013) 114010, [1308.2993].
[58] P. Taels, T. Altinoluk, G. Beuf and C. Marquet, Dijet photoproduction at low x at
next-to-leading order and its back-to-back limit, JHEP 10 (2022) 184, [2204.11650].
[59] P. Caucal, F. Salazar, B. Schenke, T. Stebel and R. Venugopalan, Back-to-back inclusive
dijets in DIS at small x: Gluon Weizs¨acker-Williams distribution at NLO, 2304.03304.
– 23 –
### Page 25

[60] CMS collaboration, V. Khachatryan et al., Dijet Azimuthal Decorrelations in pp Collisions
at √s = 7 TeV, Phys. Rev. Lett. 106 (2011) 122003, [1101.5029].
[61] CMS collaboration, S. Chatrchyan et al., Studies of dijet transverse momentum balance and
pseudorapidity distributions in pPb collisions at √sNN = 5.02 TeV, Eur. Phys. J. C 74
(2014) 2951, [1401.4433].
[62] CMS collaboration, A. M. Sirunyan et al., Constraining gluon distributions in nuclei using
dijets in proton-proton and proton-lead collisions at √sNN = 5.02 TeV, Phys. Rev. Lett. 121
(2018) 062002, [1805.04736].
[63] K. J. Eskola, P. Paakkinen, H. Paukkunen and C. A. Salgado, EPPS16: Nuclear parton
distributions with LHC data, Eur. Phys. J. C 77 (2017) 163, [1612.05741].
[64] R. Abdul Khalek, R. Gauld, T. Giani, E. R. Nocera, T. R. Rabemananjara and J. Rojo,
nNNPDF3.0: evidence for a modified partonic structure in heavy nuclei, Eur. Phys. J. C
82 (2022) 507, [2201.12363].
[65] C. W. Bauer, S. Fleming, D. Pirjol and I. W. Stewart, An Effective field theory for collinear
and soft gluons: Heavy to light decays, Phys. Rev. D63 (2001) 114020, [hep-ph/0011336].
[66] C. W. Bauer and I. W. Stewart, Invariant operators in collinear effective theory, Phys. Lett.
B516 (2001) 134–142, [hep-ph/0107001].
[67] C. W. Bauer, D. Pirjol and I. W. Stewart, Soft collinear factorization in effective field
theory, Phys. Rev. D65 (2002) 054022, [hep-ph/0109045].
[68] C. W. Bauer, S. Fleming, D. Pirjol, I. Z. Rothstein and I. W. Stewart, Hard scattering
factorization from effective field theory, Phys. Rev. D66 (2002) 014017, [hep-ph/0202088].
[69] M. Beneke, A. P. Chapovsky, M. Diehl and T. Feldmann, Soft collinear effective theory and
heavy to light currents beyond leading power, Nucl. Phys. B643 (2002) 431–476,
[hep-ph/0206152].
[70] J. C. Collins and D. E. Soper, Back-To-Back Jets in QCD, Nucl. Phys. B193 (1981) 381.
[71] J. C. Collins, D. E. Soper and G. F. Sterman, Transverse Momentum Distribution in
Drell-Yan Pair and W and Z Boson Production, Nucl. Phys. B 250 (1985) 199–224.
[72] T. Becher and M. Neubert, Drell-Yan Production at Small qT , Transverse Parton
Distributions and the Collinear Anomaly, Eur. Phys. J. C71 (2011) 1665, [1007.4005].
[73] T. Becher, M. Neubert and D. Wilhelm, Electroweak Gauge-Boson Production at Small qT :
Infrared Safety from the Collinear Anomaly, JHEP 02 (2012) 124, [1109.6027].
[74] J. Collins and J.-W. Qiu, kT factorization is violated in production of
high-transverse-momentum particles in hadron-hadron collisions, Phys. Rev. D75 (2007)
114014, [0705.2141].
[75] T. C. Rogers and P. J. Mulders, No Generalized TMD-Factorization in Hadro-Production of
High Transverse Momentum Hadrons, Phys. Rev. D 81 (2010) 094006, [1001.2977].
[76] S. Catani, D. de Florian and G. Rodrigo, Space-like (versus time-like) collinear limits in
QCD: Is factorization violated?, JHEP 07 (2012) 026, [1112.4405].
[77] J. R. Forshaw, M. H. Seymour and A. Siodmok, On the Breaking of Collinear Factorization
in QCD, JHEP 11 (2012) 066, [1206.6363].
[78] I. W. Stewart, Lectures on the Soft-Collinear Effective Theory, MIT Open Course Ware,
Effective Field Theory (Spring 2013) .
– 24 –
### Page 26

[79] T. Becher, A. Broggio and A. Ferroglia, Introduction to Soft-Collinear Effective Theory,
Lect. Notes Phys. 896 (2015) pp.1–206, [1410.1892].
[80] M. D. Schwartz, Quantum Field Theory and the Standard Model. Cambridge University
Press, 3, 2014.
[81] A. Gao, J. K. L. Michel, I. W. Stewart and Z. Sun, Better angle on hadron transverse
momentum distributions at the Electron-Ion Collider, Phys. Rev. D 107 (2023) L091504,
[2209.11211].
[82] R. Boussarie et al., TMD Handbook, 2304.03302.
[83] J. Collins, Foundations of perturbative QCD, vol. 32. Cambridge University Press, 11, 2013.
[84] S. Catani and M. H. Seymour, The Dipole formalism for the calculation of QCD jet
cross-sections at next-to-leading order, Phys. Lett. B 378 (1996) 287–301,
[hep-ph/9602277].
[85] R. Kelley and M. D. Schwartz, 1-loop matching and NNLL resummation for all partonic 2
to 2 processes in QCD, Phys. Rev. D 83 (2011) 045022, [1008.2759].
[86] A. J. Gao, H. T. Li, I. Moult and H. X. Zhu, Precision QCD Event Shapes at Hadron
Colliders: The Transverse Energy-Energy Correlator in the Back-to-Back Limit, Phys. Rev.
Lett. 123 (2019) 062001, [1901.04497].
[87] V. Ahrens, A. Ferroglia, M. Neubert, B. D. Pecjak and L. L. Yang, Renormalization-Group
Improved Predictions for Top-Quark Pair Production at Hadron Colliders, JHEP 09 (2010)
097, [1003.5827].
[88] S. D. Ellis, C. K. Vermilion, J. R. Walsh, A. Hornig and C. Lee, Jet Shapes and Jet
Algorithms in SCET, JHEP 11 (2010) 101, [1001.0014].
[89] M. Dasgupta and G. P. Salam, Resummation of nonglobal QCD observables, Phys. Lett. B
512 (2001) 323–330, [hep-ph/0104277].
[90] T. Becher, M. Neubert, L. Rothen and D. Y. Shao, Effective Field Theory for Jet Processes,
Phys. Rev. Lett. 116 (2016) 192001, [1508.06645].
[91] T. Becher, M. Neubert, L. Rothen and D. Y. Shao, Factorization and Resummation for Jet
Processes, JHEP 11 (2016) 019, [1605.02737].
[92] M. Dasgupta and G. P. Salam, Accounting for coherence in interjet ET flow: A Case study,
JHEP 03 (2002) 017, [hep-ph/0203009].
[93] A. Broggio, A. Ferroglia, B. D. Pecjak and Z. Zhang, NNLO hard functions in massless
QCD, JHEP 12 (2014) 005, [1409.5294].
[94] O. Almelid, C. Duhr and E. Gardi, Three-loop corrections to the soft anomalous dimension
in multileg scattering, Phys. Rev. Lett. 117 (2016) 172002, [1507.00047].
[95] O. Almelid, C. Duhr, E. Gardi, A. McLeod and C. D. White, Bootstrapping the QCD soft
anomalous dimension, JHEP 09 (2017) 073, [1706.10162].
[96] J.-y. Chiu, A. Jain, D. Neill and I. Z. Rothstein, The Rapidity Renormalization Group,
Phys. Rev. Lett. 108 (2012) 151601, [1104.0881].
[97] J.-Y. Chiu, A. Jain, D. Neill and I. Z. Rothstein, A Formalism for the Systematic Treatment
of Rapidity Logarithms in Quantum Field Theory, JHEP 05 (2012) 084, [1202.0814].
– 25 –
### Page 27

[98] Z.-B. Kang, X. Liu, S. Mantry and J.-W. Qiu, Probing nuclear dynamics in jet production
with a global event shape, Phys. Rev. D 88 (2013) 074020, [1303.3063].
[99] F. Gelis, E. Iancu, J. Jalilian-Marian and R. Venugopalan, The Color Glass Condensate,
Ann. Rev. Nucl. Part. Sci. 60 (2010) 463–489, [1002.0333].
[100] J. Collins and T. Rogers, Understanding the large-distance behavior of
transverse-momentum-dependent parton densities and the Collins-Soper evolution kernel,
Phys.Rev. D91 (2015) 074020, [1412.3820].
[101] C. Aidala, B. Field, L. Gamberg and T. Rogers, Limits on TMD Evolution From
Semi-Inclusive Deep Inelastic Scattering at Moderate Q, Phys.Rev. D89 (2014) 094002,
[1401.2654].
[102] P. Sun, J. Isaacson, C. P. Yuan and F. Yuan, Nonperturbative functions for SIDIS and
Drell–Yan processes, Int. J. Mod. Phys. A 33 (2018) 1841006, [1406.3073].
[103] F. Landry, R. Brock, P. M. Nadolsky and C. P. Yuan, Tevatron Run-1 Z boson data and
Collins-Soper-Sterman resummation formalism, Phys. Rev. D67 (2003) 073016,
[hep-ph/0212159].
[104] A. V. Konychev and P. M. Nadolsky, Universality of the Collins-Soper-Sterman
nonperturbative function in gauge boson production, Phys.Lett. B633 (2006) 710–714,
[hep-ph/0506225].
[105] A. Bacchetta, F. Delcarro, C. Pisano, M. Radici and A. Signori, Extraction of partonic
transverse momentum distributions from semi-inclusive deep-inelastic scattering, Drell-Yan
and Z-boson production, JHEP 06 (2017) 081, [1703.10157].
[106] MAP collaboration, A. Bacchetta, V. Bertone, C. Bissolotti, G. Bozzi, M. Cerutti,
F. Piacenza et al., Unpolarized transverse momentum distributions from a global fit of
Drell-Yan and semi-inclusive deep-inelastic scattering data, JHEP 10 (2022) 127,
[2206.07598].
[107] M. G. Echevarria, Z.-B. Kang and J. Terry, Global analysis of the Sivers functions at
NLO+NNLL in QCD, JHEP 01 (2021) 126, [2009.10710].
[108] S. Dulat, T.-J. Hou, J. Gao, M. Guzzi, J. Huston, P. Nadolsky et al., New parton
distribution functions from a global analysis of quantum chromodynamics, Phys. Rev. D 93
(2016) 033006, [1506.07443].
[109] A. H. Mueller, B. Wu, B.-W. Xiao and F. Yuan, Medium Induced Transverse Momentum
Broadening in Hard Processes, Phys. Rev. D 95 (2017) 034007, [1608.07339].
[110] M. Cacciari, G. P. Salam and G. Soyez, The anti-kt jet clustering algorithm, JHEP 04
(2008) 063, [0802.1189].
[111] A. Idilbi and A. Majumder, Extending Soft-Collinear-Effective-Theory to describe hard jets
in dense QCD media, Phys. Rev. D 80 (2009) 054022, [0808.1087].
[112] G. Ovanesyan and I. Vitev, An effective theory for jet propagation in dense QCD matter:
jet broadening and medium-induced bremsstrahlung, JHEP 06 (2011) 080, [1103.1074].
[113] I. Z. Rothstein and I. W. Stewart, An Effective Field Theory for Forward Scattering and
Factorization Violation, JHEP 08 (2016) 025, [1601.04695].
[114] Z.-B. Kang, F. Ringer and I. Vitev, Inclusive production of small radius jets in heavy-ion
collisions, Phys. Lett. B 769 (2017) 242–248, [1701.05839].
– 26 –
### Page 28

[115] M. A. Al-Mashad, A. van Hameren, H. Kakkad, P. Kotko, K. Kutak, P. van Mechelen
et al., Dijet azimuthal correlations in p-p and p-Pb collisions at forward LHC calorimeters,
JHEP 12 (2022) 131, [2210.06613].
[116] STAR collaboration, Measurement of transverse single-spin asymmetries for dijet
production in polarized proton-proton collisions at √s = 200 GeV, 2305.10359.
– 27 –