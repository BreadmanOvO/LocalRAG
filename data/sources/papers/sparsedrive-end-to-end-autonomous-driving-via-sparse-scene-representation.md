# SparseDrive: End-to-End Autonomous Driving via Sparse Scene Representation

**Source**: arXiv:2405.19620

**Type**: Academic Paper

---

## Page 1

SparseDrive: End-to-End Autonomous Driving via
Sparse Scene Representation
Wenchao Sun1,2
Xuewu Lin2
Yining Shi1
Chuang Zhang1
Haoran Wu1
Sifa Zheng1
1 Tsinghua University
2 Horizon
Abstract
The well-established modular autonomous driving system is decoupled into dif-
ferent standalone tasks, e.g. perception, prediction and planning, suffering from
information loss and error accumulation across modules. In contrast, end-to-end
paradigms unify multi-tasks into a fully differentiable framework, allowing for
optimization in a planning-oriented spirit. Despite the great potential of end-to-
end paradigms, both the performance and efficiency of existing methods are not
satisfactory, particularly in terms of planning safety. We attribute this to the compu-
tationally expensive BEV (bird’s eye view) features and the straightforward design
for prediction and planning. To this end, we explore the sparse representation
and review the task design for end-to-end autonomous driving, proposing a new
paradigm named SparseDrive. Concretely, SparseDrive consists of a symmetric
sparse perception module and a parallel motion planner. The sparse perception
module unifies detection, tracking and online mapping with a symmetric model
architecture, learning a fully sparse representation of the driving scene. For motion
prediction and planning, we review the great similarity between these two tasks,
leading to a parallel design for motion planner. Based on this parallel design, which
models planning as a multi-modal problem, we propose a hierarchical planning
selection strategy , which incorporates a collision-aware rescore module, to select
a rational and safe trajectory as the final planning output. With such effective
designs, SparseDrive surpasses previous state-of-the-arts by a large margin in
performance of all tasks, while achieving much higher training and inference effi-
ciency. Code will be avaliable at https://github.com/swc-17/SparseDrive
for facilitating future research.
1
Introduction
Traditional autonomous driving system is characterized as modular tasks in sequential order. While
advantageous in interpretation and error tracking, it inevitably leads to information loss and accumu-
lative errors across successive modules, thereby limiting the optimal performance potential of the
system.
Recently, an end-to-end driving paradigm emerged as a promising research direction. This paradigm
integrates all tasks into one holistic model, and can be optimized toward the ultimate pursuit for
planning. However, the existing methods[15, 20] are not satisfactory in terms of performance and
efficiency. On one hand, previous methods rely on computationally expensive BEV features. On the
other hand, the straightforward design for prediction and planning limits the model performance. We
summarize previous methods as BEV-Centric paradigm in Fig. 1a.
To fully leverage the potential of end-to-end paradigm, we review the task design of existing methods,
and argue that three main parallels shared between motion prediction and planning are neglected
as follows: (1) Aiming at predicting future trajectories of surrounding agents and ego vehicle, both
Preprint. Under review.
arXiv:2405.19620v2  [cs.CV]  31 May 2024


## Page 2

Planning
Dense BEV Features
Online
Mapping
Detection
&Tracking
Motion
Multi-view
Camera Input
(a) BEV-Centric paradigm.
Multi-view
Camera Input
Online
Mapping
Detection
&Tracking
Motion
Planning
Backbone
Perception
Motion & Planning
(b) Sparse-Centric paradigm.
(c) Comparison between our method and
privous SOTA[15].
Figure 1: The comparison of various end-to-end paradigms. (a) The BEV-Centric paradigm. (b) The
proposed Sparse-Centric paradigm. (c) Performance and efficiency comparison between (a) and (b).
motion prediction and planning should consider the high-order and bidirectional interactions among
road agents. However, previous methods typically adopt a sequential design for motion prediction
and planning, ignoring the impact of ego vehicle on surrounding agents. (2) Accurate prediction for
future trajectories requires semantic information for scene understanding, and geometric information
to predict future movement of agents, which is applicable to both motion prediction and planning.
While these information are extracted in upstream perception tasks for surrounding agents, it is
overlooked for ego vehicle. (3) Both motion prediction and planning are multi-modal problems with
inherent uncertainty, but previous methods only predict deterministic trajectory for planning.
To this end, we propose SparseDrive, a Sparse-Centric paradigm as shown in Fig. 1b. Specifically,
SparseDrive is composed of a symmetric sparse perception module and a parallel motion planner.
With the decoupled instance feature and geometric anchor as complete representation of one instance
(a dynamic road agent or a static map element), Symmetric Sparse Perception unifies detection,
tracking and online mapping tasks with a symmetric model architecture, learning a fully sparse
scene representation. In Parallel Motion Planner, a semantic-and-geometric-aware ego instance is
first obtained from ego instance initialization module. With the ego instance and surrounding agent
instances from sparse perception, motion prediction and planning are conducted simultaneously to
get multi-modal trajectories for all road agents. To ensure the rationality and safety for planning, a
hierarchical planning selection strategy that incorporating a collision-aware rescore module is applied
to select the final planning trajectory from multi-modal trajectory proposals.
With above effective designs, SparseDrive unleashes the great potential of end-to-end autonomous
driving, as shown in Fig. 1c. Without bells and whistles, our base model, SparseDrive-B, greatly
reduces the average L2 error by 19.4% (0.58m vs. 0.72m) and collision rate by 71.4% (0.06% vs.
0.21%). Compared with previous SOTA (state-of-the-art) method UniAD[15], our small model,
SparseDrive-S achieves superior performance among all tasks, while running 7.2× faster for training
(20 h vs. 144 h) and 5.0× faster for inference (9.0 FPS vs. 1.8 FPS).
The main contribution of our work are summarized as follows:
• We explore the sparse scene representation for end-to-end autonomous driving and propose a
Sparse-Centric paradigm named SparseDrive, which unifies multiple tasks with sparse instance
representation.
• We revise the great similarity shared between motion prediction and planning, correspondingly
leading to a parallel design for motion planner. We further propose a hierarchical planning selection
strategy incorporating a collision-aware rescore module to boost the planning performance.
• On the challenging nuScenes[1] benchmark, SparseDrive surpasses previous SOTA methods in
terms of all metrics, especially the safety-critical metric collision rate, while keeping much higher
training and inference efficiency.
2


## Page 3

2
Related Work
2.1
Multi-view 3D Detection
Multi-view 3D detection is a prerequisite for the safety of autonomous driving system. LSS[42]
utilizes depth estimation to lift image features to 3D space and splats features to BEV plane. Follow-up
works apply lift-splat operation to the field of 3D detection, and have made significant improvement
in accuracy[18, 16, 25, 24] and efficiency[37, 17]. Some works[26, 48, 21, 5] predefine a set of BEV
queries and project them to perspective view for feature sampling. Another line of research removes
the dependency for dense BEV features. PETR series[35, 36, 47] introduce 3D positional encoding
and global attention to learn view transformation implicitly. Sparse4D series[31, 32, 33] set explicit
anchors in 3D space, projecting them to image view to aggregate local features and refine anchors in
an iterative fashion.
2.2
End-to-End Tracking
Most multi-object tracking (MOT) methods adopt the tracking-by-detection fashion, which relies
on post-processing like data association. Such pipeline cannot fully leverage the capabilities of
neural networks. Inspired by object queries in [2], some works[52, 55, 50, 41, 46, 54] introduce track
queries to model the tracked instances in streaming manner. MOTR[52] proposes tracklet-aware label
assignment, which forces the track query to continuously detect the same target and suffers from the
conflict between detection and association[55, 50]. Sparse4Dv3 demonstrates that the temporally
propagated instances already have identity consistency, and achieves SOTA tracking performance
with a simple ID assignment process.
2.3
Online Mapping
Online mapping is proposed as an alternative of HD map, due to the high cost and vast human
efforts in HD map construction. HDMapNet[23] groups BEV semantic segmentation with post-
processing to get vectorized map instances. VectorMapNet[34] utilizes a two-stage auto-regressive
transformer for online map construction. MapTR[29] models map element as a point set of equivalent
permutations, which avoids definition ambiguity of map element. BeMapNet adopts piecewise Bezier
curve to describe the details of map elements. StreamMapNet[51] introduces BEV fusion and query
propagation for temporal modeling.
2.4
End-to-End Motion Prediction
End-to-end motion prediction is proposed to avoid the cascading error in traditional pipelines. FaF[40]
employs a single convolution network to predict both current and future bounding boxes. IntentNet[3]
takes one step further to reason both high level behavior and long term trajectories. PnPNet[28]
introduces an online tracking module to aggregate trajectory level features for motion prediction.
ViP3D[10] employs agent queries to perform tracking and prediction, taking images and HD map as
input. PIP[19] replaces human-annotated HD map with local vectorized map.
2.5
End-to-End Planning
The research of end-to-end planning has been ongoing since last century[43]. Early works[6, 7, 44]
omit intermediate tasks like perception and motion prediction, which lack interpretability and are
difficult to optimize. Some works[14, 4, 45, 8] construct explicit cost map from perception or
prediction results to enhance interpretability, but rely on hand-crafted rules to select the best trajectory
with minimum cost. Recently, UniAD[15] proposes a unified query design to integrate various
tasks into a goal-oriented model, achieving remarkable performance in perception, prediction and
planning. VAD[20] employs vectorized representation for scene learning and planning constraints.
GraphAD[56] utilizes graph model for complex interactions in traffic scenes. FusionAD[49] extends
end-to-end driving to multi-sensor input. However, previous methods mainly focus on scene learning,
and adopt a straightforward design for prediction and planning, without fully considering the similarity
between these two tasks, greatly limiting the performance.
3


## Page 4

Temporal
Current
Instance Feature
& Anchor Box
Ego Instance Feature
& Anchor Box
Map Instance Feature
& Anchor Polyline
FIFO
Instance Memory Queue
T
T-1
T-2
Symmetric Sparse Perception
Parallel Motion Planner
Driving
Command
Detection & Tracking & Online Mapping
Motion Prediction & Planning
Backbone
Neck
Image Encoder
Temporal Fusion
Update
Temporal Fusion
Update
Initialize
Figure 2: Overview of SparseDrive. SparseDrive first encodes multi-view images into feature maps,
then learns sparse scene representation through symmetric sparse perception, and finally perform
motion prediction and planning in a parallel manner. An instance memory queue is devised for
temporal modeling.
3
Method
3.1
Overview
The overall framework of SparseDrive is depicted in Fig. 2. Specifically, SparseDrive is consisted of
three parts: image encoder, symmetric sparse perception and parallel motion planner. Given multi-
view images, the image encoder, including a backbone network and a neck, first encodes images to
multi-view multi-scale feature maps I =

Is ∈RN×C×Hs×Ws|1 ≤s ≤S
	
, where S is the number
of scales and N is the number of camera views. In symmetric sparse perception module, the feature
maps I are aggregated into two groups of instances to learn the sparse representation of the driving
scene. These two groups of instances, representing surrounding agents and map elements respectively,
are fed into parallel motion planner to interact with an initialized ego instance. The motion planner
predicts multi-modal trajectories of surrounding agents and ego vehicle simultaneously, and selects a
safe trajectory as the final planning result through hierarchical planning selection strategy.
3.2
Symmetric Sparse Perception
As shown in Fig. 3, the model structure of sparse perception module exhibits a structural symmetry,
unifying detection, tracking and online mapping together.
Sparse Detection.
Surrounding agents are represented by a group of instance features Fd ∈RNd×C
and anchor boxes Bd ∈RNd×11, where Nd is the number of anchors and C is the feature channel
dimension. Each anchor box is formatted with location, dimension, yaw angle and velocity:
{x, y, z, ln w, ln h, ln l, sin yaw, cos yaw, vx, vy, vz} .
The sparse detection branch consists of Ndec decoders, including a single non-temporal decoder and
Ndec −1 temporal decoders. Each decoder takes feature maps I, instance features Fd and anchor
boxes Bd as input, outputs updated instance features and refined anchor boxes. The non-temporal
decoder takes randomly initialized instance as input, while the input for temporal decoder come from
both current frame and historical frame. Specifically, the non-temporal decoder includes three sub-
modules: deformable aggregation, feedforward network (FFN) and the output layer for refinement and
classification. The deformable aggregation module generates fixed or learnable keypoints around the
anchor boxes Bd and projects them to feature maps I for feature sampling. The instance features Fd
are updated by summation with sampled features, and are responsible for predicting the classification
4


## Page 5

scores and the offsets of anchor boxes in the output layer. The temporal decoders have two additional
multi-head attention layers: the temporal cross-attention between temporal instances from last frame
and current instances, and the self-attention among current instances. In multi-head attention layer,
the anchor boxes are transformed into high-dimensional anchor embedding Ed ∈RNd×C, and serve
as the positional encoding.
𝐼𝑡
Instance Memory Queue
Feature Maps
Temporal Propagation
Ego Motion Projection
Identity
Update
Deformable Aggregation
Feedforward Network
Refinement & Classification
Cross Attention
Self Attention
Deformable Aggregation
Feedforward Network
Refinement & Classification
× 1
× 5
Key
Value
Topk
Deformable Aggregation
Feedforward Network
Refinement & Classification
Cross Attention
Self Attention
Deformable Aggregation
Feedforward Network
Refinement & Classification
× 1
× 5
Key
Value
Topk
Initialized Map Instances
Output Map Instances
Initialized Detection Instances
Output Detection Instances
Figure 3: Model architecture of symmetric sparse perception, which unifies detection, tracking and
online mapping in a symmetric structure.
Sparse Online Mapping.
Online mapping branch shares the same model structure with detection
branch except different instance definition. For static map element, the anchor is formulated as a
polyline with Np points:

x0, y0, x1, y1, ..., xNp−1, yNp−1
	
.
Then all the map elements can be represented by map instance features Fm ∈RNm×C and anchor
polylines Lm ∈RNm×Np×2, where Nm is the number of anchor polylines.
Sparse Tracking.
For tracking, we follow the ID assignment process of Sparse4Dv3[33]: once
the detection confidence of an instance surpasses a threshold Tthresh, it is locked onto a target and
assigned with an ID, which remains unchanged throughout temporal propagation. This tracking
strategy does not need any tracking constraints, resulting in an elegant and simple symmetric design
for sparse perception module.
3.3
Parallel Motion Planner
As shown in Fig. 4, the parallel motion planner consists of three parts: ego instance initialization,
spatial-temporal interactions and hierarchical planning selection.
Ego Instance Initialization.
Similar to surrounding agents, ego vehicle is represented by ego
instance feature Fe ∈R1×C and ego anchor box Be ∈R1×11. While ego feature is typically
randomly initialized in previous methods, we argue that the ego feature also requires rich semantic
and geometric information for planning, similar to motion prediction. However, the instance features
of surrounding agents are aggregated from image feature maps I, which is not feasible for ego vehicle,
since ego vehicle is in blind area of cameras. Thus we use the smallest feature map of front camera to
initialize the ego instance feature:
Fe = AveragePool(Ifront,S)
(1)
There are two advantages in doing so: the smallest feature map has already encoded the semantic
context of the driving scene, and the dense feature map serves as a complementary for sparse
5


## Page 6

scene representation, in case there are some blacklist obstacles, which can not be detected in sparse
perception.
For ego anchor Be, the location, dimension and yaw angle can be naturally set, as we are aware of
these information of ego vehicle. For velocity, directly initialized from ground truth velocity leads to
ego status leakage, as illustrated in [27]. So we add an auxiliary task to decode current ego status
EST , including velocity, acceleration, angular velocity and steering angle. At each frame, we use the
predicted velocity from last frame as the initialization of ego anchor velocity.
d
Ego Instance Initialization
Front Feature Map Ego Status from T-1
Instance Memory Queue
Agent-Temporal Cross Attention
Agent-Agent Self Attention
Agent-Map Cross Attention
× 3
Symmetric Sparse Perception
Key
Value
Key
Value
Multi-modal trajectories and scores
0.8
0.1
0.1
0.1
0.2
0.7
0.1
0.4
0.5
Turn left
Turn right
Go straight
0.2
0.6
0.2
0.7
0.1
0.2
Motion
prediction
Planning
Hierarchical Planning Selection
1. Driving Command Selection
0.1
0.4
0.5
2. Collision-Aware Rescore
3. Max Score Selection
“Turning Right”
0.1
0.4
0.5
0
0.4
Update
Figure 4: Model structure of parallel motion planner, which performs motion prediction and planning
simultaneously and outputs safe planning trajectory.
Spatial-Temporal Interactions.
To consider the high-level interaction between all road agents, we
concatenate the ego instance with surrounding agents to get agent-level instances:
Fa = Concat(Fd, Fe), Ba = Concat(Bd, Be)
(2)
As the ego instance is initialized without temporal cues, which is important for planning, we devise
an instance memory queue with the size of (Nd + 1) × H for temporal modeling, H is the number of
stored frames. Then three types of interactions are performed to aggregate spatial-temporal context:
agent-temporal cross-attention, agent-agent self-attention and agent-map cross-attention. Note that
in temporal cross-attention of sparse perception module, the instances of current frame interact
with all temporal instances, which we name as scene-level interaction. While for agent-temporal
cross-attention here, we adopt instance-level interaction to make each instance focus on history
information of itself.
Then, we predict the multi-modal trajectories τm ∈RNd×Km×Tm×2, τp ∈RNc×Kp×Tp×2 and scores
sm ∈RNd×Km, sp ∈RNcmd×Kp for both surrounding agents and ego vehicle, Km and Kp are the
number of modes for motion prediction and planning, Tm and Tp are the number of future timestamps
for motion prediction and planning, and Ncmd is the number of driving command for planning.
Following the common practice[15, 20], we use three kinds of driving commands: turn left, turn right
and go straight. For planning, we additionally predict current ego status from ego instance feature.
Hierarchical Planning Selection.
Now we have the multi-modal planning trajectory proposals,
to select one safe trajectory τ ∗
p to follow, we design a hierarchical planning selection strategy. First,
we select a subset of trajectory proposals τp,cmd ∈Kp × Tp × 2, corresponding to the high-level
command cmd. Then, a novel collision-aware rescore module is adopted to ensure safety. With the
motion prediction results, we can assess the collision risk of each planning trajectory proposal, for
the trajectory with high collision probability, we reduce the score of this trajectory. In practice, we
simply set the score of collided trajectory to 0. Finally, we select the trajectory with the highest score
as the final planning output.
3.4
End-to-End Learning
Multi-stage Training.
The training of SparseDrive is divided into two stages. In stage-1, we train
symmetric sparse perception module from scratch to learn the sparse scene representation. In stage-2,
6


## Page 7

Table 1: Perception results on nuScenes val dataset. SparseDrive achieves best perfomance on all
perception tasks among end-to-end methods. †: Reproduced with offcial checkpoint.
Method
Backbone
mAP↑
mATE↓
mASE↓
mAOE↓
mAVE↓
mAAE↓
NDS↑
UniAD† [15]
ResNet101
0.380
0.684
0.277
0.383
0.381
0.192
0.498
SparseDrive-S
ResNet50
0.418
0.566
0.275
0.552
0.261
0.190
0.525
SparseDrive-B
ResNet101
0.496
0.543
0.269
0.376
0.229
0.179
0.588
(a) 3D detection results.
Method
AMOTA↑AMOTP↓Recall↑IDS↓
ViP3D [10]
0.217
1.625
0.363
-
QD3DT [12]
0.242
1.518
0.399
-
MUTR3D [54]
0.294
1.498
0.427
3822
UniAD [15]
0.359
1.320
0.467
906
SparseDrive-S
0.386
1.254
0.499
886
SparseDrive-B
0.501
1.085
0.601
632
(b) Multi-object tracking results.
Method
APped ↑APdivider ↑APboundry ↑mAP↑
HDMapNet [23]
14.4
21.7
33.0
23.0
VectorMapNet [34]
36.1
47.3
39.3
40.9
MapTR [29]
56.2
59.8
60.1
58.7
VAD† [20]
40.6
51.5
50.6
47.6
SparseDrive-S
49.9
57.0
58.4
55.1
SparseDrive-B
53.2
56.3
59.1
56.2
(c) Online mapping results.
sparse perception module and parallel motion planner are trained together with no model weights
frozen, fully enjoying the benefit of end-to-end optimization. More training details are provided in
Appendix B.4.
Loss Functions.
The loss functions include the loss of four tasks, and the loss of each task can be
further divider into classification loss and regression loss. For multi-modal motion prediction and
planning task, we adopt the winner-takes-all strategy. For planning, there is an additional regression
loss for ego status. We also introduce depth estimation as an auxiliary task to enhance the training
stability of the perception module. The overall loss function for end-to-end training is:
L = Ldet + Lmap + Lmotion + Lplan + Ldepth.
(3)
More details about loss functions are provided in Appendix B.3.
4
Experiments
Our experiments are conducted on challenging nuScenes[1] dataset, which contains 1000 complex
driving scenes, and each lasts for about 20 seconds. Evaluation metrics of each task are described in
Appendix A. We have two variants of the model, which only differ in backbone network and input
image resolution. For our small model SparseDrive-S, we use ResNet50[11] as backbone network
and the input image size is 256×704. For our base model, SparseDrive-B, we change backbone
network to ResNet101 and input image size to 512×1408. All experiments are conducted on 8
NVIDIA RTX 4090 24GB GPUs. More configuration details are provided in Appendix B.
4.1
Main Results
We compare with prior state-of-the-arts, both modularized and end-to-end methods. Among end-to-
end methods, our lightweight model SparseDrive-S has surpassed previous SOTAs in all tasks, while
our base model SparseDrive-B pushes the performance boundaries one step further. The main metrics
for each task are marked in grey background in Tables.
Perception.
For 3D detection in Tab. 1a, SparseDrive achieves 49.6% mAP and 58.8% NDS,
yielding a significant improvement of +11.6% mAP and +9.0% NDS compared to UniAD[15]. For
multi-object tracking in Tab. 1b, SparseDrive achieves 50.1% AMOTA, and lowest ID switch of
632, which surpasses UniAD[15] by +14.2% in terms of AMOTA and gets a 30.2% reduction for
ID switch, showing the temporal consistency of tracking tracklet. For online mapping in Tab. 1c,
SparseDrive gets a mAP of 56.2%, also surpassing previous end-to-end method VAD[20] by +8.6%.
7


## Page 8

Table 2: Motion prediction and planning results on nuScenes val dataset. SparseDrive outperforms
previous methods by a large margin. †: Reproduced with offcial checkpoint.
∗: LiDAR-based
methods.
Method
minADE(m)↓minFDE(m)↓MR↓EPA↑
Cons Pos. [15]
5.80
10.27
0.347
-
Cons Vel. [15]
2.13
4.01
0.318
-
Traditional [10]
2.06
3.02
0.277 0.209
PnPNet [28]
1.15
1.95
0.226 0.222
ViP3D [10]
2.05
2.84
0.246 0.226
UniAD[15]
0.71
1.02
0.151 0.456
SparseDrive-S
0.62
0.99
0.136 0.482
SparseDrive-B
0.60
0.96
0.132 0.555
(a) Prediction results.
Method
L2(m)↓
Col. Rate(%)↓
1s
2s
3s
Avg.
1s
2s
3s
Avg.
FF∗[13]
0.55 1.20 2.54 1.43 0.06 0.17 1.07 0.43
EO∗[22]
0.67 1.36 2.78 1.60 0.04 0.09 0.88 0.33
ST-P3 [14]
1.33 2.11 2.90 2.11 0.23 0.62 1.27 0.71
UniAD† [15]
0.45 0.70 1.04 0.73 0.62 0.58 0.63 0.61
VAD† [20]
0.41 0.70 1.05 0.72 0.03 0.19 0.43 0.21
SparseDrive-S
0.29 0.58 0.96 0.61 0.01 0.05 0.18 0.08
SparseDrive-B 0.29 0.55 0.91 0.58 0.01 0.02 0.13 0.06
(b) Planning results.
Prediction.
For motion prediction in Tab. 2a, SparseDrive achieves the best performance with
0.60m minADE, 0.96m minFDE, 13.2% MissRate and 0.555 EPA. Compared with UniAD[15],
SparseDrive reduces errors by 15.5% and 5.9% on minADE and minFDE respectively.
Planning.
For planning in Tab. 2b, among all methods, SparseDrive achieves a remarkable planning
performance, with the lowest L2 error of 0.58m and collision rate of 0.06%. Compared with previous
SOTA VAD[20], SparseDrive reduces L2 error by 19.4% and collision rate by 71.4%, demonstrating
the effectiveness and safety of our method.
Efficiency.
As shown in Tab. 3, besides the excellent performance, SparseDrive also achieves
much higher efficiency for both training and inference. With the same backbone network, our base
model achieves 4.8× faster in training and 4.1× faster in inference, compared with UniAD[15]. Our
lightweight model can achieve 7.2 × and 5.0× faster in training and inference.
Table 3: Efficiency comparison results. SparseDrive achieves high efficiency for both training and
inference. Training time and FPS for UniAD are measured on 8 and 1 NVIDIA Tesla A100 GPUs
respectively. Training time and FPS for SparseDrive are measured on 8 and 1 NVIDIA Geforce RTX
4090 GPUs respectively.
Method
Training Efficiency
Inference Efficiency
GPU Memory (G)
Batch Size
Time (h)
GPU Memory (M)
FLOPs (G)
Params (M)
FPS
UniAD [15]
50.0
1
48 + 96
2451
1709
125.0
1.8
SparseDrive-S
15.2
6
18 + 2
1294
192
85.9
9.0
SparseDrive-B
17.6
4
26 + 4
1437
787
104.7
7.3
4.2
Ablation Study
We conduct extensive ablation studies to demonstrate the effectiveness of our design choices. We use
SparseDrive-S as the default model for ablation experiments.
Effect of designs in Motion Planner.
To underscore the significance of considering similarity
between prediction and planning, we devised several specific experiments, as shown in Tab. 4.
ID-2 ignores the impact of ego vehicle on surrounding agents by changing the parallel design for
prediction and planning to sequential order, leading to worse performance for motion prediction
and collision rate. ID-3 randomly initializes ego instance feature and set all parameters of ego
anchor to 0. Removing the semantic and geometric information of ego instance leads to performance
degradation in both L2 error and collision rate. ID-4 takes planning as a deterministic problem
and only outputs one certain trajectory, resulting in highest collision rate. Moreover, ID-5 removes
the instance-level agent-temporal cross-attention, seriously degrading the L2 error to 0.77m. For
collision-aware rescore, we have detailed discussion in the following paragraph.
8


## Page 9

Collision-Aware Rescore.
In previous methods[15, 56], a post-optimization strategy is adopted to
ensure safety based on perception results. However, we argue that this strategy breaks the end-to-end
paradigm, resulting in serious degradation in L2 error, as shown in Tab. 5. Moreover, under our
re-implemented collision rate metric, the post-optimization does not make planning safer, but rather
more dangerous. By contrast, our collision-aware rescore module reduces collision rate from 0.12%
to 0.08%, with negligible increase in L2 error, showing the superiority of our method.
Multi-modal planning.
We conduct experiments on the number of planning modes. As shown
in Tab. 6, with the number of planning modes increases, the planning performance improves
continuously until saturated at 6 modes, again proving the importance of multi-modal planning.
Table 4: Ablation for designs in parallel motion planner. "PAL" means parallel design for motion
prediction and planning task; "EII" means ego instance initialization; "MTM" means multiple mode
for planning; "ATA" means agent-temporal cross-attention; "CAR" means collision-aware rescore.
ID
PAL
EII
MTM
ATA
CAR
Prediction
Planning L2(m)
Planning Coll.(%)
minADE
minFDE
MR
1s
2s
3s
Avg.
1s
2s
3s
Avg.
1
✓
✓
✓
✓
✓
0.623
0.987
0.136
0.29
0.58
0.96
0.61
0.01
0.05
0.18
0.08
2
✓
✓
✓
✓
0.641
1.008
0.138
0.30
0.58
0.95
0.61
0.02
0.06
0.23
0.10
3
✓
✓
✓
✓
0.621
0.988
0.135
0.31
0.60
0.98
0.63
0.03
0.07
0.21
0.11
4
✓
✓
✓
✓
0.626
1.002
0.136
0.33
0.66
1.08
0.69
0.03
0.11
0.60
0.25
5
✓
✓
✓
✓
0.634
1.003
0.138
0.40
0.74
1.16
0.77
0.02
0.13
0.32
0.16
6
✓
✓
✓
✓
0.623
0.987
0.136
0.29
0.58
0.95
0.61
0.01
0.06
0.30
0.12
Table 5: Ablation for collision-aware rescore and post-optimization in [15].
Method
CAR
Post-optim.
Planning L2(m)
Planning Coll.(%)
1s
2s
3s
Avg.
1s
2s
3s
Avg.
UniAD[15]
0.32
0.58
0.94
0.61
0.15
0.24
0.36
0.25
UniAD[15]
✓
0.45
0.70
1.04
0.73
0.62
0.58
0.63
0.61
SparseDrive
0.29
0.58
0.95
0.61
0.01
0.06
0.30
0.12
SparseDrive
✓
0.29
0.58
0.96
0.61
0.01
0.05
0.18
0.08
SparseDrive
✓
0.44
0.73
1.11
0.76
0.29
0.21
0.38
0.30
Table 6: Ablation for planning mode.
Number of mode
Planning L2(m)
Planning Coll.(%)
1s
2s
3s
Avg.
1s
2s
3s
Avg.
1
0.33
0.66
1.08
0.69
0.03
0.11
0.60
0.25
2
0.33
0.65
1.08
0.69
0.01
0.12
0.42
0.18
3
0.30
0.59
0.97
0.62
0.00
0.08
0.43
0.17
6
0.29
0.57
0.95
0.61
0.01
0.03
0.17
0.07
9
0.33
0.63
1.04
0.66
0.01
0.09
0.36
0.15
5
Conclusion and Future Work
Conclusion.
In this work, we explore the sparse scene representation and review the task design
in the realm of end-to-end autonomous driving. The resulting end-to-end paradigm SparseDrive
achieves both remarkable performance and high efficiency. We hope the impressive performance of
SparseDrive can inspire the community to rethink the task design for end-to-end autonomous driving
and promote technological progress in this field.
Future work.
There still are some limitations in our work. First, the performance of our end-to-end
model still falls behind the single-task method, for example, the online mapping task. Second, the
scale of the dataset is not large enough to exploit the full potential of end-to-end autonomous driving,
and the open-loop evaluation cannot comprehensively represent the model performance. We leave
these problems for future exploration.
9


## Page 10

References
[1] Holger Caesar, Varun Bankiti, Alex H Lang, Sourabh Vora, Venice Erin Liong, Qiang Xu, Anush Krishnan,
Yu Pan, Giancarlo Baldan, and Oscar Beijbom. nuscenes: A multimodal dataset for autonomous driving. In
Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pages 11621–11631,
2020.
[2] Nicolas Carion, Francisco Massa, Gabriel Synnaeve, Nicolas Usunier, Alexander Kirillov, and Sergey
Zagoruyko. End-to-end object detection with transformers. In European conference on computer vision,
pages 213–229. Springer, 2020.
[3] Sergio Casas, Wenjie Luo, and Raquel Urtasun. Intentnet: Learning to predict intention from raw sensor
data. In Conference on Robot Learning, pages 947–956. PMLR, 2018.
[4] Sergio Casas, Abbas Sadat, and Raquel Urtasun. Mp3: A unified model to map, perceive, predict and
plan. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages
14403–14412, 2021.
[5] Shaoyu Chen, Tianheng Cheng, Xinggang Wang, Wenming Meng, Qian Zhang, and Wenyu Liu. Efficient
and robust 2d-to-bev representation learning via geometry-guided kernel transformer. arXiv preprint
arXiv:2206.04584, 2022.
[6] Felipe Codevilla, Matthias Müller, Antonio López, Vladlen Koltun, and Alexey Dosovitskiy. End-to-
end driving via conditional imitation learning. In 2018 IEEE international conference on robotics and
automation (ICRA), pages 4693–4700. IEEE, 2018.
[7] Felipe Codevilla, Eder Santana, Antonio M López, and Adrien Gaidon. Exploring the limitations of
behavior cloning for autonomous driving. In Proceedings of the IEEE/CVF international conference on
computer vision, pages 9329–9338, 2019.
[8] Alexander Cui, Sergio Casas, Abbas Sadat, Renjie Liao, and Raquel Urtasun. Lookout: Diverse multi-
future prediction and planning for self-driving. In Proceedings of the IEEE/CVF International Conference
on Computer Vision, pages 16107–16116, 2021.
[9] Tri Dao, Dan Fu, Stefano Ermon, Atri Rudra, and Christopher Ré. Flashattention: Fast and memory-efficient
exact attention with io-awareness. Advances in Neural Information Processing Systems, 35:16344–16359,
2022.
[10] Junru Gu, Chenxu Hu, Tianyuan Zhang, Xuanyao Chen, Yilun Wang, Yue Wang, and Hang Zhao. Vip3d:
End-to-end visual trajectory prediction via 3d agent queries. In Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, pages 5496–5506, 2023.
[11] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition.
In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 770–778, 2016.
[12] Hou-Ning Hu, Yung-Hsu Yang, Tobias Fischer, Trevor Darrell, Fisher Yu, and Min Sun. Monocular quasi-
dense 3d object tracking. IEEE Transactions on Pattern Analysis and Machine Intelligence, 45(2):1992–
2008, 2022.
[13] Peiyun Hu, Aaron Huang, John Dolan, David Held, and Deva Ramanan. Safe local motion planning with
self-supervised freespace forecasting. In Proceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition, pages 12732–12741, 2021.
[14] Shengchao Hu, Li Chen, Penghao Wu, Hongyang Li, Junchi Yan, and Dacheng Tao. St-p3: End-to-
end vision-based autonomous driving via spatial-temporal feature learning. In European Conference on
Computer Vision, pages 533–549. Springer, 2022.
[15] Yihan Hu, Jiazhi Yang, Li Chen, Keyu Li, Chonghao Sima, Xizhou Zhu, Siqi Chai, Senyao Du, Tianwei
Lin, Wenhai Wang, et al. Planning-oriented autonomous driving. In Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition, pages 17853–17862, 2023.
[16] Junjie Huang and Guan Huang. Bevdet4d: Exploit temporal cues in multi-camera 3d object detection.
arXiv preprint arXiv:2203.17054, 2022.
[17] Junjie Huang and Guan Huang. Bevpoolv2: A cutting-edge implementation of bevdet toward deployment.
arXiv preprint arXiv:2211.17111, 2022.
[18] Junjie Huang, Guan Huang, Zheng Zhu, Yun Ye, and Dalong Du. Bevdet: High-performance multi-camera
3d object detection in bird-eye-view. arXiv preprint arXiv:2112.11790, 2021.
[19] Bo Jiang, Shaoyu Chen, Xinggang Wang, Bencheng Liao, Tianheng Cheng, Jiajie Chen, Helong Zhou,
Qian Zhang, Wenyu Liu, and Chang Huang. Perceive, interact, predict: Learning dynamic and static clues
for end-to-end motion prediction. arXiv preprint arXiv:2212.02181, 2022.
[20] Bo Jiang, Shaoyu Chen, Qing Xu, Bencheng Liao, Jiajie Chen, Helong Zhou, Qian Zhang, Wenyu Liu,
Chang Huang, and Xinggang Wang. Vad: Vectorized scene representation for efficient autonomous driving.
In Proceedings of the IEEE/CVF International Conference on Computer Vision, pages 8340–8350, 2023.
10


## Page 11

[21] Yanqin Jiang, Li Zhang, Zhenwei Miao, Xiatian Zhu, Jin Gao, Weiming Hu, and Yu-Gang Jiang. Polar-
former: Multi-camera 3d object detection with polar transformer. In Proceedings of the AAAI conference
on Artificial Intelligence, volume 37, pages 1042–1050, 2023.
[22] Tarasha Khurana, Peiyun Hu, Achal Dave, Jason Ziglar, David Held, and Deva Ramanan. Differentiable
raycasting for self-supervised occupancy forecasting. In European Conference on Computer Vision, pages
353–369. Springer, 2022.
[23] Qi Li, Yue Wang, Yilun Wang, and Hang Zhao. Hdmapnet: An online hd map construction and evaluation
framework. In 2022 International Conference on Robotics and Automation (ICRA), pages 4628–4634.
IEEE, 2022.
[24] Yinhao Li, Han Bao, Zheng Ge, Jinrong Yang, Jianjian Sun, and Zeming Li. Bevstereo: Enhancing depth
estimation in multi-view 3d object detection with temporal stereo. In Proceedings of the AAAI Conference
on Artificial Intelligence, volume 37, pages 1486–1494, 2023.
[25] Yinhao Li, Zheng Ge, Guanyi Yu, Jinrong Yang, Zengran Wang, Yukang Shi, Jianjian Sun, and Zeming Li.
Bevdepth: Acquisition of reliable depth for multi-view 3d object detection. In Proceedings of the AAAI
Conference on Artificial Intelligence, volume 37, pages 1477–1485, 2023.
[26] Zhiqi Li, Wenhai Wang, Hongyang Li, Enze Xie, Chonghao Sima, Tong Lu, Yu Qiao, and Jifeng Dai.
Bevformer: Learning bird’s-eye-view representation from multi-camera images via spatiotemporal trans-
formers. In European conference on computer vision, pages 1–18. Springer, 2022.
[27] Zhiqi Li, Zhiding Yu, Shiyi Lan, Jiahan Li, Jan Kautz, Tong Lu, and Jose M Alvarez. Is ego status all you
need for open-loop end-to-end autonomous driving? arXiv preprint arXiv:2312.03031, 2023.
[28] Ming Liang, Bin Yang, Wenyuan Zeng, Yun Chen, Rui Hu, Sergio Casas, and Raquel Urtasun. Pnpnet: End-
to-end perception and prediction with tracking in the loop. In Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, pages 11553–11562, 2020.
[29] Bencheng Liao, Shaoyu Chen, Xinggang Wang, Tianheng Cheng, Qian Zhang, Wenyu Liu, and Chang
Huang. Maptr: Structured modeling and learning for online vectorized hd map construction. In The
Eleventh International Conference on Learning Representations, 2022.
[30] Tsung-Yi Lin, Priya Goyal, Ross Girshick, Kaiming He, and Piotr Dollár. Focal loss for dense object
detection. In Proceedings of the IEEE international conference on computer vision, pages 2980–2988,
2017.
[31] Xuewu Lin, Tianwei Lin, Zixiang Pei, Lichao Huang, and Zhizhong Su. Sparse4d: Multi-view 3d object
detection with sparse spatial-temporal fusion. arXiv preprint arXiv:2211.10581, 2022.
[32] Xuewu Lin, Tianwei Lin, Zixiang Pei, Lichao Huang, and Zhizhong Su. Sparse4d v2: Recurrent temporal
fusion with sparse model. arXiv preprint arXiv:2305.14018, 2023.
[33] Xuewu Lin, Zixiang Pei, Tianwei Lin, Lichao Huang, and Zhizhong Su. Sparse4d v3: Advancing
end-to-end 3d detection and tracking. arXiv preprint arXiv:2311.11722, 2023.
[34] Yicheng Liu, Tianyuan Yuan, Yue Wang, Yilun Wang, and Hang Zhao. Vectormapnet: End-to-end
vectorized hd map learning. In International Conference on Machine Learning, pages 22352–22369.
PMLR, 2023.
[35] Yingfei Liu, Tiancai Wang, Xiangyu Zhang, and Jian Sun. Petr: Position embedding transformation for
multi-view 3d object detection. In European Conference on Computer Vision, pages 531–548. Springer,
2022.
[36] Yingfei Liu, Junjie Yan, Fan Jia, Shuailin Li, Aqi Gao, Tiancai Wang, and Xiangyu Zhang. Petrv2:
A unified framework for 3d perception from multi-camera images. In Proceedings of the IEEE/CVF
International Conference on Computer Vision, pages 3262–3272, 2023.
[37] Zhijian Liu, Haotian Tang, Alexander Amini, Xinyu Yang, Huizi Mao, Daniela L Rus, and Song Han.
Bevfusion: Multi-task multi-sensor fusion with unified bird’s-eye view representation. In 2023 IEEE
international conference on robotics and automation (ICRA), pages 2774–2781. IEEE, 2023.
[38] Ilya Loshchilov and Frank Hutter. Sgdr: Stochastic gradient descent with warm restarts. arXiv preprint
arXiv:1608.03983, 2016.
[39] Ilya Loshchilov and Frank Hutter.
Decoupled weight decay regularization.
arXiv preprint
arXiv:1711.05101, 2017.
[40] Wenjie Luo, Bin Yang, and Raquel Urtasun. Fast and furious: Real time end-to-end 3d detection, tracking
and motion forecasting with a single convolutional net. In Proceedings of the IEEE conference on Computer
Vision and Pattern Recognition, pages 3569–3577, 2018.
[41] Tim Meinhardt, Alexander Kirillov, Laura Leal-Taixe, and Christoph Feichtenhofer. Trackformer: Multi-
object tracking with transformers. In Proceedings of the IEEE/CVF conference on computer vision and
pattern recognition, pages 8844–8854, 2022.
11


## Page 12

[42] Jonah Philion and Sanja Fidler. Lift, splat, shoot: Encoding images from arbitrary camera rigs by implicitly
unprojecting to 3d. In Computer Vision–ECCV 2020: 16th European Conference, Glasgow, UK, August
23–28, 2020, Proceedings, Part XIV 16, pages 194–210. Springer, 2020.
[43] Dean A Pomerleau. Alvinn: An autonomous land vehicle in a neural network. Advances in neural
information processing systems, 1, 1988.
[44] Aditya Prakash, Kashyap Chitta, and Andreas Geiger. Multi-modal fusion transformer for end-to-end
autonomous driving.
In Proceedings of the IEEE/CVF conference on computer vision and pattern
recognition, pages 7077–7087, 2021.
[45] Abbas Sadat, Sergio Casas, Mengye Ren, Xinyu Wu, Pranaab Dhawan, and Raquel Urtasun. Perceive,
predict, and plan: Safe motion planning through interpretable semantic representations. In Computer
Vision–ECCV 2020: 16th European Conference, Glasgow, UK, August 23–28, 2020, Proceedings, Part
XXIII 16, pages 414–430. Springer, 2020.
[46] Peize Sun, Jinkun Cao, Yi Jiang, Rufeng Zhang, Enze Xie, Zehuan Yuan, Changhu Wang, and Ping Luo.
Transtrack: Multiple object tracking with transformer. arXiv preprint arXiv:2012.15460, 2020.
[47] Shihao Wang, Yingfei Liu, Tiancai Wang, Ying Li, and Xiangyu Zhang. Exploring object-centric temporal
modeling for efficient multi-view 3d object detection. In Proceedings of the IEEE/CVF International
Conference on Computer Vision, pages 3621–3631, 2023.
[48] Chenyu Yang, Yuntao Chen, Hao Tian, Chenxin Tao, Xizhou Zhu, Zhaoxiang Zhang, Gao Huang,
Hongyang Li, Yu Qiao, Lewei Lu, et al. Bevformer v2: Adapting modern image backbones to bird’s-eye-
view recognition via perspective supervision. In Proceedings of the IEEE/CVF Conference on Computer
Vision and Pattern Recognition, pages 17830–17839, 2023.
[49] Tengju Ye, Wei Jing, Chunyong Hu, Shikun Huang, Lingping Gao, Fangzhen Li, Jingke Wang, Ke Guo,
Wencong Xiao, Weibo Mao, et al. Fusionad: Multi-modality fusion for prediction and planning tasks of
autonomous driving. arXiv preprint arXiv:2308.01006, 2023.
[50] En Yu, Tiancai Wang, Zhuoling Li, Yuang Zhang, Xiangyu Zhang, and Wenbing Tao. Motrv3: Release-
fetch supervision for end-to-end multi-object tracking. arXiv preprint arXiv:2305.14298, 2023.
[51] Tianyuan Yuan, Yicheng Liu, Yue Wang, Yilun Wang, and Hang Zhao. Streammapnet: Streaming mapping
network for vectorized online hd map construction. In Proceedings of the IEEE/CVF Winter Conference
on Applications of Computer Vision, pages 7356–7365, 2024.
[52] Fangao Zeng, Bin Dong, Yuang Zhang, Tiancai Wang, Xiangyu Zhang, and Yichen Wei. Motr: End-to-end
multiple-object tracking with transformer. In European Conference on Computer Vision, pages 659–675.
Springer, 2022.
[53] Jiang-Tian Zhai, Ze Feng, Jinhao Du, Yongqiang Mao, Jiang-Jiang Liu, Zichang Tan, Yifu Zhang, Xiaoqing
Ye, and Jingdong Wang. Rethinking the open-loop evaluation of end-to-end autonomous driving in nuscenes.
arXiv preprint arXiv:2305.10430, 2023.
[54] Tianyuan Zhang, Xuanyao Chen, Yue Wang, Yilun Wang, and Hang Zhao. Mutr3d: A multi-camera
tracking framework via 3d-to-2d queries. In Proceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition, pages 4537–4546, 2022.
[55] Yuang Zhang, Tiancai Wang, and Xiangyu Zhang. Motrv2: Bootstrapping end-to-end multi-object tracking
by pretrained object detectors. In Proceedings of the IEEE/CVF Conference on Computer Vision and
Pattern Recognition, pages 22056–22065, 2023.
[56] Yunpeng Zhang, Deheng Qian, Ding Li, Yifeng Pan, Yong Chen, Zhenbao Liang, Zhiyao Zhang, Shurui
Zhang, Hongxu Li, Maolei Fu, et al. Graphad: Interaction scene graph for end-to-end autonomous driving.
arXiv preprint arXiv:2403.19098, 2024.
12


## Page 13

A
Metrics
The evaluation for detection and tracking follows standard evaluation protocols[1]. For detection, we use mean
Average Precision(mAP), mean Average Error of Translation(mATE), Scale(mASE), Orientation(mAOE),
Velocity(mAVE), Attribute(mAAE) and nuScenes Detection Score(NDS) to evaluate the model performance.
For tracking, we use Average Multi-object Tracking Accuracy(AMOTA), Average Multi-object Tracking
Precision(AMOTP), RECALL, and Identity Switches(IDS) as the metrics. For online mapping, we calculate
the Average Precision(AP) of three map classes: lane divider, pedestrian crossing and road boundary, then
average across all classes to get mean Average Precision(mAP). For motion prediction, we employ metrics
including minimum Average Displacement Error(minADE), minimum Final Displacement Error(minFDE),
Miss Rate(MR) and End-to-end Prediction Accuracy(EPA) proposed in [10]. The motion prediction benchmark
is aligned with UniAD[15].
For planning, we adopt commonly used L2 error and collision rate to evaluate the planning performance. The
evaluation of L2 error is aligned with VAD[20]. For collision rate, there are two drawbacks in previous [15, 20]
implementation, resulting in inaccurate evaluation in planning performance. On one hand, previous benchmark
convert obstacle bounding boxes into occupancy map with a grid size of 0.5m, resulting in false collisions in
certain cases, e.g. ego vehicle approaches obstacles that smaller than a single occupancy map pixel[53]. (2)
The heading of ego vehicle is not considered and assumed to remain unchanged[27]. To accurately evaluate the
planning performance, we account for the changes in ego heading by estimating the yaw angle through trajectory
points, and assess the presence of a collision by examining the overlap between the bounding boxes of ego
vehicle and obstacles. We reproduce the planning results on our benchmark with official checkpoints[15, 20] for
a fair comparison.
B
Implementation Details
B.1
Perception
For sparse perception module, we set the number of decoder layer Ndec to 6, which are 1 non-temporal decoder
and 5 temporal decoders. The location for anchor boxes Bd and anchor polylines Lm are obtained by K-Means
clustering on the training set, and other parameters of anchor boxes are initialized with {1, 1, 1, 0, 1, 0, 0, 0}.
Each map element is represented by 20 points. The number of anchor boxes Nd and polylines Nm are set to 900
and 100 respectively, and the number of temporal instances for detection and online mapping are 600 and 33.
The tracking threshold Tthresh is set to 0.2. For detection, the perception range is a circle with a radius of 55m.
For online mapping, the perception range is 60m × 30m longitudinally and laterally. For multi-head attention,
we adopt Flash Attention[9] to save the GPU memory.
B.2
Motion Planner
The number of stores frames H in instance memory queue is 3. The number of mode Km for motion prediction
and Kp for planning are both set to 6. The number of future timestamps Tm for motion prediction and Tp for
planning are set to 12 and 6 respectively. After spatial-temporal interactions in motion planner, we decode ego
status of current frame with ego feature Fe using a multi-layer perceptron (MLP):
EST = MLP(Fe)
(4)
For multi-modal trajectories and scores, we use K-Means clustering to obtain the prior intention points and
transform them into motion mode queries MQm ∈RKm×C and planning mode queries MQp ∈RNcmd×Kp×C
with sinusoidal position encoding PE(·), then we add mode queries with agent instance features, decode
trajectories and scores with MLPs:
τm = MLP(Fd + MQm),
(5)
sm = MLP(Fd + MQm),
(6)
τp = MLP(Fe + MQp),
(7)
sp = MLP(Fe + MQp)
(8)
In collision-aware rescore module, we utilize the two most confident trajectories in motion prediction to
determine whether ego vehicle will collide with surrounding obstacles.
B.3
Loss Functions
For perception, the Hungarian algorithm is adopted to match each ground truth with one predicted value. The
detection loss is a linear combination of a Focal loss[30] for classification and an L1 loss for box regression:
Ldet = λdet_clsLdet_cls + λdet_regLdet_reg.
(9)
13


## Page 14

As there are no tracking constraints in ID assignment process, we do not have a track loss. The online mapping
loss is similar to detection loss:
Lmap = λmap_clsLmap_cls + λmap_regLmap_reg.
(10)
For depth estimation, we use L1 loss for regression:
Ldepth = λdepthLdepth.
(11)
The loss weights are set as follows: λdet_cls = 2, λdet_reg = 0.25, λmap_cls = 1, λmap_reg = 10, λdepth =
0.2.
For motion prediction and planning, we calculate average displacement error (ADE) between multi-model output
and ground truth trajectory, the trajectory with lowest ADE is considered as positive sample and rest are negative
samples. For planning, ego status is additionally predicted. We also use Focal loss for classification and L1 loss
for regression:
Lmotion_planning = λmotion_clsLmotion_cls + λmotion_regLmotion_reg
+λplan_clsLplan_cls + λplan_regLplan_reg + λplan_statusLplan_status,
(12)
where λmotion_cls = 0.2, λmotion_reg = 0.2, λplan_cls = 0.5, λplan_reg = 1.0, λplan_status = 1.0.
B.4
Training Details
We use AdamW optimizer[39] and Cosine Annealing[38] scheduler for model training. The training hyperpa-
rameters are listed in Tab. 7.
Table 7: Training hyperparameters.
Model
Training stage
Batch Size
Epochs
Lr
Backbone lr scale
Weight decay
SparseDrive-S
stage-1
8
100
4 × 10−4
0.5
1 × 10−3
SparseDrive-S
stage-2
6
10
3 × 10−4
0.1
1 × 10−3
SparseDrive-B
stage-1
4
80
3 × 10−4
0.1
1 × 10−3
SparseDrive-B
stage-2
4
10
3 × 10−4
0.1
1 × 10−3
C
Visualization
14


## Page 15

Figure 5: Visualization results. SparseDrive learnes different turning modes at intersections.
15


## Page 16

Figure 6: Visualization results. SparseDrive learns to yield to moving agents or avoid collision with
obstacles.
16

