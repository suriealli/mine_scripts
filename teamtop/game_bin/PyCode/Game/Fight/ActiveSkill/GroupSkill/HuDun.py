#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.GroupSkill.HuDun")
#===============================================================================
#吸收伤害：释放一个护盾吸收相当于自己攻击的百分之X伤害，最多承受3次攻击
#===============================================================================
from Game.Fight import SkillBase

class HuDun(SkillBase.ActiveSkillBase):
	skill_id = 2002			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	play_time = 1.5			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 15		#需要士气
	has_buff = True		#是否附带buff
	prefix_round = 0
	level_to_attack_rate=[0, 0.8, 0.9, 1, 1.1, 1.2]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	def select_targets(self):
		return self.unit.select_self()
	
	def do_effect(self, target):
		argv = int(self.skill_rate * self.unit.attack * self.level_to_attack_rate[self.argv] + self.skill_value)
		#玩家获得一个BUFF，吸收伤害值
		target.create_buff("ReduceHurt", 3, argv)

if "_HasLoad" not in dir():
	HuDun.reg()
