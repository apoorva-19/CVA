import os
import json
from flask import send_from_directory
from flask import Flask, render_template, url_for, redirect
from flask_migrate import Migrate

from models import app, db
from forms import  AddStalkCollector

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

@app.route('/harvest-aider')
def harvest_aider():
    return render_template('/harvest_aider/index.html')
    
@app.route('/harvest-aider/add-collector/')
def add_collector():
    form = AddStalkCollector()
    district = code.get('AP')
    ind = list(range(1, len(district)+1))
    form.district_name.choices = list(zip(ind, district))

    return render_template('/harvest_aider/add_collector.html', form=form)
    
@app.route('/harvest-aider/add-collector/<state>')
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

    
if __name__ == '__main__':
    app.run(debug=True)