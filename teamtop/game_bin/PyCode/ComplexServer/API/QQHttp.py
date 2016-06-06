#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.API.QQHttp")
#===============================================================================
# 腾讯HTTP访问
#===============================================================================
import hmac
import time
import uuid
import urllib
import socket
import struct
import hashlib
import cProcess
import cDateTime
import Environment
from Common import CValue
from ComplexServer.Plug.DB import DBHelp
from ComplexServer.Plug.Http import HttpProxy
from Game.Role.Data import EnumDisperseInt32, EnumTempInt64

#服务器
# from ComplexServer.API import QQHttp; QQHttp.host(0)#把模拟服切换成沙箱

#本机 C:\Windows\System32\drivers\etc\hosts
#设置host 112.90.139.30 upayportal.qq.com


APP_ID = 100718848
APP_KEY = "4143da300a2a6c962e54f66dc373ef0e"
SECRET = APP_KEY + "&"

HOST = "openapi.tencentyun.com"

#union-10131 微端登录
PFD = {"qzone":1, "pengyou":2, "tapp":3, "qplus":4,  "qqgame":10,"3366":11, "website":12, "union-10131-1": 17, "union-10131-8":1}

#(1,'QQ空间')
#(2,'腾讯朋友')
#(3,'腾讯微博')
#(4,'腾讯QPlus')
#(8,'手机空间')
#(9,'手机朋友')
#(10,'QQ游戏')
#(11,'3366')
#(12,'游戏官网')
#(13,'iOS')
#(14,'Android')
#(15,'漫游')
#(16,'游戏人生')
#(17,'腾讯游戏联盟')
#(23,'腾讯游戏盒子')
#(101,'开心网')
#(888,心悦)


QREPORT_HOST = "tencentlog.com"

QQLOG_HOST = "183.61.46.225"
QQLOG_URI = "/report.php"

def host(b = True):
	global HOST
	if b:
		HOST = "openapi.tencentyun.com"#现网
	else:
		HOST = "119.147.19.43"#沙箱

def get_domain(pf):
	#APP所在平台，用于区分用户从哪个业务平台进入应用
	domain = PFD.get(pf, 0)
	if domain:
		return domain
	if pf.startswith("union"):
		#游戏联盟
		return 17
	return 0

def RoleId2UserId(roleid):
	sid, idx = divmod(roleid, CValue.P2_32)
	#最多2000个服务器？
	return idx * 2000 + sid

def has_hz(pf):
	pass

def has_lz(pf):
	pass

# 腾讯接口签名
def make_sig(uri, get, post):
	if post:
		method = "POST"
		params = post
	else:
		method = "GET"
		params = get
	keys = params.keys()
	keys.sort()
	list_parms = map(lambda it: '%s=%s' % (it, str(params[it])), keys)
	str_params = urllib.quote('&'.join(list_parms),'')
	source = "%s&%s&%s" % (method, urllib.quote(uri,''), str_params)
	hashed = hmac.new(SECRET, source, hashlib.sha1)
	# 这里多了换行符，要去掉
	sig = hashed.digest().encode("base64")[:-1]
	params["sig"] = sig

# IP转为整数
def ip_int(ip):
	try:
		return struct.unpack("I", socket.inet_aton(ip))[0]
	except:
		return 0

def IIP():
	return ip_int(Environment.IP)

# 发送Http请求
def query(uri, get, post, backfun, regparam):
	if Environment.EnvIsQQ():
		make_sig(uri, get, post)
		HttpProxy.HttpRequest(HOST, 80, uri, get, post, 20, backfun, regparam)
	else:
		backfun(None, regparam)

def query2(uri, get, post, backfun, regparam):
	if Environment.EnvIsQQ():
		HttpProxy.HttpRequest(QREPORT_HOST, 80, uri, get, post, 20, backfun, regparam)
	elif backfun:
		backfun(None, regparam)

def query_log(get, post, backfun, regparam):
	if Environment.EnvIsQQ():
		HttpProxy.HttpRequest(QQLOG_HOST, 80, QQLOG_URI, get, post, 20, backfun, regparam)
	elif backfun:
		backfun(None, regparam)

#####################################################################################
#基础接口
#####################################################################################
# 获取帐号信息
def get_info(openid, openkey, pf, backfun, regparam):
	uri = "/v3/user/get_info"
	if pf == "qqgame":
		#qqgame 要增加flag 参数  获取昵称和蓝钻数据
		get = {"appid":APP_ID, "openid":openid, "openkey":openkey, "pf":pf, "format":"json", "flag" : 3}
	else:
		get = {"appid":APP_ID, "openid":openid, "openkey":openkey, "pf":pf, "format":"json"}
	query(uri, get, None, backfun, regparam)

# 获取vip信息
def get_vip(openid, openkey, pf, backfun, regparam):
	uri = "/v3/user/total_vip_info"
	get = {"appid":APP_ID, "openid":openid, "openkey":openkey, "pf":pf, "format":"json"}
	query(uri, get, None, backfun, regparam)

# 是否登录
def is_login(openid, openkey, pf, backfun, regparam):
	uri = "/v3/user/is_login"
	get = {"appid":APP_ID, "openid":openid, "openkey":openkey, "pf":pf}
	query(uri, get, None, backfun, regparam)

# 是否VIP
def is_vip(openid, openkey, pf, backfun, regparam):
	uri = "/v3/user/is_vip"
	get = {"appid":APP_ID, "openid":openid, "openkey":openkey, "pf":pf}
	query(uri, get, None, backfun, regparam)

# 关键字屏蔽
def word_filter(openid, openkey, pf, content, backfun, regparam):
	uri = "/v3/csec/word_filter"
	get = {"appid":APP_ID, "openid":openid, "openkey":openkey, "pf":pf, "content":content, "msgid":str(uuid.uuid4()), "format":"json"}
	query(uri, get, None, backfun, regparam)

# 邀请验证
def verify_invkey(openid, openkey, pf, invkey, itime, iopenid, backfun, regparam):
	uri = "/v3/spread/verify_invkey"
	get = {"appid":APP_ID, "openid":openid, "openkey":openkey, "pf":pf, "invkey":invkey, "itime":itime, "iopenid":iopenid}
	query(uri, get, None, backfun, regparam)

# app是否在面板上
def is_app_onpanel(openid, openkey, pf, backfun, regparam):
	uri = "/v3/spread/is_app_onpanel"
	get = {"appid":APP_ID, "openid":openid, "openkey":openkey, "pf":pf}
	query(uri, get, None, backfun, regparam)

# 获取token信息
def get_token(openid, openkey, pf, pfkey, tokentype, discountid, roleid, backfun, regparam):
	uri = "/v3/pay/get_token"
	get = {"openid":openid, "openkey":openkey, "pf":pf, "pfkey":pfkey, "tokentype":tokentype,
		"discountid":discountid, "zoneid": DBHelp.GetDBIDByRoleID(roleid), "appid":APP_ID,
		"ts":int(time.time()), "version":"v3"}
	query(uri, get, None, backfun, regparam)

# 检测任务状态
def check_task_status(openid, openkey, pf, backfun, regparam):
	uri = "/v3/pay/check_task_status"
	get = {"openid":openid, "openkey":openkey, "pf":pf}
	query(uri, get, None, backfun, regparam)

# 检查cdkey绑定状态
def check_cdk(openid, openkey, pf, userip, cdkey, backfun, regparam):
	uri = "/v3/user/get_user_cdkey_info"
	get = {"openid":openid, "openkey":openkey, "pf":pf, "appid":APP_ID, "userip":ip_int(userip), "cdkey":cdkey, "format":"json"}
	query(uri, get, None, backfun, regparam)

# 获取心悦vip信息
def get_xinyue_vip(openid, openkey, pf, userip, backfun, regparam):
	uri = "/v3/user/get_xinyue_info"
	get = {"appid":APP_ID, "openid":openid, "openkey":openkey, "pf":pf, "userip":ip_int(userip), "format":"json"}
	query(uri, get, None, backfun, regparam)

#http://tencentlog.com/v3/user/get_xinyue_info?appid=100718848&openid=123&openkey=openkey&pf=888
#####################################################################################
#罗盘
#####################################################################################
#腾讯罗盘上报登录
def report_login(openid, pf, userip, roleid, source, level, backfun, regparam):
	get = {"appid":APP_ID, "userip":ip_int(userip), "svrip":IIP(),
			"domain":get_domain(pf), "worldid":cProcess.ProcessID, "opuid":RoleId2UserId(roleid),
			"opopenid":openid, "source":source, "level":level, "time":cDateTime.Seconds()}
	query2("/stat/report_login.php", get, None, backfun, regparam)
	return get
	
#腾讯罗盘上报主动注册
def report_register(openid, pf, userip, roleid, source, backfun, regparam):
	get = {"appid":APP_ID, "userip":ip_int(userip), "svrip":IIP(),
			"domain":get_domain(pf), "worldid":cProcess.ProcessID, "opuid":RoleId2UserId(roleid),
			"opopenid":openid, "source":source, "time":cDateTime.Seconds()}
	
	query2("/stat/report_register.php", get, None, backfun, regparam)

#腾讯罗盘上报接受邀请注册
def report_accept(openid, pf, userip, roleid, source, backfun, regparam):
	host = "http://tencentlog.com"
	get = {"appid":APP_ID, "userip":ip_int(userip), "svrip":IIP(),
		"domain":get_domain(pf), "worldid":cProcess.ProcessID, "opuid":RoleId2UserId(roleid),
		"opopenid":openid, "source":source, "time":cDateTime.Seconds()}
	query2("/stat/report_accept.php", get, None, backfun, regparam)

#腾讯罗盘上报邀请他人注册应用
def report_invite(openid, pf, userip, roleid, source, backfun, regparam):
	get = {"appid":APP_ID, "userip":ip_int(userip), "svrip":IIP(),
		"domain":get_domain(pf), "worldid":cProcess.ProcessID, "opuid":RoleId2UserId(roleid),
		"opopenid":openid, "source":source, "time":cDateTime.Seconds()}
	query2("/stat/report_invite.php", get, None, backfun, regparam)

#腾讯罗盘上报上报用户在应用中进行支付消费
def report_consume(openid, pf, userip, roleid, source, modifyfee, itemtype, itemcnt, backfun, regparam):
	get = {"appid":APP_ID, "userip":ip_int(userip), "svrip":IIP(),
		"domain":get_domain(pf), "worldid":cProcess.ProcessID, "opuid":RoleId2UserId(roleid),
		"opopenid":openid, "source":source, "time":cDateTime.Seconds(),
		"itemtype":itemtype, "itemcnt": itemcnt, "modifyfee" : modifyfee}
	query2("/stat/report_consume.php", get, None, backfun, regparam)

#腾讯罗盘上报用户退出应用
def report_quit(openid, pf, userip, roleid, source, level, onlinetime, backfun, regparam):
	get = {"appid":APP_ID, "userip":ip_int(userip), "svrip":IIP(),
		"domain":get_domain(pf), "worldid":cProcess.ProcessID, "opuid":RoleId2UserId(roleid),
		"opopenid":openid, "source":source, "time":cDateTime.Seconds(),
		"level":level, "onlinetime":onlinetime}
	query2("/stat/report_quit.php", get, None, backfun, regparam)
	return get

#腾讯罗盘上报充值
def report_recharge(openid, pf, userip, roleid, source, modifyfee, itemtype, itemcnt, backfun, regparam):
	get = {"appid":APP_ID, "userip":ip_int(userip), "svrip":IIP(),
		"domain":get_domain(pf), "worldid":cProcess.ProcessID, "opuid":RoleId2UserId(roleid),
		"opopenid":openid, "source":source, "time":cDateTime.Seconds(),
		"itemtype":itemtype, "itemcnt": itemcnt, "modifyfee" : modifyfee}
	query2("/stat/report_recharge.php", get, None, backfun, regparam)

#腾讯罗盘上报实时在线
def report_online(pf, user_num, backfun, regparam):
	get = {"appid":APP_ID, "userip":IIP(), "svrip":IIP(),
		"domain":get_domain(pf), "worldid":cProcess.ProcessID, "time":cDateTime.Seconds(),
		"user_num" : user_num}
	query2("/stat/report_online.php", get, None, backfun, regparam)

#####################################################################################
#回流用户
#####################################################################################
#流失用户回归
def get_app_flag(openid, openkey, pf, userip, backfun, regparam):
	uri = "/v3/user/get_app_flag"
	get = {"appid":APP_ID, "openid":openid, "openkey":openkey, "pf":pf, "userip":ip_int(userip), "format":"json"}
	query(uri, get, None, backfun, regparam)

#删除流失用户标识
def del_app_flag(openid, openkey, pf, userip, acttype, usergroupid, backfun, regparam):
	uri = "/v3/user/del_app_flag"
	get = {"appid":APP_ID, "openid":openid, "openkey":openkey, "pf":pf, "userip":ip_int(userip), "acttype":acttype, "usergroupid":usergroupid, "format":"json"}
	query(uri, get, None, backfun, regparam)

#####################################################################################
#暑期活动
#####################################################################################
def summer_task(openid, openkey, pf, userip, task_id,  backfun, regparam):
	uri = "/v3/user/set_playzone_task"
	get = {"appid":APP_ID, "openid":openid, "openkey":openkey, "pf":pf, "userip":ip_int(userip), "task_id":task_id, "source_id":10000454, "cmd":1, "format":"json"}
	query(uri, get, None, backfun, regparam)


##################################################################################
#TDW上报日志
##################################################################################
#创建角色日志
#iappid		应用ID (100718848)
#idomain		平台ID(888)
#ioptype			类型(0)
#iactionid		子类型(0)
#iworldid		大区id 
#vuin			openid
#iuserip			客户端ip主机字节序
#ieventTime		时间 unix 时间戳
#iroleId			角色id
#ijobId			角色职业
def QLog_CreateRole(role, pf, openid, serverId,  userip, backfun, regparam):
	#大区ID，由于1-255在有特殊的用途，所有上报worldid都+255，这个规则需要对所有上报的表生效。
	serverId += 255
	get = {"iappid":APP_ID, "idomain":888, "ioptype":0, "iactionid":0,\
		"iworldid":serverId, "vuin":openid, "userip":ip_int(userip), "ieventTime":cDateTime.Seconds(), \
		"iroleId":role.GetRoleID(), "ijobId":role.GetCareer(), "format":"json"}
	query_log(get, None, backfun, regparam)

#角色登入日志
#iappid		应用ID (100718848)
#idomain		平台ID(888)
#ioptype		类型(1)
#iactionid		子类型(0)
#iworldid		大区id
#vuin			openid
#iuserip		客户端ip主机字节序
#ieventTime		时间 unix 时间戳
#iroleId		角色id
#ijobId			角色职业
#ilevel			角色等级
#vparam_1		角色经验值
#iparam_16		角色金币
#iparam_17		角色绑定金币(魔晶)
#iparam_18		角色传奇币(充值神石)
#iparam_19		角色礼金(系统神石)
#iparam_20		角色创建时间unix 时间戳
#iparam_1		玩家总共在线时长(秒)

def QLog_Login(role, pf, openid, serverId,  userip, backfun, regparam):
	#大区ID，由于1-255在有特殊的用途，所有上报worldid都+255，这个规则需要对所有上报的表生效。
	serverId += 255
	get = {"iappid":APP_ID, "idomain":888, "ioptype":1, "iactionid":0,\
		"iworldid":serverId, "vuin":openid, "userip":ip_int(userip), "ieventTime":cDateTime.Seconds(), \
		"iroleId":role.GetRoleID(), "ijobId":role.GetCareer(), "ilevel": role.GetLevel(), \
		"vparam_1":role.GetExp(), "iparam_16":role.GetMoney(), "iparam_17":role.GetBindRMB(), \
		"iparam_18":role.GetUnbindRMB_Q(),"iparam_19":role.GetUnbindRMB_S(),"iparam_20" : role.GetDI32(EnumDisperseInt32.FirstLoginTimes),\
		"iparam_1":role.GetDI32(EnumDisperseInt32.enOnlineTimes), "format":"json"}
	query_log(get, None, backfun, regparam)


#角色登出日志
#iappid		应用ID (100718848)
#idomain		平台ID(888)
#ioptype			类型(1)
#iactionid		子类型(1)
#iworldid		大区id
#vuin			openid
#iuserip			客户端ip主机字节序
#ieventTime		时间 unix 时间戳
#iroleId			角色id
#ijobId			角色职业
#ilevel			角色等级
#vparam_1		角色经验值
#iparam_16		角色金币
#iparam_17		角色(魔晶)
#iparam_18		角色(充值神石)
#iparam_19		角色(系统神石)
#iparam_20		角色登陆时间unix 时间戳
#iparam_1		玩家本次在线时长(秒)

def QLog_Exit(role, pf, openid, serverId,  userip, backfun, regparam):
	#大区ID，由于1-255在有特殊的用途，所有上报worldid都+255，这个规则需要对所有上报的表生效。
	serverId += 255
	get = {"iappid":APP_ID, "idomain":888, "ioptype":1, "iactionid":1,\
		"iworldid":serverId, "vuin":openid, "userip":ip_int(userip), "ieventTime":cDateTime.Seconds(), \
		"iroleId":role.GetRoleID(), "ijobId":role.GetCareer(), "ilevel": role.GetLevel(), \
		"vparam_1":role.GetExp(), "iparam_16":role.GetMoney(), "iparam_17":role.GetBindRMB(), \
		"iparam_18":role.GetUnbindRMB_Q(),"iparam_19":role.GetUnbindRMB_S(),"iparam_20" : role.GetDI32(EnumDisperseInt32.FirstLoginTimes),\
		"iparam_1":role.GetTI64(EnumTempInt64.LoginOnlineTime), "format":"json"}
	query_log(get, None, backfun, regparam)

#在线角色数量统计
#iappid			应用ID
#idomain			平台ID
#ioptype			类型(2)
#iactionid		子类型(0)
#ieventTime		时间 unix 时间戳
#iworldid		大区id
#iparam_1		当前在线数量
def QLog_OnlineCnt(pf, serverId, cnt, backfun, regparam):
	#大区ID，由于1-255在有特殊的用途，所有上报worldid都+255，这个规则需要对所有上报的表生效。
	serverId += 255
	get = {"iappid":APP_ID, "idomain":888, "ioptype":2, "iactionid":0,\
		"iworldid":serverId,  "ieventTime":cDateTime.Seconds(), \
		"iparam_1":cnt, "format":"json"}
	query_log(get, None, backfun, regparam)


#商城购买日志
#iappid			应用ID
#idomain			平台ID
#ioptype			类型(3)
#iactionid		子类型(0)
#iworldid		大区id
#vuin			openid
#iuserip			客户端ip主机字节序
#ieventTime		时间 unix 时间戳
#iroleId			角色id
#iparam_1		支付类型 如：1:元宝 2:铜币 3:礼金
#iparam_2		支付消耗
#iparam_3		商品类型
#iparam_16		商品ID
#vparam_1		商品名称
#iparam_4		商品数量
#vreserve_1		流水号

def QLog_Consume(role, pf, openid, serverId,  userip, consumeType, consumePrice, goodsType, goodsId, goodsCnt, goodsName, backfun, regparam, vreserve_1 = 0):
	#大区ID，由于1-255在有特殊的用途，所有上报worldid都+255，这个规则需要对所有上报的表生效。
	serverId += 255
	get = {"iappid":APP_ID, "idomain":888, "ioptype":3, "iactionid":0,\
		"iworldid":serverId, "vuin":openid, "userip":ip_int(userip), "ieventTime":cDateTime.Seconds(), \
		"iroleId":role.GetRoleID(), "iparam_1":consumeType, "iparam_2": consumePrice, \
		"iparam_3":goodsType, "iparam_16":goodsId, "vparam_1":goodsName, \
		"iparam_4":goodsCnt,"vreserve_1" : vreserve_1, "format":"json"}
	query_log(get, None, backfun, regparam)


#大区信息列表--注意上报的数据的时候如果大于等于255的有加1，这里上报的时候要同样加1.
#iappid			应用ID
#idomain			填0
#ioptype			类型(4)
#iactionid		子类型(0)
#ieventTime		时间  当天的日期的unix 时间戳
#iworldid		大区id
#vparam_1		大区名称
#iparam_1                大区容量
#iparam_2                大区IDC ID 没有IDC就填0
#vparam_2                大区IDC名称 没有填空串
#vparam_3                大区开服日期

def QLog_ServerInfo(serverId, serverName, maxOnlineCnt,kaifuTime, backfun, regparam):
	#大区ID，由于1-255在有特殊的用途，所有上报worldid都+255，这个规则需要对所有上报的表生效。
	serverId += 255
	get = {"iappid":APP_ID, "idomain":0, "ioptype":4, "iactionid":0,\
		"iworldid":serverId, "ieventTime":cDateTime.Seconds(), "vparam_1":serverName, \
		"iparam_1":maxOnlineCnt, "iparam_2":0, "vparam_2":"", "vparam_3":kaifuTime, "format":"json"}
	query_log(get, None, backfun, regparam)


#增加一个特性表   心悦道具领取流水日志表
#iappid		应用ID (100718848)
#idomain		平台ID(888)
#iuserip		客户端ip主机字节序
#ioptype		类型(10)
#iactionid	子类型(0)
#iworldid	大区id
#vuin		openid
#ieventTime	时间 unix 时间戳
#iroleId		角色id
#iparam_1	特权礼包物品ID
#iparam_2	特权礼包物品数量
def QLog_XinYueLiBao(role, openid, serverId, pf, itemid, itemnum, backfun, regparam):
	serverId += 255
	get = {"iappid":APP_ID, "idomain":888, "ioptype":10, "iactionid":0,\
		"iworldid":serverId, "vuin":openid, "ieventTime":cDateTime.Seconds(), \
		"iroleId":role.GetRoleID(), "iparam_1":itemid, "iparam_2": itemnum, "format":"json"}
	query_log(get, None, backfun, regparam)


