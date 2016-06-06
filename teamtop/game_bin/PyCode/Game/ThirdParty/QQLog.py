#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLog")
#===============================================================================
# 腾讯上报日志
#===============================================================================
import cProcess
import Environment
import cComplexServer
from ComplexServer.API import QQHttp
from Common.Other import EnumSysData
from Game.SysData import WorldDataNotSync, WorldData
from Game.GlobalData import ZoneName
from Game.Role.Data import EnumTempObj


if "_HasLoad" not in dir():
	QQLogOpenFlag = True


QPointConsumeType = 1#Q点购神石
def GetGoodsName(goods_price):
	return "%s神石" % goods_price


def IsXinYueRole(role):
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	return login_info.get("adtag") == "gw.home.web.lqsz_20150325"


def LogLogin(role, pf, openid, userip):
	if QQLogOpenFlag is False:
		return
	if not IsXinYueRole(role):
		return
	QQHttp.QLog_Login(role, pf, openid, cProcess.ProcessID, userip, LogBack, None)

def LogExit(role, pf, openid, userip):
	if QQLogOpenFlag is False:
		return
	if not IsXinYueRole(role):
		return
	QQHttp.QLog_Exit(role, pf, openid, cProcess.ProcessID, userip, LogBack, None)

def LogCreateRole(role, pf, openid, userip):
	if QQLogOpenFlag is False:
		return
	if not IsXinYueRole(role):
		return
	QQHttp.QLog_CreateRole(role, pf, openid, cProcess.ProcessID, userip, LogBack, None)

def LogOnline(pf, cnt):
	if QQLogOpenFlag is False:
		return
	QQHttp.QLog_OnlineCnt(pf, cProcess.ProcessID, cnt, LogBack, None)

def LogConsume(role, pf, openid, userip, goodsId, goods_price, goodsCnt):
	if QQLogOpenFlag is False:
		return
	if not IsXinYueRole(role):
		return
	QQHttp.QLog_Consume(role, pf, openid, cProcess.ProcessID, userip, QPointConsumeType, goods_price * goodsCnt * 10, goodsId, goodsId, goodsCnt, GetGoodsName(goods_price), LogBack, None)


def LogXinYueLiBao(role, itemid, itemnum):
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	pf = login_info["pf"]
	serverId = cProcess.ProcessID
	QQHttp.QLog_XinYueLiBao(role, openid, serverId, pf, itemid, itemnum, LogBack, None)

def AfterNewDay():
	maxOnlineCnt = WorldDataNotSync.WorldDataPrivate.get(WorldDataNotSync.MaxOnlineToday, 0)
	#跨服清零
	WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.MaxOnlineToday] = 0
	if QQLogOpenFlag is False:
		return
	kaifuTime = WorldData.WD.get(EnumSysData.KaiFuKey)
	kaifuTime = kaifuTime.strftime("%Y-%m-%d %H:%M:%S")
	QQHttp.QLog_ServerInfo(cProcess.ProcessID, ZoneName.ZoneName, maxOnlineCnt,kaifuTime, LogBack, None)
	
def LogBack(response, regparam):
	#上报回调
	#print "qqlog LogBack"
	pass
#	if response is None:
#		print "GE_EXC, QLogBack  (%s) back response is None" % (regparam)
#		return
#	code, body = response
#	if code != 200:
#		print "GE_EXC, QLogBack (%s) back code(%s), body(%s)" % (regparam, code, body)
#	
	#print "LogBack", response

if "_HasLoad" not in dir():
	if Environment.EnvIsQQ() and Environment.HasLogic and (not Environment.IsCross):
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
