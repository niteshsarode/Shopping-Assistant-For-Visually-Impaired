import json
import logging
import os.path
from os import path
import pathlib
import numpy as np
import tensorflow as tf
import mobilenet
import detector
from PIL import Image
from PIL import ImageDraw
from google.cloud import storage
from flask import Flask, request, Response
import sqlalchemy
import base64
import time

app = Flask(__name__)
db = None
logger = logging.getLogger()
bucket_name = 'shoppingassitant-275209.appspot.com'
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")

# d = None

db = sqlalchemy.create_engine(
	# Equivalent URL:
	# postgres+pg8000://<db_user>:<db_pass>@/<db_name>?unix_sock=/cloudsql/<cloud_sql_instance_name>/.s.PGSQL.5432
	sqlalchemy.engine.url.URL(
		drivername = 'postgres+pg8000',
		username = 'postgres',
		password = 'postgres',
		database = 'user_db',
		# query = {
		# 	'unix_sock': '../../cloudsql/shoppingassitant-275209:us-central1:cloud-sql-instance/.s.PGSQL.5432'
		# }
		query = {
			'unix_sock': '/cloudsql/shoppingassitant-275209:us-central1:cloud-sql-instance/.s.PGSQL.5432'
		}
	),
)

db.execute("CREATE TABLE IF NOT EXISTS users "
	"( user_id SERIAL NOT NULL, username VARCHAR NOT NULL, "
	"password VARCHAR NOT NULL, email VARCHAR NOT NULL, PRIMARY KEY (user_id) );"
)
	

# @app.before_first_request
# def _load_model():
# 	d = detector.detector()

def create_file(user_id, user_list):
	with open(user_id+'.txt', 'w') as req_file:
		for ul in user_list:
			req_file.write(ul+'\n')

def upload_file(user_id):
	client = storage.Client()
	bucket = client.bucket(bucket_name)
	blob = bucket.blob(user_id+'.txt')
	blob.upload_from_filename(user_id+'.txt')

def get_list(user_id):
	client = storage.Client()
	bucket = client.bucket(bucket_name)
	blob = bucket.blob(user_id+'.txt')
	blob.download_to_filename(user_id+'.txt')

def read_list(user_id):
	user_list = []
	with open(user_id+'.txt', 'r') as ulist_file:
		user_list = ulist_file.readlines()
	return [u.replace("\n","") for u in user_list]

@app.errorhandler(500)
def server_error(e):
	logging.exception('An error occurred during a request.')
	return """
	An internal error occurred: <pre>{}</pre>
	See logs for full stacktrace.
	""".format(e), 500

@app.route('/get_user', methods=['POST'])
def get_user():
	print("skjdfksj")
	username = request.form['user_name']
	password = request.form['password']
	print("username", username)
	print("psasword", password)
	query = sqlalchemy.text(
        "SELECT * from users"
    )

	try:
		with db.connect() as conn:
			res = conn.execute(query)
			users = res.fetchall()
			print(users)
			for u in users:
				if u[2] == password and u[1] == username:
					return Response(
						status=200,
						response="Found " + str(u[0])
					)
	except Exception as e:
		logger.exception(e)
		return Response(
			status=500,
			response="Unable to fetch user! Please check the "
					 "application logs for more details."
		)

	return Response(
		status=200,
		response="Not found"
	)
	
@app.route('/add_user', methods=['POST'])
def add_user():
	user_name = request.form['user_name']
	password = request.form['password']
	email = request.form['email']
	print(user_name, password, email)
	query = sqlalchemy.text(
        "INSERT INTO users (username, password, email)"
        " VALUES (:user_name, :password, :email)"
    )
	try:
		with db.connect() as conn:
			conn.execute(query, user_name=user_name, password=password, email=email)
	except Exception as e:
		logger.exception(e)
		return Response(
			status=500,
			response="Unable to add user! Please check the "
					 "application logs for more details."
		)

	return Response(
        status=200,
        response="added"
    )

@app.route('/add_user_list', methods=['POST'])
def add_user_list():
	user_list = request.form['user_list']
	user_list = user_list.split(",")
	user_id = request.form['user_id']
	create_file(user_id, user_list)
	upload_file(user_id)
	return Response(
        status=200,
        response="User List successfully added!"
    )


@app.route('/predict', methods=['POST'])
def predict():

	user_id = request.form['user_id']
	print(user_id)
	if not path.exists(user_id+'.txt'):
		get_list(user_id)
	
	user_list = read_list(user_id)
	print("user_list: ", user_list)

	start_time = int(request.form['start_time'])
	print(start_time)

	# m = mobilenet.mnet()
	# res = m.predict('test_image.jpg')
	# print(res)
	
	image = request.form['input_image']
	image = base64.b64decode(image)
	d = detector.detector()
	res = d.detect_objects(image)
	res = list(res.keys())
	print("res", res)
	overlap = list(set(res).intersection(set(user_list)))
	print("overlap", overlap)
	end_time = time.time()
	print(end_time-start_time)
	if len(overlap) > 0:
		return overlap[0]
	else:
		return ""

@app.route('/')
def hello_world():
	return 'Shopping Assistant for Visually Impaired!'

if __name__ == '__main__':
	# app.run(host='127.0.0.1', port=8080, debug=True)
	app.run(host='0.0.0.0', port=8080, debug=True)