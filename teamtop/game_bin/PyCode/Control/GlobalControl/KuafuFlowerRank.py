#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.KuafuFlowerRank")
#===============================================================================
# 跨服鲜花排行榜
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
	#缓存排行榜数据
	CacheObj = None
	
	#逻辑进程排行榜缓存数据{服务器区域类型 : {服务器Id: 前50名数据列表}}
	#LoginRankAll_Dict --> {serverType:{processId:{1:manRank, 2:womenRank}}}
	LoginRankAll_Dict = {1 : {}, 2 : {}, 3 : {}, 4 : {}}
	
	#总共的逻辑进程
	TotalLogicCnt = 0
	
	#逻辑进程区域类型  {processId -- > serverType}
	LogicType_Dict = {}
	
	#数据载入是否成功
	ReturnDB = False
	#返回区域(需要4个都返回)
	ReturnIndexset = set()
	
	#活动是否开启(注意这里活动要比本服晚一天, 结束时间是膜拜的结束时间)
	IsStart = False
	
	CFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CFILE_FOLDER_PATH.AppendPath("CircularActive")
	
	BFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	BFILE_FOLDER_PATH.AppendPath("Flower")
	
	#跨服鲜花榜排行榜字典 {(sex, 奖励索引, 服务器类型):奖励}
	KuafuFlowerRank_Dict = {}
	#区间对应的排行榜奖励索引{sex:{排名区间:奖励索引}}
	KuafuFlowerRankToIndex_Dict = {}
	#跨服鲜花榜激活字典
	KuafuFlowerRankActive_Dict = {}
	
class RankCache():
	def __init__(self):
		self.manCache_1 = []
		self.manCache_2 = []
		self.manCache_3 = []
		self.manCache_4 = []
		
		self.womenCache_1 = []
		self.womenCache_2 = []
		self.womenCache_3 = []
		self.womenCache_4 = []
		
		self.oldManCache_1 = []
		self.oldManCache_2 = []
		self.oldManCache_3 = []
		self.oldManCache_4 = []
		
		self.oldWomenCache_1 = []
		self.oldWomenCache_2 = []
		self.oldWomenCache_3 = []
		self.oldWomenCache_4 = []
		
		self.man_1 = 0
		self.man_2 = 0
		self.man_3 = 0
		self.man_4 = 0
		
		self.women_1 = 0
		self.women_2 = 0
		self.women_3 = 0
		self.women_4 = 0
		
		
	def clearManCache(self):
		self.manCache_1 = []
		self.manCache_2 = []
		self.manCache_3 = []
		self.manCache_4 = []
		
	def clearWomenCache(self):
		self.womenCache_1 = []
		self.womenCache_2 = []
		self.womenCache_3 = []
		self.womenCache_4 = []
		
	def clearTodayCache(self):
		self.clearManCache()
		self.clearWomenCache()
		
	def clearOldManCache(self):
		self.oldManCache_1 = []
		self.oldManCache_2 = []
		self.oldManCache_3 = []
		self.oldManCache_4 = []
		
	def clearOldWomenCache(self):
		self.oldWomenCache_1 = []
		self.oldWomenCache_2 = []
		self.oldWomenCache_3 = []
		self.oldWomenCache_4 = []
	
	def clearYesterdayCache(self):
		self.clearOldManCache()
		self.clearOldWomenCache()
		
	def returnTodayCache_1(self):
		return self.manCache_1, self.womenCache_1
	
	def returnTodayCache_2(self):
		return self.manCache_2, self.womenCache_2
	
	def returnTodayCache_3(self):
		return self.manCache_3, self.womenCache_3
	
	def returnTodayCache_4(self):
		return self.manCache_4, self.womenCache_4
	
	def afterNewDay(self):
		self.oldManCache_1 = self.manCache_1
		self.oldManCache_2 = self.manCache_2
		self.oldManCache_3 = self.manCache_3
		self.oldManCache_4 = self.manCache_4
		self.clearManCache()
		
		self.oldWomenCache_1 = self.womenCache_1
		self.oldWomenCache_2 = self.womenCache_2
		self.oldWomenCache_3 = self.womenCache_3
		self.oldWomenCache_4 = self.womenCache_4
		self.clearWomenCache()
		
		self.calFirstRoleData()
		
	def calFirstRoleData(self):
		self.man_1 = self.oldManCache_1[0][0] if self.oldManCache_1 else 0
		self.man_2 = self.oldManCache_2[0][0] if self.oldManCache_2 else 0
		self.man_3 = self.oldManCache_3[0][0] if self.oldManCache_3 else 0
		self.man_4 = self.oldManCache_4[0][0] if self.oldManCache_4 else 0
		
		self.women_1 = self.oldWomenCache_1[0][0] if self.oldWomenCache_1 else 0
		self.women_2 = self.oldWomenCache_2[0][0] if self.oldWomenCache_2 else 0
		self.women_3 = self.oldWomenCache_3[0][0] if self.oldWomenCache_3 else 0
		self.women_4 = self.oldWomenCache_4[0][0] if self.oldWomenCache_4 else 0
		
	def returnFirstRoleData_1(self):
		return self.man_1, self.women_1
	
	def returnFirstRoleData_2(self):
		return self.man_2, self.women_2
	
	def returnFirstRoleData_3(self):
		return self.man_3, self.women_3
	
	def returnFirstRoleData_4(self):
		return self.man_4, self.women_4
	
	def returnYesterdayCache_1(self):
		return self.oldManCache_1, self.oldWomenCache_1
	
	def returnYesterdayCache_2(self):
		return self.oldManCache_2, self.oldWomenCache_2
	
	def returnYesterdayCache_3(self):
		return self.oldManCache_3, self.oldWomenCache_3
	
	def returnYesterdayCache_4(self):
		return self.oldManCache_4, self.oldWomenCache_4
	
	def returnManCache_1(self):
		return self.manCache_1, self.oldManCache_1
	
	def returnManCache_2(self):
		return self.manCache_2, self.oldManCache_2
	
	def returnManCache_3(self):
		return self.manCache_3, self.oldManCache_3
	
	def returnManCache_4(self):
		return self.manCache_4, self.oldManCache_4
	
	
class KuafuFlowerRankActiveConfig(TabFile.TabLine):
	FilePath = CFILE_FOLDER_PATH.FilePath("KuafuFlowerRankActive.txt")
	def __init__(self):
		self.activeID = int					#活动ID
		self.beginTime = eval				#开始时间
		self.endTime = eval					#结束时间
	
	def Active(self):
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳(注意这里跨服比本服要晚一天结束, 因为本服最后一天不会产生数据, 所以不会对最后一天数据产生影响)
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple())) + 60 * 60 * 24
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			OpenKuafuFlowerRank(None, self.activeID)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseKuafuFlower)
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, OpenKuafuFlowerRank, self.activeID)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseKuafuFlower)
			
def LoadKuafuFlowerRankActiveConfig():
	global KuafuFlowerRankActive_Dict
	
	for cfg in KuafuFlowerRankActiveConfig.ToClassType(False):
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in KuafuFlowerRankActive"
			return
		KuafuFlowerRankActive_Dict[cfg.activeID] = cfg
	
	KuafuFlowerRankActive()
	
def KuafuFlowerRankActive():
	#尝试激活跨服鲜花榜
	for cfg in KuafuFlowerRankActive_Dict.itervalues():
		cfg.Active()
	
class KuafuFlowerRankConfig(TabFile.TabLine):
	FilePath = BFILE_FOLDER_PATH.FilePath("KuafuFlowerRank.txt")
	def __init__(self):
		self.sex = int						#性别
		self.index = int					#排名奖励索引
		self.rankInterval = eval			#排名区间
		self.serverType = int				#服务器类型
		self.reward = eval					#奖励
	
def LoadKuafuFlowerRankConfig():
	global KuafuFlowerRank_Dict
	global KuafuFlowerRankToIndex_Dict
	
	for KFR in KuafuFlowerRankConfig.ToClassType(False):
		#{(sex, 奖励索引, 服务器类型):奖励}
		if (KFR.sex, KFR.index, KFR.serverType) in KuafuFlowerRank_Dict:
			print "GE_EXC, repeat (sex : %s, index : %s, serverType : %s) in KuafuFlowerRank_Dict" % (KFR.sex, KFR.index, KFR.serverType)
		
		#{sex:{排名区间:奖励索引}}
		if KFR.sex not in KuafuFlowerRankToIndex_Dict:
			KuafuFlowerRankToIndex_Dict[KFR.sex] = {}
		
		if KFR.rankInterval not in KuafuFlowerRankToIndex_Dict[KFR.sex]:
			KuafuFlowerRankToIndex_Dict[KFR.sex][KFR.rankInterval] = KFR.index
		
		KuafuFlowerRank_Dict[(KFR.sex, KFR.index, KFR.serverType)] = KFR
	
def OpenKuafuFlowerRank(callArgv, regparam):
	#开启跨服鲜花榜
	global IsStart, CacheObj
	if IsStart:
		print "GE_EXC, KuafuFlowerRank is already open"
	IsStart = True
	
def CloseKuafuFlower(callArgv, regparam):
	#结束跨服鲜花榜
	global IsStart, CacheObj, LoginRankAll_Dict, LogicType_Dict
	if not IsStart:
		print "GE_EXC, KuafuFlowerRank is already close"
	IsStart = False
	
	#清理排行榜数据
	CacheObj = None
	
	#清理逻辑进程排行榜缓存数据{服务器区域类型 : {服务器Id: 前50名数据列表}}
	LoginRankAll_Dict = {1 : {}, 2 : {}, 3 : {}, 4 : {}, 5 : {}}
	
	#清理逻辑进程区域类型
	LogicType_Dict = {}
	
	

def AfterNewMinute():
	#每一个整点(23点58分也会)向所有的逻辑进程请求每一个服务器的男女鲜花榜前50名玩家数据，等待回调并且记录数据
	#如果有某些逻辑进程没有返回或者其他原因导致了这个回调是自回调的。这个时候，就会使用上一个小时
	#的旧数据代替这个一个服的数据。
	
	#所有的回调都完毕后，触发对这些玩家数据排序出前50名。并且http请求更新到数据库
	#（缺数据清理规则，数据中可能要存储天数的时间戳，清理天数 - 2 以后的数据 （因为是保存2天的数据））
	
	
	if not IsStart: return
	
	nowMinute = cDateTime.Minute()
	nowHour = cDateTime.Hour()
	
	if nowMinute not in (0, 30, 58):
		#0, 30, 58这三个时间点可能触发向逻辑进程请求数据
		return
	if nowMinute == 58 and nowHour != 23:
		#58分的时候只有是23点才会向逻辑进程请求数据
		return
	
	global ReturnDB
	if ReturnDB is False:
		print "GE_EXC, KuafuFlowerRankControl AfterNewHour error not ReturnDB"
		#数据没有载回, 尝试再次载入
		InitGetRankEx()
		return
	
	if cDateTime.Hour() == 0 and nowMinute == 0:
		#0点0分的时候只发奖，操作数据库数据，逻辑进程自己把今天的数据拷贝到“昨天”的数据里面
		NewDayRewardRoles()
	else:
		#向逻辑进程请求数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
		RequestLogicRank()

def RequestLogicRank():
	#向所有的逻辑进程获取排行榜数据
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestLogicFlowerRank, None, LogicBackRank, sessionid)

def LogicBackRank(callargv, regparam):
	#逻辑进程返回或者自返回
	global TotalLogicCnt
	TotalLogicCnt -= 1
	
	if callargv:
		global LogicType_Dict, LoginRankAll_Dict
		processId, serverType, (logicManRankList, logicWomenRankList) = callargv
		
		LogicType_Dict[processId] = serverType
		
		#LoginRankAll_Dict --> {serverType:{processId:{1:manRank, 2:womenRank}}}
		rankDict = LoginRankAll_Dict.get(serverType)
		if not rankDict:
			LoginRankAll_Dict[serverType] = rankDict = {}
		rankDict[processId] = {1:logicManRankList, 2:logicWomenRankList}

	if TotalLogicCnt == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdataRank()
	elif TotalLogicCnt < 0:
		print "GE_EXC, error in KuafuFlowerRank RequestBack (%s)" % TotalLogicCnt
	
def SortAndUpdataRank():
	#更新数据库中的排行榜数据
	global CacheObj
	
	days = cDateTime.Days()
	
	#清理今日缓存数据
	CacheObj.clearTodayCache()
	
	rankDict = LoginRankAll_Dict.get(1, {})
	for logicRank in rankDict.itervalues():
		#合并
		CacheObj.manCache_1.extend(logicRank.get(1, []))
		CacheObj.womenCache_1.extend(logicRank.get(2, []))
	#排序
	if CacheObj.manCache_1:
		CacheObj.manCache_1.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
		CacheObj.manCache_1 = CacheObj.manCache_1[:50]
	if CacheObj.womenCache_1:
		CacheObj.womenCache_1.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
		CacheObj.womenCache_1 = CacheObj.womenCache_1[:50]
	#存储
	GlobalHttp.SetGlobalData(GlobalDataDefine.KuafuFlowerDataKey_1, (days, CacheObj.returnTodayCache_1()))
	
	rankDict = LoginRankAll_Dict.get(2, {})
	for logicRank in rankDict.itervalues():
		#合并
		CacheObj.manCache_2.extend(logicRank.get(1, []))
		CacheObj.womenCache_2.extend(logicRank.get(2, []))
	#排序
	if CacheObj.manCache_2:
		CacheObj.manCache_2.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
		CacheObj.manCache_2 = CacheObj.manCache_2[:50]
	if CacheObj.womenCache_2:
		CacheObj.womenCache_2.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
		CacheObj.womenCache_2 = CacheObj.womenCache_2[:50]
	#存储
	GlobalHttp.SetGlobalData(GlobalDataDefine.KuafuFlowerDataKey_2, (days, CacheObj.returnTodayCache_2()))
	
	rankDict = LoginRankAll_Dict.get(3, {})
	for logicRank in rankDict.itervalues():
		CacheObj.manCache_3.extend(logicRank.get(1, []))
		CacheObj.womenCache_3.extend(logicRank.get(2, []))
	if CacheObj.manCache_3:
		CacheObj.manCache_3.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
		CacheObj.manCache_3 = CacheObj.manCache_3[:50]
	if CacheObj.womenCache_3:
		CacheObj.womenCache_3.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
		CacheObj.womenCache_3 = CacheObj.womenCache_1[:50]
	GlobalHttp.SetGlobalData(GlobalDataDefine.KuafuFlowerDataKey_3, (days, CacheObj.returnTodayCache_3()))

	rankDict = LoginRankAll_Dict.get(4, {})
	for logicRank in rankDict.itervalues():
		CacheObj.manCache_4.extend(logicRank.get(1, []))
		CacheObj.womenCache_4.extend(logicRank.get(2, []))
	if CacheObj.manCache_4:
		CacheObj.manCache_4.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
		CacheObj.manCache_4 = CacheObj.manCache_1[:50]
	if CacheObj.womenCache_4:
		CacheObj.womenCache_4.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
		CacheObj.womenCache_4 = CacheObj.womenCache_1[:50]
	GlobalHttp.SetGlobalData(GlobalDataDefine.KuafuFlowerDataKey_4, (days, CacheObj.returnTodayCache_4()))

	#同步数据给所有的逻辑进程(这里需要同步今日和昨日的数据)
	SyncAllLogin()

def NewDayRewardRoles():
	#发邮件对排行榜上面的玩家发奖
	global LoginRankAll_Dict, CacheObj
	#清理一天的排行榜缓存
	LoginRankAll_Dict =  {1 : {}, 2 : {}, 3 : {}, 4 : {}, 5 : {}}
	
	CacheObj.afterNewDay()
	
	days = cDateTime.Days()
	
	#更新跨服数据到数据库中
	GlobalHttp.SetGlobalData(GlobalDataDefine.KuafuFlowerOldDataKey_1, (days - 1, CacheObj.returnYesterdayCache_1()))
	GlobalHttp.SetGlobalData(GlobalDataDefine.KuafuFlowerOldDataKey_2, (days - 1, CacheObj.returnYesterdayCache_2()))
	GlobalHttp.SetGlobalData(GlobalDataDefine.KuafuFlowerOldDataKey_3, (days - 1, CacheObj.returnYesterdayCache_3()))
	GlobalHttp.SetGlobalData(GlobalDataDefine.KuafuFlowerOldDataKey_4, (days - 1, CacheObj.returnYesterdayCache_4()))
	
	GlobalHttp.SetGlobalData(GlobalDataDefine.KuafuFlowerDataKey_1, (days, CacheObj.returnTodayCache_1()))
	GlobalHttp.SetGlobalData(GlobalDataDefine.KuafuFlowerDataKey_2, (days, CacheObj.returnTodayCache_2()))
	GlobalHttp.SetGlobalData(GlobalDataDefine.KuafuFlowerDataKey_3, (days, CacheObj.returnTodayCache_3()))
	GlobalHttp.SetGlobalData(GlobalDataDefine.KuafuFlowerDataKey_4, (days, CacheObj.returnTodayCache_4()))
	
	#邮件奖励
	transaction = AutoLog.traKuafuFlower
	
	#第一区域服务器
	SendRankRewardByMail(CacheObj.oldManCache_1, CacheObj.oldWomenCache_1, 1, transaction)
	SendRankRewardByMail(CacheObj.oldManCache_2, CacheObj.oldWomenCache_2, 2, transaction)
	SendRankRewardByMail(CacheObj.oldManCache_3, CacheObj.oldWomenCache_3, 3, transaction)
	SendRankRewardByMail(CacheObj.oldManCache_4, CacheObj.oldWomenCache_4, 4, transaction)
	
	print 'BLUE, KuafuFlowerRank rank, region 1:%s, %s, region 2:%s, %s, region 3:%s, %s, region 4:%s, %s' % (CacheObj.oldManCache_1, CacheObj.oldWomenCache_1, CacheObj.oldManCache_2, CacheObj.oldWomenCache_2, CacheObj.oldManCache_3, CacheObj.oldWomenCache_3, CacheObj.oldManCache_4, CacheObj.oldWomenCache_4)
	
	#同步今日和昨日数据
	SyncAllLogin()
	
def SendRankRewardByMail(manCache, womenCache, serverType, transaction):
	maildatas = []
	for index, rd in enumerate(manCache):
		rank = index + 1
		roleid = rd[0]
		roleSex = rd[1][4]
		rolemaildata = (roleid, GlobalPrompt.FlowerKuafuRank_ManTitle, GlobalPrompt.FlowerKuafuRank_Sender, GlobalPrompt.FlowerKuafuRank_ManContent % rank, transaction, GetRankMailReward(roleSex, rank, serverType))
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	maildatas = []
	for index, rd in enumerate(womenCache):
		rank = index + 1
		roleid = rd[0]
		roleSex = rd[1][4]
		rolemaildata = (roleid, GlobalPrompt.FlowerKuafuRank_WomenTitle, GlobalPrompt.FlowerKuafuRank_Sender, GlobalPrompt.FlowerKuafuRank_WomenContent % rank, transaction, GetRankMailReward(roleSex, rank, serverType))
		maildatas.append(rolemaildata)
	#发送邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	
def GetRankMailReward(sexNumber, rank, serverType):
	#组合一个邮件奖励字典
	mailData = {}
	
	#排名 --> 排名区间 --> 奖励索引
	global KuafuFlowerRankToIndex_Dict
	index = 0
	if sexNumber not in KuafuFlowerRankToIndex_Dict:
		print 'GE_EXC, GetRankMailReward can not find sex (%s) in KuafuFlowerRankToIndex_Dict' % sexNumber
		return
	
	for (begin, end), rewardIndex in KuafuFlowerRankToIndex_Dict[sexNumber].iteritems():
		if (begin == end) and (rank == begin):
			#begin == end
			index = rewardIndex
			break
		elif (begin != end) and (begin <= rank <= end):
			#begin != end
			index = rewardIndex
			break
	else:
		print "GE_EXC, GetRankMailReward can not find index by rank (%s) KuafuFlowerRankToIndex_Dict" % rank
		return
	
	#(奖励索引, 服务器类型) --> 奖励
	cfg = KuafuFlowerRank_Dict.get((sexNumber, index, serverType))
	if not cfg:
		print "GE_EXC, GetRankMailReward can not find reward by rank (%s) serverType (%s) KuafuFlowerRank_Dict" % (rank, serverType)
		return
	
	#目前只有物品奖励
	if cfg.reward:
		mailData[EnumMail.EnumItemsKey] = cfg.reward
	return mailData

def InitGetRankEx():
	global CacheObj
	CacheObj = RankCache()
	
	#这里一个榜50个数据, 一个区域2榜100个数据， 4个区域一次载回400个数据, 应该可以 ？
	index = 1
	key = GlobalDataDefine.KuafuFlowerDataKey_1
	oldkey = GlobalDataDefine.KuafuFlowerOldDataKey_1
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))
	
	index = 2
	key = GlobalDataDefine.KuafuFlowerDataKey_2
	oldkey = GlobalDataDefine.KuafuFlowerOldDataKey_2
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))

	index = 3
	key = GlobalDataDefine.KuafuFlowerDataKey_3
	oldkey = GlobalDataDefine.KuafuFlowerOldDataKey_3
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))

	index = 4
	key = GlobalDataDefine.KuafuFlowerDataKey_4
	oldkey = GlobalDataDefine.KuafuFlowerOldDataKey_4
	GlobalHttp.GetGlobalDataByKeys([key, oldkey], OnGetRankBackEx, (index, key, oldkey))
	
def OnGetRankBackEx(response, regparam):
	#数据返回了
	if response is None:
		#自返回
		return
	
	index, key, oldkey = regparam
	
	datadict = response
	days = cDateTime.Days()
	
	#分析和处理数据
	Checkdata(datadict, index, days, key, oldkey)
	
	global ReturnIndexset
	ReturnIndexset.add(index)

	#已经载入成功了
	global ReturnDB
	if len(ReturnIndexset) >= 4:
		ReturnDB = True
		#同步数据给所有的逻辑进程
		SyncAllLogin()

def SetRankData(pType, nowRank, oldRank):
	#设置缓存数据
	global CacheObj
	
	nowManRank, nowWomenRank = nowRank
	oldManRank, oldWomenRank = oldRank
	
	#重新排序(为什么要重新排序??)
	nowManRank.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
	nowWomenRank.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
	oldManRank.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
	oldWomenRank.sort(key = lambda x:(x[1][0], x[1][2], x[1][3], -x[0]), reverse = True)
	
	if pType == 1:
		CacheObj.manCache_1 = nowManRank
		CacheObj.oldManCache_1 = oldManRank
		CacheObj.womenCache_1 = nowWomenRank
		CacheObj.oldWomenCache_1 = oldWomenRank
		#这里需要重新计算昨日第一角色id
		CacheObj.man_1 = oldManRank[0][0] if oldManRank else 0
		CacheObj.women_1 = oldWomenRank[0][0] if oldWomenRank else 0
	elif pType == 2:
		CacheObj.manCache_2 = nowManRank
		CacheObj.oldManCache_2 = oldManRank
		CacheObj.womenCache_2 = nowWomenRank
		CacheObj.oldWomenCache_2 = oldWomenRank
		CacheObj.man_2 = oldManRank[0][0] if oldManRank else 0
		CacheObj.women_2 = oldWomenRank[0][0] if oldWomenRank else 0
	elif pType == 3:
		CacheObj.manCache_3 = nowManRank
		CacheObj.oldManCache_3 = oldManRank
		CacheObj.womenCache_3 = nowWomenRank
		CacheObj.oldWomenCache_3 = oldWomenRank
		CacheObj.man_3 = oldManRank[0][0] if oldManRank else 0
		CacheObj.women_3 = oldWomenRank[0][0] if oldWomenRank else 0
	elif pType == 4:
		CacheObj.manCache_4 = nowManRank
		CacheObj.oldManCache_4 = oldManRank
		CacheObj.womenCache_4 = nowWomenRank
		CacheObj.oldWomenCache_4 = oldWomenRank
		CacheObj.man_4 = oldManRank[0][0] if oldManRank else 0
		CacheObj.women_4 = oldWomenRank[0][0] if oldWomenRank else 0
		
def Checkdata(datadict, pType, nowdays, nowKey, oldKey):
	#检查和分析数据库返回的数据
	nowManRank, nowWomenRank = [], []
	oldManRank, oldWomenRank = [], []
	data = datadict.get(nowKey)
	olddata = datadict.get(oldKey)
	
	if data:
		d, (manRankData, womenRankData) = data
		if d == nowdays:
			#确定是今天的数据
			nowManRank, nowWomenRank = manRankData, womenRankData
		elif d > nowdays:
			#天数有问题
			if not Environment.IsDevelop:
				print "GE_EXC, day error in OnGetRankBack"
			return
		elif d == nowdays - 1:
			#昨天的数据？
			oldManRank, oldWomenRank = manRankData, womenRankData
			#数据库里面的数据有点旧了，更新一下
			GlobalHttp.SetGlobalData(nowKey, (nowdays, ([], [])))
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, (oldManRank, oldWomenRank)))
			#设置当前缓存数据
			SetRankData(pType, ([], []), (oldManRank, oldWomenRank))
			return
		else:
			# 已经相差2天了，清理数据?
			GlobalHttp.SetGlobalData(nowKey, (nowdays, ([], [])))
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, ([], [])))
			return

	if olddata:
		oldday, (oldManRankData, oldWomenRankData) = olddata
		if oldday == nowdays - 1:
			#天数准确
			oldManRank, oldWomenRank = oldManRankData, oldWomenRankData
		elif oldday >= nowdays:
			if not Environment.IsDevelop:
				print "GE_EXC, old day error in OnGetRankBack"
		else:
			#旧数据太旧了，直接清理
			GlobalHttp.SetGlobalData(oldKey, (nowdays - 1, ([], [])))
	SetRankData(pType, (nowManRank, nowWomenRank), (oldManRank, oldWomenRank))

def SyncAllLogin():
	#今天和昨天的数据是一直需要的, 所以就保留一个同步的函数了
	#同步数据给所有的逻辑进程(今天和昨天)
	global LogicType_Dict, CacheObj
	for processId, pType in LogicType_Dict.iteritems():
		cp = ProcessMgr.ControlProcesssIds.get(processId)
		if not cp:
			if not Environment.IsDevelop:
				print "GE_EXC, SyncAllLogin not process sessionid (%s)" % processId
			continue
		sessionid = cp.session_id
		if pType == 1:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataFlowerRankToLogic, (CacheObj.returnTodayCache_1(), CacheObj.returnYesterdayCache_1(), CacheObj.returnFirstRoleData_1()))
		elif pType == 2:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataFlowerRankToLogic, (CacheObj.returnTodayCache_2(), CacheObj.returnYesterdayCache_2(), CacheObj.returnFirstRoleData_2()))
		elif pType == 3:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataFlowerRankToLogic, (CacheObj.returnTodayCache_3(), CacheObj.returnYesterdayCache_3(), CacheObj.returnFirstRoleData_3()))
		elif pType == 4:
			ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataFlowerRankToLogic, (CacheObj.returnTodayCache_4(), CacheObj.returnYesterdayCache_4(), CacheObj.returnFirstRoleData_4()))
		else:
			print "GE_EXC, SyncAllLogin error pType (%s)" % pType

def LoginRequestRank(sessionid, msg):
	'''
	#逻辑进程主动请求跨服排行榜数据
	@param sessionid:
	@param msg:(进程ID， 进程区域类型)
	'''
	global ReturnDB,  LogicType_Dict
	#先记录逻辑进程的区域类型
	processId, pType, (logicManRank, logicWomenRank) = msg
	
	LoginRankAll_Dict[pType][processId] =  {1:logicManRank, 2:logicWomenRank}
	
	LogicType_Dict[processId] = pType
	
	if not ReturnDB:
		#控制进程当前还没有从DB载回数据，等待数据载回来再发过去
		return

	#根据类型发送数据
	global CacheObj
	if pType == 1:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataFlowerRankToLogic, (CacheObj.returnTodayCache_1(), CacheObj.returnYesterdayCache_1(), CacheObj.returnFirstRoleData_1()))
	elif pType == 2:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataFlowerRankToLogic, (CacheObj.returnTodayCache_2(), CacheObj.returnYesterdayCache_2(), CacheObj.returnFirstRoleData_2()))
	elif pType == 3:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataFlowerRankToLogic, (CacheObj.returnTodayCache_3(), CacheObj.returnYesterdayCache_3(), CacheObj.returnFirstRoleData_3()))
	elif pType == 4:
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_UpdataFlowerRankToLogic, (CacheObj.returnTodayCache_4(), CacheObj.returnYesterdayCache_4(), CacheObj.returnFirstRoleData_4()))
	else:
		print "GE_EXC, error pType (%s) in LoginRequestRank" % pType
	
if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadKuafuFlowerRankActiveConfig()
		LoadKuafuFlowerRankConfig()
		InitGetRankEx()
		cComplexServer.RegAfterNewMinuteCallFunction(AfterNewMinute)
		cComplexServer.RegDistribute(PyMessage.Control_GetFlowerRank, LoginRequestRank)
		
