#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionCreate")
#===============================================================================
# 公会创建
#===============================================================================
import cRoleMgr
import cSceneMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.API import QQHttp
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumTempObj
from Game.Scene import PublicScene, SceneMgr
from Game.Union import UnionMgr, UnionDefine



if "_HasLoad" not in dir():
	pass
	
	
def CreateUnion(role, unionName):
	'''
	创建公会
	@param role:
	@param unionName:
	'''
	#是否有阵营
	campId = role.GetCampID()
	if not campId:
		return
	
	campId = role.GetCampID()
	#如果该方阵营公会数量超过上限
	if campId == 1:
		if len(UnionMgr.UNION_LEFT_CAMP_LIST) + 1 > EnumGameConfig.UnionCntMax:
			role.Msg(2, 0, GlobalPrompt.UnionCntMaxTips)
			return
	elif campId == 2:
		if len(UnionMgr.UNION_RIGHT_CAMP_LIST) + 1 > EnumGameConfig.UnionCntMax:
			role.Msg(2, 0, GlobalPrompt.UnionCntMaxTips)
			return
	else:
		return
	
	#北美版
	if Environment.EnvIsNA():
		#优先扣魔晶
		if role.GetBindRMB() >= EnumGameConfig.Union_NA_Create_Need_Bind_RMB:
			#日志
			with TraCreateUnion:
				role.DecBindRMB(EnumGameConfig.Union_NA_Create_Need_Bind_RMB)
		else:
			if role.GetUnbindRMB() < EnumGameConfig.Union_Create_Need_RMB:
				return
			#日志
			with TraCreateUnion:
				role.DecUnbindRMB(EnumGameConfig.Union_Create_Need_RMB)
	else:
		#是否有足够的神石
		if role.GetUnbindRMB() < EnumGameConfig.Union_Create_Need_RMB:
			return
		#日志
		with TraCreateUnion:
			role.DecUnbindRMB(EnumGameConfig.Union_Create_Need_RMB)
	
	roleId = role.GetRoleID()
	
	unionId = UnionMgr.AllotUnionID()
	
	unionObj = UnionMgr.Union({"union_id": unionId, "camp_id": role.GetCampID(), 
							"name": unionName, "leader_id": roleId, 
							"leader_name": role.GetRoleName()})
	
	unionObj.NewMember(role, UnionDefine.LEADER_JOB_ID)
	
	#保存
	unionObj.HasChange()
	
	#公会对象加入阵营公会列表中
	if campId == 1:
		UnionMgr.UNION_LEFT_CAMP_LIST.append(unionObj)
	elif campId == 2:
		UnionMgr.UNION_RIGHT_CAMP_LIST.append(unionObj)
	else:
		pass
	
	#缓存公会对象
	UnionMgr.UNION_OBJ_DICT[unionId] = unionObj
	
	#创建公会场景
	CreateUnionScene(unionId)
	
	#通知客户端
	role.SendObj(UnionMgr.Union_Success_Join_In, None)
	role.GetPropertyMgr().ResetGlobalUnionSkillProperty()
	UnionMgr.ShowMainPanel(role)
	
	#提示
	role.Msg(2, 0, GlobalPrompt.UNION_CREATE_SUCCESS_PROMPT)

def CreateUnionScene(unionId):
	#创建每个公会的公会驻地场景
	SCPS = cSceneMgr.CreatePublicScene
	#获取注册的场景相关函数
	PSCG = PublicScene.SceneCreateFun.get
	PSJG = PublicScene.SceneJoinFun.get
	PSBG = PublicScene.SceneBeforeLeaveFun.get
	PSRG = PublicScene.SceneRestoreFun.get
	unionSceneConfig = SceneMgr.SceneConfig_Dict.get(UnionDefine.UNION_STATION_SCENE_ID)
	if unionSceneConfig:
		SID = unionId
		SCPS(SID, unionSceneConfig.SceneName, unionSceneConfig.MapId, unionSceneConfig.AreaSize, unionSceneConfig.IsSaveData, unionSceneConfig.CanSeeOther, PSCG(SID), PSJG(SID), PSBG(SID), PSRG(SID))

#===============================================================================
# 腾讯接口返回
#===============================================================================
def OnCheckArmyName(response, regparam):
	role, unionName = regparam
	if response is None:
		return
	code, body = response
	if code != 200:
		return
	body = eval(body)
	if body["ret"] != 0:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_QQ_NOT_LOGIN)
		return
	#判断是否有敏感字
	if body["is_dirty"] != 0:
		return
	
	#过滤后再判断一次
	#是否已经加入军团
	if role.GetUnionID():
		return
	
	CreateUnion(role, unionName)
	
	
#===============================================================================
# 客户端消息
#===============================================================================
def RequestCreateUnion(role, msg):
	'''
	客户端请求创建公会
	@param role:
	@param msg:
	'''
	unionName = msg
	
	#等级是否满足条件
	if role.GetLevel() < UnionDefine.UNION_NEED_LEVEL:
		return
	
	#是否已经加入阵营
	if not role.GetCampID():
		return
	
	
	#是否已经加入军团
	if role.GetUnionID():
		return
	
	#是否超过长度
	if len(unionName) > UnionDefine.UNION_NAME_LEN_MAX:
		return
	
	#名字是否有空格或者Tab
	if unionName.count(' ') or unionName.count('\t'):
		return
	
	#判断名字是否有重复
	btData = UnionMgr.BT.GetData()
	nameList = [union["name"] for union in btData.itervalues()]
	if unionName in nameList:
		#提示
		role.Msg(2, 0, GlobalPrompt.UNION_NAME_REPEAT)
		return
	
	#QQ平台过滤公会名
	if Environment.EnvIsQQ():
		login_info = role.GetTempObj(EnumTempObj.LoginInfo)
		openid = login_info["account"]
		openkey = login_info["openkey"]
		pf = login_info["pf"]
		#过滤军团名
		QQHttp.word_filter(openid, openkey, pf, unionName, OnCheckArmyName, (role, unionName))
		return
	else:
		CreateUnion(role, unionName)
		
		
if "_HasLoad" not in dir():
	#日志
	TraCreateUnion = AutoLog.AutoTransaction("TraCreateUnion", "创建公会")
	if Environment.HasLogic and not Environment.IsCross:
		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Create", "客户端请求创建公会"), RequestCreateUnion)
	
	
