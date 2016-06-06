#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.FindBack.FindBack")
#===============================================================================
# 找回系统
#===============================================================================
import cRoleMgr
import cDateTime
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumObj, EnumTempObj, EnumInt8, EnumInt16, EnumInt1
from Game.FindBack import FindBackConfig, FindBackDefine


NeedLevel = 30
RMBNeedVIPLevel = 4

if "_HasLoad" not in dir():
	FindBack_S_Data = AutoMessage.AllotMessage("FindBack_S_Data", "同步当前找回系统次数数据")
	FindBack_S_TimeData = AutoMessage.AllotMessage("FindBack_S_TimeData", "同步当前找回系统正在时间找回的数据")

	Tra_FindBack_RMB = AutoLog.AutoTransaction("Tra_FindBack_RMB", "找回系统神石找回")
	Tra_FindBack_OneKeyRMB = AutoLog.AutoTransaction("Tra_FindBack_OneKeyRMB", "找回系统一键神石找回")
	
	Tra_FindBack_BindRMB = AutoLog.AutoTransaction("Tra_FindBack_BindRMB", "找回系统魔晶找回")
	Tra_FindBack_OneKeyBindRMB = AutoLog.AutoTransaction("Tra_FindBack_OneKeyBindRMB", "找回系统一键魔晶找回")
	
	Tra_FindBack_Money = AutoLog.AutoTransaction("Tra_FindBack_Money", "找回系统金币找回")
	Tra_FindBack_OneKeyMoney = AutoLog.AutoTransaction("Tra_FindBack_OneKeyMoney", "找回系统一键金币找回")
	
	
	Tra_FindBack_TimeReward = AutoLog.AutoTransaction("Tra_FindBack_TimeReward", "找回系统时间触发时间找回奖励")

#######################################################################################
def InitFindBackData(role):
	#第一次初始化
	fbdict = role.GetObj(EnumObj.FindBackData)
	if not fbdict:
		role.SetObj(EnumObj.FindBackData, {1 : {}, 2 : {}})

def PackFindTips(tips, exp, money, rmb, reputation, items,tili):
	if exp:
		tips += GlobalPrompt.Exp_Tips % exp
	if money:
		tips += GlobalPrompt.Money_Tips % money
	if rmb:
		tips += GlobalPrompt.UnBindRMB_Tips % rmb
	if reputation:
		tips += GlobalPrompt.Reputation_Tips % reputation
	if tili:
		tips += GlobalPrompt.TiLi_Tips % tili
	if items:
		for itemCoding, itemCnt in items.iteritems():
			tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
	return tips

def RMBFindBack(role, msg):
	'''
	神石找回
	@param role:
	@param msg:
	'''
	if role.GetVIP() < RMBNeedVIPLevel:
		return
	backId, index = msg
	fbdict = role.GetObj(EnumObj.FindBackData)
	cntDict = fbdict[1]
	fbCnt = cntDict.get(index)
	if not fbCnt:
		return
	
	
	fbcfg = FindBackConfig.FindBackConfig_Dict.get(index)
	if not fbcfg:
		return
	
	needRMB = fbcfg.NeedUnbindRMB(fbCnt)
	rewardCfg = FindBackConfig.GetRMBReward(role, index)
	if not rewardCfg:
		print "GE_EXC RMBFindBack not this rewardCfg roleLevel(%s), viplevel(%s)" % (role.GetLevel(), role.GetVIP())
		return
	if role.GetUnbindRMB() < needRMB:
		return
	
	with Tra_FindBack_RMB:
		cntDict[index] = 0
		
		role.DecUnbindRMB(needRMB)
		exp, money, rmb, reputation, items, tili = rewardCfg.RewardRole(role, index, fbCnt, FindBackDefine.RMB_Reward)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveFindBackRMB, {index : fbCnt})
		
		role.CallBackFunction(backId, (index, 0))
		if index == FindBackDefine.DFFB and cDateTime.WeekDay() in (0, 1, 3, 5):
			#魔兽入侵、魔龙降临找回时提示
			name = GlobalPrompt.MD_Name
		else:
			name = fbcfg.name
		role.Msg(2, 0, PackFindTips(GlobalPrompt.FindBackTips_1 % name, exp, money, rmb, reputation, items,tili))
		
	if index == FindBackDefine.DFFB and ((not role.GetI1(EnumInt1.DemonDefenseIn)) or (not role.GetI1(EnumInt1.MDragonComeIn))):
		#魔兽入侵在更新后保留之前的找回
		#找回后需要重新参与魔兽入侵和魔龙降临后激活
		if index in cntDict:
			del cntDict[index]
		if index in fbdict[2]:
			del fbdict[2][index]
	
def OneKeyRMBFindBack(role, msg):
	'''
	一键神石找回
	@param role:
	@param msg:
	'''
	if role.GetVIP() < RMBNeedVIPLevel:
		return
	backId, _ = msg
	fbdict = role.GetObj(EnumObj.FindBackData)
	cntDict = fbdict[1]
	
	cntFindBackDict = {}
	
	for index, cnt in  cntDict.iteritems():
		if cnt <= 0: continue
		cntFindBackDict[index] = cnt
	if not cntFindBackDict:
		return
	
	rewardCfg = FindBackConfig.GetRMBReward(role)
	if not rewardCfg:
		print "GE_EXC OneKeyRMBFindBack not this rewardCfg roleLevel(%s), viplevel(%s)" % (role.GetLevel(), role.GetVIP())
		return
	
	needRMB = 0
	systemNames = []
	FDFFB = FindBackDefine.DFFB
	weekDay = cDateTime.WeekDay()
	for index, cnt in cntFindBackDict.iteritems():
		fbcfg = FindBackConfig.FindBackConfig_Dict.get(index)
		if not fbcfg:
			print "GE_EXC, OneKeyRMBFindBack not cfg (%s)" % index
			return
		needRMB += fbcfg.NeedUnbindRMB(cnt)
		if index == FDFFB and weekDay in (0, 1, 3, 5):
			systemNames.append(GlobalPrompt.MD_Name)
		else:
			systemNames.append(fbcfg.name)
	if role.GetUnbindRMB() < needRMB:
		return
	
	with Tra_FindBack_OneKeyRMB:
		#修改数据
		hasDemon = False
		for index in cntFindBackDict.iterkeys():
			cntDict[index] = 0
			
			if index == FindBackDefine.DFFB:
				hasDemon = True
			
		role.DecUnbindRMB(needRMB)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveFindBackOneKeyRMB, cntFindBackDict)
		exp, money, rmb, reputation, items, tili = 0, 0, 0, 0, {}, 0
		for index, cnt in cntFindBackDict.items():
			if FindBackDefine.IsSpecilFB(index):
				#特殊找回，重新获取奖励配置
				scfg = FindBackConfig.GetRMBReward(role, index)
				if not scfg:
					print "GE_EXC, OneKeyRMBFindBack error index (%s) cnt(%s)" % (index, cnt)
					continue
				exp_1, money_1, rmb_1, reputation_1, items_1, tili_1 = scfg.RewardRole(role, index, cnt, FindBackDefine.RMB_Reward)
			else:
				exp_1, money_1, rmb_1, reputation_1, items_1, tili_1 = rewardCfg.RewardRole(role, index, cnt, FindBackDefine.RMB_Reward)
				
			cntFindBackDict[index] = 0
			exp += exp_1
			money += money_1
			rmb += rmb_1
			reputation += reputation_1
			tili += tili_1
			for i, c in items_1.iteritems():
				items[i] = items.get(i, 0) + c
		
		role.CallBackFunction(backId, cntFindBackDict)
		sname =",".join(systemNames)
		role.Msg(2, 0, PackFindTips(GlobalPrompt.FindBackTips_1 % sname, exp, money, rmb, reputation, items, tili))
	
	if hasDemon and ((not role.GetI1(EnumInt1.DemonDefenseIn)) or (not role.GetI1(EnumInt1.MDragonComeIn))):
		#魔兽入侵在更新后保留之前的找回
		#找回后需要重新参与魔兽入侵和魔龙降临后激活
		if index in cntDict:
			del cntDict[index]
		if index in fbdict[2]:
			del fbdict[2][index]
					
def BindRMBFindBack(role, msg):
	'''
	魔晶找回
	@param role:
	@param msg:
	'''
	backId, index = msg
	fbdict = role.GetObj(EnumObj.FindBackData)
	cntDict = fbdict[1]
	fbCnt = cntDict.get(index)
	if not fbCnt:
		return
	
	fbcfg = FindBackConfig.FindBackConfig_Dict.get(index)
	if not fbcfg:
		return
	
	needBindRMB = fbcfg.NeedBindRMB(fbCnt)
	if role.GetRMB() < needBindRMB:
		return
	rewardCfg = FindBackConfig.GetBindRMBReward(role, index)
	if not rewardCfg:
		print "GE_EXC BindRMBFindBack not this rewardCfg roleLevel(%s), viplevel(%s)" % (role.GetLevel(), role.GetVIP())
		return
	with Tra_FindBack_BindRMB:
		cntDict[index] = 0
		role.DecRMB(needBindRMB)
		exp, money, rmb, reputation, items, tili = rewardCfg.RewardRole(role, index, fbCnt, FindBackDefine.BindRMB_Reward)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveFindBackBindRMB, {index : fbCnt})
		#回调
		role.CallBackFunction(backId, (index, 0))
		if index == FindBackDefine.DFFB and cDateTime.WeekDay() in (0, 1, 3, 5):
			#魔兽入侵、魔龙降临找回时提示
			name = GlobalPrompt.MD_Name
		else:
			name = fbcfg.name
		role.Msg(2, 0, PackFindTips(GlobalPrompt.FindBackTips_1 % name, exp, money, rmb, reputation, items, tili))
		
	if index == FindBackDefine.DFFB and ((not role.GetI1(EnumInt1.DemonDefenseIn)) or (not role.GetI1(EnumInt1.MDragonComeIn))):
		#魔兽入侵在更新后保留之前的找回
		#找回后需要重新参与魔兽入侵和魔龙降临后激活
		if index in cntDict:
			del cntDict[index]
		if index in fbdict[2]:
			del fbdict[2][index]
	

def OneKeyBindRMBFindBack(role, msg):
	'''
	一键魔晶找回
	@param role:
	@param msg:
	'''
	backId, _ = msg
	fbdict = role.GetObj(EnumObj.FindBackData)
	cntDict = fbdict[1]
	
	cntFindBackDict = {}
	for index, cnt in  cntDict.iteritems():
		if cnt <= 0 : continue
		cntFindBackDict[index] = cnt
	if not cntFindBackDict:
		return
	
	rewardCfg = FindBackConfig.GetBindRMBReward(role)
	if not rewardCfg:
		print "GE_EXC OneKeyBindRMBFindBack not this rewardCfg roleLevel(%s), viplevel(%s)" % (role.GetLevel(), role.GetVIP())
		return
	
	needBindRMB = 0
	systemNames = []
	FDFFB = FindBackDefine.DFFB
	weekDay = cDateTime.WeekDay()
	for index, cnt in cntFindBackDict.iteritems():
		fbcfg = FindBackConfig.FindBackConfig_Dict.get(index)
		if not fbcfg:
			print "GE_EXC, OneKeyBindRMBFindBack not cfg (%s)" % index
			return
		needBindRMB += fbcfg.NeedBindRMB(cnt)
		if index == FDFFB and weekDay in (0, 1, 3, 5):
			systemNames.append(GlobalPrompt.MD_Name)
		else:
			systemNames.append(fbcfg.name)
	
	if role.GetRMB() < needBindRMB:
		return
	
	with Tra_FindBack_OneKeyBindRMB:
		#修改数据
		hasDemon = False
		for index in cntFindBackDict.iterkeys():
			cntDict[index] = 0
			
			if index == FindBackDefine.DFFB:
				hasDemon = True
			
		role.DecRMB(needBindRMB)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveFindBackOneKeyBindRMB, cntFindBackDict)
		exp, money, rmb, reputation, items, tili = 0, 0, 0, 0, {}, 0
		for index, cnt in cntFindBackDict.items():
			if FindBackDefine.IsSpecilFB(index):
				scfg = FindBackConfig.GetBindRMBReward(role, index)
				if not scfg:
					print "GE_EXC, OneKeyBindRMBFindBack"
					continue
				exp_1, money_1, rmb_1, reputation_1, items_1, tili_1 = scfg.RewardRole(role, index, cnt, FindBackDefine.BindRMB_Reward)
			else:
				exp_1, money_1, rmb_1, reputation_1, items_1, tili_1 = rewardCfg.RewardRole(role, index, cnt, FindBackDefine.BindRMB_Reward)
				
			cntFindBackDict[index] = 0
			exp += exp_1
			money += money_1
			rmb += rmb_1
			reputation += reputation_1
			tili += tili_1
			for i, c in items_1.iteritems():
				items[i] = items.get(i, 0) + c
		
		role.CallBackFunction(backId, cntFindBackDict)
		sname =",".join(systemNames)
		role.Msg(2, 0, PackFindTips(GlobalPrompt.FindBackTips_1 % sname, exp, money, rmb, reputation, items, tili))
	
	if hasDemon and ((not role.GetI1(EnumInt1.DemonDefenseIn)) or (not role.GetI1(EnumInt1.MDragonComeIn))):
		#魔兽入侵在更新后保留之前的找回
		#找回后需要重新参与魔兽入侵和魔龙降临后激活
		if index in cntDict:
			del cntDict[index]
		if index in fbdict[2]:
			del fbdict[2][index]
	



def MoneyFindBack(role, msg):
	'''
	金币找回
	@param role:
	@param msg:
	'''
	backId, index = msg
	fbdict = role.GetObj(EnumObj.FindBackData)
	cntDict = fbdict[1]
	fbCnt = cntDict.get(index)
	if not fbCnt:
		return
	
	fbcfg = FindBackConfig.FindBackConfig_Dict.get(index)
	if not fbcfg:
		return
	
	fbmoneyDict = FindBackConfig.FindBackMoney_Dict.get(index)
	if not fbmoneyDict:
		return
	mcfg = fbmoneyDict.get(role.GetLevel())
	if not mcfg:
		return
	needMoney = mcfg.NeedMoney(fbCnt)
	if role.GetMoney() < needMoney:
		return
	
	rewardCfg = FindBackConfig.GetMoneyReward(role, index)
	if not rewardCfg:
		print "GE_EXC MoneyFindBack not this rewardCfg roleLevel(%s), viplevel(%s)" % (role.GetLevel(), role.GetVIP())
		return
	with Tra_FindBack_Money:
		cntDict[index] = 0
		role.DecMoney(needMoney)
		exp, money, rmb, reputation, items, tili = rewardCfg.RewardRole(role, index, fbCnt, FindBackDefine.MoneyReward)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveFindBackMoney, {index : fbCnt})
		#回调
		role.CallBackFunction(backId, (index, 0))
		if index == FindBackDefine.DFFB and cDateTime.WeekDay() in (0, 1, 3, 5):
			#魔兽入侵、魔龙降临找回时提示
			name = GlobalPrompt.MD_Name
		else:
			name = fbcfg.name
		role.Msg(2, 0, PackFindTips(GlobalPrompt.FindBackTips_1 % name, exp, money, rmb, reputation, items, tili))
	
	if index == FindBackDefine.DFFB and ((not role.GetI1(EnumInt1.DemonDefenseIn)) or (not role.GetI1(EnumInt1.MDragonComeIn))):
		#魔兽入侵在更新后保留之前的找回
		#找回后需要重新参与魔兽入侵和魔龙降临后激活
		if index in cntDict:
			del cntDict[index]
		if index in fbdict[2]:
			del fbdict[2][index]
	

def OneKeyMoneyFindBack(role, msg):
	'''
	一键金币找回
	@param role:
	@param msg:
	'''
	backId, _ = msg
	fbdict = role.GetObj(EnumObj.FindBackData)
	cntDict = fbdict[1]
	
	cntFindBackDict = {}
	for index, cnt in  cntDict.iteritems():
		if cnt <= 0 : continue
		cntFindBackDict[index] = cnt
	if not cntFindBackDict:
		return
	
	rewardCfg = FindBackConfig.GetMoneyReward(role)
	if not rewardCfg:
		print "GE_EXC OneKeyMoneyFindBack not this rewardCfg roleLevel(%s), viplevel(%s)" % (role.GetLevel(), role.GetVIP())
		return
	
	totalneedMoney = 0
	systemNames = []
	FDFFB = FindBackDefine.DFFB
	weekDay = cDateTime.WeekDay()
	for index, cnt in cntFindBackDict.iteritems():
		fbcfg = FindBackConfig.FindBackConfig_Dict.get(index)
		if not fbcfg:
			print "GE_EXC, OneKeyMoneyFindBack not cfg (%s)" % index
			return
		fbmoneyDict = FindBackConfig.FindBackMoney_Dict.get(index)
		if not fbmoneyDict:
			return
		mcfg = fbmoneyDict.get(role.GetLevel())
		needMoney = mcfg.NeedMoney(cnt)
		if not needMoney:
			return
		totalneedMoney += needMoney
		if role.GetMoney() < totalneedMoney:
			return
		
		if index == FDFFB and weekDay in (0, 1, 3, 5):
			systemNames.append(GlobalPrompt.MD_Name)
		else:
			systemNames.append(fbcfg.name)
			
	if role.GetMoney() < totalneedMoney:
		return
	
	with Tra_FindBack_OneKeyMoney:
		#修改数据
		hasDemon = False
		for index in cntFindBackDict.iterkeys():
			cntDict[index] = 0
			
			if index == FindBackDefine.DFFB:
				hasDemon = True
			
		role.DecMoney(totalneedMoney)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveFindBackOneKeyMoney, cntFindBackDict)
		exp, money, rmb, reputation, items, tili = 0, 0, 0, 0, {}, 0
		for index, cnt in cntFindBackDict.items():
			if FindBackDefine.IsSpecilFB(index):
				scfg = FindBackConfig.GetMoneyReward(role, index)
				if not scfg:
					print "GE_EXC, OneKeyMoneyFindBack"
					continue
				exp_1, money_1, rmb_1, reputation_1, items_1, tili_1 = scfg.RewardRole(role, index, cnt, FindBackDefine.MoneyReward)
			else:
				exp_1, money_1, rmb_1, reputation_1, items_1, tili_1 = rewardCfg.RewardRole(role, index, cnt, FindBackDefine.MoneyReward)
				
			cntFindBackDict[index] = 0
			exp += exp_1
			money += money_1
			rmb += rmb_1
			reputation += reputation_1
			tili += tili_1
			for i, c in items_1.iteritems():
				items[i] = items.get(i, 0) + c
		
		role.CallBackFunction(backId, cntFindBackDict)
		sname =",".join(systemNames)
		role.Msg(2, 0, PackFindTips(GlobalPrompt.FindBackTips_1 % sname, exp, money, rmb, reputation, items, tili))
	
	if hasDemon and ((not role.GetI1(EnumInt1.DemonDefenseIn)) or (not role.GetI1(EnumInt1.MDragonComeIn))):
		#魔兽入侵在更新后保留之前的找回
		#找回后需要重新参与魔兽入侵和魔龙降临后激活
		if index in cntDict:
			del cntDict[index]
		if index in fbdict[2]:
			del fbdict[2][index]
	
################################################################################
#系统参与后触发今天的找回次数失去了 修正 nowday
def AfterJoinQandA(role, param):
	TodayTrigger(role, FindBackDefine.QNAFB)

def AfterJoinDF(role, param):
	TodayTrigger(role, FindBackDefine.DFFB)

def AfterJoinHW(role, param):
	TodayTrigger(role, FindBackDefine.HWFB)

def AfterJoinJJC(role, param):
	TodayTrigger(role, FindBackDefine.JJCFB)

def AfterTiLiTask(role, param):
	TodayTrigger(role, FindBackDefine.TILIFB)

def AfterDayTask(role, param):
	TodayTrigger(role, FindBackDefine.DAYTASKFB)

def AfterFB(role, param):
	TodayTrigger(role, FindBackDefine.FBFB)

def AfterHT(role, param):
	TodayTrigger(role, FindBackDefine.HTFB)

def AfterDL(role, param):
	TodayTrigger(role, FindBackDefine.DLFB)

def AfterCFB(role, param):
	TodayTrigger(role, FindBackDefine.CFBFB)

################################################################################
#特殊体力溢出找回
def AfterTiLiJap(role, tiliJap):
	if not role or role.IsKick():
		return
	if Environment.IsCross or role.GetLevel() < NeedLevel:
		return
	fbdict = role.GetObj(EnumObj.FindBackData)
	if 1 not in fbdict:
		InitFindBackData(role)
		fbdict = role.GetObj(EnumObj.FindBackData)
	
	cntDict = fbdict[1]
	cfg = FindBackConfig.FindBackConfig_Dict.get(FindBackDefine.TILIFB)
	if not cfg:
		print "GE_EXC AfterTiLiJap, not cfg"
		return
	key = FindBackDefine.TILIFB
	cntDict[key] = min(cntDict.get(key, 0) + tiliJap, cfg.maxTimes)
	dayDict = fbdict[2]
	nowdays = cDateTime.Days()
	if key not in dayDict:
		dayDict[key] = nowdays - 1
	
	
################################################################################
def TodayTrigger(role, key):
	#今天这个key不能找回了 修正 nowday
	if role.GetLevel() < NeedLevel:
		return
	tset = role.GetTempObj(EnumTempObj.FindBakcTrigger)
	if key in tset:
		return
	
	nowdays = cDateTime.Days()
	fbdict = role.GetObj(EnumObj.FindBackData)
	dayDict = fbdict[2]
	if key not in dayDict:
		cntDict = fbdict[1]
		if key in cntDict:
			print "GE_EXC TodayTrigger error key repeat (%s)" % key
		cntDict[key] = 0
	#修正 nowday
	dayDict[key] = nowdays
	
	tset.add(key)

def CountFindBack(role, cntDict, dayDict, nowday, key, oldday, oldCnt):
	times = nowday - oldday - 1
	#需要隔一天才一次
	if times <= 0:
		return
	if key == FindBackDefine.QNAFB:
		return
	cfg = FindBackConfig.FindBackConfig_Dict.get(key)
	if not cfg:
		print "GE_EXC, error not (%s) cfg in findback login" % key
		#修正数据？
		return
	dayDict[key] = nowday - 1
	cntDict[key] = min(oldCnt + GetDayTimes(key, role) * times, cfg.maxTimes)
	return True

def GetDayTimes(key, role):
	#体力任务特殊
	if key == FindBackDefine.TILIFB:
		if role.GetLevel() < 60:
			return 30 * 2
		else:
			return 60 * 2
	elif key == FindBackDefine.FBFB:
		if not role.GetI16(EnumInt16.FB_Active_ID):
			return 0
	elif key == FindBackDefine.HTFB:
		if not role.GetI16(EnumInt16.HeroTempleMaxIndex):
			return 0
	elif key == FindBackDefine.CFBFB:
		if role.GetI8(EnumInt8.MarryStatus) != 3:
			return 0
	return 1
	

################################################################################
def AfterNewDay():
	nowday = cDateTime.Days()
	EFT = EnumTempObj.FindBakcTrigger
	EFD = EnumObj.FindBackData
	for role in cRoleMgr.GetAllRole():
		if role.GetLevel() < NeedLevel:
			continue
		role.SetTempObj(EFT, set())
		fbdict = role.GetObj(EFD)
		cntDict = fbdict[1]
		dayDict = fbdict[2]
		
		#计算昨天没做的事情
		needSync = False
		for key, oldday in dayDict.items():
			oldCnt = cntDict.get(key, 0)
			needSync = CountFindBack(role, cntDict, dayDict, nowday, key, oldday, oldCnt)
		
		if needSync is True:
			role.SendObj(FindBack_S_Data, role.GetObj(EnumObj.FindBackData)[1])

def AfterLogin(role, param):
	if role.GetLevel() < NeedLevel:
		return
	role.SetTempObj(EnumTempObj.FindBakcTrigger, set())
	
	nowday = cDateTime.Days()
	fbdict = role.GetObj(EnumObj.FindBackData)
	if 1 not in fbdict:
		InitFindBackData(role)
		fbdict = role.GetObj(EnumObj.FindBackData)
	
	cntDict = fbdict[1]
	dayDict = fbdict[2]
	
	for key, oldday in dayDict.items():
		oldCnt = cntDict.get(key, 0)
		CountFindBack(role, cntDict, dayDict, nowday, key, oldday, oldCnt)

def AfterLevelUp(role, param):
	if role.GetLevel() == NeedLevel:
		role.SetTempObj(EnumTempObj.FindBakcTrigger, set())
		InitFindBackData(role)
		
		
def SyncRoleOtherData(role, param):
	if role.GetLevel() < NeedLevel:
		return
	#登录同步找回系统数据
	role.SendObj(FindBack_S_Data, role.GetObj(EnumObj.FindBackData)[1])


################################################################################



if "_HasLoad" not in dir():
	if Environment.EnvIsQQ() or Environment.IsDevelop or Environment.EnvIsFT() or Environment.EnvIsNA() or Environment.EnvIsFR():
		if Environment.HasLogic and not Environment.IsCross:
			Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
			Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
			Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
			
			Event.RegEvent(Event.Eve_FB_AfterDF, AfterJoinDF)
			Event.RegEvent(Event.Eve_FB_AfterHW, AfterJoinHW)
			Event.RegEvent(Event.Eve_FB_AfterJJC, AfterJoinJJC)
			#Event.RegEvent(Event.Eve_FB_AfterQNA, AfterJoinQandA)
			
			Event.RegEvent(Event.Eve_FB_TiLiTask, AfterTiLiTask)
			Event.RegEvent(Event.Eve_FB_DayTask, AfterDayTask)
			Event.RegEvent(Event.Eve_FB_FB, AfterFB)
			Event.RegEvent(Event.Eve_FB_HT, AfterHT)
			Event.RegEvent(Event.Eve_FB_DL, AfterDL)
			Event.RegEvent(Event.Eve_FB_CFB, AfterCFB)
			
			
			cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
	
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FindBack_RMBFindBack", "请求神石找回"), RMBFindBack)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FindBack_OneKeyRMBFindBack", "请求一键神石找回"), OneKeyRMBFindBack)
			
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FindBack_BindRMBFindBack", "请求魔晶找回"), BindRMBFindBack)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FindBack_OneKeyBindRMBFindBack", "请求一键魔晶找回"), OneKeyBindRMBFindBack)
			
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FindBack_MoneyFindBack", "请求金币找回"), MoneyFindBack)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FindBack_OneKeyMoneyFindBack", "请求一键金币找回"), OneKeyMoneyFindBack)
			

