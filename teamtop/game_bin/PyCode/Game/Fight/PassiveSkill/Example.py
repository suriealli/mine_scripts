#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.Example")
#===============================================================================
# 技能样例
# 被动技能的ID从500开始
#===============================================================================
from Game.Fight import SkillBase

class Example(SkillBase.PassiveSkill):
	skill_id = 1
	
	def __init__(self, unit, argv):
		SkillBase.PassiveSkill.__init__(self, unit, argv)
	
	# AutoCodeBegin
	def load_event(self):
		self.camp._join.add(self.auto_c_join)
		self.fight._after_round.add(self.auto_f_after_round)
		self.fight._before_round.add(self.auto_f_before_round)
		self.unit._after_skill.add(self.auto_u_after_skill)
		self.unit._before_skill.add(self.auto_u_before_skill)
		self.unit._change_hp.add(self.auto_u_change_hp)
		self.unit._has_be_kill.add(self.auto_u_has_be_kill)
		self.unit._has_kill.add(self.auto_u_has_kill)
	
	def unload_event(self):
		self.camp._join.discard(self.auto_c_join)
		self.fight._after_round.discard(self.auto_f_after_round)
		self.fight._before_round.discard(self.auto_f_before_round)
		self.unit._after_skill.discard(self.auto_u_after_skill)
		self.unit._before_skill.discard(self.auto_u_before_skill)
		self.unit._change_hp.discard(self.auto_u_change_hp)
		self.unit._has_be_kill.discard(self.auto_u_has_be_kill)
		self.unit._has_kill.discard(self.auto_u_has_kill)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	
	# 有人加入战斗
	def auto_c_join(self, unit):
		#unit.create_buff("Example", 8, None)
		pass
	# 回合开始
	def auto_f_before_round(self):
		pass
	
	# 回合结束
	def auto_f_after_round(self):
		pass
	
	# 使用技能之前
	def auto_u_before_skill(self, unit, skill):
		pass
	
	# 使用技能之后
	def auto_u_after_skill(self, unit, skill):
		pass
	
	# 击杀
	def auto_u_has_kill(self, unit, target):
		pass
	
	# 被杀
	def auto_u_has_be_kill(self, source, unit):
		pass
	
	# 改变血量
	def auto_u_change_hp(self, unit, jap):
		pass

if "_HasLoad" not in dir():
	Example.reg()
