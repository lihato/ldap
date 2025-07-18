# -*- coding: utf-8 -*-
"""
Project: 智慧校园
Creator: Lihaitao
Create time: 2025-07-14 15:49
Introduction: 网易邮箱sso

"""
from flask import (Flask, redirect, request, session, url_for)
import traceback
import os
import logging
import time
import random
import signal
from mailUjn.log import set_logging
from mailUjn.const import *
from mailUjn.upInfo import (getSsoSign, getUnreadMsg)
from mailUjn.getInfo import (up_Account, up_Unit)
import cas_client

logger = logging.getLogger('mailUjn')

application = Flask(__name__)
application.secret_key = os.urandom(24)
set_logging(loggingLevel=logging.DEBUG)

cas_cl = cas_client.CASClient(CAS_URL, APP_LOGIN_URL, auth_prefix='')

@application.route('/login')
def login():
    ticket = request.args.get('ticket')
    if ticket:
        try:
            cas_response = cas_cl.perform_service_validate(
                ticket=ticket,
                service_url=APP_LOGIN_URL,
                headers=None
                )
        except Exception as exp:
            logger.error(str(exp))
            logger.error(traceback.format_exc())
            # CAS server is currently broken, sleep 3-5 second try again later.
            if session.get('retry') != True:
                time.sleep(random.randint(100, 300) / 100)
                session['retry'] = True
                return redirect(cas_cl.get_login_url(service_url=APP_LOGIN_URL))
            return "Failed to cas login"
        #print(cas_response.user)
        #print(cas_response.response_text)
        #print(cas_response.success)
        if cas_response and cas_response.success:
            session['logged-in'] = True
            usernmae = cas_response.user
            mailLoginUrl = getSsoSign(usernmae)
            #print(mailLoginUrl)
            return redirect(mailLoginUrl)
        return "Failed to cas login 2"
    session['logged-in'] = False
    session['retry'] = False
    cas_login_url = cas_cl.get_login_url(service_url=APP_LOGIN_URL)
    return redirect(cas_login_url)

@application.route('/logout')
def logout():
    del(session['logged-in'])
    cas_logout_url = cas_client.get_logout_url(service_url=CAS_LOGOUT_URL)
    return redirect(cas_logout_url)

@application.route('/upJG')
def upJG():
    if session.get('upJG') == True:
        return '教工信息已更新。'
    else:
        up_Account()
        session['upJG'] = True
        session['upOrg'] = True
        return '教工信息更新中.....'

@application.route('/upOrg')
def upOrg():
    if session.get('upOrg') == True:
        return '组织信息已更新。'
    else:
        up_Unit()
        session['upOrg'] = True
        return '组织信息更新中.....'

@application.route('/')
def root():
    if session.get('logged-in') == True:
        return 'You Are Logged In'
    else:
        #return 'You Are Not Logged In'
        return redirect(APP_LOGIN_URL)

#CAS 登录 *** uWSGI 2.0.21 ****
#uwsgi --ini ./uwsgi.ini
# nginx.conf 设置uwsgi监听的端口号和地址
#       server 0.0.0.0:8082; }
#     server {
#         listen       80;
#         listen       [::]:80;
#         server_name  _;
#         root         /usr/share/nginx/html;
#         location / {
#          include /etc/nginx/uwsgi_params;
#          uwsgi_pass mailujn;
#         }
#   ---------省略-----------
#         error_page 500 502 503 504 /50x.html;
#         location = /50x.html {
#         }
#     }

@application.route('/getUnreadNum', methods=['POST', 'GET'])
def getUnreadNum():
    retErro = {'code':-401, 'data':None,'message':"",'success':False}
    # 设置超时间
    timeout = 20
    # 设置超时处理
    def tm_handler(signum, frame):
        raise TimeoutError('time out after {} seconds'.format(timeout))
    # 注册超时信号处理函数
    signal.signal(signal.SIGALRM, tm_handler)

    if request.method == "POST":
        params = request.json
        if params is None:
            params = request.get_json()
        try:
            if 'gh' in params.keys():
                strgh = params['gh']
            else:
                retErro['message']="缺少教工工号信息（gh）"
                return retErro, 200, {"Content-Type": "application/json"}
            fid = "1,5"
            if 'fid' in params.keys():
                fid = params['fid']
        except Exception as expt:
            retErro['message']="其他错误"
            return retErro, 200, {"Content-Type": "application/json"}
        mainInfo = {"gh": strgh, "fid": fid }
        # 开时计时超时间
        signal.alarm(timeout)
        try:
            # 执行操作
            msgNum = getUnreadMsg(mainInfo)
            # 取消超时信号
            signal.alarm(0)
        except TimeoutError as e:
            retErro['message'] = "请求上级服务器超时"
            return retErro, 200, {"Content-Type": "application/json"}
        if msgNum is None:
            retErro['message'] = "其他错误"
            return retErro, 200, {"Content-Type": "application/json"}
        return msgNum, 200, {"Content-Type": "application/json"}
    # 返回json数据的方法
    else:
        return retErro, 200, {"Content-Type": "application/json"}

class SSLPATH:
    CERTPATH = "D:\wechat\mailUjn\certs\slapdserver.crt"
    KEYPATH = "D:\wechat\mailUjn\certs\slapdserver.key"
if __name__ == '__main__':
    try:
        set_logging(loggingLevel=logging.DEBUG)
        #cas_login("castest","CasTest2023@test")
        #application.run(port=8081,debug=True,ssl_context=(SSLPATH.CERTPATH,SSLPATH.KEYPATH))
        #application.run(port=8081, debug=True)
    except Exception as exp:
        logger.error(exp.__str__())
        logger.fatal(traceback.format_exc())