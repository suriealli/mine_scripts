#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SevenDayHegemony.SDHRankAcountFun")
#===============================================================================
# 排行版结算
#===============================================================================
import cRoleMgr
from ComplexServer.Log import AutoLog
from Game.SystemRank import SystemRank
from Common.Other import GlobalPrompt
from Game.Activity.SevenDayHegemony import SDHFunGather, SDHDefine


if "_HasLoad" not in dir():
	
	Tra_SevenDayHegemonyRankAccount = AutoLog.AutoTransaction("Tra_SevenDayHegemonyRankAccount", "七日争霸排行榜结算")
	

@SDHFunGather.RegRankAccountFun(SDHDefine.TeamTower)
def AccountRank_TeamTower():
	'''
	组队爬塔排行榜结算
	'''
	if not SystemRank.TTR.returnDB:
		print 'GE_EXC, SystemRank.TTR not returnDB'
		return
	
	SevenDayHegemonyDict = SDHFunGather.SevenDayHegemonyDict
	accountSet = SevenDayHegemonyDict.setdefault('accountSet', set())
	#不要重复结算
	actType = SDHDefine.TeamTower
	if actType in accountSet:
		return
	
	rankData = SystemRank.TTR.ReturnData().items()
	#[role.GetRoleName(), tindex, score, fround, role.GetZDL(), GetRoleFlower(role.GetRoleID())
	#章节 -->  回合-->战力
	rankData.sort(key=lambda x:(x[1][1], -x[1][3], x[1][4], x[1][5]), reverse=True)
	#前二十名
	rankData = rankData[:20]
	
	
	rankDict = {}
	for index, (roleId, data) in enumerate(rankData):
		#排行是索引+1
		rankDict[roleId] = [index + 1, data]
	
	
	with Tra_SevenDayHegemonyRankAccount:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveSevenDayHegemonyRank, (actType, rankDict))
		accountSet.add(actType)
		theRankData = SevenDayHegemonyDict.setdefault('rankData', {})
		theRankData[actType] = rankDict
		SevenDayHegemonyDict.HasChange()
	
	if rankData:
		firstName = rankData[0][1][0]
		cRoleMgr.Msg(1, 0, GlobalPrompt.SevenDayHegemonyGlobalTell_TeamTower % firstName)
		
		
	

@SDHFunGather.RegRankAccountFun(SDHDefine.UnionFB)
def AccountRank_UnionFB():
	'''
	公会副本排行榜结算
	'''
	if not SystemRank.UFB.returnDB:
		print "GE_EXC, SystemRank.UFB not returnDB"
		return
	
	SevenDayHegemonyDict = SDHFunGather.SevenDayHegemonyDict
	accountSet = SevenDayHegemonyDict.setdefault('accountSet', set())
	#不要重复结算
	actType = SDHDefine.UnionFB
	if actType in accountSet:
		return
	
	rankData = SystemRank.UFB.ReturnData().items()
	#[unionObj.name, maxFBId, maxLevel, maxOccupation, unionObj.level, unionObj.exp, unionObj.union_id]
	rankData.sort(key=lambda x:(x[1][1], x[1][2], x[1][3], x[1][4], x[1][5], x[1][6]), reverse=True)
	#公会只取前三
	rankData = rankData[:3]
	
	
	rankDict = {}
	for index, (unionID, data) in enumerate(rankData):
		rankDict[unionID] = [index + 1, data]
	
	with Tra_SevenDayHegemonyRankAccount:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveSevenDayHegemonyRank, (actType, rankDict))
		accountSet.add(actType)
		theRankData = SevenDayHegemonyDict.setdefault('rankData', {})
		theRankData[actType] = rankDict
		SevenDayHegemonyDict.HasChange()
	
	if rankData:
		firstName = rankData[0][1][0]
		cRoleMgr.Msg(1, 0, GlobalPrompt.SevenDayHegemonyGlobalTell_UnionFb % firstName)


@SDHFunGather.RegRankAccountFun(SDHDefine.Purgatory)
def AccountRank_Purgatory():
	'''
	心魔炼狱结算
	'''
	if not SystemRank.PR.returnDB:
		print "GE_EXC, SystemRank.PR not returnDB"
		return
	
	SevenDayHegemonyDict = SDHFunGather.SevenDayHegemonyDict
	accountSet = SevenDayHegemonyDict.setdefault('accountSet', set())
	#不要重复结算
	actType = SDHDefine.Purgatory 
	if actType in accountSet:
		return
	
	rankData = SystemRank.PR.ReturnData().items()
	#[role.GetRoleName(), pId, fround, GetRoleFlower(role.GetRoleID()), role.GetQQLZ(), role.GetQQYLZ(), role.GetQQHHLZ()]
	rankData.sort(key=lambda x:(x[1][1], -x[1][2], x[1][3], x[1][4], x[1][5], x[1][6]), reverse=True)
	#取前20
	rankData = rankData[:20]
	rankDict = {}
	for index, (unionID, data) in enumerate(rankData):
		rankDict[unionID] = [index + 1, data]
	
	with Tra_SevenDayHegemonyRankAccount:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveSevenDayHegemonyRank, (actType, rankDict))
		accountSet.add(actType)
		theRankData = SevenDayHegemonyDict.setdefault('rankData', {})
		theRankData[actType] = rankDict
		SevenDayHegemonyDict.HasChange()
	
	if rankData:
		firstName = rankData[0][1][0]
		cRoleMgr.Msg(1, 0, GlobalPrompt.SevenDayHegemonyGlobalTell_Purgatory % firstName)
