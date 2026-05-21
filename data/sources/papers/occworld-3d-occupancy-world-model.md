# OccWorld 3D Occupancy World Model

**Source**: arxiv PDF, 34 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Calibrated Explanations for Regression
Tuwe L¨ofstr¨om1*, Helena L¨ofstr¨om1, Ulf Johansson1,
Cecilia S¨onstr¨od1, Rudy Matela1
1*J¨onk¨oping AI Lab (JAIL), Department of Computing, J¨onk¨oping
University, Box 1026, J¨onk¨oping, 55111, Sweden.
*Corresponding author(s). E-mail(s): tuwe.lofstrom@ju.se;
Contributing authors: helena.lofstrom@ju.se; ulf.johansson@ju.se;
cecilia.sonstrod@ju.se; rudy.matela@ju.se;
Abstract
Artificial Intelligence (AI) is often an integral part of modern decision support
systems. The best-performing predictive models used in AI-based decision sup-
port systems lack transparency. Explainable Artificial Intelligence (XAI) aims to
create AI systems that can explain their rationale to human users. Local explana-
tions in XAI can provide information about the causes of individual predictions in
terms of feature importance. However, a critical drawback of existing local expla-
nation methods is their inability to quantify the uncertainty associated with a
feature’s importance. This paper introduces an extension of a feature importance
explanation method, Calibrated Explanations, previously only supporting clas-
sification, with support for standard regression and probabilistic regression, i.e.,
the probability that the target is above an arbitrary threshold. The extension for
regression keeps all the benefits of Calibrated Explanations, such as calibration of
the prediction from the underlying model with confidence intervals, uncertainty
quantification of feature importance, and allows both factual and counterfactual
explanations. Calibrated Explanations for standard regression provides fast, reli-
able, stable, and robust explanations. Calibrated Explanations for probabilistic
regression provides an entirely new way of creating probabilistic explanations
from any ordinary regression model, allowing dynamic selection of thresholds.
The method is model agnostic with easily understood conditional rules. An imple-
mentation in Python is freely available on GitHub and for installation using both
pip and conda, making the results in this paper easily replicable.
Keywords: Explainable AI, Feature Importance, Calibrated Explanations,
Uncertainty Quantification, Regression, Probabilistic Regression, Counterfactual
Explanations, Conformal Predictive Systems
1
arXiv:2308.16245v3  [cs.LG]  25 May 2024
### Page 2

1 Introduction
In recent times, Decision Support Systems in various domains such as retail, sport,
or defence have been incorporating Artificial Intelligence (AI) extensively [1]. How-
ever, the predictive models used in AI-based Decision Support Systems generally lack
transparency and only provide probable results [2, 3]. This can result in misuse (when
users rely on it excessively) or disuse (when users do not rely on it enough) [4, 5].
The lack of transparency has led to the development of eXplainable Artificial Intel-
ligence (XAI), which aims to create AI systems capable of explaining their reasoning
to human users. The goal of explanations is to support users in identifying incorrect
predictions, especially in critical areas such as medical diagnosis [6]. An explanation
provided by XAI should highlight the underlying model’s strengths and weaknesses
and provide insight into how it will perform in the future [2, 7].
Regarding explanations in XAI, there are two types: local and global. Local expla-
nations focus on the reasons behind individual predictions, while global explanations
provide information about the entire model [8–10]. Despite the apparent strength
stemming from the possibility of providing explanations for each instance, local expla-
nations typically have some drawbacks. For example, they can be instable, meaning
that the same model and instance may result in different explanations, or they can
lack robustness, meaning that minor differences in the instance can lead to signifi-
cantly different explanations [11, 12]. Instability and lack of robustness create issues
when evaluating the quality of the explanations. Metrics like fidelity, which measure
how well an explanation captures the behaviour of the underlying model, do not give
an accurate picture of explanation quality since they depend heavily on the details of
the explanation method [9, 11, 13–18]. Furthermore, even the best explanation tech-
niques offer limited insight into model uncertainty and reliability. Recent research has
emphasized uncertainty estimation’s role in enhancing the transparency of underlying
models [11, 19]. Although achieving well-calibrated uncertainty has been underscored
as a critical factor in fostering transparent decision-making, Bhatt et al. [19] point out
the challenges and complexities of obtaining accurately calibrated uncertainty esti-
mates for complex problems. Moreover, as indicated by Slack et al. [11], the focus has
predominantly leaned towards adopting a well-calibrated underlying model (such as
Bayesian) rather than relying on calibration techniques.
The probability estimate that most classifiers output is commonly used as an indi-
cator of the likelihood of each class in local explanation methods for classification.
However, it is widely recognized that these classifiers are often poorly calibrated,
resulting in probability estimates that do not faithfully represent the actual proba-
bility of correctness [20]. Specialized calibration techniques such as Platt Scaling [21]
and Venn-Abers (VA) [22] have been proposed to tackle these shortcomings. The VA
method generates a probability range associated with each prediction, which can be
refined into a properly calibrated probability estimate utilizing regularisation.
When employing the VA approach for decision-making, it is essential to recognize
that the technique provides intervals for the positive class. These intervals quantify the
uncertainty within the probability estimate, offering valuable insights from an explana-
tory standpoint. The breadth of the interval directly corresponds to the model’s level
of uncertainty, with a narrower interval signifying more confidence in the probability
2
### Page 3

estimate. In comparison, a broader interval indicates more substantial uncertainty in
said estimates. The uncertainty information can be extended to the features, given that
the feature weights are informed by the prediction’s probability estimate. Being able to
quantify the uncertainty of feature weights can improve the quality and usefulness of
explanations in XAI. Recently, a local explanation method, Calibrated Explanations,
utilizing the intervals provided by VA to estimate feature uncertainty was introduced
for classification [23].
In recent years, conformal prediction has increasingly been integrated into research
about XAI methods, although not focusing on the uncertainty aspect per se. The
focus has primarily been on interpretable models [24], increasing the fidelity between
model and explanations [25], lowering the computational cost [26] and explaining reject
options [27–29]. Explaining reject options has been defined as an explanation of the
uncertainty integral in taking a decision.
Existing explanation methods most commonly focus on explaining decisions from
classifiers, despite the fact that regression is widely used in highly critical situations.
Due to the lack of specialized explanation techniques for regression, applying methods
designed for classification on regression problems is not unusual, highlighting the need
for well-founded explanation methods for regression [30].
The aim of this study is to propose an explanation method - with the same possi-
bility of quantifying the uncertainty of feature weights that Calibrated Explanations
provides, through VA, for classification - for a regression context. The conformal
prediction framework [31] provides several different techniques for quantifying uncer-
tainty in a regression context. In this paper, the Conformal Predictive Systems (CPSs)
technique [32] for uncertainty estimation is used in Calibrated Explanations to allow
creation of calibrated explanations with uncertainty estimation for regression. CPSs
is not only a very flexible technique, providing a rich set of tools to be used for uncer-
tainty quantification, but it also allows for estimating the probability that the target
is above any user-defined threshold. Based on this, a new form of probabilistic expla-
nation for regression is also proposed in this paper. These approaches are user-friendly
and model-agnostic, making them easy to use and applicable to diverse underlying
models.
In summary, this paper introduces extensions of Calibrated Explanations aimed at
regression, with the following characteristics:
• Fast, reliable, stable and robust feature importance explanations for regression.
• Calibration of the predictions from the underlying model through the application
of CPSs.
• Explanations with arbitrary forms of uncertainty quantification of the predictions
from the underlying model and the feature importance weights through querying
of the conformal predictive distribution (CPD) derived from the CPS.
• Possibility of creating explanations of the probability that the prediction exceeds
a user-defined threshold, with uncertainty quantification.
• Rules with straightforward interpretation in relation to the feature values and
the target.
• Possibility to generate counterfactual rules with uncertainty quantification of the
expected predictions (or probability of exceeding a threshold).
3
### Page 4

• Conjunctive rules can be created, conveying feature importance for the interaction
of included features.
• Distribution as an open source Python package, making the proposed techniques
easily accessible for both scientific and industrial purposes.
2 Background
2.1 Post-Hoc Explanation Methods
The research area of XAI can be broadly categorized into two main types: developing
inherently interpretable and transparent models and utilizing post-hoc methods to
explain opaque models. Post-hoc explanation techniques seek to construct simplified
and interpretable models that reveal the relationship between feature values and the
model’s predictions. These explanations, which can be either local or global, often
leverage visual aids such as pixel representations, feature importance plots, or word
clouds, emphasizing the features, pixels, or words accountable for causing the model’s
predictions [9, 33].
Two distinct approaches of explanations exist: factual explanations, where a fea-
ture value directly influences the prediction outcome, and counterfactual explanations,
which explore the potential impact on predictions when altering a feature’s values
[34–36]. Importantly, counterfactual explanations are intrinsically local. They are
particularly human-friendly, mirroring how human reasoning operates [33].
2.2 Essential Characteristics of Explanations
Creating high-quality explanations in XAI requires a multidisciplinary approach that
draws knowledge from both the Human-Computer Interaction and the Machine Learn-
ing fields. The quality of an explanation method depends on the goals it addresses,
which may vary. For instance, assessing how users appreciate the explanation inter-
face differs from evaluating if the explanation accurately mirrors the underlying model
[37]. However, specific characteristics are universally desirable for post-hoc explanation
methods. It is crucial that an explanation method accurately reflects the underlying
model, which is closely related to the concept that an explanation method should have
a high level of fidelity to the underlying model [11]. Therefore, a reliable explanation
must have feature weights that correspond accurately to the actual impact on the
estimates to correctly reflect the model’s behavior [19].
Stability and robustness are two additional critical features of explanation meth-
ods [7, 18, 38]. Stability refers to the consistency of the explanations [11, 14]; the
same instance and model should produce identical explanations across multiple runs.
On the other hand, robustness refers to the ability of an explanation method to pro-
duce consistent results even when an instance undergoes small perturbations [7] or
other circumstances change. Therefore, the essential characteristics of an explanation
method in XAI are that it should be reliable, stable, and robust.
4
### Page 5

2.3 Explanations for classification and regression
Distinguishing between explanations for classification and regression lies in the nature
of the insights they offer. In classification, the task involves predicting the specific class
an instance belongs to from a set of predefined classes. The accompanying probabil-
ity estimates reflect the model’s confidence level for each class. Various explanation
techniques have been developed for classifiers to clarify the rationale behind the class
predictions. Notable methods include SHAP [39], LIME [3], and Anchor [40]. These
techniques delve into the factors that contribute to the assignment of a particular
class label. Typically, the explanations leverage the concept of feature importance,
e.g., words in textual data or pixels in images.
In regression, the paradigm shifts as there are no predetermined classes or cate-
gorical values. Instead, each instance is associated with a numerical value, and the
prediction strives to approximate this value. Consequently, explanations for regression
models cannot rely on the framework of predefined classes. Nevertheless, explana-
tion techniques designed for classifiers, as mentioned above, can often be applied to
regression problems, provided these methods concentrate on attributing features to
the predicted instance’s output.
2.4 Venn-Abers predictors
Probabilistic predictors offer class labels and associated probability distributions. Val-
idating these predictions is challenging, but calibration focuses on aligning predicted
and observed probabilities [31]. The goal is well-calibrated models where predicted
probabilities match actual accuracy. Venn predictors [41] produce multi-probabilistic
predictions, converted to confidence-based probability intervals.
Inductive Venn prediction [42] involves a Venn taxonomy, categorizing calibration
data for probability estimation. Within each category, the estimated probability for
test instances falling into a category is the relative frequency of each class label among
all calibration instances in that category.
Venn-Abers predictors (VA) [22] offer automated taxonomy optimization via iso-
tonic regression, thus introducing dynamic probability intervals. A two-class scoring
classifier assigns a prediction score si to an object xi. A higher score implies higher
belief in the positive class. In order to calibrate a model, some data must be set
aside and used as a calibration set when using inductive VA predictors. Consequently,
split the training set {z1, . . . , zi, . . . , zn}, with objects xi and labels yi, into a proper
training set ZT and a calibration set {z1, . . . , zq}1. Train a scoring classifier on ZT to
compute s for {x1, . . . , xq, x}, where x is the object of the test instance z2. Inductive
VA prediction follows these steps:
1. Derive isotonic calibrators g0 and g1 using {{s1, y1}, . . . , {sq, yq}, {s, y = 0}} and
{{s1, y1}, . . . , {sq, yq}, {s, y = 1}}, respectively.
2. The probability interval for y = 1 is [g0(s), g1(s)] (henceforth referred to as
[Pl, Ph], representing the lower and upper bounds of the interval).
1As we assume random ordering, the calibration set is indexed 1, . . . , q rather than |ZT | + 1, . . . , n, for
indexing convenience.
2The index n + 1 is dropped for indexing convenience whenever referring to the test instance (like
zn+1, xn+1 or yn+1) or values dependent on the test instance (like sn+1).
5
### Page 6

3. Obtain a regularized probability estimate for y = 1 using the recommendation
by [22]:
P =
Ph
1 −Pl + Ph
Since the class label of the test instance must be either positive or negative in binary
classification, and the lower and upper bounds are the relative frequencies calculated
from the calibration set (including the test instance with the positive or negative label
assigned), one of them must be the correctly calibrated probability estimate. Thus,
the probability interval is well-calibrated provided the data is exchangeable.
In summary, VA produces a calibrated (regularized) probability estimate P
together with a probability interval with a lower and upper bound [Pl, Ph].
2.5 Calibrated Explanations for Classification
Below is an introduction to Calibrated Explanations for classification [23], which pro-
vides the foundation to this paper’s contribution. In the following descriptions, a
factual explanation is composed of a calibrated prediction from the underlying model
accompanied by an uncertainty interval and a collection of factual feature rules, each
composed of a feature weight with an uncertainty interval and a factual condition,
covering that feature’s instance value. Counterfactual explanations only contain a col-
lection of counterfactual feature rules, each composed of a prediction estimate with
an uncertainty interval and a counterfactual condition, covering alternative instance
values for the feature. The prediction estimate represents a probability estimate for
classification, whereas for regression, the prediction estimate will be expressed as a
potential prediction.
2.5.1 Factual Calibrated Explanations for Classification
Calibrated Explanations is applied to an underlying model with the intention of
explaining its predictions of individual instances using rules conveying feature impor-
tances. The following is a high-level description of how Calibrated Explanations for
classification works, following the original description in [23] closely:
Let us assume that a scoring classifier, trained using the proper training set ZT ,
exists for which a local explanation for test object x is wanted. Use VA as a calibrator
and calibrate the underlying model for x to get the probability interval [Pl, Ph] and the
calibrated probability estimate P. For each feature f, use the calibrator to estimate
probability intervals ([P′
l.f, P′
h.f]) and calibrated probability estimates (P′
f) for slightly
perturbed versions of object x, changing one feature at a time in a systematic way (see
the detailed description below). To get the feature weight (and uncertainty interval) for
feature f, calculate the difference between P to the average of all P′
f (and [P′
l.f, P′
h.f])3:
wf = P −
1
|Vf| −1
X
P′
f,
(1)
3Exclude P (and [Pl, Ph]), i.e., the calibrator’s results on x. There may be alternatives to how we compute
these weights (see Section 6.1).
6
### Page 7

wf
l = P −
1
|Vf| −1
X
P′
l.f,
(2)
wf
h = P −
1
|Vf| −1
X
P′
h.f,
(3)
where |Vf| −1 is the number of perturbed values.
The feature weight is exactly defined to be the difference between the calibrated
probability estimate on the original test object x and the estimated (average) cali-
brated probability estimate achieved on the perturbed versions of x. The upper and
lower bounds are defined analogously using the probability intervals from the per-
turbed versions of x. As long as the same test object, underlying model and calibration
set is used, the resulting explanation will also be the same.
More formally, the following steps are pursued to achieve a factual explanation for
a test object x:
1. Use the calibrator to get the probability interval [Pl, Ph] and the calibrated
probability estimate P for x.
2. Separate all features into categorical features C and numerical features N. Define
a discretizer for numerical features that define thresholds and smaller-or-equal-
or greater-than-conditions (≤, >) for these features4.
3. For each feature f ∈C:
(a) Iterate over all possible categorical values v ∈Vf and create a perturbed
instance exchanging the feature value of xf with one value at a time, creating
a perturbed instance x′
f = v.
(b) Calculate and store the probability intervals [P′
l.f, P′
h.f] and the calibrated
probability estimate P′
f for the perturbed instance. Calculate the weights
using equations (1), (2), and (3).
(c) Define a factual condition using the the feature f, the value v and the identity
condition (=).
4. For each feature f ∈N:
(a) Use the thresholds of the discretizer to identify the closest lower or upper
threshold t surrounding the feature value of xf. Divide all possible feature
values in the calibration set for feature f into two groups Vf separated by t.
(b) Within each group, percentile values pv representing the 25th, 50th and 75th
percentiles are extracted. Iterate over the values in pv and create a perturbed
instance exchanging the feature value of xf with one value at a time, creat-
ing a perturbed instance x′
fpv. Calculate and store the probability intervals
[P′
l.fpv, P′
h.fpv] and the calibrated probability estimate P′
fpv for the perturbed
instance. Average over all perturbed instances within the group, creating a
probability interval [P′
l.f, P′
h.f] and the calibrated probability estimate P′
f for
each group. Calculate the weights using equations (1), (2), and (3).
(c) Define a factual condition using threshold t and feature f. The ≤or >
condition is used so that the factual condition covers the instance value.
4This is done using a binary subclass of the EntropyDiscretizer class in LIME.
7
### Page 8

2.5.2 Counterfactual Calibrated Explanations for Classification
When creating factual explanations, the calibrator’s results from perturbed instances
are averaged to calculate feature importance and uncertainty intervals for each feature.
When generating counterfactual rules, the calibrator’s results for perturbed instances
are instead used to form counterfactual rules. For categorical features, one counterfac-
tual rule is created for each alternative categorical value, and for numerical features,
(up to) two rules, representing ≤-rules and >-rules, can be created5. Each feature
rule’s expected probability interval is already established as [P′
l.f, P′
h.f], following the
Calibrated Explanations process in steps 3 and 4 above, defining one feature rule for
each alternative instance value. The condition will be similar as in steps 3 and 4 above,
but for the alternative instance value v. Equation (1)’s feature weights are mainly
employed to sort counterfactual rules by impact. The calibrated probability estimate
P′
f is normally neglected in counterfactual rules for classification but is calculated and
can be used.
2.5.3 Conjunctive Calibrated Explanations
Each individual rule only conveys the contribution of an individual feature. To counter-
act this shortcoming, conjoined rules can be derived to estimate the joint contribution
between combinations of features. This is done separately from the generation of the
feature rules, by combining the established feature rules. For each combination of
existing rules, new perturbed instances are created by applying the already estab-
lished feature rule conditions, limiting the search space of conjunctions to consider to
the most important existing rules. Calibration is performed following the same logic
as for single feature perturbed instances, making it possible to get well-calibrated
conjunctive rules taking feature interaction into account.
3 Calibrated Explanations for Regression
The basic idea in Calibrated Explanations for classification is that each factual and
counterfactual explanation is derived using three calibrated values: The calibrated
probability and the probability interval represented by the lower and upper bound.
For regression, there are two natural use cases, where the obvious one is predicting
the continuous target value directly, i.e., standard regression. Another use case is to
instead predict the probability of the target being below (or above) a given threshold,
basically viewing the problem as a binary classification problem.
Conformal Predictive Systems (CPSs) produce Conformal Predictive Distributions
(CPDs), as mentioned in the introduction. CPDs are cumulative distribution func-
tions which can be used for various purposes, such as deriving prediction intervals for
specified confidence levels or obtaining the probability of the true target falling below
(or above) any threshold.
5All existing Discretizers in LIME can be used for counterfactual explanations. The EntropyDiscretizer
class is used by default for counterfactual classification.
8
### Page 9

3.1 Conformal Predictive Systems
Conformal prediction [31] offer predictive confidence by generating prediction regions,
which include the true target with a specified probability. These regions are sets of
class labels for classification or prediction intervals for regression.
Errors arise when the true target falls outside the region, yet conformal predictors
are automatically valid under exchangeability, yielding an error rate of ε over time.
Thus, the key evaluation criterion is efficiency, gauged by the region’s size and sharp-
ness for greater insight. Conformal regressors (CRs), specifically an inductive (split)
CR [43], follows these steps:
1. Divide the data into a proper training set ZT and a calibration set {z1, . . . , zq}.
2. Fit an underlying regression model h to ZT .
3. Define nonconformity as the absolute error |yi −h(xi)|.
4. Compute nonconformity scores for {z1, . . . , zq} and sort them in descending order
to obtain α1 ≤α2 ≤... ≤αq.
5. Assign an ε, e.g., 0.01, 0.05, or 0.1.
6. Calculate the (1 −ε)-percentile nonconformity score, αs, where index s =
⌊ε(q + 1)⌋.
7. For a new instance xi, the prediction interval is h(xi) ± αs.
To individualize intervals, the normalized nonconformity function [44] augments non-
conformity with σi and β. These adapt intervals based on predicted difficulty σi for
each yi. Normalized nonconformity is |yi−h(xi)|
σi+β
, and the interval is h(xi) ± αs(σi + β).
This approach yields individualized prediction intervals, accommodating prediction
difficulty and enhancing region informativeness.
The process of creating (normalized) inductive CPSs closely resembles the forma-
tion of inductive CRs [32]. The primary distinction lies in calculating nonconformity
scores using actual errors, defined as:
f (zi) = yi −h (xi) ,
(4)
or normalized errors:
f (zi) = yi −h (xi)
σi + β
,
(5)
where σi, xi, and β retain their prior definitions. The prediction for a test instance xi
(potentially with an estimated difficulty σi) then becomes the following CPD:
Q(y) =
(
i+τ
q+1, if y ∈
 C(i), C(i+1)

,
for i ∈{0, ..., q}
i′−1+(i′′−i′+2)τ
q+1
, if y = C(i),
for i ∈{1, ..., q}
(6)
where C(1), . . . , C(q) are obtained from the calibration scores α1, . . . , αq, sorted in
increasing order:
C(i) = h (x) + αi
or, when using normalization:
C(i) = h (x) + σαi
9
### Page 10

Fig. 1: A CPD with three different intervals representing 90% confidence are defined:
Lower-bounded interval: more than the 10th percentile; Two-sided interval:
between the 5th and the 95th percentiles; Upper-bounded interval: less than the
90th percentile. The black dotted lines indicate how to determine the probability of
the true target being smaller than 0.5, which in this case would be approximately 80%.
with C(0) = −∞and C(q+1) = ∞. τ is sampled from the uniform distribution U(0, 1)
and its role is to allow the P-values of target values to be uniformly distributed. i′′ is
the highest index such that y = C(i′′), while i′ is the lowest index such that y = C(i′)
(in case of ties). For a specific value y, the function returns the estimated probability
P(Y ≤y), where Y is a random variable corresponding to the true target.
Given a CPD:
• A two-sided prediction interval for a chosen significance level ε can be obtained
by [C⌊(ε/2)(q+1)⌋, C⌈(1−ε/2)(q+1)⌉]. Obviously, the interval does not have to be
symmetric as long as the covered range of percentiles are 1 −ε.
• One-sided prediction intervals can be obtained by [C⌊ε(q+1)⌋, ∞] for a lower-
bounded interval, and by [−∞, C⌈(1−ε)(q+1)⌉] for an upper-bounded interval.
• Similarly, a point prediction corresponding to the median of the distribution can
be obtained by (C⌈0.5(q+1)⌉+ C⌊0.5(q+1)⌋)/2. Since the median is an unbiased mid-
point in the distribution measured on the calibration set, the median prediction
can be seen as a calibration of the underlying models prediction. Unless the model
is biased, the median will tend to be very close to the prediction of the underlying
model.
10
### Page 11

Figure 1 illustrates how the CPD can form one-sided and two-sided confidence
intervals. It also illustrates how the probability of the true target falling below a given
threshold can be determined, as well as connecting a probability with the threshold it
corresponds to.
Compared to a CR, also able to provide valid confidence intervals from the under-
lying model, a CPS offers richer opportunities to define intervals and probabilities
through querying the CPD. One particular strength of a CPS is its ability to calibrate
the underlying model. As an example, if the underlying model is consistently overly
optimistic, the median from the CPS will adjust for that and provide a calibrated
prediction better adjusted to reality.
There are several different ways that difficulty (σ) can be estimated, such as:
• The (Euclidean) distances to the k nearest neighbors.
• The standard deviation of the targets of the k nearest neighbors.
• The absolute errors of the k nearest neighbors.
• The variance of the predictions of the constituent models, in case the underlying
model is an ensemble.
3.2 Factual and Counterfactual Explanations for Regression
In order to get factual Calibrated Explanations for regression, the probability inter-
vals [Pl, Ph] and a calibrated probability estimate P from VA are exchanged for a
confidence interval and the median which are derived from the CPD. The confidence
interval is defined by user-selected lower and upper percentiles and allows dynamic
selection of arbitrary confidence intervals.
Thus, for the algorithm to produce factual and counterfactual rules in the same way
as for classification, the only thing that needs to be adjusted in the algorithm described
in section 2.5.1 is to exchange the calibrator from VA to CPS. Since the confidence
interval from CPS is based on the user-provided percentiles, the lower and upper
percentiles are two necessary additional parameters. By default, the lower and upper
percentiles are [5th, 95th], resulting in a two-sided 90% confidence interval derived from
the CPD. One-sided intervals can in practice be handled as a two-sided interval with
either −∞or ∞assigned as lower or upper percentiles. The calibrated probability
estimate used in classification is exchanged for the median from the CPD, which in
practice represents a calibration of the underlying model’s prediction, neutralizing any
systematic bias in the underlying model. Consequently, using a CPS effectively enables
factual Calibrated Explanations for regression with uncertainty quantification of both
the prediction from the underlying model and each feature rule.
More formally, the confidence interval and the median are derived as follows:
1. Use the calibration set to calculate the calibration residuals
ri = yi −h(xi), i ∈{1, . . . , q}.
2. Fit a CPS model cps using the residuals.
3. Obtain the median and interval values
[m, l, h] = cps(h(x), percentiles = [50th, Pth
l , Pth
h ])
11
### Page 12

using the 50th, the lower Pth
l
and the higher Pth
h percentiles.
4. To create factual Calibrated Explanations for regression following the procedure
described in section 2.5.1 above, substitute P and [Pl, Ph] from the VA calibrator
with m and [l, h] from the CPS.
The input to the Calibrated Explanations differs between classification and regres-
sion: in classification, it is probability estimates; in regression, it is actual predicted
values. Thus, factual Calibrated Explanations for regression will result in feature
weights indicating changes in predictions rather than changes in probabilities.
3.3 Factual and Counterfactual Probabilistic Calibrated
Explanations for Regression
The simplest approach when trying to predict the probability that a target value is
below (or above) a threshold is to treat the problem as a binary classification problem,
with the target defined as
˙yi =
(
1
if yi ≤t
0
if yi > t,
(7)
where y are the regression targets, t the threshold, and ˙y the binary classification
target. To obtain the probability, some form of probabilistic classifier is used.
The CPS makes it possible to query any regular regression model for the probability
of the target falling below any given threshold. This effectively eliminates the need to
treat the problem as a classification problem.
Utilizing this strength to create explanations is straightforward when only the
probability is of interest. However, there is no obvious equivalent to the probabil-
ity interval created by VA in classification or the confidence interval derived from a
CPS in regression. Consequently, achieving a calibrated explanation with uncertainty
quantification for this scenario is not as easy as creating factual and counterfactual
explanations for classification or regression.
The fact that probabilistic predictions for regression can be achieved by viewing it
as a classification problem holds a key to a solution. VA needs a score s for both the
calibration and the test instances. By using a CPS as a probabilistic scoring function
for both calibration and test instances, it becomes possible to use VA to calibrate
the probability and provide a probability interval. The score used is the probability
(from a CPD) of calibration and test instances being below the given threshold. The
isotonic regressors used by VA also need a binary target for the calibration set, which
is defined using equation (7).
Since the CPS is defined using the calibration set, the probabilities achieved on the
same calibration set will be biased and consequently not be entirely trustworthy. To
counteract that, the original calibration set is split in halves, and one half is used as a
calibration set for CPS while the other half is used as calibration set for VA. The CPS
can be pre-fitted at initialization of the CalibratedExplainer whereas VA needs to
be initialized for each threshold at explanation time. More formally, the following is
done at initialization:
1. Split the calibration set into two equal halves and calculate the residuals
R = {r1, . . . , ri, . . . , r⌈q/2⌉} for the first half, where ri = yi −h(xi).
12
### Page 13

2. Fit a CPS model cpsP using the residuals R.
At explanation time, the following is done:
1. Define the scores S = cpsP({x⌊q/2⌋+1, . . . , xq}, threshold = t) for the second half
of the calibration instances.
2. Define the categorical targets as ˙Y = {yi ≤t}, where i ∈{⌊q/2⌋+ 1, . . . , q}.
3. Use S as scores and ˙Y as targets to define a VA calibrator vaP.
4. Define the score for the test instance x as s = cpsP(x, threshold = t).
5. Use vaP with s to produce probability intervals [Pl, Ph] and a calibrated proba-
bility estimate P for the true target being below the threshold, y ≤t, and create a
calibrated explanation using the description in section 2.5.1 with the class labels
{y ≤t, y > t}.
If the same threshold t is used for a batch of test objects, the same calibrator, vaP, is
re-used, improving computational performance as the first three steps only needs to
be done once.
3.4 Properties of Calibrated Explanations for Regression
The median from a CPD based on the calibration data can be seen as a form of
calibration of the underlying model’s prediction, since it may adjust the prediction on
the test instance to match what has previously been seen on the calibration set. The
calibration will primarily affect systematic bias in the underlying model. Consequently,
since Calibrated Explanations calibrates the underlying model, it will create calibrated
predictions and explanations. In addition, VA provides uncertainty quantification of
both the probability estimates from the underlying model and the feature importance
weights through the intervals for probabilistic Calibrated Explanations for regression.
By using equality rules for categorical features and binary rules for numerical features
(as recommended above), interpreting the meaning of a rule with a corresponding
feature weight in relation to the target and instance value is straightforward and
unambiguous and follows the same logic as for classification.
The explanations are reliable because the rules straightforwardly define the
relationship between the calibrated outcome and the feature weight (for factual
explanations) or feature prediction estimate (for counterfactual explanations). The
explanations are robust, i.e., consistent, as long as the feature rules cover any pertur-
bations in feature values. Variation in predictions, e.g. when training using different
training sets, can be expected to result in some variation in feature rules, corresponding
to the variation in predictions. Obviously, the method does not guarantee robustness
for perturbations violating a feature rule condition. The factual and counterfactual
Calibrated Explanations for regression explanations are stable as long as the same cal-
ibration set and model are used. Finally, depending on the size of the calibration set
which is used to define a CPS, the generation of factual Calibrated Explanations for
regression is comparable to existing solutions such as LIME and SHAP. Generating a
probabilistic factual Calibrated Explanations for regression will be slower than Cali-
brated Explanations for classification since both require a VA to be trained. Compared
to Calibrated Explanations for classification, probabilistic explanations for regression
will have some additional overhead from using a CPS as well.
13
### Page 14

A minor difference between classification and regression is related to the discretiz-
ers that are used for numerical features. Both the BinaryEntropyDiscretizer and
the EntropyDiscretizer (used for classification) require categorical target values for
the calibration set as they use a classification tree (with a depth of one and three levels,
respectively) to determine the best discretization. For regression, two new discretiz-
ers have been added, BinaryRegressorDiscretizer and RegressorDiscretizer,
relying on regression trees, also with depths one and three. The discretizers are auto-
matically assigned based on the kind of problem and explanation that is extracted. The
same discretizers as used for standard factual and counterfactual Calibrated Expla-
nations for regression must also be applied for probabilistic regression explanations,
as it is motivated by the problem type.
If a difficulty estimator is used to get explanations based on normalized CPDs, σ is
calculated using the DifficultyEstimator in crepes.extras and passed along to cps
(and cpsP for probabilistic regression explanations) both when fitting and obtaining
median and interval values.
Finally, the calibrated predictions and their confidence intervals, which are an
integral part of factual Calibrated Explanations, provide the same guarantees as the
calibration model used, i.e., the same guarantees as VA for classification and CPSs for
regression (or a combination of both for probabilistic regression). However, even if the
uncertainty quantification in the form of intervals for the feature rules is also derived
from the same calibration model, these feature rule intervals do not necessarily provide
the same guarantees. The reason is that the perturbed instances (see steps 3 and 4) are
artificial and the combination of feature values may not always exist naturally in the
problem domain. Whenever that happens, the underlying model and the calibration
model will indicate that it is a strange instance but may not estimate the degree of
strangeness correctly as there is no evidence in the data to base a correct estimate on.
A Python implementation of the Calibrated Explanations solution described in
this paper is freely available with a BSD3-style license from:
• Code repository: github.com/Moffran/calibrated explanations
• PyPi package: pypi.org/project/calibrated-explanations/
• Conda-forge package: anaconda.org/conda-forge/calibrated-explanations
• Documentation: calibrated-explanations.readthedocs.io/
Since it is on PyPI and conda-forge, it can be installed with pip or conda com-
mands. The GitHub repository includes Python scripts to run the examples in this
paper, making the results here easily replicable. The repository also includes several
notebooks with additional examples. This paper details calibrated-explanations
as of version 0.3.3.
Using Calibrated Explanations with regression is done using almost identical func-
tion calls as for classification. An example on how to initialise a CalibratedExplainer
and create factual and counterfactual explanations for standard and probabilis-
tic regression from a trained model can be seen in Fig. 2. The parameter
low high percentiles=(5,95) is the default value and can be left out or changed to
some other uncertainty interval. In the example, all intervals are defined to 90% con-
fidence. The difference between standard and probabilistic explanations only require
exchanging low high percentiles=(low,high) with threshold=your threshold.
14
### Page 15

1
2 from
calibrated_explanations
import
CalibratedExplainer
3 # Load and pre -process
your data
4 # Divide it into
proper
training , calibration , and test sets
5
6 # Train
your
model
using the proper
training
set
7 model.fit(X_proper_training , y_proper_training )
8
9 # Initialize
the
CalibratedExplainer
10 ce = CalibratedExplainer (model , X_calibration , y_calibration ,
11
mode=’regression ’)
12
13 # Create and plot
factual
standard
explanations
14 factual_explanations = ce. explain_factual (X_test ,
15
low_high_percentiles =(5 ,95))
16 factual_explanations .plot_all ()
17 factual_explanations .plot_all(uncertainty=True)
18
19 # Create and plot
counterfactual
standard
explanations
20 counterfactual_explanations = ce. explain_counterfactual (X_test ,
21
low_high_percentiles =(5 ,95))
22 counterfactual_explanations .plot_all ()
23
24 # One -sided
explanations
are easily
created
25 factual_upper_bounded = ce. explain_factual (X_test ,
26
low_high_percentiles =(-np.inf ,90))
27 counterfactual_lower_bounded = ce. explain_counterfactual (X_test ,
28
low_high_percentiles =(10 ,np.inf))
29
30 # Create and plot
factual
probabilistic
explanations
31 your_threshold = 1000
32 factual_explanations = ce. explain_factual (X_test ,
33
threshold= your_threshold )
34
35 # Create and plot
counterfactual
probabilistic
explanations
36 counterfactual_explanations = ce. explain_counterfactual (X_test ,
37
threshold= your_threshold )
38
Fig. 2: Code example on using calibrated-explanations for regression.
The threshold parameter is None by default but takes precedence when having a
value assigned.
Normalization can be achieved using DifficultyEstimator from crepes.extras.
It currently has four different ways to normalize, as seen in the example shown
in Fig. 3, where alternative 3 and 4 requires an ensemble model, such as a
15
### Page 16

1 from
calibrated_explanations
import
CalibratedExplainer
2 from
crepes.extras
import
DifficultyEstimator
3 # Load and pre -process
your data
4 # Divide it into
proper
training , calibration , and test sets
5
6 # Train
your
model
using the proper
training
set
7 model.fit(X_proper_training , y_proper_training )
8
9 de = DifficultyEstimator ()
10
11 # 1: by the (Euclidean) distances to the
nearest
neighbors
12 de.fit(X=X_proper_training , scaler=True)
13
14 # 2: by the
standard
deviation of the
targets of the
nearest
15 #
neighbors
16 de.fit(X=X_proper_training , y=y_proper_training , scaler=True)
17
18 # 3: by the
absolute
errors of the k nearest
neighbors
19 residuals_oob = y_proper_training - model. oob_prediction_
20 de.fit(X=X_proper_training , residuals=residuals_oob , scaler=True)
21
22 # 4: by the
variance
among
ensemble
submodels
23 de.fit(X=X_proper_training , learner=model , scaler=True)
24
25 # Initialize
the
CalibratedExplainer
with de
26 ce = CalibratedExplainer (model , X_calibration , y_calibration ,
mode=’regression ’, difficulty_estimator =de)
27
28 # Change a DifficultyEstimator
29 ce. set_difficultyEstimator (de)
30
Fig. 3: Code example on using calibrated-explanations with normalization.
RandomForestRegressor. Creating normalized explanations with standard and prob-
abilistic regression is done exactly the same as without normalization, see Fig. 2, once
the difficulty estimator is assigned.
3.5 Summary of Calibrated Explanations
With the two solutions proposed here, Calibrated Explanations provide a number of
possible use cases, which are summarized in Table 1.
Both factual and counterfactual explanations are composed of lists of feature rules
with conditions and feature weights with confidence intervals (factual explanations) or
feature prediction estimates with confidence intervals (counterfactual explanations),
as described in Section 2.5. Conditional rules was introduced in version 0.3.1 and
described in a paper introducing this for analysis of Fairness [45].
16
### Page 17

Classification
Standard
Probabilistic
Regression
Regression
Characteristics
FR
FU
CF
FR
FU
CF
FR
FU
CF
Feature Weight w/o CI
X
X
X
Feature Weight with CI
X
X
X
Rule Prediction with CI
X
X
X
Two-sided CI
I
I
I
I
I
I
I
I
I
Lower-bounded CI
I
I
Upper-bounded CI
I
I
Conjunctive rules
O
O
O
O
O
O
O
O
O
Conditional rules
O
O
O
O
O
O
O
O
O
Normalization
O
O
O
O
O
O
# alternative setups
1
1
1
5
5
5
5
5
5
Table 1: Summary of characteristics of Calibrated Explanations. All
explanations include the calibrated prediction, with confidence intervals,
of the explained instance. FR refers to factual explanations visualized
using regular plots, FU refers to factual explanations visualized using
uncertainty plots, and CF refers to counterfactual explanations and plots.
Furthermore, CI refers to a confidence interval, Conjunctive rules indi-
cates that conjunctive rules are possible, Conditional rules indicates
support for users to create contextual explanations, Normalization indi-
cates that normalization is supported and # alternative setups refers
to the number of ways to run Calibrated Explanations, i.e., w/o normal-
ization or with any of the four different ways to normalize. X marks a
core alternative, I marks selectable interval type(s) used by the core alter-
natives, and O marks optional additions.
4 Experimental Setup
The
implementation
of
both
the
regression
and
the
probabilistic
regres-
sion
solutions
is
expanding
the
calibrated-explanations
Python
package
[23]
and
relies
on
the
ConformalPredictiveSystem
from
the
crepes
pack-
age [46]. By default, ConformalPredictiveSystem is used without normaliza-
tion but DifficultyEstimator provided by crepes.extras is fully supported by
calibrated-explanations, with normalization options corresponding to the list
given at the end of Section 3.1 and in Fig. 3.
4.1 Presentation of Calibrated Explanations trough Plots
In this paper, three different kinds of plots for Calibrated Explanations are presented.
The first two are used when visualizing factual Calibrated Explanations for standard
regression. These plots are inspired by LIME, especially the rules in LIME have been
seen as providing valuable information in the explanations.
• Regular explanations, providing Calibrated Explanations without any uncer-
tainty information. These explanations are directly comparable to other feature
importance explanation techniques like LIME.
17
### Page 18

• Uncertainty explanations, providing Calibrated Explanations including uncer-
tainty intervals to highlight both the importance of a feature and the amount of
uncertainty connected with its estimated importance.
For the reasons given in previous sections, Calibrated Explanations is meant to use
binary rules with factual explanations (even if all discretizers used by LIME can also be
used by Calibrated Explanations). One noteworthy aspect of Calibrated Explanations
is that the feature weights only show how each feature separately affects the outcome.
It is possible to see combined weights through conjunctions of features (combining
two or three different rules into a conjunctive feature rule). It is important to clarify
that the feature weights do not convey the same meaning as in attribution-based
explanations, like SHAP.
The third kind of plot is a counterfactual plot showing preliminary prediction
estimates for each feature when alternative feature values are used.
Feature rules are always ordered based on feature weight, starting with the most
impactful rules. When plotting Calibrated Explanations, the user can choose to limit
the number of rules to show. Factual explanations have one rule per feature. Counter-
factual explanations, where Calibrated Explanations creates as many counterfactual
rules as possible, may result in a much larger number of rules, especially for categorical
features with many categories.
Internally, Calibrated Explanations uses the same representation for both clas-
sification and regression. However, the plots visualizing the explanations have been
adapted to suit both standard and probabilistic factual Calibrated Explanations for
regression.
4.1.1 Calibrated Explanations Plots
The same kind of plots exists for regression as for classification. Compared to the plots
used for classification, the regression plots differ in two essential aspects.
A common difference for both factual and counterfactual Calibrated Explanations
for regression is that the feature weights represent changes in actual target values. For
factual Calibrated Explanations for regression, this means that a feature importance
of +100 means that the actual feature value contributes with +100 to the prediction.
For a counterfactual Calibrated Explanations for regression, showing the prediction
estimates with uncertainty intervals, the plot shows what the prediction is estimated
to have been if the counterfactual condition would be fulfilled.
A difference that only applies to the factual plots is that the top of the plot omits
the probabilities for the different classes and instead shows the median m and the
confidence interval [l, h] as the prediction.
4.1.2 Probabilistic Calibrated Explanations Plots
Since the probabilistic factual Calibrated Explanations for regression represents fea-
ture importances as probabilities, just like Calibrated Explanations for classification.
The only difference needed for the probabilistic plots for regression compared to clas-
sification is to change the probabilities for a class label into probabilities for being
below (P(y ≤t)) or above (P(y > t)) the given threshold.
18
### Page 19

4.2 Experiments
The evaluation is divided into an introduction to all different kinds of Calibrated
Explanations for regression through plots and an evaluation of performance. All plots
are from the California Housing data set [47]. The underlying model in all experiments
is a RandomForestRegressor from the sklearn package.
Our proposed algorithm is claimed to be fast, reliable, stable, and robust. These
claims requires validation in an evaluation of performance. The explanations are reli-
able due to the validity of the uncertainty estimates used, i.e., the results achieved by
querying the CPD, and from the uncertainty quantification of the feature weights or
feature prediction estimates. Speed, stability and robustness will be evaluated in an
experiment using the California Housing data set on a fixed set of test instances. Each
experiment is repeated 100 times using 500 instances as a calibration set (also used
by SHAP and LIME) and 10 test instances. The target values were normalized, i.e.,
y ∈[0, 1]. The following setups are evaluated:
• FCER: Factual explanation.
• CCER: Counterfactual explanation.
• PFCER: Probabilistic factual explanation. The threshold is 0.5 for all instances,
i.e., the mid-point of the interval of possible target values.
• PCCER: Probabilistic counterfactual explanation. The threshold is 0.5 for all
instances, i.e., the mid-point of the interval of possible target values.
• LIME: LIME explanation.
• LIME CPS: LIME explanation using the median from a CPD as prediction. The
CPS was based on the underlying random forest regressor.
• SHAP: SHAP explanation using the Explainer class.
• SHAP CPS: SHAP explanation using the median from a CPD as prediction. The
CPS was based on the underlying random forest regressor. Here, the Explainer
class was used.
The evaluated metrics are:
• Stability means that multiple runs on the same instance and model should pro-
duce consistent results. Stability is evaluated by generating explanations for
the same predicted instances 100 times with different random seeds (using the
iteration counter as random seed). The random seed is used to initialize the
numpy.random.seed() and by the discretizers. The largest variance in feature
weight (or feature prediction estimate) can be expected among the most impor-
tant features (by definition of having higher absolute weights). The top feature
for each test instance is identified as the feature being most important most often
in the 100 runs (i.e., the mode of the feature ranks defined by the absolute fea-
ture weight). The variance for the top feature is measured over the 100 runs and
the mean variance among the test instances is reported.
• Robustness means that small variations in the input should not result in large
variations in the explanations. Robustness is measured in a similar way as stabil-
ity, but with the training and calibration set being randomly drawn and a new
model being fitted for each run, creating a natural variation in the predictions
of the same instances without having to construct artificial instances. Again, the
variance of the top feature is used to measure robustness. The same setups as for
19
### Page 20

stability are used except that each run use a new model and calibration set and
that the random seed was set to 42 in all experiments.
• Run time is compared between the setups regarding explanation generation times
(in seconds per instance). It is only the method call resulting in an explanation
that is measured. Any overhead in initiating the explainer class is not consid-
ered). The closest equivalent to probabilistic factual Calibrated Explanations for
regression would be to apply LIME and SHAP for classification to a thresholded
classification model, as described in section 3.3. Since VA is comparably slow and
probabilistic Calibrated Explanations for regression combines both CPSs and VA,
with fitting and calls to a CPS for each calibration instance, it can be expected
to be slow.
FCER and PFCER without normalization are compared with the LIME and SHAP
alternatives. Additionally, run time is compared across both standard and probabilistic
factual and counterfactual Calibrated Explanations with and without normalization.
The difficulty estimation uses 500 randomly drawn instances from the training set to
estimate difficulty. Stability and robustness are less affected by normalization6.
5 Results
The results are divided into two parts: 1) a presentation of Calibrated Explanations
through plots, explaining and showcasing a number of different available ways Cal-
ibrated Explanations can be used and viewed; and 2) an evaluation of performance
with comparisons to LIME and SHAP.
5.1 Presentation of Calibrated Explanations through Plots
In the following subsections, a number of introductory examples of Calibrated
Explanations are given for regression. First, factual and counterfactual explanations
for regression are shown, followed by factual and counterfactual explanations for
probabilistic regression.
5.1.1 Factual Calibrated Explanations for Regression
The regular plot in Fig. 4 illustrates the calibrated prediction of the underlying model
as the solid red line at the top bar together with the 90% confidence interval in light
red. As can be seen, the house price is predicted to be ≈$285K and with 90% confi-
dence, the price can be expected to be between [$215K-$370K]. Turning to the feature
rules, the solid black line represents the median in the top-bar. The rule condition is
shown to the left and the actual instance value is shown to the right of the lower plot
area. The fact that this house is located more northbound (latitude > 34.26) has
a large negative impact on the price (reducing it with ≈$95K). On the other hand,
since the median income is a bit higher (median income > 3.52), the price is pressed
about $60K upwards. Housing median age and population are two more features
that clearly impact the price negatively.
6Detailed results for stability and robustness can be found in the evaluation/regression folder in the
repository, together with the code used for experiments shown in the paper.
20
### Page 21

100000
200000
300000
400000
500000
Prediction interval with 90% confidence
Median prediction
100000
80000
60000
40000
20000
0
20000
40000
60000
Feature weights
ocean_proximity = <1H OCEAN
total_bedrooms > 429.50
total_rooms > 2078.00
households > 409.50
longitude <= -118.53
population > 1138.50
housing_median_age <= 28.00
median_income > 3.52
latitude > 34.26
Rules
<1H OCEAN
564.0
3075.0
543.0
-121.98
1633.0
25.0
5.25
37.27
Instance values
Fig. 4: A regular plot for the California Housing data set. The top-bar illustrates the
median (the red line) and a confidence interval (the light red area), defined by the
5th and the 95th percentiles. The subplot below visualizes the weights associated with
each feature. The weights indicate how much that rule contributes to the prediction.
Negative weights in red indicate a negative impact on the prediction whereas positive
weights in blue indicate a positive impact.
When one-sided intervals are used instead, only the top-bar is affected compared to
when using regular plots. Figures 5a and 5b illustrate an upper bounded and a lower
bounded explanation for the same instance, with the identical feature rule subplot
omitted. As can be seen, the median (solid red line) is the same as before, while the
confidence interval stretches one entire side of the bar. The upper bound (≈$330K in
Fig. 5a) is lower and the lower bound (≈$240K in Fig. 5b) is higher compared to the
two-sided plot in Fig. 4.
100000
200000
300000
400000
500000
Prediction interval with 90% confidence
Median prediction
(a) Upper bounded explanation
100000
200000
300000
400000
500000
Prediction interval with 90% confidence
Median prediction
(b) Lower bounded explanation
Fig. 5: The top bars of one-sided plots with confidence intervals bounded by the 90th
upper percentile (Fig. 5a) and the 10th lower percentile (Fig. 5b). The red solid line
represents the median. The weights (and consequently the entire subplot visualizing
weights) are the same for these one-sided explanations as in Fig. 4.
21
### Page 22

100000
200000
300000
400000
500000
Prediction interval with 90% confidence
Median prediction
150000
100000
50000
0
50000
100000
Feature weights
ocean_proximity = <1H OCEAN
total_bedrooms > 429.50
total_rooms > 2078.00
households > 409.50
longitude <= -118.53
population > 1138.50
housing_median_age <= 28.00
median_income > 3.52
latitude > 34.26
Rules
<1H OCEAN
564.0
3075.0
543.0
-121.98
1633.0
25.0
5.25
37.27
Instance values
Fig. 6: An uncertainty plot for the California Housing data set. The top bar is the same
as in Fig. 4, showing the median and the [5th, 95th] percentiles confidence interval. In
the subplot below, the uncertainty of the weights is highlighted, using the [5th, 95th]
percentiles confidence interval in light red or blue for each feature. The weights still
indicate how much that rule contributes to the prediction but with a confidence interval
highlighting the span of uncertainty for the impact of the feature value and rule
combined.
Fig. 6 illustrates an uncertainty plot for the same instance as before7. When includ-
ing uncertainty quantification in the plot, the feature importance has a light colored
area corresponding to the span of possible contribution within the confidence used.
The grey area surrounding the solid black line represents the same confidence interval
as seen in the top bar.
As can be seen, the northbound location still has a large negative impact but the
span of uncertainty about exactly how large the impact is covers about $150K, falling
approximately within the interval [-$180K, -$30K]. The fact that part of the line is
solid in color indicates that we can expect this feature to impact the price at least
with -$30K, given the selected confidence level. Looking at the other features, we can
see that all of them include the median in the uncertainty interval, meaning that with
90% confidence, these features may impact the price in both directions. Obviously,
both median income and in particular housing median age are more likely to have
a positive and negative impact, respectively. Since no normalization have been used
with this example, all the intervals are similar in width.
7Uncertainty plots are not available for one-sided explanations, as the visualization becomes obscured
and hard to interpret. However, the one-sided uncertainty interval for each feature rule is calculated and
can be accessed and used if needed.
22
### Page 23

100000
200000
300000
400000
500000
Prediction interval with 90% confidence
housing_median_age < 20.0
ocean_proximity = ISLAND
housing_median_age > 25.0
latitude > 37.59
population < 1541.7999999999997
median_income < 5.08154
ocean_proximity = INLAND
latitude < 36.734
longitude < -122.02
median_income > 6.27628
Counterfactual rules
25.0
<1H OCEAN
25.0
37.27
1633.0
5.25
<1H OCEAN
37.27
-121.98
5.25
Instance values
Fig. 7: A counterfactual plot for the California Housing data set. The large lightest
red area in the background is the confidence interval defined by the 5th and the 95th
percentiles. Each row represents a counterfactual rule with an interval in darker red
indicating what confidence intervals a breach according to the rule condition would
result in. The confidence intervals for the counterfactual rules are also defined by the
5th and the 95th percentiles. The solid lines represent the median values.
5.1.2 Counterfactual Calibrated Explanations for Regression
Turning to counterfactual Calibrated Explanations for regression, Fig. 7 shows a coun-
terfactual plot for the same instance as before. Here, the solid line and the very light
area behind it represent the median and the confidence interval of the calibrated pre-
diction of the underlying model (i.e., the same as in Fig. 4). This is the ground truth
that all the counterfactual feature rules should be contrasted against.
Contrary to factual Calibrated Explanations for regression, none of the rules cover
the instance values in the counterfactual plot. Instead, there are several examples of the
same feature being present in multiple rules. Here the interpretation is that the solid
line and lighter red bar for each rule is the expected median and confidence interval
achieved if the instance would have had values according to the rule. As an example,
with everything else the same but median income > 6.28, then the expected price
would be ≈$405K with a confidence interval of [$340K, $490K]. It is also clear that if
the house would have been located further south (latitude < 36.7), the price would
go up, and if it would have been even further north (latitude > 37.6), the price
would have gone down even further. It is worth noting that as the counterfactual
rules presented in Fig. 7 are excluding the instance values, whereas the factual rules
in Figs. 4 and 6 are including the instance values, the ordering of features may be
completely different between the explanations, despite explaining the same instance.
So far, all examples (using both factual and counterfactual explanations) have
used a standard CPS to construct the explanations, with the result that all confidence
intervals are almost equal-sized. In Fig. 8, a difficulty estimator based on the stan-
dard deviation of the targets of the k nearest neighbors is used. The normalization
23
### Page 24

will both affect the calibration of the underlying model, creating confidence intervals
with varying sizes between instances, and the feature intervals. A crude assumption
regarding the width of the feature intervals is that when the calibration set contains
fewer instances covering an alternative feature value, the feature intervals will tend to
be larger due to less information, and vice versa. This does not have to be the whole
truth, as difficulty in this example is defined based on the standard deviation of the
neighboring instances target values. As can be seen in Fig. 8, normalized counterfac-
tual explanations may generate rules resulting in both smaller and wider confidence
intervals then the non-normalized rules.
100000
200000
300000
400000
500000
Prediction interval with 90% confidence
total_bedrooms > 579.3
ocean_proximity = ISLAND
housing_median_age > 25.0
latitude > 37.59
population < 1541.7999999999997
median_income < 5.08154
ocean_proximity = INLAND
latitude < 36.734
longitude < -122.02
median_income > 6.27628
Counterfactual rules
564.0
<1H OCEAN
25.0
37.27
1633.0
5.25
<1H OCEAN
37.27
-121.98
5.25
Instance values
Fig. 8: A normalized counterfactual plot comparable to Fig 7, resulting in rules with
varied interval widths as a consequence of the normalization. Difficulty is estimated
as the standard deviation of the targets of the k nearest neighbors.
Similarly to factual Calibrated Explanations for regression, counterfactual expla-
nations can also be one-sided. Fig. 9 shows an upper-bounded explanation with 90%
confidence. The interpretation of the first rule is that, with everything else as before,
but median income > 6.28 the price will be below ≈$450K with 90% certainty. Since
the same CPS is used, the median is still the same as for a two-sided explanation.
5.1.3 Probabilistic Factual Calibrated Explanations for Regression
Fig. 10 shows a regular probabilistic regression plot for the same instance as above. In
this plot, the possibility of querying the CPD about the probability of being below or
above a given threshold is utilized. In this case, the threshold is set to a house price
of $250K. Here, median income > 3.52 contributes strongly to the probability that
the target is above $250K.
In Fig. 11, the same explanation is shown with uncertainties. As can be seen, the
size of the uncertainty varies a lot between features, depending on the calibration of
the VA calibrator.
24
### Page 25

100000
200000
300000
400000
500000
Prediction interval with 90% confidence
housing_median_age < 20.0
ocean_proximity = ISLAND
housing_median_age > 25.0
latitude > 37.59
population < 1541.7999999999997
median_income < 5.08154
ocean_proximity = INLAND
latitude < 36.734
longitude < -122.02
median_income > 6.27628
Counterfactual rules
25.0
<1H OCEAN
25.0
37.27
1633.0
5.25
<1H OCEAN
37.27
-121.98
5.25
Instance values
Fig. 9: A one-sided counterfactual plot for the California Housing data set. Confidence
intervals are defined by the 90th upper percentile only. The interpretation is that with
90% certainty, the true value of the original instance will fall within the lightest red
area. If the counterfactual rule had been true for each feature individually, the true
value will fall within that feature’s darker red area with approximately 90% certainty.
P(y<=250000.00)
0.0
0.2
0.4
0.6
0.8
1.0
Probability
P(y>250000.00)
0.1
0.0
0.1
0.2
0.3
0.4
0.5
0.6
Feature weights
total_bedrooms > 429.50
households > 409.50
population > 1138.50
housing_median_age <= 28.00
latitude > 34.26
longitude <= -118.53
ocean_proximity = <1H OCEAN
total_rooms > 2078.00
median_income > 3.52
Rules
564.0
543.0
1633.0
25.0
37.27
-121.98
<1H OCEAN
3075.0
5.25
Instance values
Fig. 10: A regular probabilistic regression plot for the California Housing data set.
The plot shows the probability of the prediction for this instance being above the given
threshold ($250K in this case). The explanation is similar to a regular plot used in
Calibrated Explanations for classification with the main difference being that it shows
the probabilities of being below or above the threshold and that the probabilities are
given by the CPD.
25
### Page 26

P(y<=250000.00)
0.0
0.2
0.4
0.6
0.8
1.0
Probability
P(y>250000.00)
0.1
0.0
0.1
0.2
0.3
0.4
0.5
0.6
Feature weights
total_bedrooms > 429.50
households > 409.50
population > 1138.50
housing_median_age <= 28.00
latitude > 34.26
longitude <= -118.53
ocean_proximity = <1H OCEAN
total_rooms > 2078.00
median_income > 3.52
Rules
564.0
543.0
1633.0
25.0
37.27
-121.98
<1H OCEAN
3075.0
5.25
Instance values
Fig. 11: An uncertainty probabilistic regression plot for the same explanation as in
Fig. 10. The plot includes uncertainties for the feature weights.
5.1.4 Probabilistic Counterfactual Calibrated Explanations for
Regression
Fig. 12 shows a normalized probabilistic counterfactual plot for the same instance. In
this case, the normalization used was based on the variance of the predictions of the
trees in the random forest. The most influential rule relates to median income, with a
lower income increasing the probability for a lower price. The normalization will affect
the feature probability estimates and confidence intervals and may consequently also
result in a different ordering of rules.
0.0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
0.8
0.9
1.0
Probability of target being below 250000.00
median_income > 6.27628
ocean_proximity = NEAR BAY
population > 1847.2
total_rooms < 2790.5999999999995
latitude < 36.734
housing_median_age < 20.0
longitude > -121.326
latitude > 37.59
ocean_proximity = INLAND
median_income < 5.08154
Counterfactual rules
5.25
<1H OCEAN
1633.0
3075.0
37.27
25.0
-121.98
37.27
<1H OCEAN
5.25
Instance values
Fig. 12: A normalized probabilistic counterfactual plot for the same instance as before.
.
26
### Page 27

The final example, shown in Fig. 13, illustrates both conjunctive rules, combining
two feature conditions in one rule, and normalization using the variance of the pre-
dictions of the trees in the random forest. Here, the number of rules to plot has been
increased to 15. Here we see that conjunctive rules often result in more influential rules
than single condition rules, illustrated by the majority of rules being conjunctive.
0.0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
0.8
0.9
1.0
Probability of target being below 250000.00
longitude < -122.02 & 
median_income < 5.08154
latitude < 36.734 & 
housing_median_age < 20.0
latitude < 36.734 & 
median_income < 5.08154
longitude > -121.326
latitude < 36.734 & 
ocean_proximity = INLAND
latitude > 37.59
longitude < -122.02 & 
ocean_proximity = INLAND
total_bedrooms < 487.79999999999995 & 
median_income < 5.08154
ocean_proximity = INLAND
housing_median_age < 20.0 & 
ocean_proximity = INLAND
total_rooms < 2790.5999999999995 & 
ocean_proximity = INLAND
median_income < 5.08154
total_rooms < 2790.5999999999995 & 
median_income < 5.08154
total_bedrooms < 487.79999999999995 & 
ocean_proximity = INLAND
housing_median_age < 20.0 & 
median_income < 5.08154
Counterfactual rules
-121.98
5.25
37.27
25.0
37.27
5.25
-121.98
37.27
<1H OCEAN
37.27
-121.98
<1H OCEAN
564.0
5.25
<1H OCEAN
25.0
<1H OCEAN
3075.0
<1H OCEAN
5.25
3075.0
5.25
564.0
<1H OCEAN
25.0
5.25
Instance values
Fig. 13: A normalized probabilistic counterfactual plot with conjunctive rules for the
same instance as before.
.
Factual or counterfactual rules can be generated without normalization or with
any of the normalization options available in DifficultEstimator in crepes.extras.
Conjunctive rules can be added at any time after the explanations are generated. All
the examples shown here are from the same instance and the same underlying model,
to showcase a subset of available ways the proposed solutions can be used. Further
examples can be found in the code repository.
5.2 Performance Evaluation
Table 2 shows the results achieved regarding stability, robustness, and run time. Sta-
bility is measured using the mean variance when constructing explanations on the
same instance using different random seeds, with lower values representing more sta-
bility. It is evident that both SHAP setups and both setups for standard regression
must be considered stable, since the mean variance is 0 (i.e., less than 1e −31). LIME
27
### Page 28

and probabilistic regression, on the other hand, has a non-negligible mean variance,
meaning that they are not, in comparison, as stable. The reason for why probabilistic
regression is less stable is related to the sensitivity of the probabilities derived from
the CPD. The reason for the sensitivity is that a relatively small change in prediction
can easily result in a comparably much larger change in probability for exceeding the
threshold, especially if the target is close to the threshold (which is set to 0.5, i.e., the
mid-point in the interval of possible target values). Explanations using the median
from a CPD and explanations using the underlying model result in similar stability
levels.
Robustness is measured in a similar way as stability, but with a new model trained
using different distributions of training and calibration instances between each run.
The results achieved on robustness should be seen in relation to the variance in pre-
dictions from the underlying model on the same instances. The reason is that if the
predictions that the explanations are based on fluctuate, then we can expect a some-
what similar degree of fluctuation in the feature weights as well, since they are defined
using the predictions (the mean prediction variance is 9.1e −5). All setups for Cali-
brated Explanations have higher mean variance compared to LIME and SHAP (i.e.,
are being less robust). However, the explanations produced by the setups for Cali-
brated Explanations do not only rely on the crisp feature weight used to measure
the mean variance (i.e., robustness metric) but also include the uncertainty interval,
highlighting the degree of uncertainty associated with each feature weight.
FCER
CCER
PFCER
PCCER
LIME
LIME
SHAP
SHAP
CPS
CPS
Stability
0
0
2.2e-3
2.7e-3
2.7e-5
2.7e-5
0
0
Robustness
8.0e-3
2.1e-3
3.4e-2
1.3e-2
8.8e-4
8.7e-4
1.4e-4
1.4e-4
Run time
0.269
0.400
0.614
0.880
0.166
0.188
0.431
0.587
Table 2: Evaluation of stability, robustness and run time
Regarding run time, all setups have used the same calibration set of 500 instances,
including LIME and SHAP. LIME is the fastest and the difference between when
explaining the underlying model or when using a CPS is small. Both FCER and CCER
are faster than SHAP. The difference between SHAP explaining the underlying model
or when using a CPS is fairly large. PFCER is slightly slower than SHAP CPS, having
to calculate probabilities for half the calibration instances as well as training two
isotonic calibrators for each test instance. PCCER is the slowest alternative, having
the same overhead as PFCER but also generating a larger number of rules.
Table 3 show the average time in seconds per instance for creating an explanation
with and without normalization for the different kinds of Calibrated Explanations.
The most striking result is that using normalization adds a substantial overhead com-
pared to not using normalization: an average of 6× increase in run time. It is also
evident that the k-Nearest Neighbor based difficulty estimators (using Distance, Stan-
dard Deviation or Absolute Error among neighbors) are clearly slower than using the
Variance among ensemble base regressors. Furthermore, counterfactual explanations
28
### Page 29

Explanations
Normalization
FCER
CCER
PFCER
PCCER
Average
None
0.269
0.400
0.614
0.880
0.541
Distance
1.728
2.452
1.838
2.640
2.165
Standard Deviation
1.799
2.534
1.884
2.691
2.227
Absolute Error
1.849
2.613
1.954
2.757
2.293
Variance
1.005
1.390
1.456
1.962
1.453
Average
1.330
1.878
1.549
2.186
1.736
Table 3: Run time for different kinds of explanations and normalization
are slightly more costly than factual, which is not surprising as they generally gen-
erate a larger number of rules. Standard explanations are slightly more than twice
as fast as probabilistic explanations without normalization. With normalization, the
difference is much smaller, stemming from the fact that only half the calibration set
needs normalization, as the other half is used by VA to calibrate the probabilities.
Detailed results comparing stability and robustness for different kinds of difficulty
estimations is not included, as the differences compared to not using normalization
(see Table 2) is small. Detailed results can be found in the evaluation/regression folder
in the repository.
6 Concluding Discussion
This paper extends Calibrated Explanations, previously introduced for classification,
with support for regression. Two primary use cases are identified: standard regression
and probabilistic regression, i.e., measuring the probability of exceeding a threshold.
The proposed solution relies on Conformal Predictive Systems (CPS), making it pos-
sible to meet the different requirements of the two identified use cases. The proposed
solutions provide access to factual and counterfactual explanations with the possibil-
ity of conveying uncertainty quantification for the feature rules, just like Calibrated
Explanations for classification.
In the paper, the solutions have been demonstrated using several plots, showcas-
ing some of the many ways that the proposed solutions can be used. Furthermore, the
paper also includes a comparison with some of the best-known state-of-the-art explana-
tion methods (LIME and SHAP). The results demonstrate that the proposed solution
for standard regression is both stable and robust. Furthermore, it is reasonably fast.
The suggested solution is considered reliable for two reasons: 1) The calibration of
the underlying model and 2) the uncertainty quantification, highlighting the degree of
uncertainty of both prediction and feature weights.
The solution proposed to build probabilistic explanations for regression does not
share all the benefits seen for standard regression. The solution has comparable per-
formance as LIME, even if it is clearly slower than LIME. The main strength of this
solution is that it provides the possibility of getting probabilistic explanations in rela-
tion to an arbitrary threshold from any standard regression model without having to
impose any restrictions on the regression model.
29
### Page 30

6.1 Future Work
There are several directions for future work. An interesting area to look into is how
this technique can be adapted to explanations of time-series problems. How to capture
and convey the dependency between different time steps pose an interesting challenge.
There are room for improvement regarding plot layout. Providing additional ways
of visualization is a natural development in the future. This involves implementing
support for explanations within image and text prediction, even if these improvements
are more closely connected to classification problems.
Another direction for future work is to look into probabilistic explanations using
the form P(t1 < y ≤t2). Such predictions would complement the interval predictions
provided by CPS by allowing the user to specify the upper and lower bounds of the
uncertainty interval and provide the probability of the true target being inside that
interval.
Currently, the average calibrated value is used to define the feature weights in
equations (1), (2), and (3) (see Section 2.5.1). There are alternatives to taking the
average of the perturbed instances for a specific feature and there is room for theo-
retical analysis on how the feature weights should be calculated to provide the best
insights.
Finally, run time can probably be decreased if implementing the core in C++ or
by relying on fast languages being able to run Python code more efficiently, e.g., Mojo.
Declarations
• Funding: The authors acknowledge the Swedish Knowledge Foundation and
industrial partners for financially supporting the research and education envi-
ronment on Knowledge Intensive Product Realization SPARK at J¨onk¨oping
University, Sweden. Projects: AFAIR grant no. 20200223, ETIAI grant no.
20230040, and PREMACOP grant no. 20220187. Helena L¨ofstr¨om was a PhD
student in the Industrial Graduate School in Digital Retailing (INSiDR) at the
University of Bor˚as, funded by the Swedish Knowledge Foundation, grant no.
20160035 when this work was drafted.
• Competing interests: None
• Ethics approval: Not applicable.
• Consent to participate: Not applicable, no respondents involved.
• Consent for publication: All authors consent to publication. No respondents were
involved.
• Availability of data and materials: The evaluation/regression folder in the repos-
itory contains code for reproducing experiments. Plots corresponding to the
once included in the paper can be created using the demos for regression and
probabilistic regression in the notebooks folder.
• Code
availability:
github.com/Moffran/calibrated explanations
contains
the
Python package calibrated-explanations which is also available for instal-
lation through pip install calibrated-explanations or through conda
install -c conda-forge calibrated-explanations.
30
### Page 31

• Authors’ contributions: Tuwe L¨ofstr¨om has implemented both the extensions for
regression and the experiments and has written the major part of the paper.
Helena L¨ofstr¨om is the original inventor of the Calibrated Explanations and has
taken an active part in both discussions and in writing primarily the introduction
and background. Ulf Johansson and Cecilia S¨onstr¨od have contributed actively
to discussions. Ulf Johansson also contributed with an important improvement
making it possible to get rid of a direct reliance on lime. Cecilia S¨onstr¨od has
also been proofreading. Rudy Matela worked on the workflow for packaging and
release of the implementation as well as helping out with proofreading the paper.
References
[1] Zhou, J., Gandomi, A.H., Chen, F., Holzinger, A.: Evaluating the quality of
machine learning explanations: A survey on methods and metrics. Electronics
10(5), 593 (2021)
[2] David Gunning: Explainable Artificial Intelligence. Web. DARPA (2017). https:
//www.darpa.mil/attachments/XAIProgramUpdate.pdf Accessed 2019-08-29
[3] Ribeiro, M.T., Singh, S., Guestrin, C.: ”Why Should I Trust You?”: Explaining
the Predictions of Any Classifier. In: Proceedings of the 22nd ACM SIGKDD
International Conference on Knowledge Discovery and Data Mining. KDD ’16, pp.
1135–1144. Association for Computing Machinery, New York, NY, USA (2016).
https://doi.org/10.1145/2939672.2939778
[4] Alvarado-Valencia, J.A., Barrero, L.H.: Reliance, trust and heuristics in judgmen-
tal forecasting. Computers in human behavior 36, 102–113 (2014)
[5] Bu¸cinca, Z., Lin, P., Gajos, K.Z., Glassman, E.L.: Proxy tasks and subjective
measures can be misleading in evaluating explainable ai systems. In: Proceedings
of the 25th International Conference on Intelligent User Interfaces, pp. 454–464
(2020)
[6] Gunning, D., Aha, D.W.: Darpa’s explainable artificial intelligence program. AI
Magazine 40(2), 44–58 (2019)
[7] Dimanov, B., Bhatt, U., Jamnik, M., Weller, A.: You shouldn’t trust me: Learning
models which conceal unfairness from multiple explanation methods. Frontiers in
Artificial Intelligence and Applications: ECAI 2020 (2020)
[8] Guidotti, R., Monreale, A., Ruggieri, S., Turini, F., Giannotti, F., Pedreschi, D.:
A survey of methods for explaining black box models. ACM computing surveys
(CSUR) 51(5), 1–42 (2018)
[9] Moradi, M., Samwald, M.: Post-hoc explanation of black-box classifiers using
confident itemsets. Expert Systems with Applications 165, 113941 (2021)
31
### Page 32

[10] Martens, D., Foster, P.: Explaining data-driven document classifications. MIS
Quaterly 38(1), 73–100 (2014)
[11] Slack, D., Hilgard, A., Singh, S., Lakkaraju, H.: Reliable post hoc explanations:
Modeling uncertainty in explainability. Advances in neural information processing
systems 34, 9391–9404 (2021)
[12] Rahnama, A.H.A., Bostr¨om, H.: A study of data and label shift in the lime
framework. arXiv preprint arXiv:1910.14421 (2019)
[13] Hoffman, R.R., Mueller, S.T., Klein, G., Litman, J.: Metrics for explainable ai:
Challenges and prospects. Technical report, DARPA Explainable AI Program
(2018)
[14] Carvalho, D.V., Pereira, E.M., Cardoso, J.S.: Machine learning interpretability:
A survey on methods and metrics. Electronics 8(8), 832 (2019)
[15] Adadi, A., Berrada, M.: Peeking inside the black-box: A survey on explainable
artificial intelligence (xai). IEEE Access 6, 52138–52160 (2018)
[16] Wang, D., Yang, Q., Abdul, A., Lim, B.Y.: Designing theory-driven user-centric
explainable ai. In: Proceedings of the 2019 CHI Conference on Human Factors in
Computing Systems. CHI ’19, pp. 1–15. Association for Computing Machinery,
New York, NY, USA (2019). https://doi.org/10.1145/3290605.3300831 . https:
//doi.org/10.1145/3290605.3300831
[17] Mueller, S.T., Hoffman, R.R., Clancey, W., Emrey, A., Klein, G.: Explanation in
human-ai systems: A literature meta-review, synopsis of key ideas and publica-
tions, and bibliography for explainable ai. Technical report, DARPA Explainable
AI Program (2019)
[18] Agarwal, C., Krishna, S., Saxena, E., Pawelczyk, M., Johnson, N., Puri, I., Zitnik,
M., Lakkaraju, H.: Openxai: Towards a transparent evaluation of model expla-
nations. Advances in Neural Information Processing Systems 35, 15784–15799
(2022)
[19] Bhatt, U., Antor´an, J., Zhang, Y., Liao, Q.V., Sattigeri, P., Fogliato, R.,
Melan¸con, G., Krishnan, R., Stanley, J., Tickoo, O., et al.: Uncertainty as a form
of transparency: Measuring, communicating, and using uncertainty. In: Proceed-
ings of the 2021 AAAI/ACM Conference on AI, Ethics, and Society, pp. 401–413
(2021)
[20] Vovk, V.: Cross-conformal predictors. Annals of Mathematics and Artificial
Intelligence 74, 9–28 (2015)
[21] Platt, J., et al.: Probabilistic outputs for support vector machines and compar-
isons to regularized likelihood methods. Advances in large margin classifiers 10(3),
32
### Page 33

61–74 (1999)
[22] Vovk, V., Petej, I.: Venn-Abers predictors. arXiv preprint arXiv:1211.0025 (2012)
[23] L¨ofstr¨om, H., L¨ofstr¨om, T., Johansson, U., S¨onstr¨od, C.: Calibrated Explanations:
with Uncertainty Information and Counterfactuals (2023)
[24] Johansson, U., L¨ofstr¨om, T., Bostr¨om, H., S¨onstr¨od, C.: Interpretable and
specialized conformal predictors. In: COPA, pp. 3–22. PMLR, ??? (2019)
[25] Altmeyer, P., Farmanbar, M., Deursen, A., Liem, C.C.: Faithful model explana-
tions through energy-constrained conformal counterfactuals. In: Proceedings of
the AAAI Conference on Artificial Intelligence, vol. 38, pp. 10829–10837 (2024)
[26] Alkhatib, A., Bostrom, H., Ennadir, S., Johansson, U.: Approximating score-
based explanation techniques using conformal regression. In: Conformal and
Probabilistic Prediction with Applications, pp. 450–469 (2023). PMLR
[27] Artelt, A., Hammer, B.: “even if . . . ” – diverse semifactual explanations of reject.
In: 2022 IEEE Symposium Series on Computational Intelligence (SSCI), pp. 854–
859 (2022). https://doi.org/10.1109/SSCI51031.2022.10022139
[28] Artelt, A., Visser, R., Hammer, B.: Model agnostic local explanations of reject.
arXiv preprint arXiv:2205.07623 (2022)
[29] Artelt, A., Visser, R., Hammer, B.: “i do not know! but why?”—local model-
agnostic example-based explanations of reject. Neurocomputing 558, 126722
(2023)
[30] Letzgus, S., Wagner, P., Lederer, J., Samek, W., M¨uller, K.-R., Montavon, G.:
Toward explainable artificial intelligence for regression models: A methodological
perspective. IEEE Signal Processing Magazine 39(4), 40–58 (2022)
[31] Vovk, V., Gammerman, A., Shafer, G.: Algorithmic Learning in a Random World.
Springer, Berlin, Heidelberg (2005)
[32] Vovk, V., Shen, J., Manokhin, V., Xie, M.: Nonparametric predictive distributions
based on conformal prediction. Mach. Learn. 108(3), 445–474 (2019)
[33] Molnar, C.: Interpretable Machine Learning, 2nd edn. (2022). https://christophm.
github.io/interpretable-ml-book
[34] Mothilal, R.K., Sharma, A., Tan, C.: Explaining machine learning classifiers
through diverse counterfactual explanations. In: Proceedings of the 2020 Confer-
ence on Fairness, Accountability, and Transparency, pp. 607–617 (2020)
[35] Guidotti, R.: Counterfactual explanations and how to find them: literature review
and benchmarking. Data Mining and Knowledge Discovery, 1–55 (2022)
33
### Page 34

[36] Wachter, S., Mittelstadt, B., Russell, C.: Counterfactual explanations without
opening the black box: Automated decisions and the gdpr. Harv. JL & Tech. 31,
841 (2017)
[37] L¨ofstr¨om, H., Hammar, K., Johansson, U.: A meta survey of quality evaluation cri-
teria in explanation methods. In: De Weerdt, J., Polyvyanyy, A. (eds.) Intelligent
Information Systems, pp. 55–63. Springer, Cham (2022)
[38] Alvarez-Melis, D., Jaakkola, T.S.: On the robustness of interpretability methods.
arXiv preprint arXiv:1806.08049 (2018)
[39] Lundberg, S.M., Lee, S.-I.: A unified approach to interpreting model predic-
tions. In: Proceedings of the 31st International Conference on Neural Information
Processing Systems, pp. 4768–4777 (2017)
[40] Ribeiro, M.T., Singh, S., Guestrin, C.: Anchors: High-precision model-agnostic
explanations. In: Proceedings of the AAAI Conference on Artificial Intelligence,
vol. 32 (2018)
[41] Vovk, V., Shafer, G., Nouretdinov, I.: Self-calibrating probability forecasting. In:
Advances in Neural Information Processing Systems, pp. 1133–1140 (2004)
[42] Lambrou, A., Nouretdinov, I., Papadopoulos, H.: Inductive venn prediction.
Annals of Mathematics and Artificial Intelligence 74(1), 181–201 (2015)
[43] Papadopoulos, H., Proedrou, K., Vovk, V., Gammerman, A.: Inductive confidence
machines for regression. In: Machine Learning: ECML 2002: 13th European Con-
ference on Machine Learning Helsinki, Finland, August 19–23, 2002 Proceedings
13, pp. 345–356 (2002). Springer
[44] Papadopoulos, H., Gammerman, A., Vovk, V.: Normalized nonconformity mea-
sures for regression conformal prediction. In: Proceedings of the IASTED
International Conference on Artificial Intelligence and Applications (AIA 2008),
pp. 64–69 (2008)
[45] L¨ofstr¨om, H., L¨ofstr¨om, T.: Conditional Calibrated Explanations: Finding a Path
between Bias and Uncertainty. Manuscript submitted for publication (2024)
[46] Bostr¨om, H.: crepes: a python package for generating conformal regressors and
predictive systems. In: Johansson, U., Bostr¨om, H., An Nguyen, K., Luo, Z.,
Carlsson, L. (eds.) Proceedings of the Eleventh Symposium on Conformal and
Probabilistic Prediction and Applications. Proceedings of Machine Learning
Research, vol. 179 (2022). PMLR
[47] Pace, R.K., Barry, R.: Sparse spatial autoregressions. Statistics & Probability
Letters 33(3), 291–297 (1997)
34