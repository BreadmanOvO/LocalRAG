import argparse
import json
import statistics
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_SEPARATORS = ["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]
DEFAULT_PAIRS = [(600, 100), (1000, 100), (1200, 200)]


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def evaluate_split(text: str, chunk_size: int, chunk_overlap: int, separators: list[str]) -> dict:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
        length_function=len,
    )
    chunks = splitter.split_text(text)
    lengths = [len(c) for c in chunks]

    if not lengths:
        return {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "chunk_count": 0,
            "avg_length": 0,
            "min_length": 0,
            "max_length": 0,
            "p90_length": 0,
            "short_chunk_ratio_lt200": 0.0,
            "text_coverage_chars": 0,
        }

    p90_index = max(0, int(len(lengths) * 0.9) - 1)
    lengths_sorted = sorted(lengths)
    short_ratio = sum(1 for n in lengths if n < 200) / len(lengths)
    return {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "chunk_count": len(chunks),
        "avg_length": round(statistics.mean(lengths), 2),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "p90_length": lengths_sorted[p90_index],
        "short_chunk_ratio_lt200": round(short_ratio, 3),
        "text_coverage_chars": sum(lengths),
    }


def parse_pairs(raw_pairs: str | None) -> list[tuple[int, int]]:
    if not raw_pairs:
        return DEFAULT_PAIRS
    pairs: list[tuple[int, int]] = []
    for item in raw_pairs.split(","):
        size, overlap = item.strip().split(":")
        pairs.append((int(size), int(overlap)))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark chunk_size/chunk_overlap for LocalRAG.")
    parser.add_argument("--input", required=True, help="UTF-8 text file path used for split benchmark.")
    parser.add_argument(
        "--pairs",
        default=None,
        help='Chunk setting pairs, format: "600:100,1000:100,1200:200".',
    )
    parser.add_argument(
        "--separators-json",
        default=None,
        help='Optional separators json list, e.g. \'["\\n\\n","\\n","。"," ",""]\'.',
    )
    parser.add_argument("--out", default=None, help="Optional output json path.")

    args = parser.parse_args()
    input_path = Path(args.input).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    text = load_text(input_path)
    pairs = parse_pairs(args.pairs)
    separators = json.loads(args.separators_json) if args.separators_json else DEFAULT_SEPARATORS

    results = []
    for chunk_size, chunk_overlap in pairs:
        if chunk_overlap >= chunk_size:
            raise ValueError(f"Invalid pair {chunk_size}:{chunk_overlap}, overlap must be < chunk_size")
        result = evaluate_split(text=text, chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=separators)
        results.append(result)

    print(f"Input: {input_path}")
    print(f"Text length: {len(text)} chars")
    print("-" * 88)
    print(
        f"{'chunk_size':>10} {'overlap':>8} {'chunks':>8} {'avg_len':>10} "
        f"{'min':>6} {'max':>6} {'p90':>6} {'short<200':>10}"
    )
    print("-" * 88)
    for row in results:
        print(
            f"{row['chunk_size']:>10} {row['chunk_overlap']:>8} {row['chunk_count']:>8} "
            f"{row['avg_length']:>10} {row['min_length']:>6} {row['max_length']:>6} "
            f"{row['p90_length']:>6} {row['short_chunk_ratio_lt200']:>10}"
        )
    print("-" * 88)
    print("Tips:")
    print("- chunk_count 过大 + short<200 比例过高，通常说明切得太碎。")
    print("- max_length 经常接近 chunk_size，说明文档段落较长，可适当增大 overlap。")
    print("- 先选 2~3 组候选，再用真实问题做召回命中验证。")

    if args.out:
        out_path = Path(args.out).resolve()
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved json report to: {out_path}")


if __name__ == "__main__":
    main()
