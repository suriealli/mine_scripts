#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Social.FriendOperate")
#===============================================================================
# 好友操作
#===============================================================================
import random
import itertools
import cDateTime
import cRoleMgr
import Environment
from Common.Other import EnumSocial
from ComplexServer.API import QQHttp
from Game.Role import RoleMgr
from Game.Role.Data import EnumCD, EnumTempObj
from Game.Social import FriendData, FriendNotify

T_NO_NAME = "该玩家不存在或者不在线，请查证后再加好友！"
T_NO_FRIEND_DATA = "你的好友数据尚未初始化，请稍候！"
T_FULL = "你的好友已经满了！"
T_HAS = "该玩家已经是你的好友了！"
T_BLACK = "该玩家已经被你屏蔽无法添加！"
T_OUT_LINE = "玩家已离线,无法添加！"
T_HTTP_ERROR = "系统错误，请稍候再试试！"
T_GROUP_MGZ = "分组名不合法!"
T_GROUP_TOO_MUCH = "分组太多！"

def RequestAddFriend(role, msg):
	# 如果是整数，按照角色id加好友，否则按照角色名加好友
	if isinstance(msg, (int, long)):
		AddFriendByRoleId(role, msg)
	else:
		to_roles = RoleMgr.RoleName_Roles.get(msg)
		if to_roles is None:
			role.Msg(2, 0, T_NO_NAME)
			return
		for to_role in to_roles:
			AddFriendByRoleId(role, to_role.GetRoleID())

def AddFriendByRoleId(role, role_id):
	# 加自己？
	if role_id == role.GetRoleID():
		return
	friends = FriendData.GetFriend(role)
	# 已经是好友
	if role_id in friends:
		role.Msg(2, 0, T_HAS)
		return
	# 好友满了
	if len(friends) >= EnumSocial.MaxFriends:
		role.Msg(2, 0, T_FULL)
		return
	blacks = FriendData.GetBlack(role)
	# 在黑名单中
	if role_id in blacks:
		role.Msg(2, 0, T_BLACK)
		return
	# 对方不在线
	to_role = RoleMgr.RoleID_Role.get(role_id)
	if not to_role:
		role.Msg(2, 0, T_OUT_LINE)
		return
	# 加好友
	friend_info = FriendData.GetFriendInfo(to_role)
	friends[role_id] = friend_info
	#这里做个通知神树的处理
	# 通知控制模块
	FriendNotify.AddFriend(role, role_id)
	# 通知客户端
	role.SendObj(FriendData.Social_SetFriend, friend_info)
	# 提示对方加我为好友
	to_friends = FriendData.GetFriend(to_role)
	if len(to_friends) >= EnumSocial.MaxFriends:
		return
	me_id = role.GetRoleID()
	if me_id in to_friends:
		return
	to_black = FriendData.GetBlack(to_role)
	if me_id in to_black:
		return
	# 通知被加为好友
	to_role.SendObj(FriendData.Social_BeFriend, (role.GetRoleID(), role.GetRoleName()))

def RequestDelFriend(role, msg):
	friends = FriendData.GetFriend(role)
	if msg not in friends:
		return
	del friends[msg]
	# 通知控制模块
	FriendNotify.DelFriend(role, msg)
	# 通知客户端
	role.SendObj(FriendData.Social_DelFriend, msg)

def RequestAddBlack(role, msg):
	if role.GetRoleID() == msg:
		return
	blacks = FriendData.GetBlack(role)
	# 已经在屏蔽字典中了
	if msg in blacks:
		return
	# 满了
	if len(blacks) >= EnumSocial.MaxBlack:
		return
	# 查找目标角色的id和角色名
	to_role_id = None
	to_role_name = None
	
	# 首先要尝试删除最近联系人和好友
	recent = FriendData.GetRecent(role)
	recent_info = recent.pop(msg, None)
	if recent_info:
		to_role_id = msg
		to_role_name = recent_info[0]
	friends = FriendData.GetFriend(role)
	friend_info = friends.pop(msg, None)
	if friend_info:
		to_role_id = friend_info[EnumSocial.RoleIDKey]
		to_role_name = friend_info[EnumSocial.RoleNameKey]
		# 告诉客户端，删除好友
		role.SendObj(FriendData.Social_DelFriend, msg)
	# 如果在线的话，用在线的信息
	to_role = RoleMgr.RoleID_Role.get(msg)
	if to_role:
		to_role_id = to_role.GetRoleID()
		to_role_name = to_role.GetRoleName()
	# 如果找不到目标角色信息，则返回之
	if to_role_id is None:
		return
	# 加黑名单
	now = cDateTime.Seconds()
	blacks[to_role_id] = to_role_name, now
	# 通知客户端
	role.SendObj(FriendData.Social_AddBlack, (to_role_id, to_role_name, now))

def RequestDelBlack(role, msg):
	blacks = FriendData.GetBlack(role)
	if msg not in blacks:
		return
	# 删除黑名单
	del blacks[msg]
	# 通知客户端
	role.SendObj(FriendData.Social_DelBlack, msg)

def Recent(rolelist):
	now = cDateTime.Seconds()
	for role1, role2 in itertools.combinations(rolelist, 2):
		role1_id = role1.GetRoleID()
		role1_name = role1.GetRoleName()
		recents1 = FriendData.GetRecent(role1)
		blacks1 = FriendData.GetBlack(role1)
		
		role2_id = role2.GetRoleID()
		role2_name = role2.GetRoleName()
		recents2 = FriendData.GetRecent(role2)
		blacks2 = FriendData.GetBlack(role2)
		# 加入最近连续人并且通知
		if len(recents2) < EnumSocial.MaxRecent and role1_id not in recents2 and role1_id not in blacks2:
			recents2[role1_id] = role1_name, now
			role2.SendObj(FriendData.Social_AddRecent, (role1_id, role1_name, now))
		if len(recents1) < EnumSocial.MaxRecent and role2_id not in recents1 and role2_id not in blacks1:
			recents1[role2_id] = role2_name, now
			role1.SendObj(FriendData.Social_AddRecent, (role2_id, role2_name, now))

def RequestRetry(role, msg):
	return
	if role.GetCD(EnumCD.Social_Retry):
		return
	role.SetCD(EnumCD.Social_Retry, 600)
	FriendNotify.OnRoleLogin(role, None)

def RequestNear(role, msg):
	# 下面的操作挺耗的，加CD
	if role.GetCD(EnumCD.Social_Near_CD):
		pass
	role.SetCD(EnumCD.Social_Near_CD, 5)
	backfunid, _ = msg
	scene = role.GetScene()
	near_roles = []
	me_id = role.GetRoleID()
	if hasattr(scene, "GetAllRole"):
		roles = scene.GetAllRole()
		random.shuffle(roles)
		for other in roles:
			if other.GetRoleID() == me_id:
				continue
			# 如果是好友，或者是黑名单不能推荐
			if FriendData.IsFriend(role, other.GetRoleID()) or other.GetRoleID() in FriendData.GetBlack(role):
				continue
			near_roles.append((other.GetRoleID(), other.GetRoleName(), other.GetLevel(), other.GetCareer()))
			if len(near_roles) >= 12:
				break
	role.CallBackFunction(backfunid, near_roles)

def RequestAddGroup(role, msg):
	if not isinstance(msg, str):
		return
	if len(msg) >= 20:
		return
	if len(FriendData.GetGroup(role)) >= 3:
		return
	if Environment.EnvIsQQ():
		login_info = role.GetTempObj(EnumTempObj.LoginInfo)
		openid = login_info["account"]
		openkey = login_info["openkey"]
		pf = login_info["pf"]
		QQHttp.word_filter(openid, openkey, pf, msg, OnAddGroupCheckReturn, (role, msg))
	else:
		OnAddGroupCheckReturn((200, repr({"ret":0, "is_dirty":0})), (role, msg))

def OnAddGroupCheckReturn(response, regparam):
	role, group_name = regparam
	if response is None:
		role.Msg(2, 0, T_HTTP_ERROR)
		return
	code, body = response
	if code != 200:
		role.Msg(2, 0, T_HTTP_ERROR)
		return
	body = eval(body)
	if body["ret"] != 0:
		role.Msg(2, 0, T_HTTP_ERROR)
		return
	if body["is_dirty"] != 0:
		role.Msg(2, 0, T_GROUP_MGZ)
		return
	AddGroup(role, group_name)

def RequestSetGroup(role, msg):
	group_id, group_name = msg
	if not isinstance(group_name, str):
		return
	if len(group_name) >= 20:
		return
	if group_id not in FriendData.GetGroup(role):
		return
	if Environment.EnvIsQQ():
		login_info = role.GetTempObj(EnumTempObj.LoginInfo)
		openid = login_info["account"]
		openkey = login_info["openkey"]
		pf = login_info["pf"]
		QQHttp.word_filter(openid, openkey, pf, group_name, OnSetGroupCheckReturn, (role, group_id, group_name))
	else:
		OnSetGroupCheckReturn((200, repr({"ret":0, "is_dirty":0})), (role, group_id, group_name))

def OnSetGroupCheckReturn(response, regparam):
	role, group_id, group_name = regparam
	if response is None:
		role.Msg(2, 0, T_HTTP_ERROR)
		return
	code, body = response
	if code != 200:
		role.Msg(2, 0, T_HTTP_ERROR)
		return
	body = eval(body)
	if body["ret"] != 0:
		role.Msg(2, 0, T_HTTP_ERROR)
		return
	if body["is_dirty"] != 0:
		role.Msg(2, 0, T_GROUP_MGZ)
		return
	SetGroup(role, group_id, group_name)

def AddGroup(role, group_name):
	if len(group_name) >= 20:
		return
	groups = FriendData.GetGroup(role)
	if len(groups) >= 3:
		role.Msg(2, 0, T_GROUP_TOO_MUCH)
		return
	if groups:
		new_id = max(groups.iterkeys()) + 1
	else:
		new_id = 10
	groups[new_id] = group_name
	role.SendObj(FriendData.Social_AddGroup, (new_id, group_name))

def DelGroup(role, group_id):
	groups = FriendData.GetGroup(role)
	if group_id not in groups:
		return
	# 将该分组的好友全部T掉
	friends = FriendData.GetFriend(role)
	for friend_id, friend_info in friends.iteritems():
		if friend_info.get(EnumSocial.RoleGroupIDKey) != group_id:
			continue
		friend_info[EnumSocial.RoleGroupIDKey] = 0
		role.SendObj(FriendData.Social_MoveFriendGroup, (friend_id, 0))
	# 删除该分组
	del groups[group_id]
	role.SendObj(FriendData.Social_DelGroup, group_id)

def SetGroup(role, group_id, group_name):
	groups = FriendData.GetGroup(role)
	if group_id not in groups:
		return
	groups[group_id] = group_name
	# 设置分组名
	role.SendObj(FriendData.Social_SetGroup, (group_id, group_name))

def MoveFriendGroup(role, msg):
	friend_id, group_id = msg
	friends = FriendData.GetFriend(role)
	friend_info = friends.get(friend_id)
	if friend_info is None:
		return
	if group_id == 0:
		friend_info[EnumSocial.RoleGroupIDKey] = group_id
		role.SendObj(FriendData.Social_MoveFriendGroup, (friend_id, group_id))
	else:
		if group_id in FriendData.GetGroup(role):
			friend_info[EnumSocial.RoleGroupIDKey] = group_id
			role.SendObj(FriendData.Social_MoveFriendGroup, (friend_id, group_id))

if "_HasLoad" not in dir():
	cRoleMgr.RegDistribute(FriendData.Social_RequestAddFriend, RequestAddFriend)
	cRoleMgr.RegDistribute(FriendData.Social_RequestDelFriend, RequestDelFriend)
	cRoleMgr.RegDistribute(FriendData.Social_RequestAddBack, RequestAddBlack)
	cRoleMgr.RegDistribute(FriendData.Social_RequestDelBack, RequestDelBlack)
	cRoleMgr.RegDistribute(FriendData.Social_Retry, RequestRetry)
	cRoleMgr.RegDistribute(FriendData.Social_RequestNear, RequestNear)
	cRoleMgr.RegDistribute(FriendData.Social_AddGroup, RequestAddGroup)
	cRoleMgr.RegDistribute(FriendData.Social_DelGroup, DelGroup)
	cRoleMgr.RegDistribute(FriendData.Social_SetGroup, RequestSetGroup)
	cRoleMgr.RegDistribute(FriendData.Social_MoveFriendGroup, MoveFriendGroup)

