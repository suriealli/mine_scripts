#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.MoFaZhen.ChongZhiCD")
#===============================================================================
# 战斗中，有一定概率重置CD。
#===============================================================================
import random
from Game.Fight import SkillBase, Operate

class ChongZhiCD(SkillBase.PassiveSkill):
	skill_id = 701
	level_to_lottery_rate = [0, 8, 12, 16, 20, 25]
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._after_skill.add(self.auto_u_after_skill)
	
	def unload_event(self):
		self.unit._after_skill.discard(self.auto_u_after_skill)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_after_skill(self, unit, skill):
		if unit.is_out:
			return
		if random.randint(0, 99) < self.level_to_lottery_rate[self.argv]:
			if unit.unit_type == 1:
				for skill in unit.active_skills:
					if skill is self:
						continue
					skill.set_round(-9)
			else:
				for skill in unit.active_skills:
					if skill is self:
						continue
					skill.do_round = self.fight.round - skill.cd_round
			self.fight.play_info.append((Operate.ClearSkillCD, unit.key, skill.skill_id))

if "_HasLoad" not in dir():
	ChongZhiCD.reg()
