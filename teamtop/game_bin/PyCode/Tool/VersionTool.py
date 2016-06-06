#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Tool.VersionTool")
#===============================================================================
#  版本工具
#===============================================================================
import os
import sys


reload(sys)
getattr(sys, "setdefaultencoding")("utf8")
path = os.path.dirname(os.path.realpath(__file__))
path = path[:path.find("PyCode") + 6]
if path not in sys.path: sys.path.append(path)
path = path.replace("PyCode", "PyHelp")
if path not in sys.path: sys.path.append(path)


import md5
import time
import traceback
import threading
import subprocess

try:
	import wx
except:
	sys.stderr.write("请先安装wxPython".decode("utf8".encode("gbk")))
	sys.exit(1)

# Win的UTF8的BOM字节
UTF8_BOM = chr(239) + chr(187) + chr(191)

from ComplexServer.Plug.DB import DBHelp

ACCOUNT_SQL = "select account from version_tool;"
LOGIN_SQL = "select password, actype, envs from version_tool where account = %s;"
LOG_SQL = "insert into version_tool_log (account, env, content, log_time)  values (%s, %s, %s, now());"

LoginFrameSize = (600, 400)
MainFrameSize = (1200, 800)

######################################################################################
#正式配置
VersionPath = "F:\\LongQiShi"
BatPath = "F:\\LongQiShi\\trunk\\Tool\\VersionTool"
ConfigPath = "F:\\LongQiShi\\temp"
UploadFilePath = "F:\\LongQiShi"
DevelopPath = "F:\\LongQiShi\\trunk\\Develop"

import Environment
if Environment.IP == "192.168.8.167":
	VersionPath = "E:\\LongQiShi\\Tool\\VersionTool" 		#分支版本管理目录
	BatPath = "E:\\LongQiShi\\Tool\\VersionTool"			#批处理目录
	ConfigPath = "E:\\LongQiShi\\Tool\\VersionTool\\VersionConfig" 	#版本配置目录
	DevelopPath = "E:\\LongQiShi\\Develop" 					#主干目录
	UploadFilePath = "E:\\LongQiShi\\Develop\\Server\\PyCode\\Tool"#上传脚本目录

LogFilePath = ConfigPath + os.sep + 'log.txt'

Versions = {u"腾讯国服" : "qq", 
			u"台湾繁体" : "tw", 
			u"北美" : "na", 
			u"俄罗斯" : "rumsk", 
			u"土耳其" : "tk", 
			u"波兰" : "pl", 
			u"德国" : "de", 
			u"法国" : "fr",
			u"西班牙" : "esp",
			u"英文": "en",
			u"俄罗斯比赛服" : "rutt",
			u"国内联运" : "yy"
			}

OtherVersion = {key:value for value, key in Versions.items()}
######################################################################################



def VersionLog(account, env, content):
	#日志
	con = DBHelp.ConnectHouTaiWeb()
	with con as cur:
		cur.execute(LOG_SQL, (account, OtherVersion.get(env), content))




class ColorTextCtrl(wx.TextCtrl):
	def write(self, *args, **kwargs):
		try:
			return wx.TextCtrl.write(self, *args, **kwargs)
		except wx._core.PyDeadObjectError:
			return "TextCtrl was dead"
		except UnicodeDecodeError:
			print "unknow error", args
			#txt, = args
			#print "++++", type(txt), len(txt)
			#print "unknow error", txt
			#traceback.print_exc()
			#解决不了
			#from ThirdLib import PrintHelp
			#PrintHelp.pprint(args)
			#print "有问题", str(args).decode('GBK').encode('')
		except:
			traceback.print_exc()


class SubProcess(threading.Thread):
	def __init__(self, text_ctrl, cmds, batPath, endmsg, updatefun = None):
		threading.Thread.__init__(self)
		self.text_ctrl = text_ctrl
		self.batPath = batPath
		self.endmsg = endmsg
		self.updatefun = updatefun
		self.process = subprocess.Popen(args = cmds,shell = True,
									stdin = subprocess.PIPE,
									stdout=subprocess.PIPE,
									stderr=subprocess.STDOUT,
									cwd = self.batPath,
									creationflags = subprocess.CREATE_NEW_PROCESS_GROUP)
		
	def run(self):
		try:
			while 1:
				return_code = self.process.poll()
				if return_code is None:
					out = self.process.stdout.readline()
					if out:
						if IS_LOOP is True:
							wx.CallAfter(self.text_ctrl.write, out)
						else:
							break
				else:
					if IS_LOOP is True:
						wx.CallAfter(self.text_ctrl.write, self.endmsg)
						if self in THREADS:
							THREADS.remove(self)
						if self.updatefun:
							self.updatefun()
					break
		except:
			traceback.print_exc()
	
	def stop(self):
		try:
			if self.process.poll() is None:
				self.process.kill()
			self.join(5)
		except:
			traceback.print_exc()
		print "process thread stop"

#登录框
class LoginFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"版本工具登录", pos = wx.DefaultPosition, size = LoginFrameSize, style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		self.accounts = []
		self.LoadData()
		self.InitUI()
	
	def LoadData(self):
		con = DBHelp.ConnectHouTaiWeb()
		with con as cur:
			cur.execute(ACCOUNT_SQL)
			result = cur.fetchall()
			if result:
				for account, in result:
					if account == "1":
						continue
					self.accounts.append(account)
	
	def InitUI(self):
		#禁止拉伸
		self.SetMinSize(LoginFrameSize)
		self.SetMaxSize(LoginFrameSize)
		
		#帐号与布局管理器
		self.accountST = wx.StaticText(self, -1, u"帐号:")
		#self.accountTC = wx.TextCtrl(self, size = (120, 30))
		self.accountTC = wx.ComboBox(self, -1, u"请选择用户名", (120, 30), (120, 30), self.accounts,wx.LB_SINGLE) 
		self.accountTC.Bind(wx.EVT_COMBOBOX, self.OnChoiceAccount)
		self.accountBoxSizer = wx.BoxSizer()
		self.accountBoxSizer.Add(self.accountST, proportion = 0, flag = wx.LEFT | wx.RIGHT, border = 10)
		self.accountBoxSizer.Add(self.accountTC, proportion = 0, flag = wx.LEFT | wx.RIGHT, border = 10)
		
		#密码与布局管理器
		self.passwordST = wx.StaticText(self, -1, u"密码:")
		self.passwordTC = wx.TextCtrl(self, style=wx.TE_PASSWORD, size = (120, 30))
		self.passwordBoxSizer = wx.BoxSizer()
		self.passwordBoxSizer.Add(self.passwordST, proportion = 0, flag = wx.LEFT | wx.RIGHT, border = 10)
		self.passwordBoxSizer.Add(self.passwordTC, proportion = 0, flag = wx.LEFT | wx.RIGHT, border = 10)
		
		#测试数据
#		self.accountTC.SetValue(u"黄伟奇")
#		self.passwordTC.SetValue(u"1qaz2wsx")
		
		#版本选择与布局管理器
		self.versionST = wx.StaticText(self, -1, u"版本:")
		self.versionChoice = wx.ComboBox(self, -1, u" 请选择版本", (120, 30), (120, 30), [], wx.LB_SINGLE) 
		
		self.versionBox = wx.BoxSizer()
		self.versionBox.Add(self.versionST, proportion = 0, flag = wx.LEFT | wx.RIGHT, border = 10)
		self.versionBox.Add(self.versionChoice, proportion = 0, flag = wx.LEFT | wx.RIGHT, border = 10)
		
		#登录按钮
		self.loginbutton = wx.Button(self, label = u"登录")
		self.loginbutton.Bind(wx.EVT_BUTTON, self.OnLogin)
		
		#上下布局管理器
		self.loginBoxSizer = wx.BoxSizer(wx.VERTICAL)
		self.loginBoxSizer.Add(self.accountBoxSizer, proportion = 0, flag = wx.ALIGN_CENTER|wx.TOP, border = 80)
		self.loginBoxSizer.Add(self.passwordBoxSizer, proportion = 0, flag = wx.ALIGN_CENTER | wx.TOP, border = 20)
		self.loginBoxSizer.Add(self.versionBox, proportion = 0, flag = wx.ALIGN_CENTER  | wx.TOP, border = 20)
		self.loginBoxSizer.Add(self.loginbutton, proportion = 0, flag = wx.ALIGN_CENTER  | wx.TOP, border = 30)
		
		
		self.SetSizer(self.loginBoxSizer)
		self.Center()
		#self.Fit()
		#self.SetBackgroundColour("White")
		self.Show()
	
	def OnChoiceAccount(self, event):
		account = self.accountTC.GetValue()
		con = DBHelp.ConnectHouTaiWeb()
		envs = []
		with con as cur:
			cur.execute(LOGIN_SQL, account)
			result = cur.fetchall()
			if not result:
				return
			envs = eval(result[0][2])
		self.versionNames = []
		if "all" in envs:
			self.versionNames = Versions.keys()
		else:
			for env in envs:
				name = OtherVersion.get(env)
				if name:
					self.versionNames.append(name)
		self.versionChoice.SetItems(self.versionNames)
		self.versionChoice.SetValue(self.versionNames[0])
	
	def OnLogin(self, event):
		account = self.accountTC.GetValue()
		password = self.passwordTC.GetValue()
		if not account:
			dlg = wx.MessageDialog(None, u"帐号不能为空", u"提示", wx.YES_NO | wx.ICON_QUESTION)
			dlg.ShowModal()
			return
		if not password:
			dlg = wx.MessageDialog(None, u"密码不能为空", u"提示", wx.YES_NO | wx.ICON_QUESTION)
			dlg.ShowModal()
			return
		
		#检查帐号密码是否正确
		con = DBHelp.ConnectHouTaiWeb()
		with con as cur:
			cur.execute(LOGIN_SQL, account)
			result = cur.fetchall()
			if not result:
				dlg = wx.MessageDialog(None, u"帐号不存在", u"提示", wx.OK | wx.ICON_QUESTION)
				dlg.ShowModal()
				return
			repwd, actype, envs = result[0]
			if repwd != str(md5.new(password).hexdigest()):
				dlg = wx.MessageDialog(None, u"密码错误", u"提示", wx.OK | wx.ICON_QUESTION)
				dlg.ShowModal()
				return
		#检查版本和权限
		envName = self.versionChoice.GetValue()
		env = Versions.get(envName)
		if not env:
			dlg = wx.MessageDialog(None, u"版本错误，请联系开发者", u"提示", wx.OK | wx.ICON_QUESTION)
			dlg.ShowModal()
			return
		if "all" not in envs and env not in envs:
			dlg = wx.MessageDialog(None, u"没有这个版本的权限", u"提示", wx.OK | wx.ICON_QUESTION)
			dlg.ShowModal()
			return
		
		VersionLog(account, env, "Login")
		mf = MainFrame(self)
		mf.ShowEx((account, actype, env, envName))
		self.Hide()
		

class MainFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"版本工具", pos = wx.DefaultPosition, size = MainFrameSize, style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		self.parent = parent
		
		self.InitUI()
		
	def InitUI(self):
		#版本信息
		self.versionDocSizer = wx.StaticBoxSizer(wx.StaticBox(self, label = u"版本信息"), wx.VERTICAL)
		
		self.version = wx.BoxSizer()
		self.versionName = wx.StaticText(self, -1, u"版本")
		self.versionName.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD, True))
		
		self.choiceVersion= wx.Button(self, wx.ID_ANY, u"选择版本")
		self.choiceVersion.Bind(wx.EVT_BUTTON, self.ChoiceVersion)
		
		self.version.Add(self.versionName, 1, wx.LEFT, 1)
		self.version.Add(self.choiceVersion, 0, wx.LEFT, 111)
		
		self.fromSizer = wx.BoxSizer()
		self.versionFrom = wx.StaticText(self, -1, u"当前的父分支 :      ")
		self.setFromTags = wx.Button(self, wx.ID_ANY, u"设置父分支")
		self.setFromTags.Bind(wx.EVT_BUTTON, self.ChangeFromTags)
		
		self.fromSizer.Add(self.versionFrom, 1, wx.LEFT, 1)
		self.fromSizer.Add(self.setFromTags, 0, wx.LEFT, 111)
		
		self.versionProductionTags = wx.StaticText(self, -1, u"外网模拟服分支 :  ")
		self.versionNowTags = wx.StaticText(self, -1, u"更新定位分支 :      ")
		self.versionCheckOutTags = wx.StaticText(self, -1, u"108本地分支 :        ")
		
		self.paramSizer = wx.BoxSizer()
		self.versionParamTxt = wx.StaticText(self, -1, u"分支后缀参数 :        ")
		self.setTagsParam = wx.Button(self, wx.ID_ANY, u"设置参数")
		self.setTagsParam.Bind(wx.EVT_BUTTON, self.SetTagsParam)
		self.paramSizer.Add(self.versionParamTxt, 1, wx.LEFT, 1)
		self.paramSizer.Add(self.setTagsParam, 0, wx.LEFT, 180)
		
		#字体
		vf = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD)
		self.versionFrom.SetFont(vf)
		self.versionProductionTags.SetFont(vf)
		self.versionNowTags.SetFont(vf)
		self.versionCheckOutTags.SetFont(vf)
		self.versionParamTxt.SetFont(vf)
		
		
		self.versionDocSizer.Add(self.version, 1, wx.TOP , 5)
		self.versionDocSizer.Add(self.fromSizer, 1, wx.TOP , 5)
		self.versionDocSizer.Add(self.versionNowTags, 1, wx.TOP , 5)
		self.versionDocSizer.Add(self.versionCheckOutTags, 1, wx.TOP , 5 )
		self.versionDocSizer.Add(self.versionProductionTags, 1, wx.TOP , 5)
		self.versionDocSizer.Add(self.paramSizer, 1, wx.TOP , 5)
		
		#版本管理选项
		self.versionSizer = wx.StaticBoxSizer(wx.StaticBox(self, label = u"版本管理"), wx.VERTICAL)
		#创建分支按钮
		self.createTags = wx.Button(self, wx.ID_ANY, u"创建分支")
		self.createTags.Bind(wx.EVT_BUTTON, self.CreateNewTags)
		#拷贝分支
		self.switchTags = wx.Button(self, wx.ID_ANY, u"拷贝分支")
		self.switchTags.Bind(wx.EVT_BUTTON, self.SwitchTags)
		
		
		
		
		self.updateButton = wx.Button(self, wx.ID_ANY, u"刷新面板数据")
		self.updateButton.Bind(wx.EVT_BUTTON, self.UpdateConfig)
		
		self.versionSizer.Add(self.createTags,  0, wx.EXPAND |wx.ALL, 10 )
		self.versionSizer.Add(self.switchTags,  0, wx.EXPAND |wx.ALL, 10 )
		#self.versionSizer.Add(self.setFromTags,  0, wx.EXPAND |wx.ALL, 10 )
		#self.versionSizer.Add(self.setTagsParam,  0, wx.EXPAND |wx.ALL, 10 )
		self.versionSizer.Add(self.updateButton,  0, wx.EXPAND |wx.ALL, 10 )
		
		
		#更新管理
		self.versionUpdateSizer = wx.StaticBoxSizer(wx.StaticBox(self, label = u"版本更新管理"), wx.VERTICAL)
		self.newProductionTags = wx.Button(self, wx.ID_ANY, u"导出一个新的分支到模拟服")
		self.newProductionTags.Bind(wx.EVT_BUTTON, self.ExportTagsToGS)
		self.updateProductionTags = wx.Button(self, wx.ID_ANY, u"更新模拟服分支内容")
		self.updateProductionTags.Bind(wx.EVT_BUTTON, self.UpdateGSTags)
		self.updateProductionWeb = wx.Button(self, wx.ID_ANY, u"更新模拟服的后台")
		self.updateProductionWeb.Bind(wx.EVT_BUTTON, self.UpdateGSWeb)
		
		self.versionUpdateSizer.Add(self.newProductionTags, 0, wx.EXPAND |wx.ALL, 10)
		self.versionUpdateSizer.Add(self.updateProductionTags, 0, wx.EXPAND |wx.ALL, 10)
		self.versionUpdateSizer.Add(self.updateProductionWeb, 0, wx.EXPAND |wx.ALL, 10)
		
		#客户端更新管理
		self.clientUpdateSizer = wx.StaticBoxSizer(wx.StaticBox(self, label = u"客户端更新管理"), wx.VERTICAL)
		self.clientUpdateBigVersion = wx.Button(self, wx.ID_ANY, u"更新大版本号")
		self.clientUpdateSmallVersion = wx.Button(self, wx.ID_ANY, u"更新小版本号")
		self.clientUpdateSizer.Add(self.clientUpdateBigVersion, 0, wx.EXPAND |wx.ALL, 10)
		self.clientUpdateSizer.Add(self.clientUpdateSmallVersion, 0, wx.EXPAND |wx.ALL, 10)
		
		
		CSizer = wx.BoxSizer(wx.VERTICAL)
		self.controlsizer = wx.BoxSizer()
		
		self.controlsizer.Add(self.versionSizer, flag = wx.EXPAND | wx.ALL, border = 10)
		self.controlsizer.Add(self.versionUpdateSizer, flag = wx.EXPAND | wx.ALL, border = 10)
		self.controlsizer.Add(self.clientUpdateSizer, flag = wx.EXPAND | wx.ALL, border = 10)
		
		self.controlTxt = ColorTextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)
		self.controlTxt.SetBackgroundColour( wx.Colour( 208, 208, 208 ) )
		
		
		CSizer.Add(self.versionDocSizer,1, flag = wx.EXPAND | wx.ALL, border = 10)
		CSizer.Add(self.controlsizer,1, flag = wx.EXPAND | wx.ALL, border = 10)
		
		AllSizer = wx.BoxSizer()
		AllSizer.Add(CSizer, 1, flag = wx.EXPAND | wx.ALL, border = 10)
		AllSizer.Add(self.controlTxt, 1, flag = wx.EXPAND | wx.ALL, border = 10)
		self.SetSizer(AllSizer)
		self.Center()
		self.SetMinSize(MainFrameSize)
		self.SetMaxSize(MainFrameSize)
	
	def ShowEx(self,logininfo):
		self.logininfo = logininfo
		self.account, self.actype, self.env, self.envName = logininfo
		#设置版本名字
		self.versionName.SetLabel(self.envName)
		#父版本
		self.branchFile = ConfigPath + os.sep + self.env + "_from_branch.txt"
		#当前108的check的分支目录版本
		self.lasttagFile = ConfigPath + os.sep + self.env + "_last_version.txt"
		#最新的分支版本，必须尽量对应模拟服的GS版本，而模拟服的GS也必须尽量对应外网正式服的版本
		self.nowtagFile = ConfigPath + os.sep + self.env + "_now_version.txt"
		#GStag,模拟服的分支版本
		self.gstagFile = ConfigPath + os.sep + self.env + "_gs_version.txt"
		#分支后缀
		self.tagparamFile = ConfigPath + os.sep + self.env + "_param.txt"
		self.UpdateConfig()
		self.Show()
		
		sys.stdout = self.controlTxt
		sys.stderr = self.controlTxt
	
	def UpdateConfig(self, evnet = None):
		# 读取版本配置
		with open(self.branchFile, "r") as f:
			self.branchVersion = self.onlystring(f.read())
		with open(self.lasttagFile, "r") as f:
			self.lastVersion = self.onlystring(f.read())
		with open(self.nowtagFile, "r") as f:
			self.nowVersion = self.onlystring(f.read())
		with open(self.gstagFile, "r") as f:
			self.gsVersion = self.onlystring(f.read())
		with open(self.tagparamFile, "r") as f:
			self.versionParam = self.onlystring(f.read())
		
		self.versionFrom.SetLabel(u"当前的父分支 :      " + self.branchVersion)
		self.versionCheckOutTags.SetLabel(u"108本地分支 :        " + self.lastVersion)
		self.versionNowTags.SetLabel(u"更新定位分支 :      " + self.nowVersion)
		self.versionProductionTags.SetLabel(u"外网模拟服分支 :  " + self.gsVersion)
		self.versionParamTxt.SetLabel(u"分支后缀参数 :        " + self.versionParam)
	
	def onlystring(self, s):
		if s.startswith(UTF8_BOM):
			s = s[3:]
		return s.replace(' ','').replace('\r\n','').replace('\n','')
	
		
	def CreateNewTags(self, event):
		#二次确认
		dlg = wx.MessageDialog(None, u"是否要创建一个新的分支？", u"提示", wx.YES_NO | wx.ICON_QUESTION)
		if (dlg.ShowModal() == wx.ID_YES):
			print "\n====================CreateNewTags========================"
			nowtime = time.strftime('%Y.%m.%d')[2:]
			newtagsName = self.env + "." + nowtime + "." + self.versionParam
			#日志
			VersionLog(self.account, self.env, "CreateTags %s" % newtagsName)
			#创建分支
			cmd = "CALL CreateVersion.bat %s %s %s %s" % (self.env, self.versionParam, newtagsName, ConfigPath)
			sub_thread = SubProcess(self.controlTxt, cmd, BatPath, "====================FinishCreate========================", self.UpdateConfig)
			sub_thread.start()
			THREADS.append(sub_thread)
			self.UpdateConfig()
		dlg.Destroy()
		
	
	def SwitchTags(self, event):
		#二次确认是否要switch，确认是否在最近一天内就会从模拟服更新到正式服，否则不能操作
		dlg = wx.MessageDialog(None, u"  确认要拷贝分支？请尽量保证当前分支和外网分支的一致性.\n拷贝后请尽快上传到模拟服，并且在短时间内同步正式服", u"提示", wx.YES_NO | wx.ICON_WARNING)
		if (dlg.ShowModal() == wx.ID_YES):
			
			oldname = VersionPath + os.sep + self.lastVersion
			newname = VersionPath + os.sep + self.nowVersion
			if oldname.find('\n') != -1:
				oldname = oldname[:oldname.find('\n')]
			if newname.find('\n') != -1:
				newname = newname[:newname.find('\n')]
			
			if oldname == newname:
				return
			try:
				#检查是否可以修改名字
				os.rename(oldname, newname)
			except:
				dlg = wx.MessageDialog(None, u"%s无法重命名为%s，中断操作" % (oldname, newname), u"提示", wx.OK | wx.ICON_WARNING)
				dlg.ShowModal()
				traceback.print_exc()
				return
			#修改回去
			os.rename(newname, oldname)
			#switch 到本地分支
			#日志
			VersionLog(self.account, self.env, "SwitchTags old(%s), new(%s)" % (self.lastVersion, self.nowVersion))
			print "\n=========开始进行拷贝，请检查控制台=============="
			cmd = " cd %s && CALL SwitchVersion.bat %s %s %s" % (BatPath, self.env, ConfigPath, VersionPath)
			os.system(cmd)
			#因为拷贝的时候需要操作控制台进行冲突处理，所以不做重定向
			#sub_thread = SubProcess(self.controlTxt, cmd, BatPath, "====================FinishSwitch========================", self.UpdateConfig)
			#sub_thread.start()
			#THREADS.append(sub_thread)
			self.UpdateConfig()
		dlg.Destroy()

	def ExportTagsToGS(self, event):
		#二次确认是否要导出，确认是否在最近一天内就会从模拟服更新到正式服，否则不能操作
		dlg = wx.MessageDialog(None, u"  是否导出到模拟服？ 内网已经测试通过，并且会在短时间内同步到正式服？ \n 导出后，正式服和模拟服的版本会不一致，要修正正式服的问题需要其他复杂的操作才行", u"提示", wx.YES_NO | wx.ICON_WARNING)
		if (dlg.ShowModal() == wx.ID_YES):
			#向模拟服导出 self.versionNowTags 这个分支
			VersionLog(self.account, self.env, "ExportTags %s " % self.nowVersion)
			print "\n====================StartExportGS========================"
			cmd = "CALL ExportServer.bat %s %s %s %s %s" % (self.env, ConfigPath, VersionPath, UploadFilePath, LogFilePath)
			sub_thread = SubProcess(self.controlTxt, cmd, BatPath, "====================FinishExportGS========================", self.UpdateConfig)
			sub_thread.start()
			THREADS.append(sub_thread)
			self.UpdateConfig()
		dlg.Destroy()
	
	def UpdateGSTags(self, event):
		if self.gsVersion != self.nowVersion:
			dlg = wx.MessageDialog(None, u"当前版本和模拟服版本不一致，不能更新", u"提示", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			return
		#判断模拟服版本是否和当前的checkout版本一致，如果不一致，有可能会出现非预料中的更新
		dlg = wx.MessageDialog(None, u"  是否要更新到模拟服？需要本地测试通过才可以更新", u"提示", wx.YES_NO | wx.ICON_WARNING)
		if (dlg.ShowModal() == wx.ID_YES):
			#向模拟服导出 self.versionNowTags 这个分支
			VersionLog(self.account, self.env, "UpdateGSTags %s " % self.nowVersion)
			print "\n====================UpdateGSTags========================"
			cmd = "CALL UpdateServer.bat %s %s %s %s %s" % (self.env, ConfigPath, VersionPath, UploadFilePath, LogFilePath)
			sub_thread = SubProcess(self.controlTxt, cmd, BatPath, "====================FinishUpdateGSTags========================", self.UpdateConfig)
			sub_thread.start()
			THREADS.append(sub_thread)
		dlg.Destroy()
	
	def UpdateGSWeb(self, event):
		#同步的是主干，更新的是外网的简易后台，如果要更新外网的全局后台，需要先融合到本地的分支，更新到模拟服的GS，再同步才行
		#二次确认，更新前确认内网后台可以正常使用
		dlg = wx.MessageDialog(None, u"  更新前请确认内网简易后台无异常，并且功能全部正常", u"提示", wx.YES_NO | wx.ICON_WARNING)
		if (dlg.ShowModal() == wx.ID_YES):
			print "\n====================StartUpdateGSWeb========================"
			VersionLog(self.account, self.env, "UpdateGSWeb")
			cmd = "CALL ExportWeb.bat %s %s %s %s %s" % (self.env, ConfigPath, DevelopPath, UploadFilePath, LogFilePath)
			sub_thread = SubProcess(self.controlTxt, cmd, BatPath, "====================FinishUpdateGSWeb========================", self.UpdateConfig)
			sub_thread.start()
			THREADS.append(sub_thread)
		dlg.Destroy()
	
	def ChoiceVersion(self, event):
		#获取能够选择的版本
		dlg = wx.SingleChoiceDialog(None, u"请选择要切换的版本:", u"版本切换", self.parent.versionNames)
		if dlg.ShowModal() == wx.ID_OK:
			#选择的版本
			message = dlg.GetStringSelection()
			dlg_tip = wx.MessageDialog(None, u"是否确认切换到  【" + message + u"】", u"版本切换确认", wx.YES_NO | wx.ICON_INFORMATION)
			if dlg_tip.ShowModal() == wx.ID_YES:
				#确认后切换版本
				env = Versions.get(message)
				if env:
					self.ShowEx((self.account, self.actype, env, message))
					print u'\n%s ---> 切换到版本 ---> %s\n' % (self.envName, message)
				else:
					self.Close(True)
				dlg_tip.Destroy()
		dlg.Destroy()
	
	def ChangeFromTags(self, event):
		pass
	
	def SetTagsParam(self, event):
		pass
	
	
	def ClientBigVersion(self, event):
		pass
	
	def ClientLittleVersion(self, event):
		pass

	

if __name__ == "__main__":
	out = sys.stdout
	err = sys.stderr
	IS_LOOP = False
	THREADS = []
	try:
		app = wx.App(redirect = False)
		win = LoginFrame(None)
		win.Center()
		IS_LOOP  = True
		app.MainLoop()
		IS_LOOP  = False
		for my_thread in THREADS:
			my_thread.stop()
	except:
		IS_LOOP  = False
		sys.stdout = out
		sys.stderr = err
		traceback.print_exc()
	IS_LOOP  = False
	sys.stdout = out
	sys.stderr = err

