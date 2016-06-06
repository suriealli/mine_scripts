#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionTreasure")
#===============================================================================
# 公会夺宝
#===============================================================================
import cComplexServer
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt, EnumFightStatistics
from ComplexServer.Log import AutoLog
from Game.Fight import FightEx
from Game.Role import Event, Call, Status
from Game.Role.Data import EnumInt32, EnumDayInt8, EnumInt8, EnumInt1
from Game.Union import UnionDefine, UnionConfig, UnionMgr
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType

if "_HasLoad" not in dir():
	#开启宝箱类型对应枚举
	BOXTYPE_TO_OPEN_ENUM_DICT = {UnionDefine.TREASURE_GOLD_IDX: EnumDayInt8.UnionLaunchGold, 
								UnionDefine.TREASURE_SILVER_IDX: EnumDayInt8.UnionLaunchSilver, 
								UnionDefine.TREASURE_COPPER_IDX: EnumDayInt8.UnionLaunchCopper}
	#领取宝箱类型对应枚举
	BOXTYPE_TO_GET_ENUM_DICT = {UnionDefine.TREASURE_GOLD_IDX: EnumInt8.UnionGetGold, 
								UnionDefine.TREASURE_SILVER_IDX: EnumInt8.UnionGetSilver, 
								UnionDefine.TREASURE_COPPER_IDX: EnumInt8.UnionGetCopper}
	#抢夺宝箱类型对应枚举
	BOXTYPE_TO_ROB_ENUM_DICT = {UnionDefine.TREASURE_GOLD_IDX: EnumDayInt8.Union_Rob_Gold_Box_Cnt, 
								UnionDefine.TREASURE_SILVER_IDX: EnumDayInt8.Union_Rob_Silver_Box_Cnt, 
								UnionDefine.TREASURE_COPPER_IDX: EnumDayInt8.Union_Rob_Copper_Box_Cnt}
	#宝箱类型对应抢夺次数
	BOXTYPE_TO_ROB_CNT_DICT = {UnionDefine.TREASURE_GOLD_IDX: EnumGameConfig.Union_Rob_Gold_Cnt_Max, 
							UnionDefine.TREASURE_SILVER_IDX: EnumGameConfig.Union_Rob_Silver_Cnt_Max, 
							UnionDefine.TREASURE_COPPER_IDX: EnumGameConfig.Union_Rob_Copper_Cnt_Max}
	#宝箱类型对应战斗阵营ID
	BOXTYPE_TO_MCID = {UnionDefine.TREASURE_GOLD_IDX: 7019, 
						UnionDefine.TREASURE_SILVER_IDX: 7018, 
						UnionDefine.TREASURE_COPPER_IDX: 7017}
	
	#消息
	Union_Show_Treasure_Panel = AutoMessage.AllotMessage("Union_Show_Treasure_Panel", "通知客户端显示夺宝面板")
	
def CanLaunchTreasure(role):
	'''
	能否开启夺宝
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	unionGoldBoxNeedRMB = EnumGameConfig.Union_Gold_Box_Need_RMB
	unionSilverBoxNeedRMB = EnumGameConfig.Union_Silver_Box_Need_RMB
	unionCopperBoxNeedRMB = EnumGameConfig.Union_Copper_Box_Need_RMB
	#版本判断
	if Environment.EnvIsNA():
		unionGoldBoxNeedRMB = EnumGameConfig.Union_Gold_Box_Need_RMB_NA
		unionSilverBoxNeedRMB = EnumGameConfig.Union_Silver_Box_Need_RMB_NA
		unionCopperBoxNeedRMB = EnumGameConfig.Union_Copper_Box_Need_RMB_NA
	elif Environment.EnvIsRU():
		unionGoldBoxNeedRMB = EnumGameConfig.Union_Gold_Box_Need_RMB_RU
		unionSilverBoxNeedRMB = EnumGameConfig.Union_Silver_Box_Need_RMB_RU
		unionCopperBoxNeedRMB = EnumGameConfig.Union_Copper_Box_Need_RMB_RU
	
	dayConsumeUnbindRMB = role.GetDayConsumeUnbindRMB()
	#判断是否满足开启宝箱条件
	if dayConsumeUnbindRMB >= unionGoldBoxNeedRMB:
		#是否开启过对应宝箱
		if role.GetDI8(EnumDayInt8.UnionLaunchGold):
			return
		#可以开启宝箱
		role.SetDI8(EnumDayInt8.UnionLaunchGold, 1)
		
	if dayConsumeUnbindRMB >= unionSilverBoxNeedRMB:
		#是否开启过对应宝箱
		if role.GetDI8(EnumDayInt8.UnionLaunchSilver):
			return
		#可以开启宝箱
		role.SetDI8(EnumDayInt8.UnionLaunchSilver, 1)
		
	if dayConsumeUnbindRMB >= unionCopperBoxNeedRMB:
		#是否开启过对应宝箱
		if role.GetDI8(EnumDayInt8.UnionLaunchCopper):
			return
		#可以开启宝箱
		role.SetDI8(EnumDayInt8.UnionLaunchCopper, 1)
		
	
def ShowTreasurePanel(role):
	'''
	显示夺宝面板
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	goldDict = unionObj.treasure[UnionDefine.TREASURE_GOLD_IDX]
	silverDict = unionObj.treasure[UnionDefine.TREASURE_SILVER_IDX]
	copperDict = unionObj.treasure[UnionDefine.TREASURE_COPPER_IDX]
	
	roleId = role.GetRoleID()
	#宝箱开启状态(宝箱类型, roleId, roleName, progress, 是否已经夺取该宝箱)
	goldList = [(UnionDefine.TREASURE_GOLD_IDX, rId, data[0], data[1], 1 if roleId in data[2] else 0) for rId, data in goldDict.iteritems()]
	silverList = [(UnionDefine.TREASURE_SILVER_IDX, rId, data[0], data[1], 1 if roleId in data[2] else 0) for rId, data in silverDict.iteritems()]
	copperList = [(UnionDefine.TREASURE_COPPER_IDX, rId, data[0], data[1], 1 if roleId in data[2] else 0) for rId, data in copperDict.iteritems()]
	
	sendList = []
	sendList.extend(goldList)
	sendList.extend(silverList)
	sendList.extend(copperList)
	#自己宝箱开启状态，公会所有宝箱状态
	role.SendObj(Union_Show_Treasure_Panel, sendList)
	
def OpenTreasureBox(role, boxType):
	'''
	打开夺宝宝箱
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#类型是否正确
	enum = BOXTYPE_TO_OPEN_ENUM_DICT.get(boxType)
	if not enum:
		return
	#类型是否正确
	getEnum = BOXTYPE_TO_GET_ENUM_DICT.get(boxType)
	if not getEnum:
		return
	
	#是否可以打开对应类型宝箱
	if role.GetDI8(enum) != 1:
		return
	
	roleId = role.GetRoleID()
	#是否已经打开宝箱
	roleTreasureDict = unionObj.treasure[boxType]
	if roleId in roleTreasureDict:
		return
	
	#设置已经点击开启
	role.SetDI8(enum, 2)
	
	#roleId -> [roleName, 开启进度, 角色参与挑战列表]
	roleTreasureDict[roleId] = [role.GetRoleName(), 0, []]
	#开启公会宝箱同时重置宝箱领取状态
	role.SetI8(getEnum, 0)
	
	roleName = role.GetRoleName()
	#公会广播和公会频道
	if boxType == UnionDefine.TREASURE_GOLD_IDX:
		unionObj.AddNews(GlobalPrompt.UNION_OPEN_TREASURE_GOLD_NEWS % roleName)
		UnionMgr.UnionMsg(unionObj, GlobalPrompt.UNION_OPEN_TREASURE_GOLD_MSG % roleName)
	elif boxType == UnionDefine.TREASURE_SILVER_IDX:
		unionObj.AddNews(GlobalPrompt.UNION_OPEN_TREASURE_SILVER_NEWS % roleName)
		UnionMgr.UnionMsg(unionObj, GlobalPrompt.UNION_OPEN_TREASURE_SILVER_MSG % roleName)
	elif boxType == UnionDefine.TREASURE_COPPER_IDX:
		unionObj.AddNews(GlobalPrompt.UNION_OPEN_TREASURE_COPPER_NEWS % roleName)
		UnionMgr.UnionMsg(unionObj, GlobalPrompt.UNION_OPEN_TREASURE_COPPER_MSG % roleName)
	else:
		pass
	
	#保存
	unionObj.HasChange()
	
	#刷新面板
	ShowTreasurePanel(role)
	UnionMgr.ShowMainPanel(role)
	
	WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Inc_UnionTreasure, boxType)	
	
	#公会感叹号
	UnionMgr.IsUnionExclamatoryMark(unionObj)
	
def RobTreasureBox(role, boxType, desRoleId):
	'''
	夺取宝箱
	@param role:
	@param boxType:
	@param desRoleId:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	roleId = role.GetRoleID()
	#是否公会成员
	if not unionObj.IsMember(roleId):
		return
	
	#公会历史贡献是否满足条件
	if unionObj.members[roleId][UnionDefine.M_H_CONTRIBUTION_IDX] < 1000:
		return
	
	#是否存在对应类型的宝箱
	if boxType not in unionObj.treasure:
		return
	
	#目标玩家是否已经开启宝箱
	roleTreasureDict = unionObj.treasure[boxType]
	if desRoleId not in roleTreasureDict:
		return
	
	#roleId -> [roleName, 开启进度, 角色参与挑战列表]
	robRoleIdList = roleTreasureDict[desRoleId][2]
	#是否已经夺取了宝箱
	if roleId in robRoleIdList:
		return
	
	#战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		#print "GE_EXC in RobTreasureBox already in fight"
		return
	
	mcid = BOXTYPE_TO_MCID[boxType]
	#战斗
	FightEx.PVE_UnionRobTreasure(role, mcid, 0, AfterFight, regParam = (boxType, desRoleId))
	
def GetTreasureBox(role, boxType):
	'''
	领取夺宝宝箱
	@param role:
	@param boxType:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#获取领取枚举
	enum = BOXTYPE_TO_GET_ENUM_DICT.get(boxType)
	if not enum:
		return
	
	#是否可以领取
	if role.GetI8(enum) != 1:
		return
		
	#设置已领取
	role.SetI8(enum, 2)
	
	#领取宝箱奖励
	level = role.GetLevel()
	levelToConfigDict = UnionConfig.UNION_TREASURE_GET.get(boxType)
	if not levelToConfigDict:
		return
	getConfig = levelToConfigDict.get(level)
	if not getConfig:
		return
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		tmpMoney = getConfig.money_fcm
	elif yyAntiFlag == 0:
		tmpMoney = getConfig.money
	else:
		tmpMoney = 0
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	
	role.IncMoney(tmpMoney)
	#提示
	role.Msg(2, 0, GlobalPrompt.Money_Tips % tmpMoney)
	
def WinRobTreasure(role, boxType, desRoleId, fightObj):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	roleId = role.GetRoleID()
	#是否公会成员
	if not unionObj.IsMember(roleId):
		return
	
	#是否存在对应类型的宝箱
	if boxType not in unionObj.treasure:
		return
	
	#目标玩家是否已经开启宝箱
	roleTreasureDict = unionObj.treasure[boxType]
	if desRoleId not in roleTreasureDict:
		return
	
	#roleId -> [roleName, 开启进度, 角色参与挑战列表]
	robRoleIdList = roleTreasureDict[desRoleId][2]
	#是否已经夺取了宝箱
	if roleId in robRoleIdList:
		return
	
	#记录已经夺取
	robRoleIdList.append(roleId)
	
	#进度增加
	roleTreasureDict[desRoleId][1] += 1
	
	#保存
	unionObj.HasChange()
	
	#是否满足激活宝箱条件
	if roleTreasureDict[desRoleId][1] == EnumGameConfig.Union_Get_Treasure_Need_Progress:
		#激活宝箱（数据库角色函数呼叫）
		Call.LocalDBCall(desRoleId, ActivateTreasure, boxType)
	
	#夺宝成功奖励
	RobTreasureReward(role, boxType, fightObj)
		
	#刷新面板
	ShowTreasurePanel(role)
	UnionMgr.ShowMainPanel(role)
	
def RobTreasureReward(role, boxType, fightObj):
	#奖励配置表
	level = role.GetLevel()
	levelToConfigDict = UnionConfig.UNION_TREASURE_ROB.get(boxType)
	if not levelToConfigDict:
		return
	robConfig = levelToConfigDict.get(level)
	if not robConfig:
		return
	
	#是否还有收益次数
	robCntEnum = BOXTYPE_TO_ROB_ENUM_DICT.get(boxType)
	if not robCntEnum:
		return
	robCnt = BOXTYPE_TO_ROB_CNT_DICT.get(boxType)
	if not robCnt:
		return
	if role.GetDI8(robCntEnum) >= robCnt:
		return
	
	#消耗收益次数
	role.IncDI8(robCntEnum, 1)
	
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		tmpMoney = robConfig.money_fcm
		tmpItemTuple = robConfig.itemList_fcm
	elif yyAntiFlag == 0:
		tmpMoney = robConfig.money
		tmpItemTuple = robConfig.itemList
	else:
		tmpMoney = 0
		tmpItemTuple = ()
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	
	
	showItemList = []
	#夺取宝箱奖励
	role.IncMoney(tmpMoney)
	for item in tmpItemTuple:
		role.AddItem(*item)
		showItemList.append(item)
		
	#战斗奖励统计显示
	roleId = role.GetRoleID()
	fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumMoney, tmpMoney)
	fightObj.set_fight_statistics(roleId, EnumFightStatistics.EnumItems, tmpItemTuple)
	
#===============================================================================
# 战斗相关
#===============================================================================
def OnLeave(fight, role, reason):
	# reason 0战斗结束离场；1战斗中途掉线
	pass
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利；None战斗未结束
	# 注意，只有在角色离开的回调函数中fight.result才有可能为None

def AfterFight(fight):
	boxType, desRoleId = fight.after_fight_param
	
	# fight.round当前战斗回合
	# fight.result如果没“bug”的话将会取值1左阵营胜利；0平局；-1右阵营胜利
	# 故判断胜利请按照下面这种写法明确判定
	if fight.result == 1:
		#获取战斗玩家
		if not fight.left_camp.roles:
			return
		left_camp_roles_list = list(fight.left_camp.roles)
		role = left_camp_roles_list[0]
		#日志
		with TraUnionTreasureRobReward:
			#战斗胜利
			WinRobTreasure(role, boxType, desRoleId, fight)

def AfterPlay(fight):
	pass
		
#===============================================================================
# call
#===============================================================================
def ActivateTreasure(role, param):
	'''
	激活夺宝宝箱
	@param role:
	@param param:
	'''
	boxType = param
	
	enum = BOXTYPE_TO_GET_ENUM_DICT.get(boxType)
	if not enum:
		return
	
	#已经激活
	if role.GetI8(enum):
		return
	
	#激活
	role.SetI8(enum, 1)
	
#===============================================================================
# 数组改变调用
#===============================================================================
def AfterChangeUnbindRMB(role, param):
	'''
	神石改变
	@param role:
	@param param:
	'''
	oldValue, newValue = param
	if newValue >= oldValue:
		return
	#能否开启夺宝
	CanLaunchTreasure(role)

def AfterChangeUnbindRMB_Q(role, param):
	'''
	神石改变
	@param role:
	@param param:
	'''
	oldValue, newValue = param
	if newValue >= oldValue:
		unionObj = role.GetUnionObj()
		if not unionObj:
			return
		unionObj.other_data[UnionDefine.O_TotalFillRMB] = unionObj.other_data.get(UnionDefine.O_TotalFillRMB, 0) + \
				(newValue - oldValue)
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_UnionTotalFill, unionObj)
		
	else:
		#能否开启夺宝
		CanLaunchTreasure(role)
#===============================================================================
# 事件
#===============================================================================
def OnRoleDayClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	#清理领取宝箱状态
	for enum in BOXTYPE_TO_GET_ENUM_DICT.itervalues():
		#如果有宝箱并且已经领取过则重置(如果是1则还未领取宝箱不能清空)
		if role.GetI8(enum) == 2:
			role.SetI8(enum, 0)
			
#===============================================================================
# 时间
#===============================================================================
def AfterNewDay():
	btData = UnionMgr.BT.GetData()
	for unionId in btData.iterkeys():
		unionObj = UnionMgr.GetUnionObjByID(unionId)
		if not unionObj:
			continue
		
		#删除公会夺宝宝箱
		hasChange = False
		if unionObj.treasure[UnionDefine.TREASURE_GOLD_IDX]:
			unionObj.treasure[UnionDefine.TREASURE_GOLD_IDX] = {}
			hasChange = True
		if unionObj.treasure[UnionDefine.TREASURE_SILVER_IDX]:
			unionObj.treasure[UnionDefine.TREASURE_SILVER_IDX] = {}
			hasChange = True
		if unionObj.treasure[UnionDefine.TREASURE_COPPER_IDX]:
			unionObj.treasure[UnionDefine.TREASURE_COPPER_IDX] = {}
			hasChange = True
		if UnionDefine.O_TotalFillRMB in unionObj.other_data:
			unionObj.other_data[UnionDefine.O_TotalFillRMB] = 0
			hasChange = True
		if hasChange is True:
			#如果改变则保存
			unionObj.HasChange()
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestUnionOpenTreasurePanel(role, msg):
	'''
	客户端请求打开公会夺宝面板
	@param role:
	@param msg:
	'''
	ShowTreasurePanel(role)
	
def RequestUnionOpenTreasureBox(role, msg):
	'''
	客户端请求打开夺宝宝箱
	@param role:
	@param msg:
	'''
	boxType = msg
	
	#日志
	with TraUnionTreasureOpenBox:
		OpenTreasureBox(role, boxType)
	
def RequestUnionGetTreasureBox(role, msg):
	'''
	客户端请求领取夺宝宝箱
	@param role:
	@param msg:
	'''
	boxType = msg
	
	#日志
	with TraUnionTreasureGetReward:
		GetTreasureBox(role, boxType)
	
def RequestUnionRobTreasureBox(role, msg):
	'''
	客户端请求夺取夺宝宝箱
	@param role:
	@param msg:
	'''
	boxType, desRoleId = msg
	
	RobTreasureBox(role, boxType, desRoleId)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#每日调用
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
	
	#每日清理调用
	Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	#改变神石事件
	Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB_Q)
	Event.RegEvent(Event.AfterChangeUnbindRMB_S, AfterChangeUnbindRMB)
	
	#日志
	TraUnionTreasureOpenBox = AutoLog.AutoTransaction("TraUnionTreasureOpenBox", "公会夺宝开启宝箱")
	TraUnionTreasureGetReward = AutoLog.AutoTransaction("TraUnionTreasureGetReward", "公会夺宝领取宝箱奖励")
	TraUnionTreasureRobReward = AutoLog.AutoTransaction("TraUnionTreasureRobReward", "公会夺宝夺取宝箱奖励")
	
	if Environment.HasLogic and not Environment.IsCross:
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Treasure_Panel", "客户端请求打开公会夺宝面板"), RequestUnionOpenTreasurePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Treasure_Box", "客户端请求开启夺宝宝箱"), RequestUnionOpenTreasureBox)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Get_Treasure_Box", "客户端请求领取夺宝宝箱"), RequestUnionGetTreasureBox)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Rob_Treasure_Box", "客户端请求夺取夺宝宝箱"), RequestUnionRobTreasureBox)
		
