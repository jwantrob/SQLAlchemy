# 1. import everything
from flask import Flask, jsonify
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>")



# 4. Define what to do when a user hits the route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Query
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()

    all_prcp = []
    for date, prcp in results:
        all_dict = {}
        all_dict["date"] = date
        all_dict["prcp"] = prcp
        all_prcp.append(all_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    
    # Query
    session = Session(engine)
    results = session.query(Station.station).all()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    
    # Query
    session = Session(engine)
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    # Calculate the date 1 year ago from the last data point in the database
    last=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    laststr=str(last[0])
    lastdate=datetime.strptime(laststr , '%Y-%m-%d')
    #not sure why but I had to change to 366 to ensure it included 8/23/2016
    year_ago = lastdate - dt.timedelta(days=366)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).filter(Measurement.date <= lastdate).order_by(Measurement.date).all()
    all_tobs = []
    for date, tobs in results:
        all_dict = {}
        all_dict["date"] = date
        all_dict["tobs"] = tobs
        all_tobs.append(all_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def weather(start):
    # Query
    session = Session(engine)
    resultsdate = session.query(Measurement.date)
    all_dates = list(np.ravel(resultsdate))
    results = session.query(func.min(Measurement.tobs).label('min_tobs'), func.max(Measurement.tobs).label('max_tobs'), func.avg(Measurement.tobs).label('avg_tobs')).filter(Measurement.date>=start).all()
    all_results = list(np.ravel(results))
    return jsonify(all_results)

    

@app.route("/api/v1.0/<start>/<end>")
def weather2(start, end):
    # Query
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs).label('min_tobs'), func.max(Measurement.tobs).label('max_tobs'), func.avg(Measurement.tobs).label('avg_tobs')).filter(Measurement.date>=start).filter(Measurement.date <= end).all()
    all_results = list(np.ravel(results))
    return jsonify(all_results)


if __name__ == "__main__":
    app.run(debug=True)
