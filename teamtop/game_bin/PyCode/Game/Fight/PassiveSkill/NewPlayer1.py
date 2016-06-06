#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.PassiveSkill.NewPlayer1")
#===============================================================================
# 北美版新手特殊战斗被动技能，用于战斗中召唤
#===============================================================================
from Game.Fight import SkillBase, Middle, UnitEx

HERO_DATA = {
		Middle.HeroType: 81,
		Middle.FightPos: 3,
		Middle.Level: 60,
		Middle.Career: 2,
		Middle.PetType:0,
		Middle.NormalSkill: ("HeroNormalSkill",(251,2)),
		Middle.ActiveSkill: (201,2),
		Middle.PassiveSkills: [], 
		Middle.MaxHP: 2000,
		Middle.Morale: 0,
		Middle.Speed: 100,
		Middle.AttackP: 210000,
		Middle.AttackM: 210000,
		Middle.DefenceP: 0,
		Middle.DefenceM: 0,
		Middle.Crit: 10000,
		Middle.CritPress: 100,
		Middle.AntiBroken: 20000,
		Middle.NotBroken: 1000,
		Middle.Parry: 100,
		Middle.Puncture: 100,
		Middle.DamageUpgrade: 20000,
		Middle.DamageReduce: 10000,
		}

class NewPlayer1(SkillBase.PassiveSkill):
	# AutoCodeBegin
	def load_event(self):
		self.fight._after_round.add(self.auto_f_after_round)
	
	def unload_event(self):
		self.fight._after_round.discard(self.auto_f_after_round)
	# AutoCodeEnd
	
	# 回合开始
	def auto_f_after_round(self):
		if self.fight.round == 2:
			unit1 = self.other_camp.real_create_one_monster_unit(1, 11003)#位置，ID
			unit1.create(unit1.run_create)
			unit1.join_fight()
			unit2 = self.other_camp.real_create_one_monster_unit(5, 11003)#位置，ID
			unit2.create(unit2.run_create)
			unit2.join_fight()
			# 补偿时间
			self.fight.add_play_time(2.0)
		elif self.fight.round == 3:
			HERO_DATA[Middle.RoleID] = self.unit.role_id
			hero_pos = 1 * self.camp.mirror
			self.camp.pos_units[hero_pos] = unit = UnitEx.HeroUnit(hero_pos, self.camp, HERO_DATA, self.unit)
			unit.create(unit.run_create)
			unit.join_fight()
	
if "_HasLoad" not in dir():
	NewPlayer1.reg()
