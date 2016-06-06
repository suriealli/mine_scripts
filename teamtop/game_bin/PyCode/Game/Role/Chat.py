#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Chat")
#===============================================================================
# 聊天模块
#===============================================================================
import cDateTime
import cRoleMgr
import cNetMessage
import Environment
import cProcess
from Common import CValue
from Common.Other import EnumSocial, EnumKick
from ComplexServer.Log import AutoLog
from World import Define
from Game.Team import TeamBase
from Game.Social import FriendData, FriendOperate
from Game.Role import Event, Call
from Game.Role.Data import EnumInt32, EnumDisperseInt32, EnumDayInt8, EnumTempInt64, EnumTempObj, EnumCD

# 这里的值是按照EnumInt32中的下标来的
ChatCDEnum = [None] * 130
ChatCDEnum[EnumInt32.WorldChatCD] = 3
ChatCDEnum[EnumInt32.UnionChatCD] = 1
ChatCDEnum[EnumInt32.TeamChatCD] = 1
ChatCDEnum[EnumInt32.ChuanYinChatCD] = 0
ChatCDEnum[EnumInt32.SceneChatCD] = 3
ChatCDEnum[EnumInt32.KuafuZhanchangChatCD] = 3

# 传音符 喇叭 物品coding (vip3 或者等级大于等于36)
ChuanYinFu = 25832

#===============================================================================
# 发广告检测条件
# 1 角色等级小于CheckLevel
#   a 在线超过CheckOnlineTime秒没升级并且(今日发送聊天超过CheckDayCnt次或者本次登录发送聊天超过CheckLoginCnt次)
#     发送一次非私聊算一次，私聊一个新角色算一次
#   b 本次登录私聊人数超过CheckRoleChatCnt
#===============================================================================
CheckLevel = 36
CheckOnlineTime = 120
CheckDayCnt = 50 #最大200
CheckLoginCnt = 20
CheckRoleChatCnt = 30
ReleaseLevel = 40
ReleaseTimes = CValue.MAX_INT32 - 7

T_Chat_Error = "请正确发言！"


def OnRoleChat(role, i64, tsize):
	# 整个消息的长度
	if Environment.EnvIsQQ():
		if tsize >= 200:
			role.Kick(True, EnumKick.ChatError)
			return
	else:
		if tsize >= 400:
			role.Kick(True, EnumKick.ChatError)
			return
	# 检测广告
	if not Environment.EnvIsFT():
		if Environment.IsQQ and role.GetLevel() < CheckLevel and role.GetVIP() < 3 \
		and role.GetDI32(EnumDisperseInt32.enOnlineTimes) - role.GetI32(EnumInt32.LastLeaveUpTotalOnlineTimes) > CheckOnlineTime \
		and (role.GetDI8(EnumDayInt8.ChatCnt) > CheckDayCnt or role.GetTI64(EnumTempInt64.ChatCnt) > CheckLoginCnt):
			role.SetCanChatTime(ReleaseTimes)
	# 如果参数大于2**32，则认为是角色之间点对点聊天
	if i64 > CValue.P2_32:
		RoleChat(role, i64)
	# 否则认为是喊话
	else:
		BroadChat(role, i64)

def RoleChat(role, to_role_id):
	if role.GetRoleID() == to_role_id:
		return
	# 黑名单中忽视之
	if to_role_id in FriendData.GetBlack(role):
		return
	# 记录聊天的角色数
	if not Environment.EnvIsFT():
		if role.GetLevel() < CheckLevel:
			role_id_set = role.GetTempObj(EnumTempObj.CharRoleIDSet)
			if role_id_set is None:
				role_id_set = set()
				role.SetTempObj(EnumTempObj.CharRoleIDSet, role_id_set)
			if to_role_id not in role_id_set:
				role_id_set.add(to_role_id)
				if len(role_id_set) > CheckRoleChatCnt:
					role.SetCanChatTime(ReleaseTimes)
				# 增加一次聊天计数
				if role.GetDI8(EnumDayInt8.ChatCnt) < 126:
					role.IncDI8(EnumDayInt8.ChatCnt, 1)
				role.IncTI64(EnumTempInt64.ChatCnt, 1)
	# 如果在本进程能够找到这个角色，则转发消息之
	to_role = cRoleMgr.FindRoleByRoleID(to_role_id)
	if to_role:
		# 在对方黑名单中，忽视之
		if role.GetRoleID() in FriendData.GetBlack(to_role):
			return
		to_role.BroadMsg()
		FriendOperate.Recent([role, to_role])
		return
	# 否则有可能是跨服聊天，必须要是在线好友才可以
	friends = FriendData.GetFriend(role)
	# 好友数据未初始化，忽视之
	if not friends:
		return
	# 没有这个好友，忽视之
	friend_info = friends.get(to_role_id)
	if friend_info is None:
		return
	# 该玩家不在线
	if not friend_info.get(EnumSocial.RoleOnLineKey):
		return
	# 发送私聊
	chat_info = cNetMessage.MsgToString()
	Call.ControlCall(to_role_id, OnCrossRoleChat, chat_info)
	

def OnCrossRoleChat(role, param):
	cNetMessage.StringToMsg(param)
	role.BroadMsg()

def BroadChat(role, param):
	# CD
	if param >= len(ChatCDEnum):
		role.Kick(True, EnumKick.ChatError)
		return
	cd = ChatCDEnum[param]
	if cd is None:
		role.Kick(True, EnumKick.ChatError)
		return
	if cd > 0:
		now = cDateTime.Seconds()
		if now <= role.GetI32(param):
			role.WPE()
			return
		role.SetI32(param, now + cd)
	# 增加一次聊天计数
	if role.GetLevel() < CheckLevel:
		if role.GetDI8(EnumDayInt8.ChatCnt) < 126:
			role.IncDI8(EnumDayInt8.ChatCnt, 1)
		role.IncTI64(EnumTempInt64.ChatCnt, 1)
	# 转发
	if param == EnumInt32.WorldChatCD:
		if Environment.IsCross:
			#跨服环境下不能世界聊天(除特殊几个跨服外)
			if cProcess.ProcessID != Define.GetCrossID_2():
				return
			else:
				if role.GetCD(EnumCD.CrossWorldChatCD):
					return
				else:
					role.SetCD(EnumCD.CrossWorldChatCD, 60)
		cRoleMgr.BroadMsg()
	elif param == EnumInt32.UnionChatCD:
		if Environment.IsCross:
			#跨服环境下不能公会聊天
			return
		UnionChat(role)
	elif param == EnumInt32.TeamChatCD:
		TeamChat(role)
	elif param == EnumInt32.ChuanYinChatCD:
		# 扣传音符
		if Environment.EnvIsQQ() or Environment.EnvIsFT():
			if role.GetVIP() < 3 and role.GetLevel() < 36:
				return
		if role.ItemCnt(ChuanYinFu) > 0:
			# 注意这里要先广播消息在扣物品，因为聊天消息缓存
			cRoleMgr.BroadMsg()
			with TraChat:
				role.DelItem(ChuanYinFu, 1)
	elif param == EnumInt32.SceneChatCD:
		#区域聊天
		scene = role.GetScene()
		scene.BroadMsg()
	elif param == EnumInt32.KuafuZhanchangChatCD:
		#跨服战场阵营聊天
		KuafuZhanchangChat(role)
	else:
		role.Kick(True, EnumKick.ChatError)
		return

def UnionChat(role):
	union_obj = role.GetUnionObj()
	if union_obj is None:
		return
	
	for role_id in union_obj.members.iterkeys():
		role = cRoleMgr.FindRoleByRoleID(role_id)
		if not role:
			continue
		role.BroadMsg()

def TeamChat(role):
	jtobj = role.GetTempObj(EnumTempObj.CrossJTeamObj)
	if jtobj:
		JTeamChat(jtobj)
		return
	team = TeamBase.GetTeamByRoleID(role.GetRoleID())
	if not team:
		role.WPE()
		return
	for role in team.members:
		role.BroadMsg()

def JTeamChat(jtobj):
	#跨服组队竞技假的队伍聊天
	for role in jtobj.members:
		role.BroadMsg()

def KuafuZhanchangChat(role):
	sceneId = role.GetSceneID()
	roleId = role.GetRoleID()
	
	from Game.Activity.KuafuZhanchang import KuafuZhanchangMgr
	kfzc = KuafuZhanchangMgr.KFZC_SCENE_KFZC.get(sceneId)
	if not kfzc:
		return
	campId = KuafuZhanchangMgr.KFZC_ROLE_CAMP.get(roleId)
	if not campId:
		return
	
	campRoles = kfzc.left_roles if campId == 1 else kfzc.right_roles
	for role in campRoles:
		if not role or role.IsKick():
			continue
		role.BroadMsg()
	
def OnRoleLevelUp(role, regparam):
	# 标记角色升级时间
	role.SetI32(EnumInt32.LastLeaveUpTotalOnlineTimes, role.GetDI32(EnumDisperseInt32.enOnlineTimes))
	# 重置计数
	role_id_set = role.GetTempObj(EnumTempObj.CharRoleIDSet)
	if role_id_set is None:
		cnt = 0
	else:
		cnt = len(role_id_set)
	role.SetDI8(EnumDayInt8.ChatCnt, cnt)
	role.SetTI64(EnumTempInt64.ChatCnt, cnt)
	# 自动解禁
	if role.GetLevel() > ReleaseLevel and role.GetDI32(EnumDisperseInt32.CanChatTime) == ReleaseTimes:
		role.SetCanChatTime(0)


if "_HasLoad" not in dir():
	#这里特殊处理下能跨服世界聊天的跨服id
	
	Event.RegEvent(Event.Eve_AfterLevelUp, OnRoleLevelUp)
	TraChat = AutoLog.AutoTransaction("TraChat", "世界聊天，喇叭")
	
