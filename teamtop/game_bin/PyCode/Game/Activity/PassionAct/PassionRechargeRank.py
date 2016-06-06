#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.PassionAct.PassionRechargeRank")
#===============================================================================
# 激情活动 -- 充值排名
#===============================================================================
import cRoleMgr
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
from Game.Role.Data import EnumDayInt1
from Game.Activity.PassionAct import PassionRechargeRankConfig
import cDateTime

RANKTYPE_LOCAL = 2
RANKTYPE_KUAFU = 1

if "_HasLoad" not in dir():
	IsStart = False									#开启标志
	
	ENDTIME = 0										#活动结束时间戳
	
	PassionRechargeControlRank = []					#今日跨服排行榜数据
	PassionRechargeControlRank_Old = []				#昨日跨服排行榜数据
	
	#格式 : (IsStart, ENDTIME)
	PassionRecharge_ActiveStatus_S = AutoMessage.AllotMessage("PassionRecharge_ActiveStatus_S", "激情活动充值排行_同步活动状态")
	#今日跨服排行榜 -- [[激情活动充值, 角色ID, 角色名字, 服务器名字]] 已序
	PassionRecharge_KuafuTodayRank_S = AutoMessage.AllotMessage("PassionRecharge_KuafuTodayRank_S", "激情活动充值排行_同步今日跨服排行榜 ")
	#昨日跨服排行榜 -- [[激情活动充值, 角色ID, 角色名字, 服务器名字]] 已序
	PassionRecharge_KuafuYesterdayRank_S = AutoMessage.AllotMessage("PassionRecharge_KuafuYesterdayRank_S", "激情活动充值排行_同步昨日跨服排行榜")
	#今日本地排行榜 -- [[激情活动充值, 角色ID, 角色名字, 服务器名字]] 无序
	PassionRecharge_LocalTodayRank_S = AutoMessage.AllotMessage("PassionRecharge_LocalTodayRank_S", "激情活动充值排行_同步今日本地排行榜 ")
	#昨日本地排行榜 -- [[激情活动充值, 角色ID, 角色名字, 服务器名字]] 无序
	PassionRecharge_LocalYesterdayRank_S = AutoMessage.AllotMessage("PassionRecharge_LocalYesterdayRank_S", "激情活动充值排行_同步昨日本地排行榜")
	
	Tra_PassionRecharge_LocalRank = AutoLog.AutoTransaction("Tra_PassionRecharge_LocalRank", "激情活动充值排行_本地排行榜")
	Tra_PassionRecharge_Reward = AutoLog.AutoTransaction("Tra_PassionRecharge_Reward", "激情活动充值排行_安慰奖")
#===============================================================================
# 激情活动充值，角色ID，角色名字，服务器名字
#===============================================================================
class PassionRechargeRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 500						#本服排名10个,但是这里的个数要和跨服排行榜个数一样, 防止本服未上榜的跨服也不能上榜
	dead_time = (2038, 1, 1)
	
	needSync = False						#不需要同步给客户端 
	name = "Rank_PassionRechargeRank"
	
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
def OnStartPassionRecharge(*param):
	'''
	开启
	'''
	if not IsOldServer():
		return
	
	global IsStart
	if IsStart:
		print "GE_EXC,repeat open PassionRecharge"
		return 
	
	#保存配置那边触发带过来的活动结束时间戳
	global ENDTIME
	_,ENDTIME = param
	
	#先设置活动开启标志  此标志还代表了: 当前时间处于活动期间
	IsStart = True
	
	#触发活动开启
	TryStartActive()

def OnEndPassionRecharge(*param):
	'''
	结束
	'''
	global IsStart
	if not IsStart:
		print "GE_EXC,end PassionRecharge while not start"
	IsStart = False
	
	#清理缓存排行榜
	global PassionRechargeControlRank, PassionRechargeControlRank_Old
	PassionRechargeControlRank = []
	PassionRechargeControlRank_Old = []
	
	#这里不清理持久化数据， 持久化数据会在活动结束后一天的跨天时清理
	
	cNetMessage.PackPyMsg(PassionRecharge_ActiveStatus_S, (IsStart, ENDTIME))
	cRoleMgr.BroadMsg()

def TryStartActive(*param):
	'''
	尝试真正开启活动
	'''
	#当前是否处于活动期间
	global IsStart
	if not IsStart: return
	
	#今日榜单是否载回
	if not PRR.returnDB: return
	
	#向控制进程请求跨服排行榜数据
	ControlProxy.SendControlMsg(PyMessage.Control_GetPassionRechargeRank, (cProcess.ProcessID, GetLogicRank()))
	
	#活动真正开启了 广播同步
	cNetMessage.PackPyMsg(PassionRecharge_ActiveStatus_S, (IsStart, ENDTIME))
	cRoleMgr.BroadMsg()

def GetCloseValue(value, valueList):
	tmp_level = 0
	for i in valueList:
		if i > value:
			return tmp_level
		tmp_level = i
	else:
		return tmp_level
	
def OnGetConsolationReward(role, msg = None):
	'''
	激情活动充值排行榜_请求领取安慰奖
	'''
	global IsStart
	if not IsStart: return
	
	if role.GetLevel() < EnumGameConfig.PassionMinLevel:
		return
	if role.GetDI1(EnumDayInt1.PassionRechargeRank_IsReward):
		return
	if role.GetDayBuyUnbindRMB_Q() < PassionRechargeRankConfig.PassionRechargeRankMinRMB:
		return
	
	rewardCfg = PassionRechargeRankConfig.PassionRechargeRankReward_Dict.get(PassionRechargeRankConfig.PassionRechargeRankMinRMB)
	if not rewardCfg:
		print 'GE_EXC, PassionRechargeRank OnGetConsolationReward can not find rmb %s' % PassionRechargeRankConfig.PassionRechargeRankMinRMB
		return
	
	prompt = GlobalPrompt.PassionRechargeRank_Tips_Head
	with Tra_PassionRecharge_Reward:
		#已领取
		role.SetDI1(EnumDayInt1.PassionRechargeRank_IsReward, 1)
		
		#奖励获得
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	role.Msg(2, 0, prompt)
	
def OnViewTodayRank(role, msg):
	'''
	激情活动充值排行_请求查看今日排行榜数据
	@param msg: rankType 1-local 2-kuafu
	'''
	global IsStart
	if not IsStart: return
	
	global PRR
	if not PRR.returnDB: return
	
	rankType = msg
	if RANKTYPE_LOCAL == rankType:
		role.SendObj(PassionRecharge_LocalTodayRank_S, PRR.data.values())
	elif RANKTYPE_KUAFU == rankType:
		role.SendObj(PassionRecharge_KuafuTodayRank_S, PassionRechargeControlRank)
	else:
		pass

def OnViewYesterdayRank(role, msg):
	'''
	激情活动充值排行_请求查看昨日排行榜数据
	@param msg: rankType 1-local 2-kuafu
	'''
	global IsStart
	if not IsStart: return
	
	global PRR_List
	if not PRR_List.returnDB: return
	
	rankType = msg
	if RANKTYPE_LOCAL == rankType:
		role.SendObj(PassionRecharge_LocalYesterdayRank_S, PRR_List.data)
	elif RANKTYPE_KUAFU == rankType:
		role.SendObj(PassionRecharge_KuafuYesterdayRank_S, PassionRechargeControlRank_Old)
	else:
		pass

def GetLogicRank():
	'''
	返回当前今日榜数据
	'''
	return PRR.data.values()

#### 数据交互 start
def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服前30名数据 (需要返回服务器区域)
	@param sessionid:
	@param msg:
	'''
	if not PRR.returnDB:
		return
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetLogicRank()))

def OnControlUpdataRank(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global PassionRechargeControlRank, PassionRechargeControlRank_Old
	PassionRechargeControlRank, PassionRechargeControlRank_Old = msg
	
def OnControlUpdataRank_T(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	
	global PassionRechargeControlRank
	PassionRechargeControlRank = msg

#### 事件 start
def AfterNewDay():
	'''
	跨天处理 
	1.发奖
	2.本服今日榜  -> 本服昨日榜
	'''
	global IsStart, PRR, PRR_List
	if not IsStart:
		#持久化数据在活动结束的时候没有清理, 数据将会在会动结束后一天的跨天时清理
		#如果活动没有开启的话, 每日clear
		if PRR.returnDB:
			PRR.Clear()
		if PRR_List.returnDB:
			PRR_List.clear()
		return
	
	#跨服排行榜清理
	global PassionRechargeControlRank, PassionRechargeControlRank_Old
	PassionRechargeControlRank_Old = PassionRechargeControlRank
	PassionRechargeControlRank = []
	
	#记录今日排行榜
	with Tra_PassionRecharge_LocalRank:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.evePassionRechargeLocalRank, PRR.data)
		
		#保存今日排行榜
		PRR_List.data = PRR.data.values()
		PRR_List.HasChange()
	
	#排序:激情活动充值-->玩家ID
	localRankData = PRR.data.items()
	localRankData.sort(key = lambda x:(x[1][0], x[1][1], x[1][4]), reverse=True)
	
	tmpRankDict = {}	#{roleId:rank}
	tmpRank = 1			#初始排名
	maxRankLen = 10		#排行榜最大个数
	
	LRRG = PassionRechargeRankConfig.PassionRechargeRank_Dict.get
	for (roleId, rankData) in localRankData:
		if tmpRank > maxRankLen:
			#超过排行榜最大个数了
			continue
		
		#先拿到当前排名需要的配置
		cfg = LRRG(tmpRank)
		if not cfg:
			print 'GE_EXC, PassionRechargeMgr::AfterNewDay can not find rank %s cfg' % tmpRank
			continue
		
		while rankData[0] < cfg.needRMB:
			#如果当前的激情活动充值小于需要的激情活动充值, 排名往后加
			tmpRank += 1
			if tmpRank > maxRankLen:
				break
			#获取下一个排名的配置
			cfg = LRRG(tmpRank)
			if not cfg:
				print 'GE_EXC, PassionRechargeMgr::AfterNewHour can not find rank %s cfg' % tmpRank
				continue
		
		if tmpRank > maxRankLen:
			break
		
		if rankData[0] < cfg.needRMB:
			print 'GE_EXC, PassionRechargeMgr::AfterNewHour error'
			continue
		
		tmpRankDict[roleId] = tmpRank
		
		tmpRank += 1
		
	with Tra_PassionRecharge_LocalRank:
		for roleId, rank in tmpRankDict.iteritems():
			cfg =  LRRG(rank)
			if not cfg:
				print 'GE_EXC, WangZheLocalRank can not find rank %s in localRankRewardDict' % rank
				continue
			Mail.SendMail(roleId, GlobalPrompt.PassionRechargeRank_Local_Title, GlobalPrompt.PassionRechargeRank_Local_Sender, GlobalPrompt.PassionRechargeRank_Local_Content % (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), rank), items=cfg.rewardItems)
		
	#清理今日排行榜
	PRR.Clear()

def afterLoadPRR():
	'''
	昨日榜载回
	强制重新排序  配合合服数据合并之后乱序
	'''
	
	global PRR_List
	PRR_List.sort(key = lambda x:(x[0], x[1], x[4]), reverse = True)
	PRR_List.data = PRR_List[:10]
	PRR_List.changeFlag = True

def SyncRoleOtherData(role, param):
	'''
	上线同步活动状态
	'''
	global IsStart, ENDTIME
	if not IsStart:
		return
	
	role.SendObj(PassionRecharge_ActiveStatus_S, (IsStart, ENDTIME))
	
	#尝试入榜
	OnTryInPassionRecharge(role,None)

def OnTryInPassionRecharge(role, param):
	'''
	激情活动充值增加 触发尝试入榜逻辑
	等级提升后会尝试再次入榜
	'''
	global IsStart
	if not IsStart: return
	
	global PRR
	if not PRR.returnDB: return
	
	level = role.GetLevel()
	if level < EnumGameConfig.PassionMinLevel:
		return
	
	curRMB = role.GetDayBuyUnbindRMB_Q()
	if curRMB < PassionRechargeRankConfig.PassionRechargeRankMinRMB:
		return
	
	#入榜
	PRR.HasData(role.GetRoleID(), [curRMB, role.GetRoleID(), role.GetRoleName(), ZoneName.ZoneName, level])
	

def IsOldServer():
	'''
	充值排行新服老服区分
	'''
	#if WorldData.GetWorldKaiFuDay() > EnumGameConfig.PassionRechargeRank_NeedKaiFuDay:
	return True
	#else:
	#	return False

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsPL() or Environment.EnvIsTK()):
		#激情活动充值排行今日榜
		PRR = PassionRechargeRank()
		#激情活动充值排行昨日榜
		PRR_List = Contain.List("PRR_List", (2038, 1, 1), afterLoadPRR)
		
		#数据交互
		#1.请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicPassionRechargeRank, OnControlRequestRank)
		#2.发送跨服排行榜数据到逻辑进程(今天, 昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataPassionRechargeRankToLogic, OnControlUpdataRank)
		#3.发送跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataPassionRechargeRankToLogic_T, OnControlUpdataRank_T)
		
		#跨天
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		#玩家事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)	
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, OnTryInPassionRecharge)
		Event.RegEvent(Event.Eve_AfterLevelUp, OnTryInPassionRecharge)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionRecharge_OnGetConsolationReward", "激情活动充值排行_请求领取安慰奖"), OnGetConsolationReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionRecharge_OnViewTodayRank", "激情活动充值排行_请求查看今日排行榜数据"), OnViewTodayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("PassionRecharge_OnViewYesterdayRank", "激情活动充值排行_请求查看昨日排行榜数据"), OnViewYesterdayRank)

	
