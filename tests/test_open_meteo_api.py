from unittest.mock import Mock, patch

from open_meteo_api import fetch_meteo_api_forecast_data


def test_fetch_meteo_api_forecast_data_returns_json_payload():
    payload = {
        "hourly": {
            "time": ["2026-01-01T00:00"],
            "temperature_2m": [10.0],
            "precipitation": [0.0],
        }
    }
    mock_response = Mock()
    mock_response.json.return_value = payload
    mock_response.raise_for_status.return_value = None

    with patch("open_meteo_api.requests.get", return_value=mock_response) as mock_get:
        result = fetch_meteo_api_forecast_data(latitude=35.6762, longitude=139.6503)

    assert result == payload
    mock_get.assert_called_once()
    mock_response.raise_for_status.assert_called_once()

    _, kwargs = mock_get.call_args
    assert kwargs["params"]["latitude"] == 35.6762
    assert kwargs["params"]["longitude"] == 139.6503
    called_url = (
        mock_get.call_args.args[0] if mock_get.call_args.args else kwargs.get("url")
    )
    assert called_url == "https://api.open-meteo.com/v1/forecast"
