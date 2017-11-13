# Author:Bob

import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
import os
import config
import redis

from handlers import Passport
from tornado.options import define, options
from urls import urls

define('prot', default=8000, type=int, help='run serve on the given port')


class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__()
        self.db = tornado.Connection(**config.mysql_options)
        self.db = tornado.Connection(**config.redis_options)

        '''self.db = tornado.Connection(
            host = config.mysql_options['host'],
            database = config.mysql_options['database'],
            user = config.mysql_options['user'],
            password = config.mysql_options['password'],
            
        )'''

        """ self.redis = redis.StrictRedis(
                 host=config.redis_options['host'],
                 port = config.redis_options['port'],
             )
           
        """


def main():
    options.log_file_prefix = config.log_path
    options.logging = config.log_level
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        urls, **config.setting
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
