#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 迷你客户端
#===============================================================================
import math
import time
import struct
import random
import traceback
import Environment
from Tool.GM import GMCMD
from Common.Message import OtherMessage, CMessage
from Common import CValue

class MiniClient(object):
	def __init__(self, account, pwd, zid, ip, port):
		self.account = account
		self.pwd = pwd
		self.zid = zid
		self.gm = GMCMD.GMConnect(ip, port, True)
		self.gm.iamclient()
		# 角色位置
		self.scene_id = 0
		self.pos_x = None
		self.pos_y = None
		self.target_x = None
		self.target_y = None
		# 注册处理函数
		self.gm.functions[CMessage.enSyncRoleScenePos] = self.on_enter_scene
	
	def login(self):
		login_info = {"serverid":self.zid, "account":self.account, "userip":"userip", "openkey":self.pwd, "pf":"pf", "pfkey":"pfkey"}
		self.gm.sendobj(OtherMessage.OMsg_Login, login_info)
		msg_type, msg_body = self.gm.recvobj()
		if msg_type == OtherMessage.OMsg_RoleError:
			self.create()
			return
		if msg_type != OtherMessage.OMsg_ServerUnixTime:
			print "login fail", msg_body
			return
		print "server time is", msg_body
		self.client_ok()
	
	def create(self):
		self.gm.sendobj(OtherMessage.OMsg_CreateRole, [None, self.account, random.randint(1, 2), random.randint(1, 2)])
		msg_type, msg_body = self.gm.recvobj()
		if msg_type != OtherMessage.OMsg_FirstCreateRole:
			print "create fail 1", msg_body
			return
		msg_type, msg_body = self.gm.recvobj()
		if msg_type != OtherMessage.OMsg_ServerUnixTime:
			print "create fail 2", msg_body
			return
		print "server time is", msg_body
		self.client_ok()
	
	def client_ok(self):
		self.gm.sendobj(OtherMessage.OMsg_ClientOK, None)
		print "login success"
		self.gm.threadrecvmsg()
	
	def close(self):
		self.gm.close()
	
	def ping(self):
		self.gm.sendmsg(CMessage.enGEMsg_Ping, "")
	
	def echo(self):
		self.gm.sendmsg(CMessage.enProcessMsg_Echo, "")
	
	def say(self, roleid, s):
		if len(s) > CValue.MAX_UINT8:
			msgbody = struct.pack("QbH", roleid, GMCMD.BIG_STRING_FLAG, len(s)) + s
		else:
			msgbody = struct.pack("QbB", roleid, GMCMD.SMALL_STRING_FLAG, len(s)) + s
		self.gm.sendmsg(CMessage.enClientCharMsg, msgbody)
	
	def move_chat(self, rate = 0):
		if self.pos_x is None:
			return
		if self.target_x is None or (self.pos_x == self.target_x and self.pos_y == self.target_y):
			self.target_x = random.randint(0, 4000)
			self.target_y = random.randint(0, 4000)
			self.gm.sendmsg(CMessage.enRoleToTargetPos, struct.pack("HH", self.target_x, self.target_y))
			self.say(2, "我的目标在(%s, %s)" % (self.target_x, self.target_y))
		total_disdance = int(math.sqrt(abs(self.target_x - self.pos_x) ** 2 + abs(self.target_y - self.pos_y) ** 2))
		if total_disdance < 160:
			self.pos_x = self.target_x
			self.pos_y = self.target_y
		else:
			self.pos_x += 160 * (self.target_x - self.pos_x) / total_disdance
			self.pos_y += 160 * (self.target_y - self.pos_y) / total_disdance
		self.gm.sendmsg(CMessage.enRoleMovePos, struct.pack("HH", self.pos_x, self.pos_y))
	
	def role_gm(self, command):
		from Game.Role import RoleGM
		msgtype = RoleGM.AutoMessage.AutoMsg["RMMsg_GM"][0]
		self.gm.sendobj(msgtype, (0, command))
	
	def on_enter_scene(self, msgbody):
		self.scene_id, _, _, self.pos_x, self.pos_y = struct.unpack("IHHHH", msgbody)
		print "enter scene %s" % self.scene_id
		self.gm.sendmsg(CMessage.enClientJoinSceneOK, "")

def set_broad(zid):
	_, _, _, ip, port = get_info(zid, "account")
	gm = GMCMD.GMConnect(ip, port, True)
	gm.iamgm()
	print gm.gmcommand("import cRoleMgr;cRoleMgr.SetEchoLevel(999999)")

def set_say(zid):
	_, _, _, ip, port = get_info(zid, "account")
	gm = GMCMD.GMConnect(ip, port, True)
	gm.iamgm()
	print gm.gmcommand("import Game.Role.Chat as C;C.CD[2]=0")

def create_login_cliet(zid, cnt):
	l = []
	for idx in xrange(cnt):
		account = "%s_%s" % (Environment.IP, idx)
		print account
		try:
			account, pwd, zid, ip, port = get_info(zid, account)
			client = MiniClient(account, pwd, zid, ip, port)
			client.login()
			l.append(client)
		except:
			traceback.print_exc()
	return l

def test_net_work():
	zid = 3
	#set_broad(zid)
	#set_say(zid)
	client_list = create_login_cliet(zid, 200)
	# 广播
	cnt = 0
	while True:
		cnt += 1
		enter = 0
		for client in client_list:
			if not client.scene_id:
				continue
			enter += 1
			client.echo()
			#client.say(2, str(cnt))
		print cnt, enter
		time.sleep(1)

def test_move():
	zid = 1
	client_list = create_login_cliet(zid, 1000)
	need_move = True
	# 飞指定场景
	while need_move:
		need_move = False
		for client in client_list:
			if client.scene_id == 0:
				need_move = True
				continue
			if client.scene_id != 3:
				client.role_gm("role.Revive(3, 4038, 1957)")
				need_move = True
				continue
		time.sleep(1)
	# 设置飞行
	for client in client_list:
		client.role_gm("role.SetFly(1)")
	# 移到
	while True:
		for client in client_list:
			client.move_chat(100)
		time.sleep(1)
	

def get_info(serverid, account, thirdparty = 1):
	return account, "1", serverid, "192.168.5.236", 9000
	return account, "1", serverid, "banben1.app100718848.twsapp.com", 8001

if __name__ == "__main__":
	test_net_work()

