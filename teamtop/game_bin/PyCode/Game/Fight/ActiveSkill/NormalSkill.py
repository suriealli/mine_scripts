#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.NormalSkill")
#===============================================================================
# 普通技能
#===============================================================================
from Game.Fight import SkillBase

class HeroNormalSkill(SkillBase.ActiveSkillBase):
	skill_id = 200
	prefix_round = 0
	cd_round = 0
	need_moral = 0
	play_time = 1.8			#播放时间（秒）
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_id, self.skill_value = argv
	
	def select_targets(self):
		return self.unit.select_front_row_first_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)

class MonsterNormalSkill(SkillBase.ActiveSkillBase):
	skill_id = 101
	prefix_round = 0
	cd_round = 0
	need_moral = 0
	play_time = 1.8			#播放时间（秒）
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_id = argv
		# 按照客户端的规则，重置服务端的并行播放设置
		if 200 < self.skill_id < 300:
			self.play_parallel = 1
		else:
			self.play_parallel = 0
	
	def select_targets(self):
		return self.unit.select_front_row_first_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)

class NoneSkill(SkillBase.ActiveSkillBase):
	skill_id = 9999			#技能ID
	def can_do(self):
		return False

if "_HasLoad" not in dir():
	HeroNormalSkill.reg()
	MonsterNormalSkill.reg()
	NoneSkill.reg()
