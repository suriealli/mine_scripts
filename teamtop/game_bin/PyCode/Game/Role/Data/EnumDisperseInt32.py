#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.EnumDisperseInt32")
#===============================================================================
# 角色Int32数组(离散)使用枚举
#===============================================================================
import cRoleDataMgr
from Common import CValue, Coding
from Game.Role.Data import Enum
from ComplexServer.Log import AutoLog

# 禁止reload，具体原因在Game.Login中
assert "_HasLoad" not in dir()

L = []
def F(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient = False, sLogEvent = ""):
	'''
	设置数值规范
	@param uIdx:下标索引
	@param nMinValue:最小值
	@param nMinAction:超过最小值的处理
	@param nMaxValue:最大值
	@param nMaxAction:超过最大值的处理
	@param bSyncClient:数值改变了是否同步客户端
	@param sLogEvent:数值改变了是否记录日志
	'''
	assert uIdx < (Coding.RoleDisperseInt32Range[1] - Coding.RoleDisperseInt32Range[0])
	assert nMinValue >= CValue.MIN_INT32
	assert nMaxValue <= CValue.MAX_INT32
	if sLogEvent: AutoLog.RegEvent(Coding.RoleDisperseInt32Range[0] + uIdx, sLogEvent)
	if not L:
		assert uIdx == 0
	else:
		assert uIdx == L[-1] + 1
	L.append(uIdx)
	cRoleDataMgr.SetDisperseInt32Rule(uIdx, nMinValue, nMinAction, nMaxValue, nMaxAction, bSyncClient, sLogEvent)
	return uIdx

#===============================================================================
# 数组使用定义
#===============================================================================
# 注意下面这个不能改，搜索di32_0
LastActiveUnixTime = 0 # 最后活跃时间（在载入的时候，数据库的时间,请不要用这个值和服务器时间做对比）
F(LastActiveUnixTime, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)

enOnlineTimes = 1 # 总共在线时间 秒
F(enOnlineTimes, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)

enLastClearDays = 2 # 最后清理日期(天的时间戳)(可以用于判断今天是否登录过)
F(enLastClearDays, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)

CanLoginTime = 3 #下次可登录的时间(封号)
CanChatTime = 4 #下次可聊天的时间(禁言)
F(CanLoginTime, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, False, "封号时间")
F(CanChatTime, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "禁言时间")

Version = 5 #角色数据版本
F(Version, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, False, "更新角色版本号")

ConsumeQPoint = 6 #玩家消费的Q点
F(ConsumeQPoint, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "玩家消费的Q点")

enSex = 7 #性别
F(enSex, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "设置性别")
enCareer = 8 #职业 物理,法术
F(enCareer, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoIgnore, True, "设置职业")

ZDL = 9 #战斗力 (必须保存到数据库，需要查询离线玩家的战斗力)
F(ZDL, 0, Enum.DoIgnore, CValue.MAX_INT32, Enum.DoIgnore, True)

FirstLoginTimes = 10 #第一登陆时间
F(FirstLoginTimes, 0, Enum.DoIgnore, CValue.MAX_INT32, Enum.DoIgnore, True, "第一登陆时间")

enLevel = 11#角色等级
F(enLevel, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "改变等级")

enVIP = 12 #vip等级
F(enVIP, 0, Enum.DoIgnore, 10, Enum.DoKick, True, "设置VIP")

enUnbindRMB_Q = 13 #非绑定RMB(充值获得)
F(enUnbindRMB_Q, 0, Enum.DoKick, CValue.MAX_INT32, Enum.DoKick, True, "改变非绑定RMB(充值获得)")

enBindRMB = 14 #绑定RMB
F(enBindRMB, 0, Enum.DoKick, CValue.MAX_INT32, Enum.DoKick, True, "改变绑定RMB")

LastSaveProcessID = 15 #最后保存的进程ID
LastSaveUnixTime = 16 #最后保存的进程时间
F(LastSaveProcessID, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)
F(LastSaveUnixTime, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing)

HuangZuan_Y_H_L = 17#黄钻 (高16位 低8位年费， 高8位豪华)， (低16位 等级)
LanZuan_Y_H_L = 18#蓝钻 (高16位 低8位年费， 高8位豪华)， (低16位 等级)
F(HuangZuan_Y_H_L, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)
F(LanZuan_Y_H_L, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

RoleGrade = 19#角色品阶
F(RoleGrade, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "角色品阶")

RightMountID = 20 #当前骑乘的坐骑ID
F(RightMountID, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

FTVIP = 21 #繁体VIP 0:没有  1：黄钻      2：蓝钻 
F(FTVIP, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True)

GM_UnbindRMB = 22 #内部号发的神石记录
F(GM_UnbindRMB, 0, Enum.DoKick, CValue.MAX_INT32, Enum.DoKick, False, "内部号发的神石记录")

CampID = 23 #阵营ID   1： 联盟      2：部落
F(CampID, 0, Enum.DoIgnore, CValue.MAX_INT32, Enum.DoIgnore, True, "阵营ID")

enUnbindRMB_S = 24 #非绑定RMB(服务器发放获得)
F(enUnbindRMB_S, 0, Enum.DoKick, CValue.MAX_INT32, Enum.DoKick, True, "改变非绑定RMB(服务器发放获得)")

HerFuRecord = 25 #合服记录，如果和worlddata中的不一样，则需要触发一次合服处理
F(HerFuRecord, 0, Enum.DoKick, CValue.MAX_INT32, Enum.DoKick, False, "合服记录")

DayConsumeRMB = 26#每日消费神石
F(DayConsumeRMB, 0, Enum.DoKick, CValue.MAX_INT32, Enum.DoKick, False)

DayConsumeRMB_Q = 27#每日消费充值神石
F(DayConsumeRMB_Q, 0, Enum.DoKick, CValue.MAX_INT32, Enum.DoKick, True)

OpenYearLoginDays = 28#登录的Unix时间戳(天数) 
F(OpenYearLoginDays, 0, Enum.DoKick, CValue.MAX_INT32, Enum.DoKick, False)

TheMammonDays = 29#天降财神最近一次返利的时间戳(天数) 
F(TheMammonDays, 0, Enum.DoKick, CValue.MAX_INT32, Enum.DoKick, False, "天降财神最近一次返利的时间戳")

OldServerBackDays_OS = 30#老服回流玩家回流的时间戳(天数)OS = Old Server回流至老服
F(OldServerBackDays_OS, 0, Enum.DoKick, CValue.MAX_INT32, Enum.DoKick, True, "老玩家回流（回流至老服）时间戳")

OldRoleBackDays_FT = 31#【繁体版】老服回流玩家回流的时间戳(天数)
F(OldRoleBackDays_FT, 0, Enum.DoKick, CValue.MAX_INT32, Enum.DoKick, True, "老玩家回流（繁体版）时间戳")

enZhuanShengHaloLv = 32 #角色转生光环等级
F(enZhuanShengHaloLv, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "改变角色转生光环等级")

enZhuanShengLv = 33 #角色转生等级
F(enZhuanShengLv, 0, Enum.DoNothing, CValue.MAX_INT32, Enum.DoNothing, True, "改变角色转生等级")
