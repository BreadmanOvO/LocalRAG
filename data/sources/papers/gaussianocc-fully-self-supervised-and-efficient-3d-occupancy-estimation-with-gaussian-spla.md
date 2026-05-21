# GaussianOcc: Fully Self-supervised and Efficient 3D Occupancy Estimation with Gaussian Splatting

**Source**: arXiv:2408.11447

**Type**: Academic Paper

---

## Page 1

GaussianOcc: Fully Self-supervised and Efficient 3D Occupancy Estimation with
Gaussian Splatting
Wanshui Gan 1,2,∗
Fang Liu 1,∗
Hongbin Xu 3
Ningkai Mo 4
Naoto Yokoya 1,2,†
1The University of Tokyo,2 RIKEN, 3South China University of Technology
4Shenzhen Institute of Advanced Technology, Chinese Academy of Sciences
∗Equal contribution, † Corresponding author
{wanshuigan, fangliu2896, hongbinxu1013, nk.mo19941001}@gmail.com
yokoya@k.u-tokyo.ac.jp
Abstract
We introduce GaussianOcc, a systematic method that in-
vestigates Gaussian splatting for fully self-supervised and
efficient 3D occupancy estimation in surround views. First,
traditional methods for self-supervised 3D occupancy es-
timation still require ground truth 6D ego pose from sen-
sors during training. To address this limitation, we propose
Gaussian Splatting for Projection (GSP) module to provide
accurate scale information for fully self-supervised train-
ing from adjacent view projection. Additionally, existing
methods rely on volume rendering for final 3D voxel rep-
resentation learning using 2D signals (depth maps and se-
mantic maps), which is time-consuming and less effective.
We propose Gaussian Splatting from Voxel space (GSV) to
leverage the fast rendering properties of Gaussian splat-
ting. As a result, the proposed GaussianOcc method en-
ables fully self-supervised (no ground truth ego pose) 3D
occupancy estimation in competitive performance with low
computational cost (2.7 times faster in training and 5 times
faster in rendering).
The relevant code is available in
https://github.com/GANWANSHUI/GaussianOcc.git.
1. Introduction
Surround view 3D occupancy estimation [31, 34, 39, 45,
48, 51, 56] has emerged as a core perception task and a
promising alternative to bird’s-eye view (BEV) methods
[9, 28, 29]. To facilitate 3D occupancy estimation, several
benchmarks have been developed for supervised training
[41–43, 45], though these require substantial effort in 3D
annotation. To reduce the burden of 3D annotation, self-
supervised [5, 11, 16, 22, 54] and weakly-supervised [37]
learning approaches based on volume rendering have been
Figure 1. Problem setting of GaussianOcc. Given a surround
image sequence, the spatial camera extrinsic and its correspond-
ing 2D semantic annotation, GaussianOcc is able to perform 3D
occupancy estimation without the need for ground truth occupancy
label and ground truth 6D ego pose for training.
proposed [10, 35, 46]. Volume rendering allows 3D rep-
resentation learning using 2D supervision signals, such as
2D semantic maps and depth maps, thereby eliminating the
need for extensive 3D annotation.
Existing methods [22, 54] achieve self-supervised learn-
ing through volume rendering, where the 2D semantic map
supervision is derived from open-vocabulary semantic seg-
mentation [55], and the depth map supervision is obtained
arXiv:2408.11447v4  [cs.CV]  14 Jul 2025


## Page 2

from self-supervised depth estimation [11, 12]. However,
these approaches face two significant limitations. First, vol-
ume rendering is performed at real-world scale, which re-
quires the ground truth 6D ego pose to calculate the multi-
view photometric loss across sequential images. Second,
the inefficiency in volume rendering poses a challenge, the
same as in novel view synthesis tasks [1, 17, 26], due to
the dense sampling operation required. These limitations
impede the development of a more general and efficient
paradigm for self-supervised 3D occupancy estimation.
To address the aforementioned limitations, we propose
a fully self-supervised and efficient approach to 3D occu-
pancy estimation with dedicated designs based on Gaus-
sian splatting [1, 26]. Specifically, we introduce the use of
Gaussian splatting to perform cross-view splatting, where
the rendered image constructs a cross-view loss that pro-
vides scale information during joint training with the 6D
pose network. This eliminates the need for ground truth
6D ego pose during training. To improve rendering effi-
ciency, we move away from the dense sampling required in
traditional volume rendering. Instead, we propose perform-
ing Gaussian splatting directly from the 3D voxel space.
In this approach, each vertex in the voxel grid is treated
as a 3D Gaussian, and we optimize the attributes of these
Gaussians—such as semantic and opacity—directly within
the voxel space. Through the above innovative approach,
our proposed method makes progress toward fully self-
supervised and efficient 3D occupancy estimation, as out-
lined in Figure 1.
In summary, our core contributions are as follows:
• We introduce the first fully self-supervised method for ef-
ficient surrounding-view 3D occupancy estimation, fea-
turing the exploration of Gaussian splatting.
• We propose Gaussian splatting for cross-view projection
module, which can provide scale information to get rid of
the need of ground truth 6D ego pose during the training.
• We propose Gaussian splatting from voxel space module,
achieving competitive performance with 2.7 times faster
training and 5 times faster rendering compared to the pre-
vious works with volume rendering.
2. Related work
2.1. Surround view depth estimation
The surround view setting offers an ego-centric 360-degree
perception solution [3, 13, 34, 39].
[15] introduces the
surround view benchmark in the supervised setting, which
learns the depth scale directly from the ground truth depth
map. FSM [14] is a pioneering work in scale-aware sur-
round view depth estimation relying on stereo constraint
[53]. However, subsequent studies [27, 44] have found that
reproducing the performance of [14] is challenging. Sur-
rounddepth [44] improves the scale supervision signal us-
ing sparse point clouds from Structure-from-Motion (SFM).
Building on the spatial and temporal constraints in FSM,
[27] introduces a volume feature fusion module to enhance
performance.
For better performance, [38] proposes the
temporal offline refinement strategy based on the multiple
cameras and monocular depth refinement.
These works
[14, 27, 38, 44] all use traditional projection and index in-
terpolation for cross-view synthesis, computing the loss be-
tween the synthesized view and target images. Compared to
the traditional projection, our approach employs Gaussian
splatting with a dedicated design for cross-view constraint,
achieving better performance.
2.2. Surround view 3D occupancy estimation
Surround view 3D occupancy estimation has gained sig-
nificant attention in recent years, with several benchmarks
based on the nuScenes dataset [41, 43, 45]. In addition to
the advanced architectures being proposed [30, 31, 51, 57],
another research trend involves utilizing volume rendering
for 3D occupancy learning with 2D supervision [11, 22,
37, 54]. SimpleOcc [11] pioneered the use of volume ren-
dering for 3D occupancy estimation, exploring both super-
vised and self-supervised learning. RenderOcc [37] extends
semantic information for rendering.
OccNeRF [54] and
SelfOcc [22] share a similar approach by using 2D open-
vocabulary semantic models to generate semantic maps for
supervision. However, since volume rendering processes
are conducted at real-world scale, these self-supervised
methods [11, 22, 54] require ground truth 6D poses from
sensors to provide the real-world scale for training. Dif-
ferently, we are exploring a solution that utilizes the over-
lap region in adjacent cameras to learn the real-world scale,
eliminating the need for ground truth 6D poses.
2.3. 3D Gaussian splatting
3D Gaussian splatting has become a popular method for
modeling 3D and 4D scenes using well-posed images [8, 25,
26, 47], which has the property of fast rendering compared
to the volume rendering in neural radiance field [10, 17, 35].
In driving scenes, a line of research has focused on scene-
specific reconstruction [20, 49, 59]. Our work, however,
investigates the function of Gaussian splatting in a general-
ized setting, where existing methods generally construct 3D
Gaussians from the unprojection of learned 2D Gaussian at-
tributes [7, 32, 40, 58]. We also employ this unprojection
approach, but uniquely, our approach constructs cross-view
information from adjacent views to learn scale information
through Gaussian splatting projection. In addition, we in-
vestigate the Gaussian splatting on the voxel space for faster
rendering compared with the previous volume rendering-
based works [11, 22, 54].
Note that, recent works, GaussianFormer [23], GaussTR
[24] and GaussianBeV [6], are related to ours in their focus


## Page 3

Figure 2. GaussianOcc is a two-stage method. In Stage 1, we train a scale-aware 6D pose network, using a U-Net architecture to predict
Gaussian attributes in the 2D image grid space for cross-view Gaussian splatting. This approach provides scale information in the joint
training with the 6D pose net. Based on the 6D pose from Stage 1, we perform self-supervised 3D occupancy estimation in Stage 2, where
we lift the 2D features to a 3D voxel space and propose voxel grid Gaussian splatting for fast rendering. Note that, for clarity, we omit the
line from the 6D pose network to the loss in Stage 1, and the 2D encoder is independent for each stage (not shared).
on 3D occupancy estimation and BEV prediction. However,
our exploration diverges by focusing on two new properties
that Gaussian splatting can contribute to occupancy estima-
tion: scale-aware training and faster rendering.
3. Method
3.1. Preliminaries
3D Gaussian splatting [26] is for modeling static 3D scenes
using point primitives, where each primitive is character-
ized with the following attributes: (1) a 3D position X ∈
R3, (2) a color defined by SH coefficients c ∈Rk (where
k denotes the dimensionality of the SH basis), (3) a rota-
tion represented by a quaternion r ∈R4, (4) a scaling fac-
tor s ∈R3
+, and (5) an opacity α ∈[0, 1]. The original
Gaussian splatting is for scene-specific, fast 3D novel view
synthesis, where the attributes of Gaussian points are opti-
mized by the multi-view constraint. Differently, we study
fully self-supervised and efficient 3D occupancy estimation
by exploring the Gaussian attributes that are well-aligned in
both 2D and 3D grids. Our design allows us to benefit from
the Gaussian splatting rendering for the scale-aware train-
ing by cross-view constraint and faster rendering on voxel
grids, as illustrated in Figure 2.
3.2. Scale-aware training by Gaussian Splatting
Scale from spatial camera rig: Similar to the previous
work [14, 27, 44], the scale information is from the sur-
round camera rig. Specifically, the real-world scale can be
obtained by leveraging camera extrinsic matrices, which is
to use spatial photometric loss in the overlap region between
two adjacent views, i.e., warping Ii
t to Ij
t :
  p^
{
i  \ri ghtar row
 j}_t = K
^{j} (T^{j})^{-1} T^{i} D_t^{i} (K^{i})^{-1} p^{i}_t, 
(1)
where Ki, T i are the intrinsic and extrinsic matrices of i-th
camera, Di
t is the predicted depth map of i-th camera, pt is
the corresponding pixel during the warping. The warping
operation is achieved by direct bilinear interpolation with
the corresponding pi→j
t
. However, as pointed out by [44],
the mapping in such a small overlap region, pi→j
t
, can easily
go into sub-optimal depth result, where we verify this in the
experiment section in Figure 5. Therefore, apart from the
spatial loss, [44] proposes to facilitate the Structure-from-
Motion (SFM) to extract sparse depth information for direct
depth supervision to provide a stronger supervision signal,
but it is time-consuming and not straightforward. Different
from [44], [27] enhances the depth estimation performance
with spatio-temporal context that does not need the sparse
depth from SFM but the performance is still limited. In-
spired by the explicit sparse depth supervision in [44], we
ask whether we can enforce the cross-view constraint on
adjacent views more explicitly. The answer is yes. We find


## Page 4

that the nature of Gaussian splatting is scale-aware projec-
tion that could serve for the cross-view stereo constraint.
We propose Gaussian splatting for projection in stage 1 for
better scale-aware training as follows.
Gaussian Splatting for Projection (GSP): As illustrated in
Figure 2, we adapt a depth network [52] to predict the Gaus-
sian attributes in 2D grid space, where, apart from the orig-
inal depth map, we also predict the scale map and rotation
map. For each adjacent view, we first calculate the mask
in the overlap region, then mask out one side of these over-
lap regions. Due to the presence of the other side’s overlap
region, the unprojected 3D scene remains complete if the
depth map is predicted well. This mask-out step is criti-
cal for providing scale training, as indicated in the experi-
ment section (Table 3). We then perform splatting rendering
on the adjacent views to obtain the rendered image. If the
depth map is accurately learned, the rendered image should
resemble the original images, providing the necessary scale
information for the joint training with 6D pose net.
Overlap Mask: The process of acquiring the overlap mask
is illustrated in Figure 3. We densely sample points along
the ray in one view, and a pixel is considered part of the
overlap region if more than one sampled 3D point falls
within the adjacent view.
The overlap mask is only de-
termined by the camera’s extrinsic and defined max depth
(e.g., 80m in nuScenes). Note that in the DDAD dataset
[13], we exclude regions with self-occlusion (such as parts
of the vehicle body). Besides, we apply the erosion opera-
tion from OpenCV [2] to the mask for purification.
3.3. Fast rendering by Gaussian Splatting
Inefficient performance in volume rendering: For 2D
supervision (semantic and depth maps), previous methods
[11, 22, 37, 54] employed volume rendering based on dense
sampling. Although the final 3D voxel representation for
modeling the 3D scene is much quicker than the original im-
plicit representation [35], it remains time-consuming, par-
ticularly when incorporating semantic map rendering. For
example, in OccNeRF [54], the number of sampled points
at a resolution of 180 × 320 is 108,735,066. However, the
target optimized points correspond to the vertices in the 3D
voxel grid, totaling 300 × 300 × 24 = 2, 160, 000. This
redundancy in densely sampled points helps optimization
with volume rendering but is highly inefficient.
Gaussian Splatting from Voxel (GSV): As analyzed
above, the target optimized points are the vertices in the
3D voxel grid, prompting us to consider directly optimiz-
ing these vertices. Interestingly, we find that it is suitable
to use the Gaussian splatting to replace the volume render-
ing if we regard the vertices of each the voxel grid as the
position of the 3D Gaussian. Then, we can optimize the at-
tributes of the 3D Gaussian, such as semantic and opacity
information. For example, in the empty space of voxel, even
Figure 3. Overlap mask in nuScenes [3] and DDAD [13].
though we have the vertices at that region during the splat-
ting rendering, after the optimization, the network would
predict the opacity as zero at these vertices then these ver-
tices would not contribute any geometry or semantic infor-
mation during the rendering. Since all vertices are arranged
in 3D voxel space with real-world 3D position X, we can
use fixed scale s and fixed rotation r for each vertex for
simplification. This allows us to model the 3D scene by op-
timizing the rest Gaussian attributes (semantic and opacity).
3.4. Loss function
We formulate the loss function of each stage as follows:
  \labe l  {total l o ss} \mathcal {L}_{stage 1}=\mathcal {L}_{temporal} + \mathcal {L}_{cross}, 
(2)
  \math c al {L}_{s t age 2}=\mathcal {L}_{temporal} + \lambda \mathcal {L}_{semantic}, 
(3)
  (\mathcal  {L}_{t e
m p oral
}
, \ mat
h
c
a l
 {L}_ { cro
ss} )= \frac {1-\operatorname {SSIM}\left (I_t, \hat {I}_t\right )}{2}+ \beta \left \|I_t-\hat {I}_t\right \|, 
(4)
where I_t and \protect \hat  {I}_t refer to the target image and the corre-
sponding synthesized image, respectively. Note that \protect \hat  {I}_t in
the temporal-view photometric loss \protect \mathcal  {L}_{temporal} is generated
by projecting pixels from the source image using the coor-
dinate index. In contrast, \protect \hat  {I}_t in the cross-view photometric
loss \protect \mathcal  {L}_{cross} is derived from our proposed cross-view Gaus-
sian splatting method. \protect \mathcal  {L}_{semantic} is 2D semantic loss with
balanced weight λ = 0.02. For \protect \mathcal  {L}_{cross} and \protect \mathcal  {L}_{temporal}, we
set \beta is set to 0.15 for weight balance the same as [54].
4. Experiment
4.1. Tasks, datasets, and metric
nuScenes [3]: For 3D occupancy estimation, we utilize an-
notations from Occ3D [41]. For fair comparison, we use


## Page 5

Method
GT Occ.
GT Pose
mIoU*
mIoU
MonoScene [4]
✓
×
6.33
6.06
BEVDet [19]
✓
×
20.03
19.38
BEVFormer [29]
✓
×
24.64
23.67
OccFormer [57]
✓
×
22.39
21.93
TPVFormer [21]
✓
×
28.69
27.83
CTF-Occ [41]
✓
×
29.54
28.53
RenderOcc [37]
×
×
24.53
23.93
SimpleOcc [11]
×
✓
7.99
7.05
SelfOcc [22]
×
✓
10.54
9.30
OccNeRF [54]
×
✓
10.81
9.54
GaussianOcc
×
×
11.26
9.94
Table 1. 3D occupancy comparison on the Occ3D dataset with
mIoU metric. Since ‘other’ and ‘other flat’ classes are the invalid
prompts for open-vocabulary models, we also calculate ‘mIoU*’
as the result ignoring the classes that do not consider these two
classes during evaluation, while ‘mIoU’ is the original result. GT
Occ. means using the ground truth occupancy label for supervi-
sion. GT Pose is the ground truth 6D ego pose from the sensor for
self-supervised geometry learning.
the 2D pseudo semantic map provided by OccNeRF [54]
for training.
We measure 3D occupancy estimation per-
formance using the mean Intersection over Union (mIoU)
metric. For depth estimation, we set the perception range
in [-80m, -80m, -1m, 80m, 80m, 6m], while we clamp
the ground truth to a range of 0.1m to 80m for evaluation,
consistent with OccNeRF and SurroundDepth [44].
We
evaluate depth maps using error metrics (Abs Rel, Sq Rel,
RMSE, RMSE log) and threshold accuracy metrics (δ).
DDAD [13]: Though we do not have the 3D occupancy
labels on DDAD dataset, we can present qualitative results
thanks to our fully self-supervised 3D occupancy estimation
setting. We obtain the 2D pseudo semantic labels for train-
ing following OccNeRF pipeline in nuScenes dataset. For
depth estimation, we clamp the depth range within 0.1m and
200m for evaluation, consistent with SurroundDepth [44].
4.2. Implementation details
Network details: For U-Net architecture, we adapt New-
CRFs [52] to predict the Gaussian attributes, which is based
on the Swin Transformer [33]. The 6D pose net is the same
as that used in SurroundDepth [44]. For the 2D-to-3D lift-
ing, we follow the approach used in SimpleOcc [11]. In the
depth estimation benchmark, we use the network proposed
by SimpleOcc, where the final output size is 256×256×16.
In our Gaussian splatting setting, we further upsample the
final output to 512×512×32 for improved performance since
we observe that a finer voxel grid leads to a finer rendered
depth map, which requires ignorable computational cost.
For occupancy estimation, we use the same network as Oc-
cNeRF [54] to ensure a fair comparison.
Training details: We propose a two-stage training for fully
self-supervised 3D occupancy estimation as indicated in
Figure 2. In stage 1, we jointly train the depth estimation
network and the 6D pose net, where we train the models
for 8 epochs on the nuScenes and 12 epochs on the DDAD.
In stage 2, we train the 3D occupancy network in a self-
supervised manner with the 6D pose predicted from stage
1 rather than the ground truth pose used in OccNeRF [54].
We train the models for 12 epochs on both the nuScenes and
DDAD. The optimizer and learning rate adjustment strategy
follow those used in SimpleOcc [11] and OccNeRF [54].
4.3. Main results
3D occupancy estimation in nuScenes: In Table 1, the
proposed GaussianOcc achieves the best performance com-
pared to other self-supervised methods. In particular, we do
not require ground truth occupancy labels and ground truth
6D ego pose for training, thanks to the predicted 6D pose
from the stage 1. Note that RenderOcc [37] does not re-
quire the 3D occupancy label, but it is not a self-supervised
method since it uses the ground truth depth map and se-
mantic map for the 2D supervision; it could be regarded as
a weakly-supervised method. In addition, we also achieve
the best result on the RayIoU metric [31], with further de-
tails provided in the supplementary material.
3D occupancy estimation in DDAD: To the best of our
knowledge, our work is the first to achieve 3D occu-
pancy estimation on this dataset, thanks to our fully self-
supervised learning setting. We present visualization results
in Figure 4. As highlighted by the red rectangle, the sky re-
gion has a short-range depth value, but this does not appear
in the rendered 3D occupancy estimation map thanks to the
parameterized coordinate design of OccNeRF [54].
Depth estimation: We present a comparison of depth esti-
mation results in Table 2 for both the nuScenes and DDAD.
In stage 1, GaussianOcc ‡ achieves top performance on the
nuScenes dataset and delivers competitive results on the
DDAD. It is important to note that methods such as Sur-
roundDepth [44] and SA-FSM [50] rely on third-party mod-
ule for the sparse depth supervision. Additionally, SA-FSM
is preprint work and has not released the code. R3D3 [38]
is a temporal offline refinement method that requires multi-
frame optimization, as discussed in [22]. In stage 2, which
involves depth estimation from rendering, our method also
achieves competitive results compared to those trained with
ground truth poses. Besides, we observe that the rendered
depth in stage two outperforms the depth results from stage
1 on the nuScenes, whereas the opposite is true for the
DDAD. This discrepancy might be attributed to differences
in perception range—80 meters in nuScenes versus 200 me-
ters in DDAD. Moreover, an interesting phenomenon is that
the semantic information is helpful for the depth estimation


## Page 6

Method
GT pose
Occ.
Abs Rel
Sq Rel
RMSE
RMSE log
δ < 1.25
δ < 1.252
δ < 1.253
nuScenes [3]
FSM [14]
×
×
0.297
-
-
-
-
-
-
FSM* [14]
×
×
0.319
7.534
7.860
0.362
0.716
0.874
0.931
SurroundDepth [44]
×
×
0.280
4.401
7.467
0.364
0.661
0.844
0.917
SA-FSM [50]
×
×
0.272
4.706
7.391
0.355
0.689
0.868
0.929
VFF [27]
×
×
0.289
5.718
7.551
0.348
0.709
0.876
0.932
R3D3 [38]
×
×
0.253
4.759
7.150
-
0.729
-
-
GaussianOcc ‡
×
×
0.258
5.733
7.222
0.343
0.753
0.888
0.934
SimpleOcc [11]
✓
✓
0.224
3.383
7.165
0.333
0.753
0.877
0.930
OccNeRF [54]
✓
✓
0.202
2.883
6.697
0.319
0.768
0.882
0.931
OccNeRF [54] †
✓
✓
0.456
12.682
9.194
0.399
0.704
0.833
0.890
SelfOcc [22]
✓
✓
0.215
2.743
6.706
0.316
0.753
0.875
0.932
GaussianOcc
×
✓
0.211
3.115
7.131
0.326
0.762
0.878
0.931
GaussianOcc †
×
✓
0.197
1.846
6.733
0.312
0.746
0.873
0.931
DDAD [13]
FSM* [14]
×
×
0.228
4.409
13.433
0.342
0.687
0.870
0.932
VFF [27]
×
×
0.218
3.660
13.327
0.339
0.674
0.862
0.932
SurroundDepth [44]
×
×
0.208
3.371
12.977
0.330
0.693
0.871
0.934
SA-FSM [50]
×
×
0.187
3.093
12.578
0.311
0.731
0.891
0.945
R3D3 [38]
×
×
0.162
3.019
11.408
-
0.811
-
-
GaussianOcc ‡
×
×
0.212
3.556
12.564
0.320
0.701
0.888
0.944
GaussianOcc
×
✓
0.228
3.854
14.326
0.357
0.660
0.853
0.922
Table 2. Comparisons for self-supervised multi-camera depth estimation on the nuScenes [3] and DDAD datasets [13]. The results
are averaged over all views without median scaling at test time. ‘FSM*’ is the reproduced result in [27]. GaussianOcc ‡ represents the depth
estimation result from Stage 1. GaussianOcc † and OccNeRF † means the model trained with the semantic information. Occ. represents
the ability of the method to predict the 3D occupancy.
Figure 4. Visualization of the render depth map and 3D occupancy prediction on the nuScenes and DDAD datasets.


## Page 7

Scale-aware training in [27, 44]
Scale-aware training by ours
RMSE
Loss in [44]
Loss in [27]
GS loss
Mask
Erode
Refine
Abs Rel
Sq Rel
RMSE
log
δ < 1.25
δ < 1.252
δ < 1.253
✓*
0.280
4.401
7.467
0.364
0.661
0.844
0.917
✓
0.672
25.405
11.999
0.568
0.419
0.808
0.878
✓*
0.289
5.718
7.551
0.348
0.709
0.876
0.932
✓
0.285
6.046
7.514
0.342
0.702
0.865
0.931
✓
0.798
11.571
15.251
1.472
0.006
0.015
0.028
✓
✓
0.293
7.127
7.536
0.376
0.743
0.876
0.923
✓
✓
✓
0.281
6.986
7.347
0.354
0.766
0.885
0.929
✓
✓
✓
✓
0.258
5.733
7.222
0.343
0.753
0.888
0.934
Table 3. Ablation study for scale-aware depth estimation on the nuScenes dataset [3]. ✓* means the result from the original paper and
✓means the result using New-CRFs [52] as the depth network the same as ours. GS loss means using the spatial context constraint by our
proposed Gaussian splatting for projection. Mask represents using the mask-out strategy before the unprojection. Erode means the erode
process to the binary overlap mask and Refine is the refinement of depth estimation network with 2 epochs by fixing the 6D pose net.
Figure 5. The comparison of the depth map and its synthesis over-
lap image with (1) direct bilinear interpolation cross-view synthe-
sis [44] and (2) our cross-view Gaussian splatting synthesis.
as indicated in GaussianOcc † whereas it worsens the re-
sult in OccNeRF †. This phenomenon can be attributed to
the biased sampling strategy of OccNeRF, where only 25%
of the sample points are used for faster semantic map ren-
dering compared to depth map rendering. In contrast, our
proposed Gaussian splatting method, which renders directly
from the voxel vertices, eliminates this issue.
4.4. Ablation Study
Scale-aware training in Stage 1: We compare our method
with existing approaches [27, 44] on Table 3 to demonstrate
the effectiveness of the proposed scale-aware training using
Gaussian Splatting. For a more fair comparison, we also
implemented scale-aware training on [27, 44] that uses the
same depth estimation network as ours [52], noted as ✓.
We could reproduce the result on [27], but it is not good
to training network with the sparse depth following [44].
Our proposed scale-aware training method is better than
[27, 44]. Specifically, we observed that a naive implemen-
tation of Gaussian splatting without a mask-out strategy for
cross-view rendering is ineffective because it would lead to
a sub-optimal solution that the rendered image is still from
the current view. Besides, to enhance performance, we in-
troduced an erosion operation on the binary mask to purify
Figure 6. The comparison for the depth map in the different set-
ting, corresponding to the training strategy in Table 4 and render-
ing type in Table 5.
it, excluding regions that may fall outside the overlap area.
This step ensures better alignment during training. Finally,
we refined the depth estimation by fixing the 6D pose net
and disabling the cross-view loss. This refinement helps
reduce artifacts at the edges of the overlap region. Visual-
ization: In Figure 5, we can see that the depth map is eas-
ily be suboptimal depth estimation in near overlap region
with the training of (1) direct cross-view interpolation con-
strain in [44]. Specifically, though the region with yellow
rectangle has the incorrect large depth value, the synthesis
region still presents a reasonable result that would lead to
sub-optimal training. Thanks to our cross-view Gaussian
splatting design analysis above, our method shown in (2)
does not have the sub-optimal situation.
6D pose learning and training strategy: Considering the
6D ego pose from the sensor is imperfect as a lack of verti-
cal movement [36]. We further evaluate the learned 6D pose
quality by self-supervised depth result at stage 2, where the


## Page 8

Pose type
Abs Rel
Sq Rel
RMSE
δ < 1.25
GT pose
0.214
3.362
7.127
0.771
One stage training
0.946
17.008
16.397
0.103
[27]
0.235
3.592
7.295
0.750
Ours
0.211
3.115
7.131
0.762
Table 4. Comparison of pose type for stage 2 training on depth
estimation task [3]. One stage training directly uses the cross-view
loss to the rendered depth map. Apart from the GT pose, we also
experiment the learned pose from [27] for comparison.
Render type
Abs Rel
Sq Rel
RMSE
δ < 1.25
VR
0.215
3.508
7.113
0.775
SR (s = 0.05)
0.223
3.694
7.246
0.761
SR (s = 0.1)
0.217
3.504
7.152
0.770
SR (s = 0.15)
0.217
3.406
7.204
0.763
SR (s = learnable)
0.212
3.248
7.112
0.771
Table 5. Comparison of the render result between the volume ren-
dering (VR) [54] and splatting rendering (SR, Ours) on depth es-
timation task [3]. The coefficient s means the scale of the 3D
Gaussian and learnable means the scale is learnable by the Sig-
moid function. We use GT pose for this set of the ablation study.
Pose type
mIoU*
Abs Rel
Sq Rel
δ < 1.25
GT pose (VR)
10.81
0.456
12.682
0.704
GT pose (SR)
11.30
0.225
4.339
0.787
Learned pose (VR)
11.19
0.506
15.577
0.684
Learned pose (SR)
11.26
0.197
1.846
0.746
Table 6. Comparison of ground truth pose (GT Pose) and our
learned pose (Two stages) on 3D occupancy estimation task [3]
in volume rendering (VR) and splatting rendering (SR).
Render
Render resolution and time (s)
Training
type
180 × 320
240 × 520
360 × 640
time (h)
VR
≈0.85
≈1.57
N/A
≈2.68
SR
≈0.17
≈0.17
≈0.17
≈1
Table 7. Comparison of rendering efficiency between volume ren-
dering (VR) [54] and splatting rendering (SR, Ours) on 3D occu-
pancy estimation task [3]. The render time is calculated from sur-
round 6 images. ”N/A” indicates out-of-memory errors running in
NVIDIA A 100 (40 GB). Training time is averaged per epoch.
experiments on Table 4 use the same network but with dif-
ferent pose constraints. Our result is competitive compared
with GT pose, indicating that the predicted pose is of high
quality. Furthermore, one stage training was ineffective in
using the 6D pose from the jointly trained with 6D pose
net because the cross-view loss in the 3D voxel space led
to local optimization, which failed to generalize predictions
to non-overlapping regions, as shown in Figure 6. How-
ever, this issue did not occur in the depth maps produced
by the 2D decoder in Stage 1, highlighting the necessity of
the two-stage training. Besides, our result is also better than
[27], which is consistent the depth result on Table 3.
Volume rendering and Splatting rendering: In Table 5,
we compare the performance of volume rendering (VR) and
splatting rendering (SR) in the voxel space. For each 3D
Gaussian, we first set a uniform scale s for all Gaussians,
considering the well-arranged positions of vertices within
the voxel grid. Since the scale s is consistent across all three
dimensions, we set the rotation R as the identity matrix. We
found that a scale of 0.1 produced the best results, closely
matching the VR at this scale. Besides, by applying a learn-
able scale through the output of a Sigmoid function and
clamping the maximum scale to 0.12, we achieved the high-
est performance. The render depth maps are shown in Fig-
ure 6. The depth map by the volume rendering is smoother
thanks to dense sampling and the depth maps from splatting
rendering have the graininess effect, especially at the small
scale factor (0.05).
Pose and render types ablation study in occupancy task:
In Table 6, we present an ablation study to evaluate the im-
pact of using ground truth versus learned poses in the oc-
cupancy task, with training conducted using different ren-
dering methods. The results show that splatting rendering
achieves superior performance in both occupancy metrics
(mIoU*) and depth metrics. One observation is that depth
estimation results with the semantic learning in volume ren-
dering are significantly worse than those in Table 2 whereas
our proposed splatting rendering method maintains consis-
tent performance, which suggests the splatting rendering in
voxel grid contributes better 3D geometry.
Rendering efficiency analysis: We analyze rendering effi-
ciency in Table 7. The results show that volume rendering
consumes 5 times more rendering time compared to splat-
ting rendering. As resolution increases, both volume ren-
dering time and GPU consumption rise significantly.
In
contrast, splatting rendering shows no significant increase
in computational cost with higher resolutions, highlighting
its efficiency and scalability.
5. Conclusion
In this paper, we introduce GaussianOcc, a fully self-
supervised and efficient method for 3D occupancy esti-
mation. Through the carefully designed cross-view splat-
ting rendering, we can accurately learn the real scale in
depth and the 6D pose, enabling effective self-supervised
3D occupancy learning. Additionally, the proposed Gaus-
sian splatting in voxel grids outperforms volume rendering
in 3D occupancy estimation while reducing computational
cost.
Acknowledgments This work was supported in part by
the JSPS, KAKENHI under Grant Number 22H03609, JST,
FOREST under Grant Number JPMJFR206S. Wanshui Gan
was also supported by RIKEN JRA Program. Big thanks for
Xiaoyu Dong for helping proofreading the manuscript.


## Page 9

Appendix
Abstract
In this supplementary material, we provide more implemen-
tation details, experiment results with analysis, and further
discussion on the limitations and future work.
A. More implementation details
The detailed parameter setting in Gaussian attributes
estimation network [52]. During the joint depth and 6D
pose training in stage 1, we predict the 3D Gaussian pa-
rameters alongside the 2D depth map. Since the Gaussian
parameters are well-arranged in the 2D image plane prior
to unprojection, we maintain equal scaling across all three
dimensions of each 3D Gaussian and constrain the maxi-
mum scale to 0.02. Given that the scale s is uniform across
all dimensions, we set the rotation matrix \protect \mathbf  {R} to the identity
matrix. Additionally, we assign an opacity value of 1 to
each 3D Gaussian, ensuring that every 2D depth value cor-
responds to a valid point in 3D space. We do not predict the
color defined by SH coefficients c, while we directly use the
source RGB image as the color map the same as in [58].
The detailed parameter setting in voxel grid splat-
ting rendering for semantic rendering. For semantic ren-
dering, we chose a fixed scale for each grid vertex to en-
sure a well-arranged structure that accurately models the
3D space. If we use a learnable scale, it may lead to a
situation where the scale is small but the opacity is large,
which may not be captured in the rendered depth map and
semantic map but could still affect the 3D occupancy re-
sult. Therefore, using a fixed scale is simple and sufficient
for optimization, as demonstrated in the results presented
in the main paper (Table 5) that the performance is close
to the learnable scale. Since the scale s ∈R3
+ are iden-
tical for both three dimensions, we do not need to predict
the rotation r ∈R4 and set it with the identical matrix is
sufficient. Similar to the OccNeRF [54], we render the 2D
feature map for the semantic regression, while we leverage
the 3D Gaussian splatting rendering and OccNeRF uses vol-
ume rendering.
The detailed parameter setting in training. We follow
the training setting as OccNeRF [54], the resolution of input
images and rendered depth maps are set as 384×640 and
180×320 respectively. All experiments are conducted on 8
NVIDIA A100 (40 GB).
The detailed training strategy of the self-supervised
pretraining setting. We first do the self-supervised train-
ing with 12 epochs with the learned pose from stage 1 and
the 2D pseudo semantic label, which does not require the
3D occupancy label. Then, we finetune the model with 12
epochs with the 3D occupancy label. We add the RayIoU
Figure 7. One-stage training analysis. This is the visualization
of the overlap mask and the rendered depth map with one-stage
training.
metric [31] in Table 11 for a comprehensive comparison.
The detailed definition of depth map metric. Follow-
ing the depth estimation task [44], we report the depth map
evaluation with the following metrics,
  \ begi n
 {s
p
lit
} \ te x t {Ab s Re
l: } \f r
ac 
{
1}{
|M| } \ sum _
{
d \i
n M}\
l
e
ft 
|
\ha
t {d } -d^*\
righ t | 
/
 
d^*
 
, \
\ \te xt  {Sq  Rel:
}  \ f r ac  {1}{ |M|
}  \
su m  _
{d
 
\ i n  M}\left \|\hat {d}-d^*\right \|^2 / d^*, \\ \text { RMSE: } \sqrt {\frac {1}{|M|} \sum _{d \in M}|| \hat {d}-d^* \|^2}, \\ \text { RMSE log: } \sqrt {\frac {1}{|M|} \sum _{d \in M}|| \log \hat {d}-\log d^* \|^2} , \\ \delta <t: \% \text { of } d \text { s.t. } \max \left (\frac {\hat {d}}{d^*}, \frac {d^*}{\hat {d}}\right )=\delta <t, \end {split} 
(5)
where M is the valid pixel, ˆd is the ground truth depth and
d∗is the predicted depth.
B. More experiment results and analysis
Why we need two-stage training. We made extensive ef-
forts to develop one-stage training that directly applies the
cross-view loss to the rendered depth map but were unsuc-
cessful. As suggested in Figure 7, the cross-view supervi-
sion signals are effective only in overlapping regions. The
rendered depth map learned from 3D CNN has lower gener-
alization ability in non-overlap regions compared with the


## Page 10

decoder depth learned by the 2D CNN, which led to local
minima.
mIoU metric. Due to the limited space in the main pa-
per, the full table of mIoU results is presented in Table 9 for
reference.
RayIoU metric. In addition to the mIoU metric for 3D
occupancy estimation, we also evaluate our method with a
novel metric, RayIoU, introduced by the recent work [31].
The RayIoU is a ray-based evaluation metric that resolves
the inconsistency penalty along the depth axis introduced in
the traditional voxel-level mIoU criteria. As shown in Table
10, our approach also outperforms OccNeRF [54] in this
metric as well. It’s important to note that the FPS is cal-
culated excluding rendering time. Since GaussianOcc and
OccNeRF utilize the same network architecture, they share
the same inference time when the rendering process is not
taken into account.
More
visualization.
We
provide
more
visual-
ization for nuScenes dataset in Figure 8.
Please
check
the
videos
for
sequence
visualization
in
https://github.com/GANWANSHUI/GaussianOcc.git.
More analysis on 3D occupancy and depth map result
on different supervision types.
3D occupancy analysis: In Figure 9, we present visual-
izations of different supervision types. These visualizations
highlight key differences in the results for the invisible re-
gions (marked with red rectangles) and the rendered depth
quality (marked with green rectangles).
Experiments (1) and (2) involve supervision using
ground truth (GT) occupancy labels. Specifically:
Experiment (1) is trained without the visible mask pro-
vided by Occ3D-nuScenes [41], which defines the visibility
of the occupancy labels. Without this mask, the invisible re-
gions are treated as empty, and the loss function is applied
to these regions as well. Experiment (2), on the other hand,
excludes the loss computation in invisible regions. From the
results, we observe that in Experiment (1), the model tends
to predict empty values for invisible regions due to empty
loss penalty. In contrast, Experiment (2), by ignoring the
loss in invisible areas, shows more non-empty predictions
in these regions.
Self-supervised experiments (3) and (4) rely on render-
ing techniques, which inherently cannot optimize predic-
tions in invisible regions.
This limitation leads to non-
empty predictions in the red-highlighted areas. Notably, Ex-
periment (4) frequently predicts invisible regions as related
to foreground categories, as shown in the dark rectangles.
Conversely, Experiment (3) demonstrates a consistent ten-
dency to classify invisible regions as man-made structures,
likely because the surrounding environment predominantly
consists of man-made elements.
Render depth map analysis: In Tables 2 and 6 of main
paper, we observe an interesting phenomenon that the se-
Render resolution
Render time (s) with different voxel resolutions (Gaussians number)
180 × 320
16 × 200 × 200
24 × 300 × 300
32 × 512 × 512
VR
≈0.50
≈0.85
≈1.52
SR
≈0.06
≈0.17
≈0.44
Table 8. Comparison of rendering efficiency under different Gaus-
sians number between volume rendering (VR) [54] and splatting
rendering (SR, Ours).
mantic information is helpful for the depth estimation with
our GaussianOcc whereas it worsens the result in OccN-
eRF. In Figure 9, we visualize the depth map and highlight
with green rectangles that our Gaussian splatting rendering
produces higher-quality depth predictions compared to vol-
ume rendering. This should be concluded to the biased sam-
pling strategy of OccNeRF, where only 25% of the sample
points are used for faster semantic map rendering compared
to depth map rendering. Here is the piece of the code in
OccNeRF [54]. In contrast, our proposed Gaussian splat-
ting method, which renders directly from the voxel vertices,
eliminates this issue. At last, since Experiments (1) and (2)
do not involve rendering-based training, they fail to produce
reasonable depth predictions.
Gaussians number and its related render time: (1) In
stage 1, Gaussians number depends on the depth map res-
olution from the 2D decoder, where each pixel is a Gaus-
sian primitive after unprojection. We use the depth map
resolution in 224 × 352, resulting in 78,848 Gaussian prim-
itives in one image.
In stage 2, Gaussians number de-
pends on the voxel resolution, where each voxel grid is
a Gaussian primitive. In Table 7 of the main paper, we
follow the voxel resolution the same as OccNeRF [52] in
24×300×300, resulting in 2,160,000 Gaussian primitives.
(2) We revealed the rendering time under different render
image resolutions compared with volume rendering in Ta-
ble 7 of the main paper. We conducted the extra experiment
for render time comparison under the same render image
resolution (180 × 320) but with different Gaussians num-
ber (voxel resolutions) as shown in Table 8. From Table 7
of the main paper and Table 8, we observe: (1) The ren-
der time of splatting rendering (SR) is mainly affected by
the Gaussians number, not the render image resolution. (2)
SR is 3–8 times faster than volume rendering (VR) across
different voxel settings.
Bonus of the fully self-supervised setting: The fully self-
supervised setting of our method could be a general pre-
training solution for supervised learning.
After the self-
supervised training on the DDAD and nuScenes datasets,
we further finetune the model with the 3D occupancy label
from Occ3D [41]. As shown in Table 11, experiments with
self-supervised pretraining outperform the baseline. In par-
ticular, we find that pretraining on nuScenes is better than
the DDAD dataset, which may own to the domain gap fac-
tors, such as differences in the scenarios (RGB images) and


## Page 11

sensor configurations (camera extrinsics).
C. Limitation and future work
The proposed method achieves reasonable predictions in
most scenes; however, we observe that some cases still
present challenges, as shown in Figure 10.
Specifically,
in the DDAD dataset, incorrect predictions occur in the
back camera in certain situations as marked with the red
circle, where the drivable surface is mistakenly projected
into the car due to extensive self-occlusion. Notably, this
issue is absent in the nuScenes dataset, which has less self-
occlusion. We believe that this problem could be mitigated
with better 2D semantic maps for supervision, which war-
rants further investigation. The proposed method is for the
surround view setting which is not suitable for the monocu-
lar images. Additionally, in stage 1, we leverage the spatial
cross-view constraint for scale-aware training through the
proposed Gaussian splatting method. In the future, we aim
to explore its potential benefits for temporal view synthesis
as well.
References
[1] Yanqi Bao, Tianyu Ding, Jing Huo, Yaoli Liu, Yuxin Li,
Wenbin Li, Yang Gao, and Jiebo Luo. 3d gaussian splatting:
Survey, technologies, challenges, and opportunities. arXiv
preprint arXiv:2407.17418, 2024. 2
[2] Gary Bradski. The opencv library. Dr. Dobb’s Journal: Soft-
ware Tools for the Professional Programmer, 25(11):120–
123, 2000. 4
[3] Holger Caesar, Varun Bankiti, Alex H Lang, Sourabh Vora,
Venice Erin Liong, Qiang Xu, Anush Krishnan, Yu Pan,
Giancarlo Baldan, and Oscar Beijbom. nuscenes: A mul-
timodal dataset for autonomous driving.
In CVPR, pages
11621–11631, 2020. 2, 4, 6, 7, 8
[4] Anh-Quan Cao and Raoul de Charette. Monoscene: Monoc-
ular 3d semantic scene completion. In CVPR, pages 3991–
4001, 2022. 5, 12
[5] Anh-Quan Cao and Raoul de Charette.
Scenerf:
Self-
supervised monocular 3d scene reconstruction with radiance
fields. In ICCV, pages 9387–9398, 2023. 1
[6] Florian Chabot, Nicolas Granger, and Guillaume Lapouge.
Gaussianbev:
3d gaussian representation meets percep-
tion models for bev segmentation.
arXiv preprint
arXiv:2407.14108, 2024. 2
[7] David Charatan, Sizhe Lester Li, Andrea Tagliasacchi, and
Vincent Sitzmann. pixelsplat: 3d gaussian splats from image
pairs for scalable generalizable 3d reconstruction. In Pro-
ceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition, pages 19457–19467, 2024. 2
[8] Yuanxing Duan, Fangyin Wei, Qiyu Dai, Yuhang He, Wen-
zheng Chen, and Baoquan Chen. 4d-rotor gaussian splatting:
Towards efficient novel view synthesis for dynamic scenes.
In ACM SIGGRAPH 2024 Conference Papers, pages 1–11,
2024. 2
[9] Shaoheng Fang, Zi Wang, Yiqi Zhong, Junhao Ge, and Si-
heng Chen. Tbp-former: Learning temporal bird’s-eye-view
pyramid for joint perception and prediction in vision-centric
autonomous driving. In Proceedings of the IEEE/CVF Con-
ference on Computer Vision and Pattern Recognition, pages
1368–1378, 2023. 1
[10] Wanshui Gan, Hongbin Xu, Yi Huang, Shifeng Chen, and
Naoto Yokoya.
V4d: Voxel for 4d novel view synthesis.
IEEE Transactions on Visualization and Computer Graph-
ics, 2023. 1, 2
[11] Wanshui Gan, Ningkai Mo, Hongbin Xu, and Naoto Yokoya.
A comprehensive framework for 3d occupancy estimation in
autonomous driving. IEEE Transactions on Intelligent Vehi-
cles, 2024. 1, 2, 4, 5, 6, 12, 15
[12] Cl´ement Godard, Oisin Mac Aodha, Michael Firman, and
Gabriel J Brostow. Digging into self-supervised monocular
depth estimation. In ICCV, pages 3828–3838, 2019. 2
[13] Vitor Guizilini, Rares Ambrus, Sudeep Pillai, Allan Raven-
tos, and Adrien Gaidon.
3d packing for self-supervised
monocular depth estimation.
In Proceedings of the
IEEE/CVF conference on computer vision and pattern
recognition, pages 2485–2494, 2020. 2, 4, 5, 6
[14] Vitor Guizilini,
Igor Vasiljevic,
Rares Ambrus,
Greg
Shakhnarovich, and Adrien Gaidon.
Full surround mon-
odepth from multiple cameras. RAL, 7(2):5397–5404, 2022.
2, 3, 6
[15] Xianda Guo, Wenjie Yuan, Yunpeng Zhang, Tian Yang,
Chenming Zhang, Zheng Zhu, and Long Chen.
A sim-
ple baseline for supervised surround-view depth estimation.
arXiv preprint arXiv:2303.07759, 2023. 2
[16] Adrian Hayler, Felix Wimbauer, Dominik Muhle, Christian
Rupprecht, and Daniel Cremers. S4c: Self-supervised se-
mantic scene completion with neural fields. In 2024 Inter-
national Conference on 3D Vision (3DV), pages 409–420.
IEEE, 2024. 1
[17] Lei He, Leheng Li, Wenchao Sun, Zeyu Han, Yichen Liu,
Sifa Zheng, Jianqiang Wang, and Keqiang Li. Neural radi-
ance field in autonomous driving: A survey. arXiv preprint
arXiv:2404.13816, 2024. 2
[18] Junjie Huang and Guan Huang. Bevdet4d: Exploit tempo-
ral cues in multi-camera 3d object detection. arXiv preprint
arXiv:2203.17054, 2022. 12
[19] Junjie Huang, Guan Huang, Zheng Zhu, and Dalong Du.
Bevdet: High-performance multi-camera 3d object detection
in bird-eye-view. arXiv preprint arXiv:2112.11790, 2021. 5,
12
[20] Nan Huang, Xiaobao Wei, Wenzhao Zheng, Pengju An,
Ming Lu, Wei Zhan, Masayoshi Tomizuka, Kurt Keutzer,
and Shanghang Zhang.
S3 gaussian:
Self-supervised
street gaussians for autonomous driving.
arXiv preprint
arXiv:2405.20323, 2024. 2
[21] Yuanhui Huang, Wenzhao Zheng, Yunpeng Zhang, Jie Zhou,
and Jiwen Lu. Tri-perspective view for vision-based 3d se-
mantic occupancy prediction. In CVPR, pages 9223–9232,
2023. 5, 12
[22] Yuanhui Huang, Wenzhao Zheng, Borui Zhang, Jie Zhou,
and Jiwen Lu. Selfocc: Self-supervised vision-based 3d oc-


## Page 12

Method
GT Occ.
GT Pose
mIoU* mIoU
■barrier
■bicycle
■bus
■car
■const. veh.
■motorcycle
■pedestrian
■traffic cone
■trailer
■truck
■drive. suf.
■sidewalk
■terrain
■manmade
■vegetation
MonoScene [4]
✓×
6.33
6.06
7.23
4.26
4.93
9.38
5.67
3.98
3.01
5.90
4.45
7.17 14.91 7.92
7.43
1.01
7.65
BEVDet [19]
✓× 20.03 19.38 30.31 0.23 32.26 34.47 12.97 10.34 10.36 6.26
8.93 23.65 52.27 26.06 22.31 15.04 15.10
BEVFormer [29] ✓× 24.64 23.67 38.79 9.98 34.41 41.09 13.24 16.50 18.15 17.83 18.66 27.70 48.95 29.08 25.38 15.41 14.46
OccFormer [57] ✓× 22.39 21.93 30.29 12.32 34.40 39.17 14.44 16.45 17.22 9.27 13.90 26.36 50.99 34.66 22.73 6.76
6.97
RenderOcc [37] ✓× 24.53 23.93 27.56 14.36 19.91 20.56 11.96 12.42 12.14 14.34 20.81 18.94 68.85 42.01 43.94 17.36 22.61
TPVFormer [21] ✓× 28.69 27.83 38.90 13.67 40.78 45.90 17.23 19.99 18.85 14.30 26.69 34.17 55.65 37.55 30.70 19.40 16.78
CTF-Occ [41]
✓× 29.54 28.53 39.33 20.56 38.29 42.24 16.93 24.52 22.72 21.05 22.98 31.11 53.33 37.98 33.23 20.79 18.00
SimpleOcc [11]
× ✓
7.99
7.05
0.67
1.18
3.21
7.63
1.02
0.26
1.80
0.26
1.07
2.81 40.44 18.30 17.01 13.42 10.84
SelfOcc [22]
× ✓10.54
9.30
0.15
0.66
5.46 12.54 0.00
0.80
2.10
0.00
0.00
8.25 55.49 26.30 26.54 14.22 5.60
OccNeRF [54]
× ✓10.81
9.54
0.83
0.82
5.13 12.49 3.50
0.23
3.10
1.84
0.52
3.90 52.62 20.81 24.75 18.45 13.19
GaussianOcc
× × 11.26
9.94
1.79
5.82 14.58 13.55 1.30
2.82
7.95
9.76
0.56
9.61 44.59 20.10 17.58 8.61 10.29
Table 9. 3D occupancy prediction performance on the Occ3D-nuScenes dataset in mIoU metric. Since ‘other’ and ‘other flat’ classes
are the invalid prompts for open-vocabulary models, we also calculate ‘mIoU*’ as the result ignoring the classes that do not consider these
two classes during evaluation, while ‘mIoU’ is the original result. GT Occ. refers to the use of the ground truth occupancy label for
supervision. GT Pose is the ground truth pose from the sensor for self-supervised geometry learning.
Method
GT Occ.
GT Pose
Backbone
Input Size
Epoch
RayIoU
RayIoU1m, 2m, 4m
mIoU
FPS
BEVFormer (4f) [29]
✓
×
R101
1600×900
24
32.4
26.1
32.9
38.0
39.2
3.0
RenderOcc [37]
✓
×
Swin-B
1408×512
12
19.5
13.4
19.6
25.5
24.4
-
SimpleOcc [11]
✓
×
R101
672×336
12
28.2
22.3
28.7
33.7
37.3
9.7
BEVDet-Occ (2f) [18]
✓
×
R50
704×256
90
29.6
23.6
30.0
35.1
36.1
2.6
BEVDet-Occ-Long (8f)
✓
×
R50
704×384
90
32.6
26.6
33.1
38.2
39.3
0.8
FB-Occ (16f) [30]
✓
×
R50
704×256
90
33.5
26.7
34.1
39.7
39.1
10.3
SparseOcc (8f)
✓
×
R50
704×256
24
34.0
28.0
34.7
39.4
30.1
17.3
SparseOcc (16f)
✓
×
R50
704×256
48
36.1
30.2
36.8
41.2
30.9
12.5
OccNeRF [54]
×
✓
R101
640×384
12
10.49
6.93
10.28
14.26
9.54
10.8
GaussianOcc
×
×
R101
640×384
12
11.85
8.69
11.90
14.95
9.94
10.8
Table 10. 3D Occupancy prediction performance on the Occ3D-nuScenes dataset in RayIoU metric. GT Occ. means using the ground
truth occupancy label for the supervision. GT Pose is the ground truth pose from the sensor for self-supervised geometry learning. “8f”
and “16f” mean fusing temporal information from 8 or 16 frames. mIoU is the mean Intersection over Union for all categories. FPS means
frame per second for each method, which is measured on a Tesla A100 GPU.
cupancy prediction. In Proceedings of the IEEE/CVF Con-
ference on Computer Vision and Pattern Recognition, pages
19946–19956, 2024. 1, 2, 4, 5, 6, 12
[23] Yuanhui Huang, Wenzhao Zheng, Yunpeng Zhang, Jie Zhou,
and Jiwen Lu.
Gaussianformer: Scene as gaussians for
vision-based 3d semantic occupancy prediction.
arXiv
preprint arXiv:2405.17429, 2024. 2
[24] Haoyi Jiang, Liu Liu, Tianheng Cheng, Xinjie Wang, Tian-
wei Lin, Zhizhong Su, Wenyu Liu, and Xinggang Wang.
Gausstr: Foundation model-aligned gaussian transformer for
self-supervised 3d spatial understanding. In CVPR, 2025. 2
[25] Kai Katsumata, Duc Minh Vo, and Hideki Nakayama. An ef-
ficient 3d gaussian representation for monocular/multi-view
dynamic scenes. arXiv preprint arXiv:2311.12897, 2023. 2
[26] Bernhard Kerbl, Georgios Kopanas, Thomas Leimk¨uhler,
and George Drettakis.
3d gaussian splatting for real-time
radiance field rendering. ACM Trans. Graph., 42(4):139–1,
2023. 2, 3
[27] Jung-Hee Kim, Junhwa Hur, Tien Phuoc Nguyen, and
Seong-Gyun Jeong. Self-supervised surround-view depth es-
timation with volumetric feature fusion. NeurlPS, 35:4032–
4045, 2022. 2, 3, 6, 7, 8
[28] Yinhao Li, Zheng Ge, Guanyi Yu, Jinrong Yang, Zengran
Wang, Yukang Shi, Jianjian Sun, and Zeming Li. Bevdepth:
Acquisition of reliable depth for multi-view 3d object detec-
tion. arXiv preprint arXiv:2206.10092, 2022. 1


## Page 13

Figure 8. The visualization of the render depth map and 3D occupancy prediction on nuScenes dataset.
[29] Zhiqi Li, Wenhai Wang, Hongyang Li, Enze Xie, Chong-
hao Sima, Tong Lu, Qiao Yu, and Jifeng Dai. Bevformer:
Learning bird’s-eye-view representation from multi-camera
images via spatiotemporal transformers. In ECCV, 2022. 1,
5, 12
[30] Zhiqi Li, Zhiding Yu, David Austin, Mingsheng Fang, Shiyi
Lan, Jan Kautz, and Jose M Alvarez. Fb-occ: 3d occupancy
prediction based on forward-backward view transformation.
arXiv preprint arXiv:2307.01492, 2023. 2, 12
[31] Haisong Liu, Haiguang Wang, Yang Chen, Zetong Yang, Jia
Zeng, Li Chen, and Limin Wang. Fully sparse 3d panop-
tic occupancy prediction. arXiv preprint arXiv:2312.17118,


## Page 14

Figure 9. The visualization of the different supervision types (1-4) comparison on nuScenes dataset.


## Page 15

Method
Pretraining setting
mIoU
RayIoU
RayIoU1m, 2m, 4m
Baseline
None
37.29
28.2
22.3
28.7
33.7
Self-supervised pretrain
DDAD
37.40
28.7
22.9
29.1
34.0
nuScenes
38.45
29.9
23.9
30.4
35.5
Table 11. The study on SimpleOcc [11] with fully self-supervised pretrain. The baseline is directly training the model with 3D occupancy
label. The self-supervised pretraining is conducted on DDAD and nuScenes and then finetuned the model with 3D occupancy label. The
number with bold typeface means the best.
Figure 10. Some wrong predictions due to the large self-occlusion on DDAD dataset.
2023. 1, 2, 5, 9, 10
[32] Tianqi Liu, Guangcong Wang, Shoukang Hu, Liao Shen,
Xinyi Ye, Yuhang Zang, Zhiguo Cao, Wei Li, and Ziwei
Liu.
Fast generalizable gaussian splatting reconstruction
from multi-view stereo. arXiv preprint arXiv:2405.12218,
2024. 2
[33] Ze Liu, Yutong Lin, Yue Cao, Han Hu, Yixuan Wei, Zheng
Zhang, Stephen Lin, and Baining Guo. Swin transformer:
Hierarchical vision transformer using shifted windows. In
Proceedings of the IEEE/CVF international conference on
computer vision, pages 10012–10022, 2021. 5
[34] Yuexin Ma, Tai Wang, Xuyang Bai, Huitong Yang, Yue-
nan Hou, Yaming Wang, Yu Qiao, Ruigang Yang, Dinesh
Manocha, and Xinge Zhu. Vision-centric bev perception: A
survey. arXiv preprint arXiv:2208.02797, 2022. 1, 2
[35] Ben Mildenhall, Pratul P Srinivasan, Matthew Tancik,
Jonathan T Barron, Ravi Ramamoorthi, and Ren Ng. Nerf:
Representing scenes as neural radiance fields for view syn-
thesis. In ECCV, pages 405–421. Springer, 2020. 1, 2, 4
[36] nuScenes team. Ego pose discussion. https://github.
com/nutonomy/nuscenes-devkit/issues/961.
Accessed November 12, 2024 [Online]. 7
[37] Mingjie Pan, Jiaming Liu, Renrui Zhang, Peixiang Huang,
Xiaoqi Li, Li Liu, and Shanghang Zhang.
Renderocc:
Vision-centric 3d occupancy prediction with 2d rendering
supervision. arXiv preprint arXiv:2309.09502, 2023. 1, 2, 4,
5, 12
[38] Aron Schmied, Tobias Fischer, Martin Danelljan, Marc
Pollefeys, and Fisher Yu. R3d3: Dense 3d reconstruction
of dynamic scenes from multiple cameras. In ICCV, pages
3216–3226, 2023. 2, 5, 6
[39] Yining Shi, Kun Jiang, Jiusi Li, Junze Wen, Zelin Qian,
Mengmeng Yang, Ke Wang, and Diange Yang. Grid-centric
traffic scenario perception for autonomous driving: A com-
prehensive review. arXiv preprint arXiv:2303.01212, 2023.
1, 2
[40] Stanislaw Szymanowicz, Chrisitian Rupprecht, and Andrea
Vedaldi.
Splatter image: Ultra-fast single-view 3d recon-


## Page 16

struction. In Proceedings of the IEEE/CVF Conference on
Computer Vision and Pattern Recognition, pages 10208–
10217, 2024. 2
[41] Xiaoyu Tian, Tao Jiang, Longfei Yun, Yue Wang, Yilun
Wang, and Hang Zhao.
Occ3d: A large-scale 3d occu-
pancy prediction benchmark for autonomous driving. arXiv
preprint arXiv:2304.14365, 2023. 1, 2, 4, 5, 10, 12
[42] Wenwen Tong, Chonghao Sima, Tai Wang, Li Chen, Silei
Wu, Hanming Deng, Yi Gu, Lewei Lu, Ping Luo, Dahua Lin,
et al. Scene as occupancy. In Proceedings of the IEEE/CVF
International Conference on Computer Vision, pages 8406–
8415, 2023.
[43] Xiaofeng Wang, Zheng Zhu, Wenbo Xu, Yunpeng Zhang, Yi
Wei, Xu Chi, Yun Ye, Dalong Du, Jiwen Lu, and Xingang
Wang. Openoccupancy: A large scale benchmark for sur-
rounding semantic occupancy perception. In ICCV, 2023. 1,
2
[44] Yi Wei, Linqing Zhao, Wenzhao Zheng, Zheng Zhu, Yong-
ming Rao, Guan Huang, Jiwen Lu, and Jie Zhou. Surround-
depth:
Entangling surrounding views for self-supervised
multi-camera depth estimation. In CoRL, pages 539–549.
PMLR, 2023. 2, 3, 5, 6, 7, 9
[45] Yi Wei, Linqing Zhao, Wenzhao Zheng, Zheng Zhu, Jie
Zhou, and Jiwen Lu. Surroundocc: Multi-camera 3d occu-
pancy prediction for autonomous driving. In ICCV, pages
21729–21740, 2023. 1, 2
[46] Felix Wimbauer, Nan Yang, Christian Rupprecht, and Daniel
Cremers. Behind the scenes: Density fields for single view
reconstruction. In Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, pages 9076–
9086, 2023. 1
[47] Guanjun Wu, Taoran Yi, Jiemin Fang, Lingxi Xie, Xiaopeng
Zhang, Wei Wei, Wenyu Liu, Qi Tian, and Xinggang Wang.
4d gaussian splatting for real-time dynamic scene rendering.
In Proceedings of the IEEE/CVF Conference on Computer
Vision and Pattern Recognition, pages 20310–20320, 2024.
2
[48] Huaiyuan Xu, Junliang Chen, Shiyu Meng, Yi Wang, and
Lap-Pui Chau. A survey on occupancy perception for au-
tonomous driving: The information fusion perspective. arXiv
preprint arXiv:2405.05173, 2024. 1
[49] Yunzhi Yan, Haotong Lin, Chenxu Zhou, Weijie Wang,
Haiyang Sun, Kun Zhan, Xianpeng Lang, Xiaowei Zhou,
and Sida Peng. Street gaussians for modeling dynamic ur-
ban scenes. arXiv preprint arXiv:2401.01339, 2024. 2
[50] Yuchen Yang, Xinyi Wang, Dong Li, Lu Tian, Ashish
Sirasao, and Xun Yang.
Towards scale-aware full sur-
round monodepth with transformers.
arXiv preprint
arXiv:2407.10406, 2024. 5, 6
[51] Zichen Yu, Changyong Shu, Jiajun Deng, Kangjie Lu, Zong-
dai Liu, Jiangyong Yu, Dawei Yang, Hui Li, and Yan
Chen.
Flashocc:
Fast and memory-efficient occupancy
prediction via channel-to-height plugin.
arXiv preprint
arXiv:2311.12058, 2023. 1, 2
[52] Weihao Yuan, Xiaodong Gu, Zuozhuo Dai, Siyu Zhu, and
Ping Tan. Newcrfs: Neural window fully-connected crfs for
monocular depth estimation.
In Proceedings of the IEEE
Conference on Computer Vision and Pattern Recognition,
2022. 4, 5, 7, 9
[53] Zhenlong Yuan, Jiakai Cao, Zhaoxin Li, Hao Jiang, and
Zhaoqi Wang.
Sd-mvs: Segmentation-driven deformation
multi-view stereo with spherical refinement and em opti-
mization. In Proceedings of the AAAI Conference on Arti-
ficial Intelligence, pages 6871–6880, 2024. 2
[54] Chubin Zhang, Juncheng Yan, Yi Wei, Jiaxin Li, Li Liu,
Yansong Tang, Yueqi Duan, and Jiwen Lu. Occnerf: Self-
supervised multi-camera occupancy prediction with neural
radiance fields. arXiv preprint arXiv:2312.09243, 2023. 1,
2, 4, 5, 6, 8, 9, 10, 12
[55] Hao Zhang, Feng Li, Xueyan Zou, Shilong Liu, Chunyuan
Li, Jianfeng Gao, Jianwei Yang, and Lei Zhang. A simple
framework for open-vocabulary segmentation and detection.
arXiv preprint arXiv:2303.08131, 2023. 1
[56] Haiming Zhang, Wending Zhou, Yiyao Zhu, Xu Yan, Jiantao
Gao, Dongfeng Bai, Yingjie Cai, Bingbing Liu, Shuguang
Cui, and Zhen Li. Visionpad: A vision-centric pre-training
paradigm for autonomous driving.
In Proceedings of the
Computer Vision and Pattern Recognition Conference, pages
17165–17175, 2025. 1
[57] Yunpeng Zhang, Zheng Zhu, and Dalong Du. Occformer:
Dual-path transformer for vision-based 3d semantic occu-
pancy prediction. In ICCV, 2023. 2, 5, 12
[58] Shunyuan Zheng, Boyao Zhou, Ruizhi Shao, Boning Liu,
Shengping Zhang, Liqiang Nie, and Yebin Liu.
Gps-
gaussian: Generalizable pixel-wise 3d gaussian splatting for
real-time human novel view synthesis.
In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition, pages 19680–19690, 2024. 2, 9
[59] Xiaoyu Zhou, Zhiwei Lin, Xiaojun Shan, Yongtao Wang,
Deqing Sun, and Ming-Hsuan Yang.
Drivinggaussian:
Composite gaussian splatting for surrounding dynamic au-
tonomous driving scenes. In Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition,
pages 21634–21643, 2024. 2

