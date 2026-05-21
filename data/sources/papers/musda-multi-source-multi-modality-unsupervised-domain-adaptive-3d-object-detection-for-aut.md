# MUSDA: Multi-source Multi-modality Unsupervised Domain Adaptive 3D Object Detection for Autonomous Driving

**Source**: arXiv:2605.10026

**Type**: Academic Paper

---

## Page 1

MUSDA: Multi-source Multi-modality
Unsupervised Domain Adaptive 3D Object
Detection for Autonomous Driving
Xiaohu Lu
Electrical and Computer Engineering
Michigan State University
East Lansing, USA
luxiaohu@msu.edu
Hamed Khatounabadi
Electrical and Computer Engineering
Michigan State University
East Lansing, USA
khatouna@msu.edu
Hayder Radha
Electrical and Computer Engineering
Michigan State University
East Lansing, USA
radha@msu.edu
Abstract—With the advancement of autonomous driving, nu-
merous annotated multi-modality datasets have become avail-
able. This presents an opportunity to develop domain-adaptive
3D object detectors for new environments without relying on
labor-intensive manual annotations. However, traditional domain
adaptation methods typically focus on a single source domain or a
single modality, limiting their effectiveness in multi-source, multi-
modality scenarios. In this paper, we propose a novel framework
for multi-source, multi-modality unsupervised domain adaptation
in 3D object detection for autonomous driving. Given multi-
ple labeled source domains and one unlabeled target domain,
our framework first introduces hierarchical spatially-conditioned
(HSC) domain classifiers, which jointly align features from both
camera and LiDAR modalities at two distinct levels for each
source–target domain pair. To effectively leverage information
from multiple source domains, we construct a prototype graph
between each pair of domains. Based on this, we develop a
prototype graph weighted (PGW) multi-source fusion strategy
to aggregate predictions from multiple source detection heads.
Experimental results on three widely used 3D object detection
datasets — Waymo, nuScenes, and Lyft — demonstrate that
our proposed framework effectively integrates information across
both modalities and source domains, consistently outperforming
state-of-the-art methods.
Index Terms—Multi-source, Multi-modality, 3D Object Detec-
tion
I. INTRODUCTION
With increase deployment of self-driving cars, the per-
ception systems of autonomous vehicles must now operate
reliably across a wide range of scenarios, including adverse
weather, varying lighting conditions, and other challenging
environments. These requirements necessitate the integration
of multiple sensors to enhance perception performance and
ensure safety. Consequently, an increasing number of datasets
have been released with multimodal data. Early examples
include KITTI [1], Lyft Level 5 [2], nuScenes [3], Waymo [4],
and DENSE [5], followed by more recent datasets such
as Ithaca365 [6], Argoverse 2 [7], MSU-Four Seasons [8],
and MUSES [9], among others. With dozens of annotated
multi-modal datasets now available for autonomous driving,
it becomes increasingly valuable to explore how the industry
and academia can leverage these resources to develop domain-
adaptive 3D object detectors for new environments in the
absence of labor-intensive manual annotations.
Traditional domain adaptation, involving a single source
domain and a single modality, has been extensively studied
in tasks such as image classification [10], [11], semantic
segmentation [12], [13], and object detection [14], [15], [16].
These approaches aim to transfer knowledge from a single la-
beled source domain to improve performance on an unlabeled
target domain within the same modality. However, extend-
ing from traditional domain adaptation to the multi-source,
multi-modality setting introduces significantly greater chal-
lenges. These challenges arise from two key aspects: (1) how
to effectively fuse domain-adaptive features across different
modalities, and (2) how to efficiently exploit complementary
information from multiple source domains. To tackle the multi-
modality aspect in object detection, several methods have
been proposed [17], [18], [19], [20], [5]. Meanwhile, other
approaches focus on the multi-source setting [21], [22], [23],
[24], [25], [26], [27], [28], [29], aiming to leverage diverse
domain knowledge to improve generalization. However, as of
the time of writing of this manuscript and to the best of our
knowledge, no existing work has addressed multi-source multi-
modality domain-adaptive 3D object detection for autonomous
driving.
Consequently, in this paper, we address this arguably new
problem of multi-source multi-modality unsupervised domain
adaptation (UDA) for 3D object detection in autonomous driv-
ing. Specifically, we propose hierarchical spatially-conditioned
domain classifiers that first condition a multi-modality feature
map using a predicted heatmap. The resulting multi-modality
domain probability map is then used as a conditioning sig-
nal for the modality-specific feature maps from LiDAR and
camera inputs, enabling fine-grained alignment between source
and target domain features. To effectively leverage the diverse
information across different source domains, we introduce a
low-complexity modification to the baseline architecture by
incorporating a Bird’s Eye View (BEV) domain embedding,
which learns domain-specific representations. During infer-
arXiv:2605.10026v1  [cs.CV]  11 May 2026


## Page 2

ence, the input LiDAR and camera data are processed by a
shared backbone network and passed through the detection
head multiple times, each time with a different BEV domain
embedding to generate multiple predictions that correspond
to the multi-source domain-specific representations. To guide
the fusion of these multi-source predictions during inference,
we further propose a novel prototype graph, resulting in
improved detection performance. Our MUlti-Source multi-
modality unsupervised Domain Adaptive 3D object detection
for autonomous driving is referred to as MUSDA for the
remainder of this paper. In summary, our contributions are:
1) We propose a novel hierarchical spatially-conditioned
domain classifiers to align multi-modality domain fea-
tures in both modality-fused feature map and modality-
specific feature maps.
2) We introduce a novel BEV domain embedding strategy
to learn domain-specific information in multi-source
scenario.
3) We develop a prototype graph to model relationships
between multiple domains and use it to weight and fuse
predictions from different sources.
4) Experiments on three popular 3D object detection
datasets with both LiDAR and camera modalities, i.e.,
Waymo [4], nuScenes [3], and Lyft [2] demonstrate the
effectiveness of the proposed MUSDA framework.
TABLE I
TIME CONSUMPTION FOR DIFFERENT COMPONENTS IN THE BASELINE
METHOD BEVFUSION [30].
Name
Time (ms)
Percentage
Camera Backbone
55.8
38.8%
LiDAR Backbone
73.5
51.2%
Fusion Backbone
1.1
0.8%
Fusion Head
13.2
9.2%
II. METHODOLOGY
A. Hierarchical Spatially-conditioned (HSC) Domain Classi-
fiers
In unsupervised domain adaptation, domain classifiers [31]
combined with gradient reversal layers (GRL) are widely used
to encourage the backbone network to learn domain-invariant
features that confuse the domain classifier. Several previous
methods have extended this approach from image-level to
pixel-level features [32], and from single-scale to multi-scale
representations [33]. To address the complex multi-modality
scenario, where features originate from images, point clouds,
and their fusion, we propose a novel hierarchical spatially-
conditioned domain classifiers strategy that aligns features
from both camera and LiDAR modalities across each source-
target domain pair. Specifically, let G2D
f , G3D
f , and GMM
f
represent the camera backbone network, LiDAR backbone
network, and multi-modality fusion backbone network, respec-
tively. Given a point cloud P and the corresponding multi-view
images I, the camera backbone network generates camera
BEV features f 2D = G2D
f (I), and the LiDAR backbone
network generates LiDAR BEV features f 3D = G3D
f (P).
These 2D and 3D BEV features are concatenated and fed
into the fusion backbone to generate multi-modality features
f MM = GMM
f
([f 2D, f 3D]). Finally the fusion head Y takes
f MM and the BEV domain embedding f emb (explained in
Sec. II-B1) as input to generate the predictions of the bounding
boxes and the heatmap h.
To eliminate the influence of background pixels and enable
more precise feature alignment on foreground regions, we
use the predicted heatmap as a spatial condition to guide
the multi-modality domain classifier operating on the multi-
modality feature. Specifically, given the multi-modality feature
f MM ∈RC×H×W and the predicted heatmap h ∈RK×H×W ,
where K is the number of classes, we first calculate the class-
agnostic heatmap h
′ ∈RH×W as the maximum probability
along the class dimension of h. The multi-modality feature
is then weighted by the class-agnostic heatmap as the first-
level spatial condition and passed to the multi-modality do-
main classifier DMM to predict the multi-modality domain
probability map as below:
pMM = DMM(GRL(f MM ⊙h
′)) ∈RH×W .
(1)
The corresponding domain classification loss is calculated
pixel-wisely as:
LMM
dom = −1
uv
X
u,v

d log pMM
u,v
+ (1 −d) log(1 −pMM
u,v )

,
(2)
where u and v denote spatial location on the feature map, d ∈
{0, 1} is the domain label, with d = 0 for the target domain
and d = 1 for the source domains, and pu,v represents the
predicted domain probability at position (u, v) for the multi-
modality feature map. GRL denotes the gradient reversal layer,
which inverts the gradient during backpropagation.
Aligning the fused multi-modality features may be insuf-
ficient in complex multi-modality UDA scenarios. Therefore,
we further design domain classifiers for both the camera and
LiDAR modalities using a hierarchical spatially-conditioned
strategy. Specifically, we use the multi-modality domain prob-
ability map as the second-level spatial condition to the camera
and LiDAR BEV feature, which is then passed to the corre-
sponding single-modality domain classifier D2D and D3D to
predict the single-modality domain probability map as below:
pSM = DSM(GRL(f SM ⊙pMM)) ∈RH×W .
(3)
where SM ∈{2D, 3D} denotes the single modality (either
2D or 3D). The same domain classification loss as in Eq. 2 is
used to train the 2D and 3D domain classifiers.
In summary, our hierarchical spatially-conditioned domain
classifiers operate in two levels: the first-level domain classifier
uses a class-agnostic heatmap as a spatial condition to separate
foreground from background, while the second-level domain
classifiers use the domain probability map from the first level
to further distinguish features that are easy or hard for the
domain classifier to confuse. This hierarchical design leads to


## Page 3

Camera 
Encoder
LiDAR
Encoder
Multiview
Images
LiDAR
Pointcloud
Camera 
Features
LiDAR
Features
Camera-BEV 
View Transform
Map to BEV
Camera-BEV 
Feature
LiDAR-BEV 
Feature
Multi-Modality 
Domain  Classifier
LiDAR Backbone
Heatmap
BEV Domain 
Embedding
Bounding 
Boxes
Fusion Backbone
Camera Backbone
Low-level 
Middle-level 
High-level 
Multi-Modality Domain 
Probability Map
GRL
Camera 
Domain  Classifier
GRL
LiDAR
Domain  Classifier
GRL
Spatial Conditioning
Spatial Conditioning
Spatial 
Conditioning
Fig. 1. The framework of our single-source multi-modality unsupervised domain adaptive approach. We first use the predicted heatmap as a first-level spatial
condition to guide the multi-modality domain classifier. Then, the predicted multi-modality domain probability map is employed as a second-level spatial
condition to further guide the camera and LiDAR BEV features.
improved performance, as demonstrated in the experimental
results.
The overall training objective is defined as:
L = Ldet + λ(LMM
dom + L3D
dom + L2D
dom),
(4)
where Ldet is the detection loss computed on the heatmap
and bounding boxes, following the formulation in [30]; LMM
dom ,
L3D
dom, and L2D
dom denote the domain classification losses for the
multi-modality, 3D, and 2D, respectively; and λ is a weighting
factor that balances the effect of domain classification.
B. Prototype Graph Weighted (PGW) Multi-source Fusion
In a multi-source unsupervised domain adaptation (UDA)
object detection scenario, we consider N labeled source
domains, denoted as S1, S2, . . . , SN, and a single unlabeled
target domain T. A key challenge in this setting is that differ-
ent source domains often exhibit varying domain gaps across
object classes. For instance, as shown in Tab. II, Lyft shares
more similar car sizes with Waymo, while nuScenes offers
significantly more pedestrian annotations than Lyft, reflect-
ing distinct source-domain-specific characteristics. To address
this phenomenon, we extend our single-source multi-modality
framework (shown in Fig. 1) to a multi-source setting that is
designed to handle variations in domain gaps between different
source-target pairs. In that context, we develop a graph-based
multi-source fusion strategy to effectively leverage source-
domain-specific information, as illustrated in Fig. 2.
1) Multi-source Training With Domain Embedding: Train-
ing a unified model that can effectively learn from multiple
source domains while minimizing the domain gap with the
target domain is challenging, as different source domains
may have varying levels of similarity to the target domain
depending on the object class. A naive approach is to use
separate fusion backbones for each source domain, but this sig-
nificantly increases model complexity. Noting that these sepa-
rate backbones largely share functionality and differ mainly
in source-domain-specific information, we propose to train
a single shared fusion backbone for all source domains. To
capture source-domain-specific characteristics more efficiently,
we introduce a domain embedding of size N×dim, where N is
the number of source domains. The embedding dimension is
set to dim = 128 by default in all experiments. As shown
in Fig. 2, during each training iteration involving the i-th
source domain, the corresponding domain embedding vector
is expanded from R1×dim to Rdim×H×W to match the spatial
dimensions of the multi-modality feature f MM ∈RC×H×W
and then concatenated with it on the channel dimension. The
resulting feature is then passed through the corresponding
fusion head to compute the detection loss Lossdet. During
training, the domain embedding is updated in the first half
of the total epochs and frozen in the second half to en-
hance stability. Specifically, in the first half, the model learns
representative embeddings for different domains, while in
the second half, these embeddings are used to guide feature
learning.
2) Multi-source Fusion Via Prototype Graph: To effectively
capture domain-specific information across different source
domains, we propose constructing a prototype graph to capture
class-wise relationships between domains, and use this graph
to guide the fusion of predictions from multiple sources.
Specifically, after completing the training stage with all source
domains and the target domain (with pseudo labels, as de-
scribed in Sec. II-B1), we input every training sample from
each domain into the trained model to extract low-, middle-,
and high-level multi-modality features along with the predicted
heatmap. For the i-th feature map f MM
i
∈RCi×Hi×Wi, where
i ∈{1, 2, 3} corresponds to the low-, middle-, and high-level
features, we interpolate the predicted heatmap h ∈RK×H×W
to obtain hi ∈RK×Hi×Wi, which matches the spatial di-
mensions of f MM
i
. Then we flatten the spatial dimensions
of the interpolated heat maps to get f flat
i
∈RCi×Mi and
hflat
i
∈RK×Mi, where Mi = Hi × Wi. To compute spatial


## Page 4

TABLE II
ANNOTATIONS PER FRAME AND MEAN SIZE OF THREE DIFFERENT OBJECT CLASSES: CAR, PEDESTRIAN, CYCLIST IN WAYMO, NUSCENES, AND LYFT.
Dataset
#Annotations Per Frame
Mean Size (m)
Car
Pedestrian
Cyclist
Car
Pedestrian
Cyclist
Waymo
27.5
12.8
0.3
[4.81, 2.11, 1.78]
[0.91, 0.86, 1.74]
[1.81, 0.84, 1.77]
nuScenes
18.9
6.6
0.6
[5.43, 2.11, 2.04]
[0.72, 0.66, 1.76]
[1.91, 0.69, 1.38]
Lyft
25.9
1.0
1.0
[5.20, 2.01, 1.87]
[0.80, 0.77, 1.78]
[1.77, 0.64, 1.45]
Fusion 
Head 1
1
.  .  .
ƾ
ƽя
…
ƽ֏
ƾ
0.0
0.3
…
0.6
ƽя
0.3
0.0
…
0.1
…
…
…
…
…
ƽ֏ 0.6
0.1
…
0.0
Prediction N
Domain 
Embedding 1
Domain 
Embedding N
Prediction 1
Prototype Graph 
Generation
Ǐ
Weighted 
Box  Fusion
Fusion 
Head 1
Prototype Graph
Fig. 2. Overview of our prototype graph weighted (PGW) multi-source fusion approach. During training, a domain embedding is learned to capture source-
domain-specific characteristics. At inference time, the multi-modality feature map is concatenated with different domain embeddings and passed through the
detection head multiple times to generate diverse predictions. A prototype graph is then constructed and used to weight and fuse these predictions for improved
detection performance.
weights for each class, we normalize the heatmap across
the spatial dimension, yielding ˜hflat
i . The class-wise feature
prototypes are then obtained as weighted sums of the feature
vectors:
Pi = ˜hflat
i
· f flat
i
⊤,
Pi ∈RK×Ci.
(5)
Each row of Pi represents the prototype feature vector for
a specific class. For the i-th feature level, we obtain a set
of prototypes {PT
i , PS1
i , . . . , PSN
i
}, corresponding to the target
domain and each of the N source domains. These prototypes
are then ℓ2-normalized, and pairwise distances are computed
as 1.0 minus the cosine similarity between each pair of
normalized vectors, resulting in a prototype graph for the i-
th feature level. The final prototype graph G is obtained by
averaging the graphs from the low-, middle-, and high-level
features.
During
inference,
given
the
prototype
graph
G
∈
RK×(1+N)×(1+N) and the N sets of predictions generated
using different domain embeddings, we apply a weighted box
fusion strategy to obtain the final fused predictions. Specifi-
cally, for each prediction consisting of a 3D bounding box b,
confidence score s, and category label l, we first calculate its
weight based on the prototype graph as follows:
w = s/(1 + Gl,1+n,1),
(6)
where Gl,1+n,1 denotes the prototype distance between the
n-th source domain and the target domain for category l.
Next, for each category, the 3D Intersection-over-Union (IoU)
is computed between all pairs of predictions belong to this
category, and predictions are grouped into clusters if their IoU
exceeds 0.1. For each resulting cluster Ci, the fused bounding
box ˆbi and confidence score ˆsi are computed as weighted
averages of the predictions within the cluster as follows:
ˆbi =
P
j∈Ci wjbj
P
j∈Ci wj
,
ˆsi =
P
j∈Ci wjsj
P
j∈Ci wj
(7)
Here, Ci denotes the set of indices corresponding to the
predictions in the i-th cluster, and j is an index within
this set. To enable effective averaging of orientations, the
rotation component of each bounding box is first converted
to its sine and cosine representations before fusion. Note
that the prototype graph only needs to be constructed once,
offline, after training. During inference, the only additional
computational cost comes from executing the fusion head
N −1 extra times, which is relatively low compared to the
cost of the feature backbones as shown in Tab. I.
III. EXPERIMENTS
A. Setup Details
Datasets and Metrics We conduct experiments on three
widely used multi-modal datasets that provide both LiDAR
and camera data: Waymo [4], nuScenes [3], and Lyft [2].
Since bounding boxes predicted in the UDA setting typically
deviate more from the ground truth, we adopt relatively relaxed
evaluation metrics. Specifically, when using Waymo as the
target domain, we lower the default 3D IoU thresholds from
0.7, 0.5, and 0.5 to 0.5, 0.3, and 0.3 for Car, Pedestrian,
and Cyclist, respectively, and report results on mAPL1/L2
as well as mAPHL1/L2. In the following experiments, unless
otherwise specified, we use nuScenes and Lyft as the source
domains and Waymo as the target domain.


## Page 5

TABLE III
AN ABLATION STUDY ON DIFFERENT PRE-TRAINING DOMAIN ADAPTATION (PTDA) STRATEGIES FOR SINGLE-SOURCE MULTI-MODALITY DOMAIN
ADAPTATION FROM NUSCENES TO WAYMO.
PTDA Strategy
mAP L1/mAP L2
mAPH L1/mAPH L2
Coordinate
Shifting
Intensity
Removal
Velocity
Removal
Class
Remapping
Car
Pedestrian
Cyclist
Car
Pedestrian
Cyclist
×
×
×
×
25.8/22.0
17.3/14.4
2.1/2.0
24.8/21.1
9.4/7.8
1.4/1.3
✓
×
×
×
34.2/29.1
16.0/13.2
4.3/4.2
32.8/28.0
8.3/6.9
2.7/2.6
✓
✓
×
×
44.0/37.5
12.2/10.1
5.2/5.0
42.8/36.5
6.8/5.6
3.3/3.2
✓
✓
✓
×
50.6/43.2
17.9/14.8
4.8/4.7
49.3/42.0
9.6/8.0
3.3/3.2
✓
✓
✓
✓
61.0/52.0
55.5/46.0
7.3/7.1
59.1/50.4
30.4/25.2
4.8/4.6
TABLE IV
COMPARISON OF DIFFERENT METHODS ON MULTI-SOURCE MULTI-MODALITY DOMAIN ADAPTATION FROM NUSCENES, LYFT TO WAYMO. WE
IMPLEMENTED THE PSEUDO LABEL METHOD IN [34] AND THE DISENTANGLE LEARNING METHOD IN [29] FOR COMPARISION. HSC-DC REPRESENTS
OUR PROPOSED HIERARCHICAL SPATIALLY-CONDITIONED DOMAIN CLASSIFIERS, AND PGW-MF DENOTES THE PROTOTYPE GRAPH WEIGHTED
MULTI-SOURCE FUSION MODULE.
Method
mAP L1/mAP L2
mAPH L1/mAPH L2
Car
Pedestrian
Cyclist
Car
Pedestrian
Cyclist
Source Only (w/ PTDA)
63.8/54.5
53.2/44.1
20.0/19.2
62.4/53.2
30.0/24.9
15.3/14.7
Pseudo label [34]
67.4/57.5
54.7/45.4
20.7/19.9
66.2/56.5
32.6/27.0
17.7/17.1
Disentangle learning [29]
66.9/57.1
54.7/45.4
20.4/19.6
65.8/56.2
32.2/26.7
15.2/14.6
HSC-DC (Our)
68.9/58.8
57.3/47.6
23.0/22.1
67.8/57.9
33.7/27.9
18.8/18.1
HSC-DC + PGW-MF (Our)
68.2/58.2
63.5/52.7
28.0/27.0
67.1/57.3
37.0/30.7
22.9/22.0
Oracle (Fully Supervised Target)
78.8/67.4
83.7/69.7
61.5/59.1
77.7/66.4
72.9/60.7
59.6/57.3
Methods We adopt the widely used BEVFusion [30] as
our baseline and implement two additional approaches —
pseudo labeling [34] and disentangled learning [29] — for
comparison, given the absence of existing multi-source multi-
modality methods.
Parameters We follow the default configuration of the
BEVFusion implementation in mmdetection3d [35]. The de-
tection range is set to [−54.0m, 54.0m] along the X and Y
axes, and [−5.0m, 3.0m] along the Z axis. The voxel size is
[0.075m, 0.075m, 0.2m] for the X, Y, and Z axes, respectively.
All experiments are conducted using two RTX A6000 GPUs.
Pre-training Domain Adaptation Simple preprocessing
operations on the source domain prior to training have been
shown to be highly effective for domain adaptation. For
instance, in the early LiDAR-only UDA work SN [36], source-
domain bounding boxes were resized to better match the
target-domain distribution. In the multi-modality setting, how-
ever, factors such as image resolution, point cloud coordinates,
and intensity introduce additional complexity. As summarized
in Tab. III, we evaluate four practical pre-training domain
adaptation (PTDA) strategies — coordinate shifting, intensity
removal, velocity removal, and class remapping — using the
BEVFusion model trained on nuScenes and tested on Waymo.
Coordinate shifting aligns the Z axis such that the ground plane
corresponds to z=0. Intensity removal restricts input to the
X, Y, and Z coordinates of the point cloud, thereby reducing
the domain gap associated with intensity values. Velocity
removal omits velocity prediction, allowing the model to focus
exclusively on 3D bounding box estimation. Class remapping
standardizes the label space across datasets by consolidating
classes into Car, Pedestrian, Cyclist, and Others, and the model
is trained to predict only Car, Pedestrian, and Cyclist. As
shown in Tab. III, these PTDA strategies effectively reduce
prominent domain gaps, resulting in more reasonable domain
adaptation performance. The corresponding results serve as
our comparison baseline.
TABLE V
ABLATION STUDY ON THE EFFECT OF OUR PROPOSED HIERARCHICAL
SPATIALLY-CONDITIONED DOMAIN CLASSIFIERS (HSC-DC) STRATEGY.
Method
mAP L1/mAP L2
Car
Pedestrian
Cyclist
Domain Classifier [32]
67.2/57.3
60.7/50.3
4.8/4.6
HSC-DC (Our)
68.9/58.8
57.3/47.6
23.0/22.1
B. Comparison
As shown in Tab. IV, the Source Only (w/ PTDA) baseline
exhibits the lowest performance across all object categories,
indicating a pronounced domain gap when transferring from
nuScenes and Lyft to Waymo even after applying pre-training
domain adaptation strategies. Incorporating Pseudo Label or
Disentangle Learning yields consistent improvements, demon-
strating that leveraging target pseudo supervision or enforcing
disentangled domain-invariant representations can partially
mitigate domain shifts. Our proposed HSC-DC framework can
improve performance across all metrics, confirming the advan-
tage of hierarchical spatially-conditioned domain classifiers
in aligning heterogeneous multi-source feature distributions.
Integrating the PGW-MF module can further improve the
performance, especially for challenging objects like Pedestrian
and Cyclist, indicating that our prototype graph weighted


## Page 6

TABLE VI
ABLATION STUDY ON OUR PROPOSED PROTOTYPE GRAPH WEIGHTED MULTI-SOURCE FUSION (PGW-MF) STRATEGY.“SOURCE 1 PREDICTION” AND
“SOURCE 2 PREDICTION” DENOTE THE PREDICTION RESULTS GENERATED BY THE FIRST AND SECOND FUSION HEADS, RESPECTIVELY.
Method
mAP L1/mAP L2
mAPH L1/mAPH L2
Car
Pedestrian
Cyclist
Car
Pedestrian
Cyclist
Source 1 Prediction
67.4/57.5
54.3/45.0
23.5/22.6
66.3/56.6
32.0/26.5
19.3/18.6
Source 2 Prediction
61.0/52.1
59.9/49.6
20.6/19.8
59.5/50.8
34.0/28.2
16.0/15.4
PGW-MF (Our)
68.2/58.2
63.5/52.7
28.0/27.0
67.1/57.3
37.0/30.7
22.9/22.0
(a)
(b)
Fig. 3. Visual comparison between our method (HSC-DC + PGW-MF) and the Source Only baseline (w/ PTDA). The red, blue, and green bounding boxes
denote the ground truth, our result, and the baseline result, respectively. Black arrows highlight our method’s predictions miss-detected by the baseline.
fusion strategy can effectively capitalizes on complementary
information across multiple source domains.
C. Ablation Study
Tab. V shows the comparison between our proposed hier-
archical spatially-conditioned domain classifiers and the tradi-
tional pixel-level domain classifier proposed in [32]. As shown
in the table, while the traditional domain classifier performs
well on the Pedestrian category, it struggles significantly on
Cyclist, leading to imbalanced performance across categories.
By contrast, our HSC-DC achieves clear improvements on
both Car and Cyclist, resulting in a more balanced overall
performance. This indicates that by introducing spatial con-
ditioning, the domain classifier can distribute attention more
evenly across object categories, rather than being biased to-
ward specific ones. In summary, incorporating spatial structure
helps the model achieve more stable and reliable cross-domain
feature alignment.
Tab. VI shows an ablation study assessing the effectiveness
of the proposed PGW-MF multi-source fusion strategy. Across
all object categories and metrics, PGW-MF consistently out-
performs using either source model alone. For instance, PGW-
MF improves Car mAP to 68.2/58.2 compared to 67.4/57.5
and 61.0/52.1 from the individual sources. The gains are
more pronounced for Pedestrian and Cyclist, where PGW-
MF effectively leverages complementary strengths of the two
sources. Similar improvements in mAPH indicate that PGW-
MF also enhances orientation estimation reliability. These
results confirm that simply selecting one single source model
is insufficient, and that PGW-MF provides a principled mecha-
nism to integrate heterogeneous source predictions. By weight-
ing contributions based on prototype-level feature distances,
PGW-MF effectively emphasizes reliable predictions while
suppressing misleading ones, leading to better performance.
D. Visual Comparison
Fig. 3 presents a visual comparison between our method and
the Source-Only baseline (w/ PTDA). As highlighted by the
black arrows, our method produces more correct detections
(blue bounding boxes) than the baseline (green bounding
boxes). Notably, these additional true positives often occur
in challenging scenarios, such as distant objects or cases with
sparse point observations. This demonstrates that our method
achieves more robust and reliable detection performance com-
pared to the baseline.
IV. CONCLUSION
In this work, we addressed the challenge of multi-source,
multi-modality unsupervised domain adaptation for 3D object
detection in autonomous driving. We introduced hierarchi-
cal spatially-conditioned domain classifiers to jointly align
camera and LiDAR features across all source–target domain
pairs. To further exploit cross-domain complementarity, we
constructed a prototype distance graph to characterize domain
relationships and guide fusion. Building on this, we proposed a
prototype distance graph weighted multi-source fusion strategy
that adaptively aggregates predictions from multiple source
detectors. Extensive experiments on Waymo, nuScenes, and
Lyft demonstrate that our framework delivers consistent im-
provements over existing state-of-the-art baselines.
ACKNOWLEDGMENT
This work was supported in part by the Sony Research
Award Program.


## Page 7

REFERENCES
[1] A. Geiger, P. Lenz, and R. Urtasun, “Are we ready for autonomous
driving? the kitti vision benchmark suite,” in 2012 IEEE conference on
computer vision and pattern recognition.
IEEE, 2012, pp. 3354–3361.
[2] Lyft,
“Lyft
level
5
perception
dataset
2019,”
in
https://level5.lyft.com/dataset/, 2019.
[3] H. Caesar, V. Bankiti, A. H. Lang, S. Vora, V. E. Liong, Q. Xu,
A. Krishnan, Y. Pan, G. Baldan, and O. Beijbom, “nuscenes: A
multimodal dataset for autonomous driving,” in Proceedings of the
IEEE/CVF conference on computer vision and pattern recognition, 2020,
pp. 11 621–11 631.
[4] P. Sun, H. Kretzschmar, X. Dotiwalla, A. Chouard, V. Patnaik, P. Tsui,
J. Guo, Y. Zhou, Y. Chai, B. Caine et al., “Scalability in perception
for autonomous driving: Waymo open dataset,” in Proceedings of the
IEEE/CVF conference on computer vision and pattern recognition, 2020,
pp. 2446–2454.
[5] M. Bijelic, T. Gruber, F. Mannan, F. Kraus, W. Ritter, K. Dietmayer,
and F. Heide, “Seeing through fog without seeing fog: Deep multi-
modal sensor fusion in unseen adverse weather,” in Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern Recognition,
2020, pp. 11 682–11 692.
[6] C. A. Diaz-Ruiz, Y. Xia, Y. You, J. Nino, J. Chen, J. Monica, X. Chen,
K. Luo, Y. Wang, M. Emond et al., “Ithaca365: Dataset and driving
perception under repeated and challenging weather conditions,” in Pro-
ceedings of the IEEE/CVF Conference on Computer Vision and Pattern
Recognition, 2022, pp. 21 383–21 392.
[7] B. Wilson, W. Qi, T. Agarwal, J. Lambert, J. Singh, S. Khandelwal,
B. Pan, R. Kumar, A. Hartnett, J. K. Pontes et al., “Argoverse 2: Next
generation datasets for self-driving perception and forecasting,” arXiv
preprint arXiv:2301.00493, 2023.
[8] D. Kent, M. Alyaqoub, X. Lu, H. Khatounabadi, K. Sung, C. Scheller,
A. Dalat, A. bin Thabit, R. Whitley, and H. Radha, “Msu-4s-the
michigan state university four seasons dataset,” in Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern Recognition,
2024, pp. 22 658–22 667.
[9] T. Br¨odermann, D. Bruggemann, C. Sakaridis, K. Ta, O. Liagouris,
J. Corkill, and L. Van Gool, “Muses: The multi-sensor semantic per-
ception dataset for driving under uncertainty,” in European Conference
on Computer Vision.
Springer, 2025, pp. 21–38.
[10] D. Peng, Q. Ke, A. Ambikapathi, Y. Yazici, Y. Lei, and J. Liu,
“Unsupervised domain adaptation via domain-adaptive diffusion,” IEEE
Transactions on Image Processing, 2024.
[11] I. Nejjar, Q. Wang, and O. Fink, “Dare-gram: Unsupervised domain
adaptation regression by aligning inverse gram matrices,” in Proceedings
of the IEEE/CVF conference on computer vision and pattern recognition,
2023, pp. 11 744–11 754.
[12] M. B. Colomer, P. L. Dovesi, T. Panagiotakopoulos, J. F. Carvalho,
L. H¨arenstam-Nielsen, H. Azizpour, H. Kjellstr¨om, D. Cremers, and
M. Poggi, “To adapt or not to adapt? real-time adaptation for semantic
segmentation,” in Proceedings of the IEEE/CVF International Confer-
ence on Computer Vision, 2023, pp. 16 548–16 559.
[13] Y. Cheng, F. Wei, J. Bao, D. Chen, and W. Zhang, “Adpl: Adaptive dual
path learning for domain adaptation of semantic segmentation,” IEEE
Transactions on Pattern Analysis and Machine Intelligence, vol. 45,
no. 8, pp. 9339–9356, 2023.
[14] X. Lu and H. Radha, “Dali: Domain adaptive lidar object detection
via distribution-level and instance-level pseudo label denoising,” IEEE
Transactions on Robotics, 2024.
[15] M. Kennerley, J.-G. Wang, B. Veeravalli, and R. T. Tan, “2pcnet:
Two-phase consistency training for day-to-night unsupervised domain
adaptive object detection,” in Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, 2023, pp. 11 484–11 493.
[16] G. Mattolin, L. Zanella, E. Ricci, and Y. Wang, “Confmix: Unsupervised
domain adaptation for object detection via confidence-based mixing,” in
Proceedings of the IEEE/CVF Winter Conference on Applications of
Computer Vision, 2023, pp. 423–433.
[17] D. Hegde, S. Lohit, K.-C. Peng, M. J. Jones, and V. M. Patel,
“Multimodal 3d object detection on unseen domains,” arXiv preprint
arXiv:2404.11764, 2024.
[18] G. Chang, W. Roh, S. Jang, D. Lee, D. Ji, G. Oh, J. Park, J. Kim,
and S. Kim, “Cmda: Cross-modal and domain adversarial adaptation for
lidar-based 3d object detection,” in Proceedings of the AAAI Conference
on Artificial Intelligence, vol. 38, no. 2, 2024, pp. 972–980.
[19] D. Tsai, J. S. Berrio, M. Shan, S. Worrall, and E. Nebot, “See eye to eye:
A lidar-agnostic 3d detection framework for unsupervised multi-target
domain adaptation,” IEEE Robotics and Automation Letters, 2022.
[20] G. Eskandar, R. A. Marsden, P. Pandiyan, M. D¨obler, K. Guirguis, and
B. Yang, “An unsupervised domain adaptive approach for multimodal
2d object detection in adverse weather conditions,” in 2022 IEEE/RSJ
International Conference on Intelligent Robots and Systems (IROS).
IEEE, 2022, pp. 10 865–10 872.
[21] S. Zhao, H. Yao, C. Lin, Y. Gao, and G. Ding, “Multi-source-free domain
adaptive object detection,” International Journal of Computer Vision,
vol. 132, no. 12, pp. 5950–5982, 2024.
[22] A. Belal, A. Meethal, F. P. Romero, M. Pedersoli, and E. Granger,
“Multi-source domain adaptation for object detection with prototype-
based mean teacher,” in Proceedings of the IEEE/CVF Winter Confer-
ence on Applications of Computer Vision, 2024, pp. 1277–1286.
[23] D. Tsai, J. S. Berrio, M. Shan, E. Nebot, and S. Worrall, “Ms3d++:
Ensemble of experts for multi-source unsupervised domain adaptation
in 3d object detection,” 2024.
[24] ——, “Ms3d: Leveraging multiple detectors for unsupervised domain
adaptation in 3d object detection,” in 2023 IEEE 26th International
Conference on Intelligent Transportation Systems (ITSC).
IEEE, 2023,
pp. 140–147.
[25] G. Wu, T. Cao, B. Liu, X. Chen, and Y. Ren, “Towards universal
lidar-based 3d object detection by multi-domain knowledge transfer,” in
Proceedings of the IEEE/CVF International Conference on Computer
Vision, 2023, pp. 8669–8678.
[26] J. Wu, J. Chen, M. He, Y. Wang, B. Li, B. Ma, W. Gan, W. Wu,
Y. Wang, and D. Huang, “Target-relevant knowledge preservation for
multi-source domain adaptive object detection,” in Proceedings of the
IEEE/CVF conference on computer vision and pattern recognition, 2022,
pp. 5301–5310.
[27] D. Zhang, M. Ye, Y. Liu, L. Xiong, and L. Zhou, “Multi-source unsu-
pervised domain adaptation for object detection,” Information Fusion,
vol. 78, pp. 138–148, 2022.
[28] X. Yao, S. Zhao, P. Xu, and J. Yang, “Multi-source domain adaptation
for object detection,” in Proceedings of the IEEE/CVF international
conference on computer vision, 2021, pp. 3273–3282.
[29] C. Lin, Z. Yuan, S. Zhao, P. Sun, C. Wang, and J. Cai, “Domain-invariant
disentangled network for generalizable object detection,” in Proceedings
of the IEEE/CVF international conference on computer vision, 2021, pp.
8771–8780.
[30] Z. Liu, H. Tang, A. Amini, X. Yang, H. Mao, D. L. Rus, and S. Han,
“Bevfusion: Multi-task multi-sensor fusion with unified bird’s-eye view
representation,” in 2023 IEEE international conference on robotics and
automation (ICRA).
IEEE, 2023, pp. 2774–2781.
[31] Y. Ganin, E. Ustinova, H. Ajakan, P. Germain, H. Larochelle, F. Lavio-
lette, M. Marchand, and V. Lempitsky, “Domain-adversarial training of
neural networks,” The Journal of Machine Learning Research, vol. 17,
no. 1, pp. 2096–2030, 2016.
[32] C. C. Hsu, Y. H. Tsai, Y. Y. Lin, and M. H. Yang, “Every pixel matters:
Center-aware feature alignment for domain adaptive object detector,” in
Proceedings of the European conference on computer vision (ECCV).
Springer Science and Business Media Deutschland GmbH, 2020, pp.
733–748.
[33] M. Hnewa and H. Radha, “Multiscale domain adaptive yolo for cross-
domain object detection,” in 2021 IEEE International Conference on
Image Processing (ICIP).
IEEE, 2021, pp. 3323–3327.
[34] N. Inoue, R. Furuta, T. Yamasaki, and K. Aizawa, “Cross-domain
weakly-supervised object detection through progressive domain adap-
tation,” in Proceedings of the IEEE conference on computer vision and
pattern recognition, 2018, pp. 5001–5009.
[35] M.
Contributors,
“MMDetection3D:
OpenMMLab
next-generation
platform for general 3D object detection,” https://github.com/open-
mmlab/mmdetection3d, 2020.
[36] Y. Wang, X. Chen, Y. You, L. E. Li, B. Hariharan, M. Campbell,
K. Q. Weinberger, and W.-L. Chao, “Train in germany, test in the usa:
Making 3d object detectors generalize,” in Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition, 2020, pp.
11 713–11 723.

