#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ZhongQiu.ZhongQiuShangYueMgr")
#===============================================================================
# 中秋赏月 Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Mail import Mail
from Game.Activity import CircularDefine
from Game.Role.Data import EnumObj, EnumInt8
from Game.Activity.ZhongQiu import ZhongQiuShangYueConfig

IDX_REWARD = 2

if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_ZhongQiuShangYue_AuToReward = AutoLog.AutoTransaction("Tra_ZhongQiuShangYue_AuToReward", "中秋赏月_活动结束自动发奖")
	Tra_ZhongQiuShangYue_YiCiShangYue = AutoLog.AutoTransaction("Tra_ZhongQiuShangYue_YiCiShangYue", "中秋赏月_一次赏月")
	Tra_ZhongQiuShangYue_ShiCiShangYue = AutoLog.AutoTransaction("Tra_ZhongQiuShangYue_ShiCiShangYue", "中秋赏月_十次赏月")
	Tra_ZhongQiuShangYue_GetReward = AutoLog.AutoTransaction("Tra_ZhongQiuShangYue_GetReward", "中秋赏月_一键拾取奖励")
	Tra_ZhongQiuShangYue_DefaultSuit = AutoLog.AutoTransaction("Tra_ZhongQiuShangYue_DefaultSuit", "中秋赏月_初始化奖励套")
	
	
	ZhongQiuShangYue_RewardState_S = AutoMessage.AllotMessage("ZhongQiuShangYue_RewardState_S", "中秋赏月_奖励数据同步")

#===============================================================================
# 活动控制
#===============================================================================
def OnStartZhongQiuShangYue(*param):
	'''
	活动开启
	'''
	_, circularType = param
	if CircularDefine.CA_ZhongQiuShangYue != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open ZhongQiuShangYue"
		return
		
	IS_START = True
	

def OnEndZhongQiuShangYue(*param):
	'''
	活动结束
	'''
	_, circularType = param
	if CircularDefine.CA_ZhongQiuShangYue != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end ZhongQiuShangYue while not start"
		return
		
	IS_START = False
	
	#处理在线玩家未领取奖励自动邮件发奖励
	for role in cRoleMgr.GetAllRole():
		TryAuToReward(role)


#===============================================================================
# 客户端请求
#===============================================================================
def OnOpenPanel(role, msg = None):
	'''
	中秋赏月_请求打开界面
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ZhongQiuShangYue_NeedLevel:
		return
	
	if role.GetI8(EnumInt8.ZhongQiuShangYue_RewardSuitID) not in ZhongQiuShangYueConfig.ZhongQiuShangYue_RewardSuit_Set:
		with Tra_ZhongQiuShangYue_DefaultSuit:
			role.SetI8(EnumInt8.ZhongQiuShangYue_RewardSuitID, 1)
		
	role.SendObj(ZhongQiuShangYue_RewardState_S, role.GetObj(EnumObj.ZhongQiuData)[IDX_REWARD])


def OnLottery(role, msg = None):
	'''
	中秋赏月_请求一次赏月
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ZhongQiuShangYue_NeedLevel:
		return
	
	if (role.ItemCnt_NotTimeOut(EnumGameConfig.ZhongQiuShangYue_LotteryCoding) < 1):
		haveLotteryItem = False
	else:
		haveLotteryItem = True
	
	if not haveLotteryItem and (role.GetUnbindRMB() < EnumGameConfig.ZhongQiuShangYue_LotteryRMB):
		return
	
	#有未领取的奖励
	if len(role.GetObj(EnumObj.ZhongQiuData)[IDX_REWARD]) > 0:
		return
	
	with Tra_ZhongQiuShangYue_YiCiShangYue:
		if haveLotteryItem:
			DoItemLottery(role)
		else:
			DoRMBLottery(role, 1)


def OnShiCiLottery(role, msg = None):
	'''
	中秋赏月_请求十次赏月
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ZhongQiuShangYue_NeedLevel:
		return
	
	haveCnt = role.ItemCnt_NotTimeOut(EnumGameConfig.ZhongQiuShangYue_LotteryCoding)	
	needItemCnt = min(10, haveCnt)
	needRMB = max(0, (10 - haveCnt) * EnumGameConfig.ZhongQiuShangYue_LotteryRMB)	
	if role.ItemCnt(EnumGameConfig.ZhongQiuShangYue_LotteryCoding) < needItemCnt or role.GetUnbindRMB() < needRMB:
		return
	
	#有未领取的奖励
	if len(role.GetObj(EnumObj.ZhongQiuData)[IDX_REWARD]) > 0:
		return
	
	with Tra_ZhongQiuShangYue_ShiCiShangYue:
		DoRMBLottery(role, 10)


def OnGetReward(role, msg = None):
	'''
	中秋赏月_请求拾取奖励
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ZhongQiuShangYue_NeedLevel:
		return
	
	rewardIdList = role.GetObj(EnumObj.ZhongQiuData)[IDX_REWARD]
	if len(rewardIdList) < 1:
		return
	
	prompt = GlobalPrompt.Reward_Tips
	with Tra_ZhongQiuShangYue_GetReward:
		#删除未拾取奖励记录
		role.GetObj(EnumObj.ZhongQiuData)[IDX_REWARD] = []
		#获得
		for tRewardId in rewardIdList:
			tRewardCfg = ZhongQiuShangYueConfig.ZhongQiuShangYue_BaseConfig_Dict.get(tRewardId, None)
			if tRewardCfg:
				coding, cnt = tRewardCfg.rewardItem
				role.AddItem(coding, cnt)
				prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#获得提示
	role.Msg(2, 0, prompt)
	#同步最新奖励状态数据
	role.SendObj(ZhongQiuShangYue_RewardState_S, role.GetObj(EnumObj.ZhongQiuData)[IDX_REWARD])
		

#===============================================================================
# 辅助
#===============================================================================
def DoItemLottery(role):
	'''
	道具赏月 
	'''
	lotteryType = 0
	roleLevel = role.GetLevel()
	rewardSuitId = role.GetI8(EnumInt8.ZhongQiuShangYue_RewardSuitID)
	randomObj = ZhongQiuShangYueConfig.GetRewardRandomObj(lotteryType, roleLevel, rewardSuitId)
	if not randomObj:
		print "GE_EXC, DoItemLottery::can not get RandomObj by lotteryType(%s), roleLevel(%s),rewardSuitId(%s), role(%s)" % (lotteryType, roleLevel, rewardSuitId, role.GetRoleID())
		return
	
	rewardInfo = randomObj.RandomOne()
	rewardId, coding, cnt, isPrecious, isBroad = rewardInfo
	
	rewardList = [rewardId]
	role.GetObj(EnumObj.ZhongQiuData)[IDX_REWARD] = rewardList
	
	#扣除道具
	role.DelItem(EnumGameConfig.ZhongQiuShangYue_LotteryCoding, 1)
	
	#珍稀奖励更新奖励套
	if isPrecious:
		if rewardSuitId + 1 in ZhongQiuShangYueConfig.ZhongQiuShangYue_RewardSuit_Set:
			newRewardSuitId = rewardSuitId + 1
		else:
			newRewardSuitId = 1
		
		role.SetI8(EnumInt8.ZhongQiuShangYue_RewardSuitID, newRewardSuitId) 
	#广播 
	if isBroad:
		cRoleMgr.Msg(11, 0, GlobalPrompt.ZhongQiuShangYue_Msg_Precious % (role.GetRoleName(), coding, cnt))
	
	role.SendObj(ZhongQiuShangYue_RewardState_S, rewardList)
	

def DoRMBLottery(role, lotteryCnt):
	'''
	神石赏月 
	'''
	lotteryType = 1
	roleLevel = role.GetLevel()	
	
	rewardList = []
	for _ in xrange(lotteryCnt):
		rewardSuitId = role.GetI8(EnumInt8.ZhongQiuShangYue_RewardSuitID)
		randomObj = ZhongQiuShangYueConfig.GetRewardRandomObj(lotteryType, roleLevel, rewardSuitId)
		if not randomObj:
			print "GE_EXC, DoRMBLottery::can not get RandomObj by lotteryType(%s), roleLevel(%s),rewardSuitId(%s), role(%s)" % (lotteryType, roleLevel, rewardSuitId, role.GetRoleID())
			return
		
		rewardInfo = randomObj.RandomOne()
		rewardId, coding, cnt, isPrecious, isBroad = rewardInfo
		
		rewardList.append(rewardId)
		
		#珍稀奖励更新奖励套
		if isPrecious:
			if rewardSuitId + 1 in ZhongQiuShangYueConfig.ZhongQiuShangYue_RewardSuit_Set:
				newRewardSuitId = rewardSuitId + 1
			else:
				newRewardSuitId = 1
			
			role.SetI8(EnumInt8.ZhongQiuShangYue_RewardSuitID, newRewardSuitId) 
		#广播
		if isBroad:
			cRoleMgr.Msg(11, 0, GlobalPrompt.ZhongQiuShangYue_Msg_Precious % (role.GetRoleName(), coding, cnt))
	
	#更新奖励状态数据
	role.GetObj(EnumObj.ZhongQiuData)[IDX_REWARD] = rewardList
	#扣除神石
	role.DecUnbindRMB(EnumGameConfig.ZhongQiuShangYue_LotteryRMB * lotteryCnt)
	#同步客户端最新奖励状态
	role.SendObj(ZhongQiuShangYue_RewardState_S, rewardList)	


#===============================================================================
# 事件
#===============================================================================
def TryAuToReward(role, param = None):
	'''
	角色上线 处理活动结束之后邮件发抽取而未领取的奖励
	'''
	#活动中 不处理
	if IS_START:
		return
	
	rewardDict = {}
	tShangyueRewardIdList = role.GetObj(EnumObj.ZhongQiuData)[IDX_REWARD]
	if len(tShangyueRewardIdList) > 0:
		for tRewardId in tShangyueRewardIdList:
			tRewardCfg = ZhongQiuShangYueConfig.ZhongQiuShangYue_BaseConfig_Dict.get(tRewardId, None)
			if tRewardCfg:
				coding ,cnt = tRewardCfg.rewardItem
				if coding in rewardDict:
					rewardDict[coding] += cnt
				else:
					rewardDict[coding] = cnt
	
	if len(rewardDict) < 1:
		return
	
	with Tra_ZhongQiuShangYue_AuToReward:
		#处理过了 删除角色记录的奖励数据
		role.GetObj(EnumObj.ZhongQiuData)[IDX_REWARD] = []
		#统计有奖励 处理下
		rewardList = []
		for coding, cnt in rewardDict.iteritems():
			rewardList.append([coding, cnt])
		if len(rewardList):
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.ZhongQiuShangYue_Mail_Title, GlobalPrompt.ZhongQiuShangYue_Mail_Sender, GlobalPrompt.ZhongQiuShangYue_Mail_Content, items = rewardList)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveShangYueAuToReward, (tShangyueRewardIdList, rewardList))
	
	
def OnInitPyRole(role, param = None):
	'''
	初始化相关key
	'''
	zhongQiuDataDict = role.GetObj(EnumObj.ZhongQiuData)
	if IDX_REWARD not in zhongQiuDataDict:
		zhongQiuDataDict[IDX_REWARD] = []


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_InitRolePyObj, OnInitPyRole)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, TryAuToReward)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartZhongQiuShangYue)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndZhongQiuShangYue)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ZhongQiuShangYue_OnOpenPanel", "中秋赏月_请求打开界面"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ZhongQiuShangYue_OnLottery", "中秋赏月_请求一次赏月"), OnLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ZhongQiuShangYue_OnShiCiLottery", "中秋赏月_请求十次赏月"), OnShiCiLottery)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ZhongQiuShangYue_OnGetReward", "中秋赏月_请求拾取奖励"), OnGetReward)
		