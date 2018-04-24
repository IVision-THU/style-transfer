import os
import json

import concurrent.futures
from io import BytesIO
from PIL import Image

import tornado.web
import tornado.gen

from style_transfer import handle_input_image


stylizer_pool = concurrent.futures.ThreadPoolExecutor(1)


class BaseHandler(tornado.web.RequestHandler):

    @property
    def model(self):
        return self.application.style_transfer_model

    @property
    def use_cuda(self):
        return self.application.use_cuda

    def write_json(self, data):
        self.write(json.dumps(data))


class HomeHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.write("Presented by IVision\n")


class ImageStyleTransferHandler(BaseHandler):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.future = None

    @tornado.gen.coroutine
    def post(self):
        content_image = self.request.files.get("content-image", None)
        if content_image is None or len(content_image) == 0:
            return self.write_error(500)
        content_image = content_image[0]
        input_im = Image.open(BytesIO(content_image.body))
        self.future = stylizer_pool.submit(
            handle_input_image,
            self.model,
            input_im,
            self.use_cuda,
            True
        )
        response_json = yield self.future
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
        content_image = self.request.files.get("content-image", None)
        if content_image is None or len(content_image) == 0:
            return self.write_error(500)
        content_image = content_image[0]
        input_im = Image.open(BytesIO(content_image.body))
        output_image = yield stylizer_pool.submit(
            handle_input_image,
            self.model,
            input_im,
            self.use_cuda,
            False
        )
        self.set_header("Content-Type", "image/jpeg")
        self.set_header("Refresh", "1")
        self.set_header("content-transfer-encoding", "binary")
        output_data = BytesIO()
        output_image.save(output_data, format="JPEG")
        self.write(output_data.getvalue())
