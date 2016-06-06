#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SuperDiscount.SDManager")
#===============================================================================
# 超值大礼 akm
#===============================================================================
import cRoleMgr
import cNetMessage
import Environment
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role import Event
from Game.Persistence import Contain
from Game.Activity.SuperDiscount import SDConfig
from Game.Activity import CircularDefine
from Game.Role.Data import EnumInt32
from Game.Activity.HappyNewYear import NewYearDiscount

if "_HasLoad" not in dir():		
	SUPERDISCOUNT_ONLINE_SET = set()	#超值大礼 当前开启的主题set([SDType1,SDType2...])
	IS_START = False			
	#消息
	Sync_SD_Buy_Record = AutoMessage.AllotMessage("Sync_SD_Buy_Record", "同步玩家超值大礼购买记录")
	Sync_SD_Online_Type = AutoMessage.AllotMessage("Sync_SD_Online_Type", "同步当前开启的超值大礼主题") 
	#事务
	Tra_SD_Buy_LiBao = AutoLog.AutoTransaction("Tra_SD_Buy_LiBao", "购买超值大礼礼包")	

def SuperDiscountStart(*param):
	'''
	超值大礼某主题开启
	'''
	_, circularType = param
	if CircularDefine.CA_SuperDiscountStart > circularType or circularType > CircularDefine.CA_SuperDiscountEnd:
		return
	
	# 已开启 
	global IS_START
	global SUPERDISCOUNT_ONLINE_SET
	if circularType in SUPERDISCOUNT_ONLINE_SET:
		print "GE_EXC,repeat open superDiscount activeType(%s)" % circularType
		return
		
	IS_START = True	
	SUPERDISCOUNT_ONLINE_SET.add(circularType)	

def SuperDiscountEnd(*param):
	'''
	超值大礼某主题结束
	'''
	_, circularType = param
	if CircularDefine.CA_SuperDiscountStart > circularType or circularType > CircularDefine.CA_SuperDiscountEnd:
		return
	
	# 未开启 
	global SUPERDISCOUNT_ONLINE_SET
	if circularType not in SUPERDISCOUNT_ONLINE_SET:
		print "GE_EXC,end superDiscount activeType(%s) not open" % circularType
		return
	
	#移除circularType 
	SUPERDISCOUNT_ONLINE_SET.remove(circularType)	
	
	#最后一个主题结束 关闭超值大礼活动
	if len(SUPERDISCOUNT_ONLINE_SET) < 1:
		global IS_START
		IS_START = False
		
	#广播客户端最新开启主题集合
	cNetMessage.PackPyMsg(Sync_SD_Online_Type, SUPERDISCOUNT_ONLINE_SET)
	cRoleMgr.BroadMsg()
	
	#清除对应主题所有玩家购买记录
	global SUPERDISDOUNT_BUY_RECORD_PDICT
	toClearSet = SDConfig.SUPERDISCOUNT_LIBAO_TYPE_DICT.get(circularType,set())
	
	for roleId, buyDict in  SUPERDISDOUNT_BUY_RECORD_PDICT.items():
		for LiBaoId, _ in buyDict.items():
			if LiBaoId not in toClearSet:
				continue
			else:
				del buyDict[LiBaoId]
		if len(SUPERDISDOUNT_BUY_RECORD_PDICT[roleId]) == 0:
			del SUPERDISDOUNT_BUY_RECORD_PDICT[roleId]	
			
	SUPERDISDOUNT_BUY_RECORD_PDICT.HasChange()

def RequestOpenSDPanel(role, param):
	'''
	客户端请求打开超值大礼面板
	@param role: 
	@param param: 	
	'''
	#未开启
	if not IS_START:
		return
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.SuperDiscount_NeedLevel:
		return
	
	SyncSDBuyRecord(role, False)
	
def SyncSDBuyRecord(role, isOnlyBuyRecord):
	'''
	同步玩家购买记录
	@param role: 
	@param param: isOnlyBuyRecord 是否仅仅同步购买记录
	'''
	#同步当前开启主题集合
	if not isOnlyBuyRecord:	
		role.SendObj(Sync_SD_Online_Type, SUPERDISCOUNT_ONLINE_SET)
	
	#同步购买记录
	role.SendObj(Sync_SD_Buy_Record, SUPERDISDOUNT_BUY_RECORD_PDICT.get(role.GetRoleID(), {}))	

def RequestSDBuyLiBao(role, msg):
	'''
	购买请求处理
	@param role: 
	@param msg: [SDType, LiBaoID, buyCnt]
	'''
	#未开启任何主题
	if not IS_START:
		return
	
	#等级不足
	if role.GetLevel() < EnumGameConfig.SuperDiscount_NeedLevel:
		return
	
	#参数检测	
	SDType,LiBaoID,buyCnt = msg
	if SDType not in SUPERDISCOUNT_ONLINE_SET:
		return
		
	if SDType not in SDConfig.SUPERDISCOUNT_LIBAO_TYPE_DICT:
		return
	
	if LiBaoID not in SDConfig.SUPERDISCOUNT_LIBAO_TYPE_DICT[SDType]:
		return

	#购买数量检测
	cfg =SDConfig.SUPERDISCOUNT_LIBAO_DICT.get(LiBaoID,None)
	if not cfg or buyCnt > cfg.Cnt:
		return
	
	#神石不足
	if cfg.MoneyType == 1:
		if role.GetUnbindRMB() < cfg.RealPrice:
			return
	elif cfg.MoneyType == 0:
		if role.GetUnbindRMB_Q() < cfg.RealPrice:
			return
	else:
		return
	
	global SUPERDISDOUNT_BUY_RECORD_PDICT
	buyRecordDict = SUPERDISDOUNT_BUY_RECORD_PDICT.get(role.GetRoleID(), {})
	broughtCnt = buyRecordDict.get(LiBaoID,0) + buyCnt
	if broughtCnt > cfg.Cnt:
		return 
	
	#购买处理
	with Tra_SD_Buy_LiBao:
		#写购买记录
		buyRecordDict[LiBaoID] = broughtCnt
		SUPERDISDOUNT_BUY_RECORD_PDICT[role.GetRoleID()] = buyRecordDict
		
		#扣钱
		if cfg.MoneyType == 1:	
			role.DecUnbindRMB(cfg.RealPrice)
		elif cfg.MoneyType == 0:
			role.DecUnbindRMB_Q(cfg.RealPrice)
		else:
			pass	
		
		if NewYearDiscount.IsOpen:
			#新年乐翻天积分
			role.IncI32(EnumInt32.NewYearScore, cfg.RealPrice)
		
		#发金币
		if cfg.RewardMoney > 0:
			role.IncMoney(cfg.RewardMoney)
		
		#发奖励神石
		if cfg.RewardRMB > 0:
			role.IncUnbindRMB_S(cfg.RewardRMB)
		
		#发魔晶
		if cfg.RewardBindRMB > 0:
			role.IncBindRMB(cfg.RewardBindRMB)	
		
		#发普通物品
		for item in cfg.RealItems:
			role.AddItem(*item)	
		
		#同步最新购买记录
		SyncSDBuyRecord(role, True)		
			
		#物品
		itemRewardMsg = ""
		for itemCoding, cnt in cfg.RealItems:
			itemRewardMsg = itemRewardMsg + GlobalPrompt.SDRewardMsg_Item % (itemCoding, cnt)
		
		#金币
		if cfg.RewardMoney == 0:
			moneyRewardMsg = ""
		else:
			moneyRewardMsg = GlobalPrompt.SDRewardMsg_Money % cfg.RewardMoney
		
		#魔晶
		if cfg.RewardBindRMB == 0:
			bindRMBRewardMsg = ""
		else:
			bindRMBRewardMsg = GlobalPrompt.SDRewardMsg_BindRMB % cfg.RewardBindRMB	
		
		#奖励神石	
		if cfg.RewardRMB == 0:
			RMBRewardMsg = ""
		else:
			RMBRewardMsg = GlobalPrompt.SDRewardMsg_RMB % cfg.RewardRMB				
		
		SDRewardMsg = GlobalPrompt.SDRewardMsg_Head + itemRewardMsg + moneyRewardMsg + bindRMBRewardMsg + RMBRewardMsg
		role.Msg(2, 0, SDRewardMsg)		
			
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#超值大礼玩家购买记录 {roleId:{LiBaoID:cnt},}
		SUPERDISDOUNT_BUY_RECORD_PDICT = Contain.Dict("SuperDiscount_Buy_Record", (2038, 1, 1))
		
		Event.RegEvent(Event.Eve_StartCircularActive, SuperDiscountStart)
		Event.RegEvent(Event.Eve_EndCircularActive, SuperDiscountEnd)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_Open_SuperDiscount_Panel", "客户端打开超值大礼面板"), RequestOpenSDPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request_SuperDiscount_Buy", "客户端请求购买超值大礼礼包"), RequestSDBuyLiBao)		
			