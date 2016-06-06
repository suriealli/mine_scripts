#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.LostScene.LostSceneMirror")
#===============================================================================
# 注释
#===============================================================================
import random
import cRoleMgr
import cSceneMgr
import cDateTime
import cComplexServer
from Util import Random
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, EnumRoleStatus, GlobalPrompt
from Game.Role import Status
from Game.Role.Data import EnumTempObj, EnumInt32, EnumInt1, EnumDisperseInt32,\
	EnumDayInt1
from Game.LostScene import LostSceneConfig, LostSceneNPC
from Game.Scene import MutilMirrorBase, SceneMgr, MirrorIdAllot
import cNetMessage
from ComplexServer.Log import AutoLog

EnumTick = 1
EnumCard = 2

if "_HasLoad" not in dir():
	#{技能id:技能冷却时间}
	LostSceneSkillData = AutoMessage.AllotMessage("LostSceneSkillData", "迷失之境技能")
	#可翻牌索引集合
	LostSceneCardsPreview = AutoMessage.AllotMessage("LostSceneCardsPreview", "迷失之境翻牌预览")
	#[翻出牌的索引, 已翻出的所有牌索引字典]
	LostSceneCardsIndex = AutoMessage.AllotMessage("LostSceneCardsIndex", "迷失之境翻牌索引")
	#[第几轮, {躲藏者id:[躲藏者名字, 是否处于躲藏中]}]
	LostSceneHideData = AutoMessage.AllotMessage("LostSceneHideData", "迷失之境躲藏者数据")
	#迷失之境阶段枚举
	LostScenePhase = AutoMessage.AllotMessage("LostScenePhase", "迷失之境阶段枚举")
	#翻牌次数
	LostSceneTurnCnt = AutoMessage.AllotMessage("LostSceneTurnCnt", "迷失之境翻牌次数")
	#冒险点
	LostSceneScore = AutoMessage.AllotMessage("LostSceneScore", "迷失之境冒险点")
	
	LostSceneFind_Log = AutoLog.AutoTransaction("LostSceneFind_Log", "迷失之境抓捕日志")
	LostSceneTime_Log = AutoLog.AutoTransaction("LostSceneTime_Log", "迷失之境隐藏时间日志")
	LostSceneTimeEx_Log = AutoLog.AutoTransaction("LostSceneTimeEx_Log", "迷失之境隐藏时间额外日志")
	LostSceneCardReward_Log = AutoLog.AutoTransaction("LostSceneCardReward_Log", "迷失之境翻牌奖励日志")
	
class LostSceneMirror(MutilMirrorBase.MutilMirrorBase):
	def __init__(self, team):
		MutilMirrorBase.MutilMirrorBase.__init__(self)
		#队伍数据
		self.team = team
		
		#已抓到人数
		self.findCnt = 0
		#当前抓捕玩家id
		self.findRoleId = None
		
		#轮数
		self.roundCnt = 0
		#是否结束了
		self.isFinish = False
		
		#隐藏玩家数据{roleId:[roleName, isHide]}
		self.hideRoleDict = {}
		
#		已完成抓捕玩家角色id集合
#		self.finishRoleIdSet = set()

		#离开玩家id集合
		self.lostRoleIdSet = set()			
		
		#{奖励tick:{roleId:tickId}, 翻牌:{roleId:{1:set(所有牌索引), 2:翻牌次数, 3:{位置:牌索引}}}
		self.rewardDict = {EnumTick:{}, EnumCard:{}}
		
		self.roleDict = {}
		self.mountSpeedDict = {}
		self.mountIdDict = {}
		self.roleIdSet = set()
		self.scoreDict = {}
		
		for member in team.members:
			roleId = member.GetRoleID()
			#角色名字
			self.roleDict[roleId] = member.GetRoleName()
			#坐骑速度
			self.mountSpeedDict[roleId] = member.GetMountSpeed()
			#坐骑id
			self.mountIdDict[roleId] = member.GetDI32(EnumDisperseInt32.RightMountID)
			#所有玩家id集合
			self.roleIdSet.add(roleId)
			#冒险点
			self.scoreDict[roleId] = 0
		
		#抓捕者是否能够使用技能
		self.canUseSkill = False
		
		#所有玩家是否能够使用技能
		self.allCanUseSkill = False
		
		#获取场景配置
		self.sceneId = EnumGameConfig.LostSceneSceneID
		sceneConfig = SceneMgr.SceneConfig_Dict.get(self.sceneId)
		if not sceneConfig:
			print "GE_EXC, LostSceneMirror not this scene (%s)" % self.sceneId
			return
		
		#分配全局副本ID
		self.mirrorGId = MirrorIdAllot.AllotMirrorID()
		
		#尝试创建副本场景
		self.mirrorScene = cSceneMgr.CreateMultiMirrorScene(self.mirrorGId, self.sceneId, sceneConfig.SceneName, sceneConfig.MapId, self.BeforeLeave)
		if not self.mirrorScene:
			print "GE_EXC, CreateMultiMirrorScene error in LostSceneMirror" 
			return
		
		#尝试进入场景
		for member in team.members:
			if not self.mirrorScene.JoinRole(member, *EnumGameConfig.LostSceneJoinPos):
				print "GE_EXC, LostSceneMirror join role error"
				continue
		
		#技能组合
		self.findSkillIdList = LostSceneConfig.LostSceneSkillCombin_Dict.get(1)
		if not self.findSkillIdList:
			print 'GE_EXC, LostSceneMirror can not find findSkillIdList'
			return
		self.hideSkillIdList = LostSceneConfig.LostSceneSkillCombin_Dict.get(2)
		if not self.hideSkillIdList:
			print 'GE_EXC, LostSceneMirror can not find hideSkillIdList'
			return
		
		#强制进入状态
		Status.ForceInStatus_Roles(team.members, EnumInt1.ST_InTeamMirror)
		
		#进入副本场景后调用
		self.AfterJoinRoles(team.members)
		
	def AfterJoinRoles(self, roles):
		MutilMirrorBase.MutilMirrorBase.AfterJoinRoles(self, roles)
		
		#创建npc
		self.npcIndexSet = LostSceneConfig.LostScenePosRandom.RandomMany(EnumGameConfig.LostSceneNpcCnt)
		LLDG = LostSceneConfig.LostScenePosNpc_Dict.get
		for npcIndex in self.npcIndexSet:
			cfg = LLDG(npcIndex)
			if not cfg:
				print 'GE_EXC, LostSceneMirror can not find npcPosIndex %s in LostScenePosNpc_Dict' % npcIndex
				continue
			#不需要点击函数
			self.JoinNPC(LostSceneNPC.LostSceneMonsterNPC(self, (cfg.npcType, cfg.pos)))
		
		#轮数
		self.roundCnt += 1
		
		#抓铺者
		self.findRoleId = random.choice(list(self.roleIdSet))
		
		#生成躲藏者名字
		self.hideRoleDict = {}
		for roleId, roleName in self.roleDict.iteritems():
			if roleId == self.findRoleId:
				continue
			self.hideRoleDict[roleId] = [roleName, 0]
		
		#分配技能
		for roleId in self.roleIdSet:
			role = cRoleMgr.FindRoleByRoleID(roleId)
			if role:
				if (not role.GetTempObj(EnumTempObj.MirrorScene)) or (self.mirrorGId != role.GetTempObj(EnumTempObj.MirrorScene).mirrorGId):
					role = None
			
			if roleId == self.findRoleId:
				if not role:
					findRoleData = self.roleDict.get(roleId)
					if not findRoleData:
						print 'GE_EXC, LostSceneMirror NextFind can not find findRoleName'
						continue
					cComplexServer.RegTick(20, self.FindTips, findRoleData[0])
					continue
				else:
					#分配抓捕者技能
					self.AllocSkill(role, self.findSkillIdList, canMove=False)
			else:
				if not role:
					#隐藏者掉线在原地创建假人
					self.CreateFakeRole(EnumRoleStatus.LostScene_Apps_1, (EnumGameConfig.LostSceneJoinPos[0], EnumGameConfig.LostSceneJoinPos[1], 1), roleId)
				else:
					#分配躲藏者技能
					self.AllocSkill(role, self.hideSkillIdList)
			if role:
				role.SendObj(LostSceneScore, self.scoreDict.get(roleId, 0))
		
		
		self.allCanUseSkill = True
		
		#第一阶段 -- 准备
		for role in self.roles:
			role.SendObj(LostScenePhase, 1)
			role.SetMountSpeed(0)
			role.SetRightMountID(0)
			role.SetFly(0)
			role.SetDI1(EnumDayInt1.LostSceneIsIn, True)
		
		for role in self.roles:
			role.Msg(1, 0, GlobalPrompt.LostSceneTips_1 % self.roundCnt)
		
		#这轮结束tick
		self.nextFindTick = cComplexServer.RegTick(200, self.NextFindTick, None)
		
		cComplexServer.RegTick(20, self.NextPhase, None)
		
	def NextPhase(self, callargv, regparam):
		#第二阶段 -- 追捕阶段
		cNetMessage.PackPyMsg(LostScenePhase, 2)
		for role in self.roles:
			role.BroadMsg()
			
	def AllocSkill(self, role, skillIdList, canMove=True):
		#分配技能, 完成后同步客户端
		sec = cDateTime.Seconds()
		skillData = {skillId:sec for skillId in skillIdList}
		
		role.SetTempObj(EnumTempObj.LostScene, skillData)
		
		if not canMove:
			#不可以移动的就是抓捕者
			#禁止移动, 注册20s后解除禁止移动tick
			role.RegTick(20, self.ReleaseMove, (role, role.GetMoveSpeed()))
			role.SetMoveSpeed(0)
			role.SetAppStatus(0)
		else:
			role.RegTick(20, self.BeginRewardTick, None)
			#默认第一个外观
			role.SetAppStatus(EnumRoleStatus.LostScene_Apps_1)
		
		#轮数, 躲藏者名字字典
		role.SendObj(LostSceneHideData, (self.roundCnt, self.hideRoleDict))
		#技能
		role.SendObj(LostSceneSkillData, skillData)
		
	def BeginRewardTick(self, role, argv, regparam):
		#注册15s奖励tick
		if (not role.GetTempObj(EnumTempObj.MirrorScene)) or (self.mirrorGId != role.GetTempObj(EnumTempObj.MirrorScene).mirrorGId):
			#已经不在场景中了
			return
		
		self.rewardDict[EnumTick][role.GetRoleID()] = role.RegTick(15, self.Reward, None)
		
	def JoinNPC(self, npc):
		#加入一个NPC
		self.mirrorNPCDict[npc.gid] = npc
		#同步消息
		npc.SyncToRoles(self.roles)
		
	def ReleaseMove(self, role, callargv, regparam):
		#解除禁止移动
		role, moveSpeed = regparam
		#设置坐骑速度和人物速度都为0
		role.SetMoveSpeed(moveSpeed)
		
		self.canUseSkill = True
		
		findRoleName = role.GetRoleName()
		for role in self.roles:
			role.Msg(1, 0, GlobalPrompt.LostSceneTips_2 % findRoleName)
		
	def Reward(self, role, callargv, regparam):
		#15s躲藏奖励
		
		if (not role.GetTempObj(EnumTempObj.MirrorScene)) or (self.mirrorGId != role.GetTempObj(EnumTempObj.MirrorScene).mirrorGId):
			return
		
		with LostSceneTime_Log:
			role.IncI32(EnumInt32.LostSceneScore, EnumGameConfig.LostSceneScore_15sReward)
		
		roleId = role.GetRoleID()
		if roleId in self.scoreDict:
			self.scoreDict[roleId] += EnumGameConfig.LostSceneScore_15sReward
		role.SendObj(LostSceneScore, self.scoreDict.get(roleId, 0))
		
		#注册下一个
		self.rewardDict[EnumTick][roleId] = role.RegTick(15, self.Reward, None)
		
		role.Msg(2, 0, GlobalPrompt.LostSceneSocre_Tips % EnumGameConfig.LostSceneScore_15sReward)
		
	def FindOne(self, role, findRoleId, findRole):
		#找到一个
		with LostSceneFind_Log:
			hideRoleData = self.hideRoleDict.get(findRoleId)
			if not hideRoleData or hideRoleData[1]:
				#不是躲藏的玩家 or 已经被找到的玩家
				return False
			
			if findRole:
				#解除隐藏者变身
				findRole.SetAppStatus(EnumRoleStatus.LostScene_BeFind)
			
			#标记隐藏者被找到
			hideRoleData[1] = 1
			self.hideRoleDict[findRoleId] = hideRoleData
			
			#找到人数+1
			self.findCnt += 1
			
			#获得冒险点
			role.IncI32(EnumInt32.LostSceneScore, EnumGameConfig.LostSceneScore_findReward)
			
			roleId = role.GetRoleID()
			if roleId in self.scoreDict:
				self.scoreDict[roleId] += EnumGameConfig.LostSceneScore_findReward
			role.SendObj(LostSceneScore, self.scoreDict.get(roleId, 0))
			
			AutoLog.LogBase(role.GetRoleID(), AutoLog.eveLostSceneFind, 1)
			
			#取消掉被找到玩家的奖励tick
			tickId = self.rewardDict[EnumTick].get(findRoleId)
			
			if tickId:
				if findRole:
					findRole.UnregTick(tickId)
				del self.rewardDict[EnumTick][findRoleId]
			
			findRoleName = role.GetRoleName()
			for tRole in self.roles:
				tRole.SendObj(LostSceneHideData, (self.roundCnt, self.hideRoleDict))
				tRole.Msg(1, 0, GlobalPrompt.LostSceneTips_3 % (findRoleName, hideRoleData[0]))
			
			if self.findCnt == (len(self.roleIdSet) - 1):
				self.FindAll()
			
			return True
		
	def FindAll(self):
		#全部找到
		#取消下一轮tick
		cComplexServer.UnregTick(self.nextFindTick)
		self.nextFindTick = 0

		#再次确认一下是否所有奖励tick都被取消了
		if self.rewardDict[EnumTick]:
			print 'GE_EXC, LostSceneMirror FindAll rewardDict[EnumTick] is not empty'
			for roleId, tickId in self.rewardDict[EnumTick].iteritems():
				role = cRoleMgr.FindRoleByRoleID(roleId)
				if not role:
					continue
				role.UnregTick(tickId)
			self.rewardDict[EnumTick] = {}

		#翻牌预览
		self.CardPreview()
		
	def CardPreview(self):
		#翻牌预览
		
		#所有人都不可以使用技能了
		self.allCanUseSkill = False
		
		for role in self.roles:
			roleId = role.GetRoleID()
			
			#随机奖励索引
			tmpList = []
			tmpList.extend(random.sample(LostSceneConfig.LostSceneCardsRewardsGrade_Dict[1], 4))
			tmpList.extend(random.sample(LostSceneConfig.LostSceneCardsRewardsGrade_Dict[2], 1))
			
			#组合翻牌字典
			self.rewardDict[EnumCard][roleId] = {1:set(tmpList), 2:0, 3:{1:0, 2:0, 3:0, 4:0, 5:0}}
			
			#同步客户端翻牌字典
			role.SendObj(LostSceneCardsPreview, self.rewardDict[EnumCard][roleId][1])
			role.SendObj(LostSceneTurnCnt, 0)
			
			#奖励结算阶段
			role.SendObj(LostScenePhase, 3)
		if self.roles:
			#注册自动翻牌tick
			cComplexServer.RegTick(23, self.AutoTurnCard, None)
	
	def TurnCard(self, role, posIndex):
		#玩家手动翻牌
		if not self.rewardDict:
			return
		
		roleId = role.GetRoleID()
		
		#获取翻牌数据
		cardData = self.rewardDict[EnumCard].get(roleId)
		if not cardData:
			return
		
		if (posIndex not in cardData[3]) or cardData[3][posIndex]:
			#位置错误 or 这个位置已经翻过了
			return
		
		#最多三次翻牌
		if cardData[2] == 3:
			return

		#判断是否够钱
		cntCfg = LostSceneConfig.LostSceneTurnCardRMB_Dict.get(cardData[2]+1)
		if not cntCfg:
			return
		if role.GetKuaFuMoney() < cntCfg.needRMB:
			return
		
		#已经随机过的牌集合
		usedCardSet = set(cardData[3].values())
		
		#剩下的牌
		unusedCardSet = set(cardData[1]) - usedCardSet
		
		#重新组合概率
		randomObj = Random.RandomRate()
		LCRG = LostSceneConfig.LostSceneCardsRewards_Dict.get
		for cardIndex in unusedCardSet:
			cfg = LCRG(cardIndex)
			if not cfg:
				continue
			randomObj.AddRandomItem(cfg.rate, cardIndex)
		
		#随机
		cardIndex = randomObj.RandomOne()
		
		cfg = LCRG(cardIndex)
		if not cfg:
			print 'GE_EXC, LostSceneMirror TurnCard can not find reward index %s' % cardIndex
			return
		
		#翻牌数+1
		cardData[2] += 1
		#记录翻牌位置
		cardData[3][posIndex] = cardIndex
		
		self.rewardDict[EnumCard][roleId] = cardData
		
		with LostSceneCardReward_Log:
			role.DecKuaFuMoney(cntCfg.needRMB)
			
			tips = GlobalPrompt.Reward_Tips
			if cfg.rewardCoding:
				role.AddItem(*cfg.rewardCoding)
				tips += GlobalPrompt.Item_Tips % cfg.rewardCoding
			elif cfg.rewardSocre:
				role.IncI32(EnumInt32.LostSceneScore, cfg.rewardSocre)
				tips += GlobalPrompt.LostSceneSocre_Tips % cfg.rewardSocre
			else:
				return
			
		role.SendObj(LostSceneCardsIndex, (posIndex, cardData[3]))
		
		role.SendObj(LostSceneTurnCnt, cardData[2])
		
		role.Msg(2, 0, tips)
		
	def AutoTurnCard(self, callargv, regparam):
		#15s后自动翻牌并开始下一轮
		#计算还没有翻牌的玩家
		noTurnRoleIdSet = set()
		for roleId, cardData in self.rewardDict[EnumCard].iteritems():
			if len(set(cardData[3].values())) == 1:
				noTurnRoleIdSet.add(roleId)
		
		#还没有翻牌玩家集合 - 已经掉线玩家集合
		noTurnRoleIdSet = noTurnRoleIdSet - self.lostRoleIdSet
		
		if not noTurnRoleIdSet:
			#都翻过了, 2s后开始下一轮
			self.rewardDict = {EnumTick:{}, EnumCard:{}}
			
			cComplexServer.RegTick(2, self.Phase_4, None)
			return
		
		LLDG = LostSceneConfig.LostSceneCardsRewards_Dict.get
		with LostSceneCardReward_Log:
			for roleId in noTurnRoleIdSet:
				role = cRoleMgr.FindRoleByRoleID(roleId)
				if not role:
					continue
				if not role.GetTempObj(EnumTempObj.MirrorScene):
					continue
				if self.mirrorGId != role.GetTempObj(EnumTempObj.MirrorScene).mirrorGId:
					continue
				
				randomObj = Random.RandomRate()
				for cardIndex in self.rewardDict[EnumCard][roleId][1]:
					cfg = LLDG(cardIndex)
					if not cfg:
						continue
					randomObj.AddRandomItem(cfg.rate, cardIndex)
				
				#位置
				tmpDict = {1:0, 2:0, 3:0, 4:0, 5:0}
				pos = random.randint(1, 5)
				rewardIndex = randomObj.RandomOne()
				tmpDict[pos] = rewardIndex
				
				cfg = LLDG(rewardIndex)
				if not cfg:
					print 'GE_EXC, LostSceneMirror TurnCard can not find reward index %s' % rewardIndex
					return
				
				tips = GlobalPrompt.Reward_Tips
				if cfg.rewardCoding:
					role.AddItem(*cfg.rewardCoding)
					tips += GlobalPrompt.Item_Tips % cfg.rewardCoding
				elif cfg.rewardSocre:
					role.IncI32(EnumInt32.LostSceneScore, cfg.rewardSocre)
					tips += GlobalPrompt.LostSceneSocre_Tips % cfg.rewardSocre
				else:
					return
				
				role.SendObj(LostSceneCardsIndex, (pos, tmpDict))
				role.SendObj(LostSceneTurnCnt, cardData[2])
				role.Msg(2, 0, tips)
		
		self.rewardDict = {EnumTick:{}, EnumCard:{}}
		
		cComplexServer.RegTick(2, self.Phase_4, None)
		
	def Phase_4(self, callargv, regparam):
		for role in self.roles:
			#奖励结算完阶段
			role.SendObj(LostScenePhase, 4)
		
		#5s后开始下一轮
		cComplexServer.RegTick(5, self.NextFind, None)
		
	def NextFindTick(self, callargv, regparam):
		#tick触发的下一轮
		self.nextFindTick = 0
		
		#如果全部掉线了, 结束
		if len(self.lostRoleIdSet) == len(self.roleIdSet):
			self.FinishFind()
			return
		
		#发放额外奖励
		self.RewardEx()
		
		#翻牌预览
		self.CardPreview()
		
	def RewardEx(self):
		#发放额外奖励
		CFR = cRoleMgr.FindRoleByRoleID
		
		with LostSceneTimeEx_Log:
			for roleId, tickId in self.rewardDict[EnumTick].iteritems():
				tRole = CFR(roleId)
				if not tRole:
					continue
				tRole.UnregTick(tickId)
				
				if not tRole.GetTempObj(EnumTempObj.MirrorScene):
					continue
				if self.mirrorGId != tRole.GetTempObj(EnumTempObj.MirrorScene).mirrorGId:
					continue
				tRole.IncI32(EnumInt32.LostSceneScore, EnumGameConfig.LostSceneScore_exReward)
				
				if roleId in self.scoreDict:
					self.scoreDict[roleId] += EnumGameConfig.LostSceneScore_exReward
				tRole.SendObj(LostSceneScore, self.scoreDict.get(roleId, 0))
				
				tRole.Msg(2, 0, GlobalPrompt.LostSceneTips_5 % EnumGameConfig.LostSceneScore_exReward)
			self.rewardDict[EnumTick] = {}
	
	def NextFind(self, callargv=None, regparam=None):
		#下一轮
		self.rewardDict = {EnumTick:{}, EnumCard:{}}
		
		self.findCnt = 0
		
		#处理没有轮过玩家
#		self.finishRoleIdSet.add(self.findRoleId)
#		
#		noFinishRoleIDSet = self.roleIdSet - self.finishRoleIdSet
#		if not noFinishRoleIDSet:
#			#全部轮过了
#			self.FinishFind()
#			return
		
		if self.roundCnt == 4:
			#五个人, 四轮
			self.FinishFind()
			return
		
		#清理npc
		for npc in self.mirrorNPCDict.values():
			npc.Destroy()
		
		#创建新npc
		self.npcIndexSet = LostSceneConfig.LostScenePosRandom.RandomMany(EnumGameConfig.LostSceneNpcCnt)
		LLDG = LostSceneConfig.LostScenePosNpc_Dict.get
		for npcIndex in self.npcIndexSet:
			cfg = LLDG(npcIndex)
			if not cfg:
				print 'GE_EXC, LostSceneMirror can not find npcPosIndex %s in LostScenePosNpc_Dict' % npcIndex
				continue
			#不需要点击函数
			self.JoinNPC(LostSceneNPC.LostSceneMonsterNPC(self, (cfg.npcType, cfg.pos)))
		
		#下一个抓捕者
		self.findRoleId = random.choice(list(self.roleIdSet))
		
		#轮数+1
		self.roundCnt += 1
		
		#生成躲藏者名字
		self.hideRoleDict = {}
		self.scoreDict = {}
		for roleId, roleName in self.roleDict.iteritems():
			self.scoreDict[roleId] = 0
			if roleId == self.findRoleId:
				continue
			self.hideRoleDict[roleId] = [roleName, 0]
		
		#分配技能
		for roleId in self.roleIdSet:
			role = cRoleMgr.FindRoleByRoleID(roleId)
			if role:
				if (not role.GetTempObj(EnumTempObj.MirrorScene) or (self.mirrorGId != role.GetTempObj(EnumTempObj.MirrorScene).mirrorGId)):
					#不在副本内了 或者 在另外的副本中了
					role = None
			
			#所有人回到起点
			if role:
				role.JumpPos(*EnumGameConfig.LostSceneJoinPos)
			
			if roleId == self.findRoleId:
				if not role:
					findRoleData = self.roleDict.get(roleId)
					if not findRoleData:
						print 'GE_EXC, LostSceneMirror NextFind can not find findRoleName'
						continue
					cComplexServer.RegTick(20, self.FindTips, findRoleData[0])
					continue
				else:
					self.AllocSkill(role, self.findSkillIdList, canMove=False)
			else:
				if not role:
					self.CreateFakeRole(LostSceneConfig.LostSceneChange_Dict.get(EnumRoleStatus.LostScene_Apps_1, 0), (EnumGameConfig.LostSceneJoinPos[0], EnumGameConfig.LostSceneJoinPos[1], 1), roleId)
				else:
					#躲藏人
					self.AllocSkill(role, self.hideSkillIdList)
			if role:
				role.SendObj(LostSceneScore, self.scoreDict.get(roleId, 0))
		
		self.canUseSkill = False
		
		self.allCanUseSkill = True
		
		#第一阶段 -- 准备
		cNetMessage.PackPyMsg(LostScenePhase, 1)
		for role in self.roles:
			role.BroadMsg()
		for role in self.roles:
			role.Msg(1, 0, GlobalPrompt.LostSceneTips_1 % self.roundCnt)
		
		self.nextFindTick = cComplexServer.RegTick(200, self.NextFindTick, None)
		
		cComplexServer.RegTick(20, self.NextPhase, None)
		
	def FindTips(self, callargv, regparam):
		for role in self.roles:
			role.Msg(1, 0, GlobalPrompt.LostSceneTips_2 % regparam)
		
	def CreateFakeRole(self, npcType, npcPos, roleId):
		self.JoinNPC(LostSceneNPC.LostSceneMonsterNPC(self, (npcType, npcPos), roleId))
	
	def FinishFind(self):
		#结束
		self.isFinish = True
		
		self.ClearAllNPC()
		
		for role in list(self.roles):
			self.BackToCity(role)
	
	def BackToCity(self, role):
		from Game.CrossTeamTower import CrossTTMgr
		posx, posy = CrossTTMgr.GetTPPox()
		role.Revive(EnumGameConfig.CTT_SCENE_ID, posx, posy)
		
	def BeforeLeave(self, scene, role):
		#离开副本前调用
		MutilMirrorBase.MutilMirrorBase.BeforeLeave(self, role)
		#离开关卡调用， 一般用于角色掉线，或者没用通过回城达到离开关卡处理
		#请不要在此函数内调用scene.Destroy()
		#退出多人副本状态
		Status.Outstatus(role, EnumInt1.ST_InTeamMirror)
		
		mirrorScene = role.GetTempObj(EnumTempObj.MirrorScene)
		if not mirrorScene:
			return
		
		if (not self.isFinish) and role.GetRoleID() != self.findRoleId:
			#如果不是追捕者的话创建假人npc
			x, y = role.GetPos()
			self.CreateFakeRole(LostSceneConfig.LostSceneChange_Dict.get(EnumRoleStatus.LostScene_Apps_1, 0), (x, y, 1), role.GetRoleID())
		
		#取消奖励tick
		roleId = role.GetRoleID()
		tickId = self.rewardDict[EnumTick].get(roleId)
		if tickId:
			role.UnregTick(tickId)
			del self.rewardDict[EnumTick][roleId]
		self.lostRoleIdSet.add(roleId)
		
		#清理临时缓存数据
		role.SetTempObj(EnumTempObj.MirrorScene, None)
		role.SetTempObj(EnumTempObj.LostScene, None)
		
		role.SetMountSpeed(self.mountSpeedDict.get(roleId, 0))
		role.SetRightMountID(self.mountIdDict.get(roleId, 0))
		role.SetFly(0)
		
		#处理队伍数据
		team = role.GetTeam()
		if not team:
			return
		team.Quit(role)
		
	def Destroy(self):
		#销毁多人副本(注意多人限时副本的处理需要非常小心,一般把权限交给C++处理比较好)
		if not self.mirrorScene:
			return
		if self.mirrorScene.IsDestroy():
			return
		
		if self.nextFindTick:
			cComplexServer.UnregTick(self.nextFindTick)
		
		#调用C++函数，踢掉副本内玩家,会触发玩家退出场景调用函数
		self.mirrorScene.Destroy()
		self.mirrorScene = None
		self.mirrorGId = 0
