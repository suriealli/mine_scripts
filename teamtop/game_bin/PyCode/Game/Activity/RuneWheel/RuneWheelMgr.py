#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RuneWheel.RuneWheelMgr")
#===============================================================================
# 符文宝轮
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumDayInt1, EnumInt16
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Persistence import Contain
from Game.Activity.RuneWheel import RuneWheelConfig
from Game.Role import Event

if "_HasLoad" not in dir():
	#消息
	RuneWheel_callback = AutoMessage.AllotMessage("RuneWheel_callback", "符文宝轮回调")
	RuneWheel_role_list = AutoMessage.AllotMessage("RuneWheel_role_list", "符文宝轮玩家获奖信息")
	
	CallBackSec = 40			#回调时间
	Rune_role_list_len = 10		#获奖信息列表长度
	Cnttwosame = 6				#两次相同物品奖励数
	Cntthreesame = 30			#三次相同物品奖励数
	Cntnosame = 1				#无相同物品奖励
	
	#日志
	RuneWheelCost = AutoLog.AutoTransaction("RuneWheelCost", "参加符文宝轮扣除神石或者符文宝珠")
	RuneWheelReward = AutoLog.AutoTransaction("RuneWheelReward", "参加符文宝轮获取奖励")
	RuneWheelFifytyTimesCost = AutoLog.AutoTransaction("RuneWheelFifytyTimes", "参加50次符文宝轮扣除神石或者符文宝珠")
	RuneWheelFifytyTimesReward = AutoLog.AutoTransaction("RuneWheelFifytyTimesReward", "参加50次符文宝轮获取奖励")

def RequestOneRuneWheel(role,msg):
	'''
	客户端请求1次符文宝轮
	@param role:
	@param msg:
	'''
	#若有符文宝珠，则扣除一个符文宝珠
	
	if role.GetLevel() < EnumGameConfig.RuneWHeel_Need_Level:
		return
	if role.ItemCnt(EnumGameConfig.RuneWHeel_RunePearlCode) > 0:
		with RuneWheelCost:
			role.DelItem(EnumGameConfig.RuneWHeel_RunePearlCode,1)
	else:
		#判断角色当日是否第一次参加符文宝轮，给出不同的价格
		if role.GetDI1(EnumDayInt1.IsFirstRuneWheel) == 0:
			price = EnumGameConfig.RuneWHeel_FirstTinmepRice
			#版本判断
			if Environment.EnvIsNA():
				price = EnumGameConfig.RuneWHeel_FirstTinmepRice_NA
			elif Environment.EnvIsRU():
				price = EnumGameConfig.RuneWHeel_FirstTinmepRice_RU
		else:
			price = EnumGameConfig.RuneWHeel_OtherTimePrice
			#版本判断
			if Environment.EnvIsNA():
				price = EnumGameConfig.RuneWHeel_OtherTimePrice_NA
			elif Environment.EnvIsRU():
				price = EnumGameConfig.RuneWHeel_OtherTimePrice_RU
			
		if role.GetUnbindRMB() < price:
			return
		else:
			with RuneWheelCost:
				role.DecUnbindRMB(price)
				#角色当日是否参加过符文宝轮标志位置为1
				role.SetDI1(EnumDayInt1.IsFirstRuneWheel, 1)
	#开始抽奖
	nowTimes = role.GetI16(EnumInt16.RuneWheelTimes) + 1
	if nowTimes % 10:
		resultwheel, awardlist, awardtype = RandomWheelOnce(isTentimes=False)
	else:
		resultwheel, awardlist, awardtype = RandomWheelOnce(isTentimes=True)
	#将抽奖结果发送给客户端病等待回调，回调后将抽奖结果奖励给玩家
	role.SendObjAndBack(RuneWheel_callback, resultwheel, CallBackSec, CallbackRuneWheel, [awardlist,awardtype])

def RequestFiftyRuneWheel(role,msg):
	'''
	客户端请求50次符文宝轮
	@param role:
	@param msg:
	'''
	#如果等级不符合要求则返回
	if role.GetLevel() < EnumGameConfig.RuneWHeel_Need_Level:
		return
	#如果VIP等级不符合要求则返回
	if role.GetVIP() < EnumGameConfig.Fifty_RuneWHeel_Need_VIPLevel:
		return
	#消耗的符文宝珠数量
	RunePearlCost = min(role.ItemCnt(EnumGameConfig.RuneWHeel_RunePearlCode), 50)
	
	perTimeNeedRMB = EnumGameConfig.RuneWHeel_OtherTimePrice
	#版本判断
	if Environment.EnvIsNA():
		perTimeNeedRMB = EnumGameConfig.RuneWHeel_OtherTimePrice_NA
	elif Environment.EnvIsRU():
		perTimeNeedRMB = EnumGameConfig.RuneWHeel_OtherTimePrice_RU
	
	#消耗的神石数量
	RMBCost = perTimeNeedRMB * (50 - RunePearlCost)
	#如果玩家神石数小于预计消耗的神石数量则返回
	if role.GetUnbindRMB() < RMBCost:
		return

	with RuneWheelFifytyTimesCost:
		if RunePearlCost > 0 :
			#消耗玩家符文宝珠
			role.DelItem(EnumGameConfig.RuneWHeel_RunePearlCode,RunePearlCost)
		if RMBCost:
			#消耗玩家神石
			role.DecUnbindRMB(RMBCost)
		#角色当日是否参加过符文宝轮标志位置为1
		role.SetDI1(EnumDayInt1.IsFirstRuneWheel, 1)
	awardlist = 		[]
	onetimescnt = 		0
	sixtimescnt = 		0
	thirtytimescnt = 	0
	AE = awardlist.extend
	for _ in xrange(45):
		_, award, awardtype = RandomWheelOnce(isTentimes=False)
		if awardtype == 3:
			thirtytimescnt += 1
		elif awardtype == 2:
			sixtimescnt += 1
		elif awardtype == 1:
			onetimescnt += 1
		else:
			print "GE_EXC, error in RequestFiftyRuneWheel (%s) roleID (%s)" % (awardtype, role.GetRoleID())
			continue
		AE(award)
		
	#次数为为10的整数倍时要特殊处理
	for _ in xrange(5):
		_, award, _ = RandomWheelOnce(isTentimes=True)
		sixtimescnt += 1
		AE(award)

	with RuneWheelFifytyTimesReward:
		role.IncI16(EnumInt16.RuneWheelTimes, 50)
		awardrdict = {}
		awardrdictget = awardrdict.get
		for itemcode , cnt in awardlist:
			awardrdict[itemcode] = awardrdictget(itemcode,0) + cnt
		roleAddItem = role.AddItem
		for itemc ,ct in awardrdict.iteritems():
			#发放奖励	
			roleAddItem(itemc, ct)
	
	global rewardrolelist
	#修改持久化列表数据
	rewardrolelist.append((role.GetRoleName(), 50, ((onetimescnt, sixtimescnt, thirtytimescnt),awardrdict.items())))
	#发送玩家中奖信息
	if len(rewardrolelist) > Rune_role_list_len:
		rewardrolelist.data = rewardrolelist.data[-Rune_role_list_len:]
	role.SendObj(RuneWheel_role_list, rewardrolelist.data)
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_RuneWheel, 50))
	
	#系统消息提示玩家中奖信息
	roleName = role.GetRoleName()
	cRoleMgr.Msg(1, 0, GlobalPrompt.RuneWheel_Fiftyth % (roleName, onetimescnt, sixtimescnt, thirtytimescnt))
	
def CallbackRuneWheel(role, callargv, regparam):
	'''
	符文宝轮单次回调
	@param role:
	@param msg:
	'''
	global rewardrolelist
	awardlist , awardtype = regparam
	with RuneWheelReward:
		role.IncI16(EnumInt16.RuneWheelTimes, 1)
		roleAddItem = role.AddItem
		for itemcode , cnt in awardlist:
			#给玩家发放奖励
			roleAddItem(itemcode, cnt)
	rewardrolelist.append((role.GetRoleName(),1,(awardtype, awardlist)))
	#发送最新的符文宝轮中奖明细
	if len(rewardrolelist) > Rune_role_list_len:
		rewardrolelist.data = rewardrolelist.data[-Rune_role_list_len:]
	role.SendObj(RuneWheel_role_list, rewardrolelist.data)
	if awardtype == 3 or awardtype == 2 :
		if awardtype ==3:
			t = Cntthreesame
		else:
			t = Cnttwosame	
		roleName = role.GetRoleName()
		cRoleMgr.Msg(1, 0, GlobalPrompt.RuneWheel_Once % (roleName, awardtype, t))
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_RuneWheel, 1))
	
def RandomWheelOnce(isTentimes=False):
	#次数为10的整数倍的话要特殊处理 
	resultWheel = []
	awardlist = []
	awardtype = 0
	Random_item = RuneWheelConfig.RANDOM_ITEM.RandomOne
	#如果次数是10的整数倍的话直接取出
	if isTentimes:
		resultWheel = RuneWheelConfig.RANDOM_ITEM_Ten.RandomOne()
	#从配置表中随机读取三次数据
	#每读取一次数据，将数据存入名为resultWheel的空列表中
	else:
		for _ in xrange(3):
			randonItem = Random_item()
			resultWheel.append(randonItem)
	#检查resultWheel表中一共有几种物品代码，将他们存储在resultWheelabs中
	resultWheelabs_set = set(resultWheel)
	listLen = len(resultWheelabs_set)
	if listLen == 3:
		#三次各不相同
		awardtype = 1
		for item in resultWheel:
			awardlist.append((item, Cntnosame))
	elif listLen == 1:
		#三次相同
		awardtype = 3
		awardlist = [(resultWheel[0], Cntthreesame)]
	elif listLen == 2:
		#有两次相同
		awardlistappend = awardlist.append
		for item in resultWheelabs_set:
			if resultWheel.count(item) == 2:
				awardlistappend((item , Cnttwosame))
			else:
				awardlistappend((item , Cntnosame))
		awardtype = 2
	return resultWheel, awardlist, awardtype

def RuneWheelAfterLoad():
	pass

def RuneWheelBeforeSave():
	global rewardrolelist
	if len(rewardrolelist) > Rune_role_list_len:
		rewardrolelist.data = rewardrolelist[-Rune_role_list_len:]
		rewardrolelist.HasChange()

def RequestOpenRuneWheel(role ,msg):
	'''
	客户端请求打开符文宝轮面板
	@param role:
	@param msg:
	'''
	if len(rewardrolelist) > Rune_role_list_len:
		rewardrolelist.data = rewardrolelist.data[-Rune_role_list_len:]
	role.SendObj(RuneWheel_role_list, rewardrolelist.data)

def DayClear(role, param):
	if role.GetI16(EnumInt16.RuneWheelTimes) > 0:
		role.SetI16(EnumInt16.RuneWheelTimes, 0)

if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		rewardrolelist = Contain.List("rewardrolelist", (2038, 1, 1), RuneWheelAfterLoad, RuneWheelBeforeSave, isSaveBig = False)
		
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, DayClear)
		
		if not Environment.IsCross:
			#客户端请求	
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOneRuneWheel", "客户端请求一次符文宝轮"), RequestOneRuneWheel)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestFiftyRuneWheel", "客户端请求五十次次符文宝轮"), RequestFiftyRuneWheel)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenuneWheel", "客户端请求打开符文宝轮"), RequestOpenRuneWheel)
	
