#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.SixStarAttackHeroBSSS")
#===============================================================================
# 攻击地方后排随机单体目标，额外造成3000点伤害，大概率造成2倍伤害。
#===============================================================================
import random
from Game.Fight import SkillBase, Operate


class SixStarAttackHeroBSSS(SkillBase.ActiveSkillBase):
	skill_id = 404			#技能ID
	skill_rate = 2.5	#技能系数（1是平衡点）
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	level_to_value = [0, 0, 2500]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
	
	# 释放技能
	def do(self):
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
		targets = self.unit.select_back_row_first_enemy()
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
	
	# 修正伤害计算
	def computer_hurt(self, target, no_defence=False):
		hurt = SkillBase.ActiveSkillBase.computer_hurt(self, target, no_defence)
		if random.randint(0, 99) < 30:
			hurt *= 2
		return hurt

if "_HasLoad" not in dir():
	SixStarAttackHeroBSSS.reg()
