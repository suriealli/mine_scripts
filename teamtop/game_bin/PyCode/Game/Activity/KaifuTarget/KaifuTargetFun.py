#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KaifuTarget.KaifuTargetFun")
#===============================================================================
# 7日目标的所有领取奖励的函数
#===============================================================================
import Environment
import cRoleMgr
import cDateTime
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.SysData import WorldData
from Game.Property import PropertyEnum
from Game.Role.Data import EnumObj, EnumInt16, EnumTempObj, EnumInt32
from Game.Activity.KaifuTarget import KaifuTargetConfig, TargetDefine,\
	KaifuTargetAccount

if "_HasLoad" not in dir():
	StartFlag = {1:False, 2:False, 3:False, 4:False, 5:False, 6:False, 7:False}
	
	#日志
	Tra_KaifuTarget_LevelTarget = AutoLog.AutoTransaction("Tra_KaifuTarget_LevelTarget", "7日目标活动冲级目标奖励")
	Tra_KaifuTarget_MountTarget = AutoLog.AutoTransaction("Tra_KaifuTarget_MountTarget", "7日目标活动坐骑目标奖励")
	Tra_KaifuTarget_GemTarget = AutoLog.AutoTransaction("Tra_KaifuTargetGemTarget", "7日目标活动宝石目标奖励")
	Tra_KaifuTarget_WedingRingTarget = AutoLog.AutoTransaction("Tra_KaifuTargetWedingRingTarget", "7日目标活动婚戒目标奖励")
	Tra_KaifuTarget_RoleZDLTarget = AutoLog.AutoTransaction("Tra_KaifuTarget_RoleZDLTarget", "7日目标活动主角战斗力目标奖励")
	Tra_KaifuTarget_HeroZDLTarget = AutoLog.AutoTransaction("Tra_KaifuTarget_HeroZDLTarget", "7日目标活动英雄战斗力目标奖励")
	Tra_KaifuTarget_TotalZDlTarget = AutoLog.AutoTransaction("Tra_KaifuTarget_TotalZDlTarget", "7日目标活动总战斗力目标奖励")
	KaifuTargetAccountRankData = AutoLog.AutoTransaction("KaifuTargetAccountRankData", "七日目标排行榜结算数据数据")
	
	KaifuTargetRewardData = AutoMessage.AllotMessage("KaifuTargetRewardData", "七日目标领取奖励数据")
	
#=====================================================================================================================
#排行榜奖励获取函数，函数参数为role和index
#中定义的活动类型枚举,index为配置表中配置的某个目标奖励的索引
#=====================================================================================================================
def RequestTargetReward_level(role, index):
	'''
	冲级达人
	@param role:
	@param index:冲级目标索引
	'''
	if not WorldData.WD.returnDB:
		return
	target_type = TargetDefine.Level
	configDict = KaifuTargetConfig.KaifuTargetConfig_Dict
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		target_type = TargetDefine.NewLevel
		configDict = KaifuTargetConfig.NewKaifuTargetConfig_Dict
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		target_type = TargetDefine.Level
		configDict = KaifuTargetConfig.KaifuTargetConfig_Dict
	
	global StartFlag
	if not StartFlag.get(target_type): return
	
	#已经领过该档奖励了
	reward_data = role.GetObj(EnumObj.KaifuTarget).setdefault(target_type, set())
	if index in reward_data:
		return
	
	config = configDict.get((target_type, index))
	if not config:
		return
	
	if role.GetLevel() < config.param:
		return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	unbindrmb_s = config.unbindRMB_S
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	unbind_RMB_S_tips = GlobalPrompt.UnBindRMB_Tips
	
	with Tra_KaifuTarget_LevelTarget:
		reward_data.add(index)
		
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
		
		if unbindrmb_s:
			role.IncUnbindRMB_S(unbindrmb_s)
			tips += unbind_RMB_S_tips % unbindrmb_s
	
	role.SendObj(KaifuTargetRewardData, role.GetObj(EnumObj.KaifuTarget))
	
	role.Msg(2, 0, tips)

def RequestTargetReward_gem(role, index):
	'''
	宝石达人
	@param role:
	@param index:冲级目标索引
	'''
	if not WorldData.WD.returnDB:
		return
	target_type = TargetDefine.Gem
	configDict = KaifuTargetConfig.KaifuTargetConfig_Dict
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		target_type = TargetDefine.NewGem
		configDict = KaifuTargetConfig.NewKaifuTargetConfig_Dict
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		target_type = TargetDefine.Gem
		configDict = KaifuTargetConfig.KaifuTargetConfig_Dict
		
	global StartFlag
	if not StartFlag.get(target_type): return
	
	#已经领过该档奖励了
	reward_data = role.GetObj(EnumObj.KaifuTarget).setdefault(target_type, set())
	if index in reward_data:
		return
	
	config = configDict.get((target_type, index))
	if not config:
		return
	
	if role.GetTotalGemLevel() < config.param:
		return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	unbindrmb_s = config.unbindRMB_S
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	unbind_RMB_S_tips = GlobalPrompt.UnBindRMB_Tips	
	
	with Tra_KaifuTarget_GemTarget:
		reward_data.add(index)
		
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

		if unbindrmb_s:
			role.IncUnbindRMB_S(unbindrmb_s)
			tips += unbind_RMB_S_tips % unbindrmb_s	
			
	role.SendObj(KaifuTargetRewardData, role.GetObj(EnumObj.KaifuTarget))
	
	role.Msg(2, 0, tips)

def RequestTargetReward_mount(role, index):
	'''
	坐骑活动
	@param role:
	@param index:冲级目标索引
	'''
	if not WorldData.WD.returnDB:
		return
	target_type = TargetDefine.Mount
	configDict = KaifuTargetConfig.KaifuTargetConfig_Dict
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		target_type = TargetDefine.NewMount
		configDict = KaifuTargetConfig.NewKaifuTargetConfig_Dict
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		target_type = TargetDefine.Mount
		configDict = KaifuTargetConfig.KaifuTargetConfig_Dict
		
	global StartFlag
	if not StartFlag.get(target_type): return
	
	reward_data = role.GetObj(EnumObj.KaifuTarget).setdefault(target_type, set())
	if index in reward_data:
		return
	
	config = configDict.get((target_type, index))
	if not config:
		return
	
	if role.GetI16(EnumInt16.MountEvolveID) < config.param:
		return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	unbindrmb_s = config.unbindRMB_S
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	unbind_RMB_S_tips = GlobalPrompt.UnBindRMB_Tips
	
	with Tra_KaifuTarget_MountTarget:
		reward_data.add(index)
		
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

		if unbindrmb_s:
			role.IncUnbindRMB_S(unbindrmb_s)
			tips += unbind_RMB_S_tips % unbindrmb_s
				
	role.SendObj(KaifuTargetRewardData, role.GetObj(EnumObj.KaifuTarget))
	
	role.Msg(2, 0, tips)


def RequestTargetReward_ring(role, index):
	'''
	婚戒活动
	@param role:
	@param index:冲级目标索引
	'''
	target_type = TargetDefine.WedingRing
	
	global StartFlag
	if not StartFlag.get(target_type): return
	
	#已经领过该档奖励了
	reward_data = role.GetObj(EnumObj.KaifuTarget).setdefault(target_type, set())
	if index in reward_data:
		return
	
	config = KaifuTargetConfig.KaifuTargetConfig_Dict.get((target_type, index))
	if not config:
		return
	
	if role.GetI16(EnumInt16.WeddingRingID) < config.param:
		return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	unbindrmb_s = config.unbindRMB_S
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	unbind_RMB_S_tips = GlobalPrompt.UnBindRMB_Tips
		
	with Tra_KaifuTarget_WedingRingTarget:
		reward_data.add(index)
		
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

		if unbindrmb_s:
			role.IncUnbindRMB_S(unbindrmb_s)
			tips += unbind_RMB_S_tips % unbindrmb_s	
			
	role.SendObj(KaifuTargetRewardData, role.GetObj(EnumObj.KaifuTarget))
	
	role.Msg(2, 0, tips)

def RequestTargetReward_rolezdl(role, index):
	'''
	主角战斗力活动
	@param role:
	@param index:冲级目标索引
	'''
	target_type = TargetDefine.RoleZDL
	
	global StartFlag
	if not StartFlag.get(target_type): return
	
	#已经领过该档奖励了
	reward_data = role.GetObj(EnumObj.KaifuTarget).setdefault(target_type, set())
	if index in reward_data:
		return
	
	config = KaifuTargetConfig.KaifuTargetConfig_Dict.get((target_type, index))
	if not config:
		return
	
	#获取主角战斗力
	roleZDL = role.GetPropertyGather().total_p_m.p_dict.get(PropertyEnum.zdl, 0)
	if roleZDL < config.param:
		return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	unbindrmb_s = config.unbindRMB_S
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	unbind_RMB_S_tips = GlobalPrompt.UnBindRMB_Tips
	
	with Tra_KaifuTarget_RoleZDLTarget:
		reward_data.add(index)
		
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
			
		if unbindrmb_s:
			role.IncUnbindRMB_S(unbindrmb_s)
			tips += unbind_RMB_S_tips % unbindrmb_s
				
	role.SendObj(KaifuTargetRewardData, role.GetObj(EnumObj.KaifuTarget))
	
	role.Msg(2, 0, tips)

def RequestTargetReward_herozdl(role, index):
	'''
	英雄战斗力活动
	@param role:
	@param index:冲级目标索引
	'''
	target_type = TargetDefine.HeroZDL
	
	global StartFlag
	if not StartFlag.get(target_type): return
	
	#已经领过该档奖励了
	reward_data = role.GetObj(EnumObj.KaifuTarget).setdefault(target_type, set())
	if index in reward_data:
		return
	
	config = KaifuTargetConfig.KaifuTargetConfig_Dict.get((target_type, index))
	if not config:
		return
	
	heroZDLlist = []
	roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	for hero in roleHeroMgr.HeroDict.itervalues():
		if hero.GetStationID() > 0:
			#只有上阵的才算战斗力
			hero_zdl = hero.GetPropertyGather().total_p_m.p_dict.get(PropertyEnum.zdl, 0)
			heroZDLlist.append(hero_zdl)
	max_herozdl = max(heroZDLlist)
	
	if max_herozdl < config.param:
		return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	unbindrmb_s = config.unbindRMB_S
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	unbind_RMB_S_tips = GlobalPrompt.UnBindRMB_Tips
	
	with Tra_KaifuTarget_HeroZDLTarget:
		reward_data.add(index)
		
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

		if unbindrmb_s:
			role.IncUnbindRMB_S(unbindrmb_s)
			tips += unbind_RMB_S_tips % unbindrmb_s
	role.SendObj(KaifuTargetRewardData, role.GetObj(EnumObj.KaifuTarget))
	
	role.Msg(2, 0, tips)

def RequestTargetReward_zdl(role, index):
	'''
	总战斗力活动
	@param role:
	@param index:冲级目标索引
	'''
	if not WorldData.WD.returnDB:
		return
	target_type = TargetDefine.TotalZDl
	configDict = KaifuTargetConfig.KaifuTargetConfig_Dict
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		target_type = TargetDefine.NewTotalZDl
		configDict = KaifuTargetConfig.NewKaifuTargetConfig_Dict
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		target_type = TargetDefine.TotalZDl
		configDict = KaifuTargetConfig.KaifuTargetConfig_Dict
		
	global StartFlag
	if not StartFlag.get(target_type): return
	
	#已经领过该档奖励了
	reward_data = role.GetObj(EnumObj.KaifuTarget).setdefault(target_type, set())
	if index in reward_data:
		return
	
	config = configDict.get((target_type, index))
	if not config:
		return
	
	if role.GetZDL() < config.param:
		return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	unbindrmb_s = config.unbindRMB_S
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	unbind_RMB_S_tips = GlobalPrompt.UnBindRMB_Tips
	
	with Tra_KaifuTarget_TotalZDlTarget:
		reward_data.add(index)
		
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

		if unbindrmb_s:
			role.IncUnbindRMB_S(unbindrmb_s)
			tips += unbind_RMB_S_tips % unbindrmb_s
	role.SendObj(KaifuTargetRewardData, role.GetObj(EnumObj.KaifuTarget))
	
	role.Msg(2, 0, tips)

def RequestTargetReward_Consume(role, index):
	'''
	消费达人
	@param role:
	@param index:
	'''
	target_type = TargetDefine.NewConsume
	
	global StartFlag
	if not StartFlag.get(target_type): return
	
	#已经领过该档奖励了
	reward_data = role.GetObj(EnumObj.KaifuTarget).setdefault(target_type, set())
	if index in reward_data:
		return
	
	config = KaifuTargetConfig.NewKaifuTargetConfig_Dict.get((target_type, index))
	if not config:
		return
	
	if role.GetI32(EnumInt32.KaifuTargetConsume) < config.param:
		return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	unbindrmb_s = config.unbindRMB_S
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	unbind_RMB_S_tips = GlobalPrompt.UnBindRMB_Tips
	
	with Tra_KaifuTarget_TotalZDlTarget:
		reward_data.add(index)
		
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

		if unbindrmb_s:
			role.IncUnbindRMB_S(unbindrmb_s)
			tips += unbind_RMB_S_tips % unbindrmb_s
	role.SendObj(KaifuTargetRewardData, role.GetObj(EnumObj.KaifuTarget))
	
	role.Msg(2, 0, tips)
	
def RequestTargetReward_Charge(role, index):
	'''
	充值达人
	@param role:
	@param index:
	'''
	target_type = TargetDefine.NewCharge
	
	global StartFlag
	if not StartFlag.get(target_type): return
	
	#已经领过该档奖励了
	reward_data = role.GetObj(EnumObj.KaifuTarget).setdefault(target_type, set())
	if index in reward_data:
		return
	
	config = KaifuTargetConfig.NewKaifuTargetConfig_Dict.get((target_type, index))
	if not config:
		return
	
	if role.GetI32(EnumInt32.KaifuTargetBuyRMB) < config.param:
		return
	
	itemlist = config.item
	tarotlist = config.tarot
	bindrmb = config.bindRMB
	unbindrmb_s = config.unbindRMB_S
	
	tips = GlobalPrompt.Reward_Tips
	item_tips = GlobalPrompt.Item_Tips
	tarot_tips = GlobalPrompt.Tarot_Tips
	bind_RMB_tips = GlobalPrompt.BindRMB_Tips
	unbind_RMB_S_tips = GlobalPrompt.UnBindRMB_Tips
	
	with Tra_KaifuTarget_TotalZDlTarget:
		reward_data.add(index)
		
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

		if unbindrmb_s:
			role.IncUnbindRMB_S(unbindrmb_s)
			tips += unbind_RMB_S_tips % unbindrmb_s
	role.SendObj(KaifuTargetRewardData, role.GetObj(EnumObj.KaifuTarget))
	
	role.Msg(2, 0, tips)
	
#=====================================================================================================================
#活动开关
#=====================================================================================================================
def StartKaifuTarget(param1, param2):
	global StartFlag
	if param2 not in StartFlag:
		print 'GE_EXC, StartKaifuTarget target type error' % param2
		return
	if StartFlag[param2]:
		print 'GE_EXC, StartKaifuTarget target type %s is already true' % param2
	StartFlag[param2] = True
	
def EndKaifuTarget(param1, param2):
	global StartFlag
	if param2 not in StartFlag:
		print 'GE_EXC, StartKaifuTarget target type error' % param2
		return
	if not StartFlag[param2]:
		print 'GE_EXC, StartKaifuTarget target type %s is already false' % param2
	StartFlag[param2] = False
	
	from Game.Activity.KaifuTarget import TimeControl
	
	if param2 in TimeControl.KaifuTarget_Dict['accountSet']:
		print 'GE_EXC, KaifuTarget type %s is alread account' % param2
		return
	
	#结算排行榜数据
	accountFun = KaifuTargetAccount.AccountFunDict.get(param2)
	if not accountFun:
		#没有排行榜结算函数
		return
	rankData, firstName = accountFun()
	if not rankData:
		print 'GE_EXC, EndKaifuTarget account empty rank by %s day' % param2
	
	with KaifuTargetAccountRankData:
		TimeControl.KaifuTarget_Dict[param2] = rankData
		TimeControl.KaifuTarget_Dict['accountSet'].add(param2)
		TimeControl.KaifuTarget_Dict.changeFlag = True
		
		#天数, 排行榜
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveKaifuTargetRank, (param2, rankData))
	
	isNew = False
	cfg = TimeControl.KaifuTargetActiveConfig_Dict.get(param2)
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		isNew = True
		cfg = TimeControl.NewKaifuTargetActiveConfig_Dict.get(param2)
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		isNew = False
		cfg = TimeControl.KaifuTargetActiveConfig_Dict.get(param2)
	
	if not cfg:
		print 'GE_EXC, EndKaifuTarget can not find %s cfg in KaifuTargetActiveConfig_Dict' % param2
		return
	if firstName:
		if isNew:
			if param2 == 1:
				cRoleMgr.Msg(1, 0, GlobalPrompt.KaifuTarget_EndTips_2 % firstName)
			elif param2 == 4:
				cRoleMgr.Msg(1, 0, GlobalPrompt.KaifuTarget_EndTips_3 % firstName)
		else:
			cRoleMgr.Msg(1, 0, GlobalPrompt.KaifuTarget_EndTips % (cfg.targetRankName, firstName))
	else:
		print 'GE_EXC, EndKaifuTarget account empty rank %s' % param2
	
def SyncRoleOtherData(role, param):
	#上线同步领取目标奖励数据
	if not WorldData.WD.returnDB:
		return
	
	if (cDateTime.Now() - WorldData.WD[1]).days > 7:
		return
	
	from Game.Activity.KaifuTarget import TimeControl
	if Environment.EnvIsQQ() or Environment.IsDevelop or Environment.EnvIsPL():
		if WorldData.WD[1] > TimeControl.KaifuTargetTime_New:
			return
	else:
		if WorldData.WD[1] < TimeControl.KaifuTargetTime:
			return
	
	role.SendObj(KaifuTargetRewardData, role.GetObj(EnumObj.KaifuTarget))
	
	
def AfterChangeDayBuyUnbindRMB_Q(role, param):
	#七日目标累计充值
	global StartFlag
	if not StartFlag.get(TargetDefine.NewCharge): return
	
	oldValue, newValue = param
	if newValue <= oldValue:
		return
	
	role.IncI32(EnumInt32.KaifuTargetBuyRMB, newValue - oldValue)

def AfterChangeDayConsumeUnbindRMB(role, param):
	#七日目标累计消费
	global StartFlag
	if not StartFlag.get(TargetDefine.NewConsume): return
	
	newValue, oldValue = param
	if newValue >= oldValue:
		return
	
	role.IncI32(EnumInt32.KaifuTargetConsume, oldValue - newValue)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartKaifuTarget, StartKaifuTarget)
		Event.RegEvent(Event.Eve_EndKaifuTarget, EndKaifuTarget)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, AfterChangeDayBuyUnbindRMB_Q)
		Event.RegEvent(Event.Eve_AfterChangeDayConsumeUnbindRMB, AfterChangeDayConsumeUnbindRMB)
		
		
