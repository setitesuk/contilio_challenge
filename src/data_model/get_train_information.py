"""
This module provides an interface to return the journey details

It should look into the database, and if it is stored there, then return this
else it should go to request the information from the transport api,
store a copy in the database, and then return the information

"""

from datetime import datetime
from src.data_model.dataclasses import JourneyDetails, JourneyRequest
from src.data_model.db.trains import (
    store_journey,
    retrieve_journey as retrieve_from_database,
    initialise_database,
)
from src.data_model.api.transport_api import retrieve_journey as retrieve_from_api


def retrieve_journey(journey_request: JourneyRequest) -> JourneyDetails:
    """
    retrieve a journey from models based on the station list provided.
    store the journey in the database if it wasn't found from there

    Args:
        journey_request (JourneyRequest): The journey that has been requested
    Returns:
        JourneyDetails

    """

    station_list = journey_request.station_identifiers
    departure_date_time = journey_request.departure_date_time

    journey_details = retrieve_from_database(
        station_list=station_list,
        departure_date_time=departure_date_time,
    )

    if journey_details.time_in_mins is not None:
        return journey_details

    print("Not cached in database, retrieving from API")
    journey_details = retrieve_from_api(
        journey_request=journey_request,
    )

    store_journey(journey=journey_details)

    return journey_details
