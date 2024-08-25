"""
test file for trains
"""
from src.data_model.db.trains import (
    Journeys,
    JourneyStations,
    initialise_database,
    Session,
    store_journey,
)

JOURNEY_ONE = {
    "time_in_mins": 32,
    "train_stations_with_wait": [
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
    ]
}

JOURNEY_TWO = {
    "time_in_mins": 24,
    "train_stations_with_wait": [
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
    ]
}


class TestStoringTrainJourneys:
    def test_store_journey(self):
        """
        test storing a journey
        """
        store_journey(JOURNEY_ONE)
        db_session = Session()
        query = db_session.query(
            Journeys,
            JourneyStations
        ).join(
            JourneyStations,
            JourneyStations.journey_id == Journeys.journey_id
        ).order_by(JourneyStations.station_order)

        journey_stations = {}

        for row in query.all():
            assert row[0].total_journey_time_mins == 32
            journey_stations[row[1].station_identifier] = row[1]

        assert journey_stations["LBG"].wait_time == 0
        assert journey_stations["LBG"].station_order == 0

        assert journey_stations["SAJ"].wait_time == 10
        assert journey_stations["SAJ"].station_order == 1

        assert journey_stations["NWX"].wait_time == 5
        assert journey_stations["NWX"].station_order == 2

        assert journey_stations["BXY"].wait_time == None
        assert journey_stations["BXY"].station_order == 3
