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
import cas_client

application = Flask(__name__)
application.secret_key = os.urandom(24)
CAS_URL = 'https://sso.ujn.edu.cn/tpass/'
CAS_LOGIN_URL = 'https://sso.ujn.edu.cn/tpass/login'
CAS_LOGOUT_URL = 'https://sso.ujn.edu.cn/tpass/logout'
APP_LOGIN_URL = 'http://localhost:8081/login'
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
            print.error(str(exp))
            print.error(traceback.format_exc())
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
            mailLoginUrl = "test.html" #getSsoSign(usernmae)
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
#*    upstream mailcon {
#*      # uwsgi监听的端口号和地址
#*       server 0.0.0.0:8082; }
#     server {
#         listen       80;
#         listen       [::]:80;
#         server_name  _;
#         root         /usr/share/nginx/html;
#         location / {
#*          include /etc/nginx/uwsgi_params;
#*          uwsgi_pass mailujn;
#         }
#   ---------省略-----------
#         error_page 500 502 503 504 /50x.html;
#         location = /50x.html {
#         }
#     }


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
        print(exp.__str__())
        print(traceback.format_exc())
