"""
Module for describing dataclasses
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class JourneyRequest:
    """
    A class to describe the journey request
    """
    departure_date_time: datetime
    max_wait_time: int
    station_identifiers: list[str]

@dataclass
class JourneyDetails:
    """
    A class to describe the journey details
    """
    time_in_mins: int
    departure_date_time: datetime
    train_stations_with_wait: list[dict[str, Any]]

    def as_dict(self):
        """
        return the data as a dictionary
        """
        return {
            "time_in_mins": self.time_in_mins,
            "departure_date_time": self.departure_date_time,
            "train_stations_with_wait": self.train_stations_with_wait,
        }