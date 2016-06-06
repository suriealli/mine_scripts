#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.FightConfig")
#===============================================================================
# 战斗配置
#===============================================================================
import Environment
import DynamicPath
from Util.File import TabFile
from Game.Fight import Middle
from Game.Activity.HunluanSpace import HunluanSpaceConfig

FightFolder = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).AppendPath("Fight")

class FightConfig(TabFile.TabLine):
	FilePath = FightFolder.FilePath("Fight.txt")
	def __init__(self):
		self.fight_type = int
		self.pvp = self.GetBoolByString
		self.canJumpFight = self.GetBoolByString
		self.group = int
		self.viewFightType = self.GetIntByString


class MonsterConfig(TabFile.TabLine):
	FilePath = FightFolder.FilePath("Monster.txt")
	
	def __init__(self):
		self.monster_id = int
		self.level = int
		self.career = int
		self.max_hp = int
		self.speed = int
		self.attack_p = int
		self.attack_m = int
		self.defence_p = int
		self.defence_m = int
		self.crit = int
		self.crit_press = int
		self.anti_broken = int
		self.not_broken = int
		self.parry = int
		self.puncture = int
		self.damage_upgrade = int
		self.damage_reduce = int
		self.normal_skill = self.GetEvalByString
		self.active_skill = self.GetEvalByString
		self.passive_skills = self.GetEvalByString

class MonsterCampConfig(TabFile.TabLine):
	FilePath = FightFolder.FilePath("MonsterCamp.txt")
	
	def __init__(self):
		self.monster_camp_id = int
		self.pos1 = self.GetIntByString
		self.pos2 = self.GetIntByString
		self.pos3 = self.GetIntByString
		self.pos4 = self.GetIntByString
		self.pos5 = self.GetIntByString
		self.pos6 = self.GetIntByString

def LoadAllConfig():
	for f in FightConfig.ToClassType():
		if f.fight_type in FIGHT_TYPES:
			print "GE_EXC, repeat fight type(%s)" % f.fight_type
		FIGHT_TYPES[f.fight_type] = f
	for m in MonsterConfig.ToClassType():
		if m.monster_id in MONSTER:
			print "GE_EXC, repeat monster(%s)" % m.monster_id
		MONSTER[m.monster_id] = {Middle.MonsterID:m.monster_id,
								Middle.Level: m.level,
								Middle.Career: m.career,
								Middle.MaxHP: m.max_hp,
								Middle.Speed: m.speed,
								Middle.AttackP: m.attack_p,
								Middle.AttackM: m.attack_m,
								Middle.DefenceP: m.defence_p,
								Middle.DefenceM: m.defence_m,
								Middle.Crit: m.crit,
								Middle.CritPress: m.crit_press,
								Middle.AntiBroken: m.anti_broken,
								Middle.NotBroken: m.not_broken,
								Middle.Parry: m.parry,
								Middle.Puncture: m.puncture,
								Middle.DamageUpgrade: m.damage_upgrade,
								Middle.DamageReduce: m.damage_reduce,
								Middle.NormalSkill: m.normal_skill,
								Middle.ActiveSkill: m.active_skill,
								Middle.PassiveSkills: m.passive_skills,
								}
	for mc in MonsterCampConfig.ToClassType():
		if mc.monster_camp_id in MONSTER_CAMP:
			print "GE_EXC, repeat monster camp(%s)" % mc.monster_camp_id
		MONSTER_CAMP[mc.monster_camp_id] = d = {}
		for pos in xrange(1, 7):
			monster_id = getattr(mc, "pos%s" % pos)
			if not monster_id:
				continue
			monster_data = MONSTER.get(monster_id)
			if monster_data is None:
				print "GE_EXC, can't find monster(%s)" % monster_id
			d[pos] = monster_data

def CalHunluanSpace():
	#读取混乱时空配置的怪物阵营中的怪物最大血量
	global HSMONSTER_HP_DICT
	
	for campID in HunluanSpaceConfig.MonsterCampIDSet:
		campData = MONSTER_CAMP.get(campID)
		if not campData:
			print 'GE_EXC, CalHunluanSpace can not find camp id %s' % campID
			continue
		#位置写死是4
		monsterID = campData[4].get(Middle.MonsterID)
		if not monsterID:
			print 'GE_EXC, CalHunluanSpace can not find monste id %s' % monsterID
			continue
		monsterData = MONSTER.get(monsterID)
		if not monsterData:
			print 'GE_EXC, CalHunluanSpace can not find monste data %s' % monsterID
			continue
		HSMONSTER_HP_DICT[campID] = monsterData.get(Middle.MaxHP)
	
if "_HasLoad" not in dir():
	FIGHT_TYPES = {}
	MONSTER = {}
	MONSTER_CAMP = {}
	HSMONSTER_HP_DICT = {}			#混乱时空血量字典 {阵营ID --> monster血量}
	
	if Environment.HasLogic:
		LoadAllConfig()
		#注意下面这两个配置表的导入是有先后顺序的(检测配表)
		HunluanSpaceConfig.LoadHunluanDevil()
		HunluanSpaceConfig.LoadHunluanDemon()
		HunluanSpaceConfig.LoadHunluanDevilBoss()
		CalHunluanSpace()
		
