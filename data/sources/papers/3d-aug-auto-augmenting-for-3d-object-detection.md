# 3D-Aug Auto-Augmenting for 3D Object Detection

**Source**: arxiv PDF, 25 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

arXiv:2210.04166v2  [cs.LG]  3 Jun 2023
Test-time recalibration of conformal predictors under
distribution shift based on unlabeled examples
Fatih Furkan Yilmaz∗and Reinhard Heckel∗,†
∗Dept. of Electrical and Computer Engineering, Rice University
†Dept. of Computer Engineering, Technical University of Munich
Abstract
Modern image classiﬁers are very accurate, but the predictions come without uncertainty
estimates. Conformal predictors provide uncertainty estimates by computing a set of classes
containing the correct class with a user-speciﬁed probability based on the classiﬁer’s probability
estimates. To provide such sets, conformal predictors often estimate a cutoﬀthreshold for the
probability estimates based on a calibration set.
Conformal predictors guarantee reliability
only when the calibration set is from the same distribution as the test set. Therefore, conformal
predictors need to be recalibrated for new distributions. However, in practice, labeled data from
new distributions is rarely available, making calibration infeasible. In this work, we consider the
problem of predicting the cutoﬀthreshold for a new distribution based on unlabeled examples.
While it is impossible in general to guarantee reliability when calibrating based on unlabeled
examples, we propose a method that provides excellent uncertainty estimates under natural
distribution shifts, and provably works for a speciﬁc model of a distribution shift.
1
Introduction
Consider a (black-box) image classiﬁer, typically a deep neural network with a softmax layer at
the end, that is trained to output probability estimates for L classes given an input feature vector
x ∈Rd. Conformal predictors are wrapped around such a classiﬁer and generate a set of classes
that contains the correct label with a user-speciﬁed probability based on the classiﬁer’s probability
estimates.
Let x ∈Rd be a feature vector with associated label y ∈{1, . . . , L}. We say that a set-valued
function C generates valid prediction sets for the distribution P if
P(x,y)∼P [y ∈C(x)] ≥1 −α,
(1)
where 1 −α is the desired coverage level.
Conformal predictors generate valid set generating
functions C for the distribution P by utilizing a calibration set consisting of labeled examples
{(x1, y1), . . . , (xn, yn)} drawn from the distribution P. An important caveat of conformal predic-
tors is that the examples from the calibration set are drawn from the test distribution P.
This assumption is diﬃcult to satisfy in applications and potentially limits the applicability of
conformal prediction methods in practice. In fact, in practice one usually expects a distribution
shift between the calibration set and the examples at inference (or the test set), in which case the
coverage guarantees provided by conformal prediction methods are void. For example, the new
ImageNetV2 test set was created in the same way as the original ImageNet test sets, yet Recht et al.
[Rec+19] found a notable drop in classiﬁcation accuracy for all classiﬁers considered.
Ideally, a conformal predictor is recalibrated on a distribution before testing, otherwise the
coverage guarantees are not valid [Cau+20]. However, in real-world applications, where distribution
shifts are ubiquitous, labeled data from new distributions is scarce or non-existent.
1
### Page 2

We therefore consider the problem of recalibrating a conformal predictor only based on unlabeled
data from the new domain. This is an ill-posed problem: it is in general impossible to calibrate
a conformal predictor based on unlabeled data. Yet, we propose a simple calibration method that
gives excellent performance for a variety of natural distribution shifts.
Organization and contributions.
We start with concrete examples on how conformal predictors
yield miscalibrated uncertainty estimates under natural distribution shifts. We next propose a simple
recalibration method that only uses unlabeled examples from the target distribution.
We show
that our method correctly recalibrates a popular conformal predictor [SLW19] on a theoretical toy
model. We provide empirical results for various natural distribution shifts of ImageNet showing that
recalibrating conformal predictors using our proposed method signiﬁcantly reduces the performance
gap. In certain cases, it even achieves near oracle-level coverage.
Related work.
Several works have considered the robustness of conformal prediction to distri-
bution shift.
Tibshirani et al. [Tib+19] and Park et al. [Par+22] propose methods that assume
a covariate shift and calibrate based on estimating the amount of covariate shift. Podkopaev and
Ramdas [PR21] studies the related, but discrete setting of label shifts between the source and target
domains and proposes a method that is more robust under the label shift setting. In contrast, we
focus on complex image datasets for which covariate shift is not well deﬁned and label shift not
broadly relevant. In Section 5.2, we provide a comparison of our method to the above covariate
shift based methods for a setting where we have access to labeled examples from multiple domains
during training/calibration, one of which correspond to the target distribution.
We are not aware of other works studying calibration of conformal predictors under distribution
shift based on unlabeled examples. However, prior works propose to make conformal predictors
robust to various distribution shifts from the source distribution of the calibration set [Cau+20;
Gen+22], via calibrating the conformal predictor to achieve a desired coverage in the worse case
scenario of the considered distribution shifts. Cauchois et al. [Cau+20] considers covariate shifts
and calibrates the conformal predictor to achieve coverage for the worst-case distribution within
the f-divergence ball of the source distribution.
Gendler et al. [Gen+22] considers adversarial
perturbations as distribution shifts and calibrates a conformal predictor to achieve coverage for the
worst-case distribution obtained through ℓ2-norm bounded adversarial noise.
While making the conformal predictor robust to a range of worst-case distributions at calibra-
tion time allows maintaining coverage under the worst-case distributions, these approaches have
two shortcomings: First, natural distribution shifts are diﬃcult to capture mathematically, and
models like covariate-shifts or adversarial perturbations do not seem to model natural distribution
shifts (such as that from ImageNet to ImageNetV2) accurately. Second, calibrating for a worst-case
scenario results in an overly conservative conformal predictor that tends to yield much higher cover-
age than desired for test distributions that correspond to a less severe shift from the source, which
comes at the cost of reduced eﬃciency (i.e., larger set size, or larger conﬁdence interval length).
In contrast, our method does not compromise the eﬃciency of the conformal predictor on easier
distributions as we recalibrate the conformal predictor for any new dataset.
A related problem is to predict the accuracy of a classiﬁer on new distributions from unlabeled
data sampled from a new distribution [DZ21; CGS21; Jia+22; DGZ21; Gui+21; GBL22]. In partic-
ular, Garg et al. [GBL22] proposed a simple method that achieves state-of-the-art performance in
predicting classiﬁer accuracy across a range of distributions. However, the calibration problem we
2
### Page 3

consider is fundamentally diﬀerent than estimating the accuracy of a classiﬁer. While predicting
the accuracy of the classiﬁer would allow making informed decisions on whether to use the classiﬁer
for a new distribution, it doesn’t provide a solution for recalibration.
2
Background on conformal prediction
Consider a black-box classiﬁer with input feature vector x ∈Rd that outputs a probability estimate
πℓ(x) ∈[0, 1] for each class ℓ= 1, . . . , L. Typically, the classiﬁer is a neural network trained on some
distribution, and the probability estimates are the softmax outputs. We denote the order statistics
of the probability estimates by π(1)(x) ≥π(2)(x) ≥. . . ≥π(L)(x).
Many conformal predictors are based on calibrating on a calibration set DP = {(xi, yi)}n
i=1
to ﬁnd a cutoﬀthreshold [SLW19; RSC20; Ang+20; Bat+21] that achieves the desired empirical
coverage on this set. Here, the superscript P denotes the distribution from which the examples in
the calibration set are sampled from. Given a set-valued function C(x, u, τ) ⊂{1, . . . , L} containing
the set of predicted classes by the conformal predictor, such conformal predictors compute the
threshold parameter τ as
τ ∗= inf {τ : |{i : yi ∈C(xi, ui, τ)}| ≥(1 −α)(n + 1)} ,
(2)
where ui is added randomization to smoothen the cardinality term, chosen independently and uni-
formly from the interval [0, 1], see Vovk et al. [VGS05] on smoothed conformal predictors. Finally,
the ‘+1’ term in the (n + 1) term is a bias correction for the ﬁnite size of the calibration set.
This conformal calibration procedure achieves distributional coverage as deﬁned in the expres-
sion (1), for any set valued function C(x, u, τ) satisfying the nesting property C(x, u, τ1) ⊆C(x, u, τ2)
for τ1 < τ2, see [Ang+20, Thm. 1].
In this paper, we primarily focus on the popular conformal predictors Thresholded Prediction
Sets (TPS) [SLW19] and Adaptive Prediction Sets (APS) Romano et al. [RSC20]. The set generating
functions of the two conformal predictors are
CTPS(x, τ) = {ℓ= 1, . . . , L: πℓ(x) ≥1 −τ} ,
(3)
CAPS(x, u, τ) = {ℓ= 1, . . . , L:
ℓ−1
X
j=1
π(j)(x) + u · π(ℓ)(x) ≤τ},
(4)
with u ∼U(0, 1) for smoothing. The set generating function of TPS doesn’t require smoothing
since each softmax score is independently thresholded and therefore there are no discrete jumps.
Computing the threshold τ through conformal calibration (2) requires a labeled calibration set
from distribution P. We therefore add a superscript to the threshold to designate which distribution
the calibration set set was sampled from; for example τ P indicates that the calibration set was
sampled from the distribution P. The prediction set function CTPS for TPS and CAPS for APS
both satisfy the nesting property. Therefore, TPS and APS calibrated on a calibration set DP by
computing the threshold in the expression (2) is guaranteed to achieve coverage on the distribution
P. However, coverage is only guaranteed if the test distribution Q is the same as the calibration
distribution P.
3
### Page 4

3
Failures under distribution shifts and problem statement
Often we’re most interested in quantifying uncertainty with conformal prediction when we apply a
classiﬁer to new data that might come from a slightly diﬀerent distribution than the distribution
we calibrated on. Yet, conformal predictors only provide coverage guarantees for data coming from
the same distribution as the calibration set, and the coverage guarantees often fail even under
slight distribution shifts. For example, our experiments (see Figure 3) show that APS calibrated on
ImageNet-Val to yield 1−α = 0.9 coverage on the only achieves a coverage of 0.64 on the ImageNet-
Sketch dataset, which consists of sketches of the ImageNet-Val images and hence constitutes a
distribution shift [Wan+19].
Diﬀerent conformal predictors typically have diﬀerent coverage gaps under the same distribution
shift. More eﬃcient conformal predictors (i.e., those that produce smaller prediction sets) tend
to have a larger coverage gap under a distribution shift. For example, both TPS and RAPS (a
generalization of APS proposed by Angelopoulos et al. [Ang+20]) yield smaller conﬁdence sets, but
only achieve a coverage of 0.38 vs. 0.64 for APS on the ImageNet-Sketch distribution shift discussed
above.
Even under more subtle distribution shifts such as subpopulation shifts [STM21], the achieved
coverage can drop signiﬁcantly. For example, APS calibrated to yield 1 −α = 0.9 coverage on the
source distribution of the Living-17 BREEDS dataset only achieves a coverage of 0.68 on the target
distribution. The source and target distributions contain images of exclusively diﬀerent breeds of
animals while the animals’ species is shared as the label [STM21].
Problem statement.
Our goal is to recalibrate a conformal predictor on a new distribution Q
based on unlabeled data. Given an unlabeled dataset DQ = {x1, . . . , xn} sampled from the target
distribution Q, our goal is to provide an accurate estimate ˆτ Q for the threshold τ Q. Recall that the
threshold τ Q is so that the conformal predictor with set function C(x, u, τ Q) achieves the desired
coverage of 1 −α on the target distribution Q. Thus, in other words, our goal is to estimate a
threshold ˆτ Q so that the set C(x, u, ˆτ Q) achieves close to the desired coverage of 1−α on the target
distribution, based on the unlabeled dataset only.
In general, it is impossible to guarantee coverage since conformal prediction relies on exchange-
ability assumptions which can not be guaranteed in practice for new datasets [VGS05; RSC20;
Ang+20; Cau+20; Bat+21]. However, we will see that we can consistently estimate the threshold
τ Q for a variety of natural distribution shifts.
We refer to the diﬀerence between the target coverage of 1−α and the actual coverage achieved
on a given distribution without any recalibration eﬀorts as the coverage gap. We assess how eﬀective
a recalibration method is based on the reduction of the coverage gap after recalibration.
4
Methods
In this section we introduce our calibration method, termed Quantile Thresholded Conﬁdence
(QTC), along with baseline methods we consider in our experiments.
4
### Page 5

DP
α
Conformal
calibration
(2)
τ P
α
x ∼Q
Conformal
inference
(3)
C(x, τ P
α )
QTC
DQ, DP
α
QTC
calibration
(5)
q(D, α)
DP, DQ
QTC
estimate
(7)
ˆβ
Conformal
calibration
(2)
ˆτ Q
α
x ∼Q
Conformal
inference
(3)
C(x, ˆτ Q
α )
Figure 1:
Top: Vanilla conformal prediction. Bottom: QTC recalibration. QTC encapsulates
the conformal calibration process to recalibrate the conformal predictor for each new distribution
without altering the underlying set generating function. DQ is the unlabeled test set and DP is the
labeled training/calibration set. QTC ﬁnds a threshold on the scores of the model on the unlabeled
samples and predicts the coverage level by utilizing how the distribution of the scores changes across
test distribution with respect to this threshold.
4.1
Quantile thresholded conﬁdence
Consider a conformal predictor with threshold τ P
α calibrated so that the conformal predictor achieves
coverage 1 −α on the source distribution P. On a diﬀerent distribution Q the coverage of the
conformal predictor is oﬀ. But there is a value β such that, if we calibrate the conformal predictor
on the source distribution using the value β instead of α, it achieves 1 −α coverage on the target
distribution, i.e., the corresponding thresholds obey τ P
β = τ Q
α .
Our method ﬁrst estimates the value β based on unlabeled examples. From the estimate ˆβ, we
estimate τ Q
α based on computing the threshold τ P
ˆβ by calibrating the conformal predictor on the
source calibration set using ˆβ. This yields a threshold close to the desired one, i.e., τ P
ˆβ ≈τ Q
α .
Step 1, estimation of β:
We are given a labeled source dataset DP and an unlabeled target
dataset DQ. Our estimate of β relies on the quantile function
q(D, c) = inf
(
p:
1
|D|
X
x∈D
1{s(π(x))<p} ≥c
)
.
(5)
The quantile function depends on the classiﬁer’s predictions through a score function s(π(x)) =
maxℓπℓ(x), which we take as the largest softmax score of the classiﬁer’s predictions. Here, D is a
set of unlabeled examples and c ∈[0, 1] is a scalar. Our method ﬁrst identiﬁes a threshold based
on the unlabeled target dataset DQ for a desired coverage level α in expression (5) by computing
q(DQ, α). Since this process is identical to ﬁnding the (α)th quantile of the scores on the dataset,
5
### Page 6

we dub the method Quantile Thresholded Conﬁdence (QTC). QTC estimates β as
βQTC = min(βQTC−T, βQTC−S),
(6)
where the QTC-Target and QTC-Source estimates are
βQTC−T(DQ) =
1
|DP|
X
x∈DP
1{s(π(x))<q(DQ,α)}
(7)
βQTC−S(DQ) = 1 −
1
|DQ|
X
x∈DQ
1{s(π(x))<q(DP ,1−α)}.
(8)
We consider two estimates for β and aggregate them to a single value by taking the minimum of
the two. This yields best performance, as demonstrated by studying the three versions of QTC,
corresponding to the three estimates (6), (7), and (8).
The reasons for having two estimates and aggregating them is as follows. DNNs have a tendency
to be over-conﬁdent in their predictions [Guo+17]. If the distribution of the softmax scores over
the dataset is not suﬃciently smooth in the lower-conﬁdence regime, the QTC-T estimate might be
inaccurate. In this higher-conﬁdence regime QTC-S provides a better estimate. The minimum of
the two provides a good estimate in the high and low conﬁdence regions.
Step 2, estimation of the threshold τ Q
α based on β:
QTC predicts the conformal threshold τ Q
α
by conformal calibration with target value βQTC. Speciﬁcally, we calibrate the conformal predictor
on the dataset DP as
τQTC = inf

τ : |{i : yi ∈C(xi, ui, τ)}| ≥(1 −βQTC)(|DP| + 1)
	
,
(9)
which yields the estimate τQTC for τ Q
α . QTC is illustrated in Figure 1.
QTC is inspired by a method for predicting a classiﬁer’s accuracy from Garg et al. [GBL22].
Garg et al. [GBL22]’s method ﬁnds a threshold on the scores matching the accuracy of a classiﬁer
on the dataset and predicts the accuracy on other datasets. Contrary, we predict the threshold of
a conformal predictor, and our method is based on predicting an auxillary parameter β instead of
a threshold directly.
4.2
Baseline methods
We consider regression-based methods as baselines. Regression-based methods have been used for
predicting classiﬁcation accuracy, assuming a correlation between the classiﬁcation accuracy and
a feature (e.g., average conﬁdence) across diﬀerent distributions [DGZ21; DZ21; Gui+21].
We
consider regression-based methods as baselines for predicting the conformal threshold on a target
distribution that would achieve 1−α coverage. We train the regression-based methods on a dataset
consisting of synthetically generated distributions given a source distribution (e.g. ImageNet-C from
ImageNet) with the goal of predicting the conformal threshold for a test dataset sampled from a
natural distribution.
Let φπ(D): RL →Rd be the feature extractor part of a neural network that maps the softmax
scores of the classiﬁer to the features for a given dataset D. A simple example is the one-dimensional
feature (d = 1) extracted by computing the average conﬁdence of a given classiﬁer across the
examples of a given dataset.
6
### Page 7

We ﬁt a regression function fθ parameterized by diﬀerent feature extractors φπ by minimizing
the mean squared error between the output and the calibrated threshold τ across the distributions
as
ˆθ = arg min
θ
X
j
(fθ(φπ(Dj)) −τ Pj)2.
(10)
We consider the following choices for the feature extractor φπ (see App B for details):
• Average conﬁdence regression (ACR): The average conﬁdence of the classiﬁer across the entire
dataset.
• Diﬀerence of conﬁdence regression (DCR) [Gui+21]: The average conﬁdence of the classiﬁer
across the entire dataset oﬀset by the average conﬁdence on the source dataset. Prediction is
also for the oﬀset target τ −τ P. DCR performs better than ACR for predicting a classiﬁer’s
accuracy [Gui+21].
• Conﬁdence histogram-density regression (CHR): Normalized histogram density of the classiﬁer
conﬁdence across the dataset, where the feature dimension is controlled by a hyperparameter
that determines the number of histogram bins in the probability range [0, 1]. Neural networks
tend to be overconﬁdent in their prediction which heavily skews the histogram densities to
the last bin. We also therefore consider a variant of CHR, dubbed CHR-, where we drop the
last bin of the histogram as a feature.
• Predicted class-wise average conﬁdence regression (PCR): Class-wise (by predicted class) av-
erage conﬁdence of the classiﬁer across the samples.
5
Experiments
We study the performance of QTC on natural distribution shifts and on an artiﬁcal covariate shift.
5.1
Natural distribution shifts
We consider the following choices for the source distribution P and associated natural distribution
shifts:
ImageNet [Den+09] distribution shifts:
In our ImageNet experiments, ImageNet is the source
distribution P and the following natural distribution shifts are the target distributions Q:
• ImageNetV2 [Rec+19] was constructed by following the same procedure as for constructing
and labeling the original ImageNet dataset. However, all standard models perform signiﬁcantly
worse on ImageNetV2 relative to the original ImageNet test set.
• ImageNet-Sketch [Wan+19] contains sketch-like images of the objects in the original Ima-
geNet, but otherwise matches the original categories and scales.
7
### Page 8

ACR
CHR
CHR-
DCR
PCR
QTC-T
QTC-S
QTC
0.81
0.88
0.88
0.88
0.87
0.89
0.89
0.88
0.89
0.9
achieved coverage
ImageNetV2
ACR
CHR
CHR-
DCR
PCR
QTC-T
QTC-S
QTC
0.38
0.65
0.61
0.64
0.66
0.47
0.84
0.8
0.84
0.9
ImageNet Sketch
ACR
CHR
CHR-
DCR
PCR
QTC-T
QTC-S
QTC
0.34
0.56
0.54
0.54
0.57
0.36
0.73
0.75
0.75
0.9
ImageNet-R
ACR
CHR
CHR-
DCR
PCR
QTC-T
QTC-S
QTC
0.61
0.76
0.78
0.78
0.77
0.79
0.81
0.92
0.92
0.9
achieved coverage
Entity-13
ACR
CHR
CHR-
DCR
PCR
QTC-T
QTC-S
QTC
0.57
0.73
0.75
0.74
0.73
0.74
0.79
0.89
0.89
0.9
Entity-30
ACR
CHR
CHR-
DCR
PCR
QTC-T
QTC-S
QTC
0.55
0.7
0.73
0.71
0.7
0.71
0.75
0.93
0.93
0.9
Living-17
Figure 2: Coverage obtained by TPS for a desired coverage of 1−α = 0.9 on the target distribution Q
after recalibration using the unlabeled samples from Q for various recalibration methods. The dotted
line is the coverage without recalibration, and the dashed line is the target coverage 1 −α = 0.9.
QTC almost fully close the coverage gap across ImageNet and BREEDS test distribution shifts.
QTC performs as well as the best of the ablation methods QTC-S and QTC-T, which illustrates
why it is necessary to aggregate the QTC-S and QTC-T estimates for β to a single number as QTC
does.
• ImageNet-R [Hen+21] contains artwork images of the ImageNet class objects found in the
web. ImageNet-R only contains images for a 200-class subset of the original ImageNet. We
don’t limit our experiments to this subset but instead consider the adverse setting of calibrating
on all 1000 classes since our main goal is to provide an end-to-end solution for recalibration
of the conformal predictors and we are interested in how well our method performs against
possible adversaries such as dataset imbalance that can be encountered in practice.
BREEDS [STM21] distribution shifts:
The BREEDS datasets feature sub-population shifts
from the training set to test. The BREEDS datasets were constructed using the existing ImageNet
images, but with diﬀerent classes.
BREEDS utilizes the hierarchical WordNet structure of the
classes to choose a parent class that makes the original ImageNet classes the leaves. For example, in
the BREEDS Living-17 dataset, one of the classes is domestic cat. This is a parent class of several
ImageNet classes, which are tiger cat, Egyptian cat, Persian cat and Siamese cat. BREEDS induces
a subpopulation shift from the source distribution to the target by assigning these leaf classes to
either the source or target. For example, the images in the source dataset of Living-17 under the
domestic cat class are that of either tiger cats or Egyptian cats, whereas in the target are that of
8
### Page 9

0.7
0.8
0.9
1
(TPS)
achieved coverage
ImageNetV2
0.2
0.4
0.6
0.8
1
ImageNet-Sketch
0.2
0.4
0.6
0.8
1
ImageNet-R
y = x
original
QTC
CHR-
0.8
0.9
1
0.7
0.8
0.9
1
desired coverage 1 −α
(APS)
achieved coverage
ImageNetV2
0.8
0.9
1
0.6
0.8
1
desired coverage 1 −α
ImageNet-Sketch
0.8
0.9
1
0.4
0.6
0.8
1
desired coverage 1 −α
ImageNet-R
Figure 3: Coverage obtained by TPS and APS on the target distribution Q as a function of the
desired coverage (i.e., 1 −α) after recalibration with the respective prediction method. For regres-
sion methods, only the best performing method, CHR-, is shown. QTC signiﬁcantly closes the
coverage gap across the range of 1 −α, while CHR- yields inconsistent or insuﬃcient performance
improvements.
either Persian cats or Siamese cats. Therefore, despite having the same label (domestic cat), the
source and target distributions semantically diﬀer due to the diﬀerences between the breeds, which
induces a subpopulation shift.
We consider three BREEDS datasets: Entity-13, Entity-30 and Living-17, which are named
using the convention theme/object type–#classes.
Experimental procedure.
For the ImageNet experiments we use a ResNet-50 and DenseNet-
121 pretrained on the ImageNet training set. For the BREEDS experiments, we train a ResNet-18
model from scratch for the BREEDS datasets. In both cases, the classiﬁers only see examples from
the source distribution.
For all experiments, we ﬁrst calibrate the conformal predictor on the source distribution P to
ﬁnd the cutoﬀthreshold τ P. For QTC and variants, we ﬁnd the threshold q using the expression (5).
For the regression methods, we use the ImageNet-C dataset [HD19] as the source of synthetic distri-
butions, ﬁnd the cutoﬀthreshold τ for each of the distributions, and ﬁt a regressor by minimizing
the loss (10). For the regression function we use a 4-layer MLP with ReLU activations. ImageNet-C
consists of 90 diﬀerent distributions obtained by synthetically perturbing the images of ImageNet-
Val for 18 diﬀerent types of perturbations at 5 diﬀerent levels of severity, resulting in 90 distinct
distributions.
9
### Page 10

Recalibration experiments for a ﬁxed target coverage.
We ﬁrst evaluate the recalibration
methods for a ﬁxed target coverage of 1 −α = 0.9. The results in Figure 2 for recalibrating TPS
show that QTC reduces the coverage gap much more than regression methods, and even closes it
in some cases.
We also display QTC-T and QTC-S as ablation studies. Here it can be seen that sometimes
QTC-T and sometimes QTC-S performs best, which is why combining them is necessary.
The
diﬀerent performance of QTC-T and QTC-S can be attributed to the diﬀerence of the type of shifts
(e.g. semantic vs. subpopulation) between ImageNet and BREEDS. Note that QTC-T operates
on the regime of samples with lower conﬁdence whereas QTC-S on the higher conﬁdence regime.
Therefore, QTC-T may perform subpar compared to QTC-S for datasets consisting of fewer, more
distinct classes like BREEDS, for which a well-trained classiﬁer tends to assign high conﬁdence to
its predictions.
Recalibration experiments for diﬀerent target coverage levels.
The coverage gap (i.e., the
diﬀerence of achieved coverage and targeted coverage) varies across the desired coverage level 1 −α.
We therefore next evaluate the performance as a function of the desired coverage level.
Figure 3 shows the coverage obtained after recalibration with TPS and APS for diﬀerent values
of 1−α for the natural distribution shifts from ImageNet. QTC closes the coverage gap signiﬁcantly
for all choices of 1 −α, whereas the best performing regression-based baseline method, CHR-, fails
to signiﬁcantly improve the coverage gap consistently across all choices of 1 −α.
5.2
Comparison to covariate shift based methods
QTC does not require labeled data from the target distribution at training or inference time. Exist-
ing methods that aim to measure the amount of covariate shift based on unlabeled examples also
improve the robustness of conformal prediction, but rely on labeled examples from the target do-
main [Tib+19; Par+22]. Here, we compare the performance of QTC to that of covariate shift based
methods and show that QTC outperforms the state-of-the-art when labeled data is not available
during training, and performs only marginally worse if labeled data is available.
Under a covariate shift, the conditional distribution of the label y given the feature vector x is
ﬁxed but the marginal distribution of the feature vectors diﬀer:
source:(x, y) ∼P = pP(x) × p(y|x),
target:(x, y) ∼Q = pQ(x) × p(y|x),
where pP(x) and pQ(x) are the marginal PDFs of the features x, and p(y|x) is the conditional PDF
of the label y.
In order to account for a covariate shift, Tibshirani et al. [Tib+19] and Park et al. [Par+22]
utilize an approach called weighted conformal calibration. Weighted conformal calibration uses the
likelihood ratio of the covariate distributions, i.e., the importance weights w(x) = pQ(x)/pP(x) to
weigh the scores used for the set generating function of the conformal predictor for each sample
(x, y) ∈DP
cal. A conformal predictor calibrated on a source calibration set with the true importance
weights for a target distribution is guaranteed to achieve the desired coverage on the target, see Tib-
shirani et al. [Tib+19, Cor. 1]. In practice, the importance weights are not known and are therefore
estimated heuristically.
Covariate shifts is not well deﬁned for complex tasks such as image classiﬁcation. We therefore
follow the experimental setup of Park et al. [Par+22] and consider a backbone ResNet-101 classiﬁer
10
### Page 11

0.6
0.8
1
achieved coverage
P = DomainNetAll
0.4
0.6
0.8
1
P = DomainNetReal
y = x
original
QTC
PS-W
WSCI
0.8
0.9
1
101.5
102
102.5
desired coverage 1 −α
avg. set size
0.8
0.9
1
101
102
desired coverage 1 −α
Figure 4: Coverage (top row) and the average set size (bottom row) obtained by TPS on the
target Q = DomainNet-Infograph for various settings of (1 −α). For the setting where all domains
are available for the discriminator (left), WSCI closes the coverage gap while QTC considerably
improves it; whereas when only DomainNet-Real is available, QTC slightly outperforms. In both
settings, PS-W fails by constructing uninformatively large conﬁdence sets for the range 1 −α > 0.9.
trained using unsupervised domain adaptation based on training sets sampled from both the source
and target distribution as well as an auxillary classiﬁer (discriminator) g that yields probability
estimates of membership between the two for a given sample. For the weighted split conformal
inference (WSCI) method of Tibshirani et al. [Tib+19], we estimate the importance weights using
this discriminator g and for the PAC prediction sets method of Park et al. [Par+22] based on
rejection sampling (PS-W), using histogram density estimation over the probability estimates. We
use TPS as the conformal predictor.
We consider the DomainNet distribution shift problem [Pen+19] and choose DomainNet-Infograph
as the target distribution since the coverage gap is insigniﬁcant for the others (see Park et al.
[Par+22, Table 1]). We consider two scenarios, for both of which all six DomainNet domains, i.e.
DomainNet-Sketch, DomainNet-Clipart, DomainNet-Painting, DomainNet-Quickdraw, DomainNet-
Real, and DomainNet-Infograph, are available during training. In the ﬁrst scenario all domains are
also available at inference, whereas in the second scenario, analogous to the ImageNet setup, we only
have access to the examples from DomainNet-Real (source) and DomainNet-Infograph (target).
The results in Figure 4 show that when the source includes all the domains, WSCI outperforms
other methods. However, when only DomainNet-Real is available for the source at calibration time,
QTC slightly outperforms WSCI. In both settings, PS-W fails if α is chosen such that 1 −α > 0.9,
by constructing uninformatively large conﬁdence sets that tend to contain all possible labels. On the
other hand, QTC and WSCI tend to construct similarly sized conﬁdence sets consistently across
11
### Page 12

the range of 1 −α. Note that while QTC considerably closes the coverage gap in both setups,
QTC-S fails to improve the coverage gap. This might be due to the fact that ResNet-101 trained
with domain adaptation tends to yield very high conﬁdence across all examples. While a separate
discriminator that uses the representations of the ResNet-101 before the fully-connected linear layer
is utilized for the covariate shift based methods, this is not the case for QTC and its variants.
Therefore, the threshold found by QTC-S tends to be very close or even equal to 1.0, hindering the
performance.
6
Theoretical results
We consider a simple binary classiﬁcation distribution shift model from Nagarajan et al. [NAN21]
and Garg et al. [GBL22], and adapt the analysis from Garg et al. [GBL22] to show that recalibrating
provably succeeds within this model. Speciﬁcally, we show that the conformal predictor TPS with
QTC-T yields the desired coverage of 1 −α on the target distribution based on unlabeled examples.
The distribution shift model from Nagarajan et al. [NAN21] is as follows. Consider a binary
classiﬁcation problem with response y ∈{−1, 1} and with two features x = [xinv, xsp] ∈R2, an
invariant one and a spuriously correlated one. The source and target distributions P and Q over
the feature vector and label are deﬁned as follows. The label y is uniformly distributed over {−1, 1}.
The invariant fully-predictive feature xinv is uniformly distributed in an interval determined by the
constants c > γ ≥0, with the interval being conditional on y:
xinv|y ∼
(
U [γ, c]
if
y = 1
U [−c, −γ]
if
y = −1 .
(11)
The spurious feature xsp is correlated with the response y such that P(x,y)∼P [xsp · y > 0] = pP,
where pP ∈(0.5, 1.0) for some joint distribution P. A distribution shift is modeled by simulating
target data with diﬀerent degrees of spurious correlation such that P(x,y)∼Q [xsp · y > 0] = pQ,
where pQ ∈[0, 1]. There is a distribution shift from source to target when pP ̸= pQ. Two example
distributions P and Q are illustrated in Figure 5.
We consider a logistic regression classiﬁer that predicts class probability estimates for the classes
y = −1 and y = 1 as π(x) =

1
1+ewT x ,
ewT x
1+ewT x

, where w = [winv, wsp] ∈R2. The classiﬁer with
winv > 0 and wsp = 0 minimizes the misclassiﬁcation error across all choices of distributions P and
Q (i.e., across all choices of p). However, a classiﬁer learned by minimizing the empirical logistic
loss via gradient descent depends on both the invariant feature xinv and the spuriously-correlated
feature xsp, i.e., wsp ̸= 0 due to the geometric skews on the ﬁnite data and statistical skews of the
optimization with ﬁnite gradient descent steps [NAN21].
We consider the conformal predictor TPS [SLW19] applied to this problem to generate conﬁdence
sets. For the logistic regression classiﬁer TPS recalibrated with QTC-T provably suceeds:
Theorem 1 (Informal). Consider the logistic regression classiﬁer for the binary classiﬁcation prob-
lem described above with winv > 0, wsp ̸= 0, let n be the number of samples for the source and
target datasets and α ∈(0, ǫ) be a user-deﬁned value, where ǫ is the error rate of the classiﬁer on
the source. The coverage achieved on the target by recalibrating TPS on the source with the QTC
estimate obtained in (7) by ﬁnding the QTC threshold on the target as in (5) converges to 1 −α as
n →∞with high probability.
12
### Page 13

−2
0
2
−1
1
xinv
xsp
Source P
−2
0
2
xinv
Target Q
y = −1
y = +1
Figure 5: Example source and target distributions P and Q for the binary classiﬁcation model,
and a classiﬁer with winv, wsp = 1. The decision boundary is shown with a faded dotted line. The
correlation between the feature xsp and the label y is higher for the source than target (pP > pQ).
Regarding the assumption on α: A value of α that is larger than the error rate of the classiﬁer
does make sense as it would result in empty conﬁdence sets for a portion of the examples in the
dataset.
In order to understand the intuition behind Theorem 1, we ﬁrst explain how the coverage is oﬀ
under a distribution shift in this model. Consider a classiﬁer that depends positively on the spurious
feature (i.e., wsp > 0). When the spurious correlation is decreased from the source distribution to
the target, the error rate of the classiﬁer increases. TPS calibrated on the source samples ﬁnds a
threshold τ such that the prediction sets yield 1 −α coverage on the source dataset as n →∞. In
other words, the fraction of misclassiﬁed points for which the model conﬁdence is larger than the
threshold τ is equal to α on the source. As the spurious correlation decreases and the error rate
increases from source to target, the fraction of misclassiﬁed points for which the model conﬁdence
is larger than the threshold τ surpasses α, leading to a gap in targeted and actual coverage.
Now, we remark on how QTC recalibrates and ensures the target coverage is met. Note that
there exists an unknown coverage level 1 −β that can be used to calibrate TPS on the source
distribution such that it yields 1 −α coverage on the target. Theorem 1 guarantees that QTC
correctly estimates β and therefore recalibration of the conformal predictor using QTC yields the
desired coverage level of 1 −α on the target.
7
Conclusion
We considered the problem of providing reliable uncertainty estimates for conformal prediction
algorithms under distribution shifts based on unlabeled examples. We propose a simple test-time
recalibration method dubbed Quantile Thresholded Conﬁdence (QTC) that recalibrates conformal
predictors based only on unlabeled examples.
QTC provably succeeds on the distribution shift
model from Nagarajan et al. [NAN21] and Garg et al. [GBL22], and most importantly reduces,
or even closes, the coverage gap (i.e., the diﬀerence of achieved coverage and desired coverage) of
conformal predictors under distribution shifts for a variety of natural distribution shifts.
13
### Page 14

Code
Code to reproduce the experiments is available at https://github.com/MLI-lab/recalibrating_conformal_pred
Acknowledgements
F. F. Yilmaz and R. Heckel are (partially) supported by NSF under award IIS-1816986. R. Heckel
is also supported by the Institute of Advanced Studies at the Technical University of Munich, and
also received funding by the German Federal Ministry of Education and Research and the Bavarian
State Ministry for Science and the Arts.
References
[Ang+20]
A. N. Angelopoulos, S. Bates, M. Jordan, and J. Malik. “Uncertainty sets for image
classiﬁers using conformal prediction”. In: International Conference on Learning Repre-
sentations (ICLR) (2020).
[Bat+21]
S. Bates, A. Angelopoulos, L. Lei, J. Malik, and M. I. Jordan. “Distribution-free, risk-
controlling prediction sets”. In: Journal of the ACM (2021).
[Cau+20]
M. Cauchois, S. Gupta, A. Ali, and J. C. Duchi. “Robust validation: Conﬁdent predic-
tions even when distributions shift”. In: arXiv:2008.04267 [cs, stat] (2020).
[CGS21]
M. Chen, K. Goel, and N. Sohoni. “MANDOLINE: Model evaluation under distribution
shift”. In: International Conference on Machine Learning (ICML) (2021).
[Den+09]
J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li, and L. Fei-Fei. “ImageNet: A large-
scale hierarchical image database”. In: Conference on Computer Vision and Pattern
Recognition (CVPR) (2009).
[DGZ21]
W. Deng, S. Gould, and L. Zheng. “What does rotation prediction tell us about classiﬁer
accuracy under varying testing environments?” In: International Conference on Machine
Learning (ICML) (2021).
[DZ21]
W. Deng and L. Zheng. “Are labels always necessary for classiﬁer accuracy evaluation?”
In: Conference on Computer Vision and Pattern Recognition (CVPR) (2021).
[GBL22]
S. Garg, S. Balakrishnan, and Z. C. Lipton. “Leveraging unlabeled data to predict out-
of-distribution performance”. In: International Conference on Learning Representations
(ICLR) (2022).
[Gen+22]
A. Gendler, T.-W. Weng, L. Daniel, and Y. Romano. “Adversarially robust conformal
prediction”. In: International Conference on Learning Representations (ICLR) (2022).
[Gui+21]
D. Guillory, V. Shankar, S. Ebrahimi, T. Darrell, and L. Schmidt. “Predicting with
conﬁdence on unseen distributions”. In: IEEE International Conference on Computer
Vision (ICCV) (2021).
[Guo+17]
C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger. “On Calibration of Modern Neural
Networks”. In: International Conference on Machine Learning. PMLR, 2017.
14
### Page 15

[HD19]
D. Hendrycks and T. Dietterich. “Benchmarking neural network robustness to common
corruptions and perturbations”. In: International Conference on Learning Representa-
tions (ICLR) (2019).
[Hen+21]
D. Hendrycks et al. “The many faces of robustness: A critical analysis of out-of-distribution
generalization”. In: IEEE International Conference on Computer Vision (ICCV) (2021).
[Jia+22]
Y. Jiang, V. Nagarajan, C. Baek, and J. Z. Kolter. “Assessing generalization of SGD
via disagreement”. In: International Conference on Learning Representations (ICLR)
(2022).
[Lei+18]
J. Lei, M. G’Sell, A. Rinaldo, R. J. Tibshirani, and L. Wasserman. “Distribution-Free
Predictive Inference For Regression”. In: Journal of the American Statistical Association
(JASA) (2018).
[NAN21]
V. Nagarajan, A. Andreassen, and B. Neyshabur. “Understanding the failure modes of
out-of-distribution generalization”. In: International Conference on Learning Represen-
tations (ICLR) (2021).
[Par+22]
S. Park, E. Dobriban, I. Lee, and O. Bastani. “PAC prediction sets under covariate
shift”. In: International Conference on Learning Representations (ICLR). 2022.
[Pen+19]
X. Peng, Q. Bai, X. Xia, Z. Huang, K. Saenko, and B. Wang. “Moment matching
for multi-source domain adaptation”. In: IEEE International Conference on Computer
Vision (ICCV). 2019.
[PR21]
A. Podkopaev and A. Ramdas. “Distribution-Free Uncertainty Quantiﬁcation for Clas-
siﬁcation under Label Shift”. In: arXiv:2103.03323 [cs, stat] (2021).
[Rec+19]
B. Recht, R. Roelofs, L. Schmidt, and V. Shankar. “Do ImageNet classiﬁers generalize
to ImageNet?” In: International Conference on Machine Learning (ICML) (2019).
[RSC20]
Y. Romano, M. Sesia, and E. J. Candès. “Classiﬁcation with valid and adaptive cover-
age”. In: Advances in Neural Information Processing Systems (NeurIPS) (2020).
[SLW19]
M. Sadinle, J. Lei, and L. Wasserman. “Least ambiguous set-valued classiﬁers with
bounded error levels”. In: Journal of the American Statistical Association (JASA) (2019).
[STM21]
S. Santurkar, D. Tsipras, and A. Madry. “BREEDS: Benchmarks for subpopulation
shift”. In: International Conference on Learning Representations (ICLR) (2021).
[Tib+19]
R. J. Tibshirani, R. F. Barber, E. J. Candes, and A. Ramdas. “Conformal prediction un-
der covariate shift”. In: Advances in Neural Information Processing Systems (NeurIPS)
(2019).
[VGS05]
V. Vovk, A. Gammerman, and G. Shafer. Algorithmic learning in a random world.
Springer, 2005.
[Wan+19]
H. Wang, S. Ge, E. P. Xing, and Z. C. Lipton. “Learning robust global representations
by penalizing local predictive power”. In: Advances in Neural Information Processing
Systems (NeurIPS) (2019).
15
### Page 16

A
Proof of Theorem 1
In this section, we state and prove a formal version of Theorem 1. Our results rely on adapting the
proof idea of Garg et al. [GBL22, Theorem 3] for predicting the classiﬁcation accuracy of a model
to our conformal prediction setup.
Recall that we consider a distribution shift model for a binary classiﬁcation problem with an
invariant predictive feature and a spuriously correlated feature, where a distribution shift is induced
by the spurious feature of the target distribution being more or less correlated with the label than
the source distribution [NAN21; GBL22].
We consider a logistic regression classiﬁer that outputs class probability estimates (softmax
scores) for the two classes of y = −1 and y = +1 as
π(x) =
"
1
1 + ewT x ,
ewT x
1 + ewT x
#
,
where w = [winv, wsp] ∈R2. The classiﬁer with winv > 0 and wsp = 0 minimizes the misclassiﬁcation
error across all choices of distributions P and Q (i.e., across all choices of p). However, a classiﬁer
learned by minimizing the empirical logistic loss via gradient descent depends on both the invariant
feature xinv and the spuriously-correlated feature xsp, i.e., wsp ̸= 0 due to the geometric skews on
the ﬁnite data and statistical skews of the optimization with ﬁnite gradient descent steps [NAN21].
In order to understand how geometric skews result in learning a classiﬁer that depends on the
spurious feature, suppose the probability that the spurious feature agrees with the label is high, i.e.,
p is close to 1.0. Note that in a ﬁnite-size training set drawn from this distribution, the fraction of
samples for which the spurious feature disagrees with the label (i.e., xsp ̸= y) is small. Therefore,
the margin on the invariant feature for these samples alone can be signiﬁcantly larger than the
actual margin γ of the underlying distribution. This implies that the max-margin classiﬁer depends
positively on the spurious feature, i.e., wsp > 0. Furthermore, we assume that winv > 0, which is
required to obtain non-trivial performance (beating a random guess).
Conformal prediction in the distribution shift model.
We consider the conformal predic-
tion method TPS [SLW19] applied to the linear classiﬁer described above. While other conformal
prediction methods such as APS and RAPS also work for this model, the smoothing induced by the
randomization of the model scores used in those conformal predictors would introduce additional
complexity to the analysis. TPS also tends to be more eﬃcient in that it yields smaller conﬁdence
sets compared to APS and RAPS at the same coverage level, see [Ang+20, Table 9].
In the remaining part of this section, we establish Theorem 1, which states that TPS recali-
brated on the source calibration set with QTC achieves the desired coverage of 1 −α on any target
distribution that has a (potentially) diﬀerent correlation probability p for the spurious feature. We
show this in two steps:
First, consider the oracle conformal predictor that is calibrated to achieve α misscoverage on
the target distribution, i.e., the conformal predictor with threshold τ Q
α chosen so that
α = P(x,y)∼Q

y /∈C(x, τ Q
α )

.
(12)
Deﬁne the misscoverage on the source distribution as
β = P(x,y)∼P

y /∈C(x, τ Q
α )

.
16
### Page 17

From those two equations, it follows that a conformal predictor callibrated to achieve misscoverage
β on the source distribution P achieves the desired misscoverage of α on the target distribution,
provided that the calibration sets are suﬃciently large, which is assumed as we consider the case of
n →∞.
Second, we provide a bound on the deviation of the QTC estimate from the true value of β. We
show that in the inﬁnite sample size case, the QTC estimate converges to the true value of β. Those
two steps prove Theorem 1.
Step 1:
QTC relies on the fact that there exists an unknown β ∈(0, 1) that can be used to
calibrate TPS on the source distribution such that it yields 1 −α coverage on the target.
Here, we show that callibrating to achieve 1 −β coverage on the source calibration set DP via
computing the threshold (2) achieves 1 −α coverage on the target distribution Q as n →∞.
We utilize the following coverage guarantee of conformal predictors established by Vovk et al.
[VGS05], Lei et al. [Lei+18], and Angelopoulos et al. [Ang+20]:
Lemma 1. [Lei+18, Thm. 2.2], [Ang+20, Thm. 1, Prop. 1] Consider (xi, yi), i = 1, . . . , n drawn
iid from some distribution P. Let C(x, τ) be the conformal set generating function that satisﬁes the
nesting property in τ, i.e., C(x, τ ′) ⊆C(x, τ) if τ ′ ≤τ. Then, the conformal predictor calibrated by
ﬁnding τ ∗that achieves 1−α coverage on the ﬁnite set {(xi, y)}n
i=1 as in (2) achieves 1−α coverage
on distribution P, i.e.,
P(x,y)∼P [y ∈C(x, τ ∗)] ≥1 −α.
(13)
Furthermore, assume that the variables si = s(xi, yi) = inf{τ : yi ∈C(xi, τ)} for i = 1, . . . , n are
distinct almost surely. Then, the coverage achieved by the calibrated conformal predictor with the
set generating function C(x, τ) = {ℓ∈Y : s(x, ℓ) ≤τ} is also accurate, in that it satisﬁes
P(x,y)∼P [y ∈C(x, τ ∗)] ≤1 −α +
1
n + 1.
(14)
Both the lower bound (13) and the upper bound (14) of Lemma 1 apply to TPS in the context
of the binary classiﬁcation problem that we consider. To see this, we verify that TPS calibrated
with the set generating function (19) satisﬁes both assumptions of Lemma 1.
First, note that
TPS satisﬁes the nesting property, since we have CTPS(x, τ ′) ⊆CTPS(x, τ) for τ ′ ≤τ. Next, note
that for TPS we have s(x, y) = πy(x). Further note that the linear logistic regression model we
consider assigns a distinct score to each data point and since the invariant feature xinv is uniformly
distributed in a continuous interval conditional on y, the variables si are distinct almost surely.
Now, consider the oracle TPS threshold τ Q
α that achieves 1 −α coverage, or equivalently α
miscoverage, on the target distribution, i.e.,
P(x,y)∼Q

y /∈CTPS(x, τ Q
α )

= α.
(15)
Next, note that y /∈CTPS(x, τ Q
α ) if and only if arg maxj∈{0,1} πj (x) ̸= y and maxj∈{0,1} πj (x) ≥τ Q
α .
To see that, note that the conﬁdence set returned by TPS is a singleton containing only the top
prediction of the model when the conﬁdence of this prediction is higher than the threshold τ Q
α .
Moreover, the conﬁdence set returned by TPS for the binary classiﬁcation problem above does not
17
### Page 18

contain the true label only when the conﬁdence set is the singleton set of the top prediction of the
model and is diﬀerent than the true label. Thus, equation (15) implies
P(x,y)∼Q

arg max
j∈{0,1} πj (x) ̸= y and
max
j∈{0,1} πj (x) ≥τ Q
α

= α.
(16)
We deﬁne β as the miscoverage that the oracle TPS yields on the source distribution, i.e.,
β := P(x,y)∼P

arg max
j∈{0,1} πj (x) ̸= y and
max
j∈{0,1} πj (x) ≥τ Q
α

.
(17)
We have β ̸= α if there is a distribution shift from target to source.
Consider the threshold ˆτ P
β found by calibrating TPS on the set DP to achieve empirical coverage
of 1 −β as in (2). TPS with the threshold ˆτ P
β achieves coverage on the source distribution P as a
result of Lemma 1. Moreover, combining (13) with (14) at n →∞yields exact coverage of 1 −β
on the source distribution P. Thus, we have
P(x,y)∼P

arg max
j∈{0,1} πj (x) ̸= y and
max
j∈{0,1} πj (x) ≥ˆτ P
β

= β.
(18)
Comparing equation (18) to the deﬁnition of β in equation (17) yields ˆτ P
β = τ Q
α . Therefore, it
follows that TPS calibrated to achieve 1 −β coverage on the source calibration set DP as in (2)
achieves exactly 1 −α coverage on the target distribution Q as n →∞.
Step 2:
In the second step, we show that QTC correctly estimates the value of β deﬁned above.
This is formalized by the lemma below.
Recall that the calibration of TPS entails identifying a cutoﬀthreshold τ computed by the
formula (2). The set generating function of TPS for the linear classiﬁcation problem described
above simpliﬁes to
CTPS(x, τ) = {j ∈{0, 1}: πj(x) ≥1 −τ} ,
(19)
where π0(x) and π1(x) are the ﬁrst and second entry of π(x) as deﬁned above.
We are only interested in the regime where the desired coverage level 1 −α is larger than the
classiﬁer’s accuracy, or equivalently α < ǫ with ǫ being the error rate of the classiﬁer.
This is
because a trivial method that constructs conﬁdence sets with equal length of 1 for all samples (i.e.,
singleton sets of only the predicted label) already achieves coverage of 1 −ǫ.
Lemma 2. Given the logistic regression classiﬁer for the binary classiﬁcation problem described
above with any winv > 0, wsp ̸= 0, assume that the threshold q for QTC is computed using a dataset
DQ consisting of n samples, sampled from some target distribution Q, such that
1
|DQ|
X
x∈DQ
1{maxj∈{0,1} πj(x)<q} = α.
(20)
Consider the oracle TPS conformal predictor with conformal threshold τ Q
α , i.e., the predictor that
achieves 1 −α coverage on the target distribution Q. Denote with 1 −β the coverage achieved on
18
### Page 19

the source distribution P by this oracle TPS. Fix a δ > 0. The QTC estimate of the miscoverage β,
denoted by
βQTC =
1
|DP|
X
x∈DP
1{s(π(x))<q},
(21)
satisﬁes the following inequality with probability at least 1−δ over a randomly drawn set of examples
DQ
|βQTC −β| ≤
s
2 log(16/δ)
n · csp
,
(22)
where csp = (1 −pQ) · (1 −pP)2 if wsp > 0 and csp = pQ · (pP)2 otherwise.
Proof. We adapt the proof idea of Garg et al. [GBL22, Theorem 3], which pertains to the problem
of estimating the classiﬁcation error of the classiﬁer on the target, to estimating the source coverage
of the oracle conformal predictor that achieves 1 −α coverage on the target distribution.
For notational convenience, we deﬁne the event that a sample (x, y) is not in the prediction set
of the oracle TPS with conformal threshold τ Q
α (i.e., y /∈CTPS(x, τ Q
α )) as
Emc = {y /∈CTPS(x, τ Q
α )}
= {arg max
j∈{0,1} πj (x) ̸= y and
max
j∈{0,1} πj (x) ≥τ Q
α }.
The inﬁnite sample size case (n →∞).
In this part we show that as n →∞, the QTC
estimate βQTC found as in (21) converges to the source miscoverage β, to illustrate the proof idea.
For n →∞, the QTC estimate βQTC in (21) becomes
βQTC = E(x,y)∼P
h
1{maxj∈{0,1} fj(x)≤q}
i
= P(x,y)∼P

max
j∈{0,1} πj (x) < q

= P(x,y)∼P [Emc]
(23)
= β,
where the last equality is the deﬁnition of β as given in equation (17). The critical step is equa-
tion (23), which we establish in the remainder of this part of the proof.
First, we condition on the label y. Using the law of total probability, we get
P(x,y)∼P

max
j∈{0,1} πj (x) < q

= Px∼P|y=−1

max
j∈{0,1} πj (x) < q

· P(x,y)∼P [y = −1]
+ Px∼P|y=+1

max
j∈{0,1} πj (x) < q

· P(x,y)∼P [y = +1]
(i)
= 1
2 · Px∼P|y=−1

max
j∈{0,1} πj (x) < q

+ 1
2 · Px∼P|y=+1

max
j∈{0,1} πj (x) < q

(ii)
= Px∼P|y

max
j∈{0,1} πj (x) < q

.
(24)
19
### Page 20

For equation (i), we used that y is uniformly distributed across {−1, 1}, and for equation (ii) that
x is symmetrically distributed with respect to the label y.
That is, we have xinv ∼U[−c, −γ]
and P [xsp = −1] = p if y = −1 and xinv ∼U[γ, c] and P [xsp = +1] = p if y = +1, so the two
probabilities in (i) are equal.
We can further expand the expression for the probability Px∼P|y

maxj∈{0,1} πj (x) < q

by ad-
ditionally conditioning on the spurious feature xsp, which yields
P(x,y)∼P

max
j∈{0,1} πj (x) < q

= Pxinv∼P|y,xsp=y

max
j∈{0,1} πj (x) < q

· Px∼P|y [xsp = y]
+ Pxinv∼P|xsp̸=y

max
j∈{0,1} πj (x) < q

· Px∼P|y [xsp ̸= y] .
(25)
In order to simplify the expression in the RHS of equation (25), we consider the cases of wsp > 0
and wsp < 0 separately. If wsp > 0, we have maxj∈{0,1} πj (x) > q if xsp = y. Therefore, we have
Pxinv∼P|y,xsp=y

maxj∈{0,1} πj (x) < q

= 0 if wsp > 0 and equation (25) simpliﬁes to
P(x,y)∼P

max
j∈{0,1} πj (x) < q

= Pxinv∼P|xsp̸=y

max
j∈{0,1} πj (x) < q

· Px∼P|y [xsp ̸= y]
= Pxinv∼P|xsp̸=y

max
j∈{0,1} πj (x) < q

· (1 −pP).
(26)
Similarly, if wsp < 0, we have maxj∈{0,1} πj (x) > q if xsp ̸= y, and equation (25) becomes
P(x,y)∼P

max
j∈{0,1} πj (x) < q

= Pxinv∼P|xsp=y

max
j∈{0,1} πj (x) < q

· Px∼P|y [xsp = y]
= Pxinv∼P|xsp=y

max
j∈{0,1} πj (x) < q

· pP.
(27)
We next follow the same steps that we carried out above for P(x,y)∼P

maxj∈{0,1} πj (x) < q

to
rewrite the probability P(x,y)∼P [Emc]. If wsp > 0, the classiﬁer makes no errors if xsp = y and only
misclassiﬁes a fraction of examples if xsp ̸= y. Therefore, we have
Px∼P|y [Emc] = Pxinv∼P|xsp̸=y [Emc] · Px∼P|y [xsp ̸= y]
= Pxinv∼P|xsp̸=y [Emc] · (1 −pP).
(28)
Similarly, for wsp < 0, we have
Px∼P|y [Emc] = Pxinv∼P|xsp̸=y [Emc] · Px∼P|y [xsp = y]
= Pxinv∼P|xsp̸=y [Emc] · pP.
(29)
Therefore, in order to establish equation (23), it suﬃces to show
Pxinv∼P|y,xsp̸=y

max
j∈{0,1} πj (x) < q

= Pxinv∼P|y,xsp̸=y [Emc] ,
for wsp > 0 and
(30)
Pxinv∼P|y,xsp=y

max
j∈{0,1} πj (x) < q

= Pxinv∼P|y,xsp=y [Emc] ,
for wsp < 0.
(31)
20
### Page 21

The feature xinv is identically distributed conditioned on y, i.e., uniformly distributed in the same in-
terval, regardless of the underlying source or target distributions P and Q. Therefore, equations (30)
and (31) are equivalent to
Pxinv∼Q|y,xsp̸=y

max
j∈{0,1} πj (x) < q

= Pxinv∼Q|y,xsp̸=y [Emc] ,
for wsp > 0 and
(32)
Pxinv∼Q|y,xsp=y

max
j∈{0,1} πj (x) < q

= Pxinv∼Q|y,xsp=y [Emc] ,
for wsp < 0.
(33)
Equations (32) and (33) in turn follow from
P(x,y)∼Q

max
j∈{0,1} πj (x) < q

= P(x,y)∼Q [Emc] ,
(34)
by carrying out the same steps that we carried out to expand the probabilities Px∼P|y

maxj∈{0,1} πj (x) < q

and P(x,y)∼P

maxj∈{0,1} πj (x) < q

starting from equation (24) to establish equations (30) and (31).
Equation (34) in turn is a consequence of combining (16) with (20) at n →∞. This establishes
equation (23), as desired.
The ﬁnite sample case:
We next show that the desired results approximately hold with high
probability over a randomly drawn ﬁnite-sized set of examples DQ. We bound the diﬀerence between
the LHS and RHS of (32) and (33) with high probability.
First, consider the case of wsp > 0. Recall that for the case of wsp > 0 we are interested in the
regime where xsp ̸= y. We denote the set of points in the target set DQ for which the spurious
feature disagrees with the label as
XD = {i = 1, . . . , n : xsp ̸= y, (xi, yi) ∈DQ},
and denote the set of points for which the spurious feature agrees with the label as
XA = {i = 1, . . . , n : xsp = y, (xi, yi) ∈DQ}.
Note that the QTC threshold q found on the entire set DQ as in (20) satisﬁes
1
|XD|
X
i∈XD
1{maxj∈{0,1} πj(xi)<q} =
1
|XD|
X
i∈XD
1{Emc(xi,yi)},
(35)
which follows from noting that the classiﬁer only makes an error on the subset XD if wsp > 0
and therefore the only points for which the event Emc is observed lie in the set XD. Similarly, as
established before in the inﬁnite sample case, we have
1{maxj∈{0,1} πj(xi)<q} = 0 for all i ∈XD.
By the Dvoretzky-Kiefer-Wolfowitz-Massart (DKWM) inequality, for any q > 0 we have with
probability at least 1 −δ/8

1
|XD|
X
i∈XD
1{maxj∈{0,1} πj(xi)<q} −Exinv∼Q|y,xsp̸=y
h
1{maxj∈{0,1} πj(x)<q}
i

≤
s
log(16/δ)
2|XD|
.
(36)
21
### Page 22

Plugging equation (35) into (36), we have with probability at least 1 −δ/8

Exinv∼Q|y,xsp̸=y
h
1{maxj∈{0,1} πj(x)<q}
i
−
1
|XD|
X
i∈XD
1{Emc}

≤
s
log(16/δ)
2|XD|
.
(37)
We next bound the second term in the LHS of equation (37) from its expectation. Using Hoeﬀding’s
inequality, we have with probability at least 1 −δ/8

1
|XD|
X
i∈XD
1{Emc} −Exinv∼Q|y,xsp̸=y

1{Emc}


≤
s
log(16/δ)
2|XD|
.
(38)
Combining equations (37) and (38) using the triangle inequality and union bound, we have with
probability at least 1 −δ/4
Exinv∼Q|y,xsp̸=y
h
1{maxj∈{0,1} πj(x)<q}
i
−Exinv∼Q|y,xsp̸=y

1{Emc}
 ≤
s
2 log(16/δ)
|XD|
.
(39)
Recall that the invariant feature xinv is uniformly distributed in the same interval conditioned on y re-
gardless of the source or target distributions P and Q and that Pxinv|y,xsp=y

maxj∈{0,1} πj (x) > q

=
Pxinv|y,xsp=y

arg maxj∈{0,1} πj (x) ̸= y

= 0 for the case of wsp > 0 as shown before. Therefore, by
dividing both sides of (39) with 1/Px∼P|y [xsp ̸= y] we have with probability at least 1 −δ/4
E(x,y)∼P
h
1{maxj∈{0,1} πj(x)<q}
i
−E(x,y)∼P

1{Emc}
 ≤
1
Px∼P|y [xsp ̸= y]
s
2 log(16/δ)
|XD|
=
1
1 −pP
s
2 log(16/δ)
|XD|
.
(40)
For the case of wsp < 0, we can show an analogous result by noting that the above results can be
shown on the set XA, where xsp = y. Speciﬁcally, noting that
1
|XA|
P
i∈XA
1{maxj∈{0,1} πj(xi)<q} =
1
|XA|
P
i∈XA
1{Emc} if wsp < 0 and following exactly the same steps from equation (35) onward that
lead to equation (40), we have with probability at least 1 −δ/4
E(x,y)∼P
h
1{maxj∈{0,1} πj(x)<q}
i
−E(x,y)∼P

1{Emc}
 ≤1
pP
s
2 log(16/δ)
|XA|
.
(41)
Using Hoeﬀding’s inequality we can further bound the RHS of (40) and (41). For the set XD,
we have with probability at least 1 −δ/2
|XD| −n · (1 −pQ)
 ≤
r
log(4/δ)
2n
,
(42)
and for the set XA, we have with probability at least 1 −δ/2
|XA| −n · pQ ≤
r
log(4/δ)
2n
.
(43)
22
### Page 23

We next bound the diﬀerence between the ﬁnite sample QTC estimation on the source from its
expectation. By DKWM inequality, for any q > 0 we have with probability at least 1 −δ/4

1
|DP|
X
x∈DP
1{maxj∈{0,1} πj(x)<q} −E(x,y)∼P
h
1{maxj∈{0,1} πj(x)<q}
i

≤
r
log(8/δ)
2n
.
(44)
We ﬁrst show the result for the case wsp > 0. Combining equations (40) and (44) using the
triangle inequality and union bound, we have with probability at least 1 −δ/2

1
|DP|
X
x∈DP
1{maxj∈{0,1} πj(x)<q} −E(x,y)∼P

1{Emc}


≤
1
1 −pP
s
2 log(16/δ)
|XD|
.
(45)
Plugging in the deﬁnitions of βQTC in (21) and β in (17) above, equivalently we get
|βQTC −β| ≤
1
1 −pP
s
2 log(16/δ)
|XD|
,
(46)
which holds with probability at least 1 −δ/2. Combining (46) with (42) proves equation (22) for
wsp > 0, as desired.
Similarly, for the case wsp < 0, following the same steps by ﬁrst combining equation (41)
with (44), we have with probability at least 1 −δ/2
|βQTC −β| ≤1
pP
s
2 log(16/δ)
|XA|
.
(47)
Combining (47) with (43) yields equation (22), as desired, for the case wsp < 0, which concludes
the proof.
B
Details on the baseline regression methods
In this section, we provide details on the baseline regression based methods. Recall that we consider
several regression-based methods as baselines by ﬁtting a regression function fθ parameterized by a
feature extractor φπ by minimizing the mean squared error between the output and the calibrated
threshold τ across the distributions as
ˆθ = arg min
θ
X
j
(fθ(φπ(Dj)) −τ Pj)2.
We consider the following choices for the feature extractor φπ:
• Average conﬁdence regression (ACR): The one-dimensional (d = 1) average conﬁdence of the
classiﬁer across the entire dataset which is φπ(D) =
1
|D|
P
x∈D maxℓπℓ(x).
23
### Page 24

0.8
0.9
1
0.7
0.8
0.9
1
desired coverage 1 −α
achieved coverage
ImageNetV2
0.8
0.9
1
0.4
0.6
0.8
1
desired coverage 1 −α
ImageNet-Sketch
0.8
0.9
1
0.4
0.6
0.8
1
desired coverage 1 −α
ImageNet-R
y = x
original
QTC
CHR-
Figure 6: Coverage obtained by RAPS on the target distribution Q for various settings of (1 −α)
w/ and w/o recalibration using QTC.
• Diﬀerence of conﬁdence regression (DCR) [Gui+21]: The one-dimensional (d = 1) average
conﬁdence of the classiﬁer across the entire dataset oﬀset by the average conﬁdence on the
source dataset, which is φπ(D) =
1
|D|
P
x∈D maxℓπℓ(x) −
1
|DP|
P
x∈DP maxℓπℓ(x), where DP
is the source dataset. Prediction is also for the oﬀset target τ −τ P.
We consider DCR in addition to ACR, because DCR performs better for predicting the clas-
siﬁer accuracy [Gui+21]. Since the threshold τ found by conformal calibration depends on
the distribution of the conﬁdences beyond the average, we propose the below techniques for
extracting more detailed information from the dataset.
• Conﬁdence histogram-density regression (CHR): Variable dimensional (d = p) features ex-
tracted as φπ(D) =

1
|D|
P
x∈D
1n
maxℓπℓ(x)∈
h
j−1
p , j
p
io

j={1,...,p}
. This corresponds to the nor-
malized histogram density of the classiﬁer conﬁdence across the dataset, where p is a hyperpa-
rameter that determines the number of histogram bins in the probability range [0, 1]. Neural
networks tend to be overconﬁdent in their prediction which heavily skews the histogram densi-
ties to the last bin. We also therefore consider a variant of CHR, dubbed CHR-, where we have
j = {1, . . . , p −1} and hence d = p −1, equivalent to dropping the last bin of the histogram
as a feature.
• Predicted class-wise average conﬁdence regression (PCR): Features with dimensionality equal
to the number of classes (d = L) extracted as φπ(D) =
P
x∈D πj(x)· 1{l=arg maxℓπℓ(x)}
P
x∈D
1{l=arg maxℓπℓ(x)}

j={1,...,L}
.
This corresponds to the average conﬁdence of the classiﬁer across the samples for each pre-
dicted class.
C
RAPS recalibration experiments
APS is a powerful yet simple conformal predictor. However, other conformal predictors [SLW19;
Ang+20] are more eﬃcient (in that they have on average smaller conﬁdence sets for a given desired
coverage 1 −α).
24
### Page 25

In this section, we focus on the conformal predictor proposed by Angelopoulos et al. [Ang+20],
dubbed Regularized Adaptive Prediction Sets (RAPS). RAPS is an extension of APS that is obtained
by adding a regularizing term to the classiﬁer’s probability estimates of the higher-order predictions
(i.e., subsequent predictions after the top-k predictions).
RAPS is more eﬃcient and tends to
produce smaller conﬁdence sets when calibrated on the same calibration set as APS, as it penalizes
large sets. While TPS tends to achieve slightly better results in terms of eﬃciency compared to
RAPS, see [Ang+20, Table 9], RAPS coverage tends to be more uniform across diﬀerent instances
(in terms of diﬃcult vs. easy instances) and therefore RAPS still carries practical relevance.
Recall that while eﬃciency can be improved by constructing conﬁdence sets more aggressively,
eﬃcient models tend to be less robust, meaning the coverage gap is greater when there is distribution
shift at test time. For example, when calibrated to yield 1 −α = 0.9 coverage on ImageNet-Val
and tested on Image-Sketch, the coverage of RAPS drops to 0.38 in contrast to that of APS, which
only drops to 0.64 (see Section 3). It is therefore of interest to understand how QTC performs for
recalibration of RAPS under distribution shift.
RAPS is calibrated using exactly the same conformal calibration process as APS and only diﬀers
from APS in terms of the prediction set function C(x, u, τ). The prediction set function for RAPS
is deﬁned as
CRAPS(x, u, τ) =





ℓ∈{1, . . . , L}:
ℓ−1
X
j=1
[π(j)(x) +
1{j−kreg>0} · λ
|
{z
}
regularization
] + u · π(ℓ)(x) ≤τ





,
(48)
where u ∼U(0, 1), similar to APS and λ, kreg are the hyperparameters of RAPS corresponding to
the regularization amount and the number of top non-penalized predictions respectively.
We show the results of RAPS’ performance under distribution shift with or without calibration
by QTC in Figure 6. The results show that while QTC is not able to completely mitigate the
coverage gap, it signiﬁcantly reduces it.
25