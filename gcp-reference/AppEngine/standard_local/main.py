from flask import Flask, redirect, url_for, request, render_template, jsonify
from google.appengine.api import taskqueue, memcache, urlfetch
from google.appengine.ext import ndb
from datetime import datetime 
from flasgger import Swagger
from flasgger.utils import swag_from
from bs4 import BeautifulSoup
import numpy as np
import logging
import time


app = Flask(__name__)
app.config['SWAGGER'] = {
		'title':'Quotes',
		'description':'Random quote generator with respect to category',
	}
Swagger(app)

@app.route('/')
def hello_world():
	return "Hello World!"

################################## NDB DATASTORE ##########################################

class HelloWorld(ndb.Model):
	# https://cloud.google.com/appengine/docs/standard/python/ndb/
	Date = ndb.DateTimeProperty(indexed=True)
	Text = ndb.StringProperty(indexed=True)
	Integer = ndb.IntegerProperty(indexed=True)
	Float = ndb.FloatProperty(indexed=True)

@app.route('/insert')
def insert_datastore():

	now = datetime.now()
	hello_data = HelloWorld(Date = now,
							Text = 'hello world!',
							Integer = now.hour,
							Float = np.random.rand(1)[0])
	hello_data.put()
	return 'Data inserted to datastore at {}'.format(now), 200

################################## TASK QUEUE #############################################

@app.route('/queue')
def queue_task():
	queue = taskqueue.Queue(name='happyqueue')
	task = taskqueue.Task(
	    url="/delay_insert",
	    method="GET",
	    target="neurotic")
	    # payload=json.dumps(payload))
	rpc = queue.add_async(task)
	task = rpc.get_result()
	logging.info(task)
	return "queue {}".format(task.name)

@app.route('/delay_insert')
def delay():
	now = datetime.now()
	time.sleep(5)
	logging.info('task queue at time {}'.format(now.isoformat()))
	hello_data = HelloWorld(Date = now,
							Text = 'queued hello world!',
							Integer = now.hour,
							Float = np.random.rand(1)[0])
	hello_data.put()
	return 'Data inserted from queue to datastore at {}'.format(now), 200


################################## MEMCACHE ###############################################
m = memcache.Client()

@app.route('/cache', methods=['GET','POST'])
def name():
	if request.method == 'POST':
		name = request.form['Name']
		
		value = m.get(name)
		if not value:
			return render_template('whatmood.html', name=name)
		elif value:
			return render_template('updatemood.html', name=name, mood=value)

	return render_template('mood.html')

@app.route('/mood', methods=['POST'])
def current_mood():

	name = request.form['Name']
	mood = request.form['mood']
	
	if request.form['submit_mood'] == 'Update':
		m.get(name, for_cas=True)
		m.cas(name,mood) # Update existing memcache value
	elif request.form['submit_mood'] == 'Forget about me':
		m.delete(name)
		return "<html><p>Goodbye... Unknown guest</p><a href=/cache>Go back</a></html>"
	else:
		m.add(name, mood, 60) # key, value, timeout

	return '''
	<html>
		<body>
			<p>Hi {}, You are feeling {} now...</p>
			<a href=/cache>Go back</a>
		</body>
	</html>
	'''.format(name, mood)

################################### urlfetch, flasgger #########################################
# http://brunorocha.org/python/flask/flasgger-api-playground-with-flask-and-swagger-ui.html
@app.route('/quote/<string:category>')
@swag_from('swag.yaml')
def quote(category):
	resp = urlfetch.Fetch('https://www.brainyquote.com/topics/{}'.format(category))
	soup = BeautifulSoup(resp.content, 'html.parser')

	quotes = [q.text for q in soup.find_all('a',{'title':'view quote'})]
	length = len(quotes)

	if length:
		quote =  quotes[np.random.randint(length-1)]
		return jsonify(quote=quote)
	else:
		return 'Quote category not found!', 500

if __name__=='__main__':
	app.run()
