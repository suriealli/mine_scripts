#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WeiXin.WeiXin")
#===============================================================================
# 微信关注
#===============================================================================
import Environment
import cRoleMgr
import cComplexServer
from Common.Message import AutoMessage, PyMessage
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.Control import ControlProxy
from Game.Activity.WeiXin import WeiXinConfig
from Game.Role.Data import EnumInt8, EnumObj
from Game.Role import Event
from Game.SysData import WorldData

if "_HasLoad" not in dir():
	#消息
	WeiXinTargetData = AutoMessage.AllotMessage("WeiXinTargetData", "微信关注目标达成数据")

	#日志
	WeiXinReward_Log = AutoLog.AutoTransaction("WeiXinReward_Log", "领取微信关注奖励")
	WeiboZoneReward_Log = AutoLog.AutoTransaction("WeiboZoneReward_Log", "领取微博空间分享奖励")

	
def RequestWeiXinReward(role, msg):
	'''
	领取微信关注奖励
	@param role:
	@param msg:
	'''
	index = msg
	if not index: return
	
	cfg = WeiXinConfig.WeiXin_Dict.get(index)
	if not cfg:
		print "GE_EXC, RequestWeiXinReward can not find index (%s) in WeiXin_Dict" % index
		return
	
	#关注人数不满足条件
	if WorldData.GetWeiXinAttentionCnt() < cfg.needCnt:
		return
	
	#已领取过奖励
	if index in role.GetObj(EnumObj.WeiXinTarget)[1]:
		return
	
	#背包满
	if role.PackageIsFull():
		return
	
	role.GetObj(EnumObj.WeiXinTarget)[1].add(index)
	
	#发放奖励
	with WeiXinReward_Log:
		role.AddItem(*cfg.rewards)
	
	role.SendObj(WeiXinTargetData, role.GetObj(EnumObj.WeiXinTarget)[1])
	
def RequestWeiboZoneShare(role, msg):
	'''
	请求微博空间分享
	@param role:
	@param msg:
	'''
	index = msg
	if not index: return
	
	nowIndex = role.GetI8(EnumInt8.WeiboZoneIndex)
	if index != nowIndex + 1:
		return
	
	if not nowIndex:
		nowIndex = 1
	
	#已领取奖励
	if nowIndex == -1:
		return
	
	cfg = WeiXinConfig.WeiboZone_Dict.get(nowIndex)
	if not cfg:
		return
	
	#已完成
	if cfg.nextIndex == -1:
		return
	
	role.SetI8(EnumInt8.WeiboZoneIndex, index)

def RequestWeiboZoneReward(role, msg):
	'''
	领取微博空间奖励
	@param role:
	@param msg:
	'''
	nowIndex = role.GetI8(EnumInt8.WeiboZoneIndex)
	
	#已领取奖励
	if nowIndex == -1:
		return
	
	cfg = WeiXinConfig.WeiboZone_Dict.get(nowIndex)
	if not cfg:
		return
	
	#未完成
	if cfg.nextIndex != -1:
		return
	
	#背包空间不足
	if role.PackageEmptySize() < len(cfg.rewards):
		return
	
	#设置任务完成
	role.SetI8(EnumInt8.WeiboZoneIndex, -1)
	
	#发放奖励
	with WeiboZoneReward_Log:
		for item in cfg.rewards:
			role.AddItem(*item)
	
def AfterLogin(role, msg):
	if role.GetObj(EnumObj.WeiXinTarget):
		return
	role.SetObj(EnumObj.WeiXinTarget, {1:set()})
	
def SyncRoleOtherData(role, msg):
	role.SendObj(WeiXinTargetData, role.GetObj(EnumObj.WeiXinTarget)[1])


def UpdateWeiXinGuanZhuCnt(sessionid, msg):
	'''
	控制进程发来了微信关注人数
	@param sessionid:
	@param msg:
	'''
	WorldData.SetWeiXinAttentionCnt(msg)
	
def AfterLoadWorldData(param1, param2):
	#请求获取微信关注人数
	ControlProxy.SendControlMsg(PyMessage.Control_GetWeiXinGuanZhuCnt, None)


if "_HasLoad" not in dir():
	
	if Environment.HasLogic and Environment.EnvIsQQ() and not Environment.IsCross:
		Event.RegEvent(Event.Eve_AfterLogin, AfterLogin)
		Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
		#尝试获取一下微信关注人数
		Event.RegEvent(Event.Eve_AfterLoadWorldData, AfterLoadWorldData)
		#控制进程发来了微信关注人数
		cComplexServer.RegDistribute(PyMessage.Control_UpdateWeiXinGuanZhuCnt, UpdateWeiXinGuanZhuCnt)
		
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WeiXin_Reward", "请求领取微信关注奖励"), RequestWeiXinReward)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WeiboZone_Share", "请求微博空间分享"), RequestWeiboZoneShare)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("WeiboZone_Reward", "请求领取微博空间奖励"), RequestWeiboZoneReward)
	

	
	