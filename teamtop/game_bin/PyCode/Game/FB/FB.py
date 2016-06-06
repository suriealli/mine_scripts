#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.FB.FB")
#===============================================================================
# 副本
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.DailyDo import DailyDo
from Game.FB import FBConfig
from Game.Role import Event, Status
from Game.Role.Data import  EnumInt16, EnumDayInt8, EnumObj, EnumCD, EnumInt1,\
	EnumTempObj
from Game.Scene import FBMirror


if "_HasLoad" not in dir():
	#消息
	FB_S_FBStarData = AutoMessage.AllotMessage("FB_S_FBStarData", "同步副本通关星级")
	FB_S_FBJoinCntData = AutoMessage.AllotMessage("FB_S_FBJoinCntData", "同步副本挑战今天的次数")
	FB_S_FB_ZJReward = AutoMessage.AllotMessage("FB_S_FB_ZJReward", "同步副本章节奖励数据")
	FB_S_FB_Progress = AutoMessage.AllotMessage("FB_S_FB_Progress", "同步未完成的副本数据")
	
	#日志
	Tra_FB_GetZJBxReward = AutoLog.AutoTransaction("Tra_FB_GetZJBxReward", "领取章节宝箱奖励")
	Tra_FB_GetZJBx3StarReward = AutoLog.AutoTransaction("Tra_FB_GetZJBx3StarReward", "领取章节3星宝箱奖励")
	Tra_FB_GuaJiReward = AutoLog.AutoTransaction("Tra_FB_GuaJiReward", "副本挂机奖励")
	Tra_FB_CleanFBCD = AutoLog.AutoTransaction("Tra_FB_CleanFBCD", "清除副本挂机CD")
	Tra_FB_BuyAddTime = AutoLog.AutoTransaction("Tra_FB_BuyAddTime", "增加副本参与次数")
	Tra_FB_Join = AutoLog.AutoTransaction("Tra_FB_Join", "进入副本")




def JoinFB(role, msg):
	'''
	请求进入副本
	@param role:
	@param msg:
	'''
	fbId = msg
	reJoin = False
	fbData = role.GetObj(EnumObj.FB_Progress)
	if fbId in fbData:
		reJoin = True
		
	if reJoin is False and role.GetDI8(EnumDayInt8.FB_Times) >= EnumGameConfig.FB_DayMaxPlayTimes:
		return
	
	if not Status.CanInStatus(role, EnumInt1.ST_InMirror):
		return
	
	fbdict = role.GetObj(EnumObj.FB_JoinData)
	joinCnt = fbdict.get(fbId, 0)
	
	if reJoin is False:
		if joinCnt >= EnumGameConfig.FB_EachFBDailyJoinCnt:
			return
	
	if role.GetI16(EnumInt16.FB_Active_ID) < fbId - 1:
		#没有通关上一个关卡
		return
	
	cfg = FBConfig.FB_Config_Dict.get(fbId)
	if not cfg:
		return
	
	if role.GetLevel() < cfg.needLevel:
		return
	
	with Tra_FB_Join:
		#扣除次数
		if reJoin is False:
			role.IncDI8(EnumDayInt8.FB_Times, 1)
			fbdict[fbId] = joinCnt + 1

		#进入副本
		fbm = FBMirror.FBMirror(role, cfg)
		if fbm.createOk is True:
			fbm.AfterJoinRole()
			
		#版本判断
		if Environment.EnvIsNA():
			#北美万圣节活动
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.finish_fb()
		elif Environment.EnvIsRU():
			#七日活动
			sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
			sevenActMgr.finish_fb()
		
		Event.TriggerEvent(Event.Eve_FB_FB, role)
			
def GetMaxBuyTimes(role):
	#根据VIP获取角色购买副本次数
	return FBConfig.FB_BuyAddTimeDict.get(role.GetVIP(), 0)

def FBBuyTimes(role, msg):
	'''
	购买一个副本次数
	@param role:
	@param msg:
	'''
	backId, fbId = msg
	
	cfg = FBConfig.FB_Config_Dict.get(fbId)
	if not cfg:
		return
	if role.GetLevel() < cfg.needLevel:
		return
	
	needRMB = EnumGameConfig.FB_BuyTimesNeedRMB
	#版本判断
	if Environment.EnvIsNA():
		needRMB = EnumGameConfig.FB_BuyTimesNeedRMB_NA
	elif Environment.EnvIsRU():
		needRMB = EnumGameConfig.FB_BuyTimesNeedRMB_RU
	
	if role.GetRMB() < needRMB:
		return
	if role.GetDI8(EnumDayInt8.FB_BuyTimes) >= GetMaxBuyTimes(role):
		return
	
	with Tra_FB_BuyAddTime:
		role.IncDI8(EnumDayInt8.FB_BuyTimes, 1)
		role.DecRMB(needRMB)
		role.DecDI8(EnumDayInt8.FB_Times, 1)
	
	fbdict = role.GetObj(EnumObj.FB_JoinData)
	cnt = fbdict.get(fbId, 0)
	cnt -= 1
	fbdict[fbId] = cnt
	role.CallBackFunction(backId, fbId)

def FBReset(role, msg):
	'''
	重置副本
	@param role:
	@param msg:
	'''
	#清理一个未完成的副本的挑战记录
	backId, fbId = msg
	
	if Status.IsInStatus(role, EnumInt1.ST_InMirror):
		return
	
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	fbData = role.GetObj(EnumObj.FB_Progress)
	if fbId not in fbData:
		return
	
	#删除进度数据
	del fbData[fbId]
	
	role.CallBackFunction(backId, fbId)

def FBGuaJi(role, msg):
	'''
	请求副本挂机
	@param role:
	@param msg:
	'''
	backId, fbId = msg
	
	if role.GetDI8(EnumDayInt8.FB_Times) >= EnumGameConfig.FB_DayMaxPlayTimes:
		#没次数了
		return
	
	fbData = role.GetObj(EnumObj.FB_Progress)
	if fbId in fbData:
		#需要先完成才能挂机
		return
	
	fbStarData = role.GetObj(EnumObj.FB_Star)
	star = fbStarData.get(fbId)
	if not star:
		return
	
	fbdict = role.GetObj(EnumObj.FB_JoinData)
	joinCnt = fbdict.get(fbId, 0)
	if joinCnt >= EnumGameConfig.FB_EachFBDailyJoinCnt:
		return
	
	cfg = FBConfig.FB_Config_Dict.get(fbId)
	if not cfg:
		return
	
	#版本特权判断
	if Environment.EnvIsNA():
		#北美版
		if not role.GetCD(EnumCD.Card_HalfYear) and not role.GetCD(EnumCD.Card_Year):
			if role.GetCD(EnumCD.FB_GuaJiCD):
				return
			#CD
			role.SetCD(EnumCD.FB_GuaJiCD, EnumGameConfig.FB_GuaJiCD)
	else:
		#其他版本
		if role.GetVIP() < EnumGameConfig.FB_VIP_Free:
			if role.GetCD(EnumCD.FB_GuaJiCD):
				return
			#CD
			role.SetCD(EnumCD.FB_GuaJiCD, EnumGameConfig.FB_GuaJiCD)
	
	with Tra_FB_GuaJiReward:
		#总次数
		role.IncDI8(EnumDayInt8.FB_Times, 1)
		#这个副本今天已经使用的次数
		fbdict[fbId] = joinCnt + 1
		
		#奖励
		cfg.GuaJiReward(role, star)
		role.CallBackFunction(backId, fbId)
		#每日必做 -- 副本
		Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_FB, 1))
		
		Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_FB, 1))
		
		#版本判断
		if Environment.EnvIsNA():
			#北美万圣节活动
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.finish_fb()
		elif Environment.EnvIsRU():
			#七日活动
			sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
			sevenActMgr.finish_fb()
		
		Event.TriggerEvent(Event.Eve_FB_FB, role)
	
def FBBuyCD(role, msg):
	'''
	副本秒CD
	@param role:
	@param msg:
	'''
	sec = role.GetCD(EnumCD.FB_GuaJiCD)
	if not sec:
		return
	totalMinute = sec / 60
	if sec % 60 > 0:
		totalMinute += 1
	
	perRMB = EnumGameConfig.FB_BuyCDNeedRMB
	#版本判断
	if Environment.EnvIsNA():
		perRMB = EnumGameConfig.FB_BuyCDNeedRMB_NA
		
	needRMB = totalMinute * perRMB
	if role.GetRMB() < needRMB:
		return
	with Tra_FB_CleanFBCD:
		role.DecRMB(needRMB)
		role.SetCD(EnumCD.FB_GuaJiCD, 0)


def FBGetZJReward(role, msg):
	'''
	领取章节通关奖励
	@param role:
	@param msg:
	''' 
	
	backId, zjId = msg
	
	zjDataSet = role.GetObj(EnumObj.FB_ZJReward)[1]
	if zjId in zjDataSet:
		return 
	
	maxID = FBConfig.FBZJ_MaxFBId.get(zjId)
	if not maxID:
		return
	
	if role.GetI16(EnumInt16.FB_Active_ID) < maxID:
		return
	
	rewardCfg = FBConfig.FBZJRewardConfig_Dict.get(zjId)
	if not rewardCfg:
		return
	
	with Tra_FB_GetZJBxReward:
		zjDataSet.add(zjId)
		rewardCfg.FinishReward(role)
	
	role.CallBackFunction(backId, zjId)

def FBGetZJ3StarReward(role, msg):
	'''
	领取章节3星通关奖励
	@param role:
	@param msg:
	'''
	backId, zjId = msg
	
	zjDataSet = role.GetObj(EnumObj.FB_ZJReward)[2]
	if zjId in zjDataSet:
		return 
	
	rewardCfg = FBConfig.FBZJRewardConfig_Dict.get(zjId)
	if not rewardCfg:
		return
	
	fbIds = FBConfig.FBZJ_Config_Dict.get(zjId)
	if not fbIds:
		return
	
	starDataDict = role.GetObj(EnumObj.FB_Star)
	SG = starDataDict.get
	for fbId in fbIds:
		if 3 != SG(fbId):
			#需要全部3星
			return
	
	with Tra_FB_GetZJBx3StarReward:
		zjDataSet.add(zjId)
	
		rewardCfg.ThreeStarReward(role)
	
	role.CallBackFunction(backId, zjId)


def RequestFBData(role, msg):
	'''
	请求副本数据
	@param role:
	@param msg:
	'''
	role.SendObj(FB_S_FBJoinCntData, role.GetObj(EnumObj.FB_JoinData))
	role.SendObj(FB_S_FB_Progress, role.GetObj(EnumObj.FB_Progress).keys())
	

def RoleDayClear(role, param):
	#每日清理
	role.SetObj(EnumObj.FB_JoinData, {})

def SyncRoleOtherData(role, param):
	role.SendObj(FB_S_FBStarData, role.GetObj(EnumObj.FB_Star))
	role.SendObj(FB_S_FB_ZJReward, role.GetObj(EnumObj.FB_ZJReward))


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		#客户端请求消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FB_JoinFB", "请求进入副本"), 		JoinFB)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FB_FBBuyTimes", "请求购买副本次数"), FBBuyTimes)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FB_FBReset", "请求重置副本进度"), FBReset)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FB_FBGuaJi", "请求请求副本挂机"), FBGuaJi)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FB_FBBuyCD", "请求清除副本挂机CD"), FBBuyCD)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FB_FBGetZJReward", "请求领取章节通关奖励"), FBGetZJReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FB_FBGetZJ3StarReward", "领取章节3星通关奖励"), FBGetZJ3StarReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FB_FBRequestFBData", "请求获取副本全部数据"), RequestFBData)
		



