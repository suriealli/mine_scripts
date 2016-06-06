#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WorldCup.WorldCup")
#===============================================================================
# 世界杯
#===============================================================================
#import cRoleMgr
#import DynamicPath
#import Environment
#from Util.File import TabFile
#from Common.Message import AutoMessage
#from Common.Other import GlobalPrompt
#from ComplexServer.Log import AutoLog
#from Game import RTF
#from Game.Persistence import Contain
#from Game.Role import Event
#from Game.Role.Data import EnumObj
#from Game.Activity import CircularDefine
#
#
#
#持久化数据记录的keys
#旧数据，小组赛到决赛的小组队伍记录
#WorldCupKey_16 = "WorldCup16"
#WorldCupKey_8 = "WorldCup8"
#WorldCupKey_4 = "WorldCup4"
#WorldCupKey_2 = "WorldCup2"
#WorldCupKey_3 = "WorldCup3"
#WorldCupKey_1 = "WorldCupCampion"
#
#淘汰赛对战分组
#WorldCupKey_Group16 = "W_G16"	#16进8 {组别:(队伍Id1, 队伍id 2)}
#WorldCupKey_Group8 = "W_G8"		#8进 4
#WorldCupKey_Group4 = "W_G4"		#4进2
#WorldCupKey_Group2 = "W_G2"		#决赛
#WorldCupKey_Group3 = "W_G3"		#季军赛
#
#淘汰赛结果
#WorldCupKey_Result16 = "W_R16"	#16进8｛组别  : {队伍Id : 进球数}｝
#WorldCupKey_Result8 = "W_R8"	#8进 4
#WorldCupKey_Result4 = "W_R4"	#4进2
#WorldCupKey_Result2 = "W_R2"	#决赛
#WorldCupKey_Result3 = "W_R3"	#季军赛
#
#
#阶段对应的存储数据key
#StageTokey = {16 : (WorldCupKey_16, WorldCupKey_Group16, WorldCupKey_Result16),
#				8 : (WorldCupKey_8, WorldCupKey_Group8, WorldCupKey_Result8),
#				4 : (WorldCupKey_4, WorldCupKey_Group4, WorldCupKey_Result4),
#				2 : (WorldCupKey_2, WorldCupKey_Group2, WorldCupKey_Result2),
#				3 : (WorldCupKey_3, WorldCupKey_Group3, WorldCupKey_Result3)
#				}
#
#阶段，组别对应的活动开启flag
#StageGroupFlagDict = { 16 : {1 : (CircularDefine.CA_WorldCupGuess_8_1, CircularDefine.CA_WorldCupReward_8_1),
#					2 : (CircularDefine.CA_WorldCupGuess_8_2, CircularDefine.CA_WorldCupReward_8_2),
#					3 : (CircularDefine.CA_WorldCupGuess_8_3, CircularDefine.CA_WorldCupReward_8_3),
#					4 : (CircularDefine.CA_WorldCupGuess_8_4, CircularDefine.CA_WorldCupReward_8_4),
#					5 : (CircularDefine.CA_WorldCupGuess_8_5, CircularDefine.CA_WorldCupReward_8_5),
#					6 : (CircularDefine.CA_WorldCupGuess_8_6, CircularDefine.CA_WorldCupReward_8_6),
#					7 : (CircularDefine.CA_WorldCupGuess_8_7, CircularDefine.CA_WorldCupReward_8_7),
#					8 : (CircularDefine.CA_WorldCupGuess_8_8, CircularDefine.CA_WorldCupReward_8_8)
#					},
#			8 : {1 : (CircularDefine.CA_WorldCupGuess_4_1, CircularDefine.CA_WorldCupReward_4_1),
#				2 : (CircularDefine.CA_WorldCupGuess_4_2, CircularDefine.CA_WorldCupReward_4_2),
#				3 : (CircularDefine.CA_WorldCupGuess_4_3, CircularDefine.CA_WorldCupReward_4_3),
#				4 : (CircularDefine.CA_WorldCupGuess_4_4, CircularDefine.CA_WorldCupReward_4_4)
#				 },
#			4 : {1 : (CircularDefine.CA_WorldCupGuess_2_1, CircularDefine.CA_WorldCupReward_2_1),
#				2 : (CircularDefine.CA_WorldCupGuess_2_2, CircularDefine.CA_WorldCupReward_2_2)
#				},
#			3 : {1 : (CircularDefine.CA_WorldCupGuessJiJun, CircularDefine.CA_WorldCupRewardJiJun)
#				},
#			2 : {1 : (CircularDefine.CA_WorldCupGuessJueSai, CircularDefine.CA_WorldCupRewardJueSai)}
#		}
#
#
#16强竞猜
#WorldCupGuess16NeedUnbindRMB = 20
#冠军竞猜
#WorldCunGuessChampionNeedUnbindRMB = 100
#世界杯宝箱
#WorldCupItem = 26231
#
#淘汰赛竞猜需要金币
#WorldCupGroupGuessNeedMoney = 80000 
#WorldCupGroupGuessNeedUnbindRMB = 88
#
#决赛竞猜需要金币
#WorldCupJueSaiGuessNeedMoney = 80000 
#WorldCupJueSaiGuessNeedUnbindRMB = 200
#
#
#奖励类型
#WCReward_Group_RMB_Win = 1		#淘汰赛神石胜利	
#WCReward_Group_RMB_Lose = 2		#淘汰赛神石失败	
#WCReward_Group_Money_Win = 3	#淘汰赛金币胜利	
#WCReward_Group_Money_Lose = 4	#淘汰赛金币失败	
#WCReward_JueSai_RMB_Win = 5		#冠军神石胜利	
#WCReward_JueSai_RMB_Lose = 6	#冠军神石失败	
#WCReward_JueSai_Money_Win = 7	#冠军金币胜利
#WCReward_JueSai_Money_Lose = 8	#冠军金币失败	
#
#
#
#if "_HasLoad" not in dir():
#	FILE_FOLDER_PATH = DynamicPath.DynamicFolder(DynamicPath.ConfigPath)
#	FILE_FOLDER_PATH.AppendPath("WorldCup")
#
#	WorldCupConfig_Dict = {}
#	WorldCupConfig_Name_Dict = {}
#	WorldCupConfig_Group_Dict = {}
#	
#	WorldCupRewardConfig_Dict = {}
#	
#	活动开启的类型记录
#	CircularStartFlags = set()
#
#
#################################################################################
#def GetDataInitDict():
#	持久化数据初始化参照字典
#	return { WorldCupKey_16 : set(),
#			WorldCupKey_8 : set(),
#			WorldCupKey_4 : set(),
#			WorldCupKey_2 : set(),
#			WorldCupKey_3 : set(),
#			WorldCupKey_1 : 0,
#			
#			WorldCupKey_Group16 : {},
#			WorldCupKey_Group8 : {},
#			WorldCupKey_Group4 : {},
#			WorldCupKey_Group2 : {},
#			WorldCupKey_Group3 : {},
#			
#			WorldCupKey_Result16 : {},
#			WorldCupKey_Result8 : {},
#			WorldCupKey_Result4 : {},
#			WorldCupKey_Result2 : {},
#			WorldCupKey_Result3 : {}
#			}
#
#
#################################################################################
#class WorldCupConfig(TabFile.TabLine):
#	FilePath = FILE_FOLDER_PATH.FilePath("WorldCup.txt")
#	def __init__(self):
#		self.group = int
#		self.groupName = str
#		self.teamID = int
#		self.teamName = str
#
#def LoadWorldCupConfig():
#	global WorldCupConfig_Dict, WorldCupConfig_Name_Dict, WorldCupConfig_Group_Dict
#	for wcc in WorldCupConfig.ToClassType():
#		WorldCupConfig_Dict[wcc.teamID] = wcc
#		WorldCupConfig_Name_Dict[wcc.teamName] = wcc
#		
#		if wcc.group not in WorldCupConfig_Group_Dict:
#			WorldCupConfig_Group_Dict[wcc.group] = {wcc.teamID : wcc}
#		else:
#			WorldCupConfig_Group_Dict[wcc.group][wcc.teamID] = wcc
#
#class WorldCupRewardConfig(TabFile.TabLine):
#	FilePath = FILE_FOLDER_PATH.FilePath("Reward.txt")
#	def __init__(self):
#		self.rewardType = int
#		self.reward = self.GetEvalByString
#
#def LoadWorldCupRewardConfig():
#	global WorldCupRewardConfig_Dict
#	for wcc in WorldCupRewardConfig.ToClassType():
#		WorldCupRewardConfig_Dict[wcc.rewardType] = wcc.reward
#
#
#################################################################################
#后台调用函数
#################################################################################
#@RTF.RegFunction
#def Add_Group_16(team1, team2):
#	'''
#	增加一对16强队伍, 填写队伍名称如  "巴西","法国"
#	@param team1:
#	@param team2:
#	'''
#	global WorldCupConfig_Name_Dict
#	teamCfg_1 = WorldCupConfig_Name_Dict.get(team1)
#	if not teamCfg_1:
#		print "GE_EXC Add_Group_16 not this team1 (%s)" % team1
#		return
#	
#	teamCfg_2 = WorldCupConfig_Name_Dict.get(team2)
#	if not teamCfg_2:
#		print "GE_EXC Add_Group_16 not this team2 (%s)" % team2
#		return
#	
#	if teamCfg_1.group != teamCfg_2.group:
#		print "GE_EXC, Add_Group_16 not same group team "
#		return
#	
#	if teamCfg_1.teamID == teamCfg_2.teamID:
#		print "GE_EXC, repeat set team in 16"
#		return
#	
#	global WorldCupConfig_Group_Dict
#	gd = WorldCupConfig_Group_Dict.get(teamCfg_1.group)
#	if not gd:
#		print "GE_EXC, error in Add_Group_16 not group cfg dict (%s)" % teamCfg_1.group
#		return
#	
#	grupteams = gd.keys()
#	if teamCfg_1.teamID not in grupteams:
#		print "GE_EXC Add_Group_16 error cfg "
#		return
#	if teamCfg_2.teamID not in grupteams:
#		print "GE_EXC Add_Group_16 error cfg "
#		return
#	
#	winTeams = WorldCupData.get(WorldCupKey_16)
#	if winTeams:
#		if len(winTeams) >= 16:
#			print "GE_EXC, 16 team is full"
#			return
#		for teamId in grupteams:
#			if teamId in winTeams:
#				print "GE_EXC, already set team in this group "
#				return
#		winTeams.add(teamCfg_1.teamID)
#		winTeams.add(teamCfg_2.teamID)
#		WorldCupData.HasChange()
#	else:
#		winTeams = set()
#		winTeams.add(teamCfg_1.teamID)
#		winTeams.add(teamCfg_2.teamID)
#		WorldCupData[WorldCupKey_16] = winTeams
#
#@RTF.RegFunction
#def Set_World_Champion(teamName):
#	'''
#	设置冠军队, 填写队伍名称如  "巴西"
#	@param teamName:
#	'''
#	global WorldCupConfig_Name_Dict
#	teamCfg = WorldCupConfig_Name_Dict.get(teamName)
#	if not teamCfg:
#		print "GE_EXC Set_World_Champion not this teamName (%s)" % teamName
#		return
#	global WorldCupData
#	perwinTeams = WorldCupData.get(WorldCupKey_2)
#	if not perwinTeams or len(perwinTeams) != 2 :
#		print "GE_EXC, 2 team not enought"
#		return
#	
#	if teamCfg.teamID not in perwinTeams:
#		print "GE_EXC, error in Set_World_Champion not in this 2 team"
#		return
#
#	ChampionId = WorldCupData.get(WorldCupKey_1)
#	if ChampionId:
#		print "GE_EXC repeat  set ChampionId"
#		return
#	WorldCupData[WorldCupKey_1] = teamCfg.teamID
#
#################################################################################
#淘汰赛
#################################################################################
#@RTF.RegFunction
#def Set_WorldCupTeam(stage, group, teamName1, teamName2):
#	'''
#	设置淘汰赛对战队伍
#	@param stage:
#	@param group:
#	@param teamName1:
#	@param teamName2:
#	'''
#	keys = StageTokey.get(stage)
#	if not keys:
#		return
#	
#	if group < 1 or group > stage / 2:
#		return
#	
#	team_1_Cfg = WorldCupConfig_Name_Dict.get(teamName1)
#	if not team_1_Cfg:
#		return
#	team_2_Cfg = WorldCupConfig_Name_Dict.get(teamName2)
#	if not team_2_Cfg:
#		return
#	
#	team_1_Id = team_1_Cfg.teamID
#	team_2_Id = team_2_Cfg.teamID
#	if team_1_Id == team_2_Id:
#		return
#	
#	global WorldCupData
#	oldData = WorldCupData.get(keys[0])
#	groupdata = WorldCupData.get(keys[1])
#	
#	if group in groupdata:
#		return
#	
#	if team_1_Id not in oldData or team_2_Id not in oldData:
#		oldData.add(team_1_Id)
#		oldData.add(team_2_Id)
#	
#	groupdata[group] = (team_1_Id, team_2_Id)
#	WorldCupData.HasChange()
#
#
#@RTF.RegFunction
#def Set_WorldCupTeamGoal(stage, group, teamName1, goal1, teamName2, goal2):
#	'''
#	设置淘汰赛比分结果
#	@param stage:
#	@param group:
#	@param teamName1:
#	@param goal1:
#	@param teamName2:
#	@param goal2:
#	'''
#	keys = StageTokey.get(stage)
#	if not keys:
#		return
#	
#	if group < 1 or group > stage / 2:
#		return
#	
#	team_1_Cfg = WorldCupConfig_Name_Dict.get(teamName1)
#	if not team_1_Cfg:
#		return
#	team_2_Cfg = WorldCupConfig_Name_Dict.get(teamName2)
#	if not team_2_Cfg:
#		return
#	
#	team_1_Id = team_1_Cfg.teamID
#	team_2_Id = team_2_Cfg.teamID
#	if team_1_Id == team_2_Id:
#		return
#	
#	global WorldCupData
#	oldData = WorldCupData.get(keys[0])
#	groupdata = WorldCupData.get(keys[1])
#	
#	if team_1_Id not in oldData or team_2_Id not in oldData:
#		return
#	
#	groupteams = groupdata.get(group)
#	if not groupteams:
#		return
#	
#	if team_1_Id not in groupteams or team_2_Id not in groupteams:
#		return
#	
#	goalData = WorldCupData.get(keys[2])
#	if group in goalData:
#		return
#	
#	goalData[group] = {team_1_Id : goal1, team_2_Id : goal2}
#
#	WorldCupData.HasChange()
#
#################################################################################
#
#################################################################################
#def AfterLoadWorldCupDataDB():
#	持久化数据载入处理
#	global WorldCupData
#	for k, v in GetDataInitDict().iteritems():
#		if k not in WorldCupData:
#			WorldCupData[k] = v
#
#################################################################################
#def GetRoleWorldCupData(role):
#	获取角色数据
#	role_worldCupData = role.GetObj(EnumObj.WorldCup)
#	if 1 not in role_worldCupData:
#		做一个版本修正
#		role.SetObj(EnumObj.WorldCup, {1 : set(), 2 : 0, 3 : 0, 4 : 0, 5 : {}})
#		return role.GetObj(EnumObj.WorldCup)
#	elif 5 not in role_worldCupData:
#		第二次修正
#		role_worldCupData[5] = {}
#		{阶段  : {组别 : {竞猜类型 : (队伍ID, 是否已经领奖)}}
#		return role_worldCupData
#	else:
#		return role_worldCupData
#
#################################################################################
#def RequestData(role, msg):
#	'''
#	请求打开世界杯面板
#	@param role:
#	@param msg:
#	'''
#	backId, _ = msg
#	role.CallBackFunction(backId, (GetRoleWorldCupData(role), WorldCupData.GetData()))
#
#
#def RequestGuess16(role, msg):
#	'''
#	请求竞猜世界杯16强
#	@param role:
#	@param msg:
#	'''
#	global WorldCupGuess16_Flag
#	if WorldCupGuess16_Flag is not True:
#		return
#	
#	if role.GetUnbindRMB() < WorldCupGuess16NeedUnbindRMB:
#		return
#	
#	role_worldCupData = GetRoleWorldCupData(role)
#	guessSet = role_worldCupData.get(1)
#	已经竞猜过了
#	if guessSet : return
#	
#	backId, teamIds = msg
#	验证ID正确性(ID唯一，并且有16个)
#	if len(teamIds) != len(set(teamIds)) or len(teamIds) != 16:
#		print "GE_EXC, RequestGuess16 teamIds error"
#		return
#	
#	groupCount = {}
#	for teamId in teamIds:
#		cfg = WorldCupConfig_Dict.get(teamId)
#		if not cfg:
#			print "GE_EXC, RequestGuess16 not this team (%s), roleId(%s)" % (teamId, role.GetRoleID())
#			return
#		记录这个组别选了多少个队伍
#		groupCount[cfg.group] = groupCount.get(cfg.group, 0) + 1
#	
#	if len(groupCount) != 8:
#		没有8组,参数有问题
#		print "GE_EXC, RequestGuess16 groupCount error"
#		return
#	
#	gCount = list(set(groupCount.values()))
#	if len(gCount) != 1:
#		每组2个，所以组对应队伍的数量的集合应该是1
#		print "GE_EXC, RequestGuess16 gCount error"
#		return
#	if gCount[0] != 2:
#		每组2个，所以组对应队伍的数量应该是2
#		print "GE_EXC, RequestGuess16 gCount team error"
#		return
#	
#	with Tra_WorldCup_Guess16:
#		扣钱，记录数据
#		role.DecUnbindRMB(WorldCupGuess16NeedUnbindRMB)
#		role_worldCupData[1] = set(teamIds)
#		
#	role.CallBackFunction(backId, None)
#
#def RequestGetGuessReward(role, msg):
#	'''
#	请求领取16强竞猜奖励
#	@param role:
#	@param msg:
#	'''
#	global WorldCupReward16_Flag
#	if WorldCupReward16_Flag is not True:
#		return
#	backId, _ = msg
#	
#	role_worldCupData = GetRoleWorldCupData(role)
#	teamIds = role_worldCupData.get(1)
#	if not teamIds:
#		return
#	
#	if role_worldCupData.get(3):
#		已经领取过了
#		return
#	
#	global WorldCupData
#	w_16 = WorldCupData[WorldCupKey_16]
#	if len(w_16) != 16 or len(teamIds) != 16:
#		print "GE_EXC, RequestGetGuessReward not enought team"
#		return
#	cnt = 0
#	for teamId in teamIds:
#		if teamId in w_16:
#			猜中一个奖励一个宝箱
#			cnt += 1
#	
#	with Tra_WorldCup_Guess16Reward:
#		role_worldCupData[3] = 1
#		role.AddItem(WorldCupItem, cnt)
#		
#	role.CallBackFunction(backId, None)
#	role.Msg(2, 0,GlobalPrompt.WorldCup_Tips_1 % (cnt, cnt))
#
#def RequestGuessChampion(role, msg):
#	'''
#	请求竞猜世界杯冠军
#	@param role:
#	@param msg:
#	'''
#	global WorldCupChampionGuess_Flag
#	if WorldCupChampionGuess_Flag is not True:
#		return
#	
#	backId, teamId = msg
#	if teamId < 1 or teamId > 32:
#		return
#	
#	if role.GetUnbindRMB() < WorldCunGuessChampionNeedUnbindRMB:
#		return
#	
#	role_worldCupData = GetRoleWorldCupData(role)
#	if role_worldCupData.get(2):
#		return
#	
#	with Tra_WorldCup_GuessChampion:
#		role.DecUnbindRMB(WorldCunGuessChampionNeedUnbindRMB)
#		role_worldCupData[2] = teamId
#		
#	role.CallBackFunction(backId, teamId)
#
#
#def RequestGetChampionReward(role, msg):
#	'''
#	请求领取竞猜世界杯冠军奖励
#	@param role:
#	@param msg:
#	'''
#	global WorldCupChampionReward_Flag
#	if WorldCupChampionReward_Flag is not True:
#		return
#	
#	backId, _ = msg
#	role_worldCupData = GetRoleWorldCupData(role)
#	
#	teamId = role_worldCupData.get(2)
#	if not teamId : return	#没有参与竞猜
#	if role_worldCupData.get(4) : return #已经领取了
#	
#	global WorldCupData
#	16强
#	w_16 = WorldCupData[WorldCupKey_16]
#	if len(w_16) != 16:
#		print "GE_EXC, error in RequestGetChampionReward not enought team 16"
#		return
#	if teamId not in w_16 : return #不能领奖
#	
#	cnt = 1
#	8强
#	w_8 = WorldCupData[WorldCupKey_8]
#	if len(w_8) != 8 : return #还没开始比赛，暂定不能领取
#	
#	if teamId not in w_8:
#		已经开始比赛完毕，出现了8强，但是竞猜的队伍不在之内，只能获得16强这个档次的奖励
#		ChampionReward(role, cnt, backId)
#		return
#	cnt += 2
#	
#	4强
#	w_4 = WorldCupData[WorldCupKey_4]
#	if len(w_4) != 4 : return
#	if teamId not in w_4:
#		ChampionReward(role, cnt, backId)
#		return
#	cnt += 4
#	
#	决赛
#	w_2 = WorldCupData[WorldCupKey_2]
#	if len(w_2) != 2 : return
#	if teamId not in w_2:
#		ChampionReward(role, cnt, backId)
#		return
#	cnt += 8
#	
#	冠军
#	championTeam = WorldCupData[WorldCupKey_1]
#	if not championTeam : return
#	if championTeam != teamId:
#		ChampionReward(role, cnt, backId)
#		return
#	cnt += 12 
#	ChampionReward(role, cnt, backId)
#
#def ChampionReward(role, cnt, backFunId):
#	冠军奖励
#	with Tra_WorldCup_GuessChampionReward:
#		role_worldCupData = GetRoleWorldCupData(role)
#		role_worldCupData[4] = 1
#		role.AddItem(WorldCupItem, cnt)
#	
#	role.CallBackFunction(backFunId, None)
#	role.Msg(2, 0,GlobalPrompt.WorldCup_Tips_2 % cnt)
#
############################################################################
#def WorldCupGroupGuess(role, msg):
#	'''
#	淘汰赛投注(stage 16, 8, 4, 季军3)
#	@param role:
#	@param msg:
#	'''
#	backId, (stage, group, teamId, guessType) = msg
#	
#	if guessType != 1 and guessType != 2:
#		return
#	
#	if stage not in [16, 8, 4, 3] : return
#	
#	看看对应的活动是否开启
#	global StageGroupFlagDict
#	gd = StageGroupFlagDict.get(stage)
#	if not gd : return
#	flag = gd.get(group)
#	if not flag : return
#	
#	global CircularStartFlags
#	if flag[0] not in CircularStartFlags:
#		活动没开启
#		return
#	
#	取持久化数据验证组别队伍信息
#	keys = StageTokey.get(stage)
#	if not keys:
#		return
#	判断是否有这一组
#	groupteams = WorldCupData[keys[1]].get(group)
#	if not groupteams:
#		还没有这组的对战数据
#		return
#	if teamId not in groupteams:
#		这个队伍不是这个组的
#		return
#	
#	role_worldCupData = GetRoleWorldCupData(role)
#	stagegroupdata = role_worldCupData[5]
#	
#	rolegroupdata = stagegroupdata.get(stage)
#	if rolegroupdata:
#		有竞猜过这个阶段的数据
#		if group in rolegroupdata:
#			有竞猜过这个组别
#			if guessType in rolegroupdata[group]:
#				已经用过这种竞猜类型了
#				return
#	else:
#		stagegroupdata[stage] = rolegroupdata = {}
#	
#	with Tra_WorldCup_GuessGroup:
#		if guessType == 1:
#			if role.GetMoney() < WorldCupGroupGuessNeedMoney:
#				return
#			role.DecMoney(WorldCupGroupGuessNeedMoney)
#		else:
#			if role.GetUnbindRMB() < WorldCupGroupGuessNeedUnbindRMB:
#				return
#			role.DecUnbindRMB(WorldCupGroupGuessNeedUnbindRMB)
#	
#	if group not in rolegroupdata:
#		第一次对这个组别进行竞猜
#		rolegroupdata[group] = {guessType : (teamId, 0)}
#	else:
#		第二次竞猜,记录{竞猜类型 ： (竞猜队伍, 是否领奖)}
#		rolegroupdata[group][guessType] = (teamId, 0)
#
#	role.CallBackFunction(backId, stagegroupdata)
#	
#def WorldCupGroupReward(role, msg):
#	'''
#	领取淘汰赛奖励
#	@param role:
#	@param msg:
#	'''
#	backId, (stage, group, guessType) = msg
#	if guessType != 1 and guessType != 2:
#		return
#	
#	if stage not in [16, 8, 4, 3] : return
#	
#	global StageGroupFlagDict
#	gd = StageGroupFlagDict.get(stage)
#	if not gd:
#		return
#	flag = gd.get(group)
#	if not flag:
#		return
#	
#	global CircularStartFlags
#	if flag[1] not in CircularStartFlags:
#		活动没开启
#		return
#	
#	keys = StageTokey.get(stage)
#	if not keys:
#		return
#	判断是否有这一组
#	results = WorldCupData[keys[2]].get(group)
#	if not results:
#		还没有这组的对战结果
#		return
#	result结构 ｛队伍id : 进球数｝
#	winteamId = 0
#	wingoal = 0
#	for teamId, goal in  results.items():
#		if wingoal < goal:
#			winteamId = teamId
#			wingoal = goal
#	
#	role_worldCupData = GetRoleWorldCupData(role)
#	stagegroupdata = role_worldCupData[5]
#	
#	rolegroupdata = stagegroupdata.get(stage)
#	if not rolegroupdata:
#		return
#	
#	guessData = rolegroupdata.get(group)
#	if not guessData:
#		return
#	
#	guessTypeData = guessData.get(guessType)
#	if not guessTypeData:
#		return
#	
#	guessTeamId, isGetReward = guessTypeData
#	if isGetReward != 0:
#		已经领取过了
#		return
#	
#	记录已经领取
#	guessData[guessType] = (guessTeamId, 1)
#	发放奖励
#	rewardItem = None
#	with Tra_WorldCup_GuessGroupReward:
#		if guessTeamId != winteamId:
#			猜错奖励
#			if guessType == 1:
#				rewardItem = WorldCupRewardConfig_Dict.get(WCReward_Group_Money_Lose)
#				if rewardItem:
#					role.AddItem(*rewardItem)
#			else:
#				rewardItem = WorldCupRewardConfig_Dict.get(WCReward_Group_RMB_Lose)
#				if rewardItem:
#					role.AddItem(*rewardItem)
#		else:
#			猜对奖励
#			if guessType == 1:
#				rewardItem = WorldCupRewardConfig_Dict.get(WCReward_Group_Money_Win)
#				if rewardItem:
#					role.AddItem(*rewardItem)
#			else:
#				rewardItem = WorldCupRewardConfig_Dict.get(WCReward_Group_RMB_Win)
#				if rewardItem:
#					role.AddItem(*rewardItem)
#	
#	role.Msg(2, 0, GlobalPrompt.WorldCup_Gjjc_Msg_1 % rewardItem)
#
#	role.CallBackFunction(backId, stagegroupdata)
#
#def WorldCupJuesaiGuess(role, msg):
#	'''
#	世界杯决赛竞猜(另外一种猜冠军模式)
#	@param role:
#	@param msg:
#	'''
#	backId, (teamId, guessType) = msg
#	if guessType != 1 and guessType != 2:
#		return
#	global CircularStartFlags
#	if CircularDefine.CA_WorldCupGuessJueSai not in CircularStartFlags:
#		return
#	stage = 2
#	group = 1
#	global WorldCupData
#	keys = StageTokey[stage]
#	
#	判断是否有这一组
#	groupteams = WorldCupData[keys[1]].get(group)
#	if not groupteams:
#		还没有这组的对战数据
#		return
#	if teamId not in groupteams:
#		这个队伍不是这个组的
#		return
#	
#	stagegroupdata = GetRoleWorldCupData(role)[5]
#	
#	rolegroupdata = stagegroupdata.get(stage)
#	if rolegroupdata:
#		有竞猜过这个阶段的数据
#		if group in rolegroupdata:
#			有竞猜过这个组别
#			if guessType in rolegroupdata[group]:
#				已经用过这种竞猜类型了
#				return
#	else:
#		stagegroupdata[stage] = rolegroupdata = {}
#	
#	with Tra_WorldCup_GuessJuesai:
#		if guessType == 1:
#			if role.GetMoney() < WorldCupJueSaiGuessNeedMoney:
#				return
#			role.DecMoney(WorldCupJueSaiGuessNeedMoney)
#		else:
#			if role.GetUnbindRMB() < WorldCupJueSaiGuessNeedUnbindRMB:
#				return
#			role.DecUnbindRMB(WorldCupJueSaiGuessNeedUnbindRMB)
#			
#			role.AddPet(4)
#			cRoleMgr.Msg(1, 0, GlobalPrompt.WorldCup_Gjjc_Msg % role.GetRoleName())
#	
#	if group not in rolegroupdata:
#		第一次对这个组别进行竞猜
#		rolegroupdata[group] = {guessType : (teamId, 0)}
#	else:
#		第二次竞猜,记录{竞猜类型 ： (竞猜队伍, 是否领奖)}
#		rolegroupdata[group][guessType] = (teamId, 0)
#	
#	role.CallBackFunction(backId, stagegroupdata)
#
#
#def WorldCupJuesaiReward(role, msg):
#	'''
#	世界杯决赛奖励
#	@param role:
#	@param msg:
#	'''
#	global CircularStartFlags
#	if CircularDefine.CA_WorldCupRewardJueSai not in CircularStartFlags:
#		return
#	
#	backId, guessType = msg
#	guessType = guessType[0]
#	if guessType != 1 and guessType != 2:
#		return
#	stage = 2
#	group = 1
#	global WorldCupData
#	keys = StageTokey.get(stage)
#	if not keys:
#		return
#	判断是否有这一组
#	results = WorldCupData[keys[2]].get(group)
#	if not results:
#		还没有这组的对战结果
#		return
#	result结构 ｛队伍id : 进球数｝
#	winteamId = 0
#	wingoal = 0
#	for teamId, goal in  results.items():
#		if wingoal < goal:
#			winteamId = teamId
#			wingoal = goal
#	
#	role_worldCupData = GetRoleWorldCupData(role)
#	stagegroupdata = role_worldCupData[5]
#	
#	rolegroupdata = stagegroupdata.get(stage)
#	if not rolegroupdata:
#		return
#	
#	guessData = rolegroupdata.get(group)
#	if not guessData:
#		return
#	
#	guessTypeData = guessData.get(guessType)
#	if not guessTypeData:
#		return
#	
#	guessTeamId, isGetReward = guessTypeData
#	if isGetReward != 0:
#		已经领取过了
#		return
#	
#	记录已经领取
#	guessData[guessType] = (guessTeamId, 1)
#	发放奖励
#	rewardItem = None
#	with Tra_WorldCup_GuessJuesaiReward:
#		if guessTeamId != winteamId:
#			猜错奖励
#			if guessType == 1:
#				rewardItem = WorldCupRewardConfig_Dict.get(WCReward_JueSai_Money_Lose)
#				if rewardItem:
#					role.AddItem(*rewardItem)
#			else:
#				rewardItem = WorldCupRewardConfig_Dict.get(WCReward_JueSai_RMB_Lose)
#				if rewardItem:
#					role.AddItem(*rewardItem)
#		else:
#			猜对奖励
#			if guessType == 1:
#				rewardItem = WorldCupRewardConfig_Dict.get(WCReward_JueSai_Money_Win)
#				if rewardItem:
#					role.AddItem(*rewardItem)
#			else:
#				rewardItem = WorldCupRewardConfig_Dict.get(WCReward_JueSai_RMB_Win)
#				if rewardItem:
#					role.AddItem(*rewardItem)
#	
#	role.Msg(2, 0, GlobalPrompt.WorldCup_Gjjc_Msg_1 % rewardItem)
#	
#	role.CallBackFunction(backId, stagegroupdata)
#
#def StartCircularActive(param, activeType):
#	活动开启触发事件
#	if activeType == CircularDefine.CA_WorldCupGuess16:
#		global WorldCupGuess16_Flag
#		if WorldCupGuess16_Flag is True:
#			print "GE_EXC, repeat start WorldCupGuess16_Flag"
#			return
#		WorldCupGuess16_Flag = True
#		return
#	
#	if activeType == CircularDefine.CA_WorldCupReward16:
#		global WorldCupReward16_Flag
#		if WorldCupReward16_Flag is True:
#			print "GE_EXC, repeat start WorldCupReward16_Flag"
#			return
#		WorldCupReward16_Flag = True
#		return
#	
#	if activeType == CircularDefine.CA_WorldCupChampionGuess:
#		global WorldCupChampionGuess_Flag
#		if WorldCupChampionGuess_Flag is True:
#			print "GE_EXC, repeat start WorldCupChampionGuess_Flag"
#			return
#		WorldCupChampionGuess_Flag = True
#		return
#	
#	if activeType == CircularDefine.CA_WorldCupChampionReward:
#		global WorldCupChampionReward_Flag
#		if WorldCupChampionReward_Flag is True:
#			print "GE_EXC, repeat start WorldCupChampionReward_Flag"
#			return
#		WorldCupChampionReward_Flag = True
#		return
#	
#	
#	global CircularStartFlags
#	CircularStartFlags.add(activeType)
#	
#
#def EndCircularActive(param, activeType):
#	活动结束触发事件
#	if activeType == CircularDefine.CA_WorldCupGuess16:
#		global WorldCupGuess16_Flag
#		if WorldCupGuess16_Flag is False:
#			print "GE_EXC, repeat End WorldCupGuess16_Flag"
#			return
#		WorldCupGuess16_Flag = False
#		return
#	
#	if activeType == CircularDefine.CA_WorldCupReward16:
#		global WorldCupReward16_Flag
#		if WorldCupReward16_Flag is False:
#			print "GE_EXC, repeat End WorldCupReward16_Flag"
#			return
#		WorldCupReward16_Flag = False
#		return
#	
#	if activeType == CircularDefine.CA_WorldCupChampionGuess:
#		global WorldCupChampionGuess_Flag
#		if WorldCupChampionGuess_Flag is False:
#			print "GE_EXC, repeat End WorldCupChampionGuess_Flag"
#			return
#		WorldCupChampionGuess_Flag = False
#		return
#	
#	if activeType == CircularDefine.CA_WorldCupChampionReward:
#		global WorldCupChampionReward_Flag
#		if WorldCupChampionReward_Flag is False:
#			print "GE_EXC, repeat End WorldCupChampionReward_Flag"
#			return
#		WorldCupChampionReward_Flag = False
#		return
#	
#	global CircularStartFlags
#	CircularStartFlags.discard(activeType)
#
#if "_HasLoad" not in dir():
#	if Environment.HasLogic:
#		LoadWorldCupConfig()
#		LoadWorldCupRewardConfig()
#		
#		WorldCupGuess16_Flag = False
#		WorldCupReward16_Flag = False
#		WorldCupChampionGuess_Flag = False
#		WorldCupChampionReward_Flag = False
#		
#		Event.RegEvent(Event.Eve_StartCircularActive, StartCircularActive)
#		Event.RegEvent(Event.Eve_EndCircularActive, EndCircularActive)
#		
#		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WorldCup_RequestData", "请求世界杯数据"), 	RequestData)
#		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WorldCup_RequestGuess16", "请求竞猜世界杯16强"), 	RequestGuess16)
#		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WorldCup_RequestGuessChampion", "请求竞猜世界杯冠军"), 	RequestGuessChampion)
#		
#		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WorldCup_RequestGetGuessReward", "请求领取竞猜世界杯16强奖励"), 	RequestGetGuessReward)
#		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WorldCup_RequestGetChampionReward", "请求领取竞猜世界杯冠军奖励"), 	RequestGetChampionReward)
#		
#		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WorldCup_RequestWorldCupGroupGuess", "请求淘汰赛投注(16, 8, 4, 季军)"), 	WorldCupGroupGuess)
#		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WorldCup_RequestWorldCupGroupReward", "请求领取竞猜淘汰赛奖励"), 	WorldCupGroupReward)
#		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WorldCup_RequestWorldCupJuesaiGuess", "请求世界杯决赛竞猜"), 	WorldCupJuesaiGuess)
#		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WorldCup_RequestWorldCupJuesaiReward", "请求领取世界杯决赛奖励"), 	WorldCupJuesaiReward)
#		
#		
#		日志
#		Tra_WorldCup_Guess16 = AutoLog.AutoTransaction("Tra_WorldCup_Guess16", "世界杯竞猜16强")
#		Tra_WorldCup_GuessChampion = AutoLog.AutoTransaction("Tra_WorldCup_GuessChampion", "世界杯竞猜冠军")
#		Tra_WorldCup_Guess16Reward = AutoLog.AutoTransaction("Tra_WorldCup_Guess16Reward", "世界杯竞猜16强奖励")
#		Tra_WorldCup_GuessChampionReward = AutoLog.AutoTransaction("Tra_WorldCup_GuessChampionReward", "世界杯竞猜冠军奖励")
#		
#		
#		
#		Tra_WorldCup_GuessGroup = AutoLog.AutoTransaction("Tra_WorldCup_GuessGroup", "世界杯竞猜淘汰赛")
#		Tra_WorldCup_GuessJuesai = AutoLog.AutoTransaction("Tra_WorldCup_GuessJuesai", "世界杯竞猜决赛")
#		Tra_WorldCup_GuessGroupReward = AutoLog.AutoTransaction("Tra_WorldCup_GuessGroupReward", "世界杯竞猜淘汰赛奖励")
#		Tra_WorldCup_GuessJuesaiReward = AutoLog.AutoTransaction("Tra_WorldCup_GuessJuesaiReward", "世界杯竞猜决赛奖励")
#		
#		
#		
#		
#	if Environment.HasLogic or Environment.HasWeb:
#		WorldCupData = Contain.Dict("WorldCupData", (2014, 7, 17), AfterLoadWorldCupDataDB)
#		
#		
