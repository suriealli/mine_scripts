#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.CrossTeamTower.CTTMirror")
#===============================================================================
# 虚空幻境场景
#===============================================================================
import cSceneMgr
import cComplexServer
from Game.Scene import MutilMirrorBase, SceneMgr, MirrorIdAllot
from Game.CrossTeamTower import CTTConfig, CTTNPC, CTTRank
from Game.Role import Status
from Game.Role.Data import EnumInt1, EnumDayInt8, EnumInt16, EnumTempObj
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import EnumGameConfig, EnumFightStatistics, GlobalPrompt
from Game.Fight import FightEx


if "_HasLoad" not in dir():
	CTT_S_FightRound = AutoMessage.AllotMessage("CTT_S_FightRound", "同步虚空幻境战斗总回合数")
	CTT_S_NowLayer = AutoMessage.AllotMessage("CTT_S_NowLayer", "同步组虚空幻境层数")
	CTT_S_FinishTower = AutoMessage.AllotMessage("CTT_S_FinishTower", "通知客户端虚空幻境已全部爬完")
	
	FB_KEEP_TIME = 90 * 60
	#日志
	Tra_CTTRewardTimes = AutoLog.AutoTransaction("Tra_CTTRewardTimes", "进入虚空幻境扣除收益次数")
	Tra_CTTFightReward = AutoLog.AutoTransaction("Tra_CTTFightReward", "虚空幻境战斗奖励")
	Tra_CTTFirstFinishReward = AutoLog.AutoTransaction("Tra_CTTFirstFinishReward", "虚空幻境首次通关奖励")
	
class CTTMirror(MutilMirrorBase.MutilMirrorBase):
	def __init__(self, team, IsFirst = True, bossFightRound = 9999, fightRound = 0, layer = 1, rewardRoles = None, norewardRoles = None):
		MutilMirrorBase.MutilMirrorBase.__init__(self)
		
		self.team = team
		self.IsFirst = IsFirst
		self.isFinish = False
		self.readyJoinNext = False
		
		if rewardRoles is None:
			self.rewardRoles = set()				#有收益的角色
		else:
			self.rewardRoles = rewardRoles
			
		if norewardRoles is None:
			self.norewardRoles = set()				#无收益玩家，只有幻境点奖励
		else:
			self.norewardRoles = norewardRoles
		
		self.fightRound = fightRound			#战斗总回合数
		self.bossFightRound = bossFightRound	#上一层的BOSS击杀回合数
		self.layer = layer						#当前的层数
		self.index = -1							#当前层数的第几波
		
		self.nowlayer_cfg = CTTConfig.CTeamTowerLayerConfig_Dict.get(self.layer)
		sceneId, self.posX, self.posY = self.nowlayer_cfg.scenePos
		#获取场景配置
		sceneConfig = SceneMgr.SceneConfig_Dict.get(sceneId)
		if not sceneConfig:
			print "GE_EXC, TTMirror not this scene (%s)" % sceneId
			return
		
		#分配全局副本ID
		self.mirrorGId = MirrorIdAllot.AllotMirrorID()
		#尝试创建副本场景
		self.mirrorScene = cSceneMgr.CreateMultiMirrorScene(self.mirrorGId, sceneId, sceneConfig.SceneName, sceneConfig.MapId, self.BeforeLeave)
		if not self.mirrorScene:
			print "GE_EXC, CreateMultiMirrorScene error in TTMirror" 
			return
		
		#尝试进入场景
		for member in team.members:
			if not self.mirrorScene.JoinRole(member, self.posX, self.posY):
				print "GE_EXC, TTMirror join role error"
				continue
		
		#强制进入状态
		Status.ForceInStatus_Roles(team.members, EnumInt1.ST_InTeamMirror)
		#进入副本场景后调用
		self.AfterJoinRoles(team.members)
		
		#注册一个60分钟的Tick
		self.SpecialTickID = cComplexServer.RegTick(FB_KEEP_TIME, self.EndFBCallBack, None)
		
	def EndFBCallBack(self, callargv, regparam):
		for role in list(self.roles):
			self.BackToCity(role)
		
	def AfterJoinRole(self, role):
		#爬塔过程中有人加入队伍
		self.roles.add(role)
		#设置临时对象
		role.SetTempObj(EnumTempObj.MirrorScene, self)
		#强制进入状态
		Status.ForceInStatus(role, EnumInt1.ST_InTeamMirror)
		#同步副本回合数
		role.SendObj(CTT_S_FightRound, self.fightRound)
		#同步层数
		role.SendObj(CTT_S_NowLayer, self.layer)
		
		if role.GetI1(EnumInt1.CTTNoRewardState):
			self.norewardRoles.add(role)
		elif role.GetDI8(EnumDayInt8.CTTRewardTimes) >= EnumGameConfig.CTT_RewardTimes:
			self.norewardRoles.add(role)
		else:
			#加入奖励列表
			self.rewardRoles.add(role)
			with Tra_CTTRewardTimes:
				#扣除次数
				role.IncDI8(EnumDayInt8.CTTRewardTimes, 1)
		
	def AfterJoinRoles(self, roles):
		MutilMirrorBase.MutilMirrorBase.AfterJoinRoles(self, roles)
		for role in roles:
			#同步副本回合数
			role.SendObj(CTT_S_FightRound, self.fightRound)
			#同步层数
			role.SendObj(CTT_S_NowLayer, self.layer)
			
			if not self.IsFirst:
				continue
			
			if role.GetI1(EnumInt1.CTTNoRewardState):
				self.norewardRoles.add(role)
				continue
			if role.GetDI8(EnumDayInt8.CTTRewardTimes) >= EnumGameConfig.CTT_RewardTimes:
				self.norewardRoles.add(role)
				continue
			#加入奖励列表
			self.rewardRoles.add(role)
			
			if self.layer != 1:
				continue
			with Tra_CTTRewardTimes:
				#扣除次数
				role.IncDI8(EnumDayInt8.CTTRewardTimes, 1)
			
		#创建副本NPC
		if self.nowlayer_cfg.m1:
			self.NextNPC(0)
		else:
			self.NextNPC(2)
		
	def NextNPC(self, index = 0):
		#创建下一个NPC
		if index <= self.index:
			print "GE_EXC, error in teamtower NextNPC index (%s), (%s)" % (self.layer, index)
			return
		self.index = index
			
		if index == 0:
			npc = CTTNPC.CTTMonsterNPC(self, 1, self.nowlayer_cfg.m1, self.AfterClickNPC)
			self.JoinNPC(npc)
		elif index == 1:
			npc = CTTNPC.CTTMonsterNPC(self, 2, self.nowlayer_cfg.m2, self.AfterClickNPC)
			self.JoinNPC(npc)
		elif index == 2:
			#创建BOSS
			npc = CTTNPC.CTTMonsterNPC(self, 3, self.nowlayer_cfg.boss, self.AfterClickBoss)
			self.JoinNPC(npc)
		elif index == 3:
			#创建传送门
			npc = CTTNPC.CTTDoorNPC(self, 4, self.nowlayer_cfg.door, self.AfterClickDoor)
			self.JoinNPC(npc)
	
	def AfterClickNPC(self, npc, role):
		#只有队长可以点击NPC
		if not self.team.IsTeamLeader(role):
			return
		
		#队伍能否进入战斗状态
		if not Status.CanInStatus_Roles(self.team.members, EnumInt1.ST_FightStatus):
			return
		
		#是否满足跳关，满足则直接发奖
		if self.nowlayer_cfg.jumpRound and self.nowlayer_cfg.jumpRound >= self.bossFightRound:
			npc.Destroy()
			#奖励
			with Tra_CTTFightReward:
				self.Reward(npc.rewardcfg)
				
			#创建下一个NPC
			self.NextNPC(npc.index)
		else:
			FightEx.PVE_CTT(role, self.team.members, npc.fightType, npc.mcid, self.AfterFight, npc, AfterPlay = self.AfterPlay)
	
	def AfterClickBoss(self, npc, role):
		#只有队长可以点击NPC
		if not self.team.IsTeamLeader(role):
			return
		#队伍能否进入战斗状态
		if not Status.CanInStatus_Roles(self.team.members, EnumInt1.ST_FightStatus):
			return
		#进入战斗
		FightEx.PVE_CTT(role, self.team.members, npc.fightType, npc.mcid, self.AfterFight, npc, AfterPlay = self.AfterPlay)
		
	def AfterClickDoor(self, npc, role):
		#只有队长可以点击NPC
		if not self.team.IsTeamLeader(role):
			return
		#传送到下一层
		if not Status.CanInStatus_Roles(self.roles, EnumInt1.ST_TP):
			return
		
		if not self.nowlayer_cfg.nextlayer:
			return
		#设置当前副本标识
		self.readyJoinNext = True
		#清理所有的NPC
		self.ClearAllNPC()
		#进入下一个副本
		CTTMirror(self.team, False, self.bossFightRound, self.fightRound, self.nowlayer_cfg.nextlayer, self.rewardRoles, self.norewardRoles)
		
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
		#销毁NPC
		npc.Destroy()
		
		#日志
		with Tra_CTTFightReward:
			self.Reward(npc.rewardcfg, fightObj)

	def AfterPlay(self, fightObj):
		for role in fightObj.left_camp.roles:
			#同步副本回合数
			if role.IsKick():
				continue
			role.SendObj(CTT_S_FightRound, self.fightRound)
		
		if fightObj.result != 1:
			#传送队长，队员会自动跟随
			if self.team.leader.IsKick():
				return
			self.team.leader.JumpPos(self.posX, self.posY)
			return
		
		npc = fightObj.after_fight_param
		with Tra_CTTFightReward:
			if npc.index == 3:
				#更新BOSS击杀回合数
				self.bossFightRound = fightObj.round
				#通关处理
				self.Finish()
			else:
				self.NextNPC(npc.index)
	
	def Finish(self):
		#通关
		if self.isFinish is True:
			print "GE_EXC, repeat finish TTMirror"
			return
		self.isFinish = True
		
		nowLayer = self.nowlayer_cfg.layer
		
		if self.nowlayer_cfg.hasFirst:
			#首次通关奖励
			hasFirst = True
			money = self.nowlayer_cfg.firstMoney
			items = self.nowlayer_cfg.firstItems
			rmb = self.nowlayer_cfg.firstRMB
			tips = GlobalPrompt.TT_First_Reward_Tips % nowLayer
			if money:
				tips = tips + GlobalPrompt.Money_Tips % money
			if rmb:
				tips = tips + GlobalPrompt.BindRMB_Tips % rmb
			if items:
				for itemCoding, itemCnt in items:
					tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
		else:
			hasFirst = False
			money = 0
			rmb = 0
			items = None
			tips = None
			
		with Tra_CTTFirstFinishReward:
			for role in self.roles:
				if role.IsKick():
					continue
				oldlayer = role.GetI16(EnumInt16.CTTMaxLayer)
				if oldlayer >= self.layer:
					continue
				else:
					role.SetI16(EnumInt16.CTTMaxLayer, self.layer)
				if hasFirst is False:
					continue
				if money:
					role.IncMoney(money)
				if rmb:
					role.IncBindRMB(rmb)
				if items:
					for itemCoding, itemCnt in items:
						role.AddItem(itemCoding, itemCnt)
				
				role.Msg(2, 0, tips)
		
		for role in self.roles:
			#通关额外提示
			role.SendObj(CTT_S_NowLayer, nowLayer + 1)
		
		#是否有下一层
		if not self.nowlayer_cfg.nextlayer:
			#通关章节
			self.FinishAll()
		else:
			#还没有全部打完
			if self.nowlayer_cfg.nextlayer:
				#创建传送门
				self.NextNPC(3)
			else:
				print "GE_EXC, error in teamtower nextlayer is None index(%s), layer(%s)" % (self.ttLayerCfg.index, self.ttLayerCfg.layer)
	
	
	def FinishAll(self):
		self.isFinishAll = True
		
		#取消服务器tick
		cComplexServer.UnregTick(self.SpecialTickID)
		
		for role in self.roles:
			role.SendObjAndBack(CTT_S_FinishTower, None, 5, self.CallBackToCity)
			
	def CallBackToCity(self, role, callArgv, regparam):
		if not role.GetTempObj(EnumTempObj.MirrorScene):
			return
		if role not in self.roles:
			return
		self.BackToCity(role)
		
	def BackToCity(self, role):
		#将玩家传送进场景
		from Game.CrossTeamTower import CrossTTMgr
		posx, posy = CrossTTMgr.GetTPPox()
		role.Revive(EnumGameConfig.CTT_SCENE_ID, posx, posy)
			
	def JoinNPC(self, npc):
		#加入一个NPC
		self.mirrorNPCDict[npc.gid] = npc
		#同步消息
		npc.SyncToRoles(self.roles)
	
	def Reward(self, rewardcfg, fightObj = None):
		#战斗奖励
		#无收益的玩家奖励幻境点
		for role in self.norewardRoles:
			if role.IsKick():
				continue
			point = rewardcfg.RewardCTTPoint(role)
			if fightObj:
				if point:
					fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumCrossTTPoint, point)
			else:
				tips = GlobalPrompt.TT_JumpReward_Tips
				if point:
					tips += GlobalPrompt.CTT_POINT_Tips % point
					role.Msg(2, 0, tips)
		#有收益的玩家
		for role in self.rewardRoles:
			if role.IsKick():
				continue
			rewrads = rewardcfg.RewardRole(role)
			money, items = rewrads
			if fightObj:
				if money:
					fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumMoney, money)
				if items:
					fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumItems, items)
			else:
				AutoLog.LogBase(role.GetRoleID(), AutoLog.eveTeamTowerJumpFight, (self.nowlayer_cfg.layer))
				tips = GlobalPrompt.TT_JumpReward_Tips
				
				if money:
					tips += GlobalPrompt.Money_Tips % money
				if items:
					for itemCoding, itemCnt in items:
						tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
				if money or items:
					role.Msg(2, 0, tips)
				
	def BeforeLeave(self, scene, role):
		#离开副本前调用
		MutilMirrorBase.MutilMirrorBase.BeforeLeave(self, role)
		#离开关卡调用， 一般用于角色掉线，或者没用通过回城达到离开关卡处理
		#请不要在此函数内调用scene.Destroy()
		#退出多人副本状态
		Status.Outstatus(role, EnumInt1.ST_InTeamMirror)
		#更新排行榜数据
		if self.isFinish is True:
			CTTRank.UpdateCTTRank(role, self.fightRound, self.layer)
		else:
			CTTRank.UpdateCTTRank(role, self.fightRound, self.layer - 1)
		
		mirrorScene = role.GetTempObj(EnumTempObj.MirrorScene)
		#清理临时缓存数据
		role.SetTempObj(EnumTempObj.MirrorScene, None)
		if mirrorScene:
			if mirrorScene.readyJoinNext is True:
				return
			if role in mirrorScene.rewardRoles:
				#移出收益列表
				mirrorScene.rewardRoles.discard(role)
			if role in mirrorScene.norewardRoles:
				mirrorScene.norewardRoles.discard(role)
		else:
			print "GE_EXC, TTMirror BeforeLeave error not mirrorScene (%s) " % role.GetRoleID()
		team = role.GetTeam()
		if not team:
			return
		#队伍成员数
		memberCnt = len(team.members)
		team.Quit(role)
		#如果队伍只剩下一个人，退出后队伍将解散，这时候要销毁副本
		if memberCnt == 1:
			self.ReadyToDestroy()
				
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