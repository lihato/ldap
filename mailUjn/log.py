# -*- coding: utf-8 -*-
"""
Project: 智慧校园
Creator: Lihaitao
Create time: 2023-07-06 15:49
Introduction: 网易邮箱接口

"""
import logging
import logging.config

standard_format = '%(asctime)s %(name)s [%(levelname)s][%(thread)d] %(message)s'
simple_format = '%(asctime)s [%(thread)d] %(name)s [%(levelname)s] %(message)s'
test_format = '%(asctime)s] [%(levelname)s] %(name)s[%(thread)d] %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'
LOGGING_DIC = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': standard_format,
            'datefmt': datefmt
        },
        'simple': {
            'format': simple_format,
            'datefmt': datefmt
        },
        'test': {
            'format': test_format,
            'datefmt': datefmt
        },
    },
    'filters': {},
    'handlers': {
        # 打印到终端的日志
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',  # 打印到屏幕
            'formatter': 'simple'
        },
        # 打印到文件的日志,收集info及以上的日志
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件,日志轮转
            'formatter': 'standard',
            # 可以定制日志文件路径
            # BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # log文件的目录
            # LOG_PATH = os.path.join(BASE_DIR,'a1.log')
            'filename': './mailujn.log',  # 日志文件
            'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
            'backupCount': 3,
            'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
        },
        'other': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件,日志轮转
            'formatter': 'test',
            'filename': './mailujn-debug.log',
            'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
            'backupCount': 3,
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        # logging.getLogger(__name__)拿到的logger配置
        'mailUjn': {
            'handlers': ['default'],  # 这里把上面定义的两个handler都加上，即log数据既写入文件又打印到屏幕
            'level': 'DEBUG',  # loggers(第一层日志级别关限制)--->handlers(第二层日志级别关卡限制)
            'propagate': False,  # 默认为True，向上（更高level的logger）传递，通常设置为False即可，否则会一份日志向上层层传递
        },
        '': {
            'handlers': ['other'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


class LogSystem(object):
    loggingLevel = logging.DEBUG

    def __init__(self):
        logging.config.dictConfig(LOGGING_DIC)
        self.logger = logging.getLogger('mailUjn')

    def set_logging(self, loggingLevel=logging.INFO):
        logging.config.dictConfig(LOGGING_DIC)
        self.logger.setLevel(loggingLevel)
        self.loggingLevel = loggingLevel
        return self.logger


ls = LogSystem()
set_logging = ls.set_logging
