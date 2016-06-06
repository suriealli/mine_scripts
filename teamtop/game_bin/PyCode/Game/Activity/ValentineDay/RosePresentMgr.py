#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.RosePresentMgr")
#===============================================================================
# 送人玫瑰Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Mail import Mail
from Game.Role.Data import EnumInt16, EnumInt32
from Game.Activity import CircularDefine
from Game.Role import KuaFu, Call, Event
from Game.Activity.ValentineDay import RosePresentConfig
import random

TYPE_ONE = 1	#一朵玫瑰花
TYPE_TWO = 2 	#九十九朵玫瑰花

if "_HasLoad" not in dir():
	IS_START = False
	
	Tra_RosePresent_SendNomalRose = AutoLog.AutoTransaction("Tra_RosePresent_SendNomalRose", "送人玫瑰_赠送1朵玫瑰")
	Tra_RosePresent_ReceiveNomalRose = AutoLog.AutoTransaction("Tra_RosePresent_ReceiveNomalRose", "送人玫瑰_收到1朵玫瑰")
	Tra_RosePresent_SendSuperRose = AutoLog.AutoTransaction("Tra_RosePresent_SendSuperRose", "送人玫瑰_赠送99朵玫瑰")
	Tra_RosePresent_ReceiveSuperRose = AutoLog.AutoTransaction("Tra_RosePresent_ReceiveSuperRose", "送人玫瑰_收到99朵玫瑰")
	
#### 活动控制  start ####
def OnStartRosePresent(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_RosePresent != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open RosePresent"
		return
		
	IS_START = True

def OnEndRosePresent(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_RosePresent != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end RosePresent while not start"
		return
		
	IS_START = False

#### 客户端请求  start ####
def OnSendRose(role, msg):
	'''
	送人玫瑰_赠送玫瑰
	@param msg: targetRoleId, roseType, sendCnt (目标角色ID, 赠送类型, 赠送数量)
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.RolePresent_NeedLevel:
		return
	
	targetRoleId, roseType, sendCnt = msg
	if sendCnt < 1:
		return
	
	roseCfg = RosePresentConfig.RosePresent_BaseConfig_Dict.get(roseType,None)
	if not roseCfg:
		return
	
	#拥有道具不足
	needCoding = roseCfg.needCoding
	if role.ItemCnt(needCoding) < sendCnt:
		return
	
	needMoney = roseCfg.needMoney * sendCnt
	if role.GetMoney() < needMoney:
		return
	
	# 自己送自己限制
	roleId = role.GetRoleID()
	if targetRoleId == roleId:
		return
	
	#非本服 
	if not KuaFu.IsLocalRoleByRoleID(targetRoleId):
		role.Msg(2, 0, GlobalPrompt.RosePresent_Tips_NotLocalServer)
		return
	
	#随机抽奖
	randomObj = RosePresentConfig.GetRandomObjByTypeAndLevel(roseType, roleLevel)
	if not randomObj:
		print "GE_EXC, OnSendRose::config error! can not get randomObj with roseType(%s), roleLevel(%s), roleId(%s)" % (roseType, roleLevel, roleId)
		return
	
	#组装随机返利奖励 以及 其中的珍贵获得
	rebateItemDict = {}
	preciousItemDict = {}
	for _ in xrange(sendCnt):
		rebateReward = randomObj.RandomOne()
		if not rebateReward:
			print "GE_EXC, can not random rebateReward with randomObj.randomList of roseType(%s)" % (randomObj.randomList, roseType)
			continue
		_, _, coding, cnt, isPrecious = rebateReward
		oldCnt = rebateItemDict.setdefault(coding, 0)
		rebateItemDict[coding] = oldCnt + cnt
		if isPrecious:
			oldCntEx = preciousItemDict.setdefault(coding,0)
			preciousItemDict[coding] = oldCntEx + cnt
	
	rewardGalmour = roseCfg.rewardSendGlamour * sendCnt
	prompt = GlobalPrompt.RosePresent_Tips_SendSucceed % (rewardGalmour)
	Tra_SendRose = Tra_RosePresent_SendNomalRose
	if roseType == TYPE_TWO:
		Tra_SendRose = Tra_RosePresent_SendSuperRose
	with Tra_SendRose:
		#扣除道具
		role.DelItem(needCoding, sendCnt)
		#扣金币
		role.DecMoney(needMoney)
		#获得随机返利道具
		for coding, cnt in rebateItemDict.iteritems():
			role.AddItem(coding, cnt)
			prompt += GlobalPrompt.RosePresent_Tips_Item % (coding, cnt)
		#魅力值获得
		if rewardGalmour:
			role.IncI32(EnumInt32.DayGlamourExp, rewardGalmour)
			role.IncI32(EnumInt32.HistoryGlamourExp, rewardGalmour)
		#处理赠送次数 
		if TYPE_TWO == roseType:
			role.IncI16(EnumInt16.RosePresentSendTimes, sendCnt)
			#触发魅力目标是否增加达标人数处理  
			Event.TriggerEvent(Event.Eve_AfterSendRose, role)
		#尝试入魅力榜
		Event.TriggerEvent(Event.Eve_TryInGlamorRank, role)
		#log
		AutoLog.LogBase(roleId, AutoLog.eveRosePresentDonate, (targetRoleId, needCoding, sendCnt))
	
	#离线命令执行赠送
	roleName = role.GetRoleName()
	Call.LocalDBCall(targetRoleId, ReceiveRoseDonate, (roleId, roleName, roseType, sendCnt))
	
	#赠送成功提示
	role.Msg(2, 0, prompt)
	#珍贵返利广播
	for coding, cnt in preciousItemDict.iteritems():
		cRoleMgr.Msg(11, 0, GlobalPrompt.RosePresent_Msg_Precious % (roleName, coding, cnt))
		

#离线命令执行 勿修改	
def ReceiveRoseDonate(role, param):
	'''
	送人玫瑰_赠送玫瑰  接受赠送的Role调用
	'''
	#解析参数
	roleId = role.GetRoleID()
	giveRoleId, giveRoleName, roseType, sendCnt = param
	roseCfg = RosePresentConfig.RosePresent_BaseConfig_Dict.get(roseType, None)
	if not roseCfg:
		return
	#组装内容
	content = GlobalPrompt.RosePresent_Mail_Content % (giveRoleName, roseCfg.needCoding, sendCnt)
	#process
	Tra_ReceiveRose = Tra_RosePresent_ReceiveNomalRose
	if roseType == TYPE_TWO:
		Tra_ReceiveRose = Tra_RosePresent_ReceiveSuperRose
	with Tra_ReceiveRose:
		#log
		AutoLog.LogBase(roleId, AutoLog.eveRosePresentReceive, (giveRoleId, roseCfg.needCoding, sendCnt))
		#发邮件
		receiveGlamour = roseCfg.rewardReceiverGlamour * sendCnt
		Mail.SendMail(roleId, GlobalPrompt.RosePresent_Mail_Title, GlobalPrompt.RosePresent_Mail_Sender, content)
		
		#邮件只是提示性 没有实质的东西 这里直接增加魅力值 触发入榜啥的
		if IS_START:
			role.IncI32(EnumInt32.DayGlamourExp, receiveGlamour)
			role.IncI32(EnumInt32.HistoryGlamourExp, receiveGlamour)
			#尝试入魅力榜
			Event.TriggerEvent(Event.Eve_TryInGlamorRank, role)
			
	#提示
	role.Msg(2, 0, content)	

def RosePresent_ExtendReward(role, param):
	'''
	副本和英灵神殿 通关活动期间概率获得 一朵玫瑰花
	'''
	global IS_START
	if not IS_START:
		return None
	
	activityType, idx = param	
	cfg = RosePresentConfig.RosePresent_RoseDropConfig_Dict.get((activityType, idx))
	if not cfg:
		return None
	
	rewardDict = {}
	#一朵玫瑰花掉落
	if random.randint(1, 10000) <= cfg.dropRate:
		rewardDict[cfg.proCoding] = 1
	
	return rewardDict
	
#### 事件 start 
def OnRoleDayClear(role, param):
	'''
	每日清理 
	'''
	#清理今日魅力值
	role.SetI32(EnumInt32.DayGlamourExp, 0)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartRosePresent)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndRosePresent)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RosePresent_OnSendRose", "送人玫瑰_请求赠送玫瑰"), OnSendRose)