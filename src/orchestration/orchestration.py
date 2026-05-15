# src/orchestration/orchestration.py

import subprocess
import sys
import logging
from src.config import LOG_DIR

PIPELINE_STEPS = [

    
    # Weather pipeline

    ("Extract coordinates from Nominatim.org", "src.extract.extract_coordinates"),

    ("Extract weather data from Openweather API", "src.extract.extract_weather"),

    ("Load raw weather data to S3", "src.load.load_to_s3"),

    ("Transform weather data", "src.transform.transform_weather"),

    ("Load transformed weather data to S3", "src.load.load_to_s3"),

    ("Load weather data to RDS", "src.load.load_to_rds"),

    ("Create top destinations table", "src.analytics.create_top_destinations"),


    
    # Hotels pipeline
    
    ("Extract hotel data from Booking.com", "src.extract.extract_booking"),

    ("Load raw hotel data to S3", "src.load.load_to_s3"),

    ("Transform booking data", "src.transform.transform_booking"),

    ("Load transformed booking data to S3", "src.load.load_to_s3"),

    ("Load booking data to RDS", "src.load.load_to_rds"),


    
    # Visualizations
    
    ("Plot top destinations", "src.visualization.plot_top_destinations"),

    ("Plot top hotels", "src.visualization.plot_top_hotels"),
]

logging.basicConfig(
    level=logging.INFO,

    format="%(asctime)s - %(levelname)s - %(message)s",

    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log"),
        logging.StreamHandler()
    ]
)


def run_module(step_name, module_name):

    logging.info(f"Starting: {step_name}")

    try:

        subprocess.run(
            [sys.executable, "-m", module_name],
            check=True,
        )

        logging.info(f"Finished: {step_name}")

    except subprocess.CalledProcessError as e:

        logging.error(
            f"Failed: {step_name} | Exit code: {e.returncode}"
        )

        raise


def main():

    for step_name, module_name in PIPELINE_STEPS:

        run_module(step_name, module_name)

    logging.info("Full pipeline completed successfully")


if __name__ == "__main__":
    main()