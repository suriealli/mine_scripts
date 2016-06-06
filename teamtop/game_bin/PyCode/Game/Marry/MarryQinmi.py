#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Marry.MarryQinmi")
#===============================================================================
# 亲密度
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Marry import MarryConfig
from Game.Role.Data import EnumInt8, EnumInt16, EnumInt32, EnumObj
from Common.Other import GlobalPrompt
from Game.Activity.Title import Title
from Game.Persistence import Contain
from Game.Role import Event

if "_HasLoad" not in dir():
	QinmiUpLevel_Log = AutoLog.AutoTransaction("QinmiUpLevel_Log", "亲密度等级提升")
	QinmiUpGrade_Log = AutoLog.AutoTransaction("QinmiUpGrade_Log", "亲密度品阶提升")
	
def RequestUpQinmiLv(role, msg):
	'''
	请求提升亲密等级
	@param role:
	@param msg:
	'''
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	
	qinmiLevel = role.GetI16(EnumInt16.QinmiLevel)
	
	cfg = MarryConfig.Qinmi_Dict.get(qinmiLevel)
	if not cfg:
		print 'GE_EXC, MarryQinmi RequestUpQinmiLv can not find qinmi level %s' % qinmiLevel
		return
	
	if cfg.nextLevel == -1:
		return
	if cfg.needQinmiGrade > role.GetI8(EnumInt8.QinmiGrade):
		return
	
	if role.GetI32(EnumInt32.Qinmi) < cfg.needQinmi:
		return
	
	with QinmiUpLevel_Log:
		role.DecI32(EnumInt32.Qinmi, cfg.needQinmi)
		role.IncI16(EnumInt16.QinmiLevel, 1)
	
	role.ResetGlobalQinmiProperty()
	
	role.Msg(2, 0, GlobalPrompt.QinmiLvUp)
	
def RequestUpGrade(role, msg):
	'''
	请求提升亲密品阶
	@param role:
	@param msg:
	'''
	global QinmiLevelDict
	if not QinmiLevelDict.returnDB: return
	
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	
	qinmiGrade = role.GetI8(EnumInt8.QinmiGrade)
	
	cfg = MarryConfig.QinmiGrade_Dict.get(qinmiGrade)
	if not cfg:
		print 'GE_EXC, MarryQinmi RequestUpGrade can not find qinmi grade %s' % qinmiGrade
		return
	
	if cfg.maxLevel == qinmiGrade:
		return
	
	if role.GetI16(EnumInt16.QinmiLevel) < cfg.needQinmiLevel:
		return
	
	if role.GetI32(EnumInt32.Qinmi) < cfg.needQinmi:
		return
	
	if role.GetLevel() < cfg.needRoleLevel:
		return
	
	with QinmiUpGrade_Log:
		role.DecI32(EnumInt32.Qinmi, cfg.needQinmi)
		role.IncI8(EnumInt8.QinmiGrade, 1)
	
	role.ResetGlobalQinmiGradeProperty()
	
	#夫妻id
	roleId = role.GetRoleID()
	marryRoleId = role.GetObj(EnumObj.MarryObj).get(1, 0)
	#夫妻品阶
	ownGrade = role.GetI8(EnumInt8.QinmiGrade)
	marryGrade = QinmiLevelDict.get(marryRoleId, 0)
	#更新亲密品阶
	QinmiLevelDict[roleId] = ownGrade
	QinmiLevelDict.changeFlag = True
	#尝试激活夫妻双方亲密称号
	minGrade = min(ownGrade, marryGrade)
	TryActQinmiTitle(role, minGrade)
	marryRole = cRoleMgr.FindRoleByRoleID(marryRoleId)
	if marryRole:
		TryActQinmiTitle(marryRole, minGrade)
	
	role.Msg(2, 0, GlobalPrompt.QinmiLvUp)
	
def AfterLogin(role, param):
	global QinmiLevelDict
	if not QinmiLevelDict.returnDB: return
	
	if role.GetI8(EnumInt8.MarryStatus) != 3:
		return
	qinmiGrade = role.GetI8(EnumInt8.QinmiGrade)
	if not qinmiGrade:
		return
	
	roleId = role.GetRoleID()
	if roleId not in QinmiLevelDict:
		#上线尝试将亲密品阶记录下来
		QinmiLevelDict[roleId] = qinmiGrade
	
	marryRoleId = role.GetObj(EnumObj.MarryObj).get(1)
	if not marryRoleId:
		return
	
	marryRoleQinmiGrade = QinmiLevelDict.get(marryRoleId)
	if not marryRoleQinmiGrade:
		return
	
	minGrade = min(qinmiGrade, marryRoleQinmiGrade)
	#尝试激活亲密品阶称号
	TryActQinmiTitle(role, minGrade)
	
	marryRole = cRoleMgr.FindRoleByRoleID(marryRoleId)
	if marryRole:
		TryActQinmiTitle(marryRole, minGrade)
	
def TryActQinmiTitle(role, minGrade):
	roleId = role.GetRoleID()
	titleObj = role.GetObj(EnumObj.Title).get(1, {})
	
	MQG = MarryConfig.QinmiTitleIdToGrade.get
	TA = Title.AddTitle
	for titleId in MarryConfig.QinmiTitleSet:
		if titleId in titleObj:
			#已有的称号
			continue
		needGrade = MQG(titleId)
		if not needGrade:
			#顶级
			continue
		if needGrade > minGrade:
			#品阶不够
			continue
		TA(roleId, titleId)
	
if "_HasLoad" not in dir():
	if (Environment.HasLogic and not Environment.IsCross) or Environment.HasWeb:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		
		QinmiLevelDict = Contain.Dict("QinmiLevelDict", (2038, 1, 1))
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Qinmi_Up", "请求提升亲密等级"), RequestUpQinmiLv)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Qinmi_UpGrade", "请求提升亲密品阶"), RequestUpGrade)
		
