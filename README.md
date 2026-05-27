# Cloud-Based Travel Recommendation Data Platform

End-to-end data engineering pipeline designed to identify attractive travel destinations in France based on short-term weather conditions and enrich them with hotel recommendations collected from Booking.com.

The project combines API ingestion, web scraping, cloud storage, warehouse modeling, orchestration, and analytical visualization in a modular ETL architecture inspired by modern lakehouse workflows.

---

# Academic & Business Context

This project was developed as part of the CDSD RNCP Level 6 certification pathway (RNCP35288), within Bloc 1: *Construction et alimentation d'une infrastructure de gestion de données*.

The business case simulates a lightweight recommendation platform for a travel company similar to Kayak. The objective is to:

* collect weather forecasts for multiple French destinations
* rank destinations using weather-based scoring
* retrieve hotel recommendations for selected cities
* expose curated analytical datasets and visual outputs

Although the RNCP35288 certification is currently marked as inactive for new enrollments, learners enrolled before February 2026 remain fully eligible to complete and validate the certification process.

Official RNCP registry:
[France Compétences – RNCP35288](https://www.francecompetences.fr/recherche/rncp/35288/)

---

# Technology Stack

| Layer           | Technologies                    |
| --------------- | ------------------------------- |
| Programming     | Python                          |
| Data Processing | Pandas                          |
| APIs            | OpenWeather API, Nominatim API  |
| Web Scraping    | Scrapy, Playwright              |
| Cloud Storage   | AWS S3                          |
| Warehouse       | PostgreSQL on AWS RDS           |
| Database Access | SQLAlchemy                      |
| Visualization   | Plotly                          |
| Configuration   | dotenv, pathlib                 |
| Orchestration   | Python subprocess orchestration |

---

# System Architecture & Data Flow

The platform follows a Medallion-inspired architecture separating raw ingestion, cleaned datasets, analytical models, and serving outputs.

```text
External APIs / Booking.com
            ↓
        Bronze Layer
     Raw JSON / CSV Data
            ↓
        Silver Layer
   Cleaned & Standardized
            ↓
         Gold Layer
 Destination Scoring Logic
            ↓
      Serving Marts
 Interactive Maps & Tables
```

Execution flow:

```text
Cities List
    ↓
Coordinates Extraction
    ↓
Weather API Extraction
    ↓
Raw Data Storage
    ↓
AWS S3 Data Lake
    ↓
Cleaning & Standardization
    ↓
PostgreSQL Warehouse
    ↓
Destination Scoring
    ↓
Booking Scraping
    ↓
Hotel Analytics
    ↓
Interactive Visualizations
```

Hotel scraping is intentionally executed only after destination ranking.
This reduces unnecessary scraping volume, lowers execution time, and limits requests sent to Booking.com.

---

# Repository Structure & Execution Order

```text
project/
│
├── data/
│   ├── raw/
│   └── outputs/
│
├── logs/
├── notebooks/
│
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

Main orchestration entrypoint:

```bash
python -m src.orchestration.orchestration
```

Pipeline execution order:

```text
Extract → Load Raw → Transform → Warehouse Load → Analytics → Visualization
```

---

# Layer-by-Layer Engineering

## EDA Layer

Exploratory notebooks were used to validate:

* API responses
* schema consistency
* hotel scraping quality
* warehouse ingestion
* visualization rendering

Notebooks remain isolated from production pipeline logic.

```text
notebooks/
├── 01_Kayak_S3.ipynb
├── 02_Kayak_Weather_EDA.ipynb
└── 03_Kayak_Booking_EDA.ipynb
```

---

# Bronze Layer — Raw Ingestion

The Bronze layer stores raw extracted data with minimal transformation.

Sources:

* Nominatim API
* OpenWeather API
* Booking.com scraping

Raw datasets are persisted locally and uploaded to AWS S3.

Example:

```text
data/raw/weather/weather_forecasts.json
data/raw/weather/weather_forecasts.csv
```

The S3 loader preserves the local folder hierarchy using relative paths:

```python
relative_path = path.relative_to(RAW_DIR)
```

Resulting structure:

```text
s3://bucket/raw/weather/weather_forecasts.csv
```

This layer acts as the system’s immutable ingestion zone.

---

# Silver Layer — Standardization & Cleaning

The Silver layer contains cleaned and standardized analytical datasets.

Main transformations:

* duplicate removal
* type casting
* datetime normalization
* missing value handling
* city normalization
* URL deduplication
* numeric cleaning

Outputs:

```text
data/outputs/weather_cleaned.csv
data/outputs/hotels_cleaned.csv
```

The cleaned datasets are then loaded into PostgreSQL on AWS RDS.

---

# Gold Layer — Core Analytical Models

The Gold layer contains business-oriented analytical logic.

## Destination Scoring

Weather forecasts are transformed into destination quality scores based on:

* temperature comfort
* rainfall
* humidity
* wind conditions
* sky conditions

The pipeline aggregates forecast scores at city level to produce ranked destinations.

Output:

```text
top_5_destinations.csv
```

---

# Serving Marts

Serving marts expose lightweight analytical outputs for visualization and exploration.

Current marts include:

* Top destination rankings
* Top hotel recommendations
* Interactive Plotly maps

Outputs:

```text
top_5_destinations.html
top_20_hotels_map.html
```

---

# Warehouse Modeling

The warehouse follows a lightweight analytical modeling approach inspired by dimensional modeling principles.

## Core Tables

| Table                | Purpose                        |
| -------------------- | ------------------------------ |
| `weather_cleaned`    | standardized weather forecasts |
| `hotels_cleaned`     | cleaned hotel dataset          |
| `top_5_destinations` | ranked destination outputs     |

## Fact-like Structures

Weather observations behave as fact-style analytical tables:

* multiple forecast records
* time-based metrics
* city-level aggregation

## Dimension-like Structures

Cities and hotels behave similarly to lightweight dimensions:

* descriptive attributes
* stable identifiers
* geographic metadata

## Bridge Relationships

Hotels and destinations naturally create many-to-many relationships:

* one city contains many hotels
* hotels are linked to ranked destinations
* rankings evolve over time

The project keeps this relationship handling intentionally lightweight given the project scope.

---

# Performance & Storage Optimizations

The project focuses on simple but practical optimization patterns rather than advanced distributed processing.

Implemented optimizations include:

* selective scraping after destination ranking
* separation between raw and curated layers
* hierarchical S3 object organization
* centralized orchestration
* warehouse loading from curated datasets only
* lightweight logging for execution traceability

Example orchestration pattern:

```python
subprocess.run(
    [sys.executable, "-m", module_name],
    check=True,
)
```

---

# Analytical Themes & Insights

The analytics primarily focus on:

* short-term destination attractiveness
* weather comfort scoring
* hotel quality distribution
* geographic recommendation patterns

The project intentionally avoids overly complex predictive modeling and instead focuses on explainable ranking logic and clean analytical transformations.

---

# Key Findings

Some recurring observations from the generated datasets:

* coastal destinations generally receive stronger weather scores during forecast windows
* cities with moderate temperatures outperform extremely hot or rainy destinations
* hotel availability and ratings vary significantly between destinations
* ranking destinations before scraping hotels substantially reduces scraping workload

The project demonstrates how relatively small datasets can still support meaningful analytical workflows when structured correctly.

---

# Running the Pipeline

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a `.env` file:

```env
API_KEY=
AWS_ACCESS_KEY=
AWS_SECRET_ACCESS_KEY=

RDS_HOST=
RDS_PORT=
RDS_DB=
RDS_USER=
RDS_PASSWORD=
```

## Run the Full Pipeline

```bash
python -m src.orchestration.orchestration
```

---

# Future Roadmap

Planned improvements include:

* Airflow-based orchestration
* Docker containerization
* automated testing
* incremental ingestion strategies
* dbt-style warehouse transformations
* Delta Lake migration
* CI/CD integration
* Infrastructure as Code deployment

---

# Repository Structure

```text
src/
├── analytics/
├── config/
├── extract/
├── load/
├── orchestration/
├── transform/
└── visualization/
```

Main responsibilities:

| Module           | Responsibility                 |
| ---------------- | ------------------------------ |
| `extract/`       | API ingestion & scraping       |
| `transform/`     | cleaning & standardization     |
| `load/`          | S3 & RDS loading               |
| `analytics/`     | scoring & ranking logic        |
| `visualization/` | Plotly analytical outputs      |
| `orchestration/` | centralized pipeline execution |

---

# Conclusion

This project demonstrates a modular cloud-based data engineering workflow combining:

* API ingestion
* web scraping
* cloud storage
* warehouse loading
* analytical transformation
* orchestration
* visualization

The implementation intentionally prioritizes clarity, modularity, and practical engineering structure over unnecessary complexity.
