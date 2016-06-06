#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ShenWangBaoKu.ShenWangBaoKu")
#===============================================================================
# 神王宝库
#===============================================================================
import time
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
import DynamicPath
import Environment
from Game.Role import Event
from Util.File import TabFile
from Game.SysData import WorldData
from Game.Persistence import Contain
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Role.Data import EnumInt32, EnumObj
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Activity.ShenWangBaoKu import ShenWangBaoKuConfig


if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("ShenWangBaoKu")
	
	IsStart = False				#活动开启结束标志
	RoleOpenPanelSet = set()	#打开面板的角色id集合
	CallBackSec = 20				#回调超时时间
	ActVersion = 0
	IsStart = False
	EndTime = 0

	
	#消息
	SyncShenWangBaoKuStatu = AutoMessage.AllotMessage("SyncShenWangBaoKuStatu", "同步神王摆酷活动开启情况")
	SyncShenWangBaoKuServerData = AutoMessage.AllotMessage("SyncShenWangBaoKuServerData", "同步神王宝库服务器数据")
	SyncShenWangBaoKuPersonalData = AutoMessage.AllotMessage("SyncShenWangBaoKuPersonalData", "同步神王宝库商城个人数据")
	CallBackShenWangBaoKu = AutoMessage.AllotMessage("ShenWangBaoKucallback", "神王宝库转盘回调")
	#日志
	TraShenWangBaoKuOneTimeCost = AutoLog.AutoTransaction("TraShenWangBaoKuOneTimeCost", "神王宝库一次抽奖扣费")
	TraShenWangBaoKuOneTime = AutoLog.AutoTransaction("TraShenWangBaoKuOneTime", "神王宝库一次抽奖")
	TraShenWangBaoKuTenTime = AutoLog.AutoTransaction("TraShenWangBaoKuTenTime", "神王宝库十次抽奖")
	TraShenWangBaoExchange = AutoLog.AutoTransaction("TraShenWangBaoExchange", "神王宝库积分商店兑换")
	TraShenWangBaoVersion = AutoLog.AutoTransaction("TraShenWangBaoVersion", "神王宝库版本更替")
	

class ShenWangBaoKuTimeConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("ShiJianKongZhi.txt")
	def __init__(self):
		self.actVersion = int									#活动版本号
		self.beginTime = self.GetDatetimeByString				#开始时间
		self.endTime = self.GetDatetimeByString					#结束时间
	
	def Active(self):
		#开始时间戳
		beginTime = int(time.mktime(self.beginTime.timetuple()))
		#结束时间戳
		endTime = int(time.mktime(self.endTime.timetuple()))
		
		if endTime <= beginTime:
			print "GE_EXC, endTime <= beginTime in ShenWangBaoKuTimeConfig"
			return
		
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			Start(None, (endTime, self.actVersion))
			cComplexServer.RegTick(endTime - nowTime , End)
			
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, Start, (endTime, self.actVersion))
			cComplexServer.RegTick(endTime - nowTime , End)


def Start(callargv, param):
	global IsStart, EndTime, ActVersion
	if IsStart is True:
		print "GE_EXC,ShenWangBaoKu has been started"
		return
	#下两行不能调换顺序，因为要确保IsStart为真的时候，活动版本号已经初始化了
	EndTime, ActVersion = param
	IsStart = True
	
	global ShenWangBaoKuDict
	if ShenWangBaoKuDict.returnDB:
		if ShenWangBaoKuDict.get('ActVersion') != ActVersion:
			InitShenWangBaoKuDict()
	
	for theRole in cRoleMgr.GetAllRole():
		if not theRole:
			continue
		
		if theRole.GetI32(EnumInt32.ShenWangBaoKuVersion) != ActVersion:
			with TraShenWangBaoVersion:
				theRole.SetI32(EnumInt32.ShenWangBaoKuPoint, 0)
				theRole.SetI32(EnumInt32.ShenWangBaoKuVersion, ActVersion)
			
	#同步客户端活动开启
	cNetMessage.PackPyMsg(SyncShenWangBaoKuStatu, (IsStart, EndTime))
	cRoleMgr.BroadMsg()
	


def End(callargv, param):
	global IsStart, EndTime, ActVersion
	if IsStart is False:
		print "GE_EXC,ShenWangBaoKu has been ended"
		return
	IsStart = False
	EndTime = 0
	ActVersion = 0
	#同步客户端活动开启
	cNetMessage.PackPyMsg(SyncShenWangBaoKuStatu, (IsStart, EndTime))
	cRoleMgr.BroadMsg()


def LoadShenWangBaoKuTimeConfig():
	for cfg in ShenWangBaoKuTimeConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in ShenWangBaoKuTimeConfig"
			return
		#无依赖, 起服触发
		cfg.Active()


def RequestOneTime(role, msg):
	'''
	客户端请求一次抽奖
	'''
	if IsStart is False:
		return
	
	#角色身上的活动版本号与本次活动不一致
	if role.GetI32(EnumInt32.ShenWangBaoKuVersion) != ActVersion:
		return
	
	#奖池的活动版本号与本次活动不一致
	global ShenWangBaoKuDict
	if ShenWangBaoKuDict['ActVersion'] != ActVersion:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.ShenWangBaoKuNeedLevel:
		return
	
	costItemCnt = 1
	costUnbindRMB = 0
	if role.ItemCnt(EnumGameConfig.ShenWangBaoKuYiZhuCoding) < 1:
		costItemCnt = 0
		costUnbindRMB = EnumGameConfig.ShenWangBaoKuPerTimePrice
		if Environment.EnvIsNA():
			costUnbindRMB = EnumGameConfig.ShenWangBaoKuPerTimePrice_NA
		if role.GetUnbindRMB() < costUnbindRMB:
			return
	
	if costItemCnt <= 0 and costUnbindRMB <= 0:
		return
	
	config = ShenWangBaoKuConfig.RewardConfigDict.get(roleLevel)
	if config is None:
		return
	
	luckPool = ShenWangBaoKuDict['Pool']
	
	#只在奖池神石大于500的时候才可能随机到神石
	if luckPool >= 500:
		randomRate = config.randomRate1
	else:
		randomRate = config.randomRate2
	
	rewardIndex = randomRate.RandomOne()

	with TraShenWangBaoKuOneTimeCost:
		if costItemCnt > 0:
			role.DelItem(EnumGameConfig.ShenWangBaoKuYiZhuCoding, costItemCnt)
			
		elif costUnbindRMB > 0:
			role.DecUnbindRMB(costUnbindRMB)
			
		else:
			return
		
	role.SendObjAndBack(CallBackShenWangBaoKu, rewardIndex, CallBackSec, OneTimeCallBack, rewardIndex)
	

def OneTimeCallBack(role, callargv, regparam):
	'''
	一次抽奖客户端回调
	'''
	rewardIndex = regparam
	global ShenWangBaoKuDict
	
	config = ShenWangBaoKuConfig.RewardItemConfigDict.get(rewardIndex)
	if config is None:
		return
	
	tips = GlobalPrompt.Reward_Tips
	with TraShenWangBaoKuOneTime:
		
		role.IncI32(EnumInt32.ShenWangBaoKuPoint, EnumGameConfig.ShenWangBaoKuPointPerTime)
		if config.type == 1:
			role.AddItem(*config.thing)
			tips += GlobalPrompt.Item_Tips % config.thing
			
		elif config.type == 2:
			role.AddTarotCard(*config.thing)
			tips += GlobalPrompt.Tarot_Tips % config.thing
		#天赋卡	
		elif config.type == 3:
			role.AddTalentCard(config.thing)
			tips += GlobalPrompt.Talent_Tips % (config.thing, 1)
		#奖池神石	
		elif config.type == 4:
			pool = ShenWangBaoKuDict["Pool"]
			#记录当前奖池神石数
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveShenWangBaoKu, pool)
			rewardUnbindRMB = pool * config.thing / 100
			ShenWangBaoKuDict["Pool"] = pool - rewardUnbindRMB
			role.IncUnbindRMB_S(rewardUnbindRMB)
			tips += GlobalPrompt.UnBindRMB_Tips % rewardUnbindRMB
			
		else:
			return
		
		ShenWangBaoKuDict["Pool"] = ShenWangBaoKuDict.get("Pool", 0) + EnumGameConfig.ShenWangBaoKuIncPoolPerTime
		
		
		dataList = role.GetObj(EnumObj.ShenWangBaoKu).setdefault(1, [])
		
		if config.type == 4:
			dataList.append((rewardIndex, rewardUnbindRMB))
			if config.isBroadcast:
				ShenWangBaoKuDict['LuckyRoles'].append((role.GetRoleName(), rewardIndex, rewardUnbindRMB))
		else:
			dataList.append(rewardIndex)
			if config.isBroadcast:
				ShenWangBaoKuDict['LuckyRoles'].append((role.GetRoleName(), rewardIndex))
				
		ShenWangBaoKuDict.HasChange()		
		if len(dataList) > 20:
			role.GetObj(EnumObj.ShenWangBaoKu)[1] = dataList[-20:]
	
	role.Msg(2, 0, tips)
	
	roleData = role.GetObj(EnumObj.ShenWangBaoKu)
	data = [roleData.get(2, {}), roleData.get(1, [])]
	role.SendObj(SyncShenWangBaoKuPersonalData, data)
	for roleId in RoleOpenPanelSet:
		theRole = cRoleMgr.FindRoleByRoleID(roleId)
		if theRole:
			theRole.SendObj(SyncShenWangBaoKuServerData, (ShenWangBaoKuDict["Pool"], ShenWangBaoKuDict["LuckyRoles"][-20:]))


def RequestTenTime(role, msg):
	'''
	客户端请求十次抽奖
	'''
	if IsStart is False:
		return
	
	#角色身上的活动版本号与本次活动不一致
	if role.GetI32(EnumInt32.ShenWangBaoKuVersion) != ActVersion:
		return
	
	#奖池的活动版本号与本次活动不一致
	global ShenWangBaoKuDict
	if ShenWangBaoKuDict['ActVersion'] != ActVersion:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.ShenWangBaoKuNeedLevel:
		return
	
	costRMB = EnumGameConfig.ShenWangBaoKuTenTimePrice
	if Environment.EnvIsNA():
		costRMB = EnumGameConfig.ShenWangBaoKuTenTimePrice_NA
	if role.GetUnbindRMB() < costRMB:
		return
	
	config = ShenWangBaoKuConfig.RewardConfigDict.get(roleLevel)
	if config is None:
		return
	
	itemDict = {}
	talentCardDict = {}
	tarotDict = {}
	totalUnbindRMB = 0
	
	with TraShenWangBaoKuTenTime:
		#扣除神石
		role.DecUnbindRMB(costRMB)
		
		for _ in xrange(10):
			
			luckPool = ShenWangBaoKuDict['Pool']
			
			if luckPool >= 500:
				randomRate = config.randomRate1
			else:
				randomRate = config.randomRate2
			
			rewardIndex = randomRate.RandomOne()
			rewardConfig = ShenWangBaoKuConfig.RewardItemConfigDict.get(rewardIndex)
			if rewardConfig is None:
				print "GE_EXC,error while rewardConfig = ShenWangBaoKuConfig.RewardItemConfigDict.get(%s),roleID(%s)" % (rewardIndex, role.GetRoleID())
				continue
			
			role.IncI32(EnumInt32.ShenWangBaoKuPoint, EnumGameConfig.ShenWangBaoKuPointPerTime)
			if rewardConfig.type == 1:
				role.AddItem(*rewardConfig.thing)
				itemDict[rewardConfig.thing[0]] = itemDict.get(rewardConfig.thing[0], 0) + rewardConfig.thing[1]
			#命魂
			elif rewardConfig.type == 2:
				role.AddTarotCard(*rewardConfig.thing)
				tarotDict[rewardConfig.thing[0]] = tarotDict.get(rewardConfig.thing[0], 0) + rewardConfig.thing[1]
			#天赋卡	
			elif rewardConfig.type == 3:
				role.AddTalentCard(rewardConfig.thing)
				tarotDict[rewardConfig.thing] = tarotDict.get(rewardConfig.thing, 0) + rewardConfig.thing
			#奖池神石	
			elif rewardConfig.type == 4:
				pool = ShenWangBaoKuDict["Pool"]
				#记录当前奖池神石数
				AutoLog.LogBase(role.GetRoleID(), AutoLog.eveShenWangBaoKu, pool)
				rewardUnbindRMB = pool * rewardConfig.thing / 100
				ShenWangBaoKuDict["Pool"] = pool - rewardUnbindRMB
				role.IncUnbindRMB_S(rewardUnbindRMB)
				totalUnbindRMB += rewardUnbindRMB
			else:
				return
			
			ShenWangBaoKuDict["Pool"] = ShenWangBaoKuDict.get("Pool", 0) + EnumGameConfig.ShenWangBaoKuIncPoolPerTime
		
			dataList = role.GetObj(EnumObj.ShenWangBaoKu).setdefault(1, [])
		
			if rewardConfig.type == 4:
				dataList.append((rewardIndex, rewardUnbindRMB))
				if rewardConfig.isBroadcast:
					ShenWangBaoKuDict['LuckyRoles'].append((role.GetRoleName(), rewardIndex, rewardUnbindRMB))
			else:
				dataList.append(rewardIndex)
				if rewardConfig.isBroadcast:
					ShenWangBaoKuDict['LuckyRoles'].append((role.GetRoleName(), rewardIndex))
					
			if len(dataList) > 20:
				role.GetObj(EnumObj.ShenWangBaoKu)[1] = dataList[-20:]
	
	ShenWangBaoKuDict.HasChange()
	tips = GlobalPrompt.Reward_Tips
	for item in itemDict.iteritems():
		tips += GlobalPrompt.Item_Tips % item
	for tarot in tarotDict.iteritems():
		tips += GlobalPrompt.Tarot_Tips % tarot
	for talentCard in talentCardDict.iteritems():
		tips += GlobalPrompt.Talent_Tips % talentCard
	if totalUnbindRMB > 0:
		tips += GlobalPrompt.UnBindRMB_Tips % totalUnbindRMB
	
	role.Msg(2, 0, tips)
	roleData = role.GetObj(EnumObj.ShenWangBaoKu)
	data = [roleData.get(2, {}), roleData.get(1, [])]
	role.SendObj(SyncShenWangBaoKuPersonalData, data)
	#打包消息，发送玩家信息以及奖池神石数目
	for roleId in RoleOpenPanelSet:
		theRole = cRoleMgr.FindRoleByRoleID(roleId)
		if theRole:
			theRole.SendObj(SyncShenWangBaoKuServerData, (ShenWangBaoKuDict["Pool"], ShenWangBaoKuDict["LuckyRoles"][-20:]))


def RequestExchange(role, msg):
	'''
	 客户端请求积分兑换商店兑换
	'''
	if IsStart is False:
		return
	
	#角色身上的活动版本号与本次活动不一致
	if role.GetI32(EnumInt32.ShenWangBaoKuVersion) != ActVersion:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.ShenWangBaoKuNeedLevel:
		return
	
	coding, cnt = msg
	
	if not cnt > 0:
		return
	
	config = ShenWangBaoKuConfig.PointStoreConfigDict.get(coding)
	if config is None:
		return
	
	if roleLevel < config.needLevel:
		return
	
	if WorldData.GetWorldLevel() < config.needWorldLevel:
		return
	
	gotDict = role.GetObj(EnumObj.ShenWangBaoKu).setdefault(2, {})
	
	if config.limitCnt > 0:
		if gotDict.get(coding, 0) + cnt > config.limitCnt:
			return
		
	needPoint = config.needPoint * cnt
	
	if role.GetI32(EnumInt32.ShenWangBaoKuPoint) < needPoint:
		return
	
	with TraShenWangBaoExchange:
		role.DecI32(EnumInt32.ShenWangBaoKuPoint, needPoint)
		role.AddItem(config.itemCoding, cnt)
		#玩家购买该物品的数量增加
		gotDict[config.itemCoding] = gotDict.get(config.itemCoding, 0) + cnt
	
	roleData = role.GetObj(EnumObj.ShenWangBaoKu)
	data = [roleData.get(2, {}), roleData.get(1, [])]
	role.SendObj(SyncShenWangBaoKuPersonalData, data)
	role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (config.itemCoding, cnt))
	

def RequestOpenPanel(role, msg):
	'''
	客户端请求打开面板
	'''
	if IsStart is False:
		return
	roleID = role.GetRoleID()
	global RoleOpenPanelSet
	if roleID not in RoleOpenPanelSet:
		RoleOpenPanelSet.add(roleID)
	
	roleData = role.GetObj(EnumObj.ShenWangBaoKu)
	data = [roleData.get(2, {}), roleData.get(1, [])]
	role.SendObj(SyncShenWangBaoKuPersonalData, data)
	role.SendObj(SyncShenWangBaoKuServerData, (ShenWangBaoKuDict["Pool"], ShenWangBaoKuDict["LuckyRoles"][-20:]))
	

def RequestClosePanel(role, msg):
	'''
	请求关闭面板
	'''
	RoleClosePanel(role)


def OnClientLostorExit(role, param):
	'''
	客户端掉线或退出的处理 
	@param role:
	@param param:
	'''	
	RoleClosePanel(role)


def RoleClosePanel(role):
	'''
	关闭面板处理，将玩家id从Role_Open_Panel_List移除
	@param role:
	'''
	roleId = role.GetRoleID()
	global RoleOpenPanelSet
	if roleId in RoleOpenPanelSet:
		RoleOpenPanelSet.discard(roleId)


def SyncRoleOtherData(role, param):
	if IsStart is False:
		return
	role.SendObj(SyncShenWangBaoKuStatu, (IsStart, EndTime))


def AfterRoleLogin(role, param):
	'''
	角色登录处理
	'''
	if IsStart is False:
		return
	if role.GetI32(EnumInt32.ShenWangBaoKuVersion) == ActVersion:
		return
	
	with TraShenWangBaoVersion:
		role.SetI32(EnumInt32.ShenWangBaoKuPoint, 0)
		role.SetI32(EnumInt32.ShenWangBaoKuVersion, ActVersion)


def AfterLoad():
	#数据载入后初始化
	global ShenWangBaoKuDict
	if IsStart is False:
		return
	
	if ActVersion == 0:
		return
	
	#如果版本号相同的话不用做任何处理
	if ShenWangBaoKuDict.get('ActVersion') == ActVersion:
		return
	InitShenWangBaoKuDict()


def InitShenWangBaoKuDict():
	ShenWangBaoKuDict['ActVersion'] = ActVersion
	ShenWangBaoKuDict['Pool'] = EnumGameConfig.ShenWangBaoKuLuckPoolInit
	ShenWangBaoKuDict['LuckyRoles'] = []


def BeforeSave():
	global ShenWangBaoKuDict
	if len(ShenWangBaoKuDict.get('LuckyRoles', [])) > EnumGameConfig.ShenWangBaoKuLuckrolelist_lenth:
		ShenWangBaoKuDict['LuckyRoles'] = ShenWangBaoKuDict.get('LuckyRoles', [])[-20:]
		

if "_HasLoad" not in dir():
	if (Environment.HasLogic or Environment.HasWeb) and not Environment.IsCross:
		ShenWangBaoKuDict = Contain.Dict("ShenWangBaoKuDict", (2038, 1, 1), AfterLoad, BeforeSave, isSaveBig=False)
	
	if Environment.HasLogic and not Environment.IsCross:
		LoadShenWangBaoKuTimeConfig()
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestShenWangBaoKuOneTime", "客户端请求神王宝库一次抽奖"), RequestOneTime)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestShenWangBaoKuTenTime", "客户端请求神王宝库十次抽奖"), RequestTenTime)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestShenWangBaoKuExchange", "客户端请求神王宝库积分兑换商店兑换商品"), RequestExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestShenWangBaoKuOpenPanel", "客户端请求神王宝库积打开面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestShenWangBaoKuClosePanel", "客户端请求神王宝库关闭面板"), RequestClosePanel)
		
		Event.RegEvent(Event.Eve_AfterLogin, AfterRoleLogin)
		Event.RegEvent(Event.Eve_ClientLost, OnClientLostorExit)
		Event.RegEvent(Event.Eve_BeforeExit, OnClientLostorExit)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)

