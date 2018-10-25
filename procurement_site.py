import os
from flask import send_from_directory
from models import app, db
# from forms import  AddForm , DelForm
from flask import Flask, render_template, url_for, redirect
from flask_migrate import Migrate

Migrate(app, db)

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
    

if __name__ == '__main__':
    app.run(debug=True)