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

S3_KEY = "raw/weather/weather_forecasts.csv"

OUTPUT_PATH = OUTPUT_DIR / "weather_cleaned.csv"

# S3 client

def get_s3_client():

    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    return session.client("s3")

# Downloading raw weather CSV from S3

def download_weather_dataset():

    s3_client = get_s3_client()

    temp_dir = Path(tempfile.gettempdir())

    local_path = temp_dir / "weather_forecasts.csv"

    print("Downloading weather dataset from S3...")

    s3_client.download_file(
        BUCKET_NAME,
        S3_KEY,
        str(local_path),
    )

    print(f"downloaded to : {local_path}")

    return local_path

# Cleaning dataset


def clean_weather_data(df: pd.DataFrame) -> pd.DataFrame:

    # Removing duplicates
    df = df.drop_duplicates()

    # Datetime conversion
    df["datetime"] = pd.to_datetime(df["datetime"])

    # Numeric conversions
    numeric_cols = [
        "temperature",
        "feels_like",
        "humidity",
        "wind_speed",
        "rain_3h"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Removing rows with critical missing identifiers
    df = df.dropna(subset=["city", "datetime"])

    # Filling rain values with 0 because missing rain information is interpreted as no expected rainfall
    df["rain_3h"] = df["rain_3h"].fillna(0)

    # Filling the other numerical weather columns with median values
    numeric_fill_cols = [
        "temperature",
        "feels_like",
        "humidity",
        "wind_speed"
    ]

    for col in numeric_fill_cols:
        median_value = df[col].median()
        df[col] = df[col].fillna(median_value)

   # Cleaning text columns
 
    text_cols = [
        "city",
        "weather"
    ]

    for col in text_cols:
        df[col] = df[col].str.strip()
    

    # Standardizing city names
    df["city"] = df["city"].str.title()

    return df


def main():

    local_input_path = download_weather_dataset()

    print("Loading raw weather dataset...")

    df = pd.read_csv(local_input_path)
    
    initial_rows = len(df)
   
    cleaned_df = clean_weather_data(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    cleaned_df.to_csv(OUTPUT_PATH, index=False)

    
    final_rows = len(cleaned_df)

    print(f"Removed {initial_rows - final_rows} rows during cleaning")

    print(f"Cleaned weather data saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()