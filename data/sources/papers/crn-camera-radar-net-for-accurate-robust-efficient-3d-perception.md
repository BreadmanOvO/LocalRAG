# CRN: Camera Radar Net for Accurate, Robust, Efficient 3D Perception

**Source**: arXiv:2304.00670

**Type**: Academic Paper

---

## Page 1

CRN: Camera Radar Net for Accurate, Robust, Efficient 3D Perception
Youngseok Kim1
Juyeb Shin1
Sanmin Kim1
In-Jae Lee1
Jun Won Choi2
Dongsuk Kum1
1KAIST
2Hanyang University
{youngseok.kim, juyebshin, sanmin.kim, injaelee, dskum}@kaist.ac.kr, junwchoi@hanyang.ac.kr
Abstract
Autonomous driving requires an accurate and fast 3D
perception system that includes 3D object detection, track-
ing, and segmentation. Although recent low-cost camera-
based approaches have shown promising results, they are
susceptible to poor illumination or bad weather conditions
and have a large localization error. Hence, fusing cam-
era with low-cost radar, which provides precise long-range
measurement and operates reliably in all environments, is
promising but has not yet been thoroughly investigated. In
this paper, we propose Camera Radar Net (CRN), a novel
camera-radar fusion framework that generates a semanti-
cally rich and spatially accurate bird’s-eye-view (BEV) fea-
ture map for various tasks. To overcome the lack of spa-
tial information in an image, we transform perspective view
image features to BEV with the help of sparse but accu-
rate radar points. We further aggregate image and radar
feature maps in BEV using multi-modal deformable atten-
tion designed to tackle the spatial misalignment between
inputs.
CRN with real-time setting operates at 20 FPS
while achieving comparable performance to LiDAR detec-
tors on nuScenes, and even outperforms at a far distance
on 100m setting. Moreover, CRN with offline setting yields
62.4% NDS, 57.5% mAP on nuScenes test set and ranks first
among all camera and camera-radar 3D object detectors.
1. Introduction
Accurate and robust 3D perception system is crucial for
many applications, such as autonomous driving and mo-
bile robot. For efficient 3D perception, obtaining a reli-
able bird’s eye view (BEV) feature map from sensor inputs
is necessary since various downstream tasks can be oper-
ated on BEV space (e.g., object detection & tracking [84],
BEV segmentation [87], HD map generation [67], trajec-
tory prediction [19], and motion planning [55]). Another
important ingredient for deploying 3D perception to the
real world is to build a system that relies less on LiDAR
disadvantaged from high-cost, high-maintenance, and low-
reliability. Apart from the drawbacks of LiDAR, 3D per-
35
40
45
50
55
60
0
5
10
15
20
25
30
NDS [%]
FPS [frame/s]
PETR
CRN (Ours)
BEVFormer
BEVDepth
CRAFT
SOLOFusion
256×704
384×1056
512×1408
900×1600
Figure 1.
FPS vs. accuracy on nuScenes val set. We show
that fusing radar can significantly boost camera-only method with
marginal computational cost. CRN outperforms all methods with
much faster speed. See Table 1 and Fig. 6 for more details.
ception system is required to identify semantic information
on the road (e.g., traffic lights, road sign) that can be eas-
ily leveraged by camera. In addition to the need for rich
semantic information, detecting distant objects is essential,
and this can be benefited from radar.
Recently, camera-based 3D perception in BEV [22, 55,
60] has drawn great attention. Thanks to rich semantic in-
formation in dense image pixels, camera approaches can
distinguish objects even at a far distance. Despite the advan-
tage of cameras, localizing the accurate position of objects
from a monocular image is naturally a challenging ill-posed
problem. Moreover, cameras can be significantly affected
by illumination conditions (e.g., glare, low-contrast, or low-
lighting) due to the nature of the passive sensor. To address
this, we aim to generate a BEV feature map using a camera
with the help of a cost-effective range sensor, radar.
Radar has advantages not only in cost but also in high-
reliability, long-range perception (up to 200m for typical
automotive radar [8]), robustness in various conditions (e.g.,
snow, fog, or rain), and providing velocity estimation from
a single measurement. However, radar also brings its chal-
lenges such as sparsity (typically 180× fewer than LiDAR
points per single frame in nuScenes [2]), noisy and am-
biguous measurements (false negatives by low resolution,
arXiv:2304.00670v3  [cs.CV]  23 Dec 2023


## Page 2

accuracy, or low radar cross-section, and false positives
by multi-path or clutters). As a result, previous camera-
radar fusion methods using late fusion strategies that fuse
detection-level results [7, 15] fail to fully exploit the com-
plementary information, thus having limited performance
and operating environment. Despite the huge potential of
learning-based fusion, only a few studies [26, 27, 51] ex-
plore camera-radar fusion in autonomous driving scenarios.
To put the aforementioned advantages and disadvan-
tages of camera and radar in perspective, camera-radar fu-
sion should be capable of following properties to fully
exploit the complementary characteristics of each sensor.
First, camera features should be accurately transformed into
BEV space in terms of spatial position. Second, the fu-
sion method should be able to handle the spatial misalign-
ment between feature maps when aggregating two modal-
ities. Last but not least, transformation and fusion should
be adaptive in order to tackle noisy and ambiguous radar
measurements.
To this end, we design a novel two-stage fusion method
for BEV feature encoding, Camera Radar Net (CRN). The
key idea of the proposed method is to generate semantically
rich and spatially accurate BEV feature map by fusing com-
plementary characteristics of camera and radar sensors. In
particular, we first transform image features in perspective
view into BEV not solely relying on estimated depth but us-
ing radar, named radar-assisted view transformation (RVT).
Since transformed image features in BEV is not completely
accurate, following multi-modal feature aggregation (MFA)
layers consecutively encodes the multi-modal feature maps
into a unified feature map using an attention mechanism.
We conduct extensive experiments on nuScenes and demon-
strate that our proposed method can generate a fine-grained
BEV feature map to set the new state-of-the-art on various
tasks while maintaining high efficiency, as shown in Fig 1.
The main contributions of our works are three-fold:
• Accuracy.
CRN achieves LiDAR-level performance
using camera and radar on 3D object detection, track-
ing, and BEV segmentation tasks.
• Robustness.
CRN maintains robust performance
even if one of the single sensor inputs is entirely un-
available, which allows the fault-tolerant system.
• Efficiency.
CRN requires marginal extra cost for
significant performance improvement, which enables
long-range perception in real-time.
2. Related Work
Camera-based 3D Perception.
Thanks to well-
established 2D object detection methods [73, 89] on per-
spective view images, early approaches extend 2D detector
to 3D detector by additionally estimating the distance to ob-
jects [68, 78], then transforming object center. DD3D [53]
improves detection performance by pre-training depth es-
timation task on depth dataset [16].
Although a simple
and intuitive approach, the view discrepancy between in-
put feature space (perspective view, PV) and output space
(bird’s-eye-view, BEV) restricts the network from extend-
ing to other tasks.
Recent advances in camera-based perception exploit
view transformation.
Geometry-based methods [35, 54,
55, 60] explicitly estimate the depth distribution of each
image feature on PV and transform them into BEV.
BEVDepth [35] empirically shows that training depth dis-
tribution with auxiliary pixel-wise depth supervision im-
proves the performance, which corresponds to the results of
DD3D [53]. Learning-based methods [23, 36, 48, 87] im-
plicitly model the mapping function from PV to BEV using
multi-layer perceptron (MLP) [32, 61] or attention [36, 63].
Obtaining a BEV feature map allows the framework to
be easily extended to various downstream tasks performed
on BEV space, such as 3D detection and tracking [35], seg-
mentation [87], and prediction [55]. However, camera-only
methods have limited localization accuracy due to the ab-
sence of distance information in image and are sensitive to
lighting or weather conditions. Moreover, achieving high
performance only using a camera requires large image in-
put and backbone, which is slow and not applicable for real-
time applications.
Point-based 3D Perception.
LiDAR is the most com-
mon and favorable sensor for autonomous driving, while
radar point cloud has not yet been thoroughly investi-
gated.
LiDAR-only 3D detectors extract features (e.g.,
PointNet [58, 59]) given irregular and unordered point sets
and predict 3D objects on point- [65] or voxelized- [29]
feature. Some approaches further utilize point and voxel
features together [64], use range view as additional fea-
tures [79], or filter background points [70].
Although similar data representation of radar point
cloud [2, 50] to LiDAR, radar point-based 3D perception
is considerably less investigated. Several works [56, 69, 81]
examine the radar points for free space detection, but only
a few studies [71, 75] attempt 3D object detection in au-
tonomous driving.
Radar point-based detection methods
adapt PointPillars [29] with graph neural network [66] or
KPConv [72] focusing on extracting better local features.
However, mostly due to many clutter points and lack of
contextual information on radar, the performance of radar-
only methods lags significantly behind compared to LiDAR.
Considering the high potential of radar having robust mea-
surements regardless of weather conditions and perception
range, fusing radar with a camera is promising to supple-
ment the insufficient semantic information.
Camera-Point 3D Perception.
Fusing complementary
information of camera image and range measurement is a


## Page 3

⊗
Multi-modal
Deformable
Cross
Attention
Depth (PV)
Distribution
Radar (PV)
Occupancy
Image Feature (PV)
Radar Feature (BEV)
Image Feature (BEV)
3D Detection & Tracking
BEV Segmentation
K, V
K, V
Multi-view Images 
& Radar Point Cloud
Fused Feature
BEV Pooling
Radar-assisted View Transformation
Multi-modal Feature Aggregation
Depth Supervision
(Sparse
Aggr.)
+
Figure 2.
The overall architecture of the proposed Camera Radar Net. Given multi-view images and radar points, modality-specific
backbones extract features in each view. First, image context features in perspective view are transformed into a bird’s-eye-view with the
help of radar measurements by Radar-assisted View Transformation (RVT). After, Multi-modal Feature Aggregation (MFA) adaptively
aggregates image and radar feature maps to generate semantically rich and spatially accurate bird’s-eye-view representation.
promising and active research topic.
However, the view
discrepancy between two sensors is regarded as a bottle-
neck for multi-modal fusion. A line of approach handles
discrepancy by projecting 3D information to a 2D image
(e.g., points [6, 77, 82], proposals [1, 26, 28], or prediction
results [52]) and gathering information around the projected
region. Some camera-radar fusion methods [38, 46] attempt
to improve depth estimation by projecting radar points to
the image.
On the other hand, another line of work lifts 2D image in-
formation into 3D. Early studies in 3D detection [27, 51, 57]
detect 2D or 2.5D object proposals and lift them into 3D
space to fuse with point data; however, this object-level
fusion is difficult to be generalized to other tasks in BEV.
Thanks to advances in monocular BEV approaches, re-
cent fusion approaches extract image and point feature
maps in unified BEV space and then fuse feature maps
by element-wise concatenation [45] or summation [34], as-
suming multi-modal feature maps are spatially well aligned.
After, the fused BEV feature map is used in various percep-
tion tasks such as 3D detection [12, 34, 37, 85], BEV seg-
mentation [45, 88], or HD map generation [11, 32]. How-
ever, despite the unique characteristics of a camera (e.g.,
inaccurate BEV transformation) and radar (e.g., sparsity
and ambiguity), previous camera-radar fusion less considers
them. Our proposed CRN focuses on fusing multi-modal
feature maps considering the characteristics of each sensor
thoroughly to have the best of both worlds.
3. Camera Radar Net
In this paper, we propose a camera radar fusion frame-
work to produce a unified BEV representation given multi-
view images and radar points, as illustrated in Fig 2. In
Sec. 3.2, we introduce a method to transform image features
with radar, then a multi-modal feature aggregation method
in Sec. 3.3. Finally, generated BEV feature map is used for
downstream tasks in Sec. 3.4.
3.1. Preliminaries
Monocular 3D Approaches.
The crux of monocular 3D
perception is how to construct accurate 3D (or BEV) in-
formation from 2D features, which can be categorized into
two groups. Geometry-based approaches [35, 55, 60] pre-
dict depth D as an explicit intermediate representation and
transform features F in perspective view (u, v) into frustum
view (d, u, v) then 3D (x, y, z) by:
F3D(x, y, z) = M(F2D(u, v) ⊗D(u, v)),
(1)
where M denotes view transformation module (e.g., Voxel
Pooling [35, 45]) and ⊗denotes outer product. Meanwhile,
learning-based approaches [36, 87] implicitly model 3D to
2D projection utilizing mapping networks as:
F3D(x, y, z) = f(Pxyz, F2D(u, v)),
(2)
where f denotes mapping function between perspective
view and BEV (e.g., multi-layer perceptron (MLP) [61] or
cross-attention [36]), and Pxyz is voxels in 3D space. Al-
though the approaches are different, the key is to obtain spa-
tially accurate 3D features F3D(x, y, z) through implicit or
explicit transformation. We aim to explicitly improve the
transformation process using radar measurement.
Radar Characteristics.
Radar can have various repre-
sentations (e.g., 2-D FFT [42], 3D Tensor [25, 49], point
cloud [2, 50]). Radar point cloud has a similar represen-
tation to LiDAR, but their characteristics are different in
terms of resolution and accuracy [8]. Moreover, due to the
nature of the operating mechanism of radar [24, 31] and its
millimeter scale wavelength, radar measurements are noisy,
ambiguous, and do not provide elevation. Therefore, radar
measurements are often not returned when objects exist or
returned when objects do not exist; hence, naively adopt-
ing LiDAR methods to radar shows very limited perfor-
mance on complex scenarios, as in Tables 7 and 8 (Center-
Point [84] with radar input). We exploit radar in an adaptive
manner to handle its sparsity and ambiguity.


## Page 4

D
W
H
⊗
Depth Distribution
[N×D×H×W]
Image Context (PV)
[N×C×H×W]
Image Context (FV)
[N×C×D×H×W]
Radar Occupancy
[N×D×1×W]
Image Context (FV)
[N×C×D×1×W]
Image Context (FV)
[N×C×D×1×W]
⊗
=
=
Image Context (PV)
[N×C×1×W]
⇒
⇒
Collapse
Collapse
Figure 3.
Radar-assisted View Transformation (RVT). The pro-
posed RVT can benefit from dense but less accurate depth distri-
bution and sparse but accurate radar occupancy to obtain spatially
accurate image context features.
3.2. Radar-assisted View Transformation (RVT)
Image Feature Encoding and Depth Distribution. Given
a set of N surrounding images, we use an image back-
bone (e.g., ResNet [18], ConvNeXt [44]) with a feature
pyramid network (FPN) [39] and obtain 16× downsam-
pled feature map FI for each image view.
Then, addi-
tional convolutional layers further extract image context
features CP V
I
∈RN×C×H×W and depth distribution of
each pixel DI ∈RN×D×H×W in perspective view, follow-
ing LSS [55]:
CP V
I
= Conv(FI)
DI(u, v) = Softmax(Conv(FI)(u, v)),
(3)
where (u, v) indicates coordinate in the image plane, and D
is the number of depth bins.
Radar Feature Encoding and Radar Occupancy.
Un-
like previous methods [35, 55, 60] that directly “lift” im-
age features into BEV using estimated depth distribution as
Eq. 1, we exploit noisy yet accurate radar measurements for
view transformation. Radar points are first projected onto
each N camera view to find corresponding image pixels
while preserving its depth, then voxelized [29] into cam-
era frustum view voxels VF V
R (d, u, v). Note that u, v are
pixel units in the image width and height directions, while
d is a metric unit in a depth direction. We set v = 1 to
use pillar-style since radars do not provide reliable elevation
measurements. The non-empty radar pillars are encoded
into features FR ∈RN×C×D×W with PointNet [59] and
sparse convolution [83]. Similar to Eq. 3, we extract radar
context feature CF V
R
∈RN×C×D×W and radar occupancy
OR ∈RN×1×D×W in frustum view. Here, convolution is
applied to top-view (d, u) coordinate instead of (u, v):
CF V
R
= Conv(FR), OR(d, u) = σ(Conv(FR)(d, u)).
(4)
Here, a sigmoid is used instead of softmax since radar oc-
cupancy is not necessarily one-hot encoded as a depth dis-
tribution.
Frustum View Transformation.
Given depth distribution
DI and radar occupancy OR, the image context feature map
CP V
I
is transformed into a camera frustum view CF V
I
∈
RN×C×D×H×W as:
CF V
I
= Conv[CP V
I
⊗DI; CP V
I
⊗OR],
(5)
where [·; ·] denotes the concatenation operating along the
channel dimension and ⊗is the outer product. Due to the
absence of height dimension in radar and for saving mem-
ory, we collapse the image context feature by summation
along the height axis, as illustrated in Fig. 3.
Bird’s-Eye-View Transformation.
Finally, camera and
radar context feature maps in N camera frustum views
FF V = {CF V
I
, CF V
R
∈RN×C×D×H×W } are transformed
into a single BEV space RC×1×X×Y by view transforma-
tion module M:
FBEV = M({FF V
i
}N
i=1).
(6)
Specifically, we adopt CUDA-enabled Voxel Pooling [33]
implementation and modify it to aggregate features within
each BEV grid using average pooling instead of summation.
It helps the network to predict a more consistent BEV fea-
ture map regardless of the distance to the ego vehicle since
a closer BEV grid is associated with a more frustum grid
due to the perspective projection.
3.3. Multi-modal Feature Aggregation (MFA)
Motivation.
Combining complementary multi-modal in-
formation while avoiding the drawbacks of each is espe-
cially crucial in camera radar fusion, as claimed in Sec. 3.1.
Image feature has rich semantic cues, but their spatial posi-
tion is inherently inaccurate; on the other hand, radar feature
is spatially accurate, but contextual information is insuffi-
cient and noisy. Naive approaches are channel-wise con-
catenation [45] or summation [34], but these cannot han-
dle neither spatial misalignment nor ambiguity between two
modalities, thus less effective, as can be seen in Table 6. To
have the best of both worlds, the key motivation of our fu-
sion is to leverage multi-modal features in an adaptive man-
ner, using an attention mechanism [76].
Multi-modal Deformable Cross Attention (MDCA).
Cross attention [76] is inherently suitable for multi-modal
fusion. However, the computation cost is quadratic to input
sequence length O(N 2), where N = XY and X, Y denote
the height and width of the BEV feature map. If we assume
perception range R = X/2 = Y/2, computation com-
plexity becomes biquadratic O(16R4) to perception range,
which is not scalable for a long-range perception; Thus
we develop the fusion method based on deformable atten-
tion [91], which is of linear complexity with the input size
O(2N +NK), where K is the total number of the sampled
key (K ≪N = XY ).


## Page 5

(a) Fusion
(b) Image
(c) Radar
Figure 4. Visualization of feature maps trained on detection task.
In image, a vehicle heavily occluded (white) or hardly visible at
a long distance (blue) is not detected. In radar, clutters from the
wall (black) or pedestrian with row RCS (red) lead to failure. Our
MFA generates a more reliable BEV feature map by fusion. Note
that BEV feature maps are cropped for better visualization.
Given flattened BEV context feature maps xm
=
{CBEV
I
, CBEV
R
∈RC×XY }, we first project xm into
C dimensional query feature after concatenation as zq =
W z[LN(CI); LN(CP )], where W z ∈RC×2C is a linear
projection and LN is layer norm. After, the feature map is
aggregated by multi-modal deformable cross attention as
MDCA(zq, pq, xm) =
H
X
h
W h
" M
X
m
K
X
k
Ahmqk · W ′
hmxm(ϕm(pq + ∆phmqk))
#
,
(7)
where h, m, k indexes the attention head, modality, and
sampling point. To better exploit multi-modal information,
we separately apply attention weights Ahmqk and sampling
offset ∆phmqk to multi-modal feature maps xm. By do-
ing so, the feature aggregation module can adaptively ben-
efit from image and radar as shown in Fig. 4. We refer the
reader to Appendix for details of the notation.
Sparse Aggregation.
Although MDCA has linear com-
plexity with respect to the size of BEV grids, it still can
be a bottleneck when the perception range becomes large.
Inspired by [62], we propose a method to further reduce
the number of input queries from N = XY to N =
Nk ≪XY by using features with top-k confidence. Given
BEV depth distribution DI and radar occupancy OP , Nk
features zNk
q
∈RC×Nk are selected from input queries
zq ∈RC×XY using a probability of max(DI, OP ). The
complexity of the proposed sparse aggregation is now in-
dependent of perception range, which is more efficient for
long-range perception.
3.4. Training Objectives and Task Heads
For all tasks, we train the depth distribution network with
a depth map obtained by projecting LiDAR points into the
image view, following BEVDepth [35].
3D Detection and Tracking.
For the 3D object detec-
tion task, we follow CenterPoint [84] to predict the center
heatmap with anchor-free and multi-group head [90]. Af-
ter, we perform 3D tracking by tracking-by-detection using
velocity-based closest distance matching [84]. For train-
ing sparse aggregation setting, we filter LiDAR points out-
side of the 3D bounding box when obtaining a ground truth
depth map and replace the softmax to sigmoid in Eq. 3;
thereby, only feature grids containing foreground objects
can have a high probability.
BEV Segmentation.
For the BEV segmentation task, we
attach a convolutional decoder head to obtain the prediction
map following CVT [87]. Given a BEV feature map from
Multi-modal Feature Aggregation (MFA) layers, the seg-
mentation head encodes to a latent representation and de-
codes back to the final output segmentation map, followed
by a sigmoid layer. Our BEV segmentation network pre-
dicts a semantic occupancy grid of vehicles and drivable
area, trained with a focal loss [40].
4. Experiments
4.1. Experimental Settings
Dataset and Metrics.
We conduct experiments on
nuScenes [2], which provides radar point clouds at scale.
For 3D object detection and tracking, we use official met-
rics: mAP [13], NDS [2], and AMOTA [80], and we follow
the settings proposed by LSS [55] for BEV segmentation.
We refer the reader to nuScenes [2] and LSS [55] for details
of metrics.
Implementation Details.
For the camera stream, we
adopt BEVDepth [35] as a baseline with several modifi-
cations. We reduce the number of depth estimation layers
and eliminate the depth refinement module, which increases
the inference speed without a significant performance drop.
For radar, we accumulate six previous radar sweeps and use
normalized RCS and Doppler speed as features following
GRIF Net [26]. Unless otherwise specified, we follow stan-
dard practices [35] for implementation and training details.
We accumulate previous three BEV feature maps with an
interval of 1 second, similar to BEVFormer [36].
Our models are trained for 24 epochs with AdamW [47]
optimizer in an end-to-end manner, unless otherwise speci-
fied. In addition to image and BEV data augmentation [35],
we randomly drop sweeps and points for radar [30]. Infer-
ence time is measured on an Intel Core i9 CPU and RTX
3090 GPU with a single batch and FP16 precision. The full
experimental settings are provided in Appendix.


## Page 6

Method
Input
Backbone
Image Size
NDS↑
mAP↑
mATE↓
mASE↓
mAOE↓
mAVE↓
mAAE↓
FPS
CenterPoint-P†∗[84]
L
Pillars
-
59.8
49.4
0.320
0.262
0.377
0.334
0.198
-
CenterPoint-V†∗[84]
L
Voxel
-
65.3
56.9
0.285
0.253
0.323
0.272
0.186
-
BEVDet† [22]
C
R50
256 × 704
39.2
31.2
0.691
0.272
0.523
0.909
0.247
15.6
CenterFusion† [51]
C+R
DLA34
448 × 800
45.3
33.2
0.649
0.263
0.535
0.540
0.142
-
BEVDepth† [35]
C
R50
256 × 704
47.5
35.1
0.639
0.267
0.479
0.428
0.198
11.6
RCBEV4d† [88]
C+R
Swin-T
256 × 704
49.7
38.1
0.526
0.272
0.445
0.465
0.185
-
CRAFT† [27]
C+R
DLA34
448 × 800
51.7
41.1
0.494
0.276
0.454
0.486
0.176
4.1
SOLOFusion† [54]
C
R50
256 × 704
53.4
42.7
0.567
0.274
0.411
0.252
0.188
11.4
CRN
C+R
R18
256 × 704
54.3
44.8
0.518
0.283
0.552
0.279
0.180
27.9
CRN
C+R
R50
256 × 704
56.0
49.0
0.487
0.277
0.542
0.344
0.197
20.4
PETR† [43]
C
R101
900 × 1600
44.2
37.0
0.711
0.267
0.383
0.865
0.201
1.7
MVFusion† [82]
C+R
R101
900 × 1600
45.5
38.0
0.675
0.258
0.372
0.833
0.196
-
BEVFormer [36]
C
R101
900 × 1600
51.7
41.6
0.673
0.274
0.372
0.394
0.198
1.7
BEVDepth† [35]
C
R101
512 × 1408
53.5
41.2
0.565
0.266
0.358
0.331
0.190
5.0
SOLOFusion [54]
C
R101
512 × 1408
54.4
47.2
0.518
0.275
0.604
0.310
0.210
-
SOLOFusion† [54]
C
R101
512 × 1408
58.2
48.3
0.503
0.264
0.381
0.246
0.207
-
CRN
C+R
R101
512 × 1408
59.2
52.5
0.460
0.273
0.443
0.352
0.180
7.2
CRN‡
C+R
R101
512 × 1408
60.7
54.5
0.445
0.268
0.425
0.332
0.180
-
Table 1. 3D Object Detection on nuScenes val set. ‘L’, ‘C’, and ‘R’ represent LiDAR, camera, and radar, respectively. ∗: results from
MMDetection3D [4]. †: trained with CBGS. ‡: use test time augmentation.
Method
Input
Backbone
NDS↑
mAP↑
mATE↓
PointPillars [29]
L
Pillars
55.0
40.1
0.392
CenterPoint [84]
L
Voxel
67.3
60.3
0.262
KPConvPillars [75]
R
Pillars
13.9
4.9
0.823
CenterFusion [51]
C+R
DLA34
44.9
32.6
0.631
RCBEV [88]
C+R
Swin-T
48.6
40.6
0.484
PETR [43]
C
V2-99
50.4
44.1
0.593
MVFusion [82]
C+R
V2-99
51.7
45.3
0.569
CRAFT [27]
C+R
DLA34
52.3
41.1
0.467
BEVFormer [36]
C
V2-99
56.9
48.1
0.582
BEVDepth [35]
C
ConvNeXt-B
60.9
52.0
0.445
BEVStereo [33]
C
V2-99
61.0
52.5
0.431
SOLOFusion [54]
C
ConvNeXt-B
61.9
54.0
0.453
CRN
C+R
ConvNeXt-B
62.4
57.5
0.416
Table 2. 3D Object Detection on nuScenes test set. V2-99 is
pre-trained on external depth dataset DDAD [16].
4.2. Main Results
3D Object Detection.
For a fair comparison with previous
state-of-the-art 3D detection methods, we train our model
only on 3D detection task and report val and test set re-
sults in Tables 1 and 2. Under various input image sizes
and backbone settings, our CRN ranks first place among all
camera-only and camera-radar methods with much faster
FPS (Sec. 4.4 for inference time analysis). We empha-
size that CRN with a small image input and backbone
(256 × 704 and R18) already outperforms competitors with
a large image input and backbone (BEVFormer [36] and
BEVDepth [35] with 512×1408 and R101) in terms of mAP
while running an order of magnitude faster, showing the ef-
fectiveness of using radar over camera-only methods. CRN
also outperforms the LiDAR method CenterPoint-P [84],
demonstrating the potential of cost-effective camera and
radar to replace LiDAR for autonomous driving. Qualita-
tive results are provided in Fig. 5 and Appendix.
Method
Input
AMOTA↑AMOTP↓
FP↓
FN↓
IDS↓
CenterPoint [84]
L
63.8
0.555
18612 22928
760
DEFT [3]
C
17.7
1.564
22163 60565 6901
QD-3DT [20]
C
21.7
1.550
16495 60156 6856
CC-3DT [14]
C
41.0
1.274
18114 42910 3334
Sparse4D [41]
C
51.9
1.078
19626 32954 1090
CRN
C+R
56.9
0.809
16822 41093
946
Table 3. 3D Object Tracking on nuScenes test set.
Method
Input Backbone Image Size
Veh. D.A. FPS
LSS [55]
C
EffNetB0
128 × 352
32.1 72.0
25
FIERY [19]
C
EffNetB4
224 × 480
35.8
-
8
CVT [87]
C
EffNetB4
224 × 448
36.0 74.3
35
GKT [5]
C
EffNetB4
224 × 448
38.0
-
45.6
BEVFormer [36]
C
R101
900 × 1600
46.7 77.5
1.7
Simple-BEV [17]
C
R101
448 × 800
47.4
-
-
Simple-BEV [17] C+R
R101
448 × 800
55.7
-
7.3
CRN
C+R
R50
256 × 704
58.8 82.1 24.8
Table 4. BEV Segmentation on nuScenes val set.
3D Object Tracking and BEV Segmentation.
We fur-
ther demonstrate the generalization performance of CRN on
3D object tracking and BEV segmentation tasks. As shown
in Table 3, our tracking result outperforms all published
camera-only methods on nuScenes test set. Also, ours
not only significantly improves AMOTA but also reduces
AMOTP and identity switches.
CRN consistently achieves state-of-the-art performance
on BEV segmentation task as shown in Table 4. When com-
pared to previous segmentation methods with a small im-
age input and backbone [87, 5], ours performs significantly
better while maintaining a real-time inference speed thanks
to our semantically rich and spatially accurate BEV feature
map from camera and radar. CRN also achieves higher per-
formance at a much faster FPS than a large image input and
backbone [36], demonstrating the effectiveness of fusion.


## Page 7

Input
RVT
All
Car
NDS
mAP
mATE
mAP
Depth
✗
43.9
33.2
0.716
50.4
Radar
✗
33.6
24.3
0.706
44.7
Depth+Radar
✓
52.1
44.8
0.521
70.5
Depth+LiDAR
✓
57.0
51.6
0.419
76.2
Table 5.
Ablation of view transformation methods. LiDAR and
radar are used only for transformation and not used for feature
aggregation.
Input
All
Car
NDS
mAP
mATE
mAP
CenterPoint
L
52.8
41.2
0.406
73.9
BEVDepth
C
43.9
33.2
0.716
50.4
BEVFusion
C+R
51.9
42.4
0.536
68.4
+ deeper conv
C+R
51.9
42.8
0.532
69.0
+ RVT
C+R
52.7
44.3
0.517
70.6
MFA
C+R
53.4
44.5
0.507
70.3
+ RVT
C+R
53.9
45.2
0.501
71.6
Table 6. Ablation of feature aggregation methods. Note that MFA
with RVT is our full model.
4.3. Ablation Studies
We conduct ablation studies on val set with a 3D de-
tection task. Unless otherwise specified, models use two
frames of 256 × 704 image, R50 backbone, and are trained
for 24 epochs without CBGS [90].
For thorough com-
parison, we additionally build three baseline detectors for
camera – BEVDepth [35], point – CenterPoint [84], and
camera-point – BEVFusion [45]. Details of baselines and
additional ablation studies are provided in Appendix.
View Transformation.
In Table 5, we study how the
radar-assisted feature transformation affects performance.
View transformation solely relying on estimated depth suf-
fers from inaccurate localization due to the inherent low ac-
curacy of depth distribution. If we naively replace depth
distribution to radar (1 if radar point exists inside the voxel,
0 else), performance is severely degraded. This is because
image features in perspective view cannot be properly trans-
formed due to the ambiguity and sparsity of radar. With
the proposed RVT, the model can benefit from both dense
depth and sparse range measurement to significantly im-
prove performance (+8.2% NDS, +11.6% mAP) over depth-
only transformation. Moreover, we find consistent perfor-
mance improvement on LiDAR input, showing the effec-
tiveness of RVT.
Feature Aggregation.
Table 6 shows the comparison
between different feature aggregation methods.
BEVFu-
sion [45] fuses multi-modal feature maps in BEV using a
single convolutional layer, which is not adaptive and has a
small receptive field (3 × 3). Simply adding two additional
convolutional layers for fusion, which provides a larger re-
ceptive field (7 × 7) and bigger capacity, does not improve
the performance much. On the other hand, using only MFA
Input
Car mAP
FPS
[0,100)
[0,30)
[30,60)
[60,100)
CenterPoint
L
54.2
84.3
35.8
4.8
6.3
BEVDepth
C
34.1
65.4
13.7
0.2
13.0
CenterPoint
R
20.3
36.6
11.6
2.9
30.7
CRN
C+R
56.9
82.6
42.6
7.0
11.5
CRN-S
C+R
54.0
79.2
39.8
6.2
14.0
Table 7.
Analysis over various perception ranges. Suffix -S de-
notes sparse aggregation, and we use 256 × 704 and R50 for all
camera streams.
Input
Drop
# of view drops
0
1
3
6
BEVDepth
C
C
49.4
41.1
24.2
0
CenterPoint
R
R
30.6
25.3
14.9
0
BEVFusion
C+R
C
63.9
58.5
45.7
14.3
R
59.9
50.9
34.4
CRN
C+R
C
68.8
(+4.9)
62.4(+3.9) 48.9(+3.2)
12.8(-1.5)
R
64.3(+4.4) 57.0(+6.1) 43.8(+9.4)
Table 8.
Analysis of robustness using Car class mAP. Six view
drops denote the single modality is entirely off.
already outperforms deeper BEVFusion with RVT, showing
the effectiveness of the proposed multi-modal deformable
cross attention. We find that the performance gain of RVT
is less significant on MFA than BEVFusion since MFA is
already capable of handling spatial misalignment between
multi-modal features.
4.4. Analysis
Scaling Up Perception Range.
In Table 7, we extend
the perception range from 51.2m to 102.4m and also in-
crease the evaluation range twice correspondingly (see Ap-
pendix for details). Although CenterPoint [84] uses 10 Li-
DAR sweeps, points become extremely sparse as the range
increases, and thus performance is significantly degraded at
far distances. On the other hand, CRN outperforms LiDAR
especially at farther than 30m range with a much faster FPS,
showing the effectiveness of camera and radar for long-
range perception. Moreover, CRN with sparse aggregation
further improves the inference speed while preserving com-
parable performance.
Robustness.
To systematically analyze the robustness of
sensor failure cases, we randomly drop image and radar
inputs in Table 8.
For fair comparisons, we use single
frame input and fix the seed to ensure the same views can
be dropped over experiments. We also train both fusion
methods with data-level augmentation [6]. CRN not only
outperforms BEVFusion when all modalities are available
but maintains higher mAP on sensor failure cases. Consid-
ering that ours uses radar points at multiple stages (RVT
and MFA), each proposed module is trained to be robust to
sparse and ambiguous radar points. Especially when radar
input is entirely unavailable, BEVFusion suffers from a per-
formance drop over BEVDepth (-15.0%), while CRN still


## Page 8

Figure 5. Qualitative results of long-range model on various weather conditions. Images on the top are the six camera views surrounding
the vehicle. Green boxes are ground truths, blue boxes are our prediction results, and black dots are radar points. Perception ranges are set
to 200m × 200m, and ground truth maps on the background are used for visualization. Best viewed in color with zoom in.
Input
Sunny
Rainy
Day
Night
CenterPoint [84]
L
62.9
59.2
62.8
35.4
RCBEV [88]
C+R
36.1
38.5
37.1
15.5
BEVDepth [35]
C
39.0
39.0
39.3
16.8
CRN
C+R
54.8(+15.8) 57.0(+18.0) 55.1(+15.8) 30.4(+13.6)
Table 9.
Analysis of different lighting and weather conditions
using mAP metric.
CenterPoint [84] results are from BEVFu-
sion [45], and BEVDepth results are reproduced by us.
keeps the competitive performance (-5.6%). This advan-
tage comes from our attention module, which can adap-
tively choose modalities to use.
Weather and Lighting.
We analyze the performance un-
der different weather and lightning conditions in Table 9.
Note that R101 backbone with 512 × 1408 input is used for
BEVDepth and ours for comparable comparisons with Li-
DAR methods. Sensor noises of LiDAR in rainy conditions
or poor illumination of camera at night make object detec-
tion challenging for LiDAR-only or camera-only methods.
Thanks to fusion with radar, ours shows consistent perfor-
mance improvement of more than 10 mAP over the camera-
only method, demonstrating the effectiveness and robust-
ness of camera and radar sensors in all weather conditions.
Inference Time.
We analyze the inference time of each
proposed component in Fig. 6. In all analyses, we assume
that the BEV feature map of the previous frame T −1 can
be stored and accessed at the current frame T since ours
does not use temporal information (e.g., temporal stereo
methods [33, 54]) when obtaining the BEV feature map. It
means that using a multi-frame only increases the latency of
the BEV head. Ours requires negligible additional compu-
tation for point encoder and fusion modules, but the perfor-
43.5
50.5
22.7
23.6
9.3
7.6
6.7
4.1
6.6
6.7
7.9
10.5
7.9
10.5
0
20
40
60
80
C R N
B E V D E P
C R N
B E V D E P
Image Enc. 
Radar Enc. 
RVT 
MFA 
BEV Head
BEVDepth
384x1056, R50
CRN
384x1056, R50
CRN
256x704, R50
BEVDepth
256x704, R50
FPS / NDS
29.3 / 43.6
20.4 / 56.0
16.4 / 48.4
13.5 / 57.9
Latency [ms]
Figure 6.
Inference time analysis of proposed components. All
latency numbers are measured with batch size 1, GPU warm-up,
and FP16 precision.
mance gain over additional latency is substantial (+14.9ms
for +12.4 NDS in 256x704 and R50 setting). Moreover,
ours with small input can outperform camera-only with
larger input in terms of both latency and performance. We
expect that inference optimization methods (e.g., TensorRT)
can further reduce the latency of large model for long per-
ception range setting to match the real-time.
5. Conclusion
We present CRN, a novel camera-radar fusion method
for accurate, robust, and efficient multi-task 3D percep-
tion. Our method effectively overcomes the limitation of
each modality and fuses multi-modal information to gener-
ate contextually rich and spatially accurate BEV scene rep-
resentation. CRN is also suitable for long-range percep-
tion in real-time and achieves state-of-the-art performance
on various tasks. We hope that CRN will inspire future re-
search on camera-radar fusion for 3D perception.


## Page 9

Acknowledgment
This work was supported by Institute of Informa-
tion & communications Technology Planning & Evalu-
ation (IITP) and the National Research Foundation of
Korea (NRF) grant funded by the Korea government
(MSIT) (RS-2023-00236245,
Development of Percep-
tion/Planning AI SW for Seamless Autonomous Driv-
ing in Adverse Weather/Unstructured Environment and
2022R1A2C200494412)
References
[1] Xuyang Bai, Zeyu Hu, Xinge Zhu, Qingqiu Huang, Yilun
Chen, Hongbo Fu, and Chiew-Lan Tai. Transfusion: Robust
lidar-camera fusion for 3d object detection with transform-
ers. In Proceedings of the IEEE/CVF Conference on Com-
puter Vision and Pattern Recognition (CVPR), pages 1090–
1099, 2022. 3
[2] Holger Caesar, Varun Bankiti, Alex H. Lang, Sourabh Vora,
Venice Erin Liong, Qiang Xu, Anush Krishnan, Yu Pan, Gi-
ancarlo Baldan, and Oscar Beijbom.
nuscenes: A multi-
modal dataset for autonomous driving. In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition (CVPR), pages 11621–11631, 2020. 1, 2, 3, 5,
14
[3] Mohamed Chaabane, Peter Zhang, J Ross Beveridge, and
Stephen O’Hara. Deft: Detection embeddings for tracking.
In Proceedings of the IEEE/CVF Conference on Computer
Vision and Pattern Recognition Workshops (CVPRW), 2021.
6
[4] Kai Chen, Jiaqi Wang, Jiangmiao Pang, Yuhang Cao, Yu
Xiong, Xiaoxiao Li, Shuyang Sun, Wansen Feng, Ziwei Liu,
Jiarui Xu, et al. Mmdetection: Open mmlab detection tool-
box and benchmark. arXiv preprint arXiv:1906.07155, 2019.
6
[5] Shaoyu Chen, Tianheng Cheng, Xinggang Wang, Wenming
Meng, Qian Zhang, and Wenyu Liu. Efficient and robust
2d-to-bev representation learning via geometry-guided ker-
nel transformer. arXiv preprint arXiv:2206.04584, 2022. 6,
13
[6] Zehui Chen, Zhenyu Li, Shiquan Zhang, Liangji Fang, Qin-
hong Jiang, and Feng Zhao. Autoalignv2: Deformable fea-
ture aggregation for dynamic multi-modal 3d object detec-
tion. In Proceedings of the European Conference on Com-
puter Vision (ECCV), pages 628–644, 2022. 3, 7, 14
[7] Hyunggi Cho, Young-Woo Seo, BVK Vijaya Kumar, and Ra-
gunathan Raj Rajkumar. A multi-sensor fusion system for
moving object detection and tracking in urban driving envi-
ronments. In Proceedings of the IEEE International Confer-
ence on Robotics and Automation (ICRA), pages 1836–1843,
2014. 2
[8] Continental. Continental ARS 408-21 Datasheet. https:
//conti-engineering.com/components/
ars-408/. Accessed: 2023-03-01. 1, 3
[9] MMCV
Contributors.
MMCV:
OpenMMLab
com-
puter vision foundation.
https://github.com/
open-mmlab/mmcv, 2018. 13
[10] Jia Deng, Wei Dong, Richard Socher, Li-Jia Li, Kai Li,
and Li Fei-Fei.
Imagenet: A large-scale hierarchical im-
age database. In Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition (CVPR), pages
248–255, 2009. 13
[11] Hao Dong, Xianjing Zhang, Xuan Jiang, Jun Zhang, Jin-
tao Xu, Rui Ai, Weihao Gu, Huimin Lu, Juho Kannala, and
Xieyuanli Chen. Superfusion: Multilevel lidar-camera fu-
sion for long-range hd map generation and prediction. arXiv
preprint arXiv:2211.15656, 2022. 3
[12] Florian Drews, Di Feng, Florian Faion, Lars Rosenbaum,
Michael Ulrich, and Claudius Gl¨aser.
Deepfusion: A ro-
bust and modular 3d object detector for lidars, cameras and
radars. In Proceedings of the IEEE/RSJ International Con-
ference on Intelligent Robots and Systems (IROS), pages
560–567, 2022. 3
[13] Mark Everingham, Luc Van Gool, Christopher KI Williams,
John Winn, and Andrew Zisserman. The pascal visual object
classes (voc) challenge. International Journal of Computer
Vision (Int. J. Comput. Vis.), 88(2):303–338, 2010. 5
[14] Tobias Fischer, Yung-Hsu Yang, Suryansh Kumar, Min Sun,
and Fisher Yu. Cc-3dt: Panoramic 3d object tracking via
cross-camera fusion. In Proceedings of the Conference on
Robot Learning (CoRL), pages 2294–2305, 2023. 6
[15] Daniel G¨ohring, Miao Wang, Michael Schn¨urmacher, and
Tinosch Ganjineh.
Radar/lidar sensor fusion for car-
following on highways. In Proceedings of the IEEE Interna-
tional Conference on Automation, Robotics and Applications
(ICARA), pages 407–412, 2011. 2
[16] Vitor Guizilini, Rares Ambrus, Sudeep Pillai, Allan Raven-
tos, and Adrien Gaidon.
3D Packing for Self-Supervised
Monocular Depth Estimation.
In Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern
Recognition (CVPR), pages 2485–2494, 2020. 2, 6
[17] Adam W Harley, Zhaoyuan Fang, Jie Li, Rares Ambrus, and
Katerina Fragkiadaki. Simple-bev: What really matters for
multi-sensor bev perception? In Proceedings of the IEEE In-
ternational Conference on Robotics and Automation (ICRA),
pages 2759–2765, 2023. 6
[18] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun.
Deep residual learning for image recognition. In Proceed-
ings of the IEEE/CVF Conference on Computer Vision and
Pattern Recognition (CVPR), pages 770–778, 2016. 4, 13
[19] Anthony Hu, Zak Murez, Nikhil Mohan, Sof´ıa Dudas, Jef-
frey Hawke, Vijay Badrinarayanan, Roberto Cipolla, and
Alex Kendall. Fiery: Future instance prediction in bird’s-eye
view from surround monocular cameras. In Proceedings of
the IEEE/CVF International Conference on Computer Vision
(ICCV), pages 15273–15282, 2021. 1, 6, 13
[20] Hou-Ning Hu, Yung-Hsu Yang, Tobias Fischer, Trevor Dar-
rell, Fisher Yu, and Min Sun.
Monocular quasi-dense 3d
object tracking. IEEE Transactions on Pattern Analysis and
Machine Intelligence (IEEE Trans. Pattern Anal. Mach. In-
tell.), 45(2):1992–2008, 2022. 6
[21] Gao Huang, Yu Sun, Zhuang Liu, Daniel Sedra, and Kilian Q
Weinberger. Deep networks with stochastic depth. In Pro-
ceedings of the European Conference on Computer Vision
(ECCV), pages 646–661, 2016. 14


## Page 10

[22] Junjie Huang, Guan Huang, Zheng Zhu, and Dalong Du.
Bevdet: High-performance multi-camera 3d object detection
in bird-eye-view. In arXiv preprint arXiv:2112.11790, 2021.
1, 6, 13, 14
[23] Yanqin Jiang, Li Zhang, Zhenwei Miao, Xiatian Zhu, Jin
Gao, Weiming Hu, and Yu-Gang Jiang. Polarformer: Multi-
camera 3d object detection with polar transformers. In Pro-
ceedings of the AAAI Conference on Artificial Intelligence
(AAAI), 2023. 2
[24] Don H Johnson and Dan E Dudgeon. Array signal process-
ing: concepts and techniques. Simon & Schuster, Inc., 1992.
3
[25] Jinhyeong Kim, Youngseok Kim, and Dongsuk Kum. Low-
level sensor fusion network for 3d vehicle detection using
radar range-azimuth heatmap and monocular image.
In
Proceedings of the Asian Conference on Computer Vision
(ACCV), pages 388–402, 2020. 3
[26] Youngseok Kim, Jun Won Choi, and Dongsuk Kum. GRIF
Net: Gated region of interest fusion network for robust 3D
object detection from radar point cloud and monocular im-
age.
In Proceedings of the IEEE/RSJ International Con-
ference on Intelligent Robots and Systems (IROS), pages
10857–10864, 2020. 2, 3, 5
[27] Youngseok Kim, Sanmin Kim, Jun Won Choi, and Dong-
suk Kum. CRAFT: Camera-Radar 3D Object Detection with
Spatio-Contextual Fusion Transformer. In Proceedings of the
AAAI Conference on Artificial Intelligence (AAAI), 2023. 2,
3, 6, 14, 15
[28] Jason Ku, Melissa Mozifian, Jungwook Lee, Ali Harakeh,
and Steven L Waslander. Joint 3d proposal generation and
object detection from view aggregation. In Proceedings of
the IEEE/RSJ International Conference on Intelligent Robots
and Systems (IROS), pages 5750–5757, 2018. 3
[29] Alex H Lang, Sourabh Vora, Holger Caesar, Lubing Zhou,
Jiong Yang, and Oscar Beijbom. Pointpillars: Fast encoders
for object detection from point clouds. In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition (CVPR), pages 12697–12705, 2019. 2, 4, 6, 14
[30] Zhaoqi Leng, Guowang Li, Chenxi Liu, Ekin Dogus Cubuk,
Pei Sun, Tong He, Dragomir Anguelov, and Mingxing Tan.
Lidaraugment: Searching for scalable 3d lidar data augmen-
tations. In Proceedings of the IEEE International Confer-
ence on Robotics and Automation (ICRA), pages 7039–7045,
2023. 5
[31] Jian Li and Petre Stoica. MIMO radar signal processing.
John Wiley & Sons, 2008. 3
[32] Qi Li, Yue Wang, Yilun Wang, and Hang Zhao. Hdmap-
net: An online hd map construction and evaluation frame-
work.
In Proceedings of the IEEE International Confer-
ence on Robotics and Automation (ICRA), pages 4628–4634,
2022. 2, 3
[33] Yinhao Li, Han Bao, Zheng Ge, Jinrong Yang, Jianjian Sun,
and Zeming Li.
Bevstereo: Enhancing depth estimation
in multi-view 3d object detection with dynamic temporal
stereo. In Proceedings of the AAAI Conference on Artificial
Intelligence (AAAI), 2023. 4, 6, 8, 15
[34] Yanwei Li, Yilun Chen, Xiaojuan Qi, Zeming Li, Jian Sun,
and Jiaya Jia.
Unifying voxel-based representation with
transformer for 3d object detection. In Advances in Neural
Information Processing Systems (NeurIPS), 2022. 3, 4
[35] Yinhao Li, Zheng Ge, Guanyi Yu, Jinrong Yang, Zengran
Wang, Yukang Shi, Jianjian Sun, and Zeming Li. Bevdepth:
Acquisition of reliable depth for multi-view 3d object detec-
tion. In Proceedings of the AAAI Conference on Artificial
Intelligence (AAAI), 2023. 2, 3, 4, 5, 6, 7, 8, 13, 14, 15
[36] Zhiqi Li, Wenhai Wang, Hongyang Li, Enze Xie, Chonghao
Sima, Tong Lu, Qiao Yu, and Jifeng Dai. Bevformer: Learn-
ing bird’s-eye-view representation from multi-camera im-
ages via spatiotemporal transformers. In Proceedings of the
European Conference on Computer Vision (ECCV), pages 1–
18, 2022. 2, 3, 5, 6, 15
[37] Tingting Liang, Hongwei Xie, Kaicheng Yu, Zhongyu Xia,
Zhiwei Lin, Yongtao Wang, Tao Tang, Bing Wang, and Zhi
Tang. Bevfusion: A simple and robust lidar-camera fusion
framework. In Advances in Neural Information Processing
Systems (NeurIPS), 2022. 3
[38] Juan-Ting Lin, Dengxin Dai, and Luc Van Gool. Depth es-
timation from monocular images and sparse radar data. In
Proceedings of the IEEE/RSJ International Conference on
Intelligent Robots and Systems (IROS), pages 10233–10240,
2020. 3
[39] Tsung-Yi Lin, Piotr Doll´ar, Ross Girshick, Kaiming He,
Bharath Hariharan, and Serge Belongie.
Feature pyra-
mid networks for object detection.
In Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern
Recognition (CVPR), pages 2117–2125, 2017. 4
[40] Tsung-yi Lin, Priya Goyal, Ross Girshick, Kaiming He, and
Piotr Dollar.
Focal Loss for Dense Object Detection.
In
Proceedings of the IEEE/CVF International Conference on
Computer Vision (ICCV), pages 2980–2988, 2017. 5
[41] Xuewu Lin, Tianwei Lin, Zixiang Pei, Lichao Huang, and
Zhizhong Su.
Sparse4d:
Multi-view 3d object detec-
tion with sparse spatial-temporal fusion.
arXiv preprint
arXiv:2211.10581, 2022. 6
[42] Yier Lin, Julien Le Kernec, Shufan Yang, Francesco Fio-
ranelli, Olivier Romain, and Zhiqin Zhao. Human activity
classification with radar: Optimization and noise robustness
with iterative convolutional neural networks followed with
random forests. IEEE Sensors Journal, 18(23):9669–9681,
2018. 3
[43] Yingfei Liu, Tiancai Wang, Xiangyu Zhang, and Jian Sun.
Petr: Position embedding transformation for multi-view 3d
object detection. In Proceedings of the European Conference
on Computer Vision (ECCV), pages 531––548, 2022. 6
[44] Zhuang Liu, Hanzi Mao, Chao-Yuan Wu, Christoph Feicht-
enhofer, Trevor Darrell, and Saining Xie. A convnet for the
2020s. In Proceedings of the IEEE/CVF Conference on Com-
puter Vision and Pattern Recognition (CVPR), pages 11976–
11986, 2022. 4, 13
[45] Zhijian Liu, Haotian Tang, Alexander Amini, Xinyu Yang,
Huizi Mao, Daniela Rus, and Song Han. Bevfusion: Multi-
task multi-sensor fusion with unified bird’s-eye view repre-
sentation. In Proceedings of the IEEE International Confer-
ence on Robotics and Automation (ICRA), 2023. 3, 4, 7, 8,
14


## Page 11

[46] Yunfei Long, Daniel Morris, Xiaoming Liu, Marcos Cas-
tro, Punarjay Chakravarty, and Praveen Narayanan. Radar-
camera pixel depth association for depth completion. In Pro-
ceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition (CVPR), pages 12507–12516, 2021.
3
[47] Ilya Loshchilov and Frank Hutter. Decoupled weight decay
regularization. In Proceedings of the International Confer-
ence on Learning Representations (ICLR), 2019. 5, 13
[48] Jiachen Lu, Zheyuan Zhou, Xiatian Zhu, Hang Xu, and Li
Zhang. Learning ego 3d representation as ray tracing. In
Proceedings of the European Conference on Computer Vi-
sion (ECCV), pages 129–144, 2022. 2
[49] Bence
Major,
Daniel
Fontijne,
Amin
Ansari,
Ravi
Teja Sukhavasi, Radhika Gowaikar, Michael Hamilton, Sean
Lee, Slawomir Grzechnik, and Sundar Subramanian.
Ve-
hicle detection with automotive radar using deep learning
on range-azimuth-doppler tensors.
In Proceedings of the
IEEE/CVF International Conference on Computer Vision
Workshops (ICCVW), pages 924–932, 2019. 3
[50] Michael Meyer and Georg Kuschk. Automotive radar dataset
for deep learning based 3d object detection. In Proceedings
of the European Radar Conference (EuRAD), pages 129–
132, 2019. 2, 3
[51] Ramin Nabati and Hairong Qi. Centerfusion: Center-based
radar and camera fusion for 3d object detection. In Proceed-
ings of the IEEE/CVF Winter Conference on Applications of
Computer Vision (WACV), pages 1527–1536, 2021. 2, 3, 6,
15
[52] Su Pang, Daniel Morris, and Hayder Radha. Clocs: Camera-
lidar object candidates fusion for 3d object detection.
In
Proceedings of the IEEE/RSJ International Conference on
Intelligent Robots and Systems (IROS), pages 10386–10393.
IEEE, 2020. 3
[53] Dennis Park, Rares Ambrus, Vitor Guizilini, Jie Li, and
Adrien Gaidon.
Is pseudo-lidar needed for monocular 3d
object detection? In Proceedings of the IEEE/CVF Interna-
tional Conference on Computer Vision (ICCV), pages 3142–
3152, 2021. 2
[54] Jinhyung Park, Chenfeng Xu, Shijia Yang, Kurt Keutzer,
Kris Kitani, Masayoshi Tomizuka, and Wei Zhan. Time will
tell: New outlooks and a baseline for temporal multi-view 3d
object detection. In Proceedings of the International Confer-
ence on Learning Representations (ICLR), 2023. 2, 6, 8, 15
[55] Jonah Philion and Sanja Fidler. Lift, splat, shoot: Encoding
images from arbitrary camera rigs by implicitly unprojecting
to 3d. In Proceedings of the European Conference on Com-
puter Vision (ECCV), pages 194–210, 2020. 1, 2, 3, 4, 5, 6,
13, 14
[56] Alexander Popov, Patrik Gebhardt, Ke Chen, Ryan Oldja,
Heeseok Lee, Shane Murray, Ruchi Bhargava, and Nikolai
Smolyanskiy. Nvradarnet: Real-time radar obstacle and free
space detection for autonomous driving. In Proceedings of
the IEEE International Conference on Robotics and Automa-
tion (ICRA), pages 6958–6964, 2023. 2
[57] Charles R Qi, Wei Liu, Chenxia Wu, Hao Su, and Leonidas J
Guibas. Frustum pointnets for 3d object detection from rgb-d
data. In Proceedings of the IEEE/CVF Conference on Com-
puter Vision and Pattern Recognition (CVPR), pages 918–
927, 2018. 3
[58] Charles R Qi, Hao Su, Kaichun Mo, and Leonidas J Guibas.
Pointnet: Deep learning on point sets for 3d classification
and segmentation. In Proceedings of the IEEE/CVF Confer-
ence on Computer Vision and Pattern Recognition (CVPR),
pages 652–660, 2017. 2
[59] Charles Ruizhongtai Qi, Li Yi, Hao Su, and Leonidas J
Guibas. Pointnet++: Deep hierarchical feature learning on
point sets in a metric space. In Advances in Neural Informa-
tion Processing Systems (NeurIPS), pages 5105–5114, 2017.
2, 4
[60] Cody Reading, Ali Harakeh, Julia Chae, and Steven L
Waslander.
Categorical depth distribution network for
monocular 3d object detection.
In Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern
Recognition (CVPR), pages 8555–8564, 2021. 1, 2, 3, 4
[61] Thomas Roddick and Roberto Cipolla. Predicting seman-
tic map representations from images using pyramid occu-
pancy networks. In Proceedings of the IEEE/CVF Confer-
ence on Computer Vision and Pattern Recognition (CVPR),
pages 11138–11147, 2020. 2, 3
[62] Byungseok Roh, JaeWoong Shin, Wuhyun Shin, and Sae-
hoon Kim. Sparse detr: Efficient end-to-end object detection
with learnable sparsity. In Proceedings of the International
Conference on Learning Representations (ICLR), 2022. 5
[63] Avishkar Saha, Oscar Mendez, Chris Russell, and Richard
Bowden. Translating images into maps. In Proceedings of
the IEEE International Conference on Robotics and Automa-
tion (ICRA), pages 9200–9206, 2022. 2
[64] Shaoshuai Shi, Chaoxu Guo, Li Jiang, Zhe Wang, Jianping
Shi, Xiaogang Wang, and Hongsheng Li. PV-RCNN: Point-
Voxel Feature Set Abstraction for 3D Object Detection. In
Proceedings of the IEEE/CVF Conference on Computer Vi-
sion and Pattern Recognition (CVPR), pages 10529–10538,
2020. 2
[65] Shaoshuai Shi, Xiaogang Wang, and Hongsheng Li. Pointr-
cnn: 3d object proposal generation and detection from point
cloud. In Proceedings of the IEEE/CVF Conference on Com-
puter Vision and Pattern Recognition (CVPR), pages 770–
779, 2019. 2
[66] Weijing Shi and Raj Rajkumar. Point-gnn: Graph neural net-
work for 3d object detection in a point cloud. In Proceedings
of the IEEE/CVF Conference on Computer Vision and Pat-
tern Recognition (CVPR), pages 1711–1719, 2020. 2
[67] Juyeb Shin,
Francois Rameau,
Hyeonjun Jeong,
and
Dongsuk Kum.
InstaGraM: Instance-level Graph Mod-
eling for Vectorized HD Map Learning.
arXiv preprint
arXiv:2301.04470, 2023. 1
[68] Andrea Simonelli, Samuel Rota Rota Bul`o, Lorenzo Porzi,
Manuel L´opez-Antequera, and Peter Kontschieder. Disen-
tangling Monocular 3D Object Detection. In Proceedings of
the IEEE/CVF International Conference on Computer Vision
(ICCV), pages 1991–1999, 2019. 2
[69] Liat Sless, Bat El Shlomo, Gilad Cohen, and Shaul Oron.
Road scene understanding by occupancy grid learning from


## Page 12

sparse radar clusters using semantic segmentation. In Pro-
ceedings of the IEEE/CVF International Conference on
Computer Vision Workshops (ICCVW), 2019. 2
[70] Pei Sun, Weiyue Wang, Yuning Chai, Gamaleldin El-
sayed, Alex Bewley, Xiao Zhang, Cristian Sminchisescu,
and Dragomir Anguelov.
Rsn: Range sparse net for effi-
cient, accurate lidar 3d object detection. In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition (CVPR), pages 5725–5734, 2021. 2
[71] Peter Svenningsson, Francesco Fioranelli, and Alexander
Yarovoy. Radar-pointgnn: Graph based object recognition
for unstructured radar point-cloud data. In Proceedings of
the IEEE Radar Conference (RadarConf), pages 1–6, 2021.
2
[72] Hugues Thomas, Charles R Qi, Jean-Emmanuel Deschaud,
Beatriz Marcotegui, Franc¸ois Goulette, and Leonidas J
Guibas. Kpconv: Flexible and deformable convolution for
point clouds. In Proceedings of the IEEE/CVF International
Conference on Computer Vision (ICCV), pages 6411–6420,
2019. 2
[73] Zhi Tian, Chunhua Shen, Hao Chen, and Tong He. Fcos:
Fully convolutional one-stage object detection. In Proceed-
ings of the IEEE/CVF International Conference on Com-
puter Vision (ICCV), pages 9627–9636, 2019. 2
[74] Hugo Touvron, Matthieu Cord, Alexandre Sablayrolles,
Gabriel Synnaeve, and Herv´e J´egou. Going deeper with im-
age transformers. In Proceedings of the IEEE/CVF Interna-
tional Conference on Computer Vision (ICCV), pages 32–42,
2021. 14
[75] Michael Ulrich, Sascha Braun, Daniel K¨ohler, Daniel
Niederl¨ohner, Florian Faion, Claudius Gl¨aser, and Holger
Blume. Improved orientation estimation and detection with
hybrid object detection networks for automotive radar. In
Proceedings of the IEEE International Intelligent Trans-
portation Systems Conference (ITSC), pages 111–117, 2022.
2, 6
[76] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszko-
reit, Llion Jones, Aidan N Gomez, Łukasz Kaiser, and Illia
Polosukhin. Attention is all you need. In Advances in Neu-
ral Information Processing Systems (NeurIPS), pages 6000–
6010, 2017. 4, 13
[77] Sourabh Vora, Alex H Lang, Bassam Helou, and Oscar Bei-
jbom. Pointpainting: Sequential fusion for 3d object detec-
tion. In Proceedings of the IEEE/CVF Conference on Com-
puter Vision and Pattern Recognition (CVPR), pages 4604–
4612, 2020. 3
[78] Tai Wang, Xinge Zhu, Jiangmiao Pang, and Dahua Lin.
Fcos3d: Fully convolutional one-stage monocular 3d object
detection.
In Proceedings of the IEEE/CVF International
Conference on Computer Vision Workshops (ICCVW), pages
913–922, 2021. 2
[79] Yue Wang, Alireza Fathi, Abhijit Kundu, David A Ross,
Caroline Pantofaru, Tom Funkhouser, and Justin Solomon.
Pillar-based object detection for autonomous driving. In Pro-
ceedings of the European Conference on Computer Vision
(ECCV), pages 18–34, 2020. 2
[80] Xinshuo Weng and Kris Kitani.
A baseline for 3d multi-
object tracking. In arXiv preprint arXiv:1907.03961, 2019.
5
[81] Rob Weston, Sarah Cen, Paul Newman, and Ingmar Pos-
ner.
Probably unknown: Deep inverse sensor modelling
radar.
In Proceedings of the IEEE International Confer-
ence on Robotics and Automation (ICRA), pages 5446–5452,
2019. 2
[82] Zizhang Wu, Guilian Chen, Yuanzhu Gan, Lei Wang, and
Jian Pu.
Mvfusion: Multi-view 3d object detection with
semantic-aligned radar and camera fusion. In Proceedings
of the IEEE International Conference on Robotics and Au-
tomation (ICRA), 2023. 3, 6
[83] Yan Yan, Yuxing Mao, and Bo Li. Second: Sparsely em-
bedded convolutional detection. Sensors, 18(10):3337–3352,
2018. 4, 13, 14
[84] Tianwei Yin, Xingyi Zhou, and Philipp Krahenbuhl. Center-
based 3d object detection and tracking. In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition (CVPR), pages 11784–11793, 2021. 1, 3, 5, 6,
7, 8, 14, 15
[85] Jin Hyeok Yoo, Yecheol Kim, Jisong Kim, and Jun Won
Choi. 3d-cvf: Generating joint camera and lidar features us-
ing cross-view spatial feature fusion for 3d object detection.
In Proceedings of the European Conference on Computer Vi-
sion (ECCV), pages 720–736, 2020. 3
[86] Wenwei Zhang, Zhe Wang, and Chen Change Loy. Explor-
ing data augmentation for multi-modality 3d object detec-
tion. arXiv preprint arXiv:2012.12741, 2020. 14
[87] Brady Zhou and Philipp Kr¨ahenb¨uhl. Cross-view transform-
ers for real-time map-view semantic segmentation. In Pro-
ceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition (CVPR), pages 13760–13769, 2022.
1, 2, 3, 5, 6, 13
[88] Taohua Zhou, Junjie Chen, Yining Shi, Kun Jiang, Meng-
meng Yang, and Diange Yang. Bridging the view disparity
between radar and camera features for multi-modal fusion 3d
object detection. IEEE Transactions on Intelligent Vehicles
(IEEE Trans. Intell. Veh.), 2023. 3, 6, 8
[89] Xingyi Zhou, Dequan Wang, and Philipp Kr¨ahenb¨uhl. Ob-
jects as points. In arXiv preprint arXiv:1904.07850, 2019. 2,
15
[90] Benjin Zhu, Zhengkai Jiang, Xiangxin Zhou, Zeming Li,
and Gang Yu.
Class-balanced grouping and sampling
for point cloud 3d object detection.
In arXiv preprint
arXiv:1908.09492, 2019. 5, 7, 14
[91] Xizhou Zhu, Weijie Su, Lewei Lu, Bin Li, Xiaogang Wang,
and Jifeng Dai. Deformable detr: Deformable transformers
for end-to-end object detection. In Proceedings of the In-
ternational Conference on Learning Representations (ICLR),
2021. 4, 13


## Page 13

Appendix
A. Overview
This supplementary material provides additional details
of architecture, qualitative and quantitative experimental re-
sults.
We describe the notation of MDCA (Sec. B) and
implementation details for experiments in the main paper
(Sec. C). We further provide additional experimental results
(Sec. D) and qualitative results (Sec. E).
B. Multi-modal Deformable Cross Attention
We adopt the deformable attention [91] and extend it
for multi-modal feature maps, denoted as multi-modal de-
formable cross attention (MDCA).
Given an input queries zq and flattened multi-modal
BEV feature maps xm = {CBEV
I
, CBEV
R
∈RC×XY }, let
q index a query element and pq ∈[0, 1]2 be the normalized
coordinates of the reference point for each query element
q. The multi-modal deformable cross attention (MDCA) is
defined as
MDCA(zq, pq, xm) =
H
X
h
W h
" M
X
m
K
X
k
Ahmqk · W ′
hmxm(ϕm(pq + ∆phmqk))
#
.
(8)
h, m, k index the attention head H, multiple modalities
{CI, CR}, and the number of sampling points K. W h ∈
RC×Cv is the output projection matrix at hth head, and
W ′
hm ∈RCv×C is the input value projection matrix at hth
head and modality m. We use Cv = C/H following multi-
head attention in Transformers [76]. Note that separated
input value projection matrices W ′
hm are used for each
modality to make MDCA modality-specific and achieve ro-
bust fusion (e.g., sensor failure case).
Both Ahmqk and
∆phmqk are obtained by linear projection over the input
queries zq, and the attention weight Ahmqk is normalized
to modalities and sampling points as PM
m
PK
k Ahmqk = 1.
Function ϕm(pq) scales the normalized coordinates pq in
case two modalities have different shapes.
The proposed multi-modal deformable attention module
is designed to look over multi-modal feature maps and mul-
tiple sampling points. This can overcome spatial misalign-
ment around reference points and enable adaptive fusion
over modalities.
C. Implementation Details
This section provides the experimental settings for the
main results and ablation studies.
C.1. Pre-processing and Hyper-parameters
For the camera stream, the image backbone yields
4 levels of feature maps of stride 4, 8, 16, and 32,
and we employ SECONDFPN [83], which concatenates
output feature maps at stride 16.
nn.Conv2d and
nn.ConvTranspose2d are used for downsampling and
upsampling. Given FPN feature maps, the depth distribu-
tion network outputs D size depth bins. We use uniform
discretization with a depth range of [2.0, 58.0]m and bin
size of 0.5m, resulting in D = 112.
As stated in the main paper, we first project point cloud
into an image coordinate system while preserving its depth
and features for radar stream. Note that the projection ma-
trix for radar point projection corresponds to the image
stream. Next, we voxelize radar points in the frustum coor-
dinate system (d, u, v) to have the same size with an image
frustum feature. Taking into account the sparsity and accu-
racy of radar, we use 8× downsampled pillar canvas and fur-
ther extract pillar features using SECOND backbone, which
yields 3 levels of feature maps of stride of 1, 2, and 4. Fi-
nally, SECONDFPN is employed to pillar feature maps to
output 16× downsampled size in the image width direction
and to have D = 112 in a depth direction.
We use multi scale deform attn implementa-
tion from MMCV [9] for deformable cross attention in
Multi-modal Feature Aggregation (MFA). Specifically, we
use 6 layers of MFA, 8 attention heads, and 4 sampling
points for MFA in our experiments. MFA is applied to the
single-frame camera and radar inputs and produces a fused
BEV feature map. After, fused BEV feature maps from the
previous T timestamps are aligned to the current timestamp
and concatenated. We use T = 3 for the submission and
T = 1 for ablation studies and note that future frames are
not used.
Following standard practices in monocular 3D object de-
tection [22, 35], we set perception range [−51.2, 51.2]m
with a pillar size of (0.2, 0.2)m and a downsampling fac-
tor of 4. As a result, the size of the BEV feature map is
128 × 128.
For the BEV segmentation task, the perception range
is set to [−50.0, 50.0]m in both X−and Y −axis cen-
tered around the ego vehicle, following previous works
[55, 19, 87, 5]. The resolution of the final output is 0.5m,
resulting in 200 × 200 grid map.
C.2. Training Settings
All models are trained for 24 epochs with AdamW [47]
optimizer in an end-to-end manner. Image backbones are
pre-trained on ImageNet [10].
In Table 10, we provide
ResNet [18] and ConvNeXt [44] training settings used for
our main results.
For image and radar data augmentation (in perspective
view), we use resize, crop, and horizontal flipping augmen-


## Page 14

configs
ResNet-50/101
ConvNeXt-B
optimizer
AdamW
AdamW
base learning rate
2e-4
1e-4
backbone learning rate
2e-4/1e-4
5e-5
weight decay
1e-4
1e-2
optimizer momentum
β1, β2 = 0.9, 0.999
β1, β2 = 0.9, 0.999
batch size
64/32
16
training epochs
24
24
lr schedule
step decay
step decay
gradient clip
5
5
stochastic depth [21]
None
0.4
layer scale [74]
None
1.0
Table 10. Training settings for the main results.
tation following standard practices [22, 35]. We discard
rotation augmentation since the rotation can have an ad-
verse effect when collapsing the height dimension in radar-
assisted view transformation (RVT). Note that the same data
augmentation is applied to the image and radar in the per-
spective view.
For BEV augmentation, we use random flipping along
X and Y axis, global rotation between [−π/8, π/8], and
global scale between [0.95, 1.05]. BEV data augmentation
is applied to the BEV feature map and ground truth boxes
correspondingly. Note that ground-truth sampling augmen-
tation (GT-AUG) [83] is not used in our experiments, and
we leave GT-AUG for a multi-modal setting [6, 86] as fu-
ture work.
C.3. Baselines for Ablation Studies
We conduct three baselines BEVDepth [35], Center-
Point [84], and BEVFusion [45] for camera-only, point-
only, and camera-point fusion detectors. Note that Center-
Point and BEVFusion originally take LiDAR points as input
and we replace LiDAR points (x, y, z, intensity) to radar
points (x, y, z, RCS, Doppler) without network modifica-
tion.
For BEVDepth, we use the official code1 without class-
balanced grouping and sampling (CBGS) [90] and exponen-
tial moving average (EMA).
For CenterPoint, we use MMDetection2 implementation
using PointPillar [29] backbone with (0.2, 0.2, 8)m pillar
size. Different from the official implementation, CBGS [90]
and GT-AUG [83] are discarded for fair comparisons.
For BEVFusion, we use BEVDepth for obtaining the
camera BEV feature map and CenterPoint-Pillar for point
BEV feature maps and fuse them by a single 3 × 3 convolu-
tion layer following official implementation. Note that our
BEVFusion may yield better performance since our imple-
mentation uses BEVDepth for the camera stream, while the
original BEVFusion uses LSS [55].
1 https://github.com/Megvii-BaseDetection/BEVDepth
2 https://github.com/open-mmlab/mmdetection3d
C.4. Details of Long-Range Model
To analyze the performance of CRN over long per-
ception ranges, we increase the perception range of base-
lines to [−102.4, 102.4]m.
For camera streams, we in-
crease the range of depth distribution from [2.0, 58.0]m to
[2.0, 116.0]m, and the number of depth bins is doubled to
D = 224. For point streams, the range of point cloud and
pillars are increased to correspond to the perception range.
Note that we use the same pillar size (0.2, 0.2)m and down-
sampling factor of 4, resulting in a 256 × 256 BEV feature
map for all baselines.
For training and evaluating long-range models, we in-
crease the ‘class range’ in nuScenes [2] twice to filter the
ground truth and predictions. Particularly, the class range of
car, truck, bus, trailer, and construction vehicle are 100m,
pedestrian, motorcycle, and bicycle are 80m, traffic cone
and barrier are 60m. Moreover, nuScenes filters annotation
that does not contain at least single LiDAR or radar point
inside the 3D bounding box (denote as ‘points in box fil-
tering’) for training and evaluation, but we disable this fil-
tering for thorough analysis. Thus, some moving objects
are visible on the image but do not have annotations (due
to not enough points to label), and some static objects can
have annotations but are not visible on the image (labeled on
the previous timestamp but occluded on the current times-
tamp) in our setting. Although disabling point filtering may
cause inconsistency between input data and annotation and
harms performance during training, all methods are trained
and evaluated using the same setting for a fair comparison.
We find that the inference speed of CenterPoint [84] with
radar input is much faster than LiDAR input, assuming that
the sparsity of radar points can highly benefit from voxeliza-
tion and sparse convolution [83].
D. Additional Experimental Results
D.1. Per-Class Analysis
In Table 11, we compare the performance improvement
of camera-radar methods over camera-only baselines. For
fair comparisons, we report 256 × 704 and R50 mod-
els for BEVDepth and CRN. Corresponds to results on
CRAFT [27], metallic and frequently appeared on road
classes (car, truck, bus, and motorcycle) gain significant
improvements. Different from CRAFT, ours also shows a
huge improvement in non-metallic classes (pedestrian, bi-
cycle, traffic cone, and barrier). Moreover, we find that the
performance gain of using radar is much more significant
on ours than other fusion methods. Considering the per-
formance difference of camera baselines are not significant,
results in Table 11 demonstrate that the design of fusion
methods greatly affects the performance.


## Page 15

Method
Input
Car
Truck
Bus
Trailer
C.V.
Ped.
M.C.
Bicycle
T.C.
Barrier
mAP
CenterPoint-P [84]
L
83.9
49.5
61.9
34.1
12.3
76.9
44.1
18.0
54.0
59.1
49.4
CenterNet [89]
C
48.4
23.1
34.0
13.1
3.5
37.7
24.9
23.4
55.0
45.6
30.6
CenterFusion [51]
C+R
52.4(+4.0)
26.5(+3.4)
36.2(+2.2) 15.4(+2.3)
5.5(+2.0)
38.9(+1.2)
30.5(+5.6)
22.9(-0.5)
56.3(+1.3) 47.0(+1.4)
33.2(+2.6)
CRAFT-I [27]
C
52.4
25.7
30.0
15.8
5.4
39.3
28.6
29.8
57.5
47.8
33.2
CRAFT [27]
C+R
69.6(+17.2) 37.6(+11.9) 47.3(+17.3) 20.1(+4.3) 10.7(+5.3) 46.2(+6.9) 39.5(+10.9) 31.0(+1.2)
57.1(-0.4) 51.1(+3.3)
41.1(+7.9)
BEVDepth [35]
C
55.3
25.2
37.8
16.3
7.6
36.1
31.9
28.6
53.6
55.9
34.8
CRN
C+R
73.6(+18.3) 44.5(+19.3) 55.6(+17.8) 22.0(+5.7) 15.4(+7.8) 50.2(+14.1) 54.7(+22.8) 48.9(+20.3) 61.4(+7.8) 63.8(+7.9) 49.0(+14.2)
Table 11.
Per-class comparisons on nuScenes val set. ‘C.V.’, ‘Ped.’, ‘M.C.’, and ‘T.C.’ denote construction vehicle, pedestrian, mo-
torcycle, and traffic cone, respectively. CenterNet [89], CRAFT-I [27], and BEVDepth [35] are camera baselines of CenterFusion [51],
CRAFT [27], and CRN. CenterPoint-P and BEVDepth results are from MMDetection3D and the official code.
# Frames
NDS
mAP
mATE
mAOE
mAVE
1
50.3
42.9
0.519
0.577
0.520
2
54.5
46.0
0.495
0.538
0.350
3
55.7
47.3
0.480
0.507
0.342
4
56.0
48.1
0.474
0.541
0.328
5
56.4
48.4
0.469
0.515
0.345
Table 12. Ablation of temporal frames.
D.2. Design Decisions
We study architecture designs that affect the perfor-
mance of CRN to provide insights on the proposed sensor
fusion framework.
Temporal Frames.
We accumulate multiple BEV feature
maps on channel dimension by concatenation and aggregate
them by a few convolutional layers before feeding them to
the BEV backbone. We find that the time interval of 1 sec-
ond yields a better performance than 0.5 second proposed
in previous approaches [36, 35].
Compared to temporal
stereo methods [33, 54], ours does not require sequential
data input for obtaining the BEV feature map; thus, using
an arbitrary number of BEV feature maps does not increase
latency. We note that BEV feature maps on previous times-
tamps are obtained without gradients during training fol-
lowing standard practices.
As shown in Table 12, using multiple temporal frames
significantly improves mAP, mATE, and mAVE. Corre-
sponding to results on recent approaches using temporal
BEV feature maps [54], a larger number of frames con-
sistently yields better performance. However, we observe
the unstable orientation error (mAOE), suggesting room for
improvement in utilizing BEV feature maps, and we leave
this as future work. As the performance gain is saturated
on four frames, we decide to use four frames considering
computation time and memory during training.
Sparse Aggregation.
In Table 13, we ablate the num-
ber of Nk feature grids on sparse aggregation settings.
Note that the total number of BEV feature grids is N =
256 × 256 = 65536 in our long-range setting and we report
the performance on Car class at 100m perception range.
Since the computational complexity of sparse aggregation
O(2Nk + NkK) is linear to sparse input queries Nk, us-
# Top-K
AP
ATE
AOE
AVE
FPS
1024
49.8
0.399
0.216
0.371
14.1
2048
52.4
0.382
0.202
0.352
14.0
4096
54.0
0.367
0.194
0.340
14.0
8192
54.6
0.362
0.191
0.352
13.8
All
56.9
0.325
0.158
0.298
11.5
Table 13. Ablation of sparse aggregation.
ing a small set of features for MFA significantly reduces
the computation of Multi-modal Deformable Cross Atten-
tion (MDCA). More specifically, using 4096 size queries
reduce the latency of MFA by 76.4% (21.01ms to 4.96ms)
on 256 × 256 size BEV grid. However, as the BEV fea-
ture map becomes sparse and discretized after top-k sam-
pling, the performance is degraded. We find that the per-
formance drops on True Positive metrics (e.g., ATE, AOE,
AVE) are more significant than AP, assuming that the clas-
sification network can maintain its performance, but the re-
gression network suffers from sparsely spread BEV features
to regress objects’ attributes.
E. Additional Qualitative Results
We show additional qualitative results of 3D object de-
tection (long-range 256 × 704 and R50 model) and BEV
segmentation (256 × 704 and R50 model).
To visualize 3D detection results for the range of 200m×
200m, we disable points in box filtering as described in Ap-
pendix C.4. As can be seen in Fig. 7, CRN is capable of
detecting objects even at a very far distance under various
and complex driving scenarios. Thanks to radar fusion, ob-
jects strongly occluded by other objects or hardly visible by
low lighting are successfully detected by ours. Moreover,
even if some objects do not have radar point returns, CRN
can still detect them by image only. Failure cases of CRN
are likely caused when objects are rare classes and do not
without radar points (e.g., construction vehicles behind wire
mesh or trailers heavily occluded).
We further visualize BEV segmentation results in the
range of 100m×100m, following the same setting of previ-
ous works. As shown in Fig. 8, CRN is also capable of accu-
rately predicting segmentation occupancy of drivable region
and vehicle. Thanks to our camera-radar fusion framework


## Page 16

to generate a semantically rich and spatially accurate fea-
ture map, our results show stable performance under vari-
ous lighting and weather conditions. CRN can further pre-
dict occupancy of the vehicles with a complete shape both
at nearby and faraway distances, even when the vehicles are
partially visible. In terms of the drivable region, CRN can
successfully predict the complex shapes of the road even
under occlusions.


## Page 17

Figure 7. Additional qualitative results of 3D object detection on nuScenes val set: from left to right, day, rainy, and night scenarios.
Green boxes are ground truths, blue boxes are our prediction results, and black dots are radar points. We also show the failure cases and
highlight them with red circles on the bottom row. Ground truth maps on the background are used for visualization. Best viewed in color
with zoom in.


## Page 18

Figure 8. Qualitative results of BEV segmentation on nuScenes val set on various road shapes and weather conditions: from top to bottom,
day, rainy, and night scenarios. Images on the top are the six camera views surrounding the vehicle, the bottom left is ground truth, and the
bottom right is our prediction results. Best viewed in color with zoom in.

