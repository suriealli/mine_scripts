#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.RoleSkill.FuMoZhanA")
#===============================================================================
# 伏魔斩 基础攻击技能，随机攻击一个先前排再后排目标，使用后恢复8点怒气
#===============================================================================
from Game.Fight import SkillBase

class FuMoZhanA(SkillBase.ActiveSkillBase):
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数S
	need_moral = 0		#需要士气
	play_time = 2.3			#播放时间（秒）
	level_to_value = [0, 900, 1050, 1200, 1350, 1500]
	level_to_rate = [0, 1.03, 1.04, 1.05, 1.06, 1.08]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_value = self.level_to_value[argv]
		self.skill_rate = self.level_to_rate[argv]
	
	def select_targets(self):
		return self.unit.select_front_row_first_enemy()
	
	def do_effect(self, target):
		self.do_hurt(target)
	
	def do_after(self, targets):
		self.unit.change_moral(8)


if "_HasLoad" not in dir():
	FuMoZhanA.reg()
