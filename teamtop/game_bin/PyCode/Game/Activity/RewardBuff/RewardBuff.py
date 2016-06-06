#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.RewardBuff.RewardBuff")
#===============================================================================
# 奖励加成buff
#===============================================================================
import math
import Environment
from Game.Role import Event
from Game.Activity.RewardBuff import RewardBuffConfig
from Game.SysData import WorldData
from Game.ThirdParty.QQLZ import QQLZShopMgr
from Common.Other import EnumGameConfig

if "_HasLoad" not in dir():
	pass

enHunluanSpace = 1			#混乱时空
enDukeOnDuty = 2			#城主轮值
enGloryWar = 3				#荣耀之战
enEvilHole = 4				#恶魔深渊
enClashOfTitans = 5			#诸神之战
enDailyFB = 6				#勇者试炼场
enMarryParty = 7			#婚礼派对

def GetRewardBuffCoef(index):
	'''返回奖励buff系数'''
	coef = 0
	if not WorldData.WD.returnDB:
		#依赖世界等级
		return coef
	buffId = RewardBuffConfig.RewardBuffIndexToId_Dict.get(index)
	if not buffId:
		#活动没有开启
		return coef
	cfg = RewardBuffConfig.RewardBuff_Dict.get(buffId)
	if not cfg:
		return coef
	if cfg.needWorldLevel > WorldData.GetWorldLevel():
		#世界等级不够
		return coef
	if cfg.buffCoef >= 10000:
		coef = cfg.buffCoef / 10000.0
		return coef - 1
	else:
		return coef

def CalNumber(index, nu):
	return int(math.ceil(nu * (1 + GetRewardBuffCoef(index))))

def CalNumberRole(role, index, nu):
	coef = GetRewardBuffCoef(index)
	if QQLZShopMgr.IsQQLZ(role):
		coef += EnumGameConfig.QQLZDailyFBBuff / 10000.0
	return int(math.ceil(nu * (1 + coef)))
	
def SyncRoleOtherData(role, param):
	role.SendObj(RewardBuffConfig.RewardBuffData, RewardBuffConfig.RewardBuffAct_Dict)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	
