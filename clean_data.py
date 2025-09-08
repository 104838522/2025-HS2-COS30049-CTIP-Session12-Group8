#!/usr/bin/env python3
import os
import re
import json
import csv
import pathlib
from typing import Iterable, Dict, Any, List, Tuple

import pandas as pd

# ========= USER CONFIG =========
DATA_PATH = "/Users/gianniedwards-hernandez/Desktop/uni/2025_s2/Technology_Innovation_project/Assignment Datasets/3sv/basic_data_3.jsonl"
# ===============================

REQUIRED_KEYS = {
    "id",
    "language",
    "vulnerability_type",
    "description",
    "code_snippet",
    "exploitation_techniques",
    "mitigation",
}

CONTROL_CHARS_REGEX = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def strip_bom(text: str) -> str:
    return text[1:] if text and text[0] == "\ufeff" else text


def remove_control_chars(text: str) -> str:
    # Keep \n \r \t; remove other ASCII control chars
    return CONTROL_CHARS_REGEX.sub("", text)


def iter_top_level_json_objects(text: str) -> Iterable[str]:
    """
    Robustly split pretty-printed, concatenated JSON objects.
    Ignores braces inside strings and yields each complete top-level object as a string.
    Skips leading noise before the first '{'.
    """
    text = strip_bom(text)
    i, n = 0, len(text)
    in_string = False
    escape = False
    depth = 0
    buf: List[str] = []
    started = False

    while i < n:
        ch = text[i]
        if not started:
            if ch == "{":
                started = True
                depth = 1
                buf = ["{"]
            i += 1
            continue

        buf.append(ch)

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    yield "".join(buf)
                    buf = []
                    started = False
        i += 1


def read_json_like_records(
    path: pathlib.Path,
) -> Tuple[List[Dict[str, Any]], List[Tuple[int, str]]]:
    """
    Read JSON/JSONL or concatenated pretty-printed JSON objects.
    Returns (records, malformed_info) where malformed_info holds (index, reason).
    """
    text = path.read_text(encoding="utf-8")
    text = remove_control_chars(text)

    records: List[Dict[str, Any]] = []
    malformed: List[Tuple[int, str]] = []

    stripped = text.lstrip()

    # Case 1: A proper JSON array
    if stripped.startswith("["):
        try:
            data = json.loads(stripped)
            if isinstance(data, list):
                for i, obj in enumerate(data, start=1):
                    if isinstance(obj, dict):
                        records.append(obj)
                    else:
                        malformed.append(
                            (i, "Top-level array element is not an object")
                        )
            else:
                malformed.append((0, "Top-level JSON is not an array of objects"))
        except Exception as e:
            malformed.append((0, f"Failed to parse JSON array: {e}"))
        return records, malformed

    # Case 2: Try JSONL (one object per line)
    lines = [ln for ln in text.splitlines() if ln.strip()]
    jsonl_parsed = True
    tmp: List[Dict[str, Any]] = []
    line_errors = 0
    for i, ln in enumerate(lines, start=1):
        try:
            obj = json.loads(ln)
            if isinstance(obj, dict):
                tmp.append(obj)
            else:
                jsonl_parsed = False
                line_errors += 1
                break
        except Exception:
            jsonl_parsed = False
            line_errors += 1
            break

    if jsonl_parsed and tmp:
        return tmp, malformed

    # Case 3: Fallback – concatenated pretty-printed objects
    idx = 0
    for obj_text in iter_top_level_json_objects(text):
        idx += 1
        try:
            obj = json.loads(obj_text)
            if isinstance(obj, dict):
                records.append(obj)
            else:
                malformed.append((idx, "Chunk is not a JSON object"))
        except Exception as e:
            malformed.append((idx, f"Invalid JSON object: {e}"))

    return records, malformed


def validate_exact_keys(rec: Dict[str, Any]) -> bool:
    return set(rec.keys()) == REQUIRED_KEYS


def filter_valid_records(
    records: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Tuple[int, str]]]:
    valid: List[Dict[str, Any]] = []
    bad: List[Tuple[int, str]] = []
    for i, r in enumerate(records, start=1):
        k = set(r.keys())
        if k == REQUIRED_KEYS:
            valid.append(r)
        else:
            reason = (
                f"Expected exactly 7 keys, got {len(k)} "
                f"(missing={sorted(REQUIRED_KEYS - k)}, extra={sorted(k - REQUIRED_KEYS)})"
            )
            bad.append((i, reason))
    return valid, bad


def write_clean_jsonl(path: pathlib.Path, records: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def read_csv_records(
    path: pathlib.Path,
) -> Tuple[List[Dict[str, Any]], List[Tuple[int, str]]]:
    records: List[Dict[str, Any]] = []
    malformed: List[Tuple[int, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])
        # We enforce EXACTLY the 7 required columns per instruction.
        if headers != REQUIRED_KEYS:
            malformed.append(
                (
                    0,
                    f"CSV headers must match exactly the 7 required keys. "
                    f"Found {len(headers)} headers: {sorted(headers)}",
                )
            )
            return records, malformed
        for i, row in enumerate(reader, start=1):
            # DictReader always gives the same headers; presence is guaranteed.
            # We still allow empty values, since the rule is about parameters (keys), not value completeness.
            records.append({k: row.get(k, "") for k in REQUIRED_KEYS})
    return records, malformed


def write_clean_csv(path: pathlib.Path, records: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(REQUIRED_KEYS))
        writer.writeheader()
        for rec in records:
            writer.writerow({k: rec.get(k, "") for k in REQUIRED_KEYS})


def main():
    src = pathlib.Path(DATA_PATH)
    if not src.exists():
        raise FileNotFoundError(f"File not found: {src}")

    ext = src.suffix.lower()
    # Build output path named "clean_data_test" with the same extension
    out_path = src.with_name("clean_data_test" + ext)
    report_path = src.with_name("clean_data_test_report.txt")

    all_records: List[Dict[str, Any]] = []
    malformed_info: List[Tuple[int, str]] = []

    if ext in (".json", ".jsonl"):
        raw_records, malformed = read_json_like_records(src)
        malformed_info.extend(malformed)
        valid_records, key_malformed = filter_valid_records(raw_records)
        malformed_info.extend(key_malformed)

        # Write cleaned duplicate file
        write_clean_jsonl(out_path, valid_records)

    elif ext == ".csv":
        raw_records, malformed = read_csv_records(src)
        malformed_info.extend(malformed)
        if raw_records:
            # For CSV, headers are exact by construction (or we aborted above).
            # Still check each row for exactly the 7 keys (always true for DictReader).
            valid_records, key_malformed = filter_valid_records(raw_records)
            malformed_info.extend(key_malformed)
        else:
            valid_records = []

        write_clean_csv(out_path, valid_records)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use .json, .jsonl, or .csv")

    # Build DataFrame from valid records only
    if valid_records:
        df = pd.DataFrame(valid_records)
        print("DataFrame shape (valid only):", df.shape)
        print(df.head())
    else:
        print("No valid records found; DataFrame will be empty.")
        df = pd.DataFrame(columns=sorted(REQUIRED_KEYS))

    # Save a short report
    with report_path.open("w", encoding="utf-8") as r:
        r.write(f"Source file: {src}\n")
        r.write(f"Cleaned duplicate: {out_path}\n\n")
        r.write(f"Valid records: {len(valid_records)}\n")
        r.write(f"Malformed records: {len(malformed_info)}\n")
        if malformed_info:
            r.write("\nExamples of malformed (up to 20):\n")
            for i, (idx, reason) in enumerate(malformed_info[:20], start=1):
                r.write(f"{i:02d}. Record #{idx}: {reason}\n")

    print(f"\nWrote cleaned duplicate to: {out_path}")
    print(f"Wrote cleaning report to: {report_path}")


if __name__ == "__main__":
    main()
