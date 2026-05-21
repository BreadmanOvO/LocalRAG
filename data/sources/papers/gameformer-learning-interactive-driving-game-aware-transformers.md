# GameFormer Learning Interactive Driving Game-aware Transformers

**Source**: arxiv PDF, 11 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

LLM4VG: Large Language Models Evaluation for Video Grounding
Wei Feng
Tsinghua University
Xin Wang*
Tsinghua University
Hong Chen
Tsinghua University
Zeyang Zhang
Tsinghua University
Houlun Chen
Tsinghua University
Zihan Song
Tsinghua University
Yuwei Zhou
Tsinghua University
Yuekui Yang
Tencent
Tsinghua University
Haiyang Wu
Tencent
Wenwu Zhu∗
Tsinghua University
Abstract
Large language models (LLMs) have achieved great suc-
cess in various tasks. Recently, researchers have attempted
to investigate the capability of LLMs in handling videos and
proposed several video LLM models. However, the ability
of LLMs to handle video grounding (VG), which is an im-
portant time-related video task requiring the model to pre-
cisely locate the start and end timestamps of temporal mo-
ments in videos that match the given textual queries, still re-
mains unclear and unexplored in literature. To fill the gap,
in this paper, we propose the LLM4VG benchmark, which
systematically evaluates the performance of different LLMs
on video grounding tasks. Based on our proposed LLM4VG,
we design extensive experiments to examine two groups of
video LLM models on video grounding: (i) the video LLMs
trained on the text-video pairs (denoted as VidLLM), and
(ii) the LLMs combined with pretrained visual description
models such as the video/image captioning model. We pro-
pose tailored prompt methods to integrate the instruction of
VG and description from different kinds of generators, in-
cluding caption-based generators for direct visual descrip-
tion and VQA-based generators for information enhance-
ment. We also provide comprehensive comparisons of vari-
ous VidLLMs and explore the influence of different choices
of visual models, LLMs, prompt designs, etc, as well. Our
experimental evaluations lead to two conclusions: (i) the
existing VidLLMs are still far away from achieving satisfac-
tory video grounding performance, and more time-related
video tasks should be included to further fine-tune these
models, and (ii) the combination of LLMs and visual models
*Corresponding author
shows preliminary abilities for video grounding with con-
siderable potential for improvement by resorting to more re-
liable models and further guidance of prompt instructions.
1. Introduction
With the rapid development of large language models
(LLMs) in recent years, various tasks beyond natural lan-
guage processing, such as dynamic graphs [48], visual ques-
tion answering [13], reinforcement learning [5], have be-
gun to combine with LLMs for performance improvement.
Also, more and more tasks requiring multimodal informa-
tion are dedicated to linking LLMs’ text processing capa-
bilities with video perception abilities [44, 49].
For in-
stance, Li et al. [18] and Zhang et al. [47] propose large lan-
guage models such as Video-Chat and Video-LLaMA that
can handle video data, demonstrating impressive ability in
receiving and understanding video.
Video grounding (VG), as an important time-related
video task aiming to identify the corresponding video seg-
ments of given textual descriptions [40], asks to precisely
understand temporal boundary information with start and
end time of different segments in videos [9]. However, de-
spite the success of the existing LLMs, their ability to han-
dle video grounding (VG) which requires accurate localiza-
tion of time boundaries for moments, still remains unclear
and unexplored in literature.
To fill the gap, we propose LLM4VG, a comprehensive
benchmark which systematically evaluates the performance
of VG task for LLMs. We adopt two methods to complete
video grounding. Based on our proposed LLM4VG, we ex-
amine two groups of video LLM strategies on VG task: i)
1
arXiv:2312.14206v3  [cs.CV]  12 Sep 2024
### Page 2

the video LLMs trained on the text-video dataset directly
accept the video content and video grounding task instruc-
tions as input and then output the prediction results (denoted
as VidLLM); ii) the LLMs combined with pretrained vi-
sual description model that converts video content to text
descriptions via visual description generators, thus bridg-
ing the visual and textual information. As for the second
group of strategies, we specifically design prompts that inte-
grate the instruction of VG and the given visual description
information from different kinds of generators, including
caption-based generators to directly output description and
VQA-based to enhance the description information, which
compensates for the failure of the caption model to include
keywords of grounding query, revealing LLMs’ temporal
understanding abilities on video grounding tasks.
We conduct extensive evaluations to analyze the perfor-
mance of employing six visual models, three LLMs, and
three prompting methods, and compare them with three
VidLLMs which are directly instructed to conduct VG task.
Furthermore, we claim eight experimental observations as
foundations for designing good video LLMs on VG. Specif-
ically, our evaluations show that VidLLMs are still far away
from achieving satisfactory VG performance, and more
time-related video tasks should be included to further fine-
tune the VidLLMs in order to reach a performance boost. In
terms of the combining visual models and LLMs, our pro-
posed strategy which incorporates LLMs with visual mod-
els achieves better performance for temporal boundary un-
derstanding than VidLLMs, showing preliminary abilities
for VG task.
The video grounding ability of combining
strategy is mainly limited by the prompt designs and vi-
sual description models. More fine-grained visual models
should be utilized so that more visual information is intro-
duced to empower LLMs with the capability of understand-
ing the visual scene and therefore adequately completing
the VG task. In addition, the prompting method with fur-
ther guidance of instructions is also required to help LLMs
better conduct the VG task.
To summarize, we make the following contributions:
• We propose LLM4VG, the first comprehensive bench-
mark for evaluating LLMs on video grounding (VG) task.
• We develop an integration of task instruction of VG and
visual description from different kinds of visual genera-
tors, including caption-based generators and VQA-based
generators, which proves to be effective LLM prompts.
• We systematically evaluate and analyze the VG perfor-
mance of different groups of video LLM models through
combinations with different visual description models
and promoting methods.
• We conclude fine-grained observations about LLMs’ per-
formance on VG, which can serve as foundations for de-
signing good video LLMs on VG.
2. Related Work
2.1. LLMs for Video Understanding
Large Language Model (LLM) is trained through massive
text data [33] and is able to perform a wide range of tasks
including text summarization, translation, reasoning, emo-
tional analysis, and more [16, 27, 50]. With the introduc-
tion of GPT-3 [10], InstructGPT [32], and GPT-4 [31], this
concept has become widely known for understanding and
generating human language.
However, in the digital world today, video and audio con-
tent share the same importance with textual content as part
of multimedia data [51]. This makes it hard for a simple
LLM to expand into the field of audiovisual perception to
meet the needs of users. To address this issue, two differ-
ent approaches have been proposed in the academic com-
munity.
One is to develop a large language model with
multimodal information processing capabilities. Therefore,
many large language models that can handle videos have
emerged, such as Video-LLaMA [47], Video-Chat [18] and
Video-ChatGPT [28].
We collectively refer to them as
VidLLM. While retaining LLM’s powerful language com-
prehension abilities, VidLLM has also demonstrated im-
pressive ability in receiving and understanding visual and
auditory content. The other one is to convert the visual and
audio information into intermediate language descriptions
instead of dense vectors [3], using the descriptions and few-
shot in-context exemplars to instruct normal LLMs to com-
plete video-related tasks, which has been used by Guo et al.
for visual question answering tasks of LLMs [13].
Naturally, we wonder whether the method mentioned
above can complete cross-modal tasks related to video, such
as video grounding.
2.2. Video Grounding
Video grounding is a task that requires the model to lo-
calize the starting and ending times of the segment target
from a video [8], which has drawn increasing attention over
the past few years [19, 29], since video grounding task is
closely related to quite a few computer vision and language
processing methods such as video understanding, video re-
trieval, and human-computer interaction, etc [11, 15, 45].
Regarding the challenges of video grounding tasks,
many approaches have been proposed [36, 42, 43]. He et al.
propose a reinforcement learning method that includes an
adjustable temporal window with a sliding boundary, which
has the learned policy for video grounding [14]. Zeng et
al. proposed a dense regression network that regresses the
distances from every frame to the starting or ending frame
of the video segment described by the query [46]. Chen
et al. proposed an Adaptive Dual-branch Promoted Net-
work (ADPN) that exploits consistency and complementar-
ity of audio and visual information instead of focusing on
2
### Page 3

VidLLM
🦜🦜 
Video-Chat
🎥🎥 💬💬
Video-ChatGPT
Video-LLaMA
LLM
GPT-3.5
Vicuna
Longchat
Prompt Design
One-shot
Zero-shot
…
Visual Description 
Generator
Fc, Att2in
Transformer, Updown,
Blip for caption, 
Blip for VQA
Start time: 𝑥𝑥𝑠𝑠
End time: 𝑦𝑦𝑠𝑠
Find the start time and end time of the query below from the video.
Query: A man reaches out and then pets the fish.
Figure 1. Benchmark of LLM4VG. We analyze the influences
of applying six visual description generators, three LLMs, and
three prompting methods for video grounding, comparing them
with three VidLLMs which are directly instructed to conduct video
grounding tasks.
visual information only [7]. These methods, however, all re-
quire the use of annotated specific video grounding training
datasets for pre-training, which cannot be directly applied
to task scenarios.
3. The LLM4VG Benchmark
In this section, we will introduce our proposed LLM4VG
benchmark to evaluate whether LLMs are capable of un-
derstanding temporal information on the video grounding
task. As shown in Figure 1, our benchmark mainly includes
four variables to be evaluated for their impact on completing
video grounding tasks, including the selection of VidLLMs,
normal LLMs, visual description models, and prompt de-
signs. We will then introduce their role in completing the
video grounding task in sequence.
3.1. Video Grounding with VidLLMs
As shown in Figure 2(a), we first use VidLLMs that can ac-
cess video content as the baseline of our experiment, trying
to complete the video grounding task. They will directly re-
ceive video and instruct prompt to output video grounding
predictions. The details of the instruct prompt are consis-
tent with the question prompt mentioned in the following
prompt design section 3.2.2.
3.2. Video Grounding with Combination of LLMs
and Visual Models
As shown in Figure 2(b), for those LLMs without the abil-
ity to process visual data, we first used a visual description
generator to process the video, generating a basic descrip-
tion sequence with controllable time span parameters (such
as a second-by-second caption of individual video content).
Next, we adjust the description sequence to an appropri-
ately formatted prompt as input, instructing LLM to output
grounding predictions. Based on this process, we evaluate
the result of video grounding from three different perspec-
tives, which include visual description generators, prompt
designs, and LLMs.
3.2.1
Visual Description Generator
In order to convert video data information into text content
that LLMs can understand, we first extract images from
the video at 1 FPS, then input images to the visual mod-
els, and then output text describing the frame at that times-
tamp, summarizing them to form a continuous visual de-
scription Des = {(t1, c1), (t2, c2)...(tm, cm)}, where t ∼
T({1s, 2s, ...}) is a sequential timestamp and ci is a visual
description of the corresponding time. The visual models
we use can be divided into caption-based and VQA-based.
Caption-based generator.
We use a series of caption
models including the simple Fc model using CNN and
LSTM networks [25, 34], the Attention model(Att2in) [26,
34] and Updown model [1] introducing attention mech-
anisms, the transformer-based sequence modeling frame-
work(Transformer) [22, 38], and advanced caption models
such as the Blip model that effectively utilizes the noise
web data by bootstrapping the captions to improve visual
language task capabilities [23]. As the easiest way, these
models would directly transform the image into the visual
description ci per second.
VQA-based generator. Considering the occasional miss-
ing key information in the visual description due to the
weak generalization ability of caption-based generator(for
example, many visual descriptions provided by the caption
model do not contain keywords in the query), we also use
the Blip model with visual question answering(VQA) ca-
pability as a visual description generator [20, 23] to en-
hance the description information. We first use its answer
to ‘What is happening in the image’ as the caption descrip-
tion for the video at time ti, and then ask it to answer ‘Is
it currently happening <query event> in the image’. Fi-
nally, we will merge the two answers as the video descrip-
tion ci of the current time and form the description sequence
Des = {(t1, c1), (t2, c2)...(tm, cm)}.
3.2.2
Prompt Design
To instruct the LLM for the video grounding task, we de-
sign the input text prompt for the LLM that mainly consists
of three parts: question prompt, description prompt, and ex-
emplar prompt.
3
### Page 4

❆ VidLLM
Find the start time and end time of 
the query below from the video.
Query: A man reaches out and then 
pets the fish.
Question Prompt
❆ LLM
Find the start time and end time of 
the query below from the video.
Query: A man reaches out and then 
pets the fish.
Question Prompt
Start time: 𝑥𝑥𝑠𝑠
End time: 𝑦𝑦𝑠𝑠
Visual description generator
1.0s: A man swimming underwater.
… 
14.0s: A man underwater reaches his hand.
Description Prompt
Find the start time and end time of the 
query below from the video.
Query: A person flipped the light 
switch near the door.
Input:
…
12.0s: A person flipped a switch.
13.0s: A person turns the light on.
…
Answer: Start time:12𝑠𝑠End time:14𝑠𝑠
Exemplar Prompt
(b) Video grounding with LLMs and visual models
(a) Video grounding with VidLLMs
Start time: 𝑥𝑥𝑠𝑠
End time: 𝑦𝑦𝑠𝑠
Figure 2. Framework of video grounding for LLMs. (a) stands for video grounding with VidLLMs. (b) stands for video grounding with
LLMs and visual models. The dashed box represents that in the one-shot method, we will input the exemplar prompt, description prompt,
and question prompt, while in the zero-shot method, we will not input the exemplar prompt.
The question prompt Ques mainly describes the task
of video grounding, which consists of task requirements
and a query for video.
The task requirements are ‘Find
the start time and end time of the query below from the
video’. The description prompt is the description sequence
Des received from the visual description generator, which
includes the video description content of every second un-
til the end of the video. The exemplar prompt Exem is a
video grounding example that we pre-generated, including
the combined content of a hypothetical description prompt
and a hypothetical question prompt, and an answer to it.
Finally, as shown in Figure 2(b), we propose a zero-shot
method to integrate the description prompt and question
prompt as input, and we add the extra exemplar prompt to
enable LLMs to better understand the task of video ground-
ing for the one-shot method.
Shown in Table 1, we form the prompt prepared for
LLMs as input:
Prompt = [Exem, Des, Ques],
(1)
where Exem is optional depending on the chosen of one-
shot or zero-shot method.
3.2.3
Large Language Model
For LLMs that cannot directly access video content, they
will be input the Prompt generated in the process above
and instructed to complete the video grounding task. For
the result Output = LLM(Prompt), we will extract the
content in the answer for the prediction result of start and
end time.
3.3. Video Grounding Evaluation
We evaluate the results of LLM in video grounding tasks.
And corresponding evaluation dimension was used to mea-
sure their ability to complete video grounding. We will in-
Prompt
Example
Exemplar
Here is an example:
Question:
Given a sequence of video de-
scriptions with the time stamps
[(t1, c1), (t2, c2)...(tm, cm)].
When
is
the
woman
cooking?
Answer:[15s, 21s]
Description
A
sequence
of
video
descrip-
tion
with
the
time
stamps
[(t1, c1), (t2, c2)...(tm, cm)].
Question
Find the start time and end time
of the query below from the video.
Query: the person flipped the light
switch near the door.
Answer
[10s, 14s]
Table 1. An example of prompt construction for the video ground-
ing task.
troduce the definition and measurement of corresponding
evaluation dimensions as follows:
Evaluation: Recall on Video Grounding. Recall is the
main outcome evaluation metric for verifying the LLMs’
completion of video grounding tasks, which directly calcu-
lates the difference between the grounding time answer pro-
vided by LLMs and the actual results. In the usual process
of evaluating video grounding results, we first calculate the
intersection over union ratio (IoU) based on the predicted
results and ground truth and then use R@n, IoU = m as the
evaluation metrics [12], which represents the percentage of
testing video grounding samples that have at least one cor-
rect prediction (i.e., the IoU between the ground truth and
the prediction result is larger than m) in the top-n results of
prediction.
4
### Page 5

Valid Rate
Model
Fc [34]
Att2in [34]
Transformer [22]
Updown [1]
Blip [23]
Blip(VQA) [23]
Zero-Shot Evaluation with Large Language Model
R@1 IoU=0.3
Random:23.36
GPT-3.5 [30]
25.83
25.99
25.46
23.74
25.81
25.97
Vicuna-7B [41]
19.87
19.19
20.73
19.92
19.41
19.57
Longchat-7B [21]
23.47
23.17
23.01
23.90
22.55
23.95
R@1 IoU=0.5
Random:9.06
GPT-3.5
9.68
10.19
10.62
9.03
10.03
10.05
Vicuna-7B
8.20
7.72
8.04
7,72
8.06
7.90
Longchat-7B
9.38
9.60
9.84
10.91
9.60
9.95
R@1 IoU=0.7
Random:2.88
GPT-3.5
2.50
2.58
2.31
2.50
3.20
3.04
Vicuna-7B
2.53
2.55
2.42
2.12
2.47
2.23
Longchat-7B
3.09
2.82
3.25
3.47
2.82
3.33
One-Shot Evaluation with Large Language Model
R@1 IoU=0.3
Random:23.36
GPT-3.5
24.11
23.47
24.19
24.25
26.02
17.96
Vicuna-7B
16.72
16.94
17.66
17.82
15.22
16.29
Longchat-7B
19.70
19.03
18.68
18.25
19.30
19.54
R@1 IoU=0.5
Random:9.06
GPT-3.5
9.30
8.90
9.60
9.11
10.91
7.61
Vicuna-7B
7.10
7.23
7.45
7.02
5.99
7.02
Longchat-7B
8.87
8.58
8.33
7.69
8.33
8.74
R@1 IoU=0.7
Random:2.88
GPT-3.5
2.85
2.23
3.04
2.85
2.93
2.69
Vicuna-7B
2.12
2.23
1.94
1.94
1.85
2.10
Longchat-7B
2.88
2.96
2.12
2.31
2.61
2.31
One-Shot+confidence judgment Evaluation with Large Language Model
R@1 IoU=0.3
Random:23.36
GPT-3.5
24.68
28.23
26.32
25.13
30.67
33.87
Vicuna-7B
21.67
20.70
21.67
19.30
22.37
23.63
Longchat-7B
23.20
23.71
22.82
24.41
24.57
23.63
R@1 IoU=0.5
Random:9.06
GPT-3.5
9.27
11.34
9.92
9.03
11.26
11.80
Vicuna-7B
9.76
9.09
9.38
8.74
8.20
9.14
Longchat-7B
9.60
10.22
9.01
10.22
9.97
9.76
R@1 IoU=0.7
Random:2.88
GPT-3.5
2.55
2.85
2.80
2.55
3.84
4.22
Vicuna-7B
3.15
2.77
2.69
2.80
2.45
2.63
Longchat-7B
3.17
3.17
2.45
3.92
3.31
2.96
Table 2. The overall model performance on the video grounding with different visual description generators, Large Language Models, and
prompting methods. The ‘Blip’ means we use the Blip model for captioning, while the ‘Blip(VQA)’ means the Blip model is used for
visual question answering and captioning. Considering that in some cases the visual descriptions obtained by LLMs may not be applicable
to video grounding tasks, we added an extra confidence judgment prompt to check whether the description sequence is suitable for video
grounding tasks.
Valid Rate
Video-Chat [18]
Video-ChatGPT [28]
Video-LLaMA [47]
Random
R@1 IoU=0.3
9.03
20.00
10.38
23.36
R@1 IoU=0.5
3.31
7.69
3.84
9.06
R@1 IoU=0.7
1.26
1.75
0.91
2.88
Table 3. The overall model performance on the video grounding with VidLLMs
4. Experiments
In this chapter, we conduct experiments to evaluate LLMs’
ability to understand temporal information and language
reasoning on video grounding problems.
4.1. Setups
Visual description generators.
We used caption mod-
els such as Att2in, Fc [26, 34], Transformer [22], Up-
down [1], and Blip [20, 23] model as the main visual de-
scription generators to generate a per-second description
sequence of video content. In addition, we also used the
VQA model [2, 20], to generate a per-second description
sequence and additional answering sequence. (i.e., answer-
ing that in every second of the video if the event mentioned
in the video grounding question is happening)
Prompts.
To investigate the impact of different prompt
methods on the model’s ability to complete video ground-
ing, we compared different prompt methods, including
zero-shot prompting and one-shot prompting [4, 24]. For
examples shown in Table 1, the prompt is composed
5
### Page 6

of exemplar prompts, description prompts, and question
prompts.
Models.
Considering that the prompt obtained through
the visual description generator generally has a large num-
ber of tokens, we used GPT-3.5-turbo-16k [30], Vicuna-
7B [41], Longchat-7B [21], and VidLLM such as Video-
Chat, Video-ChatGPT and Video-LLaMA [6, 18, 28, 47].
As a comparison, we apply a random method that randomly
generates answers within the video duration for grounding.
For a few prompts that LLMs refuse to provide answers due
to the poor quality of visual description, the answer will be
randomly generated using the rando baseline method. For
VidLLM, it does not require the use of a visual description
generator, as it already has the ability to receive and process
video data.
Data.
We use the Charades-STA dataset [12] for video
grounding tasks, which is a benchmark dataset developed
based on the Charades dataset [35] by adding sentence tem-
poral annotations. It contains 3720 video-query pairs for
testing.
4.2. Main Results
The main results of video grounding for LLMs are shown in
Table 2 and Table 3. We summarize our findings as follows.
Observation 1.
LLMs show preliminary abilities for
video grounding tasks, outperforming the VidLLMs.
On the one hand, all the VidLLMs we test are not as
good as the random method in completing the video ground-
ing tasks, which indicates that the current VidLLMs are still
far from satisfying video temporal understanding, and more
temporal-related video tasks should be added to further fine-
tune these model.
On the other hand, although some combination methods
of LLMs and visual model we tried cannot outperform the
random method, on average, GPT-3.5 has shown better per-
formance improvement over the VidLLMs and random re-
sults, indicating that LLMs are indeed able to understand
the visual description and questions for video grounding
and use the corresponding temporal information to provide
reasonable answers. Our combination of LLMs and visual
models has been proven to be effective. Overall, we can
find that LLMs have the ability of temporal information un-
derstanding.
Observation 2. Different combinations of visual descrip-
tion generators, LLMs, and prompt designs, can signifi-
cantly affect the recall rate of video grounding
As shown in Table 2, using the same valid rate as the
evaluation metrics, we can see a huge difference in video
grounding performance when changing the visual descrip-
tion generators, LLMs, and prompt designs.
For exam-
ple, compared with Vicuna-7B using zero-shot prompts and
the Fc model, GPT-3.5 using the VQA model of Blip and
one-shot with confidence judgment prompts has a signif-
icantly better performance in conducting video grounding
tasks (from 25.83 to 33.87, with a performance difference
of more than 30%). However, considering that the current
video grounding model has higher performance in the same
dataset (for instance, R@1 Iou=0.5 could achieve more than
40 [46]), these results show that it is worth further studying
and analyzing the impact of different models and methods
to better reveal their impact on the results of video ground-
ing using LLMs for achieving higher performance.
4.3. Results with Different LLMs
We compared different LLMs, including GPT-3.5, Vicuna-
7B, Longchat-7B, and some VidLLMs such as Video-Chat,
Video-ChatGPT, and Video-LLaMA. For normal LLMs, we
used the aforementioned combination of LLMs and visual
descriptions to complete the video grounding task.
For
VidLLMs, we directly asked them to read the correspond-
ing video content and answer the video grounding question.
The final results are shown in Table 4, and we can draw the
following conclusion based on this.
Observation 3. LLMs’ ability to complete video ground-
ing tasks not only depends on the model scale but is also
related to the models’ ability of handling long sequence
question answers.
As shown in Table 2 and 4, we can clearly see that GPT-
3.5 achieves higher results in video grounding tasks than
Vicuna-7B and Longchat-7B in most cases, indicating that
larger LLM can perform better in video grounding tasks.
As for the performance difference between small-size
LLMs, although Longchat and Vicuna are both finetuned
from LLaMA [37], we can see from the table that in most
cases (i.e. using different visual models and prompt meth-
ods), Longchat-7B shows better results than Vicuna-7B in
video grounding under the same conditions (Vicuna-7B is
even worse than random results in many circumstances).
The main reason may be that the prompt we input for video
grounding usually has thousands or even nearly 10000 to-
kens, while the Longchat-7B model has extra condensing
rotary embeddings and finetuning for long-context data,
showing better long-context capability than Vicuna.
Valid Rate
IoU=0.3
IoU=0.5
IoU=0.7
GPT-3.5
33.87
11.80
4.22
Vicuna-7B
23.63
9.76
3.15
Longchat-7B
24.57
10.91
3.92
Video-Chat
9.03
3.31
1.26
Video-ChatGPT
20.00
7.69
1.75
Video-LLaMA
10.38
3.84
0.91
Random
23.26
9.06
2.88
Table 4. The overall best performance on the video grounding with
different LLMs.
6
### Page 7

4.4. Results with Different Visual Models
We compare the results in completing video grounding
tasks when receiving visual descriptions generated by dif-
ferent generators, and we have observations as follows:
Observation 4. General advanced caption models as vi-
sual description models do not guarantee a performance
boost in helping LLMs conduct video grounding tasks.
As shown in Table 2 and 5, some advanced caption meth-
ods, such as Blip, as visual description generators with
higher CIDEr value, may achieve higher performance than
other methods in a few evaluation metrics. Generally, it
can increase the number of cases with IoU ≥0.3, which
shows that a more efficient caption description of video con-
tent, to some extent, can better activate LLMs’ ability to
capture key content and conduct spatiotemporal reasoning.
However, no caption methods as visual models consistently
achieve the best performance on all the evaluation metrics,
even for the well-known model that obtained high perfor-
mance of image caption. This result calls for the need to
design a more fine-grained caption model to describe the
video content second by second in detail.
Valid Rate
IoU=0.3
IoU=0.5
IoU=0.7
CIDEr
Fc
25.83
9.68
3.17
1.053
Att2in
28.23
11.34
3.17
1.195
Transformer
26.32
10.62
3.25
1.303
Updown
25.13
10.91
3.92
1.239
Blip
30.67
11.26
3.84
1.335
Blip(VQA)
33.87
11.80
4.22
-
Table 5. The overall best performance on the video grounding with
different visual models. CIDEr represents a metric for measuring
models’ captioning capability [39]. Generally speaking, caption
models with higher CIDEr values are supposed to exhibit better
caption capabilities.
Observation 5. Introducing additional query informa-
tion into the description of video content can signifi-
cantly improve the ability of LLMs to conduct video
grounding, even with a small amount of additional in-
formation.
In the process of designing visual description genera-
tors, although we mostly use caption-based generators for
descriptions, they occasionally fail to include keywords of
grounding query.
Thereby, we also introduce the VQA-
based generator to enhance the description, since the answer
to ‘Is it currently happening <query event> in the image’
is strongly related to the <query event>, bringing extra in-
formation. Through our observation, with the addition of
VQA information, the LLMs have achieved improvements
in most metrics of video grounding, indicating that we still
have significant potential for improvement in visual descrip-
tion generator design by introducing incremental informa-
tion.
4.5. Results with Different Prompting Methods
As shown in Table 2 and 6, we make comparisons with dif-
ferent prompting methods, which include zero-shot prompt-
ing and one-shot prompting. Compared to the zero-shot
method, the one-shot prompting method additionally adds
exemplars for video grounding tasks. We can see that when
the one-shot prompt method and the zero-shot method us-
ing different visual models are input to different LLMs, the
presence or absence of example can not decisively improve
the effect of video grounding, and different LLMs show dif-
ferent degrees of sensitivity to them.
In order to further explore whether the prompt design
can help LLMs complete the video grounding task more ef-
fectively, and in response to the situation where visual de-
scription information sometimes appears vague and cannot
accurately guide LLMs and humans in video grounding, we
design a judgment guidance prompt that allows LLMs to
consider whether the given information is suitable for video
grounding before the prediction, and we can have the fol-
lowing observations.
Valid Rate
IoU=0.3
IoU=0.5
IoU=0.7
Zero-shot
25.97
10.91
3.47
One-shot
26.02
10.91
3.04
One-shot
Confidence judgment
33.87
11.80
4.22
Table 6. The overall best performance on the video grounding with
different prompting methods.
Observation 6. The prompting method of instructing
LLMs to separately judge the predictability and in-
fer results can significantly improve the performance of
video grounding.
As shown in Table 6, comparing different one-shot
prompt methods, there are only a few differences between
the two methods (i.e., the one-shot with confidence judg-
ment prompt has an additional sentence ‘judge whether the
description sequence is suitable for the video grounding’),
which leads to a significant change in the prediction effect
of video grounding, and the confidence gadget significantly
improves the prediction recall, from 26.02 to 33.87. We
analyze the reasons for the improvement, which may stem
from LLMs directly giving answers of ‘unpredictable’ in
some cases with low predictability. However, this does not
mean that the description sequence generated by the visual
model is completely unable to be used for video grounding
tasks. In this case, our prompt with confidence judgment
can better instruct LLMs to infer video grounding results
based on existing information (and we will provide similar
examples in the following case analysis section).
7
### Page 8

L
L
M
Find the start time and end time of the query below from the video.
Query: person is putting dishes on shelf
0.0s: a man standing in a kitchen next to a sink
1.0s: a man standing in a kitchen next to a sink
2.0s: a man standing in a kitchen next to a stove top oven
…
14.0s: a man standing in a kitchen holding a plate
15.0s: a man in striped shirt holding a white frisbee
16.0s: a man in striped shirt holding a white plate
17.0s: a man in striped shirt holding a white plate
18.0s: a man standing in a kitchen next to a counter
…
31.0s: a person standing in a room next to a table
Based on the given caption, it is not possible to determine the 
grounding time for the query “person is putting dishes on shelf”.
(d)
L
L
M
Find the start time and end time of the query below from the video.
Query: person opens the door
0.0s: a white door in a room with a blue floor
…
6.0s: a man standing in front of a door holding a plate
7.0s: a man standing in front of a white door
8.0s: a man standing in front of a door talking on a cell phone
9.0s: a man standing in front of a door
10.0s: a man standing in front of a closet
11.0s: a man standing in front of a closet
12.0s: a man standing in front of a door
13.0s: a man standing in a doorway with his hands in his pockets
…
20.0s: a man is taking a picture of himself in the mirror
0007-0012
(b)
L
L
M
Find the start time and end time of the query below from the video.
Query: person puts the pillow down
0.0s: a living room filled with furniture and pictures on the wall
1.0s: a living room filled with furniture and pictures on the wall
…
16.0s: a woman sitting on a couch in a living room
…
24.0s: a woman sitting in a chair in a living room
…
27.0s: a living room filled with furniture and decor
28.0s: a living room filled with furniture and pictures
29.0s: a woman sitting on a couch with a cat in her lap
30.0s: a woman sitting on a couch in a living room
Based on the given caption, it is not possible to determine the 
grounding time for the query “person puts the pillow down”.
(c)
L
L
M
Find the start time and end time of the query below from the video.
Query: a person takes a vacuum
0.0s: a man standing in a living room holding a vacuum
1.0s: a man is using a vacuum in a living room
2.0s: a man is cleaning a living room with a vacuum
3.0s: a man standing in a living room next to a table
4.0s: a man standing in a living room holding a wii mote
5.0s: a man standing in a living room with a vacuum
6.0s: a man in a living room vacuuming a couch
7.0s: a man standing in a living room next to a couch
8.0s: a man standing in a living room next to a couch
…
23.0s: a man in a white shirt and black shorts
…
0000-0006
(a)
Figure 3. Example cases of LLMs conducting video grounding task, (a) and (b) are successful cases, while (c) and (d) are failure cases,
since LLMs give the answer ‘Based on the given caption, it is not possible to determine the grounding time for the query’. The text with
a blue background represents positive for grounding answers, while the text with a red background represents negative for grounding
answers, although it might be related to the query.
4.6. Examples and Case Analysis
In Figure 3, we present four prompt examples for LLMs to
complete video rounding, as shown in Figure 3, including
successful and failed examples. Based on these actual cases,
we can draw the following observations.
Observation 7. LLMs infer from the actually received
information and complete the video grounding task,
rather than randomly guessing
In Figure 3(a), the visual description for the video di-
rectly mentions the keyword ‘vacuum’ in the initial descrip-
tion sequence, ensuring that LLMs can easily infer when ‘a
person takes a vacuum’ occurs; In Figure 3(b), although the
visual description sequence did not directly mention the ac-
tion of ‘open the door’, it concentrates on mentioning the
word-door for a period of time, which helps LLMs effec-
tively infer the start and end time of the video grounding
task based on the occurrence of ‘a man’ in the descrip-
tion. These successful cases demonstrate that LLMs have
the ability to infer video grounding answers based on corre-
sponding textual information while generating effective vi-
sual descriptions for videos. However, in some cases, LLMs
are unable to complete the visual grounding task according
to the description of the visual description sequence for dif-
ferent reasons, and LLMs would respond ‘ it’s not possi-
ble to determine the grounding time of the query’. These
failed cases and successful cases prove that LLMs are in-
deed trying to infer the answer of video grounding instead
of randomly guessing.
Observation 8. The reason for the failure case is mainly
from the vague description of the visual models, and
the secondary one is the insufficient reasoning ability of
LLMs in the case of weak information.
The reasons for the failure cases of video grounding
mainly lie in the incomplete visual description and the key
information not mentioned. As shown in Figure 3(c), due to
the lack of keyword ‘pillow’ mentioned in the visual de-
scription sequence, LLMs cannot effectively confirm the
start and end time of the query ‘person puts the pilot down’.
On the other hand, due to the fuzziness of the description
8
### Page 9

for the video generated by the caption model, it will increase
the reasoning difficulty for LLMs. As shown in Figure 3(d),
although the ‘plate’ and ‘kitchen’ mentioned in the descrip-
tion sequence can be seen to be highly correlated with the
‘dishes’ mentioned in the query, LLMs still gave the answer
‘impossible for grounding’, which shows that the reasoning
ability of LLMs in the case of weak information still need
to be strengthened.
5. Conclusion
In this paper, we propose LLM4VG, a comprehensive
benchmark that systematically evaluates the performance
of different LLMs on the video grounding task, with our
proposed combination prompting method of various vi-
sual models and LLMs for video grounding. We evaluate
and analyze the performances using different visual mod-
els, LLMs, and prompting methods.
Our evaluation re-
sults demonstrate that the existing VidLLMs are still far
from satisfying video temporal understanding, requiring
temporal training tasks. The combination of visual models
and LLMs shows preliminary abilities for video grounding
tasks, achieving higher performance than VidLLMs. We
conclude that more fine-grained visual models and prompt-
ing methods with further guidance of instructions are re-
quired to help LLMs better conduct video grounding tasks.
References
[1] Peter Anderson, Xiaodong He, Chris Buehler, Damien
Teney, Mark Johnson, Stephen Gould, and Lei Zhang.
Bottom-up and top-down attention for image captioning and
visual question answering. In Proceedings of the IEEE con-
ference on computer vision and pattern recognition, pages
6077–6086, 2018. 3, 5
[2] Stanislaw Antol, Aishwarya Agrawal, Jiasen Lu, Margaret
Mitchell, Dhruv Batra, C Lawrence Zitnick, and Devi Parikh.
Vqa: Visual question answering. In Proceedings of the IEEE
international conference on computer vision, pages 2425–
2433, 2015. 5
[3] Hrishikesh Aradhye, George Toderici, and Jay Yagnik.
Video2text: Learning to annotate video content.
In 2009
IEEE International Conference on Data Mining Workshops,
pages 144–151. IEEE, 2009. 2
[4] Tom Brown, Benjamin Mann, Nick Ryder, Melanie Sub-
biah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakan-
tan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Lan-
guage models are few-shot learners. Advances in neural in-
formation processing systems, 33:1877–1901, 2020. 5
[5] Thomas Carta, Cl´ement Romac, Thomas Wolf, Sylvain Lam-
prier, Olivier Sigaud, and Pierre-Yves Oudeyer. Grounding
large language models in interactive environments with on-
line reinforcement learning. In Proceedings of the 40th Inter-
national Conference on Machine Learning. JMLR.org, 2023.
1
[6] Guo Chen, Yin-Dong Zheng, Jiahao Wang, Jilan Xu, Yifei
Huang, Junting Pan, Yi Wang, Yali Wang, Yu Qiao, Tong
Lu, et al. Videollm: Modeling video sequence with large
language models. arXiv preprint arXiv:2305.13292, 2023. 6
[7] Houlun Chen, Xin Wang, Xiaohan Lan, Hong Chen,
Xuguang Duan, Jia Jia, and Wenwu Zhu.
Curriculum-
listener:
Consistency-and complementarity-aware audio-
enhanced temporal sentence grounding.
In Proceedings
of the 31st ACM International Conference on Multimedia,
pages 3117–3128, 2023. 3
[8] Jingyuan Chen, Xinpeng Chen, Lin Ma, Zequn Jie, and Tat-
Seng Chua. Temporally grounding natural sentence in video.
In Proceedings of the 2018 conference on empirical methods
in natural language processing, pages 162–171, 2018. 2
[9] Wei Feng, Haoyang Li, Xin Wang, Xuguang Duan, Zi Qian,
Wu Liu, and Wenwu Zhu. Multimedia cognition and evalu-
ation in open environments. In Proceedings of the 1st Inter-
national Workshop on Multimedia Content Generation and
Evaluation: New Methods and Practice, pages 9–18, 2023.
1
[10] Luciano Floridi and Massimo Chiriatti. Gpt-3: Its nature,
scope, limits, and consequences. Minds and Machines, 30:
681–694, 2020. 2
[11] Valentin Gabeur, Chen Sun, Karteek Alahari, and Cordelia
Schmid.
Multi-modal transformer for video retrieval.
In
Computer Vision–ECCV 2020: 16th European Conference,
Glasgow, UK, August 23–28, 2020, Proceedings, Part IV 16,
pages 214–229. Springer, 2020. 2
[12] Jiyang Gao, Chen Sun, Zhenheng Yang, and Ram Nevatia.
Tall: Temporal activity localization via language query. In
Proceedings of the IEEE international conference on com-
puter vision, pages 5267–5275, 2017. 4, 6
[13] Jiaxian Guo, Junnan Li, Dongxu Li, Anthony Meng Huat
Tiong, Boyang Li, Dacheng Tao, and Steven Hoi. From im-
ages to textual prompts: Zero-shot visual question answer-
ing with frozen large language models. In Proceedings of
the IEEE/CVF Conference on Computer Vision and Pattern
Recognition, pages 10867–10877, 2023. 1, 2
[14] Dongliang He, Xiang Zhao, Jizhou Huang, Fu Li, Xiao Liu,
and Shilei Wen.
Read, watch, and move: Reinforcement
learning for temporally grounding natural language descrip-
tions in videos. In Proceedings of the AAAI Conference on
Artificial Intelligence, pages 8393–8400, 2019. 2
[15] De-An Huang, Vignesh Ramanathan, Dhruv Mahajan,
Lorenzo Torresani,
Manohar Paluri,
Li Fei-Fei,
and
Juan Carlos Niebles.
What makes a video a video: An-
alyzing temporal information in video understanding mod-
els and datasets.
In Proceedings of the IEEE Conference
on Computer Vision and Pattern Recognition, pages 7366–
7375, 2018. 2
[16] Takeshi Kojima, Shixiang Shane Gu, Machel Reid, Yutaka
Matsuo, and Yusuke Iwasawa. Large language models are
zero-shot reasoners.
Advances in neural information pro-
cessing systems, 35:22199–22213, 2022. 2
[17] Ranjay Krishna, Kenji Hata, Frederic Ren, Li Fei-Fei, and
Juan Carlos Niebles. Dense-captioning events in videos. In
Proceedings of the IEEE international conference on com-
puter vision, pages 706–715, 2017. 11
[18] Li KunChang, He Yinan, Wang Yi, Li Yizhuo, Wang Wen-
hai, Ping Luo, Wang Yali, Wang Limin, and Qiao Yu.
9
### Page 10

Videochat: Chat-centric video understanding. arXiv preprint
arXiv:2305.06355, 2023. 1, 2, 5, 6
[19] Xiaohan Lan, Yitian Yuan, Xin Wang, Zhi Wang, and
Wenwu Zhu. A survey on temporal sentence grounding in
videos. ACM Transactions on Multimedia Computing, Com-
munications and Applications, 19(2):1–33, 2023. 2
[20] Dongxu Li, Junnan Li, Hung Le, Guangsen Wang, Silvio
Savarese, and Steven C.H. Hoi. LAVIS: A one-stop library
for language-vision intelligence. In Proceedings of the 61st
Annual Meeting of the Association for Computational Lin-
guistics (Volume 3: System Demonstrations), pages 31–41,
Toronto, Canada, 2023. Association for Computational Lin-
guistics. 3, 5
[21] Dacheng Li*, Rulin Shao*, Anze Xie, Ying Sheng, Lianmin
Zheng, Joseph E. Gonzalez, Ion Stoica, Xuezhe Ma, and Hao
Zhang.
How long can open-source llms truly promise on
context length?, 2023. 5, 6
[22] Guang Li, Linchao Zhu, Ping Liu, and Yi Yang.
Entan-
gled transformer for image captioning. In Proceedings of
the IEEE/CVF international conference on computer vision,
pages 8928–8937, 2019. 3, 5
[23] Junnan Li, Dongxu Li, Caiming Xiong, and Steven Hoi.
Blip: Bootstrapping language-image pre-training for uni-
fied vision-language understanding and generation. In In-
ternational Conference on Machine Learning, pages 12888–
12900. PMLR, 2022. 3, 5
[24] Pengfei Liu, Weizhe Yuan, Jinlan Fu, Zhengbao Jiang, Hi-
roaki Hayashi, and Graham Neubig. Pre-train, prompt, and
predict: A systematic survey of prompting methods in nat-
ural language processing. ACM Computing Surveys, 55(9):
1–35, 2023. 5
[25] Ruotian Luo. Goal-driven text descriptions for images. arXiv
preprint arXiv:2108.12575, 2021. 3
[26] Ruotian Luo, Brian Price, Scott Cohen, and Gregory
Shakhnarovich. Discriminability objective for training de-
scriptive captions. In Proceedings of the IEEE conference on
computer vision and pattern recognition, pages 6964–6974,
2018. 3, 5
[27] Bonan Min, Hayley Ross, Elior Sulem, Amir Pouran Ben
Veyseh, Thien Huu Nguyen, Oscar Sainz, Eneko Agirre,
Ilana Heintz, and Dan Roth. Recent advances in natural lan-
guage processing via large pre-trained language models: A
survey. ACM Computing Surveys, 56(2):1–40, 2023. 2
[28] Salman Khan Muhammad Maaz, Hanoona Rasheed and
Fahad Khan.
Video-chatgpt: Towards detailed video un-
derstanding via large vision and language models.
ArXiv
2306.05424, 2023. 2, 5, 6
[29] Guoshun Nan, Rui Qiao, Yao Xiao, Jun Liu, Sicong Leng,
Hao Zhang, and Wei Lu.
Interventional video ground-
ing with dual contrastive learning.
In Proceedings of
the IEEE/CVF conference on computer vision and pattern
recognition, pages 2765–2775, 2021. 2
[30] OpenAI. Openai: Introducing chatgpt, 2022. 5, 6
[31] OpenAI.
Gpt-4 technical report.
arXiv preprint
arXiv:2303.08774, 2023. 2
[32] Long Ouyang, Jeffrey Wu, Xu Jiang, Diogo Almeida, Car-
roll Wainwright, Pamela Mishkin, Chong Zhang, Sandhini
Agarwal, Katarina Slama, Alex Ray, et al.
Training lan-
guage models to follow instructions with human feedback.
Advances in Neural Information Processing Systems, 35:
27730–27744, 2022. 2
[33] Alec Radford, Karthik Narasimhan, Tim Salimans, Ilya
Sutskever, et al. Improving language understanding by gen-
erative pre-training. 2
[34] Steven J Rennie, Etienne Marcheret, Youssef Mroueh, Jerret
Ross, and Vaibhava Goel. Self-critical sequence training for
image captioning. In Proceedings of the IEEE conference on
computer vision and pattern recognition, pages 7008–7024,
2017. 3, 5
[35] Gunnar A Sigurdsson, G¨ul Varol, Xiaolong Wang, Ali
Farhadi, Ivan Laptev, and Abhinav Gupta.
Hollywood in
homes: Crowdsourcing data collection for activity under-
standing.
In Computer Vision–ECCV 2016: 14th Euro-
pean Conference, Amsterdam, The Netherlands, October 11–
14, 2016, Proceedings, Part I 14, pages 510–526. Springer,
2016. 6
[36] Mattia Soldan, Mengmeng Xu, Sisi Qu, Jesper Tegner, and
Bernard Ghanem.
Vlg-net: Video-language graph match-
ing network for video grounding.
In Proceedings of the
IEEE/CVF International Conference on Computer Vision,
pages 3224–3234, 2021. 2
[37] Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier
Martinet, Marie-Anne Lachaux, Timoth´ee Lacroix, Baptiste
Rozi`ere, Naman Goyal, Eric Hambro, Faisal Azhar, et al.
Llama:
Open and efficient foundation language models.
arXiv preprint arXiv:2302.13971, 2023. 6
[38] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszko-
reit, Llion Jones, Aidan N Gomez, Łukasz Kaiser, and Illia
Polosukhin. Attention is all you need. Advances in neural
information processing systems, 30, 2017. 3
[39] Ramakrishna Vedantam, C Lawrence Zitnick, and Devi
Parikh. Cider: Consensus-based image description evalua-
tion. In Proceedings of the IEEE conference on computer
vision and pattern recognition, pages 4566–4575, 2015. 7
[40] Xin Wang, Xiaohan Lan, and Wenwu Zhu. Video ground-
ing and its generalization. In Proceedings of the 30th ACM
International Conference on Multimedia, pages 7377–7379,
2022. 1
[41] Chiang Wei-Lin, Li Zhuohan, Lin Zi, Sheng Ying, Wu
Zhanghao, Zhang Hao, Zheng Lianmin, Zhuang Siyuan,
Zhuang Yonghao, Gonzalez Joseph E., Stoica Ion, and
Xing Eric P. Vicuna: An open-source chatbot impressing
gpt-4 with 90%* chatgpt quality, 2023. 5, 6
[42] Huijuan Xu, Kun He, Bryan A Plummer, Leonid Sigal, Stan
Sclaroff, and Kate Saenko.
Multilevel language and vi-
sion integration for text-to-clip retrieval. In Proceedings of
the AAAI Conference on Artificial Intelligence, pages 9062–
9069, 2019. 2
[43] Antoine Yang, Antoine Miech, Josef Sivic, Ivan Laptev, and
Cordelia Schmid. Tubedetr: Spatio-temporal video ground-
ing with transformers. In Proceedings of the IEEE/CVF Con-
ference on Computer Vision and Pattern Recognition, pages
16442–16453, 2022. 2
[44] Qinghao Ye, Haiyang Xu, Guohai Xu, Jiabo Ye, Ming Yan,
Yiyang Zhou, Junyang Wang, Anwen Hu, Pengcheng Shi,
10
### Page 11

Yaya Shi, et al.
mplug-owl: Modularization empowers
large language models with multimodality. arXiv preprint
arXiv:2304.14178, 2023. 1
[45] Yitian Yuan, Xiaohan Lan, Xin Wang, Long Chen, Zhi
Wang, and Wenwu Zhu. A closer look at temporal sentence
grounding in videos: Dataset and metric. In Proceedings of
the 2nd international workshop on human-centric multime-
dia analysis, pages 13–21, 2021. 2
[46] Runhao Zeng, Haoming Xu, Wenbing Huang, Peihao Chen,
Mingkui Tan, and Chuang Gan. Dense regression network
for video grounding. In Proceedings of the IEEE/CVF Con-
ference on Computer Vision and Pattern Recognition, pages
10287–10296, 2020. 2, 6
[47] Hang Zhang, Xin Li, and Lidong Bing. Video-llama: An
instruction-tuned audio-visual language model for video un-
derstanding. arXiv preprint arXiv:2306.02858, 2023. 1, 2,
5, 6
[48] Zeyang Zhang, Xin Wang, Ziwei Zhang, Haoyang Li, Yijian
Qin, Simin Wu, and Wenwu Zhu. Llm4dyg: Can large lan-
guage models solve problems on dynamic graphs?
arXiv
preprint arXiv:2310.17110, 2023. 1
[49] Zhuosheng Zhang,
Aston Zhang,
Mu Li,
Hai Zhao,
George Karypis, and Alex Smola.
Multimodal chain-of-
thought reasoning in language models.
arXiv preprint
arXiv:2302.00923, 2023. 1
[50] Denny Zhou, Nathanael Sch¨arli, Le Hou, Jason Wei, Nathan
Scales, Xuezhi Wang, Dale Schuurmans, Claire Cui, Olivier
Bousquet, Quoc Le, et al. Least-to-most prompting enables
complex reasoning in large language models. arXiv preprint
arXiv:2205.10625, 2022. 2
[51] Wenwu Zhu, Xin Wang, and Wen Gao. Multimedia intelli-
gence: When multimedia meets artificial intelligence. IEEE
Transactions on Multimedia, 22(7):1823–1835, 2020. 2
6. Supplementary matierals
As shown in Table 7, we provide the extra experiment of
LLMs’ video grounding performance on the ActivityNet-
Captions dataset [17], which shares many similar trends
compared to the Charades-STA dataset.
Table 7. Performance of video grounding on ActivityNet-Captions
dataset with different Large Language Models.
Valid Rate
IoU=0.3
IoU=0.5
IoU=0.7
Video-Chat
8.8
3.7
1.5
Video-LLaMA
6.9
2.1
0.8
Video-ChatGPT
26.4
13.6
6.1
Vicuna
17.37
8.26
2.94
Longchat
19.78
9.45
3.35
GPT-3.5
33.51
14.97
7.43
11