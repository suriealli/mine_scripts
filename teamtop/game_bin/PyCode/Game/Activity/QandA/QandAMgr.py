#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.QandA.QandAMgr")
#===============================================================================
# 答题
#===============================================================================
import cNetMessage
import cRoleMgr
import random
import cDateTime
import cSceneMgr
import cComplexServer
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from ComplexServer.Time import Cron
from Game.Activity.QandA import QandAConfig
from Game.DailyDo import DailyDo
from Game.Role import Event, Call
from Game.Role.Data import EnumDayInt1
from Game.Role.Mail import Mail
from Game.Scene import PublicScene
from Game.SysData import WorldData
from Game.ThirdParty.QQidip import QQEventDefine


if "_HasLoad" not in dir():
	IS_READY = False			#答题活动是否准备中
	IS_START = False			#答题活动是否开启

	QandA_START_DURATION = 60 * 15 + 3		#答题活动开始持续时间
	QandA_PER_QUESTION_TIME = 30			#答题活动刷新问题间隔时间
	QandA_PER_ANSWER_TIME = 29				#问题提出29秒后判断玩家答案
	QandA_READY_DURATION = 60				#答题活动准备时间
	QandA_QUESTION_NO = 0					#答题活动问题编码
	QAMGR = None							#答题管理器
	question_dict = {}						#随机问题获取器
	QandA_ENTER_SCENE_POS = ((100, 100), (1000, 1000)) 
	#消息
	QandA_Start = AutoMessage.AllotMessage("QandA_Start", "通知客户端答题开始")
	QandA_End = AutoMessage.AllotMessage("QandA_End", "通知客户端答题结束")
	QandA_Ask = AutoMessage.AllotMessage("QandA_Ask", "通知客户端问题题目")
	QandA_Show_Role_Data = AutoMessage.AllotMessage("QandA_Show_Role_Data", "通知客户端展示答题玩家数据")
	#日志
	QandA_Reward_Log = AutoLog.AutoTransaction("QandA_Reward_Log", "答题奖励")

class QandARole(object):
	def __init__(self, roleID):
		self.role_id = roleID				#roleId
		self.rightanswer_no = 0				#答题正确数
		self.wronganswer_no = 0				#答题错误数
		self.money_reward = 0				#角色获得金币数
		self.item_reward = {}				#角色获得物品及物品数量{itemid:item_cnt }		
		self.isLeave = False
		
	def AfterLeave(self):
		self.isLeave = True
		
		
	def AfterJoin(self):
		self.isLeave = False

class QandAMgr(object):
	def __init__(self):
		self.quest_index = 0			#问题索引
		self.next_question_time = 0		#下一题出题时间
		self.qarole_dict = {}			#保存进入过答题场景的角色
		self.scene = cSceneMgr.SearchPublicScene(EnumGameConfig.QandA_SCENE_ID)

	def AskQuestion(self):
		'''
		创建问题
		'''
		#获取第一题配置
		if self.quest_index > 30:
			return
		if not question_dict:
			print "GE_EXC, No such questiondict, check the config of QandA"
			return
		qandaConfig = question_dict.get(self.quest_index)
		if not qandaConfig:
			print "GE_EXC, can not find qandaConfig:%s in question_dict" % self.quest_index
			return
		#将问题编号以及下一题出题时间发送给客户端
		self.next_question_time = cDateTime.Seconds() + QandA_PER_QUESTION_TIME
		if self.quest_index == 30:
			cRoleMgr.Msg(11,0,GlobalPrompt.QandA_READY_BROADCAST_last)
		cNetMessage.PackPyMsg(QandA_Ask, (qandaConfig.index, self.next_question_time))
		self.scene.BroadMsg()

	def NextQuestion(self):
		'''
		下一题
		'''
		#下一题的题号
		if self.quest_index >= 30:
			return
		self.quest_index += 1
		#提问
		self.AskQuestion()


def SaveRoleAns(role , right):
	'''
	保存角色答题情况
	@param role:
	@param hurt:
	'''	
	roleId = role.GetRoleID()
	rolelevel = role.GetLevel()
	reward_cfg = QandAConfig.QandA_Award_dict.get(rolelevel)
	qarole = QAMGR.qarole_dict.get(roleId)
	if not qarole:
		print "GE_EXC, can not find roleID:%s in QAMGR.qarole_dict" % roleId
		return
	if not reward_cfg :
		print "GE_EXC, can not find roleLevel:%s in QandAConfig.QandA_Award_dict" % rolelevel
		return
	#如果回答错误
	if CheckAns(role) != right:
		qarole.wronganswer_no += 1
		#回答错误奖励金币
		qarole.money_reward += reward_cfg.w_money
		#回答错误获取的物品奖励
		if reward_cfg.w_item:
			for itemCoding, cnt in reward_cfg.w_item:
				qarole.item_reward.setdefault(itemCoding,0)
				qarole.item_reward[itemCoding] += cnt
	#如果回答正确
	else:
		qarole.rightanswer_no += 1
		#回答正确奖励金币
		qarole.money_reward += reward_cfg.r_money
		#回答正确获取的物品奖励
		if reward_cfg.r_item:
			for itemCoding, cnt in reward_cfg.r_item:
				qarole.item_reward.setdefault(itemCoding,0)
				qarole.item_reward[itemCoding] += cnt
		
		#答题正确次数达成王者公测奖励狂翻倍任务
		if qarole.rightanswer_no == EnumGameConfig.WZCR_Task_QAndATargetCnt:
			Event.TriggerEvent(Event.Eve_WangZheCrazyRewardTask, role, (EnumGameConfig.WZCR_Task_QAndA, True))
		
		#答题正确次数达成激情活动奖励狂翻倍任务
		if qarole.rightanswer_no == EnumGameConfig.PMR_Task_QAndATargetCnt:
			Event.TriggerEvent(Event.Eve_PassionMultiRewardTask, role, (EnumGameConfig.PassionMulti_Task_QAndA, True))
	
	Event.TriggerEvent(Event.Eve_FB_AfterQNA, role, None)

def RewardRole(role, regparam):
	'''
	 角色发放奖励
	@param role:
	@param regparam:
	'''	
	money_get, items = regparam
	AddItem = role.AddItem
	with QandA_Reward_Log:
		role.IncMoney(money_get)
		if role.PackageEmptySize() < len(items) :
			#发送邮件
			Mail.SendMail(role.GetRoleID(), GlobalPrompt.QandA_Mail_Title, GlobalPrompt.QandA_Mail_Send, GlobalPrompt.QandA_Mail_Content, items.items())
		else:
			#加入背包
			for itemCoding, cnt in items.iteritems():
				AddItem(itemCoding, cnt)

def RandomQues():
	'''
	获取随机问题
	'''
	#首先获取当前的世界等级
	world_level = WorldData.GetWorldLevel()
	#根据当前的世界等级取得该等级下可以获得的题目类型
	QandA_questtypeconfig = QandAConfig.QandA_Questiontype_dict.get(world_level)
	if not QandA_questtypeconfig:
		print "GE_EXC, may not find quetiontype for current Worldlevel in QandA Activity"
		return
	question_type = QandA_questtypeconfig.exam_type
	#仅有题目类型小于或等于question_type的题目可以出现，取出所有的这样的题目的题号
	question_list = []
	for questin_index, question_config in QandAConfig.QandA_QA_dict.iteritems():
		if not question_config.exam_type > question_type:
			question_list.append(questin_index)
	#若这样的题目少于30个，则打印异常并返回,对应当前世界等级的题目少于30个
	if len(question_list) < 30:
		print "GE_EXC, QandA examlib is less than 30 for the current World level"
		return
	#如果问题的编号出现 了重复，也打印异常并且返回
	if len(set(question_list)) < 30:
		print "GE_EXC, repeat quest_no in current world level in QandA Activity"
		return
	#随机获取题目
	ls = random.sample(question_list,30)
	index = 1
	questiondict = {}
	for key in ls:
		questiondict[index] = QandAConfig.QandA_QA_dict[key]
		index += 1
	return questiondict


def RandomXY(leftXY, rightXY):
	'''
	随机指定范围内的一个坐标
	@param leftXY:
	@param rightXY:
	'''
	lx, ly = leftXY
	rx, ry = rightXY
	randomX = 0
	randomY = 0
	if lx < rx:
		randomX = random.randint(lx, rx)
	else:
		randomX = random.randint(rx, lx)
	if ly < ry:
		randomY = random.randint(ly, ry)
	else:
		randomY = random.randint(ry, ly)
		
	return (randomX, randomY)	


def ShowRoleData(role):
	'''
	显示角色信息
	@param role:
	'''
	qaRole = QAMGR.qarole_dict.get(role.GetRoleID())
	if not qaRole:
		print "GE_EXC, can not find roleId:%s in  QAMGR.qarole_dict while ShowRoleData" % role.GetRoleID()
		return
	item_reward = [(k,v) for k,v in qaRole.item_reward.iteritems()]
	#当前题数，答对数，答错数,奖励金币，奖励物品
	role.SendObj(QandA_Show_Role_Data, (qaRole.rightanswer_no + qaRole.wronganswer_no , qaRole.rightanswer_no, qaRole.money_reward, item_reward))


def CheckAns(role):
	'''
	获得玩家答案
	@param role:
	'''
	pos_x = role.GetPos()[0]
	if pos_x > EnumGameConfig.QandA_the_line:
		return 2
	else:
		return 1



#==========================================
# 场景控制
#===============================================================================
@PublicScene.RegSceneAfterJoinRoleFun(EnumGameConfig.QandA_SCENE_ID)
def AfterJoin(scene, role):
	roleId = role.GetRoleID()
	global QAMGR
	#可能还未初始化,或者答题已经结束
	if not QAMGR:
		return
	#初始化答题角色数据
	if roleId not in QAMGR.qarole_dict:
		QAMGR.qarole_dict[roleId] = QandARole(roleId)
	#判断角色在场景中
	qarole = QAMGR.qarole_dict.get(roleId)
	if not qarole:
		print "GE_EXC, error while qarole = QAMGR.qarole_dict.get(roleId) , no such roleId(%s)" % roleId
		return
	qarole.AfterJoin()
	#显示角色数据
	ShowRoleData(role)
	#显示当前问题
	qandaConfig = question_dict.get(QAMGR.quest_index)
	if not qandaConfig:
		print "GE_EXC, QAMGR.quest_index can not be larger than 30"
		return
	role.SendObj(QandA_Ask, (qandaConfig.index, QAMGR.next_question_time))
	
	


@PublicScene.RegSceneBeforeLeaveFun(EnumGameConfig.QandA_SCENE_ID)
def AfterBeforeLeave(scene, role):
	#判断角色离开场景
	roleID = role.GetRoleID()
	qarole = QAMGR.qarole_dict.get(roleID)
	if not qarole:
		print "GE_EXC, error while qarole = QAMGR.qarole_dict.get(roleID) in AfterBeforeLeave, no such roleID(%s)" % roleID
		return
	qarole.AfterLeave()



#===============================================================================
# 事件
#===============================================================================
def OnRoleClientLost(role, param):
	'''
	角色客户端掉线
	@param role:
	@param param:
	'''
	if role.GetSceneID() == EnumGameConfig.QandA_SCENE_ID:
		role.BackPublicScene()

#===============================================================================
# 时间控制
#===============================================================================
def FiveMinutesReady():
	'''
	【答题】答题活动将在五分钟后正式开始。
	'''
	#系统通知
	cRoleMgr.Msg(11, 0, GlobalPrompt.QandA_READY_BROADCAST_5)
	
def OneMinutesReady():
	'''
	【答题】答题活动将在五分钟后正式开始。
	
	'''
	global IS_READY
	IS_READY = True
	
	global QAMGR
	QAMGR = QandAMgr()		#创建答题管理器
	#入侵准备时间1分钟
	global question_dict
	
	question_dict = RandomQues()
	cComplexServer.RegTick(QandA_READY_DURATION, StartQandA)
	#系统通知
	cRoleMgr.Msg(11, 0, GlobalPrompt.QandA_READY_BROADCAST_1)
	
def QandAEveryThirtySecAsk(callargv, regparam):
	'''
	答题开始后每30秒调用，用来发送问题
	'''
	#答题结束
	if IS_START is False:
		return
	#答题开始后每30秒调用，用来发送问题
	cComplexServer.RegTick(QandA_PER_QUESTION_TIME, QandAEveryThirtySecAsk)
	#答题开始后每29秒调用，用来保存玩家答题数据
	cComplexServer.RegTick(QandA_PER_ANSWER_TIME, QandAEveryTHirtySecSave)
	#出题
	QAMGR.NextQuestion()
	

def QandAEveryTHirtySecSave(callargv, regparam):
	if IS_START is False:
		return
	#问问题后每29秒调用，用来保存玩家数据
	right = question_dict[QAMGR.quest_index].right
	for qarole in QAMGR.qarole_dict.itervalues():
		if not qarole.isLeave :
			#保存玩家数据
			roleID = qarole.role_id
			role = cRoleMgr.FindRoleByRoleID(roleID)
			if not role:
				continue
			SaveRoleAns(role , right)
			#展示玩家答题数据
			ShowRoleData(role)


def StartQandA(callargv, regparam):
	'''
	答题开始
	@param callargv:
	@param regparam:
	'''
	global IS_READY
	IS_READY = False
	
	global IS_START
	IS_START = True
	cRoleMgr.Msg(11, 0, GlobalPrompt.QandA_READY_BROADCAST_0)
	#问答开始，注册结束时间
	cComplexServer.RegTick(QandA_START_DURATION, EndQandA)
	#每30秒调用，用来发送问题以及答案
	QandAEveryThirtySecAsk(1, 1)



def EndQandA(callargv, regparam):
	'''
	答题结束
	@param callargv:
	@param regparam:
	'''
	global IS_START
	global QAMGR
	if IS_START is False:
		return
	#答题活动不可进入
	IS_START = False
	
	#答题奖励
	for roleId, qarole in QAMGR.qarole_dict.iteritems():
		Call.LocalDBCall(roleId, RewardRole, (qarole.money_reward, qarole.item_reward))
		#离线命令设置今日参与了答题
		Call.LocalDBCall(roleId, HasJoinQA, cDateTime.Days())


	#通知客户端答题结束
	QandA_SCENE_ID = EnumGameConfig.QandA_SCENE_ID
	for role in QAMGR.scene.GetAllRole():
		role.SendObj(QandA_End, None)
		#退出答题场景
		if role.GetSceneID() == QandA_SCENE_ID:
			role.BackPublicScene()
	QAMGR = None
		

def HasJoinQA(role, param):
	'''
	设置今日已经参与了答题
	@param role:
	@param param:
	'''
	oldDays = param
	newDays = cDateTime.Days()
	#若跨天则不需要设置
	if newDays > oldDays:
		return
	
	role.SetDI1(EnumDayInt1.QandAJoin, 1)
	
	Event.TriggerEvent(Event.QQidip_Eve, role, QQEventDefine.QQ_QANDA)

#===============================================================================
# 客户端请求
#===============================================================================
def RequestQAEnterScene(role, msg):
	'''
	客户端请求进入入侵场景
	@param role:
	@param msg:
	'''
	#判断时间
	
	if not IS_START:
			return
	#需要等级
	if role.GetLevel() < EnumGameConfig.QandA_NEED_LEVEL:
		return
	
	#北美版
	if Environment.EnvIsNA():
		#今天是否已经参与过答题
		if role.GetDI1(EnumDayInt1.QandAJoin):
			#提示
			role.Msg(2, 0, GlobalPrompt.QandA_Has_Join)
			return
	
	#随机一个点
	x, y = RandomXY(*QandA_ENTER_SCENE_POS)
	role.Revive(EnumGameConfig.QandA_SCENE_ID, x, y)
	
	#每日必做 -- 进入答题场景
	Event.TriggerEvent(Event.Eve_DoDailyDo, role, (DailyDo.Daily_Dati, 1))
	
def RequestQALeaveScene(role, msg):
	'''
	客户端请求离开问答场景
	@param role:
	@param msg:
	'''
	if role.GetSceneID() == EnumGameConfig.QandA_SCENE_ID:
		role.BackPublicScene()


if "_HasLoad" not in dir():	
	if not Environment.IsCross and not Environment.EnvIsQQ() and not Environment.EnvIsQQUnion() and not Environment.EnvIsFT() and not Environment.EnvIsNA() and not Environment.EnvIsYY():
		#旧答题，国服不开放
		if Environment.HasLogic:
			#距离答题开始还有10分钟
			Cron.CronDriveByMinute((2038, 1, 1), FiveMinutesReady, H = "H == 12", M = "M == 55")
			#答题准备
			Cron.CronDriveByMinute((2038, 1, 1), OneMinutesReady, H = "H == 12", M = "M == 59")
		
			#北美版
			if Environment.EnvIsNA():
				#距离答题开始还有10分钟
				Cron.CronDriveByMinute((2038, 1, 1), FiveMinutesReady, H = "H == 17", M = "M == 55")
				#答题准备
				Cron.CronDriveByMinute((2038, 1, 1), OneMinutesReady, H = "H == 17", M = "M == 59")
				
		#事件
		Event.RegEvent(Event.Eve_ClientLost, OnRoleClientLost)
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleClientLost)

		#消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QandA_Enter_Scene", "客户端请求进入答题场景"), RequestQAEnterScene)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QandA_Leave_Scene", "客户端请求离开答题场景"), RequestQALeaveScene)		
		
		
		
