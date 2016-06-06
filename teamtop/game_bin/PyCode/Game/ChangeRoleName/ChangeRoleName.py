#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ChangeRoleName.ChangeRoleName")
#===============================================================================
# 改名
#===============================================================================
import Environment
import cProcess
import cRoleMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.API import QQHttp
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.DB import DBProxy
from Game.Role import Event, RoleMgr, Call
from Game.Role.Data import EnumTempObj

if "_HasLoad" not in dir():
	
	CHANGE_ITEM = 26147 #改名卷轴
	
	#日志
	Change_Names_Msg = AutoLog.AutoTransaction("ChangeName", "更改名字消耗")
	Change_Name_Faile_Msg = AutoLog.AutoTransaction("Change_Name_Faile_Msg", "更改名字失败返还")
	
	#消息
	Change_Name_Suc = AutoMessage.AllotMessage("Change_Name_Suc", "改名成功后同步")
	
def RequestChangeName(role, msg):
	'''
	客户端请求改名
	@param role:
	@param param:
	'''
	newName = msg
	if not newName:
		role.Msg(2, 0, GlobalPrompt.ERROR_NULL_MSG)
		return
	if str(role.GetRoleID()) != role.GetRoleName():#玩家名==玩家ID就免费
		#根据玩家改名次数判断所需道具是否够
		if role.ItemCnt(CHANGE_ITEM) < 1:
			return
	CheckNewName(role, newName)

#==============================================	
def CheckNewName(role, param):
	'''
	检查名字是否已使用，是否屏蔽字
	@param role:
	@param param:
	'''	
	NewName = param
	#名字已存在
	if NewName in RoleMgr.RoleName_Roles:
		role.Msg(2, 0, GlobalPrompt.ERROR_SAME_NAME)
		return
	if '#' in NewName:
		return
	if '*' in NewName:
		return
	if '"' in NewName:
		return
	if '\'' in NewName:
		return
	if '\\' in NewName:
		return
	oldName = role.GetRoleName()
	if oldName == NewName:
		return
	#新名和角色ID一样不让改名
	if str(role.GetRoleID()) == NewName:
		return
	#QQ平台过滤名字
	if Environment.EnvIsQQ():
		login_info = role.GetTempObj(EnumTempObj.LoginInfo)
		openid = login_info["account"]
		openkey = login_info["openkey"]
		pf = login_info["pf"]
		QQHttp.word_filter(openid, openkey, pf, NewName, CheckCallBack, (role, NewName, oldName))
		return
	else:
		TimetoChangeName(role, NewName, oldName)
#==========================================================
def CheckCallBack(response, regparam):
	'''
	qq过滤回调
	@param response:
	@param regparam:
	'''
	role, NewName, oldName = regparam
	if response is None:
		return
	code, body = response
	if code != 200:
		return
	body = eval(body)
	if body["ret"] != 0:
		return
	#判断是否有敏感字
	if body["is_dirty"] != 0:
		#提示
		role.Msg(2, 0, GlobalPrompt.ERROR_WRONG_NAME)
		return	
	#再做次判断
	if NewName in RoleMgr.RoleName_Roles:
		role.Msg(2, 0, GlobalPrompt.ERROR_SAME_NAME)
		return
	TimetoChangeName(role, NewName, oldName)

def TimetoChangeName(role, NewName, oldName):
	'''
	没有屏蔽字，扣除道具，再检查名字表check_name
	@param role:
	@param NewName:
	'''
	if str(role.GetRoleID()) != oldName:#玩家名==玩家ID就免费
		#根据玩家改名次数判断所需道具是否够
		if role.ItemCnt(CHANGE_ITEM) < 1:
			return
		with Change_Names_Msg:			
			role.DelItem(CHANGE_ITEM, 1)
		
	#查询单独表
	DBProxy.DBVisit(cProcess.ProcessID, None, "check_name", (NewName), CheckOldNameReq, (role.GetRoleID(), NewName, oldName))


def CheckOldNameReq(ret, regparam):
	roleId, new_name, oldName = regparam
	if not ret:#失败
		#离线命令
		Call.LocalDBCall(roleId, CheckNameFail, (new_name, oldName))
	else:
		ChangeName(roleId, new_name, oldName)
		

def CheckNameFail(role, param):
	_, oldName = param
	if str(role.GetRoleID()) != oldName:
		with Change_Name_Faile_Msg:
			role.AddItem(CHANGE_ITEM, 1)
		role.Msg(2, 0, GlobalPrompt.ERROR_SAME_NAME)


def ChangeName(roleId, NewName, oldName):
	'''
	更改玩家名字
	@param role:
	@param NewName:
	@param cnt:
	'''	
	DBProxy.DBRoleVisit(roleId, "Change_Name", (roleId, NewName), ChangeNameReq, (roleId, NewName, oldName))

def ChangeNameReq(ret, regparam):
	'''
	改名回调
	@param ret:
	@param regparam:
	'''
	roleId, new_name, old_name = regparam
	if not ret:#更改名字失败
		Call.LocalDBCall(roleId, CheckNameFail, (new_name, old_name))
	else:
		Call.LocalDBCall(roleId, ChangeNameSucceed, (new_name, old_name))

#离线命令
def ChangeNameSucceed(role, param):
	new_name, old_name = param
	IsFree = False
	if str(role.GetRoleID()) == old_name:
		IsFree = True
	role.SetRoleName(new_name)
	RoleMgr.RoleChangeName(role, old_name, new_name)
	#触发事件
	Event.TriggerEvent(Event.Eve_AfterChangeName, role, old_name)
	role.SendObj(Change_Name_Suc, new_name)
	if not IsFree:
		#发世界公告
		cRoleMgr.Msg(1, 0, GlobalPrompt.CHANGE_NAME_SUC_MSG % (old_name, new_name))
	else:
		cRoleMgr.Msg(1, 0, GlobalPrompt.CHANGE_NAME_SUC_MSG2 % (old_name, new_name))
		
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Client_ChangeName_req", "客户端请求改名"), RequestChangeName)
	