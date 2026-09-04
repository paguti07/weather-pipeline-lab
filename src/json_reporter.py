import pandas as pd
import logging
from dotenv import load_dotenv
import os
from pipeline_logger import setup_logger
from datetime import datetime
import json
from pathlib import Path
from typing import List, Dict

logger = setup_logger(__name__)


# Load environment variables from .env file
load_dotenv()

# Get WEATHER_UNIT from .env, default to 30 if not set
ALERT_THRESHOLD_C = os.getenv("ALERT_THRESHOLD_C", "30")


def generate_weather_alerts(
    merged_df: pd.DataFrame,
    temperature_threshold: float = float(ALERT_THRESHOLD_C)
) -> Dict:
    """
    Generate weather alert payload for cities exceeding temperature threshold.
    
    Args:
        merged_df: Merged DataFrame with weather data
        temperature_threshold: Temperature threshold (default: 30°C)
        
    Returns:
        Dictionary with alert payload
    """
    try:
        logger.info(f"Generating weather alerts (threshold: > {temperature_threshold}°C)")
        
        # Filter cities exceeding threshold
        alert_data = merged_df[merged_df['max_temperature'] > temperature_threshold]
        
        if alert_data.empty:
            logger.warning(f"No cities exceed {temperature_threshold}°C threshold")
            return {
                'alert_timestamp': datetime.now().isoformat(),
                'threshold_celsius': temperature_threshold,
                'alert_count': 0,
                'cities_in_alert': []
            }
        
        # Group by city and create alert payload
        alerts = []
        for city in alert_data['city'].unique():
            city_data = alert_data[alert_data['city'] == city]

            # Get highest temperature record
            max_temp_record = city_data.loc[city_data['max_temperature'].idxmax()]
            
            alert_dict = {
                'city': city,
                'latitude': max_temp_record['latitude'],
                'longitude': max_temp_record['longitude'],
                'alert_type': 'HIGH_TEMPERATURE',
                'threshold_celsius': temperature_threshold,
                'max_temperature_recorded': float(max_temp_record['max_temperature']),
                'date': str(max_temp_record['date']),
                'excess_degrees': round(max_temp_record['max_temperature'] - temperature_threshold, 1)
            }
            alerts.append(alert_dict)
        
        # Create alert payload
        alert_payload = {
            'alert_timestamp': datetime.now().isoformat(),
            'alert_system': 'Weather Alert System v1.0',
            'threshold_celsius': temperature_threshold,
            'alert_count': len(alerts),
            'cities_in_alert': sorted(alerts, key=lambda x: x['max_temperature_recorded'], reverse=True)
        }
        
        logger.info(f"Generated {len(alerts)} weather alerts")
        return alert_payload
        
    except Exception as e:
        logger.error(f"Error generating weather alerts: {e}")
        raise


 
def export_alerts_to_json(
    alert_payload: Dict,
    output_path: str = "reports/weather_alerts.json",
) -> Path:
    """
    Export weather alert payload to JSON file.
    
    Args:
        alert_payload: Dictionary with alert data
        reports_dir: Directory to save JSON file
        filename: Output filename
        
    Returns:
        Path to created JSON file
    """
    try:
        json_path = Path(output_path)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting JSON alert export to: {json_path}")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(alert_payload, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON alert export completed: {json_path}")
        print(f"✓ Weather alerts JSON saved: {json_path}")
        
        return json_path
        
    except Exception as e:
        logger.error(f"Error exporting alerts to JSON: {e}")
        raise
 