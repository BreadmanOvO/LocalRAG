# FreqPDE: Rethinking Positional Depth Embedding for Multi-View 3D Object Detection Transformers

**Source**: arXiv:2510.15385

**Type**: Academic Paper

---

## Page 1

FreqPDE: Rethinking Positional Depth Embedding for Multi-View 3D Object
Detection Transformers
Haisheng Su1,3♠
Junjie Zhang2,3♠♡
Feixiang Song3
Sanping Zhou2
Wei Wu3
Nanning Zheng2B
Junchi Yan1B
1Shanghai Jiao Tong University, 2Xi’an Jiaotong University, 3SenseAuto Research
{suhaisheng,yanjunchi}@sjtu.edu.cn, hooz1009@stu.xjtu.edu.cn, nnzheng@mail.xjtu.edu.cn
Abstract
Detecting 3D objects accurately from multi-view 2D im-
ages is a challenging yet essential task in the field of au-
tonomous driving. Current methods resort to integrating
depth prediction to recover the spatial information for ob-
ject query decoding, which necessitates explicit supervision
from LiDAR points during the training phase.
However,
the predicted depth quality is still unsatisfactory such as
depth discontinuity of object boundaries and indistinction
of small objects, which are mainly caused by the sparse
supervision of projected points and the use of high-level
image features for depth prediction. Besides, cross-view
consistency and scale invariance are also overlooked in
previous methods. In this paper, we introduce Frequency-
aware Positional Depth Embedding (FreqPDE) to equip 2D
image features with spatial information for 3D detection
transformer decoder, which can be obtained through three
main modules. Specifically, the Frequency-aware Spatial
Pyramid Encoder (FSPE) constructs a feature pyramid by
combining high-frequency edge clues and low-frequency se-
mantics from different levels respectively. Then the Cross-
view Scale-invariant Depth Predictor (CSDP) estimates the
pixel-level depth distribution with cross-view and efficient
channel attention mechanism. Finally, the Positional Depth
Encoder (PDE) combines the 2D image features and 3D
position embeddings to generate the 3D depth-aware fea-
tures for query decoding. Additionally, hybrid depth super-
vision is adopted for complementary depth learning from
both metric and distribution aspects. Extensive experiments
conducted on the nuScenes dataset demonstrate the effec-
tiveness and superiority of our proposed method.
1. Introduction
In recent years, great advancements in perception technol-
ogy [22, 44, 47, 54] have been witnessed in autonomous
♠Equal Contribution.
B Corresponding Authors.
♡Work done during an internship at SenseAuto Research.
(a) Input Image
(b) Projected LiDAR Points 
(c) Pseudo Depth Map
(d) Image Coverage of Projected Points with Different Input Resolution
Figure 1. Illustration of motivation. (a) Input image with a fixed
resolution. (b) Missing depth supervision of distant vehicles (red
circle) with sparse projected LiDAR points. (c) Pseudo depth map
complements implicit distribution priors additionally. (d) Cover-
age comparisons of projected points with different input resolution
and downsampling factors.
driving. Compared to LiDAR-based 3D perception applica-
tions, the camera-based paradigm has drawn increasing at-
tention from both industrial and academic researchers ow-
ing to the controllable cost. However, recovering the 3D
spatial information from multi-view 2D images is an ill-
posed problem, and current methods usually integrate the
depth prediction task for introducing additional supervision.
Literally, recent works attempt to exploit depth informa-
tion in various ways. Pseudo-LiDAR [54] estimates dense
depth map and generates the pseudo 3D lidar points us-
ing the camera extrinsic which can be processed with the
off-the-shelf LiDAR-based 3D detector. CaDDN [44] and
BEVDet series [16–18] predict the pixel-wise probabilistic
depth distribution and then project the 2D image features
to the 3D space following the Lift-Splat-Shoot (LSS) [40]
paradigm. BEVDepth [25] introduces the explicit super-
vision of the depth branch with the projected lidar points
arXiv:2510.15385v1  [cs.CV]  17 Oct 2025


## Page 2

as shown in Fig. 1 (b), which increases the depth pre-
diction accuracy and detection performance significantly.
3DPPE [45] proposes the 3D point positional encoding to
generate position-aware 3D features and performs the posi-
tion embedding transformation following [32]. Undoubt-
edly, the quality of predicted depth determines the per-
formance upper limit of depth-based detectors. However,
the predicted depth quality remains unsatisfactory in three
main aspects: (1) only high-level image features are used
for depth prediction, leading to depth discontinuity of ob-
ject boundaries and indistinction of small objects, owing
to the loss of local details during the downsampling pro-
cess. (2) Sparse supervision of projected lidar points also
accounts for incomplete depth learning. As shown in Fig. 1
(d), the image coverage of projected lidar points decreases
significantly with the increase of input image resolution.
(3) Moreover, the independent visual feature extraction and
depth prediction inevitably neglect the cross-view consis-
tency and scale invariance.
To this end, we propose FreqPDE, a frequency-aware po-
sitional depth embedding, to equip 2D visual features with
high-quality spatial information for the 3D detection trans-
former decoder. Specifically, three main modules are de-
signed to relieve the above issues accordingly. First, the
Frequency-aware Spatial Pyramid Encoder (FSPE) handles
the extracted visual features to construct a multi-scale fea-
ture pyramid through combining high-frequency local de-
tails and low-frequency global semantics from different lev-
els respectively. Then the Cross-view Scale-invariant Depth
Predictor (CSDP) is designed to perform hierarchy depth
prediction with cross-view attention and efficient channel
attention, ensuring cross-view consistency and scale invari-
ance. Besides, hybrid depth supervision is introduced to
facilitate complementary depth learning from both explicit
metric and implicit distribution aspects, with the help of
sparse lidar maps and dense pseudo depth maps as shown
in Fig. 1 (b) and (c) respectively. Finally, the Positional
Depth Encoder (PDE) combines the 2D image features and
multi-scale positional embeddings to generate 3D depth-
aware features, which are adapted for object query decoding
with a detection transformer. In sum, the main contributions
of our work are three folds:
• We propose a Frequency-aware Positional Depth En-
coder for high-quality depth prediction, named Fre-
qPDE, which is proven to be effective for improving 3D
detection transformers from multi-view perspectives.
• We introduce a plug-and-play depth predictor to per-
form hierarchy depth prediction upon the constructed
feature pyramid with frequency enhancement. Besides,
cross-view attention and camera-aware channel attention
are conducted consecutively to ensure cross-view consis-
tency and scale invariance under the hybrid supervision
of both explicit metric and implicit distribution levels.
• Extensive
experiments
conducted
on
nuScenes
[7]
demonstrate the prominent effectiveness of our proposed
FreqPDE, revealing the great potential of the high-quality
positional embedding for 3D detection transformers.
2. Related Work
2.1. Multi-view 3D Object Detection
The advancement of autonomous systems underscores the
critical role of surround-view 3D object detection for safety
and comfort [15, 16, 25, 26, 30, 53].
The BEVDet se-
ries [15–18, 25] constructs Bird-Eye-View (BEV) features
with 2D to 3D view transformation. DETR3D [53] em-
ploys transformers to implicitly convert image features and
object queries from 2D to 3D, enabling direct 3D ob-
ject detection following the DETR [8] paradigm.
Po-
lar DETR [11] enhances feature interaction by reformu-
lating positional parameterization. BEVFormer [26] inte-
grates both spatial and temporal information through inter-
action with spatial and temporal spaces via predefined grid-
shaped BEV queries.
SparseBEV [30] introduces scale-
adaptive self-attention and adaptive spatio-temporal sam-
pling to boost performance.
StreamPETR [50] achieves
performance comparable to LiDAR-based methods by em-
ploying object-centric temporal modeling and maintaining
a memory queue for storing historical object queries.
2.2. Frequency Domain Learning
In recent years, frequency domain analysis methods, central
to signal processing, have seen significant advancements in
deep learning.
Works [41, 56] discovered deep learning
models tend to prioritize learning low-frequency informa-
tion. Richard Zhang [62] and Zou et al. [64] applied clas-
sical anti-aliasing from signal processing to deep learning,
enhancing the shift-equivariance of the model. FLCP [12]
proposed an alias-free down-sampling method to address
the reduction in model robustness caused by frequency
aliasing. Chen et al. [9] improves instance segmentation
accuracy in low-light environments by suppressing high-
frequency noise in image features. SSAH [35] suggests that
perturbing high-frequency noise causes intra-category sim-
ilarity inconsistency. DFSA [36] argues that the absence
of high-frequency signals leads to boundary displacement.
FreqFusion [10] employs both high-pass and low-pass fil-
ters to retain both high-frequency and low-frequency infor-
mation, thereby addressing intra-category similarity incon-
sistency and boundary displacement.
3. Our Approach
3.1. Overview Architecture
The overall framework of the proposed FreqPDE is illus-
trated in Fig. 2, which aims to improve the 3D detec-


## Page 3

Multi-view Images
Decoder
Initial Object
Queries
Hybrid Supervision
Detection Results
Visual
Backbone
Multi-Scale / View
Image Features
Frequency-aware 
Spatial Pyramid 
Encoder
Frequency-Aware
Pyramid Features
Positional 
Depth Encoder
Camera
Parameters
Sparse LiDAR Depth Maps
Dense Pseudo Depth Maps
Cross-view 
Scale-invariant 
Depth Predictor
Predicted Depth Maps
3D Depth-aware 
Image Features
Figure 2. Overview of our proposed FreqPDE framework. FreqPDE first extracts multi-scale features from multi-view images using an
off-the-shelf visual encoder. Then the FSPE module constructs a feature pyramid through combining high-frequency edge clues and low-
frequency semantics from low-level and high-level image features respectively. The CSDP module estimates multi-scale depth maps with
cross-view attention based on the frequency-enhanced features. Finally, the PDE module encodes both semantic features and geometric
depth embedding to generate 3D depth-aware features for object query decoding. Hybrid depth supervision is introduced to facilitate
complementary depth learning.
tion performance from multi-view perspectives by introduc-
ing frequency-aware positional depth embedding. Specifi-
cally, FreqPDE mainly consists of three modules, namely
FSPE, CSDP and PDE. First, the FSPE module is designed
to encode multi-scale spatial features by combining high-
frequency edge clues and low-frequency semantics from
different levels in a pyramidal structure, respectively. Then
the CSDP module conducts hierarchy depth prediction with
cross-view consistency and scale invariance. Finally, the
PDE module encodes the positional depth values to obtain
depth-aware 3D features through element-wise addition of
image features and 3D PE, which are used to decode object
queries for 3D detection.
3.2. Frequency-aware Spatial Pyramid Encoder
Previous detection frameworks typically implement a Fea-
ture Pyramid Network (FPN) [28] to reconstruct a set of
multi-scale features with abundant semantic information in
a top-down pathway. However, Sapa [34] discovered that
outputs from the simple and direct interpolation used by
FPN often lean towards excessive smoothness, resulting in
boundary displacement [10] issue. Meanwhile, there exists
the spectral bias in DCNNs that these networks prioritize
learning the low-frequency modes [41], which leads to the
lack of high-frequency information in high-level features,
affecting the depth prediction at the edges of 3D objects
and localization accuracy.
To overcome the aforementioned problems, we design
the FSPE module which is composed of several blocks and
each block consists of high-frequency boundary enhance-
ment and low-frequency semantic extraction modules. Tak-
ing one layer of FSPE as an example, with high-level fea-
tures Sn ∈RC×H×W and low-level features Sn−1 ∈
RC×2H×2W as input, the previous method [28] directly in-
terpolates and upsamples Sn which will be added to Sn−1
directly, this process can be formulated as:
S′
n−1 = fup(Sn) + Sn−1,
(1)
where fup indicates upsampling methods, S′
n−1 denotes the
fused low-level feature which is also the high-level fea-
ture input of the next block in the top-down multi-scale
feature-building pathway. Instead, with the same inputs, our
method can be formulated as:
S′
n−1 = fiDWT(flf(Sn−1), fhf(Sn)) + Sn−1,
(2)
where flf and fhf denotes the low-frequency semantic ex-
traction and high-frequency boundary enhancement mod-
ules, which can utilize high and low-frequency information
adaptively, fiDWT is the inverse discrete wavelet transform
(iDWT), as illustrated in Fig. 3.
Low-frequency Semantic Extraction.
To eliminate the
smooth and inaccurate boundaries caused by simple inter-
polation from high-level features during the upsampling
process, we utilize low-pass filters which are generated dy-
namically [64] to effectively extract the global semantics of


## Page 4

high-level features as shown in Fig. 3. In particular, we take
the high-level features Sn as input to predict spatial-variant
low-pass filters with a learnable method, which comprises a
3 × 3 convolutional layer and a Softmax layer, this can be
represented as:
W = Softmax(Conv3×3(Sn)),
(3)
where W ∈RK2×H×W , K is the kernel size of predicted
low-pass filters, each of the K2 channels indicates a weight
at one of the K × K locations within the filters, and the
kernel-wise softmax is utilized to constrain these weights to
be positive and sum to one. Then we apply W to input Sn
to generate context-aware high-level feature as follows:
Si,j
n =
X
p,q∈Ω
W i,j
p,q · Si+p,j+q
n
,
(4)
where Si,j
n
is the output feature at location (i, j) and Ωis
the K × K region surrounding positions (i, j), in which we
apply the pixel-wise product and sum together, new feature
Sn will be used for reconstructing low-level feature after-
ward.
High-frequency Boundary Enhancement.
Inspired by
some lossless wavelet methods [13], we introduce DWT
to preserve high-frequency information from low-level fea-
tures of higher resolution. Given input low level feature
Sn−1, DWT is performed first to split Sn−1 into 4 sub-
components(LL, LH, HL, HH) as described in Fig. 3,
where all the components have identical shapes with Sn.
Although the low-frequency components LL possess cer-
tain global semantic information, they lack the response to
salient features due to the average pooling operation [60].
Therefore, we add high-level feature Sn with LL to con-
struct a fresh component LL′ which can be performed with
iDWT operation. This method not only avoids the boundary
displacement issue caused by upsampling methods, but also
losslessly retains the high-frequency details corresponding
to the larger size. Finally, we add the original low-level
feature Sn−1 to the new feature residually to obtain the
frequency-aware feature S′
n−1, this can be formulated as:
S′
n−1 = fiDWT(LL′, (LH, HL, HH)) + Sn−1
(5)
3.3. Cross-view Scale-invariant Depth Prediction
Previous works [46, 51] have demonstrated that features at
different levels significantly enhance the detection perfor-
mance for objects of various sizes, which inspires us to
build a multi-scale depth head to predict a more accurate
depth map. Specifically, in contrast to the other depth pre-
diction framework, we exploit multi-scale output features of
FSPE to predict the depth maps of the corresponding size
with hybrid-depth module [45], the structure of our depth
head is shown in Fig. 4.
LL
HL
LH
HH
Conv
Softmax
Low-frequency Semantic Extraction
High-frequency Boundary Enhancement
Fusion
(N, C, 2H, 2W)
(N, C, H, W)
(N, C, 2H, 2W)
Low-pass Filter 
Generator
*
𝐾×𝐾
Low-level Features 𝑺𝒏"𝟏
High-level Features 𝑺𝒏
Frequency-aware Features 𝑺𝒏"𝟏
$
*
Convolve
Pixel-wise addition
Low-pass filter
Replace
HH: Diagonal high-frequency component
LH: Horizontal middle-frequency component
HL: Vertical middle-frequency component
LL:  Low-frequency component
DWT
IDWT
Wavelet Transform
DWT
Figure 3. Illustration of FSPE module. After encoding multi-scale
features, low-frequency semantics are extracted from the high-
level features through adaptive low-pass filters. Then the Discrete
Wavelet Transform (DWT) is conducted on the low-level features
to decompose four sub-components of different frequencies. The
low-frequency component of low-level features is combined with
the extracted high-level semantics for boundary enhancement.
Cross-view Modeling. With multi-view image feature in-
put, it is crucial to ensure consistency across different per-
spectives during the feature extraction and depth predic-
tion process. Therefore, we introduce a novel Cross-view
Width Attention (CWA) block to facilitate interaction in
the overlapping regions between the image features of ad-
jacent views. As illustrated in Fig. 4 (d), we first mask
the feature with a fixed ratio µ to ignore the influence
of non-overlapping regions. Then we reshape the multi-
view features into groups according to their row indices and
the width-attention [31] mechanism is performed to ensure
width-wise features only interact with the others belonging
to the same row. Moreover, to avoid increasing the model
parameters and computation significantly, we only insert
one CWA block to the features at each layer.
Scale-invariant Learning. To associate depth prediction
with the camera intrinsics, we scale up the dimension of
camera intrinsics to the features with an MLP layer, then
we introduce ECANet [48] to re-weight the input features
Fi,j ∈RC×Hi×Wi, this process can be written in:
F ′
i,j = ECA(Fi,j|MLP(ζiKj)),
(6)
where i = 1, · · · , l, indicate the level of input features,
j = 1, · · · , 6, indicate the index of the cameras, Kj is the
corresponding camera intrisics and ζi is the downsampling
scale. In this way, each level feature is able to be aware of
the specific spatial location with the aid of the equivalent
camera intrinsic.
Hierarchy Depth Prediction. We individually predict the
regressed depth DR
i,j ∈RHi×Wi [25] and the categori-
cal depth DC
i,j ∈RHi×Wi [52] to generate more reliable
depth maps. However, in previous methods, depth range
[dmin, dmax] is divided into multiple fixed-position bins, ne-
glecting the variations among samples and pixels. To han-
dle this issue, we implement the multi-scale pixel-wise re-
finement of the bin [4]. Specifically, we first predict the


## Page 5

Efficient Channel 
Attention
Categorical Depth 
Regressed Depth 
𝟏
𝟒
𝑫𝟎,𝒋
𝐑
𝑷𝟎,𝒋𝑫𝟎,𝒋
𝐂
MLP
Conv
Block
𝝎
(a) Multi-scale Cross-view Modeling
(b) Hierarchy Depth Prediction 
(d) Cross-view Width Attention
𝟏
𝟏𝟔
MLP
𝑫𝟐,𝒋
𝐑
𝑷𝟐,𝒋𝑫𝟐,𝒋
𝐂
CWA
𝟏
𝟖
MLP
𝑫𝟏,𝒋
𝐑
𝑷𝟏,𝒋𝑫𝟏,𝒋
𝐂
CWA
CWA
ConvBlock
ConvBlock
Updated Feature
View 1
View N
Masked Feature
Width Attention
Original Feature
𝑵×𝑪×𝑯×𝑾
𝑵×𝑪×𝑯×𝑾
𝑯×𝑪×(𝑵𝑾)
𝑵×𝑪×𝑯×𝑾
View 1
View N
…
…
Intrinsic
Parameters
𝑪×𝑯×𝑾
𝑪×𝑯×𝑾
(c) Efficient Channel Attention
Conv(𝒌)
MLP
𝝍(𝒄)
𝑘= 𝜓𝑐= | 𝑙𝑜𝑔! 𝑐
𝛾
+ 𝑏
𝛾|"##
𝑪×𝟏
𝝎
𝝎
Figure 4. Detailed structure of CSDP module. (a) illustrates the process of visual feature re-weighting with efficient channel attention and
cross-view attention from different levels to achieve cross-view consistency and scale invariance respectively. (b) describes the details of
hierarchy depth prediction, where both categorical and regressed depth are predicted accordingly, which are fused with a hyper-parameter
ω to generate the final depth map. (c) and (d) show the process of efficient channel attention and cross-view attention respectively.
original depth bins cl,j from the highest feature F ′
l,j at each
pixel position with an MLP layer, then cl,j is adjusted to
generate another set of depth bins for next layer feature of
higher resolution. Take the ith layer feature F ′
i,j as an ex-
ample, an MLP layer is introduced to predict N attractor
points for each pixel position. The adjusted bin center is
ci,j = ci+1,j + △ci,j, this adjustment can be given by:
△ci,j =
N
X
n=1
pn −ci+1,j
1 + α|pn −ci+1,j|β ,
(7)
where pn is the position of N attractor points, ci+1,j is the
generated bin center of higher level feature, α and β are
hyper-parameters. Meanwhile, we predict the probabilis-
tic Pi,j over these bins for each pixel, P ∈RNB×Hi×Wi,
where NB denotes the number of bins for each pixel. Thus,
the categorical depth can be formulated as:
DC
i,j =
NB
X
k=1
P k
i,j × ci,j.
(8)
Finally, we fuse DR
i,j and DC
i,j with a hyper-parameters
ω, the final depth prediction Di,j can be represented as:
Di,j = ωDC
i,j + (1 −ω)DR
i,j.
(9)
3.4. Hybrid Depth Supervision
To address the issue of insufficient supervision for depth es-
timation due to sparse point clouds, we introduce hybrid
depth supervision, which compose of two parts, explicit
metric supervision and implicit distribution supervision.
Explicit Metric Supervision.
Similar to other meth-
ods [16, 25], the LiDAR point cloud data is introduced and
converted to image view with rotation and translation ma-
trix, then we discard the projected 2.5D points that exceed
the resolution of corresponding multi-view features. Con-
sequently, the sparse one-hot pixel-wise depth ground-truth
label Dgt is acquired and will be the explicit metric super-
vision for the final depth prediction Dpred.
Implicit Distribution Supervision. We exploit a founda-
tion model, DepthAnything [58], to generate the pseudo
depth label for dense supervision. However, the high gener-
alization ability of DepthAnything comes with the neglect
of scale and shift of each sample during multi-dataset joint
training [5, 42]. Accordingly, the pseudo depth maps pro-
vide implicit distribution prior instead of exact metric depth
values, which are more reliable and general.
To fully leverage the strengths of the foundation model,
we exploit the generated relative depth results as pseudo
labels Dpd for extra supervision of our depth prediction
Di,j. Specifically, we first take the reciprocal of the pre-
dicted depth results Di,j, then perform mean-variance nor-


## Page 6

malization [1] to generate predicted relative depth results
d
1
Di,j , which ignore sample-wise scale and shift variations
and can be supervised by pre-generated pseudo labels Dpd.
3.5. Positional Depth Encoder and Query Decoder
3D Positional Depth Encoder. For the purpose of obtain-
ing depth-aware 3D features that encompass both seman-
tic features and geometric embeddings, we propose the 3D
PDE, similar to 3DPPE [45], which introduces point-level
positional embedding. Specifically, we generate 3D points
based on the predicted depth map Di,j and transform them
into LiDAR coordinates to serve as position embeddings.
This process can be expressed as
PEj = Sine(fproj(Di,j, Kj, Ej)),
(10)
Where Sine represents the positional embedding function
used in DETR [8], and fproj denotes the transformation
process from 2D points to 3D space using the camera in-
trinsics Kj and extrinsics Ej. Subsequently, an element-
wise addition is performed between the positional embed-
ding PEj and the image features to construct the 3D depth-
aware feature set F3D.
Query Decoder. We adopt the transformer decoder struc-
ture from StreamPETR [50] to produce the final detection
results. Specifically, a fixed number of learnable queries
are initially generated and then processed through the prop-
agation decoder, utilizing the 3D features F3D and infor-
mation from a pre-defined memory queue to facilitate spa-
tial and temporal interactions. Concurrently, with the as-
sistance of motion-aware layer normalization, feature ag-
gregation, and the hybrid attention layer within the prop-
agation transformer, the queries are progressively refined,
ultimately yielding the final detection results.
3.6. Detection Head and Loss
During training stage, we exploit sparse projected LiDAR
depth Dgt and dense pseudo relative depth Dpd simulta-
neously, where smooth L1 loss [51] and MSE loss [6] are
used:
Ldepth = λsLs(Di,j, Dgt) + λmLm(
d
1
Di,j
, d
Dpd),
(11)
where λs and λm are the hyper-parameters.
Total Loss
given the depth prediction loss Ldepth, 2D focal sampling
loss [49] Lsampl and 3D bounding box regression loss Lreg,
we adopt the Hungarian Matching to achieve label assign-
ment and the total loss can be formulated as:
L = λ1Ldepth + λ2Lsamp + λ3Lreg,
(12)
where λ1, λ2 and λ3 are hyper-parameters to balance the
different losses.
4. Experiments
4.1. Dataset and Metrics
All experiments are conducted on the nuScenes [7] dataset,
which is a widely used public dataset specifically designed
for autonomous driving research. The dataset contains six
calibrated high-resolution cameras, which cover the sur-
rounding view of the road. It consists of 700 training, 150
validation, and 150 testing sequences, with 34K annotated
key frames and 10 object categories. For the 3D detection
task, we use nuScenes Detection Score (NDS), mean Av-
erage Precision (mAP), and adopt other official True Posi-
tive (TP) metrics, including mean Average Translation Er-
ror (mATE), mean Average Scale Error (mASE), mean Av-
erage Orientation Error (mAOE), mean Average Velocity
Error (mAVE), mean Average Attribute Error (mAAE).
4.2. Implementation Details
We set StreamPETR [50] as the baseline to conduct ex-
periments with ResNet50, ResNet101 [14], and VoVNet-
99 [51] backbones on the nuScenes [7] dataset without
any test-time augmentation or future information. The pre-
trained weights for ResNet models were obtained from
ImageNet-1K [21] and nuImages datasets, while the pre-
trained weights for VoVNet were provided by DD3D [38].
For the hierarchy depth prediction, we set α to 300.0, β
to 2.0, and ω to 0.5. For the balancing factors of differ-
ent losses, we set λ1, λ2, and λ3 to 1.0, 0.5 and 1.0. We
adopt image data augmentations, including random crop-
ping, scaling, flipping, and rotation. All models are trained
with the streaming video training method [50] on 4 NVIDIA
A100 GPUs with 24 epochs for V2-99 backbone and 90
epochs for ResNet backbone, using AdamW optimizer. The
learning rate is set to 4e-4 and batch size is set to 16. Fur-
thermore, all pseudo labels are generated offline and stored
as NPZ files, which enable direct loading during training
process without additional computational overhead.
4.3. Main Results
We compare the proposed FreqPDE with previous state-
of-the-art multi-view 3D object detectors on the nuScenes
val set. As shown in Tab. 1, our method achieves 56.2%
NDS and 46.3% mAP performance with the image size of
256 and ResNet50 backbone which is pre-trained on nuIm-
ages, surpassing other SOTA methods and outperforming
the baseline(StreamPETR) by 1.2% NDS and 1.3% mAP.
When adopting the image size of 320 and V2-99 backbone,
our method has an obvious performance improvement over
the baseline with NDS of 1.4% and mAP of 2.4%. Further-
more, under the setting of ResNet101 and high-resolution
input, FreqPDE also achieves the highest performance met-
rics, exceeding the state-of-the-art method (Far3D) by 0.7%
NDS and 0.9% mAP. Tab. 2 presents the performance met-


## Page 7

Table 1. Comparison of other methods on the nuScenes val set. † The backbone benefits from perspective pretraining. The best is in bold.
Method
Backbone
Input Size
NDS↑
mAP↑
mATE↓
mASE↓
mAOE↓
mAVE↓
mAAE↓
BevDet4D [16]
ResNet50
256 × 704
45.7
32.2
0.703
0.278
0.495
0.354
0.206
PETRv2 [33]
ResNet50
256 × 704
45.6
34.9
0.700
0.275
0.580
0.437
0.187
BEVStereo [24]
ResNet50
256 × 704
50.0
37.2
0.598
0.270
0.438
0.367
0.190
SOLOFusion [39]
ResNet50
256 × 704
53.4
42.7
0.567
0.274
0.511
0.252
0.181
FreqPDE (Ours)
ResNet50
256 × 704
54.3
43.5
0.577
0.270
0.442
0.257
0.199
Sparse4Dv2† [29]
ResNet50
256 × 704
53.8
43.9
0.598
0.270
0.475
0.282
0.179
BEVFormerv2† [57]
ResNet50
-
52.9
42.3
0.618
0.273
0.413
0.333
0.188
StreamPETR† [50]
ResNet50
256 × 704
55.0
45.0
0.613
0.267
0.413
0.265
0.196
SparseBEV† [30]
ResNet50
256 × 704
55.8
44.8
0.581
0.271
0.373
0.247
0.190
FreqPDE (Ours) †
ResNet50
256 × 704
56.2
46.3
0.575
0.268
0.405
0.245
0.203
StreamPETR† [50]
V2-99
320 × 800
57.2
48.2
0.602
0.256
0.372
0.267
0.192
FreqPDE (Ours) †
V2-99
320 × 800
58.6
50.6
0.576
0.261
0.375
0.253
0.200
Far3D† [19]
ResNet101
512 × 1408
59.4
51.0
0.551
0.258
0.372
0.238
0.195
Sparse4Dv2† [29]
ResNet101
512 × 1408
59.4
50.5
0.548
0.268
0.348
0.239
0.184
StreamPETR† [50]
ResNet101
512 × 1408
59.2
50.4
0.569
0.262
0.315
0.257
0.199
FreqPDE (Ours) †
ResNet101
512 × 1408
60.1
51.9
0.562
0.258
0.324
0.242
0.196
Table 2. Comparison of other methods on nuScenes test set. These results are reported without test-time augmentation, model ensem-
bling, and any future information. The best is in bold.
Method
Backbone
Input Size
NDS↑
mAP↑
mATE↓
mASE↓
mAOE↓
mAVE↓
mAAE↓
BEVDepth [25]
V2-99
640 × 1600
60.0
50.3
0.445
0.245
0.378
0.320
0.126
CAPE-T [55]
V2-99
640 × 1600
61.0
52.5
0.503
0.242
0.361
0.306
0.114
FB-BEV [30]
V2-99
640 × 1600
62.4
53.7
0.439
0.250
0.358
0.270
0.128
HoP [63]
V2-99
640 × 1600
61.2
52.8
0.491
0.242
0.332
0.343
0.109
StreamPETR [50]
V2-99
640 × 1600
63.6
55.0
0.479
0.239
0.317
0.241
0.119
SparseBEV [30]
V2-99
640 × 1600
63.6
55.6
0.485
0.244
0.332
0.246
0.117
Sparse4Dv2 [29]
V2-99
640 × 1600
63.8
55.6
0.462
0.238
0.328
0.264
0.115
Ours
V2-99
640 × 1600
64.2
56.0
0.468
0.241
0.315
0.242
0.115
rics on the nuScenes test set, in terms of the both metric
NDS and mAP, FreqPDE have achieved the SOTA perfor-
mance, surpassing HoP, StreamPETR and Sparse4dv2.
4.4. Ablation Study
In our ablation experiments, we consistently use V2-99 with
nuImage pretraining weights. The input image size is set to
320 × 800.
Component Analysis. We conduct ablation studies to study
the effectiveness of each proposed module. As shown in
Tab. 3, compared with the baseline, FSPE brings 0.5 % NDS
performance improvement, indicating the effectiveness of
frequency information in detection tasks. And CSDP ob-
tains 1.2 % mAP improvement, which is non-trivial in pro-
moting the quality of object position regression with the
additional depth prediction as an auxiliary task.
More-
over, with the help of PDE, our method can achieve consis-
tent 0.4% NDS performance improvement by exploiting the
depth-aware position embedding to construct the 3D fea-
tures. Combining all designs, FreqPDE achieves a convinc-
ing performance upon the baseline, which demonstrates the
Table 3. Component analysis of FreqPDE on nuScenes val set.
FSPE
CSDP
PDE
NDS ↑
mAP ↑
✗
✗
✗
57.2
48.2
✓
✗
✗
57.7
48.8
✗
✓
✗
57.6
49.4
✗
✓
✓
58.0
49.9
✓
✓
✓
58.6
50.6
effectiveness of our proposed method.
Ablation for design choices in FSPE module.
In our
Frequency-aware Spatial Pyramid Encoder, high-frequency
and low-frequency information are introduced for differ-
ent usages, namely boundary enhancement and semantic
extraction.
As shown in Tab. 4, introducing the high-
frequency information brings significant improvement in
mAP metric than NDS, which achieves a 1.0% increase.
With the combination of low-frequency and high-frequency
information, our method results in a 1.8% increase in mAP,
reflecting the necessity of enhanced boundary and global
semantic for 3D object detection.


## Page 8

Table 4. Ablation for Frequency-aware Spatial Pyramid Encoder.
Low-Frequency
High-Frequency
NDS ↑
mAP ↑
✗
✗
57.8
49.2
✗
✓
57.9
49.7
✓
✗
58.1
49.6
✓
✓
58.2
50.1
Table 5. Ablation of Computation Consumption.
Method
Backbone
Neck
Head
Total
NDS
FPS
StreamPETR
66.3MB
1.0MB
11.8MB
79.1MB
57.2
10.7
20.1ms
0.8ms
71.3ms
92.2ms
FreqPDE
66.3MB
4.1MB
29.9MB
100.3MB
58.6
8.8
20.1ms
3.5ms
88.8ms
112.4ms
(+1.4)
FreqPDE-L1
66.3MB
2.1MB
16.6MB
85.0MB
58.1
10.2
20.1ms
1.6ms
76.7ms
98.4ms
(+0.9)
Table 6. Ablation for Cross-view Scale-invariant Depth Predictor.
HDP
ECA
CVA
NDS ↑
mAP ↑
✗
✗
✗
57.7
48.8
✓
✗
✗
58.1
49.8
✓
✓
✗
58.2
50.0
✓
✓
✓
58.6
50.6
Computation Consumption We compared the parameter
count and inference time of different modules in Stream-
PETR and FreqPDE, as shown in Table 5, our method im-
proved NDS by 1.4% at the cost of a 20MB increase in pa-
rameter size, primarily due to the multi-layer structures of
FSPE and CSDP. To address this issue, we also evaluated a
single-layer variant, which reduced the parameter increase
to 6MB while still achieving a 0.9% NDS improvement,
with FPS remaining nearly unchanged. This highlights the
efficiency and resource effectiveness of our approach.
Ablation for design choices in CSDP module. We com-
pare various designs for predicting the depth map in Tab. 6.
The hierarchical depth prediction approach boost the per-
formance with a 2.0% increase in mAP, highlighting the
necessity of depth prediction for addressing scale invari-
ance. Furthermore, incorporating efficient channel attention
and cross-view attention leads to notable improvements of
1.8% mAP and 0.9% NDS, demonstrating the effectiveness
of multi-scale camera parameter embeddings and adjacent
perspective interactions.
Pseudo Depth Label Supervision. To validate the effec-
tiveness of Implicit Distribution Supervision, we analyze
detection performance at different distances, as shown in
Table 7. As the distance increases, the method that com-
bines sparse LiDAR supervision with dense pseudo super-
vision achieves increasingly significant improvements in
NDS. Specifically, dense pseudo labels bring an improve-
ment of 1.9% , while sparse LiDAR labels only bring an
improvement of 0.6% when the distance exceeds 40 me-
ters. Our results demonstrate that pseudo labels notably en-
hance long-range object detection, reinforcing our approach
to mitigating sparse supervision in distant regions.
Table 7. Comparison in different distances. NDS>0, NDS>20,
and NDS>40 represent different evaluation metrics under distance
thresholds of 0, 20, and 40 meters, respectively.
Method
Supervision
NDS>0 ↑
NDS>20 ↑
NDS>40 ↑
Baseline
-
57.2
38.2
13.3
FreqPDE
Sparse
58.4 (+1.2)
39.3 (+1.1)
13.9 (+0.6)
FreqPDE
Sparse + Dense
58.6 (+1.4)
39.7 (+1.5)
15.2 (+1.9)
Figure 5. Feature visualization and intra-category similarity (In-
traSim). The brighter color indicates a higher IntraSim for the car.
4.5. Qualitative Results
To examine the quality of extracted features from the pro-
posed FSPE module, we visualize the image features be-
fore and after using the corresponding module. As shown
in Fig. 5 (a) and (c), with the helpf of high-frequency bound-
ary enhancement module, the feature contours are more dis-
tinct, with more consistent background. We also calculate
the intra-category similarity [10] where the brighter color
shows the high similarity within the same car category, in-
dicating that the feature Fig. 5 (d) obtains more global se-
mantic information than Fig. 5 (b), thanks to the utilization
of low-frequency semantic extraction module.
5. Conclusion
In this paper, we propose the FreqPDE, a novel positional
depth embedding method for multi-view 3D object detec-
tion transformers.
Different from the previous methods,
our work mainly harnesses the frequency-dimensional in-
formation across multi-level features which are encoded to
generate the 3D depth-aware features for complementary
perception. Specifically, we first utilize FSPE to construct
frequency-aware 2D features. Then, CSDP is introduced to
predict the pixel-wise depth map with a hierarchy predic-
tor. Besides, the positional depth encoder generated the 3D
depth-aware features which are fed into the transformer de-
coder to output the final detection results. Furthermore, suf-
ficient experiments have been conducted on the nuScenes
dataset to validate the effectiveness and feasibility of our
proposed components. Finally, we hope FreqPDE could
promote the research of frequency domain and depth in
multi-view 3D object detection.


## Page 9

6. Acknowledgments
This paper is in part supported by National Natural Science
Foundation of China (No. 62088102) and Shanghai Mu-
nicipal Science and Technology Major Project, China (No.
2021SHZDZX0102).
References
[1] Peshawa Jamal Muhammad Ali, Rezhna Hassan Faraj, Erbil
Koya, Peshawa J Muhammad Ali, and Rezhna H Faraj. Data
normalization and standardization: a technical report. Mach
Learn Tech Rep, 1(1):1–6, 2014. 6, 1
[2] Shariq Farooq Bhat, Ibraheem Alhashim, and Peter Wonka.
Adabins: Depth estimation using adaptive bins. In Proceed-
ings of the IEEE/CVF conference on computer vision and
pattern recognition, pages 4009–4018, 2021. 1
[3] Shariq Farooq Bhat, Ibraheem Alhashim, and Peter Wonka.
Localbins: Improving depth estimation by learning local dis-
tributions.
In European Conference on Computer Vision,
pages 480–496. Springer, 2022. 1
[4] Shariq Farooq Bhat, Reiner Birkl, Diana Wofk, Peter
Wonka, and Matthias M¨uller.
Zoedepth: Zero-shot trans-
fer by combining relative and metric depth. arXiv preprint
arXiv:2302.12288, 2023. 4, 1
[5] Reiner Birkl, Diana Wofk, and Matthias M¨uller. Midas v3.
1–a model zoo for robust monocular relative depth estima-
tion. arXiv preprint arXiv:2307.14460, 2023. 5
[6] Christopher M Bishop and Nasser M Nasrabadi.
Pattern
recognition and machine learning. Springer, 2006. 6
[7] Holger Caesar, Varun Bankiti, Alex H Lang, Sourabh Vora,
Venice Erin Liong, Qiang Xu, Anush Krishnan, Yu Pan, Gi-
ancarlo Baldan, and Oscar Beijbom.
nuscenes: A multi-
modal dataset for autonomous driving. In Proceedings of
the IEEE/CVF conference on computer vision and pattern
recognition, pages 11621–11631, 2020. 2, 6
[8] Nicolas Carion, Francisco Massa, Gabriel Synnaeve, Nicolas
Usunier, Alexander Kirillov, and Sergey Zagoruyko. End-to-
end object detection with transformers. In European confer-
ence on computer vision, pages 213–229. Springer, 2020. 2,
6
[9] Linwei Chen, Ying Fu, Kaixuan Wei, Dezhi Zheng, and Fe-
lix Heide. Instance segmentation in the dark. International
Journal of Computer Vision, 131(8):2198–2218, 2023. 2
[10] Linwei Chen, Ying Fu, Lin Gu, Chenggang Yan, Tatsuya
Harada, and Gao Huang.
Frequency-aware feature fusion
for dense image prediction. IEEE Transactions on Pattern
Analysis and Machine Intelligence, 2024. 2, 3, 8
[11] Shaoyu Chen, Xinggang Wang, Tianheng Cheng, Qian
Zhang, Chang Huang, and Wenyu Liu. Polar parametrization
for vision-based surround-view 3d detection. arXiv preprint
arXiv:2206.10965, 2022. 2
[12] Julia Grabinski, Steffen Jung, Janis Keuper, and Margret Ke-
uper. Frequencylowcut pooling-plug and play against catas-
trophic overfitting. In European Conference on Computer
Vision, pages 36–57. Springer, 2022. 2
[13] Amara Graps. An introduction to wavelets. IEEE computa-
tional science and engineering, 2(2):50–61, 1995. 4
[14] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun.
Deep residual learning for image recognition. In Proceed-
ings of the IEEE conference on computer vision and pattern
recognition, pages 770–778, 2016. 6
[15] Bin Huang, Yangguang Li, Enze Xie, Feng Liang, Luya
Wang, Mingzhu Shen, Fenggang Liu, Tianqi Wang, Ping
Luo,
and Jing Shao.
Fast-bev:
Towards real-time
on-vehicle bird’s-eye view perception.
arXiv preprint
arXiv:2301.07870, 2023. 2
[16] Junjie Huang and Guan Huang. Bevdet4d: Exploit tempo-
ral cues in multi-camera 3d object detection. arXiv preprint
arXiv:2203.17054, 2022. 1, 2, 5, 7
[17] Junjie Huang and Guan Huang. Bevpoolv2: A cutting-edge
implementation of bevdet toward deployment. arXiv preprint
arXiv:2211.17111, 2022.
[18] Junjie Huang, Guan Huang, Zheng Zhu, Yun Ye, and Dalong
Du. Bevdet: High-performance multi-camera 3d object de-
tection in bird-eye-view. arXiv preprint arXiv:2112.11790,
2021. 1, 2
[19] Xiaohui Jiang, Shuailin Li, Yingfei Liu, Shihao Wang, Fan
Jia, Tiancai Wang, Lijin Han, and Xiangyu Zhang. Far3d:
Expanding the horizon for surround-view 3d object detec-
tion. In Proceedings of the AAAI Conference on Artificial
Intelligence, pages 2561–2569, 2024. 7
[20] Jinyoung Jun, Jae-Han Lee, Chul Lee, and Chang-Su Kim.
Depth map decomposition for monocular depth estimation.
In European Conference on Computer Vision, pages 18–34.
Springer, 2022. 1
[21] Alex Krizhevsky, Ilya Sutskever, and Geoffrey E Hinton.
Imagenet classification with deep convolutional neural net-
works. Advances in neural information processing systems,
25, 2012. 6
[22] Yuqing Lan, Yao Duan, Chenyi Liu, Chenyang Zhu, Yueshan
Xiong, Hui Huang, and Kai Xu. Arm3d: Attention-based re-
lation module for indoor 3d object detection. Computational
Visual Media, 8(3):395–414, 2022. 1
[23] Jae-Han Lee and Chang-Su Kim.
Monocular depth es-
timation using relative depth maps.
In Proceedings of
the IEEE/CVF conference on computer vision and pattern
recognition, pages 9729–9738, 2019. 1
[24] Yinhao Li, Han Bao, Zheng Ge, Jinrong Yang, Jianjian Sun,
and Zeming Li. Bevstereo: Enhancing depth estimation in
multi-view 3d object detection with temporal stereo. In Pro-
ceedings of the AAAI Conference on Artificial Intelligence,
pages 1486–1494, 2023. 7
[25] Yinhao Li, Zheng Ge, Guanyi Yu, Jinrong Yang, Zengran
Wang, Yukang Shi, Jianjian Sun, and Zeming Li. Bevdepth:
Acquisition of reliable depth for multi-view 3d object detec-
tion. In Proceedings of the AAAI Conference on Artificial
Intelligence, pages 1477–1485, 2023. 1, 2, 4, 5, 7
[26] Zhiqi Li, Wenhai Wang, Hongyang Li, Enze Xie, Chong-
hao Sima, Tong Lu, Yu Qiao, and Jifeng Dai. Bevformer:
Learning bird’s-eye-view representation from multi-camera
images via spatiotemporal transformers. In European con-
ference on computer vision, pages 1–18. Springer, 2022. 2
[27] Zhenyu Li, Xuyang Wang, Xianming Liu, and Junjun Jiang.
Binsformer: Revisiting adaptive bins for monocular depth


## Page 10

estimation. IEEE Transactions on Image Processing, 2024.
1
[28] Tsung-Yi Lin, Piotr Doll´ar, Ross Girshick, Kaiming He,
Bharath Hariharan, and Serge Belongie.
Feature pyra-
mid networks for object detection.
In Proceedings of the
IEEE conference on computer vision and pattern recogni-
tion, pages 2117–2125, 2017. 3
[29] Xuewu Lin, Tianwei Lin, Zixiang Pei, Lichao Huang, and
Zhizhong Su. Sparse4d v2: Recurrent temporal fusion with
sparse model. arXiv preprint arXiv:2305.14018, 2023. 7
[30] Haisong Liu, Yao Teng, Tao Lu, Haiguang Wang, and Limin
Wang. Sparsebev: High-performance sparse 3d object de-
tection from multi-camera videos.
In Proceedings of the
IEEE/CVF International Conference on Computer Vision,
pages 18580–18590, 2023. 2, 7
[31] Jihao Liu, Tai Wang, Boxiao Liu, Qihang Zhang, Yu Liu,
and Hongsheng Li. Geomim: Towards better 3d knowledge
transfer via masked image modeling for multi-view 3d un-
derstanding. In Proceedings of the IEEE/CVF International
Conference on Computer Vision, pages 17839–17849, 2023.
4
[32] Yingfei Liu, Tiancai Wang, Xiangyu Zhang, and Jian Sun.
Petr: Position embedding transformation for multi-view 3d
object detection. In European Conference on Computer Vi-
sion, pages 531–548. Springer, 2022. 2, 1
[33] Yingfei Liu, Junjie Yan, Fan Jia, Shuailin Li, Aqi Gao, Tian-
cai Wang, and Xiangyu Zhang. Petrv2: A unified framework
for 3d perception from multi-camera images. In Proceedings
of the IEEE/CVF International Conference on Computer Vi-
sion, pages 3262–3272, 2023. 7, 1
[34] Hao Lu, Wenze Liu, Zixuan Ye, Hongtao Fu, Yuliang Liu,
and Zhiguo Cao. Sapa: Similarity-aware point affiliation for
feature upsampling. Advances in Neural Information Pro-
cessing Systems, 35:20889–20901, 2022. 3
[35] Cheng Luo, Qinliang Lin, Weicheng Xie, Bizhu Wu, Jin-
heng Xie, and Linlin Shen. Frequency-driven imperceptible
adversarial attack on semantic similarity. In Proceedings of
the IEEE/CVF conference on computer vision and pattern
recognition, pages 15315–15324, 2022. 2
[36] Salma Abdel Magid, Yulun Zhang, Donglai Wei, Won-Dong
Jang, Zudi Lin, Yun Fu, and Hanspeter Pfister.
Dynamic
high-pass filtering and multi-spectral attention for image
super-resolution.
In Proceedings of the IEEE/CVF Inter-
national Conference on Computer Vision, pages 4288–4297,
2021. 2
[37] Alican Mertan, Damien Jade Duff, and Gozde Unal. Single
image depth estimation: An overview. Digital Signal Pro-
cessing, 123:103441, 2022. 1
[38] Dennis Park, Rares Ambrus, Vitor Guizilini, Jie Li, and
Adrien Gaidon.
Is pseudo-lidar needed for monocular 3d
object detection?
In Proceedings of the IEEE/CVF Inter-
national Conference on Computer Vision, pages 3142–3152,
2021. 6
[39] Jinhyung Park, Chenfeng Xu, Shijia Yang, Kurt Keutzer,
Kris Kitani, Masayoshi Tomizuka, and Wei Zhan. Time will
tell: New outlooks and a baseline for temporal multi-view 3d
object detection. arXiv preprint arXiv:2210.02443, 2022. 7
[40] Jonah Philion and Sanja Fidler. Lift, splat, shoot: Encoding
images from arbitrary camera rigs by implicitly unproject-
ing to 3d. In Computer Vision–ECCV 2020: 16th European
Conference, Glasgow, UK, August 23–28, 2020, Proceed-
ings, Part XIV 16, pages 194–210. Springer, 2020. 1
[41] Nasim Rahaman, Aristide Baratin, Devansh Arpit, Felix
Draxler, Min Lin, Fred Hamprecht, Yoshua Bengio, and
Aaron Courville. On the spectral bias of neural networks. In
International conference on machine learning, pages 5301–
5310. PMLR, 2019. 2, 3
[42] Ren´e Ranftl,
Katrin Lasinger,
David Hafner,
Konrad
Schindler, and Vladlen Koltun. Towards robust monocular
depth estimation: Mixing datasets for zero-shot cross-dataset
transfer. IEEE transactions on pattern analysis and machine
intelligence, 44(3):1623–1637, 2020. 5
[43] Ren´e Ranftl, Alexey Bochkovskiy, and Vladlen Koltun. Vi-
sion transformers for dense prediction. In Proceedings of
the IEEE/CVF international conference on computer vision,
pages 12179–12188, 2021. 1
[44] Cody Reading, Ali Harakeh, Julia Chae, and Steven L
Waslander.
Categorical depth distribution network for
monocular 3d object detection.
In Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern
Recognition, pages 8555–8564, 2021. 1
[45] Changyong Shu, Jiajun Deng, Fisher Yu, and Yifan Liu.
3dppe: 3d point positional encoding for transformer-based
multi-camera 3d object detection.
In Proceedings of the
IEEE/CVF International Conference on Computer Vision,
pages 3580–3589, 2023. 2, 4, 6, 1
[46] Zhi Tian, Chunhua Shen, Hao Chen, and Tong He. Fcos: A
simple and strong anchor-free object detector. IEEE trans-
actions on pattern analysis and machine intelligence, 44(4):
1922–1933, 2020. 4
[47] Junyi Wang and Yue Qi. Multi-task learning and joint re-
finement between camera localization and object detection.
Computational Visual Media, 10(5):993–1011, 2024. 1
[48] Qilong Wang, Banggu Wu, Pengfei Zhu, Peihua Li, Wang-
meng Zuo, and Qinghua Hu. Eca-net: Efficient channel at-
tention for deep convolutional neural networks. In Proceed-
ings of the IEEE/CVF conference on computer vision and
pattern recognition, pages 11534–11542, 2020. 4
[49] Shihao Wang, Xiaohui Jiang, and Ying Li. Focal-petr: Em-
bracing foreground for efficient multi-camera 3d object de-
tection. IEEE Transactions on Intelligent Vehicles, 2023. 6
[50] Shihao Wang, Yingfei Liu, Tiancai Wang, Ying Li, and Xi-
angyu Zhang. Exploring object-centric temporal modeling
for efficient multi-view 3d object detection. In Proceedings
of the IEEE/CVF International Conference on Computer Vi-
sion, pages 3621–3631, 2023. 2, 6, 7
[51] Tai Wang, Xinge Zhu, Jiangmiao Pang, and Dahua Lin.
Fcos3d: Fully convolutional one-stage monocular 3d object
detection.
In Proceedings of the IEEE/CVF International
Conference on Computer Vision, pages 913–922, 2021. 4, 6
[52] Tai Wang, ZHU Xinge, Jiangmiao Pang, and Dahua Lin.
Probabilistic and geometric depth: Detecting objects in per-
spective. In Conference on Robot Learning, pages 1475–
1485. PMLR, 2022. 4


## Page 11

[53] Yue Wang, Vitor Campagnolo Guizilini, Tianyuan Zhang,
Yilun Wang, Hang Zhao, and Justin Solomon.
Detr3d:
3d object detection from multi-view images via 3d-to-2d
queries. In Conference on Robot Learning, pages 180–191.
PMLR, 2022. 2
[54] Xinshuo Weng and Kris Kitani. Monocular 3d object de-
tection with pseudo-lidar point cloud.
In Proceedings of
the IEEE/CVF International Conference on Computer Vision
Workshops, pages 0–0, 2019. 1
[55] Kaixin Xiong, Shi Gong, Xiaoqing Ye, Xiao Tan, Ji Wan,
Errui Ding, Jingdong Wang, and Xiang Bai. Cape: Camera
view position embedding for multi-view 3d object detection.
In Proceedings of the IEEE/CVF Conference on Computer
Vision and Pattern Recognition, pages 21570–21579, 2023.
7
[56] Zhiqin John Xu and Hanxu Zhou. Deep frequency principle
towards understanding why deeper learning is faster. In Pro-
ceedings of the AAAI conference on artificial intelligence,
pages 10541–10550, 2021. 2
[57] Chenyu Yang, Yuntao Chen, Hao Tian, Chenxin Tao, Xizhou
Zhu, Zhaoxiang Zhang, Gao Huang, Hongyang Li, Yu Qiao,
Lewei Lu, et al.
Bevformer v2: Adapting modern image
backbones to bird’s-eye-view recognition via perspective su-
pervision. In Proceedings of the IEEE/CVF Conference on
Computer Vision and Pattern Recognition, pages 17830–
17839, 2023. 7
[58] Lihe Yang, Bingyi Kang, Zilong Huang, Xiaogang Xu, Jiashi
Feng, and Hengshuang Zhao. Depth anything: Unleashing
the power of large-scale unlabeled data. In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition, pages 10371–10381, 2024. 5, 1
[59] Lihe Yang, Bingyi Kang, Zilong Huang, Zhen Zhao, Xiao-
gang Xu, Jiashi Feng, and Hengshuang Zhao. Depth any-
thing v2. arXiv preprint arXiv:2406.09414, 2024. 1
[60] Y YL, Lan Boureau, and Jean Ponce. A theoretical analysis
of feature pooling in vision algorithms. In Proc International
Conference on Machine Learning. ICML, 2010. 4
[61] W Yuan, X Gu, Z Dai, S Zhu, and P Tan. New crfs: Neu-
ral window fully-connected crfs for monocular depth estima-
tion. arxiv 2022. arXiv preprint arXiv:2203.01502, 2022. 1
[62] Richard Zhang.
Making convolutional networks shift-
invariant again.
In International conference on machine
learning, pages 7324–7334. PMLR, 2019. 2
[63] Zhuofan Zong, Dongzhi Jiang, Guanglu Song, Zeyue Xue,
Jingyong Su, Hongsheng Li, and Yu Liu. Temporal enhanced
training of multi-view 3d object detector via historical object
prediction. In Proceedings of the IEEE/CVF International
Conference on Computer Vision, pages 3781–3790, 2023. 7
[64] Xueyan Zou, Fanyi Xiao, Zhiding Yu, Yuheng Li, and
Yong Jae Lee.
Delving deeper into anti-aliasing in con-
vnets.
International Journal of Computer Vision, 131(1):
67–81, 2023. 2, 3


## Page 12

FreqPDE: Rethinking Positional Depth Embedding for Multi-View 3D Object
Detection Transformers
Supplementary Material
A. Appendix
A.1. More Related Work
Depth Estimation Depth estimation from 2D camera im-
ages is a challenging topic in Computer Vision, categorized
into regressing metric depth [2, 3, 20, 27, 61] and rela-
tive depth [23, 37, 43]. BinsFormer [27] introduces suf-
ficient interaction between probability distribution and bin
predictions to generate proper metric estimation. DPT [43]
exploits vision transformers as a backbone for dense rela-
tive depth prediction. Recent works [4, 58, 59] attempt to
build a foundation model with excellent generalization per-
formance across domains while maintaining metric scale.
ZoeDepth [4] uses a lightweight depth head with a novel
metric bin design to combine metric and relative depth es-
timation.
DepthAnything [58, 59] introduces the affine-
invariant loss to ignore the unknown scale and shift during
the training stage, additionally, a data engine has been de-
vised to automatically generate pseudo depth annotations
for unlabeled images.
3D Positional Embedding The necessity of the 3D Po-
sition Encoder (PE) has been addressed in prior stud-
ies [32, 33, 45]. PETR series [32, 33] discretize the camera
frustum space into meshgrid coordinates which are trans-
formed to 3D world space with camera parameters, then the
3D coordinates are input to a 3D position encoder with 2D
image features to construct the 3D position-aware features.
However, leveraging hand-crafted camera-ray depth bins as
the channel dimensionality for the point cloud disregards
depth variations across different pixels. To ameliorate the
aforementioned problem, 3DPPE [45] transforms the pixels
to 3D space with camera parameters and predicted pixel-
wise depth results, the resulting 3D points are sent to a po-
sition encoder to construct the 3D feature with point-level
embeddings.
A.2. Implicit Distribution Supervision.
To fully leverage the strengths of the foundation model, we
exploit the generated relative depth results as pseudo labels
for extra supervision of our depth prediction Di,j. To elab-
orate, the crucial issue is converting metric depth to relative
depth, this process can be formulated as:
Drel =
1
scale(
1
Dmtr −shift),
(13)
where Drel is relative depth, Dmtr is metric depth, scale
and shift are sample-wise parameters for transposition.
Noticing the linear relationship between
1
Dmtr and Drel, we
perform mean-variance normalization [1] separately:
\
1
Dmtr =
1
Dmtr −E(
1
Dmtr )
q
V ar(
1
Dmtr )
,
d
Drel =
1
scale(
1
Dmtr −E(
1
Dmtr ))
|
1
scale|
q
V ar(
1
Dmtr )
,
(14)
where E and V ar represent the computation of the mean
and variance respectively, [
1
Dmtr and d
Drel correspond to
the normalized outcomes. Given that the coefficient
1
scale is
strictly positive, it follows that the two normalization results
for each sample are equivalent. Consequently, we take the
reciprocal of the predicted depth Di,j, normalize the out-
come, and employ the normalized pseudo-labels as super-
visory signals to facilitate the supervised learning transition
from metric depth to relative depth.
A.3. More Ablation Study
Cross View Attention. In our CSDP module, we apply a
fixed-ratio mask to the features in order to mitigate the in-
fluence of non-overlapping regions. To verify the effective-
ness of this masking approach, we conduct ablation studies
to evaluate the impact of different mask ratios, as illustrated
in Tab. 8. With a mask ratio of 0.2, our method demonstrates
improved performance, outperforming the model without
masking and other mask ratio.
Table 8. Necessity of cross-view.
Mask Ratio
NDS ↑
mAP ↑
mATE↓
-
58.3
50.3
0.578
0.1
57.3
49.6
0.609
0.2
58.5
50.5
0.569
0.3
58.2
50
0.580
Effect of Positional Depth Encoder This study seeks to
provide empirical evidence of that positional encoding,
within the multi-level depth maps, enhances the detection
capacity of 3D objects by the query. As shown in Tab. 9,
wherein multi-level scale-invariant depth prediction results
are resized to the same scale and fused together to be fed
into a point-wise embedding function, which outperforms
the baseline by 1.4% NDS and 2.4% mAP, also exceed the
single-level embedding method similar to 3DPPE [45].
Comparison with LSS method To validate the ’plug-and-
play’ capability of proposed depth predictor, we replace the


## Page 13

Table 9. Ablation for Positional Depth Encoder on nuScenes.
Method
NDS ↑
mAP ↑
mATE ↓
Baseline
57.2
48.2
0.602
Single-level
57.9
49.6
0.587
Multi-levels
58.6
50.6
0.576
Table 10. Comparison with LSS-based method.
Method
Backbone
Input Resolution
mAP
NDS
BEVDepth
R50
256*704
35.1
47.5
BEVDepth-R
R50
256*704
36.0
48.4
Table 11. Effect of Hybrid Depth Supervision on nuScenes val
set.
Supervision
Abs Rel ↓
Sq Rel ↓
NDS ↑
mAP ↑
LiDAR only
0.17
1.45
58.3
49.9
Pseudo only
0.23
3.71
58.4
50.1
Hybrid
0.15
1.41
58.6
50.6
depth predictor in BEVDepth with our FSPE and CSDP
modules. The results, presented in Table 10, demonstrate
the effectiveness and transferability of our proposed design.
Effect of Hybrid Depth Supervision.
To further vali-
date the effectiveness of the hybrid supervision approach
for CSDP, we compare the performance of different super-
vision methodologies. As presented in Tab. 11, employ-
ing only pseudo-labels results in an improvement in detec-
tion performance; however, it leads to a decrease in depth
estimation performance.
This indicates that distribution-
based supervision provides a more comprehensive supervi-
sory signal for overall depth maps but lacks the precision
of absolute depth supervision. Consequently, with hybrid
supervision, both the absolute relative error (Abs Rel) and
squared relative error (Sq Rel) decrease, while the model
achieves a 1.4% increase in mAP and a 0.6% increase in
NDS.
A.4. Result Visualization
Qualitative Results. We show the qualitative detection re-
sults of FreqPDE in Fig. 6 on multi-view images. The 3D
predicted bounding boxes are drawn with different colors
for different classes. As illustrated by the highlighted cir-
cles, our method accurately detects the category and lo-
cation of distant targets, while also mitigating the chal-
lenges posed by occluded small targets to some extent. This
demonstrates an enhancement in the model’s detection ca-
pability for distant targets following the integration of a
more precise depth estimation module.
More Visualization. We also show more detection results
of some challenging scenes in Fig. 7 and Fig. 8. Our method
shows impressive results on crowded and distant objects.


## Page 14

Figure 6. Qualitative detection results on multi-view images on the nuScenes val set. The 3D predicted bounding boxes are drawn with
different colors for different classes.


## Page 15

Figure 7. Qualitative detection results on multi-view images and BEV space on the nuScenes val set.


## Page 16

Figure 8. Qualitative detection results on multi-view images and BEV space on the nuScenes val set.

