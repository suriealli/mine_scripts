#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.Global.GlobalData")
#===============================================================================
# 全局数据
#===============================================================================
from Integration.Help import OtherHelp
from Integration.WebPage.User import Permission
from Integration import AutoHTML
from ComplexServer.Plug.DB import DBHelp
from World import Define


def GetGlobalData(request):
	return OtherHelp.Apply(_GetGlobalData, request, __name__)

def _GetGlobalData(request):
	global_data_key = AutoHTML.AsString(request.GET, "key")
	process_id = AutoHTML.AsInt(request.GET, "pid")
	if process_id in Define.TestWorldIDs:
		#测试服，特殊处理key
		global_data_key = global_data_key + "_testworld"
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select data from global_data where global_data_key = '%s';" % global_data_key)
		result = cur.fetchall()
		if result:
			value = result[0][0]
		else:
			value = 0
	con.close()
	return value


def GetGlobalData_ByKeys(request):
	return OtherHelp.Apply(_GetGlobalData_ByKeys, request, __name__)

def _GetGlobalData_ByKeys(request):
	keys = AutoHTML.AsString(request.GET, "keys")
	keys = eval(keys)
	process_id = AutoHTML.AsInt(request.GET, "pid")
	backData = {}
	con = DBHelp.ConnectGlobalWeb()
	if process_id in Define.TestWorldIDs:
		#测试服，特殊处理key
		with con as cur:
			for gk in keys:
				global_data_key = str(gk) + "_testworld"
				cur.execute("select data from global_data where global_data_key = '%s';" % global_data_key)
				result = cur.fetchall()
				if result:
					value = result[0][0]
				else:
					value = 0
				backData[gk] = value
		con.close()
	else:
		with con as cur:
			for global_data_key in keys:
				cur.execute("select data from global_data where global_data_key = '%s';" % global_data_key)
				result = cur.fetchall()
				if result:
					value = result[0][0]
				else:
					value = 0
				backData[global_data_key] = value
		con.close()
	return backData


def SetGlobalData(request):
	return OtherHelp.Apply(_SetGlobalData, request, __name__)
	
	
def _SetGlobalData(request):
	global_data_key = AutoHTML.AsString(request.POST, "key")
	global_data = AutoHTML.AsString(request.POST, "value")
	process_id = AutoHTML.AsInt(request.POST, "pid")
	if process_id in Define.TestWorldIDs:
		#测试服，特殊处理key
		global_data_key = global_data_key + "_testworld"
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		h = cur.execute("replace into global_data (global_data_key, data, save_datetime) values(%s, %s, now());", (global_data_key, global_data))
	con.close()
	return h


def SetGlobalDataByDict(request):
	return OtherHelp.Apply(_SetGlobalDataByDict, request, __name__)
	
	
def _SetGlobalDataByDict(request):
	datadict = AutoHTML.AsString(request.POST, "datadict")
	datadict = eval(datadict)
	process_id = AutoHTML.AsInt(request.POST, "pid")
	global_data_Dict = {}
	if process_id in Define.TestWorldIDs:
		#测试服，特殊处理key
		for gkey, gvalue in datadict.iteritems():
			gkey = str(gkey) + "_testworld"
			global_data_Dict[gkey] = gvalue
	else:
		global_data_Dict = datadict
		
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		for gkey, gvalue in global_data_Dict.iteritems():
			h = cur.execute("replace into global_data (global_data_key, data, save_datetime) values(%s, %s, now());", (gkey, gvalue))
	con.close()
	return h



def IncGlobalData(request):
	return OtherHelp.Apply(_IncGlobalData, request, __name__)


def _IncGlobalData(request):
	global_data_key = AutoHTML.AsString(request.GET, "key")
	incValue = AutoHTML.AsInt(request.GET, "value")
	process_id = AutoHTML.AsInt(request.GET, "pid")
	if process_id in Define.TestWorldIDs:
		#测试服，特殊处理key
		global_data_key = global_data_key + "_testworld"
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select data from global_data where global_data_key = '%s';" % global_data_key)
		result = cur.fetchall()
		value = 0
		if result:
			value = result[0][0]
		
		value = int(value) + incValue
		h = cur.execute("replace into global_data (global_data_key, data, save_datetime) values(%s, %s, now());", (global_data_key, value))
	con.close()
	return h

def DecGlobalData(request):
	return OtherHelp.Apply(_DecGlobalData, request, __name__)


def _DecGlobalData(request):
	global_data_key = AutoHTML.AsString(request.GET, "key")
	incValue = AutoHTML.AsInt(request.GET, "value")
	process_id = AutoHTML.AsInt(request.GET, "pid")
	if process_id in Define.TestWorldIDs:
		#测试服，特殊处理key
		global_data_key = global_data_key + "_testworld"
	con = DBHelp.ConnectGlobalWeb()
	with con as cur:
		cur.execute("select data from global_data where global_data_key = '%s';" % global_data_key)
		result = cur.fetchall()
		value = 0
		if result:
			value = result[0][0]
		value = int(value) - incValue
		h = cur.execute("replace into global_data (global_data_key, data, save_datetime) values(%s, %s, now());", (global_data_key, value))
	con.close()
	return h


Permission.reg_public(GetGlobalData)
Permission.reg_public(SetGlobalData)
Permission.reg_public(GetGlobalData_ByKeys)
Permission.reg_public(SetGlobalDataByDict)
Permission.reg_public(IncGlobalData)
Permission.reg_public(DecGlobalData)

