# Assignment 1 - Event-Driven S3 Processing

Uploading a CSV to one S3 bucket triggers a Lambda, which converts it to JSON
Lines and writes it to a second bucket.

```
s3://input-bucket/incoming/users.csv
        |  ObjectCreated event, filtered to .csv
        v
   Lambda (Python 3.13)
        |
        v
s3://output-bucket/processed/incoming/users_20260803T070640Z.jsonl
```

## Files

```
processor/src/handler.py     the Lambda. Reads the event, streams from S3, writes back.
processor/src/transform.py   CSV to JSON Lines. No AWS, so it can be tested on its own.
scripts/generate_csv.py      make a test CSV
scripts/upload_csv.py        upload one to the input bucket
scripts/list_output.py       list what came out
```

## Running the scripts

```
uv run scripts/generate_csv.py --rows 2000 --messy
uv run scripts/upload_csv.py data/users.csv
uv run scripts/list_output.py
```

`--messy` adds the cases the handler exists to survive: a byte order mark,
spaced and mixed-case headers, non-Latin text, zero-padded numbers and a row
with extra fields.

Bucket names are worked out from the AWS account and region, so nothing needs
editing. `INPUT_BUCKET` and `OUTPUT_BUCKET` override them.

## Deploying the Lambda

```
cd processor/src && zip ../../function.zip *.py
```

Upload that zip to the function, set the handler to `handler.lambda_handler`,
and give it `OUTPUT_BUCKET` as an environment variable.

The execution role needs `s3:GetObject` on the input bucket, `s3:PutObject`
and `s3:AbortMultipartUpload` on the output bucket, and permission to write
its own CloudWatch logs. Nothing more.

## Notes

The conversion streams, so memory stays flat regardless of file size - a
26 MB file peaked at 121 MB against 98 MB for a 174 KB one. Output under
8 MiB goes up as a single PutObject; past that boto3 switches to a multipart
upload.

Input and output are separate buckets on purpose. Writing the output back
into the bucket that triggered the function would re-trigger it. Separate
buckets plus a role with no PutObject on the input make that impossible
rather than merely unlikely.
