#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.SkillBase")
#===============================================================================
# 技能基本
#===============================================================================
import random
from Game.Fight import Operate

# 破击参数
BROKEN_A = 1.0
BROKEN_B = 15000.0
BROKEN_C = 0.02
# 暴击参数
CRIT_A = 1.0
CRIT_B = 15000.0
CRIT_C = 0.02
# 格挡参数
PARRY_A = 1.0
PARRY_B = 15000.0
PARRY_C = 0.02

#暴击，破档，破防减去免爆，格挡，免破小于下面的值时，不产生效果
MAX_COUNT = -75000

if "_HasLoad" not in dir():
	ACTIVE_SKILLS = {}
	PASSIVE_SKILLS = {}

class ActiveSkillBase(object):
	skill_id = 0			#技能ID
	skill_rate = 1.0		#技能系数（1是平衡点）
	skill_value = 0			#技能绝对值
	play_time = 1.8			#播放时间（秒）
	play_parallel = 0		#技能并行播放
	prefix_round = 0		#前置回合数
	cd_round = 999			#CD回合数
	need_moral = 999		#需要士气
	is_aoe = False			#是否群攻
	aoe_need_target_cnt = 2	#aoe所需的目标数
	has_buff = False		#是否附带buff
	is_treat = False		#是否治疗
	crit_hurt = 1.5			#默认暴击倍数
	
	@classmethod
	def reg(cls):
		if cls.__name__ in ACTIVE_SKILLS:
			print "GE_EXC, repeat active skill(%s)" % cls.__name__
		ACTIVE_SKILLS[cls.__name__] = cls
		if cls.skill_id:
			if cls.skill_id in ACTIVE_SKILLS:
				print "GE_EXC, repeat active skill id(%s)" % cls.skill_id
			ACTIVE_SKILLS[cls.skill_id] = cls
	
	def __init__(self, unit, argv):
		self.unit = unit
		self.argv = argv
		self.camp = unit.camp
		self.other_camp = unit.other_camp
		self.fight = unit.fight
		# 上次释放回合（因为这里定义了前置回合数，故这样计算之）
		self.do_round = self.unit.create_round + self.prefix_round - self.cd_round
		# 临时技能系数
		self.target_skill_rate = 0.0
	
	def set_round(self, do_round):
		self.do_round = do_round
		self.fight.play_info.append((Operate.SetSkillRound, self.unit.key, self.skill_id, do_round))
	
	# 获取播放时间
	def get_play_time(self):
		return self.play_time
	
	# 是否可以治疗
	def need_treat(self):
		is_need = False
		for unit in self.camp.pos_units.itervalues():
			if unit.hp < int(0.8 * unit.max_hp):
				is_need = True
				break
		return is_need
	
	# 判断是否可做
	def can_do(self):
		ROUND = self.fight.round
		if self.do_round + self.cd_round >= ROUND:
			return False
		if self.need_moral > self.unit.moral:
			return False
		return True
	
	# 释放技能
	def do(self):
		targets = self.select_targets()
		FIGHT = self.fight
		UNIT = self.unit
		# 记录释放回合数
		self.do_round = FIGHT.round
		# 修改play_info
		fight_play_info = FIGHT.new_play_info()
		# 尝试扣士气
		if self.need_moral:
			self.unit.change_moral(-self.need_moral)
		# 触发事件
		UNIT.before_skill(self)
		# 出手前
		self.do_before(targets)
		do_before_play_info = FIGHT.new_play_info()
		# 出手
		for target in targets:
			self.do_target(target)
		do_targets_play_info = FIGHT.new_play_info()
		# 出手后
		self.do_after(targets)
		# 触发事件
		UNIT.after_skill(self)
		# 构建播放列表
		do_after_play_info = FIGHT.play_info
		fight_play_info.append((Operate.UserSkill, UNIT.key, self.skill_id, do_before_play_info, do_targets_play_info, do_after_play_info))
		# 计算播放时间
		self.fight.add_play_time(self.play_time, self.play_parallel)
		# 还原play_info
		FIGHT.restore_play_info(fight_play_info)
	
	def do_cnt(self, cnt=1):
		targets = []
		FIGHT = self.fight
		UNIT = self.unit
		# 记录释放回合数
		self.do_round = FIGHT.round
		# 修改play_info
		fight_play_info = FIGHT.new_play_info()
		# 尝试扣士气
		if self.need_moral:
			self.unit.change_moral(-self.need_moral)
		# 触发事件
		UNIT.before_skill(self)
		self.do_before(targets)
		# 出手前
		do_before_play_info = FIGHT.new_play_info()
		# 出手
		for _ in xrange(cnt):
			targets_cnt = self.select_targets()
			if targets_cnt:
				targets.append(targets_cnt[0])
				self.do_target(targets_cnt[0])
		do_targets_play_info = FIGHT.new_play_info()
		self.do_after(targets)
		# 触发事件
		UNIT.after_skill(self)
		# 构建播放列表
		do_after_play_info = FIGHT.play_info
		fight_play_info.append((Operate.UserSkill, UNIT.key, self.skill_id, do_before_play_info, do_targets_play_info, do_after_play_info))
		# 计算播放时间
		self.fight.add_play_time(self.play_time, self.play_parallel)
		# 还原play_info
		FIGHT.restore_play_info(fight_play_info)
	
	# 对一个目标进行计算
	def do_target(self, target):
		FIGHT = self.fight
		# 修正play_info
		targets_play_info = FIGHT.new_play_info()
		FIGHT.play_info.append((Operate.DoTarget, target.key))
		self.target_skill_rate = 0.0
		target.temp_damage_reduce_rate = 0.0
		# 目标修正
		self.unit.event_before_target(target, self)
		target.event_before_be_target(self.unit, self)
		# 执行效果
		self.do_effect(target)
		self.target_skill_rate = 0.0
		target.temp_damage_reduce_rate = 0.0
		targets_play_info.append(FIGHT.play_info)
		# 还原play_info
		FIGHT.restore_play_info(targets_play_info)
	
	# 判定是否破击
	def is_broken(self, target):
		UNIT = self.unit
		# a/(b/(破击-免破)+c)
		be_div = UNIT.anti_broken - target.not_broken
		if be_div <= MAX_COUNT:
			return False
		if be_div == 0:
			be_div = 1
		rate = BROKEN_A / (BROKEN_B / be_div + BROKEN_C)
		rate += UNIT.anti_broken_rate
		rate -= target.not_broken_rate
		return rate > random.random()
	
	# 判定是否暴击
	def is_crit(self, target):
		UNIT = self.unit
		# a/(b/(暴击-免爆)+c)
		be_div = UNIT.crit - target.crit_press
		if be_div <= MAX_COUNT:
			return False
		if be_div == 0:
			be_div = 1
		rate = CRIT_A / (CRIT_B / be_div + CRIT_C)
		rate += UNIT.crit_rate
		rate -= target.crit_press_rate
		return rate > random.random()
	
	# 判定是否格挡
	def is_parry(self, target):
		UNIT = self.unit
		# a/(b/(格挡-免档)+c)
		be_div = target.parry - UNIT.puncture
		if be_div <= MAX_COUNT:
			return False
		if be_div == 0:
			be_div = 1
		rate = PARRY_A / (PARRY_B / be_div + PARRY_C)
		rate += target.parry_rate
		rate -= UNIT.puncture_rate
		return rate > random.random()
	
	# 通用造成伤害流程
	def computer_hurt(self, target, no_defence=False):
		UNIT = self.unit
		has_broken = False
		#1≤Int(random(0.97,1.02)*(攻击*(技能系数+增伤-减伤-防御免伤比)+技能绝对值))
		if no_defence:
			defence_rate = 0
		else:
			if self.is_broken(target):
				self.fight.play_info.append((Operate.HasBroken, target.key))
				defence_rate = 0
				has_broken = True
			else:
				defence_rate = target.compute_defence_rate(UNIT.career)
		
		other_rate = 1.0 + UNIT.damage_upgrade_rate - target.damage_reduce_rate - target.temp_damage_reduce_rate - defence_rate
		if other_rate < 0.2:
			other_rate = 0.2
		rate = (self.skill_rate + self.target_skill_rate) * other_rate
		if rate < 0:
			rate = 0.0
		hurt = random.uniform(0.97, 1.02) * (UNIT.attack * rate + self.skill_value)
		if self.is_crit(target):
			if not has_broken:
				self.fight.play_info.append((Operate.HasCrit, target.key))
			hurt *= self.crit_hurt
		if self.is_parry(target):
			self.fight.play_info.append((Operate.HasParry, target.key))
			hurt *= target.parry_hurt
		if hurt < 1:
			hurt = 1
		else:
			hurt = int(hurt)
		return hurt
	
	def do_hurt(self, target, no_defence=False):
		UNIT = self.unit
		hurt = self.computer_hurt(target, no_defence)
		target.hurt(hurt, UNIT)
		# 策划要求只算第一次伤害
		if UNIT.total_hurt == 0:
			UNIT.total_hurt += hurt
		UNIT.event_has_hurt(target, hurt)
		target.event_has_be_hurt(UNIT, hurt)
		return hurt
	
	def do_treat(self, target):
		UNIT = self.unit
		hp = (UNIT.attack * (self.skill_rate + self.target_skill_rate) + self.skill_value) * (1.0 + target.treat_rate)
		if random.randint(0, 9999) < UNIT.crit:
			hp *= 1.5
		hp = int(hp)
		target.treat(hp, UNIT)
		return hp
	
	# 选择目标
	def select_targets(self):
		return []
	
	# 技能开始效果
	def do_before(self, targets):
		pass
	
	# 对目标效果
	def do_effect(self, target):
		pass
	
	# 技能结束效果
	def do_after(self, targets):
		pass

class PassiveSkill(object):
	skill_id = 0
	
	@classmethod
	def reg(cls):
		if cls.__name__ in PASSIVE_SKILLS:
			print "GE_EXC, repeat passive skill(%s)" % cls.__name__
		PASSIVE_SKILLS[cls.__name__] = cls
		if cls.skill_id:
			if cls.skill_id in PASSIVE_SKILLS:
				print "GE_EXC, repeat passive skill id(%s)" % cls.skill_id
			PASSIVE_SKILLS[cls.skill_id] = cls
	
	def __init__(self, unit, argv):
		self.unit = unit
		self.argv = argv
		self.camp = unit.camp
		self.other_camp = unit.other_camp
		self.fight = unit.fight
		self.load_event()
		self.unit.passive_skills.append(self)
	
	def make_revive_status(self, flag=None):
		if flag is None:
			flag = self.__class__.__name__
		self.unit.revive_status[flag] = True
	
	def has_revive_status(self, flag=None):
		if flag is None:
			flag = self.__class__.__name__
		return flag in self.unit.revive_status
	
	def load_event(self):
		pass
	
	def unload_event(self):
		pass
