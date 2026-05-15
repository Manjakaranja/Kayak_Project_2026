import json
import os

import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv

from src.config import RAW_DIR, OUTPUT_DIR

load_dotenv()

RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")
RDS_HOST = os.getenv("RDS_HOST")
RDS_PORT = os.getenv("RDS_PORT")
RDS_NAME = os.getenv("RDS_DB")

DATABASE_URL = (
    f"postgresql+psycopg2://{RDS_USER}:{RDS_PASSWORD}"
    f"@{RDS_HOST}:{RDS_PORT}/{RDS_NAME}"
)

engine = create_engine(DATABASE_URL)

df_top = pd.read_sql(
    "SELECT * FROM top_5_destinations",
    engine
)

coordinates_path = (
    RAW_DIR
    / "coordinates"
    / "coordinates.json"
)

with open(coordinates_path, "r", encoding="utf-8") as f:
    coordinates = json.load(f)

rows = []

for city, values in coordinates.items():

    if values:

        rows.append({
            "city": city,
            "latitude": float(values["lat"]),
            "longitude": float(values["lon"]),
        })

df_coords = pd.DataFrame(rows)

df_final = df_top.merge(
    df_coords,
    on="city",
    how="left",
)

fig = px.scatter_mapbox(
    df_final,
    lat="latitude",
    lon="longitude",
    hover_name="city",
    hover_data={
        "avg_weather_score": ":.2f",
        "latitude": False,
        "longitude": False,
    },
    color="avg_weather_score",
    size="avg_weather_score",
    zoom=5,
    center={
        "lat": 46.5,
        "lon": 2.5,
    },
    height=950,
)


fig.update_layout(

    mapbox_style="open-street-map",

    height=800,

    margin={
        "r": 30,
        "t": 30,
        "l": 30,
        "b": 170,
    },

    paper_bgcolor="white",

    annotations=[

        dict(
            text=(
                "<b>How the Average Weather Score is Calculated</b><br>"
                "Forecasts are scored using sky conditions, rain, wind, humidity and temperature. "
                "Clear skies and comfortable temperatures increase the score, "
                "while rain and strong wind reduce it.<br><br>"

                "The displayed value corresponds to the "
                "<b>average weather score</b> computed from all forecasts "
                "over the next few days."
            ),

            x=0.5,
            y=-0.17,

            xref="paper",
            yref="paper",

            showarrow=False,

            align="center",

            font=dict(
                size=13,
                color="#2c3e50",
            ),

            bordercolor="#d9d9d9",
            borderwidth=1,

            borderpad=12,

            bgcolor="rgba(248,248,248,0.95)",
        )
    ]
)



# Save map
output_path = OUTPUT_DIR / "top_5_destinations.html"

fig.write_html(
    output_path,
    full_html=True,
    include_plotlyjs="cdn",
)

print(f"Map saved to: {output_path}")

fig.show()

