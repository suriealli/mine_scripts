#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionConsumeRank")
#===============================================================================
# 激情活动 -- 消费排名
#===============================================================================
import cRoleMgr
import cDateTime
import cNetMessage
import cProcess
import cComplexServer
import Environment
from Common.Message import AutoMessage, PyMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.Control import ControlProxy
from Game.Role.Mail import Mail
from Game.Role import Rank, Event
from Game.GlobalData import ZoneName
from Game.Persistence import Contain
from Game.Role.Data import EnumDayInt1, EnumInt32
from Game.Activity.PassionAct import PassionConsumeRankConfig


if "_HasLoad" not in dir():
	IsStart = False									#开启标志
	ENDTIME = 0										#活动结束时间戳
	
	RANKTYPE_LOCAL = 2
	RANKTYPE_KUAFU = 1
	
	PassionConsumeControlRank = []					#今日跨服排行榜数据
	PassionConsumeControlRank_Old = []				#昨日跨服排行榜数据
	
	#格式 : (IsStart, ENDTIME)
	PassionConsume_ActiveStatus_S = AutoMessage.AllotMessage("PassionConsume_ActiveStatus_S", "激情活动消费排行_同步活动状态")
	#今日跨服排行榜 -- [[激情活动消费, 角色ID, 角色名字, 服务器名字]] 已序
	PassionConsume_KuafuTodayRank_S = AutoMessage.AllotMessage("PassionConsume_KuafuTodayRank_S", "激情活动消费排行_同步今日跨服排行榜 ")
	#昨日跨服排行榜 -- [[激情活动消费, 角色ID, 角色名字, 服务器名字]] 已序
	PassionConsume_KuafuYesterdayRank_S = AutoMessage.AllotMessage("PassionConsume_KuafuYesterdayRank_S", "激情活动消费排行_同步昨日跨服排行榜")
	#今日本地排行榜 -- [[激情活动消费, 角色ID, 角色名字, 服务器名字]] 无序
	PassionConsume_LocalTodayRank_S = AutoMessage.AllotMessage("PassionConsume_LocalTodayRank_S", "激情活动消费排行_同步今日本地排行榜 ")
	#昨日本地排行榜 -- [[激情活动消费, 角色ID, 角色名字, 服务器名字]] 无序
	PassionConsume_LocalYesterdayRank_S = AutoMessage.AllotMessage("PassionConsume_LocalYesterdayRank_S", "激情活动消费排行_同步昨日本地排行榜")
	
	Tra_PassionConsume_LocalRank = AutoLog.AutoTransaction("Tra_PassionConsume_LocalRank", "激情活动消费排行_本地排行榜")
	Tra_PassionConsume_Reward = AutoLog.AutoTransaction("Tra_PassionConsume_Reward", "激情活动消费排行_安慰奖")
#===============================================================================
# 激情活动消费，角色ID，角色名字，服务器名字
#===============================================================================
class PassionConsumeRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 500						#本服排名10个,但是这里的个数要和跨服排行榜个数一样, 防止本服未上榜的跨服也不能上榜
	dead_time = (2038, 1, 1)
	
	needSync = False						#不需要同步给客户端 
	name = "Rank_PassionConsumeRank"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return (v1[0], v1[1], v1[4]) < (v2[0], v2[1], v2[4])
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		self.changeFlag = True
	
	def AfterLoadFun(self):
		Rank.SmallRoleRank.AfterLoadFun(self)
		TryStartActive()

#### 活动控制 start
def OnStartPassionConsume(*param):
	'''
	开启
	'''
	global IsStart
	if IsStart:
		print "GE_EXC,repeat open PassionConsume"
		return 
	
	#保存配置那边触发带过来的活动结束时间戳
	global ENDTIME
	_, ENDTIME = param
	
	#先设置活动开启标志  此标志还代表了: 当前时间处于活动期间
	IsStart = True
	
	#触发活动开启
	TryStartActive()

def OnEndPassionConsume(*param):
	'''
	结束
	'''
	global IsStart
	if not IsStart:
		print "GE_EXC,end PassionConsume while not start"
	IsStart = False
	
	#清理缓存排行榜
	global PassionConsumeControlRank, PassionConsumeControlRank_Old
	PassionConsumeControlRank = []
	PassionConsumeControlRank_Old = []
	
	#这里不清理持久化数据， 持久化数据会在活动结束后一天的跨天时清理
	
	cNetMessage.PackPyMsg(PassionConsume_ActiveStatus_S, (IsStart, ENDTIME))
	cRoleMgr.BroadMsg()

def TryStartActive(*param):
	'''
	尝试真正开启活动
	'''
	#当前是否处于活动期间
	global IsStart
	if not IsStart: return
	
	#今日榜单是否载回
	if not PCR.returnDB: return
	
	#向控制进程请求跨服排行榜数据
	ControlProxy.SendControlMsg(PyMessage.Control_GetPassionConsumeRank, (cProcess.ProcessID, GetLogicRank()))
	
	#活动真正开启了 广播同步
	cNetMessage.PackPyMsg(PassionConsume_ActiveStatus_S, (IsStart, ENDTIME))
	cRoleMgr.BroadMsg()

def GetCloseValue(value, valueList):
	tmp_level = 0
	for i in valueList:
		if i > value:
			return tmp_level
		tmp_level = i
	else:
		return tmp_level
	
def OnGetConsolationReward(role, msg=None):
	'''
	激情活动消费排行榜_请求领取安慰奖
	'''
	global IsStart
	if not IsStart: return
	
	if role.GetLevel() < EnumGameConfig.PassionMinLevel:
		return
	
	if role.GetDI1(EnumDayInt1.PassionConsumeRank_IsReward):
		return
	
	if role.GetI32(EnumInt32.DayConsumeUnbindRMB_Q) < PassionConsumeRankConfig.PassionConsumeRankMinRMB:
		return
	
	rewardCfg = PassionConsumeRankConfig.PassionConsumeRankReward_Dict.get(PassionConsumeRankConfig.PassionConsumeRankMinRMB)
	if not rewardCfg:
		print 'GE_EXC, PassionConsumeRank OnGetConsolationReward can not find rmb %s' % PassionConsumeRankConfig.PassionConsumeRankMinRMB
		return
	
	prompt = GlobalPrompt.PassionConsumeRank_Tips_Head
	with Tra_PassionConsume_Reward:
		#已领取
		role.SetDI1(EnumDayInt1.PassionConsumeRank_IsReward, 1)
		
		#奖励获得
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	role.Msg(2, 0, prompt)
	
def OnViewTodayRank(role, msg):
	'''
	激情活动消费排行_请求查看今日排行榜数据
	@param msg: rankType 1-local 2-kuafu
	'''
	global IsStart
	if not IsStart: return
	
	global PCR
	if not PCR.returnDB: return
	
	rankType = msg
	if RANKTYPE_LOCAL == rankType:
		role.SendObj(PassionConsume_LocalTodayRank_S, PCR.data.values())
	elif RANKTYPE_KUAFU == rankType:
		role.SendObj(PassionConsume_KuafuTodayRank_S, PassionConsumeControlRank)
	else:
		pass

def OnViewYesterdayRank(role, msg):
	'''
	激情活动消费排行_请求查看昨日排行榜数据
	@param msg: rankType 1-local 2-kuafu
	'''
	global IsStart
	if not IsStart: return
	
	global PCR_List
	if not PCR_List.returnDB: return
	
	rankType = msg
	if RANKTYPE_LOCAL == rankType:
		role.SendObj(PassionConsume_LocalYesterdayRank_S, PCR_List.data)
	elif RANKTYPE_KUAFU == rankType:
		role.SendObj(PassionConsume_KuafuYesterdayRank_S, PassionConsumeControlRank_Old)
	else:
		pass

def GetLogicRank():
	'''
	返回当前今日榜数据
	'''
	return PCR.data.values()

#### 数据交互 start
def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服前30名数据 (需要返回服务器区域)
	@param sessionid:
	@param msg:
	'''
	if not PCR.returnDB:
		return
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetLogicRank()))

def OnControlUpdataRank(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global PassionConsumeControlRank, PassionConsumeControlRank_Old
	PassionConsumeControlRank, PassionConsumeControlRank_Old = msg
	
def OnControlUpdataRank_T(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	
	global PassionConsumeControlRank
	PassionConsumeControlRank = msg

#### 事件 start
def AfterNewDay():
	'''
	跨天处理 
	1.发奖
	2.本服今日榜  -> 本服昨日榜
	'''
	global IsStart, PCR, PCR_List
	if not IsStart:
		#持久化数据在活动结束的时候没有清理, 数据将会在会动结束后一天的跨天时清理
		#如果活动没有开启的话, 每日clear
		if PCR.returnDB:
			PCR.Clear()
		if PCR_List.returnDB:
			PCR_List.clear()
		return
	
	#跨服排行榜清理
	global PassionConsumeControlRank, PassionConsumeControlRank_Old
	PassionConsumeControlRank_Old = PassionConsumeControlRank
	PassionConsumeControlRank = []
	
	#记录今日排行榜
	with Tra_PassionConsume_LocalRank:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.evePassionConsumeLocalRank, PCR.data)
		
		#保存今日排行榜
		PCR_List.data = PCR.data.values()
		PCR_List.HasChange()
	
	#排序:激情活动消费-->玩家ID
	localRankData = PCR.data.items()
	localRankData.sort(key=lambda x:(x[1][0], x[1][1], x[1][4]), reverse=True)
	
	tmpRankDict = {}	#{roleId:rank}
	tmpRank = 1			#初始排名
	maxRankLen = 10		#排行榜最大个数
	
	LRRG = PassionConsumeRankConfig.PassionConsumeRank_Dict.get
	for (roleId, rankData) in localRankData:
		if tmpRank > maxRankLen:
			#超过排行榜最大个数了
			continue
		
		#先拿到当前排名需要的配置
		cfg = LRRG(tmpRank)
		if not cfg:
			print 'GE_EXC, PassionConsumeMgr::AfterNewDay can not find rank %s cfg' % tmpRank
			continue
		
		while rankData[0] < cfg.needRMB:
			#如果当前的激情活动消费小于需要的激情活动消费, 排名往后加
			tmpRank += 1
			if tmpRank > maxRankLen:
				break
			#获取下一个排名的配置
			cfg = LRRG(tmpRank)
			if not cfg:
				print 'GE_EXC, PassionConsumeMgr::AfterNewHour can not find rank %s cfg' % tmpRank
				continue
		
		if tmpRank > maxRankLen:
			break
		
		if rankData[0] < cfg.needRMB:
			print 'GE_EXC, PassionConsumeMgr::AfterNewHour error'
			continue
		
		tmpRankDict[roleId] = tmpRank
		
		tmpRank += 1
		
	with Tra_PassionConsume_LocalRank:
		for roleId, rank in tmpRankDict.iteritems():
			cfg = LRRG(rank)
			if not cfg:
				print 'GE_EXC, WangZheLocalRank can not find rank %s in localRankRewardDict' % rank
				continue
			Mail.SendMail(roleId, GlobalPrompt.PassionConsumeRank_Local_Title, GlobalPrompt.PassionConsumeRank_Local_Sender, GlobalPrompt.PassionConsumeRank_Local_Content % (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), rank), items=cfg.rewardItems)
		
	#清理今日排行榜
	PCR.Clear()

def afterLoadPCR():
	'''
	昨日榜载回
	强制重新排序  配合合服数据合并之后乱序
	'''
	
	global PCR_List
	PCR_List.sort(key=lambda x:(x[0], x[1], x[4]), reverse=True)
	PCR_List.data = PCR_List[:10]
	PCR_List.HasChange()

def SyncRoleOtherData(role, param):
	'''
	上线同步活动状态
	'''
	global IsStart, ENDTIME
	if not IsStart:
		return
	
	#尝试入榜
	OnTryInPassionConsume(role, None)
	role.SendObj(PassionConsume_ActiveStatus_S, (IsStart, ENDTIME))
	

def OnTryInPassionConsume(role, param):
	'''
	激情活动消费增加 触发尝试入榜逻辑
	等级提升后会尝试再次入榜
	'''
	global IsStart
	if not IsStart: return
	
	global PCR
	if not PCR.returnDB: return
	
	level = role.GetLevel()
	if level < EnumGameConfig.PassionMinLevel:
		return
	
	consumeUnbindRMB_Q = role.GetI32(EnumInt32.DayConsumeUnbindRMB_Q)
	if consumeUnbindRMB_Q < PassionConsumeRankConfig.PassionConsumeRankMinRMB:
		return
	#入榜
	PCR.HasData(role.GetRoleID(), [consumeUnbindRMB_Q, role.GetRoleID(), role.GetRoleName(), ZoneName.ZoneName, level])


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#激情活动消费排行今日榜
		PCR = PassionConsumeRank()
		#激情活动消费排行昨日榜
		PCR_List = Contain.List("PCR_List", (2038, 1, 1), afterLoadPCR)
		
		#数据交互
		#1.请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicPassionConsumeRank, OnControlRequestRank)
		#2.发送跨服排行榜数据到逻辑进程(今天, 昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataPassionConsumeRankToLogic, OnControlUpdataRank)
		#3.发送跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataPassionConsumeRankToLogic_T, OnControlUpdataRank_T)
		
		#跨天
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		#玩家事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)	
		Event.RegEvent(Event.Eve_AfterChangeDayConsumeUnbindRMB_Q, OnTryInPassionConsume)
		Event.RegEvent(Event.Eve_AfterLevelUp, OnTryInPassionConsume)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionConsume_OnGetConsolationReward", "激情活动消费排行_请求领取安慰奖"), OnGetConsolationReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionConsume_OnViewTodayRank", "激情活动消费排行_请求查看今日排行榜数据"), OnViewTodayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionConsume_OnViewYesterdayRank", "激情活动消费排行_请求查看昨日排行榜数据"), OnViewYesterdayRank)

	
