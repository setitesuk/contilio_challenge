"""
test file to test the module src.data_model.get_train_information
"""

import os
import json
from datetime import datetime
from unittest.mock import patch
from src.data_model.get_train_information import retrieve_journey

from src.data_model.dataclasses import (
    JourneyDetails,
    JourneyRequest,
)
from src.data_model.db.trains import (
    initialise_database,
    store_journey,
    retrieve_journey as db_retrieve_journey,
)

JOURNEY_ONE = JourneyDetails(
    time_in_mins=32,
    departure_date_time=datetime(2022, 2, 9, 14, 17),
    train_stations_with_wait=[
        {
            "station_id": "LBG",  # London Bridge
            "wait_time": 0,
        },
        {
            "station_id": "SAJ",  # St Johns
            "wait_time": 10,
        },
        {
            "station_id": "NWX",  # New Cross
            "wait_time": 5,
        },
        {
            "station_id": "BXY",  # Bexley
            "wait_time": None,
        },
    ],
)

JOURNEY_TWO = JourneyDetails(
    time_in_mins=24,
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
            "station_id": "SAJ",
            "wait_time": None,
        },
    ],
)

JOURNEY_REQUEST_ONE = JourneyRequest(
    departure_date_time=datetime(2022, 2, 9, 14, 17),
    max_wait_time=60,
    station_identifiers=["LBG", "SAJ", "NWX", "BXY"],
)

JOURNEY_REQUEST_TWO = JourneyRequest(
    departure_date_time=datetime(2022, 2, 9, 14, 17),
    max_wait_time=60,
    station_identifiers=["LBG", "SAJ", "NWX", "SAJ"],
)

JOURNEY_REQUEST_THREE = JourneyRequest(
    departure_date_time=datetime(2024, 2, 9, 14, 17),
    max_wait_time=60,
    station_identifiers=["LBG", "SAJ", "NWX", "SAJ", "LBG"],
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

class TestSourceFromDatabase:
    def setup_method(self, method):
        try:
            os.remove("trains.db")
        except Exception:
            pass
        initialise_database()
        store_journey(JOURNEY_ONE)
        store_journey(JOURNEY_TWO)

    def teardown_method(self, method):
        os.remove("trains.db")

    def test_retrieve_journey_sourced_db(self):
        assert retrieve_journey(JOURNEY_REQUEST_ONE) == JOURNEY_ONE
        assert retrieve_journey(JOURNEY_REQUEST_TWO) == JOURNEY_TWO


class TestSourceFromAPI:
    def setup_method(self, method):
        try:
            os.remove("trains.db")
        except Exception:
            pass
        initialise_database()
        store_journey(JOURNEY_ONE)
        store_journey(JOURNEY_TWO)

    def teardown_method(self, method):
        os.remove("trains.db")

    @patch("requests.get", side_effect=mocked_requests_get)
    def test_retrieve_journey_sourced_api(self, mock_get):

        # prove that it is not in the database
        assert db_retrieve_journey(
            station_list=API_JOURNEY_REQUEST.station_identifiers,
            departure_date_time=API_JOURNEY_REQUEST.departure_date_time,
        ) == JourneyDetails(
            time_in_mins=None,
            train_stations_with_wait=[],
            departure_date_time=API_JOURNEY_REQUEST.departure_date_time
        )

        # the fetch will come from the api as it is not in the database
        assert retrieve_journey(API_JOURNEY_REQUEST) == API_JOURNEY_DETAILS

        # prove that it is now cached in the database
        assert db_retrieve_journey(
            station_list=API_JOURNEY_REQUEST.station_identifiers,
            departure_date_time=API_JOURNEY_REQUEST.departure_date_time,
        ) == API_JOURNEY_DETAILS

class TestSourceFromAPINoInitialisedDB:
    def setup_method(self, method):
        try:
            os.remove("trains.db")
        except Exception:
            pass

    def teardown_method(self, method):
        try:
            os.remove("trains.db")
        except Exception:
            pass

    @patch("requests.get", side_effect=mocked_requests_get)
    def test_retrieve_journey_sourced_api_no_db(self, mock_get):

        # the fetch will come from the api as it is not in the database
        assert retrieve_journey(API_JOURNEY_REQUEST) == API_JOURNEY_DETAILS

        # prove that it is now cached in the database
        assert db_retrieve_journey(
            station_list=API_JOURNEY_REQUEST.station_identifiers,
            departure_date_time=API_JOURNEY_REQUEST.departure_date_time,
        ) == API_JOURNEY_DETAILS
