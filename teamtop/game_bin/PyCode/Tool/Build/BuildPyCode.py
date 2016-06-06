#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 根据C++代码构建Python代码
#===============================================================================
from Util.C import CParseBuild
from Util.PY import PyParseBuild

def MessageBuild():
	cf1 = CParseBuild.CFile("GameEngine\\GENetDefine.h")
	cf2 = CParseBuild.CFile("ComplexServer\\MessageDefine.h")
	pf = PyParseBuild.PyFile("Common.Message.CMessage")
	
	msglist = []
	msglist.extend(cf1.GetEnumerate("GEMsgType"))
	msglist.extend(cf2.GetEnumerate("ProcessMsgType"))
	pf.ReplaceCEnumerate("C中消息定义", msglist, "MsgBegin", "MsgEnd")
	pf.Write()

def WhoBuild():
	cf = CParseBuild.CFile("ComplexServer\\ClutterDefine.h")
	pf = PyParseBuild.PyFile("Common.Connect.Who")
	pf.ReplaceCEnumerate("连接类型定义", cf.GetEnumerate("EndPointType"), "WhoBegin", "WhoEnd")
	pf.Write()

def RoleActionBuild():
	cf = CParseBuild.CFile("ComplexServer\\RoleDataMgr.h")
	pf = PyParseBuild.PyFile("Game.Role.Data.Enum")
	pf.ReplaceCEnumerate("角色数值超出范围处理", cf.GetEnumerate("RoleAction"), "ActionBegin", "ActionEnd")
	pf.Write()
	
	
if __name__ == "__main__":
	MessageBuild()
	WhoBuild()
	RoleActionBuild()



