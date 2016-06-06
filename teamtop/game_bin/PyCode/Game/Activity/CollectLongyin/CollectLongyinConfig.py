#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.CollectLongyin.CollectLongyinConfig")
#===============================================================================
# 每日集龙印
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	#配置
	CLFILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	CLFILE_FOLDER_PATH.AppendPath("CollectLongyin")
	
	CollectRmbReward_Dict = {}
	CollectLongyinReward_Dict = {}
	CollectBuqian_Dict = {}
	CollectQiandao_Dict = {}		#签到奖励{1:cfg}
	CollectQiandaoLevel_List = []
	
class CollectRmbRewardConfig(TabFile.TabLine):
	FilePath = CLFILE_FOLDER_PATH.FilePath("CollectLongyinRmbReward.txt")
	def __init__(self):
		self.rewardIndex = int				#充值神石奖励索引
		self.needRMB = int					#需要充值神石
		self.rewardLongyin = int			#奖励龙印
		
class CollectLongRewardConfig(TabFile.TabLine):
	FilePath = CLFILE_FOLDER_PATH.FilePath("CollectLongReward.txt")
	def __init__(self):
		self.rewardIndex = int				#奖励索引
		self.needLongyinCnt = int			#领取奖励需要龙印个数
		self.rewardItem = eval				#奖励物品
		self.rewardBindRMB = int			#奖励魔晶
		
class CollectBuqianConfig(TabFile.TabLine):
	FilePath = CLFILE_FOLDER_PATH.FilePath("CollectBuqian.txt")
	def __init__(self):
		self.buqianCnt = int
		self.needUnbindRMB = int
	
class CollectQiandaoConfig(TabFile.TabLine):
	FilePath = CLFILE_FOLDER_PATH.FilePath("SignReward.txt")
	def __init__(self):
		self.minLevel = int
		self.rewardItem = eval
		self.rewardMoney = int
		
def LoadCollectQiandaoConfig():
	global CollectQiandao_Dict, CollectQiandaoLevel_List
	for CQC in CollectQiandaoConfig.ToClassType():
		if CQC.minLevel in CollectQiandao_Dict:
			print 'GE_EXC, repeat minLevel %s in CollectQiandao_Dict' % CQC.minLevel
			continue
		CollectQiandao_Dict[CQC.minLevel] = CQC
		CollectQiandaoLevel_List.append(CQC.minLevel)
	CollectQiandaoLevel_List.sort()
	
def LoadCollectBuqianConfig():
	global CollectBuqian_Dict
	for CBC in CollectBuqianConfig.ToClassType():
		if CBC.buqianCnt in CollectBuqian_Dict:
			print 'GE_EXC, repeat buqianCnt %s in CollectBuqian_Dict' % CBC.buqianCnt
			continue
		CollectBuqian_Dict[CBC.buqianCnt] = CBC
	
def LoadCollectLongRewardConfig():
	global CollectLongyinReward_Dict
	for CLR in CollectLongRewardConfig.ToClassType():
		if CLR.rewardIndex in CollectLongyinReward_Dict:
			print 'GE_EXC, repeat rewardIndex %s in CollectLongyinReward_Dict' % CLR.rewardIndex
			continue
		CollectLongyinReward_Dict[CLR.rewardIndex] = CLR
	
def LoadCollectRmbRewardConfig():
	global CollectRmbReward_Dict
	for CRR in CollectRmbRewardConfig.ToClassType():
		if CRR.rewardIndex in CollectRmbReward_Dict:
			print 'GE_EXC, repeat rewardIndex %s in CollectRmbReward_Dict'
			continue
		CollectRmbReward_Dict[CRR.rewardIndex] = CRR
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadCollectQiandaoConfig()
		LoadCollectBuqianConfig()
		LoadCollectLongRewardConfig()
		LoadCollectRmbRewardConfig()
		
		
		