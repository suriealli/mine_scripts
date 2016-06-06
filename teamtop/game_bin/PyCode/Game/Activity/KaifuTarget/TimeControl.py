#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KaifuTarget.TimeControl")
#===============================================================================
# 7日目标时间控制,在这里发放奖励,公告啊啥啥啥的
#===============================================================================
import time
import datetime
import cDateTime
import DynamicPath
import Environment
import cRoleMgr
import cNetMessage
import cComplexServer
from Util.File import TabFile
from Common.Message import AutoMessage
from Common.Other import EnumSysData, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.SysData import WorldData
from Game.Persistence import Contain
from Game.Role.Mail import Mail
from Game.Activity.KaifuTarget import KaifuTargetAccount, KaifuTargetConfig,\
	TargetDefine, KaifuTargetRequest, KaifuRankFun


if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("KaifuTarget")
	IsAct = False
	
	#七日目标激活时间配置
	KaifuTargetActiveConfig_Dict = {}
	#新七日目标激活时间配置
	NewKaifuTargetActiveConfig_Dict = {}
	#七日目标开启缓存(这里是所有活动的结束时间)
	KaifuTargetActiveCache_Dict = {}
	
	#记录一个tickid，用于重设开服时间之后的处理
	TryActiveId = 0
	
	#写死一个时间, 这个时间之前的所有服都不开七日目标
	#繁体的时间
	if Environment.EnvIsFT():
		KaifuTargetTime = datetime.datetime(2014, 12, 9, 19, 0, 0)
	#北美
	elif Environment.EnvIsNA():
		KaifuTargetTime = datetime.datetime(2015, 1, 15, 20, 0, 0)
	#其他的时间
	else:
		KaifuTargetTime = datetime.datetime(2014, 12, 4, 20, 0, 0)
	
	if Environment.EnvIsPL():
		KaifuTargetTime_New = datetime.datetime(2015, 12, 9, 23, 59, 59)
	else:
		KaifuTargetTime_New = datetime.datetime(2015, 10, 22, 23, 59, 59)
	
	KaifuTargetActive_AllData = AutoMessage.AllotMessage("KaifuTargetActive_AllData", "同步七日目标所有数据")
	KaifuTargetActive_AllStop = AutoMessage.AllotMessage("KaifuTargetActive_AllStop", "通知客户端七日目标活动结束")

def IsOldServer():
	global KaifuTargetTime, KaifuTargetTime_New
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	
	#这个时间点之前开的服都不开七日目标活动
	if Environment.EnvIsQQ() or Environment.IsDevelop or Environment.EnvIsPL():
		#国服、波兰不开
		return kaifuTime > KaifuTargetTime_New or KaifuTargetTime > kaifuTime
	
	return KaifuTargetTime > kaifuTime

class KaifuTargetActConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("KaifuTargetAct.txt")
	startTickId = 0
	endTickId = 0
	lastTickId = 0
	def __init__(self):
		self.targetType = int				#活动类型
		self.isLastTarget = int				#是否最后一个活动
		self.beginDay = int					#活动开启
		self.continueDay = int				#持续天数
		self.targetRankName = str			#活动名字
		
	def Active(self):
		#当前时间
		nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
		
		#开服时间
		worldData = WorldData.WD[EnumSysData.KaiFuKey]
		kaifuDate = (worldData.year, worldData.month, worldData.day, worldData.hour, worldData.minute, worldData.second)
		
		#时间错了
		if kaifuDate > nowDate:
			print 'GE_EXC, KaifuTargetActConfig Active date error'
			#cComplexServer.RegTick(uSec, fun_BorrowRef, regparam_BorrowRef)
			return
		
		#计算开始时间
		beginTime = int(time.mktime((datetime.datetime(worldData.year, worldData.month, worldData.day, worldData.hour, worldData.minute, worldData.second) + datetime.timedelta(self.beginDay)).timetuple()))
		#结束时间
		self.endTime = int(time.mktime((datetime.datetime(worldData.year, worldData.month, worldData.day, worldData.hour, worldData.minute, worldData.second) + datetime.timedelta(self.beginDay + self.continueDay)).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(*nowDate).timetuple()))
		
		#缓存住活动结束时间
		global KaifuTargetActiveCache_Dict
		KaifuTargetActiveCache_Dict[self.targetType] = self.endTime
		
		if beginTime <= nowTime < self.endTime:
			#在开始和结束时间戳之间, 激活
			Event.TriggerEvent(Event.Eve_StartKaifuTarget, None, self.targetType)
			
			self.startTickId = 0
			self.endTickId = cComplexServer.RegTick(self.endTime - nowTime, EndKaifuTarget, self.targetType)
			
			if self.isLastTarget:
				#晚最后一个活动10s结算(给最后一个活动一点时间去结算排行榜)
				self.lastTickId = cComplexServer.RegTick(self.endTime - nowTime + 10, EndLastTarget, self.targetType)
		elif nowTime < beginTime:
			#在开始时间戳之前
			self.startTickId = cComplexServer.RegTick(beginTime - nowTime, StartKaifuTarget, self.targetType)
			self.endTickId = cComplexServer.RegTick(self.endTime - nowTime, EndKaifuTarget, self.targetType)
			
			if self.isLastTarget:
				self.lastTickId = cComplexServer.RegTick(self.endTime - nowTime + 10, EndLastTarget, self.targetType)
		else:
			#活动不会开, 尝试结算排行榜
			global KaifuTarget_Dict
			if self.targetType in KaifuTarget_Dict['accountSet']:
				return
			accountFun = KaifuTargetAccount.AccountFunDict.get(self.targetType)
			if not accountFun:
				#没有找到排行榜结算函数, 算结算过了
				KaifuTarget_Dict['accountSet'].add(self.targetType)
				KaifuTarget_Dict.changeFlag = True
				return
			rankData, _ = accountFun()
			if not rankData:
				print 'GE_EXC, KaifuTargetActConfig Active account rank error %s' % self.targetType
				
			from Game.Activity.KaifuTarget import KaifuTargetFun
			with KaifuTargetFun.KaifuTargetAccountRankData:
				KaifuTarget_Dict['accountSet'].add(self.targetType)
				KaifuTarget_Dict[self.targetType] = rankData
				KaifuTarget_Dict.changeFlag = True
				
				AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveKaifuTargetRank, (self.targetType, rankData))
			
	def ForceTrigger(self):
		if self.startTickId:
			#正在准备的活动取消掉开启和关闭的tick
			cComplexServer.UnregTick(self.startTickId)
			cComplexServer.UnregTick(self.endTickId)
			cComplexServer.UnregTick(self.lastTickId)
		elif self.endTickId:
			#修正活动开启标志, 不触发活动结束
			from Game.Activity.KaifuTarget import KaifuTargetFun
			KaifuTargetFun.StartFlag[self.targetType] = False
			#取消结束tick
			cComplexServer.UnregTick(self.endTickId)
			if self.lastTickId:
				#取消最后一个活动结束tick
				cComplexServer.UnregTick(self.lastTickId)
		#清理掉开始和结束的tickID
		self.startTickId = 0
		self.endTickId = 0
		self.lastTickId = 0
		
def LoadKaifuTargetAct():
	global KaifuTargetActiveConfig_Dict
	
	for KTA in KaifuTargetActConfig.ToClassType():
		if KTA.targetType in KaifuTargetActiveConfig_Dict:
			print 'GE_EXC, repeat targetType %s in KaifuTargetActiveConfig_Dict' % KTA.targetType
			continue
		KaifuTargetActiveConfig_Dict[KTA.targetType] = KTA
	
class NewKaifuTargetActConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("NewKaifuTargetAct.txt")
	startTickId = 0
	endTickId = 0
	lastTickId = 0
	def __init__(self):
		self.targetType = int				#活动类型
		self.isLastTarget = int				#是否最后一个活动
		self.beginDay = int					#活动开启
		self.continueDay = int				#持续天数
		self.targetRankName = str			#活动名字
		
	def Active(self):
		#当前时间
		nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
		
		#开服时间
		worldData = WorldData.WD[EnumSysData.KaiFuKey]
		kaifuDate = (worldData.year, worldData.month, worldData.day, worldData.hour, worldData.minute, worldData.second)
		
		#时间错了
		if kaifuDate > nowDate:
			print 'GE_EXC, KaifuTargetActConfig Active date error'
			#cComplexServer.RegTick(uSec, fun_BorrowRef, regparam_BorrowRef)
			return
		
		#计算开始时间
		beginTime = int(time.mktime((datetime.datetime(worldData.year, worldData.month, worldData.day, worldData.hour, worldData.minute, worldData.second) + datetime.timedelta(self.beginDay)).timetuple()))
		#结束时间
		self.endTime = int(time.mktime((datetime.datetime(worldData.year, worldData.month, worldData.day, worldData.hour, worldData.minute, worldData.second) + datetime.timedelta(self.beginDay + self.continueDay)).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(*nowDate).timetuple()))
		
		#缓存住活动结束时间
		global KaifuTargetActiveCache_Dict
		KaifuTargetActiveCache_Dict[self.targetType] = self.endTime
		
		if beginTime <= nowTime < self.endTime:
			#在开始和结束时间戳之间, 激活
			Event.TriggerEvent(Event.Eve_StartKaifuTarget, None, self.targetType)
			
			self.startTickId = 0
			self.endTickId = cComplexServer.RegTick(self.endTime - nowTime, EndKaifuTarget, self.targetType)
			
			if self.isLastTarget:
				#晚最后一个活动10s结算(给最后一个活动一点时间去结算排行榜)
				self.lastTickId = cComplexServer.RegTick(self.endTime - nowTime + 10, EndLastTarget, self.targetType)
		elif nowTime < beginTime:
			#在开始时间戳之前
			self.startTickId = cComplexServer.RegTick(beginTime - nowTime, StartKaifuTarget, self.targetType)
			self.endTickId = cComplexServer.RegTick(self.endTime - nowTime, EndKaifuTarget, self.targetType)
			
			if self.isLastTarget:
				self.lastTickId = cComplexServer.RegTick(self.endTime - nowTime + 10, EndLastTarget, self.targetType)
		else:
			#活动不会开, 尝试结算排行榜
			global KaifuTarget_Dict
			if self.targetType in KaifuTarget_Dict['accountSet']:
				return
			accountFun = KaifuTargetAccount.AccountFunDict.get(self.targetType)
			if not accountFun:
				#没有找到排行榜结算函数, 算结算过了
				KaifuTarget_Dict['accountSet'].add(self.targetType)
				KaifuTarget_Dict.changeFlag = True
				return
			rankData, _ = accountFun()
			if not rankData:
				print 'GE_EXC, KaifuTargetActConfig Active account rank error %s' % self.targetType
				
			from Game.Activity.KaifuTarget import KaifuTargetFun
			with KaifuTargetFun.KaifuTargetAccountRankData:
				KaifuTarget_Dict['accountSet'].add(self.targetType)
				KaifuTarget_Dict[self.targetType] = rankData
				KaifuTarget_Dict.changeFlag = True
				
				AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveKaifuTargetRank, (self.targetType, rankData))
			
	def ForceTrigger(self):
		if self.startTickId:
			#正在准备的活动取消掉开启和关闭的tick
			cComplexServer.UnregTick(self.startTickId)
			cComplexServer.UnregTick(self.endTickId)
			cComplexServer.UnregTick(self.lastTickId)
		elif self.endTickId:
			#修正活动开启标志, 不触发活动结束
			from Game.Activity.KaifuTarget import KaifuTargetFun
			KaifuTargetFun.StartFlag[self.targetType] = False
			#取消结束tick
			cComplexServer.UnregTick(self.endTickId)
			if self.lastTickId:
				#取消最后一个活动结束tick
				cComplexServer.UnregTick(self.lastTickId)
		#清理掉开始和结束的tickID
		self.startTickId = 0
		self.endTickId = 0
		self.lastTickId = 0
		
def LoadNewKaifuTargetAct():
	global NewKaifuTargetActiveConfig_Dict
	
	for KTA in NewKaifuTargetActConfig.ToClassType():
		if KTA.targetType in NewKaifuTargetActiveConfig_Dict:
			print 'GE_EXC, repeat targetType %s in NewKaifuTargetActiveConfig_Dict' % KTA.targetType
			continue
		NewKaifuTargetActiveConfig_Dict[KTA.targetType] = KTA
	
def AfterLoadWorldData(param1, param2):
	#世界数据载回后尝试触发活动
	#如果持久化字典没有载回的等持久化字典载回后再尝试触发
	global KaifuTarget_Dict
	if not KaifuTarget_Dict.returnDB: return
	
	TryActive()
	
def AfterLoad():
	#持久化字典载回后尝试触发
	#初始化持久化字典
	global KaifuTarget_Dict
	if not KaifuTarget_Dict:
		KaifuTarget_Dict['accountSet'] = set()
	
	#世界数据没有载回的话等世界数据载回后再尝试触发
	if not WorldData.WD.returnDB:
		return
	
	TryActive()

def TryActive():
	if IsOldServer():
		return
	
	#开服时间区分开启的活动
	
	#默认旧版
	accountCnt = 7
	accountList = [1,2,3,4,5,6,7]
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		accountCnt = 6
		accountList = [1,2,3,4,5,6]
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		accountCnt = 7
		accountList = [1,2,3,4,5,6,7]
	
	if (len(KaifuTarget_Dict['accountSet']) < accountCnt) and ((cDateTime.Now() - WorldData.WD[1]).days >= 7):
		#如果结算过的活动的个数少于7个, 而这个时候开服时间已经过去7天了, 尝试去结算还没有结算过的活动
		for i in accountList:
			if i in KaifuTarget_Dict['accountSet']:
				continue
			accoutFun = KaifuTargetAccount.AccountFunDict.get(i)
			if not accoutFun:
				#没有找到排行榜结算函数, 算结算过了
				KaifuTarget_Dict['accountSet'].add(i)
				KaifuTarget_Dict.changeFlag = True
				continue
			rankData, _ = accoutFun()
			if not rankData:
				print 'GE_EXC, AfterLoad account empty rank by %s day' % i
			
			from Game.Activity.KaifuTarget import KaifuTargetFun
			with KaifuTargetFun.KaifuTargetAccountRankData:
				KaifuTarget_Dict['accountSet'].add(i)
				KaifuTarget_Dict[i] = rankData
				
				AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveKaifuTargetRank, (i, rankData))
			
		KaifuTarget_Dict.changeFlag = True
		#结算失败 ?
		if len(KaifuTarget_Dict['accountSet']) != accountCnt:
			print 'GE_EXC, AfterLoad account error'
			return
		#结算完排行榜后结束七日活动(对排行榜内所有未领取奖励的玩家发放邮件奖励)
		EndLastTarget(None, i)
		return
	
	#已经结算过了
	if len(KaifuTarget_Dict['accountSet']) == accountCnt:
		return
	ActiveAll()

def ActiveAll(callArgv = None, regparam = None):
	nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
	#开服时间
	worldData = WorldData.WD[EnumSysData.KaiFuKey]
	kaifuDate = (worldData.year, worldData.month, worldData.day, worldData.hour, worldData.minute, worldData.second)
	#时间错了
	if kaifuDate > nowDate:
		#print 'GE_EXC, ActiveAll Active date error'
		kaifuSecs = int(time.mktime(datetime.datetime(*kaifuDate).timetuple()))
		nowSec = cDateTime.Seconds()
		global TryActiveId
		TryActiveId = cComplexServer.RegTick(kaifuSecs - nowSec + 5, AfterSetKaiFuTime, None)
		return
	global KaifuTargetActiveConfig_Dict
	ActiveConfig_Dict = KaifuTargetActiveConfig_Dict
		
	if worldData > TargetDefine.KaifuTime_New:
		global NewKaifuTargetActiveConfig_Dict
		ActiveConfig_Dict =NewKaifuTargetActiveConfig_Dict
	if worldData > TargetDefine.KaifuTime_Old:
		ActiveConfig_Dict = KaifuTargetActiveConfig_Dict
	
	for cfg in ActiveConfig_Dict.itervalues():
		cfg.Active()

def AfterSetKaiFuTime(param1, param2):
	#设置开服时间后重新载入排行榜结算函数
	KaifuTargetAccount.LinkAccountFun(None, None)
	
	KaifuRankFun.LoadLogDict()
	
	KaifuTargetRequest.AfterLoadWorldData(None, None)
	
	global TryActiveId
	if TryActiveId > 0:
		cComplexServer.UnregTick(TryActiveId)
		TryActiveId = 0
		
	#设置开服时间后先强行关闭所有活动再尝试触发活动
	global KaifuTargetActiveCache_Dict, KaifuTarget_Dict
	kaifuTime = WorldData.WD[EnumSysData.KaiFuKey]
	
	#新的活动和旧的活动都要尝试取消一遍
	ActiveConfig_Dict = KaifuTargetActiveConfig_Dict
	New_ActiveConfig_Dict = NewKaifuTargetActiveConfig_Dict
	
	#先把缓存的活动结束时间清理掉
	KaifuTargetActiveCache_Dict = {}
	
	#设置开服时间后先删除持久化字典, 之后会根据时间结算排行榜
	KaifuTarget_Dict.clear()
	KaifuTarget_Dict['accountSet'] = set()
	KaifuTarget_Dict.HasChange()
	
	#这个时间点之后开的服都不开七日目标活动
	if IsOldServer():
		for cfg in ActiveConfig_Dict.itervalues():
			cfg.ForceTrigger()
		for ncfg in New_ActiveConfig_Dict.itervalues():
			ncfg.ForceTrigger()
		return
	
	#超过7天的服不开
	if (datetime.datetime.now() - kaifuTime).days >= 7:
		for cfg in ActiveConfig_Dict.itervalues():
			cfg.ForceTrigger()
		for ncfg in New_ActiveConfig_Dict.itervalues():
			ncfg.ForceTrigger()
		return
	
	#设置开服时间后先处理之前的tick
	for cfg in ActiveConfig_Dict.itervalues():
		cfg.ForceTrigger()
	for ncfg in New_ActiveConfig_Dict.itervalues():
		ncfg.ForceTrigger()
	
	#再触发活动, 到这里的时候会用新的配置
	ActiveAll()
	#同步客户端最新的活动结束时间
	cNetMessage.PackPyMsg(KaifuTargetActive_AllData, KaifuTargetActiveCache_Dict)
	cRoleMgr.BroadMsg()
	
def StartKaifuTarget(argv, param):
	#活动开启
	targetType = param
	
	global KaifuTargetActiveConfig_Dict
	ActiveConfig_Dict = KaifuTargetActiveConfig_Dict
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		global NewKaifuTargetActiveConfig_Dict
		ActiveConfig_Dict =NewKaifuTargetActiveConfig_Dict
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		ActiveConfig_Dict = KaifuTargetActiveConfig_Dict
	
	if targetType not in ActiveConfig_Dict:
		print 'GE_EXC, StartKaifuTarget targetType %s error' % targetType
		return
	#取消活动开启tick
	ActiveConfig_Dict[targetType].startTickId = 0
	
	#触发活动开启
	Event.TriggerEvent(Event.Eve_StartKaifuTarget, None, param)
	
def EndKaifuTarget(argv, param):
	#活动关闭
	targetType = param
	
	global KaifuTargetActiveConfig_Dict
	ActiveConfig_Dict = KaifuTargetActiveConfig_Dict
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		global NewKaifuTargetActiveConfig_Dict
		ActiveConfig_Dict =NewKaifuTargetActiveConfig_Dict
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		ActiveConfig_Dict = KaifuTargetActiveConfig_Dict
	
	if targetType not in ActiveConfig_Dict:
		print 'GE_EXC, EndKaifuTarget targetType %s error' % targetType
		return
	#取消活动结束tick
	ActiveConfig_Dict[targetType].endTickId = 0
	
	#触发活动结束
	Event.TriggerEvent(Event.Eve_EndKaifuTarget, None, targetType)
	
def EndLastTarget(argv, param):
	targetType = param
	
	isNew = False
	accountCnt = 7
	accountList = [1,2,3,4,5,6,7]
	KaifuTargetRank_Dict = KaifuTargetConfig.KaifuTargetRank_Dict
	
	if WorldData.WD[1] > TargetDefine.KaifuTime_New:
		accountCnt = 6
		accountList = [1,2,3,4,5,6]
		KaifuTargetRank_Dict = KaifuTargetConfig.NewKaifuTargetRank_Dict
		isNew = True
	if WorldData.WD[1] > TargetDefine.KaifuTime_Old:
		accountCnt = 7
		accountList = [1,2,3,4,5,6,7]
		KaifuTargetRank_Dict = KaifuTargetConfig.KaifuTargetRank_Dict
		isNew = False
	
	#最后一个活动关闭, 给所有未领取排行榜奖励的玩家有奖奖励
	global KaifuTarget_Dict
	if not KaifuTarget_Dict:
		print 'GE_EXC, EndLastTarget KaifuTarget_Dict error'
		return
	
	#这里不做开服时间的判断了
	
	if len(KaifuTarget_Dict['accountSet']) < accountCnt:
		#还有活动没有结算过
		from Game.Activity.KaifuTarget import KaifuTargetFun
		for i in accountList:
			if i in KaifuTarget_Dict['accountSet']:
				continue
			accountFun = KaifuTargetAccount.AccountFunDict.get(i)
			if not accountFun:
				#没有找到排行榜结算函数, 算结算过了
				KaifuTarget_Dict['accountSet'].add(i)
				KaifuTarget_Dict.changeFlag = True
				continue
			rankData, _ = accountFun()
			if not rankData:
				print 'GE_EXC, EndLastTarget account empty rank by %s day' % i
				
			with KaifuTargetFun.KaifuTargetAccountRankData:
				KaifuTarget_Dict['accountSet'].add(i)
				KaifuTarget_Dict[i] = rankData
				AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveKaifuTargetRank, (i, rankData))
			
		KaifuTarget_Dict.changeFlag = True
		if len(KaifuTarget_Dict['accountSet']) != accountCnt:
			print 'GE_EXC, EndLastTarget accout error, accoutCnt %s, real %s'  % (accountCnt, len(KaifuTargetRank_Dict['accountSet']))
			return
	
	#奖励发放完后删除所有的结算数据, 但保留结算记录
	delType = []
	for targetType, rankData in KaifuTarget_Dict.items():
		if targetType == 'accountSet':
			continue
		for roleId, rankData in rankData.iteritems():
			for _, data in rankData.iteritems():
				if data[1]:
					#奖励已领取
					continue
				cfg = KaifuTargetRank_Dict.get((targetType, data[0]))
				if not cfg:
					print 'GE_EXC, EndLastTarget can not find type %s rank %s cfg' % (targetType, data[0])
					continue
				tarot_list = None
				if cfg.tarot:
					tarot_list = [i[0] for i in cfg.tarot]
				from Game.Activity.KaifuTarget import KaifuRankFun
				log = KaifuRankFun.Tra_KaifuTarget_RankLogDict.get(targetType)
				if log:
					with log:
						if isNew:
							if targetType == 1:
								Mail.SendMail(roleId, GlobalPrompt.KaifuTarget_MTitle, GlobalPrompt.KaifuTarget_MSender, GlobalPrompt.KaifuTarget_MContent_2 % data[0], items=cfg.item, tarotList=tarot_list, bindrmb=cfg.bindRMB, money=cfg.money)
							elif targetType == 4:
								Mail.SendMail(roleId, GlobalPrompt.KaifuTarget_MTitle, GlobalPrompt.KaifuTarget_MSender, GlobalPrompt.KaifuTarget_MContent_3 % data[0], items=cfg.item, tarotList=tarot_list, bindrmb=cfg.bindRMB, money=cfg.money)
						else:
							Mail.SendMail(roleId, GlobalPrompt.KaifuTarget_MTitle, GlobalPrompt.KaifuTarget_MSender, GlobalPrompt.KaifuTarget_MContent % (targetType, data[0]), items=cfg.item, tarotList=tarot_list, bindrmb=cfg.bindRMB, money=cfg.money)
						
				else:
					print 'GE_EXC, EndLastTarget can not find log %s' % targetType
					return
			
		delType.append(targetType)
	
	#清理排行榜数据
	for targetType in delType:
		del KaifuTarget_Dict[targetType]
	
	KaifuTarget_Dict.changeFlag = True
	
	
	cNetMessage.PackPyMsg(KaifuTargetActive_AllStop, None)
	cRoleMgr.BroadMsg()
	
def SyncRoleOtherData(role, param):
	#上线同步缓存的活动数据(所有活动的结束时间)
	global KaifuTargetActiveCache_Dict
	role.SendObj(KaifuTargetActive_AllData, KaifuTargetActiveCache_Dict)
	
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadKaifuTargetAct()
		LoadNewKaifuTargetAct()
		
	if (Environment.HasLogic and not Environment.IsCross) or Environment.HasWeb:
		#{'accountSet':已经结算过的活动类型集合, targetType:{roleId:{1:[排名,是否领取奖励, 排行榜数据],}}
		KaifuTarget_Dict = Contain.Dict("KaifuTarget_Dict", (2038, 1, 1), AfterLoad)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		Event.RegEvent(Event.Eve_AfterSetKaiFuTime, AfterSetKaiFuTime)

		
