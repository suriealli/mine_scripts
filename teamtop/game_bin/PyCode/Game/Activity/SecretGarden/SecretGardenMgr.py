#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SecretGarden.SecretGardenMgr")
#===============================================================================
# 秘密花园 Mgr
#===============================================================================
import cRoleMgr
import cNetMessage
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Mail import Mail
from Game.Role import Event, Call
from Game.Persistence import Contain
from Game.SysData import WorldDataNotSync, WorldData
from Game.Activity.SecretGarden import SecretGardenConfig

VERSION = "version"

RT_LOTTERY = 1
RT_LUCKY = 2

IDX_GROWSTATE = 1
IDX_LEFTSTATE = 2
IDX_UNLOCKREWARD = 3
IDX_LOTTERYCNT = 4

if "_HasLoad" not in dir():
	#活动开关
	IS_START = False
	#结束时间戳
	END_TIME = 0
	#配置触发标志
	CONFIG_TRIGGER = False	
	#活动控制配置
	SecretGarden_Active_Control = None
	#珍惜记录 格式  [(recodeType, roleName, coding, cnt ),] 其中recodeType=1表示抽奖获得珍惜道具 recodeType=2表示领取极品成熟果实
	SecretGarden_PreciousRecord_List = []
	
	#格式 {1:{rewardIndex:grownCnt,},2:{rewardIndex:leftCnt,}, 3:set(rewardId,)}
	#1表示 未成熟的幸运果实当前成熟度状态 即 果实 rewardIndex 的当前成熟度为 grownCnt
	#2表示已成熟的幸运果实剩余可领取数量 即 果实 rewardIndex 还可以 领取 leftCnt
	#3表示已经领取的累计解锁奖励 即rewardId已经领取了 
	#4表示玩家抽奖次数
	#key 1,2,3,4可选,不一定都有
	SecretGarden_ActiveDataAll_S = AutoMessage.AllotMessage("SecretGarden_ActiveDataAll_S", "秘密花园_玩家所有活动数据同步")
	#格式 （IS_START, END_TIME）
	SecretGarden_ActiveState_S = AutoMessage.AllotMessage("SecretGarden_ActiveState_S", "秘密花园_同步活动状态")
	#抽奖回调 格式 rewardId 表示抽中奖励的rewardId
	SecretGarden_SingleLotteryResult_SB = AutoMessage.AllotMessage("SecretGarden_SingleLotteryResult_SB", "秘密花园_单次抽奖回调") 
	#格式  [(recodeType, roleName, coding, cnt ),] 其中recodeType=1表示抽奖获得珍惜道具 recodeType=2表示领取极品成熟果实
	SecretGarden_PreciousRecord_S = AutoMessage.AllotMessage("SecretGarden_PreciousRecord_S", "秘密花园_珍贵记录同步")
	
	Tra_SecretGarden_SingleLottery = AutoLog.AutoTransaction("Tra_SecretGarden_SingleLottery", "秘密花园_单次抽奖")
	Tra_SecretGarden_MultieLottery = AutoLog.AutoTransaction("Tra_SecretGarden_MultieLottery", "秘密花园_批量抽奖")
	Tra_SecretGarden_GetUnlockReward = AutoLog.AutoTransaction("Tra_SecretGarden_GetUnlockReward", "秘密花园_领取累计奖励")
	Tra_SecretGarden_AutoReward = AutoLog.AutoTransaction("Tra_SecretGarden_AutoReward", "秘密花园_自动发放奖励")
	Tra_SecretGarden_GetLuckyReward = AutoLog.AutoTransaction("Tra_SecretGarden_GetLuckyReward", "秘密花园_领取成熟果实奖励")
	
#===============================================================================
# 活动控制
#===============================================================================
def StartSecretGarden(callArgv, regparam):
	'''
	秘密花园_开启活动
	'''
	global END_TIME
	global SecretGarden_Active_Control
	SecretGarden_Active_Control, END_TIME = regparam
	
	global CONFIG_TRIGGER
	CONFIG_TRIGGER = True
	
	TryRealStart()


def TryRealStart():
	'''
	1.配置触发到了(两个世界数据载回了才触发配置逻辑)
	2.持久化数据到了 
	'''
	if not CONFIG_TRIGGER:
#		print "GE_EXC,SecretGarden::TryRealStart,not CONFIG_TRIGGER"
		return 
	
	if not SecretGarden_Dict.returnDB:
#		print "GE_EXC,SecretGarden::TryRealStart,not SecretGarden_Dict.returnDB"
		return 
	
	global IS_START
	if IS_START:
#		print "GE_EXC, SecretGarden::repeat start active"
		return
	
	#版本号合理性判断
	oldVersion = WorldDataNotSync.GetSecretGardenVersion()
	nowVersion = SecretGarden_Active_Control.activeID
	if nowVersion < oldVersion:
		print "GE_EXC,SecretGarden::TryRealStart: nowVersion(%s) < oldVersion(%s)" % (nowVersion, oldVersion)
		return 
	
	#新的版本号 清理数据 (WD的本服累计次数+持久化数据+版本号) 
	if nowVersion > oldVersion:
		WorldDataNotSync.SetSecretGardenVersion(nowVersion)
		WorldData.SetSecretGardenServerCnt(0)
		SecretGarden_Dict.clear()
	
	#真正开启活动
	IS_START = True
	
	#同步活动开启
	cNetMessage.PackPyMsg(SecretGarden_ActiveState_S, (IS_START, END_TIME))
	cRoleMgr.BroadMsg()
	
	#同步在线玩家相关活动数据
	for trole in cRoleMgr.GetAllRole():
		trole.SendObj(SecretGarden_ActiveDataAll_S, SecretGarden_Dict.get(trole.GetRoleID(), {}))


def EndSecretGarden(callArgv, regparam):
	'''
	秘密花园_结束活动
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,EndSecretGarden Error: end active but not start"
		return 
	
	IS_START = False
	
	cNetMessage.PackPyMsg(SecretGarden_ActiveState_S, (IS_START, END_TIME))
	cRoleMgr.BroadMsg()
	
	with Tra_SecretGarden_AutoReward:
		AuToRewardAll()


#===============================================================================
# 客户端请求
#===============================================================================
def OnOpenPanel(role, msg=None):
	'''
	秘密花园_请求打开面板
	'''
	if not IS_START:
		return 
	
	if role.GetLevel() < EnumGameConfig.SecretGarden_NeedLevel:
		return 
	
	role.SendObj(SecretGarden_PreciousRecord_S, SecretGarden_PreciousRecord_List)


def OnSingleLottery(role, msg=None):
	'''
	秘密花园_请求单次抽奖
	'''
	if not IS_START:
		return 
	
	roleLevel = role.GetLevel() 
	if roleLevel < EnumGameConfig.SecretGarden_NeedLevel:
		return 
	
	if role.GetUnbindRMB_Q() < EnumGameConfig.SecretGarden_LotteryRMB_1:
		return 
	
	lotteryRandomObj = SecretGardenConfig.GetLotteryRandomByLevel(roleLevel)
	if not lotteryRandomObj:
		print "GE_EXC,SecretGarden::OnSingleLottery: can not get lottery random obj by roleLevel(%s)" % roleLevel
		return 
	
	randomRewardInfo = lotteryRandomObj.RandomOne()
	if not randomRewardInfo:
		print "GE_EXC,SecretGarden::OnSingleLottery: can not random reward info"
		return 
	
	rewardId, coding, cnt, isPrecious = randomRewardInfo
	luckyRewardIndex = SecretGardenConfig.SecretGarden_LuckyReward_RandomObj.RandomOne() 
	if not luckyRewardIndex:
		print "GE_EXC, SecretGarden::OnSingleLottery: can not random lucky rewardIndex "
		return 
	
	with Tra_SecretGarden_SingleLottery:
		#扣钱
		role.DecUnbindRMB_Q(EnumGameConfig.SecretGarden_LotteryRMB_1)
		#回调客户端
		role.SendObjAndBack(SecretGarden_SingleLotteryResult_SB, rewardId, 8, SingleLotteryBack, (role.GetRoleID(), role.GetRoleName(), rewardId, coding, cnt, isPrecious, luckyRewardIndex))
		#日志
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveSecretGardenSingleLottery, (rewardId, luckyRewardIndex))
		

def SingleLotteryBack(role, callArgvs=None, regParams=None):
	'''
	单次抽奖回调
	'''
	roleId, roleName, _, coding, cnt, isPrecious, luckyRewardIndex = regParams
	#珍贵奖励记录处理
	if isPrecious:
		global SecretGarden_PreciousRecord_List
		preciousInfo = (RT_LOTTERY, roleName, coding, cnt)
		SecretGarden_PreciousRecord_List.append(preciousInfo)
		SecretGarden_PreciousRecord_List = SecretGarden_PreciousRecord_List[-50:]
		
		#广播
		cRoleMgr.Msg(11, 0, GlobalPrompt.SecretGarden_Msg_Precious % (roleName, coding, cnt))
		
		#同步最新珍贵奖励记录给缓存的role
		if not role.IsKick() and not role.IsLost():
			role.SendObj(SecretGarden_PreciousRecord_S, SecretGarden_PreciousRecord_List)
	
	#处理果实成熟度逻辑
	GrowingAfterLottery(roleId, {luckyRewardIndex:1}, lotteryCnt=1)
		
	Call.LocalDBCall(roleId, RealAward, (coding, cnt))
		

def RealAward(role, param):
	'''
	抽奖实际获得处理
	'''
	coding, cnt = param
	with Tra_SecretGarden_SingleLottery:
		#物品获得
		role.AddItem(coding, cnt)
		#获得提示
		role.Msg(2, 0, GlobalPrompt.SecretGarden_Tips_Head + GlobalPrompt.Item_Tips % (coding, cnt))


def OnMultiLottery(role, msg):
	'''
	秘密花园_请求批量抽奖
	@param msg: lotteryCnt
	'''
	if not IS_START:
		return 
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.SecretGarden_NeedLevel:
		return 

	lotteryCnt = msg
	if lotteryCnt < 1:
		return 
	
	needRMB = EnumGameConfig.SecretGarden_LotteryRMB_1 * lotteryCnt
	if role.GetUnbindRMB_Q() < needRMB:
		return 
	
	lotteryRandomObj = SecretGardenConfig.GetLotteryRandomByLevel(roleLevel)
	if not lotteryRandomObj:
		print "GE_EXC,SecretGarden::OnSingleLottery: can not get lottery random obj by roleLevel(%s)" % roleLevel
		return 
	
	luckyRewardDict = {}
	lotteryRewardDict = {}
	preciouseRewardList = []
	roleName = role.GetRoleName()
	for _ in xrange(lotteryCnt):
		randomRewardInfo = lotteryRandomObj.RandomOne()
		if not randomRewardInfo:
			print "GE_EXC,SecretGarden::OnMultiLottery: can not random reward info"
			continue 
		
		_, coding, cnt, isPrecious = randomRewardInfo
		#统计抽奖奖励字典
		if coding not in lotteryRewardDict:
			lotteryRewardDict[coding] = cnt
		else:
			lotteryRewardDict[coding] += cnt 
		
		#统计珍稀奖励字典
		if isPrecious:
			preciouseRewardList.append((RT_LOTTERY, roleName, coding, cnt))
		
		luckyRewardIndex = SecretGardenConfig.SecretGarden_LuckyReward_RandomObj.RandomOne() 
		if not luckyRewardIndex:
			print "GE_EXC, SecretGarden::OnMultiLottery: can not random lucky rewardIndex "
			continue 
		
		#统计果实成熟度字典
		if luckyRewardIndex not in luckyRewardDict:
			luckyRewardDict[luckyRewardIndex] = 1
		else:
			luckyRewardDict[luckyRewardIndex] += 1
		
	prompt = GlobalPrompt.SecretGarden_Tips_Head
	with Tra_SecretGarden_MultieLottery:
		#扣钱
		role.DecUnbindRMB_Q(needRMB)
		#物品获得
		for coding, cnt in lotteryRewardDict.iteritems():
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
		#抽奖获得成熟度处理
		GrowingAfterLottery(role.GetRoleID(), luckyRewardDict, lotteryCnt=lotteryCnt)
		#珍贵奖励处理
		global SecretGarden_PreciousRecord_List
		SecretGarden_PreciousRecord_List.extend(preciouseRewardList)
		SecretGarden_PreciousRecord_List = SecretGarden_PreciousRecord_List[-50:]
		#提示
		role.Msg(2, 0, prompt)
		#广播
		for preciousInfo in preciouseRewardList:
			cRoleMgr.Msg(11, 0, GlobalPrompt.SecretGarden_Msg_Precious % (preciousInfo[1], preciousInfo[2], preciousInfo[3]))
		#同步最新珍贵记录
		role.SendObj(SecretGarden_PreciousRecord_S, SecretGarden_PreciousRecord_List)


def OnGetUnlockReward(role, msg):
	'''
	秘密花园_请求领取累计解锁奖励
	@param msg: targetRewardId
	'''
	if not IS_START:
		return 
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.SecretGarden_NeedLevel:
		return 
	
	targetRewardId = msg
	rewardCfg = SecretGardenConfig.SecretGarden_UnlockReward_Dict.get(targetRewardId, None)
	if not rewardCfg:
		return 
	
	
	roleSGDict = SecretGarden_Dict.setdefault(role.GetRoleID(), {})
	lotteryCnt = roleSGDict.get(IDX_LOTTERYCNT, 0)
	if lotteryCnt < rewardCfg.needRoleCnt:
		return 
	
	if WorldData.GetSecretGardenServerCnt() < rewardCfg.needServerCnt:
		return 
	
	unlockRewardSet = roleSGDict.setdefault(IDX_UNLOCKREWARD, set())
	if targetRewardId in unlockRewardSet:
		return 
	
	coding, cnt = rewardCfg.rewardItem
	with Tra_SecretGarden_GetUnlockReward:
		unlockRewardSet.add(targetRewardId)
		role.AddItem(coding, cnt)
		role.Msg(2, 0, GlobalPrompt.SecretGarden_Tips_Head + GlobalPrompt.Item_Tips % (coding, cnt))
	
	SecretGarden_Dict[role.GetRoleID()] = roleSGDict
	role.SendObj(SecretGarden_ActiveDataAll_S, roleSGDict)


def OnGetGrowUpReward(role, msg=None):
	'''
	秘密花园_请求领取成熟果实奖励
	@param msg: targetRewardId
	'''
	if not IS_START:
		return 
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.SecretGarden_NeedLevel:
		return 
	
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	prompt = GlobalPrompt.SecretGarden_Tips_Head
	roleSGDict = SecretGarden_Dict.setdefault(roleId, {})
	leftRewardDict = roleSGDict.get(IDX_LEFTSTATE, {})
	if len(leftRewardDict):
		global SecretGarden_PreciousRecord_List
		with Tra_SecretGarden_GetLuckyReward:
			rewardDict = {}
			preciousDict = {}
			for luckyRewardId, luckyCnt in leftRewardDict.iteritems():
				rewardCfg = SecretGardenConfig.SecretGarden_LuckyReward_Dict.get(luckyRewardId, None)
				if not rewardCfg:
					continue
				coding, cnt = rewardCfg.rewardItem[0], rewardCfg.rewardItem[1] * luckyCnt
				rewardDict[coding] = cnt
				if rewardCfg.isPrecious:
					preciousDict[coding] = cnt
					SecretGarden_PreciousRecord_List.append((RT_LUCKY, roleName, coding, cnt))
			#清除剩余果实
			leftRewardDict.clear()
			#回存
			SecretGarden_Dict[roleId] = roleSGDict
			#获得道具奖励
			for coding, cnt in rewardDict.iteritems():
				role.AddItem(coding, cnt)
				prompt += GlobalPrompt.Item_Tips % (coding, cnt)
			
			for coding, cnt in preciousDict.iteritems():
				cRoleMgr.Msg(11, 0, GlobalPrompt.SecretGarden_Msg_Lucky % (roleName, coding, cnt))
		SecretGarden_PreciousRecord_List = SecretGarden_PreciousRecord_List[-50:]
	
	#同步最新活动数据
	role.SendObj(SecretGarden_ActiveDataAll_S, roleSGDict)
	#同步最新珍贵记录
	role.SendObj(SecretGarden_PreciousRecord_S, SecretGarden_PreciousRecord_List)
		
#===============================================================================
# 辅助
#===============================================================================
def AuToRewardAll():
	'''
	活动结束 尝试自动发放奖励
	'''
	global SecretGarden_Dict
	serverCnt = WorldData.GetSecretGardenServerCnt()
	for roleId, roleSGDict in SecretGarden_Dict.iteritems():
		#处理成熟果实奖励
		luckyRewardList = []
		for luckyIndex, luckyCnt in roleSGDict.get(IDX_LEFTSTATE, {}).iteritems():
			luckyCfg = SecretGardenConfig.SecretGarden_LuckyReward_Dict.get(luckyIndex, None)
			if not luckyCfg:
				continue
			luckyRewardList.append((luckyCfg.rewardItem[0], luckyCfg.rewardItem[1] * luckyCnt))
		
		if len(luckyRewardList):
			Mail.SendMail(roleId,
						GlobalPrompt.SecretGarden_Mail_Title_1,
						GlobalPrompt.SecretGarden_Mail_Sender_1,
						GlobalPrompt.SecretGarden_Mail_Content_1,
						items=luckyRewardList)
		
		#删除剩余可领取果实
		if IDX_LEFTSTATE in roleSGDict:
			del roleSGDict[IDX_LEFTSTATE]
		#处理累计解锁奖励
		unlockRewardList = []
		roleLotteryCnt = roleSGDict.get(IDX_LOTTERYCNT, 0)
		unlockRewardSet = roleSGDict.setdefault(IDX_UNLOCKREWARD, set())
		for unlockRewardIndex, unlockRewardCfg in SecretGardenConfig.SecretGarden_UnlockReward_Dict.iteritems():
			if unlockRewardIndex not in unlockRewardSet:
				if serverCnt >= unlockRewardCfg.needServerCnt and roleLotteryCnt >= unlockRewardCfg.needRoleCnt:
					unlockRewardSet.add(unlockRewardIndex)
					unlockRewardList.append((unlockRewardCfg.rewardItem[0], unlockRewardCfg.rewardItem[1]))
		
		if len(unlockRewardList):
			Mail.SendMail(roleId,
						GlobalPrompt.SecretGarden_Mail_Title_2,
						GlobalPrompt.SecretGarden_Mail_Sender_2,
						GlobalPrompt.SecretGarden_Mail_Content_2,
						items=unlockRewardList)
		
		SecretGarden_Dict[roleId] = roleSGDict


def GrowingAfterLottery(roleId, growDict={}, lotteryCnt=1):
	'''
	抽奖后成长度处理
	@param growList: {luckyIndex:cnt,}
	'''
	if not IS_START:
		return 
	
	global SecretGarden_Dict
	roleSGDict = SecretGarden_Dict.get(roleId, {})
	if IDX_GROWSTATE not in roleSGDict:
		roleSGDict[IDX_GROWSTATE] = {}
	
	GrowUpDict = {}
	growStateDict = roleSGDict.setdefault(IDX_GROWSTATE, {})
	leftStateDict = roleSGDict.setdefault(IDX_LEFTSTATE, {})
	for luckyIndex, luckyCnt in growDict.iteritems():
		if luckyIndex not in growStateDict:
			growStateDict[luckyIndex] = luckyCnt
		else:
			growStateDict[luckyIndex] += luckyCnt
		
		luckyCfg = SecretGardenConfig.SecretGarden_LuckyReward_Dict.get(luckyIndex, None)
		if not luckyCfg:
			print "GE_EXC,GrowingAfterLottery: can not get lucky cfg by luckyIndex(%s)" % luckyIndex
			continue
		
		grownCnt = luckyCfg.grownCnt
		if growStateDict[luckyIndex] >= grownCnt:
			tempCnt = growStateDict[luckyIndex] / grownCnt
			growStateDict[luckyIndex] %= grownCnt
			
			if luckyIndex not in leftStateDict:
				leftStateDict[luckyIndex] = tempCnt
			else:
				leftStateDict[luckyIndex] += tempCnt
			
			#统计此次成熟的果实
			GrowUpDict[luckyIndex] = tempCnt
	
	#增加玩家抽奖次数(同EnumInt16.SecretGarden_LotteryCnt 冗余为了自动发放未领取的奖励)
	if IDX_LOTTERYCNT not in roleSGDict:
		roleSGDict[IDX_LOTTERYCNT] = lotteryCnt
	else:
		roleSGDict[IDX_LOTTERYCNT] += lotteryCnt
	#增加本服累计次数
	WorldData.IncSecretGardenServerCnt(lotteryCnt)
	#保存最新
	SecretGarden_Dict[roleId] = roleSGDict	
	#同步最新果实状态
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if role and (not role.IsKick() and not role.IsLost()):
		role.SendObj(SecretGarden_ActiveDataAll_S, roleSGDict)
	
	return GrowUpDict
	

#===============================================================================
# 事件
#===============================================================================
def AfterLoad():
	'''
	活动持久化数据载回 尝试触发活动开启
	'''
	TryRealStart()


def OnSyncRoleOtherData(role, param=None):
	if not IS_START:
		return 

	role.SendObj(SecretGarden_ActiveState_S, (IS_START, END_TIME))
	role.SendObj(SecretGarden_ActiveDataAll_S, SecretGarden_Dict.get(role.GetRoleID(), {}))


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		SecretGarden_Dict = Contain.Dict("SecretGarden_Dict", (2038, 1, 1), AfterLoad)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SecretGarden_OnOpenPanel", "秘密花园_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SecretGarden_OnSingleLottery", "秘密花园_请求单次抽奖"), OnSingleLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SecretGarden_OnMultiLottery", "秘密花园_请求批量抽奖"), OnMultiLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SecretGarden_OnGetUnlockReward", "秘密花园_请求领取累计解锁奖励"), OnGetUnlockReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SecretGarden_OnGetGrowUpReward", "秘密花园_请求领取成熟果实奖励"), OnGetGrowUpReward)
