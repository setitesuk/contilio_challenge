"""
main file to run the application
"""
import os
import sys
import argparse
from dateutil import parser
from datetime import datetime
from typing import Any

from tomlkit import date

module_path = os.path.abspath(os.path.join(".."))
if module_path not in sys.path:
    sys.path.append(module_path)

from src.data_model.dataclasses import JourneyDetails, JourneyRequest
from src.data_model.db.trains import (
    store_journey,
    retrieve_journey,
    initialise_database,
)
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
    except Exception as err:
        print("datetime is not in a recognised format")
        raise
    return dt_object

def main(journey_request: JourneyRequest) -> None:
    """
    primary function to run the code
    """
    print(journey_request)
    journey_details = retrieve_journey(
        station_list=journey_request.station_identifiers,
        departure_date_time=journey_request.departure_date_time,
    )
    print(journey_details)


if __name__ == "__main__":
    try:
        arg_parser = argparse.ArgumentParser(
            description="How long is my journey?"
        )
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

        departure_date_time = get_datetime_from_string(args.departure_date_time)
        max_wait_time = args.max_wait_time
        if max_wait_time is None:
            max_wait_time = defaults.MAX_WAIT_TIME
        journey_request = JourneyRequest(
            departure_date_time=departure_date_time,
            max_wait_time=max_wait_time,
            station_identifiers=args.station_identifiers,
        )
        print("*************")
        print(args)
        main(journey_request=journey_request)
    except Exception as err:
        print(err)
