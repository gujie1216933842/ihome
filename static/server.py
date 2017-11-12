#Author:Bob

import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
import config

from tornado.options import define,options
from urls import urls

import



define('prot',type = int ,default=8000,help='run serve on the given port')

class Application(tornado.web.Application):
    def __init__(self,*args,**kwargs):
        super(Application,self).__init__()
        self.db = tornado.Connection(
            host = "192.168.116.128",
            database = "ihome",
            user = "root",
            password = "123"
        )

         self.redis =






def main():
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers,**config.setting
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()





















