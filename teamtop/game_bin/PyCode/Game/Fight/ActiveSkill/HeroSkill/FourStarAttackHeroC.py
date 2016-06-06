#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.FourStarAttackHeroC")
#===============================================================================
#连续两次攻击敌方竖排目标，额外造成2400的伤害，忽视目标防御。
#===============================================================================
from Game.Fight import SkillBase, Operate

class FourStarAttackHeroC(SkillBase.ActiveSkillBase):
	skill_id = 306			#技能ID
	skill_rate = 1.2		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	play_time = 1.4			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	#prefix_round = 999		#前置回合数
	cd_round = 2		#CD回合数
	need_moral = 0		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	level_to_value = [0, 0, 2400]
	level_to_prefixround = [2, 1, 0]
	
	def __init__(self, unit, argv):
		self.skill_value = self.level_to_value[argv]
		self.prefix_round = self.level_to_prefixround[argv]
		SkillBase.ActiveSkillBase.__init__(self, unit, argv)
		
	def select_targets(self):
		return self.unit.select_cell_enemy()
	
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
		targets = self.unit.select_cell_enemy()
		for target in targets:
			self.do_target(target)
		for target in targets:
			if target.is_out:
				continue
			self.do_target(target)
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
		self.do_hurt(target, True)


if "_HasLoad" not in dir():
	FourStarAttackHeroC.reg()
