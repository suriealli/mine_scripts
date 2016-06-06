#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.SysData.WorldDataNotSync")
#===============================================================================
# 不同步给客户端的世界数据
#===============================================================================
import Environment
import cComplexServer
from Game.Persistence import Contain
from Game.Role import Event


#===============================================================================
#keys 
BraveHeroServerType = 1	#勇者英雄坛服务器区域类型
BraveHeroActiveId = 2	#生成服务器类型的活动ID(不对应活动就要重新生成)
TeamTowerFinishDict = 3	#组队副本全服通关记录
TodayNewRole = 4		#今天注册人数
ToDayCDKOutPut = 5		#充值送豪礼本服今日产出CDK奖励个数
ZB_GuessFinalStep_1 = 6	#记录跨服争霸已经发奖的步骤(防止重复发奖)
ZB_ChampionTeamName_1 = 7	#跨服争霸天榜战队名字
ZB_ChampionTeamName_2 = 8	#跨服争霸地榜战队名字

ZB_GuessFinalStep_2 = 9	#记录跨服争霸已经发奖的步骤(防止重复发奖)
MaxOnlineToday = 10		#今天最大在线人数
QiMiRevertRoleIDs = 11	
SpringBRankActID = 12		#春节活动最靓丽活动ID
GlamourRankVersion = 13		#魅力情人节--魅力排行 活动版本号
RoseRebateVersion = 14		#魅力情人节--玫瑰返利  活动版本号
PartyServerType = 15		#跨服派对服务器类型
WZGC_AutoRefreshVersion = 16	#王者公测_充值返利转盘自动刷新版本号
KuafuFlowerRankServerType = 17		#跨服鲜花榜服务器区域类型
KuafuFlowerRankActiveId = 18		#跨服鲜花榜活动id
PassionTJHCBaseN = 19			#天降横财兑奖券序列基数
PassionTJHCBaseNVersion = 20	#天降横财兑奖券序列基数版本号
SecretGardenVersion = 21		#秘密花园版本号
#===============================================================================
#每次修改都要考虑合服情况  参考模块 PersisteneceMerge
#===============================================================================


def GetData(key):
	return WorldDataPrivate.get(key)

def SetData(key, value):
	WorldDataPrivate[key] = value

def AfterLoadDB():
	#载入数据之后，判断新KEY是否在字典里面，不在则需要初始化
	#注意初始化的时候如果需要导入其他模块，请直接在这个函数里面导入
	if BraveHeroServerType not in WorldDataPrivate:
		WorldDataPrivate[BraveHeroServerType] = 1
	if BraveHeroActiveId not in WorldDataPrivate:
		WorldDataPrivate[BraveHeroActiveId] = 0
	
	if TeamTowerFinishDict not in WorldDataPrivate:
		WorldDataPrivate[TeamTowerFinishDict] = {}
	
	if TodayNewRole not in WorldDataPrivate:
		WorldDataPrivate[TodayNewRole] = 0
	
	if ToDayCDKOutPut not in WorldDataPrivate:
		WorldDataPrivate[ToDayCDKOutPut] = 0
	
	if ZB_GuessFinalStep_1 not in WorldDataPrivate:
		WorldDataPrivate[ZB_GuessFinalStep_1] = 0
	
	if ZB_GuessFinalStep_2 not in WorldDataPrivate:
		WorldDataPrivate[ZB_GuessFinalStep_2] = 0
		
	if ZB_ChampionTeamName_1 not in WorldDataPrivate:
		WorldDataPrivate[ZB_ChampionTeamName_1] = ""
		
	if ZB_ChampionTeamName_2 not in WorldDataPrivate:
		WorldDataPrivate[ZB_ChampionTeamName_2] = ""
	if MaxOnlineToday not in WorldDataPrivate:
		WorldDataPrivate[MaxOnlineToday] = 0
	
	if QiMiRevertRoleIDs not in WorldDataPrivate:
		WorldDataPrivate[QiMiRevertRoleIDs] = set()
	
	if GlamourRankVersion not in WorldDataPrivate:
		WorldDataPrivate[GlamourRankVersion] = 0
	
	if RoseRebateVersion not in WorldDataPrivate:
		WorldDataPrivate[RoseRebateVersion] = 0
	
	
	if PartyServerType not in WorldDataPrivate:
		WorldDataPrivate[PartyServerType] = 0
	
	#此处默认不为0是有意为之 系统更新出去角色上线满足条件就刷新相关数据
	if WZGC_AutoRefreshVersion not in WorldDataPrivate:
		WorldDataPrivate[WZGC_AutoRefreshVersion] = 1
	
	if KuafuFlowerRankServerType not in WorldDataPrivate:
		WorldDataPrivate[KuafuFlowerRankServerType] = 0
	
	if KuafuFlowerRankActiveId not in WorldDataPrivate:
		WorldDataPrivate[KuafuFlowerRankActiveId] = 0
	
	if PassionTJHCBaseN not in WorldDataPrivate:
		WorldDataPrivate[PassionTJHCBaseN] = 0
		
	if PassionTJHCBaseNVersion not in WorldDataPrivate:
		WorldDataPrivate[PassionTJHCBaseNVersion] = 0
	
	if SecretGardenVersion not in WorldDataPrivate:
		WorldDataPrivate[SecretGardenVersion] = 0
	
	Event.TriggerEvent(Event.Eve_AfterLoadWorldDataNotSync, None)

def HasQiMiRevert(roleId):
	#是否已经修复过了
	if QiMiRevertRoleIDs not in WorldDataPrivate:
		WorldDataPrivate[QiMiRevertRoleIDs] = set()
	
	return roleId in WorldDataPrivate[QiMiRevertRoleIDs]

def AddQiMiRevert(roleId):
	if QiMiRevertRoleIDs not in WorldDataPrivate:
		WorldDataPrivate[QiMiRevertRoleIDs] = set()
	WorldDataPrivate[QiMiRevertRoleIDs].add(roleId)
	
def GetGuessFinalStep_1():
	return WorldDataPrivate[ZB_GuessFinalStep_1]

def SetGuessFinalStep_1(step):
	WorldDataPrivate[ZB_GuessFinalStep_1] = step

def GetGuessFinalStep_2():
	return WorldDataPrivate[ZB_GuessFinalStep_2]

def SetGuessFinalStep_2(step):
	WorldDataPrivate[ZB_GuessFinalStep_2] = step

def SetZBChampionTeamName1(name):
	WorldDataPrivate[ZB_ChampionTeamName_1] = name

def GetZBChampionTeamName1():
	return WorldDataPrivate[ZB_ChampionTeamName_1]

def SetZBChampionTeamName2(name):
	WorldDataPrivate[ZB_ChampionTeamName_2] = name

def GetZBChampionTeamName2():
	return WorldDataPrivate[ZB_ChampionTeamName_2]

def GetGlamourRankVersion():
	return WorldDataPrivate[GlamourRankVersion]

def SetGlamourRankVersion(version):
	WorldDataPrivate[GlamourRankVersion] = version

def GetRoseRebateVersion():
	return WorldDataPrivate[RoseRebateVersion]

def SetRoseRebateVersion(version):
	WorldDataPrivate[RoseRebateVersion] = version

def GetWZGCRefreshVersion():
	return WorldDataPrivate[WZGC_AutoRefreshVersion]

def SetWZGCRefreshVersion(version):
	WorldDataPrivate[WZGC_AutoRefreshVersion] = version

def SetTJHCBaseN(baseN):
	WorldDataPrivate[PassionTJHCBaseN] = baseN

def GetTHJCBaseN():
	return WorldDataPrivate[PassionTJHCBaseN]

def SetSecretGardenVersion(version):
	WorldDataPrivate[SecretGardenVersion] = version

def GetSecretGardenVersion():
	return WorldDataPrivate[SecretGardenVersion]
	
def AfterNewRole(role, param):
	WorldDataPrivate[TodayNewRole] += 1

def AfterNewDay():
	WorldDataPrivate[TodayNewRole] = 0
	WorldDataPrivate[ToDayCDKOutPut] = 0

if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		WorldDataPrivate = Contain.Dict("world_data_notsync", (2038, 1, 1), AfterLoadDB, isSaveBig = False)

	if Environment.HasLogic:
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay, 2)
		Event.RegEvent(Event.Eve_FirstInitRole, AfterNewRole)
