#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SeaXunbao.SeaXunbao")
#===============================================================================
# 深海寻宝
#===============================================================================
import random
import Environment
import cRoleMgr
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Mail import Mail
from Game.Activity.SeaXunbao import SeaXunbaoConfig
from Game.Role import Event
from Game.Activity import CircularDefine, CircularActive
from Game.Role.Data import EnumTempObj

if "_HasLoad" not in dir():
	SeaXunbaoNormal_Log = AutoLog.AutoTransaction("SeaXunbaoNormal_Log", "深海普通寻宝日志")
	SeaXunbaoAdvance_Log = AutoLog.AutoTransaction("SeaXunbaoAdvance_Log", "深海高级寻宝日志")
	
	IsSeaXunbaoOpen = False
	
	SeaActiveID = 0
	
def NormalXunbao(role, grade, level, xunbaoCnt, activeId):
	#普通寻宝
	needCoding = EnumGameConfig.SeaXunbaoNormalCoding
	if role.ItemCnt(needCoding) < xunbaoCnt:
		#需要的物品不足
		return
	needMoney = 0
	if Environment.EnvIsNA():
		needMoney = EnumGameConfig.SeaXunbaoNormalMoney_NA * xunbaoCnt
	else:
		needMoney = EnumGameConfig.SeaXunbaoNormalMoney * xunbaoCnt
	if role.GetMoney() < needMoney:
		return
	cfg = SeaXunbaoConfig.SeaXunbao_Dict.get((grade, level, activeId))
	if not cfg:
		print 'GE_EXC, can not find (grade %s, level %s, activeId %s) in SeaXunbao_Dict' % (grade, level, activeId)
		return
	#扣物品
	role.DelItem(needCoding, xunbaoCnt)
	#扣金币
	role.DecMoney(needMoney)
	roleName = role.GetRoleName()
	#传闻物品列表(类型, coding, cnt)
	rumorList = []
	#奖励物品字典
	rewardItemDict = {}
	#奖励命魂列表
	rewardTarotList = []
	#奖励天赋卡列表
	rewardTalentList = []
	CNR = cfg.normalRewardRandom.RandomOne
	for _ in xrange(xunbaoCnt):
		tp, coding, cnt = CNR()
		if tp == 1:
			#道具
			if coding not in rewardItemDict:
				rewardItemDict[coding] = cnt
			else:
				rewardItemDict[coding] += cnt
		elif tp == 2:
			#命魂
			rewardTarotList.append(coding)
		elif tp == 3:
			#天赋卡
			rewardTalentList.append(coding)
		else:
			print 'GE_EXC, NormalXunbao error coding type %s' % tp
			return
		if coding in SeaXunbaoConfig.SeaXunbaoRumor_Set:
			#加入需要传闻列表
			rumorList.append((tp, coding, cnt))
	tips = GlobalPrompt.Reward_Tips
	needTips = False
	#背包满的话奖励通过邮件发送
	if rewardItemDict:
		if role.PackageEmptySize() < len(rewardItemDict):
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.SeaXunbaoMail_Title, GlobalPrompt.SeaXunbaoMail_Sender, GlobalPrompt.SeaXunbaoMail_Content, items = [(coding, cnt) for coding, cnt in rewardItemDict.iteritems()])
		else:
			for coding, cnt in rewardItemDict.iteritems():
				role.AddItem(coding, cnt)
				tips += GlobalPrompt.Item_Tips % (coding, cnt)
			needTips = True
	if rewardTarotList:
		if role.GetTempObj(EnumTempObj.enTarotMgr).PackageEmptySize() < len(rewardTarotList):
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.SeaXunbaoMail_Title, GlobalPrompt.SeaXunbaoMail_Sender, GlobalPrompt.SeaXunbaoMail_Content, tarotList = rewardTarotList)
		else:
			for coding in rewardTarotList:
				role.AddTarotCard(coding, 1)
				tips += GlobalPrompt.Tarot_Tips % (coding, 1)
			needTips = True
	if rewardTalentList:
		if role.GetTalentEmptySize() < len(rewardTalentList):
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.SeaXunbaoMail_Title, GlobalPrompt.SeaXunbaoMail_Sender, GlobalPrompt.SeaXunbaoMail_Content, talents = rewardTalentList)
		else:
			for coding in rewardTalentList:
				role.AddTalentCard(coding)
				tips += GlobalPrompt.Talent_Tips % (coding, 1)
			needTips = True
	if needTips:
		role.Msg(2, 0, tips)
	else:
		role.Msg(2, 0, GlobalPrompt.SeaXunbaoPackageFull)
	
	for (tp, coding, cnt) in rumorList:
		if tp == 1:
			cRoleMgr.Msg(1, 0, GlobalPrompt.SeaXunbaoRumor_1 % (roleName, coding, cnt))
		elif tp == 2:
			cRoleMgr.Msg(1, 0, GlobalPrompt.SeaXunbaoRumor_2 % (roleName, coding, cnt))
		elif tp == 3:
			cRoleMgr.Msg(1, 0, GlobalPrompt.SeaXunbaoRumor_3 % (roleName, coding, cnt))
	
def AdvanceXunbao(role, grade, level, xunbaoCnt, activeId):
	#高级寻宝
	needCoding = EnumGameConfig.SeaXunbaoAdvanceCoding
	if role.ItemCnt(needCoding) < xunbaoCnt:
		return
	cfg = SeaXunbaoConfig.SeaXunbao_Dict.get((grade, level, activeId))
	if not cfg:
		print 'GE_EXC, can not find (grade %s, level %s, activeId %s) in SeaXunbao_Dict' % (grade, level, activeId)
		return
	role.DelItem(needCoding, xunbaoCnt)
	roleName = role.GetRoleName()
	rumorList = []
	rewardItemDict = {}
	rewardTarotList = []
	rewardTalentList = []
	CAR = cfg.advanceRewardRandom.RandomOne
	for _ in xrange(xunbaoCnt):
		tp, coding, cnt = CAR()
		if tp == 1:
			#道具
			if coding not in rewardItemDict:
				rewardItemDict[coding] = cnt
			else:
				rewardItemDict[coding] += cnt
		elif tp == 2:
			#命魂
			rewardTarotList.append(coding)
		elif tp == 3:
			#天赋卡
			rewardTalentList.append(coding)
		else:
			print 'GE_EXC, AdvanceXunbao error coding type %s' % tp
			return
		if coding in SeaXunbaoConfig.SeaXunbaoRumor_Set:
			#传闻
			rumorList.append((tp, coding, cnt))
	tips = GlobalPrompt.Reward_Tips
	needTips = False
	if rewardItemDict:
		if role.PackageEmptySize() < len(rewardItemDict):
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.SeaXunbaoMail_Title, GlobalPrompt.SeaXunbaoMail_Sender, GlobalPrompt.SeaXunbaoMail_Content, items = [(coding, cnt) for coding, cnt in rewardItemDict.iteritems()])
		else:
			for coding, cnt in rewardItemDict.iteritems():
				role.AddItem(coding, cnt)
				tips += GlobalPrompt.Item_Tips % (coding, cnt)
			needTips = True
	if rewardTarotList:
		if role.GetTempObj(EnumTempObj.enTarotMgr).PackageEmptySize() < len(rewardTarotList):
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.SeaXunbaoMail_Title, GlobalPrompt.SeaXunbaoMail_Sender, GlobalPrompt.SeaXunbaoMail_Content, tarotList = rewardTarotList)
		else:
			for coding in rewardTarotList:
				role.AddTarotCard(coding, 1)
				tips += GlobalPrompt.Tarot_Tips % (coding, 1)
			needTips = True
	if rewardTalentList:
		if role.GetTalentEmptySize() < len(rewardTalentList):
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.SeaXunbaoMail_Title, GlobalPrompt.SeaXunbaoMail_Sender, GlobalPrompt.SeaXunbaoMail_Content, talents = rewardTalentList)
		else:
			for coding in rewardTalentList:
				role.AddTalentCard(coding)
				tips += GlobalPrompt.Talent_Tips % (coding, 1)
			needTips = True
	if needTips:
		role.Msg(2, 0, tips)
	else:
		role.Msg(2, 0, GlobalPrompt.SeaXunbaoPackageFull)
	
	for (tp, coding, cnt) in rumorList:
		if tp == 1:
			cRoleMgr.Msg(1, 0, GlobalPrompt.SeaXunbaoRumor_1 % (roleName, coding, cnt))
		elif tp == 2:
			cRoleMgr.Msg(1, 0, GlobalPrompt.SeaXunbaoRumor_2 % (roleName, coding, cnt))
		elif tp == 3:
			cRoleMgr.Msg(1, 0, GlobalPrompt.SeaXunbaoRumor_3 % (roleName, coding, cnt))
#===============================================================================
# 掉落羊皮卷
#===============================================================================
def SeaXunbaoMap_ExtendReward(role, param):
	#活动是否开始
	global IsSeaXunbaoOpen
	if IsSeaXunbaoOpen is False:
		return None
	
	#等级不够不掉落奖励
	if role.GetLevel() < 60:
		return
	
	activityType, idx = param
	
	oddsConfig = SeaXunbaoConfig.SeaXunbao_Map.get((activityType, idx))
	if not oddsConfig:
		return None
	
	rewardDict = {}
	#藏宝图掉落
	if random.randint(1, 10000) <= oddsConfig.mapOdds:
		rewardDict[oddsConfig.mapCoding] = 1
	
	return rewardDict
#===============================================================================
# 辅助
#===============================================================================
def GetCloseValue(value, value_list):
	'''
	返回第一个大于value的上一个值
	@param value:
	@param value_list:
	'''
	tmp_level = 0
	for i in value_list:
		if i > value:
			return tmp_level
		tmp_level = i
	else:
		#没有找到返回最后一个值
		return tmp_level
#===============================================================================
# 开关
#===============================================================================
def OpenSeaXunbao(role, param):
	if param != CircularDefine.CA_SeaXunbao:
		return
	global IsSeaXunbaoOpen
	if IsSeaXunbaoOpen:
		print 'GE_EXC, SeaXunbao is already open'
	IsSeaXunbaoOpen = True
	
	global SeaActiveID
	if SeaActiveID:
		print 'GE_EXC, SeaActiveID is already have'
	isActiveTypeRepeat = False
	for activeId, (activeType, _) in CircularActive.CircularActiveCache_Dict.iteritems():
		if activeType != param:
			continue
		if isActiveTypeRepeat:
			print 'GE_EXC, repeat SeaXunbaoType in CircularActiveCache_Dict'
		SeaActiveID = activeId
		isActiveTypeRepeat = True
	
def CloseSeaXunbao(role, param):
	if param != CircularDefine.CA_SeaXunbao:
		return
	global IsSeaXunbaoOpen
	if not IsSeaXunbaoOpen:
		print 'GE_EXC, SeaXunbao is already close'
	IsSeaXunbaoOpen = False
	
	global SeaActiveID
	if not SeaActiveID:
		print 'GE_EXC, SeaActiveID is already zero'
	SeaActiveID = 0
#===============================================================================
# 客户端请求
#===============================================================================
def RequestSeaXunbao(role, param):
	'''
	请求深海寻宝
	@param role:
	@param param:(寻宝等级, 寻宝次数)
	'''
	global IsSeaXunbaoOpen
	if not IsSeaXunbaoOpen:
		#活动未开启
		return
	if role.GetLevel() < EnumGameConfig.SeaXunbaoLevelLimit:
		#等级不足
		return
	if not param:
		#参数错误
		return
	#获取活动ID
	xunbaoGrade, xunbaoCnt = param
	if xunbaoGrade not in (1, 2) or xunbaoCnt not in (1, 10, 50):
		#参数错误
		return
	global SeaActiveID
	if not SeaActiveID:
		return
	#获得合适的等级
	level = GetCloseValue(role.GetLevel(), SeaXunbaoConfig.SeaXunbaoLevel_List)
	if xunbaoGrade == 1:
		#普通寻宝
		with SeaXunbaoNormal_Log:
			NormalXunbao(role, 1, level, xunbaoCnt, SeaActiveID)
	else:
		#高级寻宝
		with SeaXunbaoAdvance_Log:
			AdvanceXunbao(role, 2, level, xunbaoCnt, SeaActiveID)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SeaXunbao", "请求深海寻宝"), RequestSeaXunbao)
		
		Event.RegEvent(Event.Eve_StartCircularActive, OpenSeaXunbao)
		Event.RegEvent(Event.Eve_EndCircularActive, CloseSeaXunbao)