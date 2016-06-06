#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("DB.MailVisit")
#===============================================================================
# 邮件
#===============================================================================
import cComplexServer
import Environment
from ComplexServer.Plug.DB import DBWork, DBHelp
from Game.Role.Mail import EnumMail

LoadAllMailSQL = "select mail_id, title, sender, dt from role_mail where role_id = %s and mail_id > %s limit 200;"
LoadOneMailSQL = "select content, maildata from role_mail where mail_id = %s;"
UseOneMailSQL = "select mail_transaction, maildata from role_mail where mail_id = %s and role_id = %s;"
DelOneMailSQL = "delete from role_mail where mail_id = %s;"

class LoadAllMail(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute(LoadAllMailSQL % self.arg)
		return cur.fetchall()

class LoadOneMail(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute(LoadOneMailSQL % self.arg)
		result = cur.fetchall()
		if result:
			row = result[0]
			#content, maildata
			return row[0], eval(row[1])
		else:
			return None

#提取附件(参数是邮件ID列表)
class UseMail(DBWork.DBVisit):
	def _execute(self, cur):
		roleid, mailids, itemPackageSize, tarotPackageSize, talentPackageSize = self.arg
		result = []
		CUR_EXECUTE = cur.execute
		CUR_FETCHALL = cur.fetchall
		needPackageSize = 0
		needTarotSize = 0
		needTalentSize = 0
		for mail_id in mailids:
			#查询邮件附件
			CUR_EXECUTE(UseOneMailSQL % (mail_id, roleid))
			res = CUR_FETCHALL()
			if not res:
				continue
			row = res[0]
			mail_transaction = row[0]
			maildata = eval(row[1])
			items = maildata.get(EnumMail.EnumItemsKey)
			if items:
				needPackageSize += len(items)
				if needPackageSize > itemPackageSize:
					break
			tarots = maildata.get(EnumMail.EnumTarotCardKey)
			if tarots:
				needTarotSize += len(tarots)
				if needTarotSize > tarotPackageSize:
					break
				
			talents = maildata.get(EnumMail.EnumTalentCardKey)
			if talents:
				needTalentSize += len(talents)
				if needTalentSize > talentPackageSize:
					break
			
			#记录附近内容
			result.append((mail_id, mail_transaction, maildata))
			#删除邮件
			cur.execute(DelOneMailSQL % mail_id)
			CUR_FETCHALL()
		return result

class SendMail(DBWork.DBVisit):
	def _execute(self, cur):
		roleid, title, sender, content, mail_transaction, maildata = self.arg
		return DBHelp.InsertRoleMail(cur, roleid, title, sender, content, mail_transaction, maildata)

class HasItemsMail(DBWork.DBVisit):
	def _execute(self, cur):
		# 查找是否有新邮件
		h = cur.execute("select 1 from role_mail where role_id = %s limit 1;" % self.arg)
		cur.fetchall()
		return h

class DelMail(DBWork.DBVisit):
	def _execute(self, cur):
		cur.execute("delete from role_mail where dt < %s;", DBHelp.GetTwoWeekAgoDateTime())

def AfterNewDay():
	DBWork.OnDBVisit_MainThread(0, "DelMail", None, (None, None))

if Environment.HasDB and "_HasLoad" not in dir():
	LoadAllMail.reg()
	LoadOneMail.reg()
	UseMail.reg()
	SendMail.reg()
	HasItemsMail.reg()
	DelMail.reg()
	cComplexServer.RegAfterNewDayCallFunction(AfterNewDay)
