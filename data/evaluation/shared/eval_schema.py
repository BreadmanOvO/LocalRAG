REQUIRED_TOP_LEVEL_KEYS = {"id", "question", "reference_answer", "evidence", "metadata"}
REQUIRED_EVIDENCE_KEYS = {"quote", "source_id", "locator"}
REQUIRED_METADATA_KEYS = {"difficulty", "topic", "doc_type"}


def _require_non_empty_string(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def validate_record(record):
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")

    missing_keys = REQUIRED_TOP_LEVEL_KEYS - record.keys()
    if missing_keys:
        raise ValueError(f"missing required keys: {sorted(missing_keys)}")

    for key in ("id", "question", "reference_answer"):
        _require_non_empty_string(record[key], key)

    evidence = record["evidence"]
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("evidence must be a non-empty list")

    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("evidence entries must be dicts")
        missing_evidence_keys = REQUIRED_EVIDENCE_KEYS - item.keys()
        if missing_evidence_keys:
            raise ValueError(f"missing evidence keys: {sorted(missing_evidence_keys)}")
        for key in REQUIRED_EVIDENCE_KEYS:
            _require_non_empty_string(item[key], key)

    metadata = record["metadata"]
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict")

    missing_metadata_keys = REQUIRED_METADATA_KEYS - metadata.keys()
    if missing_metadata_keys:
        raise ValueError(f"missing metadata keys: {sorted(missing_metadata_keys)}")

    for key in REQUIRED_METADATA_KEYS:
        _require_non_empty_string(metadata[key], key)


def validate_dataset(records):
    seen_ids = set()
    for record in records:
        validate_record(record)
        record_id = record["id"]
        if record_id in seen_ids:
            raise ValueError(f"duplicate record id: {record_id}")
        seen_ids.add(record_id)
