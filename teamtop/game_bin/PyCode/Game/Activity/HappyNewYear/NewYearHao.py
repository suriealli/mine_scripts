#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HappyNewYear.NewYearHao")
#===============================================================================
# 新年乐翻天-新年我最壕
#===============================================================================
import Environment
import cProcess
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
from Common.Message import PyMessage, AutoMessage
from ComplexServer.Plug.Control import ControlProxy
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer import Init
from ComplexServer.Log import AutoLog
from Game.Role import Rank, Event
from Game.GlobalData import ZoneName
from Game.Role.Mail import Mail
from Game.Activity.HappyNewYear import NewYearConfig
from Game.Role.Data import EnumInt32, EnumDayInt1
from Game.Persistence import Contain

TWO_MINUTE_SECONDS = 120			#两分钟秒数
ONE_DAY_SECONDS = 24 * 60 * 60		#一天的总秒数

if "_HasLoad" not in dir():
	NewYearHaoIsOpen = False					#新年我最壕开启标志
	
	NewYearHaoControlRank = []					#今日跨服排行榜数据
	NewYearHaoControlRank_Old = []				#昨日跨服排行榜数据
	
	#True or False
	NewYearHaoOpen = AutoMessage.AllotMessage("NewYearHaoOpen", "新年我最壕活动开启")
	#今日跨服排行榜 -- [[消费, 角色ID, 角色名字, 服务器名字]]
	NewYearHaoKuafuTodayRank = AutoMessage.AllotMessage("NewYearHaoKuafuTodayRank", "新年我最壕今日跨服排行榜")
	#昨日跨服排行榜 -- [[消费, 角色ID, 角色名字, 服务器名字]]
	NewYearHaoKuafuYesterdayRank = AutoMessage.AllotMessage("NewYearHaoKuafuYesterdayRank", "新年我最壕昨日跨服排行榜")
	#今日本地排行榜 -- {roleId:[消费, 角色ID, 角色名字, 服务器名字]}
	NewYearHaoLocalTodayRank = AutoMessage.AllotMessage("NewYearHaoLocalTodayRank", "新年我最壕今日本地排行榜")
	#今日本地排行榜 -- {roleId:[消费, 角色ID, 角色名字, 服务器名字]}
	NewYearHaoLocalYesterdayRank = AutoMessage.AllotMessage("NewYearHaoLocalYesterdayRank", "新年我最壕昨日本地排行榜")
	
	NewYearHaoScoreReward_Log = AutoLog.AutoTransaction("NewYearHaoScoreReward_Log", "新年我最壕今日积分奖励")
	NewYearHaoScoreLRankReward_Log = AutoLog.AutoTransaction("NewYearHaoScoreLRankReward_Log", "新年我最壕本地排行奖励")
	NewYearHaoScoreLRank_Log = AutoLog.AutoTransaction("NewYearHaoScoreLRank_Log", "新年我最壕本地排行榜")
	NewYearHaoConsume_Log = AutoLog.AutoTransaction("NewYearHaoConsume_Log", "新年乐翻天消费")
	
	
class NewYearHaoRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 100						#最大排行榜 100个
	dead_time = (2038, 1, 1)
	
	needSync = False						#这个排行榜需要同步客户端的, 查看消息在下面注册了, 可选查看今日和昨日排行榜
	
	name = "Rank_NewYearHao"
	
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
		TryUpdate()
		
def TryUpdate():
	'''
	排行榜数据载回来后尝试更新富豪榜
	'''
	global NewYearHaoIsOpen
	if not NewYearHaoIsOpen: return
	
	#向控制进程请求跨服排行榜数据
	ControlProxy.SendControlMsg(PyMessage.Control_GetNewYearHaoRank, (cProcess.ProcessID, GetLogicRank()))

def GetLogicRank():
	#返回本地排行榜
	return NYHR.data.values()

def RequestRank():
	#起服的时候向控制进程请求跨服排行榜数据
	global NewYearHaoIsOpen
	if not NewYearHaoIsOpen: return
	
	global NYHR
	if not NYHR.returnDB: return
	
	ControlProxy.SendControlMsg(PyMessage.Control_GetNewYearHaoRank, (cProcess.ProcessID, GetLogicRank()))
#===============================================================================
# 进程
#===============================================================================
def OnControlUpdataRank_T(sessionid, msg):
	'''
	控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	global NewYearHaoControlRank
	NewYearHaoControlRank = msg

def OnControlUpdataRank(sessionid, msg):
	'''
	控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global NewYearHaoControlRank, NewYearHaoControlRank_Old
	NewYearHaoControlRank, NewYearHaoControlRank_Old = msg
	
def OnControlRequestRank(sessionid, msg):
	'''
	控制进程请求获取本服前100名数据 
	@param sessionid:
	@param msg:
	'''
	global NYHR
	if not NYHR.returnDB: return
	
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetLogicRank()))
#===============================================================================
# 事件
#===============================================================================
def AfterNewHour():
	#0点结算奖励并清理本地排行榜
	#小概率0点玩家积分数据可能被清理掉
	global NewYearHaoIsOpen
	if not NewYearHaoIsOpen: return
	
	if cDateTime.Hour() != 0:
		return
	
	#跨服排行榜清理
	global NewYearHaoControlRank, NewYearHaoControlRank_Old
	NewYearHaoControlRank_Old = NewYearHaoControlRank
	NewYearHaoControlRank = []
	
	global NYHR
	#记录今日排行榜
	with NewYearHaoScoreLRank_Log:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveNewYearLocalRank, NYHR.data)
		#保存今日排行榜
		NYH_List.data = NYHR.data.values()
		NYH_List.HasChange()
	
	#排序:消费-->玩家ID
	localRankData = NYHR.data.items()
	localRankData.sort(key = lambda x:(x[1][0], x[1][1]), reverse=True)
	
	tmpRankDict = {}	#{roleId:rank}
	tmpRank = 1			#初始排名
	maxRankLen = 10		#排行榜最大个数
	
	NNG = NewYearConfig.NewYearLRank_Dict.get
	for (roleId, rankData) in localRankData:
		if tmpRank > maxRankLen:
			#超过排行榜最大个数了
			continue
		
		#先拿到当前排名需要的积分配置
		cfg = NNG(tmpRank)
		if not cfg:
			print 'GE_EXC, AfterNewHour can not find rank %s cfg' % tmpRank
			continue
		
		while rankData[0] < cfg.needScore:
			#如果当前的积分小于需要的积分, 排名往后加
			tmpRank += 1
			if tmpRank > maxRankLen:
				break
			#获取下一个排名的配置
			cfg = NNG(tmpRank)
			if not cfg:
				print 'GE_EXC, AfterNewHour can not find rank %s cfg' % tmpRank
				continue
		
		if tmpRank > maxRankLen:
			break
		
		if rankData[0] < cfg.needScore:
			print 'GE_EXC, AfterNewHour error'
			continue
		
		tmpRankDict[roleId] = tmpRank
		
		tmpRank += 1
		
	with NewYearHaoScoreLRank_Log:
		for roleId, rank in tmpRankDict.iteritems():
			cfg =  NewYearConfig.NewYearLRank_Dict.get(rank)
			if not cfg:
				print 'GE_EXC, haoqi can not find rank %s in HaoqiLocalRank_Dict' % (rank)
				continue
			Mail.SendMail(roleId, GlobalPrompt.NYEARHaoReward_Title, GlobalPrompt.NYEARHaoReward_Sender, GlobalPrompt.NYEARHaoReward_Content % rank, items=cfg.rewardItems, money=cfg.money, bindrmb=cfg.bindRMB)
		
	#清理今日排行榜
	NYHR.Clear()
	
def SyncRoleOtherData(role, param):
	global NewYearHaoIsOpen
	if not NewYearHaoIsOpen: return
	
	#活动开启
	role.SendObj(NewYearHaoOpen, True)
	
	#登录后 触发入榜 兼容维护之前今日充值数
	global NYHR
	if not NYHR.returnDB: return
	
	recharge = role.GetDayBuyUnbindRMB_Q()
	roleId = role.GetRoleID()
	
	if recharge >= 3000:
		NYHR.HasData(roleId, [recharge, roleId, role.GetRoleName(), ZoneName.ZoneName])
	
def OpenNewYearHao(callArgv, regparam):
	global NewYearHaoIsOpen
	if NewYearHaoIsOpen:
		print "GE_EXC, NewYearHao is already open"
		return
	NewYearHaoIsOpen = True
	
	#同步客户端活动开启
	cNetMessage.PackPyMsg(NewYearHaoOpen, True)
	cRoleMgr.BroadMsg()
	
def CloseNewYearHao(callArgv, regparam):
	global NewYearHaoIsOpen
	if not NewYearHaoIsOpen:
		print "GE_EXC, NewYearHao is already close"
		return
	NewYearHaoIsOpen = False
	
	global NewYearHaoControlRank, NewYearHaoControlRank_Old, NYHR
	NewYearHaoControlRank, NewYearHaoControlRank_Old = [], []
	
	#清理本地排行榜
	global NYHR
	NYHR.Clear()
	
	#清理
	global NYH_List
	NYH_List.clear()
	
	#同步客户端活动关闭
	cNetMessage.PackPyMsg(NewYearHaoOpen, False)
	cRoleMgr.BroadMsg()
	
def RequestOpenPanel(role, param):
	'''
	请求打开面板
	@param role:
	@param param:
	'''
	global NewYearHaoIsOpen
	if not NewYearHaoIsOpen: return
	
	global NYHR
	if not NYHR.returnDB: return
	
	#跨服排名
	global NewYearHaoControlRank
	role.SendObj(NewYearHaoKuafuTodayRank, NewYearHaoControlRank)
	#本地排名
	role.SendObj(NewYearHaoLocalTodayRank, NYHR.data.values())
	
def RequestWatchTodayRank(role, msg):
	'''
	请求查看今日排名
	@param role:
	@param msg:1-本地, 2-跨服
	'''
	global NewYearHaoIsOpen
	if not NewYearHaoIsOpen: return
	
	global NYHR
	if not NYHR.returnDB: return
	
	if msg == 1:
		role.SendObj(NewYearHaoLocalTodayRank, NYHR.data.values())
	else:
		global NewYearHaoControlRank
		role.SendObj(NewYearHaoKuafuTodayRank, NewYearHaoControlRank)
	
def RequestWatchYesterdayRank(role, msg):
	'''
	请求查看昨日排名
	@param role:
	@param msg:1-本地, 2-跨服
	'''
	global NewYearHaoIsOpen
	if not NewYearHaoIsOpen: return
	
	global NYHR
	if not NYHR.returnDB: return
	
	if msg == 1:
		global NYH_List
		role.SendObj(NewYearHaoLocalYesterdayRank, NYH_List.data)
	else:
		global NewYearHaoControlRank_Old
		role.SendObj(NewYearHaoKuafuYesterdayRank, NewYearHaoControlRank_Old)
	
def RequestReward(role, msg):
	'''
	请求领取今日充值奖励
	@param role:
	@param msg:
	'''
	global NewYearHaoIsOpen
	if not NewYearHaoIsOpen: return
	
	global NYHR
	if not NYHR.returnDB: return
	
	if role.GetDI1(EnumDayInt1.NewYearHaoFlag):
		return
	
	recharge = role.GetDayBuyUnbindRMB_Q()
	
	if recharge < EnumGameConfig.NYEAR_MIN_SCORE:
		return
	
	cfg = NewYearConfig.NewYearScoreReward_Dict.get(1)
	if not cfg:
		print 'GE_EXC, NewYearHao can not find score reward'
		return
	
	with NewYearHaoScoreReward_Log:
		role.SetDI1(EnumDayInt1.NewYearHaoFlag, True)
		
		tips = GlobalPrompt.Reward_Tips
		for item in cfg.rewardItems:
			role.AddItem(*item)
			tips += GlobalPrompt.Item_Tips % item
		role.Msg(2, 0, tips)
	
def afterLoad():
	global NYH_List
	if len(NYH_List) <= 100:
		return
	
	#和服了 ? 要排一次序
	NYH_List.sort(key = lambda x:(x[0], x[1]), reverse = True)
	NYH_List.data = NYH_List[:100]
	NYH_List.changeFlag = True
	
def OnChangeUnbindRMB_Q(role, param):
	global NYHR
	if not NYHR.returnDB: return
	
	global NewYearHaoIsOpen
	if not NewYearHaoIsOpen: return
	
	#非充值
	oldValue, newValue = param
	if oldValue >= newValue:
		return
	
	recharge = role.GetDayBuyUnbindRMB_Q()
	roleId = role.GetRoleID()
	
	if recharge >= 3000:
		NYHR.HasData(roleId, [recharge, roleId, role.GetRoleName(), ZoneName.ZoneName])
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#新年我最壕充值排行榜
		NYHR = NewYearHaoRank()
		#新年我最壕昨日排行榜
		NYH_List = Contain.List("NYH_List", (2038, 1, 1), afterLoad)
		
		#注册服务器启动调用函数
		Init.InitCallBack.RegCallbackFunction(RequestRank)
		
		#请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicNewYearHaoRank, OnControlRequestRank)
		#发送跨服排行榜数据到逻辑进程(今天, 昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataNewYearHaoRankToLogic, OnControlUpdataRank)
		#发送跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataNewYearHaoRankToLogic_T, OnControlUpdataRank_T)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, OnChangeUnbindRMB_Q)
		
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NewYearHao_OpenPanel", "请求打开新年我最壕面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NewYearHao_Reward", "新年我最壕领取积分奖励"), RequestReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NewYearHao_TodayRank", "新年我最壕查看今日排行榜"), RequestWatchTodayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("NewYearHao_YesterdayRank", "新年我最壕查看昨日排行榜"), RequestWatchYesterdayRank)
