# -*- coding: UTF-8 -*-

# import necessary libraries
import pandas as pd
import json
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, render_template, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///belly_button_biodiversity.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
import time
time.sleep(1)
Base.prepare(engine, reflect=True)
print(Base.classes.keys())
time.sleep(1)
# Save references to the table
Otu = Base.classes.otu
Samples = Base.classes.samples
Samples_metadata = Base.classes.samples_metadata

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

# Query the database and send the jsonified results

# Create the route for names
@app.route("/names")
def names():
    samples = Samples.__table__.columns.keys()
    return jsonify(samples)

# create the route for sample info details -- otu
@app.route("/otu")
def otu():
    bacteria_names = session.query(Otu.lowest_taxonomic_unit_found).all()
    bacteria_names = [x[0] for x in bacteria_names]
    return jsonify(bacteria_names)

# create the matadata + search sample API
@app.route("/metadata/<id>")
def metadata(id):
    
    # set up appropirate queries
    sample_metadata = session.query(Samples_metadata.AGE, Samples_metadata.BBTYPE, Samples_metadata.ETHNICITY,
                                    Samples_metadata.GENDER, Samples_metadata.LOCATION, Samples_metadata.SAMPLEID).all()
    sample_metadata = pd.DataFrame(sample_metadata)
    sample_metadata['ID'] = 'BB_' + sample_metadata['SAMPLEID'].astype(str)
    sample_metadata = sample_metadata.set_index('ID').to_dict('index')

    data = sample_metadata[id]

    metaData = []

    # for loop to append data for HTML table 
    for x, y in data.items():
        xy = {'t0': x, 't1': y}
        metaData.append(xy)

    return jsonify(metaData)

# create a route for washing freq data with id name (otu_name)
@app.route("/wfreq/<id>")
def wfreq(id):

    wfreq_data = session.query(Samples_metadata.WFREQ, Samples_metadata.SAMPLEID).all()
    wfreq_data = pd.DataFrame(wfreq_data)
    wfreq_data['ID'] = 'BB_' + wfreq_data['SAMPLEID'].astype(str)
    wfreq_data = wfreq_data.set_index('ID').to_dict('index')
    data = int(wfreq_data[id]['WFREQ'])

    return jsonify(data)

# create sample API search with otu_id 
@app.route('/samples/<id>')
def sample(id):
    
    samples_df = pd.read_sql_table('samples', engine)
    samples_df = samples_df.sort_values(by=id, ascending=0)
    samples_df = samples_df[['otu_id', id]].sort_values(by=id, ascending=0)

    samples_df.columns = ['otu_id', "sample_values"]
    samples_df_top = samples_df[samples_df['sample_values'] > 10]

    other_values = samples_df[samples_df['sample_values'] < 10]['sample_values'].sum()
    other_data = {'otu_id' : 'Other GERMS', 'sample_values' : other_values}

    samples_df_other = pd.DataFrame(other_data, index=[0])
    samples_data = pd.concat([samples_df_top, samples_df_other])
    samples_data_dic = samples_data.to_dict('list')

    return jsonify(samples_data_dic)

if __name__ == "__main__":
    app.run(debug=True, port=9000)
