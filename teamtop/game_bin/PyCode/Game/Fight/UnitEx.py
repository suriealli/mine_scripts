#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.UnitEx")
#===============================================================================
# 战斗单位
#===============================================================================
import Environment
from Game.Fight import UnitBase, Operate, Middle
from Game.StarGirl import StarGirlConfig

class MainUnit(UnitBase.UnitBase):
	unit_type = 1
	run_create = Operate.CreateMainUnit
	def __init__(self, pos, camp, data):
		self.role_id = data[Middle.RoleID]
		self.cur_skill = None
		self.active_skills = []
		UnitBase.UnitBase.__init__(self, pos, camp, data)
		# 主角都是使用物攻
		self.attack = self.attack_p
		# 有可能需要指定士气
		if camp.moral_dict:
			self.moral = max(self.moral, camp.moral_dict.get(self.role_id, 0))
		# 构建主动技能
		ACTIVE_SKILL_APPEND = self.active_skills.append
		NEW_ACTIVE_SKILL = self.new_active_skill
		if self.fight.group:
			if Environment.EnvIsNA() and self.fight.group == 1:
				active_skills = data.get(Middle.GActiveSkills, [])
			else:
				active_skills = data[Middle.ActiveSkills]
		else:
			active_skills = data[Middle.ActiveSkills]
		for info in active_skills:
			ACTIVE_SKILL_APPEND(NEW_ACTIVE_SKILL(*info))
		# 标记是否在线
		self.is_online = data[Middle.IsOnline]
		# 标记操作单位
		self.control_role_id = data[Middle.ControlRoleID]
		# 标记上次选择技能的回合
		self.select_skill_round = -1
		self.fight.on_main_unit_create(self)
	
	def get_unit_info(self, ope = Operate.MainUnit):
		DATA = self.data
		role_name = DATA[Middle.RoleName]
		sex = DATA[Middle.Sex]
		grade = DATA[Middle.Grade]
		if self.fight.group:
			if Environment.EnvIsNA() and self.fight.group == 1:
				active_skills = DATA.get(Middle.GActiveSkills, [])
			else:
				active_skills = DATA[Middle.ActiveSkills]
		else:
			active_skills = DATA[Middle.ActiveSkills]
		mountEvolve_id = DATA[Middle.MountEvolveID]
		mount_id = DATA.get(Middle.MountID, 0)
		monut_property = DATA[Middle.MountProperty]
		help_station = DATA[Middle.HelpStation]
		help_station_property = DATA[Middle.HelpStationProperty]
		buff_info = self.get_buff_info()
		wingId = DATA[Middle.WingID]
		petType = DATA.get(Middle.PetType, 0)
		gCareer = DATA.get(Middle.GCareer, 0)
		fashionClothes = DATA.get(Middle.FashionClothes, 0)
		fashionHat = DATA.get(Middle.FashionHat, 0)
		fashionWeapons = DATA.get(Middle.FashionWeapons, 0)
		fashionState = DATA.get(Middle.FashionState, 0)
		dragon_train_property = DATA.get(Middle.DragonTrainProperty, {})
		title_role_property = DATA.get(Middle.TitleProperty_Role, {})
		title_team_property = DATA.get(Middle.TitleProperty_Team, {})
		return (ope, self.key, self.pos, self.role_id, role_name, self.level, sex, self.career, grade, 
				self.hp, self.max_hp, self.moral, self.max_moral, self.control_role_id, active_skills, 
				buff_info, mountEvolve_id, monut_property, help_station, help_station_property, wingId, petType, 
				gCareer, fashionClothes, fashionHat, fashionWeapons, fashionState, dragon_train_property, mount_id, title_role_property, title_team_property)
	
	def create(self, ope = Operate.MainUnit):
		self.fight.play_info.append(self.get_unit_info(ope))
	
	def do_shot(self):
		self.auto_select_active_skill()
		CUR_SKILL = self.cur_skill
		self.cur_skill = None
		if not CUR_SKILL:
			return
		if not CUR_SKILL.can_do():
			return
		CUR_SKILL.do()
		
		if self.fight.group == 2:
			for pos, unit in self.fight.left_camp.pos_units.iteritems():
				if pos == self.pos:
					continue
				unit.change_moral(4)
		
	
	def select_active_skill(self, idx):
		self.select_skill_round = self.fight.round
		if idx < 0:
			pass
		elif idx < len(self.active_skills):
			self.cur_skill = self.active_skills[idx]
		else:
			print "GE_EXC, error idx(%s) select_active_skill" % (idx)
	
	def auto_select_active_skill(self):
		if self.cur_skill and self.cur_skill.can_do():
			return
		max_mornal = -1;
		max_skill = None
		TARGET_CNT = len(self.other_camp.pos_units)
		for skill in self.active_skills:
			if skill.is_aoe and TARGET_CNT < skill.aoe_need_target_cnt:
				continue
			if not skill.can_do():
				continue
			if skill.need_moral < max_mornal:
				continue
			max_mornal = skill.need_moral
			max_skill = skill
		self.cur_skill = max_skill
	
	def leave_fight(self):
		# 释放操作单位
		self.fight.on_main_unit_leave(self)
		# 离开战斗
		UnitBase.UnitBase.leave_fight(self)
		# 头像
		head_portrait = self.camp.head_portrait.get(self.role_id)
		if head_portrait:
			head_portrait[4] = True
	
	def save_hp(self):
		# 保存血量士气
		CAMP = self.camp
		if CAMP.hp_dict is not None:
			#Hp1*(Hp2/(Hp1*(1+n)))
			CAMP.hp_dict[self.role_id] = int(self.temp_init_hp * (self.hp / (self.temp_init_hp * (1.0 + max(self.temp_hp_coef, 0)))))
		# 需要本方胜利才保存士气
		if self.fight.only_win_save_moral:
			RESULT = self.fight.result
			if CAMP.moral_dict is not None and RESULT is not None and RESULT * CAMP.mirror > 0:
				CAMP.moral_dict[self.role_id] = self.moral
		else:
			if CAMP.moral_dict is not None:
				CAMP.moral_dict[self.role_id] = self.moral
	
	def get_all_active_skill(self):
		return self.active_skills
	
	def revive(self, hp_rate):
		if self.pos in self.camp.pos_units:
			return None
		# 创建单位
		self.camp.pos_units[self.pos] = main_unit = self.__class__(self.pos, self.camp, self.data)
		# 还原参数
		main_unit.append_round_revive_cnt = self.append_round_revive_cnt
		main_unit.append_skill_revive_cnt = self.append_skill_revive_cnt
		main_unit.revive_status = self.revive_status
		# 重置血量，这里要兼容百分比和绝对值得问题
		if type(hp_rate) is float and hp_rate <= 1.0:
			main_unit.hp = int(main_unit.max_hp * hp_rate)
		else:
			main_unit.hp = min(main_unit.max_hp, int(hp_rate))
		# 修正英雄对角色的绑定
		for unit in self.camp.pos_units.itervalues():
			if unit.unit_type == 2 and unit.main_unit is self:
				unit.main_unit = main_unit
		for unit in self.camp.round_revives.iterkeys():
			if unit.unit_type == 2 and unit.main_unit is self:
				unit.main_unit = main_unit
		for unit in self.camp.skill_revives:
			if unit.unit_type == 2 and unit.main_unit is self:
				unit.main_unit = main_unit
		main_unit.create()
		return main_unit

class HeroUnit(UnitBase.UnitBase):
	unit_type = 2
	run_create = Operate.CreateHeroUnit
	def __init__(self, pos, camp, data, main_unit):
		self.role_id = data[Middle.RoleID]
		self.hero_type = data[Middle.HeroType]
		self.petType = data.get(Middle.PetType, 0)
		self.main_unit = main_unit
		UnitBase.UnitBase.__init__(self, pos, camp, data)
		# 构建主动技能
		self.normal_skill = self.new_active_skill(*data[Middle.NormalSkill])
		#=======================================================================
		# 2015年3月9日增加了英雄的主动技能个数，在这里还要兼容下缓存的战斗数据和新旧配表
		# self.active_skill = self.new_active_skill(*data[Middle.ActiveSkill])
		#=======================================================================
		self.active_skills = ACTIVE_SKILLS = []
		NEW_ACTIVE_SKILL = self.new_active_skill
		ACTIVE_SKILL_INFO = data[Middle.ActiveSkill]
		# 兼容缓存的战斗数据
		if type(ACTIVE_SKILL_INFO) is tuple:
			ACTIVE_SKILLS.append(NEW_ACTIVE_SKILL(*ACTIVE_SKILL_INFO))
		# 构造新的主动技能列表
		else:
			for skill_info in ACTIVE_SKILL_INFO:
				ACTIVE_SKILLS.append(NEW_ACTIVE_SKILL(*skill_info))
	
	def get_unit_info(self, ope = Operate.HeroUnit):
		return (ope, self.key, self.pos, self.role_id, self.hero_type, self.level, self.hp, self.max_hp, self.get_buff_info(), self.petType)
	
	def create(self, ope = Operate.HeroUnit):
		self.fight.play_info.append(self.get_unit_info(ope))
	
	def do_shot(self):
		if self.is_out:
			return
		if self.stun:
			return
		self.do_skill()
		# 英雄出手，给主角加4点士气
		if self.main_unit:
			self.main_unit.change_moral(4)
	
	def do_skill(self):
		#=======================================================================
		# ACTIVE_SKILL = self.active_skill
		# NORMAL_SKILL = self.normal_skill
		# # 不能释放，则普攻
		# if not ACTIVE_SKILL.can_do():
		#	NORMAL_SKILL.do()
		#	return
		# # AOE特殊处理
		# if ACTIVE_SKILL.is_aoe:
		#	if not ACTIVE_SKILL.has_buff and len(self.other_camp.pos_units) < 2:
		#		NORMAL_SKILL.do()
		#	else:
		#		ACTIVE_SKILL.do()
		#	return
		# # 治疗特殊处理
		# if ACTIVE_SKILL.is_treat:
		#	if ACTIVE_SKILL.need_treat():
		#		ACTIVE_SKILL.do()
		#	else:
		#		NORMAL_SKILL.do()
		#	return
		# # 释放主动技能
		# ACTIVE_SKILL.do()
		# 这上面是旧的技能释放规则，因为将英雄的主动技能变为多个，下面是新的技能释放规则
		#=======================================================================
		for active_skill in self.active_skills:
			# 不能释放
			if not active_skill.can_do():
				continue
			# 不带buff的AOE在对方少于2人的情况下不释放
			if active_skill.is_aoe and (not active_skill.has_buff) and len(self.other_camp.pos_units) < active_skill.aoe_need_target_cnt:
				continue
			# 治疗技能在不需要治疗的时候不释放
			if active_skill.is_treat and (not active_skill.need_treat()):
				continue
			# 释放主动技能
			active_skill.do()
			return
		# 释放普攻
		self.normal_skill.do()
	
	def save_hp(self):
		# 保存血量
		CAMP = self.camp
		if CAMP.hp_dict is not None:
			CAMP.hp_dict[self.hero_type] = int(self.temp_init_hp * (self.hp / (self.temp_init_hp * (1.0 + max(self.temp_hp_coef, 0)))))
	
	def get_all_active_skill(self):
		skills = [self.normal_skill]
		skills.extend(self.active_skills)
		return skills
	
	def revive(self, hp_rate):
		if self.pos in self.camp.pos_units:
			return None
		# 创建单位
		self.camp.pos_units[self.pos] = hero_unit = self.__class__(self.pos, self.camp, self.data, self.main_unit)
		# 还原参数
		hero_unit.append_round_revive_cnt = self.append_round_revive_cnt
		hero_unit.append_skill_revive_cnt = self.append_skill_revive_cnt
		hero_unit.revive_status = self.revive_status
		# 重置血量，这里要兼容百分比和绝对值得问题
		if type(hp_rate) is float and hp_rate <= 1.0:
			hero_unit.hp = int(hero_unit.max_hp * hp_rate)
		else:
			hero_unit.hp = min(hero_unit.max_hp, int(hp_rate))
		hero_unit.create()
		return hero_unit

class MonsterUnit(UnitBase.UnitBase):
	unit_type = 3
	run_create = Operate.CreateMonsterUnit
	def __init__(self, pos, camp, data):
		self.monster_id = data[Middle.MonsterID]
		UnitBase.UnitBase.__init__(self, pos, camp, data)
		# 构建主动技能
		self.normal_skill = self.new_active_skill(*data[Middle.NormalSkill])
		self.active_skill = self.new_active_skill(*data[Middle.ActiveSkill])
	
	def get_unit_info(self, ope = Operate.MonsterUnit):
		return (ope, self.key, self.pos, self.monster_id, self.level, self.hp, self.max_hp, self.get_buff_info())
	
	def create(self, ope = Operate.MonsterUnit):
		self.fight.play_info.append(self.get_unit_info(ope))
	
	def do_shot(self):
		ACTIVE_SKILL = self.active_skill
		NORMAL_SKILL = self.normal_skill
		if ACTIVE_SKILL.can_do():
			if ACTIVE_SKILL.is_aoe \
			and (not ACTIVE_SKILL.has_buff) \
			and len(self.other_camp.pos_units) < ACTIVE_SKILL.aoe_need_target_cnt:
				if NORMAL_SKILL.can_do():
					NORMAL_SKILL.do()
			else:
				ACTIVE_SKILL.do()
		else:
			if NORMAL_SKILL.can_do():
				NORMAL_SKILL.do()
	
	def save_hp(self):
		# 保存血量
		CAMP = self.camp
		if CAMP.hp_dict is not None:
			CAMP.hp_dict[self.pos] = self.hp
	
	def get_all_active_skill(self):
		return [self.normal_skill, self.active_skill]

class StarGirlUnit(UnitBase.UnitBase):
	unit_type = 4
	run_create = Operate.CreateStarGirlUnit
	def __init__(self, pos, camp, data, role_id, control_role_id):
		self.star_girl_id = data[Middle.StarGirlID]
		self.star_girl_star_level = data[Middle.StarGirlStarLevel]
		self.star_girl_skill_rate = 0
		self.set_skill_rate()
		UnitBase.UnitBase.__init__(self, pos, camp, data)
		self.role_id = role_id
		self.control_role_id = control_role_id
		self.active_skill = self.new_active_skill(*data[Middle.ActiveSkill])
		
	def create(self, ope = Operate.StarGirlUnit):
		self.fight.play_info.append(self.get_unit_info(ope))
	
	def get_unit_info(self, ope = Operate.StarGirlUnit):
		star_girl_grade = self.data[Middle.StarGirlGrade]
		return (ope, self.key, self.pos, self.level, self.hp, self.max_hp, self.star_girl_id, star_girl_grade, self.moral, self.role_id, self.star_girl_star_level, self.control_role_id)
	
	def do_shot(self):
		if self.is_out:
			return
		if not self.active_skill.can_do():
			return
		self.active_skill.do()
	
	def leave_fight(self):
		self.hp = 0
		self.is_out = True
		del self.camp.vpos_units[self.pos]
		self.fight.play_info.append((Operate.Leave, self.key))
		self.unload_event()
	
	
	def set_skill_rate(self):
		girlcfg = StarGirlConfig.STAR_LEVEL.get((self.star_girl_id, self.star_girl_star_level))
		if not girlcfg:
			print "GE_EXC, set_skill_rate not this girlcfg (%s, %s)" % (self.star_girl_id, self.star_girl_star_level)
			return
		#根据星灵ID和星级设置主动技能系数
		self.star_girl_skill_rate = girlcfg.skill_rate / 10000.0
	
