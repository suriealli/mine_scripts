#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Fight.Fight")
#===============================================================================
# 战斗模块
#===============================================================================
import random
import traceback
import cDateTime
import cNetMessage
import cComplexServer
import cRoleMgr
import Environment
from Util import Trace
from Common import CValue
from Common.Message import AutoMessage
from Game.Role import Event, Status
from Game.Role.Data import EnumTempObj, EnumInt1
from Game.Fight import Camp, Handle, Operate, FightConfig

class Fight(Handle.Handle):
	def __init__(self, fight_type):
		Handle.Handle.__init__(self)
		self.fight_type = fight_type						#战斗类型
		self.fight_id = self.allot_fight_id()				#战斗唯一id
		self.config = FightConfig.FIGHT_TYPES[fight_type]	#战斗配置
		self.pvp = self.config.pvp							#是否PVP（决定出手模式）
		#=======================================================================
		# 非0：同时上，只上主角
		# 2：出手时给队友加士气
		# 3：在pvp模式下，随机先出手阵营
		#=======================================================================
		self.group = self.config.group						#是否组队战斗
		self.group_need_hero = False						#组队战斗是否需要英雄
		self.restore = False								#是否可恢复战斗
		self.only_win_save_moral = True						#只有胜利才保存士气
		self.skip_fight_play = False						#跳过战斗播放
		self.viewFightType = self.config.viewFightType		#是否可以保存观战数据
		self.fight_view_data = []							#观战数据
		
		self.key = 0										#战斗分配key
		self.round = 0										#战斗回合数
		self.trigger = 0									#战斗触发数
		self.play_info = []									#战斗码
		self.result = None									#结果 1左边赢 0平局 -1右边赢
		self.is_buy_life = False							#是否买活（用来记录客户端的选择的）
		self.buy_life_count = 0								#买活次数
		
		self.buy_life_role_id = 0							#可以买活的角色ID
		self.control_info = {}								#控制信息 role_id -> main_unit
		
		self.wait_tick_id = 0								#客户端播放tickid
		self.wait_operate = 0								#等待客户端操作
		self.play_total_time = 1.0							#客户端播放总时间
		self.play_parallel = 0								#并行播放类型
		
		self.on_leave_fun = None							#玩家离开战斗回调函数 def(fight, role)
		self.after_fight_fun = None							#战斗结束后的回调函数 def(fight)
		self.after_play_fun = None							#战斗播放后的回调函数 def(fight)
		self.buy_life_fun = None							#战斗中购买复活回调函数 def(fight)
		
		self.fight_statistics = {}							#战斗结束统计数据{roleID: {fightEnum:data}}
		
		#=======================================================================
		# 全局状态
		#=======================================================================
		self.is_back_hurt_trigger = False					#反弹伤害触发
		
	def allot_fight_id(self):
		global Fight_ID
		Fight_ID += 1
		return Fight_ID
	
	def allot_key(self):
		self.key += 1
		return self.key
	
	def reset_trigger(self):
		self.trigger = 0
	
	def try_trigger(self):
		if self.trigger < 128:
			self.trigger += 1
			return True
		else:
			print "GE_EXC, fight trigger too much."
			return False
	
	def on_main_unit_create(self, unit):
		control_role_id = unit.control_role_id
		if not control_role_id:
			return
		if control_role_id in self.control_info:
			sw = "on_main_unit_create role(%s) repeat control" % control_role_id
			Trace.StackWarn(sw)
			return
		# 检查配置是否冲突
		if self.skip_fight_play is True:
			Trace.StackWarn("skip fight play with control main unit.")
			self.skip_fight_play = False
		self.control_info[control_role_id] = unit
	
	def on_main_unit_leave(self, unit):
		control_role_id = unit.control_role_id
		if control_role_id not in self.control_info:
			return
		del self.control_info[control_role_id]
	
	def get_only_controle_role_id(self):
		if len(self.control_info) != 1:
			return 0
		for control_role_id in self.control_info.iterkeys():
			return control_role_id
	
	def get_only_control_main_unit(self, role_id):
		if len(self.control_info) != 1:
			return None
		return self.control_info.get(role_id)
	
	def need_wait_client_select_skill(self):
		#===================================================
		# 当pvp战斗或者pve车轮战主角死了，此时不等待玩家选择技能
		# 附1 眩晕了也不需要选择技能
		# 附2 客户端掉线了也不需要选择技能
		#===================================================
		# 遍历未死的主角
		for control_main_unit in self.control_info.itervalues():
			# 眩晕
			if control_main_unit.stun:
				continue
			# 掉线
			if not control_main_unit.is_online:
				continue
			return True
		return False
	
	def is_all_control_unit_select(self):
		ROUND = self.round
		for control_main_unit in self.control_info.itervalues():
			if control_main_unit.is_online is False:
				continue
			if control_main_unit.select_skill_round != ROUND:
				return False
		return True
	
	def new_play_info(self):
		old_play_info = self.play_info
		self.play_info = []
		return old_play_info
	
	def restore_play_info(self, old_play_info):
		self.play_info = old_play_info
	
	def add_play_time(self, usecond, parallel = 0):
		if parallel and parallel == self.play_parallel:
			self.play_total_time += 0.5
		else:
			self.play_total_time += usecond
		self.play_parallel = parallel
	
	def restore_client(self, role):
		if not self.restore:
			return
		if role in self.left_camp.roles:
			mirror = self.left_camp.mirror
		elif role in self.right_camp.roles:
			mirror = self.right_camp.mirror
		else:
			print "GE_EXC restore_client(%s) has error" % role.GetRoleID()
			return
		LEFT_CAMP = self.left_camp
		RIGHT_CAMP = self.right_camp
		play_info = []
		# 战斗回合数
		play_info.append((Operate.FightRound, self.round))
		# 同步怪物波数
		play_info.append((Operate.MonsterWave, RIGHT_CAMP.monster_wave, len(RIGHT_CAMP.wheels)))
		for unit in LEFT_CAMP.pos_units.itervalues():
			play_info.append(unit.get_unit_info())
		for unit in LEFT_CAMP.vpos_units.itervalues():
			play_info.append(unit.get_unit_info())
		for unit in RIGHT_CAMP.pos_units.itervalues():
			play_info.append(unit.get_unit_info())
		for unit in RIGHT_CAMP.vpos_units.itervalues():
			play_info.append(unit.get_unit_info())
		# 同步头像
		play_info.append((Operate.HeadPortrait, LEFT_CAMP.mirror, LEFT_CAMP.head_portrait))
		play_info.append((Operate.HeadPortrait, RIGHT_CAMP.mirror, RIGHT_CAMP.head_portrait))
		# 如果正在等待客户端选择技能，则插入一个选择技能的指令
		if self.wait_tick_id and self.wait_operate == Operate.SelectSkill:
			#self.play_info.append((Operate.SelectSkill, self.control_info.keys()))
			play_info.append((Operate.WaitTimePoint, self.wait_tick_id / CValue.P2_32))
		# 初始化战场
		role.SendObj(Fight_Init, (self.fight_id, self.fight_type, mirror))
		# 创建战斗单位列表
		role.SendObj(Fight_List, play_info)
	
	def notice_wait_client_select(self):
		if self.need_wait_client_select_skill():
			#保存观战数据(不添加选择技能提示)
			self.save_view()
			self.add_play_time(SELECT_SKILL_WAIT_TIME, 0)
			self.play_info.append((Operate.SelectSkill, self.control_info.keys()))
			self.play_info.append((Operate.WaitTimePoint, cDateTime.Seconds() + int(self.play_total_time)))
			cNetMessage.PackPyMsg(Fight_List, self.play_info)
			for role in self.left_camp.roles:
				role.BroadMsg_NoExcept()
			for role in self.right_camp.roles:
				role.BroadMsg_NoExcept()
			if self.wait_tick_id != 0:
				print "GE_EXC, repeat notice_wait_client_select"
			self.wait_operate = Operate.SelectSkill
			self.wait_tick_id = cComplexServer.RegFastTick(int(self.play_total_time), self.on_wait_select, None)
			self.show(self.play_total_time, None)
			self.play_total_time = 1.0
			self.play_info = []
		else:
			self.on_wait_select(None)
	
	def on_wait_select(self, regparam):
		self.wait_tick_id = 0
		self.do_round()
	
	def notice_wait_client_end(self):
		# 因为有可能是强制结束战斗，故要取消前面的tick，并计算补偿时间
		if self.wait_tick_id:
			cComplexServer.UnregFastTick(self.wait_tick_id)
			bc_time = (self.wait_tick_id / CValue.P2_32) -cDateTime.Seconds() - SELECT_SKILL_WAIT_TIME
			if bc_time > 0:
				self.add_play_time(bc_time)
			self.wait_tick_id = 0
		# 不跳过战斗播放，则通知客户端播放
		if self.skip_fight_play is False:
			cNetMessage.PackPyMsg(Fight_List, self.play_info)
			for role in self.left_camp.roles:
				role.BroadMsg_NoExcept()
			for role in self.right_camp.roles:
				role.BroadMsg_NoExcept()
			self.wait_operate = Operate.End
			self.wait_tick_id = cComplexServer.RegFastTick(int(self.play_total_time), self.on_wait_end, None)
			self.show(self.play_total_time, None)
			self.save_view()
			self.play_total_time = 1.0
			self.play_info = []
		# 否则直接结束
		else:
			self.on_wait_end(None)
	
	def on_wait_end(self, regparam):
		self.wait_tick_id = 0
		self.on_after_play()
	
	def notic_wait_client_buy(self):
		self.play_info.append((Operate.BuyLife, self.buy_life_role_id, self.buy_life_count))
		self.add_play_time(SELECT_SKILL_WAIT_TIME, 0)
		cNetMessage.PackPyMsg(Fight_List, self.play_info)
		for role in self.left_camp.roles:
			role.BroadMsg_NoExcept()
		for role in self.right_camp.roles:
			role.BroadMsg_NoExcept()
		if self.wait_tick_id != 0:
				print "GE_EXC, repeat notic_wait_client_buy"
		self.wait_operate = Operate.BuyLife
		self.is_buy_life = False
		self.wait_tick_id = cComplexServer.RegFastTick(int(self.play_total_time), self.on_wait_buy, None)
		self.show(self.play_total_time, None)
		self.save_view()
		self.play_total_time = 1.0
		self.play_info = []
	
	def on_wait_buy(self, regparam):
		self.wait_tick_id = 0
		try:
			if self.is_buy_life:
				self.is_buy_life = False
				self.buy_life_fun(self)
				self.buy_life_count += 1
			else:
				self.buy_life_fun = None
		except:
			traceback.print_exc()
			Trace.StackWarn("fight buy error")
			self.result = 0
			self.do_result()
		self.try_result()
	
	def save_view(self):
		if not self.viewFightType:
			return
		self.fight_view_data.append(self.play_info)
	
	def GetViewData(self):
		#每10回合一个单位
		fight_view_init_data = (self.fight_id, self.viewFightType, 1)
		all_round_view_data = []
		roundList = []
		for playInfo in self.fight_view_data:
			if playInfo[0] != Operate.Round or playInfo[1] % 10 != 0:
				roundList.extend(playInfo)
				continue
			all_round_view_data.append(roundList)
			roundList = playInfo
		all_round_view_data.append(roundList)
		return fight_view_init_data, all_round_view_data
				
		
	
	def show(self, wait_time, init):
		if not Environment.IsWindows:
			return
		import DynamicPath
		from Util.PY import PyParseBuild
		pf = PyParseBuild.PyObj(Operate)
		vs = {}
		for _, v, s in pf.GetEnumerateInfo():
			vs[v] = s
		if init:
			with open(DynamicPath.BinPath + "Play.txt", "w") as f:
				print>>f, "-----------fight id(%s)-----------fight type(%s)-----------wait %s" % (init[0], init[1], wait_time)
		else:
			with open(DynamicPath.BinPath + "Play.txt", "a") as f:
				print>>f, "======================================= wait %s" % wait_time
				self.show_fight(self.play_info, f, vs)
	
	def show_fight(self, l, f, vs):
		if not Environment.IsWindows:
			return
		for row in l:
			if row[0] == Operate.UserSkill:
				print>>f, "|-->", "unit %s use skill %s" % (row[1], row[2])
				self.show_skill(row[3], f, vs)
				self.show_targets(row[4], f, vs)
				self.show_skill(row[5], f, vs)
			else:
				print>>f, "----", vs.get(row[0], row[0]), row
	
	def show_skill(self, l, f, vs):
		for row in l:
			print>>f, "|-->", vs.get(row[0], row[0]), row
	
	def show_targets(self, l, f, vs):
		for target in l:
			for row in target:
				if row[0] == Operate.DoTarget:
					print>>f, "    |-->", "target %s" % row[1]
				else:
					print>>f, "    |-->", vs.get(row[0], row[0]), row
	
	def create_camp(self):
		self.left_camp = Camp.Camp(self, 1)
		self.right_camp = Camp.Camp(self, -1)
		self.left_camp.other_camp = self.right_camp
		self.right_camp.other_camp = self.left_camp
		return self.left_camp, self.right_camp
	
	def start(self):
		try:
			# 如果可以买活，则记录买活角色ID
			if self.buy_life_fun:
				self.buy_life_role_id = self.get_only_controle_role_id()
			LEFT_CAMP = self.left_camp
			RIGHT_CAMP = self.right_camp
			LEFP_UNITS = LEFT_CAMP.pos_units
			RIGHT_UNITS = RIGHT_CAMP.pos_units
			# 复位触发计数
			self.reset_trigger()
			# 初始化客户端
			for unit in LEFP_UNITS.itervalues():
				unit.create()
			for unit in LEFT_CAMP.vpos_units.itervalues():
				unit.create()
			for unit in RIGHT_UNITS.itervalues():
				unit.create()
			for unit in RIGHT_CAMP.vpos_units.itervalues():
				unit.create()
			# 非跳过战斗才发送战斗初始化
			if self.skip_fight_play is False:
				if LEFT_CAMP.roles:
					cNetMessage.PackPyMsg(Fight_Init, (self.fight_id, self.fight_type, LEFT_CAMP.mirror))
					for role in LEFT_CAMP.roles:
						role.BroadMsg_NoExcept()
				if RIGHT_CAMP.roles:
					cNetMessage.PackPyMsg(Fight_Init, (self.fight_id, self.fight_type, RIGHT_CAMP.mirror))
					for role in RIGHT_CAMP.roles:
						role.BroadMsg_NoExcept()
			self.show(0, (self.fight_id, self.fight_type, RIGHT_CAMP.mirror))
			#self.save_view((self.fight_id, self.fight_type, LEFT_CAMP.mirror))
			
			# 怪物波数
			self.play_info.append((Operate.MonsterWave, RIGHT_CAMP.monster_wave, len(RIGHT_CAMP.wheels)))
			# 头像
			self.play_info.append((Operate.HeadPortrait, LEFT_CAMP.mirror, LEFT_CAMP.head_portrait))
			self.play_info.append((Operate.HeadPortrait, RIGHT_CAMP.mirror, RIGHT_CAMP.head_portrait))
			# 将战斗单位加入战场
			for unit in LEFP_UNITS.itervalues():
				unit.join_fight()
			for unit in LEFT_CAMP.vpos_units.itervalues():
				unit.join_fight()
			for unit in RIGHT_UNITS.itervalues():
				unit.join_fight()
			for unit in RIGHT_CAMP.vpos_units.itervalues():
				unit.join_fight()
			# 开始回合战斗
			if self.result is None:
				self.notice_wait_client_select()
			else:
				self.do_result()
		except:
			traceback.print_exc()
			Trace.StackWarn("fight init error.")
			self.result = 0
			self.do_result()
	
	def end(self, result = 0):
		self.result = result
		self.do_result()
	
	def do_round(self):
		try:
			LEFP_UNITS = self.left_camp.pos_units
			RIGHT_UNITS = self.right_camp.pos_units
			# 复位触发计数
			self.reset_trigger()
			# 回合计数
			self.round += 1
			self.play_info.append((Operate.Round, self.round))
			# 触发回合开始
			self.event_before_round()
			# 在这之前，星灵先出手
			star_girl_shot_list = []
			star_girl_shot_list.extend(self.left_camp.vpos_units.itervalues())
			star_girl_shot_list.extend(self.right_camp.vpos_units.itervalues())
			star_girl_shot_list.sort(key=lambda u:u.speed, reverse=True)
			for unit in star_girl_shot_list:
				unit.change_moral(25)
			for unit in star_girl_shot_list:
				# 有可能提前结束本回合出手
				if LEFP_UNITS and RIGHT_UNITS:
					unit.do_shot()
			# 回合开始确定出手顺序
			shot_list = []
			if self.pvp:
				lus = LEFP_UNITS.values()
				lus.sort(key=lambda u:u.speed, reverse=True)
				rus = RIGHT_UNITS.values()
				rus.sort(key=lambda u:u.speed, reverse=True)
				# 跨服组队竞技场需要随机先出手方
				if self.group == 3 and random.randint(0, 1):
					lus, rus = rus, lus
				li = 0
				ri = 0
				ll = len(lus)
				rl = len(rus)
				for _ in xrange(max(ll, rl)):
					if li < ll:
						shot_list.append(lus[li])
						li += 1
					if ri < rl:
						shot_list.append(rus[ri])
						ri += 1
			else:
				shot_list.extend(LEFP_UNITS.itervalues())
				shot_list.sort(key=lambda unit:unit.speed, reverse=True)
				right_list = RIGHT_UNITS.values()
				right_list.sort(key=lambda unit:unit.speed, reverse=True)
				shot_list.extend(right_list)
			# 按顺序出手
			for unit in shot_list:
				if unit.is_out:
					unit.cur_skill = None
					continue
				if unit.stun:
					unit.cur_skill = None
					continue
				# 有可能提前结束本回合出手
				if LEFP_UNITS and RIGHT_UNITS:
					unit.do_shot()
				else:
					unit.cur_skill = None
					break
			# 触发回合结束
			self.event_after_round()
			# 尝试复活
			self.right_camp.try_revive()
			self.left_camp.try_revive()
			# 星灵退场【解决组队战斗星灵问题】
			if self.buy_life_fun is None:
				self.right_camp.try_star_girl_leave()
				self.left_camp.try_star_girl_leave()
			# 尝试援助
			self.right_camp.try_wheel()
			self.left_camp.try_wheel()
			# 结算
			self.try_result()
		except:
			traceback.print_exc()
			Trace.StackWarn("fight round error.")
			self.result = 0
			self.do_result()
	
	def try_result(self):
		# 已经有结果了，结算
		if self.result is not None:
			self.do_result()
			return
		# 双方还有人，可以继续打
		if self.left_camp.pos_units and self.right_camp.pos_units:
			# 超过最大回合数，强行平局
			if self.round > (30 if self.pvp else 99):
				self.result = 0
				self.do_result()
			# 否则继续打
			else:
				self.notice_wait_client_select()
			return
		# 左阵营有人，或者不能买活，就不用购买了（这里有个潜规则，只有左阵营才能买活）
		if self.left_camp.pos_units or self.buy_life_fun is None:
			self.do_result()
			return
		# 可控的玩家不在线，不能买活
		role = cRoleMgr.FindRoleByRoleID(self.buy_life_role_id)
		if role is None:
			self.do_result()
			return
		# 第一次自动复活
		if self.buy_life_count == 0:
			self.is_buy_life = True
			self.on_wait_buy(None)
		# 通知客户端播放并选择是否买活
		else:
			self.notic_wait_client_buy()
	
	def do_result(self):
		# 星灵退场
		self.right_camp.try_star_girl_leave()
		self.left_camp.try_star_girl_leave()
		# 结果
		if self.result is None:
			self.result = (1 if self.left_camp.pos_units else -1)
		self.play_info.append((Operate.End, self.result, self.fight_statistics))
		self.add_play_time(4, 0)
		# 保存血量
		self.left_camp.save_hp()
		self.right_camp.save_hp()
		self.save_view()
		# 战斗结束()
		self.on_after_fight()
		# 播结果
		self.notice_wait_client_end()
	
	def set_fight_statistics(self, roleId, enumKey, sValue):
		#设置战斗结束统计( 必须在afterplay 之前调用)
		if roleId not in self.fight_statistics:
			self.fight_statistics[roleId] = {}
		self.fight_statistics[roleId][enumKey] = sValue
	
	def on_after_fight(self):
		if self.after_fight_fun is None:
			return
		try:
			self.after_fight_fun(self)
			# 确保只调用一次
			self.after_fight_fun = None
		except:
			traceback.print_exc()
	
	def on_leave_fight(self, role):
		# 取消战斗关联
		role.SetTempObj(EnumTempObj.FightCamp, None)
		#退出战斗状态
		Status.Outstatus(role, EnumInt1.ST_FightStatus)
		# 触发回调
		if self.on_leave_fun:
			try:
				self.on_leave_fun(self, role)
			except:
				traceback.print_exc()
	
	def on_after_play(self):
		# 强制结束战斗
		cNetMessage.PackPyMsg(Fight_End, self.fight_id)
		LEFT_CAMP = self.left_camp
		for role in LEFT_CAMP.roles:
			# 确保没掉线
			if role.IsKick(): continue
			# 确保没有提前离开（快速结束战斗）
			if role.GetTempObj(EnumTempObj.FightCamp) is not LEFT_CAMP: continue
			# 非跳过战斗才通知客户端
			if self.skip_fight_play is False:
				role.BroadMsg()
			self.on_leave_fight(role)
		RIGHT_CAMP = self.right_camp
		for role in RIGHT_CAMP.roles:
			# 确保没掉线
			if role.IsKick(): continue
			# 确保没有提前离开（快速结束战斗）
			if role.GetTempObj(EnumTempObj.FightCamp) is not RIGHT_CAMP: continue
			# 非跳过战斗才通知客户端
			if self.skip_fight_play is False:
				role.BroadMsg()
			self.on_leave_fight(role)
		# 触发回调
		if self.after_play_fun is None:
			return
		try:
			self.after_play_fun(self)
			# 确保只调用一次
			self.after_play_fun = None
		except:
			traceback.print_exc()
	
	def do_select_skill_normal(self, role, camp, index):
		control_main_unit = self.get_only_control_main_unit(role.GetRoleID())
		# 无可控制对象【无权限】
		if control_main_unit is None:
			return
		# 选择技能
		control_main_unit.select_active_skill(index)
		# 提前触发tick
		cComplexServer.TriggerFastTick(self.wait_tick_id)
	
	def do_select_skill_group(self, role, camp, index):
		control_main_unit = self.control_info.get(role.GetRoleID())
		# 无可控制对象【无权限】
		if control_main_unit is None:
			return
		# 选择技能
		control_main_unit.select_active_skill(index)
		# 通知客户端
		for camp_role in camp.roles:
			camp_role.SendObj_NoExcept(LongQiShiSelectSkill, (role.GetRoleID(), camp.mirror, self.round))
		# 如果所有的客户端都选完技能，则提前触发tick
		if self.is_all_control_unit_select():
			cComplexServer.TriggerFastTick(self.wait_tick_id)

def SelectSkill(role, msg):
	client_round, index = msg
	# 没在战斗中
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if camp is None:
		return
	fight = camp.fight
	# 回合不对
	if fight.round != client_round:
		return
	# 并非在等待玩家选择技能
	if not fight.wait_tick_id:
		return
	if fight.wait_operate != Operate.SelectSkill:
		return
	# 玩家可能加速了
	if cDateTime.Seconds() < ((fight.wait_tick_id / CValue.P2_32) - SELECT_SKILL_WAIT_TIME - 15):
		#print "GE_EXC role(%s) select skill too fast(%s)" % (role.GetRoleID(), cDateTime.Seconds() - fight.wait_tick_id / CValue.P2_32 + SELECT_SKILL_WAIT_TIME)
		return
	if fight.group:
		fight.do_select_skill_group(role, camp, index)
	else:
		fight.do_select_skill_normal(role, camp, index)

def BuyLife(role, msg):
	client_round, is_buy_life = msg
	# 没在战斗中
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if camp is None:
		return
	fight = camp.fight
	# 回合不对
	if fight.round != client_round:
		return
	# 无权限
	if role.GetRoleID() != fight.buy_life_role_id:
		return
	# 并非在等待玩家购买
	if not fight.wait_tick_id:
		return
	if fight.wait_operate != Operate.BuyLife:
		return
	# 标记是否购买
	fight.is_buy_life = is_buy_life
	# 提前触发tick
	cComplexServer.TriggerFastTick(fight.wait_tick_id)

def EndFight(role, msg):
	if type(msg) is not int:
		print "GE_EXC, role(%s) EndFight error." % role.GetRoleID()
		role.WPE()
		return
	# 没在战斗中
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if camp is None:
		return
	fight = camp.fight
	# 战斗id错误
	if fight.fight_id != msg:
		#print "GE_EXC, role(%s) fight id is not equal on EndFight" % role.GetRoleID()
		return
	# 服务端还没结束
	if fight.result is None:
		#print "GE_EXC, role(%s) fight is running but client is end." % role.GetRoleID()
		role.WPE()
		return
	# 等待的事件不对
	if fight.wait_operate != Operate.End:
		return
	# 服务端已经自行结束了
	if not fight.wait_tick_id:
		return
	# 玩家可能加速了
	if (not fight.config.canJumpFight) and (cDateTime.Seconds() < ((fight.wait_tick_id / CValue.P2_32) - 10)):
		#print "GE_EXC role(%s) end fight too fast(%s)" % (role.GetRoleID(), cDateTime.Seconds() - fight.wait_tick_id / CValue.P2_32)
		return
	# 离开战斗
	fight.on_leave_fight(role)
	# 检测是否所有的玩家都离开战斗了
	LEFT_CAMP = fight.left_camp
	for role in LEFT_CAMP.roles:
		if not role.IsKick() and role.GetTempObj(EnumTempObj.FightCamp) is LEFT_CAMP:
			return
	RIGHT_CAMP = fight.right_camp
	for role in RIGHT_CAMP.roles:
		if not role.IsKick() and role.GetTempObj(EnumTempObj.FightCamp) is RIGHT_CAMP:
			return
	# 所有玩家都提前离开战斗，提前触发tick
	cComplexServer.TriggerFastTick(fight.wait_tick_id)

def BeforeExit(role, param):
	#真正的离开游戏
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if camp is None:
		return
	fight = camp.fight
	# 标记受控主角离线
	control_main_unit = fight.control_info.get(role.GetRoleID())
	if control_main_unit:
		control_main_unit.is_online = False
	# 取消战斗关联
	camp.roles.discard(role)
	# 离开战斗
	camp.fight.on_leave_fight(role)

def ClientLost(role, param):
	#断线
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if camp is None:
		return
	fight = camp.fight
	# 标记受控主角离线
	control_main_unit = fight.control_info.get(role.GetRoleID())
	if control_main_unit:
		control_main_unit.is_online = False
	if fight.restore:
		#如果是需要还原的战斗，不做操作
		return
	# 取消战斗关联
	camp.roles.discard(role)
	# 离开战斗
	camp.fight.on_leave_fight(role)

def RestoreFight(role):
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if camp is None:
		return
	fight = camp.fight
	if not fight.restore:
		return
	camp.fight.restore_client(role)
	# 标记受控主角上线
	control_main_unit = camp.fight.control_info.get(role.GetRoleID())
	if control_main_unit:
		control_main_unit.is_online = True

if "_HasLoad" not in dir():
	Fight_ID = 0
	SELECT_SKILL_WAIT_TIME = 25
	Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
	Event.RegEvent(Event.Eve_ClientLost, ClientLost)
	Fight_Init = AutoMessage.AllotMessage("Fight_Init", "初始化战场")
	Fight_List = AutoMessage.AllotMessage("Fight_List", "战斗列表")
	Fight_End = AutoMessage.AllotMessage("Fight_End", "战斗强行结束")
	
	LongQiShiSelectSkill= AutoMessage.AllotMessage("LongQiShiSelectSkill", "战斗选技能")
	
	Fight_BuyLife = AutoMessage.AllotMessage("Fight_BuyLife", "是否购买复活")
	cRoleMgr.RegDistribute(LongQiShiSelectSkill, SelectSkill)
	cRoleMgr.RegDistribute(Fight_BuyLife, BuyLife)
	cRoleMgr.RegDistribute(Fight_End, EndFight)
