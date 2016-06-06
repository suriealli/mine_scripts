#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 同步客户端数据
#===============================================================================
import Environment
from django.http import HttpResponse
from ThirdLib import PrintHelp
from Integration.Help import OtherHelp
from Integration.WebPage.User import Permission
from Game.NPC import EnumRNPC






def Reg(request):
	'''
	【测试】--同步服务器常量
	'''
	d = GetSyncData()
	s = PrintHelp.pformat(d, width = 160)
	s = s.replace("\n", "<br>")
	s = s.replace("\t", "&nbsp;&nbsp;")
	s = s.replace(" ", "&nbsp;")
	return HttpResponse(s)

def Reg_Interface(request):
	return HttpResponse(repr(GetSyncData()))

def GetSyncData():
	from Common import Coding
	from Common.Other import EnumAppearance, EnumSocial
	from Common.Message import CMessage, OtherMessage, AutoMessage
	from Common.Other import EnumRoleStatus, EnumSysData, EnumGameConfig, EnumFightStatistics
	from Game.Role.Data import EnumInt64, EnumInt32, EnumInt16, EnumInt8, EnumInt1, EnumCD
	from Game.Role.Data import EnumDayInt1, EnumDayInt8, EnumDynamicInt64, EnumDisperseInt32
	from Game.Role.Data import EnumObj, EnumTempInt64
	from Game.Property import PropertyEnum
	from Game.Role.Obj import EnumOdata
	from Game.Item import EnumPackage
	from Game.Fight import Operate, Fight
	from Game.Team import EnumTeamType
	from Game.NPC import EnumNPCData
	from Game.Role.Mail import EnumMail
	from Game.Activity import CircularDefine
	from Game.SuperCards import EnumSuperCards
	
	d = {}
	msg = []
	msg.extend(OtherHelp.GetModuleDefine(CMessage))
	msg.extend(OtherHelp.GetModuleDefine(OtherMessage))
	
	# 强制读取文件中的消息
	AutoMessage.AutoMsg.clear()
	AutoMessage.Values.clear()
	AutoMessage.LoadMsg()
	
	nameList = AutoMessage.AutoMsg.keys()
	nameList.sort()
	for name in nameList:
		value, zs = AutoMessage.AutoMsg[name]
		msg.append((name, value, zs))
	d["MsgDefine"] = msg
	d["Coding"] = OtherHelp.GetModuleDefine(Coding, tuple)
	d["EnumI64"] = OtherHelp.GetModuleDefine(EnumInt64)
	d["EnumI32"] = OtherHelp.GetModuleDefine(EnumInt32)
	d["EnumI16"] = OtherHelp.GetModuleDefine(EnumInt16)
	d["EnumI8"] = OtherHelp.GetModuleDefine(EnumInt8)
	d["EnumI1"] = OtherHelp.GetModuleDefine(EnumInt1)
	d["EnumDayInt1"] = OtherHelp.GetModuleDefine(EnumDayInt1)
	d["EnumDayInt8"] = OtherHelp.GetModuleDefine(EnumDayInt8)
	d["EnumDynamicInt64"] = OtherHelp.GetModuleDefine(EnumDynamicInt64)
	d["EnumDisperseInt32"] = OtherHelp.GetModuleDefine(EnumDisperseInt32)
	d["EnumObj"] = OtherHelp.GetModuleDefine(EnumObj)
	d["EnumTempInt64"] = OtherHelp.GetModuleDefine(EnumTempInt64)
	d["EnumCD"] = OtherHelp.GetModuleDefine(EnumCD)
	d["EnumOdata"] = OtherHelp.GetModuleDefine(EnumOdata)
	d["EnumPackage"] = OtherHelp.GetModuleDefine(EnumPackage)
	d["PropertyEnum"] = OtherHelp.GetModuleDefine(PropertyEnum)
	d["Fight"] = []
	d["Fight"].extend(OtherHelp.GetModuleDefine(Operate))
	d["Fight"].extend(OtherHelp.GetModuleDefine(Fight))
	d["EnumAppearance"] = OtherHelp.GetModuleDefine(EnumAppearance)
	d["Social"] = OtherHelp.GetModuleDefine(EnumSocial)
	d["EnumRoleStatus"] = OtherHelp.GetModuleDefine(EnumRoleStatus)
	
	d["EnumSysData"] = OtherHelp.GetModuleDefine(EnumSysData)
	d["EnumGameConfig"] = OtherHelp.GetModuleDefine(EnumGameConfig)
	
	d["EnumTeamType"] = OtherHelp.GetModuleDefine(EnumTeamType)

	d["EnumNPCData"] = OtherHelp.GetModuleDefine(EnumNPCData)
	
	d["EnumMail"] = OtherHelp.GetModuleDefine(EnumMail)
	
	d["EnumFightStatistics"] = OtherHelp.GetModuleDefine(EnumFightStatistics)
	
	d["CircularDefine"] = OtherHelp.GetModuleDefine(CircularDefine)
	d["EnumRNPC"] = OtherHelp.GetModuleDefine(EnumRNPC)
	d["EnumSuperCards"] = OtherHelp.GetModuleDefine(EnumSuperCards)
	
	#修改了这个同步客户端常量的，记得修改生成的脚本 BuildAS3.py
	return d


Permission.reg_develop(Reg)
if Environment.IsDevelop:
	Permission.reg_public(Reg_Interface)
else:
	Permission.reg_develop(Reg_Interface)

