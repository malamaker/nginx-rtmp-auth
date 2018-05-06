from flask import Flask, request
from flask_api import status
import psycopg2
import sys
sys.path.append('/app/flask/auth')
import config

app = Flask(__name__)

@app.route('/auth')
def auth():
	if request.args.get('name') is None or request.args.get('id') is None:
		return 'Malformed request', status.HTTP_400_BAD_REQUEST
	
	username = request.args.get('name')
	app = request.args.get('app')
	idhash = request.args.get('id')
	# idhash = request.args.get('swfurl').split("?")[-1]
	
	conn = psycopg2.connect(database=config.database, user=config.user, password=config.password, host=config.host)
	cur = conn.cursor()
	cur.execute("SELECT FROM %s WHERE ((username=%s AND all_access=1 AND idhash=%s) AND (username=%s AND idhash=%s AND (app LIKE %s OR app LIKE %s OR app LIKE %s))) AND enable=1", \
		    ( \
		     config.usertablename, \
		     username, \
		     idhash, \
		     username, \
		     idhash, \
		     "all", \
		     app + ",%", \
		     "%," + app + ",%" \
		    ))
	
	if len(cur.fetchall()) == 0:
		return 'Incorrect credentials or access', status.HTTP_401_UNAUTHORIZED

	return 'OK', status.HTTP_200_OK

if __name__== '__main__':
	app.run()
