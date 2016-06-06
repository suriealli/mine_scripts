#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.Gem")
#===============================================================================
# 宝石镶嵌
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumTempObj, EnumInt8, EnumInt32
from Game.Activity.ProjectAct import ProjectAct, EnumProActType

if "_HasLoad" not in dir():
	Equipment_Gem_Dict = {} #宝石配置
	Sealing_Spirit_Dict = {} #宝石封灵配置
	
	#宝石锻造配置 {forgeId:cfg,}
	GemForge_ForgeConfig_Dict = {}
	#锻造石转换配置 {transformId:cfg,}
	ForgeStone_TransformConfig_Dict = {}
	
	MIN_LEVEL_GEM = 35 #宝石开启的最低等级
	MIN_LEVEL_SEALING = 60 #封灵的最低等级
	MAX_SEALING_LEVEL = 12 #封灵最高可达多少级
	#日志
	MosaicGem_log = AutoLog.AutoTransaction("MosaicGem_log", "镶嵌宝石")
	GemSynthetic_log = AutoLog.AutoTransaction("GemSynthetic_log", "宝石合成")
	GetoffGem_log = AutoLog.AutoTransaction("GetoffGem_log", "下宝石")
	GemSealing_log = AutoLog.AutoTransaction("GemSealing_log", "宝石封灵")
	GemLevelup_log = AutoLog.AutoTransaction("GemLevelup_log", "宝石升级")
	
	Tra_GemForge_Forge = AutoLog.AutoTransaction("Tra_GemForge_Forge", "宝石锻造_锻造宝石")
	Tra_GemForge_Transform = AutoLog.AutoTransaction("Tra_GemForge_Transform", "宝石锻造_锻造石转换")
	GemResolve_log = AutoLog.AutoTransaction("GemResolve_log", "宝石分解")

def GetAllGem(role):
	'''
	获取背包所有的宝石,并按宝石类型分类
	'''
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	gem_coding_by_type = {} #key为宝石类型
	gem_coding_list = Equipment_Gem_Dict.values()
	for coding, _ in packageMgr.codingGather.iteritems():
		if coding in gem_coding_list:
			cfg = Equipment_Gem_Dict.get(coding)
			cnt = packageMgr.ItemCnt(coding)
			if not cnt:
				continue 
			GemType = cfg.GemType
			if GemType not in gem_coding_by_type:				
				gem_coding_by_type[GemType] = [[coding,cnt]]
			else:
				gem_coding_by_type[GemType].append([coding,cnt])
	return gem_coding_by_type
			
def GetoffGem(role, msg):	
	'''
	取下宝石
	@param role:
	@param msg:
	'''
	backId, (eId, location) = msg #从下标1开始
	if location <= 0:
		return
	equipment = role.FindGlobalProp(eId)
	if not equipment:
		return
	#获取已镶嵌的宝石
	gem_list = equipment.GetEquipmentGem()
	#没镶嵌宝石
	if not gem_list:
		return
	#下标不存在
	if location > len(gem_list):
		return
	with GetoffGem_log:
		del_gem = equipment.delGembyLocation(location)
		if del_gem:#删除成功
			role.AddItem(del_gem, 1)
	#判断重算属性
	equipment.ResetGemPro()
	if equipment.owner:
		#设置装备属性重算
		equipment.owner.GetPropertyGather().ReSetRecountEquipmentGemFlag()
	#将新的宝石列表发给客户端
	gem_list = equipment.GetEquipmentGem()
	role.CallBackFunction(backId, gem_list)
	
def MosaicGem(role, msg):
	'''
	镶嵌宝石
	@param role:
	@param msg:
	'''
	backId, (eId, GemCoding) = msg
	global MIN_LEVEL_GEM
	if role.GetLevel() < MIN_LEVEL_GEM:
		return
	equipment = role.FindGlobalProp(eId)
	if not equipment:
		return
	if not equipment.cfg.Mosaic:
		return
	if role.ItemCnt(GemCoding) < 1:
		return
	global Equipment_Gem_Dict
	cfg = Equipment_Gem_Dict.get(GemCoding)
	if not cfg:
		print "GE_EXC, can not find cfg by (%s) in Equipment_Gem_Dict" % GemCoding
		return
	
	#获取已镶嵌的宝石
	gem_list = equipment.GetEquipmentGem()
	holed = len(gem_list) #已镶嵌的数量
	cfg_hole = equipment.cfg.holeNum #装备可镶嵌的孔数
	if holed >= cfg_hole:#已镶嵌满
		return
	gemType = cfg.GemType#宝石类型

	for gem in gem_list:
		if gem[1] == gemType:#存在相同类型的宝石
			return
	
	with MosaicGem_log:
		role.DelItem(GemCoding, 1)
		equipment.SetEquipmentGem(GemCoding, gemType, cfg.GemLevel)
	#判断重算属性
	equipment.ResetGemPro()
	if equipment.owner:
		equipment.owner.GetPropertyGather().ReSetRecountEquipmentGemFlag()
	gem_list = equipment.GetEquipmentGem()
	role.CallBackFunction(backId, gem_list)
				
def GemSynthetic(role, msg):
	'''
	宝石合成
	@param role:
	@param msg:
	'''
	backId, (coding, num) = msg #coding宝石材料ID，num是需要合成的数目
	if num <= 0:
		return
	global Equipment_Gem_Dict
	cfg = Equipment_Gem_Dict.get(coding)
	if not cfg:
		print "GE_EXC, can not find cfg by (%s) in Equipment_Gem_Dict,GemSynthetic" % coding
		return
	if not cfg.CanMix:#检测材料是否能合成
		return
	if not cfg.NextGemID:#下一级的宝石是否存在
		return
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	need_num = cfg.MixNum * num
	if packageMgr.ItemCnt(coding) < need_num:
		return
	need_money = cfg.MixMoney * num
	if role.GetMoney() < need_money:
		return
	
	with GemSynthetic_log:
		if role.DelItem(coding,need_num) < need_num:
			return
		role.DecMoney(need_money)
		role.AddItem(cfg.NextGemID, num)
	#专题活动相关
	if cfg.GemLevel >= 4:
		ProjectAct.GetFunByType(EnumProActType.ProjectGemEvent, [role, cfg.GemLevel+1, num])
		#北美通用活动
		if Environment.EnvIsNA():
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.GemSynthetic(cfg.GemLevel + 1, num)
			HalloweenNAMgr.GemSyntheticDay(cfg.GemLevel + 1, num)
	role.CallBackFunction(backId, 1)
	
def SealingSpirit(role, msg):
	'''
	宝石封灵
	@param role:
	@param msg:
	'''
	backId, _ = msg
	global MIN_LEVEL_SEALING
	global MAX_SEALING_LEVEL
	if role.GetLevel() < MIN_LEVEL_SEALING:
		return
	global Sealing_Spirit_Dict
	#获取玩家的封灵
	Sealing_level = role.GetI8(EnumInt8.SealingSpiritID)
	cfg = Sealing_Spirit_Dict.get(Sealing_level)
	if not cfg:
		print "GE_EXC,can not find cfg by SealingLevel=(%s) in Sealing_Spirit_Dict" % Sealing_level
		return
	if not cfg.NextLevel:#已是最高级
		return
	coding = cfg.needItem
	cnt = role.ItemCnt(coding)
	if cnt <= 0:
		return
	exp = role.GetI32(EnumInt32.SealingExpID)
	#升级需要的个数
	need_cnt = (cfg.needExp - exp) / cfg.addExp
	
	with GemSealing_log:
		if cnt < need_cnt:
			role.DelItem(coding, cnt)
			role.IncI32(EnumInt32.SealingExpID, cnt * cfg.addExp)
		else:
			role.DelItem(coding, need_cnt)
			#升级
			role.IncI8(EnumInt8.SealingSpiritID, 1)
			#经验清0
			role.SetI32(EnumInt32.SealingExpID, 0)
			#属性重算
			equipmentMgr = role.GetTempObj(EnumTempObj.enRoleEquipmentMgr)
			for equipment in equipmentMgr.objIdDict.itervalues():
				equipment.ResetGemPro()
				#设置装备属性重算
				equipment.owner.GetPropertyGather().ReSetRecountEquipmentGemFlag()
			AllHero = role.GetAllHero()
			for hero in AllHero.values():
				heroEquipmentMgr = hero.equipmentMgr
				if not heroEquipmentMgr : continue
				for equipment in heroEquipmentMgr.objIdDict.itervalues():
					equipment.ResetGemPro()
					#设置装备属性重算
					equipment.owner.GetPropertyGather().ReSetRecountEquipmentGemFlag()
	role.CallBackFunction(backId, 1)

def AllGemLevelUp(role, msg):
	'''
	一键合成
	@param role:
	@param msg:
	'''
	backId, gem_list = msg
	if role.GetVIP() < EnumGameConfig.VIP_ALL_SYNTHETI:
		return
	tbool = False
	for Hcoding in gem_list:
		cfg = Equipment_Gem_Dict.get(Hcoding)
		if not cfg:
			continue
		can_cnt = GetGemCnt(role, Hcoding)
		if not can_cnt:
			continue
		k = SyntheticGemNum(role, Hcoding, can_cnt)
		if k and tbool == False:
			tbool = True
	if tbool:
		role.CallBackFunction(backId, 1)
		
def GetGemCnt(role, Hcoding):
	'''
	获取可以合成这种宝石的个数
	@param role:
	@param Hcoding:
	'''	
	cfg = Equipment_Gem_Dict.get(Hcoding)
	if not cfg:
		return
	needNum = cfg.decompositionNum
	lowerlist = cfg.lowerlist
	if not lowerlist:
		return
	new_cnt = 0
	if type(lowerlist) == int:
		new_cfg = Equipment_Gem_Dict.get(lowerlist)
		if not new_cfg:
			return
		cfg_cnt = role.ItemCnt(lowerlist)
		if not cfg_cnt:
			return
		if new_cfg.decompositionNum:
			new_cnt = new_cfg.decompositionNum * cfg_cnt
		else:
			new_cnt = cfg_cnt
	elif type(lowerlist) == list:
		for coding in lowerlist:
			lower_cfg = Equipment_Gem_Dict.get(coding)
			if not lower_cfg:
				return
			cnt = role.ItemCnt(coding)
			if not cnt:
				continue			
			if lower_cfg.decompositionNum:
				new_cnt += lower_cfg.decompositionNum * cnt
			else:
				new_cnt += cnt
	if not new_cnt:
		return
	return new_cnt / needNum		

def SyntheticGemNum(role, Hcoding, num):
	'''
	合成指定个数宝石
	@param role:
	@param Hcoding:
	@param num:
	'''
	cfg = Equipment_Gem_Dict.get(Hcoding)
	if not cfg:
		return
	lowerlist = cfg.lowerlist
	if not lowerlist:
		return
	needNum = cfg.decompositionNum * num
	del_list = []
	if type(lowerlist) == int:#升级成2级宝石
		new_cfg = Equipment_Gem_Dict.get(lowerlist)
		if not new_cfg:
			return
		cfg_cnt = role.ItemCnt(lowerlist)
		if not cfg_cnt:
			return
		if cfg.decompositionNum:
			new_cnt = cfg.decompositionNum * cfg_cnt
		else:
			new_cnt = cfg_cnt
		if new_cnt < needNum:
			return
		else:
			del_list.append([lowerlist, needNum])
	elif type(lowerlist) == list:#升级成>2级宝石
		left_cnt = needNum
		tbool = False
		for coding in lowerlist:
			cfg_cnt = role.ItemCnt(coding)
			if not cfg_cnt:
				continue
			new_cfg = Equipment_Gem_Dict.get(coding)
			if not new_cfg:
				continue
			new_cnt = cfg_cnt
			if new_cfg.decompositionNum:
				new_cnt = new_cfg.decompositionNum * cfg_cnt
			if new_cnt >= left_cnt:
				cnt = left_cnt
				if new_cfg.decompositionNum:
					cnt = left_cnt / new_cfg.decompositionNum
				del_list.append((coding, cnt))
				tbool = True
				break
			else:
				del_list.append((coding, cfg_cnt))
				left_cnt -= new_cnt
	if not tbool:
		return
	with GemLevelup_log:
		for item in del_list:
			if not item[1]:
				continue
			if role.DelItem(item[0], item[1]) < item[1]:
				return
		role.AddItem(Hcoding, num)
		#专题活动相关
		if cfg.GemLevel >= 5:
			ProjectAct.GetFunByType(EnumProActType.ProjectGemEvent, [role, cfg.GemLevel, num])
			#北美通用活动
			if Environment.EnvIsNA():
				HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
				HalloweenNAMgr.GemSynthetic(cfg.GemLevel, num)
				HalloweenNAMgr.GemSyntheticDay(cfg.GemLevel, num)
		return True
	
def GemLevelUp(role, msg):
	'''
	宝石升级
	@param role:
	@param msg:
	'''
	backId, (eId, index) = msg #Hcoding为目标等级的宝石,Ocoding为当前宝石等级
	if index < 1 : return

	equipment = role.FindGlobalProp(eId)
	if not equipment : return
	gem_list = equipment.GetEquipmentGem()
	if len(gem_list) < index:
		return
	
	nowCoding, Otype, level  = gem_list[index - 1]
	
	nowCodingCfg = Equipment_Gem_Dict.get(nowCoding)
	if not nowCodingCfg: 
		print "GE_EXC, GemLevelUp nowCoding(%s)" % nowCoding
		return
	Hcoding = nowCodingCfg.NextGemID
	cfg = Equipment_Gem_Dict.get(Hcoding)
	if not cfg : return
	lowerlist = cfg.lowerlist
	#下一级宝石竟然是一级宝石，有问题
	if not lowerlist : return
	
	if Otype != cfg.GemType:#宝石类型不同
		return
	
	if role.ItemCnt(nowCoding) >= 1:
		with GemLevelup_log:
			role.DelItem(nowCoding, 1)
			equipment.LevelUpEquipmentGem(index, Hcoding, cfg.GemType, cfg.GemLevel)
	
		#判断重算属性
		equipment.ResetGemPro()
		if equipment.owner:
			#设置装备属性重算
			equipment.owner.GetPropertyGather().ReSetRecountEquipmentGemFlag()
		role.CallBackFunction(backId, 1)
		if cfg.GemLevel >= 5:
			ProjectAct.GetFunByType(EnumProActType.ProjectGemEvent, [role, cfg.GemLevel, 1])
			#北美通用活动
			if Environment.EnvIsNA():
				HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
				HalloweenNAMgr.GemSynthetic(cfg.GemLevel, 1)
				HalloweenNAMgr.GemSyntheticDay(cfg.GemLevel, 1)
		return
	elif level == 1:
		#一级宝石，并且没有其他的一级宝石了
		return
	
	#总共需要的一级宝石数量
	needNum = cfg.decompositionNum
	del_list = []
	new_cnt = 0

	tbool = False
	for coding in lowerlist:
		itemCnt = role.ItemCnt(coding)
		if coding == nowCoding:
			itemCnt += 1
		if not itemCnt:
			continue
		new_cfg = Equipment_Gem_Dict.get(coding)
		if not new_cfg:
			print "GE_EXC, error GemLevelUp no cfg coding(%s)" % coding
			continue
		#计算相当于多少个一级宝石
		new_cnt = new_cfg.decompositionNum * itemCnt
		if new_cnt >= needNum:
			#计算真正需要的宝石数量
			realNeeItemCnt = needNum / new_cfg.decompositionNum
			if coding == nowCoding:
				realNeeItemCnt -= 1
			del_list.append((coding, realNeeItemCnt))
			tbool = True
			break
		else:
			if coding == nowCoding:
				itemCnt -= 1
			del_list.append((coding, itemCnt))
			needNum -=  new_cnt
	if not tbool:
		return
	with GemLevelup_log:
		for item in del_list:
			if not item[1]:
				continue
			if role.DelItem(item[0], item[1]) < item[1]:
				print "GE_EXC, error in GemLevelUp DelItem （%s）" % role.GetRoleID()
				return
		equipment.LevelUpEquipmentGem(index, Hcoding, cfg.GemType, cfg.GemLevel)			
	#判断重算属性
	equipment.ResetGemPro()
	if equipment.owner:
		#设置装备属性重算
		equipment.owner.GetPropertyGather().ReSetRecountEquipmentGemFlag()
	#专题活动相关
	if cfg.GemLevel >= 5:
		ProjectAct.GetFunByType(EnumProActType.ProjectGemEvent, [role, cfg.GemLevel, 1])
		#北美通用活动
		if Environment.EnvIsNA():
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.GemSynthetic(cfg.GemLevel, 1)
			HalloweenNAMgr.GemSyntheticDay(cfg.GemLevel, 1)
	role.CallBackFunction(backId, 1)
	
	
def GetTotalGemLevel(role):
	AllHero = role.GetAllHero()
	gemLevel = 0
	#遍历玩家
	roleEquipmentMgr = role.GetTempObj(EnumTempObj.enRoleEquipmentMgr)
	for equipment in roleEquipmentMgr.objIdDict.itervalues():
		gemList = equipment.GetEquipmentGem()
		if not gemList: continue
		for value in gemList:
			gemLevel += value[2]
	#遍历英雄
	for hero in AllHero.values():
		heroEquipmentMgr = hero.equipmentMgr
		if not heroEquipmentMgr : continue
		for equipment in heroEquipmentMgr.objIdDict.itervalues():
			gemList = equipment.GetEquipmentGem()
			if not gemList: continue
			for value in gemList:
				gemLevel += value[2]
	return gemLevel


def OnForge(role, msg):
	'''
	宝石锻造_请求宝石锻造
	@param msg: backId,forgeId
	'''
	if role.GetLevel() < EnumGameConfig.GemFoege_NeedLevel:
		return
	
	backId, forgeId = msg
	forgeCfg = GemForge_ForgeConfig_Dict.get(forgeId)
	if not forgeCfg:
		return
	
	gemCodingA, gemCodingB, needItemA, needItemB = forgeCfg.gemCodingA, forgeCfg.gemCodingB, forgeCfg.needItemA, forgeCfg.needItemB
	
	#待合成的两种宝石数量不足
	if role.ItemCnt(gemCodingA) < 1 or role.ItemCnt(gemCodingB) < 1:
		return
	
	#A辅助材料数量不足
	needItemACoding, needItemACnt = needItemA
	if role.ItemCnt(needItemACoding) < needItemACnt:
		return
	
	#B辅助材料数量不足
	needItemBCoding, needItemBCnt = needItemB
	if role.ItemCnt(needItemBCoding) < needItemBCnt:
		return
	
	with Tra_GemForge_Forge:
		#扣除待合成宝石
		role.DelItem(gemCodingA, 1)
		role.DelItem(gemCodingB, 1)
		#扣除辅助材料
		role.DelItem(needItemACoding, needItemACnt)
		role.DelItem(needItemBCoding, needItemBCnt)
		#获得新宝石
		returnCoding, returnCnt = forgeCfg.returnItem
		role.AddItem(returnCoding, returnCnt)
		role.Msg(2, 0, GlobalPrompt.GemForge_Tips_FotrgeSuccess % (returnCoding, returnCnt))
	
	role.CallBackFunction(backId, None)
		

def OnTransform(role, msg):
	'''
	宝石锻造_请求转换锻造石
	@param msg: backId,transformId
	'''
	if role.GetLevel() < EnumGameConfig.GemFoege_NeedLevel:
		return
	
	backId, transformId = msg
	transformCfg = ForgeStone_TransformConfig_Dict.get(transformId)
	if not transformCfg:
		return
	
	
	forgeStoneA, needUnbindRMB = transformCfg.forgeStoneA, transformCfg.needUnbindRMB
	#待转换锻造石数量
	forgeStoneACoding, forgeStoneACnt = forgeStoneA
	if role.ItemCnt(forgeStoneACoding) < forgeStoneACnt:
		return
	
	#转换神石
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	with Tra_GemForge_Transform:
		#扣除待转换的锻造石
		role.DelItem(forgeStoneACoding, forgeStoneACnt)
		#扣神石
		role.DecUnbindRMB(needUnbindRMB)
		#获得新的锻造石
		returnItemCoding, returnItemCnt = transformCfg.forgeStoneB
		role.AddItem(returnItemCoding, returnItemCnt)
		#提示
		role.Msg(2, 0, GlobalPrompt.GemForge_Tips_TransformSuccess % (returnItemCoding, returnItemCnt))
	
	role.CallBackFunction(backId, None)
	
	
def GemResolve(role,msg):
	'''
	宝石分解
	@param msg:backid,coding
	'''
	level = role.GetLevel()
	if level < EnumGameConfig.GemResolve_NeedLevel :
		return
	backid, coding = msg   #coding:宝石的coding
	global Equipment_Gem_Dict
	cfg =  Equipment_Gem_Dict.get(coding)
	if not cfg:
		print "GE_EXC ,can't not found cfg by (%s) in GemResolve" % coding
		return
	if not cfg.IsResolve :
		#提示不能分解
		role.Msg(2, 0, GlobalPrompt.Can_not_resolve)
		return
	from Game.Item import ItemConfig
	packMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	DiveItemCoding = cfg.GetResolve
	Divecfg = ItemConfig.ItemCfg_Dict.get(coding)
	DiveName = Divecfg.name
	AfterDivecfg = ItemConfig.ItemCfg_Dict.get(DiveItemCoding)
	AfterDiveName=AfterDivecfg.name
	#背包该物品数量不足
	if packMgr.ItemCnt(coding) < 1 :
		return
	#背包剩余空格不足
	if not role.FindItem(DiveItemCoding) and  role.PackageEmptySize() < 1 :
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return 
	needRMB = cfg.CostRMB
	#分解所需的神石不足
	if needRMB > role.GetUnbindRMB() :
		return
	with GemResolve_log:
		role.DelItem(coding, 1)  
		role.DecUnbindRMB(needRMB)
		role.AddItem(DiveItemCoding, 2)
		role.Msg(2, 0, GlobalPrompt.Suc_Resovle % (DiveName,AfterDiveName))
	role.CallBackFunction(backid, 1)		

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Mosaic_Gem", "镶嵌宝石"), MosaicGem)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Synthetic_Gem", "宝石合成"), GemSynthetic)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Sealing_spirit_Gem", "宝石封灵"), SealingSpirit)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_GemLevelUp_Gem", "宝石升级"), GemLevelUp)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Gemgetoff_Gem", "宝石卸下"), GetoffGem)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_ALLlevelUp_Gem", "一键合成宝石"), AllGemLevelUp)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Gem_OnForge", "宝石_请求宝石锻造"), OnForge)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Gem_OnTransform", "宝石_请求转换锻造石"), OnTransform)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Resolve", "宝石分解"), GemResolve)
		
	
