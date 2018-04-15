#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
author: Zhou Xiangxin
time: 2018/4/14

"""
import subprocess
import os
import base64
from PIL import Image, ImageChops, ImageOps
import base64
from io import BytesIO


def base64_to_PIL_image(base64_img):
    return Image.open(BytesIO(base64.b64decode(base64_img)))


def PIL_image_to_base64(pil_image):
    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue())


def transfer_image(img_string):
    # cv2.imwrite('src.jpg', img)
    image = base64_to_PIL_image(img_string)
    image = image.convert('RGB')
    image.save('src.jpg')
    cu_dir = os.getcwd()
    os.chdir('/home/zhouxx/style-transfer/fast-neural-style')
    subprocess.call("bash run.sh", shell=True)
    os.chdir(cu_dir)
    # cv2.imread('out.png')
    # byte_string = cv2.imencode('.png', opencvImage)[1]
    # output = base64.b64encode(byte_string)
    image = Image.open('out.png')
    return PIL_image_to_base64(image)

