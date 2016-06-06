#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 服务器
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

import socket
import thread
import exceptions
import contextlib
import threading
import subprocess
import traceback
try:
	import wx
except:
	sys.stderr.write("请先安装wxPython".decode("utf8".encode("gbk")))
	sys.exit(1)
import DynamicPath

ConfigFilePath = DynamicPath.FilePath + "ServerToolConfig.txt"
GMFilePath = DynamicPath.FilePath + "ServerToolGM.txt"

def GetSVNUrl():
	pfile = os.popen("svn info %s" % __file__)
	urllist = pfile.read().split('\n')
	url = urllist[3]
	if "trunk" in url:
		return url[:url.find("trunk") + 6]
	else:
		return url[:url.find("Server")]
def IsTrunk(url):
	return"/svn/LongQiShi/trunk/" in url



class PolicyServer(threading.Thread):
	def __init__(self, port, path):
		threading.Thread.__init__(self)
		self.is_run = True
		self.port = port
		self.policy = self.read_policy(path)
		self.log_path = DynamicPath.FilePath + "843.log"
		# 清空数据
		with open(self.log_path, "w"):
			pass
		# 监听端口
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('', self.port))
		self.sock.listen(20)
		print "listen %s ok." % self.port
	
	def read_policy(self, path):
		with file(path, 'rb') as f:
			policy = f.read(10001)
			if len(policy) > 10000:
				raise exceptions.RuntimeError('File probably too large to be a policy file',
											  path)
			if 'cross-domain-policy' not in policy:
				raise exceptions.RuntimeError('Not a valid policy file',
											  path)
			return policy
	
	def run(self):
		try:
			while self.is_run:
				thread.start_new_thread(self.handle, self.sock.accept())
		except socket.error, e:
			self.log('Error accepting connection: %s' % (e[1],))
	
	def stop(self):
		self.is_run = False
		try:
			self.sock.close()
			try:
				# 这里要自连接下才能出发windows下accept函数从阻塞中返回
				so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				so.connect(("127.0.0.1", self.port))
			except:
				traceback.print_exc()
			self.join(5)
		except:
			traceback.print_exc()
	
	def handle(self, conn, addr):
		addrstr = '%s:%s' % (addr[0],addr[1])
		try:
			self.log('Connection from %s' % (addrstr,))
			with contextlib.closing(conn):
				# It's possible that we won't get the entire request in
				# a single recv, but very unlikely.
				request = conn.recv(1024).strip()
				if request != '<policy-file-request/>\0':
					self.log('Unrecognized request from %s: %s' % (addrstr, request))
					return
				self.log('Valid request received from %s' % (addrstr,))
				conn.sendall(self.policy)
				self.log('Sent policy file to %s' % (addrstr,))
		except socket.error, e:
			self.log('Error handling connection from %s: %s' % (addrstr, e[1]))
		except Exception, e:
			self.log('Error handling connection from %s: %s' % (addrstr, e[1]))
	
	def log(self, s):
		with open(self.log_path, "a") as f: 
			print >>f, s

class SubProcess(threading.Thread):
	def __init__(self, text_ctrl, cmds, binPath):
		threading.Thread.__init__(self)
		self.text_ctrl = text_ctrl
		self.binPath = binPath[:binPath.find("ComplexServer.exe")]
		self.process = subprocess.Popen(args = cmds,
									stdin = subprocess.PIPE,
									stdout=subprocess.PIPE,
									stderr=subprocess.STDOUT,
									cwd = self.binPath,
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
						wx.CallAfter(self.text_ctrl.write, u"当前进程意外关闭，返回：%s" % return_code)
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

class ColorTextCtrl(wx.TextCtrl):
	def write(self, *args, **kwargs):
		try:
			line = args[0]
			if line.find("GE_EXC") >= 0:
				self.SetDefaultStyle(wx.TextAttr("YELLOW"))
			elif line.startswith("RED"):
				self.SetDefaultStyle(wx.TextAttr("RED"))
			elif line.startswith("BLUE"):
				self.SetDefaultStyle(wx.TextAttr("BLUE"))
			elif line.startswith("GREEN"):
				self.SetDefaultStyle(wx.TextAttr("GREEN"))
			else:
				self.SetDefaultStyle(wx.TextAttr("BLACK"))
			return wx.TextCtrl.write(self, *args, **kwargs)
		except wx._core.PyDeadObjectError:
			return "TextCtrl was dead"
		except UnicodeDecodeError:
			print args, kwargs
			return "Code error"

class ProcessPanel(wx.Panel):
	processInfo = None
	def SetProcessInfo(self, info):
		#exe, ptype, str(pid), str(port)
		self.processInfo = info
		self.ptype = info[1]
		self.processId = int(info[2])
		self.port = int(info[3])
		self.gm = None
	
	def IsGUI(self):
		return self.processInfo is None
	
	def SendCommand(self, command):
		if self.gm is None:
			self.InitGMConnect()
		self.gm.gmcommand(str(command))

	def InitGMConnect(self):
		from Tool.GM import GMCMD
		self.gm = GMCMD.GMConnect("127.0.0.1", self.port, "G" in self.ptype)
		self.gm.iamgm()
	
	def SendCommand_C_GHL(self, command, ptypes = "C, GHL"):
		#一般只有控制进程和逻辑进程有批量发送指令的需求(ToTime)
		if self.ptype not in ptypes:
			return
		self.SendCommand(command)


class ServerBox(wx.StaticBoxSizer):
	def BindServerInfo(self, frame, serverInfos, isControl):
		self.processThreadDict = {}
		self.frame = frame
		self.serverinfos = serverInfos
		self.binPath = DynamicPath.BinPath + "ComplexServer.exe"
		self.isGMSelect = False
		self.isControl = isControl
		self.AnalysisServer()
	
		self.restart = wx.Button( frame, wx.ID_ANY, u"启动" )
		self.close = wx.Button(frame, wx.ID_ANY, u"关闭")
		self.reloadall = wx.Button(frame, wx.ID_ANY, u"重载所有脚本")
		self.gmselect = wx.Button( frame, wx.ID_ANY, u"执行所有指令" )
		self.cleardb = wx.Button( frame, wx.ID_ANY, u"清档")
		
		self.restart.Bind(wx.EVT_BUTTON, self.Restart)
		self.close.Bind(wx.EVT_BUTTON, self.Close)
		self.reloadall.Bind(wx.EVT_BUTTON, self.ReloadAll)
		self.gmselect.Bind(wx.EVT_BUTTON, self.GMSelect)
		self.cleardb.Bind(wx.EVT_BUTTON, self.ClearDB)
		
		self.Add( self.restart, 0, wx.EXPAND |wx.ALL , 2 )
		self.Add( self.close, 0, wx.EXPAND |wx.ALL , 2 )
		self.Add( self.reloadall, 0, wx.EXPAND |wx.ALL , 2 )
		self.Add( self.gmselect, 0, wx.EXPAND |wx.ALL , 2 )
		self.Add( self.cleardb, 0, wx.EXPAND |wx.ALL , 2 )
		
	def AnalysisServer(self):
		#分析这个服务器的配置, bin路径，是否控制进程，数据库信息等
		self.databases = set()
		if self.isControl:
			self.mainGHLId = self.serverinfos[0][1]
			self.zoneId = self.mainGHLId
			self.zoneName = u"控制进程"
			self.configkey = "%s:%s" % (self.zoneName, self.zoneId)
		else:
			self.mainGHLId = 0
			self.zoneId = 0
			self.zoneName = ""
			for ptype, pid, port, word_zoneid, zonename in self.serverinfos:
				port, word_zoneid, zonename
				self.zoneName = zonename
				if not self.zoneId:
					self.zoneId = word_zoneid
				else:
					if self.zoneId != word_zoneid:
						print "Error world_zoneId", word_zoneid
				if "GHL" in ptype:
					if self.mainGHLId:
						print "Repeat GHL in one server!"
					self.mainGHLId = pid
				self.databases.add("role_sys_data_%s" % pid)
			
			self.configkey = "%s:%s" % (self.zoneName, self.zoneId)
		self.UpdataBinPath()
	
	def UpdataBinPath(self):
		global ServerConfig
		configpath = ServerConfig.get(self.configkey)
		if not configpath:
			ServerConfig[self.configkey] = self.binPath
		else:
			#使用配置的执行路径替换默认路径
			self.binPath = configpath
	
	def GetServerPathInfo(self):
		return self.configkey, self.binPath
	
	def Restart(self, event):
		if self.processThreadDict:
			for sthread in self.processThreadDict.itervalues():
				sthread.stop()
				THREADS.remove(sthread)
			#要从后面删起，不然会因为删除前面的导致后面的页码改变
			for pageindex in range(self.frame.ServerProcess.GetPageCount()-1, -1, -1):
				name = self.frame.ServerProcess.GetPageText(pageindex)
				if name in self.processThreadDict:
					self.frame.ServerProcess.DeletePage(pageindex)
			self.processThreadDict = {}
			
		for sinfo in self.serverinfos:
			sthread, pagename = self.frame.CreateServer(sinfo, self.binPath)
			self.processThreadDict[pagename] = sthread
		
		self.restart.SetLabel(u"重启")
		self.restart.SetBackgroundColour("Green")
			
	def Close(self, event):
		if not self.processThreadDict:
			return
		for sthread in self.processThreadDict.itervalues():
			sthread.stop()
			THREADS.remove(sthread)
		#要从后面删起，不然会因为删除前面的导致后面的页码改变
		for pageindex in range(self.frame.ServerProcess.GetPageCount()-1, -1, -1):
			name = self.frame.ServerProcess.GetPageText(pageindex)
			if name in self.processThreadDict:
				self.frame.ServerProcess.DeletePage(pageindex)
		self.processThreadDict = {}
		
		self.restart.SetLabel(u"启动")
		self.restart.SetBackgroundColour(wx.NullColour)

	def GMSelect(self, event):
		#选择执行GM指令的对象(只针对执行所有的GM指令功能)
		if self.isGMSelect:
			self.isGMSelect = False
			self.gmselect.SetLabel(u"执行所有指令")
			self.gmselect.SetBackgroundColour(wx.NullColour)
		else:
			self.isGMSelect = True
			self.gmselect.SetLabel(u"已选定")
			self.gmselect.SetBackgroundColour("Red")
	
	def ClearDB(self, event):
		if self.isControl:
			dlg = wx.MessageDialog(None, u"控制进程无须清档", "警告", wx.ICON_WARNING)
			dlg.ShowModal()
			return
		if self.processThreadDict:
			#必须先关服再清档
			dlg = wx.MessageDialog(None, u"必须先关服再清档", "警告", wx.ICON_WARNING)
			dlg.ShowModal()
			return
		if not self.databases:
			return
		import MySQLdb
		from World import Define
		ip, port, user, pwd = Define.Web_Global_MySQL
		con = MySQLdb.connect(host = ip, port = port, user = user, passwd = pwd,  charset = "utf8", use_unicode = False)
		with con as cur:
			cur.execute("Show databases;")
			result = cur.fetchall()
			nowdbs = [it[0] for it in result]
			for db in self.databases:
				if db not in nowdbs:
					dlg = wx.MessageDialog(None, u"已经清档了", "警告", wx.ICON_WARNING)
					dlg.ShowModal()
					continue
				cur.execute("drop database if exists %s;" % db)
				dlg = wx.MessageDialog(None, u"清档完毕", "提示", wx.ICON_INFORMATION)
				dlg.ShowModal()
				
	def ReloadAll(self, event):
		for pageindex in range(self.frame.ServerProcess.GetPageCount()-1, -1, -1):
			name = self.frame.ServerProcess.GetPageText(pageindex)
			if name in self.processThreadDict:
				self.frame.ServerProcess.GetPage(pageindex).SendCommand("from ComplexServer import GMEXE;GMEXE.ReloadAll()")
	
	def SendCommandSelect(self, command):
		if not self.isGMSelect:
			return
		for pageindex in range(self.frame.ServerProcess.GetPageCount()-1, -1, -1):
			name = self.frame.ServerProcess.GetPageText(pageindex)
			if name in self.processThreadDict:
				self.frame.ServerProcess.GetPage(pageindex).SendCommand_C_GHL(command)

class PathText(wx.StaticText):
	def SetData(self,configname, binpath):
		self.configname = configname
		self.realpath = binpath
		self.tmppath = ""
	
	def UpdateInfo(self):
		global ServerConfig
		self.realpath = self.GetLabel()
		ServerConfig[self.configname] = self.realpath
		self.tmppath = ""
	
	def SetTmpLabel(self, txt):
		if not txt:
			return
		self.tmppath = txt
		self.SetLabel(txt)
	
	def RevertLabel(self):
		if not self.tmppath:
			return
		if self.tmppath == self.realpath:
			return
		self.tmppath = ""
		self.SetLabel(self.realpath)

class ChooseButton(wx.Button):
	def BindEx(self, frame, txtCtrl):
		self.frame = frame
		self.txtCtrl = txtCtrl
		self.Bind(wx.EVT_BUTTON, self.ChangePath)
		
	def ChangePath(self, event):
		dialog = wx.FileDialog(self,"Choose file...",os.getcwd(),style=wx.OPEN,wildcard="ComplexServer.exe")
		if dialog.ShowModal() == wx.ID_OK:
			self.txtCtrl.SetTmpLabel(dialog.GetPath())


class ConfigFrame(wx.Frame):
	def __init__( self, parent):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"执行文件路径配置", size = wx.Size( 650,500 ),style = wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX |  wx.RESIZE_BORDER | wx.CAPTION )
		self.serverpathtxts = []
		self.InitUI()
	
	def InitUI(self):
		mgrframe = self.GetParent()
		self.configSizer = wx.StaticBoxSizer(wx.StaticBox(self, label = u"配置列表"), wx.VERTICAL)
		for serverbox in mgrframe.serverboxs:
			self.configSizer.Add(self.BuildOneConfig(serverbox.GetServerPathInfo()), 0)
		
		self.SaveButton = wx.Button(self, wx.ID_ANY, u"保存")
		self.SaveButton.Bind(wx.EVT_BUTTON, self.SaveConfigData)
		self.CancleButton = wx.Button(self, wx.ID_ANY, u"取消")
		self.CancleButton.Bind(wx.EVT_BUTTON, self.Cancle)
		
		bsizer = wx.BoxSizer()
		bsizer.Add(self.SaveButton,0,wx.ALL, 5)
		bsizer.Add(self.CancleButton,0,wx.ALL, 5)
		
		self.configSizer.Add(bsizer, 0, wx.TOP|wx.RIGHT| wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 25)
		self.SetSizer( self.configSizer )
		
		self.Center()
		self.Fit()
		self.SetBackgroundColour("White")
		
	def BuildOneConfig(self, configinfo):
		configname, binpath = configinfo
		
		stxt = wx.StaticBox(self, label = configname)
		bSizer = wx.StaticBoxSizer(stxt)
		
		pathtxt = PathText(self, -1, binpath, size = (400,30))
		pathtxt.SetData(configname, binpath)
		self.serverpathtxts.append(pathtxt)
		
		button = ChooseButton(self, wx.ID_ANY, u"修改")
		button.BindEx(self, pathtxt)
	
		bSizer.Add(pathtxt, 1, wx.EXPAND |wx.ALL , 2 )
		bSizer.Add(button, 0, wx.EXPAND |wx.ALL , 2 )
		return bSizer
	
	
	def SaveConfigData(self, event):
		for s in self.serverpathtxts:
			s.UpdateInfo()
		#写文件
		self.GetParent().UpdateConfig()
		
		dlg = wx.MessageDialog(None, u"保存成功", "警告", wx.ICON_WARNING)
		dlg.ShowModal()
		self.HideConfig()
	
	def Cancle(self, event):
		self.HideConfig()
		
	def HideConfig(self):
		#还原临时修改数据(静态文本框内数据)
		for txt in self.serverpathtxts:
			txt.RevertLabel()
		self.Hide()
		self.GetParent().configFrameIsOpen = False
	
	def ShowConfig(self):
		self.Show()
		self.GetParent().configFrameIsOpen = True

class GMLogFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"GM指令记录", pos = wx.DefaultPosition, size = wx.Size( 850,750 ), style = wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX |  wx.RESIZE_BORDER | wx.CAPTION  )
		self.InitUI()
		
	def InitUI(self):
		self.filenameTxt = wx.TextCtrl(self, size = (410, 25))
		self.contents = wx.TextCtrl(self, size = (390, 260), style = wx.TE_MULTILINE | wx.HSCROLL)
		self.filenameTxt.SetValue(GMFilePath)
		if not os.path.exists(GMFilePath):
			with open(GMFilePath, 'a') as _:
				return
		with open(GMFilePath, 'r') as f:
			self.contents.SetValue(f.read())
		self.tSizer = wx.BoxSizer(wx.VERTICAL)
		self.tSizer.Add(self.filenameTxt, 0, wx.EXPAND |wx.ALL,10)
		self.tSizer.Add(self.contents, 1, wx.EXPAND |wx.ALL,10)
		
		self.Hidebutton = wx.Button(self, wx.ID_ANY, u"隐藏")
		self.Hidebutton.Bind(wx.EVT_BUTTON, self.HideLog)
		self.tSizer.Add(self.Hidebutton, 0, wx.ALIGN_RIGHT | wx.ALL, 20)
		self.SetSizer( self.tSizer )
		self.SetBackgroundColour("White")
	
	def ShowLog(self):
		with open(GMFilePath, 'r') as f:
			self.contents.SetValue(f.read())
		self.Show()
	
	def HideLog(self, event = None):
		self.GetParent().gmlogFrameIsOpen = False
		self.Hide()

class MgrFrame(wx.Frame):
	def __init__( self, parent):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"龙骑士传", pos = wx.DefaultPosition, size = wx.Size( 880,800 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		self.serverboxs = []
		self.configFrameIsOpen = False
		self.gmlogFrameIsOpen = False
		self.InitUI()
		self.CreatStdOut()
		self.Create843()
	
	def InitUI(self):
		#三部分，服务器控制，控制台，进程控制
		self.BuildServerSizer(wx.StaticBox(self, label = u"服务器列表"))
		
		
		self.ServerProcess = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
		self.BuildControlSizer()
		self.ConfigsSizer()
		
		
		#第一排,服务器控制，配置
		self.serverandconfigSizer = wx.BoxSizer()
		self.serverandconfigSizer.Add(self.serverSizer, 1, wx.EXPAND | wx.ALL, 5)
		self.serverandconfigSizer.Add(self.cSizer, 0, wx.ALIGN_RIGHT|wx.RIGHT | wx.TOP, 15)
		#第二排，进程控制台页签
		self.serverprocessbox = wx.StaticBoxSizer(wx.StaticBox(self, label = "进程控制台(可对当前选中页签发送GM指令)"))
		self.serverprocessbox.Add(self.ServerProcess,1, wx.EXPAND | wx.ALL, 5)
		
		
		#总布局管理器
		AllSizer = wx.BoxSizer( wx.VERTICAL )
		AllSizer.Add( self.serverandconfigSizer, 0, wx.EXPAND | wx.ALL, 5 )
		AllSizer.Add( self.serverprocessbox, 7, wx.EXPAND |wx.ALL, 5 )
		AllSizer.Add( self.ControlSizer, 3, wx.EXPAND, 5 )
		
		self.SetSizer( AllSizer )
		self.Center()
		self.SetBackgroundColour("White")
		
		#配置面板
		self.configFrame = ConfigFrame(self)
		self.gmlogFrame = GMLogFrame(self)
	
	def ConfigsSizer(self):
		self.cSizer = wx.BoxSizer( wx.VERTICAL )
		self.SetServerEXEPath = wx.Button( self, wx.ID_ANY, u"设置启服路径")
		self.SetServerEXEPath.Bind(wx.EVT_BUTTON, self.ServerEXEConfig)
		self.about = wx.Button( self, wx.ID_ANY, u"其他信息")
		self.cSizer.Add( self.SetServerEXEPath, 0, wx.EXPAND |wx.ALL|wx.RIGHT, 5 )
		self.cSizer.Add( self.about, 0, wx.EXPAND |wx.ALL|wx.RIGHT, 5 )
	
	def BuildOneServerBox(self, serverName, sinfo = None, isControl = False):
		stxt = wx.StaticBox(self, label = serverName)
		bottomSizer = ServerBox(stxt, wx.VERTICAL)
		bottomSizer.BindServerInfo(self, sinfo, isControl)
		self.serverboxs.append(bottomSizer)
		
		return bottomSizer

	def BuildServerSizer(self, sBox):
		#服务器控制
		self.serverSizer = wx.StaticBoxSizer(sBox)
		
		import BuildStart
		self.nameDict = {}
		self.controlServers = {}
		for ptype, pid, port, word_zoneid, zonename, in BuildStart.GetProcessInfo():
			if zonename == "None":
				#控制进程
				self.controlServers[pid] = [(ptype, pid, port, word_zoneid, zonename)]
				continue
			if zonename not in self.nameDict:
				self.nameDict[zonename] = [(ptype, pid, port, word_zoneid, zonename)]
			else:
				self.nameDict[zonename].append((ptype, pid, port, word_zoneid, zonename))
		
		for pid, serverInfo in self.controlServers.iteritems():
			self.serverSizer.Add(self.BuildOneServerBox(u"控制进程%s" % pid, serverInfo, True), 0, wx.LEFT , 10 )
			
		for name, serverInfo in self.nameDict.iteritems():
			self.serverSizer.Add(self.BuildOneServerBox(name, serverInfo), 0, wx.LEFT , 10 )
		
	def BuildControlSizer(self):
		#GM指令控制
		ButtonSizer = wx.BoxSizer(wx.VERTICAL)
		self.SendCommand = wx.Button( self, wx.ID_ANY, u"发送GM命令")
		self.SendCommand.Bind(wx.EVT_BUTTON, self.SendCommandEx)
		self.SendCommands = wx.Button( self, wx.ID_ANY, u"多个进程命令")
		self.SendCommands.Bind(wx.EVT_BUTTON, self.SendCommandsEx)
		self.CommandLog = wx.Button( self, wx.ID_ANY, u"GM指令记录")
		self.CommandLog.Bind(wx.EVT_BUTTON, self.OpenGMLog)
		
		
		ButtonSizer.Add( self.SendCommand, 0, wx.EXPAND |wx.ALL, 5 )
		ButtonSizer.Add( self.SendCommands, 0, wx.EXPAND |wx.ALL, 5 )
		ButtonSizer.Add( self.CommandLog, 0, wx.EXPAND |wx.ALL, 5 )
	
		self.GMText = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 600,250 ), wx.HSCROLL|wx.TE_MULTILINE)
		self.GMText.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString ) )
		
		self.ControlSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.ControlSizer.Add( self.GMText, 1, wx.ALL|wx.EXPAND, 5 )
		self.ControlSizer.Add( ButtonSizer, 0, wx.ALL|wx.EXPAND, 5 )
	
	
	def CreatePage(self, name, text_ctrl = None, processInfo = None):
		if text_ctrl is None:
			text_ctrl = wx.TextCtrl
		tab = ProcessPanel( self.ServerProcess, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		if processInfo:
			#设置这个页签所属的进程信息
			tab.SetProcessInfo(processInfo)
		out_text = text_ctrl( tab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 750,-1 ), wx.HSCROLL|wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)
		out_text.SetBackgroundColour( wx.Colour( 208, 208, 208 ) )
		font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
		out_text.SetFont(font)
		box_sizer = wx.BoxSizer( wx.VERTICAL )
		box_sizer.Add( out_text, 1, wx.ALL | wx.EXPAND, 5 )
		
		tab.SetSizer( box_sizer )
		tab.Layout()
		box_sizer.Fit( tab )
		self.ServerProcess.AddPage(tab, name, False)
		self.ServerProcess.SetSelection(self.ServerProcess.GetPageCount() - 1)
		return out_text, self.ServerProcess.GetPageText(self.ServerProcess.GetPageCount() - 1)
	
	def CreateProcess(self, name, args, binPath):
		out_text, pageName = self.CreatePage(name, ColorTextCtrl, args)
		sub_thread = SubProcess(out_text, args, binPath)
		sub_thread.start()
		THREADS.append(sub_thread)
		return sub_thread, pageName
	
	def CreateServer(self, serverInfo, binPath):
		ptype, pid, port, _, _ = serverInfo
		name = "%s.%s" % (ptype, pid)
		args = [binPath, ptype, str(pid), str(port)]
		return self.CreateProcess(name.decode("utf8"), args, binPath)
	
	def CreatStdOut(self):
		out_text, _ = self.CreatePage(u"GUI")
		sys.stdout = out_text
		sys.stderr = out_text
	
	def Create843(self):
		policyd_thread = PolicyServer(843, DynamicPath.PyFloderPath + "Policyd/FlashPolicy.xml")
		policyd_thread.start()
		THREADS.append(policyd_thread)
		
	def SendCommandEx(self, event):
		processPage = self.ServerProcess.GetPage(self.ServerProcess.GetSelection())
		if not processPage or processPage.IsGUI():
			return
		processPage.SendCommand(self.GMText.GetValue())
		SaveCommand(self.GMText.GetValue())
	
	def SendCommandsEx(self, event):
		for serverbox in self.serverboxs:
			serverbox.SendCommandSelect(self.GMText.GetValue())
		SaveCommand(self.GMText.GetValue())
		
	def ServerEXEConfig(self, event):
		if self.configFrameIsOpen:
			self.configFrame.HideConfig()
		else:
			self.configFrame.ShowConfig()
			
	def UpdateConfig(self):
		for sb in self.serverboxs:
			sb.UpdataBinPath()
		UpdateConfig()
	
	def OpenGMLog(self, event):
		if self.gmlogFrameIsOpen:
			self.gmlogFrameIsOpen = False
			self.gmlogFrame.HideLog()
		else:
			self.gmlogFrameIsOpen = True
			self.gmlogFrame.ShowLog()

def LoadConfig():
	if not os.path.exists(ConfigFilePath):
		with open(ConfigFilePath, 'a') as _:
			return
	with open(ConfigFilePath, 'r') as f:
		line = f.readline()
		if line:
			global ServerConfig
			ServerConfig = eval(line)

def UpdateConfig():
	with open(ConfigFilePath, 'w') as f:
		f.write(str(ServerConfig))

def SaveCommand(command):
	with open(GMFilePath, 'a') as f:
		print>>f, command


if __name__ == "__main__":
	out = sys.stdout
	err = sys.stderr
	IS_LOOP = None
	THREADS = []
	ServerConfig = {}
	LoadConfig()
	try:
		# 创建应用、主面板
		app = wx.App(redirect = False)
		frame = MgrFrame(None)
		frame.Show()
		# GUI循环
		IS_LOOP = True
		app.MainLoop()
		IS_LOOP = False
		sys.stdout = out
		sys.stderr = err
		# 强制停止所有的线程、子进程
		for my_thread in THREADS:
			my_thread.stop()
	except:
		sys.stdout = out
		sys.stderr = err
		traceback.print_exc()
	sys.stdout = out
	sys.stderr = err
	print "End"
