# FusionAD: Multi-modality Fusion for Prediction and Planning Tasks of Autonomous Driving

**Source**: arxiv PDF, 8 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

FusionAD: Multi-modality Fusion for Prediction and Planning Tasks of
Autonomous Driving
Tengju Ye2,∗, Wei Jing3,∗, Chunyong Hu3, Shikun Huang3, Lingping Gao3, Fangzhen Li3, Jingke Wang4,
Wencong Xiao4, Weibo Mao3, Ke Guo3, Hang Zheng3, Kun Li3, Junbo Chen2, Kaicheng Yu1
Abstract— Building a multi-modality multi-task neural net-
work toward accurate and robust performance is a de-facto
standard in perception task of autonomous driving. However,
leveraging such data from multiple sensors to jointly optimize
the prediction and planning tasks remains largely unexplored.
In this paper, we present FusionAD, to the best of our
knowledge, the first unified framework that fuse the information
from two most critical sensors, camera and LiDAR, goes beyond
perception task. Concretely, we first build a transformer based
multi-modality fusion network to effectively produce fusion
based features. In constrast to camera-based end-to-end method
UniAD, we then establish a fusion aided modality-aware pre-
diction and status-aware planning modules, dubbed FMSPnP
that take advantages of multi-modality features. We conduct
extensive experiments on commonly used benchmark nuScenes
dataset, our FusionAD achieves state-of-the-art performance
and surpassing baselines on average 15% on perception tasks
like detection and tracking, 10% on occupancy prediction
accuracy, reducing prediction error from 0.708 to 0.389 in ADE
score and reduces the collision rate from 0.31% to only 0.12%.
I. INTRODUCTION
Deep Learning has been accelerating the development of
Autonomous Driving (AD) in past few years. For self-driving
vehicles, the AD algorithm often take the camera and lidar
as sensory input, and output the control command. AD tasks
are often divided into perception, prediction and planning. In
traditional paradigm, each learning module in AD separately
uses its own backbones and learns the tasks independently.
Additionally, downstream tasks such as prediction and plan-
ning tasks often rely on vectorized representations from
perception results, while high-level semantic information is
often unavailable as in Figure 1 (Top).
Previously, the end-to-end learning based approaches often
directly output the control command or trajectory based
on the perspective-view camera and lidar information [2].
Recent end-to-end learning approaches [3]–[5] start to for-
mulate the end-to-end learning as a multi-task learning
problem, while outputs intermediate information along with
the planned trajectories. These approaches only adopt single
input modality. On the other hand, especially through fusion
with lidar and camera information for perception tasks, the
perception results could be significantly improved, which has
∗Equal contribution.
1Westlake University; 2Udeer.ai, Hangzhou, China; 3Cainiao Network,
Hangzhou, China; 4Alibaba Group, Hangzhou, China;
Email:
yetengju@gmail.com; kyu@westlake.edu.cn;
21wjing@gmail.com
Camera
C
BEV
Perception
C
L
Module 
Visual-centric End-to-end Pipeline
Post Fusion-based Pipeline
C
L
Proposed
FusionAD
C
LiDAR
L
Non-differentiable
Differentiable
Fig. 1: Comparing different design pipelines of the au-
tonomous driving system.
(Top) A common practice of
autonomous driving system, which consists of perception,
prediction, and planning tasks. Each task is an independent
task module that has its own input and output definition,
and the transition between modules usually requires non-
differentiable operations and prevents the system from being
optimized in an end-to-end manner. (Middle) It refers to a
recent end-to-end visual-centric system that learns percep-
tion, prediction and planning tasks [1]. (Bottom) We present
FusionAD, the first multi-modality and multi-task end-to-
end learning framework that enables joint optimization of
perception, prediction and planning tasks.
been validated in several previous work [6], [7]. Recently,
there has been a surge of interest in BEV (Bird’s Eye View)
perception, particularly for vision-centric perception [8], [9]
as depicted in Figure 1 (Middle). This development has
significantly advanced the capabilities of self-driving vehi-
cles and enabled a more natural fusion of vision and lidar
modalities. BEV fusion-based methods [2], [6], [7] have
demonstrated effectiveness, particularly for perception tasks.
However, the use of features from multi-modality sensors in
an end-to-end manner remains unexplored in prediction and
planning tasks.
arXiv:2308.01006v4  [cs.CV]  14 Aug 2023
### Page 2

To this end, we propose FusionAD, to the best of our
knowledge, the first uniform BEV multi-modality based,
multi-task end-to-end learning framework, with focus on pre-
diction and planning tasks for autonomous driving. We start
from a recent popular vision-centric approach to formulate
our pipeline [1]. First, we design a simple yet effective trans-
former architecture to fuse the multi-modality information
into one transformer, to produce a unified features in the
BEV space. As our primary focus is to explore the fusion
features to enhance the prediction and planning tasks, we
then formulate a fusion aided modality-aware prediction and
status-aware planning modules, dubbed FMSPnP, that incor-
porates progressive interaction and refinement and formulate
fusion-based collision loss modeling. Different from [1], our
FMSPnP module exploits a hierarchical pyramid formulation
as depicted in Figure 1 (Bottom), that ensures all tasks
can benefit from the intermediate perception features. The
proposed method better propagate high-level semantic infor-
mation, as well as efficiently share features among different
tasks.
We conduct extensive experiments in a popular au-
tonomous driving benchmark nuScenes [10] dataset, and
shows that our FusionAD significantly surpass the state-of-
the-art method: a 37% error reduction for trajectory predic-
tion, a 29% enhancement for occupancy prediction, and a
14% decrease in collision rates for planning.
The main contributions as summarized as follows:
• We propose a BEV-fusion based, multi-sensory, multi-
task, end-to-end learning approach for the main tasks
in autonomous driving; the fusion-based method greatly
improve the results compared to the camera-based BEV
method.
• We propose the FMSPnP module that incorporate
modality self-attention and refinement for prediction
task, as well as relaxed collision loss and fusion with
vectorized ego information for planning task. Experi-
ment studies verified that FMSPnP improves the pre-
diction and planning results.
• We conduct extensive studies in multiple tasks to val-
idate the effectiveness of the proposed method; the
experiment results shows FusionAD achieves SOTA re-
sults in prediction and planning tasks, while maintaining
competitive results in intermediate perception tasks.
II. RELATED WORK
A. BEV Perception
Bird’s Eye View (BEV) perception methods have gained
attention in autonomous driving for perceiving the surround-
ing environment. Camera-based BEV methods transform
multi-view camera image features into the BEV space,
enabling end-to-end perception without post-processing over-
lapping regions. LSS [11] and BEVDet [12] use image-
based depth prediction to build frustums and extract image
BEV features for map segmentation and 3D object detec-
tion. Building on this, BEVdet4D [13] and SoloFusion [14]
achieve temporal fusion by combining current frame BEV
features with aligned historical frame BEV features. BEV-
Former [8] uses spatiotemporal attention with transformers
to obtain temporally fused image BEV features. These ap-
proaches improve understanding of the dynamic environment
and enhance perception results.
However, camera-based perception methods suffer from
insufficient distance perception accuracy. LiDAR can offer
accurate location information, but its points are sparse. To
address this issue, some previous methods [2], [15] have ex-
plored the benefits of fusing multimodal data for perception.
BEV is a common perspective in LiDAR-based perception
algorithms [16], [17], and transforming multimodal features
into the BEV space facilitates fusion of these features. BEV-
Fusion [6], [7] concatenates image BEV features obtained by
the LSS [11] method with LiDAR BEV features obtained by
Voxelnet [18] to obtain fused BEV features, which improves
perception performance. SuperFusion [18] further proposes
multi-stage fusion for multi-modal based map perception.
B. Motion Forecasting
Following the success of VectorNet [19], mainstream
motion forecasting (or trajectory prediction) methods com-
monly utilize HD maps and vector-based obstacle represen-
tation to predict future trajectories of agents. Building upon
this foundation, LaneGCN [20] and PAGA [21] enhance
trajectory-map matching through refined map features, such
as lane connection attributes. Furthermore, certain anchor-
based methods [22], [23] sample target points near the map,
enabling trajectory prediction based on these points. How-
ever, these approaches heavily rely on pre-collected High-
definition maps, making them unsuitable for areas where
maps are not available.
Vectorized prediction methods often lack of the high-level
semantic information and requires HD Map, thus, recent
work starts to use raw sensory information for trajectory pre-
diction. PnPNet [24] proposes a novel tracking module that
generates object tracks online from detection and exploits tra-
jectory level features for motion forecasting, but their overall
framework is based on CNN, and the motion forecasting
module is relatively simple, with only single-mode output.
As the transformer is applied to detection [25] and track-
ing [26], VIP3D [27] successfully draws on previous work
and proposes the first transformer-based joint perception-
prediction framework. Uniad [3] further incorporates more
downstream tasks and proposes a planning-oriented end-to-
end autonomous driving model. On the basis of our prede-
cessors, we have carried out more refined optimization for
the task of motion forecasting and introduced the refinement
mechanism and mode-attention, which has greatly improved
the prediction indicators.
C. Learning for Planning
Imitation Learning (IL) and Reinforcement Learning (RL)
have been used for planning [28]. IL and RL are used in
either an end-to-end approach [29], [30] (i.e. using image
and/or lidar as input), or vectorized approach [31], [32]
(i.e. using vectorized perception results as input). Even
### Page 3

FMSPnP
Points Cross-Attn
Add & Norm
Feed Forward
Add & Norm
Images Cross-Attn
Add & Norm
Temporal Self-Attn
Add & Norm
Fusion Encoder
Tracking
Mapping
Perception
Prediction
Planning
Modality Self-Attn
Refinement 
Network
Ego
Status
Collision Loss
position
velocity
heading
…
Fig. 2: FusionAD Architecture Overview - FusionAD employs BEVfusion to facilitate multi-sensory, multi-task end-to-
end learning specifically tailored for autonomous driving. The architecture primarily focuses on enhancing prediction and
planning tasks, utilizing the fusion aided modality-aware prediction and status-aware planning modules (FMSPnP) for these
specific tasks.
though using intermediate perception results for planning can
improve the generalization and transparency, vectorized ap-
proach suffers from the post-processing noise and variations
of the perception results. Early end-to-end approach such
as ALVINN [33] and PilotNet [34] often output the control
command or trajectory directly, while lacking of intermediate
results/tasks. Instead, P3 [35], MP3 [4], UniAD [3] learn an
end-to-end learnable network that performs joint perception,
prediction and planning, which can produce interpretable
intermediate representation and improve the final planning
performance. However, they either only make use of the
lidar input [4], [35] or the camera input [3], which limits
their performance. Transfuser [36] uses both lidar and camera
input, but not in BEV space and only perform few AD
learning tasks as auxiliary tasks. To address the issue, we
propose a BEV fusion based, unified multi-modal, multi-task
framework that absorbs both the lidar and camera input.
III. METHOD
The overall network architecture of our proposed Fu-
sionAD is illustrated in Figure 2. Initially, the camera images
are mapped to the Bird’s Eye View (BEV) space using a
BEVFormer-based image encoder. These are then combined
with the lidar features in BEV space. Following temporal
fusion, the fused BEV features are used for detection,
tracking, and mapping tasks though query-based approach.
Subsequently, the tokens are forwarded to the motion and
occupancy prediction tasks and planning tasks. We name
our fusion aided modality-aware prediction and status-aware
planning modules as FMSPnP in short.
A. BEV Encoder and Perception
Drawing inspiration from FusionFormer [37], we propose
a novel multi-modal temporal fusion framework for 3D
object detection with a Transformer-based architecture. To
improve efficiency, we adopt a recurrent temporal fusion
technique that is similar to BEVFormer. Unlike Fusion-
Former, we use feature in BEV format as input for the
LiDAR branch instead of voxel features. The multi-modal
temporal fusion module comprises 6 encoding layers, as
illustrated in Figure 1. A group of learnable BEV querier
is first employed to fuse LiDAR features and image features
using Points cross-attention and Image cross-attention, re-
spectively. We then fuse the resulting features with historical
BEV features from the previous frame via Temporal self-
attention. The queries is updated by a feedforward network
before being used as input for the next layer. After 6 layers of
fusion encoding, the final multi-modal temporal fused BEV
features are generated for the subsequent tasks.
LiDAR. The raw LiDAR point cloud data is first voxelized,
and then used to generate LiDAR BEV features based on the
SECOND network.
Camera. The multi-view camera images are first processed
through a backbone network for feature extraction. After-
wards, the FPN network is employed to generate multi-scale
image features.
We further develop the following techniques to efficiently
improve the performance of fusion module.
Points Cross-Attention. During the points cross-attention
process, each BEV query only interacts with the LiDAR
BEV features around its corresponding reference points. This
interaction is achieved using deformable attention:
PCA(Qp, BLiDAR) = DefAttn(Qp, P, BLiDAR)
(1)
where Qp represents the BEV query at point p = (x, y),
and BLiDAR represents the BEV feature output from the
LiDAR branch. P is the projection of the coordinate p=(x,y)
in the BEV space onto the LiDAR BEV space.
Image
Cross-Attention.
To
implement
image
cross-
attention, we follow a similar approach to BEVFormer. Each
BEV query is expand with a height dimension similar to the
### Page 4

A2A
Cross-Attn
global
anchor
𝑎!
Embed
+
A2G
Cross-Attn
query embedding
map embedding
BEV
embedding
A2M
Cross-Attn
𝐾/𝑉
𝐾/𝑉
𝐾/𝑉
||
Modality
Self-Attn
current
position
𝑥"
prediction
𝑥#!
#$%
𝑥#!
#
Embed
Embed
Embed
Trajectory Generation
Displacement Generation
Modality
Self-Attn
𝑥#!
&
…
…
x L
+
Embed
Embed
Embed
+
PE
MLP
Embed
+
add
concatenate
||
Legend
Fig. 3: Design of the prediction module in FMSPnP. There are mainly two stages including trajectory generation with
the Modality Self-attention and displacement generation, where two stages share a similar backbone structure.
Pillar representation. A fixed number of Nref 3D reference
points are sampled in each pillar along its Z-axis. And the
image cross-attention process is shown below:
ICA(Qp, F) =
1
Vhit
Vhit
X
i=1
Nref
X
j=1
DefAttn(Qp, P(p, i, j), Fi)
(2)
where Vhit denotes the number of camera views to which
the reference point can be projected, i is the index of the
camera view, Fi represents the image feature of the i-th
camera, and P(p, i, j) represents the projection of the 3D
reference point (x, y, zi) of the BEV Query Qp onto the
image coordinate system of the i-th camera.
Temporal Self-Attention. We also leverage the insights
from BEVFormer to implement Temporal Self-Attention.
Specifically, our approach involves temporal alignment of the
historical frame BEV features based on the vehicle’s motion
between frames. We then utilize Temporal Self-Attention to
fuse historical frame BEV features, as shown below:
TSA(Qp, (Q, B
′
t−1)) =
X
V ∈{Q,B′
t−1}
DefAttn(Qp, p, V ) (3)
where B
′
t−1 represents the BEV features at timestamp t−1
after temporal alignment.
Since we are interested in the prediction and planning
enhancement, for the detection, tracking and mapping tasks
in perception, we mainly follow the setting in UniAD [3].
B. Prediction
Benefiting from the more informative BEV features, pre-
diction module receives more stable and fine-grained in-
formation. Based on this, in order to further capture the
multi-modal distribution and improve prediction accuracy,
we introduce modality self-attention and refinement net.
Details of the design can be found in Figure 3.
Context-Informed Mode attention. In UniAD [3], dataset-
level statistical anchors are used to assist multimodal tra-
jectory learning, and inter-anchor self-attention is applied to
enhance the quality of the anchors. However, since these
anchors does not consider historical state and map infor-
mation, their contribution to multimodal learning is limited.
Therefore, we are considering adding this operation later.
After the motion query retrieves all scene context to capture
agent-agent, agent-map, and agent-goal point information,
We then introduce mode self-attention to enable mutual
visibility between the various modes, leading to better quality
and diversity.
Qmode = MHSA(Qu)
(4)
where MHSA denotes multi-head self-attention. Qu repre-
sents the query that obtains the context information.
Refinement Network. Deformable attention uses statistical
anchors as reference trajectories to interact with Bev features.
As mentioned earlier, this reference trajectory increases the
difficulty of subsequent learning due to the need for specific
scene information. We introduce a refinement net to use
the trajectories generated by Motionformer as more accurate
spatial priors, query the scene context, and predict the offset
between the ground truth trajectory and the prior trajectory
at this stage. As shown below:
QR = DefAttn(Anchorp, bxm, B)
(5)
where Anchorp represents the spatial prior. A simple MLP
will be used to encode the trajectory output by Motionformer,
and perform maxpool in the time dimension to get Anchorp.
bxm represents the end point of the Motionformer output
trajectory.
C. Planning
During the evaluation process, we do not have access to
high-definition (HD) maps or pre-defined routes. Therefore,
we rely on learnable command embeddings to represent
### Page 5

TABLE I: Main results for multi-tasks, end-to-end learning; ∗denotes evaluation using checkpoints from official implemen-
tation.
Detection
Tracking
Mapping
Prediction
Occupancy
Planning
mAP ↑NDS ↑AMOTA ↑AMOTP ↓IoU-Lane ↑IoU-D ↑ADE↓FDE↓MR↓EPA ↑VPQ-n↑VPQ-f↑IoU-n↑IoU-f↑DE ↓CRavg ↓CRtraj ↓
UniAD
0.382*
0.499*
0.359
1.320
0.313
0.691
0.708
1.025 0.151
0.456
54.7
33.5
63.4
40.2
1.03
0.31
1.46*
FusionAD
0.574
0.646
0.501
1.065
0.367
0.731
0.389
0.615 0.084
0.620
64.7
50.2
70.4
51.0
0.81
0.12
0.37
local command
𝑆!
Embed
turn right
ego status
𝐶
+
tracking
feature
motion
feature
𝑓"
𝑓!
BEV Cross-Attn
BEV 
embedding
𝐾/𝑉
MLP
MLP
||
𝑝, 𝑣, 𝑎
MLP
occupancy
Nonlinear
Optimization
Fig. 4: Design of the planning module in FMSPnP.
We enhance the current state sensitivity by injecting ego
information.
navigation signals (including turning left, turning right, and
keeping forward) to guide the direction. To obtain the sur-
rounding embedding, we input the plan query, which consists
of the ego-query and command embedding, into bird’s-eye-
view (BEV) features. We then fuse this with the ego vehicle’s
embedding, which is processed by a MLP network, to obtain
the state embedding. This state embedding is then decoded
into the future waypoint ˆτ.
To ensure safety, during training, we incorporate a differ-
entiable relaxation of the collision loss as [38], in addition to
the naive imitation L2 loss. We present the complete design
in Figure 4.
Ltra = λcolLcol(ˆτ, b) + λimiLimi(ˆτ, eτ)
(6)
where λimi = 1, λcol = 2.5, ˆτ is the original planning
results, eτ denotes the planning labels,and b indicates agents
forecasted in the scene. The collision loss is calculated by:
Lcol(ˆτ, b) =
1
N 2
N
X
i=0
max
 
1,
P
X
t=0
Lpair
 ˆτ t, bt
i

!
Lpair
 ˆτ t, bt
i

=
(
1 −
d
ri+rj ,
if d ≤ri + rj
0,
otherwise
(7)
Besides, during inference, to further ensure safety and
smoothness of the trajectory, we perform trajectory optimiza-
tion using Newton’s method [3] using occupancy prediction
results from the occupancy prediction model.
D. Training
We utilize three stage training for the multi-sensor, multi-
task learning. For the first stage, we only train the BEV
encoder and perception tasks; for the second stage, we fix
the BEV encoder and train the perception, prediction and
planning tasks; while for an optional third stage, we further
trains the occupancy and planning tasks, with fixing all other
components.
IV. EXPERIMENTS
A. Experiment Setup
We conduct all our experiments on A100 GPU cluster,
utilizing 32 A100 GPUs for the experiment training. We
use the nuScenes dataset [10], comprising 1000 driving
scenes captured in both Boston and Singapore. Each scene
spans approximately 20 seconds, and nuScenes offers a vast
collection of 1.4 million 3D bounding boxes encompassing
23 distinct categories, sampled at 2Hz. For our work, we
use of the available camera, lidar, and canbus data. For the
hyperparameters, we use 0.075 × 0.075 × 0.2m for lidar
pointcloud; we use the resolution of 1600 × 900 for image;
the BEV size is 200 × 200; we use AdamW optimizer with
the start learning rate of 2e−4, warm-up of 1000 iteration is
used and CosineAnnealing scheduling is used; the batch size
is 1 due to the high GPU memory consumption; the queue
size is 5 for stage one, and 3 for stage two and three.
We follow [1] to evaluate the performance of end-to-end
autonomous driving tasks. Specifically, for the metrics of
perception tasks, we use mAP and NDS to evaluate the
detection task, AMOTA and AMOTP to evaluate the tracking
task, IoU to evaluate the mapping task.
To evaluate the prediction and planning tasks, we use
commonly used metrics, such as End-to-end Prediction Ac-
curacy (EPA), Average Displacement Error (ADE), Final
Displacement Error (FDE), and Miss Rate (MR) to evaluate
the performance of motion prediction. For future occupancy
prediction, we use the metrics Future Video Panoptic Quality
(VPQ) and IoU for near (30 × 30m) and far (100 × 100m)
range, adopted from FIERY [39]. And we adopt Displace-
ment Error (DE) and Collision Rate (CR) to evaluate the
planning performance, where the collision rate considered
as the main metrics.
B. Experiment Results
The main experimental results are shown in Table I. We
can see that our design of fusing camera and Lidar sensory
### Page 6

TABLE II: The results of motion forecasting FusionAD
remarkably outperforms previous methods.
Method
minADE ↓minFDE ↓MR ↓EPA ↑
PnPNet [24]
1.15
1.95
0.226 0.222
VIP3D [27]
2.05
2.84
0.246 0.226
UniAD [3]
0.71
1.02
0.151 0.456
FusionAD
0.388
0.617
0.086 0.626
TABLE III: The results of occupancy prediction FusionAD
remarkably outperforms previous methods on all metrics.
"n." and "f." indicates near (30×30m) and far (100×100m)
evaluation ranges respectively.
Method
IoU-n ↑IoU-f ↑VPQ-n ↑VPQ-f ↑
FIERY [39]
59.4
36.7
50.2
29.9
StretchBEV [41]
55.5
37.1
46.0
29.0
ST-P3 [42]
-
38.9
-
32.1
BEVerse [43]
61.4
40.9
54.3
36.1
PowerBEV [44]
62.5
39.3
55.5
33.8
UniAD [3]
63.4
40.2
54.7
33.5
FusionAD
71.2
51.5
65.5
51.1
TABLE IV: Planning Results: FusionAD achieves the state-
of-the-art performance in the most critical metrics, average
collision rate and trajectory collision rate, surpassing both
planning only methods [5] as well as end-to-end method [1]
Method
DEavg CR1s CR2s CR3s CRavg CRtraj
FF [45]
1.43
0.06
0.17
1.07
0.43
-
EO [46]
1.60
0.04
0.09
0.88
0.33
-
ST-P3 [42]
2.11
0.23
0.62
1.27
0.71
-
VAD [5]
0.37
0.07
0.10
0.24
0.14
-
UniAD [3]
1.03
0.05
0.17
0.71
0.31
1.46∗
FusionAD
0.81
0.02
0.08
0.27
0.12
0.37
information significantly improve the performance of almost
all tasks, compared to the UniAD baseline [1]. Note that we
do not include any data augmentation methods, which are
commonly used for perception tasks.
The motion forecasting results are shown in Table II.
FusionAD significantly outperforms existing methods. For
the future occupancy prediction, we also observed that Fu-
sionAD performs much better than existing methods, espe-
cially for IoU-f and VPQ-f in (100×100m) range, as shown
in Table III, this indicates the fusion of lidar information is
helpful for longer range.
Table IV presents the planning results, demonstrating Fu-
sionAD’s superior performance compared to existing meth-
ods, as indicated by its lowest average and total collision
rates. CRtraj denote the collision rate among whole 3-second
trajectory, while CRavg adopted from [3] denotes the average
collision rate of trajecotory at 1,2 and 3 second. Furthermore,
FusionAD achieves the second lowest L2 distance, which
serves as a reference metric to assess the similarity between
the planned trajectory and the ground truth. It is important to
note that the collision rate is the primary metric [32], [40],
whereas in real-world scenarios, multiple viable trajectories
may exist, making the L2 distance a secondary consideration.
C. Ablation Studies
The ablation studies pertaining to the FMSPnP module
are presented in Tables V and VI. Upon examination, it
becomes evident that the refinement net and mode attention
module significantly contribute to enhancing the predic-
tion outcomes. In terms of planning results, a noticeable
improvement is observed when fusion with a vectorized
representation of past trajectories and ego status.
TABLE V: Ablation studies for designs in the motion fore-
casting module.
ID Refine Mode minADE ↓minFDE ↓MR ↓minFDE-mAP ↑EPA ↑
1
0.394
0.636
0.088
0.507
0.622
2
✓
0.395
0.627
0.086
0.516
0.624
3
✓
✓
0.388
0.617
0.086
0.516
0.626
TABLE VI: Ablation studies for designs in the planning
module.
ID loss ego status DEavg CR1s CR2s CR3s CRavg CRtraj
1
1.08
0.28
0.13
0.32
0.24
0.71
2
✓
1.03
0.25
0.13
0.25
0.21
0.56
3
✓
✓
0.81
0.02
0.08
0.27
0.12
0.37
D. Qualitative Results
The comparative qualitative results between FusionAD
and UniAD are depicted in Figure 5. The integration of
Lidar sensory inputs and the novel design of FMSPnP
module in FusionAD demonstrates an enhancement in per-
ception and prediction performance. For instance, Figure 5a
illustrates a significant heading error in the bus detection
by UniAD, attributable to the distortion from the camera,
particularly in the overlapping region between the front
and front-right cameras. In contrast, FusionAD accurately
identifies the bus’s heading. Figure 5b presents a prediction
scenario involving a U-turn. FusionAD consistently predicts
U-turn trajectories, whereas UniAD generates moving for-
ward, left-turn, and U-turn modes. Please see videos on our
project page, https://github.com/westlake-autolab/FusionAD,
for more details.
E. Discussion
While the proposed method demonstrates strong quantita-
tive and qualitative performances, it still relies on a rule-
based system for post-processing the output in order to
achieve reliable real-world performance. Furthermore, the
current research work [3], [5], [42] primarily evaluates the
learned planner using open-loop results of planning tasks,
which may not effectively gauge its performance. Evaluating
the planner in a close-loop manner with real-world percep-
tion data poses challenges. Nonetheless, the prediction results
under the end-to-end framework remain promising, and there
is potential for further improvement of the planning module
within this framework.
### Page 7

(a) Case 1: Perception of a bus. FusionAD detects the heading correctly while distorsion exists in near range, but UniAD incorrectly
predicts the heading.
(b) Case 2: Prediction of U-turn. FusionAD consistantly predicts the U-turn earlier in all modes which aligns with the ground-truth trace,
while UniAD still predicts the move-foward, left-turn and U-turn modes until the very last second U-turn actually happens.
Fig. 5: Visual comparison of two example cases between UniAD [1] (Top) and our FusionAD (Bottom).
V. CONCLUSIONS
We propose FusionAD, a novel approach that leverages
BEV fusion to facilitate multi-sensory, multi-task, end-to-end
learning, thereby significantly enhancing prediction and plan-
ning tasks in the realm of autonomous driving. The proposed
method underscores the potential of extending a uniform end-
to-end framework to fusion-based methodologies effectively.
The proposed approach has yielded substantial performance
improvements in both prediction and planning tasks, and has
notably improved perception tasks when compared to end-
to-end learning methods solely reliant on camera-based BEV.
### Page 8

REFERENCES
[1] Y. Hu, J. Yang, L. Chen, K. Li, C. Sima, X. Zhu, S. Chai, S. Du,
T. Lin, W. Wang, L. Lu, X. Jia, Q. Liu, J. Dai, Y. Qiao, and H. Li,
“Planning-oriented autonomous driving,” 2022.
[2] X. Bai, Z. Hu, X. Zhu, Q. Huang, Y. Chen, H. Fu, and C.-L. Tai,
“TransFusion: Robust lidar-camera fusion for 3d object detection with
transformers,” in CVPR, 2022.
[3] Y. Hu, J. Yang, L. Chen, K. Li, C. Sima, X. Zhu, S. Chai, S. Du,
T. Lin, W. Wang, L. Lu, X. Jia, Q. Liu, J. Dai, Y. Qiao, and
H. Li, “Planning-oriented autonomous driving,” in Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern Recognition,
2023.
[4] S. Casas, A. Sadat, and R. Urtasun, “Mp3: A unified model to map,
perceive, predict and plan,” in CVPR, 2021.
[5] B. Jiang, S. Chen, Q. Xu, B. Liao, J. Chen, H. Zhou, Q. Zhang, W. Liu,
C. Huang, and X. Wang, “Vad: Vectorized scene representation for
efficient autonomous driving,” arXiv preprint arXiv:2303.12077, 2023.
[6] Z. Liu, H. Tang, A. Amini, X. Yang, H. Mao, D. Rus, and S. Han,
“BEVFusion: Multi-task multi-sensor fusion with unified bird’s-eye
view representation,” in ICRA, 2023.
[7] T. Liang, H. Xie, K. Yu, Z. Xia, Z. Lin, Y. Wang, T. Tang, B. Wang,
and Z. Tang, “BEVFusion: A simple and robust lidar-camera fusion
framework,” in NeurIPS, 2022.
[8] Z. Li, W. Wang, H. Li, E. Xie, C. Sima, T. Lu, Q. Yu, and J. Dai,
“BEVFormer: Learning bird’s-eye-view representation from multi-
camera images via spatiotemporal transformers,” in ECCV, 2022.
[9] H. Li, C. Sima, J. Dai, W. Wang, L. Lu, H. Wang, E. Xie, Z. Li,
H. Deng, H. Tian, X. Zhu, L. Chen, Y. Gao, X. Geng, J. Zeng,
Y. Li, J. Yang, X. Jia, B. Yu, Y. Qiao, D. Lin, S. Liu, J. Yan, J. Shi,
and P. Luo, “Delving into the devils of bird’s-eye-view perception:
A review, evaluation and recipe,” arXiv preprint arXiv:2209.05324,
2022.
[10] H. Caesar, V. Bankiti, A. H. Lang, S. Vora, V. E. Liong, Q. Xu,
A. Krishnan, Y. Pan, G. Baldan, and O. Beijbom, “nuscenes: A
multimodal dataset for autonomous driving,” in CVPR, 2020.
[11] J. Philion and S. Fidler, “Lift, splat, shoot: Encoding images from
arbitrary camera rigs by implicitly unprojecting to 3d,” in ECCV, 2020.
[12] J. Huang, G. Huang, Z. Zhu, and D. Du, “BEVDet: High-performance
multi-camera 3d object detection in bird-eye-view,” arXiv preprint
arXiv:2112.11790, 2021.
[13] J. Huang and G. Huang, “BEVDet4D: Exploit temporal cues in multi-
camera 3d object detection,” arXiv preprint arXiv:2203.17054, 2022.
[14] J. Park, C. Xu, S. Yang, K. Keutzer, K. Kitani, M. Tomizuka, and
W. Zhan, “Time will tell: New outlooks and a baseline for temporal
multi-view 3d object detection,” arXiv preprint arXiv:2210.02443,
2022.
[15] T. Yin, X. Zhou, and P. Krähenbühl, “Multimodal virtual point
3d detection,” Advances in Neural Information Processing Systems,
vol. 34, pp. 16494–16507, 2021.
[16] T. Yin, X. Zhou, and P. Krahenbuhl, “Center-based 3d object detection
and tracking,” in CVPR, 2021.
[17] A. H. Lang, S. Vora, H. Caesar, L. Zhou, J. Yang, and O. Beijbom,
“Pointpillars: Fast encoders for object detection from point clouds,”
in Proceedings of the IEEE/CVF conference on computer vision and
pattern recognition, pp. 12697–12705, 2019.
[18] Y. Zhou and O. Tuzel, “Voxelnet: End-to-end learning for point cloud
based 3d object detection,” in Proceedings of the IEEE conference on
computer vision and pattern recognition, pp. 4490–4499, 2018.
[19] J. Gao, C. Sun, H. Zhao, Y. Shen, D. Anguelov, C. Li, and C. Schmid,
“Vectornet: Encoding hd maps and agent dynamics from vectorized
representation,” in CVPR, 2020.
[20] M. Liang, B. Yang, R. Hu, Y. Chen, R. Liao, S. Feng, and R. Urta-
sun, “Learning lane graph representations for motion forecasting,” in
ECCV, 2020.
[21] F. Da and Y. Zhang, “Path-aware graph attention for hd maps in
motion prediction,” in 2022 International Conference on Robotics and
Automation (ICRA), pp. 6430–6436, IEEE, 2022.
[22] H. Zhao, J. Gao, T. Lan, C. Sun, B. Sapp, B. Varadarajan, Y. Shen,
Y. Shen, Y. Chai, C. Schmid, C. Li, and D. Anguelov, “TNT: Target-
driven trajectory prediction,” in CoRL, 2020.
[23] J. Gu, C. Sun, and H. Zhao, “Densetnt: End-to-end trajectory predic-
tion from dense goal sets,” in ICCV, 2021.
[24] M. Liang, B. Yang, W. Zeng, Y. Chen, R. Hu, S. Casas, and R. Urtasun,
“Pnpnet: End-to-end perception and prediction with tracking in the
loop,” in CVPR, 2020.
[25] N. Carion, F. Massa, G. Synnaeve, N. Usunier, A. Kirillov, and
S. Zagoruyko, “End-to-end object detection with transformers,” in
ECCV, 2020.
[26] F. Zeng, B. Dong, T. Wang, X. Zhang, and Y. Wei, “Motr: End-to-end
multiple-object tracking with transformer,” in ECCV, 2021.
[27] J. Gu, C. Hu, T. Zhang, X. Chen, Y. Wang, Y. Wang, and H. Zhao,
“ViP3D: End-to-end visual trajectory prediction via 3d agent queries,”
in CVPR, 2023.
[28] L. Gao, Z. Gu, C. Qiu, L. Lei, S. E. Li, S. Zheng, W. Jing, and J. Chen,
“Cola-hrl: Continuous-lattice hierarchical reinforcement learning for
autonomous driving,” in IEEE/RSJ International Conference on Intel-
ligent Robots and Systems (IROS), pp. 13143–13150, 2022.
[29] A. Kendall, J. Hawke, D. Janz, P. Mazur, D. Reda, J.-M. Allen, V.-D.
Lam, A. Bewley, and A. Shah, “Learning to drive in a day,” in ICRA,
2019.
[30] J. Chen, S. E. Li, and M. Tomizuka, “Interpretable end-to-end urban
autonomous driving with latent deep reinforcement learning,” IEEE
Transactions on Intelligent Transportation Systems, vol. 23, pp. 5068–
5078, 2020.
[31] O. Scheel, L. Bergamini, M. Wolczyk, B. Osi´nski, and P. Ondruska,
“Urban Driver: Learning to drive from real-world demonstrations using
policy gradients,” in Conference on Robot Learning (CoRL), pp. 718–
728, 2022.
[32] K. Guo, W. Jing, J. Chen, and J. Pan, “CCIL: Context-conditioned
imitation learning for urban driving,” in Robotics: Science and Systems
(RSS), 2023.
[33] D. A. Pomerleau, “Alvinn: An autonomous land vehicle in a neural
network,” in NeurIPS, 1988.
[34] M. Bojarski, D. Del Testa, D. Dworakowski, B. Firner, B. Flepp,
P. Goyal, L. D. Jackel, M. Monfort, U. Muller, J. Zhang, X. Zhang,
J. Zhao, and Z. Karol, “End to end learning for self-driving cars,”
arXiv preprint arXiv:1604.07316, 2016.
[35] A. Sadat, S. Casas, M. Ren, X. Wu, P. Dhawan, and R. Urtasun, “Per-
ceive, predict, and plan: Safe motion planning through interpretable
semantic representations,” in ECCV, 2020.
[36] A. Prakash, K. Chitta, and A. Geiger, “Multi-modal fusion transformer
for end-to-end autonomous driving,” in CVPR, 2021.
[37] C. Hu, “Fusionformer: Unified multi-modal and temporal fusion with
transformer for 3d detection in bird’s-eye-view,” 2023.
[38] S. Suo, S. Regalado, S. Casas, and R. Urtasun, “Trafficsim: Learning to
simulate realistic multi-agent behaviors,” 2021 IEEE/CVF Conference
on Computer Vision and Pattern Recognition (CVPR), pp. 10395–
10404, 2021.
[39] A. Hu, Z. Murez, N. Mohan, S. Dudas, J. Hawke, V. Badrinarayanan,
R. Cipolla, and A. Kendall, “FIERY: Future instance prediction in
bird’s-eye view from surround monocular cameras,” in ICCV, 2021.
[40] H. Caesar, J. Kabzan, K. S. Tan, W. K. Fong, E. Wolff, A. Lang,
L. Fletcher, O. Beijbom, and S. Omari, “nuplan: A closed-loop ml-
based planning benchmark for autonomous vehicles,” arXiv preprint
arXiv:2106.11810, 2021.
[41] A. K. Akan and F. Güney, “StretchBEV: Stretching future instance
prediction spatially and temporally,” in ECCV, 2022.
[42] S. Hu, L. Chen, P. Wu, H. Li, J. Yan, and D. Tao, “ST-P3: End-
to-end vision-based autonomous driving via spatial-temporal feature
learning,” in ECCV, 2022.
[43] Y. Zhang, Z. Zhu, W. Zheng, J. Huang, G. Huang, J. Zhou, and J. Lu,
“BEVerse: Unified perception and prediction in birds-eye-view for
vision-centric autonomous driving,” arXiv preprint arXiv:2205.09743,
2022.
[44] P. Li, S. Ding, X. Chen, N. Hanselmann, M. Cordts, and J. Gall,
“Powerbev: A powerful yet lightweight framework for instance pre-
diction in bird’s-eye view,” arXiv preprint arXiv:2306.10761, 2023.
[45] P. Hu, A. Huang, J. Dolan, D. Held, and D. Ramanan, “Safe local
motion planning with self-supervised freespace forecasting,” in CVPR,
2021.
[46] T. Khurana, P. Hu, A. Dave, J. Ziglar, D. Held, and D. Ramanan,
“Differentiable raycasting for self-supervised occupancy forecasting,”
in ECCV, 2022.