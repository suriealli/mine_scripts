#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.ThanksGiving.TGRechargeRewardMgr")
#===============================================================================
# 充值送豪礼Mgr
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig, GlobalPrompt
from ComplexServer.Log import AutoLog
from Game.Role.Mail import Mail
from Game.Role import Event, Call
from Game.Persistence import Contain
from Game.Activity import CircularDefine
from Game.Activity.ThanksGiving import ThanksGivingConfig
from Game.Role.Data import EnumInt32, EnumDayInt8, EnumTempInt64
from Game.SysData import WorldDataNotSync

if "_HasLoad" not in dir():
	IS_START = False	#充值送豪礼活动开关标志	
	TG_RECHARGEREWARD_PRECIOUSRECORD_LIST = []	#大奖记录 [(roleName,coding,cnt) or (roleName),] 前者表示物品奖励 后者表示CDK奖励
	TG_RECHARGEREWARD_OPENPANEL_ROLEID_SET = set()	#当前打开操作面板的玩家ID	
	
	TG_RechargeReward_Lottery_SB = AutoMessage.AllotMessage("TG_RechargeReward_Lottery_SB", "充值送豪礼抽奖结果")
	TG_RechargeReward_PreciousRecord_S = AutoMessage.AllotMessage("TG_RechargeReward_PreciousRecord_S", "充值送豪礼大奖记录")
	
	Tra_TGRechargeReward_RewardTimes = AutoLog.AutoTransaction("Tra_TGRechargeReward_RewardTimes","领取充值获得的抽奖次数")
	Tra_TGRechargeReward_LotteryReward = AutoLog.AutoTransaction("Tra_TGRechargeReward_LotteryReward","充值送豪礼抽奖")

def OnStartTGRecharge(*param):
	'''
	开启充值送豪礼
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_TGRechargeReward:
		return
	
	# 已开启 
	global IS_START
	if IS_START:
		print "GE_EXC,repeat open TGRecharge"
		return
		
	IS_START = True	

def OnEndTGRecharge(*param):
	'''
	关闭充值送豪礼
	'''
	_, circularType = param
	if circularType != CircularDefine.CA_TGRechargeReward:
		return
	
	# 未开启 
	global IS_START
	if not IS_START:
		print "GE_EXC,end TGRecharge while not open "
		return
		
	IS_START = False	

def OnGetRewardTimes(role, msg):
	'''
	领取今日单笔充值 奖励的抽奖次数
	@param msg: rewardIndex 
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.TG_RechargeReward_NeedLevel:
		return
	
	#今日已领取
	rewardIndex = msg
	todayRewardIdx = role.GetI32(EnumInt32.TGRechargeRewardRecord)
	if rewardIndex & todayRewardIdx:
		return
	
	rewardCfg = ThanksGivingConfig.TG_RECHARGEREWARD_TIMES_DICT.get(rewardIndex)
	if not rewardCfg:
		print "GE_EXC, error rewardIndex(%s) can not get rewardCfg" % rewardIndex
		return
	
	#最大单笔充值不达标 
	rechargeRMB = role.GetI32(EnumInt32.TGRechargeRewardMaxToday)
	if rechargeRMB < rewardCfg.needRMBOnce:
		return
	
	with Tra_TGRechargeReward_RewardTimes:
		#更新领取记录
		role.IncI32(EnumInt32.TGRechargeRewardRecord, rewardIndex)
		#增加有效抽奖次数
		role.IncDI8(EnumDayInt8.TGRechargeRewardRechargeTimes, rewardCfg.rewardTimes)

def OnLotteryReward(role, msg = None):
	'''
	请求抽奖
	'''
	if not IS_START:
		return
	
	roleLevel = role.GetLevel()
	if roleLevel < EnumGameConfig.TG_RechargeReward_NeedLevel:
		return
	
	#各种剩余次数
	rechargeTimes = role.GetDI8(EnumDayInt8.TGRechargeRewardRechargeTimes)
	inviteTimes = role.GetDI8(EnumDayInt8.TGRechargeRewardInviteTimes)
	onlineTimes = role.GetDI8(EnumDayInt8.TGRechargeRewardOnlineTimes)
	
	#根据不同平台 统计剩余次数
	effectTimes = 0
	is3366 = role.GetTI64(EnumTempInt64.Is3366)
	isQQGame = role.GetTI64(EnumTempInt64.IsQQGame)	
	if is3366 or isQQGame:
		effectTimes = rechargeTimes + inviteTimes + onlineTimes
	else:
		effectTimes = rechargeTimes
	
	#有效次数不足
	if effectTimes < 1:
		return
	
	#判定奖励用哪一套 
	rewardType = 0
	if is3366 or isQQGame:
		if onlineTimes > 0:
			rewardType = ThanksGivingConfig.QQHALL_ONLINEREWARD
		elif inviteTimes > 0:
			rewardType = ThanksGivingConfig.QQHALL_INVITEFRIEND
		elif rechargeTimes > 0:
			rewardType = ThanksGivingConfig.QQHALL_RECHARGEREWARD
		else:
			pass
	else:
		if rechargeTimes > 0:
			rewardType = ThanksGivingConfig.OTHERS_RECHARGEREWARD
	
	#物品奖励随机器
	rewardRandomer = ThanksGivingConfig.GetRewardRandomerByTypeAndLevel(rewardType, roleLevel)
	if not rewardRandomer:
		print "GE_EXC,can not get rewardRandomer by level(%s)" % roleLevel
		return
	
	#检测是否还有剩余CDK奖励可用
	hasCDK = False
	global TG_RechargeReward_UsedCDKRewardId_List
	localServerCDKRewardIdSet = ThanksGivingConfig.GetLocalServerCDKRewardIdSet()
	localServerCDKRewardIdSet.difference_update(TG_RechargeReward_UsedCDKRewardId_List)
	if len(localServerCDKRewardIdSet) > 0:
		hasCDK = True
	
	#有剩余CDK 并且 今日产出指标还有剩余 增加一个CDK的随机奖项
	toDayCDKOutPut = WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.ToDayCDKOutPut]
	if hasCDK and toDayCDKOutPut < EnumGameConfig.TG_RechargeReward_CDK_DayMax:
		rateValue = ThanksGivingConfig.GetCDKRateByTypeAndLevel(rewardType, roleLevel)
		rewardRandomer.AddRandomItem(rateValue, (ThanksGivingConfig.CDK_REWARD, 0))
	
	#随机奖励
	reward = rewardRandomer.RandomOne()
	if not reward:
		print "GE_EXC,rewardRandomer can not random one on OnLotteryReward"
		return
	
	CDKRewardId = None
	nomalRewardId = None
	if reward[0] == ThanksGivingConfig.CDK_REWARD:
		#抽到CDK奖励了
		CDKRewardId = localServerCDKRewardIdSet.pop()
		if CDKRewardId in TG_RechargeReward_UsedCDKRewardId_List:
			print "GE_EXC, get an used cdkrewardID(%s) in TG_RechargeReward_UsedCDKRewardId_List" % CDKRewardId
			return
		#记录已抽出的CDK奖励ID
		TG_RechargeReward_UsedCDKRewardId_List.append(CDKRewardId)
		TG_RechargeReward_UsedCDKRewardId_List.changeFlag = True
		#更新本服今日CDK产出
		WorldDataNotSync.WorldDataPrivate[WorldDataNotSync.ToDayCDKOutPut] = toDayCDKOutPut + 1
		WorldDataNotSync.WorldDataPrivate.HasChange()
	elif reward[0] == ThanksGivingConfig.NOMAL_REWARD:
		#没有抽到CDK
		nomalRewardId = reward[1]
	else:
		pass
	
	#根据rewardType扣除对应次数
	with Tra_TGRechargeReward_LotteryReward:
		if rewardType == ThanksGivingConfig.QQHALL_ONLINEREWARD:
			role.DecDI8(EnumDayInt8.TGRechargeRewardOnlineTimes, 1)
		elif rewardType == ThanksGivingConfig.QQHALL_INVITEFRIEND:
			role.DecDI8(EnumDayInt8.TGRechargeRewardInviteTimes, 1)
		else:
			role.DecDI8(EnumDayInt8.TGRechargeRewardRechargeTimes, 1)
	
	#同步抽奖结果 等待回调
	roleId = role.GetRoleID()
	roleName = role.GetRoleName()
	if CDKRewardId:
		role.SendObjAndBack(TG_RechargeReward_Lottery_SB, (ThanksGivingConfig.CDK_REWARD, CDKRewardId), 8, LotteryCallBack, (ThanksGivingConfig.CDK_REWARD, CDKRewardId, roleId, roleName))
	elif nomalRewardId:
		role.SendObjAndBack(TG_RechargeReward_Lottery_SB, (ThanksGivingConfig.NOMAL_REWARD, nomalRewardId), 8, LotteryCallBack, (ThanksGivingConfig.NOMAL_REWARD, nomalRewardId, roleId, roleName))

def LotteryCallBack(role, callargv, regparam):
	'''
	抽奖回调 
	'''
	rewardType, rewardId, roleId, roleName = regparam
	if rewardType == ThanksGivingConfig.CDK_REWARD:
		#CDK中奖处理
		rewardCfg = ThanksGivingConfig.TG_RECHARGEREWARD_CDK_BASE_DICT.get(rewardId)
		if not rewardCfg:
			print "GE_EXC, can not get rewardCfg with rewardId(%s) in TG_RECHARGEREWARD_CDK_BASE_DICT" % rewardId
			return
		
		#邮件
		title = GlobalPrompt.TG_RechargeReward_Mail_CDK_TiTle
		sender = GlobalPrompt.TG_RechargeReward_Mail_CDK_Sender
		content = GlobalPrompt.TG_RechargeReward_Mail_CDK_Content % rewardCfg.cdkey
		with Tra_TGRechargeReward_LotteryReward:
			Mail.SendMail(roleId, title, sender, content)
			AutoLog.LogBase(roleId, AutoLog.eveTGRechargeRewardCDK, (rewardId, rewardCfg.cdkey))
			
		#大奖记录 及 公告 处理
		recordInfo = (roleName, 0, 0)
		ProcessPreciousReward(role, (roleId, recordInfo, rewardType, rewardCfg.isPrecious))
		
	elif rewardType == ThanksGivingConfig.NOMAL_REWARD:
		#非CDK中奖处理
		rewardCfg = ThanksGivingConfig.TG_RECHARGEREWARD_ITEMS_BASE_DICT.get(rewardId)
		if not rewardCfg:
			print "GE_EXC, can not get rewardCfg with rewardId(%s) in TG_RECHARGEREWARD_ITEMS_BASE_DICT" % rewardId
			return
		
		coding, cnt = rewardCfg.item
		Call.LocalDBCall(roleId, TGLotteryNomalReward, (coding, cnt))
		#大奖处理
		if rewardCfg.isPrecious :
			recordInfo = (roleName, coding, cnt)
			ProcessPreciousReward(role, (roleId, recordInfo, rewardType, rewardCfg.isPrecious))
	else:
		pass

def TGLotteryNomalReward(role, param):
	'''
	充值送豪礼 物品奖励获得
	'''
	coding, cnt = param
	with Tra_TGRechargeReward_LotteryReward:
		role.AddItem(coding, cnt)	
	role.Msg(2, 0, GlobalPrompt.TG_RechargeReward_Tips_Head + GlobalPrompt.TG_RechargeReward_Tips_Item % (coding, cnt))

def ProcessPreciousReward(role, param):
	'''
	抽出大奖 记录 和 公告 处理
	'''
	rewardRoleId, recordInfo, rewardType, isPrecious = param 
	roleName, coding, cnt = recordInfo
	global TG_RECHARGEREWARD_PRECIOUSRECORD_LIST
	#更新大奖记录
	if isPrecious:
		if len(TG_RECHARGEREWARD_PRECIOUSRECORD_LIST) >= EnumGameConfig.TG_RechargeReward_RecordNum:
			TG_RECHARGEREWARD_PRECIOUSRECORD_LIST.pop(0)
		TG_RECHARGEREWARD_PRECIOUSRECORD_LIST.append(recordInfo)
	
	#在线
	if not role.IsKick():
		#获得CDK奖励提示获得奖励邮件
		if rewardType == ThanksGivingConfig.CDK_REWARD:
			role.Msg(2, 0, GlobalPrompt.TG_RechargeReward_Tips_MailPrompt)
		#并同步最新大奖记录	
		if isPrecious:
			role.SendObj(TG_RechargeReward_PreciousRecord_S, TG_RECHARGEREWARD_PRECIOUSRECORD_LIST)
	
	#CDK奖励公告
	if rewardType == ThanksGivingConfig.CDK_REWARD:
		cRoleMgr.Msg(1, EnumGameConfig.PLATFORM_MSG_LanZuan, GlobalPrompt.TG_RechargeReward_Msg_Precious_CDK % roleName)
	elif rewardType == ThanksGivingConfig.NOMAL_REWARD and isPrecious:
		#物品珍贵奖励公告
		cRoleMgr.Msg(1, 0, GlobalPrompt.TG_RechargeReward_Msg_Precious_Item % (roleName, coding, cnt))
	else:
		pass
	
	#同步最新大奖记录给其他打开面板的玩家	
	offlineRoleSet = set()
	global TG_RECHARGEREWARD_OPENPANEL_ROLEID_SET
	for tmpRoleId in TG_RECHARGEREWARD_OPENPANEL_ROLEID_SET:
		if rewardRoleId == tmpRoleId:
			continue
		tmpRole = cRoleMgr.FindRoleByRoleID(tmpRoleId)
		if not tmpRole:
			offlineRoleSet.add(tmpRoleId)
			continue
		tmpRole.SendObj(TG_RechargeReward_PreciousRecord_S, TG_RECHARGEREWARD_PRECIOUSRECORD_LIST)
	#删除掉不在线的roleId
	TG_RECHARGEREWARD_OPENPANEL_ROLEID_SET.difference_update(offlineRoleSet)

def OnOpenPanel(role, msg = None):
	'''
	打开面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.TG_RechargeReward_NeedLevel:
		return
	
	global TG_RECHARGEREWARD_OPENPANEL_ROLEID_SET
	TG_RECHARGEREWARD_OPENPANEL_ROLEID_SET.add(role.GetRoleID())
	
	role.SendObj(TG_RechargeReward_PreciousRecord_S, TG_RECHARGEREWARD_PRECIOUSRECORD_LIST)
	
def OnClosePanel(role, msg = None):
	'''
	关闭面板
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.TG_RechargeReward_NeedLevel:
		return
	
	global TG_RECHARGEREWARD_OPENPANEL_ROLEID_SET
	TG_RECHARGEREWARD_OPENPANEL_ROLEID_SET.discard(role.GetRoleID())

def AfterChangeUnbindRMB_Q(role, param):
	'''
	神石改变时间处理
	'''
	global IS_START
	if not IS_START: 
		return
	
	if role.GetLevel() < EnumGameConfig.TG_RechargeReward_NeedLevel:
		return
	
	oldValue, newValue = param
	if newValue <= oldValue:
		return
	
	#增加今日充值神石数
	rechargeRMB = newValue - oldValue
	role.IncI32(EnumInt32.TGRechargeRewardMaxToday, rechargeRMB)

def AfterInvite(role, param):
	'''
	邀请好友成功增加次数
	'''
	if not IS_START:
		return
	
	if role.GetLevel() < EnumGameConfig.TG_RechargeReward_NeedLevel:
		return
	
	newInviteTimes = role.GetDI8(EnumDayInt8.TGToDayInviteTimes) + 1
	needInviteTimes = EnumGameConfig.TG_RechargeReward_NeedInviteTimes
	if needInviteTimes == newInviteTimes:
		role.IncDI8(EnumDayInt8.TGRechargeRewardInviteTimes, 1)
	
	role.IncDI8(EnumDayInt8.TGToDayInviteTimes, 1)

def OnRoleLost(role, param):
	'''
	掉线处理
	'''
	if not IS_START:
		return
	
	roleId = role.GetRoleID()
	global TG_RECHARGEREWARD_OPENPANEL_ROLEID_SET
	TG_RECHARGEREWARD_OPENPANEL_ROLEID_SET.discard(roleId)

def OnRoleDayClear(role, param):
	'''
	充值充值神石数 和 奖励次数领取记录
	'''
	role.SetI32(EnumInt32.TGRechargeRewardMaxToday, 0)
	role.SetI32(EnumInt32.TGRechargeRewardRecord, 0)
	
if "_HasLoad" not in dir():
	if Environment.HasLogic:
		Event.RegEvent(Event.AfterChangeUnbindRMB_Q, AfterChangeUnbindRMB_Q)
		
		Event.RegEvent(Event.Eve_RoleDayClear, OnRoleDayClear)
	
	if Environment.HasLogic and (Environment.EnvIsQQ() or Environment.IsDevelop):
		Event.RegEvent(Event.Eve_AfterInviteQQFriend, AfterInvite)
	
	if Environment.HasLogic and not Environment.IsCross:
		#记录本服抽奖已放出的CDK对应rewardId [rewardId1,rewardId2,]
		TG_RechargeReward_UsedCDKRewardId_List = Contain.List("TG_RechargeReward_UsedCDKRewardId_List")	
		
		Event.RegEvent(Event.Eve_StartCircularActive, OnStartTGRecharge)
		Event.RegEvent(Event.Eve_EndCircularActive, OnEndTGRecharge)
		Event.RegEvent(Event.Eve_BeforeExit, OnRoleLost)
		Event.RegEvent(Event.Eve_ClientLost, OnRoleLost)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TG_RechargeReward_OnGetRewardTimes", "请求领取充值对应次数奖励"), OnGetRewardTimes)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TG_RechargeReward_OnLotteryReward", "请求抽奖"), OnLotteryReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TG_RechargeReward_OnOpenPanel", "打开抽奖面板"), OnOpenPanel)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("TG_RechargeReward_OnClosePanel", "关闭抽奖面板"), OnClosePanel)