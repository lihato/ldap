# -*- coding: utf-8 -*-
"""
Project: 智慧校园
Creator: Lihaitao
Create time: 2025-07-14 15:49
Introduction: 网易邮箱接口

"""
# 固定数据区 网易
DOMAIN_NAME = 'sdmail.vip'
BASE_URL = 'https://api.qiye.163.com'
TOKEN_URL = '/api/pub/token/acquireToken'
SSOTOKEN_URL = '/api/pub/token/ssoAuthToken'
UNITLIST_URL = '/api/open/unit/getUnitList'
CREATEUNIT_URL = '/api/open/unit/createUnit'
GETACCOUTLIST_URL = '/api/open/unit/getAccountList'
GETACCOUNT_URL = '/api/open/account/getAccount'
CREATEACCOUNT_URL = '/api/open/account/createAccount'
DELEACCOUNTSIM_URL = '/api/open/account/deleteAccountSim'
DELEACCOUNT_URL = '/api/open/account/deleteAccount'
UPDATEACCOUNT_URL = '/api/open/account/updateAccount'
RECOVERACCOUNT_URL = '/api/open/account/recoverAccount'
MOVECCOUNT_URL = '/api/open/account/moveUnit'
MOVEUNIT_URL = '/api/open/unit/moveUnit'
DELUNIT_URL = '/api/open/unit/deleteUnit'
UNREADMSG_URL = '/api/open/mailbox/getUnreadMsg'
SSOSIGN_URL = '/api/sso/ssoSign'

APPID = 'qytest058CD52'
AUTHCODE = 'Ntestl'
ORGOPENID = 'ftest'

HEADERS_COM = {
            'Content-Type': 'application/json',
            'qiye-access-token': 'token',
            'qiye-app-id': APPID,
            'qiye-org-open-id': ORGOPENID,
            'qiye-sso-auth-token': 'ssotoken',
            'qiye-timestamp': 'token',
            'qiye-nonce': '123456789012'
}
"""
REPSAMPLE ={
"code": 0,
"success": 'true',
"message":"SUCCESS(0, '成功')",
"data": 'object'
}
"""
"""
响应状态 响应码 状态说明
SUCCESS 0 成功
SYSTEM_ERROR -1 系统内部异常
SYSTEM_INNER_SERVICE_ERROR -2 系统内部服务异常
SYSTEM_COMMON_BIZ_FAILURE -3 通用业务操作失败
SYSTEM_DATA_NOT_EXISTS -4 系统数据不存在
AUTH_FAILURE -100 认证失败
AUTH_DATA_NOT_FOUND -101 认证数据不存在
ACCESS_DENY -200 访问受限
IP_DENY -201 IP 受限
PERMISSION_NOT_REGISTER -202 接口权限未注册
TOKEN_NOT_AVAILABLE -300 token 不可用
TOKEN_ACCESS_EXPIRED -301 access token 失效
TOKEN_REFRESH_EXPIRED -302 refresh token 失效
TOKEN_GENERATE_ERROR -303 token 产生失败
AUTH_EXPIRED -304 授权失效
APP_EXPIRED -305 应用失效
TOKEN_SSO_GENREATE_ERROR -320 sso token 产生失败
TOKEN_SSO_VERIFY_ERROR -321 sso token 验证失败
TOKEN_SSO_EXPIRED -322 sso token 过期
REQUEST_ERROR -400 请求异常
PARAM_ERROR -401 请求参数异常
REQUEST_REPEAT -421 请求重复
REQUEST_FREQUENCY_TOO_HIGH -422 请求频率过高
REQUEST_FREQUENCY_TOO_HIGH_APP -423 APP 请求频率过高
HEADER_ERROR -424 请求头异常
THIRD_ACCESS_ERROR -500 第三方服务访问异常
"""

TOKENID = "tokenid"
REFRESHTOKEN = "refreshtokeId"
SSOTOKENID = "ssotokenid"

# 固定数据区 校内
GETTOKEN_URL = 'http://127.0.0.1/mail/getToken'
JG_URL = 'http://127.0.0.1/mail/getJG'
ORG_URL = 'http://127.0.0.1/mail/getOrg'
LZJG_URL = 'http://127.0.0.1/mail/getLzJG'

CAS_URL = 'https://sso.ujn.edu.cn/tpass/'
CAS_LOGIN_URL = 'https://sso.ujn.edu.cn/tpass/login'
CAS_LOGOUT_URL = 'https://sso.ujn.edu.cn/tpass/logout'
# app login url this sso.py app's login url
#APP_LOGIN_URL = 'http://192.168.120.60/login'
APP_LOGIN_URL = 'http://localhost:8081/login'

USERID = "wangyimail"
SIGNATURE = "ujn4fkkkh1i"
DQZTM = 136  # 教工在职状态	136为在职
BZLX = 522  # 教工的用工性质	为在编
# 固定数据区 共通
EXITES_DEPCODE = -2
WAITE_DEPCODE = -1
ROOT_DEPCODE = 10
ADD_ACCOUNT = 0
EXITES_ACCOUNT = 1
DELETE_ACCOUNT = 2
MODIFY_ACCOUNT = 3
IGNORE_ACCOUNT = 4
RECOVER_ACCOUNT = 5
DEFAULT_UNIT = 'ujn_default'
