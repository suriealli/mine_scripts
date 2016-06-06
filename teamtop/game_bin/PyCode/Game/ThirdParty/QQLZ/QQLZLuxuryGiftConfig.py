#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZLuxuryGiftConfig")
#===============================================================================
# 蓝钻豪华六重礼配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("QQLZ")
	
	QQLZLuxuryGift_Config_Base = None	#活动控制配置
	QQLZLuxuryGift_Reward_Dict = {}		#奖励配置{rewardId:cfg}

class QQLZLuxuryGiftBase(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZLuxuryGiftBase.txt")
	def __init__(self):
		self.activeTitle = str
		self.beginDate = self.GetDatetimeByString
		self.endDate = self.GetDatetimeByString
		self.needLevel = int

class QQLZLuxuryGiftReward(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZLuxuryGiftReward.txt")
	def __init__(self):
		self.rewardId = int
		self.needKaiTongTimes = int
		self.item = self.GetEvalByString 

def LoadQQLZLuxuryGiftBase():
	global QQLZLuxuryGift_Config_Base
	for cfg in QQLZLuxuryGiftBase.ToClassType():
		if QQLZLuxuryGift_Config_Base:
			print "GE_EXC, QQLZLuxuryGift_Config_Base already have data!"
		QQLZLuxuryGift_Config_Base = cfg

def LoadQQLZLuxuryGiftReward():
	global QQLZLuxuryGift_Reward_Dict
	for cfg in QQLZLuxuryGiftReward.ToClassType():
		rewardId = cfg.rewardId 
		if rewardId in QQLZLuxuryGift_Reward_Dict:
			print "GE_EXC,repeat rewardId(%s) in QQLZLuxuryGift_Reward_Dict" % rewardId
		QQLZLuxuryGift_Reward_Dict[rewardId] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQLZLuxuryGiftBase()
		LoadQQLZLuxuryGiftReward()