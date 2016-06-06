#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SuperInvest.SuperInvestConfig")
#===============================================================================
# 超级投资配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	SI_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	SI_FILE_FOLDER_PATH.AppendPath("SuperInvest")
	
	SuperInvest_Dict = {}

class SuperInvestConfig(TabFile.TabLine):
	FilePath = SI_FILE_FOLDER_PATH.FilePath("SuperInvestLevel.txt")
	def __init__(self):
		self.InvestIndex = int										#超级投资索引
		self.needLevel = eval										#开启需要等级
		self.needRMB = int											#投资需要充值神石
		
		self.rewardItems1 = eval									#第一个奖励道具
		self.rewardTili1 = int										#第一个奖励体力
		self.rewardBindRMB1 = int									#第一个奖励魔晶
		self.needDay1 = int											#第一个奖励需要登录天数
		self.rewardItems2 = eval									#第二个奖励道具
		self.rewardTili2 = int										#第二个奖励体力
		self.rewardBindRMB2 = int									#第二个奖励魔晶
		self.needDay2 = int											#第二个奖励需要登录天数
		self.rewardItems3 = eval									#第三个奖励道具
		self.rewardTili3 = int										#第三个奖励体力
		self.rewardBindRMB3 = int									#第三个奖励魔晶
		self.needDay3 = int											#第三个奖励需要登录天数
		self.rewardItems4 = eval									#第四个奖励道具
		self.rewardTili4 = int										#第四个奖励体力
		self.rewardBindRMB4 = int									#第四个奖励魔晶
		self.needDay4 = int											#第四个奖励需要登录天数
		self.rewardItems5 = eval									#第五个奖励道具
		self.rewardTili5 = int										#第五个奖励体力
		self.rewardBindRMB5 = int									#第五个奖励魔晶
		self.needDay5 = int											#第五个奖励需要登录天数
		self.rewardItems6 = eval									#第六个奖励道具
		self.rewardTili6 = int										#第六个奖励体力
		self.rewardBindRMB6 = int									#第六个奖励魔晶
		self.needDay6 = int											#第六个奖励需要登录天数
		self.rewardItems7 = eval									#第七个奖励道具
		self.rewardTili7 = int										#第七个奖励体力
		self.rewardBindRMB7 = int									#第七个奖励魔晶
		self.needDay7 = int											#第七个奖励需要登录天数
		self.rewardItems8 = eval									#第八个奖励道具
		self.rewardTili8 = int										#第八个奖励体力
		self.rewardBindRMB8 = int									#第八个奖励魔晶
		self.needDay8 = int											#第八个奖励需要登录天数
		
	def InitReward(self):
		self.dayReward = {}
		
		self.dayReward[self.needDay1] = {1:self.rewardItems1, 2:self.rewardTili1, 3:self.rewardBindRMB1}
		self.dayReward[self.needDay2] = {1:self.rewardItems2, 2:self.rewardTili2, 3:self.rewardBindRMB2}
		self.dayReward[self.needDay3] = {1:self.rewardItems3, 2:self.rewardTili3, 3:self.rewardBindRMB3}
		self.dayReward[self.needDay4] = {1:self.rewardItems4, 2:self.rewardTili4, 3:self.rewardBindRMB4}
		self.dayReward[self.needDay5] = {1:self.rewardItems5, 2:self.rewardTili5, 3:self.rewardBindRMB5}
		self.dayReward[self.needDay6] = {1:self.rewardItems6, 2:self.rewardTili6, 3:self.rewardBindRMB6}
		self.dayReward[self.needDay7] = {1:self.rewardItems7, 2:self.rewardTili7, 3:self.rewardBindRMB7}
		self.dayReward[self.needDay8] = {1:self.rewardItems8, 2:self.rewardTili8, 3:self.rewardBindRMB8}
		
def LoadSuperInvestConfig():
	global SuperInvest_Dict
	
	for SIC in SuperInvestConfig.ToClassType():
		if SIC.InvestIndex in SuperInvest_Dict:
			print "GE_EXC, repeat InvestIndex (%s) in SuperInvest_Dict" % SIC.InvestIndex
		SIC.InitReward()
		SuperInvest_Dict[SIC.InvestIndex] = SIC
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadSuperInvestConfig()
	

	