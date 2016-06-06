#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WangZheGongCe.WangZheRankMgr")
#===============================================================================
# 王者公测积分排行榜Mgr
#===============================================================================
import cRoleMgr
import cNetMessage
import cProcess
import cComplexServer
import Environment
from Common.Message import AutoMessage, PyMessage
from Common.Other import EnumSysData, GlobalPrompt
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.Control import ControlProxy
from Game.Role.Mail import Mail
from Game.Role import Rank, Event
from Game.SysData import WorldData
from Game.GlobalData import ZoneName
from Game.Persistence import Contain
from Game.Role.Data import EnumDayInt1
from Game.Activity.WangZheGongCe import WangZheRankConfig

RANKTYPE_LOCAL = 1
RANKTYPE_KUAFU = 2
if "_HasLoad" not in dir():
	IS_START = False					#开启标志
	ENDTIME = 0							#活动结束时间戳
	
	WangZheRankControlRank = []					#今日跨服排行榜数据
	WangZheRankControlRank_Old = []				#昨日跨服排行榜数据
	
	#格式 : (IS_START, ENDTIME)
	WangZheRank_ActiveStatus_S = AutoMessage.AllotMessage("WangZheRank_ActiveStatus_S", "王者积分排行_同步活动状态")
	#今日跨服排行榜 -- [[王者积分, 角色ID, 角色名字, 服务器名字]]
	WangZheRank_KuafuTodayRank_S = AutoMessage.AllotMessage("WangZheRank_KuafuTodayRank_S", "王者积分排行_同步今日跨服排行榜 ")
	#昨日跨服排行榜 -- [[王者积分, 角色ID, 角色名字, 服务器名字]]
	WangZheRank_KuafuYesterdayRank_S = AutoMessage.AllotMessage("WangZheRank_KuafuYesterdayRank_S", "王者积分排行_同步昨日跨服排行榜")
	#今日本地排行榜 -- {roleId:[王者积分, 角色ID, 角色名字, 服务器名字]}
	WangZheRank_LocalTodayRank_S = AutoMessage.AllotMessage("WangZheRank_LocalTodayRank_S", "王者积分排行_同步今日本地排行榜 ")
	#昨日本地排行榜 -- {roleId:[王者积分, 角色ID, 角色名字, 服务器名字]}
	WangZheRank_LocalYesterdayRank_S = AutoMessage.AllotMessage("WangZheRank_LocalYesterdayRank_S", "王者积分排行_同步昨日本地排行榜")
	
	Tra_WangZheRank_LocalRank = AutoLog.AutoTransaction("Tra_WangZheRank_LocalRank", "王者积分排行_本地排行榜")
	Tra_WangZheRank_ConsolationReward = AutoLog.AutoTransaction("Tra_WangZheRank_ConsolationReward", "王者积分排行_安慰奖")
	
#===============================================================================
# 王者积分，角色ID，角色名字，服务器名字
#===============================================================================
class WangZheJiFenRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 500						#最大排行榜 500个 
	dead_time = (2038, 1, 1)
	
	needSync = False						#不需要同步给客户端 
	name = "Rank_WangZheJiFen"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return (v1[0], v1[1],v1[4]) < (v2[0], v2[1],v2[4])
	
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
def OnStartWangZheRank(*param):
	'''
	魅力派对_开启
	'''
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open WangZheRank"
		return 
	
	#保存配置那边触发带过来的活动结束时间戳
	global ENDTIME
	_,ENDTIME = param
	#先设置活动开启标志  此标志还代表了: 当前时间处于活动期间
	IS_START = True
	
	#触发活动开启
	TryStartActive()

def OnEndWangZheRank(*param):
	'''
	魅力派对_结束
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,end WangZheRank while not start"
	IS_START = False
	
	cNetMessage.PackPyMsg(WangZheRank_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()

def TryStartActive(*param):
	'''
	尝试真正开启活动
	'''
	#当前是否处于活动期间
	if not IS_START:
		return
	
	#世界数据是否载回
	if not WorldData.WD.returnDB:
		return
	
	#今日榜单是否载回
	if not WZJFR.returnDB:
		return
	
	#没有制定服务器类型(活动期间活动开启之后新开的服务器) 有类型了不能重算(活动期间重启了)
	curServerType = GetServerType()
	if not curServerType:
		SetServerType(CalculateServerType())
	
	#向控制进程请求跨服排行榜数据
	ControlProxy.SendControlMsg(PyMessage.Control_GetWangZheRank, (cProcess.ProcessID, GetServerType(), GetLogicRank()))
	
	#活动真正开启了 广播同步
	cNetMessage.PackPyMsg(WangZheRank_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()

#### 客户端请求 start 
def OnGetConsolationReward(role, msg = None):
	'''
	王者积分排行_请求领取安慰奖
	'''
	if not IS_START:
		return
	
	if role.GetDI1(EnumDayInt1.WangZheRank_IsReward):
		return
	
	curServerType = GetServerType()
	rewardCfg = WangZheRankConfig.WangZheRank_ConsolationReward_Dict.get(curServerType)
	if role.GetDayWangZheJiFen() < rewardCfg.needJiFen:
		return
	
	prompt = GlobalPrompt.WangZheRank_Tips_Head
	with Tra_WangZheRank_ConsolationReward:
		#已领取
		role.SetDI1(EnumDayInt1.WangZheRank_IsReward, 1)
		#奖励获得
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.WangZheRank_Tips_Item % (coding, cnt)
	
	role.Msg(2, 0, prompt)

def OnViewTodayRank(role, msg):
	'''
	王者积分排行_请求查看今日排行榜数据
	@param msg: rankType 1-local 2-kuafu
	'''
	if not IS_START:
		return
	
	global WZJFR
	if not WZJFR.returnDB: return
	
	rankType = msg
	if RANKTYPE_LOCAL == rankType:
		role.SendObj(WangZheRank_LocalTodayRank_S, WZJFR.data.values())
	elif RANKTYPE_KUAFU == rankType:
		role.SendObj(WangZheRank_KuafuTodayRank_S, WangZheRankControlRank)
	else:
		pass


def OnViewYesterdayRank(role, msg):
	'''
	王者积分排行_请求查看昨日排行榜数据
	@param msg: rankType 1-local 2-kuafu
	'''
	if not IS_START:
		return
	
	global YWZJFR_List
	if not YWZJFR_List.returnDB: return
	
	rankType = msg
	if RANKTYPE_LOCAL == rankType:
		role.SendObj(WangZheRank_LocalYesterdayRank_S, YWZJFR_List.data)
	elif RANKTYPE_KUAFU == rankType:
		role.SendObj(WangZheRank_KuafuYesterdayRank_S, WangZheRankControlRank_Old)
	else:
		pass

#### Helper start
def GetServerType():
	'''
	返回当前指定的服务器类型
	'''
	return WorldData.WD[EnumSysData.WangZheRankServerType]

def SetServerType(serverType):
	'''
	指定服务器类型
	'''
	WorldData.SetWangZheRankServerType(serverType)
	
	#分配了服务器类型 广播活动开始(当且仅当 活动开启 各种依赖数据到位之后 能成功设置)
	cNetMessage.PackPyMsg(WangZheRank_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()
	
def GetLogicRank():
	'''
	返回当前今日榜数据
	'''
	return WZJFR.data.values()

def CalculateServerType():
	'''
	根据当前开服天数和配置区段 计算服务器类型
	'''
	kaifuDay = WorldData.GetWorldKaiFuDay()
	for serverType, cfg in WangZheRankConfig.WangZheRank_ServerType_Dict.iteritems():
		if cfg.kaifuDay[0] <= kaifuDay <= cfg.kaifuDay[1]:
			return serverType
		
	#找不到的话返回最大的服务器类型
	return WangZheRankConfig.WangZheRank_MaxServerType
	
#### 数据交互 start
def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服前30名数据 (需要返回服务器区域)
	@param sessionid:
	@param msg:
	'''
	if not WorldData.WD.returnDB:
		return
	if not WZJFR.returnDB:
		return
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetServerType(), GetLogicRank()))

def OnControlUpdataRank(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global WangZheRankControlRank, WangZheRankControlRank_Old
	WangZheRankControlRank, WangZheRankControlRank_Old = msg
	
def OnControlUpdataRank_T(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	
	global WangZheRankControlRank
	WangZheRankControlRank = msg

#### 事件 start
def AfterNewDay():
	'''
	跨天处理 
	1.发奖
	2.本服今日榜  -> 本服昨日榜
	'''
	#活动结束tick已经延迟了60秒 此处触发若IS_START为False 必然活动已经正常结束了 不再处理
	if not IS_START:
		return
	
	#跨服排行榜清理
	global WangZheRankControlRank, WangZheRankControlRank_Old
	WangZheRankControlRank_Old = WangZheRankControlRank
	WangZheRankControlRank = []
	
	#记录今日排行榜
	global WZJFR
	global YWZJFR_List
	with Tra_WangZheRank_LocalRank:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveWangZheRankLocalRank, WZJFR.data)
		#保存今日排行榜
		YWZJFR_List.data = WZJFR.data.values()
		YWZJFR_List.HasChange()
	
	#排序:王者积分-->玩家ID
	localRankData = WZJFR.data.items()
	localRankData.sort(key = lambda x:(x[1][0], x[1][1]), reverse=True)
	
	tmpRankDict = {}	#{roleId:rank}
	tmpRank = 1			#初始排名
	maxRankLen = 10		#排行榜最大个数
	
	localRankRewardDict = WangZheRankConfig.WangZheRank_LocalRankReward_Dict.get(GetServerType())
	LRRG = localRankRewardDict.get
	for (roleId, rankData) in localRankData:
		if tmpRank > maxRankLen:
			#超过排行榜最大个数了
			continue
		
		#先拿到当前排名需要的积分配置
		cfg = LRRG(tmpRank)
		if not cfg:
			print 'GE_EXC, WangZheRankMgr::AfterNewDay can not find rank %s cfg' % tmpRank
			continue
		
		while rankData[0] < cfg.needJiFen:
			#如果当前的王者积分小于需要的王者积分, 排名往后加
			tmpRank += 1
			if tmpRank > maxRankLen:
				break
			#获取下一个排名的配置
			cfg = LRRG(tmpRank)
			if not cfg:
				print 'GE_EXC, WangZheRankMgr::AfterNewHour can not find rank %s cfg' % tmpRank
				continue
		
		if tmpRank > maxRankLen:
			break
		
		if rankData[0] < cfg.needJiFen:
			print 'GE_EXC, WangZheRankMgr::AfterNewHour error'
			continue
		
		tmpRankDict[roleId] = tmpRank
		
		tmpRank += 1
		
	with Tra_WangZheRank_LocalRank:
		for roleId, rank in tmpRankDict.iteritems():
			cfg =  localRankRewardDict.get(rank)
			if not cfg:
				print 'GE_EXC, WangZheLocalRank can not find rank %s in localRankRewardDict with ServerType(%s)' % (rank, GetServerType())
				continue
			Mail.SendMail(roleId, GlobalPrompt.WangZheRank_Local_Title, GlobalPrompt.WangZheRank_Local_Sender, GlobalPrompt.WangZheRank_Local_Content % rank, items=cfg.rewardItems)
		
	#清理今日排行榜
	WZJFR.Clear()

def afterLoadYWZJFR():
	'''
	昨日榜载回
	强制重新排序  配合合服数据合并之后乱序
	'''
	
	global YWZJFR_List
	YWZJFR_List.sort(key = lambda x:(x[0], x[1]), reverse = True)
	YWZJFR_List.data = YWZJFR_List[:10]
	YWZJFR_List.changeFlag = True

def SyncRoleOtherData(role, param):
	'''
	上线同步活动状态
	'''
	if not IS_START:
		return
	
	role.SendObj(WangZheRank_ActiveStatus_S, (IS_START, ENDTIME))
	
	#尝试入榜
	OnTryInWangZheRank(role,None)

def OnTryInWangZheRank(role, param):
	'''
	王者积分增加 触发尝试入榜逻辑
	'''
	if not IS_START:
		return
	
	global WZJFR
	if not WZJFR.returnDB:
		return
	
	curJiFen = role.GetDayWangZheJiFen()
	minJiFen = WangZheRankConfig.WangZheRank_ConsolationReward_Dict.get(GetServerType()).minJiFen
	if curJiFen < minJiFen:
		return
	
	#入榜
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	roleLevel = role.GetLevel()
	WZJFR.HasData(roleId, [curJiFen, roleId, roleName, ZoneName.ZoneName, roleLevel])

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU()):
		#王者积分排行今日榜
		WZJFR = WangZheJiFenRank()
		#王者积分排行昨日榜
		YWZJFR_List = Contain.List("YWZJFR_List", (2038, 1, 1), afterLoadYWZJFR)
		
		#数据交互
		#1.请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicWangZheRank, OnControlRequestRank)
		#2.发送跨服排行榜数据到逻辑进程(今天, 昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataWangZheRankToLogic, OnControlUpdataRank)
		#3.发送跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataWangZheRankToLogic_T, OnControlUpdataRank_T)
		
		#三触发 :: 1.载回今日榜WZJFR 2.载回世界数据  3.活动开启 
		Event.RegEvent(Event.Eve_AfterLoadWorldData, TryStartActive)
		
		#跨天
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		#玩家事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)	
		Event.RegEvent(Event.Eve_AfterChangeDayBuyUnbindRMB_Q, OnTryInWangZheRank)
		Event.RegEvent(Event.Eve_AfterLevelUp, OnTryInWangZheRank)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheRank_OnGetConsolationReward", "王者积分排行_请求领取安慰奖"), OnGetConsolationReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheRank_OnViewTodayRank", "王者积分排行_请求查看今日排行榜数据"), OnViewTodayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WangZheRank_OnViewYesterdayRank", "王者积分排行_请求查看昨日排行榜数据"), OnViewYesterdayRank)
