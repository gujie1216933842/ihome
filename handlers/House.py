# Author:Bob

from .BaseHandler import BaseHandler
import logging
import config
import json


class Indexhandler(BaseHandler):
    def get(self):
        '''
        首页加载信息
        1.先从redis中去取首页信息数据
        2.如果redis中没有数据,再去数据库中去取数据
        '''
        try:
            ret = self.redis.get("home_page_data")
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            json_houses = ret
        else:
            # redis中没有数据,需要去数据库中捞取
            sql = " select hi_house_id,hi_title,hi_order_count,hi_index_image_url from ih_house_info " \
                  " order by hi_order_count desc limit %s"
            try:
                house_ret = self.db.query(sql, config.HOME_PAGE_MAX_HOUSES)
            except Exception as e:
                logging.error(e)
                return self.write(dict(code="02", msg="get data error from database"))
            if not house_ret:
                # 数据中取出的数据为空
                return self.write(dict(code="03", msg="get empty from database"))
            # 成功在数据库中取出数据,遍历,如果其中一项数据为空,则加入图片
            houses = []  # 列表.append(字典) 把字典添加到列表中  ,  最终需要保存在redis中的数据(需要转成json数据)
            for value in house_ret:
                if not value['hi_index_image_url']:
                    continue
                # 如果为空  house 字典
                house = {
                    "house_id": value['hi_house_id'],
                    "title": value['hi_title'],
                    "img_url": config.qiniu_url + value['hi_index_image_url']
                }
                houses.append(house)
            # 列表转成json数据
            json_houses = json.dumps(houses)
            # 把数据保存在redis中
            try:
                self.redis.setex("home_page_data", config.HOME_PAGE_DATA_REDIS_EXPIRE_SECOND, json_houses)
            except Exception as e:
                logging.error(e)
                return self.write(dict(code="02", msg="set redis error"))
                # 成功设置redis

        # 首页城区数据
        # 在redis中取数据
        try:
            ret = self.redis.get("area_info")
        except Exception as e:
            logging.error(e)
            ret = None
        # 如果取出数据,遍历
        if ret:
            json_areas = ret
        else:
            # 如果过为空,需要在数据库中取
            sql = " select ai_area_id,ai_name from ih_area_info "
            try:
                area_ret = self.db.query(sql)
            except Exception as e:
                logging.error(e)
                area_ret = None
            areas = []
            if area_ret:
                for item in area_ret:
                    area = {
                        "area_id": item['ai_area_id'],
                        "name": item['ai_name']
                    }
                    areas.append(area)
            json_areas = json.dumps(areas)
            # 信息存入redis
            try:
                self.redis.setex("area_info", config.REDIS_AREA_INFO_EXPIRES_SECONDES, json_areas)
            except Exception as e:
                logging.error(e)
                return self.write(dict(code="01", msg=" get error from redis "))
        data_info = {
            "code": "00",
            "msg": "ok",
            "houses": json.loads(json_houses.decode()),
            "areas": json.loads(json_areas.decode())
        }
        return self.write(data_info)


class HouseInfoHandle(BaseHandler):
    '''
    房屋信息
    '''

    def post(self):
        """保存"""
        # 获取参数
        """{
            "title":"",
            "price":"",
            "area_id":"1",
            "address":"",
            "room_count":"",
            "acreage":"",
            "unit":"",
            "capacity":"",
            "beds":"",
            "deposit":"",
            "min_days":"",
            "max_days":"",
            "facility":["7","8"]
        }"""

        title = self.get_argument('title')
        price = self.get_argument('price')
        area_id = self.get_argument('area_id')
        address = self.get_argument('address')
        room_count = self.get_argument('room_count')  # 出租房间数目
        acreage = self.get_argument('acreage')  # 房屋面积
        unit = self.get_argument('unit')  # 户型描述
        capacity = self.get_argument('capacity')  # 宜住人数
        beds = self.get_argument('beds')  # 床数量
        deposit = self.get_argument('deposit')  # 押金数额
        min_days = self.get_argument('min_days')  # 最少入住天数
        max_days = self.get_argument('max_days')  # 最多入住天数
        facility = self.get_argument('facility')  # 配套设施,取出的是一个列表
        # 校验数据问题
        if not all((title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days,
                    max_days)):
            return self.write(dict(code="01", msg="参数缺失"))

        # 价格和金额先取整*100
        try:
            price = int(price) * 100
            deposit = int(deposit) * 100
        except Exception as e:
            return self.write(dict(code="02", msg="参数错误"))

        # 开始插入数据
        sql = " insert into ih_house_info (title,price,area_id,address,room_count,acreage," \
              " unit,capacity,beds,deposit,min_days,max_days) " \
              " VALUES ( %(title)s , %(price)s , %(area_id)s , %(address)s , %(room_count)s" \
              " %(acreage)s , %(unit)s , %(capacity)s , %(beds)s , %(deposit)s , " \
              " %(min_days)s , %(max_days)s )"
        try:
            house_id = self.db.excut(sql, title=title, price=price, area_id=area_id, address=address,
                                     room_count=room_count, acreage=acreage, unit=unit, capacity=capacity, beds=beds,
                                     deposit=deposit, min_days=min_days, max_days=max_days)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code="03", msg="save data error"))

        # 配套设施   插入的是ih_house_facility
        # 多条记录同时插入
        sql = " insert into ih_house_facility() VALUES "
        sql_value = []  # 用来保存(%s,%s)部分,最终的形式['(%s,%s)','(%s,%s)']
        values = []  # 用来保存具体绑定的变量值
        # 前端传到后台的facility是一个列表[],遍历列表
        for facility_id in facility:
            sql_value.append("(%s,s%)")
            values.append(house_id)
            values.append(facility_id)
        sql += ",".join(sql_value)
        values = tuple(values)
        try:
            self.db.excute(sql, values)
        except Exception as e:
            logging.error(e)
            # 执行失败,需要回滚,因为toradb.py自身没有带事务机制,需要手动回滚
            # 这里手动回滚:就是把前面成功插入的数据要删除
            try:
                self.db.excute(" delete from ih_house_info WHERE  ih_house_id = %s", house_id)
            except Exception as e:
                logging.error(e)
                return self.write(dict(code="03", msg="delete fail"))
            else:
                return self.write(dict(code="04", msg="rollback success"))

        # 两个表中的数据都插入成功,返回成功的信息
        return self.write(dict(code="00", msg="ok"))


