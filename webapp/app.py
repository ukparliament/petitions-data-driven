import os
import socket
import httplib
import json
import urllib2

from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime
from healthcheck import HealthCheck, EnvironmentDump
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)
# datadriven_endpoint = os.environ["DATADRIVEN_ENDPOINT"]
datadriven_endpoint = "ukpds-data-driven.herokuapp.com"


#====== Health checks ====== #

# health = HealthCheck(app, "/healthcheck")
# envdump = EnvironmentDump(app, "/environment",
# 	include_python=False, include_os=False,
# 	include_process=False, include_config=False)

# def datadriven_endpoint_available():
# 	if not datadriven_endpoint:
# 		return False, "Data driven endpoint has not been configured"

# 	url = "http://" + datadriven_endpoint + "/"
# 	try:
# 		resp = urllib2.urlopen(url)
# 		try:
# 			code = resp.getcode()
# 			if code < 400:
# 				return True, "Endpoint available: " + url
# 			else:
# 				return False, "Endpoint " + url + " returned a status code " + code
# 		finally:
# 			resp.close()
# 	except Exception, ex:
# 		return False, "Endpoint " + url + " threw an exception: " + ex.__repr__()

# health.add_check(datadriven_endpoint_available)

# # add your own data to the environment dump
# def application_data():
#     return {
# 		"maintainer": "Parliamentary Digital Service",
# 		"git_repo": "https://github.com/ukpds/petitions-data-driven"
# 	}

# envdump.add_section("application", application_data)

#====== Routes ====== #

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
	return render_template("petitions/show.html", data = __get_json_data("/petitions/{0}.json".format(id)), endpoint = datadriven_endpoint)

@app.route('/petitions/edit/<id>')
def petition_edit(id):
	return render_template("petitions/edit.html", petition_data = __get_json_data("/petitions/{0}.json".format(id)), concepts_data = __get_json_data("/concepts.json"))

@app.route('/petitions/update/<id>', methods = ['POST'])
def petition_update(id):
	subject_uri = __resource_uri(id)

	if request.form.get('update') == 'add':
		object_id = request.form.get('add_concepts')
		object_uri = __resource_uri(object_id)
		queryStringUpload = "insert {<%s> <http://purl.org/dc/terms/subject> <%s>} WHERE { }" % (subject_uri, object_uri)

	if request.form.get('update') == 'remove':
		concepts = request.form.getlist('remove_concepts')
		delete_statements = [ "<%s> <http://purl.org/dc/terms/subject> <%s> . " % (subject_uri, __resource_uri(concept_id)) for concept_id in concepts]
		queryStringUpload = "delete {" + "".join(delete_statements) + "} WHERE { }"

	if request.form.get('update') == 'index':
		queryStringUpload = __update_index_status(request.form.get('index-checkbox'), subject_uri)

	sparql = SPARQLWrapper("http://graphdbtest.eastus.cloudapp.azure.com/repositories/DataDriven06/statements")
	sparql.setQuery(queryStringUpload)
	sparql.method = 'POST'
	sparql.query()
	return redirect(url_for('petition_edit', id = id))

@app.route('/constituencies')
def constituencies():
	return render_template("constituencies/index.html", data = __get_json_data('/constituencies.json'))

@app.route('/constituencies/<id>')
def constituency(id):
	return render_template("constituencies/show.html", data = __get_json_data("/constituencies/{0}.json".format(id)), endpoint = datadriven_endpoint)

def __update_index_status(checkbox_status, subject_uri):
	if checkbox_status == 'indexed':
		return "insert {<%s> <http://data.parliament.uk/schema/parl#indexed> 'indexed'} WHERE { } " % (subject_uri)
	else:
		return "delete {<%s> <http://data.parliament.uk/schema/parl#indexed> 'indexed'} WHERE { } " % (subject_uri)

def __get_json_data(url):
	conn = httplib.HTTPConnection(datadriven_endpoint)
	try:
		conn.request("GET", url)
		response = conn.getresponse()
		repsonse_body = response.read()
	finally:
		conn.close()

	return json.loads(repsonse_body)

def __resource_uri(id):
	return "http://id.ukpds.org/{0}".format(id)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
