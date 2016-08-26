#!/usr/bin/env python
#coding:utf8

import socket,os
import struct,types
from configobj import ConfigObj
import codecs

# C中的标识位定义
NONE_FLAG =				-100			#None
TRUE_FLAG =				-101			#True
FALSE_FLAG =			-102			#False
SMALL_TUPLE_FLAG =		-103			#Tuple
BIG_TUPLE_FLAG =		-104			#Tuple
SMALL_LIST_FLAG =		-105			#List
BIG_LIST_FLAG =			-106			#List
SMALL_SET_FLAG =		-107			#Set
BIG_SET_FLAG =			-108			#Set
SMALL_DICT_FLAG =		-109			#Dict
BIG_DICT_FLAG =			-110			#Dict
SMALL_STRING_FLAG =		-111			#String
BIG_STRING_FLAG =		-112			#String
DATETIME_FLAG =			-113			#DateTime
SIGNED_INT8_FLAG =		-114			#signed int8
SIGNED_INT16_FLAG =		-115			#signed int16
SIGNED_INT32_FLAG =		-116			#signed int32
SIGNED_INT64_FLAG =		-117			#signed int64
CLASS_OBJ_FLAG = 		-118			#class
CLASS_OBJ_FLAG2 = 		-119			#class2
SUPER_BIG_STRING_FLAG =	-120			#String

EndPoint_GM_ = 4
CMsg_Who = 3
PyMsg_GMRequest = 101
PyMsg_GMResponse = 102
MIN_UINT8 = 0
MAX_UINT8 = 255
MIN_UINT16 = 0
MAX_UINT16 = 65535
MIN_UINT32 = 0
MAX_UINT32 = 4294967295

class GMConnect(object):
    def __init__(self, host, port, tgw = False):
        if host and port:
            self.sock = socket.socket()
            self.sock.connect((host, port))
            if tgw:
                self.sock.sendall("tgw_l7_forward\r\nHost: %s:%s\r\n\r\n" % (host, port))
            self.thread = False
    def iamgm(self):
        msgbody = struct.pack("I", EndPoint_GM_)
        self.sendmsg(CMsg_Who, msgbody)
    def sendmsg(self, msgtype, msgbody = ""):
        head = struct.pack("HH", 4 + len(msgbody), msgtype)
        self.sock.sendall(head + msgbody)

    def sendobj(self, msgtype, msgobj = None):
        msglis = []
        self.packobj(msgobj, msglis)
        self.sendmsg(msgtype, "".join(msglis))

    def __recvmsg(self):
        head = ""
        while len(head) != 4:
            head += self.sock.recv(4 - len(head))
        #print "__recvmsg, head"
        bodylen, msgtype = struct.unpack("HH", head)
        bodylen -= 4
        #print "__recvmsg, bodylen", bodylen
        if bodylen == 0:
            return msgtype, ""
        body = ""
        while len(body) != bodylen:
            body += self.sock.recv(bodylen - len(body))
        #print "__recvmsg, body"
        return msgtype, body

    def recvobj(self):
        assert not self.thread
        msgtype, self.body = self.__recvmsg()
        if self.body:
            obj = self.unpackobj()
        else:
            obj = None
        del self.body
        return msgtype, obj

    def unpackobj(self):
        flag = struct.unpack("b", self.body[:1])[0]
        self.body = self.body[1:]
        if flag > NONE_FLAG:
            return flag
        elif flag == NONE_FLAG:
            return None
        elif flag == TRUE_FLAG:
            return True
        elif flag == FALSE_FLAG:
            return False
        elif flag == SMALL_TUPLE_FLAG:
            size = struct.unpack("B", self.body[:1])[0]
            self.body = self.body[1:]
            lis = []
            for _ in xrange(size):
                lis.append(self.unpackobj())
            return tuple(lis)
        elif flag == BIG_TUPLE_FLAG:
            size = struct.unpack("H", self.body[:2])[0]
            self.body = self.body[2:]
            lis = []
            for _ in xrange(size):
                lis.append(self.unpackobj())
            return tuple(lis)
        elif flag == SMALL_LIST_FLAG:
            size = struct.unpack("B", self.body[:1])[0]
            self.body = self.body[1:]
            lis = []
            for _ in xrange(size):
                lis.append(self.unpackobj())
            return lis
        elif flag == BIG_LIST_FLAG:
            size = struct.unpack("H", self.body[:2])[0]
            self.body = self.body[2:]
            lis = []
            for _ in xrange(size):
                lis.append(self.unpackobj())
            return lis
        elif flag == SMALL_SET_FLAG:
            size = struct.unpack("B", self.body[:1])[0]
            self.body = self.body[1:]
            lis = []
            for _ in xrange(size):
                lis.append(self.unpackobj())
            return set(lis)
        elif flag == BIG_LIST_FLAG:
            size = struct.unpack("H", self.body[:2])[0]
            self.body = self.body[2:]
            lis = []
            for _ in xrange(size):
                lis.append(self.unpackobj())
            return set(lis)
        elif flag == SMALL_DICT_FLAG:
            size = struct.unpack("B", self.body[:1])[0]
            self.body = self.body[1:]
            dic = {}
            for _ in xrange(size):
                key = self.unpackobj()
                value = self.unpackobj()
                dic[key] = value
            return dic
        elif flag == BIG_DICT_FLAG:
            size = struct.unpack("H", self.body[:2])[0]
            self.body = self.body[2:]
            dic = {}
            for _ in xrange(size):
                key = self.unpackobj()
                value = self.unpackobj()
                dic[key] = value
            return dic
        elif flag == SMALL_STRING_FLAG:
            size = struct.unpack("B", self.body[:1])[0]
            self.body = self.body[1:]
            s = self.body[:size]
            self.body = self.body[size:]
            return s
        elif flag == BIG_STRING_FLAG:
            size = struct.unpack("H", self.body[:2])[0]
            self.body = self.body[2:]
            s = self.body[:size]
            self.body = self.body[size:]
            return s
        elif flag == DATETIME_FLAG:
            year = struct.unpack("H", self.body[:2])[0]
            self.body = self.body[2:]
            month = struct.unpack("H", self.body[:2])[0]
            self.body = self.body[2:]
            day = struct.unpack("H", self.body[:2])[0]
            self.body = self.body[2:]
            hour = struct.unpack("H", self.body[:2])[0]
            self.body = self.body[2:]
            minute = struct.unpack("H", self.body[:2])[0]
            self.body = self.body[2:]
            second = struct.unpack("H", self.body[:2])[0]
            self.body = self.body[2:]
            return datetime.datetime(year, month, day, hour, minute, second)
        elif flag == SIGNED_INT8_FLAG:
            i = struct.unpack("b", self.body[:1])[0]
            self.body = self.body[1:]
            return i
        elif flag == SIGNED_INT16_FLAG:
            i = struct.unpack("h", self.body[:2])[0]
            self.body = self.body[2:]
            return i
        elif flag == SIGNED_INT32_FLAG:
            i = struct.unpack("i", self.body[:4])[0]
            self.body = self.body[4:]
            return i
        elif flag == SIGNED_INT64_FLAG:
            i = struct.unpack("q", self.body[:8])[0]
            self.body = self.body[8:]
            return i
        else:
            print "unpack flag", flag, self.body
            assert False

    @staticmethod
    def packobj(msgobj, msglis):
        t = type(msgobj)
        if msgobj is None:
            msglis.append(struct.pack("b", NONE_FLAG))
        elif msgobj is True:
            msglis.append(struct.pack("b", TRUE_FLAG))
        elif msgobj is False:
            msglis.append(struct.pack("b", FALSE_FLAG))
        elif t == types.IntType or t == types.LongType:
            if MIN_INT8 <= msgobj <= MAX_INT8:
                if msgobj > NONE_FLAG:
                    msglis.append(struct.pack("b",msgobj))
                else:
                    msglis.append(struct.pack("b",SIGNED_INT8_FLAG))
                    msglis.append(struct.pack("b",msgobj))
            elif MIN_INT16 <= msgobj <= MAX_INT16:
                msglis.append(struct.pack("b",SIGNED_INT16_FLAG))
                msglis.append(struct.pack("h", msgobj))
            elif MIN_INT32 <= msgobj <=MAX_INT32:
                msglis.append(struct.pack("b",SIGNED_INT32_FLAG))
                msglis.append(struct.pack("i", msgobj))
            else:
                msglis.append(struct.pack("b",SIGNED_INT64_FLAG))
                msglis.append(struct.pack("q", msgobj))
        elif t == types.TupleType or t == types.ListType or t == type(set()):
            size = len(msgobj)
            if size > MAX_UINT8:
                msglis.append(struct.pack("b",BIG_TUPLE_FLAG))
                msglis.append(struct.pack("H", size))
            else:
                msglis.append(struct.pack("b",SMALL_TUPLE_FLAG))
                msglis.append(struct.pack("B", size))
            for item in msgobj:
                GMConnect.packobj(item, msglis)
        elif t == types.ListType or t == type(set()):
            size = len(msgobj)
            if size > MAX_UINT8:
                msglis.append(struct.pack("b", BIG_LIST_FLAG))
                msglis.append(struct.pack("H", size))
            else:
                msglis.append(struct.pack("b",SMALL_LIST_FLAG))
                msglis.append(struct.pack("B", size))
            for item in msgobj:
                GMConnect.packobj(item, msglis)
        elif t == type(set()):
            size = len(msgobj)
            if size > MAX_UINT8:
                msglis.append(struct.pack("b", BIG_SET_FLAG))
                msglis.append(struct.pack("H", size))
            else:
                msglis.append(struct.pack("b", SMALL_SET_FLAG))
                msglis.append(struct.pack("B", size))
            for item in msgobj:
                GMConnect.packobj(item, msglis)
        elif t == types.DictType:
            size = len(msgobj)
            if size > MAX_UINT8:
                msglis.append(struct.pack("b", BIG_DICT_FLAG))
                msglis.append(struct.pack("H", size))
            else:
                msglis.append(struct.pack("b", SMALL_DICT_FLAG))
                msglis.append(struct.pack("B", size))
            for key, value in msgobj.iteritems():
                GMConnect.packobj(key, msglis)
                GMConnect.packobj(value, msglis)
        elif t == types.StringType:
            size = len(msgobj)
            if size > MAX_UINT16:
                msglis.append(struct.pack("b", SUPER_BIG_STRING_FLAG))
                msglis.append(struct.pack("I", size))
            elif size > MAX_UINT8:
                msglis.append(struct.pack("b", BIG_STRING_FLAG))
                msglis.append(struct.pack("H", size))
            else:
                msglis.append(struct.pack("b", SMALL_STRING_FLAG))
                msglis.append(struct.pack("B", size))
            msglis.append(msgobj)
        elif t == datetime.datetime:
            msglis.append(struct.pack("b", DATETIME_FLAG))
            msglis.append(struct.pack("H", msgobj.year))
            msglis.append(struct.pack("H", msgobj.month))
            msglis.append(struct.pack("H", msgobj.day))
            msglis.append(struct.pack("H", msgobj.hour))
            msglis.append(struct.pack("H", msgobj.minute))
            msglis.append(struct.pack("H", msgobj.second))
        else:
            if getattr(msgobj, "ok", None):
                if type(msgobj.net_data) is str:
                    msglis.append(struct.pack("b", CLASS_OBJ_FLAG2))
                    msglis.append(struct.pack("H", msgobj.cls_id))
                    msglis.append(struct.pack("H", len(msgobj.net_data)))
                    msglis.append(msgobj.net_data)
                else:
                    msglis.append(struct.pack("b", CLASS_OBJ_FLAG))
                    msglis.append(struct.pack("H", msgobj.cls_id))
                    GMConnect.packobj(msgobj.net_data, msglis)
            else:
                print "unpack type", t, msgobj
                assert False


    def gmcommand(self, command):
        self.sendobj(PyMsg_GMRequest, command)
        msgType, body = self.recvobj()
        assert msgType == PyMsg_GMResponse
        return body
    

plat = 'qq'
id = '432'
script_dir = os.path.dirname(os.path.realpath(__file__))
conf_file = script_dir + r'/conf/%s_%s.conf'  %(plat,id)
conf = ConfigObj(conf_file)
#ip = conf['intranet_ip']
#Logic_port = conf['Logic_port']
#D_port = 10000 + int(id)
#merge_zids = conf['merge_zids']
ip = '121.42.176.120'
port = 24044
command = 'kill()'
process_key = 'logic'
gm = GMConnect(ip, port, True if process_key.startswith("logic") else False)
gm.iamgm()
gm.gmcommand(command)
