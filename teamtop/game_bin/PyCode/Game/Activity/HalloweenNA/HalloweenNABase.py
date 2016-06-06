#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HalloweenNA.HalloweenNABase")
#===============================================================================
# 北美万圣节基础
#===============================================================================
import copy
from Common.Message import AutoMessage
from Game.Role.Mail import Mail
from Common.Other import GlobalPrompt
from Game.Activity.HalloweenNA import HalloweenNAConfig, HalloweenNADefine
from Game.Role.Data import EnumObj, EnumDayInt8, EnumInt16
from Game.SysData import WorldData

if "_HasLoad" not in dir():
	SEVEN_ACT_DURATION = 7 		#七日活动持续天数
	
	#Obj索引
	REWARD_STATUS_DICT_INDEX = 1	#奖励状态字典
	BUY_UNBIND_RMB_INDEX = 2		#累计充值神石
	FIRST_PAY_INDEX = 3				#首充
	FIRST_CONSUME_INDEX = 4			#每日首笔消费
	UNION_FB_CNT_INDEX = 5			#公会副本次数
	JJC_CNT_INDEX = 6				#挑战竞技场次数
	ACTIVE_VERSION = 7				#当前7日活动的版本号 
	WING_TRAIN_TOTALCNT = 8			#羽翼活动期间累计培养次数
	GEM_SYNTHTIC_INDEX = 9			#宝石合成
	EVIHOLE_TIMES_INDEX = 10		#恶魔深渊挑战次数
	PETEVL_TIMES_INDEX = 11			#宠物培养次数
	MOUNT_TRAIN_INDEX = 12			#坐骑培养次数
	MOUNT_RMB_TRAIN_INDEX = 13		#坐骑神石培养
	SLAVE_TIMES_INDEX = 14			#解救奴隶次数
	CATCH_SLAVE_TIMES_INDEX = 15	#抓捕奴隶次数
	TOTAL_COST_RMB_INDEX = 16		#每日累计消费
	EQUIPMENT_STRENG_INDEX = 17		#装备强化次数
	TAROT_DICT_INDEX = 18			#获取命魂次数
	TATOT_CNT_INDEX = 19			#每日占卜次数
	GEM_SYNTHTIC_DAY_INDEX = 20		#每日宝石合成
	GEM_BUY_DAY_INDEX = 21			#每日购买宝石数量
	PETEVL_TIMES_FOREVER_INDEX = 22	#累计宠物培养
	FUWEN_SYN_INDEX = 23			#累计符文合成
	MARRY_PARTY_TIMES_INDEX = 24	#累计开派对次数
	COUPLES_FB_INDEX = 25			#累计情缘副本次数
	#消息
	NA_Halloween_Icon_Twinkle = AutoMessage.AllotMessage("NA_Halloween_Icon_Twinkle", "通知客户端北美万圣节图标闪烁")

class HalloweenMgr(object):
	def __init__(self, role):
		HallowActDict = role.GetObj(EnumObj.NAHalloweenData)
		
		self.role = role
		
		self.reward_status_dict = copy.deepcopy(HallowActDict.get(REWARD_STATUS_DICT_INDEX, {}))
		self.buy_unbind_rmb = HallowActDict.get(BUY_UNBIND_RMB_INDEX, 0)
		self.is_first_pay = HallowActDict.get(FIRST_PAY_INDEX, False)
		self.is_first_consume = HallowActDict.get(FIRST_CONSUME_INDEX, False)
		self.union_fb_cnt = HallowActDict.get(UNION_FB_CNT_INDEX, 0)
		self.jjc_cnt = HallowActDict.get(JJC_CNT_INDEX, 0)
		self.ActiveVersion = HallowActDict.get(ACTIVE_VERSION, 0)
		self.wing_train_totalcnt = HallowActDict.get(WING_TRAIN_TOTALCNT, 0)
		self.gem_syn_dict = HallowActDict.get(GEM_SYNTHTIC_INDEX, {})
		self.online_time = role.GetOnLineTimeToday()
		self.EvilHole_times = HallowActDict.get(EVIHOLE_TIMES_INDEX, 0)
		self.Petevl_times = HallowActDict.get(PETEVL_TIMES_INDEX, 0)
		self.mount_train_cnt = HallowActDict.get(MOUNT_TRAIN_INDEX, 0)
		self.mount_rmb_train_cnt = HallowActDict.get(MOUNT_RMB_TRAIN_INDEX, 0)
		self.slave_cnt = HallowActDict.get(SLAVE_TIMES_INDEX, 0)
		self.catch_slave_cnt = HallowActDict.get(CATCH_SLAVE_TIMES_INDEX, 0)
		self.total_cost_RMB = HallowActDict.get(TOTAL_COST_RMB_INDEX, 0)
		self.equipment_streng_cnt = HallowActDict.get(EQUIPMENT_STRENG_INDEX, 0)
		self.tarot_cnt_dict = HallowActDict.get(TAROT_DICT_INDEX, {})
		self.tarot_cnt = HallowActDict.get(TATOT_CNT_INDEX, 0)
		self.gem_day_syn_dict = HallowActDict.get(GEM_SYNTHTIC_DAY_INDEX, {})
		self.buy_gem_day_cnt = HallowActDict.get(GEM_BUY_DAY_INDEX, 0)
		self.Petevl_times_forever = HallowActDict.get(PETEVL_TIMES_FOREVER_INDEX, 0)
		self.Fuwen_syn_dict = HallowActDict.get(FUWEN_SYN_INDEX, {})
		self.party_times_dict = HallowActDict.get(MARRY_PARTY_TIMES_INDEX, {})
		self.couples_fb_times = HallowActDict.get(COUPLES_FB_INDEX, 0)
		#不保存
		self.online_reward_tick_id = 0
		
	def is_active(self, actId):
		'''
		指定活动是否开启
		@param actId:
		'''
		if actId in HalloweenNAConfig.HALLOWEENNA_STARING_SET:
			cfg = HalloweenNAConfig.HALLOWEENNA_ACT_BASE.get(actId)
			if WorldData.GetWorldKaiFuDay() >= cfg.kaifuDays:
				return True
		return False
	
	def UpdateVersion(self):
		if self.ActiveVersion != HalloweenNAConfig.ActiveVersion:
			#版本号不一致，可以重新领取了
			self.ActiveVersion = HalloweenNAConfig.ActiveVersion
			#需要清理活动状态的活动ID
			for actId in HalloweenNADefine.GetClearDataActIDs():
				self.reward_status_dict[actId] = {}
			#累计充值
			self.buy_unbind_rmb = 0
			#首充置为False
			self.is_first_pay = False
			#清除累计培养羽翼相关数据
			self.wing_train_totalcnt = 0
			#清除宝石合成相关数据
			self.gem_syn_dict = {}
			#累计消费
			self.total_cost_RMB = 0
			#清除累计宠物培养
			self.Petevl_times_forever = 0
			#累计符文合成
			self.Fuwen_syn_dict = {}
			#累计开派对
			self.party_times_dict = {}
			#情缘副本次数
			self.couples_fb_times = 0
			#需要清理下DB数据
			from Game.Activity.HalloweenNA import HalloweenNAMgr
			HalloweenNAMgr.ResetDB(HalloweenNAConfig.ActiveVersion)
			
	def inc_buy_unbind_rmb(self, buyUnbindRMB):
		'''
		活动1
		累计充值
		@param buyUnbindRMB:
		'''
		actId = 1
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		self.buy_unbind_rmb += buyUnbindRMB
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.buy_unbind_rmb < idxConfig.needBuyUnbindRMB:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
		
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def first_pay(self):
		'''
		活动2
		首充
		'''
		#是否活动期间
		actId = 0
		for cid in HalloweenNADefine.FIRST_PAY_ACTID_LIST:
			if self.is_active(cid):
				actId = cid
				break
		if not actId:
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		#是否完成首充
		if self.is_first_pay is True:
			return
		self.is_first_pay = True
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
		
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def day_first_consume(self):
		'''
		活动3
		每日首笔消费
		'''
		#是否活动期间
		actId = 0
		for cid in HalloweenNADefine.DAY_COST_ACTID_LIST:
			if self.is_active(cid):
				actId = cid
				break
		if not actId:
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		#是否完成首充
		if self.is_first_consume is True:
			return
		self.is_first_consume = True
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
		
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def finish_gve_fb(self):
		'''
		活动4
		挑战组队副本
		'''
		actId = 0
		for cid in HalloweenNADefine.GVEFB_ACTID_LIST:
			if self.is_active(cid):
				actId = cid
				break
		if not actId:
			return
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.role.GetDI8(EnumDayInt8.GVEFBCnt) < idxConfig.needFinishGVEFBCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def challenge_jjc(self):
		'''
		活动5
		挑战竞技场
		'''
		#是否活动期间
		actId = 0
		for cfg_actid in HalloweenNADefine.JJC_ACTID_LIST:
			if self.is_active(cfg_actid):
				actId = cfg_actid
				break
		if not actId: return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		#完成次数+1
		self.jjc_cnt += 1
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.jjc_cnt < idxConfig.needJJCCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def finish_fb(self):
		'''
		活动6
		挑战副本
		'''
		actId = 0
		for cfg_actid in HalloweenNADefine.FB_ACTID_LIST:
			if self.is_active(cfg_actid):
				actId = cfg_actid
				break
		if not actId: return
			
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		#挑战副本次数
		finishFBCnt = 0
		fbDict = self.role.GetObj(EnumObj.FB_JoinData)
		for cnt in fbDict.itervalues():
			finishFBCnt += cnt
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if finishFBCnt < idxConfig.needFinishFBCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def finish_union_fb(self):
		'''
		挑战公会副本
		'''
		#是否活动期间
		actId = 0
		for cfg_actId in HalloweenNADefine.UNION_FB_ACTID_LIST:
			if self.is_active(cfg_actId):
				actId = cfg_actId
				break
		if not actId: return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		#完成次数+1
		self.union_fb_cnt += 1
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.union_fb_cnt < idxConfig.needFinishUnionFBCnt:
				return
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def slave_play(self):
		'''
		活动8
		勇斗领主
		'''
		actId = 8
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.role.GetDI8(EnumDayInt8.Slave_PlayTimes) < idxConfig.needSlavePlayCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def online_reward(self):
		'''
		活动9
		在线奖励
		'''
		actId = 9
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		self.online_time = onlinesecond = self.role.GetOnLineTimeToday()
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			#活动条件
			if onlinesecond < idxConfig.needOnlineTime * 60:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def purgatoryPass(self, purgatoryId, passLevel):
		'''
		心魔挑战
		@param purgatoryId:
		@param passLevel:
		'''
		actId = 0
		for cfg_actId in HalloweenNADefine.PURGATORYPASS_ACTID_LIST:
			if self.is_active(cfg_actId):
				actId = cfg_actId
				break
		if not actId: return

		if passLevel < 1:
			#没有通关
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if idxConfig.needPurgatoryId:
				if idxConfig.needPurgatoryId == -1:
					if passLevel > 3:
						continue
				else:
					if purgatoryId == idxConfig.needPurgatoryId:
						continue
					#是否SSS级以上通关
					if passLevel > 1:
						continue
			else:
				if self.role.GetDI8(EnumDayInt8.PurgatoryCnt) < idxConfig.needPurgatoryPassCnt:
					continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
				
	def HeroLevel(self):
		'''
		英雄升级
		'''
		actId = 11
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		from Game.Activity.HalloweenNA import HalloweenNAMgr
		actDate = HalloweenNAMgr.HalloweenNaDict.get(actId, {})
		
		allHero = self.role.GetAllHero()
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			GetedData = actDate.get(idx, 0)
			if idxConfig.maxCnt > 0:
				if GetedData >= idxConfig.maxCnt:#已领取完
					continue
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			if not idxConfig.HeroLevel:#配置有问题
				continue
			
			heroId, level = idxConfig.HeroLevel
			
			IsCan = False 
			for hero in allHero.values():
				if hero.GetNumber() == heroId and hero.GetLevel() >= level:
					IsCan = True
			if IsCan != True:
				continue
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
				
	def HeroEvolution(self, HeroOId):
		'''
		英雄进化
		'''
		actId = 12
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
#		from Game.Activity.HalloweenNA import HalloweenNAMgr
#		actDate = HalloweenNAMgr.HalloweenNaDict.get(actId, {})
		
#		allHero = self.role.GetAllHero()
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
#			if idxConfig.maxCnt > 0:
#				GetedData = actDate.get(idx, 0)
#				if GetedData >= idxConfig.maxCnt:#已领取完
#					continue
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			if not idxConfig.HeroIds:#配置有问题
				continue
			
			if HeroOId not in idxConfig.HeroIds:
				continue
				
#			IsCan = False
#			for hero in allHero.values():
#				if hero.GetNumber() in idxConfig.HeroIds:
#					IsCan = True
#					break
#			if IsCan != True:
#				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def gold(self):
		'''
		点石成金
		'''
		actId = 13
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
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
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	
	def WingCultivate(self, cnt):
		'''
		累计羽翼培养
		'''
		actId = 14
		#是否活动期间
		if not self.is_active(actId):
			return
		
		self.wing_train_totalcnt += cnt
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.wing_train_totalcnt < idxConfig.WingculCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def Blessing(self):
		'''
		祝福
		'''
		#是否活动期间
		actId = 0
		for cfg_actId in HalloweenNADefine.BLESS_ACTID_LIST:
			if self.is_active(cfg_actId):
				actId = cfg_actId
		if not actId: return

		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def GemSynthetic(self, gemLevel, cnt):
		'''
		宝石合成
		'''
		actId = 16
		#是否活动期间
		if not self.is_active(actId):
			return
		self.gem_syn_dict[gemLevel] = self.gem_syn_dict.get(gemLevel, 0) + cnt
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			GemLevel, cnt = idxConfig.GemsynCnt
			if self.gem_syn_dict.get(GemLevel, 0) < cnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def SaveSlave(self):
		'''
		解救奴隶
		'''
		actId = 17
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		self.slave_cnt += 1
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.slave_cnt < idxConfig.SaveSlaveCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
	
	def ChallengeHero(self):
		'''
		英灵勇士
		'''
		actId = 18
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		from Game.Activity.HalloweenNA import HalloweenNAMgr
		actDate = HalloweenNAMgr.HalloweenNaDict.get(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			if idxConfig.maxCnt > 0:
				GetedData = actDate.get(idx, 0)
				if GetedData >= idxConfig.maxCnt:#已领取完
					continue
			#活动条件
			if self.role.GetI16(EnumInt16.HeroTempleMaxIndex) < idxConfig.challengeTimes:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
	
	def ChallengeEvilHole(self, times):
		'''
		恶魔深渊挑战
		'''
		#是否活动期间
		actId = 0
		for cfg_actId in HalloweenNADefine.EVILHOLE_ACTID_LIST:
			if self.is_active(cfg_actId):
				actId = cfg_actId
				break
		if not actId: return

		self.EvilHole_times += times
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.EvilHole_times < idxConfig.EvlHoleTimes:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def OneTimeCost(self, costRMB):
		'''
		一次性消费
		'''
		actId = 20
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			if costRMB < idxConfig.costRMB[0] or costRMB > idxConfig.costRMB[1]:
				continue
			
			Mail.SendMail(self.role.GetRoleID(), GlobalPrompt.HalloweenNA_TITLE, GlobalPrompt.HalloweenNA_SENDER, \
					GlobalPrompt.HalloweenNA_CONTENT, items = idxConfig.rewardItem)
			break
			
	def CultivatePet(self, times):
		'''
		宠物培养(每日)
		@param times:
		'''
		actId = 21
		#是否活动期间
		if not self.is_active(actId):
			return
		self.Petevl_times += times
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.Petevl_times < idxConfig.PetevlTimes:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
		
	def PetEvo(self, Petstar):
		'''
		宠物升阶
		'''
		actId = 22
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			if Petstar < idxConfig.Petstar:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
		
	def mount_train(self, trainType, cnt):
		'''
		坐骑养成
		@param cnt:
		'''
		actId = 23
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		#增加坐骑培养次数
		self.mount_train_cnt += cnt
		if trainType != 1:
			self.mount_rmb_train_cnt += cnt
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.mount_train_cnt < idxConfig.needMountTrainCnt:
				continue
			
			if self.mount_rmb_train_cnt < idxConfig.needMountRMBTrainCnt:
				continue
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def CatchSlave(self):
		'''
		抓捕奴隶
		'''
		actId = 24
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		self.catch_slave_cnt += 1
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.catch_slave_cnt < idxConfig.CatchSlaveTimes:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def ChallengeHeroCnt(self):
		'''
		英灵勇士2
		'''
		actId = 25
		
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.role.GetDI8(EnumDayInt8.HeroTempCnt) < idxConfig.ChallengHeroTimes:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def TotalCostRMB(self, costRMB):
		'''
		累计消费
		'''
		#是否活动期间
		actId = 0
		for cfg_actId in HalloweenNADefine.TOTAL_COST_ACTID_LIST:
			if self.is_active(cfg_actId):
				actId = cfg_actId
		if not actId: return
		
		self.total_cost_RMB += costRMB
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.total_cost_RMB < idxConfig.TotalcostRMB:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
		
	def PetSpiritLevel(self, levelCoding):
		'''
		宠物附灵升级
		'''
		actId = 27
		
		Level_map_coding = {1:[26161,26162,26163,26164,26165,26166],2:[26167,26168,26169,26170,26171,26172],\
		 3:[26173,26174,26175,26176,26177,26178],4:[26179,26180,26181,26182,26183,26184],\
		 5:[26185,26186,26187,26188,26189,26190],6:[26191,26192,26193,26194,26195,26196],\
		 7:[26197,26198,26199,26200,26201,26202],8:[26203,26204,26205,26206,26207,26208],\
		 9:[26209,26210,26211,26212,26213,26214],10:[26215,26216,26217,26218,26219,26220]}
		sLevel = 0
		for level, codingList in Level_map_coding.iteritems():
			if levelCoding in codingList:
				sLevel = level
				break
		if not sLevel: return
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if sLevel != idxConfig.PetSpiritLevel:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def PetLuckyDraw(self):
		'''
		宠物转盘
		'''
		actId = 28
		#是否活动期间
		if not self.is_active(actId):
			return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.role.GetDI8(EnumDayInt8.PetLuckyDrawCnt) < idxConfig.PetLuckyDraw:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def EquipmentStrengthen(self):
		'''
		装备强化
		'''
		actId = 29
		#是否活动期间
		if not self.is_active(actId):
			return
		
		self.equipment_streng_cnt += 1
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.equipment_streng_cnt < idxConfig.EquipmentStengCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
		
	def Petpractice(self, evoId):
		'''
		宠物修行
		'''
		actId = 31
		
		if not self.is_active(actId):
			return
	
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			if evoId < idxConfig.PetEvoId:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
		
	def IncTarotCnt(self, grade):
		'''
		占卜天天乐
		@param grade:
		'''
		actId = 32
		
		if not self.is_active(actId):
			return
		
		self.tarot_cnt_dict[grade] = self.tarot_cnt_dict.get(grade, 0) + 1
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			cfg_grade, cnt = idxConfig.tarotCntDict
			if self.tarot_cnt_dict.get(cfg_grade, 0) < cnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
		
	def TarotTimes(self, times):
		'''
		占卜大家乐
		'''
		actId = 33
		
		if not self.is_active(actId):
			return
		
		self.tarot_cnt += times
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			if self.tarot_cnt < idxConfig.tarotCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def GemSyntheticDay(self, gemLevel, cnt):
		'''
		宝石合成每日
		'''
		actId = 34
		#是否活动期间
		if not self.is_active(actId):
			return
		self.gem_day_syn_dict[gemLevel] = self.gem_day_syn_dict.get(gemLevel, 0) + cnt
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			GemLevel, cnt = idxConfig.GemsynCnt
			if self.gem_day_syn_dict.get(GemLevel, 0) < cnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def BuyGem(self, goodsId, cnt):
		'''
		购买宝石
		@param goodsId:
		@param cnt:
		'''
		actId = 35
		#是否活动期间
		if not self.is_active(actId):
			return
		
		from Game.Activity.WonderfulAct import WonderfulActDefine
		WonderfulActDefine.LIBAO_FOR_GEM_DICT
		buy_cnt = 0
		for num, codingList in WonderfulActDefine.LIBAO_FOR_GEM_DICT.iteritems():
			if goodsId in codingList:
				buy_cnt = num * cnt
				break
		self.buy_gem_day_cnt += buy_cnt
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			if self.buy_gem_day_cnt < idxConfig.dayBuyGem:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def CultivatePetForever(self, times):
		'''
		宠物培养
		@param times:
		'''
		actId = 36
		#是否活动期间
		if not self.is_active(actId):
			return
		self.Petevl_times_forever += times
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.Petevl_times_forever < idxConfig.PetevlTimes:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def Fuwensynthetic(self, fuwenlevel, cnt):
		'''
		累计符文合成
		@param fuwenlevel:
		'''
		actId = 37
		#是否活动期间
		if not self.is_active(actId):
			return
		self.Fuwen_syn_dict[fuwenlevel] = self.Fuwen_syn_dict.get(fuwenlevel, 0) + cnt
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			#活动条件
			cfglevel ,cfgcnt = idxConfig.fuwenSyn
			if self.Fuwen_syn_dict.get(cfglevel, 0) < cfgcnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def FinishMarry(self):
		'''
		完成婚礼
		'''
		actId = 0
		for cfg_actId in HalloweenNADefine.MARRY_ACTID_LIST:
			if self.is_active(cfg_actId):
				actId = cfg_actId
		if not actId: return
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def FinishParty(self, partyGrade):
		'''
		派对活动
		'''
		actId = 0
		for cfg_actId in HalloweenNADefine.PARTY_ACTID_LIST:
			if self.is_active(cfg_actId):
				actId = cfg_actId
		if not actId: return
		
		self.party_times_dict[partyGrade] = self.party_times_dict.get(partyGrade, 0) + 1
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			#条件判断
			grade, times = idxConfig.partytimes
			if self.party_times_dict.get(grade, 0) < times:
				continue
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def CouplesFB(self):
		'''
		情缘副本
		'''
		actId = 0
		for cfg_actId in HalloweenNADefine.COUPLESFB_ACTID_LIST:
			if self.is_active(cfg_actId):
				actId = cfg_actId
		if not actId: return
		#是否活动期间
		if not self.is_active(actId):
			return
		
		self.couples_fb_times += 1
		
		idxList = HalloweenNAConfig.HALLOWEENNA_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = HalloweenNAConfig.HALLOWEENNA_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			#条件判断
			if self.couples_fb_times < idxConfig.CFbtimes:
				continue
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(NA_Halloween_Icon_Twinkle, None)
			
	def save(self):
		HalloweenActDict = self.role.GetObj(EnumObj.NAHalloweenData)
		
		HalloweenActDict[REWARD_STATUS_DICT_INDEX] = copy.deepcopy(self.reward_status_dict)
		HalloweenActDict[BUY_UNBIND_RMB_INDEX] = self.buy_unbind_rmb
		HalloweenActDict[FIRST_PAY_INDEX] = self.is_first_pay
		HalloweenActDict[FIRST_CONSUME_INDEX] = self.is_first_consume
		HalloweenActDict[UNION_FB_CNT_INDEX] = self.union_fb_cnt
		HalloweenActDict[JJC_CNT_INDEX] = self.jjc_cnt
		HalloweenActDict[ACTIVE_VERSION] = self.ActiveVersion
		HalloweenActDict[WING_TRAIN_TOTALCNT] = self.wing_train_totalcnt
		HalloweenActDict[GEM_SYNTHTIC_INDEX] = self.gem_syn_dict
		HalloweenActDict[EVIHOLE_TIMES_INDEX] = self.EvilHole_times
		HalloweenActDict[PETEVL_TIMES_INDEX] = self.Petevl_times
		HalloweenActDict[MOUNT_TRAIN_INDEX] = self.mount_train_cnt
		HalloweenActDict[MOUNT_RMB_TRAIN_INDEX] = self.mount_rmb_train_cnt
		HalloweenActDict[SLAVE_TIMES_INDEX] = self.slave_cnt
		HalloweenActDict[CATCH_SLAVE_TIMES_INDEX] = self.catch_slave_cnt
		HalloweenActDict[TOTAL_COST_RMB_INDEX] = self.total_cost_RMB
		HalloweenActDict[EQUIPMENT_STRENG_INDEX] = self.equipment_streng_cnt
		HalloweenActDict[TAROT_DICT_INDEX] = self.tarot_cnt_dict
		HalloweenActDict[TATOT_CNT_INDEX] = self.tarot_cnt
		HalloweenActDict[GEM_SYNTHTIC_DAY_INDEX] = self.gem_day_syn_dict
		HalloweenActDict[GEM_BUY_DAY_INDEX] = self.buy_gem_day_cnt
		HalloweenActDict[PETEVL_TIMES_FOREVER_INDEX] = self.Petevl_times_forever
		HalloweenActDict[FUWEN_SYN_INDEX] = self.Fuwen_syn_dict
		HalloweenActDict[MARRY_PARTY_TIMES_INDEX] = self.party_times_dict
		HalloweenActDict[COUPLES_FB_INDEX] = self.couples_fb_times

