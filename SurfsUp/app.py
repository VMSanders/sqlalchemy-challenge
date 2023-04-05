# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)
# Base.classes.keys() would show what tables we have but we already know from the Jupyter notebook.

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
def homepage():
    # Start at the homepage and list all available routes.
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():    
    # Convert the query results for last 12 months of data to a dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.
    
    #Initialize a dictionary.
    prcp_dict = {}
    
    # Let's grab the last 12 months' of dates in the dataset.
    dates = session.query(Measurement.date).filter(Measurement.date > '2016-08-23').order_by(Measurement.date).all()
    
    # Loop through all the dates and query the precipitation measurements for each date.
    for date in dates:
        try:
            measurements = session.query(Measurement.prcp).filter(Measurement.date == date[0]).all()
        # From working through the Jupyter notebook, I know that this query spits out a list of tuples instead of a list of numbers. I want the dictionary value for this date key to be a list of number measurements.
            prcp_dict[date[0]]=[obs[0] for obs in measurements]
        except:
            continue        
    return jsonify(prcp_dict)
    # Heads up, I know this one doesn't work. I don't really understand why because the code functions when I test it in Jupyter.

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    # Let's just grab the same query as I used in the Jupyter notebook.
    station_list = [entry[1] for entry in engine.execute('SELECT * FROM Station').fetchall()]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    # Return a JSON list of temperature observations for the previous year.
    
    # Good news: we know from the Jupyter notebook which station is the most active in this dataset. It's USC00519281. Let's reuse the queries in the notebook.
    
    active_station_measurements = session.query(Measurement.tobs).filter(Measurement.station =='USC00519281', Measurement.date > '2016-08-23')
    
    # Let's make that an actual list of numbers before we jsonify.
    msmts_list = [msmt[0] for msmt in active_station_measurements]
    
    return jsonify(msmts_list)


@app.route("/api/v1.0/<start>")
def msmts_after_date(start):
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date.
    # Query all measurements after start date
    # the .min, .max, and .avg functions didn't work for me in the Jupyter notebook, so I'm going to work with a list here too.
    msmts_list = [entry[0] for entry in session.query(Measurement.tobs).filter(Measurement.date >= start)]
    msmt_dict = {}
    msmt_dict['Min Temp']=min(msmts_list)
    msmt_dict['Avg Temp']=sum(msmts_list)/len(msmts_list)
    msmt_dict['Max Temp']=max(msmts_list)
    
    return jsonify(msmt_dict)


@app.route("/api/v1.0/<start>/<end>")
def msmts_between_dates(start,end):
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end date.
    # Query all measurements between the start and end dates.
    msmts_list = [entry[0] for entry in session.query(Measurement.tobs).filter(Measurement.date >= start, Measurement.date <= end)]
    msmt_dict = {}
    msmt_dict['Min Temp']=min(msmts_list)
    msmt_dict['Avg Temp']=sum(msmts_list)/len(msmts_list)
    msmt_dict['Max Temp']=max(msmts_list)
    
    return jsonify(msmt_dict)


# Now that we've defined everything, let's actually start the server.
if __name__ == '__main__':
    app.run(debug=True)










