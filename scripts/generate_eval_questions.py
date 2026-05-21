"""Generate evaluation questions for all source documents using LLM."""
import json
import os
import re
import time
import random
from collections import defaultdict
from openai import OpenAI

config = json.load(open("config/runtime_models.json", "r", encoding="utf-8"))
client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])
MODEL = config["chat_model_name"]

REGISTRY_PATH = "data/evaluation/shared/source_registry.json"
EVAL_DIR = "data/evaluation/gold"
TRAIN_DIR = "data/evaluation/train"

SYSTEM_PROMPT = """你是自动驾驶感知领域的评测题生成专家。根据文档内容生成评测题。

严格按以下格式输出，每道题用 === 分隔：

===QUESTION===
DIFFICULTY: easy
TOPIC: 从给定的主题标签中选择一个
Q: 问题（中文）
A: 参考答案（中文）
EVIDENCE: 原文引用（50-200字，保留英文原文）
LOCATOR: page=N 或 section描述
===END===

要求：
1. 每道题必须基于文档中的具体内容，不能编造
2. 生成 3 道题：easy/medium/hard 各一
3. 题目和答案用中文，EVIDENCE 保留原文（英文）
4. EVIDENCE 必须是文档中的原文，50-200字
5. TOPIC 必须从文档提供的主题标签中选择，不要自己发明标签"""


def parse_questions(text, source_id, doc_type, topic_tags):
    """Parse structured text format into question objects."""
    questions = []
    blocks = re.split(r'===QUESTION===', text)
    for block in blocks:
        if '===END===' not in block:
            continue
        block = block.split('===END===')[0].strip()

        difficulty = "medium"
        topic = topic_tags[0] if topic_tags else "autonomous_driving"
        q = ""
        a = ""
        evidence = ""
        locator = ""

        for line in block.split('\n'):
            line = line.strip()
            if line.startswith('DIFFICULTY:'):
                difficulty = line.split(':', 1)[1].strip().lower()
            elif line.startswith('TOPIC:'):
                topic = line.split(':', 1)[1].strip()
            elif line.startswith('Q:'):
                q = line.split(':', 1)[1].strip()
            elif line.startswith('A:'):
                a = line.split(':', 1)[1].strip()
            elif line.startswith('EVIDENCE:'):
                evidence = line.split(':', 1)[1].strip()
            elif line.startswith('LOCATOR:'):
                locator = line.split(':', 1)[1].strip()

        if q and a and evidence:
            questions.append({
                "question": q,
                "reference_answer": a,
                "evidence": [{"quote": evidence, "source_id": source_id, "locator": locator}],
                "metadata": {"difficulty": difficulty, "topic": topic, "doc_type": doc_type}
            })

    return questions


def generate_for_doc(source_id, title, content, doc_type, topic_tags):
    """Generate 3 questions for a single document."""
    max_chars = 12000
    if len(content) > max_chars:
        content = content[:max_chars//2] + "\n\n... (中间省略) ...\n\n" + content[-max_chars//2:]

    topic_str = ", ".join(topic_tags[:5])
    user_msg = f"""文档信息：
- Source ID: {source_id}
- 标题: {title}
- 类型: {doc_type}
- 主题: {topic_str}

文档内容：
{content}

请为这篇文档生成 3 道评测题（easy/medium/hard 各一）。严格按格式输出。"""

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            text = resp.choices[0].message.content.strip()
            questions = parse_questions(text, source_id, doc_type, topic_tags)
            if len(questions) >= 2:
                return questions
            elif attempt < 2:
                time.sleep(1)
                continue
            else:
                print(f"  WARN: only {len(questions)} questions parsed")
                return questions
        except Exception as e:
            print(f"  LLM ERROR (attempt {attempt+1}): {e}")
            if attempt < 2:
                time.sleep(2)
    return []


def main():
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    os.makedirs(TRAIN_DIR, exist_ok=True)

    existing_gold = []
    eval_path = os.path.join(EVAL_DIR, "eval_set.json")
    if os.path.exists(eval_path):
        existing_gold = json.load(open(eval_path, 'r', encoding='utf-8'))

    # Check which source_ids already have questions in existing eval/train sets
    train_path = os.path.join(TRAIN_DIR, "train_set.json")

    existing_eval = []
    existing_train = []
    covered_ids = set()

    if os.path.exists(eval_path):
        existing_eval = json.load(open(eval_path, 'r', encoding='utf-8'))
        for q in existing_eval:
            for ev in q.get('evidence', []):
                covered_ids.add(ev.get('source_id', ''))

    if os.path.exists(train_path):
        existing_train = json.load(open(train_path, 'r', encoding='utf-8'))
        for q in existing_train:
            for ev in q.get('evidence', []):
                covered_ids.add(ev.get('source_id', ''))

    all_new_questions = []
    processed = 0
    skipped = 0
    failed = 0

    for entry in registry:
        source_id = entry["source_id"]
        title = entry["title"]
        md_path = entry["path_or_url"]
        doc_type = entry.get("doc_type", "paper")
        topic_tags = entry.get("topic_tags", [])

        # Skip if already covered
        if source_id in covered_ids:
            skipped += 1
            continue

        if not os.path.exists(md_path):
            print(f"SKIP (no file): {source_id} {title[:40]}")
            continue

        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if len(content) < 500:
            print(f"SKIP (too short): {source_id} {title[:40]}")
            continue

        print(f"Generating: {source_id} - {title[:50]} ...")
        questions = generate_for_doc(source_id, title, content, doc_type, topic_tags)

        if questions:
            all_new_questions.extend(questions)
            processed += 1
            print(f"  OK ({len(questions)} questions)")
        else:
            failed += 1
            print(f"  FAILED")

        time.sleep(0.5)

    # Combine with existing
    all_questions = existing_eval + existing_train + all_new_questions

    # Group questions by source_id
    by_source = defaultdict(list)
    for q in all_questions:
        sid = ""
        for ev in q.get('evidence', []):
            sid = ev.get('source_id', '')
            break
        if sid:
            by_source[sid].append(q)
        else:
            by_source['_no_source'].append(q)

    # Split: ensure each source has at least 1 question in eval
    random.seed(42)
    eval_questions = []
    train_questions = []

    for sid, qs in by_source.items():
        random.shuffle(qs)
        if sid == '_no_source':
            train_questions.extend(qs)
        elif len(qs) == 1:
            eval_questions.append(qs[0])
        else:
            eval_questions.append(qs[0])
            train_questions.extend(qs[1:])

    # If eval > 100, move excess to train
    if len(eval_questions) > 100:
        random.shuffle(eval_questions)
        train_questions.extend(eval_questions[100:])
        eval_questions = eval_questions[:100]
    elif len(eval_questions) < 100:
        # Move some from train to eval
        random.shuffle(train_questions)
        needed = 100 - len(eval_questions)
        eval_questions.extend(train_questions[:needed])
        train_questions = train_questions[needed:]

    # Re-number
    random.shuffle(eval_questions)
    random.shuffle(train_questions)
    for i, q in enumerate(eval_questions):
        q["id"] = f"eval-{i+1:03d}"
    for i, q in enumerate(train_questions):
        q["id"] = f"train-{i+1:03d}"

    # Save
    with open(eval_path, 'w', encoding='utf-8') as f:
        json.dump(eval_questions, f, indent=2, ensure_ascii=False)

    with open(train_path, 'w', encoding='utf-8') as f:
        json.dump(train_questions, f, indent=2, ensure_ascii=False)

    # Update compat files
    with open(os.path.join(EVAL_DIR, "gold_set_extended.json"), 'w', encoding='utf-8') as f:
        json.dump(eval_questions, f, indent=2, ensure_ascii=False)
    with open(os.path.join(EVAL_DIR, "gold_set_100.json"), 'w', encoding='utf-8') as f:
        json.dump(eval_questions, f, indent=2, ensure_ascii=False)

    print(f"\n=== Results ===")
    print(f"Processed: {processed}")
    print(f"Skipped (already covered): {skipped}")
    print(f"Failed: {failed}")
    print(f"New questions: {len(all_new_questions)}")
    print(f"Total questions: {len(all_questions)}")
    print(f"Eval set: {len(eval_questions)} -> {eval_path}")
    print(f"Train set: {len(train_questions)} -> {train_path}")


if __name__ == "__main__":
    main()
