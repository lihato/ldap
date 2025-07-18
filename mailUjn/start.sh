#!/bin/bash
for i in ` ps -ef | grep "uwsgi.ini" | grep uwsgi | grep -v 'grep' | tr -s ' ' | cut -d ' ' -f 2` ; do
  kill $i
done
uwsgi --ini ./uwsgi.ini
systemctl restart nginx.service
