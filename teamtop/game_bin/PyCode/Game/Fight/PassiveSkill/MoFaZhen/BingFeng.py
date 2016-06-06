#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.MoFaZhen.BingFeng")
#===============================================================================
# 攻击有一定概率触发眩晕。持续1回合无法出手不能释放任何技能。（其中群攻有概率眩晕一个单位。）被眩晕后，伤害加成一定的百分比
#===============================================================================
from Game.Fight import SkillBase
import random

class BingFeng(SkillBase.PassiveSkill):
	skill_id = 700
	Level_to_stun_rate = [0, 15, 22.5, 30, 37.5, 50]
	level_to_damage_reduce_rate = [0, 0, 0, 0, 0, 0]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.targets = []
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._after_skill.add(self.auto_u_after_skill)
		self.unit._before_skill.add(self.auto_u_before_skill)
		self.unit._before_target.add(self.auto_u_before_target)
	
	def unload_event(self):
		self.unit._after_skill.discard(self.auto_u_after_skill)
		self.unit._before_skill.discard(self.auto_u_before_skill)
		self.unit._before_target.discard(self.auto_u_before_target)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_before_skill(self, unit, skill):
		self.targets = []
	
	def auto_u_before_target(self, target, skill):
		if target.camp is self.camp:
				return
		self.targets.append(target)
	
	def auto_u_after_skill(self, unit, skill):
		l = []
		for target in self.targets:
			if target.is_out:
				continue
			if target.stun:
				continue
			l.append(target)
		if not l:
			return
		target = random.choice(l)
		buff = target.create_stun(self.Level_to_stun_rate[self.argv], 2, 18)
		if buff is not None:
			target.create_buff("AddDemage", 2, self.level_to_damage_reduce_rate[self.argv])

if "_HasLoad" not in dir():
	BingFeng.reg()
