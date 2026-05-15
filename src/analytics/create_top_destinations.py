from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

from src.config import OUTPUT_DIR



# Environment variables


load_dotenv(find_dotenv(), override=True)

RDS_HOST = os.getenv("RDS_HOST")
RDS_PORT = os.getenv("RDS_PORT", "5432")
RDS_DB = os.getenv("RDS_DB")
RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")



# SQLAlchemy engine


def create_db_engine():

    database_url = (
        f"postgresql+psycopg2://"
        f"{RDS_USER}:{RDS_PASSWORD}"
        f"@{RDS_HOST}:{RDS_PORT}/{RDS_DB}"
    )

    engine = create_engine(database_url)

    return engine



# Load weather dataset from RDS


def load_weather_dataset():

    engine = create_db_engine()

    query = """
    SELECT *
    FROM weather_cleaned
    """

    df = pd.read_sql(
        query,
        con=engine,
    )

    print(f"Loaded rows: {len(df)}")

    return df



# Weather scoring


def compute_weather_score(row):

    score = 0

    weather = str(
        row["weather"]
    ).lower()

    # -----------------------------------------------------
    # Sky conditions
    # -----------------------------------------------------

    if "clear sky" in weather:
        score += 4

    elif "few clouds" in weather:
        score += 3

    elif "scattered clouds" in weather:
        score += 2

    elif "broken clouds" in weather:
        score += 1

    # -----------------------------------------------------
    # Rain
    # -----------------------------------------------------

    rain = row.get(
        "rain_3h",
        0,
    )

    if pd.isna(rain):
        rain = 0

    if rain == 0:
        score += 3

    elif rain < 1:
        score += 2

    elif rain < 3:
        score += 1

    # -----------------------------------------------------
    # Wind
    # -----------------------------------------------------

    wind = row.get(
        "wind_speed",
        0,
    )

    if wind < 15:
        score += 3

    elif wind < 25:
        score += 2

    elif wind < 35:
        score += 1

    # -----------------------------------------------------
    # Humidity
    # -----------------------------------------------------

    humidity = row.get(
        "humidity",
        50,
    )

    if 40 <= humidity <= 70:
        score += 3

    elif 30 <= humidity <= 80:
        score += 2

    else:
        score += 1

    # -----------------------------------------------------
    # Temperature
    # -----------------------------------------------------

    temperature = row.get(
        "temperature",
        20,
    )

    if 18 <= temperature <= 28:
        score += 3

    elif 28 < temperature <= 32:
        score += 2

    elif 10 <= temperature < 18:
        score += 2

    else:
        score += 1

    return score



# Create top destinations


def create_top_destinations(df):

    print(
        "Computing weather scores..."
    )

    df["weather_score"] = df.apply(
        compute_weather_score,
        axis=1,
    )

    print(
        "Aggregating city scores..."
    )

    city_ranking = (
        df.groupby("city")
        .agg(
            avg_weather_score=(
                "weather_score",
                "mean",
            ),
        )
        .reset_index()
    )

    city_ranking = city_ranking.sort_values(
        by="avg_weather_score",
        ascending=False,
    )

    top_5 = city_ranking.head(5)

    print(
        "Top 5 destinations created"
    )

    return top_5



# Save CSV locally


def save_csv_locally(df):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    local_csv_path = (
        OUTPUT_DIR
        / "top_5_destinations.csv"
    )

    df.to_csv(
        local_csv_path,
        index=False,
    )

    print(
        f"CSV saved locally: "
        f"{local_csv_path}"
    )

    return local_csv_path



# Main


def main():

    df = load_weather_dataset()

    top_5 = create_top_destinations(df)

    print(top_5)

    save_csv_locally(top_5)

    print(
        "Top destinations pipeline completed"
    )


if __name__ == "__main__":
    main()