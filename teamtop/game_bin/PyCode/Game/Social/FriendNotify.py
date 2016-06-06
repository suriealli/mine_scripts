#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Social.FriendNotify")
#===============================================================================
# 好友通知
#===============================================================================
import cRoleMgr
import cDateTime
import cComplexServer
from Common.Other import EnumSocial
from Common.Message import PyMessage
from ComplexServer.Plug.Control import ControlProxy
from Game.Role import Event
from Game.Social import FriendData

ONE_WEEK_SECOND = 7 * 24 * 3600

def OnRoleLogin(role, param):
	friends = FriendData.GetFriend(role)
	#backs = FriendData.GetBlack(role)
	recents = FriendData.GetRecent(role)
	#groups = FriendData.GetGroup(role)
	# 清理最近联系人
	over_time = cDateTime.Seconds() - ONE_WEEK_SECOND
	# 这里要删除，故不能使用迭代器遍历
	for role_id, black_info in recents.items():
		if black_info[1] < over_time:
			del recents[role_id]
	# 初始化好友在线情况
	for friend_info in friends.itervalues():
		friend_info[EnumSocial.RoleOnLineKey] = False
	
	# 通知控制进程“我”上线了，和查询“我”的好友集合
	ControlProxy.SendControlMsg(PyMessage.Control_RoleLogin, (FriendData.GetRoleSimpleInfo(role), friends.keys()))

def OnSyncRoleOtherData(role, msg):
	friends = FriendData.GetFriend(role)
	backs = FriendData.GetBlack(role)
	recents = FriendData.GetRecent(role)
	groups = FriendData.GetGroup(role)
	# 同步客户端
	role.SendObj(FriendData.Social_Init, (friends, backs, recents, groups))

def OnRoleExit(role, param):
	ControlProxy.SendControlMsg(PyMessage.Control_RoleExit, role.GetRoleID())

def AddFriend(role, friend_id):
	ControlProxy.SendControlMsg(PyMessage.Control_AddFriend, (role.GetRoleID(), friend_id))

def DelFriend(role, friend_id):
	ControlProxy.SendControlMsg(PyMessage.Control_DelFriend, (role.GetRoleID(), friend_id))

def OnInitFriends(sessionid, msg):
	role_id, my_friend_infos = msg
	role = cRoleMgr.FindRoleByRoleID(role_id)
	if not role:
		return
	# 清理好友数据
	friends = FriendData.GetFriend(role)
	for friend_id, friend_info in my_friend_infos.items():
		###好友数据
		# None说明没有查询到该角色的数据，用旧的
		if friend_info is None:
			pass
		# False说明该角色已经流失，要删除之
		elif friend_info is False:
			if friend_id in friends:
				del friends[friend_id]
				role.SendObj(FriendData.Social_DelFriend, friend_id)
		# 否则肯定是好友角色数据的字典，更新之
		else:
			# 这里要用update来更新（因为有个特殊的分组标记）
			old_friend_info = friends.get(friend_id)
			if old_friend_info is not None:
				old_friend_info.update(friend_info)
				role.SendObj(FriendData.Social_SetFriend, old_friend_info)

def OnLineFriend(sessionid, msg):
	role_id, friend_info = msg
	role = cRoleMgr.FindRoleByRoleID(role_id)
	if not role:
		return
	friend_id = friend_info[EnumSocial.RoleIDKey]
	friends = FriendData.GetFriend(role)
	old_friend_info = friends.get(friend_id)
	if old_friend_info is None:
		return
	# 设置角色在线情况(这里要用update来更新,因为有个特殊的分组标记)
	old_friend_info.update(friend_info)
	# 通知客户端
	role.SendObj(FriendData.Social_SetFriend, old_friend_info)

def OutLineFriend(sessionid, msg):
	role_id, friend_id = msg
	role = cRoleMgr.FindRoleByRoleID(role_id)
	if not role:
		return
	friends = FriendData.GetFriend(role)
	friend_info = friends.get(friend_id)
	if not friend_info:
		return
	# 修正角色在线情况
	friend_info[EnumSocial.RoleOnLineKey] = False
	friends[friend_id] = friend_info
	# 通知客户端
	role.SendObj(FriendData.Social_OutFriend, friend_id)


if "_HasLoad" not in dir():
	Event.RegEvent(Event.Eve_AfterLogin, OnRoleLogin)
	Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
	
	Event.RegEvent(Event.Eve_BeforeExit, OnRoleExit)
	cComplexServer.RegDistribute(PyMessage.Control_InitFriends, OnInitFriends)
	cComplexServer.RegDistribute(PyMessage.Control_OnLineFriend, OnLineFriend)
	cComplexServer.RegDistribute(PyMessage.Control_OutLineFriend, OutLineFriend)

