#!/usr/bin/env python
# -*- coding:UTF-8 -*-
import traceback

def getTransaction(msg=None):
	data={}
	if not msg:msg={}
	from ComplexServer.Log import AutoLog
	for value,zs in AutoLog.Transactions.items():
		data[int(value)]={"value":zs,"key":value,"desc":zs}
	return data