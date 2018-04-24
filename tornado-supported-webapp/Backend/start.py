import logging

import tornado.ioloop
import tornado.httpserver
from tornado.options import options, define

from app import Application


define("port", default=8000, help="run on given port", type=int)
define("cuda", default=False, help="use cuda for style transfer", type=bool)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application(options))
    server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
