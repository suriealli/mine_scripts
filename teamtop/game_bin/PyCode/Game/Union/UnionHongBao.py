#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionHongBao")
#===============================================================================
# 公会红包  @author: Gaoshuai 2016
#===============================================================================
import random
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import  GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt32
from Game.Union import UnionMgr


if "_HasLoad" not in dir():
	
	OpenPanelDict = {}					#打开公会红包面板玩家id集合
	#公会红包消息
	UnionHongBaoAllData = AutoMessage.AllotMessage("UnionHongBaoAllData", "同步红包数据")
	UnionHongBaoChangeData = AutoMessage.AllotMessage("UnionHongBaoChangeData", "同步红包状态改变数据")
	UnionHongBaoNewRecordData = AutoMessage.AllotMessage("UnionHongBaoNewRecordData", "同步红包新数据记录")
	UnionHongBaoRocordData = AutoMessage.AllotMessage("UnionHongBaoRocordData", "同步红包领取发放记录")
	UnionHongBaoDetail = AutoMessage.AllotMessage("UnionHongBaoDetail", "同步红包明细")
	
	#公会红包日志
	Tra_SetUnionHongBao = AutoLog.AutoTransaction("Tra_SetUnionHongBao", "玩家发红包 ")
	Tra_GetUnionHongBao = AutoLog.AutoTransaction("Tra_GetUnionHongBao", "玩家领取红包 ")
	Tra_UseUnionHongBaoItem = AutoLog.AutoTransaction("Tra_UseUnionHongBaoItem", "使用公会红包道具发红包 ")
	
	
def randomHongBao(total, num, MaxPercent=70):
	if num == 1:
		return [total]
	minMoney = 1
	maxMoney = total * MaxPercent / 100
	randomList = []
	for i in range(0, num):
		tmp = 0
		whileCnt = 0
		while True:
			whileCnt += 1
			#以total / num 为期望和方差随机
			tmp = int(random.normalvariate(total / num , total / num + 3))
			if minMoney < tmp < maxMoney:
				break
			elif whileCnt > num:
				tmp = (minMoney + maxMoney) / 2
				break
		randomList.append(tmp)
	last = total - sum(randomList)
	while last != 0:
		averageNum = max(abs(last / num), 1)
		for i in range(0, num):
			if last > 0:
				if randomList[i] + averageNum > maxMoney:
					continue
				randomList[i] += averageNum
				last -= averageNum
			elif last < 0:
				if randomList[i] - averageNum < minMoney:
					continue
				randomList[i] -= averageNum
				last += averageNum
			else:
				break
	random.shuffle(randomList)
	return randomList


def RequestSetUnionHongBao(role, param):
	'''
	请求发公会红包
	@param role:
	@param param: (红包金额，红包数量， 红包祝福语)
	'''
	#检查参数是否合法
	RMB, cnt, message = param
	#钱不够
	if RMB > role.GetUnbindRMB_Q():
		return
	#红包金额太大
	if RMB > EnumGameConfig.UnionHongBaoMaxRMB:
		return
	#数量不对
	if cnt < EnumGameConfig.UnionHongBaoMinCnt or cnt > RMB:
		return
	#祝福语长度太长
	if len(message) > EnumGameConfig.UnionHongBaoMessageLen:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	moneyList = randomHongBao(RMB, cnt)
		#玩家发红包
	with Tra_SetUnionHongBao:
		#删除物品及其他操作
		role.DecUnbindRMB_Q(RMB)
		#红包闹新春数据。跨天会清零
		role.IncI32(EnumInt32.SpringHongBaoRMB, RMB)
		hongbaoid = unionObj.SetHongBao(role.GetRoleID(), role.GetRoleName(), moneyList, message)
		#记得加日志
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveSetUnionHongBao, (RMB, cnt, role.GetUnionID(), hongbaoid))
	
	#向打开领红包面板的玩家同步该红包
	global OpenPanelDict
	rolesSet = OpenPanelDict.get(role.GetUnionID(),set())
	for tmpId in rolesSet:
		#打开面板的玩家，同步红包数据
		tmpRole = cRoleMgr.FindRoleByRoleID(tmpId)
		if not tmpRole:
			continue
		#新红包(0,hongbaoid,roleName)
		tmpRole.SendObj(UnionHongBaoChangeData, (0, hongbaoid, role.GetRoleName()))
		tmpRole.SendObj(UnionHongBaoNewRecordData, (role.GetRoleName(), message))
	for tmpId in unionObj.GetOnLineMemberIds():
		#在线玩家同步显示叹号，打开面板的玩家不处理
		if tmpId in rolesSet:
			continue
		tmpRole = cRoleMgr.FindRoleByRoleID(tmpId)
		if not tmpRole:
			continue
		tmpRole.SendObj(UnionMgr.UnionHongBaoShowTips, True)
	
	UnionMgr.UnionMsg(role.GetUnionObj(), GlobalPrompt.UnionHongBaoSet_Tip % (role.GetRoleName(), message))


def UseItemSetUnionHongBao(role, item, cnt):
	#请求使用内部发公会红包道具
	
	itemCoding = item.GetItemCoding()
	
	if role.ItemCnt(itemCoding) < 1:
		return
	#每次只能使用一个道具
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	moneyList = randomHongBao(EnumGameConfig.UnionHongBaoRMB, EnumGameConfig.UnionHongBaoCnt)
	with Tra_UseUnionHongBaoItem:
		role.DelItem(itemCoding, 1)
		role.IncI32(EnumInt32.SpringHongBaoRMB, 100)
		hongbaoid = unionObj.SetHongBao(role.GetRoleID(), role.GetRoleName(), moneyList, GlobalPrompt.UnionHongBaoMessage)
	
	#向打开领红包面板的玩家同步该红包
	global OpenPanelDict
	rolesSet = OpenPanelDict.get(role.GetUnionID(), set())
	for tmpId in rolesSet:
		#打开面板的玩家，同步红包数据
		tmpRole = cRoleMgr.FindRoleByRoleID(tmpId)
		if not tmpRole:
			continue
		#新红包(0,hongbaoid,roleName)
		tmpRole.SendObj(UnionHongBaoChangeData, (0, hongbaoid, role.GetRoleName()))
		tmpRole.SendObj(UnionHongBaoNewRecordData, (role.GetRoleName(), GlobalPrompt.UnionHongBaoMessage))
	for tmpId in unionObj.GetOnLineMemberIds():
		#在线玩家同步显示叹号，打开面板的玩家不处理
		if tmpId in rolesSet:
			continue
		tmpRole = cRoleMgr.FindRoleByRoleID(tmpId)
		if not tmpRole:
			continue
		tmpRole.SendObj(UnionMgr.UnionHongBaoShowTips, True)
	
	UnionMgr.UnionMsg(role.GetUnionObj(), GlobalPrompt.UnionHongBaoSet_Tip % (role.GetRoleName(), GlobalPrompt.UnionHongBaoMessage))
	role.Msg(2, 1, GlobalPrompt.UnionHongBaoUseCntError)


def RequestGetUnionHongBao(role, param):
	'''
	玩家领取公会红包
	@param role:
	@param param: 回调Id, 红包Id
	'''
	#消息参数是否合法
	callBackId, hongbaoId = param
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	CanGetFlag = unionObj.CanGetHongBao(hongbaoId, role.GetRoleID())
	if CanGetFlag == 1:
		#红包已经过期
		role.CallBackFunction(callBackId, -1)
		role.Msg(2, 0, GlobalPrompt.UnionHongBaoOutData)
		return
	elif CanGetFlag == 2:
		#红包已经领取或被领完
		role.CallBackFunction(callBackId, 0)
		role.SendObj(UnionHongBaoChangeData, (1, hongbaoId, None))
		return
	roleName = role.GetRoleName()
	with Tra_GetUnionHongBao:
		flag, SetName, RMB = unionObj.GetHongBao(hongbaoId, role.GetRoleID(), roleName)
		#加神石
		role.IncUnbindRMB_S(RMB)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveGetUnionHongBao, (RMB, role.GetUnionID(), hongbaoId))
		
	role.CallBackFunction(callBackId, RMB)
	role.SendObj(UnionHongBaoChangeData, (1, hongbaoId, None))
	#向打开领红包面板的玩家更新此红包数据
	global OpenPanelDict
	#newRecord = 领红包角色名，发红包角色名，神石数
	newRecord = (roleName, SetName, RMB) 
	for tmpId in OpenPanelDict.get(role.GetUnionID(), []):
		tmpRole = cRoleMgr.FindRoleByRoleID(tmpId)
		if not tmpRole:
			continue
		if flag == 0:
			tmpRole.SendObj(UnionHongBaoChangeData, (1, hongbaoId, None))
		tmpRole.SendObj(UnionHongBaoNewRecordData, newRecord)
	UnionMgr.UnionMsg(role.GetUnionObj(), GlobalPrompt.GetHongBaoTip() % (roleName, SetName))


def RequestCloseUnionHongBaoPanel(role, msg):
	'''
	关闭发红包面板
	@param role:
	@param msg: None
	'''
	global OpenPanelDict
	OpenPanelDict.get(role.GetUnionID(), set()).discard(role.GetRoleID())
	
	
def RequestOpenUnionHongBaoPanel(role, msg):
	'''
	打开公会发红包面板
	@param role:
	@param msg: None
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	global OpenPanelDict
	unionId = role.GetUnionID()
	if unionId not in OpenPanelDict:
		OpenPanelDict[unionId] = set()
	OpenPanelDict[unionId].add(role.GetRoleID())
	#同步发送领取记录
	role.SendObj(UnionHongBaoAllData, unionObj.GetAllHongBao(role.GetRoleID()))
	role.SendObj(UnionHongBaoRocordData, unionObj.GetRecordList())
	
	
def RequestUnionHongBaoDetail(role, hongbaoId):
	'''
	查看公会红包
	@param role:
	@param hongbaoId: 红包Id
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	detailList = unionObj.GetHongBaoDetail(hongbaoId, role.GetRoleID())
	role.SendObj(UnionHongBaoDetail, detailList)
	if not detailList:
		role.Msg(2, 0, GlobalPrompt.UnionHongBaoOutData)


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and not Environment.EnvIsTK() and not Environment.EnvIsEN():
		#角色登陆同步其它数据
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestSetUnionHongBao", "发公会红包"), RequestSetUnionHongBao)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetUnionHongBao", "领公会红包"), RequestGetUnionHongBao)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenUnionHongBaoPanel", "打开公会红包面板"), RequestOpenUnionHongBaoPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestCloseUnionHongBaoPanel", "关闭公会红包面板"), RequestCloseUnionHongBaoPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestUnionHongBaoDetail", "查看公会红包"), RequestUnionHongBaoDetail)
