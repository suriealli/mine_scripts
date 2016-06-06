#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ClashOfTitans.ClashOfTitans")
#===============================================================================
# 诸神之战
#===============================================================================
import copy
import random
import cRoleMgr
import cDateTime
import cSceneMgr
import cNetMessage
import Environment
import cComplexServer
from Game.Role import Rank
from Game.Scene import PublicScene
from Game.Role import Status, Event
from ComplexServer.Time import Cron
from Game.Fight import Middle, Fight
from ComplexServer.Log import AutoLog
from Common.Message import AutoMessage
from Game.Activity.Award import AwardMgr
from Game.NPC import EnumNPCData, NPCServerFun
from Game.Role.Data import  EnumInt1, EnumCD, EnumTempObj
from Game.Activity.ClashOfTitans import ClashOfTitansConfig
from Common.Other import GlobalPrompt, EnumAward, EnumRoleStatus, EnumFightStatistics, \
	EnumGameConfig
from Game.Activity.RewardBuff import RewardBuff


if "_HasLoad" not in dir():
	TheWarMgr = None				#战斗管理器对象
	CanJoin = False					#是否可以进入诸神之战场景
	IsStart = False					#战斗是否开始了
	OneMinute = 60					#一分钟
	TheDistance = 1000000			#挑战距离的平方
	
	#随机复活区域x轴取值范围和y轴取值范围
	Area1 = ((1014, 2280), (833, 1665))
	Area2 = ((2599, 3754), (741, 1338))
	Area3 = ((3496, 5004), (895, 1742))
	Area4 = ((3405, 5048), (2040, 2923))
	Area5 = ((972, 2310), (2164, 3000))
	Aera = [Area1, Area2, Area3, Area4, Area5]

	#英魂可以替换的属性种类 ：
	#主角
	SoulRolePropertyList = [Middle.HelpStationProperty, Middle.MaxHP, Middle.Morale, Middle.Speed,
							Middle.AttackP, Middle.AttackM, Middle.DefenceP, Middle.DefenceM,
							Middle.Crit, Middle.CritPress, Middle.AntiBroken, Middle.NotBroken,
							Middle.Parry, Middle.Puncture, Middle.DamageUpgrade, Middle.DamageReduce,
							]

	#英雄
	SoulHeroPropertyList = [Middle.MaxHP, Middle.Morale, Middle.Speed, Middle.AttackP,
							Middle.AttackM, Middle.DefenceP, Middle.DefenceM, Middle.Crit,
							Middle.CritPress, Middle.AntiBroken, Middle.NotBroken, Middle.Parry,
							Middle.Puncture, Middle.DamageUpgrade, Middle.DamageReduce,
							]
	
	#死亡原因枚举
	DieByTick = 1		#死亡倒计时至0
	DieByKilled = 2		#战斗失败被杀死
	DieByOutScene = 3	#离开场景死亡
	DieByTimeOut = 4		#战斗播放超时死亡
	
	#消息
	SyncClashOfTitansPersonnalData = AutoMessage.AllotMessage("SyncClashOfTitansPersonnalData", "同步诸神之战玩家个人数据")
	SyncClashOfTitansKillRank = AutoMessage.AllotMessage("SyncClashOfTitansKillRank", "同步诸神之战连杀榜数据")
	SyncClashOfTitansAliveRank = AutoMessage.AllotMessage("SyncClashOfTitansAliveRank", "同步诸神之战生存榜数据")
	SyncClashOfTitansScoreRank = AutoMessage.AllotMessage("SyncClashOfTitansScoreRank", "同步诸神之战玩家积分榜数据")
	SyncClashOfTitansFinallyData = AutoMessage.AllotMessage("SyncClashOfTitansFinallyData", "同步诸神之战最终数据")
	SyncClashOfTitansDeathSeconds = AutoMessage.AllotMessage("SyncClashOfTitansDeathSeconds", "同步诸神之战死亡时间戳")
	SyncClashOfTitansRoleCnt = AutoMessage.AllotMessage("SyncClashOfTitansRoleCnt", "同步诸神之战当前活动剩余人数")
	SyncClashOfTitansFightHistory = AutoMessage.AllotMessage("SyncClashOfTitansFightHistory", "同步诸神之战战斗历史")
	
	#日志
	TraClashOfTitansPersonScoreRank = AutoLog.AutoTransaction("TraClashOfTitansPersonScoreRank", "诸神之战个人积分排行榜结算")
	TraClashOfTitansPersonScoreRankAward = AutoLog.AutoTransaction("TraClashOfTitansPersonScoreRankAward", "诸神之战个人积分排行奖励")		
	TraClashOfTitansPersonScoreAward = AutoLog.AutoTransaction("TraClashOfTitansPersonScoreAward", "诸神之战个人积分奖励")	
	TraClashOfTitansUnionScoreAward = AutoLog.AutoTransaction("TraClashOfTitansUnionScoreAward", "诸神之战公会积分奖励")		
	TraClashOfTitansTitanAward = AutoLog.AutoTransaction("TraClashOfTitansTitanAward", "诸神之战战神奖励")		
	TraClashOfTitansTitanUnionAward = AutoLog.AutoTransaction("TraClashOfTitansTitanUnionAward", "诸神之战战神公会奖励")	
	TraClashOfTitansTitanFightTimeOut = AutoLog.AutoTransaction("TraClashOfTitansTitanFightTimeOut", "诸神之战战斗播放超时")
	TraClashOfTitansTitanRoleReborn = AutoLog.AutoTransaction("TraClashOfTitansTitanRoleReborn", "诸神之战角色死亡复活")
	TraClashOfTitansTitanWinGetScore = AutoLog.AutoTransaction("TraClashOfTitansTitanWinGetScore", "诸神之战胜利获取积分")
	TraClashOfTitansTitanLoseGetScore = AutoLog.AutoTransaction("TraClashOfTitansTitanLoseGetScore", "诸神之战失败获取积分")
	TraClashOfTitansTitanSystemScore = AutoLog.AutoTransaction("TraClashOfTitansTitanSystemScore", "诸神之战系统发放积分")
	TraClashOfTitansTitanOutScene = AutoLog.AutoTransaction("TraClashOfTitansTitanOutScene", "诸神之战角色离开场景")
	
class personalScoreRank(Rank.SmallRoleRank):
	'''
	个人积分排行榜
	'''
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 10						#最大排行榜 10个
	dead_time = (2038, 1, 1)
	needSync = False						#这个排行榜需要同步客户端的,
	name = "RankClashOfTitansPersonalScore"
	
	def IsLess(self, v1, v2):
		#[积分，已复活次数，战力，姓名，公会名]
		return (v1[0], -v1[1], v1[2]) < (v2[0], -v2[1], v2[2])
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		self.changeFlag = True
	
	def HasData(self, role_id, value):
		# 排行榜未满
		if self.max_rank_size > len(self.data):
			# 入榜
			self.data[role_id] = value
			self.changeFlag = True
			# 有可能导致排行榜满了
			if self.max_rank_size == len(self.data):
				self.BuildMinValue()
				
		# 排行榜已满，并且排行值大于最小值
		elif self.IsLess(self.min_value, value):
			# 入榜
			self.data[role_id] = value
			self.changeFlag = True
			# 有可能导致排行榜爆了
			if self.max_rank_size < len(self.data):
				del self.data[self.min_role_id]
				self.BuildMinValue()
			elif role_id == self.min_role_id:
				#自己本身就是最小值，需要重新构建一个
				self.BuildMinValue()


class theRank(Rank.LittleRank):
	'''
	连杀榜
	'''
	def IsLess(self, v1, v2):
		return v1[0] < v2[0]
	
	def DelData(self, roleID):
		if not roleID in self.data:
			return 
		del self.data[roleID]
		if roleID == self.min_role_id:
			self.BuildMinValue()


class WarMgr(object):
	'''
	战争管理器
	'''
	def __init__(self):
		self.sceneID = EnumGameConfig.ClashOfTitansSceneID									#场景id
		self.scene = cSceneMgr.SearchPublicScene(EnumGameConfig.ClashOfTitansSceneID)		#场景
		self.warRoleDict = {}									#roleID - ->warRole
		self.warUnionDict = {}									#参战公会ID字典{unionID-->set([roleID])}
		self.roleIDInScene = set()								#在诸神之战场景中的角色id
		self.unionScoreDict = {}								#公会积分字典
		self.wantRank = theRank(10)								#连杀榜，这个可以做到实时更新		
		self.rebornRank = []									#生存榜，这个每分钟更新一次
		
	def WarBegin(self):
		'''
		战斗开始
		'''
		global IsStart
		IsStart = True
		
		#如果场景内的角色数量不大于一个的话，活动直接结束，其中如果没人的话，算非正常结束
		if len(self.roleIDInScene) < 1:
			#非正常结束
			self.WarEnd(unNormal=True)
			return
		elif len(self.roleIDInScene) == 1:
			self.WarEnd()
			
		#战斗开始，所有角色注册死亡tick
		for warRole in self.warRoleDict.itervalues():
			warRole.RegDeathTick()
			
		#每60秒给所有的在场景中的角色加60分
		cComplexServer.RegTick(OneMinute, self.AddPointPerMinite, None)
		
		#每60秒更新并同步生存榜数据
		cComplexServer.RegTick(OneMinute, self.UpDateRebornRank, None)
		
		#每60秒同步连杀榜数据
		cComplexServer.RegTick(30, self.SyncKillRankPerMiniute, None)

		#给所有的角色设置等死状态
		for role in self.scene.GetAllRole():
			warRole = self.GetWarRole(role.GetRoleID())
			role.SendObj(SyncClashOfTitansDeathSeconds, warRole.deathSeconds)
			role.SetAppStatus(EnumRoleStatus.CT_Dying)
			
	def WarEnd(self, unNormal=False):
		'''
		战斗结束
		'''
		global IsStart
		if IsStart is False:
			return
		IsStart = False
		#如果是非正常结束的话那就算了
		if unNormal is True:
			return
		
		tips = GlobalPrompt.ClashOfTitansEndWithOutTitan % len(self.roleIDInScene)
		#诸神之战战神的角色ID	
		if len(self.roleIDInScene) == 1:
			self.titanID = list(self.roleIDInScene)[0]
			titanWarRole = self.GetWarRole(self.titanID)
			tips = GlobalPrompt.ClashOfTitansTitanStandOut % titanWarRole.name
		
		#最终数据记录日志
		with TraClashOfTitansPersonScoreRank:
			AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveClashOfTitansRoleScoreRankFinal, COTR.data)
		
		
		for theRole in self.scene.GetAllRole():
			theRole.SetAppStatus(0)
		
		self.DoReward()
		
		cNetMessage.PackPyMsg(SyncClashOfTitansRoleCnt, len(self.roleIDInScene))
		cNetMessage.PackPyMsg(SyncClashOfTitansFinallyData, COTR.data)
		self.scene.BroadMsg()
		
		cRoleMgr.Msg(1, 0, tips)
		
	
	def DoReward(self):
		#活动还在进行中，不发奖
		if IsStart is True:
			return
		
		#个人积分排行奖励
		with TraClashOfTitansPersonScoreRankAward:
			PersonalRankReward(COTR.data)
		#个人积分奖励
		with TraClashOfTitansPersonScoreAward:
			PersonalScoreReward(self.warRoleDict)
		
		#公会积分奖励
		with TraClashOfTitansUnionScoreAward:
			SU = self.UpDateUnionScoreDict
			SUG = self.unionScoreDict.get
			for unionID, roleIDList in self.warUnionDict.iteritems():
				#发奖前先更新一下公会积分
				SU(unionID)
				score = SUG(unionID, 0)
				if not roleIDList:
					continue
				UnionScoreReward(roleIDList, self.warRoleDict, score)
		
		if not hasattr(self, "titanID"):
			return
		#战神奖励
		titanWarRole = self.warRoleDict.get(self.titanID)
		if not titanWarRole:
			return
		with TraClashOfTitansTitanAward:
			TitanPersonalReward(titanWarRole)
		
		roleIDSet = self.warUnionDict.get(titanWarRole.unionID)
		if not roleIDSet:
			return
		#战神公会奖励
		with TraClashOfTitansTitanUnionAward:
			TitanUnionReaward(roleIDSet, self.warRoleDict, self.titanID, titanWarRole.name)
		
		
	def GetWarRole(self, roleID):
		return self.warRoleDict.get(roleID, None)


	def JoinBattle(self, role):
		'''
		角色参战(角色进入诸神之战场景)
		'''
		roleID = role.GetRoleID()
		unionID = role.GetUnionID()
		#已经加入了诸神之战，又再次进入的，需要更新血量和战斗数据
		if self.IsWarRole(role):
			warRole = self.GetWarRole(roleID)
			warRole.role = role
			warRole.UpDateFightData()
			return
		
		self.warUnionDict.setdefault(unionID, set()).add(roleID)
		self.warRoleDict[roleID] = WarRole(role)
		
	
	def InScene(self, role):
		'''
		进入诸神之战场景
		'''
		if not self.IsWarRole(role):
			return
		roleID = role.GetRoleID()
		self.roleIDInScene.add(roleID)
		
		cNetMessage.PackPyMsg(SyncClashOfTitansRoleCnt, len(self.roleIDInScene))
		self.scene.BroadMsg()
	
	
	def LeaveScene(self, role):
		'''
		离开诸神之战场景
		'''
		if not self.IsWarRole(role):
			return 
		roleID = role.GetRoleID()
		self.roleIDInScene.discard(roleID)
		
		if len(self.roleIDInScene) <= 1:
			self.WarEnd()
			
		cNetMessage.PackPyMsg(SyncClashOfTitansRoleCnt, len(self.roleIDInScene))
		self.scene.BroadMsg()
		
		if IsStart is False:
			return
		warRole = self.GetWarRole(roleID)
		with TraClashOfTitansTitanOutScene:
			AutoLog.LogBase(warRole.roleID, AutoLog.eveClashOfTitansOutScene, None)
			
		warRole.UnregDeathTick()
		warRole.RegDeathTick()
		warRole.Die(reason=DieByOutScene)


	def AddPointPerMinite(self, callargv=None, params=None):
		'''
		所有在场景内的角色每分钟积分需要增加60
		'''
		if IsStart is False:
			return
		#这里先注册tick防止被打断后没有后续tick
		cComplexServer.RegTick(OneMinute, self.AddPointPerMinite, None)
		
		#对于在场景中的所有角色，每分钟积分增加60
		SWG = self.warRoleDict.get
		for roleID in self.roleIDInScene:
			warRole = SWG(roleID)
			if warRole is None:
				continue
			warRole.IncScore(EnumGameConfig.ClashOfTitansAddScorePerMinute, None)
			role = self.scene.SearchRole(roleID)
			if not role:
				continue
			if role.IsKick():
				continue
			SyncRoleData(role)
			role.Msg(2, 0, GlobalPrompt.ClashOfTitansPerMinuteScore % EnumGameConfig.ClashOfTitansAddScorePerMinute)


	def IsWarRole(self, role):
		'''
		是否参战角色
		'''
		return role.GetRoleID() in self.warRoleDict
	
	
	def UpDateUnionScoreDict(self, unionID):
		'''
		更新公会积分字典
		'''
		SWG = self.warRoleDict.get
		unionScoreDict = self.unionScoreDict
		roleIDSet = self.warUnionDict.get(unionID)
		if not roleIDSet:
			return
		
		score = 0
		for roleID in roleIDSet:
			warRole = SWG(roleID)
			if not warRole:
				continue
			score += warRole.GetScore()
		unionScoreDict[unionID] = score

		
	def UpdateWantDict(self, roleID):
		'''
		 尝试进入连杀榜,如果已经在里面但是不满足条件的话就出来
		'''
		if IsStart is False:
			return
		
		warRole = self.GetWarRole(roleID)
		if warRole is None:
			return
		if warRole.killCnt < 3:
			self.wantRank.DelData(roleID)
		else:
			self.wantRank.HasData(roleID, [warRole.killCnt , warRole.name])
		

	def UpDateRebornRank(self, callargv=None, params=None):
		'''
		更新生存榜
		'''
		if IsStart is False:
			return
		cComplexServer.RegTick(OneMinute, self.UpDateRebornRank, None)
		warRoleList = self.warRoleDict.values()
		warRoleList.sort(key=lambda x:(-x.rebornCnt, x.zdl), reverse=True)
		warRoleRebornList = warRoleList[:10]
		rebornRank = self.rebornRank = [(warRole.roleID, warRole.name, warRole.rebornCnt) for warRole in warRoleRebornList]
		#每分钟更新生存榜之后立即广播出去
		cNetMessage.PackPyMsg(SyncClashOfTitansAliveRank, rebornRank)
		self.scene.BroadMsg()
	
	def SyncKillRankPerMiniute(self, callargv, params):
		'''
		'''
		if IsStart is False:
			return
		cComplexServer.RegTick(OneMinute, self.SyncKillRankPerMiniute, None)
		cNetMessage.PackPyMsg(SyncClashOfTitansKillRank, self.wantRank.data)
		self.scene.BroadMsg()


	def GetRoleData(self, role):
		roleID = role.GetRoleID()
		warRole = self.GetWarRole(roleID)
		if not warRole:
			return
		unionID = role.GetUnionID()
		rebornCnt = warRole.rebornCnt
		personalScore = warRole.GetScore()
		self.UpDateUnionScoreDict(unionID)
		unionScore = self.unionScoreDict.get(unionID, 0)
		killCnt = warRole.killCnt
		hp_show = warRole.hp_show
		#返回角色积分，公会积分，已复活次数 ，连杀数，血量
		return personalScore, unionScore, rebornCnt, killCnt, hp_show


	def GetRankData(self):
		return self.wantRank.data, self.rebornRank


class WarRole(object):
	'''
	仅仅是用来保存角色数据
	'''
	def __init__(self, role):
		self.role = role
		self.roleID = role.GetRoleID()				#角色id
		self.level = role.GetLevel()				#角色等级
		self.name = role.GetRoleName()				#角色名字
		self.unionName = role.GetUnionObj().name 	#这里确定可以进入的角色肯定有公会
		self.unionID = role.GetUnionID()			#角色公会ID
		self.zdl = role.GetZDL()					#战力
		self.deathTickID = 0						#死亡tickID
		self.fightTimeOutTickID = 0					#战斗超时tick
		self.rebornCnt = 0							#复活次数
		self.hp = 0									#角色血量
		self.isDeadOut = False						#角色是否死透（不能再复活了）
		self.score = 0								#积分
		self.killCnt = 0							#连杀次数
		self.fightData = Middle.GetRoleData(role, use_property_X=True)
		self.soulFightData = None					#英魂战斗数据
		self.realFightData = None					#真实的战斗数据
		self.soulName = None						#英魂的名字
		self.bind_hp = {}							#角色血量字典
		self.deathSeconds = 0						#角色死亡时间戳
		self.protectSeconds = 0						#角色的保护时间戳，早于该时间不能被攻击
		
		maxHP = GetRoleMaxHp(role)
		self.hp_show = [maxHP, maxHP]				#用于显示血条的角色血量[最大血量, 当前血量]
		self.fightHistory = []						#战斗历史[(胜利失败，对战角色名，获得积分)]
	
	
	def UpDateFightData(self):
		'''
		角色退出场景重新进入的时候需要这么做，更新角色的战斗数据，最大血量
		'''
		if self.role.IsKick():
			return
		self.fightData = Middle.GetRoleData(self.role, use_property_X=True)
		self.level = self.role.GetLevel()
		
		maxHP = GetRoleMaxHp(self.role)
		self.hp_show[0] = maxHP
		
		self._UpdateFightData()
	
	def History(self, result, fightName, score):
		self.fightHistory.append((result, fightName, score))
		history = self.fightHistory
		if len(history) > 5:
			self.fightHistory = history[-5:]
		

	def GetCurrentHP(self):
		return self.bind_hp.get("total_hp", 0)


	def IncKillCnt(self, value):
		'''
		增加连杀次数
		'''
		if IsStart is False:
			return
		
		global TheWarMgr
		if TheWarMgr is None:
			return
		
		self.killCnt += value
		TheWarMgr.UpdateWantDict(self.roleID)
	
		scene = TheWarMgr.scene
		
		#发连杀公告
		if self.killCnt % 5 == 0:
			if self.killCnt >= 30:
				tips = GlobalPrompt.ClashOfTitansKillTips4 % (self.killCnt, self.name)
			elif self.killCnt > 0:
				tips = GetRandomTips() % (self.name, self.killCnt)
			scene.Msg(1, 0, tips)

	
	def ResetKillCnt(self):
		'''
		重置连杀次数 
		'''
		if IsStart is False:
			return
	
		global TheWarMgr
		if TheWarMgr is None:
			return
		
		self.killCnt = 0
		TheWarMgr.UpdateWantDict(self.roleID)
		

	def RegDeathTick(self, needProtect=False):
		'''
		注册死亡tick
		'''
		#不能同时注册好几个死亡tick
		if self.deathTickID != 0:
			return
		self.deathTickID = cComplexServer.RegTick(OneMinute, self.TryDie, None)
		self.deathSeconds = cDateTime.Seconds() + OneMinute
		if needProtect:
			self.protectSeconds = cDateTime.Seconds() + EnumGameConfig.ClashOfTitansProtectSeconds


	def UnregDeathTick(self):
		'''
		反注册死亡tick
		'''
		if self.deathTickID:
			cComplexServer.UnregTick(self.deathTickID)
			self.deathTickID = 0
			self.deathSeconds = 0
			self.protectSeconds = 0


	def TryDie(self, callargv=None, param=None):
		'''
		战斗角色死亡
		'''
		self.UnregDeathTick()
		if IsStart is False:
			return
		
		if self.isDeadOut is True:
			return
		
		self.RegDeathTick(needProtect=True)
		self.Die()


	def Die(self, reason=DieByTick, killer=''):
		'''
		真正的死亡
		'''
		#连杀次数大于三的角色死亡要创建英魂npc
		if IsStart is False:
			return
		
		oldKillCnt = self.killCnt
		#死了要重置连杀次数
		self.ResetKillCnt()
		self.TryReborn(reason)
		
		if reason == DieByTick:
			if not self.role.IsKick():
				self.role.Msg(2, 0, GlobalPrompt.ClashOfTitansRoleDieWithoutFighting)
				
		elif reason == DieByKilled:
			if oldKillCnt >= 3:
				soulPos = self.CreateSoulNPC()
				if soulPos:
					X, Y = soulPos
					TheWarMgr.scene.Msg(1, 0, GlobalPrompt.ClashOfTitansBeKilledTips % (killer, self.name, oldKillCnt, X, Y, X, Y, self.name, self.name))
		else:
			pass
		
		if not self.role.IsKick():
			if self.role.GetSceneID() == EnumGameConfig.ClashOfTitansSceneID:
				jumpX, jumpY = GetRandomPositon()
				self.role.JumpPos(jumpX, jumpY)


	def CreateSoulNPC(self):
		'''
		创建英魂NPC
		'''
		if self.role.IsKick():
			return None
		#如果角色已经不在当前场景中
		if self.role.GetSceneID() != EnumGameConfig.ClashOfTitansSceneID:
			return None
		
		pos_x, pos_y = self.role.GetPos()
		if TheWarMgr is None:
			return None
		if IsStart is False:
			return None
		npc = TheWarMgr.scene.CreateNPC(EnumGameConfig.ClashOfTitansNPCType, pos_x, pos_y, 1, 1, {EnumNPCData.EnNPC_Name:GlobalPrompt.ClashOfTitansSoulNpcName % self.name})
		npc.SetPyDict(1, self.fightData)
		npc.SetPyDict(2, self.name)
		return pos_x, pos_y


	def IncScore(self, value, win):
		if IsStart is False:
			return
		if not value > 0:
			return
		if win is True:
			tra = TraClashOfTitansTitanWinGetScore
		elif win is False:
			tra = TraClashOfTitansTitanLoseGetScore
		else :
			# win is None
			tra = TraClashOfTitansTitanSystemScore
			
		with tra:
			self.score += value
			AutoLog.LogBase(self.roleID, AutoLog.eveClashOfTitansGetScore, value)
		global COTR
		COTR.HasData(self.roleID, [self.score, self.rebornCnt, self.zdl, self.level , self.name, self.unionName, self.isDeadOut])


	def TryReborn(self, reason):
		'''
		尝试重生
		'''
		#如果活动已经结束的话不用重生了
		if IsStart is False:
			return
		
		if self.rebornCnt >= EnumGameConfig.ClashOfTitansMaxRebornCnt:
			self.isDeadOut = True
			self.UnregDeathTick()
			global COTR
			COTR.HasData(self.roleID, [self.score, self.rebornCnt, self.zdl, self.level , self.name, self.unionName, self.isDeadOut])
			
			role = self.role
			if role.IsKick():
				return
			if role.GetSceneID() != EnumGameConfig.ClashOfTitansSceneID:
				return
			#如果是由于离开场景造成的死亡的话，是不允许执行下面role.BackPublicScene()逻辑的，否则会造成循环调用耗尽堆栈的问题
			if reason == DieByOutScene:
				role.Msg(5, 0, GlobalPrompt.ClashOfTitansDeadoutTips % self.score)
				return
			
			#传送出诸神之战场景
			role.BackPublicScene()
			role.Msg(5, 0, GlobalPrompt.ClashOfTitansDeadoutTips % self.score)
			return
		
		with TraClashOfTitansTitanRoleReborn:
			AutoLog.LogBase(self.roleID, AutoLog.eveClashOfTitansDieReborn, None)
			self.rebornCnt += 1
			#清除英魂，重置血量
			self.ResetHP()
			self.UpdateHPShow()
		
		if self.role.IsKick():
			return
		if self.role.GetSceneID() != EnumGameConfig.ClashOfTitansSceneID:
			return
		
		self.role.SendObj(SyncClashOfTitansDeathSeconds, self.deathSeconds)
		self.role.SetAppStatus(EnumRoleStatus.CT_Dying)
		
		SyncRoleData(self.role)
	
	
	def UpdateHPShow(self):
		'''
		更新用于显示的血量
		'''
		self.hp_show[1] = self.GetCurrentHP() if self.GetCurrentHP() > 0 else self.hp_show[0]
	

	def ResetHP(self):
		'''
		重置血量
		'''
		self.bind_hp = {}


	def GetBindHP(self):
		return self.bind_hp


	def GetScore(self):
		'''
		获取分数
		'''
		return self.score
	

	def PickUpSoal(self, soulName, soulFightData):
		'''
		拾取英灵
		'''
		self.soulName = soulName
		self.soulFightData = soulFightData
		self._UpdateFightData()
		
		self.role.Msg(2, 0, GlobalPrompt.ClashOfTitansPickUpSoulSelf % (soulName, soulName))
		TheWarMgr.scene.Msg(1, 0, GlobalPrompt.ClashOfTitansPickUpSoulGlobal % (self.name, soulName))

	
	def ClearSoul(self):
		'''
		清理英灵
		'''
		self.soulName = None
		self.soulFightData = None
		self._UpdateFightData()


	def GetFightData(self):
		'''
		战斗数据，有英魂的时候属性会有变化
		'''
		return self.realFightData

	
	def _UpdateFightData(self):
		'''
		更新真正的战斗数据
		'''
		#如果有英灵的话，返回英灵的战斗数据；否则返回角色自己的战斗数据
		#这里的情况是，主角战斗数据完全由英灵代替，英雄的话则根据英雄类型来取出英雄战斗数据，如果英灵不存在该类型，则不覆盖，存在则覆盖，存在多个则随机取出其中一个进行覆盖
		
		if self.soulFightData is None:
			self.realFightData = self.fightData
		
		else:
			soulRoleData, soulHeroData = copy.deepcopy(self.soulFightData)
			roleData, heroData = copy.deepcopy(self.fightData)
			#主角数据处理
			DictUpDate(roleData, soulRoleData, SoulRolePropertyList)
			#英雄数据处理
			for data in heroData.itervalues():
				#首先获取英雄职业类型(相同职业类型才能发生属性替换)
				heroCareer = data[Middle.Career]
				for soulData in soulHeroData.itervalues():
					if soulData[Middle.Career] != heroCareer:
						continue
					DictUpDate(data, soulData, SoulHeroPropertyList)
					break
			self.realFightData = roleData, heroData
			
#===============================================================================
# 数据同步
#===============================================================================
def SyncRoleData(role):
	if TheWarMgr is None:
		return
	warRoleData = TheWarMgr.GetRoleData(role)
	if warRoleData is None:
		return
	role.SendObj(SyncClashOfTitansPersonnalData, warRoleData)


def SyncKillRankData(role):
	'''
	同步连杀榜数据
	'''
	if TheWarMgr is None:
		return
	killRank = TheWarMgr.wantRank.data
	role.SendObj(SyncClashOfTitansKillRank, killRank)


def SyncAliveRankData(role):
	'''
	同步生存榜数据
	'''
	if TheWarMgr is None:
		return
	aliveRank = TheWarMgr.rebornRank
	role.SendObj(SyncClashOfTitansAliveRank, aliveRank)


def SyncFightHistory(role):
	'''
	同步战斗历史
	'''
	if TheWarMgr is None:
		return
	roleID = role.GetRoleID()
	warRole = TheWarMgr.GetWarRole(roleID)
	if warRole is None:
		return
	role.SendObj(SyncClashOfTitansFightHistory, warRole.fightHistory)


#===============================================================================
# tools
#===============================================================================
def DictUpDate(dt1, dt2, keys):
	'''
	keys->type(list)
	for key in keys:
	dt1[key] = dt2[key]
	example:
	>>dt1 = {1:1,2:2,3:3}
	>>dt2 = {1:2,2:3,3:4}
	>>keys = [1,2]
	>>DictUpDate(dt1, dt2, keys)
	>>dt1
	>>{1:2,2:3,3:3}
	'''
	for key in keys:
		if key not in dt1 or key not in dt2:
			continue
		dt1[key] = dt2[key]


def GetRoleMaxHp(role):
	'''
	获取玩家最大血量
	'''	
	roleData, heroData = Middle.GetRoleData(role, True)
	total_maxhp = roleData.get(Middle.MaxHP, 0)
	if heroData:
		for data in heroData.itervalues():
			total_maxhp += data.get(Middle.MaxHP, 0)
	return total_maxhp


def ToLeft(value, theset):
	'''
	获取theset中数轴上value左侧最接近value的值
	example:
	>> ToLeft(7, set([1,3,4,5,7]))
	>> 7
	>> ToLeft(6, set([1,3,4,5,7]))
	>> 5
	'''
	if value in theset:
		return value
	else:
		theList = list(theset)
		theList.sort()
		theIndex = 0
		for i in theList:
			if i > value:
				return theIndex
			theIndex = i
		else:
			return theIndex

def DistanSquare(posA, posB):
	'''
	返回两个坐标点距离的平方
	'''
	return (posA[0] - posB[0]) ** 2 + (posA[1] - posB[1]) ** 2


def GetRandomTips():
	'''
	连杀的时候返回随机的公告
	'''
	tipSList = [GlobalPrompt.ClashOfTitansKillTips1, GlobalPrompt.ClashOfTitansKillTips2, GlobalPrompt.ClashOfTitansKillTips3]
	return random.choice(tipSList)


def GetRandomPositon():
	'''
	随机位置
	'''
	area = random.choice(Aera)
	x = random.choice(range(*area[0]))
	y = random.choice(range(*area[1]))
	return x, y


#===============================================================================
# NPC管理,场景中所有的英魂都以NPC的形式出现
#===============================================================================
def OnClickSoalNPC(role, npc):
	'''
	点击英魂的NPC
	'''
	#战斗状态中不能拾取英魂
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		#战斗状态中不能拾取
		return
	
	#不在这个场景中
	if role.GetSceneID() != TheWarMgr.sceneID:
		return
	
	roleID = role.GetRoleID()
	warRole = TheWarMgr.GetWarRole(roleID)
	if warRole is None:
		return
	
	#英魂的属性字典
	soulDict = npc.GetPyDict()
	#英魂的战斗数据
	soulFightData = soulDict.get(1)
	if not soulFightData:
		return
	#英魂的名字
	soulName = soulDict.get(2)
	if not soulName:
		return
	
	#先删除npc再拾取 英魂防止重复拾取
	npc.Destroy()
	warRole.PickUpSoal(soulName, soulFightData)


def InitClickFun():
	"""
	注册英魂点击函数
	"""
	NPCServerFun.RegNPCServerOnClickFunEx(EnumGameConfig.ClashOfTitansNPCType, OnClickSoalNPC)
#===============================================================================
# 战斗控制
#===============================================================================
def ClashOfTitansPvP(leftWarRole, rightWarRole, AfterFight, OnLeaveFun):
	'''
	诸神之战战斗
	'''
	fight = Fight.Fight(EnumGameConfig.ClashOfTitansFightType)
	left_camp, right_camp = fight.create_camp()
	
	#注册战斗超时tick
	leftWarRole.fightTimeOutTickID = cComplexServer.RegTick(EnumGameConfig.ClashOfTitansFightTimeOutSeconds, OnFightPlayTimeOut, leftWarRole)
	rightWarRole.fightTimeOutTickID = cComplexServer.RegTick(EnumGameConfig.ClashOfTitansFightTimeOutSeconds, OnFightPlayTimeOut, rightWarRole)
	
	leftWarRole.role.SetAppStatus(EnumRoleStatus.CT_Fighting)
	rightWarRole.role.SetAppStatus(EnumRoleStatus.CT_Fighting)
	
	#一旦进入战斗，就取消死亡tick
	leftWarRole.UnregDeathTick()
	rightWarRole.UnregDeathTick()
	
	#绑定血量并创建左右阵营
	left_camp.bind_hp(leftWarRole.GetBindHP())
	right_camp.bind_hp(rightWarRole.GetBindHP())
	left_camp.create_online_role_unit(leftWarRole.role, fightData=leftWarRole.GetFightData(), use_px=True)
	right_camp.create_online_role_unit(rightWarRole.role, fightData=rightWarRole.GetFightData(), use_px=True)
	
	fight.after_fight_fun = AfterFight
	fight.on_leave_fun = OnLeaveFun
	fight.after_fight_param = leftWarRole, rightWarRole
	fight.start()


def AfterClashOfTitansFight(fightObj):
	'''
	战斗后处理
	'''
	#战斗结束的时候可能活动已经结束了
	if TheWarMgr is None:
		return
	if IsStart is False:
		return
	
	leftWarRole, rightWarRole = fightObj.after_fight_param
	
	#不管战斗结果如何，首先应该清除英魂
	leftWarRole.ClearSoul()
	rightWarRole.ClearSoul()
	
	#平局的话算攻击方胜利
	if not fightObj.result:
		warRoleWin = rightWarRole
		warRoleLose = leftWarRole
	
	#确定胜利和失败的角色
	if fightObj.result == -1:
		warRoleWin = rightWarRole
		warRoleLose = leftWarRole
		
	elif fightObj.result == 1:
		warRoleWin = leftWarRole
		warRoleLose = rightWarRole
	
	
	#计算胜利和失败角色分别获得的积分
	winScore = EnumGameConfig.ClashOfTitansFightScoreBase + EnumGameConfig.ClashOfTitansFightScoreCoe * leftWarRole.killCnt + EnumGameConfig.ClashOfTitansFightScoreCoe * rightWarRole.killCnt
	loseScore = EnumGameConfig.ClashOfTitansFightScoreBase
	warRoleLose.IncScore(loseScore, False)
	warRoleWin.IncScore(winScore, True)
	
	#输了的不仅会死，还要重置连杀次数；赢了的增加连杀次数	。此外，输赢都要增加积分。
	warRoleWin.IncKillCnt(1)
	#以下两行顺序不能调换，否则的话无法创建英魂了
	warRoleLose.Die(reason=DieByKilled, killer=warRoleWin.name)
	warRoleLose.ResetKillCnt()
	
	warRoleLose.History(0, warRoleWin.name, loseScore)
	warRoleWin.History(1, warRoleLose.name, winScore)
	#更新用于显示的血量
	warRoleLose.UpdateHPShow()
	warRoleWin.UpdateHPShow()
	
	fightObj.set_fight_statistics(warRoleWin.roleID, EnumFightStatistics.EnumClashOfTitansScore, winScore)
	fightObj.set_fight_statistics(warRoleLose.roleID, EnumFightStatistics.EnumClashOfTitansScore, loseScore)
	
	#角色数据同步
	roleLeft = leftWarRole.role
	if not roleLeft.IsKick():
		SyncRoleData(roleLeft)
		SyncKillRankData(roleLeft)
		SyncFightHistory(roleLeft)
	
	roleRight = rightWarRole.role
	if not roleRight.IsKick():
		#战斗后立即同步角色个人数据和连杀榜数据
		SyncRoleData(roleRight)
		SyncKillRankData(roleRight)
		SyncFightHistory(roleRight)
	

def OnFightPlayTimeOut(callargv, params):
	'''
	战斗开始的时候要注册这个tick，战斗结束的时候要取消这个tick
	'''
	if IsStart is False:
		return
	if TheWarMgr is None:
		return
	
	warRole = params
	#注册死亡tick
	warRole.RegDeathTick()
	#每次发生超时都要记录日志
	with TraClashOfTitansTitanFightTimeOut:
		AutoLog.LogBase(warRole.roleID, AutoLog.eveClashOfTitansFightTimeOut, None)
		if warRole.fightTimeOutTickID > 0:
			cComplexServer.UnregTick(warRole.fightTimeOutTickID)
			warRole.fightTimeOutTickID = 0
			
	warRole.Die(reason=DieByTimeOut)
			
	if warRole.role.IsKick():
		return
	
	warRole.role.SendObj(SyncClashOfTitansDeathSeconds, warRole.deathSeconds)
	
	if warRole.role.GetSceneID() == EnumGameConfig.ClashOfTitansSceneID:
		warRole.role.SetAppStatus(EnumRoleStatus.CT_Dying)

	role = warRole.role
	#战斗强制结束
	camp = role.GetTempObj(EnumTempObj.FightCamp)
	if not camp:
		return
	camp.fight.end(-1)
	
	SyncRoleData(role)
	SyncKillRankData(role)
	SyncFightHistory(role)
	
	role.Msg(2, 0, GlobalPrompt.ClashOfTitansTimeOutTip)


def OnLeaveFightFun(fightObj, role):
	'''
	角色离开战斗处理
	'''
	#战斗结束的时候可能活动已经结束了
	if TheWarMgr is None:
		return
	if IsStart is False:
		return
	
	roleID = role.GetRoleID()
	warRole = TheWarMgr.GetWarRole(roleID)
	if warRole is None:
		return
	
	leftWarRole, rightWarRole = fightObj.after_fight_param
	
	#战斗播放完成首先要重新注册死亡tick
	if fightObj.result == 1:
		if leftWarRole.roleID == roleID:
			leftWarRole.RegDeathTick()
		elif rightWarRole.roleID == roleID:
			rightWarRole.RegDeathTick(needProtect=True)
		else:
			warRole.RegDeathTick()
	else:
		if leftWarRole.roleID == roleID:
			leftWarRole.RegDeathTick(needProtect=True)
		elif rightWarRole.roleID == roleID:
			rightWarRole.RegDeathTick()
		else:
			warRole.RegDeathTick()
	
	#取消战斗超时tick
	if warRole.fightTimeOutTickID > 0:
		cComplexServer.UnregTick(warRole.fightTimeOutTickID)
		warRole.fightTimeOutTickID = 0
		
	#如果战斗后角色还在线的话应该改变其头顶状态为等死状态
	if not role.IsKick():
		role.SendObj(SyncClashOfTitansDeathSeconds, warRole.deathSeconds)
		if role.GetSceneID() == EnumGameConfig.ClashOfTitansSceneID:
			role.SetAppStatus(EnumRoleStatus.CT_Dying)

#===============================================================================
# 场景控制
#===============================================================================
@PublicScene.RegSceneAfterJoinRoleFun(EnumGameConfig.ClashOfTitansSceneID)
def AfterJoin(scene, role):
	'''
	诸神之战角色进入场景后的处理
	'''
	#活动管理器都没有初始化的话就传出场景
	if TheWarMgr is None:
		role.BackPublicScene()
		return
	if TheWarMgr.IsWarRole(role) is False:
		role.BackPublicScene()
		return
	TheWarMgr.InScene(role)
	#进入诸神之战状态
	Status.ForceInStatus(role, EnumInt1.ST_ClashOfTitans)
	
	if IsStart is True:
		#设置等死状态
		role.SetAppStatus(EnumRoleStatus.CT_Dying)
	
	SyncRoleData(role)
	SyncAliveRankData(role)
	SyncKillRankData(role)
	SyncFightHistory(role)
	
	warRole = TheWarMgr.GetWarRole(role.GetRoleID())
	role.SendObj(SyncClashOfTitansDeathSeconds, warRole.deathSeconds)
	

@PublicScene.RegSceneBeforeLeaveFun(EnumGameConfig.ClashOfTitansSceneID)
def BeforeLeave(scene, role):
	'''
	诸神之战角色退出场景前的处理
	'''
	#退出诸神之战状态
	Status.Outstatus(role, EnumInt1.ST_ClashOfTitans)
	role.SetAppStatus(0)
	
	if TheWarMgr is not None:
		if TheWarMgr.IsWarRole(role) is not  False:
			TheWarMgr.LeaveScene(role)
	
	Status.Outstatus(role, EnumInt1.ST_ClashOfTitans)
	role.SetAppStatus(0)
	

#===============================================================================
# 活动时间控制
#===============================================================================
def FiveMinitesReady():
	'''
	五分钟倒计时，此时，角色已经可以进入场景
	'''
	#生成战争管理器
	if cDateTime.WeekDay() not in [1, 3, 5, 0]:
		return
	
	global TheWarMgr
	if not TheWarMgr is None:
		return
	global CanJoin
	CanJoin = True
	TheWarMgr = WarMgr()
	global COTR
	COTR.Clear()
	
	#注册一分钟倒计时公告
	cComplexServer.RegTick(OneMinute * 4, OneMinitesReady, None)
	cRoleMgr.Msg(1, 0, GlobalPrompt.ClashOfTitansFiveMiniutesReady)


def OneMinitesReady(callargv, params):
	'''
	一分钟倒计时
	'''
	if cDateTime.WeekDay() not in [1, 3, 5, 0]:
		return
	cRoleMgr.Msg(1, 0, GlobalPrompt.ClashOfTitansOneMiniutesReady)


def Start():
	'''
	活动开始
	'''
	if cDateTime.WeekDay() not in [1, 3, 5, 0]:
		return
	global TheWarMgr
	if TheWarMgr is None:
		return
	global IsStart, CanJoin
	if IsStart is True:
		return
	IsStart = True
	CanJoin = False
	TheWarMgr.WarBegin()
	cRoleMgr.Msg(1, 0, GlobalPrompt.ClashOfTitansStart)


def End():
	'''
	活动结束
	'''
	if cDateTime.WeekDay() not in [1, 3, 5, 0]:
		return
	global TheWarMgr
	if TheWarMgr is None:
		return
	TheWarMgr.WarEnd()
	

def Final():
	'''
	到扫战场
	'''
	if cDateTime.WeekDay() not in [1, 3, 5, 0]:
		return
	global TheWarMgr
	#赶走玩家
	for role in TheWarMgr.scene.GetAllRole():
		role.BackPublicScene()
	
	#干掉场景内所有的NPC
	for npc in TheWarMgr.scene.GetAllNPC():
		npc.Destroy()
	
	#干掉战争管理器
	TheWarMgr = None


#===============================================================================
# 奖励管理
#===============================================================================
def PersonalRankReward(rankData):
	'''
	个人排行奖励
	'''
	#首先对排行榜字典里的数据进行排行
	rankList = rankData.items()
	#self.roleID, [self.score, self.killCnt, self.zdl, self.level,self.name, self.unionName, self.isDeadOut]
	rankList.sort(key=lambda x:(x[1][0], x[1][1], x[1][2]), reverse=True)
	
	rankDict = {}
	for index, (roleId, theList) in enumerate(rankList):
		#排行是索引+1
		rankDict[roleId] = [index + 1, theList[3]]
		
	RC = RewardBuff.CalNumber
	RCO = RewardBuff.enClashOfTitans
	
	for roleID, (rank, level) in rankDict.iteritems():
		levelRange = ClashOfTitansConfig.LevelRangeDict.get(level)
		if not levelRange:
			continue
		config = ClashOfTitansConfig.PersonRankConfigDict.get((rank, levelRange))
		if not config:
			continue
		
		#这里还需要配置奖励枚举
		AwardMgr.SetAward(roleID, EnumAward.ClashOfTitansPersonScoreRankAward, money=RC(RCO, config.rewardMoney), itemList=[(coding, RC(RCO, cnt)) for (coding, cnt) in config.rewardItems], clientDescParam=(rank,))


def PersonalScoreReward(warRoleDict):
	'''
	个人积分奖励
	'''
	RC = RewardBuff.CalNumber
	RCO = RewardBuff.enClashOfTitans
	
	for warRole in warRoleDict.itervalues():
		levelRange = ClashOfTitansConfig.LevelRangeDict.get(warRole.level)
		if not levelRange:
			continue
		
		theSet = ClashOfTitansConfig.PersonScoreRangeDict.get(levelRange)
		if not theSet:
			continue
		roleScore = warRole.GetScore()
		theScore = ToLeft(roleScore, theSet)
		config = ClashOfTitansConfig.PersonScoreConfigDict.get((theScore, levelRange))
		roleID = warRole.roleID
		if not config:
			continue
		AwardMgr.SetAward(roleID, EnumAward.ClashOfTitansPersonScoreAward, money=RC(RCO, config.rewardMoney), itemList=[(coding, RC(RCO, cnt)) for (coding, cnt) in config.rewardItems], clientDescParam=(roleScore,))


def UnionScoreReward(roleIDList, warRoleDict, score):
	'''
	公会积分奖励
	'''
	RC = RewardBuff.CalNumber
	RCO = RewardBuff.enClashOfTitans
	
	for roleID in roleIDList:
		warRole = warRoleDict.get(roleID)
		if not warRole:
			continue
		levelRange = ClashOfTitansConfig.LevelRangeDict.get(warRole.level)
		if not levelRange:
			continue
		theSet = ClashOfTitansConfig.UnionScoreRangeDict.get(levelRange)
		if not theSet:
			continue
		theScore = ToLeft(score, theSet)
		config = ClashOfTitansConfig.UnionScoreConfigDict.get((theScore, levelRange))
		if not config:
			continue
		AwardMgr.SetAward(roleID, EnumAward.ClashOfTitansUnionScoreAward, exp=RC(RCO, config.experience), itemList=[(coding, RC(RCO, cnt)) for (coding, cnt) in config.rewardItems], clientDescParam=(score,))
	

def TitanPersonalReward(warRole):
	'''
	战神个人奖励 
	'''
	levelRange = ClashOfTitansConfig.LevelRangeDict.get(warRole.level)
	if not levelRange :
		return
	config = ClashOfTitansConfig.TitanConfigDict.get(levelRange)
	if not config:
		return
	AwardMgr.SetAward(warRole.roleID, EnumAward.ClashOfTitansTitanAward, money=config.rewardMoney, itemList=config.rewardItems)


def TitanUnionReaward(roleIDSet, warRoleDict, titanID, titanName):
	'''
	战神公会奖励
	'''
	for roleID in roleIDSet:
		if roleID == titanID:
			continue
		warRole = warRoleDict.get(roleID)
		if not warRole:
			continue
		levelRange = ClashOfTitansConfig.LevelRangeDict.get(warRole.level)
		if not levelRange :
			continue
		config = ClashOfTitansConfig.TitanUnionConfigDict.get(levelRange)
		if not config:
			continue
		AwardMgr.SetAward(roleID, EnumAward.ClashOfTitansTitanUnionAward, money=config.rewardMoney, itemList=config.rewardItems, clientDescParam=(titanName,))

#===============================================================================
# 客户端请求
#===============================================================================
def RequestJoinClashOfTitans(role, msg):
	#需要加一些状态判断
	if role.GetLevel() < EnumGameConfig.ClashOfTitansNeedLevel:
		return
	
	#只有加入过公会的角色才可以参加诸神之战
	if not role.GetUnionObj():
		return
	
	if TheWarMgr is None:
		return
	
	#当前不是可以进入的时间并且之前也没进入过
	if CanJoin is False:
		if not TheWarMgr.IsWarRole(role):
			role.Msg(2, 0, GlobalPrompt.ClashOfTitansEntryClose)
			return
		elif IsStart is False:
			role.Msg(2, 0, GlobalPrompt.ClashOfTitansEnd)
			return
		
	#如果不能进入诸神之战状态 
	if not Status.CanInStatus(role, EnumInt1.ST_ClashOfTitans):
		return

	#加入诸神之战
	TheWarMgr.JoinBattle(role)
	
	#如果不在场景中则传送至众神之战的场景
	if role.GetSceneID() == EnumGameConfig.ClashOfTitansSceneID:
		return
	
	#检测是否加入成功了
	roleID = role.GetRoleID()
	warRole = TheWarMgr.GetWarRole(roleID)
	
	if not warRole:
		return
	
	Event.TriggerEvent(Event.Eve_WangZheCrazyRewardTask, role, (EnumGameConfig.WZCR_Task_ClashOfTitans, True))
	
	Event.TriggerEvent(Event.Eve_PassionMultiRewardTask, role, (EnumGameConfig.PassionMulti_Task_ClashOfTitans, True))
	#元旦金猪活动任务进度
	Event.TriggerEvent(Event.Eve_NewYearDayPigTask, role, (EnumGameConfig.NewYearDay_Task_ClashOfTitans, True))
	#死透的玩家不能再进场景
	if warRole.isDeadOut:
		role.Msg(2, 0, GlobalPrompt.ClashOfTitansCanNotReborn)
		return
	
	X, Y = GetRandomPositon()
	role.Revive(EnumGameConfig.ClashOfTitansSceneID, X, Y)


def RequestQuitClashOfTitans(role, msg):
	'''
	客户端请求退出诸神之战
	'''
	if role.GetSceneID() != EnumGameConfig.ClashOfTitansSceneID:
		return
	role.BackPublicScene()


def RequestGetWantPos(role, msg):
	'''
	请求获取被追杀者坐标
	'''
	callBackId, wantRoleID = msg
	scene = cSceneMgr.SearchPublicScene(EnumGameConfig.ClashOfTitansSceneID)
	wantRole = scene.SearchRole(wantRoleID)
	if not wantRole:
		role.Msg(2, 0, GlobalPrompt.ClashOfTitansNotInScene)
		return
	
	#回调客户端
	role.CallBackFunction(callBackId, wantRole.GetPos())


def RequestPersonGetScoreRank(role, msg):
	'''
	请求获取角色积分排行
	'''
	role.SendObj(SyncClashOfTitansScoreRank, COTR.data)


def RequestFightClashOfTitans(role, msg):
	'''
	客户端请求战斗
	'''
	#不存在战斗管理器
	if TheWarMgr is None:
		return
	
	#战斗还没开始
	if IsStart is False:
		return
	
	if role.GetCD(EnumCD.ClashOfTitansFight) > 0:
		return
	
	#战斗右侧角色id
	rightRoleID = msg
	
	#不能挑战自己
	roleID = role.GetRoleID()
	if role.GetRoleID() == rightRoleID:
		return
	
	#不能挑战一个不在线的角色
	rightRole = cRoleMgr.FindRoleByRoleID(rightRoleID)
	if rightRole is None:
		return
	
	#只有在等死状态下的角色才能战斗
	if role.GetAppStatus() != EnumRoleStatus.CT_Dying or rightRole.GetAppStatus() != EnumRoleStatus.CT_Dying:
		return
	
	#判断角色距离
	posA = role.GetPos()
	posB = rightRole.GetPos()
	if DistanSquare(posA, posB) > TheDistance:
		return
	
	#是否可以进入战斗
	if not Status.CanInStatus(role, EnumInt1.ST_FightStatus) or not Status.CanInStatus(rightRole, EnumInt1.ST_FightStatus):
		return
	
	#角色必须都在场景中
	if not role.GetSceneID() == rightRole.GetSceneID() == TheWarMgr.sceneID:
		return
	
	warRole = TheWarMgr.GetWarRole(roleID)
	rightWarRole = TheWarMgr.GetWarRole(rightRoleID)
	
	#复活后的前20秒是保护时间，此时不能收到攻击
	if cDateTime.Seconds() < rightWarRole.protectSeconds:
		role.Msg(2, 0, GlobalPrompt.ClashOfTitansRoleInProtected)
		return
	
	if not warRole or not rightWarRole:
		return

	#请求了战斗之后，无论输赢，都要设置15秒的冷却时间
	role.SetCD(EnumCD.ClashOfTitansFight, EnumGameConfig.ClashOfTitansFightCDSeconds)
	ClashOfTitansPvP(warRole, rightWarRole, AfterClashOfTitansFight, OnLeaveFightFun)


#===============================================================================
# 事件触发
#===============================================================================
def OnClientLostOrRoleExit(role, param):
	'''
	 客户端掉线需要先离开诸神之战场景
	'''
	if role.GetSceneID() != EnumGameConfig.ClashOfTitansSceneID:
		return
	role.BackPublicScene()


if "_HasLoad" not in dir():
	if Environment.IsDevelop or Environment.EnvIsQQ() or Environment.EnvIsFT() or Environment.EnvIsTK() or Environment.EnvIsPL() or Environment.EnvIsRU() or Environment.EnvIsNA() or Environment.EnvIsFR():
		if Environment.HasLogic or Environment.HasWeb:
			#诸神之战个人积分排行
			COTR = personalScoreRank()
		
		if Environment.HasLogic and not Environment.IsCross:
			Cron.CronDriveByMinute((2038, 1, 1), FiveMinitesReady, H=" H == 20", M="M == 0")
			Cron.CronDriveByMinute((2038, 1, 1), Start, H="H == 20", M="M == 5")
			Cron.CronDriveByMinute((2038, 1, 1), End, H="H == 20", M="M == 30")
			Cron.CronDriveByMinute((2038, 1, 1), Final, H="H == 20", M="M == 32")
			
			InitClickFun()
			Event.RegEvent(Event.Eve_BeforeExit, OnClientLostOrRoleExit)
			Event.RegEvent(Event.Eve_ClientLost, OnClientLostOrRoleExit)
			
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestJoinClashOfTitans", "客户端请求进入诸神之战"), RequestJoinClashOfTitans)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestFightClashOfTitans", "客户端请求诸神之战战斗"), RequestFightClashOfTitans)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetPosClashOfTitans", "客户端请求诸神之战获取被追杀者位置"), RequestGetWantPos)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestQuitClashOfTitans", "客户端请求退出诸神之战"), RequestQuitClashOfTitans)
			cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestGetPersonScoreRankClashOfTitans", "客户端请求获取个人积分排行诸神之战"), RequestPersonGetScoreRank)
		
