#for setting up the database
#from models import db
#db.create_all()

#set migrations (save changes made to database)
#export FLASK_APP=procurement.py
#First time
##flask db init
#All other times
## flask db migrate -m "some message"
## flask db upgrade

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://Smoke:smoke_cva123@localhost/cva'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Farmer(db.Model):

    __tablename__ = 'farmer'

    farmer_id = db.Column(db.String(20), primary_key = True)
    farmer_name = db.Column(db.String(40))
    farm_size = db.Column(db.Integer)
    contact_no = db.Column(db.String(10))
    adhaar = db.Column(db.String(12))
    village_name = db.Column(db.String(20))
    district_name = db.Column(db.String(25))
    state = db.Column(db.String(2))

    def __init__(self, farmer_id, farmer_name, farm_size, contact_no, adhaar, village_name, district_name, state):
        self.farmer_id = farmer_id
        self.farmer_name = farmer_name
        self.farm_size = farm_size
        self.contact_no = contact_no
        self.adhaar = adhaar
        self.village_name = village_name
        self.district_name = district_name
        self.state = state

    def __repr__(self):
        print (f"Farmer id {self.farmer_id}, Farmer name {self.farmer_name}")

class Harvest_Equipment(db.Model):

    __tablename__ = 'harvest_equipment'

    equip_id = db.Column(db.String(20), primary_key=True)
    name_equip = db.Column(db.String(30))
    type_equip = db.Column(db.String(20))
    manufac_cmp = db.Column(db.String(30))
    year_of_purchase = db.Column(db.Integer)
    last_servicing = db.Column(db.Date)
    next_servicing = db.Column(db.Date)
    servicing_comp = db.Column(db.String(25))
    contact_person = db.Column(db.String(40))
    contact_number = db.Column(db.String(10))

    def __init__(self, equip_id, name_equip, type_equip, manufac_cmp, year_of_purchase, last_servicing, next_servicing, servicing_comp, contact_person, contact_number):
        self.equip_id = equip_id
        self.name_equip = name_equip
        self.type_equip = type_equip
        self.manufac_cmp = manufac_cmp
        self.year_of_purchase = year_of_purchase
        self.last_servicing = last_servicing
        self.next_servicing = next_servicing
        self.servicing_comp = servicing_comp
        self.contact_person = contact_person
        self.contact_number = contact_number

class Stalk_Collector(db.Model):

    __tablename__= 'stalk_collector'

    collector_id = db.Column(db.String(20), primary_key=True)
    collector_name = db.Column(db.String(40))
    contact_no = db.Column(db.String(10))
    hours_of_work = db.Column(db.Integer, default=0)

    def __init__(self, collector_id, collector_name, contact_no, hours_of_work):
        self.collector_id = collector_id
        self.collector_name = collector_name
        self.contact_no = contact_no
        self.hours_of_work = hours_of_work

class Gram_Panchayat(db.Model):

    __tablename__ = 'gram_panchayat'

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(256))
    name = db.Column(db.String(30))
    contact_no = db.Column(db.String(10))
    email_id = db.Column(db.String(50))
    village_name = db.Column(db.String(20))
    district_name = db.Column(db.String(25))
    state = db.Column(db.String(2))

    def __init__(self, username, password, name, contact_no, email_id, village_name, district_name, state):
        self.username = username
        self.password = password
        self.name = name
        self.contact_no = contact_no
        self.email_id = email_id
        self.village_name = village_name
        self.district_name = district_name
        self.state = state

class Request_Harvest(db.Model):
    
    __tablename__ = 'request_harvest'

    request_id = db.Column(db.Integer, primary_key=True)
    requestor_id = db.Column(db.String(20), db.ForeignKey('gram_panchayat.username'))
    req_gen = db.relationship('Gram_Panchayat', backref='request_harvest', uselist=False, foreign_keys=['requestor_id'])
    no_farmers = db.Column(db.Integer)
    date_request = db.Column(db.Date)
    jobs_completed = db.Column(db.Integer, default = 0)

    def __init__(self, requestor_id, no_farmers, date_request):
        self.request_id = requestor_id
        self.requestor_id = requestor_id
        self.no_farmers = no_farmers
        self.date_request = date_request

class Request_user_id(db.Model):

    __tablename__ = 'request_user_id'

    new_user_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    req_gen_id = db.Column(db.String(20), db.ForeignKey('gram_panchayat.username'))
    req_gen = db.relationship('Gram_Panchayat', backref='request_user_id', uselist=False, foreign_keys=['req_gen_id'])
    no_gen = db.Column(db.Integer)

    def __init__(self, new_user_id, date, req_gen_id, no_gen):
        self.new_user_id = new_user_id
        self.date = date
        self.req_gen_id = req_gen_id
        self.no_gen = no_gen

class Factory_Stalk_Collection(db.Model):

    __tablename__ = 'factory_stalk_collection'

    request_id = db.Column(db.Integer, primary_key=True)
    date_request = db.Column(db.Date)
    date_fulfilment = db.Column(db.Date)
    bails_stalk = db.Column(db.Integer)
    no_trucks = db.Column(db.Integer)
    amt_received = db.Column(db.Integer)

    def __init__(self, request_id, date_request, bails_stalk, no_trucks):
        self.request_id = request_id
        self.date_request = date_request
        self.bails_stalk = bails_stalk
        self.no_trucks = no_trucks

class Harvest_Aider(db.Model):

    __tablename__ = 'harvest_aider'

    aider_id = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(270))
    name = db.Column(db.String(40))
    contact_no = db.Column(db.String(10))
    district = db.Column(db.String(20))
    state = db.Column(db.String(2))
    no_villages = db.Column(db.Integer)

    def __init__(self, aider_id, password, name, contact_no, district, state, no_villages):
        self.aider_id = aider_id
        self.password = password
        self.name = name
        self.contact_no = contact_no
        self.district = district
        self.state = state
        self.no_villages = no_villages

class Job_List(db.Model):
    
    __tablename__='job_list'

    job_no = db.Column(db.String(15), primary_key=True)
    date_job = db.Column(db.Date)
    time = db.Column(db.Time)
    collector_id = db.Column(db.String(20), db.ForeignKey('stalk_collector.collector_id'))
    collector = db.relationship('Stalk_Collector', backref='job_list', uselist=False, foreign_keys=[collector_id])
    equip_id = db.Column(db.String(20), db.ForeignKey('harvest_equipment.equip_id'))
    equip = db.relationship('Harvest_Equipment', backref='job_list', uselist=False, foreign_keys=[equip_id])
    farmer_id = db.Column(db.String(20), db.ForeignKey('farmer.farmer_id'))
    farmer = db.relationship('Farmer', backref='job_list', uselist=False, foreign_keys=[farmer_id])
    request_id = db.Column(db.Integer, db.ForeignKey('request_harvest.request_id'))
    request = db.relationship('Request_Harvest', backref='job_list', uselist=False, foreign_keys=[request_id])
    location = db.Column(db.String(250))
    farm_size= db.Column(db.Integer)
    fees = db.Column(db.Integer)
    expected_duration = db.Column(db.Float)
    bails_collected = db.Column(db.Integer)
    job_complete = db.Column(db.Integer)

    def __init__(self, job_no, farmer_id, request_id, location, farm_size, fees, expected_duration):
        self.job_no = job_no
        self.farmer_id = farmer_id
        self.request_id = request_id
        self.location = location
        self.farm_size = farm_size
        self.fees = fees
        self.expected_duration = expected_duration
