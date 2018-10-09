import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Primary_Node(db.Model):

    __tablename__ = 'primary_node'
    
    primary_id = db.Column(db.Integer, primary_key = True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    owner = db.Column(db.String(30))
    address = db.Column(db.String(150))
    contact = db.Column(db.String(10))
    size_field = db.Column(db.Float)
    no_sensors = db.Column(db.Integer, default=0)
    no_repair = db.Column(db.Integer, default=0)
    no_fines = db.Column(db.Integer, default=0)

    def __init__(self, primary_id, latitude, longitude, owner, address, contact, size_field):
        self.primary_id = primary_id
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.address = address
        self.contact = contact
        self.size_field = size_field

    def __repr__(self):
        return f"Owner: {self.owner}, No of sensors: {self.no_sensors}"

class Secondary_Node(db.Model):

    __tablename__ = 'secondary_node'

    secondary_id = db.Column(db.Integer, primary_key = True)
    primary_id = db.Column(db.Integer, db.ForeignKey('primary_node.primary_id'), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    condition = db.Column(db.Integer, default=1)
    no_repair = db.Column(db.Integer, default=0)

    def __init__(self, secondary_id, primary_id, latitude, longitude):
        self.secondary_id = secondary_id
        self.primary_id = primary_id
        self.latitude = latitude
        self.longitude = longitude

class Police_Station(db.Model):

    __tablename__ = 'police_station'

    station_no = db.Column(db.Integer, primary_key = True)
    officer_name = db.Column(db.String(30))
    address = db.Column(db.String(150))
    contact = db.Column(db.String(10))

    def __init__(self, station_no, officer_name, address, contact):
        self.station_no = station_no
        self.officer_name = officer_name
        self.address = address
        self.contact = contact

class Gram_Panchayat(db.Model):

    __tablename__ = 'gram_panchayat'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    sarpanch_name = db.Column(db.String(30))
    contact = db.Column(db.String(10))
    login = db.Column(db.String(20))
    password = db.Column(db.String(256))
    no_trips = db.Column(db.Integer, default=0)

    def __init__(self, id, sarpanch_name, contact, login, password):
        self.id = id,
        self.sarpanch_name = sarpanch_name
        self.contact = contact
        self.login = login
        self.password = password
