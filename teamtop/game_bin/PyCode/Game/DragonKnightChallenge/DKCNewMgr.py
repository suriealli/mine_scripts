#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DragonKnightChallenge.DKCNewMgr")
#===============================================================================
# 新龙骑试炼Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Fight import Fight
from Game.Role import Event, Status
from Game.DragonKnightChallenge import DKCNewConfig
from Game.Role.Data import EnumInt8, EnumObj, EnumInt1

IDX_REWARD = 1

if "_HasLoad" not in dir():
	#格式 {DKCLevel:{rewardPoolId:[idx, pos],} 
	DKCNew_RewardData_S = AutoMessage.AllotMessage("DKCNew_RewardData_S", "新龙骑试炼_同步试练奖励数据")
	
	Tra_DKCNew_Challenge = AutoLog.AutoTransaction("Tra_DKCNew_Challenge", "新龙骑试炼_挑战试练")
	Tra_DKCNew_GetReward = AutoLog.AutoTransaction("Tra_DKCNew_GetReward", "新龙骑试炼_领取试练奖励")
	Tra_DKCNew_OneKeyFree = AutoLog.AutoTransaction("Tra_DKCNew_OneKeyFree", "新龙骑试炼_一键免费收益")
	Tra_DKCNew_OneKeyAll = AutoLog.AutoTransaction("Tra_DKCNew_OneKeyAll", "新龙骑试炼_一键全部收益")


#===============================================================================
# 客户端请求 start
#===============================================================================
def OnChallenge(role, msg):
	'''
	新龙骑试炼_请求挑战试练
	@param msg: DKCLevel
	'''
	if role.GetLevel() < EnumGameConfig.DKCNew_needLevel:
		return
	
	targetLevel = msg
	maxLevel = role.GetI8(EnumInt8.DKCNewMaxLevel)
	if targetLevel > maxLevel + 1:
		return
	
	#参数异常
	targetDKCCfg = DKCNewConfig.DKCNEW_BASECONFIG_DICT.get(targetLevel, None)
	if not targetDKCCfg:
		return
	
	#是否能进入龙骑试炼战斗
	if not Status.CanInStatus(role, EnumInt1.ST_DKCFight):
		return
	
	#是否能进入战斗
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#强制进入龙骑试练状态
	Status.ForceInStatus(role, EnumInt1.ST_DKCFight)
	
	#战斗
	PVE_DKCFight(role, targetDKCCfg.fightType, targetDKCCfg.campId, (maxLevel, targetLevel, role.GetRoleName(), targetDKCCfg.levelName))

	
def OnGetReward(role, msg):
	'''
	新龙骑试炼_请求领取试练奖励
	@param msg:DKCLevel, targetPos 对应关卡 和 宝箱位置 
	'''
	if role.GetLevel() < EnumGameConfig.DKCNew_needLevel:
		return
	
	targetDKCLevel, targetPos = msg
	rewardDataDict = role.GetObj(EnumObj.DKCNewData)[IDX_REWARD]
	if targetDKCLevel not in rewardDataDict:
		#没有解锁对应关卡的奖励
		return
	
	#目标位置不存在宝箱
	if targetPos < 1 or targetPos > 4:
		return
	
	openCnt = 0
	levelRewardDict = rewardDataDict[targetDKCLevel]
	for _, rewardState in levelRewardDict.iteritems():
		_, pos = rewardState
		#对应位置宝箱已经打开
		if pos == targetPos:
			return
		#统计已经开了多少个
		if pos > 0:
			openCnt += 1
	
	#神石不足 或者  开启宝箱次数异常
	needRMB = EnumGameConfig.GetRMBByCnt(openCnt + 1)
	if needRMB < 0 or role.GetUnbindRMB() < needRMB:
		return
	
	#条件满足 组装抽奖随机器
	randomObj = DKCNewConfig.GetRandomObjByLevelAndState(targetDKCLevel, levelRewardDict)
	randomReward = randomObj.RandomOne()
	if not randomReward:
		print "GE_EXC, DKCNewMgr::OnGetReward::not randomReward role(%s)" % role.GetRoleID()
		return
	_, rewardPoolId, idx, coding, cnt = randomReward

	with Tra_DKCNew_GetReward:
		#扣除抽奖神石消耗
		if needRMB > 0:
			role.DecUnbindRMB(needRMB)
		#更新领奖数据状态
		levelRewardDict[rewardPoolId] = [idx, targetPos]
		#道具获得
		role.AddItem(coding, cnt)
		#记录日志::在关卡targetDKCLevel中 位置targetPos的宝箱 抽中了第rewardPoolId套奖励的下标为idx的奖励
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveDKCNewReward, (targetDKCLevel, rewardPoolId, idx, targetPos))
	
	#同步最新领奖数据状态
	role.SendObj(DKCNew_RewardData_S, rewardDataDict)
	#奖励提示
	role.Msg(2, 0, GlobalPrompt.DKCNew_Tips_Head + GlobalPrompt.Item_Tips % (coding, cnt))


def OnOneKeyFree(role, msg = None):
	'''
	新龙骑试炼_请求一键免费收益
	'''
	if role.GetLevel() < EnumGameConfig.DKCNew_needLevel:
		return
	
	if role.GetVIP() < EnumGameConfig.KDC_OneKeyFree_NeedVIP:
		return
	
	#统计未领取免费次数奖励的关卡
	canFreeLevelList = []
	rewardDataDict = role.GetObj(EnumObj.DKCNewData)[IDX_REWARD]
	for tDKCLevel, tRewardData in rewardDataDict.iteritems():
		canFree = True
		for _, rewardInfo in tRewardData.iteritems():
			if rewardInfo[1] != 0:
				canFree = False
				break
		if canFree:
			canFreeLevelList.append(tDKCLevel)
	
	#没有可以免费领取光卡奖励
	if len(canFreeLevelList) < 1:
		return
	
	rewardDict = {}
	rewardList_ForLog = []
	prompt = GlobalPrompt.DKCNew_Tips_OneKeyFreeHead
	with Tra_DKCNew_OneKeyFree:
		for targetDKCLevel in canFreeLevelList:
			levelRewardDict = rewardDataDict[targetDKCLevel]
			randomObj = DKCNewConfig.GetRandomObjByLevelAndState(targetDKCLevel, levelRewardDict)
			randomReward = randomObj.RandomOne()
			if not randomReward:
				print "GE_EXC, DKCNewMgr::OnOneKeyFree::not randomReward role(%s),targetDKCLevel(%s)" % (role.GetRoleID(), targetDKCLevel)
				continue
			_, rewardPoolId, idx, coding, cnt = randomReward
			#更新领奖数据状态 默认自动领取免费奖励位置为1
			levelRewardDict[rewardPoolId] = [idx, 1]
			#道具获得
			role.AddItem(coding, cnt)
			#统计获得
			if coding not in rewardDict:
				rewardDict[coding] = cnt
			else:
				rewardDict[coding] += cnt
			#统计日志数据:在关卡targetDKCLevel中 位置 1 的宝箱 抽中了第rewardPoolId套奖励的下标为idx的奖励
			logInfo = (targetDKCLevel, rewardPoolId, idx)
			rewardList_ForLog.append(logInfo)
				
		#记录日志::
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveDKCNewOneKeyFree, rewardList_ForLog)
	
	#同步最新领奖数据状态
	role.SendObj(DKCNew_RewardData_S, rewardDataDict)
	#奖励提示
	for coding, cnt in rewardDict.iteritems():
		prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	role.Msg(2, 0, prompt)
	

def OnOneKeyAll(role, msg = None):
	'''
	新龙骑试炼_请求一键全部收益
	'''
	if role.GetLevel() < EnumGameConfig.DKCNew_needLevel:
		return
	
	if role.GetVIP() < EnumGameConfig.KDC_OneKeyAll_NeedVIP:
		return
	
	#统计有奖励未领取的关卡及随机未领取位置信息 {DKCLevel:[pos1,pos2,],}
	needUnbindRMB = 0
	canRewardLevelDict = {}
	rewardedPosSet = set()
	rewardDataDict = role.GetObj(EnumObj.DKCNewData)[IDX_REWARD]
	for tDKCLevel, tRewardData in rewardDataDict.iteritems():
		rewardedPosSet.clear()
		for _, rewardInfo in tRewardData.iteritems():
			_, tPos = rewardInfo
			if tPos != 0:
				rewardedPosSet.add(tPos)
		
		unRewardPosList = list(EnumGameConfig.DKC_RewardPos_Set.difference(rewardedPosSet))
		toBeOpenCnt = len(unRewardPosList)
		if toBeOpenCnt > 0:
			canRewardLevelDict[tDKCLevel] = unRewardPosList
			needUnbindRMB += EnumGameConfig.GetTotalRMBByCnt(toBeOpenCnt)
				
	#没有可领取的奖励
	if len(canRewardLevelDict) < 1:
		return
	
	#神石不足
	if needUnbindRMB < 0 or role.GetUnbindRMB() < needUnbindRMB:
		return
	
	rewardDict = {}
	rewardDict_ForLog = {}		#格式 ｛targetDKCLevel：[(rewardPoolId, idx, targetPos),],｝
	prompt = GlobalPrompt.DKCNew_Tips_OneKeyAllHead
	with Tra_DKCNew_OneKeyAll:
		#扣除神石
		role.DecUnbindRMB(needUnbindRMB)
		#处理奖励记录
		for targetDKCLevel, targetPosList in canRewardLevelDict.iteritems():
			rewardList_ForLog = []
			for targetPos in targetPosList:
				levelRewardDict = rewardDataDict[targetDKCLevel]
				randomObj = DKCNewConfig.GetRandomObjByLevelAndState(targetDKCLevel, levelRewardDict)
				randomReward = randomObj.RandomOne()
				if not randomReward:
					print "GE_EXC, DKCNewMgr::OnOneKeyAll::not randomReward role(%s),targetDKCLevel(%s)" % (role.GetRoleID(), targetDKCLevel)
					continue
				_, rewardPoolId, idx, coding, cnt = randomReward
				#更新领奖数据状态 默认自动领取免费奖励位置为1
				levelRewardDict[rewardPoolId] = [idx, targetPos]
				#道具获得
				role.AddItem(coding, cnt)
				#统计奖励获得
				if coding not in rewardDict:
					rewardDict[coding] = cnt
				else:
					rewardDict[coding] += cnt
				#记录日志::在关卡targetDKCLevel中 位置targetPos的宝箱 抽中了第rewardPoolId套奖励的下标为idx的奖励
				logInfo = (rewardPoolId, idx, targetPos,)
				rewardList_ForLog.append(logInfo)
			rewardDict_ForLog[targetDKCLevel] = rewardList_ForLog
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveDKCNewOneKeyAll, rewardDict_ForLog)
	
	#同步最新领奖数据状态
	role.SendObj(DKCNew_RewardData_S, rewardDataDict)
	#奖励提示
	for coding, cnt in rewardDict.iteritems():
		prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	role.Msg(2, 0, prompt)


#===============================================================================
# 战斗start
#===============================================================================
def PVE_DKCFight(role, fightType, mcid, regParam):
	'''
	龙骑试炼战斗
	'''
	fight = Fight.Fight(fightType)
	# 可收到设置客户端断线重连是否还原战斗,默认不还原
	fight.restore = True
	#创建两个阵营
	left_camp, right_camp = fight.create_camp()
	#在阵营中创建战斗单位
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(mcid)
	#设置回调函数
	fight.after_fight_fun = AfterFight		#战斗结束
	fight.after_play_fun = AfterPlay		#客户端播放完毕
	fight.after_fight_param = regParam		#注册参数
	fight.start()


def AfterFight(fightObj):
	'''
	龙骑试炼战斗结束  
	'''
	#获取战斗role
	if not fightObj.left_camp.roles:
		return
	left_camp_roles_list = list(fightObj.left_camp.roles)
	role = left_camp_roles_list[0]
	
	#退出龙骑试练状态
	Status.Outstatus(role, EnumInt1.ST_DKCFight)
	maxLevel, targetLevel, roleName, levelName = fightObj.after_fight_param
	#突破新的关卡
	if fightObj.result == 1 and targetLevel > maxLevel:
		with Tra_DKCNew_Challenge:
			#记录历史最高通关
			role.SetI8(EnumInt8.DKCNewMaxLevel, targetLevel)
			#初始最新通关关卡奖励状态
			rewardDataDict = role.GetObj(EnumObj.DKCNewData)[IDX_REWARD]
			rewardDataDict[targetLevel] = DKCNewConfig.GetRandomDictByLevel(targetLevel)
		#同步客户端
		role.SendObj(DKCNew_RewardData_S, rewardDataDict)
		#首次通关广播
		cRoleMgr.Msg(11, 0, GlobalPrompt.DKCNew_Msg_UnlockLevel % (roleName, levelName))			
	elif fightObj.result == -1:
		pass
	else:
		pass
		
		
def AfterPlay(fightObj):
	'''
	龙骑试炼播放战斗结束  
	'''
	pass


#===============================================================================
# 事件 start
#===============================================================================
def OnInitRole(role, param = None):
	'''
	初始化角色相关key
	'''
	roleDKCNewData = role.GetObj(EnumObj.DKCNewData)
	if IDX_REWARD not in roleDKCNewData:
		roleDKCNewData[IDX_REWARD] = {}
	
	
def OnSyncOtherData(role, param = None):
	'''
	同步角色新龙骑试炼数据给前端做表现
	'''
	role.SendObj(DKCNew_RewardData_S, role.GetObj(EnumObj.DKCNewData)[IDX_REWARD])


def OnDayClear(role, param = None):
	'''
	每日清理新龙骑试炼数据
	直接根据玩家历史最高通关记录 初始化宝箱状态
	'''
	rewardDataDict = {}
	maxLevel = role.GetI8(EnumInt8.DKCNewMaxLevel)
	for i in xrange(maxLevel):
		rewardDataDict[i+1] = DKCNewConfig.GetRandomDictByLevel(i+1)
	
	role.GetObj(EnumObj.DKCNewData)[IDX_REWARD] = rewardDataDict
	
	role.SendObj(DKCNew_RewardData_S, rewardDataDict)
	
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitRole)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DKCNew_OnChallenge", "新龙骑试炼_请求挑战试练"), OnChallenge)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DKCNew_OnGetReward", "新龙骑试炼_请求领取试练奖励"), OnGetReward)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DKCNew_OnOneKeyFree", "新龙骑试炼_请求一键免费收益"), OnOneKeyFree)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DKCNew_OnOneKeyAll", "新龙骑试炼_请求一键全部收益"), OnOneKeyAll)