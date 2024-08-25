"""
module to connect to the transport api
and retrieve journey details from there
"""

from datetime import datetime
from typing import Any
from src.data_model.dataclasses import JourneyDetails, JourneyRequest
from src import defaults


def retrieve_journey(journey_request: JourneyRequest) -> JourneyDetails:
    """
    retrieve a journey from the transport api based on the station list provided.

    Args:
        journey_request (JourneyRequest): the journey request details
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
        },
    ]

    for station_id in journey_request.station_identifiers:
        print(
            build_query_params(
                station_identifier=station_id,
                departures_from=journey_request.departure_date_time,
                max_wait_time=journey_request.max_wait_time,
            )
        )

    return JourneyDetails(
        time_in_mins=time_in_mins,
        departure_date_time=journey_request.departure_date_time,
        train_stations_with_wait=train_stations_with_wait,
    )


def build_query_params(
    station_identifier: str, departures_from: datetime, max_wait_time: int
):
    """
    build up the query parameters for the request of the api

    Args:
        station_identifier (str): the station id
        departures_from (datetime): A datetime that specifies the earliest the train can depart from that location
        max_wait_time (int): The maximum amount of wait time that should be used to query on

    Returns:
        dict : a dictionary of the request parameters
    """

    offset = defaults.REQUEST_OFFSET
    if max_wait_time > defaults.MAX_WAIT_TIME:
        offset = defaults.MAX_REQUEST_OFFSET

    params: dict[str, Any] = {
        "id": station_identifier,
        "datetime": departures_from.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "to_offset": offset,
        "limit": defaults.NUMBER_OF_DEPARTURES_TO_RETURN,
        "train_status": defaults.TRAIN_STATUS,
        "type": "departure",
    }
    return params
