"""
test the transport_api module
"""
import os
import json
from datetime import datetime
from unittest.mock import patch
from src import defaults
from src.data_model.dataclasses import JourneyRequest, JourneyDetails
from src.data_model.api.transport_api import (
    retrieve_journey,
    build_query_params,
)

JOURNEY_REQUEST = JourneyRequest(
    departure_date_time=datetime(2024, 6, 2, 14, 17),
    max_wait_time=60,
    station_identifiers=["LBG", "CHX", "WAT", "HMC"],
)

JOURNEY_DETAILS = JourneyDetails(
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


class TestBuildQueryParams:
    def test_build_query_params(self):
        """
        test that we build the correct query params
        """
        built_params = build_query_params(
            origin_station="LYM",
            destination="PGN",
            departures_from=JOURNEY_REQUEST.departure_date_time,
        )
        assert built_params == {
            "from": "crs:LYM",
            "to": "crs:PGN",
            "date": JOURNEY_REQUEST.departure_date_time.strftime("%Y-%m-%d"),
            "time": JOURNEY_REQUEST.departure_date_time.strftime("%H:%M"),
            "journey_time_type": defaults.JOURNEY_TIME_TYPE,
            "service": defaults.SERVICE,
            "modes": defaults.TRAVEL_MODES,
        }


class TestTransportApi:
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_retrieve_journey(self, mock_get):
        """
        test the retrieve_journey function
        """
        assert retrieve_journey(JOURNEY_REQUEST) == JOURNEY_DETAILS
