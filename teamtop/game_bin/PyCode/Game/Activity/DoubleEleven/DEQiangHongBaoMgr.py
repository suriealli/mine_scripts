#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.DEQiangHongBaoMgr")
#===============================================================================
# 双十一2015 抢红包 Mgr
#===============================================================================
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
import Environment
from Util import Random
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Role.Data import EnumCD
from Game.Activity.DoubleEleven import DEQiangHongBaoConfig
import time


TYPE_NO = 0
TYPE_QHB = 1
TYPE_QG = 2

ONEMIN_SEC = 60 * 1
if "_HasLoad" not in dir():
	#活动开关
	IS_START = False
	#结束时间戳
	ENDTIME = 0
	#购买记录缓存 {roleId:set([goodsId,])}
	BUYRECORD_DICT = {}
	#当前回合Index
	CURROUNDINDEX = 0
	#有效回合tick缓存 {roundIndex:tickId,}
	ROUNDTICK_DICT = {}
	#剩余红包缓存 {coding:cnt,}
	HONGBAOPOOL = {}
	#缓存当前打开操作面板玩家ID
	DEQiangHongBao_OnLineRole_Set = set()
	
	#格式( IS_START, endTime) (非零表示活动结束时间戳，零表示告知活动结束！)
	DEQiangHongBao_ActiveState_S = AutoMessage.AllotMessage("DEQiangHongBaoMgr", "双十一抢红包_活动状态同步")
	#格式： roundIndex 
	DEQiangHongBao_RoundIndex_S = AutoMessage.AllotMessage("DEQiangHongBao_RoundIndex_S", "双十一抢红包_当前回合同步")
	#格式 set([goodsId1,goodsId2])
	DEQiangHongBao_BuyRecord_S = AutoMessage.AllotMessage("DEQiangHongBao_BuyRecord_S", "双十一抢红包_购买记录同步")
	# true or false
	DEQiangHongBao_AnyHongBao_S = AutoMessage.AllotMessage("DEQiangHongBao_AnyHongBao_S", "双十一抢红包_是否剩余红包同步")
	
	
	Tra_DEQiangHongBao_QiangHongBao = AutoLog.AutoTransaction("Tra_DEQiangHongBao_QiangHongBao", "双十一抢红包_抢红包")
	Tra_DEQiangHongBao_QiangGou = AutoLog.AutoTransaction("Tra_DEQiangHongBao_QiangGou", "双十一抢红包_抢购")

#===============================================================================
# 活动控制
#===============================================================================
def OpenActive(callArgv, regparam):
	'''
	古堡探秘-开启
	'''
	global ENDTIME
	global IS_START
	
	if IS_START:
		print 'GE_EXC, repeat start DEQiangHongBao'
		return
	IS_START = True
	
	ENDTIME = regparam
	
	cNetMessage.PackPyMsg(DEQiangHongBao_ActiveState_S, (IS_START,ENDTIME))
	cRoleMgr.BroadMsg()
	
	#活动开启 即可处理
	InitActiveRound()
	
	
def CloseActive(callArgv, regparam):
	'''
	古堡探秘-结束
	'''
	global IS_START
	
	if not IS_START:
		print 'GE_EXC, repeat end DEQiangHongBao'
		return
	IS_START = False
	
	cNetMessage.PackPyMsg(DEQiangHongBao_ActiveState_S, (IS_START,ENDTIME))
	cRoleMgr.BroadMsg()
	

#===============================================================================
# 客户端请求
#===============================================================================
def OnOpenPanel(role, msg = None):
	'''
	双十一抢红包_请求打开操作面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DEQiangHongBao_NeedLevel:
		return
	
	role.SendObj(DEQiangHongBao_RoundIndex_S, CURROUNDINDEX)
	
	roundCfg = DEQiangHongBaoConfig.DEQiangHongBao_RoundControl_Dict.get(CURROUNDINDEX)
	if not roundCfg:
		print "GE_EXC,DEQiangHongBaoMgr::OnOpenPanel can not get cfg by CURROUNDINDEX(%s)" % CURROUNDINDEX
		return
	
	global DEQiangHongBao_OnLineRole_Set
	DEQiangHongBao_OnLineRole_Set.add(role.GetRoleID())
	
	curRoundType = roundCfg.roundType
	if curRoundType == TYPE_QG:
		role.SendObj(DEQiangHongBao_BuyRecord_S, BUYRECORD_DICT.get(role.GetRoleID(),set()))
	elif curRoundType == TYPE_QHB:
		role.SendObj(DEQiangHongBao_AnyHongBao_S, AnyHongBao())


def OnClosePanel(role, msg = None):
	'''
	双十一抢红包_请求关闭操作面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DEQiangHongBao_NeedLevel:
		return
	
	global DEQiangHongBao_OnLineRole_Set
	DEQiangHongBao_OnLineRole_Set.discard(role.GetRoleID())
	
	
def OnQiangHongBao(role, msg = None):
	'''
	双十一抢红包_请求抢红包
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DEQiangHongBao_NeedLevel:
		return
	
	roundCfg = DEQiangHongBaoConfig.DEQiangHongBao_RoundControl_Dict.get(CURROUNDINDEX)
	if not roundCfg:
		return
	
	if roundCfg.roundType != TYPE_QHB:
		return
	
	if role.GetCD(EnumCD.DEQiangHongBaoCD):
		return
	
	if role.PackageEmptySize() < 1:
		return
	
	if CountRoleHongBaoCnt(role) >= EnumGameConfig.DEQiangHongBao_RoleMaxCnt:
		return
	
	#上一个玩家抢了最后一个红包 提前启动狂购 
	if AnyHongBao() == 0:
		AheadNextRound()
		return
	
	hongBaoCoding = RandomHongBao()
	#随机不出红包了 证明抢完了 提前触发结束 并启动抢购
	if not hongBaoCoding:
		AheadNextRound()
		role.Msg(2, 0, GlobalPrompt.DEQiangHongBao_Tips_NoHongBao)
		return
	
	with Tra_DEQiangHongBao_QiangHongBao:
		#获得
		role.AddItem(hongBaoCoding, 1)
		#设置CD
		role.SetCD(EnumCD.DEQiangHongBaoCD, EnumGameConfig.DEQiangHongBaoCD)
	
	#提示
	role.Msg(2, 0, GlobalPrompt.DEQiangHongBao_Tips_QHB + GlobalPrompt.Item_Tips % (hongBaoCoding, 1))
	#同步剩余红包数量
	nowCnt = AnyHongBao()
	for tRoleId in DEQiangHongBao_OnLineRole_Set:
		tRole = cRoleMgr.FindRoleByRoleID(tRoleId)
		if tRole and not tRole.IsLost():
			tRole.SendObj(DEQiangHongBao_AnyHongBao_S, nowCnt)
	
	#抢完之后 再判断是否还有红包剩余处理
	if nowCnt == 0:
		AheadNextRound()

def OnQiangGou(role, msg):
	'''
	双十一抢红包_请求抢购
	@param msg: ([goodsId1,goodsId2],couponCoding) 购买物品列表 优惠卷coding 没有优惠卷发0
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.DEQiangHongBao_NeedLevel:
		return
	
	roundCfg = DEQiangHongBaoConfig.DEQiangHongBao_RoundControl_Dict.get(CURROUNDINDEX)
	if not roundCfg:
		return
	
	if roundCfg.roundType != TYPE_QG:
		return
	
	goodsDict = {}
	curGoodsPool = roundCfg.goodsPool 
	backId, param = msg
	goodsIdList, couponsId = param
	for goodsId in goodsIdList:
		if goodsId not in curGoodsPool:
			return
		
		goodsCfg = DEQiangHongBaoConfig.DEQiangHongBao_GoodsConfig_Dict.get(goodsId, None)
		if not goodsCfg:
			return
		
		coding, cnt = goodsCfg.goodsItem
		if coding not in goodsDict:
			goodsDict[coding] = cnt
		else:
			goodsDict[coding] += cnt
	
	roleId = role.GetRoleID()
	roleRecordSet = BUYRECORD_DICT.get(roleId, set())
	for goodsId in goodsIdList:
		if goodsId in roleRecordSet:
			return
	
	#没有优惠卷
	couponsItem = None
	couponCfg = None
	if couponsId:
		couponsItem = role.FindPackProp(couponsId)
		if not couponsItem:
			return
		if couponsItem.IsDeadTime():
			return 
		couponCfg = DEQiangHongBaoConfig.DEQiangHongBao_CouponsConfig_Dict.get(couponsItem.otype)
		if not couponCfg:
			return
	
	if couponsItem:
		needUnbindRMB = CalculateRMB(goodsIdList, couponsItem.otype)
	else:
		needUnbindRMB = CalculateRMB(goodsIdList, 0)
		
	if role.GetUnbindRMB() < needUnbindRMB:
		return
	
	prompt = GlobalPrompt.DEQiangHongBao_Tips_QG
	with Tra_DEQiangHongBao_QiangGou:
		#记录
		roleRecordSet.update(set(goodsIdList))
		BUYRECORD_DICT[roleId] = roleRecordSet
		#扣钱
		role.DecUnbindRMB(needUnbindRMB)
		#扣优惠卷
		if couponsItem:
			role.DecPropCnt(couponsItem, 1)
		#获得
		for coding, cnt in goodsDict.iteritems():
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.Item_Tips % (coding, cnt)
	
	#提示
	role.Msg(2, 0, prompt)
	#同步最新购买记录
	role.SendObj(DEQiangHongBao_BuyRecord_S, BUYRECORD_DICT[roleId])
	#成功回调
	role.CallBackFunction(backId, None)

	
#===============================================================================
# 辅助
#===============================================================================
def InitActiveRound():
	global ROUNDTICK_DICT
	ROUNDTICK_DICT.clear()
	nowTime = cDateTime.Seconds()
	for tRoundIndex, tCfg in DEQiangHongBaoConfig.DEQiangHongBao_RoundControl_Dict.iteritems():
		beginTime =  int(time.mktime(tCfg.beginTime.timetuple()))
		endTime = int(time.mktime(tCfg.endTime.timetuple()))
		if beginTime <= nowTime < endTime:
			#激活本轮 并注册结束TICK
			StartRound(None, (tRoundIndex))
			eTickId = cComplexServer.RegTick(endTime - nowTime, EndRound)
			ROUNDTICK_DICT[tRoundIndex] = (0, eTickId)
		elif nowTime < beginTime:
			#注册一个tick激活
			sTickId = cComplexServer.RegTick(beginTime - nowTime, StartRound, (tRoundIndex))	
			eTickId = cComplexServer.RegTick(endTime - nowTime, EndRound)
			ROUNDTICK_DICT[tRoundIndex] = (sTickId, eTickId)
			
			#注册抢红包提前一分钟广播
			if tCfg.roundType == TYPE_QHB and beginTime - nowTime > ONEMIN_SEC:
				cComplexServer.RegTick(beginTime - nowTime - ONEMIN_SEC, OneMinBeforeQHB)


def StartRound(callArgs, regParam):
	'''
	开启新的回合
	'''
	roundIndex = regParam
	roundCfg = DEQiangHongBaoConfig.DEQiangHongBao_RoundControl_Dict.get(roundIndex)
	if not roundCfg:
		print "GE_EXC, error roundIndex(%s) when Start round" % roundIndex
		return
	
	if not IS_START:
		return
	
	global CURROUNDINDEX
	CURROUNDINDEX = roundIndex
	
	#抢红包开始
	if roundCfg.roundType == TYPE_QHB:
		cRoleMgr.Msg(11, 0, GlobalPrompt.DEQiangHongBao_Msg_QHBBegan) 	
	
	cNetMessage.PackPyMsg(DEQiangHongBao_RoundIndex_S, CURROUNDINDEX)
	cRoleMgr.BroadMsg()
	
	roundType = roundCfg.roundType
	if roundType == TYPE_NO:
		#中场休息
		pass
	elif roundType == TYPE_QHB:
		#抢红包阶段
		global HONGBAOPOOL
		HONGBAOPOOL.clear()
		#配置检测
		roundCfg = DEQiangHongBaoConfig.DEQiangHongBao_RoundControl_Dict.get(CURROUNDINDEX, None)
		if not roundCfg or not roundCfg.hongBaoPool:
			print "GE_EXC,DEQiangHongBaoMgr::StartRound::no cfg or no hong bao pool in RoundIndex(%s)" % CURROUNDINDEX
			return
		#红包池缓存
		for coding, cnt in roundCfg.hongBaoPool:
			HONGBAOPOOL[coding] = cnt
		#广播通知有红包了
		cNetMessage.PackPyMsg(DEQiangHongBao_AnyHongBao_S, True)
		cRoleMgr.BroadMsg()
	elif roundType == TYPE_QG:
		#抢购阶段
		global BUYRECORD_DICT
		BUYRECORD_DICT.clear()
		#此处考虑下是否要做打开面板玩家缓存 减少不必要的推送
		for tmpRole in cRoleMgr.GetAllRole():
			tmpRole.SendObj(DEQiangHongBao_BuyRecord_S, BUYRECORD_DICT.get(tmpRole.GetRoleID(), set()))
	else:
		pass
	

def EndRound(callArgs, regParam):	
	'''
	结束当前回合
	'''
	if not IS_START:
		return
	
	global CURROUNDINDEX
	RCG = DEQiangHongBaoConfig.DEQiangHongBao_RoundControl_Dict.get
	curRoundCfg = RCG(CURROUNDINDEX)
	if not curRoundCfg:
		print "GE_EXC, DEQiangHongBao::EndRound:: no round cfg for roundIndex(%s)" % CURROUNDINDEX
		return
	
	#抢红包结束广播抢购开始
	if curRoundCfg.roundType == TYPE_QHB:
		cRoleMgr.Msg(11, 0, GlobalPrompt.DEQiangHongBao_Msg_QHBEnd) 
	elif curRoundCfg.roundType == TYPE_QG:
		cRoleMgr.Msg(11, 0, GlobalPrompt.DEQiangHongBao_Msg_QGEnd)
	else:
		pass
	
	nextRoundIndex = curRoundCfg.nextRoundIndex
	if not nextRoundIndex or not RCG(nextRoundIndex):
		CURROUNDINDEX = 1
		#没有后续回合 立刻同步中场休息
		cNetMessage.PackPyMsg(DEQiangHongBao_RoundIndex_S, CURROUNDINDEX)
		cRoleMgr.BroadMsg()
	else:
		#由下一回合开启逻辑处理
		pass
	
	
def AnyHongBao():
	'''
	判断是否有红包剩余
	'''
	totalCnt = 0
	for cnt in HONGBAOPOOL.values():
		totalCnt += cnt
	
	return totalCnt
	

def CountRoleHongBaoCnt(role):
	'''
	统计role背包总共的有效红包红包数量
	'''
	totalCnt = 0
	for couponCoding in DEQiangHongBaoConfig.DEQiangHongBao_CouponsConfig_Dict.keys():
		totalCnt += role.ItemCnt_NotTimeOut(couponCoding)
	
	return totalCnt
	

def RandomHongBao():
	'''
	随机出一个红包
	'''
	global HONGBAOPOOL
	randomObj = Random.RandomRate()
	for coding, cnt in HONGBAOPOOL.iteritems():
		if cnt > 0:
			randomObj.AddRandomItem(1, coding)
	
	#等概率随机红包coding
	coding = randomObj.RandomOne()
	#同步更新红包池缓存
	HONGBAOPOOL[coding] -= 1
	if HONGBAOPOOL[coding] < 1:
		del HONGBAOPOOL[coding]
		
	return coding 


def AheadNextRound():
	'''
	抢红包结束 提前触发抢购
	'''
	global CURROUNDINDEX
	curRoundCfg = DEQiangHongBaoConfig.DEQiangHongBao_RoundControl_Dict.get(CURROUNDINDEX, None)
	if not curRoundCfg or curRoundCfg.roundType != TYPE_QHB:
		print "GE_EXC,AheadInItQiangGou::no cfg for roundIndex(%s) or now is not Qiang hong Bao" % CURROUNDINDEX
		return
	
	nextRoundIndex = curRoundCfg.nextRoundIndex
	if not nextRoundIndex:
		print "GE_EXC,AheadInItQiangGou::no next round for cur roundIndex(%s)" % CURROUNDINDEX
		return
	
	nextRoundCfg = DEQiangHongBaoConfig.DEQiangHongBao_RoundControl_Dict.get(nextRoundIndex, None)
	if not nextRoundCfg:
		print "GE_EXC,AheadInItQiangGou::no nextRoundCfg for nextRoundIndex(%s)" % nextRoundIndex
		return
	
	#抢红包结束广播抢购开始
	if curRoundCfg.roundType == TYPE_QHB:
		cRoleMgr.Msg(11, 0, GlobalPrompt.DEQiangHongBao_Msg_QHBEnd) 
	
	#取消当前回合正常结束TICK
	if CURROUNDINDEX in ROUNDTICK_DICT:
		_, eTickId = ROUNDTICK_DICT[CURROUNDINDEX]
		cComplexServer.UnregTick(eTickId)
		
	#注销被提前启动回合的tick
	if nextRoundIndex in ROUNDTICK_DICT:
		sTickId, _ = ROUNDTICK_DICT[nextRoundIndex]
		cComplexServer.UnregTick(sTickId)
	#启动下一个回合
	StartRound(None, nextRoundIndex)


def CalculateRMB(goodsList, couponCoding):
	'''
	计算神石消耗
	'''
	totalRMB = 0
	GCG = DEQiangHongBaoConfig.DEQiangHongBao_GoodsConfig_Dict.get
	for goodsId in goodsList:
		goodsCfg = GCG(goodsId, None)
		if goodsCfg:
			totalRMB += goodsCfg.needUnbindRMB
	
	couponCfg = DEQiangHongBaoConfig.DEQiangHongBao_CouponsConfig_Dict.get(couponCoding)
	if couponCfg:
		totalRMB -= min(int(totalRMB / 100.0 * couponCfg.discountPercent), couponCfg.maxDiscount)
	
	return int(totalRMB)


def OneMinBeforeQHB(callArgvs = None, regParam = None):
	'''
	抢红包提前一分钟广播处理
	'''
	if IS_START:
		cRoleMgr.Msg(11, 0, GlobalPrompt.DEQiangHongBao_Msg_OneMinBefore)
	
#===============================================================================
# 事件
#===============================================================================
def OnSyncOtherData(role, param = None):
	'''
	上线处理
	'''
	if IS_START:
		#同步活动状态
		role.SendObj(DEQiangHongBao_ActiveState_S, (IS_START, ENDTIME))
		#同步当前回合
		role.SendObj(DEQiangHongBao_RoundIndex_S, CURROUNDINDEX)
		

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DEQiangHongBao_OnOpenPanel", "双十一抢红包_请求打开操作面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DEQiangHongBao_OnClosePanel", "双十一抢红包_请求关闭操作面板"), OnClosePanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DEQiangHongBao_OnQiangHongBao", "双十一抢红包_请求抢红包"), OnQiangHongBao)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DEQiangHongBao_OnQiangGou", "双十一抢红包_请求抢购"), OnQiangGou)


