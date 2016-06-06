#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.QQidip.QQidip")
#===============================================================================
# idip统一url
#===============================================================================
import time
import json
import datetime
import traceback
import Environment
import DynamicPath
from django.http import HttpResponse
from Integration.WebPage.QQidip import QQRoleList, QQRoleInfo, QQRoleMail,\
	QQOnline, QQEvent, QQRoleConsume, QQRank, QQSystemRank, QQOpenID, QQActiveGrade


IDIP_DICT = {4097 : (4098, QQRoleList.RoleList),
			4099 : (4100, QQRoleInfo.RoleInfo),
			4101 : (4102, QQRoleMail.Mail),
			4103 : (4104, QQOnline.Online),
			4105 : (4106, QQEvent.Event),
			4107 : (4108, QQRoleConsume.RoleConsume),
			4109 : (4110, QQRank.Rank ),
			4111 : (4112, QQSystemRank.SystemRank),
			4113 : (4114, QQOpenID.OpenID),
			4115 : (4116, QQActiveGrade.ActiveGrade),
			}

#result = 0 /* 错误码,返回码类型：0：处理成功，需要解开包体获得详细信息,
#1：处理成功，但包体返回为空，不需要处理包体（eg：查询用户角色，用户角色不存在等），
#-1: 网络通信异常,
#-2：超时,
#-3：数据库操作异常,
#-4：API返回异常,
#-5：服务器忙,
#-6：其他错误,
#小于-100 ：用户自定义错误，需要填写szRetErrMsg *

#-1007 : area error
#-1008 : itemid error
#-1009 : openid error
#-1010 : roleid error
#-1011 : event error 
#-1012 : type error

class QQRequest(object):
	def __init__(self, request):
		self.request = request
		self.Unpack()
	
	def Unpack(self):
		data_packet = self.request.POST.get('data_packet')
		if not data_packet:
			print "GE_EXC, QQRequest Unpack error"
			assert False
		null = None
		null#eval 里面需要用到这个
		
		data_packet = eval(data_packet)
		self.head = data_packet.get('head')
		self.body = data_packet.get('body')
		
		self.cmdid = self.head.get('Cmdid')
		if not self.cmdid:
			assert False
		cmddata = IDIP_DICT.get(self.cmdid)
		if not cmddata:
			assert False
		self.resCmdid, self.reqfun = cmddata
	
	def DoCmd(self):
		return self.reqfun(self)
	
	def GetBody(self):
		return self.body
	
	def BodyGet(self, key):
		return self.body.get(key)
	
	def GetInt(self, key):
		s = self.body.get(key)
		if s:
			return int(s)
		else:
			return 0
	
	def GetString(self, key):
		return self.body.get(key)
	
	def response(self, body, result = 0, errormsg = ''):
		self.head['Result'] = result
		self.head['SendTime'] = int(time.strftime('%Y%m%d'))
		self.head['RetErrMsg'] = errormsg
		self.head['Cmdid'] = self.resCmdid
		return json.dumps({'head':self.head, 'body':body})
	
	def ErrorResponse(self, result, errormsg = ''):
		self.head['Result'] = result
		self.head['SendTime'] = int(time.strftime('%Y%m%d'))
		self.head['RetErrMsg'] = errormsg
		self.head['Cmdid'] = self.resCmdid
		return json.dumps({'head':self.head, 'body':{}})


#{u'data_packet': [u'{ "head" : { "PacketLen" : null , "Cmdid" : 4103 , "Seqid" : 1 , "ServiceName" : "OP_LQSZ" , "SendTime" : 20141027 , "Version" : 5 , "Authenticate" : "" , "Result" : 0 , "RetErrMsg" : "" }, "body" : { "AreaId" : null } }']}

# "Result" : 错误码,返回码类型：
#0：处理成功，需要解开包体获得详细信息,
#1：处理成功，但包体返回为空，不需要处理包体（eg：查询用户角色，用户角色不存在等），
#-1: 网络通信异常,
#-2：超时,
#-3：数据库操作异常,
#-4：API返回异常,
#-5：服务器忙,
#-6：其他错误,
#小于-100 ：用户自定义错误，需要填写szRetErrMsg


def Apply(request, file_name = "QQidip"):
	try:
		qqrequest = QQRequest(request)
		response = qqrequest.DoCmd()
		#返回的是json串
		if not isinstance(response, str):
			response = HttpResponse(qqrequest.ErrorResponse(-4, str(response)))
		return HttpResponse(response)
	except:
		if Environment.IsWindows:
			raise
		else:
			with open(DynamicPath.DynamicFolder(DynamicPath.FilePath).FilePath(file_name), "a") as f:
				f.write(str(datetime.datetime.now()))
				f.write("\n")
				traceback.print_exc(None, f)
			return HttpResponse(qqrequest.ErrorResponse(-6, "request error"))



