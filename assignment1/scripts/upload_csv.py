"""Upload a CSV to the input bucket, which fires the Lambda.

    python scripts/upload_csv.py data/users.csv
    python scripts/upload_csv.py data/users.csv --key incoming/2026/07/users.csv
"""

import argparse
import sys
import time
from pathlib import Path

from common import session_and_buckets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", type=Path)
    parser.add_argument("--key", help="S3 key (default: incoming/<filename>)")
    args = parser.parse_args()

    if not args.file.is_file():
        sys.exit(f"No such file: {args.file}")

    session, input_bucket, _ = session_and_buckets()
    key = args.key or f"incoming/{args.file.name}"

    started = time.time()
    # upload_file handles multipart and retries for us; put_object would need
    # the whole file in memory.
    session.client("s3").upload_file(str(args.file), input_bucket, key)

    print(f"uploaded s3://{input_bucket}/{key}  "
          f"{args.file.stat().st_size:,} bytes  {time.time() - started:.1f}s")


if __name__ == "__main__":
    main()
