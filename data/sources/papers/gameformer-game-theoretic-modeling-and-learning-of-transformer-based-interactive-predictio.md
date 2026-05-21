# GameFormer: Game-theoretic Modeling and Learning of Transformer-based Interactive Prediction and Planning for Autonomous Driving

**Source**: arXiv:2303.05760

**Type**: Academic Paper

---

## Page 1

GameFormer: Game-theoretic Modeling and Learning of Transformer-based
Interactive Prediction and Planning for Autonomous Driving
Zhiyu Huang†, Haochen Liu†, Chen Lv∗
Nanyang Technological University, Singapore
† Equal contribution {zhiyu001,haochen002}@e.ntu.edu.sg
∗Corresponding author lyuchen@ntu.edu.sg
Abstract
Autonomous vehicles operating in complex real-world
environments require accurate predictions of interactive be-
haviors between traffic participants.
This paper tackles
the interaction prediction problem by formulating it with
hierarchical game theory and proposing the GameFormer
model for its implementation. The model incorporates a
Transformer encoder, which effectively models the relation-
ships between scene elements, alongside a novel hierarchi-
cal Transformer decoder structure. At each decoding level,
the decoder utilizes the prediction outcomes from the previ-
ous level, in addition to the shared environmental context,
to iteratively refine the interaction process. Moreover, we
propose a learning process that regulates an agent’s be-
havior at the current level to respond to other agents’ be-
haviors from the preceding level. Through comprehensive
experiments on large-scale real-world driving datasets, we
demonstrate the state-of-the-art accuracy of our model on
the Waymo interaction prediction task. Additionally, we val-
idate the model’s capacity to jointly reason about the mo-
tion plan of the ego agent and the behaviors of multiple
agents in both open-loop and closed-loop planning tests,
outperforming various baseline methods. Furthermore, we
evaluate the efficacy of our model on the nuPlan planning
benchmark, where it achieves leading performance. Project
website: https://mczhi.github.io/GameFormer/
1. Introduction
Accurately predicting the future behaviors of surround-
ing traffic participants and making safe and socially-
compatible decisions are crucial for modern autonomous
driving systems. However, this task is highly challenging
due to the complexities arising from road structures, traffic
norms, and interactions among road users [14, 23, 24]. In
recent years, deep neural network-based approaches have
shown remarkable advancements in prediction accuracy and
scalability [7, 11, 15, 22, 40]. In particular, Transformers
have gained prominence in motion prediction [25,31,32,35,
Level-0
Level-1
Level-K
Initial Modality Query
Plan
Trajectory
Predicted
Trajectory
Level-k
Vectorized Scene
Agent History + Map
AV
Neighboring 
Agents
Future trajectories
Common 
background
Figure 1. Hierarchical game theoretic modeling of agent interac-
tions. The historical states of agents and maps are encoded as
background information; a level-0 agent’s future is predicted in-
dependently based on the initial modality query; a level-k agent
responds to all other level-(k −1) agents.
45,47] because of their flexibility and effectiveness in pro-
cessing heterogeneous information from the driving scene,
as well as their ability to capture interrelationships among
the scene elements.
Despite the success of existing prediction models in
encoding the driving scene and representing interactions
through agents’ past trajectories, they often fail to explic-
itly model agents’ future interactions and their interaction
with the autonomous vehicle (AV). This limitation results
in a passive reaction from the AV’s planning module to the
prediction results. However, in critical situations such as
merge, lane change, and unprotected left turn, the AV needs
to proactively coordinate with other agents. Therefore, joint
prediction and planning are necessary for achieving more
interactive and human-like decision-making.
To address
this, a typical approach is the recently-proposed conditional
prediction model [17,34,36,37,39], which utilizes the AV’s
internal plans to forecast other agents’ responses to the AV.
Although the conditional prediction model mitigates the in-
teraction issue, such a one-way interaction still neglects the
dynamic mutual influences between the AV and other road
users. From a game theory perspective, the current pre-
diction/planning models can be regarded as leader-follower
games with limited levels of interaction among agents.
arXiv:2303.05760v2  [cs.RO]  11 Aug 2023


## Page 2

In this study, we utilize a hierarchical game-theoretic
framework (level-k game theory) [5, 42] to model the in-
teractions among various agents [27, 28, 41] and introduce
a novel Transformer-based prediction model named Game-
Former. Stemming from insights in cognitive science, level-
k game theory offers a structured approach to modeling in-
teractions among agents. At its core, the theory introduces a
hierarchy of reasoning depths denoted by k. A level-0 agent
acts independently without considering the possible actions
of other agents. As we move up the hierarchy, a level-1
agent considers interactions by assuming that other agents
are level-0 and predicts their actions accordingly. This pro-
cess continues iteratively, where a level-k agent predicts
others’ actions assuming they are level-(k−1) and responds
based on these predictions. Our model aligns with the spirit
of level-k game theory by considering agents’ reasoning
levels and explicit interactions.
As illustrated in Fig. 1, we initially encode the driving
scene into background information, encompassing vector-
ized maps and observed agent states, using Transformer en-
coders. In the future decoding stage, we follow the level-k
game theory to design the structure. Concretely, we set up
a series of Transformer decoders to implement level-k rea-
soning. The level-0 decoder employs only the initial modal-
ity query and encoded scene context as key and value to
predict the agent’s multi-modal future trajectories. Then, at
each iteration k, the level-k decoder takes as input the pre-
dicted trajectories from the level-(k−1) decoder, along with
the background information, to predict the agent’s trajec-
tories at the current level. Moreover, we design a learning
process that regulates the agents’ trajectories to respond to
the trajectories of other agents from the previous level while
also staying close to human driving data. The main contri-
butions of this paper are summarized as follows:
1. We propose GameFormer, a Transformer-based inter-
active prediction and planning framework. The model
employs a hierarchical decoding structure to capture
agent interactions, iteratively refine predictions, and is
trained based on the level-k game formalism.
2. We demonstrate the state-of-the-art prediction perfor-
mance of our GameFormer model on the Waymo in-
teraction prediction benchmark.
3. We validate the planning performance of the Game-
Former framework in open-loop driving scenes and
closed-loop simulations using the Waymo open motion
dataset and the nuPlan planning benchmark.
2. Related Work
2.1. Motion Prediction for Autonomous Driving
Neural network models have demonstrated remarkable
effectiveness in motion prediction by encoding contextual
scene information.
Early studies utilize long short-term
memory (LSTM) networks [1] to encode the agent’s past
states and convolutional neural networks (CNNs) to pro-
cess the rasterized image of the scene [7, 12, 21, 34]. To
model the interaction between agents, graph neural net-
works (GNNs) [4,13,20,30] are widely used for represent-
ing agent interactions via scene or interaction graphs. More
recently, the unified Transformer encoder-decoder structure
for motion prediction has gained popularity, e.g., Scene-
Transformer [32] and WayFormer [31], due to their com-
pact model description and superior performance. However,
most Transformer-based prediction models focus on the en-
coding part, with less emphasis on the decoding part. Mo-
tion Transformer [35] addresses this limitation by proposing
a well-designed decoding stage that leverages iterative local
motion refinement to enhance prediction accuracy. Inspired
by iterative refinement and hierarchical game theory, our
approach introduces a novel Transformer-based decoder for
interaction prediction, providing an explicit way to model
the interactions between agents.
Regarding the utilization of prediction models for plan-
ning tasks, numerous works focus on multi-agent joint mo-
tion prediction frameworks [14, 24, 30, 38] that enable effi-
cient and consistent prediction of multi-modal multi-agent
trajectories. An inherent issue in existing motion prediction
models is that they often ignore the influence of the AV’s ac-
tions, rendering them unsuitable for downstream planning
tasks. To tackle this problem, several conditional multi-
agent motion prediction models [8, 17, 36] have been pro-
posed by integrating AV planning information into the pre-
diction process. However, these models still exhibit one-
way interactions, neglecting the mutual influence among
agents. In contrast, our approach aims to jointly predict the
future trajectories of surrounding agents and facilitate AV
planning through iterative mutual interaction modeling.
2.2. Learning for Decision-making
The primary objective of the motion prediction module
is to enable the planning module to make safe and intelli-
gent decisions. This can be achieved through the use of of-
fline learning methods that can learn decision-making poli-
cies from large-scale driving datasets. Imitation learning
stands as the most prevalent approach, which aims to learn
a driving policy that can replicate expert behaviors [19,44].
Offline reinforcement learning [26] has also gained interest
as it combines the benefits of reinforcement learning and
large collected datasets. However, direct policy learning
lacks interpretability and safety assurance, and often suf-
fers from distributional shifts. In contrast, planning with a
learned motion prediction model is believed to be more in-
terpretable and robust [3,6,18,46], making it a more desir-
able way for autonomous driving. Our proposed approach
aims to enhance the capability of prediction models that can
improve interactive decision-making performance.
2


## Page 3

Transformer Encoder
Level-0 Decoder
Scene context encoding
Modality embedding 
query
Agent history 
query 
Query 
content
K&V
×K
Agent State 
Encoder
Map Polyline 
Encoder
Self-attention
Cross-attention
K&V
GMM Prediction
Query 
content
Scores
Trajectories
Level-k 
Decoder
...
...
...
...
...
Map encoding
Agent encoding
Concatenate
Trajectories
Scores
Level-(k-1) 
future query
Level-(k-1) agent future encoding
Figure 2. Overview of our proposed GameFormer framework. The scene context encoding is obtained via a Transformer-based encoder;
the level-0 decoder takes the modality embedding and agent history encodings as query and outputs level-0 future trajectories and scores;
the level-k decoder uses a self-attention module to model the level-(k −1) future interaction and append it to the scene context encoding.
3. GameFormer
We introduce our interactive prediction and planning
framework, called GameFormer, which adopts the Trans-
former encoder-decoder architecture (see Fig. 2). In the fol-
lowing sections, we first define the problem and discuss the
level-k game theory that guides the design of the model and
learning process in Sec. 3.1. We then describe the encoder
component of the model, which encodes the scene context,
in Sec. 3.2, and the decoder component, which incorporates
a novel interaction modeling concept, in Sec. 3.3. Finally,
we present the learning process that accounts for interac-
tions among different reasoning levels in Sec. 3.4.
3.1. Game-theoretic Formulation
We consider a driving scene with N agents, where
the AV is denoted as A0 and its neighboring agents as
A1, · · · , AN−1 at the current time t = 0. Given the his-
torical states of all agents (including the AV) over an ob-
servation horizon Th, S = {s−Th:0
i
}, as well as the map
information M including traffic lights and road waypoints,
the goal is to jointly predict the future trajectories of neigh-
boring agents Y1:Tf
1:N−1 over the future horizon Tf, as well
as a planned trajectory for the AV Y1:Tf
0
. In order to cap-
ture the uncertainty, the results are multi-modal future tra-
jectories for the AV and neighboring agents, denoted by
Y1:Tf
i
= {y1:Tf
j
, pj|j =1 : M}, where y1:Tf
j
is a sequence
of predicted states, pj the probability of the trajectory, and
M the number of modalities.
We leverage level-k game theory to model agent interac-
tions in an iterative manner. Instead of simply predicting a
single set of trajectories, we predict a hierarchy of trajecto-
ries to model the cognitive interaction process. At each rea-
soning level, with the exception of level-0, the decoder takes
as input the prediction results from the previous level, which
effectively makes them a part of the scene, and estimates the
responses of agents in the current level to other agents in the
previous level. We denote the predicted multi-modal trajec-
tories (essentially a Gaussian mixture model) of agent i at
reasoning level k as π(k)
i
, which can be regarded as a policy
for that agent. The policy π(k)
i
is conditioned on the poli-
cies of all other agents except the i-th agent at level-(k −1),
denoted by π(k−1)
¬i
. For instance, the AV’s policy at level-2
π(2)
0
would take into account all neighboring agents’ poli-
cies at level-1 π(1)
1:N−1. Formally, the i-th agent’s level-k
policy is set to optimize the following objective:
  \
mi
n 
_
{
\pi 
_
i } \ \m
at
h
cal {L}^k_i \left ( \pi _{i}^{(k)} \mid \pi _{\neg i}^{(k-1)} \right ), 
(1)
where L(·) is the loss (or cost) function. It is important to
note that policy π here represents the multi-modal predicted
trajectories (GMM) of an agent and that the loss function is
calculated on the trajectory level.
3


## Page 4

For the level-0 policies, they do not take into account
probable actions or reactions of other agents and instead
behave independently. Based on the level-k game theory
framework, we design the future decoder, which we elabo-
rate upon in Section 3.3.
3.2. Scene Encoding
Input representation. The input data comprises histor-
ical state information of agents, Sp ∈RN×Th×ds, where ds
represents the number of state attributes, and local vector-
ized map polylines M ∈RN×Nm×Np×dp. For each agent,
we find Nm nearby map elements such as routes and cross-
walks, each containing Np waypoints with dp attributes.
The inputs are normalized according to the state of the ego
agent, and any missing positions in the tensors are padded
with zeros.
Agent History Encoding. We use LSTM networks to
encode the historical state sequence Sp for each agent, re-
sulting in a tensor Ap ∈RN×D, which contains the past
features of all agents. Here, D denotes the hidden feature
dimension.
Vectorized Map Encoding. To encode the local map
polylines of all agents, we use the multi-layer percep-
tron (MLP) network, which generates a map feature tensor
Mp ∈RN×Nm×Np×D with a feature dimension of D. We
then group the waypoints from the same map element and
use max-pooling to aggregate their features, reducing the
number of map tokens. The resulting map feature tensor is
reshaped into Mr ∈RN×Nmr×D, where Nmr represents
the number of aggregated map elements.
Relation Encoding.
We concatenate the agent fea-
tures and their corresponding local map features to cre-
ate an agent-wise scene context tensor Ci = [Ap, M i
p] ∈
R(N+Nmr)×D for each agent. We use a Transformer en-
coder with E layers to capture the relationships among all
the scene elements in each agent’s context tensor Ci. The
Transformer encoder is applied to all agents, generating a fi-
nal scene context encoding Cs ∈RN×(N+Nmr)×D, which
represents the common environment background inputs for
the subsequent decoder network.
3.3. Future Decoding with Level-k Reasoning
Modality embedding. To account for future uncertain-
ties, we need to initialize the modality embedding for each
possible future, which serves as the query to the level-0 de-
coder. This can be achieved through either a heuristics-
based method, learnable initial queries [31], or through a
data-driven method [35].
Specifically, a learnable initial
modality embedding tensor I ∈RN×M×D is generated,
where M represents the number of future modalities.
Level-0 Decoding.
In the level-0 decoding layer, a
multi-head cross-attention Transformer module is utilized,
which takes as input the combination of the initial modality
embedding I and the agent’s historical encoding in the final
scene context Cs,Ap (by inflating a modality axis), result-
ing in (Cs,Ap + I) ∈RN×M×D as the query and the scene
context encoding Cs as the key and value. The attention is
applied to the modality axis for each agent, and the query
content features can be obtained after the attention layer as
ZL0 ∈RN×M×D. Two MLPs are appended to the query
content features ZL0 to decode the GMM components of
predicted futures GL0 ∈RN×M×Tf ×4 (corresponding to
(µx, µy, log σx, log σy) at every timestep) and the scores of
these components PL0 ∈RN×M×1.
Level-(k-1) 
Scores
𝑷𝑳𝒌−𝟏 [N, M, 1]
Level-(k-1) 
Trajectories
𝑺𝒇
𝑳𝒌−𝟏 [N, M, Tf , 2]
MLP +
Max-Pooling
Future Encoding
𝑨𝒇
𝑳𝒌−𝟏 [N, D]
Self-attention Transformer
Cross-attention Transformer
Scene Context 
Encoding
𝑪𝒔𝒊 [N+Nm , D]
MLP
Updated Scene 
Context Encoding
𝑪𝑳𝒌
𝒊 [N+N+Nm, D]
MLP
Multi-future
Encoding
𝑨𝒎𝒇
𝑳𝒌−𝟏 [N, M, D]
Future Interaction
𝑨𝒇𝒊
𝑳𝒌−𝟏 [N, D]
Q
K
V
Level-(k-1) Agent 
Query content
𝒁𝑳𝒌−𝟏 
𝒊
[M, D]
Level-(k) Agent 
Scores
𝑷𝑳𝒌
𝒊 [M, 1]
Level-(k) Agent 
Gaussians
𝑮𝑳𝒌
𝒊 [M, Tf , 4]
Weighted
Sum
Concatenate
Agent Multi-future
𝑨𝒎𝒇
𝒊,𝑳𝒌−𝟏 [M, D]
Agent 
Future
Mask
Q
K
V
Agent Query 
Content 𝒁𝑳𝒌
𝒊 [M, D]
Figure 3. The detailed structure of a level-k interaction decoder.
Interaction Decoding. The interaction decoding stage
contains K decoding layers corresponding to K reason-
ing levels.
In the level-k layer (k ≥1), it receives all
agents’ trajectories from the level-(k −1) layer SLk−1
f
∈
RN×M×Tf ×2 (the mean values of the GMM GLk−1) and
use an MLP with max-pooling on the time axis to encode
the trajectories, resulting in a tensor of agent multi-modal
future trajectory encoding ALk−1
mf
∈RN×M×D. Then, we
apply weighted-average-pooling on the modality axis with
the predicted scores from the level-(k −1) layer PLk−1 to
obtain the agent future features ALk−1
f
∈RN×D. We use
a multi-head self-attention Transformer module to model
the interactions between agent future trajectories ALk−1
fi
and
concatenate the resulting interaction features with the scene
context encoding from the encoder part. This yields an up-
4


## Page 5

dated scene context encoding for agent i, denoted by Ci
Lk =
[ALk−1
fi
, Ci
s] ∈R(N+Nm+N)×D. We adopt a multi-head
cross-attention Transformer module with the query content
features from the level-(k −1) layer Zi
Lk−1 and agent future
features ALk−1
mf
, (Zi
Lk−1 + Ai,Lk−1
mf
) ∈RM×D as query and
the updated scene context encoding Ci
Lk as key and value.
We use a masking strategy to prevent an agent from access-
ing its own future information from the last layer. For ex-
ample, agent A0 can only get access to the future interaction
features of other agents {A1, · · · , AN−1}. Finally, the re-
sulting query content tensor from the cross-attention mod-
ule Zi
Lk is passed through two MLPs to decode the agent’s
GMM components and scores, respectively. Fig. 3 illus-
trates the detailed structure of a level-k interaction decoder.
Note that we share the level-k decoder for all agents to gen-
erate multi-agent trajectories at that level. At the final level
of interaction decoding, we can obtain multi-modal trajec-
tories for the AV and neighboring agents GLK, as well as
their scores PLK.
3.4. Learning Process
We present a learning process to train our model using
the level-k game theory formalism. First, we employ imi-
tation loss as the primary loss to regularize the agent’s be-
haviors, which can be regarded as a surrogate for factors
such as traffic regulations and driving styles. The future be-
havior of an agent is modeled as a Gaussian mixture model
(GMM), where each mode m at time step t is described by
a Gaussian distribution over the (x, y) coordinates, charac-
terized by mean µt
m and covariance σt
m. The imitation loss
is computed using the negative log-likelihood loss from the
best-predicted component m∗(closest to the ground truth)
at each timestep, as formulated:
  \ m
at
h
cal
 {L}_{I
L} = 
\su m _{ t=1}^{T_f} \mathcal {L}_{NLL}(\mu ^{t}_{m^*}, \sigma ^{t}_{m^*}, p_{m*}, \mathbf {s}_t). 
(2)
The negative log-likelihood loss function LNLL is de-
fined as follows:
  \s m all  \math cal 
{
L}_{
NL
L}
 
= \
lo
g \
sigma _x + \log \sigma _y + \frac {1}{2} \left ( \left ( \frac {dx}{\sigma _x} \right )^2 + \left ( \frac {dx}{\sigma _x} \right )^2 \right ) - \log (p_{m*}), 
(3)
where dx = sx −µx and dy = sy −µy, (sx, sy) is ground-
truth position; pm∗is the probability of the selected compo-
nent, and we use the cross-entropy loss in practice.
For a level-k agent A(k)
i
, we design an auxiliary loss
function inspired by prior works [4, 16, 29] that considers
the agent’s interactions with others. The safety of agent
interactions is crucial, and we use an interaction loss (ap-
plicable only to decoding levels k ≥1) to encourage the
agent to avoid collisions with the possible future trajecto-
ries of other level-(k −1) agents. Specifically, we use a
repulsive potential field in the interaction loss to discourage
the agent’s future trajectories from getting too close to any
possible trajectory of any other level-(k −1) agent A(k−1)
¬i
.
The interaction loss is defined as follows:
  \mat h
c
a
l {
L}
_
{In
ter
} = \
sum _{
m
=
1
}^{M} \
sum  _{t=1}^{T
_f}
 
\ m
ax _{ \substack {\forall j \neq i \\ \forall n \in {1:M}}} \frac {1}{ d \left ( \mathbf {\hat s}^{(i, k)}_{m, t}, \mathbf {\hat s}^{(j, k-1)}_{n, t} \right ) + 1}, 
(4)
where d(·, ·) is the L2 distance between the future states
((x, y) positions), m is the mode of the agent i, n is the
mode of the level-(k −1) agent j. To ensure activation of
the repulsive force solely within close proximity, a safety
margin is introduced, meaning the loss is only applied to
interaction pairs with distances smaller than a threshold.
The total loss function for the level-k agent i is the
weighted sum of the imitation loss and interaction loss.
  
\ label
 
{ l oss} \math
c
a l  {L}_{i}^{k}(
\
p i _i^{
(k
)}) = w_{1} \mathcal {L}_{IL}(\pi _i^{(k)}) + w_{2} \mathcal {L}_{Inter}(\pi _i^{(k)}, \pi _{\neg i}^{(k-1)}), (5)
where w1 and w2 are the weighting factors to balance the
influence of the two loss terms.
4. Experiments
4.1. Experimental Setup
Dataset. We set up two different model variants for dif-
ferent evaluation purposes. The prediction-oriented model
is trained and evaluated using the Waymo open motion
dataset (WOMD) [9], specifically addressing the task of
predicting the joint trajectories of two interacting agents.
For the planning tasks, we train and test the models on both
WOMD with selected interactive scenarios and the nuPlan
dataset [2] with a comprehensive evaluation benchmark.
Prediction-oriented model. We adopt the setting of the
WOMD interaction prediction task, where the model pre-
dicts the joint future positions of two interacting agents 8
seconds into the future. The neighboring agents within the
scene will serve as the background information in the en-
coding stage, while only the two labeled interacting agents’
joint future trajectories are predicted. The model is trained
on the entire WOMD training dataset, and we employ the
official evaluation metrics, which include minimum aver-
age displacement error (minADE), minimum final displace-
ment error (minFDE), miss rate, and mean average preci-
sion (mAP). We investigate two different prediction model
settings. Firstly, we consider the joint prediction setting,
where only M = 6 joint trajectories of the two agents are
predicted [32]. Secondly, we examine the marginal predic-
tion setting and train our model to predict M = 64 marginal
trajectories for each agent in the interaction pair. During in-
ference, the EM method proposed in MultiPath++ [40] is
employed to generate a set of 6 marginal trajectories for
each agent, from which the top 6 joint predictions are se-
lected for these two agents.
5


## Page 6

Planning-oriented model. We introduce another model
variant designed for planning tasks. Specifically, this vari-
ant takes into account multiple neighboring agents around
the AV and predicts their future trajectories. The model
is trained and tested across two datasets: WOMD and nu-
Plan. For WOMD, we randomly select 10,000 20-second
scenarios, where 9,000 of them are used for training and
the remaining 1,000 for validation.
Then, we evaluate
the model’s joint prediction and planning performance on
400 9-second interactive and dynamic scenarios (e.g., lane-
change, merge, and left-turn) in both open-loop and closed-
loop settings. To conduct closed-loop testing, we utilize
a log-replay simulator [18] to replay the original scenar-
ios involving other agents, with our planner taking control
of the AV. In open-loop testing, we employ distance-based
error metrics, which include planning ADE, collision rate,
miss rate, and prediction ADE. In closed-loop testing, we
focus on evaluating the planner’s performance in a realistic
driving context by measuring metrics including success rate
(no collision or off-route), progress along the route, longi-
tudinal acceleration and jerk, lateral acceleration, and po-
sition errors. For the nuPlan dataset, we design a compre-
hensive planning framework and adhere to the nuPlan chal-
lenge settings to evaluate the planning performance. Specif-
ically, we evaluate the planner’s performance in three tasks:
open-loop planning, closed-loop planning with non-reactive
agents, and closed-loop with reactive agents. These tasks
are evaluated using a comprehensive set of metrics pro-
vided by the nuPlan platform, and an overall score is derived
based on these tasks. More information about our models is
provided in the supplementary material.
4.2. Main Results
4.2.1
Interaction Prediction
Within the prediction-oriented model, we use a stack of
E = 6 Transformer encoder layers, and the hidden feature
dimension is set to D = 256. We consider 20 neighboring
agents around the two interacting agents as background in-
formation and employ K = 6 decoding layers. The model
only generates trajectories for the two labeled interacting
agents. Moreover, the local map elements for each agent
comprise possible lane polylines and crosswalk polylines.
Quantitative results. Table 1 summarizes the predic-
tion performance of our model in comparison with state-of-
the-art methods on the WOMD interaction prediction (joint
prediction of two interacting agents) benchmark. The met-
rics are averaged over different object types (vehicle, pedes-
trian, and cyclist) and evaluation times (3, 5, and 8 seconds).
Our joint prediction model (GameFormer (J, M=6)) outper-
forms existing methods in terms of position errors. This can
be attributed to its superior ability to capture future interac-
tions between agents through an iterative process and to pre-
dict future trajectories in a scene-consistent manner. How-
ever, the scoring performance of the joint model is limited
without predicting an over-complete set of trajectories and
aggregation. To mitigate this issue, we employ the marginal
prediction model (GameFormer (M, M=64)) with EM ag-
gregation, which significantly improves the scoring perfor-
mance (better mAP metric). The overall performance of
our marginal model is comparable to that of the ensemble
and more complicated MTR model [35]. Nevertheless, it
is worth noting that marginal ensemble models may not be
practical for real-world applications due to their substan-
tial computational burden. Therefore, we utilize the joint
prediction model, which provides better prediction accuracy
and computational efficiency, for planning tests.
Table 1. Comparison with state-of-the-art models on the WOMD
interaction prediction benchmark
Model
minADE (↓)
minFDE (↓)
Miss rate (↓)
mAP (↑)
LSTM baseline [9]
1.9056
5.0278
0.7750
0.0524
Heat [30]
1.4197
3.2595
0.7224
0.0844
AIR2 [43]
1.3165
2.7138
0.6230
0.0963
SceneTrans [32]
0.9774
2.1892
0.4942
0.1192
DenseTNT [15]
1.1417
2.4904
0.5350
0.1647
M2I [37]
1.3506
2.8325
0.5538
0.1239
MTR [35]
0.9181
2.0633
0.4411
0.2037
GameFormer (M, M=64)
0.9721
2.2146
0.4933
0.1923
GameFormer (J, M=6)
0.9161
1.9373
0.4531
0.1376
Qualitative results. Fig. 4 illustrates the interaction
prediction performance of our approach in several typical
scenarios. In the vehicle-vehicle interaction scenario, two
distinct situations are captured by our model: vehicle 2 ac-
celerates to take precedence at the intersection, and vehicle
2 yields to vehicle 1. In both cases, our model predicts that
vehicle 1 creeps forward to observe the actions of vehicle 2
before executing a left turn. In the vehicle-pedestrian sce-
nario, our model predicts that the vehicle will stop and wait
for the pedestrian to pass before starting to move. In the
vehicle-cyclist interaction scenario, where the vehicle in-
tends to merge into the right lane, our model predicts the
vehicle will decelerate and follow behind the cyclist in that
lane. Overall, the results manifest that our model can cap-
ture multiple interaction patterns of interacting agents and
accurately predict their possible joint futures.
4.2.2
Open-loop Planning
We first conduct the planning tests in selected WOMD sce-
narios with a prediction/planning horizon of 5 seconds. The
model uses a stack of E = 6 Transformer encoder layers,
and we consider 10 neighboring agents closest to the ego
vehicle to predict M = 6 joint future trajectories for them.
Determining the decoding levels. To determine the op-
timal reasoning levels for planning, we analyze the impact
of decoding layers on open-loop planning performance, and
the results are presented in Table 2. Although the planning
ADE and prediction ADE exhibit a slight decrease with ad-
6


## Page 7

V1
V2
V
C
V
P
t+0s
t+8s
low
high
Vehicle-Vehicle
Vehicle-Pedestrian
Vehicle-Cyclist
Time Score
Figure 4. Qualitative results of the proposed method in interaction prediction (multi-modal joint prediction of two interacting agents). The
red boxes are interacting agents to predict and the magenta boxes are background neighboring agents.
t+0s
t+0s
t+5s
t+5s
Roadside Parking
Merge
Intersection
Time 
ego
Time 
other
Figure 5. Qualitative results of the proposed method in open-loop planning. The red box is the AV and the magenta boxes are its neighboring
agents; the red trajectory is the plan of the AV and the blue ones are the predictions of neighboring agents.
ditional decoding layers, the miss rate and collision rate are
at their lowest when the decoding level is 4. The intuition
behind this observation is that humans are capable of per-
forming only a limited depth of reasoning, and the optimal
iteration depth empirically appears to be 4 in this test.
Table 2. Influence of decoding levels on open-loop planning
Level
Planning ADE
Collision Rate
Miss Rate
Prediction ADE
0
0.9458
0.0384
0.1154
1.0955
1
0.8846
0.0305
0.0994
0.9377
2
0.8529
0.0277
0.0897
0.8875
3
0.8423
0.0269
0.0816
0.8723
4
0.8329
0.0198
0.0753
0.8527
5
0.8171
0.0245
0.0777
0.8361
6
0.8208
0.0238
0.0826
0.8355
Quantitative results. Our joint prediction and planning
model employs 4 decoding layers, and the results of the fi-
nal decoding layer (the most-likely future evaluated by the
trained scorer) are utilized as the plan for the AV and predic-
tions for other agents. We set up some imitation learning-
based planning methods as baselines, which are: 1) vanilla
imitation learning (IL), 2) deep imitative model (DIM) [33],
3) MultiPath++ [40] (which predicts multi-modal trajecto-
ries for the ego agent), 4) MTR-e2e (end-to-end variant with
learnable motion queries) [35], and 5) differentiable inte-
grated prediction and planning (DIPP) [18]. Table 3 reports
the open-loop planning performance of our model in com-
parison with the baseline methods. The results reveal that
our model performs significantly better than vanilla IL and
DIM, because they are just trained to output the ego’s trajec-
tory while not explicitly predicting other agents’ future be-
haviors. Compared to performant motion prediction models
(MultiPath++ and MTR-e2e), our model also shows better
planning metrics for the ego agent. Moreover, our model
outperforms DIPP (a joint prediction and planning method)
in both planning and prediction metrics, especially the col-
lision rate. These results emphasize the advantage of our
model, which explicitly considers all agents’ future behav-
iors and iteratively refines the interaction process.
Qualitative results. Fig. 5 displays qualitative results
of our model’s open-loop planning performance in complex
driving scenarios. For clarity, only the most-likely trajecto-
ries of the agents are displayed. These results demonstrate
that our model can generate a plausible future trajectory for
the AV and handle diverse interaction scenarios, and predic-
tions of the surrounding agents enhance the interpretability
of our planning model’s output.
7


## Page 8

Table 3. Evaluation of open-loop planning performance in selected WOMD scenarios
Method
Collision rate (%)
Miss rate (%)
Planning error (m)
Prediction error (m)
@1s
@3s
@5s
ADE
FDE
Vanilla IL
4.25
15.61
0.216
1.273
3.175
–
–
DIM
4.96
17.68
0.483
1.869
3.683
–
–
MultiPath++
2.86
8.61
0.146
0.948
2.719
–
–
MTR-e2e
2.32
8.88
0.141
0.888
2.698
–
–
DIPP
2.33
8.44
0.135
0.928
2.803
0.925
2.059
Ours
1.98
7.53
0.129
0.836
2.451
0.853
1.919
Table 4. Evaluation of closed-loop planning performance in selected WOMD scenarios
Method
Success rate
Progress
Acceleration
Jerk
Lateral acc.
Position error to expert driver (m)
(%)
(m)
(m/s2)
(m/s3)
(m/s2)
@3s
@5s
@8s
Vanilla IL
0
6.23
1.588
16.24
0.661
9.355
20.52
46.33
RIP
19.5
12.85
1.445
14.97
0.355
7.035
17.13
38.25
CQL
10
8.28
3.158
25.31
0.152
10.86
21.18
40.17
DIPP
68.12±5.51
41.08±5.88
1.44±0.18
12.58±3.23
0.31±0.11
6.22±0.52
15.55±1.12
26.10±3.88
Ours
73.16±6.14
44.94±7.69
1.19±0.15
13.63±2.88
0.32±0.09
5.89±0.78
12.43±0.51
21.02±2.48
DIPP (w/ refinement)
92.16±0.62
51.85±0.14
0.58±0.03
1.54±0.19
0.11±0.01
2.26±0.10
5.55±0.24
12.53±0.48
Ours (w/ refinement)
94.50±0.66
52.67±0.33
0.53±0.02
1.56±0.23
0.10±0.01
2.11±0.21
4.87±0.18
11.13±0.33
4.2.3
Closed-loop Planning
We evaluate the closed-loop planning performance of our
model in selected WOMD scenarios. Within a simulated
environment [18], we execute the planned trajectory gener-
ated by the model and update the ego agent’s state at each
time step, while other agents follow their logged trajectories
from the dataset. Since other agents do not react to the ego
agent, the success rate is a lower bound for safety assess-
ment. For planning-based methods (DIPP and our proposed
method), we project the output trajectory onto a reference
path to ensure the ego vehicle’s adherence to the roadway.
Additionally, we employ a cost-based refinement planner
[18], which utilizes the initial output trajectory and the pre-
dicted trajectories of other agents to explicitly regulate the
ego agent’s actions. Our method is compared against four
baseline methods: 1) vanilla IL, 2) robust imitative planning
(RIP) [10], 3) conservative Q-learning (CQL) [26], and 4)
DIPP [18]. We report the means and standard deviations of
the planning-based methods over three training runs (mod-
els trained with different seeds). The quantitative results
of closed-loop testing are summarized in Table 4. The re-
sults show that the IL and offline RL methods exhibit subpar
performance in the closed-loop test, primarily due to distri-
butional shifts and casual confusion. In contrast, planning-
based methods perform significantly better across all met-
rics. Without the refinement step, our model outperforms
DIPP because it captures agent interactions more effectively
and thus the raw trajectory is closer to an expert driver.
With the refinement step, the planner becomes more robust
against training seeds, and our method surpasses DIPP be-
cause it can deliver better predictions of agent interactions
and provide a good initial plan to the refinement planner.
4.2.4
nuPlan Benchmark Evaluation
To handle diverse driving scenarios in the nuPlan plat-
form [2], we develop a comprehensive planning framework
GameFormer Planner. It fulfills all important steps in the
planning pipeline, including feature processing, path plan-
ning, model query, and motion refinement. We increase the
prediction and planning horizon to 8 seconds to meet bench-
mark requirements. The evaluation is conducted over three
tasks: open-loop (OL) planning, closed-loop (CL) planning
with non-reactive agents, and closed-loop planning with re-
active agents. The score for each individual task is calcu-
lated using various metrics and scoring functions, and an
overall score is obtained by aggregating these task-specific
scores. It is important to note that we reduce the size of our
model (encoder and decoder layers) due to limited compu-
tational resources on the test server. The performance of our
model on the nuPlan test benchmark is presented in Table 5,
in comparison with other competitive learning-based meth-
ods and a rule-based approach (IDM Planner). The results
reveal the capability of our planning framework in achiev-
ing high-quality planning results across the evaluated tasks.
Moreover, the closed-loop visualization results illustrate the
ability of our model to facilitate the ego vehicle in making
interactive and human-like decisions.
Table 5. Results on the nuPlan planning test benchmark
Method
Overall
OL
CL non-reactive
CL reactive
Hoplan
0.8745
0.8523
0.8899
0.8813
Multi path
0.8477
0.8758
0.8165
0.8506
GameFormer
0.8288
0.8400
0.8087
0.8376
Urban Driver
0.7467
0.8629
0.6821
0.6952
IDM Planner
0.5912
0.2944
0.7243
0.7549
8


## Page 9

4.3. Ablation Study
Effects of agent future modeling. We investigate the
impact of different agent future modeling settings on open-
loop planning performance in WOMD scenarios. We com-
pare our base model to three ablated models: 1) No future:
agent future trajectories from the preceding level are not
incorporated in the decoding process at the current level,
2) No self-attention: agent future trajectories are incorpo-
rated but not processed through a self-attention module,
and 3) No interaction loss: the model is trained without
the proposed interaction loss. The results, as presented in
Table 6, demonstrate that our game-theoretic approach can
significantly improve planning and prediction accuracy. It
underscores the advantage of utilizing the future trajecto-
ries of agents from the previous level as contextual infor-
mation for the current level. Additionally, incorporating a
self-attention module to represent future interactions among
agents improves the accuracy of planning the prediction.
Using the proposed interaction loss during training can sig-
nificantly reduce the collision rate.
Table 6. Influence of future modeling on open-loop planning
Planning ADE
Collision Rate
Miss Rate
Prediction ADE
No future
0.9210
0.0295
0.0963
0.9235
No self-attention
0.8666
0.0231
0.0860
0.8856
No interaction loss
0.8415
0.0417
0.0846
0.8486
Base
0.8329
0.0198
0.0753
0.8527
Influence of decoder structures. We investigate the in-
fluence of decoder structures on the open-loop planning task
in WOMD scenarios. Specifically, we examine two ablated
models. First, we assess the importance of incorporating
k independent decoder layers, as opposed to training a sin-
gle shared interaction decoder and iteratively applying it k
times. Second, we explore the impact of simplifying the de-
coder into a multi-layer Transformer that does not generate
intermediate states. This translates into applying the loss
solely to the final decoding layer, rather than all intermedi-
ate layers. The results presented in Table 7 demonstrate bet-
ter open-loop planning performance for the base model (in-
dependent decoding layers with intermediate trajectories).
This design allows each layer to capture different levels of
relationships, thereby facilitating hierarchical modeling. In
addition, the omission of intermediate trajectory outputs can
degrade the model’s performance, highlighting the neces-
sity of regularizing the intermediate state outputs.
Table 7. Influence of decoder structures on open-loop planning
Planning ADE
Collision Rate
Miss Rate
Prediction ADE
Base
0.8329
0.0198
0.0753
0.8547
Shared decoder
0.9196
0.0382
0.0860
0.9095
Multi-layer decoder
0.9584
0.0353
0.0988
0.9637
Ablation results on the interaction prediction task.
We investigate the influence of the decoder on the WOMD
interaction prediction task. Specifically, we vary the decod-
ing levels from 0 to 8 to determine the optimal decoding
level for this task. Moreover, we remove either the agent
future encoding part from the decoder or the self-attention
module (for modeling agent future interactions) to investi-
gate their influences on prediction performance. We train
the ablated models using the same training set and evalu-
ate their performance on the validation set. The results in
Table 8 reveal that the empirically optimal number of de-
coding layers is 6 for the interaction prediction task. It is
evident that fewer decoding layers fail to adequately cap-
ture the interaction dynamics, resulting in subpar predic-
tion performance. However, using more than 6 decoding
layers may introduce training instability and overfitting is-
sues, leading to worse testing performance. Similarly, we
find that incorporating predicted agent future information
is crucial for achieving good performance, and using self-
attention to model the interaction among agents’ futures can
also improve prediction accuracy.
Table 8. Decoder ablation results on interaction prediction
Decoding layers
minADE
minFDE
Miss Rate
mAP
K=0
1.0505
2.2905
0.5113
0.1226
K=1
1.0169
2.1876
0.5061
0.1281
K=3
0.9945
2.1143
0.5026
0.1265
K=6
0.9133
1.9251
0.4564
0.1339
K=8
0.9839
2.1515
0.5003
0.1255
K=6 w/o future
0.9862
2.0848
0.4979
0.1256
K=6 w/o self-attention
0.9263
1.9931
0.4599
0.1281
5. Conclusions
This paper introduces GameFormer, a Transformer-
based model that utilizes hierarchical game theory for in-
teractive prediction and planning. Our proposed approach
incorporates novel level-k interaction decoders in the Trans-
former prediction model that iteratively refine the future
trajectories of interacting agents.
We also implement a
learning process that regulates the predicted behaviors of
agents based on the prediction results from the previous
level.
Experimental results on the Waymo open motion
dataset demonstrate that our model achieves state-of-the-art
accuracy in interaction prediction and outperforms baseline
methods in both open-loop and closed-loop planning tests.
Moreover, our proposed planning framework delivers lead-
ing performance on the nuPlan planning benchmark.
Acknowledgement
This work was supported in part by the A*STAR AME
Young Individual Research Grant (No. A2084c0156), the
MTC Individual Research Grants (No.M22K2c0079), the
ANR-NRF joint grant (No.NRF2021-NRF-ANR003 HM
Science), and the SUG-NAP Grant of Nanyang Technolog-
ical University, Singapore.
9


## Page 10

References
[1] Alexandre Alahi, Kratarth Goel, Vignesh Ramanathan,
Alexandre Robicquet, Li Fei-Fei, and Silvio Savarese. So-
cial lstm: Human trajectory prediction in crowded spaces. In
Proceedings of the IEEE conference on computer vision and
pattern recognition, pages 961–971, 2016. 2
[2] Holger Caesar, Juraj Kabzan, Kok Seang Tan, Whye Kit
Fong, Eric Wolff, Alex Lang, Luke Fletcher, Oscar Beijbom,
and Sammy Omari. nuplan: A closed-loop ml-based plan-
ning benchmark for autonomous vehicles. In CVPR ADP3
workshop, 2021. 5, 8
[3] Sergio Casas, Abbas Sadat, and Raquel Urtasun. Mp3: A
unified model to map, perceive, predict and plan. In Pro-
ceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition, pages 14403–14412, 2021. 2
[4] Yuxiao Chen, Boris Ivanovic, and Marco Pavone.
Scept:
Scene-consistent, policy-based trajectory predictions for
planning. In Proceedings of the IEEE/CVF Conference on
Computer Vision and Pattern Recognition, pages 17103–
17112, 2022. 2, 5
[5] Miguel A Costa-Gomes, Vincent P Crawford, and Nagore
Iriberri.
Comparing models of strategic thinking in van
huyck, battalio, and beil’s coordination games. Journal of
the European Economic Association, 7(2-3):365–376, 2009.
2
[6] Alexander Cui, Sergio Casas, Abbas Sadat, Renjie Liao,
and Raquel Urtasun. Lookout: Diverse multi-future predic-
tion and planning for self-driving.
In Proceedings of the
IEEE/CVF International Conference on Computer Vision,
pages 16107–16116, 2021. 2
[7] Henggang Cui, Vladan Radosavljevic, Fang-Chieh Chou,
Tsung-Han Lin, Thi Nguyen, Tzu-Kuo Huang, Jeff Schnei-
der, and Nemanja Djuric. Multimodal trajectory predictions
for autonomous driving using deep convolutional networks.
In 2019 International Conference on Robotics and Automa-
tion (ICRA), pages 2090–2096. IEEE, 2019. 1, 2
[8] Jose Luis Vazquez Espinoza, Alexander Liniger, Wilko
Schwarting, Daniela Rus, and Luc Van Gool. Deep inter-
active motion prediction and planning: Playing games with
motion prediction models. In Learning for Dynamics and
Control Conference, pages 1006–1019. PMLR, 2022. 2
[9] Scott Ettinger, Shuyang Cheng, Benjamin Caine, Chenxi
Liu, Hang Zhao, Sabeek Pradhan, Yuning Chai, Ben Sapp,
Charles R Qi, Yin Zhou, et al. Large scale interactive motion
forecasting for autonomous driving: The waymo open mo-
tion dataset. In Proceedings of the IEEE/CVF International
Conference on Computer Vision, pages 9710–9719, 2021. 5,
6
[10] Angelos Filos,
Panagiotis Tigkas,
Rowan McAllister,
Nicholas Rhinehart, Sergey Levine, and Yarin Gal. Can au-
tonomous vehicles identify, recover from, and adapt to dis-
tribution shifts?
In International Conference on Machine
Learning, pages 3145–3153. PMLR, 2020. 8
[11] Jiyang Gao, Chen Sun, Hang Zhao, Yi Shen, Dragomir
Anguelov, Congcong Li, and Cordelia Schmid. Vectornet:
Encoding hd maps and agent dynamics from vectorized rep-
resentation.
In Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, pages 11525–
11533, 2020. 1
[12] Thomas Gilles, Stefano Sabatini, Dzmitry Tsishkou, Bogdan
Stanciulescu, and Fabien Moutarde. Home: Heatmap output
for future motion estimation. In 2021 IEEE International
Intelligent Transportation Systems Conference (ITSC), pages
500–507. IEEE, 2021. 2
[13] Thomas Gilles, Stefano Sabatini, Dzmitry Tsishkou, Bog-
dan Stanciulescu, and Fabien Moutarde. Gohome: Graph-
oriented heatmap output for future motion estimation.
In
2022 International Conference on Robotics and Automation
(ICRA), pages 9107–9114. IEEE, 2022. 2
[14] Thomas Gilles, Stefano Sabatini, Dzmitry Tsishkou, Bog-
dan Stanciulescu, and Fabien Moutarde. Thomas: Trajectory
heatmap output with learned multi-agent sampling. In Inter-
national Conference on Learning Representations, 2022. 1,
2
[15] Junru Gu, Chen Sun, and Hang Zhao. Densetnt: End-to-end
trajectory prediction from dense goal sets. In Proceedings
of the IEEE/CVF International Conference on Computer Vi-
sion, pages 15303–15312, 2021. 1, 6
[16] Niklas Hanselmann, Katrin Renz, Kashyap Chitta, Apra-
tim Bhattacharyya, and Andreas Geiger. King: Generating
safety-critical driving scenarios for robust imitation via kine-
matics gradients. In European Conference on Computer Vi-
sion, pages 335–352. Springer, 2022. 5
[17] Zhiyu Huang, Haochen Liu, Jingda Wu, and Chen Lv. Con-
ditional predictive behavior planning with inverse reinforce-
ment learning for human-like autonomous driving.
IEEE
Transactions on Intelligent Transportation Systems, 2023. 1,
2
[18] Zhiyu Huang, Haochen Liu, Jingda Wu, and Chen Lv. Dif-
ferentiable integrated motion prediction and planning with
learnable cost function for autonomous driving. IEEE trans-
actions on neural networks and learning systems, 2023. 2, 6,
7, 8
[19] Zhiyu Huang, Chen Lv, Yang Xing, and Jingda Wu. Multi-
modal sensor fusion-based deep neural network for end-to-
end autonomous driving with scene understanding.
IEEE
Sensors Journal, 21(10):11781–11790, 2020. 2
[20] Zhiyu Huang, Xiaoyu Mo, and Chen Lv. Multi-modal mo-
tion prediction with transformer-based neural network for
autonomous driving. In 2022 International Conference on
Robotics and Automation (ICRA), pages 2605–2611. IEEE,
2022. 2
[21] Zhiyu Huang, Xiaoyu Mo, and Chen Lv. Recoat: A deep
learning-based framework for multi-modal motion predic-
tion in autonomous driving application. In 2022 IEEE 25th
International Conference on Intelligent Transportation Sys-
tems (ITSC), pages 988–993. IEEE, 2022. 2
[22] Xiaosong Jia, Li Chen, Penghao Wu, Jia Zeng, Junchi Yan,
Hongyang Li, and Yu Qiao. Towards capturing the tempo-
ral dynamics for trajectory prediction: a coarse-to-fine ap-
proach. In Conference on Robot Learning, pages 910–920.
PMLR, 2023. 1
[23] Xiaosong Jia, Liting Sun, Masayoshi Tomizuka, and Wei
Zhan. Ide-net: Interactive driving event and pattern extrac-
10


## Page 11

tion from human data. IEEE Robotics and Automation Let-
ters, 6(2):3065–3072, 2021. 1
[24] Xiaosong Jia, Liting Sun, Hang Zhao, Masayoshi Tomizuka,
and Wei Zhan. Multi-agent trajectory prediction by combin-
ing egocentric and allocentric views. In Conference on Robot
Learning, pages 1434–1443. PMLR, 2022. 1, 2
[25] Xiaosong Jia, Penghao Wu, Li Chen, Yu Liu, Hongyang Li,
and Junchi Yan. Hdgt: Heterogeneous driving graph trans-
former for multi-agent trajectory prediction via scene encod-
ing. IEEE Transactions on Pattern Analysis and Machine
Intelligence (TPAMI), 2023. 1
[26] Aviral Kumar, Aurick Zhou, George Tucker, and Sergey
Levine.
Conservative q-learning for offline reinforcement
learning. Advances in Neural Information Processing Sys-
tems, 33:1179–1191, 2020. 2, 8
[27] Nan Li, Ilya Kolmanovsky, Anouck Girard, and Yildiray
Yildiz. Game theoretic modeling of vehicle interactions at
unsignalized intersections and application to autonomous ve-
hicle control. In 2018 Annual American Control Conference
(ACC), pages 3215–3220, 2018. 2
[28] Nan Li, Dave W Oyler, Mengxuan Zhang, Yildiray Yildiz,
Ilya Kolmanovsky, and Anouck R Girard. Game theoretic
modeling of driver and vehicle interactions for verification
and validation of autonomous vehicle control systems. IEEE
Transactions on control systems technology, 26(5):1782–
1797, 2017. 2
[29] Jerry Liu, Wenyuan Zeng, Raquel Urtasun, and Ersin Yumer.
Deep structured reactive planning.
In 2021 IEEE Inter-
national Conference on Robotics and Automation (ICRA),
pages 4897–4904. IEEE, 2021. 5
[30] Xiaoyu Mo, Zhiyu Huang, Yang Xing, and Chen Lv.
Multi-agent trajectory prediction with heterogeneous edge-
enhanced graph attention network. IEEE Transactions on
Intelligent Transportation Systems, 2022. 2, 6
[31] Nigamaa Nayakanti, Rami Al-Rfou, Aurick Zhou, Kratarth
Goel, Khaled S Refaat, and Benjamin Sapp.
Wayformer:
Motion forecasting via simple & efficient attention networks.
arXiv preprint arXiv:2207.05844, 2022. 1, 2, 4
[32] Jiquan Ngiam, Vijay Vasudevan, Benjamin Caine, Zheng-
dong Zhang, Hao-Tien Lewis Chiang, Jeffrey Ling, Rebecca
Roelofs, Alex Bewley, Chenxi Liu, Ashish Venugopal, et al.
Scene transformer: A unified architecture for predicting fu-
ture trajectories of multiple agents. In International Confer-
ence on Learning Representations, 2021. 1, 2, 5, 6
[33] Nicholas Rhinehart, Rowan McAllister, and Sergey Levine.
Deep imitative models for flexible inference, planning, and
control. In International Conference on Learning Represen-
tations, 2019. 7
[34] Tim Salzmann, Boris Ivanovic, Punarjay Chakravarty, and
Marco Pavone. Trajectron++: Dynamically-feasible trajec-
tory forecasting with heterogeneous data. In European Con-
ference on Computer Vision, pages 683–700. Springer, 2020.
1, 2
[35] Shaoshuai Shi, Li Jiang, Dengxin Dai, and Bernt Schiele.
Motion transformer with global intention localization and lo-
cal movement refinement. Advances in Neural Information
Processing Systems, 2022. 1, 2, 4, 6, 7
[36] Haoran Song, Wenchao Ding, Yuxuan Chen, Shaojie Shen,
Michael Yu Wang, and Qifeng Chen.
Pip:
Planning-
informed trajectory prediction for autonomous driving. In
European Conference on Computer Vision, pages 598–614.
Springer, 2020. 1, 2
[37] Qiao Sun, Xin Huang, Junru Gu, Brian C Williams, and
Hang Zhao. M2i: From factored marginal trajectory pre-
diction to interactive prediction.
In Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern
Recognition, pages 6543–6552, 2022. 1, 6
[38] Qiao Sun, Xin Huang, Brian C Williams, and Hang Zhao.
Intersim: Interactive traffic simulation via explicit relation
modeling. In 2022 IEEE/RSJ International Conference on
Intelligent Robots and Systems (IROS), pages 11416–11423.
IEEE, 2022. 2
[39] Ekaterina Tolstaya, Reza Mahjourian, Carlton Downey,
Balakrishnan Vadarajan, Benjamin Sapp, and Dragomir
Anguelov. Identifying driver interactions via conditional be-
havior prediction. In 2021 IEEE International Conference on
Robotics and Automation (ICRA), pages 3473–3479. IEEE,
2021. 1
[40] Balakrishnan Varadarajan, Ahmed Hefny, Avikalp Srivas-
tava, Khaled S Refaat, Nigamaa Nayakanti, Andre Cornman,
Kan Chen, Bertrand Douillard, Chi Pang Lam, Dragomir
Anguelov, et al.
Multipath++: Efficient information fu-
sion and trajectory aggregation for behavior prediction. In
2022 International Conference on Robotics and Automation
(ICRA), pages 7814–7821. IEEE, 2022. 1, 5, 7
[41] Wenshuo Wang, Letian Wang, Chengyuan Zhang, Changliu
Liu, Lijun Sun, et al.
Social interactions for autonomous
driving:
A review and perspectives.
Foundations and
Trends® in Robotics, 10(3-4):198–376, 2022. 2
[42] James R Wright and Kevin Leyton-Brown. Beyond equi-
librium: Predicting human behavior in normal-form games.
In Twenty-Fourth AAAI Conference on Artificial Intelligence,
2010. 2
[43] David Wu and Yunnan Wu. Air2 for interaction prediction.
arXiv preprint arXiv:2111.08184, 2021. 6
[44] Danfei Xu, Yuxiao Chen, Boris Ivanovic, and Marco Pavone.
Bits:
Bi-level imitation for traffic simulation.
In 2023
IEEE International Conference on Robotics and Automation
(ICRA), pages 2929–2936. IEEE, 2023. 2
[45] Ye Yuan, Xinshuo Weng, Yanglan Ou, and Kris M Kitani.
Agentformer: Agent-aware transformers for socio-temporal
multi-agent forecasting. In Proceedings of the IEEE/CVF
International Conference on Computer Vision, pages 9813–
9823, 2021. 1
[46] Wenyuan Zeng, Wenjie Luo, Simon Suo, Abbas Sadat, Bin
Yang, Sergio Casas, and Raquel Urtasun.
End-to-end in-
terpretable neural motion planner.
In Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern
Recognition, pages 8660–8669, 2019. 2
[47] Zikang Zhou, Luyao Ye, Jianping Wang, Kui Wu, and Ke-
jie Lu. Hivt: Hierarchical vector transformer for multi-agent
motion prediction. In Proceedings of the IEEE/CVF Con-
ference on Computer Vision and Pattern Recognition, pages
8823–8833, 2022. 1
11


## Page 12

GameFormer: Game-theoretic Modeling and Learning of Transformer-based
Interactive Prediction and Planning for Autonomous Driving
Supplementary Material
A. Experiment Details
A.1. Prediction-oriented Model
Model inputs. In each scene, one of the two interacting
agents is designated as the focal agent, with its current state
serving as the origin of the coordinate system. We consider
10 surrounding agents closest to a target agent as the back-
ground agents, and therefore, there are two target agents to
predict and up to 20 different background agents in a scene.
The current and historical states of each agent are retrieved
for the last one second at a sampling rate of 10Hz, result-
ing in a tensor with a shape of (22 × 11) for each agent.
The state at each timestep includes the agent’s position
(x, y), heading angle (θ), velocity (vx, vy), bounding box
size (L, W, H), and one-hot category encoding of the agent
(totally three types). All historical states for each agent are
aggregated into a fixed-shape tensor of (22×11×11), with
missing agent states padded as zeros, to form the input ten-
sor of historical agent states.
For each target agent, up to 6 drivable lanes (each extend-
ing 100 meters) that the agent may take are identified using
depth-first search on the road graph, along with 4 nearby
crosswalks as the local map context, with each map vector
containing 100 waypoints. The features of a waypoint in a
drivable lane include the position and heading angles of the
centerline, left boundary, and right boundary, speed limit, as
well as discrete attributes such as the lane type, traffic light
state, and controlled by a stop sign. The features of a way-
point in the crosswalk polyline only encompass position and
heading angle. Therefore, the local map context for a tar-
get agent comprises two tensors: drivable lanes with shape
(6 × 100 × 15) and crosswalks with shape (4 × 100 × 3).
Encoder structure. In the encoder part, we utilize two
separate LSTMs to encode the historical states of the target
and background agents, respectively, resulting in a tensor
with shape (22 × 256) that encompasses all agents’ histor-
ical state sequences. The local map context encoder con-
sists of a lane encoder for processing the drivable lanes and
a crosswalk encoder for the crosswalk polylines. The lane
encoder employs MLPs to encode numeric features and em-
bedding layers to encode discrete features, outputting a ten-
sor of encoded lane vectors with shape (2×6×100×256),
while the crosswalk encoder uses an MLP to encode nu-
meric features, resulting in a tensor of crosswalk vectors
with shape (2 × 4 × 100 × 256). Subsequently, we utilize a
max-pooling layer (with a step size of 10) to aggregate the
waypoints from a drivable lane in the encoded lane tensor,
yielding a tensor with shape (2 × 6 × 10 × 256) that is re-
shaped to (2 × 60 × 256). Similarly, the encoded crosswalk
tensor is processed using a max-pooling layer with a step
size of 20 to obtain a tensor with shape (2 × 20 × 256).
These two tensors are concatenated to produce an encoded
local map context tensor with shape (2 × 80 × 256). For
each target agent, we concatenate its local map context ten-
sor with the historical state tensor of all agents to obtain a
scene context tensor with dimensions of (102 × 256), and
we use self-attention Transformer encoder layers to extract
the relationships among the elements in the scene. It is im-
portant to note that invalid positions in the scene context
tensor are masked from attention calculations.
Decoder structure. For the M = 6 joint prediction
model, we employ the learnable latent modality embedding
with a shape of (2 × 6 × 256). For each agent, the query
(6 × 256) in the level-0 decoder is obtained by summing
up the encoding of the target agent’s history and its corre-
sponding latent modality embedding; the value and key are
derived from the scene context by the encoder. The level-0
decoder generates the multi-modal future trajectories of the
target agent with x and y coordinates using an MLP from
the attention output. The scores of each trajectory are de-
coded by another MLP with a shape of (6 × 1). In a level-
k decoder, we use a shared future encoder across different
layers, which includes an MLP and a max-pooling layer, to
encode the future trajectories from the previous level into
a tensor with a shape of (6 × 256). Next, we employ the
trajectory scores to average-pool the encoded trajectories,
which results in the encoded future of the agent. The en-
coded futures of the two target agents are then fed into a
self-attention Transformer layer to model their future inter-
action. Finally, the output of the Transformer layer is ap-
pended to the scene context obtained from the encoder.
For the M = 64 marginal prediction model, we use a set
of 64 fixed intention points that are encoded with MLPs to
create the modality embedding with shape (2 × 64 × 256).
This modality embedding serves as the query input for the
level-0 decoder.
The fixed intention points are obtained
through the K-means method from the training dataset. For
each scene, the intention points for the two target agents are
normalized based on the focal agent’s coordinate system.
The other components of the decoder are identical to those
used in the joint prediction model.
Training. In the training dataset, each scene contains
several agent tracks to predict, and we consider each track
sequentially as the focal agent, while the closest track to
12


## Page 13

the focal agent is chosen as the interacting agent. The task
is to predict six possible joint future trajectories of these
two agents. We employ only imitation loss at each level to
improve the prediction accuracy and training efficiency.
In the joint prediction model, we aim to predict the joint
and scene-level future trajectories of the two agents. There-
fore, we backpropagate the loss through the joint future
trajectories of the two agents that most closely match the
ground truth (i.e., have the least sum of displacement er-
rors). In the marginal prediction model, we backpropagate
the imitation loss to the individual agent through the posi-
tive GMM component that corresponds to the closest inten-
tion point to the endpoint of the ground-truth trajectory.
Our models are trained for 30 epochs using the AdamW
optimizer with a weight decay of 0.01. The learning rate
starts with 1e-4 and decays by a factor of 0.5 every 3 epochs
after 15 epochs. We also clip the gradient norm of the net-
work parameters with the max norm of the gradients as 5.
We train the models using 4 NVIDIA Tesla V100 GPUs,
with a batch size of 64 per GPU.
Testing. The testing dataset has three types of agents:
vehicle, pedestrian, and cyclist. For the vehicle-vehicle in-
teraction, we randomly select one of the two vehicles as
the focal agent. For other types of interaction pairs (e.g.,
cyclist-vehicle and pedestrian-vehicle), we consider the cy-
clist or pedestrian as the focal agent. For the marginal pre-
diction model, we employ the Expectation-Maximization
(EM) method to aggregate trajectories for each agent.
Specifically, we use the EM method to obtain 6 marginal
trajectories (along with their probabilities) from the 64 tra-
jectories predicted for each agent. Then, we consider the
top 6 joint predictions from the 36 possible combinations of
the two agents, where the confidence of each combination
is the product of the marginal probabilities.
A.2. Planning-oriented Model
Model inputs. In each scene, we consider the AV and 10
surrounding agents to perform planning for the AV and pre-
diction for other agents. The AV’s current state is the origin
of the local coordinate system. The historical states of all
agents in the past two seconds are extracted; for each agent,
we find its nearby 6 drivable lanes and 4 crosswalks. Addi-
tionally, we extract the AV’s traversed lane waypoints from
its ground truth future trajectory and use a cubic spline to
interpolate these waypoints to generate the AV’s reference
route. The reference route extends 100 meters ahead of the
AV and contains 1000 waypoints with 0.1 meters intervals.
It is represented as a tensor with shape (1000 × 5). The ref-
erence route tensor also contains information on the speed
limit and stop points in addition to positions and headings.
Model structure. For each agent, its scene context ten-
sor is created as a concatenation of all agents’ historical
states and encoded local map elements, resulting in a ten-
sor of shape (91 × 256). In the decoding stage, a learn-
able modality embedding of size (11 × 6 × 256) and the
agent’s historical encoding are used as input to the level-0
decoder, which outputs six possible trajectories along with
corresponding scores. In the level-k decoder, the future en-
codings of all agents are obtained through a self-attention
module of size (11 × 256), and are concatenated with the
scene context tensor from the encoder. This concatenation
generates an updated scene context tensor with a shape of
(102 × 256). When decoding an agent’s future trajectory
at the current level, the future encoding of that agent in the
scene context tensor is masked to avoid using its previously
predicted future information.
Training.
In data processing, we filter those scenes
where the AV’s moving distance is less than 5 meters (e.g.,
when stopping at a red light). Similarly, we perform joint
future prediction and calculate the imitation loss through
the joint future that is closest to the ground truth.
The
weights for the imitation loss and interaction loss are set
to w1 = 1, w2 = 0.1. Our model is trained for 20 epochs
using the AdamW optimizer with a weight decay of 0.01.
The learning rate is initialized to 1e-4 and decreases by a
factor of 0.5 every 2 epochs after the 10th epoch. We train
the model using an NVIDIA RTX 3080 GPU, with a batch
size of 32.
Testing. The testing scenarios are extracted from the
WOMD, wherein the ego agent shows dynamic driving be-
haviors1. In open-loop testing, we check collisions between
the AV’s planned trajectory and other agents’ ground-truth
future trajectories, and we count a miss if the distance be-
tween AV’s planned state at the final step and the ground-
truth state is larger than 4.5 meters. The planning errors and
prediction errors are calculated according to the most-likely
trajectories scored by the model. In closed-loop testing, the
AV plans a trajectory at every timestep with an interval of
0.1 seconds and executes the first step of the plan.
A.3. Baseline Methods
To compare model performance, we introduce the fol-
lowing learning-based planning baselines.
Vanilla Imitation Learning (IL): A simplified version
of our model that directly outputs the planned trajectory of
the AV without explicitly reasoning other agents’ future tra-
jectories. The plan is only a single-modal trajectory. The
original encoder part of our model is utilized, but only one
decoder layer with the ego agent’s historical encoding as the
query is used to decode the AV’s plan.
Deep Imitative Model (DIM): A probabilistic planning
method that aims to generate expert-like future trajectories
q (S1:T |ϕ) = QT
t=1 q (St|S1:t−1, ϕ) given the AV’s obser-
1https://github.com/smarts-project/smarts-
project.offline-datasets/blob/master/waymo_
candid_list.csv
13


## Page 14

vations ϕ. We follow the original open-source DIM imple-
mentation and use the rasterized scene image R200×200×3
and the AV’s historical states R11×5 as the observation. We
use a CNN to encode the scene image and an RNN to en-
code the agent’s historical states. The AV’s future state is
decoded (as a multivariate Gaussian distribution) in an au-
toregressive manner.
In testing, DIM requires a specific
goal G to direct the agent to the goal, and a gradient-based
planner maximizes the learned imitation prior log q (S|ϕ)
and the test-time goal likelihood log p(G|S, ϕ).
Robust
Imitative
Planning
(RIP):
An
epistemic
uncertainty-aware planning method that is developed upon
DIM and shows good performance in conducting robust
planning in out-of-distribution (OOD) scenarios. Specifi-
cally, we employ the original open-source implementation
and choose the worst-case model that has the worst likeli-
hood mind log q (S1:T |ϕ) among d = 6 trained DIM mod-
els and improve it with a gradient-based planner.
Conservative Q-Learning (CQL): A widely-used of-
fline reinforcement learning algorithm that learns to make
decisions from offline datasets. We implement the CQL
method with the d3rlpy offline RL library2. The RL agent
takes the same state inputs as the DIM method and outputs
the target pose of the next step (∆x, ∆y, ∆θ) relative to the
agent’s current position. The reward function is the distance
traveled per step plus an extra reward for reaching the goal,
i.e., rt = ∆dt +10×1 (d(st, sgoal) < 1). Since the dataset
only contains perfect driving data, no collision penalty is
included in the reward function.
Differentiable Integrated Prediction and Planning
(DIPP): A joint prediction and planning method that uses a
differentiable motion planner to optimize the trajectory ac-
cording to the prediction result. We adopt the original open-
source implementation and the same state input setting. We
increase the historical horizon to 20 and the number of pre-
diction modalities from 3 to 6. In open-loop testing, we uti-
lize the results from the DIPP prediction network without
trajectory planning (refinement).
MultiPath++:
A high-performing motion prediction
model that is based on the context-aware fusion of hetero-
geneous scene elements and learnable latent anchor embed-
dings. We utilize the open-source implementation of Mul-
tiPath++3 that achieved state-of-the-art prediction accuracy
on the WOMD motion prediction benchmark. We train the
model to predict 6 possible trajectories and corresponding
scores for the ego agent using the same dataset. In open-
loop testing, only the most-likely trajectory will be used as
the plan for the AV.
Motion Transformer (MTR)-e2e: A state-of-the-art
prediction model that occupies the first place on the WOMD
2https://github.com/takuseno/d3rlpy
3https://github.com/stepankonev/waymo-motion-
prediction-challenge-2022-multipath-plus-plus
motion prediction leaderboard.
We follow the original
open-source implementation of the context encoder and
MTR decoder. However, we modified the decoder to use
an end-to-end variant of MTR that is better suited for the
open-loop planning task. Specifically, only 6 learnable mo-
tion query pairs are used to decode 6 possible trajectories
and scores. The same dataset is used to train the MTR-e2e
model, and the data is processed according to the MTR con-
text inputs.
A.4. Refinement Planner
Inverse dynamic model. To convert the initial planned
trajectory to control actions {at, δt} (i.e., acceleration and
yaw rate), we utilize the following inverse dynamic model.
  \ b eg i n 
{s p l it} \ Ph i
 ^
{
-1 } : v_t &= 
\fr
a
c { \Del t a 
p}
{
\D e lta t } 
= 
\frac {\parallel p_{t+1} - p_{t} \parallel }{\Delta t}, \\ \theta _t &= \arctan \frac {\Delta p_y}{\Delta p_x}, \\ a_t &= \frac {v_{t+1} - v_{t}}{\Delta t}, \\ \delta _t &= \frac {\theta _{t+1} - \theta _{t}}{\Delta t}, \end {split} 
(S1)
where pt is a predicted coordinate in the trajectory, and ∆t
is the time interval.
Dynamic model. To derive the coordinate and heading
{pxt, pyt, θ} from control actions, we adopt the following
differentiable dynamic model.
  \beg i n {s p lit
} \P h i : v _{t
+1} & =  a _t \Del t a t 
+ v_t ,  \ \ \ thet a  _{t+1} &= \delta _t \Delta t + \theta _t, \\ {p_x}_{t+1} &= v_t \cos \theta _t {\Delta t} + {p_x}_{t}, \\ {p_y}_{t+1} &= v_t \sin \theta _t {\Delta t} + {p_y}_{t}. \end {split} 
(S2)
Motion planner. We use a differentiable motion plan-
ner proposed in DIPP to plan the trajectory for the AV. The
planner takes as input the initial control action sequence de-
rived from the planned trajectory given by our model. We
formulate each planning cost term ci as a squared vector-
valued residual, and the motion planner aims to solve the
following nonlinear least squares problem:
  \ mat hbf
 
{
u
}
^
{ *} = \a rg \min _\mathbf {u} \frac {1}{2} \sum _i \parallel \omega _i c_i(\mathbf {u}) \parallel ^2, 
(S3)
where u is the sequence of control actions, and ωi is the
weight for cost ci.
We consider a variety of cost terms as proposed in DIPP,
including travel speed, control effort (acceleration and yaw
rate), ride comfort (jerk and change of yaw rate), distance
to the reference line, heading difference, as well as the cost
of violating traffic light. Most importantly, the safety cost
takes all other agents’ predicted states into consideration
and avoids collision with them, as illustrated in DIPP.
14


## Page 15

We use the Gauss-Newton method to solve the optimiza-
tion problem. The maximum number of iterations is 30,
and the step size is 0.3. We use the best solution during the
iteration process as the final plan to execute.
Learning cost function weights. Since the motion plan-
ner is differentiable, we can learn the weights of the cost
terms by differentiating through the optimizer. We use the
imitation learning loss below (average displacement error
and final displacement error) to learn the cost weights, as
well as minimize the sum of cost values. We set the maxi-
mum number of iterations to 3 and the step size to 0.5 in the
motion planner. We use the Adam optimizer with a learning
rate of 5e-4 to train the cost function weights; the batch size
is 32 and the total number of training steps is 10,000.
  \m
a
t
hcal { L} = \ lambda _ 1 \su m  _
t
 
||\hat s_t - s_t||^2 + \lambda _2 ||\hat s_T - s_T||^2 + \lambda _3 \sum _i ||c_i||^2, 
(S4)
where λ1 = 1, λ2 = 0.5, λ3 = 0.001 are the weights.
A.5. GameFormer Planner
To validate our model’s performance on the nuPlan
benchmark4, we have developed a comprehensive planning
framework to handle the realistic driving scenarios in nu-
Plan. The planning process comprises the following steps:
1) feature processing: relevant data from the observation
buffer and map API undergoes preprocessing to extract in-
put features for the prediction model; 2) path planning: can-
didate route paths for the ego vehicle are computed, from
which the optimal path is selected as the reference path; 3)
model query: the prediction model is queried to generate
an initial plan for the ego vehicle and predict the trajecto-
ries of surrounding agents; and 4) trajectory refinement: a
nonlinear optimizer is employed to refine the ego vehicle’s
trajectory on the reference path and produce the final plan.
For computational efficiency, we use a compact version of
the GameFormer model, configuring it with 3 encoding lay-
ers and 3 decoding layers (1 initial decoding layer and 2
interaction decoding layers). Additionally, we introduce an
extra decoding layer after the last interaction decoding layer
to separately generate the ego vehicle’s plan. The ego plan
is then projected onto the reference path as an initialization
of the refinement planner. The output of the GameFormer
model consists of multimodal trajectories for the surround-
ing agents. For each neighboring agent, we select the trajec-
tory with the highest probability and project it onto the ref-
erence path using the Frenet transformation, subsequently
calculating spatiotemporal path occupancy. A comprehen-
sive description of the planning framework can be found in
this dedicated report5.
4https://eval.ai/web/challenges/challenge-
page/1856/overview
5https://opendrivelab.com/e2ead/AD23Challenge/
Track_4_AID.pdf
B. Additional Quantitative Results
B.1. Interaction Prediction
Table S1 displays the per-category performance of our
models on the WOMD interaction prediction benchmark,
in comparison with the MTR model.
The GameFormer
joint prediction model exhibits the lowest minFDE across
all object categories, indicating the advantages of our model
and joint training of interaction patterns.
Our Game-
Former model surpasses MTR in the cyclist category and
achieves comparable performance to MTR in other cate-
gories, though with a much simpler structure than MTR.
Table S1. Per-class performance of interaction prediction on the
WOMD interaction prediction benchmark
Class
Model
minADE (↓)
minFDE (↓)
Miss rate (↓)
mAP (↑)
Vehicle
MTR
0.9793
2.2157
0.3833
0.2977
GF (J)
0.9822
2.0745
0.3785
0.1856
GF (M)
1.0499
2.4044
0.4321
0.2469
Pedestrian
MTR
0.7098
1.5835
0.3973
0.2033
GF (J)
0.7279
1.4894
0.4272
0.1505
GF (M)
0.7978
1.8195
0.4713
0.1962
Cyclist
MTR
1.0652
2.3908
0.5428
0.1102
GF (J)
1.0383
2.2480
0.5536
0.0768
GF (M)
1.0686
2.4199
0.5765
0.1338
B.2. nuPlan Benchmark
Table S2 presents a performance comparison between
our planner and the DIPP planner. For the benchmark eval-
uation, we replace the prediction model in the proposed
planning framework with the DIPP model and other parts
of the framework remain the same. The results show that
the GameFormer model still outperforms the DIPP model,
as a result of better initial plans for the ego agent and pre-
diction results for other agents.
Table S2. Comparison with DIPP planner on the nuPlan testing
benchmark
Method
Overall
OL
CL non-reactive
CL reactivate
DIPP
0.7950
0.8141
0.7853
0.7857
Ours
0.8288
0.8400
0.8087
0.8376
B.3. Abalation Study
Effects of decoding levels on closed-loop planning.
We investigate the influence of decoding levels on closed-
loop planning performance in selected WOMD scenarios,
using the success rate (without collision) as the main metric.
We also report the inference time of the prediction network
(without the refine motion planner) in closed-loop planning,
which is executed on an NVIDIA RTX 3080 GPU. The re-
sults in Table S3 reveal that increasing the decoding lay-
ers could potentially lead to a higher success rate, and even
adding a single layer of interaction modeling can bring sig-
nificant improvement compared to level-0. In closed-loop
15


## Page 16

testing, the success rate reaches a plateau at a decoding
level of 2, while the computation time continues to increase.
Therefore, using two reasoning levels in our model may of-
fer a favorable balance between performance and efficiency
in practical applications.
Table S3. Effects of decoding levels on closed-loop planning
Level
Success rate (%)
Inference time (ms)
0
89.5
31.8
1
92.25
44.1
2
94
56.7
3
94.5
66.5
4
94.5
79.2
C. Additional Qualitative Results
C.1. Interaction Prediction
Fig.
S1 presents additional qualitative results of our
GameFormer framework in the interaction prediction task,
showcasing the ability of our method to handle a variety of
interaction pairs and complex urban driving scenarios.
C.2. Level-k Prediction
Fig. S2 illustrates the most-likely joint trajectories of
the target agents at different interaction levels. The results
demonstrate that our proposed model is capable of refining
the prediction results in the iterated interaction process. At
level-0, the predictions for target agents appear more inde-
pendent, potentially leading to trajectory collisions. How-
ever, through iterative refinement, our model can generate
consistent and human-like trajectories at a higher interac-
tion level.
C.3. Open-loop Planning
Fig.
S3 provides additional qualitative results of our
model in the open-loop planning task, which show the abil-
ity of our model to jointly plan the trajectory of the AV and
predict the behaviors of neighboring agents.
C.4. Closed-loop Planning
We visualize the closed-loop planning performance of
our method through videos available on the project website,
including interactive urban driving scenarios from both the
WOMD and nuPlan datasets.
16


## Page 17

t+0s
t+8s
low
high
Figure S1. Additional qualitative results of interaction prediction. The red boxes are interacting agents to predict, and the magenta boxes
are background neighboring agents. Six joint trajectories of the two interacting agents are predicted.
17


## Page 18

t+0s
t+8s
Scene 1
Scene 2
Level-0
Level-2
Level-4
Figure S2. Prediction results of the two interacting agents at different reasoning levels. Only the most-likely joint trajectories of the target
agents are displayed for clarity.
t+0s
t+0s
t+5s
t+5s
Figure S3. Additional qualitative results of open-loop planning. The red box is the AV and the magenta boxes are its neighboring agents;
the red trajectory is the plan of the AV and the blue ones are the predictions of neighboring agents.
18

