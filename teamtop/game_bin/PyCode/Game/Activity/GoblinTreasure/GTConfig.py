#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.GoblinTreasure.GTConfig")
#===============================================================================
# 地精宝库配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	GT_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	GT_FILE_FOLDER_PATH.AppendPath("GoblinTreasure")
	
	#地精宝库兑换配置字典
	GT_Dict = {}
	
	#地精宝库npc配置字典
	GTNpc_Dict = {}
	
	#地精宝库npc类型集合
	GTNpcTypeSet = set()
	
	#地精宝库开启世界等级列表(有序)
	GTWorldLevel_List = []
	
class GTConfig(TabFile.TabLine):
	FilePath = GT_FILE_FOLDER_PATH.FilePath("GTConfig.txt")
	def __init__(self):
		self.itemCoding = int	#物品coding
		self.itemType = int		#物品类型
		self.needCoding = int	#兑换物品需要coding
		self.needCnt = int		#兑换物品需要个数
		self.limitCnt = int		#限购个数
		
class GTNpcConfig(TabFile.TabLine):
	FilePath = GT_FILE_FOLDER_PATH.FilePath("GTNpcConfig.txt")
	def __init__(self):
		self.minLvl = int			#世界等级
		
		self.sceneId1 = int			#场景1 ID
		self.sceneId2 = int
		self.scene1Name = str
		self.scene2Name = str
		self.levelLimit1 = int		#场景1 等级限制
		self.levelLimit2 = int
		
		self.npc_1 = eval			#npc类型, 阵营ID, posX, posY, direct, 点(1-4)
		self.pos1 = eval			#传送位置 (sceneId, posX, posY)
		self.npc_2 = eval
		self.pos2 = eval
		self.npc_3 = eval
		self.pos3 = eval
		self.npc_4 = eval
		self.pos4 = eval
		
		self.reward1 = eval			#[(coding, cnt, rate), ]
		self.reward2 = eval
		
	def InitPosToTp(self):
		#预处理位置等级限制和传送地点
		self.PTP = {}
		self.PTP[1] = (self.levelLimit1, self.pos1, self.scene1Name)
		self.PTP[2] = (self.levelLimit1, self.pos2, self.scene1Name)
		self.PTP[3] = (self.levelLimit2, self.pos3, self.scene2Name)
		self.PTP[4] = (self.levelLimit2, self.pos4, self.scene2Name)
		
	def InitSceneToNpc(self):
		#预处理场景对应的npc
		self.sceneToNpc = {}
		self.sceneToNpc[self.sceneId1] = [self.npc_1, self.npc_2]
		self.sceneToNpc[self.sceneId2] = [self.npc_3, self.npc_4]
		
	def randomReward(self):
		#预处理随机奖励
		self.RandomReward_1 = Random.RandomRate()
		for (coding, cnt, rate) in self.reward1:
			self.RandomReward_1.AddRandomItem(rate, (coding, cnt))
			
		self.RandomReward_2 = Random.RandomRate()
		for (coding, cnt, rate) in self.reward2:
			self.RandomReward_2.AddRandomItem(rate, (coding, cnt))
		
		self.rewardDict = {}
		self.rewardDict[self.sceneId1] = self.RandomReward_1
		self.rewardDict[self.sceneId2] = self.RandomReward_2
	
def LoadGTConfig():
	global GT_Dict
	for TE in GTConfig.ToClassType():
		if TE.itemCoding in GT_Dict:
			print "GE_EXC, repeat item coding (%s) in GT_Dict" % TE.itemCoding
			continue
		GT_Dict[TE.itemCoding] = TE

def LoadGTNpcConfig():
	global GTNpcTypeSet
	global GTNpc_Dict
	global GTWorldLevel_List
	
	for GND in GTNpcConfig.ToClassType():
		if GND.minLvl in GTNpc_Dict:
			print "GE_EXC, repeat minLvl (%s) in GTNpc_Dict" % GND.minLvl
			continue
		GTNpc_Dict[GND.minLvl] = GND
		
		GND.randomReward()
		GND.InitSceneToNpc()
		GND.InitPosToTp()
		
		if GND.npc_1:
			GTNpcTypeSet.add(GND.npc_1[0])
		if GND.npc_2:
			GTNpcTypeSet.add(GND.npc_2[0])
		if GND.npc_3:
			GTNpcTypeSet.add(GND.npc_3[0])
		if GND.npc_4:
			GTNpcTypeSet.add(GND.npc_4[0])
		
		GTWorldLevel_List.append(GND.minLvl)
	
	GTWorldLevel_List.sort()
		
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadGTConfig()
		LoadGTNpcConfig()
		