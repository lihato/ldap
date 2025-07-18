#!/bin/bash
dnf install -y python3 python3-devel.x86_64 python3-pip.noarch nginx gcc
pip3 install -r ./requirements.txt
/usr/bin/cp -f ./cas_client.py /usr/local/lib/python3.6/site-packages/cas_client/cas_client.py
/usr/bin/cp -f ./nginx.conf /etc/nginx/nginx.conf
systemctl restart nginx.service
firewall-cmd  --zone=public --add-port=8081/tcp --permanent && firewall-cmd --reload
