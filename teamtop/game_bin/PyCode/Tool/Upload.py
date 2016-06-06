#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Tool.Upload")
#===============================================================================
# 上传文件，并执行命令
#===============================================================================
import sys
import time
import socket
import struct

GT = "tgw_l7_forward\r\nHost: %s:%s\r\n\r\n"

# 新的连接
def NewConnect(host, port):
	so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	so.connect((host, port))
	return so

# 从socket中读取一个ui32
def ReadUint32From(so):
	ui32 = ""
	while len(ui32) != 4:
			ui32 += so.recv(4 - len(ui32))
	ui32 = struct.unpack("I", ui32)[0]
	return ui32

# 发送TGW数据
def SendTGWData(so, host, port):
	so.sendall(GT % (host, port))

# 发送文件
def SendZIPFile(so, fp):
	with open(fp, "rb") as f:
		buf = f.read()
		buflen = len(buf)
		so.sendall(struct.pack("I", buflen))
		so.sendall(buf)
	
	rate = 0
	cell = 0
	while True:
		nowlen = ReadUint32From(so)
		if nowlen == buflen:
			print "OK"
			break
		else:
			if rate != (nowlen * 100 / buflen):
				rate = (nowlen * 100 / buflen)
				print "%s%%" % rate,
				cell += 1
				if cell == 20:
					cell = 0
					print

# 执行之后的操作
def AfterSend(so, scr):
	so.sendall(struct.pack("I", len(scr)))
	so.sendall(scr)
	ret = so.recv(1024)
	so.close()
	print ret
	with open("log.txt", "w") as f:
		print>>f, ret
	
# 开始上传
def StartUpload(fp, cmd, host, port):
	so = NewConnect(host, port)
	SendTGWData(so, host, port)
	SendZIPFile(so, fp)
	AfterSend(so, cmd)

if __name__ == "__main__":
	fp = sys.argv[1]
	cmd = sys.argv[2]
	host = sys.argv[3]
	port = int(sys.argv[4])
	StartUpload(fp, cmd, host, port)
