#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.DoubleEleven.ElevenMallReward")
#===============================================================================
# 双十一商城消费返利  @author: Gaoshuai 2015
#===============================================================================
import Environment
from Game.Role import Event
from Common.Other import EnumGameConfig
from Common.Message import AutoMessage
from Game.Activity import CircularDefine
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt
from Game.Role.Mail import Mail
from Game.Role.Data import EnumObj
from Game.Activity.DoubleEleven.ElevenMallRewardConfig import ElevenMallRewardDict, ElevenMallRewardList
from Game.Activity.DoubleEleven.ElevenActivityDefine import ElevenMallReward


if "_HasLoad" not in dir():
	IsStart = False
	#消息
	MallConsume = AutoMessage.AllotMessage("ElevenMallConsumeData", "商城消费数据")
	#日志
	ElevenMallRewardLog = AutoLog.AutoTransaction("ElevenMallRewardLog", "双十一商城满返邮件发奖 ")
	
def StartCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_ElevenMallReward:
		return
	if IsStart:
		print 'GE_EXC, ElevenMallReward is already start'
	IsStart = True

def EndCircularActive(param1, param2):
	global IsStart
	if param2 != CircularDefine.CA_ElevenMallReward:
		return
	if not IsStart:
		print 'GE_EXC, ElevenMallReward is already end'
	IsStart = False
	
def RoleDayClear(role, param=None):
	'''
	每日清理玩家数据，发奖
	@param role:
	@param param: None
	'''
	mallRMB = role.GetObj(EnumObj.ElevenActData).get(ElevenMallReward, 0)
	if mallRMB == 0:
		return
	#商城消费神石不够第一等级直接清理数据
	if mallRMB < ElevenMallRewardList[0]:
		role.GetObj(EnumObj.ElevenActData)[ElevenMallReward] = 0
		return
	#确定奖励阶段
	tmpRMB = 0
	for i in ElevenMallRewardList:
		if mallRMB >= i:
			tmpRMB = i
			continue
		break
	percent = ElevenMallRewardDict.get(tmpRMB, 0)
	
	rewardRMB = mallRMB * percent / 100
	mailContent = GlobalPrompt.ElevenMallRewardContent % (mallRMB, rewardRMB)
	with ElevenMallRewardLog:
		role.GetObj(EnumObj.ElevenActData)[ElevenMallReward] = 0
		Mail.SendMail(role.GetRoleID(), GlobalPrompt.ElevenMallRewardTitle, GlobalPrompt.Sender, mailContent , unbindrmb=rewardRMB)
	
def SyncRoleData(role, param=None):
	'''
	@param role:
	@param param: None
	'''
	global IsStart
	if not IsStart: return
	
	if role.GetLevel() < EnumGameConfig.ElevenMallReward_NeedLevel:
		return
	
	role.SendObj(MallConsume, role.GetObj(EnumObj.ElevenActData).get(ElevenMallReward, 0))
	
#响应商城消费函数
def MallAddConsume(role, RMBConsume):
	'''
	@param role:
	@param RMBConsume: 本次消费神石数
	'''
	global IsStart
	if not IsStart:return 
	
	if role.GetLevel() < EnumGameConfig.ElevenMallReward_NeedLevel:
		return
	
	role.GetObj(EnumObj.ElevenActData)[ElevenMallReward] = role.GetObj(EnumObj.ElevenActData).get(ElevenMallReward, 0) + RMBConsume
	
	role.SendObj(MallConsume, role.GetObj(EnumObj.ElevenActData).get(ElevenMallReward, 0))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleData)
