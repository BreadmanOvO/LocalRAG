from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from math import ceil
from pathlib import Path

from source_catalog import REGISTRY_REL_PATH, ROOT, SourceDocument, all_documents, documents_for_category

WHITESPACE_RE = re.compile(r"[ \t\xa0\u3000]+")
PARAGRAPH_SPLIT_RE = re.compile(r"\n{2,}")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？.!?])\s+")
SENTENCE_END_RE = re.compile(r"[。！？.!?]$")
ABSTRACT_RE = re.compile(r"\babstract\b[:\s-]*", re.IGNORECASE)
INTRODUCTION_RE = re.compile(r"(?:^|\s)(?:\d+(?:\.\d+)*)?\s*introduction\b[:\s-]*", re.IGNORECASE)
DOC_CODE_RE = re.compile(r"^E/ECE/TRANS/[^\s]+(?:\s*-\s*\d+\s*-?)?\s*", re.IGNORECASE)
CITATION_RE = re.compile(r"\[\d+\]")
LEADING_CITATION_RE = re.compile(r"^\[\d+\]")
DOT_LEADER_RE = re.compile(r"\.{5,}")
PAGE_NUMBER_RE = re.compile(r"^\d+(?:/\d+)?$")
URL_LINE_RE = re.compile(r"https?://\S+", re.IGNORECASE)
LOW_SIGNAL_MARKERS = (
    "agreement concerning the adoption",
    "former titles of the agreement",
    "this document is meant purely as documentation tool",
    "united nations",
    "contents page",
    "communication no",
    "test report no",
    "approval communication",
    "name of administration",
    "issued by:",
    "approval mark",
    "arxiv preprint",
)
CONTENT_START_MARKERS = (
    ("Through this course", True),
    ("概览", False),
)
TRAILING_NOISE_MARKERS = (
    "文档意见反馈",
    "参考文献",
    "详情参见",
    "FollowUs",
    "Scan the QR code",
    "Join Apollo Developer communication group",
    "Apollo Road Map",
    "WeChat: Apollodev",
    "Congratulations",
)
INLINE_NOISE_PATTERNS = (
    re.compile(r"\b\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}\b"),
    re.compile(r"Apollo开放平台文档"),
    re.compile(r"Q搜索"),
    re.compile(r"发版说明|安装说明|快速上手|上机使用教程|上车使用教程|常见问题"),
    re.compile(r"实时通信框架CyberRT的使用>?"),
    re.compile(r"更新时间[:：]\s*\d{4}-\d{2}-\d{2}"),
    re.compile(r"上机实践Apollo[\u4e00-\u9fffA-Za-z]+"),
    re.compile(r"基于Dreamland调试控制能力实践"),
    re.compile(r"使用MSFLocalizer的多传感\s*器融合定位实践"),
    re.compile(r"基于MSFVisualizer的Apollo\s*定位可视化实践"),
    re.compile(r"ing with VCV"),
    re.compile(r"position/velcity/attitu"),
    re.compile(r"\(AA\) axueyen-oo pue"),
)
NAV_MARKERS = (
    "q搜索",
    "上机使用教程",
    "上车使用教程",
    "文档意见反馈",
    "followus",
    "wechat",
    "scan the qr",
    "join apollo developer communication group",
)
OCR_KEEP_LINE_MARKERS = (
    "through this course",
    "you will be able to",
    "本文档介绍",
    "高精度",
    "利用gps+imu",
    "结合gps+imu+lidar",
    "这里重点介绍",
    "msf定位系统",
    "the course instructors",
)
OCR_FIGURE_TEXT_MARKERS = (
    "specific force and rotation rate",
    "predicted prior pva with vcv",
    "observed posterior",
    "raw gnss",
    "raw gns5",
    "position/velocity with vcv",
    "point clouds",
    "database",
    "prior lidar map",
    "prior ludar map",
    "gnss localization",
    "lidar localization",
    "de (pva) with varli",
)
_OCR_ENGINE = None



def normalize_page_text(text: str) -> str:
    text = text.replace("\r", "")
    paragraphs = []
    for block in PARAGRAPH_SPLIT_RE.split(text):
        lines = [WHITESPACE_RE.sub(" ", line).strip() for line in block.splitlines()]
        cleaned_lines = [line for line in lines if line]
        if cleaned_lines:
            paragraphs.append(" ".join(cleaned_lines))
    return "\n\n".join(paragraphs)



def _is_nav_like_ocr_line(line: str) -> bool:
    compact = " ".join(line.split()).strip()
    if not compact:
        return True

    lowered = compact.lower()
    if any(marker in lowered for marker in OCR_KEEP_LINE_MARKERS):
        return False
    if any(marker in lowered for marker in OCR_FIGURE_TEXT_MARKERS):
        return True
    if any(marker in lowered for marker in NAV_MARKERS):
        return True
    if PAGE_NUMBER_RE.match(compact):
        return True
    if URL_LINE_RE.search(compact):
        return True
    if compact in {"Apollo", "Open Platform", "Developer Center", "Lesson Structrue", "中文"}:
        return True
    if compact.startswith(("Apollo开放平台文档", "Apollo定位能力介绍", "上机实践Apollo", "使用MSFLocalizer", "基于MSFVisualizer")):
        return True
    if compact in {"HDMap", "Localization", "Perception", "Prediction", "Planning", "Control"}:
        return True
    if compact in {"FollowUs", "Apollo Road Map", "Courseinstructors"}:
        return True
    if len(compact) <= 3 and not SENTENCE_END_RE.search(compact):
        return True
    if compact.isascii() and len(compact.split()) <= 3 and compact[:1].isupper() and not SENTENCE_END_RE.search(compact):
        return True
    return False



def _starts_new_ocr_paragraph(previous: str, current: str) -> bool:
    if not previous:
        return True
    if SENTENCE_END_RE.search(previous):
        return True
    if len(previous) >= 90:
        return True
    if current[:1].isupper() and previous[:1].isupper():
        return True
    return False



def _merge_ocr_continuation_lines(lines: list[str]) -> list[str]:
    merged: list[str] = []
    for line in lines:
        if not merged:
            merged.append(line)
            continue

        previous = merged[-1]
        if line[:1].islower():
            merged[-1] = f"{previous} {line}".strip()
            continue
        if previous[:1].islower() and len(previous.split()) <= 4:
            merged[-1] = f"{previous} {line}".strip()
            continue
        merged.append(line)
    return merged



def assemble_ocr_page_text(lines: list[str]) -> str:
    cleaned_lines = [WHITESPACE_RE.sub(" ", line).strip() for line in lines]
    kept_lines = [line for line in cleaned_lines if line and not _is_nav_like_ocr_line(line)]
    kept_lines = _merge_ocr_continuation_lines(kept_lines)
    if not kept_lines:
        return ""

    paragraphs: list[list[str]] = []
    current: list[str] = []
    for line in kept_lines:
        if _starts_new_ocr_paragraph(current[-1], line) if current else True:
            if current:
                paragraphs.append(current)
            current = [line]
            continue
        current.append(line)

    if current:
        paragraphs.append(current)

    return normalize_page_text("\n\n".join("\n".join(paragraph) for paragraph in paragraphs))



def _cluster_ocr_columns(records: list[dict], page_width: float) -> list[list[dict]]:
    if not records:
        return []

    gap_threshold = max(120.0, page_width * 0.12)
    clusters: list[list[dict]] = []
    for record in sorted(records, key=lambda item: item["xc"]):
        if not clusters:
            clusters.append([record])
            continue
        previous_cluster = clusters[-1]
        previous_x = max(item["xc"] for item in previous_cluster)
        if record["xc"] - previous_x > gap_threshold:
            clusters.append([record])
            continue
        previous_cluster.append(record)
    return clusters



def _should_drop_ocr_column(cluster: list[dict], page_width: float) -> bool:
    if not cluster:
        return True

    texts = [item["text"] for item in cluster]
    nav_like_count = sum(_is_nav_like_ocr_line(text) for text in texts)
    avg_left = sum(item["x0"] for item in cluster) / len(cluster)
    avg_width = sum(item["width"] for item in cluster) / len(cluster)
    return (
        avg_left < page_width * 0.3
        and avg_width < page_width * 0.28
        and nav_like_count >= max(1, ceil(len(cluster) * 0.3))
    )



def _assemble_ocr_narrow_band(records: list[dict], page_width: float) -> str:
    parts: list[str] = []
    for cluster in _cluster_ocr_columns(records, page_width):
        if _should_drop_ocr_column(cluster, page_width):
            continue
        lines = [item["text"] for item in sorted(cluster, key=lambda item: (item["y0"], item["x0"]))]
        text = assemble_ocr_page_text(lines)
        if text:
            parts.append(text)
    return "\n\n".join(parts)



def _is_ocr_figure_label_band(records: list[dict]) -> bool:
    texts = [record["text"] for record in records]
    lowered = " ".join(text.lower() for text in texts)
    return sum(marker in lowered for marker in OCR_FIGURE_TEXT_MARKERS) >= 2



def assemble_ocr_page_text_from_items(items: list) -> str:
    records: list[dict] = []
    for item in items or []:
        if len(item) < 2:
            continue
        box = item[0]
        text = WHITESPACE_RE.sub(" ", item[1]).strip()
        if not text:
            continue
        xs = [point[0] for point in box]
        ys = [point[1] for point in box]
        records.append(
            {
                "text": text,
                "x0": min(xs),
                "x1": max(xs),
                "y0": min(ys),
                "y1": max(ys),
                "xc": (min(xs) + max(xs)) / 2,
                "width": max(xs) - min(xs),
            }
        )

    if not records:
        return ""

    page_width = max(record["x1"] for record in records)
    wide_threshold = max(280.0, page_width * 0.42)
    ordered = sorted(records, key=lambda item: (item["y0"], item["x0"]))

    bands: list[tuple[str, list[dict]]] = []
    current_kind = "wide" if ordered[0]["width"] >= wide_threshold else "narrow"
    current_band: list[dict] = [ordered[0]]
    for record in ordered[1:]:
        kind = "wide" if record["width"] >= wide_threshold else "narrow"
        vertical_gap = record["y0"] - current_band[-1]["y1"]
        if kind != current_kind or vertical_gap > 40:
            bands.append((current_kind, current_band))
            current_kind = kind
            current_band = [record]
            continue
        current_band.append(record)
    bands.append((current_kind, current_band))

    sections: list[str] = []
    for kind, band in bands:
        if kind == "wide":
            if _is_ocr_figure_label_band(band):
                continue
            text = assemble_ocr_page_text([item["text"] for item in band])
        else:
            text = _assemble_ocr_narrow_band(band, page_width)
        if text:
            sections.append(text)
    return "\n\n".join(sections)



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



def trim_to_content_start(text: str) -> str:
    for marker, keep_marker in CONTENT_START_MARKERS:
        index = text.find(marker)
        if 0 <= index < 1200:
            return text[index if keep_marker else index + len(marker) :].strip()
    return text



def strip_trailing_noise(text: str) -> str:
    lowered = text.lower()
    end = len(text)
    for marker in TRAILING_NOISE_MARKERS:
        index = lowered.find(marker.lower())
        if index != -1:
            end = min(end, index)
    return text[:end].strip()



def remove_inline_noise(text: str) -> str:
    cleaned = text
    for pattern in INLINE_NOISE_PATTERNS:
        cleaned = pattern.sub(" ", cleaned)
    return cleaned



def normalize_candidate_text(text: str) -> str:
    compact = " ".join(text.split()).strip()
    if not compact:
        return ""

    compact = DOC_CODE_RE.sub("", compact).strip()
    compact = trim_to_content_start(compact)

    abstract_match = ABSTRACT_RE.search(compact)
    if abstract_match and abstract_match.start() < 1200:
        compact = compact[abstract_match.end() :].strip()
    else:
        introduction_match = INTRODUCTION_RE.search(compact)
        if introduction_match and introduction_match.start() < 1200:
            compact = compact[introduction_match.end() :].strip()

    compact = strip_trailing_noise(compact)
    compact = remove_inline_noise(compact)
    compact = INTRODUCTION_RE.sub("", compact, count=1).strip()
    compact = " ".join(compact.split()).strip()
    return compact



def is_low_signal_text(text: str) -> bool:
    raw_lowered = text.lower()
    if any(marker in raw_lowered for marker in ("followus", "scan the qr", "wechat", "join apollo developer communication group")):
        return True

    compact = normalize_candidate_text(text)
    if not compact:
        return True

    lowered = compact.lower()
    if DOT_LEADER_RE.search(compact):
        return True
    if compact.count("@") >= 1:
        return True
    if LEADING_CITATION_RE.match(compact):
        return True
    if len(CITATION_RE.findall(compact)) >= 3:
        return True
    if lowered.startswith(("references", "appendix", "figure ", "table ")):
        return True
    if "ground truth prediction" in lowered or "visualization results" in lowered:
        return True
    if lowered.count("figure ") >= 2 or lowered.count("table ") >= 2:
        return True
    if any(marker in lowered for marker in ("followus", "scan the qr", "wechat", "join apollo developer communication group")):
        return True
    if sum(marker in lowered for marker in NAV_MARKERS) >= 2:
        return True
    if any(marker in lowered for marker in LOW_SIGNAL_MARKERS):
        return True
    return False



def split_candidate_text(text: str, min_chars: int = 80, max_chars: int = 480) -> list[str]:
    compact = normalize_candidate_text(text)
    if not compact or is_low_signal_text(compact):
        return []
    if min_chars <= len(compact) <= max_chars:
        return [compact]
    if len(compact) <= max_chars:
        return []

    pieces = [piece.strip() for piece in SENTENCE_SPLIT_RE.split(compact) if piece.strip()]
    if len(pieces) <= 1:
        return []

    candidates: list[str] = []
    window: list[str] = []
    for piece in pieces:
        combined = " ".join(window + [piece]).strip() if window else piece
        if len(combined) <= max_chars:
            window.append(piece)
            continue

        excerpt = " ".join(window).strip()
        if min_chars <= len(excerpt) <= max_chars and not is_low_signal_text(excerpt):
            candidates.append(excerpt)
        window = [piece]

    excerpt = " ".join(window).strip()
    if min_chars <= len(excerpt) <= max_chars and not is_low_signal_text(excerpt):
        candidates.append(excerpt)
    return candidates



def extract_candidate_snippets(page_text: str, min_chars: int = 80, max_chars: int = 480) -> list[str]:
    snippets: list[str] = []
    for paragraph in extract_paragraphs(page_text):
        snippets.extend(split_candidate_text(paragraph, min_chars=min_chars, max_chars=max_chars))
    return snippets



def select_evidence_excerpts(page_texts: list[str], limit: int = 3) -> list[tuple[int, str]]:
    candidates: list[tuple[int, str]] = []
    for page_number, page_text in enumerate(page_texts, start=1):
        for snippet in extract_candidate_snippets(page_text):
            candidates.append((page_number, snippet))

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



def _get_ocr_engine():
    global _OCR_ENGINE
    if _OCR_ENGINE is not None:
        return _OCR_ENGINE
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Install OCR dependencies with `python -m pip install -r requirements-source-cleaning.txt` before using OCR fallback."
        ) from exc
    _OCR_ENGINE = RapidOCR()
    return _OCR_ENGINE



def extract_pdf_pages_with_ocr(pdf_path: Path) -> list[str]:
    try:
        import fitz
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Install OCR dependencies with `python -m pip install -r requirements-source-cleaning.txt` before using OCR fallback."
        ) from exc

    ocr = _get_ocr_engine()
    document = fitz.open(str(pdf_path))
    pages: list[str] = []
    for page in document:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        result, _ = ocr(image)
        pages.append(assemble_ocr_page_text_from_items(result or []))
    return drop_repeating_lines(pages)



def extract_pdf_pages(pdf_path: Path) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "Install pypdf with `python -m pip install -r requirements-source-cleaning.txt` before running source_cleaning.py."
        ) from exc

    reader = PdfReader(str(pdf_path))
    pages = [normalize_page_text(page.extract_text() or "") for page in reader.pages]
    if any(page.strip() for page in pages):
        return drop_repeating_lines(pages)
    return extract_pdf_pages_with_ocr(pdf_path)



def build_key_points(page_texts: list[str], limit: int = 4) -> list[str]:
    bullets: list[str] = []
    seen = set()
    for page_text in page_texts:
        for snippet in extract_candidate_snippets(page_text):
            sentence = shorten_for_bullet(first_sentence(snippet), max_chars=180)
            if 40 <= len(sentence) <= 180 and not is_low_signal_text(sentence) and sentence not in seen:
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
        end_page = max(1, len(page_texts))
        return [(f"Pages 1-{end_page}", ["- [p.1] No extractable text found in the PDF text layer."])]

    group_size = max(1, ceil(len(non_empty_pages) / max_sections))
    sections: list[tuple[str, list[str]]] = []
    for start_index in range(0, len(non_empty_pages), group_size):
        group = non_empty_pages[start_index : start_index + group_size]
        start_page = group[0][0]
        end_page = group[-1][0]
        bullets: list[str] = []
        for page_number, page_text in group:
            for snippet in extract_candidate_snippets(page_text):
                bullets.append(f"- [p.{page_number}] {shorten_for_bullet(snippet)}")
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
            "- OCR fallback is used when the PDF has no extractable text layer.",
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
