# DriveDreamer: Towards Real-world-driven World Models for Autonomous Driving

**Source**: arXiv:2309.09777

**Type**: Academic Paper

---

## Page 1

DriveDreamer: Towards Real-world-driven World Models
for Autonomous Driving
Xiaofeng Wang*1 Zheng Zhu*1 Guan Huang1,2 Xinze Chen1 Jiagang Zhu1 Jiwen Lu2
1GigaAI
2Tsinghua University
Project Page: https://drivedreamer.github.io
xd
xd
DriveDreamer
xd
DriveDreamer
Different Driving Actions
Different Text Prompts
“Sunny”“Rainy”“Night”
Initial Condition
DriveDreamer
Driving Video Generation with Traffic Condition and Different Text Prompts
Future Driving Video Generation with Action Interaction
Future Driving Action Generation
Initial Driving Actions
Initial Conditions
Initial Condition
Figure 1. DriveDreamer demonstrates a comprehensive understanding of driving scenarios. It excels in controllable driving video gener-
ation, aligning seamlessly with text prompts and structured traffic constraints. DriveDreamer can also interact with the driving scene and
predict different future driving videos, based on input actions. Furthermore, DriveDreamer extends its utility to anticipate future actions.
Abstract
World models, especially in autonomous driving, are
trending and drawing extensive attention due to their ca-
pacity for comprehending driving environments. The estab-
lished world model holds immense potential for the gen-
eration of high-quality driving videos, and driving poli-
cies for safe maneuvering. However, a critical limitation
in relevant research lies in its predominant focus on gam-
ing environments or simulated settings, thereby lacking the
representation of real-world driving scenarios. Therefore,
we introduce DriveDreamer, a pioneering world model en-
tirely derived from real-world driving scenarios. Regarding
that modeling the world in intricate driving scenes entails
an overwhelming search space, we propose harnessing the
1
arXiv:2309.09777v2  [cs.CV]  27 Nov 2023


## Page 2

powerful diffusion model to construct a comprehensive rep-
resentation of the complex environment. Furthermore, we
introduce a two-stage training pipeline. In the initial phase,
DriveDreamer acquires a deep understanding of structured
traffic constraints, while the subsequent stage equips it with
the ability to anticipate future states. The proposed Drive-
Dreamer is the first world model established from real-
world driving scenarios. We instantiate DriveDreamer on
the challenging nuScenes benchmark, and extensive exper-
iments verify that DriveDreamer empowers precise, con-
trollable video generation that faithfully captures the struc-
tural constraints of real-world traffic scenarios. Addition-
ally, DriveDreamer enables the generation of realistic and
reasonable driving policies, opening avenues for interac-
tion and practical applications.
1. Introduction
Spurred by insights from AGI (Artificial General Intelli-
gence) and the principles of embodied AI, a profound trans-
formation in autonomous driving is underway. Autonomous
vehicles rely on sophisticated systems that engage with and
comprehend the real driving world. At the heart of this evo-
lution is the integration of world models [15,17–19]. World
models hold great promise for generating diverse and real-
istic driving videos, encompassing even long-tail scenarios,
which can be utilized to train various driving perception ap-
proaches. Furthermore, the predictive capabilities in world
models facilitate end-to-end driving, ushering in a new era
of autonomous driving experiences.
Deriving
latent
dynamics
of
world
models
from
visual signals was initially introduced in video predic-
tion [8, 11, 19].
By extrapolating from observed visual
sequences, video prediction methods can infer future states
of the environment, effectively modeling how objects and
entities within a scene will evolve over time.
However,
modeling the intricate driving scenarios in pixel space is
challenging due to the large sampling space [5, 7].
To
alleviate this problem, recent research endeavors have
sought innovative strategies to enhance sampling efficiency.
ISO-Dream [52] explicitly disentangles visual dynamics
into controllable and uncontrollable states.
MILE [29]
strategically
incorporates
world
modeling
within
the
Bird’s Eye View (BEV) semantic segmentation space,
complementing world modeling with imitation learning.
SEM2 [13] further extends the Dreamer framework into
BEV segmentation maps, utilizing Reinforce Learning
(RL) for training. Despite the progress witnessed in world
models, a critical limitation in relevant research lies in its
predominant focus on simulation environments.
In this paper, we propose DriveDreamer, which pioneers
the construction of comprehensive world models from real
driving videos and human driver behaviors. Considering the
intricate nature of modeling real-world driving scenes, we
introduce the Autonomous-driving Diffusion Model (Auto-
DM), which empowers the ability to create a comprehen-
sive representation of the complex driving environment. We
propose a two-stage training pipeline.
In the first stage,
we train Auto-DM by incorporating traffic structural infor-
mation as intermediate conditions, which significantly en-
hances sampling efficiency. Consequently, Auto-DM ex-
hibits remarkable capabilities in comprehending real-world
driving scenes, particularly concerning the dynamic fore-
ground objects and the static background. In the second-
stage training, we establish the world model through video
prediction. Specifically, driving actions are employed to it-
eratively update future traffic structural conditions, which
enables DriveDreamer to anticipate variations in the driving
environment based on different driving strategies. More-
over, DriveDreamer extends its predictive prowess to fore-
see forthcoming driving policies, drawing from historical
observations and Auto-DM features. Thus creating a exe-
cutable, and predictable driving world model.
The main contributions of this paper can be summa-
rized as follows: (1) We introduce DriveDreamer, which
is the first world model derived from real-world driving
scenarios. DriveDreamer can jointly enable the generation
of high-quality driving videos and reasonable driving poli-
cies. (2) To enhance the comprehension of real-world driv-
ing scenes and expedite the world model convergence, we
introduce the Autonomous-driving Diffusion Model and a
two-stage training pipeline. The first-stage training enables
the comprehension of traffic structural information, and the
second-stage video prediction training empowers the pre-
dictive capacity. (3) DriveDreamer can controllably gener-
ate driving scene videos that are highly aligned with traffic
constraints (see Fig. 1), enhancing the training of driving
perception methods (e.g., 3D detection). Besides, Drive-
Dreamer can generate future driving policies based on his-
torical observations and Auto-DM features. Notably, Drive-
Dreamer achieves promising planning results in open-loop
assessments on the nuScenes dataset.
2. Related Work
2.1. Diffusion Model
Diffusion models represent a family of probabilistic gen-
erative models that progressively introduce noise to data
and subsequently learn to reverse this process for the pur-
pose of generating samples [73]. These models have re-
cently garnered significant attention due to their exceptional
performance in various applications, setting new bench-
marks in image synthesis [1, 14, 49, 55, 57], video gener-
ation [21, 23, 35, 60, 67, 74], and 3D content generation
[6, 43, 53, 69]. To enhance the controllable generation ca-
pability, ControlNet [76], GLIGEN [42], T2I-Adapter [48]
2


## Page 3

and Composer [32] have been introduced to utilize various
control inputs, including depth maps, segmentation maps,
canny edges, and sketches. Concurrently, BEVControl [72],
MagicDrive [12] and DrivingDiffuson [41] incorporate lay-
out conditions to enhance image generation. The funda-
mental essence of diffusion-based generative models lies in
their capacity to comprehend and understand the intricacies
of the world. Harnessing the power of these diffusion mod-
els, DriveDreamer seeks to comprehend the complex realm
of autonomous-driving scenarios.
2.2. Video Generation
Video generation and video prediction are effective
approaches to understanding the visual world.
In the
realm of video generation, several standard architectures
have been employed, including Variational Autoencoders
(VAEs) [8,28], auto-regressive models [34,56,61,70], flow-
based models [40], and Generative Adversarial Networks
(GANs) [46, 58, 62, 65]. Recently, the burgeoning diffu-
sion models [9, 24, 25, 49, 50, 57] have also been extended
to the domain of video generation. Video diffusion mod-
els [21, 23, 35, 60, 67, 74] exhibit higher-quality video gen-
eration capabilities, producing realistic frames and transi-
tions between frames while offering enhanced controllabil-
ity.
They accommodate various input control conditions
such as text, canny, sketch, semantic maps, and depth maps.
Video prediction models represent a specialized form
of video generation models, sharing numerous similari-
ties. In particular, video prediction involves anticipating
future video changes based on historical video observa-
tions [8, 11, 19, 27, 64]. DriveGAN [36] establishes asso-
ciations between driving actions and pixels, predicting fu-
ture driving videos by specifying future driving policies. In
contrast, DriveDreamer incorporates structured traffic con-
ditions, text prompts, and driving actions as inputs, empow-
ering precise, realistic video and action generation that are
faithfully aligned with real-world driving scenarios.
2.3. World Models
World models have been extensively explored in model-
based imitation learning, demonstrating remarkable suc-
cess in various applications [15–20, 37, 44, 59, 71]. These
approaches typically leverage Variational Autoencoders
(VAE) [39] and Long Short-Term Memory (LSTM) [26]
to model transition dynamics and rendering functionality.
World methods target at establishing dynamic models of en-
vironments, enabling agents to be predictive of the future.
This aspect is of paramount importance in autonomous driv-
ing, where precise predictions about the future are essential
for safe maneuvering. However, constructing world mod-
els in autonomous driving presents unique challenges, pri-
marily due to the high sample complexity inherent in real-
world driving tasks [5]. To address these problems, ISO-
DriveDreamer
First-stage Training
Second-stage Training
Single Condition
Sequential Conditions
DriveDreamer
Image Generation
Video Generation
Step 1
Step 2
Image Supervision
Video Supervision
Single Condition
Sequential Driving 
Actions
DriveDreamer
Future Driving 
Actions
Future Video 
Generation
Video Supervision
Action Supervision
( ActionFormer )
( Auto-DM )
Figure 2. Two-stage training pipeline of DriveDreamer.
Dream [52] introduces an explicit disentanglement of visual
dynamics into controllable and uncontrollable states. MILE
[29] strategically incorporates world modeling within the
BEV semantic segmentation space, enhancing world mod-
eling through imitation learning. SEM2 [13] extends the
Dreamer framework into BEV segmentation maps, em-
ploying reinforcement learning for training.
Despite the
progress witnessed in world models, a critical limitation in
relevant research lies in its predominant focus on simulation
environments. The transition to real-world driving scenar-
ios remains an under-explored frontier.
3. DriveDreamer
The overall framework of DriveDreamer is depicted in
Fig 3.
The framework begins with an initial reference
frame I0 and its corresponding road structural informa-
tion (i.e., HDMap H0 and 3D box B0). Within this con-
text, DriveDreamer leverages the proposed ActionFormer
to predict forthcoming road structural features in the latent
space.
These predicted features serve as conditions and
are provided to Auto-DM, which generates future driving
videos. Simultaneously, the utilization of text prompts al-
lows for dynamic adjustments to the driving scenario style
(e.g., weather and time of the day).
Moreover, Drive-
Dreamer incorporates historical action information and the
multi-scale latent features extracted from Auto-DM, which
are combined to generate reasonable future driving actions.
In essence, DriveDreamer offers a comprehensive frame-
work that seamlessly integrates multi-modal inputs to gen-
erate future driving videos and driving policies, thereby ad-
vancing the capabilities of autonomous-driving systems.
Regarding the extensive search space of establishing
world models in real-world driving scenarios, we introduce
a two-stage training strategy for DriveDreamer. This strat-
egy is designed to significantly enhance sampling efficiency
and expedite model convergence. The two-stage training is
3


## Page 4

Text
"A realistic
driving scene "
HDMap
3D Box
Reference Image
ActionFormer
Actions
Video
Decoder
Action
Decoder
Enc
Enc
Enc
CLIP
CLIP Embedding
Enc
Reference Style Embedding
Autonomous-driving
Diffusion Model
Denoising
Condition Input
Future Driving Actions
Output
Temporal-attention
Cross-attention
Gated Self-attention
Cross-Attention
Self-Attention
Cross-Attention
Self-Attention
Cross-Attention
Self-Attention
Future Driving Videos
Figure 3. Overall framework of DriveDreamer. The framework initiates with reference frame I0 and road structural information (i.e.,
HDMap H0 and 3D box B0). DriveDreamer employs the ActionFormer to predict future road structural features, which serve as conditions
provided to Auto-DM, generating future driving videos ˆIN−1
i=0 . Additionally, text prompts enable dynamic scenario style adjustments. The
model integrates past driving actions and multi-scale features from Auto-DM to generate plausible future driving actions ˆAN+M
i=N .
illustrated in Fig. 2. There are two steps in the first-stage
training. Step 1 involves utilizing the single-frame struc-
tured condition, which guides DriveDreamer to generate
driving scene image, facilitating its comprehension of struc-
tural traffic constraints. Step 2 extends its understanding
into video generation. The second-stage training enables
DriveDreamer to interact with the environment and predict
future states effectively. This phase takes an initial frame
image along with its corresponding structured information
as input. Simultaneously, sequential driving actions are pro-
vided, with the model expected to generate future driving
videos and future driving actions. In the following sections,
we delve into the specifics of the model architecture and
training pipelines.
3.1. First-stage Training
Auto-DM. In DriveDreamer, we introduce Auto-DM, to
model and comprehend driving scenarios from real-world
driving videos.
It is noted that comprehending driving
scenes solely from pixel space presents challenges due to
extensive search space in real-world driving scenarios. To
mitigate this, we explicitly incorporate structured traffic in-
formation as conditional inputs.
The overall structure of Auto-DM is illustrated in Fig. 4,
where traffic conditions are projected onto the image plane,
generating HDMap conditions {Hi}N−1
i=0
∈RN×H×W ×3,
and 3D boxes conditions {Bi}N−1
i=0
∈RN×NB×16, along
with the box categories {Ci}N−1
i=0
∈RN×NB (N is the
number of video frames, and NB is the predefined maxi-
mum box numbers with zero padded). In this following,
unless specified, the subscript i is omitted for readability.
To enable controllability, the spatially aligned conditions H
are encoded by convolution layers and then concatenated
with Zt, where {Zt}N−1
i=0 are noisy latent features generated
by the forward diffusion process [57]. For position condi-
tions (i.e., 3D boxes) that are not spatially aligned with Zt,
we first aggregate position embeddings Hp:
  H ^p = \m athcal {F}_\alpha ( [ C_e,\text {Fourier}(B) ] ), 
(1)
where Fa is MLP layers, Ce is CLIP [54] embed box cat-
egories features, Fourier(·) is Fourier embedding [47], and
[·] is the concatenation operation. Then gated self-attention
[42] is leveraged to integrate position embeddings Hp with
visual signals v from the original UNet features [57]:
  v  = v + \ t ext {tanh }(\eta )\cdot \text {TS}(\mathcal {F}_s([v, H^p])), 
(2)
where η is a learnable parameter, Fs is self-attention, and
TS(·) is the token selection operation that considers visual
tokens only [42].
To further empower Auto-DM with comprehension of
driving dynamics, we introduce temporal attention layers
Ft to enhance frame coherence in the generated videos:
  \ma t hcal {F}_t(v) = \tex t  {Reshape}(\mathcal {F}_s(\text {Reshape}(v+\mathcal {T}_{\text {pos}}))), 
(3)
where
we
first
reshape
the
visual
signal
v
from
RN×C×H×W to RC×NHW .
The shape transformation
4


## Page 5

Text
"A realiVWic driYing
Vcene, da\Wime"
HDMaps
3D Boxes
GT Video
Enc
Enc
CLIP
Spatiall\ Aligned
Conditions
VWepV
TemSRUal-aWWenWiRn
CURVV-aWWenWiRn
GaWed Self-aWWenWiRn
Enc
Dec
Generated Video
CRQdiWiRQV
DiffXViRQ SWeSV
LoVV
DenoiVing
Position Embedding
CLIP Embedding
PUed
NRiVe
GaXVVian
NRiVe
"Car /¬PedeVWUian/..."
CLIP
Figure 4. Overall structure of the Auto-DM. Auto-DM takes three types of control conditions as inputs. Spatially aligned conditions
(i.e., HDMap HN−1
i=0 ), are concatenated with noise images and fed into the diffusion steps. Position conditions, represented by 3D boxes
BN−1
i=0 and their labels, are flattened and utilized in the gated self-attention. Text prompts are incorporated into diffusion steps using cross-
attention, influencing the style of the generated driving video. Temporal attention layers are employed to ensure the consistency of the
generated video frames. The diffusion steps estimate noise and generate loss with the input noise to optimize Auto-DM.
facilitates the frame-wise self-attention layers Fs to learn
inter-frame dynamics. Tpose denotes temporal position em-
beddings that are encoded by sinusoidal function [2]. Fi-
nally, we restore the visual signal to its original dimensions,
thus ensuring the feature integrity. Notably, the same archi-
tecture can be extended to generate multi-view images (see
Fig. 6), where the Fs solely attends to neighbor views. Ad-
ditionally, a stack of frame-wise attention and view-wise at-
tention contributes to multi-view video generation (see sup-
plement for more details).
Furthermore, cross-attention layers [57] are utilized to
facilitate feature interactions between text inputs and visual
signals, empowering text descriptions to influence driving
scene attributes such as weather and time of day. In the
next, we will elaborate on the first-stage training pipeline,
which involves two steps.
Step 1 training. The Auto-DM incorporates input solely
from a single frame of structured traffic conditions, coupled
with supervision from a single-frame image. For structured
traffic conditions, HDMaps and 3D boxes are obtained ei-
ther from human annotations or pertained perception meth-
ods (e.g., LAV [4], BEVerse [77], UniAD [31]). Then three-
channel HDMaps (lane boundary, lane divider, and pedes-
trian crossing) and eight-corner 3D boxes are projected onto
the image plane to generate corresponding conditions. No-
tably, during step 1 training, temporal attention layers are
omitted, which enables the network to focus exclusively
on learning the traffic structural constraints, expediting the
convergence of the training process.
Step 2 training.
The Auto-DM incorporates input from
multiple frames of structured traffic conditions and is su-
pervised using driving videos. In contrast to step 1, learning
from videos allows Auto-DM to gain a deeper understand-
ing of the intricate motion transitions in driving scenarios.
Building upon the pretrained models established in step 1,
step 2 incorporates temporal attention layers into the model
architecture. These additional parameters enable the Auto-
DM to focus on the temporal dynamics present in the input
data, further enhancing its ability to capture and interpret
the nuanced temporal aspects of driving scenes.
In step 1 and step 2 training, the proposed Auto-DM is
trained using the same noise schedule as the underlying im-
age model [57]. Specifically, the forward process gradually
adds noise ϵ to the latent feature Z0, resulting in the noisy
latent feature ZT . Then we train ϵϕ to predict the noise we
added, and the trainable parameters ϕ are optimized via:
  \
m i n  _{\phi } \mathc
a
l { L} =\ma th bb {
E
}
_{\mathcal {Z}_{0}, \epsilon \sim \mathcal {N}(\mathbf {0}, \mathbf {I}), t, c}\left [\left \|\epsilon -\epsilon _{\phi }\left (\mathcal {Z}_{t}, t, c\right )\right \|_{2}^{2}\right ], 
(4)
where ϕ denotes the trainable parameters involved in the
gated self-attention, temporal attention, and cross-attention
layers, and time step t is uniformly sampled from [1, T].
3.2. Second-stage Training
Based on the first-stage training, DriveDreamer has ob-
tained comprehension of the structured traffic information.
However, the desired world model should also be predictive
of the future and can interact with the environment. There-
fore, we embark on the second phase of our approach. In
this phase, we leverage the video prediction task to establish
5


## Page 6

Self-Attention
MLP
Enc
Enc
Self-Attention
Cross-Attention
GRU Blocks
Enc
Concat
Dec
Dec
Dec
"A realistic driving
scene, daytime"
Autonomous-driving Diffusion Model
CLIP
Enc
Observing
Predicting
Self-Attention
Cross-Attention
GRU Blocks
Enc
Concat
Figure 5. Overall structure of ActionFormer. The initial structural conditions H0 and B0 are first encoded and flattened into a 1D latent
space. These latent features are then concatenated and processed through self-attention and MLP layers, generating the hidden state.
Cross-attention layers establish associations between hidden states and driving actions. Gated Recurrent Units (GRUs) are employed to
iteratively predict future hidden states. These predicted hidden states are further concatenated with action features and decoded into future
traffic structural conditions to be fed into Auto-DM.
the driving world model. Specifically, the video prediction
task entails providing an initial observation I0, H0, B0, as
well as driving actions {Ai}T −1
i=0 , with the desired outcome
being the future driving videos {Ii}T
i=1, and future driving
actions {Ai}T +N
i=T .
ActionFormer. Recall that the trained Auto-DM can gen-
erate driving videos {Ii}T
i=0 based on sequential structured
information {Hi}T
i=0, {Bi}T
i=0. However, in the video pre-
diction task, future traffic structural conditions beyond the
present timestamp is unavailable. To address this challenge,
we introduce the ActionFormer, which leverages driving ac-
tions {Ai}T −1
i=0 to iteratively predict future structural condi-
tions. The overall architecture of ActionFormer is in Fig. 5.
Firstly the initial structural conditions H0, B0 are encoded
and flattened into 1D latent space. The latent features are
concatenated and aggregated by self-attention and MLP lay-
ers to generate the hidden state h0. Subsequently, cross-
attention layers Fca are utilized to construct associations
between hidden states and driving actions. Then latent vari-
able st is parameterized as:
  \ m ath bf {s}_{ t} \ s im  \mathca l {N }\ left (\mu _{\theta }\left (\mathcal {F}_{ca}(\mathbf {h}_t, A_t)\right ), \sigma _{\theta }\left (\mathcal {F}_{ca}(\mathbf {h}_t, A_t)\right ) \boldsymbol {I}\right ), 
(5)
where µθ, σθ are layers to learn Gaussian parameters. To
predict future hidden states, we employ Gated Recurrent
Units (GRUs) to iteratively make updates:
  \m a thbf {h} _{t+1} = \mathcal {F}_\text {GRU}(\mathbf {h}_t, \mathbf {s}_t). \label {eq:hidden} 
(6)
These hidden states are concatenated with action features
and are decoded into future traffic structural conditions. It’s
noted that the Actionformer forecasts future traffic condi-
tions at the feature level, which mitigates noise interference
at the pixel level, resulting in more robust predictions. Be-
sides the traffic structural conditions generated by Action-
former and the text prompt condition, we process the refer-
ence image condition I0 similar to [2]. Based on the above
conditions, we extend Auto-DM to jointly generate future
driving videos {Ii}T
i=1 and driving actions {Ai}T +N
i=T . We
formalize this process as a generative probabilistic model,
where the joint probability can be factorized as:
  \beg i n {a lig ned}  &p\l eft
 ( I_{0:  T} , A_ { 0: T + N}, \ma thbf  {h }_{
0
:
 T}
,  \ma th b f {s} _{0:T -1}  \right )\\ &\quad =p\left (I_{1:T}, A_{T:T+N} \mid \mathbf {h}_{0:T}, \mathbf {s}_{0:T-1}, A_{0:T-1}, I_0\right )\\ &\quad \quad \prod _{t=0}^{T} p\left (\mathbf {h}_{t}, \mathbf {s}_{t} \mid \mathbf {h}_{t-1}, \mathbf {s}_{t-1}, A_{t}\right ), \end {aligned} 
(7)
where
  \be gi n  {ali gned}  &p
\ l eft  (\mat hbf { h }_{ t }, \ma
t hbf { s }_ {t } \ mid \ math bf {h}_ {t- 1},
 \ mathb f  {s} _ {t-1 }, A_{t }\r igh
t  ) \\  & \ quad  \qua d \ quad  =p \le ft (\mathbf {h}_{t} \mid \mathbf {h}_{t-1}, \mathbf {s}_{t-1}\right ) p\left (\mathbf {s}_{t} \mid \mathbf {h}_{t}, A_{t}\right ) \\ &p\left (I_{1:T}, A_{T:T+N} \mid \mathbf {h}_{0:T}, \mathbf {s}_{0:T-1}, A_{0:T-1}, I_0\right ) \\ &\quad \quad \quad =p\left (I_{1:T}\mid \mathbf {h}_{0:T}, \mathbf {s}_{0:T-1}, A_{0:T-1}, I_0\right ) \\ &\quad \quad \quad \quad \quad p\left (A_{T:T+N}\mid \mathbf {h}_{0:T}, \mathbf {s}_{0:T-1}, A_{0:T-1}, I_0\right ). \end {aligned} 
(8)
6


## Page 7

Considering updating hidden states p(ht | ht−1, st−1) is
a deterministic process (Eq. 6), only latent variables st are
needed to be inferred to maximize the marginal likelihood
of observation p(I1:T , AT :T +N). Therefore, variational dis-
tribution qvd is introduced to conduct variational inference:
  \ b e gin { a lign e d} q _ \tex t {
v
d
}
 &\
t ria n gleq q\lef t  (\ m athb f {h }_{1: T}, \mathbf {s}_{1: T} \mid I_{0: T}, A_{0: T+N}\right )\\ &=\prod _{t=1}^{T} q\left (\mathbf {h}_{t} \mid \mathbf {h}_{t-1}, \mathbf {s}_{t-1}\right ) q\left (\mathbf {s}_{t} \mid I_{\leq t}, A_{<t}\right ), \end {aligned} 
(9)
where q (ht | ht−1, st−1) = p (ht | ht−1, st−1). Similar
to [29], the variational lower bound can be derived as:
  \ b egin { al ig ned }
 &\log p \le ft (I _{1: T},\rig h t . \ l eft .  A_{ T: T+N} \ri ght
 
)\
g
e \\ &\mathbb {
E }_{ q \le ft  ( \ math b f {h }_{ 1: T }, \ma
t
hb
f
 {s}_{ 1: T} \mid
 I_{0:T}, A_{0:T+N}\right )}[\underbrace {\log p\left (I_{1:T} \mid \mathbf {h}_{0:T}, \mathbf {s}_{0:T-1}, A_{0:T-1}, I_0\right )}_{\text {video prediction }}\\ &\quad +\underbrace {\log p\left (A_{T:T+N} \mid \mathbf {h}_{0:T}, \mathbf {s}_{0:T-1}, A_{0:T-1}, I_0\right )}_{\text {action predcition}}]. \label {eq:vi} \end {aligned} 
(10)
Note that the posterior and prior matching [29] is not in-
cluded, as we empirically find the simplified variational
lower bound produces similar plausible results. In Eq. 10,
the video prediction and action prediction parts can be mod-
eled by Gaussian distributions N(G(h0:T , A0:T −1, I0), I)
and Laplace distribution Laplace(π(h0:T , A0:T −1, I0), 1).
Therefore, we employ mean-squared error and L1 loss to
optimize the video prediction training. G, π are learnable
layers involved in ActionFormer, Auto-DM, video decoder
(i.e., VAE decoder) and action decoder. For action predic-
tion details, we first pool multi-scale UNet features from
Auto-DM. The pooled features are concatenated with histor-
ical action features, which are then decoded by MLP layers
to generate future driving actions.
Based on the two-stage training, DriveDreamer has ac-
quired a comprehensive understanding of the driving world,
encompassing the structural constraints of traffic, predic-
tions of future driving states, and interaction with the es-
tablished world model.
4. Experiment
4.1. Experiment Details
Dataset. The training data is sourced from the real-world
driving dataset nuScenes [3], comprising a total of 700
training videos and 150 validation videos. Each video in-
cludes ∼20 seconds of footage captured by six surround-
view cameras. The videos have a frame rate of 12Hz, re-
sulting in ∼1M video frames available for training. During
the first-stage training, we utilize the nuScenes-devkit [51]
to acquire HDMap annotations (lane boundary, lane divider,
and pedestrian crossing) corresponding to 12Hz frames,
which are then projected onto the image plane. Consider-
ing the nuScenes dataset only provides 2Hz 3D bounding
box annotations, we supplement this with 12Hz bounding
box annotations from [68]. In the second-stage training, we
employ the yaw angle and velocity of the ego-car as the
driving action inputs. Besides, we extract scene description
information (e.g., weather and time) from the nuScenes an-
notation, which serves as text conditions.
Training. The proposed Auto-DM is built upon Stable Dif-
fusion v1.4 [57], whose original parameters are frozen. In
step 1 of first-stage training, our model is trained for 40
epochs with a batch size of 16. In step 2, Auto-DM is trained
for 10 epochs with a batch size of 1, with video frame length
N = 32, and spatial size of 448×256. During second-stage
video prediction training, our model predicts 16 frame driv-
ing videos I1:16 and 16 future driving actions I17:32, and the
model is trained for 10 epochs on a batch size of 1. All the
experiments are conducted on A800 GPUs, and we use the
AdamW optimizer [38] with a learning rate 5 × 10−5.
Evaluation.
We conducted a comprehensive evaluation
of the proposed DriveDreamer, employing both qualita-
tive and quantitative assessments. We utilized frame-wise
Fr´echet Inception Distance (FID) [22] and Fr´echet Video
Distance (FVD) [63] to evaluate the generation quality,
where the evaluated image is resized to 448 × 256. Be-
sides, to verify the generated images enhance the training
of driving perception methods, DriveDreamer is evaluated
through 3D object detection, with FCOS3D [66] and BEV-
Fusion [45] as baseline methods. Furthermore, we test the
performance of driving policy generation. Following the
settings in [30], we evaluate output driving trajectories for
future 3 seconds.
4.2. Controllable Driving Video Generation
The proposed DriveDreamer exhibits a profound com-
prehension of driving scenarios, capable of controllably
generating diverse driving videos. In this subsection, we
first demonstrate that, based on first-stage training, Drive-
Dreamer can generate diverse driving videos under struc-
tured traffic conditions. Besides, we verify that the gener-
ated images can enhance the training of driving perception
methods. Furthermore, DriveDreamer showcases its versa-
tility by responding to different input actions, allowing for
the control of the vehicle’s trajectory and consequently gen-
erating diverse driving videos.
As shown in Fig. 1 and Fig 6, DriveDreamer exhibits
proficiency in producing images and videos that adhere
meticulously to structured traffic conditions (more visual-
izations are in supplement). Significantly, we can also ma-
nipulate the text prompt to induce variations in the gener-
ated videos, encompassing changes in weather and time of
day. To further validate the generation quality, we extract
4K traffic conditions (from the nuScenes training set) to
generate driving images. The generated images are com-
bined with real images for training the 3D detection task.
Results in Tab. 1 indicate that training with our synthetic
7


## Page 8

Ground Truth images
Generated images
Ground Truth images
Generated images
Figure 6. Visualizations of generated multi-view images, where the generation conditions (HDMaps, 3D boxes) are from nuScenes valida-
tion set. Regions highlighted by red rectangles and yellow circles indicate that the generated images share multi-view consistency and are
aligned with ground truth conditions.
Methods
Resolution
Data
mAP (↑)
NDS (↑)
FCOS3D [66]
1600 × 900
w/o synthetic data
30.2
38.1
FCOS3D [66]
1600 × 900
w 4K synthetic data
30.9 (+0.7)
38.3 (+0.2)
BEVFusion [45]
704 × 256
w/o synthetic data
32.8
37.6
BEVFusion [45]
704 × 256
w 4K synthetic data
35.8 (+3.0)
39.5 (+1.9)
Table 1. Performance of synthetic data augmentation on training
3D object detection.
data significantly enhances the performance of 3D detec-
tion. Specifically, compared with training without synthetic
data, the mAP metrics of FCOS3D and BEVFusion are im-
proved by 0.7 and 3.0.
In addition to the utilization of structured traffic condi-
tions for generating driving videos, DriveDreamer exhibits
the capability to diversify the generated driving videos by
adapting to different driving actions. As depicted in Fig. 1
(more visualizations are in supplement), starting from an
initial frame paired with its corresponding structural infor-
mation, DriveDreamer can generate distinct videos based
on various driving actions, such as videos depicting left and
right turns. In summary, DriveDreamer excels in produc-
ing a wide spectrum of driving scene videos, characterized
by both high controllability and diversity.
Thus, Drive-
Dreamer holds promise for training autonomous-driving
systems across a wide range of tasks, encompassing even
corner cases and long-tail scenarios.
In the quantitative experiment, we extract ego-car driv-
ing actions from the nuScenes validation set as conditions
to generate driving videos. For comparison, we train Drive-
GAN [36] on the nuScenes dataset, employing the same
training settings as those used for Drivedreamer. Besides,
we train Drivedreamer without ActionFormer as a baseline
Methods
1st-stage train
2nd-stage train
FID (↓)
FVD (↓)
(Auto-DM)
(ActionFormer)
DriveGAN [36]
-
-
27.8
390.8
DriveDreamer
15.9
363.3
DriveDreamer
✓
15.3
349.6
DriveDreamer
✓
✓
14.9
340.8
Table 2. Comparison of generation quality on nuScenes validation.
(specifically, the action features are directly concatenated
with the zero-padded structured traffic conditions). The re-
sults are presented in Tab. 2, where we evaluate the quality
of generated videos. Notably, our approach without first-
stage training achieves superior FID and FVD scores com-
pared to DriveGAN. This observation underscores the ef-
fectiveness of leveraging a powerful diffusion model in vi-
sually comprehending driving scenarios. Furthermore, our
findings reveal that Drivedreamer after first-stage training,
exhibits an improved understanding of the structured in-
formation within driving scenes, resulting in higher-quality
video generation. Lastly, we observe that the proposed Ac-
tionFormer effectively leverages the traffic structural infor-
mation knowledge acquired during the first-stage training.
Compared to the concatenation baseline approach, the Ac-
tionFormer iteratively updates future structured information
based on input actions, which further enhances the quality
of generated videos.
4.3. Driving Action Generation
In addition to its capacity for generating highly control-
lable driving videos, DriveDreamer demonstrates the abil-
ity to predict reasonable driving actions. As depicted in
8


## Page 9

Method
Visual Info.
Action Info.
L2 Avg. (m)
Col. Avg. (%)
ST-P3 [30]
✓
2.11
0.71
UniAD [31]
✓
1.65
0.31
AD-MLP [75]
✓
0.29
0.19
VAD [33]
✓
✓
0.37
0.14
DriveDreamer
✓
✓
0.29
0.15
Table 3. Open-loop planning performance on nuScenes validation
set. The evaluation settings are the same as ST-P3 [30].
Fig. 1, provided with an initial frame condition and past
driving actions, DriveDreamer can generate future driving
actions that align with real-world scenarios . Furthermore,
we conduct a quantitative assessment of the prediction ac-
curacy. Specifically, MLP layers [75] are utilized to encode
past driving action information. Additionally, multi-scale
UNet features are pooled as visual cues. The two modality
features are then concatenated to learn future driving trajec-
tories (more implementation details are in supplement). The
results of open-loop evaluation on the nuScenes dataset are
presented in Tab. 3. Remarkably, the average L2 trajectory
error of DriveDreamer is merely 0.29m, surpassing the per-
formance of the multi-modality method VAD [33]. In addi-
tion, DriveDreamer relatively decreases the average colli-
sion rate reported in [75] by 21%, confirming that the visual
features learned by DriveDreamer contribute to end-to-end
autonomous driving, thereby enhancing driving safety.
5. Discussion and Conclusion
DriveDreamer represents a significant advancement in
the field of world modeling, particularly in the context
of autonomous driving. By focusing on real-world driv-
ing scenarios and harnessing the power of the diffusion
model, DriveDreamer has demonstrated its ability to com-
prehend complex environments, generate high-quality driv-
ing videos, and formulate realistic driving policies. While
prior research primarily concentrated on gaming or simu-
lated environments, DriveDreamer extends the boundaries
of world modeling to encompass the intricacies of actual
driving conditions. DriveDreamer paves the way for future
research in autonomous driving, emphasizing the impor-
tance of real-world representation for more accurate mod-
eling and decision-making in this critical domain.
References
[1] Fan Bao, Shen Nie, Kaiwen Xue, Chongxuan Li, Shi Pu,
Yaole Wang, Gang Yue, Yue Cao, Hang Su, and Jun Zhu.
One transformer fits all distributions in multi-modal diffu-
sion at scale. arXiv preprint arXiv:2303.06555, 2023. 2
[2] Andreas Blattmann, Robin Rombach, Huan Ling, Tim Dock-
horn, Seung Wook Kim, Sanja Fidler, and Karsten Kreis.
Align your latents: High-resolution video synthesis with la-
tent diffusion models. In CVPR, 2023. 5, 6
[3] Holger Caesar, Varun Bankiti, Alex H. Lang, Sourabh Vora,
Venice Erin Liong, Qiang Xu, Anush Krishnan, Yu Pan, Gi-
ancarlo Baldan, and Oscar Beijbom.
nuscenes: A multi-
modal dataset for autonomous driving. CVPR, 2019. 7, 12
[4] Dian Chen and Philipp Kr¨ahenb¨uhl. Learning from all vehi-
cles. In CVPR, 2022. 5
[5] Li Chen, Penghao Wu, Kashyap Chitta, Bernhard Jaeger,
Andreas Geiger,
and Hongyang Li.
End-to-end au-
tonomous driving: Challenges and frontiers. arXiv preprint
arXiv:2306.16927, 2023. 2, 3
[6] Rui Chen, Yongwei Chen, Ningxin Jiao, and Kui Jia.
Fantasia3d:
Disentangling geometry and appearance for
high-quality text-to-3d content creation.
arXiv preprint
arXiv:2303.13873, 2023. 2
[7] Felipe Codevilla, Eder Santana, Antonio M L´opez, and
Adrien Gaidon.
Exploring the limitations of behavior
cloning for autonomous driving. In CVPR, 2019. 2
[8] Emily Denton and Rob Fergus. Stochastic video generation
with a learned prior. In ICML, 2018. 2, 3
[9] Prafulla Dhariwal and Alexander Nichol. Diffusion models
beat gans on image synthesis. NeurIPS, 2021. 3
[10] Stefan Elfwing, Eiji Uchibe, and Kenji Doya.
Sigmoid-
weighted linear units for neural network function approxi-
mation in reinforcement learning. Neural networks, 2018.
12
[11] Jean-Yves Franceschi, Edouard Delasalles, Micka¨el Chen,
Sylvain Lamprier, and Patrick Gallinari. Stochastic latent
residual video prediction. In ICML, 2020. 2, 3
[12] Ruiyuan Gao, Kai Chen, Enze Xie, Lanqing Hong, Zhenguo
Li, Dit-Yan Yeung, and Qiang Xu. Magicdrive: Street view
generation with diverse 3d geometry control. arXiv preprint
arXiv:2310.02601, 2023. 3
[13] Zeyu Gao, Yao Mu, Ruoyan Shen, Chen Chen, Yangang Ren,
Jianyu Chen, Shengbo Eben Li, Ping Luo, and Yanfeng Lu.
Enhance sample efficiency and robustness of end-to-end ur-
ban autonomous driving via semantic masked world model.
arXiv preprint arXiv:2210.04017, 2022. 2, 3
[14] Shuyang Gu, Dong Chen, Jianmin Bao, Fang Wen, Bo
Zhang, Dongdong Chen, Lu Yuan, and Baining Guo. Vec-
tor quantized diffusion model for text-to-image synthesis. In
CVPR, 2022. 2
[15] David Ha and J¨urgen Schmidhuber. Recurrent world models
facilitate policy evolution. NeurIPS, 2018. 2, 3
[16] Danijar Hafner, Kuang-Huei Lee, Ian Fischer, and Pieter
Abbeel. Deep hierarchical planning from pixels. NeurIPS,
2022. 3
[17] Danijar Hafner, Timothy Lillicrap, Jimmy Ba, and Moham-
mad Norouzi. Dream to control: Learning behaviors by la-
tent imagination. arXiv preprint arXiv:1912.01603, 2019. 2,
3
[18] Danijar Hafner, Timothy Lillicrap, Mohammad Norouzi, and
Jimmy Ba. Mastering atari with discrete world models. arXiv
preprint arXiv:2010.02193, 2020. 2, 3
[19] Danijar Hafner, Jurgis Pasukonis, Jimmy Ba, and Timothy
Lillicrap. Mastering diverse domains through world models.
arXiv preprint arXiv:2301.04104, 2023. 2, 3
9


## Page 10

[20] Danijar Hafner, Jurgis Pasukonis, Jimmy Ba, and Timothy
Lillicrap. Mastering diverse domains through world models.
arXiv preprint arXiv:2301.04104, 2023. 3
[21] William Harvey, Saeid Naderiparizi, Vaden Masrani, Chris-
tian Weilbach, and Frank Wood. Flexible diffusion modeling
of long videos. NeurIPS, 2022. 2, 3
[22] Martin Heusel, Hubert Ramsauer, Thomas Unterthiner,
Bernhard Nessler, and Sepp Hochreiter. Gans trained by a
two time-scale update rule converge to a local nash equilib-
rium. NeurIPS, 2017. 7
[23] Jonathan Ho, William Chan, Chitwan Saharia, Jay Whang,
Ruiqi Gao, Alexey Gritsenko, Diederik P Kingma, Ben
Poole, Mohammad Norouzi, David J Fleet, et al. Imagen
video: High definition video generation with diffusion mod-
els. arXiv preprint arXiv:2210.02303, 2022. 2, 3
[24] Jonathan Ho, Ajay Jain, and Pieter Abbeel. Denoising diffu-
sion probabilistic models. NeurIPS, 2020. 3
[25] Jonathan Ho, Chitwan Saharia, William Chan, David J Fleet,
Mohammad Norouzi, and Tim Salimans. Cascaded diffusion
models for high fidelity image generation. JMLR, 2022. 3
[26] Sepp Hochreiter and J¨urgen Schmidhuber. Long short-term
memory. Neural computation, 1997. 3
[27] Tobias H¨oppe, Arash Mehrjou, Stefan Bauer, Didrik Nielsen,
and Andrea Dittadi. Diffusion models for video prediction
and infilling. arXiv preprint arXiv:2206.07696, 2022. 3
[28] Jun-Ting Hsieh, Bingbin Liu, De-An Huang, Li F Fei-Fei,
and Juan Carlos Niebles. Learning to decompose and disen-
tangle representations for video prediction. NeurIPS, 2018.
3
[29] Anthony Hu, Gianluca Corrado, Nicolas Griffiths, Zachary
Murez, Corina Gurau, Hudson Yeo, Alex Kendall, Roberto
Cipolla, and Jamie Shotton. Model-based imitation learning
for urban driving. NeurIPS, 2022. 2, 3, 7
[30] Shengchao Hu, Li Chen, Penghao Wu, Hongyang Li, Junchi
Yan, and Dacheng Tao. St-p3: End-to-end vision-based au-
tonomous driving via spatial-temporal feature learning. In
ECCV, 2022. 7, 9
[31] Yihan Hu, Jiazhi Yang, Li Chen, Keyu Li, Chonghao Sima,
Xizhou Zhu, Siqi Chai, Senyao Du, Tianwei Lin, Wenhai
Wang, Lewei Lu, Xiaosong Jia, Qiang Liu, Jifeng Dai, Yu
Qiao, and Hongyang Li. Planning-oriented autonomous driv-
ing. In CVPR, 2023. 5, 9
[32] Lianghua Huang, Di Chen, Yu Liu, Yujun Shen, Deli Zhao,
and Jingren Zhou. Composer: Creative and controllable im-
age synthesis with composable conditions. arXiv preprint
arXiv:2302.09778, 2023. 3
[33] Bo Jiang, Shaoyu Chen, Qing Xu, Bencheng Liao, Jia-
jie Chen, Helong Zhou, Qian Zhang, Wenyu Liu, Chang
Huang, and Xinggang Wang. Vad: Vectorized scene rep-
resentation for efficient autonomous driving. arXiv preprint
arXiv:2303.12077, 2023. 9
[34] Nal Kalchbrenner, A¨aron Oord, Karen Simonyan, Ivo Dani-
helka, Oriol Vinyals, Alex Graves, and Koray Kavukcuoglu.
Video pixel networks. In ICML, 2017. 3
[35] Levon Khachatryan, Andranik Movsisyan, Vahram Tade-
vosyan,
Roberto
Henschel,
Zhangyang
Wang,
Shant
Navasardyan, and Humphrey Shi. Text2video-zero: Text-to-
image diffusion models are zero-shot video generators. arXiv
preprint arXiv:2303.13439, 2023. 2, 3
[36] Seung Wook Kim, Jonah Philion, Antonio Torralba, and
Sanja Fidler. Drivegan: Towards a controllable high-quality
neural simulation. In CVPR, 2021. 3, 8
[37] Seung Wook Kim, Yuhao Zhou, Jonah Philion, Antonio Tor-
ralba, and Sanja Fidler. Learning to simulate dynamic envi-
ronments with gamegan. In CVPR, 2020. 3
[38] Diederik P Kingma and Jimmy Ba. Adam: A method for
stochastic optimization.
arXiv preprint arXiv:1412.6980,
2014. 7
[39] Diederik P Kingma and Max Welling. Auto-encoding varia-
tional bayes. arXiv preprint arXiv:1312.6114, 2013. 3
[40] Manoj Kumar, Mohammad Babaeizadeh, Dumitru Erhan,
Chelsea Finn, Sergey Levine, Laurent Dinh, and Durk
Kingma.
Videoflow: A flow-based generative model for
video. arXiv preprint arXiv:1903.01434, 2019. 3
[41] Xiaofan Li, Yifu Zhang, and Xiaoqing Ye.
Drivingdif-
fusion:
Layout-guided multi-view driving scene video
generation with latent diffusion model.
arXiv preprint
arXiv:2310.07771, 2023. 3
[42] Yuheng Li, Haotian Liu, Qingyang Wu, Fangzhou Mu, Jian-
wei Yang, Jianfeng Gao, Chunyuan Li, and Yong Jae Lee.
Gligen: Open-set grounded text-to-image generation.
In
CVPR, 2023. 2, 4
[43] Chen-Hsuan Lin, Jun Gao, Luming Tang, Towaki Takikawa,
Xiaohui Zeng, Xun Huang, Karsten Kreis, Sanja Fidler,
Ming-Yu Liu, and Tsung-Yi Lin. Magic3d: High-resolution
text-to-3d content creation. In CVPR, 2023. 2
[44] Jessy Lin, Yuqing Du, Olivia Watkins, Danijar Hafner, Pieter
Abbeel, Dan Klein, and Anca Dragan. Learning to model
the world with language. arXiv preprint arXiv:2308.01399,
2023. 3
[45] Zhijian Liu, Haotian Tang, Alexander Amini, Xinyu Yang,
Huizi Mao, Daniela L Rus, and Song Han. Bevfusion: Multi-
task multi-sensor fusion with unified bird’s-eye view repre-
sentation. In ICRA, 2023. 7, 8, 13
[46] Michael Mathieu, Camille Couprie, and Yann LeCun. Deep
multi-scale video prediction beyond mean square error.
arXiv preprint arXiv:1511.05440, 2015. 3
[47] Ben Mildenhall, Pratul P Srinivasan, Matthew Tancik,
Jonathan T Barron, Ravi Ramamoorthi, and Ren Ng. Nerf:
Representing scenes as neural radiance fields for view syn-
thesis. Communications of the ACM, 2021. 4, 12
[48] Chong Mou, Xintao Wang, Liangbin Xie, Jian Zhang, Zhon-
gang Qi, Ying Shan, and Xiaohu Qie. T2i-adapter: Learning
adapters to dig out more controllable ability for text-to-image
diffusion models. arXiv preprint arXiv:2302.08453, 2023. 2
[49] Alex Nichol, Prafulla Dhariwal, Aditya Ramesh, Pranav
Shyam, Pamela Mishkin, Bob McGrew, Ilya Sutskever, and
Mark Chen. Glide: Towards photorealistic image generation
and editing with text-guided diffusion models. arXiv preprint
arXiv:2112.10741, 2021. 2, 3
[50] Alexander Quinn Nichol and Prafulla Dhariwal. Improved
denoising diffusion probabilistic models. In ICML, 2021. 3
10


## Page 11

[51] nuScenes Contributors. The devkit of the nuscenes dataset.
https : / / github . com / nutonomy / nuscenes -
devkit, 2019. 7
[52] Minting Pan, Xiangming Zhu, Yunbo Wang, and Xiaokang
Yang. Iso-dream: Isolating and leveraging noncontrollable
visual dynamics in world models. NeurIPS, 2022. 2, 3
[53] Ben Poole, Ajay Jain, Jonathan T Barron, and Ben Milden-
hall.
Dreamfusion: Text-to-3d using 2d diffusion.
arXiv
preprint arXiv:2209.14988, 2022. 2
[54] Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya
Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry,
Amanda Askell, Pamela Mishkin, Jack Clark, et al. Learn-
ing transferable visual models from natural language super-
vision. In ICML. 4
[55] Aditya Ramesh, Prafulla Dhariwal, Alex Nichol, Casey Chu,
and Mark Chen. Hierarchical text-conditional image gen-
eration with clip latents. arXiv preprint arXiv:2204.06125,
2022. 2
[56] MarcAurelio Ranzato, Arthur Szlam, Joan Bruna, Michael
Mathieu, Ronan Collobert, and Sumit Chopra. Video (lan-
guage) modeling: a baseline for generative models of natural
videos. arXiv preprint arXiv:1412.6604, 2014. 3
[57] Robin Rombach, Andreas Blattmann, Dominik Lorenz,
Patrick Esser, and Bj¨orn Ommer. High-resolution image syn-
thesis with latent diffusion models. In CVPR, 2022. 2, 3, 4,
5, 7
[58] Masaki Saito, Eiichi Matsumoto, and Shunta Saito. Tempo-
ral generative adversarial nets with singular value clipping.
In ICCV, 2017. 3
[59] Younggyo Seo, Danijar Hafner, Hao Liu, Fangchen Liu,
Stephen James, Kimin Lee, and Pieter Abbeel.
Masked
world models for visual control. In CoRL, 2023. 3
[60] Uriel Singer, Adam Polyak, Thomas Hayes, Xi Yin, Jie An,
Songyang Zhang, Qiyuan Hu, Harry Yang, Oron Ashual,
Oran Gafni, et al. Make-a-video: Text-to-video generation
without text-video data. arXiv preprint arXiv:2209.14792,
2022. 2, 3
[61] Nitish Srivastava, Elman Mansimov, and Ruslan Salakhudi-
nov. Unsupervised learning of video representations using
lstms. In ICML, 2015. 3
[62] Sergey Tulyakov, Ming-Yu Liu, Xiaodong Yang, and Jan
Kautz.
Mocogan: Decomposing motion and content for
video generation. In CVPR, 2018. 3
[63] Thomas Unterthiner, Sjoerd Van Steenkiste, Karol Kurach,
Raphael Marinier, Marcin Michalski, and Sylvain Gelly. To-
wards accurate generative models of video: A new metric &
challenges. arXiv preprint arXiv:1812.01717, 2018. 7
[64] Vikram Voleti, Alexia Jolicoeur-Martineau, and Chris Pal.
Mcvd-masked conditional video diffusion for prediction,
generation, and interpolation. NeurIPS, 2022. 3
[65] Carl Vondrick, Hamed Pirsiavash, and Antonio Torralba.
Generating videos with scene dynamics. NeurIPS, 29, 2016.
3
[66] Tai Wang, Xinge Zhu, Jiangmiao Pang, and Dahua Lin.
Fcos3d: Fully convolutional one-stage monocular 3d object
detection. In CVPR, 2021. 7, 8, 13
[67] Xiang Wang, Hangjie Yuan, Shiwei Zhang, Dayou Chen,
Jiuniu Wang, Yingya Zhang, Yujun Shen, Deli Zhao,
and Jingren Zhou.
Videocomposer: Compositional video
synthesis with motion controllability.
arXiv preprint
arXiv:2306.02018, 2023. 2, 3
[68] Xiaofeng Wang, Zheng Zhu, Yunpeng Zhang, Guan Huang,
Yun Ye, Wenbo Xu, Ziwei Chen, and Xingang Wang. Are we
ready for vision-centric driving streaming perception? the
asap benchmark. In CVPR, 2023. 7
[69] Zhengyi Wang, Cheng Lu, Yikai Wang, Fan Bao, Chongxuan
Li, Hang Su, and Jun Zhu. Prolificdreamer: High-fidelity and
diverse text-to-3d generation with variational score distilla-
tion. arXiv preprint arXiv:2305.16213, 2023. 2
[70] Dirk Weissenborn, Oscar T¨ackstr¨om, and Jakob Uszkor-
eit.
Scaling autoregressive video models.
arXiv preprint
arXiv:1906.02634, 2019. 3
[71] Philipp Wu, Alejandro Escontrela, Danijar Hafner, Pieter
Abbeel, and Ken Goldberg. Daydreamer: World models for
physical robot learning. In CoRL, 2023. 3
[72] Kairui Yang, Enhui Ma, Jibin Peng, Qing Guo, Di Lin, and
Kaicheng Yu.
Bevcontrol: Accurately controlling street-
view elements with multi-perspective consistency via bev
sketch layout. arXiv preprint arXiv:2308.01661, 2023. 3
[73] Ling Yang, Zhilong Zhang, Yang Song, Shenda Hong, Run-
sheng Xu, Yue Zhao, Yingxia Shao, Wentao Zhang, Bin
Cui, and Ming-Hsuan Yang. Diffusion models: A compre-
hensive survey of methods and applications. arXiv preprint
arXiv:2209.00796, 2022. 2
[74] Ruihan Yang, Prakhar Srivastava, and Stephan Mandt. Dif-
fusion probabilistic modeling for video generation.
arXiv
preprint arXiv:2203.09481, 2022. 2, 3
[75] Jiang-Tian Zhai, Ze Feng, Jihao Du, Yongqiang Mao, Jiang-
Jiang Liu, Zichang Tan, Yifu Zhang, Xiaoqing Ye, and Jing-
dong Wang. Rethinking the open-loop evaluation of end-
to-end autonomous driving in nuscenes.
arXiv preprint
arXiv:2305.10430, 2023. 9, 12
[76] Lvmin Zhang, Anyi Rao, and Maneesh Agrawala. Adding
conditional control to text-to-image diffusion models, 2023.
2
[77] Yunpeng Zhang, Zheng Zhu, Wenzhao Zheng, Junjie Huang,
Guan Huang, Jie Zhou, and Jiwen Lu. Beverse: Unified per-
ception and prediction in birds-eye-view for vision-centric
autonomous driving.
arXiv preprint arXiv:2205.09743,
2022. 5
11


## Page 12

In the supplement materials, we first elaborate on the
implementation details of DriveDreamer, including model
architecture and synthetic data training details. Then, we
present additional visualization results.
6. Implementation Details
Condition encoders. In DriveDreamer, diverse encoders
are employed to embed different condition inputs, includ-
ing the reference image, HDMap, 3D box, and action. The
detailed architectures of these encoders are listed in Table 4.
For spatially aligned conditions, such as the reference im-
age I ∈RH×W ×3 and HDMap H ∈RH×W ×3, a stack
of 2D convolution layers is utilized to perform downsam-
pling, ensuring the final output dimensions align with those
of the diffusion noise. For unstructured conditions like the
3D box B ∈RN×NB×16 and action A ∈RN×2, Multi-
layer Perceptron (MLP) layers are employed for encoding
features.
Conditions
Layer Description
Output Size
Ref. Img. (Step A)
Conv2D, 4 × 4, S4
H/4 × W/4 × 4
Ref. Img. (Step B)
Conv2D, 4 × 4, S4
H/16 × W/16 × 4
Ref. Img. (Step C)
Conv2D, 4 × 4, S4
H/64 × W/64 × 8
HDMap (Step A)
Conv2D, 4 × 4, S4
H/4 × W/4 × 4
HDMap (Step B)
Conv2D, 4 × 4, S4
H/16 × W/16 × 4
HDMap (Step C)
Conv2D, 4 × 4, S4
H/64 × W/64 × 8
3D Box (Step A)
FourierEmbedder [47]
N × NB × 256
3D Box (Step B)
MLP
N × NB × 512
3D Box (Step C)
MLP
N × NB × 768
Action (Step A)
MLP
N × 32
Action (Step B)
MLP
N × 128
Table 4. Encoder architecture details, where S denotes stride, and
each convolution layer and MLP layer are followed by Sigmoid
Linear Units [10].
Multi-view generation. The framework of DriveDreamer
can be easily extended to multi-view image/video genera-
tion.
The model architecture comparison between video
generation, multi-view image generation and multi-view
video generation are shown in Fig. 7. For multi-view im-
age generation, the model framework is the same as that of
video generation, except that the frame-vise attention lay-
ers are replaced with view-wise attention layers. Besides,
the view-wise attention layers construct associations solely
between adjacent views. For multi-view video generation,
view-wise attention layers and frame-wise attention layers
are stacked to process diffusion latent features, which re-
sults in view-consistent and frame-consistent videos (see
Fig. 8).
Action prediction architecture. For action prediction, the
multi-modal features are first concatenated:
  \text {CONCA T}(\mat hcal {F }_{\tex t {p}}(U_0), \mathcal {F}_{\text {p}}(U_1), \mathcal {F}_{\text {p}}(U_2), \mathcal {F}_{\text {p}}(U_3), A_f), 
(11)
steps
Denoising
View-wise-attention
Cross-attention
Gated Self-attention
steps
Denoising
Frame-wise-attention
steps
Denoising
Video Generation
Multi-view Image Generation
Multi-view Video Generation
Figure 7. Model architecture comparison between video genera-
tion, multi-view image generation and multi-view video genera-
tion.
where Fp is the average pooling operation, Ui(i
=
0, 1, 2, 3) are multi-scale UNet features, and Af is the en-
coded driving action (i.e., velocity and yaw angle) features.
Then we use MLP layers [75] to learn future driving ac-
tions. For trajectory prediction evaluation, following [75],
Af is additionally extracted from high-level command, ac-
celerate and past trajectories, and we use the same action
feature encoder of [75].
Synthetic data training.
We leverage data generated
by DriveDreamer to augment the training of 3D detec-
tion tasks. Specifically, DriveDreamer is fine-tuned with
higher-resolution images, where the training data is from
nuScenes [3]. Consequently, DriveDreamer can generate
high-fidelity images with a resolution of 768 × 448. Then
the generated images are resized to the original resolution
of 1600 × 900, which can be utilized to train various off-
the-shelf 3D detectors. During the training process, we ran-
domly select 4000 samples (3D boxes and HDMap) from
the nuScenes training set, which are employed to generate
multi-view images. These synthetic data are mixed with
the original training set to train 3D detectors. In the ex-
12


## Page 13

Figure 8. Visualizations of the generated multi-view video. Regions highlighted by red circles indicate that the generated videos are view-
consistent and frame-consistent.
periment, we train each baseline (i.e., FCOS3D [66] and
BEVFusion [45]) for 12 epochs. The results presented in
Tab. 1 demonstrate that our approach significantly improves
the performance of downstream tasks.
7. Visualizations
As shown in Fig. 9, DriveDreamer exhibits significant
proficiency in producing a diverse range of driving scene
videos that adhere meticulously to structured traffic condi-
tions, comprising elements such as HDMaps and 3D boxes.
Significantly, we can also manipulate the text prompt to
induce variations in the generated videos, encompassing
changes in weather and time of day. This heightened adapt-
ability contributes substantially to the multifaceted nature of
the generated video outputs. In addition to the utilization of
structured traffic conditions for generating driving videos,
DriveDreamer exhibits the capability to diversify the gen-
erated driving videos by adapting to different driving ac-
tions. As depicted in Fig. 10, starting from an initial frame
paired with its corresponding structural information, Drive-
Dreamer can generate distinct videos based on various driv-
ing actions, such as videos depicting left and right turns.
Apart from its capacity for generating highly controllable
driving videos, DriveDreamer demonstrates the ability to
predict reasonable driving actions. As depicted in Fig. 11,
provided with an initial frame condition and past driving
actions, DriveDreamer can generate future driving actions
that align with real-world scenarios. Comparative analysis
of the generated actions against corresponding ground truth
videos reveals that DriveDreamer consistently predicts sen-
sible driving actions, even in complex situations such as in-
tersections, obeying traffic lights, and executing turns.
13


## Page 14

“Realistic autonousmous
     driving scen, sunny”
“Realistic autonousmous
     driving scene, night”
“Realistic autonousmous
     driving scene, rainy”
Structured traffic conditions
    HDMaps, 3D Bboxes
“Realistic autonousmous
     driving scene, sunny”
“Realistic autonousmous
     driving scene, night”
“Realistic autonousmous
     driving scene, rainy”
Structured traffic conditions
    HDMaps, 3D Bboxes
“Realistic autonousmous
     driving scene, sunny”
“Realistic autonousmous
     driving scene, night”
“Realistic autonousmous
     driving scene, rainy”
Structured traffic conditions
    HDMaps, 3D Bboxes
Figure 9. Driving video generation with structured traffic conditions (HDMaps and 3D boxes), where text prompts are utilized to adjust
driving scenario style (e.g., weather and time of the day).
14


## Page 15

Initial condition
Initial Conditions
Initial Conditions
Initial Condition
Turn Right
Turn Left
“Realistic autonousmous
     driving scene”
“Realistic autonousmous
     driving scene”
“Realistic autonousmous
     driving scene”
Turn Right
Turn Left
Turn Right
Turn Left
Figure 10. Future driving video generation with driving actions interaction, where different driving actions (e.g. turn left, turn right) can
produce corresponding driving videos.
Initial Condition
Initial Condition
Initial Condition
Initial Driving Actions
Initial Driving Actions
Initial Driving Actions
Figure 11. Visualization of the predicted future driving actions, along with the corresponding ground truth driving video.
15

