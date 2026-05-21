# MonoDepth2 Monocular Self-Supervised Depth Estimation

**Source**: arxiv PDF, 9 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Self-Improving Visual Odometry
Daniel DeTone
Magic Leap, Inc.
Sunnyvale, CA
ddetone@magicleap.com
Tomasz Malisiewicz
Magic Leap, Inc.
Sunnyvale, CA
tmalisiewicz@magicleap.com
Andrew Rabinovich
Magic Leap, Inc.
Sunnyvale, CA
arabinovich@magicleap.com
Abstract
We propose a self-supervised learning framework that
uses unlabeled monocular video sequences to generate
large-scale supervision for training a Visual Odometry
(VO) frontend, a network which computes pointwise data
associations across images. Our self-improving method en-
ables a VO frontend to learn over time, unlike other VO and
SLAM systems which require time-consuming hand-tuning
or expensive data collection to adapt to new environments.
Our proposed frontend operates on monocular images and
consists of a single multi-task convolutional neural network
which outputs 2D keypoints locations, keypoint descriptors,
and a novel point stability score. We use the output of VO
to create a self-supervised dataset of point correspondences
to retrain the frontend. When trained using VO at scale on
2.5 million monocular images from ScanNet, the stability
classiﬁer automatically discovers a ranking for keypoints
that are not likely to help in VO, such as t-junctions across
depth discontinuities, features on shadows and highlights,
and dynamic objects like people.
The resulting frontend
outperforms both traditional methods (SIFT, ORB, AKAZE)
and deep learning methods (SuperPoint and LF-Net) in a
3D-to-2D pose estimation task on ScanNet.
1. Introduction
Simultaneous Localization and Mapping (SLAM) is an
important problem in robotics, autonomous vehicles and
augmented reality. Visual SLAM is one ﬂavor of SLAM
which operates on visual data, typically gray-scale or color
image sequences. Visual Odometry (VO) is similar to Vi-
sual SLAM but is less complicated because it only opti-
mizes over a recent set of observations, not requiring addi-
tional subsystems such as a re-localization and loop closure.
There are many excellent Visual SLAM and VO sys-
tems that exist today, but SLAM still struggles in many sce-
narios involving robustness, scalability and life-long oper-
ation. This is described in detail in Cadena et al.’s histori-
cal overview of SLAM [4]. Additionally, the constraints of
augmented reality wearable devices and consumer robotics
require SLAM algorithms be computationally lightweight
Keypoint 2D 
Locations
Keypoint 
Stability
Keypoint 
Descriptors
ConvNet
Convolutional 
Frontend 
[see Section 3]
VO Backend 
[see Section 4]
Point Tracks
3D Points
stable 
unstable 
ignore
Input Monocular 
Sequence
#1
#3
#2
#1
#1
#1
#2
#2
#2
#3
#3
#3
#4
#4
#4
#1
#2
#3
6DOF Trajectory
Labeled Point Tracks
a)
b)
c)
ConvNet
Self-Supervision 
from VO 
[see Section 5]
Supervision Signal
Figure 1. Self-Improving Visual Odometry. a) Our Convolu-
tional Frontend computes points and descriptors for each image in
a monocular sequence to form point tracks. b) The VO Backend
performs Bundle Adjustment to upgrade the tracks to 3D points
and to classify their stability based on re-projection error. c) Stable
3D points act as supervision signal when we re-train the ConvNet.
and at the same time adaptable to new environments. To
achieve this, a new type of SLAM system is required–as de-
scribed in Spatial AI by Andrew Davison [8]–an approach
which can use its own model of the world to self-supervise
its ability to compute correspondence across time.
To overcome these challenges, we propose to use the
temporal consistency of sequences for self-improvement.
We combine a learnable frontend with a VO style optimiza-
tion over sparse 2D keypoints which have been tracked over
time. The key idea behind Self-Improving Visual Odometry
is: the best points for a VO system are those which can be
stably tracked and matched over many views.
1
arXiv:1812.03245v1  [cs.CV]  8 Dec 2018
### Page 2

Pose
Learnable 
Frontend
Image
Pose
Supervisory 
Signal
Self-Supervised VO (ours)
Learnable 
Frontend
Image
Supervisory Signal
Externally Supervised VO
Image
Traditional VO
External 
Ground Truth
Handcrafted 
Frontend
Pose c)
b)
a)
Backend
Backend
Backend
Figure 2. Visual Odometry Paradigms. a) A Traditional VO System uses a hand-crafted frontend combined with a backend to compute
pose for an image. b) An Externally Supervised VO system is able to improve with more data, but requires an external mechanism to
provide ground-truth data, which can be expensive. c) Self-Supervised VO uses its own outputs as supervision for the learnable frontend.
A visual overview of the paper is shown in Figure 1. We
discuss our network architecture in Section 3, the backend
optimization of VO in Section 4, VO supervision in Sec-
tion 5, pose estimation results in Section 6, and conclude
with discussion in Section 7.
The contributions of our
work are as follows:
• A novel self-labeling framework which runs VO on the
outputs of a convolutional frontend and classiﬁes their
stability. The stable points are then fed back into the
convolutional frontend and used as supervision to im-
prove the system.
• A novel stability classiﬁer in the frontend which pre-
dicts the stability of points from a single image, and
learns to suppress points which are problematic for
VO, such as points at depth discontinuities and points
on dynamic objects such as people.
2. Related Work
Traditional VO. The traditional approach to visual
odometry [11, 16] is based on handcrafted visual features
(see Figure 2a). To modify or adapt most SLAM/VO sys-
tems based on handcrafted features to different sensors
and environments, practitioners typically inject hand-tuned
heuristics or tune hyper-parameters, often at the expense of
performance in other scenarios. This happens because ex-
isting systems have little to no learned components and that
ground truth data collection for SLAM/VO is very expen-
sive and time-consuming.
Externally Supervised VO. A small number of solu-
tions in recent years such as LIFT [24] and SuperPoint [10]
formulate the task of extracting image features and match-
ing them across time as a learning problem and tackle them
using convolutional neural networks (ConvNets).
These
systems can act as SLAM Frontends – where raw images
are processed and reduced to a set of geometric primi-
tives, which are ready to be optimized by a SLAM Backend
(to concurrently estimate a camera pose and 3D map). In
their formulation as learning problems, these systems can
improve their performance with more data, alleviating the
need for heuristics. However, this is not straightforward
because collecting labeled data is challenging. LIFT, for
example, cleverly leverages the fact it is relatively easy to
run an existing SLAM and Structure-from-Motion (SfM)
systems at large-scale, since most modern systems such as
ORB-SLAM [15] and VisualSfM [23] can be run in real-
time. LF-Net [17] is a powerful method that uses ideas from
reinforcement learning to discover keypoint locations and
relies on external ground truth for camera pose and scene
depths.
SIPS [6] uses a ranking loss to estimate a concise set
of interest points. IMIPS [5] uses a similar approach to
SIPS for learning implicit keypoint correspondence be-
tween pairs of images, without the need for descriptors.
MegaDepth [13] uses SfM combined with semantic seg-
mentation to label a large set of outdoor images. All these
methods rely on external supervision which is problematic
because it introduces a second SLAM system with an ad-
ditional set of limitations and dependencies, which all are
inherited by the learned system (see Figure 2b).
Self-supervised VO. SuperPoint [10] takes a different
approach by self-labeling a large set of images and using
homographies of images to learn correspondence. While
this is a surprisingly powerful technique given its simplicity,
it is limited by its reliance on static images and cannot learn
from real illumination changes and correspondence across
difﬁcult non-planar scenes. The backend in this method
is a simple homography model, where the homographies
are generated synthetically. This method falls into the self-
supervised VO paradigm (see Figure 2c).
Geometric Matching Networks [18] and Deep Image
Homography Estimation [9] use a similar self-supervision
strategy to create training data for estimating image trans-
formations. However, these methods lack interest points
and point correspondences, which are typically required for
doing higher-level computer vision tasks such as SLAM and
SfM.
Learning Stability. In [26], Zhou et al. present an un-
supervised approach for learning monocular depth and rel-
ative pose that does not rely on external ground truth. The
model also predicts an explainability mask, which is simi-
lar to the stability classiﬁer presented in this work because
it discovers dynamic objects like people without explicitly
being trained to do so. It operates on a pair of images, rather
than SuperPointVO which operates on a single image.
2
### Page 3

3. Convolutional Frontend
There are a variety of architectures available which can
be trained to detect keypoints and descriptors. We choose
to base the SuperPointVO architecture off of the Super-
Point [10] architecture because it is simple and works well
in practice. We ﬁrst summarize the SuperPoint architecture
and describe the addition of the stability classiﬁcation head;
then, we describe how this architecture can be used to pro-
duce sparse optical ﬂow tracks.
3.1. SuperPoint Architecture Review
The SuperPoint architecture consists of a ”backbone”
fully convolutional neural network, which maps the in-
put image I ∈RH×W to an intermediate tensor B ∈
RHc×Wc×F with smaller spatial dimension and greater
channel depth (i.e., Hc < H, Wc < W and F > 1). These
shared features are used in all following computation and
account for the majority (roughly 90%) of the system com-
pute. The computation then splits into two heads: a 2D
interest point detector head and descriptor head. The in-
terest point detector head computes X ∈RHc×Wc×65 and
outputs a tensor sized RH×W . The 65 channels correspond
to local, non-overlapping 8 × 8 grid regions of pixels plus
an extra “no interest point” dustbin. The descriptor head
computes D ∈RHc×Wc×D. We use bi-linear interpolation
to sparsely upsample the descriptor ﬁeld at the pixel level
locations given by the interest point detector head.
In our experiments, we use the same backbone as in Su-
perPoint. The encoder has a VGG-like [21] architecture that
has eight 3x3 convolution layers sized 64-64-64-64-128-
128-128-128. Between every two layers there is a 2x2 max
pool layer.
3.2. Stability Classiﬁer Head
The added stability classiﬁer head operates on the in-
termediate features B output by the backbone network. It
computes S ∈RHc×Wc×2. To compute pixel level predic-
tions, the coarse predictions are interpolated with bi-linear
interpolation and followed by channel-wise softmax over
the two output channels to get the ﬁnal stability probability
value. In our experiments, the stability classiﬁer decoder
head has a single 3x3 convolutional layer of 256 units fol-
lowed by a 1x1 convolution layer with 2 units for the binary
classiﬁcation of stable versus not stable.
3.3. Point Tracks
Once trained, the SuperPointVO Frontend can be used to
form sparse optical ﬂow tracks for an image sequence. This
works by associating the points and descriptors in consecu-
tive pairs of images with a “connect-the-dots” algorithm.
In other words, given a set monocular images I =
[I1, I2, . . . IN], where Ii ∈RH×W , we can compute a cor-
responding set of 2D keypoints U = [U1, U2, . . . UN] and
Input
H
1
SuperPoint Network
W
Interpolate
Softmax
Stability Classi!er Head
Conv
Wc
Hc 2
Keypoint 2D 
Locations
Keypoint 
Descriptors
Keypoint 
Stability
Figure 3. Stability Classiﬁer Head. To predict a stability proba-
bility for each keypoint, we augment the SuperPoint network with
an additional decoder head to compute S.
Ui ∈R2×Oi and descriptors D = [D1, D2, . . . DN] and
Di ∈R256×Oi, where Oi is equal to the number of points
detected in the image i.
To match points across a pair of images Ia and Ib, we
take the bi-directional nearest neighbors of the correspond-
ing Da and Db. A bi-directional nearest neighbor match
(dai, dbj), where dai, dbj ∈R256 is one such that the near-
est neighbor match from dai to Db is dbj and the nearest
neighbor match from dbj to Da is dai. This parameter-less
alternative to Lowe’s ratio test [14] helps the algorithm use
as few parameters a possible, and works well in practice. A
second removal of matches is done to remove all matches
such that ||dai −dbj|| > τ where we typically set τ = 0.7.
To form tracks, the same procedure is done for all con-
secutive pairs of images (I1, I2), (I2, I3), . . . , (IN−1, IN).
We found this to be a powerful heuristic in selecting good
tracks, and can qualitatively be seen in Figure 4a.
Once the set of tracks is established, we can treat each
track in the sequence as a single 3D point, and use the tracks
to jointly estimate the 3D scene structure and camera poses.
The following section describes this procedure.
4. VO Backend
A self-supervised Visual SLAM Frontend uses its own
outputs, combined with multiple-view geometry, to create
a supervised training dataset. To achieve invariance to the
non-planarity of the real world, we propose to exploit the
temporal aspect of monocular video and the mostly-rigid
nature of the real world. We call this extension VO Adap-
tation. The key idea of VO Adaptation is to leverage VO
to label which points can be stably tracked over time and
use the stable tracks to learn keypoint correspondence over
many views.
To describe our VO backend and thus the VO Adapta-
tion process, we summarize some multiple-view geometry
concepts in following sections to establish our mathematical
notation. We refer the reader to the Hartley and Zisserman
Multiple View Geometry [12] textbook for more details.
3
### Page 4

4.1. Optimization Variables
In a monocular sequence of N images, the set of camera
poses for the i-th camera are represented by their rotation
and translation (Ri,ti), where Ri ∈SO(3) and ti ∈R3.
For a scene with M 3D points which re-project into
some or all of the N images, each point is represented by
Xj, where Xj ∈R3. There is no 3D prior structure imposed
on the reconstruction, other than the depth regularization
function d(Z) (introduced later) which penalizes point con-
ﬁgurations too close (or behind) or too far from the camera.
The camera intrinsics K is an upper-triangular matrix
made up of focal lengths fx and fy together with the princi-
pal point (cx,cy). While it is possible to optimize over one
K for each image (as is typically done in a SfM pipeline),
our VO backend assumes a single, ﬁxed K.
4.2. Observation Variables
U is the set of 2D point observations, a collection of
N matrices, one for each image. U = [U1, U2, . . . UN] and
Ui ∈R2×Oi, where Oi is equal to the number of 2D ob-
servations in the image i. A single image measurement is
represented by uij ∈R2.
W is the set of observation conﬁdence weights. The
observation conﬁdence weights are used during optimiza-
tion to prioritize more conﬁdence observations over less
conﬁdent ones. Each image has a set of associated scalar
weights W = [W1, W2, . . . WN] where Wi ∈ROi. Each
scalar weight ranges between zero and one, i.e. wij ∈[0, 1].
A is the set of 3D-to-2D association tracks. Since every
3D point Xj in the sparse 3D map is not observed in every
frame due to the moving camera and scene occlusions, we
have a set of 3D-to-2D association vectors for each image
A = [A1, A2, . . . AN], where Ai ∈ZOi. Each association
integer indicates the 3D map point index it corresponds to
and ranges between zero and the total number of points in
the scene, i.e. aij ∈[1, M].
4.3. 3D Projection Model
We use a pinhole camera model for camera projection
which explains how a 3D world point gets projected into a
2D image given the camera pose and the camera intrinsics.
Letting Xj ∈R3 denote the j-th 3D point, (Ri, ti) the i-
th camera pose, K the camera intrinsics, and uij ∈R2 the
corresponding 2D projection:


uij1
uij2
1

∼K[Ri|ti]
Xj
1

.
(1)
The ∼in Equation 1 denotes projective equality. To sim-
plify our calculations, we use a R3 →R2 projection func-
tion Π(X) which performs the 3D to 2D conversion,
Π(


X
Y
Z

)
=
1
Z
X
Y

.
(2)
To measure the quality of the estimated camera poses
and 3D points, we can measure the re-projection of each 3D
point into each camera. We write the squared re-projection
error e2
ij for the j-th 3D point in the i-th image as follows:
e2
ij = ||Π(K(RiXaij + ti)) −uij||2.
(3)
4.4. Depth Regularization
We introduce a depth regularization function d(Z′
ij),
where Z′
ij = [RiXij + tij]3, where [·] means taking the
third component of the vector, which incurs a quadratic
penalty for estimated 3D point depths Z′
ij which are too
close or too far from the camera, parameterized by two
scalars dmin and dmax. It also prevents depths from mov-
ing behind the camera center. We found dmin = 0.1 and
dmax = 5.0 to work well for indoor scenes. The term is:
d(Z′
ij) = max(0, Z′
ij −dmax)2+
min(Z′
ij −dmin, 0)2.
(4)
4.5. Camera Pose and Point Depth Initialization
We initialize each new camera pose (RN+1,tN+1) with
the camera pose from the previous frame (RN,tN). We ini-
tialize new 3D point depths to 1.0. While it is common
for traditional SfM pipeline will initialize the 3D points
depths Z′
ij using linear triangulation methods, we found
that this did not improve our VO results signiﬁcantly and
added more complexity to the system. We found that sim-
ply initializing the point depths to unity depth and adding
the depth regularization term was enough of a prior for the
BA optimization to work well.
4.6. Final Bundle Adjustment Objective
The ﬁnal bundle adjustment objective is the combination
of the re-projection error function e2
ij, the depth regulariza-
tion function, the 2D observation weights wij and a Huber
robust loss function ρ(·) to help deal with outliers. We de-
note the ﬁnal objective function for BA, ΩBA(·), as follows:
Ω(·) =
N
X
i=1
Oi
X
j=1
wijρ
 e2
ij + d(Z′
ij)

.
(5)
{R∗, t∗}N
i=1, X∗= argmin
{R,t}N
i=1,X
Ω({R, t}N
i=1, X|K, U, W, A)
(6)
4
### Page 5

T-junction 
Across Depth
Lighting 
Highlight
Repeated 
Texture
Dynamic 
Person
Lighting 
Re!ection
a)
b)
c)
d)
Figure 4. Labeling points with VO. Five examples of patterns labeled by VO to have a low stability due to ﬁve different effects are shown
in each column. We show a) Sparse point tracks from the convolutional frontend, b) Overhead projection of the computed VO backend
camera pose trajectory and sparse 3D map, c) Re-projection error residual images (red = low error, blue = high error), and d) Labeled point
tracks with stability labels (green = stable, red = unstable, blue = ignore, pink circle = characteristic example of unstable point).
4.7. VO Backend Implementation
The BA optimization is done over a ﬁxed window of the
most recent Nlast = 30 poses, corresponding to about one
second of motion. We use the ceres-solver [1] c++ pack-
age to perform the Levenberg-Marquardt optimization over
Equation 6.
For each new image, we run BA for up to
100 iterations, which on average takes about one second per
frame. Row b in Figure 4 shows some example trajectories
in a jet colormap, where blue is the earlier part of the trajec-
tory, red is the latter part of the trajectory, and black is the
Nlast poses, while the white points show the 3D points Xj.
5. Self-Supervision from VO
We combine the SuperPoint-based VO Frontend de-
scribed in Section 3 with the VO Backend system described
in Section 4 to run on monocular video sequences.
5.1. Labeling Stability
Once VO is complete for a given sequence, the number
of observations and re-projection errors for each 3D point
are used to label stability. If a point is tracked for a reason-
ably long time, we can use its reprojection error to classify it
as stable versus non-stable. Let Tj denote the number of ob-
servations tracked to form a 3D point Xj. Let mean(ej) and
max(ej) be the mean and maximum of the re-projections
respectively into each observed camera. We deﬁne the sta-
bility Sj of that 3D point as:
Sj =





stable,
if (Tj ≥10) and (mean(ej) ≤1)
unstable,
else if (Tj ≥10) and (max(ej) ≥5)
ignore,
otherwise
(7)
In other words, stable points are those which have been
tracked for at least ten frames and have an average re-
projection error less than one pixel. Unstable points are
those which have been tracked for at least ten frames and
have a maximum re-projection error of more than ﬁve pix-
els. The points which do not satisfy these two constraints
are ignored during training–the network can decide to treat
them as stable or unstable as it chooses.
The self-labeling procedure discovers unstable regions
such as t-junctions across depth discontinuities, features on
shadows and highlights, and dynamic objects like people.
See examples of this in Figure 4 row d.
5
### Page 6

H1
H2
Randomly 
Select Pair
Random 
Homography
#1
#1
#1
#2
#2
#2
#3
#3
#3
#4
#4
#1
#2
#3
SuperPointVO
SuperPointVO
Descriptor 
Loss
Keypoint Loss
Stability Loss
Keypoint Loss
Stability Loss
Labeled 
Sequence
Figure 5. Siamese Training Set-up. The SuperPointVO network
is trained using Siamese learning. Random nearby image pairs
are selected from a labeled sequence, and warped by a random
homography before being used to train the three network tasks.
5.2. Training Details
SuperPointVO is trained on the full ScanNet [7] training
set, consisting of 2.5 million images collected from 1500 di-
verse indoor scenes. VO Adaptation requires only monoc-
ular images and intrinsics calibration information, so the
depth frames and pose information is not used during train-
ing time.
The network is trained by loading random nearby pairs
from sequences which have been labeled by the VO back-
end as described in Section 4. The Siamese training set-
up is pictured in Figure 5. We follow the same method-
ology of SuperPoint [10], where the descriptor is trained
using Siamese metric learning, and the keypoint detector is
trained using a standard softmax + cross entropy loss. The
pairs are randomly sampled from a temporal window of +/-
60 frames, resulting in pairs with a maximum time window
of about 4 seconds. The loss functions also incorporate the
“ignore class,” which is used for unknown correspondences
and unknown 2D point locations.
To train the stability classiﬁer, we add an extra loss term
to the ﬁnal loss of SuperPoint Ls which denotes the stability
loss. The stability loss is trained with a standard binary
cross-entropy loss function.
6. Evaluation
6.1. 3D-to-2D Pose Estimation
We compare SuperPointVO to various Frontend systems
in their ability to do 3D-to-2D pose estimation, a critical
component of Visual Odometry. To evaluate this, we fol-
low the 3D-to-2D methodology described in Scaramuzza
and Fraundorfer [20]. We ﬁrst load random pairs of images
from a given sequence, separated by 30 frames, or about 1
second worth of motion. Correspondences are chosen us-
ing matches which are the nearest neighbor to each other,
as described in Section 3.3, except with no τ match score
threshold, to keep the comparison fair among all methods.
Next, rather than triangulating the point depths from 2D-
to-2D correspondences, we use the depth from the RGBD
frame of one of the images in the image pair. This sim-
ulates a sparse 3D map built from integration and esti-
mation of many previous views. We then use the default
OpenCV SolvePnPRansac() function to estimate the
camera pose given 3D-to-2D matches.
Frame Difference
30
60
90
30
60
90
Average Relative Pose 15◦28◦
38◦25cm 48cm 67cm
Rot. Error < 5◦Transl. Error < 5cm
ORB
.432 .154 .074 .285
.076
.036
AKAZE
.641 .238 .120 .413
.114
.056
SIFT
.650 .325 .181 .448
.156
.083
SURF
.698 .322 .172 .457
.152
.069
LF-Net
.803 .425 .233 .524
.194
.094
SuperPoint (COCO)
.818 .488 .283 .587
.250
.116
SuperPoint (ScanNet) .836 .499 .288 .613
.267
.128
SuperPointVO (ours) .848 .536 .331 .622
.277
.140
Table 1. ScanNet Pose Estimation Accuracy. Best results are
marked in bold.
SuperPointVO is compared to full sparse feature match-
ing pipelines: SuperPoint, LF-NET, SIFT[14], SURF[3],
AKAZE [2] and ORB [19], which each computes 2D key-
points with corresponding descriptors.
We allow each
method to detect up to 500 keypoints per frame. For Su-
perPoint, we compare to both the author’s original imple-
mentation which was trained on MS-COCO images and a
variant we trained from scratch on ScanNet. For LF-Net,
we use the authors’ implementation, trained on the ScanNet
training set. Note that LF-Net requires both the depths and
camera poses for training, while our method does not. We
use the default OpenCV implementation for all other meth-
ods. The systems are tested on the full ScanNet test set,
consisting of 100 diverse indoor scenes. For each scene, 50
random pairs are selected, resulting in 5000 pairs. We ex-
periment with different frame differences: 30, 60, and 90
corresponding to one, two, and three-second intervals from
the 30 FPS camera. Results are presented in Table 1. Super-
PointVO achieves the best pose estimation accuracy across
all frame differences.
The beneﬁt of SuperPointVO over SuperPoint trained on
ScanNet is the most apparent at larger baselines. For exam-
ple, there are relative improvements of 1.5%, 7.5%, 15% for
rotation error estimation at 30, 60 and 90 frame difference
settings respectively. This makes sense – the homography
assumption made in SuperPoint breaks down more at larger
camera baselines in non-planar scenes.
Qualitatively, when compared to SuperPoint, our Super-
PointVO variant is better at wide-baseline matching, espe-
6
### Page 7

Figure 6. 3D Pose Estimation Comparison. Pose estimation accuracy on the ScanNet indoors dataset with a frame difference of 60. Our
SuperPointVO method outperforms all other methods at various pose thresholds.
cially in non-planar scenes. When compared to LF-NET,
SuperPointVO detect fewer points in texture-less regions,
which can be problematic for LF-Net in pose estimation.
See Figure 8 for examples.
6.2. VO Trajectory Evaluation
To evaluate the quality of the stability classiﬁer outputs,
we run two variants of SuperPointVO, one with the stabil-
ity classiﬁer head enabled and another with it disabled. We
follow the evaluation protocol of [25], where relative rota-
tion and translation errors are computed for varying sub-
trajectory lengths. To make the VO estimation difﬁcult, we
run VO with every 10th frame as input. We exclude tra-
jectories with any invalid ground truth pose, which results
in 57/100 valid trajectories. The stability conﬁdence values
for each keypoint are used in the backend optimization by
setting the value of wij for each keypoint. When the stabil-
ity is disabled, wij = 1.0. The addition of stability into VO
improves trajectory estimation, as shown in Table 2.
Sub-Trajectory Length
2 sec 5 sec 10 sec 2 sec 5 sec 10 sec
Rot. Error (◦)
Transl. Error (cm)
No Prediction
22.9 49.1
70.9
39.6 80.3
116
SuperPointVO (-stability) 2.09 4.45
7.89
5.5
14.0
32.0
SuperPointVO (+stability) 1.93 4.12
7.26
5.1
12.9
26.5
Table 2. VO Trajectory Evaluation. Using the stability classiﬁer
during VO improves performance. Best results are marked in bold.
6.3. Visualizing Stability
When trained at scale, the stability classiﬁer discovers
regions of the image which are likely to result in unsta-
ble tracks (i.e., large reprojection error) during VO. Even
though the stability classiﬁer’s training data comes from VO
tracks (see Figure 4d), we can apply the resulting stability
classiﬁer to create dense stability heatmaps as shown in Fig-
ure 7. The most common types of regions that our method
deems unstable are the following: t-junctions, lighting high-
lights, and repeated texture. We lastly show an example in
Figure 7d of stability on the Freiburg RGBD dataset [22].
a)
b)
c)
d)
Lighting Highlight Suppression
Repeated Texture Suppression
T-junction Suppression
Generalization on Freiburg Dataset
Figure 7. Stability Classiﬁer in Action. Sample visualizations of
dense per-pixel stability predictions depicting three types of “low
stability” regions such as a) lighting highlights, b) repeated tex-
ture, and c) t-junctions. d) shows an example on a different dataset.
The pink circles highlight suppressed regions.
7. Conclusion
In this paper, we presented a self-supervised method for
improving convolutional neural network VO frontends. The
approach works by combining an existing frontend with a
traditional VO backend to track points over time and es-
timate their stability via a re-projection error metric. Our
method does not rely on expensive data collection and uses
the VO output for self-supervision.
When trained on a
monocular video dataset comprising 2.5 million images, the
resulting system out-performs existing methods (both tradi-
tional and learning-based) for the task of pose estimation, in
both small and wide-baseline settings. The system automat-
ically learns which points are good for VO and suppresses
unstable points, such as those caused by lighting highlights
and from dynamic objects.
7
### Page 8

SuperPointVO
LF-Net
SuperPoint
SuperPointVO
a) Detections in Image A
b) Match Flow in Image B
c) Re-projection Error in Image B
a) Detections in Image A
b) Match Flow in Image B
c) Re-projection Error in Image B
a) Detections in Image A
b) Match Flow in Image B
c) Re-projection Error in Image B
a) Detections in Image A
b) Match Flow in Image B
c) Re-projection Error in Image B
Figure 8. Qualitative ScanNet Comparison. SuperPointVO is compared to both SuperPoint and LF-Net. Each row represents a different
example. The triplets of images are explained as follows: a) Detections in Image A are shown in cyan. b) Detections in Image B are shown
in cyan, with the match ﬂow vectors drawn in blue. c) After the relative pose is estimated via PnP + RANSAC, the points from Image A are
transformed to Image B using the estimated pose. If the re-projection error is less than 3 pixels, the projection is colored green–otherwise
it is colored red, and the re-projection residual vector is drawn. Best viewed in color.
8
### Page 9

References
[1] S. Agarwal, K. Mierle, and Others.
Ceres solver.
http://ceres-solver.org.
[2] P. F. Alcantarilla, A. Bartoli, and A. J. Davison. Kaze
features. In Proceedings of the 12th European Confer-
ence on Computer Vision - Volume Part VI, ECCV’12,
pages 214–227, Berlin, Heidelberg, 2012. Springer-
Verlag.
[3] H. Bay, A. Ess, T. Tuytelaars, and L. Van Gool.
Speeded-up robust features (surf). 2008.
[4] C. Cadena, L. Carlone, H. Carrillo, Y. Latif, D. Scara-
muzza, J. Neira, I. Reid, and J. J. Leonard.
Past,
present, and future of simultaneous localization and
mapping: Toward the robust-perception age. Trans.
Rob., 32(6):1309–1332, Dec. 2016.
[5] T. Cieslewski, M. Bloesch, and D. Scaramuzza.
Matching features without descriptors:
Implicitly
matched interest points imips.
arXiv:1811.10681,
2018.
[6] T. Cieslewski and D. Scaramuzza. SIPS: unsupervised
succinct interest points. arXiv:1805.01358, 2018.
[7] A. Dai,
A. X. Chang,
M. Savva,
M. Halber,
T. Funkhouser, and M. Nießner.
Scannet: Richly-
annotated 3d reconstructions of indoor scenes.
In
Proc. Computer Vision and Pattern Recognition
(CVPR), IEEE, 2017.
[8] A. J. Davison.
Futuremapping: The computational
structure of spatial AI systems.
arXiv:1803.11288,
2018.
[9] D. DeTone, T. Malisiewicz, and A. Rabinovich. Deep
image homography estimation.
arXiv:1606.03798,
2016.
[10] D. DeTone, T. Malisiewicz, and A. Rabinovich. Su-
perpoint: Self-supervised interest point detection and
description. In CVPR Deep Learning for Visual SLAM
Workshop, 2018.
[11] F. Fraundorfer and D. Scaramuzza. Visual odometry:
Part ii: Matching, robustness, optimization, and ap-
plications. IEEE Robotics & Automation Magazine,
19(2):78–90, 2012.
[12] R. Hartley and A. Zisserman. Multiple View Geometry
in computer vision. 2003.
[13] Z. Li and N. Snavely. Megadepth: Learning single-
view depth prediction from internet photos. In Com-
puter Vision and Pattern Recognition (CVPR), 2018.
[14] D. G. Lowe. Distinctive image features from scale-
invariant keypoints. IJCV, 2004.
[15] R. Mur-Artal, J. Montiel, and J. D. Tardos.
ORB-
SLAM: a versatile and accurate monocular SLAM
system. IEEE Transactions on Robotics, 2015.
[16] D. Nist´er, O. Naroditsky, and J. Bergen. Visual odom-
etry.
In Computer Vision and Pattern Recognition,
2004. CVPR 2004. Proceedings of the 2004 IEEE
Computer Society Conference on, volume 1, pages I–I.
Ieee, 2004.
[17] Y. Ono, E. Trulls, P. Fua, and K.M.Yi. Lf-net: Learn-
ing local features from images.
arXiv:1805.09662,
2018.
[18] I. Rocco, R. Arandjelovi´c, and J. Sivic. Convolutional
neural network architecture for geometric matching.
In CVPR, 2017.
[19] E. Rublee, V. Rabaud, K. Konolige, and G. Bradski.
ORB: An efﬁcient alternative to SIFT or SURF. In
ICCV, 2011.
[20] D. Scaramuzza and F. Fraundorfer. Visual odometry
tutorial part 1. IEEE Robot. Automat. Mag., 18(4):80–
92, 2011.
[21] K. Simonyan and A. Zisserman.
Very deep convo-
lutional networks for large-scale image recognition.
arXiv:1409.1556, 2014.
[22] J. Sturm, N. Engelhard, F. Endres, W. Burgard, and
D. Cremers. A benchmark for the evaluation of rgb-d
slam systems. In Proc. of the International Conference
on Intelligent Robot Systems (IROS), 2012.
[23] C. Wu.
Towards linear-time incremental structure
from motion. In Proceedings of the 2013 International
Conference on 3D Vision, 3DV ’13, pages 127–134,
Washington, DC, USA, 2013. IEEE Computer Soci-
ety.
[24] K. M. Yi, E. Trulls, V. Lepetit, and P. Fua.
LIFT:
Learned Invariant Feature Transform. In ECCV, 2016.
[25] Z. Zhang and D. Scaramuzza. A tutorial on quanti-
tative trajectory evaluation for visual-inertial odome-
try. Proc. of the International Conference on Intelli-
gent Robot Systems (IROS), 2012.
[26] T. Zhou, M. Brown, N. Snavely, and D. G. Lowe.
Unsupervised learning of depth and ego-motion from
video. In CVPR, 2017.
9