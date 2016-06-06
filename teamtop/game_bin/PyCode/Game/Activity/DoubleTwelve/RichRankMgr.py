#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleTwelve.RichRankMgr")
#===============================================================================
# 双十二跨服富豪榜管理
#===============================================================================
import cComplexServer
import cProcess
import cRoleMgr
import Environment
from Common.Message import PyMessage, AutoMessage
from ComplexServer import Init
from ComplexServer.Plug.Control import ControlProxy
from Game.GlobalData import ZoneName
from Game.Persistence import Contain
from Game.Role import Rank, Event, KuaFu
from Game.Activity.DoubleTwelve import DoubleTwelveConfig
from Game.Activity.Award import AwardMgr
from Common.Other import EnumAward
from Game.Activity.Title import Title

if "_HasLoad" not in dir():
	IS_START = False			#活动是否开启
	IS_RR_CLEAR = False			#是否清除本地富豪榜数据
	IS_P_DICT_CLEAR = False		#是否清除持久化字典数据
	
	IN_RANK_LIMIT_RMB = 10000	#入榜限制神石
	
	RICH_RANK = []				#富豪榜数据
	
	Rich_Rank_Show_Panel = AutoMessage.AllotMessage("Rich_Rank_Show_Panel", "通知客户端显示富豪榜面板")
	Rich_Rank_Total_Consume_RMB = AutoMessage.AllotMessage("Rich_Rank_Total_Consume_RMB", "通知客户端显示富豪榜累计消耗神石")

class RichRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 50						#最大排行榜 50个
	dead_time = (2038, 1, 1)
	needSync = False
	name = "Rank_DoubleTwelveRich"
	
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
		
		global IS_RR_CLEAR
		if IS_RR_CLEAR == True:
			IS_RR_CLEAR = False
			self.Clear()
		
		TryUpdate()
		
def TryUpdate():
	'''
	排行榜数据载回来后尝试更新富豪榜
	'''
	if IS_START is False:
		#活动没有开启
		return
	
	#向控制进程请求跨服排行榜数据
	ControlProxy.SendControlMsg(PyMessage.Control_RequestControlRichRank, (cProcess.ProcessID, GetLogicRank()))

def AfterLoad():
	global IS_P_DICT_CLEAR
	global RICH_RANK_CONSUME_RMB_DICT
	if IS_P_DICT_CLEAR == True:
		IS_P_DICT_CLEAR = False
		RICH_RANK_CONSUME_RMB_DICT.clear()

def GetLogicRank():
	#返回本地排行榜
	return RR.data.values()

def ShowRichRankPanel(role):
	role.SendObj(Rich_Rank_Show_Panel, RICH_RANK)
	
def RichRankReward():
	for idx, data in enumerate(RICH_RANK):
		rank = idx + 1
		roleId = data[1]
		#是否本服玩家
		if not KuaFu.IsLocalRoleByRoleID(roleId):
			continue
		
		rewardConfig = DoubleTwelveConfig.RICH_RANK_REWARD.get(rank)
		if not rewardConfig:
			print "GE_EXC, can't find rewardConfig in RichRankReward(%s)" % (roleId)
			continue
		
		#玩法奖励
		AwardMgr.SetAward(roleId, EnumAward.DTRichRankAward, 
						money = rewardConfig.rewardMoney, 
						bindRMB = rewardConfig.rewardRMB, 
						itemList = rewardConfig.rewardItem, 
						clientDescParam = (rank, ))
		
		#称号奖励
		if rewardConfig.rewardTitleId:
			Title.AddTitle(roleId, rewardConfig.rewardTitleId)

#===============================================================================
# tick
#===============================================================================
def OpenRichRank(callArgv, regparam):
	global IS_START
	if IS_START:
		print "GE_EXC, RichRank is already open"
		return
	IS_START = True
	
	global IS_RR_CLEAR
	global IS_P_DICT_CLEAR
	IS_RR_CLEAR = True
	IS_P_DICT_CLEAR = True
	
	#活动开启清空所有富豪榜数据
	global RICH_RANK_CONSUME_RMB_DICT
	if IS_P_DICT_CLEAR == True:
		if RICH_RANK_CONSUME_RMB_DICT.returnDB:
			IS_P_DICT_CLEAR = False
			RICH_RANK_CONSUME_RMB_DICT.clear()
	if IS_RR_CLEAR == True:
		if RR.returnDB:
			IS_RR_CLEAR = False
			RR.Clear()
	
def CloseRichRank(callArgv, regparam):
	#这里会比配置的时间晚一分钟结束
	global IS_START
	if not IS_START:
		print "GE_EXC, RichRank is already close"
		return
	IS_START = False

#===============================================================================
# 服务器启动
#===============================================================================
def ServerUp():
	#起服的时候向控制进程请求跨服排行榜数据
	if IS_START is False:
		return
	if not RR.returnDB:
		return
	ControlProxy.SendControlMsg(PyMessage.Control_RequestControlRichRank, (cProcess.ProcessID, GetLogicRank()))

#===============================================================================
# 事件
#===============================================================================
def AfterChangeUnbindRMB_Q(role, param):
	'''
	神石改变
	@param role:
	@param param:
	'''
	#活动未开启
	if IS_START is False:
		return
	
	oldValue, newValue = param
	#充值
	if newValue >= oldValue:
		return
	
	#消耗RMB
	costRMB = oldValue - newValue
	
	IncRichRankRMB(role, costRMB)
	
def AfterChangeUnbindRMB_S(role, param):
	'''
	神石改变
	@param role:
	@param oldValue:
	@param newValue:
	'''
	#活动未开启
	if IS_START is False:
		return
	
	oldValue, newValue = param
	#充值
	if newValue >= oldValue:
		return
	
	#消耗RMB
	costRMB = oldValue - newValue
	
	IncRichRankRMB(role, costRMB)
	
def IncRichRankRMB(role, rmb):
	global RICH_RANK_CONSUME_RMB_DICT
	roleId = role.GetRoleID()
	if roleId not in RICH_RANK_CONSUME_RMB_DICT:
		RICH_RANK_CONSUME_RMB_DICT[roleId] = rmb
	else:
		RICH_RANK_CONSUME_RMB_DICT[roleId] += rmb
	
	#入榜限制
	totalConsumeRMB = RICH_RANK_CONSUME_RMB_DICT[roleId]
	if totalConsumeRMB >= IN_RANK_LIMIT_RMB:
		#入榜
		RR.HasData(roleId, [totalConsumeRMB, roleId, role.GetRoleName(), role.GetLevel(), ZoneName.ZoneName])
	
	#同步客户端富豪榜累计消耗神石
	role.SendObj(Rich_Rank_Total_Consume_RMB, totalConsumeRMB)
	
def OnSyncRoleOtherData(role, param):
	'''
	角色登陆同步其它数据
	@param role:
	@param param:
	'''
	roleId = role.GetRoleID()
	
	totalConsumeRMB = 0
	if roleId in RICH_RANK_CONSUME_RMB_DICT:
		totalConsumeRMB = RICH_RANK_CONSUME_RMB_DICT[roleId]
		
	#同步客户端富豪榜累计消耗神石
	role.SendObj(Rich_Rank_Total_Consume_RMB, totalConsumeRMB)
	
#===============================================================================
# 控制进程请求
#===============================================================================
def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服富豪榜榜
	@param sessionid:
	@param msg:
	'''
	if not RR.returnDB:
		return
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetLogicRank()))
	
def OnControlUpdateRank(sessionid, msg):
	'''
	#控制进程更新富豪榜数据过来
	@param sessionid:
	@param msg:
	'''
	global RICH_RANK
	RICH_RANK = msg
	
def OnControlRequestRankReward(sessionid, msg):
	'''
	#控制进程请求获取本服富豪榜榜
	@param sessionid:
	@param msg:
	'''
	global RICH_RANK
	RICH_RANK = msg
	
	RichRankReward()
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestRichRankOpenPanel(role, msg):
	'''
	客户端请求富豪榜打开面板
	@param role:
	@param msg:
	'''
	ShowRichRankPanel(role)
	
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		RR = RichRank()		#本地富豪榜
		
		#累计消耗神石记录 
		#{roleId: rmb}
		RICH_RANK_CONSUME_RMB_DICT = Contain.Dict("RICH_RANK_CONSUME_RMB_DICT", (2038, 1, 1), AfterLoad)
		
		#注册服务器启动调用函数
		Init.InitCallBack.RegCallbackFunction(ServerUp)
		
		#事件
		#改变神石事件
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		Event.RegEvent(Event.AfterChangeUnbindRMB_S, AfterChangeUnbindRMB_S)
		#角色登陆同步其它数据
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		#请求逻辑进程的双十二富豪榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicRichRank, OnControlRequestRank)
		#更新逻辑进程双十二富豪榜
		cComplexServer.RegDistribute(PyMessage.Control_UpdateLogicRichRank, OnControlUpdateRank)
		#请求逻辑进程的双十二富豪榜颁发奖励
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicRichRankReward, OnControlRequestRankReward)
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Rich_Rank_Open_Panel", "客户端请求富豪榜打开面板"), RequestRichRankOpenPanel)
		
		
		