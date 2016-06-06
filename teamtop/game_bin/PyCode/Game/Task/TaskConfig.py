#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Task.TaskConfig")
#===============================================================================
# 任务配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Util import Random
from Game.Role import Event
from Common.Other import GlobalPrompt


if "_HasLoad" not in dir():
	TaskFolder = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	TaskFolder.AppendPath("Task")
	#主线任务配置
	MainTaskConfig_Dict = {}
	#主线任务战斗奖励
	MainTaskFightRewardConfig_Dict = {}
	
	#支线任务配置
	SubTaskConfig_Dict = {}
	LevelActiveSubTask = {}
	#支线任务等级激活配置
	SubTaskLevelConfig_Dict = {}
	#日常任务配置
	DayTaskConfig_Dict = {}
	#日常任务等级随机
	DayTaskLevelRandom_Dict = {}
	
	#体力任务配置
	TiLiTaskConfig_Dict = {}
	#体力任务等级随机
	TiLiTaskLevelRandom_Dict = {}
	
	#相信客户端任务
	BelieveClientTask_Dict = {}
	
class BelieveClientTask(TabFile.TabLine):
	FilePath = TaskFolder.FilePath("BelieveClientTask.txt")
	
	enumNameDict = {'DownloadMicroend':1}
	
	def __init__(self):
		self.taskIndex = int
		self.needLevel = int
		self.rewardExp = int
		self.rewardMoney = int
		self.rewardBindRMB = int
		self.rewardItems = eval
		
def LoadBelieveClientTask():
	global BelieveClientTask_Dict
	
	for BCT in BelieveClientTask.ToClassType():
		if BCT.taskIndex in BelieveClientTask_Dict:
			print 'GE_EXC, repeat taskIndex %s in BelieveClientTask_Dict' % BCT.taskIndex
			continue
		BelieveClientTask_Dict[BCT.taskIndex] = BCT
	
class MainTaskConfig(TabFile.TabLine):
	FilePath = TaskFolder.FilePath("MainTask.txt")
	def __init__(self):
		self.stepIndex = int
		self.nextStep = int
		self.needLv = int
		self.taskType = int
		self.taskParam = self.GetEvalByString
		
		#奖励相关
		self.needReward = self.GetIntByString
		self.Exp = self.GetIntByString
		self.AwardNMoney = self.GetIntByString
		self.awardBindRMB = self.GetIntByString
		self.awardItems = self.GetEvalByString
	
	def Preprocess(self):
		#直接缓存下一个步骤的配置
		self.next_step_cfg = MainTaskConfig_Dict.get(self.nextStep)
		self.checkFun = None
	
	def SetCheckFun(self, fun):
		#设置检查任务完成条件的函数
		self.checkFun = fun
	
	
	def GetNext(self, next_step):
		if next_step == self.nextStep:
			return self.next_step_cfg
		else:
			return False

	def RewardRole(self, role):
		#任务奖励
		if not self.needReward:
			return
		if self.Exp :
			role.IncExp(self.Exp)
			role.Msg(2, 0, GlobalPrompt.Exp_Tips % self.Exp)
		if self.AwardNMoney:
			role.IncMoney(self.AwardNMoney)
			role.Msg(2, 0, GlobalPrompt.Money_Tips % self.AwardNMoney)
		if self.awardBindRMB:
			role.IncBindRMB(self.awardBindRMB)
			role.Msg(2, 0, GlobalPrompt.BindRMB_Tips % self.awardBindRMB)
		if self.awardItems:
			for itemCoding, cnt in self.awardItems:
				role.AddItem(itemCoding, cnt)
				role.Msg(2, 0, GlobalPrompt.Item_Tips % (itemCoding, cnt))

class MainTaskFightRewardConfig(TabFile.TabLine):
	FilePath = TaskFolder.FilePath("TaskFightReward.txt")
	def __init__(self):
		self.taskStep = int
		self.fightCampId = int
		self.fightType = int
		self.anger = int
		self.studySkill = self.GetEvalByString
		
		self.star_3_round = int
		self.rewardExp_3 = int
		self.rewardMoney_3 = int
		self.rewardItem_3 = self.GetEvalByString
		
		self.star_2_round = int
		self.rewardExp_2 = int
		self.rewardMoney_2 = int
		self.rewardItem_2 = self.GetEvalByString
		
		self.star_1_round = int
		self.rewardExp_1 = int
		self.rewardMoney_1 = int
		self.rewardItem_1 = self.GetEvalByString
	
	def RewardRole(self, role, fightRound):
		exp = 0
		money = 0
		itemCoding = 0
		cnt = 0
		if fightRound <= self.star_3_round:
			exp = self.rewardExp_3
			money = self.rewardMoney_3
			if self.rewardItem_3:
				itemCoding, cnt = self.rewardItem_3
		elif fightRound <= self.star_2_round:
			exp = self.rewardExp_2
			money = self.rewardMoney_2
			if self.rewardItem_2:
				itemCoding, cnt = self.rewardItem_2
		else:
			exp = self.rewardExp_1
			money = self.rewardMoney_1
			if self.rewardItem_1:
				itemCoding, cnt = self.rewardItem_1
		
		if exp:
			role.IncExp(exp)
			role.Msg(2, 0, GlobalPrompt.Exp_Tips % exp)
		if money:
			role.IncMoney(money)
			role.Msg(2, 0, GlobalPrompt.Money_Tips % money)
		if itemCoding:
			role.AddItem(itemCoding, cnt)
			role.Msg(2, 0, GlobalPrompt.Item_Tips % (itemCoding, cnt))
	
	def GetFightReward(self, fightRound):
		star = 0
		exp = 0
		money = 0
		itemCoding = 0
		cnt = 0
		if fightRound <= self.star_3_round:
			star = 3
			exp = self.rewardExp_3
			money = self.rewardMoney_3
			if self.rewardItem_3:
				itemCoding, cnt = self.rewardItem_3
		elif fightRound <= self.star_2_round:
			star = 2
			exp = self.rewardExp_2
			money = self.rewardMoney_2
			if self.rewardItem_2:
				itemCoding, cnt = self.rewardItem_2
		else:
			star = 1
			exp = self.rewardExp_1
			money = self.rewardMoney_1
			if self.rewardItem_1:
				itemCoding, cnt = self.rewardItem_1
		
		return star, exp, money, itemCoding, cnt
	
	

class SubTaskConfig(TabFile.TabLine):
	FilePath = TaskFolder.FilePath("SubTask.txt")
	def __init__(self):
		self.subTaskIndex = int
		self.needTaskIndex = int
		self.needLevel = int
		self.rewardExp = int
		self.rewardMoney = int
		self.rewardBindRMB = int
		self.rewardItems = self.GetEvalByString
		
		self.taskType = int
		self.taskParam = self.GetEvalByString
	
	
	def InitLinker(self):
		#初始化完成这个任务后可以激活的其他任务列表
		self.nextCfgs = []
	
	def LinkActiveIndex(self, cfg):
		#链接完成这个支线后可以继续激活的支线任务
		self.nextCfgs.append(cfg)
	
	def LinkCheckFun(self, fun):
		#检测任务条件是否达成的函数
		self.checkFun = fun
	
	def RewardRole(self, role):
		#任务奖励
		tips = GlobalPrompt.SubTask_Reward
		if self.rewardExp:
			role.IncExp(self.rewardExp)
			tips += GlobalPrompt.Exp_Tips % self.rewardExp
		if self.rewardMoney:
			role.IncMoney(self.rewardMoney)
			tips += GlobalPrompt.Money_Tips % self.rewardMoney
		if self.rewardBindRMB:
			role.IncBindRMB(self.rewardBindRMB)
			tips += GlobalPrompt.BindRMB_Tips % self.rewardBindRMB
		if self.rewardItems:
			for itemCoding, cnt in self.rewardItems:
				role.AddItem(itemCoding, cnt)
				tips += GlobalPrompt.Item_Tips % (itemCoding, cnt)
		
		role.Msg(2, 0, tips)

class DayTaskConfig(TabFile.TabLine):
	FilePath = TaskFolder.FilePath("DayTask.txt")
	def __init__(self):
		self.taskIndex = int
		self.group = int
		self.minLevel = int#大于等于
		self.maxLevel = int#小于等于
		self.rewardItem = int
		self.rewardMoney = int
		self.rewardExp = int
		
		self.mf1 = int
		self.mf2 = int
		self.mf3 = int
		self.mf4 = int
		
		self.killNpcId1 = int
		self.killNpcId2 = int
		self.killNpcId3 = int
		self.killNpcId4 = int
		self.rewardMoney_fcm = int                    #奖励金币
		self.rewardExp_fcm = int                      #奖励经验


	def Preprocess(self, npc_data_dict):
		self.m_dict = {}
		
		npcCfg = npc_data_dict.get(self.killNpcId1)
		if not npcCfg:
			return False
		self.m_dict[self.killNpcId1] = (1, self.mf1, npcCfg.sceneID, npcCfg.npcPosX, npcCfg.npcPosY, npcCfg.clickLen)
		
		npcCfg = npc_data_dict.get(self.killNpcId2)
		if not npcCfg:
			return False
		self.m_dict[self.killNpcId2] = (2, self.mf2, npcCfg.sceneID, npcCfg.npcPosX, npcCfg.npcPosY, npcCfg.clickLen)
		
		npcCfg = npc_data_dict.get(self.killNpcId3)
		if not npcCfg:
			return False
		self.m_dict[self.killNpcId3] = (3, self.mf3, npcCfg.sceneID, npcCfg.npcPosX, npcCfg.npcPosY, npcCfg.clickLen)
		
		npcCfg = npc_data_dict.get(self.killNpcId4)
		if not npcCfg:
			return False
		self.m_dict[self.killNpcId4] = (4, self.mf4, npcCfg.sceneID, npcCfg.npcPosX, npcCfg.npcPosY, npcCfg.clickLen)
		return True
	
	def RewardRole(self, role, times = 1):
		#YY防沉迷对奖励特殊处理
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:
			money = self.rewardMoney_fcm * times
			exp = self.rewardExp_fcm * times
		elif yyAntiFlag == 0:
			money = self.rewardMoney * times
			exp = self.rewardExp * times
		else:
			money = 0
			exp = 0
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
		
		if money:
			role.IncMoney(money)
			role.Msg(2, 0, GlobalPrompt.Money_Tips % money)
		if exp:
			role.IncExp(exp)
			role.Msg(2, 0, GlobalPrompt.Exp_Tips % exp)
			
		role.AddItem(self.rewardItem, times)
		role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (self.rewardItem, times))

class TiLiTaskConfig(TabFile.TabLine):
	FilePath = TaskFolder.FilePath("TiLiTask.txt")
	def __init__(self):
		self.taskIndex = int
		self.group = int
		self.minLevel = int
		self.maxLevel = int
		self.rewardItem = int
		self.rewardTili = int
		self.rewardMoney = int
		self.rewardExp = int
			
		self.mf1 = int
		self.mf2 = int
		self.mf3 = int
		self.mf4 = int
		
		self.killNpcId1 = int
		self.killNpcId2 = int
		self.killNpcId3 = int
		self.killNpcId4 = int
		self.rewardTili_fcm = int                     #奖励体力(后端用）

	def Preprocess(self, npc_data_dict):
		self.m_dict = {}
		
		npcCfg = npc_data_dict.get(self.killNpcId1)
		if not npcCfg:
			return False
		self.m_dict[self.killNpcId1] = (1, self.mf1, npcCfg.sceneID, npcCfg.npcPosX, npcCfg.npcPosY, npcCfg.clickLen)
		
		npcCfg = npc_data_dict.get(self.killNpcId2)
		if not npcCfg:
			return False
		self.m_dict[self.killNpcId2] = (2, self.mf2, npcCfg.sceneID, npcCfg.npcPosX, npcCfg.npcPosY, npcCfg.clickLen)
		
		npcCfg = npc_data_dict.get(self.killNpcId3)
		if not npcCfg:
			return False
		self.m_dict[self.killNpcId3] = (3, self.mf3, npcCfg.sceneID, npcCfg.npcPosX, npcCfg.npcPosY, npcCfg.clickLen)
		
		npcCfg = npc_data_dict.get(self.killNpcId4)
		if not npcCfg:
			return False
		self.m_dict[self.killNpcId4] = (4, self.mf4, npcCfg.sceneID, npcCfg.npcPosX, npcCfg.npcPosY, npcCfg.clickLen)

		return True

	def RewardRole(self, role, times = 1):
		money = self.rewardMoney * times
		if money:
			role.IncMoney(money)
			role.Msg(2, 0, GlobalPrompt.Money_Tips % money)
		exp = self.rewardExp * times
		if exp:
			role.IncExp(exp)
			role.Msg(2, 0, GlobalPrompt.Exp_Tips % exp)
		role.AddItem(self.rewardItem, times)
		#YY防沉迷对奖励特殊处理
		yyAntiFlag = role.GetAnti()
		if yyAntiFlag == 1:
			role.IncTiLi(self.rewardTili_fcm * times)
		elif yyAntiFlag == 0:
			role.IncTiLi(self.rewardTili * times)
		else:
			role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
			return None
		role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (self.rewardItem, times))


def LoadMainTaskConfig():
	#读取主线任务配置
	global MainTaskConfig_Dict
	for mtc in MainTaskConfig.ToClassType():
		if mtc.stepIndex in MainTaskConfig_Dict:
			print "GE_EXC, LoadMainTaskConfig repeat step(%s)" % mtc.stepIndex
			continue
		MainTaskConfig_Dict[mtc.stepIndex] = mtc
	
	global MainTaskFightRewardConfig_Dict
	for mtrc in MainTaskFightRewardConfig.ToClassType():
		if mtrc.taskStep in MainTaskFightRewardConfig_Dict:
			print "GE_EXC, LoadMainTaskConfig  fightreward repeat taskStep(%s)" % mtrc.taskStep
		MainTaskFightRewardConfig_Dict[mtrc.taskStep] = mtrc

def LoadSubTaskConfig():
	#读取支线任务配置
	global SubTaskConfig_Dict
	for stc in SubTaskConfig.ToClassType():
		if stc.subTaskIndex in SubTaskConfig_Dict:
			print "GE_EXC, subTaskIndex repeat step(%s)" % stc.subTaskIndex
			continue
		SubTaskConfig_Dict[stc.subTaskIndex] = stc
		stc.InitLinker()
	
	global LevelActiveSubTask
	for taskIndex, cfg in SubTaskConfig_Dict.iteritems():
		if not cfg.needTaskIndex:
			if cfg.needLevel not in LevelActiveSubTask:
				LevelActiveSubTask[cfg.needLevel] = []
			LevelActiveSubTask[cfg.needLevel].append(cfg)
			continue
		a_cfg = SubTaskConfig_Dict.get(cfg.needTaskIndex)
		if not a_cfg:
			print "GE_EXC, error in LoadSubTaskConfig not needTaskIndex cfg (%s)" % taskIndex
			continue
		a_cfg.LinkActiveIndex(cfg)


def LoadDayTaskConfig():
	#读取日常任务配置
	global DayTaskConfig_Dict
	
	Group_Level_Dict = {}
	Group_Cfgs = {}
	for dtc in DayTaskConfig.ToClassType():
		if dtc.taskIndex in DayTaskConfig_Dict:
			print "GE_EXC, LoadDayTaskConfig repeat taskIndex(%s)" % dtc.taskIndex
			continue
		DayTaskConfig_Dict[dtc.taskIndex] = dtc
		
		if dtc.group not in Group_Level_Dict:
			Group_Level_Dict[dtc.group] = (dtc.minLevel, dtc.maxLevel)
			if dtc.minLevel >= dtc.maxLevel:
				print "GE_EXC, error in  LoadDayTaskConfig dtc.minLevel <= dtc.maxLevel (%s)" % dtc.taskIndex
			
			Group_Cfgs[dtc.group] = [dtc.taskIndex]
		else:
			minLevel, maxLevel = Group_Level_Dict[dtc.group]
			if minLevel != dtc.minLevel or maxLevel != dtc.maxLevel:
				print "GE_EXC, error in  LoadDayTaskConfig minLevel != dtc.maxLevel or maxLevel != dtc.maxLevel (%s)" % dtc.taskIndex
			Group_Cfgs[dtc.group].append(dtc.taskIndex)
	
	#构建等级随机任务
	global DayTaskLevelRandom_Dict
	for group, leveld in Group_Level_Dict.iteritems():
		minLevel, maxLevel = leveld
		randomItem = Random.RandomRate()
		for taskIndex in Group_Cfgs[group]:
			randomItem.AddRandomItem(1, taskIndex)
			
		for i in xrange(minLevel, maxLevel + 1):
			if i in DayTaskLevelRandom_Dict:
				print "GE_EXC, error in LoadDayTaskConfig level error", i
				continue
			DayTaskLevelRandom_Dict[i] = randomItem
	
	from Game.NPC import NPCMgr
	if NPCMgr.SceneNPC_Dict:
		for taskIndex, cfg in DayTaskConfig_Dict.iteritems():
			if not cfg.Preprocess(NPCMgr.SceneNPC_Dict):
				print "GE_EXC, DayTaskConfig_Dict Preprocess warning (%s)" % taskIndex
		


def LoadTiLiTaskConfig():
	#读取体力任务配置
	global TiLiTaskConfig_Dict
	
	Group_Level_Dict = {}
	Group_Cfgs = {}
	for dtc in TiLiTaskConfig.ToClassType():
		if dtc.taskIndex in TiLiTaskConfig_Dict:
			print "GE_EXC, LoadTiLiTaskConfig repeat taskIndex(%s)" % dtc.taskIndex
			continue
		TiLiTaskConfig_Dict[dtc.taskIndex] = dtc
		
		if dtc.group not in Group_Level_Dict:
			Group_Level_Dict[dtc.group] = (dtc.minLevel, dtc.maxLevel)
			if dtc.minLevel >= dtc.maxLevel:
				print "GE_EXC, error in  LoadTiLiTaskConfig dtc.minLevel <= dtc.maxLevel (%s)" % dtc.taskIndex
			
			Group_Cfgs[dtc.group] = [dtc.taskIndex]
		else:
			minLevel, maxLevel = Group_Level_Dict[dtc.group]
			if minLevel != dtc.minLevel or maxLevel != dtc.maxLevel:
				print "GE_EXC, error in  LoadTiLiTaskConfig minLevel != dtc.maxLevel or maxLevel != dtc.maxLevel (%s)" % dtc.taskIndex
			Group_Cfgs[dtc.group].append(dtc.taskIndex)
	
	#构建等级随机任务
	global TiLiTaskLevelRandom_Dict
	for group, leveld in Group_Level_Dict.iteritems():
		minLevel, maxLevel = leveld
		randomItem = Random.RandomRate()
		for taskIndex in Group_Cfgs[group]:
			randomItem.AddRandomItem(1, taskIndex)
			
		for i in xrange(minLevel, maxLevel + 1):
			if i in TiLiTaskLevelRandom_Dict:
				print "GE_EXC, error in LoadTiLiTaskConfig level error"
				continue
			TiLiTaskLevelRandom_Dict[i] = randomItem
	
	from Game.NPC import NPCMgr
	if NPCMgr.SceneNPC_Dict:
		for taskIndex, cfg in TiLiTaskConfig_Dict.iteritems():
			if not cfg.Preprocess(NPCMgr.SceneNPC_Dict):
				print "GE_EXC, TiLiTaskConfig_Dict Preprocess warning (%s)" % taskIndex
		
	



def AfterLoadSceneNPC(SceneNPC_Dict, param):
	global DayTaskConfig_Dict
	global TiLiTaskConfig_Dict
	if DayTaskConfig_Dict:
		for taskIndex, cfg in DayTaskConfig_Dict.iteritems():
			if not cfg.Preprocess(SceneNPC_Dict):
				print "GE_EXC, DayTaskConfig_Dict Preprocess warning (%s)" % taskIndex
	if TiLiTaskConfig_Dict:
		for taskIndex, cfg in TiLiTaskConfig_Dict.iteritems():
			if not cfg.Preprocess(SceneNPC_Dict):
				print "GE_EXC, TiLiTaskConfig_Dict Preprocess warning (%s)" % taskIndex
		
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		LoadMainTaskConfig()
		LoadSubTaskConfig()
		LoadDayTaskConfig()
		LoadTiLiTaskConfig()
		
		LoadBelieveClientTask()
		Event.RegEvent(Event.Eve_AfterLoadSceneNPC, AfterLoadSceneNPC)
		
