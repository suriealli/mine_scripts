#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Global.WebServerTime")
#===============================================================================
# 后台时间查询
#===============================================================================
import time
import Environment
from django.http import HttpResponse
from Integration.WebPage.User import Permission
from Integration import AutoHTML

def ReqWebTime(request):
	'''【数据与工具】--后台时间与版本查询'''
	gd = AutoHTML.Table(["版本", "unixtime", "时区", "当前时间"], [], "后台时间与版本")
	gd.body.append((Environment.ENV, int(time.time()), time.timezone / 3600, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
	return HttpResponse(gd.ToHtml())

Permission.reg_develop(ReqWebTime)
