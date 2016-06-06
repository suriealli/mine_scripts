#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.RoleSkill.ShenGuiMoDi")
#===============================================================================
# 神鬼莫敌 一回合内攻击3次，消耗60点怒气，有概率回复30点怒气值，等却CD3回合
#===============================================================================
from Game.Fight import SkillBase, Operate
import random

class ShenGuiMoDi(SkillBase.ActiveSkillBase):
	skill_rate = 1.5		#技能系数（1是平衡点）
	play_time = 3.5			#播放时间（秒）
	prefix_round = 0		#前置回合数
	cd_round = 3			#CD回合数
	need_moral = 60		#需要士气
	level_to_value = [0, 360, 720, 1080, 1440, 1800]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_value = self.level_to_value[argv]
	
	# 释放技能
	def do(self):
		#targets = self.select_targets()
		FIGHT = self.fight
		UNIT = self.unit
		# 记录释放回合数
		self.do_round = FIGHT.round
		# 修改play_info
		fight_play_info = FIGHT.new_play_info()
		# 尝试扣士气
		if self.need_moral:
			self.unit.change_moral(-self.need_moral)
		# 触发事件
		UNIT.before_skill(self)
		# 出手前
		do_before_play_info = FIGHT.new_play_info()
		# 出手
		targets = self.unit.select_random_enemy()
		if targets:
			self.do_target(targets[0])
		targets = self.unit.select_random_enemy()
		if targets:
			self.do_target(targets[0])
		targets = self.unit.select_random_enemy()
		if targets:
			self.do_target(targets[0])
		do_targets_play_info = FIGHT.new_play_info()
		# 出手后
		self.do_after(targets)
		# 触发事件
		UNIT.after_skill(self)
		# 构建播放列表
		do_after_play_info = FIGHT.play_info
		fight_play_info.append((Operate.UserSkill, UNIT.key, self.skill_id, do_before_play_info, do_targets_play_info, do_after_play_info))
		# 计算播放时间
		self.fight.add_play_time(self.play_time, self.play_parallel)
		# 还原play_info
		FIGHT.restore_play_info(fight_play_info)
	
	def do_effect(self, target):
		self.do_hurt(target)
	
	def do_after(self, targets):
		if random.randint(0, 99) < 30:
			self.unit.change_moral(30)


if "_HasLoad" not in dir():
	ShenGuiMoDi.reg()
