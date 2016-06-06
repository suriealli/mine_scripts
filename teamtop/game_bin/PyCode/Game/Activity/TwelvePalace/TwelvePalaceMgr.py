#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TwelvePalace.TwelvePalaceMgr")
#===============================================================================
# 勇闯十二宫
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Persistence import Contain
from Game.Union import UnionMgr
from Game.Role import Event
from Game.Role.Data import EnumDayInt8, EnumCD
from Game.Activity import CircularDefine
from Game.VIP import VIPConfig

if "_HasLoad" not in dir():
	__IsTwelvePalaceBegin = False	#勇闯十二宫活动是否开始
	#消息
	SyncTwelvePalaceRoleData = AutoMessage.AllotMessage("SyncTwelvePalaceRoleData", "勇闯十二宫同步玩家数据")
	#日志
	Tra_RequestTwelvePalace = AutoLog.AutoTransaction("Tra_RequestTwelvePalace", "勇闯十二宫请求闯宫")
	Tra_TwelvePalaceHelpOther = AutoLog.AutoTransaction("Tra_TwelvePalaceHelpOther", "勇闯十二宫协助他人闯宫")
	Tra_TwelvePalaceSuccess = AutoLog.AutoTransaction("Tra_TwelvePalaceSuccess", "勇闯十二宫完美闯宫")
	Tra_TwelvePalaceInAdvance = AutoLog.AutoTransaction("Tra_TwelvePalaceInAdvance", "勇闯十二宫提前闯宫")
#==============================================
def TwelvePalaceStart(*param):
	'''
	勇闯十二宫开启
	'''
	_, activetype = param
	if activetype != CircularDefine.CA_TwelvePalace:
		return
	global __IsTwelvePalaceBegin
	if __IsTwelvePalaceBegin is True:
		return
	__IsTwelvePalaceBegin = True

def TwelvePalaceEnd(*param):
	'''
	勇闯十二宫关闭
	'''
	_, activetype = param
	if activetype != CircularDefine.CA_TwelvePalace:
		return
	global __IsTwelvePalaceBegin
	global TwelvePalaceDict
	if __IsTwelvePalaceBegin is False:
		return
	__IsTwelvePalaceBegin = False

#============================================	
def RequestTwelvePalace(role, msg):
	'''
	客户端请求闯宫
	@param role:
	@param msg:
	'''
	if __IsTwelvePalaceBegin is False:
		return
	if role.GetLevel() < EnumGameConfig.TwelvePalaceNeedLevel:
		return
	role_vip = role.GetVIP()
	if role_vip < EnumGameConfig.TwelvePalaceNeedVIP:
		return
	if role.ItemCnt(EnumGameConfig.TwelvePalacePalaceCardCode) < 1:
		return
	cfg = VIPConfig._VIP_BASE.get(role_vip)
	if not cfg:
		print "GE_EXC, TwelvePalaceMgr can not find vip level (%s) in _VIP_BASE" % role_vip
		return
	role_daily_cnt = role.GetDI8(EnumDayInt8.TwelvePalaceCnt)
	if role_daily_cnt > cfg.twelevePalaceCnt:
		return
	#已经是闯宫状态
	if role.GetRoleID() in TwelvePalaceDict:
		return
	with Tra_RequestTwelvePalace:
		if role.DelItem(EnumGameConfig.TwelvePalacePalaceCardCode, 1) < 1:
			return
		role.IncDI8(EnumDayInt8.TwelvePalaceCnt, 1)
		TwelvePalaceDict[role.GetRoleID()] = {}
	role.SendObj(SyncTwelvePalaceRoleData, [1, {}])

def RequestHelpOtherTwelvePalace(role, msg):
	'''
	玩家请求协助他人勇闯十二宫
	@param role:
	@param msg:
	'''
	if __IsTwelvePalaceBegin is False:
		return
	if role.GetLevel() < EnumGameConfig.TwelvePalaceHelpNeedLevel:
		return
	#帮助别人的roleId
	roleID_to_help_other = role.GetRoleID()
	#被帮助的roleId
	roleID_to_be_helped = msg
	#不能自助
	if roleID_to_help_other == roleID_to_be_helped:
		role.Msg(2, 0, GlobalPrompt.TwelvePalace_Helpself_Tips)
		return
	role_to_be_helped = cRoleMgr.FindRoleByRoleID(roleID_to_be_helped)
	#被协助玩家下线了
	if not role_to_be_helped:
		return
	#被协助的玩家须处在闯宫状态 
	helpDict = TwelvePalaceDict.get(roleID_to_be_helped, None)
	if helpDict is None:
		role.Msg(2, 0, GlobalPrompt.TwelvePalace_HelpOver_Tips)
		return
	#已经协助过了 
	if roleID_to_help_other in helpDict:
		role.Msg(2, 0, GlobalPrompt.TwelvePalace_HelpAlready_Tips)
		return
	#被协助者已经被协助了8次
	if not len(helpDict) < EnumGameConfig.TwelvePalaceHelpPlayerLimit:
		role.Msg(2, 0, GlobalPrompt.TwelvePalace_HelpFull_Tips)
		return
	
	with Tra_TwelvePalaceHelpOther:
		role.IncDI8(EnumDayInt8.TwelvePalaceHelpCnt, 1)
		if not role.GetDI8(EnumDayInt8.TwelvePalaceHelpCnt) > EnumGameConfig.TwelvePalaceMaxHelpTimes:
			role.AddItem(EnumGameConfig.TwelvePalaceHelpAwardCode, EnumGameConfig.TwelvePalaceHelpAwardCnt)
			role.Msg(2, 0, GlobalPrompt.TwelvePalace_HelpAwrad_Tips % (EnumGameConfig.TwelvePalaceHelpAwardCode, EnumGameConfig.TwelvePalaceHelpAwardCnt))
		else:
			role.Msg(2, 0, GlobalPrompt.TwelvePalace_HelpNoAwrad_Tip)
	helpDict[roleID_to_help_other] = role.GetRoleName(), role.GetSex(), role.GetCareer(), role.GetGrade()
	role_to_be_helped.SendObj(SyncTwelvePalaceRoleData, [1 , helpDict])

def RequestTwelvePalaceHarvest(role, msg):
	'''
	客户端请求完美闯宫
	@param role:
	@param msg:
	'''
	if __IsTwelvePalaceBegin is False:
		return
	helpdict = TwelvePalaceDict.get(role.GetRoleID(), None)
	if helpdict is None:
		return
	if len(helpdict) < EnumGameConfig.TwelvePalaceHelpPlayerLimit:
		return
	with Tra_TwelvePalaceSuccess:
		del TwelvePalaceDict[role.GetRoleID()]
		#发放奖励
		role.AddItem(EnumGameConfig.TwelvePalaceAwardCode, EnumGameConfig.TwelvePalaceAwardCnt)
	role.SendObj(SyncTwelvePalaceRoleData, [0 , {}])
	role.Msg(2, 0, GlobalPrompt.TwelvePalace_Awrad_Tips % (EnumGameConfig.TwelvePalaceAwardCode, EnumGameConfig.TwelvePalaceAwardCnt))

def RequestHarvestInAdvance(role, msg):
	'''
	客户端请求提前闯宫
	@param role:
	@param msg:
	'''
	if __IsTwelvePalaceBegin is False:
		return
	if not role.GetRoleID() in TwelvePalaceDict:
		return
	
	DEFINE_PRICE = EnumGameConfig.TwelvePalaceInAdvancePrice
	if Environment.EnvIsNA():
		DEFINE_PRICE = EnumGameConfig.TwelvePalaceInAdvancePrice_NA
	bd_RMB_cost = min(role.GetBindRMB(), DEFINE_PRICE)
	ubd_RMB_cost = DEFINE_PRICE - bd_RMB_cost

	if role.GetUnbindRMB() < ubd_RMB_cost:
		return
	with Tra_TwelvePalaceInAdvance:
		if ubd_RMB_cost > 0:
			role.DecUnbindRMB(ubd_RMB_cost)
		if bd_RMB_cost > 0:
			role.DecBindRMB(bd_RMB_cost)
		del TwelvePalaceDict[role.GetRoleID()]
		#发放奖励
		role.AddItem(EnumGameConfig.TwelvePalaceAwardCode, EnumGameConfig.TwelvePalaceAwardCnt)
	if role.GetCD(EnumCD.TwelvePalaceHelpCD) > 0:
		role.SetCD(EnumCD.TwelvePalaceHelpCD, 0)
	role.SendObj(SyncTwelvePalaceRoleData, [0 , {}])
	role.Msg(2, 0, GlobalPrompt.TwelvePalace_Awrad_Tips % (EnumGameConfig.TwelvePalaceAwardCode, EnumGameConfig.TwelvePalaceAwardCnt))

def AskForHelp(role, msg):	
	'''
	客户端请求招募炼金术士
	@param role:
	@param msg:
	'''
	if __IsTwelvePalaceBegin is False:
		return
	help_type = msg
	if role.GetCD(EnumCD.TwelvePalaceHelpCD) > 0:
		return
	role.SetCD(EnumCD.TwelvePalaceHelpCD, EnumGameConfig.TwelvePalaceAskForHelpCD)	
	if 1 == help_type:#世界喊话
		#世界求助
		cRoleMgr.Msg(7, 0, GlobalPrompt.TwelvePalace_AskForHelp_Tips % (role.GetRoleName(), role.GetRoleID()))	
	elif 2 == help_type:
		#玩家没有加入公会 
		if role.GetUnionID() == 0:
			return
		#公会求助
		UnionMgr.UnionMsg(role.GetUnionObj(), GlobalPrompt.TwelvePalace_AskForHelp_Tips % (role.GetRoleName(), role.GetRoleID()))

def RequestOpenPanel(role, msg):
	'''
	请求打开勇闯十二宫面板
	@param role:
	@param msg:
	'''
	if __IsTwelvePalaceBegin is False:
		return
	statu = 0
	help_dict = TwelvePalaceDict.get(role.GetRoleID(), None)
	if help_dict is not None:
		statu = 1
	role.SendObj(SyncTwelvePalaceRoleData, [statu , help_dict])

if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		#构建一个持久化字典用来保存进入了闯宫状态的角色，在活动结束时全部退出闯宫状态
		TwelvePalaceDict = Contain.Dict("TwelvePalaceDict", (2038, 1, 1), None, None)
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_StartCircularActive, TwelvePalaceStart)
		Event.RegEvent(Event.Eve_EndCircularActive, TwelvePalaceEnd)
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestTwelvePalace", "客户端请求开始闯宫勇闯十二宫"), RequestTwelvePalace)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestHelpTwelvePalace", "客户端请求协助他人勇闯十二宫"), RequestHelpOtherTwelvePalace)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestTwelvePalaceHarvest", "客户端请勇闯十二宫完美闯宫"), RequestTwelvePalaceHarvest)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestTwelvePalaceHarvestInAdvance", "客户端请勇闯十二宫提前闯宫"), RequestHarvestInAdvance)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TwelvePalaceAskForHelp", "客户端请求勇闯十二宫发送协助请求"), AskForHelp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_open_TwelvePalace", "客户端请求打开勇闯十二宫面板"), RequestOpenPanel)
