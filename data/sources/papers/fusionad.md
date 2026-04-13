# FusionAD: Multi-modality Fusion for Prediction and Planning Tasks of Autonomous Driving

- Source type: paper
- Category: papers
- Original file: data/sources/raw/papers/FusionAD Multi-modality Fusion for Prediction and Planning Tasks of Autonomous.pdf
- Original URL: https://arxiv.org/abs/2308.01006
- Language: en
- Version: FusionAD
- Pages: 8
- Topic tags: [planning_control, sensor_fusion]

## Summary
Research paper on multimodal fusion for prediction and planning, targeted at end-to-end autonomous-driving behavior generation.

## Key points
- There are mainly two stages including trajectory generation with the Modality Self-attention and displacement generation, where two stages share a similar backbone structure.
- And the image cross-attention process is shown below: ICA(Qp, F ) = 1 Vhit VhitX i=1 NrefX j=1 DefAttn(Qp, P (p, i, j), Fi) (2) where Vhit denotes the number of camera views to wh…
- We then utilize Temporal Self-Attention to fuse historical frame BEV features, as shown below: TSA(Qp, (Q, B ′ t−1)) = X V ∈{Q,B′ t−1} DefAttn(Qp, p, V ) (3) where B ′ t−1 represe…
- Prediction Benefiting from the more informative BEV features, pre- diction module receives more stable and fine-grained in- formation.

## Structured notes
### Pages 1-3
- [p.1] No clean paragraph extracted.

### Pages 4-6
- [p.4] A2ACross-Attn globalanchor𝑎! Embed + A2GCross-Attn query embedding map embedding BEVembedding A2MCross-Attn 𝐾/𝑉 𝐾/𝑉 𝐾/𝑉 ||ModalitySelf-Attn currentposition𝑥" prediction𝑥#!#$% 𝑥#!# Embed Embed Embed Trajector y Generatio…
- [p.4] There are mainly two stages including trajectory generation with the Modality Self-attention and displacement generation, where two stages share a similar backbone structure. Pillar representation. A fixed number of Nre…
- [p.4] And the image cross-attention process is shown below: ICA(Qp, F ) = 1 Vhit VhitX i=1 NrefX j=1 DefAttn(Qp, P (p, i, j), Fi) (2) where Vhit denotes the number of camera views to which the reference point can be projected…

### Pages 7-8
- [p.7] (a) Case 1: Perception of a bus. FusionAD detects the heading correctly while distorsion exists in near range, but UniAD incorrectly predicts the heading. (b) Case 2: Prediction of U-turn. FusionAD consistantly predicts…
- [p.7] 5: Visual comparison of two example cases between UniAD [1] (Top) and our FusionAD (Bottom). V. CONCLUSIONS We propose FusionAD, a novel approach that leverages BEV fusion to facilitate multi-sensory, multi-task, end-to…
- [p.7] The proposed approach has yielded substantial performance improvements in both prediction and planning tasks, and has notably improved perception tasks when compared to end- to-end learning methods solely reliant on cam…

## Evidence-ready excerpts
- [p.4] A2ACross-Attn globalanchor𝑎! Embed + A2GCross-Attn query embedding map embedding BEVembedding A2MCross-Attn 𝐾/𝑉 𝐾/𝑉 𝐾/𝑉 ||ModalitySelf-Attn currentposition𝑥" prediction𝑥#!#$% 𝑥#!# Embed Embed Embed Trajector y GenerationDisplacement Generation ModalitySelf-Attn 𝑥#!& …… x L +Embed Embed Embed +PEMLPEmbed+addconcatenate|| Legend Fig. 3: Design of the prediction module in FMSPnP.
- [p.4] After the motion query retrieves all scene context to capture agent-agent, agent-map, and agent-goal point information, We then introduce mode self-attention to enable mutual visibility between the various modes, leading to better quality and diversity. Qmode = MHSA(Qu) (4) where MHSA denotes multi-head self-attention. Qu repre- sents the query that obtains the context information. Refinement Network.
- [p.7] The proposed approach has yielded substantial performance improvements in both prediction and planning tasks, and has notably improved perception tasks when compared to end- to-end learning methods solely reliant on camera-based BEV .

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
