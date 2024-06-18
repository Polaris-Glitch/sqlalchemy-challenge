# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import timedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


# PRECIPITATION ROUTE
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates and prcp data"""
    # Query dates and prcp data for the last 12 months
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year).\
        order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into a dictionary
    prcp_dict = {date: prcp for date, prcp in prcp_data}

    return jsonify(prcp_dict)


# STATIONS ROUTE
@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations from the data"""
    # Query a list of all 9 stations
    most_active_stations = session.query(
        Measurement.station,
        func.count(Measurement.station).label('count')
    ).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    session.close()

    # Convert list of tuples into a list of dictionaries
    stations_list = [{"station": station, "count": count} for station, count in most_active_stations]

    return jsonify(stations_list)


# TOBS ROUTE
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return temperature data for the most active station"""
    # Query the dates and temperatures for the last 12 months of data
    one_year_ago = dt.date(2017, 8, 18) - dt.timedelta(days=365)

    temp_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into a list of dictionaries
    temp_list = [{"date": date, "temp": tobs} for date, tobs in temp_data]

    return jsonify(temp_list)


# START DATE ROUTE
@app.route('/api/v1.0/<start>', methods=['GET'])
def start(start):
        # Create our session (link) from Python to the DB
        session = Session(engine)

        """Get the min, max, and avg temp for a start date"""
        # Parse the start date from the URL parameter
        start_date = dt.strptime(start_date, '%Y-%m-%d')
            
        # Filter the data from the start date to the end of the dataset
        results = session.query(Measurement.date, Measurement.temperature).filter(Measurement.date >= start_date).all()
            
        # Extract temperatures from the results
        temperatures = [result.temperature for result in results]
            

         # Calculate min, max, and average temperatures
        min_temp = min(temperatures)
        max_temp = max(temperatures)
        avg_temp = sum(temperatures) / len(temperatures)
            
        session.close()
        
        # Return the results as a JSON response
        return jsonify({
            'start_date': start_date.strftime('%Y-%m-%d'),
            'min_temperature': min_temp,
            'max_temperature': max_temp,
            'average_temperature': avg_temp
        })
        
            


# START/END ROUTE

@app.route('/api/v1.0/<start>/<end>', methods=['GET'])
def start_end(start, end):
        # Create our session (link) from Python to the DB
        session = Session(engine)
       
        """Get the min, max, and avg temp for a start date to an end date"""
        # Parse the start date from the URL parameter
        start_date = dt.strptime(start, '%Y-%m-%d')

        # Parse the end date from the URL parameter
        end_date = dt.strptime(end, '%Y-%m-%d')

        # Query to filter the data from the start date to the end date
        results = session.query(Measurement.date, Measurement.temperature)\
                         .filter(Measurement.date >= start_date)\
                         .filter(Measurement.date <= end_date)\
                         .all()
        
        # Extract temperatures from the results
        temperatures = [result.temperature for result in results]

        if not temperatures:
            return jsonify({'error': 'No data available for the specified date range'}), 404
        
        # Calculate min, max, and average temperatures
        min_temp = min(temperatures)
        max_temp = max(temperatures)
        avg_temp = sum(temperatures) / len(temperatures)

        session.close()
        
        # Return the results as a JSON response
        return jsonify({
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'TMIN': min_temp,
            'TAVG': avg_temp,
            'TMAX': max_temp
        })



if __name__ == "__main__":
    app.run(debug=True)
