#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 显示日志
#===============================================================================
from django.http import HttpResponse
from ComplexServer.Log import AutoLog
from Integration import AutoHTML
from Integration.WebPage.User import Permission
from Integration.Help import ConfigHelp

def MakeAutoTable(kv, title, cnt = 10):
	# 构建表头
	l = len(kv)
	head = []
	body = []
	for head_idx in xrange(cnt):
		if head_idx >= l:
			break
		head.append(kv[head_idx][0])
		head.append(kv[head_idx][1])
	row = []
	for body_idx in xrange(head_idx + 1, l):
		row.append(kv[body_idx][0])
		row.append(kv[body_idx][1])
		if len(row) == 2 * cnt:
			body.append(row)
			row = []
	if row:
		row.extend([None] * (2 * cnt - len(row)))
		body.append(row)
	return AutoHTML.Table(head, body, title).ToHtml()

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>日志信息</title>
</head>
<body>
%s<br>
%s<br>
%s<br>
%s<br>
%s<br>
</body>
</html>'''

def ShowLog(request):
	'''【工具】--日志信息'''
	tra = AutoLog.Transactions.items()
	tra.sort(key=lambda it:it[0])
	eve = AutoLog.Events.items()
	eve.sort(key=lambda it:it[0])
	cod = ConfigHelp.GetCodingName().items()
	cod.sort(key=lambda it:it[0])
	tarots = ConfigHelp.GetTarotNameCashe().items()
	tarots.sort(key=lambda it:it[0])
	talents = ConfigHelp.GetTalentCardCache().items()
	talents.sort(key=lambda it:it[0])
	cnt = 6
	return HttpResponse(html % (MakeAutoTable(tra, "事务", cnt), MakeAutoTable(eve, "事件", cnt), MakeAutoTable(cod, "Obj", cnt), MakeAutoTable(tarots, "命魂", cnt), MakeAutoTable(talents, "天赋卡", cnt)))

Permission.reg_design(ShowLog)
Permission.reg_operate(ShowLog)
