#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Logic.S843")
#===============================================================================
# 启动843端口监听
#===============================================================================
import time
import socket
import thread
import threading
import exceptions
import contextlib
import Environment
import DynamicPath
from ComplexServer import Init

class PolicyServer(threading.Thread):
	def __init__(self, port, path):
		threading.Thread.__init__(self)
		self.is_run = True
		self.policy = self.read_policy(path)
		self.log_path = DynamicPath.FilePath + "843.log"
		# 清空数据
		with open(self.log_path, "w"):
			pass
		# 监听端口
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('', port))
		self.sock.listen(20)
		print "BLUE listen %s ok." % port
	
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

def start_server():
	global THREAD
	THREAD = PolicyServer(843, DynamicPath.PyFloderPath + "Policyd/FlashPolicy.xml")
	THREAD.start()

def stop_server():
	global THREAD
	THREAD.is_run = False
	THREAD.sock.close()
	time.sleep(2)

if "_HasLoad" not in dir():
	THREAD = None
	if Environment.IsWindows and Environment.HasLogic:
		Init.InitCallBack.RegCallbackFunction(start_server)
		Init.FinalCallBack.RegCallbackFunction(stop_server)
