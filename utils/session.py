# Author:Bob
import uuid  # UUID是128位的全局唯一标识符，通常由32字节的字母串表示。它可以保证时间和空间的唯一性，也称为GUID。
import json
import logging
import config


class Session(object):
    def __init__(self, request_handler_object):
        # 先判断用户是否有session_id
        self._request_handler = request_handler_object
        self.session_id = request_handler_object.get_secure_cookie('session_id')

        # 如果没有session_id则生成session_id,
        if not self.session_id:
            self.session_id = uuid.uuid4().hex
            self.data = {}
            request_handler_object.set_secure_cookie('session_id', self.session_id)

        # 如果存在session_id就去redis中去取出data
        else:
            try:
                json_data = request_handler_object.redis.get("sess_" + self.session_id.decode())
            # 取redis过程出错
            except Exception as e:
                logging.error(e)
                raise e
            # 如果取出的redis中的值为空
            if not json_data:
                self.data = {}
            else:
                # 可以顺利在redis中取到想要的值
                self.data = json.loads(json_data.decode())  # 将redis中的数据序列化

    def save(self):
        '''
        保存session方法
        :return:
        '''

        # 先把数据序列化成json字符串
        json_data = json.dumps(self.data)
        logging.info('需要保存的session对象:' + json_data)
        try:
            self._request_handler.redis.setex("sess_" + self.session_id.decode(), config.session_expires, json_data)
        except Exception as e:
            logging.error(e)
            raise e

    def clear(self):
        '''
        清楚session方法
        :return:
        '''
        try:
            self._request_handler.redis.delete("sess_%s" % (self.session_id))
        except Exception as e:
            logging.error(e)
            raise e
        self._request_handler.clear_cookie('session_id')
