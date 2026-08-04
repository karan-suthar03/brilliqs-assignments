"""CSV to JSON Lines conversion. No AWS dependencies so it can be unit tested."""

import codecs
import csv
import json
import re
from pathlib import PurePosixPath

_NON_ALNUM = re.compile(r"[^0-9a-z]+")

OUTPUT_PREFIX = "processed/"


def output_prefix(input_key: str) -> str:
    # Everything before the timestamp, so callers can find the output without
    # knowing when it was written.
    path = PurePosixPath(input_key)
    folders = str(path.parent) if path.parent != PurePosixPath(".") else ""
    parts = [OUTPUT_PREFIX.strip("/"), folders, f"{path.stem}_"]
    return "/".join(part for part in parts if part)


def output_key(input_key: str, stamp: str) -> str:
    return f"{output_prefix(input_key)}{stamp}.jsonl"


def normalise_headers(raw_headers: list[str]) -> list[str]:
    normalised: list[str] = []
    seen: dict[str, int] = {}

    for position, raw in enumerate(raw_headers):
        name = _NON_ALNUM.sub("_", raw.strip().lower()).strip("_")
        if not name:
            name = f"column_{position}"

        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 1

        normalised.append(name)

    return normalised


def csv_to_jsonl(binary_stream):
    reader = csv.DictReader(codecs.getreader("utf-8-sig")(binary_stream))
    rename = dict(zip(reader.fieldnames, normalise_headers(reader.fieldnames)))

    for row in reader:
        record = {rename[key]: (value or "").strip() or None
                  for key, value in row.items()}
        yield (json.dumps(record, ensure_ascii=False) + "\n").encode("utf-8")
