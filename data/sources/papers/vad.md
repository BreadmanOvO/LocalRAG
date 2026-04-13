# VAD: Vectorized Scene Representation for Efficient Autonomous Driving

- Source type: paper
- Category: papers
- Original file: data/sources/raw/papers/VAD Vectorized Scene Representation for Efficient Autonomous Driving.pdf
- Original URL: https://arxiv.org/abs/2303.12077
- Language: en
- Version: VAD
- Pages: 11
- Topic tags: [planning_control, perception]

## Summary
End-to-end autonomous-driving research paper using vectorized scene representation to connect perception, prediction, and planning efficiently.

## Key points
- Overall architecture of V AD.The full pipeline of V AD is divided into four phases.
- In the inferring phase of planning, V AD utilizes an ego query to extract map and agent information via query interaction and outputs the planning trajectory (represented as ego v…
- In order to learn the lo- cation and motion information of other dynamic traffic par- ticipants, the ego query first interacts with the agent queries through a Transformer decoder…
- The po- sitional embeddings provide information on the relative po- sition relationship between agents and the ego vehicle.

## Structured notes
### Pages 1-4
- [p.4] Overall architecture of V AD.The full pipeline of V AD is divided into four phases. Backbone includes an image feature extractor and a BEV encoder to project the image features to the BEV features. Vectorized Scene Lear…
- [p.4] In the inferring phase of planning, V AD utilizes an ego query to extract map and agent information via query interaction and outputs the planning trajectory (represented as ego vector). The proposed vectorized planning…
- [p.4] In order to learn the lo- cation and motion information of other dynamic traffic par- ticipants, the ego query first interacts with the agent queries through a Transformer decoder [46], in which ego query serves as quer…

### Pages 5-8
- [p.5] LongitudinalSafety LateralSafety Ego-AgentCollision Constraint BoundarySafety Ego-BoundaryOverstepping ConstraintEgo-LaneDirectional Constraint Lane Directionas Guidance // Figure 3. Illustration of Vectorized Planning…
- [p.5] Ego-boundary overstepping constraint punishes the predictions when the planning trajec- tory gets too close to the lane boundary. Ego-lane directional constraint leverages the direction of the closet lane vector from th…
- [p.5] Ego-agent collision constraint explicitly considers the compatibility of the ego planning trajectory and the future trajectory of other vehi- cles, in order to improve planning safety and avoid colli- sion. Unlike previ…

### Pages 9-11
- [p.9] No clean paragraph extracted.

## Evidence-ready excerpts
- [p.4] Overall architecture of V AD.The full pipeline of V AD is divided into four phases. Backbone includes an image feature extractor and a BEV encoder to project the image features to the BEV features. Vectorized Scene Learning aims to encode the scene information into agent queries and map queries, as well as represent the scene with motion vectors and map vectors.
- [p.5] So we adopt different agent distance thresholds δX and δY for different directions. For each future timestamp, we find the closest agent within a certain range δa in both directions. Then for each direction i ∈ { X, Y}, if the dis- tance di a with the closet agent is less than the threshold δi, then the loss item of this constraint Li col = δi − di a, other- wise it is 0.
- [p.8] V AD-Base achieves the best planning performance and still runs 2.5 × faster.It is worth noticing that in the main results, V AD omits ego sta- tus features to avoid shortcut learning in the open-loop plan- ning [50], but the results of V AD using ego status features are still preserved in Tab. 1 for reference.

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
