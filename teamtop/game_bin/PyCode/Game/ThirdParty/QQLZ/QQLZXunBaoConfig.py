#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZXunBaoConfig")
#===============================================================================
# 注释
#===============================================================================
import DynamicPath
import Environment

from Util.File import TabFile
if "_HasLoad" not in dir():
	FILE_FLODER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FLODER_PATH.AppendPath("QQLZ")
	
	QQLZXunBao_Config_Base = None	#活动控制配置
	
	QQLZXunBao_DICT = {}					#蓝钻寻宝奖励字典

class QQLZXunBao(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZXunBaoReward.txt")
	def __init__(self):
		self.rewardId = int
		self.item = self.GetEvalByString
		
class QQLZXunBaoBase(TabFile.TabLine):
	FilePath = FILE_FLODER_PATH.FilePath("QQLZXunBaoBase.txt")
	def __init__(self):
		self.activeTitle = str
		self.beginDate = self.GetDatetimeByString
		self.endDate = self.GetDatetimeByString
		self.needLevel = int
		
def LoadQQLZXunBao():
	global QQLZXunBao_DICT
	for cfg in QQLZXunBao.ToClassType():
		if cfg.rewardId in QQLZXunBao_DICT:
			print "GE_EXC, QQLZXunBao(id == %s) already have the data!" % id
		QQLZXunBao_DICT[cfg.rewardId] = cfg.item
		
def LoadQQLZXunBaoBase():
	global QQLZXunBao_Config_Base
	for cfg in QQLZXunBaoBase.ToClassType():
		if QQLZXunBao_Config_Base:
			print "GE_EXC, QQLZXunBao_Base already have data!"
		QQLZXunBao_Config_Base = cfg

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadQQLZXunBaoBase()
		LoadQQLZXunBao()
