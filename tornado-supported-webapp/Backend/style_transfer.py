import os
import uuid
import time

import torch
import numpy as np
from PIL import Image
from style_transfer_tools.transformer_net import TransformerNet

MEDIA_URL = "/media"
MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), "media")


def generate_export_file_name(filename=None, ext="jpg"):
    if filename is not None:
        ext = filename.split(".")[-1]
    random_file_name = str(uuid.uuid4())
    return "%s.%s" % (random_file_name, ext)


def load_model(use_cuda):
    style_model = TransformerNet()
    proj_root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    style_model_state_dict_dir = os.path.join(
        proj_root_dir, "pytorch_fast-neural-style", "saved-models", "mosaic.pth")
    style_model.load_state_dict(torch.load(style_model_state_dict_dir))
    if use_cuda:
        style_model.cuda()
    return style_model


def style_transfer_from_file(style_model, filename="data/input.jpg"):
    img = Image.open(filename)
    style_tranfer(style_model, img)


def style_tranfer(style_model, img, use_cuda):
    img = img.convert('RGB')
    img = np.array(img).transpose(2, 0, 1)
    img = torch.from_numpy(img).float()
    content_image = img.unsqueeze(0)
    if use_cuda:
        content_image = content_image.cuda()

    output = style_model(content_image)
    output = output.data[0]
    if use_cuda:
        img = output.clone().cpu().clamp(0, 255).numpy()
    else:
        img = output.clone().clamp(0, 255).numpy()
    img = img.transpose(1, 2, 0).astype('uint8')
    img = Image.fromarray(img)
    return img


def handle_input_image(style_model, img, use_cuda, save_to_file=True):
    width, height = img.size
    start = time.time()
    img = style_tranfer(style_model, img, use_cuda)
    process_time = time.time() - start

    res = {"process_time": process_time}
    if save_to_file:
        saved_file_name = generate_export_file_name()
        img.save("{}/{}".format(MEDIA_ROOT, saved_file_name))
        res["image_url"] = "{}/{}".format(MEDIA_URL, saved_file_name)
        return res
    else:
        return img
