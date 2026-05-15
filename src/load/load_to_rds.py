from pathlib import Path
import os
import tempfile

import boto3
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine



# Environment variables


load_dotenv(find_dotenv(), override=True)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

AWS_REGION = "eu-west-3"
BUCKET_NAME = "01-kayak-jedha"

S3_OUTPUT_PREFIX = "outputs/"

RDS_HOST = os.getenv("RDS_HOST")
RDS_PORT = os.getenv("RDS_PORT", "5432")
RDS_DB = os.getenv("RDS_DB")
RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")



# S3 client


def get_s3_client():

    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    return session.client("s3")



# List CSV files in S3


def list_output_csv_files():

    s3_client = get_s3_client()

    response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=S3_OUTPUT_PREFIX,
    )

    csv_files = []

    for obj in response.get("Contents", []):

        key = obj["Key"]

        if key.endswith(".csv"):

            csv_files.append(key)

    print("\nCSV files found in S3:")

    for file in csv_files:
        print(f"- {file}")

    return csv_files



# Download file from S3


def download_s3_file(s3_key: str):

    s3_client = get_s3_client()

    temp_dir = Path(tempfile.gettempdir())

    local_path = (temp_dir / Path(s3_key).name)

    print(f"\nDownloading {s3_key}...")

    s3_client.download_file(
        BUCKET_NAME,
        s3_key,
        str(local_path),
    )

    print(f"Downloaded to: {local_path}")

    return local_path



# SQLAlchemy engine


def create_db_engine():

    if not all([
        RDS_HOST,
        RDS_DB,
        RDS_USER,
        RDS_PASSWORD,
    ]):
        raise ValueError(
            "Missing RDS environment variables"
        )

    database_url = (
        f"postgresql+psycopg2://"
        f"{RDS_USER}:{RDS_PASSWORD}"
        f"@{RDS_HOST}:{RDS_PORT}/{RDS_DB}"
    )

    engine = create_engine(database_url)

    return engine



# Upload DataFrame to RDS


def upload_dataframe_to_rds(
    df: pd.DataFrame,
    table_name: str,
):

    engine = create_db_engine()

    print(
        f"\nUploading table: {table_name}"
    )

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False,
    )

    print(
        f"Table '{table_name}' uploaded "
        f"successfully"
    )



# Main


def main():

    # list all CSVs in outputs/
    csv_files = list_output_csv_files()

    for s3_key in csv_files:

        # download file
        local_path = download_s3_file(
            s3_key
        )

        # load DataFrame
        print(
            f"Loading DataFrame from "
            f"{local_path.name}"
        )

        df = pd.read_csv(local_path)

        print(
            f"Rows loaded: {len(df)}"
        )

        # infer table name
        table_name = (
            Path(s3_key)
            .stem
            .lower()
        )

        # upload to RDS
        upload_dataframe_to_rds(
            df=df,
            table_name=table_name,
        )

    print(
        "\nAll CSV files uploaded "
        "to RDS successfully"
    )


if __name__ == "__main__":
    main()