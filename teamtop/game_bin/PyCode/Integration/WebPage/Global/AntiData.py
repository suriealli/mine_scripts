#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Global.AntiData")
#===============================================================================
# 防沉迷查询
#===============================================================================
from Integration.Help import OtherHelp
from Integration.WebPage.User import Permission
from Integration import AutoHTML
from ComplexServer.Plug.DB import DBHelp


def GetAntiData(request):
	return OtherHelp.Apply(_GetAntiData, request, __name__)

def _GetAntiData(request):
	account = AutoHTML.AsString(request.GET, "account")
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select state from anti_data where account = '%s';" % account)
		result = cur.fetchall()
		if result:
			value = result[0][0]
		else:
			value = 0
	con.close()
	return value

def SetAntiData(request):
	return OtherHelp.Apply(_SetAntiData, request, __name__)
	
	
def _SetAntiData(request):
	account = AutoHTML.AsString(request.GET, "account")
	name = AutoHTML.AsString(request.GET, "name")
	idcard = AutoHTML.AsString(request.GET, "idcard")
	state = AutoHTML.AsInt(request.GET, "state")
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		h = cur.execute("replace into anti_data (account, name, idcard, state) values(%s, %s, %s, %s);", (account, name, idcard, state))
	con.close()
	return h


Permission.reg_public(GetAntiData)
Permission.reg_public(SetAntiData)
