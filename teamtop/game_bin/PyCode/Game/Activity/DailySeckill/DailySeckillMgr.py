#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DailySeckill.DailySeckillMgr")
#===============================================================================
# 天天秒杀
#===============================================================================
import cRoleMgr
import cNetMessage
import Environment
import cDateTime
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from Game.Persistence import Contain
from Common.Message import AutoMessage
from Game.SysData import WorldData
from Game.Role import Event
from Game.Role.Data import EnumCD
from Common.Other import GlobalPrompt, EnumGameConfig
from Game.Activity import CircularDefine
from Game.Activity.DailySeckill import DailySeckillConfig

if "_HasLoad" not in dir():
	__IS_START = False			#活动开启控制
	Role_Open_Panel_List = []	#打开面板的玩家id列表
	TimeToTimes = {12:1, 13:2, 14:3, 15:4, 16:5, 17:6, 18:7, 19:8, 20:9, 21:10}	#当前时间对应的天天秒杀的波次
	
	#消息
	RefreshDailySeckill = AutoMessage.AllotMessage('RefreshDailySeckill', '刷新每日秒杀的物品')#每小时刷新
	SyncDailySeckillData = AutoMessage.AllotMessage('SyncDailySeckillData', '同步每日秒杀可购买物品数量')#每次有玩家成功秒杀后同步
	#日志
	Tra_DailySeckill = AutoLog.AutoTransaction('Tra_DailySeckill', '参加天天秒杀交易成功 ')
#=============================================================================================
def DailySeckillStart(*param):
	'''
	天天秒杀活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_DailySeckill:
		return
	global __IS_START
	if __IS_START is True:
		print "GE_EXC, DailySeckill has already been started"
		return
	__IS_START = True

def DailySeckillEnd(*param):
	'''
	天天秒杀活动关闭
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_DailySeckill:
		return
	global __IS_START
	if __IS_START is False:
		print "GE_EXC, DailySeckill has already been ended"
		return
	__IS_START = False
	global DailySecKill_Goods_Dict
	DailySecKill_Goods_Dict.clear()

#=============================================================================================

def GlobalTellStart():
	'''
	全服公告當日秒杀开始
	'''
	if __IS_START is False:
		return
	#全服公告，秒杀开始
	cRoleMgr.Msg(1, 0, GlobalPrompt.DailySeckill_StartTips)

def GlobalTellGetReady():
	'''
	全服公告请做好准备
	'''
	if __IS_START is False:
		return
	#全服公告，请做好准备
	cRoleMgr.Msg(1, 0, GlobalPrompt.DailySeckill_GetReadyTips)
	
def GlobalTellPerHour():
	'''
	每小时刷新前的全服公告
	'''
	if __IS_START is False:
		return
	#根据当前的时间取出接下来的波数
	times = TimeToTimes.get(cDateTime.Hour() + 1)#这里是在活动开始前1分钟，故小时数要增加一个小时
	cRoleMgr.Msg(1, 0, GlobalPrompt.DailySeckill_TimesTips % times)
	

def DailySeckillRefresh():
	'''
	刷新天天秒杀商城里的物品
	'''
	if __IS_START is False:
		return
	#首先更新物品字典
	DailySecKill_Goods_Dict_Update()
	#全服广播消息，通知商店已经刷新
	cNetMessage.PackPyMsg(RefreshDailySeckill, None)
	cRoleMgr.BroadMsg()
	#全服都要更新物品数量的,这里只给打开了面板的玩家发送消息
	for memberid in Role_Open_Panel_List:
		member = cRoleMgr.FindRoleByRoleID(memberid)
		#如果玩家在线的话
		if member:
			member.SendObj(SyncDailySeckillData, DailySecKill_Goods_Dict.data)
		else:
			Role_Open_Panel_List.remove(memberid)


def DailySecKill_Goods_Dict_Update():
	'''
	更新用来存储商品及数量的DailySecKill_Goods_Dict
	'''
	if __IS_START is False:
		return
	#首先清空物品字典
	global DailySecKill_Goods_Dict
	#如果存在物品的話首先清空
	if DailySecKill_Goods_Dict.data:
		DailySecKill_Goods_Dict.clear()
	#随机生成新的物品字典
	config_list = __GetRandomItemIndex(8)
	if config_list == None:
		return
	for index in config_list:
		cfg = DailySeckillConfig.DailySeckillConfig_Dict.get(index)
		if not cfg:
			print "GE_EXC, error in cfg = DailySeckillConfig.DailySeckillConfig_Dict.get(index),no such index(%s)" % index
			return
		DailySecKill_Goods_Dict[index] = cfg.Cnt

def RequestBuySomething(role, msg):
	'''
	客户端请求购买天天秒杀里的物品 
	@param role:
	@param msg:
	'''
	if __IS_START is False:
		return
	#只能在这个时间区间秒杀物品 
	if not 12 <= cDateTime.Hour() < 22:
		return
	if role.GetLevel() < EnumGameConfig.DailySeckillNeedLevel:
		return
	#cd时间还没到 
	cdTime = role.GetCD(EnumCD.DailySeckillCD)
	if cdTime > 0:
		role.Msg(2, 0, GlobalPrompt.DailySeckill_CDTips % cdTime)
		return
	#客户端请求购买物品 
	index = msg
	#如果当前正在出售的物品里没有请求的交易
	if not index in DailySecKill_Goods_Dict:
		return
	#当前某个交易物品已经数量不足了
	if DailySecKill_Goods_Dict.get(index) <= 0:
		role.Msg(2, 0, GlobalPrompt.DailySeckill_SlowTips)
		return

	cfg = DailySeckillConfig.DailySeckillConfig_Dict.get(index)
	if not cfg:
		print "GE_EXC,error in cfg = DailySeckillConfig.DailySeckillConfig_Dict.get(index),no such index(%s)" % index
		return
	#玩家的神石不足
	#如果可以使用奖励神石的话
	if cfg.CanSysRMB == 1:
		if cfg.Price > role.GetUnbindRMB():
			return
	#如果不能使用奖励神石的话
	else:
		if cfg.Price > role.GetUnbindRMB_Q():
			return
	#如果玩家的背包或者命魂背包已满，提示并返回
	if role.PackageIsFull():
		role.Msg(2, 0, GlobalPrompt.DailySeckill_PackageFulltips)
		return
	if role.TarotPackageIsFull():
		role.Msg(2, 0, GlobalPrompt.DailySeckill_PackageFulltips)
		return
	#如果天赋卡背包已满，提示并返回
	if role.GetTalentEmptySize() < 1:
		role.Msg(2, 0, GlobalPrompt.DailySeckill_PackageFulltips)
		return
	itemcode = 0
	itemcnt = 0
	with Tra_DailySeckill:
		#如果可以使用奖励神石
		if cfg.CanSysRMB == 1:
			role.DecUnbindRMB(cfg.Price)
		#如果不能使用奖励神石
		else:
			role.DecUnbindRMB_Q(cfg.Price)
			
		DailySecKill_Goods_Dict[index] -= 1
		role.SetCD(EnumCD.DailySeckillCD, EnumGameConfig.DailySeckillCD)
		#如果是普通物品
		if cfg.Type == 1:
			role.AddItem(*cfg.ItemCode)
			#物品类型不同，奖励公告也有区别
			itemcode, itemcnt = cfg.ItemCode
			personaltips = GlobalPrompt.DailySeckill_PersonalItemtips
			globaltips = GlobalPrompt.DailySeckill_PreciousItemTips
		#如果是命魂
		elif cfg.Type == 2:
			role.AddItem(*cfg.ItemCode)
			itemcode, itemcnt = cfg.ItemCode
			#物品类型不同，奖励公告也有区别
			personaltips = GlobalPrompt.DailySeckill_PersonalTarottips
			globaltips = GlobalPrompt.DailySeckill_PreciousTarotTips
		#天赋卡
		elif cfg.Type == 3:
			itemcode = cfg.ItemCode[0]
			itemcnt = cfg.ItemCode[1]
			#天賦卡只能一張一張加
			for _ in xrange(itemcnt):
				role.AddTalentCard(itemcode)
			#物品类型不同，奖励公告也有区别
			personaltips = GlobalPrompt.DailySeckill_PersonalTalenttips
			globaltips = GlobalPrompt.DailySeckill_PreciousTalentTips
		else:
			return

	#全服都要更新物品数量的,这里只给打开了面板的玩家发送消息
	for memberid in Role_Open_Panel_List:
		member = cRoleMgr.FindRoleByRoleID(memberid)
		#如果玩家在线的话
		if member:
			member.SendObj(SyncDailySeckillData, DailySecKill_Goods_Dict.data)
	#弹出提示
	role.Msg(2, 0, personaltips % (itemcode, itemcnt))
	#如果整个物品需要广播的话
	if cfg.IsBroadcast == 1:
		cRoleMgr.Msg(1, 0, globaltips % (role.GetRoleName(), itemcode, itemcnt))

def __GetRandomItemIndex(cnt):
	'''
	获取随机物品交易编号
	@param cnt:获取随机物品的数量
	'''
	if __IS_START is False:
		return
	#首先获取当前的世界等级
	worldlevel = WorldData.GetWorldLevel()
	#获取当前的世界等级区间
	#先把存有世界等级区间最大世界等级的列表复制过来
	world_level_section_list = list(DailySeckillConfig.DailySeckillWLS_List)
	#如果当前世界等级不在这个列表里，就把它插进去
	if worldlevel not in world_level_section_list:
		world_level_section_list.append(worldlevel)
	#排序
	world_level_section_list.sort()
	#取出世界等级区间
	section = world_level_section_list.index(worldlevel) + 1
	#根据世界等级区间取出当前的配置
	cfg = DailySeckillConfig.DailySeckillWLSConfig_Dict.get(section)
	if not cfg:
		print "GE_EXC, error in cfg = DailySeckillConfig.DailySeckillWLSConfig_Dict.get(section), no such section(%s)" % section
		return None
	return cfg.GetRandom(cnt)

def RequestOpenPanel(role, msg):
	'''
	客户端请求打开面板
	@param role:
	@param msg:
	'''
	if __IS_START is False:
		return
	#如果商品字典是空的，首先更新商品字典
	if not DailySecKill_Goods_Dict.data:
		DailySecKill_Goods_Dict_Update()
	#等级限制
	if role.GetLevel() < EnumGameConfig.DailySeckillNeedLevel:
		return
	#玩家的id放入到当前打开面板的玩家id列表里
	if not role.GetRoleID() in Role_Open_Panel_List:
		Role_Open_Panel_List.append(role.GetRoleID())
	role.SendObj(SyncDailySeckillData, DailySecKill_Goods_Dict.data)

def RequestClosePanel(role, msg):
	'''
	客户端请求关闭面板
	@param role:
	@param msg:
	'''
	if __IS_START is False:
		return
	RoleClosePanel(role)

def OnClientLostorExit(role, param):
	'''
	客户端掉线或退出的处理 
	@param role:
	@param param:
	'''	
	if __IS_START is False:
		return
	RoleClosePanel(role)

def RoleClosePanel(role):
	'''
	关闭面板处理，将玩家id从Role_Open_Panel_List移除
	@param role:
	'''
	if __IS_START is False:
		return
	roleId = role.GetRoleID()
	if roleId in Role_Open_Panel_List:
		Role_Open_Panel_List.remove(roleId)

if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		#当前可以秒杀物品的数量统统放在这个持久化字典里面{index->cnt}
		DailySecKill_Goods_Dict = Contain.Dict("DailySecKill_Goods_Dict", (2038, 1, 1), None, None)
	if Environment.HasLogic and not Environment.IsCross:
#		#每天12点发出全服公告 
		Cron.CronDirveByHour((2038, 1, 1), GlobalTellStart, H="H == 12")
#		#每小时刷新秒杀物品
		Cron.CronDirveByHour((2038, 1, 1), DailySeckillRefresh, H="H in xrange(13, 23)")
#		#活动开始前15分钟的通知
		Cron.CronDriveByMinute((2038, 1, 1), GlobalTellGetReady, H="H == 11", M="M == 45")
		#每波活动开始前1分钟发出公告
		Cron.CronDriveByMinute((2038, 1, 1), GlobalTellPerHour, H="H in xrange(11, 21)", M="M == 59")
		#事件
		Event.RegEvent(Event.Eve_ClientLost, OnClientLostorExit)
		Event.RegEvent(Event.Eve_BeforeExit, OnClientLostorExit)
		Event.RegEvent(Event.Eve_StartCircularActive, DailySeckillStart)
		Event.RegEvent(Event.Eve_EndCircularActive, DailySeckillEnd)

		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_Dailyseckill_buy", "客户端请求每日秒杀购买物品 "), RequestBuySomething)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_Dailyseckill_OpenPanel", "客户端请求打开每日秒杀面板 "), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_Dailyseckill_ClosePanel", "客户端请求关闭每日秒杀面板 "), RequestClosePanel)
