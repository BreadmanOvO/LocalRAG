# AD-MLP Autonomous Driving with MLP

**Source**: arxiv PDF, 30 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

arXiv:2310.10984v1  [cs.SI]  17 Oct 2023
Latent class analysis with weighted responses
Huan Qinga,∗
aSchool of Economics and Finance, Chongqing University of Technology, Chongqing, 400054, China
Abstract
The latent class model has been proposed as a powerful tool for cluster analysis of categorical data in various
ﬁelds such as social, psychological, behavioral, and biological sciences. However, one important limitation of the
latent class model is that it is only suitable for data with binary responses, making it fail to model real-world data with
continuous or negative responses. In many applications, ignoring the weights throws out a lot of potentially valuable
information contained in the weights. To address this limitation, we propose a novel generative model, the weighted
latent class model (WLCM). Our model allows data’s response matrix to be generated from an arbitrary distribution
with a latent class structure. In comparison to the latent class model, our WLCM is more realistic and more general.
To our knowledge, our WLCM is the ﬁrst model for latent class analysis with weighted responses. We investigate
the identiﬁability of the model and propose an eﬃcient algorithm for estimating the latent classes and other model
parameters. We show that the proposed algorithm enjoys consistent estimation. The performance of the proposed
algorithm is investigated using both computer-generated and real-world weighted response data.
Keywords: Categorical data, latent class model, spectral method, SVD, weighted responses
1. Introduction
Latent class model (LCM) [1, 2, 3] is a powerful tool for categorical data, with many applications across vari-
ous areas such as social, psychological, behavioral, and biological sciences. These applications include movie rating
[4, 5], psychiatric evaluation [6, 7, 8, 9], educational assessments [10], political surveys [11, 12, 13, 14], transport
economics personal interview [15], and disease etiology detection [16, 17, 18]. In categorical data, subjects (individ-
uals) typically respond to several items (questions). LCM is a theoretical model that categorizes subjects into disjoint
groups, known as latent classes, according to their response pattern to a collection of categorical items. For example,
in movie rating, latent classes may represent diﬀerent groups of users with an aﬃnity for certain movie themes; in
psychological tests, latent classes may represent diﬀerent types of personalities. In educational assessments, latent
classes may indicate diﬀerent levels of abilities. In political surveys, latent classes may represent distinct types of
political ideologies. In transport economics personal interview, each latent class stands for a partition of the popula-
tion. In disease etiology detection, latent classes may represent diﬀerent disease categories. To infer latent classes for
categorical data generated from LCM, various approaches have been developed in recent years, including maximum
likelihood estimation techniques [19, 20, 21, 22] and tensor-based methods [23, 24].
To mathematically describe categorical data, let R be the N-by-J observed response matrix such that R(i, j) repre-
sents subject i’s response to item j, where N denotes the number of subjects and J denotes the number of items. For
LCM, researchers commonly focus on binary choice data where elements of the observed response matrix R only take
0 or 1 [16, 10, 24, 25, 26, 27, 28, 29, 30, 31, 32]. LCM models binary response matrix by generating its elements from
a Bernoulli distribution. In categorical data, binary responses can be agree/disagree responses in psychiatric eval-
uation, correct/wrong responses in educational assessments, and presence/absence of symptoms in disease etiology
detection. However, categorical data is more than binary response. Categorical data with weighted responses is also
commonly encountered in the real world and ignoring weighted data may lose potentially meaningful information
∗Corresponding author.
Email address: qinghuan@u.nus.edu&qinghuan07131995@163.com (Huan Qing)
Preprint submitted to Elsevier
October 18, 2023
### Page 2

[33]. For example, in movie rating [4], rating scores range in {1, 2, 3, 4, 5} and simply letting R be binary by record-
ing rated/not rated loses valuable information that can reﬂect users’ preference patterns; for real-world categorical
data from various online personality tests in the link https://openpsychometrics.org/_rawdata/, the range of
most responses are {0, 1, 2, . . ., m}, where m is an integer like 2, 5, and 10; in the buyer-seller rating e-commerce data
[34], elements of the observed response matrix take values in {−1, 0, 1} (for convenience, we call such R as signed
response matrix in this paper) since sellers are rated by users by applying three levels of rating, “Positive”, “Neutral”,
and “Negative”. In the users-jokes ratting categorical data Jester 100 [35], all responses (i.e., ratings) are continuous
numbers ranging in [−10, 10]. All aforementioned real-world data with weighted responses cannot be generated from
a Bernoulli distribution. Therefore, the classical latent class model is inadequate for handling the aforementioned data
with weighted responses. As a result, it is desirable to develop a more ﬂexible model for data with weighted responses.
With this motivation, our key contributions to the literature of latent class analysis are summarized as follows.
• Model. We propose a novel, identiﬁable, and generative statistical model, the weighted latent class model
(WLCM), for categorical data with weighted responses, where the responses can be continuous or negative
values. Our WLCM allows the elements of an observed weighted response matrix R to be generated from any
distribution provided that the population version of R under WLCM enjoys a latent class structure. For example,
our WLCM allows R to be generated from Bernoulli, Normal, Poisson, Binomial, Uniform, and Exponential
distributions, etc. By considering a speciﬁcally designed discrete distribution, our WLCM can also model
signed response matrices. For details, please refer to Examples 1-7. For comparison, LCM requires R to be
generated from Bernoulli distribution and LCM is a sub-model of our WLCM. Under the proposed model, the
elements of the observed weighted response matrix R can take any value. Therefore, WLCM is more ﬂexible
than LCM. As far as we know, our WLCM is the ﬁrst statistical model for categorical data in which weighted
responses can be continuous or negative values.
• Algorithm. We develop an easy-to-implement algorithm, spectral clustering with K-means (SCK), to infer
latent classes for weighted response matrices generated from arbitrary distribution under the proposed model.
Our algorithm is designed based on a combination of two popular techniques: the singular value decomposition
(SVD) and the K-means algorithm.
• Theoretical property. We build a theoretical framework to show that SCK enjoys consistent estimation under
WLCM. We also provide Examples 1-7 to show that the theoretical performance of the proposed algorithm can
be diﬀerent when the observed weighted response matrices R are generated from diﬀerent distributions under
the proposed model.
• Empirical validation. We conduct extensive simulations to validate our theoretical insights. Additionally, we
apply our SCK approach to two real-world datasets with meaningful interpretations.
The remainder of this paper is organized as follows. Section 2 describes the model. Section 3 details the algorithm.
Section 4 establishes the consistency results and provides examples for further analysis. Section 5 contains numerical
studies that verify our theoretical ﬁndings and examine the performance of the proposed method. Section 6 demon-
strates the proposed method using two real-world datasets. Section 7 concludes the paper with a brief discussion of
contributions and future work.
The following notations will be used throughout the paper. For any positive integer m, let [m] and Im×m be
[m] := {1, 2, . . ., m} and the m × m identity matrix, respectively. For any vector x and any q > 0, ∥x∥q denotes x’s
lq-norm. For any matrix M, M′ denotes its transpose, ∥M∥denotes its spectral norm, ∥M∥F denotes its Frobenius
norm, rank(M) denotes its rank, σi(M) denotes its i-th largest singular value, λi(M) denotes its i-th largest eigenvalue
ordered by magnitude, M(i, :) denotes its i-th row, and M(:, j) denotes its j-th column. Let R and N be the set of real
numbers and nonnegative integers, respectively. For any random variable X, E(X) and P(X = a) are the expectation
and the probability that X equals to a, respectively. Let Mm,K be the collection of all m × K matrices where each row
has only one 1 and all others 0.
2. Weighted latent class model
Unlike most researchers that only focus on binary responses, in our weighted response setting in this paper, all
elements of the observed weighted response matrix R are allowed to be any real value, i.e., R ∈RN×J.
2
### Page 3

Consider categorical data with N subjects and J items, where the N subjects belong to K disjoint extreme latent
proﬁles (also known as latent classes). Throughout this paper, the number of classes K is assumed to be a known
integer. To describe the membership of each subject, we let Z be a N × K matrix such that Z(i, k) is 1 if subject i
belongs to the k-th extreme latent proﬁle and Z(i, k) is 0 otherwise. Call Z the classiﬁcation matrix in this paper. For
each subject i ∈[N], it is assumed to belong to a single extreme latent proﬁle. For convenience, deﬁne ℓas a N-by-1
vector whose i-th entry ℓ(i) is k if the i-th subject belongs to the k-th extreme latent proﬁle for i ∈[N]. Thus for subject
i ∈[N], we have Z(i, ℓ(i)) = 1 and the other (K −1) entries of the K × 1 classiﬁcation vector Z(i, :) is 0.
Introduce the J × K item parameter matrix Θ ∈RJ×K. For k ∈[K], our weighted latent class model (WLCM)
assumes that Θ(j, k) collects the conditional-response expectation for the response of the i-th subject to the j-th item
under arbitrary distribution F provided that subject i belongs to the k-th extreme latent proﬁle. Speciﬁcally, for
i ∈[N], j ∈[J], given the classiﬁcation vector Z(i, :) of subject i and the item parameter matrix Θ, our WLCM
assumes that for arbitrary distribution F , the conditional response expectation of the i-th subject to the j-th item is
E(R(i, j)|Z(i, :), Θ) =
K
X
k=1
Z(i, k)Θ(j, k) ≡Θ(j, ℓ(i)).
(1)
Based on Equation (1), our WLCM can be simpliﬁed as follows.
Deﬁnition 1. Let R ∈RN×J denote the observed weighted response matrix. Let Z ∈MN,K be the classiﬁcation matrix
and Θ ∈RJ×K be the item parameter matrix. For i ∈[N], j ∈[J], our weighted latent class model (WLCM) assumes
that for an arbitrary distribution F , R(i, j) are independent random variables generated from the distribution F and
the expectation of R(i, j) under the distribution F should satisfy the following formula:
E(R(i, j)) = R0(i, j), where R0 := ZΘ′.
(2)
Deﬁnition 1 says that WLCM is determined by the classiﬁcation matrix Z, the item parameter matrix Θ, and
the distribution F . For brevity, we denote WLCM by WLCM(Z, Θ, F ). Under WLCM, F is allowed to be any
distribution as long as Equation (2) is satisﬁed under F , i.e., WLCM only requires the expectation (i.e., population)
response matrix R0 of the observed weighted response matrix R to be ZΘ′ under any distribution F .
Remark 1. For the case that F is Bernoulli distribution, all elements of Θ range in [0, 1], R only contains binary
responses (i.e., R(i, j) ∈{0, 1} for i ∈[N], j ∈[J] when F is Bernoulli distribution), and Equation (1) becomes
P(R(i, j) = 1|Z(i, :), Θ) = Θ(j, ℓ(i)). For this case, WLCM reduces to the LCM model, i.e., LCM is a special case of
our WLCM.
Remark 2. It should be noted that Equation (2) does not hold for all distributions. For instance, we cannot set F
as a t-distribution because the expectation of a t-distribution is always 0, which cannot capture the latent structure
required by the WLCM model; F cannot be a Cauchy distribution whose expectation even does not exist; F cannot
be a Chi-square distribution because the expectation of a Chi-square distribution is its degrees of freedom, which is
a ﬁxed positive integer and cannot capture the latent structure required by WLCM. We will provide some examples to
demonstrate that Equation (2) can be satisﬁed for diﬀerent distribution F . For details, please refer to Examples 1-7.
Remark 3. It should be also noted that the ranges of the observed weighted response matrix R and the item parameter
matrix Θ depend on distribution F . For example, when F is Bernoulli distribution, R ∈{0, 1}N×J and Θ ∈[0, 1]J×K;
when F is Poisson distribution, R ∈NN×J and Θ ∈[0, +∞)J×K; If we let F be Normal distribution, R ∈RN×J and
Θ ∈(−∞, +∞)J×K. For details, please refer to Examples 1-7.
The following proposition shows that the WLCM model is identiﬁable as long as there exists at least one subject
for every extreme latent proﬁle.
Proposition 1. (Identiﬁability). Consider a WLCM model as in Equation (2), when each extreme latent proﬁle has at
least one subject, the model is identiﬁable: for any other valid parameter set ( ˜Z, ˜Θ), if ˜Z ˜Θ′ = ZΘ′, then (Z, Θ) and
( ˜Z, ˜Θ) are identical up to a permutation of the K extreme latent proﬁles.
3
### Page 4

All proofs of theoretical results developed in this paper are given in the Appendix. The condition that each extreme
latent proﬁle must contain at least one subject means that each extreme latent proﬁle cannot be an empty set and we
have rank(Z) = K.
Remark 4. Note that Z and ˜Z are the same up to a permutation of the K latent classes in Proposition 1. A permutation
is acceptable since the equivalence of Z and ˜Z should not rely on how we label each of the K extreme latent proﬁles.
A similar argument holds for the identity of Θ and ˜Θ.
The observed weighted response matrix R along with the ground-truth classiﬁcation matrix Z and the item pa-
rameter matrix Θ can be generated using our WLCM model as follows: let R(i, j) be a random variable generated by
distribution F with expected value R0(i, j) for i ∈[N], j ∈[J], where R0 = ZΘ′ satisﬁes the latent structure required
by WLCM. In latent class analysis, given the observed weighted response matrix R generated from WLCM(Z, Θ, F ),
our goal is to infer the classiﬁcation matrix Z and the item parameter matrix Θ. Proposition 1 ensures that the model
parameters Z and Θ can be reliably inferred from the observed weighted response matrix R. In the following two
sections, we will develop a spectral algorithm to ﬁt WLCM and show that this algorithm yields consistent estimation.
3. A spectral method for parameters estimation
We have presented our model, WLCM, and demonstrated its superiority over the classical latent class model.
In addition to providing a more general model for latent class analysis, we are also interested in estimating the
model parameters. In this section, we focus on the parameter estimation problem within the WLCM framework
by developing an eﬃcient and easy-to-implement spectral method.
To provide insight into developing an algorithm for the WLCM model, we ﬁrst consider an oracle case where we
observe the expectation response matrix R0 given in Equation (2). We would like to estimate Z and Θ from R0. Recall
that the item parameter matrix Θ is a J-by-K matrix , here we let rank(Θ) = K0, where K0 is a positive integer and it
is no larger than K. As R0 = ZΘ′, rank(Z) = K, and rank(Θ) = K0 ≤K, we see that R0 is a rank-K0 matrix. As the
number of extreme latent proﬁles K is usually far smaller than the number of subjects N and the number of items J,
the N-by-J population response matrix R0 enjoys a low-dimensional structure. Next, we will demonstrate that we can
greatly beneﬁt from the low-dimensional structure of R0 when we aim to develop a method to infer model parameters
under the WLCM model.
Let R0 = UΣV′ be the compact singular value decomposition (SVD) of R0 such that Σ is a K0 ×K0 diagonal matrix
collecting the K0 nonzero singular values of R0. Write Σ = diag(σ1(R0), σ2(R0), . . ., σK0(R0)). The N × K0 matrix U
collects the corresponding left singular vectors and it satisﬁes U′U = IK0×K0. Similarly, the J × K0 matrix V collects
the corresponding right singular vectors and it satisﬁes V′V = IK0×K0. For k ∈[K], let Nk be the number of subjects
that belong to the k-th extreme latent proﬁle, i.e., Nk = PN
i=1 Z(i, k). The ensuing lemma constitutes the foundation of
our estimation method.
Lemma 1. Under WLCM(Z, Θ, F ), let R0 = UΣV′ be the compact SVD of R0. The following statements are true.
• (1) The left singular vectors matrix U can be written as
U = ZX,
(3)
where X is a K × K0 matrix.
• (2) U has K distinct rows such that for any two distinct subjects i and ¯i that belong to the same extreme latent
proﬁle (i.e., ℓ(i) = ℓ(¯i)), we have U(i, :) = U(¯i, :).
• (3) Θ can be written as
Θ = VΣU′Z(Z′Z)−1.
(4)
• (4) Furthermore, when K0 = K, for all k ∈[K], l ∈[K], and k , l, we have
∥X(k, :) −X(l, :)∥F = (N−1
k
+ N−1
l )1/2.
(5)
4
### Page 5

From now on, for the simplicity of our further analysis, we let K0 ≡K. Hence, the last statement of Lemma 1
always holds.
The second statement of Lemma 1 indicates that the rows of U corresponding to subjects assigned to the same
extreme latent proﬁle are identical. This circumstance implies that the application of a clustering algorithm to the
rows of U can yield an exact reconstruction of the classiﬁcation matrix Z after a permutation of the K extreme latent
proﬁles.
In this paper, we adopt the K-means clustering algorithm, an unsupervised learning technique that groups similar
data points into K clusters. This clustering technique is detailed as follows,
( ¯¯Z, ¯¯X) = arg min ¯Z∈MN,K, ¯X∈RK×K∥¯Z ¯X −¯U∥2
F,
(6)
where ¯U is any N × K matrix. For convenience, call Equation (6) as “Run K-means algorithm on all rows of ¯U with
K clusters to obtain ¯¯Z” because we are interested in the classiﬁcation matrix ¯¯Z. Let ¯U in Equation (6) be U, the
second statement of Lemma 1 guarantees that ¯¯Z = ZP, ¯¯X = P′X, where P is a K × K permutation matrix, i.e., running
K-means algorithm on all rows of U exactly recovers Z up to a permutation of the K extreme latent proﬁles.
After obtaining Z from U, Θ can be recovered subsequently by Equation (4). The above analysis suggests the
following algorithm, Ideal SCK, where SCK stands for Spectral Clustering with K-means. Ideal SCK returns a
permutation of (Z, Θ), which also supports the identiﬁability of the proposed model as stated in Proposition 1.
Algorithm 1 Ideal SCK
Require: The expectation response matrix R0 and the number of extreme latent proﬁles K.
Ensure: A permutation of Z and Θ.
1: Obtain UΣV′, the top K SVD of R0.
2: Run K-means algorithm on all rows of U with K clusters to obtain ZP, a permutation of Z.
3: Equation (4) gives VΣU′ZP((ZP)′ZP)−1 = ΘP, a permutation of Θ.
For the real case, the weighted response matrix R is observed rather than the expectation response matrix R0. We
now move from the ideal scenario to the real scenario, intending to estimate Z and Θ when the observed weighted re-
sponse matrix R is a random matrix generated from an unknown distribution F satisfying Equation (2) with K extreme
latent proﬁles under the WLCM model. The expectation of R is R0 according to Equation (2) under WLCM, so intu-
itively, the singular values and singular vectors of R will be close to those of R0. Set ˆR = ˆU ˆΣ ˆV′ as the top K SVD of R,
where ˆΣ is a K×K diagonal matrix collecting the top K singular values of R. Write ˆΣ = diag(σ1(R), σ2(R), . . ., σK(R)).
As E(R) = R0 and the N × J matrix R0 has K non-zero singular values while the other (min(N, J) −K) singular values
are zeros, we see that ˆR should be a good approximation of R0. Matrices ˆU ∈RN×K, ˆV ∈RJ×K collect the corre-
sponding left and right singular vectors and satisfy ˆU′ ˆU = ˆV′ ˆV = IK×K. The above analysis implies that ˆU should
have roughly K distinct rows because ˆU is a slightly perturbed version of U. Therefore, to obtain a good estimation
of the classiﬁcation matrix Z, we should apply the K-means algorithm on all rows of ˆU with K clusters. Let ˆZ be
the estimated classiﬁcation matrix returned by applying the K-means method on all rows of ˆU with K clusters. Then
we are able to obtain a good estimation of Θ according to Equation (4) by setting ˆΘ = ˆV ˆΣ ˆU′ ˆZ( ˆZ′ ˆZ)−1. Algorithm 2,
referred to as SCK, is a natural extension of the Ideal SCK from the oracle case to the real case. Note that in our SCK
algorithm, there are only two inputs: the observed weighted response matrix R and the number of latent classes K,
i.e., SCK does not require any tuning parameters.
Algorithm 2 Spectral Clustering with K-means (SCK for short)
Require: The observed weighted response matrix R ∈RN×J and the number of extreme latent proﬁles K.
Ensure: ˆZ and ˆΘ.
1: Obtain ˆR = ˆU ˆΣ ˆV′, the top K SVD of R.
2: Run K-means algorithm on all rows of ˆU with K clusters to obtain ˆZ.
3: Obtain an estimate of Θ by setting ˆΘ = ˆR′ ˆZ( ˆZ′ ˆZ)−1.
Here, we evaluate the computational cost of our SCK algorithm. The computational cost of the SVD step involved
in the SCK approach is O(max(N2, J2)K). For the K-means algorithm, its complexity is O(NlK2) with l being the
5
### Page 6

number of K-means iterations. In all experimental studies considered in this paper, l is set as 100 for the K-means
algorithm. The complexity of the last step in SCK is O(JNK). Since K ≪min(N, J) in this paper, as a consequence,
the total time complexity of our SCK algorithm is O(max(N2, J2)K).
4. Theoretical properties
In this section, we present comprehensive theoretical properties of the SCK algorithm when the observed weighted
response matrix R is generated from the proposed model. Our objective is to demonstrate that the estimated classiﬁ-
cation matrix ˆZ and the estimated item parameter matrix ˆΘ both concentrate around the true classiﬁcation matrix Z
and the true item parameter matrix Θ, respectively.
Let T = {T1, T2, . . . , TK} be the collection of true partitions for all subjects, where Tk = {i : Z(i, k) = 1 for i ∈[N]}
for k ∈[K], i.e., Tk is the set of true partition of subjects into the k-th extreme latent proﬁle. Similarly, let ˆT =
{ ˆT1, ˆT2, . . . , ˆTK} represent the collection of estimated partitions for all subjects, where ˆTk = {i : ˆZ(i, k) = 1 for i ∈[N]}
for k ∈[K]. We use the measure deﬁned in [36] to quantify the closeness of the estimated partition ˆT and the ground
truth partition T . Denote the Clustering error associated with T and ˆT as
ˆf = minπ∈S Kmaxk∈[K]
|Tk ∩ˆT c
π(k)| + |T c
k ∩ˆTπ(k)|
NK
,
(7)
where S K represents the set of all permutations of {1, 2, . . ., K}, ˆT c
π(k) and T c
k denote the complementary sets. As
stated in the reference [36], ˆf evaluates the maximum proportion of subjects in the symmetric diﬀerence of Tk and
ˆTπ(k). Since the observed weighted response matrix R is generated from WLCM with expectation R0, and ˆf measures
the performance of the SCK algorithm, it is expected that SCK estimates Z with small Clustering error ˆf.
For convenience, let ρ = maxj∈[J],k∈[K]|Θ(j, k)| and call it the scaling parameter. Let B = Θ
ρ , we have maxj∈[J],k∈[K]|B(j, k)| =
1 and R0 = ρZB′. Let τ = maxi∈[N], j∈[J]|R(i, j) −R0(i, j)| and γ = maxi∈[N], j∈[J]Var(R(i, j)) where Var(R(i, j)) means
the variance of R(i, j). We require the following assumption to establish theoretical guarantees of consistency for our
SCK method.
Assumption 1. Assume γ ≥τ2log(N+J)
max(N,J) .
The following theorem presents our main result, which provides upper bounds for the error rates of our SCK
algorithm under our WLCM model.
Theorem 1. Under WLCM(Z, Θ, F ), if Assumption 1 is satisﬁed, with probability at least 1 −o((N + J)−3),
ˆf = O(γK2Nmaxmax(N, J)log(N + J)
ρ2N2
minJ
) and ∥ˆΘ −ΘP∥F
∥Θ∥F
= O(
p
γKmax(N, J)log(N + J)
ρ √NminJ
),
where Nmax = maxk∈[K]{Nk}, Nmin = mink∈[K]{Nk}, and P is a permutation matrix.
Because our WLCM is distribution-free, Theorem 1 provides a general theoretical guarantee of the SCK algorithm
when R is generated from WLCM for any distribution F as long as Equation (2) is satisﬁed. We can simplify Theorem
1 by considering additional conditions:
Corollary 1. Under WLCM(Z, Θ, F ), when Assumption 1 holds, if we make the additional assumption that Nmax
Nmin =
O(1) and K = O(1), with probability at least 1 −o((N + J)−3),
ˆf = O(γmax(N, J)log(N + J)
ρ2NJ
) and ∥ˆΘ −ΘP∥F
∥Θ∥F
= O(
p
γmax(N, J)log(N + J)
ρ
√
NJ
).
For the case J = βN for any positive constant β, Corollary 1 implies that the SCK algorithm yields consistent
estimation under WLCM since the error bounds in Corollary 1 decrease to zero as N →+∞when ρ and distribution
F are ﬁxed.
6
### Page 7

Recall that R is an observed weighted response matrix generated from a distribution F with expectation R0 =
ZΘ′ = ρZB′ under the WLCM model and γ is the maximum variance of R(i, j) and it is closely related to the dis-
tribution F , the ranges of R, ρ, B, and γ can vary depending on the speciﬁc distribution F . The following examples
provide the ranges of R, ρ, B, the upper bound of γ, and the explicit forms of error bounds in Theorem 1 for diﬀerent
distribution F under our WLCM model. Meanwhile, based on the explicitly derived error bounds for diﬀerent distri-
bution F , we also investigate how the scaling parameter ρ inﬂuences the performance of the SCK algorithm in these
examples. For all pairs (i, j) with i ∈[N], j ∈[J], we consider the following distributions when E(R) = R0 in Equation
(2) holds.
Example 1. Let F be Bernoulli distribution such that R(i, j) ∼Bernoulli(R0(i, j)), where R0(i, j) is the Bernoulli
probability, i.e., E(R(i, j)) = R0(i, j). For this case, our WLCM degenerates to the LCM model. According to the
properties of the Bernoulli distribution, we have the following conclusions.
• R(i, j) ∈{0, 1}, i.e., R(i, j) only takes two values 0 and 1.
• B(i, j) ∈[0, 1] and ρ ∈(0, 1] because R0(i, j) is a probability located in [0, 1] and maxi∈[N], j∈[J]|B(i, j)| is
assumed to be 1.
• τ ≤1 because τ = maxi∈[N], j∈[J]|R(i, j) −R0(i, j)| ≤1.
• γ ≤ρ because γ = maxi∈[N], j∈[J]Var(R(i, j)) = maxi∈[N], j∈[J]R0(i, j)(1 −R0(i, j)) ≤maxi∈[N], j∈[J]R0(i, j) =
maxi∈[N], j∈[J]ρ(ZB)(i, j) ≤ρ.
• Let τ be its upper bound 1 and γ be its upper bound ρ, Assumption 1 becomes ρ ≥log(N+J)
max(N,J), which means a
sparsity requirement on R because ρ controls the probability of the numbers of ones in R for this case.
• Let γ be its upper bound ρ in Theorem 1, we have
ˆf = O(K2Nmaxmax(N, J)log(N + J)
ρN2
minJ
) and ∥ˆΘ −ΘP∥F
∥Θ∥F
= O(
p
Kmax(N, J)log(N + J)
√ρNminJ
).
We observe that increasing ρ leads to a decrease in SCK’s error rates when F is a Bernoulli distribution.
Example 2. Let F be Binomial distribution such that R(i, j) ∼Binomial(m, R0(i, j)
m ) for any positive integer m, where
R(i, j) is a random variable that reﬂects the number of successes in a ﬁxed number of independent trials m with the
same probability of success R0(i, j)
m , i.e., E(R(i, j)) = R0(i, j). For Binomial distribution, we have P(R(i, j) = r) =
m
r

( R0(i, j)
m )r(1 −R0(i, j)
m )m−r for r = 0, 1, 2, . . ., m, where
•
•

is a binomial coeﬃcient. By the property of the Binomial
distribution, we have the following conclusions.
• R(i, j) ∈{0, 1, 2, . . ., m}.
• B(i, j) ∈[0, 1] and ρ ∈(0, m] because R0(i, j)
m
is a probability that ranges in [0, 1].
• τ ≤m because τ = maxi∈[N], j∈[J]|R(i, j) −R0(i, j)| ≤m.
• γ ≤ρ because γ = maxi∈[N], j∈[J]Var(R(i, j)) = m R0(i, j)
m (1 −R0(i, j)
m
) = R0(i, j)(1 −R0(i, j)
m ) ≤ρ.
• Let τ be its upper bound m and γ be its upper bound ρ, Assumption 1 becomes ρ ≥m2log(N+J)
max(N,J) which provides a
lower bound requirement of the scaling parameter ρ.
• Let γ be its upper bound ρ in Theorem 1, we obtain the exact forms of error bounds for SCK when F is a
Binomial distribution, and we observe that increasing ρ reduces SCK’s error rates.
Example 3. Let F be Poisson distribution such that R(i, j) ∼Poisson(R0(i, j)), where R0(i, j) is the Poisson pa-
rameter, i.e., E(R(i, j)) = R0(i, j). By the properties of the Poisson distribution, the following conclusions can be
obtained.
7
### Page 8

• R(i, j) ∈N, i.e., R(i, j) is an nonnegative integer.
• B(i, j)] ∈[0, 1] and ρ ∈(0, +∞) because Poisson distribution can take any positive value for its mean.
• τ is an unknown positive value because we cannot know the exact upper bound of R(i, j) when R is obtained
from the Poisson distribution under the WLCM model.
• γ ≤ρ because γ = maxi∈[N], j∈[J]Var(R(i, j)) = maxi∈[N], j∈[J]R0(i, j) ≤ρ.
• Let γ be its upper bound ρ, Assumption 1 becomes ρ ≥τ2log(N+ j)
max(N,J) which is a lower bound requirement of ρ.
• Let γ be its upper bound ρ in Theorem 1 obtains the exact forms of error bounds for the SCK algorithm when
F is a Poisson distribution. It is easy to observe that increasing ρ leads to a decrease in SCK’s error rates.
Example 4. Let F be Normal distribution such that R(i, j) ∼Normal(R0(i, j), σ2), where R0(i, j) is the mean ( i.e.,
E(R(i, j)) = R0(i, j)) and σ2 is the variance parameter for Normal distribution. For this case, we have
• R(i, j) ∈R, i.e., R(i, j) is a real value.
• B(i, j) ∈[−1, 1] and ρ ∈(0, +∞) because the mean of Normal distribution can take any value. Note that, unlike
the cases when F is Bernoulli or Poisson, B can have negative elements for the Normal distribution case.
• Similar to Example 3, τ is an unknown positive value.
• γ = σ2 because γ = maxi∈[N], j∈[J]Var(R(i, j)) = maxi∈[N], j∈[J]σ2 = σ2 for Normal distribution.
• Let γ be its exact value σ2, Assumption 1 becomes σ2max(N, J) ≥τ2log(N + J) which means that max(N, J)
should be set larger than τ2log(N+J)
σ2
for our theoretical analysis.
• Let γ be its exact value σ2 in Theorem 1 provides the exact forms of error bounds for SCK. We observe that
increasing the scaling parameter ρ (or decreasing the variance σ2) reduces SCK’s error rates.
Example 5. Let F be Exponential distribution such that R(i, j) ∼Exponential(
1
R0(i, j)), where
1
R0(i, j) is the Exponential
parameter, i.e., E(R(i, j)) = R0(i, j). For this case, we have
• R(i, j) ∈R+, i.e., R(i, j) is a positive value.
• B(i, j) ∈(0, 1] and ρ ∈(0, +∞) because the mean of Exponential distribution can be any positive value.
• Similar to Example 3, τ is an unknown positive value.
• γ ≤ρ2 because γ = maxi∈[N], j∈[J]Var(R(i, j)) = maxi∈[N], j∈[J]R2
0(i, j) ≤ρ2 for Exponential distribution.
• Let γ be its upper bound ρ2, Assumption 1 becomes ρ2 ≥τ2log(N + J)/max(N, J), a lower bound requirement
of ρ.
• Let γ be its upper bound ρ2 in Theorem 1, the theoretical bounds demonstrate that ρ vanishes, which indicates
that increasing ρ has no signiﬁcant impact on the error rates of SCK.
Example 6. Let F be Uniform distribution such that R(i, j) ∼Uniform(0, 2R0(i, j)), where E(R(i, j)) = 0+2R0(i, j)
2
=
R0(i, j) holds immediately. For this case, we have
• R(i, j) ∈(0, 2ρ) because 2R0(i, j) ≤2ρ.
• B(i, j) ∈(0, 1] and ρ ∈(0, +∞) because Uniform(0, 2R0(i, j)) allows 2R0(i, j) to be any positive value.
• τ is an unknown positive value with an upper bound 2ρ.
• γ ≤ρ2
3 because γ = maxi∈[N], j∈[J]Var(R(i, j)) = maxi∈[N], j∈[J]
(2R0(i, j)−0)2
12
= maxi∈[N], j∈[J]
R2
0(i, j)
3
≤ρ2
3 for Uniform
distribution.
8
### Page 9

• Let γ be its upper bound ρ2
3 , Assumption 1 becomes ρ2 ≥3τ2log(N + J)/max(N, J), a lower bound requirement
of ρ.
• Since ρ disappears in the error bounds when we let γ = ρ2
3 in Theorem 1, increasing ρ does not signiﬁcantly
inﬂuence SCK’s error rates, a conclusion similar to Example 5.
Example 7. Our WLCM can also model signed response matrix by setting P(R(i, j) = 1) = 1+R0(i, j)
2
and P(R(i, j) =
−1) = 1−R0(i, j)
2
, where E(R(i, j)) = 1+R0(i, j)
2
−1−R0(i, j)
2
= R0(i, j) and Equation (2) holds surely. For the signed response
matrix, we have
• R(i, j) ∈{−1, 1}, i.e., R(i, j) only takes two values -1 and 1.
• B(i, j) ∈[−1, 1] and ρ ∈(0, 1] because 1+R0(i, j)
2
and 1−R0(i, j)
2
are two probabilities which should range in [0, 1].
Note that similar to Example 4, B(i, j) can be negative for the signed response matrix.
• τ ≤2 because R(i, j) ∈{−1, 1} and R0(i, j) ∈[−1, 1].
• γ ≤1 because γ = maxi∈[N], j∈[J]Var(R(i, j)) = maxi∈[N], j∈[J](1 −R2
0(i, j)) ≤1.
• When setting τ = 2 and γ = 1, Assumption 1 turns to be max(N, J) ≥4log(N + J).
• Setting γ as its upper bound 1 in Theorem 1 gives that increasing ρ reduces SCK’s error rates.
5. Simulation studies
In this section, we conduct extensive simulation experiments to evaluate the eﬀectiveness of the proposed method
and validate our theoretical results in Examples 1-7.
5.1. Baseline method
More than the SCK algorithm, here we brieﬂy provide an alternative spectral method that can also be applied to
ﬁt our WLCM model. Recall that R0 = ZΘ′ under WLCM, it is easy to see that R0(i, :) = R0(¯i, :) when two distinct
subjects i and ¯i belong to the same extreme latent proﬁle for i,¯i ∈[N]. Therefore, the population response matrix
R0 features K disparate rows, and running the K-means approach on all rows of R0 with K clusters can faithfully
recover the classiﬁcation matrix Z in terms of a permutation of the K extreme latent proﬁles. R0 = ZΘ′ also gives that
Θ = R′
0Z(Z′Z)−1, which suggests the following ideal algorithm called Ideal RMK.
Algorithm 3 Ideal RMK
Require: R0, K.
Ensure: A permutation of Z and Θ.
1: Run K-means algorithm on all rows of R0 with K clusters to obtain ZP, a permutation of Z.
2: Compute R′
0ZP((ZP)′ZP)−1 = ΘP, a permutation of Θ.
Algorithm 4 called RMK is a natural generalization of the Ideal RMK from the oracle case to the real case because
E(R) = R0 under the WLCM model. Unlike the SCK method, the RMK method does not need to obtain the SVD of
the observed weighted response matrix R.
Algorithm 4 Response Matrix with K-means (RMK for short)
Require: R, K.
Ensure: ˆZ, ˆΘ.
1: Run K-means algorithm on all rows of R with K clusters to obtain ˆZ.
2: Obtain an estimate of Θ by setting ˆΘ = R′ ˆZ( ˆZ′ ˆZ)−1.
9
### Page 10

The computational cost of the ﬁrst step in RMK is O(lNJK), where l denotes the number of iterations for the
K-means algorithm. The complexity of the second step in RMK is O(JNK). Therefore, the overall computational
cost of RMK is O(lNJK). When J = βN for a constant value β ∈(0, 1], the complexity of RMK is O(βlKN2), and
it is larger than the SCK’s complexity O(KN2) when βl > 1. Therefore, SCK runs faster than RMK when βl > 1, as
conﬁrmed by our numerical results in this section.
5.2. Evaluation metric
For the classiﬁcation of subjects, when the true classiﬁcation matrix Z is known, to evaluate how good the quality
of the partition of the subjects into extreme latent proﬁles, four metrics are considered including the Clustering error
ˆf computed by Equation (7). The other three popular evaluation criteria are Hamming error [37], normalized mutual
information (NMI) [38, 39, 40, 41], and adjusted rand index (ARI) [41, 42, 43].
• Hamming error is deﬁned as
Hamming error = N−1minP∈PK∥ˆZ −ZP∥0,
where PK denotes the collection of all K-by-K permutation matrices. Hamming error falls within the range
[0, 1], and a smaller Hamming error indicates better classiﬁcation performance.
• Let C be a K × K confusion matrix such that C(k, l) is the number of common subjects between Tk and ˆTl for
k, l ∈[K]. NMI is deﬁned as
NMI =
−2 P
k,l C(k, l)log( C(k,l)N
Ck.C.l )
P
k Ck.log( Ck.
N ) + P
l C.llog( C.l
N )
,
where Ck. = PK
m=1 C(k, m) and C.l = PK
m=1 C(m, l). NMI ranges in [0, 1] and it is the larger the better.
• ARI is deﬁned as
ARI =
P
k,l
C(k,l)
2

−
P
k (Ck.
2 ) P
l (C.l
2 )
(N
2)
1
2[P
k
Ck.
2

+ P
l
C.l
2

] −
P
k (
Ck.
2 ) P
l (
C.l
2 )
(N
2)
,
where
.
.

is a binomial coeﬃcient. ARI falls within the range [-1,1] and it is the larger the better.
For the estimation of Θ, we use the Relative l1 error and the Relative l2 error to evaluate the performance. The two
criteria are deﬁned as
Relative l1 error = minP∈PK
∥ˆΘ −ΘP∥1
∥Θ∥1
and Relative l2 error = minP∈PK
∥ˆΘ −ΘP∥F
∥Θ∥F
.
Both measures are the smaller the better.
5.3. Synthetic weighted response matrices
We conduct numerical studies to examine the accuracy and the eﬃciency of our SCK and RMK approaches by
changing the scaling parameter ρ and the number of subjects N. Unless speciﬁed, in all computer-generated weighted
response matrices, we set K = 3, J = N
5 , and the N × K classiﬁcation matrix Z is generated such that each subject
belongs to one of the K extreme latent proﬁles with equal probability. For distributions that require B’s entries to be
nonnegative, we let B(j, k) = rand(1) for j ∈[J], k ∈[K], where rand(1) is a random value simulated from the uniform
distribution on [0, 1]. For Normal distribution and signed response matrix that allow B to have negative entries, we let
B(j, k) = 2rand(1) −1 for j ∈[J], k ∈[K], i.e., B(j, k) ranges in [−1, 1]. Set Bmax = maxj∈[J],k∈[K]|B(j, k)|. Because
the generation process of B makes |B(j, k)| ∈[0, 1] but cannot guarantee that Bmax = 1 which is required in the
deﬁnition of B. Therefore, we update B by
B
Bmax . For the scaling parameter ρ and the number of subjects N, they
are set independently for each distribution. After setting all model parameters (K, N, J, Z, B, ρ), we can generate the
10
### Page 11

observed weighted response matrix R from distribution F with expectation R0 = ZΘ′ = ρZB′ under our WLCM
model. By applying the SCK method (and the RMK method) to R with K extreme latent proﬁles, we can compute
the evaluation metrics of SCK (and RMK). In every simulation scenario, we generate 50 independent replicates and
report the mean of Clustering error (as well as Hamming error, NMI, ARI, Relative l1 error, Relative l2 error, and
running time) computed from the 50 repetitions for each method.
5.3.1. Bernoulli distribution
When R(i, j) ∼Bernoulli(R0(i, j)) for i ∈[N], j ∈[J], we consider the following two simulations.
Simulation 1(a): changing ρ. Set N = 500. For the Bernoulli distribution, the scaling parameter ρ should be set
within the range (0, 1] according to Example 1. Here, for simulation studies, we let ρ range in {0.1, 0.2, 0.3, . . ., 1}.
Simulation 1(b): changing N. Let ρ = 0.1 and N range in {1000, 2000, . . ., 5000}.
The results are presented in Figure 1. We observe that SCK outperforms RMK because SCK returns more accurate
estimations of (Z, Θ) and SCK runs faster than RMK across all settings. Both methods achieve better performances as
ρ increases, which conforms to our analysis in Example 1. Additionally, both algorithms enjoy better performances
when the number of subjects N increases, as predicted by our analysis following Corollary 1.
5.3.2. Binomial distribution
When R(i, j) ∼Binomial(m, R0(i, j)
m ) for i ∈[N], j ∈[J], we consider the following two simulations.
Simulation 2(a): changing ρ. Set N = 500 and m = 5. Recall that ρ’s range is (0, m] when F is Binomial
distribution according to Example 2, here, we let ρ range in {0.2, 0.4, 0.6, . . ., 2}.
Simulation 2(b): changing N. Let ρ = 0.1, m = 5, and N range in {1000, 2000, . . ., 5000}.
Figure 2 presents the corresponding results. We note that SCK and RMK have similar error rates, while SCK runs
faster than RMK for this simulation. Meanwhile, increasing ρ (and N) decreases error rates for both methods, which
conﬁrms our ﬁndings in Example 2 and Corollary 1.
5.3.3. Poisson distribution
When R(i, j) ∼Poisson(R0(i, j)) for i ∈[N], j ∈[J], we consider the following two simulations.
Simulation 3(a): changing ρ. Set N = 500. Example 3 says that the theoretical range of ρ is (0, +∞) when F is
Poisson distribution. Here, we let ρ range in {0.2, 0.4, 0.6, . . ., 2}.
Simulation 3(b): changing N. Let ρ = 0.1 and N range in {1000, 2000, . . ., 5000}.
Figure 3 displays the numerical results of Simulation 3(a) and Simulation 3(b). The results are similar to those
of the Bernoulli distribution case: SCK outperforms RMK in both estimating (Z, Θ) and running time; Both methods
perform better as ρ and N increase, which supports our analysis in Example 3 and Corollary 1.
5.3.4. Normal distribution
When R(i, j) ∼Normal(R0(i, j), σ2) for i ∈[N], j ∈[J], we consider the following two simulations.
Simulation 4(a): changing ρ. Set N = 500 and σ2 = 2. According to Example 4, the scaling parameter ρ can be
set as any positive value when F is Normal distribution. Here, we let ρ range in {0.2, 0.4, 0.6, . . ., 2}.
Simulation 4(b): changing N. Let ρ = 0.5, σ2 = 2, and N range in {1000, 2000, . . ., 5000}.
Figure 4 shows the results. We see that SCK and RMK have similar performances in estimating model parameters
(Z, Θ) while SCK runs faster than RMK. Additionally, the error rates of both approaches decrease when the scaling
parameter ρ and the number of subjects N increase, supporting our ﬁndings in Example 4 and Corollary 1.
5.3.5. Exponential distribution
When R(i, j) ∼Exponential(
1
R0(i, j)) for i ∈[N], j ∈[J], we consider the following two simulations.
Simulation 5(a): changing ρ. Set N = 300. According to Example 5, the range of the scaling parameter ρ is
(0, +∞) when F is Exponential distribution. Here, we let ρ range in {1, 2, . . ., 20} for our numerical studies.
Simulation 5(b): changing N. Let ρ = 1 and N range in {300, 600, . . ., 3000}.
Figure 5 displays the results. We see that both methods provide satisfactory estimations for Z and Θ for their small
error rates, large NMI, and large ARI. SCK provides more accurate estimations than RMK and SCK takes less time
for estimations than RMK. Meanwhile, we ﬁnd that increasing ρ does not signiﬁcantly inﬂuence the performances
11
### Page 12

0
0.2
0.4
0.6
0.8
1
0
0.5
1
1.5
2
Clustering error
SCK
RMK
(a) Simulation 1(a)
0
0.2
0.4
0.6
0.8
1
0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
Hamming error
SCK
RMK
(b) Simulation 1(a)
0
0.2
0.4
0.6
0.8
1
0
0.2
0.4
0.6
0.8
1
NMI
SCK
RMK
(c) Simulation 1(a)
0
0.2
0.4
0.6
0.8
1
0
0.2
0.4
0.6
0.8
1
ARI
SCK
RMK
(d) Simulation 1(a)
0
0.2
0.4
0.6
0.8
1
0
0.2
0.4
0.6
0.8
SCK
RMK
(e) Simulation 1(a)
0
0.2
0.4
0.6
0.8
1
0
0.2
0.4
0.6
0.8
1
1.2
1.4
SCK
RMK
(f) Simulation 1(a)
0
0.2
0.4
0.6
0.8
1
0
0.1
0.2
0.3
0.4
0.5
0.6
Running time /s
SCK
RMK
(g) Simulation 1(a)
1000
2000
3000
4000
5000
N
0
0.5
1
1.5
Clustering error
SCK
RMK
(h) Simulation 1(b)
1000
2000
3000
4000
5000
N
0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
Hamming error
SCK
RMK
(i) Simulation 1(b)
1000
2000
3000
4000
5000
N
0
0.2
0.4
0.6
0.8
1
NMI
SCK
RMK
(j) Simulation 1(b)
1000
2000
3000
4000
5000
N
0
0.2
0.4
0.6
0.8
1
ARI
SCK
RMK
(k) Simulation 1(b)
1000
2000
3000
4000
5000
N
0
0.1
0.2
0.3
0.4
0.5
0.6
SCK
RMK
(l) Simulation 1(b)
1000
2000
3000
4000
5000
N
0
0.2
0.4
0.6
0.8
1
SCK
RMK
(m) Simulation 1(b)
1000
2000
3000
4000
5000
N
0
5
10
15
20
Running time /s
SCK
RMK
(n) Simulation 1(b)
Figure 1: Numerical results of Simulation 1.
12
### Page 13

0
0.5
1
1.5
2
0
0.2
0.4
0.6
0.8
1
1.2
1.4
Clustering error
SCK
RMK
(a) Simulation 2(a)
0
0.5
1
1.5
2
0
0.1
0.2
0.3
0.4
0.5
0.6
Hamming error
SCK
RMK
(b) Simulation 2(a)
0
0.5
1
1.5
2
0
0.2
0.4
0.6
0.8
1
NMI
SCK
RMK
(c) Simulation 2(a)
0
0.5
1
1.5
2
0
0.2
0.4
0.6
0.8
1
ARI
SCK
RMK
(d) Simulation 2(a)
0
0.5
1
1.5
2
0
0.1
0.2
0.3
0.4
0.5
SCK
RMK
(e) Simulation 2(a)
0
0.5
1
1.5
2
0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
SCK
RMK
(f) Simulation 2(a)
0
0.5
1
1.5
2
0.05
0.1
0.15
0.2
0.25
0.3
0.35
0.4
Running time /s
SCK
RMK
(g) Simulation 2(a)
1000
2000
3000
4000
5000
N
0
0.5
1
1.5
Clustering error
SCK
RMK
(h) Simulation 2(b)
1000
2000
3000
4000
5000
N
0
0.1
0.2
0.3
0.4
0.5
0.6
Hamming error
SCK
RMK
(i) Simulation 2(b)
1000
2000
3000
4000
5000
N
0
0.2
0.4
0.6
0.8
1
NMI
SCK
RMK
(j) Simulation 2(b)
1000
2000
3000
4000
5000
N
0
0.2
0.4
0.6
0.8
1
ARI
SCK
RMK
(k) Simulation 2(b)
1000
2000
3000
4000
5000
N
0
0.1
0.2
0.3
0.4
0.5
0.6
SCK
RMK
(l) Simulation 2(b)
1000
2000
3000
4000
5000
N
0
0.2
0.4
0.6
0.8
1
SCK
RMK
(m) Simulation 2(b)
1000
2000
3000
4000
5000
N
0
5
10
15
Running time /s
SCK
RMK
(n) Simulation 2(b)
Figure 2: Numerical results of Simulation 2.
13
### Page 14

0
0.5
1
1.5
2
0
0.2
0.4
0.6
0.8
1
1.2
Clustering error
SCK
RMK
(a) Simulation 3(a)
0
0.5
1
1.5
2
0
0.1
0.2
0.3
0.4
0.5
Hamming error
SCK
RMK
(b) Simulation 3(a)
0
0.5
1
1.5
2
0
0.2
0.4
0.6
0.8
1
NMI
SCK
RMK
(c) Simulation 3(a)
0
0.5
1
1.5
2
0
0.2
0.4
0.6
0.8
1
ARI
SCK
RMK
(d) Simulation 3(a)
0
0.5
1
1.5
2
0
0.1
0.2
0.3
0.4
0.5
0.6
SCK
RMK
(e) Simulation 3(a)
0
0.5
1
1.5
2
0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
SCK
RMK
(f) Simulation 3(a)
0
0.5
1
1.5
2
0
0.1
0.2
0.3
0.4
0.5
0.6
Running time /s
SCK
RMK
(g) Simulation 3(a)
1000
2000
3000
4000
5000
N
0
0.5
1
1.5
Clustering error
SCK
RMK
(h) Simulation 3(b)
1000
2000
3000
4000
5000
N
0
0.1
0.2
0.3
0.4
0.5
0.6
Hamming error
SCK
RMK
(i) Simulation 3(b)
1000
2000
3000
4000
5000
N
0
0.2
0.4
0.6
0.8
1
NMI
SCK
RMK
(j) Simulation 3(b)
1000
2000
3000
4000
5000
N
0
0.2
0.4
0.6
0.8
1
ARI
SCK
RMK
(k) Simulation 3(b)
1000
2000
3000
4000
5000
N
0
0.1
0.2
0.3
0.4
0.5
0.6
SCK
RMK
(l) Simulation 3(b)
1000
2000
3000
4000
5000
N
0
0.2
0.4
0.6
0.8
1
SCK
RMK
(m) Simulation 3(b)
1000
2000
3000
4000
5000
N
0
5
10
15
20
Running time /s
SCK
RMK
(n) Simulation 3(b)
Figure 3: Numerical results of Simulation 3.
14
### Page 15

0
0.5
1
1.5
2
0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
Hamming error
SCK
RMK
(a) Simulation 4(a)
0
0.5
1
1.5
2
0
0.1
0.2
0.3
0.4
0.5
Hamming error
SCK
RMK
(b) Simulation 4(a)
0
0.5
1
1.5
2
0
0.2
0.4
0.6
0.8
1
NMI
SCK
RMK
(c) Simulation 4(a)
0
0.5
1
1.5
2
0
0.2
0.4
0.6
0.8
1
ARI
SCK
RMK
(d) Simulation 4(a)
0
0.5
1
1.5
2
0
0.5
1
1.5
2
2.5
3
SCK
RMK
(e) Simulation 4(a)
0
0.5
1
1.5
2
0
0.5
1
1.5
2
2.5
3
SCK
RMK
(f) Simulation 4(a)
0
0.5
1
1.5
2
0.1
0.2
0.3
0.4
0.5
0.6
Running time /s
SCK
RMK
(g) Simulation 4(a)
1000
2000
3000
4000
5000
N
0
0.1
0.2
0.3
0.4
Clustering error
SCK
RMK
(h) Simulation 4(b)
1000
2000
3000
4000
5000
N
0
0.05
0.1
0.15
0.2
Hamming error
SCK
RMK
(i) Simulation 4(b)
1000
2000
3000
4000
5000
N
0.4
0.5
0.6
0.7
0.8
0.9
1
NMI
SCK
RMK
(j) Simulation 4(b)
1000
2000
3000
4000
5000
N
0.5
0.6
0.7
0.8
0.9
1
ARI
SCK
RMK
(k) Simulation 4(b)
1000
2000
3000
4000
5000
N
0.15
0.2
0.25
0.3
0.35
0.4
0.45
0.5
SCK
RMK
(l) Simulation 4(b)
1000
2000
3000
4000
5000
N
0.1
0.2
0.3
0.4
0.5
SCK
RMK
(m) Simulation 4(b)
1000
2000
3000
4000
5000
N
0
2
4
6
8
10
12
14
Running time /s
SCK
RMK
(n) Simulation 4(b)
Figure 4: Numerical results of Simulation 4.
15
### Page 16

0
5
10
15
20
0.01
0.015
0.02
0.025
Clustering error
SCK
RMK
(a) Simulation 5(a)
0
5
10
15
20
3
4
5
6
7
8
9
Hamming error
10-3
SCK
RMK
(b) Simulation 5(a)
0
5
10
15
20
0.96
0.965
0.97
0.975
0.98
0.985
NMI
SCK
RMK
(c) Simulation 5(a)
0
5
10
15
20
0.975
0.98
0.985
0.99
ARI
SCK
RMK
(d) Simulation 5(a)
0
5
10
15
20
0.08
0.085
0.09
0.095
0.1
0.105
0.11
SCK
RMK
(e) Simulation 5(a)
0
5
10
15
20
0.095
0.1
0.105
0.11
0.115
0.12
0.125
0.13
SCK
RMK
(f) Simulation 5(a)
0
5
10
15
20
0.06
0.08
0.1
0.12
0.14
0.16
0.18
0.2
Running time /s
SCK
RMK
(g) Simulation 5(a)
0
500
1000
1500
2000
2500
3000
N
0
0.005
0.01
0.015
0.02
Clustering error
SCK
RMK
(h) Simulation 5(b)
0
500
1000
1500
2000
2500
3000
N
0
1
2
3
4
5
6
Hamming error
10-3
SCK
RMK
(i) Simulation 5(b)
0
500
1000
1500
2000
2500
3000
N
0.97
0.975
0.98
0.985
0.99
0.995
1
NMI
SCK
RMK
(j) Simulation 5(b)
0
500
1000
1500
2000
2500
3000
N
0.98
0.985
0.99
0.995
1
ARI
SCK
RMK
(k) Simulation 5(b)
0
500
1000
1500
2000
2500
3000
N
0.02
0.04
0.06
0.08
0.1
0.12
SCK
RMK
(l) Simulation 5(b)
0
500
1000
1500
2000
2500
3000
N
0.02
0.04
0.06
0.08
0.1
0.12
0.14
SCK
RMK
(m) Simulation 5(b)
0
500
1000
1500
2000
2500
3000
N
0
0.5
1
1.5
2
2.5
3
3.5
Running time /s
SCK
RMK
(n) Simulation 5(b)
Figure 5: Numerical results of Simulation 5.
of SCK and RMK and this veriﬁes our theoretical analysis in Example 5 that ρ disappears in the theoretical upper
bounds of error rates by setting γ = ρ2 in Theorem 1 for Exponential distribution. Furthermore, when we increase N,
both methods perform better and this supports our analysis after Corollary 1.
5.3.6. Uniform distribution
When R(i, j) ∼Uniform(0, 2R0(i, j)) for i ∈[N], j ∈[J], we consider the following two simulations.
Simulation 6(a): changing ρ. Set N = 120. According to Example 6, the scaling parameter ρ can be set as any
positive value when F is Uniform distribution. Here, we let ρ range in {1, 2, . . ., 20}.
Simulation 6(b): changing N. Let ρ = 1 and N range in {300, 600, . . ., 3000}.
Figure 6 displays the numerical results. We see that increasing ρ does not signiﬁcantly decrease or increase esti-
mation accuracies of SCK and RMK which veriﬁes our theoretical analysis in Example 6. For all settings, SCK runs
faster than RMK. When increasing N, the Clustering error and Hamming error (NMI and ARI) for both approaches
are 0 (1), and this suggests that SCK and RMK return the exact estimation of the classiﬁcation matrix Z. This phe-
nomenon occurs because N is set quite large for Uniform distribution in Simulation 6(b). For the estimation of Θ,
16
### Page 17

0
5
10
15
20
0.015
0.02
0.025
0.03
Clustering error
SCK
RMK
(a) Simulation 6(a)
0
5
10
15
20
5
6
7
8
9
10
Hamming error
10-3
SCK
RMK
(b) Simulation 6(a)
0
5
10
15
20
0.96
0.965
0.97
0.975
0.98
NMI
SCK
RMK
(c) Simulation 6(a)
0
5
10
15
20
0.972
0.974
0.976
0.978
0.98
0.982
0.984
0.986
ARI
SCK
RMK
(d) Simulation 6(a)
0
5
10
15
20
0.08
0.085
0.09
0.095
0.1
SCK
RMK
(e) Simulation 6(a)
0
5
10
15
20
0.09
0.095
0.1
0.105
SCK
RMK
(f) Simulation 6(a)
0
5
10
15
20
0.05
0.055
0.06
0.065
0.07
0.075
0.08
0.085
Running time /s
SCK
RMK
(g) Simulation 6(a)
0
500
1000
1500
2000
2500
3000
N
-1
-0.5
0
0.5
1
Clustering error
SCK
RMK
(h) Simulation 6(b)
0
500
1000
1500
2000
2500
3000
N
-1
-0.5
0
0.5
1
Hamming error
SCK
RMK
(i) Simulation 6(b)
0
500
1000
1500
2000
2500
3000
N
0
0.5
1
1.5
2
NMI
SCK
RMK
(j) Simulation 6(b)
0
500
1000
1500
2000
2500
3000
N
0
0.5
1
1.5
2
ARI
SCK
RMK
(k) Simulation 6(b)
0
500
1000
1500
2000
2500
3000
N
0.01
0.02
0.03
0.04
0.05
0.06
SCK
RMK
(l) Simulation 6(b)
0
500
1000
1500
2000
2500
3000
N
0.01
0.02
0.03
0.04
0.05
0.06
0.07
SCK
RMK
(m) Simulation 6(b)
0
500
1000
1500
2000
2500
3000
N
0
0.5
1
1.5
2
2.5
3
3.5
Running time /s
SCK
RMK
(n) Simulation 6(b)
Figure 6: Numerical results of Simulation 6.
error rates for both methods decrease when we increase N and this is consistent with our ﬁndings following Corollary
1.
5.3.7. Signed response matrix
For signed response matrices when P(R(i, j) = 1) = 1+R0(i, j)
2
and P(R(i, j) = −1) = 1−R0(i, j)
2
for i ∈[N], j ∈[J], we
consider the following two simulations.
Simulation 7(a): changing ρ. Set N = 500. Recall that the theoretical range of the scaling parameter ρ is (0, 1]
for signed response matrices according to our analysis in Example 7, here, we let ρ range in {0.1, 0.2, . . ., 1}.
Simulation 7(b): changing N. Let ρ = 0.2 and N range in {1000, 2000, . . ., 5000}.
Figure 7 shows the results. We see that increasing ρ and N improves the estimation accuracies of SCK and RMK,
which conﬁrms our analysis in Example 7 and Corollary 1. Additionally, it is easy to see that both algorithms enjoy
similar performances in estimating Z and Θ, and SCK requires less computation time compared to RMK.
17
### Page 18

0
0.2
0.4
0.6
0.8
1
0
0.2
0.4
0.6
0.8
1
1.2
1.4
Clustering error
SCK
RMK
(a) Simulation 7(a)
0
0.2
0.4
0.6
0.8
1
0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
Hamming error
SCK
RMK
(b) Simulation 7(a)
0
0.2
0.4
0.6
0.8
1
0
0.2
0.4
0.6
0.8
1
NMI
SCK
RMK
(c) Simulation 7(a)
0
0.2
0.4
0.6
0.8
1
0
0.2
0.4
0.6
0.8
1
ARI
SCK
RMK
(d) Simulation 7(a)
0
0.2
0.4
0.6
0.8
1
0
0.5
1
1.5
2
2.5
3
SCK
RMK
(e) Simulation 7(a)
0
0.2
0.4
0.6
0.8
1
0
0.5
1
1.5
2
2.5
3
SCK
RMK
(f) Simulation 7(a)
0
0.2
0.4
0.6
0.8
1
0
0.1
0.2
0.3
0.4
0.5
Running time /s
SCK
RMK
(g) Simulation 7(a)
1000
2000
3000
4000
5000
N
0
0.2
0.4
0.6
0.8
Clustering error
SCK
RMK
(h) Simulation 7(b)
1000
2000
3000
4000
5000
N
0
0.05
0.1
0.15
0.2
0.25
0.3
0.35
Hamming error
SCK
RMK
(i) Simulation 7(b)
1000
2000
3000
4000
5000
N
0.2
0.4
0.6
0.8
1
NMI
SCK
RMK
(j) Simulation 7(b)
1000
2000
3000
4000
5000
N
0.2
0.4
0.6
0.8
1
ARI
SCK
RMK
(k) Simulation 7(b)
1000
2000
3000
4000
5000
N
0.2
0.3
0.4
0.5
0.6
0.7
0.8
SCK
RMK
(l) Simulation 7(b)
1000
2000
3000
4000
5000
N
0.2
0.3
0.4
0.5
0.6
0.7
0.8
SCK
RMK
(m) Simulation 7(b)
1000
2000
3000
4000
5000
N
0
5
10
15
20
Running time /s
SCK
RMK
(n) Simulation 7(b)
Figure 7: Numerical results of Simulation 7.
18
### Page 19

(a) Normal distribution
(b) Poisson distribution
Figure 8: Illustration for weighted response matrices R generated from WLCM. In both panels, Si denote subject i and Ij denotes item j for
i ∈[16], j ∈[10].
5.3.8. Simulated weighted response matrices
For visuality, we plot two weighted response matrices R generated from the Normal distribution and the Poisson
distribution under WLCM. Let K = 2, N = 16, J = 10, σ2 = 1, ℓ(i) = 1, ℓ(i + 8) = 2 for i ∈[8], and Θ(j, 1) =
100, Θ(j, 2) = 110 −10 j for j ∈[10]. Because R0 = ZΘ′ has been set, we can generate R under diﬀerent distributions
with expectation R0 under the proposed WLCM model. Here, we consider the following two settings.
Simulation 8 (a): When R(i, j) ∼Normal(R0(i, j), σ2) for i ∈[N], j ∈[J], the left panel of Figure 8 displays a
weighted response matrix R generated from Simulation 8 (a).
Simulation 8 (b): When R(i, j) ∼Poisson(R0(i, j)) for i ∈[N], j ∈[J], the right panel of Figure 8 provides a R
generated from Simulation 8 (b).
Table 1: Error rates of SCK and RMK for R in Figure 8. Values outside (and inside) the brackets are results for R in panel (a) (and (b)) of Figure 8.
Clustering error
Hamming error
NMI
ARI
Relative l1 error
Relative l2 error
SCK
0 (0)
0 (0)
1 (1)
1 (1)
0.0024 (0.0254)
0.0032 (0.0295)
RMK
0 (0)
0 (0)
1 (1)
1 (1)
0.0024 (0.0245)
0.0032 (0.0295)
Error rates of the proposed methods for the observed weighted response matrices provided in Figure 8 are dis-
played in Table 1. We also plot the estimated item matrix ˆΘ for both methods in Figure 9. We see that both approaches
exactly recover Z from R while they estimate Θ with slight perturbations. Meanwhile, since Z, Θ, and K are known
for this simulation, R provided in Figure 8 can be regarded as benchmark weighted response matrices, and readers can
apply SCK and RMK (and other methods) to R to check their eﬀectiveness in estimating Z and Θ.
6. Real data applications
As the main goal of this paper is to introduce the proposed WLCM model and the SCK algorithm for weighted
response matrices, this section reports empirical results on two data sets with weighted response matrices. Because
the true classiﬁcation matrix and the true item parameter matrix are unknown for real data, and SCK runs much faster
than RMK, we only report the outcomes of the SCK approach. For real-world datasets, the number of extreme latent
proﬁles K is often unknown. Here, we infer K for real-world weighted response matrices using the following strategy:
K = arg mink∈[rank(R)]∥R −ˆZ ˆΘ′∥,
(8)
where ˆZ and ˆΘ are outputs in Algorithm 2 with inputs R and k. The method speciﬁed in Equation (8) selects K by
picking the one that minimizes the spectral norm diﬀerence between R and ˆZ ˆΘ′. The determination of the number
19
### Page 20

profile 1 profile 2
Item 1
Item 2
Item 3
Item 4
Item 5
Item 6
Item 7
Item 8
Item 9
Item 10
Normal distribution: SCK
100.1
100.3
99.85
100.4
99.84
99.68
100.4
99.98
99.97
100.1
100.3
89.67
79.77
69.52
60.07
50.38
39.96
29.97
19.97
10.48
20
40
60
80
100
profile 1 profile 2
Item 1
Item 2
Item 3
Item 4
Item 5
Item 6
Item 7
Item 8
Item 9
Item 10
Normal distribution: RMK
100.1
100.3
99.86
100.4
99.84
99.68
100.4
99.98
99.97
100.1
100.3
89.68
79.76
69.53
60.07
50.38
39.96
29.97
19.97
10.48
20
40
60
80
100
profile 1 profile 2
Item 1
Item 2
Item 3
Item 4
Item 5
Item 6
Item 7
Item 8
Item 9
Item 10
Poisson distribution: SCK
104.4
104
100.3
96.88
101.2
96.35
100.3
100
104.2
95.83
102
87.89
81.18
69.93
57.33
51.79
41.06
29.01
18.35
10.87
20
40
60
80
100
profile 1 profile 2
Item 1
Item 2
Item 3
Item 4
Item 5
Item 6
Item 7
Item 8
Item 9
Item 10
Poisson distribution: RMK
104.5
103.9
100.2
97.25
100.8
96.62
100
100
104.6
95.62
102
88.12
81.25
69.12
58
51.25
41.62
29.12
17.75
11.12
20
40
60
80
100
Figure 9: Heatmap of the estimated item parameter matrix ˆΘ of SCK and RMK for R in Figure 8.
20
### Page 21

of extreme latent proﬁles K in our WLCM model in a rigorous manner with theoretical guarantees remains a future
direction.
6.1. International Personality Item Pool (IPIP) personality test data
Background. We apply SCK to an experiment personality test data called the International Personality Item Pool
(IPIP) personality test, which is obtainable for download at https://openpsychometrics.org/_rawdata/. This
data consists of 1005 subjects and 40 items. The IPIP data also records the age and gender of each subject. After drop-
ping subjects with missing entries in their responses, age, or gender, and dropping two subjects that are neither male
nor female, there are 896 subjects left, i.e., N = 896, J = 40. All items are rated on a 5-point scale, where 1=Strongly
disagree, 2=Disagree, 3=Neither agree not disagree, 4=Agree, 5=Strongly agree, i.e., R ∈{1, 2, 3, 4, 5}896×40, a
weighted response matrix. Items 1-10 measure the personality factor Assertiveness (short as “AS”); Items 11-20
measure the personality factor Social conﬁdence (short as “SC”); Items 21-30 measure the personality factor Adven-
turousness (short as “AD”); Items 31-40 measure the personality factor Dominance (short as “DO”). The details of
each item are depicted in Figure 10.
Analysis. We apply Equation (8) to infer K for the IPIP dataset and ﬁnd that the estimated value of K is 3. We
then apply the SCK algorithm to the response matrix R with K = 3 to obtain the 896 × 3 matrix ˆZ and the 40 × 3
matrix ˆΘ. The running time for SCK on this dataset is around 0.2 seconds.
Table 2: Basic information for each estimated extreme latent proﬁle obtained from ˆZ for the IPIP data.
proﬁle 1
proﬁle 2
proﬁle 3
Size
276
226
394
#Male
123
129
241
#Female
153
97
153
Average age of male
35.9837
32.8240
35.9004
Average age of female
35.5425
31.3814
38.7059
Results. For convenience, we denote the estimated three extreme latent proﬁles as proﬁle 1, proﬁle 2, and proﬁle
3. Based on ˆZ and the information of age and gender, we can obtain some basic information (shown in Table 2) such as
the size of each proﬁle, number of males (females) in each proﬁle, and the average age of males (and females) in each
proﬁle. From Table 2, we see that the number of females is larger than that of males for proﬁle 1 while proﬁles 2 and
3 have more males. The average age of males (and females) in proﬁle 2 is smaller than that of proﬁles 1 and 3 while
the average age of females in proﬁle 3 is the largest. We can also obtain the average point on each item for males (and
females) in each estimated extreme latent proﬁle and the results are shown in panel (a) (and panel (b)) of Figure 10.
We observe that males in proﬁle 3 tend to be more conﬁdent, more creative, more social, and more open to changes
than males in proﬁles 1 and 2; males in proﬁle 3 are more (less) dominant than males in proﬁle 1 (proﬁle 2). Males in
proﬁle 2 are more conﬁdent&creative&social&open to changes&dominant than males in proﬁle 1. Meanwhile, in the
three estimated extreme latent proﬁles, females enjoy similar personalities to males. We also ﬁnd that males in proﬁle
3 (proﬁle 2) are more (less) conﬁdent&creative&social&open to changes&dominant than females in proﬁle 3 (proﬁle
2). Furthermore, it is interesting to see that, though males in proﬁle 1 are less conﬁdent&creative&social&open to
changes than females in proﬁle 1, they are more dominant than females in proﬁle 1. We also plot the average point on
each item in each estimated extreme latent proﬁle regardless of gender in panel (c) of Figure 10 where we can draw
similar conclusions as that for male. In panel (d) of Figure 10, we plot the heatmap of the estimated item parameter
matrix ˆΘ. By comparing panel (c) with panel (d), we see that the (j, k)-th element in the matrix shown in panel (c) is
close to ˆΘ(j, k) for j ∈[40], k ∈[3]. Such a result implies that the behavior diﬀerences on each item for every extreme
latent proﬁle are governed by the item parameter matrix Θ.
Remark 5. Recall that E(R) = R0 = ZΘ′ under the WLCM model, we have R0(i, j) = Θ(j, ℓ(i)) for i ∈[N], j ∈[J].
Then we have P
ℓ(i)≡k R0(i, j) = P
ℓ(i)≡k Θ(j, ℓ(i)) = P
ℓ(i)≡k Θ(j, k) = NkΘ(j, k) which gives that Θ(j, k) =
P
ℓ(i)≡k R0(i, j)
Nk
for k ∈[K]. This interprets why the average value on the j-th item in the k-th estimated extreme latent proﬁle
approximates ˆΘ(j, k) for j ∈[J], k ∈[K].
21
### Page 22

profile 1
profile 2
profile 3
AS1: Express myself easily
AS2: Try to lead others
AS3: Automatically take charge
AS4: Know how to convince others
AS5: Am the first to act
AS6: Take control of things
AS7: Wait for others to lead the way
AS8: Let others make the decisions
AS9: Am not highly motivated to succeed
AS10: Can not come up with new ideas
SC1: Feel comfortable around people
SC2: Do not mind being the center of attention
SC3: Am good at making impromptu speeches
SC4: Express myself easily
SC5: Have a natural talent for influencing people
SC6: Hate being the center of attention
SC7: Lack the talent for influencing people
SC8: Often feel uncomfortable around others
SC9: Do not like to draw attention to myself
SC10: Have little to say
AD1: Prefer variety to routine
AD2: Like to visit new places
AD3: Interested in many things
AD4: Like to begin new things
AD5: Prefer to stick with things that I know
AD6: Dislike changes
AD7: Do not like the idea of change
AD8: Am a creature of habit
AD9: Dislike new foods
AD10: Am attached to conventional ways
DO1: Try to surpass others accomplishments
DO2: Try to outdo others
DO3: Am quick to correct others
DO4: Impose my will on others
DO5: Demand explanations from others
DO6: Want to control the conversation
DO7: Am not afraid of providing criticism
DO8: Challenge others points of view
DO9: Lay down the law to others
DO10: Put people under pressure
Male
3.195
3.252
3.293
3.187
3.244
3.203
3.423
3.74
3.317
4.081
4.325
3.927
3.13
3.22
3.114
3.171
3.217
3.798
3.512
3.519
3.357
3.752
3.085
3.093
3.186
3.233
3.364
3.364
3.868
4.302
3.953
3.38
3.953
3.946
4.078
3.488
3.984
3.271
3.868
4.163
3.186
3.24
4.365
4.129
3.855
4.154
3.813
3.942
4.307
4.091
3.896
4.249
4.017
3.963
4.473
4.631
4.39
3.751
3.651
3.432
3.427
3.178
3.867
4.004
2.837
2.561
2.732
2.992
2.545
2.073
2.61
2.707
2.878
2.74
2.821
2.886
2.683
2.537
2.179
2.772
2.911
2.74
2.764
1.951
2.496
2.228
2.057
1.748
2.798
2.783
1.969
1.829
2.868
2.752
2.705
2.62
2.364
3.008
2.682
2.349
2.186
2.496
2.191
2.432
1.564
1.481
1.892
1.751
1.801
2.336
1.705
2.419
1.913
1.755
2.701
1.689
2.017
2.905
2.763
2.647
1.5
2
2.5
3
3.5
4
4.5
(a) Average point on each item for male in each estimated extreme
latent proﬁle
profile 1
profile 2
profile 3
AS1: Express myself easily
AS2: Try to lead others
AS3: Automatically take charge
AS4: Know how to convince others
AS5: Am the first to act
AS6: Take control of things
AS7: Wait for others to lead the way
AS8: Let others make the decisions
AS9: Am not highly motivated to succeed
AS10: Can not come up with new ideas
SC1: Feel comfortable around people
SC2: Do not mind being the center of attention
SC3: Am good at making impromptu speeches
SC4: Express myself easily
SC5: Have a natural talent for influencing people
SC6: Hate being the center of attention
SC7: Lack the talent for influencing people
SC8: Often feel uncomfortable around others
SC9: Do not like to draw attention to myself
SC10: Have little to say
AD1: Prefer variety to routine
AD2: Like to visit new places
AD3: Interested in many things
AD4: Like to begin new things
AD5: Prefer to stick with things that I know
AD6: Dislike changes
AD7: Do not like the idea of change
AD8: Am a creature of habit
AD9: Dislike new foods
AD10: Am attached to conventional ways
DO1: Try to surpass others accomplishments
DO2: Try to outdo others
DO3: Am quick to correct others
DO4: Impose my will on others
DO5: Demand explanations from others
DO6: Want to control the conversation
DO7: Am not afraid of providing criticism
DO8: Challenge others points of view
DO9: Lay down the law to others
DO10: Put people under pressure
Female
3.471
3.163
3.458
3.288
3.725
3.412
3.314
3.516
3.438
4.307
4.222
3.915
3.209
3.176
3.402
3.794
3.691
3.577
3.66
3.938
3.227
3.216
3.165
3.247
3.206
3.907
4.124
3.701
3.268
3.278
3.68
3.588
3.763
3.33
3.773
3.381
3.804
3.959
3.186
4.353
4.065
3.817
4.072
3.732
3.922
4.333
3.928
3.712
4.275
3.797
4.013
4.641
4.621
4.425
3.588
3.386
3.242
3.307
3.575
3.784
2.967
2.667
2.902
3.007
2.386
2.15
2.654
2.431
2.941
2.634
2.562
2.51
2.608
2.373
2.033
2.699
2.706
2.536
2.621
2.013
2.503
2.033
2.725
3.013
1.948
1.712
2.505
2.619
1.948
1.773
3.031
2.722
2.392
2.485
2.948
2.557
2.814
2.619
2.536
2.773
3.113
2.281
2.503
1.667
1.601
2.052
1.843
1.85
2.248
1.627
2.399
2.105
1.856
2.529
1.66
2.118
2.791
2.856
2.654
2.51
2
2.5
3
3.5
4
4.5
(b) Average point on each item for female in each estimated ex-
treme latent proﬁle
profile 1
profile 2
profile 3
AS1: Express myself easily
AS2: Try to lead others
AS3: Automatically take charge
AS4: Know how to convince others
AS5: Am the first to act
AS6: Take control of things
AS7: Wait for others to lead the way
AS8: Let others make the decisions
AS9: Am not highly motivated to succeed
AS10: Can not come up with new ideas
SC1: Feel comfortable around people
SC2: Do not mind being the center of attention
SC3: Am good at making impromptu speeches
SC4: Express myself easily
SC5: Have a natural talent for influencing people
SC6: Hate being the center of attention
SC7: Lack the talent for influencing people
SC8: Often feel uncomfortable around others
SC9: Do not like to draw attention to myself
SC10: Have little to say
AD1: Prefer variety to routine
AD2: Like to visit new places
AD3: Interested in many things
AD4: Like to begin new things
AD5: Prefer to stick with things that I know
AD6: Dislike changes
AD7: Do not like the idea of change
AD8: Am a creature of habit
AD9: Dislike new foods
AD10: Am attached to conventional ways
DO1: Try to surpass others accomplishments
DO2: Try to outdo others
DO3: Am quick to correct others
DO4: Impose my will on others
DO5: Demand explanations from others
DO6: Want to control the conversation
DO7: Am not afraid of providing criticism
DO8: Challenge others points of view
DO9: Lay down the law to others
DO10: Put people under pressure
3.348
3.203
3.384
3.243
3.511
3.319
3.362
3.616
3.384
4.207
4.268
3.92
3.174
3.196
3.083
3.296
3.796
3.588
3.544
3.487
3.832
3.146
3.146
3.177
3.111
3.314
3.296
3.885
4.226
3.845
3.119
3.336
3.836
3.792
3.942
3.42
3.894
3.319
3.841
4.075
3.186
3.186
4.36
4.104
3.84
4.122
3.782
3.934
4.317
4.028
3.825
4.259
3.931
3.982
4.538
4.627
4.404
3.688
3.548
3.358
3.381
3.754
3.919
2.909
2.62
2.826
3
2.457
2.116
2.634
2.554
2.913
2.681
2.678
2.678
2.641
2.446
2.098
2.732
2.797
2.627
2.685
1.986
2.5
2.12
2.899
1.996
1.728
2.673
2.712
1.96
1.805
2.938
2.739
2.571
2.562
2.447
2.739
2.465
2.336
2.615
2.226
2.459
1.604
1.528
1.954
1.787
1.82
2.302
1.675
2.411
1.987
1.794
2.635
1.678
2.056
2.86
3.053
2.721
2.594
2
2.5
3
3.5
4
4.5
(c) Average point on each item in each estimated extreme latent
proﬁle
profile 1
profile 2
profile 3
AS1: Express myself easily
AS2: Try to lead others
AS3: Automatically take charge
AS4: Know how to convince others
AS5: Am the first to act
AS6: Take control of things
AS7: Wait for others to lead the way
AS8: Let others make the decisions
AS9: Am not highly motivated to succeed
AS10: Can not come up with new ideas
SC1: Feel comfortable around people
SC2: Do not mind being the center of attention
SC3: Am good at making impromptu speeches
SC4: Express myself easily
SC5: Have a natural talent for influencing people
SC6: Hate being the center of attention
SC7: Lack the talent for influencing people
SC8: Often feel uncomfortable around others
SC9: Do not like to draw attention to myself
SC10: Have little to say
AD1: Prefer variety to routine
AD2: Like to visit new places
AD3: Interested in many things
AD4: Like to begin new things
AD5: Prefer to stick with things that I know
AD6: Dislike changes
AD7: Do not like the idea of change
AD8: Am a creature of habit
AD9: Dislike new foods
AD10: Am attached to conventional ways
DO1: Try to surpass others accomplishments
DO2: Try to outdo others
DO3: Am quick to correct others
DO4: Impose my will on others
DO5: Demand explanations from others
DO6: Want to control the conversation
DO7: Am not afraid of providing criticism
DO8: Challenge others points of view
DO9: Lay down the law to others
DO10: Put people under pressure
3.32
3.208
3.342
3.279
3.474
3.3
3.311
3.577
3.382
4.178
4.279
3.91
3.163
3.213
3.11
3.346
3.7
3.549
3.527
3.419
3.76
3.21
3.114
3.154
3.094
3.329
3.255
3.901
4.233
3.836
3.131
3.346
3.858
3.831
3.957
3.409
3.966
3.32
3.856
4.02
3.266
3.19
4.361
4.136
3.848
4.131
3.794
3.948
4.313
4.016
3.814
4.25
3.936
4
4.532
4.598
4.399
3.672
3.547
3.351
3.339
3.752
3.926
2.936
2.637
2.851
3.024
2.473
2.12
2.64
2.569
2.942
2.662
2.704
2.688
2.681
2.491
2.142
2.747
2.795
2.608
2.675
1.948
2.496
2.157
2.881
1.942
1.718
2.694
2.715
1.926
1.83
2.983
2.752
2.604
2.591
2.448
2.738
2.442
2.272
2.633
2.245
2.44
1.627
1.525
1.982
1.765
1.789
2.309
1.652
2.425
1.98
1.798
2.641
1.699
2.061
2.9
3.04
2.719
2.602
2
2.5
3
3.5
4
4.5
(d) Heatmap of ˆΘ
Figure 10: Numerical results for the IPIP data.
22
### Page 23

6.2. Big Five Personality Test with Random Number (BFPTRN) data
Background. Our SCK method is also applied to personality test data: the Big Five Personality Test with Random
Number (BFPTRN) data. This dataset can be downloaded from the same URL as the IPIP data. This data asks
respondents to generate random numbers in certain ranges attached to 50 personality items. The Big Five personality
traits are extraversion (items E1-E10), neuroticism (items N1-N10), agreeableness (items A1-A10), conscientiousness
(items C1-C10), and openness (items O1-O10). The original BFPTRN data contains 1369 subjects. After excluding
subjects with missing responses or missing random numbers and removing those with random numbers exceeding the
speciﬁed range, there remain 1155 subjects, i.e., N = 1155, J = 50. All items are rated using the same 5-point scale
as the IPIP data, which results in R ∈{1, 2, 3, 4, 5}1155×50 being weighted. The detail of each item and each range for
random numbers can be found in Figure 11.
Analysis. The estimated number of extreme latent proﬁles for the BFPTRN dataset is 3. Applying the SCK
approach to R with K = 3 produces the 1155 × 3 matrix ˆZ and the 50 × 3 matrix ˆΘ. SCK takes around 1.6 seconds to
process this data.
Results. Without confusion, we also let proﬁle 1, proﬁle 2, and proﬁle 3 represent the three estimated extreme
latent proﬁles. Proﬁle 1,2, and 3 have 409, 320, and 426 subjects, respectively. Similar to the IPIP data, based on
ˆZ and ˆΘ, we can also obtain the heatmap of the average point on each subject for every proﬁle, the heatmap of the
average random number on each range for every proﬁle, and the heatmap of ˆΘ as shown in Figure 11. We observe
that there is no signiﬁcant connection between the average point and the average random number on each item in each
estimated extreme latent proﬁle. From panel (a) of Figure 11, we ﬁnd that: for extraversion, subjects in proﬁle 1 are
the most extrovertive while subjects in proﬁle 2 are the most introverted; for neuroticism, subjects in proﬁle 3 are
emotionally stable while subjects in proﬁles 1 and 2 are emotionally unstable; for agreeableness, subjects in proﬁles
1 and 3 are easier to get along with than subjects in proﬁle 2; for conscientiousness, subjects in proﬁle 3 are more
responsible that those in proﬁles 1 and 2; for openness, subjects in proﬁles 1 and 3 are more open than those in proﬁle
2. Meanwhile, the matrix shown in panel (a) approximates ˆΘ well, which has been explained in Remark 5.
7. Conclusion and future work
In this paper, we introduced the weighted latent class model (WLCM), a novel class of latent class analysis mod-
els for categorical data with weighted responses. We studied its model identiﬁability, developed an eﬃcient inference
method SCK to ﬁt WLCM, and built a theoretical guarantee of estimation consistency for the proposed method under
WLCM. On the methodology side, the new model WLCM provides exploratory and useful tools for latent class anal-
ysis in applications where the categorical data may have weighted responses. WLCM allows the observed weighted
response matrix to be generated from any distribution as long as its expectation follows a latent class structure modeled
by WLCM. In particular, the popular latent class model is a sub-model of our WLCM, and categorical data with signed
responses can also be modeled by WLCM. Ground-truth latent classes of categorical data with weighted responses
generated from WLCM serve as benchmarks for evaluating latent class analysis approaches. On the algorithmic side,
the SVD-based spectral method SCK is eﬃcient and easy to implement. SCK requires no tuning parameters and
it is applicable for any categorical data with weighted responses. This means that researchers in ﬁelds such as so-
cial, psychological, behavioral, biological sciences, and beyond can design their tests/evaluations/surveys/interviews
without worrying that the response should be binary or positive, as our method SCK is applicable for any weighted
response matrices in latent class analysis. On the theoretic side, we established the rate of convergence for our method
SCK under the proposed model WLCM. We found that SCK exhibits diﬀerent behaviors when the weighted response
matrices are generated from diﬀerent distributions, and we conducted extensive experiments to verify our theoretical
ﬁndings. Empirically, we applied our method to two real categorical datasets with weighted responses. We expect
that our WLCM model and SCK method will have broad applications for latent class analysis of data with weighted
responses in diverse ﬁelds, similar to the widespread use of latent class models in recent years.
There are several future directions worth exploring. First, methods with theoretical guarantees should be designed
to determine the number of extreme latent proﬁles K for observed weighted response matrices generated from any
distribution F under WLCM. Second, the grade of membership (GoM) model [44, 45] provides a richer modeling ca-
pacity than the latent class model since GoM allows a subject to belong to multiple extreme latent proﬁles. Therefore,
following the distribution-free idea developed in this work, it is meaningful to extend the model GoM to categorical
23
### Page 24

profile 1
profile 2
profile 3
E1: I am the life of the party
E2: I do not talk a lot
E3: I feel comfortable around people
E4: I keep in the background
E5: I start conversations
E6: I have little to say
E7: I talk to a lot of different people at parties
E8: I do not like to draw attention to myself
E9: I do not mind being the center of attention
E10: I am quiet around strangers
N1: I get stressed out easily
N2: I am relaxed most of the time
N3: I worry about things
N4: I seldom feel blue
N5: I am easily disturbed
N6: I get upset easily
N7: I change my mood a lot
N8: I have frequent mood swings
N9: I get irritated easily
N10: I often feel blue
A1: I feel little concern for others
A2: I am interested in people
A3: I insult people
A4: I sympathize with others feelings
A5: I am not interested in other peoples problems
A6: I have a soft heart
A7: I am not really interested in others
A8: I take time out for others
A9: I feel others emotions
A10: I make people feel at ease
C1: I am always prepared
C2: I leave my belongings around
C3: I pay attention to details
C4: I make a mess of things
C5: I get chores done right away
C6: I often forget to put things back in their proper place
C7: I like order
C8: I shirk my duties
C9: I follow a schedule
C10: I am exacting in my work
O1: I have a rich vocabulary
O2: I have difficulty understanding abstract ideas
O3: I have a vivid imagination
O4: I am not interested in abstract ideas
O5: I have excellent ideas
O6: I do not have a good imagination
O7: I am quick to understand things
O8: I use difficult words
O9: I spend time reflecting on things
O10: I am full of ideas
Average points
3.249
3.751
3.939
3.572
3.704
3.215
3.631
3.122
4.088
3.271
3.396
3.753
3.325
3.543
4.313
4.176
3.902
3.863
4.161
3.817
3.609
3.773
3.227
3.553
3.333
3.467
3.76
4.276
3.988
4.042
3.342
4.09
4.142
3.615
3.948
3.075
4.052
4.439
3.685
4.115
3.195
3.317
3.455
3.157
3.582
3.232
3.458
3.674
3.547
3.448
3.509
3.15
3.228
3.908
3.751
3.148
3.54
3.629
4.005
3.5
3.765
3.195
4.15
3.662
4.025
3.894
3.3
3.309
3.222
3.047
3.759
3.266
3.284
4.338
4.284
3.987
4.162
4.078
4.069
3.969
4.312
3.388
4.081
3.775
3.994
3.878
4.069
4.081
4.334
3.181
4.162
4.209
1.995
2.655
1.875
2.878
2.433
3.012
2.156
2.516
1.961
1.778
3.01
2.181
2.814
2.797
2.2
2.039
1.738
1.901
2.484
2.413
1.786
2.134
2.812
2.465
2.563
2.347
2.641
2.749
2.852
2.852
2.617
2.878
2.641
2.444
2.291
2.178
2.95
2.434
2.797
1.972
2.475
2.275
2.05
2.253
1.759
2.266
1.831
1.834
1.653
1.931
1.797
2.388
1.8
2.094
1.756
1.772
1.844
1.706
2
2.5
3
3.5
4
(a) Average point on each item in each estimated extreme latent
proﬁle
profile 1
profile 2
profile 3
R2: What is a number between 1 and 1000?
R3: What is a number between 44 and 99?
R4: What is a number between 100 and 500?
R5: What is a number between 1 and 100?
R6: What is a number between 123 and 1234?
R7: What is a number between 1 and 100?
R8: What is a number between 7 and 50?
R9: What is a number between 1 and 100?
R10: What is a number between 60 and 140?
R11: What is a number between 80 and 90?
R12: What is a number between 1 and 100?
R13: What is a number between 5 and 8?
R14: What is a number between 600 and 800?
R15: What is a number between 1 and 100?
R16: What is a number between 600 and 800?
R17: What is a number between 1 and 4?
R18: What is a number between 1 and 100?
R19: What is a number between 77 and 4012?
R20: What is a number between 30 and 60?
Average random numbers
1756
1830
1885
47.83
480
63.16
283.5
47.11
609.6
51.11
31.25
49.44
89.96
84.14
51.43
6.479
693.4
46.81
695.2
2.746
52.95
43.76
45.29
448.5
63.78
281.2
47.06
553.4
50.35
29.69
49.55
91.73
84.31
46.31
10.01
704.5
47.08
694
2.732
47.39
45.27
154.9
507.9
62.67
283.1
49.12
629
49.62
30.57
52.04
92.45
84.39
46.26
6.744
700.2
51.23
714.8
2.641
65.59
47.98
200
400
600
800
1000
1200
1400
1600
1800
(b) Average random number on each range in each estimated ex-
treme latent proﬁle
profile 1
profile 2
profile 3
E1: I am the life of the party
E2: I do not talk a lot
E3: I feel comfortable around people
E4: I keep in the background
E5: I start conversations
E6: I have little to say
E7: I talk to a lot of different people at parties
E8: I do not like to draw attention to myself
E9: I do not mind being the center of attention
E10: I am quiet around strangers
N1: I get stressed out easily
N2: I am relaxed most of the time
N3: I worry about things
N4: I seldom feel blue
N5: I am easily disturbed
N6: I get upset easily
N7: I change my mood a lot
N8: I have frequent mood swings
N9: I get irritated easily
N10: I often feel blue
A1: I feel little concern for others
A2: I am interested in people
A3: I insult people
A4: I sympathize with others feelings
A5: I am not interested in other peoples problems
A6: I have a soft heart
A7: I am not really interested in others
A8: I take time out for others
A9: I feel others emotions
A10: I make people feel at ease
C1: I am always prepared
C2: I leave my belongings around
C3: I pay attention to details
C4: I make a mess of things
C5: I get chores done right away
C6: I often forget to put things back in their proper place
C7: I like order
C8: I shirk my duties
C9: I follow a schedule
C10: I am exacting in my work
O1: I have a rich vocabulary
O2: I have difficulty understanding abstract ideas
O3: I have a vivid imagination
O4: I am not interested in abstract ideas
O5: I have excellent ideas
O6: I do not have a good imagination
O7: I am quick to understand things
O8: I use difficult words
O9: I spend time reflecting on things
O10: I am full of ideas
3.234
3.759
3.933
3.556
3.635
3.157
3.645
4.116
3.325
3.436
3.725
3.32
3.55
4.343
4.217
3.965
3.926
4.189
3.824
3.592
3.789
3.208
3.536
3.349
3.415
3.762
4.309
3.945
4.027
3.326
4.092
4.137
3.59
4.012
4.027
4.484
3.716
4.108
3.16
3.323
3.497
3.183
3.566
3.264
3.46
3.675
3.544
3.407
3.508
3.156
3.249
3.937
3.763
3.153
3.599
3.627
3.984
3.518
3.788
3.206
4.171
3.682
4.003
3.845
3.274
3.275
3.243
3.792
3.274
3.314
4.277
4.239
3.938
4.156
4.074
4.075
4.023
4.282
3.389
4.081
3.781
4.014
3.881
4.061
4.126
4.327
3.215
4.154
4.201
2.003
2.658
1.845
2.923
3.055
2.439
3.033
2.123
2.463
1.945
1.766
2.971
2.205
2.807
2.816
2.178
2.002
1.756
1.849
2.462
2.441
3.053
1.816
2.163
2.801
2.383
2.537
2.341
2.592
2.722
2.829
2.853
2.619
2.831
2.619
2.412
2.232
2.119
3.019
2.426
2.712
2.019
3.05
2.469
2.27
2.043
2.269
1.769
2.301
1.782
1.873
1.703
1.935
1.789
2.397
1.791
2.129
1.731
1.804
1.92
1.703
2
2.5
3
3.5
4
(c) Heatmap of ˆΘ
Figure 11: Numerical results for the BFPTRN data.
24
### Page 25

data with weighted responses. Third, like the LCM can be equipped with individual covariates [46, 47, 48, 49, 50, 51],
it is worth considering additional individual covariates into the WLCM analysis. Fourth, our WLCM only considers
static latent class analysis and it is meaningful to extend WLCM to the dynamic case [52]. Fifth, our SCK is a spectral
clustering method and it is possible to speed up it by applications of the random-projection techniques [53] or the
distributed spectral clustering idea [54] to deal with large-scale categorical data for latent class analysis.
CRediT authorship contribution statement
Huan Qing is the sole author of this paper.
Declaration of competing interest
The author declares no competing interests.
Data availability
Data and code will be made available on request.
Appendix A. Proofs under WLCM
Appendix A.1. Proof of Proposition 1
Proof. According to Lemma 1, we know that U = ZX, where X = Θ′VΣ−1. Similarly, U can be rewritten as U = ˜Z ˜X,
where ˜X = ˜Θ′VΣ−1. Then, for i ∈[N], we have
U(i, :) = Z(i, :)X = X(ℓ(i), :) = ˜Z(i, :) ˜X = ˜X(˜ℓ(i), :),
(A.1)
where ˜ℓ(i) denotes the extreme latent proﬁle that the i-th subject belongs in the alternative classiﬁcation matrix ˜Z. For
¯i ∈[N] and ¯i , i, we have
U(¯i, :) = Z(¯i, :)X = X(ℓ(¯i), :) = ˜Z(¯i, :) ˜X = ˜X(˜ℓ(¯i), :).
(A.2)
When ℓ(i) = ℓ(¯i), by the second statement of Lemma 1, we get U(i, :) = U(¯i, :). Combining this fact (i.e., U(i, :) =
U(¯i, :)) with Equations (A.1) and (A.2) leads to
X(ℓ(i), :) = X(ℓ(¯i), :) = ˜X(˜ℓ(i), :) = ˜X(˜ℓ(¯i), :) when ℓ(i) = ℓ(¯i).
(A.3)
Equation (A.3) implies that ˜ℓ(i) = ˜ℓ(¯i) when ℓ(i) = ℓ(¯i), i.e., for any two distinct subjects i and ¯i, they are in the same
extreme latent proﬁle under ˜Z when they are in the same extreme latent proﬁle under Z. Therefore, we have ˜Z = ZP,
where P is a permutation matrix. Combining ˜Z = ZP with ZΘ′ = ˜Z ˜Θ′ leads to ZΘ′ = ˜Z ˜Θ′ = ZP ˜Θ′, which gives that
Z(Θ′ −P ˜Θ′) = 0.
(A.4)
Taking the transposition of Equation (A.4) gives
(Θ −˜ΘP′)Z′ = 0.
(A.5)
Right multiplying Z at both sides of Equation (A.6) gives
(Θ −˜ΘP′)Z′Z = 0.
(A.6)
Since each extreme latent proﬁle is not an empty set, the N × K classiﬁcation matrix Z has a rank K, which gives
that the K × K matrix Z′Z is nonsingular. Therefore, Right multiplying (Z′Z)−1 at both sides of Equation (A.6) gives
Θ = ˜ΘP′, i.e., ˜Θ = ΘP since P is a permutation matrix.
25
### Page 26

Appendix A.2. Proof of Lemma 1
Proof. For the ﬁrst statement: Since R0 = ZΘ′ = UΣV′, V′V = IK0×K0, and the K0 × K0 diagonal matrix Σ is
nonsingular, we have U = ZΘ′VΣ−1 ≡ZX, where X = Θ′VΣ−1. Hence, the ﬁrst statement holds.
For the second statement: For i ∈[N], U = ZX gives U(i, :) = Z(i, :)X = X(ℓ(i), :). Then, if ℓ(¯i) = ℓ(i), we have
U(¯i, :) = X(ℓ(¯i), :) = X(ℓ(i), :) = U(i, :), i.e., U has K distinct rows. Thus, the second statement holds.
For the third statement: Since R0 = ZΘ′ = UΣV′, we have ΘZ′ = VΣU′ ⇒ΘZ′Z = VΣU′Z ⇒Θ =
VΣU′Z(Z′Z)−1 where the K × K matrix Z′Z is nonsingular because each extreme latent proﬁle has at least one subject,
i.e., rank(Z′Z) = rank(Z) = K. Thus, the third statement holds.
For the fourth statement: Recall that when K0 = K, we have U ∈RN×K, V ∈RJ×K, Σ is a K × K full-rank diagonal
matrix, and X is a K × K matrix, where U′U = IK×K, V′V = IK×K. Let ∆= diag( √N1, √N2, . . ., √NK), then
R0 = ZΘ′ = Z∆−1∆Θ′.
(A.7)
It is straightforward to verify that Z∆−1 is a column orthogonal matrix, i.e., (Z∆−1)′Z∆−1 = IK×K.
Since K0 = K, we have rank(∆Θ′) = K. Let ˜U ˜Σ ˜V′ = ∆Θ′ be the compact SVD of ∆Θ′, where ˜Σ is a K × K
diagonal matrix, ˜U ∈RK×K, ˜V ∈RJ×K, ˜U′ ˜U = IK×K, and ˜V′ ˜V = IK×K. Note that ˜U ∈RK×K and ˜U′ ˜U = IK×K imply
rank( ˜U) = K. Equation (A.7) implies
R0 = ZΘ′ = UΣV′ = Z∆−1∆Θ′ = Z∆−1 ˜U ˜Σ ˜V′.
(A.8)
Note that U, V, Z∆−1 ˜U, and ˜V are all orthonormal matrices. Also note that Σ and ˜Σ are K × K diagonal matrices. Then
we have
U = Z∆−1 ˜U, Σ = ˜Σ, and V = ˜V.
(A.9)
Recall that U = ZX, Equation (A.9) gives that X = ∆−1 ˜U ∈RK×K and rank(X) = K because rank(∆) = K and
rank( ˜U) = K. We can easily verify that the rows of ∆−1 ˜U are perpendicular to each other and the k-th row has length
√1/Nk for k ∈[K], i.e.,
√
XX′ =
√
∆−1 ˜U ˜U′∆−1 =
√
∆−2 = ∆−1. Thus, the fourth statement holds.
Remark 6. In this remark, we provide the reason why the fourth statement does not hold when K0 < K. For this case,
the rank of ∆Θ′ is K0, thus ˜U ∈RK×K0 and rank( ˜U) = K0. Then we have X = ∆−1 ˜U ∈RK×K0 and rank(X) = K0. Thus,
rank(XX′) = K0 < K = rank(∆−2), which implies
√
XX′ , ∆−1 when K0 < K and the fourth statement does not hold.
Appendix A.3. Proof of Theorem 1
First, the following two lemmas are provided for our further proof.
Lemma 2. Under WLCM(Z, Θ, F ), we have
max(∥ˆU ˆO −U∥F, ∥ˆV ˆO −V∥F) ≤2
√
2K∥R −R0∥
ρσK(B) √Nmin
,
where ˆO is a K-by-K orthogonal matrix.
Proof. According to the proof of Lemma 3 in [55], there is a K × K orthogonal matrix ˆO such that
max(∥ˆU ˆO −U∥F, ∥ˆV ˆO −V∥F) ≤
√
2K∥ˆR −R0∥
pλK(R0R′
0)
.
Because ˆR is the top K SVD of R and rank(R0) = K, we have ∥R −ˆR∥≤∥R −R0∥. Then we have ∥ˆR −R0∥=
∥ˆR −R + R −R0∥≤2∥R −R0∥, which gives
max(∥ˆU ˆO −U∥F, ∥ˆV ˆO −V∥F) ≤2
√
2K∥R −R0∥
pλK(R0R′
0)
.
(A.10)
26
### Page 27

For λK(R0R′
0), because R0 = ZΘ′ = ρZB′ and λK(Z′Z) = Nmin, we have
λK(R0R′
0) = λK(ZΘ′ΘZ′) = λK(ρ2ZB′BZ′) = ρ2λK(B′BZ′Z)
≥ρ2λK(Z′Z)λK(B′B) = ρ2NminλK(B′B).
Combining Equation (A.10) with λK(R0R′
0) ≥ρ2NminλK(B′B) gives
max(∥ˆU ˆO −U∥F, ∥ˆV ˆO −V∥F) ≤2
√
2K∥R −R0∥
ρσK(B) √Nmin
.
Lemma 3. Under WLCM(Z, Θ, F ), if Assumption 1 is satisﬁed, then with probability at least 1 −o((N + J)−3),
∥R −R0∥≤C
p
γ max(N, J)log(N + J),
where C is a positive constant.
Proof. This lemma holds by setting α in Lemma 2 [56] as 3, where Lemma 2 of [56] is obtained from the rectangular
version of Bernstein inequality in [57].
Proof. Now, we prove the ﬁrst statement of Theorem 1. Set ς > 0 as a small value, by Lemma 2 of [36] and the fourth
statement of Lemma 1, if
√
K
ς ∥U −ˆU ˆO∥F(
1
√Nk
+
1
√Nl
) ≤
r
1
Nk
+ 1
Nl
, for each 1 ≤k , l ≤K,
(A.11)
then the Clustering error ˆf = O(ς2) using the K-means algorithm. By setting ς =
q
2KNmax
Nmin ∥U −ˆU ˆO∥F, we see that
Equation (A.11) always holds for all 1 ≤k , l ≤K. So we get ˆf = O(ς2) = O(
KNmax∥U−ˆU ˆO∥2
F
Nmin
). According to Lemma
2, we have
ˆf = O(K2Nmax∥R −R0∥2
ρ2σ2
K(B)N2
min
).
By Lemma 3, we have
ˆf = O(γK2Nmaxmax(N, J)log(N + J)
ρ2σ2
K(B)N2
min
).
Next, we prove the second statement of Theorem 1. Since U = ZX by Equation (3) in Lemma 1 and U′U = IK×K,
we have X′Z′ZX = IK×K which gives that (Z′Z)−1 = XX′ and λ1(XX′) = σ2
1(XX′) =
1
λK(Z′Z) =
1
Nmin . We also have
Z(Z′Z)−1 = ZXX′ = UX′. Similarly, we have ˆZ( ˆZ′ ˆZ)−1 ≈ˆU ˆX′, where ˆX is the K × K centroid matrix returned by
K-means method for ˆU. Recall that ˆR = ˆU ˆΣ ˆV′, combine it with Equation (4) and Lemma 3, we have
∥ˆΘ −ΘP∥= ∥ˆV ˆΣ ˆU′ ˆZ( ˆZ′ ˆZ)−1 −VΣU′Z(Z′Z)−1P∥= ∥ˆR′ ˆZ( ˆZ′ ˆZ)−1 −R′
0Z(Z′Z)−1P∥
= ∥( ˆR′ −R′
0) ˆZ( ˆZ′ ˆZ)−1 + R′
0( ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P)∥≤∥( ˆR′ −R′
0) ˆZ( ˆZ′ ˆZ)−1∥+ ∥R′
0( ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P)∥
≤∥ˆR −R0∥∥ˆZ( ˆZ′ ˆZ)−1∥+ ∥R0∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P∥≤2∥R −R0∥∥ˆZ( ˆZ′ ˆZ)−1∥+ ∥R0∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P∥
= 2∥R −R0∥∥ˆZ( ˆZ′ ˆZ)−1∥+ ∥ρZB′∥∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P∥≤2∥R −R0∥∥ˆZ( ˆZ′ ˆZ)−1∥+ ρ∥Z∥∥B∥∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P∥
= 2∥R −R0∥∥ˆZ( ˆZ′ ˆZ)−1∥+ ρσ1(B)
p
Nmax∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P∥
= 2∥R −R0∥∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P + Z(Z′Z)−1P∥+ ρσ1(B)
p
Nmax∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P∥
≤2∥R −R0∥(∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P∥+ ∥Z(Z′Z)−1P∥) + ρσ1(B)
p
Nmax∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P∥
27
### Page 28

≤2∥R −R0∥(∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P∥+ ∥Z(Z′Z)−1∥∥P∥) + ρσ1(B)
p
Nmax∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P∥
= 2∥R −R0∥(∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P∥+
1
√Nmin
) + ρσ1(B)
p
Nmax∥ˆZ( ˆZ′ ˆZ)−1 −Z(Z′Z)−1P∥
= O(∥R −R0∥(∥ˆU ˆX′ −UX′P∥+
1
√Nmin
)) ≤O(∥R −R0∥(∥ˆU ˆX′∥+ ∥UX′P∥+
1
√Nmin
))
≤O(∥R −R0∥(∥ˆU∥∥ˆX∥+ ∥U∥∥X∥∥P∥+
1
√Nmin
)) = O(∥R −R0∥(∥ˆX∥+ ∥X∥+
1
√Nmin
))
= O(∥R −R0∥
√Nmin
) = O(
r
γ max(N, J)log(N + J)
Nmin
)
Since ( ˆΘ −ΘP) is a J × K matrix and K ≪J in this paper, we have rank( ˆΘ −ΘP) = K. Since ∥M∥F ≤√rank(M)∥M∥
holds for any matrix M, we have ∥ˆΘ −ΘP∥F ≤
√
K∥ˆΘ −ΘP∥. Thus, we have
∥ˆΘ −ΘP∥F = O(
r
γK max(N, J)log(N + J)
Nmin
).
(A.12)
Combing Equation (A.12) with the fact that ∥Θ∥F ≥∥Θ∥= ∥ρB∥= ρ∥B∥= ρσ1(B) ≥ρσK(B) gives
∥ˆΘ −ΘP∥F
∥Θ∥F
≤∥ˆΘ −ΘP∥F
ρσK(B)
= O(
p
γKmax(N, J)log(N + J)
ρσK(B) √Nmin
).
Recall that the J-by-K matrix B satisﬁes maxj∈[J],k∈[K]|B(j, k)| = 1, we have σK(B) is at least of the order
√
J−
√
K −1
with high probability by applying the lower bound of the smallest singular value of a random rectangular matrix in
[58]. Since K ≪J in this paper, we have
ˆf = O(γK2Nmaxmax(N, J)log(N + J)
ρ2N2
minJ
) and ∥ˆΘ −ΘP∥F
∥Θ∥F
= O(
p
γKmax(N, J)log(N + J)
ρ √NminJ
).
References
[1] C. M. Dayton, G. B. Macready, Concomitant-variable latent-class models, Journal of the american statistical association 83 (401) (1988)
173–178.
[2] J. A. Hagenaars, A. L. McCutcheon, Applied latent class analysis, Cambridge University Press, 2002.
[3] J. Magidson, J. K. Vermunt, Latent class models, The Sage handbook of quantitative methodology for the social sciences (2004) 175–198.
[4] G. Guo, J. Zhang, D. Thalmann, N. Yorke-Smith, Etaf: An extended trust antecedents framework for trust prediction, in: 2014 IEEE/ACM
International Conference on Advances in Social Networks Analysis and Mining (ASONAM 2014), IEEE, 2014, pp. 540–547.
[5] F. M. Harper, J. A. Konstan, The movielens datasets: History and context, Acm transactions on interactive intelligent systems (tiis) 5 (4)
(2015) 1–19.
[6] G. J. Meyer, S. E. Finn, L. D. Eyde, G. G. Kay, K. L. Moreland, R. R. Dies, E. J. Eisman, T. W. Kubiszyn, G. M. Reed, Psychological testing
and psychological assessment: A review of evidence and issues., American psychologist 56 (2) (2001) 128.
[7] J. J. Silverman, M. Galanter, M. Jackson-Triche, D. G. Jacobs, J. W. Lomax, M. B. Riba, L. D. Tong, K. E. Watkins, L. J. Fochtmann,
R. S. Rhoads, et al., The american psychiatric association practice guidelines for the psychiatric evaluation of adults, American Journal of
Psychiatry 172 (8) (2015) 798–802.
[8] J. De La Torre, L. A. van der Ark, G. Rossi, Analysis of clinical data from a cognitive diagnosis modeling framework, Measurement and
Evaluation in Counseling and Development 51 (4) (2018) 281–296.
[9] Y. Chen, X. Li, S. Zhang, Joint maximum likelihood estimation for high-dimensional exploratory item factor analysis, Psychometrika 84
(2019) 124–146.
[10] Z. Shang, E. A. Erosheva, G. Xu, Partial-mastery cognitive diagnosis models, The Annals of Applied Statistics 15 (3) (2021) 1529–1555.
[11] K. T. Poole, Nonparametric unfolding of binary choice data, Political Analysis 8 (3) (2000) 211–237.
[12] J. Clinton, S. Jackman, D. Rivers, The statistical analysis of roll call data, American Political Science Review 98 (2) (2004) 355–370.
[13] R. Bakker, K. T. Poole, Bayesian metric multidimensional scaling, Political analysis 21 (1) (2013) 125–140.
[14] Y. Chen, Z. Ying, H. Zhang, Unfolding-model-based visualization: theory, method and applications, The Journal of Machine Learning
Research 22 (1) (2021) 548–598.
28
### Page 29

[15] J. Martinez-Moya, M. Feo-Valero, Do shippers’ characteristics inﬂuence port choice criteria? capturing heterogeneity by using latent class
models, Transport Policy 116 (2022) 96–105.
[16] A. K. Formann, T. Kohlmann, Latent class analysis in medical research, Statistical methods in medical research 5 (2) (1996) 179–211.
[17] A. Kongsted, A. M. Nielsen, Latent class analysis in health research, Journal of physiotherapy 63 (1) (2017) 55–58.
[18] Z. Wu, M. Deloria-Knoll, S. L. Zeger, Nested partially latent class models for dependent binary data; estimating disease etiology, Biostatistics
18 (2) (2017) 200–213.
[19] P. G. Van der Heijden, J. Dessens, U. Bockenholt, Estimating the concomitant-variable latent-class model with the em algorithm, Journal of
Educational and Behavioral Statistics 21 (3) (1996) 215–229.
[20] Z. Bakk, J. K. Vermunt, Robustness of stepwise latent class modeling with continuous distal outcomes, Structural equation modeling: a
multidisciplinary journal 23 (1) (2016) 20–31.
[21] H. Chen, L. Han, A. Lim, Beyond the em algorithm: constrained optimization methods for latent class model, Communications in Statistics-
Simulation and Computation 51 (9) (2022) 5222–5244.
[22] Y. Gu, G. Xu, A joint mle approach to large-scale structured latent attribute analysis, Journal of the American Statistical Association 118 (541)
(2023) 746–760.
[23] A. Anandkumar, R. Ge, D. Hsu, S. M. Kakade, M. Telgarsky, Tensor decompositions for learning latent variable models, Journal of machine
learning research 15 (2014) 2773–2832.
[24] Z. Zeng, Y. Gu, G. Xu, A tensor-em method for large-scale latent class analysis with binary responses, Psychometrika 88 (2) (2023) 580–612.
[25] A. K. Formann, Constrained latent class models: Theory and applications, British Journal of Mathematical and Statistical Psychology 38 (1)
(1985) 87–111.
[26] B. Lindsay, C. C. Clogg, J. Grego, Semiparametric estimation in the rasch model and related exponential response models, including a simple
latent class model for item analysis, Journal of the American Statistical Association 86 (413) (1991) 96–107.
[27] N. L. Zhang, Hierarchical latent class models for cluster analysis, The Journal of Machine Learning Research 5 (2004) 697–723.
[28] C.-C. Yang, Evaluating latent class analysis models in qualitative phenotype identiﬁcation, Computational statistics & data analysis 50 (4)
(2006) 1090–1104.
[29] G. Xu, Identiﬁability of restricted latent class models with binary responses, The Annals of Statistics 45 (2) (2017) 675 – 707.
[30] G. Xu, Z. Shang, Identifying latent structures in restricted latent class models, Journal of the American Statistical Association 113 (523)
(2018) 1284–1295.
[31] W. Ma, W. Guo, Cognitive diagnosis models for multiple strategies, British Journal of Mathematical and Statistical Psychology 72 (2) (2019)
370–392.
[32] Y. Gu, G. Xu, Partial identiﬁability of restricted latent class models, The Annals of Statistics 48 (4) (2020) 2082 – 2107.
[33] M. E. Newman, Analysis of weighted networks, Physical review E 70 (5) (2004) 056131.
[34] T. Derr, C. Johnson, Y. Chang, J. Tang, Balance in signed bipartite networks, in: Proceedings of the 28th ACM International Conference on
Information and Knowledge Management, 2019, pp. 1221–1230.
[35] K. Goldberg, T. Roeder, D. Gupta, C. Perkins, Eigentaste: A constant time collaborative ﬁltering algorithm, information retrieval 4 (2001)
133–151.
[36] A. Joseph, B. Yu, Impact of regularization on spectral clustering, Annals of Statistics 44 (4) (2016) 1765–1791.
[37] J. Jin, Fast community detection by SCORE, Annals of Statistics 43 (1) (2015) 57–89.
[38] A. Strehl, J. Ghosh, Cluster ensembles—a knowledge reuse framework for combining multiple partitions, Journal of machine learning re-
search 3 (Dec) (2002) 583–617.
[39] L. Danon, A. Diaz-Guilera, J. Duch, A. Arenas, Comparing community structure identiﬁcation, Journal of statistical mechanics: Theory and
experiment 2005 (09) (2005) P09008.
[40] J. P. Bagrow, Evaluating local community methods in networks, Journal of Statistical Mechanics: Theory and Experiment 2008 (05) (2008)
P05001.
[41] W. Luo, Z. Yan, C. Bu, D. Zhang, Community detection by fuzzy relations, IEEE Transactions on Emerging Topics in Computing 8 (2)
(2017) 478–492.
[42] L. Hubert, P. Arabie, Comparing partitions, Journal of classiﬁcation 2 (1985) 193–218.
[43] N. X. Vinh, J. Epps, J. Bailey, Information theoretic measures for clusterings comparison: is a correction for chance necessary?, in: Proceed-
ings of the 26th annual international conference on machine learning, 2009, pp. 1073–1080.
[44] M. A. Woodbury, J. Clive, A. Garson Jr, Mathematical typology: a grade of membership technique for obtaining disease deﬁnition, Computers
and biomedical research 11 (3) (1978) 277–298.
[45] E. A. Erosheva, Comparing latent structures of the grade of membership, rasch, and latent class models, Psychometrika 70 (4) (2005) 619–
628.
[46] G.-H. Huang, K. Bandeen-Roche, Building an identiﬁable latent class model with covariate eﬀects on underlying and measured variables,
Psychometrika 69 (1) (2004) 5–32.
[47] A. Forcina, Identiﬁability of extended latent class models with individual covariates, Computational Statistics & Data Analysis 52 (12) (2008)
5263–5268.
[48] B. A. Reboussin, E. H. Ip, M. Wolfson, Locally dependent latent class models with covariates: an application to under-age drinking in the
usa, Journal of the Royal Statistical Society Series A: Statistics in Society 171 (4) (2008) 877–897.
[49] J. K. Vermunt, Latent class modeling with covariates: Two improved three-step approaches, Political analysis 18 (4) (2010) 450–469.
[50] R. Di Mari, Z. Bakk, A. Punzo, A random-covariate approach for distal outcome prediction with latent class analysis, Structural Equation
Modeling: A Multidisciplinary Journal 27 (3) (2020) 351–368.
[51] Z. Bakk, R. Di Mari, J. Oser, J. Kuha, Two-stage multilevel latent class analysis with covariates in the presence of direct eﬀects, Structural
Equation Modeling: A Multidisciplinary Journal 29 (2) (2022) 267–277.
[52] T. Asparouhov, E. L. Hamaker, B. Muth´en, Dynamic latent class analysis, Structural Equation Modeling: A Multidisciplinary Journal 24 (2)
(2017) 257–269.
29
### Page 30

[53] H. Zhang, X. Guo, X. Chang, Randomized spectral clustering in large-scale stochastic block models, Journal of Computational and Graphical
Statistics 31 (3) (2022) 887–906.
[54] S. Wu, Z. Li, X. Zhu, A distributed community detection algorithm for large scale networks under stochastic block models, Computational
Statistics & Data Analysis (2023) 107794.
[55] Z. Zhou, A. A. Amini, Analysis of spectral clustering algorithms for community detection: the general bipartite setting, Journal of Machine
Learning Research 20 (47) (2019) 1–47.
[56] H. Qing, J. Wang, Community detection for weighted bipartite networks, Knowledge-Based Systems 274 (2023) 110643.
[57] J. A. Tropp, User-friendly tail bounds for sums of random matrices, Foundations of Computational Mathematics 12 (4) (2012) 389–434.
[58] M. Rudelson, R. Vershynin, Smallest singular value of a random rectangular matrix, Communications on Pure and Applied Mathematics: A
Journal Issued by the Courant Institute of Mathematical Sciences 62 (12) (2009) 1707–1739.
30