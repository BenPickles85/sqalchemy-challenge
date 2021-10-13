import numpy as np
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Available routes:<br/>"
        f"Daily precipitation: /api/v1.0/precipitation<br/>"
        f"List of stations: /api/v1.0/stations<br/>"
        f"Temperature observations from last year for the most active station: /api/v1.0/tobs<br/>"
        f"Avg, max and min temp from date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Avg, max and min temp from date to end date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    final_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    final_date = dt.datetime.strptime(final_date[0], '%Y-%m-%d')
    query_date = dt.date(final_date.year -1, final_date.month, final_date.day)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()

    session.close()

    precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        precip.append(precip_dict)
        
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)

    results = session.query(Station.station, Station.name).all()

    session.close()

    stations = []
    for station,name in results:
        stations_dict = {}
        stations_dict["Station"] = station
        stations_dict["Name"] = name
        stations.append(stations_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    final_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    final_date = dt.datetime.strptime(final_date[0], '%Y-%m-%d')
    query_date = dt.date(final_date.year -1, final_date.month, final_date.day)

    station_frequency = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    station_frequency

    active_station = station_frequency[0][0]

    results = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.station == active_station).filter(Measurement.date >= query_date).all()

    session.close()

    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temp Obs"] = tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    start_tobs = []

    for min, avg, max in results:
        start_dict = {}
        start_dict["Min Temp"] = min
        start_dict["Avg Temp"] = avg
        start_dict["Max Temp"] = max
        start_tobs.append(start_dict)

    return jsonify(start_tobs)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    start_tobs = []

    for min, avg, max in results:
        start_dict = {}
        start_dict["Min Temp"] = min
        start_dict["Avg Temp"] = avg
        start_dict["Max Temp"] = max
        start_tobs.append(start_dict)

    return jsonify(start_tobs)

if __name__ == '__main__':
    app.run(debug=True)