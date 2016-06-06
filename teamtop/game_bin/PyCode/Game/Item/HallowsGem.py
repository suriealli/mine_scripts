#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.HallowsGem")
#===============================================================================
# 圣器雕纹
#===============================================================================
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumTempObj,EnumInt8,EnumInt32

if "_HasLoad" not in dir():
	Hallows_Gem_Dict = {}		#雕纹配置
	Hallows_Spirit_Dict = {}	#雕纹封印配置
	
	MIN_LEVEL_GEM = 80			#雕纹开启的最低等级
	MIN_LEVEL_SEALING = 80		#封印的最低等级
	MAX_SEALING_LEVEL = 12		#封印最高可达多少级
	#日志
	Hallows_MosaicGem_log = AutoLog.AutoTransaction("Hallows_MosaicGem_log", "雕纹镶嵌")
	Hallows_GemSynthetic_log = AutoLog.AutoTransaction("Hallows_GemSynthetic_log", "雕纹合成")
	Hallows_GetoffGem_log = AutoLog.AutoTransaction("Hallows_GetoffGem_log", "雕纹卸下")
	Hallows_GemLevelup_log = AutoLog.AutoTransaction("Hallows_GemLevelup_log", "雕纹升级")
	Hallows_GemSealing_log = AutoLog.AutoTransaction("Hallows_GemSealing_log", "雕纹封印")

def GetAllGem(role):
	'''
	获取背包所有的雕纹,并按雕纹类型分类
	'''
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	gem_coding_by_type = {} #key为雕纹类型
	gem_coding_list = Hallows_Gem_Dict.values()
	for coding, _ in packageMgr.codingGather.iteritems():
		if coding in gem_coding_list:
			cfg = Hallows_Gem_Dict.get(coding)
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
	雕纹卸下
	@param role:
	@param msg:
	'''
	backId, (eId, location) = msg #从下标1开始
	if location <= 0:
		return
	hallows = role.FindGlobalProp(eId)
	if not hallows:
		return
	#获取已镶嵌的雕纹
	gem_list = hallows.GetHallowsGem()
	#没镶嵌雕纹
	if not gem_list:
		return
	#下标不存在
	if location > len(gem_list):
		return
	with Hallows_GetoffGem_log:
		del_gem = hallows.delGembyLocation(location)
		if del_gem:#删除成功
			role.AddItem(del_gem, 1)
	#判断重算属性
	hallows.ResetGemPro()
	if hallows.owner:
		#设置装备属性重算
		hallows.owner.GetPropertyGather().ReSetRecountHallowsGemFlag()
	#将新的雕纹列表发给客户端
	gem_list = hallows.GetHallowsGem()
	role.CallBackFunction(backId, gem_list)
	
def MosaicGem(role, msg):
	'''
	雕纹镶嵌
	@param role:
	@param msg:
	'''
	backId, (eId, GemCoding) = msg
	global MIN_LEVEL_GEM
	if role.GetLevel() < MIN_LEVEL_GEM:
		return
	hallows = role.FindGlobalProp(eId)
	if not hallows:
		return
	if role.ItemCnt(GemCoding) < 1:
		return
	global Hallows_Gem_Dict
	cfg = Hallows_Gem_Dict.get(GemCoding)
	if not cfg:
		print "GE_EXC, can not find cfg by (%s) in Hallows_Gem_Dict" % GemCoding
		return
	
	#获取已镶嵌的雕纹
	gem_list = hallows.GetHallowsGem()
	holed = len(gem_list) #已镶嵌的数量
	cfg_hole = hallows.cfg.hole #装备可镶嵌的孔数
	if holed >= cfg_hole:#已镶嵌满
		return
	gemType = cfg.GemType#雕纹类型

	for gem in gem_list:
		if gem[1] == gemType:#存在相同类型的雕纹
			return
	
	with Hallows_MosaicGem_log:
		role.DelItem(GemCoding, 1)
		hallows.SetHallowsGem(GemCoding, gemType, cfg.GemLevel)
	#判断重算属性
	hallows.ResetGemPro()
	if hallows.owner:
		hallows.owner.GetPropertyGather().ReSetRecountHallowsGemFlag()
	gem_list = hallows.GetHallowsGem()
	role.CallBackFunction(backId, gem_list)
				
def GemSynthetic(role, msg):
	'''
	雕纹合成
	@param role:
	@param msg:
	'''
	backId, (coding, num) = msg #coding雕纹材料ID，num是需要合成的数目
	if num <= 0:
		return
	global Hallows_Gem_Dict
	cfg = Hallows_Gem_Dict.get(coding)
	if not cfg:
		print "GE_EXC, can not find cfg by (%s) in Hallows_Gem_Dict,GemSynthetic" % coding
		return
	if not cfg.CanMix:#检测材料是否能合成
		return
	if not cfg.NextGemID:#下一级的雕纹是否存在
		return
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	need_num = cfg.MixNum * num
	if packageMgr.ItemCnt(coding) < need_num:
		return
	need_money = cfg.MixMoney * num
	if role.GetMoney() < need_money:
		return
	
	with Hallows_GemSynthetic_log:
		if role.DelItem(coding,need_num) < need_num:
			return
		role.DecMoney(need_money)
		role.AddItem(cfg.NextGemID, num)
	
	role.CallBackFunction(backId, 1)
	
def AllGemLevelUp(role, msg):
	'''
	雕纹一键合成
	@param role:
	@param msg:
	'''
	backId, gem_list = msg
	if role.GetVIP() < EnumGameConfig.VIP_ALL_SYNTHETI:
		return
	tbool = False
	for Hcoding in gem_list:
		cfg = Hallows_Gem_Dict.get(Hcoding)
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
	获取可以合成这种雕纹的个数
	@param role:
	@param Hcoding:
	'''	
	cfg = Hallows_Gem_Dict.get(Hcoding)
	if not cfg:
		return
	needNum = cfg.decompositionNum
	lowerlist = cfg.lowerlist
	if not lowerlist:
		return
	new_cnt = 0
	if type(lowerlist) == int:
		new_cfg = Hallows_Gem_Dict.get(lowerlist)
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
			lower_cfg = Hallows_Gem_Dict.get(coding)
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
	合成指定个数雕纹
	@param role:
	@param Hcoding:
	@param num:
	'''
	cfg = Hallows_Gem_Dict.get(Hcoding)
	if not cfg:
		return
	lowerlist = cfg.lowerlist
	if not lowerlist:
		return
	needNum = cfg.decompositionNum * num
	del_list = []
	if type(lowerlist) == int:#升级成2级雕纹
		new_cfg = Hallows_Gem_Dict.get(lowerlist)
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
	elif type(lowerlist) == list:#升级成>2级雕纹
		left_cnt = needNum
		tbool = False
		for coding in lowerlist:
			cfg_cnt = role.ItemCnt(coding)
			if not cfg_cnt:
				continue
			new_cfg = Hallows_Gem_Dict.get(coding)
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
	with Hallows_GemLevelup_log:
		for item in del_list:
			if not item[1]:
				continue
			if role.DelItem(item[0], item[1]) < item[1]:
				return
		role.AddItem(Hcoding, num)
		
		return True
	
def GemLevelUp(role, msg):
	'''
	雕纹升级
	@param role:
	@param msg:
	'''
	backId, (eId, index) = msg #Hcoding为目标等级的雕纹,Ocoding为当前雕纹等级
	if index < 1 : return

	hallows = role.FindGlobalProp(eId)
	if not hallows : return
	gem_list = hallows.GetHallowsGem()
	if len(gem_list) < index:
		return
	
	nowCoding, Otype, level  = gem_list[index - 1]
	
	nowCodingCfg = Hallows_Gem_Dict.get(nowCoding)
	if not nowCodingCfg: 
		print "GE_EXC, GemLevelUp nowCoding(%s)" % nowCoding
		return
	Hcoding = nowCodingCfg.NextGemID
	cfg = Hallows_Gem_Dict.get(Hcoding)
	if not cfg : return
	lowerlist = cfg.lowerlist
	#下一级雕纹竟然是一级雕纹，有问题
	if not lowerlist : return
	
	if Otype != cfg.GemType:#雕纹类型不同
		return
	
	if role.ItemCnt(nowCoding) >= 1:
		with Hallows_GemLevelup_log:
			role.DelItem(nowCoding, 1)
			hallows.LevelUpHallowsGem(index, Hcoding, cfg.GemType, cfg.GemLevel)
	
		#判断重算属性
		hallows.ResetGemPro()
		if hallows.owner:
			#设置装备属性重算
			hallows.owner.GetPropertyGather().ReSetRecountHallowsGemFlag()
		role.CallBackFunction(backId, 1)
		
		return
	elif level == 1:
		#一级雕纹，并且没有其他的一级雕纹了
		return
	
	#总共需要的一级雕纹数量
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
		new_cfg = Hallows_Gem_Dict.get(coding)
		if not new_cfg:
			print "GE_EXC, error GemLevelUp no cfg coding(%s)" % coding
			continue
		#计算相当于多少个一级雕纹
		new_cnt = new_cfg.decompositionNum * itemCnt
		if new_cnt >= needNum:
			#计算真正需要的雕纹数量
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
	with Hallows_GemLevelup_log:
		for item in del_list:
			if not item[1]:
				continue
			if role.DelItem(item[0], item[1]) < item[1]:
				print "GE_EXC, error in GemLevelUp DelItem （%s）" % role.GetRoleID()
				return
		hallows.LevelUpHallowsGem(index, Hcoding, cfg.GemType, cfg.GemLevel)			
	#判断重算属性
	hallows.ResetGemPro()
	if hallows.owner:
		#设置装备属性重算
		hallows.owner.GetPropertyGather().ReSetRecountHallowsGemFlag()
		
	role.CallBackFunction(backId, 1)

def SealingSpirit(role, msg):
	'''
	封灵
	@param role:
	@param msg:
	'''
	
	backId, _ = msg
	global MIN_LEVEL_SEALING
	
	if role.GetLevel() < MIN_LEVEL_SEALING:
		return
	global Hallows_Spirit_Dict
	global MAX_SEALING_LEVEL
	#获取玩家的封灵
	Sealing_level = role.GetI8(EnumInt8.HallowsSealingSpiritID)	
	cfg = Hallows_Spirit_Dict.get(Sealing_level)
	if not cfg:
		print "GE_EXC,can not find cfg by SealingLevel=(%s) in Hallows_Spirit_Dict" % Sealing_level
		return
	if not cfg.NextLevel:#已是最高级
		return
	coding = cfg.needItem
	cnt = role.ItemCnt(coding)
	if cnt <= 0:
		return
	
	exp = role.GetI32(EnumInt32.HallowsSealExp)
	need_cnt = (cfg.needExp - exp) / cfg.addExp
	
	with Hallows_GemSealing_log:
		if cnt < need_cnt:
			role.DelItem(coding, cnt)
			role.IncI32(EnumInt32.HallowsSealExp, cnt * cfg.addExp)
		else:
			role.DelItem(coding, need_cnt)
			#升级
			role.IncI8(EnumInt8.HallowsSealingSpiritID, 1)
			#将经验清0
			role.SetI32(EnumInt32.HallowsSealExp, 0)
			#重算属性
			HallowsMgr = role.GetTempObj(EnumTempObj.enRoleHallowsMgr)
			for Hallowfact in HallowsMgr.objIdDict.itervalues():
				Hallowfact.ResetGemPro()
				#设置圣器属性重算
				Hallowfact.owner.GetPropertyGather().ReSetRecountHallowsGemFlag()
			AllHero = role.GetAllHero()
			for hero in AllHero.values():
				heroHallowsMgr = hero.HallowsMgr
				if not heroHallowsMgr : continue
				for Hallowfact in heroHallowsMgr.objIdDict.itervalues():
					Hallowfact.ResetGemPro()
					#设置圣器属性重算
					Hallowfact.owner.GetPropertyGather().ReSetRecountHallowsGemFlag()
	role.CallBackFunction(backId, 1)
	
if "_HasLoad" not in dir():
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Hallows_Mosaic_Gem", "雕纹镶嵌"), MosaicGem)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Hallows_Synthetic_Gem", "雕纹合成"), GemSynthetic)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Hallows_GemLevelUp_Gem", "雕纹升级"), GemLevelUp)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Hallows_Gemgetoff_Gem", "雕纹卸下"), GetoffGem)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Hallows_ALLlevelUp_Gem", "雕纹一键合成"), AllGemLevelUp)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Hallows_Sealing_spirit_Gem", "雕纹封印"), SealingSpirit)
	
	