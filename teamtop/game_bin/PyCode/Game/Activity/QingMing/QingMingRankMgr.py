#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QingMing.QingMingRankMgr")
#===============================================================================
# 注释
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
from Game.Activity.QingMing import QingMingRankConfig

RANKTYPE_LOCAL = 1
RANKTYPE_KUAFU = 2
if "_HasLoad" not in dir():
	IS_START = False					#开启标志
	ENDTIME = 0							#活动结束时间戳
	
	QingMingRankControlRank = []					#今日跨服排行榜数据
	QingMingRankControlRank_Old = []				#昨日跨服排行榜数据
	
	#格式 : (IS_START, ENDTIME)
	QingMingRank_ActiveStatus_S = AutoMessage.AllotMessage("QingMingRank_ActiveStatus_S", "清明消费排行_同步活动状态")
	#今日跨服排行榜 -- [[魅力值, 角色ID, 角色名字, 服务器名字]]
	QingMingRank_KuafuTodayRank_S = AutoMessage.AllotMessage("QingMingRank_KuafuTodayRank_S", "清明消费排行_同步今日跨服排行榜 ")
	#昨日跨服排行榜 -- [[魅力值, 角色ID, 角色名字, 服务器名字]]
	QingMingRank_KuafuYesterdayRank_S = AutoMessage.AllotMessage("QingMingRank_KuafuYesterdayRank_S", "清明消费排行_同步昨日跨服排行榜")
	#今日本地排行榜 -- {roleId:[魅力值, 角色ID, 角色名字, 服务器名字]}
	QingMingRank_LocalTodayRank_S = AutoMessage.AllotMessage("QingMingRank_LocalTodayRank_S", "清明消费排行_同步今日本地排行榜 ")
	#昨日本地排行榜 -- {roleId:[魅力值, 角色ID, 角色名字, 服务器名字]}
	QingMingRank_LocalYesterdayRank_S = AutoMessage.AllotMessage("QingMingRank_LocalYesterdayRank_S", "清明消费排行_同步今日本地排行榜")
	
	Tra_QingMingRank_LocalRank = AutoLog.AutoTransaction("Tra_QingMingRank_LocalRank", "清明消费排行_本地排行榜")
	Tra_QingMingRank_ConsolationReward = AutoLog.AutoTransaction("Tra_QingMingRank_ConsolationReward", "清明消费排行_安慰奖")
	
#===============================================================================
# 魅力值，角色ID，角色名字，服务器名字
#===============================================================================
class QingMingScoreRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 100						#最大排行榜 10个
	dead_time = (2038, 1, 1)
	
	needSync = False						#不需要同步给客户端 
	name = "Rank_QingMingScore"
	
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
def OnStartQingMingRank(*param):
	'''
	魅力派对_开启
	'''
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open QingMingRank"
		return 
	
	#保存配置那边触发带过来的活动结束时间戳
	global ENDTIME
	_,ENDTIME = param
	#先设置活动开启标志  此标志还代表了: 当前时间处于活动期间
	IS_START = True
	
	#触发活动开启
	TryStartActive()

def OnEndQingMingRank(*param):
	'''
	魅力派对_结束
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,end QingMingRank while not start"
	IS_START = False
	
	cNetMessage.PackPyMsg(QingMingRank_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()

def TryStartActive(*param):
	'''
	尝试真正开启活动
	'''
	#当前是否处于活动期间
	if not IS_START:
#		print "GE_EXC, not IS_START"
		return
	
	#世界数据是否载回
	if not WorldData.WD.returnDB:
#		print "GE_EXC, not WorldData.WD.returnDB"
		return
	
	#今日榜单是否载回
	if not QMSR.returnDB:
#		print "GE_EXC, not QMSR.returnDB"
		return
	
	#没有制定服务器类型(活动期间活动开启之后新开的服务器) 有类型了不能重算(活动期间重启了)
	curServerType = GetServerType()
	if not curServerType:
		SetServerType(CalculateServerType())
	
	#向控制进程请求跨服排行榜数据
	ControlProxy.SendControlMsg(PyMessage.Control_GetQingMingRank, (cProcess.ProcessID, GetServerType(), GetLogicRank()))
	
	#活动真正开启了 广播同步
	cNetMessage.PackPyMsg(QingMingRank_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()

#### 客户端请求 start 
def OnGetConsolationReward(role, msg = None):
	'''
	清明消费排行_请求领取安慰奖
	'''
	if not IS_START:
		return
	
	if role.GetDI1(EnumDayInt1.QingMingRank_IsReward):
		return
	
	curServerType = GetServerType()
	rewardCfg = QingMingRankConfig.QingMingRank_ConsolationReward_Dict.get(curServerType)
	if role.GetDayConsumeUnbindRMB() < rewardCfg.needValue:
		return
	
	prompt = GlobalPrompt.QingMingRank_Tips_Head
	with Tra_QingMingRank_ConsolationReward:
		#已领取
		role.SetDI1(EnumDayInt1.QingMingRank_IsReward, 1)
		#奖励获得
		for coding, cnt in rewardCfg.rewardItems:
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.QingMingRank_Tips_Item % (coding, cnt)
	
	role.Msg(2, 0, prompt)

def OnViewTodayRank(role, msg):
	'''
	清明消费排行_请求查看今日排行榜数据
	@param msg: rankType 1-local 2-kuafu
	'''
	if not IS_START:
		return
	
	global QMSR
	if not QMSR.returnDB: return
	
	rankType = msg
	if RANKTYPE_LOCAL == rankType:
		role.SendObj(QingMingRank_LocalTodayRank_S, QMSR.data.values())
	elif RANKTYPE_KUAFU == rankType:
		role.SendObj(QingMingRank_KuafuTodayRank_S, QingMingRankControlRank)
	else:
		pass


def OnViewYesterdayRank(role, msg):
	'''
	清明消费排行_请求查看昨日排行榜数据
	@param msg: rankType 1-local 2-kuafu
	'''
	if not IS_START:
		return
	
	global QMSR
	if not QMSR.returnDB: return
	
	rankType = msg
	if RANKTYPE_LOCAL == rankType:
		role.SendObj(QingMingRank_LocalYesterdayRank_S, YQMCR_List.data)
	elif RANKTYPE_KUAFU == rankType:
		role.SendObj(QingMingRank_KuafuYesterdayRank_S, QingMingRankControlRank_Old)
	else:
		pass

#### Helper start
def GetServerType():
	'''
	返回当前指定的服务器类型
	'''
	return WorldData.WD[EnumSysData.QingMingRankServerType]

def SetServerType(serverType):
	'''
	指定服务器类型
	'''
	if serverType not in QingMingRankConfig.QingMingRank_ServerType_Dict:
		print "GE_EXC, SetServerType::error serverType(%s) not in Config" % serverType
		serverType = QingMingRankConfig.QingMingRank_MaxServerType
		return
	
	WorldData.SetQingMingRankServerType(serverType)
	
	#分配了服务器类型 广播活动开始(当且仅当 活动开启 各种依赖数据到位之后 能成功设置)
	cNetMessage.PackPyMsg(QingMingRank_ActiveStatus_S, (IS_START, ENDTIME))
	cRoleMgr.BroadMsg()
	
def GetLogicRank():
	'''
	返回当前今日榜数据
	'''
	return QMSR.data.values()

def CalculateServerType():
	'''
	根据当前开服天数和配置区段 计算服务器类型
	'''
	kaifuDay = WorldData.GetWorldKaiFuDay()
	for serverType, cfg in QingMingRankConfig.QingMingRank_ServerType_Dict.iteritems():
		if cfg.kaifuDay[0] <= kaifuDay <= cfg.kaifuDay[1]:
			return serverType
		
	#找不到的话返回最大的服务器类型
	return QingMingRankConfig.QingMingRank_MaxServerType
	
#### 数据交互 start
def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服前30名数据 (需要返回服务器区域)
	@param sessionid:
	@param msg:
	'''
	if not WorldData.WD.returnDB:
		return
	if not QMSR.returnDB:
		return
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetServerType(), GetLogicRank()))

def OnControlUpdataRank(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global QingMingRankControlRank, QingMingRankControlRank_Old
	QingMingRankControlRank, QingMingRankControlRank_Old = msg
	
def OnControlUpdataRank_T(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	
	global QingMingRankControlRank
	QingMingRankControlRank = msg

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
	global QingMingRankControlRank, QingMingRankControlRank_Old
	QingMingRankControlRank_Old = QingMingRankControlRank
	QingMingRankControlRank = []
	
	#记录今日排行榜
	global QMSR
	global YQMCR_List
	with Tra_QingMingRank_LocalRank:
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveQingMingRankLocalRank, QMSR.data)
		#保存今日排行榜
		YQMCR_List.data = QMSR.data.values()
		YQMCR_List.HasChange()
	
	#排序:消费-->玩家ID
	localRankData = QMSR.data.items()
	localRankData.sort(key = lambda x:(x[1][0], x[1][1]), reverse=True)
	
	tmpRankDict = {}	#{roleId:rank}
	tmpRank = 1			#初始排名
	maxRankLen = 10		#排行榜最大个数
	
	localRankRewardDict = QingMingRankConfig.QingMingRank_LocalRankReward_Dict.get(GetServerType())
	LRRG = localRankRewardDict.get
	for (roleId, rankData) in localRankData:
		if tmpRank > maxRankLen:
			#超过排行榜最大个数了
			continue
		
		#先拿到当前排名需要的积分配置
		cfg = LRRG(tmpRank)
		if not cfg:
			print 'GE_EXC, QingMingRankMgr::AfterNewDay can not find rank %s cfg' % tmpRank
			continue
		
		while rankData[0] < cfg.needValue:
			#如果当前的魅力值小于需要的魅力值, 排名往后加
			tmpRank += 1
			if tmpRank > maxRankLen:
				break
			#获取下一个排名的配置
			cfg = LRRG(tmpRank)
			if not cfg:
				print 'GE_EXC, QingMingRankMgr::AfterNewHour can not find rank %s cfg' % tmpRank
				continue
		
		if tmpRank > maxRankLen:
			break
		
		if rankData[0] < cfg.needValue:
			print 'GE_EXC, QingMingRankMgr::AfterNewHour error'
			continue
		
		tmpRankDict[roleId] = tmpRank
		
		tmpRank += 1
		
	with Tra_QingMingRank_LocalRank:
		for roleId, rank in tmpRankDict.iteritems():
			cfg =  localRankRewardDict.get(rank)
			if not cfg:
				print 'GE_EXC, QingMingLocalRank can not find rank %s in localRankRewardDict with ServerType(%s)' % (rank, GetServerType())
				continue
			Mail.SendMail(roleId, GlobalPrompt.QingMingRank_Local_Title, GlobalPrompt.QingMingRank_Local_Sender, GlobalPrompt.QingMingRank_Local_Content % rank, items=cfg.rewardItems)
		
	#清理今日排行榜
	QMSR.Clear()

def afterLoadQMCR():
	'''
	昨日榜载回
	强制重新排序  配合合服数据合并之后乱序
	'''
	
	global YQMCR_List
	YQMCR_List.sort(key = lambda x:(x[0], x[1]), reverse = True)
	YQMCR_List.data = YQMCR_List[:10]
	YQMCR_List.changeFlag = True

def SyncRoleOtherData(role, param):
	'''
	上线同步活动状态
	'''
	if not IS_START:
		return
	
	role.SendObj(QingMingRank_ActiveStatus_S, (IS_START, ENDTIME))
	
	#登录尝试入榜
	OnTryInQingMingRank(role, None)

def OnTryInQingMingRank(role, param):
	'''
	魅力值增加 触发尝试入榜逻辑
	'''
	if not IS_START:
		return
	
	global QMSR
	if not QMSR.returnDB:
		return
	
	curValue = role.GetDayConsumeUnbindRMB()
	minValue = QingMingRankConfig.QingMingRank_ConsolationReward_Dict.get(GetServerType()).minValue
	if curValue < minValue:
		return
	
	#入榜
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	QMSR.HasData(roleId, [curValue, roleId, roleName, ZoneName.ZoneName])

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#清明消费排行今日榜
		QMSR = QingMingScoreRank()
		#清明消费排行昨日榜
		YQMCR_List = Contain.List("YQMCR_List", (2038, 1, 1), afterLoadQMCR)
		
		#数据交互
		#1.请求逻辑进程的排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicQingMingRank, OnControlRequestRank)
		#2.发送跨服排行榜数据到逻辑进程(今天, 昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataQingMingRankToLogic, OnControlUpdataRank)
		#3.发送跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdataQingMingRankToLogic_T, OnControlUpdataRank_T)
		
		#三触发 :: 1.载回今日榜QMSR 2.载回世界数据  3.活动开启 
		Event.RegEvent(Event.Eve_AfterLoadWorldData, TryStartActive)
		
		#跨天
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		#玩家事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)	
		Event.RegEvent(Event.Eve_AfterChangeDayConsumeUnbindRMB, OnTryInQingMingRank)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QingMingRank_OnGetConsolationReward", "清明消费排行_请求领取安慰奖"), OnGetConsolationReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QingMingRank_OnViewTodayRank", "清明消费排行_请求查看今日排行榜数据"), OnViewTodayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QingMingRank_OnViewYesterdayRank", "清明消费排行_请求查看昨日排行榜数据"), OnViewYesterdayRank)
