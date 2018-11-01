import os
import json
import datetime
from copy import deepcopy
from flask import send_from_directory
from flask import Flask, render_template, url_for, redirect
from flask_migrate import Migrate
from models import app, db, Job_List
from state_district import code, state

Migrate(app, db)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon.ico', mimetype='image/vnd.microsoft.icon')
@app.route('/')
def base():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/harvest_aider')
def harvest_aider():
    return render_template('/harvest_aider/index.html')
    
@app.route('/harvest_aider/add_collector/')
def add_collector():
    district = code.get('AP')
    ind = list(range(1, len(district)+1))
    district_name = list(zip(ind, district))

    return render_template('/harvest_aider/add_collector.html', state=list(zip(state.values(), state.keys())), district_name=district_name)
    
@app.route('/harvest_aider/add_collector/<state>')
def city(state):
    print(state)
    district = code.get(state)
    ind = list(range(1, len(district)+1))
    district_name = list(zip(ind, district))
    
    cityArray = []

    for city in district_name:
        cityObj = {}
        cityObj['id'] = city[0]
        cityObj['name'] = city[1]
        cityArray.append(cityObj)

    return json.dumps({'cities' : cityArray})

@app.route('/harvest_aider/job_schedule/')    
def show_job_schedule():
    jobs = Job_List.query.filter((Job_List.collector_id != 'Not assigned') | (Job_List.job_complete == 0))
    return render_template('/harvest_aider/job_schedule.html', joblist=jobs)

@app.route('/harvest_aider/gen_user_id/')
def gen_user_id():
    
    
if __name__ == '__main__':
    app.run(debug=True)