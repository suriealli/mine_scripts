#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KaifuTarget.KaifuRankFun")
#===============================================================================
# 7日目标排行奖励的模块 
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Role import Event
from Game.SysData import WorldData
from Game.Activity.KaifuTarget import TargetDefine, KaifuTargetConfig

if "_HasLoad" not in dir():
	Tra_KaifuTarget_LevelRank = AutoLog.AutoTransaction("Tra_KaifuTarget_LevelRank", "7日目标活动冲级排名奖励")
	Tra_KaifuTarget_MountRank = AutoLog.AutoTransaction("Tra_KaifuTarget_MountRank", "7日目标活动坐骑排名奖励")
	Tra_KaifuTarget_GemRank = AutoLog.AutoTransaction("Tra_KaifuTarget_GemRank", "7日目标活动宝石排名奖励")
	Tra_KaifuTarget_WedingRingRank = AutoLog.AutoTransaction("Tra_KaifuTarget_WedingRingRank", "7日目标活动婚戒排名奖励")
	Tra_KaifuTarget_RoleZDLRank = AutoLog.AutoTransaction("Tra_KaifuTarget_RoleZDLRank", "7日目标活动主角战斗力排名奖励")
	Tra_KaifuTarget_HeroZDLRank = AutoLog.AutoTransaction("Tra_KaifuTarget_HeroZDLRank", "7日目标活动英雄战斗力排名奖励")
	Tra_KaifuTarget_TotalZDLRank = AutoLog.AutoTransaction("Tra_KaifuTarget_TotalZDLRank", "7日目标活动总战斗力排名奖励")
	
	KaifuTargetRankData = AutoMessage.AllotMessage("KaifuTargetRankData", "七日目标排行榜数据")
	
	Tra_KaifuTarget_RankLogDict = {}
#=====================================================================================================================
#排行榜奖励获取函数，函数唯一参数为role
#中定义的活动类型枚举
#=====================================================================================================================
def RequestRankReward_level(role, param):
	'''
	冲级达人
	'''
	from Game.Activity.KaifuTarget import TimeControl
	if not TimeControl.KaifuTarget_Dict.returnDB:
		return
	if not WorldData.WD.returnDB:
		return
	
	target_type = TargetDefine.Level
	configDict = KaifuTargetConfig.KaifuTargetRank_Dict
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		target_type = TargetDefine.NewLevel
		configDict = KaifuTargetConfig.NewKaifuTargetRank_Dict
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		target_type = TargetDefine.Level
		configDict = KaifuTargetConfig.KaifuTargetRank_Dict
	
	rankDict = TimeControl.KaifuTarget_Dict.get(target_type, None)
	if rankDict == None:
		return
	#角色不在排行榜里面
	role_id = role.GetRoleID()
	
	data = rankDict.get(role_id)
	if not data:
		return
	roledata = data.get(param)
	if not roledata:
		return
	
	role_rank, has_got, _ = roledata
	#已经领取过了 
	if has_got == 1:
		return
	config = configDict.get((target_type, role_rank), None)
	if not config:
		print "GE_EXC, error while config = KaifuTargetConfig.KaifuTargetRank_Dict.get((target_type, role_rank), None)(%s,%s)" % (target_type, role_rank)
		return
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	money = config.money
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	money_tips = GlobalPrompt.Money_Tips
	
	with Tra_KaifuTarget_LevelRank:
		roledata[1] = 1
		TimeControl.KaifuTarget_Dict.HasChange()
		
		if itemlist:
			for coding, cnt in itemlist:
				if cnt:
					role.AddItem(coding, cnt)
					tips += item_tips % (coding, cnt)
		if tarotlist:
			for coding, cnt in tarotlist:
				if cnt:
					role.AddTarotCard(coding, cnt)
					tips += tarot_tips % (coding, cnt)
		if bindrmb:
			role.IncBindRMB(bindrmb)
			tips += bind_RMB_tips % bindrmb
			
		if money:
			role.IncMoney(money)
			tips += money_tips % money
		
	role.SendObj(KaifuTargetRankData, TimeControl.KaifuTarget_Dict.data)
	
	role.Msg(2, 0, tips)

def RequestRankReward_gem(role, param):
	'''
	宝石达人
	'''
	from Game.Activity.KaifuTarget import TimeControl
	if not TimeControl.KaifuTarget_Dict.returnDB:
		return
	
	target_type = TargetDefine.Gem
	configDict = KaifuTargetConfig.KaifuTargetRank_Dict
		
	rankDict = TimeControl.KaifuTarget_Dict.get(TargetDefine.Gem, None)
	if rankDict == None:
		return
	#角色不在排行榜里面
	role_id = role.GetRoleID()
	
	data = rankDict.get(role_id)
	if not data:
		return
	roledata = data.get(param)
	if not roledata:
		return
	
	role_rank, has_got, _ = roledata
	#已经领取过了 
	if has_got == 1:
		return
	config = configDict.get((target_type, role_rank), None)
	if not config:
		print "GE_EXC, error while config = KaifuTargetConfig.KaifuTargetRank_Dict.get((target_type, role_rank), None)(%s,%s)" % (target_type, role_rank)
		return
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	money = config.money

	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	money_tips = GlobalPrompt.Money_Tips
	
	with Tra_KaifuTarget_GemRank:
		roledata[1] = 1
		TimeControl.KaifuTarget_Dict.HasChange()
		if itemlist:
			for coding, cnt in itemlist:
				if cnt:
					role.AddItem(coding, cnt)
					tips += item_tips % (coding, cnt)
		if tarotlist:
			for coding, cnt in tarotlist:
				if cnt:
					role.AddTarotCard(coding, cnt)
					tips += tarot_tips % (coding, cnt)
		if bindrmb:
			role.IncBindRMB(bindrmb)
			tips += bind_RMB_tips % bindrmb
			
		if money:
			role.IncMoney(money)
			tips += money_tips % money
	
	role.SendObj(KaifuTargetRankData, TimeControl.KaifuTarget_Dict.data)
	
	role.Msg(2, 0, tips)

def RequestRankReward_mount(role, param):
	'''
	坐骑达人
	'''
	from Game.Activity.KaifuTarget import TimeControl
	if not TimeControl.KaifuTarget_Dict.returnDB:
		return
	
	if not WorldData.WD.returnDB:
		return
	target_type = TargetDefine.Mount
	configDict = KaifuTargetConfig.KaifuTargetRank_Dict
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		target_type = TargetDefine.NewMount
		configDict = KaifuTargetConfig.NewKaifuTargetRank_Dict
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		target_type = TargetDefine.Mount
		configDict = KaifuTargetConfig.KaifuTargetRank_Dict
	
	rankDict = TimeControl.KaifuTarget_Dict.get(TargetDefine.Mount, None)
	if rankDict == None:
		return
	#角色不在排行榜里面
	role_id = role.GetRoleID()
	
	data = rankDict.get(role_id)
	if not data:
		return
	roledata = data.get(param)
	if not roledata:
		return
	
	role_rank, has_got, _ = roledata
	#已经领取过了 
	if has_got == 1:
		return
	config = configDict.get((target_type, role_rank), None)
	if not config:
		print "GE_EXC, error while config = KaifuTargetConfig.KaifuTargetRank_Dict.get((target_type, role_rank), None)(%s,%s)" % (target_type, role_rank)
		return
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	money = config.money
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	money_tips = GlobalPrompt.Money_Tips
	
	with Tra_KaifuTarget_MountRank:
		roledata[1] = 1
		TimeControl.KaifuTarget_Dict.HasChange()
		if itemlist:
			for coding, cnt in itemlist:
				if cnt:
					role.AddItem(coding, cnt)
					tips += item_tips % (coding, cnt)
		if tarotlist:
			for coding, cnt in tarotlist:
				if cnt:
					role.AddTarotCard(coding, cnt)
					tips += tarot_tips % (coding, cnt)
		if bindrmb:
			role.IncBindRMB(bindrmb)
			tips += bind_RMB_tips % bindrmb
			
		if money:
			role.IncMoney(money)
			tips += money_tips % money
	
	role.SendObj(KaifuTargetRankData, TimeControl.KaifuTarget_Dict.data)
	
	role.Msg(2, 0, tips)

def RequestRankReward_ring(role, param):
	'''
	婚戒活动
	'''
	from Game.Activity.KaifuTarget import TimeControl
	if not TimeControl.KaifuTarget_Dict.returnDB:
		return
	
	target_type = TargetDefine.WedingRing
	configDict = KaifuTargetConfig.KaifuTargetRank_Dict
	
	rankDict = TimeControl.KaifuTarget_Dict.get(TargetDefine.WedingRing, None)
	if rankDict == None:
		return
	#角色不在排行榜里面
	role_id = role.GetRoleID()
	
	data = rankDict.get(role_id)
	if not data:
		return
	roledata = data.get(param)
	if not roledata:
		return
	
	role_rank, has_got, _ = roledata
	#已经领取过了 
	if has_got == 1:
		return
	config = configDict.get((target_type, role_rank), None)
	if not config:
		print "GE_EXC, error while config = KaifuTargetConfig.KaifuTargetRank_Dict.get((target_type, role_rank), None)(%s,%s)" % (target_type, role_rank)
		return
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	money = config.money
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	money_tips = GlobalPrompt.Money_Tips
	
	with Tra_KaifuTarget_WedingRingRank:
		roledata[1] = 1
		TimeControl.KaifuTarget_Dict.HasChange()
		if itemlist:
			for coding, cnt in itemlist:
				if cnt:
					role.AddItem(coding, cnt)
					tips += item_tips % (coding, cnt)
		if tarotlist:
			for coding, cnt in tarotlist:
				if cnt:
					role.AddTarotCard(coding, cnt)
					tips += tarot_tips % (coding, cnt)
		if bindrmb:
			role.IncBindRMB(bindrmb)
			tips += bind_RMB_tips % bindrmb
			
		if money:
			role.IncMoney(money)
			tips += money_tips % money
	
	role.SendObj(KaifuTargetRankData, TimeControl.KaifuTarget_Dict.data)
	
	role.Msg(2, 0, tips)

def RequestRankReward_rolezdl(role, param):
	'''
	主角战斗力活动
	'''
	from Game.Activity.KaifuTarget import TimeControl
	if not TimeControl.KaifuTarget_Dict.returnDB:
		return
	
	target_type = TargetDefine.RoleZDL
	configDict = KaifuTargetConfig.KaifuTargetRank_Dict
	
	rankDict = TimeControl.KaifuTarget_Dict.get(TargetDefine.RoleZDL, None)
	if rankDict == None:
		return
	#角色不在排行榜里面
	role_id = role.GetRoleID()
	
	data = rankDict.get(role_id)
	if not data:
		return
	roledata = data.get(param)
	if not roledata:
		return
	
	role_rank, has_got, _ = roledata
	#已经领取过了 
	if has_got == 1:
		return
	config = configDict.get((target_type, role_rank), None)
	if not config:
		print "GE_EXC, error while config = KaifuTargetConfig.KaifuTargetRank_Dict.get((target_type, role_rank), None)(%s,%s)" % (target_type, role_rank)
		return
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	money = config.money
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	money_tips = GlobalPrompt.Money_Tips
	
	with Tra_KaifuTarget_RoleZDLRank:
		roledata[1] = 1
		TimeControl.KaifuTarget_Dict.HasChange()
		if itemlist:
			for coding, cnt in itemlist:
				if cnt:
					role.AddItem(coding, cnt)
					tips += item_tips % (coding, cnt)
		if tarotlist:
			for coding, cnt in tarotlist:
				if cnt:
					role.AddTarotCard(coding, cnt)
					tips += tarot_tips % (coding, cnt)
		if bindrmb:
			role.IncBindRMB(bindrmb)
			tips += bind_RMB_tips % bindrmb
			
		if money:
			role.IncMoney(money)
			tips += money_tips % money
	
	role.SendObj(KaifuTargetRankData, TimeControl.KaifuTarget_Dict.data)
	
	role.Msg(2, 0, tips)

def RequestRankReward_herozdl(role, param):
	'''
	英雄战斗力活动
	'''
	from Game.Activity.KaifuTarget import TimeControl
	if not TimeControl.KaifuTarget_Dict.returnDB:
		return
	
	target_type = TargetDefine.HeroZDL
	configDict = KaifuTargetConfig.KaifuTargetRank_Dict
	
	rankDict = TimeControl.KaifuTarget_Dict.get(TargetDefine.HeroZDL, None)
	if rankDict == None:
		return
	#角色不在排行榜里面
	role_id = role.GetRoleID()
	
	data = rankDict.get(role_id)
	if not data:
		return
	roledata = data.get(param)
	if not roledata:
		return
	
	role_rank, has_got, _ = roledata
	#已经领取过了 
	if has_got == 1:
		return
	config = configDict.get((target_type, role_rank), None)
	if not config:
		print "GE_EXC, error while config = KaifuTargetConfig.KaifuTargetRank_Dict.get((target_type, role_rank), None)(%s,%s)" % (target_type, role_rank)
		return
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	money = config.money
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	money_tips = GlobalPrompt.Money_Tips
	
	with Tra_KaifuTarget_HeroZDLRank:
		roledata[1] = 1
		TimeControl.KaifuTarget_Dict.HasChange()
		if itemlist:
			for coding, cnt in itemlist:
				if cnt:
					role.AddItem(coding, cnt)
					tips += item_tips % (coding, cnt)
		if tarotlist:
			for coding, cnt in tarotlist:
				if cnt:
					role.AddTarotCard(coding, cnt)
					tips += tarot_tips % (coding, cnt)
		if bindrmb:
			role.IncBindRMB(bindrmb)
			tips += bind_RMB_tips % bindrmb
			
		if money:
			role.IncMoney(money)
			tips += money_tips % money
	
	role.SendObj(KaifuTargetRankData, TimeControl.KaifuTarget_Dict.data)
	
	role.Msg(2, 0, tips)

def RequestRankReward_zdl(role, param):
	'''
	总战斗力活动
	'''
	from Game.Activity.KaifuTarget import TimeControl
	if not TimeControl.KaifuTarget_Dict.returnDB:
		return
	
	if not WorldData.WD.returnDB:
		return
	target_type = TargetDefine.TotalZDl
	configDict = KaifuTargetConfig.KaifuTargetRank_Dict
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		target_type = TargetDefine.NewTotalZDl
		configDict = KaifuTargetConfig.NewKaifuTargetRank_Dict
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		target_type = TargetDefine.TotalZDl
		configDict = KaifuTargetConfig.KaifuTargetRank_Dict
		
	rankDict = TimeControl.KaifuTarget_Dict.get(TargetDefine.TotalZDl, None)
	if rankDict == None:
		return
	#角色不在排行榜里面
	role_id = role.GetRoleID()
	
	data = rankDict.get(role_id)
	if not data:
		return
	roledata = data.get(param)
	if not roledata:
		return
	
	role_rank, has_got, _ = roledata
	#已经领取过了 
	if has_got == 1:
		return
	config = configDict.get((target_type, role_rank), None)
	if not config:
		print "GE_EXC, error while config = KaifuTargetConfig.KaifuTargetRank_Dict.get((target_type, role_rank), None)(%s,%s)" % (target_type, role_rank)
		return
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	money = config.money
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	money_tips = GlobalPrompt.Money_Tips
	
	with Tra_KaifuTarget_TotalZDLRank:
		roledata[1] = 1
		TimeControl.KaifuTarget_Dict.HasChange()
		if itemlist:
			for coding, cnt in itemlist:
				if cnt:
					role.AddItem(coding, cnt)
					tips += item_tips % (coding, cnt)
		if tarotlist:
			for coding, cnt in tarotlist:
				if cnt:
					role.AddTarotCard(coding, cnt)
					tips += tarot_tips % (coding, cnt)
		if bindrmb:
			role.IncBindRMB(bindrmb)
			tips += bind_RMB_tips % bindrmb
			
		if money:
			role.IncMoney(money)
			tips += money_tips % money
	
	role.SendObj(KaifuTargetRankData, TimeControl.KaifuTarget_Dict.data)
	
	role.Msg(2, 0, tips)
	
def SyncKaifuTargetRankData(role, param):
	#上线同步领取排行榜奖励数据
	from Game.Activity.KaifuTarget import TimeControl
	if not TimeControl.KaifuTarget_Dict.returnDB:
		return
	
	if not WorldData.WD.returnDB:
		return
	
	if (cDateTime.Now() - WorldData.WD[1]).days >= 7:
		return
	
	if Environment.EnvIsQQ() or Environment.IsDevelop or Environment.EnvIsPL():
		if WorldData.WD[1] > TimeControl.KaifuTargetTime_New:
			return
	else:
		if WorldData.WD[1] < TimeControl.KaifuTargetTime:
			return
	
	role.SendObj(KaifuTargetRankData, TimeControl.KaifuTarget_Dict.data)
	
	
def AfterLoadWorldData(param1, param2):
	LoadLogDict()
	
def LoadLogDict():
	global Tra_KaifuTarget_RankLogDict
	Tra_KaifuTarget_RankLogDict = {}
	Tra_KaifuTarget_RankLogDict[TargetDefine.Level] = Tra_KaifuTarget_LevelRank
	Tra_KaifuTarget_RankLogDict[TargetDefine.Mount] = Tra_KaifuTarget_MountRank
	Tra_KaifuTarget_RankLogDict[TargetDefine.Gem] = Tra_KaifuTarget_GemRank
	Tra_KaifuTarget_RankLogDict[TargetDefine.WedingRing] = Tra_KaifuTarget_WedingRingRank
	Tra_KaifuTarget_RankLogDict[TargetDefine.HeroZDL] = Tra_KaifuTarget_HeroZDLRank
	Tra_KaifuTarget_RankLogDict[TargetDefine.RoleZDL] = Tra_KaifuTarget_RoleZDLRank
	Tra_KaifuTarget_RankLogDict[TargetDefine.TotalZDl] = Tra_KaifuTarget_TotalZDLRank
		
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		Tra_KaifuTarget_RankLogDict = {}
		Tra_KaifuTarget_RankLogDict[TargetDefine.NewLevel] = Tra_KaifuTarget_LevelRank
		Tra_KaifuTarget_RankLogDict[TargetDefine.NewMount] = Tra_KaifuTarget_MountRank
		Tra_KaifuTarget_RankLogDict[TargetDefine.NewTotalZDl] = Tra_KaifuTarget_TotalZDLRank
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		Tra_KaifuTarget_RankLogDict = {}
		Tra_KaifuTarget_RankLogDict[TargetDefine.Level] = Tra_KaifuTarget_LevelRank
		Tra_KaifuTarget_RankLogDict[TargetDefine.Mount] = Tra_KaifuTarget_MountRank
		Tra_KaifuTarget_RankLogDict[TargetDefine.Gem] = Tra_KaifuTarget_GemRank
		Tra_KaifuTarget_RankLogDict[TargetDefine.WedingRing] = Tra_KaifuTarget_WedingRingRank
		Tra_KaifuTarget_RankLogDict[TargetDefine.HeroZDL] = Tra_KaifuTarget_HeroZDLRank
		Tra_KaifuTarget_RankLogDict[TargetDefine.RoleZDL] = Tra_KaifuTarget_RoleZDLRank
		Tra_KaifuTarget_RankLogDict[TargetDefine.TotalZDl] = Tra_KaifuTarget_TotalZDLRank
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncKaifuTargetRankData)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenKaifuTargetPanel", "客户端请求打开七日目标面板"), SyncKaifuTargetRankData)
