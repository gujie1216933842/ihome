# Author:Bob

from .BaseHandler import BaseHandler
import logging
import config


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
                  "order by hi_order_count desc limit %s"
            try:
                ret_house = self.db.get(sql, config.HOME_PAGE_MAX_HOUSES)
            except Exception as e:
                logging.error(e)
                return self.write(dict(code = "02",msg = "get data error from database"))
            if  not  ret_house:
                #数据中取出的数据为空
                return  self.write(dict(code="03",msg="get empty from database"))
            #成功在数据库中取出数据

