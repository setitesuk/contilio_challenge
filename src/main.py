"""
main file to run the application
"""

import os
import sys
import argparse
from dateutil import parser
from datetime import datetime, timedelta
from typing import Any

from tomlkit import date

module_path = os.path.abspath(os.path.join(".."))
if module_path not in sys.path:
    sys.path.append(module_path)

from src.data_model.dataclasses import JourneyDetails, JourneyRequest
from src.data_model.get_train_information import retrieve_journey
from src import defaults


# Run code and output time here


def is_wait_is_too_long(journey_details: JourneyDetails, max_wait_time: int) -> bool:
    """
    see if the wait at any station is too long for the passenger

    Args:
        journey_details (JourneyDetails): the journey details
        max_wait_time (int): the maximum time a passenger will wait at any station

    Returns:
        bool : True is the wait is too long at any station

    """

    for wait_time in [x["wait_time"] for x in journey_details.train_stations_with_wait]:
        if wait_time is not None and wait_time > max_wait_time:
            return True
    return False


def get_datetime_from_string(datetime_str: str) -> datetime:
    """
    converts a datetime string into a datetime object
    """
    try:
        dt_object = parser.parse(datetime_str)
    except Exception:
        print("datetime is not in a recognised format")
        raise
    return dt_object


def date_time_as_a_string(
    date_time: datetime,
) -> str:
    """
    Takes a datetime object and returns as a string in the format

    Args:
        date_time (datetime): a datetime object

    Returns:
        str: a string in the format "2022:02:09 14:17:00"
    """
    return date_time.strftime("%Y-%m-%d %H:%M:%S")


def stdout_output_result(
    journey_request: JourneyRequest,
    journey_details: JourneyDetails,
) -> None:
    """
    Output to STDOUT the result
    """
    if is_wait_is_too_long(
        journey_details=journey_details, max_wait_time=journey_request.max_wait_time
    ):
        print(
            f"Error: This journey has at least one wait at a station longer than the requested maximum wait time of {journey_request.max_wait_time} minutes."
        )
        return

    print(f"Arrival time: {date_time_as_a_string(journey_details.arrival_date_time())}")


def main(journey_request: JourneyRequest) -> None:
    """
    primary function to run the code
    """
    print(journey_request)
    journey_details = retrieve_journey(journey_request=journey_request)
    print(journey_details)
    stdout_output_result(
        journey_request=journey_request,
        journey_details=journey_details,
    )


if __name__ == "__main__":
    try:
        arg_parser = argparse.ArgumentParser(description="How long is my journey?")
        arg_parser.add_argument(
            "--departure_date_time",
            dest="departure_date_time",
            help="The departure date & time in ISO8601 format",
            required=True,
        )
        arg_parser.add_argument(
            "--station_identifiers",
            nargs="+",
            dest="station_identifiers",
            help="give a list of space separated station identifiers in the order the journey should be taken",
            required=True,
        )
        arg_parser.add_argument(
            "--max_wait_time",
            dest="max_wait_time",
            help="the maximum amount of time (in mins) that you would wait at a station",
            required=False,
        )
        args = arg_parser.parse_args()

        request_departure_date_time = get_datetime_from_string(args.departure_date_time)
        max_wait_time = args.max_wait_time
        if max_wait_time is None:
            max_wait_time = defaults.MAX_WAIT_TIME
        request_journey = JourneyRequest(
            departure_date_time=request_departure_date_time,
            max_wait_time=max_wait_time,
            station_identifiers=args.station_identifiers,
        )
        print("*************")
        print(args)
        main(journey_request=request_journey)
    except Exception as err:
        print(err)
