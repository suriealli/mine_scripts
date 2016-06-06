#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.DeepHell.DeepHellCross")
#===============================================================================
# 深渊炼狱 cross
#===============================================================================
import copy
import random
import cRoleMgr
import cProcess
import cSceneMgr
import cDateTime
import cNetMessage
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumAward, GlobalPrompt, EnumRoleStatus
from World import Define
from ComplexServer.Log import AutoLog
from Game.Fight import Fight, Middle
from Game.Activity.Award import AwardMgr
from Game.Role import Status, Event, Rank
from Game.NPC import NPCServerFun, EnumNPCData
from Game.DeepHell import DeepHellConfig, DeepHellDefine
from Game.Role.Data import EnumInt1, EnumTempObj, EnumCD

if "_HasLoad" not in dir():
	#活动图标开关
	IS_START = False
	#是否可以进入
	CAN_IN = False
	#活动开关
	IS_INIT = False
	#活动ID
	ACTIVEID = 0
	#开始击杀时间戳
	TIMESTAMPSTART = 0
	#活动结束时间戳
	TIMESTAMPEND = 0
	
	#战区下一个玩家进入的房间缓存 {areaType:roomId,}
	DeepHell_AreaNextRoom_Dict = {}
	#房间字典 {roomId:DeepHellRoom,}
	DeepHell_Room_Dict = {}
	#角色字典 {roleId:DeepHellRole,}
	DeepHell_Role_Dict = {}
	
	#深渊炼狱_活动状态_同步 格式：(IS_START, IS_INIT, ACTIVEID)
	DeepHellCross_ActiveState_S = AutoMessage.AllotMessage("DeepHellCross_ActiveState_S", "深渊炼狱跨服_活动状态_同步")
	
	#深渊炼狱跨服_积分排行榜同步 格式 {roleId:[score, history_floor, role_id, role_name, zone_name],}
	DeepHellCross_ScoreRank_S = AutoMessage.AllotMessage("DeepHellCross_ScoreRank_S", "深渊炼狱跨服_积分排行榜同步")
	
	#深渊炼狱跨服_炼狱者数据同步 格式[活动ID, 当前塔层, 最高塔层, 本层击杀, 击杀玩家总数, 击杀怪物总数, 积分, 连杀数, 房间ID]
	DeepHellCross_DHRoleData_S = AutoMessage.AllotMessage("DeepHellCross_DHRoleData_S", "深渊炼狱跨服_炼狱者数据同步")
	
	#深渊炼狱跨服_战败等待复活选项
	DeepHellCross_AfterPVPFailWait_SB = AutoMessage.AllotMessage("DeepHellCross_AfterPVPFailWait_SB", "深渊炼狱跨服_战败等待复活选项")
	
	#深渊炼狱跨服_正式开始时间戳同步 
	DeepHellCross_RealTimeStamp_S = AutoMessage.AllotMessage("DeepHellCross_RealTimeStamp_S", "深渊炼狱跨服_正式开始时间戳同步")
	
	#
	DeepHellCross_ShowRank_S = AutoMessage.AllotMessage("DeepHellCross_ShowRank_S", "深渊炼狱跨服_展示排行榜同步")
	
	#深渊炼狱跨服_活动结束时间戳_同步 格式 timeStamp
	DeepHellCross_EndTimeStamp_S = AutoMessage.AllotMessage("DeepHellCross_EndTimeStamp_S", "深渊炼狱跨服_活动结束时间戳_同步")
	
	Tra_DeepHell_ProtectReview = AutoLog.AutoTransaction("Tra_DeepHell_ProtectReview", "深渊炼狱跨服_保层复活")
	Tra_DeepHellCross_FloorReward = AutoLog.AutoTransaction("Tra_DeepHellCross_FloorReward", "深渊炼狱跨服_塔层奖励")
	Tra_DeepHellCross_RankReward = AutoLog.AutoTransaction("Tra_DeepHellCross_RankReward", "深渊炼狱跨服_排名奖励")
	
	
	
#===============================================================================
# 对象定义
#===============================================================================
class DeepHellScoreRank(Rank.LittleRank):
	'''
	深渊炼狱 积分排行榜
	数据格式 ：{roleId:[score, history_floor, role_id, role_name, zone_name],}
	'''
	def __init__(self, maxRankSize):
		Rank.LittleRank.__init__(self, maxRankSize)
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return (v1[0],v1[1],v1[2]) < (v2[0],v2[1],v2[2])
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		
	
class DeepHellRoom():
	'''
	深渊炼狱 房间类
	'''
	def __init__(self, room_cfg):
		self.room_cfg = room_cfg
		self.room_id = room_cfg.roomID
		self.area_type = room_cfg.roomAreaType
		self.floor_dict = {}							#塔层字典{floor_index:floor_obj,}
		self.score_rank = DeepHellScoreRank(DeepHellDefine.DeepHell_ScoreRankSize)
		self.total_role_cnt = 0							#房间内总人数
		
		self.after_init()
	
	def after_init(self):
		#缓存战区下个进入的房间
		global DeepHell_AreaNextRoom_Dict
		if self.area_type not in DeepHell_AreaNextRoom_Dict:
			DeepHell_AreaNextRoom_Dict[self.area_type] = self.room_id
		
		#创建房间塔层
		for floorIndex in xrange(len(self.room_cfg.sceneList)):
			self.floor_dict[floorIndex + 1] = DeepHellFloor(floorIndex + 1, self)
			
		#注册同步房间数据tick
		self.sync_room_data_tick = cComplexServer.RegTick(DeepHellDefine.Sync_RoomData_Interval, self.sync_room_data)
	
	
	def sync_room_data(self, callArgvs = None, regParams = None):
		'''
		同步房间数据给房间内所有人
		'''
		if not IS_START:
			return
		
		#注册同步房间数据tick
		self.sync_room_data_tick = cComplexServer.RegTick(DeepHellDefine.Sync_RoomData_Interval, self.sync_room_data)
		
		if not IS_INIT:
			return
		
		for floor_obj in self.floor_dict.itervalues():
			floor_obj.on_sync_data()
	

	def end_process(self):
		'''
		活动结束 房间结算处理
		'''
		#结算积分排行榜
		score_rank_dict = self.score_rank.data
		if len(score_rank_dict) > 1:
			score_rank_list = list(score_rank_dict.values())
			score_rank_list.sort(key = lambda x:(x[0],x[1],x[2]), reverse = True)
			with Tra_DeepHellCross_RankReward:
				AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveDeepHellScoreReward, (ACTIVEID, self.room_id, score_rank_list))
			for rank, rankInfo in enumerate(score_rank_list):
				AwardMgr.SetAward(rankInfo[2], EnumAward.DeepHellScoreRankReward, itemList=DeepHellConfig.GetRankRewardByTypeAndRank(self.area_type, rank + 1), clientDescParam=(rank + 1,))
		
		#计算塔层奖励
		for floor_obj in self.floor_dict.values():
			floor_obj.on_end_process()
		
		
class DeepHellFloor():
	'''
	深渊炼狱 塔层类
	'''
	def __init__(self, floor_index, room_obj):
		self.floor_index = floor_index
		self.room_obj = room_obj					#塔层所属房间obj
		self.room_id = room_obj.room_id				#塔层所属房间id
		self.scene_id = 0							#塔层对应场景ID
		self.scene_obj = None						#塔层对应场景obj
		self.dh_role_dict = {}						#塔层中玩家
		self.monster_index_set = set()					#塔层怪物索引集合
		self.refresh_interval = 0					#塔层刷怪间隔秒
		self.monster_info_list = None					#塔层怪物点信息
		
		self.after_init()
	

	def after_init(self):
		'''
		根据  room_obj， floor_index 获取配置场景 并注册NPC创建TICK逻辑
		'''
		room_id = self.room_id
		self.scene_id = DeepHellDefine.DeepHell_SceneConfig_Dict[room_id][self.floor_index - 1]
		
		scene = cSceneMgr.SearchPublicScene(self.scene_id)
		if not scene:
			print "GE_EXC, DeepHell can not find scene by scene_id(%s) with room_id(%s) and floorIndex(%s) " % (self.scene_id, room_id, self.floor_index)
			return
		self.scene_obj = scene
		
		#floor_cfg
		self.floor_cfg = DeepHellConfig.DeepHell_FloorConfig_Dict.get(self.floor_index, None)
		
		#需要刷怪 注册tick
		self.refresh_interval, self.monster_info_list = DeepHellConfig.GetMonsterInfoByFloorIndex(self.floor_index)
		if len(self.monster_info_list) > 0:
			self.refresh_monster_tick = cComplexServer.RegTick(self.refresh_interval, self.refresh_monster)
		
	
	def refresh_monster(self, callArgvs = None, regParams = None):
		'''
		tick触发刷出怪物
		'''
		if not IS_START:
			return
		
		#不管如何 注册下一轮刷怪TICK
		self.refresh_monster_tick = cComplexServer.RegTick(self.refresh_interval, self.refresh_monster)
		
		if not IS_INIT:
			return
		
		for monsterIndex, monsterInfo in enumerate(self.monster_info_list):
			if monsterIndex not in self.monster_index_set:
				monster = self.scene_obj.CreateNPC(*monsterInfo)
				monster.SetPyDict(DeepHellDefine.IDX_ROOM_ID, self.room_obj.room_id)
				monster.SetPyDict(DeepHellDefine.IDX_FLOOR_INDEX, self.floor_index)
				monster.SetPyDict(DeepHellDefine.IDX_IN_FIGHT, False)
				monster.SetPyDict(DeepHellDefine.IDX_MONSTER_INFO,monsterInfo)
				monster.SetPyDict(DeepHellDefine.IDX_MONSTER_INDEX, monsterIndex)
				monster.SetPyDict(DeepHellDefine.IDX_MONSTER_SCENEID, self.scene_id)
				self.monster_index_set.add(monsterIndex)
	
	
	def on_role_join(self, dh_role, isReload = False, isAfterFail = False):
		'''
		炼狱者进入塔层处理
		@param isReload: True表示重载 未改变塔层  击杀数不变   False表示非重载改变塔层 改变击杀数
		@param isAfterFail: True表示失败 击杀数初始配置值 False表示升高塔层 击杀数重置
		'''
		#进入塔层 强制关联
		dh_role.floor_index = self.floor_index
		dh_role.floor_obj = self
		dh_role.room_id = self.room_id
		dh_role.room_obj = self.room_obj
		#非重载 同步击杀数
		if not isReload:
			if not isAfterFail:
				dh_role.cur_floor_kill_cnt = 0
			else:
				dh_role.cur_floor_kill_cnt = self.floor_cfg.crashKillCnt
		else:
			pass
		
		#附加炼狱者状态
		dh_role.state |= DeepHellDefine.STATE_ONLINE
		#历史最高塔层处理
		if dh_role.max_floor_history < self.floor_index:
			dh_role.max_floor_history = self.floor_index
		#缓存炼狱者到字典
		self.dh_role_dict[dh_role.role_id] = dh_role
		
		#已经掉线了
		if dh_role.role and not dh_role.role.IsLost() and not dh_role.role.IsKick():
			#场景传送
			dh_role.role.Revive(self.scene_id, *self.random_pos())
	
	
	def on_role_leave(self, dh_role):
		'''
		炼狱者离开塔层处理
		'''
		#取消原floor关联
		if dh_role.role_id in self.dh_role_dict:
			del self.dh_role_dict[dh_role.role_id]
	
	
	def on_change_floor(self, dh_role, step = 1):
		'''
		炼狱者改变塔层
		@param step: 爬塔步长 step>0 去升高层 step<0 坠低层
		'''
		targetFloorIndex = dh_role.floor_index + step
		if targetFloorIndex not in self.room_obj.floor_dict:
			print "GE_EXC, DeepHell::DeepHellFloor::on_change_floor, targetFloorIndex(%s) error!" % targetFloorIndex
			return
		
		#离开旧塔层
		dh_role.floor_obj.on_role_leave(dh_role)
		#进入新塔层
		(self.room_obj.floor_dict[targetFloorIndex]).on_role_join(dh_role, isReload = False, isAfterFail = False if step > 0 else True)
		#同步客户端数据
		dh_role.sync_role_data()

	
	def random_pos(self):
		'''
		返回 随机出身点 （X,Y）
		'''
		return self.floor_cfg.random_review_pos()
	
	
	def on_end_process(self):
		'''
		本次活动结束处理
		'''
		role_id_list = [role_id for role_id in self.dh_role_dict.keys()]
		with Tra_DeepHellCross_FloorReward:
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveDeepHellFloorReward, (ACTIVEID, self.room_id, self.floor_index, role_id_list))
		
		#结算塔层奖励
		for role_id in role_id_list:
			AwardMgr.SetAward(role_id, EnumAward.DeepHellFloorReward, itemList=DeepHellConfig.GetFloorRewardByTypeAndIndex(self.room_obj.area_type, self.floor_index), clientDescParam=(self.floor_index,))
		
		#删除场景内剩余monster
		for monster in self.scene_obj.GetAllNPC():
			monster.Destroy()
			
		#删除NPC索引记录
		self.monster_index_set.clear()
		
		#最终同步排行版
		self.on_sync_data()
		
		#通知客户端展示排行榜
		for dh_role in self.dh_role_dict.values():
			#已经掉线了
			if dh_role.role and not dh_role.role.IsLost() and not dh_role.role.IsKick():
				dh_role.role.SendObj(DeepHellCross_ShowRank_S, None)
		
		#注册tick踢出场景内玩家回本服
		cComplexServer.RegTick(DeepHellDefine.DeepHell_KickOut_Delay, self.kick_all)
	
	
	def kick_all(self, callArgvs = None, regParams = None):
		'''
		踢出场景内所有玩家
		'''
		for role in self.scene_obj.GetAllRole():
			role.GotoLocalServer(None, None)
			
			
	def on_sync_data(self, callArgvs = None, regParams = None):
		'''
		同步数据
		'''
		#同步房间积分排行榜
		cNetMessage.PackPyMsg(DeepHellCross_ScoreRank_S, self.room_obj.score_rank.data)
		self.scene_obj.BroadMsg()


class DeepHellRole():
	'''
	深渊炼狱 角色类
	'''
	def __init__(self, role, zone_name, room_id, floor_index = DeepHellDefine.DEFAULT_FLOOR):
		self.role = role
		self.role_id = role.GetRoleID()
		self.role_name = role.GetRoleName()
		self.zone_name = zone_name
		
		self.room_id = room_id							#房间ID
		self.room_obj = None							#房间OBJ
		self.floor_index = floor_index					#塔层索引
		self.floor_obj = None							#塔层OBJ
		
		self.fight_data = None							#角色战斗数据
		self.fight_data_soul = None						#英魂战斗数据
		
		self.dh_score = 0								#炼狱积分
		self.max_floor_history = floor_index			#历史最高塔层
		self.total_kill_role = 0						#总击杀数玩家数
		self.total_kill_monster = 0						#总击杀怪物数
		self.kill_cnt = 0								#连杀数
		self.be_kill_cnt = 0							#被连杀数
		self.cur_floor_kill_cnt = 0						#当前塔层击杀数
		
		self.state = DeepHellDefine.STATE_UNDEFINE		#初始状态
		
		self.after_init()
	
	
	def after_init(self):
		'''
		炼狱者初始后关联塔层和房间obj
		'''
		self.room_obj = DeepHell_Room_Dict.get(self.room_id, None)
		if not self.room_obj:
			print "GE_EXC, DeepHell::DeepHellRole::after_init,can not get room_obj by room_id(%s)" % self.room_id
			return
		self.floor_obj = self.room_obj.floor_dict.get(self.floor_index, None)
		if not self.floor_obj:
			print "GE_EXC, DeepHell::DeepHellRole::after_init,can not floor_obj by room_id(%s) and floor_index(%s)" % (self.room_id, self.floor_index)
			return
		
		#缓存
		global DeepHell_Role_Dict
		DeepHell_Role_Dict[self.role_id] = self
		
		#同步更新可进入房间缓存
		global DeepHell_AreaNextRoom_Dict
		self.room_obj.total_role_cnt += 1
		if self.room_obj.total_role_cnt >= self.room_obj.room_cfg.expectRoleCnt:
			DeepHell_AreaNextRoom_Dict[self.room_obj.room_cfg.roomAreaType] = self.room_obj.room_cfg.nextRoomID
		
		#缓存炼狱者对象
		if self.role and not self.role.IsKick():
			self.role.SetTempObj(EnumTempObj.DeepHellRole, self)
		
		#初始化完成 进入塔层
		self.join_floor()
	
	
	def join_floor(self):
		'''
		根据炼狱者数据 进入对应位置
		'''
		#直接通过塔层对象进入
		if not self.floor_obj:
			print "GE_EXC, DeepHell::DeepHellRole::join_floor,can not join floor while floor_obj is None"
			return
		
		#更新战斗数据
		self.update_fight_data()
		#塔层处理
		self.floor_obj.on_role_join(self, isReload = True)
		#CD处理
		if self.role and not self.role.IsKick():
			self.role.SetCD(EnumCD.DeepHellProtectCD, DeepHellDefine.DeepHell_ProtectCD_Init)
		#炼狱者状态
		self.state |= DeepHellDefine.STATE_ONLINE
		#清理离线状态
		if self.state & DeepHellDefine.STATE_OFFLINE:
			self.state -= DeepHellDefine.STATE_OFFLINE
		#设置头顶状态
		self.set_rolestatus(isFightStatus = True if (self.state & DeepHellDefine.STATE_FIGHT) else False)
		#同步客户端数据
		self.sync_role_data()
		#同步排行版
		self.sync_score_rank()

	
	def leave_floor(self):
		'''
		离开塔层 并没有去新的塔层
		'''
		#设置离线状态
		self.state |= DeepHellDefine.STATE_OFFLINE
		#取消role关联
		self.role = None
		
		#塔层对象 处理离场
		if not self.floor_obj:
			print "GE_EXC, DeepHell::DeepHellRole::leave_floor,can not join floor while floor_obj is None"
			return
		
		self.floor_obj.on_role_leave(self)
		
	
	def change_floor(self, step = 1):
		'''
		改变塔层 去到新的塔层
		@param step: 塔层位移 
		'''
		#塔层对象 处理离场
		if not self.floor_obj:
			print "GE_EXC, DeepHell::DeepHellRole::change_floor,can not change floor while floor_obj is None"
			return
		
		self.floor_obj.on_change_floor(self, step)
	
	
	def try_change_floor(self, isUp = True):
		'''
		战斗后尝试改变塔层
		@param isUp: true:去高层   False:坠落低层
		'''
		#第一层要下 最高层要上
		if (isUp and not self.floor_obj.floor_cfg.nextFloorIndex) or (isUp is False and not self.floor_obj.floor_cfg.lastFloorIndex):
			return
		
		self.change_floor(step = 1 if isUp else -1)
	
	
	
	def can_chanllenge(self, other_dh_role):
		'''
		是否可以挑战另外一个炼狱者
		'''
		if not self.can_join_fight(isAttacker = True) or not other_dh_role.can_join_fight():
			return False
		
		if self.floor_index != other_dh_role.floor_index or self.room_id != other_dh_role.room_id:
			return False
		
		return True
	
	
	def can_join_fight(self, isAttacker = False):
		'''
		判断炼狱者是否可以加入战斗
		'''
		if not IS_START or not IS_INIT:
			return False
		
		#关联role异常
		if not self.role or self.role.IsKick() or self.role.IsLost():
			return False
		
		#炼狱者状态 处于 离线 or 战斗 or 等待复活选项 不可挑战
		if self.state & DeepHellDefine.STATE_OFFLINE or self.state & DeepHellDefine.STATE_FIGHT or self.state & DeepHellDefine.STATE_WAITCHOICE:
			return False
		
#		if self.state != DeepHellDefine.STATE_ONLINE:
#			return False
		
		#角色状态不可进入战斗
		if not Status.CanInStatus(self.role, EnumInt1.ST_FightStatus):
			return False
		
		#战斗CD限制
		if isAttacker and self.role.GetCD(EnumCD.DeepHellFightCD):
			return False
		
		return True


	def join_fight(self):
		'''
		炼狱者进入战斗设置相关标记
		'''
		#已经掉线了
		if self.state & DeepHellDefine.STATE_OFFLINE:
			return False
		
		#战斗CD
		self.role.SetCD(EnumCD.DeepHellFightCD, DeepHellDefine.DeepHell_FightCD)
		#炼狱者战斗状态
		self.state |= DeepHellDefine.STATE_FIGHT
		#设置角色头顶状态
		self.set_rolestatus(isFightStatus = True)
		
		return True
	
	
	def update_fight_data(self):
		'''
		获取最新战斗数据
		'''
		self.fight_data = Middle.GetRoleData(self.role, use_property_X = True)
		
		
	def replace_fight_data(self, soul_fight_data):
		'''
		英魂战斗数据 转换为 自身战斗数据
		'''
		other_role_data, other_hero_data_dict = copy.deepcopy(soul_fight_data)
		own_role_data, own_hero_data_dict = copy.deepcopy(self.fight_data)
		
		#替换主角属性
		self.replace_role_pro(other_role_data, own_role_data)
		
		#替换英雄属性
		for own_hero_datas in own_hero_data_dict.itervalues():
			hero_career = own_hero_datas[Middle.Career]
			max_attack = None #[pos, attack]
			for pos, other_hero_datas in other_hero_data_dict.iteritems():
				if other_hero_datas[Middle.Career] != hero_career:
					continue
				if hero_career == 1:
					attack = other_hero_datas[Middle.AttackP]
				else:
					attack = other_hero_datas[Middle.AttackM]
				if not max_attack or attack > max_attack[1]:
					max_attack = [pos, attack]
			if max_attack:
				#查找到匹配的属性了
				self.replace_hero_pro(other_hero_data_dict[max_attack[0]], own_hero_datas)
		return own_role_data, own_hero_data_dict
	
	
	def replace_role_pro(self, other_data, own_data):
		'''
		属性替换 用别人的属性替换自己的属性
		'''
		own_data[Middle.HelpStationProperty] = other_data[Middle.HelpStationProperty]
		own_data[Middle.MaxHP] = other_data[Middle.MaxHP]
		own_data[Middle.Morale] = other_data[Middle.Morale]
		own_data[Middle.Speed] = other_data[Middle.Speed]
		own_data[Middle.AttackP] = other_data[Middle.AttackP]
		own_data[Middle.AttackM] = other_data[Middle.AttackM]
		own_data[Middle.DefenceP] = other_data[Middle.DefenceP]
		own_data[Middle.DefenceM] = other_data[Middle.DefenceM]
		own_data[Middle.Crit] = other_data[Middle.Crit]
		own_data[Middle.CritPress] = other_data[Middle.CritPress]
		own_data[Middle.AntiBroken] = other_data[Middle.AntiBroken]
		own_data[Middle.NotBroken] = other_data[Middle.NotBroken]
		own_data[Middle.Parry] = other_data[Middle.Parry]
		own_data[Middle.Puncture] = other_data[Middle.Puncture]
		own_data[Middle.DamageUpgrade] = other_data[Middle.DamageUpgrade]
		own_data[Middle.DamageReduce] = other_data[Middle.DamageReduce]
		own_data[Middle.DragonTrainProperty] = other_data[Middle.DragonTrainProperty]
	
	
	def replace_hero_pro(self, other_hero_data, own_hero_data):
		'''
		替换英雄属性
		'''
		own_hero_data[Middle.MaxHP] = other_hero_data[Middle.MaxHP]
		own_hero_data[Middle.Morale] = other_hero_data[Middle.Morale]
		own_hero_data[Middle.Speed] = other_hero_data[Middle.Speed]
		own_hero_data[Middle.AttackP] = other_hero_data[Middle.AttackP]
		own_hero_data[Middle.AttackM] = other_hero_data[Middle.AttackM]
		own_hero_data[Middle.DefenceP] = other_hero_data[Middle.DefenceP]
		own_hero_data[Middle.DefenceM] = other_hero_data[Middle.DefenceM]
		own_hero_data[Middle.Crit] = other_hero_data[Middle.Crit]
		own_hero_data[Middle.CritPress] = other_hero_data[Middle.CritPress]
		own_hero_data[Middle.AntiBroken] = other_hero_data[Middle.AntiBroken]
		own_hero_data[Middle.NotBroken] = other_hero_data[Middle.NotBroken]
		own_hero_data[Middle.Parry] = other_hero_data[Middle.Parry]
		own_hero_data[Middle.Puncture] = other_hero_data[Middle.Puncture]
		own_hero_data[Middle.DamageUpgrade] = other_hero_data[Middle.DamageUpgrade]
		own_hero_data[Middle.DamageReduce] = other_hero_data[Middle.DamageReduce]
	
	
	def after_fight_pve(self, isWin = True):
		'''
		挑战怪物之后
		'''
		#清除英魂
		self.fight_data_soul = None
		#清除战斗状态
		if self.state & DeepHellDefine.STATE_FIGHT:
			self.state -= DeepHellDefine.STATE_FIGHT
			
		#已经掉线了 直接算输了
		if self.state & DeepHellDefine.STATE_OFFLINE:
			if self.kill_cnt > DeepHellDefine.DeepHell_DropSoul_NeedCnt:
				self.drop_soul(GlobalPrompt.DeepHell_NPC_Name, self.kill_cnt)
			
			self.kill_cnt = 0
			self.be_kill_cnt += 1
			#输了并且不走运
			if random.randint(1,100) < self.floor_obj.floor_cfg.crashRate:
				self.try_change_floor(False)
			return
			
		if isWin is True:
			self.dh_score += self.floor_obj.floor_cfg.killBaseScore + self.kill_cnt * self.floor_obj.floor_cfg.killAddScore
			self.kill_cnt += 1
			self.total_kill_monster += 1
			self.cur_floor_kill_cnt += 1
			self.be_kill_cnt = 0
			self.room_obj.score_rank.HasData(self.role_id, self.get_rank_data())
			
			#取消保护CD
			self.role.SetCD(EnumCD.DeepHellProtectCD, 0)
				
			#连杀广播
			if self.kill_cnt % DeepHellDefine.DeepHell_RumorKill == 0:
				self.floor_obj.scene_obj.Msg(15, 0, GlobalPrompt.GetDeepHellKillRumor(self.role_name, self.kill_cnt))
		else:
			if self.kill_cnt > DeepHellDefine.DeepHell_DropSoul_NeedCnt:
				self.drop_soul(GlobalPrompt.DeepHell_NPC_Name, self.kill_cnt)
			
			self.kill_cnt = 0
			self.be_kill_cnt += 1
			
			#设置战斗保护CD
			self.role.SetCD(EnumCD.DeepHellProtectCD, DeepHellDefine.DeepHell_ProtectCD_Nomal)
		
		#输了并且不走运 或者 击杀数够了
		if (not isWin and random.randint(1,100) < self.floor_obj.floor_cfg.crashRate) or self.cur_floor_kill_cnt >= self.floor_obj.floor_cfg.maxKillCnt:
			self.try_change_floor(isWin)
		
		#设置头顶状态
		self.set_rolestatus()
		
		#同步最新数据
		self.sync_role_data()
	
	
	def after_fight_pvp(self, isWin = True, enemy_kill_cnt = 0):
		'''
		挑战结束
		''' 
		#清除英魂
		self.fight_data_soul = None
		#清除战斗状态
		if self.state & DeepHellDefine.STATE_FIGHT:
			self.state -= DeepHellDefine.STATE_FIGHT
			
		#已经掉线了 直接算输了
		if self.state & DeepHellDefine.STATE_OFFLINE:
			#清除英魂
			self.fight_data_soul = None
			self.kill_cnt = 0
			self.be_kill_cnt += 1
			#设置炼狱者状态
			self.state |= DeepHellDefine.STATE_WAITCHOICE
			#后续处理
			self.after_pvp_fail_wait_back(None, None, DeepHellDefine.DeepHell_ReviewChoice_No)
			return
		
		if isWin:
			self.dh_score += self.floor_obj.floor_cfg.killBaseScore + (self.kill_cnt + enemy_kill_cnt) * self.floor_obj.floor_cfg.killAddScore
			self.kill_cnt += 1
			self.total_kill_role += 1
			self.cur_floor_kill_cnt += 1
			self.be_kill_cnt = 0
			self.room_obj.score_rank.HasData(self.role_id, self.get_rank_data())
			
			#取消保护CD
			self.role.SetCD(EnumCD.DeepHellProtectCD, 0)
				
			#连杀广播
			if self.kill_cnt % DeepHellDefine.DeepHell_RumorKill == 0:
				self.floor_obj.scene_obj.Msg(15, 0, GlobalPrompt.GetDeepHellKillRumor(self.role_name, self.kill_cnt))
		else:
			self.kill_cnt = 0
			self.be_kill_cnt += 1
			
			#设置战斗保护CD
			self.role.SetCD(EnumCD.DeepHellProtectCD, DeepHellDefine.DeepHell_ProtectCD_Nomal)
		
		#设置头顶状态
		self.set_rolestatus()
		
		#杀够了
		if isWin:
			#同步客户端数据
			self.sync_role_data()
			#击杀数够 并且还有下一层
			if self.cur_floor_kill_cnt >= self.floor_obj.floor_cfg.maxKillCnt and self.floor_obj.floor_cfg.nextFloorIndex:
				# 击杀数够了
				self.try_change_floor(isUp = True)
				return
		else:
			#输了 等待复活选项
			#设置炼狱者状态
			self.state |= DeepHellDefine.STATE_WAITCHOICE
			if self.floor_index >= DeepHellDefine.DeepHell_ReviewTips_MinFloor:
				#同步回调
				self.role.SendObjAndBack(DeepHellCross_AfterPVPFailWait_SB, None, DeepHellDefine.DeepHell_AfterPVPFailWaitSec, self.after_pvp_fail_wait_back, DeepHellDefine.DeepHell_ReviewChoice_No)
			else:
				self.after_pvp_fail_wait_back(None,None, DeepHellDefine.DeepHell_ReviewChoice_No)
					
	
	def after_pvp_fail_wait_back(self, role, callArgvs = None, regParams = None):
		'''
		战败复活选项回调
		'''
		#非等待复活选项状态
		if not self.state & DeepHellDefine.STATE_WAITCHOICE:
			return
		
		#清理等待复活选项状态
		if self.state & DeepHellDefine.STATE_WAITCHOICE:
			self.state -= DeepHellDefine.STATE_WAITCHOICE
			
		#已经掉线了 当作不保层
		if self.state & DeepHellDefine.STATE_OFFLINE:
			if random.randint(1,100) < self.floor_obj.floor_cfg.crashRate:
				#输了并且不走运
				self.try_change_floor(isUp = False)
			else:
				#保层 or 运气好不坠落
				if self.role and not self.role.IsLost() and not self.role.IsKick():
					self.role.Revive(self.floor_obj.scene_id, *self.floor_obj.random_pos())
				#同步最新数据
				self.sync_role_data()
			return
		
		if callArgvs is None:
			#超时自回调
			choice = regParams
		else:
			#客户端回调
			choice = callArgvs
		
		#确保参数
		if choice != DeepHellDefine.DeepHell_ReviewChoice_No and choice != DeepHellDefine.DeepHell_ReviewChoice_Yes:
			choice = DeepHellDefine.DeepHell_ReviewChoice_No
			
		#没钱一边凉快
		if self.role.GetKuaFuMoney() < self.floor_obj.floor_cfg.noCrashNeedRMB:
			choice = DeepHellDefine.DeepHell_ReviewChoice_No
		
		#不保层
		if choice == DeepHellDefine.DeepHell_ReviewChoice_No and random.randint(1,100) < self.floor_obj.floor_cfg.crashRate:
			#输了并且不走运
			self.try_change_floor(isUp = False)
		else:
			#保层扣处跨服币
			if choice == DeepHellDefine.DeepHell_ReviewChoice_Yes:
				with Tra_DeepHell_ProtectReview:
					self.role.DecKuaFuMoney(self.floor_obj.floor_cfg.noCrashNeedRMB)
			#保层 or 运气好不坠落
			self.role.Revive(self.floor_obj.scene_id, *self.floor_obj.random_pos())
			#同步最新数据
			self.sync_role_data()
	
	
	def drop_soul(self, killer_name, terminal_kill):
		'''
		英魂掉落
		'''
		color = 1
		if 20 <= terminal_kill < 50:
			color = 2
		elif 50 <= terminal_kill:
			color = 3
		
		#刷出英魂NPC	
		pos_x, pos_y = self.floor_obj.random_pos()
		soul_npc = self.floor_obj.scene_obj.CreateNPC(DeepHellDefine.DeepHell_NPCSoulType, pos_x, pos_y, 1, 1, {EnumNPCData.EnNPC_Name:GlobalPrompt.DeepHell_BuffName % self.role_name, EnumNPCData.EnNPC_Color:color})
		soul_npc.SetPyDict(DeepHellDefine.IDX_MONSTER_SCENEID, self.floor_obj.scene_id)
		soul_npc.SetPyDict(DeepHellDefine.IDX_MASTER_FIGHTDATA, self.fight_data)
		soul_npc.SetPyDict(DeepHellDefine.IDX_MASTER_ROLENAME, self.role_name)
		#塔层内广播
		self.floor_obj.scene_obj.Msg(15, 0, GlobalPrompt.DeepHell_Msg_DropSoul % (killer_name, self.role_name, terminal_kill, pos_x, pos_y, pos_x, pos_y, self.role_name, self.role_name))
	
	
	def pick_soul(self, soul_fight_data, soul_role_name):
		'''
		拾取英魂
		'''
		#已经掉线了
		if self.state & DeepHellDefine.STATE_OFFLINE:
			return
		
		#拾取的时候打包一份战斗数据
		self.fight_data_soul = self.replace_fight_data(soul_fight_data)
		
		#拾取提示
		self.role.Msg(2, 0, GlobalPrompt.DeepHell_Tips_PickUpBuff % (soul_role_name, soul_role_name))
			
		self.floor_obj.scene_obj.Msg(15, 0, GlobalPrompt.DeepHell_Msg_PickUpBuffMsg % (self.role_name, soul_role_name))


	def get_sync_data(self):
		'''
		返回同步的数据
		'''
		return [ACTIVEID, self.floor_index,self.max_floor_history,self.cur_floor_kill_cnt,self.total_kill_role,self.total_kill_monster,self.dh_score, self.kill_cnt, self.room_id]
		
	
	def sync_role_data(self):
		'''
		同步角色炼狱数据
		'''
		if not self.role or self.role.IsLost() or self.role.IsKick():
			return
		
		self.role.SendObj(DeepHellCross_DHRoleData_S, self.get_sync_data())
	
	def sync_score_rank(self):
		'''
		同步房间排行榜		
		'''
		#已经掉线了
		if self.state & DeepHellDefine.STATE_OFFLINE:
			return
		
		self.role.SendObj(DeepHellCross_ScoreRank_S, self.room_obj.score_rank.data)
	
	
	def set_rolestatus(self, isFightStatus = False):
		'''
		根据连杀数 设置头顶状态
		'''
		#已经掉线了
		if self.state & DeepHellDefine.STATE_OFFLINE:
			return

		self.role.SetAppStatus(DeepHellConfig.GetStateByKillCnt(self.kill_cnt, 1 if isFightStatus else 0))
		
		
	def get_rank_data(self):
		'''
		返回排行数据
		格式 score, history_floor, role_id, role_name, zone_name
		'''
		return [self.dh_score, self.max_floor_history, self.role_id, self.role_name, self.zone_name]
	
	
	def display(self):
		'''
		打印数据
		'''
		print "room_id",self.room_id
		print "floor_index",self.floor_index
		print "dh_score",self.dh_score
		print "max_floor_history",self.max_floor_history
		print "total_kill_role",self.total_kill_role
		print "total_kill_monster",self.total_kill_monster
		print "kill_cnt",self.kill_cnt
		print "be_kill_cnt",self.be_kill_cnt
		print "cur_floor_kill_cnt",self.cur_floor_kill_cnt
		print "state",self.state


#===============================================================================
# 战斗
#===============================================================================	
def DeepHellPVE(DHRole, mcid, afterFightFun, afterPlayFun, param = None):
	'''
	深渊炼狱 打怪
	'''
	fight = Fight.Fight(DeepHellDefine.DeepHell_FightType_PVE)
	
	left_camp, right_camp = fight.create_camp()
	#左阵营
	if DHRole.fight_data_soul:
		left_camp.create_online_role_unit(DHRole.role, control_role_id = DHRole.role.GetRoleID(), fightData = DHRole.fight_data_soul)
	else:
		left_camp.create_online_role_unit(DHRole.role, control_role_id = DHRole.role.GetRoleID(), fightData = DHRole.fight_data)
	
	#连续被击杀，获得buff
	if DHRole.be_kill_cnt >= DeepHellDefine.DeepHell_Buff_NeedBeKillCnt:
		for u in left_camp.pos_units.itervalues():
			u.damage_upgrade_rate += DeepHellDefine.DeepHell_Buff_DamageUpgradeRate
			u.damage_reduce_rate += DeepHellDefine.DeepHell_Buff_DamageReduceRate
	
	#怪物阵营
	right_camp.create_monster_camp_unit(mcid)
	
	#回调及参数
	fight.after_fight_fun = afterFightFun
	fight.after_play_fun = afterPlayFun
	fight.after_fight_param = DHRole, param
	
	#炼狱者进入战斗
	if not DHRole.join_fight():
		return
	
	#启动
	fight.start()


def AfterFightPVE(fightObj):
	'''
	怪物挑战服务端计算完毕
	'''
	pass


def AfterPlayPVE(fightObj):
	'''
	怪物挑战客户端播放完毕
	'''
	if not IS_START or not IS_INIT:
		return
	
	DHRole, monster = fightObj.after_fight_param
	monsterInfoDict = monster.GetPyDict()
	if fightObj.result == 1:
		#删除怪物 同步塔层关联
		monsterInfoDict = monster.GetPyDict()
		DHRole.floor_obj.monster_index_set.discard(monsterInfoDict.get(DeepHellDefine.IDX_MONSTER_INDEX))
		monster.Destroy()		
	else:
		#删除没有头顶战斗状态的怪
		monster.Destroy()
	
		#原地创建有头顶战斗状态的怪
		npcType, npcPosX, npcPosY, direct = monsterInfoDict.get(DeepHellDefine.IDX_MONSTER_INFO)
		monster = DHRole.floor_obj.scene_obj.CreateNPC(npcType, npcPosX, npcPosY, direct, 1)
	
		#归整相关数据
		monster.SetPyDict(DeepHellDefine.IDX_ROOM_ID, monsterInfoDict.get(DeepHellDefine.IDX_ROOM_ID))
		monster.SetPyDict(DeepHellDefine.IDX_IN_FIGHT, True)
		monster.SetPyDict(DeepHellDefine.IDX_MONSTER_INFO,monsterInfoDict.get(DeepHellDefine.IDX_MONSTER_INFO))
		monster.SetPyDict(DeepHellDefine.IDX_MONSTER_INDEX, monsterInfoDict.get(DeepHellDefine.IDX_MONSTER_INDEX))
		monster.SetPyDict(DeepHellDefine.IDX_MONSTER_SCENEID, monsterInfoDict.get(DeepHellDefine.IDX_MONSTER_SCENEID))
	
	#炼狱者对象处理
	DHRole.after_fight_pve(True if fightObj.result == 1 else False)


def DeepHellPVP(left_dh_role, right_dh_role, AfterFightPVP, AfterPlayPVP):
	'''
	深渊炼狱 单挑
	'''
	fight = Fight.Fight(DeepHellDefine.DeepHell_FightType_PVP)
	left_camp, right_camp = fight.create_camp()
	
	#左阵营
	if left_dh_role.fight_data_soul:
		left_camp.create_online_role_unit(left_dh_role.role, control_role_id = left_dh_role.role.GetRoleID(), fightData = left_dh_role.fight_data_soul, use_px = True)
	else:
		left_camp.create_online_role_unit(left_dh_role.role, control_role_id = left_dh_role.role.GetRoleID(), fightData = left_dh_role.fight_data, use_px = True)
	
	#持续被击杀 获得buff
	if left_dh_role.be_kill_cnt >= DeepHellDefine.DeepHell_Buff_NeedBeKillCnt:
		for u in left_camp.pos_units.itervalues():
			u.damage_upgrade_rate += DeepHellDefine.DeepHell_Buff_DamageUpgradeRate
			u.damage_reduce_rate += DeepHellDefine.DeepHell_Buff_DamageReduceRate
	
	#右阵营
	if right_dh_role.fight_data_soul:
		right_camp.create_online_role_unit(right_dh_role.role, fightData = right_dh_role.fight_data_soul, use_px = True)
	else:
		right_camp.create_online_role_unit(right_dh_role.role, fightData = right_dh_role.fight_data, use_px = True)
	
	#持续被击杀 获得buff
	if right_dh_role.be_kill_cnt >= DeepHellDefine.DeepHell_Buff_NeedBeKillCnt:
		for u in right_camp.pos_units.itervalues():
			u.damage_upgrade_rate += DeepHellDefine.DeepHell_Buff_DamageUpgradeRate
			u.damage_reduce_rate += DeepHellDefine.DeepHell_Buff_DamageReduceRate
	
	#战斗回调
	fight.after_fight_fun = AfterFightPVP
	fight.after_play_fun = AfterPlayPVP
	fight.after_fight_param = left_dh_role, right_dh_role
	
	#炼狱者进入战斗
	if not left_dh_role.join_fight() or not right_dh_role.join_fight():
		return
	
	#启动战斗
	fight.start()
	

def AfterFightPVP(fightObj):
	'''
	深渊炼狱 单挑服务端完毕
	'''
	pass

def AfterPlayPVP(fightObj):
	'''
	深渊炼狱 客户端播放完毕
	'''
	if not IS_START or not IS_INIT:
		return
	
	left_dh_role, right_dh_role = fightObj.after_fight_param
	
	if fightObj.result == 1:
		#挑战者赢了
		PrcessAfterPlayPVP(left_dh_role, right_dh_role)
	elif fightObj.result == 0:
		#平局
		PrcessAfterPlayPVP(left_dh_role, right_dh_role, all_loser = True)
	else:
		#挑战者输了
		PrcessAfterPlayPVP(right_dh_role, left_dh_role)


def PrcessAfterPlayPVP(win_dh_role, lose_dh_role, all_loser = False):
	'''
	战斗结果处理
	@param win_dh_role: 赢家
	@param lose_dh_role: 输家
	@param all_loser: 平局都是输家
	'''
	if all_loser:
		#平局 都是输
		#A英魂掉落
		if win_dh_role.kill_cnt >= DeepHellDefine.DeepHell_DropSoul_NeedCnt:
			win_dh_role.drop_soul(lose_dh_role.role_name, win_dh_role.kill_cnt)
		
		#B英魂掉落
		if lose_dh_role.kill_cnt >= DeepHellDefine.DeepHell_DropSoul_NeedCnt:
			lose_dh_role.drop_soul(win_dh_role.role_name, lose_dh_role.kill_cnt)
			
		win_dh_role.after_fight_pvp(isWin = False)
		lose_dh_role.after_fight_pvp(isWin = False)
	else:
		#有输有赢
		#B英魂掉落
		if lose_dh_role.kill_cnt >= DeepHellDefine.DeepHell_DropSoul_NeedCnt:
			lose_dh_role.drop_soul(win_dh_role.role_name, lose_dh_role.kill_cnt)
			
		win_dh_role.after_fight_pvp(isWin = True, enemy_kill_cnt = lose_dh_role.kill_cnt)
		lose_dh_role.after_fight_pvp(isWin = False)


#===============================================================================
# 辅助
#===============================================================================
def RealInitActive(callArgvs = None, regParams = None):
	'''
	启动活动
	'''
	global IS_INIT
	IS_INIT = True
	
	#广播
	cRoleMgr.Msg(11, 0, GlobalPrompt.DeepHell_Msg_RealStart)


def EndDeepHell(callArgvs = None, regParams = None):
	'''
	活动结束
	'''
	global IS_INIT, CAN_IN,TIMESTAMPEND
	if not IS_INIT:
		return 
	IS_INIT = False
	CAN_IN = False
	TIMESTAMPEND = 0
	
	global DeepHell_Room_Dict
	for _, roomObj in DeepHell_Room_Dict.iteritems():
		roomObj.end_process()
	
	
def InitMonsterClickFun():
	'''
	初始化怪物点击处理
	'''
	#塔层怪物点击回调
	for monsterType in DeepHellConfig.DeepHell_MonsterType_Set:
		NPCServerFun.RegNPCServerOnClickFunEx(monsterType, ClickMonster)
	
	#英魂NPC点击回调
	NPCServerFun.RegNPCServerOnClickFunEx(DeepHellDefine.DeepHell_NPCSoulType, ClickMonsterSoul)


def ClickMonster(role, monster):
	'''
	角色点击怪物处理
	'''
	roleId = role.GetRoleID()
	DHRole = DeepHell_Role_Dict.get(roleId, None)
	if not DHRole:
		return
	
	#怪物在战斗
	monsterInfoDict = monster.GetPyDict()
	if monsterInfoDict.get(DeepHellDefine.IDX_IN_FIGHT, False):
		role.Msg(2, 0, GlobalPrompt.DeepHell_Tips_MonsterInFight)
		return
	
	#关联
	if not DHRole.role:
		DHRole.role = role
	
	#已经掉线了
	if DHRole.state & DeepHellDefine.STATE_OFFLINE:
		return
	
	#战斗CD限制
	fightSecs = role.GetCD(EnumCD.DeepHellFightCD)
	if fightSecs:
		role.Msg(2, 0, GlobalPrompt.DeepHell_Tips_InFightCD % fightSecs)
		return
	
	#炼狱者状态不可进入战斗
	if not DHRole.can_join_fight():
		return
	
	#怪物不在角色场景
	if role.GetSceneID() != monsterInfoDict.get(DeepHellDefine.IDX_MONSTER_SCENEID,None):
		return
	
	#确保关联
	if not role.GetTempObj(EnumTempObj.DeepHellRole):
		role.SetTempObj(EnumTempObj.DeepHellRole, DHRole)
	
	#删除没有头顶战斗状态的怪
	monster.Destroy()
	
	#原地创建有头顶战斗状态的怪
	npcType, npcPosX, npcPosY, direct = monsterInfoDict.get(DeepHellDefine.IDX_MONSTER_INFO)
	monster = DHRole.floor_obj.scene_obj.CreateNPC(npcType, npcPosX, npcPosY, direct, 1, {EnumNPCData.EnNPC_Statu : EnumRoleStatus.GT_NPC})
	
	#归整相关数据
	monster.SetPyDict(DeepHellDefine.IDX_ROOM_ID, monsterInfoDict.get(DeepHellDefine.IDX_ROOM_ID))
	monster.SetPyDict(DeepHellDefine.IDX_IN_FIGHT, True)
	monster.SetPyDict(DeepHellDefine.IDX_MONSTER_INFO,monsterInfoDict.get(DeepHellDefine.IDX_MONSTER_INFO))
	monster.SetPyDict(DeepHellDefine.IDX_MONSTER_INDEX, monsterInfoDict.get(DeepHellDefine.IDX_MONSTER_INDEX))
	monster.SetPyDict(DeepHellDefine.IDX_MONSTER_SCENEID, monsterInfoDict.get(DeepHellDefine.IDX_MONSTER_SCENEID))
	
	#战斗处理
	DeepHellPVE(DHRole, DeepHellDefine.DeepHeel_MCID, AfterFightPVE, AfterPlayPVE, monster)


def ClickMonsterSoul(role, soulMonster):
	'''
	点击英魂处理
	'''
	if not IS_INIT or not IS_START:
		return
	
	DHRole = role.GetTempObj(EnumTempObj.DeepHellRole)
	if not DHRole:
		DHRole = DeepHell_Role_Dict.get(role.GetRoleID(),None)
		if not DHRole:
			return
	
	#战斗状态中不能拾取
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	#当前已经有英魂
	if DHRole.fight_data_soul:
		role.Msg(2, 0, GlobalPrompt.DeepHell_Tips_PickUpBuffFail)
		return
	
	#战斗数据
	monsterInfoDict = soulMonster.GetPyDict()
	fight_data = monsterInfoDict.get(DeepHellDefine.IDX_MASTER_FIGHTDATA)
	if not fight_data:
		return
	
	master_role_name = monsterInfoDict.get(DeepHellDefine.IDX_MASTER_ROLENAME)
	if not master_role_name:
		return
	
	#删除npc
	soulMonster.Destroy()
	
	DHRole.pick_soul(fight_data, master_role_name)
	

def ReviveDeepHell(role, callArgvs = None, regParams = None):
	'''
	进入深渊炼狱
	'''
	if not Environment.IsCross:
		return
	
	if not IS_START:
		return
	
	if not CAN_IN:
		return
	
	global DeepHell_Role_Dict
	dh_role = DeepHell_Role_Dict.get(role.GetRoleID())
	if dh_role:
		#双向关联
		dh_role.role = role
		role.SetTempObj(EnumTempObj.DeepHellRole, dh_role)
		#炼狱者对象处理
		dh_role.join_floor()
		#暂未集结完毕 同步倒计时间戳
		if not IS_INIT:
			role.SendObj(DeepHellCross_RealTimeStamp_S, TIMESTAMPSTART)
		return
		
	#第一次进来,根据等级划分战区并进入到房间
	roomAreaType = DeepHellConfig.GetAreaTypeByLevel(role.GetLevel()) 
	if roomAreaType not in DeepHell_Room_Dict:
		print "GE_EXC,DeepHell::ReviveDeepHell, roomAreaType(%s) not in DeepHell_Room_Dict" % roomAreaType
		return
	
	if roomAreaType not in DeepHell_AreaNextRoom_Dict:
		print "GE_EXC, DeepHellCross::ReviveDeepHell,roomAreaType(%s) error" % roomAreaType
		return
	
	DeepHellRole(role, regParams, DeepHell_AreaNextRoom_Dict[roomAreaType], DeepHellDefine.DEFAULT_FLOOR)
	
	#暂未集结完毕 同步倒计时间戳
	if not IS_INIT:
		role.SendObj(DeepHellCross_RealTimeStamp_S, TIMESTAMPSTART)
	

#===============================================================================
# 活动控制
#===============================================================================
def OpenActive(callArgvs = None, regParams = None):
	'''
	深渊炼狱_开启活动_跨服
	'''
	global IS_START, ACTIVEID
	if IS_START:
		print "GE_EXC,repeat open DeepHellCross"
		return
	
	IS_START = True
	ACTIVEID = regParams
	
	
def CloseActive(callArgvs = None, regParams = None):
	'''
	深渊炼狱_结束活动_跨服
	'''
	global IS_START, ACTIVEID
	if not IS_START:
		print "GE_EXC,repeat close DeepHellCross"
		return
	
	IS_START = False
	ACTIVEID = regParams
	
	global DeepHell_AreaNextRoom_Dict, DeepHell_Role_Dict, DeepHell_Room_Dict
	DeepHell_AreaNextRoom_Dict.clear()
	DeepHell_Role_Dict.clear()
	DeepHell_Room_Dict.clear()
	

def InitActive(callArgvs = None, regParams = None):
	'''
	深渊炼狱_启动_跨服
	'''
	global IS_START, ACTIVEID, CAN_IN
	if not IS_START:
		print "GE_EXC,can not InitActive while IS_START is False"
		return
	
	if ACTIVEID != regParams:
		print "GE_EXC, can not InitActive while ACTIVEID(%s) != regParams(%s)" % (ACTIVEID, regParams)
		return 
	
	CAN_IN = True
	
	#创建所有房间
	global DeepHell_Room_Dict
	global DeepHell_AreaNextRoom_Dict
	for roomId, roomCfg in DeepHellConfig.DeepHell_RoomConfig_Dict.iteritems():
		DeepHell_Room_Dict[roomId] = DeepHellRoom(roomCfg)
		
		#默认先从小ID的房间开始进入
		areaType = roomCfg.roomAreaType
		if areaType not in DeepHell_AreaNextRoom_Dict or roomId < DeepHell_AreaNextRoom_Dict[areaType]:
			DeepHell_AreaNextRoom_Dict[areaType] = roomId
			
	global TIMESTAMPEND
	TIMESTAMPEND = DeepHellDefine.DeepHell_ActiveSeconds + cDateTime.Seconds()
	cNetMessage.PackPyMsg(DeepHellCross_EndTimeStamp_S, TIMESTAMPEND)
	cRoleMgr.BroadMsg()
	
	#注册开打
	cComplexServer.RegTick(DeepHellDefine.DeepHell_RealStartDelaySec, RealInitActive)
	#注册结束
	cComplexServer.RegTick(DeepHellDefine.DeepHell_ActiveSeconds, EndDeepHell)
	
	#更新时间戳
	global TIMESTAMPSTART
	TIMESTAMPSTART = cDateTime.Seconds() + DeepHellDefine.DeepHell_RealStartDelaySec
	
	cNetMessage.PackPyMsg(DeepHellCross_RealTimeStamp_S, TIMESTAMPSTART)
	cRoleMgr.BroadMsg()
	

#===============================================================================
# 客户端请求
#===============================================================================
def OnRequestBack(role, msg = None):
	'''
	深渊炼狱跨服_请求离开跨服回到本服
	'''
	dh_role = role.GetTempObj(EnumTempObj.DeepHellRole)
	if dh_role:
		dh_role.leave_floor()
	
	role.SetTempObj(EnumTempObj.DeepHellRole, None)
	
	#回去本服
	role.GotoLocalServer(None, None)


def OnChanllenge(role, msg):
	'''
	深渊炼狱跨服_请求挑战玩家
	@param msg: right_role_id
	'''
	if not IS_START or not IS_INIT:
		return
	
	right_role_id = msg
	right_dh_role = DeepHell_Role_Dict.get(right_role_id, None)
	if not right_dh_role:
		return
	
	#对手已经掉线了
	if right_dh_role.state == DeepHellDefine.STATE_OFFLINE:
		return
	
	if not right_dh_role.role or right_dh_role.role.IsLost() or right_dh_role.role.IsKick():
		role.Msg(2, 0, GlobalPrompt.DeepHell_Tips_TargetOffLine)		
		return
	
	#对手保护CD
	protectSecs = right_dh_role.role.GetCD(EnumCD.DeepHellProtectCD)
	if protectSecs:
		role.Msg(2, 0, GlobalPrompt.DeepHell_Tips_InProtectCD % protectSecs)
		return
	
	#不能挑战自己
	if role.GetRoleID() == right_role_id:
		return
	
	left_dh_role = role.GetTempObj(EnumTempObj.DeepHellRole)
	if not left_dh_role:
		left_dh_role = DeepHell_Role_Dict.get(role.GetRoleID(), None)
		if not left_dh_role:
			return
		else:
			role.SetTempObj(EnumTempObj.DeepHellRole, left_dh_role)
	
	if not left_dh_role.can_chanllenge(right_dh_role):
		return
	
	DeepHellPVP(left_dh_role, right_dh_role, AfterFightPVP, AfterPlayPVP)


#===============================================================================
# 事件
#===============================================================================
def OnClientLost(role, param = None):
	'''
	客户端掉线处理   or 角色掉线处理
	'''
	dh_role = role.GetTempObj(EnumTempObj.DeepHellRole)
		
	if dh_role:
		#处于等待复活选项状态 直接默认不保层
		if dh_role.state & DeepHellDefine.STATE_WAITCHOICE:
			dh_role.after_pvp_fail_wait_back(None, None, DeepHellDefine.DeepHell_ReviewChoice_No)
		dh_role.leave_floor()
	else:
		pass
		
	
	role.SetTempObj(EnumTempObj.DeepHellRole, None)
	
	
def OnSyncRoleOtherData(role, param = None):
	'''
	角色上限同步活动状态
	'''
	if IS_START:
		role.SendObj(DeepHellCross_ActiveState_S, (IS_START, IS_INIT, ACTIVEID))
	
	if TIMESTAMPEND > 0:
		role.SendObj(DeepHellCross_EndTimeStamp_S, TIMESTAMPEND)

if "_HasLoad" not in dir():
	if Environment.HasLogic and Environment.IsCross and cProcess.ProcessID == Define.GetDefaultCrossID():
		InitMonsterClickFun()
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_ClientLost, OnClientLost)
		Event.RegEvent(Event.Eve_BeforeExit, OnClientLost)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DeepHellCross_OnRequestBack", "深渊炼狱跨服_请求离开跨服回到本服"), OnRequestBack)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("DeepHellCross_OnChanllenge", "深渊炼狱跨服_请求挑战玩家"), OnChanllenge)
		