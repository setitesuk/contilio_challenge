# Overview
The aim of this task is to pull information from an API, into a database, and be able to query it.

We would like you to use SQLAlchemy for this task, and store the results in a SQLite database.

We have provided some skeleton code to get you started, and will be reviewing how you use Pythonic style, and OOP.

# Task Description
Given a list of train station codes (three letters), and a starting time, we want you to find the arrival time at the destination station.

For example, given the following set of train codes,
* a start_time of '2022-02-09 14:17': ['LBG', 'SAJ', 'NWX', 'BXY'] The code should return the arrival time of: 2022-02-09 14:49:00
*  ['LBG', 'SAJ', 'NWX', 'SAJ']
The code should return the arrival time of: 2022-02-09 14:41:00

Notes:
- You should store information in the database to speed up subsequent runs of the code.
- You should not find the shortest time between start and destination stations, but follow the route.
- You will be given the maximum time (in minutes) that someone is willing to wait at a station. If they have to wait longer you should display an error.
- The Transport API can be found here. You need to sign up for a free trial account.

Skeleton Code

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./trains.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":
False})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
MAX_WAIT_TIME = 60 # minutes
with Session() as session:
Base.metadata.create_all(session.get_bind()) # Create tables in database
# Run code and output time here
```
Bonus Points
- Implement an API that allows you call your function through a REST/gRPC call

# Answer

I have chosen to approach this task with the intention of it being extensible and maintainable, taking the approach of separating data_models, defaults and main call. This would then make it easier to place into the back end of an API.

## How to run

This will run in the command line
* python3 -m venv .venv
* source .venv/bin/activate
* pip install -r requirements.txt
* cd src
* python3 main.py --departure_date_time "2024-06-02 14:17" --station_identifiers LBG CHX WAT HMC

This gives output:

Arrival time: 2024-06-02 16:09:00

## test driven development

This was developed with a focus on unit test driven development, where the test folder structure mimics the src code folder structure


## data_model

The data_model directory contains
* `db` module, with the `trains.py` file that handles the tables, and store and retrieve functions
* `api` module, with the `transport_api.py` file that handles querying the api and returning the data in the same format
* `dataclasses.py` which defines the `JourneyRequest` and `JourneyDetails` classes, so that the data is enforced to a consistent format
`get_train_information.py` which acts as a controller, choosing the right method for obtaining the data, and if required, caching it

## defaults.py

The defaults are put into there own file, for ease of management. I have also put the MAX_WAIT_TIME of 60 minutes in here, as this has the potential to be changed in the future.

## main.py

main.py handles running and outputting the result.

It takes in 2 required arguments `--departure_date_time` and `--station_identifiers` and an optional override of `--max_wait_time`

These are then converted into a JourneyRequest object, which is then passed to the `main` function. This in turn calls `retrieve_journey` from `get_train_information.py`. Once the JourneyDetails object is received back, it then calls the function `stdout_output_result` to give the relevant information back to the user.

## database tables

Whilst it would have been easy to create 1 table with just the departure_date_time and the station_identifiers as a key, and a result (arrival time or error as too long to wait), I created 2 tables to store a little more information so that we could in the future actually return how long the wait periods are at each stop (as 0-2 minutes might be less than MAX_WAIT_TIME, but may be difficult to get to your next train). This makes the application a little more extensible.

Future work - store more information about each journey, in order to be able to quickly return an itinery about it.

## extension work

Due to family commitments over the weekend, I was unable to create the API functionality. To do this, I would use FastAPI or Flask to create a routing module. With this, it could take a get request with the requested departure_date_time, and a list of station identifiers in, build this into a JourneyRequest object, and pass to the retrieve_journey function in get_train_information.py. The response from this could then be passed back out as a json string in the format

```json
{"arrival_time":"<isoformat>", "error":"any error found"}
```
