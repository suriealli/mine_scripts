#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HunluanSpace.HunluanSpaceConfig")
#===============================================================================
# 混乱时空配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random

if "_HasLoad" not in dir():
	HS_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	HS_FILE_FOLDER_PATH.AppendPath("HunluanSpace")
	
	#群魔乱舞			{worldLevel --> obj}
	HunluanDevil_Dict = {}
	#群魔乱舞npc类型
	HunluanDevilNpcTypeSet = set()
	#群魔乱舞九层boss		{worldLevel --> obj}
	HunluanDevilBoss_Dict = {}
	#群魔乱舞boss类型
	HunluanDevilBNpcTypeSet = set()
	#tp		{worldLevel --> obj}
	HunluanTp_Dict = {}
	#梦幻龙域			{(level, wave, worldLevel) --> obj}
	HunluanDemon_Dict = {}
	#梦幻龙域npc类型
	HunluanDemonNpcTypeSet = set()
	#个人积分排名			{(rank, worldLevel) --> obj}
	HunluanPersonRank_Dict = {}
	#公会积分排名			{(rank, worldLevel) --> obj}
	HunluanUnionRank_Dict = {}
	#公会积分			{(score, worldLevel) --> obj}
	HunluanUnionScore_Dict = {}
	#公会积分列表 -- 有序
	HunluanUnionScore_List = []
	
	HunluanRewardLevel_List = []	#个人奖励的等级都有检测
	HunluanWorldLevel_List = []		#devil和demon的配置表有世界等级检测, 但是devil boss和tp没有检测(因为配置表载入的先后顺序不能确定)
	
	#配置表中所有的怪物阵营ID集合
	MonsterCampIDSet = set()
	
class HunluanDevilConfig(TabFile.TabLine):
	FilePath = HS_FILE_FOLDER_PATH.FilePath("HunluanSpaceDevil.txt")
	def __init__(self):
		self.worldLevel = int
		#[rate, [是否传闻, 名字, [(npcType, fightType, mcid, posX, posY, direct, 最大血量, 击杀获得积分), ...]]]
		self.npc_1 = eval
		self.npc_2 = eval
		self.npc_3 = eval
		self.npc_4 = eval
		self.npc_5 = eval
		self.npc_6 = eval
		self.npc_7 = eval
		self.npc_8 = eval
		self.npc_9 = eval
	
	def InitNpc(self):
		global HunluanDevilNpcTypeSet, MonsterCampIDSet
		
		self.randomNpc = Random.RandomRate()
		
		self.randomNpc.AddRandomItem(*self.npc_1)
		for npc in self.npc_1[1][2]:
			HunluanDevilNpcTypeSet.add(npc[0])
			MonsterCampIDSet.add(npc[2])
			
		self.randomNpc.AddRandomItem(*self.npc_2)
		for npc in self.npc_2[1][2]:
			HunluanDevilNpcTypeSet.add(npc[0])
			MonsterCampIDSet.add(npc[2])
			
		self.randomNpc.AddRandomItem(*self.npc_3)
		for npc in self.npc_3[1][2]:
			HunluanDevilNpcTypeSet.add(npc[0])
			MonsterCampIDSet.add(npc[2])
			
		self.randomNpc.AddRandomItem(*self.npc_4)
		for npc in self.npc_4[1][2]:
			HunluanDevilNpcTypeSet.add(npc[0])
			MonsterCampIDSet.add(npc[2])
			
		self.randomNpc.AddRandomItem(*self.npc_5)
		for npc in self.npc_5[1][2]:
			HunluanDevilNpcTypeSet.add(npc[0])
			MonsterCampIDSet.add(npc[2])
			
		self.randomNpc.AddRandomItem(*self.npc_6)
		for npc in self.npc_6[1][2]:
			HunluanDevilNpcTypeSet.add(npc[0])
			MonsterCampIDSet.add(npc[2])
			
		self.randomNpc.AddRandomItem(*self.npc_7)
		for npc in self.npc_7[1][2]:
			HunluanDevilNpcTypeSet.add(npc[0])
			MonsterCampIDSet.add(npc[2])
			
		self.randomNpc.AddRandomItem(*self.npc_8)
		for npc in self.npc_8[1][2]:
			HunluanDevilNpcTypeSet.add(npc[0])
			MonsterCampIDSet.add(npc[2])
			
		self.randomNpc.AddRandomItem(*self.npc_9)
		for npc in self.npc_9[1][2]:
			HunluanDevilNpcTypeSet.add(npc[0])
			MonsterCampIDSet.add(npc[2])
			
def LoadHunluanDevil():
	global HunluanDevil_Dict, HunluanDevilNpcTypeSet, HunluanWorldLevel_List
	for HDC in HunluanDevilConfig.ToClassType():
		if HDC.worldLevel in HunluanDevil_Dict:
			print 'GE_EXC, repeat worldLevel %s in HunluanDevil_Dict' % HDC.worldLevel
			continue
		HDC.InitNpc()
		HunluanDevil_Dict[HDC.worldLevel] = HDC
		HunluanWorldLevel_List.append(HDC.worldLevel)
	HunluanWorldLevel_List = list(set(HunluanWorldLevel_List))
	HunluanWorldLevel_List.sort()
	
class HunluanDevilBoss(TabFile.TabLine):
	FilePath = HS_FILE_FOLDER_PATH.FilePath("HunluanSpaceDevilBoss.txt")
	def __init__(self):
		self.worldLevel = int
		self.boss = eval	#npcType, posX, posY, direct
		self.mcid = int
		self.fightType = int
	
def LoadHunluanDevilBoss():
	global HunluanDevilBoss_Dict, HunluanDevilBNpcTypeSet, MonsterCampIDSet
	for HDB in HunluanDevilBoss.ToClassType():
		if HDB.worldLevel in HunluanDevilBoss_Dict:
			print 'GE_EXC, repeat worldLevel %s in HunluanDevilBoss_Dict' % HDB.worldLevel
			continue
		HunluanDevilBoss_Dict[HDB.worldLevel] = HDB
		HunluanDevilBNpcTypeSet.add(HDB.boss[0])
		MonsterCampIDSet.add(HDB.mcid)
	
class HunluanTp(TabFile.TabLine):
	FilePath = HS_FILE_FOLDER_PATH.FilePath("HunluanSpaceTp.txt")
	def __init__(self):
		self.worldLevel = int
		self.fightType = int
		self.mcid = int
	
def LoadHunluanTp():
	global HunluanTp_Dict
	for HT in HunluanTp.ToClassType():
		if HT.worldLevel in HunluanTp_Dict:
			print 'GE_EXC, repeat worldLevel %s in HunluanTp_Dict' % HT.worldLevel
			continue
		HunluanTp_Dict[HT.worldLevel] = HT
	
class HunluanDemonConfig(TabFile.TabLine):
	FilePath = HS_FILE_FOLDER_PATH.FilePath("HunluanSpaceDemon.txt")
	def __init__(self):
		self.level = int
		self.wave = int
		self.worldLevel = int
		#[(npcType, fightType, mcid, posX, posY, direct, 最大血量, 击杀获得积分), ...]
		self.npc = eval
		self.waveName = str
	
	def InitNPC(self):
		global MonsterCampIDSet
		for npc in self.npc:
			MonsterCampIDSet.add(npc[2])
		
def LoadHunluanDemon():
	global HunluanDemon_Dict, HunluanDemonNpcTypeSet, HunluanWorldLevel_List
	tmpList = []
	for HDC in HunluanDemonConfig.ToClassType():
		if (HDC.level, HDC.wave, HDC.worldLevel) in HunluanDemon_Dict:
			print 'GE_EXC, repeat level %s wave %s worldLevel %s in HunluanDemon_Dict' % (HDC.level, HDC.wave, HDC.worldLevel)
			continue
		HDC.InitNPC()
		HunluanDemon_Dict[(HDC.level, HDC.wave, HDC.worldLevel)] = HDC
		for npcCfg in HDC.npc:
			HunluanDemonNpcTypeSet.add(npcCfg[0])
		tmpList.append(HDC.worldLevel)
	tmpList = list(set(tmpList))
	tmpList.sort()
	
	if tmpList != HunluanWorldLevel_List:
		print 'GE_EXC, HunluanDemonConfig have worldLevel not equal HunluanDevilConfig'
	
class HunluanPersonRankConfig(TabFile.TabLine):
	FilePath = HS_FILE_FOLDER_PATH.FilePath("HunluanSpacePersonRank.txt")
	def __init__(self):
		self.rank = int
		self.Level = int
		self.rewardItems = eval
		self.rewardMoney = int
	
def LoadHunluanPersonRank():
	global HunluanPersonRank_Dict, HunluanRewardLevel_List
	tmpList = []
	for HPR in HunluanPersonRankConfig.ToClassType():
		if (HPR.rank, HPR.Level) in HunluanPersonRank_Dict:
			print 'GE_EXC, repeat rank %s Level %s in HunluanPersonRank_Dict' % (HPR.rank, HPR.Level)
			continue
		HunluanPersonRank_Dict[(HPR.rank, HPR.Level)] = HPR
		tmpList.append(HPR.Level)
	tmpList = list(set(tmpList))
	tmpList.sort()
	
	if tmpList != HunluanRewardLevel_List:
		print 'GE_EXC, HunluanPersonRankConfig have level not equal HunluanUnionScoreConfig'
	
class HunluanUnionRankConfig(TabFile.TabLine):
	FilePath = HS_FILE_FOLDER_PATH.FilePath("HunluanSpaceUnionRank.txt")
	def __init__(self):
		self.rank = int
		self.Level = int
		self.rewardItems = eval
	
def LoadHunluanUnionRank():
	global HunluanUnionRank_Dict, HunluanRewardLevel_List
	tmpList= []
	for HUR in HunluanUnionRankConfig.ToClassType():
		if (HUR.rank, HUR.Level) in HunluanUnionRank_Dict:
			print 'GE_EXC, repeat rank %s Level %s in HunluanUnionRank_Dict' % (HUR.rank, HUR.Level)
			continue
		HunluanUnionRank_Dict[(HUR.rank, HUR.Level)] = HUR
		tmpList.append(HUR.Level)
	tmpList = list(set(tmpList))
	tmpList.sort()
	
	if tmpList != HunluanRewardLevel_List:
		print 'GE_EXC, HunluanUnionRankConfig have level not equal HunluanUnionScoreConfig'
	
class HunluanUnionScoreConfig(TabFile.TabLine):
	FilePath = HS_FILE_FOLDER_PATH.FilePath("HunluanSpaceUnionScore.txt")
	def __init__(self):
		self.score = int
		self.Level = int
		self.rewardItems = eval
		self.rewardMoney = int
		self.rewardExp = int
	
def LoadHunluanUnionScore():
	global HunluanUnionScore_Dict, HunluanUnionScore_List, HunluanRewardLevel_List
	for HUC in HunluanUnionScoreConfig.ToClassType():
		if (HUC.score, HUC.Level) in HunluanUnionScore_Dict:
			print 'GE_EXC, repeat score %s Level %s in HunluanUnionScore_Dict' % (HUC.score, HUC.Level)
			continue
		HunluanUnionScore_Dict[(HUC.score, HUC.Level)] = HUC
		HunluanUnionScore_List.append(HUC.score)
		HunluanRewardLevel_List.append(HUC.Level)
	#去重
	HunluanUnionScore_List = list(set(HunluanUnionScore_List))
	#排序
	HunluanUnionScore_List.sort()
	
	HunluanRewardLevel_List = list(set(HunluanRewardLevel_List))
	HunluanRewardLevel_List.sort()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadHunluanTp()
		#注意这里有先后顺序
		LoadHunluanUnionScore()
		LoadHunluanPersonRank()
		LoadHunluanUnionRank()
		
	