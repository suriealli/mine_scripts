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
	def __init__(self, text_ctrl, cmds):
		threading.Thread.__init__(self)
		self.text_ctrl = text_ctrl
		self.process = subprocess.Popen(args = cmds,
									stdin = subprocess.PIPE,
									stdout=subprocess.PIPE,
									stderr=subprocess.STDOUT,
									cwd = DynamicPath.BinPath,
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
						wx.CallAfter(self.text_ctrl.write, u"返回：%s" % return_code)
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
		print "stop"

class ColorTextCtrl(wx.TextCtrl):
	def write(self, *args, **kwargs):
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


class ProcessPanel(wx.Panel):
	processInfo = None
	def SetProcessInfo(self, info):
		print "SetProcessInfo"
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
		print "SEND command"
		
	def InitGMConnect(self):
		from Tool.GM import GMCMD
		self.gm = GMCMD.GMConnect("127.0.0.1", self.port, "G" in self.ptype)
		self.gm.iamgm()




class LY5_Frame(wx.Frame):
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"龙骑士传", pos = wx.DefaultPosition, size = wx.Size( 1000,800 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
	
	def InitUI(self):
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		AllSizer = wx.BoxSizer( wx.VERTICAL )
		self.ServerProcess = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
		AllSizer.Add( self.ServerProcess, 8, wx.EXPAND |wx.ALL, 5 )
		
		ControlSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.GMText = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 600,150 ), wx.HSCROLL|wx.TE_MULTILINE)
		self.GMText.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString ) )
		ControlSizer.Add( self.GMText, 7, wx.ALL|wx.EXPAND|wx.SHAPED, 5 )
		
		ButtonSizer = wx.GridSizer( 0, 2, 0, 0 )
		self.SendCommand = wx.Button( self, wx.ID_ANY, u"发送GM命令", wx.DefaultPosition, wx.DefaultSize, 0 )
		
		self.SendCommand.Bind(wx.EVT_BUTTON, self.SendCommandEx)
		ButtonSizer.Add( self.SendCommand, 0, wx.ALL, 5 )
		self.ReloadAll = wx.Button( self, wx.ID_ANY, u"重载所有脚本", wx.DefaultPosition, wx.DefaultSize, 0 )
		ButtonSizer.Add( self.ReloadAll, 0, wx.ALL, 5 )
		self.SendCommands = wx.Button( self, wx.ID_ANY, u"多进程命令", wx.DefaultPosition, wx.DefaultSize, 0 )
		ButtonSizer.Add( self.SendCommands, 0, wx.ALL, 5 )
		self.Kill = wx.Button( self, wx.ID_ANY, u"关闭进程", wx.DefaultPosition, wx.DefaultSize, 0 )
		ButtonSizer.Add( self.Kill, 0, wx.ALL, 5 )
		
		ControlSizer.Add( ButtonSizer, 3, wx.EXPAND, 5 )
		AllSizer.Add( ControlSizer, 2, wx.EXPAND, 5 )
		
		self.SetSizer( AllSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def CreatePage(self, name, text_ctrl = None, processInfo = None):
		if text_ctrl is None:
			text_ctrl = wx.TextCtrl
		tab = ProcessPanel( self.ServerProcess, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		if processInfo:
			#设置这个页签所属的进程信息
			tab.SetProcessInfo(processInfo)
		out_text = text_ctrl( tab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 750,-1 ), wx.HSCROLL|wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)
		out_text.SetBackgroundColour( wx.Colour( 208, 208, 208 ) )
		box_sizer = wx.BoxSizer( wx.VERTICAL )
		box_sizer.Add( out_text, 1, wx.ALL, 5 )
		
		tab.SetSizer( box_sizer )
		tab.Layout()
		box_sizer.Fit( tab )
		self.ServerProcess.AddPage(tab, name, False)
		return out_text
	
	def CreateProcess(self, name, args):
		out_text = self.CreatePage(name, ColorTextCtrl, args)
		sub_thread = SubProcess(out_text, args)
		sub_thread.start()
		THREADS.append(sub_thread)
	
	def CreatStdOut(self):
		out_text = self.CreatePage(u"GUI")
		sys.stdout = out_text
		sys.stderr = out_text
	
	def Create843(self):
		policyd_thread = PolicyServer(843, DynamicPath.PyFloderPath + "Policyd/FlashPolicy.xml")
		policyd_thread.start()
		THREADS.append(policyd_thread)
	
	def CreateServer(self, serverlist):
		for ptype, pid, port, _, _, in serverlist:
			name = "%s.%s" % (ptype, pid)
			args = [DynamicPath.BinPath + "ComplexServer.exe", ptype, str(pid), str(port)]
			self.CreateProcess(name.decode("utf8"), args)
	
	
	def SendCommandEx(self, event):
		#单独对一个进程发指令
		#获取当前页签的进程GM指令
		processPage = self.ServerProcess.GetPage(self.ServerProcess.GetSelection())
		if not processPage or processPage.IsGUI():
			return
		processPage.SendCommand(self.GMText.GetValue())
	
	def ReloadAllEx(self, event):
		pass
	
	def SendCommandsEx(self, event):
		pass
	
	def KillEx(self, event):
		pass
	

class ServerCheckBox(wx.CheckBox):
	def InitServerInfos(self):
		self.Servers = []
	
	def AppendServerInfo(self, info):
		self.Servers.append(info)
	
	def GetServers(self):
		return self.Servers

class SelectFrame(wx.Frame):
	def __init__( self, parent):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"龙骑士传", pos = wx.DefaultPosition, size = wx.Size( 600,350 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		self.InitUI()

	def InitUI(self):
		self.startSelectButton = wx.Button( self, wx.ID_ANY, u"启动选择的服务器" )
		self.startSelectButton.Bind(wx.EVT_BUTTON, self.StartSelect)
		self.startAllButton = wx.Button( self, wx.ID_ANY, u"启动所有的服务器" )
		self.startAllButton.Bind(wx.EVT_BUTTON, self.StartAll)
		sb1 = wx.StaticBox(self, label=u"功能")  
		bottomSizer = wx.StaticBoxSizer(sb1, wx.VERTICAL)
		bottomSizer.Add( self.startSelectButton, 1, wx.EXPAND |wx.ALL , 10 )
		bottomSizer.Add( self.startAllButton, 1, wx.EXPAND |wx.ALL, 10 )
		
		#复选框
		import BuildStart
		nameDict = {}
		controlServers = {}
		for ptype, pid, port, word_zoneid, zonename, in BuildStart.GetProcessInfo():
			if zonename == "None":
				#控制进程
				controlServers[pid] = (ptype, pid, port, word_zoneid, zonename)
			elif zonename not in nameDict:
				nameDict[zonename] = [(ptype, pid, port, word_zoneid, zonename)]
			else:
				nameDict[zonename].append((ptype, pid, port, word_zoneid, zonename))

		
		self.CheckBoxs = []
		sb2 = wx.StaticBox(self, label=u"选择启动的服务器")
		checkBosSizer = wx.StaticBoxSizer(sb2, wx.VERTICAL)
		for cinfo in controlServers.itervalues():
			scb = ServerCheckBox(self, -1, u"控制进程: C%s" % cinfo[1])
			scb.InitServerInfos()
			scb.SetValue(True)
			scb.AppendServerInfo(cinfo)
			checkBosSizer.Add(scb, 0, wx.EXPAND |wx.ALL, 10 )
			self.CheckBoxs.append(scb)
		
		for name, infos in nameDict.iteritems():
			scb = ServerCheckBox(self, -1, name + ":S%s"% infos[0][1])
			scb.InitServerInfos()
			for info in infos:
				scb.AppendServerInfo(info)
			checkBosSizer.Add(scb, 0, wx.EXPAND |wx.ALL, 10 )
			self.CheckBoxs.append(scb)
			
		AllSizer = wx.BoxSizer( )
		AllSizer.Add(checkBosSizer, 1, wx.ALIGN_CENTER, 0 )
		AllSizer.Add(bottomSizer, 1, wx.ALIGN_CENTER)
		
		
		self.SetSizer( AllSizer )
		self.Center()
		self.SetBackgroundColour("White")
		
		
	def StartAll(self, event):
		serverlist = []
		for scb in self.CheckBoxs:
			serverlist.extend(scb.GetServers())
		StartServers(serverlist)
		self.Close()
	
	def StartSelect(self, event):
		serverlist = []
		for scb in self.CheckBoxs:
			if not scb.GetValue():
				continue
			serverlist.extend(scb.GetServers())
		StartServers(serverlist)
		self.Close()

def StartServers(serverlist):
	frame = LY5_Frame(None)
	# 创建UI
	frame.InitUI()
	# 创建系统输出面板
	frame.CreatStdOut()
	# 创建进程
	frame.Create843()
	frame.CreateServer(serverlist)
	# 显示之
	frame.Show()


if __name__ == "__main__":
	out = sys.stdout
	err = sys.stderr
	IS_LOOP = None
	THREADS = []
	try:
		# 创建应用、主面板
		app = wx.App()
		frame = SelectFrame(None)
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
