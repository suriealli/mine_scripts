#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.RoleGM")
#===============================================================================
# 角色GM指令
#===============================================================================
import os
import Environment
import cRoleMgr
import cProcess
from Common.Message import AutoMessage
from Common.Other import EnumSocial, EnumGameConfig, GlobalPrompt
from ComplexServer.Plug.DB import DBHelp
from ComplexServer.GMEXE import *
from Game.Role import Call
from Game.Marry import MarryConfig
from Game.Role.Base import LevelEXP
from Game.SystemRank import SystemRank
from Game.SysData import WorldData, WorldDataNotSync
from Game.Role.Config import RoleBaseConfig, RoleConfig
from Game.Role.Data import EnumTempObj, EnumInt32, EnumInt16,\
	EnumInt8, EnumObj, EnumInt1
from ThirdLib import PinYin
from Game.SuperCards import SuperCards

Tips = "你的帐号有问题，麻烦马上找程序查询"

ROLE_LOCALS = {}
JTFightViewData = None

def OnRoleGM(role, msg):
	import Environment
	assert Environment.IsDevelop
	
	IpNameDict = {"192.168.8.239":"xiechen",
				"192.168.8.221":"xiedaojian",
				"192.168.8.60":"liangzhaoguo",
				"192.168.8.222":"caijie",
				"192.168.8.42":"tansonghui",
				}
	
	backfunid, gmcommand = msg
	if "role.SetDI32(11" in gmcommand:
		#设置等级的指令禁用，直接封号
		role.Msg(4, 0, Tips)
		role.SetCanLoginTime(200000000)
		return
	# 上下文环境
	localdict = ROLE_LOCALS.setdefault(role.GetRoleID(), {})
	localdict["role"] = role
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	ipport = role.RemoteEndPoint()
	
	main_con = DBHelp.ConnectGlobalWeb()
	with main_con as main_cur:
		main_cur.execute("select name from computer where ip = '%s';" % ipport)
		main_result = main_cur.fetchall()
		if main_result and main_result[0]:
			PinYin.Load()
			ipname = "_".join(PinYin.GetPinYin(main_result[0][0]))
			PinYin.Release()
		else:
			ipname = IpNameDict.get(ipport, 'client ?')
		
	# 执行之
	with AutoLog.AutoTransaction(AutoLog.traRoleGM):
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveRoleGM, gmcommand)
		with OutBuf.OutBuf() as GF:
			gmIsTrue = False
			if gmcommand.startswith("@"):
				gmcommand = gmcommand[1:]
				for _role in cRoleMgr.GetAllRole():
					localdict["role"] = _role
					try:
						exec(gmcommand, globals(), localdict)
						gmIsTrue = True
					except:
						traceback.print_exc()
			else:
				try:
					exec(gmcommand, globals(), localdict)
					gmIsTrue = True
				except:
					traceback.print_exc()
					print "GE_EXC, GM error by roleId (%s)" % role.GetRoleID()
			outerr = GF.get_value()
			GF.pprint(str((roleId, ipport, ipname)))
			GF.pprint("gm-->\n")
			GF.pprint(gmcommand)
			GF.pprint("\n")
			GF.pprint(outerr)
			role.CallBackFunction(backfunid, outerr)
			
			if "ToTime" in gmcommand:
				tips = "++++++++玩家【%s】 ToTime 了   +++ " % roleName
				cRoleMgr.Msg(1, 0, tips)
		
		if not Environment.IsWindows:
			return
		
		#文件在项目的根目录下
		fileName = os.sep.join([os.path.splitdrive(os.getcwd())[0]] + os.path.splitdrive(os.getcwd())[1].split(os.sep)[1:-1] + ['File', 'GM_Log_%s.txt'  % cProcess.ProcessID])
		if os.path.exists(fileName) and os.path.getsize(fileName) <= 1024 * 1024 * 10:
			mode = 'a'
		else:
			#文件超过10m了的话删除文件
			mode = 'w'
		with open(fileName, "%s" % mode) as gmLog:
			if gmIsTrue:
				gmLog.write('time:' + str(cDateTime.Now()) + '\tname:' + ipname + '\tip:' + ipport + '\tcommand:' + gmcommand + "\tcorrect\n\n")
			else:
				gmLog.write('time:' + str(cDateTime.Now()) + '\tname:' + ipname + '\tip:' + ipport + '\tcommand:' + gmcommand + "\terror\n\n")
		
def GMRMB(role, rmb):
	if Environment.IsCross:
		print "GE_EXC, gm rmb in cross (%s), (%s)" % (role.GetRoleID(), rmb)
		return
	import Game.ThirdParty.QPointShop as A
	if rmb < 100:
		return
	goods = "7*100*%s" % (rmb / 100)
	A.OnDeliverGoods(role, goods)
	role.IncI32(EnumInt32.DayBuyUnbindRMB_Q, rmb)


def SaveData():
	'''
	强制保存服务器持久化数据
	'''
	from Game.File import Base
	for fo in Base.KeyDict.itervalues():
		fo.SaveData()

def SaveRole(role):
	from Game import Login
	Login.SaveRole(role)

def ShowCallbackFunction(key = ""):
	'''
	显示服务器的所有回调函数信息
	@param key:
	'''
	from Util import Callback
	lcbs = Callback.CallBackDict.values()
	lcbs.sort(key=lambda it:it.key)
	for lcb in lcbs:
		lcb.ShowFunction(key)

def SendMail(role, title, sender, content, items=None, tarotList=None, money=0, exp=0, tili=0, bindrmb=0, unbindrmb=0, contribution=0):
	'''
	发送邮件
	@param role:角色
	@param title:标题
	@param sender:发送者
	@param content:内容
	@param items:物品
	@param money:钱
	@param reputation:声望
	@param contribution:贡献
	@param bindrmb:绑元宝(魔晶)
	'''
	from Game.Role.Mail import Mail
	Mail.SendMail(role.GetRoleID(), title, sender, content, items, tarotList, money, exp, tili, bindrmb, unbindrmb, contribution=contribution)

def FightExample(role):
	from Game.Fight import FightExample
	FightExample.DoOneFight(role)

ACTIVE_SKILL = None
PASSIVE_SKILL = None

def FightSkill(active_skill = None, passive_skill = None):
	global ACTIVE_SKILL, PASSIVE_SKILL
	ACTIVE_SKILL = active_skill
	PASSIVE_SKILL = passive_skill

def ChangeFightSkill(role_data, hero_datas):
	from Game.Fight import Middle
	for hero_data in hero_datas.itervalues():
		if ACTIVE_SKILL:
			hero_data[Middle.NormalSkill] = ACTIVE_SKILL
			hero_data[Middle.ActiveSkill] = ACTIVE_SKILL
		if PASSIVE_SKILL:
			hero_data[Middle.PassiveSkills] = [PASSIVE_SKILL]

def FightSelf(role):
	'''
	和自己战斗
	@param role:角色
	'''
	from Game.Fight import Fight, Middle
	fight = Fight.Fight(0)
	fight.pvp = True
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	with Middle.RDH(ChangeFightSkill):
		left_camp.create_online_role_unit(role, role.GetRoleID(), use_px = True)
		right_camp.create_outline_role_unit(Middle.GetRoleData(role, True))
	fight.start()

MORAL_DICT = {}
def FightMonster(role, *mcids):
	from Game.Fight import Fight, Middle
	fight = Fight.Fight(0)
	left_camp, right_camp = fight.create_camp()
	left_camp.bind_moral(MORAL_DICT)
	with Middle.RDH(ChangeFightSkill):
		left_camp.create_online_role_unit(role, role.GetRoleID())
	for mcid in mcids:
		right_camp.create_monster_camp_unit(mcid)
	fight.buy_life_fun = BuyLife
	fight.buy_role = role
	fight.start()

def FightPVP(role):
	roles = cRoleMgr.GetAllRole()
	if len(roles) < 2:
		return
	from Game.Fight import Fight, Middle
	fight = Fight.Fight(0)
	fight.pvp = True
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(role, role.GetRoleID(), None, True)
	right_camp.create_outline_role_unit(Middle.GetRoleData(role, True), 0)
	for _role in roles[:2]:
		if _role == role:
			continue
		left_camp.create_online_role_unit(_role, role.GetRoleID(), None, True)
		right_camp.create_outline_role_unit(Middle.GetRoleData(_role, True), 0)
		break
	fight.start()

def FightPVPVeiw(role):
	roles = cRoleMgr.GetAllRole()
	if len(roles) < 3:
		return
	from Game.Fight import Fight, Middle
	fight = Fight.Fight(0)
	fight.save_fight_veiw_data = True
	fight.pvp = True
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(role, role.GetRoleID(), None, True)
	right_camp.create_outline_role_unit(Middle.GetRoleData(role, True), 0)
	for _role in roles[:2]:
		if _role == role:
			continue
		left_camp.create_online_role_unit(_role, role.GetRoleID(), None, True)
		right_camp.create_outline_role_unit(Middle.GetRoleData(_role, True), 0)
		break
	fight.start()


def FightLOL(roleIds):
	from Game.Fight import Fight
	fight = Fight.Fight(174)
	fight.restore = True
	left_camp, right_camp = fight.create_camp()

	for index, roleId in enumerate(roleIds):
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if role:
			left_camp.create_online_role_unit(role, role.GetRoleID(), use_px = True, team_pos_index = index + 1)
	
	for mcid in [7123,7124,7125]:
		right_camp.create_monster_camp_unit(mcid)
	fight.start()

	fight.after_fight_fun = AfterFight

def AfterFight(fight):
	print fight.right_camp.wheels
	
def FightGVE(role, *mcids):
	from Game.Fight import Fight
	fight = Fight.Fight(0)
	fight.pvp = False
	fight.group = True
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	left_camp.create_online_role_unit(role, role.GetRoleID(), None, True)
	cnt = 1
	for _role in cRoleMgr.GetAllRole():
		if _role == role:
			continue
		left_camp.create_online_role_unit(_role, _role.GetRoleID(), None, True)
		cnt += 1
		if cnt >= 3:
			break
	for mcid in mcids:
		right_camp.create_monster_camp_unit(mcid)
	fight.start()

def FightGVG(role):
	from Game.Fight import Fight
	fight = Fight.Fight(0)
	fight.pvp = True
	fight.group = 3
	fight.restore = True
	left_camp, right_camp = fight.create_camp()
	
	roles = cRoleMgr.GetAllRole()
	roles.remove(role)
	if len(roles) < 3:
		return
	left_camp.create_online_role_unit(role, role.GetRoleID(), None, True, 1)
	left_camp.create_online_role_unit(roles[0], roles[0].GetRoleID(), None, True, 2)
	right_camp.create_online_role_unit(roles[1], roles[1].GetRoleID(), None, True, 1)
	right_camp.create_online_role_unit(roles[2], roles[2].GetRoleID(), None, True, 2)
	
	fight.start()

def FightJT(roleId1, roleId2):
	role1 = cRoleMgr.FindRoleByRoleID(roleId1)
	if not role1:
		print "no role1"
		return
	role2 = cRoleMgr.FindRoleByRoleID(roleId2)
	if not role2:
		print "no role2"
		return
	if roleId1 == roleId2:
		print " role1 == role2"
		return
	
	jtobj1 = role1.GetJTObj()
	jtobj2 = role2.GetJTObj()
	if not jtobj1 or not jtobj2:
		print "no jteam"
		return
	
	if not jtobj1.CanJoinCross() or not jtobj2.CanJoinCross():
		print "no members"
		return
	
	leftRoles = []
	for roleId in jtobj1.members.keys():
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if not role:
			print "no members"
			return
		leftRoles.append(role)
	
	rightRoles = []
	for roleId in jtobj2.members.keys():
		role = cRoleMgr.FindRoleByRoleID(roleId)
		if not role:
			print "no members"
			return
		rightRoles.append(role)
	
	from Game.Fight import Fight
	fight = Fight.Fight(151)
	fight.restore = False
	fight.group_need_hero = True
	left_camp, right_camp = fight.create_camp()
	
	for index, fightRole in enumerate(leftRoles):
		left_camp.create_online_role_unit(fightRole, fightRole.GetRoleID(), use_px = True, role_realfight_pos = index + 1)
	
	for index, fightRole in enumerate(rightRoles):
		right_camp.create_online_role_unit(fightRole, fightRole.GetRoleID(), use_px = True, role_realfight_pos = index + 1)
	
#	import Game.Fight.SkillBase as b
#	for u in left_camp.pos_units.itervalues():
#		u.new_passive_skill(1002,1)
#		#u.passive_skills.append(b.PASSIVE_SKILLS.get(1002))
#		
#	for u in right_camp.pos_units.itervalues():
#		u.new_passive_skill(1002,1)
		
	fight.on_leave_fun = None			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterViewFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = None		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = None

	fight.start()

def AfterViewFight(fightobj):
	global JTFightViewData
	JTFightViewData = fightobj.GetViewData()
	
def ViewJTFight(role):
	global JTFightViewData
	if not JTFightViewData:
		print "not fight data"
		return
	from Game.Fight import Fight
	initdata, veiwdata = JTFightViewData
	role.SendObj(Fight.Fight_Init, initdata)
	for data in veiwdata:
		role.SendObj(Fight.Fight_List, data)

def BuyLife(fight):
	from Game.Fight import Middle
	role = fight.buy_role
	fight.left_camp.create_outline_role_unit(Middle.GetRoleData(role), role.GetRoleID())
	for unit in fight.left_camp.pos_units.itervalues():
		unit.create()

def FightEnd(role, result = 1):
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if not camp:
		return
	camp.fight.end(result)

def FightHP(role, jap):
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if not camp:
		return
	for unit in camp.pos_units.values():
		unit.change_hp(jap)

def FightMoral(role, jap):
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if not camp:
		return
	for unit in camp.pos_units.values():
		unit.change_moral(jap)

def FightCamp(role):
	return role.GetTempObj(EnumTempObj.FightCamp)

def FightUnit(role):
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if not camp:
		return None
	return camp.fight.get_only_control_main_unit(role.GetRoleID())

def ShowCRole():
	'''
	显示控制进程的玩家关系
	'''
	from Control import RoleMgr
	for cr in RoleMgr.ControlRoles.itervalues():
		print cr.role_id, cr.role_info, cr.friends
	print "--------------------------------------"
	for role_id, d in RoleMgr.WatchRoles.iteritems():
		print "* ", role_id
		for cr in d.itervalues():
			print "--->", cr.role_id, cr.role_info, cr.friends

def DebugRole(role, b = True):
	'''
	调试角色，显示该角色的所有通信
	@param role:角色
	@param b:调试开关
	'''
	from Game.Role import Debug
	if b:
		Debug.DebugRoleID.add(role.GetRoleID())
	else:
		Debug.DebugRoleID.discard(role.GetRoleID())

def ClearDebugRole():
	from Game.Role import Debug
	Debug.DebugRoleID = set()

def DebugLog(b = True):
	'''
	调试日志，显示没有事务的日志
	@param b:调试开关
	'''
	from ComplexServer.Plug.DB import DBProxy
	DBProxy.TraceEmptyTransaction = b

def Msg(role, cnt):
	'''
	测试所有的消息显示
	@param role:角色
	@param cnt:
	'''
	for idx in xrange(cnt):
		role.Msg(idx, 0, str(idx))



def CreateNPC(role):
	from Game.NPC import EnumNPCData
	scene = role.GetScene()
	posX, posY = role.GetPos()
	npc = scene.CreateNPC(2001, posX, posY, 1, 0, {EnumNPCData.EnNPC_Name : role.GetRoleName()})
	
	print "BLue CreateNPC", npc.GetNPCID()

def ChangeNPC(role ,npcId):
	from Game.NPC import EnumNPCData
	scene = role.GetScene()
	npc = scene.SearchNPC(npcId)
	npc.SetPySyncDict(EnumNPCData.EnNPC_Name, "changeOK")
	npc.AfterChange()

def SliceTable():
	'''
	强行切表
	'''
	from ComplexServer.Plug.DB import LogTable
	cnt = LogTable.SliceCount
	LogTable.SliceCount = 0
	LogTable.SliceTable()
	LogTable.SliceCount = cnt

def SuperRole(role):
	role.GetTempObj(26).role_propertyGather.total_p.p_dict[4] = 999999999
	role.GetTempObj(26).role_propertyGather.total_p.p_dict[6] = 999998999
	role.GetTempObj(26).role_propertyGather.total_p.p_dict[1] = 999998999
	role.GetTempObj(26).role_propertyGather.total_p_m.p_dict[1]= 999998999
	role.GetTempObj(26).role_propertyGather.total_p_m.p_dict[4]= 999998999
	role.GetTempObj(26).role_propertyGather.total_p_m.p_dict[6]= 999998999
	for i in range(4,16):
		role.GetTempObj(26).role_propertyGather.total_p_m.p_dict[i]= 1999998999

def SetHP(role, hp1, hp2):
	role.GetPropertyGather().total_p.p_dict[1] = hp1
	role.GetPropertyGather().total_p_m.p_dict[1] = hp1
	for hero in role.GetAllHero().itervalues():
		hero.GetPropertyGather().total_p.p_dict[1] = hp2
		hero.GetPropertyGather().total_p_m.p_dict[1] = hp2

def RMBBankStore(role, storeGrade):
	from Common.Message import PyMessage
	from Common.Other import EnumGameConfig
	from ComplexServer.Plug.Control import ControlProxy
	from Game.GlobalData import ZoneName
	from Game.Activity.RMBBank import RMBBank, RMBBankConfig
	
	roleID = role.GetRoleID()
	roleName = role.GetRoleName()
	
	cfg = RMBBankConfig.RMBBankGrade_Dict.get(storeGrade)
	if not cfg:
		print "GE_EXC, RoleGM RMBBankStore error storeGrade (%s)" % storeGrade
		return
	storeRMB = cfg.RMB_Q
	
	if roleID in RMBBank.RMBBankDict and \
		(RMBBank.RMBBankDict[roleID][1] + cfg.RMB_Q > EnumGameConfig.RMBBankMax or
		RMBBank.RMBBankDict[roleID][2] == set(RMBBankConfig.RMBBankRate_Dict.keys())):
		print "GE_EXC, RoleGM RMBBankStore store too much or reward already award all"
		return
	
	if roleID not in RMBBank.RMBBankDict:
		RMBBank.RMBBankDict[roleID] = {1: storeRMB, 2 :set()}
	else:
		RMBBank.RMBBankDict[roleID][1] += storeRMB
	role.SendObj(RMBBank.RMBBankData, RMBBank.RMBBankDict[roleID])
	
	#[存放, 服务器名字, 角色名字, 存放神石数, 0]
	record = [1, ZoneName.ZoneName, roleName, storeRMB, 0]
	#更新本地缓存
	if len(RMBBank.RMBBankRecordList) >= 100:
		#超过一百条, 删除前面的
		RMBBank.RMBBankRecordList.pop( 0)
	RMBBank.RMBBankRecordList.append(record)
	role.SendObj(RMBBank.RMBBankSingleRecord, record)
	
	ControlProxy.SendControlMsg(PyMessage.Control_AddBankLog, record)
	
def HaoqiFillRMB(role, fillRMB):
	#豪气冲天充值
	from Game.Activity.Haoqi import HaoqiMgr
	HaoqiMgr.AfterChangeUnbindRMB_Q(role, (fillRMB, fillRMB + fillRMB))



def SetJTScore(role, score):
	#设置跨服积分
	import Environment
	if not Environment.IsCross:
		print "GE_EXC, SetJTScore onle cross can use this"
		return
	
	jtobj = role.GetTempObj(EnumTempObj.CrossJTeamObj)
	if not jtobj:
		print "GE_EXC, SetJTScore  jtobj is None"
		return 
	jtobj.teamScore = score
	jtobj.UpdataSave()
	jtobj.SyncDataToRole(role)

def SetJTRoleScore(role, score):
	#设置个人积分
	import Environment
	if not Environment.IsCross:
		print "GE_EXC, SetJTRoleScore onle cross can use this"
		return
	
	jtobj = role.GetTempObj(EnumTempObj.CrossJTeamObj)
	if not jtobj:
		print "GE_EXC, SetJTRoleScore jtobj is None"
		return
	
	memberdata = jtobj.members.get(role.GetRoleID())
	if memberdata:
		memberdata[7] = min(max((memberdata[7] + score), 800), 3000)
	jtobj.UpdataSave()
	jtobj.SyncDataToRole(role)

def DismissUnion(roleId):
	from Game.Union import UnionMgr
	
	#需要角色在线
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if not role:
		return
	
	unionId = role.GetUnionID()
	unionObj = UnionMgr.GetUnionObjByID(unionId)
	if not unionObj:
		return
	
	#开服时间限制(开服三天内使用)
	if WorldData.GetWorldKaiFuDay() >= 3:
		return
	
	#添加时间限制(20~22点不能解散公会)
	hour = cDateTime.Hour()
	if hour >= UnionMgr.UNION_ACT_START_HOUR and hour < UnionMgr.UNION_ACT_END_HOUR:
		return
	
	#T掉所有公会成员
	for memberId in unionObj.members.iterkeys():
		#离线命令
		Call.LocalDBCall(memberId, UnionMgr.BeKicked, None)
		
	#清空公会成员字典
	unionObj.members.clear()
		
	#删除阵营中的公会
	UnionMgr.DelUnionInCamp(unionObj)
	#删除公会
	unionObj.HasDelete()
	
	#删除缓存的公会对象
	if unionId in UnionMgr.UNION_OBJ_DICT:
		del UnionMgr.UNION_OBJ_DICT[unionId]
	
def ToLevel32AndSetRandomVIP(roleId):
	#需要角色在线
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if not role:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel >= 32:
		return
	
	#设置等级
	from Game.Role.Config import RoleConfig
	for l in xrange(roleLevel, 32):
		exp = RoleConfig.LevelExp_Dict.get(l)
		role.IncExp(exp)
	
	#随机贵族
	import random
	vip = random.randint(1, 3)
	role.SetVIP(vip)
	

def RevertQinmi(role, param = None):
	if WorldDataNotSync.HasQiMiRevert(role.GetRoleID()):
		print "GE_EXC, repeat RevertQinmi", role.GetRoleID()
		return
	nowLevel = role.GetI16(EnumInt16.QinmiLevel)
	nowGrade = role.GetI8(EnumInt8.QinmiGrade)
	
	totalQinmi = role.GetI32(EnumInt32.Qinmi)
	initLevel = 0
	initGrade = 0
	while initLevel < nowLevel:
		levelCfg = MarryConfig.Qinmi_Dict.get(initLevel)
		if not levelCfg:
			print 'GE_EXC, RevertQinmi levelCfg error %s' % nowLevel
			return
		totalQinmi += levelCfg.needQinmi
		initLevel += 1
	
	while initGrade < nowGrade:
		gradeCfg = MarryConfig.QinmiGrade_Dict.get(initGrade)
		if not gradeCfg:
			print 'GE_EXC, RevertQinmi gradeCfg error %s' % nowLevel
			return
		totalQinmi += gradeCfg.needQinmi
		initGrade += 1
		
	if totalQinmi < 100000:
		print 'GE_EXC, RevertQinmi error role id :%s' % role.GetRoleID()
		return
	
	totalQinmi -= 100000
	
	initLevel = 0
	initGrade = 0
	wcnt = 1000
	while wcnt:
		canContinue = True
		while True:
			cfg = MarryConfig.Qinmi_Dict.get(initLevel)
			if not cfg:
				print 'GE_EXC, RevertQinmi can not find qinmi level %s' % initLevel
				return
			
			if cfg.nextLevel == -1:
				print 'GE_EXC, RevertQinmi cfg.nextLevel == -1 role id %s' % role.GetRoleID()
				return
			if cfg.needQinmiGrade > initGrade:
				break
			
			if totalQinmi < cfg.needQinmi:
				canContinue = False
				break
			
			totalQinmi -= cfg.needQinmi
			initLevel += 1
		
		if canContinue is False:
			break
		isGradeUp = False
		while True:
			cfg = MarryConfig.QinmiGrade_Dict.get(initGrade)
			if not cfg:
				print 'GE_EXC, RevertQinmi RequestUpGrade can not find qinmi grade %s' % initGrade
				return
			
			if cfg.maxLevel == initGrade:
				print 'GE_EXC, RevertQinmi cfg.maxLevel == initGrade %s' % role.GetRoleID()
				return
			
			if nowLevel < cfg.needQinmiLevel:
				if isGradeUp is False:
					canContinue = False
				break
			
			if totalQinmi < cfg.needQinmi:
				canContinue = False
				break
			
			if role.GetLevel() < cfg.needRoleLevel:
				canContinue = False
				break
			
			totalQinmi -= cfg.needQinmi
			initGrade += 1
			isGradeUp = True
		
		if canContinue is False:
			break
		wcnt -= 1
	
	if wcnt <= 0:
		print "GE_EXC, revert while error"
	
	role.SetI32(EnumInt32.Qinmi, totalQinmi)
	role.SetI16(EnumInt16.QinmiLevel, initLevel)
	role.SetI8(EnumInt8.QinmiGrade, initGrade)
	WorldDataNotSync.AddQiMiRevert(role.GetRoleID())
	
	if role.GetRoleID() in SystemRank.QM.data:
		SystemRank.QM.data[role.GetRoleID()] = [role.GetRoleName(), initLevel, totalQinmi, role.GetLevel(), role.GetExp(), 0]
		SystemRank.QM.BuildMinValue()
		
	role.ResetGlobalQinmiProperty()
	role.ResetGlobalQinmiGradeProperty()
	
	
	otherRoleId = role.GetObj(EnumObj.MarryObj)[1]
	if not otherRoleId:
		print "GE_EXC, revert qinmi not otherroleid"
		return
	if WorldDataNotSync.HasQiMiRevert(otherRoleId):
		return
	Call.LocalDBCall(otherRoleId, RevertQinmi, None)


def LoadConfig(fileName = "GSS.txt"):
	import DynamicPath
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("GSS")
	from Util.File import TabFile
	class GSS(TabFile.TabLine):
		FilePath = FILE_FOLDER_PATH.FilePath(fileName)
		def __init__(self):
			self.cnt = int
			self.role_id = int
	
	roleDict = {}
	for rowItems in GSS.ToClassType():
		if rowItems.role_id in roleDict:
			print "error"
		roleDict[rowItems.role_id] = rowItems.cnt
	
	return roleDict


def RevertGSEX():
	roleDict = LoadConfig()
	for roleId, cnt in roleDict.iteritems():
		Call.DBCall(roleId, RevertGS, cnt)
	

def RevertGS(role, cnt):
	with AutoLog.AutoTransaction(AutoLog.traRoleCommand):
		rmb = 200 * cnt
		if role.GetBindRMB() < rmb:
			role.SetBindRMB(0)
		else:
			role.DecBindRMB(rmb)
		
		itemCnt1 = role.ItemCnt(26042)
		if itemCnt1 < cnt:
			role.DelItem(26042, itemCnt1)
		else:
			role.DelItem(26042, cnt)
		
		itemCnt2 = role.ItemCnt(26144)
		if itemCnt2 < cnt * 20:
			role.DelItem(26144, itemCnt2)
		else:
			role.DelItem(26144, cnt * 20)
		
		itemCnt3 = role.ItemCnt(25600)
		if itemCnt3 < cnt * 20:
			role.DelItem(25600, itemCnt3)
		else:
			role.DelItem(25600, cnt * 20)
		
		AutoLog.LogBase(role.GetRoleID(), 30146, cnt)



def RevertMount(role, evolveId):
	from Game.Mount import MountConfig
	config = MountConfig._MOUNT_EVOLVE.get(evolveId)
	if not config:
		print "GE_EXC, not this id"
		return
	
	role.SetI16(EnumInt16.MountEvolveID, evolveId)
	role.SetI32(EnumInt32.MountExp, 0)
	
	
	if evolveId < 11:
		return
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	config = MountConfig._MOUNT_EVOLVE.get((evolveId - 1) / 10 * 10 )
	maxId = config.NextID
	for mid in range(1, 10):
		if mid <= maxId:
			if mid not in mountMgr.MountId_list:
				mountMgr.MountId_list.append(mid)
			continue
		if mid not in mountMgr.MountId_list:
			continue
		mountMgr.MountId_list.remove(mid)
		if mid in mountMgr.MountAGDict:
			del mountMgr.MountAGDict[mid]
		
	role.SetRightMountID(1)
	role.SetI8(EnumInt8.LastMountID, 1)


def RevertMountAll(fileName = "zm.txt", bugroleName = "GSS.txt"):
	import DynamicPath
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("GSS")
	from Util.File import TabFile
	class zm(TabFile.TabLine):
		FilePath = FILE_FOLDER_PATH.FilePath(fileName)
		def __init__(self):
			self.mid = int
			self.role_id = int
	
	bugRole = LoadConfig(bugroleName)
	roleDict = {}
	for rowItems in zm.ToClassType():
		if rowItems.role_id not in bugRole:
			continue
		if rowItems.role_id in roleDict:
			print "error"
		roleDict[rowItems.role_id] = rowItems.mid
	
	return roleDict


def GetRevertPetConfig(fileName = "pq.txt"):
	import DynamicPath
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("GSS")
	from Util.File import TabFile
	class zm(TabFile.TabLine):
		FilePath = FILE_FOLDER_PATH.FilePath(fileName)
		def __init__(self):
			self.star = int
			self.role_id = int
	
	roleDict = {}
	for rowItems in zm.ToClassType():
		if rowItems.role_id in roleDict:
			print "GE_EXC, GetRevertPetConfig error"
		if rowItems.star < 1:
			continue
		roleDict[rowItems.role_id] = rowItems.star
	
	return roleDict

#MAX(当前星数-降低星数，MIN(2,当前星数))
def Revertpet(role, decstar):
	if decstar <= 0:
		return
	if role.GetLevel() < 70:
		return
	from Game.Pet import PetConfig
	from Game.Pet import PetBase
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	for petId, pet in petMgr.pet_dict.iteritems():
		petstar = max(pet.star - decstar, min(2, pet.star))
		#取下一个星级的属性
		petMaxPropertyConfig = PetConfig.PET_MAX_PROPERTY.get((pet.type, petstar - 1))
		if not petMaxPropertyConfig:
			print "GE_EXC, Revertpet error ", petId, role.GetRoleID()
			continue
		
		pet.star = petstar
		#获取当前星级的最低属性
		for pEnum in pet.property_dict.keys():
			pet.property_dict[pEnum] = petMaxPropertyConfig.property_dict[pEnum]
		#幸运值
		afterUpgradePetConfig = PetConfig.PET_BASE.get((pet.type, petstar))
		if afterUpgradePetConfig:
			for k in pet.lucky_dict.keys():
				pet.lucky_dict[k] = afterUpgradePetConfig.initLucky
		PetBase.RecountPropertyByPet(role, pet)


def LoadTarot(fileName = "tqq.txt"):
	import DynamicPath
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("GSS")
	from Util.File import TabFile
	class zm(TabFile.TabLine):
		FilePath = FILE_FOLDER_PATH.FilePath(fileName)
		def __init__(self):
			self.role_id = int
			self.bugCnt = int
			self.grade4 = int
			self.grade5 = int
			self.grade6 = int
	
	roleDict = {}
	for rowItems in zm.ToClassType():
		if rowItems.role_id in roleDict:
			print "GE_EXC, GetRevertPetConfig error"
		if rowItems.grade4 < 1 and rowItems.grade5 < 1 and rowItems.grade6 < 1:
			continue
		roleDict[rowItems.role_id] = (rowItems.bugCnt, {4:rowItems.grade4, 5:rowItems.grade5,6:rowItems.grade6})
	
	return roleDict


#最终等级=MAX(命魂当前等级-对应品质降低等级，MIN（2，命魂当前等级）)
def ReverTarot(role, param):
	bugCnt, gradeDict = param
	TM = role.GetTempObj(EnumTempObj.enTarotMgr)
	if bugCnt >= 20:
		for cardId in TM.tarotOwner_ID_Dict[1].keys():
			TM.DelPackageCard(cardId) 
	
	
	for td in TM.tarotOwner_ID_Dict.itervalues():
		for card in td.itervalues():
			if card.grade < 4:
				continue
			declevel = gradeDict.get(card.grade)
			if not declevel:
				continue
			
			level = max(card.level - declevel, min(2, card.level))
			card.level = level
			card.exp = 0
			card.real_property_value = 0
			card.real_property_value_2 = 0
	
	role.GetPropertyGather().ReSetRecountTarotFlag()




def GetRevertPetConfig_2(fileName = "petstar_qq.txt"):
	import DynamicPath
	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
	FILE_FOLDER_PATH.AppendPath("GSS")
	from Util.File import TabFile
	class zm(TabFile.TabLine):
		FilePath = FILE_FOLDER_PATH.FilePath(fileName)
		def __init__(self):
			self.star = int
			self.roleid = int
	
	roleDict = {}
	for rowItems in zm.ToClassType():
		if rowItems.roleid in roleDict:
			print "GE_EXC, GetRevertPetConfig_2 error"
		if rowItems.star < 1:
			continue
		roleDict[rowItems.roleid] = rowItems.star
	
	return roleDict


def RevertPet_2(role, Incstar):
	from Game.Pet import PetConfig
	from Game.Pet import PetBase
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	for petId, pet in petMgr.pet_dict.iteritems():
		if pet.star >= 5:
			continue
		petstar = min(5, pet.star + Incstar)
		#取下一个星级的属性
		petMaxPropertyConfig = PetConfig.PET_MAX_PROPERTY.get((pet.type, petstar - 1))
		if not petMaxPropertyConfig:
			print "GE_EXC, Revertpet error ", petId, role.GetRoleID()
			continue
		
		pet.star = petstar
		#获取当前星级的最低属性
		for pEnum in pet.property_dict.keys():
			pet.property_dict[pEnum] = petMaxPropertyConfig.property_dict[pEnum]
		#幸运值
		afterUpgradePetConfig = PetConfig.PET_BASE.get((pet.type, petstar))
		if afterUpgradePetConfig:
			for k in pet.lucky_dict.keys():
				pet.lucky_dict[k] = afterUpgradePetConfig.initLucky
		PetBase.RecountPropertyByPet(role, pet)


def GMDecMoney(role, money):
	if role.GetMoney() < money:
		role.SetMoney(0)
	else:
		role.DecMoney(money)

def SetGMFlag(roleId, boolFlag):
	'''
	设置GM标志
	@param roleId:
	@param boolFlag: True or False
	'''
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if not role:
		return
	
	role.SetI1(EnumInt1.GMRoleFlag, boolFlag)
	
	#设置聊天
	role.SetChatInfo(EnumSocial.RoleGMKey, boolFlag)

def SuperInvestInvest(role, investIndex):
	'''
	超级投资投资
	@param role:
	@param investIndex: 投资id
	'''
	from Game.Activity.SuperInvest import SuperInvest
	investObj = role.GetObj(EnumObj.SuperInvestObj)
	if not investObj:
		investObj = {}
	if investIndex not in investObj:
		investObj[investIndex] = {1:cDateTime.Days(), 2:set()}
	
	role.SetObj(EnumObj.SuperInvestObj, investObj)
	
	role.SendObj(SuperInvest.SuperInvestData, investObj)

def ClearPack(role):
	'''
	清空背包
	'''
	itemsDict = {}
	packMgr = role.GetTempObj(1)
	for _, v in packMgr.objIdDict.iteritems():
		coding, cnt = v.otype, v.oint
		if coding not in itemsDict:
			itemsDict[coding] = cnt
		else:
			itemsDict[coding] += cnt
	
	for coding, cnt in itemsDict.iteritems():
		role.DelItem(coding, cnt)
	
def ToLevelEx(role, level):
	'''升级不改变当前经验'''
	nowLevel = role.GetLevel()
	MAXLEVEL = RoleBaseConfig.ROLE_MAX_LEVEL
	if nowLevel >= MAXLEVEL:
		print 'GE_EXC, ToLevelEx now level %s is max by role id %s' % (nowLevel, role.GetRoleID())
		return
	toLevel = nowLevel + level
	if toLevel > MAXLEVEL:
		print 'GE_EXC, ToLevelEx to level %s > max level %s by role id %s, now level %s' % (toLevel, MAXLEVEL, role.GetRoleID(), nowLevel)
		toLevel = MAXLEVEL
	
	exp = RoleConfig.LevelExp_Dict.get(toLevel)
	if not exp:
		print 'GE_EXC, ToLevelEx can not find level (%s) in LevelExp_Dict by role id %s' % (toLevel, role.GetRoleID())
		return
	with ToLevelExGM_Log:
		#升级
		while nowLevel < toLevel:
			nowLevel += 1
			LevelEXP.LevelUp(role)

	
def BuySuperCards(role):
	if role.GetLevel() < EnumGameConfig.SuperCardsLvLimit:
		return
	
	cardsObj = role.GetObj(EnumObj.SuperCards)
	if not cardsObj:
		return
	
	nowDays = cDateTime.Days()
	
	if cardsObj.get(1):
		return
	cardsObj[1] = nowDays + 3650
	role.SetObj(EnumObj.SuperCards, cardsObj)
	
	#全服开启公会副本替身组队
	WorldData.SetSuperCardsUnionFB(1)
	
	role.SendObj(SuperCards.SuperCardsData, cardsObj)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.SuperCardsBuySucess2 % role.GetRoleName())
	
if "_HasLoad" not in dir():
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RMMsg_GM", "GM指令"), OnRoleGM)
	
	if Environment.HasLogic:
		ToLevelExGM_Log = AutoLog.AutoTransaction("ToLevelExGM_Log", "GM指令提升等级")
