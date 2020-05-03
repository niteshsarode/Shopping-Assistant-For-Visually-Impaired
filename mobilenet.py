import numpy as np
from keras.models import Model
from keras.preprocessing import image
from keras.applications import imagenet_utils, mobilenet

class mnet:
    def __init__(self):
        self.model = mobilenet.MobileNet()

    def process_image(self, img_path):
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        return mobilenet.preprocess_input(img_array)

    def predict(self,image_path):
        img = self.process_image(image_path)
        prediction = self.model.predict(img)
        return imagenet_utils.decode_predictions(prediction)
