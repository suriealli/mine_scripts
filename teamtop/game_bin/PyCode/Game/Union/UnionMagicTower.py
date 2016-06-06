#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionMagicTower")
#===============================================================================
# 公会魔法塔
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
import cComplexServer
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumInt1
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Union import UnionDefine, UnionConfig, UnionMgr


if "_HasLoad" not in dir():
	OneHour = 3600
	UnionSkillIsResearchingDict = {}	#公会是否正在研究技能unionId-->True是  False否(暂停)
	SkillResearchingTickDict = {}		#公会ID-->tickID
	
	#日志
	TraRoleActivateUnionSkill = AutoLog.AutoTransaction("TraRoleActivateUnionSkill", "角色激活公会技能")
	TraRoleLearnUnionSkill = AutoLog.AutoTransaction("TraRoleLearnUnionSkill", "角色学习公会技能")
	
	
	#消息
	Sync_UnionSkillProcessData = AutoMessage.AllotMessage("Sync_UnionSkillProcessData", "同步公会技能的研究进度")
	Sync_UnionSkillInResearching = AutoMessage.AllotMessage("Sync_UnionSkillInResearching", "同步正在研究的公会技能")
	Sync_RoleUnionSkillData = AutoMessage.AllotMessage("Sync_RoleUnionSkillData", "同步角色公会技能的激活数据")
	

def GetUnionSkillData(unionObj):
	'''
	获取公会所有技能研究情况 
	'''
	otherData = unionObj.other_data
	skillDict = otherData.setdefault(UnionDefine.O_UnionSkillProgress, {})
	skillInResearching = otherData.setdefault(UnionDefine.O_UnionSillResearching, None)
	return skillDict, skillInResearching


def GetUnionSKillProgress(unionObj, skillId):
	'''
	 获取某个公会技能的研究进度
	'''
	skillDict, _ = GetUnionSkillData(unionObj)
	return skillDict.get(skillId)


def GetUnionSKillLevel(unionObj, skillId):
	'''
	获取当前某个公会技能的研究等级(也就是公会成员可以学习的公会技能的最大等级)
	'''
	skillDict, _ = GetUnionSkillData(unionObj)
	skillData = skillDict.get(skillId)
	if skillData is None:
		return 0
	
	level = skillData.get('level', 0)
	
	if skillData.get('enable') is True:
		return level
	return level - 1


def GetUnionSkillResearching(unionObj):
	'''
	获取当前正在研究的技能
	''' 
	return unionObj.other_data.get(UnionDefine.O_UnionSillResearching)


def SetUnionSkillResearching(unionObj, skillId):
	'''
	设置当前正在研究的技能id
	'''
	unionObj.other_data[UnionDefine.O_UnionSillResearching] = skillId
	

def ClearUnionSkillResearching(unionObj):
	'''
	清空当前公会技能的研究状态
	'''
	if UnionDefine.O_UnionSillResearching in unionObj.other_data:
		del unionObj.other_data[UnionDefine.O_UnionSillResearching]


def GetSkillName(skillId, level):
	'''
	获取技能的名称
	'''
	config = UnionConfig.UnionSkillConfigDict.get((skillId, level))
	if not config:
		print "GE_EXC,error while config = UnionConfig.UnionSkillConfigDict.get((skillId, level))(%s,%s)" % (skillId, level)
		return
	return config.name


def StartResearchUnionSkill(unionObj, role, skillId):
	#开始研究某个公会技能
	
	#当前正在研究某个技能 
	skillDict, nowResearching = GetUnionSkillData(unionObj)
	if nowResearching is not None:
		return	
	oldLevel = GetUnionSKillLevel(unionObj, skillId)
	newLevel = oldLevel + 1 
	if (skillId, newLevel) not in UnionConfig.UnionSkillConfigDict:
		return
	config = UnionConfig.UnionSkillConfigDict[(skillId, newLevel)]
	#公会资源少于每小时消耗的资源则不开启 
	if unionObj.resource < config.needResorcePerHour:
		return
	global UnionSkillIsResearchingDict
	UnionSkillIsResearchingDict[unionObj.union_id] = True
	nowSec = cDateTime.Seconds()
	skillDict[skillId] = {'level':newLevel, 'time':nowSec, 'process':0, 'enable':False}
	
	unionObj.HasChange()
	#设置为当前正在研究的技能
	SetUnionSkillResearching(unionObj, skillId)
	unionID = unionObj.union_id
	UnionSKillResearch(None, (unionID, skillId, newLevel))
	
	roleName = role.GetRoleName()
	role.Msg(2, 0, GlobalPrompt.UnionSkillResearchSuccess)
	UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionSkillResearchSuccessAll % (roleName, GetSkillName(skillId, newLevel)))


def UnionSKillResearch(callargv, regparam):
	#公会技能研究的
	unionID, skillId, level = regparam
	global SkillResearchingTickDict
	if unionID in SkillResearchingTickDict:
		del SkillResearchingTickDict[unionID]
	
	#这个时候公会有可能已经不存在了
	unionObj = UnionMgr.GetUnionObjByID(unionID)
	if unionObj is None:
		return
	skillData = GetUnionSKillProgress(unionObj, skillId)
	if skillData is None:
		return
	if skillData.get('enable') is True:
		return
	config = UnionConfig.UnionSkillConfigDict.get((skillId, level))
	if not config:
		print "GE_EXC,error while config = UnionConfig.UnionSkillConfigDict.get((skillId, level))(%s,%s)" % (skillId, level)
		return
	
	global UnionSkillIsResearchingDict
	#如果资源不足
	if unionObj.resource < config.needResorcePerHour:
		SkillResearchingTickDict[unionID] = cComplexServer.RegTick(OneHour, UnionSKillResearch, regparam)
		IsInResearching = UnionSkillIsResearchingDict[unionID] = False
		UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionSkillResearchPause % config.name)
	
	else:
		unionObj.DecUnionResource(config.needResorcePerHour)
		oldProcess = skillData['process']
		newProcess = oldProcess + config.processPerHour
		skillData['process'] = newProcess
		#如果增加进度值之后进度值已经满了
		if newProcess >= config.maxProcess:
			ClearUnionSkillResearching(unionObj)
			skillData['enable'] = True
			IsInResearching = UnionSkillIsResearchingDict[unionID] = False
			UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionSkillResearchOkay % config.name)
			
		else:
			lastTime = UnionSkillIsResearchingDict.get(unionID, True)
			SkillResearchingTickDict[unionID] = cComplexServer.RegTick(OneHour, UnionSKillResearch, regparam)
			IsInResearching = UnionSkillIsResearchingDict[unionID] = True
			if lastTime is False and IsInResearching is True:
				UnionMgr.UnionMsg(unionObj, GlobalPrompt.UnionSkillResearchGoOn % config.name)
	
		unionObj.HasChange()
	
	processDict, inResearchingId = GetUnionSkillData(unionObj)
	
	for roleId in unionObj.members.iterkeys():
		the_role = cRoleMgr.FindRoleByRoleID(roleId)
		if the_role is None:
			continue
		the_role.SendObj(Sync_UnionSkillProcessData, processDict)
		the_role.SendObj(Sync_UnionSkillInResearching, (inResearchingId, IsInResearching))
	

def AfterUnionObjInit(unionObj):
	#公会对象生成后的处理
	#获取当前正在研究的公会技能id
	skillId = GetUnionSkillResearching(unionObj)
	if skillId is None:
		return
	skillData = GetUnionSKillProgress(unionObj, skillId)
	if skillData is None:
		return
	startSec = skillData.get('time', None)
	level = skillData.get('level', None)
	if startSec is None or level is None:
		print "GE_EXC, UnionObj (id:%s) union skill data has no key named time or level" % unionObj.union_id
		return
	nowSec = cDateTime.Seconds()
	nexSec = (nowSec - startSec) % OneHour
	
	if nexSec != 0:
		global SkillResearchingTickDict
		SkillResearchingTickDict[unionObj.union_id] = cComplexServer.RegTick(nexSec, UnionSKillResearch, (unionObj.union_id, skillId, level))
	else:
		UnionSKillResearch(None, (unionObj.union_id, skillId, level))


#===============================================================================
#客户端请求
#===============================================================================
def RequestResearchSkill(role, msg):
	'''
	客户端请求研究公会技能
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	skillId = msg
	roleID = role.GetRoleID()
	roleJob = unionObj.GetMemberJob(roleID)
	jobConfig = UnionConfig.UNION_JOB.get(roleJob)
	
	if jobConfig is None:
		return
	
	if not jobConfig.skillResearch:
		return
	
	StartResearchUnionSkill(unionObj, role, skillId)


def RequestActivateSkill(role, msg):
	'''
	客户端请求激活公会技能
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	skillId = msg
	roleSkillDict = role.GetObj(EnumObj.Union).setdefault(4, {})
	if skillId not in roleSkillDict:
		return
	level = roleSkillDict[skillId]['level']
	config = UnionConfig.UnionSkillConfigDict.get((skillId, level))
	if not config:
		print "GE_EXC, error while config = UnionConfig.UnionSkillConfigDict.get((skillId, level))(%s,%s)" % (skillId, level)
		return
	
	if role.GetContribution() < config.needContriActive:
		return
	
	with TraRoleActivateUnionSkill:
		role.DecContribution(config.needContriActive)
		nowSec = cDateTime.Seconds()
		roleSkillDict[skillId]['time'] = nowSec
		
	role.GetPropertyMgr().ResetGlobalUnionSkillProperty()
	role.RegTick(config.continueTime, RecountUnionSkill, None)
	role.SendObj(Sync_RoleUnionSkillData, roleSkillDict)
	
	role.Msg(2, 0, GlobalPrompt.UnionSkillActiveOkay)


def RequestLearnUnionSkill(role, msg):
	'''
	客户端请求学习公会技能
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	skillId = msg
	
	roleSkillDict = role.GetObj(EnumObj.Union).setdefault(4, {})
	skillData = roleSkillDict.get(skillId, {})
	oldLevel = skillData.get('level', 0)
	newLevel = oldLevel + 1
	
	if newLevel > GetUnionSKillLevel(unionObj, skillId):
		return 
	config = UnionConfig.UnionSkillConfigDict.get((skillId, newLevel))
	if not config:
		print "GE_EXC, error while config = UnionConfig.UnionSkillConfigDict.get((skillId, oldLevel)) (%s,%s) " % (skillId, oldLevel)
		return
	
	if role.GetLevel() < config.roleLevel:
		return
	if role.GetMoney() < config.needMoney:
		return
	if role.GetContribution() < config.needContriLearn:
		return
	
	with TraRoleLearnUnionSkill:
		role.DecMoney(config.needMoney)
		role.DecContribution(config.needContriLearn)
		nowSec = cDateTime.Seconds()
		roleSkillDict[skillId] = {'level':newLevel, 'time':nowSec}
	
	
	role.GetPropertyMgr().ResetGlobalUnionSkillProperty()
	role.RegTick(config.continueTime, RecountUnionSkill, None)
	role.SendObj(Sync_RoleUnionSkillData, roleSkillDict)
	
	role.Msg(2, 0, GlobalPrompt.UnionSkillLearnOkay)


def RequestRoleUnionSkillData(role, msg):
	'''
	客户端请求获取角色公会技能数据
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	skillDict = role.GetObj(EnumObj.Union).setdefault(4, {})
	role.SendObj(Sync_RoleUnionSkillData, skillDict)


def RequestUnionSkillProcessData(role, msg):
	'''
	 客户端请求获取公会技能研究进度
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	unionID = unionObj.union_id
	theDict, searchingID = GetUnionSkillData(unionObj)
	role.SendObj(Sync_UnionSkillProcessData, theDict)
	IsInResearching = UnionSkillIsResearchingDict.setdefault(unionID, False)
	role.SendObj(Sync_UnionSkillInResearching, (searchingID, IsInResearching))


def GetRoleUnionSkillProperty(role):
	'''
	获取角色通过公会技能增加的属性
	'''
	#首先判断角色是否在公会中
	if not role.GetI1(EnumInt1.InUnion):
		return {}
	
	skillDict = role.GetObj(EnumObj.Union).setdefault(4, {})
	totalPropertyDict = {}
	TPG = totalPropertyDict.get
	now = cDateTime.Seconds()
	for skillID, data in skillDict.iteritems():
		if "time" not in data or 'level' not in data:
			print "GE_EXC, role(%s) has UnionSkillID(%s) but has no data" % (role.GetRoleID(), skillID)
			continue
		time = data['time']
		level = data['level']
		config = UnionConfig.UnionSkillConfigDict.get((skillID, level))
		if config is None:
			print "GE_EXC, error while config = UnionConfig.UnionSkillConfigDict.get((skillID, level))(%s,%s) " % (skillID, level)
			continue
		if config.continueTime - (now - time) <= 0:
			continue
		for pt, pv in config.property_dict.iteritems():
			totalPropertyDict[pt] = TPG(pt, 0) + pv
	return totalPropertyDict


def AfterRoleLogin(role, param):
	'''
	角色登录之后的处理,主要是设置战力重算的时间 
	'''
	roleSkillData = role.GetObj(EnumObj.Union).setdefault(4, {})
	
	for skillID, data in roleSkillData.iteritems():
		if "time" not in data or 'level' not in data:
			print "GE_EXC, role(%s) has UnionSkillID(%s) but has no data" % (role.GetRoleID(), skillID)
			continue
		time = data['time']
		level = data['level']
		config = UnionConfig.UnionSkillConfigDict.get((skillID, level))
		if config is None:
			print "GE_EXC, error while config = UnionConfig.UnionSkillConfigDict.get((skillID, level))(%s,%s) " % (skillID, level)
			continue
		now = cDateTime.Seconds()
		leftTime = config.continueTime - (now - time)
		if leftTime <= 0:
			continue
		role.RegTick(leftTime, RecountUnionSkill, None)


def SyncRoleOtherData(role, param):
	'''
	角色进入场景后如果有公会技能过期则需要弹窗通知
	@param role:
	@param param:
	'''	
	roleSkillData = role.GetObj(EnumObj.Union).get(4, {})
	isTimeOut = False
	for skillID, data in roleSkillData.iteritems():
		if "time" not in data or 'level' not in data:
			continue
		time = data['time']
		level = data['level']
		config = UnionConfig.UnionSkillConfigDict.get((skillID, level))
		if config is None:
			print "GE_EXC, error while config = UnionConfig.UnionSkillConfigDict.get((skillID, level))(%s,%s) " % (skillID, level)
			continue
		now = cDateTime.Seconds()
		if config.continueTime - (now - time) <= 0:
			isTimeOut = True
			break
		
	if isTimeOut is True:
		role.Msg(4, 0, GlobalPrompt.UnionSkillTimeOut)
		

def RecountUnionSkill(role, callargv, regparam):
	'''
	设置技能过期后重算公会技能属性
	'''
	if role.IsKick():
		return
	role.GetPropertyMgr().ResetGlobalUnionSkillProperty()
	role.Msg(4, 0, GlobalPrompt.UnionSkillTimeOut)


if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_AfterLogin, AfterRoleLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		if not Environment.IsCross:
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestResearchUnionSkill", "客户端请求研究公会技能"), RequestResearchSkill)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestActiveteUnionSkill", "客户端请求激活公会技能"), RequestActivateSkill)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestLearnUnionSkill", "客户端请求学习公会技能"), RequestLearnUnionSkill)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestRoleUnionSkillData", "客户端请求获取角色公会技能数据"), RequestRoleUnionSkillData)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestUnionSkillProcessData", "客户端请求获取公会技能研究进度"), RequestUnionSkillProcessData)
		
		

