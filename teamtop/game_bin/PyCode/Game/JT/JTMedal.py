#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.JT.JTMedal")
#===============================================================================
# 勋章系统
#===============================================================================
import cRoleMgr
import Environment
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from Game.Role.Data import EnumInt32, EnumInt16, EnumObj
from Game.Role import Event
from Game.Property import PropertyEnum
from Game.Item import ItemConfig
from Game.JT import JTConfig


if "_HasLoad" not in dir():
	
	DefensePt = PropertyEnum.defense_m, PropertyEnum.defense_p
	#消息
	SyncCrystalData = AutoMessage.AllotMessage("JT_SyncCrystalData", "同步勋章数据")
	SyncCrystalSealingData = AutoMessage.AllotMessage("JT_SyncCrystalSealingData", "同步勋章封灵数据")
	
	#日志
	Tra_JTMedal_RequestWearMedal = AutoLog.AutoTransaction("Tra_JTMedal_RequestWearMedal", "跨服竞技场请求佩戴勋章")
	Tra_JTMedal_CrystalInlay = AutoLog.AutoTransaction("Tra_JTMedal_CrystalInlay", "跨服竞技场勋章晶石镶嵌")
	Tra_JTMedal_CrystalUpLevel = AutoLog.AutoTransaction("Tra_JTMedal_CrystalUpLevel", "跨服竞技场勋章晶石升级")
	Tra_JTMedal_CrystalSealingUp = AutoLog.AutoTransaction("Tra_JTMedal_CrystalSealingUp", "跨服竞技场勋章封灵升级")


#==========================================
#晶石相关 About crystal
#==========================================
def CrystalInlay(role, msg):
	'''
	晶石镶嵌
	'''
	coding = msg
	
	medalLevel = role.GetI16(EnumInt16.JTMedalLevel)
	medalConfig = JTConfig.JTMedalConfigDict.get(medalLevel)
	if medalConfig is None:
		return
	
	crystalConfig = ItemConfig.JTCrystalConfigDict.get(coding)
	if crystalConfig is None:
		return
	
	postion = crystalConfig.crystalType
	if postion not in medalConfig.crystalPostion:
		return
	
	medalData = role.GetObj(EnumObj.JTMedalCrystal).setdefault("medal", {})
	#已经镶嵌了晶石
	if postion in medalData:
		return
	
	#用于镶嵌的晶石等级必须为1
	if crystalConfig.crystalLevel != 1:
		return
	
	#角色没有这个晶石
	if role.ItemCnt(coding) < 1:
		role.Msg(2, 0, GlobalPrompt.JTItemLackOf)
		return
	
	#这里增加日志
	with Tra_JTMedal_CrystalInlay:
		if role.DelItem(coding, 1) < 1:
			return
		medalData[postion] = coding
	role.GetPropertyGather().ReSetRecountJTMedalFlag()
	role.SendObj(SyncCrystalData, medalData)
	role.Msg(2, 0, GlobalPrompt.JTCrystalInlayOk)
	

def CrystalUpLevel(role, msg):
	'''
	晶石升级
	'''
	postion = msg
	medallevel = role.GetI16(EnumInt16.JTMedalLevel)
	medalConfig = JTConfig.JTMedalConfigDict.get(medallevel)
	if medalConfig is None:
		return
	
	if postion not in medalConfig.crystalPostion:
		return
	
	medalData = role.GetObj(EnumObj.JTMedalCrystal).setdefault("medal", {})
	#该位置没有镶嵌晶石则不能升级
	if postion not in medalData:
		return
	
	oldCrystalCoding = medalData[postion]
	crystalConfig = ItemConfig.JTCrystalConfigDict.get(oldCrystalCoding)
	if crystalConfig is None:
		return
	
	newCoding = crystalConfig.netxLevel
	newConfig = ItemConfig.JTCrystalConfigDict.get(newCoding)
	if newConfig is None:
		return
	
	#已经到了最高级
	if newCoding <= 0:
		return
	
	#等价的该种晶石的最低等级晶石的数量
	needLowestCnt = newConfig.equalLowest
	lowerList = newConfig.lowerList
	delList = []
	isEnough = False
	
	if role.ItemCnt(newCoding) >= 1:
		delList.append((newCoding, 1))
		isEnough = True

	else:
		stillNeedCnt = needLowestCnt
		JTG = ItemConfig.JTCrystalConfigDict.get
		for theCoding in lowerList:
			cnt = role.ItemCnt(theCoding)
			if cnt <= 0:
				continue
			theConfig = JTG(theCoding)
			if not theConfig:
				continue
			
			if theConfig.equalLowest <= 0 :
				print "GE_EXC, theConfig.equalLowest can not be zero!"
				return
			
			#等价最低等级晶石数
			equalCnt = theConfig.equalLowest * cnt
			
			if equalCnt >= stillNeedCnt:
				#这里断定肯定可以整除，否则必然是配置表有问题
				cnt = stillNeedCnt / theConfig.equalLowest
				delList.append((theCoding, cnt))
				isEnough = True
				break
			
			delList.append((theCoding, cnt))
			stillNeedCnt = stillNeedCnt - equalCnt
		
	if isEnough is False:
		role.Msg(2, 0, GlobalPrompt.JTItemLackOf)
		return
	
	#这里添加日志
	with Tra_JTMedal_CrystalUpLevel:
		for itemCoding, itemCnt in delList:
			if role.DelItem(itemCoding, itemCnt) < itemCnt:
				return
		medalData[postion] = newCoding
	
	role.GetPropertyGather().ReSetRecountJTMedalFlag()
	role.SendObj(SyncCrystalData, medalData)
	role.Msg(2, 0, GlobalPrompt.JTCrystalUpLevelOk)


def CrystalSealing(role, msg):
	'''
	晶石光环升级
	'''
	sealingData = role.GetObj(EnumObj.JTMedalCrystal).setdefault("sealing", [0, 0])
	nowLevel, nowExp = sealingData
	config = ItemConfig.JTCrystalSealingConfigDict.get(nowLevel)
	if config is None:
		return
	
	#已经是最高级了
	if config.highestlevel == 1:
		return

	coding = config.needItem
	
	theCnt = role.ItemCnt(coding)
	if theCnt < 1:
		return
	
	needExp = config.upLevelExp - nowExp
	needCnt = needExp / config.incExp
	levelUp = False
	
	with Tra_JTMedal_CrystalSealingUp:
		if theCnt >= needCnt:
			role.DelItem(coding, needCnt)
			#等级增加
			sealingData[0] = sealingData[0] + 1
			#经验清零
			sealingData[1] = 0
			
			levelUp = True
		else:
			if theCnt > 0:
				role.DelItem(coding, theCnt)
				sealingData[1] = sealingData[1] + theCnt * config.incExp
	
	role.GetPropertyGather().ReSetRecountJTMedalFlag()
	role.SendObj(SyncCrystalSealingData, sealingData)
	
	if levelUp:
		role.Msg(2, 0, GlobalPrompt.JTSealingOk_1 % sealingData[0])
	else:
		role.Msg(2, 0, GlobalPrompt.JTSealingOk_2)
	


def OpenJTMedalPanel(role, msg):
	'''
	客户端请求打开勋章面板
	'''
	medalData = role.GetObj(EnumObj.JTMedalCrystal).get("medal", {})
	sealingData = role.GetObj(EnumObj.JTMedalCrystal).get("sealing", [0, 0])
	role.SendObj(SyncCrystalData, medalData)
	role.SendObj(SyncCrystalSealingData, sealingData)


def RequestWearMedal(role, msg):
	'''
	客户端请求佩戴勋章
	@param role:
	@param msg:
	'''
	#当前佩戴的就是这个勋章
	nowLevel = role.GetI16(EnumInt16.JTMedalLevel)
	#区分是第一次激活还是之后的升级
	isActive = False
	if nowLevel == 0:
		isActive = True
		
	newLevel = nowLevel + 1
	
	if newLevel not in JTConfig.JTMedalConfigDict:
		return
	
	config = JTConfig.JTMedalConfigDict.get(newLevel, None)
	if config == None:
		print "GE_EXC, error while config = JTMedalConfig.JTMedalConfigDict.get(medal_level, None), no such medal_id(%s)" % newLevel
		return
	#功勋达不到条件
	if role.GetI32(EnumInt32.JTExp) < config.needJTexp:
		return
	with Tra_JTMedal_RequestWearMedal:
		#设置当前佩戴的勋章的等级
		role.SetI16(EnumInt16.JTMedalLevel, newLevel)
	#设置属性重算
	role.GetPropertyGather().ReSetRecountJTMedalFlag()
	
	if isActive:
		role.Msg(2, 0, GlobalPrompt.JT_ActiveMedalOkay)
	else:
		role.Msg(2, 0, GlobalPrompt.JT_UplevelMedalOkay)


def GetMedalPropertyDict(role):
	'''
	获取当前勋章的属性字典
	@param role:
	'''
	medalProptyDict = {}
	MPG = medalProptyDict.get
	medalData = role.GetObj(EnumObj.JTMedalCrystal).get('medal', {})
	sealingData = role.GetObj(EnumObj.JTMedalCrystal).setdefault("sealing", [0, 0])
	nowLevel, _ = sealingData
	sealingCfg = ItemConfig.JTCrystalSealingConfigDict.get(nowLevel, None)
	if sealingCfg is None:
		return medalProptyDict
	
	addOnDict = sealingCfg.addOn
	JJCG = ItemConfig.JTCrystalConfigDict.get
	for coding in medalData.itervalues():
		crystalCfg = JJCG(coding)
		if crystalCfg is None:
			continue
		
		pt = crystalCfg.pt
		pv = crystalCfg.pv
		level = crystalCfg.crystalLevel
		if not pt or not pv:
			continue
		if pt not in DefensePt:
			addOn = addOnDict.get(level, 0)
			medalProptyDict[pt] = MPG(pt, 0) + int(pv * (1 + addOn / 100.0))
		else:
			medalProptyDict[pt] = MPG(pt, 0) + pv
	
	medal_level = role.GetI16(EnumInt16.JTMedalLevel)
	
	config = JTConfig.JTMedalConfigDict.get(medal_level, None)
	
	if config is None:
		return medalProptyDict
	for pt, pv in config.property_dict.iteritems():
		medalProptyDict[pt] = MPG(pt, 0) + pv

	return medalProptyDict


def SyncOtherData(role , param):
	medalData = role.GetObj(EnumObj.JTMedalCrystal).get("medal", {})
	sealingData = role.GetObj(EnumObj.JTMedalCrystal).get("sealing", [0, 0])
	role.SendObj(SyncCrystalData, medalData)
	role.SendObj(SyncCrystalSealingData, sealingData)


if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.IsDevelop or Environment.EnvIsNA() or Environment.EnvIsRU() or Environment.EnvIsPL()) and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncOtherData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_RequestWearMedal", "跨服竞技场勋章系统请求佩戴勋章"), RequestWearMedal)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_CrystalInlay", "跨服竞技场勋章系统请求镶嵌晶石"), CrystalInlay)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_CrystalUpLevel", "跨服竞技场勋章系统请求升级晶石"), CrystalUpLevel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("JT_CrystalSealing", "跨服竞技场勋章系统请求封灵"), CrystalSealing)
