#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZRollGiftConfig")
#===============================================================================
# 蓝钻转大礼配置
#===============================================================================
import DynamicPath
import Environment
from Util import Random
from Util.File import TabFile

if "_HasLoad" not in dir():
	QQHZ_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	QQHZ_FILE_FOLDER_PATH.AppendPath("QQLZ")
	
	QQLZ_KAITONG_REWARD_DICT = {} 	#QQ蓝钻转大礼礼包配置{LiBaoID：cfg}
	QQLZKTR_RANDOMER = Random.RandomRate() #蓝钻开通转大礼奖励随机器
	
class QQLZKaiTongReward(TabFile.TabLine):
	'''
	蓝钻开通转大礼奖励
	'''
	FilePath = QQHZ_FILE_FOLDER_PATH.FilePath("QQLZKaiTongReward.txt")
	def __init__(self):
		self.rewardId = int 
		self.rateItem = self.GetEvalByString	#(coding,cnt,rate)

def LoadQQLZKaiTongReward():
	global QQLZ_KAITONG_REWARD_DICT
	for cfg in QQLZKaiTongReward.ToClassType():
		if cfg.rewardId in QQLZ_KAITONG_REWARD_DICT:
			print "GE_EXC, repeat rewardId(%s) in QQLZ_KAITONG_REWARD_DICT" % cfg.rewardId
		QQLZ_KAITONG_REWARD_DICT[cfg.rewardId] = cfg
	
	AfterLoadQQLZKaiTongReward()

def AfterLoadQQLZKaiTongReward():
	'''
	蓝钻开通转大礼奖励生成器 配置加载之后初始化 
	'''
	global QQLZKTR_RANDOMER
	QQLZKTR_RANDOMER = Random.RandomRate()
	for _, cfg in QQLZ_KAITONG_REWARD_DICT.iteritems():
		rewardId = cfg.rewardId
		rate = cfg.rateItem[2]
		QQLZKTR_RANDOMER.AddRandomItem(rate, rewardId)

if '_HasLoad' not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQLZKaiTongReward()
