#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.EightStarAuxiliaryHeroB")
#===============================================================================
# 复活我方一个死亡单位，攻击力越高，额外恢复的生命越高。
#===============================================================================
from Game.Fight import SkillBase

class EightStarAuxiliaryHeroB(SkillBase.ActiveSkillBase):
	skill_id = 230			#技能ID
	#skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	#play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 5			#CD回合数
	need_moral = 0		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	level_to_hp_rate = [0, 0.4, 0.4]
	
	def can_do(self):
		# 如果这里是主角的主动技能不应该这样写，但是英雄的可以
		if SkillBase.ActiveSkillBase.can_do(self):
			return bool(self.camp.skill_revives)
		else:
			return False
	
	def do_after(self, targets):
		hp_upgrade = int(self.unit.attack * self.level_to_hp_rate[self.argv])
		self.camp.revive_unit(hp_upgrade)

if "_HasLoad" not in dir():
	EightStarAuxiliaryHeroB.reg()
