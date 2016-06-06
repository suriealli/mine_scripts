#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Pet.PetLuckyDraw")
#===============================================================================
# 宠物转转乐
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Activity import CircularDefine
from Game.Pet import PetConfig
from Game.Role import Event
from Game.Role.Data import EnumDayInt8, EnumTempObj
from Game.VIP import VIPConfig

if "_HasLoad" not in dir():
	
	IS_START = False		#活动是否开启
	
	#消息
	Pet_Lucky_Draw_Result = AutoMessage.AllotMessage("Pet_Lucky_Draw_Result", "通知客户端宠物转转乐结果")

def PetLuckyDraw(role):
	vip = role.GetVIP()
	if not vip:
		return
	
	#获取VIP配置
	vipConfig = VIPConfig._VIP_BASE.get(vip)
	if not vipConfig:
		return
	
	#是否有次数
	if role.GetDI8(EnumDayInt8.PetLuckyDrawCnt) >= vipConfig.petLuckyDrawCnt:
		return
	
	needRMB = EnumGameConfig.PET_LUCKY_DRAW_NEED_RMB
	#版本判断
	if Environment.EnvIsNA():
		needRMB = EnumGameConfig.PET_LUCKY_DRAW_NEED_RMB_NA
	elif Environment.EnvIsRU():
		needRMB = EnumGameConfig.PET_LUCKY_DRAW_NEED_RMB_RU
	
	#是否够RMB
	if role.GetUnbindRMB() < needRMB:
		return
	
	#扣RMB
	role.DecUnbindRMB(needRMB)
	#扣除次数
	role.IncDI8(EnumDayInt8.PetLuckyDrawCnt, 1)
	
	#随机一个奖励
	rewardId = PetConfig.LUCKY_DRAW_RANDOM.RandomOne()
	#北美通用活动
	if Environment.EnvIsNA():
		HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
		HalloweenNAMgr.PetLuckyDraw()
	#同步客户端
	role.SendObjAndBack(Pet_Lucky_Draw_Result, rewardId, 20, CallBackPetLuckyDraw, rewardId)
	

def CallBackPetLuckyDraw(role, callargv, regparam):
	'''
	宠物转转乐回调
	@param role:
	@param callargv:
	@param regparam:
	'''
	rewardId = regparam
	
	config = PetConfig.PET_LUCKY_DRAW.get(rewardId)
	if not config:
		return
	
	#日志
	with TraPetLuckyDrawReward:
		#发奖励
		role.AddItem(config.itemCoding, config.cnt)
		
	#提示
	role.Msg(2, 0, GlobalPrompt.PET_LUCKY_DRAW_REWARD_PROMPT % (config.itemCoding, config.cnt))

#===============================================================================
# 事件
#===============================================================================
def PetLuckyDrawStart(*param):
	'''
	宠物转转乐活动开启
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_PetLuckyDraw:
		return
	
	global IS_START
	if IS_START is True:
		print "GE_EXC, PetLuckyDraw is already start"
		return
	
	IS_START = True


def PetLuckyDrawEnd(*param):
	'''
	宠物转转乐活动关闭
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_PetLuckyDraw:
		return
	
	global IS_START
	if IS_START is False:
		print "GE_EXC, PetLuckyDraw is already end"
		return
	
	IS_START = False
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestPetLuckyDraw(role, msg):
	'''
	客户端请求宠物转转乐
	@param role:
	@param msg:
	'''
	#活动是否开始
	if IS_START is False:
		return
	
	#日志
	with TraPetLuckyDraw:
		PetLuckyDraw(role)

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_StartCircularActive, PetLuckyDrawStart)
		Event.RegEvent(Event.Eve_EndCircularActive, PetLuckyDrawEnd)
		
		#日志
		TraPetLuckyDraw = AutoLog.AutoTransaction("TraPetLuckyDraw", "宠物转转乐")
		TraPetLuckyDrawReward = AutoLog.AutoTransaction("TraPetLuckyDrawReward", "宠物转转乐奖励")
		
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Pet_Lucky_Draw", "客户端请求宠物转转乐"), RequestPetLuckyDraw)
		
	
