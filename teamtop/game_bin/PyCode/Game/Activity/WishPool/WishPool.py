#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WishPool.WishPool")
#===============================================================================
# 许愿池
#===============================================================================
import Environment
import cRoleMgr
import cComplexServer
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumSysData, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Activity.WishPool import WishPoolConfig
from Game.Role.Data import EnumInt32, EnumObj, EnumTempObj, EnumInt16
from Game.Role import Event
from Game.Role.Mail import Mail
from Game.Persistence import Contain
from Game.SysData import WorldData
from Game.ThirdParty.QQidip import QQEventDefine
from Game.Activity.HappyNewYear import NewYearDiscount

if "_HasLoad" not in dir():
	WishPoolBack = AutoMessage.AllotMessage("WishPoolBack", "许愿池许愿回调")
	WishPoolExData = AutoMessage.AllotMessage("WishPoolExData", "许愿池积分兑换数据")
	WishPoolWishCntData = AutoMessage.AllotMessage("WishPoolWishCntData", "许愿池每日许愿次数数据")
	WishPoolRecord = AutoMessage.AllotMessage("WishPoolRecord", "许愿池特定物品记录")
	
	WishPoolEx_Log = AutoLog.AutoTransaction("WishPoolEx_Log", "许愿池积分兑换日志")
	WishPoolWishOnce_Log = AutoLog.AutoTransaction("WishPoolWishOnce_Log", "许愿池许愿一次日志")
	WishPoolWishTen_Log = AutoLog.AutoTransaction("WishPoolWishTen_Log", "许愿池许愿十次日志")
	WishPoolWishTwenty_Log = AutoLog.AutoTransaction("WishPoolWishTwenty_Log", "许愿池许愿二十次日志")
	WishPoolWishHundred_Log = AutoLog.AutoTransaction("WishPoolWishHundred_Log", "许愿池许愿一百次次日志")

	
def RequestOpelWishPool(role, msg):
	'''
	请求打开许愿池
	@param role:
	@param msg:
	'''

	#同步特殊奖励记录
	global WishPoolRecordList
	role.SendObj(WishPoolRecord, WishPoolRecordList.data)
	
	#同步许愿池许愿记录
	role.SendObj(WishPoolWishCntData, role.GetObj(EnumObj.WishPoolWishRecord))
	
	#同步积分兑换记录
	role.SendObj(WishPoolExData, role.GetObj(EnumObj.WishPoolExRecord))
	
def RequestWish(role, msg):
	'''
	许愿
	@param role:
	@param msg:
	'''
	if not msg:
		return
	
	#许愿池索引 , 许愿次数
	index, cnt = msg
	
	#配置
	cfg = WishPoolConfig.WishPool_Dict.get(index)
	if not cfg:
		print "GE_EXC, RequestWish can not find index (%s) in WishPool_Dict" % index
		return
	
	#许愿需要等级
	if role.GetLevel() < cfg.needLevel:
		return
	
	#许愿池许愿记录
	wishCntRecord = role.GetObj(EnumObj.WishPoolWishRecord)
	
	#超过每日最大许愿次数
	if index in wishCntRecord and (wishCntRecord[index] + cnt) > cfg.maxCnt:
		return
	
	#现有的许愿石和需要的许愿石
	haveCnt = role.ItemCnt(cfg.needItemCoding)
	needCnt = cfg.needCnt * cnt
	
	useCnt = 0
	useRMB = 0
	
	if haveCnt >= needCnt:
		#道具足够, 优先使用道具
		useCnt = needCnt
	else:
		#道具不足使用神石替代道具
		useRMB = (needCnt - haveCnt) * cfg.needUnbindRMB
		useCnt = haveCnt
	
	#需要使用神石但神石不够
	if useRMB and role.GetUnbindRMB() < useRMB:
		return
	
	if not useRMB and not useCnt:
		print "GE_EXC, error in RequestWish"
		return
	
	#回调客户端播放特效, 完了发奖
	role.SendObjAndBack(WishPoolBack, None, 10, CallBackFun, (cfg, cnt, index, useCnt, useRMB, wishCntRecord))
	
def CallBackFun(role, callargv, regparam):
	cfg, cnt, index, useCnt, useRMB, wishCntRecord = regparam
	
	
	#需要使用道具但道具不够
	if useCnt and role.ItemCnt(cfg.needItemCoding) < useCnt:
		return
	
	#需要使用神石但神石不够
	if useRMB and role.GetUnbindRMB() < useRMB:
		return
	
	if not useRMB and not useCnt:
		print "GE_EXC, error in RequestWish CallBackFun"
		return
	
	if cnt == 1:
		with WishPoolWishOnce_Log:
			wish(role, cfg, cnt, index, useCnt, useRMB, wishCntRecord)
	elif cnt == 10:
		with WishPoolWishTen_Log:
			wish(role, cfg, cnt, index, useCnt, useRMB, wishCntRecord)
	elif cnt == 20:
		with WishPoolWishTwenty_Log:
			wish(role, cfg, cnt, index, useCnt, useRMB, wishCntRecord)
	elif cnt == 100:
		with WishPoolWishHundred_Log:
			wish(role, cfg, cnt, index, useCnt, useRMB, wishCntRecord)
		
def wish(role, cfg, cnt, index, useCnt, useRMB, wishCntRecord):
	#随机奖励 -- 不能用randomMany
	reward = []
	for _ in xrange(cnt):
		reward.append(cfg.randomReward.RandomOne())
	
	#生成奖励字典
	itemList = []
	tarotCardList = []
	for (tp, coding, nt) in reward:
		if tp == 1:
			#道具
			itemList.append([coding, nt])
			continue
		if tp == 2:
			#命魂
			tarotCardList.append(coding)
	if cnt == 100:
		#一百次额外奖励(策划暂定是物品)
		itemList.extend(cfg.extraReward)
	
	roleName = role.GetRoleName()
	tmpDict = {}
	needBroad = False
	global WishPoolRecordList
	recordLen = len(WishPoolRecordList)
	
	for (coding, nt) in itemList:
		if coding in tmpDict:
			tmpDict[coding] += nt
		else:
			tmpDict[coding] = nt
		#特殊物品记录
		if coding not in WishPoolConfig.WPRumorsSet:
			continue
		#有特殊物品了, 标志需要广播
		if not needBroad:
			needBroad = True
		#最多保存5条
		if recordLen >= 5:
			WishPoolRecordList.pop(0)
			recordLen -= 1
		WishPoolRecordList.append([roleName, (1, coding, nt)])
		recordLen += 1
		cRoleMgr.Msg(1, 0, GlobalPrompt.WishPoolSpecItem % (roleName, coding, nt))
	for cardID in tarotCardList:
		#特殊物品记录
		if cardID not in WishPoolConfig.WPRumorsSet:
			continue
		#有特殊物品了, 标志需要广播
		if not needBroad:
			needBroad = True
		#最多保存5条
		if recordLen >= 5:
			WishPoolRecordList.pop(0)
			recordLen -= 1
		WishPoolRecordList.append([roleName, (2, cardID, 1)])
		recordLen += 1
		cRoleMgr.Msg(1, 0, GlobalPrompt.WishPoolSpecTarot % (roleName, cardID, 1))
	
	
	#是否需要广播
	if needBroad:
		role.SendObj(WishPoolRecord, WishPoolRecordList.data)
		
	if useCnt:
		#使用道具
		role.DelItem(cfg.needItemCoding, useCnt)
	if useRMB:
		#使用神石
		role.DecUnbindRMB(useRMB)
		
		#新年乐翻天
		if NewYearDiscount.IsOpen:
			role.IncI32(EnumInt32.NewYearScore, useRMB)
	
	if not useCnt and not useRMB:
		print 'GE_EXC, wish pool wish use no items and not rmb?'
		return
	
	if cfg.maxCnt:
		#如果有次数限制的话记录许愿次数
		if index in wishCntRecord:
			wishCntRecord[index] += cnt
		else:
			wishCntRecord[index] = cnt
	
	role.IncI16(EnumInt16.WishPoolDayCnt, cnt)
	#发放奖励
	if role.PackageEmptySize() < len(tmpDict) \
	or role.GetTempObj(EnumTempObj.enTarotMgr).PackageEmptySize() < len(tarotCardList):
		#道具背包满或命魂背包满, 邮件发放奖励
		Mail.SendMail(role.GetRoleID(),
					GlobalPrompt.WishPoolMail_Title,
					GlobalPrompt.WishPoolMail_Sender,
					GlobalPrompt.WishPoolMail_Content,
					[(x, y) for x, y in tmpDict.iteritems()], tarotList = tarotCardList)
		role.Msg(2, 0, GlobalPrompt.WishPoolPackFull)
	else:
		tips = GlobalPrompt.WishPoolRevive
		for tarotCard in tarotCardList:
			role.AddTarotCard(tarotCard, 1)
			tips += GlobalPrompt.Tarot_Tips % (tarotCard, 1)
		for coding, nt in tmpDict.iteritems():
			role.AddItem(coding, nt)
			tips += GlobalPrompt.Item_Tips % (coding, nt)
		role.Msg(2, 0, tips)
		
	#加积分
	role.IncI32(EnumInt32.WishPoolScore, cfg.score * cnt)
	
	#尝试激活金币副本
	ActGoldMirror(role.GetRoleName(), cnt)
	
	role.SetObj(EnumObj.WishPoolWishRecord, wishCntRecord)
	role.SendObj(WishPoolWishCntData, wishCntRecord)
	#专题活动
	from Game.Activity.ProjectAct import ProjectAct, EnumProActType
	ProjectAct.GetFunByType(EnumProActType.ProjectWishEvent, (role, cnt))
	
	
	Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_WishPool)
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_WishPool, cnt))
	
def ActGoldMirror(roleName, cnt):
	#金币副本次数限制:最多一百次
	oldCnt = WorldData.GetWishPoolCnt()
	nowCnt = oldCnt + cnt
	#计算能激活几个金币副本
	actCnt = nowCnt / EnumGameConfig.WP_ActGoldCnt - oldCnt / EnumGameConfig.WP_ActGoldCnt
	#设置许愿池许愿次数
	WorldData.SetWishPoolCnt(nowCnt)
	
	#设置金币副本次数
	if actCnt:
		lastGoldCnt = WorldData.GetGoldMirrorCnt_1()
		if lastGoldCnt >= 100:
			return
		nowGoldCnt = lastGoldCnt + actCnt
		if nowGoldCnt >= 100:
			WorldData.SetGoldMirrorCnt_1(100)
		else:
			WorldData.SetGoldMirrorCnt_1(nowGoldCnt)
		cRoleMgr.Msg(1, 0, GlobalPrompt.WPG_Open % (roleName, nowCnt, nowGoldCnt))
	
def RequestScoreEx(role, msg):
	'''
	积分兑换
	@param role:
	@param msg:
	'''
	if not msg:
		return
	
	#兑换物品coding
	coding, cnt = msg
	
	#配置
	cfg = WishPoolConfig.ScoreShop_Dict.get(coding)
	if not cfg:
		print "GE_EXC, RequestScoreEx can not find coding (%s) in ScoreShop_Dict" % coding
		return
	
	#积分
	#积分 + 神石
	if cfg.needScore and role.GetI32(EnumInt32.WishPoolScore) < cfg.needScore * cnt:
		return
	if cfg.needUnbindRMB and role.GetUnbindRMB() < cfg.needUnbindRMB * cnt:
		return
	
	#背包空间不足
	if role.PackageIsFull():
		return
	
	#兑换记录
	exRecord = role.GetObj(EnumObj.WishPoolExRecord)
	
	if cfg.limitCnt:
		#限购
		if coding in exRecord and ((exRecord[coding] + cnt) > cfg.limitCnt):
			#超过每日限购数量
			return
		#记录购买数量
		if coding not in exRecord:
			exRecord[coding] = cnt
		else:
			exRecord[coding] += cnt
		role.SetObj(EnumObj.WishPoolExRecord, exRecord)
	
	with WishPoolEx_Log:
		if cfg.needScore:
			role.DecI32(EnumInt32.WishPoolScore, cnt * cfg.needScore)
		if cfg.needUnbindRMB:
			role.DecUnbindRMB(cfg.needUnbindRMB * cnt)
		
		#发放物品
		role.AddItem(coding, cnt)
	
	role.SendObj(WishPoolExData, role.GetObj(EnumObj.WishPoolExRecord))
	
def RoleDayClear(role, param):
	#每日清理兑换记录和许愿池许愿次数
	role.SetObj(EnumObj.WishPoolExRecord, {})
	role.SetObj(EnumObj.WishPoolWishRecord, {})
	
	role.SendObj(WishPoolExData, {})
	role.SendObj(WishPoolWishCntData, {})
	
	role.SetI16(EnumInt16.WishPoolDayCnt, 0)
	
def AfterNewDay():
	#清理许愿池许愿次数
	if EnumSysData.WishPoolCnt in WorldData.WD:
		#许愿池许愿次数
		WorldData.SetWishPoolCnt(0)
		#金币副本1次数
		WorldData.SetGoldMirrorCnt_1(0)
		#金币副本2次数
		WorldData.SetGoldMirrorCnt_2(0)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		WishPoolRecordList = Contain.List("WishPoolRecordList", (2038, 1, 1), isSaveBig = False)
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WishPool_Open", "请求打开许愿池"), RequestOpelWishPool)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WishPool_Wish", "请求许愿"), RequestWish)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WishPool_ScoreEx", "请求积分兑换"), RequestScoreEx)
	