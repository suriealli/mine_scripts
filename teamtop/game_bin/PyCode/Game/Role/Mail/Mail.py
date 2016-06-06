#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Mail.Mail")
#===============================================================================
# 邮件模块
#===============================================================================
import cRoleMgr
import cLogTransaction
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from ComplexServer.Plug.DB import DBProxy
from Game import RTF
from Game.Role.Mail import EnumMail
from Game.Role.Data import EnumTempObj, EnumInt32
from Game.Role import Event
import Environment


# 发送一封邮件(需要加日志事务)
@RTF.RegFunction
def SendMail(roleid, title, sender, content, items=None, tarotList=None, money=0, exp=0, tili=0, bindrmb=0, unbindrmb=0, talents=None, jtgold=0, jtexp=0, contribution=0, kuafuMoney=0, touchpoint=0):
	'''
	发送一封邮件给玩家
	@param roleid:角色id
	@param title:邮件标题
	@param sender:邮件发送者
	@param content:邮件内容
	@param items:邮件物品[(coding, count),]
	@param tarotList:命魂[cardType,]
	@param money:钱
	@param exp:经验
	@param tili:体力
	@param bindrmb:魔晶
	@param unbindrmb:系统神石
	'''
	mailData = {}
	if items:
		mailData[EnumMail.EnumItemsKey] = items
	if tarotList:
		mailData[EnumMail.EnumTarotCardKey] = tarotList
	if money:
		mailData[EnumMail.EnumMonyKey] = money
	if exp:
		mailData[EnumMail.EnumExpKey] = exp
	if tili:
		mailData[EnumMail.EnumTiLiKey] = tili
	if bindrmb:
		mailData[EnumMail.EnumBindRMBKey] = bindrmb
	if unbindrmb:
		mailData[EnumMail.EnumUnbindRMBKey] = unbindrmb
	if talents:
		mailData[EnumMail.EnumTalentCardKey] = talents
	if jtgold:
		mailData[EnumMail.EnumJTGold] = jtgold
	if jtexp:
		mailData[EnumMail.EnumJTExp] = jtexp
	if contribution:
		mailData[EnumMail.EnumContribution] = contribution
	if kuafuMoney:
		mailData[EnumMail.EnumKuaFuMoney] = kuafuMoney
	if touchpoint:
		mailData[EnumMail.EnumTouchPoint] = touchpoint
	tra, _ = cLogTransaction.GetTransaction()
	if not tra:
		print "GE_EXC, send mail not Transaction (%s)" % roleid
	DBProxy.DBRoleVisit(roleid, "SendMail", (roleid, title, sender, content, tra, mailData), OnSendMail, roleid)
	if mailData:
		AutoLog.LogBase(roleid, AutoLog.eveSendMail, mailData)

def OnSendMail(result, param):
	#系统发送邮件成功，通知这个玩家自己有新的邮件
	if not result:return
	role = cRoleMgr.FindRoleByRoleID(param)
	if not role: return
	role.SendObj(Mail_YouHaveNew, None)


def RequestLoadAllMail(role, msg):
	'''
	客户端请求载入未读取的邮件
	@param role:
	@param msg:
	'''
	if Environment.IsCross:
		return
	backfunid, mail_id = msg
	roleid = role.GetRoleID()
	DBProxy.DBRoleVisit(roleid, "LoadAllMail", (roleid, mail_id), OnLoadAllMail, (role, backfunid))

def OnLoadAllMail(result, regparam):
	role, backfunid = regparam
	role.CallBackFunction(backfunid, result)
	

def RequestLoadOneMail(role, msg):
	'''
	客户端请求载入邮件具体内容
	@param role:
	@param msg:
	'''
	if Environment.IsCross:
		return
	backfuid, mailid = msg
	DBProxy.DBRoleVisit(role.GetRoleID(), "LoadOneMail", mailid, OnLoadOneMail, (role, backfuid))

def OnLoadOneMail(result, regparam):
	role, backfunid = regparam
	role.CallBackFunction(backfunid, result)


def RequestUseMail(role, msg):
	'''
	客户端请求使用邮件
	@param role:
	@param msg:
	'''
	if Environment.IsCross:
		return
	backfuid, mailids = msg
	if len(mailids) > 200:
		print "GE_EXC RequestUseMail too many (%s) , (%s)" % (role.GetRoleID(), len(mailids))
		mailids = mailids[:200]
	roleid = role.GetRoleID()
	itemPackageSize = role.PackageEmptySize()
	tarotPackageSize = role.GetTempObj(EnumTempObj.enTarotMgr).PackageEmptySize()
	talentPackageSize = role.GetTempObj(EnumTempObj.TalentCardMgr).GetEmptySize()
	
	DBProxy.DBRoleVisit(roleid, "UseMail", (roleid, mailids, itemPackageSize, tarotPackageSize, talentPackageSize), OnUseMail, (role, backfuid))

def OnUseMail(result, regparam):
	#使用邮件回调
	role, backfunid = regparam
	usemalis = []
	UA = usemalis.append
	for mailid, mail_transaction, maildata in result:
		UA(mailid)
		if not mail_transaction:
			with TraUseMail:
				UseMailData(role, maildata)
		else:
			with AutoLog.BuildTransaction(mail_transaction):
				UseMailData(role, maildata)

	role.CallBackFunction(backfunid, usemalis)


def UseMailData(role, maildata):
	money = maildata.get(EnumMail.EnumMonyKey)
	if money:
		role.IncMoney(money)
	exp = maildata.get(EnumMail.EnumExpKey)
	if exp:
		role.IncExp(exp)
	tili = maildata.get(EnumMail.EnumTiLiKey)
	if tili:
		role.IncTiLi(tili)
	bindrmb = maildata.get(EnumMail.EnumBindRMBKey)
	if bindrmb:
		role.IncBindRMB(bindrmb)
	unbindrmb = maildata.get(EnumMail.EnumUnbindRMBKey)
	if unbindrmb:
		role.IncUnbindRMB_S(unbindrmb)
	items = maildata.get(EnumMail.EnumItemsKey)
	if items:
		ROLE_ADDITEM = role.AddItem
		for itemCoding, cnt in items:
			ROLE_ADDITEM(itemCoding, cnt)
	tarots = maildata.get(EnumMail.EnumTarotCardKey)
	if tarots:
		ROLE_ADDTAROT = role.AddTarotCard
		for cardType in tarots:
			ROLE_ADDTAROT(cardType, 1)
	
	talentcards = maildata.get(EnumMail.EnumTalentCardKey)
	if talentcards:
		RATC = role.AddTalentCard
		for cardType in talentcards:
			RATC(cardType)
	
	jtgold = maildata.get(EnumMail.EnumJTGold)
	if jtgold:
		role.IncI32(EnumInt32.JTGold, jtgold)
		
	jtexp = maildata.get(EnumMail.EnumJTExp)
	if jtexp:
		role.IncI32(EnumInt32.JTExp, jtexp)
	
	contribution = maildata.get(EnumMail.EnumContribution)
	if contribution:
		role.IncContribution(contribution)
	
	kuafuMoney = maildata.get(EnumMail.EnumKuaFuMoney)
	if kuafuMoney:
		role.IncKuaFuMoney(kuafuMoney)
	touchpoint = maildata.get(EnumMail.EnumTouchPoint)
	if touchpoint:
		role.IncTouchGoldPoint(touchpoint)

# 角色登录后过30秒查询下是否有新邮件
def SyncRoleOtherData(role, param):
	if Environment.IsCross:
		return
	role.RegTick(30, HasItemsMail, None)

def HasItemsMail(role, callargv, regparam):
	roleid = role.GetRoleID()
	DBProxy.DBRoleVisit(roleid, "HasItemsMail", roleid, OnHasItemsMail, role)

def OnHasItemsMail(result, role):
	if result:
		role.SendObj(Mail_YouHaveNew, None)

if "_HasLoad" not in dir():
	TraUseMail = AutoLog.AutoTransaction("TraUseMail", "接收邮件")
	Mail_YouHaveNew = AutoMessage.AllotMessage("Mail_YouHaveNew", "你有一封新邮件")
	
	Event.RegEvent(Event.Eve_SyncRoleOtherData, SyncRoleOtherData)
	
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mail_SeeAll", "查看所有邮件"), RequestLoadAllMail)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mail_SeeOne", "查看一个邮件详情"), RequestLoadOneMail)
	cRoleMgr.RegDistribute(AutoMessage.AllotMessage("Mail_Uses", "使用一批邮件"), RequestUseMail)
	
