import os
import json
import base64

import concurrent.futures
from io import BytesIO
from PIL import Image

import tornado.web
import tornado.gen

from style_transfer import handle_input_image


stylizer_pool = concurrent.futures.ThreadPoolExecutor(1)


class BaseHandler(tornado.web.RequestHandler):

    def get_model(self, model_name):
        return self.application.style_transfer_models.get(model_name or "mosaic")

    @property
    def use_cuda(self):
        return self.application.use_cuda

    @property
    def gpu_idx(self):
        return self.application.gpu_idx

    def write_json(self, data):
        self.write(json.dumps(data))


class HomeHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render("index.html")


class MobileHomeHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render("index-mobile.html")


class ImageStyleTransferHandler(BaseHandler):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.future = None

    @tornado.gen.coroutine
    def post(self):
        model_name = self.get_argument("model-name", default="mosaic")
        model = self.get_model(model_name)

        content_image = self.request.files.get("content-image", None)
        if content_image is None or len(content_image) == 0:
            return self.write_error(500)
        content_image = content_image[0]
        input_im = Image.open(BytesIO(content_image.body))

        self.future = stylizer_pool.submit(
            handle_input_image,
            model,
            input_im,
            self.use_cuda,
            self.gpu_idx,
            True
        )
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET")
        response_json = yield self.future
        response_json["model-name"] = model_name

        self.write(json.dumps(response_json))


class ImageRealtimeStyleTransferHandler(BaseHandler):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.future = None

    @tornado.gen.coroutine
    def post(self):
        """
        returns images directly instead of json obj
        """
        model_name = self.get_argument("model-name", default="mosaic")
        model = self.get_model(model_name)
        content_image = self.request.files.get("content-image", None)
        if content_image is None or len(content_image) == 0:
            return self.write_error(500)
        content_image = content_image[0]
        input_im = Image.open(BytesIO(content_image.body))
        output_image = yield stylizer_pool.submit(
            handle_input_image,
            model,
            input_im,
            self.use_cuda,
            self.gpu_idx,
            False
        )
        self.set_header("Content-Type", "image/jpeg")
        self.set_header("Refresh", "1")
        self.set_header("content-transfer-encoding", "binary")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET")
        output_data = BytesIO()
        output_image.save(output_data, format="JPEG")
        self.write(base64.b64encode(output_data.getvalue()))
