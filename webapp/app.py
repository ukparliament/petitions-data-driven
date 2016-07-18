import os
import socket
import httplib
import json
import urllib2

from flask import Flask
from flask import render_template
from datetime import datetime
from healthcheck import HealthCheck, EnvironmentDump

app = Flask(__name__)
datadriven_endpoint = os.environ["DATADRIVEN_ENDPOINT"]


# ====== Health checks ====== #

health = HealthCheck(app, "/healthcheck")
envdump = EnvironmentDump(app, "/environment",
	include_python=False, include_os=False,
	include_process=False, include_config=False)

def datadriven_endpoint_available():
	if not datadriven_endpoint:
		return False, "Data driven endpoint has not been configured"

	url = "http://" + datadriven_endpoint + "/"
	try:
		resp = urllib2.urlopen(url)
		try:
			code = resp.getcode()
			if code < 400:
				return True, "Endpoint available: " + url
			else:
				return False, "Endpoint " + url + " returned a status code " + code
		finally:
			resp.close()
	except Exception, ex:
		return False, "Endpoint " + url + " threw an exception: " + ex.__repr__()

health.add_check(datadriven_endpoint_available)

# add your own data to the environment dump
def application_data():
    return {
		"maintainer": "Parliamentary Digital Service",
		"git_repo": "https://github.com/ukpds/petitions-data-driven"
	}

envdump.add_section("application", application_data)

# ====== Routes ====== #

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

@app.route('/constituencies/<id>')
def constituency(id):
	return render_template("constituencies/show.html", data = __get_json_data("/constituencies/{0}.json".format(id)))

def __get_json_data(url):
	conn = httplib.HTTPConnection(datadriven_endpoint)
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
