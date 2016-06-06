#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.FiveStarDefendHero")
#===============================================================================
# 五星防将主动技能 攻击敌方全体单位，降低对方治疗效果，且增加自身防御值
# 英雄技能的ID从200开始
#===============================================================================
from Game.Fight import SkillBase

class FiveStarDefendHero(SkillBase.ActiveSkillBase):
	skill_id = 216			#技能ID
	skill_rate = 0.35		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True			#是否群攻
	has_buff = True		#是否附带buff
	level_to_value = [0, 0, 200]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
		target.create_buff("ReduceTreatRate", 2, 0.2)
	
	def do_after(self, targets):
		self.unit.create_buff("AddDefend", 2, 500)


if "_HasLoad" not in dir():
	FiveStarDefendHero.reg()
