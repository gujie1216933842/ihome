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

    @require_logined
    def post(self):
        # 获取参数(提交订单的用户id,房屋id,订单开始时间,订单结束时间)
        user_id = self.session.data['user_id']
        house_id = self.json_args.get('house_id')
        start_date = self.json_args.get('start_date')
        end_date = self.json_args.get('end_date')

        # 检查参数
        if not all((user_id, house_id, start_date, end_date)):
            return self.write(dict(code='01', msg="参数确实"))

        # 查看预定的房屋是否存在
        sql = " select hi_price,hi_user_id from ih_house_info where hi_house_id = %s "
        try:
            house = self.db.get(sql, house_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code="02", msg="查询预定房屋是否存在出错"))
        if not house:
            return self.write(dict(code="03", msg="数据库中无此房屋!"))

        # 检查用户预定的房屋的房东是否是自己
        if user_id == house['hi_user_id']:
            return self.write(dict(code="04", msg="该房屋是您发布的,您无法预定!"))

        # 校验结束时间是否比开始时间小
        days = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - datetime.datetime.strptime(start_date,
                                                                                              "%Y-%m-%d")).days + 1
        if days <= 0:
            return self.write(dict(code="05", msg="时间参数不对!"))
        # 判断预定的日期是否可行,(是否别的用户已经预定),需要转化为datetime比较
        sql = " select count(*) counts from ih_order_info " \
              "where oi_house_id=%(house_id)s and oi_begin_date<%(end_date)s " \
              "and oi_end_date>%(start_date)s "
        try:
            ret = self.db.get(sql, house_id=house_id, end_date=end_date, start_date=start_date)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code="06", msg="该房屋已经被人预定"))

        if ret['counts'] > 0:
            return self.write(dict(code="07", msg="serve data error"))

        amount = days * house['hi_price']

        # 开始保存订单数据
        sql = " insert into ih_order_info(oi_user_id,oi_house_id,oi_begin_date,oi_end_date,oi_days,oi_house_price,oi_amount)" \
              " values(%(user_id)s,%(house_id)s,%(begin_date)s,%(end_date)s,%(days)s,%(price)s,%(amount)s); " \
              "update ih_house_info set hi_order_count=hi_order_count+1 where hi_house_id=%(house_id)s;"
        try:
            self.db.execute(sql, user_id=user_id, house_id=house_id, begin_date=start_date, end_date=end_date,
                            days=days, price=house["hi_price"], amount=amount)
        except Exception as e:
            logging.info(e)
            return self.write(dict(code="08", msg="保存订单失败"))

        return self.write(dict(code="00", msg="ok"))
