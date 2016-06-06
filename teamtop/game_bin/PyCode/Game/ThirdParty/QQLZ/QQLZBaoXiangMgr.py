#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QQLZ.QQLZBaoXiangMgr")
#===============================================================================
# 蓝钻宝箱Mgr
#===============================================================================
import cRoleMgr
import cDateTime
import cNetMessage
import cComplexServer
import Environment
from Util import Time
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig,GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumObj, EnumInt8, EnumTempInt64, EnumTempObj
from Game.ThirdParty.QQLZ import QQLZBaoXiangConfig
from Game.Role import Event

OPEN_STATE = 1
CLOSE_STATE = 0

if "_HasLoad" not in dir():
	IS_START = False	#蓝钻宝箱活动开启标志
	ENDTIME = 0			#活动结束时间戳
	#消息
	QQLZBaoXiang_ActiveState_Sync = AutoMessage.AllotMessage("QQLZBaoXiang_ActiveState_Sync", "同步蓝钻宝箱活动状态")
	QQLZBaoXiang_BXState_Sync = AutoMessage.AllotMessage("QQLZBaoXiang_BXState_Sync", "同步已经开启的宝箱字典")
	QQLZBaoXiang_Reset_Sync = AutoMessage.AllotMessage("QQLZBaoXiang_Reset_Sync", "同步蓝钻宝箱重置状态")
	QQLZBaoXiang_BXOpen_Sync = AutoMessage.AllotMessage("QQLZBaoXiang_BXOpen_Sync", "同步本次开启的宝箱")
	QQLZBaoXiang_TiamMa_Sync = AutoMessage.AllotMessage("QQLZBaoXiang_TiamMa_Sync", "同步天马流星领取消息")
	
	#日志
	QQLZBaoXiangReward = AutoLog.AutoTransaction("QQLZBaoXiangReward", "QQ蓝钻宝箱开启箱子")
	QQLZBaoXiangTianMaReward = AutoLog.AutoTransaction("QQLZBaoXiangTianMaReward", "QQ蓝钻宝箱领取天马流星")
	QQLZBaoXiangClearData = AutoLog.AutoTransaction("QQLZBaoXiangClearData", "QQ蓝钻宝箱活动结束清理数据")
#============= 活动控制 ====================
#启服之后根据当前时间和活动配置时间 注册tick控制活动
def Initialize():	
	'''
	初始化活动 tick
	'''
	#获取活动配置时间
	activeBase = QQLZBaoXiangConfig.QQLZBaoXiang_Config_Base
	if not activeBase:
		print "GE_EXC, activeBase is None while Initialize QQLZBaoXiang"
		return
	beginDate = activeBase.beginDate
	endDate = activeBase.endDate
	
	#当前日期-时间
	nowDate = cDateTime.Now()
	nowTime = cDateTime.Seconds()
	
	#开始时间戳-结束时间戳
	beginTime = Time.DateTime2UnitTime(beginDate)
	endTime = Time.DateTime2UnitTime(endDate)
	
	if beginDate <= nowDate < endDate:
		#开启 并注册结束tick
		QQLZBaoXiang_Start(None, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZBaoXiang_End)
	elif nowDate < beginDate:
		#注册开启和结束的tick
		cComplexServer.RegTick(beginTime - nowTime, QQLZBaoXiang_Start, endTime)
		cComplexServer.RegTick(endTime - nowTime, QQLZBaoXiang_End)
	
	#如果活动没有结束，对版本号进行检测
	if nowDate < endDate:
		Event.TriggerEvent(Event.Eve_QQCheckVersion, None, (1, beginDate, "QQLZBaoXiang"))

def QQLZBaoXiang_Start(callArgv, regParam):
	'''
	开启蓝钻宝箱
	'''
	global IS_START
	global ENDTIME
	if IS_START:
		print "GE_EXC,repeat start QQLZBaoXiang"
		return
	
	IS_START = True
	ENDTIME = regParam
	cNetMessage.PackPyMsg(QQLZBaoXiang_ActiveState_Sync, (OPEN_STATE, ENDTIME))
	cRoleMgr.BroadMsg()
	

def QQLZBaoXiang_End(callArgv, regParam):
	'''
	结束蓝钻宝箱
	'''
	global IS_START
	if not IS_START:
		print "GE_EXC,close QQLZBaoXiang while not open"
		return
	
	IS_START = False
	cNetMessage.PackPyMsg(QQLZBaoXiang_ActiveState_Sync, (CLOSE_STATE, ENDTIME))
	cRoleMgr.BroadMsg()


def RequestBaoXiang(role, msg):
	'''
	 客户端请求开启一个宝箱
	@param role:
	@param msg is BaoXiang_ID 1-9
	'''
	global IS_START
	if not IS_START:
		return
	
	#判断客户端消息是否正确
	if(msg > 9 or msg < 1):
		return
	
	
	#非蓝钻渠道
	if role.GetTI64(EnumTempInt64.QVIP) != 2:
		return
	
	#判断等级
	roleLevel = role.GetLevel()
	activeBase = QQLZBaoXiangConfig.QQLZBaoXiang_Config_Base
	if roleLevel < activeBase.needLevel:
		return
	LevelSection = QQLZBaoXiangConfig.QQLZBX_LEVEL_DICT[roleLevel]
	#判断宝箱是否已经开启
	BaoXiang_Dict = role.GetObj(EnumObj.QQLZBaoXiang)[1]
	BaoXiang_JiShu = role.GetObj(EnumObj.QQLZBaoXiang)[2]
	if BaoXiang_Dict.get(msg, None):
		return
	
	
	BaoXiang_cnt = len(BaoXiang_JiShu)
	
	if BaoXiang_cnt < 7:
		need_Item_Num = 1
		random_obj = QQLZBaoXiangConfig.QQLZBX_REWARD_RANDOM_DICT_6.get(roleLevel)
	else:
		need_Item_Num = 2
		random_obj = QQLZBaoXiangConfig.QQLZBX_REWARD_RANDOM_DICT_3.get(roleLevel)
	#判断蓝钻密匙够不够
	if(need_Item_Num > role.GetI8(EnumInt8.QQLanZuanKaiTongTimes) - role.GetI8(EnumInt8.QQLZBaoXiangTimes)):
		return
	if not random_obj:
		print "GE_EXC, Can't Find roleLevel(%s) in QQLZBX_REWARD_RANDOM_DICT_6 or QQLZBX_REWARD_RANDOM_DICT_3" % roleLevel
		return	
	
	#随机出一个宝箱
	if BaoXiang_cnt < 8:
		index, coding, cnt = random_obj.RandomOne()
	else:
		itemMany = random_obj.RandomMany(3)
		
		
		index, coding, cnt = random_obj.RandomOne()
		if BaoXiang_cnt == 8:
			if [itemMany[0][0], LevelSection] != BaoXiang_Dict.get(BaoXiang_JiShu[7], None)[:2]:
				index, coding, cnt = itemMany[0]
			else:
				index, coding, cnt = itemMany[1]
		elif BaoXiang_cnt == 9:
			if BaoXiang_Dict.get(BaoXiang_JiShu[7], None)[:2] != [itemMany[0][0], LevelSection] != BaoXiang_Dict.get(BaoXiang_JiShu[8], None)[:2]:
				index, coding, cnt = itemMany[0]
			elif BaoXiang_Dict.get(BaoXiang_JiShu[7], None)[:2] != [itemMany[1][0], LevelSection] != BaoXiang_Dict.get(BaoXiang_JiShu[8], None)[:2]:
				index, coding, cnt = itemMany[1]
			else:
				index, coding, cnt = itemMany[2]
		else:
			print "GE_EXC, Error of BaoXiangJiShu %s" % BaoXiang_cnt
			return	
	#设置宝箱开启状态，保存宝箱对应索引，等级段, 第几次抽奖
	BaoXiang_Dict[msg] = [index, LevelSection, BaoXiang_cnt]
	BaoXiang_JiShu.append(msg)
	
	#给用户发物品
	with QQLZBaoXiangReward:
		role.IncI8(EnumInt8.QQLZBaoXiangTimes, need_Item_Num)
		role.AddItem(coding, cnt)
	
	role.SendObj(QQLZBaoXiang_BXOpen_Sync, [index, LevelSection, BaoXiang_cnt])
	#获得提示及广播
	rewardPrompt = GlobalPrompt.QQLZBXKaiQi+ GlobalPrompt.Reward_Item_Tips % (coding, cnt)
	role.Msg(2, 0, rewardPrompt)
	
	#如果宝箱未全部开启，返回
	if len(BaoXiang_JiShu) < 10:
		return

	role.SendObj(QQLZBaoXiang_Reset_Sync, None)
	#重置宝箱
	for i in range(1,10):
		BaoXiang_Dict[i] = None	
	role.GetObj(EnumObj.QQLZBaoXiang)[2] = [0]
	
	if role.GetI8(EnumInt8.QQLZTianMa) is 2:
		return
	elif role.GetI8(EnumInt8.QQLZTianMa) is 0:
		role.SetI8(EnumInt8.QQLZTianMa, 1)
	

def RequestBaoXiangPanel(role, msg):
	'''
	打开蓝钻宝箱面板
	@param role:
	@param msg is not used:
	'''
	
	role.SendObj(QQLZBaoXiang_BXState_Sync, role.GetObj(EnumObj.QQLZBaoXiang).get(1, None))

def RequestTianMa(role, msg):
	'''
	 客户端请求兑换天马流星
	@param role:
	@param msg is not used
	'''
	global IS_START
	if not IS_START:
		return
	#非蓝钻渠道
	if role.GetTI64(EnumTempInt64.QVIP) != 2:
		return
	activeBase = QQLZBaoXiangConfig.QQLZBaoXiang_Config_Base
	if role.GetLevel() < activeBase.needLevel:
		return
	
	#如果不是可以领取的状态，返回
	if(role.GetI8(EnumInt8.QQLZTianMa) != 1):
		return
	
	TianMaID = EnumGameConfig.QQLZBX_TianMa_ID
	#用户领取天马流星
	with QQLZBaoXiangTianMaReward:
		role.SetI8(EnumInt8.QQLZTianMa, 2)
		role.AddItem(TianMaID, 1)
	role.SendObj(QQLZBaoXiang_TiamMa_Sync, [1])
	#获得提示及广播
	rewardPrompt = GlobalPrompt.QQLZBXTianMa + GlobalPrompt.Reward_Item_Tips % (TianMaID, 1)
	role.Msg(2, 0, rewardPrompt)
	
def RoleDayClear(role, param):
	if not IS_START:
		return
	role.GetObj(EnumObj.QQLZBaoXiang)[1] = {}
	for i in range(1,10):
		role.GetObj(EnumObj.QQLZBaoXiang)[1][i] = None
	role.GetObj(EnumObj.QQLZBaoXiang)[2]=[0]
	role.SendObj(QQLZBaoXiang_Reset_Sync, None)
	
def AfterLogin(role, param):
	
	TianMaID = EnumGameConfig.QQLZBX_TianMa_ID
	BaoXiang_Obj = role.GetObj(EnumObj.QQLZBaoXiang)
	
	if role.ItemCnt(TianMaID) or (TianMaID in role.GetTempObj(EnumTempObj.MountMgr).MountId_list):
		role.SetI8(EnumInt8.QQLZTianMa, 2)
	else:
		role.SetI8(EnumInt8.QQLZTianMa, 0)
	if not BaoXiang_Obj:
		BaoXiang_Obj[1] = {}
		BaoXiang_Obj[2] = [0]
		for i in range(1, 10):
			BaoXiang_Obj[1][i] = None
			

if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#pre_process
		Initialize()
		
		Event.RegEvent(Event.Eve_RoleDayClear, RoleDayClear)
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		#注册消息
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZBXRequestTianMa", "蓝钻宝箱领取天马流星"), RequestTianMa)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZBXRequestBaoXiang", "蓝钻宝箱开启箱子"), RequestBaoXiang)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQLZBXRequestBaoXiangPanel", "蓝钻宝箱打开面板"), RequestBaoXiangPanel)

		
