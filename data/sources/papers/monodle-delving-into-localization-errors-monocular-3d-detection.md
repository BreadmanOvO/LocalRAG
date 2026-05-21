# MonoDLE Delving into Localization Errors Monocular 3D Detection

**Source**: arxiv PDF, 15 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Domain-Adaptive Self-Supervised Face & Body Detection in Drawings
Barıs¸ Batuhan Topal1 , Deniz Yuret1 , Tevﬁk Metin Sezgin1
1Department of Computer Engineering, KUIS AI Center, Koc¸ University
{baristopal20, dyuret, mtsezgin}@ku.edu.tr,
Abstract
Drawings are powerful means of pictorial ab-
straction and communication. Understanding di-
verse forms of drawings, including digital arts,
cartoons, and comics, has been a major prob-
lem of interest for the computer vision and com-
puter graphics communities.
Although there are
large amounts of digitized drawings from comic
books and cartoons, they contain vast stylistic vari-
ations, which necessitate expensive manual label-
ing for training domain-speciﬁc recognizers.
In
this work, we show how self-supervised learning,
based on a teacher-student network with a mod-
iﬁed student network update design, can be used
to build face and body detectors.
Our setup al-
lows exploiting large amounts of unlabeled data
from the target domain when labels are provided
for only a small subset of it. We further demon-
strate that style transfer can be incorporated into
our learning pipeline to bootstrap detectors using
a vast amount of out-of-domain labeled images
from natural images (i.e., images from the real
world). Our combined architecture yields detec-
tors with state-of-the-art (SOTA) and near-SOTA
performance using minimal annotation effort. Our
code can be accessed from https://github.
com/barisbatuhan/DASS_Detector.
1
Introduction
Drawings serve as a rich and expressive medium for commu-
nication. The earliest examples were painted on cave walls
more than 45,000 years ago [Brumm et al., 2021]. Here we
focus on comic books and cartoons, which are relatively re-
cent forms of media. They combine text and graphics in a
unique format to convey narratives. Key problems such as ex-
tracting the visual structure of the scenes, understanding the
accompanying text, and modeling how they connect to form
the narrative pose signiﬁcant challenges. Hence, understand-
ing comics has been a problem of interest to computer vision,
computer graphics, and NLP communities.
In drawings, the story is narrated primarily through the
scene’s main characters. Hence, we study on face and body
detection, two primary problems for understanding drawings.
Figure 1: Examples on the adversity of this domain (left: non-
human character, right: samples from different character designs and
styles).
Training face and body detectors is complicated by two chal-
lenges. First, although a tremendous amount of unlabeled
data is available (primarily as digitized comic book pages
and animations), face and body annotations are largely lack-
ing. Second, since character design and drawing style change
substantially across artists, series, and cultures (see Figure
1), each domain inevitably requires domain-speciﬁc tuning
to create detectors. In this work, we present a pre-training
pipeline for creating domain-adapted detectors, which ad-
dresses both problems. Our pipeline has two major compo-
nents. The ﬁrst is a self-learning component that can exploit
vast amounts of unlabeled data from the target domain to cre-
ate detectors that can be tuned with minimal labeled data.
More speciﬁcally, we introduce a modiﬁed version of teacher-
student architecture to drawings, where we periodically up-
date the student network’s weights with teacher’s after a spe-
ciﬁc number of iterations and utilize the OHEM [Shrivastava
et al., 2016] loss with an additional positive and negative con-
ﬁdence threshold limitation for a more stable training. We
show that this self-learning model works best if it starts with
a sufﬁciently good teacher. This component leads to the sec-
ond key component of our pipeline, which uses style transfer
to transform vast amounts of labeled natural images to create
sufﬁciently good teacher models by utilizing 11 styles from 4
style transfer algorithms.
We employ a multi-tasking strategy by jointly training the
model for faces and bodies to reduce inference time and to
beneﬁt from the contextual and spatial relationship. To uti-
arXiv:2211.10641v2  [cs.CV]  25 Apr 2023
### Page 2

Natural Images 
(COCO & WF)
Style 
Transfer
Cartoonized 
Images
Pre-trained 
Weights V1
Unlabeled 
Drawing Images
Supervised 
Training
Teac. Stu. 
Training
Pre-trained 
Weights V2
Low Sized 
(64-1024) Labeled 
Drawing Images 
Supervised 
Training
Final Model
Process
Data
Model Weights
Stage 1
Stage 2
Stage 3: Fine-Tuning
Figure 2: Summary of the proposed pipeline.
lize datasets with face-only and body-only annotations, we
use two detection heads: one to predict the faces, and the
other for bodies.
Even without drawing domain supervi-
sion, our teacher-student model outperforms previous super-
vised SOTA of DCM 772 [Nguyen et al., 2018] and weakly-
supervised SOTA [Inoue et al., 2018] in most datasets. When
initialized with our pre-trained weights, our supervised model
sets a new SOTA performance for most datasets, even if lim-
ited drawing data is used in training.
2
Related Works
2.1
Detection
With the increasing size of annotated data, models with
high dependence on supervision were able to get good re-
sults (e.g., [Bochkovskiy et al., 2020; Zhang et al., 2020b;
Ge et al., 2021]). [Liu et al., 2021] and [Xu et al., 2021] in-
troduced teacher-student training schemes and gained a sig-
niﬁcant performance boost with a low amount of labeled
data. Unlike this work, these studies target natural images.
Thus, cross-domain detection with these models is prone
to false positives (FP) and negatives (FN). Several studies
have improved the teacher-student scheme to work well in
cross-domain detection.
While MTOR [Cai et al., 2019]
exploits object relations in region-level consistency, inter-
graph consistency, and intra-graph consistency, UMT [Deng
et al., 2020] tries to eliminate teacher and student network bi-
ases through distillation and style transferring, D-adapt [Jiang
et al., 2022] adopts an adversarial pipeline to the detector
model, H2FA R-CNN [Xu et al., 2022] utilizes weak su-
pervision and domain classiﬁers to create a more domain-
invariant model. Although our solution is more similar to
UMT compared to other cross-domain studies, we improve
its style transferring part by mixing multiple styles, we mod-
ify the standard teacher-student training to compensate for the
FP and FN cases, and we change the loss function to force the
model to learn from more conﬁdent proposals.
Several studies have been done on face and object detec-
tion, speciﬁcally in drawings.
[Zhang et al., 2020a] pro-
posed a fully-supervised face detector using only iCartoon-
Face; [Ogawa et al., 2018] trained a detector from Manga
109; [Nguyen et al., 2018] used DCM 772; [Inoue et al.,
2018] utilized Comic2k, Watercolor2k, and Clipart1k. How-
ever, these models are only trained on speciﬁc sub-domains
of drawings (i.e., only utilized a single dataset with limited
stylistic coverage). In this study, we leverage unlabeled draw-
ing images from any sub-drawing domain and show that the
performance on drawings can be signiﬁcantly improved by
using an effective pre-training pipeline and a better detector
architecture.
2.2
Style Transfer
Conversion of natural images to drawings is an unpaired
image-to-image translation task. SOTA models for this task
have been designed with U-Net-like Generative Adversarial
Networks (i.e., down-sampling ﬁrst and then up-sampling).
We use several cartoonization models to increase the stylis-
tic variety of the pre-training data by selecting 11 styles from
these works: Monet, Van Gogh, Cezanne from CycleGAN
[Zhu et al., 2017]; Shinkai, Hayao, Hosoda, Paprika from
CartoonGAN [Chen et al., 2018]; AS, KH, Miyazaki from
GANILLA [Hicsonmez et al., 2020]; and the default style in
White-Box Cartoonization [Wang and Yu, 2020]. While pre-
vious detection studies on drawings have also utilized style
transfer methods (e.g., [Inoue et al., 2018; Deng et al., 2020]),
we improve on these results by combining multiple styles and
analyzing which styles increase the performance more.
2.3
Datasets
Digitization has made millions of unlabeled drawings reach-
able on the internet. Thousands of old comic book series (e.g.,
Golden Age Comics between the 1930s - 1950s) have been
published on several websites 1 and gathered as an unlabeled
dataset named COMICS [Iyyer et al., 2017]. Newer series
can be obtained through web crawling. Unfortunately, anno-
tated datasets only comprise a small subset of this domain in
terms of stylistic variety and quantity. Regarding the stylistic
distribution of labeled datasets, the majority of iCartoonFace
[Zheng et al., 2020] is retrieved from Asian products (∼74%),
Manga 109 [Matsui et al., 2017] only covers Japanese Manga
1comicbookplus.com and digitalcomicmuseum.com
### Page 3

styles, DCM 772 [Nguyen et al., 2018] is limited to comics
from Golden Age Era. Although [Inoue et al., 2018] intro-
duces Comic2k, Watercolor2k, and Clipart1k for body detec-
tion, they also remain stylistically bound in their sub-domain.
Currently, none of the available datasets provide comprehen-
sive stylistic coverage. In particular, contemporary US and
Western comics have little if any annotated examples.
In
terms of dataset quantity, iCartoonFace contains a signiﬁcant
amount of face data with its 50,000 training and 10,000 val-
idation images. The situation is a bit more challenging with
body annotations: Manga 109 has ∼21,000 page images, but
the style is limited to black and white mangas. DCM 772
consists of only 772 images. Comic2k, Watercolor2k, and
Clipart1k increase the total labeled data by 2,500 instances.
Building a body detector for drawings that is not fragile to dif-
ferent styles is challenging using only these datasets. Hence,
self-supervised approaches are essential for creating suitable
models for target instances with unseen styles.
3
Methodology
Our training consists of three stages. In the ﬁrst stage, we use
two large and annotated real-life image datasets, cartoonize
them using style transfer methods, and perform pre-training
for face and body detection. In the second stage, we utilize
the extensive amount of unlabeled comic drawings available
and perform self-supervised training on our pre-trained model
with the modiﬁed form of the teacher-student architecture. In
the ﬁnal stage, we leverage the limited amount of annotated
comic drawings to ﬁne-tune our model. In Figure 2, you can
see a demonstration of our complete pipeline. In the follow-
ing subsections, we describe our base model and the three
stages we propose in more detail.
3.1
Model Architecture
Since the challenge in our domain consists of stylistic vari-
ety in object representations (see Figure 1), we decide that
adopting an object-detector-like model would provide greater
performance, where the architecture is speciﬁcally designed
to ﬁnd multiple objects with various appearances. Secondly,
we aim to use a more robust and simple model with low in-
ference time to focus mainly on the effects of style transfer
and self-supervised training. Therefore, we select one of the
SOTA single-shot non-swin-transformer anchor-free object
detectors, YOLOX [Ge et al., 2021], as our baseline archi-
tecture. However, our pre-training pipeline does not depend
on this speciﬁc baseline. Hence it can be applied to any de-
tector.
As discussed in Section 2, COCO [Lin et al., 2014],
WIDER FACE [Yang et al., 2016], and some of the available
drawing datasets do not include both face and body annota-
tions together. To train the model jointly for both face and
body parts and beneﬁt from all the available datasets, we sep-
arate the detection head of the original YOLOX model into
two pieces. Each piece proposes bounding boxes with their
conﬁdence values only for a single class. Our overall archi-
tecture can be seen in Figure 3. During training, the heads are
trained alternately at each forward pass.
3.2
Stage 1: Style Transferred Pre-Training
Preprocessing.
We process COCO and WIDER FACE
datasets with 11 different styles. We eliminate all the images
in COCO that do not have people or animals. We also count
animals as bodies during training because drawings may in-
clude animal-like characters. To the best of our knowledge,
no dataset includes annotations for animal faces. Thus, fa-
cial training is solely done through human faces in WIDER
FACE. We discard the images in which a person has a face
with its maximum facial side length smaller than ∼2% of the
image’s minimum side length. These faces are not required in
the dataset since characters in drawings mostly have a bigger
appearance on the image.
Training Experiments.
We create 5 different experiments
to test our model’s success at pre-training stage 1:
• Single Styles: We analyze the effect of each style on
the detection performance by training individual models
with only one style transferring method.
• All Styles: We train an additional model by combin-
ing all styles with random selection per each image to
notice if using multiple styles increases the overall per-
formance.
• Best Styles:
We choose ﬁve styles that result in
the greatest performance individually and train another
model by combining only these to ﬁnd if selecting the
most effective styles is more logical instead of utilizing
all styles.
• No Style: We train an extra model that uses the original
images without any stylization to observe the beneﬁt of
style transferring.
• No Animals Included: We test the effect of including
animal bodies to body annotations to the performance.
We utilize all of the styles but exclude the animal boxes
from the training data.
3.3
Stage 2: Self-Supervised Pre-Training
Model Architecture.
The model consists of two different
network parts: teacher and student. These networks are iden-
tical and initialized from the same pre-trained set of weights
that we obtain from stage 1: style transferred pre-training
with the mixture of all styles. The teacher network processes
a non-augmented complete image and generates bounding
box predictions along with their conﬁdence values. The stu-
dent network also generates predictions, but it processes a
heavily augmented version of the same input image. High-
conﬁdence predictions of the teacher network are further pro-
cessed with the non-maximum suppression (NMS) algorithm,
and the outputs are considered as the pseudo-ground-truth la-
bels of the image. The student network is trained with the
loss computed by using the labels retrieved from the teacher
network. The gradient ﬂow of the teacher network is stopped,
and it is updated at each iteration with respect to the Eq. 1,
where TN is the teacher, SN is the student network weight,
d is a hyper-parameter:
TN = d · TN + (1 −d) · SN
(1)
### Page 4

DarkNet 53
Image
(H0 x W0 x 3)
P5
(H3 x W3 x 256)
P4
(H2 x W2 x 256)
P3
(H1 x W1 x 256)
Face Det. 
Head
Body Det. 
Head
Face Det. 
Head
Body Det. 
Head
Face Det. 
Head
Body Det. 
Head
1 x 1 conv.
 two 3 x 3 conv.
inputs & outputs
Detection Head
P
(H x W x 256)
Confidences
(H x W x 1)
Box Areas
(H x W x 3)
Figure 3: Our complete model architecture.
Although TN is updated with the student weights in earlier
studies, student weights are only changed with backpropaga-
tion. In our experiments, we have seen that this design causes
the development of both modules at the earlier stages but a
signiﬁcant performance drop in SN in the later iterations due
to the noisy pseudo-ground-truth labels caused by the change
in the input domain between pre-training stage 1 (i.e., car-
toonized natural images) and self-supervised processes (i.e.,
drawings). This drop also affects the performance of TN.
Hence, we load the weights of TN to SN per each Φ itera-
tion to ﬁx the deterioration of SN. Since this step manipu-
lates the values without the gradient ﬂow, an optimizer with
the momentum information may mislead the overall model.
Thus, we change our optimizer to Stochastic Gradient De-
scent (SGD). Our self-supervised architecture can be seen in
Figure 4.
Loss.
In Focal Loss, each prediction is included in the con-
ﬁdence loss calculation with a weight that balances the posi-
tive (i.e., predictions in which the actual ground truth object
is present) and negative (i.e., predictions that point to a back-
ground area) boxes. This approach is advantageous in fully
supervised training since the ground truth box areas of every
object in the image are given to the model. On the other hand,
in self-supervised detectors, the high-probability predictions
of the teacher model are selected as pseudo-ground-truth val-
ues, which are prone to false positives (FP) and false nega-
tives (FN). FP cases can be minimized by increasing the con-
ﬁdence threshold for ground truth selection. However, this
choice also increases the FN rate. To further decrease the FN
cases, we follow the OHEM loss [Shrivastava et al., 2016],
where only a subset of predictions are chosen to calculate the
loss. We also modify this loss so that the predictions can be
selected as positive predictions only above a speciﬁc conﬁ-
dence threshold and negative predictions below a particular
threshold.
Subset selection and this modiﬁcation help the
model to skip a subset of FN cases of the teacher model in
loss calculations (e.g., if a face/body area is predicted but has
a low conﬁdence value). Loss calculation of a single selected
box proposal can be seen in Eq. 2:
Lconf = −p · ctpos · log(ˆp) −(1 −p) · ctneg · log(1 −ˆp)
Lreg =
{w,h,x,y}
X
i
smoothL1(igt, ipred)
Ltotal = Lconf + βLreg
(2)
Lconf is the conﬁdence loss and Lreg is the regression loss.
p ∈{0, 1} indicates if the box is selected as positive (p = 1)
or negative (p = 0), ˆp ∈[0, 1] is the conﬁdence value of
the selected box, ctpos ∈{0, 1} is 1 if the conﬁdence of
the proposed box is above the positive conﬁdence threshold,
ctneg ∈{0, 1} is 1 if the conﬁdence of the proposed box is
below the negative conﬁdence threshold, {w, h, x, y} are the
width, height, and the center points of the box, β is the bal-
ancing parameter between conﬁdence and regression losses.
Unlabeled Datasets.
We crawled 195,321 comic book
pages from today’s US and European series to train our
model. We also utilized 198,657 pages from COMICS and
leveraged iCartoonFace, Manga 109 pages, Comic2k, Water-
color2k, and Clipart1k images. At each forward pass, we se-
lect a random image from these image sets.
Experiments & Hyper-parameters.
We run several exper-
iments with different losses, Φ, β, d, positive and negative
student conﬁdence thresholds. In our ﬁnal model, we set Φ to
500, β to 2, d to 0.9996, and positive and negative thresholds
(ctthres
pos
and ctthres
neg ) to 0.5.
3.4
Stage 3: Fine-Tuning
We conduct experiments with three different pre-training
methods: random initialization, style transferred pre-training
in stage 1, and teacher-student network from stage 2. Since
### Page 5

Horizontal Flip 
 + Gaussian Noise 
 + Color Distortion
 + Random Crop
Teacher Network 
(TN)
Student Network 
(SN)
Pseudo ground truth labels
Student predictions
OHEM LOSS
back
propagation
EMA Update:
TN = d x TN + (1 - d) x SN
Load TN weights to SN per Φ iterations
Figure 4: Our stage 2 teacher-student network training process.
each drawing dataset contains its own separate stylistic dis-
tribution, they should be ﬁne-tuned separately to obtain the
maximum performance on their test set. Thus, we ﬁne-tune
the model with single datasets for each pre-training variation
by randomly selecting a limited number of image instances
(i.e., 64, 128, 256, 512, 1024 images, or all data). As Manga
109 and DCM 772 consist of page images instead of indi-
vidual panels, we separate panels during training to increase
the number of input data and test the models with their page
images.
4
Results & Discussion
In the following parts, we explain our training details, dis-
cuss the effect of style transferring in stage 1, analyze the
experiments done by utilizing the teacher-student network,
and present our results retrieved after ﬁne-tuning with limited
and unlimited drawing data. We will use abbreviations2 of
datasets in the given tables to save space since there are many
datasets for evaluation. Average Precision (AP) is selected
as the evaluation metric for detection, and the intersection of
union value for evaluation is ﬁxed at 0.5. At each table given
in this section, the best result per column is marked in bold
and the second is underlined.
4.1
Training Details
In all variations and experiments, the batch size is set to 16,
and one Tesla T4 GPU is used. AP scores are calculated by
running the same variation ﬁve times and computing the aver-
age of these runs. At stages 1 and 3, the learning rate is ﬁxed
at 0.001. The highest-scoring checkpoints in the evaluation
2iCartoonFace as iCF, Manga 109 faces as M109-F, Manga 109
bodies as M109-B, DCM 772 faces as DCM-F, DCM772 bodies as
DCM-B, Comic2k as C2k, Watercolor2k as W2k, and Clipart1k as
C1k. If Manga 109 is used directly, then it means that the face and
body AP scores are averaged.
set among 350 epochs are chosen as the ﬁnal models. The
ﬁrst and the last 15 epochs include no augmentation. Other-
wise, horizontal & vertical ﬂips, the color distortion between
[−20◦, 20◦] degrees, shear, and mosaic augmentation (i.e.,
combining four random images and passing them as a sin-
gle image) are applied randomly between the 15th and 335th
epochs. For the teacher-student network, the learning rate is
set as 0.0001, and the best checkpoints in 10000 iterations are
taken as ﬁnal models. While the input image of the teacher
network is only horizontally ﬂipped, Gaussian noise, color
distortion, and random crop are applied additionally to the
student network in all epochs.
4.2
Stage 1: Style Transferred Pre-Training
In this stage, we try to ﬁnd the best combination to initialize
the teacher-student network. For this purpose, we train the
model variations with cartoonized natural images but evalu-
ate them with drawing datasets. Scores retrieved after pre-
training stage 1 are given in Table 2 for the individual top-5
styles (i.e., Whitebox, Hosoda, KH, Hayao and Shinkai) and
other experiments.
In the drawing domain, characters can be drawn in vari-
ous styles. Although texture and colors continuously change
among products, key fragments of faces and bodies preserve
their existence (e.g., faces include at least one eye, and bodies
contain either a head, arms, or legs). In our case, we believe
that using multiple styles instead of one forces the model to
focus more on to shape of the object rather than texture. Con-
sequently, the model learns more generalizable information
rather than style-speciﬁc; the objects are detected more accu-
rately when the model is tested with unseen examples. There-
fore, while leveraging even a single style transferring method
from top-5 ensures performance increase compared to using
No Styles, All Styles outperforms both individual styles and
Top-5 Styles. Furthermore, adding animal annotations to the
ground truth during the style transferred pre-training stage
### Page 6

Index
Φ
Loss
ctthres
pos
ctthres
neg
ST
γ
iCF
Manga 109
DCM-B
AP Diff.
1
250
OHEM
0.15
0.85
Yes
0.0
49.10
69.21
77.52
0.12
2
500
OHEM
0.15
0.85
Yes
0.0
49.05
69.32
77.83
0.09
3
1000
OHEM
0.15
0.85
Yes
0.0
48.48
69.02
77.93
0.52
4
Never
OHEM
0.15
0.85
Yes
0.0
47.83
67.68
77.29
1.56
5
500
SimOTA
-
-
Yes
0.0
47.13
65.64
75.42
2.89
6
Never
SimOTA
-
-
Yes
0.0
47.10
65.71
75.48
2.87
7
500
OHEM
0.70
0.30
Yes
0.0
49.14
69.20
77.63
0.10
8
500
OHEM
0.50
0.50
Yes
0.0
49.19
69.32
77.90
0.02
9
500
OHEM
0.30
0.70
Yes
0.0
49.09
69.32
77.90
0.07
10
500
OHEM
0.00
1.00
Yes
0.0
49.22
69.20
77.75
0.06
11
500
OHEM
0.15
0.85
No
0.0
41.66
62.64
75.64
7.12
12
500
OHEM
0.15
0.85
Yes
0.9
48.72
65.72
76.59
2.05
Table 1: AP scores of different stage 2 conﬁgurations in the largest 3 drawing datasets. Φ is the number of iterations where teacher weights
are loaded to student networks afterward, ctthres
pos
is the minimum conﬁdence threshold for the student network prediction to be counted as
positive in ohem loss, ctthres
neg
is the maximum conﬁdence threshold for the student network prediction to be counted as negative in ohem loss.
ST indicates if style transfer is applied in pre-training stage 1, γ is the momentum value that is used in the SGD optimizer (if used, nesterov
SGD is utilized). The “AP Diff.” column is calculated by averaging the maximum score in each dataset minus the experiment score.
Styles
iCF
Manga 109
DCM-B
Hayao
36.53 ± 0.77
35.30 ± 3.66
51.63 ± 4.48
Shinkai
34.88 ± 1.26
36.03 ± 2.33
56.40 ± 1.85
Hosoda
38.81 ± 0.40
43.05 ± 0.96
54.63 ± 3.13
KH
37.69 ± 0.62
36.39 ± 1.43
49.10 ± 1.41
Whitebox
42.22 ± 1.49
45.86 ± 1.93
52.46 ± 2.23
No Styles
33.00 ± 1.97
35.57 ± 2.82
58.94 ± 3.75
Top-5 Styles
42.04 ± 1.41
47.90 ± 2.61
59.96 ± 1.82
No Animals
42.31 ± 0.70
44.81 ± 1.30
62.85 ± 1.16
All Styles
42.50 ± 1.25
48.73 ± 2.60
65.46 ± 1.35
Table 2: AP scores after stage 1 in the largest 3 drawing datasets.
pushes the performance even further.
4.3
Stage 2: Self-supervised Pre-Training
In this Section, we discuss all of our experiments in the
self-supervised stage.
We will refer to Table 1 for the
additional student network (SN) update interval (Φ), loss se-
lection, positive (cthold
pos ) and negative (cthold
neg ) SN conﬁdence
thresholds, usage of momentum in the optimizer (γ), and for
highlighting the importance of style transferring before the
self-supervised stage (ST).
Loss.
In experiments 2, 4, 5, and 6, our modiﬁed OHEM
loss is compared with the SimOTA loss, which is the de-
fault loss method in YOLOX and an advanced variation of
Focal loss. We believe that selecting a subset of predictions
for backpropagation reduces the amount of misleading in FP
and FN cases. Our results also validate that OHEM loss is
more suitable for our self-supervised architecture. Models
with OHEM loss outperform others with up to ∼2.8 AP dif-
ference.
Updating SN per Φ Iterations.
Between experiments 1
and 4, we try various iteration counts for Φ. We observe that
the overall performance drops if Φ > 500. The score is worst
if there is no manual SN update (i.e., Φ = None).
Student Conﬁdence Thresholds (cthold
pos
and cthold
neg ).
We
test the inﬂuence of positive and negative SN conﬁdence
thresholds in experiments 2 and 7-10. With a threshold start-
ing from too high for positive and too low for negative (exp.
7), the average performance is lower than the others. While
the original OHEM loss corresponds to exp. 10, adding ad-
ditional thresholds for SN results in greater or similar scores
(e.g., experiments 8 and 9). The best performance is obtained
by setting both cthold
pos
and cthold
neg
to 0.5.
Optimizer Selection.
Our study states that manually
changing SN’s weights with TN’s may mislead the overall
model if an optimizer with momentum is utilized. To test
our statement, we train two models with the same hyper-
parameter conﬁgurations but select standard SGD in one and
Nesterov SGD in the other (exp. 2 and 12). In almost every
dataset, standard SGD scores ∼1.5 −2% higher.
Style Transferring Before Self-supervised Stage 2.
We
investigate if style transferring is needed in stage 1 before ap-
plying self-supervised stage 2. We train two models with the
same settings but initialize the pre-trained weights of these
models in the teacher-student stage differently: one with the
weights retrieved from pre-training stage 1, including style
transferring, the other without style transferring (exp. 2 and
11). Overall, AP difference is ∼7%. Hence, applying style
transferring in stage 1 has a signiﬁcant positive effect on the
self-supervised stage 2 model performance.
4.4
Stage 3: Fine-Tuning
We train our architecture for single datasets with limited in-
stances to evaluate their behavior when only a low amount
### Page 7

Types
Models
iCF
M109-F
DCM-F
M109-B
DCM-B
C2k
W2k
C1k
NS
All Styles
42.50
54.74
69.93
42.72
65.46
56.80
67.36
55.65
SS
Teacher-Student
49.19
69.25
82.45
69.38
77.90
67.41
71.53
64.25
SS
UMT [Deng et al., 2020]
-
-
-
-
-
-
69.90
70.50
SS
D-adapt [Jiang et al., 2022]
-
-
-
-
-
53.50
68.90
69.30
WS
Inoue et al. [Inoue et al., 2018]
-
-
-
36.71*
41.89*
57.30
73.20
63.00
WS
H2FA R-CNN [Xu et al., 2022]
-
-
-
-
-
66.80
73.80
75.70
FS
Train w/ 64 Images **
65.47
80.41
69.80
77.72
77.28
68.36
71.24
58.74
FS
Train w/ 256 Images **
71.24
84.20
73.72
80.79
80.91
69.96
73.83
65.18
FS
Train w/ 512 Images **
74.39
85.15
74.85
82.32
82.40
71.05
77.63
-
FS
Train w/ All Images **
87.75
87.86
75.87
87.06
84.89
71.66
89.17
77.97
FS
XL Model w/ All Images **
90.01
87.88
77.40
87.98
86.14
73.65
89.81
83.59
FS
ACFD [Zhang et al., 2020a]
90.94
-
-
-
-
-
-
-
FS
Ogawa et al. [Ogawa et al., 2018]
-
76.20
-
79.60
-
-
-
-
FS
Nguyen et al. [Nguyen et al., 2018]
-
-
74.94
-
76.76
-
-
-
FS
Inoue et al. [Inoue et al., 2018]
-
-
-
-
-
70.10
77.30
76.20
Table 3: Overall AP performances of our models and previous SOTA models. Our models are titled in italic. The teacher-student network is
initialized with the style transferred pre-training, All of our supervised models are initialized with pre-training stage 2 weights. NS: no target
domain supervision. SS: self-supervision, WS: weak-supervision, FS: full target domain supervision. Scores with ”*” mean that they are
evaluated by us using the model from the original project repository. ”**” indicates that the results are retrieved from single-dataset trainings
and each score is calculated by a separate model trained speciﬁcally with the particular dataset.
Image Instance Counts
Pre-training
64
512
All
None
47.79 ± 1.38
69.38 ± 0.82
80.60 ± 0.65
Stage 1
66.90 ± 1.40
75.34 ± 0.99
82.87 ± 1.53
Stage 1 + 2
71.13 ± 0.92
77.44 ± 0.47
82.78 ± 0.93
Table 4: Average AP performance of our model when trained with a
subset of individual datasets having annotations of a limited number
of random images. Average is calculated by taking the mean of each
score retrieved from each 6 datasets.
of data is available. The average of scores for all datasets
(i.e., iCartoonFace, Manga 109, DCM 772, Comic2k, Wa-
tercolor2, Clipart 1k) are shared in Table 4.
In the cases
with extremely low instance counts (i.e., 64 and 512 im-
ages), utilization of natural images and self-supervised learn-
ing results in up to ∼24% performance increase compared
to starting from a random initial state. When trained with
all available data, both style-transferring-based and teacher-
student-based pre-training methods score similar values. We
believe this is caused since there is sufﬁcient data for these
speciﬁc sub-domains to close the gap that emerged from the
self-supervised stage. However, we still obtain a signiﬁcant
improvement (∼2.2%) when models start from pre-trained
weights instead of random initialization.
This shows that
leveraging style transferred pre-training enhances the perfor-
mance independently from the amount of labeled ﬁne-tuning
data.
In Table 3, we compare previous SOTA models with our re-
sults from each stage checkpoint (i.e., style transfer, teacher-
student, ﬁne-tuning with individual datasets).
Our model
achieves close scores to ACFD [Zhang et al., 2020a] and out-
performs other SOTA models. Even with a low amount of
training images, we obtain better or comparable results with
[Nguyen et al., 2018] and [Ogawa et al., 2018]. Increasing
the model size from the tiny version of YOLOX to the XL
version also results in a further performance increase. Our XL
model dominates our tiny version in each individual dataset.
5
Conclusion
In this study, we work on efﬁcient pre-training for face and
body detection models in drawings. First of all, we intro-
duce a self-supervised teacher-student network to the domain
of drawings. We propose a modiﬁed OHEM loss to over-
come the false-negative cases caused by the teacher network
and equalize the student network’s weights to the teacher net-
work’s per 500 iterations to prevent distortions in the student
network.
By leveraging the existing style-transferring methods, we
highlight the importance of using pre-trained weights for the
domain adaptation task and the positive effects of using style-
transfer on the pre-training data. Additionally, we analyze
the individual impacts of the variations and show that using
multiple style-transferring variations together provides higher
performance.
Lastly, we train fully supervised models with limited and
available labeled data, where the models are initialized with
the pre-trained weights. Even with limited drawing data, our
model obtains the new SOTA score in most drawing datasets
when pre-trained with our pipeline. This ﬁnding indicates
that efﬁcient pre-training is an important aspect where a low
amount of data is available, and the teacher-student network
is an effective way of pre-training.
### Page 8

References
[Bochkovskiy et al., 2020] Alexey Bochkovskiy, Chien-Yao
Wang, and Hong-Yuan Mark Liao. Yolov4: Optimal speed
and accuracy of object detection, 2020.
[Brumm et al., 2021] Adam Brumm, Adhi Agus Oktaviana,
Basran Burhan, Budianto Hakim, Rustan Lebe, Jian-xin
Zhao, Priyatno Hadi Sulistyarto, Marlon Ririmasse, Shi-
natria Adhityatama, Iwan Sumantri, et al.
Oldest cave
art found in sulawesi. Science Advances, 7(3):eabd4648,
2021.
[Cai et al., 2019] Qi Cai, Yingwei Pan, Chong-Wah Ngo,
Xinmei Tian, Lingyu Duan, and Ting Yao. Exploring ob-
ject relation in mean teacher for cross-domain detection,
2019.
[Chen et al., 2018] Yang Chen, Yu-Kun Lai, and Yong-Jin
Liu.
Cartoongan: Generative adversarial networks for
photo cartoonization. In Proceedings of the IEEE confer-
ence on computer vision and pattern recognition, pages
9465–9474, 2018.
[Deng et al., 2020] Jinhong Deng, Wen Li, Yuhua Chen, and
Lixin Duan. Unbiased mean teacher for cross-domain ob-
ject detection, 2020.
[Ge et al., 2021] Zheng Ge, Songtao Liu, Feng Wang, Zem-
ing Li, and Jian Sun.
Yolox: Exceeding yolo series in
2021. arXiv preprint arXiv:2107.08430, 2021.
[Hicsonmez et al., 2020] Samet Hicsonmez, Nermin Samet,
Emre Akbas, and Pinar Duygulu. GANILLA: generative
adversarial networks for image to illustration translation.
CoRR, abs/2002.05638, 2020.
[Inoue et al., 2018] Naoto Inoue, Ryosuke Furuta, Toshihiko
Yamasaki, and Kiyoharu Aizawa. Cross-domain weakly-
supervised object detection through progressive domain
adaptation, 2018.
[Iyyer et al., 2017] Mohit Iyyer, Varun Manjunatha, Anu-
pam Guha, Yogarshi Vyas, Jordan Boyd-Graber, Hal
Daum´e III au2, and Larry Davis. The amazing mysteries
of the gutter: Drawing inferences between panels in comic
book narratives, 2017.
[Jiang et al., 2022] Junguang Jiang, Baixu Chen, Jianmin
Wang, and Mingsheng Long. Decoupled adaptation for
cross-domain object detection. In International Confer-
ence on Learning Representations, 2022.
[Lin et al., 2014] Tsung-Yi Lin, Michael Maire, Serge Be-
longie, James Hays, Pietro Perona, Deva Ramanan, Piotr
Doll´ar, and C Lawrence Zitnick. Microsoft coco: Com-
mon objects in context. In European conference on com-
puter vision, pages 740–755. Springer, 2014.
[Liu et al., 2021] Yen-Cheng Liu, Chih-Yao Ma, Zijian He,
Chia-Wen Kuo, Kan Chen, Peizhao Zhang, Bichen Wu,
Zsolt Kira, and Peter Vajda. Unbiased teacher for semi-
supervised object detection, 2021.
[Matsui et al., 2017] Yusuke Matsui, Kota Ito, Yuji Aramaki,
Azuma Fujimoto, Toru Ogawa, Toshihiko Yamasaki, and
Kiyoharu Aizawa.
Sketch-based manga retrieval using
manga109 dataset.
Multimedia Tools and Applications,
76(20):21811–21838, 2017.
[Nguyen et al., 2018] Nhu-Van Nguyen, Christophe Rigaud,
and Jean-Christophe Burie. Digital comics image indexing
based on deep learning. Journal of Imaging, 4(7), 2018.
[Ogawa et al., 2018] Toru Ogawa,
Atsushi Otsubo,
Rei
Narita, Yusuke Matsui, Toshihiko Yamasaki, and Kiyoharu
Aizawa. Object detection for comics using manga109 an-
notations, 2018.
[Shrivastava et al., 2016] Abhinav
Shrivastava,
Abhinav
Gupta, and Ross Girshick. Training region-based object
detectors with online hard example mining, 2016.
[Wang and Yu, 2020] Xinrui Wang and Jinze Yu. Learning
to cartoonize using white-box cartoon representations. In
IEEE/CVF Conference on Computer Vision and Pattern
Recognition (CVPR), June 2020.
[Xu et al., 2021] Mengde Xu, Zheng Zhang, Han Hu, Jian-
feng Wang, Lijuan Wang, Fangyun Wei, Xiang Bai, and
Zicheng Liu. End-to-end semi-supervised object detection
with soft teacher. Proceedings of the IEEE/CVF Interna-
tional Conference on Computer Vision (ICCV), 2021.
[Xu et al., 2022] Yunqiu Xu, Yifan Sun, Zongxin Yang, Ji-
axu Miao, and Yi Yang. H2FA R-CNN: Holistic and hi-
erarchical feature alignment for cross-domain weakly su-
pervised object detection. In Proceedings of IEEE/CVF
Conference on Computer Vision and Pattern Recognition
(CVPR), pages 14329–14339, 2022.
[Yang et al., 2016] Shuo Yang, Ping Luo, Chen Change Loy,
and Xiaoou Tang. Wider face: A face detection bench-
mark. In IEEE Conference on Computer Vision and Pat-
tern Recognition (CVPR), 2016.
[Zhang et al., 2020a] Bin Zhang, Jian Li, Yabiao Wang,
Zhipeng Cui, Yili Xia, Chengjie Wang, Jilin Li, and Feiyue
Huang. Acfd: Asymmetric cartoon face detector, 2020.
[Zhang et al., 2020b] Hongkai Zhang, Hong Chang, Bing-
peng Ma, Naiyan Wang, and Xilin Chen.
Dynamic R-
CNN: Towards high quality object detection via dynamic
training. In ECCV, 2020.
[Zheng et al., 2020] Yi Zheng, Yifan Zhao, Mengyuan Ren,
He Yan, Xiangju Lu, Junhui Liu, and Jia Li. Cartoon face
recognition: A benchmark dataset. In Proceedings of the
28th ACM International Conference on Multimedia, pages
2264–2272, 2020.
[Zhu et al., 2017] Jun-Yan Zhu, Taesung Park, Phillip Isola,
and Alexei A Efros. Unpaired image-to-image translation
using cycle-consistent adversarial networks. In Computer
Vision (ICCV), 2017 IEEE International Conference on,
2017.
### Page 9

6
Supplementary Material
In this section, we provide additional explanations on our
task, release the extended versions of our experiment tables,
and discuss these results. We use abbreviations of datasets in
the given tables to save space since there are many datasets for
evaluation (iCartoonFace as iCF, Manga 109 faces as M109-
F, Manga 109 bodies as M109-B, DCM 772 faces as DCM-F,
DCM772 bodies as DCM-B, Comic2k as C2k, Watercolor2k
as W2k, and Clipart1k as C1k). Average Precision (AP) is
selected as the evaluation metric for detection, and the in-
tersection of union value for evaluation is ﬁxed at 0.5. AP
scores are calculated by running the same variation ﬁve times
and computing the average of these runs. At each table given
in this section, the best result per column is marked in bold
and the second is underlined if otherwise is not speciﬁed in
the table explanation.
6.1
More on the Applications in Real World
Drawings are a multi-modal medium for communication. In
drawings, stories and thoughts are transmitted mainly through
the characters in the scene. Thus, detecting and analyzing
faces and bodies are important preliminary tasks for under-
standing drawings. Through detection, we can process char-
acter data to reach the actions, relations, and emotions in the
scene, which may lead to reasoning tasks in the next step. By
generating a model-aided face and body dataset, we can train
generative models for face and character synthesis, face ma-
nipulation, real-face-to-drawing-face conversion, etc., which
may further help with productization (e.g., animation, comic
books, anime, digital art creation) and interfaces for that pur-
pose. A good detector model enables us to perform higher-
level tasks in future works. With this motivation, we focus on
the detection task and on drawings as our domain in general.
However, our design in stage 2 can be adapted to other do-
main adaptation or generalization studies if a teacher-student-
like self-supervised network is utilized.
6.2
Results of All Style Transfer Variations
In the main paper, top-5-scoring style transferring variations
are shared. In Table 5, you can see performances with the
other 6 variations as well. You can also see the visual ef-
fect of each style in Figure 5. Although cartoonization meth-
ods convert natural images to drawing-like images, they also
cause the deterioration of ﬁne details in the images. For the
cases where variations result in a worse performance than the
non-style-transferred version (i.e., No Styles), we observe that
these variations are not only inferior in the cartoonization of
humans but also cause a decrease in the quality of the image.
Thus, utilizing only these variations provides a worse score
than no style-transferring.
6.3
Additional Experiments on Self-Supervised
Teacher-Student Network
In Table 6, complete hyper-parameter testing process for
stage-2 is given. Since the effects of Φ, ctthres
pos , ctthres
neg , ST,
and γ are investigated in the main paper, this section will ana-
lyze different values of d (i.e., EMA keep rate), β (i.e., coefﬁ-
cient of regression loss), and cteac (i.e., minimum conﬁdence
threshold for the student network prediction to be counted as
positive in OHEM loss). Moreover, the effect of Φ in the
training curve will also be discussed.
- EMA Keep Rate (d)
In the previous self-supervised detection studies, it has
been shown that rates below 0.999 result in a worse per-
formance.
Therefore, we limit our rate range to d
∈
{0.999, 0.9992, 0.9996, 0.9998, 0.9999}. Experiments 2, 9,
10, 11, and 12 contain the model performances with different
d values. While we achieve the greatest average performance
with d = 0.9996, we obtain similar scores with all values
except 0.9999.
- Teacher Conﬁdence Threshold (cteac)
Stage 2 performance may also signiﬁcantly change based on
different conﬁdence limits for selecting a TN prediction as a
pseudo-ground-truth box. Between 2th and 22-25th experi-
ments, we analyze how different teacher conﬁdence thresh-
olds change the AP result.
Among the 5 values we set,
cteac = 0.65 gives the best average AP score among the
datasets we evaluate. The outcomes are slightly worse for
the values smaller or larger than 0.65. However, the model is
not too sensitive to this threshold since the AP Difference is
only 0.02 for 0.5 and 0.7.
- Regression Loss Coefﬁcient (β)
Between experiments 2 and 13-16, our model’s dependence
on β is investigated. Although the model is not extra sen-
sitive to differing β values, the most suitable values for this
parameter are 2 and 4.
- Training Curve Analysis (Φ)
In Figure 6, developments of teacher and student networks
for 3 different datasets (i.e., iCartoonFace, Manga 109, and
Comic 2k) are given.
While the y-axis provides the AP
scores, the x-axis corresponds to the total training iteration
count. As seen in the graphs, in each dataset, the teacher
network curve increases more steadily for a longer interval if
Φ = 500. Moreover, this setting achieves higher AP scores in
iCartoonFace and Manga 109, the two largest and most qual-
itative labeled drawing datasets. This indicates that setting
student network weights with teachers per Φ = 500 iteration
results in more stable training and better performance.
6.4
Stylistic Domain Coverage of Individual
Datasets
In our paper, we express that the labeled drawing data only
covers a small subset of the overall domain in terms of stylis-
tic variety. To analyze the stylistic coverage of individual
datasets, we design an experiment where the models, that are
ﬁne-tuned on a single labeled dataset with a limited number
of instances, are evaluated on the other annotated datasets
(e.g., if our model is ﬁne-tuned in iCartoonFace, then we
also evaluate that model in Manga 109 and DCM 772 faces).
By comparing these results, we can infer how valuable each
dataset is in other unseen styles/sub-domains. To prevent our
model from being affected by other datasets, we will base our
statements on the randomly initialized ﬁne-tuning in the Ta-
ble 7 (i.e., the columns titled with N) during our analysis if
no other pre-training is mentioned.
### Page 10

Monet
Van Gogh
Cezanne
Shinkai
Hayao
Hosoda
Paprika
AS
KH
Miyazaki
Whitebox
Wider
Face
C
O
C
O
Figure 5: Example results from the Style transfer variations in single WIDER FACE and COCO images.
Styles
iCF
M109-F
DCM-F
M109-B
DCM-B
C2k
W2k
C1k
Hayao
36.53 ± 0.77
42.34 ± 3.44 63.43 ± 1.44 28.25 ± 3.88 51.63 ± 4.48
47.88 ± 1.11
61.38 ±0.97
49.07 ±1.28
Shinkai
34.88 ± 1.26
41.21 ± 2.64 57.56 ± 3.11 30.84 ± 2.01 56.40 ± 1.85
48.21 ± 1.15
60.26 ±1.21
50.47 ±0.65
Hosoda
38.81 ± 0.40
49.59 ± 0.85 60.35 ± 3.13 36.50 ± 1.07 54.63 ± 3.13
51.12 ± 0.90
62.52 ±0.67
53.58 ±1.22
Paprika
32.27 ± 0.66
32.16 ± 4.17 50.95 ± 3.39 21.69 ± 1.84 40.40 ± 3.09
40.50 ± 1.64
47.96 ±2.43
40.46 ±1.58
Van Gogh
33.31 ± 1.66
35.30 ± 1.80 62.73 ± 1.30 26.09 ± 2.42 50.80 ± 2.56
44.66 ± 1.87
58.38 ±1.16
46.18 ±1.68
Monet
26.25 ± 2.98
30.44 ± 3.06 58.89 ± 4.06 21.13 ± 2.98 50.96 ± 1.54
39.31 ± 1.81
58.84 ±1.43
44.62 ±2.13
Cezanne
29.96 ± 0.76
35.49 ± 2.64 59.10 ± 2.59 26.76 ± 3.05 46.22 ± 8.25
41.50 ± 4.16
52.04 ±8.21
42.12 ±4.08
Miyazaki
32.16 ± 1.62
38.39 ± 0.94 59.63 ± 2.52 28.31 ± 1.53 55.91 ± 2.23
42.78 ± 0.29
61.31 ±0.45
47.83 ±1.71
AS
35.34 ± 0.94
39.81 ± 2.83 57.09 ± 0.66 27.01 ± 1.34 52.23 ± 2.19
44.79 ± 1.81
60.81 ±0.64
47.34 ±0.69
KH
37.69 ± 0.62
44.18 ± 2.20 59.68 ± 2.97 28.59 ± 0.65 49.10 ± 1.41
49.04 ± 1.14
63.51 ±1.00
50.34 ±0.73
Whitebox
42.22 ± 1.49
53.10 ± 2.12 59.63 ± 3.93 38.61 ± 1.73 52.46 ± 2.23
52.41 ± 1.25
63.35 ±0.41
54.56 ±1.64
No Styles
33.00 ± 1.97
40.44 ± 3.04 59.63 ± 3.83 30.69 ± 2.59 58.94 ± 3.75
44.81 ± 1.05
61.88 ± 0.95
49.60 ± 1.20
Top-5 Styles 42.04 ± 1.41
53.82 ± 3.28 65.94 ± 2.71 41.98 ± 1.94 59.96 ± 1.82
55.36 ± 1.56
66.91 ± 0.89
55.99 ± 0.73
No Animals
42.31 ± 0.70
52.09 ± 1.73 69.70 ± 2.26 37.53 ± 0.87 62.85 ± 1.16
54.58 ± 0.51
67.97 ± 0.24
58.37 ± 0.64
All Styles
42.50 ± 1.25
54.74 ± 2.20 69.93 ± 2.67 42.72 ± 3.00 65.46 ± 1.35
56.80 ± 1.42
67.36 ± 0.39
55.65 ± 0.87
Table 5: AP performances of our model after pre-training stage 1 for different style transferring variations: with single style transferring
variation is selected, no style is selected, top-5 best-performing styles are combined, all styles are combined but no animal annotations are
included, all styles are combined and animal annotations are also included.
In
the
following
parts,
we
will
use
the
notation
train dataeval data
number of images to mention the models and their
results (e.g., if a model is trained in iCartoonFace with 64 im-
ages and evaluated on DCM faces, then the notation will be
icf dcm
64
).
- In Face Data
In facial analysis, we observe that our ﬁne-tuned models
with iCartoonFace and Manga 109 perform better in other
datasets than the variations with DCM 772. In both iCar-
toonFace and Manga 109, when trained with one dataset
(i.e., source sub-domain) and evaluated on the other (i.e., tar-
get sub-domain), using 1024 images from the source sub-
domain is almost equal to utilizing 128 images from the
target sub-domain for training (i.e., icf m109
1024
≈m109m109
128
and m109icf
1024 ≈icf icf
128).
If all instances are allowed to
be leveraged, this equality changes to All & 512 for both.
However, the models trained with DCM 772 obtain signiﬁ-
cantly worse performances in both iCartoonFace and Manga
109 (e.g., dcmicf
All < icf icf
128 and dcmm109
All
≈m109m109
64
).
Lastly, Manga 109 models outperform iCartoonFace models
on DCM 772, if all of the training data are leveraged (i.e.,
m109dcm
All > icf dcm
All ). In conclusion, while DCM 772 is the
worst choice for the unseen sub-domains, both iCartoonFace
and Manga 109 result similarly on the other. However, Manga
109 distinguishes further compared to iCartoonFace due to its
greater score on DCM 772.
- In Body Data
In the case of no pre-training (N), DCM 772 outperforms
C2k* on Manga 109 if the number of images is less than
equal to 256. However, with the increasing data size, both
dataset models result in similar scores. On the other hand,
C2k* outperforms Manga 109 if both dataset models are
evaluated on DCM 772 with the number of instances less
than equal to 1024. Lastly, Manga 109 outperforms DCM
772 on C2k* evaluation if image instances are between 128
and 1024. Therefore, there is no outstanding winner when
no pre-training is applied. Similar results (i.e., no signiﬁ-
cant difference) are also present for other pre-training options
(e.g., m109dcm
1024 > c2k∗dcm
1024 and m109c2k∗
1024 < dcmc2k∗
1024 and
c2k∗m109
1024
> dcmm109
1024 on SS, m109dcm
1024 > c2k∗dcm
1024 and
m109c2k∗
1024 < dcmc2k∗
1024 and c2k∗m109
1024
< dcmm109
1024 on ST).
Only on style transferred pre-training (ST), DCM 773 domi-
nates others with a small gap.
### Page 11

Index
Φ
Loss
d
β
ctthres
pos
ctthres
neg
cteac
ST
γ
iCF
M109-F
DCM-F
M109-B
DCM-B
C2k
W2k
C1k
AP Diff.
1
250
OHEM
0.9996
2
0.15
0.85
0.65
Yes
0.0
49.10
69.14
81.52
69.28
77.52
67.13
71.18
64.63
0.697
2
500
OHEM
0.9996
2
0.15
0.85
0.65
Yes
0.0
49.05
69.23
82.22
69.41
77.83
67.38
71.60
64.12
0.433
3
1000
OHEM
0.9996
2
0.15
0.85
0.65
Yes
0.0
48.48
68.92
82.14
69.11
77.93
67.30
72.18
63.37
0.527
4
2000
OHEM
0.9996
2
0.15
0.85
0.65
Yes
0.0
48.71
68.79
81.91
67.30
77.50
66.79
72.07
63.83
0.954
5
5000
OHEM
0.9996
2
0.15
0.85
0.65
Yes
0.0
48.26
68.55
81.62
67.04
77.30
66.88
72.37
63.23
1.104
6
Never
OHEM
0.9996
2
0.15
0.85
0.65
Yes
0.0
47.83
68.32
81.71
67.03
77.29
67.21
72.33
63.27
1.147
7
500
SimOTA
0.9996
2
-
-
0.65
Yes
0.0
47.13
67.65
82.23
63.62
75.42
65.86
72.55
61.41
2.184
8
Never
SimOTA
0.9996
2
-
-
0.65
Yes
0.0
47.10
67.58
82.19
63.83
75.48
65.96
72.59
61.36
2.146
9
500
OHEM
0.9990
2
0.15
0.85
0.65
Yes
0.0
49.01
69.10
82.21
69.48
77.89
67.24
71.30
64.21
0.503
10
500
OHEM
0.9992
2
0.15
0.85
0.65
Yes
0.0
49.05
69.07
81.95
69.29
77.83
67.25
71.46
64.08
0.550
11
500
OHEM
0.9998
2
0.15
0.85
0.65
Yes
0.0
49.31
69.32
81.74
68.37
77.44
67.23
71.83
64.40
0.644
12
500
OHEM
0.9999
2
0.15
0.85
0.65
Yes
0.0
49.81
68.31
79.28
63.52
75.35
65.67
72.17
64.37
2.234
13
500
OHEM
0.9996
0
0.15
0.85
0.65
Yes
0.0
48.07
68.71
81.65
69.13
77.60
67.02
71.41
64.79
0.880
14
500
OHEM
0.9996
1
0.15
0.85
0.65
Yes
0.0
49.29
69.36
81.64
68.65
77.50
66.97
71.75
65.02
0.656
15
500
OHEM
0.9996
4
0.15
0.85
0.65
Yes
0.0
48.82
69.04
82.44
69.65
77.82
67.55
71.69
63.50
0.391
16
500
OHEM
0.9996
10
0.15
0.85
0.65
Yes
0.0
48.94
69.07
81.71
68.43
77.87
67.31
72.43
63.10
0.570
17
500
OHEM
0.9996
2
0.70
0.30
0.65
Yes
0.0
49.14
69.26
82.13
69.14
77.63
67.41
71.67
64.07
0.481
18
500
OHEM
0.9996
2
0.50
0.50
0.65
Yes
0.0
49.19
69.25
82.45
69.38
77.90
67.41
71.53
64.25
0.377
19
500
OHEM
0.9996
2
0.30
0.70
0.65
Yes
0.0
49.09
69.15
82.08
69.48
77.90
67.37
71.68
64.09
0.429
20
500
OHEM
0.9996
2
0.05
0.95
0.65
Yes
0.0
48.99
69.14
82.33
69.32
78.03
67.31
71.62
63.99
0.430
21
500
OHEM
0.9996
2
0.00
1.00
0.65
Yes
0.0
49.22
69.27
82.12
69.12
77.75
67.40
71.72
64.33
0.450
22
500
OHEM
0.9996
2
0.15
0.85
0.35
Yes
0.0
49.09
69.04
81.70
69.25
77.63
67.27
71.83
64.10
0.563
23
500
OHEM
0.9996
2
0.15
0.85
0.50
Yes
0.0
49.15
69.24
81.50
69.19
77.75
67.45
71.82
64.55
0.521
24
500
OHEM
0.9996
2
0.15
0.85
0.75
Yes
0.0
49.08
69.26
82.51
69.19
77.85
67.26
71.43
64.13
0.453
25
500
OHEM
0.9996
2
0.15
0.85
0.90
Yes
0.0
48.92
69.20
82.76
68.95
77.93
66.93
71.04
63.67
0.575
26
500
OHEM
0.9996
2
0.15
0.85
0.65
Yes
0.9
48.72
67.26
80.10
64.17
76.59
66.81
72.51
62.20
1.941
27
500
OHEM
0.9996
2
0.15
0.85
0.65
No
0.0
41.66
58.96
74.56
66.32
75.64
65.32
69.56
64.13
5.390
Table 6: AP scores of different unsupervised experiment conﬁgurations. Φ: number of iterations where teacher weights are loaded to student
networks afterward, d: ema keep rate, β: coefﬁcient of regression loss, cteac: conﬁdence threshold of teacher network to select a prediction
as pseudo ground truth, ctthres
pos
: minimum conﬁdence threshold for the student network prediction to be counted as positive in OHEM loss,
ctthres
neg : maximum conﬁdence threshold for the student network prediction to be counted as negative in OHEM loss, ST: if style transfer
is applied in stage 1 pre-training, γ: if momentum is used in the optimizer. the “AP Diff.” column is calculated by averaging the maximum
score in each dataset minus the experiment score.
### Page 12

Figure 6: AP curves of teacher and student networks when Φ is 500 and None.
6.5
Effect of Pre-Training on Low and High
Amount of Data
In this Section, we examine the effects of our pre-training
strategies on stage 3 ﬁne-tuning performance. We execute
ﬁne-tuning and evaluation on the same dataset and discuss
the inﬂuence of both low and high amounts of training data.
While pre-training is always advantageous against random
initialization, additional self-supervised pre-training outper-
forms style-transferred pre-training mainly on the small train-
ing data.
Additionally, our pre-training design achieves
higher scores than previous supervised SOTA models, even
with few images. In Table 7, we share the model evaluations
after ﬁne-tuning with single datasets and a limited number of
instances. The scores are underlined if they are greater than
the previous supervised SOTA drawing detectors.
Self-supervised pre-training before ﬁne-tuning improves
detection performance, especially in low amounts of data, but
it is still beneﬁcial for higher data sizes compared to random
initialization. When trained with only 64 images, there is up
to ∼7% difference between initializing with style-transferred
stage 1 weights and self-supervised stage 2 weights. The dif-
ference increases up to ∼35% against random initialization.
On the other hand, if the size of the data increases, the margin
between different initialization methods decreases. But still,
the performance with random initialization on no data limita-
tion is approximately ∼2% worse than self-supervised stage
2 and style transferred stage 1. This indicates that pre-training
is essential for higher performance even with high data.
We obtain better performances than most previous super-
vised SOTAs even with tiny subsets of the datasets during
ﬁne-tuning. 256 panels from Manga 109 are enough to out-
perform the previous SOTA. This changes to 1024 panels in
DCM 772 and 1024 images C2k*. However, we fail to pass
the iCartoonFace SOTA. While we aim to keep the model
size and design more straightforward, the current iCartoon-
Face SOTA (ACFD) is ×5 times larger than our model and
is designed explicitly for the iCartoonFace challenge. Still,
our ﬁnal performance is only ∼3% smaller. This gap de-
creases to 0.93% if our model size changes to the XL version
of YOLOX.
6.6
Visual Results
In Figures 7, 8, and 9 you can see our model’s visual outputs
for sample drawing images from Manga 109, COMICS, and
iCartoonFace. These experiments are conducted with a 0.65
conﬁdence threshold and 0.4 NMS threshold. Overall, mov-
ing from stage 1 to stage 2 weights results in a signiﬁcant
increase in detected areas. However, the false positive pro-
posals also increase with this step. Fine-tuning the model that
is initialized with the stage 2 weights successfully suppresses
these false positive predictions. By increasing the model size,
undetected faces, and bodies are further found.
### Page 13

Evaluation Datasets
Training
# of
iCF
M109-F
DCM-F
Datasets
images
N
ST
SS
N
ST
SS
N
ST
SS
iCF
64
42.29 ± 5.18
61.67 ± 1.27
65.47 ± 0.67
36.40 ± 7.84
66.50 ± 3.68
73.55 ± 1.51
26.97 ± 5.77
52.40 ± 11.38
73.31 ± 3.35
iCF
128
52.18 ± 1.89
64.41 ± 1.05
68.58 ± 0.62
48.78 ± 5.57
69.00 ± 3.91
75.85 ± 1.06
31.13 ± 9.91
59.36 ± 7.81
72.35 ± 4.07
iCF
256
60.87 ± 0.68
69.20 ± 0.91
71.24 ± 0.65
62.25 ± 2.11
74.51 ± 1.88
76.08 ± 0.67
44.11 ± 4.78
60.94 ± 8.46
70.59 ± 1.85
iCF
512
66.22 ± 0.49
72.51 ± 1.38
74.39 ± 0.60
68.97 ± 3.51
75.38 ± 2.59
78.43 ± 1.46
50.91 ± 1.92
58.10 ± 9.41
66.30 ± 5.25
iCF
1024
72.47 ± 0.78
77.22 ± 2.13
77.31 ± 0.30
73.36 ± 2.74
78.36 ± 3.65
80.59 ± 0.47
53.44 ± 3.90
61.43 ± 3.84
67.90 ± 2.87
iCF
All
83.70 ± 0.21
87.61 ± 0.07
87.75 ± 0.02
83.33 ± 0.49
85.62 ± 0.06
85.63 ± 0.13
64.16 ± 0.98
71.98 ± 1.16
72.11 ± 0.41
M109
64
25.28 ± 4.19
47.36 ± 4.06
51.99 ± 3.04
67.46 ± 3.46
77.70 ± 4.05
80.41 ± 1.41
22.60 ± 8.16
54.40 ± 7.13
70.90 ± 3.70
M109
128
34.54 ± 3.29
49.40 ± 1.20
53.47 ± 1.18
74.89 ± 0.82
80.35 ± 0.54
82.14 ± 1.12
35.45 ± 5.18
56.63 ± 5.65
71.02 ± 1.44
M109
256
39.59 ± 3.96
53.11 ± 0.83
56.11 ± 1.97
76.80 ± 0.49
83.35 ± 0.62
84.20 ± 0.68
41.42 ± 10.71
57.83 ± 3.10
71.71 ± 3.12
M109
512
48.55 ± 1.68
58.16 ± 2.48
58.74 ± 1.42
82.98 ± 0.54
85.58 ± 0.61
85.15 ± 0.22
53.83 ± 4.76
63.56 ± 4.02
74.17 ± 1.86
M109
1024
51.41 ± 2.40
60.80 ± 0.95
62.46 ± 0.80
85.83 ± 0.41
86.50 ± 0.27
86.21 ± 0.19
57.74 ± 4.22
67.99 ± 2.21
72.87 ± 1.43
M109
All
66.84 ± 1.56
69.89 ± 0.65
70.71 ± 0.49
87.70 ± 0.05
87.87 ± 0.07
87.86 ± 0.02
77.20 ± 1.66
75.15 ± 1.36
78.40 ± 1.86
DCM
64
13.75 ± 2.13
32.43 ± 4.53
35.14 ± 2.56
32.28 ± 4.83
57.92 ± 4.59
62.15 ± 2.55
57.15 ± 2.20
66.64 ± 3.62
69.80 ± 3.38
DCM
128
19.63 ± 2.87
41.46 ± 3.37
38.38 ± 2.12
39.11 ± 3.06
64.38 ± 1.89
63.96 ± 1.44
67.01 ± 2.12
69.04 ± 5.26
73.78 ± 2.07
DCM
256
23.04 ± 1.41
36.56 ± 2.20
42.73 ± 0.95
49.00 ± 4.13
62.80 ± 3.14
68.25 ± 1.39
68.54 ± 0.93
75.34 ± 1.30
73.72 ± 2.35
DCM
512
29.13 ± 2.90
38.04 ± 2.73
43.93 ± 1.65
55.09 ± 2.46
67.02 ± 2.74
71.50 ± 1.38
71.76 ± 2.48
71.01 ± 2.95
74.85 ± 0.28
DCM
1024
34.78 ± 2.26
44.06 ± 2.09
46.70 ± 0.56
62.53 ± 2.23
71.73 ± 1.69
73.17 ± 0.67
74.66 ± 5.09
78.06 ± 2.89
75.93 ± 0.52
DCM
All
45.01 ± 1.67
47.22 ± 1.55
49.24 ± 0.22
68.17 ± 2.62
72.25 ± 1.01
73.26 ± 0.04
78.27 ± 0.32
79.48 ± 3.48
75.87 ± 2.79
Training
# of
M109-B
DCM-B
C2k*
Datasets
images
N
ST
SS
N
ST
SS
N
ST
SS
M109
64
54.36 ± 4.04
72.52 ± 1.07
77.72 ± 0.74
20.83 ± 5.11
66.94 ± 1.73
74.47 ± 0.38
26.41 ± 6.28
55.98 ± 3.38
62.57 ± 1.61
M109
128
64.18 ± 2.18
75.58 ± 1.25
79.27 ± 0.74
31.44 ± 6.17
66.96 ± 3.80
72.52 ± 2.75
36.91 ± 4.41
58.29 ± 1.69
62.59 ± 1.91
M109
256
71.68 ± 0.54
77.78 ± 0.52
80.79 ± 0.61
36.68 ± 4.07
64.30 ± 4.78
73.13 ± 0.28
44.22 ± 2.35
59.66 ± 1.71
63.08 ± 1.10
M109
512
75.37 ± 0.28
81.63 ± 1.25
82.32 ± 0.24
47.61 ± 2.15
69.46 ± 3.27
74.87 ± 1.20
53.35 ± 1.61
61.74 ± 2.44
64.65 ± 1.07
M109
1024
79.67 ± 1.48
83.32 ± 0.40
83.51 ± 0.35
53.46 ± 3.83
71.34 ± 2.07
76.89 ± 0.68
56.81 ± 1.83
63.96 ± 0.87
66.47 ± 1.46
M109
All
85.78 ± 0.22
87.15 ± 0.04
87.06 ± 0.10
71.27 ± 2.46
75.30 ± 1.13
78.06 ± 1.12
66.39 ± 1.21
69.24 ± 0.93
70.49 ± 0.68
DCM
64
37.51 ± 4.20
62.79 ± 3.71
68.90 ± 1.18
46.55 ± 1.78
71.97 ± 4.72
77.28 ± 1.45
31.60 ± 2.95
58.19 ± 3.87
64.40 ± 1.03
DCM
128
43.57 ± 3.77
66.92 ± 3.57
68.29 ± 1.47
54.80 ± 1.04
76.71 ± 1.94
78.34 ± 0.36
36.67 ± 1.93
60.99 ± 4.36
65.13 ± 0.73
DCM
256
53.20 ± 1.41
66.17 ± 2.76
71.40 ± 1.45
64.63 ± 1.22
79.27 ± 1.03
80.91 ± 1.59
43.77 ± 2.64
60.05 ± 1.96
66.10 ± 0.49
DCM
512
58.32 ± 4.07
70.29 ± 2.42
73.60 ± 0.47
69.93 ± 1.45
80.84 ± 1.44
82.40 ± 0.57
49.96 ± 2.33
62.78 ± 2.10
67.38 ± 0.67
DCM
1024
64.58 ± 0.86
72.00 ± 1.78
74.96 ± 0.51
76.89 ± 1.27
83.31 ± 0.58
83.81 ± 0.43
56.75 ± 1.51
64.57 ± 1.72
68.00 ± 0.69
DCM
All
68.01 ± 1.33
70.42 ± 2.17
70.09 ± 0.39
81.16 ± 0.29
84.66 ± 0.55
84.89 ± 0.20
62.19 ± 1.40
65.67 ± 1.24
65.73 ± 0.63
C2k*
64
31.04 ± 1.96
56.78 ± 4.99
67.94 ± 1.51
24.20 ± 3.34
58.17 ± 3.11
72.52 ± 0.84
41.29 ± 1.84
62.66 ± 1.95
67.59 ± 1.57
C2k*
128
40.02 ± 4.74
62.81 ± 2.46
69.64 ± 2.06
32.06 ± 5.57
65.39 ± 3.61
71.86 ± 2.24
49.83 ± 3.15
66.69 ± 1.38
69.45 ± 1.27
C2k*
256
50.43 ± 3.75
67.76 ± 2.48
72.13 ± 0.74
45.63 ± 1.50
67.12 ± 4.00
73.43 ± 1.48
57.59 ± 2.02
69.21 ± 0.87
70.55 ± 1.32
C2k*
512
58.60 ± 0.52
67.87 ± 1.52
72.53 ± 1.71
54.99 ± 2.37
69.26 ± 4.94
72.92 ± 1.24
64.98 ± 1.77
70.90 ± 0.93
73.82 ± 1.12
C2k*
1024
63.20 ± 1.60
70.78 ± 0.98
75.87 ± 0.41
59.03 ± 0.92
71.03 ± 1.44
76.84 ± 0.65
73.35 ± 1.00
76.19 ± 1.41
76.34 ± 0.55
C2k*
All
68.13 ± 1.84
71.81 ± 0.35
71.57 ± 0.19
67.78 ± 1.99
70.29 ± 0.67
71.10 ± 0.52
76.19 ± 1.32
79.90 ± 0.61
79.93 ± 0.28
Table 7: AP performances of our model after stage 3 ﬁne-tuning when trained with a subset of individual datasets having annotations of
a limited number of random images. c2k* indicates that all Comic2k, Watercolor2k, and Clipart1k datasets are combined for training the
model. N: no pre-training, ST: pre-trained with style transferred images, SS: additional teacher-student pre-training. Underlined if the score
of the evaluated dataset is higher than the previous supervised SOTA detector, and bold if the score is the best for the particular dataset in this
table.
### Page 14

Figure 7: Sample results from Manga 109 pages. Top-left: stage 1 weights, top-right: stage 2 weights, bottom-left: stage 3 weights, bottom-
right: stage 3 XL model weights. Better viewed by zooming.
### Page 15

Figure 8: Sample results from COMICS pages. Left to right: stage 1 weights, stage 2 weights, stage 3 weights, stage 3 XL model weights.
Better viewed by zooming.
Figure 9: Sample results from iCartoonFace. Left to right: stage 1 weights, stage 2 weights, stage 3 weights, stage 3 XL model weights.
Better viewed by zooming.