#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Purgatory.PurgatoryConfig")
#===============================================================================
# 心魔炼狱配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile

if "_HasLoad" not in dir():
	PURGATORY_FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	PURGATORY_FILE_FOLDER_PATH.AppendPath("Purgatory")
	
	#心魔炼狱配置字典
	Purgatory_Dict = {}
	PurgatoryRoundList = []
	
	PurgatoryFuhuo_Dict = {}
	

class PurgatoryConfig(TabFile.TabLine):
	FilePath = PURGATORY_FILE_FOLDER_PATH.FilePath("PurgatoryConfig.txt")
	def __init__(self):
		self.purgatoryId = int			#炼狱ID
		
		self.minLevel = int				#进入需要的最小等级
		
		self.mcidList = eval				#战斗阵营ID列表
		
		#评级回合数、评级奖励
		self.sss_round = int
		self.sss_reward = eval
		self.ss_round = int
		self.ss_reward = eval
		self.s_round = int
		self.s_reward = eval
		self.a_round = int
		self.a_reward = eval
		self.b_round = int
		self.b_reward = eval
		self.c_round = int
		self.c_reward = eval
		self.d_round = int
		self.d_reward = eval
		
		#怪物奖励
		self.mReward1 = eval
		self.mReward2 = eval
		self.mReward3 = eval
		self.mReward4 = eval
		self.mReward5 = eval
		self.mReward6 = eval
		self.mReward7 = eval
		self.mReward8 = eval
		self.mReward9 = eval
		self.mReward10 = eval
		self.mReward11 = eval
		self.mReward12 = eval
		self.mReward13 = eval
		self.mReward14 = eval
		self.mReward15 = eval
		
		#boss奖励金钱、小怪奖励金钱
		self.bRewardMoney = int
		self.mRewardMoney = int
		
		
		self.sss_reward_fcm = self.GetEvalByString    #sss评级奖励
		self.ss_reward_fcm = self.GetEvalByString     #ss评级奖励
		self.s_reward_fcm = self.GetEvalByString      #s评级奖励
		self.a_reward_fcm = self.GetEvalByString      #a评级奖励
		self.b_reward_fcm = self.GetEvalByString      #b评级奖励
		self.c_reward_fcm = self.GetEvalByString      #c评级奖励
		self.d_reward_fcm = self.GetEvalByString      #d评级奖励
		self.mReward1_fcm = self.GetEvalByString      #第一波怪物奖励物品
		self.mReward2_fcm = self.GetEvalByString      #第二波怪物奖励物品
		self.mReward3_fcm = self.GetEvalByString      #第三波怪物奖励物品
		self.mReward4_fcm = self.GetEvalByString      #第四波怪物奖励物品
		self.mReward5_fcm = self.GetEvalByString      #第五波怪物奖励物品
		self.mReward6_fcm = self.GetEvalByString      #第六波怪物奖励物品
		self.mReward7_fcm = self.GetEvalByString      #第七波怪物奖励物品
		self.mReward8_fcm = self.GetEvalByString      #第八波怪物奖励物品
		self.mReward9_fcm = self.GetEvalByString      #第九波怪物奖励物品
		self.mReward10_fcm = self.GetEvalByString     #第十波怪物奖励物品
		self.mReward11_fcm = self.GetEvalByString     #第十一波怪物奖励物品
		self.mReward12_fcm = self.GetEvalByString     #第十二波怪物奖励物品
		self.mReward13_fcm = self.GetEvalByString     #第十三波怪物奖励物品
		self.mReward14_fcm = self.GetEvalByString     #第十四波怪物奖励物品
		self.mReward15_fcm = self.GetEvalByString     #第十五波怪物奖励物品
		self.bRewardMoney_fcm = int                   #boss奖励金钱
		self.mRewardMoney_fcm = int                   #怪物奖励金钱
		
			
	def InitReward(self):
		#预处理评级奖励
		self.PRR = {}
		self.PRR[self.sss_round] = self.sss_reward
		self.PRR[self.ss_round] = self.ss_reward
		self.PRR[self.s_round] = self.s_reward
		self.PRR[self.a_round] = self.a_reward
		self.PRR[self.b_round] = self.b_reward
		self.PRR[self.c_round] = self.c_reward
		self.PRR[self.d_round] = self.d_reward
		
		#预处理回合-->星级
		self.RTS = {}
		self.RTS[self.sss_round] = 1
		self.RTS[self.ss_round] = 2
		self.RTS[self.s_round] = 3
		self.RTS[self.a_round] = 4
		self.RTS[self.b_round] = 5
		self.RTS[self.c_round] = 6
		self.RTS[self.d_round] = 7
		
		#预处理击杀怪物奖励
		self.PKR = {}
		self.PKR[1] = (self.mReward1, self.mRewardMoney)
		self.PKR[2] = (self.PKR[1][0] + self.mReward2, self.PKR[1][1] + self.mRewardMoney)
		self.PKR[3] = (self.PKR[2][0] + self.mReward3, self.PKR[2][1] + self.bRewardMoney)
		self.PKR[4] = (self.PKR[3][0] + self.mReward4, self.PKR[3][1] + self.mRewardMoney)
		self.PKR[5] = (self.PKR[4][0] + self.mReward5, self.PKR[4][1] + self.mRewardMoney)
		self.PKR[6] = (self.PKR[5][0] + self.mReward6, self.PKR[5][1] + self.bRewardMoney)
		self.PKR[7] = (self.PKR[6][0] + self.mReward7, self.PKR[6][1] + self.mRewardMoney)
		self.PKR[8] = (self.PKR[7][0] + self.mReward8, self.PKR[7][1] + self.mRewardMoney)
		self.PKR[9] = (self.PKR[8][0] + self.mReward9, self.PKR[8][1] + self.bRewardMoney)
		self.PKR[10] = (self.PKR[9][0] + self.mReward10, self.PKR[9][1] + self.mRewardMoney)
		self.PKR[11] = (self.PKR[10][0] + self.mReward11, self.PKR[10][1] + self.mRewardMoney)
		self.PKR[12] = (self.PKR[11][0] + self.mReward12, self.PKR[11][1] + self.bRewardMoney)
		self.PKR[13] = (self.PKR[12][0] + self.mReward13, self.PKR[12][1] + self.mRewardMoney)
		self.PKR[14] = (self.PKR[13][0] + self.mReward14, self.PKR[13][1] + self.mRewardMoney)
		self.PKR[15] = (self.PKR[14][0] + self.mReward15, self.PKR[14][1] + self.bRewardMoney)
		
	def InitReward_fcm(self):
		#预处理评级奖励
		self.PRR_fcm = {}
		self.PRR_fcm[self.sss_round] = self.sss_reward_fcm
		self.PRR_fcm[self.ss_round] = self.ss_reward_fcm
		self.PRR_fcm[self.s_round] = self.s_reward_fcm
		self.PRR_fcm[self.a_round] = self.a_reward_fcm
		self.PRR_fcm[self.b_round] = self.b_reward_fcm
		self.PRR_fcm[self.c_round] = self.c_reward_fcm
		self.PRR_fcm[self.d_round] = self.d_reward_fcm
		
		#预处理回合-->星级
		self.RTS_fcm = {}
		self.RTS_fcm[self.sss_round] = 1
		self.RTS_fcm[self.ss_round] = 2
		self.RTS_fcm[self.s_round] = 3
		self.RTS_fcm[self.a_round] = 4
		self.RTS_fcm[self.b_round] = 5
		self.RTS_fcm[self.c_round] = 6
		self.RTS_fcm[self.d_round] = 7
		
		#预处理击杀怪物奖励
		self.PKR_fcm = {}
		self.PKR_fcm[1] = (self.mReward1_fcm, self.mRewardMoney_fcm)
		self.PKR_fcm[2] = (self.PKR_fcm[1][0] + self.mReward2_fcm, self.PKR_fcm[1][1] + self.mRewardMoney_fcm)
		self.PKR_fcm[3] = (self.PKR_fcm[2][0] + self.mReward3_fcm, self.PKR_fcm[2][1] + self.bRewardMoney_fcm)
		self.PKR_fcm[4] = (self.PKR_fcm[3][0] + self.mReward4_fcm, self.PKR_fcm[3][1] + self.mRewardMoney_fcm)
		self.PKR_fcm[5] = (self.PKR_fcm[4][0] + self.mReward5_fcm, self.PKR_fcm[4][1] + self.mRewardMoney_fcm)
		self.PKR_fcm[6] = (self.PKR_fcm[5][0] + self.mReward6_fcm, self.PKR_fcm[5][1] + self.bRewardMoney_fcm)
		self.PKR_fcm[7] = (self.PKR_fcm[6][0] + self.mReward7_fcm, self.PKR_fcm[6][1] + self.mRewardMoney_fcm)
		self.PKR_fcm[8] = (self.PKR_fcm[7][0] + self.mReward8_fcm, self.PKR_fcm[7][1] + self.mRewardMoney_fcm)
		self.PKR_fcm[9] = (self.PKR_fcm[8][0] + self.mReward9_fcm, self.PKR_fcm[8][1] + self.bRewardMoney_fcm)
		self.PKR_fcm[10] = (self.PKR_fcm[9][0] + self.mReward10_fcm, self.PKR_fcm[9][1] + self.mRewardMoney_fcm)
		self.PKR_fcm[11] = (self.PKR_fcm[10][0] + self.mReward11_fcm, self.PKR_fcm[10][1] + self.mRewardMoney_fcm)
		self.PKR_fcm[12] = (self.PKR_fcm[11][0] + self.mReward12_fcm, self.PKR_fcm[11][1] + self.bRewardMoney_fcm)
		self.PKR_fcm[13] = (self.PKR_fcm[12][0] + self.mReward13_fcm, self.PKR_fcm[12][1] + self.mRewardMoney_fcm)
		self.PKR_fcm[14] = (self.PKR_fcm[13][0] + self.mReward14_fcm, self.PKR_fcm[13][1] + self.mRewardMoney_fcm)
		self.PKR_fcm[15] = (self.PKR_fcm[14][0] + self.mReward15_fcm, self.PKR_fcm[14][1] + self.bRewardMoney_fcm)
		
def LoadPurgatoryConfig():
	global Purgatory_Dict
	for PC in PurgatoryConfig.ToClassType():
		if PC.purgatoryId in Purgatory_Dict:
			print "GE_EXC, repeat id (%s) in Purgatory_Dict" % PC.purgatoryId
			continue
		Purgatory_Dict[PC.purgatoryId] = PC
		
		#预处理奖励
		PC.InitReward()
		#预处理防沉迷奖励
		PC.InitReward_fcm()

class PurgatoryFuhuoCntConfig(TabFile.TabLine):
	FilePath = PURGATORY_FILE_FOLDER_PATH.FilePath("PurgatoryFuhuo.txt")
	def __init__(self):
		self.cnt = int
		self.bindRMB = int
	
def LoadPFCConfig():
	global PurgatoryFuhuo_Dict
	for PFC in PurgatoryFuhuoCntConfig.ToClassType():
		if PFC.cnt in PurgatoryFuhuo_Dict:
			print "GE_EXC, repeat purgatory fuhuo cnt (%s) in PurgatoryFuhuo_Dict" % PFC.cnt
			continue
		PurgatoryFuhuo_Dict[PFC.cnt] = PFC
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		LoadPurgatoryConfig()
		LoadPFCConfig()
		
	
	
