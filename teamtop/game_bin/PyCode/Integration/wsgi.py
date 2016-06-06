#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.wsgi")
#===============================================================================
# uwsgi 启动脚本
#===============================================================================
import os
import sys
from django.core.handlers.wsgi import WSGIHandler

if not os.path.dirname(__file__) in sys.path[:1]:
	sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

application = WSGIHandler()

