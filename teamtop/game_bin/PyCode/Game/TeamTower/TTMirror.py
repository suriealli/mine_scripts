#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.TeamTower.TTMirror")
#===============================================================================
# 组队爬塔场景
#===============================================================================
import cSceneMgr
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Common.Other import EnumGameConfig, EnumFightStatistics, GlobalPrompt
from Game.Role import Status, Event
from Game.TeamTower import TTNPC
from Game.Fight import FightEx
from Game.Role.Data import EnumInt1, EnumDayInt8, EnumTempObj, EnumObj
from Game.Scene import MutilMirrorBase, SceneMgr, MirrorIdAllot
from Game.SysData import WorldDataNotSync
from Game.ThirdParty.QQidip import QQEventDefine
from Game.SystemRank import SystemRank
from Game.Activity.SevenDayHegemony import SDHFunGather, SDHDefine

if "_HasLoad" not in dir():
	#消息
	TT_S_FightRound = AutoMessage.AllotMessage("TT_S_FightRound", "同步组队爬塔战斗总回合数")
	TT_S_FinishReward = AutoMessage.AllotMessage("TT_S_FinishReward", "同步组队爬塔通关章节奖励")
	TT_S_ShowData = AutoMessage.AllotMessage("TT_S_ShowData", "通知客户端组队爬塔基本数据")
	TT_S_NowLayer = AutoMessage.AllotMessage("TT_S_NowLayer", "通知客户端组队爬塔层数据")
	TT_S_Show_Invite_Data = AutoMessage.AllotMessage("TT_S_Show_Invite_Data", "通知客户端组队爬塔有人邀请你")
	TT_S_SyncBest = AutoMessage.AllotMessage("TT_S_SyncBest", "通知客户端角色在组队爬塔中的最好成绩")
	
	#日志
	Tra_TTFightReward = AutoLog.AutoTransaction("Tra_TTFightReward", "组队副本战斗奖励")
	Tra_TTFirstFinishReward = AutoLog.AutoTransaction("Tra_TTFirstFinishReward", "组队副本首次通关奖励")
	Tra_TTFinishReward = AutoLog.AutoTransaction("Tra_TTFinishReward", "组队副本章节通关奖励")
	Tra_TTRewardTimes = AutoLog.AutoTransaction("Tra_TTRewardTimes", "进入组队爬塔扣除收益次数")
	Tra_TTRewardExit = AutoLog.AutoTransaction("Tra_TTRewardExit", "组队爬塔有收益次数的退出爬塔副本")

class TTMirror(MutilMirrorBase.MutilMirrorBase):
	def __init__(self, team, ttconfig, ttLayerCfg = None, bossFightRound = 9999, rewardRoles = None, fightRound = 0):
		MutilMirrorBase.MutilMirrorBase.__init__(self)
		
		self.team = team
		self.ttconfig = ttconfig						#爬塔章节基本配置
		if ttLayerCfg is None:
			self.isFirst = True
			self.ttLayerCfg = ttconfig.ttLayerFirstCfg	#第一层配置
		else:
			self.isFirst = False
			self.ttLayerCfg = ttLayerCfg
		if rewardRoles is None:
			self.rewardRoles = set()					#有收益的角色
		else:
			self.rewardRoles = rewardRoles
			
		self.fightRound = fightRound					#战斗总回合数
		self.bossFightRound = bossFightRound			#上一层的BOSS击杀回合数
		self.nowIndex = -1
		
		self.readyJoinNext = False
		self.isFinish = False							#副本是否完成
		self.isFinishAll = False
		
		sceneId, self.posX, self.posY = self.ttLayerCfg.scenePos
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
		
	def AfterJoinRoles(self, roles):
		MutilMirrorBase.MutilMirrorBase.AfterJoinRoles(self, roles)
		for role in roles:
			#同步副本回合数
			role.SendObj(TT_S_FightRound, self.fightRound)
			#同步层数
			role.SendObj(TT_S_NowLayer, self.ttLayerCfg.layer)
			
			if not self.isFirst:
				continue
			if role.GetI1(EnumInt1.TeamTowerNoReward):
				#无奖励模式
				continue
			if role.GetDI8(EnumDayInt8.TT_RewradTimes) >= EnumGameConfig.TT_RewardTimes:
				continue
			with Tra_TTRewardTimes:
				#扣除次数
				role.IncDI8(EnumDayInt8.TT_RewradTimes, 1)
				Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_TT)
			#加入奖励列表
			self.rewardRoles.add(role)
			
		#创建副本NPC
		if self.ttLayerCfg.m1:
			self.NextNPC(0)
		else:
			self.NextNPC(2)
	
	def NextNPC(self, index = 0):
		#创建下一个NPC
		if index <= self.nowIndex:
			print "GE_EXC, error in teamtower NextNPC index (%s), (%s)" % (self.nowIndex, index)
			return
		self.nowIndex = index
			
		if index == 0:
			npc = TTNPC.TTMonsterNPC(self, 1, self.ttLayerCfg.m1, self.AfterClickNPC)
			self.JoinNPC(npc)
		elif index == 1:
			npc = TTNPC.TTMonsterNPC(self, 2, self.ttLayerCfg.m2, self.AfterClickNPC)
			self.JoinNPC(npc)
		elif index == 2:
			#创建BOSS
			npc = TTNPC.TTMonsterNPC(self, 3, self.ttLayerCfg.boss, self.AfterClickBoss)
			self.JoinNPC(npc)
		elif index == 3:
			#创建传送门
			npc = TTNPC.TTDoorNPC(self, 4, self.ttLayerCfg.door, self.AfterClickDoor)
			self.JoinNPC(npc)
	
	
	def AfterClickNPC(self, npc, role):
		#只有队长可以点击NPC
		if not self.team.IsTeamLeader(role):
			return
		
		#队伍能否进入战斗状态
		if not Status.CanInStatus_Roles(self.team.members, EnumInt1.ST_FightStatus):
			return
		
		#是否满足跳关，满足则直接发奖
		if self.ttLayerCfg.jumpRound and self.ttLayerCfg.jumpRound >= self.bossFightRound:
			npc.Destroy()
			#奖励
			with Tra_TTFightReward:
				self.Reward(npc.rewardcfg)
				
			#创建下一个NPC
			self.NextNPC(npc.index)
		else:
			FightEx.PVE_TT(role, self.team.members, npc.fightType, npc.mcid,  self.AfterFight, npc, AfterPlay = self.AfterPlay)
	
	def AfterClickBoss(self, npc, role):
		#只有队长可以点击NPC
		if not self.team.IsTeamLeader(role):
			return
		#队伍能否进入战斗状态
		if not Status.CanInStatus_Roles(self.team.members, EnumInt1.ST_FightStatus):
			return
		#进入战斗
		FightEx.PVE_TT(role, self.team.members, npc.fightType, npc.mcid,  self.AfterFight, npc, AfterPlay = self.AfterPlay)
	
	def AfterClickDoor(self, npc, role):
		#只有队长可以点击NPC
		if not self.team.IsTeamLeader(role):
			return
		#传送到下一层
		if not Status.CanInStatus_Roles(self.roles, EnumInt1.ST_TP):
			return
		
		if not self.ttLayerCfg.ttLayerNextCfg:
			return
		#设置当前副本标识
		self.readyJoinNext = True
		#清理所有的NPC
		self.ClearAllNPC()
		
		#进入下一个副本
		TTMirror(self.team, self.ttconfig, self.ttLayerCfg.ttLayerNextCfg, self.bossFightRound, self.rewardRoles, self.fightRound)
	
	
	def AfterReLoginRole(self, role):
		#断线重连后
		team = role.GetTeam()
		if not team : return
		
		#重新登录触发(只同步数据)
		#角斗重新登录过触发恢复场景
		self.mirrorScene.RestoreRole(role)
		#同步副本所有NPC
		self.SyncALLNPC(role)
		#同步队伍信息
		team.SyncClient()
		#同步副本回合数
		role.SendObj(TT_S_FightRound, self.fightRound)
		#同步层数
		role.SendObj(TT_S_NowLayer, self.ttLayerCfg.layer)
		

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
		with Tra_TTFightReward:
			self.Reward(npc.rewardcfg, fightObj)

	def AfterPlay(self, fightObj):
		for role in fightObj.left_camp.roles:
			#同步副本回合数
			role.SendObj(TT_S_FightRound, self.fightRound)
		
		if fightObj.result != 1:
			#传送队长，队员会自动跟随
			self.team.leader.JumpPos(self.posX, self.posY)
			return
		
		npc = fightObj.after_fight_param
		with Tra_TTFightReward:
			if npc.index == 3:
				#更新BOSS击杀回合数
				self.bossFightRound = fightObj.round
				#通关处理
				self.Finish()
			else:
				self.NextNPC(npc.index)

	def Reward(self, rewardcfg, fightObj = None):
		#战斗奖励
		for role in self.rewardRoles:
			rewrads = rewardcfg.RewardRole(role)
			money, soul, items = rewrads
			if fightObj:
				if money:
					fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumMoney, money)
				if soul:
					fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumDragonSoul, soul)
				if items:
					fightObj.set_fight_statistics(role.GetRoleID(), EnumFightStatistics.EnumItems, items)
			else:
				AutoLog.LogBase(role.GetRoleID(), AutoLog.eveTeamTowerJumpFight, (self.ttLayerCfg.index, self.ttLayerCfg.layer))
				tips = GlobalPrompt.TT_JumpReward_Tips
				
				tips += GlobalPrompt.Money_Tips % money
				tips += GlobalPrompt.DragonSoul_Tips % soul
				for itemCoding, itemCnt in items:
					tips += GlobalPrompt.Item_Tips % (itemCoding, itemCnt)
				
				role.Msg(2, 0, tips)
				
	def Finish(self):
		#通关
		if self.isFinish is True:
			print "GE_EXC, repeat finish TTMirror"
			return
		self.isFinish = True
		
		nowLayer = self.ttLayerCfg.layer
		nowIndex = self.ttLayerCfg.index
		
		if self.ttLayerCfg.hasFirst:
			#首次通关奖励
			hasFirst = True
			money = self.ttLayerCfg.firstMoney
			items = self.ttLayerCfg.firstItems
			rmb = self.ttLayerCfg.firstRMB
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
			
		with Tra_TTFirstFinishReward:
			for role in self.roles:
				ttdata = role.GetObj(EnumObj.TeamTowerData)
				maxlayerdict = ttdata[1]
				oldlayer = maxlayerdict.get(nowIndex, 0)
				if oldlayer >= nowLayer:
					#已经打过这层了
					continue
				#首次通关更新最大层	
				maxlayerdict[nowIndex] = nowLayer
				role.SendObj(TT_S_ShowData, maxlayerdict)
				if hasFirst is False:
					continue
				if money:
					role.IncMoney(money)
					
				#YY防沉迷对奖励特殊处理
				if items or rmb:
					yyAntiFlag = role.GetAnti()
					if yyAntiFlag == 1:
						items = self.ttLayerCfg.firstItems_fcm
						rmb = self.ttLayerCfg.firstRMB_fcm
					elif yyAntiFlag == 0:
						items = self.ttLayerCfg.firstItems
						rmb = self.ttLayerCfg.firstRMB
					else:
						items = None
						rmb = 0
						role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
					
				if rmb:
					role.IncBindRMB(rmb)
				if items:
					for itemCoding, itemCnt in items:
						role.AddItem(itemCoding, itemCnt)
				
				role.Msg(2, 0, tips)
		
		for role in self.roles:
			#通关额外提示
			role.SendObj(TT_S_NowLayer, nowLayer + 1)
		
		
		
		#是否有下一层
		if self.ttconfig.maxLayer <= self.ttLayerCfg.layer:
			#通关章节
			self.FinishAll()
		else:
			#还没有全部打完
			if self.ttLayerCfg.ttLayerNextCfg:
				#创建传送门
				self.NextNPC(3)
				for role in self.rewardRoles:
					ttdata = role.GetObj(EnumObj.TeamTowerData)
					#更新今天通关的记录
					ttdata[3] = [nowIndex, nowLayer, 0]
				
			else:
				print "GE_EXC, error in teamtower ttLayerNextCfg is None index(%s), layer(%s)" % (self.ttLayerCfg.index, self.ttLayerCfg.layer)
	
	def FinishAll(self):
		self.isFinishAll = True
		#计算评分
		s = 7
		for fround, score in self.ttconfig.score:
			if self.fightRound <= fround:
				s = score
				break
		
		reward = self.ttconfig.GetReward(None, s)
		if reward:
			#奖励
			with Tra_TTFinishReward:
				for role in self.roles:
					if role in self.rewardRoles:
						_reward = self.ttconfig.GetReward(role, s)
						if not _reward:
							role.SendObjAndBack(TT_S_FinishReward, (s, 0, 0, []), 15, self.CallBackToCity)
							continue
						
						_money, _soul, _items = _reward
						role.IncMoney(_money)
						role.IncDragonSoul(_soul)
						for itemCoding, itemCnt in _items:
							role.AddItem(itemCoding, itemCnt)
						role.SendObjAndBack(TT_S_FinishReward, (s, _money, _soul, _items), 15, self.CallBackToCity)
						#更新排行榜(有收益次数才更新排行榜)
						SystemRank.UpdateTTRank(role, self.ttconfig.index, s, self.fightRound)
						ttdata = role.GetObj(EnumObj.TeamTowerData)
						#更新今天通关的记录
						ttdata[3] = [self.ttLayerCfg.index, self.ttLayerCfg.layer, s]
					else:
						role.SendObjAndBack(TT_S_FinishReward, (s, 0, 0, []), 15, self.CallBackToCity)
					
					
					#更新角色的最好成绩
					TeamTowerData = role.GetObj(EnumObj.TeamTowerData)
					historyIndex, historyRound = TeamTowerData.get(2, [0, 0])
					currentData = [self.ttconfig.index, self.fightRound]
					if self.ttconfig.index > historyIndex:
						role.GetObj(EnumObj.TeamTowerData)[2] = currentData
					elif self.ttconfig.index == historyIndex:
						if historyRound > self.fightRound or historyRound == 0:
							role.GetObj(EnumObj.TeamTowerData)[2] = currentData
					
					bestData = role.GetObj(EnumObj.TeamTowerData).get(2, [0, 0])
					
					if SDHFunGather.StartFlag[SDHDefine.TeamTower] is True:
						role.SendObj(TT_S_SyncBest, bestData)
					
					

		else:
			print "GE_EXC, not reward in team tower score (%s)" % s
			for role in self.roles:
				role.SendObjAndBack(TT_S_FinishReward, (s, 0, 0, []), 15, self.CallBackToCity)
			
		#更新全服通关人数次数
		mancnt = len(self.rewardRoles)
		if mancnt > 0:
			wtd = WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.TeamTowerFinishDict]
			wtd[self.ttconfig.index] = wtd.get(self.ttconfig.index, 0) + mancnt
			WorldDataNotSync.WorldDataPrivate.HasChange()
		
		for role in self.roles:
			role.SendObj(TT_S_ShowData, role.GetObj(EnumObj.TeamTowerData)[1])
	
	
	def CallBackToCity(self, role, callArgv, regparam):
		if not role.GetTempObj(EnumTempObj.MirrorScene):
			return
		if role not in self.roles:
			return
		
		self.BackToCity(role)


	def BackToCity(self, role):
		MutilMirrorBase.MutilMirrorBase.BackToCity(self, role)


	def BeforeLeave(self, scene, role):
		#离开副本前调用
		MutilMirrorBase.MutilMirrorBase.BeforeLeave(self, role)
		#离开关卡调用， 一般用于角色掉线，或者没用通过回城达到离开关卡处理
		#请不要在此函数内调用scene.Destroy()
		#退出多人副本状态
		Status.Outstatus(role, EnumInt1.ST_InTeamMirror)
		
		mirrorScene = role.GetTempObj(EnumTempObj.MirrorScene)
		#清理临时缓存数据
		role.SetTempObj(EnumTempObj.MirrorScene, None)
		if mirrorScene:
			if mirrorScene.readyJoinNext is True:
				return
			if role in mirrorScene.rewardRoles:
				#移出收益列表
				mirrorScene.rewardRoles.discard(role)
				with Tra_TTRewardExit:
					AutoLog.LogBase(role.GetRoleID(), AutoLog.eveTeamTowerExitReward, mirrorScene.ttLayerCfg.layer)
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
		
