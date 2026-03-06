from flask import Flask
app = Flask(__name__)
app.secret_key = 'neurotichl'
app.jinja_env.filters['zip'] = zip

from newsapp import views

