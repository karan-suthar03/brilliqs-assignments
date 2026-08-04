"""List the converted JSONL files in the output bucket.

    python scripts/list_output.py
    python scripts/list_output.py --prefix processed/incoming/2026
"""

import argparse

from common import session_and_buckets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", default="processed/")
    args = parser.parse_args()

    session, _, output_bucket = session_and_buckets()
    s3 = session.client("s3")

    objects = []
    for page in s3.get_paginator("list_objects_v2").paginate(
        Bucket=output_bucket, Prefix=args.prefix
    ):
        objects.extend(page.get("Contents", []))

    for obj in sorted(objects, key=lambda o: o["LastModified"], reverse=True):
        print(f"{obj['LastModified']:%Y-%m-%d %H:%M}  {obj['Size']:>12,}  {obj['Key']}")


if __name__ == "__main__":
    main()
