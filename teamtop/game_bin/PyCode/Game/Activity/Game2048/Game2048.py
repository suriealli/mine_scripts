#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Game2048.Game2048")
#===============================================================================
# 注释 @author: GaoShuai 2015
#===============================================================================
import cProcess
import cRoleMgr
import random
import copy
import cComplexServer
import Environment
from Game.Role import Event
from Game.Role import Rank
from Game.GlobalData import ZoneName
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.Control import ControlProxy
from Common.Message import AutoMessage, PyMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from Game.Role.Data import EnumTempObj, EnumInt8, EnumInt16, EnumDayInt8, EnumObj
from Game.Activity.Game2048.Game2048Config import Game2048_Dict, Game2048StepAndPoint_Dict, Game2048BuyTimes_Dict


if "_HasLoad" not in dir():
	
	GAME2048_TODAY_RANK = []		#宝石2048公会排行榜（今天）
	GAME2048_YESTERDAY_RANK = []	#宝石2048公会排行榜（昨天）
	
	DIRECTION = {1:"left", 2:"right", 3:"up", 4:"down"}
	Game2048Init = AutoMessage.AllotMessage("Game2048Init", "通知客户端2048初始化")
	Game2048Move = AutoMessage.AllotMessage("Game2048Move", "通知客户端2048移动结果")
	Game2048Goal = AutoMessage.AllotMessage("Game2048Goal", "通知客户端2048完成目标")
	Game2048GoalState = AutoMessage.AllotMessage("Game2048GoalState", "通知客户端2048当前目标完成状态")
	Game2048Reward = AutoMessage.AllotMessage("Game2048Reward", "通知客户端2048可领取奖励")
	Game2048ScoreRank = AutoMessage.AllotMessage("Game2048ScoreRank", "通知客户端2048跨服排名")
	
	Tra_Game2048GetReward = AutoLog.AutoTransaction("Tra_Game2048GetReward", "宝石2048领取通过奖励")
	Tra_Game2048BuyTimes = AutoLog.AutoTransaction("Tra_Game2048BuyTimes", "宝石2048购买次数")
	Tra_Game2048Start = AutoLog.AutoTransaction("Tra_Game2048Start", "宝石2048开始游戏")


#===============================================================================
# 排行榜
#===============================================================================
class Game2048Rank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 20						#最大排行榜 20个
	dead_time = (2038, 1, 1)
	
	needSync = False						#不需要同步给客户端 
	#roleId, maxScore, roleName, ZoneName
	name = "GAME2048_SCORE_DICT"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[1] < v2[1]
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		self.changeFlag = True
		
	def AfterLoadFun(self):
		Rank.SmallRoleRank.AfterLoadFun(self)
		TryUpdate()


class Game2048(object):
	def __init__(self, role):
		self.role = role
		if role.GetObj(EnumObj.Game2048Data):
			self.loadData()
			return
		self.initData()
	
	def initData(self):
		self.thisScore = 0					#本次分数
		self.todayMaxscore = 0				#最高分数
		self.todayLastScore = 0				#最后一次得分
		self.point = 0						#完成本目标得分
		self.win = set([])					#已经通关集合
		self.HasGetReward = set()			#已经领奖集合
		self.beginGame = False				#游戏开始的唯一标识
		self.data = [0] * 16				#2048数据
		self.level = 0						#第几关
		self.index = 1						#当前关卡对应index
		self.goal = [0, 0, 0]				#当前目标
	
	def loadData(self):
		Game2048Dict = self.role.GetObj(EnumObj.Game2048Data)
		self.thisScore = Game2048Dict["thisScore"] 
		self.todayMaxscore = Game2048Dict["todayMaxscore"] 
		self.todayLastScore = Game2048Dict["todayLastScore"]
		self.point = Game2048Dict["point"] 
		self.win = Game2048Dict["win"] 
		self.HasGetReward = Game2048Dict["HasGetReward"] 
		self.beginGame = Game2048Dict["beginGame"] 
		self.data = Game2048Dict["data"] 
		self.level = Game2048Dict["level"] 
		self.index = Game2048Dict["index"] 
		self.goal = Game2048Dict["goal"] 
	
	def saveData(self):
		Game2048Dict = {}
		Game2048Dict["thisScore"] = self.thisScore
		Game2048Dict["todayMaxscore"] = self.todayMaxscore
		Game2048Dict["todayLastScore"] = self.todayLastScore
		Game2048Dict["point"] = self.point
		Game2048Dict["win"] = self.win
		Game2048Dict["HasGetReward"] = self.HasGetReward
		Game2048Dict["beginGame"] = self.beginGame
		Game2048Dict["data"] = self.data
		Game2048Dict["level"] = self.level
		Game2048Dict["index"] = self.index
		Game2048Dict["goal"] = self.goal
		self.role.SetObj(EnumObj.Game2048Data, Game2048Dict)
	
	def createGame(self, index):
		#初始化游戏
		Game2048Obj = Game2048_Dict.get(index)
		if not Game2048Obj:
			return
		#判断是否符合游戏开启条件
		for ind in Game2048Obj.needIndex:
			if ind not in self.win:
				return
		self.thisScore = 0
		self.role.IncI8(EnumInt8.Game2048Cnt, 1)	#今日次数+1
		self.index = Game2048Obj.index
		self.goal = copy.copy(Game2048Obj.goal)		#本次目标,防止list引用篡改配置表数据
		self.point = Game2048Obj.point			#完成本目标获得积分
		self.level = Game2048Obj.level			#第几关
		self.goalIndex = Game2048Obj.goalIndex	#第几个目标
		self.role.SetI16(EnumInt16.Game2048Step, Game2048Obj.maxStep)
		
		_i, _j = random.sample([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 2)
		self.data[_i] = 2
		self.data[_j] = 2
		self.beginGame = True
		self.saveData()
		win = 0
		if self.win: 
			win = max(self.win)
		self.role.SendObj(Game2048Init, (self.data, win, self.todayMaxscore, self.todayLastScore, self.level))
	
	
	def OverGame(self):
		#完成目标或通关
		self.goal[2] += 1
		goalIndex = self.data.index(self.goal[0])
		self.data[goalIndex] = 0
		self.role.SendObj(Game2048Goal, (self.data, self.index, goalIndex))
		self.role.SendObj(Game2048GoalState, (self.index, self.goal[2]))
		#如果目标没有全部完成，返回
		if self.goal[2] < self.goal[1]:
			return
		#保存通关记录
		self.win.add(self.index)
		self.thisScore += self.point
		
		if self.win - self.HasGetReward:
			self.role.SendObj(Game2048Reward, (self.win, self.HasGetReward))
		
		Game2048Obj = Game2048_Dict.get(self.index)
		if Game2048Obj.nextIndex:
			Game2048_nextObj = Game2048_Dict.get(Game2048Obj.nextIndex)
			if Game2048_nextObj:
				self.goalIndex = Game2048_nextObj.goalIndex
				self.goal = copy.copy(Game2048_nextObj.goal)
				self.index = Game2048_nextObj.index
				self.point = Game2048_nextObj.point
		else:
			#计算积分,保存上一局分数、今日得分、今日最高分
			leaveStepDict = Game2048StepAndPoint_Dict.get(self.index, {})
			#当前剩余步数对应积分
			pointOneStep = leaveStepDict.get(self.role.GetI16(EnumInt16.Game2048Step), 0)
			self.thisScore += pointOneStep
			self.endGame()
	
	
	def roleDayClear(self):
		#若玩家在玩游戏，自动结束游戏
		if self.beginGame:
			self.role.SendObj(Game2048Move, ([0] * 16, -2))
		self.role.SendObj(Game2048Init, ([0] * 16, 0, 0, 0, 0))
		self.initData()
		self.saveData()
		#每日免费次数
		self.role.SetI8(EnumInt8.Game2048Cnt, 0)
		#剩余步数
		self.role.SetI16(EnumInt16.Game2048Step, 0)
	
	
	def endGame(self):
		#防止多次触发
		if not self.beginGame:
			return
		#当前剩余步数对应积分
		self.todayLastScore = self.thisScore
		self.todayMaxscore = max(self.todayMaxscore, self.thisScore)
		#完成一个目标，需要保存成绩,这里只处理完成目标的正常结束
		G2048.HasData(self.role.GetRoleID(), [self.role.GetRoleID(), self.todayMaxscore, self.role.GetRoleName(), ZoneName.ZoneName])
		
		self.beginGame = False
		self.goal = [0, 0, 0]
		self.data = [0] * 16
		self.point = 0
		self.thisScore = 0
		self.index = 0						#当前关卡对应index
		self.level = 0						#第几关
		self.saveData()
		#剩余步数
		self.role.SetI16(EnumInt16.Game2048Step, 0)
		win = 0
		if self.win:
			win = max(self.win)
		self.role.SendObj(Game2048Init, (self.data, win, self.todayMaxscore, self.todayLastScore, self.level))
	
	
	def move(self, direction):
		#移动
		if not self.beginGame:
			return
		
		result = self.operation(direction)
		
		if result == -1:
			self.role.SendObj(Game2048Move, (self.data, -1))
			return
		#减步数
		self.role.DecI16(EnumInt16.Game2048Step, 1)
		
		if result == -2:
			self.role.SendObj(Game2048Move, (self.data, -2))
			self.endGame()
		else:
			#是否到达目标
			for _ in range(self.goal[2], self.goal[1]):
				if max(self.data) != self.goal[0]:
					break
				self.OverGame()
			self.role.SendObj(Game2048Move, (self.data, result))
		
		self.hasReturn = 0
		if self.role.GetI16(EnumInt16.Game2048Step) <= 0:
			self.role.SendObj(Game2048Move, (self.data, -2))
			self.endGame()
	
	
	def Handle(self, vList, direction):
		#只做一次相加操作，然后向一个方向对齐
		hasChanged = self.Align(vList, direction)
		scoreFlag = self.AddSame(vList, direction)
		if scoreFlag:
			self.Align(vList, direction)
		return (scoreFlag or hasChanged)
	
	
	def operation(self, direction):
		#根据移动方向重新计算矩阵状态值，并记录得分
		changeFlag = False
		if direction in ('left', "right"):
			for row in range(4):
				vList = self.data[row * 4:(row + 1) * 4]
				hasChanged = self.Handle(vList, direction)
				changeFlag |= hasChanged
				self.data[row * 4:(row + 1) * 4] = vList
		elif direction in ('up', "down"):
			for col in range(4):
				vList = self.data[col::4]
				hasChanged = self.Handle(vList, direction)
				changeFlag |= hasChanged
				self.data[col::4] = vList
		else:
			return -1
		if not changeFlag:
			#处理所有无效移动
			return -1
		
		# 统计空白区域数目 N
		N = self.data.count(0)
		if N == 0:
			#所有格子占满是的无效移动会出现 N = 0 情况，出现后按无效移动处理
			return -1
		# 产生随机数k，上一步产生的2将被填到第k个空白区域
		k = random.randrange(1, N + 1)
		ii = -1
		n = 0
		for _i in range(len(self.data)):
			if self.data[_i] == 0:
				n += 1
				if n == k:
					ii = _i
					#当前游戏难度，只产生2
					self.data[_i] = 2
		N = self.data.count(0)
		if self.dead(N):
			ii = -2
		#返回新生成点的位置
		return ii
	
	
	def dead(self, N):
		# 统计空白区域数目 N
		#不存在空白区域
		if N != 0:
			return False
		if N == 0:
			#检查是否有可以合并项
			for _i in range(3):
				for _j in range(4):
					if self.data[_i + _j * 4] == self.data[_i + _j * 4 + 1]:
						return False
					if self.data[_i * 4 + _j] == self.data[(_i + 1) * 4 + _j]:
						return False
		return True
	
	def Align(self, vList, direction):
		'''对齐非零的数字
		direction == 'left'：向左对齐，例如[8,0,0,2]左对齐后[8,2,0,0]
		direction == 'right'：向右对齐，例如[8,0,0,2]右对齐后[0,0,8,2]
		'''
		zeros = -1
		hasChanged = False
		if direction in ('left', "up"):
			for i in range(4):
				if vList[i] == 0 and zeros == -1:
					zeros = i
				elif vList[i] == -1:
					zeros = -1
				elif vList[i] != 0 and zeros != -1:
					vList[zeros] = vList[i]
					vList[i] = 0
					zeros += 1
					hasChanged = True
		else:
			i = 3
			while i >= 0:
				if vList[i] == 0 and zeros == -1:
					zeros = i
				elif vList[i] == -1:
					zeros = -1
				elif vList[i] != 0 and zeros != -1:
					vList[zeros] = vList[i]
					vList[i] = 0
					zeros -= 1
					hasChanged = True
				i -= 1
		return hasChanged
	
	def AddSame(self, vList, direction):
		'''相同数字相加
		direction == 'left'：向左相加，例如[8,2,2,2]左对齐后[8,4,0,2]
		direction == 'right'：向右相加，例如[8,2,2,2]右对齐后[8,2,0,4]
		'''
		scoreFlag = False
		if direction in ('left', 'up'):
			i = 0
			while i < 3:
				if vList[i] == vList[i + 1] != 0: 
					vList[i] *= 2
					vList[i + 1] = 0
					i += 2
					scoreFlag = True
				else:
					i += 1
		else:
			i = 3
			while i > 0:
				if vList[i] == vList[i - 1] != 0:
					vList[i] *= 2
					vList[i - 1] = 0
					i -= 2
					scoreFlag = True
				else:
					i -= 1
		
		return scoreFlag


def Request2048OOpenPanel(role, param):
	'''
	客户端请求2048打开面板
	@param role:
	@param param: 关卡对应索引
	'''
	if role.GetLevel() < EnumGameConfig.Game2048RoleLevel :
		return
	game = role.GetTempObj(EnumTempObj.Game2048)
	if not game:
		print "Cannot find the game obj."
		return
	win = 0
	if game.win:
		win = max(game.win)
	role.SendObj(Game2048Init, (game.data, win, game.todayMaxscore, game.todayLastScore, game.level))
	role.SendObj(Game2048GoalState, (game.index, game.goal[2]))
	#同步排行榜
	global GAME2048_TODAY_RANK
	role.SendObj(Game2048ScoreRank, {1:GAME2048_TODAY_RANK})


def Request2048Start(role, param):
	'''
	客户端请求开始2048游戏
	@param role:
	@param param: 关卡对应索引
	'''
	if role.GetLevel() < EnumGameConfig.Game2048RoleLevel :
		return
	#次数不足
	if role.GetI8(EnumInt8.Game2048Cnt) >= EnumGameConfig.Game2048_FREE_CNT + role.GetDI8(EnumDayInt8.Game2048BuyTimes):
		return
	game = role.GetTempObj(EnumTempObj.Game2048)
	
	if game.beginGame:
		return
	with Tra_Game2048Start:
		game.createGame(param)
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveGame2048Srart, param)


def Request2048Move(role, direction):
	'''
	客户端请求2048游戏移动
	@param role:
	@param msg:
	'''
	if direction not in DIRECTION:
		return
	if role.GetLevel() < EnumGameConfig.Game2048RoleLevel :
		return
	Game2048obj = role.GetTempObj(EnumTempObj.Game2048)
	if role.GetI16(EnumInt16.Game2048Step) <= 0:
		role.SendObj(Game2048Move, (Game2048obj.data, -2))
		return
	
	Game2048obj.move(DIRECTION[direction])


def Request2048Reward(role, param):
	'''
	客户端请求2048领取奖励
	@param role:
	@param param: 奖励index
	'''
	if role.GetLevel() < EnumGameConfig.Game2048RoleLevel :
		return
	game = role.GetTempObj(EnumTempObj.Game2048)
	rewardIndexSet = game.win - game.HasGetReward
	if param not in rewardIndexSet:
		return
	if not rewardIndexSet:
		return
	
	tip = ""
	with Tra_Game2048GetReward:
		
		game.HasGetReward.add(param)
		Game2048ConfigObj = Game2048_Dict.get(param)
		for item, cnt in Game2048ConfigObj.reward:
			role.AddItem(item, cnt)
			tip += GlobalPrompt.Item_Tips % (item, cnt)
			
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveGame2048GetReward, param)
	role.SendObj(Game2048Reward, (game.win, game.HasGetReward))
	if tip:
		role.Msg(2, 0, GlobalPrompt.Reward_Tips + tip)


def Request2048End(role, param):
	'''
	客户端请求2048结束本局
	@param role:
	@param param:
	'''
	if role.GetLevel() < EnumGameConfig.Game2048RoleLevel :
		return
	game = role.GetTempObj(EnumTempObj.Game2048)
	if game == None:
		return
	game.endGame()


def OnRoleDayClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	if not role.GetTempObj(EnumTempObj.Game2048):
		role.SetTempObj(EnumTempObj.Game2048, Game2048(role))
	game = role.GetTempObj(EnumTempObj.Game2048)
	game.roleDayClear()
	OnSyncOtherData(role, None)


def InitGame2048(role, param):
	'''
	Game2048初始化,角色Obj初始化会早于每日清理事件
	@param role:
	@param param:
	'''
	
	role.SetTempObj(EnumTempObj.Game2048, Game2048(role))


def SaveDataGame2048(role, param):
	'''
	Game2048初始化,角色Obj初始化会早于每日清理事件
	@param role:
	@param param:
	'''
	game = role.GetTempObj(EnumTempObj.Game2048)
	game.saveData()



def Request2048BuyTimes(role, param):
	'''
	购买次数
	@param role:
	@param param:
	'''
	if role.GetLevel() < EnumGameConfig.Game2048RoleLevel:
		return
	buyTimes = role.GetDI8(EnumDayInt8.Game2048BuyTimes)
	if buyTimes not in Game2048BuyTimes_Dict:
		return
	needRMB = Game2048BuyTimes_Dict[buyTimes]
	if role.GetUnbindRMB() < needRMB:
		return
	with Tra_Game2048BuyTimes:
		role.DecUnbindRMB(needRMB)
		#每日已购买次数 +1
		role.IncDI8(EnumDayInt8.Game2048BuyTimes, 1)


def Request2048ScoreRank(role, param):
	'''
	请求跨服排行榜
	@param role:
	@param param:
	'''
	if role.GetLevel() < EnumGameConfig.Game2048RoleLevel :
		return
	if param == 1:
		global GAME2048_TODAY_RANK
		role.SendObj(Game2048ScoreRank, {1:GAME2048_TODAY_RANK})
	elif param == 2:
		global GAME2048_YESTERDAY_RANK
		role.SendObj(Game2048ScoreRank, {2:GAME2048_YESTERDAY_RANK})


def OnSyncOtherData(role, param):
	'''
	角色上线同步，同步已经通关和已领取的奖励
	@param role:
	@param param:
	'''
	if role.GetLevel() < EnumGameConfig.Game2048RoleLevel :
		return
	game = role.GetTempObj(EnumTempObj.Game2048)
	role.SendObj(Game2048Reward, (game.win, game.HasGetReward))


#===============================================================================
# 数据载回，服务器启动
#===============================================================================
def TryUpdate():
	'''
	排行榜数据载回来后尝试更新富豪榜
	'''
	ControlProxy.SendControlMsg(PyMessage.Control_RequestControlGame2048Rank, (cProcess.ProcessID, GetLogicRank()))

#===============================================================================
# 服务器启动
#===============================================================================
def ServerUp():
	#起服的时候向控制进程请求跨服排行榜数据
	if not G2048.returnDB:
		return
	ControlProxy.SendControlMsg(PyMessage.Control_RequestControlGame2048Rank, (cProcess.ProcessID, GetLogicRank()))

#===============================================================================
# 
#===============================================================================
def GetLogicRank():
	#返回本地排行榜
	return G2048.data.values()

#===============================================================================
# 控制进程请求
#===============================================================================
def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服得分排行榜
	@param sessionid:
	@param msg:
	'''
	if not G2048.returnDB:
		return
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetLogicRank()))


def OnControlUpdataRank_T(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	global GAME2048_TODAY_RANK
	GAME2048_TODAY_RANK = msg
	

def OnControlUpdataRank(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global GAME2048_TODAY_RANK, GAME2048_YESTERDAY_RANK
	GAME2048_TODAY_RANK, GAME2048_YESTERDAY_RANK = msg


def NewDayClear():
	'''
	本服数据每日清理
	'''
	if not G2048.returnDB:
		return
	G2048.Clear()
	

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross and (Environment.EnvIsQQ() or Environment.IsDevelop or Environment.EnvIsFT() or Environment.EnvIsTK()):
		
		#宝石2048得分排行榜
		G2048 = Game2048Rank()
		
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncOtherData)
		#每日清理调用
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		Event.RegEvent(Event.Eve_InitRolePyObj, InitGame2048)
		Event.RegEvent(Event.Eve_BeforeExit, SaveDataGame2048)
		Event.RegEvent(Event.Eve_ClientLost, SaveDataGame2048)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request2048OOpenPanel", "客户端请求2048打开面板"), Request2048OOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request2048Start", "客户端请求2048开始游戏"), Request2048Start)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request2048Move", "客户端请求2048移动"), Request2048Move)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request2048Reward", "客户端请求2048领取奖励"), Request2048Reward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request2048BuyTimes", "客户端请求2048购买次数"), Request2048BuyTimes)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request2048End", "客户端请求2048结束本局"), Request2048End)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Request2048ScoreRank", "客户端请求2048跨服排行榜"), Request2048ScoreRank)
		
		cComplexServer.RegBeforeNewDayCallFunction(NewDayClear)
		#控制进程消息
		#请求逻辑进程的祖玛公会排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicGame2048Rank, OnControlRequestRank)
		#发送宝石2048跨服排行榜数据到逻辑进程(今天，昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdateGame2048RankToLogic, OnControlUpdataRank)
		#发送宝石2048跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdateGame2048RankToLogic_T, OnControlUpdataRank_T)
