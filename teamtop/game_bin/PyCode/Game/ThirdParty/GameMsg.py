#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.GameMsg")
#===============================================================================
# GS系统 
#===============================================================================
import time
import datetime
import Environment
import DynamicPath
import cRoleMgr
import cDateTime
import cComplexServer
from Util.File import TabFile
from Common.Message import AutoMessage
from Common.Other import EnumSysData, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.SysData import WorldData
from Game.Role import Call, Event
from Game.Role.Data import EnumObj, EnumTempObj
from Game.Role.Mail import Mail

#############################################################################################
SET_BIRTHDAY_NEEDRMB = 10 					#设置生日需要神石
BIRTHDAY_ITEMS = [(27512, 1), (26676, 2), (26934, 10), (26227, 4), (26042, 5)]	#生日礼包物品
BIRTHDAY_RMB = 0							#生日礼包魔晶
BIRTHDAY_MONEY = 0							#生日礼包金币
NEED_QPOINT = 30000							#生日礼包需要Q点
#############################################################################################


if "_HasLoad" not in dir():
	#当前的节日礼包ID
	GSLiBaoID = 0
	GSLiBaoCfg_Dict = {}
	GSMailConfig_Dict = {}
	GSMailCFG = None
	GSBMailCFG = None
	#消息

	GS_GameMSG = AutoMessage.AllotMessage("GS_GameMSG", "游戏后台消息提示")
	GS_NotifyMSG = AutoMessage.AllotMessage("GS_NotifyMSG", "游戏后台客服系统回复了")
	
	#已经发过生日邮件的角色
	BirthDayMailRoles = set()
	#已经发过当前节日邮件的角色
	GSLiBaoRoles = set()
	
	#日志
	Tra_GS_Set_BirthDay = AutoLog.AutoTransaction("Tra_GS_Set_BirthDay", "GS系统设置生日日期")
	Tra_GS_BirthDayReward = AutoLog.AutoTransaction("Tra_GS_BirthDayReward", "GS系统生日礼包")
	Tra_GS_LiBaoReward = AutoLog.AutoTransaction("Tra_GS_LiBaoReward", "GS系统节日礼包")
	
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("QQOther")

def RoleGS(roleId, param):
	#消息提示
	Call.LocalDBCall(roleId, RoleGSEX, param)

def RoleGSEX(role, param):
#	msginfo, link = param
#	msginfo = msginfo.replace("#H", "\n")
#	param = (msginfo, link)
	gsdata = role.GetTempObj(EnumTempObj.GS_Data)
	if not gsdata:
		key = 1
		role.SetTempObj(EnumTempObj.GS_Data, {key:param})
	else:
		key = max(gsdata.keys()) + 1
		gsdata[key] = param
	if role.IsLost():
		return
	#发送一条游戏后台消息提示
	role.SendObjAndBack(GS_GameMSG, param, 600, AfterBack, key)


def AfterBack(role, cArgv, regparam):
	if cArgv is None:
		return
	gsdata = role.GetTempObj(EnumTempObj.GS_Data)
	if regparam in gsdata:
		del gsdata[regparam]

def SyncRoleOtherData(role, param):
	gsdata = role.GetTempObj(EnumTempObj.GS_Data)
	if not gsdata:
		return
	for key, msg in gsdata.iteritems():
		#发送一条游戏后台消息提示
		role.SendObjAndBack(GS_GameMSG, msg, 600, AfterBack, key)


def RequestGSQQ(role, msg):
	'''
	请求获取客服QQ
	@param role:
	@param msg:
	'''
	backID, _ = msg
	role.CallBackFunction(backID, WorldData.WD.get(EnumSysData.GameServiceQQ, 0))

def GSNotify(role, param):
	#离线命令，提示客服系统有回复
	role.SendObj(GS_NotifyMSG, None)


class GSRewardConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QQGSReward.txt")
	def __init__(self):
		self.gsId = int
		self.name = str
		self.rewardItems = self.GetEvalByString
		self.rmb = int
		self.money = int
		
		self.startDate = eval				#开始时间
		self.endDate = eval					#结束时间
	
	def PrePocess(self):
		self.startTickId = 0
		self.endTickId = 0
		#当前时间戳
		nowTime = cDateTime.Seconds()
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endDate).timetuple()))
		if nowTime >= endTime:
			return
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.startDate).timetuple()))
		if beginTime >= endTime:
			print "GE_EXC GSRewardConfig startDate >= endDate (%s)" % self.gsId
			return
		
		if beginTime <= nowTime < endTime:
			self.startTickId = cComplexServer.RegTick(5, StartGSLiBao, self)
			self.endTickId = cComplexServer.RegTick(endTime - nowTime - 5, EndGSLiBao, self)
		else:
			if beginTime - nowTime > 10 * 24 * 3600:
				return 
			self.startTickId = cComplexServer.RegTick(beginTime - nowTime, StartGSLiBao, self)
			self.endTickId = cComplexServer.RegTick(endTime - nowTime - 5, EndGSLiBao, self)


class GSMailConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("QQGSMail.txt")
	def __init__(self):
		self.gsId = int
		self.name = str
		self.title = str
		self.sender = str
		self.content = str


def LoadGSLBConfig():
	global GSLiBaoCfg_Dict
	for cfg in GSRewardConfig.ToClassType():
		GSLiBaoCfg_Dict[cfg.gsId] = cfg
		cfg.PrePocess()

def LoadGSMailConfig():
	global GSMailConfig_Dict
	for cfg in GSMailConfig.ToClassType():
		GSMailConfig_Dict[cfg.gsId] = cfg
	
	global GSBMailCFG
	GSBMailCFG = GSMailConfig_Dict[0]


def StartGSLiBao(callArgv, regparam):
	global GSLiBaoID
	if GSLiBaoID:
		print "GE_EXC repeat StartGSLiBao ", regparam.gsId
	GSLiBaoID = regparam.gsId
	global GSMailConfig_Dict
	global GSMailCFG
	GSMailCFG = GSMailConfig_Dict.get(GSLiBaoID)
	if not GSMailCFG:
		print "GE_EXC, StartGSLiBao  not mailCfg (%s)" % GSLiBaoID
		return
	for role in cRoleMgr.GetAllRole():
		CheckGSMail(role, GSMailCFG, None)

def EndGSLiBao(callArgv, regparam):
	global GSLiBaoID
	if not GSLiBaoID:
		print "GE_EXC EndGSLiBao error"
	GSLiBaoID = 0
	global GSMailCFG
	GSMailCFG = None

def GetGSData(role):
	return role.GetObj(EnumObj.QQOtherData)[2]


def HasBirthDayReward(role):
	gsData = GetGSData(role)
	bMonth, bDay = gsData[1]
	if not bMonth or not  bDay:
		return False
	nowYear = cDateTime.Year()
	
	oldYear = gsData[2]
	if oldYear == nowYear:
		return False
	
	nowMonth = cDateTime.Month()
	nowDay =  cDateTime.Day()
	if nowMonth != bMonth or bDay != nowDay:
		return False
	return True


def HasGSReward(role):
	gsData = GetGSData(role)
	getYear, getId = gsData[3]
	nowyear = cDateTime.Year()
	if getYear > nowyear:
		return False
	if getYear <  nowyear:
		gsData[3] = (nowyear, 0)
		getId = 0
	
	if getId >= GSLiBaoID:
		return False
	return True

def GetBirthDayData(role, msg):
	'''
	获取自己的生日数据
	@param role:
	@param msg:
	'''
	backId, _ = msg
	gsData = GetGSData(role)
	role.CallBackFunction(backId, gsData[1])

def SetBirthday(role, msg):
	'''
	客户端请求设置生日
	@param role:
	@param msg:
	'''
	month, day = msg
	if role.GetConsumeQPoint() < NEED_QPOINT:
		return
	try:
		datetime.date(2012, month, day)
	except:
		return
	
	gsData = GetGSData(role)
	oldMonth, oldDay = gsData[1]
	with Tra_GS_Set_BirthDay:
		if not oldMonth and not oldDay:
			gsData[1] = (month, day)
		elif oldMonth == month and oldDay == day:
			return
		else:
			if role.GetUnbindRMB() < SET_BIRTHDAY_NEEDRMB:
				return
			role.DecUnbindRMB(SET_BIRTHDAY_NEEDRMB)
			gsData[1] = (month, day)
		
		role.Msg(2,0, GlobalPrompt.GS_Birthday_Ok)

def GetBirthDayReward(role, msg):
	'''
	获取生日礼包
	@param role:
	@param msg:
	'''
	if role.GetConsumeQPoint() < NEED_QPOINT:
		return
	gsData = GetGSData(role)
	bMonth, bDay = gsData[1]
	if not bMonth or not  bDay:
		role.Msg(2, 0, GlobalPrompt.GS_Birthday_0)
		return
	nowYear = cDateTime.Year()
	nowMonth = cDateTime.Month()
	nowDay =  cDateTime.Day()
	
	oldYear = gsData[2]
	if oldYear == nowYear:
		role.Msg(2, 0, GlobalPrompt.GS_Birthday_1)
		return
	if nowMonth != bMonth or bDay != nowDay:
		role.Msg(2, 0, GlobalPrompt.GS_Birthday_2)
		return
	
	gsData[2] = nowYear
	#发奖励
	with Tra_GS_BirthDayReward:
		tips = GlobalPrompt.Reward_Tips
		for itemCoding, itemCnt in BIRTHDAY_ITEMS:
			role.AddItem(itemCoding, itemCnt)
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		if BIRTHDAY_RMB:
			role.IncBindRMB(BIRTHDAY_RMB)
			tips += GlobalPrompt.BindRMB_Tips % BIRTHDAY_RMB
		if BIRTHDAY_MONEY:
			role.IncMoney(BIRTHDAY_MONEY)
			tips += GlobalPrompt.Money_Tips % BIRTHDAY_MONEY
		
		role.Msg(2, 0, tips)

def GetGSLiBao(role, msg):
	'''
	获取GS节日礼包
	@param role:
	@param msg:
	'''
	global GSLiBaoID
	if not GSLiBaoID:
		role.Msg(2, 0, GlobalPrompt.GS_LiBao_None)
		return
	
	gsData = GetGSData(role)
	getYear, getId = gsData[3]
	nowyear = cDateTime.Year()
	if getYear > nowyear:
		return
	if getYear <  nowyear:
		gsData[3] = (nowyear, 0)
		getId = 0
	
	if getId >= GSLiBaoID:
		return
	
	cfg = GSLiBaoCfg_Dict.get(GSLiBaoID)
	if not cfg:
		return
	
	with Tra_GS_LiBaoReward:
		gsData[3] = (nowyear, GSLiBaoID)
		tips = GlobalPrompt.Reward_Tips
		if cfg.rmb:
			role.IncBindRMB(cfg.rmb)
			tips += GlobalPrompt.BindRMB_Tips % cfg.rmb
		if cfg.money:
			role.IncMoney(cfg.money)
			tips += GlobalPrompt.Money_Tips % cfg.money
		if cfg.rewardItems:
			for itemCoding, itemCnt in cfg.rewardItems:
				role.AddItem(itemCoding, itemCnt)
				tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		role.Msg(2, 0, tips)

def AfterLogin(role, param):
	qqodata = role.GetObj(EnumObj.QQOtherData)
	if 2 not in qqodata:
		qqodata[2] = {1 : (0, 0), 2 : 0, 3:(0,0)}
	
	global GSMailCFG, GSBMailCFG
	CheckGSMail(role, GSMailCFG, GSBMailCFG)
	
def AfterNewDay():
	global GSMailCFG, GSBMailCFG
	for role in cRoleMgr.GetAllRole():
		CheckGSMail(role, GSMailCFG, GSBMailCFG)

def CheckGSMail(role, mailCfg, bmailCfg):
	global GSLiBaoID
	global GSMailConfig_Dict
	global GSLiBaoRoles
	global BirthDayMailRoles
	roleId = role.GetRoleID()
	if GSLiBaoID and mailCfg:
		if (roleId not in GSLiBaoRoles) and HasGSReward(role):
			Mail.SendMail(roleId, mailCfg.title, mailCfg.sender, mailCfg.content)
			GSLiBaoRoles.add(roleId)
	if bmailCfg and (roleId not in BirthDayMailRoles):
		if HasBirthDayReward(role) :
			Mail.SendMail(roleId, bmailCfg.title, bmailCfg.sender, bmailCfg.content)
			BirthDayMailRoles.add(roleId)

if "_HasLoad" not in dir():
	if Environment.HasLogic and (not Environment.IsCross) and (Environment.EnvIsQQ() or Environment.IsDevelop):
		LoadGSLBConfig()
		LoadGSMailConfig()
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		#客户端请求消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GS_RequestGSQQ", "请求获取客服QQ"), RequestGSQQ)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GS_GetBirthDayData", "获取自己的生日数据"), GetBirthDayData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GS_SetBirthday", "客户端请求设置生日"), SetBirthday)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GS_GetBirthDayReward", "获取生日礼包"), GetBirthDayReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GS_GetGSLiBao", "获取GS节日礼包"), GetGSLiBao)
		
		
		