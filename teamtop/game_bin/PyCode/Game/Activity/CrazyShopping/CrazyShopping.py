#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.CrazyShopping.CrazyShopping")
#===============================================================================
# 疯狂抢购乐,这个活动只有繁体才会有
#===============================================================================
import time
import datetime
import cRoleMgr
import cDateTime
import cNetMessage
import DynamicPath
import Environment
import cComplexServer
from Game.Role import Event
from Util.File import TabFile
from Game.Role.Data import EnumCD
from ComplexServer.Time import Cron
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Persistence import Contain
from Common.Other import GlobalPrompt
from Game.Activity.CrazyShopping import CrazyShoppingConfig

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("CrazyShopping")
	
	IsStart = False
	NeedLevel = 30
	
	Role_Open_Panel_Set = set()		#打开面板的角色id集合
	
	#消息
	CrazyShoppingIsStart = AutoMessage.AllotMessage("CrazyShoppingIsStart", "疯狂抢购乐活动点开启情况")
	SyncCrazyShoppingData = AutoMessage.AllotMessage("SyncCrazyShoppingData", "疯狂抢购乐物品购买情况")
	SyncCrazyShoppingOnOffer = AutoMessage.AllotMessage("SyncCrazyShoppingOnOffer", "疯狂抢购乐正在出售物品")
	SyncCrazyShoppingLuckList = AutoMessage.AllotMessage("SyncCrazyShoppingLuckList", "同步疯狂抢购乐幸运榜")
	
	#日志
	Tra_CrazyShopping = AutoLog.AutoTransaction('Tra_CrazyShopping', '疯狂抢购乐交易 ')
	

class CrazyShoppingActiveConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath("CrazyShoppingActive.txt")
	def __init__(self):
		self.beginTime = eval				#开始时间
		self.endTime = eval					#结束时间
	
	def Active(self):
		#开始时间戳
		beginTime = int(time.mktime(datetime.datetime(*self.beginTime).timetuple()))
		#结束时间戳
		endTime = int(time.mktime(datetime.datetime(*self.endTime).timetuple()))
		#当前时间戳
		nowTime = cDateTime.Seconds()
		
		if beginTime <= nowTime < endTime:
			#在开始和结束时间戳之间, 激活
			Start(None, None)
			cComplexServer.RegTick(endTime - nowTime, End)
		elif nowTime < beginTime:
			#在开始时间戳之前
			cComplexServer.RegTick(beginTime - nowTime, Start)
			cComplexServer.RegTick(endTime - nowTime, End)


def LoadCrazyShoppingActiveConfig():
	for cfg in CrazyShoppingActiveConfig.ToClassType():
		if cfg.beginTime > cfg.endTime:
			print "GE_EXC, beginTime > endTime in CrazyShoppingActive"
			return
		#无依赖, 起服触发
		cfg.Active()


def Start(callargv, param):
	'''
	'''
	global IsStart
	if IsStart is True:
		return
	IsStart = True
	
	cNetMessage.PackPyMsg(CrazyShoppingIsStart, IsStart)
	cRoleMgr.BroadMsg()


def End(callargv, param):
	'''
	'''
	global IsStart
	if IsStart is False:
		return
	IsStart = False
	global CrazyShopping_Goods_Dict, CrazyShopping_LuckList
	CrazyShopping_Goods_Dict.clear()
	CrazyShopping_LuckList.clear()
	cNetMessage.PackPyMsg(CrazyShoppingIsStart, IsStart)
	cRoleMgr.BroadMsg()
	
	
def GetCurrentOnOffer():
	'''
	获取当前正在出售的商品id
	'''
	date = cDateTime.Day()
	month = cDateTime.Month()
	config = CrazyShoppingConfig.CrazyShoppingDateDict.get((month, date))
	if config is None:
		return None
	return config.index
	
	
def RequestBuy(role, msg):
	'''
	客户端请求购买疯狂抢购乐里的物品 
	@param role:
	@param msg:
	'''
	if IsStart is False:
		return
	if not 12 <= cDateTime.Hour() <= 21:
		return
	if role.GetLevel() < NeedLevel:
		return
	
	cdTime = role.GetCD(EnumCD.CrazyShoppingCD)
	if cdTime > 0:
		role.Msg(2, 0, GlobalPrompt.CrazyShoppingCD)
		return
	index = msg
	onOffer = GetCurrentOnOffer()
	
	if index != onOffer:
		role.Msg(2, 0, "你不能购买一个没有在出售的物品")
		return
	
	config = CrazyShoppingConfig.CrazyShoppingConfigDict.get(onOffer)
	if config is None:
		return
	
	global CrazyShopping_Goods_Dict
	nowCnt = CrazyShopping_Goods_Dict.get(index, 0)
	if nowCnt >= config.limit:
		return
	
	if role.PackageIsFull():
		role.Msg(2, 0, GlobalPrompt.PackageIsFull_Tips)
		return
	
	with Tra_CrazyShopping:
		role.SetCD(EnumCD.CrazyShoppingCD, 3)
		CrazyShopping_Goods_Dict[index] = CrazyShopping_Goods_Dict.get(index, 0) + 1
		role.DecUnbindRMB(config.price)
		role.AddItem(config.coding, 1)
	
	global CrazyShopping_LuckList
	roleName = role.GetRoleName()
	CrazyShopping_LuckList.append((roleName, (config.coding, 1)))
	role.SendObj(SyncCrazyShoppingLuckList, CrazyShopping_LuckList.data)
	#全服都要更新物品数量的,这里只给打开了面板的玩家发送消息
	for memberid in Role_Open_Panel_Set:
		member = cRoleMgr.FindRoleByRoleID(memberid)
		#如果玩家在线的话
		if member:
			member.SendObj(SyncCrazyShoppingData, CrazyShopping_Goods_Dict.data)
	
	role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (config.coding, 1))
	cRoleMgr.Msg(1, 0, GlobalPrompt.CrazyShoppingGlobalTell % (role.GetRoleName(), config.coding, 1))


def RequestOpenPanel(role, msg):
	'''
	客户端请求打开面板
	@param role:
	@param msg:
	'''
	if IsStart is False:
		return

	if role.GetLevel() < NeedLevel:
		return
	
	#玩家的id放入到当前打开面板的玩家id列表里
	roleId = role.GetRoleID()
	Role_Open_Panel_Set.add(roleId)
	
	role.SendObj(SyncCrazyShoppingOnOffer, GetCurrentOnOffer())
	role.SendObj(SyncCrazyShoppingData, CrazyShopping_Goods_Dict.data)
	role.SendObj(SyncCrazyShoppingLuckList, CrazyShopping_LuckList.data)


def RequestClosePanel(role, msg):
	'''
	客户端请求关闭面板
	@param role:
	@param msg:
	'''
	if IsStart is False:
		return
	RoleClosePanel(role)


def OnClientLostorExit(role, param):
	'''
	客户端掉线或退出的处理 
	@param role:
	@param param:
	'''	
	if IsStart is False:
		return
	if role.GetLevel() < NeedLevel:
		return
	RoleClosePanel(role)


def RoleClosePanel(role):
	'''
	关闭面板处理
	@param role:
	'''
	roleId = role.GetRoleID()
	Role_Open_Panel_Set.discard(roleId)


def GlobalTellGetReady1():
	'''
	'''
	if IsStart is False:
		return
	#全服公告，请做好准备
	cRoleMgr.Msg(1, 0, GlobalPrompt.CrazyShoppingGetReady1)


def GlobalTellGetReady2():
	'''
	'''
	if IsStart is False:
		return
	#全服公告，请做好准备
	cRoleMgr.Msg(1, 0, GlobalPrompt.CrazyShoppingGetReady2)


def GlobalTellGetReady3():
	'''
	'''
	if IsStart is False:
		return
	#全服公告，请做好准备
	cRoleMgr.Msg(1, 0, GlobalPrompt.CrazyShoppingGetReady3)
	

def OnSyncRoleOtherData(role, param):
	'''
	同步角色其它数据
	'''
	if IsStart is False:
		return
	role.SendObj(CrazyShoppingIsStart, IsStart)



def BeforeSave():
	'''
	幸运榜只保存最近的20人
	'''
	if len(CrazyShopping_LuckList) <= 20:
		return
	CrazyShopping_LuckList.data = CrazyShopping_LuckList[:20]
	CrazyShopping_LuckList.HasChange()


if "_HasLoad" not in dir():
	if Environment.HasLogic and (Environment.EnvIsFT() or Environment.IsDevelop) and not Environment.IsCross:
		
		LoadCrazyShoppingActiveConfig()
		#当前可以秒杀物品的数量统统放在这个持久化字典里面{index->cnt}
		CrazyShopping_Goods_Dict = Contain.Dict("CrazyShopping_Goods_Dict", (2038, 1, 1), None, None)
		CrazyShopping_LuckList = Contain.List("CrazyShopping_LuckList", (2038, 1, 1), None, beforeSaveFun=BeforeSave)
		
		Cron.CronDriveByMinute((2038, 1, 1), GlobalTellGetReady1, H="H == 11", M="M == 50")
		Cron.CronDriveByMinute((2038, 1, 1), GlobalTellGetReady2, H="H == 11", M="M == 55")
		Cron.CronDriveByMinute((2038, 1, 1), GlobalTellGetReady3, H="H == 11" , M="M == 59")
		
		#事件
		Event.RegEvent(Event.Eve_ClientLost, OnClientLostorExit)
		Event.RegEvent(Event.Eve_BeforeExit, OnClientLostorExit)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_CrazyShopping_buy", "客户端请求每日秒杀购买物品 "), RequestBuy)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_CrazyShopping_OpenPanel", "客户端请求打开每日秒杀面板 "), RequestOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_CrazyShopping_ClosePanel", "客户端请求关闭每日秒杀面板 "), RequestClosePanel)

