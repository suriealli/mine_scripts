#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Scene.FBMirror")
#===============================================================================
# 单人副本
#===============================================================================

import cRoleMgr
import cSceneMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt, EnumFightStatistics, EnumGameConfig
from ComplexServer.Log import AutoLog
from Game.Scene import MirrorBase, SceneMgr, MirrorIdAllot
from Game.Role.Data import EnumObj, EnumInt1, EnumTempObj, EnumInt16
from Game.FB import FBReward
from Game.NPC.PrivateNPC import FBNPC 
from Game.Role import Status, Event
from Game.Fight import FightEx
from Game.SysData import WorldData
from Game.Task import EnumTaskType
from Game.DailyDo import DailyDo




if "_HasLoad" not in dir():
	#消息
	FB_S_StarReward = AutoMessage.AllotMessage("FB_S_StarReward", "同步副本通关星级和翻牌奖励")
	FB_S_FightRound = AutoMessage.AllotMessage("FB_S_FightRound", "同步副本战斗回合数")
	
	FB_S_UpdataStar = AutoMessage.AllotMessage("FB_S_UpdataStar", "同步更新一个副本星级")
	
	
	#日志
	Tra_FB_FightReward = AutoLog.AutoTransaction("Tra_FB_FightReward", "副本战斗奖励")
	Tra_FB_FinishCard = AutoLog.AutoTransaction("Tra_FB_FinishCard", "副本通关翻牌奖励")
	Tra_FB_Finish = AutoLog.AutoTransaction("Tra_FB_Finish", "副本通关")
####################################################################################



#普通副本
class FBMirror(MirrorBase.SingleMirrorBase): 
	def __init__(self, role, mirrorCfg):
		self.createOk = False
		MirrorBase.SingleMirrorBase.__init__(self, role)
		#关卡配置
		self.mirrorCfg = mirrorCfg
		
		#获取场景配置
		SC = SceneMgr.SceneConfig_Dict.get(mirrorCfg.sceneID)
		if not SC:
			print "GE_EXC, error in SceneMgr.SceneConfig_Dict.get(fbCfg.sceneID) (%s)" % mirrorCfg.sceneID
			return 
		#分配全局副本ID
		self.mirrorGId = MirrorIdAllot.AllotMirrorID()
		#尝试创建副本场景
		self.mirrorScene = cSceneMgr.CreateSingleMirrorScene(self.mirrorGId, SC.SceneId, SC.SceneName, SC.MapId, self.BeforeLeave)
		if not self.mirrorScene:
			return
		#尝试进入场景
		if not self.mirrorScene.JoinRole(role, mirrorCfg.posX, mirrorCfg.posY):
			return
		
		#强制进入状态
		Status.ForceInStatus(role, EnumInt1.ST_InMirror)
		#设置临时对象
		role.SetTempObj(EnumTempObj.MirrorScene, self)
		#是否通关
		self.isFinish = False

		self.nowFightIndex = 0#现在需要击杀的怪物顺序
		self.fightRound = 0
		
		self.createOk = True
	
	def AfterJoinRole(self):
		#角色进入副本后调用
		
		MirrorBase.SingleMirrorBase.AfterJoinRole(self)
		
		#进入副本，初始化或者清理怒气值
		self.role.SetTempObj(EnumTempObj.FB_Moral, {})
		fbpro = self.role.GetObj(EnumObj.FB_Progress)
		if self.mirrorCfg.FBID not in fbpro:
			#新的一次进入
			fbpro[self.mirrorCfg.FBID] = {1 : 0, 2 : 0, 3 : 0, 4 : None}# 1:回合数 2:正在准备攻击第几个怪物, 3:通关星级(未领取奖励)
			#创建NPC
			for index, npcCfg in enumerate(self.mirrorCfg.monsterCfgs):
				#必须按照顺序创建NPC
				FBNPC.FBFightNPC(self.role, index, npcCfg, self.AfterClickNpc)
			
			self.role.SendObj(FB_S_FightRound, self.fightRound)
		else:
			#继续战斗
			dataDict = fbpro[self.mirrorCfg.FBID]
			
			self.fightRound = dataDict[1]
			self.nowFightIndex = dataDict[2]
			self.role.SendObj(FB_S_FightRound, self.fightRound)
			if self.nowFightIndex < 3:
				#还有怪物
				for index, npcCfg in enumerate(self.mirrorCfg.monsterCfgs):
					#创建未被击杀的NPC
					if index < self.nowFightIndex:
						continue
					FBNPC.FBFightNPC(self.role, index, npcCfg, self.AfterClickNpc)
			
			elif dataDict[4]:
				#没有怪物了，看看是不是需要翻牌
				FlipCard(self.role, self.mirrorCfg.FBID, dataDict[3], dataDict[4], FBReward.GetAllRewardItems(self.mirrorCfg.rewardId))
			
	def AfterReLoginRole(self, role):
		#重新登录触发(只同步数据)
		MirrorBase.SingleMirrorBase.AfterReLoginRole(self, role)
		fbpro = self.role.GetObj(EnumObj.FB_Progress)
		self.role.SendObj(FB_S_FightRound, self.fightRound)
		if self.mirrorCfg.FBID in fbpro:
			dataDict = fbpro[self.mirrorCfg.FBID]
			if dataDict[4]:
				#没有怪物了，看看是不是需要翻牌
				FlipCard(self.role, self.mirrorCfg.FBID, dataDict[3], dataDict[4], FBReward.GetAllRewardItems(self.mirrorCfg.rewardId))
				
	def JumpDoor(self, role):
		#战斗失败,传送到进入起始点
		role.JumpPos(self.mirrorCfg.posX, self.mirrorCfg.posY)


	def AfterClickNpc(self, npc):
		#点击NPC
		#战斗状态
		if not Status.CanInStatus(self.role, EnumInt1.ST_FightStatus):
			return
		
		if npc.index > self.nowFightIndex:
			#必须按照顺序击杀怪物
			self.role.Msg(2, 0, GlobalPrompt.FB_Tips_1)
			return
		
		FightEx.PVE_FB(self.role, npc.fightId, npc.fightType, self.AfterFight, npc, AfterPlay = self.AfterPlay)
	
	
	def AfterFight(self, fightObj):
		#增加回合数，无论战斗输赢
		self.fightRound += fightObj.round
		if  self.role.IsKick():
			return
		proDict = self.role.GetObj(EnumObj.FB_Progress).get(self.mirrorCfg.FBID)
		proDict[1] = self.fightRound
		if fightObj.result != 1:
			return
		roles = fightObj.left_camp.roles
		if not roles:
			return
		
		npc = fightObj.after_fight_param
		#准备击杀下一个
		nextIndex = npc.index + 1
		if nextIndex != self.nowFightIndex + 1:
			print "GE_EXC error in FB afterfight nowFightIndex(%s), nextIndex(%s)" % (self.nowFightIndex, nextIndex)
			return
		with Tra_FB_FightReward:
			#注意先销毁这个NPC
			money, items = npc.Destroy()
			
			if money:
				fightObj.set_fight_statistics(self.role.GetRoleID(), EnumFightStatistics.EnumMoney, money)
			if items:
				fightObj.set_fight_statistics(self.role.GetRoleID(), EnumFightStatistics.EnumItems, items)
		#再写入数据
		proDict[2] = nextIndex
		self.nowFightIndex = nextIndex
		
	def AfterPlay(self, fightObj):
		if self.role.IsKick():
			return
		self.role.SendObj_NoExcept(FB_S_FightRound, self.fightRound)
		if fightObj.result != 1:
			self.role.JumpPos(self.mirrorCfg.posX, self.mirrorCfg.posY)
			return
		
		roles = fightObj.left_camp.roles
		if not roles:
			return

		if self.nowFightIndex >= 3:
			#通关
			self.Finish()
		
	def Finish(self):
		#通关调用
		proDict = self.role.GetObj(EnumObj.FB_Progress).get(self.mirrorCfg.FBID, None)
		if proDict is None:
			print "GE_EXC, error in  fb Finish not proDict"
			return
		star = 1
		if self.fightRound <= 13:
			star = 3
		elif self.fightRound <= 17:
			star = 2
	
		itemList = FBReward.FlipCardReward(self.role, self.mirrorCfg.rewardId, star)
		proDict[3] = star
		proDict[4] = itemList
		#发送翻牌数据
		FlipCard(self.role, self.mirrorCfg.FBID, star, itemList, FBReward.GetAllRewardItems(self.mirrorCfg.rewardId))
		#更新星级记录
		starDataDict = self.role.GetObj(EnumObj.FB_Star)
		oldStar = starDataDict.get(self.mirrorCfg.FBID, 0)
		if star > oldStar:
			starDataDict[self.mirrorCfg.FBID] = star
			self.role.SendObj(FB_S_UpdataStar, (self.mirrorCfg.FBID, star))
		
		with Tra_FB_Finish:
			#更新激活记录
			self.role.SetI16(EnumInt16.FB_Active_ID, max(self.role.GetI16(EnumInt16.FB_Active_ID), self.mirrorCfg.FBID))
		
		if self.mirrorCfg.FBID > WorldData.GetWorldMaxFBID():
			WorldData.SetWorldMaxFBID(self.mirrorCfg.FBID)
			cRoleMgr.Msg(11, 0, GlobalPrompt.FB_Tips_2 % (self.role.GetRoleName(), self.mirrorCfg.fbName))
		
		
		
		Event.TriggerEvent(Event.Eve_SubTask, self.role, (EnumTaskType.EnSubTask_FinishFB, self.mirrorCfg.FBID))
		
		#每日必做 -- 通关副本
		Event.TriggerEvent(Event.Eve_DoDailyDo, self.role, (DailyDo.Daily_FB, 1))
		
		Event.TriggerEvent(Event.Eve_LatestActivityTask, self.role, (EnumGameConfig.LA_FB, 1))
		
	def BeforeLeave(self, scene, role):
		#离开副本之前调用
		MirrorBase.SingleMirrorBase.BeforeLeave(self, scene, role)
		
		role.SendObj(FB_S_FightRound, -1)


def FlipCard(role, fbId, star, items, allItems):
	#同步角色翻牌奖励和星级
	role.SendObj(FB_S_StarReward, (fbId, star, items, allItems))


def GetFBStarReward(role, msg):
	'''
	领取副本通关翻牌奖励
	@param role:
	@param msg:
	'''
	FBID = msg
	fbproDict = role.GetObj(EnumObj.FB_Progress)
	if FBID not in fbproDict:
		return
	
	datadict = fbproDict[FBID]
	if datadict[2] < 3:
		#没有通关
		return
	
	if not datadict[3]:
		return
	itemList = datadict[4]
	if not itemList:
		return
	#清理进度
	del fbproDict[FBID]
	
	with Tra_FB_FinishCard:
		#发奖励
		for itemCoding, cnt in itemList:
			role.AddItem(itemCoding, cnt)


if "_HasLoad" not in dir():
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("FB_GetFBStarReward", "请求领取副本通关翻牌奖励"), GetFBStarReward)


