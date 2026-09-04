from tenacity import (
    RetryCallState,
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential,
    wait_exponential_jitter,
)

from collections.abc import Generator
from pipeline_logger import setup_logger
import requests
from dotenv import load_dotenv
import os
import urllib3


logger = setup_logger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from .env file
load_dotenv()

# Get WEATHER_UNIT from .env, default to celcius if not set
WEATHER_UNIT = os.getenv("WEATHER_UNIT", "celcius").lower()

# Get MAX_RETRIES from .env, default to 3 if not set
MAX_RETRIES = os.getenv("MAX_RETRIES", "3")


def log_attempt_number(retry_state):
    pass


#     print(f"Attempt {retry_state.attempt_number} failed")
#     print(f"Retrying in {retry_state.next_action.sleep:.2f} seconds...")


@retry(
    wait=wait_exponential_jitter(
        initial=1, max=10
    ),  # ? Starts 1s wait, scales up to 10s wait, with additional random jitter waiting time
    stop=stop_after_attempt(int(MAX_RETRIES)),  # ? Will retry MAX_RETRIES times
    reraise=True,  # ? Reraise the original exception if all attempts fail
    before_sleep=log_attempt_number,  # ? Execute before every retry attempt
)
def fetch_meteo_api_forecast_data(latitude: float, longitude: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_unit": WEATHER_UNIT,
	    "hourly": ["temperature_2m", "precipitation"],
	    "timezone": "auto",
    }
    response = requests.get(url, params=params, verify=False)
    response.raise_for_status()
    return response.json()
