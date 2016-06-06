#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.GroupSkill.JingLongTuXi")
#===============================================================================
# 金龙突袭 基础攻击技能，随机攻击一个先前排再后排目标
#===============================================================================
from Game.Fight import SkillBase

class JingLongTuXi(SkillBase.ActiveSkillBase):
	skill_id = 2001
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数S
	need_moral = 0		#需要士气
	play_time = 2.3			#播放时间（秒）
	level_to_value = [0, 150, 300, 450, 600, 750]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_value = self.level_to_value[argv]
	
	def select_targets(self):
		return self.unit.select_front_row_first_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
	
	def do_after(self, targets):
		self.unit.change_moral(8)

if "_HasLoad" not in dir():
	JingLongTuXi.reg()
