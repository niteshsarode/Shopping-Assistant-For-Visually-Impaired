import json
import logging
import os
import pathlib
import numpy as np
import tensorflow as tf
from PIL import Image
from PIL import ImageDraw
from flask import Flask, request
from google.cloud import storage

app = Flask(__name__)

class detector():

	def __init__(self):
		self.bucket_name = os.environ['MODEL_BUCKET']
		self.model_filename = os.environ['MODEL_FILENAME']
		self.labels_path = 'mscoco_label_map.pbtxt'
		self.model = None
		self.category_map = None

	def get_label_map(self):
		with open(labels_path,"r") as labels:
			lines = labels.readlines()
			res = []
			for l in lines:
				if "id" in l or "display_name" in l:
					l = l.replace('display_name','')
					l = l.replace('id','')
					l = l.replace('\n','')
					l = l.replace(':','')
					l = l.replace('"','')
					l = l.strip()
					res.append(l)
			self.category_map = {res[i]: res[i+1] for i in range(0,len(res),2)}

	def _load_image_into_numpy_array(self, image):
		(im_width, im_height) = image.size
		return np.array(image.getdata()).reshape(
				(im_height, im_width, 3)).astype(np.uint8)

	def detect(self, image):
		image_np = self._load_image_into_numpy_array(image)
		input_tensor = tf.convert_to_tensor(image_np)
		input_tensor = input_tensor[tf.newaxis,...]
		output_dict = self.model(input_tensor)

		num_detections = int(output_dict.pop('num_detections'))
		output_dict = {key:value[0, :num_detections].numpy() 
										for key,value in output_dict.items()}
		boxes = output_dict['detection_boxes']
		classes = output_dict['detection_classes'].astype(np.int64)
		scores = output_dict['detection_scores']
		
		return boxes, scores, classes, num_detections

	def detect_objects(self, image_path):
		image = Image.open(image_path).convert('RGB')
		boxes, scores, classes, num_detections = detect(image)
		image.thumbnail((480, 480), Image.ANTIALIAS)

		new_images = {}
		for i in range(num_detections):
			if scores[i] < 0.7: continue
			cls = classes[i]
			if cls not in new_images.keys():
				new_images[cls] = image.copy()
			# draw_bounding_box_on_image(new_images[cls], boxes[i], thickness=int(scores[i]*10)-4)

		result = {}
		# result['original'] = encode_image(image.copy())

		for cls, new_image in new_images.items():
			category = self.category_map[cls]
			result[category] = 1
			# result[category] = encode_image(new_image)

		return result

@app.before_first_request
def _load_model():
	client = storage.Client()
	bucket = client.bucket(detector_obj.bucket_name)
	blob = bucket.blob(detector_obj.model_filename)
	print(dir(blob))
	print(detector_obj.bucket_name)
	print(detector_obj.model_filename)
	detector_obj.get_label_map()
	print(detector_obj.category_map)
	blob.download_to_file('saved_model.pb')
	print("Model Downloaded..!")
	detector_obj.model = tf.saved_model.load(detector_obj.model_filename)
	detector_obj.model = detector_obj.model.signatures['serving_default']

@app.errorhandler(500)
def server_error(e):
	logging.exception('An error occurred during a request.')
	return """
	An internal error occurred: <pre>{}</pre>
	See logs for full stacktrace.
	""".format(e), 500

@app.route('/predict', methods=['GET', 'POST'])
def predict():
	image = request.get_json()['input_image']
	res = detector_obj.detect_objects(image)
	return res, 200
	# X = request.get_json()['X']
	# y = MODEL.predict(X).tolist()
	# return json.dumps({'y': [1.0,2.0]}), 200

@app.route('/')
def hello_world():
	return 'Shopping Assistant for Visually Impaired!'

detector_obj = detector()

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)