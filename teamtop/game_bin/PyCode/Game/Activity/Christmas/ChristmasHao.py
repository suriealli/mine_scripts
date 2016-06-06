#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Christmas.ChristmasHao")
#===============================================================================
# 圣诞嘉年华 - 有钱就是任性
#===============================================================================
import Environment
import cProcess
import cRoleMgr
import cDateTime
import cNetMessage
import cRoleDataMgr
import cComplexServer
from Common.Message import PyMessage, AutoMessage
from ComplexServer.Plug.Control import ControlProxy
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer import Init
from ComplexServer.Log import AutoLog
from Game.Role import Rank, Event
from Game.GlobalData import ZoneName
from Game.Role.Mail import Mail
from Game.Activity.Christmas import ChristmasHaoConfig
from Game.Role.Data import EnumInt32, EnumDayInt1

if "_HasLoad" not in dir():
	ChristmasHaoIsOpen = False					#有钱就是任性开启标志
	
	ChristmasHaoControlRank = []				#今日跨服排行榜数据
	ChristmasHaoControlRank_Old = []			#昨日跨服排行榜数据
	
	ChristmasHaoOpen = AutoMessage.AllotMessage("ChristmasHaoOpen", "有钱就是任性活动开启")
	ChristmasHaoKuafuTodayRank = AutoMessage.AllotMessage("ChristmasHaoKuafuTodayRank", "有钱就是任性今日跨服排行榜")
	ChristmasHaoKuafuYesterdayRank = AutoMessage.AllotMessage("ChristmasHaoKuafuYesterdayRank", "有钱就是任性昨日跨服排行榜")
	
	ChristmasHaoExpReward_Log = AutoLog.AutoTransaction("ChristmasHaoExpReward_Log", "有钱就是任性今日积分奖励")
	
class ChristmasHaoRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 100						#最大排行榜 100个
	dead_time = (2038, 1, 1)
	
	needSync = False						#这个排行榜需要同步客户端的, 查看消息在下面注册了, 可选查看今日和昨日排行榜
	
	name = "Rank_ChristmasHao"
	
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
	global ChristmasHaoIsOpen
	if not ChristmasHaoIsOpen: return
	
	#向控制进程请求跨服排行榜数据
	ControlProxy.SendControlMsg(PyMessage.Control_GetChristmasHaoRank, (cProcess.ProcessID, GetLogicRank()))

def GetLogicRank():
	#返回本地排行榜
	return CHR.data.values()

def RequestRank():
	#起服的时候向控制进程请求跨服排行榜数据
	global ChristmasHaoIsOpen
	if not ChristmasHaoIsOpen: return
	
	global CHR
	if not CHR.returnDB: return
	
	ControlProxy.SendControlMsg(PyMessage.Control_GetChristmasHaoRank, (cProcess.ProcessID, GetLogicRank()))
#===============================================================================
# 进程
#===============================================================================
def OnControlUpdataRank_T(sessionid, msg):
	'''
	控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	global ChristmasHaoControlRank
	ChristmasHaoControlRank = msg

def OnControlUpdataRank(sessionid, msg):
	'''
	控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global ChristmasHaoControlRank, ChristmasHaoControlRank_Old
	ChristmasHaoControlRank, ChristmasHaoControlRank_Old = msg
	
def OnControlRequestRank(sessionid, msg):
	'''
	控制进程请求获取本服前100名数据 
	@param sessionid:
	@param msg:
	'''
	global CHR
	if not CHR.returnDB: return
	
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetLogicRank()))
#===============================================================================
# 事件
#===============================================================================
def AfterNewHour():
	#0点结算奖励并清理本地排行榜
	#小概率0点玩家积分数据可能被清理掉
	global ChristmasHaoIsOpen
	if not ChristmasHaoIsOpen: return
	
	if cDateTime.Hour() != 0:
		return
	
	#跨服排行榜清理
	global ChristmasHaoControlRank, ChristmasHaoControlRank_Old
	ChristmasHaoControlRank_Old = ChristmasHaoControlRank
	ChristmasHaoControlRank = []
	
	#清理本地排行榜
	global CHR
	CHR.Clear()
	
def AfterChangeChristmasConsume(role, oldValue, newValue):
	#记录圣诞消费积分
	global ChristmasHaoIsOpen
	if not ChristmasHaoIsOpen: return
	
	global CHR
	if not CHR.returnDB: return
	
	if newValue <= oldValue:
		return
	
	roleId = role.GetRoleID()
	
	if newValue >= EnumGameConfig.ChristmasHaoExpLimit:
		CHR.HasData(roleId, [newValue, roleId, role.GetRoleName(), ZoneName.ZoneName])
	
def SyncRoleOtherData(role, param):
	global ChristmasHaoIsOpen
	if not ChristmasHaoIsOpen: return
	
	#活动开启
	role.SendObj(ChristmasHaoOpen, True)
	
def RoleDayClear(role, param):
	#0点清理圣诞消费积分
	role.SetI32(EnumInt32.ChristmasConsumeExp, 0)
	
def OpenChristmasHao(callArgv, regparam):
	global ChristmasHaoIsOpen
	if ChristmasHaoIsOpen:
		print "GE_EXC, ChristmasHao is already open"
		return
	ChristmasHaoIsOpen = True
	
	#同步客户端活动开启
	cNetMessage.PackPyMsg(ChristmasHaoOpen, True)
	cRoleMgr.BroadMsg()
	
def CloseChristmasHao(callArgv, regparam):
	global ChristmasHaoIsOpen
	if not ChristmasHaoIsOpen:
		print "GE_EXC, ChristmasHao is already close"
		return
	ChristmasHaoIsOpen = False
	
	global ChristmasHaoControlRank, ChristmasHaoControlRank_Old, CHR
	ChristmasHaoControlRank, ChristmasHaoControlRank_Old = [], []
	
	#清理本地排行榜
	global CHR
	CHR.Clear()
	
	#同步客户端活动关闭
	cNetMessage.PackPyMsg(ChristmasHaoOpen, False)
	cRoleMgr.BroadMsg()
	
def RequestOpenPanel(role, param):
	'''
	请求打开面板
	@param role:
	@param param:
	'''
	global ChristmasHaoIsOpen
	if not ChristmasHaoIsOpen: return
	
	global CHR
	if not CHR.returnDB: return
	
	#打开面板的时候把跨服排名和本地排名一起发给客户端
	global ChristmasHaoControlRank
	role.SendObj(ChristmasHaoKuafuTodayRank, ChristmasHaoControlRank)
	
def RequestWatchTodayRank(role, param):
	'''
	请求查看今日排名
	@param role:
	@param param:
	'''
	global ChristmasHaoIsOpen
	if not ChristmasHaoIsOpen: return
	
	global CHR
	if not CHR.returnDB: return
	
	#今日跨服
	global ChristmasHaoControlRank
	role.SendObj(ChristmasHaoKuafuTodayRank, ChristmasHaoControlRank)
	
def RequestWatchYesterdayRank(role, param):
	'''
	请求查看昨日排名
	@param role:
	@param param:
	'''
	global ChristmasHaoIsOpen
	if not ChristmasHaoIsOpen: return
	
	global CHR
	if not CHR.returnDB: return
	
	#昨日跨服
	global ChristmasHaoControlRank_Old
	role.SendObj(ChristmasHaoKuafuYesterdayRank, ChristmasHaoControlRank_Old)
	
def RequestReward(role, param):
	'''
	请求领取今日充值奖励
	@param role:
	@param param:
	'''
	global ChristmasHaoIsOpen
	if not ChristmasHaoIsOpen: return
	
	global CHR
	if not CHR.returnDB: return
	
	if role.GetDI1(EnumDayInt1.ChristmasHaoFlag):
		return
	
	exp = role.GetI32(EnumInt32.ChristmasConsumeExp)
	
	if exp < EnumGameConfig.ChristmasHaoExpLimit:
		return
	
	cfg = ChristmasHaoConfig.ChristmasHaoExpReward_Dict.get(1)
	if not cfg:
		print 'GE_EXC, ChristmasHao can not find exp reward'
		return
	
	with ChristmasHaoExpReward_Log:
		role.SetDI1(EnumDayInt1.ChristmasHaoFlag, True)
		
		if role.PackageEmptySize() < len(cfg.rewardItems):
			#邮件
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.ChristmasHaoReward_Title, GlobalPrompt.ChristmasHaoReward_Sender, GlobalPrompt.ChristmasHaoReward_Content, items=cfg.rewardItems)
		else:
			tips = GlobalPrompt.Reward_Tips
			for item in cfg.rewardItems:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % item
			role.Msg(2, 0, tips)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#有钱就是任性充值排行榜
		CHR = ChristmasHaoRank()
		
		#注册服务器启动调用函数
		Init.InitCallBack.RegCallbackFunction(RequestRank)
		
		#请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicChristmasHaoRank, OnControlRequestRank)
		#发送跨服排行榜数据到逻辑进程(今天, 昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataChristmasHaoRankToLogic, OnControlUpdataRank)
		#发送跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataChristmasHaoRankToLogic_T, OnControlUpdataRank_T)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasHao_OpenPanel", "请求打开面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasHao_WatchToday", "请求查看今日排名"), RequestWatchTodayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasHao_WatchYesterday", "请求查看昨日排名"), RequestWatchYesterdayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasHao_Reward", "请求领取今日积分奖励"), RequestReward)
		
		cRoleDataMgr.SetInt32Fun(EnumInt32.ChristmasConsumeExp, AfterChangeChristmasConsume)
		
