import os
import socket
import httplib
import json

from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def hello():
    provider = str(os.environ.get('PROVIDER', 'world'))
    return 'Hello '+provider+'!'
print(socket.gethostname())

@app.route('/houses')
def houses():
	conn = httplib.HTTPConnection("data-driven.ci.ukpds.org")
	try:
		conn.request("GET", "/houses.json")
		response = conn.getresponse()
		responsebody = response.read()
	finally:
		conn.close()

	data = json.loads(responsebody)
	return render_template('houses.html', data=data)

@app.route('/houses/<id>')
def house(id):
	return id

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)