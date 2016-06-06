#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Scene.GoldMirror")
#===============================================================================
# 金币副本
#===============================================================================
import Environment
import cDateTime
import cSceneMgr
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Scene import SceneMgr, MirrorBase, MirrorIdAllot
from Game.Fight import FightEx
from Game.Role import Status, Event
from Game.Role.Data import  EnumTempObj, EnumInt1, EnumDayInt1
from Game.Activity.GoldMirror import GoldMirrorConfig
from Game.NPC.PrivateNPC import PrivateNPC

if "_HasLoad" not in dir():
	#消息
	GoldMirror_lastgold = AutoMessage.AllotMessage("GoldMirror_lastgold", "同步客户端弹出接金币玩法")
	GoldMirror_GetGold = AutoMessage.AllotMessage("GoldMirror_GetGold", "同步金币副本获取金币数")

	#日志
	GoldMirrorGold= AutoLog.AutoTransaction("GoldMirrorGold", "经验副本获取金币")
	
	MAX_GOLD = 1 #大金币类型
	CallBackSec = 600
	
class GoldMirror(MirrorBase.SingleMirrorBase):
	
	def __init__(self, role, goldCfg, total = 0, days = 0):
		MirrorBase.SingleMirrorBase.__init__(self, role)
		#关卡配置
		self.goldCfg = goldCfg
		self.total_money = total
		self.gold_length = 0
		self.days = days
		#获取场景配置
		SC = SceneMgr.SceneConfig_Dict.get(goldCfg.sceneID)
		if not SC:
			print "GE_EXC, error in SceneMgr.SceneConfig_Dict.get(goldCfg.sceneID) (%s)" % goldCfg.sceneID
			return 
		#分配全局副本ID
		self.mirrorGId = MirrorIdAllot.AllotMirrorID()
		#尝试创建副本场景
		self.mirrorScene = cSceneMgr.CreateSingleMirrorScene(self.mirrorGId, SC.SceneId, SC.SceneName, SC.MapId, self.BeforeLeave)
		if not self.mirrorScene:
			#失败了
			return
		
		#尝试进入场景
		if not self.mirrorScene.JoinRole(role, goldCfg.posX, goldCfg.posY):
			return
		
		#特殊处理坐骑不可飞行
		role.SetTempFly(2)

		#强制进入状态
		Status.ForceInStatus(role, EnumInt1.ST_InMirror)
		
		#设置临时对象
		role.SetTempObj(EnumTempObj.MirrorScene, self)
		#进入场景后调用，同步显示NPC
		self.AfterJoinRole()
		
	def AfterJoinRole(self):
		MirrorBase.SingleMirrorBase.AfterJoinRole(self)
		SR = self.role
		SA = self.AfterClickFightNpc
		gold_cfg, fight_cfg, tp_cfg = GoldMirrorConfig.GetGoldNpc(self.goldCfg.stageID)
		self.gold_length = len(gold_cfg)
		self.role.SendObj(GoldMirror_GetGold, [self.goldCfg.stageID, self.total_money, self.gold_length])
		#小怪
		for cfg in fight_cfg:
			if not cfg:
				continue
			npcdata = (cfg.npctype, cfg.x, cfg.y, cfg.direction, cfg.rewardId, cfg.camp, cfg.fightType)
			#创建关卡战斗NPC
			GoldFightNPC(SR, npcdata, SA)
		#金币NPC	
		for cfg in gold_cfg:
			if not cfg:
				continue
			npcdata = (cfg.npctype, cfg.x, cfg.y, cfg.direction, cfg.goldtype, cfg.click)
			GoldMirrorNPC(SR, npcdata, self.AfterClickGold)
		#传送门
		for cfg in tp_cfg:
			if not cfg:
				continue
			npcdata = (cfg.npctype, cfg.x, cfg.y, cfg.direction)
			self.CreateDoor(npcdata)
			
	def CreateDoor(self, npcdata):
		GoldTpNPC(self.role, npcdata, self.AfterClickTP)
	
	def JumpDoor(self, role):
		#战斗失败,传送到进入起始点
		role.JumpPos(self.goldCfg.posX, self.goldCfg.posY)
		
	def AfterClickFightNpc(self, npc):
		#客户端点击怪物，触发战斗
		if not Status.CanInStatus(self.role, EnumInt1.ST_FightStatus):
			return
		FightEx.GoldMirrorPVE(self.role, npc.fightType, npc.fightId, self.AfterFight, (npc, npc.rewardId))
	
	def AfterFight(self, fightObj):
		if fightObj.result is None:
			print "GE_EXC, Purgatory fight error"
			return
		roles = fightObj.left_camp.roles
		if not roles:
			return
		role = list(roles)[0]
		if fightObj.result != 1:
			self.JumpDoor(role)
			return
		
		npc, _ = fightObj.after_fight_param
		npc.Destroy()
	
	def AfterClickGold(self, npc):
		#点击金币
		level = self.role.GetLevel()
		gold_dict = GoldMirrorConfig.LEVEL_MAP_GOLD.get(level)
		if not gold_dict:
			print "GE_EXC,can not find LevelMapGold by level=(%s)" % level
			return
		gold = gold_dict.get(npc.goldType)
		if not gold:
			return
		npc.Destroy()
		self.gold_length -= 1
		#日志
		with GoldMirrorGold:
			self.role.IncMoney(gold)
			self.role.Msg(2, 0, GlobalPrompt.WPG_GOLD_MSG % gold)
			self.total_money += gold			
			self.role.SendObj(GoldMirror_GetGold, [self.goldCfg.stageID, self.total_money, self.gold_length])

		nextLayerCfg = GoldMirrorConfig.GOLD_STAGE_DICT.get(self.goldCfg.stageID + 1)
		#最后层,点击大金币后，删除其他NPC，弹出接金币玩法
		if not nextLayerCfg and npc.goldType == MAX_GOLD:
			for othernpc in self.role.GetTempObj(EnumTempObj.PrivateNPCDict).values():
				othernpc.Destroy()
			
			if cDateTime.Days() != self.days:
				#跨天了, 直接离开
				self.EndMirror(self.role, None, None)
				return
			
			self.role.SendObjAndBack(GoldMirror_lastgold, None, CallBackSec, self.EndMirror, None)
			
			#弹出金币玩法
			self.role.SetDI1(EnumDayInt1.IsActGoldDrop, True)
			
	def EndMirror(self, role, argv, param):
		self.Destroy()
		
	def AfterClickTP(self, npc):
		#是否可以传送
		nextLayer = self.goldCfg.stageID + 1
		nextLayerCfg = GoldMirrorConfig.GOLD_STAGE_DICT.get(nextLayer)
		if not nextLayerCfg:
			self.Destroy()#最后层点门直接退出
			return
		npc.Destroy()		
		#删除其他NPC
		for othernpc in self.role.GetTempObj(EnumTempObj.PrivateNPCDict).values():
			othernpc.Destroy()
			
		#传送到下一层,传送后，C++会把这个副本销毁
		GoldMirror(self.role, nextLayerCfg, self.total_money, self.days)
		
	def BeforeLeave(self, scene, role):
		role.SetTempFly(0)
		MirrorBase.SingleMirrorBase.BeforeLeave(self, scene, role)		
#TPNPC
class GoldTpNPC(PrivateNPC.PrivateNPC):
	def __init__(self, role, npcData, clickFun = None):
		npcType, x, y, direction = npcData
		PrivateNPC.PrivateNPC.__init__(self, role, npcType, x, y, direction, clickFun)
	
#金币NPC
class GoldMirrorNPC(PrivateNPC.PrivateNPC):
	def __init__(self, role, npcData, clickFun = None, click = 200):
		npcType, x, y, direction, self.goldType, self.click = npcData
		PrivateNPC.PrivateNPC.__init__(self, role, npcType, x, y, direction, clickFun)
	
	def CanClick(self, role):
		#是否可以点击
		x, y = role.GetPos()
		dif_x = x - self.posX
		dif_y = y - self.posY
		dis = int(pow(dif_x * dif_x + dif_y * dif_y, 0.5))
		if dis <= self.click:
			return True
		return False

#关卡战斗NPC
class GoldFightNPC(PrivateNPC.PrivateNPC):
	def __init__(self, role, npcData, clickFun = None):
		npcType, x, y, direction, self.rewardId, self.fightId, self.fightType, = npcData
		PrivateNPC.PrivateNPC.__init__(self, role, npcType, x, y, direction, clickFun)		
		self.mirror = role.GetTempObj(EnumTempObj.MirrorScene)
		
	def Destroy(self):
		#销毁
		PrivateNPC.PrivateNPC.Destroy(self)
		
def SyncRoleOtherData(role, param):
	if not role.GetDI1(EnumDayInt1.IsActGoldDrop):
		return
	role.SendObjAndBack(GoldMirror_lastgold, None, CallBackSec, None, None)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and (not Environment.IsCross):
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	