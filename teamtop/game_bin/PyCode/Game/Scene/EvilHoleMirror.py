#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Scene.EvilHoleMirror")
#===============================================================================
# 恶魔深渊,只有一个BOSS的副本
#===============================================================================
import cSceneMgr
import Environment
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumInt1, EnumObj, EnumTempObj
from Game.Scene import MirrorBase, MirrorIdAllot, SceneMgr
from Game.NPC.PrivateNPC import FBNPC
from Game.Role import Status, Event
from Game.Fight import FightEx
from Game.Task import EnumTaskType

if "_HasLoad" not in dir():
	#消息
	EvilHole_S_Finish = AutoMessage.AllotMessage("EvilHole_S_Finish", "同步通关恶魔深渊")
	EvilHole_S_FightRound = AutoMessage.AllotMessage("EvilHole_S_FightRound", "恶魔深渊战斗回合")
	
	#日志
	Tra_FB_EvilHoleFinish = AutoLog.AutoTransaction("Tra_FB_EvilHoleFinish", "恶魔深渊副本通关奖励")



#######################################################################################
#恶魔深渊副本
#######################################################################################
class EvilHoleMirror(MirrorBase.SingleMirrorBase):
	def __init__(self, role, evilHoleCfg):
		MirrorBase.SingleMirrorBase.__init__(self, role)
		self.evilHoleCfg = evilHoleCfg
		#获取场景配置
		SC = SceneMgr.SceneConfig_Dict.get(evilHoleCfg.sceneID)
		if not SC:
			print "GE_EXC, error in EvilHoleMirror scene not OK (%s)" % evilHoleCfg.sceneID
			return 
		
		#分配全局副本ID
		self.mirrorGId = MirrorIdAllot.AllotMirrorID()
		#尝试创建副本场景
		self.mirrorScene = cSceneMgr.CreateSingleMirrorScene(self.mirrorGId, SC.SceneId, SC.SceneName, SC.MapId, self.BeforeLeave)
		if not self.mirrorScene:
			#失败了
			return
		#尝试进入场景
		if not self.mirrorScene.JoinRole(role, evilHoleCfg.posX, evilHoleCfg.posY):
			return
		#强制进入状态
		Status.ForceInStatus(role, EnumInt1.ST_InMirror)
		#设置临时对象
		role.SetTempObj(EnumTempObj.MirrorScene, self)
		#是否通关
		self.isFinish = False
		self.fightRound = 0
		#创建完毕
		self.createOk = True

	def AfterJoinRole(self):
		#角色进入副本中
		MirrorBase.SingleMirrorBase.AfterJoinRole(self)
		#创建BOSS
		FBNPC.EvilHoleFightNPC(self.role, self.evilHoleCfg.bossData, self.AfterClickMonster)
		
		self.role.SendObj(EvilHole_S_FightRound, self.fightRound)
	def AfterReLoginRole(self, role):
		MirrorBase.SingleMirrorBase.AfterReLoginRole(self, role)
		#重登录进入副本逻辑
		self.role.SendObj(EvilHole_S_FightRound, self.fightRound)
		if self.isFinish is True:
			return
		#同步数据

	def AfterClickMonster(self, npc):
		#点击怪物
		#战斗状态
		if Status.IsInStatus(self.role, EnumInt1.ST_FightStatus):
			return
	
		#进入战斗
		FightEx.PVE_EvilHole(self.role, npc.fightId, npc.fightType, self.AfterFight, npc, AfterPlay = self.AfterPlay)
	
	def AfterFight(self, fightObj):
		#战斗回调
		pass
	
	def AfterPlay(self, fightObj):
		self.fightRound += fightObj.round
		self.role.SendObj_NoExcept(EvilHole_S_FightRound, self.fightRound)
		if fightObj.result != 1:
			return
		roles = fightObj.left_camp.roles
		if not roles:
			return
		
		npc = fightObj.after_fight_param
		npc.Destroy()
		
		star = 1
		if self.fightRound <= 10:
			star = 3
		elif self.fightRound <= 15:
			star = 2
			
		role = list(roles)[0]
	
		self.isFinish = True
		self.Finish(role, star) 
	
	def Finish(self, role, star):
		#通关调用
		evilHoleIndex = self.evilHoleCfg.evilIndex
		#星级记录
		starDict = role.GetObj(EnumObj.EvilHole_Star)
		starDict[evilHoleIndex] = max(starDict.get(evilHoleIndex, 0), star)
		
		with Tra_FB_EvilHoleFinish:
			#奖励
			self.evilHoleCfg.RewardRole(role, star, 1)
		
		#告诉客户端，等待回调
		role.SendObjAndBack(EvilHole_S_Finish, (evilHoleIndex, star), 10, self.CallBackReturnCity, None)
		
		Event.TriggerEvent(Event.Eve_SubTask, self.role, (EnumTaskType.EnSubTask_FinishEvilHole, evilHoleIndex))
	
		if Environment.EnvIsNA():
			HalloweenNAMgr = role.GetTempObj(EnumTempObj.HalloweenNAMgr)
			HalloweenNAMgr.ChallengeEvilHole(1)
			
	def CallBackReturnCity(self, role, callargv, regparam):
		#客户端请求回城
		self.Destroy()

	def BeforeLeave(self, scene, role):
		#离开副本之前调用
		MirrorBase.SingleMirrorBase.BeforeLeave(self, scene, role)
		role.SendObj(EvilHole_S_FightRound, -1)
