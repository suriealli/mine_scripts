#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ArtifactGem")
#===============================================================================
# 神器符石
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumTempObj, EnumInt8, EnumInt32
from Game.Activity.ProjectAct import ProjectAct, EnumProActType

if "_HasLoad" not in dir():
	Artifact_Gem_Dict = {} #符石配置
	Sealing_Spirit_Dict = {} #封灵配置
	
	MIN_LEVEL_SEALING = 60 #封灵的最低等级
	MAX_SEALING_LEVEL = 12 #封灵最高可达多少级
	#日志
	Artifact_MosaicGem_log= AutoLog.AutoTransaction("Artifact_MosaicGem_log", "符石镶嵌")
	Artifact_GemSynthetic_log = AutoLog.AutoTransaction("Artifact_GemSynthetic_log", "符石合成")
	Artifact_GetoffGem_log = AutoLog.AutoTransaction("Artifact_GetoffGem_log", "下符石")
	Artifact_GemSealing_log = AutoLog.AutoTransaction("Artifact_GemSealing_log", "符石封印")
	Artifact_GemLevelup_log = AutoLog.AutoTransaction("Artifact_GemLevelup_log", "封印升级")
			
def GetoffGem(role, msg):	
	'''
	取下
	@param role:
	@param msg:
	'''
	backId, (eId, location) = msg #从下标1开始
	if location <= 0:
		return
	Artifact = role.FindGlobalProp(eId)
	if not Artifact:
		return
	#获取已镶嵌的
	gem_list = Artifact.GetArtifactGem()
	#没镶嵌
	if not gem_list:
		return
	#下标不存在
	if location > len(gem_list):
		return
	with Artifact_GetoffGem_log:
		del_gem = Artifact.delGembyLocation(location)
		if del_gem:#删除成功
			role.AddItem(del_gem, 1)
		else:
			print "GE_EXC, GetoffGem, delGembyLocation error "
			return
	#判断重算属性
	Artifact.ResetGemPro()
	if Artifact.owner:
		#设置神器属性重算
		Artifact.owner.GetPropertyGather().ReSetRecountArtifactGemFlag()
	#将新的列表发给客户端
	gem_list = Artifact.GetArtifactGem()
	role.CallBackFunction(backId, gem_list)
	
def MosaicGem(role, msg):
	'''
	镶嵌
	@param role:
	@param msg:
	'''
	backId, (eId, GemCoding) = msg
	global MIN_LEVEL_SEALING
	if role.GetLevel() < MIN_LEVEL_SEALING:
		return
	Artifact = role.FindGlobalProp(eId)
	if not Artifact:
		return
	if not Artifact.cfg.Mosaic:
		return
	if role.ItemCnt(GemCoding) < 1:
		return
	global Artifact_Gem_Dict
	cfg = Artifact_Gem_Dict.get(GemCoding)
	if not cfg:
		print "GE_EXC, can not find cfg by (%s) in Artifact_Gem_Dict" % GemCoding
		return
	
	#获取已镶嵌的
	gem_list = Artifact.GetArtifactGem()
	holed = len(gem_list) #已镶嵌的数量
	cfg_hole = Artifact.cfg.holeNum #神器可镶嵌的孔数
	if holed >= cfg_hole:#已镶嵌满
		return
	gemType = cfg.GemType#类型

	for gem in gem_list:
		if gem[1] == gemType:#存在相同类型的
			return
	
	with Artifact_MosaicGem_log:
		role.DelItem(GemCoding, 1)
		Artifact.SetArtifactGem(GemCoding, gemType, cfg.GemLevel)
	#判断重算属性
	Artifact.ResetGemPro()
	if Artifact.owner:
		Artifact.owner.GetPropertyGather().ReSetRecountArtifactGemFlag()
	gem_list = Artifact.GetArtifactGem()
	role.CallBackFunction(backId, gem_list)
				
def GemSynthetic(role, msg):
	'''
	合成
	@param role:
	@param msg:
	'''
	backId, (coding, num) = msg #coding材料ID，num是需要合成的数目
	if num <= 0:
		return
	global Artifact_Gem_Dict
	cfg = Artifact_Gem_Dict.get(coding)
	if not cfg:
		print "GE_EXC, can not find cfg by (%s) in Artifact_Gem_Dict,GemSynthetic" % coding
		return
	if not cfg.CanMix:#检测材料是否能合成
		return
	if not cfg.NextGemID:#下一级的是否存在
		return
	packageMgr = role.GetTempObj(EnumTempObj.enPackMgr)
	need_num = cfg.MixNum * num
	if packageMgr.ItemCnt(coding) < need_num:
		return
	need_money = cfg.MixMoney * num
	if role.GetMoney() < need_money:
		return
	
	with Artifact_GemSynthetic_log:
		if role.DelItem(coding,need_num) < need_num:
			return
		role.DecMoney(need_money)
		role.AddItem(cfg.NextGemID, num)
	#专题活动相关
	if cfg.GemLevel >= 4:
		ProjectAct.GetFunByType(EnumProActType.ProjectFuwenEvent, [role, cfg.GemLevel+1, num])
		if Environment.EnvIsNA():
			KaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
			KaiFuActMgr.FuWenSyn(cfg.GemLevel+1)
			#北美通用活动
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.Fuwensynthetic(cfg.GemLevel+1, num)
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
	global Sealing_Spirit_Dict
	global MAX_SEALING_LEVEL
	#获取玩家的封灵
	Sealing_level = role.GetI8(EnumInt8.ArtifactSealingID)	
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
	
	exp = role.GetI32(EnumInt32.ArtifactSealExp)
	need_cnt = (cfg.needExp - exp) / cfg.addExp
	
	with Artifact_GemSealing_log:
		if cnt < need_cnt:
			role.DelItem(coding, cnt)
			role.IncI32(EnumInt32.ArtifactSealExp, cnt * cfg.addExp)
		else:
			role.DelItem(coding, need_cnt)
			#升级
			role.IncI8(EnumInt8.ArtifactSealingID, 1)
			#将经验清0
			role.SetI32(EnumInt32.ArtifactSealExp, 0)
			#重算属性
			ArtifactMgr = role.GetTempObj(EnumTempObj.enRoleArtifactMgr)
			for Artifact in ArtifactMgr.objIdDict.itervalues():
				Artifact.ResetGemPro()
				#设置神器属性重算
				Artifact.owner.GetPropertyGather().ReSetRecountArtifactGemFlag()
			AllHero = role.GetAllHero()
			for hero in AllHero.values():
				heroArtifactMgr = hero.ArtifactMgr
				if not heroArtifactMgr : continue
				for Artifact in heroArtifactMgr.objIdDict.itervalues():
					Artifact.ResetGemPro()
					#设置神器属性重算
					Artifact.owner.GetPropertyGather().ReSetRecountArtifactGemFlag()
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
		cfg = Artifact_Gem_Dict.get(Hcoding)
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
	获取可以合成这种的个数
	@param role:
	@param Hcoding:
	'''	
	cfg = Artifact_Gem_Dict.get(Hcoding)
	if not cfg:
		return
	needNum = cfg.decompositionNum
	lowerlist = cfg.lowerlist
	if not lowerlist:
		return
	new_cnt = 0
	if type(lowerlist) == int:
		new_cfg = Artifact_Gem_Dict.get(lowerlist)
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
			lower_cfg = Artifact_Gem_Dict.get(coding)
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
	合成指定个数
	@param role:
	@param Hcoding:
	@param num:
	'''
	cfg = Artifact_Gem_Dict.get(Hcoding)
	if not cfg:
		return
	lowerlist = cfg.lowerlist
	if not lowerlist:
		return
	needNum = cfg.decompositionNum * num
	del_list = []
	if type(lowerlist) == int:#升级成2级
		new_cfg = Artifact_Gem_Dict.get(lowerlist)
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
	elif type(lowerlist) == list:#升级成>2级
		left_cnt = needNum
		tbool = False
		for coding in lowerlist:
			cfg_cnt = role.ItemCnt(coding)
			if not cfg_cnt:
				continue
			new_cfg = Artifact_Gem_Dict.get(coding)
			if not new_cfg:
				continue
			if new_cfg.decompositionNum:
				new_cnt = new_cfg.decompositionNum * cfg_cnt
			else:
				new_cnt = cfg_cnt
			if new_cnt >= left_cnt:
				cnt = 0
				if new_cfg.decompositionNum:
					cnt = left_cnt / new_cfg.decompositionNum
				else:
					cnt = left_cnt
				del_list.append((coding, cnt))
				tbool = True
				break
			else:
				del_list.append((coding, cfg_cnt))	
				left_cnt -= new_cnt
	if not tbool:
		return
	with Artifact_GemLevelup_log:
		for item in del_list:
			if not item[1]:
				continue
			if role.DelItem(item[0], item[1]) < item[1]:
				return
		role.AddItem(Hcoding, num)
		#专题活动相关
		if cfg.GemLevel >= 5:
			ProjectAct.GetFunByType(EnumProActType.ProjectFuwenEvent, [role, cfg.GemLevel, num])
			if Environment.EnvIsNA():
				KaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
				KaiFuActMgr.FuWenSyn(cfg.GemLevel)
				#北美通用活动
				HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
				HalloweenNAMgr.Fuwensynthetic(cfg.GemLevel, num)
		return True
	
def GemLevelUp(role, msg):
	'''
	升级
	@param role:
	@param msg:
	'''
	backId, (eId, index) = msg #Hcoding为目标等级的,Ocoding为当前等级	
	if index < 1 : return
	Artifact = role.FindGlobalProp(eId)
	if not Artifact : return

	gem_list = Artifact.GetArtifactGem()
	if len(gem_list) < index:
		return

	nowCoding, Otype, level = gem_list[index - 1]

	Nowcfg = Artifact_Gem_Dict.get(nowCoding)
	if not Nowcfg:
		print "GE_EXC,Artifact.GemLevelUp can not find (%s)" % nowCoding
		return
	Hcoding = Nowcfg.NextGemID
	cfg = Artifact_Gem_Dict.get(Hcoding)
	if not cfg : return
	lowerlist = cfg.lowerlist
	if not lowerlist:
		return
	if Otype != cfg.GemType:#宝石类型不同
		return
	if role.ItemCnt(nowCoding) >= 1:
		with Artifact_GemLevelup_log:
			role.DelItem(nowCoding, 1)
			Artifact.ChangeArtifactGem(index, Hcoding, cfg.GemType, cfg.GemLevel)	
		#判断重算属性
		Artifact.ResetGemPro()
		if Artifact.owner:
			#设置神器属性重算
			Artifact.owner.GetPropertyGather().ReSetRecountArtifactGemFlag()
		role.CallBackFunction(backId, 1)
		if cfg.GemLevel >= 5:
			ProjectAct.GetFunByType(EnumProActType.ProjectFuwenEvent, [role, cfg.GemLevel, 1])
			if Environment.EnvIsNA():
				KaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
				KaiFuActMgr.FuWenSyn(cfg.GemLevel)
				#北美通用活动
				HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
				HalloweenNAMgr.Fuwensynthetic(cfg.GemLevel, 1)
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
		new_cfg = Artifact_Gem_Dict.get(coding)
		if not new_cfg:
			print "GE_EXC, error Artifact.GemLevelUp no cfg coding(%s)" % coding
			continue
		#计算相当于多少个一级符文
		new_cnt = new_cfg.decompositionNum * itemCnt
		if new_cnt >= needNum:
			#计算真正需要的符文数量
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
	with Artifact_GemLevelup_log:
		for item in del_list:
			if not item[1]:
				continue
			if role.DelItem(item[0], item[1]) < item[1]:
				print "GE_EXC, error in Artifact.GemLevelUp DelItem （%s）" % role.GetRoleID()
				return
		Artifact.ChangeArtifactGem(index, Hcoding, cfg.GemType, cfg.GemLevel)			
	#判断重算属性
	Artifact.ResetGemPro()
	if Artifact.owner:
		#设置神器属性重算
		Artifact.owner.GetPropertyGather().ReSetRecountArtifactGemFlag()
	#专题活动相关
	if cfg.GemLevel >= 5:
		ProjectAct.GetFunByType(EnumProActType.ProjectFuwenEvent, [role, cfg.GemLevel, 1])
		if Environment.EnvIsNA():
			KaiFuActMgr = role.GetTempObj(EnumTempObj.KaiFuActMgr)
			KaiFuActMgr.FuWenSyn(cfg.GemLevel)
			#北美通用活动
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.Fuwensynthetic(cfg.GemLevel, 1)
	role.CallBackFunction(backId, 1)

		
if "_HasLoad" not in dir():
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Artifact_Mosaic_Gem", "符石镶嵌"), MosaicGem)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Artifact_Synthetic_Gem", "符石合成"), GemSynthetic)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Artifact_Sealing_spirit_Gem", "符石封印"), SealingSpirit)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Artifact_GemLevelUp_Gem", "符石升级"), GemLevelUp)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Artifact_Gemgetoff_Gem", "符石卸下"), GetoffGem)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_Artifact_ALLlevelUp_Gem", "符石一键合成"), AllGemLevelUp)
