# SparseFusion Fusing Multi-modal Sparse Representations 3D Detection

**Source**: arxiv PDF, 15 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

SparseFusion: Fusing Multi-Modal Sparse Representations
for Multi-Sensor 3D Object Detection
Yichen Xie1,∗, Chenfeng Xu1,∗, Marie-Julie Rakotosaona2, Patrick Rim3, Federico Tombari2,
Kurt Keutzer1, Masayoshi Tomizuka1, Wei Zhan1
1 University of California, Berkeley 2 Google 3 California Institute of Technology
Abstract
By identifying four important components of existing
LiDAR-camera 3D object detection methods (LiDAR and
camera candidates, transformation, and fusion outputs), we
observe that all existing methods either ﬁnd dense candi-
dates or yield dense representations of scenes. However,
given that objects occupy only a small part of a scene,
ﬁnding dense candidates and generating dense represen-
tations is noisy and inefﬁcient. We propose SparseFusion,
a novel multi-sensor 3D detection method that exclusively
uses sparse candidates and sparse representations. Speciﬁ-
cally, SparseFusion utilizes the outputs of parallel detectors
in the LiDAR and camera modalities as sparse candidates
for fusion. We transform the camera candidates into the Li-
DAR coordinate space by disentangling the object represen-
tations. Then, we can fuse the multi-modality candidates in
a uniﬁed 3D space by a lightweight self-attention module.
To mitigate negative transfer between modalities, we pro-
pose novel semantic and geometric cross-modality trans-
fer modules that are applied prior to the modality-speciﬁc
detectors. SparseFusion achieves state-of-the-art perfor-
mance on the nuScenes benchmark while also running at
the fastest speed, even outperforming methods with stronger
backbones. We perform extensive experiments to demon-
strate the effectiveness and efﬁciency of our modules and
overall method pipeline. Our code will be made publicly
available at https://github.com/yichen928/SparseFusion.
1. Introduction
Autonomous driving cars rely on multiple sensors, such
as LiDAR and cameras, to perceive the surrounding envi-
ronment. LiDAR sensors provide accurate 3D scene oc-
cupancy information through point clouds with points in
the xyz coordinate space, and cameras provide rich se-
mantic information through images with pixels in the RGB
color space. However, there are often signiﬁcant discrepan-
* indicates equal contribution.
1
2
3
4
5
FPS
67
68
69
70
71
72
mAP
PointAugmenting
TransFusion
UVTR
AutoAlignV2
BEVFusion (Liang)§
DeepInteraction
SparseFusion
BEVFusion (Liu) §
(a) mAP vs. FPS
Image Features
BEV Features (LiDAR)
BEV Features (Camera)
BEV Features (Fusion)
(b) Dense-to-dense fusion.
… …
Instance Features (Camera)
3D 
Detector
Camera 
Detector
Camera Modality Inputs
… …
LiDAR Modality Inputs
Instance Features (LiDAR)
… …
Instance Features (Fusion)
Information
Transfer
(c) Overview of our sparse fusion strategy. We extract instance-
level features from the LiDAR and camera modalities separately,
and fuse them in a uniﬁed 3D space to perform detection.
Figure 1: Compared to existing fusion algorithms, Sparse-
Fusion achieves state-of-the-art performance as well as the
fastest inference speed on nuScenes test set. † : Ofﬁcial
code of [5] uses ﬂip as test-time augmentation. ‡ : We use
BEVFusion-base results in the ofﬁcial repository of [30] to
match the input resolutions of other methods. § : Swin-
T [29, 22] is adopted as image backbone.
cies between representations of the same physical scene ac-
quired by the two sensors, as LiDAR sensors capture point
clouds using 360-degree rotation while cameras capture im-
ages from a perspective view without a sense of depth. This
impedes an effective and efﬁcient fusion of the LiDAR and
camera modalities. To tackle this challenge, multi-sensor
fusion algorithms were proposed to ﬁnd correspondences
between multi-modality data to transform and fuse them
into a uniﬁed scene representation space.
Dense representations, such as bird-eye-view (BEV),
volumetric, and point representations, are commonly used
to represent 3D scenes [30, 5, 42, 27, 43, 15]. Most pre-
vious works fuse different modalities by aligning low-level
arXiv:2304.14340v1  [cs.CV]  27 Apr 2023
### Page 2

Table 1: For each LiDAR-camera fusion method, we identify the LiDAR candidates and camera candidates that are used, the
transformation process used to fuse these candidates into a uniﬁed space, and the fusion outputs generated to represent 3D
scenes using information from both modalities. Based on these components, we categorize the methods into the following
categories: Dense+Sparse→Dense approaches relate the sparse region proposals in images to a dense frustum point cloud
and fuse them into a dense point space. Dense+Dense→Dense approaches align each point feature in the point cloud to
the corresponding pixel feature in the image and represent the 3D scenes using dense features such as point/BEV features.
Sparse+Dense→Sparse approaches generate sparse queries by detecting instance features in the point cloud and then apply-
ing cross-attention with dense image features. Dense+Dense→Sparse approaches predict objects using queries that combine
dense features from each modality. Sparse+Sparse→Sparse (ours) extracts sparse instance features from each modality and
directly fuses them to obtain the ﬁnal sparse instance features used for detection.
Category
Method
LiDAR Candidate
Camera Candidate
Transformation
Fusion Outputs
Dense+Sparse→Dense
Frustum PointNets [37]
point features
region proposals
proj. & concat.
point features
Dense+Dense→Dense
PointPainting [42]
point features
segm. output
proj. & concat.
point features
PointAugmenting [43]
point features
image features
proj. & concat.
point features
PAI3D [27]
point features
segm. output
proj. & concat.
point features
BEVFusion [30]
BEV features
image features
depth. est. & proj. & concat.
BEV features
AutoAlignV2 [5]
voxel features
image features
proj. & attn.
voxel features
Sparse+Dense→Sparse
TransFusion [1]
instance features
image features
proj. & attn.
instance features
Dense+Dense→Sparse
FUTR3D [4]
voxel features
image features
attn.
instance features
UVTR [19]
voxel features
image features
depth. est. & proj. & attn.
instance features
DeepInteraction [51]
BEV features
image features
proj. & attn.
instance features
CMT [49]
BEV features
image features
attn.
instance features
Sparse+Sparse→Sparse
SparseFusion (Ours)
instance features
instance features
proj. & attn.
instance features
data or high-level features to yield dense features that de-
scribe the entire 3D scene, e.g., as shown in Fig 1b. How-
ever, for the task of 3D object detection, such dense rep-
resentations are superﬂuous since we are only interested in
instances/objects, which only occupy a small part of the 3D
space. Furthermore, noisy backgrounds can be detrimen-
tal to object detection performance, and aligning different
modalities into the same space is a time-consuming process.
For example, generating BEV features from multi-view im-
ages takes 500ms on an RTX 3090 GPU [30].
In contrast, sparse representations are more efﬁcient, and
methods based on them have achieved state-of-the-art per-
formance in multi-sensor 3D detection [1, 4, 19, 51]. These
methods use object queries to represent instances/objects
in the scene and interact with the original image and point
cloud features. However, most previous works do not take
into account the signiﬁcant domain gap between features
from different modalities [48].
The queries may gather
information from one modality that has a large distribu-
tion shift with respect to another modality, making iter-
ative interaction between modalities with large gaps sub-
optimal. Recent work [51] mitigates this issue by incorpo-
rating modality interaction, i.e. performing cross-attention
between features from two different modalities. However,
the number of computations performed in this method in-
creases quadratically with the dimensions of features and
is thus inefﬁcient. We categorize previous works into four
groups by identifying four key components, which are out-
lined in Table 1. Further discussion of the methods in these
groups is presented in Sec. 2.
In this paper, we propose SparseFusion, a novel method
(Fig. 1c) that simultaneously utilizes sparse candidates and
yields sparse representations, enabling efﬁcient and effec-
tive 3D object detection. SparseFusion is the ﬁrst LiDAR-
camera fusion method, to our knowledge, to perform 3D
detection using exclusively sparse candidates and sparse fu-
sion outputs. We highlight a key common ground between
the two modalities: an image and a point cloud that rep-
resent the same 3D scene will contain mostly the same in-
stances/objects. To leverage this commonality, we perform
3D object detection on the inputs from each modality in
two parallel branches.
Then, the instance features from
each branch are projected into a uniﬁed 3D space. Since
the instance-level features are sparse representations of the
same objects in the same scene, we are able to fuse them
with a lightweight attention module [41] in a soft manner.
This parallel detection strategy allows the LiDAR and cam-
era branches to take advantage of the unique strengths of the
point cloud and image representations, respectively. Never-
theless, the drawbacks of each single-modality detector may
result in negative transfer during the fusion phase. For ex-
ample, the point cloud detector may struggle to distinguish
between a standing person and a tree trunk due to a lack of
detailed semantic information, while the image detector is
hard to localize objects in the 3D space due to a lack of ac-
curate depth information. To mitigate the issue of negative
transfer, we introduce a novel cross-modality information
transfer method designed to compensate for the deﬁciencies
### Page 3

of each modality. This method is applied to the inputs from
both modalities prior to the parallel detection branches.
SparseFusion achieves state-of-the-art results on the
competitive nuScenes benchmark [2]. Our instance-level
sparse fusion strategy allows for a lighter network and much
higher efﬁciency in comparison with prior work.
With
the same backbone, SparseFusion outperforms the current
state-of-the-art model [51] with 1.8x acceleration. Our con-
tributions are summarized as follows:
• We revisit prior LiDAR-camera fusion works and iden-
tify four important components that allow us to catego-
rize existing methods into four groups. We propose an
entirely new category of methods that exclusively uses
sparse candidates and representations.
• We propose SparseFusion, a novel method for LiDAR-
camera 3D object detection that leverages instance-
level sparse feature fusion and cross-modality infor-
mation transfer to take advantage of the strengths of
each modality while mitigating their weaknesses.
• We demonstrate that our method achieves state-of-
the-art performance in 3D object detection with a
lightweight architecture that provides the fastest infer-
ence speed.
2. Related Work
LiDAR-based 3D Object Detection. LiDAR sensors are
commonly used for single-modality 3D object detection due
to the accurate geometric information provided by point
clouds. For detection in outdoor scenes, most existing meth-
ods transform unordered point clouds into more structured
data formats such as pillars [17], voxels [50, 8], or range
views [9, 24]. Features are extracted by standard 2D or 3D
convolutional networks, based on which a detection head is
used to recognize objects and regress 3D bounding boxes.
Mainstream detection heads apply anchor-based [55, 17] or
center-based [54] structures. Inspired by the promising per-
formance of transformer-based methods in 2D detection,
some recent works explore transformers as feature extrac-
tors [32, 38] or as detection heads [1, 33]. Our method is
agnostic to the LiDAR-based detector used in the LiDAR
branch, and the default setting uses TransFusion-L [1].
Camera-based 3D Object Detection. Camera-based 3D
detection methods are also being studied increasingly. Early
work performs monocular 3D object detection by attach-
ing extra 3D bounding box regression heads [52, 45] to 2D
detectors. In practice, scenes are often perceived by mul-
tiple cameras from different perspective views. Following
LSS [36], methods like BEVDet [14] and BEVDepth [20]
extract 2D features from multi-view images and project
them into the BEV space.
Other methods including
DETR3D [46] and PETR [28] adapt techniques from
transformer-based 2D object detection methods [58, 3] to
learn correspondences between different perspective views
through cross-attention using 3D queries. However, as re-
vealed in [12], there inevitably exists some ambiguity when
recovering 3D geometry from 2D images. In response, re-
cent works [13, 21, 34] also explore the positive effects of
temporal cues in camera-based 3D detection. In our pro-
posed SparseFusion, we extend deformable-DETR [58] to
monocular 3D object detection and explicitly transform the
regressed bounding boxes to the LiDAR coordinate space.
Multi-Modality 3D Object Detection. LiDAR and cam-
eras provide complementary information about the sur-
rounding environment, so it is appealing to fuse the multi-
modality inputs for 3D object detection tasks. As analyzed
in Tab. 1, existing fusion methods can be classiﬁed into four
categories. Early works tend to fuse multi-modality infor-
mation into a uniﬁed dense representation. Frustum Point-
Nets [37] utilizes a Dense+Sparse→Dense approach that
ﬁlters dense point clouds with sparse 2D regions of inter-
est. Subsequent works explore Dense+Dense→Dense ap-
proaches by working directly with the dense LiDAR modal-
ity and camera modality features instead. Methods such as
[42, 43] project point clouds into image perspective views
and concatenate the dense image features with point fea-
tures. BEVFusion [30, 23] signiﬁcantly improves the per-
formance of this line of methods by projecting dense im-
age features into the LiDAR coordinate space using esti-
mated per-pixel depths. AutoAlignV2 [5] also considers the
soft correspondence through cross-modality attention to in-
crease the robustness. However, we point out that dense
representations are altogether undesirable for 3D object de-
tection as they are noisy and inefﬁcient.
Recent works have begun to utilize object-centric
sparse scene representations.
TransFusion [1] adopts
a Sparse+Dense→Sparse strategy by extracting sparse
instance-level features from the LiDAR modality and reﬁn-
ing them using dense image features. Other works [4, 19,
51, 49] utilize a Dense+Dense→Sparse approach where
queries are used to extract a sparse instance-level represen-
tation from dense BEV and image features. However, it
is hard to extract information from multi-modality features
with an attention operation given the large cross-modal dis-
tribution shift. To this end, UVTR [19] projects image fea-
tures into the LiDAR coordinate space, CMT [49] encodes
modality-speciﬁc positional information to its queries, and
DeepInteraction [51] proposes cross-modality interaction.
However, these methods still need to resolve the large multi-
modal domain gap by stacking many transformer layers to
construct a heavy decoder.
In contrast to the above methods, our method adopts the
previously unexplored Sparse+Sparse→Sparse approach.
SparseFusion extracts sparse representations of both modal-
ities and fuses them to generate a more accurate and se-
mantically rich sparse representation that yields great per-
### Page 4

formance while also achieving great efﬁciency.
3. Methodology
We present SparseFusion, an effective and efﬁcient
framework for 3D object detection via LiDAR and cam-
era inputs. The overall architecture is illustrated in Fig. 2.
We acquire sparse candidates from each modality using
modality-speciﬁc object detection in the LiDAR and cam-
era branches. The instance-level features generated by the
camera branch are transformed into the LiDAR space of
the instance-level features generated by the LiDAR branch.
They are then fused with a simple self-attention module
(Sec. 3.1). To mitigate the negative transfer between modal-
ities, we apply a geometric transfer module and a seman-
tic transfer module prior to the parallel detection branches
(Sec. 3.2). Furthermore, we design custom loss functions
for each module to ensure stable optimization (Sec. 3.3).
3.1. Sparse Representation Fusion
Acquiring candidates in two modalities.
LiDAR can-
didates. We follow TransFusion-L [1] and use only one
decoder layer for LiDAR modality detection.
The Li-
DAR backbone extracts a BEV feature map from the point
cloud inputs.
We initialize NL object queries Q0
L
=
{q0
L,i}NL
i=1, q0
L,i ∈RC as well as their corresponding refer-
ence points p0
L = {p0
L,i}NL
i=1, p0
L,i ∈R2 in the BEV plane.
These queries interact with the BEV features through a
cross-attention layer to generate the updated object queries
QL = {qL,i}NL
i=1, qL,i ∈RC. These updated queries QL
represent the instance-level features of objects in the LiDAR
modality, and we use them as the LiDAR candidates in the
subsequent multi-modal fusion module. Furthermore, we
apply a prediction head to each query to classify the object
and regress the bounding box in LiDAR coordinate space.
Camera candidates. To generate the camera candidates, we
utilize a camera-only 3D detector with images from dif-
ferent perspective views as inputs. Speciﬁcally, we extend
deformable-DETR [58] with 3D box regression heads. We
also initialize NC object queries Q0
C = {q0
C,i}NC
i=1, q0
C,i ∈
RC along with their corresponding reference points p0
C =
{p0
C,i}NC
i=1, p0
C,i ∈R2 on the image. For each perspective
view v, queries on its image interact with the correspond-
ing image features using a deformable attention layer [58].
The outputs of all perspective views comprise the updated
queries QP
C = {qP
C,i}NC
i=1, qP
C,i ∈RC. We use these queries
as the camera candidates in the subsequent multi-modal fu-
sion module. We provide further details of our architecture,
the initialization method, and the prediction heads for the
two modalities in our supplementary materials.
Transformation After acquiring the candidates from each
modality, we aim to transform the candidates from the cam-
era modality to the space of the candidates from the LiDAR
modality. Since the candidates from the camera modality
are high-dimensional latent features that are distributed dif-
ferently than the candidates from the LiDAR modality, a
naive coordinate transformation between modalities is in-
applicable here. To address this issue, we disentangle the
representations of the camera candidates. Intrinsically, a
camera candidate is an instance feature that is a representa-
tion of a speciﬁc object’s class and 3D bounding box. While
an object’s class is view-invariant, its 3D bounding box is
view-dependent. This motivates us to focus on transforming
high-dimensional bounding box representations.
We ﬁrst input the candidate instance features into the
prediction head of the camera branch. We label the out-
putted bounding boxes as bP . Given the extrinsic matrix
[Rv|tv] and intrinsic matrix Kv of the corresponding v-th
camera, the bounding boxes can be easily projected into the
LiDAR coordinate system. We denote the project bound-
ing boxes as bL. We encode the projected bounding boxes
with a multi-layer perceptron (MLP) g(·), yielding a high-
dimensional box embedding. We also encode the ﬂattened
camera parameter with another MLP m(·) to obtain a cam-
era embedding. The camera embedding is multiplied with
the original instance features as done in [20], which are then
added to the box embedding, given by
qL
C,i = g(bL
i ) + h(qP
C,i · m(Rv, tv, Kv)),
(1)
where h(·) is an extra MLP to encode the query fea-
tures in the perspective view. h(·) aims to preserve view-
agnostic information while discarding view-speciﬁc infor-
mation. Afterward, QL
C = {qL
C,i} is passed through a self-
attention layer to aggregate information from multiple cam-
eras to get the updated queries QC which represent the im-
age modality instance features in the LiDAR space.
Sparse candidate fusion. Our parallel modality-speciﬁc
object detection provides sparse instance candidates QL =
{qL,i}NL
i=1 and QC = {qC,i}NC
i=1 from the LiDAR and cam-
era modalities respectively.
After the above transforma-
tion of the camera candidates into LiDAR space, candidates
from both modalities represent bounding boxes in the same
LiDAR coordinate space, as well as the view-invariant cat-
egories. We now concatenate the candidates together:
QLC = {qLC,i}NL+NC
i=1
= {fL(qL,i)}NL
i=1 ∪{fC(qC,i)}NC
i=1 (2)
where fL(·), fC(·) are learnable projectors. Afterward, we
make novel use of a self-attention module to fuse the two
modalities. Despite the simplicity of self-attention, the in-
herent intuition is novel: the modality-speciﬁc detectors en-
code the advantageous aspects of their respective inputs,
and the self-attention module is able to aggregate and pre-
serve the information from both modalities in an efﬁcient
manner. The output of the self-attention module is used for
ﬁnal classiﬁcation and regression of the bounding boxes.
### Page 5

𝑚(⋅)
𝑔(⋅)
×
ℎ(⋅)
+
Concatenate
Input Images
Camera
Detector
Query
Initial Queries (𝑸𝐶
0)
Fused Features
Input Point-Cloud
LiDAR 
Detector
Query
Initial Queries (𝑸𝑳
𝟎)
LiDAR Candidates (𝑸𝐿)
Sparse Candidates (QLC)
LiDAR Branch
Fusion Branch
Camera Branch
Key
Value
Perspective View Detections
Camera Candidates
View
Transform
Camera Parameters: 
𝑹𝒕, 𝑲
Perspective View (𝑸C
P)
LiDAR View (𝑸𝐶)
Key
Value
Semantic Transfer
Heatmap 
head
Heatmap 
head
Geometric Transfer
Figure 2: Overall framework of SparseFusion. It fuses sparse candidates from LiDAR and camera modalities to obtain a
multi-modality instance-level representation in the uniﬁed LiDAR space.
LiDAR Point-Clouds
Sparse Depth Map
Concatenate
Image Features 
Depth Features
Depth-Aware Image Features
BEV Features
Depth-Aware Image Features 
Deformable
attention
Heatmap head
Semantic-Aware
BEV Features
LiDAR Initial Queries
Geometric 
Transfer
Semantic 
Transfer
Addition
Correspondence
Figure 3: Cross-modality information transfer. We trans-
fer geometric information from LiDAR to camera modality,
and semantic information from camera to LiDAR modality.
3.2. Cross-Modality Information Transfer
Although we aim to utilize the advantages of both
modalities, we must address that the modalities also have
their own disadvantages that can result in negative trans-
fer between modalities. For example, the LiDAR detec-
tor struggles to capture rich semantic information, while
the camera detector struggles to capture accurate geomet-
ric and depth information. To mitigate negative transfer, we
propose novel geometric and semantic information transfer
modules, as illustrated in Fig. 3, that we apply prior to the
modality-speciﬁc detectors.
Geometric transfer from LiDAR to camera. We project
each point in the LiDAR point cloud input to multi-view
images to generate sparse multi-view depth maps. These
multi-view depth maps are inputted into a shared encoder
to obtain depth features, which are then concatenated with
the image features to form depth-aware image features that
compensate for the lack of geometric information in cam-
era inputs. The depth-aware image features are used as the
input to the camera branch.
Semantic transfer from camera to LiDAR. We project
the points in the LiDAR point cloud input to the image
inputs, which yields sparse points on the image features.
We perform max-pooling to aggregate the resulting multi-
scale features, and we combine them with the BEV fea-
ture through addition. The concatenated features serve as
the queries and interact with the multi-scale image features
through deformable-attention [58]. The updated queries re-
place the original queries in the BEV features, which re-
sults in the semantic-aware BEV features, which are used
for query initialization.
3.3. Objective Function
We apply the Gaussian focal loss [26] to the initialized
queries of both modalities, given by
Linit = LGF ocal( ˆYL, YL) + LGF ocal( ˆYC, YC),
(3)
where ˆYL, ˆYC are the dense predictions of category-wise
heatmaps of the LiDAR and camera modalities, respec-
tively, and YL, YC are the corresponding ground-truths.
Then, we apply the loss function for the detectors of the
LiDAR and camera modalities, as well as the view transfor-
mation of the camera candidates and the candidate fusion
stage. Firstly, the predictions of each modality-speciﬁc de-
tector are independently matched with the ground-truth us-
ing the Hungary algorithm [16]. The object classiﬁcation is
optimized with focal loss [26] and the 3D bounding box re-
gression is optimized with L1 loss. For the camera modality
detector, the ground-truth bounding boxes are in separate
### Page 6

camera coordinates. For all other detectors, ground-truth
bounding boxes are in LiDAR coordinates. The detection
loss can be represented as
Ldetect = γLcamera
detect
+ Ltrans
detect + LLiDAR
detect
+ Lfusion
detect . (4)
Our entire network is optimized using L = αLinit +
βLdetect. In our implementation, we empirically set γ =
1, α = 0.1, and β = 1 to balance different terms.
4. Experiments
4.1. Dataset and metrics
We follow previous work [51, 49, 23, 5] to evaluate our
method on the nuScenes dataset [2].
It is a challenging
dataset for 3D object detection, consisting of 700/150/150
scenes for training/validation/test. It provides point clouds
collected using a 32-beam LiDAR and six images from
multi-view cameras. There are 1.4 million annotated 3D
bounding boxes for objects from 10 different classes. We
evaluate performance using the nuScenes detection score
(NDS) and mean average precision (mAP) metrics. The
ﬁnal mAP is averaged over distance thresholds 0.5m, 1m,
2m, and 4m on the BEV across 10 classes.
NDS is a
weighted average of mAP and other true positive metrics
including mATE, mASE, mAOE, mAVE, and mAAE.
4.2. Implementation Details
Our implementation is based on the MMDetection3D
framework [6]. For the camera branch, we use ResNet-
50 [11] as the backbone and initialize it with the Mask
R-CNN [10] instance segmentation network pretrained on
nuImage [2]. The input image resolution is 800×448. For
the LiDAR branch, we apply VoxelNet [55] with voxel size
(0.075m, 0.075m, 0.2m).
The detection range is set as
[−54m, 54m] for the XY-axes and [−5m, 3m] for the Z-
axis. Our LiDAR and camera modality detectors both in-
clude only 1 decoder layer. The query numbers for the Li-
DAR and camera modalities are set as NL = NC = 200, so
our fusion stage can detect at most 400 objects per scene.
Since our framework disentangles the camera detector
and the LiDAR detector, we can conveniently apply data
augmentation separately to the LiDAR inputs and camera
inputs. We apply random rotation, scaling, translation, and
ﬂipping to the LiDAR inputs, and we apply random scaling
and horizontal ﬂipping to the camera inputs. Our training
pipeline follows previous works [1, 30, 51]. We ﬁrst train
TransFusion-L [1] as our LiDAR-only baseline, which is
used to initialize our LiDAR backbone and LiDAR modal-
ity detector. This LiDAR-only baseline is trained for 20
epochs. Afterward, we freeze the pretrained LiDAR com-
ponents and train the entire fusion framework for 6 epochs.
For both training stages, we use the AdamW optimizer [31]
with one-cycle learning rate policy [39]. The initial learning
rate is 10−4 and the weight decay is 10−2. The hidden di-
mensions in the entire model except the backbones are 128.
For both training stages, we adopt CBGS [57] to balance
the class distribution. We train our method on four NVIDIA
A6000 GPUs with batch size 16.
4.3. Results and Comparison
We report results on the nuScenes validation and test
sets, without using any test-time augmentations or model
ensembles. As shown in Tab. 2, SparseFusion signiﬁcantly
improves our LiDAR-only baseline, TransFusion-L [1], by
+3.6% NDS and +6.3% mAP on the test set, due to the ad-
ditional use of camera inputs. More importantly, SparseFu-
sion sets a new state of the art on both the validation set
and test set, outperforming prior works including those us-
ing stronger backbones. It is noteworthy that SparseFusion
demonstrates a 0.4% NDS and 1.0% mAP improvement
over the most recent state-of-the-art [51] while also achiev-
ing a 1.8x speedup (5.6 FPS vs. 3.1 FPS) on A6000 GPU.
It can be seen in Fig. 1a that, in addition to superior per-
formance, SparseFusion also provides the fastest inference
speed. We also demonstrate the performance of SparseFu-
sion by visualizing some qualitative results in Fig. 7.
4.4. Analysis
Performance Breakdown SparseFusion performs 3D ob-
ject detection in both the LiDAR and camera branch sep-
arately.
Tab. 3 shows the detection performance in dif-
ferent parts of SparseFusion including the LiDAR branch,
camera branch (before and after view transformation), and
the fusion branch. We notice that our LiDAR branch de-
tection results notably surpass the LiDAR-only baseline
TransFusion-L [1] since the proposed semantic transfer can
compensate for the weakness of point cloud inputs. In com-
parison with the state-of-the-art single-frame camera de-
tector PETR [28] (six decoder layers), our camera branch
achieves much better performance with just one decoder
layer, owing to the depth-aware features from the proposed
geometric transfer. Besides, our view transformation mod-
ule not only transforms the instance features from the cam-
era coordinate space into the LiDAR coordinate space, but
it also slightly improves the camera branch detection per-
formance by aggregating multi-view information. With this
strong performance, the modality-speciﬁc detectors in each
branch would not cause negative transfer during fusion.
Strong Image Backbone. We incorporate stronger Swin-
T [29] backbone into SparseFusion to match some previous
work [23, 49]. Tab. 4 compares the performance of different
methods on the nuScenes validation set. We do not include
any test-time augmentations or model ensembles. Although
multi-modality detection relies more on the LiDAR inputs,
SparseFusion can still beneﬁt from a stronger image back-
bone and beat all the counterparts.
### Page 7

Table 2: Comparison with existing methods on nuScenes validation set and test set.
Methods
Modality
LiDAR Backbone
Camera Backbone
validation set
test set
NDS
mAP
NDS
mAP
FCOS3D [45]
Camera
-
ResNet-101 [11]
41.5
34.3
42.8
35.8
PETR [28]
Camera
-
ResNet-101 [11]
44.2
37.0
45.5
39.1
CenterPoint [52]
LiDAR
VoxelNet [55]
-
66.8
59.6
67.3
60.3
TransFusion-L [1]
LiDAR
VoxelNet [55]
-
70.1
65.1
70.2
65.5
PointAugmenting [42]
LiDAR+Camera
VoxelNet [55]
DLA34 [53]
-
-
71.0
66.8
FUTR3D [4]
LiDAR+Camera
VoxelNet [55]
ResNet-101 [11]
68.3
64.5
-
-
UVTR [19]
LiDAR+Camera
VoxelNet [55]
ResNet-101 [11]
70.2
65.4
71.1
67.1
TransFusion [1]
LiDAR+Camera
VoxelNet [55]
ResNet-50 [11]
71.3
67.5
71.6
68.9
AutoAlignV2 [5]
LiDAR+Camera
VoxelNet [55]
CSPNet [44]
71.2
67.1
72.4
68.4
BEVFusion [23]
LiDAR+Camera
VoxelNet [55]
Dual-Swin-T [22]
72.1
69.6
73.3
71.3
BEVFusion [30]
LiDAR+Camera
VoxelNet [55]
Swin-T [29]
71.4
68.5
72.9
70.2
DeepInteraction [51]
LiDAR+Camera
VoxelNet [55]
ResNet-50 [11]
72.6
69.9
73.4
70.8
CMT [49]
LiDAR+Camera
VoxelNet [55]
ResNet-50 [11]
70.8
67.9
-
-
SparseFusion (ours)
LiDAR+Camera
VoxelNet [55]
ResNet-50 [11]
72.8
70.4
73.8
72.0
Front Left
Front
Front Right
Back Left
Back
Back Right
Car
Truck
Motorcycle
Pedestrian
Traffic cone
Figure 4: Qualitative results of SparseFusion on nuScenes validation set.
Table 3: Performance breakdown. We show the detection
results in different parts of SparseFusion on the validation
set. ’L’ and ’C’ refer to the LiDAR and camera modalities,
respectively. ’ST’ and ’GT’ refer to semantic transfer and
geometric transfer, respectively. ’VT’ is the view transfor-
mation module.
Methods
Modality
NDS
mAP
TransFusion-L [1]
L
70.1
65.1
LiDAR branch
L + ST
71.8
68.4
PETR (ResNet50) [28]
C
38.1
31.3
Camera branch (before VT)
C+GT
43.5
40.6
Camera branch (after VT)
C+GT
44.3
41.5
SparseFusion
L+C
72.8
70.4
Modality-Speciﬁc Object Recall. The parallel detectors
in the LiDAR and camera branches enable us to determine
Table 4: Results on nuScenes validation set with stronger
image backbones. We do not use any test-time augmenta-
tions or model ensembles. The inference speed is measured
on a single NVIDIA A6000 GPU. † : CMT [49] adopts
ﬂash-attention [7] for transformer acceleration.
Methods
Image
Backbone
Input
Resolution
NDS
mAP
FPS
BEVFusion [23]
Dual-Swin-T
1600×900
72.1
69.6
0.8
CMT [49]
VoVNet-99
1600×640
72.9
70.3
3.8†
SparseFusion
ResNet-50
800×448
72.8
70.4
5.6
SparseFusion
Swin-T
800×448
73.1
71.0
5.3
which modality recalls each object. Given NL + NC pre-
dictions, we know that the ﬁrst NL instances come from the
LiDAR-modality detector, while the last NC are from the
camera modality. An object is recalled if a bounding box
with correct classiﬁcation is predicted within a radius of
two meters around it. In Fig. 5, we demonstrate the number
### Page 8

car
truck
const. vehicle
bus
trailer
barrier
motorcycle
bicycle
pedestrian
traffic cone
0
1000
2000
3000
(a) Objects of different classes.
< 10m
10m - 20m
20m - 30m
30m - 40m
40m - 50m
50m - 60m
60m - 70m
> 70m
0
1000
2000
3000
LiDAR
Camera
(b) Objects at different distances.
Figure 5: Number of objects recalled by each modality. We
do not count those objects recalled by both or neither.
of objects in the nuScenes validation set recalled by exactly
one modality. We observe that each modality can compen-
sate for the weakness of the other to some extent. Although
the LiDAR modality is typically more powerful, the cam-
era modality plays an important role in detecting objects
from classes such as cars, construction vehicles, and barri-
ers. Furthermore, the camera modality is useful for detect-
ing objects at far distances where point clouds are sparse.
Cross-Modality
Sparse
Representation
Interaction.
Fig. 8 visualizes the instance feature interaction in the
sparse fusion stage.
The strength of attention between
instance-level features is reﬂected by the thickness and
darkness of lines. We notice that most objects can aggre-
gate multi-modality instance-level features during fusion.
Although the strongest interactions exist mainly between
neighboring instances, it is interesting that features from the
camera modality are also able to deliver strong interactions
with the instances at the distant range. This could be a result
of the shared semantics among objects in images.
4.5. Ablation Studies
In this section, we study the effect of using alternatives
for the different modules in SparseFusion. For our ablation
studies, we train on a 1/5 split of nuScenes training set and
evaluate on the full nuScenes validation set.
Sparse Fusion Strategy. We compare our self-attention
module for sparse feature fusion with other fusion methods.
In addition to our self-attention module in Sec. 3.1, three al-
ternatives are considered: 1) Instance-level candidates from
the two branches are directly fed into an MLP without any
cross-instance aggregation. 2) LiDAR instance candidates
are used as queries and camera instance candidates are used
as keys/values. A cross-attention module is then used to
fuse multi-modality instance features. 3) We make novel
use of optimal transport in LiDAR-camera fusion [35]. We
propose to learn a distribution transformation from camera
candidates to LiDAR candidates through optimal transport.
Then, we can directly fuse them by concatenating the can-
didates of two branches along the channel dimension. More
details about this method are provided in appendix.
Figure 6: Instance-level feature interaction in the fusion
stage. Orange boxes are detected after the fusion stage with
high conﬁdence in the BEV space. Blue and green dots
denote all instances from the LiDAR and camera branches
separately.
Orange boxes are connected with blue/green
dots with blue/green lines. The attention strength is rep-
resented by the darkness and thickness of the lines.
The results in Tab. 5a show that only cross-attention
achieves competitive performance to self-attention. Yet, we
observe that it relies so heavily on the output of the LiDAR
branch that the camera branch is not fully utilized to com-
pensate for the weaknesses of the LiDAR branch. The MLP
strategy has limited performance as it does not fuse cross-
instance and cross-modality information. Despite the im-
pressive progress of optimal transport in other ﬁelds, it fails
to learn the correspondences between the instance features
of the two modalities and thus has limited performance. In
contrast, self-attention is simple, efﬁcient, and effective.
Information Transfer. We then ablate the geometric and
semantic transfer between the LiDAR and camera modali-
ties. The results in Tab. 5b show that the fusion performance
beneﬁts from both transfers. This also validates that the
disadvantages of both modalities result in negative transfer
and that our proposed information transfer modules are in-
deed effective in mitigating this issue. The semantic trans-
fer module especially improves the ﬁnal performance since
it compensates for the LiDAR modality’s lack of semantic
information, which is critical for 3D detection.
View Transformation. As explained in Sec. 3.1, we trans-
form the sparse representations of both modalities into one
uniﬁed space. To validate the effectiveness of this approach,
we ablate the view transformation of camera candidates into
the LiDAR coordinate space. This results in a more straight-
forward method where we simply obtain the predictions of
### Page 9

Table 5: Ablation study experiments to justify our design of each module.
(a) Sparse fusion strategies.
Fusion Strategy
NDS
mAP
MLP
67.8
64.5
Cross-Attention
68.6
65.8
Optimal Transport
68.0
65.6
Self-Attention
68.8
66.4
(b) Information transfers.
Geometric
Semantic
NDS
mAP
"
%
67.7
64.2
%
"
68.4
65.7
"
"
68.8
66.4
(c) Parallel modality-speciﬁc detectors.
Seq. Pos.
Seq. Feat.
NDS
mAP
"
%
68.1
65.3
"
"
67.9
64.2
%
%
68.8
66.4
two modalities and directly fuse them using self-attention.
Ablating the view transformation drops performance from
66.4% mAP and 68.8% NDS to 65.6% mAP and 68.3%
NDS, respectively. This demonstrates that the view trans-
formation is indeed helpful to overall performance.
Parallel Detectors. In addition to the ablation studies on
the modules of the proposed pipeline, we also study alter-
natives to the structure of the pipeline. SparseFusion uses
separate 3D object detectors for the LiDAR and camera
modalities in parallel for extracting instance-level features
to address the cross-modality domain gap. Alternatively,
we consider a sequential pipeline where the camera detec-
tor runs after the LiDAR detector. The camera-modality
detector inherits the output queries from the LiDAR detec-
tor. We consider two variants of this inheritance: 1) using
the 3D position and instance features for the initial query of
the camera modality; 2) using the 3D position but initial-
izing the instance features from the corresponding image
features. The camera detector follows the structure of the
PETR [28] decoder (one layer). Tab. 5c shows that both se-
quential structures yield notably inferior performance, jus-
tifying our use of parallel modality-speciﬁc detectors.
5. Conclusion
We revisit previous LiDAR-camera fusion works and
propose SparseFusion, a novel 3D object detection method
that utilizes the rarely-explored strategy of fusing sparse
representations. SparseFusion extracts instance-level fea-
tures from each modality separately via parallel 3D object
detectors and then treats the instance-level features as the
modality-speciﬁc candidates. Afterward, we transform the
candidates into a uniﬁed 3D space, and we are able to fuse
the candidates with a lightweight attention module. Exten-
sive experiments demonstrate that SparseFusion achieves
state-of-the-art performance on the nuScenes benchmark
with the fastest inference speed. We hope SparseFusion
will serve as a powerful and efﬁcient baseline for further
research into this ﬁeld.
References
[1] Xuyang Bai, Zeyu Hu, Xinge Zhu, Qingqiu Huang, Yilun
Chen, Hongbo Fu, and Chiew-Lan Tai. Transfusion: Robust
lidar-camera fusion for 3d object detection with transform-
ers. In Proceedings of the IEEE/CVF Conference on Com-
puter Vision and Pattern Recognition, pages 1090–1099,
2022. 2, 3, 4, 6, 7, 12, 13, 15
[2] Holger Caesar, Varun Bankiti, Alex H Lang, Sourabh Vora,
Venice Erin Liong, Qiang Xu, Anush Krishnan, Yu Pan, Gi-
ancarlo Baldan, and Oscar Beijbom.
nuscenes: A multi-
modal dataset for autonomous driving. In Proceedings of
the IEEE/CVF conference on computer vision and pattern
recognition, pages 11621–11631, 2020. 3, 6
[3] Nicolas Carion, Francisco Massa, Gabriel Synnaeve, Nicolas
Usunier, Alexander Kirillov, and Sergey Zagoruyko. End-to-
end object detection with transformers. In Computer Vision–
ECCV 2020: 16th European Conference, Glasgow, UK, Au-
gust 23–28, 2020, Proceedings, Part I 16, pages 213–229.
Springer, 2020. 3
[4] Xuanyao Chen, Tianyuan Zhang, Yue Wang, Yilun Wang,
and Hang Zhao. Futr3d: A uniﬁed sensor fusion framework
for 3d detection. arXiv preprint arXiv:2203.10642, 2022. 2,
3, 7
[5] Zehui Chen, Zhenyu Li, Shiquan Zhang, Liangji Fang, Qin-
hong Jiang, and Feng Zhao. Autoalignv2: Deformable fea-
ture aggregation for dynamic multi-modal 3d object detec-
tion. arXiv preprint arXiv:2207.10316, 2022. 1, 2, 3, 6, 7
[6] MMDetection3D Contributors.
MMDetection3D: Open-
MMLab next-generation platform for general 3D ob-
ject detection. https://github.com/open-mmlab/
mmdetection3d, 2020. 6
[7] Tri Dao, Daniel Y. Fu, Stefano Ermon, Atri Rudra, and
Christopher R´e. FlashAttention: Fast and memory-efﬁcient
exact attention with IO-awareness. In Advances in Neural
Information Processing Systems, 2022. 7
[8] Jiajun Deng, Shaoshuai Shi, Peiwei Li, Wengang Zhou,
Yanyong Zhang, and Houqiang Li. Voxel r-cnn: Towards
high performance voxel-based 3d object detection. In Pro-
ceedings of the AAAI Conference on Artiﬁcial Intelligence,
volume 35, pages 1201–1209, 2021. 3
[9] Lue Fan, Xuan Xiong, Feng Wang, Naiyan Wang, and
Zhaoxiang Zhang.
Rangedet: In defense of range view
for lidar-based 3d object detection. In Proceedings of the
IEEE/CVF International Conference on Computer Vision,
pages 2918–2927, 2021. 3
[10] Kaiming He, Georgia Gkioxari, Piotr Doll´ar, and Ross Gir-
shick. Mask r-cnn. In Proceedings of the IEEE international
conference on computer vision, pages 2961–2969, 2017. 6
[11] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun.
Deep residual learning for image recognition. In Proceed-
### Page 10

ings of the IEEE conference on computer vision and pattern
recognition, pages 770–778, 2016. 6, 7, 14
[12] Chenxi Huang, Tong He, Haidong Ren, Wenxiao Wang, Bin-
bin Lin, and Deng Cai. Obmo: One bounding box multiple
objects for monocular 3d object detection. arXiv preprint
arXiv:2212.10049, 2022. 3
[13] Junjie Huang and Guan Huang. Bevdet4d: Exploit tempo-
ral cues in multi-camera 3d object detection. arXiv preprint
arXiv:2203.17054, 2022. 3
[14] Junjie Huang, Guan Huang, Zheng Zhu, and Dalong Du.
Bevdet: High-performance multi-camera 3d object detection
in bird-eye-view. arXiv preprint arXiv:2112.11790, 2021. 3
[15] Yang Jiao, Zequn Jie, Shaoxiang Chen, Jingjing Chen, Xi-
aolin Wei, Lin Ma, and Yu-Gang Jiang. Msmdfusion: Fusing
lidar and camera at multiple scales with multi-depth seeds for
3d object detection. arXiv preprint arXiv:2209.03102, 2022.
1
[16] Harold W Kuhn. The hungarian method for the assignment
problem. Naval research logistics quarterly, 2(1-2):83–97,
1955. 5
[17] Alex H Lang, Sourabh Vora, Holger Caesar, Lubing Zhou,
Jiong Yang, and Oscar Beijbom. Pointpillars: Fast encoders
for object detection from point clouds. In Proceedings of
the IEEE/CVF conference on computer vision and pattern
recognition, pages 12697–12705, 2019. 3
[18] Hei Law and Jia Deng.
Cornernet: Detecting objects as
paired keypoints. In Proceedings of the European confer-
ence on computer vision (ECCV), pages 734–750, 2018. 15
[19] Yanwei Li, Yilun Chen, Xiaojuan Qi, Zeming Li, Jian
Sun, and Jiaya Jia.
Unifying voxel-based representation
with transformer for 3d object detection.
arXiv preprint
arXiv:2206.00630, 2022. 2, 3, 7
[20] Yinhao Li, Zheng Ge, Guanyi Yu, Jinrong Yang, Zengran
Wang, Yukang Shi, Jianjian Sun, and Zeming Li. Bevdepth:
Acquisition of reliable depth for multi-view 3d object detec-
tion. arXiv preprint arXiv:2206.10092, 2022. 3, 4
[21] Zhiqi Li, Wenhai Wang, Hongyang Li, Enze Xie, Chonghao
Sima, Tong Lu, Yu Qiao, and Jifeng Dai. Bevformer: Learn-
ing bird’s-eye-view representation from multi-camera im-
ages via spatiotemporal transformers. In Computer Vision–
ECCV 2022: 17th European Conference, Tel Aviv, Israel,
October 23–27, 2022, Proceedings, Part IX, pages 1–18.
Springer, 2022. 3
[22] Tingting Liang, Xiaojie Chu, Yudong Liu, Yongtao Wang,
Zhi Tang, Wei Chu, Jingdong Chen, and Haibin Ling. Cbnet:
A composite backbone network architecture for object de-
tection. IEEE Transactions on Image Processing, 31:6893–
6906, 2022. 1, 7
[23] Tingting Liang, Hongwei Xie, Kaicheng Yu, Zhongyu Xia,
Zhiwei Lin, Yongtao Wang, Tao Tang, Bing Wang, and Zhi
Tang. Bevfusion: A simple and robust lidar-camera fusion
framework. arXiv preprint arXiv:2205.13790, 2022. 3, 6, 7
[24] Zhidong Liang, Ming Zhang, Zehan Zhang, Xian Zhao, and
Shiliang Pu. Rangercnn: Towards fast and accurate 3d object
detection with range image representation. arXiv preprint
arXiv:2009.00206, 2020. 3
[25] Tsung-Yi Lin, Piotr Doll´ar, Ross Girshick, Kaiming He,
Bharath Hariharan, and Serge Belongie.
Feature pyra-
mid networks for object detection.
In Proceedings of the
IEEE conference on computer vision and pattern recogni-
tion, pages 2117–2125, 2017. 12, 14
[26] Tsung-Yi Lin, Priya Goyal, Ross Girshick, Kaiming He, and
Piotr Doll´ar. Focal loss for dense object detection. In Pro-
ceedings of the IEEE international conference on computer
vision, pages 2980–2988, 2017. 5
[27] Hao Liu, Zhuoran Xu, Dan Wang, Baofeng Zhang, Guan
Wang, Bo Dong, Xin Wen, and Xinyu Xu. Pai3d: Painting
adaptive instance-prior for 3d object detection. In Computer
Vision–ECCV 2022 Workshops: Tel Aviv, Israel, October
23–27, 2022, Proceedings, Part V, pages 459–475. Springer,
2023. 1, 2
[28] Yingfei Liu, Tiancai Wang, Xiangyu Zhang, and Jian Sun.
Petr: Position embedding transformation for multi-view 3d
object detection. In Computer Vision–ECCV 2022: 17th Eu-
ropean Conference, Tel Aviv, Israel, October 23–27, 2022,
Proceedings, Part XXVII, pages 531–548. Springer, 2022. 3,
6, 7, 9
[29] Ze Liu, Yutong Lin, Yue Cao, Han Hu, Yixuan Wei, Zheng
Zhang, Stephen Lin, and Baining Guo. Swin transformer:
Hierarchical vision transformer using shifted windows. In
Proceedings of the IEEE/CVF international conference on
computer vision, pages 10012–10022, 2021. 1, 6, 7
[30] Zhijian Liu, Haotian Tang, Alexander Amini, Xinyu Yang,
Huizi Mao, Daniela Rus, and Song Han. Bevfusion: Multi-
task multi-sensor fusion with uniﬁed bird’s-eye view repre-
sentation. arXiv preprint arXiv:2205.13542, 2022. 1, 2, 3, 6,
7
[31] Ilya Loshchilov and Frank Hutter. Decoupled weight decay
regularization. arXiv preprint arXiv:1711.05101, 2017. 6
[32] Jiageng Mao, Yujing Xue, Minzhe Niu, Haoyue Bai, Jiashi
Feng, Xiaodan Liang, Hang Xu, and Chunjing Xu. Voxel
transformer for 3d object detection. In Proceedings of the
IEEE/CVF International Conference on Computer Vision,
pages 3164–3173, 2021. 3
[33] Ishan Misra, Rohit Girdhar, and Armand Joulin. An end-to-
end transformer model for 3d object detection. In Proceed-
ings of the IEEE/CVF International Conference on Com-
puter Vision, pages 2906–2917, 2021. 3
[34] Jinhyung Park, Chenfeng Xu, Shijia Yang, Kurt Keutzer,
Kris Kitani, Masayoshi Tomizuka, and Wei Zhan. Time will
tell: New outlooks and a baseline for temporal multi-view 3d
object detection. arXiv preprint arXiv:2210.02443, 2022. 3
[35] Gabriel Peyr´e, Marco Cuturi, et al. Computational optimal
transport: With applications to data science. Foundations
and Trends® in Machine Learning, 11(5-6):355–607, 2019.
8
[36] Jonah Philion and Sanja Fidler. Lift, splat, shoot: Encoding
images from arbitrary camera rigs by implicitly unproject-
ing to 3d. In Computer Vision–ECCV 2020: 16th European
Conference, Glasgow, UK, August 23–28, 2020, Proceed-
ings, Part XIV 16, pages 194–210. Springer, 2020. 3
[37] Charles R Qi, Wei Liu, Chenxia Wu, Hao Su, and Leonidas J
Guibas. Frustum pointnets for 3d object detection from rgb-
### Page 11

d data. In Proceedings of the IEEE conference on computer
vision and pattern recognition, pages 918–927, 2018. 2, 3
[38] Hualian Sheng, Sijia Cai, Yuan Liu, Bing Deng, Jianqiang
Huang, Xian-Sheng Hua, and Min-Jian Zhao. Improving 3d
object detection with channel-wise transformer. In Proceed-
ings of the IEEE/CVF International Conference on Com-
puter Vision, pages 2743–2752, 2021. 3
[39] Leslie N Smith. Cyclical learning rates for training neural
networks. In 2017 IEEE winter conference on applications
of computer vision (WACV), pages 464–472. IEEE, 2017. 6
[40] Zhi Tian, Chunhua Shen, Hao Chen, and Tong He. Fcos:
Fully convolutional one-stage object detection. In Proceed-
ings of the IEEE/CVF international conference on computer
vision, pages 9627–9636, 2019. 15
[41] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszko-
reit, Llion Jones, Aidan N Gomez, Łukasz Kaiser, and Illia
Polosukhin. Attention is all you need. Advances in neural
information processing systems, 30, 2017. 2, 12
[42] Sourabh Vora, Alex H Lang, Bassam Helou, and Oscar Bei-
jbom.
Pointpainting: Sequential fusion for 3d object de-
tection.
In Proceedings of the IEEE/CVF conference on
computer vision and pattern recognition, pages 4604–4612,
2020. 1, 2, 3, 7
[43] Chunwei Wang, Chao Ma, Ming Zhu, and Xiaokang Yang.
Pointaugmenting: Cross-modal augmentation for 3d object
detection. In Proceedings of the IEEE/CVF Conference on
Computer Vision and Pattern Recognition, pages 11794–
11803, 2021. 1, 2, 3
[44] Chien-Yao Wang, Hong-Yuan Mark Liao, Yueh-Hua Wu,
Ping-Yang Chen, Jun-Wei Hsieh, and I-Hau Yeh. Cspnet: A
new backbone that can enhance learning capability of cnn.
In Proceedings of the IEEE/CVF conference on computer
vision and pattern recognition workshops, pages 390–391,
2020. 7
[45] Tai Wang, Xinge Zhu, Jiangmiao Pang, and Dahua Lin.
Fcos3d: Fully convolutional one-stage monocular 3d object
detection.
In Proceedings of the IEEE/CVF International
Conference on Computer Vision, pages 913–922, 2021. 3, 7
[46] Yue Wang, Vitor Campagnolo Guizilini, Tianyuan Zhang,
Yilun Wang, Hang Zhao, and Justin Solomon.
Detr3d:
3d object detection from multi-view images via 3d-to-2d
queries. In Conference on Robot Learning, pages 180–191.
PMLR, 2022. 3
[47] Yue Wang and Justin M Solomon. Deep closest point: Learn-
ing representations for point cloud registration. In Proceed-
ings of the IEEE/CVF international conference on computer
vision, pages 3523–3532, 2019. 12
[48] Chenfeng Xu, Shijia Yang, Tomer Galanti, Bichen Wu,
Xiangyu Yue, Bohan Zhai, Wei Zhan, Peter Vajda, Kurt
Keutzer, and Masayoshi Tomizuka. Image2point: 3d point-
cloud understanding with 2d image pretrained models. In
European Conference on Computer Vision, pages 638–656.
Springer, 2022. 2
[49] Junjie Yan, Yingfei Liu, Jianjian Sun, Fan Jia, Shuailin Li,
Tiancai Wang, and Xiangyu Zhang. Cross modal transformer
via coordinates encoding for 3d object dectection.
arXiv
preprint arXiv:2301.01283, 2023. 2, 3, 6, 7
[50] Yan Yan, Yuxing Mao, and Bo Li. Second: Sparsely embed-
ded convolutional detection. Sensors, 18(10):3337, 2018. 3
[51] Zeyu Yang, Jiaqi Chen, Zhenwei Miao, Wei Li, Xiatian
Zhu, and Li Zhang. Deepinteraction: 3d object detection
via modality interaction. arXiv preprint arXiv:2208.11112,
2022. 2, 3, 6, 7
[52] Tianwei Yin, Xingyi Zhou, and Philipp Krahenbuhl. Center-
based 3d object detection and tracking. In Proceedings of
the IEEE/CVF conference on computer vision and pattern
recognition, pages 11784–11793, 2021. 3, 7
[53] Fisher Yu, Dequan Wang, Evan Shelhamer, and Trevor
Darrell.
Deep layer aggregation.
In Proceedings of the
IEEE conference on computer vision and pattern recogni-
tion, pages 2403–2412, 2018. 7
[54] Xingyi Zhou, Dequan Wang, and Philipp Kr¨ahenb¨uhl. Ob-
jects as points. arXiv preprint arXiv:1904.07850, 2019. 3,
15
[55] Yin Zhou and Oncel Tuzel. Voxelnet: End-to-end learning
for point cloud based 3d object detection. In Proceedings of
the IEEE conference on computer vision and pattern recog-
nition, pages 4490–4499, 2018. 3, 6, 7
[56] Zixiang Zhou, Xiangchen Zhao, Yu Wang, Panqu Wang, and
Hassan Foroosh. Centerformer: Center-based transformer
for 3d object detection. In Computer Vision–ECCV 2022:
17th European Conference, Tel Aviv, Israel, October 23–27,
2022, Proceedings, Part XXXVIII, pages 496–513. Springer,
2022. 15
[57] Benjin Zhu, Zhengkai Jiang, Xiangxin Zhou, Zeming Li, and
Gang Yu. Class-balanced grouping and sampling for point
cloud 3d object detection. arXiv preprint arXiv:1908.09492,
2019. 6
[58] Xizhou Zhu, Weijie Su, Lewei Lu, Bin Li, Xiaogang
Wang, and Jifeng Dai. Deformable detr: Deformable trans-
formers for end-to-end object detection.
arXiv preprint
arXiv:2010.04159, 2020. 3, 4, 5, 12
### Page 12

In Sec. A, we provide additional experimental results
of SparseFusion and complementary details of the experi-
ments presented in the main paper. Then, in Sec. B, we
elaborate on the details of the architecture of SparseFusion.
A. Additional Experiments
A.1. Category-wise Results
In Tab. 6, we report the performance of SparseFusion
and our LiDAR-only baseline [1] for each object category in
nuScenes validation set. SparseFusion achieves signiﬁcant
performance improvement for all of the object categories.
In particular, the introduction of camera inputs helps to dis-
tinguish objects with similar shapes like motorcycles and
bicycles.
A.2. Qualitative Results
We provide additional qualitative results in Fig. 7, where
SparseFusion effectively detects most objects in the scene
with the correct classiﬁcation.
A.3. Experiment Details
Cross-Modality Sparse Representation Interaction
We
provide more details about Fig. 8. The orange boxes refer to
the high-conﬁdence objects detected by the fusion branch.
The blue and green dots denote all instances from the Li-
DAR and camera branches separately even if they only have
very low conﬁdence. The blue/green lines separately con-
nect the orange boxes and blue/green dots. We only visual-
ize the distribution of attention for high-conﬁdence objects
detected in the fusion branches (orange). The magnitude
of relationships (i.e., the attention value) is represented by
the darkness and thickness of the lines. More examples are
visualized in Fig. 8.
Optimal Transport for Sparse Fusion (Tab. 5a)
We
explain some details of the optimal transport strategy for
sparse fusion in our ablation study. We model the distribu-
tion of LiDAR candidates as follows.
pL(qL,i) =
sL,i
PNL
i=1 sL,i
, i = 1, 2, . . . , NL
(5)
where sL,i is the classiﬁcation conﬁdence (highest cate-
gory) of the i-th instance for the LiDAR detector. Similarly,
the distribution of camera candidates is modeled as follows.
pC(qC,j) =
sC,j
PNC
i=1 sC,j
, i = 1, 2, . . . , NC
(6)
where sC,j is the classiﬁcation conﬁdence (highest cate-
gory) of the j-th instance for the camera detector (after view
transformation). We construct a cost matrix C = [cij], i =
1, 2, . . . , NL, j = 1, 2, . . . , NC, where cij is the euclidean
distance between the centers of the i-th LiDAR instance and
j-th camera instance on the BEV plane. We solve an op-
timal transport between pL(qL,i) and pC(qC,i) using the
IPOT algorithm [47] which outputs an optimal transport
plan T∗, where
T∗= arg
min
T∈R
NL×NC
+
< C, T >
(7)
s.t. T1NC = pL, TT 1NL = pC
(8)
We normalize T for each row as ˆTij = Tij/ PNC
j=1 Tij.
Then, we concatenate LiDAR candidates QL with the
weighted camera candidates ˆTQC (matrix product) in a
channel-wise manner. The output features are fed into a
feed-forward network to get the NL fused instance features,
then the prediction head can get the object categories and
bounding boxes based on the instance features.
B. Architecture Details
In this section, we explain the detailed structure of each
module in SparseFusion. In addition, we also illustrate the
query initialization process for both LiDAR and camera de-
tectors.
B.1. Network Architecture
LiDAR Detector
We follow TransFusion-L [1] to adopt
a transformer-based LiDAR detector. The initial LiDAR
queries Q0
L (Sec. B.3) are passed through a self-attention
module, then cross-attention is conducted with the BEV
features from the LiDAR backbone.
The output queries
are fed into a feed-forward network to get the LiDAR can-
didates QL. In both the self-attention and cross-attention
modules, we add a positional encoding to all of the queries,
keys, and values. Instead of the ﬁxed sine positional embed-
ding [41], we apply the learned embeddings by inputting
the 2D XY locations of the queries, keys, and values on the
BEV plane to an MLP encoder. A LiDAR view prediction
head (Sec. B.2) is attached to the LiDAR candidates QL to
get the object category as well as the 3D bounding box in
LiDAR coordinates.
Camera Detector
We extend Deformable-DETR [58] to
the 3D object detection task. The initial camera queries
Q0
C (Sec. B.3) go through a self-attention module, then
deformable attention is conducted with the image fea-
tures, where we aggregate multi-scale image features from
FPN [25] through deformable attention. In deformable at-
tention, each query only interacts with its corresponding
single-view image features. The output queries are fed into
a feed-forward network to get the perspective view cam-
era candidates QP
C. As we do with the LiDAR detector,
we add positional embeddings to all of the queries, keys,
and values, which indicate their 2D locations on the image
### Page 13

Front Left
Front
Front Right
Back Left
Back
Back Right
Car
Truck
Bicycle
Pedestrian
Bus
Front Left
Front
Front Right
Back Left
Back
Back Right
Car
Truck
Bicycle
Pedestrian
Bus
Figure 7: Qualitative results of SparseFusion on nuScenes validation set.
Table 6: Category-wise performance on nuScenes validation set including the overall NDS, mAP, and AP for each category.
Methods
Modality
NDS
mAP
car
truck
bus
trailer
const.
vehicle
pedestrian
motorcycle
bicycle
trafﬁc
cone
barrier
TransFusion-L [1]
L
70.2
65.1
86.5
59.6
74.4
42.2
25.4
86.6
72.1
56.0
74.1
74.1
SparseFusion
L+C
72.8
70.4
88.5
64.4
77.1
44.3
30.3
89.8
81.5
71.0
80.6
76.6
of the corresponding view. A perspective view prediction
head (Sec. B.2) is attached to the perspective view camera
candidates QP
C to get the object category as well as the 3D
bounding box in camera coordinates.
View Transformation
Our view transformation module
consists of two parts: feature projection and multi-view
aggregation.
The feature projection is already described
in Eq. 1, which encodes the camera parameters and pro-
jected boxes with two MLPs and combines them with the
original instance features. The multi-view aggregation is
based on a self-attention module. The output instance fea-
tures belonging to all the different views are put together as
QL
C = {qL
C,i}NC
i=1. They are fed into a self-attention module
and feed-forward layer. For positional embeddings added
to each instance feature, we take into account both the pre-
dicted box center on the image from the camera detector and
the box center on the BEV plane after bounding box coor-
dinate transformation. The 4-dimensional inputs are passed
through an MLP to get the positional embedding for each
instance feature. The updated queries serve as the camera
candidates QC = {qC,i}NC
i=1. We also attach a LiDAR view
prediction head to the candidates to predict the object cate-
gory and 3D bounding boxes in the LiDAR coordinates.
Fusion Branch
We process the LiDAR candidates QL =
{qL,i}NL
i=1 and camera candidates QC = {qC,i}NC
i=1 with
two separate modules fL(·), fC(·), each consisting of a
fully-connected layer and layer normalization. Then, we
concatenate the candidates as QLC = {qLC,i}NL+NC
i=1
. Af-
terward, QLC is fed into a self-attention module and a feed-
forward network to get the ﬁnal fused instance features QF .
In the self-attention module, we also add a learned posi-
tional embedding to the instance features by encoding the
XY box centers on the BEV with an MLP. Finally, we at-
tach a LiDAR view prediction head to QF to predict the
object category and 3D LiDAR view bounding boxes as the
ﬁnal results.
### Page 14

Figure 8: Instance-level feature interaction in the fusion
stage. Orange boxes are objects detected after the fusion
stage with high conﬁdence in the BEV space. Blue and
green dots denote all instances from the LiDAR and cam-
era branches separately. Orange boxes are connected with
blue/green dots with blue/green lines. The strength of at-
tention is represented by the darkness and thickness of the
lines.
Algorithm 1: Geometric Transfer
Input: Multi-scale image feature map of view v:
FC,v = [Fl
C,v]L
l=0, sparse depth map of view
v: Dv.
Output: Multi-scale depth-aware image feature
map of view v: ˆFC,v = [ˆFl
C,v]L
l=0
1 FD = Stem(Dv)
2 ˆFC,v = []
3 for l = 1, 2, . . . , L do
4
FD = Residual-Blockl(FD)
5
FD = Concatenate(FD, Fl
C,v)
/* channel-wise concatenation
*/
6
FD = Convl
3×3(FD)
7
Append FD to ˆFC,v as ˆFl
C,v.
8 Return ˆFC,v
Geometric Transfer
We project the LiDAR point clouds
to multi-view images with camera parameters to get the
sparse depth maps (200 × 112 for nuScenes) for each view.
We combine the original multi-level image features from
FPN [25] with the sparse depth map to obtain the multi-level
depth-aware image features as shown in Alg. 1, where: L is
the scale level number (L = 4 in our experiments); Stem(·)
is a stem block composed of a 3 × 3 convolution, batch
normalization, and a ReLU activation; Residual-Block(·) is
the basic residual block in ResNet-18 [11] with stride 2 for
downsampling. Since we have multi-view images describ-
ing the surrounding scene, we run Alg. 1 separately for each
view with the shared network parameters.
Semantic Transfer
Given the dense BEV features FL ∈
RH×W ×C, only a few positions are indeed covered by
the LiDAR point clouds.
For a position (xj, yj), xj ∈
{1, 2, . . . , W}, yj ∈{1, 2, . . . , H} on the BEV feature map
occupied by point clouds, we denote the median height of
the points in this pillar (xj, yj) as zj. We project all these
{(xj, yj, zj)} from LiDAR coordinates to the multi-view
images. We fetch these image features at these positions
(max-pooling to aggregate multi-scale image features), and
we combine them with the original corresponding BEV fea-
tures through element-wise addition. The added features
serve as the queries to interact with the multi-scale image
features through a deformable-attention module and a feed-
forward network. We add the positional embeddings, which
are the 2D locations on the images, to the queries, keys, and
values. This process is run separately for images of each
view. If (xj, yj, zj) can be projected to multiple views, we
perform max-pooling to aggregate the updated queries from
multiple views. Each updated query replaces the original
BEV features FL at (xj, yj) to obtain the semantic-aware
BEV features ˆFL, which will be used for the query initial-
ization of the LiDAR detector (Sec. B.3).
B.2. Prediction Head
We use two different prediction heads for 3D objects in
the perspective view and the LiDAR view.
Perspective View Head
The perspective view prediction
head is designed for the camera detector to detect objects in
the camera coordinates. The head includes six independent
MLPs as follows:
1. It predicts the category of each object. The output di-
mension is the number of object categories, denoting
the conﬁdence of each category.
2. For the image of each view, it regresses the offset of
the projected center of each object in the image from
the reference points indicated by the positional embed-
ding. The output dimension is two, denoting the XY
coordinate separately.
3. For the image of each view, it estimates the depths of
each object. The output dimension is one.
4. It regresses the logarithms of the XYZ scale of the 3D
bounding box. The output dimension is three.
### Page 15

5. It predicts the angle of each object around the vertical
axis (Y-axis in the camera coordinate). The output di-
mension is two, denoting the sin and cos of this angle.
6. It predicts the velocity in the horizontal plane (XZ-
plane in the camera coordinate space).
The output
dimension is two,denoting the velocities along the X-
axis and the Z-axis.
LiDAR View Head
The LiDAR view prediction head is
designed to detect objects in the perspective view. The same
head is used for the LiDAR detector, view transformation,
and the fusion branch with different network weights. The
head includes six independent MLPs as follows:
1. It predicts the category of each object. The output di-
mension is the number of object categories, denoting
the conﬁdence of each category.
2. It regresses the offset of the center of each object on the
BEV plane from the reference points indicated by the
positional embedding. The output dimension is two,
denoting the XY coordinate separately.
3. It regresses the height of each object center. The output
dimension is one.
4. It regresses the logarithms of the XYZ scale of the 3D
bounding box. The output dimension is three.
5. It predicts the angle of each object around the vertical
axis (Z-axis in the LiDAR coordinate space). The out-
put dimension is two, denoting the sin and cos of this
angle.
6. It predicts the velocity in the horizontal plane (XY-
plane in the LiDAR coordinate). The output dimension
is two, denoting the velocities along the X-axis and the
Y-axis.
B.3. Query Initialization
We follow CenterFormer [56] and TransFusion [1] to ini-
tialize our queries using a heatmap, which helps to acceler-
ate the convergence and reduce the number of queries.
Initialization for LiDAR Detector
We splatter the
bounding box centers on the BEV onto a category-aware
heatmap Y ∈[0, 1]H×W ×K [18, 54], where K is the
category number, with a Gaussian kernel Yx,y,ki
=
exp

(x−cL
x,i)2+(y−cL
y,i)2
2σ2
i

, where ki is the category of the
i-th object, (cx,i, cy,i) is its center on the BEV, and σi is
a standard deviation related to the object scale as done in
[1]. The heatmap is calculated for each object separately,
and we combine the multiple-object heatmaps by using the
maximal value at each location. A dense head composed
of 3 × 3 convolutions are attached to the BEV features
ˆFL, which is augmented by the semantic transfer. Posi-
tions p0
L,i ∈R2, i = 1, . . . , NL on the BEV with the high-
est conﬁdence scores in maxki ˆYxi,yi,ki are selected as the
reference points on BEV plane, along with their categories
{ki}NL
i=0. The local BEV features at these positions from FL
are fetched. We add the local feature from FL and a learn-
able category embedding {eL
ki}NL
i=0 to get the initial LiDAR
query features Q0
L = {q0
L,i}NL
i=1.
Initialization for Camera Detector
For the camera
modality, 3D box centers are projected into the multi-
view images.
We follow FCOS [40] to divide the ob-
jects of different sizes after projection into certain levels
of multi-scale image features. We set the size thresholds
to 0, 48, 96, 192, +∞. For each bounding box projected on
the image plane, if its max(length, width) falls between
the i-th and i + 1-th threshold, the object is assigned to the
i-th scale level. As we do in the LiDAR modality, corre-
sponding projected centers of each feature level are splat-
tered onto a heatmap.
We also get the reference points
p0
C = {p0
C,i}NC
i=1 with top conﬁdence scores from the multi-
view image features, as well as the corresponding categories
{ki}NC
i=0. The corresponding features from the depth-aware
image features ˆFC are added with the learnable category
embedding {eC
ki}NC
i=0 to get the initial camera query fea-
tures Q0
C = {q0
L,i}NL
i=1. It is worth mentioning that 3D
objects are projected to multi-scale multi-view images, so
initial queries come from the image features from different
views and different scales.