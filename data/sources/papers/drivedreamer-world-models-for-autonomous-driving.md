# DriveDreamer World Models for Autonomous Driving

**Source**: arxiv PDF, 13 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Towards Safer Operations: An Expert-involved Dataset of High-Pressure
Gas Incidents for Preventing Future Failures
Shumpei Inoue1, Minh-Tien Nguyen1,2,∗, Hiroki Mizokuchi1, Tuan-Anh D. Nguyen1,
Huu-Hiep Nguyen1, Dung Tien Le1
1Cinnamon AI, 10th floor, Geleximco building, 36 Hoang Cau, Dong Da, Hanoi, Vietnam.
{sinoue, ryan.nguyen, hmizokuchi, tadashi, hubert, nathan}@cinnamon.is
2Hung Yen University of Technology and Education, Hung Yen, Vietnam.
tiennm@utehy.edu.vn
Abstract
This paper introduces a new IncidentAI dataset
for safety prevention. Different from prior cor-
pora that usually contain a single task, our
dataset comprises three tasks: named entity
recognition, cause-effect extraction, and infor-
mation retrieval. The dataset is annotated by
domain experts who have at least six years of
practical experience as high-pressure gas con-
servation managers. We validate the contri-
bution of the dataset in the scenario of safety
prevention. Preliminary results on the three
tasks show that NLP techniques are beneficial
for analyzing incident reports to prevent future
failures. The dataset facilitates future research
in NLP and incident management communities.
The access to the dataset is also provided.1
1
Introduction
Daily activities usually face incidents that can sig-
nificantly affect risk management. In specific in-
dustries such as manufacturing, an incident can
make a significant consequence that not only re-
duces the reputation of companies but also breaks
the product chain and costs a lot of money. It mo-
tivates the introduction of the safety-critical area
where AI solutions have been proposed to prevent
repeated failures from historical samples (Yampol-
skiy, 2019; McGregor, 2021; Durso et al., 2022;
Nor et al., 2022; Chandra et al., 2023; Tikayat Ray
et al., 2023; Andrade and Walsh, 2023).
There still exists a gap in the adoption of AI tech-
niques for actual incident management scenarios
due to the lack of high-quality annotated datasets.
The main challenges arise from two main reasons.
First, data annotation of incidents for AI-related
tasks is a labor-expensive and time-consuming task
that requires domain experts who have a deep un-
derstanding and excellent experience in their daily
∗Corresponding Author.
1The IncidentAI dataset is available at: https://github.
com/Cinnamon/incident-ai-dataset
work. Second, the collection of historical incidents
is also challenging due to its dependence on the
policies of companies. We argue that the growth
of the safety-critical area can be leveraged by intro-
ducing annotated incident datasets.
To fill the gap, this paper takes the high-pressure
gas domain, a sector of the gas industry, as a case
study. This is because gas and its products are the
major industry in the energy market that play an
influential role in the global economy (Mokhatab
et al., 2018; Pellegrini et al., 2019). In addition,
a gas incident may cost a lot of money with sig-
nificant consequences. The detection and analysis
of past incidents are crucial for improving safety
prevention and avoiding future failures. Figure 1
shows the scenario of the detection and analysis.
The description of an occurred incident is noted
in an incident report. Then, important information
(named entity and cause-effect extraction) from the
incident report is extracted and stored in an inci-
dent database. In operation, given the description
of an incident, the manager can search historical
incidents for potential risk analyses. The system
alerts the worker by showing historically relevant
incidents and cause-effect information based on as-
signed tasks. The worker can use suggested infor-
mation for failure analysis to avoid future incidents.
In practice, given an incident report, workers, man-
agers, or analyzers would like to know: (i) which
aspects (entities) are relevant to the incident?, (ii)
what is the cause and effect of the incident?, (iii)
and which are historically relevant incidents of the
current incident for risk and failure analyses?
To address the aforementioned questions, this pa-
per introduces a new Japanese dataset that focuses
on high-gas incidents and demonstrates the poten-
tial NLP applications in analyzing high-gas inci-
dent reports. To do that, we first work closely with
business members and domain experts to identify
three potential NLP tasks: named entity recogni-
tion (NER), cause-effect extraction (CE), and infor-
arXiv:2310.12074v2  [cs.CL]  23 Oct 2023
### Page 2

Incident
occurance
Incident
reports
AI (IE)
Incident DB
(structured)
Operation manager
Incident
description
AI (Search)
Searching
Historic
incidents
Alert
Suggest
Searching
Extract
NER, CE
Cause-
effect
Worker
Figure 1: The scenario of IncidentAI in actual business cases. CE stands for cause-effect extraction.
mation retrieval (IR) based on actual scenarios. The
NER task allows analyzers to extract fundamental
units of an incident in the form of entities, e.g., the
product or the process of the product. This informa-
tion is used to visualize statistics concerning key
entities from past incidents retrieved through IR
steps. The CE task allows analyzers to extract the
cause and effect of an incident. The IR task is typi-
cally used to examine historical incidents similar
to the current one and to develop countermeasures
to prevent the recurrence of such incidents. In busi-
ness scenarios, information from the three tasks is
vital for safety-critical and risk management. This
paper makes three main contributions as follows.
• It introduces a new IncidentAI dataset that
focuses on high-gas incidents for NER, CE,
and IR. To the best of our knowledge, this is
the first Japanese dataset that covers all three
tasks in the context of high-gas incidents. It is
annotated by domain experts to ensure a high-
quality dataset that can assist in the efficient
analysis of incident reports using AI models.
• It shows a scenario of IncidentAI in actual
business cases. The scenario can serve as a
reference for AI companies that are also inter-
ested in the analysis of incident reports.
• It benchmarks the results of AI models on
NER, CE, and IR tasks that facilitate future
studies in NLP and safety prevention areas.
2
Related Work
Incident databases
There exist industry-specific
incident databases in many industries (NTSB,
2017). The databases contain a wide range of inci-
dents such as cyber-security vulnerabilities and ex-
posures (Corporation, 2023), aviation reports that
contain accident and incident information of air
flights (Administration, 2023), or reports of the
pharmaceutical industry, healthcare providers, and
consumers (Food and Administration, 2023). Re-
cently, an AIID database (AI Incident Database)
was introduced (McGregor, 2021). It indexes more
than 1,000 publicly available incident reports. The
existing databases allow the storage of incident in-
formation, yet simple AI techniques (simple match-
ing or classification) create a gap to analyze the
incidents. We leverage safety operations by intro-
ducing a new dataset that includes three main tasks:
NER, cause-effect extraction, and IR. It facilitates
the adoption of AI to prevent future failures in the
context of high-pressure gas incidents.
NLP techniques
have been applied to analyze
incident reports (McGregor, 2021; McGregor et al.,
2022; Pittaras and McGregor, 2022; Hong et al.,
2021; Nor et al., 2022; Macrae, 2022; Durso et al.,
2022; Shrishak, 2023; Nor et al., 2022). The meth-
ods range from indexing for incident databases
(McGregor, 2021; McGregor et al., 2022; Pittaras
and McGregor, 2022) to deeper analyses using ma-
chine learning (Durso et al., 2022; Nor et al., 2022;
Chandra et al., 2023). Recently, BERT (Devlin
et al., 2019) has been adapted to aviation safety
(Chandra et al., 2023; Tikayat Ray et al., 2023;
Andrade and Walsh, 2023; Jing et al., 2023). The
recent survey also shows the role of NLP in avia-
tion safety (Yang and Huang, 2023). We share the
direction of using NLP techniques in the analysis
of incident reports. However, instead of focusing
on single tasks, we are interested in three differ-
ent tasks: NER, CE, and IR, that provide critical
information for safety prevention. In addition, we
provide a Japanese dataset to facilitate the creation
of AI pipelines in a low-resource language.
3
The HPGIncident Dataset
3.1
Data Collection
The original dataset was collected from publicly
available reports of high-gas incidents published
in 2022 by the High-Pressure Gas Safety Institute
### Page 3

of Japan.2 The original data contains descriptions
of incidents, types of incidents, dates of incidents,
industries, etc. From the original 18,171 incident
cases, 2,159 cases belonging to three industries:
“general chemistry", “petrochemical", and “oil re-
fining" were first extracted. These cases were used
for the annotation of IR. Subsequently, we selected
970 cases from that 2,159 cases based on the most
recent dates for both the annotation of NER and
CE tasks. We used the description of incidents as
the input for annotation shown in the next section.
3.2
The Annotation Process
The dataset was created by three Japanese domain
experts, each with at least six years of practical
experience as high-pressure gas conservation man-
agers. These experts possess qualifications as high-
pressure gas production safety managers, a national
certification demonstrating a certain level of knowl-
edge and experience necessary to ensure the safety
of high-pressure gas manufacturing facilities.
The process was divided into two steps: the cre-
ation of the guideline and the annotation of the
entire dataset. In the first step, we randomly se-
lected 100 samples from 970 collected samples for
NER and CE, and from 2,159 collected samples for
IR. Our team collaborated closely with experts to
establish criteria for consistent annotations, includ-
ing identifying the information types (entities) and
their definitions for NER and CE, and determin-
ing the attributes that characterize incidents for IR.
These criteria formed the basis of our guidelines.
This initial stage was iterative, conducted in several
rounds until a certain agreement score was achieved
among the experts. This process played a vital
role in training the annotators, ensuring that they
shared a uniform understanding of the guidelines.
Once a high agreement score had been achieved,
the remaining samples were apportioned into three
segments, each corresponding to an annotator, who
then proceeded to annotate their respective parts.
Subsequently, 100 random samples were selected
from one annotator’s portion. The other two annota-
tors were tasked with annotating these 100 samples.
For each task, NER, CE, and IR, an inter-annotator
agreement was computed using these 100 samples.
Due to space constraints, please refer to Appendix
A for a more detailed explanation of annotation.
NER annotation
As mentioned, entities provide
basic information about an incident. This repre-
2https://shorturl.at/BLWX6
sents the first tier in the incident report analysis.
The initial step of NER annotation involves iden-
tifying the set of entities. The identification was
carried out through meticulous coordination and
several meetings with domain experts. Built on
their insights and experiences, six critical entity
types for incident analysis were established: Prod-
ucts, Chemicals, Storage, Incidents, Processes,
and Tests. Table 1 shows the definition of entities.
Table 1: The definition of entities.
Entity
Definition
Products
A noun phrase that mentions various gases. Gaseous state at normal
temperature and pressure. Do not tag items that are not general (things
that do not appear even if you search the Web). Examples: mixed gas;
flammable gas; refrigerant gas.
Chemicals
A noun phrase mentions chemical substances, reactants, and materials
(other than gases) used in gas generation and process management. Items
not included in the above Products. Examples: Benzene; Hydrocarbons.
Storage
General equipment where above Products and Chemicals come into con-
tact. (i) Include equipment such as supports and insulators. (ii) Include
expressions that indicate the entire plant or facility. (iii) Do not include
expressions indicating parts such as entrances and exits if they are placed
at the end of a word. Examples: tank; maturation furnace; refining tower;
dehumidification tower.
Incidents
A phrase mentions incidents that resulted in or caused an accident, regard-
less of severity. It includes only incidents that actually occurred, and do
not include situations that did not lead to an incident. Examples: seepage;
leakage; fire; serious injury; death.
Processes
A phrase mentions handling of gas, and unit operations related to gas. Ab-
normal processes are included in incidents. Examples: filling; distillation.
Tests
A phrase mention inspection devices and inspection actions outside the
production process line. Do not include inspection items such as XX
concentration. Examples: inspection; visual inspection; leak test.
The annotation of NER uses the definition of
entities in Table 1 and the rules mentioned in the
Appendix A.1. We observed two important points.
Firstly, the annotation was challenging even with
domain experts. In the first round of guideline cre-
ation, the agreement score was so low. After several
meetings, the agreement score was significantly
improved. It provides strong evidence for the adap-
tation of the whole NER dataset. After annotating
the whole NER dataset, the Fleiss’ Kappa score of
randomly cross-checking 100 other samples was
0.814, showing good agreement. Secondly, entities
are nested. It comes from the nature of data, for
example, a product can contain a chemical or a
process can include storage. An annotated exam-
ple of NER is shown in Figure 2 in the Appendix
A.1. Table 2 summarizes the statistics of the NER
dataset that follows the BIO format.
Cause-effect annotation
Causes and effects pro-
vide critical information about a given incident for
the analysis, in which causes contain information
about the cause of an incident and effects mention
the consequences of the causes. Similar to NER,
we engaged in detailed discussions with domain
experts to identify cause and effect types. We ob-
served that the cause is quite easy to identify while
the effect composes several types such as the leak-
### Page 4

Table 2: Statistics of the NER dataset.
Entity
Train
Test
All
Product
2,189
905
3,094
Chemical
1,440
576
2,016
Storage
5,881
2,251
8,132
Incident
5,274
2,045
7,319
Process
1,138
426
1,564
Test
1,615
572
2,187
#entities in total
17,537
6,775
24,312
#reports in total
700
270
970
age of gas, physical damages (explosion or fire),
human injuries caused by the incident, or others
(not related to leakage). After consulting, all the
types of the effect were considered as the effect of
an incident. Table 3 show CE’s definition and the
examples of cause and effect types.
Table 3: The guideline of CE annotation.
CE types
Definition
Event_Leak
(EL)
Tag sentences in which gas leakage can be directly confirmed.
However, automatic detection by equipment is not included due to
the possibility of malfunction. Human detection is included. The
definition of gas follows the NER Product. Example: Hydrogen
and aniline leakage.
Damage_Property
(DP)
Tag sentences that confirm physical damage to equipment or facil-
ities caused by Event_Leak and Event_others. Physical damage
includes burst pipes, destruction of heat exchangers, etc. Example:
Container ruptures.
Damage_Human
(DH)
Tag sentences that confirm Human casualties caused by
Event_Leak and Event_others and Damage_Property. Human
casualties include deaths, injuries, and physical illnesses. Exam-
ple: One employee injured left thigh and left ear.
Event_others
(EO)
Tag sentences containing accident events other than gas leakage.
For example, explosions, fires, etc. Example: It is estimated that
hydrogen, which has a low ignition energy, was ignited by static
electricity.
Cause
Tag sentences that confirm the event causing Event_Leak and
Event_others. Target not only direct causes but also indirect causes
(e.g., Cause’s Cause). In case of ignition or explosion, the three
elements of combustion (combustibles, oxygen, and heat) shall
be noted as a cause. Example: As a result of reduced tightening
torque in some of the flange sections cooled by hydrogen
The annotation of causes and effects is on the
span level. The annotation was done in two steps
(follows Section 3.2), in which the first step was
conducted in several rounds to create the annota-
tion guideline to annotate the whole CE dataset.
For annotation, the definition of causes and effects
in Table 3 and the rules in Appendix A.2 were used.
After creating the guideline with a high agreement
score, the guideline was adopted to annotate the
remaining 870 samples. Fleiss’ Kappa score of ran-
domly cross-checking 100 other samples was 0.764.
Table 4 shows the information of the CE dataset.
467 samples have cause-effect pairs. Others only
contain causes or effects. A sample of cause-effect
annotation is shown in Figure 3, Appendix A.2.
IR annotation
The objective of the IR annota-
tion task is to realize a use case where users can
Table 4: Statistics of the CE dataset.
Information type
Train
Test
All
Cause
1,073
396
1,469
Effect
1,063
400
1,463
#samples in total
700
270
970
#samples with CE pairs
467
—
—
query incident descriptions to retrieve relevant past
incidents. We found that the annotation of IR is
challenging to measure the similarity of incidents
by using single aspects, e.g., the description of in-
cidents. Therefore, instead of directly assigning a
relevance score to predefined levels like "Not Rele-
vant," "Relevant," and "Highly Relevant," we first
identified a set of key attributes to each incident
report and then evaluated relevance on an attribute-
by-attribute basis. The attributes allow us to reflect
the nature of similarity among incidents.
We collaborated with domain experts to iden-
tify crucial attributes for determining how similar
incident reports are. These specific attributes are
shown in Table 5. Each incident description was
annotated by assigning a relevant label to every
identified attribute. The relevance score among in-
cidents was measured by the degree of overlap in
their labels. This strategy offers two advantages: (i)
it provides a framework for a numeric evaluation
of the relevance among incidents and (ii) it allows
the flexible generation of relevance scores.
Table 5: The definitions of attributes and their labels.
Attribute
Label
#samples
Type of high
pressure gas
(a) Flammable or Flame Retardant Gas
911
(b) Toxic Gas
78
(c) Satisfies a & b
563
(d) Not applicable
607
Cause of
incident
(a) Equipment Factor
940
(b) Human Factor
598
(c) External Factor
67
(d) Other Factor
554
Incident result
(a) Leakage
1510
(b) Fires and explosions
337
(c) a & property damage
24
(d) a & human casualties
88
(e) b & property damage
47
(f) b & human casualties
78
(g) Property damage & human casualties
30
(h) Others
45
Time span from
cause to effect
(a) Sudden
364
(b) Long term
1238
(c) Unknown
557
Operational status
of equipment
(a) Steady-state operation
900
(b) Non-steady state operation
344
(c) During maintenance
409
(d) Other situations
506
In this study, we analyzed 2,159 high-pressure
gas incident reports, detailed in Section 3.1. We
employed a straightforward approach where each
attribute’s label overlap was scored as 1, and no
### Page 5

overlap received a score of 0. When labels were
jointly attributed through the use of ‘and’—for in-
stance, label (c) in the Incident Result type—the
overlap score was increased to 1.5. The final rele-
vance score was computed by summing these indi-
vidual overlap scores. Sample incident descriptions
and their corresponding relevance scores are pre-
sented in Figures 4 and 5, respectively. In this
schema, the incident description itself is used as
a query, and the goal of the retriever model is to
identify reports with high relevant scores. To as-
sess inter-annotator reliability, we evaluated the
consensus across 100 incident reports annotated
by three individuals. The resulting average Fleiss’
Kappa score was 0.541, denoting a moderate level
of agreement that is good enough for IR.
3.3
Quantitative Observation
This section shows the statistics of recent incident
databases and corpora. The databases include CVE
(Common Vulnerabilities and Exposures) (Corpo-
ration, 2023), FAA3 (Federal Aviation Administra-
tion and National Aeronautics and Space Adminis-
tration) (Administration, 2023), AIID4 (McGregor,
2021), and EF (explosion and fire) (NIOSH, 2023).
The corpora contain CFDC (high-level causes of
flight delays and cancellations) (Miyamoto et al.,
2022) and AIR (aviation incident reports) (Jiao
et al., 2022). We also note that there are quite a lot
of other incident databases and corpora but due to
space limitation, we could not show them all.
Table 6: Statistics of incident databases and corpora.
Manufac is Manufacturing and Lang is language.
Name
Samples Label
Problem
Domain
Lang
CVE
141076
No
IR
Security
EN
FAA
—
No
IR
Aviation
EN
AIID
2842
No
IR
Mix
EN
EF
6430
No
IR
Fire
JA
CFDC
4195
No
Clustering
Aviation
EN
AIR
1775
Yes
Classification
Aviation
CN
Ours
970
Yes
NER, CE, IR Manufac
JA
As observed, incident databases are usually de-
signed for IR in diverse sectors without clear labels.
Annotated corpora, e.g., AIR, are created for tar-
get problems with a smaller number of samples.
Our dataset contains a quite small number of sam-
ples. However, it has the human annotation of three
NLP tasks which are beneficial for the analysis of
incident reports. In addition, a small number of
3We could not know exactly the number of samples.
4https://incidentdatabase.ai
samples is still helpful in business scenarios for
training AI models by using transfer learning (De-
vlin et al., 2019; Nguyen et al., 2020, 2023).
4
NLP Tasks and Methodology
Once the dataset has been created, NLP tasks were
designed to establish the baselines of each task.
4.1
Nested Named Entity Recognition
The NER task was formulated as a sequence la-
beling problem (Ju et al., 2018; Rojas et al., 2022;
Zhang et al., 2022; Yan et al., 2022). Strong nested
NER models were selected as follows.
Layered nested NER
This model stacks flat
NER layers for nested NER (Ju et al., 2018). Each
flat layer composes of a BiLSTM layer to capture
the sequential context representation of an input
sequence and a cascaded CRF layer for labeling.
Multiple BiLSTM-CRF
This model uses mul-
tiple flat BiLSTM-CRF, one for each entity type
(Rojas et al., 2022). The input layer combines char-
acter embeddings and token representation from
Flair (Akbik et al., 2018) and BERT (Devlin et al.,
2019). The combined representation is fed into
BiLSTM layers to obtain long-contextual informa-
tion. Sequence labeling is done with CRF.
BINDER
is an optimized bi-encoder model for
NER by using contrastive learning (Zhang et al.,
2022). It formulates the NER task as a representa-
tion learning problem that maximizes the similarity
between an entity mention and its type.
CNN-Nested-NER
It is a simple but effective
model for nested NER (Yan et al., 2022). It uses
BERT (Devlin et al., 2019) for mapping input se-
quences into contextual vectors. The spatial rela-
tions among tokens are modeled by an additional
CNN layer for prediction with a sigmoid layer.
Preliminary results
Table 7 reports the perfor-
mance of the baseline in terms of micro and macro
F-scores.
It shows that the CNN-Nested-NER
Table 7: Performance of NER models.
Model
Micro F-1 Macro F-1
Nested NER
78.87
75.63
Multiple BiLSTM-CRF
83.62
79.67
BINDER
86.96
84.02
CNN-Nested-NER
87.53
84.54
### Page 6

model is the best for recognizing nested incident
entities. A possible reason comes from the use
of partial relations among entities and contextual
representation from BERT. The BINDER model
follows with tiny margins. It shows the contribution
of contrastive learning. Two nested NER models
based on multiple layers do not show the efficiency.
It suggests to improve representation learning. We
did not use LLMs for NER due to nested entities.
4.2
Cause-Effect Extraction
The CE extraction task was formulated as a span ex-
traction problem (Devlin et al., 2019; Nguyen and
Nguyen, 2023). As shown in Table 3, each sample
may contain one or more spans annotated as Cause
or other types. For simplicity, EL, DP, DH, and
EO spans were merged as Effect and cause spans
were kept identically. For span-based extraction
models, the question is “cause" or “effect" and the
context is an incident report. This is because the
definition of complete questions does not guaran-
tee the semantic relationship between the questions
and context documents (Mengge et al., 2020).
BERT-QA
We followed BERT-QA (Devlin et al.,
2019) to extract cause and effect spans. The ques-
tion and the context were concatenated before be-
ing encoded by BERT. The contextual representa-
tions of tokens were put into a feed-forward net-
work followed by a softmax layer. Each candi-
date span for the answer was extracted based on
start/end probabilities predicted by the model.
FastQA
Apart from BERT-QA, we also tested
FastQA (Son et al., 2022). While BERT-QA ex-
tracts each cause or effect span independently,
FastQA extracts cause and effect simultaneously
as a pair. By embedding both “cause" and “effect"
questions in a separate module, FastQA allows the
model to encode cause and effect at the same time,
which halves the complexity of the encoding.
Guided-QA
Guided-QA (Nguyen and Nguyen,
2023) is an extension of BERT-QA that implic-
itly models the relationship between causes and
effects in a sequence manner. It receives a cause
question (“cause") and predicts the corresponding
cause span. Then the predicted cause span is used
as a question for effect extraction. Compared to
BERT-QA, Guided-QA takes into account an im-
plicit relationship from effect for cause prediction.
LLMs
We tested ChatGPT5 and Vicuna-13b-
4bit6 to assess the capability of LLMs for CE in
two settings: zero-shot and 1-shot. For zero-shot
experiments, an incident report was appended to
a pre-defined prompt such as "Find the cause and
effect in the following incident. Outputs should be
in Japanese." and feed them directly to LLMs. For
1-shot experiments, we used the completion format
<instruction><example><input> as follows.
Outputs should be in Japanese.
Text: <example incident>
Cause/effect: <example cause>
Text: <target incident>
Cause/effect:
Preliminary results
Table 8 reports the results of
CE models in terms of SQUAD F-1 (token match)
(Devlin et al., 2019). With full 700 training sam-
ples, BERT-QA is competitive followed by Chat-
GPT 1-shot. It is understandable that BERT-QA
was trained with 700 samples and easy for domain
adaptation. ChatGPT and Vicuna may need more
samples for working well with this CE task.
Table 8: Performance of cause-effect extraction models.
Model
Cause
Effect
Average
The train set of 700 samples
BERT-QA
65.90
77.81
71.85
ChatGPT 1-shot
75.48
49.80
62.64
ChatGPT 0-shot
55.48
37.25
46.36
Vicuna 1-shot
32.00
31.55
31.77
Vicuna 0-shot
19.44
28.16
23.80
The train set of 467 samples
BERT-QA
76.34
80.98
78.66
FastQA
71.25
79.39
75.32
Guided-QA
75.81
72.72
74.26
As mentioned in Table 4, 467 samples have
cause-effect pairs. We did another experiment on
this refined set. The F-scores show that span-based
extraction models obtain improvement compared
to the models trained on the original set. It shows
that with more refined training samples, a simple
BERT-QA model can achieve promising results.
Note that FastQA and Guided-QA can only work
with samples that include cause-effect pairs.
4.3
Information Retrieval
The IR task was formulated as a dense text retriever
problem using bi-encoder (Zhao et al., 2022). A
5https://platform.openai.com/playground
6https://huggingface.co/elinas/vicuna-13b-4bit
### Page 7

deep neural network was used to convert incident
reports and queries into dense vectors with their
nearest neighbors searched in the database. We
conduct the evaluation on the annotated IR dataset
with several baselines as follows.
BERT-based bi-encoder (public)
Bi-encoders
are highly efficient retrieval models based on pre-
trained transformer backbones (e.g., BERT). We
utilized the popular sentence-BERT multilingual
model7 (Reimers and Gurevych, 2019) as the main
baseline for our dense retrieval task.
BERT-based bi-encoder (finetuned)
To better
adapt the model to challenging technical terms and
jargon in the incident reports, we further fine-tuned
the aforementioned base encoder by using the unsu-
pervised constrastive learning objective (Gao et al.,
2021) on the collection of the incident corpus in
Section 3.2. Detail of the fine-tuning process can
be found in Appendix A.4.3.
Commercial embedding model (OpenAI)
We
also
evaluated
the
recent
commercial
solu-
tion
from
OpenAI
with
the
model
name
text-embedding-ada-002.8 The model is avail-
able in form of an API, which we can use to create
the embedding vector for a given document.
Preliminary results
Table 9 presents the re-
sults of all IR models with nDCG@k, mAP@k and
Recall@k as evaluation metrics with k=20. The
evaluation dataset is described in Section 3.2.
Table 9: Performance of information retrieval models.
Model
nDCG@k
mAP@k
R@k
BERT-public
45.27
15.91
30.90
BERT-finetuned
56.11
21.72
42.51
OpenAI-emb
54.48
22.25
38.32
We can observe from the table that the fine-tuned
BERT encoder produces significantly better perfor-
mance than the default base model and achieves the
best score on Recall@k and nDCG@k. The OpenAI
embedding model closely follows the fine-tuned
model, albeit not directly trained on similar data
domains before. This shows the performance of
the proprietary model from OpenAI is quite trans-
ferable and robust across different domains.
7https://huggingface.co/sentence-transformers/distiluse-
base-multilingual-cased-v2
8https://platform.openai.com/docs/guides/embeddings/what-
are-embeddings
4.4
Output Observation
Nested NER
Figure 6(a) shows the example of a
success case, where the model correctly detects all
spans of entities, including the nested one between
Product and Test. Further observation shows that
for the same entities that are close together, the
model tends to incorrectly recognize these entities
separately, as shown in figure 6(b). This type of
error is more common for entities such as Incident
and Process due to their complex nature and their
lengths. For entities such as Chemical and Product,
the common problem is misclassification of entities
or incorrect recognition of other noun spans. The
observation was done by using CNN-Nested-NER.
Cause-Effect Extraction
As we observe the
data, cause and effect spans usually appear in
phrases that indicate incidents such as leak, insuffi-
cient tightening. Because causes and effects share
such common patterns, it is harder for our models
to make correct predictions. Figures 6(a) and (b)
show an example of correct effect prediction and an
example of incorrect cause prediction of BERT-QA
finetuned on 467 samples (the best model).
Information Retrieval
We analyze the success
and failure cases of IR model BERT-finetuned.
Most success retrieval cases such as Figure 7, with
query document at the top most and followed re-
trieval results, typically mention several common
subjects such as flame, gas leak, and substance
name (ethylene). However, there are still a lot of
failure cases of the model regarding the understand-
ing of substance properties (toxic, flammable, etc)
when retrieving similar cases containing different
substances, and understanding the effect (e.g: leak-
age vs explosion) of the incident (Figure 8).
5
Conclusion
This paper introduces a new Japanese dataset for
safety prevention by using AI models. The high-
quality dataset is annotated by domain experts for
NER, CE, and IR tasks. The dataset contributes
to IncidentAI in two important points. First, it
composes the three NLP tasks in a corpus that fa-
cilitates the development of AI pipelines for safety
prevention in a low-resource language. Second, it
benchmarks the results of the three tasks which are
beneficial for the next studies of analyzing incident
reports. Future work will adapt the dataset to create
AI pipelines for preventing failures of IncidentAI.
### Page 8

Limitations
Although the newly created dataset of incidents is a
very high-quality corpus that is composed of three
NLP tasks: NER, cause-effect extraction (CE), and
IR, the size of the dataset is quite small with 970
annotated samples for NER and CE. The number
of annotated samples for IR is also small with
2,159 samples. While collecting raw data is quite
easy, data annotation is time-consuming and labor-
expensive with the involvement of domain experts.
It explains the size of our dataset is quite limited.
So, it requires more effort for data augmentation
when using the dataset in some cases. For example,
LLMs need thousands annotated samples for fine-
tuning. In addition, the dataset is in Japanese. On
the one hand, it facilitates the introduction of AI
models for IncidentAI in a low-resource language.
However, the dataset requires translation to more
popular languages, e.g., English for wider use.
For evaluation, some models are quite straight-
forward because the purpose is to provide prelimi-
nary results of the dataset. We believe the perfor-
mance of the three tasks can be still improved with
stronger models, especially in the case of cause-
effect extraction with BERT-QA and LLMs.
Ethics Statement
The dataset and models experimented in this work
have no unethical applications or risky broader im-
pacts. The dataset was crawled from publicly avail-
able reports of high-pressure gas incidents pub-
lished in 2022 by the High Pressure Gas Safety
Institute of Japan. Raw data contains information
such as descriptions of incidents at high-pressure
gas plants, types of incidents, dates of incidents,
industries, ignition sources, etc. It does not include
any confidential or personal information of workers
or companies. Three annotators are domain experts
who have at least six years of experience in the
high-pressure gas incident domain. They knew the
purpose of data creation and agreed to join the an-
notation process with their responsibilities. Their
personal information is kept for data publication.
The models used for evaluation can be publicly
accessed with GitHub links. There is no bias for the
re-implementation that can affect the final results.
References
Federal Aviation Administration. 2023.
Accident
and incident data.
https://www.faa.gov/data_
research/accident_incident. Accessed: 2023-
07-17.
Alan Akbik, Duncan Blythe, and Roland Vollgraf. 2018.
Contextual string embeddings for sequence labeling.
In Proceedings of the 27th international conference
on computational linguistics, pages 1638–1649.
Sequoia R Andrade and Hannah S Walsh. 2023. Safeaer-
obert: Towards a safety-informed aerospace-specific
language model. In AIAA AVIATION 2023 Forum,
page 3437.
Chetan Chandra, Xiao Jing, Mayank V Bendarkar, Kshi-
tij Sawant, Lidya Elias, Michelle Kirby, and Dim-
itri N Mavris. 2023. Aviation-bert: A preliminary
aviation-specific natural language model. In AIAA
AVIATION 2023 Forum, page 3436.
The MITRE Corporation. 2023. Cve - common vulner-
abilities and exposures. https://cve.mitre.org/
cve/search_cve_list.html. Accessed: 2023-07-
17.
Jacob Devlin, Changm Ming-Wei, Kenton Lee, and
Kristina Toutanova. 2019. Bert: Pre-training of deep
bidirectional transformers for language understand-
ing. In Proceedings of NAACL-HLT, pages 4171–
4186.
Francis Durso, MS Raunak, Rick Kuhn, and Raghu
Kacker. 2022. Analyzing failures in artificial intelli-
gent learning systems (fails). In 2022 IEEE 29th An-
nual Software Technology Conference (STC), pages
7–8. IEEE.
United
States
Food
and
Drug
Administra-
tion.
2023.
Accident
and
incident
data.
https://www.fda.gov/drugs/questions-and-answers-
fdas-adverse-event-reporting-system-faers/fda-
adverse-event-reporting-system-faers-public-
dashboard. Accessed: 2023-07-17.
Tianyu Gao, Xingcheng Yao, and Danqi Chen. 2021.
Simcse: Simple contrastive learning of sentence em-
beddings. volume abs/2104.08821.
Matthew K Hong, Adam Fourney, Derek DeBellis, and
Saleema Amershi. 2021. Planning for natural lan-
guage failures with the ai playbook. In Proceedings
of the 2021 CHI Conference on Human Factors in
Computing Systems, pages 1–11.
Yang Jiao, Jintao Dong, Jingru Han, and Huabo Sun.
2022. Classification and causes identification of chi-
nese civil aviation incident reports. Applied Sciences,
12(21):10765.
Xiao Jing, Akul Chennakesavan, Chetan Chandra,
Mayank V Bendarkar, Michelle Kirby, and Dimitri N
Mavris. 2023. Bert for aviation text classification. In
AIAA AVIATION 2023 Forum, page 3438.
Meizhi Ju, Makoto Miwa, and Sophia Ananiadou. 2018.
A neural layered model for nested named entity recog-
nition. In Proceedings of the 2018 Conference of
### Page 9

the North American Chapter of the Association for
Computational Linguistics: Human Language Tech-
nologies, Volume 1 (Long Papers), pages 1446–1459.
Carl Macrae. 2022. Learning from the failure of au-
tonomous and intelligent systems: Accidents, safety,
and sociotechnical sources of risk. Risk analysis,
42(9):1999–2025.
Sean McGregor. 2021. Preventing repeated real world
ai failures by cataloging incidents: The ai incident
database. In Proceedings of the AAAI Conference
on Artificial Intelligence, vol. 35, no. 17, pp. 15458-
15463.
Sean McGregor, Kevin Paeth, and Khoa Lam. 2022.
Indexing ai risks with incidents, issues, and variants.
In arXiv preprint arXiv:2211.10384.
Xue Mengge, Bowen Yu, Zhenyu Zhang, Tingwen Liu,
Yue Zhang, and Bin Wang. 2020. Coarse-to-fine pre-
training for named entity recognition. In Proceedings
of the 2020 Conference on Empirical Methods in
Natural Language Processing (EMNLP), pages 6345–
6354.
Ayaka Miyamoto, Mayank V Bendarkar, and Dimitri N
Mavris. 2022. Natural language processing of avia-
tion safety reports to identify inefficient operational
patterns. Aerospace, 9(8):450.
Saeid Mokhatab, William A Poe, and John Y Mak. 2018.
Handbook of natural gas transmission and process-
ing: principles and practices. Gulf professional pub-
lishing.
Huu-Hiep Nguyen and Minh-Tien Nguyen. 2023.
Emotion-cause pair extraction as question answer-
ing. In Proceedings of the 15th International Confer-
ence on Agents and Artificial Intelligence - Volume 3:
ICAART, pages 988–995.
Minh-Tien Nguyen, Viet-Anh Phan, Le Thai Linh,
Nguyen Hong Son, Le Tien Dung, Miku Hirano, and
Hajime Hotta. 2020. Transfer learning for informa-
tion extraction with limited data. In Computational
Linguistics: 16th International Conference of the
Pacific Association for Computational Linguistics,
PACLING 2019, Hanoi, Vietnam, October 11–13,
2019, Revised Selected Papers 16, pages 469–482.
Springer.
Minh-Tien Nguyen, Nguyen Hong Son, et al. 2023.
Gain more with less: Extracting information from
business documents with small data. Expert Systems
with Applications, 215:119274.
NIOSH.
2023.
National
institute
of
occu-
pational
safety
and
health,
japan.
https:
//www.jniosh.johas.go.jp/publication/
houkoku/houkoku_2020_05.html.
Accessed:
2023-10-17.
Ahmad Kamal Mohd Nor, Srinivasa Rao Pedapati,
Masdi Muhammad, and Víctor Leiva. 2022. Abnor-
mality detection and failure prediction using explain-
able bayesian deep learning: Methodology and case
study with industrial data. Mathematics, 10(4):554.
NTSB. 2017. Collision between a car operating with
automated vehicle control systems and a tractor-
semitrailer truck. Technical Report No. NTSB/HAR-
17/02.
Laura A Pellegrini, Giorgia DE GUIDO, Stefano Lange,
et al. 2019. Handbook of natural gas transmission
and processing-principles and practices. In Hand-
book of Natural Gas Transmission and Processing:
Principles and Practices, pages 669–739. Elsevier-
Gulf Professional Publishing.
Nikiforos Pittaras and Sean McGregor. 2022.
A
taxonomic system for failure cause analysis of
open source ai incidents.
In arXiv preprint
arXiv:2211.07280.
Nils Reimers and Iryna Gurevych. 2019. Sentence-bert:
Sentence embeddings using siamese bert-networks.
volume abs/1908.10084.
Matías Rojas, Felipe Bravo-Marquez, and Jocelyn Dun-
stan. 2022. Simple yet powerful: An overlooked
architecture for nested named entity recognition. In
Proceedings of the 29th International Conference on
Computational Linguistics, pages 2108–2117.
Kris Shrishak. 2023. How to deal with an ai near-miss:
Look to the skies. Bulletin of the Atomic Scientists,
79(3):166–169.
Nguyen Hong Son, M Yu Hieu, Tuan-Anh D Nguyen,
and Minh-Tien Nguyen. 2022. Jointly learning span
extraction and sequence labeling for information ex-
traction from business documents. In 2022 Interna-
tional Joint Conference on Neural Networks (IJCNN),
pages 1–8. IEEE.
Archana Tikayat Ray, Bjorn F Cole, Olivia J Pinon Fis-
cher, Ryan T White, and Dimitri N Mavris. 2023.
aerobert-classifier: Classification of aerospace re-
quirements using bert. Aerospace, 10(3):279.
Thomas Wolf, Lysandre Debut, Victor Sanh, Julien
Chaumond, Clement Delangue, Anthony Moi, Pier-
ric Cistac, Tim Rault, Rémi Louf, Morgan Funtowicz,
et al. 2020. Transformers: State-of-the-art natural
language processing. In Proceedings of the 2020 con-
ference on empirical methods in natural language
processing: system demonstrations, pages 38–45.
Roman V Yampolskiy. 2019. Predicting future ai fail-
ures from historic examples. foresight, 21(1):138–
152.
Hang Yan, Yu Sun, Xiaonan Li, and Xipeng Qiu.
2022. An embarrassingly easy but strong baseline
for nested named entity recognition. arXiv preprint
arXiv:2208.04534.
### Page 10

Chuyang Yang and Chenyu Huang. 2023. Natural lan-
guage processing (nlp) in aviation safety: System-
atic review of research and outlook into the future.
Aerospace, 10(7):600.
Sheng Zhang, Hao Cheng, Jianfeng Gao, and Hoifung
Poon. 2022. Optimizing bi-encoder for named entity
recognition via contrastive learning. In The Eleventh
International Conference on Learning Representa-
tions.
Wayne Xin Zhao, Jing Liu, Ruiyang Ren, and Ji-Rong
Wen. 2022. Dense text retrieval based on pretrained
language models: A survey.
A
Appendix
A.1
Annotation rules and examples of NER
The following rules must be observed when tagging
entities from domain experts.
• Do not tag words indicating parts such as en-
trances, exits, and connections if they are at
the end of a word. For example, tag "inlet
pipe" as "inlet pipe", but for "heat exchanger
outlet", only tag "heat exchanger".
• For tagging corresponding parts that indicate
a range like "4-6", tag the entire "4-6".
• If the same word is used in different meanings,
tag only the relevant entity.
• For words like "XX gas generation equip-
ment," tag both Storage and Products (nested).
For example, tag "XX gas generation equip-
ment" as Storage and tag “XX gas”” as Prod-
ucts.
• If there is a modifier Process within Products,
Chemicals, or Storage, do not tag Process. For
example, do not tag "recycle" as Process in
"recycle gas."
• Do not tag phrases containing particles like
"of" in "XX of YY" (Tag only "XX" or "YY"
separately).
• Tag abbreviations as well. However, do not
tag specific abbreviations such as equipment
or model numbers.
• Do not tag the state of individuals. For exam-
ple: "Lack of perspective".
• Do not tag words within legal names or stan-
dards, such as the names of laws or regu-
lations. For example: "High-Pressure Gas
Safety Act," do not tag "High-Pressure Gas."
• Only tag Pc when it pertains to gas handling.
For example: Do not tag "tightening further".
A.2
Annotation rules and examples of CE
The following rules must be strictly followed when
tagging CE from domain experts.
• Include in one sentence to be tagged: Who,
When, Where, What. Also include endings up
to verb phrases (e.g. Tag up to "leaked").
• Do not include in a sentence to be tagged: (i)
punctuation at the end of tagging ", and.", (ii)
such as "due to...", and (iii) conjunctions at
the beginning of a sentence (e.g. And," "And
then," "And then," etc.).
• How to separate each tagging: (i) do not sep-
arate with "," but separate with ".", (ii) in the
case of "broken and leaked," "broken" and
"leaked" are two different tags, so separate
them.
• No nesting.
• Do not tag the trigger for accident discovery
(unless it is a causal factor in the accident).
For example: "I noticed a strange odor,"
A.3
Annotation rules and examples of IR
Definitions of each attribute are shown in Table 10.
The annotated example of IR is shown in Figure 4
A.4
Implementation
A.4.1
NER models
Except for the neural layered model for nested
NER (Ju et al., 2018), whose word representation is
based on the concatenation of character and word
embeddings, other models use pre-trained BERT-
based encoder, TurkuNLP/wikibert-base-ja-cased.9
Other hyperparameters are set as follows.
Layered nested NER
The number of training
epochs is set at 100, with the learning rate and de-
cay rate of 1e −4 and the batch size of 32. The
dimension of word embedding and character em-
bedding are 200 and 25, respectively.
Multiple BiLSTM-CRF
The number of training
epochs is 10 for each entity type.
9https://huggingface.co/TurkuNLP/wikibert-base-ja-
cased
### Page 11

(a) Japanese (original).
(b) English (translated version).
Figure 2: An annotated sample of NER.
(a) Japanese (original).
(b) English (translated version).
Figure 3: An annotated sample of CE.
Figure 4: The samples of incident descriptions for IR.
### Page 12

Table 10: The guideline of IR annotation.
Attribute
Definition
Type of high pressure gas
The high-pressure gas that caused the reported accident was classified from the
perspective of danger in the event of an accident. Cases where the gas could
not be identified were included under “d. Not applicable”. The definition of
flammable gas and toxic gas shall conform to the High Pressure Gas Safety Act
in Japan.
Cause of incident
The events that caused or triggered the accident were classified. Equipment
factors refer to those caused by initial defects in parts built into the equipment.
Human factors refer to errors made in operation or judgment by people on site.
External factors indicate those caused by events from outside the equipment,
such as falling objects.
Incident result
The events that occurred as a result of the accident were classified. Physical
and human damage were only considered if they occurred as secondary events,
such as gas leaks or fires. Property damage: Accidents resulting in damage
to equipment or facilities due to fire or explosion. Do not include damage to
equipment or other items that caused the accident. Human casualties: Accidents
resulting in health hazards to humans due to leakage, fire, or explosion
Time span from cause to effect
The classification was made based on the time from when the cause or trigger
of the accident occurred until the accident event took place. Sudden: Accidents
where the results are caused generally within a few minutes to several tens of
minutes from the occurrence of the cause.
Operational status of equipment
The classification was made based on the operational status of the equipment at
the time of the accident. Non-steady state operation refers to operating conditions
that differ from normal operation, such as immediately after the equipment starts
running or during test operation
Figure 5: The scoring method for the samples in Figure 4 is as follows: each single overlap is assigned a score of 1.
If a label partially overlaps, as seen with the factor "a" under the "Incident Result" attribute, it still receives a score
of 1. With instances where a label overlaps with two factors, such as with ‘Type of High Pressure Gas‘, the score is
1.5. The final correlation score is the sum of each individual overlap score, totaling 3.5 in this case.
BINDER
The number of training epochs is 10,
with the learning rate of 3e −5 and the batch size
of 8 due to the heavy model. In addition, the model
requires a text description written in Japanese for
each entity type, which describes what the entity is
and how it is labeled.
CNN-nested-NER
The
number
of
training
epochs is 10, with the learning rate of 3e −5 and
the batch size of 8. The depth of CNN layers is 3,
with a dimension of 120 for each.
A.4.2
Cause-effect extraction models
The BERT-QA models were implemented using
BERT classes provided by Huggingface (Wolf
et al., 2020). The model was trained in 5 epochs,
with the learning rate of 5e −5, and the batch size
of 16. FastQA (Son et al., 2022) and Guided-QA
(Nguyen and Nguyen, 2023) were trained using
the source code from each paper. Again, FastQA
and Guided-QA were trained in 5 epochs with the
learning rate of 5e −5 and the batch size of 16.
The pre-trained model TurkuNLP/wikibert-base-
ja-cased was also used for all CE models.
A.4.3
IR models
We
fine-tuned
the
base
model
distiluse-base-multilingual-cased-v2
from sentence-BERT 10 on the small subset of
HPGIncident dataset described in Section 3.2
containing 3000 samples (not overlapped with the
annotated IR dataset).
We utilize the unsupervised training objective
from SimCSE (Gao et al., 2021), which takes an
input sentence and predicts itself in a contrastive
10https://huggingface.co/sentence-transformers/distiluse-
base-multilingual-cased-v2
### Page 13

(a) Correct Nested NER and CE example. Consecutive tokens in green denote an effect.
(b) Incorrect Nested NER and CE example. Consecutive tokens in red denote a cause.
Figure 6: The figure shows a success and failure case for Nested NER and CE.
Figure 7: A sample of success case for IR model.
Figure 8: A failure case of IR. The retrieved sample is different in the results (leakage vs explosion).
objective, with standard dropout used as noise. The
model is fine-tuned using 3 epochs with the learn-
ing rate of 3e −5. The encoder model uses mean
pooling to aggregate contextual information from
all tokens. We trained the model with the sequence
length of 512 tokens.
A.5
Output observation
The output of nested NER and CE is shown in
Figure 6 and that of IR is shown in Figure 7.