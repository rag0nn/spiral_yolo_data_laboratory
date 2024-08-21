from tensorflow.image import adjust_saturation, adjust_brightness, rot90
import cv2
import numpy as np
from spiral_lab.dataset.spiral_dataset_object import SpiralDatasetObject

def filter_saturation(image,factor=1.25):
    """
    doygunluk filtresi ekle
    """
    return adjust_saturation(image, factor).numpy(),"saturation"

def filter_brightness(image,delta = 0.17):
    """
    parlaklık filtresi ekle
    """
    return adjust_brightness(image,delta).numpy(), "brightness" 

