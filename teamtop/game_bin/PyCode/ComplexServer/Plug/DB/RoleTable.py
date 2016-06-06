#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 角色表定义
#===============================================================================
import cProcess
from Common import CValue, Define
from ComplexServer.Plug.DB import Column
from Util.MySQL import DynamicColumn, DynamicTable
from Game.Role.Data import EnumDisperseInt32

def BuildTable():
	'''
	构建本模块定义的表
	'''
	# 连接MySQL，并且构建数据库
	DynamicTable.MySQL.Init(cProcess.ProcessID)
	DynamicTable.MySQL.UserTable("role_sys_data_%s" % cProcess.ProcessID)
	# 构建表
	se = set()
	for value in globals().itervalues():
		if not isinstance(value, DynamicTable.Table):
			continue
		if value in se:
			continue
		se.add(value)
		value.Build()
	# 关闭MySQL
	DynamicTable.MySQL.Final()

#===============================================================================
# 表定义(注意表名要全小写字母)
#===============================================================================
# 角色表
# 关于角色数据相关的地方请搜索关键字  !@RoleData
role = DynamicTable.Table("role_data", CValue.P2_32 * cProcess.ProcessID + 1, {})
role.AddColumn(DynamicColumn.IntColumn("role_id", "bigint", True, True, "角色ID"))
role.AddColumn(Column.account)
role.AddColumn(Column.role_name)
role.AddColumn(DynamicColumn.IntColumn("command_size", "int", True, False, "角色命令总条数"))
role.AddColumn(DynamicColumn.IntColumn("command_index", "int", True, False, "角色命令执行位置"))
# array这个字段个数如下[i64, i32, i16, i8, id8, i1, di1, di64, ci8, cd, o]
# 这里将各种不定长数据放在一起是因为mysql的innodb每行最大只有8K，如果变长数据太多了会导致保存不了
role.AddColumn(DynamicColumn.ObjColumn("array", "一大波数据"))
# 下面是零散的i32
for uIdx in EnumDisperseInt32.L:
	role.AddColumn(DynamicColumn.IntColumn("di32_%s" % uIdx, "int", False, False, "第%s个零散的Int32整数" % uIdx))
role.AddKey(DynamicColumn.ToPRI(Column.role_id))
role.AddKey(DynamicColumn.ToUNI(Column.account))
role.AddKey(DynamicColumn.ToUNI(Column.role_name))

# 角色Obj表（做了水平分表）
for idx in xrange(Define.ROLE_HORIZONTAL_TABLE):
	obj = DynamicTable.Table("role_obj_%s" % idx)
	obj.AddColumn(Column.obj_id)
	obj.AddColumn(Column.role_id)
	obj.AddColumn(Column.obj_type)
	obj.AddColumn(Column.obj_int)
	obj.AddColumn(Column.obj_data)
	obj.AddKey(DynamicColumn.ToPRI(Column.obj_id))
	obj.AddKey(DynamicColumn.ToMUL(Column.role_id))
	globals()["obj_%s" % idx] = obj
	
# 角色命令
command = DynamicTable.Table("role_command")
command.AddColumn(DynamicColumn.IntColumn("command_id", "bigint", True, False, "命令ID"))
command.AddColumn(Column.role_id)
command.AddColumn(DynamicColumn.IntColumn("command_index", "int", True, False, "命令ID"))
command.AddColumn(DynamicColumn.DateTimeColumn("command_datetime", "命令新增时间"))
command.AddColumn(DynamicColumn.StringColumn("command_text", 1000, "命令文本"))
command.AddKey(DynamicColumn.ToPRI("command_id"))

# 角色命令缓存
command_cache = DynamicTable.Table("role_command_cache")
command_cache.AddColumn(Column.role_id)
command_cache.AddColumn(DynamicColumn.IntColumn("channel", "tiny", True, False, "角色线程号"))
command_cache.AddKey(DynamicColumn.ToUNI(Column.role_id))
command_cache.AddKey(DynamicColumn.ToMUL("channel"))

# 邮件
mail = DynamicTable.Table("role_mail", CValue.P2_32 * cProcess.ProcessID + 1, {})
mail.AddColumn(Column.role_id)
mail.AddColumn(DynamicColumn.IntColumn("mail_id", "bigint", True, True, "邮件ID"))
mail.AddColumn(DynamicColumn.StringColumn("title", 60, "邮件标题"))
mail.AddColumn(DynamicColumn.StringColumn("sender", 60, "发件人"))
mail.AddColumn(DynamicColumn.DateTimeColumn("dt", "时间"))
mail.AddColumn(DynamicColumn.StringColumn("content", 600, "内容"))
mail.AddColumn(DynamicColumn.IntColumn("mail_transaction", "smallint", True, False, "邮件所属事务"))
mail.AddColumn(DynamicColumn.ObjColumn("maildata", "邮件附件内容"))
mail.AddKey(DynamicColumn.ToPRI("mail_id"))
mail.AddKey(DynamicColumn.ToMUL(Column.role_id))

# 帐号登录信息
account_login = DynamicTable.Table("account_login")
account_login.AddColumn(Column.account)
account_login.AddColumn(DynamicColumn.StringColumn("session", 60, "session"))
account_login.AddColumn(DynamicColumn.DateTimeColumn("login_time", "登录时间"))
account_login.AddColumn(DynamicColumn.ObjColumn("thirdparty", "第三方数据"))
account_login.AddKey(DynamicColumn.ToUNI(Column.account))

# 充值
charge = DynamicTable.Table("charge", CValue.P2_32 * cProcess.ProcessID + 1, {"billno":"'billno'"})
charge.AddColumn(DynamicColumn.IntColumn("cid", "bigint", True, True, "充值id"))
charge.AddColumn(Column.account)
charge.AddColumn(Column.role_id)
charge.AddColumn(Column.from_1)
charge.AddColumn(Column.from_2)
charge.AddColumn(Column.from_3)
charge.AddColumn(DynamicColumn.StringColumn("create_from", 60, "创建来源"))
charge.AddColumn(DynamicColumn.StringColumn("payitem", 60, "货物信息"))
charge.AddColumn(DynamicColumn.IntColumn("level", "smallint", True, False, "充值时等级"))
charge.AddColumn(DynamicColumn.StringColumn("openkey", 60, "openkey"))
charge.AddColumn(DynamicColumn.StringColumn("token", 60, "token"))
charge.AddColumn(DynamicColumn.StringColumn("billno", 60, "billno"))
charge.AddColumn(DynamicColumn.IntColumn("amt", "int", False, False, "amt"))
charge.AddColumn(DynamicColumn.IntColumn("payamt_coins", "int", False, False, "payamt_coins"))
charge.AddColumn(DynamicColumn.IntColumn("pubacct_payamt_coins", "int", False, False, "pubacct_payamt_coins"))
charge.AddColumn(DynamicColumn.StringColumn("confirm", 120, "confirm"))
charge.AddColumn(DynamicColumn.DateTimeColumn("dt", "时间"))
charge.AddKey(DynamicColumn.ToPRI("cid"))
charge.AddKey(DynamicColumn.ToMUL("token"))
charge.AddKey(DynamicColumn.ToMUL("billno"))
charge.AddKey(DynamicColumn.ToMUL(Column.account))
charge.AddKey(DynamicColumn.ToMUL(Column.role_id))
charge.AddKey(DynamicColumn.ToMUL("dt"))

merge_info = DynamicTable.Table("merge_info")
merge_info.AddColumn(DynamicColumn.IntColumn("zone_id", "int", False, False, "区信息"))

report_info = DynamicTable.Table("report_info")
report_info.AddColumn(Column.role_id)
report_info.AddColumn(DynamicColumn.DateTimeColumn("report_time", "上报时间"))
report_info.AddColumn(DynamicColumn.SmallObjColumn("report_info", "上报信息"))
report_info.AddColumn(DynamicColumn.SmallObjColumn("login_info", "登陆信息"))
report_info.AddKey(DynamicColumn.ToPRI(Column.role_id))

if __name__ == "__main__":
	from Util.PY import Load
	Load.LoadPartModule("Common")
	Load.LoadPartModule("Global")
	BuildTable()

