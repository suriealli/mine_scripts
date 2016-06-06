#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.FiveStarAuxiliaryHero")
#===============================================================================
# 五星辅将主动技能 增加全队攻击力 并增加全队50%暴击效果
# 英雄技能的ID从200开始
#===============================================================================
from Game.Fight import SkillBase

class FiveStarAuxiliaryHero(SkillBase.ActiveSkillBase):
	skill_id = 217			#技能ID
	skill_rate = 0.3		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	has_buff = True		#是否附带buff
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.add_attack = int(self.skill_rate * self.unit.attack)
		
	def select_targets(self):
		return self.unit.select_all_member()
	
	def do_effect(self, target):
		target.create_buff("AddAttackAndCrit", 3, self.add_attack)


if "_HasLoad" not in dir():
	FiveStarAuxiliaryHero.reg()
