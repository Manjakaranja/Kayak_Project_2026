import os

import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv
from src.config import OUTPUT_DIR

load_dotenv()

RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")
RDS_HOST = os.getenv("RDS_HOST")
RDS_PORT = os.getenv("RDS_PORT")
RDS_NAME = os.getenv("RDS_DB")

DATABASE_ = (
    f"postgresql+psycopg2://{RDS_USER}:{RDS_PASSWORD}"
    f"@{RDS_HOST}:{RDS_PORT}/{RDS_NAME}"
)

engine = create_engine(DATABASE_)


# LOAD TOP 20 HOTELS


query = """
SELECT
    city,
    hotel_name,
    latitude,
    longitude,
    rating
FROM hotels_cleaned
WHERE latitude IS NOT NULL
  AND longitude IS NOT NULL
  AND rating IS NOT NULL
"""

df_hotels = pd.read_sql(query, engine)

df_top20 = (
    df_hotels.sort_values(
        by=["city", "rating"],
        ascending=[True, False]
    )
    .groupby("city")
    .head(20)
)

# MAP


fig = px.scatter_mapbox(
    df_hotels,
    lat="latitude",
    lon="longitude",

    hover_name="hotel_name",

    hover_data={
        "city": True,
        "rating": ":.1f",
        "latitude": False,
        "longitude": False,
    },

    color="rating",
    size="rating",

    zoom=5,

    center={
        "lat": 46.5,
        "lon": 2.5,
    },

    height=850,
)


# LAYOUT


fig.update_layout(

    mapbox_style="open-street-map",

    title={
        "text": "<b>Top 20 Hotels in Top 5 Destinations</b>",
        "x": 0.5,
        "xanchor": "center",
    },

    margin={
        "r": 30,
        "t": 80,
        "l": 30,
        "b": 100,
    },

    paper_bgcolor="white",

    annotations=[

        dict(
            text=(
                "<b>Hotel ratings</b><br>"
                "Only hotels located in the Top 5 destination cities are displayed.<br>"
                "Markers are sized and colored according to hotel rating."
            ),

            x=0.5,
            y=-0.12,

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

# Saving map
output_path = OUTPUT_DIR / "top_20_hotels_map.html"

fig.write_html(
    output_path,
    full_html=True,
    include_plotlyjs="cdn",
)

print(f"Map saved to: {output_path}")


fig.show()

