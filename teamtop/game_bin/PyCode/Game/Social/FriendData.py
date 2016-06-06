#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Social.FriendData")
#===============================================================================
# 好友数据
#===============================================================================
from Common.Other import EnumSocial
from Common.Message import AutoMessage
from Game.Role.Data import EnumObj

if "_HasLoad" not in dir():
	Social_Init = AutoMessage.AllotMessage("Social_Init", "初始化社交数据(好友字典, 黑名单, 最近联系人, 好友分组字典)")
	Social_SetFriend = AutoMessage.AllotMessage("Social_SetFriend", "设置好友（新增、上线）")
	Social_OutFriend = AutoMessage.AllotMessage("Social_OutFriend", "好友下线")
	Social_DelFriend = AutoMessage.AllotMessage("Social_DelFriend", "删除好友")
	Social_AddBlack = AutoMessage.AllotMessage("Social_AddBlack", "加入黑名单")
	Social_DelBlack = AutoMessage.AllotMessage("Social_DelBlack", "删除黑名单")
	Social_AddRecent = AutoMessage.AllotMessage("Social_AddRecent", "加入最近连续人")

	Social_RequestAddFriend = AutoMessage.AllotMessage("Social_RequestAddFriend", "请求加好友")
	Social_BeFriend = AutoMessage.AllotMessage("Social_BeFriend", "你被加为好友")
	Social_RequestDelFriend = AutoMessage.AllotMessage("Social_RequestDelFriend", "请求删好友")
	Social_RequestAddBack = AutoMessage.AllotMessage("Social_RequestAddBack", "请求加黑名单")
	Social_RequestDelBack = AutoMessage.AllotMessage("Social_RequestDelBack", "请求删黑名单")
	Social_Retry = AutoMessage.AllotMessage("Social_Retry", "尝试重新更新好友信息")
	Social_RequestNear = AutoMessage.AllotMessage("Social_RequestNear", "请求附近玩家信息")
	
	Social_AddGroup = AutoMessage.AllotMessage("Social_AddGroup", "增加一个分组（请求返回是同一个消息）")
	Social_DelGroup = AutoMessage.AllotMessage("Social_DelGroup", "删除一个分组（请求返回是同一个消息）")
	Social_SetGroup = AutoMessage.AllotMessage("Social_SetGroup", "设置一个分组名（请求返回是同一个消息）")
	Social_MoveFriendGroup = AutoMessage.AllotMessage("Social_MoveFriendGroup", "移动一个好友分组（请求返回是同一个消息）")

def GetRoleSimpleInfo(role):
	'''
	获取角色的简单信息字典，这个字典将会缓存在控制模块
	'''
	return {EnumSocial.RoleIDKey: role.GetRoleID(),
			EnumSocial.RoleNameKey: role.GetRoleName(),
			EnumSocial.RoleLevelKey: role.GetLevel(),
			EnumSocial.RoleVIPKey: role.GetVIP(),
			EnumSocial.RoleHZKey: role.GetQQHZ(),
			EnumSocial.RoleLZKey: role.GetQQLZ(),
			EnumSocial.RoleSexKey: role.GetSex(),
			EnumSocial.RoleCareerKey: role.GetCareer(),
			EnumSocial.RoleGradeKey: role.GetGrade(),
			EnumSocial.RoleZDLKey: role.GetZDL(),
			EnumSocial.RoleYHZKey: role.GetQQYHZ(),
			EnumSocial.RoleYLZKey: role.GetQQYLZ(),
			EnumSocial.RoleHHHZKey: role.GetQQHHHZ(),
			EnumSocial.RoleHHLZKey: role.GetQQHHLZ(),
			EnumSocial.RoleZDLKey: role.GetZDL(),
			EnumSocial.FTVIP : role.GetFTVIP()
		}

def GetFriendInfo(role):
	'''
	获取角色的作为他人好友时需提供的信息
	'''
	return {EnumSocial.RoleOnLineKey: True,
			EnumSocial.RoleIDKey: role.GetRoleID(),
			EnumSocial.RoleNameKey: role.GetRoleName(),
			EnumSocial.RoleLevelKey: role.GetLevel(),
			EnumSocial.RoleVIPKey: role.GetVIP(),
			EnumSocial.RoleHZKey: role.GetQQHZ(),
			EnumSocial.RoleLZKey: role.GetQQLZ(),
			EnumSocial.RoleSexKey: role.GetSex(),
			EnumSocial.RoleCareerKey: role.GetCareer(),
			EnumSocial.RoleGradeKey: role.GetGrade(),
			EnumSocial.RoleZDLKey: role.GetZDL(),
			EnumSocial.RoleYHZKey: role.GetQQYHZ(),
			EnumSocial.RoleYLZKey: role.GetQQYLZ(),
			EnumSocial.RoleHHHZKey: role.GetQQHHHZ(),
			EnumSocial.RoleHHLZKey: role.GetQQHHLZ(),
			EnumSocial.RoleZDLKey: role.GetZDL(),
			EnumSocial.FTVIP : role.GetFTVIP()
			}

def GetFriend(role):
	'''
	获取角色的好友字典 好友角色id --> {} 好友相关信息
	@param role:
	'''
	return role.GetObj(EnumObj.Social_Friend)

def GetBlack(role):
	'''
	获取角色黑名单字典 角色id --> 角色名, 时间戳
	'''
	return role.GetObj(EnumObj.Social_Back)

def GetRecent(role):
	'''
	获取好友最长联系人 角色id --> 角色名, 时间戳
	'''
	return role.GetObj(EnumObj.Social_Recent)

def GetGroup(role):
	return role.GetObj(EnumObj.Social_GroupDefine)

def IsFriend(role, role_id):
	'''
	role_id 是否是role的好友
	'''
	return role_id in role.GetObj(EnumObj.Social_Friend)

