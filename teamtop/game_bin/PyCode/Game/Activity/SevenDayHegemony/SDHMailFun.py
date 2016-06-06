#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SevenDayHegemony.SDHMailFun")
#===============================================================================
# 七日争霸邮件发放奖励
#===============================================================================
from Common.Other import GlobalPrompt
from Game.Union import UnionMgr
from Game.Role.Mail import Mail
from Game.Activity.SevenDayHegemony import SDHDefine, SDHFunGather, SDHConfig, SDHRankFun

if "_HasLoad" not in dir():
	
	Tra_SevenDayHegemony_UnionFB = SDHRankFun.Tra_SevenDayHegemony_UnionFB
	Tra_SevenDayHegemony_Purgatory = SDHRankFun.Tra_SevenDayHegemony_Purgatory
	Tra_SevenDayHegemony_TeamTower = SDHRankFun.Tra_SevenDayHegemony_TeamTower


@SDHFunGather.RegMailRewardFun(SDHDefine.TeamTower)
def SDHMailReward_TeamTower(roleId, rank, actName):
	'''
	组队爬塔邮件发放奖励
	'''
	actType = SDHDefine.TeamTower
	rankAwardLog = SDHFunGather.SevenDayHegemonyDict.setdefault('rankAwardLog', {})
	awardLog = rankAwardLog.get(roleId, set())
	if actType in awardLog:
		return
	
	config = SDHConfig.SDHRankConfigDict.get((actType, rank))
	if config is None:
		print "GE_EXC, config = SDHConfig.SDHRankConfigDict.get((%s, %s)) error" % (actType, rank)
		return
	
	tarot_list = None
	if config.tarot:
		tarot_list = [i[0] for i in config.tarot]
	
	with Tra_SevenDayHegemony_TeamTower:
		Mail.SendMail(roleId,
					GlobalPrompt.SevenDayHegemony_MTitle,
					GlobalPrompt.SevenDayHegemony_MSender,
					GlobalPrompt.SevenDayHegemony_MContent % (actName, rank),
					items=config.item,
					tarotList=tarot_list,
					bindrmb=config.bindRMB,
					money=config.money,
					contribution=config.contribution)
	
	
@SDHFunGather.RegMailRewardFun(SDHDefine.UnionFB)
def SDHMAilReward_UnionFB(unionID, rank, actName):
	'''
	公会副本邮件发放奖励
	'''
	actType = SDHDefine.UnionFB
	unionObj = UnionMgr.GetUnionObjByID(unionID)
	if not unionObj:
		print "GE_EXC, union on rank but has dismissed in SDH"
		return
	rankAwardLog = SDHFunGather.SevenDayHegemonyDict.setdefault('rankAwardLog', {})
	
	config = SDHConfig.SDHRankConfigDict.get((actType, rank))
	if config is None:
		print "GE_EXC, config = SDHConfig.SDHRankConfigDict.get((%s, %s)) error" % (actType, rank)
		return
	
	tarot_list = None
	if config.tarot:
		tarot_list = [i[0] for i in config.tarot]
	
	for roleId in unionObj.members.iterkeys():
		awardLog = rankAwardLog.get(roleId, set())
		if actType in awardLog:
			continue
		
		with Tra_SevenDayHegemony_UnionFB:
			Mail.SendMail(roleId,
						GlobalPrompt.SevenDayHegemony_MTitle,
						GlobalPrompt.SevenDayHegemony_MSender,
						GlobalPrompt.SevenDayHegemony_MContent_Union % rank,
						items=config.item, tarotList=tarot_list,
						bindrmb=config.bindRMB,
						money=config.money,
						contribution=config.contribution)
			

@SDHFunGather.RegMailRewardFun(SDHDefine.Purgatory)
def SDHMailReward_Purgatory(roleId, rank, actName):
	'''
	心魔炼狱邮件发放奖励
	'''
	actType = SDHDefine.Purgatory
	rankAwardLog = SDHFunGather.SevenDayHegemonyDict.setdefault('rankAwardLog', {})
	awardLog = rankAwardLog.get(roleId, set())
	if actType in  awardLog:
		return

	config = SDHConfig.SDHRankConfigDict.get((actType, rank))
	if config is None:
		print "GE_EXC, config = SDHConfig.SDHRankConfigDict.get((%s, %s)) error" % (actType, rank)
		return
	
	tarot_list = None
	if config.tarot:
		tarot_list = [i[0] for i in config.tarot]
	
	with Tra_SevenDayHegemony_Purgatory:
		Mail.SendMail(roleId,
					GlobalPrompt.SevenDayHegemony_MTitle,
					GlobalPrompt.SevenDayHegemony_MSender,
					GlobalPrompt.SevenDayHegemony_MContent % (actName, rank),
					items=config.item, tarotList=tarot_list,
					bindrmb=config.bindRMB,
					money=config.money,
					contribution=config.contribution)
