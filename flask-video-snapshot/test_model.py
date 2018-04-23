import os
import time

import torch
import numpy as np
from PIL import Image
from style_transfer_tools.transformer_net import TransformerNet

USE_CUDA = False


def load_model(use_cuda):
    style_model = TransformerNet()
    proj_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    style_model_state_dict_dir = os.path.join(
        proj_root_dir, "pytorch_fast-neural-style", "saved-models", "mosaic.pth")
    style_model.load_state_dict(torch.load(style_model_state_dict_dir))
    if use_cuda:
        style_model.cuda()
    return style_model


def main(filename="data/input.jpg"):
    style_model = load_model(USE_CUDA)

    img = Image.open(filename)
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
    img.save("data/output.jpg")


if __name__ == '__main__':
    main()
