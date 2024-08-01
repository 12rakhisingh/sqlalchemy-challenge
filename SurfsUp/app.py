# Import the dependencies.

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
import pandas as pd
import numpy as np

# import the Flask class and the jsonify function from the Flask
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# Define the home route
@app.route('/')
def home():
    return (
        "<h1>Welcome to the Climate App API</h1>"
        "<p>Available Routes:</p>"
        "<ul>"
        "<li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a></li>"
        "<li><a href='/api/v1.0/stations'>/api/v1.0/stations</a></li>"
        "<li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></li>"
        "<li>/api/v1.0/&lt;start&gt;</li>"
        "<li>/api/v1.0/&lt;start&gt;/&lt;end&gt;</li>"
        "</ul>"
    )

# def home():
#     print("Server received request for 'Home' page...")
#     return(
#     '''
#     Welcome to the Climate Analysis API!
#     Available Routes:
#     /api/v1.0/precipitation
#     /api/v1.0/stations
#     /api/v1.0/tobs
#     /api/v1.0/<start>
#     /api/v1.0/<start>/<end>
#     ''')

# Convert the query results to a dictionary by using date as the key and prcp as the value.

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the JSON representation of your dictionary."""
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date_str = most_recent_date[0] 
    most_recent_date_str_value = pd.to_datetime(most_recent_date_str).date()
    last_year_date = most_recent_date_str_value - dt.timedelta(days=365)

    last_year_precipitation_data = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= last_year_date).all()
    
    session.close()

    # Create a dictionary from the precipitation data
    precipitation_data = []
    for date, prcp in last_year_precipitation_data:
        prcp_dict = {}
        prcp_dict["date"] = prcp
        precipitation_data.append(prcp_dict)

    return jsonify(precipitation_data)

# A stations route that: Returns jsonified data of all of the stations in the database
@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query Stations Name from the dataset
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    stations = list(np.ravel(results))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of temperature observations for the previous year."""
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date_str = most_recent_date[0] 
    most_recent_date_str_value = pd.to_datetime(most_recent_date_str).date()
    last_year_date = most_recent_date_str_value - dt.timedelta(days=365)

    # active_station_count = [Measurement.station,func.count(Measurement.station)]
    query_active_station = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    active_station_results = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == query_active_station[0][0]).\
                    filter(Measurement.date >= last_year_date).all()

    session.close()
    
    # Convert list of tuples into normal list
    data_active_station = list(np.ravel(active_station_results))

    return jsonify(data_active_station)


@app.route("/api/v1.0/<start_date>")
def start_route(start_date):

    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the min temp, the avg temp, and the max temp for a specified start range."""
    min_max_avg = [func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    temp_stations = session.query(*min_max_avg).filter(Measurement.date >= start_date).all()

    session.close()

    # creating a list of dictionaries returns jsonify "stations_data_list" (min, max, avg) list
    stations_data_list = []
    for min,max,avg in temp_stations:
        stations_dict = {}
        stations_dict["Minimum"] = min
        stations_dict["Maximum"] = max
        stations_dict["Average"] = avg
        stations_data_list.append(stations_dict)

    # If the query returned non-null values return the results,
    # otherwise return an error message
    if stations_dict['Minimum']:
        return jsonify(start_date,stations_data_list)
    else:
        return jsonify({"error": f"Start Date {start_date} not found. Please select different start date or check the format."}), 404


@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_date_route(start_date,end_date):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the min temp, the avg temp, and the max temp for a specified start range."""
    min_max_avg = [func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    temp_stations = session.query(*min_max_avg).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    # creating a list of dictionaries returns jsonify "stations_data_range_list" (min, max, avg) list
    stations_data_range_list = []
    for min,max,avg in temp_stations:
        stations_range_dict = {}
        stations_range_dict["Minimum"] = min
        stations_range_dict["Maximum"] = max
        stations_range_dict["Average"] = avg
        stations_data_range_list.append(stations_range_dict)

    # If the query returned non-null values return the results,
    # otherwise return an error message
    if stations_range_dict['Minimum']:
        return jsonify(start_date,end_date,stations_data_range_list)
    else:
        return jsonify({"error": f"Date range {start_date} to {end_date} not found. Please select different start and end date range."}), 404


if __name__ == "__main__":
    app.run(debug=True)

