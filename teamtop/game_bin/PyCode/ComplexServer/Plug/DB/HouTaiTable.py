#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 全局数据库表
#===============================================================================
# 构建工作环境
import os
import sys
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)

import Environment
from World import Define
from Util.MySQL import DynamicTable, DynamicColumn

def BuildTable():
	'''
	构建本模块定义的表
	'''
	# 连接MySQL，并且构建数据库
	DynamicTable.MySQL.InitWeb(Define.Web_HouTai_MySQL)
	DynamicTable.MySQL.UserTable("web_houtai_new_%s" % Environment.ReadConfig())
	for value in globals().itervalues():
		if not isinstance(value, DynamicTable.Table):
			continue
		value.Build()
	DynamicTable.MySQL.Final()

#===============================================================================
# 表定义(注意表名要全小写字母)
#===============================================================================
notice = DynamicTable.Table("notice")
notice.AddColumn(DynamicColumn.IntColumn("nid", "int", True, True, "ID"))
notice.AddColumn(DynamicColumn.ObjColumn("content", "公告内容"))
notice.AddColumn(DynamicColumn.ObjColumn("track", "发送结果"))
notice.AddColumn(DynamicColumn.ObjColumn("process", "服务器进程列表"))
notice.AddColumn(DynamicColumn.IntColumn("interval_time", "int", True, False, "Interval"))
notice.AddColumn(DynamicColumn.StringColumn("start_time", 60, "密码"))
notice.AddColumn(DynamicColumn.StringColumn("end_time", 60, "密码"))
notice.AddColumn(DynamicColumn.StringColumn("sender",60, "发送者"))
notice.AddKey(DynamicColumn.ToPRI("nid"))

user = DynamicTable.Table("user")
user.AddColumn(DynamicColumn.IntColumn("uid", "int", True, True, "ID"))
user.AddColumn(DynamicColumn.StringColumn("name", 60, "帐号"))
user.AddColumn(DynamicColumn.StringColumn("real_name", 60, "真实姓名"))
user.AddColumn(DynamicColumn.StringColumn("password", 60, "密码"))
user.AddColumn(DynamicColumn.StringColumn("ugroup",60, "用户组"))
user.AddKey(DynamicColumn.ToPRI("uid"))
user.AddKey(DynamicColumn.ToUNI("name"))

log = DynamicTable.Table("log_data")
log.AddColumn(DynamicColumn.IntColumn("lid", "int", True, True, "日志ID"))
log.AddColumn(DynamicColumn.StringColumn("url", 60, "url"))
log.AddColumn(DynamicColumn.StringColumn("time", 60, "time"))
log.AddColumn(DynamicColumn.StringColumn("user", 60, "user/ip"))
log.AddColumn(DynamicColumn.ObjColumn("get_data", "HTTP请求(GET)"))
log.AddColumn(DynamicColumn.ObjColumn("post_data", "HTTP请求(POST)"))
log.AddColumn(DynamicColumn.ObjColumn("response", "HTTP返回"))
log.AddKey(DynamicColumn.ToPRI("lid"))

warn = DynamicTable.Table("warn", 0)
warn.AddColumn(DynamicColumn.IntColumn("wid", "int", True, True, "警告ID"))
warn.AddColumn(DynamicColumn.IntColumn("zone_id", "int", True, False, "区ID"))
warn.AddColumn(DynamicColumn.StringColumn("tkey", 60, "特征码"))
warn.AddColumn(DynamicColumn.DateTimeColumn("recv_time", "时间"))
warn.AddColumn(DynamicColumn.ObjColumn("text", "警告内容"))
warn.AddColumn(DynamicColumn.IntColumn("is_read", "tinyint", True, False, "是否读取"))
warn.AddKey(DynamicColumn.ToPRI("wid"))
warn.AddKey(DynamicColumn.ToMUL("tkey"))
warn.AddKey(DynamicColumn.ToMUL("recv_time"))

task = DynamicTable.Table("task", 0)
task.AddColumn(DynamicColumn.IntColumn("tid", "int", True, True, "任务id"))
task.AddColumn(DynamicColumn.StringColumn("cls", 120, "任务类（逻辑）"))
task.AddColumn(DynamicColumn.StringColumn("name", 120, "任务名"))
task.AddColumn(DynamicColumn.StringColumn("instruction", 600, "任务说明"))
task.AddColumn(DynamicColumn.ObjColumn("argv", "任务参数"))
task.AddColumn(DynamicColumn.IntColumn("total", "smallint", True, False, "总共的区数"))
task.AddColumn(DynamicColumn.IntColumn("finish", "smallint", True, False, "完成的区数"))
task.AddKey(DynamicColumn.ToPRI("tid"))

ctask = DynamicTable.Table("ctask", 0)
ctask.AddColumn(DynamicColumn.IntColumn("lock_id", "int", True, True, "锁id"))
ctask.AddColumn(DynamicColumn.IntColumn("tid", "int", True, False, "任务id"))
ctask.AddColumn(DynamicColumn.IntColumn("ctid", "int", True, False, "子任务id"))
ctask.AddColumn(DynamicColumn.StringColumn("cname", 120, "子任务名"))
ctask.AddColumn(DynamicColumn.StringColumn("mutex", 60, "互斥关系"))
ctask.AddColumn(DynamicColumn.StringColumn("process", 60, "进程信息"))
ctask.AddColumn(DynamicColumn.StringColumn("work_state", 10000, "工作状态"))
ctask.AddColumn(DynamicColumn.DateTimeColumn("start_time", "开始时间"))
ctask.AddColumn(DynamicColumn.ObjColumn("result", "子任务结果"))
ctask.AddKey(DynamicColumn.ToPRI("lock_id"))
ctask.AddKey(DynamicColumn.ToMUL("tid"))
ctask.AddKey(DynamicColumn.ToMUL("mutex"))

role_gm = DynamicTable.Table("role_gm", 0)
role_gm.AddColumn(DynamicColumn.IntColumn("gid", "int", True, True, "指令id"))
role_gm.AddColumn(DynamicColumn.StringColumn("role_ids", comment = "使用对象角色id"))
role_gm.AddColumn(DynamicColumn.StringColumn("user", 60, "用户"))
role_gm.AddColumn(DynamicColumn.StringColumn("command", comment = "gm指令"))
role_gm.AddColumn(DynamicColumn.DateTimeColumn("exec_time", "执行时间"))
role_gm.AddKey(DynamicColumn.ToPRI("gid"))

if Environment.IsDevelop:
	#帐号
	version_tool = DynamicTable.Table("version_tool")
	version_tool.AddColumn(DynamicColumn.StringColumn("account", 60, "帐号"))
	version_tool.AddColumn(DynamicColumn.StringColumn("password", 120, "密码"))
	version_tool.AddColumn(DynamicColumn.IntColumn("actype", "int", True, False, "帐号类型"))
	version_tool.AddColumn(DynamicColumn.StringColumn("envs", 120, "操作环境"))
	version_tool.AddKey(DynamicColumn.ToPRI("account"))
	
	#日志
	version_tool_log = DynamicTable.Table("version_tool_log")
	version_tool_log.AddColumn(DynamicColumn.StringColumn("account", 60, "帐号"))
	version_tool_log.AddColumn(DynamicColumn.StringColumn("env", 60, "操作环境"))
	version_tool_log.AddColumn(DynamicColumn.StringColumn("content", 10000, "操作记录"))
	version_tool_log.AddColumn(DynamicColumn.IntColumn("logid", "int", True, True, "日志ID"))
	version_tool_log.AddColumn(DynamicColumn.DateTimeColumn("log_time", "操作时间"))
	version_tool_log.AddKey(DynamicColumn.ToUNI("logid"))
	version_tool_log.AddKey(DynamicColumn.ToMUL("account"))
	version_tool_log.AddKey(DynamicColumn.ToMUL("env"))
if __name__ == "__main__":
	BuildTable()
