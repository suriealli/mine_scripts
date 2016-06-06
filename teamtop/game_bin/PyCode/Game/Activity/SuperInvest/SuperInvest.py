#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SuperInvest.SuperInvest")
#===============================================================================
# 超级投资
#===============================================================================
import Environment
import cRoleMgr
import cDateTime
from Common.Message import AutoMessage
from Game.Role import Event
from Game.Role.Data import EnumObj
from Game.Activity.SuperInvest import SuperInvestConfig
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt

if "_HasLoad" not in dir():
	#{超级投资索引：｛1：购买时间， 2：已领取奖励索引｝}
	SuperInvestData = AutoMessage.AllotMessage("SuperInvestData", "超级投资数据")
	
	FlagDict = {320:False, 321:False, 322:False, 323:False, 324:False, 325:False, 326:False, 327:False, 329:False, 330:False, 331:False}
	
	SuperInvestInvest_Log = AutoLog.AutoTransaction("SuperInvestInvest_Log", "超级投资投资日志")
	SuperInvestReward_Log = AutoLog.AutoTransaction("SuperInvestReward_Log", "超级投资领取奖励日志")
	
def OpenSuperInvest(param1, param2):
	if param2 not in FlagDict:
		return
	if FlagDict[param2]:
		print 'GE_EXC, SuperInvest repeat open %s' % param2
	FlagDict[param2] = True
	
def CloseSuperInvest(param1, param2):
	if param2 not in FlagDict:
		return
	if not FlagDict[param2]:
		print 'GE_EXC, SuperInvest repeat close %s' % param2
	FlagDict[param2] = False
	
def RequestInvest(role, msg):
	'''
	请求超级投资投资
	@param role:
	@param msg:投资超级投资索引（循环活动活动类型）
	'''
	investIndex = msg
	
	global FlagDict
	flag = FlagDict.get(investIndex)
	if not flag:
		#活动没有开启不能投资
		return
	
	cfg = SuperInvestConfig.SuperInvest_Dict.get(investIndex)
	if not cfg:
		#没有配置
		return
	
	if role.GetLevel() < cfg.needLevel:
		#等级不够
		return
	
	if role.GetUnbindRMB_Q() < cfg.needRMB:
		#充值神石不够
		return
	
	superInvestObj = role.GetObj(EnumObj.SuperInvestObj)
	if not superInvestObj:
		superInvestObj = {}
	
	if investIndex in superInvestObj:
		#已经投资过了
		return
	
	with SuperInvestInvest_Log:
		#扣钱
		role.DecUnbindRMB_Q(cfg.needRMB)
		
		#生成投资数据
		superInvestObj[investIndex] = {1:cDateTime.Days(), 2:set()}
		role.SetObj(EnumObj.SuperInvestObj, superInvestObj)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveSuperInvestInvest, investIndex)
	
	#同步客户端
	role.SendObj(SuperInvestData, superInvestObj)
	
	role.Msg(2, 0, GlobalPrompt.SuperInvestSuccess)
	
def RequestReward(role, msg):
	'''
	请求超级投资领取奖励
	@param role:
	@param msg:（超级投资投资索引， 天数）
	'''
	investIndex, days = msg
	
	#这里不判断活动是否开启, 活动结束后还是可以领取的
	#但是如果下次活动开启还没有领取, 只有领取后才能继续投资
	#如果在活动期间奖励全部领取了, 还可以继续投资该项目
	
	cfg = SuperInvestConfig.SuperInvest_Dict.get(investIndex)
	if not cfg:
		#没有配置
		return
	
	rewardDict = cfg.dayReward.get(days)
	if not rewardDict:
		#没有这个奖励
		return
	
	superInvestObj = role.GetObj(EnumObj.SuperInvestObj)
	if not superInvestObj:
		#没有投资过
		return
	
	investData = superInvestObj.get(investIndex)
	if not investData:
		#没有投资这个项目
		return
	
	if (2 not in investData) or (days in investData[2]):
		#领取过了
		return
	
	if (cDateTime.Days() - investData.get(1) + 1) < days:
		#领取奖励需要的时间不对
		return
	
	with SuperInvestReward_Log:
		tips = GlobalPrompt.Reward_Tips
		if rewardDict.get(1):
			#奖励物品
			investData[2].add(days)
			
			for item in rewardDict[1]:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % item
			
		elif rewardDict.get(2):
			#奖励体力
			investData[2].add(days)
			
			role.IncTiLi(rewardDict[2])
			tips += GlobalPrompt.TiLi_Tips % rewardDict[2]
			
		elif rewardDict.get(3):
			#奖励神石
			investData[2].add(days)
			
			role.IncBindRMB(rewardDict[3])
			tips += GlobalPrompt.BindRMB_Tips % rewardDict[3]
			
		else:
			return
		
		if len(investData[2]) >= 8:
			#奖励领取完了
			del superInvestObj[investIndex]
		role.SetObj(EnumObj.SuperInvestObj, superInvestObj)
		
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveSuperInvestReward, (investIndex, days))
		
	role.SendObj(SuperInvestData, superInvestObj)
	
	role.Msg(2, 0, tips)
	
def SyncRoleOtherData(role, param):
	role.SendObj(SuperInvestData, role.GetObj(EnumObj.SuperInvestObj))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (not Environment.IsCross):
		Event.RegEvent(Event.Eve_StartCircularActive, OpenSuperInvest)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseSuperInvest)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SuperInvest_Invest", "请求超级投资投资"), RequestInvest)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SuperInvest_Reward", "请求超级投资领取奖励"), RequestReward)
	
	
