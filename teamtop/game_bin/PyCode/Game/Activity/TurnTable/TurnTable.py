#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.TurnTable.TurnTable")
#===============================================================================
# 全名转转乐
#===============================================================================
import Environment
import cRoleMgr
import cDateTime
import cProcess
import cNetMessage
import cComplexServer
from Common.Message import AutoMessage, PyMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer import Init
from ComplexServer.Plug.Control import ControlProxy
from Game.Persistence import Contain
from Game.Activity.TurnTable import TurnTableConfig
from Game.Role import Call, Event
from Game.GlobalData import ZoneName
from ComplexServer.Log import AutoLog

if "_HasLoad" not in dir():
	IsStart = False
	IsControlSync = False
	
	BroadRoleIDSet = set()					#需要广播的角色ID集合
	
	TurnTableRecordList = []				#奖励记录
	TurnTableTurnRecord = {}				#玩家是否中奖{roleId:抽取次数}
	PoolValue = 0							#奖池神石数
	EndTime = 0								#活动结束时间
	
	TurnTableStart = AutoMessage.AllotMessage("TurnTableStart", "全名转转乐活动开启")
	TurnTableIndex = AutoMessage.AllotMessage("TurnTableIndex", "全名转转乐转盘索引")
	TurnTableIndexEx = AutoMessage.AllotMessage("TurnTableIndexEx", "全名转转乐转盘索引(回调)")
	TurnTablePoolValue = AutoMessage.AllotMessage("TurnTablePoolValue", "全名转转乐奖池神石数")
	#区服+角色名+奖励+时间
	TurnTableRecord = AutoMessage.AllotMessage("TurnTableRecord", "全名转转乐获奖记录")
	#抽奖{1:抽奖次数, 2:set(已领取的奖励集合)}
	TurnTableBoxData = AutoMessage.AllotMessage("TurnTableBoxData", "全名转转乐抽奖数据")
	
	TurnTableOneTurn_Log = AutoLog.AutoTransaction("TurnTableOneTurn_Log", "全名转转乐一次转动")
	TurnTableTenTurn_Log = AutoLog.AutoTransaction("TurnTableTenTurn_Log", "全名转转乐十次转动")
	TurnTableFiftyTurn_Log = AutoLog.AutoTransaction("TurnTableFiftyTurn_Log", "全名转转乐五十次转动")
	TurnTableBoxReward_Log = AutoLog.AutoTransaction("TurnTableBoxReward_Log", "全名转转乐宝箱奖励")
	
	
#===============================================================================
# 活动开关
#===============================================================================
def OpenActive(callArgv, regparam):
	global IsStart, EndTime, TurnTableDict
	if IsStart:
		print 'GE_EXC, repeat start TurnTable'
	IsStart = True
	
	activeID, endTime = regparam
	if activeID != TurnTableDict.get('activeID'):
		#活动开启时如果活动id不一样, 清理数据
		TurnTableDict.clear()
		
		TurnTableDict['activeID'] = activeID
		TurnTableDict.HasChange()
	
	EndTime = endTime
	
	#活动开启的时候向控制进程请求数据
	ControlProxy.SendControlMsg(PyMessage.Control_GetGlobalTurnTablePoolValue, cProcess.ProcessID)
	
	cNetMessage.PackPyMsg(TurnTableStart, endTime)
	cRoleMgr.BroadMsg()
	
def CloseActive(callArgv, regparam):
	global IsStart, PoolValue, BroadRoleIDSet, TurnTableRecordList, TurnTableTurnRecord
	if not IsStart:
		print 'GE_EXC, repeat end TurnTable'
	IsStart = False
	PoolValue = 0
	
	#活动结束后清理
	BroadRoleIDSet = set()
	TurnTableRecordList = []
	TurnTableTurnRecord = {}
	
	cNetMessage.PackPyMsg(TurnTableStart, 0)
	cRoleMgr.BroadMsg()
#===============================================================================
# 客户端请求
#===============================================================================
def RequestOpenPanel(role, msg):
	'''
	全名转转乐打开面板
	@param role:
	@param msg:
	'''
	global IsStart, IsControlSync
	if not IsStart: return
	if not IsControlSync: return
	
	global PoolValue, BroadRoleIDSet, TurnTableDict
	roleId = role.GetRoleID()
	
	if roleId not in BroadRoleIDSet:
		BroadRoleIDSet.add(roleId)
	
	role.SendObj(TurnTablePoolValue, PoolValue)
	role.SendObj(TurnTableRecord, TurnTableRecordList)
	role.SendObj(TurnTableBoxData, TurnTableDict.get(role.GetRoleID(), {}))
	
def RequestClosePanel(role, msg):
	'''
	全名转转乐关闭面板
	@param role:
	@param msg
	'''
	global IsStart, BroadRoleIDSet
	if not IsStart: return
	
	roleId = role.GetRoleID()
	
	if roleId in BroadRoleIDSet:
		BroadRoleIDSet.discard(roleId)
	
def RequestTurn(role, msg):
	'''
	全名转转乐请求抽取
	@param role:
	@param msg:
	'''
	global IsStart, IsControlSync
	if not IsStart: return
	
	if not IsControlSync:
		#如果控制进程还没有同步数据过来的话不能抽取
		return
	
	#等级
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.TurnTableMinLevel:
		return
	#计算等级段
	level = GetCloseValue(roleLevel, TurnTableConfig.TurnTableLevel_List)
	if not level:
		return
	
	isJump, cnt = msg
	
	#计算抽奖需要神石
	needUnbindRMB_Q = cnt * EnumGameConfig.TurnTableSinglePrice
	if Environment.EnvIsNA():
		needUnbindRMB_Q = cnt * EnumGameConfig.TurnTableSinglePrice_NA
	if role.GetUnbindRMB_Q() < needUnbindRMB_Q:
		return
	
	#计算当前能抽奖奖池档次
	global TurnTableDict, PoolValue, TurnTableTurnRecord
	roleId = role.GetRoleID()
	if roleId not in TurnTableDict:
		TurnTableDict[roleId] = {1:0, 2:set()}
		turnCnt = 0
	else:
		turnCnt = TurnTableDict.get(roleId, {}).get(1, 0)
	
	TTPG = TurnTableConfig.TurnTablePoolGrade_Dict.get
	TTPL = TurnTableConfig.TurnTablePoolGrade_List
	TTCG = TurnTableConfig.TurnTableCntGrade_Dict.get
	TTCL = TurnTableConfig.TurnTableCntGrade_List
	
	grade = 5 if TurnTableTurnRecord.get(roleId, 0) >= EnumGameConfig.TurnTableJumpGrade else min(TTPG(GetCloseValueEx(PoolValue, TTPL), 0), TTCG(GetCloseValueEx(turnCnt, TTCL), 0))
	
	#抽奖
	if cnt == 1:
		OneTurn(role, level, isJump, grade, needUnbindRMB_Q)
	elif cnt == 10:
		TenTurn(role, level, grade, needUnbindRMB_Q)
	elif cnt == 50:
		FiftyTurn(role, level, grade, needUnbindRMB_Q)
	
def RequestOpenBox(role, msg):
	'''
	全名转转乐请求开启宝箱
	@param role:
	@param msg:
	'''
	global IsStart, TurnTableDict
	if not IsStart: return
	if not TurnTableDict.returnDB: return
	
	if role.GetLevel() < EnumGameConfig.TurnTableMinLevel:
		return
	
	turnDict = TurnTableDict.get(role.GetRoleID())
	if not turnDict:
		return
	turnCnt = turnDict.get(1)
	if not turnCnt:
		return
	
	boxIndex = msg
	rewardBoxSet = turnDict.get(2, set())
	if boxIndex in rewardBoxSet:
		return
	
	cfg = TurnTableConfig.TurnTableBox_Dict.get(boxIndex)
	if not cfg:
		return
	if turnCnt < cfg.needCnt:
		return
	rewardBoxSet.add(boxIndex)
	
	TurnTableDict.HasChange()
	
	tips = GlobalPrompt.Reward_Tips
	with TurnTableBoxReward_Log:
		if cfg.rewardItems:
			for item in cfg.rewardItems:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % item
		if cfg.rewardMoney:
			role.IncMoney(cfg.rewardMoney)
			tips += GlobalPrompt.Money_Tips % cfg.rewardMoney
		if cfg.rewardBindRMB:
			role.IncBindRMB(cfg.rewardBindRMB)
			tips += GlobalPrompt.BindRMB_Tips % cfg.rewardBindRMB
	
	role.SendObj(TurnTableBoxData, turnDict)
	
	role.Msg(2, 0, tips)
#===============================================================================
# 辅助函数
#===============================================================================
def GetCloseValue(value, valueList):
	tmpValue = 0
	for i in valueList:
		if i > value:
			#返回第一个大于value的上一个值
			return tmpValue
		tmpValue = i
	else:
		#没有找到返回最后一个值
		return tmpValue
	
def GetCloseValueEx(value, valueList):
	tmpValue = 0
	for i in valueList:
		if i > value:
			#返回第一个大于value的上一个值
			return tmpValue
		tmpValue = i
	else:
		#找不到的话返回0
		return 0
	
def OneTurn(role, level, isJump, grade, needUnbindRMB_Q):
	if role.PackageEmptySize() < 1:
		#一次抽取需要至少一个背包空格
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	global PoolValue, TurnTableDict
	
	#根据档次、等级段随机
	if grade == 5:
		randomObj = TurnTableConfig.TurnTableRandomEx_Dict.get(level)
	else:
		randomObj = TurnTableConfig.TurnTableRandom_Dict.get(grade, {}).get(level)
	
	if not randomObj:
		return
	tableIndex = randomObj.RandomOne()
	
	#配置
	if grade == 5:
		cfg = TurnTableConfig.TurnTableEx_Dict.get((tableIndex, level))
	else:
		cfg = TurnTableConfig.TurnTable_Dict.get((tableIndex, level))
	
	if not cfg:
		print 'GE_EXC, TurnTable OneTurn can not find tableIndex %s, level %s in TurnTable_Dict' % (tableIndex, level)
		return
	
	with TurnTableOneTurn_Log:
		#进入奖池神石
		PoolValue += EnumGameConfig.TurnTableIntoPool
		
		role.DecUnbindRMB_Q(needUnbindRMB_Q)
		
		TurnTableDict[role.GetRoleID()][1] += 1
		TurnTableDict.HasChange()
		
	global TurnTableTurnRecord
	roleId = role.GetRoleID()
	if (roleId not in TurnTableTurnRecord) or cfg.isRare:
		TurnTableTurnRecord[roleId] = 0
	else:
		TurnTableTurnRecord[roleId] += 1
	
	#不跳过转盘特效, 等待客户端回调后发奖
	role.SendObjAndBack(TurnTableIndexEx, tableIndex, 15, CallBackFun, (cfg, needUnbindRMB_Q))
	
def CallBackFun(role, callargv, regparam):
	cfg, needUnbindRMB_Q = regparam
	
	global PoolValue, TurnTableDict, BroadRoleIDSet, IsStart
	
	if not IsStart:
		role.IncUnbindRMB_Q(needUnbindRMB_Q)
		role.Msg(2, 0, GlobalPrompt.TurnTableEnd % needUnbindRMB_Q)
		return
	
	tips = GlobalPrompt.Reward_Tips
	roleName = role.GetRoleName()
	
	with TurnTableOneTurn_Log:
		if cfg.rewardItems:
			role.AddItem(*cfg.rewardItems)
			
			if cfg.isRumor:
					Call.ServerCall(0, "Game.Activity.TurnTable.TurnTable", "AllServerRumor", (ZoneName.ZoneName, role.GetRoleName(), 1, cfg.rewardItems[0], cfg.rewardItems[1]))
					cRoleMgr.Msg(1, 0, GlobalPrompt.TurnTableRewardItem_TIPS % (roleName, cfg.rewardItems[0], cfg.rewardItems[1]))
			tips += GlobalPrompt.Item_Tips % cfg.rewardItems
		else:
			incRMB = PoolValue * cfg.rewardUnbindRMB_S_Percent / 100
			
			PoolValue -= incRMB
			
			role.IncUnbindRMB_S(incRMB)
			
			if cfg.isRumor:
					Call.ServerCall(0, "Game.Activity.TurnTable.TurnTable", "AllServerRumor", (ZoneName.ZoneName, role.GetRoleName(), 0, 0, incRMB))
					cRoleMgr.Msg(1, 0, GlobalPrompt.TurnTableRewardRMB_TIPS % (roleName, incRMB))
			tips += GlobalPrompt.UnBindRMB_Tips % incRMB
	
	#通知客户端最新奖池数据
	RFR = cRoleMgr.FindRoleByRoleID
	for troleId in BroadRoleIDSet:
		trole = RFR(troleId)
		if not trole:
			continue
		trole.SendObj(TurnTablePoolValue, PoolValue)
	role.SendObj(TurnTableBoxData, TurnTableDict.get(role.GetRoleID(), {}))
	
	role.Msg(2, 0, tips)
	
def TenTurn(role, level, grade, needUnbindRMB_Q):
	if role.PackageEmptySize() < 10:
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	global PoolValue, TurnTableDict
	
	if grade == 5:
		randomObj = TurnTableConfig.TurnTableRandomEx_Dict.get(level)
	else:
		randomObj = TurnTableConfig.TurnTableRandom_Dict.get(grade, {}).get(level)
	
	if not randomObj:
		return
	tableIndexList = []
	for _ in xrange(10):
		#注意这里不能用RandomMany
		tableIndexList.append(randomObj.RandomOne())
	
	global PoolValue, TurnTableDict, BroadRoleIDSet
	tips = GlobalPrompt.Reward_Tips
	roleName = role.GetRoleName()
	
	if grade == 5:
		TTG = TurnTableConfig.TurnTable_Dict.get
	else:
		TTG = TurnTableConfig.TurnTableEx_Dict.get
	
	TTPG = TurnTableConfig.TurnTablePoolGrade_Dict.get
	TTPL = TurnTableConfig.TurnTablePoolGrade_List
	TTCG = TurnTableConfig.TurnTableCntGrade_Dict.get
	TTCL = TurnTableConfig.TurnTableCntGrade_List
	
	with TurnTableTenTurn_Log:
		#进入奖池神石
		PoolValue += EnumGameConfig.TurnTableIntoPool * 10
		
		role.DecUnbindRMB_Q(needUnbindRMB_Q)
		
		isRare = False
		
		itemDict = {}
		cnt = 0
		for tableIndex in tableIndexList:
			cfg = TTG((tableIndex, level))
			if not cfg:
				print 'GE_EXC, TurnTable TenTurn can not find tableIndex %s, level %s in TurnTable_Dict' % (tableIndex, level)
				continue
			
			#记录抽了多少次
			cnt += 1
			
			if cfg.rewardItems:
				if cfg.rewardItems[0] not in itemDict:
					itemDict[cfg.rewardItems[0]] = cfg.rewardItems[1]
				else:
					itemDict[cfg.rewardItems[0]] += cfg.rewardItems[1]
				
				if cfg.isRumor:
					Call.ServerCall(0, "Game.Activity.TurnTable.TurnTable", "AllServerRumor", (ZoneName.ZoneName, role.GetRoleName(), 1, cfg.rewardItems[0], cfg.rewardItems[1]))
					cRoleMgr.Msg(1, 0, GlobalPrompt.TurnTableRewardItem_TIPS % (roleName, cfg.rewardItems[0], cfg.rewardItems[1]))
					
			else:
				incRMB = PoolValue * cfg.rewardUnbindRMB_S_Percent / 100
				
				#扣奖池神石
				PoolValue -= incRMB
				#获得系统神石
				role.IncUnbindRMB_S(incRMB)
				
				if cfg.isRumor:
					Call.ServerCall(0, "Game.Activity.TurnTable.TurnTable", "AllServerRumor", (ZoneName.ZoneName, role.GetRoleName(), 0, 0, incRMB))
					cRoleMgr.Msg(1, 0, GlobalPrompt.TurnTableRewardRMB_TIPS % (roleName, incRMB))
				tips += GlobalPrompt.UnBindRMB_Tips % incRMB
				
			#是否抽中稀有物品
			isRare = True if isRare or cfg.isRare else False
			#稀有物品需要更换奖池
			if isRare:
				#重算奖池档次
				grade = min(TTPG(GetCloseValueEx(PoolValue, TTPL), 0), TTCG(GetCloseValueEx(TurnTableDict.get(role.GetRoleID(), 0), TTCL), 0))
				randomObj = TurnTableConfig.TurnTableRandom_Dict.get(grade, {}).get(level)
				if not randomObj:
					return
				#再随机出剩下的
				tableIndexList = []
				for _ in xrange(10 - cnt):
					#注意这里不能用RandomMany
					tableIndexList.append(randomObj.RandomOne())
				
				#这里用回原来的配置
				TTG = TurnTableConfig.TurnTable_Dict.get
				for tableIndex in tableIndexList:
					cfg = TTG((tableIndex, level))
					if not cfg:
						print 'GE_EXC, TurnTable TenTurn can not find tableIndex %s, level %s in TurnTable_Dict' % (tableIndex, level)
						continue
					
					if cfg.rewardItems:
						if cfg.rewardItems[0] not in itemDict:
							itemDict[cfg.rewardItems[0]] = cfg.rewardItems[1]
						else:
							itemDict[cfg.rewardItems[0]] += cfg.rewardItems[1]
					
						if cfg.isRumor:
							Call.ServerCall(0, "Game.Activity.TurnTable.TurnTable", "AllServerRumor", (ZoneName.ZoneName, role.GetRoleName(), 1, cfg.rewardItems[0], cfg.rewardItems[1]))
							cRoleMgr.Msg(1, 0, GlobalPrompt.TurnTableRewardItem_TIPS % (roleName, cfg.rewardItems[0], cfg.rewardItems[1]))
						
					else:
						incRMB = PoolValue * cfg.rewardUnbindRMB_S_Percent / 100
						
						#扣奖池神石
						PoolValue -= incRMB
						#获得系统神石
						role.IncUnbindRMB_S(incRMB)
						
						if cfg.isRumor:
							Call.ServerCall(0, "Game.Activity.TurnTable.TurnTable", "AllServerRumor", (ZoneName.ZoneName, role.GetRoleName(), 0, 0, incRMB))
							cRoleMgr.Msg(1, 0, GlobalPrompt.TurnTableRewardRMB_TIPS % (roleName, incRMB))
						tips += GlobalPrompt.UnBindRMB_Tips % incRMB
				break
		
		for coding, cnt in itemDict.iteritems():
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips % (coding, cnt)
		
	TurnTableDict[role.GetRoleID()][1] += 10
	TurnTableDict.HasChange()
	
	global TurnTableTurnRecord
	roleId = role.GetRoleID()
	if (roleId not in TurnTableTurnRecord) or isRare:
		TurnTableTurnRecord[roleId] = 0
	else:
		TurnTableTurnRecord[roleId] += 10
	
	#通知客户端最新奖池数据
	RFR = cRoleMgr.FindRoleByRoleID
	for troleId in BroadRoleIDSet:
		trole = RFR(troleId)
		if not trole:
			continue
		trole.SendObj(TurnTablePoolValue, PoolValue)
	role.SendObj(TurnTableBoxData, TurnTableDict.get(role.GetRoleID(), {}))
	
	role.Msg(2, 0, tips)
	
def FiftyTurn(role, level, grade, needUnbindRMB_Q):
	if role.PackageEmptySize() < 12:
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	global PoolValue, TurnTableDict
	
	if grade == 5:
		randomObj = TurnTableConfig.TurnTableRandomEx_Dict.get(level)
	else:
		randomObj = TurnTableConfig.TurnTableRandom_Dict.get(grade, {}).get(level)
		
	if not randomObj:
		return
	tableIndexList = []
	for _ in xrange(50):
		#注意这里不能用RandomMany
		tableIndexList.append(randomObj.RandomOne())
	
	global PoolValue, TurnTableDict, BroadRoleIDSet, TurnTableTurnRecord
	
	tips = GlobalPrompt.Reward_Tips
	roleName = role.GetRoleName()
	
	if grade == 5:
		TTG = TurnTableConfig.TurnTable_Dict.get
	else:
		TTG = TurnTableConfig.TurnTableEx_Dict.get
	
	TTPG = TurnTableConfig.TurnTablePoolGrade_Dict.get
	TTPL = TurnTableConfig.TurnTablePoolGrade_List
	TTCG = TurnTableConfig.TurnTableCntGrade_Dict.get
	TTCL = TurnTableConfig.TurnTableCntGrade_List
	
	with TurnTableFiftyTurn_Log:
		#进入奖池神石
		PoolValue += EnumGameConfig.TurnTableIntoPool * 50
		#扣除抽奖神石
		role.DecUnbindRMB_Q(needUnbindRMB_Q)
		
		itemDict = {}
		isRare = False
		cnt = 0
		
		for tableIndex in tableIndexList:
			cfg = TTG((tableIndex, level))
			if not cfg:
				print 'GE_EXC, TurnTable FiftyTurn can not find tableIndex %s, level %s in TurnTable_Dict' % (tableIndex, level)
				continue
			
			cnt += 1
			
			if cfg.rewardItems:
				if cfg.rewardItems[0] not in itemDict:
					itemDict[cfg.rewardItems[0]] = cfg.rewardItems[1]
				else:
					itemDict[cfg.rewardItems[0]] += cfg.rewardItems[1]
					
				if cfg.isRumor:
					Call.ServerCall(0, "Game.Activity.TurnTable.TurnTable", "AllServerRumor", (ZoneName.ZoneName, role.GetRoleName(), 1, cfg.rewardItems[0], cfg.rewardItems[1]))
					cRoleMgr.Msg(1, 0, GlobalPrompt.TurnTableRewardItem_TIPS % (roleName, cfg.rewardItems[0], cfg.rewardItems[1]))
			else:
				
				incRMB = PoolValue * cfg.rewardUnbindRMB_S_Percent / 100
				
				#抽中两个1%, 先扣1%再扣1%
				#神石直接扣, 不能直接扣2%
				PoolValue -= incRMB
				#获得系统神石
				role.IncUnbindRMB_S(incRMB)
				
				if cfg.isRumor:
					Call.ServerCall(0, "Game.Activity.TurnTable.TurnTable", "AllServerRumor", (ZoneName.ZoneName, role.GetRoleName(), 0, 0, incRMB))
					cRoleMgr.Msg(1, 0, GlobalPrompt.TurnTableRewardRMB_TIPS % (roleName, incRMB))
				tips += GlobalPrompt.UnBindRMB_Tips % incRMB
		
			#是否抽中稀有物品
			isRare = True if isRare or cfg.isRare else False
			
			if isRare:
				#重算
				grade = min(TTPG(GetCloseValueEx(PoolValue, TTPL), 0), TTCG(GetCloseValueEx(TurnTableDict.get(role.GetRoleID(), 0), TTCL), 0))
				randomObj = TurnTableConfig.TurnTableRandom_Dict.get(grade, {}).get(level)
				if not randomObj:
					return
				tableIndexList = []
				for _ in xrange(50 - cnt):
					#注意这里不能用RandomMany
					tableIndexList.append(randomObj.RandomOne())
				
				#这里用回原来的配置
				TTG = TurnTableConfig.TurnTable_Dict.get
				for tableIndex in tableIndexList:
					cfg = TTG((tableIndex, level))
					if not cfg:
						print 'GE_EXC, TurnTable TenTurn can not find tableIndex %s, level %s in TurnTable_Dict' % (tableIndex, level)
						continue
					
					if cfg.rewardItems:
						if cfg.rewardItems[0] not in itemDict:
							itemDict[cfg.rewardItems[0]] = cfg.rewardItems[1]
						else:
							itemDict[cfg.rewardItems[0]] += cfg.rewardItems[1]
					
						if cfg.isRumor:
							Call.ServerCall(0, "Game.Activity.TurnTable.TurnTable", "AllServerRumor", (ZoneName.ZoneName, role.GetRoleName(), 1, cfg.rewardItems[0], cfg.rewardItems[1]))
							cRoleMgr.Msg(1, 0, GlobalPrompt.TurnTableRewardItem_TIPS % (roleName, cfg.rewardItems[0], cfg.rewardItems[1]))
						
					else:
						incRMB = PoolValue * cfg.rewardUnbindRMB_S_Percent / 100
						
						#扣奖池神石
						PoolValue -= incRMB
						#获得系统神石
						role.IncUnbindRMB_S(incRMB)
						
						if cfg.isRumor:
							Call.ServerCall(0, "Game.Activity.TurnTable.TurnTable", "AllServerRumor", (ZoneName.ZoneName, role.GetRoleName(), 0, 0, incRMB))
							cRoleMgr.Msg(1, 0, GlobalPrompt.TurnTableRewardRMB_TIPS % (roleName, incRMB))
						tips += GlobalPrompt.UnBindRMB_Tips % incRMB
				break
		
		for coding, cnt in itemDict.iteritems():
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips % (coding, cnt)
		
	TurnTableDict[role.GetRoleID()][1] += 50
	TurnTableDict.HasChange()
	
	roleId = role.GetRoleID()
	if (roleId not in TurnTableTurnRecord) or isRare:
		TurnTableTurnRecord[roleId] = 0
	else:
		TurnTableTurnRecord[roleId] += 50
	
	#通知客户端最新奖池数据
	RFR = cRoleMgr.FindRoleByRoleID
	for troleId in BroadRoleIDSet:
		trole = RFR(troleId)
		if not trole:
			continue
		trole.SendObj(TurnTablePoolValue, PoolValue)
	role.SendObj(TurnTableBoxData, TurnTableDict.get(role.GetRoleID(), {}))
	
	role.Msg(2, 0, tips)
#===============================================================================
# ServerCall函数
#===============================================================================
def AllServerRumor(param):
	global TurnTableRecordList, BroadRoleIDSet
	zName, rName, isItem, coding, cnt = param
	
	if len(TurnTableRecordList) > 100:
		TurnTableRecordList.pop(0)
	TurnTableRecordList.append([zName, rName, isItem, coding, cnt, cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()])
	
	RFR = cRoleMgr.FindRoleByRoleID
	for troleId in BroadRoleIDSet:
		trole = RFR(troleId)
		if not trole:
			continue
		trole.SendObj(TurnTableRecord, TurnTableRecordList)
#===============================================================================
# 持久化数据载入
#===============================================================================
def AfterLoad():
	if not TurnTableDict:
		#活动id不一样的时候清理数据
		TurnTableDict["activeID"] = 0
		TurnTableDict.HasChange()
	
	#持久化数据载回后尝试开启全名转转乐
	from Game.Activity import CircularActive
	for cfg in CircularActive.TurnTableActive_Dict.itervalues():
		cfg.Active()
	
def RequestLogicTurnTablePoolValue(sessionid, msg):
	#控制进程请求逻辑进程返回数据
	global PoolValue
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, PoolValue))

def UpdataTurnTablePoolValueToLogic(sessionid, msg):
	#控制进程更新数据给逻辑进程
	global PoolValue, IsControlSync, BroadRoleIDSet
	PoolValue = msg
	IsControlSync = True
	
	RFR = cRoleMgr.FindRoleByRoleID
	for troleId in BroadRoleIDSet:
		trole = RFR(troleId)
		if not trole:
			continue
		trole.SendObj(TurnTablePoolValue, PoolValue)
	
def TryUpdate():
	global IsStart
	if not IsStart: return
	
	#起服的时候尝试向控制进程请求数据
	ControlProxy.SendControlMsg(PyMessage.Control_GetGlobalTurnTablePoolValue, cProcess.ProcessID)
#===============================================================================
# 角色事件
#===============================================================================
def BeforeExit(role, param):
	global IsStart
	if not IsStart: return
	
	global BroadRoleIDSet
	roleId = role.GetRoleID()
	
	if roleId in BroadRoleIDSet:
		BroadRoleIDSet.discard(roleId)
	
def SyncRoleOtherData(role, param):
	global EndTime
	if EndTime:
		role.SendObj(TurnTableStart, EndTime)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		TurnTableDict = Contain.Dict("TurnTableDict", (2038, 1, 1), AfterLoad)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TurnTable_OpenPanel", "全名转转乐打开面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TurnTable_ClosePanel", "全名转转乐关闭面板"), RequestClosePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TurnTable_Turn", "全名转转乐请求抽取"), RequestTurn)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TurnTable_OpenBox", "全名转转乐请求开启宝箱"), RequestOpenBox)
		
		#请求逻辑进程的奖池数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicTurnTablePoolValue, RequestLogicTurnTablePoolValue)
		#发送跨服奖池榜数据到逻辑进程
		cComplexServer.RegDistribute(PyMessage.Control_UpdataTurnTablePoolValueToLogic, UpdataTurnTablePoolValueToLogic)
		#起服调用
		Init.InitCallBack.RegCallbackFunction(TryUpdate)
		
		Event.RegEvent(Event.Eve_ClientLost, BeforeExit)
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	
