#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionTask")
#===============================================================================
# 公会任务
#===============================================================================
import random
import cDateTime
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Fight import FightEx
from Game.Role import Status, Event
from Game.Role.Data import EnumInt1, EnumDayInt8, EnumCD
from Game.Union import UnionDefine, UnionConfig, UnionMgr

if "_HasLoad" not in dir():
	UNION_TASK_MAX_STAR = 5		#公会任务最高星级
	UNION_TASK_INVITE_CD = 60	#公会任务邀请提星CD
	
	HELP_OTHER_RECORD_DICT = {}		#帮助其他人记录字典
	OTHER_HELP_ME_RECORD_DICT = {}	#其他人帮助我记录字典
	
	#消息
	Union_Task_Show_Task_Data = AutoMessage.AllotMessage("Union_Task_Show_Task_Data", "通知客户端显示公会任务数据")
	Union_Task_Show_Task_Panel = AutoMessage.AllotMessage("Union_Task_Show_Task_Panel", "通知客户端显示公会任务面板")
	Union_Task_Show_Task_Star_Panel = AutoMessage.AllotMessage("Union_Task_Show_Task_Star_Panel", "通知客户端显示公会任务提星面板")
	
def RandomUnionTask(role):
	#随机一个公会任务为可接取状态
	level = role.GetLevel()
	randomObj = UnionConfig.UNION_TASK_LEVEL_RANDOM_DICT.get(level)
	if not randomObj:
		print "GE_EXC, error in RandomUnionTask not random roleLevel(%s)" % level
		return 0
	taskIndex = randomObj.RandomOne()
	
	return taskIndex

def UnionGetTask(role):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	if role.GetDI8(EnumDayInt8.UnionTaskCnt) >= EnumGameConfig.UNION_TASK_DAY_CNT:
		return
	
	roleId = role.GetRoleID()
	#是否已经接了任务
	if roleId in unionObj.other_data[UnionDefine.O_TASK_IDX]:
		return
	
	#随机任务ID
	taskIdx = RandomUnionTask(role)
	if not taskIdx:
		return
	taskConfig = UnionConfig.UNION_TASK.get(taskIdx)
	if not taskConfig:
		return
	
	role.IncDI8(EnumDayInt8.UnionTaskCnt, 1)
	
	#随机任务星级
	randomStar = random.randint(1, 3)
	
	taskDataDict = {UnionDefine.TASK_ID_IDX: taskIdx, UnionDefine.TASK_STAR_IDX: randomStar, UnionDefine.TASK_HELP_ME_IDX: []}
	if taskConfig.killNpcId1:
		taskDataDict[1] = 0
	if taskConfig.killNpcId2:
		taskDataDict[2] = 0
	unionObj.other_data[UnionDefine.O_TASK_IDX][roleId] = taskDataDict
	
	#保存
	unionObj.HasChange()
	
	role.SendObj(Union_Task_Show_Task_Data, taskDataDict)
	
def UnionTaskAttackMonster(role, npcId):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return

	roleId = role.GetRoleID()
	#是否已经接了任务
	if roleId not in unionObj.other_data[UnionDefine.O_TASK_IDX]:
		return

	taskDataDict = unionObj.other_data[UnionDefine.O_TASK_IDX][roleId]
	taskIdx = taskDataDict[UnionDefine.TASK_ID_IDX]
	
	config = UnionConfig.UNION_TASK.get(taskIdx)
	if not config:
		return
	
	npcData = config.m_dict.get(npcId)
	if not npcData:
		return
	
	monsterIndex, fightCampID, sceneId, posX, posY, clickLen = npcData
	#判断是否可以攻击
	if taskDataDict.get(monsterIndex) != 0:
		return
	
	if role.GetSceneID() != sceneId:
		return
	
	rolePosX, rolePosY = role.GetPos()
	if abs(rolePosX - posX) > clickLen * 2:
		return
	if abs(rolePosY - posY) > clickLen * 2:
		return
	#战斗状态
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
		return
	#进入战斗，战斗胜利回调触发完成一个子任务
	FightEx.PVE_UnionTask(role, fightCampID, 0, None, monsterIndex, None, AfterPlayUnionTask)

def AfterPlayUnionTask(fightObj):
	#战斗回调
	if fightObj.result != 1:
		return
	
	roles = fightObj.left_camp.roles
	if not roles:
		return
	role = list(roles)[0]
	monsterIndex = fightObj.after_fight_param
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return

	roleId = role.GetRoleID()
	#是否已经接了任务
	if roleId not in unionObj.other_data[UnionDefine.O_TASK_IDX]:
		return

	roleTaskDataDict = unionObj.other_data[UnionDefine.O_TASK_IDX][roleId]
	if roleTaskDataDict.get(monsterIndex) != 0:
		return
	roleTaskDataDict[monsterIndex] = 1
	
	#保存
	unionObj.HasChange()
	
	#是否完成任务
	if roleTaskDataDict[UnionDefine.TASK_MONSTER_1]:
		if UnionDefine.TASK_MONSTER_2 not in roleTaskDataDict or roleTaskDataDict[UnionDefine.TASK_MONSTER_2]:
			#完成任务
			taskId = roleTaskDataDict[UnionDefine.TASK_ID_IDX]
			star = roleTaskDataDict[UnionDefine.TASK_STAR_IDX]
			taskConfig = UnionConfig.UNION_TASK.get(taskId)
			if taskConfig:
				#日志
				with TraUnionTaskFinish:
					#奖励
					taskConfig.RewardRole(role, star)
			
			#删除任务相关
			DelUnionTask(role, unionObj)
			
			#同步客户端
			role.SendObj(Union_Task_Show_Task_Data, {})
			
			#活跃度 -- 公会任务
			Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_UnionTask, 1))
			
			return
		
	#同步客户端
	role.SendObj(Union_Task_Show_Task_Data, roleTaskDataDict)
	
def DelUnionTask(role, unionObj):
	roleId = role.GetRoleID()
	taskDataDict = unionObj.other_data[UnionDefine.O_TASK_IDX]
	
	#删除帮助我的成员记录的帮助信息
	helpMeRoleIdList = taskDataDict[roleId][UnionDefine.TASK_HELP_ME_IDX]
	for helpMeRoleId in helpMeRoleIdList:
		if not unionObj.IsMember(helpMeRoleId):
			continue
		helpRoleIdList =  unionObj.other_data[UnionDefine.O_TASK_HELP_OTHER_LIST_IDX].get(helpMeRoleId, [])
		if roleId in helpRoleIdList:
			helpRoleIdList.remove(roleId)
	
	del taskDataDict[roleId]
	
	#保存
	unionObj.HasChange()
	
	role.SendObj(Union_Task_Show_Task_Data, {})
	
def UnionTaskUpgradeStar(role, desRoleId):
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	
	if roleId == desRoleId:
		return
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	if not unionObj.IsMember(desRoleId):
		return
	
	#是否有提星次数
	if role.GetDI8(EnumDayInt8.UnionTaskHelpCnt) >= EnumGameConfig.UNION_TASK_DAY_HELP_CNT:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_TASK_NO_HELP_CNT)
		return
	
	#是否已经帮助过此玩家
	helpRoleIdList =  unionObj.other_data[UnionDefine.O_TASK_HELP_OTHER_LIST_IDX].setdefault(role.GetRoleID(), [])
	if desRoleId in helpRoleIdList:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_TASK_HAS_HELPED)
		return
	
	#被提星的成员是否有公会任务
	taskDataDict = unionObj.other_data[UnionDefine.O_TASK_IDX]
	if desRoleId not in taskDataDict:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_TASK_FINISHED_HELP_FAIL)
		return
	desRoleTaskDataDict = taskDataDict[desRoleId]
	if roleId in desRoleTaskDataDict[UnionDefine.TASK_HELP_ME_IDX]:
		return
	
	#是否达到最高星级
	if desRoleTaskDataDict[UnionDefine.TASK_STAR_IDX] >= UNION_TASK_MAX_STAR:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_TASK_STAR_FULL)
		return
	
	#提星
	role.IncDI8(EnumDayInt8.UnionTaskHelpCnt, 1)
	desRoleTaskDataDict[UnionDefine.TASK_STAR_IDX] += 1
	
	helpRoleIdList.append(desRoleId)
	desRoleTaskDataDict[UnionDefine.TASK_HELP_ME_IDX].append(role.GetRoleID())
	
	unionObj.IncUnionTaskHelpCnt(roleId)
	
	#记录提星和被提星信息
	global HELP_OTHER_RECORD_DICT
	global OTHER_HELP_ME_RECORD_DICT
	days = cDateTime.Days()
	helpOtherRecordDict = {}
	otherHelpMeRecordDict = {}
	desRoleTaskStar = desRoleTaskDataDict[UnionDefine.TASK_STAR_IDX]
	
	if days not in HELP_OTHER_RECORD_DICT:
		HELP_OTHER_RECORD_DICT[days] = helpOtherRecordDict = {}
	else:
		helpOtherRecordDict = HELP_OTHER_RECORD_DICT[days]
	helpRecordList = helpOtherRecordDict.setdefault(roleId, [])
	helpRecordList.append((desRoleId, unionObj.GetMemberName(desRoleId), desRoleTaskStar))
	
	if days not in OTHER_HELP_ME_RECORD_DICT:
		OTHER_HELP_ME_RECORD_DICT[days] = otherHelpMeRecordDict = {}
	else:
		otherHelpMeRecordDict = OTHER_HELP_ME_RECORD_DICT[days]
	otherHelpMeRecordList = otherHelpMeRecordDict.setdefault(desRoleId, [])
	otherHelpMeRecordList.append((roleId, roleName, desRoleTaskStar))
	
	#保存
	unionObj.HasChange()
	
	#显示面板
	ShowUnionTaskPanel(role)
	ShowUnionTaskStarPanel(role)
	
	#提示
	role.Msg(2, 0, GlobalPrompt.UNION_TASK_UPGRADE_SUCCESS)
	desRole = cRoleMgr.FindRoleByRoleID(desRoleId)
	if desRole:
		#同步任务
		desRole.SendObj(Union_Task_Show_Task_Data, desRoleTaskDataDict)
		#提示
		desRole.Msg(2, 0, GlobalPrompt.UNION_TASK_WHO_HELP_YOU % (roleName, desRoleTaskStar))
	
#===============================================================================
# 显示
#===============================================================================
def ShowUnionTaskData(role):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	taskDataDict = unionObj.other_data[UnionDefine.O_TASK_IDX].get(role.GetRoleID(), {})
	
	role.SendObj(Union_Task_Show_Task_Data, taskDataDict)

def ShowUnionTaskPanel(role):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	roleId = role.GetRoleID()
	
	helpOtherRecordDict = {}
	for days, recordDict in HELP_OTHER_RECORD_DICT.iteritems():
		helpOtherRecordDict[days] = recordDict.get(roleId, [])
		
	otherHelpMeRecordDict = {}
	for days, recordDict in OTHER_HELP_ME_RECORD_DICT.iteritems():
		otherHelpMeRecordDict[days] = recordDict.get(roleId, [])
	
	taskDataDict = unionObj.other_data[UnionDefine.O_TASK_IDX].get(role.GetRoleID(), {})
	star = taskDataDict.get(UnionDefine.TASK_STAR_IDX, 0)
	
	role.SendObj(Union_Task_Show_Task_Panel, (star, helpOtherRecordDict, otherHelpMeRecordDict))
	
def ShowUnionTaskStarPanel(role):
	unionObj = role.GetUnionObj()
	if not unionObj:
		return

	roleId = role.GetRoleID()
	taskDict = unionObj.other_data[UnionDefine.O_TASK_IDX]
	
	sendList = []
	#是否已经接了任务
	for memberId, memberTask in taskDict.iteritems():
		#名字，任务索引，星级，助人次数，是否帮助过提星
		sendList.append((memberId, 
						unionObj.GetMemberName(memberId), 
						memberTask[UnionDefine.TASK_ID_IDX], 
						memberTask[UnionDefine.TASK_STAR_IDX], 
						unionObj.GetMemberHelpTaskCnt(memberId), 
						0 if roleId in memberTask[UnionDefine.TASK_HELP_ME_IDX] else 1))
	
	role.SendObj(Union_Task_Show_Task_Star_Panel, sendList)
	
#===============================================================================
# 事件
#===============================================================================
def SyncRoleOtherData(role, param):
	ShowUnionTaskData(role)

#===============================================================================
# 客户端请求
#===============================================================================
def RequestUnionOpenTaskPanel(role, msg):
	'''
	客户端请求打开公会任务面板
	@param role:
	@param msg:
	'''
	ShowUnionTaskPanel(role)
	
def RequestUnionOpenTaskStarPanel(role, msg):
	'''
	客户端请求打开公会任务提星面板
	@param role:
	@param msg:
	'''
	ShowUnionTaskStarPanel(role)

def RequestUnionGetTask(role, msg):
	'''
	客户端请求领取公会任务
	@param role:
	@param msg:
	'''
	UnionGetTask(role)
	
def RequestUnionTaskAttackMonster(role, msg):
	'''
	客户端请求攻击公会任务怪物
	@param role:
	@param msg:
	'''
	npcId = msg
	
	UnionTaskAttackMonster(role, npcId)
	
def RequestUnionTaskUpgradeStar(role, msg):
	'''
	客户端请求公会任务提星
	@param role:
	@param msg:
	'''
	desRoleId = msg
	
	UnionTaskUpgradeStar(role, desRoleId)
	
def RequestUnionTaskInviteUpgradeStar(role, msg):
	'''
	客户端请求邀请成员给公会任务提星
	@param role:
	@param msg:
	'''
	#CD
	if role.GetCD(EnumCD.UnionTaskInviteCD):
		return
	role.SetCD(EnumCD.UnionTaskInviteCD, UNION_TASK_INVITE_CD)
	
	unionObj = role.GetUnionObj()
	if not unionObj:
		return
	
	roleId = role.GetRoleID()
	#是否有领取公会任务
	taskDataDict = unionObj.other_data[UnionDefine.O_TASK_IDX]
	if roleId not in taskDataDict:
		return
	
	#是否达到最高星级
	if taskDataDict[roleId][UnionDefine.TASK_STAR_IDX] >= UNION_TASK_MAX_STAR:
		return
	
	#公会频道
	UnionMgr.UnionMsg(unionObj, GlobalPrompt.UNION_TASK_INVITE_MSG % (role.GetRoleName(), roleId))
	
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#事件
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		
		#日志
		TraUnionTaskFinish = AutoLog.AutoTransaction("TraUnionTaskFinish", "公会任务完成")
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Task_Panel", "客户端请求打开公会任务面板"), RequestUnionOpenTaskPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Task_Star_Panel", "客户端请求打开公会任务提星面板"), RequestUnionOpenTaskStarPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Get_Task", "客户端请求领取公会任务"), RequestUnionGetTask)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Task_Attack_Monster", "客户端请求攻击公会任务怪物"), RequestUnionTaskAttackMonster)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Task_Upgrade_Star", "客户端请求公会任务提星"), RequestUnionTaskUpgradeStar)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Task_Invite_Upgrade_Star", "客户端请求邀请成员给公会任务提星"), RequestUnionTaskInviteUpgradeStar)
		