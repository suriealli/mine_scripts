#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.TwoStarAuxiliaryHero")
#===============================================================================
# 二星辅助将 回复己方血量最小的单位的气血,并驱散其身上全部不利BUFF
# 英雄技能的ID从200开始
#===============================================================================
from Game.Fight import SkillBase

class TwoStarAuxiliaryHero(SkillBase.ActiveSkillBase):
	skill_id = 205			#技能ID
	skill_rate = 1.6		#技能系数（1是平衡点）
	play_time = 1.3			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	level_to_value = [0, 0, 1000]
	level_to_prefixround = [2, 1, 0]
	is_treat = True
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_least_hp_member()
	
	def do_effect(self, target):
		self.do_treat(target)
		target.clear_buff(buff_info = False)


if "_HasLoad" not in dir():
	TwoStarAuxiliaryHero.reg()
