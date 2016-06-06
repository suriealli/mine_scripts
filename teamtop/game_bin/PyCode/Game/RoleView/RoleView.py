#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.RoleView.RoleView")
#===============================================================================
# 角色查看另外的玩家的数据模块
#===============================================================================
import copy
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumSocial, GlobalPrompt
from Game.JJC import JJCMgr
from Game.Marry import MarryMgr
from Game.Persistence import BigTable
from Game.Role import RoleMgr, Event
from Game.Role.Data import EnumTempObj, EnumObj, EnumInt8, EnumInt16,\
	EnumTempInt64, EnumInt1
from Game.SysData import WorldData
from Game.Union import UnionMgr

#基本数据
#技能
#属性
#装备
#英雄基本数据
#英雄属性
#英雄装备
#####################################################################################

def OnRoleView(role, msg):
	'''
	查看一个玩家的数据
	@param role:
	@param msg:
	'''
	roleId = msg
	if role.GetRoleID() == roleId:
		#不可以查看自己
		return
	
	viewrole = RoleMgr.RoleID_Role.get(roleId)
	if not viewrole:
		if Environment.IsCross:
			return
		SyncOffLineRoleData(role, roleId)
		return
	
	role.SendObj(RoleView_S_SyncRoleData, PackRoleViewData(viewrole))

def OnRoleViewRank(role, msg):
	'''
	请求查看一个排行榜玩家所有信息
	@param role:
	@param msg:
	'''
	roleId = msg
	viewrole = RoleMgr.RoleID_Role.get(roleId)
	if not viewrole:
		if Environment.IsCross:
			return
		SyncOffLineRoleDataRank(role, roleId)
		return
	
	role.SendObj(RoleViewRank_S_SyncRoleData, PackRoleViewData(viewrole))

def OnRoleView_Role(role, msg):
	'''
	只查看主角
	@param role:
	@param msg:
	'''
	roleId = msg
#	if role.GetRoleID() == roleId:
#		#不可以查看自己
#		return
	viewrole = RoleMgr.RoleID_Role.get(roleId)
	if not viewrole:
		SyncOffLineRoleOnly(role, roleId)
		return
	
	role.SendObj(RoleView_S_SyncRoleOnly, PackRole(viewrole))



def OnRoleViewProp(role, msg):
	#查看一个玩家的道具
	d_roleId, propId = msg
	
	d_role = cRoleMgr.FindRoleByRoleID(d_roleId)
	if d_role is None:
		role.Msg(2, 0, GlobalPrompt.GLOBAL_NotOnlineRole)
		return
	
	prop = role.GetTempObj(EnumTempObj.enGlobalItemMgr).get(propId)
	if not prop:
		return
	
	role.SendObj(Prop_S_SyncRoleProp, prop.GetSyncData())

#####################################################################################


def PackRoleViewData(role):
	#打包全部
	##################################################################################
	#packData{1    -->角色数据{EnumSocial.keys --> value},#角色的基础数据比英雄的多一点
	#		heroId-->英雄数据{EnumSocial.keys --> value}	}
	##################################################################################
	packData = {}
	packData[1] = PackRole(role)
	roleHeroMgr = role.GetTempObj(EnumTempObj.enHeroMgr)
	for heroId, hero in roleHeroMgr.HeroDict.iteritems():
		if not hero.GetStationID():
			continue
		packData[heroId] = GetHeroData(hero)
	return packData

def PackRole(role):
	#打包主角
	roledata = {}
	roledata[EnumSocial.RoleIDKey] = role.GetRoleID()
	roledata[EnumSocial.RoleNameKey] = role.GetRoleName()
	
	roledata[EnumSocial.RoleSexKey] = role.GetSex()
	roledata[EnumSocial.RoleCareerKey] = role.GetCareer()
	roledata[EnumSocial.RoleGradeKey] = role.GetGrade()
	
	roledata[EnumSocial.RoleLevelKey] = role.GetLevel()
	roledata[EnumSocial.RoleExpKey] = role.GetExp()
	
	roledata[EnumSocial.RoleZDLKey] = role.GetZDL()
	if not Environment.IsCross:
		roledata[EnumSocial.RoleUnionNameKey] = UnionMgr.GetUnionName(role)
	else:
		roledata[EnumSocial.RoleUnionNameKey] = ""
		
	#坐骑相关
	roledata[EnumSocial.RoleMountIDKey] = role.GetRightMountID()
	roledata[EnumSocial.RoleMountEvolveIDKey] = role.GetI16(EnumInt16.MountEvolveID)
	mountMgr = role.GetTempObj(EnumTempObj.MountMgr)
	#坐骑培养属性
	roledata[EnumSocial.RoleMountPropertyKey] = mountMgr.GetAttribute()
	#坐骑外形品质属性
	roledata[EnumSocial.RoleMountApperancePro] = mountMgr.GetAppAttribute()
	#坐骑外形品质
	roledata[EnumSocial.RoleMountApperanceGrade] = mountMgr.MountAGDict
	
	skillDict = role.GetObj(EnumObj.RoleSkill)
	roledata[EnumSocial.RoleSkillKey] = [(skill_id, skillDict[skill_id]) for skill_id in role.GetObj(EnumObj.RoleFightSkill).get(1)]
	roledata[EnumSocial.RolePropertyKey] = GetUnitProperty(role)
	
	roledata[EnumSocial.RoleEquipmentKey] = role.GetTempObj(EnumTempObj.enRoleEquipmentMgr).GetSyncObjDict()
	roledata[EnumSocial.RoleKeyArtifact] = role.GetTempObj(EnumTempObj.enRoleArtifactMgr).GetSyncObjDict()
	roledata[EnumSocial.RoleArtifactSealingLevelKey] = role.GetI8(EnumInt8.ArtifactSealingID)
	roledata[EnumSocial.RoleSealingSpiritLevelKey] = role.GetI8(EnumInt8.SealingSpiritID)
	
	roledata[EnumSocial.RoleTarotRingLevel] = role.GetI8(EnumInt8.TarotRingLevel)
	roledata[EnumSocial.RoleTarotCardKey] = role.GetTempObj(EnumTempObj.enTarotMgr).GetRoleViewData()
	
	roledata[EnumSocial.RoleHelpStationKey] = role.GetTempObj(EnumTempObj.enStationMgr).GetViewData()
	
	roledata[EnumSocial.RoleWingKey] = GetWingViewData(role)
	roledata[EnumSocial.RoleWingIDKey] = role.GetWingID()
	
	roledata[EnumSocial.PetTypeKey] = role.GetI8(EnumInt8.PetType)
	roledata[EnumSocial.PetSoulKey] = role.GetTempObj(EnumTempObj.PetMgr).get_role_soul_dict(role)
	
	roledata[EnumSocial.RoleHallowsKey] = role.GetTempObj(EnumTempObj.enRoleHallowsMgr).GetSyncObjDict()
	
	roledata[EnumSocial.QVIP_3366] = role.GetTI64(EnumTempInt64.Is3366)
	roledata[EnumSocial.WeddingRingID] = role.GetI16(EnumInt16.WeddingRingID)
	roledata[EnumSocial.WeddingRingPro] = GetWeddingProperty(role)
	#时装相关
	roledata[EnumSocial.RoleFashionClothes] = role.GetTI64(EnumTempInt64.FashionClothes)
	roledata[EnumSocial.RoleFashionHat] = role.GetTI64(EnumTempInt64.FashionHat)
	roledata[EnumSocial.RoleFashionWeapons] = role.GetTI64(EnumTempInt64.FashionWeapons)
	roledata[EnumSocial.RoleFashionState] = role.GetI1(EnumInt1.FashionViewState)
	roledata[EnumSocial.RoleFashionInfo] = role.GetTempObj(EnumTempObj.enRoleFashionMgr).GetSyncObjDict()
	roledata[EnumSocial.RoleFashionSuitPro] = GetFashionSuitProperty(role)
	roledata[EnumSocial.RoleFashionIdePro] = GetFashionIdeProperty(role)
	roledata[EnumSocial.RoleFashionData] = role.GetTempObj(EnumTempObj.enRoleFashionGlobalMgr).fashion_active_dict
	roledata[EnumSocial.RoleFashionHoleLevel] = role.GetI8(EnumInt8.FashionHaloLevel)
	roledata[EnumSocial.RoleFashionYiGui] = role.GetI8(EnumInt8.FashionWardrobeLevel)
	#订婚戒指 -- 订婚戒指道具ID:(订婚戒指道具coding, 数量, {26:(1-铭刻, 0-未铭刻)})
	roleRingMgr = role.GetTempObj(EnumTempObj.enRoleRingMgr)
	roledata[EnumSocial.RoleRingData] = roleRingMgr.GetSyncObjDict()
	#战阵
	roledata[EnumSocial.RoleWarStation] = role.GetI16(EnumInt16.WarStationStarNum)
	roledata[EnumSocial.RoleWarStationItem] = role.GetI16(EnumInt16.UseStationItemCnt)
	#阵灵
	roledata[EnumSocial.RoleStationSoul] = role.GetI16(EnumInt16.StationSoulId)
	roledata[EnumSocial.RoleStationSoulItem] = role.GetI16(EnumInt16.StationSoulItemCnt)
	
	if Environment.IsCross:
		roledata[EnumSocial.RoleRingImprintMsg] = None
	else:
		ringIdSet = role.GetObj(EnumObj.En_RoleRing)
		if ringIdSet:
			for ringId in ringIdSet:
				break
			ringData = MarryMgr.RING_BT.GetData().get(role.GetRoleID())
			if ringData:
				ringData = ringData.get('ringData')
				if ringData:
					imprintMsg = ringData.get(ringId)
					#订婚戒指铭刻信息 -- [role_id, role_name, 铭刻信息]
					roledata[EnumSocial.RoleRingImprintMsg] = imprintMsg
			else:
				roledata[EnumSocial.RoleRingImprintMsg] = None
		else:
			roledata[EnumSocial.RoleRingImprintMsg] = None
	
	if role.GetI8(EnumInt8.MarryStatus) == 3:
		roledata[EnumSocial.MarryRoleName] = MarryMgr.GetMarryRoleName(role)
	else:
		roledata[EnumSocial.MarryRoleName] = None
		
	
	roledata[EnumSocial.TalentKey] = role.GetTalentMgr().GetRoleViewData()
	roledata[EnumSocial.DragonTrainKey] = role.GetTempObj(EnumTempObj.DragonTrainMgr).get_role_view_data()
	roledata[EnumSocial.StarGirlKey] = role.GetTempObj(EnumTempObj.StarGirlMgr).get_role_view_data()
	
	roledata[EnumSocial.EquipmentGemTotalLevel] = role.GetTotalGemLevel()
	
	roledata[EnumSocial.RoleTitleKey] = role.GetObj(EnumObj.Title).get(1, {})
	#魔法阵
	roledata[EnumSocial.RoleMoFaZhen] = role.GetMoFaZhen()
	#转生等级
	roledata[EnumSocial.RoleZhuanShengLevel] = role.GetZhuanShengLevel()
	#圣器封印等级
	roledata[EnumSocial.RoleHallowSealingLevelKey] = role.GetI8(EnumInt8.HallowsSealingSpiritID)

	return roledata

def GetHeroData(hero):
	#获取这个英雄的数据
	herodata = {}
	herodata[EnumSocial.RoleHeroBaseKey] = hero.GetSyncData()
	herodata[EnumSocial.RoleHeroPropertyKey] = GetUnitProperty(hero)
	herodata[EnumSocial.RoleHeroEquipmentKey] = hero.equipmentMgr.GetSyncObjDict()
	herodata[EnumSocial.RoleHeroArtifactKey] = hero.ArtifactMgr.GetSyncObjDict()
	herodata[EnumSocial.RoleTarotCardKey] = hero.role.GetTempObj(EnumTempObj.enTarotMgr).GetHeroViewData(hero.oid)
	herodata[EnumSocial.PetTypeKey] = hero.GetPetType()
	herodata[EnumSocial.PetSoulKey] = hero.role.GetTempObj(EnumTempObj.PetMgr).get_hero_soul_dict(hero)
	herodata[EnumSocial.RoleHeroHallowsKey] = hero.HallowsMgr.GetSyncObjDict()
	herodata[EnumSocial.TalentKey] = hero.role.GetTalentMgr().GetHeroViewData(hero.oid)
	#魔法阵
	herodata[EnumSocial.RoleMoFaZhen] = hero.GetMoFaZhen()
	return herodata

def GetUnitProperty(uint):
	#获取这个对象的属性
	return copy.deepcopy(uint.GetPropertyGather().total_p.p_dict)

def GetWeddingProperty(role):
	return copy.deepcopy(role.GetPropertyGather().mgr.weddingRing_p.p_dict)

def GetFashionSuitProperty(role):
	total_dict = {}
	for pt, pv in role.GetPropertyGather().fashion_p.p_dict.iteritems():
		total_dict[pt] = total_dict.get(pt, 0) + pv
	for pt, pv in role.GetPropertyGather().fashionHole_p.p_dict.iteritems():
		total_dict[pt] = total_dict.get(pt, 0) + pv
	for pt, pv in role.GetPropertyGather().fashionSuit_p.p_dict.iteritems():
		total_dict[pt] = total_dict.get(pt, 0) + pv
#	for pt, pv in role.GetPropertyGather().fashionStar_p.p_dict.iteritems():
#		total_dict[pt] = total_dict.get(pt, 0) + pv
#	for pt, pv in role.GetPropertyGather().fashionOrder_p.p_dict.iteritems():
#		total_dict[pt] = total_dict.get(pt, 0) + pv
	return copy.deepcopy(total_dict)

def GetFashionIdeProperty(role):
	return copy.deepcopy(role.GetPropertyGather().mgr.fashionglobal_p.p_dict)

def GetWingViewData(role):
	wingViewDict = {}
	wingDataDict = role.GetObj(EnumObj.Wing)[1]
	wingEvolveDict = role.GetObj(EnumObj.Wing)[2]
	for wingId, wingData in wingDataDict.iteritems():
		level, exp = wingData
		wingViewDict[wingId] = [level, exp, wingEvolveDict.get(wingId, 0)]
	
	return wingViewDict

#####################################################################################
def SyncOffLineRoleData(role, roleId):
	#查询一个离线的玩家数据
	rD = RoleView_BT.GetData().get(roleId)
	if not rD:
		role.Msg(2, 0, GlobalPrompt.GLOBAL_NotOnlineRole)
		return
	role.SendObj(RoleView_S_SyncRoleData, rD.get("viewData"))

def SyncOffLineRoleDataRank(role, roleId):
	#查询一个离线的玩家数据
	rD = RoleView_BT.GetData().get(roleId)
	if not rD:
		role.Msg(2, 0, GlobalPrompt.GLOBAL_NotOnlineRole)
		return
	role.SendObj(RoleViewRank_S_SyncRoleData, rD.get("viewData"))
	

def SyncOffLineRoleOnly(role, roleId):
	#查询一个离线的玩家主角数据
	rD = RoleView_BT.GetData().get(roleId)
	if not rD:
		role.Msg(2, 0, GlobalPrompt.GLOBAL_NotOnlineRole)
		return
	viewData = rD.get("viewData")
	if not viewData:
		return
	role.SendObj(RoleView_S_SyncRoleOnly, viewData[1])



#####################################################################################

def GetOfflineHead(roleId):
	#获取一个玩家的头像
	role = cRoleMgr.FindRoleByRoleID(roleId)
	if role:
		#先尝试查找在线玩家
		return (role.GetSex(), role.GetCareer(), role.GetGrade())
	rD = RoleView_BT.GetData().get(roleId)
	if not rD:
		return (1, 1, 1)
	roledata = rD["viewData"][1]
	return (roledata[EnumSocial.RoleSexKey], roledata[EnumSocial.RoleCareerKey], roledata[EnumSocial.RoleGradeKey])


def UpdataViewData(role):
	roleId = role.GetRoleID()
	viewdata = PackRoleViewData(role)
	RoleView_BT.SetKeyValue(roleId, {"role_id" : roleId, "viewData" : viewdata})



#####################################################################################

class RoleViewBT(BigTable.BigTable):
	def SaveData(self):
		if self.returnDB:
			#只保存一部分,竞技场前500名 ,所有的公会会长
			datadict = self.GetData()
			if len(datadict) > 700:
				#人数大于700人的时候才做数据整理逻辑，这样会在500-700之间拥有一个缓冲区
				unionLeaders = GetUnionLeaders()
				for roleId in datadict.keys():
					if roleId in unionLeaders:
						continue
					roleRank = JJCMgr.GetJJCRank(roleId)
					if not roleRank or roleRank > 500:
						self.DelKey(roleId)
		BigTable.BigTable.SaveData(self)

def GetUnionLeaders():
	lIds = set()
	for uo in UnionMgr.UNION_OBJ_DICT.itervalues():
		lIds.add(uo.leader_id)
	return lIds

def AfterLoad():
	pass


def BeforeExit(role, param):
	#离开游戏之前，看看要不要保存数据
	roleId = role.GetRoleID()
	datadict = RoleView_BT.GetData()
	if len(datadict) < 700 or WorldData.GetWorldKaiFuDay() < 7:
		#数据比较少，或者是新服，直接更新
		UpdataViewData(role)
		return
	
	#否则看看是否需要保存这个玩家的数据
	roleRank = JJCMgr.GetJJCRank(roleId)
	if roleRank and roleRank <= 500:
		#是否是竞技场前500名
		UpdataViewData(role)
	else:
		for uo in UnionMgr.UNION_OBJ_DICT.itervalues():
			if roleId == uo.leader_id:
				#是否是公会会长
				UpdataViewData(role)
				break


#####################################################################################


if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		RoleView_BT = RoleViewBT("sys_role_view", 5, AfterLoad)
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
	
	RoleView_S_SyncRoleData = AutoMessage.AllotMessage("RoleView_S_SyncRoleData", "同步一个别的玩家的所有信息")
	RoleView_S_SyncRoleOnly = AutoMessage.AllotMessage("RoleView_S_SyncRoleOnly", "同步一个别的玩家的主角信息")
	Prop_S_SyncRoleProp = AutoMessage.AllotMessage("Prop_S_SyncRoleProp", "同步一个别的玩家的道具信息")
	RoleViewRank_S_SyncRoleData = AutoMessage.AllotMessage("RoleViewRank_S_SyncRoleData", "同步一个别的玩家的排行榜所有信息")
	
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Role_OnRoleView", "请求查看一个玩家所有信息"), OnRoleView)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Role_OnRoleView_Role", "请求查看一个玩家主角的信息"), OnRoleView_Role)

	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Prop_OnRoleViewProp", "请求查看一个玩家道具"), OnRoleViewProp)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Role_OnRoleViewForRank", "请求查看一个排行榜玩家所有信息"), OnRoleViewRank)
	