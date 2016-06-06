#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Team.EnumTeamType")
#===============================================================================
# 组队类型
#===============================================================================

T_Base = 0			#组队基类(默认，不能组成一个队伍)
T_UnionFB = 1		#公会副本组队
T_GVE = 2			#GVE组队
T_KaifuBoss = 3		#开服boss组队
T_HefuBoss = 4		#合服 boss组队
T_TeamTower_1 = 5	#组队爬塔章节一
T_TeamTower_2 = 6	#组队爬塔章节二
T_TeamTower_3 = 7	#组队爬塔章节三
T_JT = 8			#跨服组队竞技场基础队伍
T_TeamTower_4 = 9	#组队爬塔章节四
T_TeamTower_5 = 10	#组队爬塔章节五
T_TeamTower_0 = 11	#组队爬塔序章
T_TeamTower_6 = 13	#组队爬塔章节六
T_CrossTeamTower = 14	#虚空幻境
T_LostScene = 15		#迷失之境
T_Shenshumijing = 16	#神树密境
T_ChaosDivinity1 = 17	#混沌神域1
T_ChaosDivinity2 = 18	#混沌神域2
T_ChaosDivinity3 = 19	#混沌神域3
T_ChaosDivinity4 = 20	#混沌神域4
T_ChaosDivinity5 = 21	#混沌神域5
T_ChaosDivinity6 = 22	#混沌神域6
T_ChaosDivinity7 = 23	#混沌神域7
T_ChaosDivinity8 = 24	#混沌神域8
T_ChaosDivinity9 = 25	#混沌神域9
T_ChaosDivinity10 = 26	#混沌神域10
T_ChaosDivinity11 = 27	#混沌神域11
T_ChaosDivinity12 = 28	#混沌神域12
T_Max = 28				#最大枚举数


def IsTeamTowerType(teamType):
	return teamType in (T_TeamTower_0, T_TeamTower_1, T_TeamTower_2, T_TeamTower_3, T_TeamTower_4, T_TeamTower_5, T_TeamTower_6)

def GetTeamTowerTypeIndex(teamType):
	return {T_TeamTower_0 : 0, T_TeamTower_1 :1, T_TeamTower_2 :2, T_TeamTower_3 :3, T_TeamTower_4 :4, T_TeamTower_5 :5, T_TeamTower_6:6}.get(teamType, None)

ChaosDivinity_Dict = {1:T_ChaosDivinity1
						,2:T_ChaosDivinity2
						,3:T_ChaosDivinity3
						,4:T_ChaosDivinity4
						,5:T_ChaosDivinity5
						,6:T_ChaosDivinity6
						,7:T_ChaosDivinity7
						,8:T_ChaosDivinity8
						,9:T_ChaosDivinity9
						,10:T_ChaosDivinity10
						,11:T_ChaosDivinity11
						,12:T_ChaosDivinity12}

def IsChaosDivinityType(teamType):
	global ChaosDivinity_Dict
	return teamType in ChaosDivinity_Dict.values()

def GetChaosDivinityType(index):
	global ChaosDivinity_Dict
	return ChaosDivinity_Dict.get(index,-1)

def GetCDIndexByTeamType(teamType):
	return teamType - T_ChaosDivinity1 + 1