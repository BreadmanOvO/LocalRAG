# BEVStereo Enhancing Depth Estimation in Multi-view 3D Detection

**Source**: arxiv PDF, 9 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

BEVStereo: Enhancing Depth Estimation in Multi-view 3D Object Detection with
Dynamic Temporal Stereo
Yinhao Li1, Han Bao1, Zheng Ge2, Jinrong Yang3, Jianjian Sun2, Zeming Li2
1Institute of Computing Technology, Chinese Academy of Sciences,
2MEGVII Technology, 3Huazhong University of Science and Technology
{liyinhao, gezheng, yangjinrong, sunjianjian, lizeming}@megvii.com, baohan20s@ict.ac.cn
Abstract
Bounded by the inherent ambiguity of depth perception, con-
temporary camera-based 3D object detection methods fall
into the performance bottleneck. Intuitively, leveraging tem-
poral multi-view stereo (MVS) technology is the natural
knowledge for tackling this ambiguity. However, traditional
attempts of MVS are ﬂawed in two aspects when applying
to 3D object detection scenes: 1) The afﬁnity measurement
among all views suffers expensive computation cost; 2) It is
difﬁcult to deal with outdoor scenarios where objects are of-
ten mobile. To this end, we introduce an effective temporal
stereo method to dynamically select the scale of matching
candidates, enable to signiﬁcantly reduce computation over-
head. Going one step further, we design an iterative algo-
rithm to update more valuable candidates, making it adaptive
to moving candidates. We instantiate our proposed method
to multi-view 3D detector, namely BEVStereo. BEVStereo
achieves the new state-of-the-art performance (i.e., 52.5%
mAP and 61.0% NDS) on the camera-only track of nuScenes
dataset. Meanwhile, extensive experiments reﬂect our method
can deal with complex outdoor scenarios better than con-
temporary MVS approaches. Codes have been released at
https://github.com/Megvii-BaseDetection/BEVStereo.
Introduction
Due to the stability and inexpensive cost of vision sen-
sors, camera-based 3D object detection has received exten-
sive concern. Specially, the multi-view schemes (Wang et al.
2022b; Huang et al. 2021; Liu et al. 2022a; Li et al. 2022b;
Huang and Huang 2022; Liu et al. 2022b; Li et al. 2022a)
show signiﬁcantly promising, and have made lots of break-
throughs. However, there is still a substantial performance
gap compared with LiDAR-based approaches (Lang et al.
2019; Yan, Mao, and Li 2018; Yin, Zhou, and Krahenbuhl
2021), since it exposes a notoriously ill-posed issue for per-
ceiving depth.
Contemporary multi-view detectors (Huang et al. 2021;
Huang and Huang 2022; Li et al. 2022a) predict a discrete
depth distribution for each point of the ﬁeld of view (FOV),
which enables to project features from image representation
to BEV map. The uniﬁed BEV map is the key to learn-
ing harmonious results since the overlap regions of adjacent
views represent more complete to directly forecast results.
Such sweetness is hard to be enjoyed by the monocular-
based detector (Wang et al. 2021b), as a post-processing
strategy is needed to remove repetitive and low-quality 3D
boxes in overlap areas.
The above paradigm is based on an important precon-
ceived assumption, i.e., the perceived depth distribution in
FOV needs accurate enough. However, most of them per-
ceive depth by only feeding into single-frame images, which
is actually an ill-posed solution (Huang et al. 2021; Huang
and Huang 2022; Li et al. 2022a). Several studies (Yao et al.
2018; Xue et al. 2019; Bae, Budvytis, and Cipolla 2022)
point out that predicting depth needs multi-view stereo con-
dition, which requires images from different views to con-
struct cost volume. Fortunately, the automatic driving sce-
nario is often processed in a continuous time sequence, en-
abling us to leverage temporal views for constructing multi-
view stereo.
To carry out the traditional temporal stereo technology
like (Yao et al. 2018) is non-trivial in automatic driving sce-
narios, which manifests in two aspects:
1. Large memory cost. When we replace the depth module
in BEVDepth with a basic temporal stereo method (Yao
et al. 2018), the memory cost grows to 3.5 times that of
BEVDepth despite bringing a 1.6 percent promotion on
NDS, making it a tremendous burden to apply it to a de-
tection task;
2. Failing to reason the depth of moving objects and
static ego vehicle cases. Temporal stereo approaches are
unable to handle several situations (Wang, Pang, and Lin
2022) like a static ego vehicle and moving objects since
the parallax angle tends to 0 if ego vehicle is static and the
stereo is unable to match if the object is moving. How-
ever, after statistics in nuScenes scene, over 10% of the
frames’ ego vehicles are static, while approximately 25%
of the objects are moving. Therefore, these two short-
comings limit its application to autonomous driving sce-
narios.
MVS methods (Wang, Pang, and Lin 2022; Wang et al.
2022a) expose that the majority of the computational mem-
ory cost is associated with constructing cost volume due
to its calculation procedure of dense similarity. It naturally
motivates us to construct a sparse cost volume for cutting
computational memory. To this end, we propose a dynamic
mechanism to sample a small number of reference candidate
features for building cost volume instead of all ones along
arXiv:2209.10248v1  [cs.CV]  21 Sep 2022
### Page 2

the depth axis. It is implemented by predicting two model-
ing parameters, i.e., depth center µ and depth range σ. This
far, it can signiﬁcantly reduce computational memory. Going
into one step, we introduce a parameter evolution method
for µ and σ, which is carried out by applying the EM algo-
rithm to update the modeling parameters µ and σ. With the
evolution technique, it is possible to continuously improve
reference candidate features that are more important for cost
volume while adjusting to situations including moving ob-
jects and stationary ego vehicles. This insight is similar to
MaGNet (Bae, Budvytis, and Cipolla 2022), but it not only
fails to deal with complex outdoor situations but introduces
redundantly learnable parameters to update µ and σ. Finally,
we also introduce an advanced variant of Circle NMS (Yin,
Zhou, and Krahenbuhl 2021), which takes objects’ size into
account for better removing duplicate 3D boxes.
We instantiate our proposed methods to advanced
BEVDepth (Li et al. 2022a), namely BEVStereo. By con-
ducting comprehensive experiments on nuScence bench-
mark (Caesar et al. 2020), it shows signiﬁcant improvements
in the 3D object detection task. In conclusion, the contribu-
tions of this work are as three-fold as follows:
• We point out that the MVS technology is a promising
method for tackling the ill-posed issue of depth percep-
tion in camera-based 3D object detection task. But it ex-
poses two fatal ﬂaws in the automatic driving scenarios,
i.e., either large memory cost issue or moving objects and
static ego vehicles.
• We introduce a dynamic temporal stereo technique,
which can save extreme memory cost to construct cost
volume. Moreover, a parameter evolution algorithm is
proposed to tackle moving and noisy features of objects.
• BEVStereo improves mAP and NDS by 1.7% and 1.7%
on nuScenes dataset, while achieving the new SOTA per-
formance on the camera-only track. Extensive experi-
ments verify that our approach can effectively be adapted
to moving objects and static ego vehicles.
Related Work
Single-view 3D Object Detection
Many approaches have made their effort on predicting ob-
jects directly from single images. For the purpose of 3D ob-
ject detection, Cai et al. (Cai et al. 2020) calculates the depth
of the objects by integrating the height of the objects in the
image with the height of the objects in the real world. Based
on FCOS (Tian et al. 2019), FCOS3D (Wang et al. 2021b)
extends it to 3D object detection by changing the classiﬁ-
cation branch and regression branch which predicts 2D and
3D attributes at the same time. M3D-RPN (Brazil and Liu
2019) treats mono-view 3D object detection task as a stand-
alone 3D region proposal network, narrowing the gap be-
tween LiDAR-based approaches and camera-based meth-
ods. D4LCN (Ding et al. 2020) replaces 2D depth map with
pseudo LiDAR representation to better present 3D structure.
DFM (Wang, Pang, and Lin 2022) integrates temporal stereo
to mono-view 3D object recognition, improving the quality
of depth estimation while minimizing the negative effects of
difﬁcult situations that temporal stereo is unable to handle.
Multi-view 3D Object Detection
Current multi-view 3D object detectors can be divided into
two schemas: LSS-based (Philion and Fidler 2020) schema
and transformer-based schema.
BEVDet (Huang et al. 2021) is the ﬁrst study that com-
bines LSS and LiDAR detection head which uses LSS to
extract BEV feature and uses LiDAR detection head to pro-
pose 3D bounding boxes. By introducing previous frames,
BEVDet4D (Huang and Huang 2022) acquires the ability of
velocity prediction. To reduce memory usage, M2BEV (Xie
et al. 2022) decreases the learnable parameters and achieves
high efﬁciency on both inference speed and memory usage.
BEVDepth (Li et al. 2022a) uses LiDAR to generate depth
GT for supervision and encodes camera intrinsic and extrin-
sic parameters to enhance the model’s ability of depth per-
ception.
DETR3D (Wang et al. 2022b) extends DETR
(Carion
et al. 2020) into 3D space, using transformer to generate 3D
bounding boxes. Based on DETR, PETR (Liu et al. 2022a)
and PETRV2 (Liu et al. 2022b) adds position embedding
onto it. BEVFormer (Li et al. 2022b) uses deformable trans-
former to extract features from images and uses cross atten-
tion to link the feature between frames for velocity predic-
tion.
Depth Estimation
Based on the number of images used for depth estimation,
depth estimation methods can be divided into single-view
depth estimation and multi-view depth estimation.
Although predicting depth from a single image is obvi-
ously ill-posed, it is still possible to estimate some of the
depth of the objects by using the context as a signal. There-
fore, many approaches (Bhat, Alhashim, and Wonka 2021;
Eigen and Fergus 2015; Eigen, Puhrsch, and Fergus 2014a;
Fu et al. 2018) use CNN method to predict depth.
For the task of multi-view depth estimation, Constructing
cost volume is an effective way to predict depth (Zhu et al.
2021; Wei et al. 2021, 2022). MVSNet (Yao et al. 2018) is
the ﬁrst research that uses cost volume for depth estimation.
RMVSNet (Yao et al. 2019) reduces memory cost by intro-
ducing GRU module. MVSCRF (Xue et al. 2019) adds CRF
module onto MVSNet. PointMVSNet (Chen et al. 2019)
uses point algorithm to optimize the regression of depth es-
timation. Cascade MVSNet (Gu et al. 2020) uses cascade
structure, making it able to use large depth range and a small
amount of depth intervals. Fast-MVSNet (Yu and Gao 2020)
uses sparse cost volume and Gauss-Newton layer to speed
up MVSNet. Wang et al. (Wang et al. 2021a) use adaptive
patchmatch and multi-scale fusion to achieve good perfor-
mance while mataining high efﬁciency. Bae et al. (Bae, Bud-
vytis, and Cipolla 2022) introduce MaGNet to better fuse
single-view depth estimation and multi-view depth estima-
tion.
Method
BEVStereo is a stereo-based multi-view 3D object detector.
By applying our temporal stereo technique, it is able to han-
dle complex outdoor scenarios while maintaining memory
2
### Page 3

efﬁciency. We also propose a size-aware circle NMS ap-
proach to improve the proposal suppression process.
Preliminary Knowledge
Multi-view 3D object detection
LSS-based (Philion and
Fidler 2020) multi-view 3D object detectors currently in-
clude four components: an image encoder to extract the im-
age features, a depth module to generate depth and context,
then outer product them to get point features, a view trans-
former to convert the feature from camera view to the BEV
view, and a 3D detection head to propose the ﬁnal 3D bound-
ing boxes.
Temporal stereo methods to predict depth
MVS-
based (Yao et al. 2018) methods predict depth by construct-
ing cost volume. For every pixel on the reference feature,
they initially put forth a number of candidates along the
depth axis. They next convert these candidates from refer-
ence to source using a homography warping operation in
order to retrieve the relevant source feature and create the
cost volume. After cost volume is constructed. For the pur-
pose of predicting the conﬁdence of each depth candidate,
3D convolution is performed to regularize the cost volume.
Dynamic Temporal Stereo
Based on BEVDepth (Li et al. 2022a), BEVStereo changes
the way of generating depth prediction. Instead of predicting
depth from a single image, BEVStereo predicts both depth
from single feature (mono depth) and depth from tempo-
ral stereo (stereo depth). For mono depth, we directly pre-
dict depth prediction, which is the same as BEVDepth. For
stereo depth, we ﬁrstly predict depth center (µ) and depth
range (σ), then µ and σ are used to generate depth distri-
bution. Additionally, Weight Net is used to create a weight
map that will be applied on stereo depth. Mono depth and
weighted stereo depth are combined to get the ﬁnal depth.
Our framework overview is illustrated in Fig. 1.
Depth Module
Our Depth Module simultaneously pre-
dicts mono depth, µ, σ and context. After iterating µ and
σ by our EM method, they are used to generate the stereo
depth. The process of iterating µ and σ is illustrated in Fig. 2.
We choose to estimate µ and σ, which stand for the depth
center and depth range of the cost volume. Compared to
other stereo-based methods of splitting bins along the depth
dimension (Yao et al. 2018; Wang et al. 2022a), our method
can dynamically choose the search area while also lower-
ing the number of candidates. After estimating µ and σ of
the reference frame, we can dynamically select candidates
for each pixel based on the depth center and range of cost
volume and obtain the depth of these candidates. These can-
didates are used for homography warping operation to fetch
the feature from source frame, as illustrated in Equ. 1, where
P denotes the coordinate of the point, D denotes the depth
of the candidate, src denotes source frame, ref denotes ref-
erence frame, Mref2src denotes the transformation matrix
from the reference frame to source frame and K denotes
the intrinsic matrix. The reference feature and the warpped
source feature are used to construct cost volume. Similarity
Net is followed to predict the conﬁdence score of all candi-
dates.
Psrc[u·z, v·z, z] = K×Mref2src×K−1×(D·Pref[u, v, 1])
(1)
Inspired by the EM algorithm, We attempt to make the ex-
pectation of µ closer to the depth gt during the iteration pro-
cess. Since we compute each point’s conﬁdence after sam-
pling a number of points close to µ, it is only natural that we
use this knowledge to further our objectives. As a result, we
update µ using the weight sum method, which causes µ to
become the expectation of the sample points for each itera-
tion. The update rule is illustrated in Eq. 2, where Di denotes
the depth of the ith candidate and Pi denotes the probabil-
ity of the ith candidate. When facing cases like static ego
vehicle and moving objects, all candidates share the same
low probability since it is hard to ﬁnd the best match point
on the source feature, µ is able to maintain its value by us-
ing the weight sum technique. For other scenarios, the value
of µ will approach the true depth value in the process of
iteration. Surprisingly, we discover that when µ and mono
depth are trained together, the quality of initial µ is also en-
hanced under the direction of mono depth. Therefore, in all
kinds of scenarios, our dynamic temporal stereo approach
can improve depth prediction. As µ is being updated in the
process of iteration, it is also critical to ﬁnd the suitable σ
to set the searching range. In accordance with existing in-
formation, the searching range should be reduced when the
conﬁdence of µ is high and expanded when it is low, we up-
date σ following Equ. 3 where Pµ denotes the conﬁdence of
µ. Without introducing any learnable parameters, the search
range is optimized during iteration.
To prevent the scenario where the projected µ is far from
the depth gt, making it difﬁcult to optimize µ during itera-
tion. we divide the depth into different ranges and use our it-
eration technique in each split range. After the iteration pro-
cess is ﬁnished, the depth map is generated following Equ. 4
where P denotes the computed depth conﬁdence and D de-
notes the depth of the split bins along the depth axis for each
pixel.
µ =
n
X
i=1
Di · Pi,
(2)
σnew = σold
2 · Pµ
,
(3)
P = exp(−1
2 · (D −µ
√σ )2).
(4)
Weight Net
Even while the temporal stereo is capable of
accurately predicting depth, there are still some areas where
it is unreliable because some reference feature points do not
correlate to positions on source feature. Therefore, we intro-
duce Weight Net to better combine mono depth and stereo
depth. To do this, we apply the same homography warping
operation to fetch the mono depth of the source frame, using
µ as the depth. A similarity net is then applied to the warped
mono depth from the source frame and the mono depth from
the reference frame to construct the weight map.
3
### Page 4

Mono 
Depth
Context
μ  and σ
Stereo Depth
Weight Map
Weight Map
Detection 
Head
Image Feature(t-1)
Image Feature(t)
Stereo Depth
Weight 
Net
Weight 
Net
Depth Module
Ft-1
Ft
Reference
Source
Ft
Ft-1
Shared 
Weight
Depth Module
Mono 
Depth
Context
Reference
Source
BEV Feature
BEV Feature
Voxel
Pooling
Voxel
Pooling
C
μ  and σ
μ
μ
Figure 1: Framework of BEVStereo. The Depth Module uses the image feature of the reference frame and source frame as input
to generate µ, σ, context, and mono depth. Stereo depth is produced using µ and σ. Weight Net uses µ and the mono depth of
two frames to create a weight map that is applied to the stereo depth. Mono depth and weighted stereo depth are accumulated
together to create the ﬁnal depth. BEV Feature is produced when context is combined with it and is used by the detecting head.
μ and σ
Source Feature
Homo 
Warping
Inner 
Product
Depth Confidence
Update
Reference Feature
Similarity 
Net
Figure 2: Iterative process of µ and σ. The initial µ and σ
are generated using feature of the reference frame as input.
For each round of iteration, µ and σ are used for homogra-
phy warping to fetch the source feature. Similarity Net takes
the inner product results of warpped source feature and ref-
erence feature as input to generate depth conﬁdence which
is used to update µ and σ.
Size-aware Circle NMS
The distance between the centers of two bounding boxes
is used by circle NMS (Yin, Zhou, and Krahenbuhl 2021)
function as a criterion for suppression. Circle NMS achieves
excellent efﬁciency and good performance by bypassing the
difﬁcult process of computing rotated IoU of bouding boxes.
However, ignoring the size of boxes will result in two draw-
backs as illustrated in Fig. 3: 1) No matter how closely the
boxes overlap, the NMS algorithm yields the same output as
long as the box centers are ﬁxed. 2) When boxes are placed
differently, boxes with 0 IoU may be removed while boxes
IoU:0.8
IoU:0 
IoU:0.2 
IoU:0.6 
Figure 3: Drawbacks of circle NMS. In the left part of the
ﬁgure, despite having distinct IoUs, the blue boxes and red
boxes share the same center distance as long as their cen-
ters coincide. In the right part of the ﬁgure, when the green
box has the highest score, the red box is more likely to be
suppressed since its center is closer to the green box’s center
which goes against our common sense.
with high IoU are kept.
We propose size-aware circle NMS, which avoids com-
puting rotated IoU while taking into consideration the size of
the boxes. We separate the distance of two bounding boxes’
centers into x axis and y axis. We use xthre and ythre as
threholds of x axis and y axis, which are computed follow-
ing Equ. 5 and Equ. 6, where θ denotes the orientation, w
denotes the hyper parameter of scale factor, dx denotes the
length of the box and dy denotes the width of the box. The
box will be suppressed when the distance in x axis is smaller
than xthre and distance in y axis is smaller than ythre. By
4
### Page 5

applying size-aware circle NMS, the blue box with a lower
score will be suppressed in scenarios like the left portion of
Fig 3 because it has a greater xthre and ythre. The blue box
will be suppressed in scenarios like the right portion of Fig. 3
because the distances in the x and y axes are more likely to
be smaller than xthre and ythre in the mean time.
xthre = w·(sinθ1·dx1+cosθ1·dy1+sinθ2·dx2+cosθ2·dy2).
(5)
ythre = w·(sinθ1×dy1+cosθ1·dx1+sinθ2·dy2+cosθ2·dx2).
(6)
Experiment
In this section, we ﬁrst describe the experimental settings
that we employ before going into the speciﬁcs of our im-
plementation strategy. Experiments involving heavy abla-
tion are carried out to conﬁrm the efﬁcacy and validity of
BEVStereo.
Experimental Settings
Dataset and evaluation metrics
We decide to run our ex-
periments on the nuScenes (Caesar et al. 2020) dataset. For
training, we use LiDAR and image data, but we only use
image data for inference. In the case of image data, the key
frame image and the furthest sweep connected to it are used,
whereas in the case of LiDAR data, only the key frame data
is used. We assess the results of our method using detec-
tion and depth metrics. Memory usage is also used to assess
the effectiveness of our method. To be more speciﬁc, we re-
port the mean Average Precision (mAP), nuScenes Detec-
tion Score (NDS), mean Average Translation Error (mATE),
mean Average Scale Error (mASE), mean Average Orienta-
tion Error (mAOE), mean Average Velocity Error (mAVE),
and mean Average Attribute Error (mAAE). We follow the
established evaluation procedures for the depth estimation
task (Eigen, Puhrsch, and Fergus 2014b), reporting scale in-
variant logarithmic error (SILog), mean absolute relative er-
ror (Abs Rel), mean squared relative error (Sq Rel), mean
…
…
…
…
…
…
…
…
…                                   …
…                                  …
…
…
…
…
…                                    …
…
…
…
…
…
…
…
…
gemo_xyz
(stored in shared memory)
point features
BEV features
0    1    2          …         29 30 31
32 33 34         …          61 62 63
64 65 66         …          93 94 95
96 97 98         …          125 126 127
thread block
warp 1
warp 2
warp 3
warp 0
Figure 4: Thread mapping of point features to BEV features.
Based on the point coordinates, the point features are atom-
ically accumulated into the corresponding BEV features.
Each thread block loads the point coordinates it is respon-
sible for into the shared memory.
log10 error (log10), and root mean squared error (RMSE) to
assess our approach.
Implementation details
We implement BEVStereo based
on BEVDepth (Li et al. 2022a). The feature map we employ
for building the cost volume has a downsampling rate of 4
while the depth feature’s ﬁnal form remains unchanged. The
MVS (Yao et al. 2018) approach is applied to replace the
depth module in BEVDepth with the same input resolution
and output resolution in order to fairly demonstrate the ef-
fectiveness of our method. The learning rate is set to 2e-4,
the EMA technique is also used, and AdamW (Loshchilov
and Hutter 2017) is used as the optimizer. During training,
we use both image and BEV data augmentation.
Analysis
We perform numerous experiments to examine the mech-
anism of BEVStereo in order to better understand how it
works. We choose BEVDepth (Li et al. 2022a) as baseline,
we also implement MVSNet (Yao et al. 2018) on BEVDepth
as a comparison to show the distinct beneﬁt that BEVStereo
provides, detection results and recall results are used for
comparison.
Memory analysis
We keep track of memory usage and
detection results to demonstrate how effectively we use our
memory. We also monitor the same matrics for the MVS-
based (Yao et al. 2018) approach for fair comparison.
As illustrated in Tab. 6, BEVStereo increases the met-
rics on mAP, mATE, and NDS considerably at the ex-
pense of adding little memory consumption. When com-
pared to using MVS (Yao et al. 2018) on BEVDepth (Li
et al. 2022a), BEVStereo considerably reduces memory us-
age while boosting performance.
Performance analysis
To begin with, we demonstrate
the performance comparison under the nuScenes (Caesar
et al. 2020) evaluation metrics. As shown in Tab. 1, Our
BEVStereo outperforms BEVDepth on mAP, mATE and
NDS. Tab. 2 shows that the accuracy of depth estimation
is improved by introducing our design.
We assess the performance of BEVStereo under challeng-
ing conditions such as moving objects, and static ego vehi-
cles in order to show how well it adapts to complicated out-
door environments. Tab. 3 demonstrates that BEVStereo still
has the ability to improve performance even while MVS ap-
proach fails when dealing with moving objects. The static
objects, which make up the majority of MVS schema’s con-
tribution, are also used to evaluate our method. As shown
in Tab. 4, BEVStereo’s ability of perceiving static objects is
even higher than BEVDepth with MVS. We choose frames
whose ego vehicle has a low velocity for evaluation since
MVS cannot handle situations when this occurs. As can be
seen in Tab. 5, BEVStereo still improves performance even
when MVS fails in these conditions. It is important to note
that BEVStereo still produces the similar results when faced
with circumstances like moving objects and static ego ve-
hicles if µ is not updated during the inference step. This
demonstrates that our schema is capable of guiding the
5
### Page 6

Method
WN
mAP↑
mATE↓
mASE↓
mAOE↓
mAVE↓
mAAE↓
NDS↑
BEVDepth
32.7
70.1
27.7
55.6
55.8
21.4
43.3
BEVStereo
34.5
66.5
27.9
52.9
55.0
23.6
44.7
BEVStereo
✓
34.6
65.3
27.4
53.1
51.6
23.0
45.3
Table 1: Detection results on the nuScenes val set. WN denotes Weight Net.
Method
SILog↓
Abs Rel↓
Sq Rel↓
log10↓
RMSE↓
BEVDepth
21.74
0.155
1.223
0.060
5.269
BEVStereo
21.74
0.152
1.206
0.059
5.246
Table 2: Evaluation of depth prediction on the nuScenes val
set.
Method
Iter
TH=0.5
TH=1
TH=2
TH=4
BEVDepth
28.32
46.10
60.37
71.18
BEVDepth + MVS
27.67
46.40
59.99
71.26
BEVStereo
29.79
49.26
61.53
72.10
BEVStereo
✓
29.40
48.97
61.53
72.27
Table 3: Recall results on the nuScenes val set. Only boxes
with velocity higher than 1m/s are maintained for analy-
sis. BEVDepth + MVS denotes replacing depth module in
BEVDepth with MVS approach. Different thresholds are
utilized depending on the distance between boxes’ center.
Iter denotes whether to iterate µ during the inference stage.
Method
TH=0.5
TH=1
TH=2
TH=4
BEVDepth
32.80
53.58
70.00
80.89
BEVDepth + MVS
33.61
54.23
69.89
80.57
BEVStereo
33.90
54.79
70.51
81.01
Table 4: Recall results on the nuScenes val set. Only boxes
with velocity lower than 1m/s are maintained for analysis.
Depth Module to produce better µ and maintaining the ini-
tial prediction of µ in the face of these eventualities.
Ablation Study
Iteration of µ and σ
We conduct various experiments dur-
ing the inference stage by modifying the number of itera-
tions just to verify the function of iterating µ and σ. As illus-
trated in Tab. 7, the detection results improve as the number
of iterations grows.
Weight Net
We run the experiment under identical condi-
tions without Weight Net to assess its validity. Weight Net
promotes the detection results, as shown in Tab. 1.
Size-aware Circle NMS
We compare BEVStereo with the
size-aware circle NMS to BEVStereo with the conventional
circle NMS as our baseline. They are subjected to class-
aware and class-agnostic procedures in order to test the va-
lidity of size-aware circle NMS.
As shown in Tab. 8, our size-aware circle NMS improves
on the matrices of mAP, mATE, and NDS when using class-
aware NMS. The traditional distance-based circle NMS has
Method
Iter
mAP↑
mATE↓
NDS↑
BEVDepth
32.73
73.47
44.14
BEVDepth + MVS
31.55
78.06
43.21
BEVStereo
33.12
63.01
46.68
BEVStereo
✓
33.76
63.49
46.76
Table 5: Detection results on the nuScenes val set. Only
frames with ego vehicles moving at speeds less than 1 m/s
are employed for evaluation.
Method
Memory
mAP↑
mATE↓
NDS↑
BEVDepth
6.49GB
32.7
70.1
43.3
BEVDepth + MVS
24.04GB
34.7
67.1
44.9
BEVStereo
8.01GB
34.6
65.3
45.3
Table 6: Memory usage and detection results of BEVDepth,
BEVDepth with MVS and BEVStereo.
num iter
mAP↑
mATE↓
NDS↑
0
32.7
67.4
43.9
1
33.1
67.0
44.2
2
34.1
65.9
45.0
3
34.6
65.3
45.3
Table 7: Detection results on the nuScenes val set. num iter
denotes the number of iterations for µ.
Method
CA
mAP↑
mATE↓
NDS↑
circlenms
34.6
65.3
45.3
circle-nms
✓
24.9
80.6
38.0
size-aware-circlenms
35.1
64.7
45.6
size-aware-circlenms
✓
33.3
64.1
45.0
Table 8: Detection results on the nuScenes val set. CA de-
notes class-agnostic. All results are conducted under the best
hyper parameters.
completely lost its capacity to suppress under class-agnostic
circumstance, while our size-aware circle NMS continues to
function well.
Efﬁcient Voxel Pooling v2
In the previous version of Efﬁ-
cient Voxel Pooling (Li et al. 2022a), threads within the same
warp access memory discontinuously, leading to more mem-
ory transactions, which results in poor performance. We en-
hance Efﬁcient Voxel Pooling by improving the way threads
are mapped, as illustrated in Fig. 4. For each block, we em-
ploy 32 and 4 threads on the x and y axes. First, 128 point
coordinates are loaded into shared memory by all the threads
in one block. Then, one point feature at a time is processed
6
### Page 7

Method
Modality
mAP↑
mATE↓
mASE↓
mAOE↓
mAVE↓
mAAE↓
NDS↑
CenterPoint
L
0.564
-
-
-
-
-
0.648
FCOS3D (Wang et al. 2021b)
C
0.358
0.690
0.249
0.452
1.434
0.124
0.428
DETR3D (Wang et al. 2022b)
C
0.412
0.641
0.255
0.394
0.845
0.133
0.479
BEVDet-Pure (Huang et al. 2021)
C
0.398
0.556
0.239
0.414
1.010
0.153
0.463
BEVDet-Beta
C
0.422
0.529
0.236
0.396
0.979
0.152
0.482
PETR (Liu et al. 2022a)
C
0.434
0.641
0.248
0.437
0.894
0.143
0.481
PETR-e
C
0.441
0.593
0.249
0.384
0.808
0.132
0.504
BEVDet4D (Huang and Huang 2022)
C
0.451
0.511
0.241
0.386
0.301
0.121
0.569
BEVFormer (Li et al. 2022b)
C
0.481
0.582
0.256
0.375
0.378
0.126
0.569
PETRv2 (Liu et al. 2022b)
C
0.490
0.561
0.243
0.361
0.343
0.120
0.582
BEVDepth (Li et al. 2022a)
C
0.503
0.445
0.245
0.378
0.320
0.126
0.600
BEVStereo
C
0.525
0.431
0.246
0.358
0.357
0.138
0.610
Table 9: Comparison on the nuScenes test set. L denotes LiDAR and C denotes camera.
(a) Baseline
(b) Baseline + MVS
(c) BEVStereo
Figure 5: Visualization of depth prediction. The blue area is the distribution of depth prediction, while the green line represents
the depth GT produced by the point cloud. The red dotted boxes denotes the promotion of depth prediction on moving objects
and the yellow dotted boxes denotes the the promotion of depth prediction on static objects.
Baseline
BEVStereo
Figure 6: Visualization of detection results. The blue dotted rectangle designates the object recognized by our approach is more
accurate on localization, while the red dotted circle designates the object detected by BEVStereo but missed by the baseline.
7
### Page 8

Method
Resolution Modality mAP↑NDS↑
CenterPoint-Voxel (Yin, Zhou, and Krahenbuhl 2021)
-
L
56.4
64.8
CenterPoint-Pillar
-
L
50.3
60.2
FCOS3D (Wang et al. 2021b)
900×1600
C
29.5
37.2
DETR3D (Wang et al. 2022b)
900×1600
C
30.3
37.4
BEVDet-R50 (Huang et al. 2021)
256×704
C
28.6
37.2
BEVDet-Base
512×1408
C
34.9
41.7
PETR-R50 (Liu et al. 2022a)
384×1056
C
31.3
38.1
PETR-R101
512×1408
C
35.7
42.1
PETR-Tiny
512×1408
C
36.1
43.1
BEVDet4D-Tiny (Huang and Huang 2022)
256×704
C
32.3
45.3
BEVDet4D-Base
640×1600
C
39.6
51.5
BEVFormer-S (Li et al. 2022b)
-
C
37.5
44.8
BEVDepth-R50 (Li et al. 2022a)
256×704
C
35.9
48.0
BEVDepth-ConvNext
512×1408
C
46.2
55.8
BEVStereo-R50
256×704
C
37.6
49.7
BEVStereo-ConvNext
512×1408
C
47.8
57.5
Table 10: Comparison on the nuScenes val set. L denotes
LiDAR and C denotes camera.
by each warp. According to the point coordinates, the point
feature is atomically accumulated to the matching BEV fea-
ture. The 128 point features are processed round robin by
four warps in a block till they are ﬁnished. In this man-
ner, performance-limiting memory transactions from the L2
cache and global memory are diminished.
We compare the latency of Efﬁcient Voxel Pooling v1 and
Efﬁcient Voxel Pooling v2 using various resolutions. Efﬁ-
cient Voxel Pooling v2 is able to reduce the latency up to
40%.
Visualization
As illustrated in Fig. 5, we can ﬁnd that BEVStereo has the
ability to promote the accuracy of depth estimation on both
moving and static objects. We also visualize the detection
results, as shown in Fig. 6 which also demonstrates the per-
formance promotion brought by BEVStereo.
Benchmark Result
We compare BEVStereo with other state-of-the-art meth-
ods like CenterPoint (Yin, Zhou, and Krahenbuhl 2021),
FCOS3D (Wang et al. 2021b), DETR3D (Wang et al.
2022b), BEVDet (Huang et al. 2021), PETR (Liu et al.
2022a), BEVDet4D (Huang and Huang 2022) and BEV-
Former (Li et al. 2022b). We evaluate our BEVStereo on
the nuScenes test and val set. As shown in Tab. 9 and
Tab. 10, BEVStereo achieves the highest score of camera-
based methods on both mAP and NDS.
Conclusion
In this paper, a novel multi-view 3D object detector is
proposed, namely BEVStereo. BEVStereo improves perfor-
mance without signiﬁcantly increasing memory usage by ap-
plying dynamic temporal stereo technique to create temporal
stereo. Some complex scenarios that other stereo-based ap-
proaches cannot handle can be resolved by our method. In
addition, we propose size-aware circle NMS, which takes
the size of boxes into account while avoiding the labori-
ous computation of rotated IoU. Under both class-aware and
class-agnostic circumstances, our size-aware circle NMS
performs satisfactorily. Last but not least, we present Efﬁ-
cient Voxel Pooling v2, which speeds up voxel pooling by
improving the efﬁciency of memory accesses.
Acknowledgements
Throughout the process of developing BEVStereo, I have
received a great deal of guidance and assistance. I would
like to thank Haotian Zhang, Yuefeng Wu and Tai Wang for
their wonderful collaboration and patient support.
References
Bae, G.; Budvytis, I.; and Cipolla, R. 2022.
Multi-View
Depth Estimation by Fusing Single-View Depth Probabil-
ity with Multi-View Geometry.
In Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern
Recognition, 2842–2851.
Bhat, S. F.; Alhashim, I.; and Wonka, P. 2021.
Adabins:
Depth estimation using adaptive bins.
In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition, 4009–4018.
Brazil, G.; and Liu, X. 2019. M3d-rpn: Monocular 3d re-
gion proposal network for object detection. In Proceedings
of the IEEE/CVF International Conference on Computer Vi-
sion, 9287–9296.
Caesar, H.; Bankiti, V.; Lang, A. H.; Vora, S.; Liong, V. E.;
Xu, Q.; Krishnan, A.; Pan, Y.; Baldan, G.; and Beijbom, O.
2020. nuscenes: A multimodal dataset for autonomous driv-
ing. In Proceedings of the IEEE/CVF conference on com-
puter vision and pattern recognition, 11621–11631.
Cai, Y.; Li, B.; Jiao, Z.; Li, H.; Zeng, X.; and Wang, X.
2020. Monocular 3d object detection with decoupled struc-
tured polygon estimation and height-guided depth estima-
tion. In Proceedings of the AAAI Conference on Artiﬁcial
Intelligence, volume 34, 10478–10485.
Carion, N.; Massa, F.; Synnaeve, G.; Usunier, N.; Kirillov,
A.; and Zagoruyko, S. 2020. End-to-end object detection
with transformers. In European conference on computer vi-
sion, 213–229. Springer.
Chen, R.; Han, S.; Xu, J.; and Su, H. 2019.
Point-based
multi-view stereo network. In Proceedings of the IEEE/CVF
international conference on computer vision, 1538–1547.
Ding, M.; Huo, Y.; Yi, H.; Wang, Z.; Shi, J.; Lu, Z.; and Luo,
P. 2020. Learning depth-guided convolutions for monocular
3d object detection. In Proceedings of the IEEE/CVF Con-
ference on Computer Vision and Pattern Recognition Work-
shops, 1000–1001.
Eigen, D.; and Fergus, R. 2015. Predicting depth, surface
normals and semantic labels with a common multi-scale
convolutional architecture. In Proceedings of the IEEE in-
ternational conference on computer vision, 2650–2658.
Eigen, D.; Puhrsch, C.; and Fergus, R. 2014a. Depth map
prediction from a single image using a multi-scale deep net-
work. Advances in neural information processing systems,
27.
Eigen, D.; Puhrsch, C.; and Fergus, R. 2014b. Depth map
prediction from a single image using a multi-scale deep net-
work. Advances in neural information processing systems,
27.
Fu, H.; Gong, M.; Wang, C.; Batmanghelich, K.; and Tao,
D. 2018. Deep ordinal regression network for monocular
8
### Page 9

depth estimation. In Proceedings of the IEEE conference on
computer vision and pattern recognition, 2002–2011.
Gu, X.; Fan, Z.; Zhu, S.; Dai, Z.; Tan, F.; and Tan, P. 2020.
Cascade cost volume for high-resolution multi-view stereo
and stereo matching. In Proceedings of the IEEE/CVF Con-
ference on Computer Vision and Pattern Recognition, 2495–
2504.
Huang, J.; and Huang, G. 2022. Bevdet4d: Exploit temporal
cues in multi-camera 3d object detection.
arXiv preprint
arXiv:2203.17054.
Huang, J.; Huang, G.; Zhu, Z.; and Du, D. 2021. Bevdet:
High-performance multi-camera 3d object detection in bird-
eye-view. arXiv preprint arXiv:2112.11790.
Lang, A. H.; Vora, S.; Caesar, H.; Zhou, L.; Yang, J.; and
Beijbom, O. 2019. Pointpillars: Fast encoders for object de-
tection from point clouds. In Proceedings of the IEEE/CVF
conference on computer vision and pattern recognition,
12697–12705.
Li, Y.; Ge, Z.; Yu, G.; Yang, J.; Wang, Z.; Shi, Y.; Sun,
J.; and Li, Z. 2022a. BEVDepth: Acquisition of Reliable
Depth for Multi-view 3D Object Detection. arXiv preprint
arXiv:2206.10092.
Li, Z.; Wang, W.; Li, H.; Xie, E.; Sima, C.; Lu, T.; Yu, Q.;
and Dai, J. 2022b. BEVFormer: Learning Bird’s-Eye-View
Representation from Multi-Camera Images via Spatiotem-
poral Transformers. arXiv preprint arXiv:2203.17270.
Liu, Y.; Wang, T.; Zhang, X.; and Sun, J. 2022a. Petr: Posi-
tion embedding transformation for multi-view 3d object de-
tection. arXiv preprint arXiv:2203.05625.
Liu, Y.; Yan, J.; Jia, F.; Li, S.; Gao, Q.; Wang, T.; Zhang,
X.; and Sun, J. 2022b. PETRv2: A Uniﬁed Framework for
3D Perception from Multi-Camera Images. arXiv preprint
arXiv:2206.01256.
Loshchilov, I.; and Hutter, F. 2017. Decoupled weight decay
regularization. arXiv preprint arXiv:1711.05101.
Philion, J.; and Fidler, S. 2020. Lift, splat, shoot: Encoding
images from arbitrary camera rigs by implicitly unprojecting
to 3d. In European Conference on Computer Vision, 194–
210. Springer.
Tian, Z.; Shen, C.; Chen, H.; and He, T. 2019. Fcos: Fully
convolutional one-stage object detection. In Proceedings of
the IEEE/CVF international conference on computer vision,
9627–9636.
Wang, F.; Galliani, S.; Vogel, C.; Speciale, P.; and Polle-
feys, M. 2021a. Patchmatchnet: Learned multi-view patch-
match stereo. In Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, 14194–14203.
Wang, T.; Lian, Q.; Zhu, C.; Zhu, X.; and Zhang, W.
2022a. MV-FCOS3D++: Multi-View Camera-Only 4D Ob-
ject Detection with Pretrained Monocular Backbones. arXiv
preprint arXiv:2207.12716.
Wang, T.; Pang, J.; and Lin, D. 2022. Monocular 3D Ob-
ject Detection with Depth from Motion.
arXiv preprint
arXiv:2207.12988.
Wang, T.; Zhu, X.; Pang, J.; and Lin, D. 2021b. Fcos3d:
Fully convolutional one-stage monocular 3d object detec-
tion. In Proceedings of the IEEE/CVF International Confer-
ence on Computer Vision, 913–922.
Wang, Y.; Guizilini, V. C.; Zhang, T.; Wang, Y.; Zhao, H.;
and Solomon, J. 2022b. Detr3d: 3d object detection from
multi-view images via 3d-to-2d queries. In Conference on
Robot Learning, 180–191. PMLR.
Wei, Z.; Zhu, Q.; Min, C.; Chen, Y.; and Wang, G. 2021. Aa-
rmvsnet: Adaptive aggregation recurrent multi-view stereo
network.
In Proceedings of the IEEE/CVF International
Conference on Computer Vision, 6187–6196.
Wei, Z.; Zhu, Q.; Min, C.; Chen, Y.; and Wang, G. 2022.
Bidirectional Hybrid LSTM Based Recurrent Neural Net-
work for Multi-view Stereo. IEEE Transactions on Visual-
ization and Computer Graphics.
Xie, E.; Yu, Z.; Zhou, D.; Philion, J.; Anandkumar, A.;
Fidler, S.; Luo, P.; and Alvarez, J. M. 2022.
Mˆ 2BEV:
Multi-Camera Joint 3D Detection and Segmentation with
Uniﬁed Birds-Eye View Representation.
arXiv preprint
arXiv:2204.05088.
Xue, Y.; Chen, J.; Wan, W.; Huang, Y.; Yu, C.; Li, T.; and
Bao, J. 2019. Mvscrf: Learning multi-view stereo with con-
ditional random ﬁelds. In Proceedings of the IEEE/CVF In-
ternational Conference on Computer Vision, 4312–4321.
Yan, Y.; Mao, Y.; and Li, B. 2018. Second: Sparsely embed-
ded convolutional detection. Sensors, 18(10): 3337.
Yao, Y.; Luo, Z.; Li, S.; Fang, T.; and Quan, L. 2018. Mvs-
net: Depth inference for unstructured multi-view stereo. In
Proceedings of the European Conference on Computer Vi-
sion (ECCV), 767–783.
Yao, Y.; Luo, Z.; Li, S.; Shen, T.; Fang, T.; and Quan,
L. 2019. Recurrent mvsnet for high-resolution multi-view
stereo depth inference.
In Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition,
5525–5534.
Yin, T.; Zhou, X.; and Krahenbuhl, P. 2021.
Center-
based 3d object detection and tracking. In Proceedings of
the IEEE/CVF conference on computer vision and pattern
recognition, 11784–11793.
Yu, Z.; and Gao, S. 2020.
Fast-mvsnet: Sparse-to-dense
multi-view stereo with learned propagation and gauss-
newton reﬁnement. In Proceedings of the IEEE/CVF Con-
ference on Computer Vision and Pattern Recognition, 1949–
1958.
Zhu, Q.; Min, C.; Wei, Z.; Chen, Y.; and Wang, G. 2021.
Deep Learning for Multi-View Stereo via Plane Sweep: A
Survey. arXiv preprint arXiv:2106.15328.
9