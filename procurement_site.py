import os
import json
import datetime
import schedule
import time
import flask
from flask import send_from_directory
from flask import Flask, render_template, url_for, redirect, request, session, g
from flask_migrate import Migrate

from werkzeug.security import generate_password_hash, check_password_hash
import models
from models import app, db
from models import Job_List, Request_user_id, Stalk_Collector, Harvest_Equipment, Farmer, Patwari, Gram_Panchayat, Harvest_Aider

from state_district import code, state
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
            print('P')
            db_pass = Patwari.query.filter_by(patwari_id=user).first()
            #if check_password_hash(db_pass, generate_password_hash(request.form['password'])):
            # if request.form['password'] == 'pass':
            session['user'] = user
            return redirect(url_for('farmer_list'))
        
        #Checking if the user is a stalk collector
        #update the redirect url
        elif user_type == 'S':
            print('S')
            db_pass = Stalk_Collector.query.filter_by(collector_id=user).first()
            # phash = generate_password_hash(request.form['password'])
            # print('dbhash:', db_pass.password_hash)
            # print('input password:', request.form['password'])
            # print('phash:', phash)
            # if check_password_hash(db_pass.password_hash,phash):
            # print('pwd correct')
            session['user'] = user
            return redirect(url_for('stalk'))
            # else:
                #  print('pwd wrong')

        #Checking if the user is a gram panchyat member
        #update the redirect url
        elif user_type == 'G':
            print('G')
            db_pass = Gram_Panchayat.query.filter_by(username=user).first()
            phash = generate_password_hash(request.form['password'])
            print('dbhash:', db_pass.password_hash)
            print('phash:', phash)
            # if check_password_hash(db_pass.password_hash, phash):
            session['user'] = user
            return redirect(url_for('farmer_list'))
    
        #Checking if the user is a harvest aider
        elif user_type == 'A':
            print('A')
            db_pass = Harvest_Aider.query.filter_by(aider_id=user).first()
            #if check_password_hash(db_pass, generate_password_hash(request.form['password'])):
            if request.form['password'] == 'pass':
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
        farmers = Farmer.query.filter((Farmer.district_name == 'Raipur'), (Farmer.state == 'CH'))
        return render_template('/patwari/index.html', farmerlist=farmers)
    else:
        return render_template('404.html')

#Insertion of new farmer by the patwari
@app.route('/patwari/insert_farmer/')
def insert_farmer():
    if g.user and g.user[4] == 'P':
        district = code.get('AP')
        ind = list(range(1, len(district)+1))
        district_name = list(zip(ind, district))
        if flask.request.method = "POST":
            # new = 
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
@app.route('/harvest_aider/add_collector/')
def add_collector():
    if g.user and g.user[4] == 'A':
        district = code.get('AP')
        ind = list(range(1, len(district)+1))
        district_name = list(zip(ind, district))
        return render_template('/harvest_aider/add_collector.html', state=list(zip(state.values(), state.keys())), district_name=district_name)
    else:
        return render_template('404.html')
    
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
    
@app.route('/addreq', methods=['GET', 'POST'])
def reqgen():
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
    return render_template('add_req.html', data=farmers)

@app.route('/stalkcol', methods=['GET','POST'])
def stalk():
    id = 'CH13S0025'
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
        jl=Job_List.query.filter_by(collector_id=id).all()
        if len(jl) != 0:   
            return render_template('/stalk_collector/stalk_collector.html', data=jl)
        return render_template('/stalk_collector/stalk_collector.html', data=0)

@app.route('/finjobs', methods=['GET', 'POST'])
def job_comp():
    if flask.request.method == 'POST':
        jobs = request.form.getlist('j')
        for j in jobs:
            jlist = Job_List.query.filter_by(job_no = j).all()
            for l in jlist:
                l.job_complete = 1
                print('l.job_complete')
                db.session.commit()
    return redirect('/stalkcol')     

@app.route('/genhash', methods=['GET', 'POST'])
def genhash():
    if flask.request.method == 'POST':
        pwd = request.form['pwd']
        print('inserted pwd: ', pwd)
        pas = generate_password_hash(pwd)
        print("len:", len(pas))
        return render_template("pwd.html", data=pas)
    return render_template("pwd.html", data=0)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
