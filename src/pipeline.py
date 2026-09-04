from csv_file_parser import parse_csv_file
from pipeline_logger import setup_logger
from open_meteo_api import fetch_meteo_api_forecast_data
from utils import get_function_time
import logging
import pandas as pd
from excel_reporter import create_excel_report
from json_reporter import generate_weather_alerts, export_alerts_to_json

logger = setup_logger(__name__)

def parse_json_response(meteo_data: Dict) -> pd.DataFrame:
    """
    Parse JSON response from Open-Meteo API and load hourly forecast into DataFrame.
    
    Args:
        meteo_data: Dictionary with 'hourly' key containing forecast data
        
    Returns:
        DataFrame with hourly forecast data
    """
    try:
        # Extract hourly data from API response
        hourly_data = meteo_data.get('hourly', {})
        
        if not hourly_data:
            logger.warning("No hourly data found in API response")
            return pd.DataFrame()
        
        # Create DataFrame from hourly data
        df = pd.DataFrame({
            'time': hourly_data.get('time', []),
            'temperature_2m': hourly_data.get('temperature_2m', []),
            'precipitation': hourly_data.get('precipitation', [])
        })
        
        logger.debug(f"Created DataFrame with {len(df)} rows")
        return df
        
    except Exception as e:
        logger.error(f"Error parsing JSON response: {e}")
        raise
 
def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in the DataFrame.
    
    Args:
        df: DataFrame with potentially missing values
        
    Returns:
        DataFrame with missing values handled
    """
    try:
        initial_nulls = df.isnull().sum().sum()
        
        # Forward fill for temperature (interpolate missing values)
        df['temperature_2m'] = df['temperature_2m'].ffill().bfill()
        
        # Fill precipitation with 0 (missing precipitation = no rain)
        df['precipitation'] = df['precipitation'].fillna(0)
        
        final_nulls = df.isnull().sum().sum()
        
        if initial_nulls > 0:
            logger.info(f"Handled {initial_nulls} missing values. Remaining: {final_nulls}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error handling missing values: {e}")
        raise

def convert_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert timestamp strings to pandas DateTime objects.
    
    Args:
        df: DataFrame with 'time' column as strings
        
    Returns:
        DataFrame with 'time' column converted to datetime
    """
    try:
        df['time'] = pd.to_datetime(df['time'])
        logger.debug("Timestamps converted to pandas DateTime objects")
        return df
        
    except Exception as e:
        logger.error(f"Error converting timestamps: {e}")
        raise
 
 
def aggregate_daily_weather(df: pd.DataFrame, city_name: str) -> pd.DataFrame:
    """
    Group hourly data by day and calculate max temperature and total precipitation.
    
    Args:
        df: DataFrame with hourly weather data
        city_name: Name of the city for reference
        
    Returns:
        DataFrame with daily aggregations
    """
    try:
        # Extract date from datetime
        df['date'] = df['time'].dt.date
        
        # Group by date and aggregate
        daily_df = df.groupby('date').agg({
            'temperature_2m': 'max',  # Maximum temperature per day
            'precipitation': 'sum'     # Total precipitation per day
        }).reset_index()
        
        # Add city name
        daily_df['city'] = city_name
        
        # Rename columns for clarity
        daily_df.columns = ['date', 'max_temperature', 'total_precipitation', 'city']
        
        # Reorder columns
        daily_df = daily_df[['city', 'date', 'max_temperature', 'total_precipitation']]
        
        logger.info(f"Aggregated weather data for {city_name}: {len(daily_df)} days")
        return daily_df
        
    except Exception as e:
        logger.error(f"Error aggregating daily weather for {city_name}: {e}")
        raise


def merge_city_weather(cities_df: pd.DataFrame, daily_weather_list: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Merge city information from CSV with aggregated weather statistics.
    
    Args:
        cities_df: DataFrame from CSV with city names, latitude, longitude
        daily_weather_list: List of DataFrames with aggregated weather data
        
    Returns:
        Merged DataFrame with city info and weather data
    """
    try:
        # Concatenate all weather DataFrames
        if not daily_weather_list:
            logger.warning("No weather data to merge")
            return cities_df
        
        weather_df = pd.concat(daily_weather_list, ignore_index=True)
        
        # Merge on city name
        merged_df = pd.merge(
            cities_df,
            weather_df,
            left_on='city',
            right_on='city',
            how='inner'  # Only keep cities that have weather data
        )
        
        logger.info(f"Merged {len(merged_df)} weather records with city data")
        return merged_df
        
    except Exception as e:
        logger.error(f"Error merging city and weather data: {e}")
        raise


 
def display_summary(merged_df: pd.DataFrame) -> None:
    """
    Display summary statistics of the merged weather data.
    
    Args:
        merged_df: Merged DataFrame with city and weather data
    """
    try:
        print(f"\n{'='*80}")
        print("WEATHER DATA SUMMARY")
        print(f"{'='*80}\n")
        
        # Overall statistics
        print(f"Total records: {len(merged_df)}")
        print(f"Cities processed: {merged_df['city'].nunique()}")
        print(f"Date range: {merged_df['date'].min()} to {merged_df['date'].max()}")
        
        # Summary by city
        print(f"\n{'City Summary:':<50}")
        print("-" * 80)
        
        city_summary = merged_df.groupby('city').agg({
            'max_temperature': ['mean', 'min', 'max'],
            'total_precipitation': ['sum', 'mean']
        }).round(2)
        
        print(city_summary)
        
        # Show first few rows
        print(f"\n{'First 10 rows of merged data:':<50}")
        print("-" * 80)
        print(merged_df.head(10).to_string(index=False))
        
    except Exception as e:
        logger.error(f"Error displaying summary: {e}")
 


def main():

    cities_list = []
    daily_weather_list = []
    df = None

    result = parse_csv_file("data/global_cities.csv")

    for city in result:
        
        logger.info(f"Procesing City: {city["city"]}")
        
        cities_list.append(city)
        
        try:
            meteo_data = get_function_time(
                fetch_meteo_api_forecast_data,
                latitude=city["latitude"],
                longitude=city["longitude"]
            )

            #  Step 1: Parse JSON into DataFrame
            hourly_df = parse_json_response(meteo_data)

            if hourly_df.empty:
                logger.warning(f"No hourly data for {city['city']}, skipping")
                continue
                
            # Step 2: Handle missing values
            hourly_df = handle_missing_values(hourly_df)

            # Step 3: Convert timestamps to DateTime
            hourly_df = convert_timestamps(hourly_df)
                
            # Step 4: Aggregate to daily statistics
            daily_df = aggregate_daily_weather(hourly_df, city['city'])

            daily_weather_list.append(daily_df)
                
            print(f"\nDaily aggregation (first 3 days):")
            print(daily_df.head(3).to_string(index=False))
                
        except Exception as e:
            logger.error(f"Error processing weather for {city['city']}: {e}")
            continue

    # Convert cities list to DataFrame
    cities_df = pd.DataFrame(cities_list)
        
    logger.info(f"Processed {len(cities_list)} cities")
    logger.info(f"Successfully fetched weather for {len(daily_weather_list)} cities")
        
    # Step 5: Merge city information with weather data
    merged_df = merge_city_weather(cities_df, daily_weather_list)
    
    display_summary(merged_df)

    create_excel_report(merged_df)

    # Generate weather alerts
    alert_payload = generate_weather_alerts(merged_df)
        
    # Export alerts to JSON
    export_alerts_to_json(alert_payload)

if __name__ == "__main__":
    main()
