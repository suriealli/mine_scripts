#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FaceBook.FaceBookLikeMgr")
#===============================================================================
# FaceBook Like管理
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import GlobalPrompt
from Game.Role.Data import EnumInt1, EnumInt16

if "_HasLoad" not in dir():
	FACE_BOOK_LIKE_REWARD_MONEY = 3000

	FaceBookDraw = AutoLog.AutoTransaction("FaceBookDraw", "FaceBook领取抽奖次数")
	
def FaceBookLikeReward(role):
	if role.GetI1(EnumInt1.FaceBookLike):
		return
	
	role.SetI1(EnumInt1.FaceBookLike, 1)
	
	role.IncMoney(FACE_BOOK_LIKE_REWARD_MONEY)
	
	#提示
	role.Msg(2, 0, GlobalPrompt.FACEBOOK_LIKE_PROMPT)
	role.Msg(2, 0, GlobalPrompt.Money_Tips % FACE_BOOK_LIKE_REWARD_MONEY)
	
#===============================================================================
# 客户端请求
#===============================================================================
def RequestFaceBookLikeReward(role, msg):
	FaceBookLikeReward(role)

def RequestFaceBookLikeDrawTimes(role, param):
	'''
	客户端请求领取facebooklike抽奖次数
	@param role:
	@param param:
	'''
	if role.GetI1(EnumInt1.FaceBookDrawState):
		return
	with FaceBookDraw:
		role.SetI1(EnumInt1.FaceBookDrawState, 1)
		role.IncI16(EnumInt16.InviteReward, 1)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveInviteFriend, 1)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FaceBook_Like_Get_Reward", "客户端请求领取facebooklike奖励"), RequestFaceBookLikeReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FaceBook_Like_Get_DrawTimes", "客户端请求领取facebooklike抽奖次数"), RequestFaceBookLikeDrawTimes)
	