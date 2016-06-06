#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.TianShenFuTi")
#===============================================================================
# 天神附体 10%概率重置技能CD
# 被动技能的ID从500开始
#===============================================================================
import random
from Game.Fight import SkillBase, Operate

class TianShenFuTi(SkillBase.PassiveSkill):
	skill_id = 504
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.level_to_lottery_rate = [0, 10]
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._after_skill.add(self.auto_u_after_skill)
	
	def unload_event(self):
		self.unit._after_skill.discard(self.auto_u_after_skill)
	# AutoCodeEnd
	
	# 下面开始写事件
	# 使用技能之后
	def auto_u_after_skill(self, unit, skill):
		if random.randint(0, 99) < self.level_to_lottery_rate[self.argv]:
			skill.do_round = self.fight.round - skill.cd_round
			self.fight.play_info.append((Operate.ClearSkillCD, unit.key, skill.skill_id))

if "_HasLoad" not in dir():
	TianShenFuTi.reg()
