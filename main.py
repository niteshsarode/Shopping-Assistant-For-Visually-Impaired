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

app = Flask(__name__)
db = None
logger = logging.getLogger()
bucket_name = 'shoppingassitant-275209.appspot.com'
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")

# d = detector.detector()

db = sqlalchemy.create_engine(
	# Equivalent URL:
	# postgres+pg8000://<db_user>:<db_pass>@/<db_name>?unix_sock=/cloudsql/<cloud_sql_instance_name>/.s.PGSQL.5432
	sqlalchemy.engine.url.URL(
		drivername = 'postgres+pg8000',
		username = 'postgres',
		password = 'postgres',
		database = 'user_db',
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
# def create_table():
# 	# Create tables (if they don't already exist)
	

# @app.before_first_request
# def _load_model():
# 	detector_obj.get_label_map()
# 	client = storage.Client()
# 	bucket = client.bucket(detector_obj.bucket_name)
# 	blob = bucket.blob(detector_obj.model_filename)
# 	blob.download_to_filename('models/saved_model.pb')
# 	print("Model Downloaded..!")
# 	detector_obj.model = tf.saved_model.load('models/saved_model.pb')
# 	detector_obj.model = detector_obj.model.signatures['serving_default']

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
	blob.download_from_filename(user_id+'.txt')

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

@app.route('/add_user', methods=['POST'])
def add_user():
	user_name = request.form['user_name']
	password = request.form['password']
	email = request.form['email']
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
        response="User '{}' successfully added!".format(
            user_name)
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
	if not path.exists(user_id+'.txt'):
		get_list(user_id)
	
	user_list = read_list(user_id)
	print("user_list: ", user_list)

	# m = mobilenet.mnet()
	# res = m.predict('test_image.jpg')
	# print(res)
	
	image = request.files.get('input_image', '')
	res = d.detect_objects(image)
	res = list(res.keys())
	overlap = list(set(res).intersection(set(user_list)))
	return {'objects': overlap}

@app.route('/')
def hello_world():
	return 'Shopping Assistant for Visually Impaired!'

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)