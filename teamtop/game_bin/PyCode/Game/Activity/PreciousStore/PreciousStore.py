#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PreciousStore.PreciousStore")
#===============================================================================
# 珍宝商店
#===============================================================================
import cRoleMgr
import cDateTime
import cNetMessage
import DynamicPath
import Environment
from Util import Time
import cComplexServer
from Game.Role import Event
from Util.File import TabFile
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Role.Data import EnumInt32, EnumObj
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Activity.PreciousStore import PreciousStoreConfig
from Game.SysData import WorldData

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("PreciousStore")
	
	IsStart = False
	ActVersion = 0
	EndSeconds = 0

	#消息
	SyncPreciousStoreStatu = AutoMessage.AllotMessage("SyncPreciousStoreStatu", "同步珍宝商店开启情况")
	SyncPreciousStorePersonalData = AutoMessage.AllotMessage("SyncPreciousStorePersonalData", "同步珍宝商店个人数据")
	#日志
	TraPreciousStoreExchange = AutoLog.AutoTransaction("TraPreciousStoreExchange", "珍宝商店交易")
	TraPreciousStoreVersion = AutoLog.AutoTransaction("TraPreciousStoreVersion", "珍宝商店版本更替")
	

class PreciousStoreTimeConfig(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("ShiJianKongZhi.txt")
	def __init__(self):
		self.actVersion = int									#活动版本号
		self.beginTime = self.GetDatetimeByString				#开始时间
		self.endTime = self.GetDatetimeByString					#结束时间
		self.kaifuDay = int
	
	def Active(self):
		#开始时间戳
		beginSeconds = Time.DateTime2UnitTime(self.beginTime)
		#结束时间戳
		endSeconds = Time.DateTime2UnitTime(self.endTime)
		
		if endSeconds <= beginSeconds:
			print "GE_EXC, endSeconds <= beginSeconds in PreciousStore"
			return
		
		#当前时间戳
		nowSeconds = cDateTime.Seconds()
		if beginSeconds <= nowSeconds < endSeconds and WorldData.GetWorldKaiFuDay() >= self.kaifuDay:
			#当前开服时间  < 距离活动开启的天数 + 要求开服天数，返回
			if (cDateTime.Now() - self.beginTime).days + self.kaifuDay > WorldData.GetWorldKaiFuDay():
				return
			#在开始和结束时间戳之间, 激活
			Start(None, (endSeconds, self.actVersion))
			cComplexServer.RegTick(endSeconds - nowSeconds , End)
			
		elif nowSeconds < beginSeconds:
			if (self.beginTime - cDateTime.Now()).days + 1 + WorldData.GetWorldKaiFuDay() < self.kaifuDay:
				return
			#在开始时间戳之前
			cComplexServer.RegTick(beginSeconds - nowSeconds, Start, (endSeconds, self.actVersion))
			cComplexServer.RegTick(endSeconds - nowSeconds , End)


def Start(callargv, param):
	
	if not IsOldServer():
		return
	
	global IsStart, EndSeconds, ActVersion
	if IsStart is True:
		print "GE_EXC,PreciousStore has been started"
		return
	
	#下两行不能调换顺序，因为要确保IsStart为真的时候，活动版本号已经初始化了
	EndSeconds, ActVersion = param
	IsStart = True
	
	for theRole in cRoleMgr.GetAllRole():
		TryRoleVersionUpdate(theRole)
			
	#同步客户端活动开启
	cNetMessage.PackPyMsg(SyncPreciousStoreStatu, (IsStart, EndSeconds))
	cRoleMgr.BroadMsg()


def End(callargv, param):
	global IsStart, EndSeconds, ActVersion
	if IsStart is False:
		print "GE_EXC,PreciousStore has been ended"
		return
	IsStart = False
	EndSeconds = 0
	ActVersion = 0
	#同步客户端活动开启
	cNetMessage.PackPyMsg(SyncPreciousStoreStatu, (IsStart, EndSeconds))
	cRoleMgr.BroadMsg()


def LoadPreciousStoreTimeConfig():
	global PreciousStoreObj
	for cfg in PreciousStoreTimeConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in PreciousStoreTimeConfig"
			return
		cfg.Active()


def RequestExchange(role, msg):
	'''
	 客户端请求积分兑换商店兑换
	'''
	if IsStart is False:
		return
	
	#角色身上的活动版本号与本次活动不一致
	if role.GetI32(EnumInt32.PreciousStoreVersion) != ActVersion:
		return
	
	index, cnt = msg
	
	if not cnt > 0:
		return
	
	config = PreciousStoreConfig.PreciousStoreConfigDict.get(index)
	if config is None:
		print "GE_EXC, role(%s) request buy index(%s) which not in config in PreciousStoreConfigDict" % (role.GetRoleID(), index)
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < config.needLevel:
		return
	
	buyDataDict = role.GetObj(EnumObj.PreciousStoreBuyData)
	dailyBuyDict = buyDataDict.setdefault(1, {})
	totalBuyDict = buyDataDict.setdefault(2, {})
	
	#每日限购
	if config.Limittype == 1:
		if dailyBuyDict.get(index, 0) + cnt > config.LimitNum:
			return
	#活动期间限购
	elif config.Limittype == 2:
		if totalBuyDict.get(index, 0) + cnt > config.LimitNum:
			return
	
	#判断代币是否足够
	needCurrencyCnt = config.currencyCnt * cnt
	if role.ItemCnt(config.currencyCoding) < needCurrencyCnt:
		return
	
	itemCoding, itemCnt = config.item
	totalItemCnt = itemCnt * cnt
	
	with TraPreciousStoreExchange:
		if role.DelItem(config.currencyCoding, needCurrencyCnt) < needCurrencyCnt:
			return
		
		role.AddItem(itemCoding, totalItemCnt)
		
		#记录每日购买次数及活动期间总的购买次数
		if config.Limittype == 1:
			dailyBuyDict[index] = dailyBuyDict.get(index, 0) + cnt
		elif config.Limittype == 2:
			totalBuyDict[index] = totalBuyDict.get(index, 0) + cnt
	
	role.SendObj(SyncPreciousStorePersonalData, (dailyBuyDict, totalBuyDict))
	
	role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (itemCoding, totalItemCnt))


def RequestOpenPanel(role, msg):
	'''
	客户端请求打开面板
	'''
	buyDataDict = role.GetObj(EnumObj.PreciousStoreBuyData)
	dailyBuyDict = buyDataDict.get(1, {})
	totalBuyDict = buyDataDict.get(2, {})
	role.SendObj(SyncPreciousStorePersonalData, (dailyBuyDict, totalBuyDict))
	

def OnSyncRoleOtherData(role, param):
	if IsStart is False:
		return
	role.SendObj(SyncPreciousStoreStatu, (IsStart, EndSeconds))


def AfterRoleLogin(role, param):
	'''
	角色登录处理
	'''
	if IsStart is False:
		return
	TryRoleVersionUpdate(role)


def TryRoleVersionUpdate(role):
	#活动没有开启
	if IsStart is False:
		return
	
	#角色身上版本号和当前版本号相同
	if role.GetI32(EnumInt32.PreciousStoreVersion) == ActVersion:
		return
	
	#角色身上版本号大于当前版本号
	if role.GetI32(EnumInt32.PreciousStoreVersion) > ActVersion:
		print "role(%s) version(%s) > PreciousStoreVersion(%s)" % (role.GetRoleID(), role.GetI32(EnumInt32.PreciousStoreVersion), ActVersion)
		return
	
	with TraPreciousStoreVersion:
		roleBuyData = role.GetObj(EnumObj.PreciousStoreBuyData)
		roleBuyData[1] = {}
		roleBuyData[2] = {}
		role.SetI32(EnumInt32.PreciousStoreVersion, ActVersion)


def OnRoleDailyClear(role, params):
	if IsStart is False:
		return
	roleBuyData = role.GetObj(EnumObj.PreciousStoreBuyData)
	roleBuyData[1] = {}


def IsOldServer():
	'''
	天降横财新服老服区分
	'''
	if WorldData.GetWorldKaiFuDay() > EnumGameConfig.PreciousStore_NeedKaiFuDay:
		return True
	else:
		return False


def AfterLoadWorldData(callArgvs = None, regParams = None):
	'''
	世界数据载回之后
	'''
	LoadPreciousStoreTimeConfig()
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsNA() or Environment.EnvIsTK() or Environment.EnvIsPL()):
#		LoadPreciousStoreTimeConfig()
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPreciousStoreExchange", "客户端请求珍宝商店交易"), RequestExchange)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestPreciousStoreOpenPanel", "客户端请求珍宝商店打开面板"), RequestOpenPanel)
		
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDailyClear)
		Event.RegEvent(Event.Eve_AfterLogin, AfterRoleLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
