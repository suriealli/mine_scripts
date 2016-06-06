#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HefuBoss.HefuBoss")
#===============================================================================
# 合服boss,为了安全，还是跟开服boss完全分开吧
#===============================================================================
import random
import cRoleMgr
import cSceneMgr
import cDateTime
import Environment
from Util import Time
from Game.Persistence import Contain
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import EnumGameConfig, GlobalPrompt, EnumFightStatistics, \
	EnumSysData
from Game.NPC import EnumNPCData
from Game.SysData import WorldData
from Game.Role import Status, Event
from Game.Role.Data import EnumInt1, EnumObj
from Game.Fight import FightEx
from Game.Team import EnumTeamType
from Game.Activity.HefuBoss import HefuBossConfig, HefuBossTeam

if "_HasLoad" not in dir():

	#消息
	Sync_HefuBoss_PersonnalWorship_Data = AutoMessage.AllotMessage("Sync_HefuBoss_PersonnalWorship_Data", "同步玩家膜拜大神数据")
	Sync_HefuBoss_Sever_Data = AutoMessage.AllotMessage("Sync_HefuBoss_Sever_Data", "同步合服boss全服数据")
	Sync_HefuBoss_SeverWorship_Data = AutoMessage.AllotMessage("Sync_HefuBoss_SeverWorship_Data", "同步合服boss全服膜拜人数")
	Sync_HefuBoss_PersonnalSeverAward_Data = AutoMessage.AllotMessage("Sync_HefuBoss_PersonnalSeverAward_Data", "同步合服boss玩家全服奖励数据")
	#日志
	Tra_HefuBoss_FightAward = AutoLog.AutoTransaction("Tra_HefuBoss_FightAward", "合服boss战斗胜利奖励")
	Tra_HefuBoss_SeverAward = AutoLog.AutoTransaction("Tra_HefuBoss_SeverAward", "合服boss全服奖励")
	Tra_HefuBoss_Worship = AutoLog.AutoTransaction("Tra_HefuBoss_Worship", "合服boss膜拜大神")
#===============================================================================
# 战斗相关
#===============================================================================
def RequestHefuBossFight(role, msg):
	'''
	客户端请求合服boss战斗
	@param role:
	@param msg:
	'''
	if not WorldData.IsHeFu():
		return
	bossid = msg
	#等级限制
	if bossid in The_Niubility_Dict:
		return
	if role.GetLevel() < EnumGameConfig.HefuBossNeedLevel:
		return
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	#战斗状态
	cfg = HefuBossConfig.HefuBossMonsterDict.get(bossid)
	if not cfg:
		print 'GE_EXC,error in cfg = HefuBossConfig.HefuBossMonsterDict.get(bossid)(%s)' % bossid
		return
	#这里写成按照合服的unix时间戳来判断合服时间
	Hefukey = WorldData.WD.get(EnumSysData.HeFuKey)
	#合服时间转换成unix时间
	HefuUnixTime = Time.DateTime2UnitTime(Hefukey)
	#当前时间转换成unix时间
	nowUnixtime = Time.DateTime2UnitTime(cDateTime.Now())
	#如果时间差大于限制的时间，天数转换成秒数， 就return掉 
	if nowUnixtime - HefuUnixTime > cfg.timeLimit * (60 * 60 * 24):
		return
	team = role.GetTeam()
	#组队
	if team:
		if len(team.members) == 1:
			return
		if team.team_type != EnumTeamType.T_HefuBoss:
			return
		if not Status.CanInStatus_Roles(team.members, EnumInt1.ST_FightStatus):
			return
		cfg = HefuBossConfig.HefuBossMonsterDict.get(bossid)
		if not cfg:
			print 'GE_EXC,error in cfg = HefuBossConfig.HefuBossMonsterDict.get(bossid)(%s)' % bossid
			return
		FightEx.PVE_KaifuBossTeam(team.leader, team.members, cfg.fightType, cfg.monsterCampIdList, HefuBossAfterFight, regParam=(bossid, cfg))
	#单挑
	else:
		if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
			return
		cfg = HefuBossConfig.HefuBossMonsterDict.get(bossid)
		if not cfg:
			print 'GE_EXC,error in cfg = HefuBossConfig.HefuBossMonsterDict.get(bossid)(%s)' % bossid
			return
		FightEx.PVE_KaifuBossSingle(role, cfg.fightType, cfg.monsterCampIdList, HefuBossAfterFight, regParam=(bossid, cfg))

def HefuBossAfterFight(fightObj):
	'''
	战斗结束回调 
	'''
	# 战斗失败
	if fightObj.result != 1:
		return
	bossid, cfg = fightObj.after_fight_param
	#被其他人抢先后通关
	if bossid in The_Niubility_Dict:
		return
	
	roles = fightObj.left_camp.roles
	if not roles:
		return
	
	role_data_dict = {}
	#单挑和非单挑的奖励是不一样的

	msg = ''

	if len(roles) == 1:
		items = []
		rewarditems = []
		member = list(roles)[0]
		with Tra_HefuBoss_FightAward:
			#这里存入打败合服boss的玩家的角色名，品阶，职业，性别，等级，以及雕像的位置，单个玩家的话雕像位置是0
			role_data_dict[member.GetRoleID()] = member.GetRoleName(), member.GetGrade(), member.GetCareer(), member.GetSex(), member.GetLevel(), 0
			for item in cfg.singlereward:
				member.AddItem(*item)
				rewarditems.append(item)
				items.append(GlobalPrompt.HefuBossItem_Tips % item)
			#持久化数据
			The_Niubility_Dict[bossid] = role_data_dict
			fightObj.set_fight_statistics(member.GetRoleID(), EnumFightStatistics.EnumItems, rewarditems)
			msg = msg + GlobalPrompt.HefuBossNiubilityNameTips % member.GetRoleName() + GlobalPrompt.HefuBossSingleTips % cfg.monsterName + GlobalPrompt.HefuBossSingleAwardTips + GlobalPrompt.HefuBossComma.join(items) + GlobalPrompt.HefuBossActiveSeverAward

	elif len(roles) > 1:
	#这里需要增加日志
		names = []
		items = []
		#将获胜的玩家列表按照等级进行排序，从高到底
		members = sorted(roles, key=lambda role:role.GetLevel(), reverse=True)
		#三个玩家的雕像位置分别是0,1,2
		sortdict = dict(zip(members, [0, 1, 2]))
		with Tra_HefuBoss_FightAward:
			for member in roles:
				names.append(GlobalPrompt.HefuBossNiubilityNameTips % member.GetRoleName())
				#这里存入打败合服boss的玩家的角色名，品阶，职业，性别，等级，以及雕像的位置，单个玩家的话雕像位置是0
				role_data_dict[member.GetRoleID()] = member.GetRoleName(), member.GetGrade(), member.GetCareer(), member.GetSex(), member.GetLevel(), sortdict.get(member)
				item = random.choice(cfg.singlereward)
				member.AddItem(*item)
				items.append(GlobalPrompt.HefuBossItem_Tips % item)
				fightObj.set_fight_statistics(member.GetRoleID(), EnumFightStatistics.EnumItems, [item])
		#持久化数据
		The_Niubility_Dict[bossid] = role_data_dict
		msg = msg + GlobalPrompt.HefuBossComma.join(names) + GlobalPrompt.HefuBossTeamTips % cfg.monsterName + GlobalPrompt.HefuBossTeamAwardTips + GlobalPrompt.HefuBossComma.join(items) + GlobalPrompt.HefuBossActiveSeverAward

	statue_cfg = HefuBossConfig.HefuBossStatuePosDict.get(bossid)
	if not statue_cfg:
		print 'GE_EXC,error in statue_cfg = HefuBossConfig.HefuBossStatuePosDict.get(bossid)(%s)' % statue_cfg
		return
	#创建雕像 
	#首先获取雕像位置
	pos = statue_cfg.pos
	if not pos:
		return
	SceneID = statue_cfg.sceneId
	#获取雕像所在的场景，如果没有的该场景的话就返回并打印异常 
	scene = cSceneMgr.SearchPublicScene(SceneID)
	if not scene:
		print 'Ge_EXC, no scene = cSceneMgr.SearchPublicScene(SceneID),(%s)in HefuBossAfterFight' % SceneID
		return
	for obj in role_data_dict.itervalues():
		name, _, career, sex, _ , indexid = obj
		#根据玩家的性别和职业来获取不同的雕像类型 
		npctype = HefuBossConfig.HefuBossStatueDict.get((career, sex))
		if not npctype:
			print 'GE_EXC, error in npctype = HefuBossConfig.HefuBossStatueDict.get((career, sex)),cannot find key (%s,%s)' % (career, sex)
			continue
		x, y, p = pos[indexid]
		#依次创建雕像
		scene.CreateNPC(npctype, x, y, p, 1, {EnumNPCData.EnNPC_Name : name})

	for member in roles:
		#同步给客户端
		member.SendObj(Sync_HefuBoss_Sever_Data, The_Niubility_Dict.data)

	cRoleMgr.Msg(1, 0, msg)

def RequestHefuBossSeverAward(role, msg):
	'''
	客户端请求获取全服奖励
	@param role:
	@param msg:
	'''
	if not WorldData.IsHeFu():
		return
	#玩家等级还不够
	if role.GetLevel() < EnumGameConfig.HefuBossNeedLevel:
		return
	bossid = msg
	#被打败过的boss才能领取全服奖励 
	if not bossid in The_Niubility_Dict:
		return
	#已经领取过该boss的全服奖励
	role_SeverAward_data = role.GetObj(EnumObj.HefuBossSeverAward)
	if bossid in role_SeverAward_data:
		return
	cfg = HefuBossConfig.HefuBossMonsterDict.get(bossid)
	if not cfg:
		print 'Ge_EXC,error in cfg = HefuBossConfig.HefuBossMonsterDict.get(bossid),no bossid(%s)' % bossid
		return
	if role.GetVIP() < cfg.allreward_vip:
		return
	cfg = HefuBossConfig.HefuBossMonsterDict.get(bossid)
	if not cfg:
		print 'GE_EXC,error in cfg = HefuBossConfig.HefuBossMonsterDict.get(bossid)(%s)' % bossid
		return
	tip = GlobalPrompt.HefuBossServerTips1 % role.GetRoleName()
	with Tra_HefuBoss_SeverAward:
		item_msg = []
		#记录玩家已经领取过这个bossid的全服奖励 
		role_SeverAward_data[bossid] = 1
		for item in cfg.allreward:
			role.AddItem(*item)
			item_msg.append(GlobalPrompt.HefuBossItem_Tips % item)
	tip = tip + GlobalPrompt.HefuBossComma.join(item_msg)
	niubilities_data = The_Niubility_Dict.get(bossid)
	tip = tip + GlobalPrompt.HefuBossServerTips2
	name_msg = []
	for obj in niubilities_data.itervalues():
			name, _, _, _, _ , _ = obj
			name_msg.append(GlobalPrompt.HefuBossNiubilityNameTips % name)
	tip = tip + GlobalPrompt.HefuBossComma.join(name_msg) + GlobalPrompt.HefuBossServerTips3 % cfg.monsterName
	role.SendObj(Sync_HefuBoss_PersonnalSeverAward_Data, role_SeverAward_data)
	cRoleMgr.Msg(1, 0, tip)

#===============================================================================
# 退出合服boss
#===============================================================================
def RequestQuitHefuboss(role, msg):
	'''
	客户端请求退出合服boss场景
	@param role:
	@param msg:
	'''
	team = role.GetTeam()
	#是否正在战斗状态
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	if team:
		team.Quit(role)
	if role.GetSceneID() == EnumGameConfig.HefuBossSceneId:
		role.BackPublicScene()

def QuitHefuboss(role, param):
	'''
	角色离线
	@param role:
	@param param:
	'''
	team = role.GetTeam()
	if team:
		if team.team_type != EnumTeamType.T_HefuBoss:
			return
		team.Quit(role)
	if role.GetSceneID() == EnumGameConfig.HefuBossSceneId:
		role.BackPublicScene()
#===============================================================================
# 膜拜大神相关
#===============================================================================
def RequestWorship(role, msg):
	'''
	客户端请求膜拜大神
	@param role:
	@param msg:
	'''
	if not WorldData.IsHeFu():
		return
	bossid = msg
	#等级限制
	if role.GetLevel() < EnumGameConfig.HefuBossNeedLevel:
		return
	#这个boss还没有被打败，不能膜拜
	if bossid not in HefuBossConfig.HefuBossMonsterDict:
		return
	#已经膜拜过
	role_Worship_data = role.GetObj(EnumObj.HefuBossWorship)
	if bossid in role_Worship_data:
		return
	with Tra_HefuBoss_Worship:
		role_Worship_data[bossid] = 1
		The_Worship_Dict.setdefault(bossid, 0)
		The_Worship_Dict[bossid] += 1
	#更新玩家的膜拜信息
	role.SendObj(Sync_HefuBoss_PersonnalWorship_Data, role_Worship_data)
	#更新全服务器膜拜的人数 
	role.SendObj(Sync_HefuBoss_SeverWorship_Data, The_Worship_Dict.data)
	#提示信息
	role.Msg(2, 0, GlobalPrompt.HefuBossWorshipTip)

#===============================================================================
# 数据库相关,在数据库载入后创建雕像 
#===============================================================================
def HefuBossAfterLoad():
	if not WorldData.WD.returnDB:
		return
	if not WorldData.IsHeFu():
		return
	if not The_Niubility_Dict.returnDB:
		return
	#这里创建雕像的步骤与战斗结束后的创建完全一致
	for bossid, role_data_dict in The_Niubility_Dict.data.iteritems():
		if not role_data_dict:
			print "GE_EXC, The_Niubility_Dict role_data_dict is None"
			continue
		statue_cfg = HefuBossConfig.HefuBossStatuePosDict.get(bossid)
		if not statue_cfg:
			print "GE_EXC HefuBossConfig not this cfg (%s)" % bossid
			continue
		#创建雕像 
		pos = statue_cfg.pos
		if not pos:
			print "GE_EXC HefuBossConfig not this cfg pos(%s)" % bossid
			continue
		SceneID = statue_cfg.sceneId
		scene = cSceneMgr.SearchPublicScene(SceneID)
		if not scene:
			print 'Ge_EXC, no scene = cSceneMgr.SearchPublicScene(SceneID),(%s)in HefuBossAfterLoad' % SceneID
			continue
		for obj in role_data_dict.itervalues():
			name, _, career, sex, _, indexid = obj
			npctype = HefuBossConfig.HefuBossStatueDict.get((career, sex))
			if not npctype:
				print 'GE_EXC, error in npctype = HefuBossConfig.HefuBossStatueDict.get((career, sex)),cannot find key %s' % (career, sex)
				continue
			x, y, p = pos[indexid]
			scene.CreateNPC(npctype, x, y, p, 1, {EnumNPCData.EnNPC_Name : name})

def OnAfterLoadWorldData(*param):
	HefuBossAfterLoad()

#===============================================================================
# 客户端显示相关
#===============================================================================
def RequestOpenHefuBoss(role, msg):
	'''
	客户端请求打开合服boss面板
	@param role:
	@param msg:
	'''
	if not WorldData.IsHeFu():
		return
	#发送消息
	role.SendObj(Sync_HefuBoss_Sever_Data, The_Niubility_Dict.data)
	role.SendObj(Sync_HefuBoss_PersonnalWorship_Data, role.GetObj(EnumObj.HefuBossWorship))
	role.SendObj(Sync_HefuBoss_SeverWorship_Data, The_Worship_Dict.data)
	role.SendObj(Sync_HefuBoss_PersonnalSeverAward_Data, role.GetObj(EnumObj.HefuBossSeverAward))
	HefuBossTeam.ShowTeams(role)


def SyncHefuBossData(role, param):
	if not WorldData.IsHeFu():
		return
	#发送消息,同步角色领取奖励和膜拜大神的情况
	role.SendObj(Sync_HefuBoss_Sever_Data, The_Niubility_Dict.data)
	role.SendObj(Sync_HefuBoss_PersonnalSeverAward_Data, role.GetObj(EnumObj.HefuBossSeverAward))

#===============================================================================
# 合服相关
#===============================================================================
def OnHefu(role, param):
	#合服后的处理,合服后把玩家领取全服奖励的数据和膜拜大神的数据都清空
	role.GetObj(EnumObj.HefuBossWorship).clear()
	role.GetObj(EnumObj.HefuBossSeverAward).clear()

if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb and not Environment.IsCross:
		#获胜的玩家信息存入此处
		The_Niubility_Dict = Contain.Dict("The_Niubility_Dict_Hefu", (2038, 1, 1), HefuBossAfterLoad, None, isSaveBig=False)
		#这里记录每个合服bossid被膜拜的次数 
		The_Worship_Dict = Contain.Dict("The_Worship_Dict_Hefu", (2038, 1, 1), None, None, isSaveBig=False)
	
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_ClientLost, QuitHefuboss)
		Event.RegEvent(Event.Eve_BeforeExit, QuitHefuboss)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncHefuBossData)
		Event.RegEvent(Event.Eve_AfterRoleHeFu, OnHefu)
		Event.RegEvent(Event.Eve_AfterLoadWorldData, OnAfterLoadWorldData)
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestHefuBossFight", "客户端请求挑战合服boss"), RequestHefuBossFight)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestHefuBossWorship", "客户端请求膜拜合服boss大神"), RequestWorship)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestHefuBossSeverAward", "客户端请求领取合服boss的全服奖励"), RequestHefuBossSeverAward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestOpenHefuBoss", "客户端请求打开合服boss面板"), RequestOpenHefuBoss)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestQuitHefuboss", "客户端请求退出合服boss"), RequestQuitHefuboss)
	
