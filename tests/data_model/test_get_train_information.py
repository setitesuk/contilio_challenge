"""
test file to test the module src.data_model.get_train_information
"""
import os
from datetime import datetime
from src.data_model.get_train_information import retrieve_journey

from src.data_model.dataclasses import (
    JourneyDetails,
    JourneyRequest,
)
from src.data_model.db.trains import (
    initialise_database,
    store_journey,
)

JOURNEY_ONE = JourneyDetails(
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
    station_identifiers=["LBG", "SAJ", "NWX", "BXY"]
)

JOURNEY_REQUEST_TWO = JourneyRequest(
    departure_date_time=datetime(2022, 2, 9, 14, 17),
    max_wait_time=60,
    station_identifiers=["LBG", "SAJ", "NWX", "SAJ"]
)

JOURNEY_REQUEST_THREE = JourneyRequest(
    departure_date_time=datetime(2022, 2, 9, 14, 17),
    max_wait_time=60,
    station_identifiers=["LBG", "SAJ", "NWX", "SAJ", "LBG"]
)

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

    def test_retrieve_journey_sourced_api(self):
        print(retrieve_journey(JOURNEY_REQUEST_THREE))
        assert False