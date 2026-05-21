# DETRs3D Monocular 3D Object Detection with DETR

**Source**: arxiv PDF, 10 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Continuation KD: Improved Knowledge Distillation through the Lens of
Continuation Optimization
Aref Jafari1
Ivan Kobyzev2
Mehdi Rezagholizadeh2
Pascal Poupart1
Ali Ghodsi1
1University of Waterloo
2Huawei Noah’s Ark Lab
{aref.jafari, ppoupart, ali.ghodsi}@uwaterloo.ca
{ivan.kobyzev, mehdi.rezagholizadeh}@huawei.com
Abstract
Knowledge Distillation (KD) has been exten-
sively used for natural language understand-
ing (NLU) tasks to improve a small model’s
(a student) generalization by transferring the
knowledge from a larger model (a teacher).
Although KD methods achieve state-of-the-art
performance in numerous settings, they suf-
fer from several problems limiting their perfor-
mance. It is shown in the literature that the
capacity gap between the teacher and the stu-
dent networks can make KD ineffective. Ad-
ditionally, existing KD techniques do not mit-
igate the noise in the teacher’s output: mod-
eling the noisy behaviour of the teacher can
distract the student from learning more useful
features. We propose a new KD method that
addresses these problems and facilitates the
training compared to previous techniques. In-
spired by continuation optimization, we design
a training procedure that optimizes the highly
non-convex KD objective by starting with the
smoothed version of this objective and mak-
ing it more complex as the training proceeds.
Our method (Continuation-KD) achieves state-
of-the-art performance across various compact
architectures on NLU (GLUE benchmark) and
computer vision tasks (CIFAR-10 and CIFAR-
100).
1
Introduction
Deep neural networks have achieved great success
in many challenging tasks including the ones in
natural language processing (Vaswani et al., 2017;
Brown et al., 2020a) and computer vision (Dosovit-
skiy et al., 2020). Most successful neural networks
are usually large and overparametrised (Liu et al.,
2019; Devlin et al., 2018). The big size of these
models prevents them from being deployed on com-
puters with low computational power such as edge
devices. Compressing the models can empower
us to provide a variety of machine learning-based
services ofﬂine on low-resource machines. This
issue is even more severe in models designed for
NLP. Although, after the introduction of the Trans-
formers (Vaswani et al., 2017) the performance of
models in this ﬁeld improved dramatically, the size
of the models increased exponentially. Nowadays,
some of these models have more than 100 billion
parameters (Brown et al., 2020b), and they are still
increasing.
One way to address the expensive computa-
tional complexity of deep networks and their over-
parameterization is neural model compression (Ja-
cob et al., 2018; Tjandra et al., 2018; Bie et al.,
2019). Among all of the compression methods,
Knowledge Distillation (KD) (Hinton et al., 2015)
is one of the prominent techniques which have been
used to compress a variety of models in different
deep learning applications such as Natural Lan-
guage Processing (Clark et al., 2019; Sun et al.;
Jiao et al., 2019; Rashid et al., 2020, 2021; Kamal-
loo et al., 2021; Haidar et al., 2021; Wu et al., 2021),
speech processing (Yun et al., 2020; Chebotar and
Waters, 2016), and computer vision (Mirzadeh
et al., 2019; Guo et al., 2020). In KD, we have a
large accurate network, which is called a teacher,
and a small network, which is called a student, that
we desire to train. The innate capacity gap between
the student and the teacher was speculated (Lopez-
Paz et al., 2015) to impede the training and was ad-
dressed by multiple works (Mirzadeh et al., 2019;
Jafari et al., 2021). However, the existing solu-
tions have several complications: for example,
(Mirzadeh et al., 2019) requires an extra intermedi-
ate network to be trained, and (Jafari et al., 2021)
has a rigid two-stage structure that requires the
careful design for successful training. Moreover,
none of these techniques is robust against the noisy
data and noisy teacher’s outputs, which can distract
the student with the limited capacity from learn-
ing more useful features and make it overﬁt to the
noise.
We propose a new solution, Continuation KD,
inspired by the continuation method from optimiza-
Published as a conference paper at EMNLP 2022 (Findings)
arXiv:2212.05998v1  [cs.LG]  12 Dec 2022
### Page 2

tion and nonlinear equations. During the train-
ing, we gradually move from the smoothed objec-
tive function, which is robust to overﬁtting to the
noise, to the original highly non-convex function.
We conduct extensive experiments on the GLUE
benchmark for DistilRoBERTA (6-layer) (Sanh
et al., 2019) and BERT-small (4-layers) (Turc et al.,
2019) core models and show a signiﬁcant improve-
ment over the previous baselines. Besides that,
we demonstrate that in the computer vision setting
continuation KD also outperforms its competitors.
Overall, our contributions are the following:
1. We proposed a novel KD technique based on
the Continuation method, which gradually in-
creases the complexity of the loss function and
provides a better optimization for all knowl-
edge distillation scenarios in both computer
vision and NLP.
2. We implement a loss function like hinge loss
function which makes a student trained with
our technique robust against the teacher’s out-
put noise.
3. Our proposed method is simple and, unlike
its competitors, does not have several stages.
This feature makes our method stable and efﬁ-
cient.
2
Related Works
2.1
Knowledge Distillation (KD)
Knowledge Distillation (Hinton et al., 2015) is
a well-known neural model compression method.
Despite the success of the original method, it has
been shown in the literature (Lopez-Paz et al.,
2015; Mirzadeh et al., 2019) that the large gap
between the size of the student and the teacher
networks makes KD ineffective. To address this
capacity gap problem, Mirzadeh et al. (2019) pro-
posed the teacher assistant knowledge distillation
(TAKD) method.However, this technique is compu-
tationally expensive as it requires training multiple
TA networks for a task. Moreover, the errors of the
TAs can accumulate and transfer to the student. To
alleviate these problems, Jafari et al. (2021) pro-
posed Annealing-KD that achieved state-of-the-art
performance on NLU and computer vision tasks.
Although this method could handle the capacity
gap problem, it is still not robust against the noisy
data and noisy teacher’s outputs. Also, two phases
of the training require some a priori decisions on
when to switch from the ﬁrst phase to the second
one.
2.2
Continuation Optimization
Continuation method was ﬁrst proposed as a numer-
ical method for solving nonlinear equations (Davi-
denko, 1953) and then it was adopted as a heuristic
for nonconvex optimization (Watson, 2000). The
main intuition of the continuation method is to
include the problem we are trying to solve in a con-
tinuous family of problems, such that one of the
members of this family is easy to solve and its so-
lution could be pulled over to give an approximate
solution of the original problem.
Machine Learning community applied the con-
tinuation idea for training neural networks. Mobahi
and Fisher III (2015) proposed the ﬁrst theoreti-
cal analysis of the bound on the approximate solu-
tion given by the continuation optimization. Gul-
cehre et al. (2017) suggested optimizing highly
non-convex neural networks by starting with a
smoothed objective function and making it more
complex over the training. We adapted this general
method for Knowledge Distillation.
3
Background
Vanilla-KD
The original knowledge distillation
(Hinton et al., 2015) trains a small network (a stu-
dent) by using two guiding signals: the hard labels
coming from the training dataset, and the predic-
tions of a large network pre-trained on the same
task (a teacher) which is known as soft labels. To
achieve this goal, Vanilla-KD utilizes a particular
loss function which is a linear combination of two
losses. The ﬁrst one is a cross-entropy between
the softmax output of the student and hard labels,
and the second one is a KL-divergence between the
softened version of the softmax outputs of the stu-
dent and the teacher networks. Equation 1 explains
this loss function in details:
LKD = λCE(y, σ
 zS(x)

+
(1 −λ)KL(σ(zT (x)
τ
), σ(zS(x)
τ
))
(1)
Here CE(.) is the cross-entropy function, KL(.)
is the KL-divergence function, zT (.) and zS(.) are
the teacher and student logits, σ(.) is the softmax
function, and τ is the softening parameter. Also, λ
is a hyper-parameter between [0, 1] which indicates
the amount of contribution of each loss function.
Minimizing the above loss function decreases the
### Page 3

distance between both underlying function and the
teacher model. In Vanilla-KD usually we assume
that the teacher is a good approximation of the
underlying function.
TAKD
In TAKD method (Mirzadeh et al., 2019)
the teacher model ﬁrst trains an intermediate model
with a slightly smaller capacity, which is called
teacher assistant (TA), by utilizing Vanilla-KD.
Then the TA model trains the student model with a
small capacity by using Vanilla-KD again. TAKD
tries to ﬁll the capacity gap between the teacher and
the student models by introducing the TA model
but this gap can be still large. As mentioned in
(Mirzadeh et al., 2019), a better idea is to use hier-
archical TAs to have a smoother knowledge transfer
from the teacher to the student.
Annealing-KD
For controlling the complexity
of the teacher model, instead of using multiple
TA networks, Annealing-KD (Jafari et al., 2021)
adds an annealed dynamic temperature factor to
the output of the teacher. By using this factor,
Annealing-KD reduces the sharpness of the teacher
at the beginning of the training process. Then it
increases the sharpness of the teacher gradually dur-
ing the training. Therefore, since the complexity of
the teacher increases gradually during the training
time, the teacher knowledge transfers much more
smoothly to the student than in TAKD.
Annealing-KD has two stages of training where
in the ﬁrst stage, a student learns from a teacher
for k epochs. During this stage, Annealing-KD
matches the student’s logits to the teacher’s logits
by using a mean square error loss function. At the
beginning of the training the temperature factor sets
to a high value to apply the maximum smoothing
to the output of the teacher and then it decreases
gradually until there is no smoothing effect remains
on the output of the teacher. Formally, one ﬁrst
deﬁnes a monotonically increasing function φ :
N →[0, 1], going from zero at the beginning of the
training to one at the end. Then, the student loss
for stage 1 is:
L(i) = ||zS(x) −φ(i)zT (x)||2
2,
(2)
where i is the training epoch, zS(x) and zT (x) are
logit outputs of the student and the teacher respec-
tively. In the second stage, Annealing-KD gets the
best checkpoint of the ﬁrst stage and ﬁnetune it on
the hard labels from the dataset by using a cross-
entropy loss for m epochs. The hyperparameters k
and m must be chosen before the training.
4
Methodology
In this section, we describe our Continuation-KD
technique, which addresses both the capacity gap
problem and the lack of robustness against the noise
in the teacher’s output. Continuation-KD uses a
loss function with two objectives (Eq. 3). The ﬁrst
objective LCE is a cross-entropy loss term that
trains the student based on the given hard labels.
The second objective LCNT
KD
is our proposed an-
nealed hinge loss function that gradually trains the
student to mimic the behaviour of the teacher. In-
spired by the continuation method (Gulcehre et al.,
2017), Continuation-KD starts with an easy ob-
jective to train at the beginning of training. As
the training proceeds, the whole objective function
becomes more and more complex. Formally, the
loss function of the Continuation-KD is deﬁned as
follows:
L = (ψ(i))LCE + (1 −ψ(i))LCNT
KD
(3)
where 1 ≤i ≤n indicates the epoch index with the
maximum number of epochs n. The 0 ≤ψ(i) ≤1
is an increasing function between 0 and 1 where
ψ(1) = 0 at the beginning and it increases during
the training. LCNT
KD
deﬁnes as:
LCNT
KD
= max{0, ∥zS −φ(Ti)zT ∥2
2 −m φ(Ti)}
(4)
where zS and zT are the output logits of the stu-
dent and teacher networks, respectively; m is the
margin factor; 1 ≤Ti ≤Tmax is the tempera-
ture factor, Tmax is the maximum temperature, and
0 ≤φ(Ti) ≤1 is an increasing function. We deﬁne
this function as:
φ(Ti) = 1 −Ti −1
Tmax
, 1 ≤Ti ≤Tmax, Ti ∈N.
(5)
Note that in Eq. 4, ∥zS −φ(Ti)zT ∥2
2 is a mean
square loss between the student’s logits and the
annealed version of the teacher’s logits.
Also,
max{0, ∥zS −φ(Ti)zT ∥2
2 −φ(Ti)m} is a hinge
loss with an annealed margin φ(Ti)m. This loss
function avoids penalizing negligible differences
(the ones less than m φ(Ti)) between the outputs of
the student and teacher. This feature helps the stu-
dent to learn a meaningful behaviour of the teacher
rather than focusing on higher frequency ﬂuctua-
tions.
### Page 4

Figure 1: Principle diagram illustrating different components of Continuation-KD. The main loss function (purple
box) is a composition of two losses - cross entropy loss LCE and continuation loss LCNT (green boxes). Because
of the smoothing in LCNT with the dynamic factor φ, it is an easier objective to optimize than LCE. During the
training, Continuation KD gradually moves from the easier objective to more complex objective with aid of the
dynamic factor ψ.
At the beginning of training, we set T1 = Tmax
which leads to the most softened version of the
teacher’s output (φ(T1) =
1
Tmax ). Since we have
ψ(1) = 0, the student only learns the behaviour of
the teacher’s smoothest version, which is an easy
target to learn. Then, during training, we decrease
the temperature, At this phase, functions ψ(i) and
φ(Ti) are both increasing which in turn leads to in-
creasing the sharpness of the teacher and smoothly
shifting from the hinge loss to the cross-entropy
loss. Both of these operations increase the com-
plexity of the whole loss function. Note that at the
function φ(Ti) also anneals margin m. Its reason
is that smoothing the teacher with φ(Ti) damps its
noise as well. Therefore we damp the margin m
with φ(Ti) to apply a margin proportional to the
amount of noise in the smoothed version of the
teacher. Figure 1 visualize different components of
continuation-KD.
Also note that, if we set m = 0 and ψ(i) to
the step function in Eq 6, then Continuation-KD
becomes identical to Annealing-KD, where k is the
number of epochs in the ﬁrst stage and n −k is the
number of epochs in the second stage. This fact
shows that the Annealing-KD is actually a special
case of our Continuation-KD.
ψ(i) =
(
0,
1 ≤i ≤k
1,
k < i ≤n
(6)
Algorithm
1
demonstrates
the
details
of
Continuation-KD. It requires a student S, a teacher
T, a dataset D, max temperature Tmax, number
of epochs n, an increasing function ψ, and mar-
gin m as inputs and returns the trained student
at the output. At the beginning, it sets variables
T = Tmax to get the maximum smoothness of
the teacher. Also, variable k indicates the num-
ber of epochs before updating T during training.
Φ and Ψ are the output values of φ(i) and ψ(i).
Function GET-MINI-BATCH(D) retrieves a mini-
batch (X, Y ) from the dataset D. Then these data
samples feed into loss functions in the next lines
to get the outputs of LCE and LCNT
KD . Then the
linear combination of line 14 combines these two
losses to get the continuation loss L. Finally, L is
fed into OPTIMIZATION-BACK-PROPAGATION(.)
function to optimize the student network based
on the back propagation of the gradient of this
loss function and update the weights of the
student.
This part of the training is identi-
cal to regular training of the neural networks.
### Page 5

SAVE-BEST-CHECKPOINT(.) function checks the
performance of the current student model on a val-
idation dataset. If it is better than the previous
checkpoints, it saves the checkpoint. In the end, we
load the best checkpoint and return it.
In the next section, we report the experimental
results of Continuation-KD method.
5
Experiments
This section demonstrates our evaluation results
comparing Continuation-KD with other baselines
for natural language processing and computer vi-
sion tasks. We compare our method with state-
of-the-art techniques such as annealing-KD (Ja-
fari et al., 2021), TAKD (Mirzadeh et al., 2019)
and other baselines like Vanilla-KD (Hinton et al.,
2015) and training the student only with hard labels.
In the following sub-sections, we will discuss each
in more detail.
5.1
Hardware Details
We trained all our baselines using a single NVIDIA
V100 GPU. All experiments were run using the
PyTorch framework1 and for NLP experiments we
used HuggingFace2 API.
5.2
Image Classiﬁcation
For the image classiﬁcation tasks, we used CIFAR-
10 and CIFAR-100 datasets with 10 and 100 classes
respectively. Both of these datasets have 60,000
data samples, and each of them is a 32 × 32 pixel
color image. Also, both of these datasets have
50,000 train and 10,000 test samples.
In all of our computer vision (CV) experiments,
ResNet-8 and ResNet-110 models are used as the
student and the teacher respectively. For the TAKD
baseline, the ResNet-20 model is used as the TA
model. Continuation-KD is trained for 200 epochs
with a maximum temperature of 20, a learning rate
of 0.2, and batch size 32. Also, the following ψ(·)
function used in these experiments:
ψ(i) =
(
i
150,
1 ≤i ≤150
1,
i ≥150
(7)
The CIFAR-10 and CIFAR-100 experiments re-
sults are reported in Tables 1 and 2. We can see
that Continuation-KD clearly outperforms other
1https://pytorch.org
2https://huggingface.co
baselines. Also, Annealing-KD achieved second-
best results in these experiments. However, other
baselines showed almost similar performances.
Table 1: Comparing the test accuracy of Continuation-
KD, Annealing-KD, TAKD, Vanilla-KD, and ﬁnetun-
ing on CIFAR-10 dataset with ResNet model
Type
Training method
Accuracy
Teacher(110)
from scratch
93.8
TA(20)
KD
92.39
Student(8)
from scratch
88.44
Student(8)
KD
88.45
Student(8)
TAKD
88.47
Student(8)
Annealing-KD
89.44
student(8)
Continuation-KD
90.21
Table 2: Comparing the test accuracy of Continuation-
KD, Annealing-KD, TAKD, Vanilla-KD, and ﬁnetun-
ing on CIFAR-100 dataset with ResNet model
Type
Training method
Accuracy
teacher(110)
from scratch
71.92
TA(20)
KD
67.6
student(8)
from scratch
61.37
student(8)
KD
61.41
student(8)
TAKD
61.82
student(8)
Annealing-KD
63.1
student(8)
Continuation-KD
64.2
5.3
Natural Language Understanding
For the NLU experiments, we use the General Lan-
guage Understanding Evaluation (GLUE) bench-
mark (Wang et al., 2018). The benchmark con-
tains several tasks, including textual entailment
(RTE and MNLI), question-answer entailment
(QNLI), paraphrase (MRPC), question paraphrase
(QQP), sentiment (SST-2), textual similarity (STS-
B), linguistic acceptability (CoLA), and Winograd
Schema (WNLI).
Two types of students with different capacities
are used in these experiments. In our ﬁrst exper-
iment, we used distilRoBERTa with 6 layers as
our student and RoBERTa-Large (24 layers) as our
teacher. Also, for the TAKD baseline, we used
RoBERTa-base (12 layers) as the teacher assistant
model. For this experiment, the maximum tem-
perature was 10, learning rate was 2e-5, and batch
size was 64. Also, we used the pre-trained distil-
RoBERTa as our student and we ﬁne-tuned it for
30 epochs. The ψ function for this experiment is
### Page 6

Algorithm 1
1: function CONTINUATION-KD(S,T,D, Tmax, n, ψ(·), m)
2:
T = Tmax
3:
k = ⌊
n
Tmax ⌋
4:
for i = 1 to n do
5:
if i mod k = 0 then
6:
T = T −1
7:
end if
8:
Φ ←1 −T −1
Tmax ,Ψ ←ψ(i)
9:
X, Y ←GET-MINI-BATCH(D)
10:
LCE ←CE(σ(S(X)), Y )
11:
LCNT
KD
←max{0, ∥S(X) −ΦT(X)∥2
2 −m Φ}
12:
L = ΨLCE + (1 −Ψ)LCNT
KD
13:
OPTIMIZATION-BACK-PROPAGATION(L)
14:
SAVE-BEST-CHECKPOINT(S)
15:
end for
16:
S ←LOAD-BEST-CHECKPOINT( )
17:
return S
18: end function
deﬁned as following:
ψ(i) =
(
i
40,
1 ≤i ≤20
1,
20 < i ≤30
(8)
Tables 3 and 4 show the results of this experi-
ment on the dev set and test set. As shown in these
tables, Continuation-KD achieved superior results
in most of the tasks and it improves the previous
baselines with a good overall average score.
For the second experiment, we utilize BERT-
large (24-layers) as the teacher, BERT-Small (4-
layers) as the student and BERT-base (12-layers)
as the teacher-assistant for TAKD. We train the
teacher for 30 epochs, and for the student, we use
the same hyperparameters as the ﬁrst experiment.
We report the results in Tables 5 and 6. Here,
Continuation-KD also outperforms other baselines
and gets better overall performance than its com-
petitors.
All presented results in our experiments show
that continuation-KD performs better than TAKD
and Annealing-KD, which indicates the effective-
ness of this method. The experimental results sup-
port the claim that our proposed Continuation-KD
can provide a better generalization than the other
methods.
6
Analysis
To investigate how Continuation-KD works, we did
two ablation studies explaining different aspects of
this technique: effects of the dynamically changing
factors and noise mitigation.
Effects of Dynamic Factors φ and ψ.
In
the ﬁrst ablation, we scrutinize the effect of
each dynamically changing component of the
Continuation-KD loss function. It basically consid-
ers the effect of functions: ψ(i) from Eq. 3, φ(Ti)
when it anneals the outputs of the teacher in Eq. 4,
and φ(Ti) when it anneals the margin of the hinge
loss in Eq. 4. To investigate the effects of these
components, we repeat the NLU experiments with
distilRoBERTa model described in section 5.3 on
MRPC and RTE datasets three times. In each trial,
we ﬁxed two of the components, and we only let
one of them dynamically change during training.
Table 7 reports the performance of each of these
experiments. The ﬁrst three columns of this table
show the performance of distilRoBERTa on each of
the datasets when only one of the three dynamical
components changes and two others are ﬁxed. The
last column shows the performance of the model
on these datasets in a regular training when all com-
ponents dynamically change. In the ﬁrst column,
the φ = 1 is ﬁxed for both teacher and margin. In
the second column, the margin’s coefﬁcient is ﬁxed
to 1 and ψ = 0.5. Also, in the third column, the
teacher’s coefﬁcient is ﬁxed to 1 and ψ = 0.5.
As shown in Table 7, for both datasets, the perfor-
mance in the ﬁrst three columns is almost similar,
which indicates the equal contribution of each dy-
### Page 7

(a)
(b)
Figure 2: (a) Illustrates the behaviour of the student model after training with a noisy teacher without using
continuation-KD. (b) Illustrates the behaviour of the student model after training with a noisy teacher by using
continuation-KD for training. Blue points are the samples from the noisy teacher. Orange points are the samples
of the trained student in each scenario.
Table 3: DistilRoBERTa results for Continuation-KD on dev set. F1 scores are reported for MRPC, pearson
correlations for STB-B, and accuracy scores for all other tasks.
KD Method
CoLA
RTE
MRPC
STS-B
SST-2
QNLI
QQP
MNLI
score
Teacher
68.1
86.3
91.9
92.3
96.4
94.6
91.5
90.22
88.91
Finetune
59.3
67.9
88.6
88.5
92.5
90.8
90.9
84
82.81
Vanilla-KD
60.97
71.11
90.2
88.86
92.54
91.37
91.64
84.18
83.85
TAKD
61.15
71.84
89.91
88.94
92.54
91.32
91.7
83.89
83.91
Annealing KD
61.67
73.64
90.6
89.01
93.11
91.64
91.5
85.34
84.56
Continuation-KD
63.75
77.62
91.93
89.71
93.58
91.76
91.64
85.16
85.64
Table 4: Performance of DistilRoBERTa trained by Continuation-KD on the GLUE leaderboard compared with
Vanilla-KD, TAKD, and annealing KD.
KD Method
CoLA
RTE
MRPC
STS-B
SST-2
QNLI
QQP
MNLI
score
Finetune
52.97
74.56
87.93
84.9
93.1
90.57
83.4
88.77
82.02
Vanilla-KD
54.3
74.1
86
85.7
93.1
83.6
90.8
89.5
82.14
TAKD
53.2
74.2
86.7
85.6
93.2
83.8
91
89.4
82.14
Annealing KD
54
73.7
88
87.0
93.6
83.8
90.8
89.7
82.58
Continuation-KD
54.5
74.2
90
87.0
93.8
84.7
91.6
90.1
83.24
Table 5: BERT-Small results for Continuation-KD on dev set. F1 scores are reported for MRPC, pearson correla-
tions for STS-B, and accuracy scores for all other tasks.
KD Method
CoLA
RTE
MRPC
STS-B
SST-2
QNLI
QQP
MNLI
score
Teacher
65.8
71.48
91.38
89.2
92.77
92.82
91.45
86.3
85.15
Finetune
41.7
64.98
83.75
87.41
88.3
86.49
88.43
78.42
77.44
Vanilla-KD
41.89
64.98
86
85.95
88.76
86.75
88.24
78.62
77.65
TAKD
40.2
65.7
85.23
86.44
88.88
86.78
88.4
78.78
77.55
Annealing-KD
41.36
64.9
87.93
87.04
89.56
86.99
88.58
78.66
78.13
Continuation-KD
41.51
65.26
89.44
87.81
90.21
87.52
90.61
79.27
78.95
### Page 8

Table 6: BERT-Small results for Continuation-KD on test set. F1 scores are reported for MRPC, pearson correla-
tions for STS-B, and accuracy scores for all other tasks.
KD Method
CoLA
RTE
MRPC
STS-B
SST-2
QNLI
QQP
MNLI
score
Finetune
38.1
61.8
83.4
78.8
89.7
86.4
78.1
77.6
74.24
Vanilla-kd
37.3
63.4
80.6
78.2
90.2
86.5
78.3
78.3
74.09
TAKD
38.5
62.3
80.5
79.3
89.7
86.7
78
78.2
74.14
Annealing-KD
38.3
63.3
81.9
80.6
89.8
86.8
78.4
79.3
74.78
Continuation-KD
38.5
64.8
84.6
82.5
90.6
87.2
80.1
79.5
75.98
namic component in the improvement of the results.
Also, the last column shows the dramatic improve-
ment in the performance. Hence, we can conclude
from this experiment that all three dynamic com-
ponents are necessary for achieving better perfor-
mance.
Table 7: Performance of distilRoBERTa on MRPC and
RTE datasets for different dynamically changing com-
ponents of continuation-KD loss
dataset
ψ
φ (teacher)
φ (margin)
all
MRPC
91.09
91.21
90.90
91.93
RTE
72.56
73.64
71.48
77.62
Noise Robustness
In the second ablation study,
we visualize the effect of Continuation-KD with
a noisy teacher. For this purpose, we consider a
sinusoidal function with low frequency, and then
we add to it a sinusoidal noise with high frequency
(blue curves in Figure 2). Then, we take a fully
connected network with one-dimensional input and
output and two hidden layers with 128 neurons in
each layer as a student model. We sample 3,000
points from the graph of the noisy sinusoidal func-
tion and train the student model once with Vanilla-
KD and once with Continuation-KD (orange curves
in Figure 2). As Figure 2 shows, the model trained
with Continuation-KD has a much smoother curve
in comparison with the model trained with vanilla-
KD and could learn the main behaviour of the
teacher function rather than learning noise.
7
Conclusion
In this work, we present Continuation-KD, a novel
KD method inspired by Continuation optimization.
Our Continuation-KD technique starts optimizing
a smoothed version of the objective function and
gradually increases the complexity of the loss to-
wards the original, highly non-convex one. We
demonstrated that our method alleviates the capac-
ity gap problem: an innate problem of KD resulting
from the different capacities of a student’s and a
teacher’s networks which detriments the perfor-
mance. Besides that, we show that the method
can lessen the student’s overﬁtting to noise in the
teacher’s output. Our technique is stable because
it doesn’t require two stages in the training and is
efﬁcient. It outperforms its competitor KD meth-
ods for different backbone models’ architectures in
both computer vision and NLP.
For this investigation, we proposed to implement
Continuation method by smoothing the objective
with the hinge loss. However, it can potentially be
done differently. Investigating other realizations
of Continuation Optimization for improving small
models’ performance is an interesting next step.
Limitation
One of the advantages of our proposed method is
that it mitigates the noise in the teacher’s output
and prevents the student from overﬁtting to the
noise. We empirically demonstrate this claim, but
we don’t have rigorous theoretical proof of how
continuation method achieves this robustness.
Acknowledgments
We thank Mindspore3 for the partial support of this
work. We thank the anonymous reviewers for their
insightful comments.
References
Alex Bie, Bharat Venkitesh, Joao Monteiro, Md Haidar,
Mehdi Rezagholizadeh, et al. 2019.
A simpliﬁed
fully quantized transformer for end-to-end speech
recognition. arXiv preprint arXiv:1911.03604.
Tom Brown, Benjamin Mann, Nick Ryder, Melanie
Subbiah,
Jared
D
Kaplan,
Prafulla
Dhariwal,
Arvind Neelakantan, Pranav Shyam, Girish Sastry,
Amanda Askell, Sandhini Agarwal, Ariel Herbert-
Voss, Gretchen Krueger, Tom Henighan, Rewon
3A new deep learning computing framework https://
www.mindspore.cn/
### Page 9

Child, Aditya Ramesh, Daniel Ziegler, Jeffrey Wu,
Clemens Winter, Chris Hesse, Mark Chen, Eric
Sigler, Mateusz Litwin, Scott Gray, Benjamin Chess,
Jack Clark, Christopher Berner, Sam McCandlish,
Alec Radford, Ilya Sutskever, and Dario Amodei.
2020a. Language models are few-shot learners. In
Advances in Neural Information Processing Systems,
volume 33, pages 1877–1901. Curran Associates,
Inc.
Tom B Brown, Benjamin Mann, Nick Ryder, Melanie
Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind
Neelakantan, Pranav Shyam, Girish Sastry, Amanda
Askell, et al. 2020b. Language models are few-shot
learners. arXiv preprint arXiv:2005.14165.
Yevgen Chebotar and Austin Waters. 2016.
Distill-
ing knowledge from ensembles of neural networks
for speech recognition. In Interspeech, pages 3439–
3443.
Kevin Clark, Minh-Thang Luong, Urvashi Khandel-
wal, Christopher D. Manning, and Quoc V. Le. 2019.
BAM! born-again multi-task networks for natural
language understanding. In Proceedings of the 57th
Annual Meeting of the Association for Computa-
tional Linguistics, pages 5931–5937, Florence, Italy.
Association for Computational Linguistics.
D.F. Davidenko. 1953. On a new method of numeri-
cal solution of systems of nonlinear equations. Dokl.
Akad. Nauk SSSR, 88:601–602.
Jacob Devlin, Ming-Wei Chang, Kenton Lee, and
Kristina Toutanova. 2018. Bert: Pre-training of deep
bidirectional transformers for language understand-
ing. arXiv preprint arXiv:1810.04805.
Alexey
Dosovitskiy,
Lucas
Beyer,
Alexander
Kolesnikov,
Dirk
Weissenborn,
Xiaohua
Zhai,
Thomas Unterthiner, Mostafa Dehghani, Matthias
Minderer, Georg Heigold, Sylvain Gelly, et al. 2020.
An image is worth 16x16 words:
Transformers
for image recognition at scale.
arXiv preprint
arXiv:2010.11929.
Caglar Gulcehre, Marcin Moczulski, Francesco Visin,
and Yoshua Bengio. 2017. Mollifying networks. In
5th International Conference on Learning Represen-
tations.
Qiushan Guo, Xinjiang Wang, Yichao Wu, Zhipeng Yu,
Ding Liang, Xiaolin Hu, and Ping Luo. 2020. On-
line knowledge distillation via collaborative learn-
ing. In Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, pages
11020–11029.
Md Akmal Haidar, Nithin Anchuri, Mehdi Reza-
gholizadeh, Abbas Ghaddar, Philippe Langlais, and
Pascal Poupart. 2021. Rail-kd: Random intermedi-
ate layer mapping for knowledge distillation. arXiv
preprint arXiv:2109.10164.
Geoffrey Hinton, Oriol Vinyals, and Jeff Dean. 2015.
Distilling the knowledge in a neural network. arXiv
preprint arXiv:1503.02531.
Benoit Jacob, Skirmantas Kligys, Bo Chen, Meng-
long Zhu, Matthew Tang, Andrew Howard, Hartwig
Adam, and Dmitry Kalenichenko. 2018.
Quanti-
zation and training of neural networks for efﬁcient
integer-arithmetic-only inference. In Proceedings of
the IEEE Conference on Computer Vision and Pat-
tern Recognition, pages 2704–2713.
Aref Jafari, Mehdi Rezagholizadeh, Pranav Sharma,
and Ali Ghodsi. 2021. Annealing knowledge distil-
lation. In Proceedings of the 16th Conference of the
European Chapter of the Association for Computa-
tional Linguistics: Main Volume, pages 2493–2504.
Xiaoqi Jiao, Yichun Yin, Lifeng Shang, Xin Jiang,
Xiao Chen, Linlin Li, Fang Wang, and Qun Liu.
2019. Tinybert: Distilling bert for natural language
understanding. arXiv preprint arXiv:1909.10351.
Ehsan Kamalloo, Mehdi Rezagholizadeh, Peyman
Passban, and Ali Ghodsi. 2021.
Not far away,
not so close: Sample efﬁcient nearest neighbour
data augmentation via minimax.
arXiv preprint
arXiv:2105.13608.
Yinhan Liu, Myle Ott, Naman Goyal, Jingfei Du, Man-
dar Joshi, Danqi Chen, Omer Levy, Mike Lewis,
Luke Zettlemoyer, and Veselin Stoyanov. 2019.
Roberta: A robustly optimized bert pretraining ap-
proach. arXiv preprint arXiv:1907.11692.
David Lopez-Paz, Léon Bottou, Bernhard Schölkopf,
and Vladimir Vapnik. 2015.
Unifying distilla-
tion and privileged information.
arXiv preprint
arXiv:1511.03643.
Seyed-Iman Mirzadeh, Mehrdad Farajtabar, Ang Li,
and Hassan Ghasemzadeh. 2019. Improved knowl-
edge distillation via teacher assistant: Bridging the
gap between student and teacher.
arXiv preprint
arXiv:1902.03393.
Hossein Mobahi and John Fisher III. 2015. A theoret-
ical analysis of optimization by gaussian continua-
tion. Proceedings of the AAAI Conference on Artiﬁ-
cial Intelligence, 29(1).
Ahmad Rashid, Vasileios Lioutas, Abbas Ghaddar, and
Mehdi Rezagholizadeh. 2020.
Towards zero-shot
knowledge distillation for natural language process-
ing. arXiv preprint arXiv:2012.15495.
Ahmad Rashid, Vasileios Lioutas, and Mehdi Reza-
gholizadeh. 2021.
Mate-kd: Masked adversarial
text, a companion to knowledge distillation. arXiv
preprint arXiv:2105.05912.
Victor Sanh, Lysandre Debut, Julien Chaumond, and
Thomas Wolf. 2019. Distilbert, a distilled version
of bert: smaller, faster, cheaper and lighter. arXiv
preprint arXiv:1910.01108.
Zhiqing Sun, Hongkun Yu, Xiaodan Song, Renjie Liu,
Yiming Yang, and Denny Zhou. Mobilebert: Task-
agnostic compression of bert for resource limited de-
vices.
### Page 10

Andros Tjandra, Sakriani Sakti, and Satoshi Nakamura.
2018. Tensor decomposition for compressing recur-
rent neural network.
In 2018 International Joint
Conference on Neural Networks (IJCNN), pages 1–8.
IEEE.
Iulia Turc, Ming-Wei Chang, Kenton Lee, and Kristina
Toutanova. 2019.
Well-read students learn better:
On the importance of pre-training compact models.
arXiv preprint arXiv:1908.08962.
Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob
Uszkoreit, Llion Jones, Aidan N Gomez, Łukasz
Kaiser, and Illia Polosukhin. 2017. Attention is all
you need. In Advances in neural information pro-
cessing systems, pages 5998–6008.
Alex Wang, Amanpreet Singh, Julian Michael, Felix
Hill, Omer Levy, and Samuel R Bowman. 2018.
Glue: A multi-task benchmark and analysis platform
for natural language understanding. arXiv preprint
arXiv:1804.07461.
L.T. Watson. 2000.
Theory of globally convergent
probability-one homotopies for nonlinear program-
ming. SIAM Journal on Optimization, 11(3):761–
780.
Yimeng Wu, Mehdi Rezagholizadeh, Abbas Ghaddar,
Md Akmal Haidar, and Ali Ghodsi. 2021. Universal-
kd: Attention-based output-grounded intermediate
layer knowledge distillation. In Proceedings of the
2021 Conference on Empirical Methods in Natural
Language Processing, pages 7649–7661.
Sukmin Yun, Jongjin Park, Kimin Lee, and Jinwoo
Shin. 2020. Regularizing class-wise predictions via
self-knowledge distillation.
In Proceedings of the
IEEE/CVF conference on computer vision and pat-
tern recognition, pages 13876–13885.