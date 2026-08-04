"""Lambda entry point. Triggered by S3 ObjectCreated on the input bucket."""

import io
import os
import urllib.parse
from datetime import datetime

import boto3
from boto3.s3.transfer import TransferConfig

from transform import csv_to_jsonl, output_key

# Module scope so warm invocations reuse the client.
s3 = boto3.client("s3")

OUTPUT_BUCKET = os.environ["OUTPUT_BUCKET"]

# use_threads=False because the source is a one-pass stream: concurrent workers
# would each hold a chunk, putting 80 MiB in memory instead of 8.
TRANSFER = TransferConfig(use_threads=False)


class ChunkReader(io.RawIOBase):
    """Presents a generator of byte chunks as a file object.

    upload_fileobj wants something with .read(); csv_to_jsonl yields rows.
    This bridges the two, so boto3 owns the multipart mechanics and memory
    stays bounded by one part rather than the file size.
    """

    def __init__(self, chunks):
        self._chunks = iter(chunks)
        self._buffer = bytearray()
        self.rows = 0

    def readable(self):
        return True

    def readinto(self, target):
        while len(self._buffer) < len(target):
            try:
                self._buffer += next(self._chunks)
                self.rows += 1
            except StopIteration:
                break

        taken = min(len(target), len(self._buffer))
        target[:taken] = self._buffer[:taken]
        del self._buffer[:taken]
        return taken


def lambda_handler(event, context):
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        # S3 URL-encodes the key in the event: "a b.csv" arrives as "a+b.csv".
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        # Stamped from the event rather than the clock, so a Lambda retry
        # rewrites the same key instead of leaving a duplicate behind.
        stamp = datetime.fromisoformat(record["eventTime"]).strftime("%Y%m%dT%H%M%SZ")

        # Never .read() - the body is consumed lazily as rows are pulled.
        body = s3.get_object(Bucket=bucket, Key=key)["Body"]
        reader = ChunkReader(csv_to_jsonl(body))
        destination = output_key(key, stamp)

        s3.upload_fileobj(
            reader, OUTPUT_BUCKET, destination, Config=TRANSFER,
            ExtraArgs={"ContentType": "application/x-ndjson"},
        )

        print(f"s3://{bucket}/{key} -> s3://{OUTPUT_BUCKET}/{destination}"
              f"  {reader.rows} rows")

    return {"statusCode": 200}
