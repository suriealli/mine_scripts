#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.DataBase.RoleMail")
#===============================================================================
# 角色邮件
#===============================================================================
from Integration.Help import OtherHelp
from Integration.WebPage.User import Permission
from Integration import AutoHTML
from ComplexServer.Plug.DB import DBHelp


def SendRoleMail(request):
	return OtherHelp.Apply(_SendRoleMail, request, __name__)

def _SendRoleMail(request):
	maildatas = AutoHTML.AsString(request.POST, "maildatas")
	maildatas = eval(maildatas)
	cnt = 0
	for md in maildatas:
		roleid, title, sender, content, mail_transaction, maildata = md
		cnt += DBHelp.SendRoleMail(roleid, title, sender, content, mail_transaction, maildata)
	return cnt

Permission.reg_public(SendRoleMail)