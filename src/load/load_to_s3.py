
from pathlib import Path
import sys
import os

import boto3
from dotenv import load_dotenv, find_dotenv

from src.config import RAW_DIR, OUTPUT_DIR

# Chargement des variables d'environnement (.env)
load_dotenv(find_dotenv(), override=True)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = "eu-west-3"
BUCKET_NAME = "01-kayak-jedha"


def get_s3_resource():

    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )
    return session.resource("s3")


def upload_file(local_path: Path, s3_key: str):

    s3 = get_s3_resource()
    bucket = s3.Bucket(BUCKET_NAME)
    bucket.upload_file(str(local_path), s3_key)
    print(f"Upload {local_path} -> s3://{BUCKET_NAME}/{s3_key}")


def upload_raw_folder(prefix: str = "raw/"):

    for path in RAW_DIR.rglob("*.csv"):

        relative_path = path.relative_to(RAW_DIR) 
        s3_key = f"{prefix}{relative_path}"

        upload_file(path, s3_key)


def upload_outputs_folder(prefix: str = "outputs/"):

    for path in OUTPUT_DIR.glob("*.csv"):
        s3_key = f"{prefix}{path.name}"
        upload_file(path, s3_key)


def upload_all():

    upload_raw_folder()
    upload_outputs_folder()


if __name__ == "__main__":
    upload_all()