#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.StarGirl.MianYiHuiFu")
#===============================================================================
# 主角受到致命伤害时保留1点生命并免疫伤害至回合结束,回合结束后恢复10%生命。（PVE无效）（一场战斗仅生效1次）
#===============================================================================
from Game.Fight import SkillBase, UnitEx, Operate

class MianYiHuiFu(SkillBase.PassiveSkill):
	skill_id = 3047
	
	def __init__(self, unit, argv):
		self.trigger_round = 0
		SkillBase.PassiveSkill.__init__(self, unit, argv)
		self.virtual_buff_key = self.fight.allot_key()
	
	# AutoCodeBegin
	def load_event(self):
		self.camp._join.add(self.auto_c_join)
		self.fight._after_round.add(self.auto_f_after_round)
		self.unit._before_hurt.add(self.auto_u_before_hurt)
	
	def unload_event(self):
		self.camp._join.discard(self.auto_c_join)
		self.fight._after_round.discard(self.auto_f_after_round)
		self.unit._before_hurt.discard(self.auto_u_before_hurt)
	# AutoCodeEnd
	
	# 下面开始写事件代码
	def auto_c_join(self, unit):
		if type(unit) is not UnitEx.MainUnit:
			return
		if unit.role_id != self.unit.role_id:
			return
		# 偷偷的给主角加上本被动技能
		self.__class__(unit, self.argv)
	
	def auto_u_before_hurt(self, unit, original_jap, now_jap):
		if not self.fight.pvp:
			return now_jap
		if self.trigger_round:
			if self.trigger_round == self.fight.round:
				return 0
			else:
				return now_jap
		else:
			# 处理复活继承的状态
			if self.has_revive_status():
				return now_jap
			if now_jap >= unit.hp:
				self.trigger_round = self.fight.round
				# 复活要继承这个状态
				self.make_revive_status()
				unit.change_hp(-unit.hp + 1)
				# 这里创建一个虚拟的buff
				self.fight.play_info.append((Operate.CreateBuff, self.virtual_buff_key, unit.key, 17, 1))
				return 0
			else:
				return now_jap
	
	# 回合结束
	def auto_f_after_round(self):
		if self.trigger_round == self.fight.round:
			self.unit.treat(int(self.unit.max_hp * 0.1), self.unit)
			# 删除虚拟buff
			self.fight.play_info.append((Operate.DeleteBuff, self.virtual_buff_key))

if "_HasLoad" not in dir():
	MianYiHuiFu.reg()
