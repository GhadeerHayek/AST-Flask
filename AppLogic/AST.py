import os
from flask import Flask, current_app
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import astimp
import astimp_tools
from skimage.io import imread
from PIL import Image
from imageio.v2 import imread, imwrite
from app import app
import time

app = current_app

"""
    genertate_image_crops() is a helper function that recieves an ast object - of an image - ,
     the main purpose is to crop region of interests from the original images and save each cropped
     AST in a separate folder inside the CROP folder. 
    --> we can now send the Mobile the folder path and they loop through it to display each crop by itself,
        we can identify which folder they need by filtering the folders since we named them based on (time))
"""


def generate_image_crops(ast):
    # creating a directory for a single AST image to save its cropped ROIs to it.
    newDirName = 'cropped-AST-'+str(time.time())
    parentDir = app.config['CROP_FOLDER']
    newDirPath = os.path.join(parentDir, newDirName)
    os.mkdir(newDirPath)
    # for each ROI
    for index, roi in enumerate(ast.rois):
        plt.imshow(astimp_tools.image.subimage_by_roi(
            ast.crop, ast.rois[index]))
        # generate new image name
        new_image_name = 'cropped-image-'+str(index)+'.jpg'
        # generate new image path
        cropped_img_path = os.path.join(newDirPath, new_image_name)
        plt.axis('off')
        # save the new image.
        plt.savefig(cropped_img_path, pad_inches=0, bbox_inches='tight')
    return newDirPath


"""
    process_image_to_crops() takes an image as a parameter, returns a list that contains:
        for each ROI in that picture, return its 
            name, path, its center in the ROI, radius, width, and height.    
"""


def process_image_to_crops(img_name):
    # get the image from the upload folder
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
    img = imread(img_path)
    # create AST object
    ast = astimp.AST(img)
    # list data structure that will hold return data
    return_list_data = []
    # call to hepler method that takes AST object, and saves the ROIs into cropped images in the CROP folder, it returns their new directory.
    img_dir = generate_image_crops(ast)
    num_of_crops = 0
    # for each ROI in AST ROIs
    for index, roi in enumerate(ast.rois):
        # dict that contains single roi data
        roi_dict = {}
        cropped_image_name = 'cropped-image-'+str(index)+'.jpg'
        # get single antibiotic object
        atb = ast.get_atb_by_idx(index)
        # get the radius of the inhibition zone.
        radius = ((atb.inhibition.diameter)/2*ast.px_per_mm)
        roi_dict['img_name'] = cropped_image_name
        roi_dict['img_folder'] = img_dir
        roi_dict['centerX'] = atb.center_in_roi[0]
        roi_dict['centerY'] = atb.center_in_roi[1]
        roi_dict['width'] = atb.roi.width
        roi_dict['height'] = atb.roi.height
        roi_dict['inhibition_radius'] = radius
        # append the dictionary to the return list
        return_list_data.append(roi_dict)
        num_of_crops += 1
    # return both the total number of cropped images and the list of data.
    return num_of_crops, return_list_data
