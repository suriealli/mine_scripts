#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#XRLAM("Game.Activity.ChunJieYuanXiao.ChunJieYuanXiaoMgr")
#===============================================================================
# 元宵花灯活动
#===============================================================================
import cRoleMgr
import Environment
from Common.Other import EnumGameConfig, GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Activity.ChunJieYuanXiao import ChunJieYuanXiaoConfig, YuanXiaoDefine
from Game.Role.Data import EnumDayInt8, EnumInt16, EnumInt1, EnumObj, EnumInt32, EnumInt8
from Util import Random
from Game.Role import Event
from Game.Activity.PassionAct.PassionDefine import PassionChunJieYuanXiao

if "_HasLoad" not in dir():
	IsStart = False
	#消息同步
	YuanXiaoHeroData = AutoMessage.AllotMessage("YuanXiaoHeroData", "元宵花灯英雄数据")
	#日志的同步
	YuanXiaoHeight_Log = AutoLog.AutoTransaction("YuanXiaoHeight_Log", "元宵花灯活动高度日志")
	YuanXiaoReward_Log = AutoLog.AutoTransaction("YuanXiaoReward_Log", "元宵花灯活动奖励日志")
	YuanXiaoBuyHuaDeng_Log = AutoLog.AutoTransaction("YuanXiaoBuyHuaDeng_Log", "元宵花灯活动购买日志")
	YuanXiaoLightHuaDeng_Log = AutoLog.AutoTransaction("YuanXiaoLightHuaDeng_Log", "元宵花灯活动点亮日志")
	

def OpenActive(*param):
	_, circularType = param
	if CircularDefine.CA_ChunJieYuanXiao != circularType:
		return
	global IsStart
	if IsStart  :
		print "GE_EXC, repeat PassionChunJieActive has started"
	IsStart = True

def CloseActive(*param):
	_, circularType = param
	if CircularDefine.CA_ChunJieYuanXiao != circularType :
		return
	global IsStart
	if not IsStart :
		print "GE_EXC, repeat PassionChunJieActive has closed"
	IsStart = False

#========================================================================================
#活动流程
#========================================================================================

def RequestBuyHuaDeng(role, param = 0):
	'''
	购买花灯
	'''
	global IsStart
	if not IsStart :
		return
	#等级不够
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	HuadengDict = ChunJieYuanXiaoConfig.YuanXiaoBuyHuaDeng
	#超过购买次数
	if len(HuadengDict) <= role.GetDI8(EnumDayInt8.YuanXiaoHuaDengBuyTimes) :
		return
	BuyTimes = role.GetDI8(EnumDayInt8.YuanXiaoHuaDengBuyTimes) + 1
	HuaDengMgr = HuadengDict.get(BuyTimes)
	if not HuaDengMgr :
		print "GE_EXC, repeat no BuyIndex %s in YuanXiaoBuyHuaDeng" % BuyTimes
		return
	#不够神石
	if HuaDengMgr.CostRmb > role.GetUnbindRMB_Q() :
		return
	with YuanXiaoBuyHuaDeng_Log :
		role.SetDI8(EnumDayInt8.YuanXiaoHuaDengBuyTimes, BuyTimes)
		role.DecUnbindRMB_Q(HuaDengMgr.CostRmb)
		role.IncI16(EnumInt16.ChunJieYuanXiao, HuaDengMgr.Award)
		Tip =GlobalPrompt.PassionYuanXiaoTip % HuaDengMgr.Award
		role.Msg(2, 0, Tip)

def RequestLightHuaDeng(role, param = 0):
	'''
	点亮花灯
	'''
	global IsStart
	if not IsStart :
		return
	#等级不够
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	#没有花灯
	if not role.GetI16(EnumInt16.ChunJieYuanXiao) :
		return
	#已经点亮花灯
	if role.GetI1(EnumInt1.YuanXiaoHuaDeng) :
		return
	with YuanXiaoLightHuaDeng_Log :
		role.DecI16(EnumInt16.ChunJieYuanXiao, 1)
		role.SetI1(EnumInt1.YuanXiaoHuaDeng, 1)
		tip = GlobalPrompt.PassionYuanXiaoLightHuaDeng
		role.Msg(2, 0, tip)
	



def RequestRaiseHeight(role, ways = 0):
	'''
	提升高度
	'''
	global IsStart
	if not IsStart :
		return
	#1代表免费，2代表20充值神石， 3代表100充值神石， 4代表500充值神石
	if ways not in (1,2,3,4) :
		return
	#等级不够
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	# 没有点亮花灯
	if not role.GetI1(EnumInt1.YuanXiaoHuaDeng) :
		return
	#10次机会
	if role.GetI8(EnumInt8.ChunJieYuanXiaoRaiseTimes) >= 10 :
		return
	HasRmb = role.GetUnbindRMB()
	if ways == 1 and role.GetDI8(EnumDayInt8.YuanXiaoLightHuaDengFreeTimes) >= YuanXiaoDefine.Free_Height :
		return
	elif ways == 2 and HasRmb < YuanXiaoDefine.Need_Low_RMB :
		return
	elif ways == 3 and HasRmb < YuanXiaoDefine.Need_Mid_RMB :
		return
	elif ways == 4 and HasRmb < YuanXiaoDefine.Need_Hight_RMB :
		return
	with YuanXiaoHeight_Log :
		role.IncI8(EnumInt8.ChunJieYuanXiaoRaiseTimes, 1)
		IncHeight = 0			#增加的高度
		#免费提升
		if ways == 1 :
			role.IncDI8(EnumDayInt8.YuanXiaoLightHuaDengFreeTimes, 1)
			IncHeight = YuanXiaoDefine.Raise_Free_Height
		#20充值神石提升
		elif ways == 2 :
			role.DecUnbindRMB(YuanXiaoDefine.Need_Low_RMB)
			IncHeight = YuanXiaoDefine.Raise_Low_Height
		#100充值神石提升
		elif ways == 3 :
			role.DecUnbindRMB(YuanXiaoDefine.Need_Mid_RMB)
			IncHeight = YuanXiaoDefine.Raise_Mid_Height
		#500充值神石提升
		elif ways == 4 :
			role.DecUnbindRMB(YuanXiaoDefine.Need_Hight_RMB)
			IncHeight = YuanXiaoDefine.Raise_Hight_Height
		#提升高度
		GetHeightRandom(role, IncHeight, ways)
		


def GetHeightRandom(role, IncHeight, Grade):
	'''
	随机事件
	IncHeight为增加的高度
	'''
	YuanXiaoEvent = Random.RandomRate()
	if PassionChunJieYuanXiao not in role.GetObj(EnumObj.PassionActData) :
		role.GetObj(EnumObj.PassionActData)[PassionChunJieYuanXiao] = set()
	YuanXiaoHearoDatas = role.GetObj(EnumObj.PassionActData)[PassionChunJieYuanXiao]
	IncBuffer = {"IncHit" :0, "IncHitRate":0, "IncNormalRate":0, "IncSpecialRate":0}
	for heroId in YuanXiaoHearoDatas :
		heroMgr = ChunJieYuanXiaoConfig.YuanXiaoHeroDict.get((heroId, Grade))
		if not heroMgr :
			print "GE_EXC, repeat no heroId %s in YuanXiaoHeroDict in GetHeightRandom" % heroId
			return
		if heroMgr.IncHit :
			#增加暴击效果
			IncBuffer["IncHit"] += heroMgr.IncHit
		elif heroMgr.IncHitRate :
			#增加暴击概率
			IncBuffer["IncHitRate"] += heroMgr.IncHitRate
		elif heroMgr.IncNormalRate :
			#增加普通英雄概率
			IncBuffer["IncNormalRate"] += heroMgr.IncNormalRate
		elif heroMgr.IncSpecialRate :
			#增加高级英雄概率
			IncBuffer["IncSpecialRate"] += heroMgr.IncSpecialRate
		
	for param, config in ChunJieYuanXiaoConfig.YuanXiaoHeroDict.iteritems() :
		heroId, herograde = param
		#抽奖档次 
		if herograde != Grade :
			continue
		#普通英雄概率
		if config.HeroAttribute == 1 :
			rate = IncBuffer["IncNormalRate"] + config.Rate
			
		#高级英雄概率
		elif config.HeroAttribute == 2 :
			rate = IncBuffer["IncSpecialRate"] + config.Rate
		#暴击事件
		elif config.HeroAttribute == 3 :
			rate = IncBuffer["IncHitRate"] + config.Rate
		else :
			rate = config.Rate
		YuanXiaoEvent.AddRandomItem(rate, heroId)
		
	Eventid = YuanXiaoEvent.RandomOne()
	heroMgr = ChunJieYuanXiaoConfig.YuanXiaoHeroDict.get((Eventid,Grade))
	if not heroMgr :
		print "GE_EXC, repeat no Eventid %s in YuanXiaoHeroDict in GetHeightRandom" % Eventid
		return
	#抽中了英雄
	if heroMgr.HeroAttribute == 1 or heroMgr.HeroAttribute == 2:
		if Eventid not in YuanXiaoHearoDatas :
			YuanXiaoHearoDatas.add(Eventid)
			#同步最新英雄信息给客户端
			role.SendObj(YuanXiaoHeroData, YuanXiaoHearoDatas)
		role.IncI32(EnumInt32.ChunJieYuanXiaoHeight, IncHeight)
		tip = GlobalPrompt.PassionYuanXiaoIncHeightTip % IncHeight
	#抽中了暴击事件
	elif heroMgr.HeroAttribute == 3 :
		IncHeghtBase = IncBuffer["IncHit"]
		IncHeight = IncHeight * ((1.5*10000 + IncHeghtBase) / 10000)
		IncHeight = int(IncHeight)
		role.IncI32(EnumInt32.ChunJieYuanXiaoHeight, IncHeight)
		tip = GlobalPrompt.PassionYuanXiaoIncMoreHeightTip % IncHeight
	#普通事件
	else :
		role.IncI32(EnumInt32.ChunJieYuanXiaoHeight, IncHeight)
		tip = GlobalPrompt.PassionYuanXiaoIncHeightTip % IncHeight
	
	role.Msg(2, 0, tip)



def RequestYuanXiaoHeightReward(role, param = 0):
	'''
	请求领取高度奖励
	'''
	global IsStart
	if not IsStart :
		return
	RoleLevel = role.GetLevel()
	if RoleLevel < EnumGameConfig.Level_30:
		return
	# 没有点亮花灯
	if not role.GetI1(EnumInt1.YuanXiaoHuaDeng) :
		return
	with YuanXiaoReward_Log :
		Height = role.GetI32(EnumInt32.ChunJieYuanXiaoHeight)
		awardId = 0
		for config in ChunJieYuanXiaoConfig.YuanXiaoHeigtAwardDict.itervalues() :
			if config.Height[0] <= Height <= config.Height[1] and config.Level[0] <= RoleLevel <= config.Level[1]:
				awardId = config.AwaIndex
				break
		if not awardId :
			print "GE_EXC, repeat no Height %s or Level %s in YuanXiaoHeigtAwardDict in RequestYuanXiaoHeightReward" % (Height, RoleLevel)
			return
		#获取第一个奖励index
		for configs in ChunJieYuanXiaoConfig.YuanXiaoHeigtAwardDict.itervalues() :
			if configs.Height[0] <= 0 <= configs.Height[1] and configs.Level[0] <= RoleLevel <= configs.Level[1]:
				beginIndex = configs.AwaIndex 
				break
		if not beginIndex:
			print "GE_EXC, repeat no 0 or Level %s in YuanXiaoHeigtAwardDict in RequestYuanXiaoHeightReward" % RoleLevel
			return
		role.SetI8(EnumInt8.ChunJieYuanXiaoRaiseTimes, 0)
		role.SetI1(EnumInt1.YuanXiaoHuaDeng, 0)
		role.SetI32(EnumInt32.ChunJieYuanXiaoHeight, 0)
		role.SetDI8(EnumDayInt8.YuanXiaoLightHuaDengFreeTimes, 0)
		if not config.Reward :
			return
		#随机奖励其中一个物品 
		Awardradom = ChunJieYuanXiaoConfig.YuanXiaoHeightRandom
		Tips = GlobalPrompt.Reward_Tips
		while beginIndex <= awardId :
			
			itemsCoding = Awardradom.get(beginIndex).RandomOne()
			for item, cnt ,_3 in ChunJieYuanXiaoConfig.YuanXiaoHeigtAwardDict.get(beginIndex).Reward :
				if itemsCoding != item : 
					continue
				role.AddItem(item, cnt)
				Tips += GlobalPrompt.PassionYuanXiaoHuaDengAward % (beginIndex - 1,item, cnt)
				break
			role.Msg(2, 0, Tips)
			Tips = ""
			beginIndex += 1
		

#===============================================================
#新的一天
#===============================================================


def ClearRoleData(role, param =0):
	'''
	每天清理
	'''
	global IsStart
	role.SetI32(EnumInt32.ChunJieYuanXiaoHeight, 0)
	role.SetI1(EnumInt1.YuanXiaoHuaDeng, 0)
	role.SetI16(EnumInt16.ChunJieYuanXiao, 2)
	role.SetI8(EnumInt8.ChunJieYuanXiaoRaiseTimes, 0)
	
def SyncRoleOtherData(role, param = 0):
	'''
	登陆后同步数据
	'''
	if PassionChunJieYuanXiao not in role.GetObj(EnumObj.PassionActData) :
		role.GetObj(EnumObj.PassionActData)[PassionChunJieYuanXiao] = set()
	YuanXiaoHearoDatas = role.GetObj(EnumObj.PassionActData)[PassionChunJieYuanXiao]
	role.SendObj(YuanXiaoHeroData, YuanXiaoHearoDatas)
	#第一次参加活动
	if not role.GetI1(EnumInt1.TheFristTimeYuanXiaoHuaDeng) :
		role.SetI1(EnumInt1.TheFristTimeYuanXiaoHuaDeng, 1)
		with YuanXiaoBuyHuaDeng_Log:
			role.SetI16(EnumInt16.ChunJieYuanXiao, 2)



if "_HasLoad" not in dir() :
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OpenActive)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseActive)
		Event.RegEvent(Event.Eve_RoleDayClear, ClearRoleData)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestChunJieYuanXiaoBuyHuaDeng", "元宵节购买花灯"), RequestBuyHuaDeng)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestChunJieYuanXiaoHeightReward", "元宵领取高度奖励"), RequestYuanXiaoHeightReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestChunJieYuanXiaoRaiseHeight", "元宵提升花灯高度"), RequestRaiseHeight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestChunJieYuanXiaoLightHuaDeng", "元宵点亮花灯"), RequestLightHuaDeng)