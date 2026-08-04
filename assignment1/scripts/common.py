"""Shared bucket resolution for the operator scripts."""

import os
import sys

import boto3
from botocore.exceptions import ClientError


def session_and_buckets():
    """Return (session, input_bucket, output_bucket).

    Names are derived from the account and region so the scripts work without
    editing, and can still be overridden with INPUT_BUCKET / OUTPUT_BUCKET.
    """
    session = boto3.Session()
    region = session.region_name
    if not region:
        sys.exit("No region configured. Set one in ~/.aws/config.")

    try:
        account = session.client("sts").get_caller_identity()["Account"]
    except ClientError as exc:
        sys.exit(f"Could not authenticate with AWS: {exc}")

    return (
        session,
        os.environ.get("INPUT_BUCKET", f"karan-input-{account}-{region}-an"),
        os.environ.get("OUTPUT_BUCKET", f"karan-output-{account}-{region}-an"),
    )
