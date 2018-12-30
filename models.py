#for setting up the database
#from models import db
#db.create_all()

#set migrations (save changes made to database)
#export FLASK_APP=procurement_site.py
#First time
##flask db init
#All other times
## flask db migrate -m "some message"
## flask db upgrade

import os
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from werkzeug.security import generate_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ethanowell.cva@gmail.com'
app.config['MAIL_PASSWORD'] = 'jfcouhooblgqvqsy'

db = SQLAlchemy(app)

class Patwari(db.Model):

    __tablename__ = 'patwari'

    patwari_id = db.Column(db.String(20), primary_key = True)
    password_hash = db.Column(db.String(128))
    patwari_name = db.Column(db.String(40))
    district_name = db.Column(db.String(20))
    state = db.Column(db.String(2))
    contact_no = db.Column(db.String(10), unique=True, index=True)
    email_id = db.Column(db.String(64), unique=True, index=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.patwari_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Patwari.query.get(user_id)

    def __init__(self, patwari_id, password, patwari_name, district_name, state, contact_no, email_id):
        self.patwari_id = patwari_id
        self.password_hash = generate_password_hash(password)
        self.patwari_name = patwari_name
        self.district_name = district_name
        self.state = state
        self.contact_no = contact_no
        self.email_id = email_id
class Farmer(db.Model):

    __tablename__ = 'farmer'

    farmer_id = db.Column(db.String(20), primary_key = True)
    farmer_name = db.Column(db.String(40))
    farm_size = db.Column(db.Integer)
    contact_no = db.Column(db.String(10), unique=True, index=True)
    adhaar = db.Column(db.String(12))
    village_name = db.Column(db.String(20))
    district_name = db.Column(db.String(25))
    state = db.Column(db.String(2))
    request_harvest = db.Column(db.Integer, default=0)

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
        print("Farmer id {1}, Farmer name {2}").format(self.farmer_id, self.farmer_name)

class Harvest_Equipment(db.Model):

    __tablename__ = 'harvest_equipment'

    equip_id = db.Column(db.String(20), primary_key=True)
    available = db.Column(db.Integer, server_default='0')
    name_equip = db.Column(db.String(30))
    type_equip = db.Column(db.String(20))
    manufac_cmp = db.Column(db.String(30))
    year_of_purchase = db.Column(db.Integer)
    last_servicing = db.Column(db.Date)
    next_servicing = db.Column(db.Date)
    servicing_comp = db.Column(db.String(25))
    contact_person = db.Column(db.String(40))
    contact_number = db.Column(db.String(10))
    hours_completed_today = db.Column(db.Integer, server_default='0')

    def __init__(self, available, equip_id, name_equip, type_equip, manufac_cmp, year_of_purchase, last_servicing, next_servicing, servicing_comp, contact_person, contact_number, hours_completed_today):
        self.equip_id = equip_id
        self.available = available
        self.name_equip = name_equip
        self.type_equip = type_equip
        self.manufac_cmp = manufac_cmp
        self.year_of_purchase = year_of_purchase
        self.last_servicing = last_servicing
        self.next_servicing = next_servicing
        self.servicing_comp = servicing_comp
        self.contact_person = contact_person
        self.contact_number = contact_number
        self.hours_completed_today = hours_completed_today

class Stalk_Collector(db.Model):

    __tablename__= 'stalk_collector'

    collector_id = db.Column(db.String(20), primary_key=True)
    password_hash = db.Column(db.String(128))
    collector_name = db.Column(db.String(40))
    contact_no = db.Column(db.String(10), unique=True, index=True)
    district_name = db.Column(db.String(25))
    state = db.Column(db.String(2))
    hours_of_work = db.Column(db.Integer, server_default='0')
    hours_completed_today = db.Column(db.Integer, server_default='0')
    email_id = db.Column(db.String(64), unique=True, index=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.collector_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Stalk_Collector.query.get(user_id)
    def __init__(self, collector_id, password, collector_name, district_name, state,contact_no,email_id):
        self.collector_id = collector_id
        self.password_hash = generate_password_hash(password)
        self.collector_name = collector_name
        self.contact_no = contact_no
        self.district_name = district_name
        self.state = state
        self.email_id = email_id


class Gram_Panchayat(db.Model):

    __tablename__ = 'gram_panchayat'

    username = db.Column(db.String(20), primary_key=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(30))
    contact_no = db.Column(db.String(10), unique=True, index=True)
    email_id = db.Column(db.String(64), unique=True, index=True)
    village_name = db.Column(db.String(20))
    district_name = db.Column(db.String(25))
    state = db.Column(db.String(2))

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.username}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Gram_Panchayat.query.get(user_id)

    def __init__(self, username, password, name, contact_no, email_id, village_name, district_name, state):
        self.username = username
        self.password_hash = generate_password_hash(password)
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
    req_gen = db.relationship('Gram_Panchayat', backref='request_harvest', uselist=False, foreign_keys=[requestor_id])
    no_farmers = db.Column(db.Integer)
    date_request = db.Column(db.Date)
    jobs_completed = db.Column(db.Integer, server_default='0')
    req_gen = db.relationship(Gram_Panchayat, backref='request_harvest', uselist=False, foreign_keys=requestor_id)

    def __init__(self, request_id , requestor_id, no_farmers, date_request):
        self.request_id = request_id
        self.requestor_id = requestor_id
        self.no_farmers = no_farmers
        self.date_request = date_request

class Request_user_id(db.Model):

    __tablename__ = 'request_user_id'

    new_user_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    req_gen_id = db.Column(db.String(20), db.ForeignKey('gram_panchayat.username'))
    req_gen = db.relationship('Gram_Panchayat', backref='request_user_id', uselist=False, foreign_keys=[req_gen_id])
    no_gen = db.Column(db.Integer)
    req_complete = db.Column(db.Integer, server_default='0')
    req_gen = db.relationship(Gram_Panchayat, backref='request_user_id', uselist=False, foreign_keys=req_gen_id)

    def __init__(self, new_user_id, date, req_gen_id, no_gen):
        self.new_user_id = new_user_id
        self.date = date
        self.req_gen_id = req_gen_id
        self.no_gen = no_gen

class Factory_Stalk_Collection(db.Model):

    __tablename__ = 'factory_stalk_collection'
    __table_args__ = {'extend_existing':True} 

    request_id = db.Column(db.Integer, primary_key=True)
    village_name = db.Column(db.String(20))
    district_name = db.Column(db.String(25))
    state = db.Column(db.String(2))
    date_request = db.Column(db.Date)
    date_fulfilment = db.Column(db.Date)
    bales_stalk = db.Column(db.Integer)
    no_trucks = db.Column(db.Integer)
    amt_received = db.Column(db.Integer)

    def __init__(self, date_request, bales_stalk, village_name, district_name, state):
        self.date_request = date_request
        self.bales_stalk = bales_stalk
        self.village_name = village_name
        self.district_name = district_name
        self.state = state
class Harvest_Aider(db.Model):

    __tablename__ = 'harvest_aider'

    aider_id = db.Column(db.String(20), primary_key=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(40))
    contact_no = db.Column(db.String(10), unique=True, index=True)
    district = db.Column(db.String(20))
    state = db.Column(db.String(2))
    no_villages = db.Column(db.Integer)
    email_id = db.Column(db.String(64), unique=True, index=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.aider_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Harvest_Aider.query.get(user_id)

    def __init__(self, aider_id, password, name, contact_no, district, state, no_villages, email_id):
        self.aider_id = aider_id
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.contact_no = contact_no
        self.district = district
        self.state = state
        self.no_villages = no_villages
        self.email_id = email_id


class Job_List(db.Model):
    
    __tablename__='job_list'

    job_no = db.Column(db.String(15), primary_key=True)
    date_job = db.Column(db.Date)
    time = db.Column(db.Time)
    collector_id = db.Column(db.String(20), db.ForeignKey('stalk_collector.collector_id'))
    equip_id = db.Column(db.String(20), db.ForeignKey('harvest_equipment.equip_id'))
    farmer_id = db.Column(db.String(20), db.ForeignKey('farmer.farmer_id'))
    request_id = db.Column(db.Integer, db.ForeignKey('request_harvest.request_id'))
    location = db.Column(db.String(250))
    farm_size= db.Column(db.Integer)
    fees = db.Column(db.Integer)
    expected_duration = db.Column(db.Float)
    bales_collected = db.Column(db.Integer, server_default='0')
    job_complete = db.Column(db.Integer, server_default='0')

    collector = db.relationship(Stalk_Collector, backref='job_list', uselist=False, foreign_keys=collector_id)
    equip = db.relationship(Harvest_Equipment, backref='job_list', uselist=False, foreign_keys=equip_id)
    farmer = db.relationship(Farmer, backref='job_list', uselist=False, foreign_keys=farmer_id)
    request = db.relationship(Request_Harvest, backref='job_list', uselist=False, foreign_keys=request_id)

    def __init__(self, job_no, farmer_id, request_id, location, farm_size, fees, expected_duration):
        self.job_no = job_no
        self.farmer_id = farmer_id
        self.request_id = request_id
        self.location = location
        self.farm_size = farm_size
        self.fees = fees
        self.expected_duration = expected_duration

class User_Id(db.Model):

    __tablename__='user_id'

    state_district = db.Column(db.String(4), primary_key=True)
    farmer_cnt = db.Column(db.Integer, server_default='0')
    stalk_collector_cnt = db.Column(db.Integer, server_default='0')
    harvest_aider_cnt = db.Column(db.Integer, server_default='0')
    harvest_equip_cnt = db.Column(db.Integer, server_default='0')
    gram_panchayat_cnt = db.Column(db.Integer, server_default='0')
    job_cnt = db.Column(db.Integer, server_default='0')
    patwari_cnt = db.Column(db.Integer, server_default='0')

    def __init__(self, state_district):
        self.state_district = state_district

class Factory_Manager(db.Model):

    __tablename__='factory_manager'

    username = db.Column(db.String(20), primary_key=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(30))
    contact_no = db.Column(db.String(10), unique=True, index=True)
    email_id = db.Column(db.String(64), unique=True, index=True)
    district_name = db.Column(db.String(25))
    state = db.Column(db.String(2))

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.username}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Factory_Manager.query.get(user_id)

    def __init__(self, username, password, name, contact_no, email_id, district_name, state):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.contact_no = contact_no
        self.email_id = email_id
        self.district_name = district_name
        self.state = state