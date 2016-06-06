#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.HeroSkill.FuHuo")
#===============================================================================
# 主动技能说明
#===============================================================================
from Game.Fight import SkillBase

class FuHuo(SkillBase.ActiveSkillBase):
	#skill_id = 8888			#技能ID
	#skill_rate = 1.0		#技能系数（1是平衡点）
	#skill_value = 0			#技能绝对值
	#play_time = 1.0			#播放时间（秒）
	#play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 0			#CD回合数
	need_moral = 40		#需要士气
	#is_aoe = False			#是否群攻
	#has_buff = False		#是否附带buff
	
	def can_do(self):
		# 如果这里是主角的主动技能不应该这样写，但是英雄的可以
		if SkillBase.ActiveSkillBase.can_do(self):
			return bool(self.camp.skill_revives)
		else:
			return False
	
	def do_after(self, targets):
		self.camp.revive_unit(1)

if "_HasLoad" not in dir():
	FuHuo.reg()
