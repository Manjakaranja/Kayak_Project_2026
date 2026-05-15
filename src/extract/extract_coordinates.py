import json
import sys
import time
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parents[2]
CITIES_PATH = BASE_DIR / "config" / "cities.json"
OUTPUT_PATH = BASE_DIR / "data" / "raw" / "coordinates" / "coordinates.json"

BASE_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    "User-Agent": "KayakProject/1.0 (emailfortheproject@gmail.com)"
}


def load_cities(cities_path: Path) -> list[str]:
    with open(cities_path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_coordinates(cities: list[str]) -> dict:
    coordinates = {}

    for city in cities:
        try:
            params = {
                "q": f"{city}, France",
                "format": "json",
                "limit": 1
            }

            response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data:
                coordinates[city] = {
                    "lat": float(data[0]["lat"]),
                    "lon": float(data[0]["lon"])
                }
                print(f"{city}: {coordinates[city]}")
            else:
                coordinates[city] = None
                print(f"No results for {city}")

        except Exception as e:
            print(f"Error fetching {city}: {e}", file=sys.stderr)
            coordinates[city] = None

        time.sleep(1)

    return coordinates


def save_coordinates(coordinates: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(coordinates, f, indent=4, ensure_ascii=False)

    print(f"\nCoordinates saved to: {output_path}")


def main():
    cities = load_cities(CITIES_PATH)
    coordinates = fetch_coordinates(cities)
    save_coordinates(coordinates, OUTPUT_PATH)


if __name__ == "__main__":
    main()