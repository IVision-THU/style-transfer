import os

import tornado.web
from tornado.web import URLSpec

from handlers import ImageStyleTransferHandler, HomeHandler, ImageRealtimeStyleTransferHandler
from style_transfer import load_model

class Application(tornado.web.Application):

    def __init__(self):
        route_table = [
            URLSpec(r"/", HomeHandler, name="home"),
            URLSpec(r"/style-transfer", ImageStyleTransferHandler, name="style-transfer"),
            URLSpec(r"/style-transfer-realtime", ImageRealtimeStyleTransferHandler, name="real-time")
        ]
        settings = {
            "autoreload": True,
            "static_path": os.path.join(os.path.dirname(__file__), "media"),
            "template_path": os.path.join(os.path.dirname(__file__), "templates")
        }
        super(Application, self).__init__(handlers=route_table, **settings)
        self.style_transfer_model = load_model(False)
