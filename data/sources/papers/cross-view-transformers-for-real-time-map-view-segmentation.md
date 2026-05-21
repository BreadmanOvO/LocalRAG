# Cross-view Transformers for Real-time Map-view Segmentation

**Source**: arxiv PDF, 10 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Cross-view Transformers for real-time Map-view Semantic Segmentation
Brady Zhou
UT Austin
brady.zhou@utexas.edu
Philipp Kr¨ahenb¨uhl
UT Austin
philkr@cs.utexas.edu
Abstract
We
present
cross-view
transformers,
an
efﬁcient
attention-based model for map-view semantic segmentation
from multiple cameras. Our architecture implicitly learns
a mapping from individual camera views into a canonical
map-view representation using a camera-aware cross-view
attention mechanism. Each camera uses positional embed-
dings that depend on its intrinsic and extrinsic calibration.
These embeddings allow a transformer to learn the map-
ping across different views without ever explicitly model-
ing it geometrically. The architecture consists of a convo-
lutional image encoder for each view and cross-view trans-
former layers to infer a map-view semantic segmentation.
Our model is simple, easily parallelizable, and runs in real-
time. The presented architecture performs at state-of-the-
art on the nuScenes dataset, with 4x faster inference speeds.
Code is available at https://github.com/bradyz/
cross_view_transformers.
1. Introduction
Autonomous vehicles depend on robust scene under-
standing and online mapping to navigate the world.
To
drive safely, these systems not only reason about the se-
mantics of their surroundings, but also a spatial under-
standing due to the geometric nature of navigation. Many
prior approaches directly model geometry and relationships
between different view and a canonical map representa-
tion [2, 14, 15, 16, 20, 29, 35].
They require an ex-
plicit [2, 15, 16, 20, 35] or probabilistic [14, 29] estimate of
depth in either image or map-view. However, this explicit
modeling can be hard. First, image-based depth estimates
are error-prone, as monocular depth estimates scale poorly
with the distance to the observer. Second, depth-based pro-
jections are a fairly inﬂexible and rigid bottleneck to map
between views. In this work, we take a different approach.
We learn to map from camera-view to a canonical map-
view representation using a cross-view transformer archi-
tecture. The transformer does not perform any explicit geo-
metric reasoning but instead learns to map between views
Cross-View 
Transformer
Map-view
embedding
Camera-aware
embedding
…
Figure 1. We introduce an architecture for perception in a map-
view frame from multiple views. Our model builds a map-view
representation by cross-attending to image features. A camera-
aware positional embedding can geometrically link up the camera
and map-views.
through a geometry-aware positional embedding.
Multi-
head attention then learns to map features from camera-
view into a canonical map-view representation using a
learned map-view positional embedding. We learn a single
map-view positional embedding for all cameras and per-
form attention across all views. The model thus learns to
link up different map locations to both cameras and loca-
tions within each camera. Our cross-view transformer re-
ﬁnes the map-view embedding through multiple attention
and MLP blocks. The cross-view transformer allows the
network to learn any geometric transformation implicitly
and directly from data.
It learns an implicit estimate of
depth through the camera-dependent map-view positional
embedding by performing the downstream task as accu-
rately as possible.
The simplicity of our model is a key strength. The model
performs at state-of-the-art on the nuScenes [3] dataset for
vehicle and road segmentation in the map-view and com-
fortably runs in real-time (35 FPS) on a single RTX 2080
Ti GPU. The model is easy to implement and trains within
1
arXiv:2205.02833v1  [cs.CV]  5 May 2022
### Page 2

32 GPU hours. The learned attention mechanism learns ac-
curate correspondences between camera and map-view di-
rectly from data.
2. Related Works
Map-view semantic segmentation lies at the intersection
of 3D recognition, depth estimation, and mapping.
Monocular 3D object detection.
Monocular detection
aims to ﬁnd objects in a scene, estimate their real-world
size, orientation, and placement in the 3D scene.
Most
common approaches reduce the problem to 2D object de-
tection and infer monocular depth [25, 48]. CenterNet [48]
directly predicts depth for each image coordinate.
ROI-
10D [25] lifts 2D detections into 3D using depth estimates
then regresses 3D bounding boxes.
Psuedo-lidar based
approaches [24, 44, 45, 46] project to 3D points using a
depth estimate and leverage 3D point based architectures
(e.g. [18, 30, 43]) with 2D labels. This family of algorithms
directly beneﬁts from advances in monocular depth estima-
tion and 3D vision.
Monocular 3D object detection is both easier and harder
than mapping from multiple cameras. The overall problem
setup deals with just a single camera and does not need
to merge multiple sources of inputs. However, it strongly
relies on a good explicit monocular depth estimate, which
may be harder to obtain.
Depth estimation.
Depth is a core ingredient in many
multi-view mapping approaches.
Classic structure-from-
motion approaches [1, 7, 20, 35, 38] leverage epipolar ge-
ometry and triangulation to explicitly compute camera ex-
trinsics and depth.
Stereo matching ﬁnds corresponding
pixels, from which depth can be explicitly computed [15].
Recent deep learning approaches directly regress depth
from images [6, 8, 11, 12, 31, 47].
While convenient, explicit depth is challenging to utilize
for downstream tasks. It is camera-dependent and requires
an accurate calibration and fusion of multiple noisy esti-
mates. Our approach side-steps explicit depth estimation
and instead allows an attention mechanism with positional
embedding to take its place. Our cross-view transformer
learns to reproject camera views into a common map repre-
sentation as part of training.
Semantic mapping in the map-view.
Driven by ever
larger 3D recognition datasets [3, 5, 10, 13, 39], a number
of works have focused on perception in the map-view. This
problem is particularly challenging as the inputs and out-
puts lie in different coordinate frames. Inputs are recorded
in calibrated camera views, outputs are rasterized onto a
map. Most prior works differ in the way the transformation
is modeled. One common technique is to assume the scene
is mostly planar and represent the image to map-view trans-
formation as a simple homography [2, 9, 16, 22, 36, 49].
A second family of methods directly produces map-view
predictions from input images, with no explicit geometric
modeling. VED [23] uses a Variational Auto Encoder [17]
to produce a semantic occupancy grid from a single monoc-
ular camera-view.
Closely related in spirit to our method, VPN [28] learns a
common feature representation across multiple views with
their proposed view relation module - an MLP that outputs
map-view features from inputs across all views. Both VED
and VPN show carefully-designed networks trained with
sufﬁcient training data can jointly learn the map-view trans-
formation and perform prediction. However, these methods
do suffer certain drawbacks as they do not model the ge-
ometric structure of the scene. They forgo the inherit in-
ductive biases contained in a calibrated camera setup and
instead need to learn an implicit model of camera calibra-
tion baked into the network weights. Our cross-view trans-
former instead uses positional embeddings derived from
calibrated camera intrinsics and extrinsics. The transformer
can learn a camera-calibration-dependent mapping akin to
raw geometric transformations.
Most recently, top-performing methods returned back to
explicit geometric reasoning [14, 27, 29, 32, 33, 34]. Ortho-
graphic Feature Transform (OFT) [33] creates a map-view
intermediate representation from a monocular image by av-
erage pooling image features from the 2D projection that
corresponds with the pillar in map-view. This pooling oper-
ation foregoes an explicit depth estimate and instead aver-
ages all possible image locations a map-view object could
take. Lift-Splat-Shoot (LSS) [29] constructs an intermedi-
ate map-view representation in a similar fashion. However,
they allow the model to learn a soft depth estimate and av-
erage across different bins using a learned depth-estimate-
dependent weight. Their downstream decoder can account
for uncertainty in depth. This weighted averaging operation
closely mimics the attention used in a transformer. How-
ever, their “attention weights” are derived from geometric
principles and not learned from data.
The original Lift-
Splat-Shoot approach considers multiple views within a sin-
gle timestep. Recent methods have extended this further to
take aggregate features from previous timesteps [34], and
use multi-view, multi-timestep observations to do motion
forecasting [14].
In this work, we show that implicit geometric reasoning
performs as well as explicit geometric models. The added
beneﬁt of our implicit handling of geometry is an improve-
ment in inference speed compared to explicit models. We
simply learn a set of positional embeddings, and attention
will reproject the camera to map-view.
2
### Page 3

query
Cross
attention
Multi-camera Images
Image features  
…
Positional 
embedding
Conv
…
Map
embedding
Decoder
Encoder
Cross
attention
Conv
Figure 2. An overview of our proposed architecture for map-view segmentation. For each image, we extract image features across multiple
scales. Using known camera pose and intrinsics, we construct a camera-aware positional embedding. We learn a map-view positional
embedding that aggregates information from all views through a series of cross attention layers. Each cross-attention reﬁnes the map-view
positional embedding and queries more accurate image locations.
3. Cross-view transformers
In this section, we introduce our proposed architecture
for semantic segmentation in the map-view from multiple
camera views. In this task, we are given a set of n monoc-
ular views (Ik, Kk, Rk, tk)n
k=1 consisting of input image
Ik ∈RH×W ×3, camera intrinsics Kk ∈R3×3, and ex-
trinsic rotation Rk ∈R3×3 and translation tk ∈R3 relative
to the center of the ego-vehicle. Our goal is to learn an ef-
ﬁcient model to extract information from the multiple cam-
era views in order to predict a binary semantic segmentation
mask y ∈{0, 1}h×w×C in the orthographic map-view co-
ordinate frame.
We design a simple, yet effective encoder-decoder archi-
tecture for map-view semantic segmentation. An image-
encoder produces a multi-scale feature representation of
each input image. A cross-view cross-attention mechanism
then aggregates multi-scale features into a shared map-view
representation. The cross-view attention relies on a posi-
tional embedding that is aware of the geometric structure
of the scene and learns to match up camera-view and map-
view locations. All cameras share the same image-encoder,
but use a positional embedding dependent on their individ-
ual camera calibration. Finally, a lightweight convolutional
decoder upsamples the reﬁned map-view embedding and
produces the ﬁnal segmentation output. The entire network
is end-to-end differentiable and learned jointly. Figure 2
shows an overview of the full architecture.
In Section 3.1, we ﬁrst present the core cross-view at-
tention mechanism and positional embedding that underlies
our entire architecture. Section 3.2 then combines multiple
cross-view attention layers into the ﬁnal map-view segmen-
tation model.
3.1. Cross-view attention
The goal of cross-view attention is to link up a map-view
representation with image-view features. For any world co-
ordinate x(W ) ∈R3, the perspective transformation de-
scribes its corresponding image coordinate x(I) ∈R3:
x(I) ≃KkRk(x(W ) −tk).
(1)
Here, ≃describes equality up to a scale factor, and x(I) =
(·, ·, 1) uses homogeneous coordinates. However, without
an accurate depth estimate in camera view or height-above-
ground estimate in map-view, the world coordinate x(W ) is
ambiguous. We do not learn an explicit estimate of depth
but encode any depth ambiguity in the positional embed-
dings and let a transformer learn a proxy for depth.
We start by rephrasing the geometric relationship be-
tween world and image coordinates in Equation 1 as a co-
sine similarity for use in an attention mechanism.
simk(x(I), x(W )) =
 R−1
k K−1
k x(I)
·
 x(W ) −tk

∥R−1
k K−1
k x(I))∥∥(x(W ) −tk∥. (2)
This similarity still relies on the exact world coordinate
w(W ). Next, we replace all geometric components of this
similarity with positional encodings that can learn both ge-
ometric and appearance features.
Camera-aware positional encoding.
The camera-aware
positional encoding starts from the unprojected image coor-
dinate dk,i = R−1
k K−1
k x(I)
i
for each image coordinate x(I)
i
.
The unprojected image coordinate dk,i describes a direction
vector from the origin tk of camera k to the image plane at
depth 1. The direction vector uses world coordinates.
3
### Page 4

We encode this direction vector dk,i using an MLP
(shared across all k views) into a D-dimensional positional
embedding δk,i ∈RD. We use D = 128 in our experi-
ments. We combine this positional embedding with image
features φk,i in the keys of our cross-view attention mecha-
nism. This allows cross-view attention to use both appear-
ance and geometric cues to reason about correspondences
across the different views.
Next, we show how to build an equivalent representation
for the map-view queries. This embedding can no longer
rely on exact geometric inputs and instead needs to learn ge-
ometric reasoning in consecutive layers of the transformer.
Map-view latent embedding.
The map-view component
of the geometric similarity metric in Equation 2 contains
a world coordinate x(W ) and camera location tk. We en-
code both in a separate positional embedding. We use an
MLP to transform each camera location tk into an embed-
ding τk ∈RD. We build the map-view representation up
over multiple iterations in our transformer. We start with a
learned positional encoding c(0) ∈Rw×h×D. The goal of
the map-view positional encoding is to produce an estimate
of the 3D location of each element of the road. Initially, this
estimate is shared across all scenes and likely learns an av-
erage position and height above the ground plane for each
element of the scene. The transformer architecture then re-
ﬁnes this estimate through multiple rounds of computation,
resulting in new latent embeddings c(1), c(2), . . .. Each po-
sitional embedding is better able to project the map-view
coordinates into a proxy of the 3D environment. Following
the geometric similarity measure in Equation 2, we use the
difference between map-view embeddings c and camera-
location embeddings τk as queries in the transformer.
Cross-view attention.
Our cross-view transformer com-
bines both positional encodings through a cross-view atten-
tion mechanism. We allow each map-view coordinate to
attend one or more image locations. Crucially, not every
map-view location has a corresponding image patch in each
view. Front-facing cameras do not see the back, rear-facing
cameras do not see the front. We allow the attention mecha-
nism to select both camera and location within each camera
when corresponding map-view and camera-view perspec-
tives. To this end, we ﬁrst combine all camera-aware po-
sitional embeddings δ1, δ2, . . . from all views into a single
key vector δ = [δ1, δ2, . . .]. At the same time, we com-
bine all image features φ1, φ2, . . . into a single value vec-
tor φ = [φ1, φ2, . . .]. We combine camera-aware positional
embeddings δ and image features φ to compute attention
keys. Finally, we perform softmax-cross-attention [42] be-
tween keys [δ, φ], values φ, and map-view queries c −τk.
The softmax attention uses a cosine similarity between
keys and queries as a basic building block
sim(δk,i, φk,i, c(n)
j , τk) =
(δk,i + φk,i)·

c(n)
j
−τk

∥δk,i + φk,i∥∥c(n)
j
−τk∥
. (3)
This cosine similarity follows the geometric interpretation
in Equation 2. This cross-view attention forms the basic
building block of our cross-view transformer architecture.
3.2. A cross-view transformer architecture
The ﬁrst stage of the network builds up a camera-view
representation for each input image. We feed each image Ii
into feature extractor (EfﬁcientNet-B4 [40]) and get a multi-
resolution patch embedding {φ1
1, φ2
1, . . . , φR
n }, where R is
the number of resolutions we consider. We found R = 2
resolutions to produce sufﬁciently accurate results. We pro-
cess each resolution separately. We start from the lowest
resolution and project all image features into map-view us-
ing cross-view attention. We then reﬁne the map-view em-
bedding and repeat the process for higher resolutions. Fi-
nally, we use three up-convolutional layers to produce the
full resolution output.
A detailed overview of this architecture is shown in Fig-
ure 2. The ﬁnal network is end-to-end trainable. We train all
layers using ground truth semantic map-view annotations
and a focal loss [19].
4. Implementation Details
Architecture.
We use (and ﬁne-tune) a pre-trained
EfﬁcientNet-B4 [40] to compute image features at two dif-
ferent scales - (28, 60) and (14, 30), which correspond to
a 8x and 16x downscaling, respectively. The initial map-
view positional embedding is a tensor of learned parame-
ters w × h × D, where D = 128. For computational ef-
ﬁciency, we choose w = h = 25 as the cross-attention
function grows quadratically with grid size. The encoder
consists of two cross-attention blocks: one for each scale of
patch features. We use multi-head attention with 4 heads
and an embedding size dhead = 64. The decoder consists
of three (bilinear upsample + conv) layers to upsample the
latent representation to the ﬁnal output size. Each upsam-
pling layer increases the resolution by a factor of 2 up to a
ﬁnal output resolution of 200 × 200. This corresponds to a
100 × 100 meter area centered around the ego-vehicle.
Training.
We train all models using a focal loss [19], with
a batch size of 4 (per GPU) for 30 epochs. We optimize us-
ing the AdamW [21] optimizer with the one-cycle learning
rate scheduler [37]. Training converges within 8 hours on a
4 GPU machine.
4
### Page 5

Setting 1 Setting 2 #Params (M) FPS
PON [32]
24.7
-
38
30
VPN [28]
25.5
-
18
-
STA [34]
36.0
-
-
-
Lift-Splat [29]
-
32.1
14
25
FIERY [14]
37.7
35.8
7
8
Ours
37.5
36.0
5
35
Table 1. Vehicle map-view segmentation on nuScenes. Setting
1 refers to the 100m×50m at 25cm resolution setting proposed
by Roddick et al. [32]. Setting 2 refers to the 100m×100m at
50cm resolution setting proposed by Philion and Fidler [29]. Both
settings evaluate the Intersection over Union (IoU) metric. Higher
is better. For a fair comparison, we use single-timestep models
only. In particular, we compare to FIERY static [14]. In both
settings, our cross-view transformer performs at the state-of-the-
art with a smaller model and runs 4.5× faster during inference.
5. Results
We evaluate our cross-view transformer on vehicle and
road map-view semantic segmentation on the nuScenes [3]
and Argoverse [4] datasets.
Dataset.
The nuScenes [3] dataset is a collection of 1000
diverse scenes collected over a variety of weathers, time-
of-day, and trafﬁc conditions. Each scene lasts 20 seconds
and contains 40 frames for a total of 40k total samples in
the dataset. The recorded data captures a full 360° view
around the ego-vehicle and is composed of 6 camera views.
Each camera view has calibrated intrinsics K and extrinsics
(R, t) at every timestep. We resize every image to 224 ×
448 unless speciﬁed otherwise. The Argoverse [4] dataset
contains 10k total frames.
Vehicles and other objects in the scene are tracked across
frames and annotated with 3D bounding boxes using Li-
DAR data. Using the pose of the ego-vehicle, we generate
the ground-truth labels y, a binary vehicle occupancy mask
rendered at a resolution of (200, 200) by orthographically
projecting 3D box annotations onto the ground plane, fol-
lowing standard practice [14, 29].
Evaluation.
There are two commonly used evaluation
settings for map-view vehicle segmentation. Setting 1 uses
a 100m×50m area around the vehicle and samples a map
at a 25cm resolution. The setting, popularized by Roddick
et al. [32], serves as the main comparison to prior work.
Setting 2 [29] uses a 100m×100m area around the vehicle,
with a 50cm sampling resolution. This setting was popular-
ized by Philion and Fidler [29] and serves as a comparison
to Lift-Splat-Shoot [29] and FIERY [14]. We use Setting 2
for all ablations. In both settings, we use the Intersection-
over-Union (IoU) score between the model predictions and
Vehicle
Driveable Area
OFT [33]
30.1
71.7
Lift-Splat [29]
32.1
72.9
Ours
36.0
74.3
Monolayout [26]
32.1
58.3
PON [32]
31.4
65.4
Ours
35.2
73.6
Table 2. Additional comparison with models that perform map-
view segmentation for vehicles and driveable area. The top and
bottom rows correspond to on nuScenes [3] setting 2 and Argov-
erse [4] dataset respectively.
the ground truth map-view labels as the main performance
measure. We additionally report inference speeds measured
on an RTX 2080 Ti GPU.
5.1. Comparison to prior work
We compare our model to the ﬁve most competitive prior
approaches on online mapping. For a fair comparison, we
use single-timestep models only and do not consider tempo-
ral models. We compare to Pyramid Occupancy Networks
(PON) [32], Orthographic Feature Transform (OFT) [33],
View Parsing Network (VPN) [28], Spatio-temporal Aggre-
gation (STA) [34], Lift-Splat-Shoot [29], and FIERY [14].
PON, VPN, STA only report numbers in Setting 1, while
Lift-Splat-Shoot only uses Setting 2.
In both settings, our cross-view transformer and FIERY
outperform all alternative approaches by a signiﬁcant mar-
gin. Our cross-view transformer and FIERY perform com-
parably.
We have a slight edge in Setting 2, FIERY in
Setting 1. The main advantage of our model is simplic-
ity and inference speed, along with the accompanying edge
in model size.
Our model trains signiﬁcantly faster (32
GPU hours vs 96 GPU hours) and performs 4× faster infer-
IoU
No camera-aware embedding δ
31.0
No image features φ in attention
33.2
No map-view embedding reﬁnement
33.6
Full model
36.0
Table 3. Ablations of the cross-view attention mechanism. The
ﬁrst row compares to a model that does not use camera-aware po-
sitional embedding thus only uses image features as attention keys.
The second row does not use any image features in the keys of the
attention mechanism. The third row uses the full attention compu-
tation in camera-view but does not reﬁne the map-view positional
embedding. All partial models degrade reasonably and perform
below the full model.
5
### Page 6

ence. We intentionally use the same image feature extractor
(EfﬁcientNet-B4) [40] and similar decoder architecture as
FIERY. This suggests our cross-view transformer is capa-
ble of combining features from multiple views in a more
efﬁcient manner.
5.2. Ablations of cross-view attention
The core ingredient of our approach is the cross-view
attention mechanism. It combines camera-aware embed-
dings and image features as keys and learned map-view po-
sitional embeddings as queries. The map-view embeddings
are allowed to update across multiple iterations, while the
camera-aware embeddings contain some geometric infor-
mation. Table 3 compares the impact of each of the compo-
nents of the attention mechanism on the resulting map-view
segmentation system. For each ablation, we trained a model
from scratch using equivalent experimental settings, chang-
ing a single component at the time.
The most important component of our system is the
camera-aware positional embedding. It bestows the atten-
tion mechanism with the ability to reason about the geo-
metric layout of the scene. Without it, attention has to rely
on the image feature to reveal its own location. It is possi-
ble for the network to learn this localization due to the size
of the receptive ﬁeld and zero padding around the boundary
of the image. However, an image feature alone struggles to
properly link up map-view and camera-view perspectives.
It also needs to explicitly infer the direction each image is
facing to disambiguate different views. On the other hand, a
purely geometric camera-aware positional embedding alone
is also insufﬁcient. The network likely uses both semantic
and geometric cues to align map-view and camera-view, es-
pecially after the reﬁnement of the map-view embedding.
Finally, using a single ﬁxed map-view embedding also de-
grades the performance of the model. The ﬁnal model per-
forms best with all its attention components.
Method
IoU
None
31.0
Learned per camera
34.4
Camera-aware + Random Fourier
35.8
Camera-aware + Linear Projection
36.0
Table 4. Ablations of the camera-aware positional embeddings.
The ﬁrst row compares to a model that does not use camera-aware
positional embedding thus only uses image features as attention
keys. The second row uses a learned embedding for each camera.
The third row uses a camera-aware positional embedding with a
random Fourier projection. The last row uses a camera-aware po-
sitional embedding with a linear projection (default).
0
25
50
75
Minimum distance (m)
0
10
20
30
IoU
Ours
FIERY
Figure 3. A comparison of model performance vs distance to the
camera. Each entry shows the average intersection over union ac-
curacy for annotations that are at least distance d away.
5.3. Camera-aware positional embeddings
As we have previously seen, the camera-aware positional
embedding plays a major role in the success of the cross-
view transformer. Table 4 compares different choices for
this embedding. We ablate just the positional embedding
and keep all other model and training parameters ﬁxed.
Not using any positional embedding performs poorly.
The attention mechanism has a hard time localizing features
and identifying cameras. A learned embedding per camera
performs surprisingly well. This is likely because the cam-
era calibration stays mostly static and a learned embedding
simply bakes in all geometric information. A camera-aware
embedding with either a linear or Random Fourier projec-
tion [41] performs best. This should not come as a surprise
as both can learn a compact embedding that directly cap-
tures the geometry of the scene.
5.4. Accuracy vs distance
Next, we evaluate how well our model performs as the
distance to the ego-vehicle increases. For this experiment,
we measure the intersection-over-union accuracy, but ig-
0
1
2
3
20
25
30
35
# Cameras Dropped
IoU
Figure 4. Degradation of our model as we randomly drop out
m ∈{0, 1, 2, 3} cameras. The models performance drops linearly
as the observed area shrinks roughly linearly with the number of
cameras removed.
6
### Page 7

Figure 5. Qualitative results on scenes with varying degrees of occlusion. Left shows the six camera views surrounding the vehicle. The top
3 views are front-facing, the bottom 3 views back-facing. On the right is our predicted map-view segmentation for vehicles and driveable
area. Second from the right is the ground truth segmentation for reference. The ego-vehicle is located at the center of the map.
nore all predictions that are closer than a certain distance
to the ego-vehicle. Figure 3 compares to our closest com-
petitor FIERY.
Both models have close to identical error modes. As the
distance to the camera increases, the models get less ac-
curate. This is easiest explained through actual qualitative
results in Figure 5. Farther away vehicles are often (par-
tially) occluded and thus much harder to detect and seg-
ment. Our approach degrades slower for close-by distances,
but slightly under-performs FIERY at longer ranges.
Partially occluded far-away samples have fewer corre-
sponding image features, thus learning a mapping from
map-view to camera-view directly is harder: There is less
training data and fewer geometric priors to rely upon for
our model. We anticipate more data to make up for this
difference.
7
### Page 8

Figure 6. Visualization of cross-view attention. We compute attention from a point in map-view coordinates and visualize the corresponding
attention values of the front camera view. Note how the network learns geometric correspondences through this attention mechanism.
5.5. Robustness to sensor dropout
We take a model trained on all six inputs and evaluate
the intersection over union (IoU) metric by randomly drop-
ping m cameras for each sample in the validation set. Fig-
ure 4 shows how the performance decreases linearly with
the number of cameras dropped. This is quite intuitive as
different cameras only overlap marginally. Thus each re-
moved camera reduces the visible area linearly and drops
the performance in the unobserved area.
Note that the
transformer-based model is generally quite robust to this
camera dropout and the overall performance does not de-
grade beyond unobserved parts of the scene.
5.6. Qualitative Results
Figure 5 shows qualitative results on a variety of scenes.
For each row, we show the six input camera views and the
predicted map-view segmentation along with the ground
truth segmentation. Our presented method can accurately
segments nearby vehicles, but does not sense far away or
occluded vehicles well.
5.7. Geometric reasoning in cross-view attention
Our quantitative experiments indicate that cross-view at-
tention can learn some geometric reasoning. In Figure 6,
we visualize the image-view attention for several points in
the map-view. Each point corresponds to part of a vehi-
cle. From qualitative evidence, the attention mechanism can
highlight closely corresponding map-view and camera-view
locations.
6. Conclusion
We present a novel map-view segmentation approach
based on a cross-view transformer architecture built on top
of camera-aware positional embeddings. The proposed ap-
proach achieves state-of-the-art performance, is simple to
implement, and runs in real time.
Acknowledgements.
This material is based upon work
supported by the National Science Foundation under Grant
No. IIS-1845485 and IIS-2006820.
8
### Page 9

References
[1] Sameer Agarwal, Yasutaka Furukawa, Noah Snavely, Ian Si-
mon, Brian Curless, Steven M Seitz, and Richard Szeliski.
Building rome in a day. Communications of the ACM, 2011.
2
[2] Syed Ammar Abbas and Andrew Zisserman. A geometric
approach to obtain a bird’s eye view from an image. In ICCV
Workshops, 2019. 1, 2
[3] Holger Caesar, Varun Bankiti, Alex H. Lang, Sourabh Vora,
Venice Erin Liong, Qiang Xu, Anush Krishnan, Yu Pan, Gi-
ancarlo Baldan, and Oscar Beijbom.
nuScenes: A multi-
modal dataset for autonomous driving. In CVPR, 2020. 1, 2,
5
[4] Ming-Fang Chang, John Lambert, Patsorn Sangkloy, Jag-
jeet Singh, Slawomir Bak, Andrew Hartnett, De Wang, Peter
Carr, Simon Lucey, Deva Ramanan, et al. Argoverse: 3d
tracking and forecasting with rich maps. In CVPR, 2019. 5
[5] Marius Cordts, Mohamed Omran, Sebastian Ramos, Timo
Scharw¨achter, Markus Enzweiler, Rodrigo Benenson, Uwe
Franke, Stefan Roth, and Bernt Schiele.
The cityscapes
dataset. In CVPRW, 2015. 2
[6] David Eigen, Christian Puhrsch, and Rob Fergus. Depth map
prediction from a single image using a multi-scale deep net-
work. NeurIPS, 2014. 2
[7] Jan-Michael Frahm, Pierre Fite-Georgel, David Gallup, Tim
Johnson, Rahul Raguram, Changchang Wu, Yi-Hung Jen,
Enrique Dunn, Brian Clipp, Svetlana Lazebnik, et al. Build-
ing rome on a cloudless day. In ECCV, 2010. 2
[8] Huan Fu, Mingming Gong, Chaohui Wang, Kayhan Bat-
manghelich, and Dacheng Tao. Deep ordinal regression net-
work for monocular depth estimation. In CVPR, 2018. 2
[9] Noa Garnett, RaﬁCohen, Tomer Pe’er, Roee Lahav, and Dan
Levi. 3d-lanenet: end-to-end 3d multiple lane detection. In
ICCV, 2019. 2
[10] Andreas Geiger, Philip Lenz, and Raquel Urtasun. Are we
ready for autonomous driving? The KITTI vision benchmark
suite. In CVPR, 2012. 2
[11] Cl´ement Godard, Oisin Mac Aodha, and Gabriel J Bros-
tow.
Unsupervised monocular depth estimation with left-
right consistency. In CVPR, 2017. 2
[12] Cl´ement Godard, Oisin Mac Aodha, Michael Firman, and
Gabriel J Brostow. Digging into self-supervised monocular
depth estimation. In CVPR, 2019. 2
[13] John Houston, Guido Zuidhof, Luca Bergamini, Yawei
Ye, Long Chen, Ashesh Jain, Sammy Omari, Vladimir
Iglovikov, and Peter Ondruska. One thousand and one hours:
Self-driving motion prediction dataset. In CoRL, 2021. 2
[14] Anthony Hu, Zak Murez, Nikhil Mohan, Sof´ıa Dudas, Jef-
frey Hawke, Vijay Badrinarayanan, Roberto Cipolla, and
Alex Kendall.
FIERY: Future instance segmentation in
bird’s-eye view from surround monocular cameras. In ICCV,
2021. 1, 2, 5
[15] Takeo Kanade and Masatoshi Okutomi. A stereo matching
algorithm with an adaptive window: Theory and experiment.
TPAMI, 1994. 1, 2
[16] Youngseok Kim and Dongsuk Kum. Deep learning based
vehicle position and orientation estimation via inverse per-
spective mapping image. In IV, 2019. 1, 2
[17] Diederik P Kingma and Max Welling. Auto-encoding varia-
tional bayes. ICLR, 2014. 2
[18] Alex H Lang, Sourabh Vora, Holger Caesar, Lubing Zhou,
Jiong Yang, and Oscar Beijbom. Pointpillars: Fast encoders
for object detection from point clouds. In CVPR, 2019. 2
[19] Tsung-Yi Lin, Priya Goyal, Ross Girshick, Kaiming He, and
Piotr Doll´ar. Focal loss for dense object detection. In CVPR,
2017. 4
[20] H Christopher Longuet-Higgins. A computer algorithm for
reconstructing a scene from two projections. Nature, 1981.
1, 2
[21] Ilya Loshchilov and Frank Hutter. Decoupled weight decay
regularization. In ICLR, 2017. 4
[22] Abdelhak Loukkal, Yves Grandvalet, Tom Drummond, and
You Li. Driving among ﬂatmobiles: Bird-eye-view occu-
pancy grids from a monocular camera for holistic trajectory
planning. In WACV, 2021. 2
[23] Chenyang Lu, Marinus Jacobus Gerardus van de Molen-
graft, and Gijs Dubbelman.
Monocular semantic occu-
pancy grid mapping with convolutional variational encoder–
decoder networks. Robotics and Automation Letters, 2019.
2
[24] Xinzhu Ma, Zhihui Wang, Haojie Li, Pengbo Zhang, Wanli
Ouyang, and Xin Fan. Accurate monocular 3d object detec-
tion via color-embedded 3d reconstruction for autonomous
driving. In ICCV, 2019. 2
[25] Fabian Manhardt, Wadim Kehl, and Adrien Gaidon. Roi-
10d: Monocular lifting of 2d detection to 6d pose and metric
shape. In CVPR, 2019. 2
[26] Kaustubh Mani, Swapnil Daga, Shubhika Garg, Sai Shankar
Narasimhan, Madhava Krishna, and Krishna Murthy Jataval-
labhula. Monolayout: Amodal scene layout from a single
image. In WACV, 2020. 5
[27] Zak Murez, Tarrence van As, James Bartolozzi, Ayan Sinha,
Vijay Badrinarayanan, and Andrew Rabinovich. Atlas: End-
to-end 3d scene reconstruction from posed images. In ECCV,
2020. 2
[28] Bowen Pan, Jiankai Sun, Ho Yin Tiga Leung, Alex Ando-
nian, and Bolei Zhou.
Cross-view semantic segmentation
for sensing surroundings. Robotics and Automation Letters,
2020. 2, 5
[29] Jonah Philion and Sanja Fidler. Lift, splat, shoot: Encoding
images from arbitrary camera rigs by implicitly unprojecting
to 3d. In ECCV, 2020. 1, 2, 5
[30] Charles R Qi, Hao Su, Kaichun Mo, and Leonidas J Guibas.
Pointnet: Deep learning on point sets for 3d classiﬁcation
and segmentation. In CVPR, 2017. 2
[31] Ren´e Ranftl,
Katrin Lasinger,
David Hafner,
Konrad
Schindler, and Vladlen Koltun. Towards robust monocular
depth estimation: Mixing datasets for zero-shot cross-dataset
transfer. TPAMI, 2020. 2
[32] Thomas Roddick and Roberto Cipolla. Predicting semantic
map representations from images using pyramid occupancy
networks. In CVPR, 2020. 2, 5
[33] Thomas Roddick, Alex Kendall, and Roberto Cipolla. Ortho-
graphic feature transform for monocular 3d object detection.
BMVC, 2019. 2, 5
[34] Avishkar Saha, Oscar Mendez, Chris Russell, and Richard
Bowden. Enabling spatio-temporal aggregation in birds-eye-
view vehicle estimation. In ICRA, 2021. 2, 5
[35] Johannes
Lutz
Sch¨onberger
and
Jan-Michael
Frahm.
9
### Page 10

Structure-from-motion revisited. In CVPR, 2016. 1, 2
[36] Sunando Sengupta, Paul Sturgess, L’ubor Ladick`y, and
Philip HS Torr. Automatic dense visual semantic mapping
from street-level imagery. In RSS, 2012. 2
[37] Leslie N Smith and Nicholay Topin.
Super-convergence:
Very fast training of neural networks using large learning
rates.
In Artiﬁcial intelligence and machine learning for
multi-domain operations applications, volume 11006, page
1100612. International Society for Optics and Photonics,
2019. 4
[38] Noah Snavely, Steven M Seitz, and Richard Szeliski. Photo
tourism: exploring photo collections in 3d. In SIGGRAPH,
2006. 2
[39] Pei Sun, Henrik Kretzschmar, Xerxes Dotiwalla, Aurelien
Chouard, Vijaysai Patnaik, Paul Tsui, James Guo, Yin Zhou,
Yuning Chai, Benjamin Caine, et al. Scalability in perception
for autonomous driving: Waymo open dataset. In CVPR,
2020. 2
[40] Mingxing Tan and Quoc Le. Efﬁcientnet: Rethinking model
scaling for convolutional neural networks. In ICML, 2019.
4, 6
[41] Matthew Tancik, Pratul P Srinivasan, Ben Mildenhall, Sara
Fridovich-Keil, Nithin Raghavan, Utkarsh Singhal, Ravi Ra-
mamoorthi, Jonathan T Barron, and Ren Ng. Fourier features
let networks learn high frequency functions in low dimen-
sional domains. NeurIPS, 2020. 6
[42] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszko-
reit, Llion Jones, Aidan N Gomez, Łukasz Kaiser, and Illia
Polosukhin. Attention is all you need. In NeurIPS, 2017. 4
[43] Sourabh Vora, Alex H Lang, Bassam Helou, and Oscar Bei-
jbom. Pointpainting: Sequential fusion for 3d object detec-
tion. In CVPR, 2020. 2
[44] Yan Wang, Wei-Lun Chao, Divyansh Garg, Bharath Hariha-
ran, Mark Campbell, and Kilian Q Weinberger. Pseudo-lidar
from visual depth estimation: Bridging the gap in 3d object
detection for autonomous driving. In CVPR, 2019. 2
[45] Xinshuo Weng and Kris Kitani. Monocular 3d object de-
tection with pseudo-lidar point cloud. In ICCV Workshops,
2019. 2
[46] Bin Xu and Zhenzhong Chen. Multi-level fusion based 3d
object detection from monocular images. In CVPR, 2018. 2
[47] Tinghui Zhou, Matthew Brown, Noah Snavely, and David G
Lowe. Unsupervised learning of depth and ego-motion from
video. In CVPR, 2017. 2
[48] Xingyi Zhou, Dequan Wang, and Philipp Kr¨ahenb¨uhl. Ob-
jects as points. In arXiv preprint arXiv:1904.07850, 2019.
2
[49] Minghan Zhu, Songan Zhang, Yuanxin Zhong, Pingping Lu,
Huei Peng, and John Lenneman. Monocular 3d vehicle de-
tection using uncalibrated trafﬁc cameras through homogra-
phy. IROS, 2021. 2
10