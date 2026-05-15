import pandas as pd
import os
import tempfile
from pathlib import Path
import boto3
from src.config import OUTPUT_DIR
from dotenv import load_dotenv, find_dotenv

# Environment variables
load_dotenv(find_dotenv(), override=True)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

AWS_REGION = "eu-west-3"
BUCKET_NAME = "01-kayak-jedha"

S3_KEY = "raw/booking/booking_data.csv"

OUTPUT_PATH = OUTPUT_DIR / "hotels_cleaned.csv"


# S3 client

def get_s3_client():

    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    return session.client("s3")



# Downloading raw booking CSV from S3

def download_booking_dataset():

    s3_client = get_s3_client()

    temp_dir = Path(tempfile.gettempdir())

    local_path = temp_dir / "booking_data.csv"

    print("Downloading booking dataset from S3...")

    s3_client.download_file(
        BUCKET_NAME,
        S3_KEY,
        str(local_path),
    )

    print(f"Downloaded to : {local_path}")

    return local_path


# Cleaning dataset

def clean_hotels_data(df: pd.DataFrame) -> pd.DataFrame:

    # Renaming columns for warehouse consistency
    df = df.rename(columns={"name": "hotel_name"})

 
    # Removing duplicates
    df = df.drop_duplicates(subset=["url"]) # urls are more stable than hotel names as they can vary
                                            # same hotel names may exist in multiple places so we prefer urls

 
    # Convert numeric columns
    numeric_cols = [
        "rating",
        "latitude",
        "longitude"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

 

    # Handle missing values
 
    # Remove rows without essential business fields
    critical_cols = [
        "hotel_name",
        "city",
        "url"
    ]

    df = df.dropna(subset=critical_cols)

    # Fill missing ratings with median
    median_rating = df["rating"].median()
    df["rating"] = df["rating"].fillna(median_rating)

    # Fill optional text columns
    df["description"] = df["description"].fillna(
        "No description available"
    )

    df["address"] = df["address"].fillna(
        "Address unavailable"
    )
 
    # Clean text columns
    text_cols = [
        "hotel_name",
        "city",
        "description",
        "address",
        "url"
    ]

    for col in text_cols:
        df[col] = df[col].str.strip()

    # Standardize city names
    df["city"] = df["city"].str.title()

    return df


def main():

    local_input_path = download_booking_dataset()

    print("Loading raw booking dataset...")

    df = pd.read_csv(local_input_path)

    initial_rows = len(df)

    print("Cleaning booking dataset...")

    cleaned_df = clean_hotels_data(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    cleaned_df.to_csv(OUTPUT_PATH, index=False)

    final_rows = len(cleaned_df)

    print(f"Removed {initial_rows - final_rows} rows during cleaning")

    print(f"Cleaned dataset saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()