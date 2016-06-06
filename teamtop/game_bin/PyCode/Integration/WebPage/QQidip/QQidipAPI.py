#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.QQidip.QQidipAPI")
#===============================================================================
# 入口
#===============================================================================
from Integration.WebPage.QQidip import QQidip
from Integration.WebPage.User import Permission



def QQidipReq(request):
	return QQidip.Apply(request)


Permission.reg_public(QQidipReq)