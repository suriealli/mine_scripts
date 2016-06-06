#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionGodTree")
#===============================================================================
# 国庆神树探秘抽奖控制	 @author: GaoShuai
#===============================================================================
import cRoleMgr
import Environment
from Game.Role import Event
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Activity.PassionAct import PassionGodTreeConfig
from Common.Other import GlobalPrompt

if "_HasLoad" not in dir():
	IsStart = False
	rewardList = []
	GoddTree_BroadRoleID_Set = set()
	#日志
	PassionGodTree_Log = AutoLog.AutoTransaction("PassionGodTree_Log", "神树探秘")
	#消息
	GodTree_Record = AutoMessage.AllotMessage("GodTreeRecord", "神树探秘全服数据记录")
	
def StartCircularActive(param1, param2):
	if param2 != CircularDefine.CA_PassionGodTree:
		return
	global IsStart
	if IsStart:
		print 'GE_EXC, PassionGodTree is already start'
	IsStart = True

def EndCircularActive(param1, param2):
	if param2 != CircularDefine.CA_PassionGodTree:
		return
	global IsStart, rewardList, GoddTree_BroadRoleID_Set
	if not IsStart:
		print 'GE_EXC, PassionGodTree is already end'
	IsStart = False
	rewardList = []
	GoddTree_BroadRoleID_Set.clear()
def RequestOpenPanel(role, param=None):
	'''
	国庆神树探秘打开面板
	@param role:
	@param msg:
	'''
	global IsStart, rewardList, GoddTree_BroadRoleID_Set
	if not IsStart:
		return 
	if len(rewardList) > 50:
		rewardList = rewardList[-50:]
	role.SendObj(GodTree_Record, rewardList)
	GoddTree_BroadRoleID_Set.add(role.GetRoleID())
def RequestClosePanel(role, param=None):
	'''
	国庆神树探秘关闭面板
	@param role:
	@param msg:
	'''
	global IsStart, GoddTree_BroadRoleID_Set
	if not IsStart:
		return 
	GoddTree_BroadRoleID_Set.discard(role.GetRoleID())
def RequestGodTreeExplor(role, param):
	'''
	国庆神树探秘请求探秘
	@param role:
	@param msg:探秘次数(1,10,50)
	'''
	global rewardList, IsStart, GoddTree_BroadRoleID_Set
	if not IsStart:
		return 
	if param not in (1, 10, 50):
		return
	level = role.GetLevel()
	levelRangeId = 0
	for key, item in PassionGodTreeConfig.GodTree_Dict.items():
		if item.levelRange[0] <= level <= item.levelRange[1] :
			levelRangeId = key
			break
	
	GodTreeObj = PassionGodTreeConfig.GodTree_Dict.get(levelRangeId, None)
	#这里获取不到对象，说明角色等级不在配置表内
	if not GodTreeObj:
		return
	#统计探秘道具和神石需求
	haveItemCnt = role.ItemCnt(GodTreeObj.needCoding)
	needItemCnt = min(haveItemCnt, param)
	needRMB = max(0, (param - haveItemCnt) * GodTreeObj.needRMB_Q)
	#判断实际是否足够
	if role.GetUnbindRMB_Q() < needRMB and haveItemCnt < param:
		return
	
	Random_obj = PassionGodTreeConfig.random_Dict.get(levelRangeId)
	if not Random_obj:
		print "GE_EXC, can't get Random_obj in PassionGodTreeConfig.random_Dict roleLevel(%s)" % role.GetLevel()
		
	rewardDict = {}
	specialReward = {}
	#循环随机出奖励
	for _ in range(param):
		(coding, cnt), special = Random_obj.RandomOne()
		#极品道具
		if special:
			specialReward[coding] = specialReward.get(coding, 0) + cnt
			rewardList.append((role.GetRoleName(), coding, cnt))
		else:
			#普通道具
			rewardDict[coding] = rewardDict.get(coding, 0) + cnt
			
	rewardTip = GlobalPrompt.Reward_Tips
	with PassionGodTree_Log:
		if needItemCnt > 0:
			role.DelItem(GodTreeObj.needCoding, needItemCnt)
		role.DecUnbindRMB_Q(needRMB)
		#极品道具
		for coding, cnt in specialReward.items():
			role.AddItem(coding, cnt)
		#普通道具
		for coding, cnt in rewardDict.items():
			role.AddItem(coding, cnt)
			rewardTip += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#提示	
	for coding, cnt in specialReward.items():
		oldRoleSet = set()
		for roleId in GoddTree_BroadRoleID_Set:
			roleTmp = cRoleMgr.FindRoleByRoleID(roleId)
			if not roleTmp or roleTmp.IsLost() or roleTmp.IsKick():
				oldRoleSet.add(roleId)
				continue
			roleTmp.SendObj(GodTree_Record, rewardList)
		GoddTree_BroadRoleID_Set -= oldRoleSet
		cRoleMgr.Msg(1, 0, GlobalPrompt.PassionGodTree % (role.GetRoleName(), coding, cnt))
	if rewardDict:
		role.Msg(2, 0, rewardTip)
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GodTreeOpenPanel", "神树探秘打开面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GodTreeClosePanel", "神树探秘关闭面板"), RequestClosePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GodTreeExplor", "神树探秘请求探秘"), RequestGodTreeExplor)

