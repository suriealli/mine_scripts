#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Camp")
#===============================================================================
# 战斗阵营
#===============================================================================
import copy
import random
import traceback
from Util import Trace
from Game.Role import Status
from Game.Role.Data import EnumTempObj, EnumInt1
from Game.Fight import Handle, Middle, UnitEx, FightConfig, Operate

ROLE_POS_2_STAR_GIRL_POS = {1: 7, 2: 7, 3: 8, 4: 8, 5: 9, 6: 9,
						- 1:-7, -2:-7, -3:-8, -4:-8, -5:-9, -6:-9}

class Camp(Handle.Handle):
	def __init__(self, fight, mirror=1):
		Handle.Handle.__init__(self)
		self.fight = fight					#战场
		self.mirror = mirror				#镜像
		self.pos_units = {}					#位置-->战斗单位
		self.vpos_units = {}				#位置-->战斗单位【虚拟的位置，为星灵特殊做的】
		self.other_camp = None				#对面阵营
		self.roles = set()					#角色集
		self.wheels = []					#车轮战列表
		self.hp_dict = None					#保存血量
		self.moral_dict = None				#保存士气
		self.monster_wave = 0				#创建怪物的波数
		self.head_portrait = {}				#主角头像
		self.round_revives = {}				#复活列表【unit --> hp_rate回合开始主动触发复活】
		self.skill_revives = []				#复活列表【由技能触发复活】
	
	def try_trigger(self):
		return self.fight.try_trigger()
	
	#===========================================================================
	# 创建单位
	#===========================================================================
	def create_online_role_unit(self, role, control_role_id=0, fightData=None, use_px=False, team_pos_index=0, role_realfight_pos= -1, use_property_H=False):
		#强制进入战斗状态
		Status.ForceInStatus(role, EnumInt1.ST_FightStatus)
		if fightData is None:
			datas = Middle.GetRoleData(role, use_px, team_pos_index, role_realfight_pos, use_property_H)
		else:
			datas = copy.deepcopy(fightData)
		# 强行修正控制角色ID、在线情况
		role_data = datas[0]
		role_data[Middle.ControlRoleID] = control_role_id
		role_data[Middle.IsOnline] = True if control_role_id else False
		# 头像列表
		role_id = role_data[Middle.RoleID]
		role_name = role_data[Middle.RoleName]
		sex = role_data[Middle.Sex]
		career = role_data[Middle.Career]
		grade = role_data[Middle.Grade]
		fight_index = len(self.head_portrait)
		warStation_id = role_data.get(Middle.WarStationID, 0)
		stationSoulId = role_data.get(Middle.StationSoulID, 0)
		self.head_portrait[role_id] = [role_name, sex, career, grade, False, fight_index, warStation_id, stationSoulId]
		# 非组队战斗并且已经有战斗单位，车轮战
		if (not self.fight.group) and self.pos_units:
			self.wheels.append(datas)
		else:
			self.real_create_role_hero_unit(datas)
		# 相互绑定
		role.SetTempObj(EnumTempObj.FightCamp, self)
		self.roles.add(role)
	
	def create_outline_role_unit(self, datas, control_role_id=0):
		# 强行修正控制角色ID、在线情况
		# 深拷贝一份，1，防止修改了外部数据， 2 防止外部数据修改了影响到战斗内的缓存数据
		datas = copy.deepcopy(datas)
		role_data = datas[0]
		role_data[Middle.ControlRoleID] = control_role_id
		role_data[Middle.IsOnline] = True if control_role_id else False
		# 头像列表
		role_id = role_data[Middle.RoleID]
		role_name = role_data[Middle.RoleName]
		sex = role_data[Middle.Sex]
		career = role_data[Middle.Career]
		grade = role_data[Middle.Grade]
		fight_index = len(self.head_portrait)
		warStation_id = role_data.get(Middle.WarStationID, 0)
		stationSoulId = role_data.get(Middle.StationSoulID, 0)
		self.head_portrait[role_id] = [role_name, sex, career, grade, False, fight_index, warStation_id, stationSoulId]
		# 非组队战斗并且已经有战斗单位，车轮战
		if (not self.fight.group) and self.pos_units:
			self.wheels.append(datas)
		else:
			self.real_create_role_hero_unit(datas)
	
	def create_monster_camp_unit(self, mcid):
		if self.pos_units:
			self.wheels.append(mcid)
		else:
			self.real_create_monster_unit(mcid)
	
	def real_create_role_hero_unit(self, datas):
		try:
			# 加速优化
			POS_UNITS = self.pos_units
			MIRROR = self.mirror
			HERO_UNIT = UnitEx.HeroUnit
			# 如果保存角色血量为None，则不特殊处理角色血量
			role_data, hero_datas = datas
			# 组队战斗只上主角，并使用组队位置
			if self.fight.group:
				role_pos = role_data[Middle.GFightPos] * MIRROR
				#是否需要带英雄
				if self.fight.group_need_hero is False:
					hero_datas = {}
			else:
				role_pos = role_data[Middle.FightPos] * MIRROR
			# 按照是否恢复血量创建战斗单位
			if self.hp_dict is None:
				POS_UNITS[role_pos] = main_unit = UnitEx.MainUnit(role_pos, self, role_data)
				for hero_pos, hero_data in hero_datas.iteritems():
					hero_pos = hero_pos * MIRROR
					POS_UNITS[hero_pos] = HERO_UNIT(hero_pos, self, hero_data, main_unit)
			# 否则按照保存的血量来工作（这里涉及的一个血量为0不创建的问题，故要在创建之前确定血量）
			else:
				HP_DICT = self.hp_dict
				role_hp = HP_DICT.get(role_data[Middle.RoleID], role_data[Middle.MaxHP])
				if role_hp:
					POS_UNITS[role_pos] = main_unit = UnitEx.MainUnit(role_pos, self, role_data)
					main_unit.hp = min(main_unit.max_hp, role_hp)
					main_unit.temp_init_hp = main_unit.hp
				else:
					main_unit = None
				for hero_pos, hero_data in hero_datas.iteritems():
					hero_hp = HP_DICT.get(hero_data[Middle.HeroType], hero_data[Middle.MaxHP])
					if hero_hp:
						hero_pos = hero_pos * MIRROR
						POS_UNITS[hero_pos] = hero_unit = HERO_UNIT(hero_pos, self, hero_data, main_unit)
						hero_unit.hp = min(hero_unit.max_hp, hero_hp)
						hero_unit.temp_init_hp = hero_unit.hp
			# 星灵是不会保存血量的
			star_girl_data = role_data.get(Middle.StarGirlUnit)
			if star_girl_data is not None:
				star_girl_pos = ROLE_POS_2_STAR_GIRL_POS[role_pos]
				if star_girl_pos not in self.vpos_units:
					self.vpos_units[star_girl_pos] = UnitEx.StarGirlUnit(star_girl_pos, self, star_girl_data, role_data[Middle.RoleID], role_data[Middle.ControlRoleID])
		except:
			traceback.print_exc()
			Trace.StackWarn("camp create_role_hero_unit error.")
			self.fight.result = 0
			return None
	
	def real_create_monster_unit(self, mcid):
		try:
			mc = FightConfig.MONSTER_CAMP.get(mcid)
			if mc is None:
				print "GE_EXC, can't find monster camp(%s)." % mcid
				return
			POS_UNITS = self.pos_units
			MIRROR = self.mirror
			UNIT_MONSTERUNIT = UnitEx.MonsterUnit
			if self.hp_dict is None:
				for monster_pos, monster_data in mc.iteritems():
					monster_pos = monster_pos * MIRROR
					POS_UNITS[monster_pos] = UNIT_MONSTERUNIT(monster_pos, self, monster_data)
			else:
				HP_DICT = self.hp_dict
				for monster_pos, monster_data in mc.iteritems():
					monster_pos = monster_pos * MIRROR
					monster_hp = HP_DICT.get(monster_pos, monster_data[Middle.MaxHP])
					if monster_hp:
						POS_UNITS[monster_pos] = monster = UNIT_MONSTERUNIT(monster_pos, self, monster_data)
						monster.hp = monster_hp
			# 增加怪物波数计数
			self.monster_wave += 1
		except:
			traceback.print_exc()
			Trace.StackWarn("camp create_monster_unit error.")
			self.fight.result = 0
	
	def real_create_one_monster_unit(self, monster_pos, monster_id):
		# 智能纠正位置
		if self.mirror * monster_pos < 0:
			monster_pos = -monster_pos
		# 位置唯一
		if monster_pos in self.pos_units:
			print "GE_EXC, create_one_monster_unit pos(%s) repeat" % monster_pos
			return
		monster_data = FightConfig.MONSTER.get(monster_id)
		if monster_data is None:
			print "GE_EXC, create_one_monster_unit monster_id(%s) error" % monster_id
			return
		self.pos_units[monster_pos] = monster_unit = UnitEx.MonsterUnit(monster_pos, self, monster_data)
		return monster_unit
	
	def revive_unit(self, hp_rate):
		if not self.skill_revives:
			return
		unit = self.skill_revives.pop()
		revive_unit = unit.revive(hp_rate)
		if revive_unit is not None:
			revive_unit.join_fight()
	
	def try_revive(self):
		if not self.pos_units:
			return
		revive_units = []
		for unit, hp_rate in self.round_revives.iteritems():
			revive_units.append(unit.revive(hp_rate))
		for revive_unit in revive_units:
			if revive_unit is None:
				continue
			revive_unit.join_fight()
		self.round_revives = {}
	
	def try_wheel(self):
		if self.pos_units:
			return
		if not self.wheels:
			self.round_revives = {}
			return
		# 强制星灵离场
		self.try_star_girl_leave()
		# 强制清空复活列表
		self.round_revives = {}
		self.skill_revives = []
		# 车轮战
		unit_data = self.wheels.pop(0)
		if type(unit_data) is int:
			self.real_create_monster_unit(unit_data)
			# 右阵营才通知客户端怪物波数
			if self.mirror < 0:
				self.fight.play_info.append((Operate.MonsterWave, self.monster_wave, len(self.wheels)))
		else:
			self.real_create_role_hero_unit(unit_data)
		# 通知客户端创建并加入战场
		for unit in self.pos_units.itervalues():
			unit.create(unit.run_create)
		for unit in self.vpos_units.itervalues():
			unit.create(unit.run_create)
		# 通知客户端创建并加入战场
		for unit in self.pos_units.itervalues():
			unit.join_fight()
		for unit in self.vpos_units.itervalues():
			unit.join_fight()
	
	def try_star_girl_leave(self):
		if self.pos_units:
			return
		for unit in self.vpos_units.values():
			unit.leave_fight()
	
	#===========================================================================
	# 保存血量士气
	#===========================================================================
	def bind_hp(self, hp_dict):
		self.hp_dict = hp_dict
	
	def bind_moral(self, moral_dict):
		self.moral_dict = moral_dict
	
	def save_hp(self):
		if self.hp_dict is None and self.moral_dict is None:
			return
		
		for unit in self.pos_units.itervalues():
			unit.save_hp()
		
		total_hp = 0
		if self.hp_dict is not None:
			for key, hp in self.hp_dict.iteritems():
				if key == "total_hp":
					continue
				total_hp += hp
			self.hp_dict["total_hp"] = total_hp
	
	def get_total_hp(self):
		total_hp = 0
		for unit in self.pos_units.itervalues():
			total_hp += unit.hp
		return total_hp
	
	#===========================================================================
	# 选择单位
	#===========================================================================
	def get_all_units(self):
		return self.pos_units.values()
	
	def get_least_hp_units(self, n):
		units = self.pos_units.values()
		units.sort(key=lambda u:float(u.hp) / u.max_hp)
		return units[:n]
	
	def get_random_units(self, n):
		units = self.pos_units.values()
		random.shuffle(units)
		return units[:n]
	
	def get_front_row_first_units(self):
		l = []
		MIRROR = self.mirror
		POS_UNITS_GET = self.pos_units.get
		LAPPEND = l.append
		for pos in (1, 3, 5):
			unit = POS_UNITS_GET(pos * MIRROR)
			if unit is not None:
				LAPPEND(unit)
		if not l:
			for pos in (2, 4, 6):
				unit = POS_UNITS_GET(pos * MIRROR)
				if unit is not None:
					LAPPEND(unit)
		if not l:
			return []
		return [random.choice(l)]
	
	def get_back_row_first_units(self, n):
		l = []
		MIRROR = self.mirror
		POS_UNITS_GET = self.pos_units.get
		LAPPEND = l.append
		for pos in (2, 4, 6):
			unit = POS_UNITS_GET(pos * MIRROR)
			if unit is not None:
				LAPPEND(unit)
		if not l:
			for pos in (1, 3, 5):
				unit = POS_UNITS_GET(pos * MIRROR)
				if unit is not None:
					LAPPEND(unit)
		if not l:
			return []
		random.shuffle(l)
		return l[:n]
	
	def get_cell_units(self):
		unitss = []
		max_cell = 1
		MIRROR = self.mirror
		POS_UNITS_GET = self.pos_units.get
		for unit_poss in ((1, 2), (3, 4), (5, 6)):
			units = []
			for unit_pos in unit_poss:
				unit = POS_UNITS_GET(unit_pos * MIRROR)
				if unit is not None:
					units.append(unit)
			units_len = len(units)
			if units_len >= max_cell:
				unitss.append(units)
				max_cell = units_len
		if unitss:
			l = []
			for units in unitss:
				if len(units) == max_cell:
					l.append(units)
			return random.choice(l)
		else:
			return []
	
	def get_row_units(self):
		l = []
		MIRROR = self.mirror
		POS_UNITS_GET = self.pos_units.get
		LAPPEND = l.append
		for pos in (1, 3, 5):
			unit = POS_UNITS_GET(pos * MIRROR)
			if unit is not None:
				LAPPEND(unit)
		if not l:
			for pos in (2, 4, 6):
				unit = POS_UNITS_GET(pos * MIRROR)
				if unit is not None:
					LAPPEND(unit)
		return l
	
