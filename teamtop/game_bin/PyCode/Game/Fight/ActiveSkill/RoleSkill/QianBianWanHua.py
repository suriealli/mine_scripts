#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.RoleSkill.QianBianWanHua")
#===============================================================================
# 千变万化 召唤两个单位出战
#===============================================================================
from Game.Fight import SkillBase

class QianBianWanHua(SkillBase.ActiveSkillBase):
	prefix_round = 0		#前置回合数
	cd_round = 7			#CD回合数
	need_moral = 30		#需要士气
	play_time = 3.6			#播放时间（秒）
	leave_to_hp = [0.1, 0.6, 0.7, 0.8, 0.9, 1.0]
	
	def do_after(self, targets):
		if self.fight.group == 3:
			return
		CAMP = self.camp
		for pos in (1, 5):
			unit = CAMP.pos_units.get(pos * CAMP.mirror)
			if unit is None:
				unit = self.camp.real_create_one_monster_unit(pos, 1)
				unit.attack = int(self.unit.attack * 0.3)
				unit.hp = unit.max_hp = int(self.leave_to_hp[self.argv] * self.unit.max_hp)
				unit.create(unit.run_create)
				unit.join_fight()
				# 补偿时间
				self.fight.add_play_time(2.0)
			else:
				unit.change_hp(unit.max_hp)

if "_HasLoad" not in dir():
	QianBianWanHua.reg()
