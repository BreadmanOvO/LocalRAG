# ViP3D: End-to-end Visual Trajectory Prediction via 3D Agent Queries

**Source**: arXiv:2208.01582

**Type**: Academic Paper

---

## Page 1

ViP3D: End-to-end Visual Trajectory Prediction via 3D Agent Queries
Junru Gu1∗
Chenxu Hu1∗
Tianyuan Zhang2,3
Xuanyao Chen2,4
Yilun Wang5
Yue Wang6
Hang Zhao1,2†
1IIIS, Tsinghua University
2Shanghai Qi Zhi Institute
3CMU
4Fudan University
5Li Auto
6MIT
Figure 1.
Comparison of a traditional multi-stage perception-prediction pipeline in autonomous driving and our proposed ViP3D. The
traditional pipeline involves multiple non-differentiable modules, i.e., detection, tracking, and prediction. ViP3D uses 3D agent queries as
the main thread of the pipeline, enabling end-to-end future trajectory prediction from raw video frame inputs. The novel design improves
trajectory prediction performance by effectively leveraging fine-grained visual information such as the turning signals of vehicles.
Abstract
Perception and prediction are two separate modules in
the existing autonomous driving systems. They interact with
each other via hand-picked features such as agent bounding
boxes and trajectories. Due to this separation, prediction,
as a downstream module, only receives limited information
from the perception module. To make matters worse, er-
rors from the perception modules can propagate and accu-
mulate, adversely affecting the prediction results. In this
work, we propose ViP3D, a query-based visual trajectory
prediction pipeline that exploits rich information from raw
videos to directly predict future trajectories of agents in a
scene. ViP3D employs sparse agent queries to detect, track,
∗Equal contribution.
†Corresponding to: hangzhao@mail.tsinghua.edu.cn
and predict throughout the pipeline, making it the first fully
differentiable vision-based trajectory prediction approach.
Instead of using historical feature maps and trajectories,
useful information from previous timestamps is encoded in
agent queries, which makes ViP3D a concise streaming pre-
diction method. Furthermore, extensive experimental re-
sults on the nuScenes dataset show the strong vision-based
prediction performance of ViP3D over traditional pipelines
and previous end-to-end models.1
1. Introduction
An autonomous driving system should be able to per-
ceive agents in the current environment and predict their
future behaviors so that the vehicle can navigate the world
1Code and demos are available on the project page: https://
tsinghua-mars-lab.github.io/ViP3D
1
arXiv:2208.01582v3  [cs.CV]  19 Jun 2023


## Page 2

safely. Perception and prediction are two separate modules
in the existing autonomous driving software pipeline, where
the interface between them is often defined as hand-picked
geometric and semantic features, such as historical agent
trajectories, agent types, agent sizes, etc. Such an interface
leads to the loss of useful perceptual information that can
be used in trajectory prediction. For example, tail lights and
brake lights indicate a vehicle’s intention, and pedestrians’
head pose and body pose tell about their attention. This
information, if not explicitly modeled, is ignored in the ex-
isting pipelines. In addition, with the separation of percep-
tion and prediction, errors are accumulated and cannot be
mitigated in later stages. Specifically, historical trajectories
used by trajectory predictors come from an upstream per-
ception module, which inevitably contains errors, leading
to a drop in the prediction performance. Designing a trajec-
tory predictor that is robust to upstream output errors is a
non-trivial task [61].
Recent
works
such
as
IntentNet
[3],
FaF
[35],
PnPNet [31] propose end-to-end models for LiDAR-based
trajectory prediction. They suffer from a couple of limita-
tions: (1) They are not able to leverage the abundant fine-
grained visual information from cameras; (2) these models
use convolutional feature maps as their intermediate rep-
resentations within and across frames, thus suffering from
non-differentiable operations such as non-maximum sup-
pression in object decoding and object association in multi-
object tracking.
To address all these challenges, we propose a novel
pipeline that leverages a query-centric model design to pre-
dict future trajectories, dubbed ViP3D (Visual trajectory
Prediction via 3D agent queries). ViP3D consumes multi-
view videos from surrounding cameras and high-definition
maps, and makes agent-level future trajectory prediction in
an end-to-end and concise streaming manner, as shown in
Figure 1. Specifically, ViP3D leverages 3D agent queries as
the interface throughout the pipeline, where each query can
map to (at most) an agent in the environment. At each time
step, the queries aggregate visual features from multi-view
images, learn agent temporal dynamics, model the relation-
ship between agents, and finally produce possible future tra-
jectories for each agent. Across time, the 3D agent queries
are maintained in a memory bank, which can be initialized,
updated and discarded to track agents in the environment.
Additionally, unlike previous prediction methods that uti-
lize historical agent trajectories and feature maps from mul-
tiple historical frames, ViP3D only uses 3D agent queries
from one previous timestamp and sensor features from the
current timestamp, making it a concise streaming approach.
In summary, the contribution of this paper is three-fold:
1. ViP3D is the first fully differentiable vision-based
approach to predict future trajectories of agents for au-
tonomous driving. Instead of using hand-picked fea-
tures like historical trajectories and agent sizes, ViP3D
leverages the rich and fine-grained visual features from
raw images which are useful for the trajectory predic-
tion task.
2. With 3D agent queries as interface, ViP3D explicitly
models agent-level detection, tracking and prediction,
making it interpretable and debuggable.
3. ViP3D is a concise model with high performance. It
outperforms a wide variety of baselines and recent end-
to-end methods on the visual trajectory prediction task.
2. Related Work
3D Detection.
There are a great number of works on 3D
object detection and tracking from point clouds [27,43,65].
In this paper, we focus on 3D detection and tracking from
cameras. Monodis [47] and FCOS3D [53] learn a single-
stage object detector with instance depth and 3D pose pre-
dictions on monocular images. Pseudo-LiDAR [54] first
predicts depth for each image pixel, then lifts them into the
3D space, and finally employs a point cloud based pipeline
to perform 3D detection. DETR3D [55] designs a sparse
3D query-based detection model that maps queries onto 2D
multi-view images to extract features. BEVFormer [29] and
PolarFormer [25] further propose a dense query-based de-
tection model. Lift-Splat-Shoot [41] projects image features
into BEV space by predicting depth distribution over pix-
els, BEVDet [23] performs 3D object detection on top of it.
Furthermore, PETR [33] develops an implicit approach to
transform 2D image features into BEV space for 3D detec-
tion.
3D Tracking.
The majority of 3D tracking approaches
follow the tracking-by-detection pipeline [39, 56]. These
methods first detect 3D objects, then associate existing
tracklets with the new detections. CenterTrack [58,64] uses
two consecutive frames to predict the speed of each detec-
tion box, then performs association using only ℓ2 distances
of the boxes. Samuel et al. [46] uses PMBM filter to es-
timate states of tracklets and match them with new obser-
vations. DEFT [4] uses a learned appearance matching net-
work for association, together with an LSTM estimated mo-
tion to eliminate implausible trajectories. QD3DT [22] uses
cues from depth-ordering and learns better appearance fea-
tures via contrastive learning. MUTR3D [62] introduces
track queries to model objects that appear in multiple cam-
eras across multiple frames.
Trajectory Prediction.
Several seminal trajectory predic-
tion works have studied historical trajectory and map ge-
ometry encoding using graph neural networks [13, 30] and
Transformers [37,38,52]. To make multiple plausible future
predictions [5,8,11,12,40,40], variety loss is a regression-
2


## Page 3

based method that only optimizes the closest predicted tra-
jectory during training. A Divide-And-Conquer [36] ap-
proach is also a good initialization technique to produce
diverse outputs.
Modeling uncertainty using latent vari-
ables [2, 7, 20, 28, 44, 49, 50, 57, 59] is another popular
approach, which predicts different future trajectories by
randomly sampling from the latent variables. Goal-based
methods recently achieve outstanding performance by first
predicting the intentions of agents, such as the endpoint of
trajectories [15–17,51,63], lanes to follow [26,30,48], and
then predicting trajectories conditioning on these goals.
End-to-End Perception and Prediction.
In the last cou-
ple of years, there has been growing interest in jointly
optimizing detection, tracking, and prediction.
FaF [35]
employs a single convolutional neural network to detect
objects from LiDAR point clouds, and forecast their cor-
responding future trajectories.
IntentNet [3] adds high-
level intention output to this framework.
More recently,
Phillips et al. [42] further learns localization together with
perception and prediction. FIERY [21] predicts future BEV
occupancy heatmaps from visual data directly. Mostly re-
lated to our work is PnPNet [31], which explicitly models
tracking in the loop. Our method is related to these meth-
ods in the sense that we also perform end-to-end predic-
tion based on sensor inputs. However, they all rely on BEV
feature maps or heatmaps as their intermediate representa-
tion, which leads to unavoidable non-differentiable opera-
tion while going from dense feature maps to instance-level
features, such as non-maximum suppression (NMS) in de-
tection, and association in tracking. Our method, on the
other hand, employs sparse agent queries as representation
throughout the model, greatly improving the differentiabil-
ity and interpretability.
3. Method
Overall, ViP3D leverages a query-centric model de-
sign to address the trajectory prediction problem from raw
videos in an end-to-end manner. As shown in Figure 2, 3D
agent queries serve as the main thread across time. At each
time step, a query-based detection and tracking module ex-
tracts multi-view image features from surrounding cameras
to update agent queries, forming a set of tracked agent
queries. The tracked agent queries potentially contain much
useful visual information, including the motion dynamics
and visual characteristics of the agents. After that, a query-
based prediction module takes the tracked agent queries as
input and associates them with HD map features, and finally
outputs agent-wise future trajectories. Over time, analogous
to traditional trackers, the 3D agent queries are initialized,
updated and discarded within a query memory bank, mak-
ing ViP3D work in a concise streaming fashion. The design
details of each module are explained in the following sub-
sections.
3.1. Query-based Detection and Tracking
For each input frame, a query-based detection and track-
ing first extracts visual features from surrounding cameras,
as shown in the upper part of Figure 2. Specifically, we fol-
low DETR3D [55] to extract 2D features from multi-view
images and use cross attention to update agent queries. For
temporal feature aggregation, inspired by MOTR [60], we
design a query-based tracking scheme with two key steps:
query feature update and query supervision. Agent queries
are updated across time to model the motion dynamics of
agents.
3.1.1
Query Feature Update
Each agent query corresponds to at most one agent that
appeared in the scene.
We use Q to denote a set of
agent queries, which are initialized as learnable embed-
dings with 3D reference points [55]. At each time step,
we first extract 2D image features of surrounding cameras
via ResNet50 [19] and FPN [32].
Then we project the
3D reference points of agent queries onto the 2D coordi-
nates of multi-view images using camera intrinsic and ex-
trinsic transformation matrices. Finally, we extract the cor-
responding image features L to update the agent queries
via cross attention. Let Q′
t = QtWQ, K = LWK, V =
LWV be query / key / value vectors, respectively, where
WQ, WK, WV ∈Rdh×dk are the matrices for linear pro-
jection, t ∈{1, . . . , T} is the current time step, dk is the
dimension of query / key / value vectors. Then the cross at-
tention is: ˜
Qt = softmax

Q′
tK⊤
√dk

V. Finally, we update
the agent queries: Q′
t = FFN

Qt + ˜
Qt

, where FFN is a
two-layer MLP with layer normalization.
3.1.2
Query Supervision
Since each agent query corresponds to at most one certain
agent, supervision is required at each time step to make sure
each query extracts features of the same agent across differ-
ent historical frames. There are two types of queries. One is
the matched queries that have been associated with ground
truth agents before this time step. The other is the empty
queries that have not been associated with any ground truth
agent. Suppose we have done association at time step t −1,
and now we perform association at time step t. For the
matched queries, we assign the same ground truth agents
to them as before: Qmatched ∼= At−1, where At−1 denotes
the ground truth agents at time step t −1. If an agent disap-
pears at time step t, we assign an empty label to supervise
the corresponding agent query and reinitialize it as an empty
unmatched query for later use. For the unmatched queries,
3


## Page 4

Figure 2. ViP3D model pipeline. 3D agent queries serve as the main thread and intermediate representations over time. At each time step,
the agent queries aggregate visual features from multi-view images to obtain tracked agent queries. The tracked queries further interact
with HD maps and are decoded into predicted trajectories. The agent queries are managed in a dynamic memory bank, and the model
works in a concise streaming manner.
we perform a bipartite matching between the unmatched
queries and the new appeared agents At,new at time step
t: Qempty ∼= At,new.
To perform the bipartite matching, we utilize a query
decoder that outputs the center coordinates of each query
at time step t. The pair-wise matching cost [1] between
ground truth yi and a prediction ˆyσ(i) for the bipartite
matching is: Lmatch
 yi, ˆyσ(i)

= −1{ci̸=∅}ˆpσ(i) (ci) +
1{ci̸=∅}Lbox

bi,ˆbσ(i)

, where ci is the target class label,
Lbox is the ℓ1 loss for bounding box parameters, bi is the
target box, ˆbσ(i) and ˆpσ(i) (ci) are the predicted box and
predicted probability of class ci, respectively.
After the bipartite matching, we get the optimal assign-
ment ˆσ. We compute the query classification loss Lcls and
query coordinate regression loss Lcoord as follows:
Lcls =
N
X
i=1
−log ˆpˆσ(i) (ci) ,
(1)
Lcoord =
N
X
i=1
1{ci̸=∅}Lbox

bi,ˆbˆσ(i)

,
(2)
where Lbox is the ℓ1 loss for bounding box parameters.
3.1.3
Query Memory Bank
To model long-term relationships for agent queries of differ-
ent time steps, we maintain historical states for each agent
query in a query memory bank. Following MOTR [60],
the memory query bank is a first-in-first-out queue with a
fixed size Sbank. After each time step, the attention mech-
anism is only applied between each query and its histori-
cal states in the memory bank for efficiency. For the ith
agent query qi
t at the time step t, the corresponding histor-
ical states in the memory bank are denoted as Qi
bank =
{qi
t−Sbank, . . . , qi
t−2, qi
t−1}.
Then the temporal cross at-
tention is ˜qi
t = softmax

qi
t,queryQi
bank,key
⊤
√
d

Qi
bank,value,
where qi
t,query, Qi
bank,key, Qi
bank,value are query / key /
value vectors after linear projection, respectively, and d is
the dimension of the agent queries. The ith agent query is
updated by: qi
t
′ = FFN

qi
t + ˜qi
t

, where FFN is a two-
layer MLP with layer normalization. Finally, the historical
states of the ith agent query in the memory bank become:
Qi
bank
′ = {qi
t−Sbank+1, . . . , qi
t−1, qi
t
′}.
3.2. Query-based Prediction
Typical trajectory prediction models can be divided into
three components: an agent encoder that extracts agent tra-
jectory features, a map encoder that extracts map features,
and a trajectory decoder that outputs predicted trajecto-
ries. In our pipeline, the query-based detection and tracking
gives tracked agent queries, which is equivalent to the out-
put of the agent encoder. Therefore, by taking agent queries
as input, the query-based prediction module is composed of
only a map encoder and a trajectory decoder.
4


## Page 5

3.2.1
Map Encoding
HD semantic maps are crucial for trajectory prediction since
they include detailed road information, such as lane types,
road boundaries, and traffic signs. HD maps are typically
represented by vectorized spatial coordinates of map ele-
ments and the topological relations between them. To en-
code this information, we adopt a popular vectorized en-
coding method VectorNet [13]. The map encoder produces
a set of map features M, which further interacts with agent
queries via cross attention: Q′ = Attention(Q, M).
3.2.2
Trajectory Decoding
The trajectory decoding takes the agent queries as input
and outputs K possible future trajectories for each agent.
ViP3D is compatible with a variety of trajectory decoding
methods, such as regression-based methods [9, 18, 30, 45],
goal-based methods [63] and heatmap-based methods [14,
15, 17]. We introduce the key ideas of these methods here
and leave the details in the Appendix. (1) The regression-
based method, namely variety loss (or min-of-K), predicts
future trajectories based on regression. During inference,
this decoder directly outputs a set of predicted trajectories.
During training, we first calculate the distance between each
predicted trajectory and the ground truth trajectory. Then
we select a predicted trajectory with the closest distance
and only calculate regression loss between it and the ground
truth trajectory.
(2) The goal-based method first defines
sparse goal anchors heuristically and then classifies these
anchors to estimate and select the goals. Finally, a trajec-
tory is completed for each selected goal. (3) The heatmap-
based method first generates a heatmap indicating the prob-
ability distribution of the goal. Then a greedy algorithm or
a neural network is used to select goals from the heatmap.
Finally, same as the goal-based method, the trajectories are
completed. We use Ltraj to denote the loss of trajectory
decoding and leave the detailed definition in the Appendix.
3.3. Loss
ViP3D is trained end-to-end with query classification
loss and query coordinate regression loss of the query-based
detection and tracking, and trajectory decoding loss of the
query-based prediction: L = Lcls + Lcoord + Ltraj.
4. Experiments
4.1. End-to-end Prediction Accuracy
To evaluate the performance of multi-future trajectory
prediction, we adopt the common metrics including mini-
mum average displacement error (minADE), minimum final
displacement error (minFDE), and miss rate (MR). How-
ever, the inputs of end-to-end prediction are raw pixels,
models may detect more false positive agents which should
False positive agent
Matched
Matched
Tracked agent
GT agent
Predicted trajectory
GT future trajectory
Prediction hit
Miss
Figure 3. An example of End-to-end Prediction Accuracy (EPA)
calculation. Blue and red agents are ground truth and detected
agents, respectively. After matching the ground truth and the de-
tection results, the red agent in the lower part is considered a false
positive agent. A predicted trajectory is considered a hit when its
final displacement error is below a certain threshold.
not exist (an example shown in Figure 3). In these metrics,
we find the closest predicted trajectory for each ground truth
trajectory to calculate displacement error, which does not
account for false positives. Therefore, we propose a more
comprehensive evaluation metric for end-to-end visual tra-
jectory prediction, named End-to-end Prediction Accuracy
(EPA).
Let us denote predicted and ground truth agents as un-
ordered sets ˆS and S, respectively, where each agent is
represented by K future trajectories of different modalities.
First, for each agent type c, we calculate the prediction pre-
cision between ˆSc and Sc, where the subscript c indicates
the agents of type c. We define the cost between a predicted
agent ˆs and a ground truth agent s as:
CEPA(s,ˆs) =
(
||s0 −ˆs0||,
if ||s0 −ˆs0|| ⩽τEPA
∞,
if ||s0 −ˆs0|| > τEPA
, (3)
where ˆs0 and s0 indicate the coordinates of the ground truth
agent and the predicted agent at the current time step, and
we set the threshold of successful matching to τEPA =
2.0m.
We utilize bipartite matching according to CEPA
to find the correspondence between predicted agents and
ground truth agents. Then the number of false-positive pre-
dicted agents is NFP = | ˆS| −| ˆSmatch|, where ˆSmatch ⊂ˆS
is the set of predicted agents which have been matched with
ground truth agents. For each matched agent, we calculate
minFDE (minimum final displacement error) between its
predicted multiple future trajectories and the ground truth
trajectory minFDE(ˆs, s) =
min
k∈1...K ||ˆs(k)
Tfuture −sTfuture||,
where ˆs(k) is the kth trajectory of the matched agent ˆs , and
Tfuture is the final time step of the future trajectory. Now
the set of agents which have matched and hit a ground truth
agent is ˆSmatch,hit = {ˆs : ˆs ∈ˆSmatch, minFDE(ˆs, s) ⩽
5


## Page 6

τEPA}. The EPA between ˆSc and Sc is defined as:
EPA( ˆSc, Sc) = | ˆSmatch,hit| −αNFP
NGT
,
(4)
where NGT is the number of ground truth agents, and we
set the penalty coefficient α = 0.5 for all experiments. For
different scenes, each number in the equation is defined as
the sum over all scenes. Finally, the EPA between ˆS and S
is averaged over all agent types.
4.2. Experimental Settings
Dataset.
We train and evaluate ViP3D on the nuScenes
dataset, a large-scale driving dataset including the urban
scenarios in Boston and Singapore. It contains 1000 scenes,
and each scene has a duration of around 20 seconds. The
full dataset has more than one million images from 6 cam-
eras and 1.4M bounding boxes for different types of objects.
Bounding boxes of objects are annotated at 2Hz over the en-
tire dataset.
Trajectory Prediction Settings.
Popular trajectory pre-
diction benchmarks, such as Argoverse Motion Prediction
Benchmark [6], require the prediction of one target agent
in each scene. In our visual trajectory prediction task, we
simultaneously predict all agents in each scene, which is
the same as real-time usage. A commonly used trick is to
predict trajectories in allocentric view, i.e., taking the last
position of the target agent as the origin and its direction as
y-axis. It makes prediction models focus on future modal-
ity prediction instead of coordinate transformation, thereby
improving the prediction performance. In our experiments,
we use this trick for all baselines and our ViP3D. Metrics
averaged over vehicles and pedestrians are used to compare
their performance on visual trajectory prediction task.
4.3. Baseline Settings
Traditional Perception and Prediction Pipeline.
The
traditional pipeline is composed of a vision-based detector,
a tracker, and a predictor. For a fair comparison, the vision-
based detector is the same as ViP3D. For the tracker, we
test the performance of the classical IoU association with
Kalman Filter, and an advanced tracking method named
CenterPoint [58]. Compared with ViP3D, the outputs of the
tracker are agent trajectories and agent attributes instead of
agent queries. These agent attributes are manually-defined
in common tracking tasks, and we use as many attributes
as possible, including agent types, agent sizes, agent veloc-
ities, etc.
PnPNet-vision.
PnPNet [31] only takes LiDAR data as
input, and it cannot be directly used for our visual trajectory
prediction task. Following the original PnPNet, we propose
PnPNet-vision by replacing the LiDAR encoder of the orig-
inal PnPNet with DETR3D, which is the same as the detec-
tor of ViP3D. Instead of using the query-based tracker and
predictor, PnPNet associates boxes across frames accord-
ing to affinity matrix and uses Kalman Filter as the motion
model, which is a non-differentiable operation. For pre-
diction, PnPNet crops features from the BEV feature map
according to tracked trajectories, and takes the cropped fea-
tures as the inputs of the prediction. We use Lift-Splat-Shot
to obtain the BEV feature map for PnPNet-vision.
4.4. Evaluation and Analysis
4.4.1
Main Results
We compare our ViP3D with traditional perception and pre-
diction pipeline and PnPNet-vision on the nuScenes dataset,
as shown in Table 1. The traditional perception and predic-
tion pipeline uses historical trajectories as the interface be-
tween tracking and prediction, so it cannot utilize visual in-
formation for prediction. Our proposed PnPNet-vision fol-
lows the key idea of the original PnPNet to obtain agent
features by cropping from BEV feature maps, and takes
the cropped features as the inputs of the predictor. More
implementation details are described in Section 4.3. All
baselines and our ViP3D use DETR3D as the detector and
regression-based trajectory decoding method as the predic-
tor for a fair comparison. We can see that ViP3D outper-
forms these baselines on all the metrics, indicating the ef-
fectiveness and superiority of directly learning from visual
information with a fully differentiable approach.
4.4.2
Ablation Study
Trajectory Prediction Inputs.
To better understand the
necessity of visual features and end-to-end training, we
compare ViP3D with different baselines. These baselines
have the same architecture as ViP3D except for the predic-
tion inputs. We use the default regression-based method
for trajectory decoding. Results are shown in Table 2. It
can be seen that Agent trajectories + Agent queries out-
performs Agent trajectories, demonstrating that the agent
queries provide more fine-grained and detailed visual in-
formation to improve prediction performance. ViP3D sur-
passes Agent trajectories and Agent trajectories + Agent
queries, demonstrating that fully differentiable end-to-end
learning is helpful in avoiding the error accumulation prob-
lem in the multi-stage pipeline.
Trajectory Decoding Methods.
We compare our ViP3D
with traditional perception and prediction pipeline under
other trajectory decoding methods, goal-based TNT [63]
and heatmap-based HOME [15], which recently achieve
state-of-the-art performance. As shown in Table 3, ViP3D
surpasses the traditional perception and prediction pipeline
6


## Page 7

Traditional
PnPNet-vision [31]
ViP3D (Ours)
Architechture
detector
DETR3D
DETR3D
DETR3D
detector-tracker interface
boxes
boxes
queries
tracker
Kalman Filter
CenterPoint
Kalman Filter
CenterPoint
query-based
tracker-predictor interface
trajectories
cropped features
queries
predictor
regression-based
regression-based
regression-based
Metrics
minADE↓
2.07
2.06
2.04
2.04
2.03
minFDE↓
3.10
3.02
3.08
3.03
2.90
MR↓
0.289
0.277
0.277
0.271
0.239
EPA↑
0.191
0.209
0.198
0.213
0.236
Table 1. Comparing ViP3D with traditional multi-stage pipeline. Classical metrics include minADE, minFDE and Miss Rate (MR), and
End-to-end Prediction Accuracy (EPA) which is our proposed metric for the end-to-end setting. For each agent, 6 future trajectories with
a time horizon of 6 seconds are evaluated.
Prediction inputs
Differentiable
minADE ↓
minFDE ↓
MR ↓
EPA↑
Agent trajectories
✗
2.30
3.33
0.282
0.186
Agent trajectories + Agent queries
✗
2.20
3.19
0.274
0.211
ViP3D
Agent queries
✓
2.03
2.90
0.239
0.236
Table 2. Ablation study on the inputs of the trajectory prediction module of ViP3D. Trajectory decoding defaults to a regression-based
method.
on these metrics under the two trajectory decoding methods,
demonstrating that ViP3D is compatible with various state-
of-the-art trajectory decoders and achieves superior perfor-
mance.
Decoder
Pipeline
mADE
mFDE
MR
EPA
Goal [63]
Traditional
2.50
3.93
0.266
0.195
ViP3D
2.24
3.33
0.238
0.219
Heatmap [15]
Traditional
2.53
3.81
0.264
0.197
ViP3D
2.33
3.42
0.218
0.214
Table 3.
Comparing trajectory prediction performance on the
nuScenes validation set with another two trajectory decoding
methods: goal-based and heatmap-based. mADE and mFDE de-
note minADE and minFDE, respectively.
View of Trajectory Prediction.
We test the performance
of the pipelines in two different prediction coordinates. One
is in the egocentric view, and the other is in the allocentric
view [24]. The egocentric view indicates predicting trajec-
tories in the coordinate system of the ego vehicle, while
the allocentric view indicates predicting trajectories in the
coordinate system of the predicted agent itself. Predicting
trajectories in the allocentric view is a commonly used nor-
malization trick, and it has a better performance compared
with the egocentric view. As shown in Table 4, the same
results are obtained in our experiments. So experiments of
baselines and ViP3D in other sections are performed in the
allocentric view by default.
View
Pipeline
minADE
minFDE
MR
EPA
Egocentric
Traditional
2.51
3.57
0.353
0.132
ViP3D
2.10
3.01
0.261
0.199
Allocentric
Traditional
2.06
3.02
0.277
0.209
ViP3D
2.03
2.90
0.239
0.236
Table 4. The comparison between different types of view of tra-
jectory prediction.
Analysis of Different Detectors
We also conduct ex-
periments
on
other
vision-based
detectors,
such
as
PETRv2 [34], which leverages the temporal information of
previous frames to assist 3D object detection. When using
PETRv2 as the detection backbone, ViP3D achieves a bet-
ter performance in short-term inference (< 3s) but fails in
long-term inference (> 10s). It indicates that the perfor-
mance of long-term inference is sensitive to the detection
backbone, and more efforts are needed to adapt ViP3D to
different detectors. A possible solution is to run ViP3D on
longer scene segments (currently 3 frames) during training
if the GPU memory is large enough. We regard it as a limi-
tation of ViP3D.
4.4.3
Qualitative Results
We provide examples of the predicted results by ViP3D and
traditional pipeline in Figure 4. In the upper example, we
can see that the left turn signal of the vehicle in the blue box
is flashing, indicating that the vehicle is about to turn left.
ViP3D can use this visual information to predict the correct
trajectory. In contrast, the traditional pipeline can only use
7


## Page 8

historical trajectory information to predict that the vehicle
is about to go straight incorrectly. In the lower example,
we can see that the pedestrian is facing the coming vehi-
cle, indicating that he has probably noticed the approaching
vehicle and will stop and wait for the vehicle to go first.
ViP3D makes use of the pedestrian’s head pose to correctly
predict that the pedestrian will stop, while the traditional
pipeline incorrectly predicts that pedestrians will cross the
road. These two examples show that ViP3D improves tra-
jectory prediction performance due to utilizing visual infor-
mation.
5. Conclusion
We present ViP3D, a fully differentiable approach to pre-
dict future trajectories of agents from multi-view videos.
It exploits the rich visual information from the raw sen-
sory input and avoids the error accumulation problem in
the traditional pipeline. Moreover, by leveraging 3D agent
queries, ViP3D models agent instances explicitly, making
the pipeline interpretable and debuggable.
Rear view
Front view
Rear view
Front view
Rear view
Tracked agent
GT agent
Ego vehicle
GT future trajectory
Prediction of ViP3D
Prediction of traditional 
Tracked history trajectory
GT history trajectory
Tracked agent
GT agent
Ego vehicle
GT future trajectory
Prediction of ViP3D
Prediction of traditional 
Tracked history trajectory
GT history trajectory
Tracked agent
GT agent
Ego vehicle
GT future trajectory
Prediction of ViP3D
Prediction of traditional 
Tracked history trajectory
GT history trajectory
Tracked agent
GT agent
Ego vehicle
GT future trajectory
Prediction of ViP3D
Prediction of traditional 
Tracked history trajectory
GT history trajectory
Figure 4. Qualitative results. Input camera images are shown on the top. The green vehicle is the ego agent. The blue and orange agents
indicate ground-truth and tracked agents, respectively. The blue, orange and red curves indicate ground-truth trajectories, prediction of
ViP3D and prediction of the traditional pipeline, respectively. For each agent, only the predicted trajectory with the highest probability is
drawn.
8


## Page 9

References
[1] Nicolas Carion, Francisco Massa, Gabriel Synnaeve, Nicolas
Usunier, Alexander Kirillov, and Sergey Zagoruyko. End-to-
end object detection with transformers. In ECCV, 2020. 4
[2] S. Casas, Cole Gulino, Simon Suo, Katie Luo, Renjie Liao,
and R. Urtasun.
Implicit latent variable model for scene-
consistent motion forecasting. In ECCV, 2020. 3
[3] Sergio Casas, Wenjie Luo, and Raquel Urtasun. Intentnet:
Learning to predict intention from raw sensor data. In Con-
ference on Robot Learning, pages 947–956. PMLR, 2018. 2,
3
[4] Mohamed Chaabane, Peter Zhang, J Ross Beveridge, and
Stephen O’Hara. Deft: Detection embeddings for tracking.
arXiv preprint arXiv:2102.02267, 2021. 2
[5] Yuning Chai, Benjamin Sapp, Mayank Bansal, and Dragomir
Anguelov.
Multipath: Multiple probabilistic anchor tra-
jectory hypotheses for behavior prediction. arXiv preprint
arXiv:1910.05449, 2019. 2
[6] Ming-Fang Chang, John Lambert, Patsorn Sangkloy, Jag-
jeet Singh, Slawomir Bak, Andrew Hartnett, De Wang, Peter
Carr, Simon Lucey, Deva Ramanan, et al. Argoverse: 3d
tracking and forecasting with rich maps. In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition, pages 8748–8757, 2019. 6
[7] Dooseop Choi and KyoungWook Min. Hierarchical latent
structure for multi-modal vehicle trajectory forecasting. In
Computer Vision–ECCV 2022: 17th European Conference,
Tel Aviv, Israel, October 23–27, 2022, Proceedings, Part
XXII, pages 129–145. Springer, 2022. 3
[8] Henggang Cui, Vladan Radosavljevic, Fang-Chieh Chou,
Tsung-Han Lin, Thi Nguyen, Tzu-Kuo Huang, Jeff Schnei-
der, and Nemanja Djuric. Multimodal trajectory predictions
for autonomous driving using deep convolutional networks.
In 2019 International Conference on Robotics and Automa-
tion (ICRA), pages 2090–2096. IEEE, 2019. 2
[9] Henggang Cui, Vladan Radosavljevic, Fang-Chieh Chou,
Tsung-Han Lin, Thi Nguyen, Tzu-Kuo Huang, Jeff Schnei-
der, and Nemanja Djuric. Multimodal trajectory predictions
for autonomous driving using deep convolutional networks.
In 2019 International Conference on Robotics and Automa-
tion (ICRA), pages 2090–2096. IEEE, 2019. 5, 12
[10] Kingma Da. A method for stochastic optimization. arXiv
preprint arXiv:1412.6980, 2014. 12
[11] Nachiket Deo and Mohan M Trivedi. Multi-modal trajec-
tory prediction of surrounding vehicles with maneuver based
lstms. In 2018 IEEE Intelligent Vehicles Symposium (IV),
pages 1179–1184. IEEE, 2018. 2
[12] Liangji Fang, Qinhong Jiang, Jianping Shi, and Bolei Zhou.
Tpnet: Trajectory proposal network for motion prediction.
In Proceedings of the IEEE/CVF Conference on Computer
Vision and Pattern Recognition, pages 6797–6806, 2020. 2
[13] Jiyang Gao, Chen Sun, Hang Zhao, Yi Shen, Dragomir
Anguelov, Congcong Li, and Cordelia Schmid. Vectornet:
Encoding hd maps and agent dynamics from vectorized rep-
resentation.
In Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, pages 11525–
11533, 2020. 2, 5, 12
[14] Thomas Gilles, Stefano Sabatini, Dzmitry Tsishkou, Bog-
dan Stanciulescu, and Fabien Moutarde. Gohome: Graph-
oriented heatmap output for future motion estimation. arXiv
preprint arXiv:2109.01827, 2021. 5, 12
[15] Thomas Gilles, Stefano Sabatini, Dzmitry Tsishkou, Bog-
dan Stanciulescu, and Fabien Moutarde. Home: Heatmap
output for future motion estimation.
arXiv preprint
arXiv:2105.10968, 2021. 3, 5, 6, 7, 12, 13
[16] Thomas Gilles, Stefano Sabatini, Dzmitry Tsishkou, Bog-
dan Stanciulescu, and Fabien Moutarde. Thomas: Trajectory
heatmap output with learned multi-agent sampling. In Inter-
national Conference on Learning Representations, 2021. 3
[17] Junru Gu, Chen Sun, and Hang Zhao. Densetnt: End-to-end
trajectory prediction from dense goal sets. In Proceedings
of the IEEE/CVF International Conference on Computer Vi-
sion, pages 15303–15312, 2021. 3, 5, 12
[18] Agrim Gupta, Justin Johnson, Li Fei-Fei, Silvio Savarese,
and Alexandre Alahi. Social gan: Socially acceptable tra-
jectories with generative adversarial networks. In Proceed-
ings of the IEEE Conference on Computer Vision and Pattern
Recognition, pages 2255–2264, 2018. 5, 12
[19] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun.
Deep Residual Learning for Image Recognition. In CVPR,
pages 770–778, 2016. 3, 12
[20] Joey Hong, Benjamin Sapp, and James Philbin. Rules of the
road: Predicting driving behavior with a convolutional model
of semantic interactions. In Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition,
pages 8454–8462, 2019. 3
[21] Anthony Hu, Zak Murez, Nikhil Mohan, Sof´ıa Dudas, Jef-
frey Hawke, Vijay Badrinarayanan, Roberto Cipolla, and
Alex Kendall. Fiery: Future instance prediction in bird’s-
eye view from surround monocular cameras. In Proceedings
of the IEEE/CVF International Conference on Computer Vi-
sion, pages 15273–15282, 2021. 3
[22] Hou-Ning Hu, Yung-Hsu Yang, Tobias Fischer, Trevor Dar-
rell, Fisher Yu, and Min Sun.
Monocular quasi-dense 3d
object tracking. arXiv preprint arXiv:2103.07351, 2021. 2
[23] Junjie Huang, Guan Huang, Zheng Zhu, and Dalong Du.
Bevdet: High-performance multi-camera 3d object detection
in bird-eye-view. arXiv preprint arXiv:2112.11790, 2021. 2
[24] Xiaosong Jia, Liting Sun, Hang Zhao, Masayoshi Tomizuka,
and Wei Zhan. Multi-agent trajectory prediction by combin-
ing egocentric and allocentric views. In Aleksandra Faust,
David Hsu, and Gerhard Neumann, editors, Proceedings of
the 5th Conference on Robot Learning, volume 164 of Pro-
ceedings of Machine Learning Research, pages 1434–1443.
PMLR, 08–11 Nov 2022. 7
[25] Yanqin Jiang, Li Zhang, Zhenwei Miao, Xiatian Zhu, Jin
Gao, Weiming Hu, and Yu-Gang Jiang. Polarformer: Multi-
camera 3d object detection with polar transformers. arXiv
preprint arXiv:2206.15398, 2022. 2
[26] ByeoungDo Kim, Seong Hyeon Park, Seokhwan Lee, Elbek
Khoshimjonov, Dongsuk Kum, Junsoo Kim, Jeong Soo Kim,
and Jun Won Choi. LaPred: Lane-aware prediction of multi-
modal future trajectories of dynamic agents. In Proceedings
of the IEEE/CVF Conference on Computer Vision and Pat-
tern Recognition, pages 14636–14645, 2021. 3
9


## Page 10

[27] Alex H Lang, Sourabh Vora, Holger Caesar, Lubing Zhou,
Jiong Yang, and Oscar Beijbom. PointPillars: Fast Encoders
for Object Detection from Point Clouds. In CVPR, pages
12697–12705, 2019. 2
[28] Namhoon Lee, Wongun Choi, Paul Vernaza, Christopher B
Choy, Philip HS Torr, and Manmohan Chandraker. Desire:
Distant future prediction in dynamic scenes with interacting
agents. In Proceedings of the IEEE Conference on Computer
Vision and Pattern Recognition, pages 336–345, 2017. 3
[29] Zhiqi Li, Wenhai Wang, Hongyang Li, Enze Xie, Chong-
hao Sima, Tong Lu, Qiao Yu, and Jifeng Dai. Bevformer:
Learning bird’s-eye-view representation from multi-camera
images via spatiotemporal transformers.
arXiv preprint
arXiv:2203.17270, 2022. 2
[30] Ming Liang, Bin Yang, Rui Hu, Yun Chen, Renjie Liao, Song
Feng, and Raquel Urtasun. Learning lane graph representa-
tions for motion forecasting.
In European Conference on
Computer Vision, pages 541–556. Springer, 2020. 2, 3, 5, 12
[31] Ming Liang, Bin Yang, Wenyuan Zeng, Yun Chen, Rui Hu,
Sergio Casas, and Raquel Urtasun. Pnpnet: End-to-end per-
ception and prediction with tracking in the loop. In Proceed-
ings of the IEEE/CVF Conference on Computer Vision and
Pattern Recognition, pages 11553–11562, 2020. 2, 3, 6, 7
[32] Tsung-Yi Lin, Piotr Doll´ar, Ross Girshick, Kaiming He,
Bharath Hariharan, and Serge Belongie. Feature Pyramid
Networks for Object Detection. In CVPR, pages 2117–2125,
2017. 3
[33] Yingfei Liu, Tiancai Wang, Xiangyu Zhang, and Jian Sun.
Petr: Position embedding transformation for multi-view 3d
object detection. arXiv preprint arXiv:2203.05625, 2022. 2
[34] Yingfei Liu, Junjie Yan, Fan Jia, Shuailin Li, Qi Gao, Tian-
cai Wang, Xiangyu Zhang, and Jian Sun. Petrv2: A uni-
fied framework for 3d perception from multi-camera images.
arXiv preprint arXiv:2206.01256, 2022. 7
[35] Wenjie Luo, Bin Yang, and Raquel Urtasun. Fast and furi-
ous: Real time end-to-end 3d detection, tracking and motion
forecasting with a single convolutional net. In Proceedings of
the IEEE conference on Computer Vision and Pattern Recog-
nition, pages 3569–3577, 2018. 2, 3
[36] Sriram Narayanan, Ramin Moslemi, Francesco Pittaluga,
Buyu Liu, and Manmohan Chandraker. Divide-and-conquer
for lane-aware diverse trajectory prediction. In Proceedings
of the IEEE/CVF Conference on Computer Vision and Pat-
tern Recognition, pages 15799–15808, 2021. 3
[37] Nigamaa Nayakanti, Rami Al-Rfou, Aurick Zhou, Kratarth
Goel, Khaled S Refaat, and Benjamin Sapp.
Wayformer:
Motion forecasting via simple & efficient attention networks.
arXiv preprint arXiv:2207.05844, 2022. 2
[38] Jiquan Ngiam, Benjamin Caine, Vijay Vasudevan, Zheng-
dong Zhang, Hao-Tien Lewis Chiang, Jeffrey Ling, Rebecca
Roelofs, Alex Bewley, Chenxi Liu, Ashish Venugopal, et al.
Scene transformer: A unified multi-task model for behavior
prediction and planning. arXiv preprint arXiv:2106.08417,
2021. 2
[39] Ziqi Pang, Zhichao Li, and Naiyan Wang. Simpletrack: Un-
derstanding and rethinking 3d multi-object tracking. arXiv
preprint arXiv:2111.09621, 2021. 2
[40] Tung Phan-Minh, Elena Corina Grigore, Freddy A Boulton,
Oscar Beijbom, and Eric M Wolff. Covernet: Multimodal
behavior prediction using trajectory sets. In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition, pages 14074–14083, 2020. 2
[41] Jonah Philion and Sanja Fidler. Lift, splat, shoot: Encoding
images from arbitrary camera rigs by implicitly unprojecting
to 3d. In European Conference on Computer Vision, pages
194–210. Springer, 2020. 2
[42] John Phillips, Julieta Martinez, Ioan Andrei Barsan, Sergio
Casas, Abbas Sadat, and Raquel Urtasun. Deep multi-task
learning for joint localization, perception, and prediction.
In Proceedings of the IEEE/CVF Conference on Computer
Vision and Pattern Recognition (CVPR), pages 4679–4689,
June 2021. 3
[43] Charles R Qi, Hao Su, Kaichun Mo, and Leonidas J Guibas.
PointNet: Deep Learning on Point Sets for 3D Classification
and Segmentation. In CVPR, pages 652–660, 2017. 2
[44] Nicholas Rhinehart, Kris M Kitani, and Paul Vernaza. R2p2:
A reparameterized pushforward policy for diverse, precise
generative path forecasting. In Proceedings of the European
Conference on Computer Vision (ECCV), pages 772–788,
2018. 3
[45] Christian Rupprecht, Iro Laina, Robert DiPietro, Maximil-
ian Baust, Federico Tombari, Nassir Navab, and Gregory D
Hager. Learning in an uncertain world: Representing ambi-
guity through multiple hypotheses.
In Proceedings of the
IEEE international conference on computer vision, pages
3591–3600, 2017. 5, 12
[46] Samuel Scheidegger, Joachim Benjaminsson, Emil Rosen-
berg, Amrit Krishnan, and Karl Granstr¨om. Mono-camera
3d multi-object tracking using deep learning detections and
pmbm filtering. In 2018 IEEE Intelligent Vehicles Sympo-
sium (IV), pages 433–440. IEEE, 2018. 2
[47] Andrea Simonelli, Samuel Rota Bulo, Lorenzo Porzi,
Manuel L´opez-Antequera, and Peter Kontschieder. Disen-
tangling monocular 3d object detection. In Proceedings of
the IEEE/CVF International Conference on Computer Vi-
sion, pages 1991–1999, 2019. 2
[48] Haoran Song,
Di Luan,
Wenchao Ding,
Michael Yu
Wang, and Qifeng Chen.
Learning to predict vehicle
trajectories with model-based planning.
arXiv preprint
arXiv:2103.04027, 2021. 3
[49] Chen Sun, Per Karlsson, Jiajun Wu, Joshua B Tenen-
baum, and Kevin Murphy. Stochastic prediction of multi-
agent interactions from partial observations. arXiv preprint
arXiv:1902.09641, 2019. 3
[50] Yichuan Charlie Tang and Ruslan Salakhutdinov. Multiple
futures prediction. arXiv preprint arXiv:1911.00997, 2019.
3
[51] Hung Tran, Vuong Le, and Truyen Tran. Goal-driven long-
term trajectory prediction. In Proceedings of the IEEE/CVF
Winter Conference on Applications of Computer Vision,
pages 796–805, 2021. 3
[52] Balakrishnan Varadarajan, Ahmed Hefny, Avikalp Srivas-
tava, Khaled S Refaat, Nigamaa Nayakanti, Andre Cornman,
Kan Chen, Bertrand Douillard, Chi Pang Lam, Dragomir
10


## Page 11

Anguelov, et al.
Multipath++: Efficient information fu-
sion and trajectory aggregation for behavior prediction. In
2022 International Conference on Robotics and Automation
(ICRA), pages 7814–7821. IEEE, 2022. 2
[53] Tai Wang, Xinge Zhu, Jiangmiao Pang, and Dahua Lin.
Fcos3d: Fully convolutional one-stage monocular 3d object
detection. arXiv preprint arXiv:2104.10956, 2021. 2
[54] Yan Wang, Wei-Lun Chao, Divyansh Garg, Bharath Hari-
haran, Mark Campbell, and Kilian Q Weinberger. Pseudo-
LiDAR from Visual Depth Estimation: Bridging the Gap in
3D Object Detection for Autonomous Driving. In CVPR,
pages 8445–8453, 2019. 2
[55] Yue Wang, Vitor Campagnolo Guizilini, Tianyuan Zhang,
Yilun Wang, Hang Zhao, and Justin Solomon.
Detr3d:
3d object detection from multi-view images via 3d-to-2d
queries. In 5th Annual Conference on Robot Learning, 2021.
2, 3, 12
[56] Xinshuo Weng, Jianren Wang, David Held, and Kris Kitani.
3D Multi-Object Tracking: A Baseline and New Evaluation
Metrics. IROS, 2020. 2
[57] Raymond A Yeh, Alexander G Schwing, Jonathan Huang,
and Kevin Murphy.
Diverse generation for multi-agent
sports games. In Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, pages 4610–
4619, 2019. 3
[58] Tianwei Yin, Xingyi Zhou, and Philipp Kr¨ahenb¨uhl. Center-
based 3D Object Detection and Tracking.
arXiv preprint
arXiv:2006.11275, 2020. 2, 6
[59] Ye Yuan and Kris M Kitani. Diverse trajectory forecasting
with determinantal point processes. In International Confer-
ence on Learning Representations, 2019. 3
[60] Fangao Zeng, Bin Dong, Tiancai Wang, Xiangyu Zhang, and
Yichen Wei. Motr: End-to-end multiple-object tracking with
transformer. arXiv preprint arXiv:2105.03247, 2021. 3, 4
[61] Pu Zhang, Lei Bai, Jianru Xue, Jianwu Fang, Nanning
Zheng, and Wanli Ouyang.
Trajectory forecasting from
detection with uncertainty-aware motion encoding.
arXiv
preprint arXiv:2202.01478, 2022. 2
[62] Tianyuan Zhang, Xuanyao Chen, Yue Wang, Yilun Wang,
and Hang Zhao. Mutr3d: A multi-camera tracking frame-
work via 3d-to-2d queries. In Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition,
pages 4537–4546, 2022. 2
[63] Hang Zhao, Jiyang Gao, Tian Lan, Chen Sun, Benjamin
Sapp, Balakrishnan Varadarajan, Yue Shen, Yi Shen, Yuning
Chai, Cordelia Schmid, et al. Tnt: Target-driven trajectory
prediction. arXiv preprint arXiv:2008.08294, 2020. 3, 5, 6,
7, 12
[64] Xingyi Zhou, Vladlen Koltun, and Philipp Kr¨ahenb¨uhl.
Tracking objects as points. In European Conference on Com-
puter Vision, pages 474–490. Springer, 2020. 2
[65] Yin Zhou and Oncel Tuzel. VoxelNet: End-to-End Learning
for Point Cloud Based 3D Object Detection. In CVPR, pages
4490–4499, 2018. 2
11


## Page 12

A. Implementation Details
Training and Inference Details.
In our experiments, all
models are trained on the nuScenes training set with a batch
size of 8 for 24 epochs.
The ADAM optimizer [10] is
adopted to train the whole pipeline. The learning rate has an
initial value of 2e−4 and decays to 10% at the 20th and the
23rd epochs. The hidden size of the query-based detection
and tracking module is set to 256, and that of the trajec-
tory predictor is set to 128. A pretrained detection back-
bone is used for model initialization. We evaluate all mod-
els on the nuScenes validation set. All models are tested
online by feeding raw multi-view images of each time step
to the model in chronological order. The metric computa-
tion is performed at every step except for steps that do not
have enough future frames. Different from popular trajec-
tory prediction benchmarks that only require predictions of
selected agents, we simultaneously predict all agents at each
step.
Query-based Detection and Tracking.
The query-based
detection and tracking takes ResNet50 [19] as the image
backbone and DETR3D [55] as the detection head. The de-
tection head consists of 6 layers, and each layer contains
a feature refinement layer and a multi-head attention layer
with layer normalization. The hidden size for the detection
head is set to 256. Finally, one branch predicts center co-
ordinates and size of agents, and the other branch predicts
agent type. Each branch consists of two fully connected
layers, where the hidden size is also 256.
Map Encoding.
Same as typical trajectory prediction
models, ViP3D also encodes HD maps to facilitate trajec-
tory prediction. VectorNet [13] is the first trajectory pre-
diction method to encode vectorized HD maps using a hier-
archical graph neural network, and we follow it to convert
each lane into a sequence of vectors. Each vector repre-
sents a segment of the lane, including the endpoints of the
segment, the attributes of the lane, and the numerical order
of the segment in the lane.
B. Trajectory Decoding
ViP3D can leverage a variety of trajectory decoding
methods, such as regression-based methods [9, 18, 30, 45],
goal-based methods [63] and heatmap-based methods [14,
15, 17]. We conduct experiments on these three trajectory
decoding methods. In this section, we introduce the imple-
mentation details of these methods.
Regression-based.
The regression-based trajectory de-
coder is a 2-layer MLP that takes the agent queries as in-
put and directly outputs multiple future trajectories. During
inference, the regression-based trajectory decoder directly
outputs a set of predicted trajectories. During training, we
first calculate the distance between each predicted trajectory
ˆs and ground truth trajectory s: d(s,ˆs) =
Tfuture
P
t=1
||st −ˆst||,
where || · || is the ℓ2 distance between two points. Then,
we select the predicted trajectory with the closest distance:
ˆk = argmink∈1...K d(s, s(k)), where s(k) is the kth pre-
dicted trajectory. Finally, we calculate regression loss be-
tween the closest predicted trajectory s(ˆk) and the ground
truth trajectory s as
Ltrajectory =
Tfuture
X
t=1
Lreg(st, s(ˆk)
t
),
(5)
where Lreg is the smooth ℓ1 loss between two points.
Goal-based.
The goal-based trajectory decoder consists
of a goal encoder, a probability decoder, an offset decoder,
and a trajectory completion module. These modules are im-
plemented using MLP. For each agent, we first randomly
generate a set of candidate goals. The goal encoder is used
to obtain the features of candidate goals by taking their co-
ordinates as input. After that, a concatenation of the agent
query and the features of goal coordinates is fed into the
probability decoder and offset decoder. The probability de-
coder and the offset decoder output predicted goal proba-
bilities and goal offsets, respectively. Let Lcls be the bi-
nary cross-entropy loss for the probability decoder, and let
Lreg be the smooth ℓ1 loss for the offset decoder. To obtain
K trajectories, Non-maximum supervision (NMS) is em-
ployed to select K goals (after adding the goal offsets), and
the trajectory completion module takes the K selected goals
and outputs K trajectories. Let Lcompletion be the smooth ℓ1
loss for the trajectory completion module. Then the overall
loss is
Ltrajectory = Lcls + Lreg + Lcompletion.
(6)
Heatmap-based.
The heatmap-based trajectory decoder
only consists of a goal encoder, a probability decoder, and
a trajectory completion module. These modules are imple-
mented using MLP. For each agent, to obtain a heatmap in-
dicating the probability distribution of the final positions of
the trajectories, we first densely sample goals with a sam-
pling density of 1m. The goal encoder is used to obtain
the features of the goals by taking their coordinates as in-
put. After that, a concatenation of the agent query and the
features of goal coordinates is fed into the probability de-
coder. The probability decoder outputs predicted goal prob-
abilities, and we obtain the heatmap. Let Lcls be the bi-
nary cross-entropy loss for the probability decoder. To ob-
tain K trajectories, we also use NMS to select K goals for
12


## Page 13

simplification, instead of using greedy algorithms as in ori-
gin heatmap-based methods [15]. The trajectory completion
module takes the K selected goals and outputs K trajecto-
ries. Let Lcompletion be the smooth ℓ1 loss for the trajectory
completion module. Then the overall loss is
Ltrajectory = Lcls + Lcompletion.
(7)
C. Qualitative Results
The visualizations of predicted results of both ViP3D and
the traditional pipeline are included in the paper. In this
section, we provide more visualizations for ViP3D, includ-
ing some failure cases. As the cases shown in Figure 5,
ViP3D can predict accurate future trajectories. As the fail-
ure cases shown in Figure 6, because ViP3D is a vision-
based pipeline, it is difficult for ViP3D to detect agents far
away from the ego vehicle or agents partially obscured. In
the upper part of Figure 6, a vehicle (surrounded by a red
box) that is far away from the ego vehicle and is partially
obscured by other vehicles, so it is difficult to be detected.
In the lower part of Figure 6, a pedestrian (surrounded by
a red box) is mostly obscured by a billboard, so ViP3D can
not detect this pedestrian.
13


## Page 14

Front view
Rear view
Front view
Rear view
Tracked agent
GT agent
Ego vehicle
GT future trajectory
Prediction of ViP3D
Tracked history trajectory
GT history trajectory
Tracked agent
GT agent
Ego vehicle
GT future trajectory
Prediction of ViP3D
Tracked history trajectory
GT history trajectory
Tracked agent
GT agent
Ego vehicle
GT future trajectory
Prediction of ViP3D
Tracked history trajectory
GT history trajectory
Tracked agent
GT agent
Ego vehicle
GT future trajectory
Prediction of ViP3D
Tracked history trajectory
GT history trajectory
Figure 5. Qualitative results of ViP3D on the nuScenes validation set. Input camera images are shown on the top. The green vehicle is
the ego agent. The blue and orange agents indicate ground-truth and tracked agents, respectively. The blue and orange curves indicate
ground-truth trajectories and predicted trajectories of ViP3D, respectively. For each agent, only the predicted trajectory with the highest
probability is drawn.
14


## Page 15

Front view
Rear view
Front view
Rear view
Tracked agent
GT agent
Ego vehicle
GT future trajectory
Prediction of ViP3D
Tracked history trajectory
GT history trajectory
Tracked agent
GT agent
Ego vehicle
GT future trajectory
Prediction of ViP3D
Tracked history trajectory
GT history trajectory
Tracked agent
GT agent
Ego vehicle
GT future trajectory
Prediction of ViP3D
Tracked history trajectory
GT history trajectory
Tracked agent
GT agent
Ego vehicle
GT future trajectory
Prediction of ViP3D
Tracked history trajectory
GT history trajectory
Figure 6. Failure cases of ViP3D on the nuScenes validation set. Input camera images are shown on the top. The green vehicle is the ego
agent. The blue and orange agents indicate ground-truth and tracked agents, respectively. The blue and orange curves indicate ground-truth
trajectories and predicted trajectories of ViP3D, respectively. For each agent, only the predicted trajectory with the highest probability is
drawn. The agent surrounded by a red box indicates that it is not detected by ViP3D.
15

