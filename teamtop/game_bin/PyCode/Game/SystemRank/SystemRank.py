#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.SystemRank.SystemRank")
#===============================================================================
# 系统排行榜
#===============================================================================
import cDateTime
import cRoleMgr
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role import Event, RoleMgr
from Game.Persistence import Contain, BigTable
from Game.Role.Data import EnumObj, EnumDayInt8, EnumInt16, EnumInt32, EnumTempObj
from Game.Union import UnionMgr
from Game.SysData import WorldData
from Game.SystemRank import SystemRankBase

#入榜等级
RankNeedLevel = 25


if "_HasLoad" not in dir():
	
	HERO_ZDL_LIST = []	#缓存英雄战力排行榜100名
	
	Rank_Level_Request = AutoMessage.AllotMessage("Rank_Level_Request", "请求查看等级排行榜")
	Rank_Level_Notify = AutoMessage.AllotMessage("Rank_Level_Notify", "同步等级排行榜")

	Rank_ZDL_Request = AutoMessage.AllotMessage("Rank_ZDL_Request", "请求查看战斗力排行榜")
	Rank_ZDL_Notify = AutoMessage.AllotMessage("Rank_ZDL_Notify", "同步战斗力排行榜")
	
	Rank_Mount_Request = AutoMessage.AllotMessage("Rank_Mount_Request", "请求查看坐骑排行榜")
	Rank_Mount_Notify = AutoMessage.AllotMessage("Rank_Mount_Notify", "同步坐骑排行榜")
	
	Rank_Purgatory_Request = AutoMessage.AllotMessage("Rank_Purgatory_Request", "请求查看心魔炼狱排行榜")
	Rank_Purgatory_Notify = AutoMessage.AllotMessage("Rank_Purgatory_Notify", "同步心魔炼狱排行榜")

	Rank_Union_Notify = AutoMessage.AllotMessage("Rank_Union_Notify", "同步帮派排行榜")
	Rank_S_RoleFlowerData = AutoMessage.AllotMessage("Rank_S_RoleFlowerData", "同步角色送花记录")
	
	Rank_WeddingRing_Request = AutoMessage.AllotMessage("Rank_WeddingRing_Request", "请求查看婚戒排行榜")
	Rank_WeddingRing_Notify = AutoMessage.AllotMessage("Rank_WeddingRing_Notify", "同步婚戒排行榜")
	
	Rank_MarryQinmi_Request = AutoMessage.AllotMessage("Rank_MarryQinmi_Request", "请求查看亲密度排行榜")
	Rank_MarryQinmi_Notify = AutoMessage.AllotMessage("Rank_MarryQinmi_Notify", "同步亲密度排行榜")
	
	Rank_EquipmentGem_Request = AutoMessage.AllotMessage("Rank_EquipmentGem_Request", "请求查看宝石排行榜")
	Rank_EquipmentGem_Notify = AutoMessage.AllotMessage("Rank_EquipmentGem_Notify", "同步宝石排行榜排行榜")
	
	Rank_RoleZDL_Request = AutoMessage.AllotMessage("Rank_RoleZDL_Request", "请求查看主角战力排行榜")
	Rank_RoleZDL_Notify = AutoMessage.AllotMessage("Rank_RoleZDL_Notify", "同步主角战力排行榜排行榜")
	
	Rank_HeroZDL_Notify = AutoMessage.AllotMessage("Rank_HeroZDL_Notify", "同步英雄战力排行榜排行榜")
	
	Rank_TT_Request = AutoMessage.AllotMessage("Rank_TT_Request", "请求查看组队爬塔排行榜")
	Rank_TT_Notify = AutoMessage.AllotMessage("Rank_TT_Notify", "同步组队爬塔排行榜")
	
	Rank_UnionFB_Request = AutoMessage.AllotMessage("Rank_UnionFB_Request", "请求查看公会副本排行榜")
	Rank_UnionFB_Notify = AutoMessage.AllotMessage("Rank_UnionFB_Notify", "同步公会副本排行榜")

	
	#日志
	TraSendFlower = AutoLog.AutoTransaction("TraSendFlower", "送花")

#===============================================================================
# 外部接口
#===============================================================================
def GetRoleFlower(roleId):
	#获取这个玩家获得的鲜花
	return Role_Flower_Dict.get(roleId, 0)

def GetSortUnionList():
	#获取全服帮派排名[(id, level, exp, name, zdl)]
	uniondatas = []
	for unionId, unionObj in UnionMgr.UNION_OBJ_DICT.iteritems():
		uniondatas.append((unionId, unionObj.level, unionObj.exp, unionObj.name, unionObj.GetZDL()))
	uniondatas.sort(key = lambda u:(u[4], u[1], -u[0]), reverse = True)
	if len(uniondatas) > 100:
		uniondatas = uniondatas[0:100]
	return uniondatas

#===============================================================================
# 等级排行榜 value (name, level, zdl, flower, exp)
#===============================================================================
class LevelRank(SystemRankBase.SysRankBase):
	Msg_Init = Rank_Level_Notify			#同步客户端数据
	Msg_Open = Rank_Level_Request			#客户端打开排行榜
	name = "Rank_Level"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		level1 = v1[1]
		exp1 = v1[4]
		level2 = v2[1]
		exp2 = v2[4]
		if level1 < level2:
			return True
		elif level1 > level2:
			return False
		else:
			return exp1 < exp2



#===============================================================================
# 战斗力(历史最大值)排行榜 value (name, level, zdl, flower, roleId)
#===============================================================================
class ZDLRank(SystemRankBase.SysRankBase):

	Msg_Init = Rank_ZDL_Notify			#同步客户端数据
	Msg_Open = Rank_ZDL_Request			#客户端打开排行榜
	name = "Rank_ZDL"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[2] < v2[2]
	

#===============================================================================
# 坐骑排行榜 value (name, level, exp, flower, roleId)
#===============================================================================
class MountRank(SystemRankBase.SysRankBase):
	Msg_Init = Rank_Mount_Notify			#同步客户端数据
	Msg_Open = Rank_Mount_Request			#客户端打开排行榜
	name = "Rank_Mount"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		level1 = v1[1]
		exp1 = v1[2]
		level2 = v2[1]
		exp2 = v2[2]
		if level1 < level2:
			return True
		elif level1 > level2:
			return False
		else:
			return exp1 < exp2



#===============================================================================
# 心魔炼狱排行榜 value (name, purgatoryId, fightRound, flower)
#===============================================================================
class PurgatoryRank(SystemRankBase.SysRankBase):
	Msg_Init = Rank_Purgatory_Notify			#同步客户端数据
	Msg_Open = Rank_Purgatory_Request			#客户端打开排行榜
	
	name = "Rank_Purgatory"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		purgatoryId1 = v1[1]
		fightRound1 = v1[2]
		purgatoryId2 = v2[1]
		fightRound2 = v2[2]
		if purgatoryId1 < purgatoryId2:
			return True
		elif purgatoryId1 > purgatoryId2:
			return False
		else:
			return fightRound1 > fightRound2
	
#===============================================================================
# 婚戒排行榜 value (roleName, weddingRingID, exp, flower, roleId)
#===============================================================================
class WeddingRingRank(SystemRankBase.SysRankBase):
	Msg_Init = Rank_WeddingRing_Notify			#同步客户端数据
	Msg_Open = Rank_WeddingRing_Request			#客户端打开排行榜
	name = "Rank_WeddingRing"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		weddingRingID1 = v1[1]
		weddingRingExp1 = v1[2]
		weddingRingID2 = v2[1]
		weddingRingExp2 = v2[2]
		if weddingRingID1 < weddingRingID2:
			return True
		elif weddingRingID1 > weddingRingID2:
			return False
		else:
			return weddingRingExp1 <= weddingRingExp2
	
#===============================================================================
# 亲密度排行榜
#===============================================================================
class MarryQinMiRank(SystemRankBase.SysRankBase):
	Msg_Init = Rank_MarryQinmi_Notify			#同步客户端数据
	Msg_Open = Rank_MarryQinmi_Request			#客户端打开排行榜
	name = "Rank_MarryQinMi"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		qinmiLevel1 = v1[1]
		qinmiExp1 = v1[2]
		
		qinmiLevel2 = v2[1]
		qinmiExp2 = v2[2]
		
		if qinmiLevel1 < qinmiLevel2:
			return True
		elif qinmiLevel1 > qinmiLevel2:
			return False
		else:
			return qinmiExp1 < qinmiExp2



#===============================================================================
# 宝石排行榜
#===============================================================================
class EquipmentGemRank(SystemRankBase.SysRankBase):
	Msg_Init = Rank_EquipmentGem_Notify			#同步客户端数据
	Msg_Open = Rank_EquipmentGem_Request			#客户端打开排行榜
	name = "Rank_EquipmentGem"
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[1] < v2[1]
		


#===============================================================================
# 主角战斗力排行榜
#===============================================================================
class RoleZDLRank(SystemRankBase.SysRankBase):
	Msg_Init = Rank_RoleZDL_Notify			#同步客户端数据
	Msg_Open = Rank_RoleZDL_Request			#客户端打开排行榜
	name = "Rank_RoleZDL"
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[1] < v2[1]


#===============================================================================
# 组队爬塔排行榜 value (name, tIndex, score, fightround, zdl, flower)
#===============================================================================
class TeamTowerRank(SystemRankBase.SysRankBase):
	Msg_Init = Rank_TT_Notify				#同步客户端数据
	Msg_Open = Rank_TT_Request				#客户端打开排行榜
	name = "Rank_TeamTower"
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return (v1[1], -v1[2], -v1[3], v1[4]) < (v2[1], -v2[2], -v2[3], v2[4])


#===============================================================================
# 公会副本榜 value (name, 章节ID, 章节等级 , 章节进度, 公会等级, 工会经验, leader_id)
#===============================================================================
class UnionFBRank(SystemRankBase.SysRankBase):
	Msg_Init = Rank_UnionFB_Notify				#同步客户端数据
	Msg_Open = Rank_UnionFB_Request				#客户端打开排行榜
	name = "Rank_UnionFB"
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return (v1[1], v1[2], v1[3], v1[4], v1[5]) < (v2[1], v2[2], v2[3], v2[4], v2[5])


#===============================================================================
# 英雄战斗力排行榜
#===============================================================================
class HeroZDLRank(BigTable.BigTable):
	def SaveData(self):
		BigTable.BigTable.SaveData(self)
		
def UpdateRoleHeroZDL(role):
	#更新玩家的英雄战斗力
	if role.GetLevel() < 30:
		return
	
	herozdl_dict = role.GetHeroZDL()
	roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	heroList = []
	for hero in roleHeroMgr.HeroDict.itervalues():
		if hero.GetStationID() > 0:
			heroList.append(hero)
		else:
			continue
	if not heroList : return
	
	roleId = role.GetRoleID()
	role_name = role.GetRoleName()
	flower = GetRoleFlower(role.GetRoleID())
	hero_data = {}
	for hero in heroList:
		heroId = hero.GetHeroId()
		zdl = herozdl_dict.get(heroId, 0)
		data = [hero.GetHeroName(), zdl, hero.GetLevel(), hero.GetExp(), roleId, role_name, flower]
		
		hero_data[heroId] = data

	HEROZDL_BT.SetKeyValue(roleId, {'role_id':roleId, 'herodata':hero_data})
	
def HeroZDLAfterLoad():
	SortedHeroZDL()

def SortedHeroZDL():
	global HEROZDL_BT
	global HERO_ZDL_LIST
	
	db_data = HEROZDL_BT.GetData()
	herodict = {}
	for _, herodata in db_data.iteritems():
		herodict.update(herodata.get('herodata'))
	
	if not herodict: return
	
	herozdl_data = herodict.items()
	#根据英雄战力，等级，经验排序
	herozdl_data.sort(key = lambda x:(x[1][1],x[1][2],x[1][3], -x[1][4]), reverse = True)
	#截取前100个数据
	herozdl_data = herozdl_data[0:100]
	roleid_list = set()	#缓存前100英雄的玩家ID
	for data in herozdl_data:
		roleid_list.add(data[1][4])
	
	HERO_ZDL_LIST = herozdl_data
	#当玩家数大于100时，删除没有英雄在前100名的玩家
	if len(db_data) > 100:
		for roleId, _ in db_data.items():
			if roleId not in roleid_list:
				HEROZDL_BT.DelKey(roleId)
				
def RequestHeroZDLRank(role, param):
	'''
	请求查看英雄战力排行
	@param role:
	@param param:
	'''
	global HERO_ZDL_LIST
	
	role.SendObj(Rank_HeroZDL_Notify, HERO_ZDL_LIST)
#===============================================================================
# 更新函数
#===============================================================================
def UpdateLevelRank(role):
	if role.GetLevel() < RankNeedLevel:
		return
	LoginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
	account = LoginInfo.get("account", "")
	LR.HasData(role.GetRoleID(), [role.GetRoleName(), role.GetLevel(), role.GetZDL(), GetRoleFlower(role.GetRoleID()), role.GetExp(), role.GetQQLZ(), role.GetQQYLZ(), role.GetQQHHLZ(),account])

def UpdateZDLRank(role):
	if role.GetLevel() < RankNeedLevel:
		return
	ZR.HasData(role.GetRoleID(), [role.GetRoleName(), role.GetLevel(), role.GetZDL(), GetRoleFlower(role.GetRoleID()), role.GetRoleID(), role.GetQQLZ(), role.GetQQYLZ(), role.GetQQHHLZ()])

def UpdateMountRank(role):
	if role.GetLevel() < RankNeedLevel:
		return
	MR.HasData(role.GetRoleID(), [role.GetRoleName(), role.GetI16(EnumInt16.MountEvolveID), role.GetI32(EnumInt32.MountExp), GetRoleFlower(role.GetRoleID()), role.GetRoleID()])

def UpdatePurgatory(role, pId, fround):
	if role.GetLevel() < RankNeedLevel:
		return
	PR.HasData(role.GetRoleID(), [role.GetRoleName(), pId, fround, GetRoleFlower(role.GetRoleID()), role.GetQQLZ(), role.GetQQYLZ(), role.GetQQHHLZ()])

def UpdateTTRank(role, tindex, score, fround):
	if role.GetLevel() < RankNeedLevel:
		return
	TTR.HasData(role.GetRoleID(), [role.GetRoleName(), tindex, score, fround, role.GetZDL(), GetRoleFlower(role.GetRoleID())])

def UpdateUnionFBRank(unionObj):
	maxFBId, maxLevel, maxOccupation = unionObj.GetMaxOccupation()
	UFB.HasData(unionObj.union_id, [unionObj.name, maxFBId, maxLevel, maxOccupation, unionObj.level, unionObj.exp, unionObj.leader_id])

def UpdateWeddingRing(role):
	if role.GetLevel() < RankNeedLevel:
		return
	weddingRingID = role.GetI16(EnumInt16.WeddingRingID)
	if not weddingRingID:
		return
	WR.HasData(role.GetRoleID(), [role.GetRoleName(), weddingRingID, role.GetI32(EnumInt32.WeddingRingExp), GetRoleFlower(role.GetRoleID()), role.GetRoleID(), role.GetObj(EnumObj.MarryObj).get(1, 0)])

def UpdateMarryQinMi(role):
	if role.GetLevel() < RankNeedLevel:
		return
	QinmiLevel = role.GetI16(EnumInt16.QinmiLevel)
	QinmiExp = role.GetI32(EnumInt32.Qinmi)
	#无亲密不上榜
	if not QinmiLevel and not QinmiExp: return
	
	QM.HasData(role.GetRoleID(), [role.GetRoleName(), QinmiLevel, QinmiExp, role.GetLevel(), role.GetExp(), GetRoleFlower(role.GetRoleID())])
	
def UpdateEquipmentGem(role):
	if role.GetLevel() < RankNeedLevel:
		return
	gemLevel = role.GetTotalGemLevel()
	#无宝石不上榜
	if not gemLevel: return
	
	EG.HasData(role.GetRoleID(), [role.GetRoleName(), gemLevel, role.GetLevel(), role.GetExp(), GetRoleFlower(role.GetRoleID())])
	
def UpdateRoleZDL(role):
	if role.GetLevel() < RankNeedLevel:
		return
	roleZDL = role.GetRoleZDL()
	RZ.HasData(role.GetRoleID(), [role.GetRoleName(), roleZDL, role.GetLevel(), role.GetExp(), GetRoleFlower(role.GetRoleID())])

def UpdateRank(role):
	#判断是否是本服的玩家
	if not role.IsLocalServer():
		return
	if role.GetLevel() < RankNeedLevel:
		return
	UpdateLevelRank(role)
	UpdateZDLRank(role)
	UpdateMountRank(role)
	UpdateWeddingRing(role)
	UpdateEquipmentGem(role)
	UpdateMarryQinMi(role)
		
		
def UpdateRankFlower():
	RG = Role_Flower_Dict.get
	for roleId, rank_data in LR.data.items():
		rank_data[3] = RG(roleId, 0)
	
	for roleId, rank_data in ZR.data.items():
		rank_data[3] = RG(roleId, 0)
	
	for roleId, rank_data in MR.data.items():
		rank_data[3] = RG(roleId, 0)
		
	for roleId, rank_data in PR.data.items():
		rank_data[3] = RG(roleId, 0)
		
	for roleId, rank_data in WR.data.items():
		rank_data[3] = RG(roleId, 0)
#===============================================================================
#客户端消息
#===============================================================================
def SendFlower(role, msg):
	'''
	请求送花（这里现在是膜拜了）
	@param role:
	@param msg:
	'''
	backId, roleId = msg
	if role.GetRoleID() == roleId:
		return
	
	if role.GetDI8(EnumDayInt8.FlowerCnt) >= EnumGameConfig.FlowerMaxCnt:
		return
	
	roleIds = role.GetObj(EnumObj.FlowerRecord)[1]
	if roleId in roleIds:
		return
	totalMoney = EnumGameConfig.FlowerMoney * role.GetLevel()
	with TraSendFlower:
		role.IncDI8(EnumDayInt8.FlowerCnt, 1)
		roleIds.add(roleId)
		role.IncMoney(totalMoney)
	
	global Role_Flower_Dict
	Role_Flower_Dict[roleId] = Role_Flower_Dict.get(roleId, 0) + 1
	
	role.CallBackFunction(backId, roleId)
	
	role.Msg(2, 0, GlobalPrompt.SendFlower_Tips % totalMoney)
	

#===============================================================================
# 帮派排行榜 value (name, level, exp, leaderName, leaderId, flower, zdl)
#===============================================================================
SYSTEM_UNION_RANK_DICT = {}	#缓存公会排行数据
def RequestAllUnionRank(role, msg):
	'''
	请求帮派排行榜
	@param role:
	@param msg:
	'''
	global SYSTEM_UNION_RANK_DICT
	if not SYSTEM_UNION_RANK_DICT:
		uniondatas = []
		for unionId, unionObj in UnionMgr.UNION_OBJ_DICT.iteritems():
			uniondatas.append((unionId, unionObj.level, unionObj.exp, unionObj.name, unionObj.GetZDL(), unionObj.leader_name, unionObj.leader_id, GetRoleFlower(unionObj.leader_id)))
		uniondatas.sort(key = lambda u:(u[4], u[1], -u[0]), reverse = True)
		if len(uniondatas) > 100:
			uniondatas = uniondatas[0:100]
		SYSTEM_UNION_RANK_DICT = {}
		for data in uniondatas:
			SYSTEM_UNION_RANK_DICT[data[0]] = (data[3], data[1], data[2], data[5], data[6], data[7], data[4])
			
	role.SendObj(Rank_Union_Notify, SYSTEM_UNION_RANK_DICT)
	
#	for unionId, unionObj in UnionMgr.UNION_OBJ_DICT.iteritems():
#		sync_Dict[unionId] = (unionObj.name, unionObj.level, unionObj.exp, unionObj.leader_name, unionObj.leader_id, GetRoleFlower(unionObj.leader_id), unionObj.GetZDL())
#	role.SendObj(Rank_Union_Notify, sync_Dict)

#===============================================================================
#事件触发
#===============================================================================
def SyncRoleOtherData(role, param):
	#同步送花数据
	role.SendObj(Rank_S_RoleFlowerData, role.GetObj(EnumObj.FlowerRecord)[1])

def AfterLoadFlower():
	pass

def RoleDayClear(role, param):
	#每天清理送花记录
	role.SetObj(EnumObj.FlowerRecord, {1 : set()})

def FinishPurgatory(role, param):
	#通关心魔炼狱
	UpdatePurgatory(role, param[0], param[1])

def AfterLogin(role, param):
	UpdateRank(role)

def BeforeExit(role, param):
	UpdateRank(role)
	UpdateRoleHeroZDL(role)
	UpdateRoleZDL(role)
	
def CallPerHour():
	#每小时调用
	for role in RoleMgr.RoleID_Role.itervalues():
		UpdateRank(role)
		UpdateRoleZDL(role)
		UpdateRoleHeroZDL(role)
		
	if cDateTime.Hour() == 0:
		#清理全部的送花记录
		Role_Flower_Dict.clear()
	#更新排行榜送花数据
	UpdateRankFlower()
	#更新世界等级
	UpdataWorldLevel()
	#更新英雄战力排行榜，重新排序
	SortedHeroZDL()
	#清空缓存的公会排行数据
	global SYSTEM_UNION_RANK_DICT
	SYSTEM_UNION_RANK_DICT = {}
	
def CallFiveMin(callargv, regparam):
	#每5分钟调用
	for role in RoleMgr.RoleID_Role.itervalues():
		#判断是否是本服的玩家
		if not role.IsLocalServer():
			return
		UpdateLevelRank(role)
	#保存次数据
	LR.SaveData()
	#再次注册5分钟tick
	cComplexServer.RegTick(300, CallFiveMin)
		
def UpdataWorldLevel():
	#更新世界等级
	level_data = LR.ReturnData().items()
	level_data.sort(key = lambda x:(x[1][1], x[1][2]), reverse = True)
	#截取前20个数据
	level_data = level_data[0:20]
	total_level = 0
	for data in level_data:
		total_level += data[1][1]
	len_of_data = len(level_data)
	if not len_of_data:
		return
	worldLevel = total_level / len_of_data
	WorldData.SetWorldLevel(worldLevel)
	if cDateTime.Hour() == 0:
		#0点更新世界BUFF等级
		WorldData.SetWorldBuffLevel(worldLevel)
		
def RequestWorldLevel(role, msg):
	'''
	请求查看世界等级
	@param role:
	@param msg:
	'''
	
	backId, _ = msg
	role.CallBackFunction(backId, WorldData.GetWorldLevel())


if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		LR = LevelRank()
		ZR = ZDLRank()
		MR = MountRank()
		PR = PurgatoryRank()
		WR = WeddingRingRank()
		QM = MarryQinMiRank()
		EG = EquipmentGemRank()
		RZ = RoleZDLRank()
		TTR = TeamTowerRank()
		UFB = UnionFBRank()
		#角色鲜花记录(排行榜中获取鲜花的数量记录)
		Role_Flower_Dict = Contain.Dict("role_flower", (2038, 1, 1), AfterLoadFlower, isSaveBig = False)
		#英雄
		HEROZDL_BT = HeroZDLRank("sys_herozdl", 100, HeroZDLAfterLoad)
	
	if Environment.HasLogic:
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
	
	if Environment.HasLogic and not Environment.IsCross:
		#每小时之前调用
		cComplexServer.RegBeforeNewHourCallFunction(CallPerHour)
		
		cComplexServer.RegTick(300, CallFiveMin)
		
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		Event.RegEvent(Event.Eve_FinishPurgatory, FinishPurgatory)

		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Rank_SendFlower", "请求送花"), SendFlower)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Rank_Union_Request", "请求查看帮派排行榜"), RequestAllUnionRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Rank_RequestWorldLevel", "请求查询世界等级"), RequestWorldLevel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Rank_HeroZDL_Request", "请求查看英雄战力排行榜"), RequestHeroZDLRank)
		