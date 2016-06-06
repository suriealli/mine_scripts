#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ClientPanel.PanelTeam")
#===============================================================================
# 组队剧情对白
#===============================================================================
import cRoleMgr
from Common.Message import AutoMessage


#自动回调
CallBackSec = 120

if "_HasLoad" not in dir():
	Msg_FilmDialog_Team_Show = AutoMessage.AllotMessage("Msg_S_FilmDialog_Team_Show", "组队电影式对话(发送ID)")
	Msg_FilmDialog_Team_Show_B = AutoMessage.AllotMessage("Msg_S_FilmDialog_Team_Show_B", "组队电影式对话(需要回调)(发送ID)")
	Msg_FilmDialog_Team_Next = AutoMessage.AllotMessage("Msg_S_FilmDialog_Team_Next", "组队电影式对话下一条")
	
#电影对白
class TeamFilmDialog(object):
	TxtType = 1
	def __init__(self, team, fun = None, regparam = None):
		'''
		对话框基类
		@param role:对话的角色
		@param fun:回调函数
		@param regparam:注册参数
		'''
		self.team = team
		self.fun = fun
		self.regparam = regparam
		#对话列表
		self.dalogList = []
	
	def Append(self, npcType, textID):
		'''
		增加一次对话
		@param npcType: 0:自己半身像  非0:对应NPC半身像
		@param textID:要说的话
		'''
		self.dalogList.append((npcType, textID))
	
	def Show(self):
		#展示对话
		if self.fun:
			#每一个都需要回调，因为队长可能掉线了..注意，队员不能点击快速跳过剧情！
			#低概率触发队员先看完，队长没看完掉线了，触发失败！
			for role in self.team.members:
				role.SendObjAndBack(Msg_FilmDialog_Team_Show_B, (self.TxtType, self.dalogList), CallBackSec, self._OnBack, self.regparam)
		else:
			for role in self.team.members:
				role.SendObj(Msg_FilmDialog_Team_Show, (self.TxtType, self.dalogList))
	
	def _OnBack(self, role, callArgv, regparam):
		'''
		回调
		@param role:回调的角色
		@param callArgv:回调参数，可能自回调，参数为None,但是不影响回调函数，直接调用
		@param regparam:注册参数，和self.regparam一样
		'''
		#客户端回调函数， 包装一层
		try:
			apply(self.fun, (role, regparam))
		except:
			print "GE_EXC, DialogBase (%s)" % str(self.fun)
			raise



def TeamNextFilmTxt(role, msg):
	'''
	队长看完了，请同步播放下一条
	@param role:
	@param msg:
	'''
	team = role.GetTeam()
	if not team:
		return
	if not team.IsTeamLeader(role):
		return
	
	if not team.IsStart():
		return
	
	for member in team.members:
		if member == role:
			continue
		member.SendObj(Msg_FilmDialog_Team_Next, None)



if "_HasLoad" not in dir():
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Msg_TeamNextFilmTxt", "队长看完了，请同步播放下一条"), TeamNextFilmTxt)

