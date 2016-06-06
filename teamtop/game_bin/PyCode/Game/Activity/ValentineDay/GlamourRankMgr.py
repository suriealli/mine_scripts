#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.GlamourRankMgr")
#===============================================================================
# 魅力排行 Mgr
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
from Game.SysData import WorldData, WorldDataNotSync
from Game.GlobalData import ZoneName
from Game.Persistence import Contain
from Game.Role.Data import EnumDayInt1, EnumInt32
from Game.Activity.ValentineDay import GlamourRankConfig, ValentineVersionMgr

RANKTYPE_LOCAL = 1
RANKTYPE_KUAFU = 2
if "_HasLoad" not in dir():
	IS_START = False					#开启标志
	ENDTIME = 0							#活动结束时间戳
	
	GlamourRankControlRank = []					#今日跨服排行榜数据
	GlamourRankControlRank_Old = []				#昨日跨服排行榜数据
	
	#格式 : (IS_START, ENDTIME)
	GlamourRank_ActiveStatus_S = AutoMessage.AllotMessage("GlamourRank_ActiveStatus_S", "魅力排行_同步活动状态")
	#今日跨服排行榜 -- [[魅力值, 角色ID, 角色名字, 服务器名字]]
	GlamourRank_KuafuTodayRank_S = AutoMessage.AllotMessage("GlamourRank_KuafuTodayRank_S", "魅力排行_同步今日跨服排行榜 ")
	#昨日跨服排行榜 -- [[魅力值, 角色ID, 角色名字, 服务器名字]]
	GlamourRank_KuafuYesterdayRank_S = AutoMessage.AllotMessage("GlamourRank_KuafuYesterdayRank_S", "魅力排行_同步昨日跨服排行榜")
	#今日本地排行榜 -- {roleId:[魅力值, 角色ID, 角色名字, 服务器名字]}
	GlamourRank_LocalTodayRank_S = AutoMessage.AllotMessage("GlamourRank_LocalTodayRank_S", "魅力排行_同步今日本地排行榜 ")
	#昨日本地排行榜 -- {roleId:[魅力值, 角色ID, 角色名字, 服务器名字]}
	GlamourRank_LocalYesterdayRank_S = AutoMessage.AllotMessage("GlamourRank_LocalYesterdayRank_S", "魅力排行_同步今日本地排行榜")
	
	Tra_GlamourRank_LocalRank = AutoLog.AutoTransaction("Tra_GlamourRank_LocalRank", "魅力排行_本地排行榜")
	Tra_GlamourRank_ConsolationReward = AutoLog.AutoTransaction("Tra_GlamourRank_ConsolationReward", "魅力排行_安慰奖")
	
#===============================================================================
# 魅力值，角色ID，角色名字，服务器名字
#===============================================================================
class GlamourScoreRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 100						#最大排行榜 10个
	dead_time = (2038, 1, 1)
	
	needSync = False						#不需要同步给客户端 
	name = "Rank_GlamourScore"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return (v1[0], v1[1]) < (v2[0], v2[1])
	
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
def OnStartGlamourRank(*param):
	'''
	魅力派对_开启
	'''
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open GlamourRank"
		return 
	
	#保存配置那边触发带过来的活动结束时间戳
	global ENDTIME
	_,ENDTIME = param
	#先设置活动开启标志  此标志还代表了: 当前时间处于活动期间
	IS_START = True
	
	#触发活动开启
	TryStartActive()

def OnEndGlamourRank(*param):
	'''
	魅力派对_结束
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,end GlamourRank while not start"
	IS_START = False
	
	cNetMessage.PackPyMsg(GlamourRank_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()

def TryStartActive(*param):
	'''
	尝试真正开启活动
	'''
	#当前是否处于活动期间
	if not IS_START:
#		print "GE_EXC, TryStartActive not IS_START"
		return
	
	#世界数据是否载回
	if not WorldData.WD.returnDB:
#		print "GE_EXC, TryStartActive not WorldData.WD.returnDB"
		return
	
	#今日榜单是否载回
	if not GSR.returnDB:
#		print "GE_EXC, TryStartActive not GSR.returnDB"
		return
	
	#没有制定服务器类型(活动期间活动开启之后新开的服务器) 有类型了不能重算(活动期间重启了)
	curServerType = GetServerType()
	if not curServerType:
		SetServerType(CalculateServerType())
	
	#向控制进程请求跨服排行榜数据
	ControlProxy.SendControlMsg(PyMessage.Control_GetGlamourRank, (cProcess.ProcessID, GetServerType(), GetLogicRank()))
	
	#活动真正开启了 广播同步
	cNetMessage.PackPyMsg(GlamourRank_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()

#	print "GE_EXC, TryStartActive start Succeed!", IS_START, ENDTIME, GetServerType()
#### 客户端请求 start 
def OnGetConsolationReward(role, msg = None):
	'''
	魅力排行_请求领取安慰奖
	'''
	if not IS_START:
		return
	
	if role.GetDI1(EnumDayInt1.GlamourRank_IsReward):
		return
	
	curServerType = GetServerType()
	rewardCfg = GlamourRankConfig.GlamourRank_ConsolationReward_Dict.get(curServerType)
	if role.GetI32(EnumInt32.DayGlamourExp) < rewardCfg.needGlamour:
		return
	
	prompt = GlobalPrompt.GlamourRank_Tips_Head
	with Tra_GlamourRank_ConsolationReward:
		#已领取
		role.SetDI1(EnumDayInt1.GlamourRank_IsReward, 1)
		#奖励获得
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.GlamourRank_Tips_Item % (coding, cnt)
	
	role.Msg(2, 0, prompt)

def OnViewTodayRank(role, msg):
	'''
	魅力排行_请求查看今日排行榜数据
	@param msg: rankType 1-local 2-kuafu
	'''
	if not IS_START:
		return
	
	global GSR
	if not GSR.returnDB: return
	
	rankType = msg
	if RANKTYPE_LOCAL == rankType:
		role.SendObj(GlamourRank_LocalTodayRank_S, GSR.data.values())
#		print "GE_EXC, OnViewTodayRank,RANKTYPE_LOCAL::",GSR.data.values()
	elif RANKTYPE_KUAFU == rankType:
		role.SendObj(GlamourRank_KuafuTodayRank_S, GlamourRankControlRank)
#		print "GE_EXC, OnViewTodayRank,RANKTYPE_KUAFU::",GlamourRankControlRank
	else:
		pass


def OnViewYesterdayRank(role, msg):
	'''
	魅力排行_请求查看昨日排行榜数据
	@param msg: rankType 1-local 2-kuafu
	'''
	if not IS_START:
		return
	
	global GSR
	if not GSR.returnDB: return
	
	rankType = msg
	if RANKTYPE_LOCAL == rankType:
		role.SendObj(GlamourRank_LocalYesterdayRank_S, YGSR_List.data)
	elif RANKTYPE_KUAFU == rankType:
		role.SendObj(GlamourRank_KuafuYesterdayRank_S, GlamourRankControlRank_Old)
	else:
		pass

#### Helper start
def GetServerType():
	'''
	返回当前指定的服务器类型
	'''
	return WorldData.WD[EnumSysData.GlamourRankServerType]

def SetServerType(serverType):
	'''
	指定服务器类型
	'''
	if serverType not in GlamourRankConfig.GlamourRank_ServerType_Dict:
		print "GE_EXC, SetServerType::error serverType(%s) not in Config" % serverType
		serverType = GlamourRankConfig.GlamourRank_MaxServerType
		return
	
	WorldData.SetGlamourRankServerType(serverType)
	
	#分配了服务器类型 广播活动开始(当且仅当 活动开启 各种依赖数据到位之后 能成功设置)
	cNetMessage.PackPyMsg(GlamourRank_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()
	
	#活动开启 触发更新活动版本号
	UpdateVersion()
	
def GetLogicRank():
	'''
	返回当前今日榜数据
	'''
	return GSR.data.values()

def CalculateServerType():
	'''
	根据当前开服天数和配置区段 计算服务器类型
	'''
	kaifuDay = WorldData.GetWorldKaiFuDay()
	for serverType, cfg in GlamourRankConfig.GlamourRank_ServerType_Dict.iteritems():
		if cfg.kaifuDay[0] <= kaifuDay <= cfg.kaifuDay[1]:
			return serverType
		
	#找不到的话返回最大的服务器类型
#	print "GE_EXC, CalculateServerType can not find kaifuDay (%s) in GlamourRank_ServerType_Dict" % kaifuDay
	return GlamourRankConfig.GlamourRank_MaxServerType
	
#### 数据交互 start
def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服前30名数据 (需要返回服务器区域)
	@param sessionid:
	@param msg:
	'''
	if not WorldData.WD.returnDB:
		return
	if not GSR.returnDB:
		return
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetServerType(), GetLogicRank()))

def OnControlUpdataRank(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global GlamourRankControlRank, GlamourRankControlRank_Old
	GlamourRankControlRank, GlamourRankControlRank_Old = msg
	
def OnControlUpdataRank_T(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	
	global GlamourRankControlRank
	GlamourRankControlRank = msg

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
	global GlamourRankControlRank, GlamourRankControlRank_Old
	GlamourRankControlRank_Old = GlamourRankControlRank
	GlamourRankControlRank = []
	
	#记录今日排行榜
	global GSR
	global YGSR_List
	with Tra_GlamourRank_LocalRank:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveGlamourRankLocalRank, GSR.data)
		#保存今日排行榜
		YGSR_List.data = GSR.data.values()
		YGSR_List.HasChange()
	
	#排序:消费-->玩家ID
	localRankData = GSR.data.items()
	localRankData.sort(key = lambda x:(x[1][0], x[1][1]), reverse=True)
	
	tmpRankDict = {}	#{roleId:rank}
	tmpRank = 1			#初始排名
	maxRankLen = 10		#排行榜最大个数
	
	localRankRewardDict = GlamourRankConfig.GlamourRank_LocalRankReward_Dict.get(GetServerType())
	LRRG = localRankRewardDict.get
	for (roleId, rankData) in localRankData:
		if tmpRank > maxRankLen:
			#超过排行榜最大个数了
			continue
		
		#先拿到当前排名需要的积分配置
		cfg = LRRG(tmpRank)
		if not cfg:
			print 'GE_EXC, GlamourRankMgr::AfterNewDay can not find rank %s cfg' % tmpRank
			continue
		
		while rankData[0] < cfg.needGalmour:
			#如果当前的魅力值小于需要的魅力值, 排名往后加
			tmpRank += 1
			if tmpRank > maxRankLen:
				break
			#获取下一个排名的配置
			cfg = LRRG(tmpRank)
			if not cfg:
				print 'GE_EXC, GlamourRankMgr::AfterNewHour can not find rank %s cfg' % tmpRank
				continue
		
		if tmpRank > maxRankLen:
			break
		
		if rankData[0] < cfg.needGalmour:
			print 'GE_EXC, GlamourRankMgr::AfterNewHour error'
			continue
		
		tmpRankDict[roleId] = tmpRank
		
		tmpRank += 1
		
	with Tra_GlamourRank_LocalRank:
		for roleId, rank in tmpRankDict.iteritems():
			cfg =  localRankRewardDict.get(rank)
			if not cfg:
				print 'GE_EXC, GlamourLocalRank can not find rank %s in localRankRewardDict with ServerType(%s)' % (rank, GetServerType())
				continue
			Mail.SendMail(roleId, GlobalPrompt.GlamourRank_Local_Title, GlobalPrompt.GlamourRank_Local_Sender, GlobalPrompt.GlamourRank_Local_Content % rank, items=cfg.rewardItems)
		
	#清理今日排行榜
	GSR.Clear()

def afterLoadYGR():
	'''
	昨日榜载回
	强制重新排序  配合合服数据合并之后乱序
	'''
	
	global YGSR_List
	YGSR_List.sort(key = lambda x:(x[0], x[1]), reverse = True)
	YGSR_List.data = YGSR_List[:10]
	YGSR_List.changeFlag = True

	#升级了活动版本号 对应处理数据
	UpdateVersion()
	
def UpdateVersion(calParam = None, regParam = None):
	'''
	升级魅力排行活动版本号 
	'''
	global YGSR_List
	if not YGSR_List.returnDB:
#		print "GE_EXC, glamourRank:: not returnDB"
		return
	
	if not WorldDataNotSync.WorldDataPrivate.returnDB:
#		print "GE_EXC, glamourRank:: not WorldDataPrivate.returnDB"
		return
	
	if not IS_START:
#		print "GE_EXC, glamourRank:: not IS_START"
		return
	
	curVersion = ValentineVersionMgr.ValentineVersion
	dateVersion = WorldDataNotSync.GetGlamourRankVersion()
	if curVersion == dateVersion:
		return
	
	if curVersion < dateVersion:
		print "GE_EXC, GlamourRankMgr：：UpdateVersion curVersion(%s) < dateVersion (%s)" % (curVersion, dateVersion)
		return 
	
	with ValentineVersionMgr.Tra_Valentine_UpdateVersion:
		#日志记录下清除掉的数据 
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveUpdateGlamourRankVersion, (curVersion, dateVersion, YGSR_List.data ))
		WorldDataNotSync.SetGlamourRankVersion(curVersion)
		YGSR_List.clear()

def SyncRoleOtherData(role, param):
	'''
	上线同步活动状态
	'''
	if not IS_START:
		return
	
	role.SendObj(GlamourRank_ActiveStatus_S, (IS_START, ENDTIME))

def OnTryInGlamourRank(role, param):
	'''
	魅力值增加 触发尝试入榜逻辑
	'''
	if not IS_START:
		return
	
	global GSR
	if not GSR.returnDB:
		return
	
	curGlamour = role.GetI32(EnumInt32.DayGlamourExp)
	minGlamour = GlamourRankConfig.GlamourRank_ConsolationReward_Dict.get(GetServerType()).minGlamour
	if curGlamour < minGlamour:
		return
	
	#入榜
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	GSR.HasData(roleId, [curGlamour, roleId, roleName, ZoneName.ZoneName])

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#魅力排行今日榜
		GSR = GlamourScoreRank()
		#魅力排行昨日榜
		YGSR_List = Contain.List("YGSR_List", (2038, 1, 1), afterLoadYGR)
		
		#数据交互
		#1.请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicGlamourRank, OnControlRequestRank)
		#2.发送跨服排行榜数据到逻辑进程(今天, 昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataGlamourRankToLogic, OnControlUpdataRank)
		#3.发送跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataGlamourRankToLogic_T, OnControlUpdataRank_T)
		
		#三触发 :: 1.载回今日榜GSR 2.载回世界数据  3.活动开启 
		Event.RegEvent(Event.Eve_AfterLoadWorldData, TryStartActive)
		#活动版本号三触发
		Event.RegEvent(Event.Eve_AfterLoadWorldDataNotSync, UpdateVersion)
		
		#跨天
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		#玩家事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)	
		Event.RegEvent(Event.Eve_TryInGlamorRank, OnTryInGlamourRank)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GlamourRank_OnGetConsolationReward", "魅力排行_请求领取安慰奖"), OnGetConsolationReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GlamourRank_OnViewTodayRank", "魅力排行_请求查看今日排行榜数据"), OnViewTodayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GlamourRank_OnViewYesterdayRank", "魅力排行_请求查看昨日排行榜数据"), OnViewYesterdayRank)
