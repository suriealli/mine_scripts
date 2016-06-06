#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.GlobalWeiXin")
#===============================================================================
# 微信关注人数
#===============================================================================
import Environment
import cComplexServer
from Common.Other import GlobalDataDefine
from Common.Message import PyMessage
from ComplexServer.API import GlobalHttp
from ComplexServer.Plug.Control import ControlProxy
from Control import ProcessMgr
from Game import RTF

if "_HasLoad" not in dir():
	GuanZhuCnt = 0


@RTF.RegFunction
def SetWeiXinCnt(cnt):
	'''
	设置微信关注人数
	@param cnt:
	'''
	if not Environment.HasControl:
		#只有控制进程才可以设置
		return
	global GuanZhuCnt
	if GuanZhuCnt == cnt:
		print "GE_EXC, repeat set SetWeiXinCnt (%s)" % cnt
		return
	GuanZhuCnt = cnt
	GlobalHttp.SetGlobalData(GlobalDataDefine.WinXinGuangZhuCnt, cnt)
	#同步给所有的逻辑进程
	SyncToLogic()


def GetBankGuanZhuCnt():
	# 请求获取关注人数
	GlobalHttp.GetGlobalData(GlobalDataDefine.WinXinGuangZhuCnt, AfterGet, None)

def AfterGet(response, regparam):
	if not response:
		return
	global GuanZhuCnt
	GuanZhuCnt = response
	SyncToLogic()

def SyncToLogic():
	#同步给所有的逻辑进程
	global GuanZhuCnt
	for sessionid in ProcessMgr.ControlProcesssSessions.iterkeys():
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateWeiXinGuanZhuCnt, GuanZhuCnt)


def GetWeiXinGuanZhuCnt(sessionid, msg):
	#逻辑进程请求获取微信关注人数
	global GuanZhuCnt
	ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateWeiXinGuanZhuCnt, GuanZhuCnt)


if "_HasLoad" not in dir():
	if Environment.HasControl and Environment.EnvIsQQ():
		GetBankGuanZhuCnt()
		cComplexServer.RegDistribute(PyMessage.Control_GetWeiXinGuanZhuCnt, GetWeiXinGuanZhuCnt)

