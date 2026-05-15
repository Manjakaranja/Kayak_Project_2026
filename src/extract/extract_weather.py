import csv
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]

COORDINATES_PATH = BASE_DIR / "data" / "raw" / "coordinates" / "coordinates.json"
RAW_OUTPUT_PATH = BASE_DIR / "data" / "raw" / "weather" / "weather_forecasts.json"
CSV_OUTPUT_PATH = BASE_DIR / "data" / "raw" / "weather" / "weather_forecasts.csv"

BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"


def load_coordinates(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_weather_forecasts(coordinates: dict, api_key: str) -> dict:
    all_forecasts = {}

    for place_name, lat_lon_keys in coordinates.items():
        if lat_lon_keys is None:
            print(f"Skipping {place_name}: no coordinates found")
            continue

        lat = lat_lon_keys["lat"]
        lon = lat_lon_keys["lon"]

        payload = {
            "lat": lat,
            "lon": lon,
            "APPID": api_key,
            "units": "metric"
        }

        response = requests.get(BASE_URL, params=payload, timeout=30)

        if response.status_code == 200:
            print(f"Forecast fetched for {place_name}")
            all_forecasts[place_name] = response.json()
        else:
            print(f"Error for {place_name}: {response.status_code} - {response.text}")

    return all_forecasts


def save_raw_json(data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)

    print(f"Raw JSON saved to: {output_path}")


def transform_forecasts_to_rows(all_forecasts: dict) -> list[dict]:
    rows = []

    for place_name, data in all_forecasts.items():
        for entry in data.get("list", []):
            row = {
                "city": place_name,
                "datetime": entry.get("dt_txt"),
                "temperature": entry.get("main", {}).get("temp"),
                "feels_like": entry.get("main", {}).get("feels_like"),
                "humidity": entry.get("main", {}).get("humidity"),
                "weather": entry.get("weather", [{}])[0].get("description"),
                "wind_speed": entry.get("wind", {}).get("speed"),
                "rain_3h": entry.get("rain", {}).get("3h", 0),
            }
            rows.append(row)

    return rows


def save_csv(rows: list[dict], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    print(f"CSV saved to: {csv_path}")


def main():
    load_dotenv()
    api_key = os.getenv("API_KEY")

    if not api_key:
        raise ValueError("API_KEY not found in .env file")

    coordinates = load_coordinates(COORDINATES_PATH)
    all_forecasts = fetch_weather_forecasts(coordinates, api_key)

    save_raw_json(all_forecasts, RAW_OUTPUT_PATH)

    rows = transform_forecasts_to_rows(all_forecasts)
    save_csv(rows, CSV_OUTPUT_PATH)


if __name__ == "__main__":
    main()