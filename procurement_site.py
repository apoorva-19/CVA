import os
import flask
from flask import send_from_directory, request
from models import app, db
# from forms import  AddForm , DelForm
from flask import Flask, render_template, url_for, redirect
from flask_migrate import Migrate
from forms import AddReq
import models
from models import Farmer, Job_List

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon.ico', mimetype='image/vnd.microsoft.icon')
@app.route('/')
def base():
    return render_template('index.html')

@app.route('/base')
def actualbase():
    return render_template('base.html')
    
@app.route('/addreq', methods=['GET', 'POST'])
def reqgen():
    # from stalk import req
    farmers = Farmer.query.filter_by(request_harvest = 0).all()
    if flask.request.method == 'POST':
        returned_values=request.form.getlist('request')
        # req(returned_values)
        for i in returned_values:
            print(i)
            val = Farmer.query.filter_by(farmer_id  = i).all()
            for v in val:
                v.request_harvest = 1
                db.session.commit()

    farmers = Farmer.query.filter_by(request_harvest = 0).all()       
    return render_template('add_req.html', data=farmers)

@app.route('/stalkcol', methods=['GET','POST'])
def stalk():
    id = 1
    if flask.request.method == 'POST':
        j_id = request.form.getlist('j_no')
        no_bales = request.form.getlist('bales')
        for j, b in zip(j_id, no_bales):
            print ("job no:",j)
            print ("no of bales: ",b)
            jlist = Job_List.query.filter_by(job_no = j).all()
            for l in jlist:
                l.bails_collected = b
                # l.job_complete = 1
                db.session.commit()      
    jl = Job_List.query.filter_by(collector_id = id).all()
    if len(jl) != 0:   
        return render_template('stalk_collector.html', data=jl)
    return render_template('stalk_collector.html', data=0)

# def est_hrs():

#     jl = Job_List.query.filter_by(collector_id = id).all()
#     if len(jl) != 0:   
#         return render_template('stalk_collector.html', data=jl)
#     return render_template('stalk_collector.html', data=0)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)