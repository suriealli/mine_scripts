#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.API.GlobalHttp")
#===============================================================================
# 全局HTTP访问
#===============================================================================
import cProcess
from World import Define
from ThirdLib import PrintHelp
from ComplexServer.Plug.Http import HttpProxy




def RoleQuery(op, roleids, backfun, regparam):
	post = {"op":op, "roleids": repr(roleids)}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Interface/RoleQuery/GetRoleInfo/", None, post, 60, backfun, regparam)

def CDKey(roleid, cdkey, backfun, regparam):
	get = {"roleid":roleid, "cdkey":cdkey}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Interface/CDKey/ActivateCDKey/", get, None, 60, backfun, regparam)

def FinishTask(openid, roleid, contractid, step, backfun, regparam):
	get = {"openid":openid, "roleid":roleid, "contractid":contractid, "step":step}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Interface/QQTask/FinishTask/", get, None, 20, backfun, regparam)


def RoleCall(roleid, command):
	get = {"roleid":roleid, "command" : command}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Interface/RemoteRoleCall/RemoteRoleCall/", get, None, 60)

class GetGlobalDataBack(object):
	def __init__(self, backfun):
		self.backfun = backfun
	
	def __call__(self, response, regparam):
		code, body = response
		if code == 200 and body:
			self.backfun(eval(body), regparam)
		else:
			print "GE_EXC, GetGlobalDataBack error. code(%s), body(%s)" % (code, body)
			self.backfun(None, regparam)

class GetGlobalDataKeysBack(object):
	def __init__(self, backfun):
		self.backfun = backfun
	
	def __call__(self, response, regparam):
		code, body = response
		if code == 200 and body:
			body = eval(body)
			datadict = {}
			for key, value in body.iteritems():
				if value:
					datadict[key] = eval(value)
				else:
					datadict[key] = value
			self.backfun(datadict, regparam)
		else:
			print "GE_EXC, GetGlobalDataKeysBack error. code(%s), body(%s)" % (code, body)
			self.backfun(None, regparam)



def SetGlobalData(key, value):
	post = {"key":key, "value" : PrintHelp.saferepr(value), "pid" : cProcess.ProcessID}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Global/GlobalData/SetGlobalData/", None, post, 60)

def SetGlobalDataByDict(datadict):
	post = {"datadict" : PrintHelp.saferepr(datadict), "pid" : cProcess.ProcessID}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Global/GlobalData/SetGlobalDataByDict/", None, post, 60)

def GetGlobalData(key, backFun, regparam = None):
	get = {"key":key, "pid" : cProcess.ProcessID}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Global/GlobalData/GetGlobalData/", get, None, 60, GetGlobalDataBack(backFun), regparam)

def GetGlobalDataByKeys(keys, backFun, regparam = None):
	get = {"keys":repr(keys), "pid" : cProcess.ProcessID}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Global/GlobalData/GetGlobalData_ByKeys/", get, None, 60, GetGlobalDataKeysBack(backFun), regparam)

def IncGlobalData(key, value):
	if type(value) is not int:
		print "GE_EXC, IncGlobalData error value not int key(%s), value(%s)" % (key, value)
		return
	get = {"key":key, "value" : value, "pid" : cProcess.ProcessID}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Global/GlobalData/IncGlobalData/", get, None, 60)

def DecGlobalData(key, value):
	if type(value) is not int:
		print "GE_EXC, DecGlobalData error value not int key(%s), value(%s)" % (key, value)
		return
	get = {"key":key, "value" : value, "pid" : cProcess.ProcessID}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Global/GlobalData/DecGlobalData/", get, None, 60)

def GetZoneName(backFun, regparam = None):
	get = {"pid" : cProcess.ProcessID}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Tool/ShowZoneName/GetZoneName/", get, None, 60, backFun, regparam)

def GetZoneNameEx(zoneids, backFun, regparam = None):
	get = {"pid" : cProcess.ProcessID, "zoneids" : PrintHelp.saferepr(list(zoneids))}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Tool/ShowZoneName/GetZoneNameEx/", get, None, 60, backFun, regparam)


def SendRoleMail(maildatas):
	#[(roleid, title, sender, content, mail_transaction, maildata)]
	post = {"maildatas" : PrintHelp.saferepr(maildatas)}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/DataBase/RoleMail/SendRoleMail/", None, post, 60)


def SetVIPInfo(getdict, backfun, regparam):
	#提交一个vip信息 只有正式服才可以访问
	#测试连接，请不要随便测试，注意角色ID相同的情况下的返回
	#http://ly.app100718848.twsapp.com:8008/vip/get?game=longqi&role_id=90194313245&server=21
	getdict["game"] = "longqi"
	HttpProxy.HttpRequest("10.207.143.220", 8888, "/vip/action/get/", getdict, None, 60, backfun, regparam)


def QQConsumeRank(rank, DayID):
	#消费排行榜(腾讯idip用)
	post = {"DayID":DayID, "rank" : PrintHelp.saferepr(rank), "pid" : cProcess.ProcessID}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Global/QQRank/NewDayRank/", None, post, 60)

def GMRoleUpdate(role):
	#内部号
	post = {"roleid":role.GetRoleID(), "account":role.GetTempObj(0)["account"], "name" : role.GetRoleName(), "pid" : cProcess.ProcessID, "level":role.GetLevel(), "viplevel":role.GetVIP(), "qp":role.GetConsumeQPoint()}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Global/GMRole/GMRole/", None, post, 60)

def CheckMyRoleBack(account, backfun, regparam):
	getdict = {"account":account}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Interface/QQMyRoleBack/CheckRoleBack/", getdict, None, 60, backfun, regparam)


def WaiGuaRoleUpdate(role, days, usecounts):
	#外挂
	from Game.GlobalData import ZoneName
	post = {"roleid":role.GetRoleID(), "account":role.GetTempObj(0)["account"], "name" : role.GetRoleName(), "pid" : cProcess.ProcessID, "zone_name": ZoneName.ZoneName, "days":days, "usecounts":usecounts, "viplevel":role.GetVIP(), "qp":role.GetConsumeQPoint()}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Global/WaiGua/WaiGuaRole/", None, post, 60)

def KGGRoleLevelHttp(data, backfun, regparam):
	print data
	HttpProxy.HttpRequest("www.kongregate.com", 80, "/api/submit_statistics.json/", data, None, 60, backfun, regparam)
	
def KGGRoleUserIDHttp(account, backfun,regparam ):
	url = "/searchUID.action?userId=%s" % account
	HttpProxy.HttpRequest("kgg.legendknight.com", 80, url, None, None, 60, backfun, regparam)


def GetAntiData(account, backfun, regparam):
	get = {"account":account}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Global/AntiData/GetAntiData/", get, None, 60, backfun, regparam)

def SetAntiData(account, name, idcard, state, backfun, regparam):
	get = {"account":account, "name":name, "idcard":idcard, "state":state}
	HttpProxy.HttpRequest(Define.Web_Global_IP, Define.Web_Global_Port, "/Global/AntiData/SetAntiData/", get, None, 60, backfun, regparam)
