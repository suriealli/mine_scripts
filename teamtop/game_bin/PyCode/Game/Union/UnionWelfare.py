#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionWelfare")
#===============================================================================
# 公会福利
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumDayInt1, EnumObj
from Game.Union import UnionConfig
from Common.Other import GlobalPrompt

if "_HasLoad" not in dir():
	#消息
	Union_Show_Achievement_Box_Panel = AutoMessage.AllotMessage("Union_Show_Achievement_Box_Panel", "通知客户端显示公会成就宝箱面板")

def ShowAchievementBoxPanel(role):
	'''
	显示成就宝箱面板
	@param role:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	unionObjDict = role.GetObj(EnumObj.Union)
	
	#已经领取的宝箱列表
	hasGetAchievementBoxIdList = unionObjDict[1]
	
	role.SendObj(Union_Show_Achievement_Box_Panel, hasGetAchievementBoxIdList)

def GetDayBox(role, backFunId):
	'''
	领取每日宝箱
	@param role:
	@param backFunId:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	#今日是否已经领取
	if role.GetDI1(EnumDayInt1.UnionDayBox):
		return
	
	#每日宝箱配置
	dayBoxConfig = UnionConfig.UNION_DAY_BOX.get(unionObj.level)
	if not dayBoxConfig:
		return
	
	#是否满足历史贡献条件
	if role.GetHistoryContribution() < dayBoxConfig.needContribution:
		return
	
	#设置已领取
	role.SetDI1(EnumDayInt1.UnionDayBox, 1)
	
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		#奖励
		role.IncMoney(dayBoxConfig.money_fcm)
		role.AddItem(*dayBoxConfig.item_fcm)
	elif yyAntiFlag == 0:
		#奖励
		role.IncMoney(dayBoxConfig.money)
		role.AddItem(*dayBoxConfig.item)
	else:
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	
	#回调成功
	role.CallBackFunction(backFunId, None)
	
def GetAchievementBox(role, boxId, backFunId):
	'''
	领取成就宝箱
	@param role:
	@param boxId:
	@param backFunId:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	unionObjDict = role.GetObj(EnumObj.Union)
	hasGetAchievementBoxIdList = unionObjDict[1]
	
	#公会等级是否满足要求
	if boxId > unionObj.level:
		return
	
	#是否已经领取过
	if boxId in hasGetAchievementBoxIdList:
		return
	
	#配置
	achievementBoxConfig = UnionConfig.UNION_ACHIEVEMENT_BOX.get(boxId)
	if not achievementBoxConfig:
		return
	
	#历史贡献是否满足
	if role.GetHistoryContribution() < achievementBoxConfig.devote:
		return
	
	#设置领取状态
	hasGetAchievementBoxIdList.append(boxId)
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		role.IncMoney(achievementBoxConfig.money_fcm)
		role.IncBindRMB(achievementBoxConfig.bindRMB_fcm)
		role.AddItem(*achievementBoxConfig.item_fcm)
	elif yyAntiFlag == 0:
		role.IncMoney(achievementBoxConfig.money)
		role.IncBindRMB(achievementBoxConfig.bindRMB)
		role.AddItem(*achievementBoxConfig.item)
	else:
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	
	#回调客户端领取成功
	role.CallBackFunction(backFunId, None)
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestUnionOpenAchievementBoxPanel(role, msg):
	'''
	客户端请求打开成就宝箱面板
	@param role:
	@param msg:
	'''
	ShowAchievementBoxPanel(role)
	

def RequestUnionGetDayBox(role, msg):
	'''
	客户端请求领取公会每日宝箱
	@param role:
	@param msg:
	'''
	backFunId, _ = msg
	
	#日志
	with TraUnionGetDayBox:
		GetDayBox(role, backFunId)
	
def RequestUnionGetAchievementBox(role, msg):
	'''
	客户端请求领取公会成就宝箱
	@param role:
	@param msg:
	'''
	backFunId, data = msg
	boxId = data
	
	#日志
	with TraUnionGetAchievementBox:
		GetAchievementBox(role, boxId, backFunId)
	

if "_HasLoad" not in dir():
	#日志
	TraUnionGetAchievementBox = AutoLog.AutoTransaction("TraUnionGetAchievementBox", "公会领取成就宝箱")
	TraUnionGetDayBox = AutoLog.AutoTransaction("TraUnionGetDayBox", "公会领取每日宝箱")
	if Environment.HasLogic and not Environment.IsCross:
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Achievement_Box_Panel", "客户端请求打开成就宝箱面板"), RequestUnionOpenAchievementBoxPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Get_Achievement_Box", "客户端请求领取公会成就宝箱"), RequestUnionGetAchievementBox)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Get_Day_Box", "客户端请求领取公会每日宝箱"), RequestUnionGetDayBox)
		
