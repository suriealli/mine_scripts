#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.MoLingDraw.MoLingLuckyDraw")
#===============================================================================
# 魔灵大转盘
#===============================================================================
import cRoleMgr
import Environment
import MoLingLuckyDrawConfig
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Role import Event
from Game.Role.Data import EnumDayInt8

if "_HasLoad" not in dir():
	
	IS_START = False		#活动是否开启
	
	#消息
	MoLing_Lucky_Draw_Result = AutoMessage.AllotMessage("MoLing_Lucky_Draw_Result", "通知客户端魔灵大转盘的结果")
	#日志
	MoLing_Lucky_Draw_Cost = AutoLog.AutoTransaction("MoLing_Lucky_Draw_Cost", "扣除魔灵大转盘需要的神石")
	TraMoLingLuckyDraw = AutoLog.AutoTransaction("TraMoLingLuckyDraw", "魔灵大转盘")
	TraMoLingLuckyDrawReward = AutoLog.AutoTransaction("TraMoLingLuckyDrawReward", "魔灵大转盘奖励")
	
def MoLingLuckyDraw(role):

	vip = role.GetVIP()
	if not vip:
		return
	if vip > 20:
		#本活动配置的最大 VIP为20级,VIP超过20级时按20级计算
		vip = 20
		print "GE_EXC,can not find vip(%s) in MoLingLuckyDraw" % vip
	
	#获取VIP配置
	MoLingDrawCnt = MoLingLuckyDrawConfig.MOLING_LUCKY_DRAW_VIP_CONFIG.get(vip)

	if not MoLingDrawCnt:
		return
	#是否有次数
	if role.GetDI8(EnumDayInt8.MoLingDrawCnt) >= MoLingDrawCnt:
		return
	
	needRMB = EnumGameConfig.MOLING_LUCKY_DRAW_NEED_RMB
	if Environment.EnvIsNA():
		needRMB = EnumGameConfig.MOLING_LUCKY_DRAW_NEED_RMB_NA
	#是否够RMB
	if role.GetUnbindRMB() < needRMB:
		return
	
	#随机一个奖励
	rewardId = MoLingLuckyDrawConfig.LUCKY_DRAW_RANDOM.RandomOne()
	config = MoLingLuckyDrawConfig.MOLING_LUCKY_DRAW.get(rewardId)
	if not config:
		print "GE_EXC, MoLingLuckyDraw not config (%s)" % rewardId
		return
	
	#扣RMB
	with MoLing_Lucky_Draw_Cost:
		role.DecUnbindRMB(needRMB)
	#扣除次数
	role.IncDI8(EnumDayInt8.MoLingDrawCnt, 1)
	
	#同步客户端
	role.SendObjAndBack(MoLing_Lucky_Draw_Result, [rewardId], 20, CallBackMoLingLuckyDraw, (config.itemCoding, config.cnt))
	

def CallBackMoLingLuckyDraw(role, callargv, regparam):
	'''
	魔灵大转盘回调
	@param role:
	@param callargv:
	@param regparam:
	'''
	itemCoding, cnt = regparam
	#日志
	with TraMoLingLuckyDrawReward:
		#发奖励
		role.AddItem(itemCoding, cnt)
		
	#提示
	role.Msg(2, 0, GlobalPrompt.MOLING_LUCKY_DRAW_REWARD_PROMPT % (itemCoding, cnt))

#===============================================================================
# 事件
#===============================================================================
def MoLingLuckyDrawStart(*param):
	'''
	魔灵大转盘活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_MoLingLuckyDraw:
		return
	
	global IS_START
	if IS_START is True:
		print "GE_EXC, MoLingLuckyDraw is already start"
		return
	
	IS_START = True


def MoLingLuckyDrawEnd(*param):
	'''
	魔灵大转盘活动关闭
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_MoLingLuckyDraw:
		return
	
	global IS_START
	if IS_START is False:
		print "GE_EXC, MoLingLuckyDraw is already end"
		return
	
	IS_START = False
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestMoLingLuckyDraw(role, msg):
	'''
	客户端请求魔灵大转盘
	@param role:
	@param msg:
	'''

	#活动是否开始
	if IS_START is False:
		return
	
	#日志
	with TraMoLingLuckyDraw:
		MoLingLuckyDraw(role)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and (Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsRU() or Environment.EnvIsNA() or Environment.EnvIsPL()):
		#事件
		Event.RegEvent(Event.Eve_StartCircularActive, MoLingLuckyDrawStart)
		Event.RegEvent(Event.Eve_EndCircularActive, MoLingLuckyDrawEnd)
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("MoLing_Lucky_Draw", "客户端请求魔灵大转盘"), RequestMoLingLuckyDraw)
		
	
