import base64
import operator
import os
import re
from collections import defaultdict
from functools import reduce
from io import BytesIO
from random import choice, randint, shuffle

# from nltk import FreqDist
from PIL import Image, ImageChops, ImageOps

import cv2
import numpy as np

basedir = os.path.abspath(os.path.dirname(__file__))
face_xml = os.path.join(basedir,'static','data', 'haarcascade_frontalface_alt.xml')
eye_xml = os.path.join(basedir,'static','data', 'haarcascade_eye_tree_eyeglasses.xml')
face_cascade = cv2.CascadeClassifier(face_xml)
eye_cascade = cv2.CascadeClassifier(eye_xml)


#reference: https://stackoverflow.com/questions/31826335/how-to-convert-pil-image-image-object-to-base64-string
def PIL_image_to_base64(pil_image):
    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue())


def base64_to_PIL_image(base64_img):
    return Image.open(BytesIO(base64.b64decode(base64_img)))

def atkinson_dither(image_string):
    image = base64_to_PIL_image(image_string)
    image = image.convert('L')
    pix = image.load()
    w, h = image.size
    for y in range(h):
        for x in range(w):
            old = pix[x, y]
            new = 0 if old < 127 else 255
            pix[x, y] = new
            quant_error = old - new
            if x < w - 1:
                pix[x + 1, y] += quant_error * 1 // 8
            if x < w - 2:
                pix[x + 2, y] += quant_error * 1 // 8
            if x > 0 and y < h - 1:
                pix[x - 1, y + 1] += quant_error * 1 // 8
            if y < h - 1:
                pix[x, y + 1] += quant_error * 1 // 8
            if y < h - 2:
                pix[x, y + 2] += quant_error * 1 // 8
            if x < w - 1 and y < h - 1:
                pix[x + 1, y + 1] += quant_error * 1 // 8

    if w > 1024 or h > 512:
        image = ImageOps.scale(image, 0.75)
    return PIL_image_to_base64(image)

# def pixelate_image(img_string):
#     image = base64_to_PIL_image(img_string)
#     img_data = list(image.getdata())
#     freq_dist = FreqDist(img_data)
#     top_1_colour = freq_dist.most_common(1)[0][0]
#     backgroundColor = top_1_colour
#     pixelSize = 9
#     image = image.resize(
#         (int(image.size[0] / pixelSize), int(image.size[1] / pixelSize)), Image.ANTIALIAS)
#     image = image.resize(
#         (image.size[0] * pixelSize, image.size[1] * pixelSize), Image.ANTIALIAS)
#     pixel = image.load()
#     for i in range(0, image.size[0], pixelSize):
#         for j in range(0, image.size[1], pixelSize):
#             for r in range(pixelSize):
#                 pixel[i + r, j] = backgroundColor
#                 pixel[i, j + r] = backgroundColor
#
#     return PIL_image_to_base64(image)


def generate_pixel_image(image_string):
    '''
    https://stackoverflow.com/questions/30520666/pixelate-image-with-pillow

    '''
    block_size = 16
    size = (block_size, block_size)
    image = base64_to_PIL_image(image_string)
    im = image.convert('RGB')
    img_data = list(im.getdata())
    freq_dist = FreqDist(set(img_data))
    most_common = freq_dist.most_common(256)
    palette = []
    for colour in most_common:
        palette.append(colour[0])
    while len(palette) < 256:
        palette.append((0, 0, 0))
    try:
        flat_palette = reduce(lambda a, b: a + b, palette)
        assert len(flat_palette) == 768
        palette_img = Image.new('P', (1, 1), 0)
        palette_img.putpalette(flat_palette)
        multiplier = 8
        scaled_img = im.resize(
            (size[0] * multiplier, size[1] * multiplier), Image.ANTIALIAS)
        reduced_img = scaled_img.quantize(palette=palette_img)
        rgb_img = reduced_img.convert('RGB')
        out = Image.new('RGB', size)
        for x in range(size[0]):
            for y in range(size[1]):
                #sample and get average color in the corresponding square
                histogram = defaultdict(int)
                for x2 in range(x * multiplier, (x + 1) * multiplier):
                    for y2 in range(y * multiplier, (y + 1) * multiplier):
                        histogram[rgb_img.getpixel((x2, y2))] += 1
                color = max(histogram.items(), key=operator.itemgetter(1))[0]
                out.putpixel((x, y), color)

        new_file = ImageOps.scale(out, 50)
        print("pixe_image done")
        output = PIL_image_to_base64(new_file)
    #https://docs.python.org/3/tutorial/errors.html
    except Exception as inst:
        print(type(inst))
        print(inst.args)
        output = image_string
    return output

def classify_face(image_string):
        # convert it to a pil image
        pil_image = base64_to_PIL_image(image_string)
        # PIL image -> OpenCV image
        opencvImage = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
       
        gray = cv2.cvtColor(opencvImage, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray,
                                      scaleFactor=1.1,
                                      minNeighbors=2,
                                      minSize=(50, 50),
                                      flags=cv2.CASCADE_SCALE_IMAGE)
    
        font = cv2.FONT_HERSHEY_SIMPLEX
        for (x, y, w, h) in faces:
            cv2.rectangle(opencvImage, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = opencvImage[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray,
                                        scaleFactor=1.1,
                                        minNeighbors=2,
                                        flags=cv2.CASCADE_SCALE_IMAGE)
                                    
            if(not len(eyes)):
                cv2.putText(roi_color, 'Sleeping', (20, 20), font,
                            1, (255, 255, 255), 2, cv2.LINE_AA)
            else:
                cv2.putText(roi_color, 'Awake', (20, 20), font,
                            1, (255, 255, 255), 2, cv2.LINE_AA)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
        byte_string = cv2.imencode('.png', opencvImage)[1]
        output = base64.b64encode(byte_string)

        return output
