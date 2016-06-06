#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.HallowsForing")
#===============================================================================
# 圣器洗练、继承、附魔
#===============================================================================
import random
import cRoleMgr
import Environment
from Util import Random
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Role.Data import EnumTempObj,EnumInt32
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role import Event

if "_HasLoad" not in dir():
	#圣器属性星阶随机
	HallowsProplevelRandom = Random.RandomRate()
	HallowsInitProplevelRandom = Random.RandomRate()
	HallowsProplevelDict = {}
	HallowsEnchantDict = {}
	HallowShenzaoDict = {}
	HallowsAct = [1, 2, 3, 4, 5]	#1为洗练 2为保存洗练 3 为继承 4为附魔5为神造
	HallowShenzaoStone = 27939
	OnkeyShenzaoMaxTime = 50
	
	#消息
	HallowsSyncData = AutoMessage.AllotMessage("HallowsSyncData", "同步圣器属性")
	#日志
	TraHallowsEnchant = AutoLog.AutoTransaction("TraHallowsEnchant", "圣器附魔")
	TraHallowsrefine = AutoLog.AutoTransaction("TraHallowsrefine", "圣器洗练")
	TraSaveHallowsrefine = AutoLog.AutoTransaction("TraSaveHallowsrefine", "保存圣器洗练属性")
	TraHallowsreheritance = AutoLog.AutoTransaction("TraHallowsreheritance", "圣器继承")
	TraHallowsShenzao = AutoLog.AutoTransaction("TraHallowsShenzao", "圣器神造")
	TraHallowsOnekeyShenzao = AutoLog.AutoTransaction("TraHallowsOnekeyShenzao", "圣器一键神造")

def OnHallowsEnchant(role, msg):
	'''
	圣器附魔
	@param role:
	@param msg:圣器ID
	'''
	hallowID = msg
	if not hallowID:
		
		return
	#等级限制
	if role.GetLevel() < EnumGameConfig.Hallows_EnchantNeedlevel:
		return
	#获取全局物品字典
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	hallowthing = globaldict.get(hallowID)
	#不是物品编码
	if not hallowthing:
		return

	#获取旧的附魔等级
	oldlevel = hallowthing.GetEnchantsLevel()
	newlevel = oldlevel + 1
	#如果附魔等级已经为最大值
	if oldlevel >= EnumGameConfig.Hallows_Max_EnchantsLevel:
		return

	#这里获取附魔配置########
	cfg = HallowsEnchantDict.get(newlevel)
	if not cfg:
		print "GE_EXC, error while get config for HallowsEnchant ,may not find level(%s)" % newlevel
		return
	#附魔石不够
	CostItemCode = cfg.CostItem
	Cost = cfg.Cost
	if role.ItemCnt(CostItemCode) < Cost:
		return
	with TraHallowsEnchant:
		if role.DelItem(CostItemCode, Cost) < Cost:
			return
		#设置附魔等级
		hallowthing.SetEnchantsLevel(newlevel)
		AutoLog.LogObj(role.GetRoleID(), AutoLog.eveHallowsEnchant, hallowID, hallowthing.otype, hallowthing.oint, hallowthing.odata, (oldlevel, newlevel))
		
	#如果圣器在角色或者英雄身上,则触发重算
	if hallowthing.owner:
		hallowthing.owner.GetPropertyGather().ReSetRecountHallowsFlag()
	#同步物品数据
	role.SendObj(HallowsSyncData, (HallowsAct[3], hallowID, hallowthing.odata))

def OnHallowsRefineBegin(role, msg):
	'''
	圣器洗练
	@param role:
	@param msg:圣器ID + 锁定属性列表
	'''
	if not msg:
		return
	hallowID, Originallocklist, is_use_RMB = msg
	
	if len(Originallocklist) != len(set(Originallocklist)):
		return
	#获取全局物品字典
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	hallowthing = globaldict.get(hallowID)
	if not hallowthing:
		return

	#圣器的位置一定在１和６之间
	postype = hallowthing.cfg.posType
	if not 1<= postype <= 6:
		return
	#一共需要花费的神石
	RMBprice = 0
	RefinelockCost = len(Originallocklist)
	RefinestoneCode = EnumGameConfig.Hallows_RefineStoneCode
	RefinestoneCost = EnumGameConfig.Hallows_RefineStoneCost
	RefineLockCode = EnumGameConfig.Hallows_RefineLockCode
	RefinestoneCode_Tmp = EnumGameConfig.Hallows_RefineStoneCode_Tmp
	RefineLockCode_Tmp = EnumGameConfig.Hallows_RefineLockCode_Tmp
	rolestonecnt = role.ItemCnt(RefinestoneCode) + role.ItemCnt_NotTimeOut(RefinestoneCode_Tmp)
	
	#如果可以使用神石代替道具
	if is_use_RMB:
		if rolestonecnt < RefinestoneCost:
			if Environment.EnvIsNA():
				RMBprice += (RefinestoneCost - rolestonecnt) * EnumGameConfig.Hallows_RefinePrice_NA
			else:
				RMBprice += (RefinestoneCost - rolestonecnt) * EnumGameConfig.Hallows_RefinePrice
			RefinestoneCost = rolestonecnt
		
		rolelockcnt = role.ItemCnt(RefineLockCode) + role.ItemCnt_NotTimeOut(RefineLockCode_Tmp)
		if rolelockcnt < RefinelockCost:
			if Environment.EnvIsNA():
				RMBprice += (RefinelockCost - rolelockcnt) * EnumGameConfig.Hallows_RefineLockPrice_NA
			else:
				RMBprice += (RefinelockCost - rolelockcnt) * EnumGameConfig.Hallows_RefineLockPrice
			RefinelockCost = rolelockcnt

		#判断神石是否足够
		if role.GetUnbindRMB() < RMBprice:
			return
		
	else:
		if role.ItemCnt(RefinestoneCode) + role.ItemCnt_NotTimeOut(RefinestoneCode_Tmp) < RefinestoneCost:
			return
		if role.ItemCnt(RefineLockCode) + role.ItemCnt_NotTimeOut(RefineLockCode_Tmp) < RefinelockCost:
			return
	
	#Originallocklist里全部都是字符，这里要做一次预处理
	locklist = []
	locklist_append = locklist.append
	if Originallocklist:
		for pt in Originallocklist:
			if not pt.startswith("buf"):
				locklist_append(int(pt))
			else:
				locklist_append(pt)
	#锁定属性字典(新属性字典)
	newpropdict = {}
	
	#锁定了不存在的属性
	if locklist:
		propdict = hallowthing.GetPropDict()
		if len(locklist) >= len(propdict):
			return
		propdictget = propdict.get
		for prop in locklist:
			if prop not in propdict:
				return
			newpropdict[prop] = propdictget(prop)
	
	newproprandom = Random.RandomRate()
	newproprandom_AddRandomItem = newproprandom.AddRandomItem
	for rate, prop in hallowthing.cfg.randomprop.randomList:
		if prop not in locklist:
			newproprandom_AddRandomItem(rate, prop)

	#随机生成的属性个数
	newpropcnt = hallowthing.cfg.inipropcnt - len(locklist)
	newproplist = newproprandom.RandomMany(newpropcnt)
	HallowsProplevelRandomRandomOne = HallowsProplevelRandom.RandomOne
	GET = HallowsProplevelDict.get
	RDI =  random.randint
	for prop in newproplist:
		new_prop_level = HallowsProplevelRandomRandomOne()
		percent_tuple = GET(new_prop_level)
		#最大值
		ptm = hallowthing.cfg.ptmax.get(prop)
		newpropdict[prop] = min(RDI(*percent_tuple), ptm)

	
	with TraHallowsrefine:
		# 如果可以使用神石代替道具且确实有神石需要扣除的话
		if RMBprice and is_use_RMB:
			role.DecUnbindRMB(RMBprice)
		if RefinestoneCost:
			#删除临时圣器洗练石（已经做好扩展适应每次洗练石不同的情况）
			if role.ItemCnt_NotTimeOut(RefinestoneCode_Tmp) >= RefinestoneCost:
				role.DelItem(RefinestoneCode_Tmp, RefinestoneCost)
				RefinestoneCost =0
			elif role.ItemCnt_NotTimeOut(RefinestoneCode_Tmp) and role.ItemCnt_NotTimeOut(RefinestoneCode_Tmp) < RefinestoneCost :
				Tmpcnt = role.ItemCnt(RefinestoneCode_Tmp)
				role.DelItem(RefinestoneCode_Tmp, Tmpcnt)
				RefinestoneCost -= Tmpcnt
			if RefinestoneCost :
				role.DelItem(RefinestoneCode, RefinestoneCost)
		if RefinelockCost:
			#删除临时圣器洗练锁(已经做好扩展适应每次洗练锁不同的情况)
			if role.ItemCnt_NotTimeOut(RefineLockCode_Tmp) >= RefinelockCost:
				role.DelItem(RefineLockCode_Tmp, RefinelockCost)
				RefinelockCost = 0
			elif role.ItemCnt_NotTimeOut(RefineLockCode_Tmp) and role.ItemCnt_NotTimeOut(RefineLockCode_Tmp) < RefinelockCost :
				Tmpcnt = role.ItemCnt_NotTimeOut(RefineLockCode_Tmp)
				role.DelItem(RefineLockCode_Tmp, Tmpcnt)
				RefinelockCost -= Tmpcnt
			if RefinelockCost :
				role.DelItem(RefineLockCode, RefinelockCost)
		#设置临时新属性
		hallowthing.SetPropRefineDict(newpropdict)
	
	#同步物品数据
	role.SendObj(HallowsSyncData, (HallowsAct[0], hallowID, hallowthing.odata))
	#圣器洗练日
	role.IncI32(EnumInt32.Hallows_Latest_Times, 1)
	from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
	LatestActivityMgr.GetFunByType(EnumLatestType.Hallows_Latest, (role, 1))
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_HallowsForing, 1))
	
def OnHallowsrefineSave(role, msg):
	'''
	保存洗练的属性
	@param role:
	@param msg:
	'''
	if not msg:
		return
	hallowID = msg
	#获取全局物品字典
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	hallowthing = globaldict.get(hallowID)
	if not hallowthing:
		return

	newpropdict = hallowthing.GetPropRefineDict()
	#如果没有洗练过
	if not newpropdict:
		return

	#保存属性, 清空未保存属性
	with TraSaveHallowsrefine:
		hallowthing.ResetPropRefineDict()
		hallowthing.SetPropDict(newpropdict)
		AutoLog.LogObj(role.GetRoleID(), AutoLog.evehallowsRefineSave, hallowID, hallowthing.otype, hallowthing.oint, hallowthing.odata, None)
		
	#如果圣器在角色或者英雄身上,则触发重算
	if hallowthing.owner:
		hallowthing.owner.GetPropertyGather().ReSetRecountHallowsFlag()
	#同步物品数据
	role.SendObj(HallowsSyncData, (HallowsAct[1], hallowID, hallowthing.odata))

def OnHallowInheritance(role, msg):
	'''
	圣器属性继承
	@param role:
	@param msg:高阶圣器id，低阶圣器id
	'''
	l_hallowthingID, h_hallowthingID = msg
	if not l_hallowthingID or not l_hallowthingID:
		return
	#获取全局物品字典
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	l_hallowthing = globaldict.get(l_hallowthingID)
	h_hallowthing = globaldict.get(h_hallowthingID)
	if not l_hallowthing or not h_hallowthing:
		return
	#物品必须是在背包中,而不是在主角或者英雄身上
	if l_hallowthing.owner is not None:
		return
	if h_hallowthing.owner is not None:
		return
	if l_hallowthing.cfg.posType != h_hallowthing.cfg.posType:
		return
	#低品阶是否有雕纹
	if l_hallowthing.GetHallowsGem():
		return
	#高品阶继承低品阶
	l_inipropcnt = l_hallowthing.cfg.inipropcnt
	h_inipropcnt = h_hallowthing.cfg.inipropcnt
	if l_inipropcnt >= h_inipropcnt:
		return
	#获取低阶圣器属性字典
	l_propdict = l_hallowthing.GetPropDict()
	#获取低阶圣器附魔等级
	l_EnchantsLevel = l_hallowthing.GetEnchantsLevel()
	#获取高阶和低阶圣器的神造等级和神造经验
	h_ShenzaoLevel, h_ShenzaoExp = h_hallowthing.GetShenzaoLevelAndExp()
	l_ShenzaoLevel, l_ShenzaoExp = l_hallowthing.GetShenzaoLevelAndExp()
	
	#获取高阶圣器需要随机生成的属性个数
	h_newpropcnt = h_inipropcnt - l_inipropcnt
	h_newpropdict = {}
	h_newproprandom = Random.RandomRate()
	l_propdict_iterkeys = l_propdict.iterkeys
	for rate, prop in h_hallowthing.cfg.randomprop.randomList:
		if prop not in l_propdict_iterkeys():
			h_newproprandom.AddRandomItem(rate, prop)
	#新属性列表
	h_newproplist = h_newproprandom.RandomMany(h_newpropcnt)
	
	#消点优化
	GET = HallowsProplevelDict.get
	RDI =  random.randint
	HallowsProplevelRandomRandomOne = HallowsProplevelRandom.RandomOne
	for prop in h_newproplist:
		new_prop_level = HallowsProplevelRandomRandomOne()
		percent_tuple = GET(new_prop_level)
		#最大值
		h_ptm = h_hallowthing.cfg.ptmax.get(prop)
		h_newpropdict[prop] = min(RDI(*percent_tuple), h_ptm)
	h_newpropdict.update(l_propdict)
	#删除低阶属性物品
	with TraHallowsreheritance:
		if not role.DelProp(l_hallowthingID):
			print "GE_EXC, DelProp error in OnHallowInheritance"
			return
		#高阶圣器设置新属性
		h_hallowthing.SetPropDict(h_newpropdict)
		h_hallowthing.SetEnchantsLevel(l_EnchantsLevel)
		#神造等级继承
		if l_ShenzaoLevel > h_ShenzaoLevel:
			h_hallowthing.SetShenzaoLevelAndExp(l_ShenzaoLevel, l_ShenzaoExp)
		elif l_ShenzaoLevel == h_ShenzaoLevel:
			if l_ShenzaoExp > h_ShenzaoExp:
				h_hallowthing.SetShenzaoLevelAndExp(l_ShenzaoLevel, l_ShenzaoExp)
		
		AutoLog.LogObj(role.GetRoleID(), AutoLog.eveHallowsInheritance, h_hallowthingID, h_hallowthing.otype, h_hallowthing.oint, h_hallowthing.odata, l_hallowthingID)
		
	role.SendObj(HallowsSyncData, (HallowsAct[2], h_hallowthingID, h_hallowthing.odata))
	role.Msg(2, 0, GlobalPrompt.Hallows_InheritanceSuccessfully)


def OnHallowShenzao(role, msg):
	'''
	神造
	@param role:
	@param msg:圣器的物品id
	'''
	if role.GetLevel() < EnumGameConfig.Hallows_ShenzaoNeedlevel:
		return
	
	hallowID = msg
	
	if role.ItemCnt(HallowShenzaoStone) < 1:
		return
	#获取全局物品字典
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	hallowthing = globaldict.get(hallowID)
	if not hallowthing:
		return
	
	#获取旧的等级和经验值
	oldLevel, oldExp = hallowthing.GetShenzaoLevelAndExp()
	maxLevel = hallowthing.cfg.maxShenzaoLevel
	#旧的等级已经是最高等级
	if oldLevel >= maxLevel:
		return
	
	#获取配置
	config = HallowShenzaoDict.get(oldLevel)
	if not config:
		print "GE_EXC, error while HallowShenzaoDict.get(oldLevel),(roleID = %s,oldLevel = %s)" \
			% (oldLevel, role.GetRoleID())
		return
	
	newExp = oldExp + 1
	newLevel = oldLevel
	
	if newExp >= config.needExp:
		newLevel += 1
		newExp = 0
	
	#这里要增加日志
	with TraHallowsShenzao:
		if role.DelItem(HallowShenzaoStone, 1) < 1:
			return
		hallowthing.SetShenzaoLevelAndExp(newLevel, newExp)
		AutoLog.LogObj(role.GetRoleID(), AutoLog.eveHallowsShenzao, hallowID, hallowthing.otype, hallowthing.oint, hallowthing.odata,
					((oldLevel, oldExp), (newLevel, newExp)))
	
	#如果圣器在角色或者英雄身上,则触发重算
	if hallowthing.owner:
		hallowthing.owner.GetPropertyGather().ReSetRecountHallowsShenzaoFlag()
	
	role.Msg(2, 0, GlobalPrompt.Hallows_ShenzaoOkay)
	
	#同步物品数据
	role.SendObj(HallowsSyncData, (HallowsAct[4], hallowID, hallowthing.odata))
	
	
def OnHallowOneKeyShenzao(role, msg):
	'''
	一键神造
	@param role:
	@param msg:圣器的物品id
	'''
	if role.GetLevel() < EnumGameConfig.Hallows_ShenzaoNeedlevel:
		return
	
	hallowID = msg
	#获取全局物品字典
	globaldict = role.GetTempObj(EnumTempObj.enGlobalItemMgr)
	hallowthing = globaldict.get(hallowID)
	if not hallowthing:
		return
	
	#获取旧的等级和经验值
	oldLevel, oldExp = hallowthing.GetShenzaoLevelAndExp()
	
	maxLevel = hallowthing.cfg.maxShenzaoLevel
	#旧的等级已经是最高等级
	if oldLevel >= maxLevel:
		return
	
	#角色身上物品允许角色神造的次数
	if role.ItemCnt(HallowShenzaoStone) < OnkeyShenzaoMaxTime:
		return
	
	newLevel = oldLevel
	newExp = oldExp
	#实际的次数
	infactTimes = 0
	
	while newLevel < maxLevel and infactTimes < OnkeyShenzaoMaxTime:
		config = HallowShenzaoDict.get(newLevel)
		if config is None:
			print "GE_EXC, error while HallowShenzaoDict.get(newLevel),(roleID = %s,newLevel = %s)" \
			% (newLevel, role.GetRoleID())
			return
		
		leftTimes = OnkeyShenzaoMaxTime - infactTimes
		if newExp + leftTimes >= config.needExp:
			infactTimes += config.needExp - newExp
			newExp = 0
			newLevel += 1
		else:
			infactTimes += leftTimes
			newExp += leftTimes
			break
	
	if infactTimes <= 0:
		return
	
	#这里要增加日志
	with TraHallowsOnekeyShenzao:
		if role.DelItem(HallowShenzaoStone, infactTimes) < infactTimes:
			return
		hallowthing.SetShenzaoLevelAndExp(newLevel, newExp)
		AutoLog.LogObj(role.GetRoleID(), AutoLog.eveHallowsShenzao, hallowID, hallowthing.otype, hallowthing.oint, hallowthing.odata,
					((oldLevel, oldExp), (newLevel, newExp)))
		
	#如果圣器在角色或者英雄身上,则触发重算
	if hallowthing.owner:
		hallowthing.owner.GetPropertyGather().ReSetRecountHallowsShenzaoFlag()
	
	#同步物品数据
	role.SendObj(HallowsSyncData, (HallowsAct[4], hallowID, hallowthing.odata))
	
	role.Msg(2, 0, GlobalPrompt.Hallows_OneKeyShenzaoOkay % infactTimes)
	

def ClearRoleData(role, param =0):
	role.SetI32(EnumInt32.Hallows_Latest_Times, 0)

if "_HasLoad" not in dir():
	Event.RegEvent(Event.Eve_RoleDayClear, ClearRoleData)
	#消息
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("OnHallowsEnchant", "圣器附魔"), OnHallowsEnchant)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("OnHallowsRefineBegin", "圣器洗练"), OnHallowsRefineBegin)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("OnHallowsrefineSave", "圣器保存洗练属性 "), OnHallowsrefineSave)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("OnHallowInheritance", "圣器继承"), OnHallowInheritance)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("OnHallowShenzao", "圣器神造 "), OnHallowShenzao)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("OnHallowOneKeyShenzao", "圣器一键神造"), OnHallowOneKeyShenzao)
		
