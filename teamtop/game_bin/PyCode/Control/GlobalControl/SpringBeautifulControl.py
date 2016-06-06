#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.SpringBeautifulControl")
#===============================================================================
# 新春最靓丽
#===============================================================================
import time
import datetime
import cDateTime
import cComplexServer
import DynamicPath
import Environment
from Util.File import TabFile
from Common.Message import PyMessage
from Common.Other import GlobalDataDefine, GlobalPrompt
from Control import ProcessMgr
from ComplexServer.Plug.Control import ControlProxy
from ComplexServer.API import GlobalHttp
from ComplexServer.Log import AutoLog
from Game.Role.Mail import EnumMail

if "_HasLoad" not in dir():
	IS_START = False	#活动开启标志
	
	ReturnDB = False	#数据载入是否成功
	ReturnIndexset = set()
	
	RANK_TODAY_1 = []
	RANK_TODAY_2 = []
	RANK_TODAY_3 = []
	RANK_TODAY_4 = []
	RANK_TODAY_5 = []
	
	RANK_OLD_1 = []
	RANK_OLD_2 = []
	RANK_OLD_3 = []
	RANK_OLD_4 = []
	RANK_OLD_5 = []
	
	#逻辑进程排行榜缓存数据{服务器区域类型 : {服务器Id: 前30名数据列表}}
	LoginRankAll_Dict = {1 : {}, 2 : {}, 3 : {}, 4 : {}, 5: {}}
	#总共的逻辑进程
	TotalLogicCnt = 0
	#逻辑进程区域类型
	LogicType_Dict = {}
	
	SPRING_ARANK_DICT = {}
	
	SFESTIVAL_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	SFESTIVAL_FILE_FOLDER_PATH.AppendPath("SpringFestival")
	
	CFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CFILE_FOLDER_PATH.AppendPath("CircularActive")
	
class SpringBActive(TabFile.TabLine):
	FilePath = CFILE_FOLDER_PATH.FilePath("SpringBActive.txt")
	def __init__(self):
		self.activeID = int
		self.beginTime = eval
		self.endTime = eval
	
	def Active(self):
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		#控制进程晚一分钟结束
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			OpenSpringB(None, self.activeID)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseSpringB)
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, OpenSpringB, self.activeID)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseSpringB)
			
def LoadSpringBActive():
	for cfg in SpringBActive.ToClassType(False):
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in LoadSpringBActive"
			return
		#不需要依赖什么, 在起服的时候就可以触发了
		cfg.Active()
		
class SprintBARank(TabFile.TabLine):
	FilePath = SFESTIVAL_FILE_FOLDER_PATH.FilePath("SprintBARank.txt")
	def __init__(self):
		self.serverType = int
		self.rank = int
		self.needScore = int
		self.rewardItems = self.GetEvalByString
		self.money = int
		self.bindRMB = int
		
def LoadSprintBARank():
	global SPRING_ARANK_DICT
	
	for cfg in SprintBARank.ToClassType(False):
		rankkey = (cfg.serverType, cfg.rank)
		if rankkey in SPRING_ARANK_DICT:
			print "GE_EXC,repeat serverType(%s) and rank(%s) in LoadSprintBARank" % (cfg.serverType, cfg.rank)
		SPRING_ARANK_DICT[rankkey] = cfg
#============活动开关==============
def OpenSpringB(callArgv, regparam):
	global IS_START
	if IS_START:
		print "GE_EXC, SpringBeautiful is already open"
		return
	IS_START = True
	
def CloseSpringB(callArgv, regparam):
	global IS_START
	if not IS_START:
		print "GE_EXC, SpringBeautiful is already close"
		return
	IS_START = False
	
	#活动关闭时清理
	global RANK_TODAY_1, RANK_TODAY_2, RANK_TODAY_3,RANK_TODAY_4,RANK_TODAY_5
	RANK_TODAY_1, RANK_TODAY_2, RANK_TODAY_3,RANK_TODAY_4,RANK_TODAY_5 = [], [], [], [], []
	global RANK_OLD_1, RANK_OLD_2, RANK_OLD_3, RANK_OLD_4, RANK_OLD_5
	RANK_OLD_1, RANK_OLD_2, RANK_OLD_3, RANK_OLD_4, RANK_OLD_5 = [], [], [], [], []

	global LoginRankAll_Dict, LogicType_Dict
	LoginRankAll_Dict = {1 : {}, 2 : {}, 3 : {}, 4 : {}, 5 : {}}
	LogicType_Dict = {}
	
def AfterNewMinute():
	#每分钟向所有的逻辑进程请求每一个服务器的前100名玩家数据，等待回调并且记录数据
	#如果有某些逻辑进程没有返回或者其他原因导致了这个回调是自回调的。这个时候，就会使用上一分钟
	#的旧数据代替这个一个服的数据。
	
	#所有的回调都完毕后，触发对这些玩家数据排序出前100名。并且http请求更新到数据库
	#（缺数据清理规则，数据中可能要存储天数的时间戳，清理天数 - 2 以后的数据 （因为是保存2天的数据））
	global IS_START
	if not IS_START: return
	
	nowMinute = cDateTime.Minute()
	nowHour = cDateTime.Hour()
	
	if nowMinute not in (0 ,30, 58):
		#0, 30, 58这三个时间点可能触发向逻辑进程请求数据
		return
	if nowMinute == 58 and nowHour != 23:
		#58分的时候只有是23点才会向逻辑进程请求数据
		return
	
	global ReturnDB
	if ReturnDB is False:
		print "GE_EXC, SpringBeautifulControl AfterNewMinute error not ReturnDB"
		#数据没有载回, 尝试再次载入
		InitSpringBRank()
		return
	
	if nowHour == 0 and nowMinute == 0:
		#0点0分的时候只发奖，操作数据库数据，逻辑进程自己把今天的数据拷贝到“昨天”的数据里面
		#NewDayRewardRoles()
		cComplexServer.RegTick(120, NewDayRewardRolesTick)
	else:
		#向逻辑进程请求数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
		RequestLogicRank()

def NewDayRewardRolesTick(callargv, prarm):
	print "BLUE, ++++++ NewDayRewardRolesTick"
	NewDayRewardRoles()

def NewDayRewardRoles():
	#发邮件对排行榜上面的玩家发奖
	global LoginRankAll_Dict
	#清理一天的排行榜缓存
	LoginRankAll_Dict =  {1 : {}, 2 : {}, 3 : {}, 4 : {}, 5: {}}
	global RANK_TODAY_1, RANK_TODAY_2, RANK_TODAY_3, RANK_TODAY_4, RANK_TODAY_5
	global RANK_OLD_1, RANK_OLD_2, RANK_OLD_3, RANK_OLD_4, RANK_OLD_5
	
	#替换昨天的跨服排行榜
	RANK_OLD_1 = RANK_TODAY_1
	RANK_OLD_2 = RANK_TODAY_2
	RANK_OLD_3 = RANK_TODAY_3
	RANK_OLD_4 = RANK_TODAY_4
	RANK_OLD_5 = RANK_TODAY_5
	#清理今天的跨服排行榜
	RANK_TODAY_1 = []
	RANK_TODAY_2 = []
	RANK_TODAY_3 = []
	RANK_TODAY_4 = []
	RANK_TODAY_5 = []
	
	days = cDateTime.Days()
	
	#更新跨服数据到数据库中
	GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBOldRankKey1, (days - 1, RANK_OLD_1))
	GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBOldRankKey2, (days - 1, RANK_OLD_2))
	GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBOldRankKey3, (days - 1, RANK_OLD_3))
	GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBOldRankKey4, (days - 1, RANK_OLD_4))
	GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBOldRankKey5, (days - 1, RANK_OLD_5))
	
	GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBRankKey1, (days, RANK_TODAY_1))
	GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBRankKey2, (days, RANK_TODAY_2))
	GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBRankKey3, (days, RANK_TODAY_3))
	GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBRankKey4, (days, RANK_TODAY_4))
	GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBRankKey5, (days, RANK_TODAY_5))
	#邮件奖励
	transaction = AutoLog.traSpringBMailReward
	
	serverType = 0
	for rank in [RANK_OLD_1,RANK_OLD_2,RANK_OLD_3,RANK_OLD_4,RANK_OLD_5]:
		serverType += 1
		RewardRoles(serverType, rank, transaction)
	
	print "BLUE, SpringBeautiful rank reward ++++++++++++++++++++++++++++++"




def RewardRoles(serverType, rank, transaction):
	SAD = SPRING_ARANK_DICT.get
	tmpRankDict = {}	#{roleId:rank}
	tmpRank = 1			#初始排名
	maxRankLen = 100	#排行榜最大个数
	for rankData in rank:
		if tmpRank > maxRankLen:
			continue
		cfg = SAD((serverType, tmpRank))
		if not cfg:
			print 'GE_EXC, SpringBeautifulControl.NewDayRewardRoles can not find serverType(%s) and rank(%s)' % (serverType, tmpRank)
			continue
			
		while rankData[0] < cfg.needScore:
			#如果当前的积分小于需要的积分，排名往后加
			tmpRank += 1
			if tmpRank > maxRankLen:
				break
			#获取下一个排名的配置
			cfg = SAD((serverType, tmpRank))
			if not cfg:
				print 'GE_EXC, SpringBeautifulControl.NewDayRewardRoles can not find serverType(%s) and rank(%s)' % (serverType, tmpRank)
				continue
				
		if tmpRank > maxRankLen:
			break
				
		if rankData[0] < cfg.needScore:
			print 'GE_EXC, SpringBeautifulControl RewardRoles error'
			continue
		
		tmpRankDict[rankData[1]] = tmpRank
		#完了排名+1
		tmpRank += 1
	
	maildatas = []
	for roleid, rank in tmpRankDict.iteritems():
		rolemaildata = (roleid, GlobalPrompt.SpringBA_Title, GlobalPrompt.SpringBA_Sender, GlobalPrompt.SpringBA_Contend % rank, transaction, GetSpringBRankMailReward(serverType,rank))
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	
def GetSpringBRankMailReward(serverType, rank):
	#组合一个邮件奖励字典
	mailData = {}
	
	global SPRING_ARANK_DICT
	cfg = SPRING_ARANK_DICT.get((serverType, rank))
	if not cfg:
		print "GE_EXC, SpringBeautifulControl GetSpringBRankMailReward can not find reward by servertype(%s) and rank(%s)" % (serverType, rank)
		return
	
	if cfg.rewardItems:
		mailData[EnumMail.EnumItemsKey] = cfg.rewardItems
	if cfg.money:
		mailData[EnumMail.EnumMonyKey] = cfg.money
	if cfg.bindRMB:
		mailData[EnumMail.EnumBindRMBKey] = cfg.bindRMB
	
	return mailData
	
def RequestLogicRank():
	#向所有的逻辑进程获取排行榜数据
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicSpringBRank, None, LogicBackRank, sessionid)
		
def LogicBackRank(callargv, regparam):
	#逻辑进程返回或者自返回
	global TotalLogicCnt
	TotalLogicCnt -= 1
	if callargv:
		global LogicType_Dict, LoginRankAll_Dict
		processId, serverType, logicranklist = callargv
		LogicType_Dict[processId] = serverType
		rankDict = LoginRankAll_Dict.get(serverType)
		if not rankDict:
			LoginRankAll_Dict[serverType] = rankDict = {} 
		rankDict[processId] = logicranklist

	if TotalLogicCnt == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdataRank()
	elif TotalLogicCnt < 0:
		print "GE_EXC, error in SpringBeautifulControl RequestBack (%s)" % TotalLogicCnt
		
def SortAndUpdataRank():
	#更新数据库中的排行榜数据
	global RANK_TODAY_1, RANK_TODAY_2, RANK_TODAY_3, RANK_TODAY_4, RANK_TODAY_5
	days = cDateTime.Days()
	RANK_TODAY_1 = []
	ranDict = LoginRankAll_Dict.get(1, {})
	for l in ranDict.values():
		RANK_TODAY_1.extend(l)
		
	if RANK_TODAY_1:
		#先排充值, 再排角色ID
		RANK_TODAY_1.sort(key = lambda it:(it[0], it[1]), reverse = True)
		RANK_TODAY_1 = RANK_TODAY_1[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBRankKey1, (days, RANK_TODAY_1))

	RANK_TODAY_2 = []
	ranDict = LoginRankAll_Dict.get(2, {})
	for l in ranDict.values():
		RANK_TODAY_2.extend(l)
	if RANK_TODAY_2:
		RANK_TODAY_2.sort(key = lambda it:(it[0], it[1]), reverse = True)
		RANK_TODAY_2 = RANK_TODAY_2[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBRankKey2, (days, RANK_TODAY_2))

	RANK_TODAY_3 = []
	ranDict = LoginRankAll_Dict.get(3, {})
	for l in ranDict.values():
		RANK_TODAY_3.extend(l)
	if RANK_TODAY_3:
		RANK_TODAY_3.sort(key = lambda it:(it[0], it[1]), reverse = True)
		RANK_TODAY_3 = RANK_TODAY_3[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBRankKey3, (days, RANK_TODAY_3))
	
	RANK_TODAY_4 = []
	ranDict = LoginRankAll_Dict.get(4, {})
	for l in ranDict.values():
		RANK_TODAY_4.extend(l)
	if RANK_TODAY_4:
		RANK_TODAY_4.sort(key = lambda it:(it[0], it[1]), reverse = True)
		RANK_TODAY_4 = RANK_TODAY_4[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBRankKey4, (days, RANK_TODAY_4))
	
	RANK_TODAY_5 = []
	ranDict = LoginRankAll_Dict.get(5, {})
	for l in ranDict.values():
		RANK_TODAY_5.extend(l)
	if RANK_TODAY_5:
		RANK_TODAY_5.sort(key = lambda it:(it[0], it[1]), reverse = True)
		RANK_TODAY_5 = RANK_TODAY_5[:100]
		GlobalHttp.SetGlobalData(GlobalDataDefine.SpringBRankKey5, (days, RANK_TODAY_5))
		
	#同步数据给所有的逻辑进程(当天数据)
	SyncAllLoginToday()
	
def SyncAllLoginToday():
	#同步当天最新的排行榜给所有的逻辑进程
	global LogicType_Dict
	for processId, pType in LogicType_Dict.iteritems():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, SpringBeautifulControl SyncAllLoginToday not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		if pType == 1:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateSpringBRankToLogic_T, RANK_TODAY_1)
		elif pType == 2:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateSpringBRankToLogic_T, RANK_TODAY_2)
		elif pType == 3:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateSpringBRankToLogic_T, RANK_TODAY_3)
		elif pType == 4:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateSpringBRankToLogic_T, RANK_TODAY_4)
		elif pType == 5:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateSpringBRankToLogic_T, RANK_TODAY_5)
		else:
			print "GE_EXC, SpringBeautifulControl SyncAllLogin error pType (%s)" % pType
			
def InitSpringBRank():
	index = 1
	key = GlobalDataDefine.SpringBRankKey1
	oldkey = GlobalDataDefine.SpringBOldRankKey1
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))
	
	index = 2
	key = GlobalDataDefine.SpringBRankKey2
	oldkey = GlobalDataDefine.SpringBOldRankKey2
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))

	index = 3
	key = GlobalDataDefine.SpringBRankKey3
	oldkey = GlobalDataDefine.SpringBOldRankKey3
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))

	index = 4
	key = GlobalDataDefine.SpringBRankKey4
	oldkey = GlobalDataDefine.SpringBOldRankKey4
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))
	
	index = 5
	key = GlobalDataDefine.SpringBRankKey5
	oldkey = GlobalDataDefine.SpringBOldRankKey5
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))
	
def OnGetRankBackEx(response, regparam):
	#数据返回
	if response is None:
		return
	
	index, key, oldkey = regparam
	
	#分析数据
	datadict = response
	days = cDateTime.Days()
	Checkdata(datadict, index, days, key, oldkey)
	
	global ReturnIndexset
	ReturnIndexset.add(index)
	
	global ReturnDB
	if len(ReturnIndexset) >= 5:
		ReturnDB = True
		#同步数据给所有逻辑进程
		SyncAllLogin()
	
def SyncAllLogin():
	#同步数据给所有的逻辑进程(今天和昨天)
	global LogicType_Dict
	for processId, pType in LogicType_Dict.iteritems():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, SpringBeautifulControl SyncAllLogin not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		if pType == 1:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateSpringBRankToLogic, (RANK_TODAY_1, RANK_OLD_1))
		elif pType == 2:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateSpringBRankToLogic, (RANK_TODAY_2, RANK_OLD_2))
		elif pType == 3:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateSpringBRankToLogic, (RANK_TODAY_3, RANK_OLD_3))
		elif pType == 4:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateSpringBRankToLogic, (RANK_TODAY_4, RANK_OLD_4))
		elif pType == 5:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdateSpringBRankToLogic, (RANK_TODAY_5, RANK_OLD_5))
		else:
			print "GE_EXC, SpringBeautifulControl SyncAllLogin error pType (%s)" % pType
			
def Checkdata(datadict, pType, nowdays, nowKey, oldKey):
	#检查和分析数据库返回的数据
	nowRank = []
	oldRank = []
	data = datadict.get(nowKey)
	olddata = datadict.get(oldKey)

	if data:
		d, rankdata = data
		if d == nowdays:
			#确定是今天的数据
			nowRank = rankdata
		elif d > nowdays:
			#天数有问题
			if not Environment.IsDevelop:
				print "GE_EXC, SpringBeautifulControl day error in OnGetRankBack"
			return
		elif d == nowdays - 1:
			#昨天的数据？
			oldRank = rankdata
			#数据库里面的数据有点旧了，更新一下
			GlobalHttp.SetGlobalData(nowKey, (nowdays, []))
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, oldRank))
			#设置当前缓存数据
			SetRankData(pType, [], oldRank)
			return
		else:
			# 已经相差2天了，清理数据?
			GlobalHttp.SetGlobalData(nowKey, (nowdays, []))
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, []))
			return

	if olddata:
		oldday, oldrankdata = olddata
		if oldday == nowdays - 1:
			#天数准确
			oldRank = oldrankdata
		elif oldday >= nowdays:
			if not Environment.IsDevelop:
				print "GE_EXC, SpringBeautifulControl old day error in OnGetRankBack"
		else:
			#旧数据太旧了，直接清理
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, []))
	SetRankData(pType, nowRank, oldRank)
	
def SetRankData(pType, nowRank, oldRank):
	#设置缓存数据
	global RANK_TODAY_1, RANK_TODAY_2, RANK_TODAY_3, RANK_TODAY_4,RANK_TODAY_5
	global RANK_OLD_1, RANK_OLD_2, RANK_OLD_3, RANK_OLD_4,RANK_OLD_5
	
	#重新排序, 先排消费，再排角色ID
	nowRank.sort(key = lambda it:(it[0], it[1]), reverse = True)
	oldRank.sort(key = lambda it:(it[0], it[1]), reverse = True)
	
	if pType == 1:
		RANK_TODAY_1 = nowRank
		RANK_OLD_1 = oldRank
	elif pType == 2:
		RANK_TODAY_2 = nowRank
		RANK_OLD_2 = oldRank
	elif pType == 3:
		RANK_TODAY_3 = nowRank
		RANK_OLD_3 = oldRank
	elif pType == 4:
		RANK_TODAY_4 = nowRank
		RANK_OLD_4 = oldRank
	elif pType == 5:
		RANK_TODAY_5 = nowRank
		RANK_OLD_5 = oldRank
		
def LoginRequestRank(sessionid, msg):
	'''
	逻辑进程主动请求跨服排行榜数据
	@param sessionid:
	@param msg:
	'''
	global ReturnDB,  LogicType_Dict
	#先记录逻辑进程的区域类型
	processId, pType, rank = msg
	LoginRankAll_Dict[pType][processId] =  rank
	
	LogicType_Dict[processId] = pType
	
	if not ReturnDB:
		#控制进程当前还没有从DB载回数据，等待数据载回来再发过去
		return

	#根据类型发送数据
	if pType == 1:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RANK_TODAY_1, RANK_OLD_1))
	elif pType == 2:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RANK_TODAY_2, RANK_OLD_2))
	elif pType == 3:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RANK_TODAY_3, RANK_OLD_3))
	elif pType == 4:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RANK_TODAY_4, RANK_OLD_4))
	elif pType == 5:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataBraveHeroRankToLogic, (RANK_TODAY_5, RANK_OLD_5))
	else:
		print "GE_EXC, error pType (%s) in LoginRequestRank" % pType
		
if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadSpringBActive()
		LoadSprintBARank()
		
		InitSpringBRank()
		cComplexServer.RegAfterNewMinuteCallFunction(AfterNewMinute)
		cComplexServer.RegDistribute(PyMessage.Control_GetSpringBRank, LoginRequestRank)
		