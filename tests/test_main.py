"""
tests the src/main.py file
"""

import pytest
from datetime import datetime
from unittest.mock import patch
from src.main import (
    is_wait_is_too_long,
    get_datetime_from_string,
    date_time_as_a_string,
)
from src.data_model.dataclasses import JourneyDetails

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
