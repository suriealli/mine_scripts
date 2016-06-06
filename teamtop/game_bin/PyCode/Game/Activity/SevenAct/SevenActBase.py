#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.SevenAct.SevenActBase")
#===============================================================================
# 七日活动基础
#===============================================================================
import copy
import cDateTime
from Common.Message import AutoMessage
from Game.Activity.SevenAct import SevenActConfig
from Game.Role.Data import EnumObj, EnumInt16, EnumDayInt8

if "_HasLoad" not in dir():
	SEVEN_ACT_DURATION = 7 		#七日活动持续天数
	
	#Obj索引
	REWARD_STATUS_DICT_INDEX = 1	#奖励状态字典
	BUY_UNBIND_RMB_INDEX = 2		#累计充值神石
	FIRST_PAY_INDEX = 3				#首充
	FIRST_CONSUME_INDEX = 4			#每日首笔消费
	MOUNT_TRAIN_CNT_INDEX = 5		#坐骑培养次数
	LAST_LOGIN_DAYS_INDEX = 6		#最后登录天数
	LOGIN_CNT_INDEX = 7				#累计登录次数
	UNION_FB_CNT_INDEX = 8			#公会副本次数
	JJC_CNT_INDEX = 9				#挑战竞技场次数
	ACTIVE_VERSION = 10				#当前7日活动的版本号 
	#消息
	Seven_Act_Icon_Twinkle = AutoMessage.AllotMessage("Seven_Act_Icon_Twinkle", "通知客户端七日活动图标闪烁")

class SevenActMgr(object):
	def __init__(self, role):
		sevenActDict = role.GetObj(EnumObj.SevenAct)
		
		self.role = role
		
		self.reward_status_dict = copy.deepcopy(sevenActDict.get(REWARD_STATUS_DICT_INDEX, {}))
		self.buy_unbind_rmb = sevenActDict.get(BUY_UNBIND_RMB_INDEX, 0)
		self.is_first_pay = sevenActDict.get(FIRST_PAY_INDEX, False)
		self.is_first_consume = sevenActDict.get(FIRST_CONSUME_INDEX, False)
		self.mount_train_cnt = sevenActDict.get(MOUNT_TRAIN_CNT_INDEX, 0)
		self.last_login_days = sevenActDict.get(LAST_LOGIN_DAYS_INDEX, 0)
		self.login_cnt = sevenActDict.get(LOGIN_CNT_INDEX, 0)
		self.union_fb_cnt = sevenActDict.get(UNION_FB_CNT_INDEX, 0)
		self.jjc_cnt = sevenActDict.get(JJC_CNT_INDEX, 0)
		
		self.ActiveVersion = sevenActDict.get(ACTIVE_VERSION, 0)
		
		self.online_time = role.GetOnLineTimeToday()
		#不保存
		self.online_reward_tick_id = 0

	def is_active(self):
		'''
		是否活动时间
		@param actId:
		'''
		return SevenActConfig.IsActive
	
	
	def UpdateVersion(self):
		if self.ActiveVersion != SevenActConfig.ActiveVersion:
			#版本号不一致，可以重新领取了
			self.ActiveVersion = SevenActConfig.ActiveVersion
			self.last_login_days = 0
			self.login_cnt = 0
			self.reward_status_dict[6] = {}
			
			self.is_first_pay = False
			self.reward_status_dict[2] = {}
			
	
	
	def inc_buy_unbind_rmb(self, buyUnbindRMB):
		'''
		活动1
		累计充值
		@param buyUnbindRMB:
		'''
		actId = 1
		
		#是否活动期间
		if not self.is_active():
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		self.buy_unbind_rmb += buyUnbindRMB
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
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
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)
			
	def first_pay(self):
		'''
		活动2
		首充
		'''
		actId = 2
		
		#是否活动期间
		if not self.is_active():
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		#是否完成首充
		if self.is_first_pay is True:
			return
		self.is_first_pay = True
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
		
			#通知客户端
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)
			
	def day_first_consume(self):
		'''
		活动3
		每日首笔消费
		'''
		actId = 3
		
		#是否活动期间
		if not self.is_active():
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		#是否完成首充
		if self.is_first_consume is True:
			return
		self.is_first_consume = True
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
		
			#通知客户端
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)
			
	def gold(self):
		'''
		活动4
		点石成金
		'''
		actId = 4
		
		#是否活动期间
		if not self.is_active():
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
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
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)
			
	def mount_train(self, cnt):
		'''
		活动5
		坐骑养成
		@param cnt:
		'''
		actId = 5
		
		#是否活动期间
		if not self.is_active():
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		#增加坐骑培养次数
		self.mount_train_cnt += cnt
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.mount_train_cnt < idxConfig.needMountTrainCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)
			
	def login(self):
		'''
		活动6
		累计登录
		'''
		actId = 6
		
		#是否活动期间
		if not self.is_active():
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		#判断累计登录时间
		days = cDateTime.Days()
		if days > self.last_login_days:
			self.last_login_days = days
			self.login_cnt += 1
		else:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			#活动条件
			if self.login_cnt < idxConfig.needLoginCnt:
				continue
			
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)
			
	def purgatoryPass(self, purgatoryId, passLevel):
		'''
		活动7
		心魔挑战
		@param purgatoryId:
		@param passLevel:
		'''
		actId = 7
		
		#是否活动期间
		if not self.is_active():
			return
		
		if passLevel < 1:
			#没有通关
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})

		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
			if not idxConfig:
				continue
			
			#是否已有奖励状态
			if idx in actRewardDict:
				continue
			
			if idxConfig.needPurgatoryId != 3:
				#活动条件
				if idxConfig.needPurgatoryId:
					if purgatoryId != idxConfig.needPurgatoryId:
						continue
					#是否SS级以上通关
					if passLevel > 2:
						continue
				else:
					if self.role.GetDI8(EnumDayInt8.PurgatoryCnt) < idxConfig.needPurgatoryPassCnt:
						continue
			else:
				#三重最通关就可以
				if purgatoryId != idxConfig.needPurgatoryId:
					continue
			#1可以领取	2已领取
			actRewardDict[idx] = 1
			
			#通知客户端
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)

	
	def finish_gve_fb(self):
		'''
		活动8
		挑战组队副本
		'''
		actId = 8
		
		#是否活动期间
		if not self.is_active():
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
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
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)
			
	def challenge_jjc(self):
		'''
		活动9
		挑战竞技场
		'''
		actId = 9
		
		#是否活动期间
		if not self.is_active():
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		#完成次数+1
		self.jjc_cnt += 1
		
		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
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
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)
			
	def finish_fb(self):
		'''
		活动10
		挑战副本
		'''
		actId = 10
		
		#是否活动期间
		if not self.is_active():
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		#挑战副本次数
		finishFBCnt = 0
		fbDict = self.role.GetObj(EnumObj.FB_JoinData)
		for cnt in fbDict.itervalues():
			finishFBCnt += cnt
		
		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
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
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)
			
	def finish_union_fb(self):
		'''
		活动11
		挑战公会副本
		'''
		actId = 11
		
		#是否活动期间
		if not self.is_active():
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		#完成次数+1
		self.union_fb_cnt += 1
		
		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
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
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)
			
	def slave_play(self):
		'''
		活动12
		勇斗领主
		'''
		actId = 12
		
		#是否活动期间
		if not self.is_active():
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
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
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)
	
	def online_reward1(self):
		'''
		活动13
		在线奖励
		'''
		actId = 13
		
		#是否活动期间
		if not self.is_active():
			return
		
		idxList = SevenActConfig.SEVEN_ACT_ID_TO_IDX.get(actId)
		if not idxList:
			return
		
		actRewardDict = self.reward_status_dict.setdefault(actId, {})
		
		self.online_time = onlinesecond = self.role.GetOnLineTimeToday()
		
		for idx in idxList:
			idxConfig = SevenActConfig.SEVEN_ACT_REWARD.get((actId, idx))
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
			self.role.SendObj(Seven_Act_Icon_Twinkle, None)
	
	
	def save(self):
		sevenActDict = self.role.GetObj(EnumObj.SevenAct)
		
		sevenActDict[REWARD_STATUS_DICT_INDEX] = copy.deepcopy(self.reward_status_dict)
		sevenActDict[BUY_UNBIND_RMB_INDEX] = self.buy_unbind_rmb
		sevenActDict[FIRST_PAY_INDEX] = self.is_first_pay
		sevenActDict[FIRST_CONSUME_INDEX] = self.is_first_consume
		sevenActDict[MOUNT_TRAIN_CNT_INDEX] = self.mount_train_cnt
		sevenActDict[LAST_LOGIN_DAYS_INDEX] = self.last_login_days
		sevenActDict[LOGIN_CNT_INDEX] = self.login_cnt
		sevenActDict[UNION_FB_CNT_INDEX] = self.union_fb_cnt
		sevenActDict[JJC_CNT_INDEX] = self.jjc_cnt
		sevenActDict[ACTIVE_VERSION] = self.ActiveVersion


