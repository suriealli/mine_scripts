#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ValentineDay.RoseRebateMgr")
#===============================================================================
# 玫瑰返利Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Other import GlobalPrompt
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from Game.Role import Event
from Game.Persistence import Contain
from Game.Activity import CircularDefine
from Game.SysData import WorldDataNotSync
from Game.Role.Data import EnumInt16, EnumObj
from Game.Activity.ValentineDay import RoseRebateConfig, ValentineVersionMgr

IDX_ROSEREBATE = 1
if "_HasLoad" not in dir():
	IS_START = False
	
	
	RoseRebate_SendRecordData_S = AutoMessage.AllotMessage("RoseRebate_SendRecordData_S", "玫瑰返利_同步最新赠送达标数据")
	RoseRebate_RewardRecordData_S = AutoMessage.AllotMessage("RoseRebate_RewardRecordData_S", "玫瑰返利_同步最新已领奖记录")
	RoseRebate_SendRecordAndRewardRecord_S = AutoMessage.AllotMessage("RoseRebate_SendRecordAndRewardRecord_S", "玫瑰返利_上线同步本服达标数和角色领奖记录")
	
	Tra_RoseRebate_GetRebateReward = AutoLog.AutoTransaction("Tra_RoseRebate_GetRebateReward", "玫瑰返利_领取贵族返利奖励")
	
#### 活动控制  start ####
def OnStartRoseRebate(*param):
	'''
	开启活动
	'''
	_, circularType = param
	if CircularDefine.CA_RoseRebate != circularType:
		return
	
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open RoseRebate"
		return
		
	IS_START = True
	UpdateVersion()

def OnEndRoseRebate(*param):
	'''
	结束活动
	'''
	_, circularType = param
	if CircularDefine.CA_RoseRebate != circularType:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC, end RoseRebate while not start"
		return
		
	IS_START = False

#### 客户端请求 start 
def OnGetRebateReward(role, msg):
	'''
	玫瑰返利_请求领取贵族返利奖励
	@param msg: rebateCategory,rebateType (返利大类 返利小类)
	'''
	if not IS_START:
		return
	
	#参数 --> 配置
	rebateCategory, rebateType = msg
	rebateCfg = RoseRebateConfig.GetRebateCfg(rebateCategory, rebateType)
	if not rebateCfg:
		return
	
	if role.GetVIP() < rebateCfg.needVIP:
		return
	
	#获取对应返利条目 根据领取记录 判断此次请求是否放行
	rebateRewardRecord = role.GetObj(EnumObj.ValentineDayData)[IDX_ROSEREBATE]
	gottenCnt = (rebateRewardRecord.get(rebateCategory, {})).get(rebateType, 0)
	totalSatisifyNum = len(RoseRebate_SendRecord_Dict.get(rebateCategory, set()))
	if gottenCnt >= totalSatisifyNum:
		return
	
	#达标人数不足 没有解锁此项返利
	if totalSatisifyNum < rebateCfg.needTotalNum:
		return
	
	
	prompt = GlobalPrompt.RoseRebate_Tips_Head
	with Tra_RoseRebate_GetRebateReward:
		#更新角色返利奖励领取记录
		rebateRecordDict = rebateRewardRecord.setdefault(rebateCategory, {})
		rebateRecordDict[rebateType] = gottenCnt + 1
		role.GetObj(EnumObj.ValentineDayData)[IDX_ROSEREBATE] = rebateRewardRecord
		#返利奖励实际获得
		coding, cnt = rebateCfg.rebateItem
		prompt += GlobalPrompt.RoseRebate_Tips_Item % (coding, cnt)
		role.AddItem(coding, cnt)
	
	#同步最新已领奖返利的记录
	role.SendObj(RoseRebate_RewardRecordData_S, rebateRewardRecord)
	
	#领取成功提示
	role.Msg(2, 0, prompt)

#### 事件处理 start 
def AfterSendRose(role, param):
	'''
	玩家送99朵玫瑰花后 触发处理是否达标 是否新增达标人数处理
	'''
	if not IS_START:
		return
	
	#根据配置每一返利大项去判断此次赠送是否有效增加达标人数 并更新数据同步
	hasChange = False
	roleId = role.GetRoleID()
	global RoseRebate_SendRecord_Dict	
	curSendTimes = role.GetI16(EnumInt16.RosePresentSendTimes)
	for rebateCategory, rebateCfgDict in RoseRebateConfig.RoseRebate_BaseConfig_Dict.iteritems():
		for _, rebateCfg in rebateCfgDict.iteritems():
			if curSendTimes >= rebateCfg.needRoseNum:
				oldRoleSet = RoseRebate_SendRecord_Dict.setdefault(rebateCategory, set())
				if roleId not in oldRoleSet:
					oldRoleSet.add(roleId)
					RoseRebate_SendRecord_Dict[rebateCategory] = oldRoleSet
					RoseRebate_SendRecord_Dict.changeFlag = True
					hasChange = True
				else:
					pass
			else:
				pass
			break	#每个返利大类一次判断是否记录对应达标角色的roleId即可   此处嵌套遍历是为了拿到rebateCfg去做逻辑 
	
	#全局赠送达标记录数据有变 同步给所有在线玩家
	if hasChange:
		#组装每个返利大类的达标人数数据
		rebateSendRecord = {}
		for rebateCategory, roleIds in RoseRebate_SendRecord_Dict.iteritems():
			rebateSendRecord[rebateCategory] = len(roleIds)
			
		for tmpRole in cRoleMgr.GetAllRole():
			tmpRole.SendObj(RoseRebate_SendRecordData_S, rebateSendRecord)
	else:
		pass
	
def OnSyncRoleOtherData(role, param):
	'''
	1.同步最新玫瑰赠送达标数据
	2.同步已领取返利奖励数据
	'''
	if not IS_START:
		return
	
	#组装每个返利大类的达标人数数据
	rebateSendRecord = {}
	for rebateCategory, roleIds in RoseRebate_SendRecord_Dict.iteritems():
		rebateSendRecord[rebateCategory] = len(roleIds)
		
	rebateRewardRecord = role.GetObj(EnumObj.ValentineDayData)[IDX_ROSEREBATE]	
	#合并到一条消息去发送给前端直接做逻辑
	role.SendObj(RoseRebate_SendRecordAndRewardRecord_S, (rebateSendRecord, rebateRewardRecord))

def OnRoleInit(role, param):
	'''
	初始角色相关Obj的key
	'''
	valentineDayData = role.GetObj(EnumObj.ValentineDayData)
	if IDX_ROSEREBATE not in valentineDayData:
		valentineDayData[IDX_ROSEREBATE] = {}

def UpdateVersion(calParam = None, regParam = None):
	'''
	玫瑰返利数据载回 根据活动版本号 和 记录版本号 处理数据
	'''
	global RoseRebate_SendRecord_Dict
	if not RoseRebate_SendRecord_Dict.returnDB:
#		print "GE_EXC, roseRebate:: not returnDB"
		return
	
	if not WorldDataNotSync.WorldDataPrivate.returnDB:
#		print "GE_EXC, roseRebate:: not WorldDataPrivate.returnDB"
		return
	
	if not IS_START:
#		print "GE_EXC, roseRebate:: not IS_START"
		return
	
	curVersion = ValentineVersionMgr.ValentineVersion
	dateVersion = WorldDataNotSync.GetRoseRebateVersion()
	if curVersion == dateVersion:
		return
	
	if curVersion < dateVersion:
		print "GE_EXC, RoseRebateMgr::UpdateVersion curVersion(%s) < dateVersion (%s)" % (curVersion, dateVersion)
		return 
	
	with ValentineVersionMgr.Tra_Valentine_UpdateVersion:
		#日志记录下清除掉的数据 
		AutoLog.LogBase(AutoLog.SystemID, AutoLog.eveUpdateRoseRebateVersion, (curVersion, dateVersion, RoseRebate_SendRecord_Dict.data ))
		WorldDataNotSync.SetRoseRebateVersion(curVersion)
		RoseRebate_SendRecord_Dict.clear()
	
if "_HasLoad" not in dir():
	if Environment.HasLogic and not Environment.IsCross:
		#持久化数据 活动期间送99朵玫瑰花统计数据 {rebateCategory:set(),} 其中set保存已经标记了达标的角色roleId 防止重复计算totalNum
		RoseRebate_SendRecord_Dict = Contain.Dict("RoseRebate_SendRecord_Dict", (2038, 1, 1), UpdateVersion) 
		
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartRoseRebate)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndRoseRebate)
		Event.RegEvent(Event.Eve_AfterSendRose, AfterSendRose)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, OnSyncRoleOtherData)
		Event.RegEvent(Event.Eve_InitRolePyObj, OnRoleInit)
		Event.RegEvent(Event.Eve_AfterLoadWorldDataNotSync, UpdateVersion)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RoseRebate_OnGetRebateReward", "玫瑰返利_请求领取贵族返利奖励"), OnGetRebateReward)