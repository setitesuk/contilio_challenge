"""
tests the src/main.py file
"""
import os
import json
import pytest
from datetime import datetime
from unittest.mock import patch
from src.main import (
    is_wait_is_too_long,
    get_datetime_from_string,
    date_time_as_a_string,
    main,
)
from src.data_model.dataclasses import JourneyDetails, JourneyRequest

JOURNEY = JourneyDetails(
    time_in_mins=32,
    departure_date_time=datetime(2022, 2, 9, 14, 17),
    train_stations_with_wait=[
        {
            "station_id": "LBG",
            "wait_time": 0,
        },
        {
            "station_id": "SAJ",
            "wait_time": 10,
        },
        {
            "station_id": "NWX",
            "wait_time": 5,
        },
        {
            "station_id": "BXY",
            "wait_time": None,
        },
    ],
)

API_JOURNEY_REQUEST = JourneyRequest(
    departure_date_time=datetime(2024, 6, 2, 14, 17),
    max_wait_time=60,
    station_identifiers=["LBG", "CHX", "WAT", "HMC"],
)

API_JOURNEY_DETAILS = JourneyDetails(
    time_in_mins=112,
    departure_date_time=datetime(2024, 6, 2, 14, 17),
    train_stations_with_wait=[
        {
            "station_id": "LBG",
            "wait_time": 0,
        },
        {
            "station_id": "CHX",
            "wait_time": 6,
        },
        {
            "station_id": "WAT",
            "wait_time": 27,
        },
        {
            "station_id": "HMC",
            "wait_time": None,
        },
    ],
)
BASE_URL = "https://transportapi.com/v3/uk/public_journey.json"

LBG_CHX_ARGS = {
    "from": "crs:LBG",
    "to": "crs:CHX",
    "date": "2024-06-02",
    "time": "14:17",
    "journey_time_type": "leave_after",
    "service": "tfl",
    "modes": "train",
}
CHX_WAT_ARGS = {
    "from": "crs:CHX",
    "to": "crs:WAT",
    "date": "2024-06-02",
    "time": "14:33",
    "journey_time_type": "leave_after",
    "service": "tfl",
    "modes": "train",
}
WAT_HMC_ARGS = {
    "from": "crs:WAT",
    "to": "crs:HMC",
    "date": "2024-06-02",
    "time": "14:39",
    "journey_time_type": "leave_after",
    "service": "tfl",
    "modes": "train",
}
HMC_NEM_ARGS = {
    "from": "crs:HMC",
    "to": "crs:NEM",
    "date": "2024-06-02",
    "time": "15:33",
    "journey_time_type": "leave_after",
    "service": "tfl",
    "modes": "train",
}


ROOT_EXAMPLE_FILES = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "data_model",
        "api",
        "example_api_responses",
    )
)

MOCK_LBG_CHX_JOURNEY = {}
with open(
    f"{ROOT_EXAMPLE_FILES}/lbg_chx.json",
    encoding="utf-8",
    mode="+r",
) as fh:
    MOCK_LBG_CHX_JOURNEY = json.load(fh)

MOCK_CHX_WAT_JOURNEY = {}
with open(
    f"{ROOT_EXAMPLE_FILES}/chx_wat.json",
    encoding="utf-8",
    mode="+r",
) as fh:
    MOCK_CHX_WAT_JOURNEY = json.load(fh)

MOCK_WAT_HMC_JOURNEY = {}
with open(
    f"{ROOT_EXAMPLE_FILES}/wat_hmc.json",
    encoding="utf-8",
    mode="+r",
) as fh:
    MOCK_WAT_HMC_JOURNEY = json.load(fh)

MOCK_HMC_NEM_JOURNEY = {}
with open(
    f"{ROOT_EXAMPLE_FILES}/hmc_nem.json",
    encoding="utf-8",
    mode="+r",
) as fh:
    MOCK_HMC_NEM_JOURNEY = json.load(fh)


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if kwargs["params"]["from"] == "crs:LBG":
        return MockResponse(MOCK_LBG_CHX_JOURNEY, 200)
    if kwargs["params"]["from"] == "crs:CHX":
        return MockResponse(MOCK_CHX_WAT_JOURNEY, 200)
    if kwargs["params"]["from"] == "crs:WAT":
        return MockResponse(MOCK_WAT_HMC_JOURNEY, 200)
    if kwargs["params"]["from"] == "crs:HMC":
        return MockResponse(MOCK_HMC_NEM_JOURNEY, 200)

    return MockResponse(None, 404)

class TestMainIsWaitTooLong:
    def test_passenger_will_not_wait_longer_than_60_mins(self):
        """
        The passenger will not wait longer than 60 mins,
        so the journey does not have any waits that are too long
        """
        assert is_wait_is_too_long(journey_details=JOURNEY, max_wait_time=60) is False

    def test_passenger_will_not_wait_longer_than_8_mins(self):
        """
        The passenger will not wait longer than 8 mins,
        so the journey does have waits that are too long
        """
        assert is_wait_is_too_long(journey_details=JOURNEY, max_wait_time=8) is True


class TestGetDateTimeFromString:
    def test_get_date_time_parses_ok(self):
        """
        tests when the date_time parser works ok
        """
        assert isinstance(get_datetime_from_string("2022-02-09 14:17"), datetime)

    @patch("src.main.parser")
    def test_get_date_time_raises_when_not_ok(self, mock_parser):
        """
        raises when the date_time parser does not work
        """

        def side_effect(*args, **kwargs):
            raise (Exception)

        mock_parser.parse.side_effect = side_effect
        with pytest.raises(Exception) as err:
            get_datetime_from_string("9-10-2022")


class TestDateTimeAsAString:
    def test_date_time_as_a_string(self):
        assert (
            date_time_as_a_string(datetime(2022, 2, 9, 14, 17)) == "2022-02-09 14:17:00"
        )
        assert (
            date_time_as_a_string(datetime(2022, 2, 9, 14, 49)) == "2022-02-09 14:49:00"
        )


class TestMain:
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_main(self, mock_get, capsys):
        """
        Run a test of the main function
        """
        main(journey_request=API_JOURNEY_REQUEST)
        captured = capsys.readouterr()
        assert "Not cached in database, retrieving from API" in captured.out
        assert "Arrival time: 2024-06-02 16:09:00" in captured.out
        main(journey_request=API_JOURNEY_REQUEST)
        captured = capsys.readouterr()
        assert "Not cached in database, retrieving from API" not in captured.out
        assert "Arrival time: 2024-06-02 16:09:00" in captured.out
