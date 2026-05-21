# 4DLidarOpen: An Open 4D FMCW Lidar Dataset for Motion-Aware Autonomous Driving

**Source**: arXiv:2605.18074

**Type**: Academic Paper

---

## Page 1

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
1
4DLidarOpen: An Open 4D FMCW Lidar Dataset for Motion-Aware
Autonomous Driving
Kane Qian1, Xin Zhao2, Yining Shi1, Rujun Yan1, Zhengqing Pan2, Kaojin Zhu2, Mengmeng Yang1, Kai Sun2,
Diange Yang1, Kun Jiang1,†
Abstract—We present 4DLidarOpen, a large-scale open multi-
modal dataset for autonomous driving, centered on 4D frequency-
modulated continuous-wave (FMCW) Lidar sensing. Unlike
conventional time-of-flight Lidar datasets that mainly provide
geometric measurements, 4DLidarOpen includes point-wise ra-
dial velocity measurements from a forward-facing 4D FMCW
Lidar, together with multiple Lidars of different types, includ-
ing rotating, solid-state, and blind-spot variants, surround-view
cameras, and 6-DOF ego-vehicle poses. The dataset was collected
in complex urban environments in Beijing and covers dense
pedestrian interactions, congested traffic, high-speed driving, and
unprotected maneuvers.
4DLidarOpen provides synchronized multi-sensor data and
3D bounding-box annotations with persistent track IDs across
five object categories. A hybrid annotation strategy is adopted,
where large-scale auto-labeled data support scalable training
and human experts refine annotations for the human-annotated
training and validation sets. Based on this dataset, we establish
benchmarks for 3D object detection, bird’s-eye view (BEV)
segmentation and flow prediction, and motion forecasting with
planning.
Extensive experiments show that direct velocity measurements
from 4D FMCW Lidar provide complementary motion cues
for dynamic-scene understanding. Compared with geometric-
only sensing, the velocity-aware representation improves motion-
related perception and downstream forecasting and planning,
especially in scenarios involving vulnerable road users and fast-
moving objects. These results indicate that 4D FMCW Lidar
is a promising sensing modality for motion-aware autonomous
driving. The dataset and evaluation toolkit are publicly released
to support research on 4D scene understanding, multi-Lidar
fusion, and velocity-aware perception and planning.
Index Terms—4D Scene Understanding, FMCW Lidar, Au-
tonomous Driving, End-to-End Learning, Spatiotemporal Per-
ception, Multi-Modal Sensing
I. INTRODUCTION
As autonomous driving systems progress toward Level 3
autonomy and beyond, end-to-end (E2E) learning has become
an increasingly important paradigm for integrating percep-
tion, prediction, and planning [1], [2]. Unlike traditional
modular pipelines that separate perception, prediction, and
planning into distinct components, E2E approaches learn a
direct mapping from raw sensor inputs to control commands.
This integration enables global optimization and fosters be-
haviorally consistent agents that can better handle complex
traffic scenarios. Recent advances in world models and unified
driving frameworks further suggest that autonomous systems
1Tsinghua University.
2Hesai Technology Co., Ltd.
†Corresponding author: Kun Jiang.
This work was supported in part by the National Natural Science Foundation
of China (52372414, 52394264, 52472449).
will depend not just on increasingly large policy networks,
but on expressive, motion-aware scene representations that
capture the dynamic nature of the driving environment [3], [4].
However, despite these advances, contemporary datasets often
fall short of providing the temporal resolution and motion
fidelity required for reliable 4D scene understanding.
4D FMCW 
Fig. 1.
4D FMCW sample showing raw point cloud data with point-wise
radial velocity information for motion-aware scene analysis.
At its core, autonomous driving requires an intelligent agent
to construct a temporally coherent representation of a dynamic
3D world. This task extends far beyond simple semantic
recognition, as the agent must simultaneously estimate 3D
geometry, track motion, maintain temporal continuity, reason
about interactions, and infer interaction patterns, all under
strict real-time constraints. The fundamental challenge in-
volves answering critical questions about the scene: identifying
the objects present, determining their locations, understanding
their motion patterns, predicting their interactions with the
ego vehicle, and anticipating how the scene will evolve in
the coming seconds. Consequently, autonomous driving is
inherently a 4D scene-understanding problem rather than a
static scene-parsing task [5].
Autonomous driving research is commonly organized
around two representative paradigms. Modular systems de-
compose the driving pipeline into separate perception, track-
ing, prediction, planning, and control components, which of-
fers interpretable intermediate representations and engineering
flexibility. In contrast, E2E approaches learn shared latent
representations, such as bird’s-eye view (BEV) grids, occu-
pancy volumes, or joint prediction-planning embeddings [6],
integrating these stages into a unified framework. Although
both paradigms have pushed the state of the art forward, their
scene representations still rely heavily on object categories,
geometric localization, and short-horizon temporal aggrega-
arXiv:2605.18074v1  [cs.RO]  18 May 2026


## Page 2

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
2
tion. This limits their ability to capture the full dynamics of
real-world traffic.
These limitations become particularly pronounced in com-
plex real-world scenarios. Frame-centric perception methods
often dilute temporal consistency and obscure continuous mo-
tion cues, while indirect motion inference through techniques
like frame-to-frame association or heuristic feature aggregation
degrades performance in long-range, high-speed, or densely
interactive situations. Furthermore, scene understanding ap-
proaches that focus solely on semantics and geometry strug-
gle to fully characterize dynamic traffic evolution, which is
essential for accurate motion forecasting, interaction reason-
ing, and effective planning. Compounding these challenges,
most existing public datasets are built around conventional
camera and time-of-flight Lidar setups that provide strong
geometric measurements but limited direct observability of
object motion. Consequently, many downstream tasks must
reconstruct dynamics indirectly, introducing ambiguity and
reducing robustness in safety-critical situations.
Recent progress in autonomous driving world models un-
derscores this limitation. DriveWorld demonstrates that au-
tonomous driving should be approached as a 4D scene under-
standing problem, highlighting the value of explicitly learning
spatiotemporal representations for perception, forecasting, oc-
cupancy prediction, and planning [7]. Similarly, World4Drive
shows that latent world modeling can support end-to-end
planning by capturing intention-aware physical scene evolution
[8]. These developments suggest that 4D understanding is not
merely an auxiliary capability but a key foundation for motion-
aware autonomous driving. This mirrors the human perception
process, where the brain seamlessly integrates motion cues,
such as the speed of surrounding objects, to anticipate and
react to changing situations. For an autonomous agent, directly
perceiving motion states rather than inferring them indirectly
is critical for building a robust and predictive understanding
of the dynamic world.
Motivated by these observations, we introduce 4DLi-
darOpen, a large-scale multi-modal dataset that bridges 4D
scene-understanding research and heterogeneous Lidar sens-
ing. The dataset provides synchronized surround-view cam-
eras, multi-Lidar streams, and 6-DOF ego-vehicle poses, form-
ing a comprehensive sensing suite for autonomous driving
research. 4DLidarOpen includes a diverse Lidar configuration:
1) A 4D FMCW Lidar that delivers (x,y,z,v) point clouds
through forward-facing scans, providing instantaneous
radial velocity for each point.
2) A 360° rotating OT Lidar with 300-meter range, serving
as the primary reference for high-quality annotations.
3) A solid-state AT Lidar that provides high-density
forward-facing scans, ideal for ADAS applications.
4) Two ATX blind-spot Lidars that monitor near-field re-
gions, capturing objects in areas often missed by other
sensors.
All sensors in 4DLidarOpen are hardware-synchronized and
jointly calibrated with high-precision extrinsic calibration [9],
ensuring coherent multi-modal data fusion. Beyond raw sensor
streams, 4DLidarOpen provides detailed per-sensor annota-
tions, including 3D bounding boxes with persistent tracklets
that maintain object identity across frames [10], [11].
Leveraging this rich dataset, we address a critical research
question: how does 4D FMCW Lidar sensing enhance au-
tonomous driving capabilities through richer 4D scene un-
derstanding? To answer this, we conduct systematic bench-
marks that compare the performance of forward-facing AT,
4D FMCW, and 360° OT Lidar configurations across a com-
prehensive suite of tasks. These benchmarks span 3D object
detection [12], [13], BEV segmentation and flow prediction
[14], [15], and motion forecasting coupled with path planning
[16], [17]. In doing so, 4DLidarOpen provides a concrete
testbed for studying how motion-aware sensing benefits object-
level perception, scene-level understanding, and downstream
driving tasks.
As illustrated in Figure 1, the 4D FMCW Lidar captures
instantaneous radial velocity information for each point, pro-
viding significant advantages for motion analysis and dynamic
object detection. This velocity-aware point cloud representa-
tion enables more accurate tracking of moving objects such
as pedestrians, cyclists, and vehicles, as the radial velocity
can be directly measured without requiring frame-to-frame
differentiation.
4DLidarOpen makes three principal contributions to the
autonomous driving research community:
1) We release 4DLidarOpen, an open multi-modal au-
tonomous driving dataset centered on 4D FMCW Li-
dar sensing. The dataset integrates a forward-facing
4D FMCW Lidar, rotating OT Lidar, solid-state AT
Lidar, ATX blind-spot Lidars, synchronized surround-
view cameras, and 6-DOF ego-vehicle poses.
2) We provide unified benchmarks for 3D object detection,
BEV segmentation and flow prediction, and motion fore-
casting with planning, enabling evaluation from object-
level perception to downstream driving tasks.
3) We empirically quantify the role of point-wise radial
velocity measurements and show that 4D FMCW Lidar
provides complementary motion cues for dynamic-scene
understanding and downstream forecasting and planning.
4DLidarOpen
and
its
open-source
evaluation
toolkit
are publicly available at https://github.com/haopen-dataset/
haopen, providing the research community with a reproducible
foundation for advancing 4D scene-understanding and motion-
aware driving technologies. By making this resource available,
we aim to support reproducible research on motion-aware
perception, prediction, and planning in dynamic traffic envi-
ronments.
II. RELATED WORK
A. Sensor Datasets
Over the past decade, the autonomous driving research
community has seen the release of numerous sensor-rich
datasets designed to train and benchmark perception, predic-
tion, and planning modules. Pioneering datasets like KITTI
[11] and Cityscapes [18] laid the foundation for calibrated
multi-modal data collection, yet their relatively limited 15
hours of driving time and lack of behavioral labels make them


## Page 3

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
3
unsuitable for end-to-end learning approaches. Building on this
foundation, nuScenes [10] introduced 1,000 twenty-second
clips with 1.4 million 3D object boxes, while ApolloScape
[19] added 140,000 high-resolution frames with pixel-level
semantics and lane masks. Waymo Open [20] further expanded
the scope with 1,950 scenes recorded across urban, suburban,
and highway domains using five Lidars and five cameras. More
recently, datasets such as CODA [21] and PandaSet [22] have
focused on capturing rare events. However, few public datasets
provide both surround-view geometric sensing and point-wise
instantaneous velocity measurements, which limits systematic
studies of motion-aware 4D scene understanding.
Three key gaps persist in the current landscape of au-
tonomous driving datasets. First, most existing datasets rely on
homogeneous sensor setups—typically frontal 120° cameras
and a single rooftop Lidar—while modern production vehicles
increasingly employ surround-view camera rigs, side and rear
radars, and multiple solid-state Lidars. Second, the Lidar speci-
fications in existing datasets often lag behind the capabilities of
contemporary assisted-driving fleets, limiting their relevance
for next-generation systems. Third, and most critically, the
perceptual value of 4D FMCW Lidar—with its ability to
provide instantaneous radial velocity measurements—remains
largely unexplored in public benchmarks, despite its potential
value for dynamic scene understanding.
While simulators such as CARLA [23] help address data
scarcity, the inherent sim-to-real gap limits their utility for
safety-critical deployment. This motivates large-scale, geo-
graphically diverse, and action-labeled real-world datasets that
support the joint study of perception and control, which is one
of the goals of 4DLidarOpen.
B. Recent Advances in End-to-End Driving
End-to-end (E2E) driving represents a paradigm shift in
autonomous vehicle development, learning a direct mapping
from raw sensor inputs to trajectories or control commands
without relying on hand-engineered intermediates like 3D
bounding boxes, motion priors [24], or HD maps [25]. Bojarski
et al. [26] popularized this approach by training a convolu-
tional neural network (CNN) to regress steering angles from
monocular video. Despite its simplicity, their system achieved
robust highway lane keeping, establishing imitation learning
(IL) as a foundational approach for E2E driving [27], [28].
Subsequent research has expanded this paradigm to include
reinforcement learning (RL) [29], [30], inverse reinforcement
learning, and behavior cloning with data augmentation tech-
niques.
Progress in E2E driving has unfolded along three primary
axes: input modalities, policy architectures, and training ob-
jectives. Inputs have evolved from monocular RGB [26] to
encompass surround-view camera rigs, Lidar point clouds [31],
and heterogeneous sensor fusion [32], [33]. TransFuser [33]
leverages transformers to fuse Lidar and camera features,
while BEVFusion [31] unifies multi-sensor cues in a bird’s-eye
view (BEV) grid. Recent vectorized approaches like VAD [34]
efficiently encode scene information for planning tasks.
Architectures have matured from simple CNNs to sophis-
ticated spatio-temporal networks. Recurrent neural networks
and temporal convolutions encode historical information [35],
while attention mechanisms dynamically weight scene entities
based on their relevance. Multi-task frameworks jointly regress
trajectories, segmentation, and occupancy, using auxiliary su-
pervision to improve generalization [36], [37]. UniAD [38]
represents a significant advance by unifying perception, pre-
diction, and planning in a single framework, while recent
generative world models [39] and diffusion models [40], [41]
synthesize diverse scenarios to enhance planning capabilities.
Training objectives have diversified beyond pure imitation
learning. Reinforcement learning with carefully designed re-
ward functions addresses the distribution shift problem inher-
ent in imitation learning [29]. Adversarial training improves
robustness to distribution shifts [42], and safety-constrained
optimization incorporates collision avoidance as differentiable
costs [43], [44]. Direct Preference Optimization (DPO) [45]
has also been adapted to align driving policies with human
preferences, improving the naturalness of generated behaviors.
A particularly significant recent development is the inte-
gration of Large Language Models (LLMs) [46], [47] and
Vision-Language Models (VLMs) [48] to inject commonsense
reasoning and interpretability into driving systems. Works like
GPT-Driver [49], DriveMLM [50], and LmDrive [51] use
LLMs as planners or reasoning engines. Subsequent studies
have enhanced this paradigm with agent-based reasoning [52],
[53], knowledge grounding [54], [55], and visual instruction-
tuning [56], [57]. The emergence of Vision-Language-Action
(VLA) models marks a pivotal shift towards true end-to-
end systems that process raw pixels and output actionable
control commands. DriveVLM [58], Senna [59], OTTER [60],
and AutoVLA [61] exemplify this VLA paradigm, unifying
perception, reasoning, and control in single autoregressive
sequence models [62], [63]. These models are typically trained
on large-scale, instruction-based datasets [64], [65] to follow
natural language commands and explain their decisions.
Despite these advances, current E2E systems still face
significant challenges in long-horizon reasoning, safety guar-
antees, and interpretability. Recent works have begun to ad-
dress these issues by integrating differentiable motion plan-
ning layers [66], [67] and constrained policy optimization
techniques. Approaches like Model Predictive Control (MPC)
integration [68], [69] and causal reasoning frameworks are also
being explored. However, the performance of VLA models
scales directly with the volume and diversity of real-world
data [70], [71], highlighting the critical need for large-scale,
multi-modal corpora like 4DLidarOpen.
Benchmarking in E2E driving has evolved alongside these
advances, with simulators like CARLA [23] and large-scale
real-world datasets such as nuScenes [72], Waymo Open [73],
and Argoverse [74], [75] providing standardized evaluation
platforms. Nevertheless, real-world deployment challenges re-
main significant due to domain gaps and the difficulty of
certifying data-driven systems for safety-critical applications.
4DLidarOpen is specifically designed to support these
emerging paradigms by providing precisely synchronized
multi-modal sensor streams. The dataset facilitates research on
unified perception-planning-control networks, advanced sensor
fusion strategies, and predictive models that leverage motion


## Page 4

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
4
information. By capturing real-world driving scenarios with
rich annotations, 4DLidarOpen aims to bridge the gap between
simulation-based research and practical deployment, acceler-
ating progress toward more robust, safe, and interpretable E2E
driving systems.
C. 4D FMCW Lidar
Frequency-Modulated Continuous-Wave (FMCW) Lidar
technology has recently advanced to deliver 4D point clouds
(x, y, z, v) at video frame rates, where v represents the in-
stantaneous radial velocity of each point [76]. This velocity
channel provides a direct measurement of radial motion,
distinguishing 4D FMCW Lidar from conventional time-of-
flight Lidars that infer motion mainly through temporal asso-
ciation. However, the absence of large-scale, publicly available
4D datasets has limited high-level perception research using
FMCW Lidar.
Existing FMCW Lidar research has predominantly focused
on low-level tasks such as odometry and localization, leaving
high-level perception relatively underexplored. HeLiPR [77]
represents the first dedicated 4D FMCW Lidar dataset, de-
signed specifically for inter-Lidar place recognition by filter-
ing dynamic objects and performing place recognition using
static points. The Doppler iterative closest point (DICP) al-
gorithm [78] addresses the specific challenge of registering
4D FMCW Lidar point clouds by incorporating velocity
consistency into the optimization process, improving accuracy
in dynamic environments [79]. Other works have explored
odometry tasks, leveraging FMCW Lidar’s ability to separate
dynamic objects from static scenes to achieve more robust
performance [80]–[82]. Recent advancements also include
tightly coupled sensor fusion for odometry [83] and efficient
continuous-time trajectory estimation methods [84].
This focus on low-level tasks leaves an important gap in
high-level perception and driving benchmarks: there are few
large-scale 4D FMCW datasets with high-level annotations
for perception and driving tasks. Initial investigations into
perception applications, such as the work by Gu et al. [85],
demonstrate the potential of 4D FMCW Lidar for direct object
tracking, benefiting from its instantaneous velocity measure-
ments. Recent studies have begun to explore more complex
perception tasks like 4D object detection [86], highlighting
the technology’s advantages in motion estimation and velocity
measurement for autonomous driving applications.
4DLidarOpen addresses this gap by providing the first large-
scale corpus that couples 4D FMCW Lidar data with high-
level perception and E2E driving annotations. By making
this resource available to the research community, we aim
to accelerate the development of motion-aware perception
systems that can fully leverage the unique capabilities of 4D
FMCW Lidar technology.
III. METHODOLOGY
A. Overview
4DLidarOpen is designed as a large-scale multi-modal
benchmark for 4D scene understanding, 3D object detection,
and E2E driving in complex urban environments. Compared
with existing autonomous driving datasets, it emphasizes
heterogeneous Lidar sensing and direct radial velocity mea-
surements from 4D FMCW Lidar, providing a testbed for
evaluating motion-aware perception and planning systems.
B. Sensor Configuration
OT128
AT128/FMCW
Camera
Camera
Camera
Camera
ATX
ATX
Fig. 2.
4DLidarOpen sensor configuration: five Lidars and five surround-
view cameras mounted on the ego vehicle, providing comprehensive coverage
around the vehicle.
4DLidarOpen employs a multi-modal sensor suite compris-
ing five Lidars and five surround-view cameras, as illustrated
in Figure 2. The system captures 10-Hz Lidar sweeps synchro-
nized with 20-Hz imagery from five cameras: four wide-angle
cameras covering the sides and rear, and one telephoto front
unit, together providing a panoramic field of view around the
ego vehicle. For each sensor, 4DLidarOpen provides detailed
camera intrinsics, extrinsics, and 6-DOF ego-vehicle poses in
a global coordinate frame.
The sensor suite includes five distinct Lidars: a 4D FMCW
Lidar, a 360° rotating OT Lidar, a solid-state AT Lidar, and
two ATX blind-spot Lidars, all operating at 10 Hz. Global-
shutter cameras are hardware-triggered to expose precisely
while the Lidar sweeps across their field of view, ensuring sub-
millisecond temporal alignment between sensor modalities.
Synchronization.
4DLidarOpen
achieves
camera–Lidar
temporal alignment within [−1.39, 1.39] milliseconds, three
times tighter than the [−6, 7] millisecond alignment of Waymo
Open [87]. This precise synchronization enables seamless
pixel-point fusion without motion blur, critical for accurate
multi-modal perception.
C. Data Collection and Scenes
4DLidarOpen was recorded in Beijing’s Yizhuang and
Shougang Industrial Park districts, areas that encapsulate
the complexity of contemporary Chinese urban traffic—from
multi-lane arterials and highway interchanges to dense in-
tersections and urban thoroughfares. Figure 3 depicts the
comprehensive processing pipeline, from initial data collection
through synchronization, annotation, and validation.
The data collection campaign systematically sampled di-
verse driving scenarios to ensure comprehensive coverage:
• Road types: multi-lane arterials, highway interchanges,
high-speed segments, and urban streets with varying
speed limits and traffic patterns.


## Page 5

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
5
External expert
Human check
Car
Pedestrian and Cyclist
Traffic Con.
• Point filter
• Class check
• Final dataset
• Raw sensor input
Van
Fig. 3. 4DLidarOpen data processing pipeline, including raw data collection, sensor synchronization, automatic labeling, human verification, and final dataset
generation.
• Illumination conditions: sunny, cloudy, dusk, dawn, and
night scenarios to stress-test system robustness across
different lighting environments.
The dataset is further enriched by frequent critical events
that challenge autonomous driving systems:
• Pedestrian interactions: dense crowds, jaywalking, and
pedestrians crossing at non-designated locations.
• High-speed cruising: stable highway navigation at ele-
vated speeds, testing long-range perception and predic-
tion.
• Unprotected maneuvers: left turns and U-turns amid
flowing traffic, requiring precise interaction prediction.
• Congested traffic: stop-and-go queues that stress close-
range perception and low-speed control.
This diversity provides a challenging evaluation setting
for perception, prediction, and planning under realistic urban
traffic conditions.
D. Annotations and Sample Format
4DLidarOpen provides rich, high-frequency 3D annotations
to support a wide range of research tasks. Figure 4 shows
a representative sample with four camera views, Lidar point
cloud, and human-annotated 3D boxes with persistent track
IDs.
Every object within 4DLidarOpen’s 5-class taxonomy is
annotated with a precise 3D cuboid at 10 Hz, ensuring
temporal consistency through unique track identifiers that
persist across frames [10]. Our annotation policy is designed to
maximize both relevance and precision: we annotate all objects
within 150 meters of the ego vehicle, with particular focus
on actionable obstacles that could impact driving decisions.
Objects in the ego lane are tagged even with sparse Lidar ev-
idence—sometimes as few as 5 points—ensuring that critical
obstacles are not missed [11], [14]. This curated approach,
executed through a rigorous annotate-then-verify workflow on
our internal platform, improves annotation reliability and en-
sures that the retained objects are relevant to driving decisions.
Privacy. To ensure compliance with privacy regulations, all
faces and license plates in the dataset are automatically blurred
during processing.
Splits. 4DLidarOpen provides 225 human-annotated sce-
narios, including 167 training scenarios and 58 validation
scenarios, together with three auto-labeled training tiers con-
taining 500, 1,000, and 2,000 sequences. This tiered structure
enables scalable self-supervised research across different com-
putational budgets.
To support large-scale self-supervised and semi-supervised
learning, we also release a substantial collection of auto-
labeled sequences across three distinct tiers: a Small set (500
scenarios), a Medium set (1,000 scenarios), and a Large set
(2,000 scenarios). This flexible structure allows researchers to
conduct experiments under varying computational constraints
and data scales, facilitating everything from quick prototyping
to large-scale pretraining.
E. Data Processing and Labelling Policy
4DLidarOpen supports a wide range of research tasks
through a rigorously validated processing pipeline, enabling
comprehensive evaluation of autonomous driving systems.
Processing. Raw PCAP Lidar streams are decoded to com-
pact PLY format for efficient storage and processing. Ego-
vehicle poses are fused from wheel odometry and IMU data
to provide accurate positioning information. All sensors are


## Page 6

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
6
ATX0
ATX1
AT128
P128
4D FMCW
4DLidarOpen
“A car drives down a city street lined with buildings and trees, passing by parked vehicles and urban infrastructure.”
Fig. 4.
4DLidarOpen sample showing 4D FMCW Lidar data with velocity information: (a) raw point cloud with radial velocity coloring, (b) semantic
segmentation results, (c) motion flow visualization with vector arrows, (d) comparison with conventional 3D Lidar without velocity cues. The 4D FMCW data
provides point-wise radial velocity cues that support motion analysis and dynamic-object detection.
synchronized using gPTP (general Precision Time Protocol) to
achieve sub-millisecond accuracy. Data are rectified to a rear-
axle-centered coordinate frame using pre-calibrated extrinsics,
ensuring consistent spatial referencing across all sensor modal-
ities. Sequences with anomalous poses or sensor artifacts are
quarantined before annotation to maintain data quality.
Annotation. Our annotation pipeline begins with an auto-
labeling system that generates preliminary 3D bounding boxes.
These initial annotations are then iteratively refined by human
experts through a two-stage review process. Objects within
150 meters of the ego vehicle that reflect more than 5 Lidar
returns are systematically annotated, while ego-lane obstacles
are retained even with sparser returns to ensure critical objects
are captured. The two-stage review pipeline ensures every
cuboid and track meets strict pixel-point fidelity standards,
resulting in high-quality annotations for both training and
evaluation.
Figure 4 illustrates the advantages of 4D FMCW Lidar data
in 4DLidarOpen. The instantaneous radial velocity information
enables precise motion analysis, allowing for earlier detection
and tracking of dynamic objects compared to conventional 3D
Lidar systems.
F. Data Statistics
Table I presents a comprehensive statistical overview of
4DLidarOpen’s subsets, highlighting the balance between
high-quality human annotations and large-scale auto-labeled
data.
The human-annotated splits (225 scenes) yield an average
of 69.3 and 62.8 instances per Lidar frame for training and
validation respectively, with 730 and 592 distinct tracks. This
rich temporal information enables robust modeling of object
dynamics and interactions over time.
The auto-labeled tier (2,000 scenes, 295.7 km, 11 hours)
delivers 1.97 million camera frames and 394,000 Lidar sweeps
with 22.9 million bounding boxes, providing a massive dataset
for scalable self-supervised learning and pretraining.
Category statistics in Figure 5 show the distribution of an-
notations across object categories, comparing auto-labeled and
human-labeled data. The long-tail distribution dominated by
cars is evident, with auto-labeled data providing significantly
more instances for rare categories like cyclists and traffic
cones, supporting research on rare-event detection.
Spatial analysis in Figure 6 shows that objects are concen-
trated within 50 meters of the ego vehicle, which aligns with
typical Lidar effective range and highlights the importance of
near-field perception for safe driving. The density distribution
per Lidar frame reflects realistic urban traffic conditions.
Speed profiles in Figure 7 reveal distinct category-specific
kinematic patterns: cars and vans exhibit higher speeds, while
pedestrians and cyclists show lower velocity distributions.
These statistics provide valuable insights for designing motion-
aware perception models and velocity prediction systems.
Together, 4DLidarOpen’s human-curated and auto-labeled
tiers constitute a versatile and comprehensive resource for
advancing research in 4D perception, motion prediction, and
E2E driving systems. The dataset’s scale, diversity, and rich
annotations make it an ideal platform for developing and
evaluating autonomous driving technologies.
IV. EXPERIMENTS
We evaluate 4DLidarOpen on three downstream tasks: 3D
object detection, BEV segmentation and flow prediction, and


## Page 7

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
7
TABLE I
STATISTICAL OVERVIEW OF THE THREE SUBSETS IN 4DLIDAROPEN.
Statistic
Training (Human-Annot.)
Validation (Human-Annot.)
Training (Auto-Labeled)
Number of Scenarios
167
58
2,000
Total Driving Distance (km)
11.60
3.49
295.70
Total Driving Duration (hours)
0.58
0.19
10.89
Total Camera Frames
105,220
35,000
1,974,480
Total Lidar Frames
21,044
7,000
394,896
Total Annotation Instances
1,457,552
439,675
22,952,926
Total Tracks
730
592
1,741
Avg. Annos. per Frame
69.26
62.81
58.12
（a）
（b）
Fig. 5. 4DLidarOpen class and richness statistics. (a) Instance counts across five categories (Car, Van, Cyclist, Pedestrian, Traffic Cone) comparing auto-labeled
(blue) and human-labeled (orange) annotations on log scale. (b) Distribution of unique class counts per Lidar frame, showing rich scene diversity.
motion forecasting with planning.
We benchmark each task below.
A. 3D Object Detection
1) Metrics: We adopt KITTI and nuScenes metrics for
compatibility.
KITTI AP: IoU=0.5 for vehicles/vans; IoU=0.25 for vul-
nerable road users.
APKITTI = 1
41
X
r∈{0,0.025,...,1}
p(r)
(1)
where p(r) is the precision interpolated at each recall level r
following the KITTI 40-point sampling scheme.
nuScenes mAP/NDS: distance-based mAP and NDS (ag-
gregating translation, scale, orientation, velocity, and attribute
errors). mAP is computed over the distance-based matching
strategy:
mAP = 1
C
C
X
c=1
1
D
D
X
d=1
APc,d
(2)
NDS aggregates mAP with five true-positive error rates:
NDS = 1
10
h
5 × mAP +
X
k∈{trans,scale,orient,vel,attr}
(1 −ek)
i
(3)
where ek denotes the average error for translation, scale,
orientation, velocity, and attribute classification, each clipped
to [0,1].
Five categories are evaluated: Car, Pedestrian, Cyclist, Van,
and Traffic Cone. Vans are split by wheel-base and height;
cones require ≥50% above-ground visibility. All metrics are
implemented in our open-source evaluation toolkit.
2) Experimental Results: Table II reports the 3D object
detection performance of different Lidar configurations using
the SparseConv encoder and Sparse4D head. Table III further
evaluates the contribution of the radial velocity channel for
4D FMCW Lidar-based detection.
We benchmark CenterPoint [13] and PointPillars [12] back-
bones with a Sparse4D head, matching SparseDrive and Dif-
fusionDrive architectures.
All Lidars use consistent voxelization parameters follow-
ing KITTI/nuScenes conventions [12], [13], with 4D FMCW
providing additional instantaneous radial velocity vr [77].
a) Analysis:: Table II presents the 3D object detection
results across three Lidar sensors, revealing distinct perfor-
mance characteristics tied to sensor architecture.
Overall Performance. AT128 achieves the highest overall
performance with mAP of 69.62% and NDS of 76.32%,
establishing the strongest baseline for detection tasks. OT128
follows closely in NDS (74.51) but lags in mAP (64.89), while
4D FMCW exhibits the lowest raw detection metrics (mAP:
63.62, NDS: 72.05) despite its velocity-sensing capabilities.
Detailed Category Analysis. AT128 demonstrates superior
performance in detecting small and geometrically complex ob-
jects, particularly excelling in Traffic Cone (66.48%) and Cy-
clist (86.87%) detection, which suggests its scanning pattern


## Page 8

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
8
（a）
（b）
Fig. 6. 4DLidarOpen spatial and density statistics. (a) Object distance distribution showing peak concentration within 50 meters. (b) Distribution of 3D cuboid
counts per Lidar frame, reflecting real-world traffic density variations.
（a）
（b）
Fig. 7. 4DLidarOpen speed statistics. (a) Category-wise box plots showing speed distributions for Car, Van, Cyclist, Pedestrian, and Traffic Cone. (b) Overall
speed histogram across all object instances.
provides denser point coverage for low-profile objects. OT128
achieves the highest Car detection accuracy (91.21%), likely
benefiting from its optimized beam distribution for mid-range
vehicle detection. 4D FMCW shows competitive performance
on Vans (57.08%) and Pedestrians (76.81%), but Traffic Cone
detection remains more challenging for FMCW 4D (35.81%),
indicating that the velocity channel’s spatial resolution trade-
off particularly affects small static object detection.
b) Velocity Channel Ablation:: Table III shows the con-
tribution of the radial velocity channel to detection perfor-
mance. In the absence of vr (xyzi only), the detection per-
formance decreases across all categories, with mAP and NDS
dropping to 21.58% and 41.86%, respectively. Incorporating
velocity information (xyziv) improves mAP from 21.58% to
28.75% and NDS from 41.86% to 51.49%. The improvement
is particularly evident for pedestrians, where AP increases
from 17.59% to 48.28%, suggesting that motion cues are
useful for detecting dynamic vulnerable road users. These
results confirm that while 4D FMCW sacrifices some spatial
resolution compared to scanning Lidars, the instantaneous
velocity channel provides complementary information that
improves detection performance in dynamic scenes.
B. Bird’s Eye View Segmentation and Flow
We benchmark BEV segmentation and flow on 4DLi-
darOpen against MotionNet [88], BE-STI [89], PriorMotion


## Page 9

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
9
TABLE II
3D OBJECT DETECTION PERFORMANCE COMPARISON ACROSS DIFFERENT LIDAR SENSORS USING SPARSECONV ENCODER AND SPARSE4D HEAD. T.C.
REFERS TO TRAFFIC CONE.
Sensor
Encoder
Decoder
Car
Ped.
Cyc.
V an
T.C.
mAP
NDS
AT128
SparseConv
Sparse4D head
90.45
76.21
86.87
51.49
66.48
69.62
76.32
FMCW 4D
SparseConv
Sparse4D head
87.87
76.81
71.63
57.08
35.81
63.62
72.05
OT128
SparseConv
Sparse4D head
91.21
70.51
81.90
54.79
53.80
64.89
74.51
TABLE III
ABLATION STUDY ON THE IMPACT OF RADIAL VELOCITY (vr) CHANNEL FOR 4D FMCW LIDAR-BASED 3D DETECTION. T.C. REFERS TO TRAFFIC
CONE.
Sensor
Encoder
Decoder
Car
Ped.
Cyc.
V an
T.C.
mAP
NDS
FMCW 4D xyzi
SparseConv
Sparse4D head
22.57
17.59
40.98
19.59
-
21.58
41.86
FMCW 4D xyziv
SparseConv
Sparse4D head
34.03
48.28
60.45
31.05
-
28.75
51.49
Frame 1
Frame 8
(a) 
(b) 
(c) 
(d) 
(e) 
(f) 
Frame 1
Frame 2
(a) 
(b) 
(c) 
(d) 
(e) 
(f) 
The traffic cone rolled into 
the road.​
A pedestrian is crossing the 
road.
Fig. 8. 4DLidarOpen campus ablation experiment. Top row: rolling cone scenario; bottom row: darting pedestrian scenario. (a)-(c) 4D FMCW Lidar results
showing raw BEV point cloud, semantic grid, and radial velocity heatmap. (d)-(f) Baseline results without velocity information. 4D FMCW detects vulnerable
road users (VRUs) significantly earlier (cone: frame 1 vs 8; pedestrian: frame 1 vs 2), illustrating the value of instantaneous velocity cues.
[90], and LEGO-Motion [24]. Given Lidar sequence {Pt}T
t=1,
we learn f that forecasts BEV motion Mt, classifies cells Ct,
and estimates static probability St.
f({Pt}T
t=1) →(Mt, Ct, St)
(4)
Input Lidar clouds Pt = {P i
t }Nt
i=1 are voxelized to Vt ∈
{0, 1}H×W ×C in ego coordinates.
The model outputs BEV motion field Mt, class logits Ct,
and static probability St per cell:
Mt ∈RH×W ×2, Ct ∈RH×W ×Nc, St ∈RH×W .
(5)
a) Campus Ablation Experiment Analysis.: Figure 8 il-
lustrates the potential benefit of 4D FMCW Lidar for early
dynamic-object detection. In the rolling cone scenario (top
row), the 4D FMCW Lidar detects the falling cone in frame
1, while the baseline without velocity information requires
8 frames to achieve the same detection. Similarly, in the
darting pedestrian scenario (bottom row), the 4D FMCW Lidar
identifies the pedestrian in frame 1, compared to frame 2
for the baseline. This early detection capability is critical for
autonomous driving systems to react in time to sudden events.
The radial velocity heatmap (c) clearly shows the motion of


## Page 10

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
10
（a）
（b）
（c）
（d）
（a）
（b）
（c）
（d）
Cyclist crossing scenario
Frame2
Frame2
Frame2
Frame2
Pedestrian crossing scenario
Frame2
Frame6
Frame4
Frame6
Fig. 9. 4DLidarOpen Tianjin crossing test. Top row: pedestrian crossing scenario; bottom row: e-bike crossing scenario. (a) 4D FMCW Lidar + our model;
(b) 3D Lidar + our model; (c) 4D FMCW Lidar + baseline model; (d) 3D Lidar + baseline model. 4D input significantly advances detection (e-bike: frame
2 vs 6) and stabilizes earlier (frame 4 vs 29), showing the benefit of direct velocity measurements in crossing scenarios.
the cone and pedestrian, providing qualitative evidence of the
velocity channel’s contribution to early detection.
b) Tianjin Crossing Test Analysis.:
Figure 9 further
demonstrates the performance of 4D FMCW Lidar in chal-
lenging crossing scenarios. In both pedestrian and e-bike
crossing scenarios, the 4D FMCW Lidar configurations (a
and c) consistently outperform their 3D Lidar counterparts (b
and d). Specifically, in the e-bike crossing scenario, the 4D
FMCW Lidar + our model (a) detects the e-bike in frame
2, while the 3D Lidar + our model (b) requires frame 6.
Moreover, the 4D configuration stabilizes its detection by
frame 4, compared to frame 29 for the 3D configuration. This
improvement in detection speed and stability suggests that
velocity information can support timely decision-making in
dynamic crossing scenarios.
1) Metrics: Following established evaluation protocols, we
group cells by speed: static (≤0.2 m/s), slow (0.2–5 m/s), and
fast (>5 m/s), and report mean and median L2 displacement
errors at 1 second. For each speed group, we calculate the
average distance between predicted and ground truth displace-
ments. The mean prediction error for a group G is:
Mean ErrorG =
1
|G|
X
i∈G
∥ˆdi −di∥2
(6)
where ˆdi is the predicted displacement and di is the ground
truth displacement for cell i.
The median prediction error for a group G is:
Median ErrorG = median
n
∥ˆdi −di∥2 | i ∈G
o
(7)
To better understand motion prediction performance, we
decompose the displacement error along radial and lateral
directions relative to the ego vehicle. The radial direction
corresponds to motion toward or away from the ego vehicle,
while the lateral direction represents side-to-side motion.
We classify cells into static, slow, and fast groups based on
their radial and lateral speeds, respectively, and compute the
mean and median errors in each direction. The mean radial
prediction error for group Gr is:
Mean Radial ErrorGr =
1
|Gr|
X
i∈Gr
(ˆdi −di) · ur

(8)
where ur is the unit vector pointing from the ego vehicle to
the cell center.
Similarly, the mean lateral prediction error for group Gl is:
Mean Lateral ErrorGl =
1
|Gl|
X
i∈Gl
(ˆdi −di) · ul

(9)


## Page 11

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
11
where ul is the unit vector orthogonal to ur in the horizontal
plane.
The corresponding median errors are computed analogously
for both radial and lateral directions.
In addition to motion prediction, we evaluate cell classi-
fication performance using overall accuracy (OA) and mean
category accuracy (MCA). OA measures the average accuracy
across all non-empty cells, while MCA calculates the average
accuracy per category, providing insight into how well models
handle different object types.
2) Experimental Analysis: Table IV summarizes the BEV
segmentation and flow estimation results across three ar-
chitectures (MotionNet, STI, PriorMotion) and three sensor
configurations (OT128, AT128, FMCW 4D), with and without
velocity input fusion.
Overall Performance. PriorMotion combined with FMCW
4D and velocity fusion achieves the best overall performance
among the evaluated configurations, with the lowest motion
prediction errors across all speed regimes (static: 0.0011, slow:
0.6218, fast: 1.0033) and the highest classification accuracy
(MCA: 0.8541, OA: 0.9864). The consistent superiority of
velocity-enhanced variants (denoted by †) across all model-
sensor combinations indicates the importance of explicit mo-
tion cues for flow estimation. Notably, the incorporation of
velocity information reduces static cell errors by an order of
magnitude (from ∼0.01 to ∼0.001), indicating precise ego-
motion compensation and static background stabilization.
Architecture Comparison. PriorMotion consistently out-
performs MotionNet and STI across all sensor configura-
tions, with the performance gap widening for fast-moving
objects (PriorMotion+FMCW 4D 0+v achieves 1.0033 vs.
MotionNet’s 1.0844 and STI’s 1.0391). This suggests that
PriorMotion’s motion-aware architectural priors better capture
dynamic scene evolution compared to convolutional (Motion-
Net) or spatial-temporal interaction (STI) approaches. STI
demonstrates competitive lateral motion estimation (best lat-
eral slow error: 0.3916 with STI+FMCW 4D 0+v), likely
benefiting from its explicit spatial-temporal feature interaction
mechanism.
Sensor Analysis. FMCW 4D exhibits distinct performance
characteristics depending on velocity fusion: without velocity
input, it generally underperforms compared to scanning Li-
dars (OT128/AT128), particularly in lateral motion estimation
(FMCW 4D 0 lateral slow error: 0.4632 vs. AT128 0: 0.4473
for MotionNet). However, with velocity fusion, FMCW 4D
configurations achieve the best radial motion estimation (best
radial slow: 0.4478, best radial fast: 0.6385) and competi-
tive lateral performance, leveraging the instantaneous Doppler
measurements for direct motion decomposition. AT128 shows
strong raw performance in slow and fast motion regimes
without velocity fusion (best non-v slow: 0.6385, best non-
v fast: 0.9959), attributed to its dense point cloud providing
rich geometric cues for optical flow-style motion estimation.
Directional Motion Decomposition. The decomposition
of motion errors into radial and lateral components reveals
that velocity fusion predominantly improves radial motion
estimation (reducing radial static errors by 15-20×), while
lateral motion benefits are more modest but consistent. This
asymmetry reflects the physical nature of FMCW Doppler
measurements, which directly observe radial velocity but
require geometric inference for lateral components. Prior-
Motion+FMCW 4D 0+v achieves the best lateral fast error
(0.7093), suggesting that advanced architectures can effec-
tively disambiguate lateral motion from radial Doppler cues
and spatial context.
Classification
Performance.
While
all
configurations
achieve high overall accuracy (OA > 0.98), mean category
accuracy (MCA) reveals significant disparities in handling rare
or challenging semantic classes. PriorMotion+FMCW 4D 0+v
achieves MCA of 0.8541, substantially outperforming the
next best configuration (PriorMotion+FMCW 4D 0: 0.8219)
and baseline scanning Lidar setups (AT128 0: 0.7572). This
13% relative improvement in per-class accuracy, coupled with
superior motion estimation, indicates that velocity-informed
models achieve more robust and semantically consistent scene
understanding, critical for downstream prediction and planning
tasks.
In summary, the experimental results indicate that (1) ex-
plicit velocity fusion is important for exploiting the motion-
sensing capability of FMCW 4D Lidar, (2) PriorMotion’s
architectural design effectively uses motion priors across dif-
ferent sensor types, and (3) combining motion-aware architec-
tures with 4D FMCW sensing improves both motion estima-
tion and semantic classification in dynamic driving scenes.
C. Motion Forecasting and Planning
End-to-end trajectory prediction and planning are core com-
ponents for driving models. We adopt two state-of-the-art
multi-modal predictors and planners as baseline E2E systems:
(1) SparseDrive: a sparse query transformer that decodes
agent-centric trajectories with cross-attention between agent
and ego queries and feature maps. (2) DiffusionDrive: a
diffusion-based policy that progressively denoises a set of
waypoint latents conditioned on the driving command and
surrounding agents. To fit for Lidar inputs, both methods are
slightly adjusted to perform deformable cross attention on
BEV feature maps.
1) Metrics: The task is formulated as, given the current 1-
second sensor context, each model forecasts the ego-vehicle
and moving obstacles for the next 3 s (30 frames @ 10 Hz).
Evaluation is restricted to dynamic objects (speed > 1.0 m/s
within the prediction horizon).
minADEk: minimum Average Displacement Error over k
predicted trajectories
minADEk = 1
T
T
X
t=1
p∗
t −ˆp(best)
t

2 ,
T = 30
(10)
minFDEk: minimum Final Displacement Error at the last
frame (t = 30)
minFDEk =
p∗
30 −ˆp(best)
30

2
(11)
We report results for k = 6 (full multi-modal output) and
k = 1 (best-of-one trajectory) to quantify both diversity and
single-hypothesis accuracy.


## Page 12

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
12
TABLE IV
COMPARISON OF BEV SEGMENTATION AND FLOW PERFORMANCE ACROSS DIFFERENT MODELS AND SENSORS (THE SMALLER THE VALUE, THE LOWER
THE SPEED ERROR. ↓: THE LOWER THE BETTER FOR ERROR METRICS; ↑: THE HIGHER THE BETTER FOR CLASSIFICATION METRICS. STATIC: SPEED ≤
0.2 M/S, SLOW: 0.2 M/S < SPEED ≤5 M/S, FAST: SPEED > 5 M/S. OA: OVERALL ACCURACY, MCA: MEAN CATEGORY ACCURACY. † DENOTES THE
USE OF THE RADIAL VELOCITY CHANNEL).
Experiment
Sensor
Overall Speed ↓
Radial Speed ↓
Lateral Speed ↓
Grid Classification ↑
Classification Interval
Classification Interval
Classification Interval
Static
Slow
Fast
Static
Slow
Fast
Static
Slow
Fast
OA
MCA
MotionNet [88]
OT128 1
0.0099
0.7103
1.1664
0.0057
0.5026
0.7779
0.0064
0.4424
0.8316
0.9825
0.7276
MotionNet
AT128 0
0.0098
0.7320
1.2625
0.0065
0.5100
0.7451
0.0060
0.4473
0.8290
0.9827
0.7364
MotionNet
FMCW 4D 0
0.0097
0.7328
1.2504
0.0063
0.4909
0.8021
0.0059
0.4632
0.8568
0.9817
0.7179
MotionNet†
FMCW 4D 0
0.0007
0.6805
1.0844
0.0004
0.4656
0.6543
0.0003
0.4204
0.7377
0.9817
0.7022
STI [89]
OT128 1
0.0097
0.6772
1.1482
0.0065
0.4732
0.6668
0.0060
0.4071
0.7751
0.9817
0.7341
STI
AT128 0
0.0099
0.6794
1.0464
0.0067
0.4533
0.6491
0.0061
0.4117
0.7049
0.9825
0.7375
STI
FMCW 4D 0
0.0099
0.7199
1.2354
0.0064
0.4891
0.7893
0.0060
0.4429
0.8600
0.9809
0.7128
STI†
FMCW 4D 0
0.0006
0.6353
1.0391
0.0005
0.4204
0.6385
0.0004
0.3916
0.7031
0.9821
0.7387
PriorMotion [90]
OT128 1
0.0098
0.6970
1.0517
0.0079
0.4836
0.6447
0.0073
0.4216
0.7174
0.9813
0.7345
PriorMotion
AT128 0
0.0099
0.6385
0.9959
0.0090
0.4545
0.6819
0.0044
0.3873
0.7482
0.9804
0.7572
PriorMotion
FMCW 4D 0
0.0103
0.6783
1.0801
0.0083
0.4886
0.6992
0.0077
0.4090
0.7308
0.9867
0.8219
PriorMotion†
FMCW 4D 0
0.0011
0.6218
1.0033
0.0009
0.4478
0.6829
0.0008
0.3822
0.7093
0.9864
0.8541
TABLE V
END-TO-END MOTION FORECASTING RESULTS COMPARING DIFFERENT LIDAR SENSORS WITH SPARSEDRIVE ARCHITECTURE.
Sensor
Method
ADE(6)
FDE(6)
AHE(6)
FHE(6)
ADE(1)
FDE(1)
AHE(1)
FHE(1)
AT128
SparseDrive
1.58
2.87
0.67
0.95
3.98
7.65
0.70
0.99
FMCW 4D
SparseDrive
1.47
2.58
0.63
0.89
3.58
6.85
0.65
0.93
OT128
SparseDrive
1.98
3.61
0.72
0.99
5.20
9.91
0.77
1.05
TABLE VI
END-TO-END PLANNING RESULTS COMPARING DIFFERENT LIDAR SENSORS WITH SPARSEDRIVE ARCHITECTURE.
Sensor
Method
ADE(6)
FDE(6)
AHE(6)
FHE(6)
ADE(1)
FDE(1)
AHE(1)
FHE(1)
AT128
SparseDrive
0.40
0.95
0.31
0.60
0.68
1.70
0.31
0.61
FMCW 4D
SparseDrive
0.38
0.79
0.27
0.52
0.66
1.54
0.25
0.51
OT128
SparseDrive
0.57
1.01
0.30
0.64
0.95
1.92
0.25
0.53
2) Baseline Results: Table V and Table VI present the E2E
motion forecasting and planning results, revealing a different
performance trend compared to the detection task.
Overall Performance. Contrary to the 3D detection results
where AT128 achieved the highest mAP/NDS, 4D FMCW
Lidar achieves the best performance among the evalu-
ated Lidar configurations in both motion forecasting and
planning tasks despite its lower raw detection metrics.
For motion forecasting (Table V), FMCW 4D achieves the
lowest errors across all metrics: ADE(6) of 1.47m (7.0% better
than AT128, 25.8% better than OT128) and FDE(6) of 2.58m
(10.1% better than AT128, 28.5% better than OT128). The
single-mode performance (k=1) shows even larger gains, with
FMCW 4D achieving FDE(1) of 6.85m vs. AT128’s 7.65m
and OT128’s 9.91m, indicating superior trajectory consistency
even when the model commits to a single hypothesis.
For planning (Table VI), FMCW 4D maintains its advantage
with FDE(6) of 0.79m (16.8% better than AT128, 21.8%
better than OT128) and FDE(1) of 1.54m (9.4% better than
AT128, 19.8% better than OT128). Heading estimation errors
(AHE/FHE) follow the same pattern, with FMCW 4D achiev-
ing the lowest angular deviations.
Performance Gap Analysis. The performance hierarchy
consistently follows: FMCW 4D > AT128 > OT128 across
all forecasting and planning metrics. The gap between FMCW
4D and scanning Lidars widens for long-horizon predictions
(FDE vs. ADE) and single-mode evaluation (k=1 vs. k=6),
suggesting that velocity information is particularly critical
for maintaining trajectory consistency over time and reducing
multi-modal ambiguity. OT128 exhibits notably degraded per-
formance in forecasting (FDE(6): 3.61m vs. FMCW’s 2.58m),
likely due to sparser point density affecting motion estimation
for distant dynamic agents.
Implications for System Design. These results suggest that
higher object-detection accuracy does not necessarily translate
into better downstream forecasting and planning performance.
While AT128 excels at static geometric reconstruction (as evi-
denced by superior detection AP), FMCW 4D’s instantaneous
velocity measurements provide critical dynamic scene under-
standing that proves more valuable for motion forecasting and
planning. The velocity channel enables:
• Early detection of dynamic agents: Direct velocity
observation reduces reliance on multi-frame motion es-
timation and can improve response latency in dynamic-


## Page 13

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
13
object detection (illustrated in Figure 8 and Figure 9).
• Robust motion initialization: More informative initial
velocity estimates can reduce the accumulation of errors
in trajectory rollouts, explaining the superior long-horizon
FDE performance.
• Reduced multi-modality: Velocity cues help reduce mo-
tion ambiguity and improve single-hypothesis prediction
accuracy (k=1 metrics).
D. Discussion
The experimental results reveal a task-dependent relation-
ship between geometric precision and direct motion measure-
ment in Lidar sensing.
Task-Specific Sensor Characteristics. For 3D object de-
tection, scanning Lidars such as AT128 show advantages
in static geometric reconstruction and small-object detection,
which can be attributed to denser spatial sampling. In contrast,
4D FMCW Lidar provides point-wise radial velocity mea-
surements that are particularly beneficial for tasks involving
dynamic-object motion, including BEV flow prediction, mo-
tion forecasting, and planning.
Value of Direct Velocity Measurement. The velocity-fused
variants in Table IV consistently improve motion estimation,
especially in the radial direction. This observation is consis-
tent with the measurement principle of FMCW Lidar, which
directly observes radial velocity while lateral motion still re-
quires inference from spatial context. The ablation in Table III
further shows that removing the velocity channel degrades
detection performance, indicating that velocity provides com-
plementary information rather than merely redundant features.
Sensor and Architecture Co-Design. The results also
suggest that the benefit of 4D FMCW Lidar depends on the
downstream model architecture. Motion-aware models such as
PriorMotion better exploit velocity cues than generic percep-
tion backbones, indicating that future 4D Lidar systems should
consider joint design of sensing modality, representation, and
learning architecture.
Practical Implications. These findings suggest that 4D
FMCW Lidar can complement scanning Lidars in autonomous
driving systems. Scanning Lidars remain useful for dense
geometric reconstruction, whereas 4D FMCW Lidar provides
direct motion measurements for dynamic-scene understanding.
Future multi-Lidar fusion strategies may benefit from explic-
itly combining these complementary sensing properties.
V. CONCLUSION
This paper presented 4DLidarOpen, an open large-scale
multi-modal autonomous driving dataset centered on 4D
FMCW Lidar sensing. The dataset integrates a forward-facing
4D FMCW Lidar, rotating OT Lidar, solid-state AT Lidar, ATX
blind-spot Lidars, synchronized surround-view cameras, and 6-
DOF ego-vehicle poses. It provides a benchmark platform for
4D scene understanding, multi-Lidar fusion, and motion-aware
autonomous driving.
Experiments on 3D object detection, BEV segmentation
and flow prediction, and motion forecasting with planning
show that point-wise radial velocity measurements provide
complementary information to conventional geometric Lidar
sensing. While scanning Lidars remain advantageous for dense
geometric reconstruction, 4D FMCW Lidar improves motion-
related perception and downstream forecasting and planning,
especially in dynamic scenarios.
The current dataset has several limitations. Its data are
mainly collected in Beijing urban environments, and part of
the training data relies on auto-labeled annotations that may
contain residual tracking errors. Future work will extend the
dataset to more cities, weather conditions, and sensor modal-
ities, and will introduce long-horizon forecasting benchmarks
and additional pretrained baselines.
4DLidarOpen provides a foundation for future research on
direct motion measurement, velocity-aware perception, and
robust planning for autonomous driving.
REFERENCES
[1] L. Chen, P. Wu, K. Chitta, B. Jaeger, A. Geiger, and H. Li, “End-to-end
autonomous driving: Challenges and frontiers,” IEEE Transactions on
Pattern Analysis and Machine Intelligence, 2024.
[2] S. Jiang, Z. Huang, K. Qian, Z. Luo, T. Zhu, Y. Zhong, Y. Tang,
M. Kong, Y. Wang, S. Jiao et al., “A survey on vision-language-
action models for autonomous driving,” in Proceedings of the IEEE/CVF
International Conference on Computer Vision, 2025, pp. 4524–4536.
[3] K. Qian, S. Jiang, Y. Zhong, Z. Luo, Z. Huang, T. Zhu, K. Jiang,
M. Yang, Z. Fu, J. Miao et al., “Agentthink: A unified framework for
tool-augmented chain-of-thought reasoning in vision-language models
for autonomous driving,” arXiv preprint arXiv:2505.15298, vol. 1, no. 2,
p. 3, 2025.
[4] B.
Yu
and
L.
Zhao,
“4d-are:
Bridging
the
attribution
gap
in
llm
agent
requirements
engineering,”
2026.
[Online].
Available:
https://arxiv.org/abs/2601.04556
[5] Y. Shi, K. Jiang, K. Wang, J. Li, Y. Wang, M. Yang, and D. Yang,
“Streamingflow: Streaming occupancy forecasting with asynchronous
multi-modal data streams via neural ordinary differential equation,” in
Proceedings of the IEEE/CVF Conference on Computer Vision and
Pattern Recognition, 2024, pp. 14 833–14 842.
[6] S. Chen, B. Jiang, H. Gao, B. Liao, Q. Xu, S. Zhang, C. Huang, C. Liu,
and X. Wang, “Vadv2: End-to-end vectorized autonomous driving via
probabilistic planning,” arXiv preprint arXiv:2402.13243, 2024.
[7] C. Min, D. Zhao, L. Xiao, J. Zhao, X. Xu, Z. Zhu, L. Jin, J. Li,
Y. Guo, J. Xing et al., “Driveworld: 4d pre-trained scene understanding
via world models for autonomous driving,” in Proceedings of the
IEEE/CVF conference on computer vision and pattern recognition, 2024,
pp. 15 522–15 533.
[8] Y. Zheng, P. Yang, Z. Xing, Q. Zhang, Y. Zheng, Y. Gao, P. Li, T. Zhang,
Z. Xia, P. Jia et al., “World4drive: End-to-end autonomous driving via
intention-aware physical latent world model,” in Proceedings of the
IEEE/CVF International Conference on Computer Vision, 2025, pp.
28 632–28 642.
[9] A. Geiger, P. Lenz, C. Stiller, and R. Urtasun, “Vision meets robotics:
The KITTI dataset,” The International Journal of Robotics Research,
vol. 32, no. 11, pp. 1231–1237, Sep. 2013.
[10] H. Caesar, V. Bankiti, A. H. Lang, S. Vora, V. E. Liong, Q. Xu,
A. Krishnan, Y. Pan, G. Baldan, and O. Beijbom, “nuscenes: A multi-
modal dataset for autonomous driving,” in Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition (CVPR), June
2020.
[11] A. Geiger, P. Lenz, and R. Urtasun, “Are we ready for autonomous
driving? The KITTI vision benchmark suite,” in Proceedings of the
IEEE/CVF Conference on Computer Vision and Pattern Recognition
(CVPR), Jun. 2012.
[12] A. H. Lang, S. Vora, H. Caesar, L. Zhou, J. Yang, and O. Beijbom,
“PointPillars: Fast encoders for object detection from point clouds,”
in Proceedings of the IEEE/CVF Conference on Computer Vision and
Pattern Recognition (CVPR), June 2019.
[13] T. Yin, X. Zhou, and P. Krahenbuhl, “Center-based 3d object detection
and tracking,” in Proceedings of the IEEE/CVF Conference on Computer
Vision and Pattern Recognition (CVPR), June 2021.


## Page 14

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
14
[14] J. Behley, M. Garbade, A. Milioto, J. Quenzel, S. Behnke, C. Stachniss,
and J. Gall, “Semantickitti: A dataset for semantic scene understanding
of lidar sequences,” in Proceedings of the IEEE/CVF International
Conference on Computer Vision (ICCV), October 2019.
[15] Z. Liu, H. Tang, A. Amini, X. Yang, H. Mao, D. Rus, and S. Han,
“Bevfusion: Multi-task multi-sensor fusion with unified bird’s-eye view
representation,” arXiv preprint arXiv:2205.13542, 2022.
[16] M. Liang, B. Yang, R. Hu, Y. Chen, R. Liao, S. Feng, and R. Urtasun,
“Learning lane graph representations for motion forecasting,” in ECCV,
2020.
[17] J. Mercat, T. Gilles, N. El Zoghby, G. Sandou, D. Beauvois, and
G. P. Gil, “Multi-head attention for multi-modal joint vehicle motion
forecasting,” in ICRA.
IEEE, 2020.
[18] M. Cordts, M. Omran, S. Ramos, T. Rehfeld, M. Enzweiler, R. Benen-
son, U. Franke, S. Roth, and B. Schiele, “The Cityscapes Dataset for
Semantic Urban Scene Understanding,” in Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition (CVPR), 2016,
pp. 3213–3223.
[19] Y. Ma, X. Zhu, S. Zhang, R. Yang, W. Wang, and D. Manocha,
“Trafficpredict: Trajectory prediction for heterogeneous traffic-agents,”
CoRR, vol. abs/1811.02146, 2018.
[20] P. Sun, H. Kretzschmar, X. Dotiwalla, A. Chouard, V. Patnaik, P. Tsui,
J. Guo, Y. Zhou, Y. Chai, B. Caine, V. Vasudevan, W. Han, J. Ngiam,
H. Zhao, A. Timofeev, S. Ettinger, M. Krivokon, A. Gao, A. Joshi,
Y. Zhang, J. Shlens, Z. Chen, and D. Anguelov, “Scalability in Percep-
tion for Autonomous Driving: Waymo Open Dataset,” in Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern Recognition
(CVPR), 2020.
[21] K. Li, K. Chen, H. Wang, L. Hong, C. Ye, J. Han, Y. Chen, W. Zhang,
C. Xu, D.-Y. Yeung et al., “Coda: A real-world road corner case dataset
for object detection in autonomous driving,” in European Conference on
Computer Vision.
Springer, 2022, pp. 406–423.
[22] P. Xiao, Z. Shao, S. Hao, Z. Zhang, X. Chai, J. Jiao, Z. Li, J. Wu, K. Sun,
K. Jiang et al., “Pandaset: Advanced sensor suite dataset for autonomous
driving,” in 2021 IEEE international intelligent transportation systems
conference (ITSC).
IEEE, 2021, pp. 3095–3101.
[23] A. Dosovitskiy, G. Ros, F. Codevilla, A. Lopez, and V. Koltun, “Carla:
An open urban driving simulator,” in Conference on robot learning.
PMLR, 2017, pp. 1–16.
[24] K. Qian, J. Miao, Z. Luo, Z. Fu, J. Li, Y. Shi, Y. Wang, K. Jiang,
M. Yang, and D. Yang, “Lego-motion: Learning-enhanced grids with
occupancy instance modeling for class-agnostic motion prediction,” in
2025 IEEE/RSJ International Conference on Intelligent Robots and
Systems (IROS).
IEEE, 2025, pp. 14 178–14 185.
[25] B. Paden, M. ˇC´ap, S. Z. Yong, D. Yershov, and E. Frazzoli, “A survey of
motion planning and control techniques for self-driving urban vehicles,”
IEEE Transactions on intelligent vehicles, vol. 1, no. 1, pp. 33–55, 2016.
[26] M. Bojarski, D. Del Testa, D. Dworakowski, B. Firner, B. Flepp,
P. Goyal, L. D. Jackel, M. Monfort, U. Muller, J. Zhang et al., “End
to end learning for self-driving cars,” arXiv preprint arXiv:1604.07316,
2016.
[27] F. Codevilla, M. M¨uller, A. L´opez, V. Koltun, and A. Dosovitskiy,
“End-to-end driving via conditional imitation learning,” in 2018 IEEE
international conference on robotics and automation (ICRA).
IEEE,
2018, pp. 4693–4700.
[28] H. Xu, Y. Gao, F. Yu, and T. Darrell, “End-to-end learning of driving
models from large-scale video datasets,” in Proceedings of the IEEE
conference on computer vision and pattern recognition, 2017, pp. 2174–
2182.
[29] A. Kendall, J. Hawke, D. Janz, P. Mazur, D. Reda, J.-M. Allen, V.-D.
Lam, A. Bewley, and A. Shah, “Learning to drive in a day,” in 2019
international conference on robotics and automation (ICRA).
IEEE,
2019, pp. 8248–8254.
[30] J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov, “Prox-
imal policy optimization algorithms,” arXiv preprint arXiv:1707.06347,
2017.
[31] Z. Liu, H. Tang, A. Amini, X. Yang, H. Mao, D. L. Rus, and S. Han,
“Bevfusion: Multi-task multi-sensor fusion with unified bird’s-eye view
representation,” in 2023 IEEE international conference on robotics and
automation (ICRA).
IEEE, 2023, pp. 2774–2781.
[32] A. Prakash, K. Chitta, and A. Geiger, “Multi-modal fusion transformer
for end-to-end autonomous driving,” in Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition, 2021, pp.
7077–7087.
[33] K. Chitta, A. Prakash, B. Jaeger, Z. Yu, K. Renz, and A. Geiger,
“Transfuser: Imitation with transformer-based sensor fusion for au-
tonomous driving,” IEEE transactions on pattern analysis and machine
intelligence, vol. 45, no. 11, pp. 12 878–12 895, 2022.
[34] B. Jiang, S. Chen, Q. Xu, B. Liao, J. Chen, H. Zhou, S. Zhang,
C. Liu, C. Huang, X. Wang et al., “Vad: Vectorized scene representation
for efficient autonomous driving,” in Proceedings of the IEEE/CVF
International Conference on Computer Vision (ICCV), 2023, pp. 8340–
8350.
[35] F. Altch´e and A. de La Fortelle, “An lstm network for highway trajectory
prediction,” in 2017 IEEE 20th international conference on intelligent
transportation systems (ITSC).
IEEE, 2017, pp. 353–359.
[36] M. Crawshaw, “Multi-task learning with deep neural networks: A
survey,” arXiv preprint arXiv:2009.09796, 2020.
[37] K. Ishihara, A. Kanervisto, J. Miura, and V. Hautamaki, “Multi-task
learning with attention for end-to-end autonomous driving,” in Pro-
ceedings of the IEEE/CVF conference on computer vision and pattern
recognition, 2021, pp. 2902–2911.
[38] Y. Hu, J. Yang, L. Chen, K. Li, C. Sima, X. Zhu, S. Chai, S. Du, T. Lin,
W. Wang et al., “Planning-oriented autonomous driving,” in Proceedings
of the IEEE/CVF conference on computer vision and pattern recognition,
2023, pp. 17 853–17 862.
[39] F. Bartoccioni, E. Ramzi, V. Besnier, S. Venkataramanan, T.-H. Vu,
Y. Xu, L. Chambon, S. Gidaris, S. Odabas, D. Hurych et al., “Vavim
and vavam: Autonomous driving through video generative modeling,”
arXiv preprint arXiv:2502.15672, 2025.
[40] W. Peebles and S. Xie, “Scalable diffusion models with transformers,”
in Proceedings of the IEEE/CVF international conference on computer
vision, 2023, pp. 4195–4205.
[41] B. Liao, S. Chen, H. Yin, B. Jiang, C. Wang, S. Yan, X. Zhang,
X. Li, Y. Zhang, Q. Zhang, and X. Wang, “Diffusiondrive: Truncated
diffusion model for end-to-end autonomous driving,” arXiv preprint
arXiv:2411.15139, 2024.
[42] B. Jaeger, K. Chitta, and A. Geiger, “Hidden biases of end-to-end driving
models,” in Proceedings of the IEEE/CVF International Conference on
Computer Vision, 2023, pp. 8240–8249.
[43] W. Zeng, W. Luo, S. Suo, A. Sadat, B. Yang, S. Casas, and R. Urtasun,
“End-to-end interpretable neural motion planner,” in Proceedings of the
IEEE/CVF conference on computer vision and pattern recognition, 2019,
pp. 8660–8669.
[44] A. Sadat, S. Casas, M. Ren, X. Wu, P. Dhawan, and R. Urtasun,
“Perceive, predict, and plan: Safe motion planning through interpretable
semantic representations,” in Computer Vision–ECCV 2020: 16th Euro-
pean Conference, Glasgow, UK, August 23–28, 2020, Proceedings, Part
XXIII 16.
Springer, 2020, pp. 414–430.
[45] R. Rafailov, A. Sharma, E. Mitchell, C. D. Manning, S. Ermon, and
C. Finn, “Direct preference optimization: Your language model is
secretly a reward model,” Advances in Neural Information Processing
Systems, vol. 36, pp. 53 728–53 741, 2023.
[46] H. Touvron, T. Lavril, G. Izacard, X. Martinet, M.-A. Lachaux,
T. Lacroix, B. Rozi`ere, N. Goyal, E. Hambro, F. Azhar et al.,
“Llama: Open and efficient foundation language models,” arXiv preprint
arXiv:2302.13971, 2023.
[47] H. Touvron, L. Martin, K. Stone, P. Albert, A. Almahairi, Y. Babaei,
N. Bashlykov, S. Batra, P. Bhargava, S. Bhosale et al., “Llama
2: Open foundation and fine-tuned chat models,” arXiv preprint
arXiv:2307.09288, 2023.
[48] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal,
G. Sastry, A. Askell, P. Mishkin, J. Clark et al., “Learning transferable
visual models from natural language supervision,” in International
conference on machine learning.
PmLR, 2021, pp. 8748–8763.
[49] J. Mao, Y. Qian, J. Ye, H. Zhao, and Y. Wang, “Gpt-driver: Learning to
drive with gpt,” arXiv preprint arXiv:2310.01415, 2023.
[50] W. Wang, J. Xie, C. Hu, H. Zou, J. Fan, W. Tong, Y. Wen, S. Wu,
H. Deng, Z. Li et al., “Drivemlm: Aligning multi-modal large language
models with behavioral planning states for autonomous driving,” arXiv
preprint arXiv:2312.09245, 2023.
[51] H. Shao, Y. Hu, L. Wang, G. Song, S. L. Waslander, Y. Liu, and H. Li,
“Lmdrive: Closed-loop end-to-end driving with large language models,”
in Proceedings of the IEEE/CVF Conference on Computer Vision and
Pattern Recognition, 2024, pp. 15 120–15 130.
[52] J. Mao, J. Ye, Y. Qian, M. Pavone, and Y. Wang, “A language agent for
autonomous driving,” arXiv preprint arXiv:2311.10813, 2023.
[53] X. Hou, W. Wang, L. Yang, H. Lin, J. Feng,
H. Min,
and
X. Zhao, “Driveagent: Multi-agent structured reasoning with llm and
multimodal sensor fusion for autonomous driving,” arXiv preprint
arXiv:2505.02123, 2025.


## Page 15

SUBMITTED TO IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT
15
[54] L. Wen, D. Fu, X. Li, X. Cai, T. Ma, P. Cai, M. Dou, B. Shi, L. He, and
Y. Qiao, “Dilu: A knowledge-driven approach to autonomous driving
with large language models,” arXiv preprint arXiv:2309.16292, 2023.
[55] K. Jiang, X. Cai, Z. Cui, A. Li, Y. Ren, H. Yu, H. Yang, D. Fu,
L. Wen, and P. Cai, “Koma: Knowledge-driven multi-agent framework
for autonomous driving with large language models,” IEEE Transactions
on Intelligent Vehicles, 2024.
[56] R. Zhang, X. Guo, W. Zheng, C. Zhang, K. Keutzer, and L. Chen,
“Instruct large language models to drive like humans,” arXiv preprint
arXiv:2406.07296, 2024.
[57] A. Ishaq, J. Lahoud, K. More, O. Thawakar, R. Thawkar, D. Dis-
sanayake, N. Ahsan, Y. Li, F. S. Khan, H. Cholakkal et al., “Drivelmm-
o1: A step-by-step reasoning dataset and large multimodal model for
driving scenario understanding,” arXiv preprint arXiv:2503.10621, 2025.
[58] Z. Huang, C. Feng, F. Yan, B. Xiao, Z. Jie, Y. Zhong, X. Liang, and
L. Ma, “Drivemm: All-in-one large multimodal model for autonomous
driving,” arXiv preprint arXiv:2412.07689, 2024.
[59] B. Jiang, S. Chen, B. Liao, X. Zhang, W. Yin, Q. Zhang, C. Huang,
W. Liu, and X. Wang, “Senna: Bridging large vision-language models
and end-to-end autonomous driving,” arXiv preprint arXiv:2410.22313,
2024.
[60] H.
Huang,
F.
Liu,
L.
Fu,
T.
Wu,
M.
Mukadam,
J.
Malik,
K. Goldberg, and P. Abbeel, “Otter: A vision-language-action model
with text-aware visual feature extraction,” 2025. [Online]. Available:
https://arxiv.org/abs/2503.03734
[61] Z. Zhou, T. Cai, S. Z. Zhao, Y. Zhang, Z. Huang, B. Zhou, and J. Ma,
“Autovla: A vision-language-action model for end-to-end autonomous
driving with adaptive reasoning and reinforcement fine-tuning,” 2025.
[Online]. Available: https://arxiv.org/abs/2506.13757
[62] R. Sapkota, Y. Cao, K. I. Roumeliotis, and M. Karkee, “Vision-language-
action models: Concepts, progress, applications and challenges,” arXiv
preprint arXiv:2505.04769, 2025.
[63] Y. Ma, Z. Song, Y. Zhuang, J. Hao, and I. King, “A survey
on vision-language-action models for embodied ai,” arXiv preprint
arXiv:2405.14093, 2024.
[64] H. Fu, D. Zhang, Z. Zhao, J. Cui, D. Liang, C. Zhang, D. Zhang,
H. Xie, B. Wang, and X. Bai, “Orion: A holistic end-to-end autonomous
driving framework by vision-language instructed action generation,”
arXiv preprint arXiv:2503.19755, 2025.
[65] H. Arai, K. Miwa, K. Sasaki, K. Watanabe, Y. Yamaguchi, S. Aoki, and
I. Yamamoto, “Covla: Comprehensive vision-language-action dataset
for autonomous driving,” in 2025 IEEE/CVF Winter Conference on
Applications of Computer Vision (WACV). IEEE, 2025, pp. 1933–1943.
[66] Z. Chen, M. Ye, S. Xu, T. Cao, and Q. Chen, “Ppad: Iterative interactions
of prediction and planning for end-to-end autonomous driving,” in
European Conference on Computer Vision.
Springer, 2024, pp. 239–
256.
[67] X. Weng, B. Ivanovic, Y. Wang, Y. Wang, and M. Pavone, “Para-
drive: Parallelized architecture for real-time autonomous driving,” in
Proceedings of the IEEE/CVF Conference on Computer Vision and
Pattern Recognition, 2024, pp. 15 449–15 458.
[68] Y. Miyaoka, M. Inoue, and T. Nii, “Chatmpc: Natural language based
mpc personalization,” in 2024 American Control Conference (ACC).
IEEE, 2024, pp. 3598–3603.
[69] K. Long, H. Shi, J. Liu, and X. Li, “Vlm-mpc: Vision language
foundation model (vlm)-guided model predictive controller (mpc) for
autonomous driving,” arXiv preprint arXiv:2408.04821, 2024.
[70] A. Naumann, X. Gu, T. Dimlioglu, M. Bojarski, A. Degirmenci,
A. Popov, D. Bisla, M. Pavone, U. M¨uller, and B. Ivanovic, “Data
scaling laws for end-to-end autonomous driving,” arXiv preprint
arXiv:2504.04338, 2025.
[71] Y. Zheng, Z. Xia, Q. Zhang, T. Zhang, B. Lu, X. Huo, C. Han, Y. Li,
M. Yu, B. Jin et al., “Preliminary investigation into data scaling laws for
imitation learning-based end-to-end autonomous driving,” arXiv preprint
arXiv:2412.02689, 2024.
[72] H. Caesar, V. Bankiti, A. H. Lang, S. Vora, V. E. Liong, Q. Xu,
A. Krishnan, Y. Pan, G. Baldan, and O. Beijbom, “nuscenes: A
multimodal dataset for autonomous driving,” in Proceedings of the
IEEE/CVF conference on computer vision and pattern recognition, 2020,
pp. 11 621–11 631.
[73] P. Sun, H. Kretzschmar, X. Dotiwalla, A. Chouard, V. Patnaik, P. Tsui,
J. Guo, Y. Zhou, Y. Chai, B. Caine et al., “Scalability in perception
for autonomous driving: Waymo open dataset,” in Proceedings of the
IEEE/CVF conference on computer vision and pattern recognition, 2020,
pp. 2446–2454.
[74] M.-F. Chang, J. Lambert, P. Sangkloy, J. Singh, S. Bak, A. Hartnett,
D. Wang, P. Carr, S. Lucey, D. Ramanan et al., “Argoverse: 3d tracking
and forecasting with rich maps,” in Proceedings of the IEEE/CVF
conference on computer vision and pattern recognition, 2019, pp. 8748–
8757.
[75] B. Wilson, W. Qi, T. Agarwal, J. Lambert, J. Singh, S. Khandelwal,
B. Pan, R. Kumar, A. Hartnett, J. K. Pontes et al., “Argoverse 2: Next
generation datasets for self-driving perception and forecasting,” arXiv
preprint arXiv:2301.00493, 2023.
[76] Y. Li and J. Ibanez-Guzman, “Lidar for autonomous driving: The
principles, challenges, and trends for automotive lidar and perception
systems,” IEEE Signal Processing Magazine, vol. 37, no. 4, pp. 50–61,
2020.
[77] M. Jung, W. Yang, D. Lee, H. Gil, G. Kim, and A. Kim, “Helipr:
Heterogeneous lidar dataset for inter-lidar place recognition under spa-
tiotemporal variations,” The International Journal of Robotics Research,
vol. 43, no. 12, pp. 1867–1883, 2024.
[78] B. Hexsel, H. Vhavle, and Y. Chen, “DICP: Doppler Iterative Closest
Point Algorithm,” in Proceedings of Robotics: Science and Systems, New
York City, NY, USA, June 2022.
[79] Y. Zeng, Y. Yu, S. Qi, and T. Wu, “Tracking 3d moving objects as
centroids using fmcw lidar,” in Proceedings of 4th 2024 International
Conference on Autonomous Unmanned Systems (4th ICAUS 2024),
L. Liu, Y. Niu, W. Fu, and Y. Qu, Eds.
Singapore: Springer Nature
Singapore, 2025, pp. 536–545.
[80] D. J. Yoon, Y. Chen, H. Vhavle, J. Reuther, and T. D. Barfoot, “Towards
fast correspondence-free odometry using multiple fmcw lidars,” IEEE
Robotics and Automation Letters, vol. 10, no. 9, pp. 9088–9095, 2025.
[81] Y. Chae, H. Park, H. Kim, and K.-J. Yoon, “Doppler-aware lidar-radar
fusion for weather-robust 3d detection,” in Proceedings of the IEEE/CVF
International Conference on Computer Vision (ICCV), October 2025, pp.
27 197–27 208.
[82] M. Zhao, J. Wang, T. Gao, C. Xu, and H. Kong, “Fmcw-lio: A doppler
lidar-inertial odometry,” IEEE Robotics and Automation Letters, vol. 9,
no. 6, pp. 5727–5734, 2024.
[83] J. P. Rodr´ıguez-G´omez, R. Tapia, M. d. M. G. Garcia, J. R. M.-d. Dios,
and A. Ollero, “Free as a bird: Event-based dynamic sense-and-avoid for
ornithopter robot flight,” IEEE Robotics and Automation Letters, vol. 7,
no. 2, pp. 5413–5420, 2022.
[84] J. Lv, K. Hu, J. Xu, Y. Liu, X. Ma, and X. Zuo, “Clins: Continuous-
time trajectory estimation for lidar-inertial system,” in 2021 IEEE/RSJ
International Conference on Intelligent Robots and Systems (IROS),
2021, pp. 6657–6663.
[85] Y. Gu, H. Cheng, K. Wang, D. Dou, C. Xu, and H. Kong, “Learning
moving-object tracking with fmcw lidar,” in 2022 IEEE/RSJ Interna-
tional Conference on Intelligent Robots and Systems (IROS), 2022, pp.
3747–3753.
[86] J.-H. Cheng, S.-Y. Kuan, H.-I. Liu, H. Latapie, G. Liu, and J.-N. Hwang,
“Centerradarnet: Joint 3d object detection and tracking framework using
4d fmcw radar,” in 2024 IEEE International Conference on Image
Processing (ICIP), 2024, pp. 998–1004.
[87] P. Sun, H. Kretzschmar, X. Dotiwalla, A. Chouard, V. Patnaik, P. Tsui,
J. Guo, Y. Zhou, Y. Chai, B. Caine, V. Vasudevan, W. Han, J. Ngiam,
H. Zhao, A. Timofeev, S. Ettinger, M. Krivokon, A. Gao, A. Joshi,
Y. Zhang, J. Shlens, Z. Chen, and D. Anguelov, “Scalability in perception
for autonomous driving: Waymo open dataset,” in 2020 IEEE/CVF
Conference on Computer Vision and Pattern Recognition (CVPR), 2020,
pp. 2443–2451.
[88] P. Wu, S. Chen, and D. N. Metaxas, “Motionnet: Joint perception and
motion prediction for autonomous driving based on bird’s eye view
maps,” in Proceedings of the IEEE/CVF conference on computer vision
and pattern recognition, 2020, pp. 11 385–11 395.
[89] Y. Wang, H. Pan, J. Zhu, Y.-H. Wu, X. Zhan, K. Jiang, and D. Yang, “Be-
sti: Spatial-temporal integrated network for class-agnostic motion predic-
tion with bidirectional enhancement,” in Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition, 2022, pp.
17 093–17 102.
[90] K. Qian, J. Miao, X. Jiao, Z. Luo, Z. Fu, Y. Shi, Y. Wang, K. Jiang,
and D. Yang, “Priormotion: Generative class-agnostic motion prediction
with raster-vector motion field priors,” in Proceedings of the IEEE/CVF
International Conference on Computer Vision, 2025, pp. 27 284–27 294.

