#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KongJianDecennial.KongJianExchangeConfig")
#===============================================================================
# 周年纪念币 config
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Game.Activity.KongJianDecennial import KongJianRechargeConfig

if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("KongJianDecennial")
	
	KJD_ExchangeConfig_Dict = {}		#空间十周年周年纪念币奖励配置 {exchangeIndex:{levelRangeId:rewardCfg,},}
	
class KongJianDecennialExchange(TabFile.TabLine):
	'''
	奖励配置
	'''
	FilePath = FILE_FLODER_PATH.FilePath("KongJianDecennialExchange.txt")
	def __init__(self):
		self.exchangeIndex = int
		self.levelRangeId = int
		self.needExchangeCoin = int
		self.rewardItems = self.GetEvalByString
		self.rewardBindRMB = int
		self.rewardMoney = int
		self.rewardExchangeCoin = int

def LoadKongJianDecennialExchange():
	global KJD_ExchangeConfig_Dict
	for cfg in KongJianDecennialExchange.ToClassType():
		exchangeIndex = cfg.exchangeIndex
		levelRangeId = cfg.levelRangeId
		exchangeIndexDict = KJD_ExchangeConfig_Dict.setdefault(exchangeIndex,{})
		if levelRangeId in exchangeIndexDict:
			print "GE_EXC,repeat levelRangeId(%s) and exchangeIndex(%s) in KJD_ExchangeConfig_Dict" % (levelRangeId, exchangeIndex)
		exchangeIndexDict[levelRangeId] = cfg

def GetCfgByIndexAndLevel(exchangeIndex, roleLevel):
	'''
	返回对应exchangeIndex和roleLevel的兑换配置
	'''
	exchangeIndexDict = KJD_ExchangeConfig_Dict.get(exchangeIndex)
	if not exchangeIndexDict:
		return None
	
	tmpLevelRangeId = KongJianRechargeConfig.GetLevelRangeIdByLevel(roleLevel)
	if (not tmpLevelRangeId) or (tmpLevelRangeId not in exchangeIndexDict):
		return None
	else:
		return exchangeIndexDict.get(tmpLevelRangeId)
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadKongJianDecennialExchange()