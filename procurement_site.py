import os
import json
import datetime
from datetime import timedelta
import schedule
import time
import requests

import flask
from flask import send_from_directory, flash
from flask import Flask, render_template, url_for, redirect, request, session, g, make_response
from flask_migrate import Migrate
from fpdf import FPDF
from send_sms import url, headers, payload

from flask_mail import Mail, Message
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import check_password_hash, generate_password_hash

from models import app, db
from models import Job_List, Request_user_id, Stalk_Collector, Harvest_Equipment, Farmer, Patwari, Gram_Panchayat, Harvest_Aider, User_Id, Factory_Manager, Factory_Stalk_Collection, Bales_Collected, Request_Harvest
from gen_report import PDF
from send_sms import url, headers, payload
from state_district import code, state

mail = Mail(app)
Migrate(app, db)
now = datetime.datetime.now()
yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
amt_per_bales = 1.75

#send messages
def send_sms(msg, numbers):
    if len(numbers) > 1:
        number = ""
        for num in numbers:
            number += num 
            number += ','
    elif len(numbers) == 1:
        number = str(numbers)

    response = requests.request("POST", url, data=payload.format(msg,number), headers=headers)

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

#moving the unfinised jobs ahead to the next day
def update_unfinished_jobs():
    jl=Job_List.query.filter_by(date_job=str(yesterday.strftime('%Y-%m-%d')), job_complete=0).all()
    for job in jl:
        job.date_job = str(now.strftime('%Y-%m-%d'))
    db.session.commit()

#add the bales of stalk collected on that day to the bales_collected table
def update_bales_collected():
    jl = Job_List.query.filter_by(bales_collected > 0, date_job=str(now.strftime('%Y-%m-%d'))).all()
    bales = 0
    for job in jl:
        bales += job.bales_collected
    
    bales_add = Bales_Collected(str(now.strftime('%Y-%m-%d')), bales)
    db.session.add(bales_add)
    db.session.commit()

#generate new id
def gen_new_id(state, district_no, col_type):
    #For example: MH06J000023
    st_dis = state+str(district_no).zfill(2) 
    cnt = User_Id.query.filter_by(state_district=st_dis).first()    
    if cnt != None:
        if col_type == 'F':
            id_number = cnt.farmer_cnt+1
            cnt.farmer_cnt += 1
        elif col_type == 'S':
            id_number = cnt.stalk_collector_cnt+1
            cnt.stalk_collector_cnt += 1
        elif col_type == 'A':
            id_number = cnt.harvest_aider_cnt+1
            cnt.harvest_aider_cnt += 1
        elif col_type == 'E':
            id_number = cnt.harvest_equip_cnt+1
            cnt.harvest_equip_cnt += 1
        elif col_type == 'J':
            id_number = cnt.job_cnt+1
            cnt.job_cnt += 1
        elif col_type == 'P':
            id_number = cnt.patwari_cnt+1
            cnt.patwari_cnt += 1
        else:
            id_number = cnt.request_cnt+1
            cnt.request_cnt += 1
            db.session.commit()
            return id_number
        db.session.commit()

        new_id = st_dis+col_type+str(id_number+1).zfill(6)
    else:
        new_id = None
    return new_id

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET', 'POST'])
def login():
    if g.user:
        user_type = g.user[4]
        if user_type == 'P':
            return redirect(url_for('farmer_list'))
        elif user_type == 'S':
            return redirect(url_for('joblist')) 
        elif user_type == 'G':
            return redirect(url_for('request_generator'))
        elif user_type == 'A':
            return redirect(url_for('harvest_aider'))
        if user_type == 'M':
            return redirect(url_for('factory_manager'))
       
    if request.method == 'POST':
        session.pop('user', None)
        user = request.form['username']
        if len(user) < 5:
            flash('Incorrect login credentials!', 'error')   
            return render_template('login.html')
        user_type = user[4]

        #Checking if the user is a patwari
        if user_type == 'P':
            db_pass = Patwari.query.filter_by(patwari_id=user).first()
            pwd_hash = check_password_hash(db_pass.password_hash,request.form['password'])
            if pwd_hash == True:
                session['user'] = user
                session['username'] = db_pass.patwari_name
                session['state'] = db_pass.state
                session['district'] = db_pass.district_name
                flash('You were successfully logged in', 'success')
                return redirect(url_for('farmer_list'))
            else:
                flash('Incorrect login credentials!', 'error')    
        
        #Checking if the user is a stalk collector
        elif user_type == 'S':
            db_pass = Stalk_Collector.query.filter_by(collector_id=user).first()
            pwd_hash = check_password_hash(db_pass.password_hash,request.form['password'])
            if pwd_hash == True:
                session['user'] = user
                session['username'] = db_pass.collector_name
                session['state'] = db_pass.state
                session['district'] = db_pass.district_name
                return redirect(url_for('joblist'))  
            else:
                flash('Incorrect login credentials!', 'error')    
              

        #Checking if the user is a gram panchyat member
        elif user_type == 'G':
            db_pass = Gram_Panchayat.query.filter_by(username=user).first()
            pwd_hash = check_password_hash(db_pass.password_hash,request.form['password'])
            if pwd_hash == True:
                session['user'] = user
                session['username'] = user
                session['state'] = db_pass.state
                session['district'] = db_pass.district_name

                flash('You were successfully logged in', 'success')
            else:
                flash('Incorrect login credentials!', 'error')    

            return redirect(url_for('request_generator'))
    
        #Checking if the user is a harvest aider
        elif user_type == 'A':
            db_pass = Harvest_Aider.query.filter_by(aider_id=user).first()
            pwd_hash = check_password_hash(db_pass.password_hash,request.form['password'])
            if pwd_hash == True:
                session['user'] = user
                session['username'] = db_pass.name
                session['state'] = db_pass.state
                session['district'] = db_pass.district

                flash('You were successfully logged in', 'success')
                return redirect(url_for('harvest_aider'))
            else:
                flash('Incorrect login credentials!', 'error')    

        #Checking if the user is a factory manager
        elif user_type == 'M':
            db_pass = Factory_Manager.query.filter_by(username=user).first()
            pwd_hash = check_password_hash(db_pass.password_hash,request.form['password'])
            if pwd_hash == True:
                session['user'] = user
                session['username'] = db_pass.name
                session['state'] = db_pass.state
                session['district'] = db_pass.district_name

                flash('You were successfully logged in', 'success')
                return redirect(url_for('factory_manager')) 
            else:
                flash('Incorrect login credentials!', 'error')    

        else:               
            flash('Incorrect login credentials!', 'error')            
    return render_template('login.html')

def send_reset_email(uname, db_pass):
    token = db_pass.get_reset_token()
    session['token'] = token
    session['uname'] = uname
    msg = Message('Password Reset Request',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[db_pass.email_id])
    msg.html = render_template("email_format.html", uname=uname, token=token)                   
    mail.send(msg)
    
@app.route('/forgot_passwd/', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'GET':
        return render_template('forgot_passwd.html')

    uname = request.form['username']
    if(uname.len() < 4):
        flash('Incorrect Username!', 'error')
        return render_template('forgot_passwd.html')
    #if the user is a patwari
    if uname[4] == 'P':
        db_pass = Patwari.query.filter_by(patwari_id=uname).first()
            
    #if the user is a stalk collector
    elif uname[4] == 'S':
        db_pass = Stalk_Collector.query.filter_by(collector_id=uname).first()

    #if the user is a gram panchyat member
    elif uname[4] == 'G':
        db_pass = Gram_Panchayat.query.filter_by(username=uname).first()

    #if the user is a harvest aider
    elif uname[4] == 'A':
        db_pass = Harvest_Aider.query.filter_by(aider_id=uname).first()

    #if the user is a factory manager
    elif uname[4] == 'M':
        db_pass = Factory_Manager.query.filter_by(username=uname).first()

    if db_pass is None:
        flash('Incorrect Username, please try again', 'error')
        return render_template('forgot_passwd.html',)
    send_reset_email(uname, db_pass)
    # print("db_pass:", db_pass)
    flash('Email for password change has been sent', success)
    return redirect(url_for('login'))

@app.route('/forgot_passwd/reset/', methods=['GET','POST'])
def reset_token():
    uname = session.get('uname', None)
    token = session.get('token', None)
    if request.method == "POST":
    #if the user is a patwari
        if uname[4] == 'P':
            user = Patwari.verify_reset_token(token)
                
        #if the user is a stalk collector
        elif uname[4] == 'S':
            user = Stalk_Collector.verify_reset_token(token)

        #if the user is a gram panchyat member
        elif uname[4] == 'G':
            user = Gram_Panchayat.verify_reset_token(token)

        #if the user is a harvest aider
        elif uname[4] == 'A':
            user = Harvest_Aider.verify_reset_token(token)

        #if the user is a factory manager
        elif uname[4] == 'M':
            user = Factory_Manager.verify_reset_token(token)
        if user is None:
            flash('Sorry! your reset link has expired, please try again','warning')
            return redirect(url_for('reset_request'))
        hashed_password =  generate_password_hash(request.form['password'])
        user.password_hash = hashed_password
        db.session.commit()
        flash('Password changed successfully', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html')

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
        g.username = session['username']
        g.state = session['state']
        g.district = session['district']

#returns the district code 
def get_district_id(state, district):
    district_list = code.get(state)
    return (district_list.index(district)+1)

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
            new_id = gen_new_id(request.form['state'], request.form['district_name'], 'F')
            if new_id == None:
                return render_template('500.hmtl')
            #Inserting the farmer details into the database
            new_farmer = Farmer(new_id, request.form['name'], request.form['size'], request.form['contact_no'], request.form['aadhar_no'], request.form['village_name'], code.get(request.form['state'])[int(request.form['district_name'])-1], request.form['state'])
            db.session.add(new_farmer)
            db.session.commit()
            flash('Farmer details added succesfully!')
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
        print(session['username'])
        return render_template('/harvest_aider/index.html')
    else:
        return render_template('404.html')

#New collectors added by the harvest aider    
@app.route('/harvest_aider/add_collector/', methods=['GET', 'POST'])
def add_collector():
    if g.user and g.user[4] == 'A':
        if request.method == 'POST':        
            #Generating a new id for the stalk collector
            new_id = gen_new_id(request.form['state'], request.form['district_name'], 'S')
            if new_id == None:
                return render_template('500.html')
            #Inserting the stalk collector details into the database
            new_collector = Stalk_Collector(new_id, 'pass', request.form['name'], code.get(request.form['state'])[int(request.form['district_name'])-1], request.form['state'], request.form['contact_no'])
            db.session.add(new_collector)
            db.session.commit()
            flash('Stalk Collector information added succesfully!', 'success')
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

#shows the schedule to the harvest aider 
@app.route('/harvest_aider/job_schedule/')    
def show_job_schedule():
    if g.user and g.user[4] == 'A':
        jobs = Job_List.query.filter((Job_List.collector_id != 'Not assigned') | (Job_List.job_complete == 0))
        return render_template('/harvest_aider/job_schedule.html', joblist=jobs)

    else:
        return render_template('404.html')

# displays the list of requests for new member ids in the gram panchayat
@app.route('/harvest_aider/gen_user_id/')
def gen_user_id():
    if g.user and g.user[4] == 'A':
        requests = Request_user_id.query.filter_by(req_complete = 0)
        return render_template('/harvest_aider/gen_user_id.html', requestlist=requests)
    else:
        return render_template('404.html')

#Allocating collectors and equipments to the farmers
@app.route('/harvest_aider/allocate/', methods=['GET','POST'])
def allocating_collector():    
    if g.user and g.user[4] == 'A':
        if request.method == 'POST':
            if request.form['allocating'] == 'yes':
                start_time = datetime.timedelta(hours=9)
                state_district = g.user[0:4]
                list_farmer = Job_List.query.filter(Job_List.collector_id == None, Job_List.farmer_id.like('%'+state_district+'%'))
                list_collector = Stalk_Collector.query.filter(Stalk_Collector.hours_completed_today < 10, Stalk_Collector.collector_id.like('%'+state_district+'%'))
                for farmer in list_farmer:
                    i = 0
                    while (i < list_collector.count()) and (list_collector[i].hours_completed_today + farmer.expected_duration > 10) :
                        i += 1
                    if i < list_collector.count():        
                        farmer.date_job = now.strftime('%Y-%m-%d')
                        if list_collector[i].hours_completed_today != 0:
                            start_time = datetime.timedelta(hours=list_collector[i].hours_completed_today+9)
                        farmer.time = start_time
                        farmer.collector_id = list_collector[i].collector_id
                        farmer.equip_id = list_collector[i].equip_id
                        list_collector[i].hours_completed_today += farmer.expected_duration
                db.session.commit()
                flash('Allocation Successful!', 'success')
        return redirect(url_for('harvest_aider'))
    else:
        return render_template('404.html')

#Requesting the collection of stalk by the bioethanol production company
@app.route('/harvest_aider/collection_request/', methods=['GET', 'POST'])
def collection_request():
    if g.user and g.user[4] == 'A':
        if request.method == 'POST':
            date = request.form['date']
            bales = request.form['bales']
            new_req = Factory_Stalk_Collection(date, bales, g.district, g.district, g.state)
            db.session.add(new_req)
            db.session.commit()
            flash('Request sent successfully!', 'success')
            return redirect(url_for('harvest_aider'))
    else:
        return render_template('404.html')    

def gen_stalk_collector_list(duration):
    header = ['Collector Id', 'Collector Name', 'Contact Number', 'Employed_Date']
    gen_by = [g.user, g.username]
    # Add the date parameter
    result = Stalk_Collector.query.filter_by(Stalk_Collector.employed_date >= duration[0], Stalk_Collector.employed_date <= duration[1]).all()
    data = []
    for res in result:
        data.append(list([res.collector_id, res.collector_name, res.contact_no, res.employed_date]))
    if len(data):
        pdf = PDF()
        pdf.add_page()
        pdf.set_title('ETHANOWELL')
        pdf.report_title('Stalk Collector List')
        pdf.report_desc(duration, gen_by)
        pdf.table(header, data)
        pdf.output("Stalk_Collector_List"+str(now)+".pdf", 'F')
        return "success"
    else:
        return "failure"

def gen_equip_list(duration):
    header = ['Equipment Id', 'Equip. Name', 'Equip. Type', 'Last Servicing', 'Next Servicing']
    gen_by = [session['user'], session['username']]
    result = Harvest_Equipment.query.filter(Harvest_Equipment.next_servicing >= duration[0], Harvest_Equipment.next_servicing <= duration[1]).all()
    data = []
    for res in result:
        data.append(list([res.equip_id, res.name_equip, res.type_equip, res.last_servicing, res.next_servicing]))
    if len(data):
        pdf = PDF()
        pdf.add_page()
        pdf.set_title('ETHANOWELL')
        pdf.report_title('Equipment List')
        pdf.report_desc(duration, gen_by)
        pdf.table(header, data)
        pdf.output("Equipment_List"+str(now)+".pdf", 'F')
        return "success"
    else:
        return "failure"

def gen_job_list(duration):
    header = ['Job Id', 'Stalk Collector', 'Farmer', 'Date', 'Status', 'Bales Collected']
    gen_by = [g.user,g.username] 
    result = db.session.query(Job_List,Stalk_Collector, Farmer).filter_by(collector_id = Stalk_Collector.collector_id).filter_by(farmer_id = Farmer.farmer_id).filter(db.between(Job_List.date_job, duration[0], duration[1])).all()
    print(result[0].Job_List.job_no)
    data = []
    for res in result:
        data.append(list([res.Job_List.job_no,res.Stalk_Collector.collector_name, res.Farmer.farmer_name, res.Job_List.date_job, res.Job_List.job_complete, res.Job_List.bales_collected]))
    if len(data):
        pdf = PDF()
        pdf.add_page()
        pdf.set_title('ETHANOWELL')
        pdf.report_title('Job List')
        pdf.report_desc(duration, gen_by)
        pdf.table(header, data)
        pdf.output("Job_List"+str(now)+".pdf", 'F')
        return "success"
    else:
        return "failure"

def gen_bales_collected_list(duration):
    header = ['Date', 'Bales Collected', 'Sent to Factory On']
    gen_by = [session['user'], session['username']]    
    result = Bales_Collected.query.filter(Bales_Collected.sent_date >= duration[0], Bales_Collected.sent_date <= duration[1]).all()
    data = []
    for res in result:
        data.append(list([res.collection_date, res.collected_bales, res.sent_date]))
    if len(data):
        pdf = PDF()
        pdf.add_page()
        pdf.set_title('ETHANOWELL')
        pdf.report_title('Bales Collection List')
        pdf.report_desc(duration, gen_by)
        pdf.table(header, data)
        pdf.output("Bales_Collection_List"+str(now)+".pdf", 'F')
        return "success"
    else:
        return "failure"

def gen_id_req_list(duration):
    header = ['Date', 'Requesting Id', 'Number Requested']
    gen_by = [session['user'], session['username']]
    result = Request_user_id.query.filter(Request_user_id.date >= duration[0], Request_user_id.date <= duration[1]).all()
    data = []
    for res in result:
        data.append(list([res.date, res.request_gen_id, res.no_gen]))
    if len(data):
        pdf = PDF()
        pdf.add_page()
        pdf.set_title('ETHANOWELL')
        pdf.report_title('Bales Collection List')
        pdf.report_desc(duration, gen_by)
        pdf.table(header, data)
        pdf.output("Bales_Collection_List"+str(now)+".pdf", 'F')
        return "success"
    else:
        return "failure"

def gen_truck_req_list(duration):
    header = ['Date of request', 'Bales', 'Date of fulfilment', 'No. Trucks']
    gen_by = [session['user'], session['username']]
    result = Factory_Stalk_Collection.query.filter(Factory_Stalk_Collection.date_request >= duration[0],Factory_Stalk_Collection.date_request <= duration[1]).all()
    data = []
    for res in result:
        data.append(list([res.date_request, res.bales_stalk, res.date_fulfilment, res.no_trucks]))
    if len(data):
        pdf = PDF()
        pdf.add_page()
        pdf.set_title('ETHANOWELL')
        pdf.report_title('Bales Collection List')
        pdf.report_desc(duration, gen_by)
        pdf.table(header, data)
        pdf.output("Truck_Request_List"+str(now)+".pdf", 'F')
        return "success"
    else:
        return "failure"

@app.route('/harvest_aider/reports/', methods=['GET', 'POST'])
def gen_report():
    if g.user and g.user[4] == 'A':
        if request.method == 'POST':
            report_type = request.form['report_type']
            duration = [request.form['start_date'], request.form['end_date']]
            switcher = {
                "0": gen_stalk_collector_list,
                "1": gen_equip_list,
                "2": gen_job_list,
                "3": gen_bales_collected_list,
                "4": gen_id_req_list,
                "5": gen_truck_req_list
            }

            result = switcher.get(str(report_type), "failure")(duration)
            if result == "success":
                flash('Report generated successfully',result)
            else:
                flash('Report not generated due to lack of data', result)
        return render_template('reports/index.html')
    else:
        return render_template('404.html')

#Generate reports
@app.route('/harvest_aider/reports/job_list<date>.pdf/')
# def job_list_report(date):
#     if g.user and g.user[4] == 'A':
#         jobs = Job_List.query.filter((Job_List.collector_id != 'Not assigned') | (Job_List.job_complete == 0))
#         html = render_template('/reports/job_list.html', joblist=jobs)
#         return render_pdf(HTML(string=html))
#     else:
#         return render_template('404.html')

def pdf_report(date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Hello World!')
    # return pdf.output('tuto1.pdf', 'F')
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers.set('Content-Disposition', 'attachment', filename='report'+date+ '.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response


# Request for harvesting by people employed in the Gram Panchanyat
@app.route('/gram_panchayat/add_request/', methods=['GET', 'POST'])
def request_generator():
    if g.user and g.user[4] == 'G':
        gp = Gram_Panchayat.query.filter_by(username=g.user).first()
        if flask.request.method == 'POST':
            returned_values = request.form.getlist('request')
            request_id = gen_new_id(gp.state, get_district_id(gp.state, gp.district_name), 'R')
            print(request_id)
            requesting_harvest = Request_Harvest(request_id,g.user,len(returned_values),str(now.strftime("%Y-%m-%d %H:%M:%S")))
            db.session.add(requesting_harvest)

            for i in returned_values:
                val = Farmer.query.filter_by(farmer_id=i).all()
                for v in val:
                    v.request_harvest = 1
                    #generating the job id
                    j_id = gen_new_id(v.state, get_district_id(v.state, v.district_name), 'J')
                    print(j_id)
                    #calculating the job's expected duration
                    exp_dur = (v.farm_size/1.5)+((v.farm_size/1.5)/4)
                    farm_size = v.farm_size
                    #if duration is more than the 10
                    if exp_dur > 10:
                        job = Job_List(j_id, v.farmer_id, request_id, v.village_name, 12, 0, 10)
                        exp_dur -= 10
                        farm_size -= 12
                        j_id = gen_new_id(v.state, get_district_id(v.state, v.district_name), 'J')

                    job = Job_List(j_id, v.farmer_id, request_id, v.village_name, farm_size, 0, exp_dur)
                    db.session.add(job)
                    db.session.commit()
            flash('Update Successful!', "success")
        farmers = Farmer.query.filter_by(request_harvest=0, district_name=gp.district_name, state=gp.state).all()
        
        return render_template('/gram_panchayat/add_req.html/', data=farmers, count=len(farmers))
    else:
        return render_template('404.html')

@app.route('/stalk_collector/joblist/', methods=['GET','POST'])
def joblist():
    if g.user and g.user[4] == 'S':
        if flask.request.method == 'POST':
            j_id = request.form.getlist('j_no')
            no_bales = request.form.getlist('bales')
            for j, b in zip(j_id, no_bales):
                jlist = Job_List.query.filter_by(job_no=j).all()
                for l in jlist:
                    l.bales_collected = b
                    l.fees = int(b)*20*amt_per_bales
                    db.session.commit()
                    flash('Update Successful!', 'success')
        # print(now.strftime('%Y/%m/%d'))
        jl=Job_List.query.filter_by(collector_id=g.user, date_job=str(now.strftime('%Y-%m-%d'))).all()
        # print(jl[0].collector_id)
        for job in jl:
            job.date_job = datetime.datetime.strptime(str(job.date_job), '%Y-%m-%d').strftime('%d/%m/%Y')
            job.time = datetime.datetime.strptime(str(job.time), "%H:%M:%S").strftime("%I:%M %p")

        if len(jl) != 0:
            return render_template('/stalk_collector/index.html', data=jl)
        
        flash('No jobs for today!')
        return render_template('/stalk_collector/index.html', data=0)
    else:
        return render_template('404.html')

@app.route('/stalk_collector/datewise_joblist/', methods=['GET', 'POST'])
def date_schedule():
    if g.user and g.user[4] == 'S':
        if flask.request.method == 'POST':
            date = request.form['date']
            datewise=Job_List.query.filter_by(collector_id=g.user, date_job = date).all()
            for job in datewise:
                job.date_job = datetime.datetime.strptime(str(job.date_job), '%Y-%m-%d').strftime('%d/%m/%Y')
            job.time = datetime.datetime.strptime(str(job.time), "%H:%M:%S").strftime("%I:%M %p")
            return render_template('/stalk_collector/datewise.html', data=datewise) 
        return render_template('/stalk_collector/datewise.html')
    else:
        return render_template('404.html')  

#Update list to complete jobs
@app.route('/stalk_collector/finjobs/', methods=['GET', 'POST'])
def job_comp():
    if g.user and g.user[4] == 'S':
        if flask.request.method == 'POST':
            jobs = request.form.getlist('j')
            for j in jobs:
                jlist = Job_List.query.filter_by(job_no = j).all()
                for l in jlist:
                    l.job_complete = 1
                    db.session.commit()
        flash('Update Successful!', success)            
        return redirect('/stalk_collector/joblist')
    else:
        return render_template('404.html') 
@app.route('/harvest_aider/mainenance/insert', methods=['GET','POST'])
def insert():
    from_date = str(now.strftime('%Y-%m-%d'))
    duration = datetime.timedelta(days=3)
    to_date = str((datetime.datetime.today() + duration).date())
    if flask.request.method == "POST":
        inserted_equipments = request.form.getlist("inserted")
        specific_equip = request.form['specific_equip']
        if inserted_equipments: 
            for i in inserted_equipments:
                print(i)
                equip = Harvest_Equipment.query.filter_by(equip_id=i).first()
                equip.available = 0
                equip.last_servicing = from_date
            db.session.commit()
            flash('equipment inserted successfully', 'success')    

        elif specific_equip:    
            s_equip = Harvest_Equipment.query.filter_by(equip_id=specific_equip).first()
            s_equip.available = 0
            s_equip.last_servicing = from_date
            flash('equipment inserted successfully', 'success')    
            return render_template('/harvest_aider/equipment_insert.html',specific_equip=s_equip, flag=0)

    equipments = Harvest_Equipment.query.filter(Harvest_Equipment.available == 1, db.between(Harvest_Equipment.next_servicing, from_date, to_date),Harvest_Equipment.state==session['state'], Harvest_Equipment.district==session['district']).all()
    return render_template('/harvest_aider/equipment_insert.html', equipments=equipments, flag=1)

@app.route('/harvest_aider/maintenance/retieve', methods=['GET', 'POST'])
def retrieve():
    if flask.request.method == "POST":
        retrieved_equipments = request.form.getlist("retrieved")
        for r in retrieved_equipments:
            retr = Harvest_Equipment.query.filter_by(equip_id=r).first()
            retr.available = 1
            duration = datetime.timedelta(days=90)
            to_date = (datetime.datetime.today() + duration).date()
            retr.next_servicing = to_date
        db.session.commit()  
        flash('Equipment retrieved successfully!','success')      
    equipments= Harvest_Equipment.query.filter(Harvest_Equipment.available==0, Harvest_Equipment.state==session['state'], Harvest_Equipment.district==session['district']).all()  
    return render_template('/harvest_aider/equipment_retrieve.html', equipments = equipments)

# def send_mail_for_service():

@app.route('/factory_manager/')
def factory_manager():
    if g.user and g.user[4] == 'M':
        complete_list = Factory_Stalk_Collection.query.filter_by(date_fulfilment=None)
        return render_template('/factory_manager/index.html', c_list=complete_list)
    else:
        return render_template('404.html')

@app.route('/factory_manager/report_generation/',methods=['GET', 'POST'])
def report_generation():
    if g.user and g.user[4] == 'M':
        return render_template('/factory_manager/report_generation.html')
    else:
        return render_template('404.html')

@app.route('/factory_manager/todays_collection/',methods=['GET', 'POST'])
def todays_report():
    if g.user and g.user[4] == 'M':
        todays_list = Factory_Stalk_Collection.query.filter_by(date_fulfilment=now.strftime("%Y/%m/%d"))
        # print(todays_list[0])
        return render_template('/factory_manager/todays_collection.html', t_list=todays_list)
    else:
        return render_template('404.html')

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000)