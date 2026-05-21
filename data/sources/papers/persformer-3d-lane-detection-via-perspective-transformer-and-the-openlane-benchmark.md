# PersFormer: 3D Lane Detection via Perspective Transformer and the OpenLane Benchmark

**Source**: arXiv:2203.11089

**Type**: Academic Paper

---

## Page 1

PersFormer: 3D Lane Detection via Perspective
Transformer and the OpenLane Benchmark
Li Chen1∗†, Chonghao Sima1∗, Yang Li1∗, Zehan Zheng1, Jiajie Xu1,
Xiangwei Geng1, Hongyang Li1,2†, Conghui He1, Jianping Shi3, Yu Qiao1, and
Junchi Yan1,2
1 Shanghai AI Laboratory
2 Shanghai Jiao Tong University
3 SenseTime Research
{lichen,simachonghao,liyang,lihongyang}@pjlab.org.cn
yanjunchi@sjtu.edu.cn
Abstract. Methods for 3D lane detection have been recently proposed
to address the issue of inaccurate lane layouts in many autonomous driv-
ing scenarios (uphill/downhill, bump, etc.). Previous work struggled in
complex cases due to their simple designs of the spatial transformation
between front view and bird’s eye view (BEV) and the lack of a real-
istic dataset. Towards these issues, we present PersFormer: an end-to-
end monocular 3D lane detector with a novel Transformer-based spatial
feature transformation module. Our model generates BEV features by
attending to related front-view local regions with camera parameters
as a reference. PersFormer adopts a unified 2D/3D anchor design and
an auxiliary task to detect 2D/3D lanes simultaneously, enhancing the
feature consistency and sharing the benefits of multi-task learning. More-
over, we release one of the first large-scale real-world 3D lane datasets:
OpenLane, with high-quality annotation and scenario diversity. Open-
Lane contains 200,000 frames, over 880,000 instance-level lanes, 14 lane
categories, along with scene tags and the closed-in-path object annota-
tions to encourage the development of lane detection and more industrial-
related autonomous driving methods. We show that PersFormer signifi-
cantly outperforms competitive baselines in the 3D lane detection task on
our new OpenLane dataset as well as Apollo 3D Lane Synthetic dataset,
and is also on par with state-of-the-art algorithms in the 2D task on
OpenLane. The project page is available at https://github.com/OpenP
erceptionX/PersFormer 3DLane and OpenLane dataset is provided at
https://github.com/OpenPerceptionX/OpenLane.
1
Introduction
Autonomous driving is one of the most successful applications for AI algorithms
to deploy in recent years. Modern Advanced Driver Assistance Systems (ADAS)
for either L2 or L4 routes provide functionalities such as Automated Lane Cen-
tering (ALC) and Lane Departure Warning (LDW), where the essential need
∗Equal contribution. † Correspondence author.
arXiv:2203.11089v3  [cs.CV]  19 Jul 2022


## Page 2

2
L. Chen et al.
for perception is a lane detector to generate robust and generalizable lane lines
[13]. With the prosperity of deep learning, lane detection algorithms in the 2D
image space has achieved impressive results [55,35,48], where the task is for-
mulated as a 2D segmentation problem given front view (perspective) image as
input [29,44,41,1]. However, such a framework to perform lane detection in the
perspective view is not applicable for industry-level products where complicated
scenarios dominate.
On one side, downstream modules as in planning and control often require
the lane location to be in the form of the orthographic bird’s eye view (BEV)
instead of a front view representation. Representation in BEV is for better task
alignment with interactive agents (vehicle, road marker, traffic light, etc.) in
the environment and multi-modal compatibility with other sensors such as Li-
DAR and Radar. The conventional approaches to address such a demand are
either to simply project perspective lanes to ones in the BEV space [61,39], or
more elegantly to cast perspective features to BEV by aid of camera in/extrinsic
matrices [16,20,70]. The latter solution is inspired by the spatial transformer
network (STN) [24] to generate a one-to-one correspondence from the image to
BEV feature grids. By doing so, the quality of features in BEV depends solely
on the quality of the corresponding feature in the front view. The predictions
using these outcome features are not adorable as the blemish of scale variance
in the front view, which inherits from the camera’s pinhole model, remains.
On the other side, the height1 of lane lines has to be considered when we
project perspective lanes into BEV space. As illustrated in Fig. 1, the lanes
would diverge/converge in case of uphill/downhill if the height is ignored, lead-
ing to improper action decisions as in the planning and control module. Previous
literature [61,41,53] inevitably hypothesize that lanes in the BEV space lie on a
flat ground, i.e., the height of lanes is zero. The planar assumption does not hold
true in most autonomous driving scenarios, e.g., uphill/downhill, bump, crush
turn, etc. Since the height information is unavailable on public benchmarks or
complicated to acquire accurate ground truth, 3D lane detection is ill-posed.
There are some attempts to address this issue by creating 3D synthetic bench-
marks [16,20]. Their performance still needs improvement in complex, realistic
scenarios nonetheless (c.f. (b-c) in Fig. 1). Moreover, the domain adaption be-
tween simulation and real data is not well-studied [17].
To address these bottlenecks aforementioned, we propose Perspective Trans-
former, shortened as PersFormer, which has a spatial feature transformation
module to generate better BEV representations for the task. The proposed frame-
work unifies 2D/3D lane detection tasks, and substantiates performance on the
proposed large-scale realistic 3D lane dataset, OpenLane.
First, we model the spatial feature transformation as a learning procedure
that has an attention mechanism to capture the interaction both among local
region in the front view feature and between two views (front view to BEV),
1 We define the height of lane line z to be the relative height concerning the zero point
in the ego vehicle coordinate system (x, y, z) in BEV 3D space. The coordinate of
the perspective (front view) 2D space in the image plane is referred to as (u, v).


## Page 3

PersFormer and OpenLane
3
Fig. 1. Motivation of performing lane detection from 2D in (a) to BEV in (b); and
the superiority of our method in (c) versus (b). Lanes would diverge/converge in pro-
jected BEV on planar assumption, and a 3D solution with height to be considered can
accurately predict the parallel topology in this case
consequently being able to generate a fine-grained BEV feature representation.
Inspired by [60,8], we construct a Transformer-based module to realize this,
while the deformable attention mechanism [72] is adopted to remarkably reduce
the computational memory requirement and dynamically adjust keys through
the cross-attention module to capture prominent feature among the local re-
gion. Compared with direct 1-1 transformation via Inverse Perspective Mapping
(IPM), the resultant features would be more representative and robust as it at-
tends to the surrounding local context and aggregates relevant information. We
further aim at unifying 2D and 3D lane detection tasks to benefit from the co-
learning optimization. Second, we release the first real-world, large-scale 3D lane
dataset and corresponding benchmark, OpenLane, to support research into the
problem. OpenLane contains 200,000 annotated frames and over 880,000 lanes
- each with one of 14 category labels (single white dash, double yellow solid,
left/right curbside, etc.), which exceeds all of the existing lane datasets. It also
has some distinguishing elements such as scenes, weather, and closed-in-path-
object (CIPO) for other research topics in autonomous driving.
The main contributions of our work are three-fold: 1) Perspective
Transformer, a novel Transformer-based architecture to realize spatial transfor-
mation of features; 2) An architecture to simultaneously unify 2D and 3D lane
detection, which is feasibly needed in the application. Experiments show that
our PersFormer outperforms state-of-the-art 3D lane detection algorithms; 3)
The OpenLane dataset, the first large-scale realistic 3D lane dataset with high-
quality labeling and vast diversity. The dataset, baselines, as well as the whole
suite of codebase, is released to facilitate the research in this area.
2
Related Work
Vision Transformers in Bird’s-Eye-View (BEV). Projecting features to
BEV and performing downstream tasks in it has become more dominant and
ensured better performance recently [36]. Compared with conventional CNN
structure, the cross attention scheme in Vision Transformers [60,14,8,38,72] is
naturally introduced to serve as a learnable transformation of features across


## Page 4

4
L. Chen et al.
different views in an elegant spirit [36].
Instead of simply projecting features
via IPM, the successful application of Transformers in view transformation has
demonstrated great success in various domains, including 3D object detection
[68,62,19,31], prediction [15,18,43], planning [46,12], etc.
Previous work [16,67,62,50,7] bring the BEV philosophy into pipeline, and
yet they do not consider attention mechanism and/or 3D vision geometry (in this
case, camera parameters). For instance, 3D-LaneNet [16] is set up with camera
in/extrinsic matrices; the IPM process generates a virtual BEV representation
from front view features. DETR3D [62] also considers camera geometry and
formulates a learnable 3D-to-2D query search with attention scheme. However,
there is no explicit BEV modelling for robust feature representation; the ag-
gregated features might not be properly represented in 3D space. To address
these shortcomings, our proposed PersFormer takes into account both the effect
of camera parameters to generate BEV features and the convenience of cross-
attention mechanism to model view transformation, achieving better feature
representation in the end.
Lane Detection Benchmarks. A large-scale, diverse dataset with high-quality
annotation is a pivot for lane detection. Along with the progress of lane detec-
tion approaches, numerous datasets have been proposed [29,23,69,58,4,44,64,10].
However, they usually fit into one or the other lane detection scenario. Tab. 1
depicts more details of the existing benchmarks and their comparison with our
proposed OpenLane dataset. OpenLane is the first large-scale, realistic 3D lane
dataset. It equips with a wide span of diversity in both data distribution and
task applicability.
3D Lane Detection. As discussed in Section 1, planar assumption does not
always reserve in some cases, i.e., uphill/downhill, bump. Several approaches
[40,5,3] utilize multi-modal or multi-view sensors, such as a stereo camera or Li-
DAR, to get the 3D ground topology. However, these sensors have shortages of
high cost in hardware and computation resources, confining their practical appli-
cations. Recently, some monocular methods [16,20,26,37] take a single image and
employ IPM to predict lanes in 3D space. 3D-LaneNet [16] is the pioneering work
in this domain with one simple end-to-end neural network, which adopts STN
[24] to accomplish the spatial projection of features. Gen-LaneNet [20] builds on
top of 3D-LaneNet and designs a two-stage network for decoupling the segmen-
tation encoder and 3D lane prediction head. These two approaches [16,20] suffer
from improper feature transformation and unsatisfying performance in curving
or crush turn cases. Confronted with the issues above, we bring in PersFormer
to provide better feature representation and optimize anchor design to unify 2D
and 3D lane detection simultaneously.
3
Methodology
In this section, we propose PersFormer, a unified 2D/3D lane detection frame-
work with Transformer. We first describe the problem formulation, followed by
an introduction to the overall structure in Section 3.1. In Section 3.2, we present


## Page 5

PersFormer and OpenLane
5
Fig. 2. Our proposed PersFormer pipeline. The core is to learn a spatial feature trans-
formation from front view to BEV space so that the generated BEV features at target
point would be more representative by attending local context around reference point.
PersFormer consists of the self-attention module to interact with its own BEV queries;
the cross-attention module that takes the key-value pair from the IPM-based front view
features to generate fine-grained BEV feature
Perspective Transformer, an explicit feature transformation module from front
view to BEV space by the aid of camera parameters. In Section 3.3, we give
details on the anchor design to unify 2D/3D tasks and in Section 3.4 we further
elaborate on the auxiliary task and loss function to finalize our training strategy.
Problem Formulation. Given an input image Iorg ∈RHorg×Worg, the goal
of PersFormer is to predict a collection of 3D lanes L3D = {l1, l2, . . . , lN3D} and
2D lanes L2D = {l1, l2, . . . , lN2D}, where N3D, N2D are the total number of 3D
lanes in the pre-defined BEV range and 2D lanes in the original image space
(front view) respectively. Mathematically, each 3D lane ld is represented by an
ordered set of 3D coordinates:
  l
_
d = \bi g [( x_{1 }, y_{1 } ,  z _{1}) , (x _{2}
,
 y_{2}, z_{2}), \dots , (x_{N_d}, y_{N_d}, z_{N_d}) \big ], \label {eqn: 3d_lane_represent} 
(1)
where d is the lane index, and Nd is the max number of sample points of this
lane. The form of 2D lane is represented similarly with 2D coordinate (u, v)
accordingly. Each lane has a categorical attribute c3D/2D, indicating the type of
this lane (e.g., single-white dash line). Also, for each point in a single 2D/3D
lane, there exists an attribute property indicating whether the point is visible or
not, denoted by visfv/bev as a vector for the lane.
3.1
Approach Overview
The overall structure, as illustrated in Fig. 2, consists of three parts: the back-
bone, the Perspective Transformer, and lane detection heads. The backbone
takes the resized image as input and generates multi-scale front view features,
where the popular ResNet variant [56] is adopted. Note that these features might
suffer from the defect of scale variance, occlusion, etc. - residing from the inher-
ent feature extraction in the front view space. The Perspective Transformer takes
the front view features as input and generates BEV features by the aid of camera
intrinsic and extrinsic parameters. Instead of simply projecting the one-to-one


## Page 6

6
L. Chen et al.
feature correspondence from the front view to BEV, we introduce Transformer
to attend local context and aggregate surrounding features to form a robust
representation in BEV. By doing so, we learn the inverse perspective mapping
from front view to BEV in an elegant manner with Transformer. Finally, the
lane detection heads are responsible for predicting 2D/3D coordinates as well
as lane types. The 2D/3D detection heads are referred to as LaneATT [55] and
3D-LaneNet [16], with modification on the structure and anchor design.
3.2
Proposed Perspective Transformer
We present Perspective Transformer, a spatial transformation method that com-
bines camera parameters and data-driven learning procedures. The general idea
of Perspective Transformer is to use the coordinates transformation matrix from
IPM as a reference to generate BEV feature representation, by attending related
region (local context) in front view feature. On the assumption that the ground
is flat and the camera parameters are given, a classical IPM approach calculates
a set of coordinate mapping from front-view to BEV, where the BEV space is
defined on the flat ground (see [21], Section 8.1.1). Given a point pfv with its co-
ordinate (u, v) in the front-view feature Ffv ∈RHfv×Wfv×C, IPM maps the point
pfv to the corresponding point pbev in BEV, where (x, y) is the coordinate in the
BEV space RHbev×Wbev×C. The transform is achieved with camera in/extrinsic
and can be represented mathematically as:
 
\
b
e
g
i
n  {pma t ri x } x  
\
\
 
y
 
\
\  
0
 
\
e
nd
 
{ pmatrix} = \alpha _{f2b} \cdot R_{\theta } \cdot K^{-1} \cdot \begin {pmatrix} u \\ v \\ 1 \end {pmatrix} + \begin {pmatrix} 0 \\ 0 \\ -h \end {pmatrix}, \label {Enq: transform} 
(2)
where αf2b implies the scale factor between front-view and BEV, Rθ denotes the
pitch rotation matrix from extrinsic, K is the intrinsic matrix, and h stands for
camera height. Such a transformation in Eqn.(2) enframes a strong prior on the
attention unit in PerFormer to generate more representative BEV features.
The architecture of Perspective Transformer is inspired by popular approaches
such as DETR [8], and consists of the self-attention module and cross-attention
module (see Fig. 2). We differentiate from them in that the queries are not im-
plicitly updated. However, instead, they are piloted by an explicit meaning - the
physical location to detect objects or lanes in BEV. In the self-attention mod-
ule, the output Qbev descends from the triplet (key, value, query) input through
their interaction. The formulation of such a self-attention can be described as:
  Q_ { \text {
bev}
} =
 
\texttt {softmax} \bigg ( \frac {QK^\top }{\sqrt {d_k}} \bigg ) V, 
(3)
where K, Q, V ∈R(Hbev×Wbev×C) are the same query that is pre-defined in BEV,
√dk is the dimensional normalized factor.
In the cross-attention module, the input query Q
′
bev is the outcome of sev-
eral additional layers feeding the self-attention output Qbev as input. Note that
Q
′
bev is an explicit feature representation as to which part in BEV should be


## Page 7

PersFormer and OpenLane
7
Fig. 3.
Generation of keys in the cross
attention. Point (x, y) in BEV space casts
the corresponding point (u, v) in front view
through intermediate state (x
′, y
′); by
learning offsets, the network learns target-
reference points mapping from green rect-
angles to yellow and related blue rectangles
as keys to Transformer
Fig. 4. Unifying anchor design in 2D and
3D. We first put curated anchors (red) in
the BEV space (left), then project them
to the front view (right). Offset xi
k and
ui
k (dashed line) are predicted to match
ground truth (yellow and green) to an-
chors. The correspondence is thus built,
and features are optimized together
paid more attention since the generation of queries is location-sensitive in BEV.
This is quite different compared with queries that do not consider view trans-
formation in most Vision Transformers [62,19,72]. Furthermore, the intuition
behind employing Transformer to map features from front view to BEV is that
such an attention mechanism would automatically attend which part of features
contribute most towards the target point (query) in the destination view. The
direct feature transformation would suffer from camera parameter noise or scale
variance issues, as discussed and illustrated in Section 1. Note that the naive
Transformer cannot be applied directly since the number of key-value pairs is
huge and thus be confined by computational burden. Inspired by Deformable
DETR [72], we attend partial key-value pairs around the local region in a learn-
able manner to save cost and improve efficiency.
Fig. 3 depicts the feature transformation process and the generation of key-
value pairs in cross-attention. Specifically, given a query point (x, y) in the target
BEV map Q
′
bev, we project it to the corresponding point (u, v) in the front view
via Eqn.(2). As does similarly in [72], we learn some offsets based on point (u, v)
to generate a set of most related points around it. These learned points, together
with (u, v) are defined as reference points. They contribute most to the query
point (x, y), defined as target point, in BEV-space. The reference points serve as
the surrounding context in the local region that contributes most to the feature
representation from perspective view to BEV space. They are the desired keys
we try to find, and their features are values for the cross attention module. Note
that the initial locations of reference points from IPM are used as preliminary
locations for the coordinate mapping; the location are adjusted gradually during
the learning procedure, which is the core role of Deformable Attention.
As a result, the output of the cross-attention module can be formulated as:
  F_ { \text {bev}}
 
= \t extt t {DeformAttn}(Q^{'}_{\text {bev}}, F_{\text {fv}}, p_{\text {fv2bev}}), 
(4)


## Page 8

8
L. Chen et al.
where Fbev ∈R(Hbev×Wbev×C) is the final desired features for the subsequent 3D
head to get lane predictions, Q
′
bev denotes the input queries, Ffv ∈R(Hfv×Wfv×C)
indicates the front view features from backbone, and pfv2bev is the IPM-inited
coordinate mapping from front view to BEV space. Considering Ffv and pfv2bev
with the deformable unit, we get the explicit transformed BEV feature Fbev.
To sum up, Perspective Transformer extracts front-view features among the
reference points to construct representative BEV features. As demonstrated in
Section 5, such a feature transformation in an aggregation spirit via Transformer
is proven to perform better than a direct IPM-based projection across views.
3.3
Simultaneous 2D and 3D Lane Detection
Although the main focus in this paper lies in 3D detection, we formulate the
PersFormer framework to detect 2D and 3D lanes in one shot. On one side, 2D
lane detection in the perspective view still draws interest in the community as
part of the general high-level vision problems [1,55,35,48]; on the other side, uni-
fying 2D and 3D tasks are naturally feasible since the BEV features to predict 3D
outputs descend from the counterpart in the 2D branch. An end-to-end unified
framework would leverage features and benefit from the co-learning optimization
process as proven in most multi-task literature [33,59,28].
Unified anchor design. Since our method is anchor-based detection, the
core issue to achieve the unified framework is to integrate anchors in both 2D and
3D. Unfortunately, anchors in these two domains usually do not share similar
distribution. For example, the popular 2D approach LaneATT [55] settles too
many anchors, spanning different directions in the image; while the recent 3D
work Gen-LaneNet [20] puts too few anchors, which are parallel and sparse
in BEV. Based on these observations, we thereby design anchors such that the
redesigned anchors could leverage the network to optimize shared features across
two domains. We start with several groups of anchors (here, the group number
is set to 7) sampled with different incline angles in the BEV space and then
projected to the front view. Fig. 4 elaborates on the integration of 2D and 3D
anchors. Below we describe how the lane line is modeled via anchors.
3D anchor design. To match ground truth lanes tightly, the anchors are
placed approximately longitudinal along x-axis, with an incline angle φ. As de-
noted in Fig. 4(left), the initial line (equally spaced) with staring position along
x-axis is denoted by Xi
bev for each anchor i. Similar to anchor regression in
object detection, the network predicts the relative offset xi w.r.t. the initial po-
sition Xi
bev; hence the resultant lane prediction along x-axis is (xi + Xi
bev). As
indicated in Eqn.(1), each lane is represented as a number of Nd points. The
prediction head generates three vectors related to lane shape as follows:
  (\ mat hbf 
{x}^ i , \mathbf  {z}^i,  \mathbf
 {v is}^
i_{\text {bev}}) = \{ (x^{(i,k)}, z^{(i,k)}, \text {vis}^{(i,k)}_{\text {bev}} ) \}^{N_d}_{k=1} 
(5)
where zi is the lane height in 3D sense, the binary vis(i,k)
bev denotes the visibility
of each location k in lane i, which controls the endpoint or length of a lane. Note
that the lane position along y-axis does not need to be predicted since each y


## Page 9

PersFormer and OpenLane
9
value of the Nd samples in a lane is pre-defined - we predict the x(i,k) value
at the corresponding (fixed) y location. To sum up, the description of a lane’s
location in the world coordinate system is denoted as (xi + Xi
bev, y, zi).
2D anchor design. The anchor description and prediction are similar to
those defined in 3D view, except that the (u, v) is in 2D space and there is no
height (see Fig. 4(right)). We omit the detailed notations for brevity. It is worth
mentioning that each 3D anchor Xi
bev with an incline angle φ corresponds to a
specific 2D anchor U i
fv with the incline angle θ; the connection is built via the
projection in Eqn.(2). We achieve the goal of unifying 2D and 3D tasks simulta-
neously by setting the same set of anchors. Such a design would optimize features
together and features being more aligned and representative across views.
3.4
Prediction Loss
Binary Segmentation under BEV. As do in many preceding work [63,42,23],
adding more intermediate supervision into the network training would boost the
performance of network. Since lane detection belongs to image segmentation
and requires general large resolution, we concatenate a U-Net structure [49]
head on top of the generated BEV features. Such an auxiliary task is to predict
lanes in BEV, but instead in a conventional 2D segmentation manner, aiming for
better feature representation for the main task. The ground truth Sgt is a binary
segmentation map projected from 3D lane ground truth to the BEV space. The
prediction output is denoted by Spred and owns the same size as Sgt.
Loss function. Equipped with the anchor representation and segmentation
head aforementioned, we summarize the overall loss. Given an image input and
its ground truth labels, it finally computes a sum of all anchors’ loss; the loss
is a combination of the 2D lane detection, 3D lane detection and intermediate
segmentation with learnable weights (α, β, γ) accordingly:
 \
l
a
bel {eq
n:t ota l_lo
ss}  \m at hca
l { L} = \ sum 
_i \ a lpha \mathcal {L}_{ \text {2D} }( c^i_{ \text {2D} }, \mathbf {u}^i, \mathbf {vis}^i_{\text {fv}} ) + \beta \mathcal {L}_{ \text { 3D } } ( c^i_{ \text {3D} }, \mathbf {x}^i, \mathbf {z}^i, \mathbf {vis}^i_{\text {bev}} ) + \gamma \mathcal {L}_{ \text {seg}} (S_{\text {pred}}), 
(6)
where ci
(·) is the predicted lane category in 2D and 3D domain respectively.
The loss input above shows the prediction part only; we omit the ground truth
notation for brevity. The loss of lane category classification for the 2D/3D task
is the cross-entropy; the loss of lane shape regression is the l1 norm; the loss of
lane visibility prediction is the binary cross-entropy loss. The loss of the auxiliary
task is a binary cross-entropy loss between two segmentation maps.
4
OpenLane: A Large-scale Realistic 3D Lane Benchmark
4.1
Highlights over Previous Benchmarks
OpenLane is the first real world 3D lane dataset and the largest scale to date
compared with existing benchmarks. We construct OpenLane on top of the influ-
ential Waymo Open dataset [54], following the same data format and evaluation


## Page 10

10
L. Chen et al.
Table 1. Comparison of OpenLane with existing benchmarks. “Avg. Length” denotes
the average time duration of segments. “Inst. Anno.” indicates whether lanes are anno-
tated instance-wise (c.f. semantic-wise). “Track. Anno.” implies if a lane has a unique
tracking ID. Numbers in ‘#Frames’ are the number of annotated frames / total frames
respectively. Details of “Scenario” can be found in Appendix
Dataset
#Segments
#Frames
Avg.
Length
Inst.
Anno.
Track.
Anno.
Max
#Lanes
Line
Category Scenario
Caltech Lanes [2]
4
1224/1224
-
✓
✗
4
-
Easy
TuSimple [58]
6.4K
6.4K/128K
1s
✓
✗
5
-
Easy
3D Synthetic [20]
-
10K/10K
-
✓
-
6
-
Easy
VIL-100 [71]
100
10K/10K
10s
✓
✗
6
10
Medium
VPG [29]
-
20K/20K
-
✗
-
-
7
Medium
OpenDenseLane [10]
1.7K
57K/57K
-
✓
✗
-
4
Medium
LLAMAS [4]
14
79K/100K
-
✓
✗
4
-
Easy
ApolloScape [23]
235
115K/115K
16s
✗
✗
-
13
Medium
BDD100K [69]
100K
100K/120M
40s
✗
✗
-
11
Medium
CULane [44]
-
133K/133K
-
✓
-
4
-
Medium
CurveLanes [64]
-
150K/150K
-
✓
-
9
-
Medium
ONCE-3DLanes [66]
-
211K/211K
-
✓
-
8
-
Medium
OpenLane
1K
200K/200K
20s
✓
✓
24
14
Hard
pipeline - leveraging existent practice in the community so that users would not
handle additional rules for a new benchmark. Tab. 1 compares OpenLane with
existing counterparts in various aspects. In short, OpenLane owns 200K frames
and over 880K carefully annotated lanes, 33% and 35% more compared with
existing largest lane dataset CurveLanes [64] respectively, with rich annotations.
We annotate all the lanes in each frame, including those in the opposite di-
rection if no curbside exists in the middle. Due to the complicated lane topology,
e.g., intersection/roundabout, one frame could contain as many as 24 lanes in
OpenLane. Statistically, about 25% frames of OpenLane have more than 6 lanes,
which exceeds the maximum number in most lane datasets. 14 lane categories
are annotated alongside to cover a wide range of lane types in most scenarios,
including road edges. Double yellow solid lanes, single white solid and dash lanes
take up almost 90% of total lanes. This is imbalanced, and yet it falls into a long-
tail distribution problem, which is common in realistic scenarios. In addition to
the lane detection task, we also annotate: (a) scene tags, such as weather and
locations; (b) the closest-in-path object (CIPO), which is defined as the most
concerned target w.r.t. ego vehicle; such a tag is quite pragmatic for subsequent
modules as in planning/control, besides a whole set of objects from perception.
An annotation example is provided in Fig. 5(d), along with some typical samples
in existing 2D lane datasets in Fig. 5(a-c). The detailed statistics, annotation
criterion and visualization can be found in Appendix.
4.2
Generation of High-quality Annotation
Building a real-world 3D lane dataset has challenges mainly in an accurate lo-
calization system and occlusions. We compare several popular sensor datasets
[9,54,6] by projecting 3D object annotations to image planes and constructing 3D


## Page 11

PersFormer and OpenLane
11
`
Scene: Suburbs
Weather: Clear
Hours: Dawn/Dusk
CIPO
R.Curb
L.Curb
1-W dash
L-Y dash
R-Y solid
L-Y solid
R-Y dash
(a) TuSimple
(b) ApolloScape
(c) CurveLanes
(d) OpenLane
Fig. 5. Annotation samples
of OpenLane compared with
other lane datasets. Open-
Lane is challenging with more
lane categories per frame in
average
and
has
rich
la-
bels including scene, weather,
hours, CIPO
scene maps using both learning-based [57] or SLAM algorithms [51,52]. The re-
construction precision and scalability of Waymo Open Dataset [54] outperforms
other candidates, leading to employing it as our basis.
Primarily, we generate the necessary high-quality 2D lane labels. They con-
tain the final annotations of tracking ID, category, and 2D points ground truth.
Then for each frame, the point clouds are first filtered with the original 3D
object bounding boxes and then projected back into the corresponding image.
We further keep those points related to 2D lanes only with a certain threshold.
However, the output directly after a static threshold filtering could lead to an
unsatisfying ground truth due to the perspective scaling issue. To solve this and
keep the slender shape of lanes, we use the filtered point clouds to interpolate
the 3D position for each point in 2D annotations. Afterward, with the help of
the localization system, 3D lane points in frames within a segment could be
spliced into long, high-density lanes. This process could bring some unreason-
able parts into the current frame; thus, points in one lane whose 2D projections
are higher than the ending position of its 2D annotation are labeled as invisible.
A smoothing step is ultimately deployed to filtrate any outliers and generate the
3D labeling results. We omit some technical details, such as how to deal with a
large U-turn during smoothing, and we refer the audience to Appendix.
5
Experiments
We examine PersFormer on two 3D lane benchmarks, the newly proposed real-
world OpenLane dataset, and the synthetic Apollo dataset. For both 3D lane
datasets, we follow the evaluation metrics designed by Gen-LaneNet [20], with
additional category accuracy on OpenLane dataset. For the 2D task, the classical
metric in CULane [44] is adopted. We put correlated details in Appendix.
5.1
Results on OpenLane
We provide 3D and 2D evaluation results on the proposed OpenLane dataset. In
order to evaluate the models thoroughly, we report F-Score on the entire valida-
tion set and different scenario sets. The scenario sets are selected from the entire
validation set based on the scene tags of each frame. In Tab. 2, PersFormer gets
the highest F-Score on the entire validation set and every scenario set, surpassing


## Page 12

12
L. Chen et al.
Table 2. Comparison with other open-sourced 3D methods on OpenLane. PersFormer
achieves the best F-Score on the entire validation set and every scenario set
Method
All
Up &
Down
Curve
Extreme
Weather
Night
Intersection Merge &
Split
3D-LaneNet [16]
44.1
40.8
46.5
47.5
41.5
32.1
41.7
Gen-LaneNet [20]
32.3
25.4
33.5
28.1
18.7
21.4
31.0
PersFormer (ours)
50.5
42.4
55.6
48.6
46.6
40.0
50.7
Table 3. Comparison with state-of-the-art 2D method on OpenLane. The result from
the 2D head of PersFormer also achieves competitive performance
Method
All
Up &
Down
Curve
Extreme
Weather
Night
Intersection Merge &
Split
LaneATT-S [55]
28.3
25.3
25.8
32.0
27.6
14.0
24.3
LaneATT-M [55]
31.0
28.3
27.4
34.7
30.2
17.0
26.5
CondLaneNet-S [35]
52.3
55.3
57.5
45.8
46.6
48.4
45.5
CondLaneNet-M [35]
55.0
58.5
59.4
49.2
48.6
50.7
47.8
CondLaneNet-L [35]
59.1
62.1
62.9
54.7
51.0
55.7
52.3
PersFormer (ours)
42.0
40.7
46.3
43.7
36.1
28.9
41.2
Table 4. Comprehensive 3D Lane evaluation under different metrics. On the strength
of unified anchor design, PersFormer outperforms previous 3D methods on the metrics
of far error while retains comparable results on near error (m). ∗denotes projecting
2D lane results from CondLaneNet [35] to BEV using IPM
Method
F-Score
Category
Accuracy
X error near
X error far
Z error near
Z error far
3D-LaneNet [16]
44.1
-
0.479
0.572
0.367
0.443
Gen-LaneNet [20]
32.3
-
0.591
0.684
0.411
0.521
Cond-IPM∗
36.6
-
0.563
1.080
0.421
0.892
PersFormer (ours)
50.5
92.3
0.485
0.553
0.364
0.431
previous SOTA methods in varying degrees. In Tab. 3, PersFormer outperforms
LaneATT [55], which is our baseline 2D method, by 11%. Detailed comparison
with previous 3D SOTAs is presented in Tab. 4. PersFormer outperforms the
previous best method in F-Score by 6.4%, realizes satisfying accuracy on the
classification of lane type, and presents the first baseline result. Note that Pers-
Former is not satisfying on the metric of near error on x-axis. This is probably
because the unified anchor design is more suitable in fitting the main body of a
lane rather than the starting point. Qualitative results are shown in Fig. 6, indi-
cating that PersFormer is good at catching dense and unapparent lanes in usual
autonomous driving scenes. Overall, PersFormer reaches the best performance
on 3D lane detection and gains remarkable improvement in 2D on OpenLane.
5.2
Results on Apollo 3D Synthetic
We evaluate PersFormer on Apollo 3D Lane Synthetic dataset [20]. In Tab. 5,
while limited by the scale of the dataset (10K frames), our PersFormer still


## Page 13

PersFormer and OpenLane
13
Fig. 6. Qualitative results of PersFormer(a), 3D-LaneNet(b) [16], and Gen-LaneNet(c)
[20]. Under a straight road scenario, PersFormer can provide lane-type information and
even detect subtle curbside while other methods are missing it
Table 5. Comparison with previous 3D methods on Apollo 3D Lane Synthetic. Pers-
Former achieves best F-Score on every scene set with comparable X/Z error (m)
Scene
Method
F-Score
X error near
X error far
Z error near
Z error far
Balanced
Scenes
3D-LaneNet [16]
86.4
0.068
0.477
0.015
0.202
Gen-LaneNet [20]
88.1
0.061
0.496
0.012
0.214
3D-LaneNet(l/att) [26]
91.0
0.082
0.439
0.011
0.242
Gen-LaneNet(l/att) [26]
90.3
0.080
0.473
0.011
0.247
CLGo [37]
91.9
0.061
0.361
0.029
0.250
PersFormer (ours)
92.9
0.054
0.356
0.010
0.234
Rarely
Observed
3D-LaneNet [16]
72.0
0.166
0.855
0.039
0.521
Gen-LaneNet [20]
78.0
0.139
0.903
0.030
0.539
3D-LaneNet(l/att) [26]
84.1
0.289
0.925
0.025
0.625
Gen-LaneNet(l/att) [26]
81.7
0.283
0.915
0.028
0.653
CLGo [37]
86.1
0.147
0.735
0.071
0.609
PersFormer (ours)
87.5
0.107
0.782
0.024
0.602
Vivual
Variants
3D-LaneNet [16]
72.5
0.115
0.601
0.032
0.230
Gen-LaneNet [20]
85.3
0.074
0.538
0.015
0.232
3D-LaneNet(l/att) [26]
85.4
0.118
0.559
0.018
0.290
Gen-LaneNet(l/att) [26]
86.8
0.104
0.544
0.016
0.294
CLGo [37]
87.3
0.084
0.464
0.045
0.312
PersFormer (ours)
89.6
0.074
0.430
0.015
0.266
achieves the best F-Score on every scene set. In terms of X/Z error, our model
gets comparable results compared to previous methods.
5.3
Ablation Study
We present ablation studies on the anchor design, multi-task strategy, transformer-
based view transformation, and auxiliary segmentation task. We mainly report
the improvement on 3D lane detection and provide related results on 2D task.
Anchor design and multi-task. Starting with a pure 3D lane detection
framework (similar to 3D-LaneNet [16]), PersFormer gains 1.7% by adopting
multi-task scheme (Exp.2) and 0.98% with new anchor design (Exp.4) respec-


## Page 14

14
L. Chen et al.
Table 6. Ablative Study on a 300 segments subset of OpenLane. Exp.1 is the baseline
3D method, growing with anchor design and multi-task learning (Exp.2-5). The per-
formance culminates with our spatial feature transformation module and explicit BEV
supervision (Exp.6,7)
Exp. Unified
Anchor
3D
Det
2D
Det
Perspective
Transformer
Binary
Seg
3D F-Score
2D F-Score
1
✓
41.77
-
2
✓
✓
43.49
32.33
3
✓
✓
-
34.90
4
✓
✓
42.75
-
5
✓
✓
✓
44.29
34.98
6
✓
✓
✓
✓
46.62
37.00
7
✓
✓
✓
✓
✓
47.79
42.00
tively. By jointly using the new anchor and multi-task trick, PersFormer acquires
an improvement of 2.5% in 3D task and 2.6% in 2D task (Exp.5).
Spatial feature transformation. By using Perspective Transformer with
the new anchor design, the improvement increases to 4.9% (Exp.6), almost
doubling the previous improvement. Adding auxiliary binary segmentation task
further brings an improvement to 6.02% (Exp.7), which is our complete model.
These ablations support our assumption that PersFormer indeed generates a
fine-grained BEV feature, and the spatial feature transformation does illustrate
its importance in 3D lane detection task. Surprisingly, a better BEV feature
helps 2D task a lot as well, improving 9.7% (Exp.7).
6
Conclusions
In this paper, we have proposed Persformer, a novel Transformer-based 2D/3D
lane detector, along with OpenLane, a large-scale realistic 3D lane dataset. We
demonstrate experimentally that a fine-grained BEV feature with explicit prior
and supervision can significantly improve the performance of lane detection.
Meanwhile, a large-scale real-world 3D lane dataset effectively align the demand
from both the academic and the industrial side.
Acknowledgments
The project is partially supported by the Shanghai Committee of Science and
Technology (Grant No. 21DZ1100100). This work was supported in part by
National Key Research and Development Program of China (2020AAA0107600),
Shanghai Municipal Science and Technology Major Project (2021SHZDZX0102).
We would like to acknowledge the great support from SenseBee labelling team
at SenseTime Research, constructive contribution from Zihan Ding at BUAA,
and the fruitful discussions and comments for this project from Zhiqi Li, Yuenan
Hou, Yu Liu, Jing Shao, Jifeng Dai.


## Page 15

PersFormer and OpenLane
15
References
1. Abualsaud, H., Liu, S., Lu, D.B., Situ, K., Rangesh, A., Trivedi, M.M.: Laneaf:
Robust multi-lane detection with affinity fields. RA-L (2021) 2, 8, 19
2. Aly, M.: Real time detection of lane markers in urban streets. In: IV (2008) 10, 19
3. Bai, M., Mattyus, G., Homayounfar, N., Wang, S., Lakshmikanth, S.K., Urtasun,
R.: Deep multi-sensor lane detection. In: IROS (2018) 4
4. Behrendt, K., Soussan, R.: Unsupervised labeled lane markers using maps. In:
ICCV (2019) 4, 10, 19
5. Benmansour, N., Labayrade, R., Aubert, D., Glaser, S.: Stereovision-based 3d lane
detection system: a model driven approach. In: ITSC (2008) 4
6. Caesar, H., Bankiti, V., Lang, A.H., Vora, S., Liong, V.E., Xu, Q., Krishnan, A.,
Pan, Y., Baldan, G., Beijbom, O.: nuscenes: A multimodal dataset for autonomous
driving. In: CVPR (2020) 10
7. Can, Y.B., Liniger, A., Paudel, D.P., Van Gool, L.: Structured bird’s-eye-view
traffic scene understanding from onboard images. In: ICCV (2021) 4
8. Carion, N., Massa, F., Synnaeve, G., Usunier, N., Kirillov, A., Zagoruyko, S.: End-
to-end object detection with transformers. In: ECCV (2020) 3, 6, 28
9. Chang, M.F., Lambert, J., Sangkloy, P., Singh, J., Bak, S., Hartnett, A., Wang,
D., Carr, P., Lucey, S., Ramanan, D., et al.: Argoverse: 3d tracking and forecasting
with rich maps. In: CVPR (2019) 10
10. Chen, X., Liao, W., Liu, B., Yan, J., He, T.: Opendenselane: a new lidar-based
dataset for hd map construction. In: ICME (2022) 4, 10
11. Chen, Z., Liu, Q., Lian, C.: Pointlanenet: Efficient end-to-end cnns for accurate
real-time lane detection. In: IV (2019) 19, 20
12. Chitta, K., Prakash, A., Geiger, A.: Neat: Neural attention fields for end-to-end
autonomous driving. In: ICCV (2021) 4
13. Comma.ai: Openpilot. https://github.com/commaai/openpilot 2
14. Dosovitskiy, A., Beyer, L., Kolesnikov, A., Weissenborn, D., Zhai, X., Unterthiner,
T., Dehghani, M., Minderer, M., Heigold, G., Gelly, S., Uszkoreit, J., Houlsby, N.:
An image is worth 16x16 words: Transformers for image recognition at scale. In:
ICLR (2021) 3
15. Gao, J., Sun, C., Zhao, H., Shen, Y., Anguelov, D., Li, C., Schmid, C.: Vectornet:
Encoding hd maps and agent dynamics from vectorized representation. In: CVPR
(2020) 4
16. Garnett, N., Cohen, R., Pe’er, T., Lahav, R., Levi, D.: 3d-lanenet: End-to-end 3d
multiple lane detection. In: ICCV (2019) 2, 4, 6, 12, 13, 20, 21, 28, 29, 31, 32, 33
17. Garnett, N., Uziel, R., Efrat, N., Levi, D.: Synthetic-to-real domain adaptation for
lane detection. In: ACCV (2020) 2
18. Gu, J., Sun, C., Zhao, H.: Densetnt: End-to-end trajectory prediction from dense
goal sets. In: ICCV (2021) 4
19. Guan, T., Wang, J., Lan, S., Chandra, R., Wu, Z., Davis, L., Manocha, D.: M3detr:
Multi-representation, multi-scale, mutual-relation 3d object detection with trans-
formers. In: WACV (2022) 4, 7
20. Guo, Y., Chen, G., Zhao, P., Zhang, W., Miao, J., Wang, J., Choe, T.E.: Gen-
lanenet: A generalized and scalable approach for 3d lane detection. In: ECCV
(2020) 2, 4, 8, 10, 11, 12, 13, 19, 20, 21, 27, 28, 29, 30, 31, 32, 33
21. Hartley, R.I., Zisserman, A.: Multiple View Geometry in Computer Vision. Cam-
bridge University Press, ISBN: 0521540518, second edn. (2004) 6


## Page 16

16
L. Chen et al.
22. Hou, Y., Ma, Z., Liu, C., Loy, C.C.: Learning lightweight lane detection cnns by
self attention distillation. In: ICCV (2019) 19
23. Huang, X., Wang, P., Cheng, X., Zhou, D., Geng, Q., Yang, R.: The apolloscape
open dataset for autonomous driving and its application. TPAMI (2019) 4, 9, 10,
19
24. Jaderberg, M., Simonyan, K., Zisserman, A., et al.: Spatial transformer networks.
In: NeurIPS (2015) 2, 4
25. Jayasinghe, O., Anhettigama, D., Hemachandra, S., Kariyawasam, S., Rodrigo,
R., Jayasekara, P.: Swiftlane: Towards fast and efficient lane detection. In: ICMLA
(2021) 19
26. Jin, Y., Ren, X., Chen, F., Zhang, W.: Robust monocular 3d lane detection with
dual attention. In: ICIP (2021) 4, 13
27. Kingma, D.P., Ba, J.: Adam: A method for stochastic optimization. In: Bengio,
Y., LeCun, Y. (eds.) ICLR (2015) 28
28. Kumar, V.R., Yogamani, S., Rashed, H., Sitsu, G., Witt, C., Leang, I., Milz, S.,
M¨ader, P.: Omnidet: Surround view cameras based multi-task visual perception
network for autonomous driving. RA-L (2021) 8
29. Lee, S., Kim, J., Shin Yoon, J., Shin, S., Bailo, O., Kim, N., Lee, T.H., Seok Hong,
H., Han, S.H., So Kweon, I.: Vpgnet: Vanishing point guided network for lane and
road marking detection and recognition. In: ICCV (2017) 2, 4, 10, 19
30. Li, X., Li, J., Hu, X., Yang, J.: Line-cnn: End-to-end traffic line detection with line
proposal unit. T-ITS (2019) 19, 20
31. Li, Z., Wang, W., Li, H., Xie, E., Sima, C., Lu, T., Yu, Q., Dai, J.: Bevformer:
Learning bird’s-eye-view representation from multi-camera images via spatiotem-
poral transformers. arXiv preprint arXiv:2203.17270 (2022) 4
32. Li, Z.Q., Ma, H.M., Liu, Z.Y.: Road lane detection with gabor filters. In: ISAI
(2016) 19
33. Liang, M., Yang, B., Chen, Y., Hu, R., Urtasun, R.: Multi-task multi-sensor fusion
for 3d object detection. In: CVPR (2019) 8
34. Lin, T.Y., Doll´ar, P., Girshick, R., He, K., Hariharan, B., Belongie, S.: Feature
pyramid networks for object detection. In: CVPR (2017) 20
35. Liu, L., Chen, X., Zhu, S., Tan, P.: Condlanenet: a top-to-down lane detection
framework based on conditional convolution. In: CVPR (2021) 2, 8, 12, 19
36. Liu, P.L.: Monocular bev perception with transformers in autonomous driving.
https://towardsdatascience.com/monocular-bev-perception-with-transfo
rmers-in-autonomous-driving-c41e4a893944 3, 4
37. Liu, R., Chen, D., Liu, T., Xiong, Z., Yuan, Z.: Learning to predict 3d lane shape
and camera pose from a single image via geometry constraints. In: AAAI (2022)
4, 13, 28
38. Liu, Z., Lin, Y., Cao, Y., Hu, H., Wei, Y., Zhang, Z., Lin, S., Guo, B.: Swin trans-
former: Hierarchical vision transformer using shifted windows. In: ICCV (2021)
3
39. Meyer, A., Salscheider, N.O., Orzechowski, P.F., Stiller, C.: Deep semantic lane
segmentation for mapless driving. In: IROS (2018) 2
40. Nedevschi, S., Schmidt, R., Graf, T., Danescu, R., Frentiu, D., Marita, T., Oniga,
F., Pocol, C.: 3d lane detection system based on stereovision. In: ITSC (2004) 4
41. Neven, D., De Brabandere, B., Georgoulis, S., Proesmans, M., Van Gool, L.: To-
wards end-to-end lane detection: an instance segmentation approach. In: IV (2018)
2, 19
42. Newell, A., Yang, K., Deng, J.: Stacked hourglass networks for human pose esti-
mation. In: ECCV (2016) 9


## Page 17

PersFormer and OpenLane
17
43. Ngiam, J., Vasudevan, V., Caine, B., Zhang, Z., Chiang, H.T.L., Ling, J., Roelofs,
R., Bewley, A., Liu, C., Venugopal, A., et al.: Scene transformer: A unified ar-
chitecture for predicting future trajectories of multiple agents. In: ICLR (2021)
4
44. Pan, X., Shi, J., Luo, P., Wang, X., Tang, X.: Spatial as deep: Spatial cnn for
traffic scene understanding. In: AAAI (2018) 2, 4, 10, 11, 19, 28
45. Paszke, A., Gross, S., Massa, F., Lerer, A., Bradbury, J., Chanan, G., Killeen,
T., Lin, Z., Gimelshein, N., Antiga, L., et al.: Pytorch: An imperative style, high-
performance deep learning library. NeurIPS (2019) 28
46. Prakash, A., Chitta, K., Geiger, A.: Multi-modal fusion transformer for end-to-end
autonomous driving. In: CVPR (2021) 4
47. Qin, Z., Wang, H., Li, X.: Ultra fast structure-aware deep lane detection. In: ECCV
(2020) 19
48. Qu, Z., Jin, H., Zhou, Y., Yang, Z., Zhang, W.: Focus on local: Detecting lane
marker from bottom up via key point. In: CVPR (2021) 2, 8, 19
49. Ronneberger, O., Fischer, P., Brox, T.: U-net: Convolutional networks for biomed-
ical image segmentation. In: MICCAI (2015) 9
50. Saha, A., Maldonado, O.M., Russell, C., Bowden, R.: Translating images into maps.
In: ICRA (2022) 4
51. Shan, T., Englot, B., Meyers, D., Wang, W., Ratti, C., Daniela, R.: Lio-sam:
Tightly-coupled lidar inertial odometry via smoothing and mapping. In: IROS
(2020) 11
52. Shan, T., Englot, B., Ratti, C., Daniela, R.: Lvi-sam: Tightly-coupled lidar-visual-
inertial odometry via smoothing and mapping. In: ICRA (2021) 11
53. Su, J., Chen, C., Zhang, K., Luo, J., Wei, X., Wei, X.: Structure guided lane
detection. In: IJCAI-21 (2021) 2, 19, 20
54. Sun, P., Kretzschmar, H., Dotiwalla, X., Chouard, A., Patnaik, V., Tsui, P., Guo,
J., Zhou, Y., Chai, Y., Caine, B., et al.: Scalability in perception for autonomous
driving: Waymo open dataset. In: CVPR (2020) 9, 10, 11, 30
55. Tabelini, L., Berriel, R., Paixao, T.M., Badue, C., De Souza, A.F., Oliveira-Santos,
T.: Keep your eyes on the lane: Real-time attention-guided lane detection. In:
CVPR (2021) 2, 6, 8, 12, 19, 20, 30
56. Tan, M., Le, Q.: Efficientnet: Rethinking model scaling for convolutional neural
networks. In: ICML (2019) 5, 20
57. Teed, Z., Deng, J.: Droid-slam: Deep visual slam for monocular, stereo, and rgb-d
cameras. In: NeurIPS (2021) 11
58. TuSimple: https://github.com/TuSimple/tusimple-benchmark (2017) 4, 10, 19
59. Vandenhende, S., Georgoulis, S., Van Gansbeke, W., Proesmans, M., Dai, D.,
Van Gool, L.: Multi-task learning for dense prediction tasks: A survey. TPAMI
(2021) 8
60. Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser,
 L., Polosukhin, I.: Attention is all you need. In: NeurIPS (2017) 3
61. Wang, J., Mei, T., Kong, B., Wei, H.: An approach of lane detection based on
inverse perspective mapping. In: ITSC (2014) 2, 19
62. Wang, Y., Guizilini, V.C., Zhang, T., Wang, Y., Zhao, H., Solomon, J.: Detr3d: 3d
object detection from multi-view images via 3d-to-2d queries. In: CoRL (2022) 4,
7, 28
63. Wei, S.E., Ramakrishna, V., Kanade, T., Sheikh, Y.: Convolutional pose machines.
In: CVPR (2016) 9


## Page 18

18
L. Chen et al.
64. Xu, H., Wang, S., Cai, X., Zhang, W., Liang, X., Li, Z.: Curvelane-nas: Unifying
lane-sensitive architecture search and adaptive point blending. In: ECCV (2020)
4, 10, 19
65. Yan, F., Nie, M., Cai, X., Han, J., Xu, H., Yang, Z., Ye, C., Fu, Y., Mi, M.B.,
Zhang, L.: Once-3dlanes: Building monocular 3d lane detection. In: Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR).
pp. 17143–17152 (June 2022) 19, 29
66. Yan, F., Nie, M., Cai, X., Han, J., Xu, H., Yang, Z., Ye, C., Fu, Y., Michael, B.M.,
Zhang, L.: Once-3dlanes: Building monocular 3d lane detection. In: CVPR (2022)
10
67. Yang, W., Li, Q., Liu, W., Yu, Y., Ma, Y., He, S., Pan, J.: Projecting your view
attentively: Monocular road scene layout estimation via cross-view transformation.
In: CVPR (2021) 4
68. Yin, J., Shen, J., Guan, C., Zhou, D., Yang, R.: Lidar-based online 3d video ob-
ject detection with graph-based message passing and spatiotemporal transformer
attention. In: CVPR (2020) 4
69. Yu, F., Chen, H., Wang, X., Xian, W., Chen, Y., Liu, F., Madhavan, V., Darrell,
T.: Bdd100k: A diverse driving dataset for heterogeneous multitask learning. In:
CVPR (2020) 4, 10, 19
70. Yu, Z., Ren, X., Huang, Y., Tian, W., Zhao, J.: Detecting lane and road markings
at a distance with perspective transformer layers. In: ITSC (2020) 2
71. Zhang, Y., Zhu, L., Feng, W., Fu, H., Wang, M., Li, Q., Li, C., Wang, S.: Vil-100:
A new dataset and a baseline model for video instance lane detection. In: ICCV
(2021) 10, 19
72. Zhu, X., Su, W., Lu, L., Li, B., Wang, X., Dai, J.: Deformable DETR: Deformable
transformers for end-to-end object detection. In: ICLR (2021) 3, 7, 28, 29, 30


## Page 19

PersFormer and OpenLane
19
Appendix
A
More Related Work
A.1
Lane Detection Benchmarks
For example, [29,23,69] annotate lanes and lane markings in pixel-level so they
are best suitable for semantic segmentation task. [58,4] collect data on highways
with light traffic only, which is not challenging and has a large gap between the
evaluation and real-world performance for up-to-date algorithms. [44,64] con-
sider more scenarios under different weather and traffic conditions; however,
no-segment character limits their applicability for future applications, such as
lane tracking or temporal lane detection. The recently released VIL-1000 [71] is
specifically designed for video instance lane detection, and yet it does not provide
tracking ID annotation across the segments. At the same time of our proposing
OpenLane dataset, there’s another large-scale realistic 3D lane dataset, named
ONCE-3DLanes [65], that annotates lane layout in 3D space. The difference be-
tween OpenLane and ONCE-3DLanes falls into three aspects. First is the dataset
statistics. The number of frames contained is quite the same, where OpenLane
has 200K in total and ONCE-3DLanes has 211K. The annotation quality dif-
ferentiates a lot, as OpenLane has more than 25% of frames with more than 6
lanes, while ONCE-3DLanes only has less than 10% of frames under the same
setting. Second is the problem setting. OpenLane provides camera extrinsics as
Waymo Open Dataset, while ONCE-3DLanes lacks of this information. Mean-
while, OpenLane provides segments annotation as scene tags, where ONCE-
3DLanes doesn’t. This could be used in video task and expand the potential
usage of OpenLane. Third is the diversity of lane annotation. In OpenLane, the
lane annotation not only contains the 3D position of such a lane, but also several
attributes and tracking id. In ONCE-3DLanes, only the 3D position information
is provided. Due to the difficulty of collecting 3D information for lanes, current
3D lane detection algorithms mainly focus on synthetic data [20]. It is small-scale
and exists the domain gap between simulation and realistic scenarios.
A.2
2D Lane Detection
Early lane detection approaches rely on traditional computer vision techniques,
such as filtering [2,32], clustering [61], etc. With the advent of deep learning,
CNN-based methods significantly outperform hand-crafted algorithms. A typical
way is to treat lane detection as a semantic segmentation problem [29,44,41,22,1].
Binary segmentation [41] needs post-clustering process for lane instance discrim-
ination, while multi-class segmentation [29,44,22] usually limits the maximum
detection results in one frame. Moreover, the pixel-wise classification takes large
computation resources. To overcome this, several work propose lightweight yet
effective grid based [47,35,25,48] or anchor based [11,30,64,53,55] methods. The
grid-based approach detects lanes in a row-wise way, whose resolution is much


## Page 20

20
L. Chen et al.
lower than the segmentation map. The model outputs the probability for each
cell if it belongs to a lane, and a vertical post-clustering process is still needed
to generate the lane instances. Anchor-based approaches adopt the idea from
classical object detection, focusing on optimizing the offsets from predefined line
anchors. In this circumstance, how to define anchors is a critical problem. Chen
et al. [11] adopts vertical anchors, which cause great difficulty for curving lane
prediction. Some work [30,55,53] design anchors as a slender tilt shape, while
the huge amount of different anchors to improve the detection accuracy would
influence the computational efficiency. Nevertheless, considering their incredi-
ble performance on public datasets, we adopt the anchor-based formulation and
carefully re-design anchors to achieve both high accuracy and efficiency.
B
Algorithm
We summarize the details of PersFormer here. We introduce the backbone, over-
all structure and the unified anchor design. Later we break down the loss function
into pieces.
B.1
Backbone
The backbone module is slightly different from previous work [16,20], as we need
to consider 2D/3D branches together. We use EfficientNet [56] as our backbone,
and extract a specific layer as our following module’s input. Later we provide
two designs, using FPN [34] or not. After using several convolution layers, the
backbone module outputs 4 different scaled front-view feature maps. Their res-
olutions are 180 × 240, 90 × 120, 45 × 60, 22 × 30. Each front-view feature map
is then transformed to BEV-space feature map with the help of Perspective
Transformer, resulting in 4 BEV feature maps.
B.2
Anchor Details
In this section, we present details of our anchor design, including angles, numbers
of anchors and how we associate ground truth lanes with anchors in 2D and 3D.
As introduced in the main body of the paper, we first set anchors in BEV space.
Following Gen-LaneNet [20], the starting positions Xi
bev are evenly placed along
x-axis with the spacing of 8 pixels. However, we differentiate it from the incline
angle φ. Gen-LaneNet sets straight-forward (parallel to y-axis) only, which makes
it hard to predict lanes with large curvatures or perpendicular lanes. Towards
this problem, we put 7 anchors at each Xi
bev with different angles, i.e., φ ∈
{π/2, arctan (±0.5), arctan (±1), arctan (±2)}. Note that the angles are in terms
of grid coordinates, which is not equal to the absolute values when grids are
not square. Moreover, we project all the BEV anchors to image space with
average camera height and pitch angle of the dataset, leading to corresponding
2D anchors.


## Page 21

PersFormer and OpenLane
21
The association between ground truth lanes and anchors is based on the av-
erage distance similar to the loss calculation process, instead of assigning the
closest anchor at Yref to ground truths as [16,20]. The Yref is set very close
to ego-vehicle, i.e., 5m in Gen-LaneNet, which makes it better predict lanes
in close area while having unsatisfactory performance in the far distance. In
our experiments, we assign the anchor with minimum edit distance to ground
truth lanes in both 2D and 3D tasks. The distance is calculated at fixed y posi-
tions: (5, 10, 15, 20, 30, 40, 50, 60, 80, 100) for 3D anchors, and 72 equally sampled
heights for 2D anchors.
B.3
Loss Function
We give the details of loss function here. As introduced in the main body of
the paper, given the pre-defined y value of the Nd samples along y-axis, the 3D
detection head outputs a set of points for each anchor i as following:
  (\ mat hbf 
{x}^ i , \mathbf  {z}^i,  \mathbf
 {v is}^
i_{\text {bev}}) = \{ (x^{(i,k)}, z^{(i,k)}, \text {vis}^{(i,k)}_{\text {bev}} ) \}^{N_d}_{k=1} 
(7)
The y values are (5, 10, 15, 20, 30, 40, 50, 60, 80, 100) in the BEV space, and the
size of the BEV space is 20m×100m. Similar to 3D setting, given the pre-defined
v value of the Nd samples along v-axis in front view, the 2D prediction is:
  (\ math
bf { u}^i, \ma thbf {vi
s} ^i_{
\text {uv}}) = \{ (u^{(i,k)}, \text {vis}^{(i,k)}_{\text {uv}} ) \}^{N_d}_{k=1} 
(8)
The loss is a combination of the 2D lane detection, 3D lane detection and inter-
mediate segmentation with learnable weights (α, β, γ) accordingly:
  
\
m
athcal 
{L}  = \sum
 _i  \a lp ha 
\ma thc al {L}_
{ \t e xt {2D} }( c^i_{ \text {2D} }, \mathbf {u}^i, \mathbf {vis}^i_{\text {fv}} ) + \beta \mathcal {L}_{ \text { 3D } } ( c^i_{ \text {3D} }, \mathbf {x}^i, \mathbf {z}^i, \mathbf {vis}^i_{\text {bev}} ) + \gamma \mathcal {L}_{ \text {seg}} (S_{\text {pred}}), 
(9)
where ci
(·) is the predicted lane category in 2D and 3D domain respectively. For
L 3D , it consists of classification loss, regression loss and visibility loss. The
classification loss is a cross-entropy loss, which is as follow:
  \math c al {L}
_{\text {3
D}{\text -}\text {cls}} = \mathcal {L}_{CE}(c^i_{\text {3D}{\text -}\text {pred}}, c^i_{\text {3D}{\text -}\text {gt}}) 
(10)
The regression loss is a L1 loss, which is as follow:
  \math c al {L}_{ \text {3 D}{\ text -}\text {reg}} = \mathcal {L}_{L_1}(\{\mathbf {x}^i, \mathbf {z}^i\}_{\text {pred}}, \{\mathbf {x}^i, \mathbf {z}^i\}_{\text {gt}}) 
(11)
The visibility loss is a binary cross-entropy loss, which is as follow:
  \math c al {L}_{\
text {3D}
{\text -}\text {vis}} = \mathcal {L}_{BCE}(\mathbf {vis}^i_{\text {pred}}, \mathbf {vis}^i_{\text {gt}}) 
(12)
The 2D loss functions are similar to the 3D ones, except they are in 2D form:
  \begi n  {spli
t} \math ca
l {L}_
{\text { 2D}{\text -}\ text {c
ls}} &=  \mathcal 
{L}_{ CE}(
c^i_{\text {2D}{\text -}\text {pred}}, c^i_{\text {2D}{\text -}\text {gt}}) \\ \mathcal {L}_{\text {2D}{\text -}\text {reg}} &= \mathcal {L}_{L_1}(\{\mathbf {u}^i \}_{\text {pred}}, \{\mathbf {u}^i\}_{\text {gt}}) \\ \mathcal {L}_{\text {2D}{\text -}\text {vis}} & = \mathcal {L}_{BCE}(\mathbf {vis}^i_{\text {pred}}, \mathbf {vis}^i_{\text {gt}}) \end {split} 
(13)
The segmentation loss is a binary cross-entropy loss as well, which is as follow:
  \m a thcal {L}_{ \text {seg}} = \mathcal {L}_{BCE}(S_{\text {pred}}, S_{\text {gt}}) 
(14)


## Page 22

22
L. Chen et al.
Table 7. Statics of scenario tags. Scene tags are annotated in terms of segments
Tags
Train
Val.
All
Weather
Clear
515
145
660
Partly cloud
131
28
159
Overcast
33
8
41
Rainy
107
18
125
Foggy
12
3
15
Scene
Residential
270
69
339
Urban
234
56
290
Suburbs
259
64
323
Highway
30
6
36
Parking lot
5
7
12
Hours
Daytime
653
167
820
Night
88
22
110
Dawn/Dusk
57
13
70
C
Details on OpenLane Benchmark
In this section, we present more details on dataset statics, our annotation crite-
rion, visualization examples, algorithms we adopted when generating the dataset.
C.1
Dataset Statistics
OpenLane has 1,150 segments with train/validation/test splits of 798/202/150,
respectively. Since the test sets are kept for its online leaderboard evaluation, we
annotate the other 1,000 segments, i.e., 200K frames at a frequency of 10 FPS,
and keep the original train/validation partition for fair comparison with other
tasks, such as object detection.
We compute the statistics in OpenLane and visualize them. The overall num-
ber of segments with different scene tags is given in Tab. 7. It implies great
diversity in data collection and raises higher requirements on the robustness of
algorithms. The weather distribution is visually presented in Fig. 7. It shows the
benchmark covers various weather conditions and well holds the consistency in
the train/validation split. The distribution of the number of lanes in each frame
is shown in Fig. 8. About 25% frames of OpenLane have more than 6 lanes,
which exceeds the maximum number in most lane datasets. Fig. 9 shows the
distribution of lane categories. Single white solid and dash lanes, double yellow
solid lanes take up almost 90% of the total lanes. This is imbalanced and yet
it falls into a long-tail distribution problem, which is common in realistic sce-
narios. Fig. 10 presents the distribution of altitude difference per frame. Only
around 20% frames are relatively flat with absolute height variation less than
0.5m, whereas the difference is more than 1m in over 50% of OpenLane. This
data further demonstrates the necessity of 3D lane detection. The above statis-
tics and examples below demonstrate that OpenLane is the most challenging
one compared to existing lane detection datasets.


## Page 23

PersFormer and OpenLane
23
Train, Clear, 65%
Train, Partly cloud, 
16%
Train, Overcast, 4%
Train, Rainy, 13%
Train, Foggy, 2%
Val, Clear, 72%
Val, Partly cloud, 
14%
Val, Overcast, 4%
Val, Rainy, 9%
Val, Foggy, 1%
Clear
Partly cloud
Overcast
Rainy
Foggy
Fig. 7. Distribution of weather tags in training and validation sets. The data is collected
under different weathers and split into training and validation with great balance
0, 8.133%
1, 9.525%
2, 17.274%
3, 10.520%
4, 9.633%
5, 10.420%
6, 8.735%
7, 7.571%
8, 6.917%
9, 4.382%
10, 2.915%
11, 1.508%
12, 1.176%
13, 0.490%
14, 0.387%
15, 0.159%
16, 0.055%
17, 0.055%
18, 0.025%
19, 0.063%
20, 0.022%
21, 0.007%
22, 0.013%
23, 0.015%
24, 0.003%
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
Fig. 8. Distribution of lane numbers per frame. The maximum number is 24, and 25%
frames have more than 6 lane
C.2
Annotation Criterion
We aim at introducing how we annotate lanes, scene tags and CIPO levels in
this section. Details such as data structures, folder hierarchy will be provided in
the dataset releasing page in the future.
Lanes. Our principle for the 2D lane detection task is to find all visible lanes
inside left and right road edges. Following this philosophy, we carefully annotate


## Page 24

24
L. Chen et al.
1-W dash
1-W solid
2-W dash
2-W solid
L-W dash
R-W solid
L-W solid
R-W dash
1-Y dash
1-Y solid
2-Y dash
2-Y solid
L-Y dash
R-Y solid
L-Y solid
R-Y dash
Left curbside
Right curbside
Others
Lane category
Lane Number
Fig. 9. Distribution of the lane category. Here we abbreviate single in 1, double in 2,
white in W, yellow in Y, left in L, and right in R. Thus 1-W dash means the category
of single white dash lanes
Altitude Difference 
0
Frame Number
1,000
2,000
3,000
4,000
5,000
6,000
4.89
0.84
2.21
9.81
19.89
Fig. 10. Altitude difference per frame. Note the x-axis is approximately in a log scale
and its unit is m
lanes in each frame. However, due to the complexity of scenarios, there exist
some special cases we seek to illustrate here. (1) Lanes are often occluded by
objects or invisible because of abrasion but they are still valuable for the real
application. Thus we annotate lanes if parts of them are visible, meaning lanes
with one side being occluded are extended or lanes with invisible intermediate
parts are completed according to the context, as shown in Fig. 11. (2) It is very
common that the number of lanes changes, especially when lanes have complex
topologies such as fork lanes in merge and split cases. Traditional lane datasets


## Page 25

PersFormer and OpenLane
25
usually omit these scenarios for simplicity, while we keep them all and further
choose them out of the whole dataset for evaluation. Fork lanes are annotated as
separate lanes with a common starting point (split) or ending point (merge) - two
close adjacent lanes are desired for the lane detection methods. (3) We further
annotate each lane as one of the 14 lane categories, i.e., single white dash, single
white solid, double white dash, double white solid, double white dash solid (left
white dash with right white solid), double white solid dash (left white solid with
right white dash), single yellow dash, single yellow solid, double yellow dash,
double yellow solid, double yellow dash solid (left yellow dash with right yellow
solid), double yellow solid dash (left yellow solid with right yellow dash), left
curbside, right curbside. Note that traffic bollards are considered as curbsides
as well if they are not temporally placed. (4) Different from all the other lane
datasets, we annotate a tracking ID for each lane which is unique across the
whole segment. We believe this could be helpful for video lane detection or lane
tracking tasks. We also assign a number in 1-4 to the most important 4 lanes
based on their relative position to the ego-vehicle. Basically, the left-left lane is
1, the left lane is 2, the right lane is 3, and the right-right lane is 4.
All valid 2D ground truths are transformed to 3D annotations by the gener-
ation method in Sec. 4.2 of the main body (Generation of High-quality Annota-
tion), except those without LiDAR points scanning through. Thus the criterion
above applies to 3D lanes as well.
Scene tags. We label each segment with 3 scene tags, i.e., weather, scene
and hours. We hope these labels can help researchers to investigate the robust-
ness of their models under various scenarios. The statics are shown in Tab. 7.
Specifically, the dataset covers 5 different kinds of weather, clear, partly cloud,
overcast, rainy and foggy. Note that we classify the video as partly cloud or
foggy when there are clouds or fog in the sky respectively, otherwise it will be
categorized as overcast. The scene, or the location, includes 5 categories, i.e.,
residential, urban, suburbs, highway and parking lot. And the hours are divided
into 3 parts: daytime, night, dawn/dusk.
Closest-in-path object (CIPO). CIPO is usually defined as the closest
object in ego lane, which refers to a single vehicle only. However, there are
cases that vehicles on left/right lanes are intended to cut in which are crucial
as well, or there may not be any qualified vehicles in ego lane. To cover the
complex scenarios, we categorize objects, mainly including vehicles, pedestrians
and cyclists, into 4 different CIPO levels. (1) The most important one, which
is closest to ego vehicle within the required reaction distance and has over 50%
part of it in the ego lane. Level 1 contains one object at most. (2) Objects
are annotated as Level 2 when their bodies interact with the real or virtual
lines of ego lane. They are typically in the process of cut-in or cut-out, which
hugely influences ego-vehicle decision-making. (3) We consider objects mainly
within the reaction distance or drivable area, or those in left/ego/right lanes
more specifically. Thus we annotate Level 3 with objects in the above area and
having occlusion rate less than 50%. Note that vehicles in the opposite direction
can be in this CIPO level as well. (4) The remainings are labeled as Level 4,


## Page 26

26
L. Chen et al.
Fig. 11. Visualization example of lane annotation in OpenLane dataset
which means they are almost unlikely to impact the future path at this moment.
They are mainly objects in lanes with far distance, objects out of drivable area,
or parked vehicles in our dataset. Examples are provided in Fig. 12.
C.3
3D lane Generation
Fig. 13 shows the intermediate results of the generation process of 3D lane labels.
However, the above process could have a few problems in some cases, especially in
the last step, i.e., smoothing and fitting. Multiple filtering and fitting algorithms
are adopted to realize it, while all of them require a set of sorted points. Due to
the large curvature, the one-to-one mapping probably does not stand either in x
or y direction, thus we could not sort the points directly. Towards this problem,
for each image with this circumstance, we simply find an angle to rotate the
whole points set, do the filtering and fitting process in the temporary coordinate
and rotate back in the end. This method is illustrated in Fig. 14.


## Page 27

PersFormer and OpenLane
27
Fig. 12. Visualization example of CIPO and Scene tags annotation in OpenLane
dataset
D
Experiments
D.1
Evaluation Metrics.
For both 3D lane datasets, we follow the evaluation metric designed by Gen-
LaneNet [20], with small modifications2 and additional category accuracy on
OpenLane dataset. The matching between prediction and ground truth is built
upon edit distance, where one predicted lane is considered to be a true positive
only if 75% of its covered y-positions have a point-wise distance less than the
max-allowed distance (1.5m). Then, with the percentage of matched ground-
truth lanes as recall and the percentage of matched prediction lanes as precision,
we use F-score to report the regression performance of such a model. Since
OpenLane dataset has category information per lane, we present the accuracy
upon the matched lanes to show classification performance. We only report the
accuracy of PersFormer on OpenLane dataset, as other 3D methods do not
2 Please see in OpenLane page: https://github.com/OpenPerceptionX/OpenLane.


## Page 28

28
L. Chen et al.
(b)
(a)
(c)
(d)
(e)
Fig. 13. 3D lane generation pipeline. (a) Original point clouds inside a certain threshold
of 2D lane annotations are reserved, which is relatively sparse; (b) Positions of points
on the 2D annotation are interpolated to get a dense point set; (c) 3D lane points in
the same segment are spliced into long, high-density lanes; (d) We remove those too far
as they are invisible, while reasonable extensions are desired; (e) A smooth and fitting
process is applied to get the final 3D lane annotation
(a)
(b)
(c)
Fig. 14. Illustration of 3D lane generation problem with large curvatures. (a) The
original image and the 2D lane; (b) Unsorted 3D points set of the lane in (a), which a
filtering algorithm is not applicable directly; (c) A simple translation and rotation can
result in a one-to-one mapping of x and y
support classification task. For the 2D task, the classical metric in CULane [44]
is adopted.
D.2
Implementation Details
To fairly compare with other methods [20,16,37], we retain many model settings
of image resolution and BEV scale. We resize the original image to 360 × 480
as model input, project it to BEV space with a resolution of 208 × 108. We use
PyTorch [45] to implement the model. The batch size is set to 8; the number of
training epochs is set to 100. We re-implement 3D-LaneNet and Gen-LaneNet on
OpenLane dataset for a fair comparison. Following previous experience on train-
ing vision transformer [8,72,62], we use Adam optimizer [27] with base learning


## Page 29

PersFormer and OpenLane
29
Table 8. New results on the new benchmark (CVPR22) ONCE-3DLanes [65]. ∗denotes
results from the paper [65]
Method
F-Score(%) Precision(%)
Recall(%)
CD error(m)
3D-LaneNet∗[16]
44.73
61.46
35.16
0.127
Gen-LaneNet∗[20]
45.59
63.95
35.42
0.121
SALAD∗[65]
64.07
75.90
55.42
0.098
PersFormer (ours)
74.33
80.30
69.18
0.074
rate of 2×10−4, β1 = 0.9, β2 = 0.999 and weight decay of 10−4. All of these mod-
els are trained on 8 NVIDIA Tesla V100 GPUs. More details about environment
setup can be referred to our GitHub repository once accepted.
D.3
More Experimental Results
In this section, we present more experimental results, mainly in 3D comparison
on ONCE-3DLanes, additional ablations and more qualitative examples.
3D Comparisons on ONCE-3DLanes. We provide additional experimen-
tal results on ONCE-3DLanes dataset [65], as it’s another real-world 3D lane
dataset concurrently presented. ONCE-3DLanes also uses F-Score as the eval-
uation metric, and more details can be found in their repo ONCE-3DLanes. In
Tab. 8, PersFormer gets the highest F-Score on the validation set, outperforming
its proposed method SALAD [65] over 10%. One thing worth noticing is that
ONCE-3DLanes does not provide camera extrinsics, therefore PersFormer pre-
define a set of extrinsic parameters to fit the model setting. The camera height
is set to be 1.5m and pitch to be 0.5. This does not affect the evaluation results
since it is just to fit the IPM process in PersFormer.
Ablations. We provide an additional ablative study on the structure of the
feature transformation module on a subset of OpenLane (∼300 segments) in Tab.
9. We argue that the IPM-based cross attention is a necessity in PersFormer,
as we compare it with two initial designs, naive one-to-one mapping and the
learned mapping. The naive one-to-one mapping simply scales every location
in the BEV space to the corresponding location in the front view space, not
considering camera parameters (Exp.1). A more “aggressive” way to simulate
the mapping is directly learning from the front view feature with several fully-
connected layers (Exp.2). Neither of them could catch up with the performance
of IPM-based mapping, indicating the importance of such a prior in generating
BEV feature. We further attempt to adopt Multi-scale Deformable Attention
from [72] to implement a several-for-one feature mapping from multi-scale front
view feature to multi-scale BEV feature (Exp.3), just like Deformable DETR.
The result slightly falls behind our final design (Exp.5), probably due to the
influence of tuning of hyper-parameters and the impact of the small-scale feature
on the large-scale feature. Finally, we try to remove the classical self attention


## Page 30

30
L. Chen et al.
Table 9. Ablative Study on PersFormer Design. IPM prior plays a vital role in guiding
the generation of BEV feature compared to naive one-to-one mapping and learned
reference-target mapping. Using MSDeformAttn from Deformable DETR [72] to map
multi-scale front-view feature to multi-scale BEV feature is competitive, and the self-
attention module of BEV query is important in Transformer-style structure
Exp.
Naive
1-1
Learned
Multi-to-
Multi
Self
Attn.
IPM
Prior
3D F-Score
1
✓
36.15
2
✓
13.45
3
✓
51.35
4
✓
47.18
5
✓
52.68
module in ordinary Transformer design (Exp.4), showing that the self attention
module is all there for a reason in Transformer-style structure.
Visualization. We provide qualitative results compared with SOTA 3D lane
detection methods in different evaluation scenarios on OpenLane dataset in Fig.
15,16. Results on Apollo 3D synthetic dataset are shown in Fig. 17. We can
observe that PersFormer could achieve higher accuracy and capture more lanes
to reconstruct the scenes on both datasets.
E
License of Assets
OpenLane dataset is based on the Waymo Open Dataset [54] and therefore
we distribute the data under Creative Commons Attribution-NonCommercial-
ShareAlike license and Waymo Dataset License Agreement for Non-Commercial
Use (August 2019). You are free to share and adapt the data, but have to give
appropriate credit and may not use the work for commercial purposes. All code
of PersFormer and OpenLane toolkit is under Apache License 2.0.
The pretrained ResNet model weights are under the MIT license. We inte-
grate part of the code of Deformable-DETR [72] and Gen-LaneNet [20] which
are under Apache License 2.0. We also use part of the code of LaneATT [55]
which is under the MIT license.
F
Outlook
As OpenLane is built upon Waymo Open Dataset [54], a road-object joint detec-
tion framework is possible in the future. Moreover, BEV is the necessity in the
future of autonomous driving, and how to design a better BEV representation
remains to be explored. The proposed PersFormer may also be adapted to new
tasks.


## Page 31

PersFormer and OpenLane
31
Fig. 15.
Qualitative
results
of
PersFormer(a),
3D-LaneNet(b)
[16],
and
Gen-
LaneNet(c) [20] on OpenLane. Night case and Up&Down case


## Page 32

32
L. Chen et al.
Fig. 16.
Qualitative
results
of
PersFormer(a),
3D-LaneNet(b)
[16],
and
Gen-
LaneNet(c)
[20]
on
OpenLane.
Extreme
weather
case,
Intersection
case
and
Merge&Split case


## Page 33

PersFormer and OpenLane
33
Fig. 17.
Qualitative
results
of
PersFormer(a),
3D-LaneNet(b)
[16],
and
Gen-
LaneNet(c) [20] on Apollo. Curve case and Up&Down case

