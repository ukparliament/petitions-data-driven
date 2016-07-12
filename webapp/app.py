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
	conn = httplib.HTTPConnection("data-driven.ci.ukpds.org")
	try:
		conn.request("GET", "/petitions.json")
		response = conn.getresponse()
		repsonse_body = response.read()
	finally:
		conn.close()

	data = json.loads(repsonse_body)
	return render_template("petitions/index.html", data = data)

@app.route('/petitions/<id>')
def petition(id):
	conn = httplib.HTTPConnection("data-driven.ci.ukpds.org")
	try:
		conn.request("GET", "/petitions/{0}.json".format(id))
		response = conn.getresponse()
		repsonse_body = response.read()
	finally:
		conn.close()

	data = json.loads(repsonse_body)
	return render_template("petitions/show.html", data = data)

@app.route('/constituency/<id>')
def constituency(id):
	return "constituency"

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
