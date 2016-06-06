#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 交叉推广V3
#===============================================================================
import json
from Integration import AutoHTML
from Integration.Help import OtherHelp
from ComplexServer.Plug.DB import DBHelp
from Game.ThirdParty import QTask
from Integration.WebPage.User import Permission

def GetRoleNameByRoleID(roleid):
	con = DBHelp.ConnectMasterDBRoleID(roleid)
	with con as cur:
		cur.execute("select role_name from role_data where role_id = %s;" % roleid)
		result = cur.fetchall()
		cur.close()
		if result:
			return result[0][0]
		else:
			return "？"

def GetZoneNameByRoleID(cur, roleid):
	cur.execute("select name from zone where zid = %s;" % DBHelp.GetDBIDByRoleID(roleid))
	result = cur.fetchall()
	if result:
		return result[0][0]
	else:
		return "？"

def FinishTask(request):
	return OtherHelp.Apply(__FinishTask, request, __name__)

def __FinishTask(request):
	openid = AutoHTML.AsString(request.GET, "openid")
	roleid = AutoHTML.AsInt(request.GET, "roleid")
	contractid = AutoHTML.AsString(request.GET, "contractid")
	step = AutoHTML.AsInt(request.GET, "step")
	
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select role_id, finish_step from qq_task where account = %s and contractid = %s for update;", (openid, contractid))
		result = cur.fetchall()
		# 已经有任务记录
		if result:
			old_role_id, finish_step = result[0]
			# 在其他服领取了任务
			if roleid != old_role_id:
				role_name = GetRoleNameByRoleID(old_role_id)
				zone_name = GetZoneNameByRoleID(cur, old_role_id)
				# 直接返回错误
				return json.dumps({"ret":QTask.RET_OTHER_ROLE, "msg":"亲爱的玩家，您在%s的%s已经领取了任务" % (zone_name, role_name)}, ensure_ascii = False)
			# 更新任务
			else:
				finish_step = QTask.SetTrue(finish_step, step)
				cur.execute("update qq_task set finish_step = %s where account = %s and contractid = %s;", (finish_step, openid, contractid))
		# 第一次任务记录
		else:
			# 强制将第一步（进入）游戏完成
			finish_step = QTask.SetTrue(0, 1)
			finish_step = QTask.SetTrue(finish_step, step)
			cur.execute("insert into qq_task (account, role_id, contractid, finish_step) values(%s, %s, %s, %s);", (openid, roleid, contractid, finish_step))
	# 返回正确
	return json.dumps({"ret":0, "msg":"OK"})



#检查方法
#登录版本机，尝试直接访问接口是否成功
#python
#>>> import urllib2
#>>>urllib2.urlopen('http://10.207.150.240:9001/Interface/QQTask/DeliverTask/?appid=100718848&billno=&cmd=check&contractid=100718848T320150924164321&openid=D9FD8DE3E76A7C92B991EF6C2909ABE9&payitem=&pf=qzone&providetype=2&sig=CgXRHeiHa4lkoEYohOJGoId2jK0%3D&step=2&ts=1448393606&version=V3').read()

#登录CRT 连接数据库 
#mysql -h1.4.14.176 -P1026 -uroot -p3edc4rfv
#选择 use web_global_new_qq;
#按照帐号ID和活动ID查询信息
#select role_id, finish_step, reward_step from qq_task where account = '3887E314CB330CAF1FB33FB905BDB723' and contractid = "100718848T320150924164321";

#登录版本机
#连接全局HTTP机器 ssh lq_global1
#进入 nginx logs目录  /data/soft/ngin/logs 
#检查 tail -f n_GS_Web.log
#检查 vim error.log



def DeliverTask(request):
	#腾讯访问我方的接口，具体接口地址和url信息是运营广告任务集市填写的
	return OtherHelp.Apply(__DeliverTask, request, __name__)


def __DeliverTask(request):
	cmd = AutoHTML.AsString(request.GET, "cmd")
	openid = AutoHTML.AsString(request.GET, "openid")
	#appid = AutoHTML.AsString(request.GET,"appid")
	#pf = AutoHTML.AsString(request.GET,"pf")
	#ts = AutoHTML.AsString(request.GET,"ts")
	#version = AutoHTML.AsString(request.GET, "version")
	contractid = AutoHTML.AsString(request.GET, "contractid")
	step = AutoHTML.AsInt(request.GET, "step")
	#payitem = AutoHTML.AsString(request.GET,"payitem")
	billno = AutoHTML.AsString(request.GET,"billno")
	#providetype = AutoHTML.AsString(request.GET,"providetype")
	#sig = AutoHTML.AsString(request.GET,"sig")
	
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		# 查找任务情况
		cur.execute("select role_id, finish_step, reward_step from qq_task where account = %s and contractid = %s for update;", (openid, contractid))
		result = cur.fetchall()
		# 没任务信息
		if not result:
			return json.dumps({"ret":1, "msg":"no task info.", "zoneid":0})
		role_id, finish_step, reward_step = result[0]
		zone_id = DBHelp.GetDBIDByRoleID(role_id)
		# 没有步骤
		if step >= len(QTask.STEP_COMMAND):
			return json.dumps({"ret":103, "msg": "no step %s" % step, "zoneid": zone_id})
		# 检测任务
		if cmd == "check":
			# 没完成
			if not QTask.IsTrue(finish_step, step):
				return json.dumps({"ret":2, "msg":"not finist step %s" % step, "zoneid": zone_id})
			return json.dumps({"ret":0, "msg":"OK", "zoneid": zone_id})
		# 发奖
		elif cmd == "award":
			# 已经发奖
			if QTask.IsTrue(reward_step, step):
				return json.dumps({"ret":3, "msg":"has reward step %s" % step, "zoneid": zone_id})
			# 记录
			reward_step = QTask.SetTrue(reward_step, step)
			h = cur.execute("update qq_task set reward_step = %s, log = CONCAT(log, '%s.%s|') where account = '%s' and contractid = '%s';" % (reward_step, billno, step, openid, contractid))
			if not h:
				return json.dumps({"ret":102, "msg":"fail reward step %s" % step, "zoneid": zone_id})
			# 发奖
			command = QTask.STEP_COMMAND[step]
			if command:
				assert DBHelp.SendRoleCommend(role_id, '''("Game.ThirdParty.QTask", "OnQQReward", %s)''' % step)
			return json.dumps({"ret":0, "msg": "OK", "zoneid": zone_id})
		elif cmd == "check_award":
			if not QTask.IsTrue(finish_step, step):
				return json.dumps({"ret":2, "msg":"not finist step %s" % step, "zoneid": zone_id})
			# 已经发奖
			if QTask.IsTrue(reward_step, step):
				return json.dumps({"ret":3, "msg":"has reward step %s" % step, "zoneid": zone_id})
			# 记录
			reward_step = QTask.SetTrue(reward_step, step)
			h = cur.execute("update qq_task set reward_step = %s, log = CONCAT(log, '%s.%s|') where account = '%s' and contractid = '%s';" % (reward_step, billno, step, openid, contractid))
			if not h:
				return json.dumps({"ret":102, "msg":"fail reward step %s" % step, "zoneid": zone_id})
			# 发奖
			command = QTask.STEP_COMMAND[step]
			if command:
				assert DBHelp.SendRoleCommend(role_id, '''("Game.ThirdParty.QTask", "OnQQReward", %s)''' % step)
			return json.dumps({"ret":0, "msg": "OK", "zoneid": zone_id})
		else:
			raise Exception("unknown cmd %s" % cmd)

Permission.reg_public(FinishTask)
Permission.reg_public(DeliverTask)

