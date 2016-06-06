#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.AutumnFestival.AutumnFestivalConfig")
#===============================================================================
# 中秋活动配置 akm
#===============================================================================
import DynamicPath
import Environment
from Util.File import TabFile

if "_HasLoad" not in dir():
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("AutumnFestival")
	
	AFC_CONFIG_DICT = {}  			#中秋活动控制配置 {id:cfg}
	AF_EXTRA_LATTERY_DICT = {}		#中秋每日充值神石获得额外搏饼次数配置{value:extraNum}
	AF_DAILY_LIBAO_DICT = {}		#中秋登陆礼包配置{id:cfg}
	AF_LATTERY_REWARD_DICT = {}		#中秋搏饼奖励{id:cfg}	
	
#中秋活动控制配置
class AFCConfig(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath('AFCConfig.txt')
	def __init__(self):
		self.id = int
		self.title = str
		self.beginDate = self.GetEvalByString
		self.endDate = self.GetEvalByString
		self.needLevel = int

#神石充值额外获得搏饼次数配置
class AFExtraLattery(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath('AFExtraLattery.txt')
	def __init__(self):
		self.id = int
		self.value = int 
		self.extraNum = int 

#中秋登陆礼包配置
class AFDailyLiBao(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath('AFDailyLiBao.txt')
	def __init__(self):
		self.id = int 
		self.items = self.GetEvalByString

#搏饼奖励
class AFLatteryReward(TabFile.TabLine):
	FilePath = FILE_FOLDER_PATH.FilePath('AFLatteryReward.txt')
	def __init__(self):
		self.id = int 
		self.name = str
		self.nomalItems = self.GetEvalByString
		self.extraItems = self.GetEvalByString
		self.rewardCoin = int

def LoadAFCConfig():
	global AFC_CONFIG_DICT	
	for cfg in AFCConfig.ToClassType():
		if cfg.id in AFC_CONFIG_DICT:
			print "GE_EXC, Autumn Festival Control Config::repeat id(%s)" % cfg.id		
		#1->中秋登陆  2-> 中秋搏饼
		if cfg.id < 1 or cfg.id > 2:
			print "GE_EXC, Autumn Festival Control Config::error id(%s)" % cfg.id
			continue
		AFC_CONFIG_DICT[cfg.id] = cfg

def LoadAFExtraLattery():
	global AF_EXTRA_LATTERY_DICT
	for cfg in AFExtraLattery.ToClassType():
		if cfg.id in AF_EXTRA_LATTERY_DICT:
			print "GE_EXC, Autumn Festival Extra Lattery::repeat id(%s)" % cfg.id
		if cfg.id % 2 != 0 and cfg.id != 1:
			print "GE_EXC,Autumn Festival Extra Lattery::error id(%s)" % cfg.id
		AF_EXTRA_LATTERY_DICT[cfg.id] = cfg

def LoadAFDailyLiBao():
	global AF_DAILY_LIBAO_DICT
	for cfg in AFDailyLiBao.ToClassType():
		if cfg.id in AF_DAILY_LIBAO_DICT:
			print "GE_EXC, Autumn Festival Daily LiBao::repeat id(%s)" % cfg.id
		AF_DAILY_LIBAO_DICT[cfg.id] = cfg

def LoadAFLatteryReward():
	global AF_LATTERY_REWARD_DICT
	for cfg in AFLatteryReward.ToClassType():
		if cfg.id in AF_LATTERY_REWARD_DICT:
			print "GE_EXC, Autumn Festival Lattery Reward::repeat id(%s)" % cfg.id
		AF_LATTERY_REWARD_DICT[cfg.id] = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadAFCConfig()
		LoadAFExtraLattery()
		LoadAFDailyLiBao()
		LoadAFLatteryReward()