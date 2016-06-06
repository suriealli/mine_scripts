#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.Zuma.ZumaMgr")
#===============================================================================
# 注释
#===============================================================================
import random
import cComplexServer
import cDateTime
import cProcess
import cRoleMgr
import Environment
from Common.Message import AutoMessage, PyMessage
from Common.Other import EnumGameConfig, GlobalPrompt, EnumAward
from ComplexServer import Init
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.Control import ControlProxy
from Game.Activity.Award import AwardMgr
from Game.Activity.Zuma import ZumaConfig
from Game.GlobalData import ZoneName
from Game.Persistence import Contain
from Game.Role import Rank, Event, Status
from Game.Role.Data import EnumTempObj, EnumObj, EnumDayInt8, EnumInt8,\
	EnumDayInt1, EnumInt1
from Game.Union import UnionMgr, UnionDefine

if "_HasLoad" not in dir():
	#祖玛Obj索引
	ZUMA_OBJ_SCORE_REWARD_IDX = 1
	ZUMA_OBJ_COLLECT_IDX = 2
	ZUMA_OBJ_COLLECT_REWARD_IDX = 3
	
	ZUMA_NEED_LEVEL = 36			#祖玛需要等级
	EXPLODE_NEED_BALL_CNT = 3		#爆炸需要的球数
	EXPLODE_REWARD_RECORD_CNT = 11	#爆炸奖励记录上限
	ZUMA_ROLE_RANK_MAX_CNT = 10		#祖玛个人排行榜最大数量
	
	EXPLODE_REWARD_RECORD_DICT = {}	#爆炸奖励记录字典
	
	ZUMA_CONTROL_UNION_TODAY_RANK = []		#祖玛跨服公会排行榜（今天）
	ZUMA_CONTROL_UNION_YESTERDAY_RANK = []	#祖玛跨服公会排行榜（昨天）
	
	#消息
	Zuma_Init = AutoMessage.AllotMessage("Zuma_Init", "通知客户端祖玛初始化")
	Zuma_Show_Shoot_Ball = AutoMessage.AllotMessage("Zuma_Show_Shoot_Ball", "通知客户端显示祖玛发射球")
	Zuma_Show_Explode_Reward = AutoMessage.AllotMessage("Zuma_Show_Explode_Reward", "通知客户端显示祖玛爆炸奖励")
	Zuma_Show_Role_Today_Rank = AutoMessage.AllotMessage("Zuma_Show_Role_Today_Rank", "通知客户端显示祖玛个人今日排行榜")
	Zuma_Show_Role_Yesterday_Rank = AutoMessage.AllotMessage("Zuma_Show_Role_Yesterday_Rank", "通知客户端显示祖玛个人昨日排行榜")
	Zuma_Show_Union_Today_Rank = AutoMessage.AllotMessage("Zuma_Show_Union_Today_Rank", "通知客户端显示祖玛公会今日排行榜")
	Zuma_Show_Union_Yesterday_Rank = AutoMessage.AllotMessage("Zuma_Show_Union_Yesterday_Rank", "通知客户端显示祖玛公会昨日排行榜")
	Zuma_Show_Rank_In_Game_Panel = AutoMessage.AllotMessage("Zuma_Show_Rank_In_Game_Panel", "通知客户端显示祖玛游戏面板内的排名")
	Zuma_Show_Score = AutoMessage.AllotMessage("Zuma_Show_Score", "通知客户端显示祖玛分数")
	Zuma_Show_Game_Over_Data = AutoMessage.AllotMessage("Zuma_Show_Game_Over_Data", "通知客户端显示祖玛游戏结束统计")
	Zuma_Show_Score_Reward =  AutoMessage.AllotMessage("Zuma_Show_Score_Reward", "通知客户端显示祖玛积分奖励状态")
	Zuma_Show_Collect_Data = AutoMessage.AllotMessage("Zuma_Show_Collect_Data", "通知客户端显示祖玛收集信息")
	
def AfterLoad():
	pass
	
def AfterLoadZumaRoleRankDict():
	global ZUMA_ROLE_RANK_DICT
	if 1 not in ZUMA_ROLE_RANK_DICT:
		ZUMA_ROLE_RANK_DICT[1] = []
	if 2 not in ZUMA_ROLE_RANK_DICT:
		ZUMA_ROLE_RANK_DICT[2] = []
	
#===============================================================================
# 排行榜
#===============================================================================
class ZumaUnionRank(Rank.SmallRoleRank):
	defualt_data_create = dict				#持久化数据需要定义的数据类型
	max_rank_size = 50						#最大排行榜 50个
	dead_time = (2038, 1, 1)
	
	needSync = False						#不需要同步给客户端 
	name = "Rank_ZumaUnionScore"
	
	# 返回v1 是否 小于 v2
	def IsLess(self, v1, v2):
		return v1[0] < v2[0]
	
	def Clear(self):
		#清理数据
		self.data = {}
		self.min_role_id = 0
		self.min_value = 0
		self.changeFlag = True
		
	def AfterLoadFun(self):
		Rank.SmallRoleRank.AfterLoadFun(self)
		TryUpdate()
	
#===============================================================================
# 祖玛玩法类
#===============================================================================
class Zuma(object):
	def __init__(self, role, levelId):
		self.role = role
		self.config = ZumaConfig.ZUMA_BASE[levelId]			#基础配置
		self.score = 0										#分数
		self.cur_combo_cnt = 0								#当前连锁次数
		self.max_combo_cnt = 0								#最大单次连击次数
		self.total_combo_cnt = 0							#总连击次数
		self.total_explode_cnt = 0							#总爆炸个数
		self.ball_chain_list = []							#球链列表
		self.shoot_ball_list = []							#发射球列表
		self.tick_id = 0									#游戏tick
		self.is_game_over = False							#是否游戏结束
		
		#创建
		self.create()
		
	def create(self):
		totalBallCnt = 0
		lastRandomBallId = 0
		#分批随机生成整个球链列表
		while(totalBallCnt < self.config.ballChainLen):
			ballCnt = self.config.randomObj.RandomOne()
			
			#随机生成
			i = 0
			randomListLen = len(self.config.randomBallIdList)
			while(i < randomListLen):
				i += 1
				ballId = random.choice(self.config.randomBallIdList)
				#两次生成的颜色不能一致
				if lastRandomBallId != ballId:
					lastRandomBallId = ballId
					break
				
			#球配置
			ballConfig = ZumaConfig.ZUMA_BALL.get(ballId)
			if not ballConfig:
				continue
			
			if totalBallCnt + ballCnt <= self.config.ballChainLen:
				for _ in xrange(ballCnt):
					#随机奖励
					rewardId = ballConfig.randomObj.RandomOne()
					self.ball_chain_list.append((ballId, rewardId))
			else:
				for _ in xrange(self.config.ballChainLen - totalBallCnt):
					#随机奖励
					rewardId = ballConfig.randomObj.RandomOne()
					self.ball_chain_list.append((ballId, rewardId))
					
			totalBallCnt += ballCnt
		
		#随机生成发射球列表
		for _ in xrange(self.config.shootBallCnt):
			ballId = random.choice(self.config.randomBallIdList)
			#颜色是否存在
			if (ballId, 0) not in self.ball_chain_list:
				ballId, _ = random.choice(self.ball_chain_list)
			self.shoot_ball_list.append(ballId)
		
		#注册倒计时
		self.tick_id = self.role.RegTick(self.config.limitTime + 5, self.tick_on)
		
		#通知客户端初始化
		self.role.SendObj(Zuma_Init, self.ball_chain_list)
		self.show_shoot_ball()
		
	def tick_on(self, role, calargv, regparam):
		if not self.tick_id:
			return
		self.tick_id = 0
		
		self.lost()
		
	def insert(self, pos):
		#是否为空
		if not self.shoot_ball_list:
			return
		
		insertBallId = self.shoot_ball_list.pop()
		
		self.ball_chain_list.insert(pos, (insertBallId,0))
		
		self.show_shoot_ball()
	
	def explode(self, startPos, explodeLen):
		#是否为空
		if not self.shoot_ball_list:
			return
		
		#重置当前连锁次数
		self.cur_combo_cnt = 0
		
		insertBallId = self.shoot_ball_list.pop()
		
		sameBallCnt = 0
		ballChainLen = len(self.ball_chain_list)
		#是否满足爆炸条件
		for x in xrange(explodeLen):
			pos = startPos + x
			if pos >= ballChainLen:
				return
			
			if insertBallId != self.ball_chain_list[pos][0]:
				return
			
			sameBallCnt += 1
			
		if sameBallCnt + 1 < EXPLODE_NEED_BALL_CNT:
			return
		
		#奖励
		for x in xrange(explodeLen):
			pos = startPos + x
			if pos >= ballChainLen:
				return
			
			rewardId = self.ball_chain_list[pos][1]
			if not rewardId:
				continue
			
			self.explode_reward(rewardId)
			
		#爆炸
		del self.ball_chain_list[startPos : startPos + explodeLen]
		
		#计算消除分数
		self.calc_explode_score(explodeLen + 1)
		
		#combo
		self.combo(startPos - 1)
		
		#更新单词最大连锁次数
		if self.cur_combo_cnt > self.max_combo_cnt:
			self.max_combo_cnt = self.cur_combo_cnt
		#更新消除总个数
		self.total_explode_cnt += (explodeLen + 1)
		
		#把发射列表中不存在于消除列表中的颜色替换
		self.is_replace()
		
		#同步客户端
		self.show_shoot_ball()
		
	def combo(self, pos):
		ballChainLen = len(self.ball_chain_list)
		#判断是否在末端
		if pos < 0:
			return
		if pos >= ballChainLen - 1:
			return
		
		ballId, rewardId = self.ball_chain_list[pos]
		#首尾是否相同
		if pos + 1 >= ballChainLen:
			return
		if ballId != self.ball_chain_list[pos + 1][0]:
			return
		
		#寻找需要爆炸的球
		frontSameBallCnt = 0
		rearSameBallCnt = 0
		#往前寻找
		reverseFrontBallChainList = self.ball_chain_list[:pos]
		reverseFrontBallChainList.reverse()
		for bId, _ in reverseFrontBallChainList:
			if bId != ballId:
				break
			frontSameBallCnt += 1
			
		#往后寻找
		for bId, _ in self.ball_chain_list[pos:]:
			if bId != ballId:
				break
			rearSameBallCnt += 1
		
		#是否满足爆炸条件
		if frontSameBallCnt + rearSameBallCnt < EXPLODE_NEED_BALL_CNT:
			return
		
		#奖励
		for x in xrange(pos - frontSameBallCnt, pos  + rearSameBallCnt):
			rewardId = self.ball_chain_list[x][1]
			if not rewardId:
				continue
			
			self.explode_reward(rewardId)
		
		#爆炸
		del self.ball_chain_list[pos - frontSameBallCnt : pos  + rearSameBallCnt]
		
		#连锁次数增加
		self.cur_combo_cnt += 1
		#总连锁次数增加
		self.total_combo_cnt += 1
		#消除总个数增加
		self.total_explode_cnt += (frontSameBallCnt + rearSameBallCnt)
		#计算消除分数
		self.calc_explode_score(frontSameBallCnt + rearSameBallCnt)
		#计算combo分数
		self.calc_combo_score()
		
		#递归
		self.combo(pos - frontSameBallCnt - 1)
		
	def pop_ball(self):
		#是否为空
		if not self.shoot_ball_list:
			return
		
		self.shoot_ball_list.pop()
		
		self.show_shoot_ball()
		
	def win(self):
		#是否游戏结束
		if self.is_game_over is True:
			return
		if self.ball_chain_list:
			print "GE_EXC, roleId(%s) zuma win error ball_chain_list is not None  " % self.role.GetRoleID()
			return
		self.is_game_over = True
		self.calc_game_over_score()
		
		#入榜
		self.in_rank()
		
		#退出天天消龙珠游戏状态
		Status.Outstatus(self.role, EnumInt1.ST_Zuma)
		
		#同步客户端
		self.show_game_over_data()
		ShowZumaMainPanel(self.role)
		
	def lost(self):
		#是否游戏结束
		if self.is_game_over is True:
			return
		self.is_game_over = True
		
		self.calc_game_over_score()
		
		#入榜
		self.in_rank()
		
		#退出天天消龙珠游戏状态
		Status.Outstatus(self.role, EnumInt1.ST_Zuma)
		
		#同步客户端
		self.show_game_over_data()
		ShowZumaMainPanel(self.role)
		
	def is_replace(self):
		if not self.ball_chain_list:
			return
		
		for idx, shootBallId in enumerate(self.shoot_ball_list):
			if (shootBallId, 0) in self.ball_chain_list:
				continue
			
			ballId, _ = random.choice(self.ball_chain_list)
			self.shoot_ball_list[idx] = ballId
				
		
	def show_game_over_data(self):
		#总爆炸个数,总连击次数,最大单次连击次数
		self.role.SendObj(Zuma_Show_Game_Over_Data, (self.total_explode_cnt, self.total_combo_cnt, self.max_combo_cnt))
		
	def calc_explode_score(self, explodeLen):
		#单次消除积分（单次消除个数）
		scoreConfig = ZumaConfig.ZUMA_SCORE.get(explodeLen)
		if scoreConfig:
			self.score += scoreConfig.explodeScorePerTime
			#提示
			self.role.Msg(2, 0, GlobalPrompt.ZUMA_EXPLODE_SCORE_PROMPT % scoreConfig.explodeScorePerTime)
			
		#同步客户端分数
		self.role.SendObj(Zuma_Show_Score, self.score)
		
	def calc_combo_score(self):
		#单次连锁积分（当前连锁次数）
		scoreConfig = ZumaConfig.ZUMA_SCORE.get(self.cur_combo_cnt)
		if scoreConfig:
			self.score += scoreConfig.cobomScorePerTime
			#提示
			self.role.Msg(2, 0, GlobalPrompt.ZUMA_COMBO_SCORE_PROMPT % (self.cur_combo_cnt, scoreConfig.cobomScorePerTime))
			
		#同步客户端分数
		self.role.SendObj(Zuma_Show_Score, self.score)
			
	def calc_game_over_score(self):
		#累计消除积分（消除总个数）
		scoreConfig = ZumaConfig.ZUMA_SCORE.get(self.total_explode_cnt)
		if scoreConfig:
			self.score += scoreConfig.totalExplodeCntScore
			
		#累计连锁次数积分（连锁总次数）
		scoreConfig = ZumaConfig.ZUMA_SCORE.get(self.total_combo_cnt)
		if scoreConfig:
			self.score += scoreConfig.totalCobomCntScore
			
		#最高连锁积分（最高单次消除连锁次数）
		scoreConfig = ZumaConfig.ZUMA_SCORE.get(self.max_combo_cnt)
		if scoreConfig:
			self.score += scoreConfig.maxCobomScorePerExplode
			
		#保存最高积分
		global ZUMA_SCORE_DICT
		roleId = self.role.GetRoleID()
		if roleId not in ZUMA_SCORE_DICT:
			ZUMA_SCORE_DICT[roleId] = self.score
		else:
			if self.score > ZUMA_SCORE_DICT[roleId]:
				ZUMA_SCORE_DICT[roleId] = self.score
				
		#判断积分奖励状态
		self.activate_score_reward()
		
		#日志
		with TraZumaScore:
			AutoLog.LogBase(self.role.GetRoleID(), AutoLog.eveZumaScore, self.score)
		
		#同步客户端分数
		self.role.SendObj(Zuma_Show_Score, self.score)
		
	def activate_score_reward(self):
		scoreRewardDict = self.role.GetObj(EnumObj.Zuma)[ZUMA_OBJ_SCORE_REWARD_IDX]
		#判断积分奖励状态
		level = self.role.GetLevel()
		configDict = ZumaConfig.ZUMA_SCORE_REWARD.get(level)
		for config in configDict.itervalues():
			if self.score >= config.score:
				if config.rewardId not in scoreRewardDict:
					scoreRewardDict[config.rewardId] = 1
		
		#同步客户端祖玛积分奖励积分奖励
		ShowZumaScoreReward(self.role)
		
	def explode_reward(self, rewardId):
		rewardConfig = ZumaConfig.ZUMA_BALL_REWARD.get(rewardId)
		if not rewardConfig:
			return
		rewardItemCoding, rewardItemCnt = rewardConfig.randomObj.RandomOne()
		if not rewardItemCoding:
			return
		
		#掉落神石
		if rewardItemCoding == 27486:
			#掉落限制
			if self.role.GetDI1(EnumDayInt1.ZumaRMBReward):
				return
			self.role.SetDI1(EnumDayInt1.ZumaRMBReward, 1)
		
		self.role.AddItem(rewardItemCoding, rewardItemCnt)
		
		#添加奖励记录
		self.add_reward_record(rewardItemCoding, rewardItemCnt)
		#是否添加收集
		IsIncCollectItem(self.role, rewardItemCoding, rewardItemCnt)
		
		#提示
		self.role.Msg(2, 0, GlobalPrompt.Reward_Item_Tips % (rewardItemCoding, rewardItemCnt))
		
		#掉落神石
		if rewardItemCoding == 27486:
			#得到神石特殊公告
			cRoleMgr.Msg(1, 0, GlobalPrompt.ZUMA_RMB_HEARSAY % (self.role.GetRoleName(), rewardItemCoding, rewardItemCnt))
			
	def add_reward_record(self, itemCoding, itemCnt):
		global EXPLODE_REWARD_RECORD_DICT
		
		roleId = self.role.GetRoleID()
		recordList = EXPLODE_REWARD_RECORD_DICT.setdefault(roleId, [])
		
		recordList.insert(0, (itemCoding, itemCnt))
		#最大保存条数
		if len(recordList) > EXPLODE_REWARD_RECORD_CNT:
			recordList.pop()
		
		#同步客户端
		self.role.SendObj(Zuma_Show_Explode_Reward, recordList)
		
	def in_rank(self):
		global ZUMA_ROLE_RANK_DICT
		rankList = ZUMA_ROLE_RANK_DICT[1]
		
		#是否已经在榜单中,是则直接更新分数
		roleId = self.role.GetRoleID()
		roleName = self.role.GetRoleName()
		for idx, data in enumerate(rankList):
			if roleId == data[1]:
				#分数是否有超过最高分
				if self.score > rankList[idx][0]:
					rankList[idx][0] = self.score
					rankList.sort(key = lambda x:(x[0], x[1]), reverse = True)
				
				ZUMA_ROLE_RANK_DICT.changeFlag = True
				return
			
		rankRoleCnt = len(rankList)
		if rankRoleCnt < ZUMA_ROLE_RANK_MAX_CNT:
			#入榜人数不足则直接入榜
			rankList.append([self.score, roleId, roleName])
			rankList.sort(key = lambda x:(x[0], x[1]), reverse = True)
		else:
			if self.score < rankList[-1][0]:
				#分数比第十名低
				return
			else:
				rankList[-1] = [self.score, roleId, roleName]
				rankList.sort(key = lambda x:(x[0], x[1]), reverse = True)
				ZUMA_ROLE_RANK_DICT[1] = rankList[:ZUMA_ROLE_RANK_MAX_CNT]
		
		ZUMA_ROLE_RANK_DICT.changeFlag = True
		
	def show_shoot_ball(self):
		self.role.SendObj(Zuma_Show_Shoot_Ball, self.shoot_ball_list)
		
#===============================================================================
# 显示
#===============================================================================
def ShowZumaMainPanel(role):
	unionRank = 0
	roleId = role.GetRoleID()
	#获取公会排行
	unionId = role.GetUnionID()
	for idx, data in enumerate(ZUMA_CONTROL_UNION_TODAY_RANK):
		if unionId != data[1]:
			continue
		
		unionRank = idx + 1
		break
	
	#最高积分，个人排行，公会排行
	role.SendObj(Zuma_Show_Rank_In_Game_Panel, [ZUMA_SCORE_DICT.get(roleId, 0), GetZumaRoleRank(roleId), unionRank])
		
	#同步客户端
	role.SendObj(Zuma_Show_Explode_Reward, EXPLODE_REWARD_RECORD_DICT.get(roleId, []))
		
def ShowZumaScoreReward(role):
	role.SendObj(Zuma_Show_Score_Reward, role.GetObj(EnumObj.Zuma)[ZUMA_OBJ_SCORE_REWARD_IDX])
	
def ShowZumaCollectData(role):
	role.SendObj(Zuma_Show_Collect_Data, role.GetObj(EnumObj.Zuma)[ZUMA_OBJ_COLLECT_IDX])
		
#===============================================================================
# 
#===============================================================================
def GetScoreReward(role, rewardId):
	scoreRewardDict = role.GetObj(EnumObj.Zuma)[ZUMA_OBJ_SCORE_REWARD_IDX]
	
	#是否满足领奖条件
	if rewardId not in scoreRewardDict:
		return
	if scoreRewardDict[rewardId] != 1:
		return
	
	configDict = ZumaConfig.ZUMA_SCORE_REWARD.get(role.GetLevel())
	if not configDict:
		return
	
	config = configDict.get(rewardId)
	if not config:
		return
	
	#设置已领取
	scoreRewardDict[rewardId] = 2
	
	#奖励
	tips = GlobalPrompt.Reward_Tips
	for coding, cnt in config.rewardItem:
		role.AddItem(coding, cnt)
		tips += GlobalPrompt.Item_Tips % (coding, cnt)
	if config.bindRMB:
		role.IncBindRMB(config.bindRMB)
		tips += GlobalPrompt.BindRMB_Tips % (config.bindRMB)
	
	#提示
	role.Msg(2, 0, tips)
	
	ShowZumaScoreReward(role)

def GetCollectReward(role, rewardId):
	collectItemDict = role.GetObj(EnumObj.Zuma)[ZUMA_OBJ_COLLECT_IDX]
	
	config = ZumaConfig.ZUMA_COLLECT.get(rewardId)
	if not config:
		return
	
	#判断是否满足领奖条件
	for needCoding, needCnt in config.condition:
		if needCoding not in collectItemDict:
			return
		if collectItemDict[needCoding] < needCnt:
			return
	
	#扣除收集道具
	for needCoding, needCnt in config.condition:
		collectItemDict[needCoding] -= needCnt
	
	#奖励
	tips = GlobalPrompt.Reward_Tips
	for coding, cnt in config.rewardItem:
		role.AddItem(coding, cnt)
		tips += GlobalPrompt.Item_Tips % (coding, cnt)
		
	#提示
	role.Msg(2, 0, tips)
	
	ShowZumaCollectData(role)
	
def BuyZumaCnt(role):
	'''
	购买竞技场次数
	@param role:
	'''
	#今日是否还可以购买
	cnt = role.GetDI8(EnumDayInt8.ZumaBuyCnt)
	if cnt >= EnumGameConfig.ZUMA_BUY_LIMIT_CNT:
		return
	
	#消耗神石
	costRMB = 0
	if Environment.EnvIsNA():
		costRMB = EnumGameConfig.ZUMA_BUY_CNT_RMB_NA
	else:
		costRMB = EnumGameConfig.ZUMA_BUY_CNT_RMB
	if role.GetUnbindRMB() < costRMB:
		return
	role.DecUnbindRMB(costRMB)
	
	#增加次数
	role.IncDI8(EnumDayInt8.ZumaBuyCnt, 1)
	role.IncI8(EnumInt8.ZumaCnt, 1)
	
def GetZumaRoleRank(roleId):
	for idx, data in enumerate(ZUMA_ROLE_RANK_DICT[1]):
		if data[1] == roleId:
			return idx + 1
	return 0

def ZumaUnionRankReward():
	btData = UnionMgr.BT.GetData()
	
	for idx, data in enumerate(ZUMA_CONTROL_UNION_TODAY_RANK):
		rank = idx + 1
		unionId = data[1]
		
		if rank >= 20:
			break
		
		#是否是本服的公会
		if unionId not in btData:
			continue
		
		unionObj = UnionMgr.GetUnionObjByID(unionId)
		
		for memberId, memberData in unionObj.members.iteritems():
			memberLevel = memberData[UnionDefine.M_LEVEL_IDX]
			rewardConfig = ZumaConfig.ZUMA_UNION_RANK_REWARD.get((rank, memberLevel))
			if not rewardConfig:
				print "GE_EXC, can't find rewardConfig in ZumaUnionRankReward(%s, %s, %s)" % (unionId, rank, memberLevel)
				continue
			
			#今日是否参与过祖玛游戏
			if memberId not in ZUMA_SCORE_DICT:
				continue
			
			#玩法奖励
			AwardMgr.SetAward(memberId, EnumAward.ZumaUnionRankAward, 
							itemList = rewardConfig.rewardItem, 
							clientDescParam = (rank, ))
		
def IsIncCollectItem(role, rewardItemCoding, cnt):
	collectItemDict = role.GetObj(EnumObj.Zuma)[ZUMA_OBJ_COLLECT_IDX]
	for collectItemCoding in ZumaConfig.ZUMA_COLLECT_ITEM:
		if collectItemCoding == rewardItemCoding:
			#记录收集
			if collectItemCoding in collectItemDict:
				collectItemDict[collectItemCoding] += cnt
			else:
				collectItemDict[collectItemCoding] = cnt
				
	#同步客户端祖玛收集
	ShowZumaCollectData(role)
	
def ZumaStartGame(role, levelId):
	#添加时间限制
	hour = cDateTime.Hour()
	minute = cDateTime.Minute()
	if hour == 0 and minute < 10:
		return
	
	#等级限制
	if role.GetLevel() < ZUMA_NEED_LEVEL:
		return
	
	#积分是否达标
	config = ZumaConfig.ZUMA_BASE.get(levelId)
	if not config:
		return
	if ZUMA_SCORE_DICT.get(role.GetRoleID(), 0) < config.needScore:
		return
	
	#是否还有次数
	if role.GetI8(EnumInt8.ZumaCnt) == 0:
		return
	
	#能否进入天天消龙珠状态
	if not Status.CanInStatus(role, EnumInt1.ST_Zuma):
		return
	#强制进入天天消龙珠状态
	Status.ForceInStatus(role, EnumInt1.ST_Zuma)
	
	#扣除次数
	role.DecI8(EnumInt8.ZumaCnt, 1)
	
	role.SetTempObj(EnumTempObj.ZumaGame, Zuma(role, levelId))
	
	Event.TriggerEvent(Event.Eve_LatestActivityTask, role, (EnumGameConfig.LA_Zuma, 1))
#===============================================================================
# 
#===============================================================================
def GetLogicRank():
	CalcAllUnionScore()
	#返回本地排行榜
	return ZUR.data.values()

def CalcAllUnionScore():
	#清空榜单
	ZUR.Clear()
	
	btData = UnionMgr.BT.GetData()
	for unionId in btData.iterkeys():
		unionObj = UnionMgr.GetUnionObjByID(unionId)
		if not unionObj:
			continue
		
		totalScore = 0
		#统计总分数
		for memberId in unionObj.members.iterkeys():
			if memberId not in ZUMA_SCORE_DICT:
				continue
		
			totalScore += ZUMA_SCORE_DICT[memberId]
		
		#入榜单
		ZUR.HasData(unionId, [totalScore, unionId, unionObj.name, ZoneName.ZoneName])
		
def TryUpdate():
	'''
	排行榜数据载回来后尝试更新富豪榜
	'''
	#向控制进程请求跨服排行榜数据
	ControlProxy.SendControlMsg(PyMessage.Control_RequestControlZumaUnionRank, (cProcess.ProcessID, GetLogicRank()))
		
#===============================================================================
# 服务器启动
#===============================================================================
def ServerUp():
	#起服的时候向控制进程请求跨服排行榜数据
	if not ZUR.returnDB:
		return
	ControlProxy.SendControlMsg(PyMessage.Control_RequestControlZumaUnionRank, (cProcess.ProcessID, GetLogicRank()))
		
#===============================================================================
# 时间
#===============================================================================
def AfterNewHour():
	pass
	
def AfterNewDay():
	global ZUMA_ROLE_RANK_DICT
	zumaRoleRank = ZUMA_ROLE_RANK_DICT[1]
	#个人排行榜奖励
	for idx, data in enumerate(zumaRoleRank):
		rank = idx + 1
		roleId = data[1]
		
		rewardConfig = ZumaConfig.ZUMA_ROLE_RANK_REWARD.get(rank)
		if not rewardConfig:
			continue
		
		#玩法奖励
		AwardMgr.SetAward(roleId, EnumAward.ZumaRoleRankAward, 
						itemList = rewardConfig.rewardItem, 
						clientDescParam = (rank, ))
		
	#跨天处理
	ZUMA_ROLE_RANK_DICT[2] = ZUMA_ROLE_RANK_DICT[1]
	ZUMA_ROLE_RANK_DICT[1] = []
	
	#活动结束后20分钟清空最高积分字典
	cComplexServer.RegTick(20 * 60, ZumaScoreClear)
	
def ZumaScoreClear(callArgv, regparam):
	#清空最高积分
	global ZUMA_SCORE_DICT
	ZUMA_SCORE_DICT.clear()
	
#===============================================================================
# 事件
#===============================================================================
def OnRoleInit(role, param):
	'''
	角色初始化
	@param role:
	@param param:
	'''
	pass

def OnSyncRoleOtherData(role, param):
	'''
	角色登陆同步其它数据
	@param role:
	@param param:
	'''
	zumaDict = role.GetObj(EnumObj.Zuma)
	if ZUMA_OBJ_SCORE_REWARD_IDX not in zumaDict:
		zumaDict[ZUMA_OBJ_SCORE_REWARD_IDX] = {}
	if ZUMA_OBJ_COLLECT_IDX not in zumaDict:
		zumaDict[ZUMA_OBJ_COLLECT_IDX] = {}
	if ZUMA_OBJ_COLLECT_REWARD_IDX not in zumaDict:
		zumaDict[ZUMA_OBJ_COLLECT_REWARD_IDX] = {}
	
	#同步客户端祖玛积分奖励积分奖励
	ShowZumaScoreReward(role)
	#同步客户端祖玛收集奖励
	ShowZumaCollectData(role)
	
def OnRoleDayClear(role, param):
	'''
	每日清理
	@param role:
	@param param:
	'''
	#日志
	with TraZumaResetCnt:
		#重置挑战次数
		role.SetI8(EnumInt8.ZumaCnt, EnumGameConfig.ZUMA_FREE_CNT)
		
	#重置积分奖励
	role.GetObj(EnumObj.Zuma)[ZUMA_OBJ_SCORE_REWARD_IDX] = {}
	
	#每个月清理收集
	saveMonth = role.GetI8(EnumInt8.ZumaCollectClearMonth)
	nowMonth = cDateTime.Month()
	if nowMonth != saveMonth:
		role.SetI8(EnumInt8.ZumaCollectClearMonth, nowMonth)
		role.GetObj(EnumObj.Zuma)[ZUMA_OBJ_COLLECT_IDX] = {}
		role.GetObj(EnumObj.Zuma)[ZUMA_OBJ_COLLECT_REWARD_IDX] = {}
		
	#同步客户端
	ShowZumaScoreReward(role)
		
#===============================================================================
# 客户端请求
#===============================================================================
def RequestZumaOpenMainPanel(role, msg):
	'''
	客户端请求祖玛打开主面板
	@param role:
	@param msg:
	'''
	#等级限制
	if role.GetLevel() < ZUMA_NEED_LEVEL:
		return
	
	ShowZumaMainPanel(role)
	
def RequestZumaStartGame(role, msg):
	'''
	客户端请求祖玛开始游戏
	@param role:
	@param msg:
	'''
	levelId = msg
	
	#日志
	with TraZumaStart:
		ZumaStartGame(role, levelId)
	
def RequestZumaInsert(role, msg):
	'''
	客户端请求祖玛插入
	@param role:
	@param msg:
	'''
	pos = msg
	zumaGame = role.GetTempObj(EnumTempObj.ZumaGame)
	if not zumaGame:
		return
	
	zumaGame.insert(pos)
	
def RequestZumaExplode(role, msg):
	'''
	客户端请求祖玛爆炸
	@param role:
	@param msg:
	'''
	startPos, explodeLen = msg
	zumaGame = role.GetTempObj(EnumTempObj.ZumaGame)
	if not zumaGame:
		return
	
	#日志
	with TraZumaExplodeReward:
		zumaGame.explode(startPos, explodeLen)
	
def RequestZumaPopBall(role, msg):
	'''
	客户端请求祖玛扔掉当前球
	@param role:
	@param msg:
	'''
	zumaGame = role.GetTempObj(EnumTempObj.ZumaGame)
	if not zumaGame:
		return
	
	zumaGame.pop_ball()
	
def RequestZumaGameWin(role, msg):
	'''
	客户端请求祖玛游戏胜利
	@param role:
	@param msg:
	'''
	zumaGame = role.GetTempObj(EnumTempObj.ZumaGame)
	if not zumaGame:
		return
	
	zumaGame.win()
	
def RequestZumaGameOver(role, msg):
	'''
	客户端请求祖玛游戏结束
	@param role:
	@param msg:
	'''
	zumaGame = role.GetTempObj(EnumTempObj.ZumaGame)
	if not zumaGame:
		return
	
	zumaGame.lost()
	
	role.SetTempObj(EnumTempObj.ZumaGame, None)
	
def RequestZumaBuyCnt(role, msg):
	'''
	客户端请求祖玛购买次数
	@param role:
	@param msg:
	'''
	#日志
	with TraZumaBuyCnt:
		BuyZumaCnt(role)
	
def RequestZumaRoleTodayRank(role, msg):
	'''
	客户端请求祖玛个人今日排行榜
	@param role:
	@param msg:
	'''
	role.SendObj(Zuma_Show_Role_Today_Rank, ZUMA_ROLE_RANK_DICT[1])
	
def RequestZumaRoleYesterdayRank(role, msg):
	'''
	客户端请求祖玛个人昨日排行榜
	@param role:
	@param msg:
	'''
	role.SendObj(Zuma_Show_Role_Yesterday_Rank, ZUMA_ROLE_RANK_DICT[2])
	
def RequestZumaUnionTodayRank(role, msg):
	'''
	客户端请求祖玛公会今日排行榜
	@param role:
	@param msg:
	'''
	role.SendObj(Zuma_Show_Union_Today_Rank, ZUMA_CONTROL_UNION_TODAY_RANK)
	
def RequestZumaUnionYesterdayRank(role, msg):
	'''
	客户端请求祖玛公会昨日排行榜
	@param role:
	@param msg:
	'''
	role.SendObj(Zuma_Show_Union_Yesterday_Rank, ZUMA_CONTROL_UNION_YESTERDAY_RANK)
	
def RequestZumaGetScoreReward(role, msg):
	'''
	客户端请求祖玛领取积分奖励
	@param role:
	@param msg:
	'''
	rewardId = msg
	
	#日志
	with TraZumaScoreReward:
		GetScoreReward(role, rewardId)
	
def RequestZumaGetCollectReward(role, msg):
	'''
	客户端请求祖玛领取收集奖励
	@param role:
	@param msg:
	'''
	rewardId = msg
	
	#日志
	with TraZumaCollectReward:
		GetCollectReward(role, rewardId)
	
def RequestZumaOpenCollectPanel(role, msg):
	'''
	客户端请求祖玛打开收集面板
	@param role:
	@param msg:
	'''
	ShowZumaCollectData(role)
	
#===============================================================================
# 控制进程请求
#===============================================================================
def OnControlRequestRank(sessionid, msg):
	'''
	#控制进程请求获取本服富豪榜榜
	@param sessionid:
	@param msg:
	'''
	if not ZUR.returnDB:
		return
	backid, _ = msg
	ControlProxy.CallBackFunction(sessionid, backid, (cProcess.ProcessID, GetLogicRank()))
	
def OnControlUpdataRank(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天, 昨天)
	@param sessionid:
	@param msg:
	'''
	global ZUMA_CONTROL_UNION_TODAY_RANK
	global ZUMA_CONTROL_UNION_YESTERDAY_RANK
	ZUMA_CONTROL_UNION_TODAY_RANK, ZUMA_CONTROL_UNION_YESTERDAY_RANK = msg
	
def OnControlUpdataRank_T(sessionid, msg):
	'''
	#控制进程更新了新的跨服排行榜数据过来(今天)
	@param sessionid:
	@param msg:
	'''
	global ZUMA_CONTROL_UNION_TODAY_RANK
	ZUMA_CONTROL_UNION_TODAY_RANK = msg
	
def OnControlRequestZumaUnionRankReward(sessionid, msg):
	'''
	#控制进程请求获取本服富豪榜榜
	@param sessionid:
	@param msg:
	'''
	global ZUMA_CONTROL_UNION_TODAY_RANK
	global ZUMA_CONTROL_UNION_YESTERDAY_RANK
	ZUMA_CONTROL_UNION_TODAY_RANK = msg
	
	ZumaUnionRankReward()
	
	#发奖后处理排行榜
	ZUMA_CONTROL_UNION_YESTERDAY_RANK = ZUMA_CONTROL_UNION_TODAY_RANK
	ZUMA_CONTROL_UNION_TODAY_RANK = []
	
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		ZUMA_SCORE_DICT = Contain.Dict("ZUMA_SCORE_DICT", (2038, 1, 1), AfterLoad, isSaveBig = False)
		#{1:今日排行榜[], 2:昨日排行榜[]}
		ZUMA_ROLE_RANK_DICT = Contain.Dict("ZUMA_ROLE_RANK_DICT", (2038, 1, 1), AfterLoadZumaRoleRankDict, isSaveBig = False)
	
	if Environment.HasLogic and not Environment.IsCross and not Environment.EnvIsESP():
		#西班牙不开
		#祖玛公会排行榜
		ZUR = ZumaUnionRank()
		
		#注册服务器启动调用函数
		Init.InitCallBack.RegCallbackFunction(ServerUp)
		
		#时间
		cComplexServer.RegAfterNewHourCallFunction(AfterNewHour)
		cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
		
		#事件
		#角色初始化
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		#角色登陆同步其它数据
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		#每日清理调用
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
		
		#日志
		TraZumaBuyCnt = AutoLog.AutoTransaction("TraZumaBuyCnt", "祖玛购买次数")
		TraZumaExplodeReward = AutoLog.AutoTransaction("TraZumaExplode", "祖玛爆炸奖励")
		TraZumaScoreReward = AutoLog.AutoTransaction("TraZumaScoreReward", "祖玛积分奖励")
		TraZumaCollectReward = AutoLog.AutoTransaction("TraZumaCollectReward", "祖玛收集奖励")
		TraZumaStart = AutoLog.AutoTransaction("TraZumaStart", "祖玛开始游戏")
		TraZumaResetCnt = AutoLog.AutoTransaction("TraZumaResetCnt", "祖玛重置次数")
		TraZumaScore = AutoLog.AutoTransaction("TraZumaScore", "祖玛分数")
		
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Open_Main_Panel", "客户端请求祖玛打开主面板"), RequestZumaOpenMainPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Start_Game", "客户端请求祖玛开始游戏"), RequestZumaStartGame)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Insert", "客户端请求祖玛插入"), RequestZumaInsert)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Explode", "客户端请求祖玛爆炸"), RequestZumaExplode)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Pop_Ball", "客户端请求祖玛扔掉当前球"), RequestZumaPopBall)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Game_Win", "客户端请求祖玛游戏胜利"), RequestZumaGameWin)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Game_Over", "客户端请求祖玛游戏结束"), RequestZumaGameOver)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Buy_Cnt", "客户端请求祖玛购买次数"), RequestZumaBuyCnt)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Role_Today_Rank", "客户端请求祖玛个人今日排行榜"), RequestZumaRoleTodayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Role_Yesterday_Rank", "客户端请求祖玛个人昨日排行榜"), RequestZumaRoleYesterdayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Union_Today_Rank", "客户端请求祖玛公会今日排行榜"), RequestZumaUnionTodayRank)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Union_Yesterday_Rank", "客户端请求祖玛公会昨日排行榜"), RequestZumaUnionYesterdayRank)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Get_Score_Reward", "客户端请求祖玛领取积分奖励"), RequestZumaGetScoreReward)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Open_Collect_Panel", "客户端请求祖玛打开收集面板"), RequestZumaOpenCollectPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Zuma_Get_Collect_Reward", "客户端请求祖玛领取收集奖励"), RequestZumaGetCollectReward)
		
		#控制进程消息
		#请求逻辑进程的祖玛公会排行榜数据(回调)
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicZumaUnionRank, OnControlRequestRank)
		#发送祖玛公会跨服排行榜数据到逻辑进程(今天，昨天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdateZumaUnionRankToLogic, OnControlUpdataRank)
		#发送祖玛公会跨服排行榜数据到逻辑进程(今天)
		cComplexServer.RegDistribute(PyMessage.Control_UpdateZumaUnionRankToLogic_T, OnControlUpdataRank_T)
		#请求逻辑进程的祖玛公会榜颁发奖励
		cComplexServer.RegDistribute(PyMessage.Control_RequestLogicZumaUnionRankReward, OnControlRequestZumaUnionRankReward)
		
		