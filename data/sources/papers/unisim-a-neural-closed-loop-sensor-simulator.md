# UniSim: A Neural Closed-Loop Sensor Simulator

**Source**: arXiv:2308.01898

**Type**: Academic Paper

---

## Page 1

UniSim: A Neural Closed-Loop Sensor Simulator
Ze Yang1,2*
Yun Chen1,2∗
Jingkang Wang1,2∗
Sivabalan Manivasagam1,2∗
Wei-Chiu Ma1,3
Anqi Joyce Yang1,2
Raquel Urtasun1,2
1Waabi
2University of Toronto
3Massachusetts Institute of Technology
{zyang, ychen, jwang, siva, weichiu, jyang, urtasun}@waabi.ai
Closed-loop simulation for safety-critical scenarios
Actor Removal
Actor Modification
SDV Sensor Lift
SDV Lane Change
Scene manipulation with actor removal, modification, sensor configuration changes, and modified ego-trajectories
Original Scenario
Modify Sedan Route
Insert New Truck
Original Scenario
Closed-loop simulation for vehicle cut-in
Original
Original
Original
Original
Figure 1. Top: UniSim takes recorded sensor data from a data collection platform and creates manipulable digital twins. Bottom: UniSim
generates realistic, temporally consistent sensor simulations for new scenarios, enabling closed-loop autonomy evaluation. The autonomy
system reactively interacts with the scenario, receives new sensor data, and changes lanes (see planned trajectory inset). All images and
LiDAR in figure simulated by UniSim. Please refer to our project page https://waabi.ai/research/unisim/ for more results.
Abstract
Rigorously testing autonomy systems is essential for
making safe self-driving vehicles (SDV) a reality. It requires
one to generate safety critical scenarios beyond what can
be collected safely in the world, as many scenarios happen
rarely on public roads. To accurately evaluate performance,
we need to test the SDV on these scenarios in closed-loop,
where the SDV and other actors interact with each other
at each timestep. Previously recorded driving logs provide
*Indicates equal contribution.
a rich resource to build these new scenarios from, but for
closed loop evaluation, we need to modify the sensor data
based on the new scene configuration and the SDV’s deci-
sions, as actors might be added or removed and the tra-
jectories of existing actors and the SDV will differ from the
original log. In this paper, we present UniSim, a neural
sensor simulator that takes a single recorded log captured
by a sensor-equipped vehicle and converts it into a realistic
closed-loop multi-sensor simulation. UniSim builds neural
feature grids to reconstruct both the static background and
dynamic actors in the scene, and composites them together
1
arXiv:2308.01898v1  [cs.CV]  3 Aug 2023


## Page 2

to simulate LiDAR and camera data at new viewpoints, with
actors added or removed and at new placements. To better
handle extrapolated views, we incorporate learnable priors
for dynamic objects, and leverage a convolutional network
to complete unseen regions. Our experiments show UniSim
can simulate realistic sensor data with small domain gap on
downstream tasks. With UniSim, we demonstrate closed-
loop evaluation of an autonomy system on safety-critical
scenarios as if it were in the real world.
1. Introduction
While driving along a highway, a car from the left sud-
denly swerves into your lane. You brake hard, avoiding an
accident, but discomforting your passengers. As you re-
play the encounter in your mind, you consider how the sce-
nario would have gone if the other vehicle had accelerated
more, if you had slowed down earlier, or if you had instead
changed lanes for a more comfortable drive. Having the
ability to generate such “what-if” scenarios from a single
recording would be a game changer for developing safe self-
driving solutions. Unfortunately, such a tool does not exist
and the self-driving industry primarily test their systems on
pre-recorded real-world sensor data (i.e., log-replay), or by
driving ever more miles in the real-world. In the former,
the autonomous system cannot execute actions and observe
their effects as new sensor data different from the original
recording is not generated, while the latter is neither safe,
nor scalable or sustainable. The status quo calls for novel
closed-loop sensor simulation systems that are high fidelity
and represent the diversity of the real world.
Here, we aim to build an editable digital twin of the real
world (through the logs we captured), where existing ac-
tors in the scene can be modified or removed, new actors
can be added, and new autonomy trajectories can be exe-
cuted. This enables the autonomy system to interact with
the simulated world, where it receives new sensor obser-
vations based on its new location and the updated states
of the dynamic actors, in a closed-loop fashion. Such a
simulator can accurately measure self-driving performance,
as if it were actually in the real world, but without the
safety hazards, and in a much less capital-intensive manner.
Compared to manually-created game-engine based virtual
worlds [16, 68], it is a more scalable, cost-effective, realis-
tic, and diverse way towards closed-loop evaluation.
Towards this goal, we present UniSim, a realistic closed-
loop data-driven sensor simulation system for self-driving.
UniSim reconstructs and renders multi-sensor data for novel
views and new scene configurations from a single recorded
log. This setting is very challenging as the observations are
sparse and often captured from constrained viewpoints (e.g.,
straight trajectories along the roads). To better handle ex-
trapolation from the observed views, we propose a series of
enhancements over prior neural rendering approaches. In
particular, we leverage multi-resolution voxel-based neural
fields to represent and compose the static scene and dy-
namic agents, and volume render feature maps. To better
handle novel views and incorporate scene context to reduce
artifacts, a convolutional network (CNN) renders the fea-
ture map to form the final image. For dynamic agents, we
learn a neural shape prior that helps complete the objects to
render unseen areas. We use this sparse voxel-based rep-
resentations to efficiently simulate both image and LiDAR
observations under a unified framework. This is very useful
as SDVs often use several sensor modalities for robustness.
Our experiments show that UniSim realistically simu-
lates camera and LiDAR observations at new views for
large-scale dynamic driving scenes, achieving SoTA perfor-
mance in photorealism. Moreover, we find UniSim reduces
the domain gap over existing camera simulation methods on
the downstream autonomy tasks of detection, motion fore-
casting and motion planning. We also apply UniSim to aug-
ment training data to improve perception models. Impor-
tantly, we show, for the first time, closed-loop evaluation of
an autonomy system on photorealistic safety-critical scenar-
ios, allowing us to better measure SDV performance. This
further demonstrates UniSim’s value in enabling safer and
more efficient development of self-driving.
2. Related Work
Simulation Environments for Robotics:
The robotics
community has a long history of building simulators for
safer and faster robot development [15, 31, 37, 49, 77, 88].
Early works focused on modeling robot dynamics and phys-
ical forces for parameter identification and controller mod-
elling [31, 53].
Several works then developed accurate
physics engines for improving robot design and motion
planning [7,13,15,28,33], and for specific domains such as
grasping [36], soft robotics [27], and SDVs [88]. But to en-
able end-to-end testing of full autonomy systems, we must
also simulate realistic sensor observations of the 3D envi-
ronment for the robot to perceive, interact with its surround-
ings, and plan accordingly [19]. Most prior sensor simula-
tion systems use 3D-scanned or manually built synthetic en-
vironments for small indoor environments [33, 37, 67], and
perform rasterization or ray-tracing [58,69] to simulate var-
ious sensor data [20,22,30]. For high-speed robots such as
SDVs, simulators such as CARLA and AirSim [16,68] ap-
plied a similar approach. But due to the costly manual effort
in creating scenes, these simulators have difficulty scaling
to all the areas we may want to test in, have limited asset
diversity (e.g., roads, vehicles, vegetation) compared to the
real world, and generate unrealistic sensor data that require
substantial domain adaptation for autonomy [26,87].
Novel View Synthesis:
Recent novel view synthesis
(NVS) work has achieved success in automatically generat-
2


## Page 3

ing highly photorealistic sensor observations [1, 35, 43, 50,
55, 56, 63, 64]. Such methods aim to learn a scene repre-
sentation from a set of densely collected observed images
and render the scene from nearby unseen viewpoints. Some
works perform geometry reconstruction and then warp and
aggregate pixel-features from the input images into new
camera views, which are then processed by learning-based
modules [1, 60, 64, 65]. Others represent the scene implic-
itly as a neural radiance field (NeRF) and perform volume
rendering with a neural network [4,50,79,93]. These meth-
ods can represent complex geometry and appearance and
have achieved photorealistic rendering, but focus on small
static scenes. Several representations [8, 42, 47, 51, 52, 61,
62,76,100] partition the space and model the volume more
efficiently to handle large-scale unbounded outdoor scenes.
However, these works focus primarily on the NVS task
where a dense collection of images are available and most
test viewpoints are close to the training views, and focus on
the static scene without rendering dynamic objects such as
moving vehicles. In contrast, our work extends NVS tech-
niques to build a sensor simulator from a single recorded
log captured by a high-speed mobile platform. We aim to
render image and LiDAR observations of dynamic traffic
scenarios from new viewpoints and modified scene config-
urations to enable closed-loop autonomy evaluation.
Data-driven Sensor Simulation for Self Driving:
Sev-
eral past works have leveraged computer vision techniques
and real world data to build sensor simulators for self-
driving.
Some works perform 3D reconstruction by ag-
gregating LiDAR and building textured geometry primi-
tives for physics-based rendering [18, 46, 75, 92], but pri-
marily simulate LiDAR or cannot model high-resolution
images. Another line of work perform object reconstruc-
tion and insertion into existing images [10, 80, 86, 93] or
point clouds [17,81,94,95], but these methods are unable to
render sensor data from new views for closed-loop interac-
tion. DriveGAN [32] represents the scene as disentangled
latent codes and generates video from control inputs with
a neural network for differentiable closed-loop simulation,
but is limited in its realism and is not temporally consis-
tent. AADS [38] and VISTA 2.0 [2, 3, 84], perform multi-
sensor simulation via image-based warping or ray-casting
on previously collected sensor data to render new views of
the static scene, and then insert and blend CAD assets into
the sensor data to create new scenarios. These approaches,
while promising, have visual artifacts for the inserted ac-
tors and rendered novel views, resulting in a large domain
gap. Neural Scene Graphs (NSG) [56] and Panoptic Neural
Fields (PNF) [35] represent the static scene and agents as
multi-layer perceptrons (MLPs) and volume render photo-
realistic images of the scene. However, the single MLP has
difficulties modelling large scale scenes. These prior works
also focus on scene editing and perception tasks where the
CNN
z
Hypernet
Sampled pts
Actor model
Background 
feature grid
Sensor
Rendered 
feature
Figure 2. Overview of our approach: We divide the 3D scene
into a static background (grey) and a set of dynamic actors (red).
We query the neural feature fields separately for static background
and dynamic actor models, and perform volume rendering to gen-
erate neural feature descriptors. We model the static scene with a
sparse feature-grid and use a hypernetwork to generate the repre-
sentation of each actor from a learnable latent. We finally use a
convolutional network to decode feature patches into an image.
SDV does not deviate significantly from the original record-
ing. Instead, we focus on multi-sensor simulation for closed
loop evaluation of autonomy systems, and specifically de-
sign our system to better handle extrapolation.
3. Neural Sensor Simulation
Given a log with camera images and LiDAR point clouds
captured by a moving platform, as well as their relative
poses in a reference frame, our goal is to construct an ed-
itable and controllable digital twin, from which we can gen-
erate realistic multi-modal sensor simulation and counter-
factual scenarios of interest.
We build our model based
on the intuition that the 3D world can be decomposed as a
static background and a set of moving actors. By effectively
disentangling and modeling each component, we can ma-
nipulate the actors to generate new scenarios and simulate
the sensor observations from new viewpoints. Towards this
goal, we propose UniSim, a neural rendering closed-loop
simulator that jointly learns shape and appearance represen-
tations for both the static scene and dynamic actors from the
sensor data captured from a single pass of the environment.
We unfold this section by first reviewing the basic build-
ing blocks of our approach. Next, we present our compo-
sitional scene representation, and detail how we design our
background and dynamic actor models. We then describe
how to generate simulated sensor data with UniSim. Fi-
nally, we discuss how to learn the model from real-world
data. Fig. 2 shows an overview of our approach.
3.1. Preliminaries
Neural feature fields:
A feature field refers to a con-
tinuous function f that maps a 3D point x ∈R3 and a
view direction d ∈R2 to an implicit geometry s ∈R
3


## Page 4

and a Nf-dimensional feature descriptor f ∈RNf . Since
the function is often parameterized as a neural network
fθ : R3 × R2 →R × RNf , with θ the learnable weights,
we call it neural feature field (NFF). NFFs can be seen as
a superset of several existing works [48, 50]. If we repre-
sent the implicit geometry as volume density s ∈R+ and
the feature descriptor as RGB radiance f ∈R3, NFFs be-
come NeRFs [50]. If we enforce the implicit geometry to
be the probability of occupancy, NFFs become occupancy
functions [48]. Importantly, NFFs naturally support com-
position [23, 35, 54], enabling the combination of multiple
relatively simple NFFs to form a complex neural field.
Multi-resolution features grid:
To improve the expres-
siveness and speed of NFFs, past works [12, 51, 74, 98]
further combined learnable multi-resolution features grid
{Gl}L
l=1 with a neural network f.
Specifically, given a
query point x ∈R3, the 3D feature grid at each level is
first trilinearly interpolated. The interpolated features are
then concatenated with the view direction d ∈R2, and the
resulting features are processed with an MLP head to obtain
the geometry s and feature descriptor f:
  s ,  
\
mathbf f =  f\left (\{\texttt {interp}(\mathbf x, \mathcal G^l)\}_{l=1}^L, \mathbf d \right ). \label {eqn:feature_fileds}
(1)
These multi-scale features encode both global context and
fine-grained details, providing richer information compar-
ing to the original input x. This also enables using a smaller
f, which significantly reduces the inference time [72,74]. In
practice, we optimize the features grid using a fixed number
of features F, and map the features grid {Gl}L
l=1 to F with
a grid index hash function [51]. Hereafter, we will use F
and {Gl}L
l=1 interchangeably.
3.2. Compositional Neural Scene Representation
We aim to build a compositional scene representation
that best models the 3D world including the dynamic ac-
tors and static scene.
Given a recorded log captured by
a data collection platform, we first define a 3D space vol-
ume over the traversed region. The volume consists of a
static background B and a set of dynamic actors {Ai}N
i=1.
Each dynamic actor is parameterized as a bounding box of
dimensions sAi ∈R3, and its trajectory is defined by a
sequence of SE(3) poses {Tt
Ai}T
t=1. We then model the
static background and dynamic actors with separate multi-
resolution features grid and NFFs. Let the static background
be expressed in the world frame. We represent each ac-
tor in its object-centroid coordinate system (defined at the
centroid of its bounding box), and transform their features
grid to world coordinates to compose with the background.
This allows us to disentangle the 3D motion of each actor,
and focus on representing shape and appearance. To learn
high-quality geometry [82,96], we adopt the signed distance
function (SDF) as our implicit geometry representation s.
We now describe each component in more detail.
Sparse background scene model:
We model the whole
static scene with a multi-resolution features grid Fbg and
an MLP head fbg.
Since a self-driving log often spans
hundreds to thousands of meters, it is computationally and
memory expensive to maintain a dense, high-resolution
voxel grid. We thus utilize geometry priors from LiDAR
observations to identify near-surface voxels and optimize
only their features. Specifically, we first aggregate the static
LiDAR point cloud from each frame to construct a dense 3D
scene point cloud. We then voxelize the scene point cloud
and obtain a scene occupancy grid Vocc. Finally, we apply
morphological dilation to the occupancy grid and coarsely
split the 3D space into free vs. near-surface space. As the
static background is often dominated by free space, this can
significantly sparsify the features grid and reduce the com-
putation cost. The geometric prior also allows us to better
model the 3D structure of the scene, which is critical when
simulating novel viewpoints with large extrapolation. To
model distant regions, such as sky, we follow [5, 100] to
extend our background scene model to unbounded scenes.
Generalized actor model:
One straightforward way to
model the actors is to parameterize each actor Ai with a
features grid FAi and adopt a shared MLP head fA for
all actors. In this design, the individual features grid en-
codes instance-specific geometry and appearance, while the
shared network maps them to the same feature space for
downstream applications. Unfortunately, such a design re-
quires large memory for dense traffic scenes and, in prac-
tice, often leads to overfitting — the features grid does not
generalize well to unseen viewpoints. To overcome such
limitations, we propose to learn a hypernetwork [24] over
the parameters of all grids of features.
The intuition is
that different actors are observed from different viewpoints,
and thus their grids of features are informative in differ-
ent regions. By learning a prior over them, we can capture
the correlations between the features and infer the invisible
parts from the visible ones. Specifically, we model each ac-
tor Ai with a low-dimensional latent code zAi and learn a
hypernetwork fz to regress the features grid FAi:
  \ m athcal F_{\mathcal A_i} = f_{\mathbf z} (\mathbf z_{\mathcal A_i}). \label {eqn:hyper_network}
(2)
Similar to the background, we adopt a shared MLP head
fA to predict the geometry and feature descriptor at each
sampled 3D point via Eq. 1. We jointly optimize the actor
latent codes {zAi} during training.
Composing neural feature fields:
Inspired by works that
composite solid objects [23,56] into a scene, we first trans-
form object-centric neural fields of the foreground actors to
world coordinates with the desired poses (e.g., using Tt
Ai
for reconstruction). As the static background is a sparse
features grid, we then simply replace the free space with the
4


## Page 5

actor feature fields. Through this simple operation, we can
insert, remove, and manipulate the actors within the scene.
3.3. Multi-modal Sensor Simulation
Now that we have a composed scene representation of
the static and dynamic world, the next step is to render it
into the data modality of interest. In this work, we focus on
camera images and LiDAR point clouds, as they are the two
main sensory modalities employed by modern SDVs.
Camera simulation:
Following recent success in view
synthesis and generation [9,54], we adopt a hybrid volume
and neural rendering framework for efficient photorealistic
image simulation. Given a ray r(t) = o+td shooting from
the camera center o through the pixel center in direction d,
we first sample a set of 3D points along the ray and extract
their features and geometry (Eq. 1). We then aggregate the
samples and obtain a pixel-wise feature descriptor via vol-
ume rendering:
  \m a
th
b
f f
(\mat
hb f  r
) =
 
\su
m _ {i=1}^{N_{\mathbf r}} w_i \mathbf f_i, \quad w_i = \alpha _i \prod _{j=1}^{i-1} (1-\alpha _j). \label {eqn:render_neural_feature}
(3)
Here, αi ∈[0, 1] represents opacity, which we can derive
from the SDF si using an approximate step function α =
1/(1+exp(β ·s)), and β is the hyper-parameter controlling
the slope. We volume render all camera rays and generate a
2D feature map F ∈RHf ×Wf ×Nf . We then leverage a 2D
CNN grgb to render the feature map to an RGB image Irgb:
  g_ \ t e xt {rg b}:  \mat h bf F  \in \mathbb R^{H_f \times W_f \times N_f} \rightarrow \mathbf I_\text {rgb} \in \mathbb R^{H \times W \times 3}. \label {eqn:render_rgb}
(4)
In practice, we adopt a smaller spatial resolution for the fea-
ture map Hf ×Wf than that of the rendered image H ×W,
and rely on the CNN grgb for upsampling. This allows us to
significantly reduce the amount of ray queries.
LiDAR simulation:
LiDAR point clouds encode 3D
(depth) and intensity (reflectivity) information, both of
which can be simulated in a similar fashion to Eq. 3. We as-
sume the LiDAR to be a time-of-flight pulse-based sensor,
and model the pulses transmitted by the oriented LiDAR
laser beams as a set of rays. We slightly abuse the notation
and let r(t) = o+td be a ray casted from the LiDAR sensor
we want to simulate. Denote o as the center of the LiDAR
and d as the normalized vector of the corresponding beam.
We then simulate the depth measurement by computing the
expected depth of the sampled 3D points:
  D( \
ma
t
hbf
 r) &= \sum _{i=1}^{N_{\mathbf r}} w_i t_i. \label {eqn:render_depth}
(5)
As for LiDAR intensity, we volume render the ray feature
(using Eq. 3) and pass it through an MLP intensity decoder
gint to predict its intensity lint(r) = gint(f(r)).
3.4. Learning
We jointly optimize all grids of features F∗(including
latent codes {zAi}, the hypernetwork fz, the MLP heads
(fbg, fA) and the decoders (grgb, gint) by minimizing the dif-
ference between the sensor observations and our rendered
outputs. We also regularize the underlying geometry such
that it satisfies real-world constraints. Our full objective is:
  \mat h cal {L} = \m a thcal {L } _\text {rgb} + \lambda _\text {lidar}\mathcal {L}_\text {lidar} + \lambda _\text {reg}\mathcal {L}_\text {reg} + \lambda _\text {adv}\mathcal {L}_\text {adv}.
In the following, we discuss in more detail each term.
Image simulation Lrgb:
This objective consists of a ℓ2
photometric loss and a perceptual loss [83,101], both mea-
sured between the observed images and our simulated re-
sults. We compute the loss in a patch-wise fashion:
  \r e
s
izeb
ox {
.
43\
t
e
xtwidth
 
} {!}{$
 
\be
g i n
 
{
spl
it} \mathc
a l  L _\text 
{ r
gb}
 
=
 \frac {1}{N_{\text {rgb}}} \sum \limits _{i=1}^{N_{\text {rgb}}} \left ( \left \lVert \mathbf I^{\text {rgb}}_i - \mathbf { \hat {I}}^{\text {rgb}}_i \right \rVert _2 + \lambda \sum _{j=1}^M \left \lVert V^j(\mathbf I^{\text {rgb}}_i) - V^j(\mathbf { \hat {I}}^{\text {rgb}}_i) \right \rVert _1 \right ), \end {split}$} (6)
where Irgb
i
= frgb(Fi) is the rendered image patch (Eq. 4)
and ˆIrgb
i
is the corresponding observed image patch. V j de-
notes the j-th layer of a pre-trained VGG network [70].
LiDAR simulation Llidar:
This objective measures the ℓ2
error between the observed LiDAR point clouds and the
simulated ones. Specifically, we compute the depth and in-
tensity differences:
  \res i z
e
b
o
x {
.43\text w idth
 
}{
! }
{$ \begin { s plit}
 
\ma
t
h
cal L_\text {lidar} = \frac {1}{N} \sum \limits _{i=1}^N \left (\left \lVert D(\mathbf r_i) - D^{\text {obs}}_i \right \rVert _2 + \left \lVert l^{\text {int}}(\mathbf r_i) - \hat {l}^{\text {int}}_i \right \rVert _2 \right ). \end {split}$} (7)
Since LiDAR observations are noisy, we filter outliers and
encourage the model to focus on credible supervision. In
practice, we optimize 95% of the rays within each batch
that have smallest depth error.
Regularization Lreg:
We further apply two additional
constraints on the learned representations. First, we encour-
age the learned sample weight distribution w (Eq. 3) to con-
centrate around the surface. Second, we encourage the un-
derlying SDF s to satisfy the Eikonal equation, which helps
the network optimization find a smooth zero level set [21]:
  \l a b
e
l
 
{eq
n :
total_
loss} \
r
esizeb
o
x {.43\tex t w
id
t
h }{!}{$ \begin {split} \mathcal L_\text {reg} = \frac {1}{N} \sum \limits _{i=1}^N \biggl ( \sum \limits _{\tau _{i,j} > \epsilon } \left \lVert w_{ij} \right \rVert _2 + \sum \limits _{\tau _{i,j} < \epsilon } \left ( \left \lVert \nabla s(\mathbf x_{ij}) \right \rVert _2 - 1 \right )^2 \biggr ), \end {split}$} (8)
where τi,j = |tij −Dgt
i | is the distance between the sample
xij and its corresponding LiDAR observation Dgt
i .
Adversarial loss Ladv:
To improve photorealism at un-
observed viewpoints, we train a discriminator CNN Dadv
to differentiate between our simulated images at observed
5


## Page 6

FVS
Instant-NGP
Neural Scene Graphs
Ours
Ground-truth
Interpolation
Lane shift
Interpolation
Lane shift
Figure 3. Qualitative comparison. We show simulation results in both the interpolation (rows 1, 3) and lane-shift test settings (rows 2, 4).
Methods
Interpolation
Lane Shift
PSNR↑
SSIM↑
LPIPS↓
FID↓@ 2m
FID↓@ 3m
FVS [64]
21.09
0.700
0.299
112.6
135.8
NSG [56]
20.74
0.600
0.556
319.2
343.0
Instant-NGP [51]
24.03
0.708
0.451
192.8
220.1
Ours
25.63
0.745
0.288
74.7
97.5
Table 1. State-of-the-art image comparison
Methods
Interpolation
Lane Shift
PSNR↑
SSIM↑
LPIPS↓
FID↓@ 2m
FID↓@ 3m
NFF only
24.93
0.717
0.393
153.7
173.5
+ Actor model
25.80
0.744
0.364
84.1
111.8
+ CNN
25.99
0.762
0.341
78.8
103.3
+ VGG & GAN loss
25.63
0.745
0.288
74.7
97.5
Table 2. Ablation of UniSim enhancements
Median ℓ2 Error (m)↓
Hit Rate↑
Intensity RMSE↓
LiDARsim [46]
0.11
92.2%
0.091
Ours
0.10
99.6%
0.065
Table 3. State-of-the-art LiDAR comparison
viewpoints and unobserved ones.
Specifically, we de-
note the set of rays to render an image patch as R =
{r(o, dj)}P ×P
j=1 , and randomly jitter the ray origin to create
unobserved ray patches R′ = {r(o + ϵ, dj)}P ×P
j=1 , where
ϵ ∈N(0, σ). The discriminator CNN Dadv minimizes:
 
 
- \f
rac 
{
1}{
N_\ text {adv}} \sum _{i=1}^{N_\text {adv}} \log \mathcal D_{\text {adv}}(\mathbf I_i^{\text {rgb}, \mathbf R}) + \log (1- \mathcal D_{\text {adv}}(\mathbf I_i^{\text {rgb}, \mathbf R'})),
(9)
where Irgb,R
i
= frgb(F(Ri)) and Irgb,R′
i
= frgb(F(R′
i))
are the rendered image patches at observed and unobserved
viewpoints, respectively. We then define the adversarial loss
Ladv to train the CNN RGB decoder grgb and neural feature
fields to improve photorealism at unobserved viewpoints as:
  \m a
t
hcal
 L_\
t
ext
 {adv }  = \frac {1}
{
N_\text {adv}} \sum _{i=1}^{N_\text {adv}} \log (1- \mathcal D_{\text {adv}}(\mathbf I_i^{\text {rgb}, \mathbf R'})).
(10)
Implementation details:
We identify actors along ren-
dered rays using the AABB ray-box intersection [45].
When sampling points along the ray, we adopt a larger step
size for background regions and a smaller one for inter-
sected actor models to ensure appropriate resolution. We
leverage the scene occupancy grid Vocc to skip point sam-
ples in free space. During learning, we also optimize the ac-
tor trajectories to account for noise in the initial input. For
vehicle actors, we also leverage the shape prior that they are
symmetric along their length.
4. Experiments
In this section we begin by introducing our experimental
setting, and then compare our model against state-of-the-art
methods to evaluate the sensor simulation realism and do-
main gap with real data, and also ablate our model compo-
nents. We then show that our method can generate diverse
sensor simulations to improve vehicle detection. Finally,
we demonstrate UniSim for evaluating an autonomy system
trained only on real data in closed-loop.
4.1. Experimental Details
Dataset:
We evaluate our method on the publicly avail-
able PandaSet [89] which contains 103 driving scenes cap-
tured in urban areas in San Francisco.
Each scene is
composed of 8 seconds (80 frames, sampled at 10hz) of
images captured from a front-facing wide angle camera
(1920×1080) and point clouds from 360◦spinning LiDAR.
6


## Page 7

Real
LiDARsim
UniSim
Figure 4. Comparison of LiDAR simulation. UniSim produces
higher-fidelity LiDAR simulation with less noise and more contin-
uous beam rings that are closer to real LiDAR compared to [46].
Baselines:
We compare our model against several SoTA
methods.
FVS [64] is an NVS method that uses recon-
structed geometry (aggregated LiDAR in our implementa-
tion) as a “proxy” to re-project pixels from the input images
into new camera views, where they are blended by a neu-
ral network. We enhance FVS to model dynamic actors.
Instant-NGP [51] is a NeRF-based method that adopts
multi-resolution hashing encoding for compact scene repre-
sentation and efficient rendering. We enhance it by adding
LiDAR depth supervision for better geometry and extrapo-
lation. NSG [56] is a camera simulation method that models
the scene with separate NeRF representations for the static
background and each dynamic actor. See supp. for details.
4.2. UniSim Controllability
We first highlight in Fig. 1 the power of UniSim to per-
form all the capabilities for closed-loop sensor simulation.
We can not only render the original scene, but because of
our decomposed actor and background representations, we
can also remove all the actors, and change their positions.
With enhanced extrapolation capabilities, we can change
the SDV’s location or test new sensor configurations. See
supp. for more results, including highway scenes.
4.3. Realism Evaluation
Sensor simulation should not only reconstruct nearby
views, but also generate realistic data at significantly dif-
ferent viewpoints. Here we evaluate both settings. Similar
to other NVS benchmarks [41], we subsample the sensor
data by two, training on every other frame and testing on
the remaining frames, dubbed “interpolation” test. We re-
port PSNR, SSIM [85], and LPIPS [101]. We also evaluate
extrapolation by simulating a new trajectory shifted later-
ally to the left or right by 2 or 3 meters, dubbed “lane shift”
test. Since ground-truth is unavailable, we report FID [25].
Camera Simulation:
We report image-similarity metrics
against SoTA in Table 1. Due to computational costs of
the baseline NSG, we select 10 scenes for evaluation. Our
method outperforms the baselines in all metrics, and the gap
is more significant in extrapolation settings. FVS performs
well on LPIPS and InstantNGP on PSNR in the interpola-
tion setting, but both have difficulty when rendering at ex-
trapolated views. Fig. 3 shows qualitative results. NSG pro-
duces decent results for dynamic actors but fails on large
static scenes, due to its sparse multi-plane representation.
Note UniSim is more realistic than the baselines.
Lane shift
Lane shift
FVS
Ours
replay
replay
Figure 5. Real2Sim Qualitative on replay and lane shift settings.
Log Replay
Lane Shift
Method
Real2Sim
Sim2Real
Real2Sim
Sim2Real
FVS [64]
36.9
38.7
30.3
32.2
Instant-NGP [51]
22.6
34.0
18.1
26.5
Ours
40.2
39.9
37.0
37.1
Table 4. Detection domain gap, mAP. Real2Real = 40.9.
Instant-NGP [51]
FVS [64]
Ours
Sim
32.4
39.2
41.4
Real + Sim
40.1
41.1
42.9
Table 5. Augmenting with simulation, mAP. Real2Real = 40.9.
Det. Agg. ↑
Pred. ADE ↓
Plan Cons. ↓
FVS [64]
0.80
2.35
6.15
Instant-NGP [51]
0.42
3.24
13.44
Ours
0.82
1.68
6.09
Table 6. Open-Loop Real2Sim Autonomy Evaluation
Ablation:
We validate the effectiveness of several key
components in Tab. 2. Both the actor model and the CNN
decoder improve the overall performance over the neural
features grid base model. The CNN is especially effective
in the extrapolation setting, as it improves the overall image
quality by spatial relation reasoning and increases model ca-
pacity. Adding perceptual and adversarial losses results in a
small performance drop for interpolation, but improves the
lane shift results. Please see supp. for more visual results.
LiDAR Simulation:
We also evaluate the fidelity of our
LiDAR simulation and compare with SoTA approach Li-
DARsim [46]. For LiDARsim, we reconstruct surfel assets
using all training frames, place actors in their original sce-
nario in test frames, and perform ray-casting. Both methods
use the real LiDAR rays to generate a simulated point cloud.
We evaluate the fraction of real LiDAR points that have a
corresponding simulated point (i.e., Hit rate), the median
per-ray ℓ2 error and the average intensity simulation errors.
As shown in Tab. 3, UniSim outperforms LiDARsim in all
metrics suggesting it is more accurate and has better cover-
age. Fig. 4 shows a visual comparison. Please see supp. for
additional autonomy results and qualitative examples.
4.4. Perception Evaluation and Training
In addition to image-similarity, sensor simulation should
be realistic with respect to how autonomy perceives it. To
verify if UniSim reduces the domain gap for perception
tasks, we leveraged the SoTA camera-based birds-eye-view
7


## Page 8

World State at T=0 
Sensor Simulation at T=0 
Autonomy Output at T=0 
Updated World State at T=1 
Sensor Simulation at T=1 
Incoming Actor
Motion 
Plan
Perception & 
Prediction 
Updated Actor
Updated 
SDV
SDV
Figure 6. Closed-loop Evaluation. From left to right: With UniSim, we can create a safety-critical scenario (e.g., incoming actor),
simulate the sensor data, run autonomy on it, update the SDV’s viewpoint and other actor locations, and simulate the new sensor data.
(BEV) detection model BEVFormer [40].
We consider
two setups (a) Real2Sim: evaluating the perception model
trained on real data on simulated data; (b) Sim2Real: train-
ing perception models with simulated data and testing on
real data. Specifically, we evaluate the real model on 24
simulated validation logs for Real2Sim and train perception
models with 79 simulated training logs for Sim2Real.
We consider both replay and lane shift test settings. In
replay, we replay all actors and SDV with their original tra-
jectories. In lane shift, we shift the SDV trajectory laterally
by 2 meters and simulate images at extrapolated views. We
report detection mean average precision (mAP).
Domain Gap in Simulation:
As shown in Table 4,
our approach achieves the smallest domain gap in both
Real2Sim and Sim2Real setups, on both replay and lane
shift settings, while other existing approaches result in
larger domain gaps, hindering their applicability to evalu-
ate and train autonomy. This is especially evident in the
more challenging lane shift setting, where there is a larger
performance gap between UniSim and the baselines. Fig. 5
shows the Real2Sim detection performance for both replay
and lane shift settings compared to FVS [64].
Data Augmentation with Simulation Data:
We now
study if our simulated data boosts performance when used
for training. Specifically, we use all PandaSet training logs
to generate simulation variations (replay, lane shift 0.5 and
2 meters) to train the detectors. As shown in Table 5, using
UniSim data only to train the perception model is even bet-
ter than training with all real data. Note we only increase the
rendered viewpoints and do not alter the content. We then
combine the real data with the simulation data and retrain
the detector. Table 5 shows UniSim augmentation yields
a significant performance gain. In contrast, baseline data
augmentation brings marginal gain or harms performance.
4.5. Full Autonomy Evaluation with UniSim
Domain gap evaluation:
Sensor simulation not only af-
fects perception tasks, but also downstream tasks such as
motion forecasting and planning. We report domain gap
metrics by evaluating an autonomy system trained on real
data on simulated images of the original scenario. The au-
tonomy system under evaluation is a module-based system,
with BEVFormer [40] taking front-view camera images as
input and producing BEV detections that are matched over
time to produce tracks via greedy association as the percep-
tion module. These are then fed to a motion forecasting
model [14] that takes in BEV tracks and a map raster and
outputs bounding boxes and 6 second trajectory forecasts.
Finally a SoTA sampling-based motion planner [66] takes
the prediction output and map to plan a maneuver. We re-
port open-loop autonomy metrics (detection agreement @
IoU 0.3, prediction average displacement error (ADE), and
motion plan consistency at 5 seconds) in Table 6. Com-
pared to other methods, our approach has the smallest do-
main gap. Please see supp. for details.
Closed-loop Simulation:
With UniSim, we can create
new scenarios, simulate the sensor data, run the autonomy
system, update the state of the actors in a reactive manner
and the SDV’s location, and execute the next time step (see
Fig. 6). This gives us a more accurate measure of the SDV’s
performance to how it would behave in the real world for
the same scenario. Fig. 1 shows additional simulations of
the autonomy on safety critical scenarios such as an actor
cutting into our lane or an oncoming actor in our lane. The
SDV then lane changes, and with UniSim we can simulate
the sensor data realistically throughout the scenario. Please
see supp. video for complete visuals.
5. Conclusion
In this paper, we leveraged real world scenarios col-
lected by a mobile platform to build a high-fidelity virtual
world for autonomy testing. Towards this goal, we pre-
sented UniSim, a neural sensor simulator that takes in a
sequence of LiDAR and camera data and can decompose
and reconstruct the dynamic actors and static background
in the scene, allowing us to create new scenarios and render
sensor observations of those new scenarios from new view-
points. UniSim improves over SoTA and generates realistic
sensor data with much lower domain gap. Furthermore, we
demonstrated that we can use it to evaluate an autonomy
system in closed loop on novel safety-critical scenarios.
Such a simulator can accurately measure self-driving per-
formance, as if it were actually in the real world, but with-
out the safety hazards, and in a much less capital-intensive
manner. We hope UniSim will enable developing safer au-
tonomy systems more efficiently and safely. Future work
involves explicitly modelling and manipulating scene light-
ing [6,71,102], weather [39], and articulated actors [80].
8


## Page 9

Acknowledgements:
We thank Ioan-Andrei Barsan for
profound discussion and constructive feedback. We thank
the Waabi team for their valuable assistance and support.
References
[1] Kara-Ali Aliev, Artem Sevastopolsky, Maria Kolos, Dmitry
Ulyanov, and Victor Lempitsky. Neural point-based graph-
ics. In ECCV, 2020. 3
[2] Alexander Amini, Igor Gilitschenski, Jacob Phillips, Julia
Moseyko, Rohan Banerjee, Sertac Karaman, and Daniela
Rus. Learning robust control policies for end-to-end au-
tonomous driving from data-driven simulation. IEEE RA-L,
2020. 3
[3] Alexander Amini, Tsun-Hsuan Wang, Igor Gilitschenski,
Wilko Schwarting, Zhijian Liu, Song Han, Sertac Karaman,
and Daniela Rus. VISTA 2.0: An open, data-driven sim-
ulator for multimodal sensing and policy learning for au-
tonomous vehicles. In ICRA, 2022. 3
[4] Jonathan T Barron, Ben Mildenhall, Matthew Tancik, Pe-
ter Hedman, Ricardo Martin-Brualla, and Pratul P Srini-
vasan.
Mip-NeRF: A multiscale representation for anti-
aliasing neural radiance fields. In ICCV, 2021. 3
[5] Jonathan T Barron, Ben Mildenhall, Dor Verbin, Pratul P
Srinivasan, and Peter Hedman.
Mip-NeRF 360:
Un-
bounded anti-aliased neural radiance fields. In CVPR, 2022.
4, 13
[6] Mark Boss, Varun Jampani, Raphael Braun, Ce Liu,
Jonathan Barron, and Hendrik Lensch. Neural-PIL: Neural
pre-integrated lighting for reflectance decomposition. 2021.
8, 22
[7] Greg Brockman, Vicki Cheung, Ludwig Pettersson, Jonas
Schneider,
John Schulman,
Jie Tang,
and Wojciech
Zaremba. OpenAI gym. arXiv, 2016. 2
[8] Rohan Chabra, Jan E Lenssen, Eddy Ilg, Tanner Schmidt,
Julian Straub, Steven Lovegrove, and Richard Newcombe.
Deep local shapes: Learning local sdf priors for detailed 3d
reconstruction. In ECCV, 2020. 3
[9] Eric R Chan, Connor Z Lin, Matthew A Chan, Koki
Nagano, Boxiao Pan, Shalini De Mello, Orazio Gallo,
Leonidas J Guibas, Jonathan Tremblay, Sameh Khamis,
et al. Efficient geometry-aware 3D generative adversarial
networks. In CVPR, 2022. 5
[10] Yun Chen, Frieda Rong, Shivam Duggal, Shenlong Wang,
Xinchen Yan, Sivabalan Manivasagam, Shangjie Xue, Ersin
Yumer, and Raquel Urtasun. Geosim: Realistic video simu-
lation via geometry-aware composition for self-driving. In
CVPR, 2021. 3
[11] Zhiqin Chen, Thomas Funkhouser, Peter Hedman, and An-
drea Tagliasacchi. Mobilenerf: Exploiting the polygon ras-
terization pipeline for efficient neural field rendering on
mobile architectures. arXiv, 2022. 14
[12] Julian Chibane, Thiemo Alldieck, and Gerard Pons-Moll.
Implicit functions in feature space for 3D shape reconstruc-
tion and completion. In CVPR, 2020. 4
[13] Erwin Coumans and Yunfei Bai. PyBullet, a python mod-
ule for physics simulation for games, robotics and machine
learning. 2016. 2
[14] Henggang Cui, Vladan Radosavljevic, Fang-Chieh Chou,
Tsung-Han Lin, Thi Nguyen, Tzu-Kuo Huang, Jeff Schnei-
der, and Nemanja Djuric. Multimodal trajectory predictions
for autonomous driving using deep convolutional networks.
ICRA, 2019. 8, 16, 18
[15] Rosen Diankov and James Kuffner. OpenRAVE: A plan-
ning architecture for autonomous robotics. Robotics Insti-
tute, Pittsburgh, PA, Tech. Rep. CMU-RI-TR-08-34, 2008.
2
[16] Alexey Dosovitskiy, German Ros, Felipe Codevilla, Anto-
nio Lopez, and Vladlen Koltun. CARLA: An open urban
driving simulator. CoRL, 2017. 2
[17] Jin Fang, Dingfu Zhou, Feilong Yan, Tongtong Zhao, Feihu
Zhang, Yu Ma, Liang Wang, and Ruigang Yang.
Aug-
mented LiDAR simulator for autonomous driving. IEEE
RA-L, 2020. 3
[18] Jin Fang, Xinxin Zuo, Dingfu Zhou, Shengze Jin, Sen
Wang, and Liangjun Zhang.
LiDAR-Aug:
A general
rendering-based augmentation framework for 3D object de-
tection. In CVPR, 2021. 3
[19] James J Gibson. The ecological approach to visual percep-
tion: classic edition. 2014. 2
[20] Adam A Goodenough and Scott D Brown. Dirsig 5: core
design and implementation. In Algorithms and Technolo-
gies for Multispectral, Hyperspectral, and Ultraspectral
Imagery XVIII, 2012. 2
[21] Amos Gropp, Lior Yariv, Niv Haim, Matan Atzmon, and
Yaron Lipman. Implicit geometric regularization for learn-
ing shapes. In ICML, 2020. 5
[22] Michael Gschwandtner, Roland Kwitt, Andreas Uhl, and
Wolfgang Pree. Blensor: Blender sensor simulation tool-
box.
In International Symposium on Visual Computing,
2011. 2
[23] Michelle Guo, Alireza Fathi, Jiajun Wu, and Thomas
Funkhouser. Object-centric neural scene rendering. arXiv,
2020. 4
[24] David Ha, Andrew Dai, and Quoc V Le. Hypernetworks.
ICLR, 2016. 4
[25] Martin Heusel, Hubert Ramsauer, Thomas Unterthiner,
Bernhard Nessler, and Sepp Hochreiter. Gans trained by
a two time-scale update rule converge to a local nash equi-
librium. In NeurIPS, 2017. 7
[26] Judy Hoffman, Eric Tzeng, Taesung Park, Jun-Yan Zhu,
Phillip Isola, Kate Saenko, Alexei Efros, and Trevor Dar-
rell. CyCADA: Cycle-consistent adversarial domain adap-
tation. In ICML, 2018. 2
[27] Yuanming Hu, Jiancheng Liu, Andrew Spielberg, Joshua B
Tenenbaum, William T Freeman, Jiajun Wu, Daniela Rus,
and Wojciech Matusik. Chainqueen: A real-time differen-
tiable physical simulator for soft robotics. In ICRA, 2019.
2
[28] Louis Hugues and Nicolas Bredeche.
Simbad: an au-
tonomous robot simulation package for education and re-
search. In International Conference on Simulation of Adap-
tive Behavior, 2006. 2
[29] Maximilian Igl, Daewoo Kim, Alex Kuefler, Paul Mou-
gin, Punit Shah, Kyriacos Shiarlis, Dragomir Anguelov,
9


## Page 10

Mark Palatucci, Brandyn White, and Shimon Whiteson.
Symphony: Learning realistic and diverse agents for au-
tonomous driving simulation. arXiv, 2022. 14
[30] Brian Karis and Epic Games. Real shading in unreal engine
4. Proc. Physically Based Shading Theory Practice, 2013.
2
[31] Pradeep K Khosla and Takeo Kanade. Parameter identifica-
tion of robot dynamics. In 1985 24th IEEE conference on
decision and control, 1985. 2
[32] Seung Wook Kim, Jonah Philion, Antonio Torralba, and
Sanja Fidler.
DriveGAN: Towards a controllable high-
quality neural simulation. In CVPR, 2021. 3
[33] Nathan Koenig and Andrew Howard.
Design and use
paradigms for gazebo, an open-source multi-robot simula-
tor. In IROS, 2004. 2
[34] Karsten Kreutz and Julian Eggert. Analysis of the general-
ized intelligent driver model (gidm) for uncontrolled inter-
sections. In ITSC, 2021. 14
[35] Abhijit Kundu, Kyle Genova, Xiaoqi Yin, Alireza Fathi,
Caroline Pantofaru, Leonidas J Guibas, Andrea Tagliasac-
chi, Frank Dellaert, and Thomas Funkhouser. Panoptic neu-
ral fields: A semantic object-aware neural scene represen-
tation. In CVPR, 2022. 3, 4
[36] Beatriz Le´on, Stefan Ulbrich, Rosen Diankov, Gustavo
Puche, Markus Przybylski, Antonio Morales, Tamim As-
four, Sami Moisio, Jeannette Bohg, James Kuffner, et al.
Opengrasp: a toolkit for robot grasping simulation. In In-
ternational conference on simulation, modeling, and pro-
gramming for autonomous robots, 2010. 2
[37] Chengshu Li, Fei Xia, Roberto Mart´ın-Mart´ın, Michael
Lingelbach, Sanjana Srivastava, Bokui Shen, Kent Vainio,
Cem Gokmen, Gokul Dharan, Tanish Jain, et al. igibson
2.0: Object-centric simulation for robot learning of every-
day household tasks. CoRL, 2021. 2
[38] Wei Li, CW Pan, Rong Zhang, JP Ren, YX Ma, Jin Fang,
FL Yan, QC Geng, XY Huang, HJ Gong, et al. Aads: Aug-
mented autonomous driving simulation using data-driven
algorithms. Science robotics, 2019. 3
[39] Yuan Li, Zhi-Hao Lin, David Forsyth, Jia-Bin Huang, and
Shenlong Wang.
ClimateNeRF: Physically-based neural
rendering for extreme climate synthesis.
arXiv e-prints,
pages arXiv–2211, 2022. 8
[40] Zhiqi Li, Wenhai Wang, Hongyang Li, Enze Xie, Chong-
hao Sima, Tong Lu, Qiao Yu, and Jifeng Dai. Bevformer:
Learning bird’s-eye-view representation from multi-camera
images via spatiotemporal transformers. In ECCV, 2022. 8,
16
[41] Yiyi Liao, Jun Xie, and Andreas Geiger. Kitti-360: A novel
dataset and benchmarks for urban scene understanding in
2d and 3d. PAMI, 2022. 7
[42] Lingjie Liu, Jiatao Gu, Kyaw Zaw Lin, Tat-Seng Chua, and
Christian Theobalt. Neural sparse voxel fields. In NeurIPS,
2020. 3
[43] Stephen Lombardi, Tomas Simon, Jason Saragih, Gabriel
Schwartz, Andreas Lehrmann, and Yaser Sheikh. Neural
volumes: Learning dynamic renderable volumes from im-
ages. In SIGGRAPH, 2019. 3
[44] Ilya Loshchilov and Frank Hutter. Decoupled weight decay
regularization. arXiv, 2017. 16
[45] Alexander Majercik, Cyril Crassin, Peter Shirley, and Mor-
gan McGuire.
A ray-box intersection algorithm and ef-
ficient dynamic voxel rendering.
Journal of Computer
Graphics Techniques Vol, 2018. 6
[46] Sivabalan Manivasagam, Shenlong Wang, Kelvin Wong,
Wenyuan Zeng, Mikita Sazanovich, Shuhan Tan, Bin Yang,
Wei-Chiu Ma, and Raquel Urtasun. Lidarsim: Realistic li-
dar simulation by leveraging the real world. In CVPR, 2020.
3, 6, 7, 15, 19, 20, 21
[47] Julien NP Martel, David B Lindell, Connor Z Lin, Eric R
Chan, Marco Monteiro, and Gordon Wetzstein.
Acorn:
Adaptive coordinate networks for neural scene representa-
tion. TOG, 2021. 3
[48] Lars Mescheder, Michael Oechsle, Michael Niemeyer, Se-
bastian Nowozin, and Andreas Geiger.
Occupancy net-
works: Learning 3d reconstruction in function space. In
CVPR, 2019. 4
[49] Olivier Michel.
Cyberbotics ltd. webots™: professional
mobile robot simulation. International Journal of Advanced
Robotic Systems, 2004. 2
[50] Ben Mildenhall, Pratul P Srinivasan, Matthew Tancik,
Jonathan T Barron, Ravi Ramamoorthi, and Ren Ng. Nerf:
Representing scenes as neural radiance fields for view syn-
thesis. ECCV, 2020. 3, 4
[51] Thomas M¨uller,
Alex Evans,
Christoph Schied,
and
Alexander Keller. Instant neural graphics primitives with
a multiresolution hash encoding. 2022. 3, 4, 6, 7, 13, 14
[52] Thomas Neff, Pascal Stadlbauer, Mathias Parger, Andreas
Kurz, Joerg H Mueller, Chakravarty R Alla Chaitanya, An-
ton Kaplanyan, and Markus Steinberger. Donerf: Towards
real-time rendering of compact neural radiance fields us-
ing depth oracle networks. In Computer Graphics Forum,
2021. 3
[53] Charles P Neuman and John J Murray.
Computational
robot dynamics: Foundations and applications. Journal of
Robotic Systems, 1985. 2
[54] Michael Niemeyer and Andreas Geiger. Giraffe: Repre-
senting scenes as compositional generative neural feature
fields. In CVPR, 2021. 4, 5
[55] Julian Ost, Issam Laradji, Alejandro Newell, Yuval Bahat,
and Felix Heide. Neural point light fields. In CVPR, 2022.
3
[56] Julian Ost, Fahim Mannan, Nils Thuerey, Julian Knodt, and
Felix Heide. Neural scene graphs for dynamic scenes. In
CVPR, 2021. 3, 4, 6, 7
[57] Keunhong Park, Utkarsh Sinha, Jonathan T Barron, Sofien
Bouaziz, Dan B Goldman, Steven M Seitz, and Ricardo
Martin-Brualla. Nerfies: Deformable neural radiance fields.
In ICCV, 2021. 22
[58] Steven G Parker, James Bigler, Andreas Dietrich, Heiko
Friedrich, Jared Hoberock, David Luebke, David McAllis-
ter, Morgan McGuire, Keith Morley, Austin Robison, et al.
Optix: a general purpose ray tracing engine. TOG, 2010. 2,
15
10


## Page 11

[59] Sida Peng, Yuanqing Zhang, Yinghao Xu, Qianqian Wang,
Qing Shuai, Hujun Bao, and Xiaowei Zhou. Neural body:
Implicit neural representations with structured latent codes
for novel view synthesis of dynamic humans. In CVPR,
2021. 22
[60] Ruslan Rakhimov, Andrei-Timotei Ardelean, Victor Lem-
pitsky, and Evgeny Burnaev. Npbg++: Accelerating neural
point-based graphics. In CVPR, 2022. 3
[61] Daniel Rebain, Wei Jiang, Soroosh Yazdani, Ke Li,
Kwang Moo Yi, and Andrea Tagliasacchi. Derf: Decom-
posed radiance fields. In CVPR, 2021. 3
[62] Christian Reiser, Songyou Peng, Yiyi Liao, and Andreas
Geiger. KiloNeRF: Speeding up neural radiance fields with
thousands of tiny MLPs. In ICCV, 2021. 3
[63] Konstantinos Rematas,
Andrew Liu,
Pratul P Srini-
vasan, Jonathan T Barron, Andrea Tagliasacchi, Thomas
Funkhouser, and Vittorio Ferrari. Urban radiance fields. In
CVPR, 2022. 3
[64] Gernot Riegler and Vladlen Koltun. Free view synthesis. In
ECCV, 2020. 3, 6, 7, 8
[65] Gernot Riegler and Vladlen Koltun. Stable view synthesis.
In CVPR, 2021. 3
[66] Abbas Sadat, Mengye Ren, Andrei Pokrovsky, Yen-Chen
Lin, Ersin Yumer, and Raquel Urtasun. Jointly learnable
behavior and trajectory planning for self-driving vehicles.
IROS, 2019. 8, 16
[67] Manolis Savva, Abhishek Kadian, Oleksandr Maksymets,
Yili Zhao, Erik Wijmans, Bhavana Jain, Julian Straub, Jia
Liu, Vladlen Koltun, Jitendra Malik, et al. Habitat: A plat-
form for embodied ai research. In ICCV, 2019. 2
[68] Shital Shah, Debadeepta Dey, Chris Lovett, and Ashish
Kapoor. AirSim: High-fidelity visual and physical simula-
tion for autonomous vehicles. In Field and service robotics,
2018. 2
[69] Dave Shreiner, Bill The Khronos OpenGL ARB Working
Group, et al.
OpenGL programming guide: the official
guide to learning OpenGL, versions 3.0 and 3.1. 2009. 2
[70] Karen Simonyan and Andrew Zisserman. Very deep con-
volutional networks for large-scale image recognition. In
ICLR, 2015. 5
[71] Pratul P. Srinivasan, Boyang Deng, Xiuming Zhang,
Matthew Tancik, Ben Mildenhall, and Jonathan T. Barron.
NeRV: Neural reflectance and visibility fields for relighting
and view synthesis. In CVPR, 2021. 8, 22
[72] Cheng Sun, Min Sun, and Hwann-Tzong Chen.
Direct
voxel grid optimization: Super-fast convergence for radi-
ance fields reconstruction. In CVPR, 2022. 4
[73] Simon Suo, Sebastian Regalado, Sergio Casas, and Raquel
Urtasun. Trafficsim: Learning to simulate realistic multi-
agent behaviors. In CVPR, 2021. 14
[74] Towaki Takikawa, Joey Litalien, Kangxue Yin, Karsten
Kreis, Charles Loop, Derek Nowrouzezahrai, Alec Jacob-
son, Morgan McGuire, and Sanja Fidler. Neural geomet-
ric level of detail: Real-time rendering with implicit 3D
shapes. In CVPR, 2021. 4
[75] Abhijeet Tallavajhula, C¸ etin Meric¸li, and Alonzo Kelly.
Off-road lidar simulation with data-driven terrain primi-
tives. In ICRA, 2018. 3
[76] Matthew Tancik, Vincent Casser, Xinchen Yan, Sabeek
Pradhan, Ben Mildenhall, Pratul P. Srinivasan, Jonathan T.
Barron, and Henrik Kretzschmar. Block-NeRF: Scalable
large scene neural view synthesis. In CVPR, 2022. 3
[77] Emanuel Todorov, Tom Erez, and Yuval Tassa. Mujoco: A
physics engine for model-based control. In IROS, 2012. 2
[78] Martin Treiber, Ansgar Hennecke, and Dirk Helbing. Con-
gested traffic states in empirical observations and micro-
scopic simulations. Physical Review E, 2000. 14
[79] Dor Verbin, Peter Hedman, Ben Mildenhall, Todd Zick-
ler, Jonathan T Barron, and Pratul P Srinivasan. Ref-nerf:
Structured view-dependent appearance for neural radiance
fields. In CVPR, 2022. 3
[80] Jingkang Wang, Sivabalan Manivasagam, Yun Chen, Ze
Yang, Ioan Andrei Bˆarsan, Anqi Joyce Yang, Wei-Chiu Ma,
and Raquel Urtasun. CADSim: Robust and scalable in-the-
wild 3d reconstruction for controllable sensor simulation.
In Conference on Robot Learning, 2022. 3, 8
[81] Jingkang Wang, Ava Pun, James Tu, Sivabalan Mani-
vasagam, Abbas Sadat, Sergio Casas, Mengye Ren, and
Raquel Urtasun. Advsim: Generating safety-critical sce-
narios for self-driving vehicles. In CVPR, 2021. 3
[82] Peng Wang, Lingjie Liu, Yuan Liu, Christian Theobalt,
Taku Komura, and Wenping Wang. NeuS: Learning neural
implicit surfaces by volume rendering for multi-view recon-
struction. In NeurIPS, 2021. 4
[83] Ting-Chun Wang, Ming-Yu Liu, Jun-Yan Zhu, Andrew Tao,
Jan Kautz, and Bryan Catanzaro. High-resolution image
synthesis and semantic manipulation with conditional gans.
In CVPR, 2018. 5
[84] Tsun-Hsuan Wang, Alexander Amini, Wilko Schwarting,
Igor Gilitschenski, Sertac Karaman, and Daniela Rus.
Learning interactive driving policies via data-driven sim-
ulation. In ICRA, 2022. 3
[85] Zhou Wang, Alan C Bovik, Hamid R Sheikh, and Eero P
Simoncelli. Image quality assessment: from error visibility
to structural similarity. TIP, 2004. 7
[86] Zian Wang, Wenzheng Chen, David Acuna, Jan Kautz, and
Sanja Fidler. Neural light field estimation for street scenes
with differentiable virtual object insertion. ECCV, 2022. 3
[87] Bichen Wu, Xuanyu Zhou, Sicheng Zhao, Xiangyu Yue,
and Kurt Keutzer. SqueezeSegV2: Improved model struc-
ture and unsupervised domain adaptation for road-object
segmentation from a LiDAR point cloud. In ICRA, 2019.
2
[88] Bernhard
Wymann,
Eric
Espi´e,
Christophe
Guion-
neau, Christos Dimitrakakis, R´emi Coulom, and An-
drew Sumner.
Torcs, the open racing car simulator.
http://torcs.sourceforge.net, 2000. 2
[89] Pengchuan Xiao, Zhenlei Shao, Steven Hao, Zishuo Zhang,
Xiaolin Chai, Judy Jiao, Zesong Li, Jian Wu, Kai Sun, Kun
Jiang, et al. Pandaset: Advanced sensor suite dataset for
autonomous driving. In ITSC, 2021. 6
[90] Tianhan Xu and Tatsuya Harada. Deforming radiance fields
with cages. In ECCV, 2022. 22
[91] Bin Yang, Wenjie Luo, and Raquel Urtasun. Pixor: Real-
time 3d object detection from point clouds. In CVPR, 2018.
21
11


## Page 12

[92] Zhenpei Yang, Yuning Chai, Dragomir Anguelov, Yin
Zhou, Pei Sun, Dumitru Erhan, Sean Rafferty, and Hen-
rik Kretzschmar. SurfelGAN: Synthesizing realistic sensor
data for autonomous driving. In CVPR, 2020. 3
[93] Ze Yang, Sivabalan Manivasagam, Yun Chen, Jingkang
Wang, Rui Hu, and Raquel Urtasun. Reconstructing ob-
jects in-the-wild for realistic sensor simulation. In ICRA,
2023. 3
[94] Ze Yang, Siva Manivasagam, Ming Liang, Bin Yang, Wei-
Chiu Ma, and Raquel Urtasun. Recovering and simulating
pedestrians in the wild. In CoRL, 2020. 3
[95] Ze Yang, Shenlong Wang, Siva Manivasagam, Zeng Huang,
Wei-Chiu Ma, Xinchen Yan, Ersin Yumer, and Raquel Ur-
tasun. S3: Neural shape, skeleton, and skinning fields for
3d human modeling. In CVPR, 2021. 3
[96] Lior Yariv, Yoni Kasten, Dror Moran, Meirav Galun, Matan
Atzmon, Basri Ronen, and Yaron Lipman. Multiview neu-
ral surface reconstruction by disentangling geometry and
appearance. In NeurIPS, 2020. 4
[97] Alex Yu, Ruilong Li, Matthew Tancik, Hao Li, Ren Ng, and
Angjoo Kanazawa. Plenoctrees for real-time rendering of
neural radiance fields. In ICCV, 2021. 14
[98] Zehao Yu, Songyou Peng, Michael Niemeyer, Torsten Sat-
tler, and Andreas Geiger. Monosdf: Exploring monocular
geometric cues for neural implicit surface reconstruction.
In NeurIPS, 2022. 4
[99] Yu-Jie Yuan, Yang-Tian Sun, Yu-Kun Lai, Yuewen Ma,
Rongfei Jia, and Lin Gao. Nerf-editing: geometry editing
of neural radiance fields. In CVPR, 2022. 22
[100] Kai Zhang, Gernot Riegler, Noah Snavely, and Vladlen
Koltun. NeRF++: Analyzing and improving neural radi-
ance fields. arXiv, 2020. 3, 4, 13, 14
[101] Richard Zhang, Phillip Isola, Alexei A Efros, Eli Shecht-
man, and Oliver Wang. The unreasonable effectiveness of
deep features as a perceptual metric. In CVPR, 2018. 5, 7
[102] Xiuming Zhang, Pratul P Srinivasan, Boyang Deng, Paul
Debevec, William T Freeman, and Jonathan T Barron. Ner-
factor: Neural factorization of shape and reflectance under
an unknown illumination. TOG, 2021. 8, 22
[103] Qian-Yi Zhou, Jaesik Park, and Vladlen Koltun. Open3d:
A modern library for 3d data processing. arXiv, 2018. 14
[104] Yi Zhou, Connelly Barnes, Jingwan Lu, Jimei Yang, and
Hao Li.
On the continuity of rotation representations in
neural networks. In CVPR, 2019. 13
12


## Page 13

Appendix
In the supplementary material, we provide implementation details, experiment setting details, additional qualitative visu-
alizations and metrics, and limitations of our method. We first provide details about UniSim in Sec. A1. Then in Sec. A2 we
provide additional details on the baseline model implementations and how we adapt them to our sensor simulation setting.
In Sec. A3 we explain in more detail our experimental setting for the experiments in the main paper. Next, we showcase
additional visualizations and metrics for camera and LiDAR in Sec. A4. Finally, we analyze the limitations of our model in
Sec. A5. Please refer to our project page https://waabi.ai/research/unisim/ for an overview of our methodol-
ogy and video results on the various capabilities of UniSim and closed-loop autonomy simulations.
A1. UniSim Details
Scene Representation Details:
We begin by defining the region of interest for the static scene based on the trajectory of
the self-driving vehicle (SDV). The scene extends 80 meters behind the SDV position at the first frame, and 80 meters ahead
of the SDV position at the last frame. The scene width is 120 meters and the scene height is 40 meters. Please see Figure 7
for a birds-eye-view illustration of our region of interest.
Next, we generate an occupancy grid for the scene volume (see Section 3.2 in the main paper) and model it using multi-
resolution feature grids. For distant regions outside the volume, we employ a background model similar to [5, 100]. For
dynamic actors, each actor model is represented by an independent multi-resolution feature grids generated from a shared
HyperNet. Following [51], we use a spatial hash function to map each feature grid to a fixed number of features.
SDV at first frame
SDV at last frame
80 m
80 m
60 m
60 m
Figure 7. Region of interest of our scene representation.
Neural Feature Fields (NFFs) Details:
To obtain the geometry s and feature descriptor f from the features grid for both
the static scene and actors (Eq. 1 in main paper), we employ two networks, denoted as fbg and fA. Each of these networks
consists of two sub-networks. The first sub-network is an MLP that takes the interpolated feature {interp(x, Gl)}L
l=1
and predicts the geometry s (signed distance value) and intermediate geometry feature, the second sub-network is an MLP
takes the intermediate geometry feature and viewpoint encoding as input and predicts the neural feature descriptor f. A
convolutional neural network grgb is applied on top of the rendered feature map and produces the final image. We also have
an additional decoder for lidar intensity (gint).
Actor Model Details:
Although we assume the dynamic actor tracklets are provided, they might be inaccurate, even when
human-annotated, and lead to blurry results. We find it advantageous to refine the actor tracklets during training. For each
dynamic actor Ai with trajectory initialized by a sequence of SE(3) poses {Tt
Ai}T
t=1, we jointly optimize the rotation and
translation components of the poses at each timestamp. We parameterize the rotation component using a 6D representa-
tion [104]. We also incorporate a symmetry prior along the longitudinal axis for vehicle objects, which are the most common
actors in self-driving scenes. Specifically, we denote the query points and view direction in the canonical object coordinate
(Front-Left-Up) as xAi and dAi. During training, we randomly flip the input point and view direction when querying the
neural feature fields:
  
\m a
t
h
b
f
 
x
'_
{
\
m
a
t
h cal 
A_
i}  
=
 
\
b
e
g
in
 
{
p
m
a
t rix} 1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 1 \end {pmatrix} \mathbf x_{\mathcal A_i},\quad \mathbf d'_{\mathcal A_i} = \begin {pmatrix} 1 & 0 & 0 \\ 0 & -1 & 0 \\ 0 & 0 & 1 \\ \end {pmatrix} \mathbf d_{\mathcal A_i}
(11)
13


## Page 14

Actor Behavior Model for Closed-loop Simulation:
For simplicity, we modelled the counterfactual actor behaviors with
heuristics. While we only demonstrated human-specified trajectories in the paper, it is intuitive to to incorporate other models
to control actors’ behaviors, such as intelligent driver models [34,78] or deep-learning based models [29,73].
Run-time and Resources:
Table 7 reports training/inference time for UniSim and baselines on an A5000 GPU for a
scenario with 31 actors (Figure 6 row 1). We believe the run-time can be further optimized with recent advancements [11,97]
and code optimization (e.g., customized CUDA kernels). We can also balance run-time and realism by adjusting the image
resolution, lidar rays sent, and the number of points sampled along the ray.
Train (Hour) ↓
Camera (FPS) ↑
LiDAR (FPS) ↑
FVS[57]
≈24
0.33
-
NSG[51]
≈20
0.06
-
Instant-NGP[46]
0.11
2.60
-
Ours
1.67
1.25
11.76
Table 7. Comparison of training speed, inference speed for camera image (1080p) and LiDAR frame (≈77k rays per frame).
A2. Implementation Details for Baselines
A2.1. Free View Synthesis (FVS)
One key component of FVS is that it requires a proxy geometry to perform warping. Instead of using COLMAP to perform
structure-from-motion as in the original paper, we take advantage of the fact that the data collection platform records accurate
LiDAR depth information for the scene. For the static scene, we aggregate LiDAR points across all frames with dynamic
points removed and then create triangle surfels for them. We first estimate per-point normals from 200 nearest neighbors,
and then we downsample the points into 4cm3 voxels [103]. After that, triangle surfels are created with a 5cm radius.
This includes static vehicles. For dynamic objects, we create surfels from aggregated point clouds using human labeled 3D
bounding boxes as correspondence. To enhance the photorealism of the rendered images, we also add the same adversarial
loss as in UniSim, which helps produce higher quality results.
To render a target image, a few source images need to be selected for warping. During training, we randomly select
from nearby frames (10 frames before and 10 frames after). To test the interpolation during inference, we select the 2 most
nearby frames. To test the lane shift, we select every 4 frames starting from 12 frames before to 4 frames after current
frame. We heuristically tried multiple settings and found this setting usually achieves better balance between performance
and efficiency. Fewer source images will result in images with large unseen region, and the network may fail to inpaint it.
More source images may produce blurry results because of geometry misalignment and runs out-of-memory on the GPU.
The FVS is trained on 2 A5000 GPUs with learning rate 0.0001, batch size 8 for 50, 000 iterations. Images are cropped to
256 × 256 patches during training.
A2.2. Instant-NGP
Instant-NGP [51] achieves state-of-the-art NeRF rendering by introducing an efficient hash encoding, accelerated ray
sampling and fully fused MLPs. In our experiments, we scale the PandaSet scenes to fully occupy the unit cube and set
aabb scale as 32 to handle the background regions (e.g., far-away buildings and sky) outside the unit cube. We tuned
aabb scale to be 1, 2, 4, 8, 16, 32, 64 and find 32 leads to the best performance. The model is trained for 20K iterations
and converges on the training views. However, we find there are obvious artifacts including floating particles and large
missing regions on the ground. This is due to the radiance-geometry ambiguity [100] and limited viewpoints that are sparse
and far apart in the driving scenarios compared to dense indoor scenes. Therefore, to improve the geometry for better
extrapolation (e.g., lane shift), we enhance the original method with LiDAR depth supervision. Specifically, we aggregate
the recorded LiDAR data and create a surfel triangle representation. We follow the same surfel asset generation pipeline as
stated in the implementation of FVS (see Sec. A2.1). We then use the surfel mesh representation to render a depth image
at each camera training viewpont. We also tried to ignore the dynamic actors with rendered object masks but it leads to
worse performance in terms of PSNR since all dynamic actors are removed. We use the official repository 1 (commit id:
ca21fd399d0eec4d85fd31ac353116bc088f3f75, Oct 19, 2022) for our experiments.
1https://github.com/NVlabs/instant-ngp
14


## Page 15

w. CNN
w.o. CNN
GT
Interpolation
Lane shift
w. CNN
w.o. CNN
GT
Figure 8. Effects of CNN Decoder. The convolutional RGB decoder helps to make the rendered image more clean and learn more details.
w. shape prior
w.o. shape prior
w. shape prior
w.o. shape prior
Figure 9. Effects of actor shape prior. We show the unobserved side of the vehicle after SDV lane change, incorporating actor shape
prior helps to reconstruct unobserved side of the vehicle.
A2.3. Neural Scene Graph (NSG)
We use the codebase on GitHub2 and adopt the default setting for the model and training parameters. For data preprocess-
ing, only dynamic vehicles are considered as object nodes, static vehicles are considered as part of the background. Also, we
only select five dynamic actors that are the most present in the log due to memory limitations. We find with a larger number
of actors the model runs out-of-memory during data loading on a 128GB memory machine because our image data is higher
resolution (1920 × 1080) than the KITTI data (1242 × 375). NSG only works well on front-facing scenarios with only small
movements along the camera viewing direction. We tried to improve the background modeling by increasing the background
points sampling and increasing model size. However, we did not see significant improvement in the visual quality, while also
making the computation cost much more expensive. Therefore, we stick to the default setting.
A2.4. LiDARsim
We re-implement LiDARsim based on OptiX ray tracing engine [58]. We first create the asset bank following [46]:
Specifically, for background assets, we aggregate the LiDAR points across all the frames and remove all actors using 3D
bounding box annotations. For dynamic actors, we aggregate the LiDAR points inside the bounding boxes in the object-
centric coordinate. We then estimate per-point normals from 200 nearest neighbors with a radius of 20cm and orient the
normals upwards for flat ground reconstruction. We downsample the LiDAR points into 8cm voxels and create per-point
triangle faces (radius 10cm) according to the estimated normals. Note that we also track the per-point intensity values
during the above post-processing. Given the asset bank, we place the background and all actors in its original locations and
transform the scene to the LiDAR coordinate for ray-triangle intersections computation. For LiDAR realism experiments,
we created surfel assets using training frames (0, 2, 4, · · · , 78) and performed raycasting using real LiDAR rays on held-out
frames (1, 3, 5, · · · , 79). For perception evaluation and training, the assets assets are created and raycasted with all 80 frames.
Instead of using real LiDAR rays which are infeasible to obtain in real-world simulation, we set the sensor intrinsics (e.g.,
beam angle, azimuth resolution, etc) based on the public documents and raw LiDAR information 3.
2https://github.com/princeton-computational-imaging/neural-scene-graphs
3https://github.com/scaleapi/pandaset-devkit/issues/67
15


## Page 16

w. tracklet optimization
w.o. tracklet optimization
w. tracklet optimization
w.o. tracklet optimization
GT
GT
Figure 10. Effects of tracklet refinment. Tracklet refinement helps to learn sharp details for dynamic actors.
A3. UniSim Experiment Details
A3.1. Image Similarity Metrics
Due to limited computation resources available to run NSG on all the logs in PandaSet, 10 scenes were selected for image
similarity evaluation: 001,011,016,028,053,063,084,106,123,158. These scenes include a variety of both city
and suburban areas, includes one night log (063), and one log containing no dynamic actors (028). These 10 scenes are of
a subset of the 24 selected for perception validation, described in the following section.
A3.2. Perception Evaluation and Training
To study whether the sensor simulation is realistic with respect how autonomy perceives it,
we first an-
alyze
the
domain
gap
for
perception
tasks.
Specifically,
we
leveraged
the
state-of-the-art
camera-based
brids-eye-view
(BEV)
detection
model
BEVFormer
[40]
and
evaluate
on
the
full
PandaSet.
Since
there
are no official train/val splits available,
we split PandaSet into 79 and 24 sequences as training and val-
idation
sets
by
considering
geographic
locations,
time
span
and
day-night
variety.
Specifically,
we
se-
lect
the
sequences
001,011,013,016,017,028,029,032,053,054,063,065,068,072,084,
086,090,103,106,110,112,115,123,158 as validation set and leave other 79 sequences as training.
We consider two setups (a) Real2Sim: evaluating the perception model trained on real data on simulated data; (b)
Sim2Real: training perception models with simulated data data and testing on real data. Specifically, we evaluate the
real model on 24 simulated validation logs for Real2Sim and train perception models with 79 simulated training logs for
Sim2Real. For data augmentation experiments, we first use all simulation variations (log-replay, lane shift to the left for 0.5
and 2.0 meters) to train the detector (Sim). Then we combine those simulation data with real data (Sim + Real) to retrain
the detector. Note that for all experiments, we train UniSim and other baselines with all image frames (i.e., frames 0 - 79).
As shown in Table 5 (main paper), incorporating UniSim lane shift variations help autonomy achieve superior detection per-
formance compared to training with real data alone. More rigorous study on how to sufficiently leverage the simulated data
(e.g., advanced actor behavior simulation, actor insertion, camera rotations, etc) is left as future works.
BEVFormer Implementation Details:
We adapt the official repository 4 for the training and evaluation on PandaSet.
Specifically, we focus on single-frame vehicle detection with the front camera. We ignore the actors that are out of the
camera field-of-view during training and evaluation. The models are trained in the vehicle frames with FLU convention (x:
forward, y: left, z: up). The region of interest is set as x ∈[0, 80m], y ∈[−40m, 40m], z ∈[−2m, 6m]. Due to memory
limit, we adopt the BEVFormer-small architecture 5 with a batch size of 2 per GPU. We train the models using AdamW
optimizer [44] for 20 epochs with the cosine learning rate schedule 6. Each model takes around 12 hours to train with 2×
RTX A5000. For data augmentation experiments, we generate the simulated data offline and train the models for 10 epochs
as the datasets become three to four times larger compared to original PandaSet.
A3.3. Open-loop Autonomy Evaluation
Evaluation Set:
In main-paper Sec. 4.5, we ran open-loop autonomy metrics on PandaSet scenes. The prediction [14]
and planning modules [66] require map information to operate, which PandaSet does not have. Maps were annotated for
4https://github.com/fundamentalvision/BEVFormer
5https://github.com/fundamentalvision/BEVFormer/blob/master/projects/configs/bevformer/bevformer_
small.py
6https://pytorch.org/docs/stable/generated/torch.optim.lr_scheduler.CosineAnnealingLR.html
16


## Page 17

FVS
Instant-NGP
Neural Scene Graphs
Ours
Ground-truth
Interpolation
Lane shift
Interpolation
Lane shift
Interpolation
Lane shift
Interpolation
Lane shift
Figure 11. Qualitative comparison on more examples. We show rendering results in both the interpolation and lane-shift test settings.
9 scenes in PandaSet that are in the autonomy validation set. These are a subset of the 10 scenes (excludes 063) used for
quantitative evaluation in main-paper Sec. 4.3 that also have LiDAR semantic segmentation from PandaSet to make map
annotation possible.
Open-loop Autonomy Metrics:
We now describe in more detail the autonomy metrics computed for each module.
For detection, we compute a metric called detection agreement. For detection agreement, we evaluate the real-trained
BEVformer model on the real image and the simulated image, obtaining real-image and simulated-image detection outputs.
We assign the real-image detections as the labels and compute the average precision (AP) between the simulated-image
detections and the real-image detections (set as labels) to report the final result. We compute the detection agreement at
intersection-over-union (IoU) 0.3. This metric measures whether the simulated sensor data generates the same true-positives
and false-positives as the real data at each frame.
For prediction, we compute the prediction average displacement error, where the motion forecasted trajectory is for a 6
17


## Page 18

Real image
FVS
NSG
UniSim
Edit static elements
Actor removal
Actor manip.
Insert cones
Real image
Figure 12. Left: Comparison to baselines on actor removal (top) and manipulation (bottom). Right: Edit static elements by copying cones.
Rendered RGB
Rendered RGB
Rendered normal map
Rendered depth map
Rendered normal map
Rendered depth map
Figure 13. Rendered Scene Geometry. For each example, from left to right: rendered RGB image, rendered normal map, and rendered
depth map.
second horizon at 10Hz frequency. The prediction module selected for the autonomy is from Cui et. al. [14], which takes a
rasterized map and 5 seconds past history tracks for each detected actor as input and outputs 6 second multi-modal trajectory
horizons (number of modes = 6) for each actor. The most-likely prediction mode for each actor generated in the real image
by the prediction model is set as the label. We then evaluate prediction outputs generated by simulated images by identifying
matched actors between the label and predicted, and computing the minimum average displacement error (minADE) across
the 6 predictions for that actor. We report minADE at the maximum F1 score for each simulation method, where a true
positive is defined as a matched detected actor from the simulated sensor data and real sensor data with IoU=0.3.
For planning, we compute the plan consistency metric. At each timestep, the autonomy model outputs a 5 second plan
it would execute given the prediction output and map information. We compute the final displacement error between the 5
second end point when running on real images and when running on simulated images at each timestep.
A4. Additional Experiments and Analysis
A4.1. Ablation Study
Convolutional RGB Decoder:
The Convolutional RGB decoder improves the overall image quality by spatial relation
reasoning and increases model capacity. Figure 8 shows a visual comparison on interpolation and lane shift settings. It can
be seen from the figure that the convolutional RGB decoder helps to make the rendered image more clean and perserve more
details.
Actor Shape Prior:
We incorporate hypernetwork and symmetry prior to learn better assets. Figure 9 shows that incorpo-
rating these actor priors helps to reconstruct unobserved regions of the vehicle when SDV performs a lane shift.
Tracklet Refinement:
We show a visual comparison training a model with and without tracklets optimization in Figure 10.
Optimizing tracklets improves reconstruction of the dynamic actors and makes sharpens their detail.
A4.2. Additional Camera Simulation Results
Realism Evaluation:
Please see Figure 11 for more examples on qualitative comparisons with the baseline models. We
show rendered results in both the interpolation and lane-shift test settings. We also show the comparison to baselines on actor
removal and manipulation in Figure 12 left. Additionally, we visualize the rendered normal (normalized gradient of SDF s)
and depth map in Figure 13.
18


## Page 19

Real
LiDARsim
UniSim (Ours)
Figure 14. Comparison of LiDAR simulation on PandaSet. Left: real lidar sweeps; Middle: simulated point clouds using LiDAR-
sim [46]; Right: simulated point clouds using UniSim. Compared to LiDARsim, our neural rendering approach produces higher-fidelity
LiDAR simulation with less noise and more continuous beam rings that are closer to real LiDAR scans. Note that the UniSim simulation
results are more realistic with respect to how the autonomy perceives it (i.e., smaller Real2Sim and Sim2Real domain gap).
Ours
GT
Limitation on animatable objects
Limitation on unseen objects
Ours (interpolation)
Ours (lane change)
Figure 15. Limitations of UniSim. Left: Our method learns blurry results for animatable objects since we do not model the animation.
Right: Our method has difficult rendering completely unseen objects after performing SDV lane change.
Editing Scene Elements:
Similar to dynamic actors, we can represent and edit static elements using bounding box anno-
tations. Figure 12 right shows we copy the cones to new placements and create new scenarios.
19


## Page 20

Real2Sim (replay)
mAP
AP@0.1
AP@0.3
AP@0.5
AP@0.7
FVS
37.2
63.4
46.7
27.1
11.5
Instant-NGP
22.6
40.9
28.8
15.4
5.4
UniSim
40.2
67.2
50.7
30.8
12.2
Real
40.9
68.1
51.4
31.3
12.7
Table 8. Real2Sim domain gap in replay setting.
Real2Sim (lane-shift)
mAP
AP@0.1
AP@0.3
AP@0.5
AP@0.7
FVS
30.3
54.1
38.9
21.7
6.6
Instant-NGP
18.1
34.3
22.2
11.9
3.8
UniSim
37.0
63.6
47.8
27.2
9.4
Table 9. Real2sim domain gap in lane-shift setting.
Sim2Real (replay)
mAP
AP@0.1
AP@0.3
AP@0.5
AP@0.7
FVS
38.7
66.2
48.8
28.7
11.1
Instant-NGP
34.0
62.3
43.9
22.9
6.7
UniSim
39.9
67.6
51.2
29.4
11.4
Real
40.9
68.1
51.4
31.3
12.7
Table 10. Sim2Real domain gap in replay setting.
Sim2Real (lane-shift)
mAP
AP@0.1
AP@0.3
AP@0.5
AP@0.7
FVS
32.2
59.9
41.5
21.0
6.5
Instant-NGP
26.5
54.3
34.8
13.9
2.9
UniSim
37.1
64.9
47.5
26.4
9.5
Table 11. Sim2Real detection performance in lane-shift setting.
A4.3. Additional LiDAR Simulation Results
To investigate the realism of LiDAR simulation, we compare UniSim with the state-of-the-art approach LiDARsim [46]
in the log-replay setting. Figure 14 show qualitative examples of real LiDAR scans (left), and simulated LiDAR scans using
LiDARsim and UniSim. LiDARsim conducts raycasting with the aggregated surfel meshes and produces incomplete beam
rings and noisy scans. This is because the surfel meshes created with the original LiDAR points can have noisy normal
estimates and incomplete shape. Compared to LiDARsim, the LiDAR sweeps simulated by UniSim is more accurate and
smoother. This is because our neural representations capture the underlying geometry better. Moreover, UniSim can simulate
the intensity values more smoothly and accurately (See the third row in Figure 14).
A4.4. Additional Perception Evaluation and Training for Camera Simulation
We report detailed detection metrics for perception evaluation and training for better reference. Specifically, we report
the average precision (AP) at different IoU thresholds: 0.1, 0.3, 0.5, 0.7. The mean average precision (mAP) is calculated
by mAP = (AP@0.1 + AP@0.3 + AP@0.5 + AP@0.7)/4.0. The Real2Sim results are shown in Table 8 (replay) and
Table 9 (lane-shift). The Sim2Real results are shown in Table 10 (replay) and Table 11 (lane-shift). The data augmentation
experiments are presented in Table 12.
20


## Page 21

Data Augmentation
mAP
AP@0.1
AP@0.3
AP@0.5
AP@0.7
Real
40.9
68.1
51.4
31.3
12.7
Sim (FVS)
39.2
68.0
50.1
28.5
10.1
Sim (Instant-NGP)
32.4
60.7
41.1
21.3
6.6
Sim (UniSim)
41.4
71.4
54.7
29.5
10.1
Real + Sim (FVS)
41.1
71.6
53.6
29.6
9.6
Real + Sim (Instant-NGP)
40.1
70.1
51.5
29.0
9.9
Real + Sim (UniSim)
42.9
71.9
54.3
32.7
12.8
Table 12. Augmenting real data with simulation. Using UniSim data only to train the perception model is even better than training with
all real data. UniSim augmentation yields a significant performance gain. In contrast, baseline data augmentation brings marginal gain or
harms performance
Real2Sim
mAP
AP@0.1
AP@0.3
AP@0.5
AP@0.7
AP@0.8
LiDARsim
74.9
88.3
86.3
82.7
69.1
48.3
UniSim
77.0
90.1
88.4
84.4
71.5
50.8
Real
80.8
93.6
92.0
88.0
75.2
55.2
Table 13. Real2Sim detection performance for LiDAR simulation.
Sim2Real
mAP
AP@0.1
AP@0.3
AP@0.5
AP@0.7
AP@0.8
LIDARsim
75.9
91.6
89.9
85.6
70.6
42.0
UniSim
77.9
92.0
89.8
85.4
72.0
50.3
Real
80.8
93.6
92.0
88.0
75.2
55.2
Table 14. Sim2Real detection performance for LiDAR simulation.
A4.5. Perception Evaluation and Training for LiDAR Simulation
Besides camera simulation, we also analyze if the simulated LiDAR reduces the domain gap for perception tasks com-
pared to an existing SoTA LiDAR simulator LiDARsim [46]. We leveraged the LiDAR-based birds-eye-view detection
model PIXOR [91] and tested Real2Sim and Sim2Real setups. We used the same training validation splits as the camera
perception model and considered the replay setting. Specifically, we use all frames to train the models (creating assets
for LiDARsim) and test with our approximated sensor configurations. We focus on multi-sweep (5 frame) vehicle detec-
tion with a region of interest (ROI) is set as x ∈[0, 80m], y ∈[−40m, 40m], z ∈[−2m, 6m]. We report the average
precision (AP) at different IoU thresholds: 0.1, 0.3, 0.5, 0.7. 0.8. The mean average precision (mAP) is calculated by
mAP = (AP@0.1 + AP@0.3 + AP@0.5 + AP@0.7 + AP@0.8)/5.0.
As shown in Table 13 and Table 14, UniSim results in smaller domain gap in both Real2Sim and Sim2Real compared to
LiDARsim especially when the IoU threshold is strict (e.g. AP@0.7, AP@0.8). This indicates our approach further bridges
the gap between simulation and real world and can help better evaluate and train autonomy. We have performed two analyses
on perception model performance on camera and LiDAR sensors separately with the same UniSim models generating both
synthetic data. Future investigation would include performing multi-sensor perception experiments to further understand the
domain gap of UniSim.
A4.6. Other Explorations
We have observed that certain commonly-used techniques in novel-view-synthesis did not offer significant improvements
with our architecture and data setting on our initial attempts. Specifically, we found that hierarchical or fine-grained sampling
did not significantly enhance realism but resulted in a considerable decrease in processing speed, possibly due to the majority
of the scene being distant from the self-driving vehicle. Additionally, optimizing exposure per frame did not improve realism
21


## Page 22

as the exposure does not change within a single log snippet for a single camera. We also attempted multi-camera training, but
found that several of the side cameras in PandaSet had mis-aligned calibration and slightly different exposures. Optimizing
the camera poses and exposure in this setting did not offer improvements, potentially due to limited data from a single 8
second log. Additionally, more training iterations and deeper architecture did not provide significant improvements, but
rather increased the complexity of the model.
A5. Limitations and Future Works
UniSim has several limitations. Our neural features grid cannot render lighting variations, as the modeled radiance bakes
the lighting into the representation. Future work involves explicitly modelling and manipulating scene lighting [6, 71, 102]
and weather. We also do not model animation (e.g., turn signals, traffic lights) or actor deformation (e.g. walking) and
hope to incorporate ideas from works [57,59,90,99] that tackle this. We also have artifacts when rendering areas that were
previously outside the field-of-view. Figure 15 shows qualitative visualizations of these phenomena. We hope future work in
this direction can further enhance sensor simulation realism.
22

