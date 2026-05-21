# 123D: Unifying Multi-Modal Autonomous Driving Data at Scale

**Source**: arXiv:2605.08084

**Type**: Academic Paper

---

## Page 1

123D: Unifying Multi-Modal
Autonomous Driving Data at Scale
Daniel Dauner1,2
Valentin Charraut4
Bastian Berle2
Tianyu Li5
Long Nguyen1,2
Jiabao Wang6
Changhui Jing5
Maximilian Igl3
Holger Caesar7
Boris Ivanovic3
Yiyi Liao6
Andreas Geiger1
Kashyap Chitta1,3
1KE:SAI
2University of Tübingen, Tübingen AI Center
3NVIDIA Research
4Valeo Brain
5OpenDriveLab at Shanghai Innovation Institute
6Zhejiang University
7Delft University of Technology
Abstract
The pursuit of autonomous driving has produced one of the richest sensor data
collections in all of robotics. However, its scale and diversity remain largely un-
tapped. Each dataset adopts different 2D and 3D modalities, such as cameras,
lidar, ego states, annotations, traffic lights, and HD maps, with different rates and
synchronization schemes. They come in fragmented formats requiring complex
dependencies that cannot natively coexist in the same development environment.
Further, major inconsistencies in annotation conventions prevent training or mea-
suring generalization across multiple datasets. We present 123D, an open-source
framework that unifies such multi-modal driving data through a single API. To
handle synchronization, we store each modality as an independent timestamped
event stream with no prescribed rate, enabling synchronous or asynchronous access
across arbitrary datasets. Using 123D, we consolidate eight real-world driving
datasets spanning 3,300 hours and 90,000 kilometers, together with a synthetic
dataset with configurable collection scripts, and provide tools for data analysis and
visualization. We conduct a systematic study comparing annotation statistics and
assessing each dataset’s pose and calibration accuracy. Further, we showcase two
applications 123D enables: cross-dataset 3D object detection transfer and rein-
forcement learning for planning, and offer recommendations for future directions.
Code and documentation are available at https://github.com/kesai-labs/py123d.
1
Introduction
Progress in autonomous driving research is strongly tied to dataset releases. Every milestone in the
field, from modular perception [25, 6, 56], behavior prediction [10, 21, 29], to end-to-end driving [68,
51], has introduced new datasets, expanding a still-growing collection of driving recordings.
This collection is rarely studied as a whole. Instead, models are typically trained and evaluated on
splits of the same dataset. Each dataset is tied to specific biases, e.g., a single sensor configuration, a
single vehicle type, a handful of cities, and a particular collection period [61, 48]. It is likely infeasible
to establish generalizable driving intelligence via training on any single dataset with such inherent
biases. Re-collecting data for each deployment is also not a workable approach: sensor stacks,
operating domains, and demographic coverage all shift over time [65, 63, 64, 52], and re-collection
at sufficient scale each time requirements change is prohibitively expensive. Several questions arise
on how to go forward: how to curate what already exists, how to scale heterogeneous datasets jointly,
and how to combine real with synthetic data. None of these can be addressed one dataset at a time.
Despite the potential societal impact and research effort invested into autonomous driving, the com-
munity so far has limited infrastructure for managing data. Natural language processing consolidates
around shared corpora and libraries (e.g., Common Crawl [23], Hugging Face Datasets [40]) that
make systematic evaluation routine and, in turn, have enabled scaling of large language models. Gen-
arXiv:2605.08084v1  [cs.RO]  8 May 2026


## Page 2

Argoverse 2
Ego State
CARLA
nuScenes
Waymo
+ More
Bounding 
Boxes
Consolidation in 123D...
HD Maps
Reinforcement 
Learning
... & more
Scene Reconstruction
Data Analysis 
& Curation
Cross-Vehicle Learning
Lidar
Cameras
... enables cross-dataset applications:
...
Shared API
Uniﬁed Logs
Web Parser
3D Viewer
Figure 1: 123D. An open-source toolkit to consolidate fragmented driving data through a unified
format for modalities such as annotations, sensors, and HD maps. By overcoming this fragmentation,
123D enables a wide range of cross-dataset applications and research directions, including scene
reconstruction, cross-vehicle learning, and reinforcement-learning-based planning.
eral robotics has done the same with LeRobot [5] and Open X-Embodiment [14], where unified access
to data from dozens of robotic platforms has already produced generalist policies and demonstrable
cross-embodiment transfer [2]. The consistent pattern across fields is that consolidation precedes
scale, and that scale, when paired with sufficient diversity, changes what the field achieves [4].
In this paper, we establish such consolidation through 123D: one unified interface for 2D and 3D
driving data (Fig. 1). We provide a log format handling arbitrary frequencies and synchronization
schemes, alongside a principled approach to unifying conventions. This allows us to populate
123D with eight established datasets, such as nuScenes [6], the Waymo Open Dataset [56, 21], and
Argoverse 2 [66], and contribute a synthetic dataset collected in CARLA [20]. Due to the variance
across these datasets, 123D involves a substantial one-time initial engineering effort (Sec. 3.1), thereby
significantly simplifying the addition of new datasets to the collection. Our contributions are: (1) We
open-source py123d, a Python library and autonomous driving toolkit providing conversion, unified
access, and visualization for the above format and datasets. (2) We conduct a systematic cross-dataset
analysis of annotation, pose, and calibration quality that informs dataset understanding and guides
curation across heterogeneous sources. (3) We demonstrate cross-dataset 3D object detection and
reinforcement-learning-based planning, where we provide empirical evidence supporting the premise
that training on heterogeneous datasets assists both in-domain and cross-domain generalization.
2
Related Work
Driving Datasets.
Since KITTI [25] laid the foundations with stereo camera and lidar data,
public driving datasets have grown considerably in scale and sensor coverage. Each release is
typically introduced for a specific set of benchmark tasks, e.g., perception [6, 56, 46], motion
forecasting [10, 66, 21], data-driven planning [35], or end-to-end driving on either real [68] or
synthetic data [55, 34, 50]. Often, these data sources are shaped by task and engineering conventions
of the organization that released them. Moreover, several datasets have been repurposed to new
emergent tasks as the field progresses [30, 45, 55, 18, 42, 7], demonstrating the need for tooling
that handles general driving recordings uniformly. In this work, we provide such tooling capable of
handling diverse datasets to support research on a wide variety of autonomous driving tasks.
Cross-Dataset Frameworks. The robotics community has consolidated around shared data ecosys-
tems such as LeRobot [5] and Open X-Embodiment [14], which accelerate progress by providing
unified formats and tooling for training across heterogeneous platforms. The driving community
has pursued similar approaches, but each effort is purpose-built for a narrow family of tasks: agent
trajectories and maps are consolidated for motion prediction and planning simulation [33, 41, 43, 22],
point clouds or images for 3D object detection [15, 57], or raw sensor data for novel-view synthesis
and scene reconstruction [58, 12]. However, each framework makes task-specific simplifications that
make combining such tools challenging. For instance, trajdata [33] and ScenarioNet [41] discard all
sensors and resample logs onto a single fixed rate, while MMDetection3D [15] and OpenPCDet [57]
retain only detection-relevant subsets of each dataset. OmniRe [12] preserves multi-camera and lidar
2


## Page 3

Dataset Parser
Log / Map 
Writer
Log / Map 
Storage 
Scene / Map 
API
Viewer
Dataloader
...
...
ego_state_se3.arrow
camera.{id}.arrow
lidar.{id}.arrow
sync.arrow
map.arrow
object_id: int64
layer: uint8
wkb: binary
features: binary
Collection
timestamp_us: int64
pose_se3: arr[float64]
dyn_state: arr[float64]
timestamp_us: int64
pose_se3: arr[float64]
data: str/binary
timestamp_us: int64
uuid: binary
ego_state_se3: uint64
lidar.{id}: uint64
camera.{id}: uint64
...
timestamp_us: int64
data: str/binary
end_us: int64
Figure 2: Architecture. We parse existing datasets from cloud/local storage, or collect data in
simulation that we write to our unified Apache Arrow [24] log format (Sec. 3.1). The scene and map
API enable access to logs, and can be passed to a dataloader, viewer, or other application (Sec. 3.2).
observations, but with fixed per-dataset sample rates at pre-processing time and provides no map or
traffic-light abstraction. Recently, OmniLiDAR [38] aggregates 12 datasets, but only for lidar point
clouds. In this work, we instead expose raw sensor data, agent annotations, maps, and ego states as
modular, independent streams under a shared API, without enforcing fixed rates or episode lengths.
We demonstrate 123D’s generality on each of the task families above (i.e., planning simulation, 3D
detection, and scene reconstruction) for a heterogeneous collection of datasets.
3
The 123D Framework
Existing driving datasets differ widely in sensor configurations, coordinate conventions, label tax-
onomies, modality frequencies, and map representations. To address this heterogeneity, we develop
py123d, an open-source Python package (Apache 2.0) that parses disparate sources into a uniform
log and map format (Sec. 3.1) and provides common data access and tooling on top of it (Sec. 3.2). In
the following, we describe the key challenges encountered and how our framework addresses them.
3.1
Data Format & Conversion
Source Formats & Dependencies.
Each dataset comes with a different file layout, often with
optional or outdated dependencies that cannot coexist in a single environment. We encapsulate all
dataset-specific logic in a dataset parser that reads the source data, converts it to the 123D datatypes
and conventions, and passes the unified log and map content to a shared log writer/map writer (Fig. 2).
Each parser operates on a local copy of the source dataset. As most driving dataset providers permit
scripted downloads [6, 56, 66, 67, 21, 35, 51, 53, 50], our parser fetches the raw data directly, so that
a single terminal command both downloads and converts the dataset into 123D files.
Heterogeneous Modalities at Varying Frequencies. Recordings may be of variable durations even
within a single dataset, capturing modalities at vastly different rates. Some provide data synchronously
at shared keyframes, while others are recorded asynchronously as independent events. To handle
this inconsistency, we represent all continuous driving recordings as a log: a directory of Apache
Arrow IPC files [24], with one dataframe of timestamped events per modality (Fig. 2). A separate
sync table records, for each synchronized frame, the corresponding row index in every modality’s
dataframe, so that cross-modal alignment is precomputed once and available as a direct lookup at
access time. The sync table is configurable: it can preserve the source dataset’s original keyframes,
operate given a chosen reference modality, and optionally resample to a target rate. Since modalities
remain independent event streams in storage, the access layer can optionally bypass the sync table
and retrieve data at arbitrary timestamps. Moreover, static metadata (e.g., vehicle extent, sensor
calibration) is embedded independently in each file’s Arrow schema. 123D supports a broad set
of modalities, including ego-states, 3D bounding boxes, traffic light states, user-defined custom
datatypes, lidar point clouds, and camera images with multiple projection models.
External vs. Self-contained Logs.
Raw sensor data, such as high-resolution images and point
clouds, typically dominates a dataset’s storage footprint. To avoid data duplication if a dataset is
stored locally, our format defaults to an external approach, such as storing relative file paths. However,
our format may also operate self-contained, where sensor data is serialized directly into the log files.
A self-contained log is particularly beneficial for portability, parsing a dataset from cloud storage,
or when large numbers of small files impose strain on a storage system [1]. We support various
compression codecs (e.g., JPEG, PNG, MP4 for camera data; Draco, LAZ, or IPC binaries for
3


## Page 4

(a) nuScenes [6]
(b) WOD-Perception [56]
(c) AV2-Sensor [66]
(d) PandaSet [67]
(e) KITTI-360 [46]
(f) WOD-Motion [21]
(g) nuPlan [35]
(h) PAI-AV [51]
(i) CARLA [20]
Figure 3: 3D Viewer. Analyzing driving recordings requires frequent visual inspections. We show
visualizations of supported datasets in 3a-3i from our interactive 3D viewer based on Viser [71].
lidar point clouds), to remain configurable along trade-offs between storage size and access latency.
Importantly, sensor data access returns unified representations agnostic to the storage choice.
Structural variance in HD maps.
HD map representations across datasets differ in semantic
granularity, spatial coverage (city-wide vs. per-log), or dimensionality (3D vs. 2D). We define a vector-
based map representation that covers the superset of objects encountered across supported datasets,
distinguishing between polygon and polyline objects. Polygon objects include Lane (with centerline,
boundaries, speed limits, and neighbor references), LaneGroup (a collection of co-directional
lanes forming a graph), Intersection (junctions linking internal lane groups), as well as
Crosswalk , Carpark , Walkway , GenericDrivable , StopZone , and SpeedBump
each with 2D/3D polygon and triangle mesh attributes. Polyline objects include RoadEdge
(drivable/non-drivable boundaries) and RoadLine (semantic markings such as solid white or
dashed yellow lines). All map elements are stored in a single Arrow IPC file with encoded object
features and their geometry represented as Well-Known Binary (WKB) representations [31]. This
representation enables fast bulk reads and initialization of a Sort-Tile-Recursive (STR) tree [39] used
during map queries. Maps can reside within a specific log directory or dataset directory when shared
across multiple logs, as is common with city-wide maps.
Inconsistent Labels & Conventions. Label taxonomies across datasets may not fully align due to
differences in the annotation guidelines. Rather than imposing a single taxonomy, our framework
preserves original labels and provides deferred mappings to common semantic categories. Coordinate
conventions also differ across datasets, requiring careful alignment when combining data from
multiple sources. To remove this burden, we enforce standardized conventions across all converted
datasets: the Body Frame for the ego vehicle pose and bounding boxes follows ISO 8855 [32] (x:
forward, y: left, z: up; e.g., [6, 56, 66]); the Camera Frame uses the OpenCV convention [3] (x:
right, y: down, z: forward: e.g., [6, 66, 46]); and global coordinates follow the source dataset’s
native definition. Since the ego-pose origin varies between datasets (e.g., ground plane [51], or IMU
4


## Page 5

position [46]), we provide transformations, partially inferred from the vehicle model, to both the
rear-axle and vehicle center to support tasks such as motion planning and collision checking.
3.2
Data Access & Visualization
Scene API. Common workflows with driving data involve managing sub-sequences of recordings,
history and future time windows, or resampling between source and target frequencies. Our framework
provides a Scene API that makes these patterns declarative: the user specifies the desired datasets,
reference frequency, and required modalities, and receives lightweight scene objects that serve as
views into the underlying driving logs. To instantiate a large number of scenes (e.g., within a
dataloader), we keep memory usage proportional to what is accessed rather than what is indexed.
Scenes store log and index references internally, and modalities are loaded on demand through a
shared, least-recently-used (LRU) cache of memory-mapped log files. The API supports multiple
access modes: modalities can be retrieved at a synchronized iteration, queried asynchronously around
a timestamp (i.e., with exact, nearest, forward, or backward matching), or within a time window. This
is particularly useful when modalities have different native frequencies, e.g., when pairing each lidar
sweep with the nearest camera frame at the camera’s native rate.
Map API. HD-maps require specialized data access, such as nearest-neighbor or intersection queries
over map objects, which become expensive when applied naively to large, city-wide maps. We
provide a Map API, accessible from a scene, that serves these operations through the STR tree index
built at load time (Sec. 3.1), e.g., retrieving all lanes near the ego vehicle, as shown in the following.
from py123d.api import MapAPI, SceneAPI, SceneFilter, get_filtered_scenes
scene_filter = SceneFilter( # Mix datasets with different rigs and native rates.
split_names=["av2-sensor_train", "nuscenes_train", "wod-perception_train"],
target_iteration_duration_s=0.5, # 2 Hz shared reference rate
future_duration_s=4.0, history_duration_s=1.0, shuffle=True)
scene: SceneAPI = get_filtered_scenes(scene_filter, data_root=...)[0]
# 1. Sync access: ego / lidar at initial iteration.
ego = scene.get_ego_state_se3_at_iteration(iteration=0)
lidar = scene.get_lidar_at_iteration(iteration=0, lidar_id="lidar_top")
# 2. Async access: the nearest front-camera frame to the lidar sweep.
camera = scene.get_camera_at_timestamp(
timestamp=lidar.timestamp_start, camera_id="pcam_f0", criteria="nearest")
# 3. Map access: query nearby lanes and crosswalks around ego.
map_api: MapAPI = scene.get_map_api()
nearby = map_api.get_map_objects_in_radius(
point=ego.center_3d, radius=50.0, layers=["lane", "crosswalk"])
Visualization & Tools.
We include an interactive 3D viewer based on Viser [71] (see Fig. 3),
supporting point clouds, images, bounding boxes, and map elements, alongside matplotlib utilities
for 2D visualizations such as bird’s-eye-view and camera overlay plots. A geometry utility library
provides coordinate transformations, projection operations, and related primitives used throughout
the framework and available to downstream code. Standalone examples, including a PyTorch dataset
built on scenes and dataset conversion templates, are provided to lower the barrier to adoption.
4
Experiments
In this section, we use 123D’s standardized format to compare several established driving datasets.
Our analysis has two aims. First, we provide a deeper understanding of the datasets themselves
by analyzing differences in their annotations (Sec. 4.1) and pose and calibration quality (Sec. 4.2).
Second, we demonstrate cross-dataset perception and simulation applications, by studying multi-view
3D object detection (Sec. 4.3) and reinforcement learning for planning (Sec. 4.4).
Datasets. Producing annotations, such as bounding boxes, is labor-intensive, and the resulting trade-
off between label fidelity and scale divides existing driving datasets into three categories, as shown in
Table 1: (1) Manual labeling. Trained annotators draw or review boxes from the sensor stack (often
across multiple passes), providing high fidelity at considerable labor cost. Supported datasets in this
category are nuScenes [6] (incl. 2Hz→10Hz bounding box interpolation), WOD-Perception [56],
Argoverse 2 Sensor [66], PandaSet [67], and KITTI-360 [46], with durations ranging from 0.2 to 6.4
5


## Page 6

Table 1: Datasets. We compare scale (duration, driven distance, number of logs), sensor setup
(number, sampling rate), and annotation availability (3D boxes, traffic light states, HD maps).
Scale
Sensors [#/Hz]
Annotations [✓/Hz]
Dataset
Year
Dur. [h]
Dist. [km]
Logs [#]
Cam.
Lidar
3D Box
Tls.
Map
Manual
nuScenes [6]
2020
5.6
100.9
1,000
6 / 12
1 / 20
✓/ 2
✗
✓
WOD-Perc. [56]
2020
6.4
154.0
1,150
5 / 10
5 / 10
✓/ 10
✗
✓
AV2-Sens. [66]
2021
4.4
87.5
1,000
9 / 20
2 / 10
✓/ 10
✗
✓
PandaSet [67]
2021
0.2
8.3
103
6 / 10
2 / 10
✓/ 10
✗
✗
KITTI-360 [46]
2022
2.7
73.7
9
4 / 10
1 / 10
✓/ 10
✗
✓
Auto-labeled
WOD-Mot. [21]
2021
574.1
10,323.5*
103,354
✗
✗
✓/ 10
✓/ 10
✓
nuPlan [35]
2024
1,174.3
17,808.6
15,910
8 / 10†
5 / 20†
✓/ 20
✓/ 20
✓
– mini
7.2
103.0
64
PAI-AV [51]
2025
1,707.0
69,265.7
307,332
7 / 30
1 / 10
✓/ 10
✗
✗
– NCore [53]
2026
6.3
167.6
1,147
Synth.
CARLA [20]
2017
var.
var.
var.
var.
var.
✓
✓
✓
– L3AD [50]
2026
7.3
138.7
789
6 / 10
2 / 10
✓/ 10
✓/ 10
*Computed only from the non-overlapping 20 s training files. †Released for a 120 h subset; full coverage on mini.
hours. (2) Auto-labeling. Detection, tracking, and refinement pipelines generate boxes automatically
from the sensor stack, covering thousands of hours of data at reduced fidelity. In this category,
we include WOD-Motion [21], nuPlan [35], and PAI-AV [51]. For comparable duration and to
remain within our storage budget, we limit experiments to the mini and NCore subsets of nuPlan
and PAI-AV, respectively. We exclude WOD-Motion from experiments that require sensor data. (3)
Synthetic. Simulators provide unlimited labeled data, inferred from the ground-truth state of the
virtual driving environment. We provide a configurable collection pipeline for CARLA [20], based
on the state-of-the-art expert policy LEAD [50]. To demonstrate this collection pipeline, we publish
our L3AD dataset, which includes maps and roughly 7h of recordings that mirror the nuScenes sensor
layout (see Fig. 3i), enabling the sim-to-real transfer study in our 3D object detection experiment
(Sec. 4.3). Dataset-specific implementations are detailed in the supplementary material.
4.1
Cross-Dataset Annotation Analysis
We analyze the different annotation strategies between all nine datasets in terms of box ego distance,
speed, and acceleration distributions, as shown in Fig. 4. For this, we summarize the original semantic
labels to five categories: vehicle (e.g., car, bus, truck), person (e.g., pedestrian, rider), two-wheeler
(e.g., bicycle, motorcycle), obstacles (e.g., traffic cone, barrier, sign), and other (e.g., train, animal).
A complete summary of semantic labels can be found in the supplementary material.
Results. Annotation range varies widely: AV2-Sens., PandaSet, and PAI-AV stand out by labeling
boxes ranging from 200 meters and more, while the remaining adopt narrower annotation ranges. Note
that we apply configurable range limits in CARLA and KITTI-360 here, in order to avoid annotating
city-wide assets on a per-timestamp basis. Speed shows an expected ordering, with vehicles fastest
and two-wheelers second. The long high-speed vehicle tails in WOD-Perc., WOD-Mot., and PAI-AV
reflect the highway driving present in those logs, whereas more urban datasets rarely exceed 20 m/s.
Semantic ambiguities and label errors are particularly prevalent in the person class. For instance, Av2
and KITTI-360 apply separate bounding boxes for the rider and the two-wheeler, whereas WOD-Perc.
annotates e-scooters as pedestrians. Acceleration most clearly shows the labeling-quality gap between
regimes: auto-labeled datasets (WOD-Mot., nuPlan, PAI-AV) carry visibly wider acceleration tails
across categories, caused by per-frame box jitter from their detection-and-tracking pipelines. Together,
these differences underscore that working across heterogeneous datasets requires careful treatment
of label conventions and quality. Since 123D preserves the original annotations as-is, we view
re-annotation and open-vocabulary methods as an interesting application to explore.
4.2
Pose Accuracy & 3DGS Reconstruction
Beyond annotation quality, pose accuracy and sensor calibration are equally important for applications
such as photorealistic sensor simulation and multi-sensor fusion. To check whether each dataset’s
released poses and calibrations support photorealistic reconstruction, we run a per-dataset consistency
6


## Page 7

0
50
100
150
200
250
Box-Ego Distance (m)
nuScenes
WOD-Perc.
Av2-Sens.
PandaSet
KITTI-360
WOD-Mot.
nuPlan
PAI-AV
CARLA
Vehicle
0
50
100
150
200
250
Box-Ego Distance (m)
Person
0
50
100
150
200
250
Box-Ego Distance (m)
Two-Wheeler
0
50
100
150
200
250
Box-Ego Distance (m)
Obstacles
0
50
100
150
200
250
Box-Ego Distance (m)
Other
0
12
25
38
50
Speed (m/s)
nuScenes
WOD-Perc.
Av2-Sens.
PandaSet
KITTI-360
WOD-Mot.
nuPlan
PAI-AV
CARLA
0
12
25
38
50
Speed (m/s)
0
12
25
38
50
Speed (m/s)
0
12
25
38
50
Speed (m/s)
0
12
25
38
50
Speed (m/s)
-10
-5
0
5
10
Acceleration (m/s2)
nuScenes
WOD-Perc.
Av2-Sens.
PandaSet
KITTI-360
WOD-Mot.
nuPlan
PAI-AV
CARLA
-10
-5
0
5
10
Acceleration (m/s2)
-10
-5
0
5
10
Acceleration (m/s2)
-10
-5
0
5
10
Acceleration (m/s2)
-10
-5
0
5
10
Acceleration (m/s2)
10−5
10−4
10−3
10−2
10−1
10−5
10−3
10−1
10−4
10−3
10−2
10−1
100
Figure 4: Annotation of bounding boxes. We compare ego distance, speed, and acceleration (rows)
over different semantic categories, grouped into vehicle, person, two-wheeler, obstacles, and other
miscellaneous classes (columns). The histograms show frequencies in the range of 0-1 on a log scale.
Table 2: FastGS reconstruction with and without lidar registration. We evaluate 100 scenes per
dataset. Rendering metrics (PSNR, SSIM, LPIPS) are reported for models trained with original poses
and with Kiss-ICP-registered poses [59], together with the translation and rotation disagreement
between the datasets and registered poses. Per-column first, second, and third values are highlighted.
Original Poses
Registered Poses
Registration Mismatch
Dataset
PSNR↑
SSIM↑
LPIPS↓
PSNR↑
SSIM↑
LPIPS↓
¯terr (m)↓
¯Rerr (°)↓
CARLA
31.97±3.45
0.889±0.05
0.184±0.08
29.53±4.38
0.833±0.08
0.224±0.07
0.844±2.20
0.96±3.53
Av2-Sens.
27.32±1.75
0.792±0.05
0.254±0.04
26.02±1.65
0.749±0.05
0.282±0.04
0.114±0.10
0.41±0.35
PAI-AV
26.66±2.29
0.826±0.07
0.212±0.05
26.22±2.28
0.812±0.07
0.223±0.05
0.158±0.11
0.31±0.32
WOD-Perc.
26.59±2.13
0.806±0.06
0.293±0.05
26.27±2.15
0.794±0.06
0.299±0.05
0.093±0.06
0.09±0.04
nuScenes
25.39±2.21
0.780±0.09
0.308±0.07
23.11±2.18
0.727±0.08
0.351±0.07
0.455±0.30
1.38±0.87
nuPlan
25.17±1.47
0.792±0.04
0.306±0.05
25.22±1.48
0.791±0.04
0.303±0.04
0.253±0.13
0.55±0.28
PandaSet
24.03±3.29
0.693±0.14
0.290±0.05
24.02±3.31
0.692±0.13
0.290±0.05
0.125±0.07
0.27±0.15
KITTI-360
19.92±1.75
0.684±0.05
0.346±0.04
19.36±1.69
0.665±0.05
0.360±0.04
0.174±0.09
0.40±0.26
check. Specifically, we create two reconstructions of each scene, one with the released poses and
one with poses independently re-estimated by the Kiss-ICP lidar-based registration algorithm [59], to
compare novel-view rendering quality. Importantly, this experiment is not a ranking of pose accuracy:
neither pose source is ground truth, and rendering quality additionally reflects each dataset’s full
sensor stack (lidar density, camera coverage, lighting, exposure). We select N = 100 scenes per
dataset at 10 Hz over a fixed 7-second duration, choosing those whose ego-path length most closely
matches the global median (∼39 m) so that speed and distance are comparable across scenes. We
generate per-frame semantic segmentation maps for all camera views using Mask2Former [13] and
mask out dynamic semantic classes in image space so that reconstruction quality reflects only static
scene geometry. For datasets with distorted images, we undistort the views using the provided intrinsic
parameters. Using these inputs, we perform lidar point cloud stacking and FastGS reconstruction [54]
(an efficient variant of 3DGS [36]) twice per scene, once with the released poses and once with
the Kiss-ICP-estimated poses. We hold out every fourth camera rig capture as a test set to evaluate
novel-view rendering quality. Further details are provided in the supplementary material.
Results. We summarize rendering quality and the disagreement between released and Kiss-ICP-
estimated poses in Table 2. On most datasets, the released poses yield equal or slightly better
rendering quality than the Kiss-ICP poses, indicating that the released calibrations are well-tuned
7


## Page 8

Figure 5: Multi-view 3D Object Detection. Per-dataset nuScenes detection score (NDS) for
PETR [49] and BEVFormer-S [44] for vehicle detection. We evaluate on held-out validation splits of
each dataset and train on nuScenes, WOD-Perc., Av2-Sens., nuPlan, CARLA, or a uniform mixture
of these five (Mixed-5, dashed). PandaSet, KITTI-360, and PAI-AV are never seen during training.
for novel-view reconstruction; nuPlan is the only real dataset where Kiss-ICP gives a marginal
improvement. The pose-disagreement column should be read as agreement between two pipelines
rather than a pose-error estimate, since a large value can reflect either an issue in the released poses
or a failure of Kiss-ICP itself. The largest disagreements occur on nuScenes (0.455 m) and CARLA
(0.844 m), both of which use sparser 32-beam lidars whose returns may yield too few correspondences
for reliable registration. Absolute rendering scores vary widely across datasets, but, as noted, reflect
the sensor stack rather than a quality ordering. CARLA’s high scores are expected from a synthetic
source with ground-truth poses, lower fidelity, and global shutters. KITTI-360’s lower scores arise
due to the limited surround coverage (after undistorting the fisheye views) and as the lidar only
projects onto the lower half of each image, leaving upper regions without point-based initialization.
4.3
Cross-Dataset Multi-View 3D Object Detection
Next, we study how well common camera-based 3D detectors generalize across sensor rigs and
operating domains. We implement two representative non-temporal architectures, PETR [49] and
BEVFormer-S [44], both with ResNet50 encoders [28], using the 123D interface. We restrict the
evaluation to the vehicle class, the category with the least taxonomic ambiguity across datasets
(Sec. 4.1), and to ground-truth boxes within a 50 m radius that are visible in the camera field of view
and contain at least one lidar return. Following common practice in this setting [60, 9, 37], we report
a modified nuScenes-detection-score (NDS) that excludes velocity and attribute errors. We train on
nuScenes, WOD-Perc., AV2-Sens., nuPlan, and CARLA individually, and on a uniform mixture of all
five (Mixed-5). To isolate data diversity from data volume, every training configuration uses a fixed
budget of 30k frames (6k per dataset for Mixed-5). Further details are outlined in the supplementary.
Results. We summarize the cross-dataset transfer results for both detectors in Fig. 5. Single-dataset
models retain 0.41–0.67 NDS in-domain but generally transfer poorly to other datasets (0.10–0.46
NDS). Transfer is asymmetric across sources: nuScenes is the most portable source relative to other
single-dataset runs, while WOD-Perc. is the weakest, likely due to its limited 230◦camera coverage
seen during training. Despite using the nuScenes camera extrinsics, CARLA-trained models do not
transfer preferentially to nuScenes (e.g., 0.24 for PETR), similar in performance to models trained on
Av2-Sens. or nuPlan. This suggests that, for object detection, sim-to-real transfer is no easier than
cross-rig transfer between real datasets, even when the simulator replicates the target rig.
Joint Mixed-5 training closes most of these gaps at no extra training budget, approaching or exceeding
single-dataset quality on most datasets in the mixture. BEVFormer-S benefits evenly (joint training
closely matches single-dataset performance throughout), whereas PETR exhibits larger swings, such
as gains on WOD-Perc. (0.41→0.54) but regressions on nuScenes (0.57→0.46).
Generalization to the three fully held-out datasets (PandaSet, KITTI-360, and PAI-AV) remains
the hardest task. BEVFormer-S is consistently better here, exceeding PETR by 0.07–0.20 NDS,
8


## Page 9

suggesting that explicit BEV-grid representations transfer across rigs more robustly. Cross-rig
generalization thus benefits from both training diversity and architectural inductive bias. However,
the gaps remain substantial, leaving cross-rig generalization an open research problem that 123D now
enables across eight heterogeneous real and synthetic datasets.
4.4
Reinforcement Learning for Planning
Data-driven simulators enable training and evaluation of policies with real-world maps and traffic
states. However, they are commonly built for a single dataset [35, 27]. We demonstrate simulation
across datasets by implementing a compatibility layer to PufferDrive [16], an optimized simulator
for multi-agent reinforcement learning. We infer the route, a necessary input for reinforcement
learning planners, for a subset of actors in a scene, covering the logged trajectory and beyond. We
use the default policy and reward implemented in PufferDrive based on GIGAFLOW [17], which
leverages self-play to control the selected actors during training. Each actor observes a vectorized
view of lanes, boundaries, and other actors in the scene, together with 5 goal points to reach along
the extracted route. We measure the success rate over agents as reaching the last point of the logged
trajectory without off-road, red-light, or collision infractions. We conduct training and evaluation on
WOD-Motion (9.1s with improved traffic lights [69]), nuPlan (20s), Av2-Sens. (15s, no traffic lights),
and mixed training of these three (Mixed-3). As a held-out test environment, we evaluate on CARLA
maps using randomly generated initial states of 40 actors in the scene, similar to [17].
Figure 6: PufferDrive Planning [16].
Results. We summarize the results on held-out test scenes
in Fig. 6. When evaluating WOD-Motion and nuPlan, we
observe the best performance with in-domain trained mod-
els. Interestingly, policies trained with Av2-Sensor exhibit
limited cross-domain generalization, but also underper-
form in-domain compared to nuPlan training, likely due
to the absence of traffic lights and the simpler scenarios
encountered during Av2-Sensor training. Cross-training
jointly on all three real-world environments (Mixed-3)
shows the highest success rates in the three in-domain
environments. Importantly, the absolute gap to in-domain
performance (i.e., WOD-Motion, nuPlan, or Av2-Sensor)
on CARLA remains substantial, even for the Mixed-3 ap-
proach which generalizes best. The results highlight the
potential of cross-domain training and motivate further
exploration in this research direction.
5
Conclusion
In this paper, we present 123D, an open-source consolidation of diverse multi-modal driving datasets.
It provides unified access to a wide range of sensor setups at an unprecedented scale. This, in turn,
opens up new research questions that are not yet well explored. Our experiments demonstrate that
cross-domain and vehicle transfer remains challenging for both perception and behavior tasks, and that
simple data mixing reduces this gap to some extent. Going further, improved data mixing methods are
an interesting avenue that has already proven crucial for training large language models [11, 26, 70].
To support this, we see particular promise in curating data through our API using foundation models
for reasoning [62] and vision [8, 47], automatically aligning annotation guidelines [72, 73], and
filtering specific scenarios [19]. By releasing 123D, we lower the barrier to pursuing these directions
and leveraging large-scale, diverse data in autonomous driving.
Limitations. We identify three concrete limitations for future development. First, we currently focus
on common sensor modalities widely available across datasets. Expanding support for additional
sensors (e.g., radar [6, 51]) and annotations (e.g., semantic point clouds or images [67, 56, 6, 46])
remains a priority for the future. Second, 123D currently does not explicitly support web datasets
or data streaming. However, the Apache Arrow IPC format provides features for cloud access [24]
that we have preliminarily tested and hope to integrate in the future. Third, our supported datasets
focus on standard vehicles. We aim to expand this scope to include trucks, mobile robots, and other
platforms, and we invite community contributions to help broaden the coverage and utility of 123D.
9


## Page 10

Acknowledgments
This work was supported by ERC Starting Grant LEGO-3D (850533) and the DFG EXC number
2064/1 - project number 390727645. Daniel Dauner was supported by the German Federal Ministry
for Economic Affairs and Energy within the project NXT GEN AI METHODS (19A23014S). This
research used compute resources at the Tübingen Machine Learning Cloud, DFG FKZ INST 37/1057-
1 FUGG as well as the Training Center for Machine Learning (TCML). We thank the International
Max Planck Research School for Intelligent Systems (IMPRS-IS) for supporting Daniel Dauner.
References
[1] Alex Aizman, Gavin Maltby, and Thomas Breuel. High performance i/o for large scale deep
learning. In 2019 IEEE International Conference on Big Data (Big Data), pages 5965–5967.
IEEE, 2019.
[2] Kevin Black, Noah Brown, Danny Driess, Adnan Esmail, Michael Equi, Chelsea Finn, Niccolo
Fusai, Lachy Groom, Karol Hausman, Brian Ichter, et al. π0: A vision-language-action flow
model for general robot control. arXiv.org, 2024.
[3] G. Bradski. The OpenCV Library. Dr. Dobb’s Journal of Software Tools, 2000.
[4] Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal,
Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, Sandhini Agarwal, Ariel
Herbert-Voss, Gretchen Krueger, Tom Henighan, Rewon Child, Aditya Ramesh, Daniel M.
Ziegler, Jeffrey Wu, Clemens Winter, Christopher Hesse, Mark Chen, Eric Sigler, Mateusz
Litwin, Scott Gray, Benjamin Chess, Jack Clark, Christopher Berner, Sam McCandlish, Alec
Radford, Ilya Sutskever, and Dario Amodei. Language models are few-shot learners. In
Advances in Neural Information Processing Systems (NeurIPS), 2020.
[5] Remi Cadene, Simon Alibert, Alexander Soare, Quentin Gallouedec, Adil Zouitine, Steven
Palma, Pepijn Kooijmans, Michel Aractingi, Mustafa Shukor, Dana Aubakirova, Martino
Russi, Francesco Capuano, Caroline Pascal, Jade Choghari, Jess Moss, and Thomas Wolf.
Lerobot: State-of-the-art machine learning for real-world robotics in pytorch. https://github.
com/huggingface/lerobot, 2024.
[6] Holger Caesar, Varun Bankiti, Alex H Lang, Sourabh Vora, Venice Erin Liong, Qiang Xu, Anush
Krishnan, Yu Pan, Giancarlo Baldan, and Oscar Beijbom. nuscenes: A multimodal dataset for
autonomous driving. In Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR),
2020.
[7] Wei Cao, Marcel Hallgarten, Tianyu Li, Daniel Dauner, Xunjiang Gu, Caojun Wang, Yakov
Miron, Marco Aiello, Hongyang Li, Igor Gilitschenski, Boris Ivanovic, Marco Pavone, Andreas
Geiger, and Kashyap Chitta. Pseudo-simulation for autonomous driving. In Proc. Conf. on
Robot Learning (CoRL), 2025.
[8] Nicolas Carion, Laura Gustafson, Yuan-Ting Hu, Shoubhik Debnath, Ronghang Hu, Didac
Suris, Chaitanya Ryali, Kalyan Vasudev Alwala, Haitham Khedr, Andrew Huang, et al. Sam 3:
Segment anything with concepts. Proc. of the International Conf. on Learning Representations
(ICLR), 2026.
[9] Gyusam Chang, Jiwon Lee, Donghyun Kim, Jinkyu Kim, Dongwook Lee, Daehyun Ji, Sujin
Jang, and Sangpil Kim. Unified domain generalization and adaptation for multi-view 3d object
detection. Advances in Neural Information Processing Systems (NeurIPS), 2024.
[10] Ming-Fang Chang, John Lambert, Patsorn Sangkloy, Jagjeet Singh, Slawomir Bak, Andrew
Hartnett, De Wang, Peter Carr, Simon Lucey, Deva Ramanan, et al. Argoverse: 3d tracking and
forecasting with rich maps. In Proc. IEEE Conf. on Computer Vision and Pattern Recognition
(CVPR), 2019.
[11] Mayee F Chen, Tyler Murray, David Heineman, Matt Jordan, Hannaneh Hajishirzi, Christo-
pher Ré, Luca Soldaini, and Kyle Lo. Olmix: A framework for data mixing throughout lm
development. arXiv.org, 2026.
10


## Page 11

[12] Ziyu Chen, Jiawei Yang, Jiahui Huang, Riccardo de Lutio, Janick Martinez Esturo, Boris
Ivanovic, Or Litany, Zan Gojcic, Sanja Fidler, Marco Pavone, et al. Omnire: Omni urban scene
reconstruction. Proc. of the International Conf. on Learning Representations (ICLR), 2025.
[13] Bowen Cheng, Ishan Misra, Alexander G Schwing, Alexander Kirillov, and Rohit Girdhar.
Masked-attention mask transformer for universal image segmentation. In Proc. IEEE Conf. on
Computer Vision and Pattern Recognition (CVPR), 2022.
[14] OX-Embodiment Collaboration, Abby O’Neill, Abdul Rehman, Abhinav Gupta, Abhiram Mad-
dukuri, Abhishek Gupta, Abhishek Padalkar, Abraham Lee, Acorn Pooley, Agrim Gupta, et al.
Open x-embodiment: Robotic learning datasets and rt-x models. In Proc. IEEE International
Conf. on Robotics and Automation (ICRA), 2023.
[15] MMDetection3D Contributors. MMDetection3D: OpenMMLab next-generation platform for
general 3D object detection. https://github.com/open-mmlab/mmdetection3d, 2020.
[16] Daphne Cornelisse*, Spencer Cheng*, Pragnay Mandavilli, Julian Hunt, Kevin Joseph, Waël
Doulazmi, Valentin Charraut, Aditya Gupta, Joseph Suarez, and Eugene Vinitsky. PufferDrive:
A fast and friendly driving simulator for training and evaluating RL agents, 2026. URL
https://github.com/Emerge-Lab/PufferDrive.
[17] Marco Cusumano-Towner, David Hafner, Alex Hertzberg, Brody Huval, Aleksei Petrenko,
Eugene Vinitsky, Erik Wijmans, Taylor Killian, Stuart Bowers, Ozan Sener, et al. Robust
autonomy emerges from self-play. Proc. of the International Conf. on Machine learning
(ICML), 2025.
[18] Daniel Dauner, Marcel Hallgarten, Tianyu Li, Xinshuo Weng, Zhiyu Huang, Zetong Yang,
Hongyang Li, Igor Gilitschenski, Boris Ivanovic, Marco Pavone, et al. Navsim: Data-driven non-
reactive autonomous vehicle simulation and benchmarking. Advances in Neural Information
Processing Systems (NeurIPS), 2024.
[19] Cainan Davidson, Deva Ramanan, and Neehar Peri. Refav: Towards planning-centric scenario
mining. In Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR), 2026.
[20] Alexey Dosovitskiy, German Ros, Felipe Codevilla, Antonio Lopez, and Vladlen Koltun.
CARLA: An open urban driving simulator. In Proc. Conf. on Robot Learning (CoRL), 2017.
[21] Scott Ettinger, Shuyang Cheng, Benjamin Caine, Chenxi Liu, Hang Zhao, Sabeek Pradhan,
Yuning Chai, Ben Sapp, Charles R Qi, Yin Zhou, et al. Large scale interactive motion forecasting
for autonomous driving: The waymo open motion dataset. In Proc. of the IEEE International
Conf. on Computer Vision (ICCV), 2021.
[22] Lan Feng, Mohammadhossein Bahari, Kaouther Messaoud Ben Amor, Éloi Zablocki, Matthieu
Cord, and Alexandre Alahi. Unitraj: A unified framework for scalable vehicle trajectory
prediction. In Proc. of the European Conf. on Computer Vision (ECCV), 2024.
[23] Common Crawl Foundation. Common crawl. https://commoncrawl.org, 2026.
[24] The Apache Software Foundation. Apache arrow. https://github.com/apache/arrow, 2026.
[25] Andreas Geiger, Philip Lenz, and Raquel Urtasun. Are we ready for autonomous driving?
The KITTI vision benchmark suite. In Proc. IEEE Conf. on Computer Vision and Pattern
Recognition (CVPR), 2012.
[26] Aaron Grattafiori, Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian,
Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Alex Vaughan, et al. The llama
3 herd of models. arXiv.org, 2024.
[27] Cole Gulino, Justin Fu, Wenjie Luo, George Tucker, Eli Bronstein, Yiren Lu, Jean Harb, Xinlei
Pan, Yan Wang, Xiangyu Chen, et al. Waymax: An accelerated, data-driven simulator for
large-scale autonomous driving research. Advances in Neural Information Processing Systems
(NeurIPS), 2023.
11


## Page 12

[28] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image
recognition. In Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR), 2016.
[29] John Houston, Guido Zuidhof, Luca Bergamini, Yawei Ye, Long Chen, Ashesh Jain, Sammy
Omari, Vladimir Iglovikov, and Peter Ondruska. One thousand and one hours: Self-driving
motion prediction dataset. In Proc. Conf. on Robot Learning (CoRL), 2021.
[30] Yihan Hu, Jiazhi Yang, Li Chen, Keyu Li, Chonghao Sima, Xizhou Zhu, Siqi Chai, Senyao Du,
Tianwei Lin, Wenhai Wang, et al. Planning-oriented autonomous driving. In Proc. IEEE Conf.
on Computer Vision and Pattern Recognition (CVPR), 2023.
[31] Open Geospatial Consortium Inc. Opengis® implementation standard for geographic informa-
tion - simple feature access - part 1: Common architecture. https://www.ogc.org/standards/sfa,
2011.
[32] International Organization for Standardization. ISO 8855:2011(en) Road vehicles — Vehicle
dynamics and road-holding ability — Vocabulary. https://www.iso.org/obp/ui/en/#iso:std:iso:
8855:, 2011.
[33] Boris Ivanovic, Guanyu Song, Igor Gilitschenski, and Marco Pavone. trajdata: A unified
interface to multiple human trajectory datasets. In Advances in Neural Information Processing
Systems (NIPS), 2023.
[34] Xiaosong Jia, Zhenjie Yang, Qifeng Li, Zhiyuan Zhang, and Junchi Yan. Bench2drive: Towards
multi-ability benchmarking of closed-loop end-to-end autonomous driving. Advances in Neural
Information Processing Systems (NeurIPS), 2024.
[35] Napat Karnchanachari, Dimitris Geromichalos, Kok Seang Tan, Nanxiang Li, Christopher
Eriksen, Shakiba Yaghoubi, Noushin Mehdipour, Gianmarco Bernasconi, Whye Kit Fong,
Yiluan Guo, et al. Towards learning-based planning: The nuplan benchmark for real-world
autonomous driving. In Proc. IEEE International Conf. on Robotics and Automation (ICRA),
2024.
[36] Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, George Drettakis, et al. 3d gaussian
splatting for real-time radiance field rendering. ACM Trans. Graph., 42(4):139–1, 2023.
[37] Zhaonian Kuang, Rui Ding, Haotian Wang, Xinhu Zheng, Meng Yang, and Gang Hua. Coin3d:
Revisiting configuration-invariant multi-camera 3d object detection. Proc. IEEE Conf. on
Computer Vision and Pattern Recognition (CVPR), 2026.
[38] Ted Lentsch, Santiago Montiel-Marín, Holger Caesar, and Dariu M Gavrila. Terraseg: Self-
supervised ground segmentation for any lidar. Proc. IEEE Conf. on Computer Vision and Pattern
Recognition (CVPR), 2026.
[39] Scott T Leutenegger, Mario A Lopez, and Jeffrey Edgington. Str: A simple and efficient
algorithm for r-tree packing. In Proceedings 13th international conference on data engineering,
pages 497–506. IEEE, 1997.
[40] Quentin Lhoest, Albert Villanova Del Moral, Yacine Jernite, Abhishek Thakur, Patrick
Von Platen, Suraj Patil, Julien Chaumond, Mariama Drame, Julien Plu, Lewis Tunstall, et al.
Datasets: A community library for natural language processing. In Conference on Empirical
Methods in Natural Language Processing (EMNLP), 2021.
[41] Quanyi Li, Zhenghao Mark Peng, Lan Feng, Zhizheng Liu, Chenda Duan, Wenjie Mo, and
Bolei Zhou. Scenarionet: Open-source platform for large-scale traffic scenario simulation and
modeling. Advances in Neural Information Processing Systems (NeurIPS), 2023.
[42] Tianyu Li, Yihang Qiu, Zhenhua Wu, Carl Lindström, Peng Su, Matthias Nießner, and Hongyang
Li. Mtgs: Multi-traversal gaussian splatting. arXiv.org, 2025.
[43] Yueyuan Li, Songan Zhang, Mingyang Jiang, Xingyuan Chen, Jing Yang, Yeqiang Qian,
Chunxiang Wang, and Ming Yang. Tactics2d: A highly modular and extensible simulator for
driving decision-making. IEEE Transactions on Intelligent Vehicles (T-IV), 2024.
12


## Page 13

[44] Zhiqi Li, Wenhai Wang, Hongyang Li, Enze Xie, Chonghao Sima, Tong Lu, Qiao Yu, and Jifeng
Dai. Bevformer: learning bird’s-eye-view representation from lidar-camera via spatiotemporal
transformers. Proc. of the European Conf. on Computer Vision (ECCV), 2022.
[45] Zhiqi Li, Zhiding Yu, Shiyi Lan, Jiahan Li, Jan Kautz, Tong Lu, and Jose M Alvarez. Is ego
status all you need for open-loop end-to-end autonomous driving? In Proc. IEEE Conf. on
Computer Vision and Pattern Recognition (CVPR), 2024.
[46] Yiyi Liao, Jun Xie, and Andreas Geiger. Kitti-360: A novel dataset and benchmarks for urban
scene understanding in 2d and 3d. IEEE Trans. on Pattern Analysis and Machine Intelligence
(PAMI), 2022.
[47] Haotong Lin, Sili Chen, Junhao Liew, Donny Y Chen, Zhenyu Li, Guang Shi, Jiashi Feng, and
Bingyi Kang. Depth anything 3: Recovering the visual space from any views. arXiv.org, 2025.
[48] Mingyu Liu, Ekim Yurtsever, Jonathan Fossaert, Xingcheng Zhou, Walter Zimmer, Yuning
Cui, Bare Luka Zagar, and Alois C Knoll. A survey on autonomous driving datasets: Statistics,
annotation quality, and a future outlook. IEEE Transactions on Intelligent Vehicles (T-IV), 2024.
[49] Yingfei Liu, Tiancai Wang, Xiangyu Zhang, and Jian Sun. Petr: Position embedding transfor-
mation for multi-view 3d object detection. In Proc. of the European Conf. on Computer Vision
(ECCV), 2022.
[50] Long Nguyen, Micha Fauth, Bernhard Jaeger, Daniel Dauner, Maximilian Igl, Andreas Geiger,
and Kashyap Chitta. Lead: Minimizing learner-expert asymmetry in end-to-end driving. Proc.
IEEE Conf. on Computer Vision and Pattern Recognition (CVPR), 2026.
[51] NVIDIA.
PhysicalAI-Autonomous-Vehicles.
https://huggingface.co/datasets/nvidia/
PhysicalAI-Autonomous-Vehicles, 2025. Hugging Face dataset.
[52] NVIDIA. NVIDIA DRIVE Hyperion: L4-Ready autonomous vehicle platform. https://www.
nvidia.com/en-us/solutions/autonomous-vehicles/drive-hyperion/, 2026. NVIDIA product page.
[53] NVIDIA. PhysicalAI-Autonomous-Vehicles-NCore. https://huggingface.co/datasets/nvidia/
PhysicalAI-Autonomous-Vehicles-NCore, 2026. Hugging Face dataset.
[54] Shiwei Ren, Tianci Wen, Yongchun Fang, and Biao Lu. Fastgs: Training 3d gaussian splatting
in 100 seconds. Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR), 2026.
[55] Chonghao Sima, Katrin Renz, Kashyap Chitta, Li Chen, Hanxue Zhang, Chengen Xie, Jens
Beißwenger, Ping Luo, Andreas Geiger, and Hongyang Li. Drivelm: Driving with graph visual
question answering. In Proc. of the European Conf. on Computer Vision (ECCV), 2024.
[56] Pei Sun, Henrik Kretzschmar, Xerxes Dotiwalla, Aurelien Chouard, Vijaysai Patnaik, Paul
Tsui, James Guo, Yin Zhou, Yuning Chai, Benjamin Caine, et al. Scalability in perception
for autonomous driving: Waymo open dataset. In Proc. IEEE Conf. on Computer Vision and
Pattern Recognition (CVPR), 2020.
[57] OpenPCDet Development Team. Openpcdet: An open-source toolbox for 3d object detection
from point clouds. https://github.com/open-mmlab/OpenPCDet, 2020.
[58] Adam Tonderski, Carl Lindström, Georg Hess, William Ljungbergh, Lennart Svensson, and
Christoffer Petersson. Neurad: Neural rendering for autonomous driving. In Proc. IEEE Conf.
on Computer Vision and Pattern Recognition (CVPR), 2024.
[59] Ignacio Vizzo, Tiziano Guadagnino, Benedikt Mersch, Louis Wiesmann, Jens Behley, and Cyrill
Stachniss. Kiss-icp: In defense of point-to-point icp–simple, accurate, and robust registration if
done the right way. IEEE Robotics and Automation Letters (RA-L), 8(2):1029–1036, 2023.
[60] Shuo Wang, Xinhai Zhao, Hai-Ming Xu, Zehui Chen, Dameng Yu, Jiahao Chang, Zhen Yang,
and Feng Zhao. Towards domain generalization for multi-view 3d object detection in bird-eye-
view. Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR), 2023.
13


## Page 14

[61] Yan Wang, Xiangyu Chen, Yurong You, Li Erran Li, Bharath Hariharan, Mark Campbell,
Kilian Q Weinberger, and Wei-Lun Chao. Train in germany, test in the usa: Making 3d object
detectors generalize. In Proc. IEEE Conf. on Computer Vision and Pattern Recognition (CVPR),
2020.
[62] Yan Wang, Wenjie Luo, Junjie Bai, Yulong Cao, Tong Che, Ke Chen, Yuxiao Chen, Jenna
Diamond, Yifan Ding, Wenhao Ding, et al. Alpamayo-r1: Bridging reasoning and action
prediction for generalizable autonomous driving in the long tail. arXiv.org, 2025.
[63] Waymo. Safe, routine, ready: Autonomous driving in five new cities. https://waymo.com/blog/
2025/11/safe-routine-ready-autonomous-driving-in-new-cities/, 2025. Waymo blog post.
[64] Waymo. Beginning fully autonomous operations with the 6th-generation Waymo driver. https:
//waymo.com/blog/2026/02/ro-on-6th-gen-waymo-driver/, 2026. Waymo blog post.
[65] Wayve. Crossing the pond and beyond: Generalizable AI driving for global deployment.
https://wayve.ai/thinking/multi-country-generalization/, 2025. Wayve blog post.
[66] Benjamin Wilson, William Qi, Tanmay Agarwal, John Lambert, Jagjeet Singh, Siddhesh
Khandelwal, Bowen Pan, Ratnesh Kumar, Andrew Hartnett, Jhony Kaesemodel Pontes, et al.
Argoverse 2: Next generation datasets for self-driving perception and forecasting. Advances in
Neural Information Processing Systems (NeurIPS), 2021.
[67] Pengchuan Xiao, Zhenlei Shao, Steven Hao, Zishuo Zhang, Xiaolin Chai, Judy Jiao, Zesong Li,
Jian Wu, Kai Sun, Kun Jiang, et al. Pandaset: Advanced sensor suite dataset for autonomous
driving. In Proc. IEEE Conf. on Intelligent Transportation Systems (ITSC). IEEE, 2021.
[68] Runsheng Xu, Hubert Lin, Wonseok Jeon, Hao Feng, Yuliang Zou, Liting Sun, John Gorman,
Ekaterina Tolstaya, Sarah Tang, Brandyn White, et al. Wod-e2e: Waymo open dataset for
end-to-end driving in challenging long-tail scenarios. arXiv.org, 2025.
[69] Xintao Yan, Erdao Liang, Jiawei Wang, Haojie Zhu, and Henry X Liu. Improving traffic signal
data quality for the waymo open motion dataset. Transportation Research Part C: Emerging
Technologies, 183:105476, 2026.
[70] An Yang, Baosong Yang, Beichen Zhang, Binyuan Hui, Bo Zheng, Bowen Yu, Chengyuan Li,
Dayiheng Liu, Fei Huang, Haoran Wei, Huan Lin, Jian Yang, Jianhong Tu, et al. Qwen2.5
technical report. arXiv.org, 2024.
[71] Brent Yi, Chung Min Kim, Justin Kerr, Gina Wu, Rebecca Feng, Anthony Zhang, Jonas
Kulhanek, Hongsuk Choi, Yi Ma, Matthew Tancik, et al. Viser: Imperative, web-based 3d
visualization in python. arXiv.org, 2025.
[72] Xiangyun Zhao, Samuel Schulter, Gaurav Sharma, Yi-Hsuan Tsai, Manmohan Chandraker, and
Ying Wu. Object detection with a unified label space from multiple datasets. In Proc. of the
European Conf. on Computer Vision (ECCV), 2020.
[73] Xingyi Zhou, Vladlen Koltun, and Philipp Krähenbühl. Simple multi-dataset detection. In Proc.
IEEE Conf. on Computer Vision and Pattern Recognition (CVPR), 2022.
14

