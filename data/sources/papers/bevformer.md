# BEVFormer

- Source type: paper
- Category: papers
- Original file: data/sources/raw/papers/BEVFormer.pdf
- Original URL: unknown
- Language: en
- Version: BEVFormer
- Pages: 20
- Topic tags: [perception, sensor_fusion]

## Summary
Research paper on bird’s-eye-view perception that uses spatiotemporal transformers to build BEV features for autonomous-driving perception tasks.

## Key points
- 3D visual perception tasks, including 3D detection and map segmentation based on multi-camera images, are essential for autonomous driving systems.
- In a nutshell, BEVFormer exploits both spatial and tempo- ral information by interacting with spatial and temporal space through predeﬁned grid-shaped BEV queries.
- Our approach achieves the new state-of-the-art 56.9% in terms of NDS metric on the nuScenes test set, which is 9.0 points higher than previous best arts and on par with the perfor…
- This work is done when Zhiqi Li is an intern at Shanghai AI Lab.

## Structured notes
### Pages 1-7
- [p.1] 3D visual perception tasks, including 3D detection and map segmentation based on multi-camera images, are essential for autonomous driving systems. In this work, we present a new framework termed BEVFormer, which learns…
- [p.1] In a nutshell, BEVFormer exploits both spatial and tempo- ral information by interacting with spatial and temporal space through predeﬁned grid-shaped BEV queries. To aggregate spatial information, we design spatial cro…
- [p.1] Our approach achieves the new state-of-the-art 56.9% in terms of NDS metric on the nuScenes test set, which is 9.0 points higher than previous best arts and on par with the performance of LiDAR-based baselines. We furth…

### Pages 8-14
- [p.8] No clean paragraph extracted.

### Pages 15-20
- [p.15] No clean paragraph extracted.

## Evidence-ready excerpts
- [p.1] 3D visual perception tasks, including 3D detection and map segmentation based on multi-camera images, are essential for autonomous driving systems. In this work, we present a new framework termed BEVFormer, which learns uniﬁed BEV representations with spatiotemporal transformers to support multiple autonomous driving perception tasks.
- [p.1] Our approach achieves the new state-of-the-art 56.9% in terms of NDS metric on the nuScenes test set, which is 9.0 points higher than previous best arts and on par with the performance of LiDAR-based baselines. We further show that BEVFormer remarkably improves the accuracy of velocity estimation and recall of objects under low visibility condi- tions. The code is available at https://github.com/zhiqi-li/BEVFormer. *: Equal contribution.
- [p.1] This work is done when Zhiqi Li is an intern at Shanghai AI Lab. B: Corresponding author. arXiv:2203.17270v2 [cs.CV] 13 Jul 2022

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
