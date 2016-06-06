#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Union.UnionTalk")
#===============================================================================
# 公会聊天
#===============================================================================
import Environment
import cRoleMgr
from Common.Message import AutoMessage
from Game.Union import UnionDefine

if "_HasLoad" not in dir():
	Union_Show_Talk_Panel = AutoMessage.AllotMessage("Union_Show_Talk_Panel", "通知客户端显示公会聊天面板")

#===============================================================================
#客户端消息
def RequestUnionOpenTalkPanel(role, msg):
	'''
	客户端请求打开公会聊天面板
	@param role:
	@param msg:
	'''
	unionObj = role.GetUnionObj()
	if not unionObj: 
		return
	
	memberList = []
	for k, v in unionObj.members.iteritems():
		if v[UnionDefine.M_ONLINE_IDX]:
			memberRole = cRoleMgr.FindRoleByRoleID(k)
			if memberRole:
				memberList.append((k, v[UnionDefine.M_NAME_IDX], v[UnionDefine.M_ONLINE_IDX], memberRole.GetVIP(), memberRole.GetSex(), 
								memberRole.GetCareer(), memberRole.GetGrade(), memberRole.GetLevel()))
		else:
			memberList.append((k, v[UnionDefine.M_NAME_IDX], 0, 0, 0, 0, 0))
	
	role.SendObj(Union_Show_Talk_Panel, (unionObj.notice, memberList))

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Union_Open_Talk_Panel", "客户端请求打开公会聊天面板"), RequestUnionOpenTalkPanel)
	
	
	