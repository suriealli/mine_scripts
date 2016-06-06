#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.GlobalControl.PassionbActD12GroupBuyControl")
#===============================================================================
# 双十二团购控制模块
#===============================================================================
import time
import datetime
import cDateTime
import DynamicPath
import Environment
import cComplexServer
from Util.File import TabFile
from Common.Message import PyMessage
from Common.Other import GlobalDataDefine, GlobalPrompt
from Control import ProcessMgr
from ComplexServer.Plug.Control import ControlProxy
from ComplexServer.API import GlobalHttp
from ComplexServer.Log import AutoLog
from Game.Role.Mail import EnumMail

if "_HasLoad" not in dir():

	IsStart = False
	#跨服全局数据
	Pre20RankRecord = {}		#前20消费缓存{idnex:[roleid]}(辅助结构用来优化排序算法)
	ConsumeRecord 	= {}		#消费记录{index:[roleid],...}

	#记录历史数据，防止逻辑服务器无法连接
	OldConsumeRecord = {}		#{serverid:{index:[(roleid,time)]}}

	ReturnDB = False
	TotalLogicCnt = 0 			#总共的逻辑进程数
	TodayFlag = 0 				#当天标记(用来索引逻辑进程双缓存数据,可解决控制进程统计期间，逻辑进程无法团购问题)
	
	LeftDay = 0					#活动结束当天

	#团购基础配置
	PassionActD12GB_Dict = {}
	#差价查询辅助字典
	PassionActDiscount = {}


	CFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CFILE_FOLDER_PATH.AppendPath("CircularActive")
	
	DFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	DFILE_FOLDER_PATH.AppendPath("PassionActDoubleTwelve")

	D12Activity = {}	#活动控制

class D12GroupBuyActiveConfig(TabFile.TabLine):
	FilePath = CFILE_FOLDER_PATH.FilePath("D12GroupBuyActive.txt")
	def __init__(self):
		self.activeID = int					#活动ID
		self.beginTime = eval				#开始时间
		self.endTime = eval					#结束时间
	
	def Active(self):
		#当前时间
		nowDate = (cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second())
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = int(time.mktime(datetime.datetime(cDateTime.Year(), cDateTime.Month(), cDateTime.Day(), cDateTime.Hour(), cDateTime.Minute(), cDateTime.Second()).timetuple()))
		
		if self.beginTime <= nowDate < self.endTime:
			#在开始和结束时间戳之间, 激活
			OpenActivity(None,None)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseActivity)
		elif nowDate < self.beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, OpenActivity)
			cComplexServer.RegTick(endTime - nowTime + 60, CloseActivity)


class D12GroupBuyConfig(TabFile.TabLine):
	FilePath = DFILE_FOLDER_PATH.FilePath("PassionGroupBuy.txt")
	def __init__(self):
		self.index = int 							#物品索引
		self.item_name = str
		self.originCost = int						#商品原价
		self.needRMB = int 							#当前团购价
		self.groupRule = self.GetEvalByString		#团购规则
		self.reward = self.GetEvalByString			#前20奖励

def LoadD12GBConfig():
	global PassionActD12GB_Dict

	for cfg in D12GroupBuyConfig.ToClassType(False):
		if cfg.index in PassionActD12GB_Dict:
			print "GE_EXC, repeat index(%s) in PassionActD12GB_Dict" % cfg.index
		PassionActDiscount[cfg.index] = {}
		for count, price,_ in cfg.groupRule:
			PassionActDiscount[cfg.index][count] = price

		PassionActD12GB_Dict[cfg.index] = cfg

def LoadD12GroupBuyActiveConfig():
	global D12Activity
	
	for cfg in D12GroupBuyActiveConfig.ToClassType(False):
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in D12Activity"
			return
		D12Activity[cfg.activeID] = cfg

def OpenActivity(callArgv, regparam):
	global IsStart
	global TodayFlag
	global LeftDay

	if IsStart:
		print "GE_EXE,D12GroupBuyActivity is alread Actived!"
		return

	IsStart = True
	TodayFlag = cDateTime.Days()

def CloseActivity(callArgv, regparam):
	global IsStart

	if not IsStart:
		print "GE_EXE,D12GroupBuyActivity is alread Closed!"
		return

	IsStart = True

def CheckActivity():
	for _,cfg in D12Activity.iteritems():
		cfg.Active()

def CleanCacheData():
	'''
	清空缓存数据
	'''
	global Pre20RankRecord
	global ConsumeRecord
	global OldConsumeRecord

	Pre20RankRecord = {}
	ConsumeRecord 	= {}
	OldConsumeRecord = {}

def SaveGlobalData():
	'''
	全局数据持久化
	'''
	global Pre20RankRecord
	global ConsumeRecord
	global OldConsumeRecord

	#记录天数，用于跨天数据清空
	days = cDateTime.Days()
	GlobalHttp.SetGlobalData( GlobalDataDefine.D12GroupBuy,(days,{1:Pre20RankRecord,2:ConsumeRecord,3:OldConsumeRecord}))	#(天数,{1:前20排行,2:全服消费记录,3:逻辑服务器历史数据)

def GetDiscount(index,count):
	'''
	计算差价
	'''
	secondDict = PassionActDiscount.get(index)
	if not secondDict:
		return 0

	maxRnum = 0
	for rnum,_ in secondDict.iteritems():
		if count >= rnum:
			maxRnum = max(maxRnum,rnum)

	item_cfg = PassionActD12GB_Dict.get(index)
	if not item_cfg:
		print "GE_EXC, no cfg in PassionActD12GB_Dict index(%s),count(%s)"%(index,count)
		return 0

	price = item_cfg.needRMB
	
	#没有达到折扣最低条件,不打折
	if not maxRnum:
		return 0
	#团购价-根据人数优惠后价格
	price -= secondDict.get(maxRnum,0)
	if price < 0:
		print "GE_EXC, Discount is less than 0 in PassionActDiscount index(%s),count(%s)"%(index,count)

	return price

def GetLogicData(conSumedict):
	'''
	格式转换{index:[(roleid,time)]} ---> {index:cnt}
	'''
	tempDict = {}

	for index,roleList in conSumedict.iteritems():
		#人数潜规则5倍
		tempDict[index] = len(roleList)*5

	return tempDict

def InitRecdordData():
	GlobalHttp.GetGlobalData( GlobalDataDefine.D12GroupBuy, OnGetRecordData)

def OnGetRecordData(response, regparam):
	'''
	全局数据载入回调
	'''
	if response is None:
		#自返回
		return

	global Pre20RankRecord
	global ConsumeRecord
	global OldConsumeRecord
	
	#还没有数据
	if not response:
		pass
	else:
	#分析和处理数据
		old_days,datadict = response
		days = cDateTime.Days()

		#同一天
		if old_days == days:
			Pre20RankRecord = datadict.get(1,{})
			ConsumeRecord = datadict.get(2,{})
			OldConsumeRecord = datadict.get(3,{})
		else:
			#跨天清空
			Pre20RankRecord = {}
			ConsumeRecord = {}
			OldConsumeRecord = {}

	#已经载入成功了
	global ReturnDB
	ReturnDB = True
	#同步数据给所有的逻辑进程
	if response:
		SyncAllLogin()

def SyncAllLogin():
	#同步数据给所有的逻辑进程
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)
	
	global ConsumeRecord
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		
		#同步给逻辑进程字典格式{index:cnt}
		SyncLogicProcess(sessionid)

def SyncLogicProcess(sessionid):
	if sessionid in ProcessMgr.ControlProcesssSessions.keys():
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_LogicSendD12GroupBuyData, GetLogicData(ConsumeRecord))

def NotifyCleanLogic():
	'''
	通知逻辑进程清空本服数据
	控制进程驱动清空逻辑进程数据，假如逻辑服务器此时不在线则需要等到起服清空
	'''
	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)

	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		#同步给逻辑进程字典格式{index:cnt}
		ControlProxy.SendLogicMsg(sessionid, PyMessage.Control_CleanLogicGroupBuyData, None)
	
def AfterNewHour():
	'''
	每整点Tick
	'''
	#每一个整点向所有的逻辑进程请求每一个服务器的玩家数据，等待回调并且记录数据
	#如果有某些逻辑进程没有返回或者其他原因导致了这个回调是自回调的。这个时候，就会使用上一个小时
	#的旧数据代替这个一个服的数据。
	
	#所有的回调都完毕后，触发对这些玩家数据排序出前20名。并且http请求更新到数据库
	if not IsStart:
		#活动没有开启
		return
	
	#更新当天标记
	global TodayFlag
	TodayFlag = cDateTime.Days()
	
	nowHour = cDateTime.Hour()
	global ReturnDB
	if ReturnDB is False:
		print "GE_EXC, PassionbActD12GroupBuyControl AfterNewHour error not ReturnDB"
		#数据没有载回, 尝试再次载入
		InitRecdordData()
		return
	
	if nowHour == 0:
		#0点的时候只发奖，操作数据库数据
		RequestLogicData(True)
	else:
		#向逻辑进程请求数据,并且进行排序，写入数据库，把最新的排序更新到逻辑进程
		RequestLogicData(False)

def NewDayRewardRoles():
	'''
	每日结算奖励
	'''
	
	global Pre20RankRecord
	#发放前20名奖励
	maildatas = []
	for item_index, item_info in Pre20RankRecord.iteritems():
		#获取物品index配置
		itemcfg = PassionActD12GB_Dict.get(item_index)
		if not itemcfg:
			print "GE_EXE, no cfg in PassionActD12GB_Dict index(%s)"%item_index
			continue
		
		#coding,_ = itemcfg.reward
		#name = 
		for index, roleid in enumerate(item_info):
			#礼包奖励
			item_reward = {}
			item_reward[EnumMail.EnumItemsKey] = itemcfg.reward
			
			#coding
			
			rolemaildata = (roleid, GlobalPrompt.D12GroupBuyPre20_Title, GlobalPrompt.D12GroupBuyPre20_Sender, GlobalPrompt.D12GroupBuyPre20_Content % itemcfg.item_name, AutoLog.traD12GroupBuyPre20, item_reward)
			maildatas.append(rolemaildata)
	
	#发送排行前20邮件奖励
	GlobalHttp.SendRoleMail(maildatas)
	
	maildatas = []
	#补差价
	for index,rlist in ConsumeRecord.iteritems():
		rcnt = len(rlist)*5
		#获取物品index配置
		itemcfg = PassionActD12GB_Dict.get(index)
		#计算差价
		discount  = GetDiscount(index,rcnt)
		if discount > 0:
			#roles = secondDict.get(2,set())
			for roleid in rlist:
				#奖励神石
				rmb_reward = {}
				rmb_reward[EnumMail.EnumUnbindRMBKey] = discount
				rolemaildata = (roleid, GlobalPrompt.D12GroupBuyDiscount_Title, GlobalPrompt.D12GroupBuyDiscount_Sender, GlobalPrompt.D12GroupBuyDiscount_Content % (itemcfg.item_name,itemcfg.needRMB,rcnt), AutoLog.traD12GroupBuy, rmb_reward)
				maildatas.append(rolemaildata)
			
	#发送补差价邮件奖励
	GlobalHttp.SendRoleMail(maildatas)

def OnLogicRequested(sessionid,msg):
	SyncLogicProcess(sessionid)

def RequestLogicData(isClean):
	'''
	@向所有的逻辑进程获取排行榜数据
	@isClean 是否清空逻辑进程数据
	'''
	#global Pre20RankRecord
	
	global ConsumeRecord
	ConsumeRecord = {}

	global TotalLogicCnt
	TotalLogicCnt = len(ProcessMgr.ControlProcesssSessions)

	global TodayFlag
	request_day = TodayFlag
	if isClean : 
		request_day  = request_day - 1
	
	for sessionid, cp in ProcessMgr.ControlProcesssSessions.iteritems():
		if cp.processid >= 30000:
			#跨服服务器不处理
			TotalLogicCnt -= 1
			continue
		ControlProxy.SendLogicMsgAndBack(sessionid, PyMessage.Control_RequestD12GroupBuyData, request_day, LogicDataBack, isClean)

def LogicDataBack(callargv, regparam):
	'''
	@逻辑进程返回或者自返回
	@callargv-->serverid,{index:[(roleid,time)]}
	'''
	
	global OldConsumeRecord
	global TotalLogicCnt
	TotalLogicCnt -= 1

	if callargv:
		#更新历史数据
		processId,tempDict = callargv
		OldConsumeRecord[processId] = tempDict

	if TotalLogicCnt == 0:
		#所有的逻辑进程已经返回了排行榜,对排行榜进行排序,然后更新到数据库
		SortAndUpdataRank()
		#每日0点逻辑
		if regparam:
			#发送奖励
			NewDayRewardRoles()
			#清空缓存
			CleanCacheData()
			#通知逻辑进程清空本服数据
			NotifyCleanLogic()
		#同步数据到逻辑进程	
		SyncAllLogin()
		#每一小时做持久化
		SaveGlobalData()

	elif TotalLogicCnt < 0:
		print "GE_EXC, error in PassionbActD12GroupBuyControl LogicDataBack (%s)" % TotalLogicCnt

def SortAndUpdataRank():
	'''
	更新每件商品前20名购买玩家
	更新全服消费记录排序
	'''
	#更新前20购买玩家排名
	global Pre20RankRecord
	Pre20RankRecord = {}

	#前20字典(包含时间戳)
	tempPre20RankDict = {}
	tempConsumeRecord = {}

	#[step 1]fetch所有逻辑服务器数据
	for _,tempDict in OldConsumeRecord.iteritems():
		for item_index,rank_list in tempDict.iteritems():
			ItemPre20List = tempPre20RankDict[item_index] = tempPre20RankDict.get(item_index,[])
			ItemList = tempConsumeRecord[item_index] = tempConsumeRecord.get(item_index,[])
			#合并每个服务器前20名玩家
			ItemPre20List.extend(rank_list[:20])
			ItemList.extend(rank_list)

	#[step 2]update前20名、全服消费记录
	for item_index,rank_list in tempPre20RankDict.iteritems():
		rank_list.sort(key = lambda x:x[1], reverse = False)
		rank_list = rank_list[:20]
		#过滤时间戳
		Pre20RankRecord[item_index] = [ roleid for (roleid,_) in rank_list]

	global ConsumeRecord
	ConsumeRecord = {}

	for item_index, roleList in tempConsumeRecord.iteritems():
		#过滤时间戳
		ConsumeRecord[item_index] = [ roleid for (roleid,_) in roleList]

if "_HasLoad" not in dir():
	if Environment.HasControl:
		LoadD12GroupBuyActiveConfig()
		LoadD12GBConfig()
		InitRecdordData()
		CheckActivity()
		
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		#逻辑进程请求团购数据
		cComplexServer.RegDistribute(PyMessage.Control_RequestControlD12GroupBuyData, OnLogicRequested)