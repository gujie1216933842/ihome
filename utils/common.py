# Author:Bob
''''
装饰器
'''
import functools
import logging


def require_logined(fun):
    @functools.wraps(fun)
    def wrapper(request_handler_obj, *args, **kwargs):
        # 如果get_current_user()方法返回的不是一个空字典,证明用户已经登录过,保存了用户的session数据
        logging.info('get_current_user返回的是否是空字典')
        logging.info(request_handler_obj.get_current_user())
        if  request_handler_obj.get_current_user():
            fun(request_handler_obj, *args, **kwargs)

        #返回的是空字典,代表用户未登录过,没有保存用户的session数据
        else:
            request_handler_obj.write(dict(code='aa',msg='用户未登录'))
    return wrapper



