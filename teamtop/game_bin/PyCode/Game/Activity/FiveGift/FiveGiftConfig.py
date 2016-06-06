#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FiveGift.FiveGiftConfig")
#===============================================================================
# 五重礼配置
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile
from Util import Random

FIVE_GIFT_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
FIVE_GIFT_FILE_FOLDER_PATH.AppendPath("FiveGift")

if "_HasLoad" not in dir():
	FIVE_GIFT_BASE = {}						#五重礼基础配置
	FIVE_GIFT_LUCKY_DRAW_CONFIG = {}		#五重礼抽奖配置
	FIVE_GIFT_LUCKY_DRAW_RANDOM = {}		#五重礼抽奖随机对象
	DAY_FIRST_PAY_REWARD = {}				#每日首充奖励配置
	
class FiveGiftBase(TabFile.TabLine):
	'''
	五重礼配置
	'''
	FilePath = FIVE_GIFT_FILE_FOLDER_PATH.FilePath("FiveGiftBase.txt")
	def __init__(self):
		self.giftId = int
		self.rewardItem = self.GetEvalByString
		self.rewardBindRMB = int
		self.rewardMoney = int
		
class FiveGiftLuckyDraw(TabFile.TabLine):
	'''
	五重礼抽奖配置
	'''
	FilePath = FIVE_GIFT_FILE_FOLDER_PATH.FilePath("FiveGiftLuckyDraw.txt")
	def __init__(self):
		self.choiceId = int
		self.needMoney = int
		self.OddsAndRewardMoney = self.GetEvalByString
		
class DayFirstPayReward(TabFile.TabLine):
	'''
	每日首充奖励配置
	'''
	FilePath = FIVE_GIFT_FILE_FOLDER_PATH.FilePath("DayFirstPayReward.txt")
	def __init__(self):
		self.days = int
		self.rewardItem = self.GetEvalByString
		self.rewardItem_hefu = self.GetEvalByString
		self.rewardBindRMB = int
		self.rewardBindRMB_hefu = int
		self.rewardMoney = int
		self.rewardMoney_hefu = int

def LoadFiveGiftBase():
	global FIVE_GIFT_BASE
	for config in FiveGiftBase.ToClassType():
		FIVE_GIFT_BASE[config.giftId] = config
		
def LoadFiveGiftLuckyDraw():
	global FIVE_GIFT_LUCKY_DRAW_CONFIG
	global FIVE_GIFT_LUCKY_DRAW_RANDOM
	for config in FiveGiftLuckyDraw.ToClassType():
		FIVE_GIFT_LUCKY_DRAW_CONFIG[config.choiceId] = config
		#生成随机对象
		r = Random.RandomRate()
		for data in config.OddsAndRewardMoney:
			r.AddRandomItem(*data)
		FIVE_GIFT_LUCKY_DRAW_RANDOM[config.choiceId] = r
		
def LoadDayFirstPayReward():
	global DAY_FIRST_PAY_REWARD
	for config in DayFirstPayReward.ToClassType():
		DAY_FIRST_PAY_REWARD[config.days] = config

if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadFiveGiftBase()
		LoadFiveGiftLuckyDraw()
		LoadDayFirstPayReward()
		
