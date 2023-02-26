import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
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
from app import app

draw = astimp_tools.draw

astimp.config.Inhibition_diameterReadingSensibility = 0.0
astimp.config.Inhibition_minInhibToBacteriaIntensityDiff = 25
astimp.config.Inhibition_maxInhibToBacteriaIntensityDiff = 90
astimp.config.Inhibition_minPelletIntensity = 160
astimp.config.PetriDish_PelletIntensityPercent =0.92
astimp.config.Inhibition_preprocImg_px_per_mm = 10
astimp.config.PetriDish_gcBorder =0.02
astimp.config.PetriDish_borderPelletDistance_in_mm=2

def process_petri_dish(img_name):
    astimp.config.Inhibition_minPelletIntensity=160
    plt.figure(figsize=(7,7))
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)   
    img = imread(img_path)
    ast = astimp.AST(img)
    draw(ast, atb_labels='all')
    #draw(ast, atb_labels='off')
    #for i in range(len(ast.inhibitions)):
    #    center = ast.circles[i].center
    #    diameter = ast.inhibitions[i].diameter
    #    pellet_r = astimp.config.Pellets_DiamInMillimeters/2
    #    temp = (center[0]-pellet_r*ast.px_per_mm, center[1]-pellet_r*ast.px_per_mm)
    #    bbox=dict(edgecolor='w', pad=2.0, facecolor='wheat', alpha=0.5)
    #    plt.text(*temp,round(diameter,2),color='w',bbox=bbox)
    #circles = astimp.find_atb_pellets(img)
    #pellets = [astimp.cutOnePelletInImage(img, circle) for circle in circles]
    #labels = [astimp.getOnePelletText(pellet) for pellet in pellets]
    #i=0
    #for label in labels:
    #    if label.confidence >=0.02:
    #        center = ast.circles[i].center        
    #        pellet_r = astimp.config.Pellets_DiamInMillimeters/2
    #        temp = (center[0]-pellet_r*ast.px_per_mm, center[1]+pellet_r*ast.px_per_mm)
    #        bbox=dict(edgecolor='w', pad=2.0, facecolor='wheat', alpha=0.5)
    #        plt.text(*temp, label.text,color='r',bbox=bbox)
    #    i=i+1
    processed_image_name = 'processed_'+img_name
    processed_img_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_image_name)   
    plt.savefig(processed_img_path)
    return processed_image_name

def process_image(img_name):
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)   
    img = imread(img_path)
    ast = astimp.AST(img)
    mobile_list = []
    for i in range(len(ast.labels)):
        loop_dict = {
        "label":ast.labels[i].text,
        "centerX":ast.circles[i].center[0],
        "centerY":ast.circles[i].center[1],
        "radius":ast.circles[i].radius,
        "diameter":ast.inhibitions[i].diameter
        }
        mobile_list.append(loop_dict)

    return mobile_list    