#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.SixStarDefendHero")
#===============================================================================
# 六星防将技能 攻击敌方竖排全部单位，并释放一个护盾，吸收大量伤害
# 英雄技能的ID从200开始
#===============================================================================
from Game.Fight import SkillBase

class SixStarDefendHero(SkillBase.ActiveSkillBase):
	skill_id = 220			#技能ID
	skill_rate = 1.47		#技能系数（1是平衡点）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	#is_aoe = False			#是否群攻
	level_to_value = [0, 0, 2500]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_cell_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
	
	def do_after(self, targets):
		argv = int(1.77 * self.unit.attack)
		self.unit.create_buff("ReduceHurt", 2, argv)

if "_HasLoad" not in dir():
	SixStarDefendHero.reg()
