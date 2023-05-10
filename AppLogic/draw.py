import os
from flask import Flask, current_app
import matplotlib.pyplot as plt
import astimp
import astimp_tools
from skimage.io import imread
from PIL import Image
import numpy as np
from matplotlib.patches import Circle
import matplotlib.transforms as mtransforms
import matplotlib.patches as mpatch
from matplotlib.patches import FancyBboxPatch
from imageio.v2 import imread, imwrite
import time


app = current_app
draw = astimp_tools.draw

astimp.config.Inhibition_diameterReadingSensibility = 0.0
astimp.config.Inhibition_minInhibToBacteriaIntensityDiff = 25
astimp.config.Inhibition_maxInhibToBacteriaIntensityDiff = 90
astimp.config.Inhibition_minPelletIntensity = 160
astimp.config.PetriDish_PelletIntensityPercent =0.92
astimp.config.Inhibition_preprocImg_px_per_mm = 10
astimp.config.PetriDish_gcBorder =0.02
astimp.config.PetriDish_borderPelletDistance_in_mm=2

def draw_petri_dish(img_path):
    astimp.config.Inhibition_minPelletIntensity = 160
    plt.figure(figsize=(7, 7))
    img = imread(img_path)
    ast = astimp.AST(img)
    draw(ast, atb_labels='all')
    processed_image_name = 'processed-'+str(time.time())+'.jpg'
    processed_img_path = os.path.join(
        app.config['PROCESSED_FOLDER'], processed_image_name)
    plt.savefig(processed_img_path)
    return processed_img_path
