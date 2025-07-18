# -*- coding: utf-8 -*-
"""
Project: 智慧校园
Creator: Lihaitao
Create time: 2025-07-14 15:49
Introduction: 网易邮箱接口

"""

import traceback
import urllib.request
import urllib.parse
from datetime import datetime
from datetime import timedelta
import json
import logging
import ssl

from mailUjn.log import set_logging
from mailUjn.const import *
from mailUjn.upInfo import (getUnitList, createUnit, createAccount, moveUnit,recoverAccount,
                            moveAccount, deleteAccountSim, deleteUnit, getAccoutList)
from mailUjn.common import (getCacheToken, localUnit, try_log)

__all__ = ['up_Account', 'up_Unit']

logger = logging.getLogger('mailUjn')


#根据Token获取学校教工信息共通
def getCommonInfo(strURL):
    """
        :param none
        :return: json
        """
    ret = None
    token = getReqToken()
    if token is None:
        return ret
    url = strURL
    params = {
        'toKen': token  # 会话标识
    }
    header = {
        'Content-Type': 'application/json'
    }
    postdata = json.dumps(params).encode('utf-8')
    request = urllib.request.Request(url, data=postdata, headers=header)
    context = ssl._create_unverified_context()  # 创建一个不验证 SSL 证书的上下文
    resp = urllib.request.urlopen(request,context=context)

    if resp.getcode() == 200:
        ret_data = resp.read().decode('utf-8')
        logger.debug("获取学校接口信息原始返回信息：" + ret_data)
        try:
            content_dict = json.loads(ret_data)
        except Exception as expt:
            logger.warning('获取学校接口 返回的数据不是json文本数据！' + str(expt) + str(ret_data))
        if content_dict['code'] == 1:  # 成功
            ret = content_dict['data']
        else:
            logger.warning('获取学校接口信息失败！' + ret_data)
    else:
        logger.warning('校内服务器 返回错误代码！' + str(resp.getcode))
    return ret


# 根据token获取教工信息
@try_log()
def get_JG():
    """
    :param none
    :return: json str format [{"id":3476,"xm":"教工姓名","gh":"100043","zzjg":24,"dqztm":1336,"bzlx":57222},...]
    """
    return getCommonInfo(JG_URL)


# 通过token获取组织机构信息
@try_log()
def get_Org():
    """
    :param none
    :return: str formate [{"id":56660,"fid":44,"name":"经营管理系党支部"},...]
    """
    return getCommonInfo(ORG_URL)

# 通过token获取离职员工数据
@try_log()
def get_LzJG():
    """
    :param none
    :return: str [{"id":3680,"xm":"杜测试","gh":"100157","zzjg":37,"dqztm":1327,"bzlx":57222},....]
    """
    return getCommonInfo(LZJG_URL)

# 使用secretKey获取token
def getReqToken():
    '''
    :param userId: 用户标识 wangyimail
    :param signature: secretKey
    :return: str,token
    '''
    ret = getCacheToken.get_token(USERID)
    if ret is not None:  # cached
        return ret
    url = GETTOKEN_URL
    header = {
        'Content-Type': 'application/json'
    }
    params = {
        'signature': SIGNATURE  # 会话标识
    }
    #postdata = urllib.parse.urlencode(params).encode('utf-8')
    postdata = json.dumps(params).encode('utf-8')
    request = urllib.request.Request(url, data=postdata, headers=header, method='POST')
    #request = urllib.request.Request(url, data=postdata)
    context = ssl._create_unverified_context()  # 创建一个不验证 SSL 证书的上下文
    resp = urllib.request.urlopen(request,context=context)

    if resp.getcode() == 200:
        ret_data = resp.read().decode('utf-8')
        logger.debug(ret_data)
        try:
            content_dict = json.loads(ret_data)
        except Exception as expt:
            logger.error('使用secretKey获取token 返回的数据不是json文本数据！' + str(expt) + str(ret_data))
        if content_dict['code'] == 1:  # 成功
            token = content_dict['data']
            expiresIn = (datetime.now() + timedelta(seconds=58)).strftime("%Y-%m-%d %H:%M:%S")
            getCacheToken.save_token(USERID, token, expiresIn)
            logger.debug(token)
        else:
            token = None
            logger.warning('校内服务器token，请求失败')
        ret = token
    else:
        logger.error('校内服务器 返回错误代码！' + str(resp.getcode))
    return ret


# 更新部门信息到邮箱服务器
@try_log()
def up_Unit():
    """
    :param userId: 用户标识 wangyimail
    :param signature: secretKey
    :return: str
    """
    ret = False
    isChangeUnit = False
    org = get_Org()
    if org is None or len(org) < 10:
        logger.info('获取学校组织信息失败！')
        return ret
    # orginfo "id":56660,"fid":44,"name":"经营管理系党支部"
    unit = getUnitList()
    if unit is None:
        return ret
    # unitinfo "rank": 0,  "unitId": "", "unitName": "", "unitOpenId": "","unitParentId": ""
    # update dpInfo  {"id": 39, "fid": 10, "name": "继续测试", "unitId":"mailunitid","parentId": id or 20 = top,'exits':'true'}
    # mailUjn [ERROR] 创建部门 失败！{"data":null,"success":false,"message":"通用业务操作失败: UNIT.EXIST","code":-3}
    # add unitID
    localUnit.mergUnit(org, unit)
    # create unit unitParentId
    dtWait = []
    for oneOrg in org:
        if oneOrg['id'] == ROOT_DEPCODE: # 顶级部门，学院，已存在
            continue
        if oneOrg['exits'] == 'true': # 部门，已存在
            continue
        if oneOrg['fid'] != ROOT_DEPCODE:
            if oneOrg['parentId'] == WAITE_DEPCODE:
                dtWait.append(oneOrg)
                continue
        unitId = createUnit(oneOrg)
        if unitId is not None: # 创建成功
            oneOrg['unitId'] = unitId
            isChangeUnit = True
    # 为防止死循环 最多同期5级数据
    iloopCnt = 1
    while(len(dtWait) >0 and iloopCnt < 10):
        # add paretID
        for oneDt in dtWait:
            for twoOrg in org:
                if oneDt['fid'] == twoOrg['id']:
                    oneDt['parentId'] = twoOrg['unitId']
                    continue
        # create unit
        for oneDt in dtWait:
            if oneDt['parentId'] == WAITE_DEPCODE:
                continue
            unitId = createUnit(oneDt)
            if unitId is not None: # 创建成功
                isChangeUnit = True
                for oneOrg in org:
                    if oneOrg['id'] == oneDt['id']:
                        oneOrg['unitId'] = unitId
                        break
                dtWait.remove(oneDt)
            else: # 创建反失败退出
                logger.info('创建部门失败！' + oneDt['name'])
                break
        iloopCnt = iloopCnt + 1
    if isChangeUnit and iloopCnt < 10:
        logger.info('同期组织信息，新建成功！')

    #检查部门信息是否有变化
    #mail 侧
    #{'unitOpenId': 'r42S7cJQeb', 'unitId': '590584007076600', 'unitParentId': '590584007070806',
    # 'unitName': '办公室党支部', 'rank': 99999, 'unitDesc': '办公室党支部'}
    #学校侧
    # {"id": 39, "fid": 10, "name": "继续教育部", "unitId":"mailunitid","parentId": id or 20 = top,'exits':'true'}
    # 取最新部门信息 更新
    if isChangeUnit :  #有更新
        unit = getUnitList()
        if unit is None:
            # 保存组织信息到缓存
            logger.info('新建部门后同期组织信息，失败！')
            return False
        localUnit.mergUnit(org, unit)
        isChangeUnit = False
    dif_unit = localUnit.getDiffUnit(org, unit)
    # 更新变化的部门信息
    if len(dif_unit) > 0:
        logger.info("更新变化的部门信息" + str(dif_unit))
        for oneChg in dif_unit:
            moveUnit(oneChg)
        isChangeUnit = True
        #ret = False
    # 删除多余部门
    if len(unit) > 0:
        logger.info("邮箱侧删多余的部门信息" + str(dif_unit))
        for oneDel in unit:
            deleteUnit(oneDel['unitId'])
        isChangeUnit = True
    if isChangeUnit :
        # 取最新部门信息 更新
        unit = getUnitList()
        if unit is None:
            logger.info('变更部门后同期组织信息，失败！')
        localUnit.mergUnit(org, unit)
    # 保存组织信息到缓存
    localUnit.SaveUnit(org)
    return True

# 更新员工部门信息到邮箱服务器
@try_log()
def up_Account():
    """
    :param userId: 用户标识 wangyimail
    :param signature: secretKey
    :return: str
    """
    ret = False
    orgJC = get_JG()
    if orgJC is None or len(orgJC) < 100:
        logger.info('获取学校教工账号失败！')
        return ret
    # orgJCinfo "id": 3476, "xm": "教工姓名", "gh": "100043", "zzjg": 24, "dqztm": 1336, "bzlx": 57222
    # accInfo  {{"id": 3476, "xm": "教工姓名", "gh": "100043", "zzjg": 24, "dqztm": 1336, "bzlx": 57222}, "unitId": "unitId", }
    unit = localUnit.getUnit()
    if unit is None:
        ret = up_Unit()
        if not ret:
            logger.info('获取学校教工部门信息失败！')
            return ret

    #获取邮箱账号列表
    mailAccount = getAccoutList()
    if mailAccount is None:
        logger.info('获取邮箱账号信息失败！')
        return ret
    # 分类教工账号状态
    localUnit.getDiffAccount(orgJC, mailAccount)
    # create mail unit
    dtdefault = []
    dtError = []
    for oneJc in orgJC:
        if oneJc['unitId'] == DEFAULT_UNIT:
            dtdefault.append(oneJc)
        #ADD_ACCOUNT = 0
        #EXITES_ACCOUNT = 1
        #DELETE_ACCOUNT = 2
        #MODIFY_ACCOUNT = 3
        if oneJc['status'] == EXITES_ACCOUNT:
            continue
        if oneJc['status'] == ADD_ACCOUNT:
            mailid = createAccount(oneJc)
            if mailid != oneJc['gh']: # 创建失败 下一个
                dtError.append(oneJc)
            continue
        if oneJc['status'] == MODIFY_ACCOUNT:
            moveAccount(oneJc)
            logger.info('邮箱删账号部门移动：' + oneJc['gh'])
            continue
        if oneJc['status'] == RECOVER_ACCOUNT:
            recoverAccount(oneJc['gh'])
            logger.info('邮箱删账号恢复：' + oneJc['gh'])
            continue
        if oneJc['status'] == DELETE_ACCOUNT:
            deleteAccountSim(oneJc['gh'])
            logger.info('删除邮箱删账号：' + oneJc['gh'])
    if len(mailAccount) > 0:
        # print("账号应该删除" + str(mailAccount))
        for delone in mailAccount:
            if delone['status'] == DELETE_ACCOUNT:
                deleteAccountSim(delone['accountName'])
                logger.info('删除邮箱删账号：' + delone['accountName'])

    if len(dtdefault) > 0:
        # create accout into default unit
        logger.info('由于没有组织信息，以下邮件账号加认默认部门未作成！' + str(dtdefault))
    if len(dtError) > 0:
        logger.warning('以下账号创建邮件账号失败！' + str(dtError))  
    if len(dtError) == 0:
        ret = True
    return ret


if __name__ == '__main__':
    try:
        set_logging(loggingLevel=logging.DEBUG)
        #form_text = get_JG()
        #form_text = get_Org()
        #print(up_Unit())
        #print(up_Account())
        #cas_login("castest","CasTest2023@sdyxy")
        #getReqToken()
        #print(get_LzJG())
    except Exception as exp:
        logger.error(exp.__str__())
        logger.fatal(traceback.format_exc())