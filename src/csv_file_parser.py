from pathlib import Path
import logging
import csv
from collections.abc import Generator
from pipeline_logger import setup_logger
import re

# Initialize logger
logger = setup_logger(__name__)


def clean_city_record(raw_city: str) -> str:
    # Remove white spaces at the beggining and the end and apply Title Case
    city_cleaned = raw_city.strip().title()

    # Replace special characters with space
    city_cleaned = re.sub(r"[+.!@#$%^&*()]", " ", city_cleaned)

    # Remvoe additional spaces between city name
    city_cleaned = re.sub(r" +", " ", city_cleaned).strip()

    # return cleaned  city name
    return city_cleaned


def clean_coordinate(raw_coordinate: str) -> str:
    coordinate_cleaned = raw_coordinate.strip()

    # Replace special characters with space
    coordinate_cleaned = re.sub(r"[!@#$%^&*()]", " ", coordinate_cleaned)

    # Remvoe additional spaces between city name
    coordinate_cleaned = re.sub(r" +", " ", coordinate_cleaned).strip()

    return coordinate_cleaned


def parse_csv_file(file_path: str) -> Generator[dict, None, None]:
    """
    Parse the csv files of global cities using regex
    and string manipulation.

    Args:
    file_path: path of the csv file name. data/global_cities.csv

    Returns:
        a generator of type dict with keys city, latitude, longitude
        each dict is clean and parsed properly
    """
    try:
        csv_file_path = Path(file_path)

        # Validate file exists and is CSV
        if not csv_file_path.exists():
            raise FileNotFoundError(f"File not found: {csv_file_path}")

        if csv_file_path.suffix.lower() != ".csv":
            raise FileNotFoundError(f"File is not a CSV: {csv_file_path}")

        # Context manager for the file, auto close on sucess or error
        with open(csv_file_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)

            # Validate headers
            if not csv_reader.fieldnames:
                raise ValueError("CSV file is empty or has no headers")

            # Validate my csv file structure
            required_columns = {"city", "latitude", "longitude"}
            if not required_columns.issubset(set(csv_reader.fieldnames)):
                raise ValueError(f"CSV missing required columns: {required_columns}")

            city_records_count = 0
            for city_record in csv_reader:
                city_records_count += 1

                city_record["city"] = clean_city_record(city_record["city"])
                city_record["latitude"] = clean_coordinate(city_record["latitude"])
                city_record["longitude"] = clean_coordinate(city_record["longitude"])
                yield city_record

            if city_records_count == 0:
                logger.warning(f"CSV file has no data rows: {csv_file_path}")

    except (FileNotFoundError, ValueError) as e:
        logger.error(f"CSV parsing error: {e}")
        raise
