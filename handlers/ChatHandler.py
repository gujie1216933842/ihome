from tornado.websocket import WebSocketHandler
from .BaseHandler import BaseHandler
import logging
import config
import json
from utils.common import require_logined
from utils.image_storage import storage
import datetime
import math
import constants
from utils import session

class ShowChatHandler(BaseHandler):
    def get(self):
        self.render('chat.html')

class ChatHandler(WebSocketHandler):
    users = []
    def open(self):
        for users in self.users:
            users.write_message("%s上线了"%self.request.remote_ip)
        self.users.append(self)

    def on_message(self,msg):
        for users in self.users:
            users.write_message("%s说:%s" % (self.request.remote_ip,msg))

    def on_close(self):
        self.users.remove(self)
        for users in self.users:
            users.write_message("%s下线了" % self.request.remote_ip)

    def check_origin(self,origin):
        return True  #允许Websocket的跨域请求





















