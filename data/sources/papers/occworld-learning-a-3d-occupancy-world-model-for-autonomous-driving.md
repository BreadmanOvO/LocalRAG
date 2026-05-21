# OccWorld: Learning a 3D Occupancy World Model for Autonomous Driving

**Source**: arXiv:2311.16038

**Type**: Academic Paper

---

## Page 1

OccWorld: Learning a 3D Occupancy World Model for Autonomous Driving
Wenzhao Zheng1,* Weiliang Chen2,*
Yuanhui Huang1
Borui Zhang1
Yueqi Duan2
Jiwen Lu1
Department of Automation, Tsinghua University, China
Department of Electronic Engineering, Tsinghua University, China
wenzhao.zheng@outlook.com; {chen-wl20,huangyh22,zhang-br21}@mails.tsinghua.edu.cn;
{duanyueqi,lujiwen}@tsinghua.edu.cn
GT
OccWorld
t = 0.5s
t = 1s
t = 1.5s
t = 2s
t = 2.5s
t = 3s
3D Occupancy 
World Model 
Observations
(+0.02m, +3.90m)
(+0.01m, +1.66m)
(+0.03m, +3.87m)(+0.04m, +3.75m)(+0.04m, +3.65m)(+0.04m, +3.71m)
(+0.03m, +3.90m)(+0.03m, +3.81m)(+0.03m, +3.81m)(+0.03m, +3.89m)(+0.03m, +3.86m)(+0.03m, +3.91m)
bicycle
car
pedestrian
truck
driveable surface
sidewalk
terrain
manmade
vegetation
More reasonable
Figure 1.
Given past 3D occupancy observations, our self-supervised OccWorld trained can forecast future scene evolutions and ego
movements jointly. This task requires a spatial understanding of the 3D scene and temporal modeling of how driving scenarios develop.
We observe that OccWorld can successfully forecast the movements of surrounding agents and future map elements such as drivable areas.
OccWorld even generates more reasonable drivable areas than the ground truth, demonstrating its ability to understand the scene rather
than memorizing training data. Still, it fails to forecast new vehicles entering the sight, which is difficult given their absence in the inputs.
Abstract
Understanding how the 3D scene evolves is vital for
making decisions in autonomous driving.
Most existing
methods achieve this by predicting the movements of ob-
ject boxes, which cannot capture more fine-grained scene
information. In this paper, we explore a new framework
of learning a world model, OccWorld, in the 3D Occupancy
space to simultaneously predict the movement of the ego car
and the evolution of the surrounding scenes. We propose to
learn a world model based on 3D occupancy rather than 3D
bounding boxes and segmentation maps for three reasons:
1) expressiveness. 3D occupancy can describe the more
fine-grained 3D structure of the scene; 2) efficiency. 3D
occupancy is more economical to obtain (e.g., from sparse
LiDAR points). 3) versatility. 3D occupancy can adapt to
both vision and LiDAR. To facilitate the modeling of the
world evolution, we learn a reconstruction-based scene to-
kenizer on the 3D occupancy to obtain discrete scene to-
kens to describe the surrounding scenes. We then adopt a
GPT-like spatial-temporal generative transformer to gen-
erate subsequent scene and ego tokens to decode the future
occupancy and ego trajectory. Extensive experiments on the
widely used nuScenes benchmark demonstrate the ability of
*Equal contribution.
OccWorld to effectively model the evolution of the driving
scenes. OccWorld also produces competitive planning re-
sults without using instance and map supervision. Code:
https://github.com/wzzheng/OccWorld.
1. Introduction
Autonomous driving has been widely explored in recent
years and demonstrated promising results in various scenar-
ios [21, 57, 65, 68]. While LiDAR-based models typically
show strong performance and robustness in 3D perception
due to its capture of structural information [7, 35, 51, 61,
62], the more hardware-economical vision-centric solutions
have dramatically caught up with the increased perception
ability of deep networks [19, 32, 33, 42, 44].
Forecasting future scene evolutions is important to the
safety of autonomous driving vehicles. Most existing meth-
ods follow a conventional pipeline of perception, predic-
tion, and planning [17, 18, 25].
Perception aims to ob-
tain a semantic understanding of the surrounding scene
such as 3D object detection [19, 32, 33] and semantic
map construction [30, 34, 37, 66].
The subsequent pre-
diction module captures the motion of other traffic partic-
ipants [11, 14, 24, 66], and the planning module then makes
decisions based on previous outputs [17, 18, 25, 45]. How-
1
arXiv:2311.16038v1  [cs.CV]  27 Nov 2023


## Page 2

ever, this serial design usually requires ground-truth labels
at each stage of training, yet the instance-level bounding
boxes and high-definition maps are difficult to annotate.
Furthermore, they usually only predict the motion of ob-
ject bounding boxes, failing to capture more fine-grained
information about the 3D scene.
In this paper, we explore a new paradigm to simultane-
ously predict the evolution of the surrounding scene and
plan the future trajectory of the self-driving vehicle. We
propose OccWorld, a world model in the 3D semantic oc-
cupancy space, to model the development of the driving
scenes.
We adopt 3D semantic occupancy as the scene
representation over the conventional 3D bounding boxes
and segmentation maps, which can describe the more fine-
grained 3D structure of the scene. Moreover, 3D occupancy
can be effectively learned from sparse LiDAR points [21],
and thus is a potentially more economical way to describe
the surrounding scenes. Given the 3D semantic occupancy
representation of the current scene, OccWorld aims to pre-
dict how it evolves as the self-driving vehicle advances. To
achieve this, we first employ a vector-quantized variational
autoencoder (VQVAE) [41] to refine high-level concepts
and obtain discrete scene tokens in a self-supervised man-
ner. We then tailor the generative pre-training transform-
ers (GPT) [2] architecture and propose a spatial-temporal
generative transformer to predict the subsequent scene to-
kens and ego tokens to forecast the future occupancy and
ego trajectory, respectively. We first perform spatial mixing
to aggregate scene tokens and obtain multi-scale tokens to
represent scenes at multiple levels. We then apply temporal
attention to tokens at different levels to predict tokens for
the next frame and use a U-net structure to integrate them.
Finally, we use the trained VQVAE decoder to transform
scene tokens to the occupancy space and learn a trajectory
decoder to obtain ego planning results.
To demonstrate the effectiveness of OccWorld, we for-
mulate a challenging task of 4D occupancy forecasting,
which aims to predict the 3D occupancy of the following
frames given a few past frames. Our OccWorld can effec-
tively forecast future evolutions including moving agents
and static elements as shown in Figure 1, and achieves an
average IoU of 26.63 and mIoU of 17.13 for 3s future given
2s history, OccWorld can also produce planning trajectories
with an L2 error of 1.16 without using any instance and map
annotations. Using self-supervised learned 3D occupancy
from camera inputs [20], our method achieves non-trivial
4D occupancy forecasting and planning results, demonstrat-
ing the potential for interpretable end-to-end autonomous
driving without additional human-annotated labels.
2. Related Work
3D Occupancy Prediction: 3D occupancy prediction aims
to predict whether each voxel in the 3D space is occupied
and its semantic label if occupied [21, 52, 53, 56, 57, 69].
Early methods exploited LiDAR as inputs to complete the
3D occupancy of the entire 3D scene [6, 29, 46, 59]. Re-
cent methods began to explore the more challenging vision-
based 3D occupancy prediction [4, 21] or applying vision
backbones to efficiently perform LiDAR-based 3D occu-
pancy prediction [69]. 3D occupancy provides more com-
prehensive descriptions of the surrounding scene and in-
cludes both dynamic and static elements [21, 57, 69]. It can
also be efficiently learned from sparse accumulated multi-
ple LiDAR scans [57], LiDAR [21], or video sequences [5].
However, existing methods only focus on obtaining the
3D semantic occupancy and ignore its temporal evolution,
which is vital to the safety of autonomous driving. In this
paper, we explore the task of 4D occupancy forecasting and
propose a 3D occupancy world model to achieve this.
World Models for Autonomous Driving: World mod-
els have a long history in control engineering and artifi-
cial intelligence [49], which are usually defined as pro-
ducing the next scene observation given action and past
observations [12].
The development of deep neural net-
works [13, 48, 50] promoted the use of deep generative
models [10, 28] as world models.
Based on large pre-
trained image generative models like StableDiffusion [47],
recent methods [9, 15, 31, 55, 60] can generate realistic
driving sequences of diverse scenarios. However, they pro-
duce future observations in the 2D image space, lacking un-
derstanding of the 3D surrounding scene. Some other meth-
ods explore forecasting point clouds using unannotated Li-
DAR scans [26, 27, 40, 58], which ignore the semantic in-
formation and cannot be applied to vision-based or fusion-
based autonomous driving. Considering this, we explore a
world model in the 3D occupancy space to more compre-
hensively model the 3D scene evolution.
End-to-End Autonomous Driving: The ultimate goal
of autonomous driving is to obtain controlling signals based
on observations of the surrounding scenes. Recent meth-
ods follow this concept to output planning results for the
ego car given sensor inputs [17, 18, 25, 53, 63].
Most
of them follow a conventional pipeline of perception [21,
32, 33, 57, 65], prediction [11, 14, 36, 66], and plan-
ning [22, 23, 54, 67].
They usually first perform BEV
perception to extract relevant information (e.g., 3D agent
boxes, semantic maps, tracklets) and then exploit them to
infer future trajectories of agents and the ego vehicle. The
following methods incorporated more data [63] or extracted
more intermediate features [17, 18, 25] to provide more in-
formation for the planner, which achieved remarkable per-
formance. Most methods only model object motions and
cannot capture the fine-grained structural and semantic in-
formation of the surroundings [11, 14, 24, 25, 66]. Differ-
ently, we propose a world model to predict the evolution of
both the surrounding dynamic and static elements.
2


## Page 3

Spatial Aggregation
Temporal Causal Self-Attention
Spatial Aggregation
Spatial Aggregation
Spatial Aggregation
Encoder
Ego Token
Encoder
Ego Token
Spatial Aggregation
Encoder
Ego Token
Decoder
Decoder
(∆x, ∆y)
Decoder
Decoder
(∆x, ∆y)
Spatial Aggregation
Decoder
Decoder
(∆x, ∆y)
Input: 
Predicted: 
t = 0
Input: 
wx+7RTE+RQ=">AB6nicbVDLSgNBEOyNrxhfUY9eBoPgKeyKr4sQ9OIxonlAsoTZyWwyZHZ2mekV
wpJP8OJBEa9+kTf/xkmyB40WNBRV3XR3BYkUBl3yksLa+srhXSxubW9s75d29polTzXiDxTLW7
YAaLoXiDRQoeTvRnEaB5K1gdDP1W49cGxGrBxwn3I/oQIlQMIpWuscr1euFV3BvKXeDmpQI56r/
zZ7csjbhCJqkxHc9N0M+oRsEkn5S6qeEJZSM64B1LFY248bPZqRNyZJU+CWNtSyGZqT8nMhoZM4
4C2xlRHJpFbyr+53VSDC/9TKgkRa7YfFGYSoIxmf5N+kJzhnJsCWVa2FsJG1JNGdp0SjYEb/Hlv6R
5UvXOq2d3p5XadR5HEQ7gEI7BgwuowS3UoQEMBvAEL/DqSOfZeXPe560FJ5/Zh19wPr4B1R+NhA=
</latexit>t = 1
t = 1
Predicted: 
Y9eBoPgKewGXxch6MVjRPOAZAmzk0kyZHZ2mekVwpJP8OJBEa9+kTf/xkmyB0saCiqunuCmIpDLrut5NbWV1b38hvFra2d3b3ivsHDRMlmvE6i2SkWwE1XArF6yhQ8lasOQ0DyZvB6HbqN5+4NiJSjzi
OuR/SgRJ9wSha6QGvK91iyS27M5Bl4mWkBlq3eJXpxexJOQKmaTGtD03Rj+lGgWTfFLoJIbHlI3ogLctVTkxk9np07IiV6pB9pWwrJTP09kdLQmHEY2M6Q4tAselPxP6+dYP/KT4WKE+SKzRf1E0kwI
tO/SU9ozlCOLaFMC3srYUOqKUObTsG4C2+vEwalbJ3UT6/PytVb7I48nAEx3AKHlxCFe6gBnVgMIBneIU3RzovzrvzMW/NOdnMIfyB8/kD1qONhQ=</latexit>t = 2
t = T −1
Input: 
t = T
Predicted: 
Figure 2. Framework of our OccWorld for 3D semantic occupancy forecast and motion planning. We adopt a GPT-like generative
architecture to predict the next scene from previous scenes in an autoregressive manner. We adapt GPT [2] to the autonomous driving
scenario with two key designs: 1) We train a 3D occupancy scene tokenizer to produce discrete high-level representations of the 3D scene;
2) We perform spatial mixing before and after spatial-wise temporal causal self-attention to efficiently produce globally consistent scene
predictions. We use ground-truth and predicted scene tokens as inputs for future generations for training and inference, respectively.
3. Proposed Approach
3.1. World Model for Autonomous Driving
Autonomous driving aims to automatically steer a vehi-
cle to fully prevent or partially reduce actions from human
drivers [18]. Formally, the objective of autonomous driving
is to obtain the control commands cT (e.g., throttle, steer,
break) for the present time stamp T given the sensor inputs
{sT , sT −1, · · · , sT −t} from the current and past t frames.
As the mapping from trajectories to control signals is
highly dependent on the vehicle specifications and status,
the literature usually assumes a given satisfactory controller
and thus focuses on trajectory planning for the ego vehi-
cle. An autonomous driving model A then takes input as
the sensor inputs and ego trajectory from the past T frames
and predicts the ego trajectory of future f frames:
A({sT , sT −1, · · · , sT −t}, {pT , pT −1, · · · , pT −t})
={pT +1, pT +2, · · · , pT +f},
(1)
where pt denotes the 3D ego position at the t-th time.
The conventional pipeline of autonomous driving usu-
ally follows a design of perception, prediction, and plan-
ning [17, 18, 25]. The perception module per perceives
the surrounding scenes and extracts high-level information
z from the input sensor data s. The prediction module pre
then integrates the high-level information z to predict the
future trajectory ti of each agent in the scene. The planning
module pla finally processes the perception and prediction
results {z, {ti}} to plan the motion of the ego vehicle. The
conventional pipeline can be formulated as:
pla(per({sT , · · · , sT −t}), pre(per({sT , · · · , T −t})))
={pT +1, pT +2, · · · , pT +f}.
(2)
Despite the promising performance of this frame-
work [17, 18, 25], it usually requires ground-truth labels
for supervision at each stage, which can be laborious to an-
notate. It only considers object-level movement and fails to
model more fine-grained evolutions.
Motivated by this, we explore a new world-model-based
autonomous driving paradigm to comprehensively model
the evolution of the surrounding scenes and the ego move-
ments. Inspired by the recent success of generative pre-
training transformers (GPT) [2] in natural language process-
ing (NLP), we propose an auto-regressive generative mod-
eling framework for autonomous driving scenarios. We de-
fine a world model w to act on scene representations y and
be able to predict future scenes. Formally, we formulate the
function of a world model w as follows:
w({yT , · · · , yT −t}, {pT , · · · , pT −t}) = yT +1, pT +1.
(3)
Having obtained the predicted scene yT +1 and the ego
position pT +1, we can add them to the input and further pre-
dict the next frame in an auto-regressive manner, as shown
in Figure 2. The world model w captures the joint distribu-
tion of the evolution of the surrounding scene and the ego
vehicle, considering their high-order interactions.
3


## Page 4

Vector
Quantized
Encoder
Encoder
Decoder
Learnable 
Codebook
3D Occupancy 
Scene Tokenzier 
Figure 3. Illustration of the proposed 3D occupancy scene to-
kenizer.
We use CNNs to encode the 3D occupancy and per-
form vector quantization to obtain discrete tokens using a learnable
codebook [41]. We then employ a decoder to reconstruct the input
3D occupancy using the quantized tokens and use a reconstruction
objective to train the autoencoder and codebook simultaneously.
3.2. 3D Occupancy Scene Tokenizer
As the world model w operates on the scene representation
y, its choice is vital to the performance of the world model.
We select y based on three principles: 1) expressiveness. It
should be able to comprehensively contain the 3D structural
and semantic information of the 3D scene; 2) efficiency.
It should be economical to learn (e.g., from weak supervi-
sion or self-supervision); 3) versatility. It should be able to
adapt to both vision and LiDAR modalities.
Considering all the aforementioned principles, we pro-
pose to adopt 3D occupancy as the 3D scene representa-
tion y ∈RH×W ×D. 3D occupancy partitions the 3D space
surrounding the ego car into H × W × D voxels and as-
signs each voxel with a label l denoting whether it is occu-
pied and which material it is occupied with. 3D occupancy
provides a dense representation of the 3D scene and can
describe both the 3D structural and semantic information
of the scene. It can be effectively learned from sparse Li-
DAR annotations [21] or potentially from self-supervision
of temporal frames [20]. 3D occupancy is also modality-
agnostic and can be obtained from monocular camera [4],
surrounding cameras [21, 53, 57], or LiDAR [69].
Despite its comprehensiveness, 3D occupancy only pro-
vides a low-level understanding of the scene, making it dif-
ficult to directly model its evolution. We therefore propose
a self-supervised way to tokenize the scene into high-level
tokens from 3D occupancy. We train a vector-quantized au-
toencoder (VQ-VAE) [41] on y to obtain discrete tokens z
to better represent the scene, as shown in Figure 3.
For efficiency, we first transform the 3D occupancy y ∈
RH×W ×D to a BEV representation ˆy ∈RH×W ×DC′ by
assigning each category with a learnable class embedding
∈RC′ and concatenating them in the height dimension. We
then adopt a lightweight encoder composed of 2D convolu-
tion layers to obtain down-sampled features ˆz ∈R
H
d × W
d ×C
of the scene, where d is the down-sampling factor.
To obtain a more compact representation, we simultane-
ously learn a codebook C ∈RN×D containing N codes.
Each code c ∈RC in the codebook encodes a high-level
concept of the scene, e.g., whether the corresponding posi-
tion is occupied by a car. We quantized each spatial feature
ˆzij in ˆz by classifying it to the nearest code N(ˆzij, C):
zij = N(ˆzij, C) = min
c∈C ||ˆzij −c||2,
(4)
where || · ||2 denotes the L2 norm. We then integrate the
quantized features {zij} to obtain the final scene represen-
tation z ∈RH×W ×C.
To reconstruct ey from the learned scene representa-
tion z, we use a decoder of 2D deconvolution layers to
progressively upsample z to its original BEV resolution
H ×W ×C′′. We then perform a split in the channel dimen-
sion to reconstruct the height dimension H × W × D × C′′
D
and apply a softmax layer on each spatial feature to classify
them into occupied semantics or unoccupied H × W × D.
The scene tokenizer transforms 3D occupancy into a
more compact discrete space to encode higher-level con-
cepts. This refined compact space facilitates the modeling
of scene evolution for the subsequent world model.
3.3. Spatial-Temporal Generative Transformer
The core of autonomous driving lies in the prediction of
how the surrounding world evolves and planning the move-
ment of the ego vehicle accordingly. While conventional
methods usually perform the two tasks separately [17, 18],
we propose to learn a world model w to jointly model the
distributions of scene evolution and ego trajectory.
As defined in (3), a world model w takes as inputs the
past scenes and ego positions and predicts their outcome af-
ter driving a certain time interval. Based on expressiveness,
efficiency, and versatility, we adopt 3D occupancy y as the
scene representation and use a self-supervised tokenizer to
obtain high-level scene tokens T = {zi}. To integrate the
ego movement, we further aggregate T with an ego token
z0 ∈RC to encode the spatial position of the ego vehicle.
The proposed OccWorld w then functions on the world
tokens T, which can be formulated as:
w(TT , · · · , TT −t) = TT +1,
(5)
where T is the current time stamp, and t is the number of
history frames available.
Inspired by the remarkable sequential prediction perfor-
mance of GPT [2], we adopt a GPT-like autoregressive
transformer architecture to instantiate (5).
However, the
migration of GPT from natural language processing to the
autonomous driving scenario is not trivial. GPTs predict
a single token each time, while the world model w in au-
tonomous driving is required to predict a set of tokens T as
4


## Page 5

Spatial Aggregation
Spatial Aggregation
Spatial-wise
Temporal Causal 
Self-Attention
Spatial-wise
Temporal Causal 
Self-Attention
Spatial Aggregation
Spatial Aggregation
Spatial-wise
Temporal Causal 
Self-Attention
World Tokens at time t
World Tokens at time t + 1
Figure 4. Illustration of the proposed spatial-temporal genera-
tive transformer. As each scene is composed of numerous world
tokens, we adopt spatial mixing modules to model their intrin-
sic dependencies and obtain multi-scale world tokens to capture
multi-level information. We then perform spatial-wise temporal
causal self-attention at each level to forecast the next scene. We
employ a U-net structure to aggregate the multi-scale predictions.
the next future. Due to the vast number of world tokens, di-
rectly leveraging the GPT architecture to predict each token
∈TT +1 is both inefficient and ineffective.
Both the spatial relations of world tokens within each
time stamp and the temporal relations of tokens across dif-
ferent time stamps should be considered to comprehen-
sively model the world evolution. Therefore, we propose
a spatial-temporal generative transformer architecture to ef-
fectively process past world tokens and make predictions of
the next future, as shown in Figure 4.
We apply spatial aggregation (e.g., self-attention [8]) to
world tokens T to enable interactions between scene tokens
as well as ego tokens. We then merge the scene tokens in
each 2 × 2 window with a stride of 2 and thus down-sample
the scene tokens by a factor of 4. We repeat this procedure
for K times to obtain world tokens of hierarchical scales
{T0, · · · , TK} to describe the 3D scene at different levels.
We use several sub-world models w = {w0, · · · , wK}
to predict the future at different spatial scales. For each
sub-world model wi, we impose temporal attention on the
tokens {zT
j,i, · · · , zT −t
j,i } at each position j to obtain the pre-
dicted corresponding token zT +1
j,i
of the next frame:
ˆzT +1
j,i
= TA(zT
j,i, · · · , zT −t
j,i ),
(6)
where TA denotes masked temporal attention which blocks
the effect of future tokens to previous tokens. zt
j,i ∈Tt
i rep-
resents the j-th world token of the i-th scale at time stamp t.
We finally employ a U-net structure to aggregate predicted
tokens at different scales to ensure spatial consistency.
Our spatial-temporal generative transformer can model
the world evolution in driving sequences considering the
joint distributions of world tokens within each time and
across time. The temporal attention predicts the evolution
of a fixed position in the surrounding area, while the spatial
aggregation makes each token aware of the global scene.
3.4. OccWorld: a 3D Occupancy World Model
We present the overall training framework of our OccWorld
model for autonomous driving. Having obtained the fore-
casted world tokens, we reuse the scene decoder d to de-
code the predicted 3D occupancy ˆyT +1 = d(ˆzT +1) and
additionally learn an ego decoder dego to produce the ego
displacement ˆpT +1 = dego(ˆzT +1
0
) w.r.t the current frame.
We adopt a two-stage training strategy to effectively train
our OccWorld. For the first stage, we train the scene tok-
enizer e and decoder d using 3D occupancy loss [21]:
Je,d = Lsoft(d(e(y)), y) + λ1 Llovasz(d(e(y)), y), (7)
where Lsoft and Llovasz is the softmax and lovasz-softmax
loss [1], respectively, and λ1 is a balance factor.
For the second stage, we adopt the learned scene tok-
enizer e to obtain scene tokens z for all the frames and
constrain the discrepancy between predicted tokens ˆz and
z. We then apply the softmax loss to enforce the correct
classification of ˆz to the correct codes in the codebook C
as z. For the ego token, we simultaneously learn the ego
decoder dego and apply L2 loss on the predicted displace-
ment ˆp = dego(ˆz0) and the ground-truth one p. The overall
objective for the second stage can be formulated as follows:
Jw,dego =
T
X
t=1
(
M0
X
j=1
Lsoft(ˆzt
j,0, C(zt
j,0)
+ λ2 LL2(dego(ˆzt
0), pt)),
(8)
where T and M0 are the numbers of frames and spatial to-
kens of the original scale, respectively. C(·) denotes the
index of the corresponding code in the codebook C. LL2
measures the L2 discrepancy between two trajectories.
For efficient training, we use tokens obtained by the
scene tokenizer e as inputs but apply masked temporal at-
tention [2] to block the effect of future tokens. During in-
ference, we progressively predict world tokens of the next
frame using predicted tokens of past frames.
Our OccWorld can be applied to various types of 3D oc-
cupancy to adapt to different settings (e.g., end-to-end au-
tonomous driving). The scene representation model r can
be an oracle providing ground-truth occupancy, or a per-
ception model taking images or LiDAR as inputs. Differ-
ent from the conventional perception, predicting, and plan-
ning pipeline, OccWorld models the joint evolution of the
surrounding scene and the ego movement to capture high-
order interactions between the ego vehicle and the envi-
ronment. Combined with machine-annotated [57], LiDAR-
collected [21], or self-supervised [20] 3D occupancy, Occ-
World has the potential to scale up to large-scale training,
paving the way for large driving models.
5


## Page 6

Table 1. 4D occupancy forecasting performance. Aux. Sup. denotes auxiliary supervision apart from the ego trajectory. Avg. denotes
the average performance of that in 1s, 2s, and 3s. We use bold numbers to denote the best results.
Method
Input
Aux. Sup.
mIoU (%) ↑
IoU (%) ↑
0s
1s
2s
3s
Avg.
0s
1s
2s
3s
Avg.
FPS
Copy&Paste
3D-Occ
None
66.38 14.91 10.54
8.52
11.33 62.29 24.47 19.77 17.31 20.52
-
OccWorld-O 3D-Occ
None
66.38 25.78 15.14 10.51 17.14 62.29 34.63 25.07 20.18 26.63 18.0
OccWorld-D
Camera
3D-Occ
18.63 11.55
8.10
6.22
8.62
22.88 18.90 16.26 14.43 16.53
2.8
OccWorld-T
Camera Semantic LiDAR
7.21
4.68
3.36
2.63
3.56
10.66
9.32
8.23
7.47
8.34
2.8
OccWorld-S
Camera
None
0.27
0.28
0.26
0.24
0.26
4.32
5.05
5.01
4.95
5.00
2.8
GT
OccWorld-O
4="R0TBbuET5FInICnKyJZ1fFfrMBg=">AB
7XicbVBNSwMxEJ2tX7V+VT16CRbB07IrVr0IR
S8eK9gPaJeSTbNtbDZkqxQlv4HLx4U8er/8ea
/MW3oK0PBh7vzTAzL0w408bzvp3Cyura+kZx
s7S1vbO7V94/aGqZKkIbRHKp2iHWlDNBG4YZT
tuJojgOW2Fo9up3qiSjMpHsw4oUGMB4JFjG
Bjpa59tyq7pUrnuvNgJaJn5MK5Kj3yl/dviR
pTIUhHGvd8b3EBlWhFOJ6VuqmCyQgPaMdS
gWOqg2x27QSdWKWPIqlsCYNm6u+JDMdaj+PQd
sbYDPWiNxX/8zqpia6CjIkNVSQ+aIo5chINH0
d9ZmixPCxJZgoZm9FZIgVJsYGVLIh+IsvL5Pm
metfuNX780rtJo+jCEdwDKfgwyXU4A7q0ACj
/AMr/DmSOfFeXc+5q0FJ585hD9wPn8AigOdw
=</latexit>t = 0.5s
Da+4oveGhik=">AB63icbVDLSsNAFL2pr1pfUZduBovgqiTiayMU3bisYB/QhjKZTtqhM5Mw
MxFK6C+4caGIW3/InX/jNM1CWw9cOJxzL/feEyacaeN5305pZXVtfaO8Wdna3tndc/cPWjpOFa
FNEvNYdUKsKWeSNg0znHYSRbEIOW2H47uZ36iSrNYPpJQgOBh5JFjGCTSze+7rtVr+blQMvEL
0gVCjT67ldvEJNUGkIx1p3fS8xQYaVYTaWXapgMsZD2rVUYkF1kOW3TtGJVQYoipUtaVC
u/p7IsNB6IkLbKbAZ6UVvJv7ndVMTXQcZk0lqCTzRVHKkYnR7HE0YIoSwyeWYKYvRWREVaYG
BtPxYbgL768TFpnNf+ydvFwXq3fFnGU4QiO4R8uI63EMDmkBgBM/wCm+OcF6cd+dj3lpyiplD
+APn8wepRI4B</latexit>t = 1s
2Tb/IZxKilI=">AB7XicbVBNSwMxEJ2tX7V+VT16CRbB07IrVr0IRS8eK9gPaJeSTbNtbDZ
kqxQlv4HLx4U8er/8ea/MW3oK0PBh7vzTAzL0w408bzvp3Cyura+kZxs7S1vbO7V94/aGqZKk
IbRHKp2iHWlDNBG4YZTtuJojgOW2Fo9up3qiSjMpHsw4oUGMB4JFjGBjpa59t2q7pUrnuvNg
JaJn5MK5Kj3yl/dviRpTIUhHGvd8b3EBlWhFOJ6VuqmCyQgPaMdSgWOqg2x27QSdWKWPIql
sCYNm6u+JDMdaj+PQdsbYDPWiNxX/8zqpia6CjIkNVSQ+aIo5chINH0d9ZmixPCxJZgoZm9FZ
IgVJsYGVLIh+IsvL5PmetfuNX780rtJo+jCEdwDKfgwyXU4A7q0ACj/AMr/DmSOfFeXc+5q0F
J585hD9wPn8Ai4qOeA=</latexit>t = 1.5s
+VT16CRbBU9ktVr0IRS8eK9gPaJeSTbNtaJdkqxQlv4FLx4U8eof8ua/Md3uQVsfDzem2FmXhBzpo3rfjuFtfWNza3idmlnd2/oHx41NZRoghtkYhHqhtgTmTtGWY4bQbK4pFwGknmNzN/c4
TVZpF8tFMY+oLPJIsZASbTLqp6UG54lbdDGiVeDmpQI7moPzVH0YkEVQawrHWPc+NjZ9iZRjhdFbqJ5rGmEzwiPYslVhQ7afZrTN0ZpUhCiNlSxqUqb8nUiy0norAdgpsxnrZm4v/eb3EhNd+ymSc
GCrJYlGYcGQiNH8cDZmixPCpJZgoZm9FZIwVJsbGU7IheMsvr5J2repdVusPF5XGbR5HEU7gFM7BgytowD0oQUExvAMr/DmCOfFeXc+Fq0FJ585hj9wPn8AqsmOAg=</latexit>t = 2s
/qh69BIvgadktVr0IRS8eK9gPaJeSTbNtbDZklmhLP0PXjwo4tX/481/Y9ruQasPBh7vzTAzL0wEN+B5X05hZXVtfaO4Wdra3tndK+8ftIxKNWVNqoTSnZAYJrhkTeAgWCfRjMShYO1wfDPz249
MG67kPUwSFsRkKHnEKQErteCq6tZMv1zxXG8O/Jf4OamgHI1+bM3UDSNmQqiDFd30sgyIgGTgWblnqpYQmhYzJkXUsliZkJsvm1U3xilQGOlLYlAc/VnxMZiY2ZxKHtjAmMzLI3E/zuilEl0HG
ZICk3SxKEoFBoVnr+MB14yCmFhCqOb2VkxHRBMKNqCSDcFfvkvaVd/9yt3Z1V6td5HEV0hI7RKfLRBaqjW9RATUTRA3pCL+jVUc6z8+a8L1oLTj5ziH7B+fgGjRGOeQ=</latexit>t = 2.5s
fUY9eBoPgKexqfFyEoBePEcwDkiXMTmaTITOzy8ysEJb8ghcPinj1h7z5N042e9DEgoaiqpvuriDmTBvX/XYK6tr6xvFzdLW9s7uXn/oKWjRBHaJBGPVCfAmnImadMw2knVhSLgN2ML6b+e0
nqjSL5KOZxNQXeChZyAg2mXRzrvlilt1M6Bl4uWkAjka/fJXbxCRFBpCMdadz03Nn6KlWGE02mpl2gaYzLGQ9q1VGJBtZ9mt07RiVUGKIyULWlQpv6eSLHQeiIC2ymwGelFbyb+53UTE17KZNx
Yqgk80VhwpGJ0OxNGCKEsMnlmCimL0VkRFWmBgbT8mG4C2+vExaZ1XvsnrxUKvUb/M4inAEx3AKHlxBHe6hAU0gMIJneIU3RzgvzrvzMW8tOPnMIfyB8/kDrE6OAw=</latexit>t = 3s
OccWorld-D
OccWorld-T
(+0.02m, +2.39m)(+0.01m, +2.57m)(+0.00m, +2.87m)(+0.02m, +2.97m)(+0.03m, +3.20m)(+0.04m, +3.74m)
(+0.03m, +2.18m)(+0.04m, +2.32m)(−0.01m, +2.54m)(+0.03m, +2.56m)(+0.01m, +2.61m)(+0.06m, +3.02m)
(+0.01m, +1.84m)(+0.01m, +1.76m)(+0.01m, +1.52m)(−0.02m, +1.03m)(+0.01m, +0.20m)(+0.00m, +0.00m)
(−0.01m, +2.04m)(+0.02m, +2.03m)(+0.02m, +2.03m)(+0.01m, +1.96m)(+0.01m, +1.91m)(+0.01m, +1.66m)
Figure 5. Visualizations of the forecasting and planning results of OccWorld-O, OccWorld-D, and OccWorld-T.
4. Experiments
4.1. Task Descriptions
In this paper, we explore a world-model-based framework
for autonomous driving and propose OccWorld to model the
joint evolutions of ego trajectory and scene evolutions. We
conduct two tasks to evaluate our OccWorld: 4D occupancy
forecasting on the Occ3D dataset [52] and motion planning
on the nuScenes dataset [3]. We present the dataset and
evaluation metric details in the supplementary material.
4D occupancy forecasting. 3D occupancy prediction
aims to reconstruct the semantic occupancy for each voxel
in the surrounding space, which cannot capture the temporal
evolution of the 3D occupancy. In this paper, we explore the
task of 4D occupancy forecasting, which aims to forecast
the future 3D occupancy given a few historical occupancy
inputs. We use mIoU and IoU as the evaluation metric.
Motion planning. The objective of motion planning is
to produce safe future trajectories for the self-driving vehi-
cle given ground-truth surrounding information or percep-
tion results. The planned trajectory is represented by a se-
ries of 2D waypoints in the BEV plane (ground plane). We
use L2 error and collision rate as the evaluation metric.
4.2. Implementation Details
We followed existing works [18, 25] and used a 2-second
historical context to forecast the subsequent 3 seconds.
The scene tokenizer employs a down-sampling factor of
4, featuring a codebook comprising 512 nodes and a 128-
dimensional feature representation.
The spatial-temporal
generative transformer comprises 3 scales, each incorporat-
ing 6 layers of spatial-wise temporal attention for scene to-
kens with 2 layers of spatial cross-attention and temporal
cross-attention for ego planning tokens.
6


## Page 7

Table 2. Motion planning performance. Aux. Sup. denotes auxiliary supervision apart from the ego trajectory. We use bold and
underlined numbers to denote the best and second-best results, respectively. † denotes using the metric computation adopted in VAD [25].
Method
Input
Aux. Sup.
L2 (m) ↓
Collision Rate (%) ↓
1s
2s
3s
Avg.
1s
2s
3s
Avg.
FPS
IL [43]
LiDAR
None
0.44 1.15 2.47
1.35
0.08 0.27 1.95
0.77
-
NMP [64]
LiDAR
Box & Motion
0.53 1.25 2.67
1.48
0.04 0.12 0.87
0.34
-
FF [16]
LiDAR
Freespace
0.55 1.20 2.54
1.43
0.06 0.17 1.07
0.43
-
EO [26]
LiDAR
Freespace
0.67 1.36 2.78
1.60
0.04 0.09 0.88
0.33
-
ST-P3 [17]
Camera
Map & Box & Depth
1.33 2.11 2.90
2.11
0.23 0.62 1.27
0.71
1.6
UniAD [18]
Camera
Map & Box & Motion & Tracklets & Occ
0.48 0.96 1.65
1.03
0.05 0.17 0.71
0.31
1.8
VAD-Tiny [25]
Camera
Map & Box & Motion
0.60 1.23 2.06
1.30
0.31 0.53 1.33
0.72
16.8
VAD-Base [25]
Camera
Map & Box & Motion
0.54 1.15 1.98
1.22
0.04 0.39 1.17
0.53
4.5
OccNet [53]
Camera
3D-Occ & Map & Box
1.29 2.13 2.99
2.14
0.21 0.59 1.37
0.72
2.6
OccNet [53]
3D-Occ
Map & Box
1.29 2.31 2.98
2.25
0.20 0.56 1.30
0.69
-
OccWorld-O
3D-Occ
None
0.43 1.08 1.99
1.17
0.07 0.38 1.35
0.60
18.0
OccWorld-D
Camera
3D-Occ
0.52 1.27 2.41
1.40
0.12 0.40 2.08
0.87
2.8
OccWorld-T
Camera
Semantic LiDAR
0.54 1.36 2.66
1.52
0.12 0.40 1.59
0.70
2.8
OccWorld-S
Camera
None
0.67 1.69 3.13
1.83
0.19 1.28 4.59
2.02
2.8
VAD-Tiny† [25]
Camera
Map & Box & Motion
0.46 0.76 1.12
0.78
0.21 0.35 0.58
0.38
16.8
VAD-Base† [25]
Camera
Map & Box & Motion
0.41 0.70 1.05
0.72
0.07 0.17 0.41
0.22
4.5
OccWorld-O†
3D-Occ
None
0.32 0.61 0.98
0.64
0.06 0.21 0.47
0.24
18.0
OccWorld-D†
Camera
3D-Occ
0.39 0.73 1.18
0.77
0.11 0.19 0.67
0.32
2.8
OccWorld-T†
Camera
Semantic LiDAR
0.40 0.77 1.28
0.82
0.12 0.22 0.56
0.30
2.8
OccWorld-S†
Camera
None
0.49 0.95 1.55
0.99
0.19 0.56 1.54
0.76
2.8
During training, we applied mask operations to all tem-
poral attention mechanisms to prevent the influence of fu-
ture information on forecasting. For inference, we employ
autoregressive prediction to foresee 3 seconds into the fu-
ture based on a 2-second historical context. We adopted
the AdamW optimizer [39] and a Cosine Annealing sched-
uler [38] for training. We set an initial learning rate of 1 ×
10−3 and the weight decay at 0.01 and. We use a batch size
of 1 per GPU on 8 NVIDIA GeForce RTX 4090 GPUs.
4.3. Results and Analysis
4D occupancy forecasting.
We evaluated the 4D occu-
pancy forecasting performance of our OccWorld in several
settings: OccWorld-O (using ground-truth 3D occupancy),
OccWorld-D (using predicted results of TPVFormer [21]
trained with dense ground-truth 3D occupancy), OccWorld-
T (using predicted results of TPVFormer [21] trained
with sparse semantic LiDAR1), and OccWorld-S (using
predicted results of TPVFormer [20] trained in a self-
supervised manner2). Copy&Paste denotes copying the cur-
rent ground-truth occupancy as future observations. The 0s
results represent the reconstruction accuracy.
We compare the performance of the aforementioned set-
tings in Table 1. We observe that OccWorld-O can generate
1https://github.com/wzzheng/TPVFormer
2https://github.com/huang-yh/SelfOcc
non-trivial future 3D occupancy with much better results
than Copy&Paste, showing that our model learns the un-
derlying scene evolution. OccWorld-D, OccWorld-T, and
OccWorld-S can be seen as end-to-end vision-based 4D oc-
cupancy forecasting methods as they take surrounding im-
ages as input. This task is very challenging since it requires
both 3D structure reconstruction and forecasting. It is espe-
cially difficult for the self-supervised OccWorld-S, which
exploits no 3D occupancy information even during train-
ing. Still, our OccWorld generates future 3D occupancy
with non-trivial mIoU and IoU on the end-to-end setting.
Visualizations. We visualize the output results of the
proposed OccWorld in Figure 5. We see that our models
can successfully forecast the movements of cars and can
complete unseen map elements in the inputs such as driv-
able areas. The planning trajectory is also more accurate
with better 4D occupancy forecasting.
Motion planning. We compare the motion planning per-
formance of the proposed OccWorld with state-of-the-art
end-to-end autonomous driving methods, as shown in Ta-
ble 2. We also evaluate our model under different settings
as those in the 4D occupancy forecasting task.
We see that UniAD achieves the best overall perfor-
mance, which exploits various types of auxiliary supervi-
sion to improve its planning quality. Despite the strong per-
formance, the additional annotations in the 3D space are
7


## Page 8

Table 3. Effect of different hyperparameters for the scene tokenizer. We use bold numbers to denote the best results.
Setting
Reconstruction
Forecasting mIoU (%) ↑
Planning L2 (m) ↓
mIoU ↑
IoU ↑
1s
2s
3s
Avg.
1s
2s
3s
Avg.
FPS
(502, 128, 512)
66.38
62.29
25.78
15.14
10.51
17.14
0.43
1.08
1.99
1.17
18.0
(502, 128, 256)
63.40
60.33
24.25
14.34
10.13
16.24
0.42
1.08
1.95
1.15
17.8
(502, 128, 1024)
60.50
59.07
23.55
14.66
10.68
16.30
0.47
1.18
2.19
1.28
17.8
(252, 256, 512)
36.28
44.02
12.10
8.13
6.20
8.81
3.27
6.54
9.78
6.53
28.1
(1002, 128, 512)
78.12
71.63
18.71
10.75
7.68
12.38
0.50
1.25
2.33
1.36
6.7
(502, 64, 512)
64.98
61.50
21.83
12.90
9.28
14.67
0.49
1.24
2.26
1.33
20.1
Table 4.
Ablation study of the spatial-temporal generative
transformer. We report average results over the 1s, 2s, and 3s.
Method
Forecast
Planning
mIoU↑
IoU↑
L2↓
Col.↓
FPS
OccWorld-O
17.14
26.63
1.17
0.60
18.0
w/o spatial attn
10.07
21.44
1.42
1.21
28.6
w/o temporal attn
8.98
20.10
2.06
2.56
26.5
w/o ego
15.13
24.66
-
-
18.8
w/o ego temporal
12.07
23.09
5.89
6.23
18.5
very difficult to obtain, making it difficult to scale to large-
scale driving data. As an alternative, OccWorld demon-
strates competitive performance by employing 3D occu-
pancy as the scene representation which can be efficiently
obtained by accumulating LiDAR scans [57].
We observe that using ground-truth 3D occupancy as in-
puts, our OccWorld-O outperforms the previous perception-
prediction-planning-based method OccNet [53] by a large
margin without using maps and bounding boxes as super-
vision, demonstrating the superiority of the world-model
paradigm for autonomous driving. Our end-to-end models
OccWorld-D and OccWorld-T also demonstrate competi-
tive performance using only 3D occupancy as supervision
and OccWorld-S delivers non-trivial results with no super-
vision other than the future trajectory, showing the potential
for interpretable end-to-end autonomous driving.
Though our model demonstrates very competitive L2 er-
ror, it slightly falls behind on the collision rate. This is be-
cause it is more difficult to learn safe trajectories without the
guidance of freespace or bounding box. Still, OccWorld-O
demonstrates comparable collision rates with OccNet which
exploits map and box supervision, showing that OccWorld
can learn the concept of freespace with 3D occupancy.
We also observe that OccWorld shows excellent short-
term planning performance (1s), but worsens quickly
when planning longer futures. For example, OccWorld-O
achieves the best L2 error at 1s among all the methods but
reaches 1.99 at 3s compared to 1.65 of UniAD. This might
result from the diverse future generations of world models,
which might deviate from the ground-truth trajectory.
Analysis of the scene tokenizer. We analyze the effect
of different hyperparameters for the scene tokenizer in Ta-
ble 3. The setting denotes latent spatial resolution, latent
channel dimension, and the codebook size. We see that us-
ing a larger codebook than 512 leads to overfitting and using
a smaller codebook, spatial resolution, or channel dimen-
sion might not be enough to capture the scene distribution.
The reconstruction accuracy greatly improves with a larger
spatial resolution, yet leads to poor forecasting and plan-
ning performance. This is because the tokens cannot learn
high-level concepts and are difficult to forecast the future.
Analysis of the spatial-temporal generative trans-
former. We conducted an ablation study on both 4D oc-
cupancy forecasting and motion planning to analyze the
design of the proposed spatial-temporal generative trans-
former, as shown in Table 4. w/o spatial attn denotes dis-
carding spatial aggregation and directly applying temporal
attention to the input tokens. w/o temporal attn represents
that we replace the temporal attention with a simple con-
volution to output the next scene using the current world
tokens. w/o ego represents that we discard the ego token.
w/o ego temporal represents that we replace the temporal
attention of the ego token with a simple MLP. We observe
that using spatial aggregation to model spatial dependencies
and using temporal attention to integrate history informa-
tion is vital to the performance of both 4D occupancy fore-
casting and motion planning tasks. Also, only performing
the 4D occupancy forecasting task without predicting mo-
tion reduces the performance. This verifies the effectiveness
of joint modeling of scene evolutions and ego trajectories.
Finally, discarding the ego temporal attention leads to poor
planning and surprisingly worse 3D forecast occupancy per-
formance. We think this is because integrating a wrongly
predicted ego trajectory will mislead the forecasting.
5. Conclusion
In this paper, we have presented a 3D occupancy world
model (OccWorld) to model the joint evolutions of ego
movements and surrounding scenes.
We have employed
a 3D occupancy scene tokenizer to extract high-level con-
cepts and used a spatial-temporal generative transformer for
future prediction in an auto-regressive manner. Both quan-
titive and visualization results have shown that OccWorld
can effectively predict future scene evolutions in the com-
prehensive 3D semantic occupancy space. We believe that
OccWorld has paved the way for interpretable end-to-end
autonomous driving without additional supervision signals.
8


## Page 9

References
[1] Maxim Berman, Amal Rannen Triki, and Matthew B
Blaschko. The lov´asz-softmax loss: A tractable surrogate
for the optimization of the intersection-over-union measure
in neural networks. In CVPR, pages 4413–4421, 2018. 5
[2] Tom Brown, Benjamin Mann, Nick Ryder, Melanie Sub-
biah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakan-
tan, Pranav Shyam, Girish Sastry, Amanda Askell, et al.
Language models are few-shot learners. NeurIPS, 33:1877–
1901, 2020. 2, 3, 4, 5
[3] Holger Caesar, Varun Bankiti, Alex H Lang, Sourabh Vora,
Venice Erin Liong, Qiang Xu, Anush Krishnan, Yu Pan, Gi-
ancarlo Baldan, and Oscar Beijbom.
nuscenes: A multi-
modal dataset for autonomous driving. In CVPR, 2020. 6
[4] Anh-Quan Cao and Raoul de Charette. Monoscene: Monoc-
ular 3d semantic scene completion. In CVPR, pages 3991–
4001, 2022. 2, 4
[5] Anh-Quan Cao and Raoul de Charette.
Scenerf:
Self-
supervised monocular 3d scene reconstruction with radiance
fields. In ICCV, pages 9387–9398, 2023. 2
[6] Xiaokang Chen, Kwan-Yee Lin, Chen Qian, Gang Zeng, and
Hongsheng Li. 3d sketch-aware semantic scene completion
via semi-supervised structure prior. In CVPR, pages 4193–
4202, 2020. 2
[7] Ran Cheng, Ryan Razani, Ehsan Taghavi, Enxu Li, and
Bingbing Liu. 2-s3net: Attentive feature fusion with adap-
tive feature selection for sparse semantic segmentation net-
work. In CVPR, pages 12547–12556, 2021. 1
[8] Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov,
Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner,
Mostafa Dehghani, Matthias Minderer, Georg Heigold, Syl-
vain Gelly, et al. An image is worth 16x16 words: Trans-
formers for image recognition at scale. In ICLR, 2020. 5
[9] Ruiyuan Gao, Kai Chen, Enze Xie, Lanqing Hong, Zhenguo
Li, Dit-Yan Yeung, and Qiang Xu. Magicdrive: Street view
generation with diverse 3d geometry control. arXiv preprint
arXiv:2310.02601, 2023. 2
[10] Ian Goodfellow, Jean Pouget-Abadie, Mehdi Mirza, Bing
Xu, David Warde-Farley, Sherjil Ozair, Aaron Courville, and
Yoshua Bengio. Generative adversarial nets. NeurIPS, 27,
2014. 2
[11] Junru Gu, Chenxu Hu, Tianyuan Zhang, Xuanyao Chen,
Yilun Wang, Yue Wang, and Hang Zhao. Vip3d: End-to-
end visual trajectory prediction via 3d agent queries. arXiv
preprint arXiv:2208.01582, 2022. 1, 2
[12] David Ha and J¨urgen Schmidhuber. World models. arXiv
preprint arXiv:1803.10122, 2018. 2
[13] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun.
Deep residual learning for image recognition.
In CVPR,
pages 770–778, 2016. 2
[14] Anthony Hu, Zak Murez, Nikhil Mohan, Sof´ıa Dudas, Jef-
frey Hawke, Vijay Badrinarayanan, Roberto Cipolla, and
Alex Kendall. Fiery: Future instance prediction in bird’s-
eye view from surround monocular cameras. In ICCV, 2021.
1, 2
[15] Anthony Hu, Lloyd Russell, Hudson Yeo, Zak Murez,
George Fedoseev, Alex Kendall, Jamie Shotton, and Gian-
luca Corrado.
Gaia-1: A generative world model for au-
tonomous driving. arXiv preprint arXiv:2309.17080, 2023.
2
[16] Peiyun Hu, Aaron Huang, John Dolan, David Held, and
Deva Ramanan.
Safe local motion planning with self-
supervised freespace forecasting. In CVPR, 2021. 7
[17] Shengchao Hu, Li Chen, Penghao Wu, Hongyang Li, Junchi
Yan, and Dacheng Tao. St-p3: End-to-end vision-based au-
tonomous driving via spatial-temporal feature learning. In
ECCV, 2022. 1, 2, 3, 4, 7
[18] Yihan Hu, Jiazhi Yang, Li Chen, Keyu Li, Chonghao Sima,
Xizhou Zhu, Siqi Chai, Senyao Du, Tianwei Lin, Wenhai
Wang, et al.
Planning-oriented autonomous driving.
In
CVPR, pages 17853–17862, 2023. 1, 2, 3, 4, 6, 7
[19] Junjie Huang, Guan Huang, Zheng Zhu, and Dalong Du.
Bevdet: High-performance multi-camera 3d object detection
in bird-eye-view. arXiv preprint arXiv:2112.11790, 2021. 1
[20] Yuanhui Huang, Wenzhao Zheng, Borui Zhang, Jie Zhou,
and Jiwen Lu. Selfocc: Self-supervised vision-based 3d oc-
cupancy prediction. arXiv preprint arXiv:2311.12754, 2023.
2, 4, 5, 7
[21] Yuanhui Huang, Wenzhao Zheng, Yunpeng Zhang, Jie Zhou,
and Jiwen Lu. Tri-perspective view for vision-based 3d se-
mantic occupancy prediction. In CVPR, pages 9223–9232,
2023. 1, 2, 4, 5, 7
[22] Zhiyu Huang, Haochen Liu, and Chen Lv.
Gameformer:
Game-theoretic modeling and learning of transformer-based
interactive prediction and planning for autonomous driving.
arXiv preprint arXiv:2303.05760, 2023. 2
[23] Zhiyu Huang, Haochen Liu, Jingda Wu, and Chen Lv. Dif-
ferentiable integrated motion prediction and planning with
learnable cost function for autonomous driving. IEEE trans-
actions on neural networks and learning systems, 2023. 2
[24] Bo Jiang, Shaoyu Chen, Xinggang Wang, Bencheng Liao,
Tianheng Cheng, Jiajie Chen, Helong Zhou, Qian Zhang,
Wenyu Liu, and Chang Huang. Perceive, interact, predict:
Learning dynamic and static clues for end-to-end motion pre-
diction. arXiv preprint arXiv:2212.02181, 2022. 1, 2
[25] Bo Jiang, Shaoyu Chen, Qing Xu, Bencheng Liao, Jia-
jie Chen, Helong Zhou, Qian Zhang, Wenyu Liu, Chang
Huang, and Xinggang Wang. Vad: Vectorized scene rep-
resentation for efficient autonomous driving. arXiv preprint
arXiv:2303.12077, 2023. 1, 2, 3, 6, 7
[26] Tarasha Khurana, Peiyun Hu, Achal Dave, Jason Ziglar,
David Held, and Deva Ramanan. Differentiable raycasting
for self-supervised occupancy forecasting. In ECCV, 2022.
2, 7
[27] Tarasha Khurana, Peiyun Hu, David Held, and Deva Ra-
manan. Point cloud forecasting as a proxy for 4d occupancy
forecasting. In CVPR, pages 1116–1124, 2023. 2
[28] Diederik P Kingma and Max Welling. Auto-encoding varia-
tional bayes. arXiv preprint arXiv:1312.6114, 2013. 2
[29] Jie Li, Kai Han, Peng Wang, Yu Liu, and Xia Yuan.
Anisotropic convolutional networks for 3d semantic scene
completion. In CVPR, pages 3351–3359, 2020. 2
[30] Qi Li, Yue Wang, Yilun Wang, and Hang Zhao. Hdmapnet:
An online hd map construction and evaluation framework. In
ICRA, 2022. 1
9


## Page 10

[31] Xiaofan Li, Yifu Zhang, and Xiaoqing Ye.
Drivingdif-
fusion:
Layout-guided multi-view driving scene video
generation with latent diffusion model.
arXiv preprint
arXiv:2310.07771, 2023. 2
[32] Yinhao Li, Zheng Ge, Guanyi Yu, Jinrong Yang, Zengran
Wang, Yukang Shi, Jianjian Sun, and Zeming Li. Bevdepth:
Acquisition of reliable depth for multi-view 3d object detec-
tion. arXiv preprint arXiv:2206.10092, 2022. 1, 2
[33] Zhiqi Li, Wenhai Wang, Hongyang Li, Enze Xie, Chong-
hao Sima, Tong Lu, Qiao Yu, and Jifeng Dai. Bevformer:
Learning bird’s-eye-view representation from multi-camera
images via spatiotemporal transformers. In ECCV, 2022. 1,
2
[34] Bencheng Liao, Shaoyu Chen, Xinggang Wang, Tianheng
Cheng, Qian Zhang, Wenyu Liu, and Chang Huang. Maptr:
Structured modeling and learning for online vectorized hd
map construction. arXiv preprint arXiv:2208.14437, 2022.
1
[35] Venice Erin Liong, Thi Ngoc Tho Nguyen, Sergi Wid-
jaja, Dhananjai Sharma, and Zhuang Jie Chong. Amvnet:
Assertion-based multi-view fusion network for lidar seman-
tic segmentation. arXiv preprint arXiv:2012.04934, 2020.
1
[36] Yicheng Liu, Jinghuai Zhang, Liangji Fang, Qinhong Jiang,
and Bolei Zhou. Multimodal motion prediction with stacked
transformers. In CVPR, 2021. 2
[37] Yicheng Liu, Yue Wang, Yilun Wang, and Hang Zhao. Vec-
tormapnet: End-to-end vectorized hd map learning. arXiv
preprint arXiv:2206.08920, 2022. 1
[38] Ilya Loshchilov and Frank Hutter.
Sgdr:
Stochas-
tic gradient descent with warm restarts.
arXiv preprint
arXiv:1608.03983, 2016. 7
[39] Ilya Loshchilov and Frank Hutter. Decoupled weight decay
regularization. arXiv preprint arXiv:1711.05101, 2017. 7
[40] Benedikt Mersch, Xieyuanli Chen, Jens Behley, and Cyrill
Stachniss. Self-supervised point cloud prediction using 3d
spatio-temporal convolutional networks.
In CoRL, pages
1444–1454. PMLR, 2022. 2
[41] Aaron
van
den
Oord,
Oriol
Vinyals,
and
Koray
Kavukcuoglu.
Neural discrete representation learning.
arXiv preprint arXiv:1711.00937, 2017. 2, 4
[42] Jonah Philion and Sanja Fidler. Lift, splat, shoot: Encoding
images from arbitrary camera rigs by implicitly unprojecting
to 3d. In ECCV, pages 194–210, 2020. 1
[43] Nathan D Ratliff, J Andrew Bagnell, and Martin A Zinke-
vich.
Maximum margin planning.
In Proceedings of the
23rd international conference on Machine learning, pages
729–736, 2006. 7
[44] Cody Reading, Ali Harakeh, Julia Chae, and Steven L
Waslander.
Categorical depth distribution network for
monocular 3d object detection. In CVPR, 2021. 1
[45] Katrin Renz, Kashyap Chitta, Otniel-Bogdan Mercea, A
Koepke, Zeynep Akata, and Andreas Geiger. Plant: Explain-
able planning transformers via object-level representations.
arXiv preprint arXiv:2210.14222, 2022. 1
[46] Luis Roldao, Raoul de Charette, and Anne Verroust-Blondet.
Lmscnet: Lightweight multiscale 3d semantic completion.
In 2020 International Conference on 3D Vision (3DV), pages
111–119, 2020. 2
[47] Robin Rombach, Andreas Blattmann, Dominik Lorenz,
Patrick Esser, and Bj¨orn Ommer. High-resolution image syn-
thesis with latent diffusion models. In CVPR, pages 10684–
10695, 2022. 2
[48] Karen Simonyan and Andrew Zisserman. Very deep convo-
lutional networks for large-scale image recognition. arXiv,
abs/1409.1556, 2014. 2
[49] Richard S Sutton. Dyna, an integrated architecture for learn-
ing, planning, and reacting. ACM Sigart Bulletin, 2(4):160–
163, 1991. 2
[50] Christian Szegedy, Wei Liu, Yangqing Jia, Pierre Sermanet,
Scott E Reed, Dragomir Anguelov, Dumitru Erhan, Vincent
Vanhoucke, and Andrew Rabinovich.
Going deeper with
convolutions. In CVPR, pages 1–9, 2015. 2
[51] Haotian Tang, Zhijian Liu, Shengyu Zhao, Yujun Lin, Ji Lin,
Hanrui Wang, and Song Han. Searching efficient 3d architec-
tures with sparse point-voxel convolution. In ECCV, pages
685–702, 2020. 1
[52] Xiaoyu Tian, Tao Jiang, Longfei Yun, Yue Wang, Yilun
Wang, and Hang Zhao.
Occ3d: A large-scale 3d occu-
pancy prediction benchmark for autonomous driving. arXiv
preprint arXiv:2304.14365, 2023. 2, 6
[53] Wenwen Tong, Chonghao Sima, Tai Wang, Li Chen, Silei
Wu, Hanming Deng, Yi Gu, Lewei Lu, Ping Luo, Dahua Lin,
et al. Scene as occupancy. In ICCV, pages 8406–8415, 2023.
2, 4, 7, 8
[54] Matt Vitelli, Yan Chang, Yawei Ye, Ana Ferreira, Maciej
Wołczyk, Bła˙zej Osi´nski, Moritz Niendorf, Hugo Grimmett,
Qiangui Huang, Ashesh Jain, et al. Safetynet: Safe planning
for real-world self-driving vehicles using machine-learned
policies. In 2022 International Conference on Robotics and
Automation (ICRA), pages 897–904, 2022. 2
[55] Xiaofeng Wang, Zheng Zhu, Guan Huang, Xinze Chen,
and Jiwen Lu.
Drivedreamer: Towards real-world-driven
world models for autonomous driving.
arXiv preprint
arXiv:2309.09777, 2023. 2
[56] Xiaofeng Wang, Zheng Zhu, Wenbo Xu, Yunpeng Zhang,
Yi Wei, Xu Chi, Yun Ye, Dalong Du, Jiwen Lu, and Xin-
gang Wang. Openoccupancy: A large scale benchmark for
surrounding semantic occupancy perception. arXiv preprint
arXiv:2303.03991, 2023. 2
[57] Yi Wei, Linqing Zhao, Wenzhao Zheng, Zheng Zhu, Jie
Zhou, and Jiwen Lu. Surroundocc: Multi-camera 3d occu-
pancy prediction for autonomous driving. In ICCV, pages
21729–21740, 2023. 1, 2, 4, 5, 8
[58] Xinshuo Weng, Jianren Wang, Sergey Levine, Kris Kitani,
and Nicholas Rhinehart.
Inverting the pose forecasting
pipeline with spf2: Sequential pointcloud forecasting for se-
quential pose forecasting. In Conference on robot learning,
pages 11–20, 2021. 2
[59] Xu Yan, Jiantao Gao, Jie Li, Ruimao Zhang, Zhen Li, Rui
Huang, and Shuguang Cui. Sparse single sweep lidar point
cloud segmentation via learning contextual shape priors from
scene completion. In AAAI, pages 3101–3109, 2021. 2
10


## Page 11

[60] Kairui Yang, Enhui Ma, Jibin Peng, Qing Guo, Di Lin, and
Kaicheng Yu.
Bevcontrol: Accurately controlling street-
view elements with multi-perspective consistency via bev
sketch layout. arXiv preprint arXiv:2308.01661, 2023. 2
[61] Dongqiangzi Ye, Zixiang Zhou, Weijia Chen, Yufei Xie, Yu
Wang, Panqu Wang, and Hassan Foroosh.
Lidarmultinet:
Towards a unified multi-task network for lidar perception.
arXiv preprint arXiv:2209.09385, 2022. 1
[62] Maosheng Ye, Rui Wan, Shuangjie Xu, Tongyi Cao, and
Qifeng Chen. Drinet++: Efficient voxel-as-point point cloud
segmentation. arXiv preprint arXiv: 2111.08318, 2021. 1
[63] Tengju Ye, Wei Jing, Chunyong Hu, Shikun Huang, Ling-
ping Gao, Fangzhen Li, Jingke Wang, Ke Guo, Wencong
Xiao, Weibo Mao, et al. Fusionad: Multi-modality fusion for
prediction and planning tasks of autonomous driving. arXiv
preprint arXiv:2308.01006, 2023. 2
[64] Wenyuan Zeng, Wenjie Luo, Simon Suo, Abbas Sadat, Bin
Yang, Sergio Casas, and Raquel Urtasun. End-to-end inter-
pretable neural motion planner. In CVPR, 2019. 7
[65] Yunpeng Zhang, Zheng Zhu, Wenzhao Zheng, Junjie Huang,
Guan Huang, Jie Zhou, and Jiwen Lu. Beverse: Unified per-
ception and prediction in birds-eye-view for vision-centric
autonomous driving.
arXiv preprint arXiv:2205.09743,
2022. 1, 2
[66] Yunpeng Zhang, Zheng Zhu, Wenzhao Zheng, Junjie Huang,
Guan Huang, Jie Zhou, and Jiwen Lu. Beverse: Unified per-
ception and prediction in birds-eye-view for vision-centric
autonomous driving.
arXiv preprint arXiv:2205.09743,
2022. 1, 2
[67] Jinyun Zhou, Rui Wang, Xu Liu, Yifei Jiang, Shu Jiang, Ji-
aming Tao, Jinghao Miao, and Shiyu Song. Exploring imita-
tion learning for autonomous driving with feedback synthe-
sizer and differentiable rasterization. In IROS, pages 1450–
1457, 2021. 2
[68] Xinge Zhu, Hui Zhou, Tai Wang, Fangzhou Hong, Yuexin
Ma, Wei Li, Hongsheng Li, and Dahua Lin. Cylindrical and
asymmetrical 3d convolution networks for lidar segmenta-
tion. In CVPR, pages 9939–9948, 2021. 1
[69] Sicheng Zuo, Wenzhao Zheng, Yuanhui Huang, Jie Zhou,
and Jiwen Lu.
Pointocc: Cylindrical tri-perspective view
for point-based 3d semantic occupancy prediction.
arXiv
preprint arXiv:2308.16896, 2023. 2, 4
11

