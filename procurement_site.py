import os
import json
import datetime
import schedule
import time

import flask
from flask import send_from_directory
from flask import Flask, render_template, url_for, redirect, request, session, g
from flask_migrate import Migrate

from werkzeug.security import check_password_hash
import models
from models import app, db
from models import Job_List, Request_user_id, Stalk_Collector, Harvest_Equipment, Farmer, Patwari, Gram_Panchayat, Harvest_Aider

from state_district import code, state
from id_count import FA, SC, HA, EQ, PW, JC, GP

Migrate(app, db)
now = datetime.datetime.now()

# to generate hashed passwords for inserting into the database

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

#generate new id
def gen_new_id(state, district_no, type, id_number):
    #For example: MH06J000023
    new_id = state+str(district_no).zfill(2)+type+str(id_number).zfill(6)
    return new_id

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user', None)
        user = request.form['username']
        user_type = user[4]
        #Checking if the user is a patwari
        if user_type == 'P':
            db_pass = Patwari.query.filter_by(patwari_id=user).first()
            if check_password_hash(db_pass.password_hash,request.form['password']):
                session['user'] = user
                return redirect(url_for('farmer_list'))
        
        #Checking if the user is a stalk collector
        elif user_type == 'S':
            db_pass = Stalk_Collector.query.filter_by(collector_id=user).first()
            if check_password_hash(db_pass.password_hash,request.form['password']):
                session['user'] = user
                session['username'] = db_pass.collector_name

                return redirect(url_for('stalk'))            

        #Checking if the user is a gram panchyat member
        #update the redirect url
        elif user_type == 'G':
            db_pass = Gram_Panchayat.query.filter_by(username=user).first()
            if check_password_hash(db_pass.password_hash,request.form['password']):
                session['user'] = user
                session['username'] = user

            return redirect(url_for('farmer_list'))
    
        #Checking if the user is a harvest aider
        elif user_type == 'A':
            db_pass = Harvest_Aider.query.filter_by(aider_id=user).first()
            if check_password_hash(db_pass.password_hash,request.form['password']):
                session['user'] = user
                return redirect(url_for('harvest_aider'))
        
    return render_template('login.html')

@app.route('/logout/')
def logout():
    if g.user:
        session.pop('user', None)
        return redirect(url_for('login'))
    else:
        return render_template('404.html')

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

#Landing page for the patwari
@app.route('/patwari/')
def farmer_list():
    if g.user and g.user[4] == 'P':
        farmers = Farmer.query.filter((Farmer.district_name == 'Pune'), (Farmer.state == 'MH'))
        return render_template('/patwari/index.html', farmerlist=farmers)
    else:
        return render_template('404.html')

#Insertion of new farmer by the patwari
@app.route('/patwari/insert_farmer/', methods=['GET', 'POST'])
def insert_farmer():
    if g.user and g.user[4] == 'P':
        if request.method == 'POST':        
            #Generating a new id for the farmer
            new_id = gen_new_id(request.form['state'], request.form['district_name'], 'F', FA.get(request.form['state'])[int(request.form['district_name'])]+1 )
            #Inserting the farmer details into the database
            print(request.form['size'])
            new_farmer = Farmer(new_id, request.form['name'], request.form['size'], request.form['contact_no'], request.form['aadhar_no'], request.form['village_name'], code.get(request.form['state'])[int(request.form['district_name'])-1], request.form['state'])
            db.session.add(new_farmer)
            db.session.commit()

        district = code.get('AN')
        ind = list(range(1, len(district)+1))
        district_name = list(zip(ind, district))

        return render_template('/patwari/insert_farmer.html', state=list(zip(state.values(), state.keys())), district_name=district_name)
    else:
        return render_template('404.html')

#generating district list depending on the state
@app.route('/patwari/insert_farmer/<state>')
def city_farmer(state):
    return city(state)

#The landing page after signing in (harvest aider)
@app.route('/harvest_aider/')
def harvest_aider():
    if g.user and g.user[4] == 'A':
        return render_template('/harvest_aider/index.html')
    else:
        return render_template('404.html')

#New collectors added by the harvest aider    
@app.route('/harvest_aider/add_collector/', methods=['GET', 'POST'])
def add_collector():
    if g.user and g.user[4] == 'A':
        if request.method == 'POST':        
            #Generating a new id for the stalk collector
            new_id = gen_new_id(request.form['state'], request.form['district_name'], 'S', SC.get(request.form['state'])[int(request.form['district_name'])]+1 )
            #Inserting the stalk collector details into the database
            new_collector = Stalk_Collector(new_id, 'pass', request.form['name'], code.get(request.form['state'])[int(request.form['district_name'])-1], request.form['state'], request.form['contact_no'])
            db.session.add(new_collector)
            db.session.commit()
            
        district = code.get('AN')
        ind = list(range(1, len(district)+1))
        district_name = list(zip(ind, district))

        return render_template('/harvest_aider/add_collector.html', state=list(zip(state.values(), state.keys())), district_name=district_name)
    else:
        return render_template('404.html')
    
#generating district list depending on the state
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

@app.route('/harvest_aider/gen_user_id/')
def gen_user_id():
    if g.user and g.user[4] == 'A':
        requests = Request_user_id.query.filter_by(req_complete = 0)
        return render_template('/harvest_aider/gen_user_id.html', requestlist=requests)
    else:
        return render_template('404.html')

#Allocating collectors and equipments to the farmers
#########################################################Add the time parameter
@app.route('/harvest_aider/allocate/')
def allocate_collector():
    if g.user and g.user[4] == 'A':
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
    else:
        return render_template('404.html')

# this is for the gram panchayat module, i made it a while ago, not for stalk collector    
@app.route('/gram_panchayat/add_request/', methods=['GET', 'POST'])
def request_generator():
    if g.user and g.user[4] == 'G':
        farmers = Farmer.query.filter_by(request_harvest = 0).all()
        if flask.request.method == 'POST':
            returned_values = request.form.getlist('request')
            for i in returned_values:
                print(i)
                val = Farmer.query.filter_by(farmer_id  = i).all()
                for v in val:
                    v.request_harvest = 1
                    j_id = v.state+v.farmer_id
                    exp_dur = (v.farm_size/1.5)+((v.farm_size/1.5)/4)
                    job = Job_List(j_id, v.farmer_id, '1', v.village_name, v.farm_size, 0, exp_dur)
                    db.session.add(job)
                    db.session.commit()
        farmers = Farmer.query.filter_by(request_harvest = 0).all()       
        return render_template('/gram_panchayat/add_req.html/', data=farmers)
    else:
        return render_template('404.html')

@app.route('/stalk_collector/joblist/', methods=['GET','POST'])
def stalk():
    if g.user and g.user[4] == 'S':
        if flask.request.method == 'POST':
            j_id = request.form.getlist('j_no')
            no_bales = request.form.getlist('bales')
            for j, b in zip(j_id, no_bales):
                print("job no:", j)
                print("no of bales: ", b)
                jlist = Job_List.query.filter_by(job_no = j).all()
                for l in jlist:
                    l.bales_collected = b
                    l.fees = (l.farm_size*400)
                    db.session.commit()
        jl=Job_List.query.filter_by(collector_id=session['user'], date_job = now.strftime('%y/%m/%d')).all()
        if len(jl) != 0:
            return render_template('/stalk_collector/stalk_collector.html', data=jl)
        return render_template('/stalk_collector/stalk_collector.html', data=0)
    else:
        return render_template('404.html')

@app.route('/stalk_collector/datewise_joblist/', methods=['GET', 'POST'])
def date_schedule():
    if g.user and g.user[4] == 'S':
        if flask.request.method == 'POST':
            date = request.form['date']
            datewise=Job_List.query.filter_by(collector_id=session['user'], date_job = date).all()
            return render_template('/stalk_collector/datewise.html', data=datewise) 
        return render_template('/stalk_collector/datewise.html')
    else:
        return render_template('404.html')  

@app.route('/stalk_collector/finjobs/', methods=['GET', 'POST'])
def job_comp():
    if g.user and g.user[4] == 'S':
        if flask.request.method == 'POST':
            jobs = request.form.getlist('j')
            for j in jobs:
                jlist = Job_List.query.filter_by(job_no = j).all()
                for l in jlist:
                    l.job_complete = 1
                    print('l.job_complete')
                    db.session.commit()
        return redirect('/stalk_collector/stalkcol')
    else:
        return render_template('404.html')
        
if __name__ == '__main__':
    app.run(debug=True)