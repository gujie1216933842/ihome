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
            houses = ret
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
            # json_houses = json.dumps(houses)
            # 把数据保存在redis中
            try:
                self.redis.setex("home_page_data", config.HOME_PAGE_DATA_REDIS_EXPIRE_SECOND, houses)
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
            areas = ret
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
            # json_areas = json.dumps(areas)
            # 信息存入redis
            try:
                self.redis.setex("area_info", config.REDIS_AREA_INFO_EXPIRES_SECONDES, areas)
            except Exception as e:
                logging.error(e)
                return self.write(dict(code="01", msg=" get error from redis "))
        #data_info = dict(code="00", msg="ok", data=dict(houses=houses.decode(), areas=areas.decode()))
        #data = {}
        #data['houses'] = houses.decode()
        #data['areas'] = areas.decode()
        json_houses = json.dumps(houses)
        json_areas = json.dumps(areas)
        data_info = {
            "code":"00",
            "msg":"ok",
            "houses":json_houses,
            "areas":json_areas
        }
        return self.write(data_info)
