# MUTR3D Multi-object Tracking with 3D Detection

**Source**: arxiv PDF, 22 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Neural Shape Deformation Priors
Jiapeng Tang1
Lev Markhasin2
Bi Wang2
Justus Thies3
Matthias Nießner1
1 Technical University of Munich
2 Sony Europe RDC Stuttgart
3 Max Planck Institute for Intelligent Systems, Tübingen, Germany
https://tangjiapeng.github.io/projects/NSDP/
Figure 1: Neural shape deformation priors allow for intuitive shape manipulation of existing source
meshes. A user can create novel shapes by dragging handles (red circles) deﬁned on the region of
interest (red regions) to desired locations (blue circles).
Abstract
We present Neural Shape Deformation Priors, a novel method for shape manip-
ulation that predicts mesh deformations of non-rigid objects from user-provided
handle movements. State-of-the-art methods cast this problem as an optimization
task, where the input source mesh is iteratively deformed to minimize an objective
function according to hand-crafted regularizers such as ARAP [54]. In this work,
we learn the deformation behavior based on the underlying geometric properties of
a shape, while leveraging a large-scale dataset containing a diverse set of non-rigid
deformations. Speciﬁcally, given a source mesh and desired target locations of
handles that describe the partial surface deformation, we predict a continuous
deformation ﬁeld that is deﬁned in 3D space to describe the space deformation.
To this end, we introduce transformer-based deformation networks that represent
a shape deformation as a composition of local surface deformations. It learns a
set of local latent codes anchored in 3D space, from which we can learn a set of
continuous deformation functions for local surfaces. Our method can be applied to
challenging deformations and generalizes well to unseen deformations. We validate
our approach in experiments using the DeformingThing4D dataset, and compare to
both classic optimization-based and recent neural network-based methods.
1
Introduction
Editing and deforming 3D shapes is a key component in animation creation and computer aided
design pipelines. Given as little user input as possible, the goal is to create new deformed instances
of the original 3D shape which look natural and behave like real objects or animals. The user input is
assumed to be very sparse, such as vertex handles that can be dragged around. For example, users
can animate a 3D model of an animal by dragging its feet forward. This problem is severely ill-
posed and typically under-constrained, as there are many possible deformations that can be matched
with the provided partial surface deformations of handles, especially for large surface deformations.
36th Conference on Neural Information Processing Systems (NeurIPS 2022).
arXiv:2210.05616v2  [cs.CV]  1 Feb 2023
### Page 2

Thus, strong priors encoding deformation regularity are necessary to tackle this problem. Physics
and differential geometry provide solutions that use various analytical priors which deﬁne natural-
looking mesh deformations, such as elasticity [62, 1], Laplacian smoothness [31, 55, 77], and
rigidity [54, 57, 29] priors. They update mesh vertex coordinates by iteratively optimizing energy
functions that satisfy constraints from both the pre-deﬁned deformation priors and given handle
locations. Although these algorithms can preserve geometric details of the original source model,
they still have limited capacity to model realistic deformations, since the deformation priors are
region independent, e.g., the head region deforms in a similar way as the tail of an animal, resulting
in unrealistic deformation states.
Hence, motivated by the recent success of deep neural networks for 3D shape modeling [33, 42,
13, 68, 58, 14, 44, 26, 2, 18, 10, 63, 60, 12], we propose to learn shape deformation priors of a
speciﬁc object class, e.g., quadruped animals, to complete surface deformations beyond observed
handles. We formulate the following properties of such a learned model; (1) it should be robust to
different mesh quality and number of vertices, (2) the source mesh is not limited to canonical pose
(i.e., the input mesh can have arbitrary pose), and (3) it should generalize well to new deformations.
Towards these goals, we represent deformations as a continuous deformation ﬁeld which is deﬁned
in the near-surface region to describe the space deformation caused by the corresponding surface
deformation. The continuity property enables us to manipulate meshes with inﬁnite number of
vertices and disconnected components. To handle source meshes in arbitrary poses, we learn shape
deformations via canonicalization. Speciﬁcally, the overall deformation process consists of two
stages: arbitrary-to-canonical transformation and canonical-to-arbitrary transformation. To obtain
more detailed surface deformations and better generalization capabilities to unseen deformations,
we propose to learn local deformation ﬁelds conditioned on local latent codes encoding geometry-
dependent deformation priors, instead of global deformation ﬁelds conditioned on a single latent
code. To this end, we propose Transformer-based Deformation Networks (TD-Nets), which learns
encoder-based local deformation ﬁelds on point cloud approximations of the input mesh. Concretely,
TD-Nets encode an input point cloud with surface geometry information and incomplete deformation
ﬂow into a sparse set of local latent codes and a global feature vector by using the vector attention
blocks proposed in [74]. The deformation vectors of spatial points are estimated by an attentive
decoder, which aggregates the information of neighboring local latent codes of a spatial point based
on the feature similarity relationships. The aggregated feature vectors are ﬁnally passed to a multi-
layer-perceptron (MLP) to predict displacement vectors which can be applied to the source mesh to
compute the ﬁnal output mesh.
To summarize, we introduce transformer-based local deformation ﬁeld networks which are capable
to learn shape deformation priors for the task of user-driven shape manipulation. The deformation
networks learn a set of anchor features based on a vector attention mechanism, enhancing the
global deformation context, and selecting the most informative local deformation descriptors for
displacement vector estimations, leading to an improved generalization ability to new deformations.
In comparison to classical hand-crafted deformation priors as well as recent neural network-based
deformation predictors, our method achieves more accurate and natural shape deformations.
2
Related Work
User-guided shape manipulation lies at the intersection of computer graphics and computer vision.
Our proposed method is related to polygonal mesh geometry processing, neural ﬁeld representations,
as well as vision transformers.
Optimization-based Shape Manipulation.
Classical methods formulate shape manipulation as
a mathematical optimization problem. They perform mesh deformations by either deforming the
vertices [5, 53] or the 3D space [23, 3, 29, 37, 51]. Performing mesh deformation without any other
information about the target shape, but only using limited user-provided correspondences is an under-
constrained problem. To this end, the optimization methods require deformation priors to constraint
the deformation regularity as well as the smoothness of the deformed surface. Various analytic
priors have been proposed which encourage smooth surface deformations, such as elasticity [62, 1],
Laplacian smoothness [31, 55, 77], and rigidity [54, 57, 29]. These methods use efﬁcient linear solvers
to iteratively optimize energy functions that satisfy constraints from both the pre-deﬁned deformation
prior and provided handle movements. Recently, NFGP [69] was proposed to optimize neural
2
### Page 3

networks with non-linear deformation regularizations. Speciﬁcally, it performs shape deformations
by warping the neural implicit ﬁelds of the source model through a deformation vector ﬁeld, which
is constrained by modeling implicitly represented surfaces as elastic shells.
NeuralMLS [52]
learned a geometry-aware weight function of a shape and given control points for moving least
squares(MLS) deformations, which smoothly interpolates the control point displacements over space.
Although they can preserve many geometric details of the source shape, they struggle to model
complex deformations, as local surfaces are simply constrained to be transformed in a similar manner.
In contrast, we aim to learn deformation priors based on local geometries to infer hidden surface
deformations.
Learning-based Shape Reconstruction and Manipulation.
Learning-based shape manipulation
has been studied to learn shape priors based on shape auto-encoding or auto-decoding. [76, 15, 20, 25]
map a class of shapes into a latent space. During inference, given handle positions as input, they
ﬁnd an optimal latent code whose 3D interpretation is the most similar to the observation. In
contrast, we learn explicit deformation priors to directly predict 3D surface deformations. Jakab et
al. [24] proposed to control shapes via unsupervised 3D keypoint discovery. Instead, we use partial
surface deformations represented by handle displacements as input observations, rather than keypoint
displacements. There exist a series of methods that use deep neural networks to complete non-rigid
shapes [25, 41, 7, 30, 61, 50, 66, 8] from partial scans. Our task is partially related to this task,
but our shape manipulation task from user input requires completion of the deformation ﬁeld. In
contrast to shape completion, our setting is more under-constrained, as the user-provided handle
correspondences are very sparse and more incomplete than partial point clouds from scans. Recent
methods for clothed-human body reconstruction choose to canonicalize the captured scan into a pre-
deﬁned T-pose [65, 35, 11] using the skeletal deformation model of SMPL [32] or STAR [40] which
can also be used to later animate the human. Inspired by this, we also perform a canonicalization to
enable editing of source meshes with arbitrary poses, before applying the actual deformation towards
the target pose handles.
Continuous Neural Fields.
Continuous neural ﬁeld representations have been widely used in
3D shape modeling [33, 13, 42] and 4D dynamics capture [39, 61, 7, 41, 30]. Recent work that
represents 3D shapes as continuous signed distance ﬁelds [2, 68, 18, 10, 63] or occupancy ﬁelds [33,
13, 14, 34, 44, 26, 59, 60, 17, 72] can theoretically obtain volumetric reconstructions with inﬁnite
resolutions, as they are not bound to the resolution of a discrete grid structure. Similarly, we learn
continuous deformation ﬁelds deﬁned in 3D space for shape deformations [58, 25, 69, 21]. Due to
the continuity of the deformation ﬁelds, our method is not limited by the number of mesh vertices,
or disconnected components.
Different from ShapeFlow [25], OFlow [39], LPDC-Net [61] and
NPMs [41] that learn a deformation ﬁeld from a single latent code, inspired by local implicit ﬁeld
learning [14, 44, 60, 17, 71], we model the deformation ﬁeld as a composition of local deformation
functions, improving the representation capability of describing complex deformations as well as
generalization to new deformations.
Visual Transformers.
Recently, transformer architectures [64] from natural language processing
have revolutionized many computer vision tasks, including image classiﬁcation [16, 67], object
recognition [9], semantic segmentation [75], or 3D reconstruction [6, 70, 17, 71, 46]. We refer the
reader to [19] for a detailed survey of visual transformers. In this work, we propose the usage of
a transformer architecture to learn deformation ﬁelds. Given the input point cloud sampled from
the source mesh with partial deformation ﬂow (deﬁned by the user handles), we employ the vector
attention blocks from Point Transformer [74] as a main point cloud processing module to extract a
sparse set of local latent codes, enhancing the global understanding of deformation behaviours. Based
on the obtained local deformation descriptors, our attentive deformation decoder learns to attend to
the most informative features from near-by local codes to predict a deformation ﬁeld.
3
Approach
Given a source mesh S = {V, F} where V and F denote the set of vertices and the set of faces,
respectively, we aim to deform S to obtain a target mesh T by selecting a sparse set of mesh vertices
H = {hi}ℓ
i=1 as handles, and dragging them to target locations O = {oi}ℓ
i=1. The key idea in this
work is to use deformation priors to complete hidden surface deformations. Speciﬁcally, the goal
3
### Page 4

User Input
Source Mesh
Target Handle Locations
Backward
Deformation
Networks
Forward
Deformation
Networks
Shape Deformation via Canonicalization
Target Mesh
Figure 2: Overview. Given a source mesh S with sparse handles H (red circles) and their respective
target locations O (blue circles) as input, our method deforms the mesh to the target mesh T via
canonicalization C. The backward Ωb and forward Ωf deformation networks store the deformation
priors that allow our method to produce consistent and natural-looking outputs.
is to learn a continuous deformation ﬁeld D deﬁned in 3D space, from which we can obtain the
deformed mesh T ′ = {V +D(V), F} through vertex deformations of the source mesh S. The overall
pipeline of the proposed approach is shown in Figure 2. Our method can be applied to input meshes
in arbitrary poses by leveraging learned shape deformation via canonicalization (see Section 3.1).
To represent the underlying deformation prior, we propose neural deformation ﬁelds as described in
Section 3.2 which can be learned from large deformation datasets (see Section 3.3).
3.1
Learning Shape Deformations via Canonicalization
To ensure robustness w.r.t. varying input mesh quality (topology and resolution), we operate on
point clouds instead of meshes. Speciﬁcally, we sample a point cloud PS = {pi}n
i=0 ∈Rn×3 from
S of size n = 5000. We deﬁne the target handle point locations PO = {oi}n
i=0 ∈Rn×3, where
we use zeros to represent unknown point ﬂows. Further, to avoid the ambiguity of zero point ﬂow,
we deﬁne the corresponding binary user handle masks M = {bi}n
i=0 ∈Rn where bi = 1 if pi is a
handle or otherwise bi = 0.
To learn the shape transformation between two arbitrary non-rigidly deformed poses, one can learn
deformation ﬁelds that directly map the source deformed space to target space. However, it would be
difﬁcult to learn the deformation priors well, as there could be inﬁnite deformation state transformation
pairs. To decrease the learning complexity, we introduce a canonical space as an intermediate state.
We divide the shape transformation process into two steps; a backward deformation that aligns the
source deformed space to canonical space, and a forward deformation that maps the canonical space to
the target deformation space. Concretely, PS is passed into the backward transformation network Ωb
to learn the backward deformation ﬁeld Db which transforms the input shape PS into a canonical pose
P′
C. Similarly, the querying non-surface point set QS = {qi}m
i=0 ∈Rm×3, m = 5000 randomly
sampled in the 3D space of S is also mapped to canonical space through Q′
C = QS + Db(QS).
Lastly, given P′
C, M, and PO as input, a forward transformation network Ωf is learned to represent
the forward deformation ﬁeld Df that predicts ﬁnal locations Q′
T = Q′
C + Df(Q′
C).
3.2
Transformer-based Deformation Networks (TD-Nets)
The deformation via canonicalization is based on two deformation ﬁeld predictors (forward and
backward deformations). Both networks share the same architecture, thus, in the following, we
will only describe the forward deformation network as visualized in Figure 3 while the backward
deformation network is analogous. It consists of a transformer-based deformation encoder and a
vector cross attention-based decoder network.
Point transformer encoder.
Given a point set PC with handle locations PO and a binary mask
M as inputs, we use point transformer layers from [74] to build our encoder modules. The point
transformer layer is based on the vector attention mechanism [73]. Let X = {xi, fi}i and Y =
{yi, gi}i be the query and key-value sequences, where xi and yi denote the coordinates of query and
key-value points with corresponding feature vectors fi and gi. The vector cross attention operator
4
### Page 5

User Input
VCA
Transformer
Encoder
MLP
Sampling
…
Target mesh
Pooling & FCs
kNN
Query
Key-Values
Figure 3: Transformer-based Forward Deformation Networks. Given a canonical mesh C with
handle positions H (red circles) and desired handle locations O (blue circles), we perform surface
sampling to obtain a point cloud PC with additional channels of handle mask M and point ﬂow PO.
A point-transformer encoder is devised to extract a sparse set of local latent codes Z = {ci, zi}i from
this point cloud, where ci are the anchor positions of the latent features zi. For a speciﬁc point q in
3D space (i.e. a vertex from the source mesh), based on the zglo, a vector cross attention (VCA) block
is used to effectively fuse the information of Zq into zq from the k nearest neighbouring latent codes
of q. Using a multi-layer perceptron (MLP) conditioned on zq, we predict the deformed location q′
in the target space.
VCA is deﬁned as:
VCA(X, Y) : f ′
i =
X
j∈Ni
ρ(γ(ϕ(gj) −ψ(fi) + δ)) ⊙(α(fi) + δ),
(1)
where f ′
i are the aggregated features, ϕ, ψ, and α are linear projections implemented by a fully-
connected layer. γ is a mapping function implemented by a two-layer MLP to predict attention
vectors. ρ is the attention weight normalization function, in our case softmax. δ := θ(xi −yj) is the
positional embedding module [64, 36] implemented by a two linear layers with a single ReLU [38].
It leverages relatively positional information of xi and yj to beneﬁt the network training. Then, with
the deﬁnition of VCA, the vector self-attention operator VSA can be deﬁned as:
VSA(X) := VCA(X, X).
(2)
Based on VCA and VSA, we can deﬁne two basic modules to build our encoder network, i.e. the
point transformer block (PTB) and the point abstraction block (PAB). The deﬁnition of the point
transformer block PTB is a combination of the BatchNorm (BN) layer [22], VSA, and residual
connections, formulated as:
PTB(X) := BN(X + VSA(X)).
(3)
For each point Xi, it encapsulates the information from kenc = 16 nearest neighborhoods while
keeping the point’s position xi unchanged. The point abstraction block PAB consists of farthest
point sampling (FPS), BN, VCA, and VSA, which is deﬁned as follow:
PAB(X) := BN(FPS(X) + VSA(VCA(FPS(X), X)).
(4)
The point cloud PC with handle mask M and ﬂow PO as additional channels are passed to a point
transformer block (PTB) to obtain a feature point cloud Z0 = {c0
i , z0
i }n
i=1. By using two consecutive
point abstraction blocks (PABs) with intermediate set size of n1 = 500 and n2 = 100, we obtain
Z1 = {c1
i , z1
i }n1
i=1 and Z2 = {c2
i , z2
i }n2
i=1. To enhance global deformation priors, we stack 4 point
transformer blocks with full self-attention whose kenc is set to 100 to exchange the global information
in the whole set of Z2. By doing so, we can obtain a sparse set of local deformation descriptors
Z = {ci, zi}100
i=1 that are anchored in {ci}. Finally, we perform a global max-pooling operation
followed by two linear layers to obtain the global latent vector zglo.
Attentive deformation decoder. Based on the learned local latent codes Z = {ci, zi}100
i=1 and global
latent vector zglo, the deformation decoder deﬁnes the forward deformation function Df : R3 −→R3,
which maps a point q from the canonical space of C to the 3D space of T . Similar to tri-linear
interpolation operations in grid-based implicit ﬁeld learning, a straightforward way to ﬁnd the
corresponding feature vector zq is to use the weighted combination of kdec = 16 nearby local
codes Zq = {ck, zk}kdec
k=1. Intuitively, the weight is inversely proportional to the euclidean distance
between q and the anchoring location ck [44]. However, distance-based feature queries ignore
5
### Page 6

the relationships between deformation descriptors. Thus, we propose to obtain zq by adaptively
aggregating information of Zq based on the vector cross-attention operator:
zq = VCA({q, zglo}, Zq).
(5)
The local information aggregation enables us to ﬂexibly search the local deformation priors, thus,
improving the generalizability to new deformations. Finally, the zq is fed into an MLP composed of
ﬁve Res-FC blocks to estimate the associate location q′ = q + Df(q; zq) in the target space.
3.3
Training Objectives
For training, we need a set of triplets (S, C, T ) with dense correspondences, from which we can
randomly sample surface point clouds (PS, PC, PT ) of size n and querying non-surface points
(QS, QC, QT ) of size m in the 3D space. To optimize the backward deformation networks, we
employ the mean ℓ2 distance error that measures the difference between deformed points from source
space and their ground-truths in the canonical space:
Lb = ||Ωb(PS) −PC||2
2 + ||Ωb(QS) −QC||2
2.
(6)
Similarly, to optimize the forward deformation networks, we use the following loss function:
Lf = ||Ωf(PC) −PT ||2
2 + ||Ωb(QC) −QT ||2
2
(7)
The total loss function for source-target shape deformations is deﬁned as:
Ltotal = ||Ωf(Ωb(PS)) −PT ||2
2 + ||Ωf(Ωb(QS)) −QT ||2
2.
(8)
4
Experiments
Dataset.
Our experiments are performed on the DeformingThing4D-Animals [30] dataset which
contains 1494 non-rigidly deforming animations with various motions comprising 40 identities of 24
categories. For the train/test split, we divide all animations into training (1296) and test (198). Similar
to the D-FAUST [4] used in OFlow [39], the test set is composed of two subsets: (S1) contains
143 sequences of new motions for seen train identities, and (S2) contains 55 sequences of unseen
individuals (and thus also new motions). During training, we randomly sample two frames from
an identity as source-target deformation pairs. During inference, we consider the ﬁrst frame of an
animation as source mesh, and other frames as target meshes. To evaluate the generalization ability
to unseen identities, we evaluate the pre-trained models on the animal dataset used in Deformation
Transfer [56]. For the quantitative comparison on each test subset, we compute evaluation metrics for
300 randomly sampled pairs. In addition, we also include comparisons on another animal dataset
used in TOSCA [47]. TOSCA [47] does not have correspondences between different poses of the
same animal, and hence does not easily provide handle displacements as input. Thus, we provide a
qualitative comparison under the setting of using user-speciﬁed handles as inputs.
Implementation details.
Our approach is built on the PyTorch library [43]. Please refer to the
supplementary material for the details of our network architecture. Our model consists of two training
stages. We use an Adam [28] optimizer with β1 = 0.9, β2 = 0.999, and ϵ = 10−8. In the ﬁrst stage,
we train the forward and backward deformation networks individually. Speciﬁcally, the backward and
forward deformation networks are respectively optimized by the objective described in Equations 6
or 7 using a batch size of 16 with the learning rate of 5e-4 for 100 epochs. In the second stage, the
whole model is trained according to Equation 8 in an end-to-end manner using a batch size of 6 with
a learning rate of 5e-5 for 20 epochs.
Baselines.
We conduct comparisons against classical optimization-based and recent neural network-
based methods. For the former, we select a representative work, ARAP [54], that constrains each
local surface to be rigidly transformed as much as possible. For the latter, we compare our method
with the learning-based deformation predictor ShapeFlow [25] that embeds each shape into a latent
space and learns ﬂow-based deformations among 3D shapes. We also compare to NFGP [69], a deep
optimization method, which constrains the implicitly represented surfaces as elastic shells during the
deformation process.
6
### Page 7

Source mesh
Target mesh
ARAP [54]
ShapeFlow [25]
NFGP [69]
Ours
and handles
and handles
Figure 4: Comparison against ARAP [54], ShapeFlow [25], and NFGP [69] on new motions. We
visualize the vertex euclidean distance errors as color maps.
Source mesh
Target mesh
ARAP [54]
ShapeFlow [25]
NFGP [69]
Ours
and handles
and handles
Figure 5: Comparison against ARAP [54], ShapeFlow [25], and NFGP [69] on the S2 test set of
DeformingThing4D-Animals and unseen shapes of Deformation Transfer [56]. We visualize the
vertex euclidean distance errors as color maps. Our approach generalizes better in comparison to
ShapeFlow and NFGP and produces natural looking deformations (in comparison, ARAP generates
rubber-like deformations).
Evaluation metrics.
We consider ℓ2 distance error of mesh vertices (ℓ2 ×0.001), Chamfer Distance
(CD ×0.01) of sampled point clouds of 30k points, and Face Normal Consistency (FNC ×0.01) as
primary evaluation metrics. Please refer to the supplementary material for a detailed explanation of
these metrics. Note that for ℓ2 and CD, lower is better, while for FNC, higher is better.
4.1
Comparisons
For a qualitative comparison, we visualize the vertex ℓ1 distance error maps of deformed meshes
in Figure 4 and Figure 5. As can be seen, our method has lower vertex errors in the hidden surface
regions since we use data-driven deformation priors, instead of employing hand-crafted regularizers
to enforce surface smoothness. The generalization ability to unseen deformations is improved by
7
### Page 8

Method
New motions (S1)
Unseen identities (S2)
Deformation Transfer
ℓ2 ↓
CD ↓
FNC ↑
ℓ2 ↓
CD ↓
FNC ↑
ℓ2 ↓
CD ↓
FNC ↑
ARAP [54]
5.568 2.312
95.35
9.794
2.308
94.89
5.145
3.475
91.21
ShapeFlow [25]
21.03 3.494
89.69
32.08
3.925
90.73
33.72
4.093
86.36
NFGP [69]
11.77 3.130
93.34
15.96
3.364
91.80
18.90
4.150
82.54
Ours-VDF
3.590 1.887
86.01
2.368
1.837
86.99
3.111
9.164
78.63
Ours-global
2.970 1.546
93.30
2.973
1.579
94.75
2.636
8.453
84.59
Ours-3D UNet
1.011 1.111
96.02
1.253
1.426
96.20
4.553
2.362
88.31
Ours-PointNet++.
0.886 1.055
95.47
1.231
1.364
95.37
4.898
2.564
85.87
Ours-w/o atten dec. 1.184 1.210
95.64
1.227
1.417
96.16
5.252
2.772
84.95
Ours-w/o cano.
1.018 1.063
96.40
0.969
1.258
96.62
2.660
1.934
90.96
Ours-full
0.752 0.948
96.59
0.795
1.241
96.68
2.495
1.877
91.40
Table 1: Quantitative comparisons on the S1 and S2 test sets of DeformingThing4D [30] and the
unseen identities of used in Deformation Transfer [56].
learning deformation ﬁelds for local surfaces, instead of modeling global deformations.Compared to
ARAP, ShapeFlow, and NFGP, we can produce more realistic results for complicated actions in the
3rd and 4th rows of Figure 4. The deformation results presented in Figure 5 demonstrate that our
method can generalize to unseen identities, and is also veriﬁed quantitatively in Table 1, where our
method consistently outperforms all baselines.
User-speciﬁed handles.
To evaluate the generalization performance of our approach on unseen
identities using user-provided handle displacements that are used in interactive editing applications,
we use random translations of handles applied to animals from TOSCA [47] as input. As depicted
in Figure 6, our approach is able to produce naturally-looking deformation results, and shows
its advantages compared to ARAP, ShapeFlow, and NFGP. Note that for this demonstration of
user-speciﬁed handles there exists no corresponding ground-truth.
4.2
Ablation studies
To verify our ﬁnal model choice, we conducted a series of ablation studies, where we analysed several
variants of our deformation ﬁelds (see Table 1 and Figure 7).
Volumetric grids vs continuous ﬁelds.
As continuous ﬁelds are not bound to the resolution of a
discrete grid structure, it can better represent complex deformations. The performance degrades when
we learn grid-based volumetric deformation ﬁelds. This can be seen in the experiment “Ours-VDF"
which uses a 3D U-Net [48] to generate volumetric deformation ﬁelds of a ﬁxed resolution 643.
Global vs local deformation ﬁelds.
“Ours-global" learns a global continuous ﬁeld only condi-
tioned on the global latent code. This variant tends to lose detailed information about local surface
deformations, and is more difﬁcult to generalize to new motions or identities, leading to inferior
results in comparison to our local deformation ﬁelds.
Network architectures (3D U-Net vs PointNet++ vs Point Transformer).
Compared to grid-
based and point-based local deformation descriptors learning, the point transformer-based encoder
captures strong global contexts that enforce more global consistency constraints. This provides
performance improvements on surface accuracy of deformed meshes. To verify this, we conducted
an experiment with “Ours-3D-UNet," which learns a volumetric feature map through a 3D U-Net,
and then predicts deformation ﬁelds based on queried features via tri-linear interpolation operations.
Additionally, we compare with “Ours-PointNet++," which replaces the point transformer encoder
with PointNet++ [45].
8
### Page 9

Source mesh,
handles and
target handles
ARAP [54]
ShapeFlow [25]
NFGP [69]
Ours
Figure 6: Comparison against ARAP [54], ShapeFlow [25] and NFGP [69] under the setting of
user-speciﬁed handles on TOSCA dataset [47]. Our method visibly produces the best results.
With vs without Attention-based feature querying.
The attention-based feature query mecha-
nism can ﬂexibly and effectively select the most relevant deformation descriptors for a query point,
resulting in improved performance over feature interpolation purely based on euclidean distances. A
deformation decoder that for example uses an interpolation with weights that are purely based on
euclidean distance instead (“Ours-w/o atten. dec."), leading to signiﬁcantly higher errors, particularly
in terms of the ℓ2 vertex error.
With vs without canonical poses.
Learning shape deformations via canonicalization improves the
generalization to source meshes in different poses. Learning without canonicalization ("Ours-w/o
cano."), i.e., learning shape deformations directly between two arbitrary poses, results in considerably
higher surface errors.
4.3
Intermediate results of canonicalization
In Figure 8, we visualize our intermediate results of canonicalization. As can be seen, our method
can project source meshes with arbitrary poses into a canonical space with a same pose.
4.4
Limitations
While compelling results have been demonstrated for shape manipulation, a few limitations still exist
in our approach that can be addressed in future work. Our approach only needs sparse user input in
form of handles which can be moved to create a new deformation state. While this allows for quick
editing, a possible extension is to add rotations to the handles. This could be done by leveraging a
different deformation representation such as a SE(3) ﬁeld which is composed of a displacement and a
rotation ﬁeld. Note that our displacement representation is able to represent general deformations,
but might require more user handles. Due to the limitations of the DeformingThing4D-Animals [30]
dataset in terms of available models and poses, our approach may suffer from the generalization to
out-of-distribution models and extreme poses. Additionally, the output of our model, as with other
9
### Page 10

Source Mesh 
and Handles
Target Mesh 
and Handles
Ours-VDF
Ours-global
Ours-3D UNet
Ours-PointNet++
Ours-w/o atten dec.
Ours-w/o cano.
Ours-full
Figure 7: Qualitative ablation studies. Each component of our approach contributes to the ﬁnal result
that has the lowest reconstruction error.
(a)
(b)
(c)
(a)
(b)
(c)
Figure 8: The intermediate results of our canonicalization. (a) Source mesh. (b) Canonical mesh. (c)
Our canonicalized mesh.
learning-based methods, may be affected by biases in the training dataset that can limit generalization.
We believe this issue can be relieved by a larger training dataset and a richer data augmentation
strategy in future work. Lastly, our training scheme only considers handles that are selected from a
set of candidate parts of the models, thus, limiting the regions the user can interact with. Enriching
the candidate handles during training is potentially helpful for allowing free handle placement.
5
Conclusion
In this work, we introduced Neural Shape Deformation Priors, a novel approach that learns mesh
deformations of non-rigid objects from user-provided handles based on the underlying geometric
properties of shapes. To enable shape manipulation for source meshes with different poses, we
choose to learn shape deformations via canonicalization where the source mesh is ﬁrst transformed
to the canonical space through a backward deformation ﬁeld and then deformed to the target space
through a forward deformation ﬁeld. For deformation ﬁeld learning, we propose Transformer-based
Deformation Networks (TD-Net) that represent a shape deformation as a composition of local
surface deformations. Our experiments and ablation studies demonstrate that our method can be
applied to challenging new deformations, outperforming classical optimization-based methods such
as ARAP [54] and neural networks-based methods such as ShapeFlow [25] and NFGP [69], while
showing a good generalization to previously unseen identities. We see our method as an important
step in the development of 3D modeling algorithms and softwares and hope to inspire more research
in learning-based shape manipulation.
10
### Page 11

Societal impact.
Our work provides an algorithm for natural-looking shape editing, which can
simplify tedious procedures in 3D content creation and empower artists in the movie and game
industries. It further has the potential to enrich 3D data with additional deformed shapes, and
could thus help improve the performance of other practical application techniques that rely on large
quantities of 3D ground-truth for training. Yet, misuse of our shape manipulation algorithm could
enable fraud or offensive content generation.
Acknowledgement.
This work is supported by a TUM-IAS Rudolf Mößbauer Fellowship, the ERC
Starting Grant Scan2CAD (804724), and Sony Semiconductor Solutions Corporation. We would also
like to thank Angela Dai for the video voice over.
References
[1] Alexa, M., Cohen-Or, D., Levin, D.: As-rigid-as-possible shape interpolation. In: Proceedings
of the 27th annual conference on Computer graphics and interactive techniques. pp. 157–164
(2000)
[2] Atzmon, M., Lipman, Y.: Sal: Sign agnostic learning of shapes from raw data. In: CVPR. pp.
2565–2574 (2020)
[3] Bechmann, D.: Space deformation models survey. Computers & Graphics 18(4), 571–586
(1994)
[4] Bogo, F., Romero, J., Pons-Moll, G., Black, M.J.: Dynamic faust: Registering human bodies in
motion. In: Proceedings of the IEEE conference on computer vision and pattern recognition. pp.
6233–6242 (2017)
[5] Botsch, M., Sorkine, O.: On linear variational surface deformation methods. IEEE transactions
on visualization and computer graphics 14(1), 213–230 (2007)
[6] Bozic, A., Palafox, P., Thies, J., Dai, A., Nießner, M.: Transformerfusion: Monocular rgb scene
reconstruction using transformers. Advances in Neural Information Processing Systems 34
(2021)
[7] Božiˇc, A., Palafox, P., Zollhofer, M., Thies, J., Dai, A., Nießner, M.: Neural deformation graphs
for globally-consistent non-rigid reconstruction. In: Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition. pp. 1450–1459 (2021)
[8] Burov, A., Nießner, M., Thies, J.: Dynamic surface function networks for clothed human
bodies. In: Proceedings of the IEEE/CVF International Conference on Computer Vision. pp.
10754–10764 (2021)
[9] Carion, N., Massa, F., Synnaeve, G., Usunier, N., Kirillov, A., Zagoruyko, S.: End-to-end
object detection with transformers. In: European conference on computer vision. pp. 213–229.
Springer (2020)
[10] Chabra, R., Lenssen, J.E., Ilg, E., Schmidt, T., Straub, J., Lovegrove, S., Newcombe, R.: Deep
local shapes: Learning local sdf priors for detailed 3d reconstruction. In: ECCV. pp. 608–625.
Springer (2020)
[11] Chen, X., Zheng, Y., Black, M.J., Hilliges, O., Geiger, A.: Snarf: Differentiable forward
skinning for animating non-rigid neural implicit shapes. In: Proceedings of the IEEE/CVF
International Conference on Computer Vision. pp. 11594–11604 (2021)
[12] Chen, Y., Tu, Z., Kang, D., Bao, L., Zhang, Y., Zhe, X., Chen, R., Yuan, J.: Model-based 3d
hand reconstruction via self-supervised learning. In: Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition. pp. 10451–10460 (2021)
[13] Chen, Z., Zhang, H.: Learning implicit ﬁelds for generative shape modeling. In: CVPR (2019)
[14] Chibane, J., Alldieck, T., Pons-Moll, G.: Implicit functions in feature space for 3d shape
reconstruction and completion. In: CVPR (2020)
11
### Page 12

[15] Deng, Y., Yang, J., Tong, X.: Deformed implicit ﬁeld: Modeling 3d shapes with learned dense
correspondence. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern
Recognition. pp. 10286–10296 (2021)
[16] Dosovitskiy, A., Beyer, L., Kolesnikov, A., Weissenborn, D., Zhai, X., Unterthiner, T., Dehghani,
M., Minderer, M., Heigold, G., Gelly, S., et al.: An image is worth 16x16 words: Transformers
for image recognition at scale. arXiv preprint arXiv:2010.11929 (2020)
[17] Giebenhain, S., Goldlücke, B.: Air-nets: An attention-based framework for locally conditioned
implicit representations. In: 2021 International Conference on 3D Vision (3DV). pp. 1054–1064.
IEEE (2021)
[18] Gropp, A., Yariv, L., Haim, N., Atzmon, M., Lipman, Y.: Implicit geometric regularization for
learning shapes. ICML (2020)
[19] Han, K., Wang, Y., Chen, H., Chen, X., Guo, J., Liu, Z., Tang, Y., Xiao, A., Xu, C., Xu, Y.,
et al.: A survey on visual transformer. arXiv e-prints pp. arXiv–2012 (2020)
[20] Hao, Z., Averbuch-Elor, H., Snavely, N., Belongie, S.: Dualsdf: Semantic shape manipulation
using a two-level representation. In: Proceedings of the IEEE/CVF Conference on Computer
Vision and Pattern Recognition. pp. 7631–7641 (2020)
[21] Hui, K.H., Li, R., Hu, J., Fu, C.W.: Neural template: Topology-aware reconstruction and
disentangled generation of 3d meshes. In: Proceedings of the IEEE/CVF Conference on
Computer Vision and Pattern Recognition. pp. 18572–18582 (2022)
[22] Ioffe, S., Szegedy, C.: Batch normalization: Accelerating deep network training by reducing
internal covariate shift. In: International conference on machine learning. pp. 448–456. PMLR
(2015)
[23] Jacobson, A., Baran, I., Popovic, J., Sorkine, O.: Bounded biharmonic weights for real-time
deformation. ACM Trans. Graph. 30(4), 78 (2011)
[24] Jakab, T., Tucker, R., Makadia, A., Wu, J., Snavely, N., Kanazawa, A.: Keypointdeformer:
Unsupervised 3d keypoint discovery for shape control. In: Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition. pp. 12783–12792 (2021)
[25] Jiang, C., Huang, J., Tagliasacchi, A., Guibas, L.J.: Shapeﬂow: Learnable deformation ﬂows
among 3d shapes. Advances in Neural Information Processing Systems 33, 9745–9757 (2020)
[26] Jiang, C., Sud, A., Makadia, A., Huang, J., Nießner, M., Funkhouser, T., et al.: Local implicit
grid representations for 3d scenes. In: CVPR. pp. 608–625 (2020)
[27] Kazhdan, M., Hoppe, H.: Screened poisson surface reconstruction. ACM Transactions on
Graphics (ToG) 32(3), 1–13 (2013)
[28] Kingma, D.P., Ba, J.:
Adam:
A method for stochastic optimization. arXiv preprint
arXiv:1412.6980 (2014)
[29] Levi, Z., Gotsman, C.: Smooth rotation enhanced as-rigid-as-possible mesh animation. IEEE
transactions on visualization and computer graphics 21(2), 264–277 (2014)
[30] Li, Y., Takehara, H., Taketomi, T., Zheng, B., Nießner, M.: 4dcomplete: Non-rigid motion
estimation beyond the observable surface. In: Proceedings of the IEEE/CVF International
Conference on Computer Vision. pp. 12706–12716 (2021)
[31] Lipman, Y., Sorkine, O., Cohen-Or, D., Levin, D., Rossi, C., Seidel, H.P.: Differential coor-
dinates for interactive mesh editing. In: Proceedings Shape Modeling Applications, 2004. pp.
181–190. IEEE (2004)
[32] Loper, M., Mahmood, N., Romero, J., Pons-Moll, G., Black, M.J.: SMPL: A skinned multi-
person linear model. ACM Trans. Graphics (Proc. SIGGRAPH Asia) 34(6), 248:1–248:16 (Oct
2015)
12
### Page 13

[33] Mescheder, L., Oechsle, M., Niemeyer, M., Nowozin, S., Geiger, A.: Occupancy networks:
Learning 3d reconstruction in function space. In: CVPR (2019)
[34] Mi, Z., Luo, Y., Tao, W.: Ssrnet: Scalable 3d surface reconstruction network. In: Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 970–979 (2020)
[35] Mihajlovic, M., Zhang, Y., Black, M.J., Tang, S.: Leap: Learning articulated occupancy
of people. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern
Recognition. pp. 10461–10471 (2021)
[36] Mildenhall, B., Srinivasan, P.P., Tancik, M., Barron, J.T., Ramamoorthi, R., Ng, R.: Nerf:
Representing scenes as neural radiance ﬁelds for view synthesis. In: European conference on
computer vision. pp. 405–421. Springer (2020)
[37] Milliron, T., Jensen, R.J., Barzel, R., Finkelstein, A.: A framework for geometric warps and
deformations. ACM Transactions on Graphics (TOG) 21(1), 20–51 (2002)
[38] Nair, V., Hinton, G.E.: Rectiﬁed linear units improve restricted boltzmann machines. In: ICML
(2010)
[39] Niemeyer, M., Mescheder, L., Oechsle, M., Geiger, A.: Occupancy ﬂow: 4d reconstruction
by learning particle dynamics. In: Proceedings of the IEEE/CVF international conference on
computer vision. pp. 5379–5389 (2019)
[40] Osman, A.A.A., Bolkart, T., Black, M.J.: STAR: A sparse trained articulated human body
regressor. European Conference on Computer Vision (ECCV) pp. 598–613 (2020), https:
//star.is.tue.mpg.de
[41] Palafox, P., Božiˇc, A., Thies, J., Nießner, M., Dai, A.: Npms: Neural parametric models for 3d
deformable shapes. In: Proceedings of the IEEE/CVF International Conference on Computer
Vision. pp. 12695–12705 (2021)
[42] Park, J.J., Florence, P., Straub, J., Newcombe, R., Lovegrove, S.: Deepsdf: Learning continuous
signed distance functions for shape representation. In: CVPR (2019)
[43] Paszke, A., Gross, S., Massa, F., Lerer, A., Bradbury, J., Chanan, G., Killeen, T., Lin, Z.,
Gimelshein, N., Antiga, L., et al.: Pytorch: An imperative style, high-performance deep learning
library. Advances in neural information processing systems 32 (2019)
[44] Peng, S., Niemeyer, M., Mescheder, L., Pollefeys, M., Geiger, A.: Convolutional occupancy
networks. In: ECCV (2020)
[45] Qi, C.R., Yi, L., Su, H., Guibas, L.J.: Pointnet++: Deep hierarchical feature learning on point
sets in a metric space. Advances in neural information processing systems 30 (2017)
[46] Rao, Y., Nie, Y., Dai, A.: Patchcomplete: Learning multi-resolution patch priors for 3d shape
completion on unseen categories. Advances in Neural Information Processing Systems (2022)
[47] Rodolà, E., Cosmo, L., Bronstein, M.M., Torsello, A., Cremers, D.: Partial functional corre-
spondence. In: Computer graphics forum. vol. 36, pp. 222–236. Wiley Online Library (2017)
[48] Ronneberger, O., Fischer, P., Brox, T.: U-net: Convolutional networks for biomedical image
segmentation. In: International Conference on Medical image computing and computer-assisted
intervention. pp. 234–241. Springer (2015)
[49] Rüegg, N., Zufﬁ, S., Schindler, K., Black, M.J.: Barc: Learning to regress 3d dog shape from
images by exploiting breed information. In: Proceedings of the IEEE/CVF Conference on
Computer Vision and Pattern Recognition. pp. 3876–3884 (2022)
[50] Saito, S., Yang, J., Ma, Q., Black, M.J.: Scanimate: Weakly supervised learning of skinned
clothed avatar networks. In: Proceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition. pp. 2886–2897 (2021)
13
### Page 14

[51] Sederberg, T.W., Parry, S.R.: Free-form deformation of solid geometric models. In: Proceedings
of the 13th annual conference on Computer graphics and interactive techniques. pp. 151–160
(1986)
[52] Shechter, M., Hanocka, R., Metzer, G., Giryes, R., Cohen-Or, D.: Neuralmls: Geometry-aware
control point deformation (2022)
[53] Sorkine, O.: Differential representations for mesh processing. In: Computer Graphics Forum.
vol. 25, pp. 789–807. Wiley Online Library (2006)
[54] Sorkine, O., Alexa, M.: As-rigid-as-possible surface modeling. In: Symposium on Geometry
processing. vol. 4, pp. 109–116 (2007)
[55] Sorkine, O., Cohen-Or, D., Lipman, Y., Alexa, M., Rössl, C., Seidel, H.P.: Laplacian surface
editing. In: Proceedings of the 2004 Eurographics/ACM SIGGRAPH symposium on Geometry
processing. pp. 175–184 (2004)
[56] Sumner, R.W., Popovi´c, J.: Deformation transfer for triangle meshes. ACM Transactions on
graphics (TOG) 23(3), 399–405 (2004)
[57] Sumner, R.W., Schmid, J., Pauly, M.: Embedded deformation for shape manipulation. In: ACM
SIGGRAPH 2007 papers, pp. 80–es (2007)
[58] Tang, J., Han, X., Pan, J., Jia, K., Tong, X.: A skeleton-bridged deep learning approach for
generating meshes of complex topologies from single rgb images. In: Proceedings of the ieee/cvf
conference on computer vision and pattern recognition. pp. 4541–4550 (2019)
[59] Tang, J., Han, X., Tan, M., Tong, X., Jia, K.: Skeletonnet: A topology-preserving solution for
learning mesh reconstruction of object surfaces from rgb images. IEEE transactions on pattern
analysis and machine intelligence (2021)
[60] Tang, J., Lei, J., Xu, D., Ma, F., Jia, K., Zhang, L.: Sa-convonet: Sign-agnostic optimization of
convolutional occupancy networks. In: Proceedings of the IEEE/CVF International Conference
on Computer Vision. pp. 6504–6513 (2021)
[61] Tang, J., Xu, D., Jia, K., Zhang, L.: Learning parallel dense correspondence from spatio-
temporal descriptors for efﬁcient and robust 4d reconstruction. In: CVPR. pp. 6022–6031
(2021)
[62] Terzopoulos, D., Platt, J., Barr, A., Fleischer, K.: Elastically deformable models. In: Proceedings
of the 14th annual conference on Computer graphics and interactive techniques. pp. 205–214
(1987)
[63] Tretschk, E., Tewari, A., Golyanik, V., Zollhöfer, M., Stoll, C., Theobalt, C.: Patchnets: Patch-
based generalizable deep implicit 3d shape representations. In: ECCV. pp. 108–124. Springer
(2020)
[64] Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, Ł.,
Polosukhin, I.: Attention is all you need. Advances in neural information processing systems 30
(2017)
[65] Wang, S., Geiger, A., Tang, S.: Locally aware piecewise transformation ﬁelds for 3d human
mesh registration. In: Proceedings of the IEEE/CVF Conference on Computer Vision and
Pattern Recognition. pp. 7639–7648 (2021)
[66] Wang, S., Mihajlovic, M., Ma, Q., Geiger, A., Tang, S.: Metaavatar: Learning animatable
clothed human models from few depth images. Advances in Neural Information Processing
Systems 34 (2021)
[67] Wang, X., Girshick, R., Gupta, A., He, K.: Non-local neural networks. In: Proceedings of the
IEEE conference on computer vision and pattern recognition. pp. 7794–7803 (2018)
[68] Xu, Q., Wang, W., Ceylan, D., Mech, R., Neumann, U.: Disn: Deep implicit surface network
for high-quality single-view 3d reconstruction. In: NeurIPS (2019)
14
### Page 15

[69] Yang, G., Belongie, S., Hariharan, B., Koltun, V.: Geometry processing with neural ﬁelds.
Advances in Neural Information Processing Systems 34 (2021)
[70] Yu, H., Li, F., Saleh, M., Busam, B., Ilic, S.: Coﬁnet: Reliable coarse-to-ﬁne correspondences
for robust pointcloud registration. Advances in Neural Information Processing Systems 34
(2021)
[71] Zhang, B., Nießner, M., Wonka, P.: 3DILG: Irregular latent grids for 3d generative modeling.
In: Advances in Neural Information Processing Systems (2022)
[72] Zhang, B., Wonka, P.: Training data generating networks: Shape reconstruction via bi-level
optimization. In: International Conference on Learning Representations (2021)
[73] Zhao, H., Jia, J., Koltun, V.: Exploring self-attention for image recognition. In: Proceedings
of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 10076–10085
(2020)
[74] Zhao, H., Jiang, L., Jia, J., Torr, P.H., Koltun, V.: Point transformer. In: Proceedings of the
IEEE/CVF International Conference on Computer Vision. pp. 16259–16268 (2021)
[75] Zheng, S., Lu, J., Zhao, H., Zhu, X., Luo, Z., Wang, Y., Fu, Y., Feng, J., Xiang, T., Torr,
P.H., et al.: Rethinking semantic segmentation from a sequence-to-sequence perspective with
transformers. In: Proceedings of the IEEE/CVF conference on computer vision and pattern
recognition. pp. 6881–6890 (2021)
[76] Zheng, Z., Yu, T., Dai, Q., Liu, Y.: Deep implicit templates for 3d shape representation. In:
Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp.
1429–1439 (2021)
[77] Zhou, K., Huang, J., Snyder, J., Liu, X., Bao, H., Guo, B., Shum, H.Y.: Large mesh deformation
using the volumetric graph laplacian. In: ACM SIGGRAPH 2005 Papers, pp. 496–503 (2005)
15
### Page 16

Neural Shape Deformation Priors
– Supplementary Material –
Our Neural Shape Deformation Priors method is based on transformer-based deformation networks
that represent the deformation as a composition of local surface deformations. The underlying
architectures are discussed in Appendix A. The used evaluation metrics are detailed in Appendix B.
Our notations are further explained in Appendix C. And more details about data-preprocessing are
given in Appendix D. In addition to the results shown in the main paper, we conducted further
experiments (see E). While our method exhibits good generalization to unseen poses and shapes, we
discuss and show failure cases in Appendix F.
A
Network Architectures
Vector Cross Attention:
In Figure 9, we illustrate the architecture of vector cross attention [73]
(VCA) which is a building block of our transformer-based deformation network (see Figure 3 in the
main paper). The feature vectors gi and fi are transformed with three linear projectors ϕ(gi), ψ(fi)
and α(fi), each of which is a fully-connected layer. To leverage relatively positional information
of fi and gi, xi −yi is encoded by a positional embedding module [64, 36] δ := θ(xi −yj) that
consists of two linear layers with a single ReLU [38]. Then, the summation result of δ(xi −yj) and
ϕ(gj) −ψ(fi) will be further processed by a MLP γ. Next, a softmax function ρ is used to generate
normalized attention scores that are used to calculate a weighted combination of α(fi) + δ(xi) to
obtain f ′
i.
: FC-256
: MLP-256
: FC-256
: MLP-256
: Softmax
: FC-256
VSA
BN
FPS
VCA
VSA
PTB
PAB
BN
VCA
Figure 9: Vector Cross Attention (VCA), Point Transformer Block (PTB), and Point Abstrac-
tion Block (PAB).
Point Transformer Block (PTB):
As illutrated in Figure 9, we introduce the architecture of point
transformer block. The point transformer block is used to encapsulate the information from kenc = 16
nearest neighborhoods while keeping the position of a point Xi unchanged. The input Xi is fed into a
vector attention block (VSA) and through a BatchNorm (BN) [22] (including a residual connection
from the input Xi).
Point Abstraction Block (PAB):
The point abstraction block consists of a farthest point sampling
module (FPS), a VCA module, a VSA module, followed by a BN layer. The farthest point sampling
(FPS) is used to downsampled X which is then fed into a VCA followed by a VSA module. We
employ a skip connection from the original X to the VCA module. The output of the FPS and the
VSA module are fed into a batchnorm layer which computes the output of the point abstraction block.
16
### Page 17

Downsampling
PTB
PAB
BN
FC−256
FC −256
for 𝑖𝑖= 1, 2
Full attention block
BN
FC −256
FC −256
for 𝑖𝑖= 1, …, 4
fullPTB
Maxpool
MLP
Figure 10: Point Transformer Encoder.
VCA
…
FC-128
FC-128
FC-128
FC-128
FC-3
for 𝑖𝑖= 1, …, 5 
128
128
128
128
3
3
256
256
Figure 11: Attentive Deformation Decoder.
Point Transformer Encoder
As shown in Figure 10, a PTB is used to obtain an initial feature
encoding Z0 = {c0
i , z0
i }n0
i=1, n0 = 5000. Two consecutive point abstraction blocks (PABs) with
intermediate set size of n1 = 500 and n2 = 100, are used to obtain downsampled feature point clouds
Z1 = {c1
i , z1
i }n1
i=1 and Z2 = {c2
i , z2
i }n2
i=1. To enhance global deformation priors, we stack 4 point
transformer block with full self-attention whose kenc is set to 100 to exchange the global information
in the whole set of Z2. By doing so, we can obtain a sparse set of local deformation descriptors
Z = {ci, zi}100
i=1 that are anchored in {ci}. Finally, a global max-pooling operation followed by two
linear layers is used to obtain the global latent vector zglo.
Attentive Deformation Decoder
The detailed architecture of attentive deformation decoder is
shown in Figure 11. It fuses near-by local latent codes Zq of q under the guidance of a global latent
code zglo into z, and feeds z into an MLP consisting of ﬁve stacked Res-FC blocks to estimate the
displacement vector of q.
B
Evaluation Metrics
For deﬁning the evaluation metrics, we assume two meshes T = {V, F} and T ′ = {V′, F} being
the ground-truth and deformed mesh respectively, sharing the same connectivity.
Vertex ℓ2 error:
The vertex ℓ2 distance error is the mean square distance between ground-truth
vertices V = {vi} and deformed vertices V′ = {v′
i}:
ℓ2(T ′, T ) := 1
|V|
|V|
X
i=1
∥vi −v′
i∥2
2,
where |V| denotes the number of mesh vertices.
Chamfer distance:
To calculate the chamfer distance between T ′ and T , we ﬁrstly sample two
point set PT ′ and PT from T ′ and T individually. Then, the Chamfer distance of two point sets is
17
### Page 18

deﬁned as:
CD(T ′, T ) := CD(PT ′, PT ) =
X
x∈PT ′
min
y∈PT ∥x −y∥2
2 +
X
y∈PT
min
x∈PT ′ ∥x −y∥2
2.
Face Normal Consistency
The face normal consistency describes the mean cosine similarity score
of the triangle normals of two meshes. Let N and N ′ denote the set of face normals of T and T ′
respectively. We deﬁne Face Normal Consistency as:
FNC(T ′, T ) :=
1
|N|
|N |
X
i=1
|n′ · n|,
where |N| = |F| denotes the number of triangle faces and · denotes the dot product of two vectors.
C
Notation
We will explain our notation in more detail after having brieﬂy deﬁned it in Section 3. By S, C,
T , T ′ we denote meshes of the considered shapes. S = {V, F} is the source mesh and V is the
set of vertices of S while F is the set of faces of S. S is deformed in a 2-step approach. By C we
denote the canonical shape and T is the target shape. We select a sparse set of handles H = {hi}ℓ
i=1
of the original shape. The handles can be dragged to new target locations O = {oi}ℓ
i=1 which
deﬁne the target mesh T . The continuous deformation ﬁeld learnt in our work is denoted by D.
We apply D to deform the vertices of S to obtain the deformed mesh T ′ = {V + D(V), F} where
V + D(V) are the vertices of the deformed mesh. We denote the backward deformation ﬁeld by Db
and the forward deformation ﬁeld by Df. It holds Df(Db(·)). Since our method performs operations
in the point cloud domain, we sample point clouds from the surface meshes. PS = {pi}n
i=0 is a
surface point cloud of canonical mesh S with size n = 5000. We deﬁne the binary user handle
mask as M = {bi | bi = 1 if pi is a handle or bi = 0 else, i = 1, . . . , n}. The point cloud PS is
passed through the backward transformation network Ωb and mapped into the canonical pose P′
C, i.e.
P′
C = PS + Db(PS). Then the point cloud P′
C is passed through the forward transformation network
Ωf and mapped into the target pose P′
T , i.e. P′
T = P′
C + Df(P′
C). Further, consult Table 2 for the
deﬁnition of all items.
D
Data
To train and evaluate our method, we use the DeformingThing4D [30] dataset, which is available
under a non-commercial academic license. It does not contain personally identiﬁable information or
offensive contents. We have obtained the consent to use the dataset.
Train/test split
The DeformingThing4D consists of a large number of quadruped animal animations
with various motions, such as “bear3EP Jump”, “bear9AK Jump”, or “bear3EP Lie” where "bear3EP"
and "bear9AK" are identity names, and "Jump" and "Lie" are motion names. Similar to the D-
FAUST [4] used in OFlow [39], the train/test split is based on these identity and motion names of
deforming sequences. We ﬁrstly divide the animations of the dataset into two parts, seen identities
and unseen identities. For the animations of seen identities, we further divide it into seen motions of
seen identities (used as training set), and unseen motions of seen identities (used as the test set of S1).
The animations of unseen identities are used as the test set of S2. Finally, the train, test S1, and test
S2 datasets individually contains 1296, 143, and 55 deforming sequences.
Data preparation
In Section 3.3 of the main text, we mentioned that our method utilizes a set of
triplets including source S, canonical C, and target mesh T with dense correspondence for training.
The point clouds PS, PC, PT of size n with one-to-one correspondence are sampled from the surfaces
of S, C, T . And the non-surface point sets QS, QC, QT of size m are sampled from their 3D space.
Here, we provide the details of data preparation. Firstly, we sample Np surface points {xi}i=Np
i=1
from the canonical mesh C; we also store the corresponding barycentric weights of sample points.
Then, each point is randomly permuted by a small displacement vector δni = xi + β ∗ni along the
normal direction ni of the corresponding triangle. The displacement distance β is from a Gaussian
18
### Page 19

Notations
Meaning
S, C, T , T ′
Source mesh, canonical mesh, target mesh, deformed mesh
V, F
Vertices, faces of source mesh S
H, hi
Set of handles, i-th handle location
O, oi
Set of target locations of handles, i-th target location
M, bi
Binary user handle mask, i-th element of M
PS, PC, PT
Surface point clouds of size n sampled from the surface of S, C, T
PO
Target handle point locations
QS, QC, QT
Non-surface point clouds of size m sampled from the 3D space of S, C, T
qi
i-th non-surface querying point
n
Size of surface point clouds PS, PC, PT
m
Size of non-surface point clouds QS, QC, QT
pi
i-th point from PS
P′
C, P′
T
Mapping of PS in canonical pose, target pose
Db, Df
Backward deformation ﬁeld, forward deformation ﬁeld
D
Deformation ﬁeld between two arbitrary poses, i.e. Df(Db(·))
Ωb, Ωf
Backward transformation network, forward transformation network
X, Y
Query sequence, key-value sequence
xi, fi, f ′
i
Coordinate of i-th query point, corresponding feature vector, aggregated feature
yj, gj
Coordinate of j-th key-value point, corresponding feature vector
VCA
Vector cross attention
ϕ, ψ, α
Fully-connected layers
γ
Attention weight normalization function, e.g. softmax function
δ
Positional embedding module
VSA
Vector self-attention operator
PTB, PAB
Point transformer block, point abstraction block
BN
BatchNorm Layer
Z
Set of local deformation descriptors
q, zq
A point in C, corresponding feature vector
ci, zi
Coordinates and feature vector of i-th deformation descriptor
zglo
Global latent vector
Lb, Lf, Ltotal
Backward loss function, forward loss function, end-to-end loss function
Table 2: Notations in order of appearance in the main paper.
distribution N(0, σ2). Next, for source S and target T meshes, we use the same barycentric weights
to obtain PS, PT with correspondences, and use the same displacements δn to obtain QS, QT with
correspondences. Concretely, we pre-compute Np = 20,000 points from each canonical surface
mesh, and get the non-surface points with 50% of surface points permuted by σ = 0.02, with 50%
of surface points permuted by σ = 0.1. During training, we down-sample n = 5000 points of
PS, PC, PT , and down-sample m = 5000 of QS, QC, QT . To maintain one-to-one correspondence,
we use the same sampling indices for S, C, T .
E
Additional Results
Effects of point cloud sampling density
To study the effect of sampling density of input point
cloud, we individually train our model by using point clouds of size 2500, 5000, 7500 as input.
Quantitative results are shown in Table 3. We can observe that the results of different evaluation
metrics only show a slightly small variance. To balance accuracy and computational cost, we use
5000 points in our ﬁnal model.
Robustness to noisy source mesh
To analyze the robustness of noise effects, we individually train
our model by adding gaussian noise permutations to the source meshes. The standard deviation of
gaussian noise is set to 0, 0.0025 or 0.005. The comparison in Table 4 shows that with the noise
becoming larger, the performance of our method experiences only slight variation; however, this
demonstrates the robustness of our method to noisy source meshes.
19
### Page 20

#sampling points
New motions (S1)
Unseen identities (S2)
ℓ2 ↓
CD ↓
FNC ↑
ℓ2 ↓
CD ↓
FNC ↑
Ours-2500
0.789
1.008
96.27
0.905
1.285
96.57
Ours-5000
0.752
0.948
96.59
0.795
1.241
96.68
Ours-7500
0.732
0.944
96.39
0.789
1.251
96.66
Table 3: Quantitative results of different input point cloud density on the S1 and S2 test sets of
DeformingThing4D [30] dataset.
#standard deviation
New motions (S1)
Unseen identities (S2)
ℓ2 ↓
CD ↓
FNC ↑
ℓ2 ↓
CD ↓
FNC ↑
Ours-0
0.752
0.948
96.59
0.795
1.241
96.68
Ours-0.0025
0.774
0.973
95.90
0.808
1.278
96.65
Ours-0.0050
0.851
1.017
96.50
0.911
1.392
96.16
Table 4: Quantitative results of source meshes with different noise intensities on the S1 and S2 test
sets of DeformingThing4D [30] dataset.
Robustness to partial source mesh
To investigate the robustness to incomplete source meshes,
we randomly sample 5 seeds from the source mesh surface, and then remove the corresponding kr
nearest vertices and corresponding faces. The kr is calculated by kr = pr ∗|V|, where pr is the
incompleteness ratio and |V| is the number of source mesh vertices. Again, our model is directly
evaluated under two different settings of pr = 0.05 and pr = 0.1. The quantitative results are
provided in Table 5. As seen, there are not signiﬁcant numerical variations between different
incompleteness ratios. This clearly demonstrates the robustness of our approach to incomplete source
meshes.
#incompleteness ratio
New motions (S1)
Unseen identities (S2)
ℓ2 ↓
CD ↓
FNC ↑
ℓ2 ↓
CD ↓
FNC ↑
Ours-0.0
0.752
0.948
96.59
0.795
1.241
96.68
Ours-0.05
0.770
0.957
95.80
0.804
1.244
96.66
Ours-0.10
0.823
1.002
96.44
0.858
1.261
96.55
Table 5: Quantitative results of source meshes with different incomplete ratios on the S1 and S2 test
sets of DeformingThing4D [30] dataset. Note that our model is directly evaluated on partial meshes
without ﬁne-tuning.
Evaluations on real animals scans.
We evaluate our pre-trained model on the real animal scans
captured by ourselves. As show in Figure 12, our method can still learn realistic shape deformations,
which demonstrates the generalization ability of our approach to real captured models.
Evaluations on reconstructed animals from real images.
In addtion, we evaluate our pre-trained
model on the reconstructed animals from real RGB images using the BARC [49] method. As shown
in Figure 13, our method estimates realistic deformations for reconstructed animals from natural
images. This also demonstrates the generalization ability of our method.
Evaluations on non-realistic user-speciﬁed handles.
While our goal of data-driven deformation
priors is to obtain deformations that are as realistic as possible, we also evaluate our method on
non-realistic or non-physical-aware handles. As shown in Figure 14, our method will try to ﬁnd the
20
### Page 21

(a)
(b)
(c)
(a)
(b)
(c)
Figure 12: Evaluation on real animal scans. (a) Real animal scans (b) Source meshes obtained via
the Screened PSR [27] and handles. (c) Ours.
(a)
(b)
(c)
(d)
(e)
Figure 13:
Evaluation on reconstructed animals from real RGB images using the method of
BARC [49] (a) Real images. (b) Reconstructed source meshes and handles. (c) Ours. (d) Re-
constructed source meshes and handles. (e) Ours.
closest deformation of animals that can best explain the provided handle displacements. However,
our method could be easily trained on non-realistic or non-physical-aware samples and learn the
respective deformation behavior.
(a)
(b)
(a)
(b)
(a)
(b)
Figure 14: Evaluation on non-realistic user-speciﬁed handles. (a) Source meshes and handles. (b)
Ours.
Without dense correspondence
While our current method uses an existing dataset where dense
correspondences between temporal mesh frames are available, our framework can also be trained
on datasets without dense correspondences through some adjustments on inputs and loss functions.
Concretely, we change our method to receive sparse handle correspondences as inputs, and utilize
Chamfer distance as the loss function that does not require ground-truth meshes with dense cor-
respondences as supervision. In Figure 15, we visualize several test results of such a modiﬁed
framework. As seen, without dense correspondences for training, our method can still obtain accurate
deformations.
21
### Page 22

(a)
(b)
(c)
(a)
(b)
(c)
Figure 15: The evaluation results of our modiﬁed framework that uses sparse handles as input and
does not require dense correspondences as supervision. (a) Source meshes and handles. (b) Target
meshes and handles. (c) Our results with vertex error map.
Video animations
To visualize the deformation behaviours of the different approaches, we use a
sequence of handle movements as inputs, and run our model frame by frame to obtain a deformation
motion sequence. We refer to the supplemental video for an animated sequence.
F
Limitations
(a)
(b)
(c)
(a)
(b)
(c)
Figure 16: The failure cases. (a) Source meshes and handles. (b) Target meshes and handles. (c) Our
results with vertex error map.
While compelling results have been demonstrated for shape manipulation, a few limitations still exist
in our approach that can be addressed in future work. Two representative failure cases are depicted
in Figure 16. We can see that our method cannot well address extreme shape deformations (e.g. left
of Figure 16) or manipulate unseen identities that are far from the training data distribution (e.g. the
elephant in the right of Figure 16). We believe this issue can be alleviated by a larger training dataset,
a richer data augmentation strategy, and/or few shot generalization techniques in the future.
22