from flask import Flask, request
from flask_api import status
import psycopg2
import sys
import config

app = Flask(__name__)

@app.route('/auth')
def auth():
	if request.args.get('name') is None or request.args.get('user') is None or request.args.get('id') is None:
		return 'Malformed request', status.HTTP_400_BAD_REQUEST
	
	stream = request.args.get('name')
	app = request.args.get('app')
	username = request.args.get('user')
	idhash = request.args.get('id')
	
	streamNum = 0
	undScr = stream[len(stream)-3:-2] == "_"
	if undScr:
		streamNumTmp = stream[len(stream)-2:]

		if streamNumTmp == "00":
			return 'Incorrect credentials or access', status.HTTP_400_BAD_REQUEST

		try:
        		streamNum = int(streamNumTmp)
			stream = stream[:-3]
    		except ValueError:
        		return 'Malformed stream', status.HTTP_400_BAD_REQUEST
		
	app_stream = app + "/" + stream
	app_streamWildcard = app + "/*"
	
	conn = psycopg2.connect(database=config.database, user=config.user, password=config.password, host=config.host)
	cur = conn.cursor()
	cur.execute("SELECT FROM " + config.usertablename + " WHERE username=%s AND idhash=%s AND enabled=1 AND (app_stream = %s OR app_stream LIKE %s OR (app_stream LIKE %s AND streams >= %s))", \
		    (username, \
		     idhash, \
		     "all", \
		     "%" + app_streamWildcard + "%", \
		     "%" + app_stream + "%", streamNum))
	
	if len(cur.fetchall()) == 0:
		return 'Incorrect credentials or access', status.HTTP_401_UNAUTHORIZED

	return 'OK', status.HTTP_200_OK

if __name__== '__main__':
	app.run()
