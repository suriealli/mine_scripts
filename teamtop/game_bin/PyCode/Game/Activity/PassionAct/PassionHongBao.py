#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionHongBao")
#===============================================================================
# 幸运红包  @author Gaoshuai 2015
#===============================================================================
import cRoleMgr
import Environment
import cComplexServer
import random
from Game.Persistence import Contain
from Game.Role import Event
from Game.Activity import CircularDefine
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Union import UnionMgr
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Activity.PassionAct.PassionHongBaoConfig import HongBaoDict


if "_HasLoad" not in dir():
	IsStart = False
	#消息
	# 格式：红包总数, [红包随机列表], [红包领取的角色名]
	HongBaoDetailData = AutoMessage.AllotMessage("HongBaoDetailData", "幸运红包数据")
	HongBaoChangedData = AutoMessage.AllotMessage("HongBaoChangedData", "红包状态改变")
	#  格式: (分包Id，分包总数)，[(是否可领, hongbaoId, 发红包的角色名)]
	HongBaoOpenPanelData = AutoMessage.AllotMessage("HongBaoOpenPanelData", "打开红包面板数据")
	#日志
	TraSetHongBao = AutoLog.AutoTransaction("TraSetHongBao", "玩家发红包")
	TraGetHongBao = AutoLog.AutoTransaction("TraGetHongBao", "玩家领红包")
	
	OpenPanelSet = set()
	HongbaoMaxNum = 30  #幸运红包，最多领取个数
	MaxHongBaoPanelCnt = 160#红包面板最多显示红包数
	MessageLen = 15 * 3		#红包祝福语最多15个汉字, 每个汉字占三个编码长度
	
	
	Enum_Version = 1#版本号
	Enum_All = 2	#所有红包
	Enum_Union = 3	#世界红包
	Enum_Role = 4	#红包
	Enum_Id = 5		#红包Id


def StartCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_PassionHongBao:
		return
	if IsStart:
		print 'GE_EXC, PassionHongBao is already start'
	IsStart = True



def EndCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_PassionHongBao:
		return
	if not IsStart:
		print 'GE_EXC, PassionHongBao is already end'
	IsStart = False


def randomHongBao(total, num, MaxPercent):
	if num == 1:
		return [total]
	minMoney = 5 - num / 5
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
		averageNum = max(last / num, 1)
		for i in range(0, num):
			if last > 0:
				if randomList[i] + averageNum >= maxMoney:
					continue
				randomList[i] += averageNum
				last -= averageNum
			elif last < 0:
				if randomList[i] - averageNum <= minMoney:
					continue
				randomList[i] -= averageNum
				last += averageNum
			else:
				break
	random.shuffle(randomList)
	return randomList


def AllotHongBaoID():
	global Enum_Id
	HONGBAO_DICT[Enum_Id] += 1
	return HONGBAO_DICT[Enum_Id]


def RequestSetHongBao(role, param):
	'''
	请求发幸运红包
	@param role:
	@param param: 红包coding，红包数量， 红包祝福语，红包类型(世界:1、工会:2)
	'''
	global IsStart
	if not IsStart:return
	
	#检查参数是否合法
	coding, cnt, message, HongBaotype = param
	if coding not in HongBaoDict:
		return
	if cnt not in HongBaoDict[coding].cnts:
		return
	
	if len(message) > MessageLen:
		return
	UnionID = role.GetUnionID()
	if HongBaotype not in (1, 2) or (HongBaotype == 2 and UnionID == 0):
		return
	
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	
	if role.ItemCnt(coding) < 1:
		return
	
	moneyList = randomHongBao(HongBaoDict[coding].RMB, cnt, HongBaoDict[coding].maxPercent)
	global HONGBAO_DICT
	unionDict = HONGBAO_DICT[Enum_Union]
	
	if len(unionDict[1]) + len(unionDict.get(UnionID, [])) >= MaxHongBaoPanelCnt:
		totalNum = 0
		for tmpId in unionDict[1]:
			honbaoList = HONGBAO_DICT[Enum_All].get(tmpId)
			if honbaoList > 0:
				totalNum += 1
		for tmpId in unionDict.get(UnionID, []):
			honbaoList = HONGBAO_DICT[Enum_All].get(tmpId)
			if honbaoList > 0:
				totalNum += 1
		if totalNum >= MaxHongBaoPanelCnt:
			role.Msg(2, 0, GlobalPrompt.CannotSendHongBao)
			return
	newHongBaoID = AllotHongBaoID()
	with TraSetHongBao:
		role.DelItem(coding, 1)
		if HongBaotype == 1:
			HONGBAO_DICT[Enum_All][newHongBaoID] = [role.GetRoleName(), moneyList, [], 1]
			unionDict[1].append(newHongBaoID)#世界未领取红包
		elif HongBaotype == 2:
			HONGBAO_DICT[Enum_All][newHongBaoID] = [role.GetRoleName(), moneyList, [], UnionID]
			if UnionID not in unionDict:
				unionDict[UnionID] = []
			unionDict[UnionID].append(newHongBaoID)#公会未领取红包				
	HONGBAO_DICT.HasChange()
	#打开面板的用户实时更新
	global  OpenPanelSet
	oldSet = set()
	for tmpId in OpenPanelSet:
		tmpRole = cRoleMgr.FindRoleByRoleID(tmpId)
		if not tmpRole:
			oldSet.add(tmpId)
			continue
		if HongBaotype == 2 and tmpRole.GetUnionID() != UnionID:
			continue
		tmpRole.SendObj(HongBaoChangedData, (1, newHongBaoID, role.GetRoleName()))
	OpenPanelSet -= oldSet
	#提示消息
	if 1 == HongBaotype:#世界红包
		cRoleMgr.Msg(1, 1, GlobalPrompt.HonBao_Tip % (role.GetRoleName(), message))	
	elif 2 == HongBaotype:#公会红包
		UnionMgr.UnionMsg(role.GetUnionObj(), GlobalPrompt.HonBao_Tip % (role.GetRoleName(), message))


def RequestGetHongBao(role, msg):
	'''
	请求领取幸运红包
	@param role:
	@param msg: 回调Id, 红包ID
	'''
	global IsStart
	if not IsStart: return
	#消息参数是否合法
	callBackId, hongbaoId = msg
	
	global HONGBAO_DICT
	allHongBaoDict = HONGBAO_DICT[Enum_All]
	#客户端参数错误，不存在此红包
	if hongbaoId not in allHongBaoDict:
		return
	
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	
	#红包领完
	hongbaoList = allHongBaoDict[hongbaoId]
	if hongbaoList[3] == 0 or (hongbaoList[3] > 1 and hongbaoList[3] != role.GetUnionID()):
		role.CallBackFunction(callBackId, 0)
		return
	
	#红包 已领取
	roleId = role.GetRoleID()
	roleDict = HONGBAO_DICT[Enum_Role]
	if roleId not in roleDict:
		roleDict[roleId] = []
	if hongbaoId in roleDict[roleId]:
		return
	
	#玩家达到红包领取上限
	if len(roleDict[roleId]) > HongbaoMaxNum:
		role.Msg(2, 0, GlobalPrompt.HongBaoOutMax)
		return
	
	money = hongbaoList[1][len(hongbaoList[2])]
	with TraGetHongBao:
		hongbaoList[2].append(role.GetRoleName())
		roleDict[roleId].append(hongbaoId)
		#加神石
		role.IncUnbindRMB_S(money)
	
	role.CallBackFunction(callBackId, money)
	
	#红包领完，更新面板数据
	if len(hongbaoList[1]) == len(hongbaoList[2]):
		global  OpenPanelSet
		oldSet = set()
		for tmpId in OpenPanelSet:
			tmpRole = cRoleMgr.FindRoleByRoleID(tmpId)
			if not tmpRole:
				oldSet.add(tmpId)
				continue
			if hongbaoList[3] > 1 and tmpRole.GetUnionID() == hongbaoList[3]:
				continue
			tmpRole.SendObj(HongBaoChangedData, (0, hongbaoId, None))
		OpenPanelSet -= oldSet
		hongbaoList[3] = 0	#设置红包为不可领取
	HONGBAO_DICT.HasChange()


def RequestHongBaoDetail(role, msg):
	'''
	查看幸运红包明细
	@param role:
	@param msg: 红包Id
	'''
	global IsStart
	if not IsStart: return
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	global HONGBAO_DICT
	
	if msg not in HONGBAO_DICT[Enum_All]:
		return
	HongBaoList = HONGBAO_DICT[Enum_All][msg]
	if HongBaoList[3] == 0:
		role.SendObj(HongBaoDetailData, (len(HongBaoList[1]), HongBaoList[1], HongBaoList[2]))
		return
	#该红包可以领取且玩家未领取
	roleDict = HONGBAO_DICT[Enum_Role]
	if msg not in roleDict.get(role.GetRoleID(), []) and len(roleDict.get(role.GetRoleID(), [])) < HongbaoMaxNum:
		return
	role.SendObj(HongBaoDetailData, (len(HongBaoList[1]), HongBaoList[1][0:len(HongBaoList[2])], HongBaoList[2]))


def RequestOpenHongBaoPanel(role, msg):
	'''
	打开幸运红包面板
	@param role:
	@param msg: None
	'''
	global IsStart
	if not IsStart: return
	if role.GetLevel() < EnumGameConfig.Level_30:
		return
	global OpenPanelSet, HONGBAO_DICT
	OpenPanelSet.add(role.GetRoleID())
	
	HongBaoList = []	#是否可领取，红包Id，发红包主角名
	
	unionDict = HONGBAO_DICT[Enum_Union]
	hongbaoDict = HONGBAO_DICT[Enum_All]
	#世界红包
	for hongbaoId in unionDict.get(1, []):
		hongbao = hongbaoDict.get(hongbaoId)
		if not hongbao:
			print "GE_EXC, Can find the HongBao where hongbaoId = %s" % hongbaoId
			continue
		flag = min(hongbao[3], 1)
		if hongbaoId in HONGBAO_DICT[Enum_Role].get(role.GetRoleID(), []):
			flag = 0
		HongBaoList.append((flag, hongbaoId, hongbao[0]))
	#公会红包
	if role.GetUnionID() != 0:
		for hongbaoId in unionDict.get(role.GetUnionID(), []):
			hongbao = hongbaoDict.get(hongbaoId)
			if not hongbao:
				print "GE_EXC, Can find the HongBao where hongbaoId = %s" % hongbaoId
				continue
			flag = min(hongbao[3], 1)
			if hongbaoId in HONGBAO_DICT[Enum_Role].get(role.GetRoleID(), []):
				flag = 0
			HongBaoList.append((flag, hongbaoId, hongbao[0]))
	
	HongBaoList.sort(key=lambda x:(-x[0], -x[1]))
	step = 8
	num = min(len(HongBaoList), MaxHongBaoPanelCnt) / step + 1
	for i in range(0, num):
		role.SendObj(HongBaoOpenPanelData, ((i + 1, num), HongBaoList[i * step: i * step + step]))


def RequestCloseHongBaoPanel(role, msg):
	'''
	关闭幸运红包面板
	@param role:
	@param msg: 参数注释
	'''
	global IsStart
	if not IsStart: return
	global OpenPanelSet
	OpenPanelSet.discard(role.GetRoleID())


def AfterDayClear():
	'''
	每日数据清理
	@param role:
	@param msg: None
	'''
	global IsStart
	if not IsStart:return
	global HONGBAO_DICT
	HONGBAO_DICT[Enum_All] = {}
	HONGBAO_DICT[Enum_Role] = {}
	HONGBAO_DICT[Enum_Union] = {1:[]}


def afterLoad():
	#初始化数据
	global HONGBAO_DICT
	if Enum_Version not in HONGBAO_DICT:
		HONGBAO_DICT[Enum_Version] = 0
	if Enum_All not in HONGBAO_DICT:
		HONGBAO_DICT[Enum_All] = {}
	if Enum_Role not in HONGBAO_DICT:
		HONGBAO_DICT[Enum_Role] = {}
	if Enum_Union not in HONGBAO_DICT:
		HONGBAO_DICT[Enum_Union] = {1:[]}
	if Enum_Id not in HONGBAO_DICT:
		HONGBAO_DICT[Enum_Id] = 0
	#激情活动版本号更新，清理红包数据
	from Game.Activity.PassionAct.PassionActVersionMgr import PassionVersion, Tra_PassionAct_UpdateVersion
	HongbaoVersion = HONGBAO_DICT.get(Enum_Version, 0)
	if PassionVersion == HongbaoVersion:
		return
	elif PassionVersion < HongbaoVersion:
		print "GE_EXC, PassionActVersionMgr::UpdateVersion PassionVersion(%s) < HongbaoVersion (%s)" % (PassionVersion, HongbaoVersion)
		return
	with Tra_PassionAct_UpdateVersion:
		HONGBAO_DICT.clear()
		HONGBAO_DICT[Enum_Version] = PassionVersion
		HONGBAO_DICT[Enum_All] = {}
		HONGBAO_DICT[Enum_Role] = {}
		HONGBAO_DICT[Enum_Union] = {1:[]}
		HONGBAO_DICT[Enum_Id] = 0


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		# {
		#  1: 激情活动版本号
		#  2: { 红包id: ( 角色名, [红包随机列表], [红包领取的角色名], 红包是否可以领取(1-世界红包可领取, 公会Id-公会红包可领取, 0-不可领取) ) },
		#  3: { 1: [ 世界红包Id ], 公会id :[ 公会红包Id ]
		#  4: { 主角id: [ 已领取红包Id ] }
		#  5: 红包id
		# }
		HONGBAO_DICT = Contain.Dict("HONGBAO_DICT", (2038, 1, 1), afterLoad)
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		
		cComplexServer.RegAfterNewDayCallFunction(AfterDayClear)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetHongBao", "请求领取幸运红包"), RequestGetHongBao)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestSetHongBao", "请求发幸运红包"), RequestSetHongBao)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestHongBaoDetail", "请求查看幸运红包"), RequestHongBaoDetail)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenHongBao", "请求打开幸运红包面板"), RequestOpenHongBaoPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestCloseHongBaoPanel", "请求关闭幸运红包面板"), RequestCloseHongBaoPanel)
		
