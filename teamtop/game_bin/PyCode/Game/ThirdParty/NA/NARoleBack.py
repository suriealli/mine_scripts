#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.NA.NARoleBack")
#===============================================================================
# 北美角色召回奖励
#===============================================================================
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt
from Game.Role.Mail import Mail
from Game.Item import ItemConfig

if "_HasLoad" not in dir():
	Tra_NARoleBack = AutoLog.AutoTransaction("Tra_NARoleBack", "北美角色召回奖励")

def NABackReward(role, param):
	'''
	北美角色召回奖励
	@param role:
	@param param:(itemCoding, itemcnt unixtime))
	'''
	itemCoding, itemcnt, unixtime = param
	if not itemCoding or not itemcnt:
		return
	if not ItemConfig.CheckItemCoding(itemCoding):
		print "GE_EXC, NARoleBack itemcoding(%s) is Wrong" % itemCoding
		return
	with Tra_NARoleBack:
		roleId = role.GetRoleID()
		#玩家等级，是否重复领取经确认无需判断
		#发邮件，需要邮件内容
		Mail.SendMail(roleId, GlobalPrompt.NARoleBack_TITKE, GlobalPrompt.NARoleBack_SENDER, \
					GlobalPrompt.NARoleBack_DESC, items = [(itemCoding, itemcnt)])
		#记录日志，需要记录时间unixtime
		AutoLog.LogBase(roleId, AutoLog.eveNARoleBackReward, unixtime)
		
		