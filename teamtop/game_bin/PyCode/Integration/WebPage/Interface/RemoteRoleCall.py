#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Interface.RemoteRoleCall")
#===============================================================================
# 角色远程调用离线命令
#===============================================================================
from ComplexServer.Plug.DB import DBHelp
from Integration import AutoHTML
from Integration.Help import OtherHelp
from Integration.WebPage.User import Permission

def RemoteRoleCall(request):
	return OtherHelp.Apply(_RemoteRoleCall, request, __name__)
	
def _RemoteRoleCall(request):
	roleid = AutoHTML.AsInt(request.GET, "roleid")
	command = AutoHTML.AsString(request.GET, "command")
	return DBHelp.SendRoleCommend(roleid, command)

Permission.reg_public(RemoteRoleCall)