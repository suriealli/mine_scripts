#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.GroupSkill.BaoHu")
#===============================================================================
# 分摊伤害;分担队友承受伤害的百分之X，最大不超过当前生命，持续1回合。
#===============================================================================
from Game.Fight import SkillBase

class BaoHu(SkillBase.ActiveSkillBase):
	skill_id = 2003			#技能ID
	skill_rate = 0.56		#技能系数（1是平衡点）
	play_time = 1.3			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 15		#需要士气
	is_aoe = True			#是否群攻
	aoe_need_target_cnt = 3
	prefix_round = 0			#前置回合
	level_to_connect_rate = [0, 0.3, 0.35, 0.4, 0.45, 0.5]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_random_member_exclude_self(n = 2)
	
	def do_effect(self, target):
		target.create_buff("HurtConnect", 1, ("BaoHu", 1, self.level_to_connect_rate[self.argv], self.unit))


if "_HasLoad" not in dir():
	BaoHu.reg()
