#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.UnitBase")
#===============================================================================
# 战斗单位基本
#===============================================================================
import random
import Environment
from Util import Trace
from Game.Fight import Handle, Operate, Middle, SkillBase, BuffBase

# 防御比参数
DEFENCE_A = 0.2
DEFENCE_B = 2
DEFENCE_C = 0.01

if "_HasLoad" not in dir():
	PassiveSkills = {}
	Buffs = {}

class UnitBase(Handle.Handle):
	unit_type = 0
	run_create = 0
	def __init__(self, pos, camp, data):
		Handle.Handle.__init__(self)
		# 战场数据
		self.pos = pos
		self.camp = camp
		self.other_camp = camp.other_camp
		self.fight = camp.fight
		self.key = self.fight.allot_key()
		self.is_out = False
		# Buff
		self.normal_buffs = set()
		self.state_buffs = {}
		# 技能
		self.passive_skills = []
		# 创建回合
		self.create_round = self.fight.round
		# 数据
		self.data = data
		# 眩晕状态
		self.stun = 0
		#免疫晕眩
		self.wushistun = 0
		# 复活次数
		self.append_round_revive_cnt = 0
		self.append_skill_revive_cnt = 0
		# 复活要继承的状态
		self.revive_status = {}
		# 战斗数值
		self.level = data[Middle.Level]
		self.career = data[Middle.Career]
		self.hp = self.max_hp = data[Middle.MaxHP]
		self.temp_init_hp = self.hp#初始血量
		self.temp_hp_coef = 0	#血量改变百分比
		self.moral = data.get(Middle.Morale, 0)
		self.max_moral = 100
		self.total_hurt = 0
		# 速度是以100为最小单位投的，这里将战斗位置换算成速度。
		self.speed = data[Middle.Speed] + 100 - abs(pos)
		self.attack_p = data[Middle.AttackP]
		self.attack_m = data[Middle.AttackM]
		self.attack = self.attack_p if self.career == 1 else self.attack_m
		self.defence_p = data[Middle.DefenceP]
		self.defence_m = data[Middle.DefenceM]
		self.crit = data[Middle.Crit]
		self.crit_press = data[Middle.CritPress]
		self.anti_broken = data[Middle.AntiBroken]
		self.not_broken = data[Middle.NotBroken]
		self.parry = data[Middle.Parry]
		self.puncture = data[Middle.Puncture]
		self.crit_rate = 0.0
		self.crit_press_rate = 0.0
		self.anti_broken_rate = 0.0
		self.not_broken_rate = 0.0
		self.parry_rate = 0.0
		self.puncture_rate = 0.0
		self.damage_upgrade_rate = float(data[Middle.DamageUpgrade]) / 10000
		self.damage_reduce_rate = float(data[Middle.DamageReduce]) / 10000
		self.treat_rate = 0.0			#治疗效果提升
		self.parry_hurt = 0.66			#格挡伤害剩余
		self.defence_stun_rate = 0		#抗眩晕率【百分比】
		self.temp_damage_reduce_rate = 0.0#临时减伤
		
		# 构建被动技能
		NEW_PASSIVE_SKILL = self.new_passive_skill
		if self.fight.group:
			if Environment.EnvIsNA() and self.fight.group == 1:
				passive_skills = data.get(Middle.GPassiveSkills, [])
			else:
				passive_skills = data[Middle.PassiveSkills]
		else:
			passive_skills = data[Middle.PassiveSkills]
		for info in passive_skills:
			# 有可能将战斗外加属性的被动技能也写进来了
			if info[0] in SkillBase.PASSIVE_SKILLS:
				NEW_PASSIVE_SKILL(*info)
	
	def try_trigger(self):
		return self.fight.try_trigger()
	
	def get_buff_info(self):
		info = []
		for buff in self.normal_buffs:
			info.append((buff.key, buff.buff_id, buff.life))
		for buff in self.state_buffs.itervalues():
			info.append((buff.key, buff.buff_id, buff.life))
		return info
	
	def compute_defence_rate(self, source_career):
		defence = self.defence_p if source_career == 1 else self.defence_m
		if defence <= 0:
			return 0
		else:
			# a/(防守者等级^b/防御+1)+c 
			return DEFENCE_A / (float(self.level ** DEFENCE_B) / defence + 1) + DEFENCE_C
	
	def create_buff(self, buff_id, life, argv):
		if self.is_out: return
		buff = BuffBase.BUFFS[buff_id](self, life, argv)
		return buff
	
	def create_stun(self, rate, life, argv=None):
		if self.wushistun:
			return None
		if random.randint(0, 99) < rate - self.defence_stun_rate:
			return self.create_buff("Stun", life, argv)
		else:
			return None
	
	def clear_buff(self, buff_info = None):
		'''
		清除Buff
		@param buff_info:None:清除所有Buff;True:清除增益Buff;False:清除减益Buff;
						BuffName:清除一个指定名字的状态Buff;
		'''
		if self.is_out: return
		if buff_info is None:
			for buff in tuple(self.normal_buffs):
				buff.dec_life(buff.life)
			for buff in self.state_buffs.values():
				buff.dec_life(buff.life)
		elif buff_info is True:
			for buff in tuple(self.normal_buffs):
				if buff.is_benefit is True:
					buff.dec_life(buff.life)
			for buff in self.state_buffs.values():
				if buff.is_benefit is True:
					buff.dec_life(buff.life)
		elif buff_info is False:
			for buff in tuple(self.normal_buffs):
				if buff.is_benefit is False:
					buff.dec_life(buff.life)
			for buff in self.state_buffs.values():
				if buff.is_benefit is False:
					buff.dec_life(buff.life)
		else:
			for buff in tuple(self.normal_buffs):
				if buff.__class__.__name__ == buff_info:
					buff.dec_life(buff.life)
			buff = self.state_buffs.get(buff_info)
			if buff:
				buff.dec_life(buff.life)
	
	def new_active_skill(self, skill_id, argv):
		active_skill = SkillBase.ACTIVE_SKILLS[skill_id](self, argv)
		return active_skill
	
	def new_passive_skill(self, skill_id, argv):
		passive_skill = SkillBase.PASSIVE_SKILLS[skill_id](self, argv)
		return passive_skill
	
	def get_all_active_skill(self):
		return []
	
	def revive_at_next_round(self, hp_rate):
		# 已经回合复活过
		if self.append_round_revive_cnt:
			return
		# 没有复活函数
		if not hasattr(self, "revive"):
			return
		# 标记加入回合复活列表次数
		self.append_round_revive_cnt += 1
		# 如果被记录在技能复活列表中，要移除
		try:
			self.camp.skill_revives.remove(self)
		except:
			pass
		# 加入回合复活列表
		self.camp.round_revives[self] = float(hp_rate)
	
	def revive_by_trigger(self):
		# 如果在回合复活列表中，不能技能复活
		if self in self.camp.round_revives:
			return
		# 没有复活函数
		if not hasattr(self, "revive"):
			return
		# 标记加入技能复活列表次数
		self.append_skill_revive_cnt += 1
		# 加入技能复活列表
		self.camp.skill_revives.append(self)
	
	#===========================================================================
	# 进程战场
	#===========================================================================
	def join_fight(self):
		self.event_join(self)
		self.camp.event_join(self)
		self.fight.event_join(self)
	
	def leave_fight(self):
		del self.camp.pos_units[self.pos]
		self.fight.play_info.append((Operate.Leave, self.key))
		self.unload_event()
	
	def die(self, source = None):
		self.hp = 0
		self.is_out = True
		if source:
			source.event_has_kill(source, self)
			source.camp.event_has_kill(source, self)
			source.fight.event_has_kill(source, self)
		self.event_has_be_kill(source, self)
		self.camp.event_has_be_kill(source, self)
		self.fight.event_has_be_kill(source, self)
		self.save_hp()
		self.leave_fight()
		# 尝试保存可被复活
		self.revive_by_trigger()
	
	def unload_event(self):
		# 卸载被动技能
		for passive_skill in self.passive_skills:
			passive_skill.unload_event()
		# 卸载Buff
		for buff in tuple(self.normal_buffs):
			buff.del_from_unit(False)
		for buff in self.state_buffs.values():
			buff.del_from_unit(False)
	
	#===========================================================================
	# 属性改变函数
	#===========================================================================
	def change_hp(self, jap, source = None, operate = Operate.ChangeHP):
		# 出局或者死亡或者没有改变，直接返回
		if self.is_out or jap == 0: return
		number = jap
		if jap > 0:
			if self.hp + jap > self.max_hp:
				jap = self.max_hp - self.hp
				self.hp = self.max_hp
			else:
				self.hp += jap
		else:
			if self.hp + jap <= 0:
				jap = -self.hp
				self.hp = 0
			else:
				self.hp += jap
		self.fight.play_info.append((operate, self.key, jap, number))
		# 处理死亡
		if self.hp <= 0:
			self.die(source)
		else:
			self.has_change_hp(jap)
	
	def hurt(self, jap, source):
		# 出局或者死亡或者没有改变，直接返回
		if self.is_out or jap == 0: return
		if jap > 0:
			original_jap = jap
			jap = self.event_before_hurt(self, original_jap, jap)
			if jap > 0:
				self.change_hp(-jap, source, Operate.DoHurt)
		else:
			Trace.StackWarn("GE_EXC, hurt with error jap(%s)" % (jap))
	
	def treat(self, jap, source):
		if jap > 0:
			self.change_hp(jap, source, Operate.DoTreat)
		else:
			sw = "GE_EXC, treat with error jap(%s)" % (jap)
			Trace.StackWarn(sw)
	
	def change_max_hp(self, jap):
		# 出局或者死亡或者没有改变，直接返回
		if self.is_out or jap == 0: return
		if jap > 0:
			self.max_hp += jap
		else:
			self.max_hp += jap
			# 不能因为减少血上限，减到负数
			if self.max_hp <= 0:
				self.max_hp = 1
			# 血不能超过血上限
			if self.hp > self.max_hp:
				self.hp = self.max_hp
		self.fight.play_info.append((Operate.ChangeMaxHP, self.key, jap))
	
	def change_max_hp_coef(self, coef):
		if self.is_out or coef == 0: return
		self.temp_hp_coef += coef
		
	
	def change_moral(self, jap):
		# 出局或者死亡或者没有改变，直接返回
		if self.is_out or jap == 0: return
		moral = self.moral + jap
		if moral > self.max_moral:
			jap = self.max_moral - self.moral
			self.moral = self.max_moral
		elif moral < 0:
			jap = -self.moral
			self.moral = 0
		else:
			self.moral = moral
		if jap == 0: return
		self.fight.play_info.append((Operate.ChangeMoral, self.key, jap))
	
	def change_max_moral(self, jap):
		# 出局或者死亡或者没有改变，直接返回
		if self.is_out or jap == 0: return
		self.max_moral += jap
		self.fight.play_info.append((Operate.ChangeMaxMoral, self.key, jap))
	
	def change_attack(self, jap):
		# 出局或者死亡或者没有改变，直接返回
		if self.is_out or jap == 0: return
		self.attack += jap
		self.fight.play_info.append((Operate.ChangeAttack, self.key, jap))
	
	def change_defence(self, jap):
		# 出局或者死亡或者没有改变，直接返回
		if self.is_out or jap == 0: return
		self.defence_p += jap
		self.defence_m += jap
		self.fight.play_info.append((Operate.ChangeDefence, self.key, jap))
	
	#===========================================================================
	# 事件触发函数
	#===========================================================================
	def before_skill(self, skill):
		self.total_hurt = 0
		self.event_before_skill(self, skill)
		self.camp.event_before_skill(self, skill)
		self.fight.event_before_skill(self, skill)
	
	def after_skill(self, skill):
		self.event_after_skill(self, skill)
		self.camp.event_after_skill(self, skill)
		self.fight.event_after_skill(self, skill)
		self.total_hurt = 0
	
	def has_change_hp(self, jap):
		self.event_change_hp(self, jap)
		self.camp.event_change_hp(self, jap)
		self.fight.event_change_hp(self, jap)
	
	#===========================================================================
	# 选择单位函数
	#===========================================================================
	def select_all_member(self):
		return self.camp.get_all_units()
	
	def select_random_member_exclude_self(self, n):
		units = self.camp.pos_units.values()
		random.shuffle(units)
		l = []
		for unit in units:
			if unit is self:
				continue
			l.append(unit)
			if len(l) >= n:
				break
		return l
	
	def select_least_hp_member(self, n = 1):
		return self.camp.get_least_hp_units(n)
	
	def select_self(self):
		return [self]
	
	def select_all_enemy(self):
		return self.other_camp.get_all_units()
	
	def select_random_enemy(self, n = 1):
		return self.other_camp.get_random_units(n)
	
	def select_front_row_first_enemy(self):
		return self.other_camp.get_front_row_first_units()
	
	def select_back_row_first_enemy(self, n = 1):
		return self.other_camp.get_back_row_first_units(n)
	
	def select_cell_enemy(self):
		return self.other_camp.get_cell_units()
	
	def select_row_enemy(self):
		return self.other_camp.get_row_units()
	
