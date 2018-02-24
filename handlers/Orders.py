from .BaseHandler import BaseHandler
import logging
import config
import json
from utils.common import require_logined
from utils.image_storage import storage
import datetime
import math
import constant


class OrderHandler(BaseHandler):
    '''提交订单接口'''

    def post(self):
        # 获取参数(提交订单的用户id,房屋id,订单开始时间,订单结束时间)
        user_id = self.session.data['user_id']
        house_id = self.json_args.get('house_id')
        start_date = self.json_args.get('start_date')
        end_date = self.json_args.get('end_date')
