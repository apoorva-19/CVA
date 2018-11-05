import os
import json
import datetime
import schedule
import time

from flask import send_from_directory
from flask import Flask, render_template, url_for, redirect

from flask_migrate import Migrate

from models import app, db
from models import Job_List, Request_user_id, Stalk_Collector, Harvest_Equipment, Farmer

from state_district import code, state

Migrate(app, db)

now = datetime.datetime.now()

#setting the hours completed to zero to allocate collectors and harvestors for the next day
def set_completed_hours():
    list_collector = Stalk_Collector.query.all()
    list_equipment = Harvest_Equipment.query.all()
    for collector in list_collector:
        collector.hours_of_work += collector.hours_completed_today
        collector.hours_completed_today = 0
    for equip in list_equipment:
        equip.hours_completed_today = 0
    
    db.session.commit()

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

#Landing page for the patwari
@app.route('/patwari/')
def farmer_list():
    farmers = Farmer.query.filter((Farmer.district_name == 'Raipur'), (Farmer.state == 'CH'))
    return render_template('/patwari/index.html', farmerlist=farmers)

#Insertion of new farmer by the patwari
@app.route('/patwari/insert_farmer/')
def insert_farmer():
    district = code.get('AP')
    ind = list(range(1, len(district)+1))
    district_name = list(zip(ind, district))

    return render_template('/patwari/insert_farmer.html', state=list(zip(state.values(), state.keys())), district_name=district_name)

#generating district list depending on the state
@app.route('/patwari/insert_farmer/<state>')
def city_farmer(state):
    return city(state)

#The landing page after signing in (harvest aider)
@app.route('/harvest_aider/')
def harvest_aider():
    return render_template('/harvest_aider/index.html')

#New collectors added by the harvest aider    
@app.route('/harvest_aider/add_collector/')
def add_collector():
    district = code.get('AP')
    ind = list(range(1, len(district)+1))
    district_name = list(zip(ind, district))

    return render_template('/harvest_aider/add_collector.html', state=list(zip(state.values(), state.keys())), district_name=district_name)
    
#generating district list depending on the state
@app.route('/harvest_aider/add_collector/<state>')
def city(state):
    district = code.get(state)
    print(district)
    ind = list(range(1, len(district)+1))
    district_name = list(zip(ind, district))
    
    cityArray = []

    for city in district_name:
        cityObj = {}
        cityObj['id'] = city[0]
        cityObj['name'] = city[1]
        cityArray.append(cityObj)

    return json.dumps({'cities' : cityArray})

#Displaying the list of the jobs scheduled
@app.route('/harvest_aider/job_schedule/')    
def show_job_schedule():
    jobs = Job_List.query.filter((Job_List.collector_id != 'Not assigned') | (Job_List.job_complete == 0))
    return render_template('/harvest_aider/job_schedule.html', joblist=jobs)

#Displaying the list of requests for new user ids.
@app.route('/harvest_aider/gen_user_id/')
def gen_user_id():
    requests = Request_user_id.query.filter_by(req_complete = 0)
    return render_template('/harvest_aider/gen_user_id.html', requestlist=requests)

#Allocating collectors and equipments to the farmers
#########################################################Add the time parameter
@app.route('/harvest_aider/allocate/')
def allocate_collector():
    list_farmer = Job_List.query.filter(Job_List.collector_id == None)
    list_collector = Stalk_Collector.query.filter(Stalk_Collector.hours_completed_today < 10)
    list_eqiup = Harvest_Equipment.query.filter(Harvest_Equipment.hours_completed_today < 10)
    for farmer in list_farmer:
        i = 0
        while (i < list_collector.count()) and (list_collector[i].hours_completed_today + farmer.expected_duration > 10) :
            print(i)
            i += 1
        print(i)
        print(list_collector.count())
        if i < list_collector.count():
            j = 0
            while (j < list_eqiup.count()) and (list_eqiup[j].hours_completed_today + farmer.expected_duration > 10):
                j += 1
            if j < list_eqiup.count():
                farmer.date_job = now.strftime('%d/%m/%y')
                farmer.collector_id = list_collector[i].collector_id
                farmer.equip_id = list_eqiup[j].equip_id
                list_collector[i].hours_completed_today += farmer.expected_duration
                list_eqiup[j].hours_completed_today += farmer.expected_duration

    db.session.commit()

if __name__ == '__main__':
    #Scheduling the setting of hours completed at mid night
    schedule.every().day.do(app.run(debug=True))
    schedule.every().day.at("18:38").do(set_completed_hours)
    while True:
        schedule.run_pending()
        time.sleep(1)
    # app.run(debug=True)