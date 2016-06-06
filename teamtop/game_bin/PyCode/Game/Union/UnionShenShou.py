#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionShenShou")
#===============================================================================
# 公会神兽
#===============================================================================
import random
import cRoleMgr
import cSceneMgr
import Environment
import cComplexServer
from Game.Role import Status, Event
from Game.Fight import Fight
from Game.NPC import EnumNPCData
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Role.Mail import Mail
from Game.Role.Data import EnumDayInt1, EnumInt1, EnumDayInt8
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Union import UnionDefine, UnionMgr, UnionConfig, UnionBuilding
from Game.DailyDo import DailyDo
from Game.Activity.WonderfulAct import WonderfulActMgr, EnumWonderType

if "_HasLoad" not in dir():
	UnionShenShouNPCDict = {}						#缓存公会神兽NPC,unionID-->NPCObj
	ShenShouNPCPos = X, Y , Z = 1482, 981, 1		#公会神兽在公会驻地中途出现的位置
	ShenShouHurtDict = {}							#缓存公会角色对神兽造成的伤害unionID-->[(roleName,hurt)]
	MaxChallengeTime = 10							#最大挑战次数 
	
	#神兽喂养类型枚举
	NormalFeed = 1
	UpperFeed = 2
	PerfectFeed = 3
	
	#日志
	TraShenShouNormalFeed = AutoLog.AutoTransaction("TraShenShouNormalFeed", "公会神兽普通喂养")
	TraShenShouUpperFeed = AutoLog.AutoTransaction("TraShenShouUpperFeed", "公会神兽高级喂养")
	TraShenShouPerfectFeed = AutoLog.AutoTransaction("TraShenShouPerfectFeed", "公会神兽完美喂养")
	TraGetShenShouBlessing = AutoLog.AutoTransaction("TraGetShenShouBlessing", "获取公会神兽祝福")
	TraShenShouChallengeAward = AutoLog.AutoTransaction("TraShenShouChallengeAward", "挑战神兽获得奖励")
	TraShenShouHurtRankAward = AutoLog.AutoTransaction("TraShenShouHurtRankAward", "公会神兽伤害排行榜奖励")

	#消息
	Sync_UnionShenShouData = AutoMessage.AllotMessage("Sync_UnionShenShouData", "同步公会神兽数据")
	Sync_UnionShenShouHurtRank = AutoMessage.AllotMessage("Sync_UnionShenShouHurtRank", "同步公会神兽伤害排行榜")
	Sync_UnionShenShouFeedLog = AutoMessage.AllotMessage("Sync_UnionShenShouFeedLog", "同步公会神兽喂养记录")
	Sync_UnionShenShouCallTimes = AutoMessage.AllotMessage("Sync_UnionShenShouCallTimes", "同步公会神兽召唤次数")
	Sync_RoleHurtUnionShenShou = AutoMessage.AllotMessage("Sync_RoleHurtUnionShenShou", "同步角色公会神兽伤害")


#==================================================================================
#神兽基本操作
#==================================================================================
def SetShenShouId(unionObj, shenshouId):
	'''
	设置神兽id
	'''
	if id < 0:
		print "GE_EXC,set Union ShenShouId can not be %s" % id
		return
	otherData = unionObj.other_data
	otherData[UnionDefine.O_ShenShouId] = shenshouId
	unionObj.HasChange()
	
	
def GetShenShouId(unionObj):
	'''
	获取神兽id
	'''
	return unionObj.other_data.setdefault(UnionDefine.O_ShenShouId, 0)


def GetShenShouIdCalled(unionObj):
	'''
	获取当前已经被召唤出的神兽Id
	'''
	return unionObj.other_data.get(UnionDefine.O_ShenShouIdCalled, None)


def SetShenShouIdCalled(unionObj, shenshouId):
	'''
	清除公户被召唤出的神兽id
	'''
	unionObj.other_data[UnionDefine.O_ShenShouIdCalled] = shenshouId


def SetShenShouGrowthValue(unionObj, value):
	'''
	设置神兽成长值
	'''
	if not isinstance(value, int):
		return
	if value < 0:
		return
	otherData = unionObj.other_data
	otherData[UnionDefine.O_ShenShouGrowthValue] = value
	unionObj.HasChange()


def GetShenShouGrowthValue(unionObj):
	'''
	获取神兽成长值
	'''
	return unionObj.other_data.get(UnionDefine.O_ShenShouGrowthValue, 0)


def GetMaxGrowthValue(unionObj):
	'''
	获取公会神兽成长的最大值
	'''
	shenshouId = GetShenShouId(unionObj)
	config = UnionConfig.UnionShenShouLevelDict.get(shenshouId)
	if not config:
		print "GE_EXC, error while config = UnionConfig.UnionShenShouLevelDict.get(shenshouId)(%s)" % shenshouId
		return 0
	return config.maxGrouthValue


def IsShenShouGrowFull(unionObj):
	'''
	神兽的成长值是否已经满了
	'''
	maxGrowthValue = GetMaxGrowthValue(unionObj)
	currentGrowthValue = GetShenShouGrowthValue(unionObj)
	if currentGrowthValue >= maxGrowthValue:
		return True
	return False


def GetShenShouCallTimes(unionObj):
	'''
	获取当日公会神兽召唤的次数
	'''
	otherData = unionObj.other_data
	return otherData.setdefault(UnionDefine.O_ShenShouCalledTimes, 0)


def SetShenShouCallTimes(unionObj, value):
	'''
	设置公会神兽的招召唤次数 
	'''
	if value < 0:
		return
	otherData = unionObj.other_data
	otherData[UnionDefine.O_ShenShouCalledTimes] = value
	unionObj.HasChange()
		

def CallShenShou(unionObj, role):
	'''
	召唤神兽
	'''
	callTimes = GetShenShouCallTimes(unionObj)
	if callTimes >= EnumGameConfig.UnionShenShouMaxCallTime:
		return
	
	if not IsShenShouGrowFull(unionObj):
		return
	
	#获取公会领地场景
	unionId = unionObj.union_id
	scene = cSceneMgr.SearchPublicScene(unionId)
	if not scene:
		return
	
	shenshouId = GetShenShouId(unionObj)
	config = UnionConfig.UnionShenShouLevelDict.get(shenshouId, None)
	if config is None:
		return
		
	#神兽成长值清零
	SetShenShouGrowthValue(unionObj, 0)
	SetShenShouIdCalled(unionObj, shenshouId)
	SetShenShouCallTimes(unionObj, callTimes + 1)

	global UnionShenShouNPCDict
	UnionShenShouNPCDict[unionId] = scene.CreateNPC(config.npcType, X, Y, Z, 0, {EnumNPCData.EnNPC_Name : config.shenshouName})
	
	
	for roleId in unionObj.members.iterkeys():
		the_role = cRoleMgr.FindRoleByRoleID(roleId)
		if the_role is None:
			continue
		the_role.SendObj(Sync_UnionShenShouCallTimes, GetShenShouCallTimes(unionObj))
		shenshouId = GetShenShouId(unionObj)
		growthvalue = GetShenShouGrowthValue(unionObj)
		the_role.SendObj(Sync_UnionShenShouData, (shenshouId, growthvalue))
	
	role.Msg(2, 0, GlobalPrompt.UnionShenShouCallSuccess)
	UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionShenShouCallSuccessAll % config.shenshouName)


def RecountHurtRank(unionObj):
	'''
	重算公会神兽伤害排行榜
	'''
	unionID = unionObj.union_id
	global ShenShouHurtDict
	otherData = unionObj.other_data
	hurtDict = otherData.get(UnionDefine.O_ShenShouHurt, {})
	#这里是为了兼容新旧数据做的临时处理，因为之前没有记录角色战力、等级等等
	for v in hurtDict.itervalues():
		if len(v) < 5:
			v.extend((5 - len(v)) * [0])
			
	hurtList = [(k, v[0], v[1], v[2], v[3], v[4])for k, v in hurtDict.iteritems()]
	#roleId,roleName,hurt,roleZdl,roleLevel,roleExp
	hurtList.sort(key=lambda x:(x[2], x[3], x[4], x[5], -x[0]), reverse=True)
	hurtList = hurtList[:20]
	ShenShouHurtDict[unionID] = hurtList


def GetHurtRank(unionObj):
	'''
	获取公会公会神兽伤害排行榜
	'''
	unionID = unionObj.union_id
	return ShenShouHurtDict.setdefault(unionID, [])


def IncRoleHurt(role, value):
	'''
	增加角色对公会神兽的伤害值
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	if value <= 0:
		return
	otherData = unionObj.other_data
	hurtLogDict = otherData.setdefault(UnionDefine.O_ShenShouHurt, {})
	roleID = role.GetRoleID()
	oldData = hurtLogDict.get(roleID)
	if oldData is None:
		hurtLogDict[roleID] = [role.GetRoleName(), value, role.GetZDL(), role.GetLevel(), role.GetExp()]
	else:
		hurtLogDict[roleID] = [role.GetRoleName(), oldData[1] + value, role.GetZDL(), role.GetLevel(), role.GetExp()]
		
	unionObj.HasChange()
	RecountHurtRank(unionObj)


def SetFeedLog(unionObj, role, feedType, growthValue):
	'''
	设置公会神兽喂养记录
	'''
	otherData = unionObj.other_data
	shenshouFeedLog = otherData.setdefault(UnionDefine.O_ShenShouFeedLog, [])
	shenshouFeedLog.append((role.GetRoleName(), feedType, growthValue))
	unionObj.HasChange()


def GetFeedLog(unionObj):
	'''
	获取公会喂养记录
	'''
	otherData = unionObj.other_data
	return otherData.setdefault(UnionDefine.O_ShenShouFeedLog, [])


def GetRoleHurt(unionObj, role):
	'''
	'''
	otherData = unionObj.other_data
	hurtDict = otherData.get(UnionDefine.O_ShenShouHurt, {})
	roleId = role.GetRoleID()
	if roleId not in hurtDict:
		return 0
	return hurtDict[roleId][1]


#===============================================================================
# 战斗相关
#===============================================================================
def PVE_ShenShou(role, fightType, shenshouId, mcid, bufId, AfterFight, OnLeave=None, AfterPlay=None):
	'''
	公会神兽PVE
	@param role:
	@param fightType:
	@param newBufId:
	@param mcid:
	@param hpDict:
	@param AfterFight:
	@param OnLeave:
	@param AfterPlay:
	'''
	fight = Fight.Fight(fightType)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(role, role.GetRoleID())
	right_camp.create_monster_camp_unit(mcid)
	shenshouHP = 0
	
	for u in right_camp.pos_units.itervalues():
		shenshouHP += u.hp
		
	config = UnionConfig.UnionShenShouBufDict.get(bufId)
	if config is not None:
		for u in left_camp.pos_units.itervalues():
			u.damage_upgrade_rate += config.damageupgrade / 10000.0
		
	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	# 如果需要带参数，则直接绑定在fight对象上
	fight.after_fight_param = (shenshouId, shenshouHP)
	# 5开启战斗（之后就不能再对战斗做任何设置了）
	fight.start()


def AfterFight(fight):
	shenshouId, beforeFightHp = fight.after_fight_param
	afterFightHp = 0
	for u in fight.right_camp.pos_units.itervalues():
		afterFightHp += u.hp
	
	hurt = abs(beforeFightHp - afterFightHp)
	#获取战斗role
	if not fight.left_camp.roles:
		return
	left_camp_roles_list = list(fight.left_camp.roles)
	role = left_camp_roles_list[0]
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	config = UnionConfig.UnionShenShouLevelDict.get(shenshouId, None)
	if config is None:
		return
	
	IncRoleHurt(role, hurt)
	
	money = int(config.moneyCoe * hurt / 100000)
	contribution = int(config.contributionCoe * hurt / 100000)
	incMoney = min(config.moneyMax, money)
	incContribution = min(config.contributionMax, contribution)
		
	if fight.result == 1:
		msg = GlobalPrompt.UnionShenShouChallengeSuccess
	else:
		msg = GlobalPrompt.UnionShenShouChallengeFail
		
	with TraShenShouChallengeAward:
		if incMoney:
			role.IncMoney(incMoney)
			msg += GlobalPrompt.Money_Tips % incMoney
		if incContribution:
			role.IncContribution(incContribution)
			msg += GlobalPrompt.UnionContribution_Tips % incContribution
	
	#如果战斗胜利的话
	if fight.result == 1:
		#随机掉落
		indexCnt = random.randint(1, 3)
		goodList = config.StoreRandomRate.RandomMany(indexCnt)
		import UnionStore
		goodDict = UnionStore.GetShenShouGoodId(unionObj)
		for index, cnt in goodList:
			goodDict[index] = goodDict.get(index, 0) + cnt
		UnionStore.SetShenShouGoodId(unionObj, goodDict)
		
		#用于公告的内容
		itemDict = {}
		for index, cnt in goodList:
			config = UnionConfig.UnionShenShouGoodDict.get(index, None)
			if config is None:
				continue
			itemDict[config.item[0]] = itemDict.get(config.item[0], 0) + config.item[1] * cnt
		
		itemMsg = ''
		for coding, cnt in itemDict.iteritems():
			itemMsg += " #Z(%s,%s) " % (coding, cnt)
		UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionShenShouChallengeSuccessAll % (role.GetRoleName(), itemMsg))
		
	for roleId in unionObj.members.iterkeys():
		theRole = cRoleMgr.FindRoleByRoleID(roleId)
		if not theRole:
			continue
		if theRole.GetSceneID() != unionObj.union_id:
			continue
		theRole.SendObj(Sync_UnionShenShouHurtRank, GetHurtRank(unionObj))
		theRole.SendObj(Sync_RoleHurtUnionShenShou, GetRoleHurt(unionObj, theRole))
		
	times = role.GetDI8(EnumDayInt8.UnionShenShouChallenge)
	role.Msg(2, 0, msg + '#H' + GlobalPrompt.UnionShenShouChallengeTime % (MaxChallengeTime - times))

def HurtRankAward(unionObj):
	'''
	公会伤害排行榜奖励
	'''
	RecountHurtRank(unionObj)
	
	for rank, data in enumerate(GetHurtRank(unionObj)):
		roleID = data[0]
		contribution = UnionConfig.UnionShenShouHurtRankCfgDict.get(rank)
		if contribution is None:
			continue
		
		with TraShenShouHurtRankAward:
			Mail.SendMail(roleID, GlobalPrompt.UnionShenShouHurtRankMailTitle,
						GlobalPrompt.UnionShenShouHurtRankMailSender,
						GlobalPrompt.UnionShenShouHurtRankMailCotent % (rank + 1),
						contribution=contribution)
	
#==================================================================================
#客户端请求
#==================================================================================
def RequestFeedShenShou(role, msg):
	'''
	客户端请求喂养神兽
	'''
	roleId = role.GetRoleID()
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	#是否是在神兽成长值满了之后的喂养
	feedAfterFull = False
	
	if IsShenShouGrowFull(unionObj):
		feedAfterFull = True
		
	if role.GetDI1(EnumDayInt1.UnionShenShouFeed):
		return
	
	feedType = msg
	
	config = UnionConfig.UnionShenShouFeedDict.get(feedType)
	if not config:
		print "GE_EXC,error while config = UnionConfig.UnionShenShouFeedDict.get(feedType)(%s)" % feedType
		return
	
	moneyToDec = 0
	unbindRMBToDec = 0
	growthValueToInc = 0
	contributionToInc = 0
	maxGrowthValue = GetMaxGrowthValue(unionObj)
	nowGrowthValue = GetShenShouGrowthValue(unionObj)
	
	
	IsFull = False
	
	#普通喂养
	if feedType == NormalFeed:
		moneyToDec = config.costMoney
		if role.GetMoney() < moneyToDec:
			return
		Tra = TraShenShouNormalFeed
		growthValueToInc = config.growthValue
		contributionToInc = config.incContribution
		
	#高级喂养
	elif feedType == UpperFeed:
		unbindRMBToDec = config.costUnbindRMB
		if role.GetUnbindRMB() < unbindRMBToDec:
			return
		Tra = TraShenShouUpperFeed
		growthValueToInc = config.growthValue
		contributionToInc = config.incContribution
	#完美喂养
	
	elif feedType == PerfectFeed:
		if feedAfterFull is True:
			return
		
		growthValueToInc = maxGrowthValue - nowGrowthValue
		totalTimes = growthValueToInc / config.growthValue
		if growthValueToInc % config.growthValue:
			totalTimes += 1
		contributionToInc = totalTimes * config.incContribution
		unbindRMBToDec = totalTimes * config.costUnbindRMB	
		if role.GetUnbindRMB() < unbindRMBToDec:
			return
		
		Tra = TraShenShouPerfectFeed
	else:
		return

	newGrowthValue = nowGrowthValue + growthValueToInc
	maxGrowthValue = GetMaxGrowthValue(unionObj)
	newGrowthValue = min(maxGrowthValue, newGrowthValue)
	deltaGrowthValue = newGrowthValue - nowGrowthValue
	if newGrowthValue >= maxGrowthValue:
		IsFull = True
	
	with Tra:
		if not feedAfterFull:
			SetShenShouGrowthValue(unionObj, newGrowthValue)
		if moneyToDec > 0:
			role.DecMoney(moneyToDec)
		if unbindRMBToDec > 0:
			role.DecUnbindRMB(unbindRMBToDec)
		if contributionToInc > 0:
			role.IncContribution(contributionToInc)
		role.SetDI1(EnumDayInt1.UnionShenShouFeed, 1)
		#增加喂养次数
		unionObj.other_data[UnionDefine.O_ShenShowDayFeed] += growthValueToInc
		
		SetFeedLog(unionObj, role, feedType, deltaGrowthValue)
	
	#每日必做 -- 每日培养一次公会神兽
	if not Environment.EnvIsRU():
		Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_UnionShenShou, 1))
		WonderfulActMgr.GetFunByType(EnumWonderType.Wonder_UnionFeed, unionObj)
	
	if feedAfterFull is True:
		role.Msg(2, 0, GlobalPrompt.UnionShenShouFeedAfterFull % contributionToInc)
		return
	
	else:
		for roleId in unionObj.members.iterkeys():
			the_role = cRoleMgr.FindRoleByRoleID(roleId)
			if the_role is None:
				continue
			the_role.SendObj(Sync_UnionShenShouCallTimes, GetShenShouCallTimes(unionObj))
			shenshouId = GetShenShouId(unionObj)
			growthvalue = GetShenShouGrowthValue(unionObj)
			the_role.SendObj(Sync_UnionShenShouData, (shenshouId, growthvalue))
			the_role.SendObj(Sync_UnionShenShouFeedLog, GetFeedLog(unionObj))
	
	
	role.Msg(2, 0, GlobalPrompt.UnionShenShouFeedOkay % (contributionToInc, deltaGrowthValue))
	roleName = role.GetRoleName()
	if feedType == PerfectFeed:
		UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionShenShouPerfectFeedOkay % roleName)
		return
		
	elif feedType == UpperFeed:
		UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionShenShouUpperFeedOkay % (roleName, deltaGrowthValue))
	
	if IsFull is True:
		shenshouId = GetShenShouId(unionObj)
		config = UnionConfig.UnionShenShouLevelDict.get(shenshouId)
		if not config:
			return
		UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionShenShouFeedFull % config.shenshouName)


def RequestCallShenShou(role, msg):
	'''
	客户端请求召唤神兽
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return

	roleID = role.GetRoleID()
	roleJob = unionObj.GetMemberJob(roleID)
	jobConfig = UnionConfig.UNION_JOB.get(roleJob)
	
	if jobConfig is None:
		return
	if not jobConfig.callShenShou:
		return
	
	#真正的召唤
	CallShenShou(unionObj, role)


def RequestChallengeShenShou(role, msg):
	'''
	客户端请求挑战神兽
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	otherData = unionObj.other_data
	shenshouId = otherData.get(UnionDefine.O_ShenShouIdCalled)
	
	#角色已经在战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	config = UnionConfig.UnionShenShouLevelDict.get(shenshouId)
	if not config:
		return
	challengeTimes = role.GetDI8(EnumDayInt8.UnionShenShouChallenge) 
	if challengeTimes >= MaxChallengeTime:
		return
	
	role.SetDI8(EnumDayInt8.UnionShenShouChallenge, challengeTimes + 1)
	
	bufId = role.GetDI8(EnumDayInt8.UnionShenShouBuf)
	
	PVE_ShenShou(role, config.fightType, shenshouId, config.monsterId, bufId, AfterFight, OnLeave=None, AfterPlay=None)
	

def RequestUpGradeShenShou(role, msg):
	'''
	客户端请求神兽升阶
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	roleID = role.GetRoleID()
	roleJob = unionObj.GetMemberJob(roleID)
	jobConfig = UnionConfig.UNION_JOB.get(roleJob)
	
	if jobConfig is None:
		return
	if not jobConfig.shenshouUpGrade:
		return
	
	currentShenShouId = GetShenShouId(unionObj)
	config = UnionConfig.UnionShenShouLevelDict.get(currentShenShouId)
	if not config:
		print "GE_EXC,error while config = UnionConfig.UnionShenShouLevelDict.get(currentShenShouId)(%s)" % currentShenShouId
		return
	newId = config.upGradeId
	if newId < 0:
		return
	if newId not in UnionConfig.UnionShenShouLevelDict:
		return
	
	if unionObj.resource < config.needUnionResorce:
		return
	if UnionBuilding.GetShenShouTanLevel(unionObj) < config.needShenShouTanLevel:
		return
	unionObj.DecUnionResource(config.needUnionResorce)
	SetShenShouId(unionObj, newId)
	role.SendObj(Sync_UnionShenShouData, (newId, GetShenShouGrowthValue(unionObj)))
	
	newConfig = UnionConfig.UnionShenShouLevelDict[newId]
	role.Msg(2, 0, GlobalPrompt.UnionShenShouUpGradeOkay)
	UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionShenShouUpGradeOkayAll % newConfig.shenshouName)
	

def RequestGetBlessing(role, msg):
	'''
	请求获取神兽祝福(获取神兽buf)
	'''
	oldBufId = role.GetDI8(EnumDayInt8.UnionShenShouBuf)
	newBufId = oldBufId + 1
	config = UnionConfig.UnionShenShouBufDict.get(newBufId)
	if config is None:
		return
	if role.GetUnbindRMB() < config.costUnbindRMB:
		return
	with TraGetShenShouBlessing:
		role.DecUnbindRMB(config.costUnbindRMB)
		role.SetDI8(EnumDayInt8.UnionShenShouBuf, newBufId)
	
	role.Msg(2, 0, GlobalPrompt.UnionShenShouBlessingOkay % int(config.damageupgrade / 100))


def RequestGetShenShouData(role, msg):
	'''
	客户端请求获取公会神兽数据
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	shenshouId = GetShenShouId(unionObj)
	growthvalue = GetShenShouGrowthValue(unionObj)
	role.SendObj(Sync_UnionShenShouData, (shenshouId, growthvalue))
	role.SendObj(Sync_UnionShenShouCallTimes, GetShenShouCallTimes(unionObj))
	role.SendObj(Sync_UnionShenShouFeedLog, GetFeedLog(unionObj))
	role.SendObj(Sync_UnionShenShouHurtRank, GetHurtRank(unionObj))
	role.SendObj(Sync_RoleHurtUnionShenShou, GetRoleHurt(unionObj, role))
	

def RequestGetShenShouHurtRank(role, msg):
	'''
	客户端请求获取神兽伤害排行
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	role.SendObj(Sync_UnionShenShouHurtRank, GetHurtRank(unionObj))


def RequestGetRoleHurt(role, msg):
	'''
	客户端请求获取角色神兽伤害值
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	role.SendObj(Sync_RoleHurtUnionShenShou, GetRoleHurt(unionObj, role))

#==================================================================================
#时间相关
#==================================================================================


def AfterNewDay():
	'''
	每日清理
	'''
	for unionObj in UnionMgr.UNION_OBJ_DICT.itervalues():
		otherData = unionObj.other_data
		if UnionDefine.O_ShenShouCalledTimes in otherData:
			del otherData[UnionDefine.O_ShenShouCalledTimes]
		if UnionDefine.O_ShenShouFeedLog in otherData:
			del otherData[UnionDefine.O_ShenShouFeedLog]
		if UnionDefine.O_ShenShouGoods in otherData:
			del otherData[UnionDefine.O_ShenShouGoods]
		if UnionDefine.O_ShenShouIdCalled in otherData:
			SetShenShouIdCalled(unionObj, None)
		if UnionDefine.O_ShenShowDayFeed in otherData:
			#清理每日喂养数
			otherData[UnionDefine.O_ShenShowDayFeed] = 0
		
		HurtRankAward(unionObj)
		
		if UnionDefine.O_ShenShouHurt in otherData:
			del otherData[UnionDefine.O_ShenShouHurt]
		
		RecountHurtRank(unionObj)
		unionObj.HasChange()
		
	#消除所有的神兽NPC
	global UnionShenShouNPCDict
	for npcObj in UnionShenShouNPCDict.itervalues():
			npcObj.Destroy()
			
	UnionShenShouNPCDict.clear()


def ShenShouNPCInit(unionObj):
	'''
	起服的时候创建公会神兽
	'''
	shenshouId = GetShenShouIdCalled(unionObj)
	if shenshouId is None:
		return
	#获取公会领地场景
	unionId = unionObj.union_id
	scene = cSceneMgr.SearchPublicScene(unionId)
	if not scene:
		return
	config = UnionConfig.UnionShenShouLevelDict.get(shenshouId, None)
	if config is None:
		return

	global UnionShenShouNPCDict
	UnionShenShouNPCDict[unionId] = scene.CreateNPC(config.npcType, X, Y, Z, 0, {EnumNPCData.EnNPC_Name : config.shenshouName})


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetShenShouData_Union", "客户端请求获取公会神兽数据"), RequestGetShenShouData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetShenShouHurtRank_Union", "客户端请求获取公会神兽伤害排行 "), RequestGetShenShouHurtRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestFeedShenShou_Union", "客户端请求喂养公会神兽"), RequestFeedShenShou)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestCallShenShou_Union", "客户端请求公会召唤神兽"), RequestCallShenShou)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestUpGradeShenShou_Union", "客户端请求公会神兽升阶"), RequestUpGradeShenShou)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestChallengeShenShou_Union", "客户端请求挑战公会神兽"), RequestChallengeShenShou)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetShenShouBlessing_Union", "客户端请求获取神兽祝福"), RequestGetBlessing)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetRoleHurtShenShou_Union", "客户端请求获取神角色公会神兽伤害"), RequestGetRoleHurt)

