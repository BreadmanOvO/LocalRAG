# Source Cleaning and Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild every knowledge source note from raw PDF files into clean markdown, then generate a stable `source_registry.json` that points to the cleaned files rather than the noisy legacy notes.

**Architecture:** Keep the repo’s flat Python layout and add two focused modules: `source_catalog.py` owns the static metadata for every raw PDF, while `source_cleaning.py` owns extraction, cleanup, markdown rendering, and registry generation. Generate outputs in three batches (`apollo`, `standards`, `papers`) so the content stays reviewable, then write `data/evaluation/shared/source_registry.json` from the reviewed clean files.

**Tech Stack:** Python standard library (`argparse`, `json`, `pathlib`, `re`, `math`, `collections`, `unittest`), `pypdf`, Markdown, Git

---

## File Structure

- `requirements-source-cleaning.txt` — dedicated dependency file for the PDF extraction pipeline so this work does not guess or overwrite the project’s existing runtime environment.
- `source_catalog.py` — single source catalog containing one `SourceDocument` entry per raw PDF, with stable `source_id`, output path, URL, version, tags, and summary hint.
- `source_cleaning.py` — PDF text extraction, text cleanup, excerpt selection, markdown rendering, per-category batch generation, and source registry writing.
- `test/test_source_catalog.py` — `unittest` coverage for catalog completeness, category counts, output-path stability, and registry path stability.
- `test/test_source_cleaning.py` — `unittest` coverage for text normalization, repeated-header/footer removal, excerpt selection, markdown rendering, and source registry writing.
- `data/sources/apollo/*.md` — regenerated clean Apollo notes based only on raw PDFs.
- `data/sources/standards/*.md` — regenerated clean standards notes based only on raw PDFs.
- `data/sources/papers/*.md` — regenerated clean paper notes based only on raw PDFs.
- `data/evaluation/shared/source_registry.json` — generated registry that points to the new clean markdown files and keeps the raw PDF path for traceability.

## Task 1: Add the dependency file and Apollo source catalog

**Files:**
- Create: `requirements-source-cleaning.txt`
- Create: `source_catalog.py`
- Create: `test/test_source_catalog.py`

- [ ] **Step 1: Write the failing tests for the Apollo catalog**

```python
import unittest
from pathlib import Path

from source_catalog import ROOT, SOURCE_DOCUMENTS, documents_for_category


class ApolloSourceCatalogTests(unittest.TestCase):
    def test_apollo_catalog_matches_raw_directory(self):
        expected = {
            path.name
            for path in (ROOT / "data" / "sources" / "raw" / "apollo").glob("*.pdf")
        }
        actual = {Path(doc.raw_relpath).name for doc in documents_for_category("apollo")}
        self.assertEqual(expected, actual)

    def test_apollo_output_paths_land_in_apollo_directory(self):
        actual = {doc.clean_relpath for doc in documents_for_category("apollo")}
        self.assertEqual(
            {
                "data/sources/apollo/apollo-devcenter-learning-path.md",
                "data/sources/apollo/apollo-cyber-rt.md",
                "data/sources/apollo/apollo-channel-data-format.md",
                "data/sources/apollo/apollo-open-platform-overview.md",
                "data/sources/apollo/apollo-perception-fusion-overview.md",
                "data/sources/apollo/apollo-vision-perception-overview.md",
                "data/sources/apollo/apollo-vision-prediction-overview.md",
                "data/sources/apollo/apollo-vision-plan-overview.md",
                "data/sources/apollo/apollo-vision-control-overview.md",
                "data/sources/apollo/apollo-vision-location-overview.md",
            },
            actual,
        )

    def test_source_ids_are_unique(self):
        source_ids = [doc.source_id for doc in SOURCE_DOCUMENTS]
        self.assertEqual(len(source_ids), len(set(source_ids)))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail because the catalog module does not exist yet**

Run: `python -m unittest test.test_source_catalog -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'source_catalog'`

- [ ] **Step 3: Create the dependency file and Apollo catalog module**

`requirements-source-cleaning.txt`
```text
pypdf
```

`source_catalog.py`
```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGISTRY_REL_PATH = "data/evaluation/shared/source_registry.json"


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    title: str
    source_type: str
    category: str
    language: str
    raw_relpath: str
    clean_relpath: str
    origin_url: str
    version: str
    topic_tags: tuple[str, ...]
    summary_hint: str

    @property
    def raw_path(self) -> Path:
        return ROOT / self.raw_relpath

    @property
    def clean_path(self) -> Path:
        return ROOT / self.clean_relpath


SOURCE_DOCUMENTS: tuple[SourceDocument, ...] = (
    SourceDocument(
        source_id="apollo-doc-001",
        title="Apollo Developer Center Learning Path",
        source_type="official_doc",
        category="apollo",
        language="en",
        raw_relpath="data/sources/raw/apollo/apollo-devcenter-learning-path.pdf",
        clean_relpath="data/sources/apollo/apollo-devcenter-learning-path.md",
        origin_url="https://developer.apollo.auto/devcenter/devcenter.html",
        version="Apollo Developer Center",
        topic_tags=("system_architecture", "perception", "planning_control"),
        summary_hint="Official Apollo learning-path material that explains the major modules, their order of study, and how perception, prediction, planning, control, and localization fit together.",
    ),
    SourceDocument(
        source_id="apollo-doc-002",
        title="Apollo Cyber RT Framework",
        source_type="official_doc",
        category="apollo",
        language="en",
        raw_relpath="data/sources/raw/apollo/Apollo-Cyber-RT-framework.pdf",
        clean_relpath="data/sources/apollo/apollo-cyber-rt.md",
        origin_url="https://developer.apollo.auto/cyber.html",
        version="Apollo Cyber RT",
        topic_tags=("system_architecture", "planning_control"),
        summary_hint="Official Apollo runtime-framework material describing Cyber RT, its component model, scheduling model, and how it supports low-latency autonomous-driving workloads.",
    ),
    SourceDocument(
        source_id="apollo-doc-003",
        title="Apollo Channel Data Format",
        source_type="official_doc",
        category="apollo",
        language="zh",
        raw_relpath="data/sources/raw/apollo/apollo-channel-data-format.pdf",
        clean_relpath="data/sources/apollo/apollo-channel-data-format.md",
        origin_url="https://developer.apollo.auto/Apollo-Homepage-Document/Apollo_Doc_CN_6_0/%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F/Channel%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F%E6%96%87%E6%A1%A3%E4%BB%8B%E7%BB%8D",
        version="Apollo Doc CN 6.0",
        topic_tags=("system_architecture", "sensor_fusion", "planning_control"),
        summary_hint="Official Apollo channel-format material describing how modules communicate through Cyber RT channels and which message types are used for perception, prediction, planning, and control.",
    ),
    SourceDocument(
        source_id="apollo-doc-004",
        title="Apollo Open Platform Overview",
        source_type="official_doc",
        category="apollo",
        language="en",
        raw_relpath="data/sources/raw/apollo/Apollo-Open-Platform-overview.pdf",
        clean_relpath="data/sources/apollo/apollo-open-platform-overview.md",
        origin_url="https://developer.apollo.auto/developer.html",
        version="Apollo Open Platform",
        topic_tags=("system_architecture", "perception", "planning_control"),
        summary_hint="Official platform-overview material describing Apollo’s software stack, hardware stack, and module boundaries across perception, localization, planning, control, and simulation.",
    ),
    SourceDocument(
        source_id="apollo-doc-005",
        title="Apollo Perception Fusion Overview",
        source_type="official_doc",
        category="apollo",
        language="zh",
        raw_relpath="data/sources/raw/apollo/apollo-perception-fusion-overview.pdf",
        clean_relpath="data/sources/apollo/apollo-perception-fusion-overview.md",
        origin_url="https://developer.apollo.auto/Apollo-Homepage-Document/Apollo_Doc_CN_6_0/%E4%B8%8A%E6%9C%BA%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B/%E4%B8%8A%E6%9C%BA%E5%AE%9E%E8%B7%B5Apollo%E6%84%9F%E7%9F%A5%E8%9E%8D%E5%90%88%E8%83%BD%E5%8A%9B/Apollo%E6%84%9F%E7%9F%A5%E8%9E%8D%E5%90%88%E8%83%BD%E5%8A%9B%E4%BB%8B%E7%BB%8D",
        version="Apollo Doc CN 6.0",
        topic_tags=("perception", "sensor_fusion"),
        summary_hint="Official Apollo perception-fusion material describing the multi-sensor fusion workflow and the role of fused perception in downstream driving tasks.",
    ),
    SourceDocument(
        source_id="apollo-doc-006",
        title="Apollo Vision Perception Overview",
        source_type="official_doc",
        category="apollo",
        language="zh",
        raw_relpath="data/sources/raw/apollo/apollo-vision-perception-overview.pdf",
        clean_relpath="data/sources/apollo/apollo-vision-perception-overview.md",
        origin_url="https://developer.apollo.auto/platform/perception_cn.html",
        version="Apollo Perception CN",
        topic_tags=("perception", "sensor_fusion"),
        summary_hint="Official Apollo perception material describing the perception module, its obstacle understanding responsibilities, and how visual perception supports autonomous driving.",
    ),
    SourceDocument(
        source_id="apollo-doc-007",
        title="Apollo Prediction Overview",
        source_type="official_doc",
        category="apollo",
        language="zh",
        raw_relpath="data/sources/raw/apollo/apollo-vision-prediction-overview.pdf",
        clean_relpath="data/sources/apollo/apollo-vision-prediction-overview.md",
        origin_url="https://developer.apollo.auto/Apollo-Homepage-Document/Apollo_Doc_CN_6_0/%E4%B8%8A%E6%9C%BA%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B/%E4%B8%8A%E6%9C%BA%E5%AE%9E%E8%B7%B5Apollo%E9%A2%84%E6%B5%8B%E8%83%BD%E5%8A%9B/Apollo%E9%A2%84%E6%B5%8B%E8%83%BD%E5%8A%9B%E4%BB%8B%E7%BB%8D",
        version="Apollo Doc CN 6.0",
        topic_tags=("planning_control", "perception"),
        summary_hint="Official Apollo prediction material describing how the system predicts surrounding-agent behavior and feeds that forecast into planning.",
    ),
    SourceDocument(
        source_id="apollo-doc-008",
        title="Apollo Planning Overview",
        source_type="official_doc",
        category="apollo",
        language="zh",
        raw_relpath="data/sources/raw/apollo/apollo-vision-plan-overview.pdf",
        clean_relpath="data/sources/apollo/apollo-vision-plan-overview.md",
        origin_url="https://developer.apollo.auto/Apollo-Homepage-Document/Apollo_Doc_CN_6_0/%E4%B8%8A%E6%9C%BA%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B/%E4%B8%8A%E6%9C%BA%E5%AE%9E%E8%B7%B5Apollo%E8%A7%84%E5%88%92%E8%83%BD%E5%8A%9B/apollo%E8%A7%84%E5%88%92%E8%83%BD%E5%8A%9B%E4%BB%8B%E7%BB%8D",
        version="Apollo Doc CN 6.0",
        topic_tags=("planning_control", "system_architecture"),
        summary_hint="Official Apollo planning material describing scenario-based planning, planner responsibilities, and the inputs and outputs of the planning module.",
    ),
    SourceDocument(
        source_id="apollo-doc-009",
        title="Apollo Control Overview",
        source_type="official_doc",
        category="apollo",
        language="zh",
        raw_relpath="data/sources/raw/apollo/apollo-vision-control-overview.pdf",
        clean_relpath="data/sources/apollo/apollo-vision-control-overview.md",
        origin_url="https://developer.apollo.auto/Apollo-Homepage-Document/Apollo_Doc_CN_6_0/%E4%B8%8A%E6%9C%BA%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B/%E4%B8%8A%E6%9C%BA%E5%AE%9E%E8%B7%B5Apollo%E6%8E%A7%E5%88%B6%E8%83%BD%E5%8A%9B/Apollo%20%E6%8E%A7%E5%88%B6%E8%83%BD%E5%8A%9B%E4%BB%8B%E7%BB%8D",
        version="Apollo Doc CN 6.0",
        topic_tags=("planning_control", "system_architecture"),
        summary_hint="Official Apollo control material describing how planned trajectories are converted into steering, throttle, and brake commands.",
    ),
    SourceDocument(
        source_id="apollo-doc-010",
        title="Apollo Localization Overview",
        source_type="official_doc",
        category="apollo",
        language="zh",
        raw_relpath="data/sources/raw/apollo/apollo-vision-location-overview.pdf",
        clean_relpath="data/sources/apollo/apollo-vision-location-overview.md",
        origin_url="https://developer.apollo.auto/Apollo-Homepage-Document/Apollo_Doc_CN_6_0/%E4%B8%8A%E6%9C%BA%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B/%E4%B8%8A%E6%9C%BA%E5%AE%9E%E8%B7%B5Apollo%E5%AE%9A%E4%BD%8D%E8%83%BD%E5%8A%9B/Apollo%E5%AE%9A%E4%BD%8D%E8%83%BD%E5%8A%9B%E4%BB%8B%E7%BB%8D/",
        version="Apollo Doc CN 6.0",
        topic_tags=("system_architecture", "planning_control"),
        summary_hint="Official Apollo localization material describing the localization stack, map alignment, and the role of high-precision position estimation in autonomous driving.",
    ),
)


def all_documents() -> tuple[SourceDocument, ...]:
    return SOURCE_DOCUMENTS



def documents_for_category(category: str) -> tuple[SourceDocument, ...]:
    return tuple(doc for doc in SOURCE_DOCUMENTS if doc.category == category)
```

- [ ] **Step 4: Run the Apollo catalog tests to verify the new catalog passes**

Run: `python -m unittest test.test_source_catalog -v`
Expected: PASS with `test_apollo_catalog_matches_raw_directory ... ok`, `test_apollo_output_paths_land_in_apollo_directory ... ok`, and `test_source_ids_are_unique ... ok`

- [ ] **Step 5: Commit the dependency and Apollo catalog foundation**

```bash
git add requirements-source-cleaning.txt source_catalog.py test/test_source_catalog.py
git commit -m "build: add Apollo source catalog for raw PDFs"
```

## Task 2: Extend the catalog to standards and papers

**Files:**
- Modify: `source_catalog.py`
- Modify: `test/test_source_catalog.py`

- [ ] **Step 1: Extend the tests to require full raw-PDF coverage and stable category counts**

```python
import unittest
from pathlib import Path

from source_catalog import ROOT, REGISTRY_REL_PATH, SOURCE_DOCUMENTS, documents_for_category


class FullSourceCatalogTests(unittest.TestCase):
    def test_catalog_matches_all_raw_pdfs(self):
        expected = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "data" / "sources" / "raw").rglob("*.pdf")
        }
        actual = {doc.raw_relpath for doc in SOURCE_DOCUMENTS}
        self.assertEqual(expected, actual)

    def test_category_counts_match_scope(self):
        self.assertEqual(10, len(documents_for_category("apollo")))
        self.assertEqual(9, len(documents_for_category("standards")))
        self.assertEqual(7, len(documents_for_category("papers")))

    def test_registry_path_is_stable(self):
        self.assertEqual("data/evaluation/shared/source_registry.json", REGISTRY_REL_PATH)

    def test_clean_paths_are_unique(self):
        clean_paths = [doc.clean_relpath for doc in SOURCE_DOCUMENTS]
        self.assertEqual(len(clean_paths), len(set(clean_paths)))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the full catalog tests to verify they fail because only Apollo entries exist**

Run: `python -m unittest test.test_source_catalog -v`
Expected: FAIL with a set mismatch showing missing `data/sources/raw/standards/*.pdf` and `data/sources/raw/papers/*.pdf`

- [ ] **Step 3: Extend `source_catalog.py` with the standards and papers entries**

Append these entries inside `SOURCE_DOCUMENTS` after the Apollo entries:

```python
    SourceDocument(
        source_id="standard-001",
        title="NHTSA Automated Driving Systems Overview",
        source_type="standard",
        category="standards",
        language="en",
        raw_relpath="data/sources/raw/standards/NHTSA ADS overview.pdf",
        clean_relpath="data/sources/standards/nhtsa-ads-overview.md",
        origin_url="https://www.nhtsa.gov/automated-vehicles/vision-safety",
        version="NHTSA ADS Overview",
        topic_tags=("safety", "system_architecture"),
        summary_hint="Official NHTSA overview material describing automated driving systems from the U.S. safety-regulation perspective.",
    ),
    SourceDocument(
        source_id="standard-002",
        title="Automated Driving Systems 2.0: A Vision for Safety",
        source_type="standard",
        category="standards",
        language="en",
        raw_relpath="data/sources/raw/standards/Automated Driving Systems 2.0 A Vision for Safety.pdf",
        clean_relpath="data/sources/standards/ads-2-0-vision-for-safety.md",
        origin_url="https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/13069a-ads2.0_090617_v9a_tag.pdf",
        version="ADS 2.0",
        topic_tags=("safety", "system_architecture"),
        summary_hint="Official NHTSA voluntary-guidance document describing high-level safety expectations for automated driving systems.",
    ),
    SourceDocument(
        source_id="standard-003",
        title="Preparing for the Future of Transportation: Automated Vehicles 3.0",
        source_type="standard",
        category="standards",
        language="en",
        raw_relpath="data/sources/raw/standards/Preparing for the Future of Transportation Automated Vehicles 3.0.pdf",
        clean_relpath="data/sources/standards/av-3-0-preparing-for-the-future-of-transportation.md",
        origin_url="https://www.transportation.gov/sites/dot.gov/files/docs/policy-initiatives/automated-vehicles/320711/preparing-future-transportation-automated-vehicle-30.pdf",
        version="AV 3.0",
        topic_tags=("safety", "system_architecture"),
        summary_hint="Official U.S. DOT automated-vehicle policy document describing broader transportation and regulatory context around automated vehicles.",
    ),
    SourceDocument(
        source_id="standard-004",
        title="Ensuring American Leadership in Automated Vehicle Technologies: AV 4.0",
        source_type="standard",
        category="standards",
        language="en",
        raw_relpath="data/sources/raw/standards/Ensuring American Leadership in Automated Vehicle Technologies AV 4.0.pdf",
        clean_relpath="data/sources/standards/av-4-0-ensuring-american-leadership.md",
        origin_url="https://www.transportation.gov/sites/dot.gov/files/docs/policy-initiatives/automated-vehicles/360956/ensuringamericanleadershipav4.pdf",
        version="AV 4.0",
        topic_tags=("safety", "system_architecture"),
        summary_hint="Official U.S. DOT automated-vehicle strategy document describing federal automated-vehicle priorities and cross-agency coordination.",
    ),
    SourceDocument(
        source_id="standard-005",
        title="Automated Driving System Safety: Overview of NHTSA Activities",
        source_type="standard",
        category="standards",
        language="en",
        raw_relpath="data/sources/raw/standards/Automated Driving System Safety Overview of NHTSA Activities.pdf",
        clean_relpath="data/sources/standards/nhtsa-ads-safety-overview.md",
        origin_url="https://www.nhtsa.gov/document/automated-driving-system-safety-overview-nhtsa-activities-0",
        version="NHTSA Activities Overview",
        topic_tags=("safety",),
        summary_hint="Official NHTSA material summarizing the agency’s activities and safety priorities for automated driving systems.",
    ),
    SourceDocument(
        source_id="standard-006",
        title="Overview of Select NHTSA Activities – Automated Driving Systems",
        source_type="standard",
        category="standards",
        language="en",
        raw_relpath="data/sources/raw/standards/Overview of Select NHTSA Activities – Automated Driving Systems.pdf",
        clean_relpath="data/sources/standards/nhtsa-select-ads-activities-overview.md",
        origin_url="https://www.nhtsa.gov/sites/nhtsa.gov/files/2024-02/16180-NSR-231211-007_SAE_Overview%20of%20Select%20NHTSA%20Activities%20-%20Automated%20Driving%20Systems-tag.pdf",
        version="NHTSA Select Activities Overview",
        topic_tags=("safety",),
        summary_hint="Official NHTSA material highlighting selected automated-driving-system activities and the agency’s current program emphasis.",
    ),
    SourceDocument(
        source_id="standard-007",
        title="UN Regulation No. 155 - Cyber security and cyber security management system",
        source_type="standard",
        category="standards",
        language="en",
        raw_relpath="data/sources/raw/standards/UN Regulation No. 155 - Cyber security and cyber security management system.pdf",
        clean_relpath="data/sources/standards/unece-r155-cyber-security-management-system.md",
        origin_url="https://unece.org/sites/default/files/2023-02/R155e%20%282%29.pdf",
        version="UN R155",
        topic_tags=("safety",),
        summary_hint="Official UNECE regulation text covering vehicle cyber-security requirements and the cyber-security management system.",
    ),
    SourceDocument(
        source_id="standard-008",
        title="UN Regulation No. 156 - Software update and software update management system",
        source_type="standard",
        category="standards",
        language="en",
        raw_relpath="data/sources/raw/standards/UN Regulation No. 156 - Software update and software update management system.pdf",
        clean_relpath="data/sources/standards/unece-r156-software-update-management-system.md",
        origin_url="https://unece.org/sites/default/files/2024-03/R156e%20%282%29.pdf",
        version="UN R156",
        topic_tags=("safety",),
        summary_hint="Official UNECE regulation text covering software update requirements and the software update management system.",
    ),
    SourceDocument(
        source_id="standard-009",
        title="UN Regulation No. 157 - Automated Lane Keeping Systems (ALKS)",
        source_type="standard",
        category="standards",
        language="en",
        raw_relpath="data/sources/raw/standards/UN Regulation No. 157 - Automated Lane Keeping Systems (ALKS).pdf",
        clean_relpath="data/sources/standards/unece-r157-alks.md",
        origin_url="https://unece.org/sites/default/files/2025-06/R157r1e.pdf",
        version="UN R157",
        topic_tags=("safety", "planning_control"),
        summary_hint="Official UNECE regulation text covering automated lane keeping systems and the operating conditions for that automated-driving function.",
    ),
    SourceDocument(
        source_id="paper-001",
        title="BEVFormer",
        source_type="paper",
        category="papers",
        language="en",
        raw_relpath="data/sources/raw/papers/BEVFormer.pdf",
        clean_relpath="data/sources/papers/bevformer.md",
        origin_url="unknown",
        version="BEVFormer",
        topic_tags=("perception", "sensor_fusion"),
        summary_hint="Research paper on bird’s-eye-view perception that uses spatiotemporal transformers to build BEV features for autonomous-driving perception tasks.",
    ),
    SourceDocument(
        source_id="paper-002",
        title="BEVFusion",
        source_type="paper",
        category="papers",
        language="en",
        raw_relpath="data/sources/raw/papers/BEVFusion.pdf",
        clean_relpath="data/sources/papers/bevfusion.md",
        origin_url="unknown",
        version="BEVFusion",
        topic_tags=("perception", "sensor_fusion"),
        summary_hint="Research paper on unified BEV fusion across LiDAR and camera inputs for robust autonomous-driving perception.",
    ),
    SourceDocument(
        source_id="paper-003",
        title="Occupancy Flow Fields for Motion Forecasting in Autonomous Driving",
        source_type="paper",
        category="papers",
        language="en",
        raw_relpath="data/sources/raw/papers/Occupancy Flow Fields for Motion Forecasting in Autonomous Driving.pdf",
        clean_relpath="data/sources/papers/occupancy-flow-fields.md",
        origin_url="unknown",
        version="Occupancy Flow Fields",
        topic_tags=("planning_control", "perception"),
        summary_hint="Research paper on occupancy-based motion forecasting for autonomous driving, connecting scene understanding to downstream behavior prediction.",
    ),
    SourceDocument(
        source_id="paper-004",
        title="Scalability in Perception for Autonomous Driving: Waymo Open Dataset",
        source_type="report",
        category="papers",
        language="en",
        raw_relpath="data/sources/raw/papers/Scalability in Perception for Autonomous Driving Waymo Open Dataset.pdf",
        clean_relpath="data/sources/papers/waymo-scalability-perception.md",
        origin_url="unknown",
        version="Waymo Open Dataset Report",
        topic_tags=("perception", "system_architecture"),
        summary_hint="Technical report from the Waymo Open Dataset context explaining perception scalability and dataset-driven evaluation considerations for autonomous driving.",
    ),
    SourceDocument(
        source_id="paper-005",
        title="VAD: Vectorized Scene Representation for Efficient Autonomous Driving",
        source_type="paper",
        category="papers",
        language="en",
        raw_relpath="data/sources/raw/papers/VAD Vectorized Scene Representation for Efficient Autonomous Driving.pdf",
        clean_relpath="data/sources/papers/vad.md",
        origin_url="https://arxiv.org/abs/2303.12077",
        version="VAD",
        topic_tags=("planning_control", "perception"),
        summary_hint="End-to-end autonomous-driving research paper using vectorized scene representation to connect perception, prediction, and planning efficiently.",
    ),
    SourceDocument(
        source_id="paper-006",
        title="FusionAD: Multi-modality Fusion for Prediction and Planning Tasks of Autonomous Driving",
        source_type="paper",
        category="papers",
        language="en",
        raw_relpath="data/sources/raw/papers/FusionAD Multi-modality Fusion for Prediction and Planning Tasks of Autonomous.pdf",
        clean_relpath="data/sources/papers/fusionad.md",
        origin_url="https://arxiv.org/abs/2308.01006",
        version="FusionAD",
        topic_tags=("planning_control", "sensor_fusion"),
        summary_hint="Research paper on multimodal fusion for prediction and planning, targeted at end-to-end autonomous-driving behavior generation.",
    ),
    SourceDocument(
        source_id="paper-007",
        title="GenAD: Generative End-to-End Autonomous Driving",
        source_type="paper",
        category="papers",
        language="en",
        raw_relpath="data/sources/raw/papers/GenAD Generative End-to-End Autonomous Driving.pdf",
        clean_relpath="data/sources/papers/genad.md",
        origin_url="https://arxiv.org/abs/2402.11502",
        version="GenAD",
        topic_tags=("planning_control", "perception"),
        summary_hint="Generative end-to-end autonomous-driving research paper that models motion prediction and planning as a unified generation problem.",
    ),
```

- [ ] **Step 4: Run the full catalog tests to verify every raw PDF is represented**

Run: `python -m unittest test.test_source_catalog -v`
Expected: PASS with `test_catalog_matches_all_raw_pdfs ... ok`, `test_category_counts_match_scope ... ok`, `test_registry_path_is_stable ... ok`, and `test_clean_paths_are_unique ... ok`

- [ ] **Step 5: Commit the full source catalog**

```bash
git add source_catalog.py test/test_source_catalog.py
git commit -m "build: catalog all raw source PDFs"
```

## Task 3: Add PDF cleaning helpers and their unit tests

**Files:**
- Create: `source_cleaning.py`
- Create: `test/test_source_cleaning.py`

- [ ] **Step 1: Write the failing helper tests for text normalization, repeated-line cleanup, and evidence selection**

```python
import unittest

from source_cleaning import (
    drop_repeating_lines,
    normalize_page_text,
    select_evidence_excerpts,
)


class SourceCleaningHelperTests(unittest.TestCase):
    def test_normalize_page_text_collapses_whitespace(self):
        raw = "Title\r\n\r\nThis   is   a test.\n\n\nAnother line.\u3000"
        self.assertEqual(
            "Title\n\nThis is a test.\n\nAnother line.",
            normalize_page_text(raw),
        )

    def test_drop_repeating_lines_removes_headers_and_footers(self):
        page_texts = [
            "Common Header\nPage 1 body text that should stay.\nCommon Footer",
            "Common Header\nPage 2 body text that should stay.\nCommon Footer",
            "Common Header\nPage 3 body text that should stay.\nCommon Footer",
        ]
        self.assertEqual(
            [
                "Page 1 body text that should stay.",
                "Page 2 body text that should stay.",
                "Page 3 body text that should stay.",
            ],
            drop_repeating_lines(page_texts),
        )

    def test_select_evidence_excerpts_spreads_quotes_across_document(self):
        page_texts = [
            "Early paragraph about the system architecture with enough detail to survive filtering. " * 2,
            "",
            "Middle paragraph about planning and prediction interactions with enough detail to survive filtering. " * 2,
            "Late paragraph about control outputs and operational constraints with enough detail to survive filtering. " * 2,
        ]
        excerpts = select_evidence_excerpts(page_texts, limit=3)
        self.assertEqual([1, 3, 4], [page for page, _ in excerpts])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the helper tests to verify they fail because the cleaning module does not exist yet**

Run: `python -m unittest test.test_source_cleaning -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'source_cleaning'`

- [ ] **Step 3: Create the cleaning helper module**

```python
from __future__ import annotations

import re
from collections import Counter
from math import ceil
from pathlib import Path

from source_catalog import SourceDocument

WHITESPACE_RE = re.compile(r"[ \t\xa0\u3000]+")
PARAGRAPH_SPLIT_RE = re.compile(r"\n{2,}")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？.!?])\s+")



def normalize_page_text(text: str) -> str:
    text = text.replace("\r", "")
    paragraphs = []
    for block in PARAGRAPH_SPLIT_RE.split(text):
        lines = [WHITESPACE_RE.sub(" ", line).strip() for line in block.splitlines()]
        cleaned_lines = [line for line in lines if line]
        if cleaned_lines:
            paragraphs.append(" ".join(cleaned_lines))
    return "\n\n".join(paragraphs)



def drop_repeating_lines(page_texts: list[str]) -> list[str]:
    page_lines = []
    for text in page_texts:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        page_lines.append(lines)

    repeated_threshold = max(2, ceil(len(page_lines) * 0.5))
    counts: Counter[str] = Counter()
    for lines in page_lines:
        counts.update(set(lines))

    repeated_lines = {
        line
        for line, count in counts.items()
        if count >= repeated_threshold and len(line) <= 120
    }

    cleaned_pages: list[str] = []
    for lines in page_lines:
        kept = [line for line in lines if line not in repeated_lines]
        cleaned_pages.append("\n".join(kept).strip())
    return cleaned_pages



def extract_paragraphs(page_text: str) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in PARAGRAPH_SPLIT_RE.split(page_text) if paragraph.strip()]
    if paragraphs:
        return paragraphs
    return [line.strip() for line in page_text.splitlines() if line.strip()]



def shorten_for_bullet(text: str, max_chars: int = 220) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"



def first_sentence(paragraph: str) -> str:
    pieces = [piece.strip() for piece in SENTENCE_SPLIT_RE.split(paragraph) if piece.strip()]
    return pieces[0] if pieces else paragraph.strip()



def select_evidence_excerpts(page_texts: list[str], limit: int = 3) -> list[tuple[int, str]]:
    candidates: list[tuple[int, str]] = []
    for page_number, page_text in enumerate(page_texts, start=1):
        for paragraph in extract_paragraphs(page_text):
            compact = " ".join(paragraph.split())
            if 80 <= len(compact) <= 480:
                candidates.append((page_number, compact))

    if not candidates:
        return []

    indices = sorted({0, len(candidates) // 2, len(candidates) - 1})
    excerpts: list[tuple[int, str]] = []
    seen = set()
    for index in indices:
        page_number, text = candidates[index]
        if text in seen:
            continue
        excerpts.append((page_number, text))
        seen.add(text)
        if len(excerpts) == limit:
            break
    return excerpts



def extract_pdf_pages(pdf_path: Path) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "Install pypdf with `python -m pip install -r requirements-source-cleaning.txt` before running source_cleaning.py."
        ) from exc

    reader = PdfReader(str(pdf_path))
    pages = [normalize_page_text(page.extract_text() or "") for page in reader.pages]
    return drop_repeating_lines(pages)
```

- [ ] **Step 4: Run the helper tests to verify the cleaning utilities pass**

Run: `python -m unittest test.test_source_cleaning -v`
Expected: PASS with `test_normalize_page_text_collapses_whitespace ... ok`, `test_drop_repeating_lines_removes_headers_and_footers ... ok`, and `test_select_evidence_excerpts_spreads_quotes_across_document ... ok`

- [ ] **Step 5: Commit the cleaning helpers**

```bash
git add source_cleaning.py test/test_source_cleaning.py
git commit -m "feat: add PDF cleaning helpers for source notes"
```

## Task 4: Add markdown rendering, batch generation, and registry writing

**Files:**
- Modify: `source_cleaning.py`
- Modify: `test/test_source_cleaning.py`

- [ ] **Step 1: Extend the tests to require markdown rendering and registry generation**

```python
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from source_catalog import SourceDocument
from source_cleaning import build_registry_entry, render_clean_markdown, write_source_registry


class SourceRenderingTests(unittest.TestCase):
    def setUp(self):
        self.doc = SourceDocument(
            source_id="sample-001",
            title="Sample Source",
            source_type="official_doc",
            category="apollo",
            language="en",
            raw_relpath="data/sources/raw/apollo/sample.pdf",
            clean_relpath="data/sources/apollo/sample.md",
            origin_url="https://example.com/sample",
            version="Sample v1",
            topic_tags=("perception", "sensor_fusion"),
            summary_hint="Sample summary that should appear in the markdown output.",
        )
        self.page_texts = [
            "Overview paragraph with enough content to become a key point and a structured note. " * 2,
            "Detailed paragraph describing module responsibilities and data flow in enough detail for evidence extraction. " * 2,
            "Constraint paragraph describing operational behavior and interface expectations in enough detail for evidence extraction. " * 2,
        ]

    def test_render_clean_markdown_contains_required_sections(self):
        markdown = render_clean_markdown(self.doc, self.page_texts)
        self.assertIn("# Sample Source", markdown)
        self.assertIn("## Summary", markdown)
        self.assertIn("## Key points", markdown)
        self.assertIn("## Structured notes", markdown)
        self.assertIn("## Evidence-ready excerpts", markdown)
        self.assertIn("## Cleaning notes", markdown)
        self.assertIn("[p.1]", markdown)

    def test_build_registry_entry_points_to_clean_markdown(self):
        entry = build_registry_entry(self.doc)
        self.assertEqual("sample-001", entry["source_id"])
        self.assertEqual("data/sources/apollo/sample.md", entry["path_or_url"])
        self.assertEqual("data/sources/raw/apollo/sample.pdf", entry["raw_path"])
        self.assertEqual(["perception", "sensor_fusion"], entry["topic_tags"])

    def test_write_source_registry_creates_parent_directory(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "data" / "evaluation" / "shared" / "source_registry.json"
            write_source_registry(output_path, [build_registry_entry(self.doc)])
            data = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual("sample-001", data[0]["source_id"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the rendering tests to verify they fail because the renderer and registry helpers do not exist yet**

Run: `python -m unittest test.test_source_cleaning -v`
Expected: FAIL with `ImportError` for `render_clean_markdown`, `build_registry_entry`, or `write_source_registry`

- [ ] **Step 3: Extend `source_cleaning.py` with rendering, batch generation, CLI, and source registry writing**

Append these functions below the helper functions from Task 3:

```python
import argparse
import json
from math import ceil

from source_catalog import REGISTRY_REL_PATH, ROOT, all_documents, documents_for_category



def build_key_points(page_texts: list[str], limit: int = 4) -> list[str]:
    bullets: list[str] = []
    seen = set()
    for page_text in page_texts:
        for paragraph in extract_paragraphs(page_text):
            sentence = shorten_for_bullet(first_sentence(paragraph), max_chars=180)
            if 40 <= len(sentence) <= 180 and sentence not in seen:
                bullets.append(sentence)
                seen.add(sentence)
            if len(bullets) == limit:
                return bullets
    return bullets or ["See structured notes and evidence-ready excerpts for the extracted content."]



def build_structured_sections(page_texts: list[str], max_sections: int = 3) -> list[tuple[str, list[str]]]:
    non_empty_pages = [
        (page_number, page_text)
        for page_number, page_text in enumerate(page_texts, start=1)
        if page_text.strip()
    ]
    if not non_empty_pages:
        return [("Pages 1-1", ["- No extractable text found in the PDF text layer."])]

    group_size = max(1, ceil(len(non_empty_pages) / max_sections))
    sections: list[tuple[str, list[str]]] = []
    for start_index in range(0, len(non_empty_pages), group_size):
        group = non_empty_pages[start_index : start_index + group_size]
        start_page = group[0][0]
        end_page = group[-1][0]
        bullets: list[str] = []
        for page_number, page_text in group:
            for paragraph in extract_paragraphs(page_text)[:2]:
                bullets.append(f"- [p.{page_number}] {shorten_for_bullet(paragraph)}")
                if len(bullets) == 3:
                    break
            if len(bullets) == 3:
                break
        sections.append((f"Pages {start_page}-{end_page}", bullets or [f"- [p.{start_page}] No clean paragraph extracted."]))
    return sections[:max_sections]



def render_clean_markdown(doc: SourceDocument, page_texts: list[str]) -> str:
    key_points = build_key_points(page_texts)
    structured_sections = build_structured_sections(page_texts)
    excerpts = select_evidence_excerpts(page_texts)

    lines = [
        f"# {doc.title}",
        "",
        f"- Source type: {doc.source_type}",
        f"- Category: {doc.category}",
        f"- Original file: {doc.raw_relpath}",
        f"- Original URL: {doc.origin_url}",
        f"- Language: {doc.language}",
        f"- Version: {doc.version}",
        f"- Pages: {len(page_texts)}",
        f"- Topic tags: [{', '.join(doc.topic_tags)}]",
        "",
        "## Summary",
        doc.summary_hint,
        "",
        "## Key points",
    ]

    lines.extend(f"- {point}" for point in key_points)
    lines.extend(["", "## Structured notes"])
    for heading, bullets in structured_sections:
        lines.append(f"### {heading}")
        lines.extend(bullets)
        lines.append("")

    lines.append("## Evidence-ready excerpts")
    if excerpts:
        lines.extend(f"- [p.{page_number}] {text}" for page_number, text in excerpts)
    else:
        lines.append("- No excerpt met the evidence filter; inspect the PDF manually.")

    lines.extend(
        [
            "",
            "## Cleaning notes",
            "- Extracted from the raw PDF text layer using pypdf.",
            "- Repeated header/footer lines were removed when they appeared on most pages.",
            "- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.",
            "- Review this file before using it for Gold Set evidence extraction.",
            "",
        ]
    )
    return "\n".join(lines)



def write_clean_markdown(doc: SourceDocument, markdown: str) -> None:
    doc.clean_path.parent.mkdir(parents=True, exist_ok=True)
    doc.clean_path.write_text(markdown, encoding="utf-8")



def build_registry_entry(doc: SourceDocument) -> dict:
    return {
        "source_id": doc.source_id,
        "title": doc.title,
        "source_type": doc.source_type,
        "category": doc.category,
        "language": doc.language,
        "path_or_url": doc.clean_relpath,
        "raw_path": doc.raw_relpath,
        "origin_url": doc.origin_url,
        "version": doc.version,
        "topic_tags": list(doc.topic_tags),
        "notes": "cleaned from raw PDF with page-level excerpts",
    }



def write_source_registry(output_path: Path, entries: list[dict]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")



def build_documents(category: str, dry_run: bool = False) -> list[Path]:
    docs = all_documents() if category == "all" else documents_for_category(category)
    written_paths: list[Path] = []
    for doc in docs:
        page_texts = extract_pdf_pages(doc.raw_path)
        markdown = render_clean_markdown(doc, page_texts)
        if dry_run:
            print(f"Would generate {doc.clean_relpath}")
        else:
            write_clean_markdown(doc, markdown)
            print(f"Generated {doc.clean_relpath}")
            written_paths.append(doc.clean_path)
    return written_paths



def build_registry(dry_run: bool = False) -> None:
    entries = [build_registry_entry(doc) for doc in all_documents() if doc.clean_path.exists()]
    registry_path = ROOT / REGISTRY_REL_PATH
    if dry_run:
        print(f"Would write {REGISTRY_REL_PATH} with {len(entries)} entries")
        return
    write_source_registry(registry_path, entries)
    print(f"Wrote {REGISTRY_REL_PATH}")



def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild clean markdown notes from raw PDF sources.")
    parser.add_argument(
        "--category",
        choices=("apollo", "standards", "papers", "all"),
        default="all",
        help="Which source category to rebuild.",
    )
    parser.add_argument(
        "--build-registry",
        action="store_true",
        help="Write data/evaluation/shared/source_registry.json after markdown generation.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print which files would be written without modifying the repository.",
    )
    args = parser.parse_args()

    build_documents(category=args.category, dry_run=args.dry_run)
    if args.build_registry:
        build_registry(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the rendering tests and a dry run to verify the end-to-end plumbing works**

Run: `python -m unittest test.test_source_catalog test.test_source_cleaning -v`
Expected: PASS with the catalog tests and rendering tests all green

Run: `python source_cleaning.py --category apollo --dry-run`
Expected: ten lines beginning with `Would generate data/sources/apollo/` and no files written yet

- [ ] **Step 5: Commit the renderer, CLI, and registry writer**

```bash
git add source_cleaning.py test/test_source_cleaning.py
git commit -m "feat: add source markdown builder and registry writer"
```

## Task 5: Generate and verify the Apollo clean markdown files

**Files:**
- Modify: `data/sources/apollo/apollo-devcenter-learning-path.md`
- Modify: `data/sources/apollo/apollo-cyber-rt.md`
- Modify: `data/sources/apollo/apollo-channel-data-format.md`
- Modify: `data/sources/apollo/apollo-open-platform-overview.md`
- Create: `data/sources/apollo/apollo-perception-fusion-overview.md`
- Create: `data/sources/apollo/apollo-vision-perception-overview.md`
- Create: `data/sources/apollo/apollo-vision-prediction-overview.md`
- Create: `data/sources/apollo/apollo-vision-plan-overview.md`
- Create: `data/sources/apollo/apollo-vision-control-overview.md`
- Create: `data/sources/apollo/apollo-vision-location-overview.md`

- [ ] **Step 1: Install the PDF extraction dependency in the active environment**

Run: `python -m pip install -r requirements-source-cleaning.txt`
Expected: PASS with `Successfully installed pypdf` or `Requirement already satisfied: pypdf`

- [ ] **Step 2: Generate the Apollo clean markdown files from raw PDFs**

Run: `python source_cleaning.py --category apollo`
Expected: ten lines beginning with `Generated data/sources/apollo/` and the corresponding markdown files written under `data/sources/apollo/`

- [ ] **Step 3: Validate the generated Apollo files for required sections and obvious noise**

Run:
```bash
python -c "from pathlib import Path; banned=('window.dataLayer','gtag(','Skip to main content'); paths=[
Path('data/sources/apollo/apollo-devcenter-learning-path.md'),
Path('data/sources/apollo/apollo-cyber-rt.md'),
Path('data/sources/apollo/apollo-channel-data-format.md'),
Path('data/sources/apollo/apollo-open-platform-overview.md'),
Path('data/sources/apollo/apollo-perception-fusion-overview.md'),
Path('data/sources/apollo/apollo-vision-perception-overview.md'),
Path('data/sources/apollo/apollo-vision-prediction-overview.md'),
Path('data/sources/apollo/apollo-vision-plan-overview.md'),
Path('data/sources/apollo/apollo-vision-control-overview.md'),
Path('data/sources/apollo/apollo-vision-location-overview.md')];
for path in paths:
    text=path.read_text(encoding='utf-8')
    assert '## Summary' in text, path
    assert '## Key points' in text, path
    assert '## Structured notes' in text, path
    assert '## Evidence-ready excerpts' in text, path
    assert '[p.' in text, path
    assert not any(token in text for token in banned), path
print('apollo outputs ok')"
```
Expected: PASS with `apollo outputs ok`

- [ ] **Step 4: Re-run the unit tests after generating the Apollo documents**

Run: `python -m unittest test.test_source_catalog test.test_source_cleaning -v`
Expected: PASS with all tests green

- [ ] **Step 5: Commit the Apollo clean markdown files**

```bash
git add data/sources/apollo/apollo-devcenter-learning-path.md data/sources/apollo/apollo-cyber-rt.md data/sources/apollo/apollo-channel-data-format.md data/sources/apollo/apollo-open-platform-overview.md data/sources/apollo/apollo-perception-fusion-overview.md data/sources/apollo/apollo-vision-perception-overview.md data/sources/apollo/apollo-vision-prediction-overview.md data/sources/apollo/apollo-vision-plan-overview.md data/sources/apollo/apollo-vision-control-overview.md data/sources/apollo/apollo-vision-location-overview.md
git commit -m "docs: rebuild Apollo source notes from raw PDFs"
```

## Task 6: Generate and verify the standards clean markdown files

**Files:**
- Modify: `data/sources/standards/nhtsa-ads-overview.md`
- Create: `data/sources/standards/ads-2-0-vision-for-safety.md`
- Create: `data/sources/standards/av-3-0-preparing-for-the-future-of-transportation.md`
- Create: `data/sources/standards/av-4-0-ensuring-american-leadership.md`
- Create: `data/sources/standards/nhtsa-ads-safety-overview.md`
- Create: `data/sources/standards/nhtsa-select-ads-activities-overview.md`
- Create: `data/sources/standards/unece-r155-cyber-security-management-system.md`
- Create: `data/sources/standards/unece-r156-software-update-management-system.md`
- Create: `data/sources/standards/unece-r157-alks.md`

- [ ] **Step 1: Generate the standards clean markdown files from raw PDFs**

Run: `python source_cleaning.py --category standards`
Expected: nine lines beginning with `Generated data/sources/standards/` and the corresponding markdown files written under `data/sources/standards/`

- [ ] **Step 2: Validate the generated standards files for required sections and obvious noise**

Run:
```bash
python -c "from pathlib import Path; banned=('window.dataLayer','gtag(','Skip to main content'); paths=[
Path('data/sources/standards/nhtsa-ads-overview.md'),
Path('data/sources/standards/ads-2-0-vision-for-safety.md'),
Path('data/sources/standards/av-3-0-preparing-for-the-future-of-transportation.md'),
Path('data/sources/standards/av-4-0-ensuring-american-leadership.md'),
Path('data/sources/standards/nhtsa-ads-safety-overview.md'),
Path('data/sources/standards/nhtsa-select-ads-activities-overview.md'),
Path('data/sources/standards/unece-r155-cyber-security-management-system.md'),
Path('data/sources/standards/unece-r156-software-update-management-system.md'),
Path('data/sources/standards/unece-r157-alks.md')];
for path in paths:
    text=path.read_text(encoding='utf-8')
    assert '## Summary' in text, path
    assert '## Key points' in text, path
    assert '## Structured notes' in text, path
    assert '## Evidence-ready excerpts' in text, path
    assert '[p.' in text, path
    assert not any(token in text for token in banned), path
print('standards outputs ok')"
```
Expected: PASS with `standards outputs ok`

- [ ] **Step 3: Re-run the unit tests after generating the standards documents**

Run: `python -m unittest test.test_source_catalog test.test_source_cleaning -v`
Expected: PASS with all tests green

- [ ] **Step 4: Commit the standards clean markdown files**

```bash
git add data/sources/standards/nhtsa-ads-overview.md data/sources/standards/ads-2-0-vision-for-safety.md data/sources/standards/av-3-0-preparing-for-the-future-of-transportation.md data/sources/standards/av-4-0-ensuring-american-leadership.md data/sources/standards/nhtsa-ads-safety-overview.md data/sources/standards/nhtsa-select-ads-activities-overview.md data/sources/standards/unece-r155-cyber-security-management-system.md data/sources/standards/unece-r156-software-update-management-system.md data/sources/standards/unece-r157-alks.md
git commit -m "docs: rebuild standards source notes from raw PDFs"
```

## Task 7: Generate the paper clean markdown files and write the source registry

**Files:**
- Modify: `data/sources/papers/bevformer.md`
- Modify: `data/sources/papers/bevfusion.md`
- Modify: `data/sources/papers/occupancy-flow-fields.md`
- Modify: `data/sources/papers/waymo-scalability-perception.md`
- Create: `data/sources/papers/vad.md`
- Create: `data/sources/papers/fusionad.md`
- Create: `data/sources/papers/genad.md`
- Create: `data/evaluation/shared/source_registry.json`

- [ ] **Step 1: Generate the paper clean markdown files from raw PDFs**

Run: `python source_cleaning.py --category papers`
Expected: seven lines beginning with `Generated data/sources/papers/` and the corresponding markdown files written under `data/sources/papers/`

- [ ] **Step 2: Validate the generated paper files for required sections and obvious noise**

Run:
```bash
python -c "from pathlib import Path; banned=('window.dataLayer','gtag(','Skip to main content'); paths=[
Path('data/sources/papers/bevformer.md'),
Path('data/sources/papers/bevfusion.md'),
Path('data/sources/papers/occupancy-flow-fields.md'),
Path('data/sources/papers/waymo-scalability-perception.md'),
Path('data/sources/papers/vad.md'),
Path('data/sources/papers/fusionad.md'),
Path('data/sources/papers/genad.md')];
for path in paths:
    text=path.read_text(encoding='utf-8')
    assert '## Summary' in text, path
    assert '## Key points' in text, path
    assert '## Structured notes' in text, path
    assert '## Evidence-ready excerpts' in text, path
    assert '[p.' in text, path
    assert not any(token in text for token in banned), path
print('paper outputs ok')"
```
Expected: PASS with `paper outputs ok`

- [ ] **Step 3: Generate the source registry from the reviewed clean markdown files**

Run: `python source_cleaning.py --build-registry`
Expected: PASS with `Wrote data/evaluation/shared/source_registry.json`

- [ ] **Step 4: Verify the registry count, uniqueness, and clean-path targets**

Run:
```bash
python -c "import json; from pathlib import Path; registry_path=Path('data/evaluation/shared/source_registry.json'); entries=json.loads(registry_path.read_text(encoding='utf-8')); assert len(entries)==26, len(entries); ids=[entry['source_id'] for entry in entries]; assert len(ids)==len(set(ids)), ids; assert all(entry['path_or_url'].endswith('.md') for entry in entries); assert all(entry['raw_path'].endswith('.pdf') for entry in entries); print('source registry ok')"
```
Expected: PASS with `source registry ok`

- [ ] **Step 5: Run the full unit-test suite for catalog and cleaning one final time**

Run: `python -m unittest test.test_source_catalog test.test_source_cleaning -v`
Expected: PASS with all tests green

- [ ] **Step 6: Commit the paper clean markdown files and source registry**

```bash
git add data/sources/papers/bevformer.md data/sources/papers/bevfusion.md data/sources/papers/occupancy-flow-fields.md data/sources/papers/waymo-scalability-perception.md data/sources/papers/vad.md data/sources/papers/fusionad.md data/sources/papers/genad.md data/evaluation/shared/source_registry.json
git commit -m "docs: rebuild paper source notes and source registry"
```

## Self-Review Checklist

- Spec coverage: this plan covers the catalog, clean markdown structure, raw-PDF-only rebuild rule, three-batch execution order, validation gate, and final `source_registry.json` generation.
- Placeholder scan: no `TODO`, `TBD`, “similar to Task N”, or undefined file references remain.
- Type consistency: `SourceDocument` fields are defined once in `source_catalog.py` and reused consistently by tests, markdown rendering, and registry generation.
