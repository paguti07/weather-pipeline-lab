import numpy as np
import pandas as pd

from pipeline import (
    aggregate_daily_weather,
    convert_timestamps,
    handle_missing_values,
    merge_city_weather,
    parse_json_response,
)


def test_parse_json_response_builds_dataframe():
    meteo_data = {
        "hourly": {
            "time": ["2026-01-01T00:00", "2026-01-01T01:00"],
            "temperature_2m": [10.0, 11.0],
            "precipitation": [0.0, 0.5],
        }
    }

    df = parse_json_response(meteo_data)

    assert list(df.columns) == ["time", "temperature_2m", "precipitation"]
    assert len(df) == 2
    assert df["temperature_2m"].tolist() == [10.0, 11.0]


def test_parse_json_response_missing_hourly_key_returns_empty_dataframe():
    df = parse_json_response({})
    assert df.empty


def test_handle_missing_values_fills_temperature_and_precipitation():
    df = pd.DataFrame(
        {
            "temperature_2m": [10.0, np.nan, 12.0],
            "precipitation": [0.0, np.nan, 1.0],
        }
    )

    result = handle_missing_values(df)

    assert result["temperature_2m"].tolist() == [10.0, 10.0, 12.0]
    assert result["precipitation"].tolist() == [0.0, 0.0, 1.0]
    assert result.isnull().sum().sum() == 0


def test_convert_timestamps_converts_strings_to_datetime():
    df = pd.DataFrame({"time": ["2026-01-01T00:00", "2026-01-01T01:00"]})

    result = convert_timestamps(df)

    assert pd.api.types.is_datetime64_any_dtype(result["time"])


def test_aggregate_daily_weather_groups_by_date():
    df = pd.DataFrame(
        {
            "time": pd.to_datetime(
                [
                    "2026-01-01T00:00",
                    "2026-01-01T01:00",
                    "2026-01-02T00:00",
                ]
            ),
            "temperature_2m": [10.0, 15.0, 5.0],
            "precipitation": [0.0, 1.0, 2.0],
        }
    )

    daily_df = aggregate_daily_weather(df, "Tokyo")

    assert list(daily_df.columns) == [
        "city",
        "date",
        "max_temperature",
        "total_precipitation",
    ]
    assert len(daily_df) == 2
    assert (daily_df["city"] == "Tokyo").all()

    day_one = daily_df[daily_df["date"] == pd.Timestamp("2026-01-01").date()].iloc[0]
    assert day_one["max_temperature"] == 15.0
    assert day_one["total_precipitation"] == 1.0


def test_merge_city_weather_inner_joins_on_city():
    cities_df = pd.DataFrame(
        {
            "city": ["Tokyo", "Cairo"],
            "latitude": ["35.6762", "30.0444"],
            "longitude": ["139.6503", "31.2357"],
        }
    )
    daily_weather = pd.DataFrame(
        {
            "city": ["Tokyo"],
            "date": [pd.Timestamp("2026-01-01").date()],
            "max_temperature": [15.0],
            "total_precipitation": [1.0],
        }
    )

    merged_df = merge_city_weather(cities_df, [daily_weather])

    assert len(merged_df) == 1
    assert merged_df.iloc[0]["city"] == "Tokyo"
    assert "Cairo" not in merged_df["city"].tolist()


def test_merge_city_weather_returns_cities_df_when_no_weather_data():
    cities_df = pd.DataFrame(
        {"city": ["Tokyo"], "latitude": ["35.6762"], "longitude": ["139.6503"]}
    )

    merged_df = merge_city_weather(cities_df, [])

    pd.testing.assert_frame_equal(merged_df, cities_df)
