from PIL import Image
from PIL import ImageDraw
from google.cloud import storage
import numpy as np
import tensorflow as tf
import os.path
from os import path

class detector:

	def __init__(self):
		# self.bucket_name = os.environ['MODEL_BUCKET']
		# self.model_filename = os.environ['MODEL_FILENAME']
		self.bucket_name = 'shoppingassitant-275209.appspot.com'
		self.model_filename = 'saved_model.pb'
		self.labels_path = 'mscoco_label_map.pbtxt'
		self.model = self.load_model()
		self.category_map = self.get_label_map()
		
	def load_model(self):
		client = storage.Client()
		bucket = client.bucket(self.bucket_name)
		blob = bucket.blob(self.model_filename)
		if not path.exists('models/'+self.model_filename):
			blob.download_to_filename('models/'+self.model_filename)
		print("Model Downloaded..!")
		# sess = tf.compat.v1.Session()
		model = tf.keras.models.load_model('models/')
		return model.signatures['serving_default']

	def get_label_map(self):
		with open(self.labels_path,"r") as labels:
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
			return {res[i]: res[i+1] for i in range(0,len(res),2)}

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
		boxes, scores, classes, num_detections = self.detect(image)
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
			category = self.category_map[str(cls)]
			result[category] = 1
			# result[category] = encode_image(new_image)

		return result