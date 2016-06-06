#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# Web表（全局数据表）
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
from ComplexServer.Plug.DB import Column
from Util.MySQL import DynamicTable, DynamicColumn

def BuildTable():
	'''
	构建本模块定义的表
	'''
	# 连接MySQL，并且构建数据库
	DynamicTable.MySQL.InitWeb(Define.Web_Global_MySQL)
	DynamicTable.MySQL.UserTable("web_global_new_%s" % Environment.ReadConfig())
	for value in globals().itervalues():
		if not isinstance(value, DynamicTable.Table):
			continue
		value.Build()
	# 动态的构建CDKEY的表
	from Game.CDKey import CDKey
	for special in CDKey.CKC.iterkeys():
		ckey = DynamicTable.Table("cdkey_%s" % special)
		ckey.AddColumn(DynamicColumn.StringColumn("cdkey", 60, "cd-key"))
		ckey.AddColumn(DynamicColumn.IntColumn("role_id", "bigint", True, False, "角色ID"))
		ckey.AddColumn(DynamicColumn.DateTimeColumn("activaty_datetime", "激活时间"))
		ckey.AddKey(DynamicColumn.ToUNI("cdkey"))
		ckey.Build()
	# 动态的构建语言包的表
#	for language in Define.Language:
#		if language == "default":
#			continue
#		config = DynamicTable.Table("language_config_%s" % language)
#		config.AddColumn(DynamicColumn.StringColumn("source_text", 100, "原文"))
#		config.AddColumn(DynamicColumn.StringColumn("target_text", 1000, "译文"))
#		config.AddColumn(DynamicColumn.StringColumn("module_name", 120, "模块名"))
#		config.AddColumn(DynamicColumn.StringColumn("class_name", 120, "类名"))
#		config.AddKey(DynamicColumn.ToPRI("source_text"))
#		script = DynamicTable.Table("language_script_%s" % language)
#		script.AddColumn(DynamicColumn.StringColumn("module_variable_name", 120, "模块变量名"))
#		script.AddColumn(DynamicColumn.TextColumn("source_text", "原文"))
#		script.AddColumn(DynamicColumn.TextColumn("target_text", "译文"))
#		script.AddColumn(DynamicColumn.IntColumn("need_translate", "tinyint", True, False, "是否需要翻译"))
#		config.Build()
#		script.Build()
	DynamicTable.MySQL.Final()

#===============================================================================
# 表定义(注意表名要全小写字母)
#===============================================================================
computer = DynamicTable.Table("computer")
computer.AddColumn(DynamicColumn.StringColumn("name", 60, "机器名"))
computer.AddColumn(DynamicColumn.StringColumn("ip", 60, "网卡IP"))
computer.AddColumn(DynamicColumn.StringColumn("public_ip", 60, "对外IP"))
computer.AddColumn(DynamicColumn.ObjColumn("tgw_bind", "腾讯域名绑定 port->set()"))
computer.AddKey(DynamicColumn.ToPRI("name"))
computer.AddKey(DynamicColumn.ToUNI("ip"))

mysql = DynamicTable.Table("mysql")
mysql.AddColumn(DynamicColumn.StringColumn("name", 60, "MySQL名"))
mysql.AddColumn(DynamicColumn.StringColumn("master_ip", 600, "主库ip"))
mysql.AddColumn(DynamicColumn.IntColumn("master_port", "smallint", True, False, "主库端口"))
mysql.AddColumn(DynamicColumn.StringColumn("master_user", 60, "主库用户名"))
mysql.AddColumn(DynamicColumn.StringColumn("master_pwd", 60, "主库密码"))
mysql.AddColumn(DynamicColumn.StringColumn("slave_ip", 600, "从库ip"))
mysql.AddColumn(DynamicColumn.IntColumn("slave_port", "smallint", True, False, "从库端口"))
mysql.AddColumn(DynamicColumn.StringColumn("slave_user", 60, "从库用户名"))
mysql.AddColumn(DynamicColumn.StringColumn("slave_pwd", 60, "从库密码"))
mysql.AddKey(DynamicColumn.ToPRI("name"))

zone = DynamicTable.Table("zone")
zone.AddColumn(DynamicColumn.IntColumn("zid", "smallint", True, False, "区ID"))
zone.AddColumn(DynamicColumn.StringColumn("name", 60, "区名"))
zone.AddColumn(DynamicColumn.StringColumn("ztype", 60, "区类型"))
zone.AddColumn(DynamicColumn.StringColumn("all_process_key", 60, "单进程KEY"))
zone.AddColumn(DynamicColumn.StringColumn("c_process_key", 60, "控制进程KEY"))
zone.AddColumn(DynamicColumn.StringColumn("d_process_key", 60, "数据库进程KEY"))
zone.AddColumn(DynamicColumn.StringColumn("ghl_process_key", 60, "逻辑进程KEY"))
zone.AddColumn(DynamicColumn.StringColumn("mysql_name", 60, "连接的MySQL名"))
zone.AddColumn(DynamicColumn.StringColumn("public_ip", 100, "客户端连接IP"))
zone.AddColumn(DynamicColumn.StringColumn("language", 60, "语言包"))
zone.AddColumn(DynamicColumn.IntColumn("be_merge_zid", "smallint", True, False, "被合并的区ID"))
zone.AddColumn(DynamicColumn.IntColumn("be_merge_cnt", "smallint", True, False, "被合区次数"))
zone.AddColumn(DynamicColumn.StringColumn("merge_zids", 600, "合并的其他区ID"))
zone.AddKey(DynamicColumn.ToPRI("zid"))
zone.AddKey(DynamicColumn.ToUNI("name"))

process = DynamicTable.Table("process")
process.AddColumn(DynamicColumn.StringColumn("pkey", 60, "进程唯一KEY"))
process.AddColumn(DynamicColumn.StringColumn("ptype", 60, "进程类型"))
process.AddColumn(DynamicColumn.IntColumn("pid", "smallint", True, False, "进程ID"))
process.AddColumn(DynamicColumn.StringColumn("computer_name", 60, "所在机器名"))
process.AddColumn(DynamicColumn.IntColumn("port", "smallint", True, False, "监听端口"))
process.AddColumn(DynamicColumn.IntColumn("bind_zid", "smallint", True, False, "绑定的区ID"))
process.AddColumn(DynamicColumn.IntColumn("work_zid", "smallint", True, False, "工作的区ID"))
process.AddKey(DynamicColumn.ToPRI("pkey"))

computer_tmp = DynamicTable.Table("computer_tmp")
for column in computer.columns.itervalues():
	computer_tmp.AddColumn(column)
for key in computer.keys.itervalues():
	computer_tmp.AddKey(key)

mysql_tmp = DynamicTable.Table("mysql_tmp")
for column in mysql.columns.itervalues():
	mysql_tmp.AddColumn(column)
for key in mysql.keys.itervalues():
	mysql_tmp.AddKey(key)

zone_tmp = DynamicTable.Table("zone_tmp")
for column in zone.columns.itervalues():
	zone_tmp.AddColumn(column)
for key in zone.keys.itervalues():
	zone_tmp.AddKey(key)

process_tmp = DynamicTable.Table("process_tmp")
for column in process.columns.itervalues():
	process_tmp.AddColumn(column)
for key in process.keys.itervalues():
	process_tmp.AddKey(key)

inner_account = DynamicTable.Table("inner_account")
inner_account.AddColumn(Column.account)
inner_account.AddColumn(DynamicColumn.StringColumn("info", 120, "帐号信息"))
inner_account.AddKey(DynamicColumn.ToPRI(Column.account))

role_back = DynamicTable.Table("role_back")
role_back.AddColumn(DynamicColumn.StringColumn("bid", 60, "备份ID"))
role_back.AddColumn(Column.role_id)
role_back.AddColumn(DynamicColumn.DateTimeColumn("back_time", "备份时间"))
role_back.AddColumn(DynamicColumn.ObjColumn("role_data", "角色数据"))
role_back.AddColumn(DynamicColumn.ObjColumn("role_objs", "角色对象"))
role_back.AddKey(DynamicColumn.ToPRI("bid"))
role_back.AddKey(DynamicColumn.ToMUL(Column.role_id))
role_back.AddKey(DynamicColumn.ToMUL("back_time"))

qq_open = DynamicTable.Table("qq_open")
qq_open.AddColumn(Column.account)
qq_open.AddColumn(DynamicColumn.StringColumn("token", 40, ""))
qq_open.AddColumn(DynamicColumn.StringColumn("billno", 60, "billno"))
qq_open.AddKey(DynamicColumn.ToMUL(Column.account))
qq_open.AddKey(DynamicColumn.ToUNI("billno"))

qq_task = DynamicTable.Table("qq_task")
qq_task.AddColumn(Column.account)
qq_task.AddColumn(Column.role_id)
qq_task.AddColumn(DynamicColumn.StringColumn("contractid", 60, "任务ID"))
qq_task.AddColumn(DynamicColumn.IntColumn("finish_step", "int", True, False, "完成步骤"))
qq_task.AddColumn(DynamicColumn.IntColumn("reward_step", "int", True, False, "领奖步骤"))
qq_task.AddColumn(DynamicColumn.StringColumn("log", 1000, "日志"))
qq_task.AddKey(DynamicColumn.ToMUL(Column.role_id))
qq_task.AddKey(DynamicColumn.ToMUL(Column.account))
qq_task.AddKey(DynamicColumn.ToMUL("contractid"))

#全局持久化数据
global_data = DynamicTable.Table("global_data")
global_data.AddColumn(DynamicColumn.StringColumn("global_data_key", 60, "全局数据唯一Key"))
global_data.AddColumn(DynamicColumn.ObjColumn("data", "数据"))
global_data.AddColumn(DynamicColumn.DateTimeColumn("save_datetime", "保存时间"))
global_data.AddKey(DynamicColumn.ToPRI("global_data_key"))


#全服消费排行榜
qq_consume_rank = DynamicTable.Table("qq_consume_rank")
qq_consume_rank.AddColumn(DynamicColumn.IntColumn("rank_dayid", "int", True, False, "保存日期ID"))
qq_consume_rank.AddColumn(DynamicColumn.ObjColumn("data", "数据"))
qq_consume_rank.AddColumn(DynamicColumn.DateTimeColumn("save_datetime", "保存时间"))
qq_consume_rank.AddKey(DynamicColumn.ToPRI("rank_dayid"))



gm_role = DynamicTable.Table("gm_role")
gm_role.AddColumn(Column.role_id)
gm_role.AddColumn(Column.account)
gm_role.AddColumn(Column.role_name)
gm_role.AddColumn(DynamicColumn.IntColumn("pid", "int", True, False, "进程ID"))
gm_role.AddColumn(DynamicColumn.IntColumn("rmb", "int", True, False, "发放神石数量"))
gm_role.AddColumn(DynamicColumn.IntColumn("level", "int", True, False, "角色等级"))
gm_role.AddColumn(DynamicColumn.IntColumn("viplevel", "int", True, False, "vip等级"))
gm_role.AddColumn(DynamicColumn.IntColumn("qp", "int", True, False, "Q点"))
gm_role.AddColumn(DynamicColumn.DateTimeColumn("save_datetime", "保存时间"))
gm_role.AddKey(DynamicColumn.ToPRI(Column.role_id))


back_role = DynamicTable.Table("back_role")
back_role.AddColumn(Column.account)
back_role.AddColumn(DynamicColumn.IntColumn("viplevel", "int", True, False, "回流的最大vip等级"))
back_role.AddKey(DynamicColumn.ToPRI(Column.account))


waigua_role = DynamicTable.Table("waigua_role")
waigua_role.AddColumn(Column.role_id)
waigua_role.AddColumn(Column.account)
waigua_role.AddColumn(Column.role_name)
waigua_role.AddColumn(DynamicColumn.IntColumn("viplevel", "int", True, False, "vip等级"))
waigua_role.AddColumn(DynamicColumn.IntColumn("qpoint", "int", True, False, "消费Q点"))
waigua_role.AddColumn(DynamicColumn.IntColumn("pid", "int", True, False, "区ID"))
waigua_role.AddColumn(DynamicColumn.StringColumn("zone_name", 60, "区名"))
waigua_role.AddColumn(DynamicColumn.IntColumn("days", "int", True, False, "封号天数"))
waigua_role.AddColumn(DynamicColumn.IntColumn("usecounts", "int", True, False, "使用外挂次数"))
waigua_role.AddColumn(DynamicColumn.DateTimeColumn("lock_start_datetime", "封号开始时间"))
waigua_role.AddColumn(DynamicColumn.DateTimeColumn("lock_end_datetime", "封号结束时间"))
waigua_role.AddKey(DynamicColumn.ToPRI(Column.role_id))

#合服计划
#merge_plan = DynamicTable.Table("merge_plan")
#merge_plan.AddColumn(DynamicColumn.IntColumn("main_zoneid", "smallint", True, False, "主区ID"))
#merge_plan.AddColumn(DynamicColumn.StringColumn("merge_zids", 600, "合并的其他区ID"))
#merge_plan.AddColumn(DynamicColumn.DateTimeColumn("plan_datetime", "定制计划的时间"))
#merge_plan.AddColumn(DynamicColumn.IntColumn("is_done", "tinyint", True, False, "是否已经完成了"))
#merge_plan.AddColumn(DynamicColumn.DateTimeColumn("done_datetime", "执行的时间"))

#防沉迷信息
anti_data = DynamicTable.Table("anti_data")
anti_data.AddColumn(Column.account)
anti_data.AddColumn(DynamicColumn.StringColumn("name", 60, "名字"))
anti_data.AddColumn(DynamicColumn.StringColumn("idcard", 100, "身份证"))
anti_data.AddColumn(DynamicColumn.IntColumn("state", "int", True, False, "防沉迷认证状态  1-未满18 2-满18"))
anti_data.AddKey(DynamicColumn.ToPRI(Column.account))

if __name__ == "__main__":
	#在内网后台 配置 创建表 中创建这些表
	BuildTable()

