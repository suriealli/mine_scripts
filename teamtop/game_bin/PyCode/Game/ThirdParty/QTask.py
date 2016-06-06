#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QTask")
#===============================================================================
# QQ任务（交叉推广）
#===============================================================================
import Environment
from Common.Message import AutoMessage
from ComplexServer.API import QQHttp, GlobalHttp, Define
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumObj, EnumInt8

RET_OTHER_ROLE = 301
#步骤对应是否发离线命令发奖励
STEP_COMMAND = [None, True, True, True, True]

def SetTrue(total_step, now_step):
	return total_step | (1 << now_step)

def IsTrue(total_step, now_step):
	return total_step & (1 << now_step)

def IsTask(role, app_contract_id):
	return role.GetObj(EnumObj.QTaskID) == app_contract_id

def GetTask(role):
	task_id = role.GetObj(EnumObj.QTaskID)
	if task_id:
		return task_id
	else:
		return ""

def FinishTask(role, step):
	# 没任务，不能完成
	if not GetTask(role):
		return
	# 不要重复完成
	if IsTrue(role.GetI8(EnumInt8.QTaskFinish), step):
		return
	openid = role.GetTempObj(EnumTempObj.LoginInfo)["account"]
	roleid = role.GetRoleID()
	contractid = GetTask(role)
	GlobalHttp.FinishTask(openid, roleid, contractid, step, OnFinishTaskBack, (role, step))

#奖励
BaiYin = (26139, 1)
HuangJin = (26140, 1)
TuHao = (26141, 1)
#任务配置 key 有多种类型，字符串的为任务类型， value为任务内容，一般是步骤, key为数字时则内容都命令客户端打开那些面板, 1~4为步骤，其他大数字为等级
QTask_Dict = {}
QTask_Dict["100718848T320140515103141"] = {"init":1, "level":(28, 2), "invite":3, "reward":(None, BaiYin, HuangJin, TuHao, None)}
QTask_Dict["100718848T320140519100500"] = {"init":1, "level":(30, 3), "invite":2, "reward":(None, BaiYin, HuangJin, None, TuHao)}
QTask_Dict["100718848T320140519100724"] = {"init":1, "level":(33, 3), "invite":2, "reward":(None, BaiYin, HuangJin, None, TuHao)}
QTask_Dict["100718848T320140519100926"] = {"init":1, "level":(34, 3), "invite":2, "reward":(None, BaiYin, HuangJin, None, TuHao)}
QTask_Dict["100718848T320140519101120"] = {"init":1, "level":(35, 3), "invite":2, "reward":(None, BaiYin, HuangJin, None, TuHao)}
QTask_Dict["100718848T320140530102740"] = {"init":1, "level":(34, 3), "hero":2, "reward":(None, BaiYin, HuangJin, None, TuHao), 2:"OPEN_SHOUCHONG", 20:"OLTB", 30:"YXJT"}
QTask_Dict["100718848T320140530102358"] = {"init":1, "level":(34, 3), "level2":(20, 2), "reward":(None, BaiYin, HuangJin, None, TuHao), 15:"OPEN_SHOUCHONG", 20:"OLTB", 30:"YXJT"}
QTask_Dict["100718848T320140710152432"] = {"init":1, "share":2, "hero2":(14, 3), "reward":(None, BaiYin, HuangJin, None, TuHao), 1:"OPEN_INVITE_PANEL", 2:"OPEN_RECRUIT_PANEL"}
QTask_Dict["100718848T320140728193240"] = {"init":1, "invite":2, "level":(34, 3), "reward":(None, BaiYin, HuangJin, None, TuHao), 1:"OPEN_INVITE_PANEL"}
QTask_Dict["100718848T320150924164321"] = {"init":1, "invite":2, "level":(34, 3), "reward":(None, BaiYin, HuangJin, None, TuHao), 1:"OPEN_INVITE_PANEL"}


#===============================================================================
#上模拟服测试的是需要去 web_global_new_qq 中删除这个帐号下面对应的任务ID的数据，因为一个任务绑定的
#是帐号，而不是角色，所以删除角色并不会清理之前的数据,但是这个删除的操作需要谨慎处理
#===============================================================================


def OnFinishTaskBack(response, regparam):
	role, step = regparam
	code, body = response
	if code != 200:
		#print "GE_EXC, role(%s) finish step(%s) error." % (role.GetRoleID(), step)
		return
	if body == Define.Error:
		#print "GE_EXC, role(%s) finish step(%s) error." % (role.GetRoleID(), step)
		return
	body = eval(body)
	if body["ret"] != 0:
		if body["ret"] == RET_OTHER_ROLE:
			role.Msg(4, 0, body["msg"])
		else:
			pass
			#print "GE_EXC, role(%s) finish step(%s) error." % (role.GetRoleID(), step)
		return
	# 标记任务完成
	role.SetI8(EnumInt8.QTaskFinish, SetTrue(role.GetI8(EnumInt8.QTaskFinish), step))
	cfg = QTask_Dict.get(GetTask(role))
	if cfg is None:
		print "GE_EXC, role(%s) can't find config OnFinishTaskBack" % (role.GetRoleID())
		return
	# 命令客户端弹出面板
	client_command = cfg.get(step)
	if client_command is None:
		return
	role.ClientCommand(client_command)

def OnQQReward(role, step):
	if step >= len(STEP_COMMAND):
		print "GE_EXC, role(%s) qq task reward error step(%s)" % (role.GetRoleID(), step)
		return
	# 读取配置
	
	cfg = QTask_Dict.get(GetTask(role))
	if cfg is None:
		print "GE_EXC, role(%s) can't find config OnQQReward" % (role.GetRoleID())
		return
	# 只能领取一次奖励
	if IsTrue(role.GetI8(EnumInt8.QTaskReward), step):
		return
	role.SetI8(EnumInt8.QTaskReward, SetTrue(role.GetI8(EnumInt8.QTaskReward), step))
	# 按照步骤发放奖励
	item = cfg["reward"][step]
	if not item:
		return
	role.AddItem(*item)

def AfterLogin(role):
	# 没任务
	if not GetTask(role):
		return
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	openkey = login_info["openkey"]
	pf = login_info["pf"]
	QQHttp.check_task_status(openid, openkey, pf, OnCheckTaskStatusBack, role)

def OnCheckTaskStatusBack(response, regparam):
	code, body = response
	if code != 200:
		return
	body = eval(body)
	if body["ret"] != 0:
		return
	if not body["task_user"]:
		return
	role = regparam
	if role.IsKick():
		return
	task_expiring = body["task_expiring"]
	app_contract_id = body["app_contract_id"]
	role.SendObj(QQTask_Notify, (task_expiring, app_contract_id))

def AfterInit(role, param):
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	if "app_user_source" not in login_info:
		return
	app_contract_id = login_info.get("app_contract_id")
	if not app_contract_id:
		return
	# 标记任务id
	role.SetObj(EnumObj.QTaskID, app_contract_id)
	# 读取配置
	cfg = QTask_Dict.get(GetTask(role))
	if cfg is None:
		return
	# 完成进入游戏任务
	FinishTask(role, cfg["init"])

def AfterLevelUp(role, param):
	# 读取配置
	cfg = QTask_Dict.get(GetTask(role))
	if cfg is None:
		return
	
	# 命令客户端弹出等级对应的面板
	client_command = cfg.get(role.GetLevel())
	if client_command:
		role.ClientCommand(client_command)
	
	stepdata = cfg.get("level")
	if not stepdata:
		return
	
	if role.GetLevel() < stepdata[0]:
		return
	
	FinishTask(role, stepdata[1])

def AfterLevelUp2(role, param):
	# 读取配置
	cfg = QTask_Dict.get(GetTask(role))
	if cfg is None:
		return
	param = cfg.get("level2")
	if not param:
		return
	if role.GetLevel() < param[0]:
		return
	FinishTask(role, param[1])

def AfterInvite(role, param):
	# 读取配置
	cfg = QTask_Dict.get(GetTask(role))
	if cfg is None:
		return
	step = cfg.get("invite")
	if not step:
		return
	FinishTask(role, step)

def NewHero(role, param):
	# 读取配置
	cfg = QTask_Dict.get(GetTask(role))
	if cfg is None:
		return
	step = cfg.get("hero")
	if step:
		#单纯的获得一个新英雄
		FinishTask(role, step)
		
	stepdata = cfg.get("hero2")
	if stepdata:
		#获得一个指定的新英雄
		if param == stepdata[0]:
			FinishTask(role, stepdata[1])

def AfterShareQQ(role, param):
	#分享
	cfg = QTask_Dict.get(GetTask(role))
	if cfg is None:
		return
	step = cfg.get("share")
	if not step:
		return
	FinishTask(role, step)

if "_HasLoad" not in dir():
	assert len(STEP_COMMAND) < 7
	QQTask_Notify = AutoMessage.AllotMessage("QQTask_Notify", "通知客户端有交叉推广任务")
	if Environment.EnvIsQQ() and not Environment.IsCross:
		Event.RegEvent(Event.Eve_FirstInitRole, AfterInit)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp)
		Event.RegEvent(Event.Eve_AfterLevelUp, AfterLevelUp2)
		Event.RegEvent(Event.Eve_AfterInviteQQFriend, AfterInvite)
		Event.RegEvent(Event.Eve_AfterShareQQ, AfterShareQQ)
		Event.RegEvent(Event.Eve_NewHero, NewHero)
