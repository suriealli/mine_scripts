#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.ElementalSpiritFire")
# 元素之灵：烈火之灵技能
#===============================================================================
# 元素之灵技能
#===============================================================================
from Game.Fight import SkillBase

class ElementalSpiritFire(SkillBase.PassiveSkill):
	skill_id = 830
	level_to_target_skill_rate = [0, 0.04, 0.08, 0.12, 0.16, 0.2]
	unsuitable_skill_rate = 0
	stifile_skill_rate = 0.5
	unstifile_skill_rate = 1
	stifile_id = 831
	unsuitable_id1 = 832
	unsuitable_id2 = 830
	
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.unit._before_target.add(self.auto_u_before_target)
	
	def unload_event(self):
		self.unit._before_target.discard(self.auto_u_before_target)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_u_before_target(self,unit,skill):
		if not self.fight.config.pvp:
			return
		level = self.argv
		stifile = self.unstifile_skill_rate
		
		if unit.passive_skills:
			for ps in unit.passive_skills:
				if ps.skill_id == self.unsuitable_id1 or ps.skill_id == self.unsuitable_id2:
					stifile = self.unsuitable_skill_rate
					break
				elif ps.skill_id == self.stifile_id:
					if ps.argv <=level:
						break
					elif ps.argv >level:
						stifile = self.stifile_skill_rate
						break
					
				
		if skill.is_treat:
			return
		
		skill.target_skill_rate += self.level_to_target_skill_rate[level] * stifile
		
		
if "_HasLoad" not in dir():
	ElementalSpiritFire.reg()
