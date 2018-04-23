from flask import Flask, render_template, request
from .app import app
import re
# from pixel_image import pixelate_image, generate_pixel_image, classify_face, atkinson_dither
from .pixel_image import generate_pixel_image, classify_face, atkinson_dither
from .style_transfer import transfer_image
from PIL import Image, ImageChops, ImageOps
import base64
from io import BytesIO

import argparse
import os
import sys
import time

import numpy as np
import torch
from torch.autograd import Variable
from torch.optim import Adam
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision import transforms

import style_transfer_tools.utils as utils
from style_transfer_tools.transformer_net import TransformerNet
from style_transfer_tools.vgg16 import Vgg16

USE_CUDA = True
style_model = TransformerNet()
style_model.load_state_dict(torch.load("/home/zhouxx/style-transfer/pytorch_fast-neural-style/saved-models/mosaic.pth"))

if USE_CUDA:
    style_model.cuda()


def base64_to_PIL_image(base64_img):
    return Image.open(BytesIO(base64.b64decode(base64_img)))


def PIL_image_to_base64(pil_image):
    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue())


def stylize(img):
    img = base64_to_PIL_image(img)
    img = img.convert('RGB')
    img = np.array(img).transpose(2, 0, 1)
    img = torch.from_numpy(img).float()
    content_image = img.unsqueeze(0)
    if USE_CUDA:
        content_image = content_image.cuda()

    output = style_model(content_image)
    output = output.data[0]
    if USE_CUDA:
        img = output.clone().cpu().clamp(0, 255).numpy()
    else:
        img = output.clone().clamp(0, 255).numpy()
    img = img.transpose(1, 2, 0).astype('uint8')
    img = Image.fromarray(img)
    return PIL_image_to_base64(img)



hex_list = []
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/face_streaming')
def face_streaming():
    return render_template('face_classify_stream.html')

@app.route('/face_classify')
def face_classify():
    return render_template('face_classify.html')


@app.route('/test')
def test():
    return render_template('testpage.html')


@app.route('/test2')
def test2():
    return render_template('testpage_2.html')


@app.route('/focus', methods=['POST','GET'])
def focus():
    if request.method == 'POST':
        hex_list.append('#')
    else:
        if len(hex_list) != 0:
            hex_list.pop()

    hex_string = ' '.join(hex_list)
    if len(hex_list) == 0:
        hex_string = 'dead'
    return hex_string


@app.route('/process', methods=['POST'])
def process():
    input = request.json
    image_data = re.sub('^data:image/.+;base64,', '', input['img'])
    # # image_ascii = atkinson_dither(image_data)
    # image_ascii = transfer_image(image_data)
    image_ascii = stylize(image_data)
    return image_ascii


@app.route('/classify', methods=['POST'])
def classify():
    input = request.json
    image_data = re.sub('^data:image/.+;base64,', '', input['img'])
    image_ascii = classify_face(image_data)
    return image_ascii
