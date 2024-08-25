"""
This file describes the tables in the trains database, and issues a session
"""

from typing import Any
from sqlalchemy import (
    Table,
    UniqueConstraint,
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

SQLALCHEMY_DATABASE_URL = "sqlite:///./trains.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
Session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Base = declarative_base()


JOURNEYS = Table(
    "journeys",
    Base.metadata,
    Column(
        "journey_id",
        Integer,
        primary_key=True,
    ),
    Column(
        "joined_journey_list",
        String,
        nullable=False,
    ),
    Column(
        "total_journey_time_mins",
        Integer,
        nullable=False,
    ),
    UniqueConstraint("joined_journey_list", name="uidx_joined_journey_list"),
)


class Journeys(Base):
    """
    class to define the Journeys table
    """

    __table__ = JOURNEYS
    journey_stations = relationship(
        "JourneyStations",
        cascade="all,delete",
        backref="journey",
    )


JOURNEY_STATIONS = Table(
    "journey_stations",
    Base.metadata,
    Column(
        "journey_station_id",
        Integer,
        primary_key=True,
    ),
    Column(
        "journey_id",
        String,
        ForeignKey(
            "journeys.journey_id",
            ondelete="Cascade",
            onupdate="Cascade",
        ),
    ),
    Column(
        "station_order",
        Integer,
        nullable=False,
    ),
    Column(
        "station_identifier",
        String,
        nullable=False,
    ),
    Column(
        "wait_time_mins",
        Integer,
        nullable=True,
    ),
)


class JourneyStations(Base):
    """
    class to define the JourneyStations table
    """

    __table__ = JOURNEY_STATIONS

    __table_args__ = (
        Index(
            "idx_station_ident_journey_id",
            "station_identifier",
            "journey_id",
        ),
    )


def initialise_database() -> None:
    """
    Initialise the database
    """
    with Session() as session:
        Base.metadata.create_all(session.get_bind())


def store_journey(journey: dict[str, Any]) -> None:
    """
    Store a journey

    Args:
        journey (dict[str, Any]): The description of the journey as follows

        {
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

    """
    db_session = Session()
    joined_journey_list = "_".join(
        [x["station_id"] for x in journey.get("train_stations_with_wait")]
    )
    journey_row = Journeys(
        joined_journey_list=joined_journey_list,
        total_journey_time_mins=journey.get("time_in_mins"),
    )
    db_session.add(journey_row)
    db_session.flush()
    journey_id = journey_row.journey_id

    for idx, station in enumerate(journey.get("train_stations_with_wait", [])):
        journey_station_row = JourneyStations(
            journey_id=journey_id,
            station_order=idx,
            station_identifier=station.get("station_id", None),
            wait_time_mins=station.get("wait_time", None),
        )
        db_session.add(journey_station_row)
    db_session.commit()


def retrieve_journey(station_list: list[str]) -> dict[str, Any]:
    """
    retrieve a journey from the database based on the station list provided.

    Args:
        station_list (list[str]): a list of the station identifiers in the order that the stations should be visited

    Returns:
        {
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


    """
    db_session = Session()
    query = (
        db_session.query(Journeys, JourneyStations)
        .join(JourneyStations, JourneyStations.journey_id == Journeys.journey_id)
        .filter(Journeys.joined_journey_list == "_".join(station_list))
        .order_by(JourneyStations.station_order)
    )

    journey_details: dict[str, Any] = {"train_stations_with_wait": []}

    for row in query.all():
        if not journey_details.get("time_in_mins"):
            journey_details["time_in_mins"] = row[0].total_journey_time_mins
        journey_details["train_stations_with_wait"].append(
            {
                "station_id": row[1].station_identifier,
                "wait_time": row[1].wait_time_mins,
            }
        )
    return journey_details
