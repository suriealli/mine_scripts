#!/usr/bin/env python
#encoding = utf-8

import socket
import struct
HOST = '0.0.0.0'
PORT = 24056 #do not use ''
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(1)
conn,addr=s.accept()


#----
print "connection addr from :" ,addr

while 1:
    data = conn.recv(4096)
    if not data:break
    print struct.unpack("HH",data)

conn.close()

