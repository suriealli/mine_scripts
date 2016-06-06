#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.ActiveSkill.MonsterSkill.FBMonsterSkill")
#===============================================================================
# 副本怪物的技能
# 怪物技能的ID从1000开始
#===============================================================================
from Game.Fight.ActiveSkill.MonsterSkill import AttackOneEnemy
from Game.Fight.ActiveSkill.MonsterSkill import HealOneTeammate
from Game.Fight.ActiveSkill.MonsterSkill import NeZa
from Game.Fight.ActiveSkill.MonsterSkill import SelfDefendUp
from Game.Fight.ActiveSkill.HeroSkill import TwoStarAttackHero
from Game.Fight.ActiveSkill.HeroSkill import OneStarDefendHero
from Game.Fight.ActiveSkill.HeroSkill import OneStarAttackHero
from Game.Fight.ActiveSkill.HeroSkill import TwoStarDefendHero
from Game.Fight.ActiveSkill.HeroSkill import OneStarAuxiliaryHero
from Game.Fight.ActiveSkill.HeroSkill import ThreeStarDefendHero
from Game.Fight.ActiveSkill.HeroSkill import ThreeStarAuxiliaryHero
from Game.Fight.ActiveSkill.HeroSkill import ThreeStarAttackHeroA
from Game.Fight.ActiveSkill.HeroSkill import FourStarAttackHeroA
from Game.Fight.ActiveSkill.HeroSkill import FiveStarDefendHero
from Game.Fight.ActiveSkill.HeroSkill import TwoStarAuxiliaryHero
from Game.Fight.ActiveSkill.HeroSkill import FourStarDefendHero
from Game.Fight.ActiveSkill.HeroSkill import FourStarAuxiliaryHero
from Game.Fight.ActiveSkill.HeroSkill import ThreeStarAttackHeroB
from Game.Fight.ActiveSkill.HeroSkill import FiveStarAttackHero
from Game.Fight.ActiveSkill.HeroSkill import FiveStarAuxiliaryHero
from Game.Fight.ActiveSkill.HeroSkill import FourStarAttackHeroB
from Game.Fight.ActiveSkill.HeroSkill import SixStarAttackHeroA
from Game.Fight.ActiveSkill.HeroSkill import SixStarAttackHeroB
from Game.Fight.ActiveSkill.HeroSkill import SixStarDefendHero
from Game.Fight.ActiveSkill.HeroSkill import SixStarAuxiliaryHero

class GuanQia2(HealOneTeammate.HealOneTeammate):
	skill_id = 1001
	skill_rate = 1.45
	level_to_value = [0, 0, 0]

class GuanQia4(TwoStarAttackHero.TwoStarAttackHero):
	skill_id = 1002
	skill_rate = 0.55
	level_to_value = [0, 0, 0]

class GuanQia6(OneStarDefendHero.OneStarDefendHero):
	skill_id = 1003
	level_to_value = [0, 0, 0]
	
	def do_effect(self, target):
		
		self.skill_value = self.level_to_hurt_value[self.argv]
		self.skill_rate = 1.0
		self.do_hurt(target)
		
		self.skill_value = self.level_to_treat_value[self.argv]
		self.skill_rate = 1.22
		self.do_treat(self.unit)

class GuanQia8(AttackOneEnemy.AttackOneEnemy):
	skill_id = 1004
	skill_rate = 1.43
	level_to_value = [0, 0, 0]

class GuanQia12(HealOneTeammate.HealOneTeammate):
	skill_id = 1005
	skill_rate = 1.53
	level_to_value = [0, 0, 0]

class GuanQia14(OneStarAttackHero.OneStarAttackHero):
	skill_id = 1006
	skill_rate = 0.55
	level_to_value = [0, 0, 0]

class GuanQia16(TwoStarDefendHero.TwoStarDefendHero):
	skill_id = 1007
	level_to_value = [0, 0, 0]

class GuanQia17(AttackOneEnemy.AttackOneEnemy):
	skill_id = 1008
	skill_rate = 1.0
	level_to_value = [0, 0, 0]

class GuanQia18(TwoStarDefendHero.TwoStarDefendHero):
	skill_id = 1009
	level_to_value = [0, 0, 0]

class GuanQia19(HealOneTeammate.HealOneTeammate):
	skill_id = 1010
	skill_rate = 1.54
	level_to_value = [0, 0, 0]

class GuanQia20(NeZa.NeZa):
	skill_id = 1011
	level_to_value = [0, 0, 0]

class GuanQia22(OneStarAuxiliaryHero.OneStarAuxiliaryHero):
	skill_id = 1012
	level_to_value = [0, 0, 0]

class GuanQia24(HealOneTeammate.HealOneTeammate):
	skill_id = 1013
	skill_rate = 2.57
	level_to_value = [0, 0, 0]

class GuanQia26(HealOneTeammate.HealOneTeammate):
	skill_id = 1014
	skill_rate = 1.6
	level_to_value = [0, 0, 0]

class GuanQia28(SelfDefendUp.SelfDefendUp):
	skill_id = 1015
	level_to_value = [0, 0, 0] 

class GuanQia29(HealOneTeammate.HealOneTeammate):
	skill_id = 1016
	skill_rate = 1.47
	level_to_value = [0, 0, 0]

class GuanQia30(ThreeStarDefendHero.ThreeStarDefendHero):
	skill_id = 1017
	skill_rate = 0.25
	level_to_value = [0, 0, 0]

class GuanQia32(AttackOneEnemy.AttackOneEnemy):
	skill_id = 1018
	skill_rate = 1.2
	level_to_value = [0, 0, 0]

class GuanQia34(TwoStarAttackHero.TwoStarAttackHero):
	skill_id = 1019
	level_to_value = [0, 0, 0]

class GuanQia35(HealOneTeammate.HealOneTeammate):
	skill_id = 1020
	skill_rate = 1.43
	level_to_value = [0, 0, 0]

class GuanQia38(ThreeStarAuxiliaryHero.ThreeStarAuxiliaryHero):
	skill_id = 1021
	skill_rate = 0.56
	level_to_value = [0, 0, 0]

class GuanQia39(HealOneTeammate.HealOneTeammate):
	skill_id = 1022
	skill_rate = 1.51
	level_to_value = [0, 0, 0]

class GuanQia41(AttackOneEnemy.AttackOneEnemy):
	skill_id = 1023
	skill_rate = 1.18
	level_to_value = [0, 0, 0]

class GuanQia42(ThreeStarAttackHeroA.ThreeStarAttackHeroA):
	skill_id = 1024
	skill_rate = 0.55
	level_to_value = [0, 0, 0]

class GuanQia46(FourStarAttackHeroA.FourStarAttackHeroA):
	skill_id = 1025
	skill_rate = 0.74
	level_to_value = [0, 0, 0]

class GuanQia51(AttackOneEnemy.AttackOneEnemy):
	skill_id = 1026
	skill_rate = 1.42
	level_to_value = [0, 0, 0]

class GuanQia52(AttackOneEnemy.AttackOneEnemy):
	skill_id = 1027
	skill_rate = 1.16
	level_to_value = [0, 0, 0]

class GuanQia53(AttackOneEnemy.AttackOneEnemy):
	skill_id = 1028
	skill_rate = 1.2
	level_to_value = [0, 0, 0]

class GuanQia54(AttackOneEnemy.AttackOneEnemy):
	skill_id = 1029
	skill_rate = 1.2
	level_to_value = [0, 0, 0]

class GuanQia55(AttackOneEnemy.AttackOneEnemy):
	skill_id = 1030
	skill_rate = 1.2
	level_to_value = [0, 0, 0]

class GuanQia56(ThreeStarAuxiliaryHero.ThreeStarAuxiliaryHero):
	skill_id = 1031
	skill_rate = 0.68
	level_to_value = [0, 0, 0]

class GuanQia62(FiveStarDefendHero.FiveStarDefendHero):
	skill_id = 1032
	skill_rate = 0.31
	level_to_value = [0, 0, 0]

class XinMo1(HealOneTeammate.HealOneTeammate):
	skill_id = 1033
	skill_rate = 9
	level_to_value = [0, 0, 0]

class MoYu1(OneStarDefendHero.OneStarDefendHero):
	skill_id = 1034
	level_to_value = [0, 0, 0]
	
	def do_effect(self, target):
		
		self.skill_value = self.level_to_hurt_value[self.argv]
		self.skill_rate = 1.0
		self.do_hurt(target)
		
		self.skill_value = self.level_to_treat_value[self.argv]
		self.skill_rate = 2.96
		self.do_treat(self.unit)

class MoYu2(OneStarAuxiliaryHero.OneStarAuxiliaryHero):
	skill_id = 1035
	skill_rate = 0.25
	level_to_value = [0, 0, 0]

class MoYu3(TwoStarAuxiliaryHero.TwoStarAuxiliaryHero):
	skill_id = 1036
	skill_rate = 2.37
	level_to_value = [0, 0, 0]

class MoYu4(ThreeStarDefendHero.ThreeStarDefendHero):
	skill_id = 1037
	skill_rate = 0.19
	level_to_value = [0, 0, 0]

class MoYu5(OneStarAttackHero.OneStarAttackHero):
	skill_id = 1038
	skill_rate = 0.49
	level_to_value = [0, 0, 0]

class MoYu6(TwoStarAttackHero.TwoStarAttackHero):
	skill_id = 1039
	skill_rate = 0.52
	level_to_value = [0, 0, 0]

class MoYu7(ThreeStarAuxiliaryHero.ThreeStarAuxiliaryHero):
	skill_id = 1040
	skill_rate = 0.58
	level_to_value = [0, 0, 0]

class MoYu8(FourStarDefendHero.FourStarDefendHero):
	skill_id = 1041
	level_to_value = [0, 0, 0]
	
	def do_effect(self, target):
		
		self.skill_value = self.level_to_hurt_value[self.argv]
		self.skill_rate = 1.0
		self.do_hurt(target)
		
		self.skill_value = self.level_to_treat_value[self.argv]
		self.skill_rate = 2.22
		self.do_treat(self.unit)
		
		#攻击后单位自身获得一个提升防御的BUFF
		self.unit.create_buff("AddDefend", 3, 500)

class MoYu9(FourStarAuxiliaryHero.FourStarAuxiliaryHero):
	skill_id = 1042
	skill_rate = 0.76
	level_to_value = [0, 0, 0]
	
	def do_effect(self, target):
		self.do_treat(target)
		argv = int(0.3 * self.unit.attack + self.skill_value)
		target.create_buff("HealthPerRound", 2, argv)

class MoYu10(ThreeStarAttackHeroA.ThreeStarAttackHeroA):
	skill_id = 1043
	skill_rate = 0.375
	level_to_value = [0, 0, 0]

class MoYu11(TwoStarDefendHero.TwoStarDefendHero):
	skill_id = 1044
	skill_rate = 2.5
	level_to_value = [0, 0, 0]

class MoYu12(ThreeStarAuxiliaryHero.ThreeStarAuxiliaryHero):
	skill_id = 1045
	skill_rate = 0.84
	level_to_value = [0, 0, 0]

class MoYu13(FourStarAuxiliaryHero.FourStarAuxiliaryHero):
	skill_id = 1046
	skill_rate = 0.5
	level_to_value = [0, 0, 0]

class MoYu14(FiveStarDefendHero.FiveStarDefendHero):
	skill_id = 1047
	skill_rate = 0.63
	level_to_value = [0, 0, 0]

class MoYu15(ThreeStarAttackHeroB.ThreeStarAttackHeroB):
	skill_id = 1048
	skill_rate = 2.0
	level_to_value = [0, 0, 0]

class MoYu16(FiveStarAuxiliaryHero.FiveStarAuxiliaryHero):
	skill_id = 1049
	skill_rate = 0.36
	level_to_value = [0, 0, 0]

class MoYu17(FourStarAttackHeroB.FourStarAttackHeroB):
	skill_id = 1050
	skill_rate = 0.935
	level_to_value = [0, 0, 0]

class MoYu18(ThreeStarAttackHeroA.ThreeStarAttackHeroA):
	skill_id = 1051
	skill_rate = 0.728
	level_to_value = [0, 0, 0]

class MoYu19(FourStarAttackHeroA.FourStarAttackHeroA):
	skill_id = 1052
	skill_rate = 0.936
	level_to_value = [0, 0, 0]

class MoYu20(FiveStarAttackHero.FiveStarAttackHero):
	skill_id = 1053
	skill_rate = 1.05
	level_to_value = [0, 0, 0]
	

class kaifu1(SixStarAttackHeroA.SixStarAttackHeroA):
	skill_id = 1100
	skill_rate = 0.8
	level_to_value = [0, 0, 0]

class kaifu2(SixStarAttackHeroB.SixStarAttackHeroB):
	skill_id = 1101
	skill_rate = 1.0
	level_to_value = [0, 0, 0]

class kaifu3(SixStarDefendHero.SixStarDefendHero):
	skill_id = 1102
	skill_rate = 0.86
	level_to_value = [0, 0, 0]

class kaifu4(SixStarAuxiliaryHero.SixStarAuxiliaryHero):
	skill_id = 1103
	skill_rate = 1.8
	level_to_value = [0, 0, 0]

class kaifu5(FiveStarAuxiliaryHero.FiveStarAuxiliaryHero):
	skill_id = 1104
	skill_rate = 0.25
	level_to_value = [0, 0, 0]



if "_HasLoad" not in dir():
	GuanQia2.reg()
	GuanQia4.reg()
	GuanQia6.reg()
	GuanQia8.reg()
	GuanQia12.reg()
	GuanQia14.reg()
	GuanQia16.reg()
	GuanQia17.reg()
	GuanQia18.reg()
	GuanQia19.reg()
	GuanQia20.reg()
	GuanQia22.reg()
	GuanQia24.reg()
	GuanQia26.reg()
	GuanQia28.reg()
	GuanQia29.reg()
	GuanQia30.reg()
	GuanQia32.reg()
	GuanQia34.reg()
	GuanQia35.reg()
	GuanQia38.reg()
	GuanQia39.reg()
	GuanQia41.reg()
	GuanQia42.reg()
	GuanQia46.reg()
	GuanQia51.reg()
	GuanQia52.reg()
	GuanQia53.reg()
	GuanQia54.reg()
	GuanQia55.reg()
	GuanQia56.reg()
	GuanQia62.reg()
	XinMo1.reg()
	MoYu1.reg()
	MoYu2.reg()
	MoYu3.reg()
	MoYu4.reg()
	MoYu5.reg()
	MoYu6.reg()
	MoYu7.reg()
	MoYu8.reg()
	MoYu9.reg()
	MoYu10.reg()
	MoYu11.reg()
	MoYu12.reg()
	MoYu13.reg()
	MoYu14.reg()
	MoYu15.reg()
	MoYu16.reg()
	MoYu17.reg()
	MoYu18.reg()
	MoYu19.reg()
	MoYu20.reg()
	kaifu1.reg()
	kaifu2.reg()
	kaifu3.reg()
	kaifu4.reg()
	kaifu5.reg()
