import os

import tornado.web
from tornado.web import URLSpec

from handlers import ImageStyleTransferHandler, HomeHandler, ImageRealtimeStyleTransferHandler
from handlers import MobileHomeHandler
from style_transfer import load_models


class Application(tornado.web.Application):

    def __init__(self, options):
        route_table = [
            (r'/media/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "media")}),
            URLSpec(r"/", HomeHandler, name="home"),
            URLSpec(r"/mobile", MobileHomeHandler, name="mobile-home"),
            URLSpec(r"/style-transfer", ImageStyleTransferHandler, name="style-transfer"),
            URLSpec(r"/style-transfer-realtime", ImageRealtimeStyleTransferHandler, name="real-time"),
        ]
        settings = {
            "autoreload": True,
            "static_path": os.path.join(os.path.dirname(__file__), "FrontEnd"),
            "template_path": os.path.join(os.path.dirname(__file__), "templates")
        }
        super(Application, self).__init__(handlers=route_table, **settings)
        self.use_cuda = options.cuda
        self.gpu_idx = options.gpu_idx

        if self.use_cuda:
            print("Using cuda for style transfer!")
            if self.gpu_idx >= 0:
                print("Use GPU %s" % self.gpu_idx)
        self.style_transfer_models = load_models(self.use_cuda, self.gpu_idx)
        print("Model loaded")
