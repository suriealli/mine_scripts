#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQHouseKeeper")
#===============================================================================
# QQ管家七日礼包
#===============================================================================
import datetime
import cDateTime
import cRoleMgr
import Environment
import DynamicPath
import cComplexServer
from Common.Message import AutoMessage
from Util.File import TabFile
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt8, EnumObj
from Common.Other import GlobalPrompt

HK_Version = 1
HK_Day = (2015, 6, 19, 0, 0, 0)

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("QQHK")
	
	#消息
	QQHK_S_Data = AutoMessage.AllotMessage("QQHK_S_Data", "qq管家七日礼包数据")
	
	Tra_QQHK_Reward = AutoLog.AutoTransaction("Tra_QQHK_Reward", "qq管家七日礼包奖励")
	Tra_QQHK_Record = AutoLog.AutoTransaction("Tra_QQHK_Record", "qq管家七日登录记录")
	
	QQHKConfig_Dict = {}
	NowIndex = None



class QQHKConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QQHK.txt")
	def __init__(self):
		self.dayIndex = int
		self.items = int

def LoadQQHKConfig():
	#读取副本购买次数配置表
	global QQHKConfig_Dict
	for cfg in QQHKConfig.ToClassType():
		QQHKConfig_Dict[cfg.dayIndex] = cfg.items

def GetHKDayIndex():
	global NowIndex
	if NowIndex is not None:
		return NowIndex
	UpdateIndex()
	return NowIndex


def AfterNewDay():
	UpdateIndex()

def UpdateIndex():
	global NowIndex
	StartDate = datetime.datetime(*HK_Day)
	delta = cDateTime.Now() - StartDate
	NowIndex = delta.days
	
def CheckInit(role):
	if 1 not in role.GetObj(EnumObj.QQOtherData):
		role.GetObj(EnumObj.QQOtherData)[1] = [0] * 7
		role.SetI8(EnumInt8.QQHK_Version, HK_Version)
	elif role.GetI8(EnumInt8.QQHK_Version) < HK_Version:
		#重新初始化
		role.SetI8(EnumInt8.QQHK_Version, HK_Version)
		role.GetObj(EnumObj.QQOtherData)[1] = [0] * 7


def RequestLoginRecord(role, msg):
	'''
	客户端请求查看登录记录
	@param role:
	@param msg:
	'''
	loginStatu = msg#1QQ管家登录， 0 其他
	nowindex= GetHKDayIndex()
	if nowindex < 0 or nowindex > 6:
		return
	with Tra_QQHK_Record:
		CheckInit(role)
		hkList = role.GetObj(EnumObj.QQOtherData)[1]
		if hkList[nowindex] == 0 and loginStatu == 1:
			hkList[nowindex] = 1
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveQQHK_Record, nowindex)
	role.SendObj(QQHK_S_Data, hkList)


def RequestGetRewrad(role, msg):
	'''
	请求领取奖励
	@param role:
	@param msg:
	'''
	backId, index = msg
	if index < 0 or index > 6:
		return
	#活动时间
	nowindex= GetHKDayIndex()
	if nowindex < 0 or nowindex > 6:
		return
	
	hkList = role.GetObj(EnumObj.QQOtherData).get(1)
	if not hkList:
		return
	if hkList[index] != 1:
		return
	itemCoding = QQHKConfig_Dict.get(index)
	if not itemCoding:
		return
	with Tra_QQHK_Reward:
		hkList[index] = 2
		role.AddItem(itemCoding, 1)
	role.CallBackFunction(backId, index)
	role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (itemCoding, 1))


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and (Environment.EnvIsQQ() or Environment.IsDevelop):
		LoadQQHKConfig()
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQHK_RequestGetRewrad", "请求获取qq管家七日礼包奖励"), RequestGetRewrad)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQHK_RequestLoginRecord", "请求获取qq管家客户端请求查看登录记录"), RequestLoginRecord)

