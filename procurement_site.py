import os
import json
import datetime
from flask import send_from_directory
from flask import Flask, render_template, url_for, redirect
from flask_migrate import Migrate
from models import app, db
from models import Job_List, Request_user_id, Stalk_Collector, Harvest_Equipment
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

@app.route('/harvest_aider/')
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
    requests = Request_user_id.query.filter_by(req_complete = 0)
    return render_template('/harvest_aider/gen_user_id.html', requestlist=requests)

@app.route('/harvest_aider/allocate/')
def allocate_collector():
    list_farmer = Job_List.query.filter(Job_List.collector_id == None)
    list_collector = Stalk_Collector.query.filter(Stalk_Collector.hours_completed_today < 10)
    list_eqiup = Harvest_Equipment.query.filter(Harvest_Equipment.hours_completed_today < 10)
    for farmer in list_farmer:
        i = 0
        while (list_collector[i].hours_completed_today + farmer.expected_duration > 10) and (i < list_collector.count()):
            i += 1
        if i < list_collector.count():
            j = 0
            while (list_eqiup[j].hours_completed_today + farmer.expected_duration > 10) and (j < list_eqiup.count()):
                j += 1
            if j < list_eqiup.count():
                farmer.collector_id = list_collector[i].collector_id
                farmer.equip_id = list_eqiup[j].equip_id
                list_collector[i].hours_completed_today += farmer.expected_duration
                list_eqiup[j].hours_completed_today += farmer.expected_duration
    
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)