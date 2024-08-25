"""
This file describes the tables in the trains database, and issues a session
"""
from sqlalchemy import (
    Table,
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
    connect_args={"check_same_thread":False},
)
Session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Base = declarative_base()

journeys = Table(
    "journeys",
    Base.metadata,
    Column(
        "journey_id",
        Integer,
        primary_key=True,
    ),
    Column(
        "total_journey_time_mins",
        Integer,
        nullable=False,
    ),
)

class Journeys(Base):
    """
    class to define the Journeys table
    """
    __table__ = journeys
    journey_stations = relationship(
        "JourneyStations",
        cascade="all,delete",
        backref="journey",
    )

journey_stations = Table(
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

)

class JourneyStations(Base):
    """
    class to define the JourneyStations table
    """
    __table__ = journey_stations

    __table_args__ = (
        Index(
            "idx_station_ident_journey_id",
            "station_identifier",
            "journey_id",
        ),
    )


def initialise_database():
    with Session() as session:
        Base.metadata.create_all(session.get_bind())
