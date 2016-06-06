#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.SevenStarAttackHeroSSS")
#===============================================================================
# 攻击4次地方随机单体目标，额外造成3500点伤害，并有几率造成昏迷，持续2回合
#===============================================================================

from Game.Fight import SkillBase, Operate

class SevenStarAttackHeroSSS(SkillBase.ActiveSkillBase):
	skill_id = 406			#技能ID
	skill_rate = 1.0
	#play_time = 1.0			#播放时间（秒）
	cd_round = 3			#CD回合数
	need_moral = 0		#需要士气
	is_aoe = True			#是否群攻
	level_to_value = [0, 0, 3500]
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
		targets = self.unit.select_random_enemy()
		if targets:
			self.do_target(targets[0])
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
		target.create_stun(20, 2)


if "_HasLoad" not in dir():
	SevenStarAttackHeroSSS.reg()
