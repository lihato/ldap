# cached# -*- coding: utf-8 -*-
"""
Project: 智慧校园
Creator: Lihaitao
Create time: 2025-07-14 15:49
Introduction: 网易邮箱接口共通

"""
import threading
import traceback
import random
import string
from datetime import datetime
from datetime import timedelta
import logging
from functools import wraps
from mailUjn.const import *
from mailUjn.log import set_logging


__all__ = ['getCacheToken', 'localUnit', 'generate_random_password', 'try_log']

logger = logging.getLogger('mailUjn')


def try_log():
    """ 用于操作的 try catch 有异常，写LOG，没有，不写。"""
    def _try_log(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as excep:
                logger.error(excep.__str__())
                logger.error(traceback.format_exc())
                return None
        return wrapper
    return _try_log


# TOKEN 有效期内，缓存防止重复请求
class getToken():
    def __init__(self):
        self.tokenCachelist={}
        self.len = 0
        self.MaxLen = 200
        self._thread_lock = threading.Lock()
    def len(self):
        self.len= len(self.tokenCachelist)
        return self.len
    def setMaxLen(self,maxlen=200):
        self.MaxLen=maxlen
    # 重复检查
    def get_token(self,tokeid):
        token=self.tokenCachelist.get(tokeid)
        #logger.debug(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        if token is not None: # 检查时间
            # 字符串转时间
            s = token['Time'] #  "2025-07-15 09:30:00"
            saveTime = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            if datetime.now() < saveTime:
                return token['token']
        return None
    def save_token(self, tokeid , token, expiresTime):
        cacheToken = self.tokenCachelist.get(tokeid)
        if cacheToken is not None:  # 检查时间
            cacheToken['Time'] = expiresTime
            cacheToken['token'] = token
        else:
            cur_token = {'Time': expiresTime, 'token': token}
            if len(self.tokenCachelist) > self.MaxLen:
                self.tokenCachelist.clear()
            self.tokenCachelist[tokeid] = cur_token


getCacheToken = getToken()


class unitInfo():
    def __init__(self):
        self.Cachelist=[]
        self.len = 0
        self.MaxLen = 1000
        self._thread_lock = threading.Lock()
    def len(self):
        self.len= len(self.Cachelist)
        return self.len
    def setMaxLen(self,maxlen=1000):
        self.MaxLen=maxlen
    def getUnit(self):
        if len(self.Cachelist) == 0:
            return None
        return self.Cachelist

    def mergUnit(self, unitOrg , UnitMail):
        # unitinfo "rank": 0,  "unitId": "", "unitName": "", "unitOpenId": "","unitParentId": ""
        # update dpInfo  {"id": 39, "fid": 10, "name": "继续教育部", "unitId":"mailunitid","parentId": id or 20 = top,'exits':'true'}
        # mailUjn [ERROR] 创建部门 失败！{"data":null,"success":false,"message":"通用业务操作失败: UNIT.EXIST","code":-3}
        # add unitID
        for oneOrg in unitOrg:
            for oneUnit in UnitMail:
                oneOrg['unitId'] = WAITE_DEPCODE
                oneOrg['exits'] = 'false'
                if oneOrg['name'] == oneUnit['unitName']:
                    oneOrg['unitId'] = oneUnit['unitId']
                    oneOrg['exits'] = 'true'
                    break

        # add unitParentId
        for oneOrg in unitOrg:
            if oneOrg['id'] == ROOT_DEPCODE:
                continue
            if oneOrg['fid'] != ROOT_DEPCODE:
                oneOrg['parentId'] = WAITE_DEPCODE
                for twoOrg in unitOrg:
                    if oneOrg['fid'] == twoOrg['id']:
                        oneOrg['parentId'] = twoOrg['unitId']
                        continue
            else:
                oneOrg['parentId'] = ROOT_DEPCODE  # 一级部门

    def SaveUnit(self, unitOrg ):
        self.Cachelist = unitOrg.copy()
        #print(self.Cachelist)

    def getDiffUnit(self, unitOrg ,UnitMail):
        # 检查部门信息是否有变化
        # 学校侧 unitOrg
        # {"id": 39, "fid": 10, "name": "继续教育部", "unitId":"mailunitid","parentId": id or 20 = top,'exits':'true'}
        # mail 侧 UnitMail
        # {'unitOpenId': 'r42S7cJQeb', 'unitId': '590584007076600', 'unitParentId': '590584007070806',
        # 'unitName': '办公室党支部', 'rank': 99999, 'unitDesc': '办公室党支部'}
        for dt0 in UnitMail:
            if dt0['unitId'] == DEFAULT_UNIT:  #　default 除外
                UnitMail.remove(dt0)
                continue
            if dt0['unitParentId'] is None:  # 顶级部门
                dt0['unitParentId'] = ROOT_DEPCODE

        dtDif = []
        for dt1 in unitOrg:
            unitName= dt1['name']
            for dt2 in UnitMail:
                if dt2['unitName'] == unitName:
                    if dt2['unitParentId'] != dt1['parentId']:
                        dtDif.append(dt1)   # 上层组织变更
                    UnitMail.remove(dt2)    # 最后剩余的为邮箱删应该删的
                    break
        return dtDif

    # 获取学校帐号与邮箱帐号的教工差异
    def getDiffAccount(self, accountOrg ,accountMail):
        # 检查教工信息是否有变化
        # 学校侧 accountOrg
        # accInfo {{"id": 3476, "xm": "教工姓名", "gh": "100043", "zzjg": 24, "dqztm": 1336, "bzlx": 57222}+
        # "unitId": "unitId", status:ADD_ACCOUNT|EXITES_ACCOUNT|DELETE_ACCOUNT|MODIFY_ACCOUNT }
        # 邮箱 侧 accountMail #DEFAULT_UNIT
        # {'account_id':['account_id'], 'accountName':['accountName'], 'unitId':['unitId']}

        # add unitID status
        for oneJc in accountOrg:
            oneJc['status'] = ADD_ACCOUNT
            oneJc['unitId'] = DEFAULT_UNIT
            for oneUnit in self.Cachelist :
                if oneJc['zzjg'] == oneUnit['id']:
                    oneJc['unitId'] = oneUnit['unitId']
                    break

        for dt1 in accountOrg:
            accoutName = dt1['gh']
            for dt2 in accountMail:
                if dt2['accountName'] == accoutName:
                    if dt2['unitId'] != dt1['unitId']:
                        dt1['status'] = MODIFY_ACCOUNT  # 组织变更
                    else:
                        if dt2['status'] == 2:
                            dt1['status'] = RECOVER_ACCOUNT
                        else:
                            dt1['status'] = EXITES_ACCOUNT
                    accountMail.remove(dt2)    # 最后剩余的为邮箱删应该删的
                    break
        #邮箱端多余账号，除测试管理外，应该删除
        for dt0 in accountMail:
            accountName = dt0['accountName']
            if accountName.find('ceshi') > -1 or accountName.find('test') > -1 or accountName.find('admin') > -1:   # 测试帐号
                dt0['status'] = IGNORE_ACCOUNT
            else:
                if dt0['status'] == 0:
                    dt0['status'] = DELETE_ACCOUNT
                else:
                    dt0['status'] = IGNORE_ACCOUNT

        return

localUnit = unitInfo()


def generate_random_password(length=10):
    # 定义密码字符集合，包含数字、大小写字母和符号
    char_set = {"small": "abcdefghijklmnopqrstuvwxyz",
                "nums": "0123456789",
                "big": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                "special": "^!\$%&/()=?{[]}+~#-_.:,;<>|\\"
                }
    password = []
    keys = ['small','nums','big','special']
    chars = string.ascii_letters + string.digits + string.punctuation  # 包含大小写字母、数字和标点符号
    while len(password) < length:
        # 随机选取一个发送邀请消息
        key = keys[int(random.randint(1, 39) / 10)]
        a_char = random.choice(chars)
        if a_char in char_set[key]:
            if check_prev_char(password, char_set[key]):
                continue
            else:
                password.append(str(a_char))
    return ''.join(password)

    # 生成随机复杂密码
    #random_password = generate_random_password(password_length)


def check_prev_char(password, current_char_set):
    """Function to ensure that there are no consecutive
    UPPERCASE/lowercase/numbers/special-characters."""
    index = len(password)
    if index == 0:
        return False
    else:
        prev_char = password[index - 1]
        if prev_char in current_char_set:
            return True
        else:
            return False


if __name__ == '__main__':
    try:
        set_logging(loggingLevel=logging.DEBUG)
        print (generate_random_password(8))
    except Exception as exp:
        logger.error(exp.__str__())
        logger.fatal(traceback.format_exc())