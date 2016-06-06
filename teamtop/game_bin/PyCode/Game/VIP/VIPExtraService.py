#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.VIP.VIPExtraService")
#===============================================================================
# VIP尊享服务
#===============================================================================
import Environment
import cRoleMgr
import cProcess
from World import Define
from Common.Message import AutoMessage
from Common.Other import EnumGameConfig
from ComplexServer.Log import AutoLog
from ComplexServer.API import GlobalHttp
from Game.Role.Data import EnumInt1
from Game.Role import Call


VIPRoleSet = set()

if "_HasLoad" not in dir():
	#日志
	TraCommitInfoReward = AutoLog.AutoTransaction('TraCommitInfoReward', '填写玩家个人真实信息奖励 ')

#提交个人信息请求
def RequestCommitPersonalInfo(role, info):
	if Environment.IsDevelop or cProcess.ProcessID in Define.TestWorldIDs:
		#开发环境和测试环境不能填写(请不要修改，这个不用翻译的)
		role.Msg(2, 0, "模拟服和内网不能填写这个信息，必须是正式服")
		return
	
	global VIPRoleSet
	if role.GetRoleID() in VIPRoleSet:
		return
	
	# 之前已经填写 无视奖励部分
	if role.GetI1(EnumInt1.PersonalInfoCommitStatus):
		return 
	
	if role.GetConsumeQPoint() < EnumGameConfig.VIP_ExtraServiceNeedQPoint:
		return
	
	#数据约束检测失败 无视
	name, gender, phoneNum, qqNum, idCard, address = info
	
	# 必填项 检测
	if not gender or not phoneNum or not qqNum:
		return
	
	# 性别检测
	if gender != '0' and gender != '1':
		return
	
	# 名字长度限制
	if name and len(name) > EnumGameConfig.VIP_ExtraInfoMaxLenOfName:
		return
	
	# 身份证长度限制
	if idCard and len(idCard) > EnumGameConfig.VIP_ExtraInfoMaxLenOfIdCard:
		return
	
	# 地址长度限制
	if address and len(address) > EnumGameConfig.VIP_ExtraInfoMaxLenOfAdress:
		return
	
	# 手机号 和 QQ号 纯数字检测
	if not phoneNum.isdigit() or not qqNum.isdigit():
		return	
	
	# 手机号长度限制
	phoneLen = len(phoneNum)
	if phoneLen < EnumGameConfig.VIP_ExtraInfoLenOfPhoneNum[0] or phoneLen > EnumGameConfig.VIP_ExtraInfoLenOfPhoneNum[1]:
		return
	
	# 手机号长度限制
	qqLen = len(qqNum)
	if qqLen < EnumGameConfig.VIP_ExtraInfoLenOfQQNum[0] or qqLen > EnumGameConfig.VIP_ExtraInfoLenOfQQNum[1]:
		return	
	
	#先访问HTTP，填写成功后才发离线命令发奖
	getdict = {}	
	getdict["server"] 	= role.GetPid()
	getdict["role_id"] 	= role.GetRoleID()			#role_id	uint64
	getdict["name"] 	= name						#name		string 
	getdict["sex"] 		= gender					#sex		string  0女1男
	getdict["phone"] 	= phoneNum					#phone		string
	getdict["qq"] 		= qqNum						#qq			string
	getdict["id_card"] 	= idCard					#id_card	string
	getdict["address"] 	= address					#address	string
	getdict["zipcode"] 	= '0'						#zipcode	string
	
	
	#只能正式服才可以访问
	GlobalHttp.SetVIPInfo(getdict, HttpBack, role.GetRoleID())
	
	VIPRoleSet.add(role.GetRoleID())
	
tpis_1 = "系统繁忙，请稍后再试"
tpis_2 = "你填写的信息有误，请修改后重新提交"
def HttpBack(response, regparam):
	code, body = response
	roleId = regparam
	role = cRoleMgr.FindRoleByRoleID(roleId)
	global VIPRoleSet
	VIPRoleSet.discard(roleId)
	if code != 200:
		if role:
			role.Msg(2, 0, tpis_1)
		print "GE_EXC SetVIPinfo error httpback ", response
		return
	if body == str(roleId):
		Call.LocalDBCall(roleId, SetVIPInfoSucceed, None)
	else:
		print "GE_EXC SetVIPinfo error httpback ", response
		if role:
			role.Msg(2, 0, tpis_2)

def SetVIPInfoSucceed(role, param):
	# 设置 奖励
	if role.GetI1(EnumInt1.PersonalInfoCommitStatus):
		#预防发送多条
		return
	with TraCommitInfoReward:
		role.SetI1(EnumInt1.PersonalInfoCommitStatus, 1)
		role.AddItem(EnumGameConfig.VIP_PersonalInfoCommitReward, 1)

if "_HasLoad" not in dir():		
	if Environment.HasLogic and not Environment.IsCross:
		#填写info请求
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("RequestCommitRolePersonalinfo", "提交玩家真实个人信息 "), RequestCommitPersonalInfo)	
	