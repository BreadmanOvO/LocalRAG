# HENet++: Hybrid Encoding and Multi-task Learning for 3D Perception and End-to-end Autonomous Driving

**Source**: arXiv:2511.07106

**Type**: Academic Paper

---

## Page 1

HENet++: Hybrid Encoding and Multi-task Learning for 3D
Perception and End-to-end Autonomous Driving
Zhongyu Xia1, Zhiwei Lin1, Yongtao Wang1*, Ming-Hsuan Yang2
1Wangxuan Institute of Computer Technology, Peking University, Beijing, China.
2University of California, Merced, USA.
*Corresponding author(s). E-mail(s): wyt@pku.edu.cn;
Contributing authors: xiazhongyu@pku.edu.cn; zwlin@pku.edu.cn; mhyang@ucmerced.edu;
Abstract
Three-dimensional feature extraction is a critical component of autonomous driving systems, where
perception tasks such as 3D object detection, bird’s-eye-view (BEV) semantic segmentation, and
occupancy prediction serve as important constraints on 3D features. While large image encoders,
high-resolution images, and long-term temporal inputs can significantly enhance feature quality and
deliver remarkable performance gains, these techniques are often incompatible in both training and
inference due to computational resource constraints. Moreover, different tasks favor distinct feature
representations, making it difficult for a single model to perform end-to-end inference across multiple
tasks while maintaining accuracy comparable to that of single-task models. To alleviate these issues,
we present the HENet
and HENet++
framework for multi-task 3D perception and end-to-end
autonomous driving. Specifically, we propose a hybrid image encoding network that uses a large image
encoder for short-term frames and a small one for long-term frames. Furthermore, our framework
simultaneously extracts both dense and sparse features, providing more suitable representations for
different tasks, reducing cumulative errors, and delivering more comprehensive information to the
planning module. The proposed architecture maintains compatibility with various existing 3D feature
extraction methods and supports multimodal inputs. HENet++ achieves state-of-the-art end-to-end
multi-task 3D perception results on the nuScenes benchmark, while also attaining the lowest collision
rate on the nuScenes end-to-end autonomous driving benchmark.
Keywords: Autonomous Driving, 3D Object Detection, BEV Segmentation, Occupancy Network, 3D
Perception
1 Introduction
3D perception capability is the foundation of
autonomous driving systems and various other
embodied control systems. It is responsible for
encoding sensor information, extracting and inter-
preting features, and serves as a prerequisite for an
agent’s interaction with the world. Specifically, 3D
perception encompasses tasks such as 3D object
detection, Bird’s Eye View (BEV) semantic seg-
mentation, and semantic occupancy prediction.
Some autonomous driving systems are divided
into multiple deep learning modules, where the
results of 3D perception are used for subsequent
planning and control. In recent years, end-to-end
autonomous driving has gained increasing atten-
tion. This approach employs a single network that
1
arXiv:2511.07106v1  [cs.CV]  10 Nov 2025


## Page 2

takes sensor information as input and directly out-
puts trajectory planning or control commands for
the ego vehicle. This does not bypass perception
because 3D feature extraction from sensor infor-
mation remains indispensable. Moreover, many
studies [1–3] have pointed out that relying solely
on trajectory supervision makes it difficult for
the network to learn complex logic, leading to
hallucinations. Therefore, the model still requires
perceptual task decoders to impose constraints on
the 3D features.
In the process of building an end-to-end
autonomous driving system, there are several chal-
lenges. The first challenge is the difficulty in
simultaneously achieving higher resolution, larger
encoding networks, and more frames. Autonomous
driving requires recognizing objects tens or even
hundreds of meters away, which necessitates the
use of high-resolution multi-view images. Pro-
cessing high-resolution images often requires an
encoder with larger parameter sizes and com-
putational demands (including backbones, necks,
depth network or Transformers for 2D-to-3D trans-
formation, etc.). Additionally, given the limited
overlap between multi-camera images, stereo spa-
tial information often relies on temporal sequences.
Moreover, information about occluded objects
must also be retrieved from historical frames.
However, each of these aspects requires more com-
putational resources, thereby increasing training
costs.
The second challenge is multi-task learning.
The vast majority of existing 3D perception work
is single-task. Even those claiming multi-task com-
patibility often train a separate model for each
task. However, in 3D perception models, over 80%
of the computational load is concentrated in the
sensor information encoding part. A single model
predicting multiple tasks end-to-end can save com-
putational resources. Yet, some tasks focus on
foreground objects while others concentrate on
background elements, potentially favoring differ-
ent model architectures. When sharing an encoder
directly, the predictive performance on each task
tends to be lower than with single-task mod-
els. Additionally, loading pre-trained parameters
from different tasks can also affect the perfor-
mance of each task. How to balance these tasks
and enhance their overall performance remains a
question worthy of research.
4
8
16
32
64
128
256
ST-P3
OccNet
UniAD
VAD
PARA-Drive
GenAD
SparseDrive
MomAD
SSR
BridgeAD
DiffusionDrive
HENet++(Ours)
Joint Sparse and 
Dense Encoding
Training
Cost
2
10
256x704 
+ R50
640x1152 
+ v2-99
Frames
Training Cost per Frame
2
10
256x704 
+ R50
640x1152 
+ v2-99
Training Cost per Frame
Frames
Hybrid 
Encoding
Multi-task Learning
Planning
Transformer
Pretrain based on
Model Merging
Hybrid Encoding
50%
60%
70%
80%
90%
100%
LSS
BEVFormer
OccNet
UniAD
PARA-Drive
PETRv2
HENet++ (Ours)
BEV Seg
Occupancy
3D Det
Multi-task 3D Perception 
Performance
End-to-end Driving
Collision Rate (‱)
Latency
0
50
100
150
200
250
300
Det
single
task
Seg
single
task
Occ
single
task
3 task
Decoder
Encoder
Fig. 1: HENet++ reduces the training cost of
simultaneously using high-resolution images and
long-sequence temporal data via Hybrid Encoding.
By integrating Hybrid Encoding, Joint Sparse and
Dense Encoding, and Pretrain based on Model
Merging, HENet++ achieves state-of-the-art multi-
task performance while attaining the lowest end-
to-end driving collision rate on nuScenes.
The third challenge is how to fully lever-
age multi-modal information and the capabili-
ties of advanced 3D perception models to build
end-to-end autonomous driving systems. Current
end-to-end autonomous driving approaches uti-
lize different subtask outcomes, employ diverse 3D
representations, and design varied planning mod-
ules, resulting in a considerable number of complex
designs. However, no unified paradigm has yet
been established. Meanwhile, most of these works
rely solely on visual sensors, while millimeter-wave
Radar has gradually become a mainstream config-
uration for intelligent vehicles in recent years due
to its low cost and ability to provide 3D position-
ing and object velocity information. Developing
end-to-end autonomous driving systems that incor-
porate millimeter-wave Radar is also a promising
research direction.
2


## Page 3

To address the aforementioned challenges, we
propose the HENet++
series. To address the
first challenge, we introduce Hybrid Encoding,
which utilizes a large neural network to encode
a small number of high-resolution frames and a
compact neural network to process long-sequence
low-resolution frames. This approach achieves
the advantages of both high resolution and long
temporal coverage at a relatively low computa-
tional cost. Through further development, our
proposed Hybrid Encoding is applicable to both
dense (e.g., BEV and voxel) and sparse feature
extraction, making it compatible with various
existing 3D feature extraction methods. For the
second challenge, we propose a multi-task BEV
feature encoding specifically designed for BEV
models. We further analyze the preferences of
different tasks and simultaneously extract both
sparse and dense features—providing sparse fea-
tures for sparse tasks (e.g., 3D object detection)
and voxel features for dense tasks (e.g., BEV
semantic segmentation or occupancy prediction).
This approach achieves leading multi-task per-
ception performance on the nuScenes dataset.
Additionally, we introduce a model-merging-based
pre-training strategy, which further enhances multi-
task accuracy. To tackle the third challenge, we
build upon the HENet++ multi-task perception
model and further refine it into an end-to-end
autonomous driving model. This model can pre-
dict future movements of objects in the scene and
generate future trajectory plans for the ego vehicle.
Moreover, our framework supports multi-modal
input from millimeter-wave radar and multiple
cameras, achieving a lower collision rate on the
nuScenes dataset than existing methods.
The contributions of this work can be summa-
rized as follows:
1) We propose HENet, which is based on multi-
view camera inputs and dense BEV features.
Through the Hybrid Encoding, a U-shaped
temporal BEV fusion module, and indepen-
dent BEV encoding, it simultaneously pre-
dicts 3D object detection and BEV semantic
segmentation.
2) Building upon the HENet model, we intro-
duce the HENet++ perception framework.
By simultaneously hybrid encoding for sparse
foreground features and dense background
voxel features, the framework enables end-
to-end prediction for 3D object detection,
BEV semantic segmentation, and occupancy
semantic segmentation, providing suitable fea-
tures for each task. In addition, we introduce
a model-merging-based pre-training strategy
that further enhances multi-task accuracy.
HENet++ achieves state-of-the-art end-to-
end multi-task perception performance on the
nuScenes dataset.
3) Based
on
the
HENet++
perception
framework,
we
further
design
an
end-
to-end autonomous driving model. Lever-
aging
the
extracted
sparse
foreground
features and dense background features,
HENet++ employs an attention-based world-
prediction module to simultaneously perform
prediction and ego-vehicle trajectory plan-
ning. HENet++
is the first work that
leverages Radar and Camera for end-to-end
autonomous driving. On the nuScenes dataset,
the HENet++ model achieves a lower colli-
sion rate compared to existing methods.
2 Related work
2.1 Multi-View 3D Object Detection
3D object detection is a classic 3D perception
task, aiming to predict the 3D bounding boxes of
objects and determine the category and confidence
of each predicted object. Early methods primar-
ily predict objects from monocular images [4–11].
In recent years, multi-view cameras have become
standard sensors on autonomous vehicles, offering
richer perceptual information. Current multi-view
3D object detection approaches can be broadly
categorized into two types based on view trans-
formation strategies: BEV-based methods [12–23]
and sparse query-based methods [24–33].
BEV-based Methods. BEVDet [12] employs
the Lift-Splat-Shoot (LSS) [34] method to con-
struct BEV features from multi-view image fea-
tures using depth prediction. To mitigate inaccu-
rate depth estimation in BEVDet, BEVDepth [13]
incorporates camera parameters into the depth
prediction network and enriches depth supervi-
sion with LiDAR point clouds. BEVDet4D [14]
integrates
temporal
information
by
aligning
BEV features across consecutive frames via ego-
motion transformation. Building upon BEVDepth,
BEVStereo [15] and STS [22] introduce tempo-
ral stereo techniques to refine depth estimation
3


## Page 4

accuracy. For long-term temporal modeling, BEV-
Former [20] and Polarformer [19] treat BEV
features as queries and apply cross-attention
to aggregate historical frame information. BEV-
Formerv2 [21] further enhances BEVFormer by
incorporating perspective view supervision. SOLO-
Fusion [16] proposes a hierarchical fusion strategy
that first combines short-term BEV features before
integrating long-term sequences. HoP [23] designs
a plug-and-play historical object prediction mod-
ule compatible with various temporal 3D detectors.
AeDet [17] introduces azimuth-equivariant convo-
lutions and anchor designs to achieve consistent
BEV representations across different orientations.
Sparse
Query-based
Methods.
DETR3D [25] first extends DETR [35] by uti-
lizing sparse 3D object query to index features.
PETR [26] enhances DETR3D by aggregating
image features with 3D position information,
and PETRv2 [27] further introduces temporal
information into 3D position embedding to allow
temporal alignment for object positions. 3D-
MAN [28] designs an alignment and aggregation
module to extract temporal features from the
memory bank that stores information generated
by a single frame detector. Sparse4D [29] assigns
and projects 4D keypoints to generate different
views, scales, and timestamps. Sparse4Dv2 [30]
improves the temporal fusion module to reduce
the computational complexity and enable long-
term fusion. StreamPetr [31] presents an efficient
intermediate representation to transfer temporal
information, like BEV-based methods, to avoid
repeated calculation of features. Far3D [33] uses
a perspective-aware aggregation module to cap-
ture features of long-range objects and designs a
denoising method to improve query propagation.
SparseBEV [32] designs a scale-adaptive self-
attention module for query feature interaction and
proposes spatio-temporal sampling and adaptive
mixing to aggregate temporal features into current
queries.
3D object detection primarily focuses on fore-
ground objects, and Sparse Query-based Meth-
ods hold distinct advantages over BEV-based
approaches. This advantage may stem from the
inherently sparse nature of object detection out-
comes. Even when dense features are extracted,
the process still requires subsequent extraction
of sparse object features from them. Additional
processing steps—such as depth estimation, pro-
jection, and heatmap clustering—introduce more
cumulative errors. Therefore, Sparse Query-based
Methods, which directly extract object features,
tend to achieve superior performance.
2.2 BEV Semantic Segmentation
As the name suggests, BEV Semantic Segmenta-
tion aims to predict a dense map from a bird’s-eye
view perspective, where each grid cell is assigned
a semantic label. Numerous studies [34, 36–39] fol-
low a paradigm similar to BEVDet [12], differing in
their task-specific heads. VPN [39] trains its model
in synthetic 3D environments and applies domain
adaptation for real-world deployment. M2BEV [40]
effectively transforms multi-view 2D image features
into 3D BEV representations within ego-vehicle
coordinates, enabling a unified encoder for multi-
ple tasks. CVT [41] leverages cross-view attention
to implicitly learn perspective-to-BEV mappings,
incorporating camera-specific positional embed-
dings based on calibration parameters. HDMap-
Net [42] encodes multi-view image features to
predict vectorized map elements directly in BEV
space.
Unlike 3D object detection, BEV semantic seg-
mentation mainly focuses on background map
elements. Its final step involves decoding cate-
gories from BEV features, and therefore, the core
methodology of BEV semantic segmentation pre-
dominantly utilizes BEV feature maps as its 3D
representation.
2.3 Occupancy Prediction
Occupancy perception aims to divide space into 3D
grids and predict whether each grid is occupied by
any object. It was initially proposed to represent
irregularly shaped objects, while subsequent works
have further extended this by assigning seman-
tic labels to each occupied grid. MonoScene [43]
represents a pioneering approach relying solely on
RGB inputs. TPVFormer [44] integrates multi-
view camera inputs and employs transformer-based
architecture to project features into tri-perspective
view representation. SurroundOcc [45] extends
high-dimensional BEV features into occupancy rep-
resentations through direct spatial cross-attention
for geometric modeling. VoxFormer [46] proposes
a two-stage transformer framework for semantic
4


## Page 5

scene completion, generating complete 3D volu-
metric semantics from 2D images. FlashOcc [47]
transforms channels into height dimensions, effi-
ciently lifting BEV representations to 3D space
with significantly improved computational perfor-
mance. FBOcc [48] introduces a front-to-back view
transformation module to overcome limitations of
conventional view transformations. UniOcc [49]
and RenderOcc [50] utilize NeRF [51] for direct
3D semantic occupancy prediction, though ren-
dering speed constrains their practical efficiency.
FastOcc [52] enhances the occupancy prediction
head to achieve accelerated inference. COTR [53]
constructs compact 3D occupancy representations
through explicit-implicit view transformation and
coarse-to-fine semantic grouping.
Occupancy prediction focuses on both fore-
ground and background elements in a scene, and
captures more content than BEV semantic seg-
mentation. By nature, occupancy is essentially
a dense 3D semantic segmentation task. There-
fore, similar to how object detection favors sparse
features, occupancy prediction tends to perform
better with dense representations such as BEV or
voxel features.
2.4 End-to-end Multi-task Learning
End-to-end multi-task learning aims to solve multi-
ple tasks, including those mentioned above, within
a single model. It eliminates redundant compu-
tations and holds significant practical value. A
limited number of studies have explored multi-
task perception, including 3D object detection and
BEV segmentation [38, 39, 54, 55]. Current works
often follow the joint training strategy of BEV-
Former [20], which generates a unified BEV feature
map for detection and segmentation. PETRv2 [27]
initializes two query sets for detection and seg-
mentation tasks and sends each query set to the
corresponding task heads. These works show con-
flicts arising when combining 3D object detection
and BEV segmentation.
ST-P3 [56] first integrates perception, predic-
tion, and planning into an end-to-end framework.
This category of tasks, which takes sensor infor-
mation as input and directly outputs the ego
vehicle’s planned trajectory or control signals,
is referred to as end-to-end autonomous driving.
UniAD [57] adopts a feature extraction approach
similar to BEVFormer [20], with relatively com-
plex feature or result passing among task-specific
decoders. VAD [58] achieves trajectory planning
by representing the driving scene in a fully vec-
torized manner. PARA-Drive [1] first explored
the use of LiDAR and cameras for end-to-end
autonomous driving and noted that overly com-
plex connections among multiple tasks should be
avoided to prevent cumulative errors. GenAD [2]
first extracts BEV features, then extracts sparse
detection and sparse mapping features from them,
and further performs planning. SparseDrive [3]
directly extracts sparse detection and sparse map-
ping features from image features, thereby reducing
cumulative errors and improving prediction perfor-
mance. MomAD [59] proposed a momentum-aware
planning approach to enhance prediction and plan-
ning outcomes. BridgeAD [60] leverages historical
prediction and planning trajectories to improve
planning results. DiffusionDrive [61] designed a
truncated diffusion model to generate diverse can-
didate trajectories. The works mentioned above
propose various multi-task paradigms. Compared
to dense features, purely sparse 3D features only
focus on foreground categories such as vehicles
and lane lines, resulting in insufficiently compre-
hensive information. However, approaches entirely
based on dense features still require extracting
object instances from them. As analyzed in Section
2.1, their prediction accuracy is inferior to directly
extracting sparse features. Our proposed method
not only extracts dense features of the entire
scene, constrained by the occupancy task, but also
extracts sparse features of foreground objects, con-
strained by 3D object detection, thereby leveraging
more comprehensive information for prediction
and planning. Meanwhile, HENet++ is the first
framework that leverages Radar and Camera for
end-to-end autonomous driving.
3 HENet: Hybrid Encoding
and Multi-task Perception
for BEV Paradigm
As shown in Figure 2, the HENet
framework
comprises three stages. Given temporal multi-view
image inputs, a hybrid image encoding network
uses image encoders of varying complexity to
extract long-sequence BEV features and short-
term BEV features. We then leverage a temporal
5


## Page 6

Long-term Sequence
III. Independent BEV 
Feature Encoding
Short-term Sequence 
Large Backbone 
& FPN
Small Backbone 
& FPN
can use the same network and share parameters
Complex 2D-to-BEV 
Network
Simple 2D-to-BEV 
Network
×k
×(n-k)
based on depth
or query
based on depth
or query
I. Hybrid Image Encoding Network
II. Temporal 
Feature 
Integration
Feature 
Selection 
& BEV Encoder
Feature 
Selection 
& BEV Encoder
3D Object
Detection Head
BEV Semantic 
Segmentation 
Decoder
{𝐼𝐼𝑡𝑡
𝑣𝑣=1,…,6, 𝐼𝐼𝑡𝑡−1
𝑣𝑣=1,..,6, … , 𝐼𝐼𝑡𝑡−𝑘𝑘+1
𝑣𝑣=1,…,6}
{𝐼𝐼𝑡𝑡−𝑘𝑘
𝑣𝑣=1,…,6, 𝐼𝐼𝑡𝑡−𝑘𝑘−1
𝑣𝑣=1,…,6, … , 𝐼𝐼𝑡𝑡−𝑛𝑛+1
𝑣𝑣=1,…,6}
Fig. 2: Overall architecture of HENet. I) Hybrid Image Encoding Network uses image encoders of
varying complexity to encode long-sequence frames and short-term images, respectively. II) Temporal
Feature Integration module fuses multi-frame features from the various encoders. III) Independent BEV
Feature Encoding prepares separate BEV feature maps for different tasks.
feature integration module, incorporating an atten-
tion mechanism, to aggregate the multi-frame
BEV features. Subsequently, the BEV features at
different grid resolutions are distributed to ded-
icated encoders and decoders for each specific
task, ultimately yielding the multi-task perception
results.
3.1 Hybrid Image Encoding Network
As shown in Fig. 2, the hybrid image encoding
network employs two image encoders of distinct
complexities to process different temporal inputs.
The first encoder handles high-resolution short-
term frames, passing them through a large image
backbone(e.g., VoVNetV2-99 [62]) and a feature
pyramid network (FPN) [63], and subsequently
applies a complex 2D-to-BEV network to gen-
erate high-precision BEV features. Specifically,
we choose BEVStereo [15] as the complex 2D-to-
BEV network. The second encoder processes long-
term sequences by down-sampling the inputs to
low resolution, using a lightweight backbone(e.g.,
ResNet-50 [64]) with FPN for efficient feature
extraction, followed by a simplified 2D-to-BEV
module. Specifically, we choose BEVDepth [13] as
the lightweight 2D-to-BEV network. Both path-
ways employ BEVPoolv2 [65] to project frustum
Algorithm 1 Pseudo-code for Section 3.2
Input: A series of BEV features {f−n+1, ..., f−1, f0}. f0
represents BEV feature of the current frame and f−i
corresponds to the ith frame before f0.
for i from 0 to n-2 do
f−(i+1) ←AFFM(f−i, f−(i+1))
end for
for i from n-2 to 0 do
f−i ←AFFM(f−(i+1), f−i)
end for
return f0
features into multi-scale BEV representations.
Based on our experimental analysis, we use BEV
feature maps with resolutions of 256×256 and
128×128 for 3D object detection and BEV seman-
tic segmentation, respectively. Some parts of the
hybrid image encoders can be shared. For exam-
ple, we can use a single backbone(e.g., a single
ResNet-50) with different 2D-to-BEV networks.
3.2 Temporal Feature Integration
Following the extraction of multi-frame BEV
features by the hybrid image encoding network, we
fuse them using a temporal integration module, as
illustrated in Fig. 3. This module operates through
complementary backward and forward processes.
The backward process propagates features from the
current frame to past frames, whereas the forward
6


## Page 7

II. Temporal Feature Integration
…
Temporal Integration Module
A
A
…
A
A
A
A
…
…
A
A
A
Adjacent Frame Fusion Module (AFFM) 
t-n+1
t-k
t-k+1
t
…
BEV feature
sequence
t-n+1
t-k
t-k+1
t
t-n+1
t
…
…
Temporal Integration Module
…
…
…
BEV features 
of different 
grid sizes
t-1
t
t-2
t-3
(b) Adjacent Conv or Attention
t-1
t
t-2
t-3
(a) Global Conv or Attention
Fig. 3: Architecture of Temporal Feature Integration module. We propose the adjacent frame
fusion module (AFFM) and adopt the temporal fusion strategy with temporal backward and forward
processes.
III. Independent BEV Feature Encoding
Adaptive Feature Selection
Sigmoid
Channel-wise Multiply
Global
Avg Pool
Conv 1x1
BEV Encoder
FPN
BEV Encoder
Adaptive Feature Selection
3D Object
Detection Head
BEV Semantic 
Segmentation 
Decoder
Resnet Blocks
Fig. 4: Design of Independent BEV Feature Encoding. Each task decoder is provided with BEV
feature maps in different grid sizes through independent adaptive feature selection and BEV encoding.
process aggregates features from past frames to the
current one. Each step in these processes employs
a weight-sharing Adjacent Frame Fusion Module
(AFFM) that uses a cross-attention mechanism to
fuse BEV features from two adjacent frames. The
pseudo-code for this entire procedure is provided
in Algorithm 1. Specifically, given BEV features
from two frames, fi and fj, the AFFM operation
can be formulated as:
AFFM(fi, fj) =fj + γ × Avg(Atn(⟨fi, fj⟩, fi, fi),
Atn(⟨fi, fj⟩, fj, fj)),
(1)
where Avg(·) represents average operator, γ is
a learnable scaling parameter, ⟨·, ·⟩denotes con-
catenation, and Atn(·, ·, ·) is a cross attention
module:
Atn(q, k, v) = softmax(qk⊤
√
d
)v.
(2)
In the backward process, j = i −1, while in the
forward process, j = i + 1.
As shown in Fig. 3, adjacent attention reduces
noise compared to global attention or cross-frame
7


## Page 8

Long-term Sequence
Short-term Sequence 
Large Backbone 
& FPN
Small Backbone 
& FPN
can use the same network and share parameters
Hybrid Encoding for
Dense Voxel Feature
Hybrid Encoding for
Sparse Instance Feature
HENet++
3D Object
Detection Head
BEV Semantic 
Segmentation 
Decoder
{𝐼𝐼𝑡𝑡
𝑣𝑣=1,…,6, 𝐼𝐼𝑡𝑡−1
𝑣𝑣=1,..,6, … , 𝐼𝐼𝑡𝑡−𝑘𝑘+1
𝑣𝑣=1,…,6}
{𝐼𝐼𝑡𝑡−𝑘𝑘
𝑣𝑣=1,…,6, 𝐼𝐼𝑡𝑡−𝑘𝑘−1
𝑣𝑣=1,…,6, … , 𝐼𝐼𝑡𝑡−𝑛𝑛+1
𝑣𝑣=1,…,6}
×k
×(n-k)
FFN
Attn
K,V
Attn
K,V
Occupancy
Decoder
Fig. 5: Overall architecture of HENet++. By simultaneously hybrid encoding for sparse foreground
features and dense background voxel features, the framework enables end-to-end multi-task prediction.
In addition, we introduce a model-merging-based pre-training strategy that further enhances multi-task
performance.
convolutions. This enables the AFFM to align mov-
ing objects and suppress redundant background
information.
3.3 Independent BEV Feature
Encoding
To mitigate conflicts between tasks, HENet pro-
poses a preliminary solution that provides separate
BEV feature maps for different tasks. Based on
our empirical analysis in [66], different tasks prefer
different sizes of BEV features. Thus, after obtain-
ing the fused multi-scale BEV features, we first
assign different-sized BEV features to other tasks.
We then independently encode the BEV features
for each task. Inspired by BEVFusion [67], the pro-
posed encoding process comprises adaptive feature
selection and BEV encoding. Specifically, the adap-
tive feature selection fadaptive(·) applies a channel
attention module to select important features:
fadaptive(F) = σ (Wfavg(F)) · F,
(3)
where F ∈RX×Y ×C is the BEV features, W
denotes linear transform matrix, favg indicates the
global average pooling, and σ represents the Sig-
moid function. For the BEV encoder, we adopt
three ResNet [64] residual blocks and a simple
FPN [63] to perform local feature integration on
the BEV feature map. Notably, the adaptive fea-
ture selection and BEV encoders for different
tasks employ the same architecture but maintain
independent weights.
3.4 Decoders and Losses
Our model employs CenterPoint [68] as the 3D
object detection decoder, with its classification
and regression losses denoted as Lcls and Lbbox,
respectively. For BEV semantic segmentation, we
use a SegNet-based decoder [69] optimized with
focal loss Lseg. Additionally, a binary cross-entropy
loss Ldepth is applied for depth estimation. The
total loss is a weighted sum:
L =αdepthLdepth + αclsLcls+
αbboxLbbox + αsegLseg
(4)
, where α is a balancing weight.
8


## Page 9

Long-term Sequence
Short-term Sequence 
Large Backbone & 
FPN
Small Backbone & 
FPN
Proposal Pillars & Features
Hybrid Image Encoding Network (Sparse)
{𝐼𝐼𝑡𝑡
𝑣𝑣=1,…,6, 𝐼𝐼𝑡𝑡−1
𝑣𝑣=1,..,6, … , 𝐼𝐼𝑡𝑡−𝑘𝑘+1
𝑣𝑣=1,…,6}
{𝐼𝐼𝑡𝑡−𝑘𝑘
𝑣𝑣=1,…,6, 𝐼𝐼𝑡𝑡−𝑘𝑘−1
𝑣𝑣=1,…,6, … , 𝐼𝐼𝑡𝑡−𝑛𝑛+1
𝑣𝑣=1,…,6}
×L
Scale-adaptive Self Attention
Spatio-temporal 
Sampling
Spatio-temporal 
Sampling
Adaptive Mixing
Adaptive Mixing
Add & Norm
Add & Norm
Instance Fusion
Feed-Forward Network
Add & Norm
Sparse Features
Add & Norm
Reg Head
Reg Head
Cls Head
3D Object
Detection Head
Fig. 6: Design of Hybrid Image Encoding Network for sparse feature extraction.
4 HENet++: Hybrid Encoding
and Multi-task Perception
for A Dense-Sparse
Collaborative Framework
4.1 Overall framework: Joint Sparse
and Dense Encoding
Based on further analysis of the characteristics of
different tasks in existing work, we have identified
potential underlying causes of multi-task conflicts.
The output of tasks such as 3D object detection
is inherently sparse. Even if dense features are
extracted, sparse object features must still be dis-
tilled from the dense features. Additional steps,
such as depth estimation, projection, and heatmap
clustering, introduce more cumulative errors. Con-
sequently, sparse tasks favor sparse query-based
architectures that directly extract instance fea-
tures. Similarly, tasks such as BEV semantic
segmentation and occupancy prediction produce
dense outputs, making them more compatible with
BEV or Voxel-based architectures.
To enhance multi-task accuracy and obtain
more comprehensive foreground and background
information, we propose the HENet++ framework,
building upon the HENet framework. As shown
in Figure 5, HENet++ innovatively introduces
the simultaneous extraction of sparse foreground
features and dense panoramic features. To achieve
this, we extend hybrid encoding to be compati-
ble with both sparse and dense feature extraction.
Furthermore, by employing a pre-training strategy
based on multi-task model consolidation, we can
further improve multi-task performance.
4.2 Hybrid Encoding for Sparse
Instance Feature
As shown in Figure 5, Hybrid Encoding employs
two backbones and FPNs to extract 2D feature
maps from short-term high-resolution images and
long-term low-resolution images, further deriving
sparse instance features and dense voxel features
from them. The method for extracting voxel
features is identical to the approach described
in Section 3.1 and Section 3.2, which involves two
2D-to-BEV networks and a U-shaped Temporal
Feature Integration module.
Regarding the method for extracting sparse
features, we have made modifications based on
SparseBEV [32]. Similarly, we adopt learnable ini-
tialization and Scale-adaptive Self-Attention to
9


## Page 10

initialize queries q ∈RN×d:
q = LayerNorm(Q+Softmax(QKT
√
d
−τD)V ), (5)
where Q, K, V ∈RN×d is the query itself, N refers
to the number of queries, d is the channel dimen-
sion, and τ is a scalar to control the receptive
field for each query. These queries are simultane-
ously used to query both short-term and long-term
features.
Supposing there are k frames for the short-
term image features fshort, n −k frames for
the long-term encoder flong, and S sampling
points per frame, Two separate Spatio-temporal
Sampling [32] respectively extract two sets of
sampling features Pshort ∈Rk×S×C and Plong ∈
R(n−k)×S×C from the image features. Next, obtain
the short-term instance feature q
′
short ∈RN×d
and the long-term instance feature q
′
long ∈RN×d
through Adaptive Mixing:
⟨qshort, qlong⟩= ReLU(LayerNorm(
⟨Pshort, Plong⟩· LinearC×C(⟨q, q⟩))),
(6)
q
′
short = ReLU(LayerNorm(
qT
short · LinearkS×kS(q))),
(7)
q
′
long = ReLU(LayerNorm(
qT
long · Linear(n−k)S×(n−k)S(q))),
(8)
where the network weights for Channel Mixing
(Equation 6) are shared between long-term and
short-term features, while Point Mixing (Equation
7 and 8) employs two separate networks for long-
term and short-term features, respectively. q
′
short
and q
′
long are fed into an FFN before proceeding to
the next iteration of Self-Attention, Sampling, and
Mixing, repeating this process until L iterations
are completed.
After L iterations, N short-term instance
features and N long-term instance features are
extracted. Although they were initially one-to-one
corresponding in the original queries q, the regions
each query attends to continuously shift during
the attention process, potentially resulting in dif-
ferent instances being matched. Additionally, there
may be overlaps between these two sets of features.
Therefore, directly merging them into N features
or simply concatenating them into 2N features is
unreasonable. Here, we employ the regression head
from the 3D object detection head, using this MLP
to decode the bounding boxes of instances, and
perform deduplication, similar to non-maximum
suppression, to identify multiple features corre-
sponding to the same instance. For each instance,
the associated C-dimensional feature vectors are
fused into a single vector via channel-wise max
pooling.
4.3 Pretrain based on Model
Merging
In the training process of a multi-task model, how
to initialize the parameters is also very important.
During our experiments, we found that using the
encoder parameters from a model pre-trained on
a single 3D task and loading the corresponding
decoder parameters leads to faster convergence
and higher accuracy compared to loading back-
bone and neck parameters pre-trained on 2D tasks.
However, since the multi-task model shares the
same encoder, determining which single-task model
should be used to provide the pre-trained weights
for the encoder is a question worth investigating.
Experiments show that when using a 3D object
detection model to initialize the encoder, the result-
ing multi-task model achieves higher accuracy in
3D object detection, while the accuracy of other
tasks decreases. Similarly, when using a single-task
occupancy model for pre-training, the occupancy
accuracy is higher, but the accuracy of other tasks
is reduced.
Algorithm 2 Model Merge for Pretrain, Modified
from [70]
Input: Single-task encoder f1..K, Number of linear layers
J, inner product matrices G(j)
i
= X(j)T
i
X(j)
i
for all linear
layers 1 ≤j ≤J and single-task encoder 1 ≤i ≤K, Scaling
factor of non-diagonal items α
for j in 1, 2, ..., J do
W (j)
1
, W (j)
2
..., W (j)
K
←getWeights(f1..K, j)
Reduce non-diagonal items of inner product matrices G(j)
i
as ˜
G(j)
i
←αG(j)
i
+ (1 −α)diag(G(j)
i
)
W (j)
M
←(Pi∈K
i
˜
G(j)
i
)−1 Pi∈K
i
( ˜
G(j)
i
W (j)
i
) and set the
weight as W (j)
M
in fM
end for
Average weights as WM =
1
K
Pi∈K
i
Wi for weights other
than linear weights in fM
Model merging, which used in natural language
processing, combines multiple single-task models
10


## Page 11

2D Encoder
LE1
3D Object Detection
Large Model
2D-to-Sparse
TS1
Decoder
OD1
2D Encoder
SE1
3D Object Detection
Small Model
2D-to-Sparse
TS2
Decoder
OD2
2D Encoder
LE2
BEV Segmentation
Large Model
2D-to-Dense
TD1
Decoder
BSD1
2D Encoder
SE2
BEV Segmentation
Small Model
2D-to-Dense
TD2
Decoder
BSD2
2D Encoder
LE3
Occupancy
Large Model
2D-to-Dense
TD3
Decoder
OCD1
2D Encoder
SE3
Occupancy
Small Model
2D-to-Dense
TD4
Decoder
OCD2
Model Merge
2D Encoder
LE1+LE2+LE3
2D Encoder
SE1+SE2+SE3
2D-to-Sparse
TS1+TS2
2D-to-Dense
TD1+TD2+TD3+TD4
Decoder
OD1+OD2
Decoder
BSD1+BSD2
Decoder
OCD1+OCD2
Fig.
7:
The
merging
process
of
the
HENet++ pre-trained models.
into one for direct multi-task inference. We also
attempted to apply model merging methods like
Regmean [70] directly to 3D vision multi-task learn-
ing, but it performed poorly. This is likely due
to the complex architectures and task representa-
tions in 3D vision models. However, inspired by
this approach, we consolidated the encoder weights
from multiple single-task models into a single
encoder and used it as a pre-trained initialization,
which achieved promising results.
The model merging method is outlined in Algo-
rithm 2. Specifically, for the weight matrices in
convolutional networks and linear layers, we apply
Regression Mean. For other learnable parameters,
we directly compute their average. The architec-
tural design of HENet++
involves three tasks.
Each task processes both short-term and long-
term components, which are inherited from two
differently sized models, respectively. The process
of merging these models to serve as multi-task
pre-training is illustrated in Figure 7.
4.4 Decoders and Losses
Our model employs two separate MLPs to pre-
dict object categories and bounding boxes from
the sparse features. The classification loss is Focal
Loss, denoted as Lcls, and the bounding box loss
is L1 Loss, denoted as Lbbox For BEV semantic
segmentation, we use a SegNet-based decoder [69]
optimized with focal loss Lseg. For Occupancy, we
use a simple MLP as decoder with focal loss Locc.
Additionally, a binary cross-entropy loss Ldepth is
applied for depth estimation. The total loss is a
weighted sum:
L =αdepthLdepth + αclsLcls + αbboxLbbox
+ αsegLseg + αoccLocc
(9)
, where α is a balancing weight.
5 End-to-End Autonomous
Driving Based on HENet++
As
shown
in
Figure
8,
we
extend
the
HENet++
framework to address end-to-end
autonomous driving. We design a simple yet
effective iterative prediction and planning decoder.
Compared to existing methods that rely solely on
a single form of 3D features, HENet++ can lever-
age more comprehensive information for planning.
Sparse instance features provide learnable queries
for object motion prediction, serving as the foun-
dation for both prediction and planning, while
dense panoramic features offer more complete
scene information.
Specifically,
the
prediction
and
planning
decoder of HENet++
employs N Transformer
layers for iterative prediction. Before the itera-
tion begins, the top-K 3D object detection results
with the highest confidence scores, along with their
instance features Fdet, are first taken. The posi-
tional encodings of their bounding box centroids
are concatenated to form K vectors F1,2,...,K. The
historical trajectory of the ego vehicle, navigation
waypoints, acceleration, velocity, and other infor-
mation are passed through a linear layer to project
them into higher dimensions, and the positional
encoding of the origin is concatenated to obtain
the ego vehicle vector F0. The occupancy grid net-
work and voxel features are downsampled, and then
the semantic category and features of each grid
are concatenated in the channel dimension with
the positional encoding of the grid coordinates to
obtain the occupancy grid tokens Focc. The ini-
tial query is defined as Q0 = ⟨F0, F1,2,...,K⟩. In the
i-th iteration, Qi−1 is used as the initial query.
It then undergoes self-attention on Qi−1, cross-
attention with Q0 as key-value, cross-attention
with Focc as key-value, and a feed-forward net-
work to produce Qi. Meanwhile, the output of each
11


## Page 12

Occupancy Result 
+ Voxel Feature
3D Detection Bboxes
+ Instance Feature
Position 
Embedding
Position 
Embedding
Ego car Information
Linear
(0, 0, 0)
Focc
Fego
Fdet
Qi
Self-Attention
Add & Norm
Cross-Attention
Add & Norm
Cross-Attention
Add & Norm
FFN
Add & Norm
x N
Trajectory
MLP
Q, K, V
Q
K, V
Q
K, V
Hybrid 
Backbone & Neck
Radar
Point Clouds
Multi-View
Images
Occupancy
Head
3D Detection
Head
Prediction & 
Planning
Trajectories
HENet++ Prediction & Planning Decoder
Hybrid 
Depth & Voxel
Encoding
Hybrid 
Sparse Feature
Encoding
Radar Encoder
Fig. 8: Architecture of the HENet++ End-to-end Autonomous Driving framework. We design
an attention-based trajectory planner that utilizes instance features (including the ego vehicle’s features)
as queries, and instance features combined with panoramic dense features as key-value pairs, enabling
simultaneous iterative prediction of future states and ego planning. The compatibility of HENet++ with
both dense and sparse features also facilitates straightforward extension to multi-modal inputs.
layer is decoded by a trajectory MLP to obtain
the trajectory Traj0,1,...,K of each object. Traj0
represents the planned trajectory of the ego vehi-
cle, while Traj1,...,K represent the predictions for
the corresponding objects.
The HENet++ framework is compatible with
both sparse and dense features, enabling relatively
straightforward integration with existing multi-
modal feature fusion methods. For example, by uti-
lizing the Radar encoder from RCBEVDet++ [71]
along with the interpolation method described in
the paper, both sparse and dense Radar features
can be obtained. The CAMF module in [71] can
be further employed to integrate Radar features
into the end-to-end model.
Denoting the perception Loss in Section 4.4
as Lprec, the end-to-end model introduces three
additional losses. The first is the L1 loss between
the ego vehicle’s future trajectory and the ground
truth, denoted as Lplan. The second is the L1 loss
between the future trajectories of other objects
and their ground truth, denoted as Lpred. Each
trajectory Traji consists of t future coordinate
points in the horizontal Cartesian coordinate sys-
tem: {(xi1, yi1), (xi2, yi2), ..., (xit, yit)}. The third
is a collision constraint Lcol, defined as follows:
D(Traja, Trajb, ti) =
p
(xati −xbti)2 + (yati −ybti)2,
(10)
P(Traja, Trajb, ti) =





3 −D(Traja, Trajb, ti),
if D(Traja, Trajb, ti) < 3
0,
else
,
(11)
Lcol =
K
X
i=1
t
X
j=1
P(Traj0, Traji, tj).
(12)
The total loss is a weighted sum:
L =Lprec + αplanLplan + αpredLpred + αcolLcol
(13)
, where α is a balancing weight.
6 Experiments
6.1 Implementation Details
We train HENet in end-to-end manner for multi-
tasks, including 3D object detection and BEV
12


## Page 13

Table 1: Comparison of end-to-end multi-task learning on the nuScences val set. Time/E
represent the training time per epoch with FP32 on 8×A800 GPUs. mIoUv, mIoUa, and mIoUd
represent the mIoU for vehicles, drivable area, and lane & road divider, respectively.
Methods
Backbone
Frames Time/E
Detection
BEV Segmentation
Occupancy
NDS↑mAP↑mIoU ↑IoUv ↑mIoUa ↑mIoUd ↑IoU ↑mIoU ↑
VPN [39]
ResNet50
1
-
33.4
25.7
43.8
37.3
76.0
18.0
-
-
LSS [34]
ResNet50
1
-
41.0
34.4
45.0
42.8
73.9
18.3
-
11.4
BEVFormer-S [20]
ResNet101
1
-
45.3
38.0
47.3
44.4
77.6
19.8
-
-
BEVFormer [20]
ResNet101
5
213min
52.0
41.2
49.4
46.7
77.5
23.9
-
30.5
OccNet [72]
ResNet101
5
230min
52.0
41.2
24.6
12.9
47.2
13.8
41.1
27.0
UniAD [57]
ResNet101
6
253min
49.9
38.2
-
-
69.1
25.7
62.3
-
PARA-Drive [1]
ResNet101
6
240min
48.0
37.0
-
-
71.0
33.0
63.6
-
HENet
R101 & R50
2 + 3
60min
56.4
47.1
53.9
44.5
77.0
40.1
-
-
HENet++
R101 & R50
2 + 3
82min
60.5
53.0
55.4
45.8
79.3
41.1
68.2
46.4
PETRv2 [27]
V2-99
2
75min
49.5
40.1
57.6
49.4
79.1
44.3
-
-
HENet
V2-99 & R50
2
58min
58.0
48.7
56.9
47.6
80.2
42.8
-
-
HENet
V2-99 & R50
2 + 7
71min
59.9
49.9
58.0
49.5
81.3
43.4
-
-
HENet++
V2-99 & R50 5 + 11
205min
63.7
56.7
58.3
49.6
81.8
43.7
70.8
47.3
Table 2: Comparison of End-to-end Autonomous Driving results on nuScenes val set. L2
refers to the L2 error between the predicted trajectory and the ground-truth trajectory of human driving.
Method
Input
Backbone
UniAD Metrics
VAD/STP3 Metrics
L2 (m) ↓
Collision Rate (%) ↓
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
1s
2s
3s
Avg.
1s
2s
3s
Avg.
ST-P3 [56]
C
EfficientNet-b4
1.72 3.26 4.86 3.28 0.44 1.08 3.01
1.51
1.33 2.11 2.90 2.11 0.23 0.62 1.27
0.71
OccNet [72]
C
ResNet101-DCN 1.29 2.13 2.99 2.14 0.21 0.59 1.37
0.72
-
-
-
-
-
-
-
-
UniAD [57]
C
ResNet101
0.48 0.96 1.65 1.03 0.05 0.17 0.71
0.31
0.45 0.70 1.04 0.73 0.62 0.58 0.63
0.61
VAD-Tiny [58]
C
ResNet50
0.60 1.23 2.06 1.30 0.31 0.53 1.33
0.72
0.46 0.76 1.12 0.78 0.21 0.35 0.58
0.38
VAD-Base [58]
C
ResNet101
0.54 1.15 1.98 1.22 0.04 0.39 1.17
0.53
0.41 0.70 1.05 0.72 0.07 0.17 0.41
0.22
PARA-Drive [1]
C
ResNet50
-
-
-
-
-
-
-
-
0.25 0.46 0.74 0.48 0.14 0.23 0.39
0.25
GenAD [2]
C
ResNet50
0.36 0.83 1.56 0.91 0.06 0.23 1.00
0.43
0.28 0.49 0.78 0.52 0.08 0.14 0.34
0.19
SparseDrive [3]
C
ResNet50
0.44 0.92 1.69 1.01 0.07 0.19 0.71
0.32
0.29 0.58 0.96 0.61 0.01 0.05 0.18
0.08
MomAD [59]
C
ResNet50
0.43 0.88 1.62 0.98 0.06 0.16 0.68
0.30
0.31 0.57 0.91 0.60 0.01 0.05 0.22
0.09
SSR [73]
C
ResNet50
0.24 0.65 1.36 0.75 0.00 0.10 0.36
0.15
0.18 0.36 0.63 0.39 0.01 0.04 0.12
0.06
BridgeAD-S [60]
C
ResNet50
-
-
-
-
-
-
-
-
0.29 0.57 0.92 0.59 0.01 0.05 0.22
0.09
BridgeAD-B [60]
C
ResNet101
-
-
-
-
-
-
-
-
0.28 0.55 0.92 0.58 0.00 0.04 0.20
0.08
DiffusionDrive [61]
C
ResNet50
-
-
-
-
-
-
-
-
0.27 0.54 0.90 0.57 0.03 0.05 0.16
0.08
HENet++
C
ResNet50
0.41 1.27 2.63 1.44 0.02 0.10 0.39
0.17
0.25 0.56 1.02 0.61 0.01 0.05 0.12
0.06
HENet++
RC
ResNet50
0.39 1.11 2.36 1.29 0.00 0.06 0.33 0.13 0.24 0.50 0.91 0.55 0.01 0.03 0.10 0.05
semantic segmentation in the same way as LSS [34].
We choose VovNet-99 [9, 62] with 640×1152 image
resolution for the large image encoder and select
ResNet-50 [64] with 256 × 704 image resolution
for the small image encoder, respectively. For the
input temporal sequence, we set short-term frame
number k = 2 and long-term frame number n = 9.
The weights of the hybrid image encoding network
are initialized from pre-trained 3D detectors. As
analyzed in [66], we choose BEV grid sizes of 0.4m
(256×256 BEV size) and 0.8m (128×128 BEV size)
for 3D object detection and BEV semantic seg-
mentation, respectively. The end-to-end multi-task
models are trained for 60 epochs without CBGS.
Besides, to further compare
HENetwith some
single-task methods, we train the single 3D object
detection models of
HENetfor 12 epochs with
CBGS [75].
For HENet++ , we choose VovNet-99 [9, 62]
with 640×1600 image resolution for the large image
encoder and select ResNet-50 [64] with 256 × 704
image resolution for the small image encoder, fol-
lowing [32]. For the input temporal sequence, we
set short-term frame number k = 5 and long-term
frame number n = 11. For the Hybrid Encoding for
sparse features, we set query number N = 900 and
layer number L = 6. We also separately trained
three single-task models with Hybrid Encoding,
13


## Page 14

Table 3: Comparison of 3D object detection results on the nuScences val set. ∗indicates the
result is benefited from the perspective pre-training. † indicates using one temporal frame information. ‡
denotes integrating two or more temporal frames. The best and second best results are marked in red and
blue.
Methods
Backbone
NDS↑mAP↑mATE↓mASE↓mAOE↓mAVE↓mAAE↓
BEVDet [12]
ResNet50
37.9
29.8
0.725
0.279
0.589
0.860
0.245
BEVDet4D [14]†
ResNet50
45.7
32.2
0.703
0.278
0.495
0.354
0.206
PETRv2 [27]†
ResNet50
45.6
34.9
0.700
0.275
0.580
0.437
0.187
BEVStereo [15]†
ResNet50
50.0
37.2
0.598
0.270
0.438
0.367
0.190
SOLOFusion [16]‡
ResNet50
53.4
42.7
0.567
0.274
0.511
0.252
0.181
Sparse4Dv2 [30]‡
ResNet50
53.9
43.9
0.598
0.270
0.475
0.282
0.179
StreamPETR [31]‡
ResNet50
54.0
43.2
0.581
0.272
0.413
0.295
0.195
SparseBEV [32]‡
ResNet50
54.5
43.2
0.606
0.274
0.387
0.251
0.186
HENet
‡
ResNet50
55.4
43.7
0.512
0.262
0.367
0.285
0.213
PETR [26]*
ResNet101-DCN
44.1
36.6
0.717
0.267
0.412
0.834
0.190
BEVDepth [13]*†
ResNet101
53.5
41.2
0.565
0.266
0.358
0.331
0.190
BEVFormer [20]*‡
ResNet101-DCN
51.7
41.6
0.673
0.274
0.372
0.394
0.198
HoP-BEVFormer [23]*‡
ResNet101-DCN
55.8
45.4
0.565
0.265
0.327
0.337
0.194
StreamPETR [31]*‡
V2-99
57.1
48.2
0.569
0.262
0.315
0.257
0.199
SOLOFusion [16]*‡
ResNet101
58.2
48.3
0.503
0.264
0.381
0.246
0.207
SparseBEV [32]*‡
ResNet101
59.2
50.1
0.562
0.265
0.321
0.243
0.195
Far3D [33]*‡
ResNet101
59.4
51.0
0.551
0.258
0.372
0.238
0.195
HENet
*‡
V2-99 & ResNet50
59.9
50.2
0.465
0.261
0.335
0.267
0.197
HENet++
*‡
V2-99 & ResNet50
65.1
57.3
0.506
0.252
0.182
0.225
0.195
Table 4: Comparison of 3D object detection results on nuScences test set. The best and second
best results are marked in red and blue. ‡uses test-time augmentation.
Methods
Backbone
NDS↑mAP↑mATE↓mASE↓mAOE↓mAVE↓mAAE↓
BEVDet4D [14]
Swin-B
56.9
45.1
0.511
0.241
0.386
0.301
0.121
PolarFormer [19]
V2-99
57.2
49.3
0.556
0.256
0.364
0.439
0.127
PETRv2 [27]
V2-99
58.2
49.0
0.561
0.243
0.361
0.343
0.120
HoP-BEVFormer [23]
V2-99
60.3
51.7
0.501
0.245
0.346
0.362
0.105
BEVDepth [13]
ConvNeXt-B
60.9
52.0
0.445
0.243
0.352
0.347
0.127
BEVStereo [15]
V2-99
61.0
52.5
0.431
0.246
0.358
0.357
0.138
SOLOFusion [16]
ConvNeXt-B
61.9
54.0
0.453
0.257
0.376
0.276
0.148
AeDet [17]
ConvNeXt-B
62.0
53.1
0.439
0.247
0.344
0.292
0.130
BEVFormerv2 [21]
InternImage-B
62.0
54.0
0.488
0.251
0.335
0.302
0.122
FB-BEV [74]
V2-99
62.4
53.7
0.439
0.250
0.358
0.270
0.128
StreamPETR [31]
V2-99
63.6
55.0
0.479
0.239
0.317
0.241
0.119
SparseBEV [32]
V2-99
63.6
55.6
0.485
0.244
0.332
0.246
0.117
Sparse4Dv2 [30]
V2-99
63.8
55.6
0.462
0.238
0.328
0.264
0.115
HENet
V2-99 & ResNet50
63.8
57.5
0.432
0.242
0.368
0.320
0.129
BEVFormerV2 [21]
InternImage-XL
64.8
58.0
0.448
0.262
0.342
0.238
0.128
BEVDet-Gamma [12] ‡
Swin-B
66.4
58.6
0.375
0.243
0.377
0.174
0.123
SparseBEV [32]
V2-99
67.5
60.3
0.425
0.239
0.311
0.172
0.116
StreamPETR-Large [31]
ViT-L
67.6
62.0
0.470
0.241
0.258
0.236
0.134
Hop [23]
ViT-L
68.5
62.4
0.367
0.249
0.353
0.171
0.131
Far3D [33]
ViT-L
68.7
63.5
0.432
0.237
0.278
0.227
0.130
HENet++
ViT-L & V2-99
70.7
64.5
0.402
0.235
0.237
0.155
0.129
each using the same settings as the multi-task
model. They were all trained on the nuScenes
training set for 12 epochs without CBGS. The
only exception is the large detection model on the
nuScenes test leaderboard, which employs 8-frame
ViT-L and 15-frame VovNet-99.
The HENet++ end-to-end autonomous driv-
ing model retained the top 200 detection results
and downsampled the voxels to 50 × 50 × 4. We
set the number of transformer layers N = 3. After
adding the Prediction & Planning Decoder to
the HENet++ perception model, this end-to-end
14


## Page 15

Table 5: Comparison of BEV semantic segmentation results on nuScences val set. The best
and second best results are marked in red and blue. For both the HENet and the HENet++ framework,
the BEV Segmentation single-task models are identical.
Methods
Backbone
mIoU ↑mIoUveh ↑mIoUarea ↑mIoUdiv ↑
VPN [39]
ResNet50
42.7
31.8
76.9
19.4
LSS [34]
ResNet50
46.5
41.7
77.7
20.0
BEVFormer [20]
ResNet101-DCN
50.2
44.8
80.1
25.7
FIERY [36]
ResNet-101
-
38.2
-
-
M2BEV [40]
ResNeXt-101
-
-
77.2
40.5
PETRv2 [27]
V2-99
60.3
46.3
85.6
49.0
HENet/HENet++
V2-99 & ResNet50
58.8
51.6
82.3
42.4
Table 6: Comparison of Occupancy results on the nuScenes-Occ3D benchmark. We present
the mean IoU over categories and the IoUs for different classes. The best and second best results are
marked in red and blue.
Method
Backbone
Visible Mask
mIoU↑
others
barrier
bicycle
bus
car
const. veh.
motorcycle
pedestrian
traffic cone
trailer
truck
drive. suf.
other flat
sidewalk
terrain
manmade
vegetation
TPVFormer [44]
R-50
✔
34.2
7.7 44.0 17.7 40.9 47.0 15.1 20.5 24.7 24.7 24.3 29.3 79.3 40.7 48.5 49.4 32.6 29.8
SurroundOcc [45]
R-101
✔
37.1
9.0 46.3 17.1 46.5 52.0 20.1 21.5 23.5 18.7 31.5 37.6 81.9 41.6 50.8 53.9 42.9 37.2
OccFormer [76]
R-50
✔
37.4
9.2 45.8 18.2 42.8 50.3 24.0 20.8 22.9 21.0 31.9 38.1 80.1 38.2 50.8 54.3 46.4 40.2
VoxFormer [46]
R-101
✔
40.7
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
-
FBOcc [74]
R-50
✔
42.1
14.3 49.7 30.0 46.6 51.5 29.3 29.1 29.4 30.5 35.0 39.4 83.1 47.2 55.6 59.9 44.9 39.6
PanoOcc [77]
R-101
-
42.1
11.7 50.5 29.6 49.4 55.5 23.3 33.3 30.6 31.0 34.4 42.6 83.3 44.2 54.4 56.0 45.9 40.4
FastOcc [52]
R-101
✔
40.8
12.9 46.6 29.9 46.1 54.1 23.7 31.1 30.7 28.5 33.1 39.7 83.3 44.7 53.9 55.5 42.6 36.5
BEVDet4D [14]
Swin-B
✔
42.5
12.4 50.2 27.0 51.9 54.7 28.4 29.0 29.0 28.3 37.1 42.5 82.6 43.2 54.9 58.3 48.8 43.8
FlashOcc [47]
Swin-B
✔
43.5
13.3 51.6 28.1 50.9 55.7 27.5 31.1 30.0 29.2 38.9 43.7 83.9 45.6 56.3 59.0 50.6 44.6
COTR [53]
Swin-B
✔
46.2
14.9 53.3 35.2 50.8 57.3 35.4 34.1 33.5 37.1 39.0 45.0 84.5 48.7 57.6 61.1 51.6 46.7
HENet++
R-50
✔
42.9
10.8 50.3 24.3 49.0 57.3 29.4 24.4 30.1 28.5 36.5 43.0 84.0 43.1 56.0 59.3 54.2 49.2
HENet++
V2-99 & R-50 ✔
48.2
13.7 58.2 28.6 57.7 60.8 34.0 33.4 39.9 34.1 46.8 52.1 84.4 46.7 58.3 61.6 58.6 51.0
autonomous driving model was fine-tuned for 10
epochs (without CBGS).
6.2 Dataset and Metrics
We evaluate our model on the nuScenes [78]
dataset, a large-scale autonomous driving dataset
containing 1,000 driving scenes (700 for training,
150 for validation, and 150 for testing), including
cities, highways, and rural roads. Each scene con-
tains various objects, such as vehicles, pedestrians,
and bicycles.
For 3D object detection evaluation, NuScenes
provides a set of evaluation metrics, including
mean Average Precision (mAP) and five true pos-
itive (TP) metrics: ATE, ASE, AOE, AVE, and
AAE for measuring translation, scale, orientation,
velocity, and attribute errors, respectively. The
overall performance is measured by the nuScenes
Detection Score (NDS), which is the composite
of the above metrics. For BEV semantic seg-
mentation, we use mean intersection over union
(mIoU) as the metric following the settings of
LSS [34]. For Occupancy, we use IoU to evalu-
ate binary occupancy results, i.e., whether a voxel
is occupied regardless of its semantic category.
Additionally, we use mIoU, the class-averaged IoU
metric, to evaluate semantic occupancy predictions.
For End-to-end Autonomous Driving, commonly
used evaluation metrics include the L2 distance to
expert human trajectories and the collision rate.
Models like UniAD [57] and VAD [58]/STP3 [56]
adopt different benchmarks, for instance, whether
to average over time and which object categories
are counted as collisions. We have conducted
evaluations on both benchmarks.
15


## Page 16

Table 7: Ablation of Hybrid Image Encoding Network on Detection Task. ‘Time’ denotes the
overall training time. ‘BS’ indicates the batch size. For A˜F, FPS is measured on RTX3090 GPU with
FP32. For H˜I, FPS is measured on A100-SMX4 GPU with FP32 and FP16 mixed precision. For A˜F,
Training cost (GPU memory and Time) is estimated on 8×Tesla A800 GPUs with FP32. For H˜I, Training
cost is estimated on 8×A100-SMX4 GPUs with FP32 and FP16 mixed precision.
Model
Backbone
Input
Frames
NDS mAP FPS GPU memory Time
A
BEVDepth4D
R18
640×1152
2 frames
48.6
34.8
14.3 31.2G / BS=64
14h
B
BEVDepth4D
R18
256×704
9 frames
48.6
34.9
21.7 22.9G / BS=64
14h
C
BEVDepth4D
R18
640×1152
9 frames
51.2
39.2
14.1 43.5G / BS=64
44h
A+B Model Ensemble
-
-
-
48.9
35.2
7.93
-
-
A+B HENet
R18 & R18
640×1152 & 256×704 2 + 7 frames
52.1
39.8
8.91 41.3G / BS=64
13h
D
BEVDepth4D
R50
256×704
9 frames
53.8
40.9
19.1 14.1G / BS=16
16h
E
BEVStereo
V2-99
640×1152
2 frames
58.2
48.0
4.52 37.0G / BS=16
48h
F
BEVStereo
V2-99
896×1600
2 frames
59.2
50.0
2.69 68.4G / BS=16
96h
D+E Model Ensemble
-
-
-
57.3
46.4
3.53
-
-
D+E HENet w/o AFFM V2-99 & R50 640×1152 & 256×704 2 + 7 frames
59.2
49.9
3.71 42.3G / BS=16
27h
D+E HENet
V2-99 & R50 640×1152 & 256×704 2 + 7 frames
59.9
50.2
3.65 43.5G / BS=16
27h
H
SparseBEV
R50
256×704
11 frames
55.8
45.2
31.1
14.7G / BS=8
17h
I
SparseBEV
V2-99
640×1600
8 frames
63.2
55.1
9.6
70.4G / BS=8
100h
H+I Model Ensemble
-
-
11 frames
60.8
52.7
7.3
-
-
H+I HENet++
V2-99 & R50 640×1600 & 256×704 5 + 6 frames
65.1
57.3
12.1
68.9G / BS=8
72h
6.3 Multi-task Results
We
compare
the
proposed
HENet
and
HENet++ with previous end-to-end multi-task
models on the nuScenes val sets in Table 1
and Figure 1. HENet++ shows favorable multi-
task performance and achieves state-of-the-art
results. Specifically, HENet++ outperforms BEV-
Former [20] by 11.0 NDS and 15.5 mAP on the
3D object detection task, 8.9 mIoU on the BEV
semantic segmentation task, and 15.9 mIoU on the
Occupancy task. As for PETRv2 [27], which shows
excellent BEV semantic segmentation performance,
our models surpass it by 14.2 NDS on the 3D object
detection task while maintaining competitive BEV
semantic segmentation performance. In addition,
we compare the training time per epoch (with the
same batch size) with these methods. HENet out-
performs all other methods with less training time,
showing the proposed HENet
is more efficient.
Moreover, HENet can use more frames to improve
performance, while other methods, like PETRv2,
cannot use 9 frames due to the limitation of GPU
memory.
We also compare the results of HENet++ for
end-to-end autonomous driving with other end-
to-end autonomous driving methods in Table 2.
Although HENet++ exhibits a higher L2 error
compared to human driving trajectories, this
does not imply a higher planning error rate, as
it achieves a lower collision rate than existing
method.
6.4 Single Task Results
Considering that many works on 3D perception
only predict single-task results, we conduct experi-
ments on single tasks and compare the results of
HENet with these task-specific models. Through
this comparison, we illustrate the superiority of
our Hybrid Image Encoding Network and Tempo-
ral Feature Integration, and further demonstrate
the effectiveness of HENet.
3D Object Detection Results. We present
the results of HENet and HENet++ for single
3D object detection task on the nuScenes val and
test sets in Table 3 and 4, respectively. As shown
in Table 3, HENet and HENet++ surpasses all
multi-view camera 3D object detection methods
under different backbone configurations, demon-
strating the effectiveness of the proposed hybrid
image encoding network and temporal feature inte-
gration module. Table 4 shows HENet++ achieves
state-of-the-art 3D object detection results. By
transitioning from the BEV paradigm to the sparse
paradigm, HENet++ achieves better 3D object
detection results than HENet. Meanwhile, when
comparing HENet++ with its primary baseline
SparseBEV, the results demonstrate that Hybrid
Encoding can effectively improve performance.
16


## Page 17

Table 8: Ablation of Hybrid Image Encoding Network on Multi-task. mIoUbev and mIoUocc
denote the mIoU for BEV semantic segmentation and semantic occupancy, respectively.
Model
Backbone
Input
Frames
NDS mIoUbev mIoUocc
A
BEVDepth4D
R50
256×704
9 frames
53.0
51.5
-
B
BEVStereo
V2-99
640×1152
2 frames
58.0
55.8
-
C
BEVStereo
V2-99
896×1600
2 frames
58.9
56.7
-
A+B HENet w/o AFFM V2-99 & R50 640×1152 & 256×704 2 + 7 frames
59.0
56.9
-
A+B HENet w/ AFFM
V2-99 & R50 640×1152 & 256×704 2 + 7 frames
59.9
58.0
-
D
HENet++ w/o HE
R50
256×704
9 frames
54.1
51.9
39.4
E
HENet++ w/o HE
V2-99
640×1600
8 frames
63.0
58.1
45.5
D+E HENet++
V2-99 & R50 640×1600 & 256×704 5 + 6 frames
63.7
58.3
47.3
Input
(a) BEVDepth4D
256x704  9 frames
(b) BEVStereo
900x1600  2 frames
(a+b)  HENet
2+7 frames
GT
route
route
Fig. 9: Visualization results of HENet and baselines on end-to-end multi-tasking. From left to
right, we show multi-view image inputs, results of BEVDepth4D, BEVStereo, and HENet (BEVDepth4D
+ BEVStereo), and the ground truth. The proposed HENet estimates occluded objects better through
long-term information and has more accurate predictions through high-resolution information.
BEV Semantic Segmentation Results.
We present the results of HENet for single BEV
semantic segmentation task on the nuScenes
val sets in Table 5. HENet obtain competitive
results compared to existing methods. In the
HENet++
framework, BEV semantic segmen-
tation is still decoded from dense features, and
the design of the BEV segmentation single-task
model remains identical. Therefore, the results for
HENet and HENet++ are presented in the same
row in Table 5.
Occupancy Results. We present the results
of HENet++
for single BEV semantic segmen-
tation task on the nuScenes val sets in Table 6.
HENet++ obtains state-of-the-art results.
It is worth mentioning that compared with
single-task performance, the end-to-end multi-task
performance of HENet++ only drops 0.6 mAP
for the 3D object detection task, 0.5 mIOU for the
BEV semantic segmentation task, and 0.9 mIoU
for the Occupancy task, respectively.
6.5 Ablation Study
We also conduct ablation studies for each proposed
module on nuScenes val set.
Hybrid Image Encoding Network. To
demonstrate the effectiveness of the proposed
hybrid image encoding network, we compare
HENet
and HENet++
with three baseline
methods and their ensemble model. As shown in
Table 7, by combining with BEVDepth4D [13] and
BEVStereo [15] through hybrid image encoding,
HENet can significantly improve the 3D object
detection performance. Compared to increasing
resolution (model C), Hybrid Image Encoding
Network can achieve higher accuracy with faster
17


## Page 18

Table 9: Ablation of Temporal Feature Integration module of HENet. Our proposed backward
and forward processes with AFFM achieve the best results.
Temporal Integration
NDS mAP Parameters
Global Concatenation&Conv (BEVDepth4D [14])
52.3
40.8
76.51M
Global Concatenation&Conv + larger BEV encoder
52.4
40.7
77.70M
Global attention
52.6
40.9
76.68M
Forward with adjacent Concatenation&Conv
52.8
40.6
76.63M
Forward with AFFM
53.1
41.2
76.64M
Backward + Forward with adjacent Concatenation&Conv 52.8
40.7
76.63M
Backward + Forward with AFFM (Ours)
53.2
41.5
76.64M
Table 10: Ablation of Independent BEV
Feature Encoding of HENet. ‘AFS’ is the
adaptive feature selection. ‘IE’ denotes the inde-
pendent BEV encoder. All experiments only used
a single BEVDepth4D with ResNet-50 as the
image encoder.
Det-grid Seg-grid AFS IE
NDS
mAP
mIoU
0.4m
0.4m
53.2
41.9
41.6
0.8m
0.8m
50.5
39.6
50.9
0.4m
0.8m
52.9
42.0
50.6
0.4m
0.8m
✓
53.3 ↑0.4 42.3 ↑0.3 51.2 ↑0.6
0.4m
0.8m
✓
✓
54.6 ↑1.7 43.1 ↑1.1 54.0 ↑3.4
Table 11: Ablation of Pretrain Method of
HENet++. This experiment is conducted on a
triple-task R50 small model. Compared to using
single-task detection or occupancy weights, load-
ing the merged model for pre-training improves
multi-task performance.
Load from
NDS
mIoUbev
mIoUocc
Detection
53.7
54.6
36.2
Occupancy
53.2
55.2
37.4
Model Merge
53.9
55.3
37.5
Table 12: Ablation on the Loss for End-to-
End Autonomous Driving.
Lplan Lpred Lcol
UniAD Metrics
VAD/STP3 Metrics
mean L2 mean Col. mean L2 mean Col.
✓
1.69
0.52
0.71
0.17
✓
✓
1.36
0.20
0.58
0.10
✓
✓
✓
1.29
0.13
0.55
0.05
inference speed and lower training costs. Com-
pared to increasing the frame number (model
F), Hybrid Image Encoding Network can achieve
higher accuracy with lower training costs. Notably,
ensembling the results of the two baselines by
NMS decreases the overall performance since the
weaker BEVDepth4D [13] introduces many false
positive detection results. The same conclusion
can be drawn from the comparative experiments
between SparseBEV [32] and HENet++, thereby
demonstrating that Hybrid Encoding is effective
across both BEV-based and sparse-feature-based
perception frameworks.
For better comparison, we provide a multi-task
ablation study, as shown in Table 8.
We also provide the visualization of the detec-
tion results in Figure 9. It can be seen that, due
to motion or occlusion, some objects or scenes
(as shown in the blue boxes) require a longer
time sequence. Besides, high-resolution and sophis-
ticated depth estimation methods benefit the
perception of difficult objects and scenes (as shown
in the red boxes). HENet
and HENet++
can
effectively combine the advantages of long-time
sequence, high-resolution, and sophisticated depth
estimation.
Temporal Feature Integration of HENet.
Table 9 compares the results between different
types of temporal feature integration methods.
Our adjacent attention achieves the best
results.
We observe that adjacent design is more effec-
tive than global operation, whether using attention
or using Concatenation&Conv. Besides, compared
to concatenation and convolution, our AFFM,
which is based on the attention mechanism, per-
forms better. Lastly, global attention and the larger
BEV encoder introduce more model parameters
and achieve worse performance than pair-wise
attention. This demonstrates that the performance
improvements in pairwise attention stem from the
design itself rather than from increased model
parameters.
Independent BEV Feature Encoding of
HENet. As analyzed in [66], 3D object detec-
tion and BEV semantic segmentation tasks prefer
different BEV feature grid sizes. As shown in
18


## Page 19

Table 10, using BEV feature maps of different sizes
across tasks achieves the best trade-off in multi-
task performance. Moreover, adopting independent
adaptive feature selection and BEV encoder for
each task can further improve the multi-task
performance of 1.7 NDS, 1.1 mAP, and 3.4 mIoU.
Pretrain
with
Model
Merge
of
HENet++. As shown in Figure 11, compared
to using single-task detection or occupancy
weights, loading the merged model for pre-training
improves multi-task performance.
Loss for End-to-End Autonomous Driv-
ing of HENet++. The experimental results in
Figure 12 demonstrate the effectiveness of the loss
mentioned in Section 5.
7 Conclusion
In this paper, we first present HENet, an end-to-
end framework for multi-task 3D perception. We
propose a Hybrid Image Encoding Network for
BEV and a Temporal Feature Integration Mod-
ule to handle high-resolution, long-term temporal
image inputs efficiently. Besides, we adopt task-
specific BEV grid sizes, an Independent BEV
Feature Encoder and Decoder to address the
multi-task conflict issue.
Based on further analysis of the characteristics
of different tasks in existing work, we introduce
the HENet++
framework. By simultaneously
hybrid encoding for sparse foreground features
and dense background voxel features, the frame-
work enables end-to-end prediction for 3D object
detection, BEV semantic segmentation, and occu-
pancy semantic segmentation, providing suitable
features for each task. In addition, we intro-
duce a model-merging-based pre-training strategy
that further enhances multi-task performance.
HENet++
achieves state-of-the-art end-to-end
multi-task perception performance on the nuScenes
dataset.
Based on the HENet++
perception frame-
work, we further design an end-to-end autonomous
driving model. Leveraging the extracted sparse
foreground features and dense background fea-
tures, HENet++
employs an attention-based
world-prediction module to perform prediction
and ego-vehicle trajectory planning simultaneously.
HENet++ is the first work that leverages Radar
and Camera for end-to-end autonomous driving.
On the nuScenes dataset, the HENet++ model
achieves a lower collision rate compared to existing
methods.
Declarations
Preliminary Version.
A preliminary version of
this manuscript was published in [66].
Acknowledgements.
This work was supported
by National Key R&D Program of China (Grant
No. 2022ZD0160305) and National Natural Science
Foundation of China (Grant No. 62176007).
Data Availability.
All experiments are con-
ducted on publicly available datasets. To be
specific, the nuScenes dataset is available at https:
//www.nuscenes.org/nuscenes. The Occupancy
Ground Truth of nuScenes can be found at https:
//github.com/Tsinghua-MARS-Lab/Occ3D.
References
[1] Weng, X., Ivanovic, B., Wang, Y., Wang, Y.,
Pavone, M.: Para-drive: Parallelized architec-
ture for real-time autonomous driving. In:
CVPR, pp. 15449–15458 (2024)
[2] Zheng, W., Song, R., Guo, X., Chen, L.:
Genad: Generative end-to-end autonomous
driving. In: ECCV (2024)
[3] Sun, W., Lin, X., Shi, Y., Zhang, C.,
Wu, H., Zheng, S.: Sparsedrive: End-to-end
autonomous driving via sparse scene represen-
tation. In: ICRA (2025)
[4] Wang, Y., Chao, W.-L., Garg, D., Hariharan,
B., Campbell, M., Weinberger, K.Q.: Pseudo-
lidar from visual depth estimation: Bridging
the gap in 3d object detection for autonomous
driving. In: CVPR, pp. 8445–8453 (2019)
[5] Wang, T., Zhu, X., Pang, J., Lin, D.: Fcos3d:
Fully convolutional one-stage monocular 3d
object detection. In: ICCV (2021)
[6] Ding, M., Huo, Y., Yi, H., Wang, Z., Shi, J.,
Lu, Z., Luo, P.: Learning depth-guided convo-
lutions for monocular 3d object detection. In:
CVPR (2020)
19


## Page 20

[7] Brazil, G., Liu, X.: M3d-rpn: Monocular 3d
region proposal network for object detection.
In: ICCV (2019)
[8] Wang, T., Pang, J., Lin, D.: Monocular 3d
object detection with depth from motion. In:
ECCV (2022)
[9] Park, D., Ambrus, R., Guizilini, V., Li, J.,
Gaidon, A.: Is pseudo-lidar needed for monoc-
ular 3d object detection? In: ICCV (2021)
[10] Reading, C., Harakeh, A., Chae, J., Waslan-
der, S.L.: Categorical depth distribution net-
work for monocular 3d object detection. In:
CVPR, pp. 8555–8564 (2021)
[11] Roddick,
T.,
Kendall,
A.,
Cipolla,
R.:
Orthographic feature transform for monoc-
ular 3d object detection. arXiv preprint
arXiv:1811.08188 (2018)
[12] Huang, J., Huang, G., Zhu, Z., Ye, Y., Du,
D.: Bevdet: High-performance multi-camera
3d object detection in bird-eye-view. arXiv
preprint arXiv:2112.11790 (2021)
[13] Li, Y., Ge, Z., Yu, G., Yang, J., Wang, Z.,
Shi, Y., Sun, J., Li, Z.: Bevdepth: Acquisi-
tion of reliable depth for multi-view 3d object
detection. In: AAAI (2023)
[14] Huang,
J.,
Huang,
G.,
Robotics,
P.:
Bevdet4d: Exploit temporal cues in multi-
camera 3d object detection. arXiv preprint
arXiv:2203.17054 (2022)
[15] Li, Y., Bao, H., Ge, Z., Yang, J., Sun, J., Li,
Z.: Bevstereo: Enhancing depth estimation in
multi-view 3d object detection with dynamic
temporal stereo. In: AAAI (2023)
[16] Park, J., Xu, C., Yang, S., Keutzer, K., Kitani,
K., Tomizuka, M., Zhan, W.: Time will tell:
New outlooks and a baseline for temporal
multi-view 3d object detection. In: ICLR
(2023)
[17] Feng, C., Jie, Z., Zhong, Y., Chu, X., Ma,
L.: Aedet: Azimuth-invariant multi-view 3d
object detection. In: CVPR, pp. 21580–21588
(2023)
[18] Huang, B., Li, Y., Xie, E., Liang, F., Wang,
L., Shen, M., Liu, F., Wang, T., Luo, P., Shao,
J.: Fast-bev: Towards real-time on-vehicle
bird’s-eye view perception. arXiv preprint
arXiv:2301.07870 (2023)
[19] Jiang, Y., Zhang, L., Miao, Z., Zhu, X.,
Gao, J., Hu, W., Jiang, Y.-G.: Polarformer:
Multi-camera 3d object detection with polar
transformer. In: AAAI, pp. 1042–1050 (2023)
[20] Li, Z., Wang, W., Li, H., Xie, E., Sima,
C., Lu, T., Qiao, Y., Dai, J.: Bevformer:
Learning bird’s-eye-view representation from
multi-camera images via spatiotemporal trans-
formers. In: ECCV (2022)
[21] Yang, C., Chen, Y., Tian, H., Tao, C., Zhu, X.,
Zhang, Z., Huang, G., Li, H., Qiao, Y., Lu, L.,
et al.: Bevformer v2: Adapting modern image
backbones to bird’s-eye-view recognition via
perspective supervision. In: CVPR, pp. 17830–
17839 (2023)
[22] Wang, Z., Min, C., Ge, Z., Li, Y., Li, Z., Yang,
H., Huang, D.: Sts: Surround-view tempo-
ral stereo for multi-view 3d detection. arXiv
preprint arXiv:2208.10145 (2022)
[23] Zong, Z., Jiang, D., Song, G., Xue, Z., Su, J.,
Li, H., Liu, Y.: Temporal enhanced training
of multi-view 3d object detector via historical
object prediction. In: ICCV (2023)
[24] Zhang, Y., Zheng, W., Zhu, Z., Huang, G.,
Lu, J., Zhou, J.: A simple baseline for multi-
camera 3d object detection. In: AAAI, pp.
3507–3515 (2023)
[25] Wang, Y., Guizilini, V., Zhang, T., Wang,
Y., Zhao, H., Solomon, J.: Detr3d: 3d object
detection from multi-view images via 3d-to-2d
queries. In: CoRL (2021)
[26] Liu, Y., Wang, T., Zhang, X., Sun, J.: Petr:
Position embedding transformation for multi-
view 3d object detection. In: ECCV (2022)
[27] Liu, Y., Yan, J., Jia, F., Li, S., Gao, A., Wang,
T., Zhang, X.: Petrv2: A unified framework
for 3d perception from multi-camera images.
In: ICCV (2023)
20


## Page 21

[28] Yang, Z., Zhou, Y., Chen, Z., Ngiam, J.: 3d-
man: 3d multi-frame attention network for
object detection. In: CVPR, pp. 1863–1872
(2021)
[29] Lin, X., Lin, T., Pei, Z., Huang, L., Su, Z.:
Sparse4d: Multi-view 3d object detection with
sparse spatial-temporal fusion. arXiv preprint
arXiv:2211.10581 (2022)
[30] Lin,
X.,
Lin,
T.,
Pei,
Z.,
Huang,
L.,
Su, Z.: Sparse4d v2: Recurrent temporal
fusion with sparse model. arXiv preprint
arXiv:2305.14018 (2023)
[31] Wang, S., Liu, Y., Wang, T., Li, Y., Zhang, X.:
Exploring object-centric temporal modeling
for efficient multi-view 3d object detection. In:
ICCV (2023)
[32] Liu, H., Teng, Y., Lu, T., Wang, H., Wang,
L.: Sparsebev: High-performance sparse 3d
object detection from multi-camera videos. In:
ICCV (2023)
[33] Jiang, X., Li, S., Liu, Y., Wang, S., Jia, F.,
Wang, T., Han, L., Zhang, X.: Far3d: Expand-
ing the horizon for surround-view 3d object
detection. In: AAAI (2024)
[34] Philion, J., Fidler, S.: Lift, splat, shoot:
Encoding images from arbitrary camera rigs
by implicitly unprojecting to 3d. In: ECCV
(2020)
[35] Nicolas, C., Francisco, M., Gabriel, S., Nico-
las, U., Alexander, K., Sergey, Z.: End-to-end
object detection with transformers. In: ECCV
(2020)
[36] Hu, A., Murez, Z., Mohan, N., Dudas, S.,
Hawke, J., Badrinarayanan, V., Cipolla, R.,
Kendall, A.: Fiery: Future instance prediction
in bird’s-eye view from surround monocular
cameras. In: ICCV (2021)
[37] Yang, W., Li, Q., Liu, W., Yu, Y., Ma, Y., He,
S., Pan, J.: Projecting your view attentively:
Monocular road scene layout estimation via
cross-view transformation. In: CVPR (2021)
[38] Roddick, T., Cipolla, R.: Predicting semantic
map representations from images using pyra-
mid occupancy networks. In: CVPR (2020)
[39] Pan, B., Sun, J., Leung, H.Y.T., Andonian, A.,
Zhou, B.: Cross-view semantic segmentation
for sensing surroundings. IEEE Robotics and
Automation Letters (2020)
[40] Xie, E., Yu, Z., Zhou, D., Philion, J., Anand-
kumar, A., Fidler, S., Luo, P., Alvarez, J.M.:
M2bev: Multi-camera joint 3d detection and
segmentation with unified birds-eye view rep-
resentation. arXiv preprint arXiv:2204.05088
(2022)
[41] Zhou, B., Kr¨ahenb¨uhl, P.: Cross-view trans-
formers for real-time map-view semantic
segmentation. In: CVPR (2022)
[42] Li, Q., Wang, Y., Wang, Y., Zhao, H.: Hdmap-
net: An online hd map construction and
evaluation framework. In: ICRA (2022)
[43] Cao, A.-Q., De Charette, R.: Monoscene:
Monocular 3d semantic scene completion. In:
CVPR, pp. 3991–4001 (2022)
[44] Huang, Y., Zheng, W., Zhang, Y., Zhou, J.,
Lu, J.: Tri-perspective view for vision-based
3d semantic occupancy prediction. In: CVPR,
pp. 9223–9232 (2023)
[45] Wei, Y., Zhao, L., Zheng, W., Zhu, Z., Zhou,
J., Lu, J.: Surroundocc: Multi-camera 3d occu-
pancy prediction for autonomous driving. In:
ICCV, pp. 21729–21740 (2023)
[46] Li, Y., Yu, Z., Choy, C., Xiao, C., Alvarez,
J.M., Fidler, S., Feng, C., Anandkumar,
A.: Voxformer: Sparse voxel transformer for
camera-based 3d semantic scene completion.
In: CVPR, pp. 9087–9098 (2023)
[47] Yu, Z., Shu, C., Deng, J., Lu, K., Liu, Z., Yu,
J., Yang, D., Li, H., Chen, Y.: Flashocc: Fast
and memory-efficient occupancy prediction
via channel-to-height plugin. arXiv preprint
arXiv:2311.12058 (2023)
[48] Li, Z., Yu, Z., Austin, D., Fang, M., Lan,
S., Kautz, J., Alvarez, J.M.: Fb-occ: 3d
21


## Page 22

occupancy prediction based on forward-
backward view transformation. arXiv preprint
arXiv:2307.01492 (2023)
[49] Pan, M., Liu, L., Liu, J., Huang, P., Wang, L.,
Zhang, S., Xu, S., Lai, Z., Yang, K.: Uniocc:
Unifying vision-centric 3d occupancy predic-
tion with geometric and semantic rendering.
arXiv preprint arXiv:2306.09117 (2023)
[50] Pan, M., Liu, J., Zhang, R., Huang, P., Li, X.,
Liu, L., Zhang, S.: Renderocc: Vision-centric
3d occupancy prediction with 2d rendering
supervision. arXiv preprint arXiv:2309.09502
(2023)
[51] Wang, Z., Wu, S., Xie, W., Chen, M.,
Prisacariu, V.A.: Nerf–: Neural radiance fields
without known camera parameters. arXiv
preprint arXiv:2102.07064 (2021)
[52] Hou, J., Li, X., Guan, W., Zhang, G., Feng,
D., Du, Y., Xue, X., Pu, J.: Fastocc: Acceler-
ating 3d occupancy prediction by fusing the
2d bird’s-eye view and perspective view. arXiv
preprint arXiv:2403.02710 (2024)
[53] Ma, Q., Tan, X., Qu, Y., Ma, L., Zhang,
Z., Xie, Y.: Cotr: Compact occupancy trans-
former for vision-based 3d occupancy predic-
tion. In: CVPR, pp. 19936–19945 (2024)
[54] Zhuang, Z., Li, R., Jia, K., Wang, Q., Li, Y.,
Tan, M.: Perception-aware multi-sensor fusion
for 3d lidar semantic segmentation. In: ICCV
(2021)
[55] Yuan, Y., Huang, L., Guo, J., Zhang, C.,
Chen, X., Wang, J.: Ocnet: Object context
network for scene parsing. arXiv preprint
arXiv:1809.00916 (2018)
[56] Hu, S., Chen, L., Wu, P., Li, H., Yan,
J., Tao, D.: St-p3: End-to-end vision-based
autonomous driving via spatial-temporal fea-
ture learning. In: ECCV, pp. 533–549 (2022).
Springer
[57] Hu, Y., Yang, J., Chen, L., Li, K., Sima, C.,
Zhu, X., Chai, S., Du, S., Lin, T., Wang, W.,
Lu, L., Jia, X., Liu, Q., Dai, J., Qiao, Y., Li,
H.: Planning-oriented autonomous driving. In:
CVPR (2023)
[58] Jiang, B., Chen, S., Xu, Q., Liao, B., Chen,
J., Zhou, H., Zhang, Q., Liu, W., Huang, C.,
Wang, X.: Vad: Vectorized scene represen-
tation for efficient autonomous driving. In:
ICCV, pp. 8340–8350 (2023)
[59] Song, Z., Jia, C., Liu, L., Pan, H., Zhang, Y.,
Wang, J., Zhang, X., Xu, S., Yang, L., Luo,
Y.: Don’t shake the wheel: Momentum-aware
planning in end-to-end autonomous driving.
In: CVPR (2025)
[60] Zhang, B., Song, N., Jin, X., Zhang, L.: Bridg-
ing past and future: End-to-end autonomous
driving with historical prediction and plan-
ning. In: CVPR (2025)
[61] Liao, B., Chen, S., Yin, H., Jiang, B., Wang,
C., Yan, S., Zhang, X., Li, X., Zhang, Y.,
Zhang, Q., et al.: Diffusiondrive: Truncated
diffusion model for end-to-end autonomous
driving. In: CVPR (2025)
[62] Lee, Y., Park, J.: Centermask: Real-time
anchor-free instance segmentation. In: CVPR
(2020)
[63] Lin, T.-Y., Doll´ar, P., Girshick, R., He, K.,
Hariharan, B., Belongie, S.: Feature pyra-
mid networks for object detection. In: CVPR
(2017)
[64] He, K., Zhang, X., Ren, S., Sun, J.: Deep
residual learning for image recognition. In:
CVPR (2016)
[65] Huang, J., Huang, G.: Bevpoolv2: A cutting-
edge implementation of bevdet toward deploy-
ment. arXiv preprint arXiv:2211.17111 (2022)
[66] Xia, Z., Lin, Z., Wang, X., Wang, Y., Xing,
Y., Qi, S., Dong, N., Yang, M.-H.: Henet:
Hybrid encoding for end-to-end multi-task
3d perception from multi-view cameras. In:
ECCV (2024)
[67] Liang, T., Xie, H., Yu, K., Xia, Z., Lin, Z.,
Wang, Y., Tang, T., Wang, B., Tang, Z.:
Bevfusion: A simple and robust lidar-camera
fusion framework. In: NeurIPS (2022)
22


## Page 23

[68] Yin, T., Zhou, X., Krahenbuhl, P.: Center-
based 3d object detection and tracking. In:
CVPR (2021)
[69] Badrinarayanan, V., Kendall, A., Cipolla, R.:
Segnet: A deep convolutional encoder-decoder
architecture for image segmentation. IEEE
TPAMI (2017)
[70] Jin, X., Ren, X., Preotiuc-Pietro, D., Cheng,
P.: Dataless knowledge fusion by merging
weights of language models. In: ICLR (2023)
[71] Lin, Z., Liu, Z., Wang, Y., Zhang, L., Zhu,
C.: Rcbevdet++: toward high-accuracy radar-
camera fusion 3d perception network. arXiv
preprint arXiv:2409.04979 (2024)
[72] Tong, W., Sima, C., Wang, T., Chen, L., Wu,
S., Deng, H., Gu, Y., Lu, L., Luo, P., Lin,
D., et al.: Scene as occupancy. In: ICCV, pp.
8406–8415 (2023)
[73] Li, P., Cui, D.: Navigation-guided sparse scene
representation for end-to-end autonomous
driving. In: ICLR (2025)
[74] Li, Z., Yu, Z., Wang, W., Anandkumar, A., Lu,
T., Alvarez, J.M.: Fb-bev: Bev representation
from forward-backward view transformations.
In: ICCV, pp. 6919–6928 (2023)
[75] Zhu, B., Jiang, Z., Zhou, X., Li, Z., Yu,
G.: Class-balanced grouping and sampling
for point cloud 3d object detection. arXiv
preprint arXiv:1908.09492 (2019)
[76] Zhang, Y., Zhu, Z., Du, D.: Occformer: Dual-
path transformer for vision-based 3d semantic
occupancy prediction. In: ICCV, pp. 9433–
9443 (2023)
[77] Wang, Y., Chen, Y., Liao, X., Fan, L.,
Zhang, Z.: Panoocc: Unified occupancy rep-
resentation for camera-based 3d panoptic
segmentation. In: CVPR, pp. 17158–17168
(2024)
[78] Caesar, H., Bankiti, V., Lang, A.H., Vora, S.,
Liong, V.E., Xu, Q., Krishnan, A., Pan, Y.,
Baldan, G., Beijbom, O.: nuscenes: A mul-
timodal dataset for autonomous driving. In:
CVPR (2020)
23

