#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.MonsterSkill.LiTianWang")
#===============================================================================
# 大闹天宫BOSS特殊技能 攻击敌方随机单个单位并眩晕
# 怪物技能的ID从1000开始
#===============================================================================
from Game.Fight import SkillBase

class LiTianWang(SkillBase.ActiveSkillBase):
	skill_id = 301			#技能ID
	skill_rate = 0.35		#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	prefix_round = 0		#前置回合数
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	has_buff = True		#是否附带buff
	level_to_value = [0, 0, 500]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_value = self.level_to_value[argv]
	
	def select_targets(self):
		return self.unit.select_random_enemy(n = 1)
	
	def do_effect(self, target):
		self.do_hurt(target)
		target.create_stun(100, 2)


if "_HasLoad" not in dir():
	LiTianWang.reg()
