#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.GroupSkill.ShangHaiLianJie")
#===============================================================================
# 伤害链接：链接的单位额外受到百分之X伤害，持续2回合
#===============================================================================
from Game.Fight import SkillBase

class ShangHaiLianJie(SkillBase.ActiveSkillBase):
	skill_id = 2008			#技能ID
	skill_rate = 0.56		#技能系数（1是平衡点）
	play_time = 1.3			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 15		#需要士气
	is_aoe = True			#是否群攻
	aoe_need_target_cnt = 3
	prefix_round = 0
	level_to_connect_rate = [0, 0.2, 0.225, 0.25, 0.275, 0.3]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_all_enemy()
	
	def do_effect(self, target):
		target.create_buff("HurtConnect", 2, ("ShangHaiLianJie", 1, self.level_to_connect_rate[self.argv]))

if "_HasLoad" not in dir():
	ShangHaiLianJie.reg()
