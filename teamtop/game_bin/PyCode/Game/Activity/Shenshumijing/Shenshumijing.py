#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Shenshumijing.Shenshumijing")
#===============================================================================
# 神树密境
#===============================================================================
import random
import Environment
import cRoleMgr
import cSceneMgr
import cDateTime
import cNetMessage
import cComplexServer
from Common.Other import GlobalPrompt, EnumGameConfig, EnumSysData,\
	EnumRoleStatus
from Common.Message import AutoMessage
from ComplexServer.Time import Cron
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumDayInt1, EnumDayInt8, EnumInt1, EnumInt64,\
	EnumObj, EnumTempObj
from Game.SysData import WorldData
from Game.Activity.Shenshumijing import ShenshumijingConfig
from Game.NPC import NPCServerFun, EnumNPCData
from Game.Team import TeamBase, EnumTeamType
from Game.Role import Status, Event
from Game.Fight import Fight
from Game.Role.Mail import Mail
from Game.Scene import PublicScene
from Game.DailyDo import DailyDo

EnumCaijiPosIndex = 1
EnumCaijiCnt = 2
EnumCaijiReward = 3
EnumGuardPosIndex = 4
EnumGuardInFight = 5
EnumGuardNpcCfg = 6
EnumCaijiIsrumor = 7
EnumCaijiReward_fcm = 8

if "_HasLoad" not in dir():
	IsStart = False
	IsGuard = False
	
	#培养次数
	S_PeiyangCnt = 0
	#神树npcid
	S_ShenshuNpcId = 0
	#公会排名对象
	S_UnionRankObj = None
	#场景对象
	S_SceneObj = None
	
	#采集刷怪tick
	S_CaijiTick = None
	#采集给经验tick
	S_CaijiExpTick = None
	#当前采集npc位置索引集合 set([posIndex,])
	S_CaijiNpcPosSet = set()
	#当前采集npc {npcId:npc}
	S_CaijiNpcDict = {}
	#当前玩家采集tick {roleId:tickId}
	S_CaijiTick_Dict = {}
	
	#总守卫个数
	S_TotalMonsterCnt = 0
	#守卫波数
	S_GuardWave = 0
	#每波刷怪个数
	S_GuardNpcCnt = 0
	#总的怪物个数
	S_GuardNpcTotalCnt = 0
	#个人击杀个数 {roleId:killCnt}
	S_PersonKill_Dict = {}
	#守卫npc索引集合  set([npc,])
	S_GuardNpcPosSet = set()
	
	#左面板消息 -- 浇水人数
	ShenshumijingPeiyangCnt = AutoMessage.AllotMessage("ShenshumijingPeiyangCnt", "神树密境培养次数")
	#右上面板消息 -- [波数, 个人击杀个数, 剩余怪物个数]
	ShenshumijingMonsterData = AutoMessage.AllotMessage("ShenshumijingMonsterData", "神树密境怪物数据")
	#右下面板消息 -- {公会id:[公会名字, 击杀怪物个数, 公会战斗力, 公会id]}
	ShenshumijingUnionData = AutoMessage.AllotMessage("ShenshumijingUnionData", "神树密境公会数据")
	#采集时间戳
	ShenshumijingCaijiSec = AutoMessage.AllotMessage("ShenshumijingCaijiSec", "采集时间戳")
	#培养时间戳
	ShenshumijingPeiyangSec = AutoMessage.AllotMessage("ShenshumijingPeiyangSec", "培养时间戳")
	#打开组队面板同步队伍信息
	ShenshumijingSynOpenData = AutoMessage.AllotMessage("ShenshumijingSynOpenData", "打开神树密境组队面板同步数据")
	#神树npcid
	ShenshumijingShenshuNpcId = AutoMessage.AllotMessage("ShenshumijingShenshuNpcId", "神树npcid")
	#神树密境组队面板可邀请玩家数据
	ShenshumijingCanInviteData = AutoMessage.AllotMessage("ShenshumijingCanInviteData", "神树密境组队面板可邀请玩家数据")
	
	#========================================日志=================================
	#神树密境使用神石增益
	ShenshumijingUseRmb_Log = AutoLog.AutoTransaction("ShenshumijingUseRmb_Log", "神树密境使用神石增益")
	#神树密境时间获得经验
	ShenshumijingTimeExp_Log = AutoLog.AutoTransaction("ShenshumijingTimeExp_Log", "神树密境时间获得经验")
	#神树密境采集获得奖励
	ShenshumijingCaiji_Log = AutoLog.AutoTransaction("ShenshumijingCaiji_Log", "神树密境采集获得奖励")
	#神树密境守卫获得奖励
	ShenshumijingGuard_Log = AutoLog.AutoTransaction("ShenshumijingGuard_Log", "神树密境守卫获得奖励")
	#神树密境公会奖励
	ShenshumijingUnionReward_Log = AutoLog.AutoTransaction("ShenshumijingUnionReward_Log", "神树密境公会奖励")
	#神树密境守卫成功奖励
	ShenshumijingSuccessReward_Log = AutoLog.AutoTransaction("ShenshumijingSuccessReward_Log", "神树密境守卫成功奖励")
	#神数秘境培养
	ShenshumijingPeiyang_Log = AutoLog.AutoTransaction("ShenshumijingPeiyang_Log", "神数秘境培养日志")
#===============================================================================
# 公会排行榜
#===============================================================================
class UnionRank():
	def __init__(self):
		self.minKill = None
		self.unionDict = {}
		self.unionRankDict = {}
		self.unionRoleDict = {}
		
	def addUnion(self, unionId, unionName, unionZDL):
		if unionId not in self.unionDict:
			self.unionDict[unionId] = [unionName, 0, unionZDL]
		
	def addRole(self, unionId, roleId):
		if unionId not in self.unionRoleDict:
			self.unionRoleDict[unionId] = set()
		self.unionRoleDict[unionId].add(roleId)
		
	def addKillCnt(self, unionId):
		if (not unionId) or (unionId not in self.unionDict):
			return
		self.unionDict[unionId][1] += 1
		
		self.inRank(unionId, self.unionDict[unionId][0])
		
	def inRank(self, unionId, unionName):
		if unionId not in self.unionDict:
			return
		killCnt, zdl = self.unionDict[unionId][1], self.unionDict[unionId][2]
		
		#尝试构建最小分值
		if not self.minKill:
			self.minKill = [unionId, killCnt]
		
		if unionId in self.unionRankDict:
			self.unionRankDict[unionId][1] = killCnt
			if unionId == self.minKill[0]:
				self.minKill[1] = killCnt
			else:
				return
		elif len(self.unionRankDict) < ShenshumijingConfig.ShenshuUnionMaxCnt:
			self.unionRankDict[unionId] = [unionName, killCnt, zdl, unionId]
			if killCnt > self.minKill[1]:
				return
		elif killCnt > self.minKill[1]:
			del self.unionRankDict[self.minKill[0]]
			self.unionRankDict[unionId] = [unionName, killCnt, zdl, unionId]
			self.minKill = [unionId, killCnt]
		elif killCnt <= self.minKill[1]:
			return
		#构建最小值
		for unionId, value in self.unionRankDict.iteritems():
			if value[1] < killCnt:
				killCnt = value[1]
				self.minKill = [unionId, killCnt]
		
	def getSyncRank(self):
		return self.unionRankDict
#===============================================================================
# 时间触发
#===============================================================================
def TenMinuteReady():
	#十分钟准备
	cRoleMgr.Msg(1, 0, GlobalPrompt.ShenshumijingTenMinuteReady)
	
def OneMinuteReady():
	#一分钟准备
	cRoleMgr.Msg(1, 0, GlobalPrompt.ShenshumijingOneMinuteReady)
	
def Begin():
	#开始培养阶段
	global IsStart
	if IsStart:
		print 'GE_EXC, Shenshumijing is already start'
	IsStart = True
	
	global S_SceneObj, S_CaijiTick, S_CaijiExpTick, S_ShenshuNpcId, S_UnionRankObj
	
	#初始化场景对象
	S_SceneObj = cSceneMgr.SearchPublicScene(EnumGameConfig.ShenshumijingSceneID)
	if not S_SceneObj:
		print 'GE_EXC, Shenshumijing can not find scene id %s' % EnumGameConfig.ShenshumijingSceneID
	
	#创建神树npc
	shenshuNpc = S_SceneObj.CreateNPC(*EnumGameConfig.ShenshumijingShenshuNpcType)
	S_ShenshuNpcId = shenshuNpc.GetNPCID()
	
	#初始化公会排行榜对象
	S_UnionRankObj = UnionRank()
	
	#每15秒给一次经验
	S_CaijiExpTick = cComplexServer.RegTick(EnumGameConfig.ShenshumijingIncExpTime, ExpInc, None)
	#每3分钟刷一波采集怪
	S_CaijiTick = cComplexServer.RegTick(EnumGameConfig.ShenshumijingCaijiTime, BrushCaijiNpc, None)
	
	cComplexServer.RegTick(14*60, BeginGuardTips, None)
	#15分钟后开始守卫阶段
	cComplexServer.RegTick(EnumGameConfig.ShenshumijingGuardEndTime, BeginGuard, None)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.ShenshumijingBegin)
	
def ExpInc(callargv, regparam):
	#给经验
	global S_SceneObj, S_CaijiExpTick, IsGuard
	
	if IsGuard: return
	
	SSG = ShenshumijingConfig.ShenshuIncExp_Dict.get
	SSRG = ShenshumijingConfig.ShenshuRMBInc_Dict.get
	shenshuLevel = WorldData.WD.get(EnumSysData.ShenshuLevel, 1)
	
	#场景内所有玩家+exp
	with ShenshumijingTimeExp_Log:
		for role in S_SceneObj.GetAllRole():
			cfg = SSG(role.GetLevel())
			if not cfg:
				print 'GE_EXC, Shenshumijing ExpInc can not find role level %s' % role.GetLevel()
				continue
			#YY防沉迷对奖励特殊处理
			yyAntiFlag = role.GetAnti()
			if yyAntiFlag == 1:
				exp = cfg.incExp_fcm.get(shenshuLevel)
			elif yyAntiFlag == 0:
				exp = cfg.incExp.get(shenshuLevel)
			else:
				exp = 0
				role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
				continue
			
			if not exp:
				print 'GE_EXC,Shenshumijing ExpInc can not find exp by role level %s, shenshu level %s' % (role.GetLevel(), shenshuLevel)
				continue
			incLevel = role.GetDI8(EnumDayInt8.ShenshuRMBInc)
			cfg = SSRG(incLevel)
			if cfg:
				exp = (10000 + cfg.coef) * exp / 10000
			role.IncExp(exp)
	
	#注册下一个tick
	S_CaijiExpTick = cComplexServer.RegTick(EnumGameConfig.ShenshumijingIncExpTime, ExpInc, None)
	
def BrushCaijiNpc(callargv, regparam):
	#开始刷采集npc
	global S_SceneObj, S_CaijiNpcPosSet, S_CaijiTick, S_CaijiNpcDict, IsGuard
	
	if IsGuard: return
	
	#计算npc索引
	posIndexList = list(ShenshumijingConfig.ShenshuCaijiPos_Set - S_CaijiNpcPosSet)
	if len(posIndexList) < EnumGameConfig.ShenshumijingCaijiNpcCnt:
		print 'GE_EXC, Shenshumijing BrushCaijiNpc pos less'
		return
	posList = random.sample(posIndexList, EnumGameConfig.ShenshumijingCaijiNpcCnt)
	
	#创建npc
	SSG = ShenshumijingConfig.ShenshuCaijiNpc_Dict.get
	for posIndex in posList:
		cfg = SSG(posIndex)
		if not cfg:
			print 'GE_EXC, Shenshumijing BrushCaijiNpc can not find pos %s cfg' % posIndex
			continue
		npc = S_SceneObj.CreateNPC(cfg.npcType, cfg.pos[0], cfg.pos[1], cfg.pos[2], 1)
		npc.SetPyDict(EnumCaijiPosIndex, posIndex)
		npc.SetPyDict(EnumCaijiCnt, cfg.caijiCnt)
		npc.SetPyDict(EnumCaijiReward, cfg.items)
		npc.SetPyDict(EnumCaijiReward_fcm, cfg.items_fcm)
		npc.SetPyDict(EnumCaijiIsrumor, cfg.isRumor)
		S_CaijiNpcDict[npc.GetNPCID()] = npc
		S_CaijiNpcPosSet.add(posIndex)
	
	#注册下一个tick
	S_CaijiTick = cComplexServer.RegTick(EnumGameConfig.ShenshumijingCaijiTime, BrushCaijiNpc, None)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.ShenshumijingBrushCaiji)
	
def BeginGuardTips(callargv, regparam):
	cRoleMgr.Msg(1, 0, GlobalPrompt.ShenshumijingBeforeBG)
	
def BeginGuard(callargv, regparam):
	#开始守卫阶段
	global IsGuard
	if IsGuard:
		print 'GE_EXC, Shenshumijing is already start guard'
	IsGuard = True
	
	global S_CaijiExpTick, S_CaijiTick
	#取消给经验tick
	cComplexServer.UnregTick(S_CaijiExpTick)
	#取消刷怪tick
	cComplexServer.UnregTick(S_CaijiTick)
	S_CaijiExpTick = None
	S_CaijiTick = None
	
	#清理全部采集npc
	global S_CaijiNpcDict, S_CaijiNpcPosSet, S_GuardNpcCnt, S_GuardNpcTotalCnt, S_PeiyangCnt
	for npc in S_CaijiNpcDict.values():
		npc.Destroy()
	S_CaijiNpcDict = {}
	S_CaijiNpcPosSet = set()
	S_GuardNpcCnt = 0
	S_GuardNpcTotalCnt = 0
	
	S_GuardNpcCnt = S_GuardNpcTotalCnt = ShenshumijingConfig.ShenshuGuardNpcCnt_Dict.get(GetCloseValue(S_PeiyangCnt, ShenshumijingConfig.ShenshuGuardNpcCnt_List), 0)
	if not S_GuardNpcCnt:
		print 'GE_EXC, Shenshumijing BeginGuard can not cal guard npc cnt by peiyang cnt %s' % S_PeiyangCnt
		return
	
	#计算位置
	if len(ShenshumijingConfig.ShenshuGuardPos_Set) < S_GuardNpcCnt:
		print 'GE_EXC, Shenshumijing BeginGuard npc cnt error %s' % S_GuardNpcCnt
		return
	#随机npc位置
	global S_GuardNpcPosSet
	SSG = ShenshumijingConfig.ShenshuGuardNpc_Dict.get
	posIndexList = random.sample(list(ShenshumijingConfig.ShenshuGuardPos_Set), S_GuardNpcCnt)
	#创建npc
	for posIndex in posIndexList:
		cfg = SSG(posIndex)
		if not cfg:
			print 'GE_EXC, Shenshumijing BeginGuard can not find pos %s' % posIndex
			continue
		npc = S_SceneObj.CreateNPC(cfg.npcType, cfg.pos[0], cfg.pos[1], cfg.pos[2], 0)
		npc.SetPyDict(EnumGuardPosIndex, posIndex)
		npc.SetPyDict(EnumGuardInFight, False)
		npc.SetPyDict(EnumGuardNpcCfg, (cfg.npcType, cfg.pos[0], cfg.pos[1], cfg.pos[2], cfg.mcid))
		
		S_GuardNpcPosSet.add(posIndex)
	
	#15s同步一次面板信息
	cComplexServer.RegTick(EnumGameConfig.ShenshumijingSyncPanelTime, SyncPanel, None)
	#一分钟后开始刷怪
	cComplexServer.RegTick(EnumGameConfig.ShenshumijingNextGuardTime, NextWave, None)
	#15分钟后结束
	cComplexServer.RegTick(EnumGameConfig.ShenshumijingGuardEndTime, End, None)
	
	#通知客户端
	global S_GuardWave, S_PersonKill_Dict, S_UnionRankObj
	S_GuardWave = 1
	for role in S_SceneObj.GetAllRole():
		role.SendObj(ShenshumijingMonsterData, (S_GuardWave, S_PersonKill_Dict.get(role.GetRoleID(), 0), S_GuardNpcTotalCnt))
		role.SendObj(ShenshumijingUnionData, S_UnionRankObj.getSyncRank())
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.ShenshumijingBrushGuard)
	
def SyncPanel(callargv, regparam):
	#同步面板信息
	global S_SceneObj, IsGuard, S_GuardWave, S_PersonKill_Dict, S_GuardNpcTotalCnt, S_UnionRankObj
	
	if not IsGuard: return
	
	for role in S_SceneObj.GetAllRole():
		role.SendObj(ShenshumijingMonsterData, (S_GuardWave, S_PersonKill_Dict.get(role.GetRoleID(), 0), S_GuardNpcTotalCnt))
		role.SendObj(ShenshumijingUnionData, S_UnionRankObj.getSyncRank())
	
	cComplexServer.RegTick(EnumGameConfig.ShenshumijingSyncPanelTime, SyncPanel, None)
	
def BeforeGuardTips(callargv, regparam):
	#守卫提示
	cRoleMgr.Msg(1, 0, GlobalPrompt.ShenshumijingBeforeBG)
	
def FirstWave(callargv, regparam):
	#根据培养人数计算守卫npc个数
	global S_PeiyangCnt, S_GuardNpcCnt, S_GuardNpcTotalCnt
	S_GuardNpcCnt = S_GuardNpcTotalCnt = ShenshumijingConfig.ShenshuGuardNpcCnt_Dict.get(GetCloseValue(S_PeiyangCnt, ShenshumijingConfig.ShenshuGuardNpcCnt_List), 0)
	if not S_GuardNpcCnt:
		print 'GE_EXC, Shenshumijing BeginGuard can not cal guard npc cnt by peiyang cnt %s' % S_PeiyangCnt
		return
	
	#计算位置
	if len(ShenshumijingConfig.ShenshuGuardPos_Set) < S_GuardNpcCnt:
		print 'GE_EXC, Shenshumijing BeginGuard npc cnt error %s' % S_GuardNpcCnt
		return
	#随机npc位置
	global S_GuardNpcPosSet
	SSG = ShenshumijingConfig.ShenshuGuardNpc_Dict.get
	posIndexList = random.sample(list(ShenshumijingConfig.ShenshuGuardPos_Set), S_GuardNpcCnt)
	#创建npc
	for posIndex in posIndexList:
		cfg = SSG(posIndex)
		if not cfg:
			print 'GE_EXC, Shenshumijing BeginGuard can not find pos %s' % posIndex
			continue
		npc = S_SceneObj.CreateNPC(cfg.npcType, cfg.pos[0], cfg.pos[1], cfg.pos[2], 0)
		npc.SetPyDict(EnumGuardPosIndex, posIndex)
		npc.SetPyDict(EnumGuardInFight, False)
		npc.SetPyDict(EnumGuardNpcCfg, (cfg.npcType, cfg.pos[0], cfg.pos[1], cfg.pos[2], cfg.mcid))
		
		S_GuardNpcPosSet.add(posIndex)
	
	#通知客户端
	global S_GuardWave, S_PersonKill_Dict, S_UnionRankObj
	for role in S_SceneObj.GetAllRole():
		role.SendObj(ShenshumijingMonsterData, (S_GuardWave, S_PersonKill_Dict.get(role.GetRoleID(), 0), S_GuardNpcTotalCnt))
		role.SendObj(ShenshumijingUnionData, S_UnionRankObj.getSyncRank())
	
	cComplexServer.RegTick(EnumGameConfig.ShenshumijingGuardBeforeTipsTime, BeforeGuardTips, None)
	cComplexServer.RegTick(EnumGameConfig.ShenshumijingNextGuardTime, NextWave, None)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.ShenshumijingBrushGuard)
	
def NextWave(callargv, regparam):
	#下一波守卫
	global S_GuardWave, IsGuard
	
	if not IsGuard: return
	
	if S_GuardWave >= EnumGameConfig.ShenshumijingMaxGuardWave:
		return
	
	S_GuardWave += 1
	
	#计算位置
	global S_GuardNpcPosSet, S_GuardNpcTotalCnt, S_PersonKill_Dict
	guardPosSet = ShenshumijingConfig.ShenshuGuardPos_Set - S_GuardNpcPosSet
	if guardPosSet:
		#这里不判断数量了, 还有空位置就刷, 没有就不刷了
		SSG = ShenshumijingConfig.ShenshuGuardNpc_Dict.get
		if len(guardPosSet) < S_GuardNpcCnt:
			posIndexList = random.sample(list(guardPosSet), len(guardPosSet))
		else:
			posIndexList = random.sample(list(guardPosSet), S_GuardNpcCnt)
		
		for posIndex in posIndexList:
			cfg = SSG(posIndex)
			if not cfg:
				print 'GE_EXC, Shenshumijing BeginGuard can not find pos %s' % posIndex
				continue
			npc = S_SceneObj.CreateNPC(cfg.npcType, cfg.pos[0], cfg.pos[1], cfg.pos[2], 0)
			npc.SetPyDict(EnumGuardPosIndex, posIndex)
			npc.SetPyDict(EnumGuardInFight, False)
			npc.SetPyDict(EnumGuardNpcCfg, (cfg.npcType, cfg.pos[0], cfg.pos[1], cfg.pos[2], cfg.mcid))
			
			S_GuardNpcPosSet.add(posIndex)
			S_GuardNpcTotalCnt += 1
			
		for role in S_SceneObj.GetAllRole():
			role.SendObj(ShenshumijingMonsterData, (S_GuardWave, S_PersonKill_Dict.get(role.GetRoleID(), 0), S_GuardNpcTotalCnt))
		
	#1分钟后下一波
	cComplexServer.RegTick(EnumGameConfig.ShenshumijingNextGuardTime, NextWave, None)
	
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.ShenshumijingBrushGuard)
	
def GetCloseValue(value, valueList):
	tmpV = 0
	for i in valueList:
		if i > value:
			return tmpV
		tmpV = i
	return tmpV
	
def End(callargv, regparam):
	global IsStart, IsGuard
	if not IsStart:
		print 'GE_EXC, Shenshumijing is already end'
	IsStart = False
	if not IsGuard:
		print 'GE_EXC, Shenshumijing guard is already end'
	IsGuard = False
	
	#剩余npc个数
	global S_GuardNpcTotalCnt
	
	isSuccess = False
	
	decScore = S_GuardNpcTotalCnt * EnumGameConfig.ShenshumijingGuardScore
	nowLevel = WorldData.GetShenshuLevel()
	nowExp = WorldData.GetShenshuExp()
	
	if not decScore:
		isSuccess = True
	
	#扣神树经验
	if decScore < nowExp:
		nowExp -= decScore
	else:
		decScore -= nowExp
		nowExp = 0
		while decScore:
			cfg = ShenshumijingConfig.ShenshuLevel_Dict.get(nowLevel)
			if not cfg:
				print 'GE_EXC, Shenshumijing End can not get shenshu level %s' % nowLevel
				break
			if cfg.lastLevel == -1:
				nowExp = 0
				break
			cfg = ShenshumijingConfig.ShenshuLevel_Dict.get(cfg.lastLevel)
			if not cfg:
				print 'GE_EXC, Shenshumijing End can not get last shenshu level %s' % cfg.lastLevel
				break
			nowLevel = cfg.level
			if cfg.needExp > decScore:
				nowExp = cfg.needExp - decScore
				break
			elif cfg.lastLevel == -1:
				nowExp = 0
				break
			else:
				decScore -= cfg.needExp
	
	S_GuardNpcTotalCnt = 0
	
	#清理数据
	global S_GuardNpcCnt, S_GuardNpcPosSet, S_GuardWave, S_PeiyangCnt
	S_GuardNpcCnt = 0
	S_GuardWave = 0
	S_PeiyangCnt = 0
	S_GuardNpcPosSet = set()
	
	#扣神树经验
	WorldData.SetShenshuExp(nowExp)
	WorldData.SetShenshuLevel(nowLevel)
	
	#清理场景内所有npc
	global S_SceneObj, S_ShenshuNpcId
	for npc in S_SceneObj.GetAllNPC():
		npc.Destroy()
	S_ShenshuNpcId = None
	
	#公会击杀排名
	global S_UnionRankObj
	unionKillData = S_UnionRankObj.getSyncRank().items()
	unionKillData.sort(key = lambda x : (x[1][1], x[1][2], x[0]), reverse=True)
	#公会击杀奖励
	with ShenshumijingUnionReward_Log:
		for rank, data in enumerate(unionKillData):
			rank += 1
			cfg = ShenshumijingConfig.ShenshuUnionReward_Dict.get(rank)
			if not cfg:
				continue
			unionId = data[0]
			if unionId not in S_UnionRankObj.unionRoleDict:
				print 'GE_EXC, Shenshumijing End can not find union id %s in S_UnionRankObj.unionRoleDict' % unionId
				continue
			for roleId in S_UnionRankObj.unionRoleDict[unionId]:
				Mail.SendMail(roleId, GlobalPrompt.ShenshumijingMail_Title, GlobalPrompt.ShenshumijingMail_Sender, GlobalPrompt.ShenshumijingMail_Content % rank, items=cfg.rewardItems)
	S_UnionRankObj = None
	
	#守卫成功奖励
	global S_PersonKill_Dict
	with ShenshumijingSuccessReward_Log:
		if isSuccess:
			for roleId in S_PersonKill_Dict:
				if not S_PersonKill_Dict[roleId]:
					continue
				Mail.SendMail(roleId, GlobalPrompt.ShenshumijingSucMail_Title, GlobalPrompt.ShenshumijingMail_Sender, GlobalPrompt.ShenshumijingSucMail_Content, items=EnumGameConfig.ShenshumijingSucItems)
			cRoleMgr.Msg(1, 0, GlobalPrompt.ShenshumijingSuccess)
		else:
			cRoleMgr.Msg(1, 0, GlobalPrompt.ShenshumijingFail % decScore)
	S_PersonKill_Dict = {}
	
	cComplexServer.RegTick(60, ClearRole, None)
	
	cRoleMgr.Msg(1, 0, GlobalPrompt.ShenshumijingClearRole)
	
def ClearRole(callargv, regparam):
	#清退所有玩家
	global S_SceneObj
	for role in S_SceneObj.GetAllRole():
		role.BackPublicScene()
	S_SceneObj = None
	
#===============================================================================
# 场景
#===============================================================================
@PublicScene.RegSceneAfterJoinRoleFun(EnumGameConfig.ShenshumijingSceneID)
def AfterJoin(scene, role):
	Status.ForceInStatus(role, EnumInt1.ST_Shenshumijing)
	
	global S_PeiyangCnt, IsGuard, S_GuardWave, S_PersonKill_Dict, S_GuardNpcTotalCnt, S_UnionRankObj
	roleId, unionObj = role.GetRoleID(), role.GetUnionObj()
	
	if unionObj:
		S_UnionRankObj.addUnion(unionObj.union_id, unionObj.name, unionObj.GetZDL())
		S_UnionRankObj.addRole(unionObj.union_id, roleId)
	
	if roleId not in S_PersonKill_Dict:
		S_PersonKill_Dict[roleId] = 0
	
	if IsGuard:
		role.SendObj(ShenshumijingMonsterData, (S_GuardWave, S_PersonKill_Dict.get(roleId, 0), S_GuardNpcTotalCnt))
		role.SendObj(ShenshumijingUnionData, S_UnionRankObj.getSyncRank())
	else:
		role.SendObj(ShenshumijingPeiyangCnt, S_PeiyangCnt)
	
	global S_ShenshuNpcId
	role.SendObj(ShenshumijingShenshuNpcId, S_ShenshuNpcId)

@PublicScene.RegSceneBeforeLeaveFun(EnumGameConfig.ShenshumijingSceneID)
def BeforeLeave(scene, role):
	Status.Outstatus(role, EnumInt1.ST_Shenshumijing)
	
	#处理采集tick
	global S_CaijiTick_Dict
	roleId = role.GetRoleID()
	tickId = S_CaijiTick_Dict.get(roleId)
	if tickId:
		role.UnregTick(tickId)
		del S_CaijiTick_Dict[roleId]
	
	#处理组队
	team = role.GetTeam()
	if not team:
		return
	#离开队伍
	team.Quit(role)
#===============================================================================
# 客户端请求
#===============================================================================
def RequestJoin(role, msg):
	'''
	神树密境进入
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart: return
	
	if role.GetLevel() < EnumGameConfig.ShenshumijingLevel:
		return
	if role.GetSceneID() == EnumGameConfig.ShenshumijingSceneID:
		return
	if not Status.CanInStatus(role, EnumInt1.ST_Shenshumijing):
		return
	
	#随机一个坐标
	minX, minY, maxX, maxY = EnumGameConfig.ShenshumijingJoinRegion
	role.Revive(EnumGameConfig.ShenshumijingSceneID, random.randint(minX, maxX), random.randint(minY, maxY))
	#激情活动奖励狂翻倍 任务进度
	Event.TriggerEvent(Event.Eve_PassionMultiRewardTask, role, (EnumGameConfig.PassionMulti_Task_ShenShuMiJing, True))
	#元旦金猪活动任务进度
	Event.TriggerEvent(Event.Eve_NewYearDayPigTask, role, (EnumGameConfig.NewYearDay_Task_ShenShuMiJing, True))
	
	
def RequestLeave(role, msg):
	'''
	神树密境离开
	@param role:
	@param msg:
	'''
	if role.GetSceneID() != EnumGameConfig.ShenshumijingSceneID:
		return
	
	if Status.IsInStatus(role, EnumInt1.ST_FightStatus):
		return
	
	role.BackPublicScene()
	
def RequestPeiyang(role, msg):
	'''
	神树密境培养
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart or IsGuard: return
	
	if role.GetLevel() < EnumGameConfig.ShenshumijingLevel:
		return
	if role.GetSceneID() != EnumGameConfig.ShenshumijingSceneID:
		return
	if role.GetDI1(EnumDayInt1.ShenshuPeiyang):
		return
	if not WorldData.WD.returnDB:
		return
	
	level = WorldData.WD.get(EnumSysData.ShenshuLevel, 1)
	
	cfg = ShenshumijingConfig.ShenshuLevel_Dict.get(level)
	if not cfg:
		print 'GE_EXC, Shenshumijing peiyang can not find shenshu level %s' % WorldData.WD.get(EnumSysData.ShenshuLevel, 1)
		return
	if cfg.nextLevel == -1:
		#不能培养了, 但是还是要给玩家完成每日必做
		with ShenshumijingPeiyang_Log:
			role.SetDI1(EnumDayInt1.ShenshuPeiyang, True)
		Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_ShenshumijingPeiyang, 1))
		role.SendObj(ShenshumijingPeiyangSec, cDateTime.Seconds() + 4)
		return
	
	with ShenshumijingPeiyang_Log:
		role.SetDI1(EnumDayInt1.ShenshuPeiyang, True)
		
		Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_ShenshumijingPeiyang, 1))
	
	#4s采集时间
	role.RegTick(4, PeiyangTips, None)
	role.SendObj(ShenshumijingPeiyangSec, cDateTime.Seconds() + 4)
	
def PeiyangTips(role, callargv, regparam):
	global S_PeiyangCnt, S_SceneObj
	
	level = WorldData.WD.get(EnumSysData.ShenshuLevel, 1)
	exp = WorldData.WD.get(EnumSysData.ShenshuExp, 0)
	
	cfg = ShenshumijingConfig.ShenshuLevel_Dict.get(level)
	if not cfg:
		print 'GE_EXC, Shenshumijing peiyang can not find shenshu level %s' % WorldData.WD.get(EnumSysData.ShenshuLevel, 1)
		return
	if cfg.nextLevel == -1:
		return
	
	if exp >= cfg.needExp:
		if cfg.nextLevel == -1:
			return
		else:
			WorldData.SetShenshuLevel(cfg.nextLevel)
			WorldData.SetShenshuExp(0)
	else:
		WorldData.SetShenshuExp(exp+1)
	S_PeiyangCnt += 1
	
	cNetMessage.PackPyMsg(ShenshumijingPeiyangCnt, S_PeiyangCnt)
	for tRole in S_SceneObj.GetAllRole():
		tRole.BroadMsg()
	
	role.Msg(2, 0, GlobalPrompt.ShenshumijingPeiyangTips)
	
def RequestRMBInc(role, msg):
	'''
	神树密境神石增益
	@param role:
	@param msg:
	'''
	global IsStart
	if not IsStart or IsGuard: return
	
	if role.GetLevel() < EnumGameConfig.ShenshumijingLevel:
		return
	if role.GetSceneID() != EnumGameConfig.ShenshumijingSceneID:
		return
	incCnt = role.GetDI8(EnumDayInt8.ShenshuRMBInc)
	if incCnt >= EnumGameConfig.ShenshumijingMaxRMBIncLv:
		return
	
	cfg = ShenshumijingConfig.ShenshuRMBInc_Dict.get(incCnt)
	if not cfg:
		print 'GE_EXC, Shenshumijing RMB inc can not find incCnt %s' % incCnt
		return
	
	if cfg.nextGrade == -1:
		return
	if role.GetUnbindRMB() < cfg.needRMB:
		return
	
	with ShenshumijingUseRmb_Log:
		role.DecUnbindRMB(cfg.needRMB)
		role.IncDI8(EnumDayInt8.ShenshuRMBInc, 1)
	
def RequestCaijiFail(role, msg):
	'''
	神树密境采集失败
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.ShenshumijingLevel:
		return
	if role.GetSceneID() != EnumGameConfig.ShenshumijingSceneID:
		return
	
	global S_CaijiTick_Dict
	roleId = role.GetRoleID()
	
	tickId = S_CaijiTick_Dict.get(roleId)
	if not tickId:
		return
	del S_CaijiTick_Dict[roleId]
	
	role.UnregTick(tickId)
	
def RequestOpenTeamPanel(role, msg):
	'''
	神树密境打开组队面板
	@param role:
	@param msg:
	'''
	sendList = []
	for team in TeamBase.SHENSHUMIJING_LIST:
		if team.leader.IsKick():
			continue
		#队伍是否正在战斗中
		if Status.IsInStatus(team.leader, EnumInt1.ST_FightStatus):
			continue
		#队伍ID，队长头像(性别, 职业, 进阶)，队长名，队伍人数
		sendList.append((team.team_id, team.leader.GetSex(), team.leader.GetCareer(), team.leader.GetGrade(), team.leader.GetRoleName(), len(team.members)))
	role.SendObj(ShenshumijingSynOpenData, sendList)
	
def RequestCanInviteData(role, msg):
	'''
	神树密境请求可邀请玩家数据
	@param role:
	@param msg:
	'''
	ES = EnumGameConfig.ShenshumijingLevel
	if role.GetLevel() < ES:
		return
	team = role.GetTeam()
	if not team or team.team_type != EnumTeamType.T_Shenshumijing:
		return
	
	unionObj = role.GetUnionObj()
	roleId = role.GetRoleID()
	
	sendRoleSet = set()
	CF = cRoleMgr.FindRoleByRoleID
	sendList = []
	if unionObj:
		for memberId in unionObj.members.iterkeys():
			#玩家是否在线
			member = CF(memberId)
			if not member:
				continue
			#等级是否满足
			level = member.GetLevel()
			if level < ES:
				continue
			#不用显示自己
			if memberId == roleId:
				continue
			#公会成员是否有队伍
			if memberId in TeamBase.ROLEID_TO_TEAM:
				continue
			if memberId in sendRoleSet:
				continue
			sendRoleSet.add(memberId)
			#roleId, 成员名, 成员等级
			sendList.append((memberId, member.GetRoleName(), level))
	
	#获取好友
	FriendDict = role.GetObj(EnumObj.Social_Friend)
	for friendRoleId, friendRoleData in FriendDict.iteritems():
		fRole = CF(friendRoleId)
		if not fRole:
			continue
		level = fRole.GetLevel()
		if level < ES:
			continue
		if friendRoleId == roleId:
			continue
		if friendRoleId in TeamBase.ROLEID_TO_TEAM:
			continue
		if friendRoleId in sendRoleSet:
				continue
		sendRoleSet.add(friendRoleId)
		sendList.append((friendRoleId, friendRoleData.get(12, ''), level))
		
	#同步客户端
	role.SendObj(ShenshumijingCanInviteData, sendList)
	
def RequestChangeFightHero(role, msg):
	'''
	修改神树密境战斗时上阵的英雄
	@param role:
	@param msg:
	'''
	#直接用了组队跨服竞技的
	heroId = msg
	hero = role.GetHero(heroId)
	if not hero or not hero.GetStationID():
		return
	if role.GetI64(EnumInt64.JTHeroID) == heroId:
		return
	team = role.GetTeam()
	if not team:
		return
	if team.team_type != EnumTeamType.T_Shenshumijing:
		return
	role.SetI64(EnumInt64.JTHeroID, heroId)
	
def RequestAutoAcceptInvite(role, msg):
	'''
	神树密境自动接受组队
	@param role:
	@param msg:
	'''
	if role.GetLevel() < EnumGameConfig.ShenshumijingLevel:
		return
	
	if role.GetI1(EnumInt1.ShenshuAutoAcceptInvite):
		role.SetI1(EnumInt1.ShenshuAutoAcceptInvite, 0)
	else:
		role.SetI1(EnumInt1.ShenshuAutoAcceptInvite, 1)
	
def InitClickFun():
	#采集npc点击函数
	for npc_type in ShenshumijingConfig.ShenshuCaijiNpc_Set:
		NPCServerFun.RegNPCServerOnClickFunEx(npc_type, ClickCaijiNpc)
	#守卫npc点击函数
	for npc_type in ShenshumijingConfig.ShenshuGuardNpc_Set:
		NPCServerFun.RegNPCServerOnClickFunEx(npc_type, ClickGuardNpc)
	
def ClickGuardNpc(role, npc):
	npcDict = npc.GetPyDict()
	
	npcInFight = npcDict.get(EnumGuardInFight)
	if npcInFight:
		role.Msg(2, 0, GlobalPrompt.ShenshumijingInFight)
		return
	
	npcPosIndex = npcDict.get(EnumGuardPosIndex)
	npcType, npcPosX, npcPosY, direct, npcMcid = npcDict.get(EnumGuardNpcCfg)
	
	team = role.GetTeam()
	global S_SceneObj
	
	if team:
		if team.team_type != EnumTeamType.T_Shenshumijing:
			return
		if role.GetRoleID() != team.leader.GetRoleID():
			return
		if not Status.CanInStatus_Roles(team.members, EnumInt1.ST_FightStatus):
			return
		
		for role in team.members:
			if role.GetI64(EnumInt64.JTHeroID):
				continue
			RandomHero(role)
		
		#删除旧的npc
		npc.Destroy()
		#创建一个新的npc
		npc = S_SceneObj.CreateNPC(npcType, npcPosX, npcPosY, direct, 1, {EnumNPCData.EnNPC_Statu : EnumRoleStatus.GT_NPC})
		npc.SetPyDict(EnumGuardPosIndex, npcPosIndex)
		npc.SetPyDict(EnumGuardInFight, True)
		npc.SetPyDict(EnumGuardNpcCfg, (npcType, npcPosX, npcPosY, direct, npcMcid))
		
		PVE_Team(role, team.members, EnumGameConfig.ShenshumijingTeamFightType, npcMcid, AfterPveTeamFight, npc)
	else:
		if not Status.CanInStatus(role, EnumInt1.ST_FightStatus):
			return
		
		#删除旧的npc
		npc.Destroy()
		#创建一个新的npc
		npc = S_SceneObj.CreateNPC(npcType, npcPosX, npcPosY, direct, 1, {EnumNPCData.EnNPC_Statu : EnumRoleStatus.GT_NPC})
		npc.SetPyDict(EnumGuardPosIndex, npcPosIndex)
		npc.SetPyDict(EnumGuardInFight, True)
		npc.SetPyDict(EnumGuardNpcCfg, (npcType, npcPosX, npcPosY, direct, npcMcid))
		
		#单人战斗
		PVE(role, EnumGameConfig.ShenshumijingFightType, npcMcid, AfterPveFight, npc)
	
def RandomHero(role):
	sm = role.GetTempObj(EnumTempObj.enStationMgr)
	if len(sm.station_to_id) < 2:
		return
	for heroId in sm.station_to_id.itervalues():
		if heroId == role.GetRoleID():
			continue
		role.SetI64(EnumInt64.JTHeroID, heroId)
	
def PVE_Team(leaderRole, fightRoleList, fightType, mcid, AfterFight, regParam, OnLeave=None, AfterPlay=None):
	fight = Fight.Fight(fightType)
	fight.restore = False
	fight.group_need_hero = True
	left_camp, right_camp = fight.create_camp()
	
	for index, fightRole in enumerate(fightRoleList):
		left_camp.create_online_role_unit(fightRole, fightRole.GetRoleID(), use_px = True, role_realfight_pos = index + 1)
	
	right_camp.create_monster_camp_unit(mcid)

	fight.on_leave_fun = OnLeave			#角色离开战斗回调（战斗结束或者超长时间掉线触发）
	fight.after_fight_fun = AfterFight		#战斗结束（所有的在线角色一定已经离场了）
	fight.after_play_fun = AfterPlay		#客户端播放完毕（一定在战斗结束后触发）
	fight.after_fight_param = regParam

	fight.start()
	
def AfterPveTeamFight(fightObj):
	if fightObj.result is None:
		print "GE_EXC, Shenshumijing fight with monster error"
		return
	#活动结束了, 不处理
	global IsGuard
	if not IsGuard: return
	
	npc = fightObj.after_fight_param
	npcDict = npc.GetPyDict()
	posIndex = npcDict.get(EnumGuardPosIndex)
	npcType, npcPosX, npcPosY, direct, mcid = npcDict.get(EnumGuardNpcCfg)
	
	if not posIndex:
		print 'GE_EXC, Shenshumijing AfterPveFight get error posIndex %s' % posIndex
		return
	
	cfg = ShenshumijingConfig.ShenshuGuardNpc_Dict.get(posIndex)
	if not cfg:
		print 'GE_EXC, Shenshumijing AfterPveFight get cfg posIndex %s' % posIndex
		return
	
	randomObj = ShenshumijingConfig.ShenshuGuardNpcRandom_Dict.get(posIndex)
	if not randomObj:
		print 'GE_EXC, Shenshumijing AfterPveFight get randomObj posIndex %s' % posIndex
		return
		
	if fightObj.result == 1:
		roles = fightObj.left_camp.roles
		if not roles:
			return
		global S_UnionRankObj, S_PersonKill_Dict, S_GuardNpcTotalCnt, S_GuardNpcPosSet, S_GuardWave
		S_GuardNpcPosSet.discard(posIndex)
		S_GuardNpcTotalCnt -= 1
		
		#胜利删除npc
		npc.Destroy()
		
		with ShenshumijingGuard_Log:
			for role in roles:
				#不在场景中(可能强制离开了战斗状态了)
				if role.GetSceneID() != EnumGameConfig.ShenshumijingSceneID:
					continue
				role.IncExp(cfg.exp)
				item = randomObj.RandomOne()
				if item:
					tips = GlobalPrompt.Reward_Tips
					role.AddItem(*item)
					tips += GlobalPrompt.Item_Tips % item
				unionObj, roleId = role.GetUnionObj(), role.GetRoleID()
				if unionObj:
					S_UnionRankObj.addUnion(unionObj.union_id, unionObj.name, unionObj.GetZDL())
					S_UnionRankObj.addRole(unionObj.union_id, roleId)
				S_UnionRankObj.addKillCnt(role.GetUnionID())
				
				if roleId in S_PersonKill_Dict:
					S_PersonKill_Dict[roleId] += 1
				
				role.SendObj(ShenshumijingMonsterData, (S_GuardWave, S_PersonKill_Dict.get(roleId, 0), S_GuardNpcTotalCnt))
				role.SendObj(ShenshumijingUnionData, S_UnionRankObj.getSyncRank())
				
				role.Msg(2, 0, tips)
	else:
		#失败删除npc
		npc.Destroy()
		
		#创建新npc
		global S_SceneObj
		npc = S_SceneObj.CreateNPC(npcType, npcPosX, npcPosY, direct, 0)
		npc.SetPyDict(EnumGuardPosIndex, posIndex)
		npc.SetPyDict(EnumGuardInFight, False)
		npc.SetPyDict(EnumGuardNpcCfg, (npcType, npcPosX, npcPosY, direct, mcid))
		
def PVE(role, fightType, mcid, AfterPveFight, regParam):
	fight = Fight.Fight(fightType)
	
	left_camp, right_camp = fight.create_camp()
	
	left_camp.create_online_role_unit(role, control_role_id = role.GetRoleID(), use_px = True)
	right_camp.create_monster_camp_unit(mcid)
	fight.after_fight_fun = AfterPveFight
	fight.after_fight_param = regParam
	fight.start()
	
def AfterPveFight(fightObj):
	if fightObj.result is None:
		print "GE_EXC, Shenshumijing fight with monster error"
		return
	#活动结束了, 不处理
	global IsGuard
	if not IsGuard: return
	
	npc = fightObj.after_fight_param
	npcDict = npc.GetPyDict()
	posIndex = npcDict.get(EnumGuardPosIndex)
	npcType, npcPosX, npcPosY, direct, mcid = npcDict.get(EnumGuardNpcCfg)
		
	if fightObj.result == 1:
		roles = fightObj.left_camp.roles
		if not roles:
			return
		role = list(roles)[0]
		
		#不在场景中(可能强制离开了战斗状态了)
		if role.GetSceneID() != EnumGameConfig.ShenshumijingSceneID:
			return
		
		if not posIndex:
			print 'GE_EXC, Shenshumijing AfterPveFight get error posIndex %s' % posIndex
			return
		
		cfg = ShenshumijingConfig.ShenshuGuardNpc_Dict.get(posIndex)
		if not cfg:
			print 'GE_EXC, Shenshumijing AfterPveFight get cfg posIndex %s' % posIndex
			return
		
		randomObj = ShenshumijingConfig.ShenshuGuardNpcRandom_Dict.get(posIndex)
		if not randomObj:
			print 'GE_EXC, Shenshumijing AfterPveFight get randomObj posIndex %s' % posIndex
			return
		
		tips = GlobalPrompt.Reward_Tips
		with ShenshumijingGuard_Log:
			role.IncExp(cfg.exp)
			item = randomObj.RandomOne()
			if item:
				role.AddItem(*item)
				tips += GlobalPrompt.Item_Tips % item
		
		global S_GuardNpcTotalCnt, S_GuardNpcPosSet, S_UnionRankObj, S_PersonKill_Dict, S_GuardWave
		S_GuardNpcPosSet.discard(posIndex)
		S_GuardNpcTotalCnt -= 1
		
		unionObj, roleId = role.GetUnionObj(), role.GetRoleID()
		if unionObj:
			S_UnionRankObj.addUnion(unionObj.union_id, unionObj.name, unionObj.GetZDL())
			S_UnionRankObj.addRole(unionObj.union_id, roleId)
		S_UnionRankObj.addKillCnt(role.GetUnionID())
		
		if roleId in S_PersonKill_Dict:
			S_PersonKill_Dict[roleId] += 1
		
		npc.Destroy()
		
		role.SendObj(ShenshumijingMonsterData, (S_GuardWave, S_PersonKill_Dict.get(roleId, 0), S_GuardNpcTotalCnt))
		role.SendObj(ShenshumijingUnionData, S_UnionRankObj.getSyncRank())
		
		role.Msg(2, 0, tips)
	else:
		#失败删除npc
		npc.Destroy()
		#创建新npc
		global S_SceneObj
		npc = S_SceneObj.CreateNPC(npcType, npcPosX, npcPosY, direct, 0)
		npc.SetPyDict(EnumGuardPosIndex, posIndex)
		npc.SetPyDict(EnumGuardInFight, False)
		npc.SetPyDict(EnumGuardNpcCfg, (npcType, npcPosX, npcPosY, direct, mcid))
	
def ClickCaijiNpc(role, npc):
	global S_CaijiTick_Dict
	roleId = role.GetRoleID()
	
	tickId = S_CaijiTick_Dict.get(roleId)
	if tickId:
		return
	
	team = role.GetTeam()
	if team and team.leader.GetRoleID() != roleId:
		return
	
	sec = cDateTime.Seconds()
	role.SendObj(ShenshumijingCaijiSec, sec + 5)
	
	tickId = role.RegTick(5, AfterCaiji, (npc.GetNPCID(), npc.GetNPCName()))
	
	S_CaijiTick_Dict[roleId] = tickId
	
def AfterCaiji(role, argv, param):
	global S_CaijiNpcDict, S_CaijiTick_Dict
	
	npcId, npcName = param
	roleId = role.GetRoleID()
	
	if roleId in S_CaijiTick_Dict:
		del S_CaijiTick_Dict[roleId]
	
	if role.GetSceneID() != EnumGameConfig.ShenshumijingSceneID:
		return
	
	npc = S_CaijiNpcDict.get(npcId)
	if not npc:
		role.Msg(2, 0, GlobalPrompt.ShenshumijingCaijiFail % npcName)
		return
	
	npcDict = npc.GetPyDict()
	caijiCnt = npcDict.get(EnumCaijiCnt)
	posIndex = npcDict.get(EnumCaijiPosIndex)
	
	if not caijiCnt:
		if npcId in S_CaijiNpcDict:
			del S_CaijiNpcDict[npcId]
		S_CaijiNpcPosSet.discard(posIndex)
		npc.Destroy()
		return
	#YY防沉迷对奖励特殊处理
	yyAntiFlag = role.GetAnti()
	if yyAntiFlag == 1:
		reward = npcDict.get(EnumCaijiReward_fcm)
	elif yyAntiFlag == 0:
		reward = npcDict.get(EnumCaijiReward)
	else:
		reward = ()
		role.Msg(2, 0, GlobalPrompt.YYAntiNoReward)
	
	caijiCnt -= 1
	isRumor = npcDict.get(EnumCaijiIsrumor)
	if not caijiCnt:
		if npcId in S_CaijiNpcDict:
			del S_CaijiNpcDict[npcId]
		S_CaijiNpcPosSet.discard(posIndex)
		npc.Destroy()
	else:
		npc.SetPyDict(EnumCaijiCnt, caijiCnt)
	
	with ShenshumijingCaiji_Log:
		tips = GlobalPrompt.Reward_Tips
		rumorTips = None
		for item in reward:
			role.AddItem(*item)
			if isRumor and not rumorTips:
				rumorTips = GlobalPrompt.ShenshumijingCaijiTips % (role.GetRoleName(), item[0], item[1])
			tips += GlobalPrompt.Item_Tips % item
		role.Msg(2, 0, tips)
	if isRumor and rumorTips:
		cRoleMgr.Msg(1, 0, rumorTips)
	
#===============================================================================
# 事件
#===============================================================================
def BeforeExit(role, param):
	if role.GetSceneID() != EnumGameConfig.ShenshumijingSceneID:
		return
	
	role.BackPublicScene()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and (Environment.EnvIsQQ() or Environment.IsDevelop or Environment.EnvIsFT() or Environment.EnvIsNA() or Environment.EnvIsYY()):
		#国服、繁体开放
		InitClickFun()
		
		Event.RegEvent(Event.Eve_ClientLost, BeforeExit)
		Event.RegEvent(Event.Eve_BeforeExit, BeforeExit)
		
		Cron.CronDriveByMinute((2038, 1, 1), TenMinuteReady, H = "H == 12", M = "M == 50")
		Cron.CronDriveByMinute((2038, 1, 1), OneMinuteReady, H = "H == 12", M = "M == 59")
		Cron.CronDriveByMinute((2038, 1, 1), Begin, H = "H == 13", M = "M == 0")
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Shenshumijing_Join", "神树密境进入"), RequestJoin)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Shenshumijing_Leave", "神树密境离开"), RequestLeave)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Shenshumijing_Peiyang", "神树密境培养"), RequestPeiyang)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Shenshumijing_RMBInc", "神树密境神石增益"), RequestRMBInc)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Shenshumijing_CaijiFail", "神树密境采集失败"), RequestCaijiFail)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Shenshumijing_OpenTeamPanel", "神树密境打开组队面板"), RequestOpenTeamPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Shenshumijing_CanInviteData", "神树密境请求可邀请玩家数据"), RequestCanInviteData)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Shenshumijing_HeroStation", "修改神树密境战斗时上阵的英雄"), RequestChangeFightHero)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Shenshumijing_AutoAcceptInvite", "神树密境自动接受组队"), RequestAutoAcceptInvite)
	
