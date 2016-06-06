#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.FunGather")
#===============================================================================
# 角色数组数据有关的聚合接口
#===============================================================================
import cProcess
import Environment
from World import Define
from Common.Other import EnumKick, EnumGameConfig
from Game.Role.Config import RoleConfig
from Game.Role.Data import EnumInt64, EnumInt32, EnumDisperseInt32, EnumInt8, EnumTempInt64, EnumCD, EnumTempObj, EnumObj, EnumInt16
from Game.Role.Obj import EnumOdata
from Game.StationSoul import StationSoulConfig
from Game.Hero import HeroConfig
from Game.Item.ItemConfig import ArtifactCuiLianHalo_Dict
from Game.ElementSpirit import ElementSpiritConfig


def IncTarotHP(role, value):
	'''增加命力'''
	role.IncI32(EnumInt32.TaortHP, value)

def IsMonthCard(role):
	'''是否月卡'''
	if Environment.EnvIsNA():
		#北美版
		return role.GetCD(EnumCD.Card_Month) or role.GetCD(EnumCD.Card_Quarter) or role.GetCD(EnumCD.Card_HalfYear) or role.GetCD(EnumCD.Card_Year)
	else:
		#其他版本
		return role.GetCD(EnumCD.Card_Month) or role.GetCD(EnumCD.Card_HalfYear)

def IncMoney(role, value):
	'''增加金钱'''
	role.IncI64(EnumInt64.enMoney, value)

def DecMoney(role, value):
	'''减少金钱'''
	role.DecI64(EnumInt64.enMoney, value)

def GetMoney(role):
	'''获取金钱'''
	return role.GetI64(EnumInt64.enMoney)

def SetMoney(role, value):
	'''设置金钱'''
	role.SetI64(EnumInt64.enMoney, value)

def GetRMB(role):
	'''获取魔晶和神石'''
	return role.GetDI32(EnumDisperseInt32.enUnbindRMB_Q) + role.GetDI32(EnumDisperseInt32.enUnbindRMB_S) + role.GetDI32(EnumDisperseInt32.enBindRMB)

def DecRMB(role, value):
	'''减少魔晶和神石'''
	bindrmb = role.GetDI32(EnumDisperseInt32.enBindRMB)
	if value > bindrmb:
		role.SetDI32(EnumDisperseInt32.enBindRMB, 0)
		value -= bindrmb
		unbindRMB_S = role.GetDI32(EnumDisperseInt32.enUnbindRMB_S)
		if value > unbindRMB_S:
			role.SetDI32(EnumDisperseInt32.enUnbindRMB_S, 0)
			role.DecDI32(EnumDisperseInt32.enUnbindRMB_Q, value - unbindRMB_S)
		else:
			role.DecDI32(EnumDisperseInt32.enUnbindRMB_S, value)
	else:
		role.DecDI32(EnumDisperseInt32.enBindRMB, value)


def DecUnbindRMB(role, value):
	'''减少非绑定(神石)'''
	unbindRMB_S = role.GetDI32(EnumDisperseInt32.enUnbindRMB_S)
	if value > unbindRMB_S:
		role.SetDI32(EnumDisperseInt32.enUnbindRMB_S, 0)
		role.DecDI32(EnumDisperseInt32.enUnbindRMB_Q, value - unbindRMB_S)
	else:
		#優先扣除系統神石
		role.DecDI32(EnumDisperseInt32.enUnbindRMB_S, value)

def GetUnbindRMB(role):
	'''获取非绑定(神石)'''
	return role.GetDI32(EnumDisperseInt32.enUnbindRMB_Q) + role.GetDI32(EnumDisperseInt32.enUnbindRMB_S)


def IncUnbindRMB_Q(role, value):
	'''增加非绑定(充值 神石)'''
	role.IncDI32(EnumDisperseInt32.enUnbindRMB_Q, value)

def DecUnbindRMB_Q(role, value):
	'''减少非绑定(充值 神石)'''
	role.DecDI32(EnumDisperseInt32.enUnbindRMB_Q, value)

def GetUnbindRMB_Q(role):
	'''获取非绑定(充值 神石)'''
	return role.GetDI32(EnumDisperseInt32.enUnbindRMB_Q)

def SetUnbindRMB_Q(role, value):
	'''设置非绑定(充值 神石)'''
	role.SetDI32(EnumDisperseInt32.enUnbindRMB_Q, value)




def IncUnbindRMB_S(role, value):
	'''增加非绑定(系统 神石)'''
	role.IncDI32(EnumDisperseInt32.enUnbindRMB_S, value)

def DecUnbindRMB_S(role, value):
	'''减少非绑定(系统 神石)'''
	role.DecDI32(EnumDisperseInt32.enUnbindRMB_S, value)

def GetUnbindRMB_S(role):
	'''获取非绑定(系统 神石)'''
	return role.GetDI32(EnumDisperseInt32.enUnbindRMB_S)

def SetUnbindRMB_S(role, value):
	'''设置非绑定(系统 神石)'''
	role.SetDI32(EnumDisperseInt32.enUnbindRMB_S, value)


def IncBindRMB(role, value):
	'''增加绑定(魔晶)'''
	role.IncDI32(EnumDisperseInt32.enBindRMB, value)

def DecBindRMB(role, value):
	'''减少绑定(魔晶)'''
	role.DecDI32(EnumDisperseInt32.enBindRMB, value)

def GetBindRMB(role):
	'''获取绑定(魔晶)'''
	return role.GetDI32(EnumDisperseInt32.enBindRMB)

def SetBindRMB(role, value):
	'''设置绑定(魔晶)'''
	role.SetDI32(EnumDisperseInt32.enBindRMB, value)

def IncReputation(role, value):
	'''增加声望'''
	role.IncI32(EnumInt32.enReputation, value)

def DecReputation(role, value):
	'''减少声望'''
	role.DecI32(EnumInt32.enReputation, value)

def GetReputation(role):
	'''获取声望'''
	return role.GetI32(EnumInt32.enReputation)

def SetReputation(role, value):
	'''设置声望'''
	role.SetI32(EnumInt32.enReputation, value)

def GetExp(role):
	'''获取经验'''
	return role.GetI64(EnumInt64.En_Exp)

def SetExp(role, value):
	'''设置经验 （小心使用）'''
	role.SetI64(EnumInt64.En_Exp, value)

def GetUnionID(role):
	'''获取公会ID'''
	return role.GetI32(EnumInt32.UnionID)

def SetUnionID(role, value):
	'''设置公会ID'''
	role.SetI32(EnumInt32.UnionID, value)

def GetLevel(role):
	'''获取角色等级'''
	return role.GetDI32(EnumDisperseInt32.enLevel)

def IncLevel(role, value):
	'''提升角色等级'''
	return role.IncDI32(EnumDisperseInt32.enLevel, value)

def GetSex(role):
	'''获取角色性别'''
	return role.GetDI32(EnumDisperseInt32.enSex)

def ChangeSex(role):
	'''改变角色性别'''
	if role.GetDI32(EnumDisperseInt32.enSex) == 1:
		role.SetDI32(EnumDisperseInt32.enSex, 2)
	elif role.GetDI32(EnumDisperseInt32.enSex) == 2:
		role.SetDI32(EnumDisperseInt32.enSex, 1)
	return role.GetDI32(EnumDisperseInt32.enSex)

def GetVIP(role):
	'''获取VIP'''
	return role.GetDI32(EnumDisperseInt32.enVIP)

def SetVIP(role, value):
	'''设置VIP'''
	role.SetDI32(EnumDisperseInt32.enVIP, value)

def GetConsumeQPoint(role):
	'''获取消费点'''
	return role.GetDI32(EnumDisperseInt32.ConsumeQPoint)

def SetConsumeQPoint(role, value):
	'''设置消费点'''
	role.SetDI32(EnumDisperseInt32.ConsumeQPoint, value)
	
def IncConsumeQPoint(role, value):
	'''增加消费点'''
	role.IncDI32(EnumDisperseInt32.ConsumeQPoint, value)


def GetStationID(role):
	'''获取阵位ID'''
	return role.GetI8(EnumInt8.enStationID)

def SetStationID(role, value):
	'''设置阵位ID'''
	role.SetI8(EnumInt8.enStationID, value)

def GetZDL(role):
	'''获取战斗力'''
	return role.GetDI32(EnumDisperseInt32.ZDL)

def SetZDL(role, value):
	'''设置战斗力'''
	role.SetDI32(EnumDisperseInt32.ZDL, value)

def GetRightMountID(role):
	'''获取玩家当前骑乘坐骑ID'''
	return role.GetDI32(EnumDisperseInt32.RightMountID)

def SetRightMountID(role, value):
	'''设置玩家当前骑乘坐骑ID'''
	role.SetDI32(EnumDisperseInt32.RightMountID, value)

def GetGrade(role):
	'''获取进阶'''
	return role.GetDI32(EnumDisperseInt32.RoleGrade)

def SetGrade(role, value):
	'''设置进阶'''
	role.SetDI32(EnumDisperseInt32.RoleGrade, value)

def GetStar(role):
	'''获取主角星级'''
	return RoleConfig.Grade_To_Star_Dict.get(role.GetGrade(), 0)

def GetColorCode(role):
	'''获取主角颜色编码'''
	return RoleConfig.Grade_To_ColorCode_Dict.get(role.GetGrade(), 0)

def GetPortrait(role):
	'''获取头像信息(性别, 职业, 进阶)'''
	return role.GetDI32(EnumDisperseInt32.enSex), role.GetDI32(EnumDisperseInt32.enCareer), role.GetDI32(EnumDisperseInt32.RoleGrade)

def SetCanLoginTime(role, unix_time):
	'''设置可登录时间，并且T掉角色（封角色）'''
	role.SetDI32(EnumDisperseInt32.CanLoginTime, unix_time)
	role.Kick(True, EnumKick.LimitLogin)

def SetCanChatTime(role, unix_time):
	'''设置可发言的时间（解/禁 发言）'''
	role.SetDI32(EnumDisperseInt32.CanChatTime, unix_time)

def GetWeek(role):
	'''获取当前周数'''
	return role.GetI8(EnumInt8.Week)

def SetWeek(role, value):
	'''设置当前周数'''
	role.SetI8(EnumInt8.Week, value)

def GetFightType(role):
	'''获取当前临时的战斗类型'''
	return role.GetTI64(EnumTempInt64.TempFightType)

def SetFightType(role, value):
	'''设置当前临时的战斗类型'''
	role.SetTI64(EnumTempInt64.TempFightType, value)

def GetCampID(role):
	'''获取阵营ID'''
	return role.GetDI32(EnumDisperseInt32.CampID)

def SetCampID(role, value):
	'''设置阵营ID'''
	role.SetDI32(EnumDisperseInt32.CampID, value)
	
def GetJobID(role):
	'''获取公会职位ID'''
	return role.GetI8(EnumInt8.UnionJobID)

def SetJobID(role, value):
	'''设置公会职位ID'''
	role.SetI8(EnumInt8.UnionJobID, value)
	
def GetContribution(role):
	'''获取公会贡献'''
	return role.GetI32(EnumInt32.UnionContribution)

def SetContribution(role, value):
	'''设置公会贡献'''
	return role.SetI32(EnumInt32.UnionContribution, value)

def IncContribution(role, value):
	'''增加公会贡献'''
	role.IncI32(EnumInt32.UnionContribution, value)
	#公会历史贡献也需要一起增加
	role.IncI32(EnumInt32.UnionHistoryContribution, value)
	
def DecContribution(role, value):
	'''减少公会贡献'''
	role.DecI32(EnumInt32.UnionContribution, value)
	
def GetHistoryContribution(role):
	'''获取公会历史贡献'''
	return role.GetI32(EnumInt32.UnionHistoryContribution)

def SetHistoryContribution(role, value):
	'''设置公会历史贡献'''
	return role.SetI32(EnumInt32.UnionHistoryContribution, value)

def IncHistoryContribution(role, value):
	'''增加公会历史贡献'''
	role.IncI32(EnumInt32.UnionHistoryContribution, value)
	
def GetWingID(role):
	'''获取翅膀ID'''
	return role.GetI8(EnumInt8.WingId)

def SetWingID(role, value):
	'''设置翅膀ID'''
	role.SetI8(EnumInt8.WingId, value)

def GetEarningExpBuff(role):
	'''获取城主经验加成buff'''
	#百分比
	return role.GetI8(EnumInt8.EarningExpBuff)
	
def SetEarningExpBuff(role, value):
	'''设置城主经验加成buff'''
	role.SetI8(EnumInt8.EarningExpBuff, value)

def GetEarningGoldBuff(role):
	'''获取城主金钱加成buff'''
	#百分比
	return role.GetI8(EnumInt8.EarningGoldBuff)
	
def SetEarningGoldBuff(role, value):
	'''设置城主金钱加成buff'''
	role.SetI8(EnumInt8.EarningGoldBuff, value)



def GetEquipmentMgr(role):
	'''获取装备管理器'''
	return role.GetTempObj(EnumTempObj.enRoleEquipmentMgr)

def GetArtifactMgr(role):
	'''获取神器管理器'''
	return role.GetTempObj(EnumTempObj.enRoleArtifactMgr)

def GetHallowsMgr(role):
	'''获取圣器管理器'''
	return role.GetTempObj(EnumTempObj.enRoleHallowsMgr)


def GetPet(role):
	'''获取角色佩戴的宠物'''
	petId = role.GetI64(EnumInt64.PetID)
	if not petId:
		return None
	
	petMgr = role.GetTempObj(EnumTempObj.PetMgr)
	
	#找不到对应的宠物
	if petId not in petMgr.pet_dict:
		return None
	pet = petMgr.pet_dict[petId]
	
	#双向验证
	if pet.hero_id != role.GetRoleID():
		if cProcess.ProcessID not in Define.TestWorldIDs:
			print "GE_EXC, role get pet error pet id not match (%s)" % role.GetRoleID()
		return None
	return pet

def GetTalentMgr(role):
	'''获取天赋卡管理器'''
	return role.GetTempObj(EnumTempObj.TalentCardMgr)

	
def GetTalentEmptySize(role):
	'''获取天赋卡背包空余格子数'''
	TalentCardMgr = role.GetTempObj(EnumTempObj.TalentCardMgr)
	return TalentCardMgr.GetEmptySize()

def GetTalentZDL(role):
	'''获取玩家天赋卡技能战斗力（只有主角）'''
	TalentCardMgr = role.GetTempObj(EnumTempObj.TalentCardMgr)
	return TalentCardMgr.GetCardZDL(2)

def GetDragonCareerID(role):
	'''获取神龙职业ID'''
	return role.GetI8(EnumInt8.DragonCareerID)

def SetDragonCareerID(role, value):
	'''设置神龙职业ID'''
	role.SetI8(EnumInt8.DragonCareerID, value)

def GetFTVIP(role):
	'''获取繁体VIP'''
	return role.GetDI32(EnumDisperseInt32.FTVIP)

def GetDragonSoul(role):
	'''获取龙灵数量'''
	return role.GetI32(EnumInt32.DragonTrainSoul)

def SetDragonSoul(role, value):
	'''设置龙灵数量'''
	role.SetI32(EnumInt32.DragonTrainSoul, value)

def IncDragonSoul(role, value):
	'''增加龙灵数量'''
	role.IncI32(EnumInt32.DragonTrainSoul, value)

def DecDragonSoul(role, value):
	'''减少龙灵数量'''
	role.DecI32(EnumInt32.DragonTrainSoul, value)
	
def GetStarLucky(role):
	'''获取星运数量'''
	return role.GetI32(EnumInt32.StarLucky)

def SetStarLucky(role, value):
	'''设置星运数量'''
	role.SetI32(EnumInt32.StarLucky, value)

def IncStarLucky(role, value):
	'''增加星运数量'''
	role.IncI32(EnumInt32.StarLucky, value)

def DecStarLucky(role, value):
	'''减少星运数量'''
	role.DecI32(EnumInt32.StarLucky, value)

def GetJTeamID(role):
	'''获取战队id'''
	return role.GetI64(EnumInt64.JTeamID)

def SetJTeamID(role, value):
	'''设置战队ID'''
	role.SetI64(EnumInt64.JTeamID, value)

def GetJTProcessID(role):
	'''获取组队竞技场是的本服进程ID'''
	role.GetTI64(EnumTempInt64.JT_ProcessID)

def GetDayBuyUnbindRMB_Q(role):
	'''获取每日充值神石'''
	return role.GetI32(EnumInt32.DayBuyUnbindRMB_Q)

def GetDayConsumeUnbindRMB(role):
	'''获取每日消费神石，包括充值神石和系统神石'''
	return role.GetI32(EnumInt32.DayConsumeUnbindRMB)

def GetXinYueLevel(role):
	'''心悦VIP等级'''
	return role.GetI8(EnumInt8.QQXinYueVipLevel)

def GetKuaFuMoney(role):
	'''获取跨服币'''
	return role.GetI32(EnumInt32.KuaFuMoney)

def SetKuaFuMoney(role, value):
	'''设置跨服币'''
	return role.SetI32(EnumInt32.KuaFuMoney, value)

def IncKuaFuMoney(role, value):
	'''增加跨服币'''
	role.IncI32(EnumInt32.KuaFuMoney, value)
	
def DecKuaFuMoney(role, value):
	'''减少跨服币'''
	role.DecI32(EnumInt32.KuaFuMoney, value)


def GetRongYu(role):
	'''获取荣誉'''
	return role.GetI32(EnumInt32.JTGold)

def SetRongYu(role, value):
	'''设置荣誉'''
	return role.SetI32(EnumInt32.JTGold, value)

def IncRongYu(role, value):
	'''增加荣誉'''
	role.IncI32(EnumInt32.JTGold, value)
	
def DecRongYu(role, value):
	'''减少荣誉'''
	role.DecI32(EnumInt32.JTGold, value)
	
def GetGongXun(role):
	'''获取功勋'''
	return role.GetI32(EnumInt32.JTExp)

def SetGongXun(role, value):
	'''设置功勋'''
	return role.SetI32(EnumInt32.JTExp, value)

def IncGongXun(role, value):
	'''增加功勋'''
	role.IncI32(EnumInt32.JTExp, value)
	
def DecGongXun(role, value):
	'''减少功勋'''
	role.DecI32(EnumInt32.JTExp, value)


def GetMagicSpiritMgr(role):
	'''获取魔灵管理器'''
	return role.GetTempObj(EnumTempObj.enRoleMagicSpiritMgr)

def GetMFZSkill(role):
	'''	获取当前携带的魔法阵技能'''
	myMFZData = role.GetObj(EnumObj.MFZData) 
	mfzSkillList = []
	if 1 in myMFZData and len(myMFZData[1]) == 2:
		mfzSkillList.append((myMFZData[1][0],myMFZData[1][1]))
	
	return mfzSkillList

def GetMFZSkillPointDict(role):
	'''获取魔法阵技能点字典'''
	skillpointDict = {}
	tmpskillpointList = []
	magicSpiritMgr = role.GetTempObj(EnumTempObj.enRoleMagicSpiritMgr)
	for _, magicSpirit in magicSpiritMgr.objIdDict.iteritems():
		tmpskillpointList = magicSpirit.GetSavedRefreshSkillPoint()
		if len(tmpskillpointList) == 2:
			st = tmpskillpointList[0]
			sv = tmpskillpointList[1]
			if st in skillpointDict:
				skillpointDict[st] += sv
			else:
				skillpointDict[st] = sv
	
	return skillpointDict

def UpdateAndSyncMFZSkillPassive(role):
	'''更新当前魔法阵技能携带状态'''
	from Game.MoFaZhen import MoFaZhenMgr
	MoFaZhenMgr.RealUpdateAndSyncMFZSkill(role, None)
	
def IsKongJianDecennialRole(role):
	'''判断玩家登录渠道是否为 空间、朋友网、 QQ游戏大厅、3366、官网'''
	isQzone = role.GetTI64(EnumTempInt64.IsQzone)
	isPengYou = role.GetTI64(EnumTempInt64.IsPengYou)
	
	isQQGame = role.GetTI64(EnumTempInt64.IsQQGame)
	is3366 = role.GetTI64(EnumTempInt64.Is3366)
	isWebsite = role.GetTI64(EnumTempInt64.IsWebsite)
	
	if isQzone or isPengYou or isQQGame or is3366 or isWebsite:
		return True
	else:
		return False

def GetDayWangZheJiFen(role):
	'''返回玩家今日王者公测积分'''
	return role.GetDayBuyUnbindRMB_Q() * EnumGameConfig.WZR_RechargeFactor + role.GetDayConsumeUnbindRMB() * EnumGameConfig.WZR_ConsumeFactor

def GetStationSoulSkill(role):
	'''返回角色当前阵灵技能'''
	nowCfg = StationSoulConfig.StationSoul_BaseConfig_Dict.get(role.GetI16(EnumInt16.StationSoulId))
	if nowCfg and nowCfg.skillState:
		return nowCfg.skillState
	else:
		return None

def GetMoFaZhen(role):
	'''返回魔法阵数据'''
	moFaZhenDict = {} 
		
	#魔法阵技能数据
	moFaZhenDict[1] = role.GetMFZSkill()
	#属性数据
	p_dict = {}
	PG = p_dict.get
	magicSpiritMgr = role.GetTempObj(EnumTempObj.enRoleMagicSpiritMgr)
	if magicSpiritMgr:
		for _, magicSpirit in magicSpiritMgr.objIdDict.iteritems():
			pt, pv = magicSpirit.odata[EnumOdata.enMagicSpiritSavedProperty]
			p_dict[pt] = PG(pt, 0) + pv			
		moFaZhenDict[2] = p_dict
	
	return moFaZhenDict
	
def GetCuiLian_MaxCnt(role):
	'''	返回角色可以淬炼的最大次数	'''
	return RoleConfig.RoleBase_Dict.get((role.GetCareer(), role.GetGrade(), role.GetSex())).CuiLianShiCnt

def GetCuiLian(role):
	'''	返回角色淬炼次数	'''
	return role.GetObj(EnumObj.En_RoleCuiLian).get(1, 0)
	
def AddCuiLian(role, msg):
	'''	增加角色淬炼次数	'''
	if msg <= 0:
			return
	if role.GetCuiLian() + msg > role.GetCuiLian_MaxCnt():
		return
	role.GetObj(EnumObj.En_RoleCuiLian)[1] = role.GetObj(EnumObj.En_RoleCuiLian).get(1, 0) + msg
	
def GetArtifactCuiLianHoleLevel(role):
	'''获取角色神器淬炼光环等级'''
	
	return role.GetI8(EnumInt8.AtifactHaloLevel)
	

def GetZhuanShengHaloLevel(role):
	'''获取角色转生光环等级'''
	return role.GetDI32(EnumDisperseInt32.enZhuanShengHaloLv)

def SetZhuanShengHaloLevel(role, value):
	'''设置角色转生光环等级'''
	return role.SetDI32(EnumDisperseInt32.enZhuanShengHaloLv, value)

def GetZhuanShengLevel(role):
	'''获取角色转生等级'''
	return role.GetDI32(EnumDisperseInt32.enZhuanShengLv)

def SetZhuanShengLevel(role, value):
	'''设置角色转生等级'''
	return role.SetDI32(EnumDisperseInt32.enZhuanShengLv, value)

def GetZhuanShengHaloAddi(role):
	'''获取角色转生光环加成'''
	congfig = HeroConfig.ZhuangShengHaloConfigDict.get(role.GetZhuanShengHaloLevel())
	return getattr(congfig, 'AddCoe', 0)

def IncTouchGoldPoint(role, value):
	#增加点石成金积分
	role.IncI32(EnumInt32.TouchGoldPoint, value)

def GetElementSpiritSkill(role):
	'''返回元素之灵技能'''
	elementSpiritCfg = ElementSpiritConfig.ElementSpirit_BaseConfig_Dict.get(role.GetI16(EnumInt16.ElementSpiritId))
	if not elementSpiritCfg:
		return None
		
	skillLevel = elementSpiritCfg.skillLevel
	skillType = role.GetI8(EnumInt8.ElementSpiritSkillType)
	skillId = ElementSpiritConfig.ElementSpirit_SkillConfig_Dict.get(skillType)
	if not skillId:
		return None
		
	return [(skillId, skillLevel)]


def GetElementBrandMgr(role):
	'''返回元素印记管理器'''
	return role.GetTempObj(EnumTempObj.ElementBrandMgr)