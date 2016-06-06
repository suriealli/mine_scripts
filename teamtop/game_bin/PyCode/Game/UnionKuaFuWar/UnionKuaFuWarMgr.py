#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.UnionKuaFuWar.UnionKuaFuWarMgr")
#===============================================================================
# 公会圣域争霸管理
#===============================================================================
import cComplexServer
import cProcess
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from World import Define
from ComplexServer.Time import Cron
from Game.GlobalData import ZoneName
from Game.Persistence import Contain
from Game.Role import Call
from Game.SysData import WorldData
from Game.Union import UnionMgr
from Game.UnionKuaFuWar import UnionKuaFuWarConfig, UnionKuaFuWarCross


if "_HasLoad" not in dir():
	CAN_JOIN_WAR = False				#是否能进入跨服争霸
	
	WAR_ZONE_ID = 0						#圣域争霸区域ID
	CAN_JOIN_WAR_UNION_ID_LIST = []		#可以参加圣域争霸的公会ID列表
	
	#消息
	Union_KuaFu_War_Sync_Union_Rank = AutoMessage.AllotMessage("Union_KuaFu_War_Sync_Union_Rank", "通知客户端公会圣域争霸公会排行榜")
	Union_KuaFu_War_Sync_Five_Role = AutoMessage.AllotMessage("Union_KuaFu_War_Sync_Five_Role", "通知客户端公会圣域争霸冠军公会五名玩家")
	
def AfterLoad():
	pass
	
def CalcZoneID():
	global WAR_ZONE_ID
	kaiFuDays = WorldData.GetWorldKaiFuDay()
	
	#开服天数是否满足条件
	for config in UnionKuaFuWarConfig.UNION_KUAFU_WAR_ZONE.itervalues():
		start, end = config.kaifuDay
		if kaiFuDays >= start and kaiFuDays <= end:
			WAR_ZONE_ID = config.zoneId
			break
		
	#世界等级是否满足天数
	if WorldData.GetWorldLevel() < 80:
		WAR_ZONE_ID = 0
	
#===============================================================================
# 显示
#===============================================================================
def ShowUnionRank(role):
	role.SendObj(Union_KuaFu_War_Sync_Union_Rank, UNION_KUAFU_WAR_END_DATA_DICT.get(1, []))

def ShowFiveRole(role):
	role.SendObj(Union_KuaFu_War_Sync_Five_Role, UNION_KUAFU_WAR_END_DATA_DICT.get(2, []))
	
#===============================================================================
# 跨服进程Call
#===============================================================================
def CrossCallWarEndRankReward(param):
	unionRankList, championRoleDataList = param
	
	global CAN_JOIN_WAR
	CAN_JOIN_WAR = False
	
	global UNION_KUAFU_WAR_END_DATA_DICT
	#排行榜列表
	UNION_KUAFU_WAR_END_DATA_DICT[1] = [unionRank[1] for unionRank in unionRankList]
	#公会前五名角色列表
	UNION_KUAFU_WAR_END_DATA_DICT[2] = championRoleDataList
	
#===============================================================================
# 时间
#===============================================================================
def TenMinuteReady():
	if UnionKuaFuWarConfig.GetWeekDay() not in (2, 5):
		return
	
	#清理
	WarClear()
	
	#确定区域
	CalcZoneID()
	
	#是否有效的区域ID
	if WAR_ZONE_ID == 0:
		return
	
	#生成有资格参赛的公会列表(排名前三名)
	sortList = UnionMgr.GetOtherUnionSortList()
	global CAN_JOIN_WAR_UNION_ID_LIST
	CAN_JOIN_WAR_UNION_ID_LIST = [ d[0] for d in sortList[:3]]
	
	#1~8分钟tick，9点02分~9点09分之间触发
	minutes = cProcess.ProcessID % 7 + 1
	cComplexServer.RegTick(minutes * 60, WarCanJoin)
	
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.UNION_KUAFU_WAR_TEN_MINUTE_READY_HEARSAY)
	
def WarCanJoin(callArgv, regparam):
	#可以进入游戏
	global CAN_JOIN_WAR
	CAN_JOIN_WAR = True
	
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.UNION_KUAFU_WAR_CAN_JOIN_HEARSAY)
	
def WarStartHearsay():
	if UnionKuaFuWarConfig.GetWeekDay() not in (2, 5):
		return
	
	#是否有效的区域ID
	if WAR_ZONE_ID == 0:
		return
	
	#通知跨服服务器信息
	Call.ServerCall(Define.GetDefaultCrossID(), "Game.UnionKuaFuWar.UnionKuaFuWarCross", "LogicCallServerData", (WAR_ZONE_ID, cProcess.ProcessID))
	
	#35分钟tick，9点45分触发
	cComplexServer.RegTick(35 * 60, WarEnd)
	
	#传闻
	cRoleMgr.Msg(1, 0, GlobalPrompt.UNION_KUAFU_WAR_START_HEARSAY)
	
def WarEnd(callArgv, regparam):
	if UnionKuaFuWarConfig.GetWeekDay() not in (2, 5):
		return
	
	global CAN_JOIN_WAR
	CAN_JOIN_WAR = False
	
def WarClear():
	global WAR_ZONE_ID
	WAR_ZONE_ID = 0
	
	global CAN_JOIN_WAR_UNION_ID_LIST
	CAN_JOIN_WAR_UNION_ID_LIST = []
	
	global UNION_KUAFU_WAR_END_DATA_DICT
	UNION_KUAFU_WAR_END_DATA_DICT.clear()

#===============================================================================
# 客户端请求
#===============================================================================
def RequstUnionKuaFuWarEnterScene(role, msg):
	'''
	客户端请求进入公会圣域争霸场景
	@param role:
	@param msg:
	'''
	if CAN_JOIN_WAR is False:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_KUAFU_WAR_ALL_GATE_BROKEN_PROMPT)
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#是否有参赛资格
	if unionObj.union_id not in CAN_JOIN_WAR_UNION_ID_LIST:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_KUAFU_WAR_CANT_ENTER_PROMPT)
		return
	
	score = 0
	zdl = role.GetZDL()
	for config in UnionKuaFuWarConfig.UNION_KUAFU_WAR_ZDL_SCORE_LIST:
		if zdl >= config.minZDL and zdl <= config.maxZDL:
			score = config.score
			break
	
	#传送到跨服
	role.GotoCrossServer(None, 376, 958, 579, UnionKuaFuWarCross.AfterJoinReadyScene, (ZoneName.ZoneName, WAR_ZONE_ID, cProcess.ProcessID, unionObj.name, score))
	
def RequstUnionKuaFuWarOpenMainPanel(role, msg):
	'''
	客户端请求打开公会圣域争霸主面板
	@param role:
	@param msg:
	'''
	ShowUnionRank(role)
	ShowFiveRole(role)
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#持久化数据
		#公会争霸结束数据{1: 排行榜列表, 2: 公会前五名角色列表}
		UNION_KUAFU_WAR_END_DATA_DICT = Contain.Dict("UNION_KUAFU_WAR_END_DATA_DICT", (2038, 1, 1), AfterLoad)
		
		#时间
		#准备时间在9点01分~9点05分之间
		if not Environment.EnvIsRU() and not Environment.EnvIsNA() and not Environment.EnvIsTK() and (not Environment.EnvIsPL()) and not Environment.EnvIsESP():
			#俄罗斯不开,土耳其不开,波兰、西班牙不开
			Cron.CronDriveByMinute((2038, 1, 1), TenMinuteReady, H="H == 21", M="M == 1")
			Cron.CronDriveByMinute((2038, 1, 1), WarStartHearsay, H="H == 21", M="M == 10")
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_KuaFu_War_Enter_Scene", "客户端请求进入公会圣域争霸场景"), RequstUnionKuaFuWarEnterScene)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_KuaFu_War_Open_Main_Panel", "客户端请求打开公会圣域争霸主面板"), RequstUnionKuaFuWarOpenMainPanel)
		
	
	
		
