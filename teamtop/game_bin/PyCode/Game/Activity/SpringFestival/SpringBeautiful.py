#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SpringFestival.SpringBeautiful")
#===============================================================================
# 新春最靓丽
#===============================================================================
import Environment
import cProcess
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
from Common.Message import PyMessage, AutoMessage
from ComplexServer.Plug.Control import ControlProxy
from Common.Other import EnumGameConfig, GlobalPrompt, EnumSysData
from ComplexServer import Init
from ComplexServer.Log import AutoLog
from Game.Role import Rank, Event
from Game.GlobalData import ZoneName
from Game.SysData import WorldDataNotSync, WorldData
from Game.Role.Mail import Mail
from Game.Role.Data import EnumDayInt1
from Game.Persistence import Contain
from Game.Activity.SpringFestival import SpringFestivalConfig

if "_HasLoad" not in dir():
	IS_START = False	#活动开启标志
	ActiveID = 0		#激活的活动ID
	
	SpringBRank_Today = []	#今日跨服排行榜数据
	SpringBRank_Old = []	#昨日跨服排行榜数据
	
	SpringBOpen = AutoMessage.AllotMessage("SpringBOpen", "春节活动最靓丽活动开启")
	SpringBKuafuTodayRank = AutoMessage.AllotMessage("SpringBKuafuTodayRank", "春节活动最靓丽今日跨服排行榜")
	SpringBLocalTodayRank = AutoMessage.AllotMessage("SpringBLocalTodayRank", "春节活动最靓丽今日本地排行榜")
	SpringBKuafuYesterdayRank = AutoMessage.AllotMessage("SpringBKuafuYesterdayRank", "春节活动最靓丽昨日跨服排行榜")
	SpringBLocalYesterdayRank = AutoMessage.AllotMessage("SpringBLocalYesterdayRank", "春节活动最靓丽昨日本地排行榜")
	#日志
	SpringBLRank_Log = AutoLog.AutoTransaction("SpringBLRank_Log", "春节活动最靓丽本地排行榜")
	SpringBLRankScoreReward_Log = AutoLog.AutoTransaction("SpringBLRankScoreReward_Log", "春节活动最靓丽今日积分奖励")

class SpringBRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 100						#最大排行榜 100个
	dead_time = (2038, 1, 1)
	
	needSync = False						#这个排行榜需要同步客户端的, 查看消息在下面注册了, 可选查看今日和昨日排行榜
	
	name = "Rank_SpringBeautiful"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[0] < v2[0]
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		self.changeFlag = True
	
	def AfterLoadFun(self):
		Rank.SmallRoleRank.AfterLoadFun(self)
		global ActiveID
		TryUpdate(ActiveID)
		
def TryUpdate(activeId = 0, updateType = False):
	'''
	@param activeID:每次都要传入激活活动的ID, 如果ID不对的话尝试重新分配服务器类型
	@param updateType:是否需要更新服务器类型可选
	'''
	global IS_START
	if not IS_START: return
	
	if not activeId: return
	
	if not IsPersistenceDataOK():
		#数据没有完全载回
		return
	#服务器启动后，尝试重新计算服务器区域类型
	if not TryResetServerType(activeId, updateType):
		#服务器类型没有分配
		return
	#向控制进程请求跨服排行榜数据
	ControlProxy.SendControlMsg(PyMessage.Control_GetSpringBRank, (cProcess.ProcessID, GetServerType(), GetLogicRank()))
	
def ReturnServerType():
	#计算服务器类型并返回
	kaifuDay = WorldData.GetWorldKaiFuDay()
	for serverType, cfg in SpringFestivalConfig.SPRING_SERVER_TYPE_DICT.iteritems():
		if cfg.kaifuDay[0] <= kaifuDay <= cfg.kaifuDay[1]:
			return serverType
	else:
		print "GE_EXC, SpringBeautiful ReturnServerType can not find kaifuDay (%s) in SPRING_SERVER_TYPE_DICT" % kaifuDay
		#找不到的话返回第三区域服务器类型
		return 3
	
def TryResetServerType(activeID, updateType):
	#尝试重新计算服务器类型
	#当前服务器类型
	nowType = WorldData.WD.get(EnumSysData.SpringBRankServerType)
	#尝试重新分配后的服务器类型
	serverType = ReturnServerType()
	if not serverType:
		return
	if not nowType:
		#没有服务器类型, 分配服务器类型, 活动ID
		SetServerType(serverType, activeID)
	elif nowType and (updateType or activeID != WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.SpringBRankActID]):
		#有服务器类型, 需要更新服务器类型或者激活活动的ID不一致, 尝试重新计算服务器类型
		SetServerType(serverType, activeID)
		
	serverType = GetServerType()
	if serverType:
		#服务器区域有了, 广播开始
		cNetMessage.PackPyMsg(SpringBOpen, True)
		cRoleMgr.BroadMsg()
	
	return serverType

def SetServerType(serverType, activeID):
	#设置服务器类型和激活活动的ID
	WorldData.SetSpringBServerType(serverType)
#	WorldData.WD[EnumSysData.SpringBRankServerType] = serverType
	WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.SpringBRankActID] = activeID
	
def IsPersistenceDataOK():
	#依赖的持久化数据时候都已经载入完毕
	global SBR
	if not SBR.returnDB:
		#本服数据
		return False
	if not WorldData.WD.returnDB:
		#世界数据
		return False
	if not WorldDataNotSync.WorldDataPrivate.returnDB:
		#不广播客户端世界数据
		return False
	return True

def GetServerType():
	#根据开服时间获取服务器类型
	return WorldData.WD.get(EnumSysData.SpringBRankServerType)

def GetLogicRank():
	#返回本地排行榜
	global SBR
	return SBR.data.values()

def OpenSpringB(callArgv, regparam):
	#开启活动
	global IS_START
	if IS_START:
		print "GE_EXC, SpringBeautiful is already open"
		return
	
	IS_START = True
	
	#记下激活的活动ID
	global ActiveID
	ActiveID = regparam
	
	AfterFirstStart(regparam)
	
def AfterFirstStart(activeID):
	#活动开始触发(从没开始到开启)
	#有服务器类型 --> 判断活动ID是否一致, 不一致重新分配服务器类型和活动ID
	#没有服务器类型 --> 分配服务器类型和活动ID
	TryUpdate(activeID)
	
def CloseSpringB(callArgv, regparam):
	#关闭活动
	global IS_START
	if not IS_START:
		print "GE_EXC, SpringBeautiful is already close"
		return
	
	IS_START = False
	
	global SpringBRank_Today, SpringBRank_Old, SBR
	#清理排行榜数据
	SpringBRank_Today, SpringBRank_Old = [], []
	#清理本地排行榜数据
	SBR.Clear()
	#清理昨天数据
	global SB_List
	SB_List.clear()
	#广播结束
	cNetMessage.PackPyMsg(SpringBOpen, False)
	cRoleMgr.BroadMsg()
	
#======================进程=======================
def OnControlUpdataRank_T(sessionid, msg):
	'''
	控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	global SpringBRank_Today
	SpringBRank_Today = msg
	
def OnControlRequestRank(sessionid, msg):
	'''
	控制进程请求获取本服前100名数据 
	@param sessionid:
	@param msg:
	'''
	global SBR
	if not SBR.returnDB: return
	
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetServerType(), GetLogicRank()))
	
def OnControlUpdataRank(sessionid, msg):
	'''
	控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global SpringBRank_Today, SpringBRank_Old
	SpringBRank_Today, SpringBRank_Old = msg
	
#=========================事件=============================
def AfterSetKaiFuTime(param1, param2):
	#更改开服时间，尝试修改服务器区域类型
	#有服务器类型 --> 尝试修改服务器类型
	global ActiveID
	TryUpdate(ActiveID, updateType=True)
	
def AfterLoadWorldDataNotSync(param1, param2):
	#载入世界数据之后
	global ActiveID
	TryUpdate(ActiveID)
	
def AfterLoadWorldData(role, param):
	#载入世界数据之后
	global ActiveID
	TryUpdate(ActiveID)
	
def SyncRoleOtherData(role, param):
	global IS_START
	if not IS_START: return
	
	#活动开启
	role.SendObj(SpringBOpen, True)
	
	#登录后 触发入榜 兼容维护之前今日消费的神石
	global SBR
	if not SBR.returnDB: return
	
	cost = role.GetDayConsumeUnbindRMB()
	roleId = role.GetRoleID()
	
	if cost >= 3000:
		SBR.HasData(roleId, [cost, roleId, role.GetRoleName(), ZoneName.ZoneName])
		
def OnChangeUnbindRMB_S(role, param):
	#系统神石
	global SBR
	if not SBR.returnDB: return
	
	global IS_START
	if not IS_START: return
	
	oldValue, newValue = param
	
	if newValue >= oldValue:
		return
	
	cost = role.GetDayConsumeUnbindRMB()
	roleId = role.GetRoleID()
	
	if cost >= 1000:
		SBR.HasData(roleId, [cost, roleId, role.GetRoleName(), ZoneName.ZoneName])
		
def OnChangeUnbindRMB_Q(role, param):
	#充值神石
	global SBR
	if not SBR.returnDB: return
	
	global IS_START
	if not IS_START: return
	
	oldValue, newValue = param
	
	if newValue >= oldValue:
		return
	
	cost = role.GetDayConsumeUnbindRMB()
	roleId = role.GetRoleID()
	
	if cost >= 1000:
		SBR.HasData(roleId, [cost, roleId, role.GetRoleName(), ZoneName.ZoneName])
		
def AfterNewHour():
	#0点结算奖励并清理本地排行榜
	#小概率0点玩家积分数据可能被清理掉
	global IS_START
	if not IS_START: return
	
	if cDateTime.Hour() != 0:
		return
	
	#跨服排行榜清理
	global SpringBRank_Today, SpringBRank_Old
	SpringBRank_Old = SpringBRank_Today
	SpringBRank_Today = []
	
	global SBR
	#记录今日排行榜
	with SpringBLRank_Log:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveSpringBLRank, SBR.data)
		#保存今日排行榜
		SB_List.data = SBR.data.values()
		SB_List.HasChange()
	
	#排序:消费-->玩家ID
	localRankData = SBR.data.items()
	localRankData.sort(key = lambda x:(x[1][0], x[1][1]), reverse=True)
	
	tmpRankDict = {}	#{roleId:rank}
	tmpRank = 1			#初始排名
	maxRankLen = 10	#排行榜最大个数
	
	serverType = WorldData.WD.get(EnumSysData.SpringBRankServerType)
	NNG = SpringFestivalConfig.SPRING_LOCAL_RANK_DICT.get
	for (roleId, rankData) in localRankData:
		if tmpRank > maxRankLen:
			#超过排行榜最大个数了
			continue
		
		#先拿到当前排名需要的积分配置
		cfg = NNG((serverType,tmpRank))
		if not cfg:
			print 'GE_EXC, SpringBeautiful AfterNewHour can not find rank(%s) and serverType(%s) cfg' % (tmpRank, serverType)
			continue
		
		while rankData[0] < cfg.needScore:
			#如果当前的积分小于需要的积分, 排名往后加
			tmpRank += 1
			if tmpRank > maxRankLen:
				break
			#获取下一个排名的配置
			
			cfg = NNG((serverType,tmpRank))
			if not cfg:
				print 'GE_EXC, SpringBeautiful AfterNewHour can not find rank(%s) and serverType(%s) cfg2' % (tmpRank, serverType)
				continue
		
		if tmpRank > maxRankLen:
			break
		
		if rankData[0] < cfg.needScore:
			print 'GE_EXC, SpringBeautiful error'
			continue
		
		tmpRankDict[roleId] = tmpRank
		
		tmpRank += 1
		
	with SpringBLRank_Log:
		for roleId, rank in tmpRankDict.iteritems():
			cfg =  SpringFestivalConfig.SPRING_LOCAL_RANK_DICT.get((serverType,rank))
			if not cfg:
				print 'GE_EXC,can not find rank %s in SpringFestivalConfig.SPRING_LOCAL_RANK_DICT' % (rank)
				continue
			Mail.SendMail(roleId, GlobalPrompt.SpringBL_Title, GlobalPrompt.SpringBA_Sender, GlobalPrompt.SpringBL_Contend % rank, items=cfg.rewardItems, money=cfg.money, bindrmb=cfg.bindRMB)
		
	#清理今日排行榜
	SBR.Clear()

def afterLoad():
	global SB_List
	if len(SB_List) < 10:
		return
	
	SB_List.sort(key = lambda x:(x[0], x[1]), reverse = True)
	SB_List.data = SB_List[:10]
	SB_List.changeFlag = True
#===========================================================
def RequestOpenPanel(role, param):
	'''
	请求打开面板
	@param role:
	@param param:
	'''
	global IS_START
	if not IS_START: return
	
	global SBR
	if not SBR.returnDB: return
	
	#跨服排名
	global SpringBRank_Today
	role.SendObj(SpringBKuafuTodayRank, SpringBRank_Today)
	#本地排名
	role.SendObj(SpringBLocalTodayRank, SBR.data.values())
	
def RequestReward(role, msg):
	'''
	请求领取今日消费奖励
	@param role:
	@param msg:
	'''
	global IS_START
	if not IS_START: return
	
	global SBR
	if not SBR.returnDB: return
	
	if role.GetDI1(EnumDayInt1.NewYearHaoFlag):
		return
	
	cost = role.GetDayConsumeUnbindRMB()
	
	if cost < EnumGameConfig.SPRING_MIN_SCORE:
		return
	
	cfg = SpringFestivalConfig.SPRING_REWARD_DICT.get(1)
	if not cfg:
		print 'GE_EXC, SpringBeautiful can not find score reward'
		return
	
	with SpringBLRankScoreReward_Log:
		role.SetDI1(EnumDayInt1.NewYearHaoFlag, True)
		
		tips = GlobalPrompt.Reward_Tips
		for item in cfg.rewardItems:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		role.Msg(2, 0, tips)
		
def RequestWatchTodayRank(role, msg):
	'''
	请求查看今日排名
	@param role:
	@param msg:1-本地, 2-跨服
	'''
	global IS_START
	if not IS_START: return
	
	global SBR
	if not SBR.returnDB: return
	
	if msg == 1:
		role.SendObj(SpringBLocalTodayRank, SBR.data.values())
	else:
		global SpringBRank_Today
		role.SendObj(SpringBKuafuTodayRank, SpringBRank_Today)
		
def RequestWatchYesterdayRank(role, msg):
	'''
	请求查看昨日排名
	@param role:
	@param msg:1-本地, 2-跨服
	'''
	global IS_START
	if not IS_START: return
	
	global SBR
	if not SBR.returnDB: return
	
	if msg == 1:
		global SB_List
		role.SendObj(SpringBLocalYesterdayRank, SB_List.data)
	else:
		global SpringBRank_Old
		role.SendObj(SpringBKuafuYesterdayRank, SpringBRank_Old)
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#春节最靓丽排行榜
		SBR = SpringBRank()
		#春节最靓丽昨日排行榜
		SB_List = Contain.List("SB_List", (2038, 1, 1), afterLoad)
		#注册服务器启动调用函数
		Init.InitCallBack.RegCallbackFunction(TryUpdate)
		
		#请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicSpringBRank, OnControlRequestRank)
		#发送跨服排行榜数据到逻辑进程(今天, 昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdateSpringBRankToLogic, OnControlUpdataRank)
		#发送跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdateSpringBRankToLogic_T, OnControlUpdataRank_T)
		
		Event.RegEvent(Event.Eve_AfterSetKaiFuTime, AfterSetKaiFuTime)
		Event.RegEvent(Event.Eve_AfterLoadWorldDataNotSync, AfterLoadWorldDataNotSync)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, OnChangeUnbindRMB_Q)
		Event.RegEvent(Event.AfterChangeUnbindRMB_S, OnChangeUnbindRMB_S)
		
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SpringB_OpenPanel", "请求打开春节最靓丽面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SpringB_Reward", "春节最靓丽积分奖励"), RequestReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SpringB_TodayRank", "春节最靓丽查看今日排行榜"), RequestWatchTodayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("SpringB_YesterdayRank", "春节最靓丽查看昨日排行榜"), RequestWatchYesterdayRank)