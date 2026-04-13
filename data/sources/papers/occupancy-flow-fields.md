# Occupancy Flow Fields for Motion Forecasting in Autonomous Driving

- Source type: paper
- Category: papers
- Original file: data/sources/raw/papers/Occupancy Flow Fields for Motion Forecasting in Autonomous Driving.pdf
- Original URL: unknown
- Language: en
- Version: Occupancy Flow Fields
- Pages: 8
- Topic tags: [planning_control, perception]

## Summary
Research paper on occupancy-based motion forecasting for autonomous driving, connecting scene understanding to downstream behavior prediction.

## Key points
- Regular Agents Speculative Agents Regular Agents Speculative Agents w o l F y c n a p u c c Oe l c i h e Vw o l F e l c i h e V (0.6s) (1.5s) (1.5s) (5.4s) Pedestrian Flow Pedestr…
- For each scene, a single ﬂow prediction ( Ft) and three combined ﬂow and occupancy predictions ( Ft.Ot) are shown.
- Predicted Time (s) Predicted Time (s) Predicted Time (s) Pedestrians Vehicles Pedestrians Vehicles Pedestrians Vehicles 0.6 0.00 0.02 0.04 0.06 0.08 0.10 1.2 1.8 2.4 3.0 3.6 4.2 4…
- 9: Occupancy and ﬂow metrics on the Interaction dataset, which contains only vehicles.

## Structured notes
### Pages 1-3
- [p.1] No clean paragraph extracted.

### Pages 4-6
- [p.4] No clean paragraph extracted.

### Pages 7-8
- [p.7] Regular Agents Speculative Agents Regular Agents Speculative Agents w o l F y c n a p u c c Oe l c i h e Vw o l F e l c i h e V (0.6s) (1.5s) (1.5s) (5.4s) Pedestrian Flow Pedestrian Occupancy Flow (0.6s) (1.5s) (1.5s)…
- [p.7] For each scene, a single ﬂow prediction ( Ft) and three combined ﬂow and occupancy predictions ( Ft.Ot) are shown. Gray boxes show the recent state of input agents and the clouds visualize predicted occupancy and ﬂow. R…
- [p.7] Predicted Time (s) Predicted Time (s) Predicted Time (s) Pedestrians Vehicles Pedestrians Vehicles Pedestrians Vehicles 0.6 0.00 0.02 0.04 0.06 0.08 0.10 1.2 1.8 2.4 3.0 3.6 4.2 4.8 5.4 6.0 0.6 0.0000 0.0025 0.0050 0.00…

## Evidence-ready excerpts
- [p.7] Regular Agents Speculative Agents Regular Agents Speculative Agents w o l F y c n a p u c c Oe l c i h e Vw o l F e l c i h e V (0.6s) (1.5s) (1.5s) (5.4s) Pedestrian Flow Pedestrian Occupancy Flow (0.6s) (1.5s) (1.5s) (5.4s) Fig. 7: Regular and speculative predictions on two sample scenes ( top two and bottom two rows) from the Crowds dataset. The left four columns display predictions for vehicles, and the right four columns show pedestrians.
- [p.7] Predicted Time (s) Predicted Time (s) Predicted Time (s) Pedestrians Vehicles Pedestrians Vehicles Pedestrians Vehicles 0.6 0.00 0.02 0.04 0.06 0.08 0.10 1.2 1.8 2.4 3.0 3.6 4.2 4.8 5.4 6.0 0.6 0.0000 0.0025 0.0050 0.0075 0.0100 0.0125 0.0150 0.0175 0.0200 1.2 1.8 2.4 3.0 3.6 4.2 4.8 5.4 6.0 0.6 0 1 2 3 4 5 6 1.2 1.8 2.4 3.0 3.6 4.2 4.8 5.4 6.0 Fig. 8: Occupancy (AUC, Soft-IOU) and ﬂow (EPE) metrics for the speculative model on the Crowds dataset.
- [p.7] MP3’s ﬂow representation is less compute- and memory-efﬁcient. For K = 3 , each timestep needs 9 output channels compared to just 2 in our method. We had to train separate MP3 models for each agent class to ﬁt into the memory—giving it an advantages since

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
