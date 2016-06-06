#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Christmas.ChristmasWishTreeMgr")
#===============================================================================
# 圣诞许愿树Mgr
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Activity import CircularDefine
from Game.Activity.Christmas import ChristmasWishTreeConfig
from Game.Role.Data import EnumObj, EnumInt16, EnumDayInt1, EnumDayInt8,\
	EnumInt32

#数据index
GOODID_IDX = 0
CODING_IDX = 1
CNT_IDX = 2
ITEMCNT_IDX = 3
NEEDUNBINDRMB_IDX = 4
RMBTYPE_IDX = 5
NEEDSOCKCNT_IDX = 6

#刷新类型
REFRESHTYPE_SYSTEM = 0
REFRESHTYPE_ROLE = 1

if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_ChristmasWishTree_RefreshShelf_Role = AutoLog.AutoTransaction("Tra_ChristmasWishTree_RefreshShelf_Role", "圣诞许愿树手动刷新货架商品") 
	Tra_ChristmasWishTree_RefreshShelf_System = AutoLog.AutoTransaction("Tra_ChristmasWishTree_RefreshShelf_System", "圣诞许愿树自动刷新货架商品")
	Tra_ChristmasWishTree_BuyGood = AutoLog.AutoTransaction("Tra_ChristmasWishTree_BuyGood", "圣诞许愿树购买货架商品")
	
	ChristmasWishTree_GoodsShelf_Sync = AutoMessage.AllotMessage("ChristmasWishTree_GoodsShelf_Sync", "圣诞许愿树_同步货架商品")

#### 活动控制  start ####
def OnStartWishTree(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_ChristmasWishTree != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open WishTree"
		return
		
	IS_START = True

def OnEndWishTree(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_ChristmasWishTree != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end WishTree while not start"
		return
		
	IS_START = False

#### 请求start ####
def OnOpenPanel(role, msg = None):
	'''
	请求打开面板 此处维护玩家
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.ChristmasWishTree_NeedLevel:
		return
	
	hasSync = RefreshAndSyncShelf(role)
	if not hasSync:
		role.SendObj(ChristmasWishTree_GoodsShelf_Sync, role.GetObj(EnumObj.ChristmasActive)[1])
	
def OnRefreshShelf(role, msg = None):
	'''
	请求刷新许愿树货架
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.ChristmasWishTree_NeedLevel:
		return
	
	refreshCntToday = role.GetDI8(EnumDayInt8.ChristmasWishTreeRefreshCnt) + 1
	needSockCnt = ChristmasWishTreeConfig.GetSockCntByRefreshCnt(refreshCntToday)
	if role.ItemCnt(EnumGameConfig.ChristmasWishTree_SockCoding) < needSockCnt:
		return
	
	#process
	with Tra_ChristmasWishTree_RefreshShelf_Role:
		#扣袜子
		role.DelItem(EnumGameConfig.ChristmasWishTree_SockCoding, needSockCnt)
		#增加今日刷新次数
		role.IncDI8(EnumDayInt8.ChristmasWishTreeRefreshCnt, 1)
		#刷新货架
		RefreshShelf(role, REFRESHTYPE_ROLE)
	
	#同步最新货架商品信息
	role.SendObj(ChristmasWishTree_GoodsShelf_Sync, role.GetObj(EnumObj.ChristmasActive)[1])

def OnBuyGoods(role, msg):
	'''
	请求购买许愿树货架商品 
	@param msg: goodId
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.ChristmasWishTree_NeedLevel:
		return
	
	#没有目标商品配置
	targetGoodId, buyCnt = msg
	targetGoodCfg = ChristmasWishTreeConfig.GetGoodCfgByID(targetGoodId)
	if not targetGoodCfg:
		return
	
	#目标商品不在当前货架  或者 剩余购买数量不足
	shelfGoodsDict = role.GetObj(EnumObj.ChristmasActive)[1]
	if targetGoodId not in shelfGoodsDict or shelfGoodsDict[targetGoodId] < buyCnt:
		return
	
	RMBType = targetGoodCfg.RMBType
	needUnbindRMB = targetGoodCfg.needUnbindRMB * buyCnt
	RMBSatisifyFlag = True
	#奖励神石和充值神石均可
	if not RMBType:
		if needUnbindRMB and role.GetUnbindRMB() < needUnbindRMB:
			RMBSatisifyFlag = False
		else:
			pass
	else:
		if needUnbindRMB and role.GetUnbindRMB_Q() < needUnbindRMB:
			RMBSatisifyFlag = False
		else:
			pass
	
	#神石不满足
	if not RMBSatisifyFlag:
		return
	
	#袜子不足
	needSockCnt = targetGoodCfg.needSockCnt * buyCnt
	if needSockCnt and role.ItemCnt(EnumGameConfig.ChristmasWishTree_SockCoding) < needSockCnt:
		return
	
	#process
	coding, cnt = targetGoodCfg.item
	with Tra_ChristmasWishTree_BuyGood:
		#扣钱加积分
		if needUnbindRMB > 0:
			if RMBType:
				role.DecUnbindRMB_Q(needUnbindRMB)
			else:
				role.DecUnbindRMB(needUnbindRMB)
			role.IncI32(EnumInt32.ChristmasConsumeExp, needUnbindRMB)
		else:
			pass
		#扣袜子
		if needSockCnt > 0:
			role.DelItem(EnumGameConfig.ChristmasWishTree_SockCoding, needSockCnt)
		else:
			pass
		#更新货架商品状态
		shelfGoodsDict[targetGoodId] -= buyCnt
		role.GetObj(EnumObj.ChristmasActive)[1] = shelfGoodsDict
		#获得物品
		role.AddItem(coding, cnt)
		
	#获得提示
	prompt = GlobalPrompt.ChristmasWishTree_Tips_Head + GlobalPrompt.ChristmasWishTree_Tips_Item % (coding, cnt)
	role.Msg(2, 0, prompt)
	#积分提示
	if needUnbindRMB > 0:
		role.Msg(2, 0, GlobalPrompt.Christmas_Tips_ConsumeEXp % needUnbindRMB)
	#同步最新货架商品状态
	role.SendObj(ChristmasWishTree_GoodsShelf_Sync, role.GetObj(EnumObj.ChristmasActive)[1])

#helper start
def RefreshAndSyncShelf(role):
	'''
	判断role是否需要重置 
	若需要则重置并同步到客户端并返回True 
	否则返回False
	'''
	curDay = cDateTime.Days()
	curHour = cDateTime.Hour()
	lastRefreshDay = role.GetI16(EnumInt16.ChristmasWishTreeRefreshDay)
	refreshFlag = role.GetDI1(EnumDayInt1.ChristmasWishTreeRefreshFlag)
	
	needRefresh = False
	#今天以前的刷新
	if lastRefreshDay < curDay:
		needRefresh = True
	elif lastRefreshDay == curDay:
		#现在超过12点了 并且 标志位表明今日还没有刷新
		if curHour >= 12 and not refreshFlag:
			needRefresh = True
		else:
			pass
	else:
		pass
	
	#是否需要刷新分别处理 再返回
	if not needRefresh:
		return  False
	else:
		RefreshShelf(role, REFRESHTYPE_SYSTEM)
		role.SendObj(ChristmasWishTree_GoodsShelf_Sync, role.GetObj(EnumObj.ChristmasActive)[1])
	
	return True
	
def RefreshAllRoleByTick():
	'''
	中午12点刷新所有玩家许愿树货架
	'''
	if not IS_START:
		return
	
	for tmpRole in cRoleMgr.GetAllRole():
		if tmpRole.GetLevel() < EnumGameConfig.ChristmasWishTree_NeedLevel:
			continue
		RefreshShelf(tmpRole, REFRESHTYPE_SYSTEM)
		tmpRole.SendObj(ChristmasWishTree_GoodsShelf_Sync, tmpRole.GetObj(EnumObj.ChristmasActive)[1])

def RefreshShelf(role, refreshType):
	'''
	刷新玩家许愿树货架 0点触发和12点触发分别处理相关数据
	系统刷新记录刷新时相关数据
	手动刷新不采集数据 仅刷新货架商品
	'''
	#1.系统刷新 采集相关数据保存
	if refreshType == REFRESHTYPE_SYSTEM:
		curDay = cDateTime.Days()
		curHour = cDateTime.Hour()
		
		#记录刷新的天数
		role.SetI16(EnumInt16.ChristmasWishTreeRefreshDay, curDay)
		
		#12点触发
		if curHour >= 12:
			#记录今日12点已刷新标志
			role.SetDI1(EnumDayInt1.ChristmasWishTreeRefreshFlag, 1)
		#0点触发	
		else:
			pass
	#手动刷新
	else:
		pass
	
	#2刷新货架
	#2.1获取刷新的货架列表
	roleLevel = role.GetLevel()
	shelfGoodsList = ChristmasWishTreeConfig.GetRandomGoodsByLevel(roleLevel)
	if not shelfGoodsList:
		print "GE_EXC, can not get shelfGoodsList by roleLevel(%s)" % roleLevel
		return None
	
	#2.2组装刷新的货架商品字典
	shelfGoodsDict = {}
	for shelfGood in shelfGoodsList:
		goodId = shelfGood[GOODID_IDX]
		itemCnt = shelfGood[ITEMCNT_IDX]
		shelfGoodsDict[goodId] = itemCnt
	
	#2.3保存刷新后的货架
	role.GetObj(EnumObj.ChristmasActive)[1] = shelfGoodsDict

#TICK and EVENT
def OnRoleDayClear(role, param):
	'''
	每日重置 此处触发0点刷新许愿树货架
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.ChristmasWishTree_NeedLevel:
		return
	
	#0点重置许愿树货架
	RefreshShelf(role, REFRESHTYPE_SYSTEM)
	role.SendObj(ChristmasWishTree_GoodsShelf_Sync, role.GetObj(EnumObj.ChristmasActive)[1])

def OnRoleInit(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	#初始key1
	if 1 not in role.GetObj(EnumObj.ChristmasActive):
		role.GetObj(EnumObj.ChristmasActive)[1] = {}
	#初始key2	
	if 2 not in role.GetObj(EnumObj.ChristmasActive):
		role.GetObj(EnumObj.ChristmasActive)[2] = {}
	#初始key3	
	if 3 not in role.GetObj(EnumObj.ChristmasActive):
		role.GetObj(EnumObj.ChristmasActive)[3] = {}
	
def AfterLevelUp(role, param):
	'''
	玩家等级提升 判断是否达到等级限制 若是则刷新货架
	'''
	if not IS_START:
		return
	
	if role.GetLevel() != EnumGameConfig.ChristmasWishTree_NeedLevel:
		return
	
	#等级解锁了 刷新圣诞树货架
	RefreshShelf(role, REFRESHTYPE_SYSTEM)

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		Cron.CronDriveByMinute((2038, 1, 1), RefreshAllRoleByTick, H = "H == 12", M = "M == 0")
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartWishTree)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndWishTree)
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)	
			
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasWishTree_OnOpenPanel", "圣诞许愿树_请求打开面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasWishTree_OnRefreshShelf", "圣诞许愿树_请求刷新货架"), OnRefreshShelf)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ChristmasWishTree_OnBuyGoods", "圣诞许愿树_请求购买商品"), OnBuyGoods)