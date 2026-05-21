# TPVFormer Tri-perspective View 3D Semantic Occupancy

**Source**: arxiv PDF, 13 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Tri-Perspective View for Vision-Based 3D Semantic Occupancy Prediction
Yuanhui Huang1,2,* Wenzhao Zheng1,2,* Yunpeng Zhang3
Jie Zhou1,2
Jiwen Lu1,2,†
1Beijing National Research Center for Information Science and Technology, China
2Department of Automation, Tsinghua University, China
3PhiGent Robotics
{huangyh22,zhengwz18}@mails.tsinghua.edu.cn; yunpengzhang97@gmail.com;
{jzhou,lujiwen}@tsinghua.edu.cn
Only RGB Images As Inputs
Vision-based Occupancy Prediction
Ground Truth
TPVFormer
bicycle
bus
car
pedestrian
truck
driveable surface
other flat
sidewalk
terrain
manmade
vegetation
Figure 1. Given only surround-camera RGB images as inputs, our model (trained using only sparse LiDAR point supervision) can predict
the semantic occupancy for all volumes in the 3D space. This task is challenging as it requires both geometric and semantic understandings
of the 3D scene. We observe that our model can produce even more comprehensive and consistent volume occupancy than the groundtruth
on the validation set (not seen during training) of nuScenes [4]. Despite the lack of geometric inputs like LiDAR, our model can accurately
identify the 3D positions and sizes of close and distant objects. Particularly, our model even successfully identiﬁes the partially occluded
bicycle captured only by two LiDAR points, demonstrating the potential advantage of vision-based 3D semantic occupancy prediction.
Abstract
Modern methods for vision-centric autonomous driving
perception widely adopt the bird’s-eye-view (BEV) repre-
sentation to describe a 3D scene. Despite its better efﬁ-
ciency than voxel representation, it has difﬁculty describing
the ﬁne-grained 3D structure of a scene with a single plane.
To address this, we propose a tri-perspective view (TPV)
representation which accompanies BEV with two additional
perpendicular planes. We model each point in the 3D space
by summing its projected features on the three planes. To
lift image features to the 3D TPV space, we further pro-
pose a transformer-based TPV encoder (TPVFormer) to ob-
tain the TPV features effectively. We employ the attention
mechanism to aggregate the image features corresponding
to each query in each TPV plane. Experiments show that
our model trained with sparse supervision effectively pre-
dicts the semantic occupancy for all voxels. We demon-
strate for the ﬁrst time that using only camera inputs can
achieve comparable performance with LiDAR-based meth-
ods on the LiDAR segmentation task on nuScenes. Code:
https://github.com/wzzheng/TPVFormer.
1. Introduction
Perceiving the 3D surroundings accurately and compre-
hensively plays an important role in the autonomous driving
system. Vision-based 3D perception recently emerges as
a promising alternative to LiDAR-based one to effectively
extract 3D information from 2D images. Though lacking
direct sensing of depth information, vision-based models
empowered by surrounding cameras demonstrate promising
performance on various 3D perception tasks such as depth
estimation [18,45], semantic map reconstruction [1,20,51],
and 3D object detection [28,31,49].
The core of 3D surrounding perceiving lies in how to ef-
fectively represent a 3D scene. Conventional methods split
the 3D space into voxels and assign each voxel a vector to
represent its status. Despite its accuracy, the vast number
of voxels poses a great challenge to computation and re-
quires specialized techniques like sparse convolution [13].
As the information in outdoor scenes is not isotropically
distributed, modern methods collapse the height dimension
and mainly focus on the ground plane (bird’s-eye-view)
where information varies the most [21,27,29,32,38,49,51].
*Equal contribution. †Corresponding author.
1
arXiv:2302.07817v2  [cs.CV]  2 Mar 2023
### Page 2

Image 
Backbone
TPVFormer
Training Phase
Test Phase
LiDAR Ground Truth
Semantic Occupancy Prediction
TPV Representation
Sparse Supervision
Dense Prediction
Camera Input
Figure 2. An overview of our method for 3D semantic occupancy
prediction. Taking camera images as inputs, the proposed TPV-
Former only uses sparse LiDAR semantic labels for training but
can effectively predict the semantic occupancy for all voxels.
They implicitly encode the 3D information of each object in
the vector representation in each BEV grid. Though more
efﬁcient, BEV-based methods perform surprisingly well on
the 3D object detection task [29, 32]. This is because 3D
object detection only demands predictions of coarse-level
bounding boxes for commonly seen objects such as cars
and pedestrians. However, objects with various 3D struc-
tures can be encountered in real scenes and it is difﬁcult
(if not impossible) to encode all of them using a ﬂattened
vector. Therefore, it requires a more comprehensive and
ﬁne-grained understanding of the 3D surroundings toward
a safer and more robust vision-centric autonomous driving
system. Still, it remains unknown how to generalize BEV
to model ﬁne-grained 3D structures while preserving its ef-
ﬁciency and detection performance.
In this paper, we advance in this direction and propose a
tri-perspective view (TPV) representation to describe a 3D
scene. Motivated by recent advances in explicit-implicit hy-
brid scene representations [7,8], we generalize BEV by ac-
companying it with two perpendicular planes to construct
three cross-planes perpendicular to each other. Each plane
models the 3D surroundings from one view and combining
them provides a comprehensive description of the 3D struc-
ture. Speciﬁcally, to obtain the feature of a point in the 3D
space, we ﬁrst project it into each of the three planes and use
bilinear interpolation to obtain the feature for each projected
point. We then sum the three projected features as the com-
prehensive feature of the 3D point. The TPV representation
is thus able to describe the 3D scene at an arbitrary resolu-
tion and produces different features for different points in
the 3D space. We further propose a transformer-based en-
coder (TPVFormer) to effectively obtain the TPV features
from 2D images. We ﬁrst perform image cross-attention
between TPV grid queries and the corresponding 2D image
features to lift 2D information to the 3D space. We then per-
form cross-view hybrid-attention among the TPV features
to enable interactions among the three planes.
To demonstrate the superiority of TPV, we formulate a
practical yet challenging task for vision-based 3D semantic
occupancy prediction, where only sparse lidar semantic la-
bels are provided for training and predictions for all voxels
are required for testing, as shown in Figure 2. However,
as no benchmark is provided on this challenging setting,
we only perform qualitative analysis but provide a quanti-
tative evaluation on two proxy tasks: LiDAR segmentation
(sparse training, sparse testing) on nuScenes [4] and 3D se-
mantic scene completion (dense training, dense testing) on
SemanticKITTI [2]. For both tasks, we only use RGB im-
ages as inputs. For LiDAR segmentation, our model use
the LiDAR data only for point query to compute evalua-
tion metrics. Visualization results show that TPVFormer
produces consistent semantic voxel occupancy prediction
with only sparse point supervision during training, as shown
in Figure 1.
We also demonstrate for the ﬁrst time that
our vision-based method achieves comparable performance
with LiDAR-based methods on LiDAR segmentation.
2. Related Work
Voxel-based Scene Representation: Obtaining an ef-
fective representation for a 3D scene is the basic procedure
for 3D surrounding perception. One direct way is to dis-
cretize the 3D space into voxels and assign a vector to repre-
sent each voxel [52,54]. The ability to describe ﬁne-grained
3D structures makes voxel-based representation favorable
for 3D semantic occupancy prediction tasks including lidar
segmentation [12, 30, 43, 47, 48, 55] and 3D scene comple-
tion [5, 10, 24, 41, 46]. Though they have dominated the
3D segmentation task [47], they still lag behind BEV-based
methods on the 3D detection performance [27]. Despite the
success of voxel-based representations in LiDAR-centric
surrounding perception, only a few works have explored
voxel-based representations for vision-centric autonomous
driving [5,26]. MonoScene [5] ﬁrst backprojects image fea-
tures to all possible positions in the 3D space along the opti-
cal ray to obtain the initial voxel representation and further
processes it using a 3D UNet. However, it is still challeng-
ing to generalize it to 3D perception with multi-view images
due to the inefﬁciency of voxel representations. This moti-
vates us to explore more efﬁcient and expressive ways to
describe the ﬁne-grained 3D structure of a scene.
BEV-based Scene Representation: The vast number
of voxels poses a great challenge to the computation efﬁ-
ciency of voxel-based methods. Considering that the height
dimension contains less information than the other two di-
mensions, BEV-based methods implicitly encode the height
information in each BEV grid for a more compact repre-
sentation of scenes [23]. Recent studies in BEV-based per-
ception focus on how to effectively transform features from
the image space to the BEV space [21, 27, 28, 38, 39, 51].
One line of works explicitly predict a depth map for each
image and utilizes it to project image features into the 3D
space followed by BEV pooling [21, 27, 29, 32, 38, 39, 51].
2
### Page 3

Another line of works employ BEV queries to implic-
itly assimilate information from image features using the
cross-attention mechanism [22,28]. BEV-based perception
achieves great success on vision-centric 3D detection from
multi-view images [27], demonstrating comparable perfor-
mance to LiDAR-centric methods. Yet, it is difﬁcult to ap-
ply BEV to 3D semantic occupancy prediction which re-
quires a more ﬁne-grained description of the 3D space.
Implicit Scene Representation: Recent methods have
also explored implicit representations to describe a scene.
They learn a continuous function that takes as input the
3D coordinate of a point and outputs the representation of
this point [34, 35, 37]. Compared with explicit represen-
tations like voxel and BEV, implicit representations usu-
ally share the advantage of arbitrary-resolution modeling
and computation-efﬁcient architectures [6, 11, 40]. These
advantages enable them to scale to larger and more com-
plex scenes with more ﬁne-grained descriptions. Especially,
our work is inspired by recent advances in hybrid explicit-
implicit representations [7,8]. They explicitly inject spatial
information into the continuous mapping of implicit repre-
sentations. Therefore, they share the computation-efﬁcient
architecture of implicit representations and better spatial
awareness of explicit representations. Still, they mainly fo-
cus on small-scale complex scenes for 3D-aware image ren-
dering. To the best of our knowledge, we are the ﬁrst to use
implicit representation to model outdoor scenes for 3D sur-
rounding perception in autonomous driving.
3. Proposed Approach
3.1. Generalizing BEV to TPV
Autonomous driving perception typically requires both
expressive and efﬁcient representation of the complex 3D
scene, among which voxel and Bird’s-Eye-View (BEV) rep-
resentations are the two most widely adopted frameworks.
Voxel representation [26,43,48] describes a 3D scene with
dense cubic features V ∈RH×W ×D×C where H, W, D
are the spatial resolution of the voxel space and C denotes
the feature dimension. A random point located at (x, y, z)
in the real world maps to its voxel coordinates (h, w, d)
through one-to-one correspondence Pvox, and the resulting
feature fx,y,z is obtained by sampling V at (h, w, d):
fx,y,z = vh,w,d = S(V, (h, w, d)),
= S(V, Pvox(x, y, z)),
(1)
where S(arg1, arg2) denotes sampling arg1 at the posi-
tion speciﬁed in arg2 and vh,w,d is the sampled voxel fea-
ture. Note that the projection function Pvox is composed of
simple scaling and rigid transformations if the voxel space
aligns with the real world. Therefore, voxel representation
preserves the dimensionality of the real world and offers
sufﬁcient expressiveness with appropriate H, W, D. Yet,
Voxel
BEV
TPV (ours)
Figure 3. Comparisons of the proposed TPV representation with
voxel and BEV representation. While BEV is more efﬁcient than
the voxel representation, it discards the height information and
cannot comprehensively describe a 3D scene.
the storage and computation complexity of voxel features
are proportion to O(HWD), making it challenging to de-
ploy them in real-time onboard applications.
As a popular alternative, BEV [22,27,28,32] models the
3D scene with a 2D feature map B ∈RH×W ×C which en-
codes the top view of the scene. Different from the voxel
counterpart, the point at (x, y, z) is projected to its BEV co-
ordinates (h, w) using only the positional information from
the ground plane regardless of the z-axis. Each feature bh,w
sampled from B corresponds to a pillar region covering the
full range of z-axis in the real world:
fx,y,Z = bh,w = S(B, (h, w)) = S(B, Pbev(x, y)),
(2)
where fx,y,Z denotes features of points sharing the same
(x, y) but differing in z, and Pbev is the point-to-BEV pro-
jection.
Although BEV greatly reduces the storage and
computation burden to O(HW), completely omitting the
z-axis has an adverse effect on its expressiveness.
To address this, we propose a Tri-Perspective View
(TPV) representation which is capable of modeling the 3D
space at full scale without suppressing any axes and avoid-
ing cubic complexity, as illustrated in Figure 3. Formally,
we learn three axis-aligned orthogonal TPV planes:
T = [THW , TDH, TW D], THW ∈RH×W ×C,
TDH ∈RD×H×C, TW D ∈RW ×D×C,
(3)
which represent the top, side and front views of a 3D scene
respectively. H, W, D denote the resolution of the three
planes and C is the feature dimension. Intuitively, a com-
plex scene, when examined from different perspectives, can
be better understood because these perspectives may pro-
vide complementary clues about the scene.
Point Querying formulation. Given a query point at
(x, y, z) in the real world, TPV representation tries to ag-
gregate its projections on the top, side and front views in
order to get a comprehensive description of the point. To
elaborate, we ﬁrst project the point onto the TPV planes
to obtain the coordinates [(h, w), (d, h), (w, d)], sample the
TPV planes at these locations to retrieve the corresponding
features [th,w, td,h, tw,d], and aggregate the three features
3
### Page 4

to generate the ﬁnal fx,y,z:
th,w = S(THW , (h, w)) = S(THW , Phw(x, y)),
td,h = S(TDH, (d, h)) = S(TDH, Pdh(z, x)),
tw,d = S(TW D, (w, d)) = S(TW D, Pwd(y, z)).
(4)
fx,y,z = A(th,w, td,h, tw,d),
(5)
where the sampling function S and the aggregation function
A are implemented with bilinear interpolation and summa-
tion respectively, and each projection function P performs
simple scaling on the two relevant coordinates since the
TPV planes are aligned with the real-world axes.
Voxel feature formulation.
Equivalent to the point
querying formulation, the TPV planes, when expanded
along respective orthogonal directions and summed up,
construct a full-scale 3D feature space similar to the voxel
feature space, but only with storage and computation com-
plexity of O(HW + DH + WD), which is an order of
magnitude lower than the voxel counterpart.
Compared with BEV, as the three planes in TPV are per-
pendicular to each other, point features along the orthogonal
direction of one plane are diversiﬁed by features sampled
from the other two planes, which is ignored by the BEV
representation. Moreover, a grid feature in each TPV plane
is only responsible for view-speciﬁc information of the cor-
responding pillar region rather than encoding the complete
information as in BEV. To sum up, TPV representation gen-
eralizes BEV from single top view to complementary and
orthogonal top, side and front views and is able to offer a
more comprehensive and ﬁne-grained understanding of the
3D surroundings while remaining efﬁcient.
3.2. TPVFormer
For vision-centric autonomous driving perception, a 2D
backbone is often employed to obtain image features be-
fore feeding them into a speciﬁc encoder depending on the
representation framework. We present a transformer-based
TPV encoder (TPVFormer) to lift the image features to the
TPV planes through the attention mechanism.
Overall Structure: In TPVFormer, we introduce TPV
queries, image cross-attention (ICA) and cross-view hybrid-
attention (CVHA) to enable effective generation of TPV
planes, as shown in Fig. 4.
In fact, TPV queries and
TPV planes refer to the same set of feature vectors de-
ﬁned in (3). Each TPV query t ∈T is a grid cell fea-
ture belonging to one of the three planes and used to en-
code view-speciﬁc information from the corresponding pil-
lar region. Cross-view hybrid-attention enables direct in-
teractions among TPV queries from the same or different
views in order to gather contextual information. Inside im-
age cross-attention, TPV queries aggregate visual informa-
tion from image features through deformable attention.
We further construct two kinds of transformer blocks:
hybrid-cross-attention block (HCAB) and hybrid-attention
block (HAB). Composed of both CVHA and ICA atten-
tion, the HCAB block is employed in the ﬁrst half of TPV-
Former to effectively query visual information from image
features. Following HCAB blocks, the HAB block contains
only CVHA attention and specializes in contextual infor-
mation encoding. Finally, we build TPVFormer by stacking
N1 HCAB blocks and N2 HAB blocks.
TPV Queries: Although TPV queries and TPV planes
refer to the same list of 2D features deﬁned in (3), they are
used in attention and 3D representation contexts, respec-
tively. Each TPV query maps to a 2D grid cell region of
size s×s m2 in the corresponding view, and further to a 3D
pillar region extending from the view in the perpendicular
direction. In our pipeline, TPV queries are ﬁrst enhanced
with raw visual information from image features in HCAB
blocks, and then reﬁned with contextual clues from other
queries in HAB blocks. As for implementation, we initial-
ize TPV queries as learnable parameters and add 3D posi-
tional embedding to them before the ﬁrst encoder layer.
Image Cross-Attention: In TPVFormer, we use image
cross-attention to lift multi-scale and possibly multi-camera
image features to the TPV planes. Considering the high res-
olution nature of TPV queries (∼104 queries) and multiple
image feature maps (∼105 pixels each), it is unfeasible
to compute full-scale vanilla cross-attention between them.
As a workaround, we employ the efﬁcient deformable at-
tention [15,53] to implement image cross-attention.
We take the local receptive ﬁeld as an inductive bias
when sampling the reference points. Speciﬁcally, for a TPV
query th,w located at (h, w) in the top plane, we ﬁrst calcu-
late its coordinates (x, y) in the top view in the real world
through the inverse projection function P−1
hw. Then we sam-
ple uniformly N HW
ref
reference points for the query th,w
along the orthogonal direction of the plane:
(x, y) = P−1
hw(h, w) = ((h −H
2 ) × s, (w −W
2 ) × s). (6)
Ref world
h,w
= (P−1
hw(h, w), Z) = {(x, y, zi)}
NHW
ref
i=1
,
(7)
where Ref world
h,w
denotes the set of reference points in the
world coordinate for query th,w. The similar procedure is
repeated for all TPV queries, and note that the number of
reference points Nref may change across planes because of
the different ranges of axes. After deriving the reference
points for th,w, we need to project them into the pixel coor-
dinate in order to sample the image feature maps later:
Ref pix
h,w = Ppix(Ref world
h,w
) = Ppix({(x, y, zi)}),
(8)
where Ref pix
h,w is the set of reference points in the pixel co-
ordinate for query th,w and Ppix is the perspective projec-
4
### Page 5

Prediction
Head
⊕
Semantic
Occupancy 
     of    
Cross-Attention
Cross-Attention
Cross-Attention
Hybrid-Attention
Hybrid-Attention
Image Inputs
Network
Network
Feature Maps
TPVFormer
TPV Representation
Point Prediction
Figure 4. Framework of the proposed TPVFormer for 3D semantic occupancy prediction. We employ an image backbone network to
extract multi-scale features for multi-camera images. We then perform cross-attention to adaptively lift 2D features to the TPV space and
use cross-view hybrid attention to enable the interactions between TPV planes. To predict the semantic occupancy of a point in the 3D
space, we apply a lightweight prediction head on the sum of projected features on the three TPV planes.
tion function determined by the camera extrinsic and intrin-
sic. Note that we may have multiple cameras in different di-
rections which will generate a set of {Ref pix,j
h,w }Nc
j=1 where
Nc denotes the number of cameras.
Since not all cam-
eras can capture the reference points of query th,w, we can
further reduce computation by removing invalid sets from
{Ref pix,j
h,w }Nc
j=1 if none of the reference points falls onto
the image captured by the corresponding camera. The ﬁ-
nal step is to generate offsets and attention weights through
two linear layers applied on th,w and produce the updated
TPV queries by summing up the sampled image features
weighted by their attention weights:
ICA(th,w, I)=
1
|N val
h,w|
X
j∈Nval
h,w
DA(th,w, Ref pix,j
h,w , Ij),
(9)
where N val
h,w, Ij, DA(·) denote the index set of valid cam-
eras, the image features from the jth camera and the de-
formable attention function, respectively.
Cross-View
Hybrid-Attention:
In
image
cross-
attention, TPV queries sample reference image features sep-
arately and no direct interactions between them are enabled.
Therefore, we propose cross-view hybrid-attention to al-
low queries to exchange their information across different
views, which beneﬁts context extraction. We also adopt
deformable attention here to reduce computation, in which
three TPV planes serve as key and value. Taking the TPV
query th,w located at (h, w) in the top plane as an exam-
ple, we group its reference points into three disjoint sub-
sets, which contains reference points belonging to the top,
side and front planes respectively:
Rh,w = Rtop
h,w ∪Rside
h,w ∪Rfront
h,w
.
(10)
To collect reference points on the top plane, we simply sam-
ple a few random points in the neighborhood of the query
th,w. As for the side and front planes, we ﬁrst sample 3D
points uniformly along the direction perpendicular to the
top plane and project them onto the side and front planes:
Rside
h,w = {(di, h)}i,
Rfront
h,w
= {(w, di)}i.
(11)
Following the derivation of reference points is the typical
practice of deformable attention: we calculate the sam-
pling offsets and attention weights for each reference point
through linear layers and sum up the sampled features
weighted by their attention score:
CVHA(th,w) = DA(th,w, Rh,w, T).
(12)
3.3. Applications of TPV
The TPV planes T obtained by TPVFormer encode ﬁne-
grained view-speciﬁc information of a 3D scene. Still, they
are in the form of orthogonal cross-planes and not readily
interpretable to common task heads. Here we explain how
to convert TPV planes to point and voxel features and fur-
ther introduce a lightweight segmentation head.
Point Feature. Given locations in the real world, we
consider the feature generation process as the points query-
ing their features from the TPV representation. As deﬁned
in (4) and (5), we ﬁrst project the points onto the TPV planes
to retrieve the corresponding features [th,w, td,h, tw,d], and
sum them up to obtain the per-point features.
Voxel Feature. For dense voxel features, we actively
broadcast each TPV plane along the corresponding orthog-
onal direction to produce three feature tensors of the same
size H × W × D × C, and aggregate them by summation
to obtain the full-scale voxel features. Note that we do not
know the position of any physical point in advance.
To conduct ﬁne-grained segmentation tasks, we apply a
lightweight MLP on the point or voxel features to predict
their semantic labels, which is instantiated by only two lin-
ear layers and an intermediate activation layer.
4. Experiments
4.1. Task Descriptions
We conduct three types of experiments, including 3D se-
mantic occupancy prediction, LiDAR segmentation, and se-
mantic scene completion (SSC). The ﬁrst two tasks are per-
formed on Panoptic nuScenes [17], and the last one is on
Semantic KITTI [2]. We detail the datasets in Section A.
For all tasks, our model only uses RGB images as inputs.
3D semantic occupancy prediction. As dense seman-
tic labels are difﬁcult to obtain, we formulate a practical yet
5
### Page 6

FRONT_LEFT
FRONT
FRONT_RIGHT
Semantic Occupancy Prediction (Ours) 
LiDAR Seg. (Ours) 
LiDAR Seg. (Cylinder3D) 
LiDAR Seg. (Ground Truth) 
BACK_LEFT
BACK
BACK_RIGHT
barrier
construction vehicle
motorcycle
traffic cone
trailer
bicycle
bus
car
pedestrian
truck
driveable surface
other flat
sidewalk
terrain
manmade
vegetation
Camera As Input:
Camera As Input:
LiDAR As Input:
Figure 5. Visualization results on 3D semantic occupancy prediction and nuScenes LiDAR segmentation. Our method can generate
more comprehensive prediction results than the LiDAR segmentation ground truth.
50×50×4
90×90×7
100×100×8
400×400×32
200×200×16
75×75×6
FRONT_LEFT
FRONT
FRONT_RIGHT
BACK_RIGHT
BACK_LEFT
BACK
Camera Inputs
Semantic Occupancy Predictions
Figure 6. Arbitrary resolution at test time. We can adjust the prediction resolution through interpolation at test time. As resolution
increases, more details about the 3D objects are captured.
challenging task for vision-based 3D semantic occupancy
prediction. Under this task, the model is only trained us-
ing sparse semantic labels (LiDAR points) but is required
to produce a semantic occupancy for all the voxels in the
concerned 3D space during testing. As no benchmark is
provided for this, we only perform a qualitative analysis of
our method. Still, our method is the ﬁrst to demonstrate
effective results on this challenging task.
LiDAR segmentation. The LiDAR segmentation task
corresponds to the point querying formulation discussed in
Section 3.3, where we predict the semantic label of a given
point. The LiDAR segmentation task does not necessarily
use point clouds as input. In our case, we use only RGB
images as input, while the points are merely used to query
their features and for supervision in the training phase.
Semantic Scene Completion.
In conventional SSC,
given a single initial LiDAR scan, one needs to predict
whether each voxel is occupied and its semantic label for the
complete scene inside a certain volume. As a vision-centric
adaptation, we use as input only RGB images and predict
the occupancy and semantic label of each voxel. Accord-
ingly, we supervise the training process with voxel labels.
In the case of TPV representation, we adopt the voxel fea-
ture formulation in Section 3.3 to generate full-scale voxel
features. Following common practices, we report the inter-
section over union (IoU) of occupied voxels, ignoring their
semantic class, for the scene completion (SC) task and the
mIoU of all semantic classes for the SSC task.
4.2. Implementation Details
3D semantic occupancy prediction and LiDAR seg-
mentation.
We construct two versions of TPVFormer,
6
### Page 7

Table 1. LiDAR segmentation results on nuScenes test set. Despite critical modal difference, our TPVFormer-Base achieves comparable
performance with LiDAR-based methods.
Method
Input
Modality mIoU
■barrier
■bicycle
■bus
■car
■const. veh.
■motorcycle
■pedestrian
■trafﬁc cone
■trailer
■truck
■drive. suf.
■other ﬂat
■sidewalk
■terrain
■manmade
■vegetation
MINet [25]
LiDAR
56.3
54.6
8.2
62.1 76.6 23.0 58.7 37.6 34.9 61.5 46.9 93.3 56.4 63.8 64.8 79.3 78.3
PolarNet [50]
LiDAR
69.4
72.2 16.8 77.0 86.5 51.1 69.7 64.8 54.1 69.7 63.5 96.6 67.1 77.7 72.1 87.1 84.5
PolarSteam [9]
LiDAR
73.4
71.4 27.8 78.1 82.0 61.3 77.8 75.1 72.4 79.6 63.7 96.0 66.5 76.9 73.0 88.5 84.8
JS3C-Net [46]
LiDAR
73.6
80.1 26.2 87.8 84.5 55.2 72.6 71.3 66.3 76.8 71.2 96.8 64.5 76.9 74.1 87.5 86.1
AMVNet [30]
LiDAR
77.3
80.6 32.0 81.7 88.9 67.1 84.3 76.1 73.5 84.9 67.3 97.5 67.4 79.4 75.5 91.5 88.7
SPVNAS [43]
LiDAR
77.4
80.0 30.0 91.9 90.8 64.7 79.0 75.6 70.9 81.0 74.6 97.4 69.2 80.0 76.1 89.3 87.1
Cylinder3D++ [55]
LiDAR
77.9
82.8 33.9 84.3 89.4 69.6 79.4 77.3 73.4 84.6 69.4 97.7 70.2 80.3 75.5 90.4 87.6
AF2S3Net [12]
LiDAR
78.3
78.9 52.2 89.9 84.2 77.4 74.3 77.3 72.0 83.9 73.8 97.1 66.5 77.5 74.0 87.7 86.8
DRINet++ [48]
LiDAR
80.4
85.5 43.2 90.5 92.1 64.7 86.0 83.0 73.3 83.9 75.8 97.0 71.0 81.0 77.7 91.6 90.2
LidarMultiNet [47]
LiDAR
81.4
80.4 48.4 94.3 90.0 71.5 87.2 85.2 80.4 86.9 74.8 97.8 67.3 80.7 76.5 92.1 89.6
TPVFormer-Small (ours)
Camera
59.2
65.6 15.7 75.1 80.0 45.8 43.1 44.3 26.8 72.8 55.9 92.3 53.7 61.0 59.2 79.7 75.6
TPVFormer-Base (ours)
Camera
69.4
74.0 27.5 86.3 85.5 60.7 68.0 62.1 49.1 81.9 68.4 94.1 59.5 66.5 63.5 83.8 79.9
Table 2. Semantic scene completion results on SemanticKITTI test set. For fair comparison, we use the performances of RGB-inferred
versions of the ﬁrst four methods reported in MonoScene [5]. We signiﬁcantly outperform other methods in both IoU and mIoU, including
MonoScene which is based on 3D convolution.
Method
Input
Modality
SC
IoU
SSC
mIoU
road
(15.30%)
sidewalk
(11.13%)
parking
(1.12%)
other-grnd
(0.56%)
building
(14.1%)
car
(3.92%)
truck
(0.16%)
bicycle
(0.03%)
motorcycle
(0.03%)
other-veh.
(0.20%)
vegetation
(39.3%)
trunk
(0.51%)
terrain
(9.17%)
person
(0.07%)
bicyclist
(0.07%)
motorcyclist.
(0.05%)
fence
(3.90%)
pole
(0.29%)
traf.-sign
(0.08%)
LMSCNet [41]
Camera 31.38 7.07 46.70 19.50 13.50 3.10 10.30 14.30 0.30 0.00 0.00 0.00 10.80 0.00 10.40 0.00 0.00 0.00 5.40 0.00 0.00
3DSketch [10]
Camera 26.85 6.23 37.70 19.80 0.00 0.00 12.10 17.10 0.00 0.00 0.00 0.00 12.10 0.00 16.10 0.00 0.00 0.00 3.40 0.00 0.00
AICNet [24]
Camera 23.93 7.09 39.30 18.30 19.80 1.60 9.60 15.30 0.70 0.00 0.00 0.00 9.60 1.90 13.50 0.00 0.00 0.00 5.00 0.10 0.00
JS3C-Net [46]
Camera 34.00 8.97 47.30 21.70 19.90 2.80 12.70 20.10 0.80 0.00 0.00 4.10 14.20 3.10 12.40 0.00 0.20 0.20 8.70 1.90 0.30
MonoScene [5]
Camera 34.16 11.08 54.70 27.10 24.80 5.70 14.40 18.80 3.30 0.50 0.70 4.40 14.90 2.40 19.50 1.00 1.40 0.40 11.10 3.30 2.10
TPVFormer (ours) Camera 34.25 11.26 55.10 27.20 27.40 6.50 14.80 19.20 3.70 1.00 0.50 2.30 13.90 2.60 20.40 1.10 2.40 0.30 11.00 2.90 1.50
namely TPVFormer-Base and TPVFormer-Small, for dif-
ferent trade-offs between performance and efﬁciency.
TPVFormer-Base uses the ResNet101-DCN [15,19] initial-
ized from FCOS3D [44] checkpoint, while TPVFormer-
Small adopts the ResNet-50 [19] pretrained on Ima-
geNet [16]. Following Cylinder3D [55], we employ both
cross entropy loss and lovasz-softmax [3] loss to optimize
our network. For lovasz-softmax loss, we use features of
real points from LiDAR scans as input to maximize the IoU
score for classes, while voxel features are used in cross en-
tropy loss to improve point classiﬁcation accuracy and avoid
semantic ambiguity. For 3D semantic occupancy predic-
tion, we generate pseudo-per-voxel labels from sparse point
cloud by assigning a new label of empty to any voxel that
does not contain any point, and we use voxel predictions as
input to both lovasz-softmax and cross-entropy losses.
Semantic Scene Completion. We follow the settings
of MonoScene [5] in the SSC task for fair comparisons.
For model architecture, we adopt the 2D UNet based on
a pretrained EfﬁcientNetB7 [42] as 2D backbone to gen-
erate multi-scale image features, which is the same as
MonoScene.
For optimization, we employ the losses in
MonoScene except for the relation loss.
We provide more details in Section B.
4.3. 3D Semantic Occupancy Prediction Results
Main results. In Figure 5, we provide the main visual-
ization results for SOP. Our result is much denser and more
realistic than the LiDAR segmentation ground truth, which
validates the effectiveness of TPV representation in model-
ing the 3D scene and semantic occupancy prediction. Fur-
thermore, only querying the LiDAR points results in very
close predictions to the ground truth and excels the Cylin-
der3D counterpart in some cases. For example, Cylinder3D
fails to predict one of the two trucks on the rightmost side
of the ﬁrst scene, while our TPVFormer predicts correctly.
Arbitrary resolution at test time. Given the simplic-
ity of our segmentation head, we can adjust the resolution
of TPV planes at test time arbitrarily without retraining the
network. Figure 6 shows the results for resolution adjust-
ment, in which we gradually increase the resolution of TPV
planes from an initial 50x50x4 to 8 times larger. It is evi-
dent that as resolution increases, TPV representation is able
to capture more details about the 3D objects, such as shape.
More visualizations are included in Section C.
7
### Page 8

Table 3. Different prediction types as input to loss functions
for LiDAR segmentation. Voxel and point in the loss column
represent voxel and point predictions. We report mIoUs calculated
with both voxel and point predictions.
Loss
mIoU
CE.
Lovasz
Voxel
Point
Voxel
Voxel
63.17
50.66
Voxel
Point
63.37
64.80
Point
Voxel
64.07
64.46
Point
Point
49.94
64.02
Table 4. Ablations on resolutions and feature dimensions.
Method
Resolution
Feature Point mIoU
BEVFormer
100x100
256
50.37
200x200
256
56.21
TPVFormer
100x100x8
256
64.15
200x200x16
128
68.86
4.4. LiDAR segmentation Results
As the ﬁrst vision-based method for LiDAR segmenta-
tion task, we benchmark TPVFormer against LiDAR-based
methods. As shown in Table 1, TPVFormer achieves com-
parable mIoU (∼70%) with most LiDAR-based methods.
This is nontrivial since our method needs to reconstruct the
complete 3D scene at a high resolution from only 2D image
input, while the 3D structural information is readily avail-
able in the point clouds for LiDAR-based methods. We in-
clude results on the validation set in Section D.
4.5. Semantic Scene Completion Results
In Table 2, we report the results of the semantic scene
completion task on SemanticKITTI test set.
We com-
pare our TPVFormer against MonoScene [5], which is a
vision-based method based on 3D convolution in the voxel
space. We also include the 4 baseline methods provided in
MonoScene [5]. TPVFormer outperforms all other meth-
ods in both IoU and mIoU, which demonstrates the effec-
tiveness of TPVFormer in occupancy and semantics predic-
tion. Furthermore, TPVFormer enjoys signiﬁcant advan-
tages over MonoScene in both parameter number and com-
putation. Speciﬁcally, TPVFormer has only 6.0M param-
eters versus 15.7M for MonoScene, and 128G FLOPS per
image versus 500G for MonoScene. We report results on
the validation set in Section E.
4.6. Abation Study
We ablate our TPVFormer on the validation sets of
nuScenes and SemanticKITTI for LiDAR segmentation and
semantic scene completion, respectively.
Loss functions for LiDAR segmentation. We employ
both cross entropy (CE.) loss and lovasz-softmax loss [3]
for LiDAR segmentation. As our TPVFormer can produce
point-level and voxel-level predictions in a single forward
Table 5. Different number of HCAB blocks and HAB blocks
for semantic scene completion. We keep the total number of at-
tention modules the same in these experiments.
# HCAB
# HAB
SC IoU
SSC mIoU
2
4
35.55
10.49
3
2
35.61
11.36
4
0
35.79
10.82
propagation, we investigate different prediction types as in-
put to these loss functions. As shown in Table 3, when
both voxel and point predictions are used as input to the
loss functions, the mIoUs from both predictions are high
and close to each other. However, when only voxel or point
prediction is employed in optimization, the corresponding
mIoU will be much higher than the other one. We think the
TPV representation might be discretized in the voxel space
if given only voxel-level supervision, and thus the interpo-
lation used to generate point predictions will not apply. In
cases with only point-level supervision, TPV fails to learn
the discretization strategy implied in the voxel space.
Other design choices. We ablate other design choices
and compare our method with an adaptation of BEVFormer
in Table 4. TPVFormer favors resolution more than feature
dimension because increasing the resolution is a direct way
to enhance its ability for modelling more ﬁne-grained struc-
tures. In addition, our method performs better than BEV-
Former under all conﬁgurations, which conﬁrms that TPV
substantially improves the ability to describe ﬁne-grained
structures with three complementary cross-views.
The number of HCAB and HAB blocks. As HCAB
and HAB blocks aggregate visual information from im-
age features and contextual information from other TPV
queries, respectively, we study the proportion of the two
blocks in Table 5. The IoU improves as increasing the num-
ber of HCAB blocks, validating the importance of direct
visual clues for geometry understanding. However, the se-
mantic prediction relies on both visual and contextual infor-
mation as the maximum mIoU is achieved with a moderate
number of HCAB and HAB blocks.
5. Conclusion
In this paper, we have presented a tri-perspective view
(TPV) representation, which is able to describe the ﬁne-
grained structures of a 3D scene efﬁciently.
To lift im-
age features to the 3D TPV space, we have proposed
a TPVFormer model based on the attention mechanism.
The visualization results have shown that our TPVFormer
produces consistent semantic voxel occupancy prediction
with only sparse point supervision during training.
We
have demonstrated for the ﬁrst time that our vision-based
method achieves comparable performance with LiDAR-
based methods on nuScenes LiDAR segmentation task.
8
### Page 9

Figure 7. An image sampled from the video demo for 3D semantic occupancy prediction on nuScenes validation set (not seen in the
training phase). We predict the semantic occupancies for all voxels in the 3D space. The six images in the top left are the inputs to our
model captured by the front-left, front, front-right, back-left, back, and back-right cameras. The six images in the top right denote our
prediction results with the corresponding views as the inputs. The bottom two images provide a global view of our predictions where the
red-green-blue box represents the ego vehicle.
A. Dataset Details
The Panoptic nuScenes dataset [17] collects 1000 driv-
ing scenes of 20 seconds duration each, and the keyframes
are annotated at 2Hz. Each sample contains RGB images
from 6 cameras with 360◦horizontal FOV and point cloud
data from 32 beams LiDAR sensor. The total of 1000 scenes
are ofﬁcially divided into training, validation and test splits
with 700, 150 and 150 scenes, respectively.
The SemanticKITTI dataset [2] is a large-scale
outdoor-scene dataset, which includes automotive LiDAR
scans voxelized into 256 × 256 × 32 grids. Each voxel has
a side length of 0.2m and is labeled with one of 21 classes
(19 semantic, 1 free and 1 unknown). In our experiments,
we also use RGB images captured by cam2 from the KITTI
odometry benchmark. The voxel and image data is ofﬁcially
arranged as 22 sequences, split into 10/1/11 sequences for
training, validation and test.
B. Implementation Details
3D semantic occupancy prediction and LiDAR
segmentation.
TPVFormer-Base uses the ResNet101-
DCN [15, 19] initialized from FCOS3D [44] checkpoint,
while TPVFormer-Small adopts the ResNet-50 [19] pre-
trained on ImageNet [16].
The TPV resolutions are
200x200x16 and 100x100x8 for the base and small ver-
sions, respectively, and we upsample the TPV planes by a
factor of 2 in TPVFormer-Small for ﬁner supervision. Al-
though both of them share the same TPV feature dimension
of 128, the base model uses multi-scale image features and
an input image resolution of 1600x900 instead of single-
scale image features and 800x450 input for the small model.
For training, we adopt the AdamW [33] optimizer with
initial learning rate as 2e-4 and weight decay as 0.01. We
use the cosine learning rate scheduler with a linear warming
up in the ﬁrst 500 iterations, and the same image augmen-
tation strategy as BEVFormer [28]. All models are trained
for 24 epochs with a batch size of 8 on 8 A100 GPUs.
Semantic Scene Completion. We adopt the 2D UNet
based on a pretrained EfﬁcientNetB7 [42] as 2D backbone
to generate multi-scale image features, which is the same
as MonoScene. Moreover, we set the resolution of TPV
planes as 128x128x16 to generate a 3D voxel feature tensor
of the same size as MonoScene, although our TPV planes
9
### Page 10

are 2D feature maps while MonoScene operates directly on
3D voxel features. We use RGB images from cam2 cropped
to 1220x370 as input and a feature dimension of 96. For
optimization, we employ the losses in MonoScene except
for the relation loss, since TPVFormer does not have the 3D
CRP module or any downsampling operation. For training,
we generally follow the recipe in MonoScene. Speciﬁcally,
we use a learning rate of 2e-4, a weight decay of 0.01, and
a cosine scheduler. We keep the other settings the same.
For a fair comparison, we also rerun the ofﬁcial code of
MonoScene with a cosine learning rate scheduler.
C. 3D Semantic Occupancy Prediction Results
We provide a video demo 1 for 3D semantic occupancy
prediction on nuScenes validation set with a sampled im-
age in Figure 7. Figure 8 provides detailed visualization
results of our model for four samples from nuScenes val-
idation set. For each sample, we present the six surround
camera images, the top view of the predicted scene, and the
zoomed-in results from three different angles. In addition,
we highlight predictions for small and rare objects with cir-
cles and further link them to corresponding ground truths
in RGB images with arrowed dash lines. Speciﬁcally, we
highlight bicycles, motorcycles and pedestrians with red,
blue and yellow circles, respectively. Note that although
some of these objects are barely visible in RGB images, our
model still predicts them successfully.
D. LiDAR segmentation Results
In Table 6, we report the performance of TPVFormer
on nuScenes validation set for LiDAR segmentation. For
a fair comparison, we replace the temporal module in BEV-
Former with self-attention moduel and use a feature di-
mension of 256 to make the model sizes of BEVFormer-
Base and TPVFormer-Base comparable.
The mIoU of
TPVFormer-Base is on par with LiDAR-based meth-
ods despite critical modal differences.
Furthermore, our
TPVFormer-Base achieves a 12.7% higher mIoU than
BEVFormer-Base, which demonstrates the effectiveness of
TPV in modeling ﬁne-grained 3D structures of a scene.
E. Semantic Scene Completion Results
We present the semantic scene completion performance
on SemanticKITTI validation set in Table 7.
Although
TPVFormer does not achieve the highest IoU for scene
completion, it outperforms other methods in mIoU with a
clear margin for semantic scene completion. We reproduce
MonoScene [5] with the ofﬁcial code in our environment
and also report its performance using the cosine learning
rate following our recipe for a fair comparison.
1https://github.com/wzzheng/TPVFormer.
Figure 8. More visualizations of the proposed TPVFormer for 3D
semantic occupancy prediction.
References
[1] Adil Kaan Akan and Fatma G¨uney. Stretchbev: Stretching
future instance prediction spatially and temporally.
arXiv
preprint arXiv:2203.13641, 2022. 1
[2] Jens Behley, Martin Garbade, Andres Milioto, Jan Quen-
zel, Sven Behnke, Cyrill Stachniss, and Jurgen Gall.
Se-
mantickitti: A dataset for semantic scene understanding of
lidar sequences. In ICCV, pages 9297–9307, 2019. 2, 5, 9
[3] Maxim Berman, Amal Rannen Triki, and Matthew B
Blaschko. The lov´asz-softmax loss: A tractable surrogate
for the optimization of the intersection-over-union measure
in neural networks. In CVPR, pages 4413–4421, 2018. 7, 8
[4] Holger Caesar, Varun Bankiti, Alex H Lang, Sourabh Vora,
Venice Erin Liong, Qiang Xu, Anush Krishnan, Yu Pan, Gi-
ancarlo Baldan, and Oscar Beijbom.
nuscenes: A multi-
modal dataset for autonomous driving. In CVPR, 2020. 1,
2
[5] Anh-Quan Cao and Raoul de Charette. Monoscene: Monoc-
ular 3d semantic scene completion. In CVPR, pages 3991–
10
### Page 11

Table 6. LiDAR segmentation results on nuScenes validation set. Despite critical modal difference, our TPVFormer-Base achieves
comparable performance with LiDAR-based methods. Moreover, the mIoU gap between BEVFormer and TPVFormer clearly proves the
effectiveness of TPV in modelling ﬁne-grained 3D structures of a scene.
Method
Input
Modality mIoU
■barrier
■bicycle
■bus
■car
■const. veh.
■motorcycle
■pedestrian
■trafﬁc cone
■trailer
■truck
■drive. suf.
■other ﬂat
■sidewalk
■terrain
■manmade
■vegetation
RangeNet++ [36]
LiDAR
65.5
66.0 21.3 77.2 80.9 30.2 66.8 69.6 52.1 54.2 72.3 94.1 66.6 63.5 70.1 83.1 79.8
PolarNet [50]
LiDAR
71.0
74.7 28.2 85.3 90.9 35.1 77.5 71.3 58.8 57.4 76.1 96.5 71.1 74.7 74.0 87.3 85.7
Salsanext [14]
LiDAR
72.2
74.8 34.1 85.9 88.4 42.2 72.4 72.2 63.1 61.3 76.5 96.0 70.8 71.2 71.5 86.7 84.4
Cylinder3D++ [55]
LiDAR
76.1
76.4 40.3 91.2 93.8 51.3 78.0 78.9 64.9 62.1 84.4 96.8 71.6 76.4 75.4 90.5 87.4
BEVFormer-Base [28]
Camera
56.2
54.0 22.8 76.7 74.0 45.8 53.1 44.5 24.7 54.7 65.5 88.5 58.1 50.5 52.8 71.0 63.0
TPVFormer-Small (ours)
Camera
59.3
64.9 27.0 83.0 82.8 38.3 27.4 44.9 24.0 55.4 73.6 91.7 60.7 59.8 61.1 78.2 76.5
TPVFormer-Base (ours)
Camera
68.9
70.0 40.9 93.7 85.6 49.8 68.4 59.7 38.2 65.3 83.0 93.3 64.4 64.3 64.5 81.6 79.3
Table 7. Semantic scene completion results on SemanticKITTI validation set. For a fair comparison, we use the performances of
RGB-inferred versions of the ﬁrst four methods reported in MonoScene [5]. ∗represents the reproduced result using the ofﬁcial code. ∗∗
represents result using the cosine learning rate schedule.
Method
Input
Modality
SC
IoU
SSC
mIoU
road
(15.30%)
sidewalk
(11.13%)
parking
(1.12%)
other-grnd
(0.56%)
building
(14.1%)
car
(3.92%)
truck
(0.16%)
bicycle
(0.03%)
motorcycle
(0.03%)
other-veh.
(0.20%)
vegetation
(39.3%)
trunk
(0.51%)
terrain
(9.17%)
person
(0.07%)
bicyclist
(0.07%)
motorcyclist.
(0.05%)
fence
(3.90%)
pole
(0.29%)
traf.-sign
(0.08%)
LMSCNet [41]
Camera 28.61 6.70 40.68 18.22 4.38 0.00 10.31 18.33 0.00 0.00 0.00 0.00 13.66 0.02 20.54 0.00 0.00 0.00 1.21 0.00 0.00
3DSketch [10]
Camera 33.30 7.50 41.32 21.63 0.00 0.00 14.81 18.59 0.00 0.00 0.00 0.00 19.09 0.00 26.40 0.00 0.00 0.00 0.73 0.00 0.00
AICNet [24]
Camera 29.59 8.31 43.55 20.55 11.97 0.07 12.94 14.71 4.53 0.00 0.00 0.00 15.37 2.90 28.71 0.00 0.00 0.00 2.52 0.06 0.00
JS3C-Net [46]
Camera 38.98 10.31 50.49 23.74 11.94 0.07 15.03 24.65 4.41 0.00 0.00 6.15 18.11 4.33 26.86 0.67 0.27 0.00 3.94 3.77 1.45
MonoScene∗[5]
Camera 36.86 11.08 56.52 26.72 14.27 0.46 14.09 23.26 6.98 0.61 0.45 1.48 17.89 2.81 29.64 1.86 1.20 0.00 5.84 4.14 2.25
MonoScene∗∗[5]
Camera 36.13 10.98 56.30 25.89 15.91 0.75 13.47 23.31 5.36 0.72 0.91 3.77 17.70 2.45 27.12 1.71 1.08 0.00 6.34 3.79 2.03
TPVFormer (ours) Camera 35.61 11.36 56.50 25.87 20.60 0.85 13.88 23.81 8.08 0.36 0.05 4.35 16.92 2.26 30.38 0.51 0.89 0.00 5.94 3.14 1.52
4001, 2022. 2, 7, 8, 10, 11
[6] Rohan Chabra, Jan E Lenssen, Eddy Ilg, Tanner Schmidt,
Julian Straub, Steven Lovegrove, and Richard Newcombe.
Deep local shapes: Learning local sdf priors for detailed 3d
reconstruction. In ECCV, pages 608–625, 2020. 3
[7] Eric R Chan, Connor Z Lin, Matthew A Chan, Koki Nagano,
Boxiao Pan, Shalini De Mello, Orazio Gallo, Leonidas J
Guibas, Jonathan Tremblay, Sameh Khamis, et al.
Efﬁ-
cient geometry-aware 3d generative adversarial networks. In
CVPR, pages 16123–16133, 2022. 2, 3
[8] Anpei Chen, Zexiang Xu, Andreas Geiger, Jingyi Yu, and
Hao Su. Tensorf: Tensorial radiance ﬁelds. arXiv preprint
arXiv:2203.09517, 2022. 2, 3
[9] Qi Chen, Sourabh Vora, and Oscar Beijbom. Polarstream:
Streaming object detection and segmentation with polar pil-
lars. NeurIPS, 34:26871–26883, 2021. 7
[10] Xiaokang Chen, Kwan-Yee Lin, Chen Qian, Gang Zeng, and
Hongsheng Li. 3d sketch-aware semantic scene completion
via semi-supervised structure prior. In CVPR, pages 4193–
4202, 2020. 2, 7, 11
[11] Yinbo Chen, Sifei Liu, and Xiaolong Wang. Learning con-
tinuous image representation with local implicit image func-
tion. In CVPR, pages 8628–8638, 2021. 3
[12] Ran Cheng, Ryan Razani, Ehsan Taghavi, Enxu Li, and
Bingbing Liu. 2-s3net: Attentive feature fusion with adap-
tive feature selection for sparse semantic segmentation net-
work. In CVPR, pages 12547–12556, 2021. 2, 7
[13] Christopher Choy, JunYoung Gwak, and Silvio Savarese. 4d
spatio-temporal convnets: Minkowski convolutional neural
networks. In CVPR, pages 3075–3084, 2019. 1
[14] Tiago Cortinhal, George Tzelepis, and Eren Erdal Aksoy.
Salsanext: Fast, uncertainty-aware semantic segmentation of
lidar point clouds.
In International Symposium on Visual
Computing, pages 207–222. Springer, 2020. 11
[15] Jifeng Dai, Haozhi Qi, Yuwen Xiong, Yi Li, Guodong
Zhang, Han Hu, and Yichen Wei. Deformable convolutional
networks. In ICCV, 2017. 4, 7, 9
[16] Jia Deng, Wei Dong, Richard Socher, Li-Jia Li, Kai Li,
and Li Fei-Fei. Imagenet: A large-scale hierarchical image
database. In CVPR, pages 248–255, 2009. 7, 9
[17] Whye Kit Fong, Rohit Mohan, Juana Valeria Hurtado, Lub-
ing Zhou, Holger Caesar, Oscar Beijbom, and Abhinav Val-
ada.
Panoptic nuscenes: A large-scale benchmark for li-
dar panoptic segmentation and tracking.
arXiv preprint
arXiv:2109.03805, 2021. 5, 9
[18] Vitor Guizilini,
Igor Vasiljevic,
Rares Ambrus,
Greg
Shakhnarovich,
and Adrien Gaidon.
Full surround
monodepth
from
multiple
cameras.
arXiv
preprint
arXiv:2104.00152, 2021. 1
[19] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun.
Deep residual learning for image recognition.
In CVPR,
11
### Page 12

2016. 7, 9
[20] Anthony Hu, Zak Murez, Nikhil Mohan, Sof´ıa Dudas, Jef-
frey Hawke, Vijay Badrinarayanan, Roberto Cipolla, and
Alex Kendall. Fiery: Future instance prediction in bird’s-
eye view from surround monocular cameras. In ICCV, pages
15273–15282, 2021. 1
[21] Junjie Huang, Guan Huang, Zheng Zhu, and Dalong Du.
Bevdet: High-performance multi-camera 3d object detection
in bird-eye-view. arXiv preprint arXiv:2112.11790, 2021. 1,
2
[22] Yanqin Jiang, Li Zhang, Zhenwei Miao, Xiatian Zhu, Jin
Gao, Weiming Hu, and Yu-Gang Jiang. Polarformer: Multi-
camera 3d object detection with polar transformers. arXiv
preprint arXiv:2206.15398, 2022. 3
[23] Alex H Lang, Sourabh Vora, Holger Caesar, Lubing Zhou,
Jiong Yang, and Oscar Beijbom. Pointpillars: Fast encoders
for object detection from point clouds. In CVPR, 2019. 2
[24] Jie Li, Kai Han, Peng Wang, Yu Liu, and Xia Yuan.
Anisotropic convolutional networks for 3d semantic scene
completion. In CVPR, pages 3351–3359, 2020. 2, 7, 11
[25] Shijie Li, Xieyuanli Chen, Yun Liu, Dengxin Dai, Cyrill
Stachniss, and Juergen Gall. Multi-scale interaction for real-
time lidar data segmentation on an embedded platform. RA-
L, 7(2):738–745, 2021. 7
[26] Yanwei Li, Yilun Chen, Xiaojuan Qi, Zeming Li, Jian Sun,
and Jiaya Jia.
Unifying voxel-based representation with
transformer for 3d object detection. In Advances in Neural
Information Processing Systems, 2022. 2, 3
[27] Yinhao Li, Zheng Ge, Guanyi Yu, Jinrong Yang, Zengran
Wang, Yukang Shi, Jianjian Sun, and Zeming Li. Bevdepth:
Acquisition of reliable depth for multi-view 3d object detec-
tion. arXiv preprint arXiv:2206.10092, 2022. 1, 2, 3
[28] Zhiqi Li, Wenhai Wang, Hongyang Li, Enze Xie, Chong-
hao Sima, Tong Lu, Qiao Yu, and Jifeng Dai. Bevformer:
Learning bird’s-eye-view representation from multi-camera
images via spatiotemporal transformers. In ECCV, 2022. 1,
2, 3, 9, 11
[29] Tingting Liang, Hongwei Xie, Kaicheng Yu, Zhongyu Xia,
Zhiwei Lin, Yongtao Wang, Tao Tang, Bing Wang, and Zhi
Tang. Bevfusion: A simple and robust lidar-camera fusion
framework. arXiv preprint arXiv:2205.13790, 2022. 1, 2
[30] Venice Erin Liong, Thi Ngoc Tho Nguyen, Sergi Wid-
jaja, Dhananjai Sharma, and Zhuang Jie Chong. Amvnet:
Assertion-based multi-view fusion network for lidar seman-
tic segmentation. arXiv preprint arXiv:2012.04934, 2020. 2,
7
[31] Yingfei Liu, Tiancai Wang, Xiangyu Zhang, and Jian Sun.
Petr: Position embedding transformation for multi-view 3d
object detection. arXiv preprint arXiv:2203.05625, 2022. 1
[32] Zhijian Liu, Haotian Tang, Alexander Amini, Xinyu Yang,
Huizi Mao, Daniela Rus, and Song Han. Bevfusion: Multi-
task multi-sensor fusion with uniﬁed bird’s-eye view repre-
sentation. arXiv preprint arXiv:2205.13542, 2022. 1, 2, 3
[33] Ilya Loshchilov and Frank Hutter. Decoupled weight decay
regularization. In ICLR, 2019. 9
[34] Lars Mescheder, Michael Oechsle, Michael Niemeyer, Se-
bastian Nowozin, and Andreas Geiger. Occupancy networks:
Learning 3d reconstruction in function space.
In CVPR,
pages 4460–4470, 2019. 3
[35] B Mildenhall, PP Srinivasan, M Tancik, JT Barron, R Ra-
mamoorthi, and R Ng. Nerf: Representing scenes as neural
radiance ﬁelds for view synthesis. In ECCV, 2020. 3
[36] Andres Milioto, Ignacio Vizzo, Jens Behley, and Cyrill
Stachniss.
Rangenet++: Fast and accurate lidar semantic
segmentation. In IROS, pages 4213–4220. IEEE, 2019. 11
[37] Jeong Joon Park, Peter Florence, Julian Straub, Richard
Newcombe, and Steven Lovegrove. Deepsdf: Learning con-
tinuous signed distance functions for shape representation.
In CVPR, pages 165–174, 2019. 3
[38] Jonah Philion and Sanja Fidler. Lift, splat, shoot: Encoding
images from arbitrary camera rigs by implicitly unprojecting
to 3d. In ECCV, pages 194–210, 2020. 1, 2
[39] Cody Reading, Ali Harakeh, Julia Chae, and Steven L
Waslander.
Categorical depth distribution network for
monocular 3d object detection. In CVPR, 2021. 2
[40] Christian Reiser, Songyou Peng, Yiyi Liao, and Andreas
Geiger. Kilonerf: Speeding up neural radiance ﬁelds with
thousands of tiny mlps. In ICCV, pages 14335–14345, 2021.
3
[41] Luis Roldao, Raoul de Charette, and Anne Verroust-Blondet.
Lmscnet: Lightweight multiscale 3d semantic completion.
In 2020 International Conference on 3D Vision (3DV), pages
111–119. IEEE, 2020. 2, 7, 11
[42] Mingxing Tan and Quoc Le. Efﬁcientnet: Rethinking model
scaling for convolutional neural networks. In ICML, pages
6105–6114, 2019. 7, 9
[43] Haotian Tang, Zhijian Liu, Shengyu Zhao, Yujun Lin, Ji Lin,
Hanrui Wang, and Song Han. Searching efﬁcient 3d architec-
tures with sparse point-voxel convolution. In ECCV, pages
685–702, 2020. 2, 3, 7
[44] Tai Wang, Xinge Zhu, Jiangmiao Pang, and Dahua Lin.
Fcos3d: Fully convolutional one-stage monocular 3d object
detection. In ICCV, 2021. 7, 9
[45] Yi Wei, Linqing Zhao, Wenzhao Zheng, Zheng Zhu, Yong-
ming Rao, Guan Huang, Jiwen Lu, and Jie Zhou. Surround-
depth:
Entangling surrounding views for self-supervised
multi-camera depth estimation. In CoRL, 2022. 1
[46] Xu Yan, Jiantao Gao, Jie Li, Ruimao Zhang, Zhen Li, Rui
Huang, and Shuguang Cui. Sparse single sweep lidar point
cloud segmentation via learning contextual shape priors from
scene completion. In AAAI, volume 35, pages 3101–3109,
2021. 2, 7, 11
[47] Dongqiangzi Ye, Zixiang Zhou, Weijia Chen, Yufei Xie, Yu
Wang, Panqu Wang, and Hassan Foroosh.
Lidarmultinet:
Towards a uniﬁed multi-task network for lidar perception.
arXiv preprint arXiv:2209.09385, 2022. 2, 7
[48] Maosheng Ye, Rui Wan, Shuangjie Xu, Tongyi Cao, and
Qifeng Chen. Drinet++: Efﬁcient voxel-as-point point cloud
segmentation. arXiv preprint arXiv: 2111.08318, 2021. 2,
3, 7
[49] Yunpeng Zhang, Wenzhao Zheng, Zheng Zhu, Guan Huang,
Jie Zhou, and Jiwen Lu. A simple baseline for multi-camera
3d object detection. arXiv preprint arXiv:2208.10035, 2022.
1
12
### Page 13

[50] Yang Zhang, Zixiang Zhou, Philip David, Xiangyu Yue, Ze-
rong Xi, Boqing Gong, and Hassan Foroosh. Polarnet: An
improved grid representation for online lidar point clouds se-
mantic segmentation. In CVPR, pages 9601–9610, 2020. 7,
11
[51] Yunpeng Zhang, Zheng Zhu, Wenzhao Zheng, Junjie Huang,
Guan Huang, Jie Zhou, and Jiwen Lu. Beverse: Uniﬁed per-
ception and prediction in birds-eye-view for vision-centric
autonomous driving.
arXiv preprint arXiv:2205.09743,
2022. 1, 2
[52] Yin Zhou and Oncel Tuzel. Voxelnet: End-to-end learning
for point cloud based 3d object detection. In CVPR, pages
4490–4499, 2018. 2
[53] Xizhou Zhu, Weijie Su, Lewei Lu, Bin Li, Xiaogang Wang,
and Jifeng Dai. Deformable {detr}: Deformable transform-
ers for end-to-end object detection. In ICLR, 2021. 4
[54] Xinge Zhu, Hui Zhou, Tai Wang, Fangzhou Hong, Yuexin
Ma, Wei Li, Hongsheng Li, and Dahua Lin. Cylindrical and
asymmetrical 3d convolution networks for lidar segmenta-
tion. In CVPR, pages 9939–9948, 2021. 2
[55] Xinge Zhu, Hui Zhou, Tai Wang, Fangzhou Hong, Yuexin
Ma, Wei Li, Hongsheng Li, and Dahua Lin. Cylindrical and
asymmetrical 3d convolution networks for lidar segmenta-
tion. In CVPR, pages 9939–9948, 2021. 2, 7, 11
13