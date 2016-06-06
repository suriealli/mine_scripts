#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QOpen")
#===============================================================================
# QQ开通、续费黄钻
#===============================================================================
import cRoleMgr
import Environment
from Common.Message import AutoMessage
from ComplexServer.API import QQHttp
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.DB import DBHelp
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumInt32, EnumInt8, EnumDayInt8,\
	EnumInt16, EnumObj,EnumInt1

#===============================================================================
# token的类型。
# 1：表示该token为每日礼包赠送、开通包月送礼包营销活动中的赠送道具/物品的token。
# 2：表示该token为任务买卖市场营销活动中的领取奖励的token。
#===============================================================================
TOKEN_TYPE = 1


#开通黄钻 1，3，6，12个月
HZKaiTongActId_1 = "UM141016223358707"
HZKaiTongActId_3 = "UM15091514225461"
HZKaiTongActId_6 = "UM150915142409650"
HZKaiTongActId_12 = "UM150915142618703"

#开通蓝钻1，3，6，12个月
LanZuankaiTong_1 = "UM141021150442966"
LanZuankaiTong_3 = "UM150915150027903"
LanZuankaiTong_6 = "UM150915150230194"
LanZuankaiTong_12 = "UM150915150335843"

#开通豪华蓝钻
HaoHuaLanZuanKaiTong = "UM14121014262228"
HaoHuaLanZuanKaiTong_3 = "UM150922110616296"
#客户端活动ID索引
ActIdDict = {1 : HZKaiTongActId_1,
			3 : LanZuankaiTong_1,
			5 : HaoHuaLanZuanKaiTong,
			6 : LanZuankaiTong_3,
			7 : LanZuankaiTong_12
			}

#===============================================================================
#每次开启黄钻、蓝钻、豪华蓝钻新的活动，请修改下面的版本号，如开启时间为(2015,8,27,0,0,0)，则版本号为20150827
################################
HuangZuanVersion = 20150825		#黄钻开通版本号，

################################
LanZuanVersion = 20160304		#蓝钻开通版本号	#1.蓝钻专属转大礼 

################################
HaoHuaLanZuanVersion = 20150825	#豪华蓝钻开通版本号
#===============================================================================

#如果一次更新内有2个黄钻开通活动,需要在第二次黄钻活动开启时全服更新HuangZuanVersion + 1 并且执行下面函数
def UpdataHuangZuanVersion():
	#更新所有在线角色的次数
	for role in cRoleMgr.GetAllRole():
		UpdataRoleHuangZuanTimes(role)

#同样，如果一次更新内有2个蓝钻开通活动,需要在第二次蓝钻活动开启时全服更新 LanZuanVersion + 1 并且执行下面函数
def UpdataLanZuanVersion():
	#更新所有在线角色的次数
	for role in cRoleMgr.GetAllRole():
		UpdataRoleLanZuanTimes(role)

#同样，如果一次更新内有2个豪华蓝钻开通活动,需要在第二次豪华蓝钻活动开启时全服更新 HaoHuaLanZuanVersion + 1 并且执行下面函数
def UpdataHaoHuaLanZuanVersion():
	#更新所有在线角色的次数
	for role in cRoleMgr.GetAllRole():
		UpdataRoleHaoHuaLanZuanTimes(role)
#===============================================================================

if "_HasLoad" not in dir():
	Tra_QOpen_HuangZuanKaiTong = AutoLog.AutoTransaction("Tra_QOpen_HuangZuanKaiTong", "开通黄钻")
	Tra_QOpen_LanZuanKaiTong = AutoLog.AutoTransaction("Tra_QOpen_LanZuanKaiTong", "开通蓝钻")
	Tra_QOpen_HaoHuaLanZuanKaiTong = AutoLog.AutoTransaction("Tra_QOpen_HaoHuaLanZuanKaiTong", "开通豪华蓝钻")
	
	
	Tra_QOpen_LanZuanKaiTong_3M = AutoLog.AutoTransaction("Tra_QOpen_LanZuanKaiTong_3M", "开通蓝钻3个月")
	Tra_QOpen_LanZuanKaiTong_12M = AutoLog.AutoTransaction("Tra_QOpen_LanZuanKaiTong_12M", "开通蓝钻12个月")
	
	Tra_QOpen_UpdateHuangZuanData = AutoLog.AutoTransaction("Tra_QOpen_UpdateHuangZuanData", "升级黄钻活动版本重置数据")
	Tra_QOpen_UpdateLanZuanData = AutoLog.AutoTransaction("Tra_QOpen_UpdateLanZuanData", "升级蓝钻活动版本重置数据")
	Tra_QOpen_UpdateHaoHuaLanZuanData = AutoLog.AutoTransaction("Tra_QOpen_UpdateHaoHuaLanZuanData", "升级豪华蓝钻活动版本重置数据")

MAX_TIMES = 120#每次活动最大开通次数
MAX_Tips = "本次活动最大开通/续费上限为120次，您已达到最大开通/续费次数。"

def RequestKaiTong(role, msg):
	if not Environment.EnvIsQQ():
		return
	backid, actType = msg
	discountid = ActIdDict.get(actType)
	if not discountid:
		return
	if actType == 1:
		#黄钻开通
		if role.GetI8(EnumInt8.QQHuangZuanKaiTongTimes) >= MAX_TIMES:
			role.Msg(2, 0, MAX_Tips)
			return
	elif actType == 3:
		#蓝钻开通
		if role.GetI8(EnumInt8.QQLanZuanKaiTongTimes) >= MAX_TIMES:
			role.Msg(2, 0, MAX_Tips)
			return
	elif actType == 5:
		#豪华蓝钻开通
		if role.GetI8(EnumInt8.QQHaoHuaLanZuanKaiTongTimes) >= MAX_TIMES:
			role.Msg(2, 0, MAX_Tips)
			return
	elif actType == 6:
		#蓝钻开通3个月
		if role.GetI8(EnumInt8.QQLanZuanKaiTongTimes) + 3 > MAX_TIMES:
			role.Msg(2, 0, MAX_Tips)
			return
	elif actType == 7:
		#蓝钻开通12个月
		if role.GetI8(EnumInt8.QQLanZuanKaiTongTimes) + 12 > MAX_TIMES:
			role.Msg(2, 0, MAX_Tips)
			return
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	openkey = login_info["openkey"]
	pf = login_info["pf"]
	pfkey = login_info["pfkey"]
	roleid = role.GetRoleID()
	
	QQHttp.get_token(openid, openkey, pf, pfkey, TOKEN_TYPE, discountid, roleid, OnGetToken, (role, backid, discountid))


def OnGetToken(response, regparam):
	code, body = response
	if code != 200:
		print "GE_EXC, get_token error code (%s) " % code
		return
	body = eval(body)
	if body["ret"] != 0:
		print "GE_EXC, get_token error ret (%s) " % body["ret"]
		return
	role, backid, discountid = regparam
	token = body["token"]
	mid = body["mid"]
	role.CallBackFunction(backid, (token, mid, discountid, DBHelp.GetDBIDByRoleID(role.GetRoleID())))

def OnKaiTongCommand(role, param):

	qqlz_old = role.GetI8(EnumInt8.QQLanZuanKaiTongTimes)

	if param == HZKaiTongActId_1:
		with Tra_QOpen_HuangZuanKaiTong:
			role.IncI8(EnumInt8.QQHuangZuanKaiTongTimes, 1)
	elif param == LanZuankaiTong_1:
		with Tra_QOpen_LanZuanKaiTong:
			role.IncI8(EnumInt8.QQLanZuanKaiTongTimes, 1)
	elif param == HaoHuaLanZuanKaiTong:
		with Tra_QOpen_HaoHuaLanZuanKaiTong:
			role.IncI8(EnumInt8.QQHaoHuaLanZuanKaiTongTimes, 1)
	elif param == LanZuankaiTong_3:
		with Tra_QOpen_LanZuanKaiTong:
			role.IncI8(EnumInt8.QQLanZuanKaiTongTimes, 3)
	elif param == LanZuankaiTong_12:
		with Tra_QOpen_LanZuanKaiTong_12M:
			role.IncI8(EnumInt8.QQLanZuanKaiTongTimes, 12)
	else:
		print "GE_EXC, unknown kai tong command(%s)" % param

	qqlz_new = role.GetI8(EnumInt8.QQLanZuanKaiTongTimes)

	Event.TriggerEvent(Event.Eve_QQLZTimesMayChanged, role, (qqlz_old,qqlz_new))

def Update(role, param = None):
	UpdataRoleHuangZuanTimes(role)
	UpdataRoleLanZuanTimes(role)
	UpdataRoleHaoHuaLanZuanTimes(role)

def UpdataRoleHuangZuanTimes(role):
	global HuangZuanVersion
	roleVersion = role.GetI32(EnumInt32.HuangZuanKaiTongVersion)
	if HuangZuanVersion == roleVersion:
		return
	if HuangZuanVersion < roleVersion:
		print "GE_EXC, UpdataRoleHuangZuanTimes HuangZuanVersion(%s) < roleVersion (%s)" % (HuangZuanVersion, roleVersion)
		return 
	
	with Tra_QOpen_UpdateHuangZuanData:
		role.SetI8(EnumInt8.QQHuangZuanKaiTongTimes, 0)
		role.SetI32(EnumInt32.HuangZuanKaiTongVersion, HuangZuanVersion)
		#黄钻转大礼
		role.SetI8(EnumInt8.QQHZGift_UsedNum_Roll, 0)
		#黄钻大献礼
		role.SetI8(EnumInt8.QQHZGift_UsedNum_Offer, 0)
		#黄钻兑好礼
		role.SetI8(EnumInt8.QQHZRoll_UsedTimes_Roll, 0)
		#黄钻水晶
		role.SetI16(EnumInt16.QQHZRollCrystal, 0)
		#黄钻转转乐
		role.SetI8(EnumInt8.QQHZHappyDraw_UsedTimes, 0)
		role.SetObj(EnumObj.QQHZHDData, set())
		role.SetI16(EnumInt16.QQHZHappyDCrystal, 0)##重置黄钻水晶数值

def UpdataRoleLanZuanTimes(role):
	global LanZuanVersion
	roleVersion = role.GetI32(EnumInt32.LanZuanKaiTongVersion)
	if LanZuanVersion == roleVersion:
		return
	if LanZuanVersion < roleVersion:
		print "GE_EXC, UpdataRoleLanZuanTimes roleId(%s),LanZuanVersion(%s) < roleVersion (%s)" % (role.GetRoleID(), LanZuanVersion, roleVersion)
		return 
	
	with Tra_QOpen_UpdateLanZuanData:
		role.SetI8(EnumInt8.QQLanZuanKaiTongTimes, 0)
		role.SetI32(EnumInt32.LanZuanKaiTongVersion, LanZuanVersion)
		#蓝钻转大礼
		role.SetI8(EnumInt8.QQLZKaiTong_UsedTimes_Roll, 0)
		#蓝钻大献礼
		role.SetI8(EnumInt8.QQLZGift_UsedNum_Offer, 0)
		role.SetDI8(EnumDayInt8.QQLZGift_OG_TodayTimes, 0)
		#蓝钻兑好礼
		role.SetI8(EnumInt8.QQLZRoll_UsedTimes_Roll, 0)
		#蓝钻转转乐
		role.SetI8(EnumInt8.QQLZHappyDraw_UsedTimes, 0)
		role.SetObj(EnumObj.QQLZHDData, set())
		role.SetI16(EnumInt16.QQLZHappyDCrystal, 0)##重置蓝钻水晶数值
		#蓝钻宝箱
		role.GetObj(EnumObj.QQLZBaoXiang)[1] = {}
		for i in range(1, 10):
			role.GetObj(EnumObj.QQLZBaoXiang)[1][i] = None
		role.GetObj(EnumObj.QQLZBaoXiang)[2] = [0]			
		role.SetI8(EnumInt8.QQLZBaoXiangTimes, 0)
		#蓝钻寻宝
		role.SetI8(EnumInt8.QQLZXunBao, 0)
		role.SetI8(EnumInt8.QQLZXunBaoStep, 0)
		#蓝钻回馈大礼
		role.SetI8(EnumInt8.QQLZFeedBackTimes,0)
		role.SetI8(EnumInt8.QQLZFeedBackRewardGroup,1)
		role.SetObj(EnumObj.QQLZFeedBackData,{})
		role.SetI1(EnumInt1.QQLzFeedBackFirstrecharge,False)
		
def UpdataRoleHaoHuaLanZuanTimes(role):
	global HaoHuaLanZuanVersion
	roleVersion = role.GetI32(EnumInt32.HaoHuaLanZuanKaiTongVersion)
	if HaoHuaLanZuanVersion == roleVersion:
		return
	if HaoHuaLanZuanVersion < roleVersion:
		print "GE_EXC, UpdataRoleHaoHuaLanZuanTimes roleId(%s),HaoHuaLanZuanVersion(%s) < roleVersion (%s)" % (role.GetRoleID(), HaoHuaLanZuanVersion, roleVersion)
		return
	
	with Tra_QOpen_UpdateHaoHuaLanZuanData:
		#重置豪华蓝钻开通次数
		role.SetI8(EnumInt8.QQHaoHuaLanZuanKaiTongTimes, 0)
		#更新豪华蓝钻活动版本号
		role.SetI32(EnumInt32.HaoHuaLanZuanKaiTongVersion, HaoHuaLanZuanVersion)
		#重置 蓝钻豪华六重礼 领取记录
		role.SetI8(EnumInt8.QQLZLuxuryGiftRewardRecord, 0)
		#重置豪华蓝钻转大礼已抽奖次数
		role.SetI8(EnumInt8.QQLZLuxury_UsedTimes_Roll, 0)
		#重置豪华蓝钻水晶数值
		role.SetI16(EnumInt16.QQLZLuxuryRollCrystal, 0)
def CheckVersion(param1, param2):
	'''
	@author: GaoShuai
	@param1: None
	@param2: (Qtype, startDateTime, name) Qtype in (0, 1, 2)
	'''
	Qtype, startTime, name = param2
	
	if Qtype not in (0, 1, 2):
		print "GE_EXC, the trigger of Event.QQCheckVersion message error , when you activate a new activity(%s)" % name
		return
	vision = startTime.year * 10000 + startTime.month * 100 + startTime.day
	QVision = [HuangZuanVersion, LanZuanVersion, HaoHuaLanZuanVersion]#[黄钻,蓝钻,豪华蓝钻]
	
	if QVision[Qtype] < vision:
		print "GE_EXC, update the version when you activate a new activity(%s), please" % name
		
if "_HasLoad" not in dir():
	if (Environment.EnvIsQQ() or Environment.IsDevelop) and Environment.HasLogic and (not Environment.IsCross):
		Event.RegEvent(Event.Eve_QQCheckVersion, CheckVersion)
		Event.RegEvent(Event.Eve_AfterLogin, Update)
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QQ_HuangZuan_RequestKaiTong", "客户端请求开通或者续费黄钻(1黄钻，3蓝钻， 5豪华蓝钻)"), RequestKaiTong)
