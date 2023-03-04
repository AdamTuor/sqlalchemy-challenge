import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

measurement=Base.classes.measurement
station=Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """List last 12 months of precipitation data"""

    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= prev_year).all()
    session.close()

    one_year = []

    for date, prcp in results:
        year_dict={}
        year_dict['date']= date
        year_dict['precipitation'] = prcp
        one_year.append(year_dict)


    return jsonify(one_year)

@app.route("/api/v1.0/stations")
def stations_list():
    """Return a list of stations"""
    
    session = Session(engine)
    stations =session.query(measurement.station).group_by(measurement.station)
    session.close()

    all_stations= []

    for station in stations:
        station_dict = {}
        station_dict['station']=station[0]
        all_stations.append(station_dict)
   
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the dates and temperature observations of the most-active station for the previous year of data."""

    
    session = Session(engine)
    tobs_data = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281')
    session.close()

    tobs_list = []

    for date, tobs in tobs_data:
        tobs_dict={}
        tobs_dict['date']=date
        tobs_dict['temperature']=tobs
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date_only(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date"""
    
    session = Session(engine)

    start_date_data = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date >= start)
    session.close()
    
    start_date_list = []
    
    for data in start_date_data:
        start_date_dict={}
        start_date_dict['min temp'] = data[0]
        start_date_dict['max temp'] = data[1]
        start_date_dict['avg temp'] = data[2]
        start_date_list.append(start_date_dict)
    return jsonify(start_date_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range."""
    
    session = Session(engine)
    start_end_date_data = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end)
    session.close()

    start_end_list=[]

    for data in start_end_date_data:
        start_end_dict={}
        start_end_dict['min temp'] = data[0]
        start_end_dict['max temp'] = data[1]
        start_end_dict['avg temp'] = data[2]
        start_end_list.append(start_end_dict)
    return jsonify(start_end_list)

if __name__ == "__main__":
    app.run(debug=True)