#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Control.RoleMgr")
#===============================================================================
# 角色管理
#===============================================================================
import cComplexServer
from Common.Other import EnumSocial
from Common.Message import PyMessage
from ComplexServer.API import GlobalHttp, Define
from ComplexServer.Plug.Control import ControlProxy
from Control import ProcessMgr

class ControlRole(object):
	def __init__(self, process, role_info, friends):
		self.process = process
		self.role_info = role_info
		self.friends = set(friends)
		self.role_id = role_info[EnumSocial.RoleIDKey]
		# 绑定
		process.control_roles[self.role_id] = self
		ControlRoles[self.role_id] = self
		for friend_role_id in self.friends:
			AddWatch(friend_role_id, self)
	
	def __str__(self):
		return "ControlRole-%s" % (self.role_id)
	
	def GetFriendInfo(self):
		role_info = self.role_info
		return {EnumSocial.RoleOnLineKey: True,
			EnumSocial.RoleIDKey: role_info[EnumSocial.RoleIDKey],
			EnumSocial.RoleNameKey: role_info[EnumSocial.RoleNameKey],
			EnumSocial.RoleLevelKey: role_info[EnumSocial.RoleLevelKey],
			EnumSocial.RoleVIPKey: role_info[EnumSocial.RoleVIPKey],
			EnumSocial.RoleHZKey: role_info[EnumSocial.RoleHZKey],
			EnumSocial.RoleLZKey: role_info[EnumSocial.RoleLZKey],
			EnumSocial.RoleSexKey: role_info[EnumSocial.RoleSexKey],
			EnumSocial.RoleCareerKey: role_info[EnumSocial.RoleCareerKey],
			EnumSocial.RoleGradeKey: role_info[EnumSocial.RoleGradeKey],
			EnumSocial.RoleYHZKey: role_info[EnumSocial.RoleYHZKey],
			EnumSocial.RoleYLZKey: role_info[EnumSocial.RoleYLZKey],
			EnumSocial.RoleHHHZKey: role_info[EnumSocial.RoleHHHZKey],
			EnumSocial.RoleHHLZKey:role_info[EnumSocial.RoleHHLZKey],
			EnumSocial.RoleZDLKey: role_info[EnumSocial.RoleZDLKey]
			}
	
	def Destroy(self):
		# 取消绑定
		del ControlRoles[self.role_id]
		del self.process.control_roles[self.role_id]
		for friend_role_id in self.friends:
			DelWatch(friend_role_id, self)
	
	def AddFriend(self, role_id):
		if role_id in self.friends:
			return
		self.friends.add(role_id)
		AddWatch(role_id, self)
	
	def DelFriend(self, role_id):
		if role_id not in self.friends:
			return
		self.friends.remove(role_id)
		DelWatch(role_id, self)
	
	def SendProcessMsg(self, msgtype, msg):
		ControlProxy.SendLogicMsg(self.process.session_id, msgtype, msg)

def OnRoleLogin(sessionid, msg):
	# 解析消息
	role_info, friends = msg
	role_id = role_info[EnumSocial.RoleIDKey]
	# 查找进程
	control_process = ProcessMgr.ControlProcesssSessions[sessionid]
	# 如果出现状态错乱，修正下
	old_control_role = ControlRoles.get(role_id)
	if old_control_role:
		print "GE_EXC, repeat role(%s) old(%s) new(%s)" % (role_id, old_control_role.process, control_process)
		old_control_role.Destroy()
	# 构建控制进程角色
	control_role = ControlRole(control_process, role_info, friends)
	# 通知上线
	crs = WatchRoles.get(role_id)
	if crs:
		# 获取好友信息
		friend_info = control_role.GetFriendInfo()
		for iter_control_role in crs.itervalues():
			iter_control_role.SendProcessMsg(PyMessage.Control_OnLineFriend, (iter_control_role.role_id, friend_info))
	# 查询好友信息
	my_friend_infos = {}
	http_roleids = []
	for friend_id in friends:
		friend_control_role = ControlRoles.get(friend_id)
		if friend_control_role is None:
			http_roleids.append(friend_id)
			###好友数据
			# 如果是None，说明没查到这个好友的信息，用旧的
			my_friend_infos[friend_id] = None
		else:
			# 如果为字典，则说明能够查询到好友的信息
			my_friend_infos[friend_id] = friend_control_role.GetFriendInfo()
	if http_roleids:
		GlobalHttp.RoleQuery("friend_info", http_roleids, OnRoleQueryBack, (role_id, my_friend_infos))
	else:
		OnRoleQueryBack(None, (role_id, my_friend_infos))

def OnRoleQueryBack(response, regparam):
	role_id, my_friend_infos = regparam
	control_role = ControlRoles.get(role_id)
	# 等查询回来已经断线了
	if control_role is None:
		return
	# 融合http查询回来的数据
	if response:
		code, body = response
		if code == 200 and body != Define.Error:
			###好友数据
			# 注意，这里用查询出来的好友信息来更新旧的好友信息，可能有False表示该角色不存在或者已经流失
			my_friend_infos.update(eval(body))
	control_role.SendProcessMsg(PyMessage.Control_InitFriends, (role_id, my_friend_infos))

def OnRoleExit(sessionid, msg):
	control_role = ControlRoles.get(msg)
	if not control_role:
		return
	# 通知下线
	crs = WatchRoles.get(msg)
	if crs:
		for iter_control_role in crs.itervalues():
			iter_control_role.SendProcessMsg(PyMessage.Control_OutLineFriend, (iter_control_role.role_id, msg))
	# 删除角色
	control_role.Destroy()

def OnAddFriend(sessionid, msg):
	role_id, friend_role_id = msg
	control_role = ControlRoles.get(role_id)
	if not control_role:
		return
	control_role.AddFriend(friend_role_id)

def OnDelFriend(sessionid, msg):
	role_id, friend_role_id = msg
	control_role = ControlRoles[role_id]
	control_role.DelFriend(friend_role_id)

def AddWatch(role_id, control_role):
	watch_role = WatchRoles.get(role_id)
	if watch_role is None:
		WatchRoles[role_id] = watch_role = {}
	watch_role[control_role.role_id] = control_role

def DelWatch(role_id, control_role):
	watch_role = WatchRoles[role_id]
	del watch_role[control_role.role_id]
	if not watch_role:
		del WatchRoles[role_id]

def OnRoleCall(sessionid, msg):
	roleid = msg[0]
	control_role = ControlRoles.get(roleid)
	if not control_role: return
	control_role.SendProcessMsg(PyMessage.Control_OnRoleCall, msg)

if "_HasLoad" not in dir():
	ControlRoles = {}
	WatchRoles = {}
	cComplexServer.RegDistribute(PyMessage.Control_RoleLogin, OnRoleLogin)
	cComplexServer.RegDistribute(PyMessage.Control_RoleExit, OnRoleExit)
	cComplexServer.RegDistribute(PyMessage.Control_AddFriend, OnAddFriend)
	cComplexServer.RegDistribute(PyMessage.Control_DelFriend, OnDelFriend)
	cComplexServer.RegDistribute(PyMessage.Control_RoleCall, OnRoleCall)

