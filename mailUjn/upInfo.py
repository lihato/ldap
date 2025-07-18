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
import json
import logging
import ssl

from mailUjn.log import set_logging
from mailUjn.const import *
from mailUjn.common import (getCacheToken, generate_random_password, try_log)

__all__ = ['getUnitList', 'createUnit', 'createAccount',
           'moveUnit', 'deleteUnit', 'getSsoSign','getAccoutList',
           'moveAccount', 'deleteAccount', 'getUnreadMsg',
           'deleteAccountSim', 'recoverAccount']

logger = logging.getLogger('mailUjn')


# 获取调用更新SSOtoken
def getOneToken(tokenid):
    '''
    :param tokenid
    :return: str,token
    '''
    ret = getCacheToken.get_token(tokenid)
    if ret is not None:  # cached
        return ret
    if tokenid == SSOTOKENID: # sso token
        ret = getSSoToken(tokenid)
    else:  # 调用更新 token
        ret = getReqToken(tokenid)
    if ret is None:
        logger.warning('邮箱服务器 访问TOKEN获取失败！')
    return ret

# 获取token
def getReqToken(tokenid):
    '''
    :param tokenid
    :return: str,token
    '''
    url = BASE_URL + TOKEN_URL
    header = {
        'Content-Type': 'application/json'
    }
    params = {
        'appId': APPID,  #  应用 ID
        'authCode': AUTHCODE , # 应用授权码
        'orgOpenId': ORGOPENID # 企业OpenId
    }

    postdata = json.dumps(params).encode('utf-8')
    try:
        context = ssl._create_unverified_context()  # 创建一个不验证 SSL 证书的上下文
        request = urllib.request.Request(url, data=postdata, headers=header, method='POST')
        resp = urllib.request.urlopen(request,context=context, timeout = 18)
    except Exception as expt:
        logger.error('获取token信息 网络异常！' + str(expt))
        return None

    if resp.getcode() == 200:
        ret_data = resp.read().decode('utf-8')
        #logger.debug(ret_data)
        try:
            content_dict = json.loads(ret_data)
            code = content_dict['code']
            if code != 0 :
                logger.error('获取 token 失败！' + str(ret_data))
                return None
            data = content_dict['data']
            token = data['accessToken']
            expiresTime = data['accessTokenExpiredTime']
            getCacheToken.save_token(TOKENID, token, expiresTime)
            reToken = token
            logger.debug("accessTokenExpiredTime" + expiresTime + " " + reToken)
            token = data['refreshToken']
            expiresTime = data['refreshTokenExpiredTime']
            getCacheToken.save_token(REFRESHTOKEN, token, expiresTime)
            if tokenid == REFRESHTOKEN:
                reToken = token
            logger.debug(expiresTime + " " + reToken)
            return reToken
        except Exception as exp:
            logger.error('getReqToken 返回的数据jsont处理异常！' + str(exp) + str(ret_data))
    else:
        logger.warning('邮箱服务器 返回错误代码！' + str(resp.getcode))
    return None


# 获取ssotoken
def getSSoToken(tokenid):
    '''
    :param tokenid
    :return: str,token
    '''
    url = BASE_URL + SSOTOKEN_URL
    header = {
        'Content-Type': 'application/json'
    }
    params = {
        'appId': APPID,  #  应用 ID
        'authCode': AUTHCODE , # 应用授权码
        'orgOpenId': ORGOPENID # 企业OpenId
    }
    postdata = json.dumps(params).encode('utf-8')
    try:
        # print (url)
        context = ssl._create_unverified_context()  # 创建一个不验证 SSL 证书的上下文
        request = urllib.request.Request(url, data=postdata, headers=header, method='POST',)
        resp = urllib.request.urlopen(request,context=context,timeout = 18)
    except Exception as expt:
        # print(str(expt))
        logger.error('获取ssotoken信息 网络异常！' + str(expt))
        return None
    if resp.getcode() == 200:
        ret_data = resp.read().decode('utf-8')
        #logger.debug(ret_data)
        try:
            content_dict = json.loads(ret_data)
        except Exception as exp:
            logger.error('getssoToken 返回的数据jsont处理异常！' + str(exp) + str(ret_data))
        code = content_dict['code']
        if code != 0 :
            logger.error('获取 ssotoken 失败！' + str(ret_data))
            return None
        data = content_dict['data']
        token = data['ssoAuthToken']
        expiresTime = data['ssoAuthTokenExpiredTime']
        getCacheToken.save_token(tokenid, token, expiresTime)
        reToken = token
        logger.debug(expiresTime + " " + reToken)
        # print(reToken)
        return reToken
    else:
        logger.warning('邮箱服务器 返回错误代码！' + str(resp.getcode))
    return None


#根据获取邮箱信息共通
def getCommonInfo(strURL,params, isCheck = False, errMsg=[], noData = False, noLog =False):
    '''
        :param  信息URL
        :return: str,token
        '''
    token = getOneToken(TOKENID)
    if token is None:
        return None
    url = BASE_URL + strURL
    header = HEADERS_COM
    header['qiye-access-token'] = token
    postdata = json.dumps(params).encode('utf-8')
    try:
        context = ssl._create_unverified_context()  # 创建一个不验证 SSL 证书的上下文
        request = urllib.request.Request(url, data=postdata, headers=header, method='POST')
        resp = urllib.request.urlopen(request,context=context, timeout = 18)
    except Exception as expt:
        logger.error(strURL +'获取邮箱信息网络异常！' + str(expt))
        return None
    if resp.getcode() == 200:
        ret_data = resp.read().decode('utf-8')
        try:
            content_dict = json.loads(ret_data)
            if not noLog:
                logger.debug(ret_data)
        except Exception as expt:
            logger.error(strURL +'获取邮箱信息 返回的数据jsont处理异常！' + str(expt) + str(ret_data))
        code = content_dict['code']
        if code != 0:
            if isCheck:  #返回上层处理
                errMsg.append(ret_data)
            else:
                logger.error(strURL + '获取邮箱信息失败！' + str(ret_data))
            return None
        if noData:
            data = content_dict
        else:
            data = content_dict['data']
        # token = data['ssoAuthToken']
        #if not noLog:
        #    logger.debug(data)
        return data
    else:
        logger.warning('邮箱服务器 返回错误代码！' + str(resp.getcode))
    return None


# 获取所有部门列表
def getUnitList():
    '''
    :param  none
    :return: str,token
    '''
    params = {
        'domain': DOMAIN_NAME  # 域名
    }
    return getCommonInfo(UNITLIST_URL,params)


# 获取所有帐号列表
@try_log()
def getAccoutList():
    '''
    :param  none
    :return: str,token
    '''
    params = {
        'domain': DOMAIN_NAME  # 域名
    }
    acount_data = getCommonInfo(GETACCOUTLIST_URL,params, noLog=True)
    if acount_data is None:
        return None
    # status 帐号状态，0-正常，1-禁用，2-已删除，4-离职，5-交接中，6-交接完成
    ret_data = []
    for oneAct in acount_data['list']:
        ret_data.append({'account_id':oneAct['account_id'],
                        'accountName':oneAct['accountName'],
                        'unitId':oneAct['unitId'],
                        'status':oneAct['status']})
    logger.debug(ret_data)
    return ret_data
# 获取账户信息
def getAccountUnit(accountName, isCheck = False):
    '''
    :param  accountName # 用户账号名，邮箱格式的前缀
    :return: str,token
    '''
    params = {
        'domain': DOMAIN_NAME,  # 域名
        'accountName': accountName  # # 用户账号名，邮箱格式的前缀
    }
    err_msg = []
    ret_data = getCommonInfo(GETACCOUNT_URL,params,isCheck,err_msg)
    if ret_data is None:
        if isCheck :
            errmg = err_msg[0]
            if errmg.find('ACCOUNT.NOTEXIST') > -1:  # 帐号不存在
                logger.debug(accountName + '帐号不存在检查成功！')
        return None
    return ret_data


# 获取单点登录签名值
def getSsoSign(accountName):
    '''
    :param  accountName # 用户账号名，邮箱格式的前缀
    :return: str,token
    '''
    token = getOneToken(SSOTOKENID)
    if token is None or accountName is None :
        return None
    url = BASE_URL + SSOSIGN_URL
    header = HEADERS_COM
    header['qiye-sso-auth-token'] = token
    params = {
        'domain': DOMAIN_NAME, #  域名
        'accountName': accountName  # # 用户账号名，邮箱格式的前缀
    }
    postdata = json.dumps(params).encode('utf-8')
    try:
        context = ssl._create_unverified_context()  # 创建一个不验证 SSL 证书的上下文
        request = urllib.request.Request(url, data=postdata, headers=header, method='POST')
        resp = urllib.request.urlopen(request,context=context, timeout = 18)
    except Exception as expt:
        logger.error('获取SSO信息网络异常！' + str(expt))
        return ""
    if resp.getcode() == 200:
        ret_data = resp.read().decode('utf-8')
        try:
            content_dict = json.loads(ret_data)
            #logger.debug(ret_data)
        except Exception as expt:
            logger.error('获取SSO信息 返回的数据jsont处理异常！' + str(expt) + str(ret_data))
            return None
        code = content_dict['code']
        if code != 0 :
            logger.error('获取SSO信息 失败！' + accountName + str(ret_data))
            if ret_data.find("sso token 过期") > -1 or code == -322:  # sso token 过期 再取
                getSSoToken(SSOTOKENID)
            return None
        #token = data['ssoAuthToken']
        data = content_dict['data']
        retURL = data['endpoint'] + "?sso_token=" + data['sign'] + "&language=0"
        return retURL
    else:
        logger.warning('getsso 邮箱服务器 返回错误代码！' + str(resp.getcode))
    return None


# 创建部门
def createUnit(dpInfo):
    '''
    :param  dpInfo{"id":39,"fid":10,"name":"继续测试","parentId":id or 20=top}
    :return: str,token
    '''
    params = {
        'domain': DOMAIN_NAME, #  域名
        'unitDesc':dpInfo['name'], # 部门描述
        'unitName': dpInfo['name'] # 部门名称
    }
    if dpInfo['parentId'] != ROOT_DEPCODE:
        params['parentId'] = dpInfo['parentId']
    ret_data = getCommonInfo(CREATEUNIT_URL, params)
    if ret_data is None:
        return None
    unitId = ret_data['unitId']
    return unitId


# 创建账户
def createAccount(accInfo):
    '''
    :param  accInfo{{"id":3476,"xm":"教工姓名","gh":"100043","zzjg":24,"dqztm":1336,"bzlx":57222},"unitId":"unitId",}
    :return: str,token
    '''
    init_pass = generate_random_password(10)  # 初始密码 随机生成
    params = {
        'domain': DOMAIN_NAME,  # 域名
        'accountName': accInfo['gh'],  # 教工工号 对应的mail地址应为<工号@test.edu.cn>
        'name': accInfo['xm'],  # 教工姓名
        'password': init_pass,   # 初始密码
        'jobNumber': accInfo['gh'],  # 教工工号
        'unitId': accInfo['unitId']  # 所属部门id
    }
    err_msg = []
    isCheck = True
    ret_data = getCommonInfo(CREATEACCOUNT_URL, params, isCheck, err_msg)
    if ret_data is None:
        errmsg=err_msg[0]
        if errmsg.find('MAILACCOUNT.NAMEEXIST') > -1:  # 帐号存在
            logger.info('账户已存在！' + accInfo['xm'] + accInfo['gh'])
            return accInfo['gh']
        return None
    accountName = ret_data['accountName']
    return accountName


# 移动部门
def moveUnit(dpInfo):
    '''
    :param  dpInfo{"id":39,"fid":10,"name":"继续测试","parentId":id or 20=top,'unitid}
    :return: str,token
    '''
    params = {
        'domain': DOMAIN_NAME, #  域名
        'unitId':dpInfo['unitId'], # 部门描述
        'unitParentId': dpInfo['parentId'] # 部门名称
    }
    if dpInfo['parentId'] == ROOT_DEPCODE:
        params['parentId'] = 'root'
    ret_data = getCommonInfo(MOVEUNIT_URL, params)
    if ret_data is None:
        return None
    unitId = ret_data['unitId']
    return unitId


# 删除部门
def deleteUnit(unitId):
    '''
    :param  unitId 部门 id
    :return: str,token
    '''
    params = {
        'domain': DOMAIN_NAME, #  域名
        'unitId': unitId # 部门描述
    }
    ret_data = getCommonInfo(DELUNIT_URL, params, noData=True)
    if ret_data is None:
        return False
    else:
        return True


# 删除账号-可恢复
def deleteAccountSim(accountName):
    '''
    :param  accountName 用户账号名，邮箱格式的前缀
    :return: str,token
    '''
    params = {
        'domain': DOMAIN_NAME, #  域名
        'accountName': accountName # 用户账号名，邮箱格式的前缀
    }
    ret_data = getCommonInfo(DELEACCOUNTSIM_URL, params, noData=True)
    if ret_data is None:
        return False
    else:
        return True


# 删除账号-不可恢复
def deleteAccount(accountName):
    '''
    :param  accountName 用户账号名，邮箱格式的前缀
    :return: true false
    '''
    params = {
        'domain': DOMAIN_NAME, #  域名
        'accountName': accountName # 用户账号名，邮箱格式的前缀
    }
    ret_data = getCommonInfo(DELEACCOUNT_URL, params, noData=True)
    if ret_data is None:
        return False
    else:
        return True


# 恢复账号
def recoverAccount(accountName):
    '''
    :param  accountName 用户账号名，邮箱格式的前缀
    :return: true false
    '''
    params = {
        'domain': DOMAIN_NAME,  # 域名
        'accountName': accountName  # 用户账号名
    }
    ret_data = getCommonInfo(RECOVERACCOUNT_URL, params, noData=True)
    if ret_data is None:
        return False
    else:
        return True


# 更新账号
def updateAccount(accInfo):
    '''
    :param  accInfo{{"id":3476,"xm":"教工姓名","gh":"100043","zzjg":24,"dqztm":1336,"bzlx":57222},"unitId":"unitId",}
    :return: str,token
    '''
    params = {
        'domain': DOMAIN_NAME,  # 域名
        'accountName': accInfo['gh'],  # 教工工号 对应的mail地址应为<工号@sddfvc.edu.cn>
        'unitId': accInfo['unitId']  # 所属部门id
    }
    ret_data = getCommonInfo(UPDATEACCOUNT_URL, params, noData=True)
    if ret_data is None:
        return False
    else:
        return True


# 移动账号所属部门
def moveAccount(accInfo):
    '''
    :param  accInfo{{"id":3476,"xm":"教工姓名","gh":"100043","zzjg":24,"dqztm":1336,"bzlx":57222},"unitId":"unitId",}
    :return: str,token
    '''
    params = {
        'domain': DOMAIN_NAME,  # 域名
        'accountName': accInfo['gh'],  # 教工工号 对应的mail地址应为<工号@sddfvc.edu.cn>
        'unitId': accInfo['unitId']  # 所属部门id
    }
    ret_data = getCommonInfo(MOVECCOUNT_URL, params, noData=True)
    if ret_data is None:
        return False
    else:
        return True


# 获得取未读邮件数量
def getUnreadMsg(mailInfo):
    '''
    :param  mailInfo{"gh":3476,"fid":"1,5"}
    :return: str,token
    '''
    params = {
        'domain': DOMAIN_NAME,  # 域名
        'accountName': mailInfo['gh'],  # 教工工号 对应的mail地址应为<工号@sddfvc.edu.cn>
        'fid': mailInfo['fid']  # 邮箱文件夹 ID,使用英文半角逗号分开， 默认传 1,5 : 1-收件箱;2-草稿箱;3-已发送;4-已删除;5-垃圾邮件
    }
    err_msg = []
    isCheck = True
    ret_data = getCommonInfo(UNREADMSG_URL, params, isCheck, err_msg, noData=True, noLog=True)
    if ret_data is None:
        return None
    return ret_data

if __name__ == '__main__':
    try:
        set_logging(loggingLevel=logging.DEBUG)
        #print(getUnitList())
        #print(getAccoutList())
        #cas_login("test","test")
        #dpInfo =  {"id": 39, "fid": 10, "name": "继续测试", "parentId":ROOT_DEPCODE}
        #print(createUnit(dpInfo))
        #print(getAccountUnit('ceshi'))
        #accInfo = {"id": 3476, "xm": "教工姓名", "gh": "100043", "zzjg": 24, "dqztm": 1336, "bzlx": 57222, "unitId": "590584007076108" }
        #print(createAccount(accInfo))
        #print(getSsoSign("100043"))
        #getSSoToken(SSOTOKENID)
        getSsoSign("300001")
    except Exception as exp:
        print(str(exp))
        logger.error(exp.__str__())
        logger.fatal(traceback.format_exc())
