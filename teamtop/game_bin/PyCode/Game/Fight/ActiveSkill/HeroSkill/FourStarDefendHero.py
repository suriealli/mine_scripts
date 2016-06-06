#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.FourStarDefendHero")
#===============================================================================
# 四星防将主动技能 攻击敌方先期排再后排单位，吸血，并提升自己防御力
# 英雄技能的ID从200开始
#===============================================================================
from Game.Fight import SkillBase

class FourStarDefendHero(SkillBase.ActiveSkillBase):
	skill_id = 213			#技能ID
	skill_rate = 0.8		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	is_treat = True		#是治疗
	level_to_prefixround = [2, 1, 0]	#前置回合数
	level_to_hurt_value = [0, 0, 600]
	level_to_treat_value = [0, 0, 700]
	
	def __init__(self, unit, argv):
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def need_treat(self):
		return self.unit.hp < int(0.8 * self.unit.max_hp)
	
	def select_targets(self):
		return self.unit.select_front_row_first_enemy()
	
	def do_effect(self, target):
		
		self.skill_value = self.level_to_hurt_value[self.argv]
		self.skill_rate = 0.8
		self.do_hurt(target)
		
		self.skill_value = self.level_to_treat_value[self.argv]
		self.skill_rate = 1.5
		self.do_treat(self.unit)
		
		#攻击后单位自身获得一个提升防御的BUFF
		self.unit.create_buff("AddDefend", 3, 500)


if "_HasLoad" not in dir():
	FourStarDefendHero.reg()
