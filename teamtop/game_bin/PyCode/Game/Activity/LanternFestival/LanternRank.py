#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.LanternFestival.LanternRank")
#===============================================================================
# 花灯高手
#===============================================================================
import cProcess
import cRoleMgr
import cNetMessage
import cRoleDataMgr
import Environment
import cComplexServer
from ComplexServer import Init
from Game.Role.Mail import Mail
from Game.Role import Rank, Event
from Game.SysData import WorldData
from Game.Persistence import Contain
from Game.Role.Data import EnumInt32, EnumObj
from Game.GlobalData import ZoneName
from ComplexServer.Log import AutoLog
from Common.Message import PyMessage, AutoMessage
from ComplexServer.Plug.Control import ControlProxy
from Common.Other import GlobalPrompt, EnumSysData, EnumGameConfig
from Game.Activity.LanternFestival import LanternFestivalConfig


if "_HasLoad" not in dir():
	IsStart = False
	MaxRankReward = 100
	
	CrossRank_T = []			#跨服排行榜(T short for Today)
	CrossRank_Y = []			#跨服排行榜(Y short for Yesterday)
	
	#消息
	LanternRankIsStart = AutoMessage.AllotMessage("LanternRankIsStart", "元宵节活动点灯高手开启情况")
	LanternRankTCross = AutoMessage.AllotMessage("LanternRankTCross", "元宵节活动点灯高手今日跨服排行榜")
	LanternRankTLocal = AutoMessage.AllotMessage("LanternRankTLocal", "元宵节活动点灯高手今日本服排行榜")
	LanternRankYCross = AutoMessage.AllotMessage("LanternRankYCross", "元宵节活动点灯高手昨日本服排行榜")
	LanternRankYLocal = AutoMessage.AllotMessage("LanternRankYLocal", "元宵节活动点灯高手昨日本服排行榜")
	LanternTargetGotData = AutoMessage.AllotMessage("LanternTargetGotData", "元宵节每日积分目标奖励已领取情况")
	
	#日志
	Tra_LanternPointRank = AutoLog.AutoTransaction("Tra_LanternPointRank", "元宵节活动花灯高手排行榜")
	Tra_LanternPointRankReward = AutoLog.AutoTransaction("Tra_LanternPointRankReward", "元宵节活动花灯高手排行榜奖励")
	Tra_LanternPointTargetReward = AutoLog.AutoTransaction("Tra_LanternPointTargetReward", "元宵节活动花灯高手积分目标奖励")


class LanternRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 10						#最大排行榜50个
	dead_time = (2038, 1, 1)
	needSync = False						#不需要同步给客户端 
	name = "Rank_LanternFestivalPoint"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[:3] < v2[:3]
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		self.changeFlag = True
	
	def AfterLoadFun(self):
		Rank.SmallRoleRank.AfterLoadFun(self)
		AfterLoadLocalRank()


def AfterLoadLocalRank():
	if IsStart is False:
		return
	if not WorldData.WD.returnDB:
		return
	localRank = GetLocalRank()
	serverType = GetServerType()
	ControlProxy.SendControlMsg(PyMessage.Logic_RequestGetCrossLanternRank, (cProcess.ProcessID, serverType, localRank))


def TryAllotServerType(force=False):
	'''
	尝试分配服务器分区类型
	'''
	if force is False:
		if WorldData.WD[EnumSysData.LanternRankServerType] is not None:
			return
		
	kaifuDay = WorldData.GetWorldKaiFuDay()
	
	for serverType, cfg in LanternFestivalConfig.LanternServerTypeDict.iteritems():
		if cfg.kaifuDay[0] <= kaifuDay <= cfg.kaifuDay[1]:
			WorldData.SetLanternRankServertype(serverType)
			break
	else:
		print "GE_EXC, TryAllotServerType can not find kaifuDay (%s) in LanternServerTypeDict" % kaifuDay
		WorldData.SetLanternRankServertype(1)


def AfterLoadWorldData(callargv, param):
	'''
	'''
	if IsStart is False:
		return
	TryAllotServerType()


def Start(callArgv, regparam):
	'''
	活动开始
	'''
	global IsStart
	if IsStart is True:
		return
	IsStart = True

	if WorldData.WD.returnDB is False:
		return
	TryAllotServerType()
	RequestGetCrossRank()
	
	
	#同步客户端活动开启
	cNetMessage.PackPyMsg(LanternRankIsStart, IsStart)
	cRoleMgr.BroadMsg()
	

def End(callArgv, regparam):
	'''
	活动结束
	'''
	global IsStart
	if IsStart is False:
		return
	IsStart = False
	
	global CrossRank_T, CrossRank_Y
	CrossRank_T = []			#跨服排行榜(T short for Today)
	CrossRank_Y = []			#跨服排行榜(Y short for Yesterday)
	#活动结束清空排行榜
	global LR, LanternRankYesterdayList
	LR.Clear()
	LanternRankYesterdayList.clear()
	#活动结束的时候把服务器的区域类型置为None
	WorldData.WD[EnumSysData.LanternRankServerType] = None

	#同步客户端活动开启
	cNetMessage.PackPyMsg(LanternRankIsStart, IsStart)
	cRoleMgr.BroadMsg()


def AfterSetKaifuTime(param1, param2):
	'''
	活动期间如果设置了开服时间要重新分配服务器类型
	'''
	global IsStart
	if IsStart is False:
		return
	TryAllotServerType(force=True)


def AfterChangeLanternPointDaily(role, oldValue, newValue):
	'''
	角色每日点灯积分变化后的处理
	'''
	if IsStart is False:
		return
	if newValue <= oldValue:
		return
	roleID = role.GetRoleID()
	global LR
	LR.HasData(roleID, [newValue, role.GetZDL(), roleID, role.GetRoleName(), ZoneName.ZoneName])


def GetLocalRank():
	'''
	获取本服排行榜
	'''
	return LR.data.values()


def GetServerType():
	#根据开服时间获取服务器类型
	if WorldData.WD[EnumSysData.LanternRankServerType] is None:
		TryAllotServerType()
		
	return WorldData.WD[EnumSysData.LanternRankServerType]


def IsPersistenceDataOK():
	#依赖的持久化数据时候都已经载入完毕
	if not LR.returnDB:
		#本服数据
		return False
	if not WorldData.WD.returnDB:
		#世界数据
		return False
	return True

#===============================================================================
# 起服的时候如果活动已经开启了则应该立即将数据同步给控制进程,这里用了四个触发，同步数据的时候本服排行榜数据已经返回并且本服区域类型已经分配
# 排行榜after load,worldData after load,活动开始各尝试同步一次
#===============================================================================

def RequestGetCrossRank():
	#以下两步确保服务器已经分配了分区类型并且本服排行榜数据已经载回
	if IsStart is False:
		return
	if not IsPersistenceDataOK():
		return
	
	#发送进程消息
	localRank = GetLocalRank()
	serverType = GetServerType()
	ControlProxy.SendControlMsg(PyMessage.Logic_RequestGetCrossLanternRank, (cProcess.ProcessID, serverType, localRank))


def OnControlUpdataRank_T(sessionid, msg):
	'''
	控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	global CrossRank_T
	CrossRank_T = msg


def OnControlUpdataRank(sessionid, msg):
	'''
	控制进程更新了新的跨服排行榜数据过来(昨天)
	@param sessionid:
	@param msg:
	'''
	global CrossRank_Y, CrossRank_T
	CrossRank_T, CrossRank_Y = msg


def OnControlRequestRank(sessionid, msg):
	'''
	控制进程请求获取本服前100名数据 
	@param sessionid:
	@param msg:
	'''
	if not WorldData.WD.returnDB:
		return
	
	if not LR.returnDB: 
		return
	
	localRank = LR.data.values()
	serverType = GetServerType()
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, serverType, localRank))


#===============================================================================
# 元宵节活动就这么一次，故服务器分区一旦确定就不再改变
# 这里三触发确定服务器分区类型 
#===============================================================================


def DailyClear(role, param):
	'''
	每日清理
	'''
	role.SetI32(EnumInt32.LanternFestivalPointDaily, 0)


def CallAfterNewDay():
	'''
	'''
	#跨天的时候使用本地缓存排行榜数据更新今日昨日排行榜数据
	if IsStart is False:
		return
	
	global CrossRank_T, CrossRank_Y
	CrossRank_T, CrossRank_Y = [], CrossRank_T
	
	#当日排行榜记录日志
	global LR, LanternRankYesterdayList
	with Tra_LanternPointRank:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveLanternLocalRank, LR.data)
		#保存今日排行榜
		LanternRankYesterdayList.data = LR.data.values()
		LanternRankYesterdayList.HasChange()
	
	#排序:消费-->玩家ID
	localRankList = LR.data.items()[:MaxRankReward]
	localRankList.sort(key=lambda x:x[1][:3], reverse=True)
	
	if WorldData.WD.returnDB is False:
		print "GE_EXC,LanternRank CallAfterNewDay but not WorldData.WD.returnDB"
		return
	
	serverType = WorldData.WD[EnumSysData.LanternRankServerType]
	
	tmpRank = 1			#初始排名
	maxRankLen = 10
	tmpRankDict = {}
	LG = LanternFestivalConfig.LanternRankConfigDict.get
	
	for roleId, rankData in localRankList:
		if tmpRank > maxRankLen:
			continue
		#先拿到当前排名需要的积分配置
		cfg = LG((tmpRank, serverType))
		if not cfg:
			print 'GE_EXC, LanternRankConfigDict can not find (tmpRank, serverType)(%s,%s) cfg' % (tmpRank, serverType)
			continue
		
		while rankData[0] < cfg.needScore:
			#如果当前的积分小于需要的积分, 排名往后加
			tmpRank += 1
			if tmpRank > maxRankLen:
				break
			#获取下一个排名的配置
			cfg = LG((tmpRank, serverType))
			if not cfg:
				print 'GE_EXC, LanternRankConfigDict can not find (tmpRank, serverType)(%s,%s) cfg' % (tmpRank, serverType)
				continue
		
		if tmpRank > maxRankLen:
			#跳出for循环
			break
		
		if rankData[0] < cfg.needScore:
			print 'GE_EXC, AfterNewHour error'
			continue
		
		tmpRankDict[roleId] = tmpRank
		#完了排名+1
		tmpRank += 1
		
	for roleID, rank in tmpRankDict.iteritems():
		config = LG((rank, serverType))
		with Tra_LanternPointRankReward:
			Mail.SendMail(roleID,
						GlobalPrompt.LanternFesitivalL_Title,
						GlobalPrompt.LanternFesitivalL_Sender,
						GlobalPrompt.LanternFesitivalL_Content % rank,
						items=config.rewardItems,
						money=config.money,
						bindrmb=config.bindRMB)
	#清除排行榜的数据
	LR.Clear()


def RequestOpenPanel(role, param):
	'''
	请求打开面板
	@param role:
	@param param:
	'''
	global IsStart
	if not IsStart: 
		return
	
	global LR
	if not LR.returnDB: 
		return


def RequestReadTodayRank(role, msg):
	'''
	客户端请求查看点灯达人今日排行榜
	@param msg:1-本地, 2-跨服
	'''
	if IsStart is False:
		return

	if not LR.returnDB: 
		return
	
	if msg == 1:
		role.SendObj(LanternRankTLocal, LR.data.values())
		
	elif msg == 2:
		role.SendObj(LanternRankTCross, CrossRank_T)


def RequestReadYesterdayRank(role, msg):
	'''
	客户端请求查看点灯达人昨日排行榜
	@param msg:1-本地, 2-跨服
	'''
	if IsStart is False:
		return
	
	if not LanternRankYesterdayList.returnDB: 
		return
	
	if msg == 1:
		role.SendObj(LanternRankYLocal, LanternRankYesterdayList.data)
	elif msg == 2:
		role.SendObj(LanternRankYCross, CrossRank_Y)



def SyncRoleOtherData(role, param):
	if not IsStart: 
		return
	
	role.SendObj(LanternRankIsStart, IsStart)
	
	gotSet = role.GetObj(EnumObj.LanternFestival).get('target', set())
	role.SendObj(LanternTargetGotData, gotSet)
	

def AfterLoad():
	global LanternRankYesterdayList
	if len(LanternRankYesterdayList) < 10:
		return
	
	LanternRankYesterdayList.sort(key=lambda x:x[:3], reverse=True)
	LanternRankYesterdayList.data = LanternRankYesterdayList[:10]
	LanternRankYesterdayList.HasChange()


def RoleDayClear(role, param):
	role.SetI32(EnumInt32.LanternFestivalPointDaily, 0)
	role.GetObj(EnumObj.LanternFestival)['target'] = set()
	role.SendObj(LanternTargetGotData, set())


#===============================================================================
# 积分目标
#===============================================================================
def RequestGetPointTargetAward(role, msg):
	'''
	客户端请求获取每日积分目标奖励
	'''
	if IsStart is False:
		return
	if role.GetLevel() < EnumGameConfig.LanternFestivalNeedLevel:
		return
	index = msg
	gotSet = role.GetObj(EnumObj.LanternFestival).setdefault('target', set())
	if index in gotSet:
		return
	
	config = LanternFestivalConfig.LanternFestivalTargetDict.get(index, None)
	if config is None:
		return
	#每日点灯积分没有达到要求
	if role.GetI32(EnumInt32.LanternFestivalPointDaily) < config.NeedPoint:
		return
	
	tips = GlobalPrompt.Reward_Tips
	with Tra_LanternPointTargetReward:
		gotSet.add(index)
		if config.Items:
			for item in config.Items:
				if item[1]:
					role.AddItem(*item)
					tips += GlobalPrompt.Item_Tips % item
	
	role.SendObj(LanternTargetGotData, gotSet)
	role.Msg(2, 0, tips)
					

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LR = LanternRank()
		#这里用一个持久化列表记录昨天的本服排行榜
		LanternRankYesterdayList = Contain.List("LanternRankYesterday", (2038, 1, 1), AfterLoad)
		#注册服务器启动调用函数
		Init.InitCallBack.RegCallbackFunction(RequestGetCrossRank)
		
		cComplexServer.RegAfterNewDayCallFunction(CallAfterNewDay)
		
		cRoleDataMgr.SetInt32Fun(EnumInt32.LanternFestivalPointDaily, AfterChangeLanternPointDaily)
		
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		Event.RegEvent(Event.Eve_AfterSetKaiFuTime, AfterSetKaifuTime)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		#请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicLanternRank, OnControlRequestRank)
		#发送跨服排行榜数据到逻辑进程(今天, 昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdateLanternRankToLogic, OnControlUpdataRank)
		#发送跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdateLanternRankToLogic_T, OnControlUpdataRank_T)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestLanternRankYesterday", "客户端请求查看点灯达人昨日排行榜"), RequestReadYesterdayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestLanternRankToday", "客户端请求查看点灯达人今日排行榜"), RequestReadTodayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestLanternTargetAwardToday", "客户端请求领取点灯积分目标奖励"), RequestGetPointTargetAward)
		
		

		
