#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.InviteFriendAndShare.InviteFriendAndShareConfig")
#===============================================================================
# 好友邀请和分享配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	InviteFriend_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	InviteFriend_FILE_FOLDER_PATH.AppendPath("InviteFriend")
	
	InviteFriend_Dict = {}
	InviteFriendReward_Dict = {}
	
	randomRewardIndex = Random.RandomRate()
	
class InviteFriendConfig(TabFile.TabLine):
	FilePath = InviteFriend_FILE_FOLDER_PATH.FilePath("InviteFriend.txt")
	def __init__(self):
		self.index = int
		self.BigType = int
		self.DayClear = int
		
def LoadInviteFriendConfig():
	global InviteFriend_Dict
	for ifc in InviteFriendConfig.ToClassType():
		if ifc.index in InviteFriend_Dict:
			print "GE_EXC, repeat index (%s) in InviteFriend_Dict" % ifc.index
			continue
		InviteFriend_Dict[ifc.index] = ifc

class InviteFriendRewardConfig(TabFile.TabLine):
	FilePath = InviteFriend_FILE_FOLDER_PATH.FilePath("InviteFriendReward.txt")
	def __init__(self):
		self.index = int
		self.reward = eval
		self.rate = int
		self.items = self.GetEvalByString
		self.bindRMB = self.GetIntByString
	
def LoadInviteFriendRewardConfig():
	global InviteFriendReward_Dict
	for ifcr in InviteFriendRewardConfig.ToClassType():
		if ifcr.index in InviteFriendReward_Dict:
			print "GE_EXC, repeat index (%s) in InviteFriendReward_Dict" % ifcr.index
			continue
		InviteFriendReward_Dict[ifcr.index] = ifcr
		randomRewardIndex.AddRandomItem(ifcr.rate, ifcr.index)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadInviteFriendConfig()
		LoadInviteFriendRewardConfig()
		
	