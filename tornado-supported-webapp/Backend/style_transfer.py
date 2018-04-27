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


def load_models(use_cuda, gpu_idx=-1):
    proj_root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model_dir = os.path.join(
        proj_root_dir, "pytorch_fast-neural-style", "saved-models")
    style_models = {}
    for model_name in["mosaic", "candy", "starry-night", "udnie"]:
        style_model = TransformerNet()
        style_model_state_dict_dir = os.path.join(model_dir, "%s.pth" % model_name)
        style_model.load_state_dict(torch.load(style_model_state_dict_dir))
        if use_cuda:
            if gpu_idx >= 0:
                style_model.cuda(gpu_idx)
            else:
                style_model.cuda()
        style_models[model_name] = style_model
    return style_models


def style_transfer_from_file(style_model, filename="data/input.jpg"):
    img = Image.open(filename)
    style_tranfer(style_model, img)


def resize_image(img):
    if img.width > 1000 or img.height > 1000:
        if img.width > img.height:
            scale = 1000 / img.width
        else:
            scale = 1000 / img.height
        return img.resize((int(img.width * scale), int(img.height * scale)))
    return img


def style_tranfer(style_model, img, use_cuda, gpu_idx):
    img = resize_image(img)
    img = img.convert('RGB')
    img = np.array(img).transpose(2, 0, 1)
    img = torch.from_numpy(img).float()
    content_image = img.unsqueeze(0)
    if use_cuda:
        if gpu_idx >= 0:
            content_image = content_image.cuda(gpu_idx)
        else:
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


def handle_input_image(style_model, img, use_cuda, gpu_idx, save_to_file=True):
    start = time.time()
    img = style_tranfer(style_model, img, use_cuda, gpu_idx)
    process_time = time.time() - start
    width, height = img.size
    res = {
        "process_time": "%.3f" % process_time,
        "width": width,
        "height": height
    }
    if save_to_file:
        saved_file_name = generate_export_file_name()
        img.save("{}/{}".format(MEDIA_ROOT, saved_file_name))
        res["image_url"] = "{}/{}".format(MEDIA_URL, saved_file_name)
        return res
    else:
        return img
