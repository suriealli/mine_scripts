#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 动态构建MySQL的表以及查询插入
#===============================================================================
import cDateTime
import DynamicColumn
from ComplexServer.Plug.DB import DBHelp
from World import Define

class MySQL(object):
	con = None
	
	@classmethod
	def Init(cls, pid):
		'''
		初始化数据库连接
		@param cls:
		@param dbprocess:db进程
		'''
		import MySQLdb
		ip, port, user, pwd = DBHelp.GetMySQLInfoByID(pid)
		cls.user = user
		cls.pwd = pwd
		cls.con = MySQLdb.connect(host = ip, port = port, user = user, passwd = pwd, charset = "utf8", use_unicode = False)
		if Define.SQL_TIME_ZONE is not None:
			with cls.con as cur:
				if cDateTime.GetDST() > 0:
					cur.execute(Define.SQL_TIME_ZONE_DST)
				else:
					cur.execute(Define.SQL_TIME_ZONE)
				cur.close()
	@classmethod
	def InitWeb(cls, connect_info):
		import MySQLdb
		ip, port, user, pwd = connect_info
		cls.user = user
		cls.pwd = pwd
		cls.con = MySQLdb.connect(host = ip, port = port, user = user, passwd = pwd, charset = "utf8", use_unicode = False)
		if Define.SQL_TIME_ZONE is not None:
			with cls.con as cur:
				if cDateTime.GetDST() > 0:
					cur.execute(Define.SQL_TIME_ZONE_DST)
				else:
					cur.execute(Define.SQL_TIME_ZONE)
				cur.close()
		
	@classmethod
	def UserTable(cls, name):
		'''
		使用数据表
		@param cls:
		@param name:
		'''
		cur = cls.con.cursor()
		cur.execute("show databases;")
		for row in cur.fetchall():
			if row[0] == name:
				break
		else:
			sql = "CREATE DATABASE %s character set utf8 collate utf8_general_ci;" % name
			print sql
			cur.execute(sql)
		cls.con.change_user(user = cls.user, passwd = cls.pwd, db = name)
		cls.con.set_character_set("utf8")
	
	@classmethod
	def GetConnect(cls):
		'''
		获取连接
		@param cls:
		'''
		return cls.con
	
	@classmethod
	def Final(cls):
		cls.con.close()
		del cls.con
	
class Table(object):
	def __init__(self, name, auto_increment = None, auto_sql = None):
		'''
		MySQL数据库表
		@param name:表名
		@param auto_increment:自增长基数
		'''
		# 列名
		self.name = name
		# 自增长信息
		self.auto_increment = "" if auto_increment is None else "auto_increment=%s" % auto_increment
		# 自增长填充sql（mysql从binlog还原的时候会丢失自增长信息）
		self.auto_sql = auto_sql
		# column和key
		self.columns = {}
		self.keys = {}
		# 主键名
		self.pri = None
	
	def Rename(self, name):
		self.name = name
		del self.hasTable
		if hasattr(self, "hasTable"):
			delattr(self, "hasTable")
	
	def Clone(self, name):
		table = Table(name)
		table.auto_increment = self.auto_increment
		for column in self.columns.itervalues():
			table.AddColumn(column)
		for key in self.keys.itervalues():
			table.AddKey(key)
		return table
	
	def AddColumn(self, column):
		'''
		增加一列
		@param column:
		'''
		assert(column.name not in self.columns)
		self.columns[column.name] = column
	
	def GetColumn(self, name):
		'''
		根据名字，获取一个列信息
		@param name:
		'''
		return self.columns[name]
	
	def AddKey(self, key):
		'''
		增加一个约束
		@param key:
		'''
		assert(key.name not in self.keys)
		self.keys[key.name] = key
		if key.tkey == key.PRI:
			self.pri = key.name
	
	def GetKey(self, name):
		'''
		根据名字，获取一个索引信息
		@param name:
		'''
		return self.keys[name]
	
	def HasAutoIncrement(self):
		'''
		是否是自增长的
		'''
		for column in self.columns.itervalues():
			# 如果这列是自增长的，则不要指定插入的值
			if isinstance(column, DynamicColumn.IntColumn) and column.auto_increment:
				return True
		return False
	
	def GetColumnNames(self):
		'''
		获取所有的列名
		'''
		names = []
		for name, column in self.columns.iteritems():
			# 如果这列是自增长的，则不要指定插入的值
			if isinstance(column, DynamicColumn.IntColumn) and column.auto_increment:
				continue
			names.append(name)
		names.sort()
		return names
	
	def GetSelectAllValueSQL(self, where):
		'''
		获取整表查询的SQL语句
		@param where:
		'''
		names = self.GetColumnNames()
		return "SELECT " + ",".join(names) + " FROM %s %s;" % (self.name, where)
	
	def GetInsertAllValueSQL(self, H = "INSERT"):
		'''
		获取整表插入的SQL语句
		'''
		names = self.GetColumnNames()
		return "%s into  %s(" % (H, self.name) + ",".join(names) + ") values(" + ",".join(["%s"] * len(names)) + ");"
	
	def GetColumnIndex(self, name):
		'''
		获取某列对应的索引
		@param name:列名
		'''
		idx = -1
		for _name in self.GetColumnNames():
			idx += 1
			if name == _name:
				return idx
		assert False
	
	def ColumnInfo(self):
		'''
		获取数据库中的表的列信息
		'''
		self.infos = []
		# 没有这个表，直接返回之
		if not self.HasTable():
			return
		with MySQL.GetConnect() as cur:
			# 查询列信息
			cur.execute("desc %s;" % self.name)
			infos = cur.fetchall()
			# 查询约束信息
			cur.execute("SHOW keys FROM %s" % self.name)
			priname = ""
			for keyinfo in cur.fetchall():
				if keyinfo[2] == "PRIMARY":
					priname = keyinfo[4]
			# 修正MySQL自动把第一个唯一索引显示为主键的问题
			for info in infos:
				info = list(info)
				if info[DynamicColumn.INFO_KEY] == DynamicColumn.Key.PRI:
					if info[DynamicColumn.INFO_NAME] != priname:
						info[DynamicColumn.INFO_KEY] = DynamicColumn.Key.UNI
				info = tuple(info)
				self.infos.append(info)
			cur.close()
	
	def IsUniqueData(self, name):
		'''
		检测某列的值是否是唯一的
		@param name:列名
		'''
		with MySQL.GetConnect() as cur:
			cur.execute("SELECT count(distinct(%s)) , count(*) FROM %s;" % (name, self.name))
			ret = cur.fetchall()
			cur.close()
			row = ret[0]
			return row[0] == row[1]
	
	def IsScope(self, name, minv, maxv):
		'''
		检测某列的值是否在指定的范围内
		@param name:列名
		@param minv:最小值
		@param maxv:最大值
		'''
		with MySQL.GetConnect() as cur:
			cur.execute("SELECT 1 FROM %s WHERE %s < %s or %s > %s LIMIT 1;" % (self.name, name, minv, name, maxv))
			ret = cur.fetchall()
			cur.close()
			return not ret
	
	def HasTable(self):
		'''
		数据库是否有这个表
		'''
		if not hasattr(self, "hasTable"):
			with MySQL.GetConnect() as cur:
				cur.execute("show tables")
				for row in cur.fetchall():
					if row[0] == self.name:
						self.hasTable = True
						cur.close()
						break
				else:
					self.hasTable = False
					cur.close()
		return self.hasTable
	
	def HasData(self):
		'''
		数据库的这个表里面是否有数据
		'''
		if not hasattr(self, "hasData"):
			with MySQL.GetConnect() as cur:
				cur.execute("SELECT count(*) from %s LIMIT 1" % self.name)
				if cur.fetchall()[0][0]:
					self.hasData = True
				else:
					self.hasData = False
				cur.close()
		return self.hasData
	
	def CheckBuild(self):
		'''
		检测构建数据库表
		'''
		# 至少有1列
		assert(self.columns)
		# 约束依赖于列
		for kname in self.keys.iterkeys():
			assert(kname in self.columns)
		# 只能有一列AUTO_INCREMENT
		ainame = None
		for column in self.columns.itervalues():
			if not isinstance(column, DynamicColumn.IntColumn):
				continue
			if not column.auto_increment:
				continue
			assert(ainame is None)
			ainame = column.name
		# AUTO_INCREMENT必须有唯一索引或者主键索引
		if ainame:
			key = self.keys[ainame]
			assert(key.IsUnique())
		# 如果表不存在，则不必检测兼容性了
		if not self.HasTable():
			return
		# 获取已经存在的列信息
		self.ColumnInfo()
		# 检测已经存在的列和定义的列是否可以改变
		for info in self.infos:
			column = self.columns.get(info[DynamicColumn.INFO_NAME])
			# 如果前后都有这列，必须兼容
			if column:
				assert(column.IsCompatible(info, self))
			# 如果以前有这一列，现在没有了
			else:
				# 如果此表有数据，必须要求这一列可以为NULL（否则会对插入数据有影响）
				# 如果没有数据，则可以删除这一列
				if self.HasData():
					if info[DynamicColumn.INFO_NULL] != "YES":
						print "GE_EXC, INFO_NULL", info[DynamicColumn.INFO_NAME]
					assert(info[DynamicColumn.INFO_NULL] == "YES")
			key = self.keys.get(info[DynamicColumn.INFO_NAME])
			# 如果前后都有这约束，必须兼容
			if key and info[DynamicColumn.INFO_KEY] != DynamicColumn.Key.NO:
				assert(key.IsEqual(info, self))
	
	def Build(self):
		'''
		构建数据库表
		'''
		self.CheckBuild()
		if self.HasTable():
			sql = self.Change()
			with MySQL.GetConnect() as cur:
				if sql:
					print "\n".join(sql)
					for one_sql in sql:
						cur.execute(one_sql)
				self.First(cur)
				cur.close()
		else:
			sql = self.Create()
			with MySQL.GetConnect() as cur:
				if sql:
					print sql
					cur.execute(sql)
				self.First(cur)
				cur.close()
	
	def First(self, cur):
		'''
		对于自增长的表，自动填充第一行。
		'''
		if not self.auto_increment:
			return
		cur.execute("select count(*) from %s limit 1;" % self.name)
		cnt = cur.fetchall()[0][0]
		if cnt != 0:
			return
		if self.auto_sql is None:
			print "GE_EXC table(%s) is empty with auto increment" % self.name
			return
		# 自动填充一行
		defual_value = {DynamicColumn.IntColumn: 0,
					DynamicColumn.StringColumn: "''",
					DynamicColumn.TextColumn: "''",
					DynamicColumn.ObjColumn: "'{}'",
					DynamicColumn.DateTimeColumn: "now()"}
		values = []
		for name in self.GetColumnNames():
			value = self.auto_sql.get(name)
			if value is None:
				column = self.columns[name]
				value = defual_value[column.__class__]
			values.append(value)
		sql = self.GetInsertAllValueSQL()
		cur.execute(sql % tuple(values))
	
	def Create(self):
		'''
		创建表
		'''
		# 构造表头
		sql_head = "CREATE TABLE %s (\n" % self.name
		sql_body = []
		# 构造列信息
		for column in self.columns.itervalues():
			sql_body.append(column.CreateColumnSQL())
		# 构造约束信息
		for key in self.keys.itervalues():
			sql_body.append(key.CreateKeySQL())
		# 构造表尾
		sql_tail = "\n)ENGINE=InnoDB %s DEFAULT CHARSET=utf8 CHECKSUM=1 DELAY_KEY_WRITE=1" % self.auto_increment
		return sql_head + ",\n".join(sql_body) + sql_tail
	
	def Change(self):
		'''
		修改表
		'''
		# 构建已有的表信息
		cd = {}
		for info in self.infos:
			cd[info[DynamicColumn.INFO_NAME]] = info
		# 修正数据库语句
		sqls = []
		# 遍历定义的列
		for column in self.columns.itervalues():
			info = cd.get(column.name)
			# 如果数据库没有该列，是新定义的，添加之
			if not info:
				sqls.append(column.AddColumnSQL(self))
				continue
			# 如果数据库和定义的列一样，则忽视之
			if column.IsEqual(info, self):
				continue
			# 否则该列有修改，必须兼容，修改之
			assert(column.IsCompatible(info, self))
			sqls.append(column.ChangeColumnSQL(self))
		# 遍历已有的列
		for name, info in cd.iteritems():
			# 数据库中的列有定义，在上面的循环中已处理
			if name in self.columns:
				continue
			# 如果数据库已有数据，该列必须可为NULL
			if self.HasData():
				assert(info[DynamicColumn.INFO_NULL] == "YES")
			# 没数据，则删除该列
			else:
				sqls.append(DynamicColumn.DropColumnSQL(info, self))
		# 遍历定义的约束
		for key in self.keys.itervalues():
			info = cd.get(key.name)
			# 如果数据库中有该约束信息
			if info:
				# 如果约束为空，则增加之
				if info[DynamicColumn.INFO_KEY] == DynamicColumn.Key.NO:
					sqls.append(key.AddKeySQL(self))
				# 否则数据库中的约束必须和定义的约束相等
				else:
					assert(key.IsEqual(info, self))
			# 没有则增加之
			else:
				sqls.append(key.AddKeySQL(self))
		# 遍历数据库中的约束
		for name, info in cd.iteritems():
			# 无约束的信息，忽视之
			if info[DynamicColumn.INFO_KEY] == DynamicColumn.Key.NO:
				continue
			# 如果该约束在数据库中有而没定义，删除之
			if name not in self.keys:
				sqls.append(DynamicColumn.DropKeySQL(info, self))
		
		return sqls
		


