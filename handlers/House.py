# Author:Bob

from .BaseHandler import BaseHandler
import logging
import config
import json
from utils.common import require_logined
from utils.image_storage import storage


class MyHouseHandler(BaseHandler):
    '''
    先在session中查询用户的用户id
    再通过userid去数据库中查询用户的房屋信息
    '''

    @require_logined
    def get(self):
        user_id = self.session.data['user_id']
        sql = "select a.hi_house_id,a.hi_title,a.hi_price,a.hi_ctime,b.ai_name,a.hi_index_image_url " \
              "from ih_house_info a inner join ih_area_info b on a.hi_area_id=b.ai_area_id where a.hi_user_id=%s"
        try:
            ret = self.db.query(sql, user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code="01", msg=" get error from database "))
        # 如果能取出数据
        houses = []
        if ret:
            for house in ret:
                houses.append({
                    "house_id": house["hi_house_id"],
                    "title": house["hi_title"],
                    "price": house["hi_price"],
                    "ctime": house["hi_ctime"],  # 将返回的Datatime类型格式化为字符串
                    "area_name": house["ai_name"],
                    "img_url": config.qiniu_url + house["hi_index_image_url"] if house["hi_index_image_url"] else ""
                })
        return self.write(dict(code="00", msg="ok", data=houses))


class HouseImageHandler(BaseHandler):
    @require_logined
    def post(self, *args, **kwargs):
        '''
        我的房屋图像上传接口
        '''
        # 接受上传的数据
        house_id = self.get_argument("house_id")
        logging.info("house_id: %s" % (house_id))
        try:
            image_data = self.request.files['house_image'][0]['body']
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='01', msg='前端向后台传输图片失败'))
        # 如果后台接收到图片数据,把图片数据作为参数传递给封装好的七牛接口
        try:
            key = storage(image_data)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code='02', msg="向七牛传递数据出错"))
        # 七牛上传图片成功,拿到返回的key,把key保存到数据库
        # 两步操作,也要用到数据库回滚
        # 1.在ih_house_image表中插入每一张的图片信息
        sql = " insert into ih_house_image ( hi_house_id,hi_url,hi_ctime) VALUES (%(house_id)s,%(url)s,now())"
        try:
            image_id = self.db.execute_rowcount(sql, house_id=house_id, url=key)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code="03", msg="表ih_house_image插入数据失败"))
        logging.info("表ih_house_image数据插入成功")
        # 表ih_house_info中的hi_index_image_url字段(房屋的主图片)插入数据
        sql = " update ih_house_info set hi_index_image_url = %s where hi_house_id = %s and hi_index_image_url = '' "
        try:
            logging.info("开始更新表ih_house_info里的hi_index_image_url字段")
            self.db.execute(sql, key, house_id)
        except Exception as e:
            logging.error(e)
            logging.info("表ih_house_info表图片字段insert failed  , rollback begin")
            # 开始把第一次插入的数据删除
            try:
                self.db.execute(" delete from ih_house_image where hi_image_id = %s ", image_id)
            except Exception as e:
                logging.error(e)
                logging.info(" rollback failed ,删除失败! ")
                return self.write(dict(code="04", msg="rollback 失败"))
            else:
                logging.info(" rollback success! ")
        return self.write(dict(code="00", msg="ok", data="%s%s" % (config.qiniu_url, key)))


class AreaInfoHandler(BaseHandler):
    def get(self):
        '''
        先到redis中取出数据,如果有数据,直接返回给前端,如果没有数据,就在数据库中去取,取出数据后,存在redis中,方便下次再取,返回给前端
        :return:
        '''
        try:
            ret = self.redis.get("area_info")
        except Exception as e:
            logging.error(e)
            ret = None
        # 如果能取到数据(数据存在)
        if ret:
            logging.info(" hit redis: area_info ")
            resp = {
                "code": "00",
                "msg": "ok",
                "data": json.loads(ret.decode())
            }
            return self.write(resp)

        # 如果redis中数据为空,需要去数据库中去取
        sql = " select ai_area_id,ai_name from ih_area_info "
        try:
            ret = self.db.query(sql)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code="01", msg="get error from database"))
        if not ret:
            return self.write(dict(code="02", msg="get no data from database"))

        # 成功取出数据,转换数据
        areas = []
        for area in ret:
            areas.append(dict(area_id=area['ai_area_id'], name=area['ai_name']))

        # 在给用户返回数据之前,先在redis中保存一下副本
        json_areas = json.dumps(areas)
        try:
            self.redis.setex("area_info", config.REDIS_AREA_INFO_EXPIRES_SECONDES, json_areas)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code="03", msg="set redis error"))
        return self.write(dict(code="00", msg="ok", data=areas))


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

    @require_logined
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

        title = self.json_args.get('title')
        price = self.json_args.get('price')
        area_id = self.json_args.get('area_id')
        address = self.json_args.get('address')
        room_count = self.json_args.get('room_count')  # 出租房间数目
        acreage = self.json_args.get('acreage')  # 房屋面积
        unit = self.json_args.get('unit')  # 户型描述
        capacity = self.json_args.get('capacity')  # 宜住人数
        beds = self.json_args.get('beds')  # 床数量
        deposit = self.json_args.get('deposit')  # 押金数额
        min_days = self.json_args.get('min_days')  # 最少入住天数
        max_days = self.json_args.get('max_days')  # 最多入住天数
        facility = self.json_args.get('facility')  # 配套设施,取出的是一个列表
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
        # 在session中获取用户id
        user_id = self.session.data['user_id']
        # 开始插入数据
        sql = " insert into ih_house_info (hi_title,hi_price,hi_area_id,hi_address,hi_room_count,hi_acreage," \
              " hi_house_unit,hi_capacity,hi_beds,hi_deposit,hi_min_days,hi_max_days,hi_user_id) " \
              " VALUES ( %(title)s , %(price)s , %(area_id)s , %(address)s , %(room_count)s," \
              " %(acreage)s , %(unit)s , %(capacity)s , %(beds)s , %(deposit)s , " \
              " %(min_days)s , %(max_days)s ,%(user_id)s)"
        try:
            house_id = self.db.execute(sql, title=title, price=price, area_id=area_id, address=address,
                                       room_count=room_count, acreage=acreage, unit=unit, capacity=capacity, beds=beds,
                                       deposit=deposit, min_days=min_days, max_days=max_days, user_id=user_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code="03", msg="save data error"))
        logging.info("ih_house_info  insert success!")

        # 配套设施   插入的是ih_house_facility
        # 多条记录同时插入
        sql = " insert into ih_house_facility( hf_house_id , hf_facility_id ) VALUES "
        sql_value = []  # 用来保存(%s,%s)部分,最终的形式['(%s,%s)','(%s,%s)']
        values = []  # 用来保存具体绑定的变量值
        # 前端传到后台的facility是一个列表[],遍历列表
        for facility_id in facility:
            sql_value.append("(%s,%s)")
            values.append(house_id)
            values.append(facility_id)
        sql += ",".join(sql_value)  # 把列表中的字符串元素用","拼接在一起
        values = tuple(values)  # 把列表数据转换成元组数据
        logging.info("sql语句: %s" % (sql))
        try:
            self.db.execute(sql, *values)
        except Exception as e:
            logging.error(e)
            logging.info("rollback begin!")
            # 执行失败,需要回滚,因为toradb.py自身没有带事务机制,需要手动回滚
            # 这里手动回滚:就是把前面成功插入的数据要删除
            try:
                self.db.execute(" delete from ih_house_info WHERE  hi_house_id = %s", house_id)
            except Exception as e:
                logging.error(e)
                return self.write(dict(code="03", msg="delete failed , rollback failed"))
            else:
                return self.write(dict(code="04", msg="rollback success"))
        logging.info(" ih_house_facility insert fail ")
        # 两个表中的数据都插入成功,返回成功的信息
        return self.write(dict(code="00", msg="ok", house_id=house_id))

    def get(self):
        '''
        获取房屋信息
        :return:
        '''
        # 获取user_id 和 house_id 作为参数信息, user_id 在session中取,house_id在get参数上获取
        user_id = self.session.data['user_id']
        house_id = self.get_argument('house_id')
        logging.info("用户id: %s" % (user_id))
        logging.info("房屋id: %s" % (house_id))

        # 校验参数
        if not house_id:
            return self.write(dict(code="01", msg="参数缺失"))
        # 先从redis中获取缓存信息
        try:
            ret = self.redis.get("house_info_%s" % (house_id))
            logging.info("redis中捞取的结果:%s" % (ret))
        except Exception as e:
            logging.error(e)
            # return  self.write(dict(code="02",msg="get error from redis"))
            ret = None
            # 把获取到的房屋信息数据返回给前端
            resp = '{"errcode":"0", "errmsg":"OK", "data":%s, "user_id":%s}' % (ret, user_id)
            return self.write(resp)

        # 如果redis中没有数据,则需要去查看数据库 (连表)
        logging.info("redis中没有数据,需要去数据库中查询")
        sql = "select hi_title,hi_price,hi_address,hi_room_count,hi_acreage,hi_house_unit,hi_capacity,hi_beds," \
              "hi_deposit,hi_min_days,hi_max_days,up_name,up_avatar,hi_user_id " \
              "from ih_house_info inner join ih_user_profile on hi_user_id=up_user_id where hi_house_id=%s "
        try:
            ret = self.db.get(sql, house_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(code="03", msg="get error from database"))

        if not ret:
            return self.write(dict(code="04", msg="查无此房"))

        # 查出有数据
        data = {
            "hid": house_id,
            "user_id": ret["hi_user_id"],
            "title": ret["hi_title"],
            "price": ret["hi_price"],
            "address": ret["hi_address"],
            "room_count": ret["hi_room_count"],
            "acreage": ret["hi_acreage"],
            "unit": ret["hi_house_unit"],
            "capacity": ret["hi_capacity"],
            "beds": ret["hi_beds"],
            "deposit": ret["hi_deposit"],
            "min_days": ret["hi_min_days"],
            "max_days": ret["hi_max_days"],
            "user_name": ret["up_name"],
            "user_avatar": config.qiniu_url + ret["up_avatar"] if ret.get("up_avatar") else ""
        }

        # 查询房屋的图片信息

        sql = " select hi_url from ih_house_image where hi_house_id = %s "
        try:
            ret = self.db.query(sql, house_id)
        except Exception as e:
            logging.error(e)
            ret = None

        # 成功取到图片信息
        images = []
        if ret:
            for image in ret:
                images.append(config.qiniu_url + image['hi_url'])
        data['images'] = images

        # 查询房屋的基本设施
        sql = " select hf_facility_id from ih_house_facility where hf_house_id = %s "
        try:
            ret = self.db.query(sql, house_id)
        except Exception as e:
            logging.error(e)
            ret = None

        # 如果查到基本设施信息
        facilitys = []
        if ret:
            for facility in ret:
                facilitys.append(facility['hf_facility_id'])
        data['facilitys'] = facilitys

        # 查询评论信息
        sql = "select oi_comment,up_name,oi_utime,up_mobile from ih_order_info inner join ih_user_profile " \
              "on oi_user_id=up_user_id where oi_house_id=%s and oi_status=4 and oi_comment is not null"

        try:
            ret = self.db.query(sql, house_id)
        except Exception as e:
            logging.error(e)
            ret = None
        # 如果查询到评论信息
        comments = []
        if not ret:
            for comment in comments:
                comments.append(dict(
                    user_name=comment['up_name'] if comment['up_name'] != comment['up_mobile'] else "匿名用户",
                    content=comment['oi_comment'],
                    ctime=comment['oi_utime'].stftime["%Y-%m-%d %H:%M:%S"]
                ))

        data['comments'] = comments

        # 存入redis
        json_data = json.dumps(data)
        try:
            self.redis.setex("house_info_%s" % (house_id), config.REDIS_HOUSE_INFO_EXPIRES_SECONDES, json_data)
        except Exception as e:
            logging.error(e)
        resp = '{"errcode":"0", "errmsg":"OK", "data":%s, "user_id":%s}' % (json_data, user_id)
        self.write(resp)
