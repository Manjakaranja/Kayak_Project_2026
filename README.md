# Kayak Travel Recommendation Pipeline

## Academic Context

This project was developed as part of the CDSD RNCP 35288 Level 6 (Bachelor's degree) certification pathway and specifically corresponds to the requirements of Bloc 1 focused on Data Engineering, Data Collection and Cloud Data Infrastructure implementation.

The objective of this bloc is to design and build a complete data pipeline capable of:

Collecting data from external sources
Structuring and storing raw datasets
Implementing transformation workflows
Managing cloud storage infrastructure
Loading curated datasets into a relational warehouse
Producing analytical outputs and visualizations

The project follows the specifications provided in the “Plan your trip with Kayak” case study.

Although the RNCP35288 certification is currently marked as inactive since February 10th, 2026, this status only applies to new enrollments. Learners enrolled before this date remain fully eligible to complete the certification process and obtain a valid RNCP certification, in accordance with France Compétences transition rules.

Additional information can be verified through the official RNCP registry and France Compétences.

https://www.francecompetences.fr/recherche/rncp/35288/


## Project Overview

This project implements an end-to-end data engineering pipeline designed to identify the best travel destinations in France based on short-term weather conditions and enrich those destinations with hotel recommendations collected from Booking.com.

The pipeline combines:

* Geolocation data extraction
* Weather forecasting ingestion
* Web scraping
* Data cleaning and transformation
* Cloud storage on AWS S3
* Relational storage in PostgreSQL on AWS RDS
* Automated orchestration
* Interactive visual analytics

The architecture follows a modular ETL/ELT design commonly used in production-grade data platforms.

The project is structured to clearly separate extraction, transformation, loading, analytics and visualization responsibilities across dedicated modules.

---

# Business Objective

The objective is to help travelers identify:

1. The most attractive destinations in France according to upcoming weather forecasts
2. The best-rated hotels available in those destinations

The pipeline automatically:

* Retrieves a predefined list of French destinations
* Collects geographical coordinates
* Fetches weather forecasts from OpenWeather API
* Scores destinations according to weather quality
* Selects the best cities
* Scrapes hotel information from Booking.com
* Cleans and standardizes datasets
* Stores datasets in AWS S3 and PostgreSQL
* Produces interactive maps for decision support

---

# Project Architecture

The repository is organized around a layered data engineering architecture:

```text
project/
│
├── config/
├── data/
│   ├── raw/
│   └── outputs/
│
├── logs/
├── notebooks/
├── src/
│   ├── analytics/
│   ├── config/
│   ├── extract/
│   ├── load/
│   ├── orchestration/
│   ├── transform/
│   └── visualization/
│
├── requirements.txt
└── README.md
```

The separation between `raw`, `outputs`, `extract`, `transform`, `load`, `analytics` and `visualization` mirrors the organization commonly used in modern data lake and data warehouse projects.

---

# Data Flow Overview

The pipeline follows the sequence below:

```text
Cities List
    ↓
Coordinates Extraction
    ↓
Weather API Extraction
    ↓
Raw CSV Storage
    ↓
AWS S3 Upload
    ↓
Data Cleaning
    ↓
Cleaned CSV Storage
    ↓
AWS S3 Upload
    ↓
AWS RDS Loading
    ↓
Destination Ranking
    ↓
Booking Scraping
    ↓
Hotel Cleaning
    ↓
Visualization Generation
```

The orchestration layer centralizes the execution order of all modules and guarantees deterministic execution of the complete workflow.

---

# Configuration Layer

The configuration layer centralizes all project paths using `pathlib`.

```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR / "outputs"
```

This design avoids hardcoded paths and ensures portability across environments.

The project relies on environment variables for:

* AWS credentials
* PostgreSQL credentials
* API keys

This prevents sensitive information from being exposed in source code.

---

# Input Dataset

The project starts from a manually curated list of French destinations stored in `cities.json`.

Example destinations include:

* Paris
* Annecy
* Cassis
* Strasbourg
* Biarritz
* Lyon
* Colmar

The cities were selected to provide geographic diversity across France and represent realistic tourism destinations.

---

# Step 1 — Coordinate Extraction

Module:

```text
src/extract/extract_coordinates.py
```

This step retrieves latitude and longitude information from the Nominatim API.

For each city:

1. A request is sent to Nominatim
2. Coordinates are extracted
3. Results are saved locally as JSON

The module also introduces throttling using `time.sleep(1)` in order to respect API usage policies.

Output:

```text
data/raw/coordinates/coordinates.json
```

This file becomes the geographical foundation of the rest of the pipeline.

---

# Step 2 — Weather Extraction

Module:

```text
src/extract/extract_weather.py
```

Using the coordinates generated previously, the pipeline queries the OpenWeather Forecast API.

For each city:

* Temperature
* Feels-like temperature
* Humidity
* Wind speed
* Rain forecast
* Weather description

are collected for multiple forecast intervals.

Two output formats are generated:

```text
data/raw/weather/weather_forecasts.json
data/raw/weather/weather_forecasts.csv
```

The JSON file preserves the raw API response while the CSV file provides a tabular structure suitable for downstream analytics.

---

# Step 3 — Uploading Raw Data to AWS S3

Module:

```text
src/load/load_to_s3.py
```

This layer acts as the project's data lake ingestion step.

The module recursively scans:

```text
data/raw/
```

and uploads all CSV files to AWS S3.

A key design choice here is the use of:

```python
relative_path = path.relative_to(RAW_DIR)
```

which preserves the original folder hierarchy inside the S3 bucket.

Example:

```text
data/raw/weather/weather_forecasts.csv
```

becomes:

```text
s3://01-kayak-jedha/raw/weather/weather_forecasts.csv
```

This approach mirrors production data lake organization practices.

---

# Step 4 — Weather Data Transformation

Module:

```text
src/transform/transform_weather.py
```

The transformation layer downloads raw weather data from S3 and performs several cleaning operations.

Transformations include:

* Duplicate removal
* Datetime conversion
* Numeric type conversion
* Missing value handling
* Rain normalization
* Text standardization
* City name normalization

The cleaned dataset is exported as:

```text
data/outputs/weather_cleaned.csv
```

The outputs directory represents curated analytical datasets ready for warehouse ingestion.

---

# Step 5 — Loading Data into AWS RDS

Module:

```text
src/load/load_to_rds.py
```

This stage loads curated datasets into PostgreSQL hosted on AWS RDS.

The loader:

1. Connects to PostgreSQL using SQLAlchemy
2. Downloads CSV outputs from S3
3. Infers table names automatically
4. Loads DataFrames into relational tables

Example:

```text
weather_cleaned.csv
```

becomes:

```sql
weather_cleaned
```

inside PostgreSQL.

This creates a centralized analytical storage layer suitable for SQL querying and visualization.

---

# Step 6 — Destination Scoring Engine

Module:

```text
src/analytics/create_top_destinations.py
```

This layer computes a weather quality score for each forecast entry.

The scoring model evaluates:

* Sky conditions
* Rain intensity
* Wind speed
* Humidity
* Temperature comfort

Each criterion contributes positively or negatively to the final score.

The pipeline then:

1. Aggregates scores by city
2. Computes average weather scores
3. Ranks destinations
4. Selects the Top 5 cities

Output:

```text
data/outputs/top_5_destinations.csv
```

This step transforms raw weather observations into actionable business intelligence.

---

# Step 7 — Booking.com Hotel Extraction

Module:

```text
src/extract/extract_booking.py
```

Once the top destinations are identified, the pipeline dynamically scrapes hotel information from Booking.com.

The scraper uses:

* Scrapy
* Playwright
* Headless Chromium

to handle dynamically rendered pages.

For each destination:

1. Search results pages are loaded
2. Hotel links are extracted
3. Individual hotel pages are visited
4. Structured hotel information is collected

Extracted fields include:

* Hotel name
* Rating
* Description
* Address
* Latitude
* Longitude
* Booking URL

The scraper includes:

* Retry management
* Download delays
* Browser automation
* Error handling
* Concurrency control

These protections are important in professional scraping pipelines to reduce blocking risk and improve stability.

Raw outputs are saved under:

```text
data/raw/booking/
```

---

# Step 8 — Hotel Data Cleaning

Module:

```text
src/transform/transform_booking.py
```

This stage standardizes hotel information before warehouse ingestion.

Cleaning operations include:

* URL-based deduplication
* Numeric conversion
* Missing value handling
* Text normalization
* City standardization

The cleaned dataset is exported as:

```text
data/outputs/hotels_cleaned.csv
```

The use of URL deduplication is particularly important because hotel names may vary while URLs remain stable identifiers.

---

# Step 9 — Interactive Visualizations

## Top Destinations Map

Module:

```text
src/visualization/plot_top_destinations.py
```

This module generates an interactive Plotly map displaying the top-ranked destinations.

Features include:

* Dynamic marker sizing
* Color-coded weather scores
* Interactive hover information
* OpenStreetMap integration

Output:

```text
data/outputs/top_5_destinations.html
```

---

## Top Hotels Map

Module:

```text
src/visualization/plot_top_hotels.py
```

This visualization displays the top-rated hotels for each destination city.

Hotels are filtered by:

* Valid coordinates
* Available ratings

and ranked by hotel score.

Output:

```text
data/outputs/top_20_hotels_map.html
```

---

# Orchestration Layer

Module:

```text
src/orchestration/orchestration.py
```

The orchestration script acts as the central execution engine of the platform.

It sequentially executes:

1. Extraction modules
2. Loading modules
3. Transformation modules
4. Analytics modules
5. Visualization modules

Execution is delegated through:

```python
subprocess.run(
    [sys.executable, "-m", module_name],
    check=True,
)
```

This design isolates execution contexts and improves operational robustness.

The orchestration layer also implements centralized logging:

```text
logs/pipeline.log
```

which provides traceability and execution monitoring.

---

# AWS Architecture

The project uses AWS as both storage and warehouse infrastructure.

## AWS S3

S3 acts as the project's data lake:

* Raw datasets
* Curated outputs
* Intermediate CSV files

are persisted in cloud object storage.

---

## AWS RDS PostgreSQL

RDS acts as the analytical warehouse layer.

Structured relational tables allow:

* SQL exploration
* Dashboard integration
* Aggregation queries
* Analytical reporting

---

# Notebooks

The project also includes exploratory notebooks:

```text
notebooks/
├── 01_Kayak_S3.ipynb
├── 02_Kayak_Weather_EDA.ipynb
└── 03_Kayak_Booking_EDA.ipynb
```

These notebooks were used for:

* Exploratory data analysis
* API validation
* Warehouse verification
* Visualization testing

---

# Technologies Used

## Data Engineering

* Python
* Pandas
* SQLAlchemy
* PostgreSQL
* AWS S3
* AWS RDS

## APIs

* OpenWeather API
* Nominatim API

## Web Scraping

* Scrapy
* Playwright

## Visualization

* Plotly
* OpenStreetMap

## Infrastructure

* dotenv
* boto3
* pathlib

---

# Running the Pipeline

## Install dependencies

```bash
pip install -r requirements.txt
```

## Configure environment variables

Create a `.env` file containing:

```text
API_KEY=
AWS_ACCESS_KEY=
AWS_SECRET_ACCESS_KEY=

RDS_HOST=
RDS_PORT=
RDS_DB=
RDS_USER=
RDS_PASSWORD=
```

## Run the full pipeline

```bash
python -m src.orchestration.orchestration
```

The orchestration layer automatically executes all modules in the correct order.

---

# Final Outputs

The pipeline produces:

| Output                    | Description                          |
| ------------------------- | ------------------------------------ |
| `weather_cleaned.csv`     | Cleaned weather forecasts            |
| `hotels_cleaned.csv`      | Cleaned hotel dataset                |
| `top_5_destinations.csv`  | Ranked travel destinations           |
| `top_5_destinations.html` | Interactive destination map          |
| `top_20_hotels_map.html`  | Interactive hotel recommendation map |

---

# Conclusion

This project demonstrates the implementation of a complete cloud-based data engineering workflow integrating:

* API ingestion
* Web scraping
* Data cleaning
* Cloud storage
* Relational warehousing
* Automated orchestration
* Interactive analytics

The architecture was designed to remain modular, extensible and production-oriented while following common industry practices used in modern ETL and analytics platforms.
