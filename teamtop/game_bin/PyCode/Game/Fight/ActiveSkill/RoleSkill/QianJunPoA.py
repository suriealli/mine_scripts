#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.RoleSkill.QianJunPoA")
#===============================================================================
# 千军破 2次选择攻击目标，消耗12点怒气
#===============================================================================
from Game.Fight import SkillBase, Operate

class QianJunPoA(SkillBase.ActiveSkillBase):
	play_time = 3.0			#播放时间（秒）
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 12		#需要士气
	level_to_value = [0, 900, 1050, 1200, 1350, 1500]
	level_to_rate = [0, 0.824, 0.832, 0.84, 0.848, 0.864]
	
	def __init__(self, unit, argv):
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		self.skill_value = self.level_to_value[argv]
		self.skill_rate = self.level_to_rate[argv]
		
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
		targets = self.unit.select_front_row_first_enemy()
		if targets:
			self.do_target(targets[0])
		targets = self.unit.select_front_row_first_enemy()
		if targets:
			self.do_target(targets[0])
		do_targets_play_info = FIGHT.new_play_info()
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


if "_HasLoad" not in dir():
	QianJunPoA.reg()
