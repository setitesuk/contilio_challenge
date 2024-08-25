"""
module to connect to the transport api
and retrieve journey details from there
"""

from datetime import datetime
from typing import Any
from src.data_model.dataclasses import JourneyDetails

def retrieve_journey(
    station_list: list[str], departure_date_time: datetime
) -> JourneyDetails:
    """
    retrieve a journey from the transport api based on the station list provided.

    Args:
        station_list (list[str]): a list of the station identifiers in the order that the stations should be visited
        departure_date_time (datetime): the departure date and time
    Returns:
        JourneyDetails

    """
    print("foobar")
    time_in_mins: int = 20

    train_stations_with_wait: list[dict[str, Any]] = [
        {
            "station_id": "LBG",
            "wait_time": 0,
        },
        {
            "station_id": "SAJ",
            "wait_time": 1,
        },
        {
            "station_id": "NWX",
            "wait_time": 1,
        },
        {
            "station_id": "SAJ",
            "wait_time": 2,
        },
        {
            "station_id": "LBG",
            "wait_time": None,
        }
    ]

    return JourneyDetails(
        time_in_mins=time_in_mins,
        departure_date_time=departure_date_time,
        train_stations_with_wait=train_stations_with_wait,
    )