#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.FindBack.FindBackBase")
#===============================================================================
# 找回基础
#===============================================================================
from Util.File import TabFile
from Game.FindBack import FindBackDefine


class FindBackReward_Base(TabFile.TabLine):
	def __init__(self):
		self.level = int

		self.qna_f_money = int
		self.qna_f_items = self.GetEvalByString
		
		self.df_f_exp = int
		self.df_f_money = int
		
		self.hw_f_money = int
		self.hw_f_reputation = int
		self.hw_f_items = self.GetEvalByString
		
		self.jjc_f_reputation = int
		self.jjc_f_items = self.GetEvalByString
		
		self.daytask_f_exp = int
		self.daytask_f_money = int
		self.daytask_f_items = self.GetEvalByString

		self.dl_f_exp = int
		self.cfb_f_items = self.GetEvalByString


	def RewardRole(self, role, index, cnt, rewardtype = 0):
		exp= 0
		money = 0
		rmb = 0
		reputation = 0
		items = {}
		tili = 0
		if index == FindBackDefine.QNAFB:
			money = self.qna_f_money * cnt
			role.IncMoney(money)
			if self.qna_f_items:
				for itemCoding, itemCnt in self.qna_f_items:
					role.AddItem(itemCoding, itemCnt * cnt)
					items[itemCoding] = items.get(itemCoding, 0) + itemCnt * cnt
					
		elif index == FindBackDefine.DFFB:
			exp = self.df_f_exp * cnt
			money = self.df_f_money * cnt
			role.IncExp(exp)
			role.IncMoney(money)
		elif index == FindBackDefine.HWFB:
			money = self.hw_f_money * cnt
			reputation = self.hw_f_reputation * cnt
			role.IncMoney(money)
			role.IncReputation(reputation)
			if self.hw_f_items:
				for itemCoding, itemCnt in self.hw_f_items:
					role.AddItem(itemCoding, itemCnt * cnt)
					items[itemCoding] = items.get(itemCoding, 0) + itemCnt * cnt
		elif index == FindBackDefine.JJCFB:
			reputation = self.jjc_f_reputation * cnt
			role.IncReputation(reputation)
			if self.jjc_f_items:
				for itemCoding, itemCnt in self.jjc_f_items:
					role.AddItem(itemCoding, itemCnt * cnt)
					items[itemCoding] = items.get(itemCoding, 0) + itemCnt * cnt
		elif index == FindBackDefine.DAYTASKFB:
			exp = self.daytask_f_exp * cnt
			role.IncExp(exp)
			money = self.daytask_f_money * cnt
			role.IncMoney(money)
			for itemCoding, itemCnt in self.daytask_f_items:
				role.AddItem(itemCoding, itemCnt * cnt)
				items[itemCoding] = items.get(itemCoding, 0) + itemCnt * cnt
		elif index == FindBackDefine.DLFB:
			exp = self.dl_f_exp * cnt
			role.IncExp(exp)
		elif index == FindBackDefine.CFBFB:
			for itemCoding, itemCnt in self.cfb_f_items:
				role.AddItem(itemCoding, itemCnt * cnt)
				items[itemCoding] = items.get(itemCoding, 0) + itemCnt * cnt
		else:
			print "GE_EXC FindBackReward error index(%s) role (%s)" % (index, role.GetRoleID())
	
		return (exp, money, rmb, reputation, items, tili)


class FindBackOther_Base(TabFile.TabLine):
	def __init__(self):
		self.vipType = int
		
		self.bindrmb_reward_money = int
		self.bindrmb_reward_items = self.GetEvalByString
		
		self.rmb_reward_money = int
		self.rmb_reward_items = self.GetEvalByString
		
		self.money_reward_money = int
		self.money_reward_items = self.GetEvalByString
		
	def RewardRole(self, role, index, cnt, rewardType):
		exp= 0
		money = 0
		rmb = 0
		reputation = 0
		items = {}
		tili = 0
		
		if rewardType == FindBackDefine.RMB_Reward:
			money = self.rmb_reward_money * cnt
			role.IncMoney(money)
			if self.rmb_reward_items:
				for itemCoding, itemCnt in self.rmb_reward_items:
					role.AddItem(itemCoding, itemCnt * cnt)
					items[itemCoding] = items.get(itemCoding, 0) + itemCnt * cnt
		elif rewardType == FindBackDefine.BindRMB_Reward:
			money = self.bindrmb_reward_money * cnt
			role.IncMoney(money)
			if self.bindrmb_reward_items:
				for itemCoding, itemCnt in self.bindrmb_reward_items:
					role.AddItem(itemCoding, itemCnt * cnt)
					items[itemCoding] = items.get(itemCoding, 0) + itemCnt * cnt
		elif rewardType == FindBackDefine.MoneyReward:
			money = self.money_reward_money * cnt
			role.IncMoney(money)
			if self.money_reward_items:
				for itemCoding, itemCnt in self.money_reward_items:
					role.AddItem(itemCoding, itemCnt * cnt)
					items[itemCoding] = items.get(itemCoding, 0) + itemCnt * cnt
		return (exp, money, rmb, reputation, items, tili)
