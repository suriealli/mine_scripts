#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Marry.WeddingRing")
#===============================================================================
# 婚戒
#===============================================================================
import random
import cRoleMgr
import Environment
from Common.Other import GlobalPrompt, EnumGameConfig, EnumSocial
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt16, EnumInt32, EnumInt8, EnumObj
from Game.Marry import MarryConfig
from Game.Role import Event
from Game.Activity.ProjectAct import ProjectAct, EnumProActType

if "_HasLoad" not in dir():
	WeddingProPercent = AutoMessage.AllotMessage("WeddingProPercent", "戒灵属性")
	WeddingSkill = AutoMessage.AllotMessage("WeddingSkill", "夫妻技能")
	
	WeddingRingForging_Log = AutoLog.AutoTransaction("WeddingRingForging_Log", "婚戒培养")
	WeddingRingSoulSuccinct_Log = AutoLog.AutoTransaction("WeddingRingSoulSuccinct_Log", "戒灵精炼")
	
def AddTempExp(role, tempExp):
	#增加临时经验值
	#婚戒等阶
	nowWeddingRingID = role.GetI16(EnumInt16.WeddingRingID)
	if not nowWeddingRingID:
		return
	
	#婚戒配置
	cfg = MarryConfig.WeddingRing_Dict.get(nowWeddingRingID)
	if not cfg:
		print "GE_EXC, RequestNormalForging can not find nowWeddingRingID (%s) in WeddingRing_Dict" % nowWeddingRingID
		return
	
	#当前经验值
	nowExp = role.GetI32(EnumInt32.WeddingRingExp)
	nowTempExp = role.GetI32(EnumInt32.TempWedRingExp)
	nowExp += (tempExp + nowTempExp)
	
	#当前经验值大于当前阶最大经验值
	if nowExp >= cfg.maxExp:
		#下一阶配置
		nextCfg = MarryConfig.WeddingRing_Dict.get(cfg.nextID)
		if not nextCfg:
			return
		#升阶
		role.SetI16(EnumInt16.WeddingRingID, cfg.nextID)
		#计算经验
		role.SetI32(EnumInt32.WeddingRingExp, 0)
		#更新婚戒ID
		UpdateRingID(role)
		#重算婚戒属性
		role.ResetGlobalWeddingRingProperty()
		#是否可激活戒灵
		if nextCfg.activeRingSoul:
			ActiveRingSoul(role, nextCfg.activeRingSoul)
		#尝试激活夫妻技能
		ActiveFuqiSkill(role)
		#将临时经验设置为0
		role.SetI32(EnumInt32.TempWedRingExp, 0)
		
		from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
		if role.GetI16(EnumInt16.WeddingRingID) >= 11:
			WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Wed_Ring, role)
		#from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
		#LatestActivityMgr.GetFunByType(EnumLatestType.HunJie_Latest, role)
	else:
		role.IncI32(EnumInt32.TempWedRingExp, tempExp)
		
	role.Msg(2, 0, GlobalPrompt.WeddingRing_Exp_Tips % tempExp)
	
def ActiveWeddingRing(role):
	'''激活婚戒'''
	#结婚状态
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	
	#获取婚戒ID
	nowWeddingRingID = role.GetI16(EnumInt16.WeddingRingID)
	if nowWeddingRingID:
		#尝试激活使用夫妻双方婚戒ID激活的夫妻技能
		ActiveFuqiSkillEx(role)
		return
	
	#之前没有婚戒,激活婚戒
	role.SetI16(EnumInt16.WeddingRingID, 1)
	nowWeddingRingID = 1
	
	#婚戒配置
	cfg = MarryConfig.WeddingRing_Dict.get(nowWeddingRingID)
	if not cfg:
		print "GE_EXC, ActiveWeddingRing can not find nowWeddingRingID (%s) in WeddingRing_Dict" % nowWeddingRingID
		return
	
	#重算婚戒属性
	role.ResetGlobalWeddingRingProperty()
	
	#激活戒灵
	if cfg.activeRingSoul:
		ActiveRingSoul(role, cfg.activeRingSoul)
	
	#激活夫妻技能
	ActiveFuqiSkill(role)
	
def RequestNormalForging(role, msg):
	'''
	婚戒普通培养
	@param role:
	@param msg:
	'''
	#等级
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	
	#结婚状态
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	
	#婚戒等阶
	nowWeddingRingID = role.GetI16(EnumInt16.WeddingRingID)
	if not nowWeddingRingID:
		return
	
	#婚戒配置
	cfg = MarryConfig.WeddingRing_Dict.get(nowWeddingRingID)
	if not cfg:
		print "GE_EXC, RequestNormalForging can not find nowWeddingRingID (%s) in WeddingRing_Dict" % nowWeddingRingID
		return
	
	#当前经验值
	nowExp = role.GetI32(EnumInt32.WeddingRingExp)
	
	nowLevel = role.GetLevel()
	#经验满, 需要进阶或是最后一阶或等级不够
	if cfg.maxExp <= nowExp and (cfg.isUpGrade or cfg.nextID == -1 or nowLevel < cfg.upNeedLevel):
		return
	
	#物品
	if role.ItemCnt(EnumGameConfig.WeddingRingCoding) < 1:
		return
	
	#是否暴击
	critTrue = cfg.critTrue.RandomOne()
	
	with WeddingRingForging_Log:
		#扣物品
		role.DelItem(EnumGameConfig.WeddingRingCoding, 1)
	
	#暴击
	if critTrue:
		AddExp(role, nowExp, cfg, 2)
		role.Msg(2, 0, GlobalPrompt.WeddingRingCritTips)
	else:
		AddExp(role, nowExp, cfg, 1)
		role.Msg(2, 0, GlobalPrompt.WeddingRingNormalTips)
	#专题活动每日培养婚戒次数
	ProjectAct.GetFunByType(EnumProActType.ProjectRingEvent, (role, 1))

def AddExp(role, nowExp, cfg, beishu):
	#暴击获得两倍经验
	nowExp += cfg.addExp * beishu
	tempExp = role.GetI32(EnumInt32.TempWedRingExp)
	#当前经验值大于当前阶最大经验值
	if nowExp + tempExp >= cfg.maxExp:
		#需要升阶或是最后一阶
		if cfg.isUpGrade or cfg.nextID == -1:
			role.SetI32(EnumInt32.WeddingRingExp, cfg.maxExp)
			return
		#下一阶配置
		nextCfg = MarryConfig.WeddingRing_Dict.get(cfg.nextID)
		if not nextCfg:
			return
		#升阶
		role.SetI16(EnumInt16.WeddingRingID, cfg.nextID)
		#计算经验
		if tempExp:
			role.SetI32(EnumInt32.WeddingRingExp, 0)
			role.SetI32(EnumInt32.TempWedRingExp, 0)
		else:
			role.SetI32(EnumInt32.WeddingRingExp, nowExp - cfg.maxExp)
		#更新婚戒ID
		UpdateRingID(role)
		#重算婚戒属性
		role.ResetGlobalWeddingRingProperty()
		#是否可激活戒灵
		if nextCfg.activeRingSoul:
			ActiveRingSoul(role, nextCfg.activeRingSoul)
		#尝试激活夫妻技能
		ActiveFuqiSkill(role)
		from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
		if role.GetI16(EnumInt16.WeddingRingID) >= 11:
			WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Wed_Ring, role)
		#from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
		#LatestActivityMgr.GetFunByType(EnumLatestType.HunJie_Latest, role)
	else:
		role.SetI32(EnumInt32.WeddingRingExp, nowExp)
	
def RequestAdvancedForging(role, msg):
	'''
	婚戒高级培养
	@param role:
	@param msg:
	'''
	#等级
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	
	#结婚状态
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	
	#vip
	if role.GetVIP() < 4:
		return
	
	#婚戒等阶
	nowWeddingRingID = role.GetI16(EnumInt16.WeddingRingID)
	if not nowWeddingRingID:
		return
	
	#配置
	cfg = MarryConfig.WeddingRing_Dict.get(nowWeddingRingID)
	if not cfg:
		return
	
	#当前经验值
	nowExp = role.GetI32(EnumInt32.WeddingRingExp)
	
	nowLevel = role.GetLevel()
	#经验满, 需要进阶或是最后一阶
	if cfg.maxExp <= nowExp and (cfg.isUpGrade or cfg.nextID == -1 or nowLevel < cfg.upNeedLevel):
		return
	
	#道具
	if role.ItemCnt(EnumGameConfig.WeddingRingCoding) < 50:
		return
	#临时的经验值
	tempExp = role.GetI32(EnumInt32.TempWedRingExp)
	
	addSumExp = 0
	useItemCnt = 0
	
	for _ in xrange(50):
		useItemCnt += 1
		
		critTrue = cfg.critTrue.RandomOne()
		if critTrue:
			addExp = cfg.addExp * 2
			addSumExp += cfg.addExp * 2
		else:
			addExp = cfg.addExp
			addSumExp += cfg.addExp
		
		nowExp += addExp
		if nowExp + tempExp < cfg.maxExp:
			continue
		
		if cfg.nextID == -1 or cfg.isUpGrade or nowLevel < cfg.upNeedLevel:
			nowExp = cfg.maxExp
			break
		if tempExp:
			nowExp = 0
			tempExp = 0
		else:
			nowExp -= cfg.maxExp
		
		cfg = MarryConfig.WeddingRing_Dict.get(cfg.nextID)
		if not cfg:
			print "GE_EXC, RequestAdvancedForging can not find weddingRingID (%s) in WeddingRing_Dict" % cfg.nextID
			return
		
	with WeddingRingForging_Log:
		role.DelItem(EnumGameConfig.WeddingRingCoding, useItemCnt)
	
	if nowWeddingRingID == cfg.weddingRingID:
		#没有升阶
		role.SetI32(EnumInt32.WeddingRingExp, nowExp)
	else:
		#升阶
		role.SetI16(EnumInt16.WeddingRingID, cfg.weddingRingID)
		#计算经验
		role.SetI32(EnumInt32.WeddingRingExp, nowExp)
		#更新婚戒ID
		UpdateRingID(role)
		#重算婚戒属性
		role.ResetGlobalWeddingRingProperty()
		#激活戒灵
		if cfg.activeRingSoul:
			ActiveRingSoul(role, cfg.activeRingSoul)
		#激活夫妻技能
		ActiveFuqiSkill(role)
		#假如有临时值
		if role.GetI32(EnumInt32.TempWedRingExp):
			role.SetI32(EnumInt32.TempWedRingExp, 0)
		from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
		if role.GetI16(EnumInt16.WeddingRingID) >= 11:
			WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Wed_Ring, role)
		#from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
		#LatestActivityMgr.GetFunByType(EnumLatestType.HunJie_Latest, role)
	#专题活动每日培养婚戒次数
	ProjectAct.GetFunByType(EnumProActType.ProjectRingEvent, (role, 50))
	
	role.Msg(2, 0, GlobalPrompt.WeddingAdvancedTips % (useItemCnt, addSumExp))
	
def RequestWeddingRingUp(role, msg):
	'''
	婚戒进阶
	@param role:
	@param msg:
	'''
	#等级
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	
	#结婚状态
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	
	#等阶
	ringID = role.GetI16(EnumInt16.WeddingRingID)
	if not ringID:
		return
	
	#配置
	cfg = MarryConfig.WeddingRing_Dict.get(ringID)
	if not cfg:
		return
	nextCfg = MarryConfig.WeddingRing_Dict.get(cfg.nextID)
	if not nextCfg:
		return
	
	#不需要进阶或是最后一阶
	if not cfg.isUpGrade or cfg.nextID == -1:
		return
	
	#当前经验
	nowExp = role.GetI32(EnumInt32.WeddingRingExp)
	if nowExp < cfg.maxExp:
		return
	
	tempExp = role.GetI32(EnumInt32.TempWedRingExp)
	if tempExp:
		#下一阶经验
		role.SetI32(EnumInt32.WeddingRingExp, 0)
		role.SetI32(EnumInt32.TempWedRingExp, 0)
	else:
		role.SetI32(EnumInt32.WeddingRingExp, nowExp - cfg.maxExp)
	#升阶
	role.IncI16(EnumInt16.WeddingRingID, 1)
	
	#更新婚戒ID
	UpdateRingID(role)
	
	#重算婚戒属性
	role.ResetGlobalWeddingRingProperty()
	
	#激活戒灵
	if nextCfg.activeRingSoul:
		ActiveRingSoul(role, nextCfg.activeRingSoul)
	
	#激活夫妻技能
	ActiveFuqiSkill(role)
	
	from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType
	if role.GetI16(EnumInt16.WeddingRingID) >= 11:
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_Wed_Ring, role)
	#from Game.Activity.LatestActivity import LatestActivityMgr, EnumLatestType
	#LatestActivityMgr.GetFunByType(EnumLatestType.HunJie_Latest, role)
	
def RequestOpenWRSPanel(role, msg):
	'''
	打开婚戒戒灵面板
	@param role:
	@param msg:
	'''
	#等级
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	
	#激活
	if not role.GetI8(EnumInt8.WedingRingSoulID):
		return
	
	role.SendObj(WeddingProPercent, role.GetObj(EnumObj.WeddingRingSoulPro))
	role.SendObj(WeddingSkill, role.GetObj(EnumObj.WeddingRingStarObj)[3])
	
def RequestSuccinct(role, msg):
	'''
	请求洗练
	@param role:
	@param msg:
	'''
	if not msg: return
	
	#等级
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	
	#激活了就可以炼, 不用一定要是结婚状态
	if not role.GetI8(EnumInt8.WedingRingSoulID):
		return
	
	#婚戒戒灵ID
	ringSoulIndex, useRMB, lockProList = msg
	
	#激活的戒灵最大ID
	if ringSoulIndex > role.GetI8(EnumInt8.WedingRingSoulID):
		return
	weddingRingSoulP = role.GetObj(EnumObj.WeddingRingSoulPro)
	if ringSoulIndex not in weddingRingSoulP[1]:
		return
	
	needRMB = 0
	needItem = 0
	needLockItem = len(lockProList)
	lockProCnt = needLockItem
	if not useRMB:
		if role.ItemCnt(EnumGameConfig.WeddingRingSoulCoding) < 1:
			return
		if role.ItemCnt(EnumGameConfig.WeddingRingSoulLockCoding) < needLockItem:
			return
	
	if role.ItemCnt(EnumGameConfig.WeddingRingSoulCoding) < 1:
		if Environment.EnvIsNA():
			needRMB += EnumGameConfig.WeddingRingSoulUnbindRMB_NA
		else:
			needRMB += EnumGameConfig.WeddingRingSoulUnbindRMB
	else:
		needItem = 1
	
	haveLockItem = role.ItemCnt(EnumGameConfig.WeddingRingSoulLockCoding)
	if haveLockItem < needLockItem:
		if Environment.EnvIsNA():
			needRMB += (needLockItem - haveLockItem) * EnumGameConfig.WeddingRingSoulUnbindRMB_NA
		else:
			needRMB += (needLockItem - haveLockItem) * EnumGameConfig.WeddingRingSoulUnbindRMB
		needLockItem = haveLockItem
	
	WRSPD = weddingRingSoulP[1][ringSoulIndex]
	#属性全部锁住不让洗
	if needLockItem == len(WRSPD):
		return
	
	#检测一下是不是锁住的属性都在保存的属性中
	for proEnum in lockProList:
		if proEnum in WRSPD:
			continue
		return
		
	#神石不够
	if role.GetUnbindRMB() < needRMB:
		return
	
	#配置
	soulCfg = MarryConfig.WeddingRingSoul_Dict.get(ringSoulIndex)
	if not soulCfg:
		return
	
	#随机星级
	starList = soulCfg.randomStar.RandomMany(soulCfg.proCnt - lockProCnt)
	
	#随机百分百
	percentList = []
	for star in starList:
		if star not in MarryConfig.WeddingRingSoulP_Dict:
			continue
		percentList.append((star, random.randint(*MarryConfig.WeddingRingSoulP_Dict[star])))
	#打包生成字典
	
	proEnumList = [proEnum for proEnum in soulCfg.proEnumList if proEnum not in lockProList]
	
	tmpProDict = dict(zip(random.sample(proEnumList, soulCfg.proCnt - lockProCnt), percentList))
	
	#生成属性字典
	proDict = {}
	for proEnum in lockProList:
		proDict[proEnum] = [1, WRSPD[proEnum][0], WRSPD[proEnum][1]]
	for proEnum, percent in tmpProDict.iteritems():
		proDict[proEnum] = [0, percent[0], percent[1]]
	
	with WeddingRingSoulSuccinct_Log:
		if needItem:
			role.DelItem(EnumGameConfig.WeddingRingSoulCoding, needItem)
		if needRMB:
			role.DecUnbindRMB(needRMB)
		if needLockItem:
			role.DelItem(EnumGameConfig.WeddingRingSoulLockCoding, needLockItem)
	
	#记录戒灵属性
	weddingRingSoulP[2][ringSoulIndex] = proDict
	
	role.SendObj(WeddingProPercent, weddingRingSoulP)
	
def RequestSavePro(role, msg):
	'''
	请求保存属性
	@param role:
	@param msg:
	'''
	if not msg: return
	
	#等级
	if role.GetLevel() < EnumGameConfig.MarryLevelLimit:
		return
	
	#激活
	if not role.GetI8(EnumInt8.WedingRingSoulID):
		return
	
	ringSoulIndex = msg
	
	#激活的戒灵最大ID
	if ringSoulIndex > role.GetI8(EnumInt8.WedingRingSoulID):
		return
	
	#配置
	soulCfg = MarryConfig.WeddingRingSoul_Dict.get(ringSoulIndex)
	if not soulCfg:
		return
	
	weddingRingSoulP = role.GetObj(EnumObj.WeddingRingSoulPro)
	if (ringSoulIndex not in weddingRingSoulP[1]) or (ringSoulIndex not in weddingRingSoulP[2]):
		return
	
	#没有洗练属性
	if not weddingRingSoulP[2][ringSoulIndex]:
		return
	
	#先统计一下之前的属性星级
	tmpStarList = []
	for tp, tv in weddingRingSoulP[1][ringSoulIndex].iteritems():
		tmpStarList.append(tv[0])
	
	starObj = role.GetObj(EnumObj.WeddingRingStarObj)
	
	for star in tmpStarList:
		starObj[2][star] -= 1
	
	#清空
	weddingRingSoulP[1][ringSoulIndex] = {}
	tmpStarList = []
	
	for tp, tv in weddingRingSoulP[2][ringSoulIndex].iteritems():
		weddingRingSoulP[1][ringSoulIndex][tp] = [tv[1], tv[2]]
		tmpStarList.append(tv[1])
	
	for star in tmpStarList:
		if star not in starObj[2]:
			starObj[2][star] = 1
		else:
			starObj[2][star] += 1
	
	starDict = {}
	for star in tmpStarList:
		if star not in starDict:
			starDict[star] = 1
		else:
			starDict[star] += 1
	
	starObj[1][ringSoulIndex] = starDict
	
	role.SetObj(EnumObj.WeddingRingStarObj, starObj)
	
	weddingRingSoulP[2][ringSoulIndex] = {}
	
	role.SetObj(EnumObj.WeddingRingSoulPro, weddingRingSoulP)
	
	#重算婚戒戒灵属性
	role.ResetGlobalWeddingRingSProperty()
	
	#激活夫妻技能
	ActiveFuqiSkill(role)
	
	role.SendObj(WeddingProPercent, weddingRingSoulP)
	
def ActiveRingSoul(role, index):
	'''
	激活戒灵
	@param index:
	'''
	#戒灵配置
	soulCfg = MarryConfig.WeddingRingSoul_Dict.get(index)
	if not soulCfg:
		return
	
	#随机星级
	starList = soulCfg.randomStar.RandomMany(soulCfg.proCnt)
	tmpStarList = []
	for star in starList:
		if star < soulCfg.ChushiMax:
			tmpStarList.append(star)
		else:
			tmpStarList.append(soulCfg.ChushiMax)
	
	#统计星级个数
	starDict = {}
	for star in tmpStarList:
		if star not  in starDict:
			starDict[star] = 1
		else:
			starDict[star] += 1
	
	starObj = role.GetObj(EnumObj.WeddingRingStarObj)
	if not starObj:
		#{1:单个戒灵星级个数, 2:多个戒灵星级个数, 3:set(夫妻技能集合)}
		starObj = {1:{}, 2:{}, 3:set()}
	
	starObj[1][index] = starDict
	
	if not starObj[2]:
		for star, cnt in starDict.iteritems():
			starObj[2][star] = cnt
	else:
		for star, cnt in starDict.iteritems():
			if star not in starObj[2]:
				starObj[2][star] = cnt
			else:
				starObj[2][star] += cnt
	
	role.SetObj(EnumObj.WeddingRingStarObj, starObj)
	
	#随机百分百
	percentList = []
	for star in tmpStarList:
		if star not in MarryConfig.WeddingRingSoulP_Dict:
			continue
		#[(星级, 万分比), ]
		percentList.append((star, random.randint(*MarryConfig.WeddingRingSoulP_Dict[star])))
	
	#打包生成属性字典
	proDict = dict(zip(random.sample(soulCfg.proEnumList, soulCfg.proCnt), percentList))
	
	#记录戒灵属性
	weddingRingSoulP = role.GetObj(EnumObj.WeddingRingSoulPro)
	if not weddingRingSoulP:
		#{1:保存的属性, 2:洗练的属性}
		weddingRingSoulP = {1:{}, 2:{}}
	
	#保存属性
	weddingRingSoulP[1][index] = proDict
	role.SetObj(EnumObj.WeddingRingSoulPro, weddingRingSoulP)
	
	role.SetI8(EnumInt8.WedingRingSoulID, index)
	
	#同步戒灵属性
	role.SendObj(WeddingProPercent, weddingRingSoulP)
	
	#重算婚戒戒灵属性
	role.ResetGlobalWeddingRingSProperty()
	
def ActiveFuqiSkillEx(role):
	'''
	升阶的时候尝试激活结婚对象的夫妻技能 -- 只尝试激活需要婚戒ID激活的技能
	@param role:
	'''
	if Environment.IsCross:
		return
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	
	oldSkillSet = role.GetObj(EnumObj.WeddingRingStarObj)[3]
	
	#夫妻婚戒最大ID
	marryRoleID = role.GetObj(EnumObj.MarryObj).get(1)
	if not marryRoleID:
		print "GE_EXC, ActiveFuqiSkillEx can get marry role ID (%s)" % role.GetRoleID()
		return
	
	minRingID = min(role.GetI16(EnumInt16.WeddingRingID), ReturnWeddingRingID(marryRoleID))
	
	#尝试激活用婚戒ID激活的技能
	for skillID, cfg in MarryConfig.WeddingIDAct_Dict.iteritems():
		if minRingID < cfg.activeGrade:
			continue
		oldSkillSet.add(skillID)
	
	role.GetObj(EnumObj.WeddingRingStarObj)[3] = oldSkillSet
	role.ResetGlobalWeddingRingSkillProperty()
	
	role.SendObj(WeddingSkill, oldSkillSet)
	
def ReturnWeddingRingID(roleId):
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if role:
		return role.GetI16(EnumInt16.WeddingRingID)
	else:
		#不在线查表
		from Game.RoleView import RoleView
		if not RoleView.RoleView_BT.returnDB:
			return 0
		rD = RoleView.RoleView_BT.GetData().get(roleId)
		if not rD:
			return 0
		viewData = rD.get("viewData")
		if not viewData:
			return 0
		return viewData[1][EnumSocial.WeddingRingID]
	
def ActiveFuqiSkillNex(role):
	'''
	上线调用的尝试激活夫妻技能函数, 因为离婚离线命令可能还没有调用, 所以可能拿不到对象婚戒信息, 这里不报异常
	@param role:
	'''
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	
	oldSkillSet = role.GetObj(EnumObj.WeddingRingStarObj)[3]
	
	#夫妻婚戒最大ID
	marryRoleID = role.GetObj(EnumObj.MarryObj).get(1)
	if not marryRoleID:
		print "GE_EXC, ActiveFuqiSkillNex can get marry role ID (%s)" % role.GetRoleID()
		return
	
	minRingID = min(role.GetI16(EnumInt16.WeddingRingID), ReturnWeddingRingID(marryRoleID))
	
	#尝试激活用婚戒ID激活的技能
	for skillID, cfg in MarryConfig.WeddingIDAct_Dict.iteritems():
		if minRingID < cfg.activeGrade:
			continue
		oldSkillSet.add(skillID)
	
	role.GetObj(EnumObj.WeddingRingStarObj)[3] = oldSkillSet
	role.ResetGlobalWeddingRingSkillProperty()
	
	role.SendObj(WeddingSkill, oldSkillSet)
	
def ActiveFuqiSkill(role):
	'''尝试激活夫妻技能'''
	starObj = role.GetObj(EnumObj.WeddingRingStarObj)
	
	oldSkillSet = starObj[3]
	
	skillSet = set()
	
	if role.GetI8(EnumInt8.MarryStatus) == 3:
		#夫妻婚戒最大ID
		marryRoleID = role.GetObj(EnumObj.MarryObj).get(1)
		if not marryRoleID:
			print "GE_EXC, ActiveFuqiSkill can get marry role ID (%s)" % role.GetRoleID()
			return
		if not Environment.IsCross:
			minRingID = min(role.GetI16(EnumInt16.WeddingRingID), ReturnWeddingRingID(marryRoleID))
			#尝试激活用婚戒ID激活的技能
			for skillID, cfg in MarryConfig.WeddingIDAct_Dict.iteritems():
				if minRingID < cfg.activeGrade:
					continue
				skillSet.add(skillID)
		
		for skillID in oldSkillSet:
			if skillID in MarryConfig.WeddingGradeAct_Dict:
				skillSet.add(skillID)
				break
		
	#尝试激活用单个婚戒属性激活的技能
	for skillID, cfg in MarryConfig.WeddingSingleProAct_Dict.iteritems():
		for _, starDict in starObj[1].iteritems():
			tmpCnt = 0
			for star, cnt in starDict.iteritems():
				if star < cfg.singleRingNeedPro[0]:
					continue
				tmpCnt += cnt
				
			if tmpCnt < cfg.singleRingNeedPro[1]:
				continue
			skillSet.add(skillID)
	
	for skillID, cfg in MarryConfig.WeddingMultiProAct_Dict.iteritems():
		tmpCnt = 0
		for star, cnt in starObj[2].iteritems():
			if star < cfg.allRingNeedPro[0]:
				continue
			tmpCnt += cnt
		if tmpCnt < cfg.allRingNeedPro[1]:
			continue
		skillSet.add(skillID)
	
	role.GetObj(EnumObj.WeddingRingStarObj)[3] = skillSet
	
	#同步客户端激活夫妻技能
	role.SendObj(WeddingSkill, skillSet)
	#重算夫妻技能属性
	role.ResetGlobalWeddingRingSkillProperty()
	
def UpdateRingID(role):
	'''
	更新婚戒ID
	@param role:
	'''
	roleID = role.GetRoleID()
	
	#更新自己信息后尝试激活对象的夫妻技能
	marryRoleID = role.GetObj(EnumObj.MarryObj)[1]
	if not marryRoleID:
		print "GE_EXC, UpdateRingID role (%s) can not get marry role ID" % roleID
		return
	marryRole = cRoleMgr.FindRoleByRoleID(marryRoleID)
	if not marryRole:
		return
	#尝试激活结婚对象的夫妻技能
	ActiveFuqiSkillEx(marryRole)
	
def AfterLogin(role, param):
	#初始化技能obj
	if not role.GetObj(EnumObj.WeddingRingStarObj):
		role.SetObj(EnumObj.WeddingRingStarObj, {1:{}, 2:{}, 3:set()})
	
	#上线后尝试激活夫妻技能
	ActiveFuqiSkillNex(role)
	
def RoleDayClear(role, param):
	if role.GetI32(EnumInt32.TempWedRingExp):
		role.SetI32(EnumInt32.TempWedRingExp, 0)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WeddingRing_NormalForging", "婚戒普通普通锻造"), RequestNormalForging)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WeddingRing_AdvancedForging", "婚戒高级锻造"), RequestAdvancedForging)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WeddingRing_Up", "婚戒升阶"), RequestWeddingRingUp)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WeddingRinS_Succinct", "婚戒戒灵洗练"), RequestSuccinct)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WeddingRinS_SavePro", "婚戒戒灵保存属性"), RequestSavePro)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WeddingRinS_OpenPanel", "打开婚戒戒灵面板"), RequestOpenWRSPanel)
