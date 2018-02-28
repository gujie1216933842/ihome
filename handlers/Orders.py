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
        sql1 = " insert into ih_order_info(oi_user_id,oi_house_id,oi_begin_date,oi_end_date,oi_days,oi_house_price,oi_amount,oi_ctime)" \
               " values(%(user_id)s,%(house_id)s,%(begin_date)s,%(end_date)s,%(days)s,%(price)s,%(amount)s,now()) "
        sql2 = " update ih_house_info set hi_order_count=hi_order_count+1 where hi_house_id=%(house_id)s "
        # 第一步订单表插入数据
        try:
            order_id = self.db.execute_rowcount(sql1, user_id=user_id, house_id=house_id, begin_date=start_date,
                                                end_date=end_date,
                                                days=days, price=house["hi_price"], amount=amount)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code="08", msg="ih_order_info表插入数据失败"))
        # 第二步房屋信息表更新数据
        try:
            self.db.execute(sql2, house_id=house_id)
        except Exception as e:
            logging.error(e)
            logging.info("ih_house_info表更新失败,rollback begin")
            try:
                self.db.execute(" delete from ih_order_info where oi_order_id = %s ", order_id)
            except Exception as e:
                logging.error(e)
                return self.write(dict(code="09", msg="rollback failed"))
        return self.write(dict(code="00", msg="ok"))


class OrderListHandler(BaseHandler):
    """我的订单"""

    @require_logined
    def get(self):
        user_id = self.session.data["user_id"]

        # 用户的身份，用户想要查询作为房客下的单，还是想要查询作为房东 被人下的单
        role = self.get_argument("role", "")
        try:
            # 查询房东订单
            if "landlord" == role:
                ret = self.db.query("select oi_order_id,hi_title,hi_index_image_url,oi_begin_date,oi_end_date,oi_ctime,"
                                    "oi_days,oi_amount,oi_status,oi_comment from ih_order_info inner join ih_house_info "
                                    "on oi_house_id=hi_house_id where hi_user_id=%s order by oi_ctime desc", user_id)
            else:
                ret = self.db.query("select oi_order_id,hi_title,hi_index_image_url,oi_begin_date,oi_end_date,oi_ctime,"
                                    "oi_days,oi_amount,oi_status,oi_comment from ih_order_info inner join ih_house_info "
                                    "on oi_house_id=hi_house_id where oi_user_id=%s order by oi_ctime desc", user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"code": "00", "msg": "get data error"})
        orders = []
        if ret:
            for l in ret:
                order = {
                    "order_id": l["oi_order_id"],
                    "title": l["hi_title"],
                    "img_url": config.qiniu_url + l["hi_index_image_url"] if l["hi_index_image_url"] else "",
                    "start_date": l["oi_begin_date"].strftime("%Y-%m-%d"),
                    "end_date": l["oi_end_date"].strftime("%Y-%m-%d"),
                    "ctime": l["oi_ctime"].strftime("%Y-%m-%d"),
                    "days": l["oi_days"],
                    "amount": l["oi_amount"],
                    "status": l["oi_status"],
                    "comment": l["oi_comment"] if l["oi_comment"] else ""
                }
                orders.append(order)
        self.write({"code": "00", "msg": "ok", "orders": orders})


class AcceptOrderHandler(BaseHandler):
    """接单"""

    @require_logined
    def post(self):
        # 处理的订单编号
        order_id = self.json_args.get("order_id")
        user_id = self.session.data["user_id"]
        if not order_id:
            return self.write({"code": "01", "msg": "params error"})

        try:
            # 确保房东只能修改属于自己房子的订单
            self.db.execute("update ih_order_info set oi_status=3 where oi_order_id=%(order_id)s and oi_house_id in "
                            "(select hi_house_id from ih_house_info where hi_user_id=%(user_id)s) and oi_status=0",
                            # update ih_order_info inner join ih_house_info on oi_house_id=hi_house_id set oi_status=3 where
                            # oi_order_id=%(order_id)s and hi_user_id=%(user_id)s
                            order_id=order_id, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"code": "02", "msg": "DB error"})
        self.write({"code": "00", "msg": "OK"})


class RejectOrderHandler(BaseHandler):
    """拒单"""

    @require_logined
    def post(self):
        user_id = self.session.data["user_id"]
        order_id = self.json_args.get("order_id")
        reject_reason = self.json_args.get("reject_reason")
        if not all((order_id, reject_reason)):
            return self.write({"code": "01", "msg": "params error"})
        try:
            self.db.execute("update ih_order_info set oi_status=6,oi_comment=%(reject_reason)s "
                            "where oi_order_id=%(order_id)s and oi_house_id in (select hi_house_id from ih_house_info "
                            "where hi_user_id=%(user_id)s) and oi_status=0",
                            reject_reason=reject_reason, order_id=order_id, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"code": "02", "msg": "DB error"})
        self.write({"code": "00", "msg": "OK"})


class OrderCommentHandler(BaseHandler):
    """评论"""

    @require_logined
    def post(self):
        user_id = self.session.data["user_id"]
        order_id = self.json_args.get("order_id")
        comment = self.json_args.get("comment")
        if not all((order_id, comment)):
            return self.write({"code": "01", "msg": "params error"})
        try:
            # 需要确保只能评论自己下的订单
            self.db.execute(
                "update ih_order_info set oi_status=4,oi_comment=%(comment)s where oi_order_id=%(order_id)s "
                "and oi_status=3 and oi_user_id=%(user_id)s", comment=comment, order_id=order_id, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"code": "02", "msg": "DB error"})

        # 同步更新redis缓存中关于该房屋的评论信息，此处的策略是直接删除redis缓存中的该房屋数据
        try:
            ret = self.db.get("select oi_house_id from ih_order_info where oi_order_id=%s", order_id)
            if ret:
                self.redis.delete("house_info_%s" % ret["oi_house_id"])
        except Exception as e:
            logging.error(e)
        self.write({"code": "00", "msg": "OK"})



