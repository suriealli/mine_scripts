#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("DB.RoleVisit")
#===============================================================================
# 角色访问
# 注意，command_size是不保存的
#===============================================================================
import cComplexServer
import Environment
from Common import CValue, Define, Serialize
from Common.Message import PyMessage
from ComplexServer import Thread
from ComplexServer.Plug.DB import DBWork, DBHelp, DBReverse
from Game.Role.Data import EnumDisperseInt32

# 关于角色数据相关的地方请搜索关键字  !@RoleData
# 载入角色数据的SQL
LoadRoleSQL = "select account, role_id, role_name, command_size, command_index, array"
for uIdx in EnumDisperseInt32.L:
	LoadRoleSQL += ", di32_%s" % uIdx
LoadRoleSQL += " from role_data where role_id = %s;"
# 载入角色OBJ的SQL
LoadObjSQL = "select obj_id, obj_type, obj_int, obj_data from role_obj_%s where role_id = %s;"
# 保存角色数据的SQL
SaveRoleSQL = "update role_data set command_index = %s, array = %s"
for uIdx in EnumDisperseInt32.L:
	SaveRoleSQL += ", di32_%s = %s" % (uIdx, "%s")
SaveRoleSQL += " where role_id = %s;"
# 设置角色为活跃的SQL
# di32_0就是角色最后活跃时间，定义在Game.Role.Data.EnumDisperseInt32
SetRoleActiveSQL = "update role_data set di32_0 = unix_timestamp(now()) where role_id = %s;"

# 保存角色OBJ的SQ
DelObjSQL = "delete from role_obj_%s where role_id = %s;"
SaveObjSQLs = ["insert into role_obj_%s" % i + " (role_id, obj_id, obj_type, obj_int, obj_data) values(%s, %s, %s, %s, %s);" for i in xrange(Define.ROLE_HORIZONTAL_TABLE)]

def DeleteRoleCommand(cur, roleid, index):
	if index == 0: return
	begin_index = (roleid % CValue.P2_32) * CValue.P2_32
	end_index = begin_index + index
	cur.execute("delete role_command where command_id > %s and command_id <= %s;" % (begin_index, end_index))

class LoadRole(DBWork.DBVisit):
	def executeex(self, thread):
		roleid, processid = self.arg
		# 如果是网络模式，则要检测权限
		if self.isnet():
			lastprocessid = thread.rolelimit.get(roleid)
			# 如果该角色数据被其他进程载入了,【则不能载入这个角色的数据】
			if lastprocessid is not None:
				# 如果是同一个进程，则打印一个警告【然后返回一个特殊值】
				if lastprocessid == processid:
					print "GE_EXC, role(%s) repeat load by process(%s)" % (roleid, processid)
					self.result((None, None))
				# 如果是不同的进程， 则命令其他进程先【保存】角色
				else:
					Thread.ThreadApply(RequestLogicSaveRole_MainThread, (lastprocessid, self.arg, self.back))
				# 这里载入出意外了，停止载入
				return
			# 【如果】该角色没被其他进程载入，则保存进程对角色的权限
			else:
				thread.rolelimit[roleid] = processid
		# 非网络模式，或者在网络模式下没有其他进程载入了这个角色数据，走正常流程
		with thread.con as cur:
			# 设置玩家为活跃的
			# 关于角色数据相关的地方请搜索关键字  !@RoleData。
			# di32_0就是角色最后活跃时间，定义在Game.Role.Data.EnumDisperseInt32
			cur.execute(SetRoleActiveSQL % roleid)
			cur.execute(LoadRoleSQL % roleid)
			roledata = cur.fetchall()
			if roledata:
				roledata = list(roledata[0])
				roledata[5] = Serialize.String2PyObjEx(roledata[5])
				cur.execute(LoadObjSQL % (roleid % Define.ROLE_HORIZONTAL_TABLE, roleid))
				roleobj = cur.fetchall()
				self.result((roledata, roleobj))
			else:
				self.result(([], []))
			# 关闭游标
			cur.close()

class LoadRoleData_Force(DBWork.DBVisit):
	def executeex(self, thread):
		roleid, processid = self.arg
		# 如果是网络模式，则要检测权限
		if self.isnet():
			lastprocessid = thread.rolelimit.get(roleid)
			# 如果该角色数据被其他进程载入了,【则T掉其他进程的该角色，不等待其他进程保存，强行载入该角色的数据】
			if lastprocessid is not None:
				# 如果是同一个进程，则打印一个警告
				if lastprocessid == processid:
					print "GE_EXC, role(%s) repeat force load by process(%s)" % (roleid, lastprocessid)
				# 如果是不同的进程， 则命令其他进程【踢掉】角色
				else:
					Thread.ThreadApply(RequestLogicKickRole_MainThread1, (lastprocessid, roleid))
			# 【强行】保存进程对角色的权限
			thread.rolelimit[roleid] = processid
		# 非网络模式，或者在网络模式下没有其他进程载入了这个角色数据，走正常流程
		with thread.con as cur:
			# 设置玩家为活跃的
			# 关于角色数据相关的地方请搜索关键字  !@RoleData。
			# di32_0就是角色最后活跃时间，定义在Game.Role.Data.EnumDisperseInt32
			cur.execute(SetRoleActiveSQL % roleid)
			cur.execute(LoadRoleSQL % roleid)
			roledata = cur.fetchall()
			if roledata:
				roledata = list(roledata[0])
				roledata[5] = Serialize.String2PyObjEx(roledata[5])
				cur.execute(LoadObjSQL % (roleid % Define.ROLE_HORIZONTAL_TABLE, roleid))
				roleobj = cur.fetchall()
				self.result((roledata, roleobj))
			else:
				self.result(([], []))
			cur.close()

class SaveRole(DBWork.DBVisit):
	def executeex(self, thread):
		roleid, processid, roledata, roleobj = self.arg
		roledata = roledata[:]
		roledata[1] = Serialize.PyObj2String(roledata[1])
		# 如果是网络模式，则要检测权限
		if self.isnet():
			# 如果权限不正确，不能保存角色数据并通知逻辑进程踢玩家
			lastprocessid = thread.rolelimit.get(roleid)
			if lastprocessid is None:
				print "GE_EXC, process(%s) save role(%s) with out limit." % (processid, roleid)
				Thread.ThreadApply(RequestLogicKickRole_MainThread2, (self.back[0], roleid))
				return
			if lastprocessid != processid:
				print "GE_EXC, process(%s) save role(%s) with out limit(%s)" % (processid, roleid, lastprocessid)
				Thread.ThreadApply(RequestLogicKickRole_MainThread2, (self.back[0], roleid))
				return
		# 正常保存角色数据
		with thread.con as cur:
			cur.execute(SaveRoleSQL, roledata)
			table_index = roleid % Define.ROLE_HORIZONTAL_TABLE
			cur.execute(DelObjSQL % (table_index, roleid))
			if roleobj:
				sql = SaveObjSQLs[table_index]
				arg = [(roleid, obj[0], obj[1], obj[2], obj[3]) for obj in roleobj]
				cur.executemany(sql, arg)
			cur.close()

class ExitRole(DBWork.DBVisit):
	def executeex(self, thread):
		# 删除进程对该角色的权限
		roleid, processid = self.arg
		lastprocessid = thread.rolelimit.get(roleid)
		if processid == lastprocessid:
			del thread.rolelimit[roleid]

class ForceExitRole(DBWork.DBVisit):
	def executeex(self, thread):
		roleid, oldprocessid = self.arg
		lastprocessid = thread.rolelimit.get(roleid)
		# 可以尝试再登陆
		if lastprocessid is None or lastprocessid == oldprocessid:
			# 删除权限
			if lastprocessid is not None:
				del thread.rolelimit[roleid]
			# 通知逻辑进程再次尝试载入角色数据
			self.result(True)
		# 此角色已经被其他进程登陆了
		else:
			self.result(False)

class LoadCommand(DBWork.DBVisit):
	def executeex(self, thread):
		roleid, processid, index = self.arg
		# 如果是网络模式，要检测权限
		if self.isnet():
			# 如果权限不正确，则不载入角色命令
			if thread.rolelimit.get(roleid) != processid:
				return
		# 正常载入角色命令
		base = (roleid % CValue.P2_32) * CValue.P2_32
		begin_index = base + index
		end_index = base + CValue.P2_32
		with thread.con as cur:
			cur.execute("select command_index, command_text from role_command where command_id > %s and command_id < %s order by command_index;" % (begin_index, end_index))
			self.result(cur.fetchall())
			cur.close()

class SaveCommand(DBWork.DBVisit):
	def _execute(self, cur):
		roleid, command = self.arg
		if not DBHelp.InsertRoleCommand_Cur(cur, roleid, command):
			print "GREEN lost role(%s) command(%s)" % (roleid, command)

class CheckCommand(DBWork.DBVisit):
	def executeex(self, thread):
		with thread.con as cur:
			cur.execute("select role_id from role_command_cache where channel = %s;" % thread.channel)
			result = cur.fetchall()
			if result:
				cur.execute("delete from role_command_cache where channel = %s" % thread.channel)
			cur.close()
			# 没有缓存，返回之
			if not result:
				return
			# 如果是网络模式，则按照processid分类
			if self.isnet():
				notifys = {}
				for row in result:
					roleid = row[0]
					processid = thread.rolelimit.get(roleid)
					if processid is None:
						continue
					if processid in notifys:
						notifys[processid].append(roleid)
					else:
						notifys[processid] = [roleid,]
				# 如果有需要通知的，则交给主线程通知
				if notifys:
					Thread.ThreadApply(NotifyLogicRoleCommand_MainThread_Net, (notifys, ))
			# 否则直接通知主线程
			else:
				if result:
					Thread.ThreadApply(NotifyLogicRoleCommand_MainThread_Local, (result, ))

class Change_Name(DBWork.DBVisit):
	def _execute(self, cur):
		roleId, NewName = self.arg
		ret = cur.execute("update ignore role_data set role_name = '%s' where role_id = %s;" % (NewName, roleId))
		if not ret:
			#改名失败
			return False
		cur.close()
		return True

def RequestLogicSaveRole_MainThread(lastprocessid, arg, back):
	sessionid = DBReverse.ProcessIDToSessionID.get(lastprocessid)
	if sessionid is None:
		print "GE_EXC RequestLogicSaveRole is fail.process id(%s)" % lastprocessid
		return
	roleid, _ = arg
	cComplexServer.SendPyMsgAndBack(sessionid, PyMessage.DB_MustSaveRole, roleid, 15, OnLogicSaveRole_MainThread, (roleid, lastprocessid, back))

def OnLogicSaveRole_MainThread(callargv, regparam):
	roleid, lastprocessid, back = regparam
	if callargv is None:
		print "GE_EXC, db kick role(%s) but logic not execute." % roleid
	# 强制旧的逻辑进程失去角色权限
	DBWork.OnDBVisit_MainThread(DBHelp.GetDBChannelByRoleID(roleid), "ForceExitRole", (roleid, lastprocessid), back)

def RequestLogicKickRole_MainThread1(processid, roleid):
	sessionid = DBReverse.ProcessIDToSessionID.get(processid)
	if sessionid is None:
		print "GE_EXC RequestLogicKickRole is fail.process id(%s)" % processid
		return
	cComplexServer.SendPyMsg(sessionid, PyMessage.DB_MustKickRole, roleid)

def RequestLogicKickRole_MainThread2(sessionid, roleid):
	cComplexServer.SendPyMsg(sessionid, PyMessage.DB_MustKickRole, roleid)

def NotifyLogicRoleCommand_MainThread_Net(notifys):
	for processid, roleids in notifys.iteritems():
		sessionid = DBReverse.ProcessIDToSessionID.get(processid)
		if sessionid is None:
			print "GE_EXC NotifyLogicRoleCommand is fail.process id(%s)" % processid
			continue
		cComplexServer.SendPyMsg(sessionid, PyMessage.DB_NotifyCommand, roleids)

def NotifyLogicRoleCommand_MainThread_Local(result):
	from Game.Role import Command
	Command.OnNotifyRoleCommand_Local(result)

if Environment.HasDB and "_HasLoad" not in dir():
	LoadRole.reg()
	LoadRoleData_Force.reg()
	SaveRole.reg()
	ExitRole.reg()
	ForceExitRole.reg()
	LoadCommand.reg()
	SaveCommand.reg()
	CheckCommand.reg()
	Change_Name.reg()
