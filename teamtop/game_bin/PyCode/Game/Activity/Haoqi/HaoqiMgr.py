#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Haoqi.HaoqiMgr")
#===============================================================================
# 豪气冲天逻辑模块
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
from Game.Persistence import Contain
from Game.GlobalData import ZoneName
from Game.Activity.Haoqi import HaoqiConfig
from Game.Role.Mail import Mail

if "_HasLoad" not in dir():
	HaoqiIsOpen = False					#豪气冲天开启标志
	
	HaoqiControlRank = []				#今日跨服排行榜数据
	HaoqiControlRank_Old = []			#昨日跨服排行榜数据
	
	HaoqiOpen = AutoMessage.AllotMessage("HaoqiOpen", "豪气冲天活动开启")
	HaoqiKuafuTodayRank = AutoMessage.AllotMessage("HaoqiKuafuTodayRank", "豪气冲天今日跨服排行榜")
	HaoqiKuafuYesterdayRank = AutoMessage.AllotMessage("HaoqiKuafuYesterdayRank", "豪气冲天昨日跨服排行榜")
	HaoqiLocalTodayRank = AutoMessage.AllotMessage("HaoqiLocalTodayRank", "豪气冲天今日本地排行榜")
	HaoqiLocalYesterdayRank = AutoMessage.AllotMessage("HaoqiLocalYesterdayRank", "豪气冲天昨日本地排行榜")
	HaoqiRMBData = AutoMessage.AllotMessage("HaoqiRMBData", "豪气冲天今日充值")
	
	HaoqiLocalRank_Log = AutoLog.AutoTransaction("HaoqiLocalRank_Log", "豪气冲天本地排行榜奖励")
	HaoqiFillReward_Log = AutoLog.AutoTransaction("HaoqiFillReward_Log", "豪气冲天今日充值奖励")
	
class HaoqiRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 10						#最大排行榜 10个
	dead_time = (2038, 1, 1)
	
	needSync = False						#这个排行榜需要同步客户端的, 查看消息在下面注册了, 可选查看今日和昨日排行榜
	
	name = "Rank_Haoqi"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[0] < v2[0]
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		self.changeFlag = True
	
def GetLogicRank():
	#返回本地排行榜
	return HR.data.values()

def RequestRank():
	#起服的时候向控制进程请求跨服排行榜数据
	global HaoqiIsOpen
	if not HaoqiIsOpen: return
	
	global HR
	if not HR.returnDB: return
	
	ControlProxy.SendControlMsg(PyMessage.Control_GetHaoqiRank, (cProcess.ProcessID, GetLogicRank()))
#===============================================================================
# 进程
#===============================================================================
def OnControlUpdataRank_T(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	global HaoqiControlRank
	HaoqiControlRank = msg

def OnControlUpdataRank(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global HaoqiControlRank, HaoqiControlRank_Old
	HaoqiControlRank, HaoqiControlRank_Old = msg
	
def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服前10名数据 
	@param sessionid:
	@param msg:
	'''
	global HR
	if not HR.returnDB: return
	
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetLogicRank()))
#===============================================================================
# 事件
#===============================================================================
def AfterNewHour():
	#0点结算奖励并清理本地排行榜
	#小概率0点充值玩家充值数据可能被清理掉
	global HaoqiIsOpen
	if not HaoqiIsOpen: return
	
	if cDateTime.Hour() != 0:
		return
	
	#跨服排行榜清理
	global HaoqiControlRank, HaoqiControlRank_Old
	HaoqiControlRank_Old = HaoqiControlRank
	HaoqiControlRank = []
	
	#本地排行榜
	global HQRMB_Dict
	HQRMB_Dict[1] = {}
	HQRMB_Dict[2] = HR.data.values()
	HQRMB_Dict.changeFlag = True
	
	localRankData = HR.data.items()
	localRankData.sort(key = lambda x:(x[1][0], x[1][1]), reverse=True)
	
	with HaoqiLocalRank_Log:
		for rank, rankData in enumerate(localRankData):
			cfg =  HaoqiConfig.HaoqiLocalRank_Dict.get(rank+1)
			if not cfg:
				print 'GE_EXC, haoqi can not find rank %s in HaoqiLocalRank_Dict' % (rank + 1)
				continue
			Mail.SendMail(rankData[0], GlobalPrompt.HaoqiLocal_Title, GlobalPrompt.HaoqiLocal_Sender, GlobalPrompt.HaoqiLocal_Content % (rank + 1), items=cfg.rewardItems, money=cfg.money, bindrmb=cfg.bindRMB)
	HR.Clear()
	
def AfterChangeUnbindRMB_Q(role, param):
	global HaoqiIsOpen
	if not HaoqiIsOpen: return
	
	global HQRMB_Dict
	if not HQRMB_Dict.returnDB: return
	
	oldValue, newValue = param
	if newValue <= oldValue:
		return
	fillRMB = newValue - oldValue
	
	roleId = role.GetRoleID()
	if roleId not in HQRMB_Dict[1]:
		HQRMB_Dict[1][roleId] = [fillRMB, 0]
		if fillRMB >= EnumGameConfig.HaoqiRMBLimit:
			HR.HasData(roleId, [fillRMB, roleId, role.GetRoleName(), ZoneName.ZoneName])
		role.SendObj(HaoqiRMBData, [fillRMB, 0])
	else:
		hqData = HQRMB_Dict[1][roleId]
		hqData[0] += fillRMB
		HQRMB_Dict[1][roleId] = hqData
		if hqData[0] >= EnumGameConfig.HaoqiRMBLimit:
			HR.HasData(roleId, [hqData[0], roleId, role.GetRoleName(), ZoneName.ZoneName])
		role.SendObj(HaoqiRMBData, hqData)
	HQRMB_Dict.changeFlag = True
	
def SyncRoleOtherData(role, param):
	global HaoqiIsOpen
	if not HaoqiIsOpen: return
	
	#活动开启
	role.SendObj(HaoqiOpen, True)
	
	global HQRMB_Dict
	if not HQRMB_Dict.returnDB: return
	
	roleId = role.GetRoleID()
	if roleId not in HQRMB_Dict[1]:
		role.SendObj(HaoqiRMBData, [0, 0])
		return
	#充值数据
	role.SendObj(HaoqiRMBData, HQRMB_Dict[1][roleId])
	
def OpenHaoqi(callArgv, regparam):
	global HaoqiIsOpen
	if HaoqiIsOpen:
		print "GE_EXC, Haoqi is already open"
		return
	HaoqiIsOpen = True
	
	#同步客户端活动开启
	cNetMessage.PackPyMsg(HaoqiOpen, True)
	cRoleMgr.BroadMsg()
	
def CloseHaoqi(callArgv, regparam):
	#这里会比配置的时间晚一分钟结束
	global HaoqiIsOpen
	if not HaoqiIsOpen:
		print "GE_EXC, Haoqi is already close"
		return
	HaoqiIsOpen = False
	
	global HaoqiControlRank, HaoqiControlRank_Old, HR
	HaoqiControlRank, HaoqiControlRank_Old = [], []
	
	#清理本地排行榜
	global HR
	HR.Clear()
	
	#清理本地昨日排行榜
	global HQRMB_Dict
	HQRMB_Dict.clear()
	
	#同步客户端活动关闭
	cNetMessage.PackPyMsg(HaoqiOpen, False)
	cRoleMgr.BroadMsg()
	
def RequestOpenPanel(role, param):
	'''
	请求打开面板
	@param role:
	@param param:
	'''
	global HaoqiIsOpen
	if not HaoqiIsOpen: return
	
	global HR
	if not HR.returnDB: return
	
	global HQRMB_Dict
	if not HQRMB_Dict.returnDB: return
	
	#打开面板的时候把跨服排名和本地排名一起发给客户端
	global HaoqiControlRank
	role.SendObj(HaoqiKuafuTodayRank, HaoqiControlRank)
	role.SendObj(HaoqiLocalTodayRank, HR.data.values())
	
	roleId = role.GetRoleID()
	if roleId not in HQRMB_Dict[1]:
		role.SendObj(HaoqiRMBData, [0, 0])
	else:
		role.SendObj(HaoqiRMBData, HQRMB_Dict[1][roleId])
	
def RequestWatchTodayRank(role, param):
	'''
	请求查看今日排名
	@param role:
	@param param:
	'''
	global HaoqiIsOpen
	if not HaoqiIsOpen: return
	
	global HR
	if not HR.returnDB: return
	
	global HQRMB_Dict
	if not HQRMB_Dict.returnDB: return
	
	if param == 2:
		#今日本地排行
		role.SendObj(HaoqiLocalTodayRank, HR.data.values())
	elif param == 1:
		#今日跨服
		global HaoqiControlRank
		role.SendObj(HaoqiKuafuTodayRank, HaoqiControlRank)
	
def RequestWatchYesterdayRank(role, param):
	'''
	请求查看昨日排名
	@param role:
	@param param:
	'''
	global HaoqiIsOpen
	if not HaoqiIsOpen: return
	
	global HR
	if not HR.returnDB: return
	
	global HQRMB_Dict
	if not HQRMB_Dict.returnDB: return
	
	if param == 2:
		#昨日本地排行
		role.SendObj(HaoqiLocalYesterdayRank, HQRMB_Dict[2])
	elif param == 1:
		#昨日跨服
		global HaoqiControlRank_Old
		role.SendObj(HaoqiKuafuYesterdayRank, HaoqiControlRank_Old)
	
def RequestReward(role, param):
	'''
	请求领取今日充值奖励
	@param role:
	@param param:
	'''
	global HaoqiIsOpen
	if not HaoqiIsOpen: return
	
	global HR
	if not HR.returnDB: return
	
	global HQRMB_Dict
	if not HQRMB_Dict.returnDB: return
	
	roleId = role.GetRoleID()
	if roleId not in HQRMB_Dict[1]:
		return
	
	hqData = HQRMB_Dict[1][roleId]
	if hqData[0] < EnumGameConfig.HaoqiRMBLimit or hqData[1]:
		return
	
	cfg = HaoqiConfig.HaoqiRMBReward_Dict.get(1)
	if not cfg:
		print 'GE_EXC, haoqi can not find fill rmb reward'
		return
	
	hqData[1] = 1
	HQRMB_Dict[1][roleId] = hqData
	HQRMB_Dict.changeFlag = True
	
	with HaoqiFillReward_Log:
		if role.PackageEmptySize() < len(cfg.rewardItems):
			#邮件
			Mail.SendMail(roleId, GlobalPrompt.HaoqiReward_Title, GlobalPrompt.HaoqiReward_Sender, GlobalPrompt.HaoqiReward_Content, items=cfg.rewardItems)
		else:
			tips = GlobalPrompt.Reward_Tips
			for item in cfg.rewardItems:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % item
			role.Msg(2, 0, tips)
	
	role.SendObj(HaoqiRMBData, hqData)
	
def afterLoad():
	global HQRMB_Dict
	if not HQRMB_Dict:
		#初始化
		HQRMB_Dict[1] = {}		#今日充值数据
		HQRMB_Dict[2] = []		#昨日的排行榜数据
	elif len(HQRMB_Dict[2]) >= 10:
		#和服了 ? 要排一次序
		HQRMB_Dict[2].sort(key = lambda x:(x[0], x[1]), reverse = True)
		HQRMB_Dict[2] = HQRMB_Dict[2][:10]
	HQRMB_Dict.changeFlag = True
	
if "_HasLoad" not in dir():
	if (Environment.HasLogic and not Environment.IsCross) or Environment.HasWeb:
		#豪气冲天充值排行榜
		HR = HaoqiRank()
		
		#充值记录 -- 这里因为每次充值后要尝试进入排行榜, 所以不用数组了
		#{1:今日排行榜{}, 2:昨日排行榜[]}
		HQRMB_Dict = Contain.Dict("HQRMB_Dict", (2038, 1, 1), afterLoad)
		
		#注册服务器启动调用函数
		Init.InitCallBack.RegCallbackFunction(RequestRank)
		
		#请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicHaoqiRank, OnControlRequestRank)
		#发送跨服排行榜数据到逻辑进程(今天, 昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataHaoqiRankToLogic, OnControlUpdataRank)
		#发送跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataHaoqiRankToLogic_T, OnControlUpdataRank_T)
		
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Haoqi_OpenPanel", "请求打开面板"), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Haoqi_WatchToday", "请求查看今日排名"), RequestWatchTodayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Haoqi_WatchYesterday", "请求查看昨日排名"), RequestWatchYesterdayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Haoqi_Reward", "请求领取今日充值奖励"), RequestReward)
		
		
		