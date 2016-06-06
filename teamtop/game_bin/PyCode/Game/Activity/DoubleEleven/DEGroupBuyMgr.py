#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.DEGroupBuyMgr")
#===============================================================================
# 双十一2015 团购送神石 Mgr
#===============================================================================
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalDataDefine, GlobalPrompt
from ComplexServer.Log import AutoLog
from ComplexServer.API import GlobalHttp
from Game.Role import Event
from Game.Role.Mail import Mail
from Game.Persistence import Contain
from Game.Role.Data import EnumDayInt1
from Game.Activity.DoubleEleven import DEGroupBuyConfig


FIFTY_FIVE_MIN_SECONDS = 55 * 60

if "_HasLoad" not in dir():
	#活动开关标志
	IS_START = False
	#活动结束时间戳
	ENDTIME = 0
	#活动开启天数
	DAYINDEX = 0
	#整点销量缓存
	DE_GROUPBUY_CNT = 0 
	
	#团购送神石_活动状态同步  格式: endTime (非零表示活动结束时间戳，零表示告知活动结束！)
	DEGroupBuy_ActiveState_S = AutoMessage.AllotMessage("DEGroupBuy_ActiveState_S", "团购送神石_活动状态同步")
	#团购送神石同步上个整点购买总数 格式 
	DEGroupBuy_SalesCnt_S = AutoMessage.AllotMessage("DEGroupBuy_SalesCnt_S", "团购送神石_整点销量同步")
	#活动开启天数同步 格式 dayIndex
	DEGroupBuy_DayIndex_S = AutoMessage.AllotMessage("DEGroupBuy_DayIndex_S", "团购送神石_开启天数同步")
	
	#日志
	Tra_DEGroupBuy_BuyGoods = AutoLog.AutoTransaction("Tra_DEGroupBuy_BuyGoods", "团购送神石_购买商品")
	Tra_DEGroupBuy_UnlockReward = AutoLog.AutoTransaction("Tra_DEGroupBuy_UnlockReward", "团购送神石_解锁奖励")

#===============================================================================
# 活动控制
#===============================================================================
def OpenActive(callArgv, regparam):
	'''
	古堡探秘-开启
	'''
	global ENDTIME
	global IS_START
	
	if IS_START is True:
		print 'GE_EXC, repeat start DEGroupBuy'
		return
	IS_START = True
	
	ENDTIME = regparam
	
	cNetMessage.PackPyMsg(DEGroupBuy_ActiveState_S, (IS_START,ENDTIME))
	cRoleMgr.BroadMsg()
	
	#活动开启即可计算天数索引  不能直接设置为1 有可能活动期间重启服务器
	CalculateDayIndex()
	
	
def CloseActive(callArgv, regparam):
	'''
	古堡探秘-结束
	'''
	global IS_START
	
	if not IS_START:
		print 'GE_EXC, repeat end DEGroupBuy'
		return
	IS_START = False
	
	cNetMessage.PackPyMsg(DEGroupBuy_ActiveState_S, (IS_START,ENDTIME))
	cRoleMgr.BroadMsg()
	

#===============================================================================
# 客户端请求
#===============================================================================
def OnOpenPanel(role, msg = None):
	'''
	团购送神石_请求打开操作面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DEGroupBuy_NeedLevel:
		return
	
	role.SendObj(DEGroupBuy_SalesCnt_S, DE_GROUPBUY_CNT)
	role.SendObj(DEGroupBuy_DayIndex_S, DAYINDEX)


def OnBuyGoods(role, msg = None):
	'''
	团购送神石_请求购买商品
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DEGroupBuy_NeedLevel:
		return
	
	if role.GetDI1(EnumDayInt1.DEGroupBuyFlag) != 0:
		return
	
	cfg = DEGroupBuyConfig.GetCfgByDayIndex(DAYINDEX)
	if not cfg:
		print "GE_EXC, DEGroupBuyMgr:: can not get cfg by dayIndex(%s)" % DAYINDEX
		return
	
	needRMB = cfg.needUnbindRMB
	if role.GetUnbindRMB_Q() < needRMB:
		return
	
	with Tra_DEGroupBuy_BuyGoods:
		#扣神石
		role.DecUnbindRMB_Q(needRMB)
		#购买记录
		role.SetDI1(EnumDayInt1.DEGroupBuyFlag, 1)
		global DEGroupBuy_BuyRecord_Dict
		recordRoleSet = DEGroupBuy_BuyRecord_Dict.get(1,set())
		recordRoleSet.add(role.GetRoleID())
		DEGroupBuy_BuyRecord_Dict.HasChange()
		#全局购买数量处理
		GlobalHttp.IncGlobalData(GlobalDataDefine.DEGroupBuyDataKey, 5)
		#物品获得
		coding, cnt = cfg.goodsItem
		role.AddItem(coding, cnt)
		role.Msg(2, 0, GlobalPrompt.DEGroup_Tips_Head + GlobalPrompt.Item_Tips % (coding, cnt))
		
		
#===============================================================================
# TICK 处理
#===============================================================================
def CallAfterNewHour():
	'''
	活动脉搏 整点触发
	'''
	global DE_GROUPBUY_CNT
	#非零点整点数据更新
	if cDateTime.Hour() != 0:
		if IS_START:
			GetGBPGlobalData()
	if cDateTime.Hour() == 23:
		#23:55分取回数据 
		if IS_START:
			cComplexServer.RegTick(FIFTY_FIVE_MIN_SECONDS, TickGetGBCGlobalData)
	elif cDateTime.Hour() == 0:
		#跨天处理 （活动为继续开启状态） 
		#发奖
		AwardUnlockReward()	
		#重算dayIndex并同步
		UpdateAndSyncDayIndex()
		if IS_START:
			#同步最新购买总数
			cNetMessage.PackPyMsg(DEGroupBuy_SalesCnt_S, DE_GROUPBUY_CNT)
			cRoleMgr.BroadMsg()


#===============================================================================
# 辅助
#===============================================================================
def CalculateDayIndex():
	'''
	计算当前活动开启天数
	'''
	#活动开始的天数
	baseCfg = DEGroupBuyConfig.DEGroupBuyActive_cfg 
	if not baseCfg:
		print "GE_EXC,CircularActive.DEGroupBuyActive_cfg is None"
		return
	
	#当前日期时间
	nowDate = cDateTime.Now()
	#活动持续开启的天数
	durableDay = (nowDate - baseCfg.beginTime).days
	#更新全局DAY_INDEX
	global DAYINDEX
	DAYINDEX = durableDay + 1	
	#超过 强制设置最后一天
	if DAYINDEX > baseCfg.totalDay:
		DAYINDEX = baseCfg.totalDay


def TickGetGBCGlobalData(callargv, regparam):
	'''
	tick触发取回数据
	'''
	GetGBPGlobalData()


def GetGBPGlobalData():
	'''
	请求获取最新全局购买总数
	'''
	#获取第一个物品全局购买总数
	GlobalHttp.GetGlobalData(GlobalDataDefine.DEGroupBuyDataKey, OnGlobalDataBack)


def OnGlobalDataBack(backvalue, regparam):
	'''
	全局购买数据载回
	'''
	global DE_GROUPBUY_CNT
	if backvalue is None:
		print "GE_EXC, DEGroupBuy::OnGlobalDataBack backvalue is None"
		return
	
	DE_GROUPBUY_CNT = backvalue
	
	if IS_START:
		cRoleMgr.Msg(11, 0, GlobalPrompt.DEGroupBuy_Msg_Hour % DE_GROUPBUY_CNT)


def AwardUnlockReward():
	'''
	根据当前数据 解锁奖励 并发奖
	'''
	global DE_GROUPBUY_CNT
	#第一个商品解锁奖励
	rewardList = []
	rewardCfg = DEGroupBuyConfig.GetCfgByDayIndex(DAYINDEX)
	if not rewardCfg:
		return
	
	for needCnt, rewardItems in rewardCfg.UnlockRewardList:
		if DE_GROUPBUY_CNT >= needCnt:
			for coding, cnt in rewardItems:
				rewardList.append((coding, cnt))
	
	#有解锁任何奖励
	global DEGroupBuy_BuyRecord_Dict
	recordRole_Set = DEGroupBuy_BuyRecord_Dict.get(1, set())
	GP = GlobalPrompt
	if len(rewardList) > 0:
		with Tra_DEGroupBuy_UnlockReward:
			for tmpRoleId in recordRole_Set:
				Mail.SendMail(tmpRoleId, GP.DEGroup_Title, GP.DEGroup_Sender, GP.DEGroup_Content % DAYINDEX, rewardList)
	print "DEGroupBuy DE_GROUPBUY_CNT and recordRole_Set:", DE_GROUPBUY_CNT,recordRole_Set
	#发奖之后
	#清除本服购买玩家的roleId	
	DEGroupBuy_BuyRecord_Dict.data = {1:set()}
	DEGroupBuy_BuyRecord_Dict.changeFlag = True
	#清楚购买总数缓存
	DE_GROUPBUY_CNT = 0
	
	
def UpdateAndSyncDayIndex():
	'''
	重算dayIndex并同步
	'''
	CalculateDayIndex()
	#活动开启状态下广播同步dayIndex
	if IS_START:
		cNetMessage.PackPyMsg(DEGroupBuy_DayIndex_S, DAYINDEX)
		cRoleMgr.BroadMsg()


#===============================================================================
# 事件
#===============================================================================
def OnSyncOtherData(role, param = None):
	'''
	上线处理
	'''
	if IS_START:
		role.SendObj(DEGroupBuy_ActiveState_S, (IS_START, ENDTIME))


def AfterDEGroupBuyRecord():
	'''
	数据载回 初始化数据结构
	'''
	global DEGroupBuy_BuyRecord_Dict
	if 1 not in DEGroupBuy_BuyRecord_Dict:
		DEGroupBuy_BuyRecord_Dict[1] = set()
		DEGroupBuy_BuyRecord_Dict.HasChange()
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		#TICK
		cComplexServer.RegBeforeNewHourCallFunction(CallAfterNewHour)
		#持久化数据
		DEGroupBuy_BuyRecord_Dict = Contain.Dict("DEGroupBuy_BuyRecord_Dict", (2038, 1, 1), AfterDEGroupBuyRecord)	#本服购买记录{1:set(roleId,),}
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DEGroupBuy_OnOpenPanel", "团购送神石_请求打开操作面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DEGroupBuy_OnBuyGoods", "团购送神石_请求购买商品"), OnBuyGoods)
