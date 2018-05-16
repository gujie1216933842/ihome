from tornado.websocket import WebSocketHandler
from .BaseHandler import BaseHandler
import time


class ShowChatHandler(BaseHandler):
    def get(self):
        self.render('chat.html')


class ChatHandler(WebSocketHandler):
    users = []

    def open(self):
        for users in self.users:
            users.write_message("[%s]-[%s]-进入聊天室" % (
            self.request.remote_ip, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
        self.users.append(self)

    def on_message(self, msg):
        for users in self.users:
            users.write_message("[%s]-[%s]-说: %s" % (
                self.request.remote_ip, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), msg))

    def on_close(self):
        self.users.remove(self)
        for users in self.users:
            users.write_message("[%s]-[%s]-离开聊天室" % (
            self.request.remote_ip, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))

    def check_origin(self, origin):
        return True  # 允许Websocket的跨域请求
