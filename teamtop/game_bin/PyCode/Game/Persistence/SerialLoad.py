#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Persistence.SerialLoad")
#===============================================================================
# 串行载入数据
#===============================================================================
import cProcess
import cComplexServer
from Common.Message import PyMessage
from ComplexServer.Plug.Control import ControlProxy

TYPE_BIG_TABLE = 1
TYPE_PERSISTENCE_DATA = 2

def request_load(ptype, name):
	ControlProxy.SendControlMsg(PyMessage.Control_RequestLoad, (cProcess.ProcessID, ptype, name))

def success_load(ptype, name):
	ControlProxy.SendControlMsg(PyMessage.Control_SuccessLoad, (cProcess.ProcessID, ptype, name))

def on_command_load(sessionid, msg):
	from Game.Persistence import BigTable, Base
	ptype, name = msg
	if ptype == TYPE_BIG_TABLE:
		obj = BigTable.ALL_TABLES[name]
		obj.LoadData(True)
	elif ptype == TYPE_PERSISTENCE_DATA:
		obj = Base.KeyDict[name]
		obj.LoadData(True)

def request_load_big_table(name):
	request_load(TYPE_BIG_TABLE, name)

def request_load_persistence_data(name):
	request_load(TYPE_PERSISTENCE_DATA, name)

def success_load_big_table(name):
	success_load(TYPE_BIG_TABLE, name)

def success_load_persistence_data(name):
	success_load(TYPE_PERSISTENCE_DATA, name)

if "_HasLoad" not in dir():
	cComplexServer.RegDistribute(PyMessage.Control_CommandLoad, on_command_load)
