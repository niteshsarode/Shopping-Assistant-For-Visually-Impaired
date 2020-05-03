import json
import logging
import os
import pathlib
import numpy as np
import tensorflow as tf
import mobilenet
import detector
from PIL import Image
from PIL import ImageDraw
from google.cloud import storage
from flask import Flask, request


app = Flask(__name__)

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

@app.errorhandler(500)
def server_error(e):
	logging.exception('An error occurred during a request.')
	return """
	An internal error occurred: <pre>{}</pre>
	See logs for full stacktrace.
	""".format(e), 500

@app.route('/predict', methods=['GET', 'POST'])
def predict():
	# m = mobilenet.mnet()
	# res = m.predict('test_image.jpg')
	# print(res)
	d = detector.detector()
	image = request.files.get('image', '')
	res = d.detect(image)
	print(res)
	return {'X':10}, 200
	# X = request.get_json()['X']
	# y = MODEL.predict(X).tolist()
	# return json.dumps({'y': [1.0,2.0]}), 200

@app.route('/')
def hello_world():
	return 'Shopping Assistant for Visually Impaired!'

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)