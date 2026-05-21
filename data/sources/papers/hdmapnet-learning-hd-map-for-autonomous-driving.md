# HDMapNet Learning HD Map for Autonomous Driving

**Source**: arxiv PDF, 11 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

TransWeather: Transformer-based Restoration of Images Degraded by Adverse
Weather Conditions
Jeya Maria Jose Valanarasu, Rajeev Yasarla, and Vishal M. Patel
Johns Hopkins University
{jvalana1,ryasarl1,vpatel36} @jhu.edu
Abstract
Removing adverse weather conditions like rain, fog, and
snow from images is an important problem in many appli-
cations. Most methods proposed in the literature have been
designed to deal with just removing one type of degrada-
tion. Recently, a CNN-based method using neural archi-
tecture search (All-in-One) was proposed to remove all the
weather conditions at once. However, it has a large num-
ber of parameters as it uses multiple encoders to cater to
each weather removal task and still has scope for improve-
ment in its performance. In this work, we focus on devel-
oping an efﬁcient solution for the all adverse weather re-
moval problem. To this end, we propose TransWeather, a
transformer-based end-to-end model with just a single en-
coder and a decoder that can restore an image degraded
by any weather condition. Speciﬁcally, we utilize a novel
transformer encoder using intra-patch transformer blocks
to enhance attention inside the patches to effectively re-
move smaller weather degradations. We also introduce a
transformer decoder with learnable weather type embed-
dings to adjust to the weather degradation at hand. Tran-
sWeather achieves signiﬁcant improvements across multi-
ple test datasets over both All-in-One network as well as
methods ﬁne-tuned for speciﬁc tasks. TransWeather is also
validated on real world test images and found to be more
effective than previous methods. Implementation code can
be found in the supplementary document. Code is available
at https://github.com/jeya-maria-jose/TransWeather.
1. Introduction
Weather conditions like rain, fog, and snow reduce the
visibility and corrupt the information captured by an image.
This drastically affects the performance of many computer
vision algorithms like detection, segmentation and depth es-
timation [3, 5, 41, 52, 59] which are important parts of au-
tonomous navigation and surveillance systems [28,34–36].
Hence, it is essential to remove adverse weather effects
(b) All-in-One Network
Weather 
Type 
Queries
(a) Task Specific Networks 
(c) TransWeather (Ours)
EFog
DFog
D
D
E
E
D
Rain
Snow
Snow
Rain
Fog
Fog
Snow
Rain
Fog
ERain
ESnow
DRain
DSnow
EFog
ERain
ESnow
Figure 1.
Weather Removal Frameworks - (a) Separate net-
works designed for each type of weather removal like rain, fog and
snow. (b) All-in-One Network [23] proposes a framework with
separate encoders for each task but a generic decoder. (c) Our pro-
posed method, Transweather, has a single encoder and a decoder
and learns weather type queries to solve all adverse weather re-
moval efﬁciently.
from images in order to make these vision systems more
reliable. Also, a clean image without any weather degrada-
tion is desired in photography. Early methods for weather
removal involve modelling priors for weather conditions
using empirical observations [13, 45, 46].
These priors
have to be modelled separately for each weather condi-
tion and a common prior modelled for all weather condi-
tions is not effective. Recently, Convolutional Neural Net-
works (CNNs) based solutions have been explored exten-
sively for deraining [11, 37, 53, 56, 61, 63, 69, 70, 76], de-
hazing [8,19,41,57,69,71,72], desnowing [29,44,73] and
raindrop removal [37, 40, 66]. Transformer-based methods
have also been explored for weather removal tasks achiev-
ing better performance than CNNs [38, 48, 74]. Most of
these methods just focus on one task at hand or ﬁne-tune
the model separately for each task. Although they achieve
excellent performance, these are not generic solutions for
all adverse weather removal problems as the networks have
to trained separately for each task. This makes it difﬁcult to
adopt them for real-time systems as there have to be mul-
tiple models making it computationally complex. Also, the
arXiv:2111.14813v2  [cs.CV]  17 Jun 2022
### Page 2

system would have to decide and switch between a series
of weather removal algorithms (Figure 1 (a)) making the
pipeline more complicated.
Recently, Li et al. [23] proposed an All-in-One bad
weather removal network which was the ﬁrst work to pro-
pose an algorithm that takes in an image degraded by any
weather condition as input and predicts the clean image.
All-in-One network was tested across 3 datasets of rain, fog,
and snow removal and achieved better or comparable per-
formance than the previous methods which were tuned indi-
vidually on separate datasets. All-in-One network is CNN-
based and uses multiple encoders. In particular, it uses sep-
arate encoders for the different weather degradation at hand
and uses neural architecture search to ﬁnd the best network
to address the problem (Figure 1 (b)). This network is still
computationally complex as there are multiple encoders. To
the best of our knowledge, no other methods apart from All-
in-One network [23] have been proposed for a generic ad-
verse weather removal in the literature. Although recent
methods like MPR-Net [67], U-former [55], Swin-IR [27]
have been proposed as generic restoration networks vali-
dated on multiple datasets, they are still ﬁne-tuned on the
individual datasets and do not use a single model for all the
weather removal tasks.
In this work, we propose a single encoder-single decoder
transformer network, called TransWeather, to tackle all ad-
verse weather removal problems at once. Instead of using
multiple encoders, we introduce weather type queries in the
transformer decoder to learn the task (Figure 1 (c)). Here,
the multi-head self attention mechanisms take in weather
type queries as input and match it with keys and values
taken from features extracted from the transformer encoder.
These weather type embeddings are learned along with the
network to understand and adjust to the weather degradation
type present in the image. The decoded features and the hi-
erarchical features obtained form the encoder are fused and
projected to the image space using a convolutional block.
Thus, TransWeather just has one encoder and one decoder
to learn the weather type as well as produce the clean image.
Transformers are good at extracting rich global information
when compared to CNNs [9]. However, we argue that when
the patches are large like in ViT [9], we fail to attend much
to the information within the patch. Weather degradations
like rain streak, rain drop and snow are usually small in size
and so multiple artifacts can occur within a single patch.
To this end, we propose a novel transformer encoder with
intra-patch transformer (Intra-PT) blocks. Intra-PT works
on sub-patches created from the original patches and ex-
cavates features and details of smaller patches. Intra-PT
thus focuses on attention inside the main patches to re-
move weather degradations effectively.
We use efﬁcient
self-attention mechanisms to calculate the attention be-
tween sub-patches to keep the computational complexity
low. From our experiments, we ﬁnd that introducing Intra-
PT blocks enhances the performance of transformer and
helps it adapt better to weather removal tasks. We train
our network on a similar conﬁguration as All-in-One and
obtain superior performance across multiple test datasets
for rain removal, snow removal, fog removal and even a
combination of these weather degradations. We also outper-
form the methods designed speciﬁcally for these individual
tasks which are ﬁnetuned on those datasets. We also show
that TransWeather is fast during inference. Finally, we also
test TransWeather on real-world weather degraded images,
achieving excellent performance compared to the previous
methods. TransWeather can act as an efﬁcient backbone in
the future for generic weather removal frameworks.
The key contributions of this work are as follows:
• We propose TransWeather - an efﬁcient solution for all
adverse weather removal problem with just a single en-
coder and a single decoder using transformers. We pro-
pose using weather type queries to efﬁciently handle the
All-in-One problem.
• We propose a novel transformer encoder using intra-patch
transformer (Intra-PT) blocks to cater to ﬁne detail feature
extraction for low-level vision tasks like weather removal.
• We achieve state-of-the-art performance on multiple
datasets. We also validate the effectiveness of the pro-
posed method on real-world images.
2. Related Works
Adverse weather removal problems like deraining [16,
21,25,51,61,65,76], dehazing [1,2,10,22,42,69], desnow-
ing [29,44,44,73] and rain drop removal [37,39,40,66] have
been extensively explored in the literature.
Rain Streak Removal: Yang et al. [61] used a recurrent
network to decompose rain layers to different layers of var-
ious streak types to remove the rain.
Zhang et al. [70]
proposed using a conditional GAN for image deraining.
Yasarla et al. [64] explored using Gaussian processes to per-
form transfer learning from synthetic rain data to real-world
rain data. Quan et al. [39] used a complementary cascaded
network to remove rain streaks and raindrops in a uniﬁed
framework. A more detailed survey of various rain removal
methods can be found in [62].
Fog Removal: Li et al. [18] proposed a CNN network con-
sidering both atmospheric light and transmission map to
perform dehazing. Ren et al. [43] proposed pre-processing
a hazy image to generate multiple inputs thus introduc-
ing color distortions to perform dehazing. Zhang and Pa-
tel [68] proposed a pyramid CNN network for image dehaz-
ing. Zhang et al. [72] proposed a hierarchial density aware
network for image dehazing.
Rain drop Removal: You et al. [66] proposed using tem-
poral information to perform video-based raindrop removal.
Qian et al. [37] used an attention GAN to remove raindrop
### Page 3

and also introduced a new dataset. Quan et al. [40] used a
dual attention mechanism to remove effects of raindrops.
Snow Removal: Desnow-Net [29] was one of the ﬁrst
CNN-based methods proposed to remove snow from an im-
age. Li et al. [20] proposed a stacked dense network for
snow removal. Chen et al. [6] proposed JSTASR in which a
size and transparency aware method was proposed to re-
move snow.
Recently, DDMSNet [72] proposed a deep
dense multiscale network using semantic and geometric pri-
ors for snow removal.
All-in-One Weather Removal: All-in-One Network [23]
was proposed to handle multiple weather degradations us-
ing a single network. All-in-One uses a generator with mul-
tiple task-speciﬁc encoders and a common decoder. It uses
a discriminator to classify the degradation type and only
backpropagates the loss to speciﬁc encoders. It also uses
neural architecture search to optimize the feature extraction
from the encoder.
Transformers in low-level vision:
Since the introduc-
tion of Vision Transformer (ViT) [9] for visual recogni-
tion, transformers have been widely adopted for various
computer vision tasks [12, 31, 49, 60, 75]. Especially for
low-level vision, Image processing transformer [4] shows
how pretraining a transformer on large-scale datasets can
help in obtaining a better performance for low-level ap-
plications. U-former [55] proposed a U-Net based trans-
former architecture for restoration problems. Swin-IR [27]
adopted Swin Transformer [30] for image restoration. Zhao
et al. [74] proposed a local-global transformer speciﬁcally
for image dehazing. A multi-branch network [48] for de-
raining was also proposed based on swin transformer. In
ETDNet [38], an efﬁcient transformer block to extract fea-
tures in a coarse to ﬁne way for image deraining was pro-
posed.
Unlike the above methods, we propose a transformer-
based single-encoder single-decoder network to solve all
adverse weather removal tasks using a single model in-
stance. Our Transformer encoder is also modiﬁed to cater
to low-level tasks with the introduction of intra-patch trans-
former block.
Our transformer decoder is trained with
weather type queries to learn the task and uses that infor-
mation to restore the clean image.
3. Proposed Method - TransWeather
In the literature, different weather phenomenons have
been modelled differently with regards to the underlying
physics involved. Rain drop [37] is modelled as
I = (1 −M) ⊙B + R,
(1)
where I is the degraded image, M is the mask, B is the back-
ground and R is the raindrop residual. Heavy rain with rain
streaks and fog effect [21] is modelled as
I = T ⊙(B +
n
X
i
Ri) + (1 −T) ⊙A,
(2)
where T is the transmission map produced by scattering ef-
fect, and A is the atmospheric light in the scene. According
to [29], snow is generally modeled as
I = M ⊙S + M ⊙(1 −z),
(3)
where z is a mask indicating snow and S corresponds to
snow ﬂakes. All-in-One method [23] generalizes the ad-
verse weather removal problem as
B = D(Ep(Ip)),
(4)
where E corresponds to the encoder and D corresponds to
the decoder. p represents the weather type present in the
image. Note that for each weather type a different encoder
is used. In this work, we follow a similar formulation of all
adverse weather removal as
B = T(Ip),
(5)
where T corresponds to TransWeather which consists of a
weather agnostic encoder and decoder network unlike All-
in-One Network. The weather type queries are learnt along
with the parameters of T() thus making the problem setup
more generic. We motivate this setup because a problem as
generic as weather removal cannot be addressed by merely
seeking for perfection on solving individual tasks. This for-
mulation not only makes the process computationally ef-
ﬁcient, but also helps in using complimentary information
between the tasks to further improve the performance. Fur-
thermore, it is also grounded with regards to how human vi-
sion works as our visual cortex can perform multiple tasks
without any difﬁculty. This view is widely agreed in neuro-
biology as the visual cortex does not have different modules
for different perception tasks [24,32].
3.1. Network Architecture
Given a degraded image I of size H × W × 3, we ﬁrst
divide it into patches. We then feed forward the patches
to a transformer encoder containing transformer blocks at
different stages. Across each stage, the resolution is re-
duced to make sure the transformer learns both coarse and
ﬁne information. We then use a transformer decoder block
that uses the encoded features as keys and values while us-
ing learnable weather type query embeddings as queries.
The extracted features are then passed through a convolu-
tional projection block to get the clean image of dimensions
H × W × 3. An overview of the network architecture of
TransWeather can be found in Figure 2. In the following
sections, we describe these components in detail.
3.1.1
Transformer Encoder
We generate a hierarchical feature representation of the in-
put image by extracting multi-level features in the trans-
former encoder.
The features are extracted at different
### Page 4

Patch Embeddings
Weather Type Queries
Transformer Decoder
xM
Clean Image
Adverse Weather
Image
Transformer
 Block
Transformer
 Block
Transformer
 Block
Transformer Encoder
Decoder
Transformer
 Block
Multi-Head
Attention
Norm
Norm
FFN Block
Transformer Block
Conv 
Projection
Patch  Embeddings
Intra Patch Transformer Block
Intra-PT 
Block 
Intra-PT 
Block 
Fog
Rain
Snow
Task Features
Hierarchical Features
From Transformer 
Encoder
Feed Forward Net Block
xN
Intra-PT 
Block 
Depth-wise 
Conv
MLP
 Transformer
 Block
Figure 2. Overview of the proposed TransWeather network. A degraded image is forwarded to transformer encoder to extract hierar-
chical features. The encoder has intra-patch transformer blocks to extract features from smaller sub-patches created from the main patch.
The transformer decoder has learnable weather type queries to obtain the task feature. Then, the hierarchical features from encoder as well
as the task feature from decoder are forwarded to a convolutional projection block to obtain the clean image.
stages in the encoder thus facilitating extraction of both
high-level and low-level features. Across each stage, we
perform overlapped patch merging [59]. Using this we com-
bine overlapping feature patches to get features of the same
size as that of non-overlapped patches before passing the
features to the next stage.
Transformer Block: In each transformer block, we use
multi-head self-attention layers and feed forward networks
to calculate the self-attention features. The computation can
be summarized as:
Ti(Ii) = FFN(MSA(Ii) + Ii),
(6)
where T() represents the transformer block, FFN() repre-
sents the feed forward network block, MSA() represents
multi head self-attention, I is the input and i represents the
stage in the encoder. Similar to the original self-attention
network, the heads of queries (Q), keys (K) and values (V)
have same dimensions and are calculated as:
Attn(Q, K, V) = softmax
 
QKT
√
d
!
V,
(7)
where d represents the dimensionality. Note that we have
multiple attention heads in each transformer block and that
number is a hyper-parameter which we vary across each
stage in the transformer encoder. More details regarding the
hyper-parameter settings can be found in the supplementary
document. We reduce the complexity of the original self-
attention from O(N 2) to O( N2
R ) by introducing a reduction
ratio R [54]. We reshape the keys into a dimension from a
dimension of (N, C) to a dimension of ( N
R , C.R). We then
use a linear layer to get the second dimension back to C
from C.R. Hence, the keys get a dimension of N
R × C thus
reducing the complexity while calculating the self attention.
The self-attention features are then passed to a FFN block.
The FFN block used here has a slight variation from ViT as
we introduce using depth-wise convolution to MLP inspired
from [26,58,59]. Using depth-wise convolution here helps
bring locality information and provide positional informa-
tion for transformers as shown in [59]. The computation in
the FFN block can be summarized as follows:
FFNi(Xi) = MLP(GELU(DWC(MLP(Xi)))) + Xi,
where X refers to self-attention features, DWC is depth-
wise convolution [7], GELU is Gaussian error linear units
[14], MLP is multi-layer perceptron, i indicates the stage.
Intra-Patch Transformer Block: The intra-patch trans-
former blocks are present in between each stage in the trans-
former encoder. These blocks take in the sub-patches cre-
ated from the original patches as the input.
These sub-
patches are ﬁxed in dimensions half of height and width
of the original patch. Intra-PT also utilizes a similar trans-
former block as explained above. We use a high R value to
make the computation very efﬁcient in the Intra-PT block.
Intra-PT block helps in extracting ﬁne details helpful in
removing smaller degradation as we operate on smaller
patches.
Note that the Intra-PT block creates patches at
the feature level except at the ﬁrst stage where it is done
at the image level. The output self-attention features from
the Intra-PT block are added to the self-attention features
from the main block across the same stage. The formula-
tion of feed forward process in our transformer encoder can
be summarized as follows:
Yi = MTi(Xi) + IntraPTi(P(Xi))
(8)
where I is input to the transformer across each stage, Y is
the output across each stage, MT() is the main transformer
block, IntraPT is the intra-patch transformer block, P()
corresponds to the process of creating sub-patches from the
input patches and i denotes the stage.
3.1.2
Transformer Decoder
In the original transformer decoder [50], an autoregressive
decoder is used to predict the output sequence one ele-
ment at a time.
Detection transformer (DETR) [3] uses
### Page 5

object queries to decode the box coordinates and class la-
bels to produce the ﬁnal predictions. Inspired from them,
we deﬁne weather type queries to decode the task, predict
a task feature vector and use it to restore the clean image.
These weather type queries are learnable embeddings which
are learnt along with the other parameters of our network.
These queries attend to the feature outputs from the trans-
former encoder. The transformer decoder here operates at a
single stage but has multiple blocks. We illustrate the trans-
former decoder block in Figure 3. These transformer blocks
are similar to encoder-decoder transformer blocks [50]. Un-
like self-attention transformer block where Q, K and V are
taken from the same input, here Q is weather type learnable
embedding while K and V are the features taken from the
last stage of the transformer encoder. The output decoded
features represent the task feature vector and are fused with
the features extracted across the transformer encoder at each
stage. All of these features are forwarded to the convolu-
tional tail to reconstruct the clean image.
FFN Block
Norm
Features from Transformer Encoder
Weather Type Queries
Q
K, V
Multi-Head 
Attention
Transformer Block
Figure 3. Conﬁguration of the transformer block in the de-
coder. The queries here are learnable embeddings representing
the weather type while the keys and values are features taken from
the last stage of the transformer encoder.
3.1.3
Convolutional Projection Block
The set of hierarchical transformer encoder features and
task features from the transformer decoder are passed
through a set of 4 convolutional layers to output the clean
image. We also use an upsampling layer before every con-
volutional layer to get back to the original image size. We
also have skip connections across each stage in the convolu-
tional tail from the transformer encoder. We also use a tanh
activation function in the ﬁnal layer.
3.2. Loss
Our network is trained in an end-to-end fashion using a
smooth L1-loss between the prediction (ˆI) and the ground
truth (G) deﬁned as follows:
LsmoothL1 =

0.5E2
if |E| < 1
|E| −0.5
otherwise ,
(9)
where E = ˆI −G. We also add a perceptual loss that mea-
sures the discrepancy between the features of prediction and
the ground truth. We extract these features using a VGG16
network [47] pretrained on ImageNet. We extract features
from the 3rd, 8th and 15th layers of VGG16 to calculate
the perceptual loss. The perceptual loss is formulated as
follows
Lperceptual = LMSE(V GG3,8,15(ˆI), V GG3,8,15(G)).
The total loss can be summarized as follows
Ltotal = LsmoothL1 + λLperceptual,
(10)
where λ is a weight that controls the contribution of
Lperceptual and L1-loss on the overall loss.
4. Experiments
We conduct extensive experiments to show the effective-
ness of our proposed method. In what follows, we explain
the datasets, implementation details, experimental settings,
results and comparison with state-of-the-art methods.
4.1. Datasets
We train our network on a combination of images de-
graded from a variety of adverse weather conditions simi-
lar to All-in-One Network [23]. We follow the same train-
ing set distribution used in All-in-One for fair comparison.
The training data consists of 9,000 images sampled from
Snow100K [29], 1,069 images from Raindrop [37] and
9,000 images of Outdoor-Rain [21]. Snow100K has syn-
thetic images degraded by snow, raindrop has real raindrop
images and Outdoor-Rain has synthetic images degraded
by both fog and rain streaks. We term this combination of
training data as “All-Weather” for better representation.
We test our methods on both synthetic and real-world
datasets. We use the Test1 dataset [21, 23], the RainDrop
test dataset [37] and the Snow100k-L test set [29] for testing
our method. In addition, we also evaluate on real-world
images degraded by rain streaks and rain drops.
4.2. Implementation Details
We implement our method using Pytorch framework
[33] and train it using an NVIDIA RTX 8000 GPU. We use
an Adam optimizer [17] and a learning rate of 0.0002. We
use a learning rate scheduler that anneals the learning rate
by 2 after 100 and 150 epochs. The network is trained for
a total of 200 epochs with a batch size of 32. Other hyper-
parameters regarding the TransWeather architecture can be
found in the supplementary document.
4.3. Comparison with state-of-the-art methods
First, we compare our method with state-of-the-art meth-
ods which are designed speciﬁcally for each task: rain drop
removal, snow removal and rain+haze removal. For rain
drop removal, we compare the performance with state-of-
the-art methods like Attention GAN [37], Quan et al. [40],
and complementary cascaded network (CCN) [39].
For
snow removal, we compare with Desnow-Net [29], JSTASR
[6] and Deep Dense Multi-Scale Network (DDMSNet) [73].
For rain+fog removal, we compare with HRGAN [21],
Details-Net [11], Recurrent squeeze-and-excitation context
### Page 6

Type
Method
Venue
PSNR (↑)
SSIM (↑)
Task
Speciﬁc
DetailsNet + Dehaze (DHF) [11]
CVPR 2017
13.36
0.5830
DetailsNet + Dehaze (DRF) [11]
CVPR 2017
15.68
0.6400
RESCAN + Dehaze (DHF) [25]
ECCV 2018
14.72
0.5870
RESCAN + Dehaze (DHF) [25]
ECCV 2018
15.91
0.6150
pix2pix [15]
CVPR 2017
19.09
0.7100
HRGAN [21]
CVPR 2019
21.56
0.8550
Swin-IR [27]
CVPR 2021
23.23
0.8685
MPRNet [67]
CVPR 2021
21.90
0.8456
Multi
Task
All-in-One [23]
CVPR 2020
24.71
0.8980
TransWeather
-
27.96
0.9509
Table 1. Quantitative Comparison on the Test1 (rain+fog) dataset based on PSNR and SSIM. DHF represents De-Hazing First and
DRF represents De-Raining First. ↑means higher the better.
Type
Method
Venue
PSNR (↑)
SSIM (↑)
Task
Speciﬁc
DetailsNet [11]
CVPR 2017
19.18
0.7495
DesnowNet [29]
TIP 2018
27.17
0.8983
JSTASR [6]
ECCV 2020
25.32
0.8076
Swin-IR [27]
CVPR 2021
28.18
0.8800
DDMSNET [73]
TIP 2021
28.85
0.8772
Multi
Task
All-in-One [23]
CVPR 2020
28.33
0.8820
TransWeather
-
28.48
0.9308
Table 2. Quantitative Comparison on the SnowTest100k-L test
dataset based on PSNR and SSIM. . ↑means higher the better.
Type
Method
Venue
PSNR (↑)
SSIM (↑)
Task
Speciﬁc
Pix2pix [15]
CVPR 2017
28.02
0.8547
Attn. GAN [37]
CVPR 2018
30.55
0.9023
Quan et al. [40]
ICCV 2019
31.44
0.9263
Swin-IR [27]
CVPR 2021
30.82
0.9035
CCN [39]
CVPR 2021
31.34
0.9500
Multi
Task
All-in-One [23]
CVPR 2020
31.12
0.9268
TransWeather
-
28.84
0.9460
Table 3. Quantitative comparison on the RainDrop test dataset
based on PSNR and SSIM. ↑means higher the better.
aggregation Net (RESCAN) [25], and Multi-Stage Progres-
sive Restoration Network (MPRNet) [67]. We also com-
pare with a recent transformer network Swin-IR [27] for all
datasets. Note that all these methods are single-task han-
dling networks which are ﬁne-tuned for speciﬁc datasets.
We also compare the performance of our method with
All-in-One network [23] which is trained to perform all the
above tasks with a single model instance. Our method Tran-
sWeather is also trained to perform all these tasks using a
single model instance.
4.3.1
Referenced Quality Metrics
We use PSNR and SSIM to evaluate the performance of dif-
ferent models. We tabulate the quantitative results in terms
of PSNR and SSIM in Tables 1, 2, and 3 while evaluating
on the Test1 (fog+rain removal), Snow100K-L (snow re-
moval) and RainDrop (rain drop removal) test datasets, re-
spectively. As Test1 has both fog and rain, we sequentially
apply deraining and dehazing methods for fair comparison
on this dataset. For example, while using Details-Net and
RESCAN for deraining, we apply Multi-scale boosted de-
hazing network (MSBDN) [8] for dehazing. Note that from
our experiments we found MSBDN to be the best perform-
ing network for dehazing. We compare the performance
while applying deraining ﬁrst, then dehazing and also vice-
versa. We train Swin-IR and MPRNet directly on “Outdoor-
Rain” (training split of Test1) and test it on Test1 for fair
comparison. Similarly, Swin-IR was trained on Snow100K
dataset, RainDrop and tested on SnowTest100k-L, Rain-
Drop test datasets respectively. It can be noted that some
recent methods like CCN and DDMSNet when ﬁne-tuned
on the individual datasets outperform All-in-One.
Tran-
sWeather is observed to achieve an observed performance
when compared to these methods.
4.3.2
Visual Quality Comparison
Synthetic Images We illustrate the predictions from syn-
thetic test datasets like Test1 and Snow100k-L in Figures
4 and 5. It can be seen that Transweather achieves visu-
ally pleasing results compared to the previous methods. It
works very well in removing both fog and rain streaks as
can be seen in Figure 4 while other methods including All-
in-One fail to remove at least one of the degradations. It
can be seen from Figure 5 that our method removes even
the snow particles which are very small in structure while
All-in-One has hard time removing them.
Real-World Images We illustrate the predictions from real
test datasets like RainDrop and Real-World images in Fig-
ures 6 and 7. It can be seen in both the ﬁgures that Tran-
sweather removes even the ﬁnest rain streaks or drops when
compared to the previous methods.
5. Discussions
Ablation Study: We conduct an ablation study to under-
stand the contributions of individual components proposed
in the TransWeather architecture. We start with a base trans-
### Page 7

Input
RESCAN
MPRNet
All-in-One
TransWeather
Ground Truth
Figure 4. Sample qualitative results on the Test1 dataset. Red box corresponds to the zoomed-in patch for better comparison.
Input
All-in-One
TransWeather
Ground Truth
Figure 5.
Sample qualitative results on the Snow100k-L
dataset. Red box corresponds to the zoomed-in patches.
former encoder architecture and a conv tail. We call this
conﬁguration Transformer Base. We then convert the trans-
former encoder to hierarchical transformer (HE) encoder to
extract both high-level and low-level features where we per-
form patch merging between each stage in the transformer
encoder.
We then add the intra patch transformer block
(Intra-PT) in the encoder. Then we add learnable weather
type queries and a transformer decoder block to learn the
task embeddings.
This conﬁguration corresponds to the
TransWeather architecture. All of these models are trained
on All-Weather and tested on the Raindrop test dataset. The
results of ablation study can be found in Table 4. It can
be observed that each individual contribution of this work
helps in improving the performance.
Method
PSNR (↑)
SSIM (↑)
Transformer Base
30.12
0.8512
+ HE
31.62
0.8671
+ HE + Intra-PT
32.37
0.9463
+ HE + Intra-PT +Weather Queries
34.55
0.9502
Table 4. Ablation Study on the RainDrop test dataset. HE de-
notes converting to hierarchical transformer encoder and Intra-PT
represents intra-patch transformer blocks.
What do the weather queries learn? The weather queries
are embeddings which learn what type of degradation is
present in the image. These queries help in predicting the
corresponding task vector which is helpful to inject the task
information to get a better prediction. To show this, we
visualize the attention maps of eight random queries (out
of 512) for three images corresponding to different weather
degradations in Figure 8. It is interesting to observe that
queries Q1, Q3, and Q6 activate highly for foggy image.
They attend throughout the image to all the places afﬂicted
by the fog. Queries Q2, Q4 and Q8 are observed to activate
highly for rainy images and the attention maps are sparse
corresponding to the rain details. Similarly, queries Q5 and
Q7 activate to snow images more when compared to im-
ages with rain and fog. This shows that different queries
activate for different weather degredations helping Tran-
sWeather learn the underlying weather condition and give
better predictions. It can also be noted that when an image
is degraded by multiple weather conditions, multiple task
type queries activate to encode speciﬁc tasks. This can be
observed from the middle row of Figure 8 where queries
that attend to both fog and rain activate as the image is de-
graded by both of these conditions.
Inference Time: In Figure 1 (bottom row), we compare
the inference speed in terms of seconds. The time reported
in the table corresponds to the time taken by each model
feed forward an image of dimensions 256 × 256 during the
inference stage. We note that our method is faster (with just
0.14 seconds per image) during inference when compared
to the previous weather removal methods. TransWeather
has 31 M parameters which are less than that of All-in-One
Network which has 44 M parameters.
Differences from All-in-One: As the All-in-One network
[23] is the ﬁrst method to look into using a single model
instance for all weather removal problems, we present clear
differences of our method from All-in-One. First, All-in-
One is a CNN-based method while TransWeather uses a
transformer backbone built speciﬁcally for low-level vision
tasks with an extra focus on operating on smaller patches.
All-in-One uses multiple encoders while TransWeather uti-
lizes a single encoder. All-in-One uses adversarial training
and neural architecture search while TransWeather just uses
a combination of L1 and perceptual loss making the train-
ing more stable. TransWeather also has a faster inference
speed, lesser number of parameters while obtaining better
quantitative and qualitative performance.
Limitations: Although TransWeather achieves better per-
formance than previous methods, there are still some open
### Page 8

Input
Attention GAN
All-in-One
TransWeather
Quan et al.
Ground Truth
Figure 6. Sample qualitative results on the RainDrop dataset. Red box corresponds to the zoomed-in patches for better comparison.
Input
DID-MDN
MPRNet
All-in-One
TransWeather
RESCAN
Figure 7. Sample qualitative results on the Real-World images. Red box corresponds to the zoomed-in patch for better comparison.
Note that these are real-world images with no availability of ground truth.
Input 
Q1
Q2
Q3
Q4
Q5
Q6
Q7
Q8
Rain
Fog+Rain
Snow
0
1
Figure 8.
Attention maps with respect to different queries.
Rows correspond to input image with different weather degrada-
tions and the columns correspond to attention maps with different
queries (Q1 to Q8). Red, Green, and Blue boxes correspond to
queries that activate most to Rain, Fog and Snow respectively. Best
viewed when zoomed in and in color.
problems that TransWeather does not solve. TransWeather
does not perform well in some real world images afﬂicted
by high intensity rains. This can be understood as some-
times real-rain is very different in terms of streak size and
intensity and are difﬁcult to model. Moreover, if the inten-
sity of rain is high, it creates a splattering effect when it
hits the surface of objects or people in the scene. Removing
this splattering effect is still a limitation by all methods in-
cluding TransWeather. A sample limitation is illustrated in
Figure 9.
6. Conclusion
In this work, we proposed TransWeather - an efﬁcient
transformer-based solution for the all adverse weather re-
Input
MPRNet
All-in-One
TransWeather
Figure 9. Limitations of our method: High intensity rain and the
splattering effect of rain is not removed by any method.
moval problem. We focus on building a single model in-
stance which can remove any weather degradation present
in the image. We build a single encoder-decoder network
for restoration while using learnable weather type queries
in the decoder to learn the type of weather degradation and
use that information for the weather removal process. We
also propose a novel transformer encoder architecture base
which work on sub-patches thus aiding transformers to re-
move small weather degradations more efﬁciently. We ex-
tensively experiment on multiple synthetic and real-world
datasets where we use a single model instance to get good
results while also obtaining a faster inference speed. We
also obtain better visual results when tested on real-world
adverse weather images.
Acknowledgement: This work was supported by an ARO
grant W911NF-21-1-0135.
### Page 9

References
[1] Dana Berman, Shai Avidan, et al. Non-local image dehazing.
In Proceedings of the IEEE conference on computer vision
and pattern recognition, pages 1674–1682, 2016. 2
[2] Bolun Cai, Xiangmin Xu, Kui Jia, Chunmei Qing, and
Dacheng Tao. Dehazenet: An end-to-end system for single
image haze removal. IEEE Transactions on Image Process-
ing, 25(11):5187–5198, 2016. 2
[3] Nicolas Carion, Francisco Massa, Gabriel Synnaeve, Nicolas
Usunier, Alexander Kirillov, and Sergey Zagoruyko. End-to-
end object detection with transformers. In European Confer-
ence on Computer Vision, pages 213–229. Springer, 2020. 1,
4
[4] Hanting Chen, Yunhe Wang, Tianyu Guo, Chang Xu, Yiping
Deng, Zhenhua Liu, Siwei Ma, Chunjing Xu, Chao Xu, and
Wen Gao. Pre-trained image processing transformer. In Pro-
ceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition, pages 12299–12310, 2021. 3
[5] Liang-Chieh Chen, Yukun Zhu, George Papandreou, Florian
Schroff, and Hartwig Adam. Encoder-decoder with atrous
separable convolution for semantic image segmentation. In
Proceedings of the European conference on computer vision
(ECCV), pages 801–818, 2018.
[6] Wei-Ting Chen, Hao-Yu Fang, Jian-Jiun Ding, Cheng-Che
Tsai, and Sy-Yen Kuo. Jstasr: Joint size and transparency-
aware snow removal algorithm based on modiﬁed partial
convolution and veiling effect removal. In European Con-
ference on Computer Vision, pages 754–770. Springer, 2020.
3, 5, 6
[7] Franc¸ois Chollet. Xception: Deep learning with depthwise
separable convolutions.
In Proceedings of the IEEE con-
ference on computer vision and pattern recognition, pages
1251–1258, 2017. 4
[8] Hang Dong, Jinshan Pan, Lei Xiang, Zhe Hu, Xinyi Zhang,
Fei Wang, and Ming-Hsuan Yang. Multi-scale boosted de-
hazing network with dense feature fusion. In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition, pages 2157–2167, 2020. 1, 6
[9] Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov,
Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner,
Mostafa Dehghani, Matthias Minderer, Georg Heigold, Syl-
vain Gelly, et al. An image is worth 16x16 words: Trans-
formers for image recognition at scale.
arXiv preprint
arXiv:2010.11929, 2020. 2, 3
[10] Raanan Fattal. Dehazing using color-lines. ACM transac-
tions on graphics (TOG), 34(1):1–14, 2014. 2
[11] Xueyang Fu, Jiabin Huang, Delu Zeng, Yue Huang, Xinghao
Ding, and John Paisley. Removing rain from single images
via a deep detail network. In Proceedings of the IEEE Con-
ference on Computer Vision and Pattern Recognition, pages
3855–3863, 2017. 1, 5, 6
[12] Meng-Hao Guo, Jun-Xiong Cai, Zheng-Ning Liu, Tai-Jiang
Mu, Ralph R Martin, and Shi-Min Hu.
Pct: Point cloud
transformer.
Computational Visual Media, 7(2):187–199,
2021. 3
[13] Kaiming He, Jian Sun, and Xiaoou Tang. Single image haze
removal using dark channel prior. IEEE transactions on pat-
tern analysis and machine intelligence, 33(12):2341–2353,
2010. 1
[14] Dan Hendrycks and Kevin Gimpel.
Gaussian error linear
units (gelus). arXiv preprint arXiv:1606.08415, 2016. 4
[15] Phillip Isola, Jun-Yan Zhu, Tinghui Zhou, and Alexei A
Efros. Image-to-image translation with conditional adver-
sarial networks. In Proceedings of the IEEE conference on
computer vision and pattern recognition, pages 1125–1134,
2017. 6
[16] Li-Wei Kang, Chia-Wen Lin, and Yu-Hsiang Fu.
Auto-
matic single-image-based rain streaks removal via image
decomposition.
IEEE transactions on image processing,
21(4):1742–1755, 2011. 2
[17] Diederik P Kingma and Jimmy Ba. Adam: A method for
stochastic optimization.
arXiv preprint arXiv:1412.6980,
2014. 5
[18] Boyi Li, Xiulian Peng, Zhangyang Wang, Jizheng Xu, and
Dan Feng. Aod-net: All-in-one dehazing network. In Pro-
ceedings of the IEEE international conference on computer
vision, pages 4770–4778, 2017. 2
[19] Pengyue Li, Jiandong Tian, Yandong Tang, Guolin Wang,
and Chengdong Wu. Deep retinex network for single im-
age dehazing.
IEEE Transactions on Image Processing,
30:1100–1115, 2020. 1
[20] Pengyue Li, Mengshen Yun, Jiandong Tian, Yandong Tang,
Guolin Wang, and Chengdong Wu. Stacked dense networks
for single-image snow removal. Neurocomputing, 367:152–
163, 2019. 3
[21] Ruoteng Li, Loong-Fah Cheong, and Robby T Tan. Heavy
rain image restoration: Integrating physics model and condi-
tional adversarial learning. In Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition,
pages 1633–1642, 2019. 2, 3, 5, 6
[22] Runde Li, Jinshan Pan, Zechao Li, and Jinhui Tang. Single
image dehazing via conditional generative adversarial net-
work. In Proceedings of the IEEE Conference on Computer
Vision and Pattern Recognition, pages 8202–8211, 2018. 2
[23] Ruoteng Li, Robby T Tan, and Loong-Fah Cheong. All in
one bad weather removal using architectural search. In Pro-
ceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition, pages 3175–3185, 2020. 1, 2, 3, 5,
6, 7
[24] Wu Li, Valentin Pi¨ech, and Charles D Gilbert. Perceptual
learning and top-down inﬂuences in primary visual cortex.
Nature neuroscience, 7(6):651–657, 2004. 3
[25] Xia Li, Jianlong Wu, Zhouchen Lin, Hong Liu, and Hongbin
Zha. Recurrent squeeze-and-excitation context aggregation
net for single image deraining. In Proceedings of the Euro-
pean Conference on Computer Vision (ECCV), pages 254–
269, 2018. 2, 6
[26] Yawei Li, Kai Zhang, Jiezhang Cao, Radu Timofte, and Luc
Van Gool. Localvit: Bringing locality to vision transformers.
arXiv preprint arXiv:2104.05707, 2021. 4
[27] Jingyun Liang, Jiezhang Cao, Guolei Sun, Kai Zhang, Luc
Van Gool, and Radu Timofte. Swinir: Image restoration us-
ing swin transformer. In Proceedings of the IEEE/CVF Inter-
national Conference on Computer Vision, pages 1833–1844,
2021. 2, 3, 6
### Page 10

[28] Ming Liang, Bin Yang, Shenlong Wang, and Raquel Urtasun.
Deep continuous fusion for multi-sensor 3d object detection.
In Proceedings of the European Conference on Computer Vi-
sion (ECCV), pages 641–656, 2018. 1
[29] Yun-Fu Liu, Da-Wei Jaw, Shih-Chia Huang, and Jenq-
Neng Hwang. Desnownet: Context-aware deep network for
snow removal.
IEEE Transactions on Image Processing,
27(6):3064–3073, 2018. 1, 2, 3, 5, 6
[30] Ze Liu, Yutong Lin, Yue Cao, Han Hu, Yixuan Wei,
Zheng Zhang, Stephen Lin, and Baining Guo. Swin trans-
former: Hierarchical vision transformer using shifted win-
dows. arXiv preprint arXiv:2103.14030, 2021. 3
[31] Ze Liu, Jia Ning, Yue Cao, Yixuan Wei, Zheng Zhang,
Stephen Lin, and Han Hu. Video swin transformer. arXiv
preprint arXiv:2106.13230, 2021. 3
[32] Justin NJ McManus, Wu Li, and Charles D Gilbert. Adap-
tive shape processing in primary visual cortex. Proceedings
of the National Academy of Sciences, 108(24):9739–9746,
2011. 3
[33] Adam Paszke, Sam Gross, Francisco Massa, Adam Lerer,
James Bradbury, Gregory Chanan, Trevor Killeen, Zeming
Lin, Natalia Gimelshein, Luca Antiga, Alban Desmaison,
Andreas Kopf, Edward Yang, Zachary DeVito, Martin Rai-
son, Alykhan Tejani, Sasank Chilamkurthy, Benoit Steiner,
Lu Fang, Junjie Bai, and Soumith Chintala. Pytorch: An im-
perative style, high-performance deep learning library. In H.
Wallach, H. Larochelle, A. Beygelzimer, F. d'Alch´e-Buc, E.
Fox, and R. Garnett, editors, Advances in Neural Informa-
tion Processing Systems 32, pages 8024–8035. Curran Asso-
ciates, Inc., 2019. 5
[34] Asanka G Perera, Yee Wei Law, and Javaan Chahl. Uav-
gesture: A dataset for uav control and gesture recognition.
In Proceedings of the European Conference on Computer Vi-
sion (ECCV) Workshops, pages 0–0, 2018. 1
[35] Aditya Prakash, Kashyap Chitta, and Andreas Geiger. Multi-
modal fusion transformer for end-to-end autonomous driv-
ing. In Proceedings of the IEEE/CVF Conference on Com-
puter Vision and Pattern Recognition, pages 7077–7087,
2021. 1
[36] Charles R Qi, Wei Liu, Chenxia Wu, Hao Su, and Leonidas J
Guibas. Frustum pointnets for 3d object detection from rgb-
d data. In Proceedings of the IEEE conference on computer
vision and pattern recognition, pages 918–927, 2018. 1
[37] Rui Qian, Robby T Tan, Wenhan Yang, Jiajun Su, and Jiay-
ing Liu. Attentive generative adversarial network for rain-
drop removal from a single image. In Proceedings of the
IEEE conference on computer vision and pattern recogni-
tion, pages 2482–2491, 2018. 1, 2, 3, 5, 6
[38] Qin Qin, Jingke Yan, Qin Wang, Xin Wang, Minyao Li, and
Yuqing Wang. Etdnet: An efﬁcient transformer deraining
model. IEEE Access, 9:119881–119893, 2021. 1, 3
[39] Ruijie Quan, Xin Yu, Yuanzhi Liang, and Yi Yang. Remov-
ing raindrops and rain streaks in one go. In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition, pages 9147–9156, 2021. 2, 5, 6
[40] Yuhui Quan, Shijie Deng, Yixin Chen, and Hui Ji.
Deep
learning for seeing through window with raindrops.
In
Proceedings of the IEEE/CVF International Conference on
Computer Vision, pages 2463–2471, 2019. 1, 2, 3, 5, 6
[41] Shaoqing Ren, Kaiming He, Ross Girshick, and Jian Sun.
Faster r-cnn: Towards real-time object detection with region
proposal networks. Advances in neural information process-
ing systems, 28:91–99, 2015. 1
[42] Wenqi Ren, Si Liu, Hua Zhang, Jinshan Pan, Xiaochun Cao,
and Ming-Hsuan Yang. Single image dehazing via multi-
scale convolutional neural networks. In European conference
on computer vision, pages 154–169. Springer, 2016. 2
[43] Wenqi Ren, Lin Ma, Jiawei Zhang, Jinshan Pan, Xiaochun
Cao, Wei Liu, and Ming-Hsuan Yang. Gated fusion network
for single image dehazing. In Proceedings of the IEEE Con-
ference on Computer Vision and Pattern Recognition, pages
3253–3261, 2018. 2
[44] Weihong Ren, Jiandong Tian, Zhi Han, Antoni Chan, and
Yandong Tang. Video desnowing and deraining based on ma-
trix decomposition. In Proceedings of the IEEE Conference
on Computer Vision and Pattern Recognition, pages 4210–
4219, 2017. 1, 2
[45] Stefan Roth and Michael J Black. Fields of experts: A frame-
work for learning image priors.
In 2005 IEEE Computer
Society Conference on Computer Vision and Pattern Recog-
nition (CVPR’05), volume 2, pages 860–867. IEEE, 2005.
1
[46] Leonid I Rudin, Stanley Osher, and Emad Fatemi. Nonlinear
total variation based noise removal algorithms. Physica D:
nonlinear phenomena, 60(1-4):259–268, 1992. 1
[47] Karen Simonyan and Andrew Zisserman. Very deep convo-
lutional networks for large-scale image recognition. arXiv
preprint arXiv:1409.1556, 2014. 5
[48] Fuxiang Tan, YuTing Kong, Yingying Fan, Feng Liu, Daxin
Zhou, Long Chen, Liang Gao, Yurong Qian, et al. Sdnet:
mutil-branch for single image deraining using swin. arXiv
preprint arXiv:2105.15077, 2021. 1, 3
[49] Jeya Maria Jose Valanarasu, Poojan Oza, Ilker Hacihaliloglu,
and Vishal M. Patel.
Medical transformer: Gated axial-
attention for medical image segmentation. In Medical Im-
age Computing and Computer Assisted Intervention – MIC-
CAI 2021, pages 36–46, Cham, 2021. Springer International
Publishing. 3
[50] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszko-
reit, Llion Jones, Aidan N Gomez, Łukasz Kaiser, and Illia
Polosukhin. Attention is all you need. In Advances in neural
information processing systems, pages 5998–6008, 2017. 4,
5
[51] Hong Wang, Qi Xie, Qian Zhao, and Deyu Meng. A model-
driven deep neural network for single image rain removal.
In Proceedings of the IEEE/CVF Conference on Computer
Vision and Pattern Recognition, pages 3103–3112, 2020. 2
[52] Lijun Wang, Jianming Zhang, Oliver Wang, Zhe Lin, and
Huchuan Lu. Sdc-depth: Semantic divide-and-conquer net-
work for monocular depth estimation.
In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition, pages 541–550, 2020. 1
[53] Tianyu Wang, Xin Yang, Ke Xu, Shaozhe Chen, Qiang
Zhang, and Rynson WH Lau. Spatial attentive single-image
### Page 11

deraining with a high quality real rain dataset. In Proceed-
ings of the IEEE/CVF Conference on Computer Vision and
Pattern Recognition, pages 12270–12279, 2019. 1
[54] Wenhai Wang, Enze Xie, Xiang Li, Deng-Ping Fan, Kaitao
Song, Ding Liang, Tong Lu, Ping Luo, and Ling Shao.
Pyramid vision transformer:
A versatile backbone for
dense prediction without convolutions.
arXiv preprint
arXiv:2102.12122, 2021. 4
[55] Zhendong Wang,
Xiaodong Cun,
Jianmin Bao,
and
Jianzhuang Liu. Uformer: A general u-shaped transformer
for image restoration.
arXiv preprint arXiv:2106.03106,
2021. 2, 3
[56] Wei Wei, Deyu Meng, Qian Zhao, Zongben Xu, and Ying
Wu.
Semi-supervised transfer learning for image rain re-
moval.
In Proceedings of the IEEE/CVF Conference on
Computer Vision and Pattern Recognition, pages 3877–
3886, 2019. 1
[57] Haiyan Wu, Yanyun Qu, Shaohui Lin, Jian Zhou, Ruizhi
Qiao, Zhizhong Zhang, Yuan Xie, and Lizhuang Ma. Con-
trastive learning for compact single image dehazing. In Pro-
ceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition, pages 10551–10560, 2021. 1
[58] Haiping Wu, Bin Xiao, Noel Codella, Mengchen Liu,
Xiyang Dai, Lu Yuan, and Lei Zhang.
Cvt:
Introduc-
ing convolutions to vision transformers.
arXiv preprint
arXiv:2103.15808, 2021. 4
[59] Enze Xie, Wenhai Wang, Zhiding Yu, Anima Anandkumar,
Jose M Alvarez, and Ping Luo. Segformer: Simple and ef-
ﬁcient design for semantic segmentation with transformers.
arXiv preprint arXiv:2105.15203, 2021. 1, 4
[60] Sen Yang, Zhibin Quan, Mu Nie, and Wankou Yang. Trans-
pose: Keypoint localization via transformer. In Proceedings
of the IEEE/CVF International Conference on Computer Vi-
sion, pages 11802–11812, 2021. 3
[61] Wenhan Yang, Robby T Tan, Jiashi Feng, Zongming Guo,
Shuicheng Yan, and Jiaying Liu. Joint rain detection and
removal from a single image with contextualized deep net-
works. IEEE transactions on pattern analysis and machine
intelligence, 42(6):1377–1393, 2019. 1, 2
[62] Wenhan Yang, Robby T. Tan, Shiqi Wang, Yuming Fang, and
Jiaying Liu. Single image deraining: From model-based to
data-driven and beyond, 2019. 2
[63] Rajeev Yasarla and Vishal M Patel.
Uncertainty guided
multi-scale residual learning-using a cycle spinning cnn for
single image de-raining. In Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition,
pages 8405–8414, 2019. 1
[64] Rajeev Yasarla, Vishwanath A Sindagi, and Vishal M Pa-
tel.
Syn2real transfer learning for image deraining using
gaussian processes. In Proceedings of the IEEE/CVF con-
ference on computer vision and pattern recognition, pages
2726–2736, 2020. 2
[65] Rajeev Yasarla, Jeya Maria Jose Valanarasu, and Vishal M
Patel. Exploring overcomplete representations for single im-
age deraining using cnns. IEEE Journal of Selected Topics
in Signal Processing, 15(2):229–239, 2020. 2
[66] Shaodi You, Robby T Tan, Rei Kawakami, Yasuhiro
Mukaigawa, and Katsushi Ikeuchi. Adherent raindrop mod-
eling, detectionand removal in video. IEEE transactions on
pattern analysis and machine intelligence, 38(9):1721–1733,
2015. 1, 2
[67] Syed Waqas Zamir, Aditya Arora, Salman Khan, Munawar
Hayat, Fahad Shahbaz Khan, Ming-Hsuan Yang, and Ling
Shao. Multi-stage progressive image restoration. In Pro-
ceedings of the IEEE/CVF Conference on Computer Vision
and Pattern Recognition, pages 14821–14831, 2021. 2, 6
[68] He Zhang and Vishal M Patel. Densely connected pyramid
dehazing network. In Proceedings of the IEEE conference on
computer vision and pattern recognition, pages 3194–3203,
2018. 2
[69] He Zhang and Vishal M Patel. Density-aware single image
de-raining using a multi-stream dense network. In Proceed-
ings of the IEEE conference on computer vision and pattern
recognition, pages 695–704, 2018. 1, 2
[70] He Zhang, Vishwanath Sindagi, and Vishal M Patel. Im-
age de-raining using a conditional generative adversarial net-
work. IEEE transactions on circuits and systems for video
technology, 30(11):3943–3956, 2019. 1, 2
[71] He Zhang, Vishwanath Sindagi, and Vishal M Patel. Joint
transmission map estimation and dehazing using deep net-
works. IEEE Transactions on Circuits and Systems for Video
Technology, 30(7):1975–1986, 2019. 1
[72] Jingang Zhang, Wenqi Ren, Shengdong Zhang, He Zhang,
Yunfeng Nie, Zhe Xue, and Xiaochun Cao.
Hierarchical
density-aware dehazing network. IEEE Transactions on Cy-
bernetics, 2021. 1, 2, 3
[73] Kaihao Zhang, Rongqing Li, Yanjiang Yu, Wenhan Luo, and
Changsheng Li. Deep dense multi-scale network for snow
removal using semantic and depth priors. IEEE Transactions
on Image Processing, 30:7419–7431, 2021. 1, 2, 5, 6
[74] Dong Zhao, Jia Li, Hongyu Li, and Long Xu.
Hybrid
local-global transformer for image dehazing. arXiv preprint
arXiv:2109.07100, 2021. 1, 3
[75] Sixiao Zheng, Jiachen Lu, Hengshuang Zhao, Xiatian Zhu,
Zekun Luo, Yabiao Wang, Yanwei Fu, Jianfeng Feng, Tao
Xiang, Philip HS Torr, et al.
Rethinking semantic seg-
mentation from a sequence-to-sequence perspective with
transformers. In Proceedings of the IEEE/CVF Conference
on Computer Vision and Pattern Recognition, pages 6881–
6890, 2021. 3
[76] Lei Zhu, Chi-Wing Fu, Dani Lischinski, and Pheng-Ann
Heng.
Joint bi-layer optimization for single-image rain
streak removal. In Proceedings of the IEEE international
conference on computer vision, pages 2526–2534, 2017. 1,
2