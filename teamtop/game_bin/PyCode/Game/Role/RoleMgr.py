#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.RoleMgr")
#===============================================================================
# 角色管理
# 注意，角色名不唯一
#===============================================================================
import cProcess
import cDateTime
import cRoleDataMgr
import cComplexServer
import Environment
from Common.Other import EnumAppearance, EnumSocial
from Common.Message import AutoMessage
from ComplexServer.Plug.DB import DBProxy
from Game.Role import Event
from Game.Role.Data import EnumInt16, EnumDisperseInt32, EnumTempObj, EnumTempInt64,\
	EnumInt1, EnumInt8, EnumObj
from Game.Role.Config import RoleBaseConfig
from Game import GlobalMessage
from ComplexServer.Log import AutoLog
from Game.Marry import MarryMgr
from Game.GlobalData import ZoneName

if "_HasLoad" not in dir():
	#角色ID-->角色对象
	RoleID_Role = {}
	#角色名字-->角色对象集合(兼容重名)
	RoleName_Roles = {}
	
	Role_DayClearOK = AutoMessage.AllotMessage("Role_DayClearOK", "每日清理完毕")
	Tra_RoleExit = AutoLog.AutoTransaction("Tra_RoleExit", "角色退出游戏")
	
	Tra_DayClearScirpt = AutoLog.AutoTransaction("Tra_DayClearScirpt", "每日清理(脚本)")
	
def RoleLogin(role):
	#角色登陆调用
	RoleID_Role[role.GetRoleID()] = role
	rolename = role.GetRoleName()
	if rolename in RoleName_Roles:
		RoleName_Roles[rolename].add(role)
	else:
		RoleName_Roles[rolename] = set([role])
	#设置角色外观
	SetRoleAppreance(role)
	#记录角色登录时间
	role.SetTI64(EnumTempInt64.RoleLoginTimesSec, cDateTime.Seconds())
	
	# 记录登录
	loginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
	account = loginInfo["account"]
	userip = loginInfo["userip"]
	roleid = role.GetRoleID()
	from_1 = loginInfo["pf"]
	from_2 = loginInfo.get("app_custom", "")
	from_3 = loginInfo.get("app_contract_id", "")
	if from_1 == "website" or not from_2:
		#官网
		from_2 = loginInfo.get("adtag", "")
	role.SetTI64(EnumTempInt64.GrowLevel3366, loginInfo.get("3366_grow_level", 0))
	DBProxy.DBVisit(cProcess.ProcessID, None, "Info_Login", (account, userip, roleid, from_1, from_2, from_3))

LoginTimes = "LoginTime : "
ExitTimes = "ExitTime : "
loginPF = "LoginPF : "
loginIP = "LoginIP : "
ExitLevel = "ExitLevel : "

def BeforeExitByKickRole(role):
	roleId = role.GetRoleID()
	if roleId not in RoleID_Role:
		return
	# 只有登陆过得角色才触发退出事件
	Event.TriggerEvent(Event.Eve_BeforeExit, role)
	del RoleID_Role[roleId]
	RoleName_Roles[role.GetRoleName()].remove(role)
	if Environment.IsCross:
		return
	if role.GetLevel() <= 30:
		return
	if role.GetConsumeQPoint() <= 0:
		return
	loginTimes = role.GetTI64(EnumTempInt64.RoleLoginTimesSec)
	exitTimes = cDateTime.Seconds()
	with Tra_RoleExit:
		AutoLog.LogValue(role.GetRoleID(), AutoLog.eveRoleExit, loginTimes, exitTimes, (loginTimes, exitTimes))
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveExitData, (str(role.GetTempObj(EnumTempObj.LoginTime)), \
														role.GetTempObj(EnumTempObj.LoginInfo).get("userip"),\
														role.GetTempObj(EnumTempObj.LoginInfo).get("pf"), \
														str(cDateTime.Now()), \
														role.GetLevel()))

#		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveExitData, (LoginTimes + str(role.GetTempObj(EnumTempObj.LoginTime)), \
#															loginIP + role.GetTempObj(EnumTempObj.LoginInfo).get("userip"),\
#															loginPF + role.GetTempObj(EnumTempObj.LoginInfo).get("pf"), \
#															ExitTimes + str(cDateTime.Now()), \
#															ExitLevel + str(role.GetLevel())))

def RoleChangeName(role, oldName, newName):
	#改名之后调用(第一个版本的新手脚本)
	RoleName_Roles[oldName].discard(role)
	if newName in RoleName_Roles:
		RoleName_Roles[newName].add(role)
	else:
		RoleName_Roles[newName] = set([role])

def InitRoleOtherPyObj(role):
	#初始化角色OBJ
	Event.TriggerEvent(Event.Eve_InitRolePyObj, role)
	

def SyncRoleOtherPyObj(role):
	#同步角色OBJ
	Event.TriggerEvent(Event.Eve_SyncRoleOtherData, role)
	
def OnRoleDayClear(role):
	if not role:
		return
	if role.IsKick():
		return
	#触发每日清理
	if not role.GetI1(EnumInt1.En_IsInitOk):
		#角色还没有进行第一次初始化
		return
	with Tra_DayClearScirpt:
		#触发事件
		Event.TriggerEvent(Event.Eve_RoleDayClear, role)
	#通知客户端每日清理完毕
	role.SendObj(Role_DayClearOK, cDateTime.Seconds())

def OnlineNumber():
	ips = set()
	totalOnlineRole = 0
	for role in RoleID_Role.itervalues():
		if role.IsLost():
			continue
		totalOnlineRole += 1
		loginInfo = role.GetTempObj(EnumTempObj.LoginInfo)
		ips.add(loginInfo.get("userip"))
	DBProxy.DBVisit(cProcess.ProcessID, None, "Info_Online", (totalOnlineRole, len(ips)))

############################################################################################
#外观相关
############################################################################################
def SetRoleAppreance(role):
	#设置角色外观信息，其他玩家会根据版本号不一致的情况下向服务器请求这一份数据
	role.SetApperance(EnumAppearance.App_Version, role.GetVersion1())					#版本号
	role.SetApperance(EnumAppearance.App_RoleID, role.GetRoleID())						#角色ID
	role.SetApperance(EnumAppearance.App_Name, role.GetRoleName())						#名字
	role.SetApperance(EnumAppearance.App_Sex, role.GetSex())							#性别
	role.SetApperance(EnumAppearance.App_Career, role.GetCareer())						#职业
	role.SetApperance(EnumAppearance.App_MountID, role.GetRightMountID())				#坐骑ID
	role.SetApperance(EnumAppearance.App_Grade, role.GetGrade())						#进阶

	role.SetApperance(EnumAppearance.App_MoveSpeed, role.GetNowSpeed())					#移动速
	role.SetApperance(EnumAppearance.App_VIP, role.GetVIP())							#VIP
	role.SetApperance(EnumAppearance.App_Level, role.GetLevel())						#角色等级
	role.SetApperance(EnumAppearance.App_Status, 0)										#角色状态
	role.SetApperance(EnumAppearance.App_NewTitle, role.GetObj(EnumObj.Title).get(2, []))	#角色称号
	role.SetApperance(EnumAppearance.App_FollowHero, role.GetI16(EnumInt16.FollowHero))	#跟随英雄
	role.SetApperance(EnumAppearance.App_UnionId, role.GetUnionID())					#公会ID
	role.SetApperance(EnumAppearance.App_WingId, role.GetWingID())						#翅膀ID
	role.SetApperance(EnumAppearance.App_PetType, role.GetI8(EnumInt8.PetFollowType))	#宠物跟随类型
	
	role.SetApperance(EnumAppearance.APP_FashionClothes, role.GetTI64(EnumTempInt64.FashionClothes))#时装衣服
	role.SetApperance(EnumAppearance.App_FashionHat, role.GetTI64(EnumTempInt64.FashionHat))#时装帽子
	role.SetApperance(EnumAppearance.App_FashionWeapons, role.GetTI64(EnumTempInt64.FashionWeapons))#时装武器
	role.SetApperance(EnumAppearance.App_FashionState, role.GetI1(EnumInt1.FashionViewState))#时装显示状态
	
	role.SetApperance(EnumAppearance.App_StarGirlId, role.GetI8(EnumInt8.StarGirlFollowId))#星灵跟随ID
	
	role.SetApperance(EnumAppearance.App_WarStation, role.GetI16(EnumInt16.WarStationStarNum))	#战阵
	
	role.SetApperance(EnumAppearance.App_StationSoul, role.GetI16(EnumInt16.StationSoulId))	#阵灵ID
	
	#这里记录下玩家服信息
	from Game.CrossTeamTower import CrossTTMgr
	role.SetApperance(EnumAppearance.App_ZoneName, CrossTTMgr.GetRoleZoneName(role))
	
#	role.SetApperance(EnumAppearance.APP_ElementSpiritFollow, role.GetI8(EnumInt8.ElementSpiritFollow))		#元素之灵跟随

	#北美版
	if not Environment.EnvIsNA():
		if not Environment.IsCross:
			role.SetApperance(EnumAppearance.App_MarryRoleName, MarryMgr.GetMarryRoleName(role))#结婚对象名字
	
	if Environment.EnvIsQQ() or Environment.IsDevelop:
		role.SetApperance(EnumAppearance.App_Is3366, role.GetTI64(EnumTempInt64.Is3366))	#是否是3366平台
		role.SetApperance(EnumAppearance.App_QQ_NianFei_HuangZuan, role.GetQQYHZ())			#是否年费黄钻
		role.SetApperance(EnumAppearance.App_QQ_NianFei_LanZuan, role.GetQQYLZ())			#是否年费蓝钻
		role.SetApperance(EnumAppearance.App_QQ_HuangZuanLevel, role.GetQQHZ())				#黄钻等级
		role.SetApperance(EnumAppearance.App_QQ_LanZuanLevel, role.GetQQLZ())				#蓝钻等级
		role.SetApperance(EnumAppearance.App_QQ_HaoHua_HuangZuan, role.GetQQHHHZ())			#豪华黄钻
		role.SetApperance(EnumAppearance.App_QQ_HaoHua_LanZuan, role.GetQQHHLZ())			#豪华蓝钻
	
	if Environment.EnvIsFT() or Environment.IsDevelop:
		role.SetApperance(EnumAppearance.App_FTVIP, role.GetFTVIP())

def SetRoleChatInfo(role):
	role.SetChatInfo(EnumSocial.RoleIDKey, role.GetRoleID())
	role.SetChatInfo(EnumSocial.RoleNameKey, role.GetRoleName())
	role.SetChatInfo(EnumSocial.RoleVIPKey, role.GetVIP())
	
	if Environment.EnvIsQQ() or Environment.IsDevelop:
		role.SetChatInfo(EnumSocial.RoleHZKey, role.GetQQHZ())
		role.SetChatInfo(EnumSocial.RoleYHZKey, role.GetQQYHZ())
		role.SetChatInfo(EnumSocial.RoleLZKey, role.GetQQLZ())
		role.SetChatInfo(EnumSocial.RoleYLZKey, role.GetQQYLZ())
		role.SetChatInfo(EnumSocial.RoleHHHZKey, role.GetQQHHHZ())
		role.SetChatInfo(EnumSocial.RoleHHLZKey, role.GetQQHHLZ())
	
	role.SetChatInfo(EnumSocial.RoleCareerKey, role.GetCareer())
	role.SetChatInfo(EnumSocial.RoleSexKey, role.GetSex())
	role.SetChatInfo(EnumSocial.RoleGradeKey, role.GetGrade())
	role.SetChatInfo(EnumSocial.RoleLevelKey, role.GetLevel())
	role.SetChatInfo(EnumSocial.RoleDukeKey, role.GetI8(EnumInt8.EarningGoldBuff))

	if Environment.EnvIsFT() or Environment.IsDevelop:
		role.SetChatInfo(EnumSocial.FTVIP, role.GetFTVIP())

	if Environment.EnvIsRU() or Environment.IsDevelop:
		role.SetChatInfo(EnumSocial.RoleGMKey, role.GetI1(EnumInt1.GMRoleFlag))

############################################################################################
#外观改变触发
############################################################################################
def AfterChangeHuangZuan(role, oldValue, newValue):
	role.SetApperance(EnumAppearance.App_QQ_HuangZuanLevel, role.GetQQHZ())
	role.SetApperance(EnumAppearance.App_QQ_HaoHua_HuangZuan, role.GetQQHHHZ())
	role.SetApperance(EnumAppearance.App_QQ_NianFei_HuangZuan, role.GetQQYHZ())
	
	role.SetChatInfo(EnumSocial.RoleHZKey, role.GetQQHZ())
	role.SetChatInfo(EnumSocial.RoleYHZKey, role.GetQQYHZ())
	role.SetChatInfo(EnumSocial.RoleHHHZKey, role.GetQQHHHZ())
	
def AfterChangeLanZuan(role, oldValue, newValue):
	role.SetApperance(EnumAppearance.App_QQ_LanZuanLevel, role.GetQQLZ())
	role.SetApperance(EnumAppearance.App_QQ_HaoHua_LanZuan, role.GetQQHHLZ())
	role.SetApperance(EnumAppearance.App_QQ_NianFei_LanZuan, role.GetQQYLZ())
	
	role.SetChatInfo(EnumSocial.RoleLZKey, role.GetQQLZ())
	role.SetChatInfo(EnumSocial.RoleYLZKey, role.GetQQYLZ())
	role.SetChatInfo(EnumSocial.RoleHHLZKey, role.GetQQHHLZ())

def AfterChangeGrade(role, oldValue, newValue):
	role.SetApperance(EnumAppearance.App_Grade, role.GetGrade())
	role.SetChatInfo(EnumSocial.RoleGradeKey, role.GetGrade())
	
	#更新星级对应最大颜色记录
	sg_dict = role.GetObj(EnumObj.StarColor_Dict)
	roleStar = role.GetStar()
	colorCode = role.GetColorCode()
	oldMaxColorCode = sg_dict.get(roleStar)
	if not oldMaxColorCode or oldMaxColorCode < colorCode:
		sg_dict[roleStar] = colorCode
		role.SendObj(GlobalMessage.Msg_S_StarColorCode, sg_dict)
	
	Event.TriggerEvent(Event.Eve_AfterChangeRoleGrade, role, (oldValue, newValue))

def AfterChangeMoveSpeed(role, oldValue, newValue):
	#改变了原始速度
	role.SetApperance(EnumAppearance.App_MoveSpeed, role.GetNowSpeed())

def AfterChangeMountSpeed(role, oldValue, newValue):
	#改变了坐骑速度
	role.SetApperance(EnumAppearance.App_MoveSpeed, role.GetNowSpeed())
	
def AfterChangeTempSpeed(role, oldValue, newValue):
	#改变了临时速度
	role.SetApperance(EnumAppearance.App_MoveSpeed, role.GetNowSpeed())


def AfterChangeSex(role, oldValue, newValue):
	role.SetApperance(EnumAppearance.App_Sex, role.GetSex())
	role.SetChatInfo(EnumSocial.RoleSexKey, role.GetSex())

def AfterChangeCareer(role, oldValue, newValue):
	role.SetApperance(EnumAppearance.App_Career, role.GetCareer())
	role.SetChatInfo(EnumSocial.RoleCareerKey, role.GetCareer())

def AfterChangeMountID(role, oldValue, newValue):
	role.SetApperance(EnumAppearance.App_MountID, role.GetRightMountID())

def AfterChangeWingID(role, oldValue, newValue):
	role.SetApperance(EnumAppearance.App_WingId, role.GetWingID())
	
	if newValue > 0:
		#触发装备翅膀事件
		Event.TriggerEvent(Event.Eve_AfterOnWing, role, newValue)
	else:
		#触发卸下翅膀事件
		Event.TriggerEvent(Event.Eve_AfterOffWing, role, newValue)
		
def AfterChangePetFollowType(role, oldValue, newValue):
	role.SetApperance(EnumAppearance.App_PetType, newValue)
	
def AfterChangeFollowHero(role, oldValue, newValue):
	#改变跟随的英雄
	role.SetApperance(EnumAppearance.App_FollowHero, role.GetI16(EnumInt16.FollowHero))	#跟随英雄

def RoleAfterLevelUp(role, param):
	role.SetApperance(EnumAppearance.App_Level, role.GetLevel())
	role.SetChatInfo(EnumSocial.RoleLevelKey, role.GetLevel())

def AfterChangeRoleName(role, param):
	role.SetApperance(EnumAppearance.App_Name, role.GetRoleName())
	role.SetChatInfo(EnumSocial.RoleNameKey, role.GetRoleName())

def AfterChangeFTVIP(role, oldValue, newValue):
	role.SetApperance(EnumAppearance.App_FTVIP, role.GetFTVIP())
	role.SetChatInfo(EnumSocial.FTVIP, role.GetFTVIP())

def ChangeTitle(role, param):
	#改变称号
	role.SetApperance(EnumAppearance.App_NewTitle, role.GetObj(EnumObj.Title).get(2, []))	#角色称号
def ChangeMarryRoleName(role, param):
	#改变结婚对象名字
	role.SetApperance(EnumAppearance.App_MarryRoleName, MarryMgr.GetMarryRoleName(role))
	
def AfterChangeFashionClothes(role, oldValue, newValue):
	#改变时装衣服
	role.SetApperance(EnumAppearance.APP_FashionClothes, newValue)
	#触发穿脱时装事件
	Event.TriggerEvent(Event.Eve_AfterOnFashion, role, (EnumSocial.RoleFashionClothes, newValue))

		
def AfterChangeFashionHat(role, oldValue, newValue):
	#改变时装帽子
	role.SetApperance(EnumAppearance.App_FashionHat, newValue)
	#触发穿脱时装事件
	Event.TriggerEvent(Event.Eve_AfterOnFashion, role, (EnumSocial.RoleFashionHat, newValue))
	
def AfterChangeFashionWeapons(role, oldValue, newValue):
	#改变时装武器
	role.SetApperance(EnumAppearance.App_FashionWeapons, newValue)
	#触发穿脱时装事件
	Event.TriggerEvent(Event.Eve_AfterOnFashion, role, (EnumSocial.RoleFashionWeapons,newValue))
		
def AfterChangeFashionState(role, oldValue, newValue):
	#改变时装显示状态（1为显示，0为屏蔽）
	role.SetApperance(EnumAppearance.App_FashionState, newValue)
	#触发时装显示状态事件
	Event.TriggerEvent(Event.Eve_AfterFashionState, role, newValue)

def AfterChangeStarGirlFollowId(role, oldValue, newValue):
	role.SetApperance(EnumAppearance.App_StarGirlId, newValue)
		
def AfterWarStationStarNum(role, oldValue, newValue):
	#战阵星级改变
	role.SetApperance(EnumAppearance.App_WarStation, newValue)
	#触发战阵星级改变事件
	Event.TriggerEvent(Event.Eve_AfterWarStation, role, newValue)
	
def AfterLogin(role, param):
	#登录的时候设置移动速度
	role.SetMoveSpeed(RoleBaseConfig.MOVE_SPEED)
	
	#设置聊天信息
	SetRoleChatInfo(role)


def AfterChangeUnbindRMB_Q(role, oldValue, newValue):
	Event.TriggerEvent(Event.AfterChangeUnbindRMB_Q, role, (oldValue, newValue))

def AfterChangeUnbindRMB_S(role, oldValue, newValue):
	Event.TriggerEvent(Event.AfterChangeUnbindRMB_S, role, (oldValue, newValue))
	
def AfterChangeGameUnionAiwan(role, oldValue, newValue):#登录平台发生改变
	if role.GetI1(EnumInt1.GameUnionBuff_Aiwan):
		role.GetPropertyGather().ReSetRecountGameUnionLogBuffFlag()

def AfterChangeGameUnionQQGJ(role, oldValue, newValue):#登录平台发生改变
	if role.GetI1(EnumInt1.GameUnionBuff_QQGJ):
		role.GetPropertyGather().ReSetRecountGameUnionLogBuffFlag()

def AfterChangeStationSoul(role, param = None):
	'''
	阵灵改变
	'''
	role.SetApperance(EnumAppearance.App_StationSoul, role.GetI16(EnumInt16.StationSoulId))	#阵灵ID


#def AfterChangeElementSpiritFollow(role, oldValue, newValue):
#	'''
#	元素之灵跟随状态变化
#	'''
#	role.SetApperance(EnumAppearance.APP_ElementSpiritFollow, role.GetI8(EnumInt8.ElementSpiritFollow))
	

if "_HasLoad" not in dir():
	# 统计在线人数
	if Environment.HasLogic:
		cComplexServer.RegSaveCallFunction1(OnlineNumber)

	#注册改变函数(其他的外观相关值可能在别的模块注册了触发函数了)
	cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.enSex, AfterChangeSex)
	cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.enCareer, AfterChangeCareer)
	
	cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.HuangZuan_Y_H_L, AfterChangeHuangZuan)
	cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.LanZuan_Y_H_L, AfterChangeLanZuan)
	
	cRoleDataMgr.SetTempInt64Fun(EnumTempInt64.MoveSpeed, AfterChangeMoveSpeed)
	cRoleDataMgr.SetTempInt64Fun(EnumTempInt64.TempSpeed, AfterChangeTempSpeed)
	cRoleDataMgr.SetTempInt64Fun(EnumTempInt64.MountSpeed, AfterChangeMountSpeed)
	cRoleDataMgr.SetTempInt64Fun(EnumTempInt64.IsGameUnionAiWan, AfterChangeGameUnionAiwan)
	cRoleDataMgr.SetTempInt64Fun(EnumTempInt64.IsGameUnionQQGJ, AfterChangeGameUnionQQGJ)
	cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.RoleGrade, AfterChangeGrade)
	cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.RightMountID, AfterChangeMountID)
	
	cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.FTVIP, AfterChangeFTVIP)
	
	cRoleDataMgr.SetInt16Fun(EnumInt16.FollowHero, AfterChangeFollowHero)
	cRoleDataMgr.SetInt8Fun(EnumInt8.WingId, AfterChangeWingID)
	cRoleDataMgr.SetInt8Fun(EnumInt8.PetFollowType, AfterChangePetFollowType)
	
	cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.enUnbindRMB_Q, AfterChangeUnbindRMB_Q)
	cRoleDataMgr.SetDisperseInt32Fun(EnumDisperseInt32.enUnbindRMB_S, AfterChangeUnbindRMB_S)
	
	cRoleDataMgr.SetTempInt64Fun(EnumTempInt64.FashionClothes, AfterChangeFashionClothes)
	cRoleDataMgr.SetTempInt64Fun(EnumTempInt64.FashionHat, AfterChangeFashionHat)
	cRoleDataMgr.SetTempInt64Fun(EnumTempInt64.FashionWeapons, AfterChangeFashionWeapons)
	cRoleDataMgr.SetInt1Fun(EnumInt1.FashionViewState, AfterChangeFashionState)
	
	cRoleDataMgr.SetInt8Fun(EnumInt8.StarGirlFollowId, AfterChangeStarGirlFollowId)
	cRoleDataMgr.SetInt16Fun(EnumInt16.WarStationStarNum, AfterWarStationStarNum)
	Event.RegEvent(Event.Eve_AfterLevelUp, RoleAfterLevelUp)
	Event.RegEvent(Event.Eve_AfterChangeName, AfterChangeRoleName)
	
	Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
	Event.RegEvent(Event.Eve_ChangeTitle, ChangeTitle)
	Event.RegEvent(Event.Eve_ChangeMarryRoleName, ChangeMarryRoleName)
	
	Event.RegEvent(Event.Eve_AfterChangeStationSoul, AfterChangeStationSoul)
	
#	cRoleDataMgr.SetInt8Fun(EnumInt8.ElementSpiritFollow, AfterChangeElementSpiritFollow)
	

