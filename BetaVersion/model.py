from tensorflow.keras.models import load_model
import cv2
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import os

def load_model(filepath):
  model = tf.keras.models.load_model('worst.keras')
  img = cv2.imread(filepath) # image file location

  resize = tf.image.resize(img, (200,240))

  grayscale_image = tf.image.rgb_to_grayscale(resize)

  # List all subdirectories using os.listdir()
  labels = [f.name for f in os.scandir('D:\\USTHGroupProject\\demo\\dataset\\HandGesture\\images') if f.is_dir()]

  yhat = model.predict(np.expand_dims(grayscale_image, 0))
  yhat
  max_position = np.argmax(yhat)
  
  return labels[max_position]