"""
test file for trains
"""

import os
from datetime import datetime
from src.data_model.dataclasses import JourneyDetails
from src.data_model.db.trains import (
    Journeys,
    JourneyStations,
    initialise_database,
    Session,
    retrieve_journey,
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


class TestTrainJourneysDB:
    def setup_method(self, method):
        try:
            os.remove("trains.db")
        except Exception:
            pass
        initialise_database()

    def teardown_method(self, method):
        os.remove("trains.db")

    def test_store_journey(self):
        """
        test storing a journey
        """
        # initialise_database()
        store_journey(JOURNEY_ONE)
        db_session = Session()
        query = (
            db_session.query(Journeys, JourneyStations)
            .join(JourneyStations, JourneyStations.journey_id == Journeys.journey_id)
            .filter(Journeys.joined_journey_list == "LBG_SAJ_NWX_BXY")
            .filter(Journeys.departure_date_time == datetime(2022, 2, 9, 14, 17))
            .order_by(JourneyStations.station_order)
        )

        journey_stations = {}

        for row in query.all():
            assert row[0].total_journey_time_mins == 32
            assert row[0].departure_date_time == datetime(2022, 2, 9, 14, 17)
            journey_stations[row[1].station_identifier] = row[1]

        assert journey_stations["LBG"].wait_time_mins == 0
        assert journey_stations["LBG"].station_order == 0

        assert journey_stations["SAJ"].wait_time_mins == 10
        assert journey_stations["SAJ"].station_order == 1

        assert journey_stations["NWX"].wait_time_mins == 5
        assert journey_stations["NWX"].station_order == 2

        assert journey_stations["BXY"].wait_time_mins == None
        assert journey_stations["BXY"].station_order == 3

    def test_retrieve_journey(self):
        """
        test that the journey is retrieved ok
        """
        store_journey(JOURNEY_ONE)
        store_journey(JOURNEY_TWO)

        journey_details = retrieve_journey(
            station_list=[
                x["station_id"] for x in JOURNEY_TWO.train_stations_with_wait
            ],
            departure_date_time=JOURNEY_TWO.departure_date_time,
        )
        assert journey_details == JOURNEY_TWO
