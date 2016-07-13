import os
import socket
import httplib
import json

from flask import Flask
from flask import render_template
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def hello():
    provider = str(os.environ.get('PROVIDER', 'world'))
    return 'Hello '+provider+'!'
print(socket.gethostname())

@app.route('/petitions')
def petitions():
	return render_template("petitions/index.html", data = __get_json_data('/petitions.json'))

@app.route('/petitions/<id>')
def petition(id):
	return render_template("petitions/show.html", data = __get_json_data("/petitions/{0}.json".format(id)))

@app.route('/constituencies')
def constituencies():
	return render_template("constituencies/index.html", data = __get_json_data('/constituencies.json'))

@app.route('/constituency/<id>')
def constituency(id):
	return "constituency"

def __get_json_data(url):
	conn = httplib.HTTPConnection("ukpds-data-driven.herokuapp.com")
	try:
		conn.request("GET", url)
		response = conn.getresponse()
		repsonse_body = response.read()
	finally:
		conn.close()

	return json.loads(repsonse_body)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
