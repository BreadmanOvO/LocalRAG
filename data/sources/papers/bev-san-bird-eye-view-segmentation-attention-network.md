# BEV-SAN Bird-eye-view Segmentation Attention Network

**Source**: arxiv PDF, 12 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Towards ML-based diagnostics of focused laser pulse
Y. R. Rodimkov,1, ∗V. D. Volokitin,1, 2, † I. B. Meyerov,1, 2, ‡ and E. S. Eﬁmenko3, §
1Department of Mathematical Software and Supercomputing Technologies,
Lobachevsky University, 603950 Nizhni Novgorod, Russia
2Mathematical Center, Lobachevsky University, 603950 Nizhni Novgorod, Russia
3Institute of Applied Physics of the Russian Academy of Sciences, 603950 Nizhni Novgorod, Russia
Currently, machine learning (ML) methods are widely used to process the results of physi-
cal experiments. In some cases, due to the limited amount of experimental data, ML-models
can be pre-trained on synthetic data simulated based on the analytical theory and then ﬁne-
tuned using experimental data. A limitation of this approach is the presence of the latent
parameters of the analytical model, which values are diﬃcult or impossible to estimate. Set-
ting these parameters incorrectly may induce a dataset shift even when applied to synthetic
data. To overcome this problem, we train the ML-model on a dataset with randomly varied
latent parameters of the analythical model to force the ML-model to concentrate on more
general patterns that depend weakly on the latent parameters. We applied this approach to
the problem of tight focusing of a laser pulse with the complex structure of the wavefront.
We observed good accuracy of reconstructing of the tilt parameters when training and test-
ing the ML-model on datasets generated for diﬀerent values of the latent parameters. This
conﬁrms that the ML-model was able to select relevant information without over-ﬁtting for
speciﬁc features inherent in certain values of the latent parameters. We believe that this
approach will enrich possible applications of ML-methods to an experimental diagnostics of
laser pulses.
I.
INTRODUCTION
With the progress in optics technologies in the last decades, laser facilities can now achieve
unprecedented intensities.
Femtosecond laser pulses focused to spot size of the order of a few
micrometers can now routinely achieve intensities above 1022 W/cm2 [1–3], with a record intensity
even exceeding 1023 W/cm2 [4]. These ultra-relativistic laser pulses allow for multiple applications
such as particle acceleration in plasmas [5, 6] and production of γ-rays [7], or exploring quanto-
electrodynamic eﬀects in laser-plasma interaction in the high-ﬁeld regime [8].
Such intensities are reached by the OPCPA technique, which successively stretches and com-
presses the pulse for further ampliﬁcation [9]. Any imperfection in this process in the laser chain
can thus introduce spatio-temporal couplings (STC), i.e. correlations between the longitudinal and
transverse intensity proﬁles, which ultimately reduces the intensity at focus [10, 11]. STC tends
to become stronger for more powerful laser systems – corresponding to an increasing waste of the
pumping energy, which becomes greatly harmful for applications.
Characterization of the laser pulse is thus crucial both for optimizing the laser proﬁle in exper-
iments and for its accurate numerical description without overestimation of the peak intensity –
leading to better agreement with the experimental results and thus ultimately to a deeper under-
standing of the underlying physics.
Spatio-temporal characterization of the ultra-intense laser pulses is however not straightfor-
ward. Direct detection is precluded due to the high frequency of the pulse, and a combination of
∗E-mail: rodimkov@bk.ru
†E-mail: valyav95@mail.ru
‡E-mail: meerov@vmk.unn.ru
§E-mail: evgeny.eﬁmenko@ipfran.ru
arXiv:2209.09959v1  [physics.comp-ph]  20 Sep 2022
### Page 2

2
spectroscopy and interferometry has to be used. 3D characterization is thus a trade-oﬀbetween
cost, time of acquisition and resolution of the data. Recently, experimental techniques leading
to a complete spatio-temporal characterization of ultra-intense laser pulses have been developed,
such as TERMITES [12] or INSIGHT [13], which have been applied to top-class PW-laser facil-
ities [14]. Such measurements are however obtained thought extensive manipulations, and eﬀort
are also pursued for simplifying this process through the combination of experimental measure-
ments and machine learning. First attempts in this sense were realized in the 90’s, in which neural
network [15] and genetic algorithm [16] were used with frequency-resolved optical gating (FROG)
for reconstructing the pulse phase. More recently, a neural network trained on simulated data
retrieved the pulse phase even in the presence of high noise, and lowered the required knowledge
about the relation between the pulse and its measurement [17]. Other works have also proposed
to reconstruct the pulse phase with neural network from dispersion scan traces [18], 2D intensity
patterns [19] or with a multimode ﬁber [20].
Training data for machine learning (ML) models can be collected experimentally or through
simulation. Quite often the amount of experimental data is not suﬃcient for training the ML-
model from scratch. In this case the training data can be numerically simulated on the basis of
some analytical theory, and then ﬁne-tuned on a real experimental data. This approach, although
seems very natural, requires good correspondence between the analytical theory and experiment.
The later can become very problematic, because the analytical model may have hidden or latent
parameters which aﬀect the results, but can not be directly measured or estimated in the exper-
iment. The number of such latent parameters for ML-models can be large. Setting parameters
incorrectly during data collection can cause a ML-model to break when applied to real data due
to dataset shift.
In this article, we demonstrate an approach to reconstructing the physical parameters of a
tightly focused laser pulse based on the energy ﬂux distribution in the case of the latent param-
eters uncertainty. In order to make the laser pulse model closer to experimental conditions we
impose a spectral-dependent tilt on its wavefront, and the properties of this tilt act as the latent
parameters of the model. The resulting analytical model is rather simpliﬁed representation of the
real experimental conditions, nevertheless it can help to ﬁnd better approaches for the problem.
This parameterized model with randomly varied parameters was used for synthetic data genera-
tion. We use this data to train the ML-model to solve the inverse problem of reconstructing pulse
parameters. In order to study the inﬂuence of the choice of the latent parameters on accuracy of
the ML-model we study the generalization ability of this model by training and testing on diﬀerent
subsets of the latent parameters values. By doing this we demonstrate tolerance of the ML-model
to wrong choice of the latent parameters during training, that can be useful for the application of
ML-methods to real experimental data.
The article is structured as follows. In Section II the analytical model used for data generation
is described. In Section III we present the methodology of our work, methods and metrics used
in this paper, the solution of the inverse problem and the analysis of the generalization ability of
the ML-model. In Section IV the results are discussed and some considerations related to further
development of the approach are given. Finally, in Section V the conclusions are formulated.
II.
GENERATIVE MODEL
The data was generated by simulation of the propagation of a tightly focused laser pulse initial-
ized in the far ﬁeld zone to the focal plane. The modeling was performed by means of the Hi-chi
module [21], which uses a spectral method for solving Maxwell’s equations. The cumulative energy
ﬂux was calculated in the focal plane to be used for the ML-model training.
### Page 3

3
For simplicity the pulse propagates along the x-axis and the pulse wavefront is chosen to be
spherical, so any ﬁeld component u in the far ﬁeld zone can be set as
u(x, y, z) = ul(r(x, y, z))ut(α(x, y, z)),
(1)
where r = |r| = |R−R0| is the distance from the center of the spherical wavefront R0 to the point R
and α = arcsin
p
y2 + z2/r is the angle between the x-axis and vector r. The electromagnetic ﬁelds
are deﬁned as E(R) = u(R)s0 and B(R) = u(R)s1 with the normalized vectors s0 = ey × ey × r
and s1 = ey × r.
The longitudinal ul and transverse ut proﬁles are deﬁned as follows
ul(x) = sin
2πx
λ0
+ ϕ

exp
 
−x2
2L2
!
Π (x, −4L, 4L) ,
(2)
ut(α) = Π

α, 0, θ −ε
2

+ cos2
π(α −θ + ε/2)
2ε

Π

α, θ −ε
2, θ + ε
2

,
(3)
where λ0 is the central wavelength, L is the length of the pulse and Π is the rectangular function,
with Π(x, xmin, xmax) = 1 if x is in [xmin, xmax] and 0 otherwise. In this case ut corresponds
to a transverse ﬂattop proﬁle with no intensity outside of the opening angle θ with the edge
smoothing angle ε. The opening angle θ is connected to the F-number of the focusing optics by
θ = arctan(1/2F). An additional phase ϕ is used to model the imperfections of the wavefront that
occur in experimental conditions.
The proposed pulse deﬁnition does not account for complex structure of wavefront inherent
to real experimental conditions. In order to model complex wavefront structure in a simpliﬁed
manner we introduce three spectral components by applying mask functions fi(k) (see Fig. 1)
to the spectra of the longitudinal proﬁle ul,i(k) = ul(k)fi(k), where ul(k) =
R ∞
−∞ul(x)e−ikxdx
is the spatial Fourier spectra of the longitudinal proﬁle ul(x) and k is the wavenumber. Three
spectral components are separated by the two wavenumbers k1 and k2 such as k1 > k0 > k2 with
ki = 2πc/λi, where c is the speed of light. These two boundary wavenumbers k1,2 are varied in the
range [ki,min, ki,max] to parameterize the laser pulse deﬁnition. For convenience, later in the text
we operate with corresponding wavelengths λ1,2 as boundary wavelengths and treat them as the
latent parameters of the model.
For each of these three spectral component we add a linear tilt by adding the additional phase
ϕi in the longitudinal proﬁle ui(x) in the Eq. 2
ϕi = aiy′
i,
y′
i = y cos θi −z sin θi,
(4)
where ai is a constant characterizing the amplitude of the tilt and θi is an angle characterizing the
direction of the tilt in the transverse plane. Further in this paper ai and θi are referred to as the
tilt amplitude and the tilt angle, respectively.
After applying the mask function we calculate longitudinal proﬁle ul,i for each spectral com-
ponent by performing inverse Fourier transform ul,i(x) = 1/2π
R ∞
−∞ul(x)eikxdk and calculate the
corresponding spectral component initial distribution ui according to Eq. 1
ui(x, y, z) = ul,i(r) ut(α).
(5)
After initialization in the far ﬁeld zone each component is propagated to the focal plane using
the spectral solver. Using the linearity of Maxwell’s equations, we can then get the total ﬁeld at
the focal position as the sum of ﬁelds of all spectral components as
utot(R) =
X
i
Aiui(R),
(6)
### Page 4

4
k2
k0
k1
k2,min
k2,max
k1,min
k1,max
1
0
f2(k)
f0(k)
f1(k)
FIG. 1:
Mask functions fi(k) used to create three spectral components with diﬀerent tilt properties.
with Ai deﬁning the relative spectral component amplitude compared with the central component
corresponding to the mask function f0 (i.e. A0 = 1). These relative amplitude parameters A1,2 act
as another pair of latent parameters of our laser pulse model.
Finally, we calculate the cumulative energy ﬂux in the focal plane
I(y, z) = 1
4π
Z ∞
−∞
Etot(x, y, z) × Btot(x, y, z) · exdx.
(7)
Summarizing, in our simpliﬁed model the energy ﬂux depends on following parameters: the
boundary wavelengths λ1,2, the relative amplitudes A1,2, the tilt amplitudes ai and the tilt angles
θi with i ∈[0, 1, 2]. The last six parameters ai and θi were predicted by the ML-model, while
λ1,2 and A1,2 acted as the latent parameters of the pulse model. Data was generated using central
wavelength λ0 = 800 nm, F-number of the focusing optics F=1.5, the pulse is initialized at 65λ0
from the spherical wavefront center. Other parameters were set in the following ranges: λ1 ∈
[600nm, 750nm], λ2 ∈[850nm, 1000nm], A1,2 ∈[0.5, 2], a0,1,2 ∈[0, 0.6] and θ0,1,2 ∈[0, 2π].
III.
RESULTS
A.
Methodology
The problem under consideration is the inverse problem of predicting of six parameters (the tilt
angle and the tilt amplitude for three spectral components) based on the cumulative energy ﬂux
in the focal plane. The analytical model which describes the experiment has latent parameters,
which can not be directly reconstructed from the experiment.
In our rather simpliﬁed model
such parameters are the boundary wavelengths λ1,2 and the relative amplitudes of the spectral
component with the lowest and highest wavelengths, respectively, A1,2. Determination of these
parameters in an experiment, in which the ML-model will be used after training on synthetic data,
is a diﬃcult task. Thus, methodologically, the work is divided into two stages. At the ﬁrst stage,
the inverse problem of reconstructing the tilt parameters ai and θi is solved. In order to do this a
suitable architecture of the ML-model is chosen, and the best way for reconstructing the parameters
is searched for. At the second stage, after the inverse problem is solved, the generalization ability
of the proposed ML-model is analyzed. To do this, the ML-model is trained on a subset of latent
parameters values, and then tested on the entire available set of latent parameter values, i.e.
the test set includes values of latent parameters that were not present in the training set. Such
experiments will help to answer the main question of interest of this paper, whether the trained
### Page 5

5
ML-model is able to generalize the extracted information to unknown values of latent parameters
or not. The data and scripts required to reproduce the numerical results may be downloaded from
https://github.com/hi-chi/Machine-Learning (the relevant examples are located in the ”Focus ML”
folder).
B.
Methods and metrics
The cumulative energy ﬂux in the focal plane can be treated as a single-channel image, see
Fig. 2. Neural networks are one of the most versatile methods for analyzing data with the same
type of continuous features. For image analysis, the best results at the moment are shown by
convolutional neural networks [22, 23] and transformers [24, 25]. It is known that transformers are
diﬃcult to train, they are very demanding on the amount of data, and also require pre-training. At
the moment, in computer vision problems, there are not a large number of successful applications
of this method without model pre-training [26, 27]. Therefore, convolutional neural networks were
chosen for the ML-based analysis of the ﬂux.
After several experiments a convolutional neural net architecture was chosen that consists of
two consecutive blocks. Each block included two convolutional layers and a max pooling layer,
with the number of convolutions 16 and 32 in each block, respectively. These two blocks were
followed by four fully connected layers with the number of neurons 1024, 512, 128, 32, and ﬁnally
there was a layer that predicts 6 tilt parameters. ReLU was used as an activation function on each
convolutional and fully connected layer, except for the last one. For training, the root-mean-square
error and the Adam optimizer with default parameters in the Keras framework were used. The
model was trained for 30 epochs.
To assess the quality of ML-models in our study we computed the Mean Absolute Percentage
Error (MAPE) and the coeﬃcient of determination (R2):
MAPE = 100
n
n
X
i=1
| byi −yi|
max(by) ,
(8)
R2 = 1 −
n
X
i=1
( byi −yi)2
(y −yi)2 ,
(9)
where byi and yi are the true and the predicted value of the i-th object, respectively, and y is the
value of the predicted parameter averaged over the training set.
For the reconstructed parameters a linear transformation to the range from -1 to 1 was used.
Each energy ﬂux proﬁle was normalized in the range from zero to one. In all experiments Keras
and Tensorﬂow frameworks were used to train neural networks.
C.
The solution of the inverse problem
Our goal was to reconstruct the tilt amplitude ai and the tilt angles θi for three spectral
components of a laser pulse based on the proﬁle of the cumulative energy ﬂux in the focal plane. The
study of the data and experiments showed that in order to achieve good accuracy the reconstructed
parameters should be carefully chosen. First, the tilt angles θi have an obvious periodicity with
a period of 2π, and therefore require a special treatment. There are diﬀerent approaches to this
problem, for example, using a special loss function that takes into account the periodicity of
angles, or reconstructing trigonometric functions of angles instead of angles themselves. Second,
### Page 6

6
when the tilt amplitude ai is small, the dependence of the ﬂux on the corresponding tilt angle θi
becomes weak, i.e. speciﬁc angle values are indistinguishable for the ML-model, which leads to
a strong increase in the angles-related error. This is caused by the fact that the tilt angle and
amplitude are not used separately in computation of the additional phase ϕi (see Eq. 4), but as the
product of the tilt amplitude and the trigonometric functions of the tilt angle. Experiments showed
that instead of reconstructing six original parameters ai and θi it makes sense to reconstruct six
derived parameters that are the combination of the original ones pi = ai sin θi, qi = ai cos θi. This
transformation can be interpreted as a transition from polar coordinates to Cartesian coordinates.
It should be noted that the proposed transformation is one-to-one, and the original parameters ai
and θi can be reconstructed from derived parameters, but the accuracy of angle reconstructing for
the close to zero tilt amplitude can still be poor.
The ML-model architecture and training parameters are described in Section 3.2.
For the
ML-model training an experimental dataset of 50000 samples was numerically generated.
The
experimental results showed that the parameters pi, qi are reconstructed with an accuracy close to
ideal (see Table I). It should be noted that the parameters p1 and q1 are reconstructed worse than
other parameters, although the accuracy is still high. This eﬀect is systematic and was observed
in all experiments. Apparently, this result is due to the fact that these parameters correspond to
the spectral component with the shortest wavelength, information about which is worse extracted
from the cumulative energy ﬂux. The accuracy of reconstructing of the parameters related to the
central spectral component p0 and q0 is the best, which can be explained by the fact that both its
amplitude and the central wavelength are ﬁxed. Thus, the use of a convolutional network makes
it possible to solve the inverse problem with a very high accuracy.
TABLE I: Average values and standard deviations of the coeﬃcient of determination (R2) and the mean
error (MAPE) for reconstructing of derived parameters pi and qi by trained convolutional network. Metrics
were averaged over 10 runs with diﬀerent splits into training and test samples in a 90/10 ratio.
Metrics
p0
p1
p2
q0
q1
q2
R2
0.991 ± 0.001 0.948 ± 0.006 0.981 ± 0.003 0.991 ± 0.002 0.951 ± 0.006 0.982 ± 0.003
MAPE, %
2.71 ± 0.21
5.70 ± 0.42
3.77 ± 0.32
2.74 ± 0.24
5.66 ± 0.45
3.78 ± 0.33
D.
Analysis of the generalization ability of the ML-model
1.
The main idea.
In the previous section, we demonstrated the high accuracy of solving the inverse problem using
the convolutional neural network trained on model data. At the same time, the application of
ML-models trained on synthetic data to the real physical experiment can be problematic, because
the wrong choice of values of the latent parameters of the analytical model during training may
signiﬁcantly aﬀect the accuracy of the ML-model on experimental data, which is explained by a
change in the data distribution. In this section we address the ability of the ML-model to cope
with such negative eﬀects using synthetic test dataset with other values of the latent parameters.
For a better understanding of the importance of a correct choice of the latent parameters values,
it makes sense to visually evaluate the inﬂuence of the choice of boundary wavelengths λ1,2 and
relative amplitudes A1,2 on the cumulative energy ﬂux proﬁle in the considered analytical model
(see Fig. 2). Local changes in the energy distribution can be noticeable, for example the distribution
### Page 7

7
(a)
(b)
(c)
(d)
FIG. 2: Examples of the cumulative energy ﬂux distribution for diﬀerent values of latent parameters. (a,
b) λ1 and λ2 are diﬀerent, A1,2 are ﬁxed; (c,d) A1 and A2 are diﬀerent, λ1,2 are ﬁxed. Parameters ai and
θi are ﬁxed for (a), (b) and (c), (d).
at the bottom in Fig. 2 (a) is diﬀerent from the case with the same parameters except λ1,2 in Fig.
2 (b). Similar diﬀerences can be seen if compare Fig. 2 (c) and (d) where all parameters are
the same except relative amplitudes A1,2. These diﬀerences show the data variability, but what is
more important, is that the general shape of the energy ﬂux distribution in the proﬁle is preserved,
which indicates that a signiﬁcant part of the relevant information is contained in the tilt angles
and amplitudes.
This fact demonstrates the possibility of information generalization for diﬀerent values of latent
parameters, although the good result is not guaranteed. It is known that ML-models can overem-
phasize irrelevant information. For example, in adversarial attacks, when a change in the data is
selected in a special way to change the prediction of the network [28, 29]. There are also examples
when irrelevant features were changed in the data, which led to a dataset shift problem and a
decrease in the accuracy of the model [30, 31]. In this regard, it seems important to evaluate the
inﬂuence of the choice of latent parameters on the accuracy of the previously considered ML-model,
as well as the ability of the ML-model to extract relevant information even in the case of previously
unseen values of the latent parameters.
Based on this, the methodology for further experiments is following: the previously considered
convolutional network is trained from scratch on a subset of the data with a reduced set of latent
parameter values, and then it is tested on a test dataset that includes all values of latent parameters,
including those not present in the training dataset. By doing this we try to quantify the eﬀect of
wrong choice of latent parameters values during training on the ﬁnal accuracy of the ML-model.
The experiments are divided into two parts. In the ﬁrst part, the boundary wavelengths λ1,2 act as
the studied latent parameters, and in the second part, the same is done for the relative amplitudes
A1,2.
2.
Generalization for diﬀerent wavelengths.
In the ﬁrst experiment, the ML-model was trained on a newly generated dataset with
50000 samples with the values of the boundary wavelengths λ1 ∈[650 nm, 700 nm] and λ2 ∈
[900 nm, 950 nm]. The ML-model was tested on a dataset with 50000 samples from Section 3.3
with λ1 ∈[600 nm, 650 nm, 700 nm, 750 nm] and λ2 ∈[850 nm, 900 nm, 950 nm, 1000 nm]. All
other parameters were randomly changed. The model architecture and training parameters are the
same as described in Section 3.2. The results of the experiments are shown in Fig. 3.
It can be seen that the accuracy of determining the parameters on data with the boundary
wavelengths that are not included in the training set slightly decreases. The ML-model shows the
### Page 8

8
FIG. 3: The dependence of the coeﬃcient of determination R2 of all parameters on the boundary wavelengths
λ1,2. The coeﬃcient was averaged over 10 runs with random initialization of neural network weights. The
black square represents the training data subset. The coeﬃcient of determination is shown by gradation of
grey: the lower the coeﬃcient, the darker the color.
worst result when the values of the boundary wavelengths become close to each other. In this case,
the diﬀerence between the spectral components from diﬀerent spectral ranges decreases, which
complicates the reconstructing of parameter values.
3.
Generalization for diﬀerent amplitudes.
In the second experiment, the ML-model was trained on a newly generated dataset with
50000 samples with the values of the relative amplitudes A1,2 ∈[0.95, 1.1, 1.25, 1.4].
The
ML-model was tested on a dataset with 50000 samples from Section 3.3 with A1,2
∈
[0.5, 0.65, 0.8, 0.95, 1.1, 1.25, 1.4, 1.55, 1.7, 1.85, 2].
All other parameters were randomly changed.
The model architecture and training parameters are the same as those used in Section 3.2. The
results of the experiments are shown in Fig. 4.
It can be seen that with an increase in the diﬀerence between the values of the relative amplitudes
used during training and testing (when approaching the boundaries of the square in Fig. 4 (a)),
the accuracy decreases. At the same time, the accuracy in most cases remains acceptable, which
indicates the ability of the network to generalize the information received without over-ﬁtting for
### Page 9

9
(a)
(b)
FIG. 4:
The dependence of the coeﬃcient of determination R2 of (a) all parameters, (b) p1 parameter on
the relative amplitudes A1,2. The coeﬃcient was averaged over 10 runs with random initialization of neural
network weights. The black square represents the training data subset. The coeﬃcient of determination is
shown by gradation of grey: the lower the coeﬃcient, the darker the color.
speciﬁc values of latent parameters.
An error for diﬀerent parameters pi, qi contributes to the overall accuracy diﬀerently depending
on values of latent parameters A1,2. If we analyze in more detail the accuracy of reconstructing the
parameters p1, we can see that the accuracy falls sharply if the value of the parameter A1 decreases
(see Fig. 4 (b)). In this case, the relative contribution of this spectral component to the energy
ﬂux becomes smaller, which complicates the determination of its parameters. For parameters p2
and q2 the situation is similar: when the value of the parameter A2 takes on minimum values,
the accuracy of reconstructing the parameters decreases. In the case of parameters p0 and q0,
the accuracy deteriorates when the values of the parameters A1 or A2 are close to the maximum
values. Thus, it can be summarized that in the case of a change in the relative amplitudes of
various spectral components, the key factor is the distinguishability of the corresponding spectral
component against the background of others. In other words, the relative energy contribution of
the spectral component to the cumulative energy ﬂux should be noticeable.
IV.
DISCUSSION
This article is devoted not only to solving the problem of reconstructing the tilt parameters of
a laser pulse, but to a greater extent to studying the generalization ability of the ML-model. The
results of the experiment, when the ML-model is trained on some values of latent parameters, and
tested on other values, can be treated diﬀerently. From the point of view of latent parameters, the
available information is extrapolated by the ML-model beyond the set of parameters values used for
training. Generally speaking, the possibility of solving such type of problems with high accuracy is
not guaranteed, because the data distribution is diﬀerent on training and testing datasets, which
generally leads to the dataset shift problem. Fortunately, in the problem under consideration, it is
the values of the reconstructed tilt parameters that mainly determine the energy ﬂux distribution,
### Page 10

10
while the latent parameters lead only to its modiﬁcation. This fact explains the good generalization
ability of the model, which makes it possible to optimistically assess the possibility of its application
in the case when the values of latent parameters are unknown and, as an ultimate case, to real
experimental data.
In the context of applying the trained ML-model to real experimental data, it should be noted
that in this work a simpliﬁed pulse model was used, when the entire spectrum of the laser pulse was
divided only into three spectral components. In the case of adapting the model to a real physical
experiment, when the wavefront has a complex structure, such a partition must be done into a
larger number of spectral components. In this regard, it is important to note that in our numerical
experiments it was observed a systematic eﬀect of deterioration in the accuracy of reconstructing
the parameters of spectral components with a small wavelength or relative amplitude. In addition,
the eﬀect of reducing the accuracy was observed in the case when the boundary wavelengths be-
come close, i.e. one of the spectral ranges becomes very narrow. In all these cases, the inﬂuence
of such spectral components on the energy ﬂux decreases, which makes it diﬃcult to reconstruct
the corresponding tilt parameters. In addition, cross-inﬂuence of spectral components with close
wavelengths on each other is possible, when the values of tilt parameters from one spectral com-
ponent can be erroneously attributed by the ML-model to another. The probability of this kind
of errors increases sharply with a decrease of the spectral component width, because the relative
energy contribution to the cumulative energy ﬂux will also decrease. This means that in the case
of partitioning into a large number of spectral components, the characteristics of which may be
close, the accuracy of simple ML-models may deteriorate signiﬁcantly, which will require the use
of more complex ML-models or approaches.
V.
CONCLUSION
In this paper an ML-based approach for determining the parameters of the spectral-dependent
tilt of a focused laser pulse based on the cumulative energy ﬂux in the focal plane was proposed.
A simpliﬁed formulation of the problem was given with the division of the spectrum of a laser
pulse into three spectral components with an individual setting of the tilt parameters for each of
them. It was shown that it is possible to obtain good accuracy of tilt parameters reconstructing
using the convolutional neural network. In order to study the generalization ability of the proposed
ML-model the methodology based on the study of the inﬂuence of the latent parameters choice
on the accuracy of the ML-model was used.
For this purpose separate datasets with diﬀerent
subsets of the latent parameters values were used during training and testing. Two experiments
were carried out in which the boundary wavelengths and relative amplitudes acted as such latent
parameters. In both experiments, it was shown that the network has good generalization ability and
can reconstruct the tilt parameters with quite good accuracy even for the latent parameter values
not included in the training set. Signiﬁcant degradation of accuracy was observed only in cases
where the relative energy contribution of the spectral component to the energy ﬂux became small.
These results indicate that the proposed approach is promising even in the presence of uncertainty
in the choice of the latent parameter values that are typical for application of analytical models to
a real experiment.
Acknowledgments
This research was funded by the Ministry of Science and Higher Education of the Russian
Federation, agreement number 075-15-2020-808. The authors would like to thank Julien Ferri for
useful discussions and other contributions. The authors acknowledge the use of computational
### Page 11

11
resources provided by the Lobachevsky University and Joint Supercomputer Center of the Russian
Academy of Sciences.
[1] V. Yanovsky, V. Chvykov, G. Kalinchenko, P. Rousseau, T. Planchon, T. Matsuoka, A. Maksimchuk,
J. Nees, G. Cheriaux, G. Mourou, and K. Krushelnick, Ultra-high intensity-300-TW laser at 0.1 Hz
repetition rate., Optics express, 16 (3), 2109-2114 (2008).
[2] A. S. Pirozhkov, Y. Fukuda, M. Nishiuchi, H. Kiriyama, A. Sagisaka, K. Ogura, M. Mori, M. Kishimoto,
H. Sakaki, N. P. Dover, K. Kondo, N. Nakanii, K. Huang, M. Kanasaki, K. Kondo, and M. Kando,
Approaching the diﬀraction-limited, bandwidth-limited Petawatt, Optics express, 25 (17), 20486–20501
(2017).
[3] G. Tiwari, E. Gaul, M. Martinez, G. Dyer, J. Gordon, M. Spinks, T. Toncian, B. Bowers, X. Jiao,
R. Kupfer, L. Lisi, E. McCary, R. Roycroft, A. Yandow, G. D. Glenn, M. Donovan, T. Ditmire, and
B. M. Hegelich, Beam distortion eﬀects upon focusing an ultrashort petawatt laser pulse to greater
than 1022 W/cm2, 44 (11), 2764–2767 (2019).
[4] J. W. Yoon, Y. G. Kim, I. W. Choi, J. H. Sung, H. W. Lee, S. K. Lee, and C. H. Nam, Realization of
laser intensity over 1023 W/cm2, Optica, 8 (5), 630-635 (2021).
[5] A. Higginson, R. J. Gray, M. King, R. J. Dance, S. D. R. Williamson, N. M. H. Butler, R. Wilson,
R. Capdessus, C. Armstrong, J. S. Green, S. J. Hawkes, P.
Martin, W. Q. Wei, S. R. Mirfayzi,
X. H. Yuan, S. Kar, M. Borghesi, R. J. Clarke, D. Neely, and P. McKenna, Near-100 MeV protons via
a laser-driven transparency-enhanced hybrid acceleration scheme, Nature communications, 9 (1), 1–9
(2018).
[6] A. J. Gonsalves, K. Nakamura, J. Daniels, C. Benedetti, C. Pieronek, T. C. H. de Raadt, S. Steinke,
J. H. Bin, S. S. Bulanov, J. van Tilborg, C. G. R. Geddes, C.
B. Schroeder, Cs. T´oth, E. Esarey,
K. Swanson, L. Fan-Chiang, G. Bagdasarov, N.
Bobrova, V. Gasilov, G. Korn, P. Sasorov, and
W. P. Leemans, laser guiding and electron beam acceleration to 8 GeV in a laser-heated capillary
discharge waveguide, Physical review letters, 122 (8), 084801 (2019).
[7] G. Sarri, D. J. Corvan, W. Schumaker, J. Cole, A. Di Piazza, H. Ahmed, C. Harvey, C. H. Keitel,
K. Krushelnick, S. P. D. Mangles, Z. Najmudin, D. Symes, A. G. R. Thomas, M. Yeung, Z. Zhao, and
M. Zepf, Ultrahigh brilliance multi-MeV γ-ray beams from nonlinear relativistic Thomson scattering,
Physical review letters, 113 (22), 224801 (2014).
[8] A. Di Piazza, C. M¨uller, K. Z. Hatsagortsyan, and C. H. Keitel, Extremely high-intensity laser inter-
actions with fundamental quantum systems, Reviews of Modern Physics, 84 (3), 1177 (2012).
[9] D. Strickland, and G. Mourou, Compression of ampliﬁed chirped optical pulses, Optics communications,
55 (6), 447–449 (1985).
[10] K. T. Kim, C. Zhang, A. D. Shiner, S. E. Kirkwood, E. Frumker, G. Gariepy, A. Naumov, D. M. Vil-
leneuve, and P. B. Corkum, Manipulation of quantum paths for space-time characterization of attosec-
ond pulses, Nature Physics, 9 (3), 159–163 (2013).
[11] C. Bourassin-Bouchet, M. M. Mang, F. Delmotte, P. Chavel, and S. de Rossi, How to focus an attosec-
ond pulse, Optics express, 21 (2), 2506-2520 (2013).
[12] G. Pariente, V. Gallet, A. Borot, O. Gobert, and F. Qu´er´e, Space-time characterization of ultra-intense
femtosecond laser beams, Nature Photonics, 26 (20), 26444–26461 (2018).
[13] A. Borot, and F. Qu´er´e, Spatio-spectral metrology at focus of ultrashort lasers: a phase-retrieval
approach, Optics express, 26 (20), 26444–26461 (2018).
[14] A. Jeandet, A. Borot, K. Nakamura, S. W. Jolly, A. J. Gonsalves, C. Toth, H. S. Mao, W. P. Leemans,
and F. Qu´er´e, Spatio-temporal structure of a petawatt femtosecond laser beam, Journal of Physics:
Photonics, 1 (3), 035001 (2019).
[15] M. A. Krumb¨ugel, C. L. Ladera, K. W. DeLong, D. N. Fittinghoﬀ, J. N. Sweetser, and R. Trebino, Direct
ultrashort-pulse intensity and phase retrieval by frequency-resolved optical gating and a computational
neural network, Optics letters, 21 (2), 143–145 (1996).
[16] J. W. Nicholson, F. G. Omenetto, D. J. Funk, and A. J. Taylor, Evolving FROGS: phase retrieval from
frequency-resolved optical gating measurements by use of genetic algorithms, Optics letters, 24 (7),
490–492 (1999).
### Page 12

12
[17] T. Zahavy, A. Dikopoltsev, D. Moss, G. I. Haham, O. Cohen, S. Mannor, and M. Segev, Deep learning
reconstruction of ultrashort pulses, Optica, 5 (5), 666–673 (2018).
[18] S. Kleinert, A. Tajalli, T. Nagy, and U. Morgner, Rapid phase retrieval of ultrashort pulses from
dispersion scan traces using deep neural networks, Optics letters, 44 (4), 979–982 (2019).
[19] R. Ziv, A. Dikopoltsev, T. Zahavy, I. Rubinstein, P. Sidorenko, O. Cohen, and M. Segev, Deep learning
reconstruction of ultrashort pulses from 2D spatial intensity patterns recorded by an all-in-line system
in a single-shot, Optics express, 28 (5), 7528–7538 (2018).
[20] W. Xiong, B. Redding, S. Gertler, Y. Bromberg, H. D. Tagare, and H. Cao, Deep learning of ultrafast
pulses with a multimode ﬁber, APL Photonics, 5 (9), 096106 (2020).
[21] E. Panova, V. Volokitin, E. Eﬁmenko, J. Ferri, T. Blackburn, M. Marklund, A. Muschet, A. Gonzalez,
P. Fischer, L. Veisz, I. Meyerov, and A. Gonoskov, Optimized Computation of Tight Focusing of Short
Pulses Using Mapping to Periodic Space, Applied Sciences, 11 (3), 956 (2021).
[22] Y. LeCun, L. Bottou, Y. Bengio, and P. Haﬀner, Gradient-based learning applied to document recog-
nition, Proceedings of the IEEE, 86 (11), 2278–2324 (1998).
[23] A. Krizhevsky, I. Sutskever and G. E. Hinton, Imagenet classiﬁcation with deep convolutional neural
networks, Advances in neural information processing systems, 25, (2012).
[24] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser and I. Polosukhin,
Attention is all you need, Advances in neural information processing systems, 30, (2017).
[25] A. Dosovitskiy, L. Beyer, A. Kolesnikov, D. Weissenborn, X. Zhai, T. Unterthiner, M. Dehghani,
M. Minderer, G. Heigold, S. Gelly, J. Uszkoreit, N. Houlsby, An image is worth 16x16 words: Trans-
formers for image recognition at scale, arXiv preprint arXiv:2010.11929, (2020).
[26] M. Caron, H. Touvron, I. Misra, H. J´egou, J. Mairal, P. Bojanowski, and A. Joulin, Emerging proper-
ties in self-supervised vision transformers, Proceedings of the IEEE/CVF International Conference on
Computer Vision, 9650–9660 (2021).
[27] H. Touvron, M. Cord, M. Douze, F. Massa, A. Sablayrolles, and H. J´egou, Training data-eﬃcient image
transformers & distillation through attention, International Conference on Machine Learning. - PMLR,
10347–10357 (2021).
[28] I. J. Goodfellow, J. Shlens and C. Szegedy, Explaining and harnessing adversarial examples, arXiv
preprint arXiv:1412.6572, (2014).
[29] X. Yuan, P. He, Q. Zhu, and X. Li, Adversarial examples: Attacks and defenses for deep learning.
IEEE transactions on neural networks and learning systems, 30(9), 2805–2824 (2019).
[30] M. Wang and W. Deng, Deep visual domain adaptation: A survey, Neurocomputing, 312, 135–153
(2018).
[31] G. Wilson, and D. J. Cook, A survey of unsupervised deep domain adaptation, ACM Transactions on
Intelligent Systems and Technology (TIST), 11(5) 1–46 (2020).