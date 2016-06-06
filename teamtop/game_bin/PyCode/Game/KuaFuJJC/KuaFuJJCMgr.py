#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.KuaFuJJC.KuaFuJJCMgr")
#===============================================================================
# 跨服竞技场管理
#===============================================================================
import cComplexServer
import cProcess
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumAward, GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Game.Activity.Award import AwardMgr
from Game.GlobalData import ZoneName
from Game.KuaFuJJC import KuaFuJJCConfig, KuaFuJJCCross
from Game.Persistence import Contain
from Game.Role import Event, Call
from Game.Role.Data import EnumObj, EnumInt16, EnumInt32
from Game.Role.Mail import Mail
from Game.SysData import WorldData
from Game.Union import UnionMgr
from World import Define

if "_HasLoad" not in dir():
	UNION_TODAY_SOCRE = {}		#缓存今日公会积分
	PALACE_DATA = []			#缓存龙骑殿堂数据
	FINALS_GUESS_DATA = {}		#缓存决赛竞猜数据
	
	#消息
	KuaFu_JJC_Show_Union_Score_Panel = AutoMessage.AllotMessage("KuaFu_JJC_Show_Union_Score_Panel", "通知客户端显示跨服个人竞技场公会积分面板")
	KuaFu_JJC_Show_Palace_Panel = AutoMessage.AllotMessage("KuaFu_JJC_Show_Palace_Panel", "通知客户端显示跨服个人竞技场龙骑殿堂面板")
	KuaFu_JJC_Show_Finals_Guess_Panel = AutoMessage.AllotMessage("KuaFu_JJC_Show_Finals_Guess_Panel", "通知客户端显示跨服个人竞技场决赛竞猜面板")
	
	#日志
	TraKuaFuJJCBuyKuaFuMoney = AutoLog.AutoTransaction("TraKuaFuJJCBuyKuaFuMoney", "跨服个人竞技场购买跨服币")
	TraKuaFuJJCUnionScoreReward = AutoLog.AutoTransaction("TraKuaFuJJCUnionScoreReward", "跨服个人竞技场公会积分奖励")
	TraKuaFuJJCVersionClear = AutoLog.AutoTransaction("TraKuaFuJJCVersionClear", "跨服个人竞技场版本清理")
	TraKFJJCElectionMail = AutoLog.AutoTransaction("TraKFJJCElectionMail", "跨服个人竞技场海选邮件")
	TraKFJJCFinalsGuess = AutoLog.AutoTransaction("TraKFJJCFinalsGuess", "跨服个人竞技场决赛竞猜")

def KuaFuJJCFinalsGuessDictAfterLoad():
	pass

def AllotKuaFuJJCZone(kuaFuJJCDataDict):
	if Environment.EnvIsRU() or Environment.EnvIsTK() or Environment.EnvIsPL():
		return
	
	if KuaFuJJCConfig.IS_START is False:
		return
	
	if KuaFuJJCConfig.KUAFU_JJC_DAY >= 1 and KuaFuJJCConfig.KUAFU_JJC_DAY <= 6:
		if KuaFuJJCConfig.KUAFU_JJC_DAY == 1:
			#活动第1天计算区域ID
			CalcZoneID()
		
		zoneId = WorldData.GetKuaFuJJCZoneId()
		if not zoneId:
			#开服天数不足
			return
		
		#请求控制进程转发(区域ID，资格玩家数据)
		Call.ServerCall(Define.GetDefaultCrossID(), "Game.KuaFuJJC.KuaFuJJCCross", "LogicToCrossJJCDataCall", (zoneId, kuaFuJJCDataDict))
	
		#日志
		with TraKFJJCElectionMail:
			#海选资格邮件
			for roleId in kuaFuJJCDataDict.iterkeys():
				Mail.SendMail(roleId, GlobalPrompt.KUAFU_JJC_ELECTION_TITLE, GlobalPrompt.KUAFU_JJC_ELECTION_SENDER, GlobalPrompt.KUAFU_JJC_ELECTION_MAIL)
		
def CalcZoneID():
	kaiFuDays = WorldData.GetWorldKaiFuDay()
	zoneId = 0
	
	for config in KuaFuJJCConfig.KUAFU_JJC_ZONE.itervalues():
		start, end = config.kaiFuDaysInterval
		if kaiFuDays >= start and kaiFuDays <= end:
			zoneId = config.zoneId
			break
	
	WorldData.SetKuaFuJJCZoneId(zoneId)
	
def BuyKuaFuMoney(role, rmb):
	if role.GetUnbindRMB() < rmb:
		return
	role.DecUnbindRMB(rmb)
	
	role.IncKuaFuMoney(rmb)
	
def ElectionUnionReward(rank, unionId):
	btData = UnionMgr.BT.GetData()
	#是否是本服的公会
	if unionId not in btData:
		return
	
	rewardConfig = KuaFuJJCConfig.KUAFU_JJC_UNION_RANK_REWARD.get(rank)
	if not rewardConfig:
		return
	
	unionObj = UnionMgr.GetUnionObjByID(unionId)
	if not unionObj:
		return
	
	#奖励
	for memberId in unionObj.members.iterkeys():
		AwardMgr.SetAward(memberId, EnumAward.KuaFuJJCUnionRankAward, itemList = rewardConfig.rewardItem, clientDescParam = (rank, ))

def RefreshUnionTodayScore(unionScoreDict):
	btData = UnionMgr.BT.GetData()
	
	global UNION_TODAY_SOCRE
	for unionId, score in unionScoreDict.iteritems():
		#是否是本服的公会
		if unionId not in btData:
			continue
		UNION_TODAY_SOCRE[unionId] = score
		
def GetUnionScoreReward(role, rewardId):
	unionId = role.GetUnionID()
	if not unionId:
		return
	
	rewardConfig = KuaFuJJCConfig.KUAFU_JJC_UNION_SCORE_REWARD.get(rewardId)
	if not rewardConfig:
		return
	
	#是否已经领取
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	rewardList = jjcDataDict[KuaFuJJCConfig.UNION_SCORE_REWARD_OBJ_IDX]
	if rewardId in rewardList:
		return
	
	#历史贡献条件
	if role.GetHistoryContribution() < 1000:
		return
		
	#score
	score = UNION_TODAY_SOCRE.get(unionId, 0)
	if score < rewardConfig.score:
		return
	
	#记录
	rewardList.append(rewardId)
	
	#奖励
	tips = GlobalPrompt.Reward_Tips
	if rewardConfig.rewardMoney:
		role.IncMoney(rewardConfig.rewardMoney)
		tips += GlobalPrompt.Money_Tips % rewardConfig.rewardMoney
	for item in rewardConfig.rewardItem:
		role.AddItem(*item)
		tips += GlobalPrompt.Item_Tips % item
		
	#提示
	role.Msg(2, 0, tips)
		
	ShowUnionScorePanel(role)
	
def KuaFuJJCFinalsGuess(role, guessRoleId, guessType):
	roleId = role.GetRoleID()
	
	#是否已经竞猜过
	global KUAFU_JJC_FINALS_GUESS_DICT
	if roleId in KUAFU_JJC_FINALS_GUESS_DICT:
		if guessType in KUAFU_JJC_FINALS_GUESS_DICT[roleId]:
			return
	
	#是否存在这个被竞猜玩家
	if guessRoleId not in FINALS_GUESS_DATA:
		return
	
	if guessType == 1:
		#金币竞猜
		if role.GetMoney() < EnumGameConfig.KUAFU_JJC_FINALS_GUESS_MONEY:
			return
		role.DecMoney(EnumGameConfig.KUAFU_JJC_FINALS_GUESS_MONEY)
			
	elif guessType == 2:
		#神石竞猜
		if role.GetUnbindRMB() < EnumGameConfig.KUAFU_JJC_FINALS_GUESS_RMB:
			return
		role.DecUnbindRMB(EnumGameConfig.KUAFU_JJC_FINALS_GUESS_RMB)
	
	#保存竞猜数据
	if roleId not in KUAFU_JJC_FINALS_GUESS_DICT:
		KUAFU_JJC_FINALS_GUESS_DICT[roleId] = {guessType: guessRoleId}
	else:
		KUAFU_JJC_FINALS_GUESS_DICT[roleId][guessType] = guessRoleId
	KUAFU_JJC_FINALS_GUESS_DICT.changeFlag = True
	
	#同步客户端
	ShowFinalsGuessPanel(role)
	
def VersionClear(role):
	#版本号判断，用于清理数据
	version = WorldData.GetKuaFuJJCVersionId()
	if role.GetI32(EnumInt32.KuaFuJJCVersionID) == version:
		return
	
	#设置版本号
	role.SetI32(EnumInt32.KuaFuJJCVersionID, version)
	
	#清理
	#积分
	role.SetI32(EnumInt32.KuaFuJJCElectionScore, 0)
	role.SetI32(EnumInt32.KuaFuJJCFinalsScore, 0)
	#Obj数据
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	jjcDataDict[KuaFuJJCConfig.ELECTION_CHALLENGE_DATA_OBJ_IDX].clear()
	jjcDataDict[KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX].clear()
	jjcDataDict[KuaFuJJCConfig.UNION_SCORE_REWARD_OBJ_IDX] = []
	
#===============================================================================
# 持久化数据载回后
#===============================================================================
def AfterLoad():
	pass

#===============================================================================
# 显示
#===============================================================================
def ShowUnionScorePanel(role):
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	
	unionId = role.GetUnionID()
	score = UNION_TODAY_SOCRE.get(unionId, 0)
	
	#同步客户端
	role.SendObj(KuaFu_JJC_Show_Union_Score_Panel, (score, jjcDataDict[KuaFuJJCConfig.UNION_SCORE_REWARD_OBJ_IDX]))

def ShowPalacePanel(role):
	roleId = role.GetRoleID()
	if not PALACE_DATA:
		#请求控制进程跨服龙骑殿堂数据
		Call.ServerCall(Define.GetDefaultCrossID(), "Game.KuaFuJJC.KuaFuJJCCross", "LogicRequestCrossPalaceDataCall", (WorldData.GetKuaFuJJCZoneId(), cProcess.ProcessID, roleId))
		#返回空数据
		role.SendObj(KuaFu_JJC_Show_Palace_Panel, [])
		return
	
	role.SendObj(KuaFu_JJC_Show_Palace_Panel, PALACE_DATA)
	
def ShowFinalsGuessPanel(role):
	roleGuessData = KUAFU_JJC_FINALS_GUESS_DICT.get(role.GetRoleID(), {})
	#同步客户端
	role.SendObj(KuaFu_JJC_Show_Finals_Guess_Panel, (FINALS_GUESS_DATA.values(), roleGuessData))

#===============================================================================
# 事件
#===============================================================================
def OnRoleLogin(role, param):
	'''
	角色登陆
	@param role:
	@param param:
	'''
	#初始化Obj
	jjcDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	if KuaFuJJCConfig.ELECTION_CHALLENGE_DATA_OBJ_IDX not in jjcDataDict:
		jjcDataDict[KuaFuJJCConfig.ELECTION_CHALLENGE_DATA_OBJ_IDX] = {}
	if KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX not in jjcDataDict:
		jjcDataDict[KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX] = {}
	if KuaFuJJCConfig.UNION_SCORE_REWARD_OBJ_IDX not in jjcDataDict:
		jjcDataDict[KuaFuJJCConfig.UNION_SCORE_REWARD_OBJ_IDX] = []
	
	#日志
	with TraKuaFuJJCVersionClear:
		#版本号清理
		VersionClear(role)
	
def OnSyncRoleOtherData(role, param):
	'''
	角色登陆同步其它数据
	@param role:
	@param param:
	'''
	#同步客户端
	KuaFuJJCConfig.SyncKuaFuJJCDay(role)

def OnRoleDayClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	kuaFuJJCDataDict = role.GetObj(EnumObj.KuaFuJJCData)
	#重置海选挑战数据
	kuaFuJJCDataDict[KuaFuJJCConfig.ELECTION_CHALLENGE_DATA_OBJ_IDX] = {}
	#重置跨服个人竞技场相关枚举
	role.SetI16(EnumInt16.KuaFuJJCBuyCnt, 0)
	role.SetI16(EnumInt16.KuaFuJJCChallengeCnt, 0)
	role.SetI16(EnumInt16.KuaFuJJCElectionRound, 0)
	role.SetI16(EnumInt16.KuaFuJJCFinalsRound, 0)
	role.SetI16(EnumInt16.KuaFuJJCElectionWinningStreak, 0)
	role.SetI16(EnumInt16.KuaFuJJCFinalsWinningStreak, 0)
	#清理挑战数据
	kuaFuJJCDataDict[KuaFuJJCConfig.ELECTION_CHALLENGE_DATA_OBJ_IDX].clear()
	kuaFuJJCDataDict[KuaFuJJCConfig.FINALS_CHALLENGE_DATA_OBJ_IDX].clear()
	kuaFuJJCDataDict[KuaFuJJCConfig.UNION_SCORE_REWARD_OBJ_IDX] = []
	
#===============================================================================
# 时间
#===============================================================================
def AfterNewDay():
	global UNION_TODAY_SOCRE
	global PALACE_DATA
	UNION_TODAY_SOCRE.clear()
	PALACE_DATA = []
	
def ElectionReady():
	if KuaFuJJCConfig.KUAFU_JJC_DAY >= 2 and KuaFuJJCConfig.KUAFU_JJC_DAY <= 6:
		#传闻
		cRoleMgr.Msg(1, 0, GlobalPrompt.KUAFU_JJC_ELECTION_READY)
	
def ElectionStart():
	if KuaFuJJCConfig.KUAFU_JJC_DAY >= 2 and KuaFuJJCConfig.KUAFU_JJC_DAY <= 6:
		#传闻
		cRoleMgr.Msg(1, 0, GlobalPrompt.KUAFU_JJC_ELECTION_START)
	
def FinalsReady():
	if KuaFuJJCConfig.KUAFU_JJC_DAY == 7:
		#传闻
		cRoleMgr.Msg(1, 0, GlobalPrompt.KUAFU_JJC_FINALS_READY)
	
def FinalsStart():
	if KuaFuJJCConfig.KUAFU_JJC_DAY == 7:
		#传闻
		cRoleMgr.Msg(1, 0, GlobalPrompt.KUAFU_JJC_FINALS_START)
	
#===============================================================================
# 跨服远程call
#===============================================================================
def CrossToLogicJJCElectionUnionReward(msg):
	'''
	收到控制进程同步过来的海选公会奖励数据
	@param sessionid:
	@param msg:
	'''
	rank, unionId = msg
	
	ElectionUnionReward(rank, unionId)
	
def CrossToLogicJJCUnionTodayScore(msg):
	'''
	收到控制进程同步过来的公会今日积分数据
	@param sessionid:
	@param msg:
	'''
	unionScoreDict = msg
	
	RefreshUnionTodayScore(unionScoreDict)

def CrossToLogicJJCPalaceData(msg):
	'''
	收到控制进程同步过来的龙骑殿堂数据
	@param sessionid:
	@param msg:
	'''
	roleId, palaceData = msg
	
	global PALACE_DATA
	PALACE_DATA = palaceData
	
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if not role:
		return
	
	ShowPalacePanel(role)
	
#===============================================================================
# 跨服进程Call
#===============================================================================
def CrossCallToSendFinalsGuessData(guessRoleData):
	if not WorldData.WD.returnDB:
		return
	zoneId = WorldData.GetKuaFuJJCZoneId()
	if zoneId not in guessRoleData:
		return
	
	#保存
	global FINALS_GUESS_DATA
	FINALS_GUESS_DATA = guessRoleData[zoneId]
	
def CrossCallToSendFinalsGuessResult(finalsFirstRoleIdData):
	global FINALS_GUESS_DATA
	global KUAFU_JJC_FINALS_GUESS_DICT
	
	zoneId = WorldData.GetKuaFuJJCZoneId()
	if zoneId not in finalsFirstRoleIdData:
		return
	
	firstRoleId = finalsFirstRoleIdData[zoneId]
	
	#奖励
	for roleId, guessData in KUAFU_JJC_FINALS_GUESS_DICT.iteritems():
		#金币竞猜
		if 1 in guessData:
			guessRoleId = guessData[1]
			if guessRoleId == firstRoleId:
				if guessRoleId not in FINALS_GUESS_DATA:
					continue
				guessRoleName = FINALS_GUESS_DATA[guessRoleId][1]
				
				#正确
				AwardMgr.SetAward(roleId, EnumAward.KuaFuJJCGuessMoneyTrueAward, itemList = [(27920, 1)], clientDescParam = (guessRoleName, ))
		#神石竞猜
		if 2 in guessData:
			guessRoleId = guessData[2]
			if guessRoleId not in FINALS_GUESS_DATA:
					continue
			guessRoleName = FINALS_GUESS_DATA[guessRoleId][1]
			if guessRoleId == firstRoleId:
				#正确
				AwardMgr.SetAward(roleId, EnumAward.KuaFuJJCGuessRMBTrueAward, itemList = [(27922, 1)], clientDescParam = (guessRoleName, ))
			else:
				#错误
				AwardMgr.SetAward(roleId, EnumAward.KuaFuJJCGuessRMBFalseAward, itemList = [(27921, 1)], clientDescParam = (guessRoleName, ))
	
	#决赛结束清理数据
	FinalsOverClear()
	
def FinalsOverClear():
	#缓存
	global PALACE_DATA
	global FINALS_GUESS_DATA
	PALACE_DATA = []
	FINALS_GUESS_DATA.clear()
	#持久化
	global KUAFU_JJC_FINALS_GUESS_DICT
	KUAFU_JJC_FINALS_GUESS_DICT.clear()
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequstKuaFuJJCEnterScene(role, msg):
	'''
	客户端请求进入跨服竞技场场景
	@param role:
	@param msg:
	'''
	#是否可以进入跨服服务器
	if KuaFuJJCConfig.CanJoinKuaFuJJCScene() is False:
		return
	GoToCrossServer(role)

def GoToCrossServer(role):
	#方便测试
	unionName = ""
	leaderName = ""
	unionObj = role.GetUnionObj()
	if unionObj:
		unionName = unionObj.name
		leaderName = unionObj.leader_name
	
	zoneId = WorldData.GetKuaFuJJCZoneId()
	#传送到跨服
	role.GotoCrossServer(None, KuaFuJJCConfig.KUAFU_JJC_SCENE_ID, 958, 579, KuaFuJJCCross.AfterJoinCrossScene, (ZoneName.ZoneName, zoneId, cProcess.ProcessID, unionName, leaderName))
	
def RequstKuaFuJJCBuyKuaFuMoney(role, msg):
	'''
	客户端请求跨服竞技场购买跨服币
	@param role:
	@param msg:
	'''
	rmb = msg
	
	#日志
	with TraKuaFuJJCBuyKuaFuMoney:
		BuyKuaFuMoney(role, rmb)
		
def RequstKuaFuJJCOpenUnionScorePanel(role, msg):
	'''
	客户端请求跨服个人竞技场打开公会积分面板
	@param role:
	@param msg:
	'''
	ShowUnionScorePanel(role)
	
def RequstKuaFuJJCGetUnionScoreReward(role, msg):
	'''
	客户端请求跨服个人竞技场领取公会积分奖励
	@param role:
	@param msg:
	'''
	rewardId = msg
	
	#日志
	with TraKuaFuJJCUnionScoreReward:
		GetUnionScoreReward(role, rewardId)
	
def RequstKuaFuJJCOpenPalacePanel(role, msg):
	'''
	客户端请求跨服个人竞技场打开龙骑殿堂面板
	@param role:
	@param msg:
	'''
	ShowPalacePanel(role)
	
def RequstKuaFuJJCOpenFinalsGuessPanel(role, msg):
	'''
	客户端请求跨服个人竞技场打开决赛竞猜面板
	@param role:
	@param msg:
	'''
	if KuaFuJJCConfig.IsFinals() is False:
		return
	
	ShowFinalsGuessPanel(role)
	
def RequstKuaFuJJCFinalsGuess(role, msg):
	'''
	客户端请求跨服个人竞技场决赛竞猜
	@param role:
	@param msg:
	'''
	guessRoleId, guessType = msg
	
	if KuaFuJJCConfig.CanGuess() is False:
		return
	
	#日志
	with TraKFJJCFinalsGuess:
		KuaFuJJCFinalsGuess(role, guessRoleId, guessType)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		if not Environment.EnvIsNAXP() and not Environment.IsNAPLUS1 and not Environment.EnvIsESP():
			#西班牙不开
			if (Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.IsDevelop or Environment.EnvIsNA()) and not Environment.IsCross:
				#持久化数据
				#跨服个人竞技场决赛竞猜字典{roleId: {guessType: guessRoleId}
				KUAFU_JJC_FINALS_GUESS_DICT = Contain.Dict("KUAFU_JJC_FINALS_GUESS_DICT", (2038, 1, 1), KuaFuJJCFinalsGuessDictAfterLoad)
				
				#事件
				#角色登陆
				Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
				#角色登陆同步其它数据
				Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
				#每日清理调用
				Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
				
				#每日调用
				cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
				
				#时间
				Cron.CronDriveByMinute((2038, 1, 1), ElectionReady, H = "H == 11", M = "M == 55")
				Cron.CronDriveByMinute((2038, 1, 1), ElectionStart, H = "H == 12", M = "M == 0")
				Cron.CronDriveByMinute((2038, 1, 1), FinalsReady, H = "H == 21", M = "M == 55")
				Cron.CronDriveByMinute((2038, 1, 1), FinalsStart, H = "H == 22", M = "M == 0")
				
				
				cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Enter_Scene", "客户端请求进入跨服个人竞技场场景"), RequstKuaFuJJCEnterScene)
				cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Buy_KuaFu_Money", "客户端请求跨服个人竞技场购买跨服币"), RequstKuaFuJJCBuyKuaFuMoney)
				cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Open_Union_Score_Panel", "客户端请求跨服个人竞技场打开公会积分面板"), RequstKuaFuJJCOpenUnionScorePanel)
				cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Get_Union_Score_Reward", "客户端请求跨服个人竞技场领取公会积分奖励"), RequstKuaFuJJCGetUnionScoreReward)
				cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Open_Palace_Panel", "客户端请求跨服个人竞技场打开龙骑殿堂面板"), RequstKuaFuJJCOpenPalacePanel)
				cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Open_Finals_Guess_Panel", "客户端请求跨服个人竞技场打开决赛竞猜面板"), RequstKuaFuJJCOpenFinalsGuessPanel)
				cRoleMgr.RegDistribute(AutoMessage.AllotMessage("KuaFu_JJC_Finals_Guess", "客户端请求跨服个人竞技场决赛竞猜"), RequstKuaFuJJCFinalsGuess)
	
