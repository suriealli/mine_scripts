#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.GVE.GVEMirror")
#===============================================================================
# GVE多人副本
#===============================================================================
import cSceneMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumFightStatistics, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Dragon import DragonConfig
from Game.Fight import FightEx
from Game.GVE import GVEMirrorNPC, GVEConfig
from Game.Role import Status
from Game.Role.Data import EnumInt1, EnumTempObj, EnumDayInt8
from Game.Scene import MutilMirrorBase, SceneMgr, MirrorIdAllot

if "_HasLoad" not in dir():
	#消息
	GVE_Show_Fight_Round = AutoMessage.AllotMessage("GVE_Show_Fight_Round", "通知客户端显示GVE副本战斗回合数")
	GVE_Show_Finish_Data = AutoMessage.AllotMessage("GVE_Show_Finish_Data", "通知客户端显示GVE通关数据")
	
	#日志
	TraGVEFightReward = AutoLog.AutoTransaction("TraGVEFightReward", "GVE副本战斗奖励")
	TraGVECardReward = AutoLog.AutoTransaction("TraGVECardReward", "GVE副本翻牌奖励")

class GVEMirror(MutilMirrorBase.MutilMirrorBase):
	def __init__(self, team, fbConfig):
		MutilMirrorBase.MutilMirrorBase.__init__(self)
		
		self.team = team
		self.fbConfig = fbConfig		#GVE副本配置
		self.fightRound = 0				#战斗回合数
		self.fightIndex = 0				#战斗序号(打到第几个怪)
		self.star = 1					#星星数量
		self.roleCardRewardItem = {}	#记录角色翻牌奖励物品
		self.roleWhoCanGetReward = []	#记录角色是否可以领取翻牌奖励(是否消耗了副本次数)
		self.isFisish = False			#GVE副本是否完成
		
		#获取场景配置
		sceneConfig = SceneMgr.SceneConfig_Dict.get(fbConfig.sceneId)
		if not sceneConfig:
			return
		
		#分配全局副本ID
		self.mirrorGId = MirrorIdAllot.AllotMirrorID()
		
		#尝试创建副本场景
		self.mirrorScene = cSceneMgr.CreateMultiMirrorScene(self.mirrorGId, sceneConfig.SceneId, sceneConfig.SceneName, sceneConfig.MapId, self.BeforeLeave)
		if not self.mirrorScene:
			return
		
		#尝试进入场景
		for member in team.members:
			if not self.mirrorScene.JoinRole(member, fbConfig.posX, fbConfig.posY):
				print "GE_EXC, GVEMirror JoinRole Fail, roleId(%s)", member.GetRoleID()
				return
		
		#强制进入状态
		Status.ForceInStatus_Roles(team.members, EnumInt1.ST_InTeamMirror)
		
		#进入副本场景后调用
		self.AfterJoinRoles(team.members)
		
	def AfterJoinRoles(self, roles):
		MutilMirrorBase.MutilMirrorBase.AfterJoinRoles(self, roles)
		
		for role in roles:
			#同步副本回合数
			role.SendObj(GVE_Show_Fight_Round, self.fightRound)
			
			#是否勾选了不消耗GVE副本次数
			if role.GetI1(EnumInt1.GVEFBNotCost):
				continue
			#扣除收益次数
			if role.GetDI8(EnumDayInt8.GVEFBCnt) >= EnumGameConfig.GVE_DAY_CNT_MAX + role.GetDI8(EnumDayInt8.GVEFBBuyCnt):
				continue
			role.IncDI8(EnumDayInt8.GVEFBCnt, 1)
			#记录
			self.roleWhoCanGetReward.append(role.GetRoleID())
			#版本判断
			if Environment.EnvIsNA():
				#北美万圣节活动
				HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
				HalloweenNAMgr.finish_gve_fb()
			elif Environment.EnvIsRU():
				#七日活动
				sevenActMgr = role.GetTempObj(EnumTempObj.SevenActMgr)
				sevenActMgr.finish_gve_fb()
				
		#创建副本NPC
		npc1 = GVEMirrorNPC.GVEMirrorNPC(self, 1, self.fbConfig.mc1, self.AfterClickNPC)
		npc2 = GVEMirrorNPC.GVEMirrorNPC(self, 2, self.fbConfig.mc2, self.AfterClickNPC)
		npc3 = GVEMirrorNPC.GVEMirrorNPC(self, 3, self.fbConfig.mc3, self.AfterClickNPC)
		
		#副本添加NPC
		self.JoinNPC(npc1)
		self.JoinNPC(npc2)
		self.JoinNPC(npc3)
		
	def AfterClickNPC(self, npc, role):
		#只有队长可以点击NPC
		if not self.team.IsTeamLeader(role):
			return
		
		dragonMgr = role.GetTempObj(EnumTempObj.DragonMgr)
		dragonConfig = DragonConfig.DRAGON_BASE.get((dragonMgr.level, dragonMgr.grade))
		if not dragonConfig:
			return
		
		#队伍能否进入战斗状态
		if not Status.CanInStatus_Roles(self.roles, EnumInt1.ST_FightStatus):
			return
		
		FightEx.PVE_GVEFB(role, self.team.members, npc.fightType, npc.mcid, dragonConfig.property_dict, self.AfterFight, npc, AfterPlay = self.AfterPlay)
		
	def AfterReLoginRole(self, role):
		team = role.GetTeam()
		if not team:
			return
		
		#重新登录触发(只同步数据)
		#角斗重新登录过触发恢复场景
		self.mirrorScene.RestoreRole(role)
		#同步副本所有NPC
		self.SyncALLNPC(role)
		#同步队伍信息
		team.SyncClient()
		#同步副本回合数
		role.SendObj(GVE_Show_Fight_Round, self.fightRound)
		
	def BeforeLeave(self, scene, role):
		#离开副本前调用
		MutilMirrorBase.MutilMirrorBase.BeforeLeave(self, role)
		
		#离开关卡调用， 一般用于角色掉线，或者没用通过回城达到离开关卡处理
		#请不要在此函数内调用scene.Destroy()
		
		#若没有完成翻牌奖励,则自动领取翻牌奖励
		self.GetCardReward(role)
		
		#退出多人副本状态
		Status.Outstatus(role, EnumInt1.ST_InTeamMirror)
	
		#清理临时缓存数据
		role.SetTempObj(EnumTempObj.MirrorScene, None)
		
		#退出GVE队伍
		team = role.GetTeam()
		if not team:
			return
		team.Quit(role)
	
	def AfterFight(self, fightObj):
		#增加回合数，无论战斗输赢
		self.fightRound += fightObj.round
		
		#是否战斗胜利
		if fightObj.result != 1:
			return
		
		roles = fightObj.left_camp.roles
		if not roles:
			return
		
		npc = fightObj.after_fight_param
		
		self.fightIndex = npc.index
		
		npcRewardId = npc.rewardId
		
		#销毁NPC
		npc.Destroy()
		
		#日志
		with TraGVEFightReward:
			self.FightReward(fightObj, npcRewardId)
	
	def AfterPlay(self, fightObj):
		for role in fightObj.left_camp.roles:
			#同步副本回合数
			role.SendObj(GVE_Show_Fight_Round, self.fightRound)
		
		if fightObj.result != 1:
			#传送队长，队员会自动跟随
			self.team.leader.JumpPos(self.fbConfig.posX, self.fbConfig.posY)
			return
		
		if self.fightIndex >= 3:
			#通关
			self.Finish()
			
	
	def FightReward(self, fightObj, rewardId):
		'''
		战斗掉落奖励
		'''
		rewardConfig = GVEConfig.GVE_FB_REWARD.get(rewardId)
		if not rewardConfig:
			return
		
		itemcoding, cnt = rewardConfig.randomObj.RandomOne()
		for member in self.team.members:
			#是否有奖励
			if member.GetRoleID() not in self.roleWhoCanGetReward:
				continue
			member.AddItem(itemcoding, cnt)
			#战斗结束展示
			fightObj.set_fight_statistics(member.GetRoleID(), EnumFightStatistics.EnumItems, [(itemcoding, cnt)])
	
	def CreateCardReward(self):
		'''
		通关翻牌奖励
		'''
		#奖励配置
		rewardConfig = GVEConfig.GVE_FB_REWARD.get(self.fbConfig.rewardId)
		if not rewardConfig:
			return
		
		#随机每个人的翻牌奖励内容
		for member in self.team.members:
			memberId = member.GetRoleID()
			if memberId in self.roleCardRewardItem:
				continue
			#星数表示可以翻牌的次数
			rewardItemList = rewardConfig.randomObj.RandomMany(self.star)
			#保存奖励物品
			self.roleCardRewardItem[memberId] = rewardItemList
			
			#是否消耗了收益次数
			if memberId in self.roleWhoCanGetReward:
				#同步客户端通关数据(星数，抽中的奖励，所有的抽奖物品)
				member.SendObj(GVE_Show_Finish_Data, (self.star, rewardItemList, rewardConfig.rewardItems))
			
	def GetCardReward(self, role):
		'''
		领取翻牌奖励
		@param role:
		'''
		roleId = role.GetRoleID()
		#是否可以领取奖励
		if roleId not in self.roleWhoCanGetReward:
			return
		
		#没有对应的翻牌奖励
		if roleId not in self.roleCardRewardItem:
			return
		
		#记录已领取
		self.roleWhoCanGetReward.remove(roleId)
		
		items = self.roleCardRewardItem[roleId]
		#日志
		with TraGVECardReward:
			#奖励
			for item in items:
				role.AddItem(*item)
	
	def Finish(self):
		self.isFisish = True
		
		#计算行星数量
		if self.fightRound <= 13:
			self.star = 3
		elif self.fightRound <= 17:
			self.star = 2
		
		#创建每个成员的翻牌奖励
		self.CreateCardReward()
		
	def BackToCity(self, role):
		MutilMirrorBase.MutilMirrorBase.BackToCity(self, role)
		
		#队伍成员数
		memberCnt = len(self.team.members)
		
		#如果队伍只剩下一个人，退出后队伍将解散，这时候要销毁GVE副本
		if memberCnt == 0:
			self.Destroy()
		
	def Destroy(self):
		#销毁多人副本(注意多人限时副本的处理需要非常小心,一般把权限交给C++处理比较好)
		if not self.mirrorScene:
			return
		if self.mirrorScene.IsDestroy():
			return
		#调用C++函数，踢掉副本内玩家,会触发玩家退出场景调用函数
		self.mirrorScene.Destroy()
		self.mirrorScene = None
		self.mirrorGId = 0
		