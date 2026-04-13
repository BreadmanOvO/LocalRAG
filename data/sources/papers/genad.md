# GenAD: Generative End-to-End Autonomous Driving

- Source type: paper
- Category: papers
- Original file: data/sources/raw/papers/GenAD Generative End-to-End Autonomous Driving.pdf
- Original URL: https://arxiv.org/abs/2402.11502
- Language: en
- Version: GenAD
- Pages: 10
- Topic tags: [planning_control, perception]

## Summary
Generative end-to-end autonomous-driving research paper that models motion prediction and planning as a unified generation problem.

## Key points
- Directly producing planning results from raw sensors has been a long-desired solution for autonomous driving and has attracted increasing attention recently.
- However, we argue that the conventional progressive pipeline still cannot comprehensively model the entire traf- fic evolution process, e.g., the future interaction between the eg…
- We propose GenAD, a genera- tive framework that casts autonomous driving into a gen- erative modeling problem.
- We further adopt a temporal model to capture the agent and ego movements in the latent space to generate more effective future trajectories.

## Structured notes
### Pages 1-4
- [p.1] Directly producing planning results from raw sensors has been a long-desired solution for autonomous driving and has attracted increasing attention recently. Most ex- isting end-to-end autonomous driving methods factori…
- [p.1] However, we argue that the conventional progressive pipeline still cannot comprehensively model the entire traf- fic evolution process, e.g., the future interaction between the ego car and other traffic participants and…
- [p.1] We propose GenAD, a genera- tive framework that casts autonomous driving into a gen- erative modeling problem. We propose an instance-centric scene tokenizer that first transforms the surrounding scenes into map-aware i…

### Pages 5-8
- [p.5] No clean paragraph extracted.

### Pages 9-10
- [p.9] No clean paragraph extracted.

## Evidence-ready excerpts
- [p.1] Directly producing planning results from raw sensors has been a long-desired solution for autonomous driving and has attracted increasing attention recently. Most ex- isting end-to-end autonomous driving methods factorize this problem into perception, motion prediction, and plan- ning.
- [p.4] ing positions. Following V AD [21], we consider three cat- egories of map elements (i.e., lane divider, road boundary, and pedestrian crossing). We use the global cross-attention mechanism to update learnable initialized queries M0 from BEV tokens B: M = CA(M0, B, B), (3) where CA(Q, K, V) denotes the cross-attention block composed of interleaved self-attention and cross-attention layers using Q, K, and V as queries, keys, and values, re- spectively. BEV to agent.
- [p.4] For example, most of the trajectories are straight lines as the vehicle driving at a constant speed, and some of them are curved lines with a near-constant curvature when the vehicle turning right or left. Only in very rare cases will the trajectories be zig-zagging. Considering this, we adopt a variational autoencoder (V AE) [24] architecture to learn a latent space Z to model this trajectory prior. Specifically, we employ a ground-truth trajectory encoder ef to model 4

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
