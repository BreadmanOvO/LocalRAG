# AB3DMOT: A Baseline for 3D Multi-Object Tracking and New Evaluation Metrics

**Source**: arXiv:2008.08063

**Type**: Academic Paper

---

## Page 1

AB3DMOT: A Baseline for 3D Multi-Object
Tracking and New Evaluation Metrics
Xinshuo Weng, Jianren Wang, David Held, and Kris Kitani
Robotics Institute, Carnegie Mellon University, Pittsburgh, USA
{xinshuow, jianrenw, dheld, kkitani}@cs.cmu.edu
Abstract. 3D multi-object tracking (MOT) is essential to applications
such as autonomous driving. Recent work focuses on developing accurate
systems giving less attention to computational cost and system com-
plexity. In contrast, this work proposes a simple real-time 3D MOT sys-
tem with strong performance. Our system ﬁrst obtains 3D detections
from a LiDAR point cloud. Then, a straightforward combination of a
3D Kalman ﬁlter and the Hungarian algorithm is used for state esti-
mation and data association. Additionally, 3D MOT datasets such as
KITTI evaluate MOT methods in 2D space and standardized 3D MOT
evaluation tools are missing for a fair comparison of 3D MOT methods.
We propose a new 3D MOT evaluation tool along with three new met-
rics to comprehensively evaluate 3D MOT methods. We show that, our
proposed method achieves strong 3D MOT performance on KITTI and
runs at a rate of 207.4 FPS on the KITTI dataset, achieving the fastest
speed among modern 3D MOT systems. Our code is publicly available
at http://www.xinshuoweng.com/projects/AB3DMOT.
Keywords: multi-object tracking, evaluation metrics
1
Introduction
MOT is essential to applications such as autonomous driving [6]. Due to ad-
vancements in detection, there has been much progress on MOT. For example,
for the car class on the KITTI [2] 2D MOT benchmark as shown in Fig. 1 (Left),
the MOTA (multi-object tracking accuracy) has improved from 57.03 to 84.04
in just two years. While we are encouraged by the progress, we observe that our
focus on innovation and accuracy may have come at the cost of important practi-
cal factors such as computational eﬃciency and system simplicity, and S.O.T.A.
methods typically require a large computational cost [8,1,7] making real-time
performance a challenge. Also, modern MOT systems are often complex and it
is not always clear which part of the system contributes the most to performance.
2
AB3DMOT: A Baseline for 3D MOT
To provide a standard 3D MOT baseline for comparative analysis, we imple-
ment a classical approach which is both eﬃcient and simple in design – the
Kalman ﬁlter [3] (1960) coupled with the Hungarian method [5] (1955). Speciﬁ-
cally, our system is shown in Fig. 1 (Right), which employs an oﬀ-the-shelf 3D
object detector to obtain 3D detections from the LiDAR point cloud [4]. Then,
a combination of the 3D Kalman ﬁlter (with a constant velocity model) and the
Hungarian algorithm is used for state estimation and data association. Unlike
arXiv:2008.08063v1  [cs.CV]  18 Aug 2020


## Page 2

2
X. Weng et al.
Proposed
Real-time
3D Object 
Detection
3D 
Kalman 
Filter
Tt-1
Dt
Data Association
(Hungarian 
algorithm)
prediction
Tunmatch
Dunmatch
Dmatch / Tmatch
Birth and 
Death
Memory
update
Test
Tt
Tnew/Tlost
Associated
Trajectories
LiDAR Point Cloud
Fig. 1. Left: MOTA of modern MOT systems on KITTI 2D MOT leaderboard. The
higher and more right is better. Right: Proposed system pipeline.
other ﬁlter-based MOT systems which deﬁne the state space of the ﬁlter in the
image plane [9], we extend the state space of the objects to 3D, including 3D
location, 3D size, 3D velocity and orientation.
Our empirical results are alarming. While the combination of modules in our
system is straightforward, we achieve strong 3D MOT performance on the KITTI
dataset. Surprisingly, although our system does not use any 2D data as input,
we also achieve competitive performance on the KITTI 2D MOT leaderboard
in Fig. 1 (Left) by projecting our 3D MOT results onto the image plane for
evaluation. We hypothesize that the strong 2D MOT performance of our 3D
MOT system may be due to the fact that tracking in 3D can better resolve
depth ambiguities and lead to fewer mismatches than tracking in 2D. Also, due
to eﬃcient design of our system, it runs at a rate of 207.4 FPS on the KITTI
dataset, achieving the fastest speed among modern 3D MOT systems. To be
clear, the contribution of this work is not to innovate 3D MOT algorithms but
to provide a more clear picture of modern 3D MOT systems in comparison to a
most basic yet strong baseline, we believe the results of which are important to
share across the community.
3
New 3D MOT Evaluation Tool
We observed one issue for current 3D MOT evaluation: Standard MOT bench-
marks such as the KITTI dataset only support 2D MOT evaluation, i.e., evalu-
ation on the image plane. A tool to evaluate 3D MOT systems directly in 3D
space is not currently available. On the KITTI dataset, the current convention
of evaluating 3D MOT methods is to project the 3D tracking results to the 2D
image plane and then use the KITTI 2D MOT evaluation tool. However, we be-
lieve that this will hamper the future progress of 3D MOT systems as evaluating
on the image plane cannot demonstrate full strength of 3D MOT methods.
To better evaluate 3D MOT systems, we implement an extension to the
KITTI 2D MOT evaluation tool for 3D MOT evaluation. Speciﬁcally, we modify
the cost function from 2D IoU to 3D IoU and match the 3D MOT results with
3D ground truth trajectories directly in the 3D space. In this way, we no longer
need to project 3D MOT results to the image plane for evaluation. For every
tracked object, a minimum 3D IoU (we use 0.25 in our experiments) with the
ground truth is required to be considered as a successful match. Although our
3D MOT evaluation tool is a straightforward extension to is 2D counterpart, we
hope that it can serve as a standard to evaluate future 3D MOT systems.


## Page 3

AB3DMOT: A Baseline for 3D Multi-Object Tracking
3
Table 1. Performance on KITTI val set using the proposed 3D MOT evaluation tool.
Method
Input Data
sAMOTA↑
AMOTA↑
AMOTP↑
MOTA↑
MOTP↑
IDS↓
FRAG↓
FPS↑
mmMOT [10]
2D + 3D
70.61
33.08
72.45
74.07
78.16
10
125
4.8
FANTrack [1]
2D + 3D
82.97
40.03
75.01
74.30
75.24
35
202
25.0
Ours
3D
93.28
45.43
77.41
86.24
78.43
0
15 207.4
Frame 13 (Ours)
Frame 28 (Ours)
Frame 43 (Ours)
Fig. 2. Qualitative results of our system on the sequence 3 of the KITTI test set.
4
New MOT Evaluation Metrics
Another issue we observed is that: Common MOT metrics such as MOTA and
MOTP do not consider the conﬁdence of tracked objects. As a result, users must
manually select a conﬁdence threshold and ﬁlter out tracked objects with con-
ﬁdence lower than the threshold before evaluation. However, selecting the best
threshold is non-trivial and the conﬁdence threshold can be signiﬁcantly diﬀerent
if using a diﬀerent detector or evaluated on a diﬀerent dataset. More importantly,
using a single conﬁdence threshold for evaluation prevents us from understanding
the full spectrum of accuracy of a MOT system. One consequence is that a MOT
system achieving high MOTA at a single threshold can still have extremely low
MOTA at other thresholds, but still be ranked high on the leaderboard. Ideally,
we should aim to develop MOT systems that can achieve high MOTA across a
large set of thresholds, i.e., robust to the conﬁdence score.
To deal with the issue that current MOT evaluation metrics do not consider
the conﬁdence score and only evaluate at a single threshold, we propose three
integral metrics – sAMOTA, AMOTA and AMOTP (scaled average MOTA,
average MOTA and MOTP) – to summarize the performance of MOTA and
MOTP across diﬀerent thresholds. Speciﬁcally, the integral metrics AMOTA
and AMOTP are computed by integrating the MOTA and MOTP over all recall
values. Similar to other integral metrics such as the average precision used in
object detection, we approximate the integration with a summation over a dis-
crete set (40) of recall values. Then, the sAMOTA matrix is proposed to adjust
the range of the AMOTA value between 0% and 100%.
5
Experiments
Dataset and Evaluation. We evaluate on the KITTI 3D MOT dataset, which
provides LiDAR point cloud and ground truth 3D bounding box trajectories. As
the KITTI test set only supports 2D MOT evaluation and its ground truth is
not released to users, we have to use the KITTI val set for 3D MOT evaluation.
Following prior work, we evaluate on the car subset of the KITTI dataset for
comparison. In addition to the proposed three integral metrics, we also evaluate
on the standard MOT metrics including MOTA, MOTP, IDS, FRAG, FPS.
Baselines. We compare against recent open-sourced 3D MOT systems such as
FANTrack [1] and mmMOT [10]. We use the same 3D detections obtained by
PointRCNN [4] on KITTI for our proposed method and baselines [1,10] that re-


## Page 4

4
X. Weng et al.
quire 3D detections as inputs. For baselines [1,10] that require the 2D detections
as inputs, we use the 2D projection of 3D detections.
Results. We show the results of baselines and our proposed system in Table 1.
Evaluation is conducted in 3D space using the proposed 3D MOT evaluation tool
with new metrics. Our 3D MOT system consistently outperforms other modern
3D MOT systems in all metrics, establishing strong performance on KITTI 3D
MOT and achieving an impressive zero identity switch. We show qualitative
results of our 3D MOT system in Fig. 2. The 3D tracking results are visualized
on the image with colored 3D bounding boxes where the color represents the
object identity. We can see that our system can reliably track objects in the 3D
space on the example sequence.
Inference Time. We show comparison of inference time in last column of Table
1. Our 3D MOT baseline system (excluding the 3D detector part) runs at a rate
of 207.4 FPS on the KITTI val set without the need of GPU, achieving the
fastest speed among modern 3D MOT systems.
6
Conclusion
We proposed an accurate, simple and real-time baseline system for online 3D
MOT. Also, a new 3D MOT evaluation tool along with a set of new metrics
was proposed for standardized 3D MOT evaluation in the future. Through ex-
periments on KITTI 3D MOT benchmark, our system established strong 3D
MOT performance while achieving the fastest speed. We hope that our system
with released code will serve as a solid baseline on which others can easily build
to advance the state-of-the-art in 3D MOT. Also, we hope that our released
evaluation tool will serve as a standard in future 3D MOT benchmarks.
References
1. Baser, E., Balasubramanian, V., Bhattacharyya, P., Czarnecki, K.: FANTrack: 3D
Multi-Object Tracking with Feature Association Network. IV (2020)
2. Geiger, A., Lenz, P., Urtasun, R.: Are We Ready for Autonomous Driving? the
KITTI Vision Benchmark Suite. CVPR (2012)
3. Kalman, R.: A New Approach to Linear Filtering and Prediction Problems. Journal
of Basic Engineering (1960)
4. Shi, S., Wang, X., Li, H.: PointRCNN: 3D Object Proposal Generation and De-
tection from Point Cloud. CVPR (2019)
5. W Kuhn, H.: The Hungarian Method for the Assignment Problem. Naval Research
Logistics Quarterly (1955)
6. Wang, S., Jia, D., Weng, X.: Deep Reinforcement Learning for Autonomous Driv-
ing. arXiv:1811.11329 (2018)
7. Weng, X., Wang, Y., Man, Y., Kitani, K.: GNN3DMOT: Graph Neural Network
for 3D Multi-Object Tracking with 2D-3D Multi-Feature Learning. CVPR (2020)
8. Weng, X., Yuan, Y., Kitani, K.: Joint 3D Tracking and Forecasting with Graph
Neural Network and Diversity Sampling. arXiv:2003.07847 (2020)
9. Wojke, N., Bewley, A., Paulus, D.: Simple Online and Realtime Tracking with a
Deep Association Metric. ICIP (2017)
10. Zhang, W., Zhou, H., Sun, S., Wang, Z., Shi, J., Loy, C.C.: Robust Multi-Modality
Multi-Object Tracking. ICCV (2019)

