"""
module to connect to the transport api
and retrieve journey details from there
"""
from math import floor
from dateutil import parser
from datetime import datetime
from typing import Any, Union
import requests
from src.data_model.dataclasses import JourneyDetails, JourneyRequest
from src import defaults

# ideally these should be environment variables
API_ID = "********"
API_KEY = "********************************"


def retrieve_journey(journey_request: JourneyRequest) -> JourneyDetails:
    """
    retrieve a journey from the transport api based on the station list provided.

    Args:
        journey_request (JourneyRequest): the journey request details
    Returns:
        JourneyDetails

    """

    next_departure_date_time = journey_request.departure_date_time
    travel_information_responses: dict[str, [dict[str, Any]]] = {}
    for idx, station_id in enumerate(journey_request.station_identifiers):
        travel_information_responses[station_id] = {
            "origin": station_id,
            "destination": None,
            "response": None,
        }
        destination = None
        try:
            destination = journey_request.station_identifiers[idx + 1]
        except IndexError:
            pass
        travel_information_responses[station_id]["destination"] = destination
        if not destination:
            continue
        query_params = build_query_params(
            origin_station=station_id,
            destination=destination,
            departures_from=next_departure_date_time,
        )
        response = get_query(url=defaults.BASE_URL, query_params=query_params)
        processed_response = process_response(
            response=response,
            earliest_departure_time=next_departure_date_time,
        )
        travel_information_responses[station_id]["response"] = processed_response
        next_departure_date_time = processed_response["arrival_time"]

    time_in_mins: int = 0
    train_stations_with_wait: list[dict[str, Any]] = []
    for station_id in journey_request.station_identifiers:
        travel_info = travel_information_responses[station_id].get("response")
        if not travel_info:
            train_stations_with_wait.append({
                "station_id": station_id,
                "wait_time": None
            })
            continue
        train_stations_with_wait.append({
            "station_id": station_id,
            "wait_time": travel_info.get("wait_time")
        })
        time_in_mins += travel_info.get("journey_time", 0)
        time_in_mins += travel_info.get("wait_time", 0)

    return JourneyDetails(
        time_in_mins=time_in_mins,
        departure_date_time=journey_request.departure_date_time,
        train_stations_with_wait=train_stations_with_wait,
    )


def process_response(earliest_departure_time: datetime, response: dict[str, Any]) -> dict[str, Any]:
    """
    process the response to get out the
    wait time (in mins),
    the journey_time (in mins),
    the arrival_time at the destination

    Args:
        earliest_departure_time (datetime): the earliest_departure_time possible
        response (dict[str, Any]): the response from the api

    Returns:
        {
            "wait_time": <int>,
            "journey_time": <int>,
            "arrival_time": <datetime>
        }    
    """
    response_routes = response.get("routes", [])
    if not response_routes:
        raise Exception("No routes found")

    for response_route in response_routes:
        departure_datetime = response_route.get("departure_datetime").split("+")[0]
        arrival_datetime = response_route.get("arrival_datetime").split("+")[0]
        departure_datetime = parser.parse(departure_datetime)
        arrival_datetime = parser.parse(arrival_datetime)


        wait_time_delta = departure_datetime - earliest_departure_time
        if wait_time_delta.total_seconds() < 0:
            continue

        wait_time_in_whole_mins = floor((wait_time_delta.total_seconds() / 60 ) + 0.5)

        hours, mins, _ = response_route.get("duration").split(":")
        hours = int(hours)
        mins = int(mins)
        journey_time = (hours * 60) + mins
        return {
            "wait_time": wait_time_in_whole_mins,
            "journey_time": journey_time,
            "arrival_time": arrival_datetime,
        }    

    raise Exception("No viable journey found")

def get_query(url: str, query_params: dict[str, Any]) -> dict[str, Any]:
    """
    make a request and return the json response
    """
    response = requests.get(
        url,
        params=query_params,
        headers={
            "X-App-Key": API_KEY,
            "X-App-Id": API_ID,
        },
    )  # JSON-Request API
    return response.json()


# def build_url(origin_station: str) -> str:
#     """
#     Build the url
#     """
#     return f"https://transportapi.com/v3/uk/train/station_timetables/{origin_station}.json",
#     # return f"https://transportapi.com/v3/uk/train/station_actual_journeys/{origin_station}.json"


def build_query_params(
    origin_station: str,
    destination: str,
    departures_from: datetime,
) -> dict[str, Union[str, int]]:
    """
    build up the query parameters for the request of the api

    Args:
        origin_station (str): the station id of the departure point
        destination (str): the station id if the destination
        departures_from (datetime): A datetime that specifies the earliest the train can depart from that location

    Returns:
        dict : a dictionary of the request parameters
    """

    params: dict[str, Any] = {
        "from": f"crs:{origin_station}",
        "to": f"crs:{destination}",
        "date": departures_from.strftime("%Y-%m-%d"),
        "time": departures_from.strftime("%H:%M"),
        "journey_time_type": defaults.JOURNEY_TIME_TYPE,
        "service": defaults.SERVICE,
        "modes": defaults.TRAVEL_MODES,
    }
    return params
