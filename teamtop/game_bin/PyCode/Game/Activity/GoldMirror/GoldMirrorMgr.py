#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GoldMirror.GoldMirrorMgr")
#===============================================================================
# 金币副本
#===============================================================================
import cRoleMgr
import cDateTime
import Environment
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Activity.GoldMirror import GoldMirrorConfig
from Game.Role import Status
from Game.Role.Data import  EnumTempObj, EnumInt1, EnumDayInt8
from Game.Scene import GoldMirror
from Game.SysData import WorldData

if "_HasLoad" not in dir():
	GoldPickGold= AutoLog.AutoTransaction("GoldPickGold", "经验副本直接获取金币")
	
def OnRoleJoinGoldStage(role, msg):
	'''
	请求挑战金币副本
	@param role:
	@param msg:0-进入金币副本挑战, 1-不进入直接领取奖励, 2-不进入花费神石领取奖励
	'''
	if role.GetLevel() < EnumGameConfig.WP_GoldLevel:
		role.Msg(2, 0, GlobalPrompt.WPG_LevelLimit)
		return
	if role.GetDI8(EnumDayInt8.GoldDropAwardCnt_1) > 100:
		return
	if role.GetDI8(EnumDayInt8.GoldDropAwardCnt_1) >= WorldData.GetGoldMirrorCnt_1():
		role.Msg(2, 0, GlobalPrompt.WPG_NoCnt)
		return
	
	stageCfg = GoldMirrorConfig.GOLD_STAGE_DICT.get(1)
	if not stageCfg:
		print "GE_EXC,can not find GoldMirrorConfig's GoldMirror by id=(%s)" % 1
		return
	
	if not Status.CanInStatus(role, EnumInt1.ST_InMirror):
		#状态管理 
		return
	
	#判断是否在副本中
	if role.GetTempObj(EnumTempObj.MirrorScene):
		return
	
	if not msg:
		#增加挑战次数
		role.IncDI8(EnumDayInt8.GoldDropAwardCnt_1, 1)
		GoldMirror.GoldMirror(role, stageCfg, days=cDateTime.Days())
		return
	
	#vip7以上才能跑后面的逻辑
	if role.GetVIP() < 7:
		return
	
	level = role.GetLevel()
	cfg = GoldMirrorConfig.GoldPickLimit_Dict.get(level)
	if not cfg:
		print 'GE_EXC, OnRoleJoinGoldStage can not find level %s in GoldPickLimit_Dict' % level
		return
	
	config = GoldMirrorConfig.GOLD_DROP_LIMIT.get(level)
	if not config:
		print 'GE_EXC, OnRoleJoinGoldStage can not find level %s in GOLD_DROP_LIMIT' % level
		return
	
	with GoldPickGold:
		if msg == 1:
			#不花费神石
			#增加挑战次数
			role.IncDI8(EnumDayInt8.GoldDropAwardCnt_1, 1)
			role.IncDI8(EnumDayInt8.GoldDropAwardCnt_2, 1)
			
			role.IncMoney(cfg.maxMoney + config.maxMoney)
			
			role.Msg(2, 0, GlobalPrompt.WPG_Pick % cfg.maxMoney)
			role.Msg(2, 0, GlobalPrompt.WPG_Drop % config.maxMoney)
		else:
			#话费神石
			if role.GetUnbindRMB() < cfg.useRMB:
				return
			#增加挑战次数
			role.IncDI8(EnumDayInt8.GoldDropAwardCnt_1, 1)
			role.IncDI8(EnumDayInt8.GoldDropAwardCnt_2, 1)
			
			role.DecUnbindRMB(cfg.useRMB)
			
			role.IncMoney((cfg.maxMoney + config.maxMoney * 2))
			
			role.Msg(2, 0, GlobalPrompt.WPG_Pick % cfg.maxMoney)
			role.Msg(2, 0, GlobalPrompt.WPG_Drop % (config.maxMoney * 2))
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("GoldStage_OnRoleJoinStage", "请求挑战金币副本"), OnRoleJoinGoldStage)