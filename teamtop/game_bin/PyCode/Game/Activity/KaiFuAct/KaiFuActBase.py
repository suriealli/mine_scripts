#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.KaiFuAct.KaiFuActBase")
#===============================================================================
# 开服活动基础
#===============================================================================
import copy
from Common.Message import AutoMessage
from Game.Activity.KaiFuAct import KaiFuActConfig
from Game.Role.Data import EnumObj, EnumInt16, EnumTempObj
from Game.SysData import WorldData

if "_HasLoad" not in dir():
	REWARD_STATUS_DICT_INDEX = 1	#奖励状态字典
	TILI_INDEX = 2					#累积消耗的体力
	ONLINE_TIME_INDEX = 3			#在线时间
	YELLOW_TAROT_CNT_INDEX = 4		#黄色命魂数量
	XINYUECHANGGONG_INDEX = 5		#新月长弓数量
	XINYUEZHANFU_INDEX = 6			#新月战斧数量
	RUNE_CNT_INDEX = 7				#4级符文购买数量
	TAROT_LEVEL_CNT_INDEX = 8		#命魂等级达标数量
	MOUNT_TRAIN_CNT_INDEX = 9		#坐骑每天培养次数
	WING_TRAIN_CNT_INDEX = 10		#羽翼每天培养次数
	PET_CLU_CNT_INDEX = 11			#宠物每天培养次数
	
	XINYUECHANGGONG_CODING = 35706	#新月长弓coding
	XINYUEZHANFU_CODING = 35707		#新月战斧coding
	
	#4级符文coding列表
	RUNE_CODING_LIST = [25886, 25887, 25888, 25889, 25890, 25891, 25892, 25893, 25894, 25895, 25896, 25897]

	#消息
	Kai_Fu_Act_Icon_Twinkle = AutoMessage.AllotMessage("Kai_Fu_Act_Icon_Twinkle", "通知客户端开服活动图标闪烁")

class KaiFuActMgr(object):
	def __init__(self, role):
		kaiFuActDict = role.GetObj(EnumObj.KaiFuAct)
		
		self.role = role
		
		self.reward_status_dict = copy.deepcopy(kaiFuActDict.get(REWARD_STATUS_DICT_INDEX, {}))
		self.tili = kaiFuActDict.get(TILI_INDEX, 0)
		self.online_time = kaiFuActDict.get(ONLINE_TIME_INDEX, 0)
		self.yellow_tarot_cnt = kaiFuActDict.get(YELLOW_TAROT_CNT_INDEX, 0)
		self.xinyuechanggong = kaiFuActDict.get(XINYUECHANGGONG_INDEX, 0)
		self.xinyuezhanfu = kaiFuActDict.get(XINYUEZHANFU_INDEX, 0)
		self.rune_cnt = kaiFuActDict.get(RUNE_CNT_INDEX, 0)
		self.tarot_level_cnt = kaiFuActDict.get(TAROT_LEVEL_CNT_INDEX, 0)
		
		self.mount_train_cnt = kaiFuActDict.get(MOUNT_TRAIN_CNT_INDEX, 0)
		self.wing_train_cnt = kaiFuActDict.get(WING_TRAIN_CNT_INDEX, 0)
		self.petcultivate_cnt = kaiFuActDict.get(PET_CLU_CNT_INDEX, 0)
		#不保存
		self.online_reward_tick_id = 0
	
	def is_active(self, actId):
		'''
		是否活动时间
		@param actId:
		'''
		config = KaiFuActConfig.KAI_FU_ACT_BASE.get(actId)
		if not config:
			return False
		
		kaiFuDays = WorldData.GetWorldKaiFuDay()
		if kaiFuDays < config.startDay or kaiFuDays > config.endDay:
			return False
		
		return True
	
	def inc_consume_tili(self, tili):
		'''
		活动1
		体力大作战
		@param tili:
		'''
		actId = 1
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		self.tili += tili
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.tili < idxConfig.needTiLi:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
		
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
			
	def daily_do_score(self):
		'''
		活动2
		每日必做积分奖励
		'''
		actId = 2
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.role.GetI16(EnumInt16.DailyDoScore) < idxConfig.needDailyDoScore:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
		
	def mount_train(self):
		'''
		活动3
		坐骑培养(等级达到条件)
		'''
		actId = 3
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.role.GetI16(EnumInt16.MountEvolveID) < idxConfig.needMountEvolveId:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
	
	def mount_train_count(self, cnt):
		'''
		活动13
		坐骑培养(计算次数)
		'''
		actId = 13
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		self.mount_train_cnt += cnt
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#活动条件
			if self.mount_train_cnt < idxConfig.needMountTrainCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
	def gold(self):
		'''
		活动4
		炼金奖励
		'''
		actId = 4
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.role.GetI16(EnumInt16.GoldTimesDay) < idxConfig.needGoldCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
		
	def online_reward1(self):
		'''
		活动5
		在线奖励1
		'''
		actId = 5
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		self.online_time = onlinesecond = self.role.GetOnLineTimeToday()
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			#活动条件
			if onlinesecond < idxConfig.needOnlineTime:#注意，开服活动配置的是秒数，而非分钟数，不要乘以60
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
		
	def online_reward2(self):
		'''
		活动6
		在线奖励2
		'''
		actId = 6
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		self.online_time = onlinesecond = self.role.GetOnLineTimeToday()
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if onlinesecond < idxConfig.needOnlineTime:#注意，开服活动配置的是秒数，而非分钟数，不要乘以60
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
		
	def inc_yellow_tarot_cnt(self):
		'''
		活动7
		占卜送大礼
		'''
		actId = 7
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		self.yellow_tarot_cnt += 1
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.yellow_tarot_cnt < idxConfig.needYellowTarotCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
		
	def tarot_level(self, level):
		'''
		活动8
		命魂等级奖励
		'''
		actId = 8
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if level < idxConfig.needTarotLevel:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
			
	def get_shenqi(self, coding):
		'''
		活动9
		神器收集
		'''
		actId = 9
		
		#是否需要的道具，不需要直接返回
		if coding not in (XINYUECHANGGONG_CODING, XINYUEZHANFU_CODING):
			return
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		#增加数量
		if coding == XINYUECHANGGONG_CODING:
			self.xinyuechanggong += 1
		else:
			self.xinyuezhanfu += 1
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			if idx in actRewardDict:
				continue
			
			#活动条件
			if idxConfig.needXinYueChangGong:
				if self.xinyuechanggong >= idxConfig.needXinYueChangGong:
					#1可以领取	2已领取
					actRewardDict[idx] = 1
					
					#通知客户端
					self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
					
			elif idxConfig.needXinYueZhanFu:
				if self.xinyuezhanfu >= idxConfig.needXinYueZhanFu:
					#1可以领取	2已领取
					actRewardDict[idx] = 1
					
					#通知客户端
					self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
			
	def union_fb(self, fbId, levelId):
		'''
		活动10
		公会副本奖励
		'''
		actId = 10
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if (fbId, levelId) != idxConfig.needUnionFB:
				continue
			
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
			
	def dragon_level(self, level):
		'''
		活动11
		神龙等级奖励
		'''
		actId = 11
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if level < idxConfig.needDragonLevel:
				continue
			
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
			
	def buy_rune(self, runeCoding, cnt):
		'''
		活动12
		符文购买奖励
		'''
		actId = 12
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		#累积购买符文数量
		if runeCoding in RUNE_CODING_LIST:
			self.rune_cnt += cnt
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.rune_cnt < idxConfig.needRuneCnt:
				continue
			
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
			
	def CheckMountCanReward(self, actId, rewardList):
		'''
		检测坐骑一起冲奖励是否可领取
		@param actId:
		@param rewardList:
		'''
		#是否活动期间
		if not self.is_active(actId):
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in rewardList:
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#活动条件
			if self.role.GetVIP() < idxConfig.needVIP:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
			
	def wing_train_count(self, cnt):
		'''
		活动16
		羽翼培养(计算次数)
		'''
		actId = 16
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		self.wing_train_cnt += cnt
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#活动条件
			if self.wing_train_cnt < idxConfig.needWingTrainCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
			
	def wing_train_level(self):
		'''
		活动17
		翅膀培养(等级达到条件)
		'''
		actId = 17
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		wingList = self.role.GetObj(EnumObj.Wing).get(1, {}).values()
		#获取玩家当前最高等级的翅膀
		maxLevel = 0
		for data in wingList:
			if data[0] > maxLevel:
				maxLevel = data[0]
		
		if not maxLevel:
			return
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if maxLevel < idxConfig.needWingLevel:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
			
	def Petadvanced(self):
		'''
		活动18
		宠物大师
		'''
		actId = 18
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		petMgr = self.role.GetTempObj(EnumTempObj.PetMgr)
		if not petMgr.pet_dict:#玩家没宠物
			return
		StarNum = {}
		SG = StarNum.get
		for pet in petMgr.pet_dict.itervalues():#获取玩家不同星级宠物的数量，是一个字典{star:NUM}
			for star in xrange(1, pet.star + 1):
				StarNum[star] = SG(star, 0) + 1
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			petStar, num = idxConfig.needPetLevelCnt
			if StarNum.get(petStar, 0) < num:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
			
	def Petcultivate(self, cnt):
		'''
		活动19
		宠物培养
		'''
		actId = 19
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		self.petcultivate_cnt += cnt
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			if self.petcultivate_cnt < idxConfig.needPetCulCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
			
	def FuWenSyn(self, fuwenLevel):
		'''
		活动20
		符文合成
		'''
		actId = 20
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = KaiFuActConfig.KAI_FU_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = KaiFuActConfig.KAI_FU_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			if fuwenLevel != idxConfig.needFuwenLevel:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Kai_Fu_Act_Icon_Twinkle, None)
		
	def save(self):
		kaiFuActDict = self.role.GetObj(EnumObj.KaiFuAct)
		
		kaiFuActDict[REWARD_STATUS_DICT_INDEX] = copy.deepcopy(self.reward_status_dict)
		kaiFuActDict[TILI_INDEX] = self.tili
		kaiFuActDict[ONLINE_TIME_INDEX] = self.online_time
		kaiFuActDict[YELLOW_TAROT_CNT_INDEX] = self.yellow_tarot_cnt
		kaiFuActDict[XINYUECHANGGONG_INDEX] = self.xinyuechanggong
		kaiFuActDict[XINYUEZHANFU_INDEX] = self.xinyuezhanfu
		kaiFuActDict[RUNE_CNT_INDEX] = self.rune_cnt
		kaiFuActDict[TAROT_LEVEL_CNT_INDEX] = self.tarot_level_cnt
		kaiFuActDict[MOUNT_TRAIN_CNT_INDEX] = self.mount_train_cnt
		kaiFuActDict[WING_TRAIN_CNT_INDEX] = self.wing_train_cnt
		kaiFuActDict[PET_CLU_CNT_INDEX] = self.petcultivate_cnt
