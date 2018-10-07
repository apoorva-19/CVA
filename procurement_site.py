from models import app, db
from forms import  AddForm , DelForm
from flask import Flask, render_template, url_for, redirect
from flask_migrate import Migrate

Migrate(app, db)

@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()

if __name__ == '__main__':
    app.run(debug=True)