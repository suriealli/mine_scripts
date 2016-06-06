#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.CatchingFish.CatchingFishMgr")
#===============================================================================
#捕鱼达人
#===============================================================================
import Environment
import cRoleMgr
import cDateTime
import cProcess
import cNetMessage
import cComplexServer
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage, PyMessage
from ComplexServer.Plug.Control import ControlProxy
from Game.Persistence import Contain
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumInt32
from Game.Activity.CatchingFish import CatchingFishConfig
from Game.Role import Call, Event
from Game.GlobalData import ZoneName
from Game.Role.Data import EnumObj
from ComplexServer import Init
if "_HasLoad" not in dir():
	IsStart = False
	IsControlSync = False
	CatchingFishItemsList = []				#跨服珍稀物品记录
	OwnerCalculus = []						#本服积分前10名
	BroadRoleIDSet = set()					#需要广播的角色ID集合
	AllCalculus = []						#跨服积分前10名
	YestDayCalculus = []					#昨天跨服积分前10名
	PoolValue = 0							#奖池神石数
	EndTime = 0								#活动结束时间
	OneTime = 20							#一次捕鱼费用
	TenTime = 190							#十次捕鱼费用
	FiftyTime = 900							#五十次捕鱼费用
	#捕鱼活动的消息
	CatchingFishStart = AutoMessage.AllotMessage("CatchingFishStart", "捕鱼活动开启")
	CatchingFishPoolValue = AutoMessage.AllotMessage("CatchingFishPoolValue", "捕鱼奖池神石数")
	#区服+角色名+奖励+时间
	CatchingFishItemRecord = AutoMessage.AllotMessage("CatchingFishItemRecord", "捕鱼跨服珍稀物品记录")
	CatchingFishCalculusRecord = AutoMessage.AllotMessage("CatchingFishCalculusRecord", "捕鱼积分排行榜")
	CatchingFishBoxData = AutoMessage.AllotMessage("CatchingFishBoxData", "捕鱼积分宝箱状态")
	GoCatchingFish = AutoMessage.AllotMessage("GoCatchingFish", "播放捕鱼动画")
	CatchFishYestDay =  AutoMessage.AllotMessage("CatchFishYestDay", "昨天捕鱼排行榜")
	#捕鱼活动的日志
	CatchingFish_Log = AutoLog.AutoTransaction("CatchingFish_Log", "捕鱼活动记录")
	CatchingFishBoxReward_Log = AutoLog.AutoTransaction("CatchingFishBoxReward_Log", "捕鱼宝箱奖励")
	


#=================================================================
#活动开关控制
#=================================================================
def OpenActive(callArgv, param):
	global IsStart
	IsStart = True
	if not CatchingFish_RANK_LIST.returnDB:
		return
	Initialization(param)


def CloseActive(callArgv, param):
	global IsStart
	if not IsStart :
		print "GE_EXC, CatchingFish has Closed"
	IsStart = False
	cNetMessage.PackPyMsg(CatchingFishStart, 0)
	cRoleMgr.BroadMsg()
	
#初始化数据
def Initialization(param):
	global BroadRoleIDSet, CatchingFishItemsList, AllCalculus, YestDayCalculus, PoolValue, IsControlSync
	activeId = param
	if activeId != CatchingFish_RANK_LIST.get("activeId") :
		CatchingFish_RANK_LIST.clear()
		CatchingFish_RANK_LIST["activeId"] = activeId
		CatchingFish_RANK_LIST["days"] = cDateTime.Days()
		OwnerCalculus = []
		CatchingFish_RANK_LIST["OwnerCalculus"] = OwnerCalculus
		CatchingFish_RANK_LIST["PoolValue"] = EnumGameConfig.CatchingFish_PoolValue 
	BroadRoleIDSet = set()
	CatchingFishItemsList = []
	AllCalculus = []
	YestDayCalculus = []
	#活动开启的时候向控制进程请求数据
	#积分排行榜数据
	ControlProxy.SendControlMsg(PyMessage.CatchingFish_Calculus_FromControl, cProcess.ProcessID)
	if not PoolValue :
		PoolValue = EnumGameConfig.CatchingFish_PoolValue
	cNetMessage.PackPyMsg(CatchingFishStart, 1)
	cRoleMgr.BroadMsg()
	IsControlSync = False
#=================================================================
#客户端请求
#=================================================================
def OpenCatchingFish(role, param):
	'''
	打开捕鱼达人面板
	@param role:
	@param param:
	'''
	global IsStart, PoolValue, CatchingFishItemsList, BroadRoleIDSet, IsControlSync
	if not IsStart :
		return
	if role.GetLevel() < EnumGameConfig.Level_30 :
		return
	roleId = role.GetRoleID()
	boxs = role.GetObj(EnumObj.CatchingFishBox)
	if roleId not in BroadRoleIDSet :
		BroadRoleIDSet.add(roleId)
	role.SendObj(CatchingFishItemRecord, CatchingFishItemsList)
	role.SendObj(CatchingFishPoolValue, PoolValue)
	role.SendObj(CatchingFishBoxData, boxs)

#关闭面板
def CloseCatchingFish(role, param):
	global IsStart, BroadRoleIDSet
	if not IsStart :
		return
	roleId = role.GetRoleID()
	if roleId in BroadRoleIDSet :
		BroadRoleIDSet.discard(roleId)

def CatchFish(role, param):
	'''
	捕鱼
	@param role:
	@param param:
	'''
	global IsStart
	if not IsStart :
		return
	if role.GetLevel() < EnumGameConfig.Level_30 :
		return
	
	if cDateTime.Hour() >= 23 and cDateTime.Minute() >= 55 :
		role.Msg(2, 0, GlobalPrompt.CatchingFishOverTime)
		return
	#小网捕鱼
	if param == 1 :
		if role.FindItem(EnumGameConfig.CatchingFish_ItemLittleCoding) :
			GetReward(role, (0, EnumGameConfig.CatchingFish_ItemLittleCoding, 1))
		elif role.GetUnbindRMB_Q() >= OneTime :
			GetReward(role, (1, OneTime, 1))
	#中网捕鱼
	elif param == 2 :
		if role.FindItem(EnumGameConfig.CatchingFish_ItemMidCoding) :
			GetReward(role, (0, EnumGameConfig.CatchingFish_ItemMidCoding, 10))
		elif role.GetUnbindRMB_Q() >= TenTime :
			GetReward(role, (1, TenTime, 10))
	#大网捕鱼
	elif param == 3 :
		if role.FindItem(EnumGameConfig.CatchingFish_ItemLargCoding) :
			GetReward(role, (0, EnumGameConfig.CatchingFish_ItemLargCoding, 50))
		elif role.GetUnbindRMB_Q() >= FiftyTime :
			GetReward(role, (1, FiftyTime, 50))
	
	role.SendObj(GoCatchingFish, param)
	
#抽奖
def GetReward(role, param):
	#消耗相应道具
	global PoolValue
	ways, counts, nums = param
	needcnt = role.GetI32(EnumInt32.CatchingFish)
	Minpool = 0
	Mincnt = 0
	for needpool in CatchingFishConfig.CatchingFishGrade.iterkeys() :
		if needpool[0] <= PoolValue and needpool[1] <= needcnt :
			if needpool[0] >= Minpool and needpool[1] >= Mincnt :
				Minpool, Mincnt = needpool

	cf = CatchingFishConfig.CatchingFishGrade.get((Minpool, Mincnt))
	if not cf :
		print "GE_EXC, No level %s needcnt %s in GetReward" % (Minpool, Mincnt)
		return
	#获取相应的抽奖机
	grade = cf.grade
	#获取相应的最低等级
	minlevel = 0
	for cf in CatchingFishConfig.CatchingFish_Dict.itervalues():
		if cf.minLevel > role.GetLevel() :
			continue
		if cf.minLevel >= minlevel:
			minlevel = cf.minLevel
	CatchingFishRandom = CatchingFishConfig.CatchingFishRandom_Dict.get((minlevel, grade))
	if not CatchingFishRandom :
		print "GE_EXC, NO CatchingFishRandom in GetReward where level %s grade %s" % (minlevel, grade)
		return
	itemslist = []
	i = 1
	while i <= nums :
		catchingIndex = CatchingFishRandom.RandomOne()
		CatchingFishItem = CatchingFishConfig.CatchingFish_Dict.get(catchingIndex)
		if not CatchingFishItem :
			print "GE_EXC, NO catchingIndex %s in GetReward" % catchingIndex
		itemslist.append(CatchingFishItem) 
		i += 1
	
	AwardDict = {}
	processId = cProcess.ProcessID
	zName = ZoneName.GetZoneName(processId)
	tips = ""
	tips += GlobalPrompt.Reward_Tips
	with CatchingFish_Log :
		if ways == 0 :
			role.DelItem(counts, 1)
		else :
			role.DecUnbindRMB_Q(counts)
		#获得奖金
		for CatchingFishItem in itemslist :
			if not CatchingFishItem.rewardItems :
				IncUnbindRMB_S = PoolValue * CatchingFishItem.rewardUnbindRMB_S_Percent / 100
				PoolValue -= IncUnbindRMB_S
				if CatchingFishItem.isRumor :
					Call.ServerCall(0, "Game.Activity.CatchingFish.CatchingFishMgr", "UpDateItemsList", (zName, role.GetRoleName(), 0, 0, IncUnbindRMB_S))
				#发送奖金
				role.IncUnbindRMB_S(IncUnbindRMB_S)
				tips += GlobalPrompt.UnBindRMB_Tips % IncUnbindRMB_S
			else :
				coding, cnt = CatchingFishItem.rewardItems
				if CatchingFishItem.isRumor :
					Call.ServerCall(0, "Game.Activity.CatchingFish.CatchingFishMgr", "UpDateItemsList", (zName, role.GetRoleName(), 1, coding, cnt))
				
				AwardDict[coding] = AwardDict.get(coding, 0) + cnt
				
			#增加奖金池
			PoolValue += EnumGameConfig.CatchingFish_IncValue
			needcnt += 10
			
		role.SetI32(EnumInt32.CatchingFish, needcnt)
		#发放奖励
		for coding, cnt in AwardDict.iteritems() :
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips % (coding, cnt)
	
	CatchingFish_RANK_LIST["PoolValue"] = PoolValue
	CatchingFish_RANK_LIST.HasChange()		
	UpdateOwnerCalculus(role.GetRoleID(), (needcnt, role.GetRoleID(), role.GetRoleName() ,role.GetLevel(), zName))
	UpdateCatchingFishBox(role)
	role.Msg(2, 0, tips)
	role.SendObj(CatchingFishPoolValue, PoolValue)



#打开达人排行榜
def GetAllCalculus(role, param):
	global IsStart, AllCalculus, YestDayCalculus, IsControlSync
	if not IsStart :
		return
	if not IsControlSync:
		return
	role.SendObj(CatchingFishCalculusRecord, AllCalculus)
	role.SendObj(CatchFishYestDay, YestDayCalculus)



def UpdateOwnerCalculus(roleid, param):
	'''
	更新本服最新前十名
	'''
	global OwnerCalculus
	for cf in OwnerCalculus:
		if cf[1] != roleid:
			continue
		index = OwnerCalculus.index(cf)
		OwnerCalculus[index] = param
		CatchingFish_RANK_LIST["OwnerCalculus"] = OwnerCalculus
		CatchingFish_RANK_LIST.HasChange()
		return
	
	if len(OwnerCalculus) >= 10 :
		OwnerCalculus.append(param)
		OwnerCalculus.sort(key=lambda x:(-x[0], -x[1]))
		OwnerCalculus.pop()
	else :
		OwnerCalculus.append(param)
	CatchingFish_RANK_LIST["OwnerCalculus"] = OwnerCalculus
	CatchingFish_RANK_LIST.HasChange()
		
#更新宝箱状态
def UpdateCatchingFishBox(role):
	owncalculs = role.GetI32(EnumInt32.CatchingFish)
	boxs = role.GetObj(EnumObj.CatchingFishBox)
	level = role.GetLevel()
	index = 0
	for cf in CatchingFishConfig.CatchingFishBox.itervalues() :
		if cf.MinLevel <= level <= cf.MaxLevel:
			if boxs[cf.boxIndex-1]==0 and owncalculs >= cf.needCnt :
				boxs[cf.boxIndex-1] = 1
				index += 1
				
	role.SetObj(EnumObj.CatchingFishBox, boxs)
	role.SendObj(CatchingFishBoxData, boxs)

#获取积分宝箱
def GetCatchingFishBox(role, index):
	global IsStart
	if not IsStart :
		return
	level = role.GetLevel()
	minLevel = 0
	for cf in CatchingFishConfig.CatchingFishBox.itervalues() :
		if cf.MinLevel <= level :
			if cf.MinLevel >= minLevel :
				minLevel =cf.MinLevel
	
	boxcf = CatchingFishConfig.CatchingFishBox.get((index + 1, minLevel))
	if not boxcf :
		return
	cnt = role.GetI32(EnumInt32.CatchingFish)
	
	if cnt < boxcf.needCnt :
		return
	boxs = role.GetObj(EnumObj.CatchingFishBox)
	if boxs[index] == 2 :
		return
	#发放奖励
	tips = ""
	tips += GlobalPrompt.Reward_Tips
	with CatchingFishBoxReward_Log :
		boxs[index] = 2
		role.SetObj(EnumObj.CatchingFishBox, boxs)
		role.IncMoney(boxcf.rewardMoney)
		role.IncBindRMB(boxcf.rewardBindRMB)
		if boxcf.rewardUnbindRMB_S :
			role.IncUnbindRMB_S(boxcf.rewardUnbindRMB_S)
			tips += GlobalPrompt.UnBindRMB_Tips % (boxcf.rewardUnbindRMB_S)
		for coding, cnt in boxcf.rewardItems :
			role.AddItem(coding, cnt)
			tips += GlobalPrompt.Item_Tips % (coding, cnt)
	
	tips += GlobalPrompt.BindRMB_Tips % boxcf.rewardBindRMB
	tips += GlobalPrompt.Money_Tips % boxcf.rewardMoney
	
	role.Msg(2, 0, tips)
		
	role.SendObj(CatchingFishBoxData, boxs)
#===============================================================================
# ServerCall函数
#===============================================================================
def UpDateItemsList(param):
	global CatchingFishItemsList, BroadRoleIDSet
	zName, rName, isItem, coding, cnt = param
	
	if len(CatchingFishItemsList) > 50 :
		CatchingFishItemsList.pop(0)
	
	CatchingFishItemsList.append([zName, rName, isItem, coding, cnt, cDateTime.Seconds()])
	for troleId in BroadRoleIDSet:
		trole = cRoleMgr.FindRoleByRoleID(troleId)
		if not trole:
			continue
		trole.SendObj(CatchingFishItemRecord, CatchingFishItemsList)
#===============================================================================
# 持久化数据载入
#===============================================================================
def AfterLoad():
	global IsStart, OwnerCalculus, PoolValue
	
	if not CatchingFish_RANK_LIST:
		#活动id不一样的时候清理数据
		CatchingFish_RANK_LIST["activeID"] = 0
	if "OwnerCalculus" not in CatchingFish_RANK_LIST :
		CatchingFish_RANK_LIST["OwnerCalculus"] = []
	if "days" not in CatchingFish_RANK_LIST :
		CatchingFish_RANK_LIST["days"] = 0
	if "PoolValue" not in CatchingFish_RANK_LIST :
		CatchingFish_RANK_LIST["PoolValue"] = EnumGameConfig.CatchingFish_PoolValue
	if cDateTime.Days() == CatchingFish_RANK_LIST["days"] :
		OwnerCalculus = CatchingFish_RANK_LIST["OwnerCalculus"]
	PoolValue = CatchingFish_RANK_LIST["PoolValue"]
	if IsStart :
		from Game.Activity import CircularActive
		CircularActive.OpenCatchingFishActive()

def RequestLogicCatchingFishCalculus(sessionid, msg):
	#控制进程请求逻辑进程返回当天排行榜的数据
	global OwnerCalculus
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, OwnerCalculus))
	
def UpdateCatchingFishCalculus(sessionid, msg):
	#逻辑进程更新排行榜数据
	global AllCalculus, IsControlSync, IsStart, YestDayCalculus
	if not IsStart :
		return
	AllCalculus , YestDayCalculus= msg
	if not AllCalculus and not YestDayCalculus:
		return
	IsControlSync = True

def TryUpdate():
	global IsStart
	if not IsStart: return
	
	#起服的时候尝试向控制进程请求数据
	ControlProxy.SendControlMsg(PyMessage.CatchingFish_Calculus_FromControl, cProcess.ProcessID)
#===============================================================================
# 角色事件
#===============================================================================
def BeforeExit(role, param):
	global IsStart
	if not IsStart: return
	
	global BroadRoleIDSet
	roleId = role.GetRoleID()
	
	BroadRoleIDSet.discard(roleId)
	
def SyncRoleOtherData(role, param):
	global IsStart
	if not IsStart:return
	if not role.GetObj(EnumObj.CatchingFishBox) :
		role.SetObj(EnumObj.CatchingFishBox, [0] * 20)
	UpdateCatchingFishBox(role)	
	role.SendObj(CatchingFishStart, 1)
#个人数据清理（每天）
def ClearRoleDateAfterDay(role, param):
	#个人积分宝箱数量，如果超过20个，则需要添加
	role.SetObj(EnumObj.CatchingFishBox, [0] * 20)
	role.SetI32(EnumInt32.CatchingFish, 0)
	boxs = role.GetObj(EnumObj.CatchingFishBox)
	role.SendObj(CatchingFishBoxData, boxs)

def ClearDayDate():
	global OwnerCalculus
	OwnerCalculus = []
	if CatchingFish_RANK_LIST.get("OwnerCalculus") :
		CatchingFish_RANK_LIST["OwnerCalculus"] = OwnerCalculus
		CatchingFish_RANK_LIST.HasChange()

def SetNewDay():
	global IsStart
	if not IsStart:return
	CatchingFish_RANK_LIST["days"] = cDateTime.Days() 
	ClearDayDate()

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		CatchingFish_RANK_LIST = Contain.Dict("CatchingFish_RANK_LIST", (2038, 1, 1), AfterLoad)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("OpenCatchingFish", "捕鱼达人打开面板"), OpenCatchingFish)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CloseCatchingFish", "捕鱼达人关闭面板"), CloseCatchingFish)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("CatchFish", "捕鱼达人捕鱼"), CatchFish)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GetAllCalculus", "打开捕鱼达人排行榜"), GetAllCalculus)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GetCatchingFishBox", "获得捕鱼达人积分宝箱"), GetCatchingFishBox)
		#发送跨服排行榜数据到逻辑进程
		cComplexServer.RegDistribute(PyMessage.CatchingFish_CalculusToLogicControl, UpdateCatchingFishCalculus)
		#发送逻辑服当天的数据到控制进程
		cComplexServer.RegDistribute(PyMessage.CatchingFish_Calculs_FromLogic, RequestLogicCatchingFishCalculus)
		#起服调用
		Init.InitCallBack.RegCallbackFunction(TryUpdate)
		Event.RegEvent(Event.Eve_ClientLost, BeforeExit)
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_RoleDayClear, ClearRoleDateAfterDay)
		#清理服当天的数据
		cComplexServer.RegAfterNewDayCallFunction(SetNewDay)
