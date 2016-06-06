#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.RunTime.RTCPage")
#===============================================================================
# 运行时关闭功能
#===============================================================================
from django.http import HttpResponse
from Integration import AutoHTML
from Integration.Help import Concurrent, WorldHelp
from Integration.WebPage.User import Permission


DisableDict = { 1 : ("关闭坐骑培养", "Game.Mount.MountMgr", "RequestMountEvolve"),
			2 : ("关闭占卜","Game.Tarot.TarotOperate","OnTarotZhanBu"),
			3 : ("关闭一键占卜","Game.Tarot.TarotOperate","OneKeyZhanBu"),
			4 : ("关闭高级占卜","Game.Tarot.TarotOperate","OnTarotActiveByRMB"),
			5 : ("关闭超级抽取", "Game.Tarot.TarotOperate", "SuperZhanBu"),
			6 : ("关闭英雄升级", "Game.Hero.HeroOperate", "OnUseHeroExpItem"), 
			7 : ("关闭炼金", "Game.Gold.GoldMgr", "RequestGold"), 
			8 : ("关闭10次炼金", "Game.Gold.GoldMgr", "RequestTenGold"), 
			9 : ("关闭公会技能学习", "Game.Union.UnionMagicTower", "RequestLearnUnionSkill"), 
			}


def Req(request):
	'''
	【运行】--禁用函数
	'''
	return HttpResponse(html)

def GetDisableCommand(GET_POST):
	commandIds =  [int(commandId) for commandId in GET_POST.getlist("commandId")]
	disablefun = "DisableFunction('%s', '%s')"
	cmds = []
	print "commandIds", commandIds
	for cid in set(commandIds):
		cmddata = DisableDict.get(cid)
		if not cmddata:
			continue
		cmds.append(disablefun % (cmddata[1], cmddata[2]))
	return cmds

def GetHTML():
	html = []
	for cid, cdata in DisableDict.iteritems():
		html.append("<input type='checkbox' name='commandId' value ='%s' alt = 'A|%s' />%s<br/>" % (cid, cid, cdata[0]))
	return "".join(html)

def Res(request):
	pkeys = AutoHTML.AsProcessKeys(request.POST)
	commands = GetDisableCommand(request.POST)
	tg = Concurrent.TaskGroup()
	for pkey in pkeys:
		print "pkeys", pkeys, commands
		tg.append(Concurrent.GMTask(pkey, "\n".join(commands)))
	tg.execute()
	return HttpResponse(tg.to_html(WorldHelp.GetFullNameByProcessKey, WorldHelp.CmpProcessKey))

html = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>禁用函数</title>
</head>
<body>
<form  action="%s" method="POST" target="_blank">
%s
<br>
%s
<input type="submit" name="提交" />
</form>
</body>
</html>''' % (AutoHTML.GetURL(Res), AutoHTML.ToProcess(), GetHTML())


Permission.reg_develop(Req)
Permission.reg_develop(Res)
Permission.reg_log(Res)
