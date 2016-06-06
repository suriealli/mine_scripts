#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DragonTrain.DragonVeinMgr")
#===============================================================================
# 龙脉
#===============================================================================
import cRoleMgr
import random
import Environment
from Game.Role import Event
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumTempObj, EnumObj, EnumDayInt8
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.DragonTrain import DragonTrainMgr, DragonTrainBase
from Game.DragonTrain import DragonVeinBase, DragonTrainConfig
from Game.DailyDo import DailyDo
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType

if "_HasLoad" not in dir():
	
	Sync_role_Dragon_Vein = AutoMessage.AllotMessage("Sync_role_Dragon_Vein", "同步角色龙脉数据")

	#日志
	Tra_DragonVeinActivate = AutoLog.AutoTransaction("Tra_DragonVeinActivate", "激活龙脉")
	Tra_DragonVeinLevelup = AutoLog.AutoTransaction("Tra_DragonVeinLevelup", "龙脉普通升级")
	Tra_DragonVeinOneKeyLevelup = AutoLog.AutoTransaction("Tra_DragonVeinOneKeyLevelup", "龙脉一键升级")
	Tra_DragonVeinGradeup = AutoLog.AutoTransaction("Tra_DragonVeinGradeup", "龙脉普通进化")
	Tra_DragonVeinOneKeyGradeup = AutoLog.AutoTransaction("Tra_DragonVeinOneKeyGradeup", "龙脉一键进化")

#===============================================================================
# 客户端请求
#===============================================================================
def RequestDragonVeinOpenMainPanel(role, msg):
	'''
	客户端请求打开龙脉主面板
	@param role:
	@param msg:
	'''
	ShowDragonVeinData(role)
	
def RequestDragonVeinActivate(role, msg):
	'''
	客户端请求龙脉激活
	@param role:
	@param msg:
	'''
	#角色等级不满足要求
	if role.GetLevel() < EnumGameConfig.DragonVeinNeedLevel:
		return

	vein_idx = msg
	#获取角色龙脉管理器
	roleVeinManager = role.GetTempObj(EnumTempObj.DragonVein)
	#已经激活的不能重复激活
	if vein_idx in roleVeinManager.vein_dict:
		return

	#龙脉的索引必须是当前最大的索引+1
	if roleVeinManager.vein_dict:
		if vein_idx != max(roleVeinManager.vein_dict) + 1:
			return
	else:
		if vein_idx != 1:
			return
	
	cfg = DragonTrainConfig.DRAGON_VEIN_BASE.get(vein_idx)
	if not cfg:
		print "GE_EXC, error while cfg = DragonTrainConfig.DRAGON_VEIN_BASE.get(vein_idx), no such vein_idx(%s)" % vein_idx
		return
	
	#角色等级达不到激活的要求
	if role.GetLevel() < cfg.activateNeedRoleLevel:
		return
	itemcode, cnt = cfg.activateNeedItem

	#角色激活的物品不足
	if role.ItemCnt(itemcode) < cnt:
		return

	with Tra_DragonVeinActivate:
		#扣除物品
		if cnt > 0:
			if role.DelItem(itemcode, cnt) < cnt:
				return
		#激活龙脉
		roleVeinManager.VeinActivate(vein_idx)
		#日志记录激活的龙脉index
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveDragonVeinActivate, vein_idx)
	
	role.GetPropertyGather().ReSetRecountDragonVeinFlag()
	role.GetPropertyGather().ReSetRecountDragonVeinBufFlag()
	ShowDragonVeinData(role)
	DragonTrainMgr.SyncDragonTrainMainPanelData(role)

	
def RequestDragonVeinLevelUp(role, msg):
	'''
	客户端请求龙脉升级
	@param role:
	@param msg:
	'''
	#角色等级不满足要求
	if role.GetLevel() < EnumGameConfig.DragonVeinNeedLevel:
		return

	vein_idx = msg
	#获取角色龙脉管理器
	roleVeinManager = role.GetTempObj(EnumTempObj.DragonVein)
	#没有激活的龙脉不能升级
	vein_obj = roleVeinManager.vein_dict.get(vein_idx, None)
	if not vein_obj:
		return
	
	old_level = vein_obj.level
	old_luck_point = int(vein_obj.level_luck)
	
	base_cfg = DragonTrainConfig.DRAGON_VEIN_BASE.get(vein_idx)
	if not base_cfg:
		print "GE_EXC, error while base_cfg = DragonTrainConfig.DRAGON_VEIN_BASE.get(vein_idx), no such vein_idx(%s)" % vein_idx
		return
	
	#已经是最大等级
	if old_level >= base_cfg.maxLevel:
		return
	
	cfg = DragonTrainConfig.DRAGON_VEIN_LEVEL.get((vein_idx, old_level), None)
	if not cfg:
		print "GE_EXC, error while cfg = DragonTrainConfig.DRAGON_VEIN_LEVEL.get((vein_idx, old_level), None), no such (vein_idx, old_level)(%s,%s)" % (vein_idx, old_level)
		return
	
	#如果免费升级次数已经用完了的话
	nowTimes = role.GetDI8(EnumDayInt8.DragonVeinLevelUpCnt)
	if nowTimes >= EnumGameConfig.DragonVeinLevelUp_DailyFreeTimes:
		#物品不足
		itemcode, cnt = cfg.evolveNeedItem
		if role.ItemCnt(itemcode) < cnt:
			return
	
	is_success = False
	
	with Tra_DragonVeinLevelup:
		#首先扣除物品 或者增加免费次数
		if nowTimes >= EnumGameConfig.DragonVeinLevelUp_DailyFreeTimes:
			if role.DelItem(itemcode, cnt) < cnt:
				return
			WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_DragonVeinLevel, (role, 1))
		else:
			role.IncDI8(EnumDayInt8.DragonVeinLevelUpCnt, 1)
		#小于最低祝福值的话则升级失败，但是增加祝福值
		if vein_obj.level_luck < cfg.successNeedMinLucky:
			new_luck_point = old_luck_point + random.randint(*cfg.failAddLuckyRange)
			vein_obj.levelluck_set(new_luck_point)

		#如果大于或者等于最低祝福值的话，则需要分情况考虑
		else:
			
			odds = cfg.oddsBase + (vein_obj.level_luck * cfg.perLuckyAddOdds)
			successRi = random.randint(1, 100000)
			
			#如果成功
			if (vein_obj.level_luck >= cfg.maxEvolveLucky) or (successRi < odds):
				#清空祝福值
				new_luck_point = 0
				vein_obj.levelluck_set(new_luck_point)
				roleVeinManager.VeinLevelup(vein_idx, 1)
				is_success = True

			#否则增加祝福值,祝福值须小于祝福值的上限
			else:
				new_luck_point = old_luck_point + random.randint(*cfg.failAddLuckyRange)
				new_luck_point = min(new_luck_point, cfg.maxEvolveLucky)
				vein_obj.levelluck_set(new_luck_point)
			
	ShowDragonVeinData(role)
	if is_success == True:		
		role.GetPropertyGather().ReSetRecountDragonVeinFlag()
		role.GetPropertyGather().ReSetRecountDragonVeinBufFlag()
		DragonTrainMgr.SyncDragonTrainMainPanelData(role)
		role.Msg(2, 0, GlobalPrompt.DragonVein_LevelUp % (vein_obj.name, vein_obj.level))
		
	else:
		role.Msg(2, 0, GlobalPrompt.DragonVein_LevelLuckUp % (new_luck_point - old_luck_point))
		
	#每日必做 -- 龙脉升级(不管失败与否, 扣了免费次数就给加)
	if nowTimes < EnumGameConfig.DragonVeinLevelUp_DailyFreeTimes:
		Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_DragonVeinLvUp, 1))
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_DragonVeinUp, 1))
	
def DragonVeinOneKeyLevelUp(role, msg):
	'''
	客户端请求龙脉一键升级
	@param role:
	@param msg:
	'''
	#角色等级不满足要求
	if role.GetLevel() < EnumGameConfig.DragonVeinNeedLevel:
		return

	vein_idx = msg
	#获取角色龙脉管理器
	roleVeinManager = role.GetTempObj(EnumTempObj.DragonVein)
	#没有激活的龙脉不能升级
	vein_obj = roleVeinManager.vein_dict.get(vein_idx, None)
	if not vein_obj:
		return
	#该龙脉的最大等级
	maxlevel = vein_obj.maxlevel
	#龙脉的本次升级之前的等级
	old_level = int(vein_obj.level)
	
	#已经是最大等级
	if old_level >= maxlevel:
		return
	
	#这里防止对龙脉的属性直接进行操作，进行了一次复制
	luck_point = int(vein_obj.level_luck)
	old_luck_point = int(vein_obj.level_luck)
	#已经用过免费升级的次数
	old_free_times = role.GetDI8(EnumDayInt8.DragonVeinLevelUpCnt)
	
	cfg = DragonTrainConfig.DRAGON_VEIN_LEVEL.get((vein_idx, old_level), None)
	if not cfg:
		print "GE_EXC, error while cfg = DragonTrainConfig.DRAGON_VEIN_LEVEL.get((vein_idx, old_level), None), no such (vein_idx, old_level)(%s,%s)" % (vein_idx, old_level)
		return
	#龙脉升级（如果不是免费升级的话）需要的物品及其个数
	itemcode, cnt = cfg.evolveNeedItem
	
	#总共可以免费升级的次数
	total_free_times = max(EnumGameConfig.DragonVeinLevelUp_DailyFreeTimes - old_free_times, 0)
	#总共可以升级的次数
	total_times = total_free_times + role.ItemCnt(itemcode) / cnt
	
	#如果总次数大于0的话才往下进行操作，否则也就没办法升级了
	if not total_times > 0:
		role.Msg(2, 0, GlobalPrompt.DragonVein_Lackof)
		return
	#实际升级的次数
	fact_times = 0
	#升级是否成功的标志
	is_seccess = False
	
	for _ in xrange(total_times):
		#实际升级的次数+1
		fact_times += 1
		#当祝福值小于升级需要的最低祝福值的时候，升级一定会失败
		if luck_point < cfg.successNeedMinLucky:
			#随机增加祝福值
			luck_point += random.randint(*cfg.failAddLuckyRange)
		#当祝福值大于升级需要的最大祝福值的时候，升级一定会成功	
		elif luck_point >= cfg.maxEvolveLucky:
			#祝福值置为0
			luck_point = 0
			#成功的标志
			is_seccess = True
			#终止循环
			break
		
		#否则就需要来获取一个随机成功的情况了
		else:
			#计算本次升级的概率
			odds = cfg.oddsBase + (vein_obj.level_luck * cfg.perLuckyAddOdds)
			#生成（伪）随机数
			successRi = random.randint(1, 100000)
			if successRi < odds:
				luck_point = 0
				is_seccess = True
				break
			else:
				luck_point += random.randint(*cfg.failAddLuckyRange)
	
	#实际上升级的免费次数 
	fact_free_times = min(fact_times, total_free_times)
	#实际上升级的收费次数
	fact_charge_times = max(fact_times - fact_free_times, 0)
	#实际应该扣除的物品个数
	total_item_to_del = fact_charge_times * cnt

	fact_total_times = fact_free_times + fact_charge_times

	with Tra_DragonVeinOneKeyLevelup:
		
		if fact_free_times > 0:
			#增加已使用免费升级的次数
			role.IncDI8(EnumDayInt8.DragonVeinLevelUpCnt, fact_free_times)
			#扣除物品
		if total_item_to_del > 0:
			role.DelItem(itemcode, total_item_to_del)
			
		if is_seccess == True:
			roleVeinManager.VeinLevelup(vein_idx, 1)
			
		vein_obj.levelluck_set(luck_point)
		#精彩活动
		if total_item_to_del:
			WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_DragonVeinLevel, (role, total_item_to_del))
		
	ShowDragonVeinData(role)
	if is_seccess == True:
		role.GetPropertyGather().ReSetRecountDragonVeinFlag()
		role.GetPropertyGather().ReSetRecountDragonVeinBufFlag()
		DragonTrainMgr.SyncDragonTrainMainPanelData(role)
		role.Msg(2, 0, GlobalPrompt.DragonVeinOnekeyLevelUpOkay % (fact_total_times, vein_obj.name, vein_obj.level))
	
	else:
		role.Msg(2, 0, GlobalPrompt.DragonVein_Lackof)
		role.Msg(2, 0, GlobalPrompt.DragonVeinOnekeyLevelUpFailed % (fact_total_times, vein_obj.name, (luck_point - old_luck_point)))
	
	#每日必做 -- 龙脉升级(不管失败与否, 扣了免费次数就给加)
	if fact_free_times:
		Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_DragonVeinLvUp, fact_free_times))
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_DragonVeinUp, fact_total_times))

def RequestDragonVeinEvolve(role, msg):
	'''
	客户端请求龙脉进化
	@param role:
	@param msg:
	'''
	#角色等级不满足要求
	if role.GetLevel() < EnumGameConfig.DragonVeinNeedLevel:
		return

	vein_idx = msg
	#获取角色龙脉管理器
	roleVeinManager = role.GetTempObj(EnumTempObj.DragonVein)
	#没有激活的龙脉不能升级
	vein_obj = roleVeinManager.vein_dict.get(vein_idx, None)
	if not vein_obj:
		return
	
	old_grade = vein_obj.grade
	old_luck_point = int(vein_obj.grade_luck)
	
	base_cfg = DragonTrainConfig.DRAGON_VEIN_BASE.get(vein_idx)
	if not base_cfg:
		print "GE_EXC, error while base_cfg = DragonTrainConfig.DRAGON_VEIN_BASE.get(vein_idx), no such vein_idx(%s)" % vein_idx
		return
	
	#已经是最大品阶
	if old_grade >= base_cfg.maxGrade:
		return
	
	cfg = DragonTrainConfig.DRAGON_VEIN_GRADE.get((vein_idx, old_grade), None)
	if not cfg:
		print "GE_EXC, error while cfg = DragonTrainConfig.DRAGON_VEIN_GRADE.get((vein_idx, old_grade), None), no such (vein_idx, old_grade)(%s,%s)" % (vein_idx, old_grade)
		return
	
	#物品不足
	itemcode, cnt = cfg.evolveNeedItem
	if role.ItemCnt(itemcode) < cnt:
		return
	
	is_success = False
	
	with Tra_DragonVeinGradeup:
		#首先扣除物品 
		if role.DelItem(itemcode, cnt) < cnt:
			return
		
		#小于最低祝福值的话则升级失败，但是增加祝福值
		if vein_obj.grade_luck < cfg.successNeedMinLucky:
			new_luck_point = old_luck_point + random.randint(*cfg.failAddLuckyRange)
			vein_obj.gradeluck_set(new_luck_point)

		#如果大于最低祝福值的话，则需要分情况考虑
		else:
			odds = cfg.oddsBase + (vein_obj.grade_luck * cfg.perLuckyAddOdds)
			successRi = random.randint(1, 100000)
			
			#如果成功
			if (vein_obj.grade_luck >= cfg.maxEvolveLucky) or (successRi < odds):
				#清空祝福值
				new_luck_point = 0
				vein_obj.gradeluck_set(new_luck_point)
				roleVeinManager.VeinGradeup(vein_idx, 1)
				is_success = True
	
			#否则增加祝福值,祝福值须小于祝福值的上限
			else:
				new_luck_point = old_luck_point + random.randint(*cfg.failAddLuckyRange)
				new_luck_point = min(new_luck_point, cfg.maxEvolveLucky)
				vein_obj.gradeluck_set(new_luck_point)
		#精彩活动
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_DragonVeinEvo, (role, cnt))
	
	#同步龙脉数据
	ShowDragonVeinData(role)
	#仅仅在升级成功的时候需要重算
	if is_success == True:
		role.GetPropertyGather().ReSetRecountDragonVeinFlag()
		role.GetPropertyGather().ReSetRecountDragonVeinBufFlag()
		DragonTrainMgr.SyncDragonTrainMainPanelData(role)
		role.Msg(2, 0, GlobalPrompt.DragonVein_GradeUp % (vein_obj.name, vein_obj.grade))

	else:
		role.Msg(2, 0, GlobalPrompt.DragonVein_GradeLuckUp % (new_luck_point - old_luck_point))
	

def DragonVeinOneKeyEvolve(role, msg):
	'''
	客户端请求龙脉一键进化
	@param role:
	@param msg:
	'''
	#角色等级不满足要求
	if role.GetLevel() < EnumGameConfig.DragonVeinNeedLevel:
		return

	vein_idx = msg
	#获取角色龙脉管理器
	roleVeinManager = role.GetTempObj(EnumTempObj.DragonVein)
	#没有激活的龙脉不能升级
	vein_obj = roleVeinManager.vein_dict.get(vein_idx, None)
	if not vein_obj:
		return
	#某个龙脉的最大品阶
	maxgrade = vein_obj.maxgrade
	#龙脉在本次进化之前的品阶
	old_grade = int(vein_obj.grade)
	
	#已经是最大等级
	if old_grade >= maxgrade:
		return
	
	luck_point = int(vein_obj.grade_luck)
	old_luck_point = int(vein_obj.grade_luck)
	
	cfg = DragonTrainConfig.DRAGON_VEIN_GRADE.get((vein_idx, old_grade), None)
	if not cfg:
		print "GE_EXC, error while cfg = DragonTrainConfig.DRAGON_VEIN_GRADE.get((vein_idx, old_grade), None), no such (vein_idx, old_grade)(%s,%s)" % (vein_idx, old_grade)
		return
	#获取进化时需要的道具及其数量
	itemcode, cnt = cfg.evolveNeedItem
	#最多可能循环进化的次数 
	total_times = role.ItemCnt(itemcode) / cnt
	
	if not total_times > 0:
		role.Msg(2, 0, GlobalPrompt.DragonVein_Lackof)
		return
	#实际循环的次数
	fact_times = 0
	#是否进化成功的标志
	is_seccess = False
	
	for _ in xrange(total_times):
		
		#实际循环的次数
		fact_times += 1
		#小于最低的进化值的话是不会进化成功的
		if luck_point < cfg.successNeedMinLucky:
			luck_point += random.randint(*cfg.failAddLuckyRange)
		
		#如果大于祝福值得最大值的话则一定会进程成功的
		elif luck_point >= cfg.maxEvolveLucky:
			#新的进化值变为0
			luck_point = 0
			#是否进化成功的标志置为True
			is_seccess = True
			#终止循环
			break

		else:
			#首先计算本次进化成功的万分率
			odds = cfg.oddsBase + (vein_obj.level_luck * cfg.perLuckyAddOdds)
			#生成一个随机的万分值与之比较，小于的话则判定成功，否则判定失败
			successRi = random.randint(1, 100000)
			if successRi < odds:
				#新的进化值变为0
				luck_point = 0
				#是否进化成功的标志置为True
				is_seccess = True
				break
			else:
				#龙脉进化祝福值随机增加
				luck_point += random.randint(*cfg.failAddLuckyRange)

	#实际应该扣除的物品个数
	total_item_to_del = fact_times * cnt

	with Tra_DragonVeinOneKeyGradeup:
		#扣除物品
		if total_item_to_del > 0:
			role.DelItem(itemcode, total_item_to_del)
			
		if is_seccess == True:
			roleVeinManager.VeinGradeup(vein_idx, 1)
		#更新龙脉的进化祝福值（进化值）
		vein_obj.gradeluck_set(luck_point)
		
		if total_item_to_del:
			#精彩活动
			WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_DragonVeinEvo, (role, total_item_to_del))
	#刷新龙脉的数据
	ShowDragonVeinData(role)
	
	if is_seccess == True:
		#重算龙脉基础属性
		role.GetPropertyGather().ReSetRecountDragonVeinFlag()
		#重算龙脉buf(被动技能)
		role.GetPropertyGather().ReSetRecountDragonVeinBufFlag()
		#同步神龙属性信息
		DragonTrainMgr.SyncDragonTrainMainPanelData(role)
		#提示神龙升级成功
		role.Msg(2, 0, GlobalPrompt.DragonVeinOnekeyGradeUpOkay % (fact_times, vein_obj.name, vein_obj.grade))
		
	else:
		#提示材料不足
		role.Msg(2, 0, GlobalPrompt.DragonVein_Lackof)
		#提示神龙升级失败 
		role.Msg(2, 0, GlobalPrompt.DragonVeinOnekeyGradeUpFailed % (fact_times, vein_obj.name, (luck_point - old_luck_point)))


def ShowDragonVeinData(role):
	#显示角色龙脉数据
	DragonTrainDict = role.GetObj(EnumObj.DragonTrain)
	vein_data_dict = DragonTrainDict.setdefault(DragonTrainBase.DRAGON_TRAIN_Vein_DICT_IDX, {})
	role.SendObj(Sync_role_Dragon_Vein, vein_data_dict)
	

def OnRoleInit(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	#初始化角色龙脉管理器
	role.SetTempObj(EnumTempObj.DragonVein, DragonVeinBase.DragonVeinManager(role))


def DailyClear(role, param):
	'''
	每日清空
	'''
	#角色等级不满足要求还未开启的不需要每日清空
	if role.GetLevel() < EnumGameConfig.DragonVeinNeedLevel:
		return
	#获取角色龙脉管理器
	roleVeinManager = role.GetTempObj(EnumTempObj.DragonVein)
	#对于小于某个品阶的所有的龙脉要清空其祝福值
	DragonVeinGrade_not_clear = EnumGameConfig.DragonVeinGrade_not_clear
	for vein_obj in roleVeinManager.vein_dict.itervalues():
		#只有小于橙色品质的龙脉其品阶祝福值才需要清空
		if vein_obj.grade < DragonVeinGrade_not_clear:
			vein_obj.gradeluck_set(0)
	#实时更新龙脉数据
	ShowDragonVeinData(role)

def OnRoleLogin(role, param):
	'''
	角色登录
	@param role:
	@param param:
	'''
	#登录的时候发送这条消息以通知客户端激活的龙脉技能情况
	ShowDragonVeinData(role)
	

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		#角色初始化
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		Event.RegEvent(Event.Eve_RoleDayClear, DailyClear)
		#角色登录
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnRoleLogin)

	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Vein_Open_Main_Panel", "客户端请求打开龙脉主面板"), RequestDragonVeinOpenMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Vein_Activate", "客户端请求龙脉激活"), RequestDragonVeinActivate)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Vein_Level_Up", "客户端请求龙脉升级"), RequestDragonVeinLevelUp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Vein_Evolve", "客户端请求龙脉进化"), RequestDragonVeinEvolve)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Vein_Onekey_Level_Up", "客户端请求龙脉一键升级"), DragonVeinOneKeyLevelUp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Dragon_Vein_Onekey_Evolve", "客户端请求龙脉一键进化"), DragonVeinOneKeyEvolve)

