# MapTracker: Tracking with Strided Memory Fusion for Consistent Vector HD Mapping

**Source**: arXiv:2403.15951

**Type**: Academic Paper

---

## Page 1

MapTracker: Tracking with Strided Memory
Fusion for Consistent Vector HD Mapping
Jiacheng Chen1∗, Yuefan Wu1∗, Jiaqi Tan1∗, Hang Ma1, and
Yasutaka Furukawa1,2
1Simon Fraser University
2Wayve
Abstract. This paper presents a vector HD-mapping algorithm that
formulates the mapping as a tracking task and uses a history of mem-
ory latents to ensure consistent reconstructions over time. Our method,
MapTracker, accumulates a sensor stream into memory buffers of two la-
tent representations: 1) Raster latents in the bird’s-eye-view (BEV) space
and 2) Vector latents over the road elements (i.e., pedestrian-crossings,
lane-dividers, and road-boundaries). The approach borrows the query
propagation paradigm from the tracking literature that explicitly asso-
ciates tracked road elements from the previous frame to the current,
while fusing a subset of memory latents selected with distance strides
to further enhance temporal consistency. A vector latent is decoded to
reconstruct the geometry of a road element. The paper further makes
benchmark contributions by 1) Improving processing code for existing
datasets to produce consistent ground truth with temporal alignments
and 2) Augmenting existing mAP metrics with consistency checks. Map-
Tracker significantly outperforms existing methods on both nuScenes and
Agroverse2 datasets by over 8% and 19% on the conventional and the
new consistency-aware metrics, respectively. The code and models are
available on our project page: https://map-tracker.github.io.
1
Introduction
Humans forget, so do neural networks. A robust memory is crucial for online
systems to produce consistent outputs. Vector HD mapping, a task of recon-
structing vector road geometries from vehicle sensor data, has made dramatic
progress. A consistent vector HD mapping system, capable of reconstructing a
consistent HD map of a city from a single drive-through (See Figure 1 for ex-
amples), would have a tremendous impact on our society, reducing the cost of
HD map creation for tens of thousands of cities in the world and enhancing the
safety and stability of self-driving cars.
Existing vector HD mapping methods [16, 18, 19, 24, 41] focus on per-frame
reconstruction via detection-style transformer networks [4]. They detect road el-
ements anew in every frame without consistency enforcement, potentially guided
by reconstructions from the previous frame. Furthermore, a standard recurrent
*Equal contribution.
arXiv:2403.15951v2  [cs.CV]  12 Oct 2024


## Page 2

2
Chen et al.
MapTRv2
MapTracker (Ours)
StreamMapNet
Fig. 1: MapTracker produces high-quality and temporally consistent vector HD maps,
which are progressively merged into a global vector HD map by a simple online algo-
rithm. The current state-of-the-art methods, MapTRv2 [19] and StreamMapNet [41],
fail to produce consistent reconstructions, leading to very noisy global maps. The figure
shows two challenging scenarios (cars are turning) from the nuScenes [2] dataset.
latent embedding is often the choice for memory mechanism [41], where accumu-
lating the entire history in a single latent memory proves challenging, especially
for cluttered environments with numerous vehicles obscuring road structures.
Towards ultimate temporal consistency, this paper presents MapTracker with
two key design elements. First, tracking instead of detection becomes the formu-
lation, specifically borrowing the query propagation paradigm from the tracking
literature that explicitly associates tracked road elements across frames. Second,
a sequence of memory latents from past frames serves as the memory mecha-
nism. Concretely, we retain memory buffers for two latent representations from
the past frames: 1) Raster latents in the bird’s-eye-view (BEV) space and 2)
Vector latents over the tracked road elements, while using a subset of memory
latents based on distance strides for effective information fusion. A vector latent
reconstructs a road element geometry.
To prepare the tracking labels and measure the consistency of HD map re-
constructions, this paper introduces a new benchmark based on nuScenes [2]
and Agroverse2 [37] datasets. Specifically, we improve the processing code of the
two datasets to produce consistent ground truth data with temporal alignments,
then propose a consistency-aware mean average precision (mAP) metric.
We have made extensive comparative evaluations based on the traditional
and the new mAP metrics. MapTracker significantly outperforms the competing
methods by over 8% on the conventional distance-based mAP, reaching 76.1
mAP on nuScenes and 76.9 mAP on Argoverse2. With the new consistency-aware
metrics, MapTracker demonstrates superior temporal consistency and improves
the StreamMapNet baseline by over 19%.


## Page 3

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
3
To summarize, this paper makes three contributions: 1) A novel vector HD
mapping algorithm that formulates HD mapping as tracking and leverages the
history of memory latents in two representations to achieve temporal consis-
tency; 2) An improved vector HD mapping benchmark with temporally consis-
tent ground truth and a consistency-aware mAP metric; and 3) SOTA perfor-
mance with significant improvements over the current best methods on tradi-
tional and new metrics. The code and the new benchmark data will be available.
2
Related Work
This paper tackles consistent vector HD mapping by 1) borrowing an idea from
the visual object tracking literature and 2) devising a new memory mechanism.
The section first reviews recent trends in visual object tracking with transform-
ers and memory designs in vision-based autonomous driving. Lastly, we discuss
competing vector HD mapping methods.
Visual object tracking with transformers. Visual object tracking [40] has a
long history, where end-to-end transformer [35] methods become a recent trend
due to the simplicity. TrackFormer [27], TransTrack [34], and MOTR [42, 45]
leverage the attention mechanism with track queries to explicitly associate in-
stances across frames. MeMOT [3] and MeMOTR [8] further extend the tracking
transformers with memory mechanisms for better long-term consistency. This
paper formulates vector HD mapping as a tracking task by incorporating track
queries with a more robust memory mechanism.
Memory designs in autonomous driving. Single-frame self-driving sys-
tems have difficulty in handling occlusion, sensor failure, or complex environ-
ments. Temporal modeling with memories offers promising complements [9,10,
12, 13, 22, 23, 36, 39, 41]. Many memory designs exist for the raster BEV fea-
tures [17,29], which form the foundation of most autonomous-driving tasks [15,
26]. BEVDet4D [12] and BEVFormerv2 [39] stack features of multiple past
frames as a memory, but the computation scales linearly with history length,
struggling to capture long-term information. VideoBEV [10] propagates BEV
raster queries across frames to accumulate information recurrently. In the vec-
tor domain, Sparse4Dv2 [22] employs a similar RNN-style memory for object
queries, while Sparse4Dv3 [23] further uses temporal denoising for robust tem-
poral learning. These ideas have been partially incorporated by vector HD map-
ping approaches [36,41]. This paper proposes a new memory design for both the
raster BEV latents and the vector latents of road elements.
Vector HD mapping. Traditionally HD maps are reconstructed offline with
SLAM-based methods [32, 33, 44], followed by human curation, requiring high
maintenance costs. Online vector HD mapping algorithms are gaining more inter-
est over their offline counterparts as their accuracy and efficiency improve, which
would simplify the production pipeline and handle map changes. HDMapNet [16]
turns raster map segmentation into vector map instances via post-processing and
has established the first Vector HD mapping benchmark. VectorMapNet [24]


## Page 4

4
Chen et al.
BEV Memory Buffer
𝐌!"# 𝑡−1 
𝐌!"# 𝑡−2
𝐌!"# 𝑡−20
…
,
,
,
,𝐌!"# 𝑡
Perspective-view images: 𝐈(𝑡) 
Image
Backbone
Perspective-view features
BEV Module
VEC Module
𝐌!"# 𝑡−1 
𝐌!"#
∗
(𝑡−1)
Affine Trans.
𝑃%&'
%
MaskBlend
1. BEV Query 
Propagation
𝐌!"#(𝑡)
2. Deformable SA
3. Perspective-to-BEV CA
4. BEV Memory Fusion
Select w/ strides
Save 𝐌!"#(𝑡)
×
2
𝐒
Vector Memory Buffer
𝐌#"( 𝑡−1 
𝐌#"( 𝑡−2
𝐌#"( 𝑡−20
…
,
,
,
, 𝐌#"( 𝑡
𝐌#"( 𝑡−1
PropMLP
𝑃%&'
%
1. Vector Query 
Propagation
Concat
…
…
…
…
…
2. Vector Instance SA
…
…
3. BEV-to-vector CA
…
…
Select w/ strides
4. Vector Memory Fusion
𝐘(𝑡)
…
…
Save 𝐌#"((𝑡)
×
6
Conv
⊕
Affine Trans
{𝑃%!% }
BEV Memory Fusion
Select 
w/ strides
BEV Fusion Layer
Vector Memory Fusion
…
…
…
…
…
{𝑃%!% }
Select 
w/ strides
…
Q
…
…
…
…
𝐊, 𝐕
Vector Fusion Layer
…
Per-instance CA
PropMLP
𝐌!"#(𝑡)
𝐌#"(
∗
(𝑡−1)
𝐌#"((𝑡)
{𝐌!"# 𝑡) , 𝑡) ∈𝝅(𝑡)}
{𝐌#"( 𝑡) , 𝑡)
∈𝝅(𝑡)}
𝐌!"#(𝑡)
𝐌!"#(𝑡)
𝐌!"#(𝑡)
𝐌#"(
*+,*(𝑡)
𝐌#"(
-./(𝑡)
𝐌#"(
*+,*(𝑡)
𝐌#"(
-./(𝑡)
BEV Fusion Layer
Vector Fusion Layer
𝐌#"(
*+,*(𝑡)
𝐌#"(
*+,*(𝑡)
KeepPositive
𝐌!"#
0-01
𝐌#"(
0-01
Fig. 2: (Top) The overall architecture of MapTracker. (Bottom) The close-up views
of the BEV and the Vector fusion layers.
and MapTR [18] both leverage DETR-based [4] transformers for end-to-end
prediction. The former predicts the vertices of each detected curve autoregres-
sively, while the latter uses hierarchical queries and matching loss to predict all
the vertices simultaneously. MapTRv2 [19] further complements MapTR with
auxiliary tasks and network modifications. Curve representation [7,30,46], net-
work design [38], and training paradigm [5, 43] are the focus of other works.
StreamMapNet [41] steps towards consistent mapping by borrowing the stream-
ing idea from BEV perception. The idea accumulates the past information into
memory latents and passes as a condition (i.e., a conditional detection frame-
work). SQD-MapNet [36] proposes temporal curve denoising to facilitate tem-
poral learning, mimicking DN-DETR [14].
3
MapTracker
A robust memory mechanism is the core of MapTracker, accumulating a sensor
stream into latent memories of two representations: 1) Bird’s-eye-view (BEV)
memory of a region around a vehicle in the top-down BEV coordinate frame as
a latent image; and 2) Vector (VEC) memory of road elements (i.e., pedestrian-
crossings, lane-dividers, and road-boundaries) as a set of latent vectors.
Two simple ideas with the memory mechanism achieve consistent mapping.
The first idea is to use a buffer of memories from the past instead of a single


## Page 5

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
5
𝐌!"# 𝑡= [𝐌!"#
$%&$(𝑡), 𝐌!"#
'() 𝑡] ←Concat(𝐌!"#
∗
𝑡−1 , 𝐌!"#
+'+, )
𝐌-"! 𝑡←Deformable-CA (𝐌-"! 𝑡, 𝐈𝑡)
𝐌-"! 𝑡←Deformable-SA (𝐌-"! 𝑡)
𝐌-"! 𝑡←MaskBlend(𝐌-"!
∗
𝑡−1 , 𝐌-"!
+'+, )
𝐘(𝑡) ←VectorOutputHeads(𝐌!"#(𝑡))
𝐒(𝑡) ←SegmentationHead(𝐌-"! 𝑡)
Vector Module
BEV Module
𝐌!"# 𝑡−1 , 𝐌!"# 𝑡−2 , … , 𝐌-"! 𝑡, 𝑃./0
.
, 𝑃./1
.
, …
1. BEV Query Propagation 
𝐌-"!
∗
𝑡−1 ←AfOine(𝐌-"! 𝑡−1 , 𝑃./0
.
)
1. Vector Query Propagation 
2. Deformable Self Attention
3. Perspective-to-BEV Cross Attention
4. BEV Memory Fusion
2. Vector Instance Self Attention
3. BEV-to-vector Cross Attention
4. Vector Memory Fusion
𝐌!"#
∗
𝑡−1 ←PropMLP (𝐌!"# 𝑡−1 , 𝑃./0
.
)
𝐌-"! 𝑡−1 , 𝐌-"! 𝑡−2 , … , 𝐈𝑡, 𝑃./0
.
, 𝑃./1
.
, …
𝐌!"# 𝑡←SA (𝐌!"# 𝑡)
𝐌!"# 𝑡←Deformable-CA (𝐌!"# 𝑡, 𝐌-"! 𝑡)
𝐌-"! 𝑡←CNN (𝐌-"! 𝑡, 𝐌-"!
∗
𝑡2 | 𝑡2 ∈𝛑(𝑡) )
𝐌-"!(𝑡)
𝐌-"!
∗
𝑡2
𝐌-"!
+'+,
𝐌!"#(𝑡)
𝐌!"#
∗
𝑡2
𝐌!"#
+'+,
𝑃.!
."
𝛑(𝑡)
Accumulated BEV memory latents 
at timestep 𝑡, ℝ!"×$""×%!& 
Transformer BEV memory latents 
from 𝑡' to current 𝑡, ℝ!"×$""×%!& 
Learnable initial BEV query 
embeddings,  ℝ!"×$""×%!&  
Accumulated vector memory latents 
at timestep 𝑡 ,  {ℝ!$%}
Transformed vector memory latents 
from 𝑡' to current 𝑡 ,  {ℝ!$%}
Learnable initial vector queries,  
ℝ$""×!$%
Transformation matrix from 𝑡$ 
to 𝑡%,  ℝ(×(
Set of selected timesteps for 
memory fusion at timestep 𝑡
Input at time step 𝒕: 
Input at time step 𝒕: 
Output at time step 𝒕: 
Output at time step 𝒕: 
Save 𝐌-"! 𝑡
𝐌!"#
$%&$ 𝑡←Per-Ins-CA (𝐌!"#
$%&$ 𝑡, 𝐌!"#
∗
𝑡2 | 𝑡2 ∈𝛑(𝑡) )
𝐌!"# 𝑡←KeepPositive(𝐌!"# 𝑡), Save 𝐌!"# 𝑡
𝐈𝑡
Perspective-view information 
(features and camera parameters)
Fig. 3: The architecture details of the BEV and the Vector modules. The BEV-related
representations are in green, while the vector-related representations are in cyan. De-
tails of the attention layers are described in §3.
memory at the current frame [10, 17, 41]. A single memory should hold the en-
tire past information but is susceptible to memory loss, especially in cluttered
environments with numerous vehicles obscuring road structures. Concretely, we
select a subset of the past latent memories for fusion at each frame based on
the vehicle motions for efficiency and coverage. The second idea is to formu-
late the online HD mapping as a tracking task. The VEC memory mechanism
maintains a sequence of memory latents with each road element and makes this
formulation straightforward by borrowing a query propagation paradigm from
the tracking literature. The rest of the section explains our neural architectures
(See Figure 2 and Figure 3), consisting of the BEV and VEC memory buffers
and their corresponding network modules, and then presents the training details.
3.1
Memory Buffers
A BEV memory, MBEV(t) ∈R50×100×256, is a 2D latent image in the BEV
coordinate frame centered and oriented with the vehicle at frame t. The spatial
dimension (i.e., 50 × 100) covers a rectangular area, 15m left/right and 30m
front/back. Each memory latent accumulates the entire past information, while
the buffer holds such memory latents for the last 20 frames, making the memory
mechamism redundant but robust.
A VEC memory, MVEC(t) ∈{R512}, is a set of vector latents, each of which
accumulates information of an active road element up to frame t. The number of
active elements varies per frame. The buffer holds the latent vectors of the past


## Page 6

6
Chen et al.
20 frames and their correspondences across frames (i.e., a sequence of vector
latents corresponding to the same road element).
3.2
BEV Module
Inputs are 1) CNN features of the onboard perspective images processed
by the image backbone (the official ResNet50 model [11] pretrained on Im-
ageNet [6]) and their camera parameters I(t); 2) the BEV memory buffer
{MBEV(t −1), MBEV(t −2), ...}; and 3) the vehicle motions

P t
t−1, P t
t−2, ...
	
,
where P t2
t1 ∈R4×4 is the affine transformation of the vehicle coordinate frame
from frame t1 to t2. The following explains the four components of the BEV
module architecture and its outputs.
[1. BEV Query Propagation]. A BEV memory is a 2D latent image in a vehi-
cle coordinate frame. An affine transformation P t
t−1 and a bilinear interpolation
initialize the current BEV memory MBEV(t) with the previous one MBEV(t−1).
For pixels that fall outside the latent image after the transformation, per-pixel
learnable embedding vectors Minit
BEV ∈R50×100×256 are the initialization instead,
whose operation is denoted as “MaskBlend” in Figure 3.
[2. Deformable Self-Attention]. A deformable self-attention layer [47] en-
riches the BEV memory MBEV(t).
[3. Perspective-to-BEV Cross-Attention]. Similar to StreamMapNet [41],
a spatial deformable cross-attention layer from BEVFormer [17] injects the
perspective-view information I(t) into MBEV(t), followed by a standard feed-
forward network (FFN) layer [35].
[4. BEV Memory Fusion]. The memory latents in the buffer are fused to
enrich MBEV(t). Using all the memories is computationally expensive and re-
dundant. We use a strided selection of four memories without repetition, whose
vehicle positions are the closest to (1m/5m/10m/15m) from the current posi-
tion. An affine transformation and a bilinear interpolation align the coordinate
frames of the selected memories to the current: {M∗
BEV(t′), t′ ∈π(t)}, where π(t)
denotes the selected times. We concatenate MBEV(t) with the aligned memo-
ries and use a lightweight residual block with two convolution layers to udpate
MBEV(t). The last three components of the BEV module repeat twice without
weight sharing.
Outputs are 1) the final memory MBEV(t) saved to the buffer and passed to
the VEC module; and 2) the rasterized road element geometries S(t) which is
inferred by a segmentation head and used for a loss calculation (See §3.4). The
segmentation head is a linear projection module that projects each pixel in the
memory latent to a 2×2 segmentation mask, thus producing a 100×200 mask.
3.3
VEC Module
Inputs are 1) the BEV memory MBEV(t); 2) the vector memory buffer
{MVEC(t −1), MVEC(t −2), ...}; and 3) the vehicle motions

P t
t−1, P t
t−2, ...
	
.


## Page 7

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
7
[1. Vector Query Propagation]. A vector memory is a set of latent vectors
of the active road elements. Borrowing the query propagation paradigm from
transformer-based tracking approaches [27,34,42], we initialize the vector mem-
ory as MVEC(t) = [Mprop
VEC(t), Mnew
VEC(t)]. Mnew
VEC(t) denotes 100 latent vectors for
100 new road element candidates, which are initialized with 100 learnable em-
beddings Minit
VEC. Mprop
VEC(t) denotes latent vectors for the currently tracked road
elements, which are initialized with the corresponding latent vectors in the pre-
vious memory MVEC(t −1) after using a two-layer MLP to align the coordinate
frame. Concretely, we turn P t
t−1 into a 4D vector of rotation quaternion and 3D
vector of translation parameters, represent with their positional encodings [35],
concatenate them with each vector latent in MVEC(t −1), and apply an MLP.
We call it PropMLP, which handles the temporal propagation.
[2. Vector Instance Self Attention]. Similar to StreamMapNet, a standard
self-attention layer enriches the vector latents in the memory MVEC(t).
[3. BEV-to-Vector Cross Attention]. The Multi-Point Attention from
StreamMapNet, which is an extension of the vanilla deformable cross-
attention [47], injects the BEV information from MBEV(t) into MVEC(t).
[4. Vector Memory Fusion]. For each latent vector in the current memory
MVEC(t), latent vectors in the buffer associated with the same road element are
fused to enrich its representation. The same strided frame-selection chooses four
latent vectors, where the selected frames π(t) would be different and fewer for
some road elements with a short tracking history. For example, an element that
has been tracked for two frames has only two latents in the buffer. A standard
cross-attention followed by an FFN layer injects the selected latents after aligning
their coordinate frames by the same PropMLP module {M∗
VEC(t′), t′ ∈π(t)}.
To be precise, a query is a latent in Mprop
VEC(t), where a key/value is a latent
in {M∗
VEC(t′), t′ ∈π(t)}. In Figure 3, we omit the element index for the “Per-
Ins-CA” operation, which acts on each element independently. The last three
components of the VEC module repeat six times without weight sharing.
Outputs are 1) the final memory MVEC(t) for “positive” road elements that
pass the classification test by a single fully connected layer from MVEC(t); and
2) vector road geometries of the positive road elements, regressed by the 3-layer
MLP from MVEC(t). The threshold of the classification test is 0.4 for the first
frame, and 0.5/0.6 for the propagated/new road elements for subsequent frames.
Y(t) = {(Vi, pi)} denotes the outputs. Following the prior convention [18], each
element geometry Vi = [(x1, y1), . . . , (x20, y20)] is a polygonal curve with 20
points in the BEV coordinate frame. pi is the class probability score.
3.4
Training
The ground-truth road element geometries are denoted as ˆY(t) = { ˆYi}. ˆYi =
( ˆVi, ˆci), where Vi has 20 points interpolated from the raw ground-truth vector.
ˆci is the class label. Standard OpenCV and PIL libraries rasterize ˆY(t) on an
empty BEV canvas to obtain the ground-truth segmentation image ˆS(t)


## Page 8

8
Chen et al.
BEV loss. We employ per-pixel Focal loss [21] and per-class Dice loss [28] on
the BEV outputs S(t), which are common auxiliary losses in vector HD mapping
approaches [19,31]. The loss is defined by
  \m a thcal {L}_\tex t {BEV }  = \lambda _1  \mathcal {L}_\text {focal}(\bevseg (t), \hat {\bevseg }(t))+ \lambda _2 \mathcal {L}_\text {dice}(\bevseg (t), \hat {\bevseg }(t)) 
(1)
VEC loss. Inspired by MOTR [42], an end-to-end transformer for multi-object
tracking, we extend the matching-based loss [18,41] to explicitly consider ground-
truth tracks (See §4 for ground-truth processing). For each frame t, ˆY(t) consists
of two disjoint subsets: new elements ˆYnew(t) and tracked elements ˆYtrack(t). For
the vector outputs, we denote the results from the propagated latents Mprop
VEC(t)
as Ytrack(t), and results from the new latents Mnew
VEC(t) as Ynew(t). Note that
to make the VEC module robust to potential errors in pose estimation, we ran-
domly perturb the transformation matrix P t
t−1 by adding a Gaussian noise dur-
ing training. We train the module with a tracking loss that explicitly considers
the temporal alignments. §4 explains the ground-truth preparation. The optimal
instance-level label assignment for new elements is defined as:
  \matc h
ing New
 (t) = \unde
rset {\ matchingNew (t) \ in \boldsymbol {\Omega }(t) }{\mathrm {arg}\min }~\mathcal {L}_\text {match}(\hat {\vecOutputs }_\text {new}(t)|_{\matchingNew (t)}, \vecOutputs _\text {new}(t)). 
(2)
Ω(t) is the space of all bipartite matches. Lmatch is the hierarchical match-
ing cost similar to the one proposed in MapTR [18], consisting of a focal
loss Lfocal({ˆci}|ωnew(t), {pi}) and a permutation-invariant line coordinate loss
Lline({ ˆVi}|ωnew(t), {Vi}). The label assignments ω(t) between all outputs and
ground truth is then defined inductively:
  \m a tching (t )  = \matc hingTrack  
(
t)
 \ c u p
 \m a tch
in g N ew (t);~ \matchingTrack (t) = \begin {cases} \varnothing , & \text {if}~ t = 0 \\ \matching (t-1), & \text {if}~ t > 0 \end {cases} .
(3)
ωtrack(t) is the label assignments between Ytrack(t) and ˆYtrack(t). The tracking-
style loss for the vector outputs is:
  \mat h cal {L}_\text {track } = \ l ambda _3 \mathcal { L}_\text {focal}(\{ \hat {c}_i\}|_{\matching (t)}, \{ p_i \} ) + \lambda _4 \mathcal {L}_\text {line}(\{ \hat {\curve }_i\}|_{\matching (t)}, \{ \curve _i \} ).
(4)
Transformation
loss. We borrow the transformation loss Ltrans
from
StreamMapNet [41] to train the PropMLP, which enforces that the query trans-
formation in the latent space maintains the vector geometry and class type. Full
details are provided in the Appendix. The final training loss is
  \mat h cal {L }  = \mathcal {L}_\text {BEV} + \mathcal {L}_\text {track} + \lambda _5 \mathcal {L}_\text {trans}. 
(5)
Training details. For each training sample, we randomly choose 4 out of the
previous 10 frames to compose a training clip with a length of 5. We freeze the
image backbone for the first four training frames to reduce the memory cost for
the clip-based training. The training of the system has three stages: 1) Pre-train
the image backbone and BEV encoder with only LBEV; 2) Warm up the vector


## Page 9

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
9
decoder while freezing all other parameters with L, where the vector memory is
turned on after 500 warmup iterations; 3) Jointly train all parameters with L.
The second stage warms up the vector module with a large batch size to facilitate
initial convergence, as we cannot afford in the joint training. The loss weights
are λ1 = 10.0, λ2 = 1.0, λ3 = 5.0, λ4 = 50.0, λ5 = 0.1. We use an AdamW [25]
optimizer with an initial learning rate 5e-4 and the weight decay is set to 0.01.
A cosine learning rate scheduler is used with a final learning rate of 1.5e-6.
4
Consistent Vector HD Mapping Benchmarks
The section makes existing HD mapping benchmarks consistency-aware by 1)
Improving pre-processing to generate temporally consistent ground truth with
“track” labels (§4.1); and 2) Augmenting the standard mAP metric with consis-
tency checks (§4.2).
4.1
Consistent ground truth
MapTR [18,19] created vector HD mapping benchmark from nuScenes and Agro-
verse2 datasets, adopted by many follow-ups [5,19,30,43,46]. However, pedestrian
crossings are merged naively and inconsistent across frames. Divider lines are also
inconsistent (for Argoverse2) with the failures of its graph tracing process.
StreamMapNet [41] inherited code from VectorMapNet [24] and created a
benchmark with better ground truth, which has been used in the workshop
challenge [1]. However, there are still issues. For Argoverse2, divider lines are
sometimes split into shorter segments. For nuScenes, large pedestrian crossings
sometimes split out small loops, whose inconsistencies arise randomly per frame,
leading to temporarily inconsistent representations. We provide visualizations for
the issues of existing benchmarks in the Appendix.
We improve processing code from existing benchmarks to (1) enhance per-
frame ground-truth geometries, then (2) compute their correspondences across
frames, forming ground-truth “tracks”.
(1) Enhancing per-frame geometries. We inherit and improve the MapTR
codebase, which has been popular in the community, while making two changes:
Replace the pedestrian-zone processing with the one in StreamMapNet and fur-
ther improve the quality by more geometric constraints; and Enforce temporal
consistency in the divider processing by augmenting the graph tracing algorithm
to handle noises of raw annotations (only for Argoverse2).
(2) Forming tracks. Given per-frame road element geometries, we solve an
optimal bipartite matching problem between every pair of adjacent frames to es-
tablish correspondences of road elements. Pairwise correspondences are chained
to form tracks of road elements. The matching score between a pair of road ele-
ments is defined as follows. A road-element geometry is either a polygonal curve
or a loop. We transform an element geometry in an older frame to the newer


## Page 10

10
Chen et al.
one based on the vehicle motion, then rasterize both curves/loops with a cer-
tain thickness into instance masks. Their intersection over union is the matching
score. Please refer to Appendix for the full algorithmic details.
4.2
Consistency-aware mAP metric
The standard mean average precision (mAP) metric does not penalize temporar-
ily inconsistent reconstructions. We match reconstructed road elements and the
ground truth in each frame independently with Chamfer distance, as in the
standard mAP process, then remove temporarily inconsistent matches with the
following check. First, for baseline methods that do not predict tracking infor-
mation, we form tracks of reconstructed road elements using the same algorithm
we used to get ground-truth temporal correspondences (we also extend the al-
gorithm to re-identify a lost element by trading off the speed; see Appendix for
details). Next, let an “ancestor” be a road element that belongs to the same track
in a prior frame. From the beginning of the sequence, we remove a per-frame
match (of reconstructed and ground-truth elements) as temporarily inconsistent
if any of their ancestors was not a match. The standard mAP is then calculated
with the remaining temporarily consistent matches. See Appendix for complete
algorithmic details.
5
Experiments
We build our system based on the StreamMapNet codebase, while using 8
NVIDIA RTX A5000 GPUs to train our model for 72 epochs on nuScenes (18,
6, and 48 epochs for the three stages) and 35 epochs on Argoverse2 (12, 3, and
20 epochs for the three stages). The batch sizes for the three training stages are
16, 48, and 16, respectively. The training takes roughly three days, while the
inference speed is roughly 10 FPS. After explaining the datasets, the metrics,
and the baseline methods, the section provides the experimental results.
Datasets. We use the nuScenes [2] and Argoverse2 [37] datasets. nuScenes
dataset is annotated with 2Hz with 6 synchronized surrounding cameras. Input
perspective images are of size 480×800. Argoverse2 dataset is annotated with 10
Hz, using 7 surrounding cameras. Input perspective images are of size 608×608.
We follow MapTRv2 [19] and use an interval of 4 to subsample the sequences of
Argoverse2. We evaluate the methods with the official dataset splits as well as
the geographically non-overlapping splits proposed in StreamMapNet [41].
Metrics. We follow prior works [18,19,24,41] and use Average Precision (AP) as
the main evaluation metric, where Chamfer distance is the matching criterion.
The AP is averaged across three distance thresholds {0.5m, 1.0m, 1.5m}. The
final mean AP (mAP) is computed by averaging the results over the three road
element types: pedestrian crossing, lane-divider, and road-boundary. We provide
both the original scores and the new consistency-aware augmented scores (§4.2).
Baselines. MapTRv2 [19] and StreamMapNet [41] are the main baselines due
to their popularity and superior performance. We run their official codebase and


## Page 11

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
11
Table 1: Results on nuScenes [2]. The first column shows three different ground
truth used for training and testing. “Consistent” is our temporarily consistent ground
truth. The standard AP scores are reported for pedestrian crossing, lane-divider, road-
boundary, and their average. C-mAP is our consistency-aware metric, which requires
tracking information in the ground truth and is reported only for Consistent. +: Num-
bers are from the original papers. †: Epochs for our multi-frame training.
G.T. data
Method
Backbone Epoch APp APd APb mAP C-mAP
MapTR
MapTR+ [18]
R50
110
56.2 59.8 60.1
58.7
-
PivotNet+ [7]
SwinT
110
62.6 68.0 69.7
66.8
MapTRv2+ [19]
R50
110
68.1 68.3 69.7
68.7
GeMap+ [46]
R50
110
67.1 69.8 71.4
69.4
StmMapNet
StreamMapNet [41]
R50
110
68.0 71.2 68.0
69.1
-
SQD-MapNet+ [36]
R50
24
63.6 66.6 64.8
65.0
MapTracker (Ours)
R50
72†
77.3 72.4 74.2
74.7
Consistent
MapTRv2 [19]
R50
110
69.6 68.5 70.3
69.5
50.5
StreamMapNet [41]
R50
110
70.0 72.9 68.3
70.4
56.4
MapTracker (Ours)
R50
72†
80.0 74.1 74.1
76.1
69.1
train the models until complete convergence. The results of recent competing
methods [7,36,46] are also included for reference by copying numbers from their
corresponding papers.
5.1
Quantitative evaluations
One of our contributions is the temporarily consistent ground truth (GT) over
the two existing counterparts (i.e., MapTR [18, 19] and StreamMapNet [41]).
Table 1 and Table 2 show the results where a system is trained and tested on
one of the three GTs (shown in the first column). Since our codebase is based
on StreamMapNet, we evaluate our system on the StreamMapNet GT and our
temporarily consistent GT.
nuScenes results. Table 1 shows that both MapTRv2 and StreamMapNet
achieve better mAP with our GT, which is expected as we fixed the inconsis-
tencies in their original GT (explained in §4.1). StreamMapNet’s improvement
is slightly higher since it has temporal modeling (whereas MapTR does not)
and exploits temporal consistency in the data. MapTracker significantly outper-
forms the competing methods, especially with our consistent GT by more than
8% and 22% in the original and the consistency-aware mAP scores. Note that
MapTracker is the only system to produce explicit tracking information (i.e.,
correspondences of reconstructed elements across frames), which is required for
the consistency-area mAP. A simple matching algorithm creates tracks for the
baseline methods (See Appendix for details). We also measure the running speed
of
Argoverse2 results. Table 2 shows that both MapTRv2 and StreamMapNet
achieve better mAP scores with our consistent GT, which has higher quality


## Page 12

12
Chen et al.
Table 2: Results on Argoverse2 [37]. +: Numbers are from the original papers. †:
Epochs for our multi-frame training.
G.T. data
Method
Backbone Epoch APp APd APb mAP C-mAP
MapTR
MapTRv2+ [19]
R50
6*4
62.9 72.1 67.1 67.4
-
GeMap+ [46]
R50
24*4
69.2 75.7 70.5 71.8
StmMapNet
StreamMapNet+ [41]
R50
30
62.0 59.5 63.0 61.5
-
StreamMapNet [41]
R50
72
65.0 62.2 64.9 64.0
SQD-MapNet+ [36]
R50
30
64.9 60.2 64.9 63.3
MapTracker (Ours)
R50
35†
74.5 66.4 73.4 71.4
Consistent
MapTRv2 [19]
R50
24*4
68.3 75.6 68.9 70.9
56.1
StreamMapNet [41]
R50
72
70.5 74.2 66.1 70.3
57.5
MapTracker (Ours)
R50
35†
77.0 80.0 73.7 76.9
68.3
Table 3: Results with geographically non-overlapping data proposed in StreamMap-
Net [41]. Our consistent ground truth is used. †: Epochs for our multi-frame training.
Range
Dataset
Method
Epoch APp APd APb mAP C-mAP
60×30m
nuScenes [2]
StreamMapNet [41]
110
31.6 28.1 40.7 33.5
22.2
MapTracker (Ours)
72†
45.9 30.0 45.1 40.3
32.5
Argoverse2 [37] StreamMapNet [41]
72
61.8 68.2 63.2 64.4
54.4
MapTracker (Ours)
35†
70.0 75.1 68.9 71.3
63.2
100×50m
nuScenes [2]
StreamMapNet [41]
110
25.1 18.9 25.0 23.0
14.6
MapTracker (Ours)
72†
45.9 24.3 38.4 36.2
27.5
Argoverse2 [37] StreamMapNet [41]
72
60.1 56.1 47.5 54.6
41.3
MapTracker (Ours)
35†
71.2 64.6 58.5 64.8
55.7
GT (for pedestrian crossings and dividers) besides being temporarily consis-
tent, benefiting all the methods. MapTracker outperforms all the other base-
lines by significant margins (i.e., 11% or 8%, respectively) in all settings. The
consistency-aware score (C-mAP) further demonstrates our superior consistency,
showing an improvement of more than 18% over StreamMapNet.
5.2
Results with geographically non-overlapping data
Official training/testing splits of nuScenes and Agroverse2 datasets have geo-
graphical overlaps (i.e., the same roads appear in both training/testing), which
allows overfitting [20]. Table 3 compares the best baseline method StreamMap-
Net [41] and MapTracker based on the geographically non-overlapping splits with
two different perception ranges (the settings are proposed by StreamMapNet).
MapTracker consistently outperforms StreamMapNet with significant margins,
demonstrating robust cross-scene generalization. Note that the performance for
nuScenes degrades for both methods. Upon careful inspection, road elements


## Page 13

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
13
Table 4: Ablation studies on the key design elements of MapTracker, evaluated on the
nuScenes dataset with our consistent ground truth.
Method
Task
Memory
Metrics
Embed. +Fusion +Stride APp APd APb mAP C-mAP
Baseline [41]
Detection
-
-
-
69.5 71.7 68.5 69.9
56.1
StmMapNet [41] Cond. detect.
✓
-
-
70.0 72.9 68.3 70.4
56.4
MapTracker
Tracking
✓
-
-
73.8 69.2 69.4 70.8
62.4
✓
✓
-
78.6 73.3 72.8 74.9
68.1
✓
✓
✓
80.0 74.1 74.1 76.1
69.1
were detected successfully, but the regressed coordinates had large errors, lead-
ing to low performance.
5.3
More analysis
Ablation study of core model components. Table 4 demonstrate the con-
tributions of key design elements in MapTracker. The first “baseline” entry is
StreamMapNet without its temporal reasoning capabilities (i.e., without its BEV
and vector streaming memories and modules). The second entry is StreamMap-
Net. Both methods are trained for 110 epochs till full convergence. The last three
entries are the variants of MapTracker with or without the key elements. The first
variant drops the memory fusion components in the BEV/VEC modules. This
variant utilizes the tracking formulation but relies on a single BEV/VEC mem-
ory to hold the past information, like the GRU embedding of StreamMapNet.
The second variant adds the memory buffers and the memory fusion components
but without the striding strategy, that is, using the latest 4 frames for the fusion.
This variant significantly boosts performance, demonstrating the effectiveness of
our memory mechanism. The last variant adds memory striding, which makes
more effective use of the memory mechanism and improves performance.
Table 5: Ablation study of the four distance strides, evaluated on the old data split
of the nuScenes dataset with 60m×30m range.
Buffer size
Strides (m)
APp APd APb mAP C-mAP
4
-
78.6
73.3 72.8
74.9
68.1
20
{0, 0, 0, 0}
78.8
73.5 72.9
75.0
68.2
{1, 2, 3, 4}
79.9
74.0 73.6
75.8
68.8
{1, 3, 5, 7}
79.9
74.0 73.8
75.9
68.8
{1, 5, 10, 15}
80.0
74.1 74.1
76.1
69.1
{5, 10, 15, 20} 77.6
71.3 72.6
73.8
51.5
Choice of memory strides. Table 5 presents the ablation study over the choice
of the four distance strides. We believe {1m, 5m, 10m, 15m} works well for two
main reasons: 1) The first entry (i.e., 1m) helps stabilize the prediction of the


## Page 14

14
Chen et al.
MapTracker (Ours)
StreamMapNet
MapTRv2
Ground Truth
Fig. 4: Qualitative comparisons of the two representative baselines, MapTracker
(Ours), and the ground truth. A simple online algorithm merges per-frame vector HD
map reconstructions across a single drive-through into a global vector HD map. The
top five examples are from nuScenes, while the bottom two are from Argoverse2.
current frame and should be close to the current frame to align with the training
setup (for each training sample, we randomly sample 4 previous frames from the
last 10 frames to form a training clip); and 2) The entries should have proper
distance gaps to minimize the information redundancy in the memory.
Inference speed. We evaluate the inference speed of MapTRv2, StreamMap-
Net, and MapTracker on the nuScenes dataset using a single NVIDIA RTX 6000


## Page 15

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
15
GPU with batch size 1. The results are 12.5 FPS, 14.2 FPS, and 11.5 FPS,
respectively. MapTracker has different query propagation from StreamMapNet
and introduces additional memory fusion layers, so the FPS is lower than the
original StreamMapNet by 19% (11.5 vs. 14.2). Our current implementation of
the vector memory fusion layer uses for-loops to iterate through all vector in-
stances without batching, which is sub-optimal and could be optimized for better
running efficiency.
5.4
Qualitative evaluations
Figure 4 presents qualitative comparisons of MapTracker and the baseline meth-
ods on both nuScenes and Argoverse2 datasets. For better visualization, we use
a simple algorithm to merge per-frame vector HD maps into a global vector HD
map. Please refer to Appendix for the details of the merging algorithm and the
visualization of per-frame reconstructions. MapTracker produces much more ac-
curate and cleaner results, demonstrating superior overall quality and temporal
consistency. For scenarios where the vehicle is turning or not trivially moving
forward (including the two examples in Figure 1), StreamMapNet and Map-
TRv2 can produce unstable results, thus leading to broken and noisy merged
results. This is mainly because the detection-based formulation has difficulties
maintaining temporally coherent reconstructions under complex vehicle motions.
6
Conclusion
This paper introduces MapTracker, which formulates vector HD mapping as a
tracking task and leverages a history of raster and vector latents to maintain
temporal consistency. We employ a query propagation mechanism to associate
tracked road elements across frames, and fuse a subset of memory entries se-
lected with distance strides to enhance consistency. We also improve existing
benchmarks by generating consistent ground truth with tracking labels and aug-
menting the original mAP metric with temporal consistency checks. MapTracker
significantly outperforms existing methods on nuScenes and Agroverse2 datasets
when evaluated with the traditional metrics and demonstrates superior temporal
consistency when evaluated with our consistency-aware metrics.
Limitations. We identify two limitations of MapTracker. First, the current
tracking formulation does not handle the merges and the splits of road elements
(e.g., a U-shaped boundary splits into two straight lines in a future frame, or vice
versa). The ground truth does not represent them properly either. Second, our
system is still at 10 FPS, falling a bit short of real-time performance, especially
at critical crashing events. Optimizing the efficiency and handling more complex
real-world road structures are our future work.
Acknowledgements. This research is partially supported by NSERC Discovery
Grants, NSERC Alliance Grants, and John R. Evans Leaders Fund (JELF). We
thank the Digital Research Alliance of Canada and BC DRI Group for providing
computational resources.


## Page 16

16
Chen et al.
References
1. Online hd map construction challenge for autonomous driving on cvpr 2023 work-
shop on end-to-end autonomous driving. https://github.com/Tsinghua-MARS-
Lab/Online-HD-Map-Construction-CVPR2023 (2023) 9
2. Caesar, H., Bankiti, V., Lang, A.H., Vora, S., Liong, V.E., Xu, Q., Krishnan, A.,
Pan, Y., Baldan, G., Beijbom, O.: nuscenes: A multimodal dataset for autonomous
driving. In: Proceedings of the IEEE/CVF conference on computer vision and
pattern recognition. pp. 11621–11631 (2020) 2, 10, 11, 12, 26
3. Cai, J., Xu, M., Li, W., Xiong, Y., Xia, W., Tu, Z., Soatto, S.: Memot: Multi-object
tracking with memory. In: Proceedings of the IEEE/CVF Conference on Computer
Vision and Pattern Recognition. pp. 8090–8100 (2022) 3
4. Carion, N., Massa, F., Synnaeve, G., Usunier, N., Kirillov, A., Zagoruyko, S.: End-
to-end object detection with transformers. In: European conference on computer
vision. pp. 213–229. Springer (2020) 1, 4
5. Chen, J., Deng, R., Furukawa, Y.: Polydiffuse: Polygonal shape reconstruction via
guided set diffusion models. arXiv preprint arXiv:2306.01461 (2023) 4, 9
6. Deng, J., Dong, W., Socher, R., Li, L.J., Li, K., Fei-Fei, L.: Imagenet: A large-
scale hierarchical image database. In: 2009 IEEE conference on computer vision
and pattern recognition. pp. 248–255. Ieee (2009) 6
7. Ding, W., Qiao, L., Qiu, X., Zhang, C.: Pivotnet: Vectorized pivot learning for
end-to-end hd map construction. In: Proceedings of the IEEE/CVF International
Conference on Computer Vision. pp. 3672–3682 (2023) 4, 11
8. Gao, R., Wang, L.: Memotr: Long-term memory-augmented transformer for multi-
object tracking. In: Proceedings of the IEEE/CVF International Conference on
Computer Vision. pp. 9901–9910 (2023) 3
9. Gu, J., Hu, C., Zhang, T., Chen, X., Wang, Y., Wang, Y., Zhao, H.: Vip3d: End-
to-end visual trajectory prediction via 3d agent queries. In: Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 5496–
5506 (2023) 3
10. Han, C., Sun, J., Ge, Z., Yang, J., Dong, R., Zhou, H., Mao, W., Peng, Y., Zhang,
X.: Exploring recurrent long-term temporal fusion for multi-view 3d perception.
arXiv preprint arXiv:2303.05970 (2023) 3, 5
11. He, K., Zhang, X., Ren, S., Sun, J.: Deep residual learning for image recognition. In:
Proceedings of the IEEE conference on computer vision and pattern recognition.
pp. 770–778 (2016) 6
12. Huang, J., Huang, G.: Bevdet4d: Exploit temporal cues in multi-camera 3d object
detection. arXiv preprint arXiv:2203.17054 (2022) 3
13. Li, E., Casas, S., Urtasun, R.: Memoryseg: Online lidar semantic segmentation
with a latent memory. In: Proceedings of the IEEE/CVF International Conference
on Computer Vision (2023) 3
14. Li, F., Zhang, H., Liu, S., Guo, J., Ni, L.M., Zhang, L.: Dn-detr: Accelerate detr
training by introducing query denoising. In: Proceedings of the IEEE/CVF Con-
ference on Computer Vision and Pattern Recognition. pp. 13619–13627 (2022) 4
15. Li, H., Sima, C., Dai, J., Wang, W., Lu, L., Wang, H., Zeng, J., Li, Z., Yang,
J., Deng, H., et al.: Delving into the devils of bird’s-eye-view perception: A re-
view, evaluation and recipe. IEEE Transactions on Pattern Analysis and Machine
Intelligence (2023) 3
16. Li, Q., Wang, Y., Wang, Y., Zhao, H.: Hdmapnet: An online hd map construc-
tion and evaluation framework. In: 2022 International Conference on Robotics and
Automation (ICRA). pp. 4628–4634. IEEE (2022) 1, 3


## Page 17

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
17
17. Li, Z., Wang, W., Li, H., Xie, E., Sima, C., Lu, T., Qiao, Y., Dai, J.: Bevformer:
Learning bird’s-eye-view representation from multi-camera images via spatiotem-
poral transformers. In: European conference on computer vision. pp. 1–18. Springer
(2022) 3, 5, 6
18. Liao, B., Chen, S., Wang, X., Cheng, T., Zhang, Q., Liu, W., Huang, C.: Maptr:
Structured modeling and learning for online vectorized hd map construction. arXiv
preprint arXiv:2208.14437 (2022) 1, 4, 7, 8, 9, 10, 11
19. Liao, B., Chen, S., Zhang, Y., Jiang, B., Zhang, Q., Liu, W., Huang, C., Wang,
X.: Maptrv2: An end-to-end framework for online vectorized hd map construction.
arXiv preprint arXiv:2308.05736 (2023) 1, 2, 4, 8, 9, 10, 11, 12, 21
20. Lilja, A., Fu, J., Stenborg, E., Hammarstrand, L.: Localization is all you evalu-
ate: Data leakage in online mapping datasets and how to fix it. arXiv preprint
arXiv:2312.06420 (2023) 12
21. Lin, T.Y., Goyal, P., Girshick, R., He, K., Dollár, P.: Focal loss for dense object
detection. In: Proceedings of the IEEE international conference on computer vision.
pp. 2980–2988 (2017) 8
22. Lin, X., Lin, T., Pei, Z., Huang, L., Su, Z.: Sparse4d v2: Recurrent temporal fusion
with sparse model. arXiv preprint arXiv:2305.14018 (2023) 3
23. Lin, X., Pei, Z., Lin, T., Huang, L., Su, Z.: Sparse4d v3: Advancing end-to-end 3d
detection and tracking. arXiv preprint arXiv:2311.11722 (2023) 3
24. Liu, Y., Yuan, T., Wang, Y., Wang, Y., Zhao, H.: Vectormapnet: End-to-end vec-
torized hd map learning. In: International Conference on Machine Learning. pp.
22352–22369. PMLR (2023) 1, 3, 9, 10
25. Loshchilov, I., Hutter, F.: Fixing weight decay regularization in adam. ArXiv
abs/1711.05101 (2017) 9
26. Ma, Y., Wang, T., Bai, X., Yang, H., Hou, Y., Wang, Y., Qiao, Y., Yang, R.,
Manocha, D., Zhu, X.: Vision-centric bev perception: A survey. arXiv preprint
arXiv:2208.02797 (2022) 3
27. Meinhardt, T., Kirillov, A., Leal-Taixe, L., Feichtenhofer, C.: Trackformer: Multi-
object tracking with transformers. In: Proceedings of the IEEE/CVF conference
on computer vision and pattern recognition. pp. 8844–8854 (2022) 3, 7
28. Milletari, F., Navab, N., Ahmadi, S.A.: V-net: Fully convolutional neural networks
for volumetric medical image segmentation. In: 2016 fourth international confer-
ence on 3D vision (3DV). pp. 565–571. Ieee (2016) 8
29. Philion, J., Fidler, S.: Lift, splat, shoot: Encoding images from arbitrary camera
rigs by implicitly unprojecting to 3d. In: Computer Vision–ECCV 2020: 16th Eu-
ropean Conference, Glasgow, UK, August 23–28, 2020, Proceedings, Part XIV 16.
pp. 194–210. Springer (2020) 3
30. Qiao, L., Ding, W., Qiu, X., Zhang, C.: End-to-end vectorized hd-map construc-
tion with piecewise bezier curve. In: Proceedings of the IEEE/CVF Conference on
Computer Vision and Pattern Recognition. pp. 13218–13228 (2023) 4, 9
31. Qiao, L., Zheng, Y., Zhang, P., Ding, W., Qiu, X., Wei, X., Zhang, C.: Machmap:
End-to-end vectorized solution for compact hd-map construction. arXiv preprint
arXiv:2306.10301 (2023) 8
32. Shan, T., Englot, B.: Lego-loam: Lightweight and ground-optimized lidar odometry
and mapping on variable terrain. In: 2018 IEEE/RSJ International Conference on
Intelligent Robots and Systems (IROS). pp. 4758–4765. IEEE (2018) 3
33. Shan, T., Englot, B., Meyers, D., Wang, W., Ratti, C., Rus, D.: Lio-sam: Tightly-
coupled lidar inertial odometry via smoothing and mapping. In: 2020 IEEE/RSJ
international conference on intelligent robots and systems (IROS). pp. 5135–5142.
IEEE (2020) 3


## Page 18

18
Chen et al.
34. Sun, P., Cao, J., Jiang, Y., Zhang, R., Xie, E., Yuan, Z., Wang, C., Luo,
P.:
Transtrack:
Multiple
object
tracking
with
transformer.
arXiv
preprint
arXiv:2012.15460 (2020) 3, 7
35. Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser,
Ł., Polosukhin, I.: Attention is all you need. Advances in neural information pro-
cessing systems 30 (2017) 3, 6, 7
36. Wang, S., Jia, F., Liu, Y., Zhao, Y., Chen, Z., Wang, T., Zhang, C., Zhang,
X., Zhao, F.: Stream query denoising for vectorized hd map construction. arXiv
preprint arXiv:2401.09112 (2024) 3, 4, 11, 12
37. Wilson, B., Qi, W., Agarwal, T., Lambert, J., Singh, J., Khandelwal, S., Pan, B.,
Kumar, R., Hartnett, A., Pontes, J.K., et al.: Argoverse 2: Next generation datasets
for self-driving perception and forecasting. arXiv preprint arXiv:2301.00493 (2023)
2, 10, 12, 26
38. Xu, Z., Wong, K.K., Zhao, H.: Insightmapper: A closer look at inner-instance in-
formation for vectorized high-definition mapping. arXiv preprint arXiv:2308.08543
(2023) 4
39. Yang, C., Chen, Y., Tian, H., Tao, C., Zhu, X., Zhang, Z., Huang, G., Li, H., Qiao,
Y., Lu, L., et al.: Bevformer v2: Adapting modern image backbones to bird’s-eye-
view recognition via perspective supervision. In: Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition. pp. 17830–17839 (2023)
3
40. Yilmaz, A., Javed, O., Shah, M.: Object tracking: A survey. Acm computing sur-
veys (CSUR) 38(4), 13–es (2006) 3
41. Yuan, T., Liu, Y., Wang, Y., Wang, Y., Zhao, H.: Streammapnet: Streaming map-
ping network for vectorized online hd map construction. In: Proceedings of the
IEEE/CVF Winter Conference on Applications of Computer Vision. pp. 7356–
7365 (2024) 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 21
42. Zeng, F., Dong, B., Zhang, Y., Wang, T., Zhang, X., Wei, Y.: Motr: End-to-end
multiple-object tracking with transformer. In: European Conference on Computer
Vision. pp. 659–675. Springer (2022) 3, 7, 8
43. Zhang, G., Lin, J., Wu, S., Song, Y., Luo, Z., Xue, Y., Lu, S., Wang, Z.: Online map
vectorization for autonomous driving: A rasterization perspective. arXiv preprint
arXiv:2306.10502 (2023) 4, 9
44. Zhang, J., Singh, S.: Loam: Lidar odometry and mapping in real-time. In: Robotics:
Science and systems (2014) 3
45. Zhang, Y., Wang, T., Zhang, X.: Motrv2: Bootstrapping end-to-end multi-object
tracking by pretrained object detectors. In: Proceedings of the IEEE/CVF Con-
ference on Computer Vision and Pattern Recognition. pp. 22056–22065 (2023) 3
46. Zhang, Z., Zhang, Y., Ding, X., Jin, F., Yue, X.: Online vectorized hd map con-
struction using geometry. arXiv preprint arXiv:2312.03341 (2023) 4, 9, 11, 12
47. Zhu, X., Su, W., Lu, L., Li, B., Wang, X., Dai, J.: Deformable detr: Deformable
transformers for end-to-end object detection. arXiv preprint arXiv:2010.04159
(2020) 6, 7


## Page 19

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
19
Appendix:
MapTracker: Tracking with Strided Memory Fusion for
Consistent Vector HD Mapping
The appendix provides remaining system details (§A,§B,§C) and additional ex-
perimental results (§D) as mentioned in the main paper.
⋄§A: Remaining details of MapTracker, including 1) The transformation loss
for PropMLP; 2) The query propagation module; and 3) The strided memory
selection mechanism.
⋄§B: Remaining details/analyses of our consistent vector HD mapping bench-
marks, including details on 1) consistent ground truth generation; 2) the
track extraction algorithm for detection-based baseline approaches; and 3)
the consistency-aware mAP (C-mAP).
⋄§C: Details of our online merging algorithm that generates the global vector
HD maps from per-frame reconstructions.
⋄§D: Additional experimental results and analyses, including 1) The C-mAP
results of all methods using the track extraction algorithm with different look-
back parameters; 2) Check the temporal consistency of MapTR’s ground truth
data using our consistent-aware benchmarks; and 3) Additional qualitative re-
sults.
A
Remaining Details of MapTracker
This section explains the remaining details of MapTracker (refer §3 of the main
paper).
A.1
Transformation loss details
The transformation loss Ltrans trains the PropMLP to ensure the latent trans-
formation maintains the geometry and class type. The inputs and outputs of
the PropMLP are described in §3.3, Figure 2, and Figure 3 of the main paper.
For the propagated vector latents M∗
VEC(t −1) from t −1 to t, we apply the
vector output heads to get the predictions Y∗(t−1). We then derive the ground
truth ˆY∗(t −1) by directly applying the transformation matrix to the ground
truth ˆY(t −1). Since we have the optimal bipartite match ω(t −1) of t −1, the
transformation loss is defined by
  \mat h cal {L}_\te
x t { trans} &= \mathcal {L}_\text {focal}(\{ \hat {c}^*_i(t-1)\}|_{\matching (t-1)}, \{ p_i^*(t-1) \} ) \\ &+ \mathcal {L}_\text {line}(\{ \hat {\curve }_i^*(t-1)\}|_{\matching (t)}, \{ \curve _i^*(t-1) \} ),
where ˆY∗(t −1) = { ˆV ∗
i (t −1), ˆc∗
i (t −1)} and Y∗(t −1) = {V ∗
i (t −1), p∗
i (t −1)}.


## Page 20

20
Chen et al.
𝑡
𝑡+ 1
MapTR
Ours
𝑡
𝑡+ 1
Stream
Ours
𝑡
𝑡−1
𝑡+ 1
𝑡
𝑡−1
𝑡+ 1
Fig. 5: Typical examples of problematic pedestrian crossing annotations in existing
ground truth for nuScenes. (Top) MapTR’s ground truth merges or splits nearby pedes-
trian crossings at the perception boundary, leading to temporal inconsistencies. (Bot-
tom) StreamMapNet’s ground truth does not have the above merge/split issue but
sometimes fails to fuse small polygons (from raw annotations) into a global one.
A.2
Memory fusion details
§3.2 and §3.3 of the main paper have explained our BEV and vector memory
fusion. We provide more implementation details here.
Strided memory selection. We present the concrete implementation steps
of our strided memory selection in the following. Firstly, we sort all memory
entries based on the distance to the current location. Then, we select one closest
memory entry for each stride value, starting from the farthest stride (i.e., 15m).
If the memory buffer contains less than four history latents, we simply take all.
Vector fusion layer. For the per-instance cross-attention of the vector fusion
layer, we compute the absolute value of the relative frame difference from the
history to the current frame, encode it with the sin/cos positional encoding,
and use the encoding as the position encoding for the key and values of the
cross-attention.
B
Remaining Details of Benchmark Contributions
This section presents thorough details of our consistent vector HD mapping
benchmarks, complementing §4 of the main paper.
B.1
Consistent ground truth
We review the typical problems of the two existing ground-truth data and demon-
strate the improved quality of our consistent ground truth.


## Page 21

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
21
MapTR
Ours
StmMapNet
Ours
StmMapNet
Ours
t
t+1
t+2
t+3
t
t+1
t+2
t+3
t
t+1
t+2
t+3
Fig. 6: Typical failure cases in MapTR and StreamMapNet’s ground truth dividers
on Argoverse2. (Top) MapTR’s ground truth fails to properly merge short divider
segments into a global one, and the entire dividers can even be missing due to the
failure of its graph tracing algorithm. (Bottom) StreamMapNet’s ground-truth dividers
suffer from temporal inconsistency (split and merge constantly as the car goes).
Pedestrain-crossing (nuScenes and Argoverse2). Figure 5 shows typical
failure cases in MapTR [19] and StreamMapNet’s [41] ground truth (GT) for the
pedestrian crossing class. The examples are from the nuScenes dataset, where
the raw annotations are many small polygon pieces. A merging algorithm must
merge the pieces to get a correct global polygon for each pedestrian crossing
instance. MapTR’s merging algorithm merges all small polygons with overlaps
in a brute-force way, making some polygons merge and split when crossing the
perception boundary and introducing temporal inconsistency. StreamMapNet’s
merging algorithm considers the orientation of each polygon piece to avoid merg-
ing orthogonal pedestrian crossings, thus achieving better temporal consistency.
However, the algorithm sometimes fails to handle noisy small pieces near the
perception boundary. We borrow the merging algorithm from StreamMapNet
and impose more geometric constraints as conditions when merging the polygon
pieces, resulting in almost perfect temporal consistency.
In Argoverse2, the raw annotations of each pedestrian crossing are two line
segments, making the ground truth processing easier. However, MapTR and


## Page 22

22
Chen et al.
Algorithm 1 Track Generation Algorithm
1: Input: Sequence of predicted vectors {V (t), t = 1, ..., T}, Sequence of predicted
scores {p(t), t = 1, ..., T}, filter threshold τ = 0.4, look-back frame number N
2: Output: {MID(t), t = 1, ...T}, MID(t) records the global id of positive predictions
in V (t)
3: for t = 1 : T do
4:
Init MID(t) as an empty mapping
5:
Obtain a subset of positive vectors V ′(t) = {Vj(t) ∈V (t), pj(t) > τ}
6:
if t = 0 then
7:
Assign a new global id to each v′
j(t), update MID(t)
8:
continue
9:
end if
10:
for k = 1 : N do
11:
Transform V ′(t−k) to the current frame, V ′
t (t−k)= Affine(V ′(t−k), P t
t−k)
12:
Do bipartite matching between V ′(t) with V ′
t (t −k) using the IoU between
rasterized masks, store the optimal bipartite matching as Brec(k)
13:
end for
14:
for k = 1 : N do
15:
for v′
j(t) in V ′(t)
16:
if v′
j(t) doesn’t have a global id in MID(t), and v′
j(t) in Brec(k) then
17:
Get the global id of v′
j(t)’s matched instance in MID(t −k),
18:
Assign this id to v′
j(t), update MID(t)
19:
end if
20:
end for
21:
end for
22:
for v′
j(t) in V ′(t)
23:
if v′
j(t) doesn’t have a global id in MID(t) then
24:
Assign a new global id to v′
j(t), update MID(t)
25:
end if
26:
end for
27: end for
StreamMapNet’s processing codes sometimes produce open-loop curves at the
perception boundary. We fix their codes to always produce closed polygon loops.
Divider (Argoverse2). Figure 6 shows the failure cases of the lane divider
class in MapTR and StreamMapNet’s ground truth. The examples are from Ar-
goverse2, where the raw annotations are many short divider segments, and a
merging algorithm should merge the segments belonging to the same divider
instance. MapTR employs a graph-tracing algorithm to connect the line seg-
ments, where each segment is a node, and segments of the same instance are
connected by tracing from a root to the leaf. However, some annotations are
corrupted with incomplete graph information, making the graph tracing algo-
rithm fail completely and miss entire dividers. For StreamMapNet, owing to its
unstable threshold-based rules to connect divider segments, it sometimes fails to
produce correct long dividers, leading to temporal inconsistency.
To obtain better ground truth, we first fix the graph-tracing algorithm
to avoid missing entire dividers. To handle the noisy/corrupted graph infor-


## Page 23

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
23
mation from the annotations, we then borrow the threshold-based rules from
StreamMapNet to further connect the dividers produced by the graph tracing
algorithm.
B.2
Track extraction algorithm
We show details of the track extraction algorithm in Algorithm 1. This algo-
rithm forms tracks for 1) our consistent ground truth to generate the temporal
alignments and 2) the baseline methods to form tracks from per-frame recon-
structions. The algorithm has a “look-back” hyper-parameter N, specifying how
many previous frames to check when determining the temporal correspondence
(i.e., assigning a global ID to an element in the current frame). Larger look-
back parameters better tolerate missing reconstructions by re-identification but
greatly slow down the entire vector HD mapping pipeline.
The ground-truth track formation uses N = 1 (See §4.1 of the main paper).
In the main paper, the baselines use N = 1 to have similar real-time inference
speeds for fair evaluations. A large N improves the C-mAP metric for all the
methods but is computationally expensive due to the per-instance rasterization
and the bipartite matching. For example, the track extraction algorithm alone
is almost 4 times more expensive than the MapTRv2 baseline (with ResNet50)
when N = 5. As reference, this appendix (§D.1) provides additional results when
N = 3 or N = 5.
B.3
Consistent-aware mAP
Algorithm 2 presents the algorithmic details for computing our Consistent-aware
mAP (C-mAP). Note that the algorithm computes the C-mAP of one distance
threshold, while the actual evaluation metrics compute the results of three dis-
tances and take the average. The consistency check is at the line 11 of the
algorithm. The definition of the C-mAP metric does not include the track ex-
traction algorithm and does not introduce extra hyperparameters. An ideal vec-
tor HD mapping method should explicitly predict tracks of reconstruction like
MapTracker, instead of relying on an external algorithm for track formation.
The conventional distance-based mAP (reported in the main paper) consid-
ers all predictions, including those with low confidence scores, when computing
the area under curve to get per-class average precision (AP). However, since
the tracks are only defined for positive predictions (negative predictions do not
have a “global ID”), the computation of C-mAP excludes negative predictions.
Therefore, the value of C-mAP can never reach the conventional mAP, even
with perfectly predicted temporal correspondences. To set up an upper bound
for C-mAP when all consistency checks are passed, §D.1 reports the results of
“C-mAP”, which computes C-mAP by ignoring the consistency checks.


## Page 24

24
Chen et al.
Algorithm 2 Consist-aware mAP
1: Input: Predicted vectors V , GT vectors ˆV , Predicted Global ID I, GT Global ID
ˆI, Predicted scores P, a Chamfer distance threshold σ (e.g., 0.5m)
2: Output: The C-mAP on the test set
3: for each sequence in the test set do
4:
Brec records the matching between predictions and GT across the sequence
5:
for each timestep t do
6:
Obtain the optimal bipartite matching between V (t) and ˆV (t), denoted as
I(t) →ˆI(t), and sort V (t) in descending order based on P(t)
7:
for vj(t) in V (t)
8:
if vj(t) has a matched GT vector with Chamfer distance ≤σ then
9:
Define ˆIj as the global ID of the GT vector that matches vj(t)
10:
if ˆIj has existed in Brec then
11:
if its matched prediction ID is not Ij // Consistency check
12:
Consider vj(t) as FP (False Positive)
13:
else
14:
Consider vj(t) as TP (True Positive)
15:
end if
16:
else
17:
Consider vj(t) as TP (True Positive), and update Brec
18:
end if
19:
else
20:
Consider vj(t) as FP
21:
end if
22:
Record the TP/FP for vj(t), along with its score pj(t)
23:
end for
24:
Get TP, FP, and scores for V (t)
25:
end for
26:
Get TP, FP, and scores for the entire sequence
27: end for
28: Sort TP and FP of all sequences with the scores in descending order to calculate
the AP, get the consistency-aware AP (C-AP).
29: The C-mAP is the average C-AP across all classes
C
Details of Online Merging Algorithm
Algorithm 3 presents the high-level pseudo-code for our online merging algo-
rithm, which merges per-frame reconstructions into a global vector HD map.
Note that our merging algorithm is simple and not perfect, and may occasion-
ally fail to accurately merge the per-frame data. However, the main goal of
implementing this merging algorithm is to investigate and analyze the consis-
tency of per-frame reconstructions. More advanced algorithms can be designed
and implemented if we need high-quality merged global maps.
D
Additional Experimental Results and Analyses
This section presents additional experimental results and analyses, complement-
ing §5 of the main paper.


## Page 25

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
25
Algorithm 3 Online Merging Algorithm
1: Input: Predicted set Y (t) for each timestep t;
2: Dictionary D[I] records the merged vectors, I represents the global ID of the pre-
dicted vectors
3: for each timestep t do
4:
for each pair (Vi, ci) in Y (t) do
5:
Ii ←Global ID of Vi
6:
if Ii is not in D then
7:
D[Ii] = Vi
8:
continue
9:
else
10:
if ci == Pedestrian Crossing then
11:
D[Ii] = MergeCrossing(D[Ii], Vi) // Merge crossing by finding the con-
vex hull that contains all points in D[Ii] and Vi
12:
else if ci == Lane Divider then
13:
D[Ii] = MergeDivider(D[Ii], Vi) // Merge divider by interpolating D[Ii]
and Vi
14:
else if ci == Road Boundary then
15:
D[Ii] = MergeBoundary(D[Ii], Vi) // Merge boundary by interpolating
D[Ii] and Vi
16:
end if
17:
end if
18:
end for
19: end for
D.1
Full C-mAP results
As discussed in §B.2, the track extraction algorithm is more robust to temporal
inconsistency in the reconstructions when using higher look-back parameters.
Table 6 and Table 7 in this appendix extend the Table 1 and Table 2 of the main
paper by providing C-mAP results with different look-back parameters. The first
row of each method is the same as the results reported in the main paper, and
MapTracker directly uses the predicted track. §D.3 contains qualitative results
with different look-back parameters. We analyze the results of the three methods
below.
MapTRv2 gets huge boosts on C-mAP with increased look-back parameters,
especially on the nuScenes dataset. This suggests that MapTRv2 suffers from
poor temporal consistency, and the predicted road elements frequently disappear
and reappear within 2 or 3 consecutive frames.
StreamMapNet also benefits from higher look-back parameters. Note that we
tried to derive the tracks from StreamMapNet’s hidden query propagation but
found almost no temporal correspondence – very few propagated elements stay
positive in the next frame. This is mainly because the detection-based formu-
lation cannot exploit tracking labels, and the model treats the propagated in-
formation as extra conditions without capturing explicit temporal relationships.
StreamMapNet’s C-mAP results are worse than MapTRv2 on Argoverse2, fur-
ther indicating the limitations of its temporal modeling designs.


## Page 26

26
Chen et al.
Table 6: Full C-mAP on nuScenes [2].†: Epochs for our multi-frame training.
Method
Epoch
Lookback
C-APp C-APd C-APb C-mAP C-mAP
MapTRv2
110
1 frame
55.8
43.8
57.9
50.5
64.9
3 frames
61.5
54.0
61.3
58.9
5 frames
62.5
55.4
62.2
60.0
StreamMapNet
110
1 frame
58.6
53.5
57.1
56.4
65.9
3 frames
62.8
59.7
58.9
60.5
5 frames
63.1
60.8
59.3
61.0
MapTracker
72†
∅(predicted)
75.4
65.0
66.9
69.1
72.5
1 frame
75.5
65.9
67.6
69.7
3 frames
76.3
66.8
68.2
70.4
5 frames
76.9
67.0
68.4
70.7
Table 7: Full C-mAP on Argoverse2 [37]. †: Epochs for our multi-frame training.
Method
Epoch
Lookback
C-APp C-APd C-APb C-mAP C-mAP
MapTRv2
24*4
1 frame
58.4
52.5
57.4
56.1
67.7
3 frames
63.2
62.1
62.8
62.7
5 frames
63.9
64.1
63.0
63.7
StreamMapNet
72
1 frame
63.0
53.3
56.2
57.5
65.8
3 frames
65.5
58.8
58.9
61.0
5 frames
65.6
59.5
59.0
61.4
MapTracker
35†
∅(predicted)
70.8
68.3
66.0
68.3
72.8
1 frame
72.6
69.5
67.4
69.8
3 frames
73.2
71.0
68.3
70.8
5 frames
73.4
71.3
68.3
71.0
MapTracker predicts tracks and obtains good results without the track extrac-
tion algorithm. Note that the track extraction algorithm and our VEC module
use different thresholds for determining positive road elements. Our VEC mod-
ule uses higher thresholds and output fewer positive elements, leading to slightly
lower C-mAP compared to the result of using the track extraction algorithm
with N = 1. When increasing the look-back parameters, the C-mAP of Map-
Tracker can also keep improving – Although MapTracker obtains much more
consistent reconstructions than the baselines, the predicted temporal correspon-
dences are sometimes incorrect, and road elements are still occasionally unstable
(i.e., disappear and reappear within several frames).
As explained in §B.3, C-mAP is the upper bound of C-mAP when the recon-
structions pass all consistency checks. MapTracker gets very close to the C-mAP
when we use the track extraction algorithm with N = 5 to trade running time
for track quality – The gap (1.8) is much smaller than the gap of the baselines,
again demonstrating our superior consistency.


## Page 27

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
27
D.2
Check MapTR ground truth
Table 8 investigates the quality of MapTR’s ground truth by evaluating its data
on our consistent benchmarks. The tracks of MapTR’s ground truth are ex-
tracted using Algorithm 1 with look-back parameter 1. The results in the table
are consistent with what we have analyzed in §B.1: 1) the pedestrian crossings
of MapTR data suffer from temporal inconsistencies on both datasets; 2) the
dividers have severe issues (e.g., entirely dropped) on Argoverse2.
Table 8: Evaluating MapTR’s ground-truth data with our consistent benchmarks.
The goal is to understand the temporal consistency of MapTR’s ground truth.
C-APp C-APd C-APb C-mAP
nuScenes
80.6
100
100
93.5
Argoverse2
95.6
65.7
100
87.1
According to the table, we observe failure in Pedestrian Crossing for both
datasets and severe misalignment in Argoverse2, which matches the conclusion
of our observation mentioned in the main paper.
D.3
More qualitative results
Figure 7 to Figure 12 present additional qualitative comparisons. We show two
additional rows for each example compared to Figure 4 of the main paper: (the
second row, “Merged LB5” is the merged results for all the methods when
using the track extraction algorithm with look-back parameter N = 5; (the
third row, “Unmerged”) is the raw unmerged results that simply place the
reconstructions of all frames together. For the first row, MapTracker uses the
predicted tracks while the baselines use the track extraction algorithm with
look-back parameter N = 1.
Note that since our VEC module and the track extraction algorithm use dif-
ferent thresholds for determining the positive predictions, MapTracker’s results
in the first and second rows of each example can be slightly different. The sec-
ond row of MapTracker sometimes has more positive road elements than the first
row, and we use the predicted tracks to plot the unmerged results. Comparing
each row of each example, MapTracker’s results are cleaner and more consistent,
further validating our contributions toward consistent vector HD mapping.


## Page 28

28
Chen et al.
MapTracker (Ours)
MapTRv2
StreamMapNet
Ground Truth
Merged
Merged LB5
Unmerged
Merged
Merged LB5
Unmerged
Merged
Merged LB5
Unmerged
Fig. 7: Additional qualitative results on the nuScenes dataset.


## Page 29

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
29
MapTracker (Ours)
MapTRv2
StreamMapNet
Ground Truth
Merged
Merged LB5
Unmerged
Merged
Merged LB5
Unmerged
Merged
Merged LB5
Unmerged
Fig. 8: Additional qualitative results on the nuScenes dataset.


## Page 30

30
Chen et al.
MapTracker (Ours)
MapTRv2
StreamMapNet
Ground Truth
Merged
Merged LB5
Unmerged
Merged
Merged LB5
Unmerged
Merged
Merged LB5
Unmerged
Fig. 9: Additional qualitative results on the nuScenes dataset.


## Page 31

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
31
MapTracker (Ours)
MapTRv2
StreamMapNet
Ground Truth
Merged
Merged LB5
Unmerged
Merged
Merged LB5
Unmerged
Merged
Merged LB5
Unmerged
Fig. 10: Additional qualitative results on the Argoverse2 dataset.


## Page 32

32
Chen et al.
MapTracker (Ours)
MapTRv2
StreamMapNet
Ground Truth
Merged
Merged LB5
Unmerged
Merged
Merged LB5
Unmerged
Merged
Merged LB5
Unmerged
Fig. 11: Additional qualitative results on the Argoverse2 dataset.


## Page 33

Tracking with Strided Memory Fusion for Consistent Vector HD Mapping
33
MapTracker (Ours)
MapTRv2
StreamMapNet
Ground Truth
Merged
Merged LB5
Unmerged
Merged
Merged LB5
Unmerged
Merged
Merged LB5
Unmerged
Fig. 12: Additional qualitative results on the Argoverse2 dataset.

