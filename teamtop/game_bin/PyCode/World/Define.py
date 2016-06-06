#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("World.Define")
#===============================================================================
# 游戏世界定义
#===============================================================================
import Environment

#模拟服替换全局http为后台http，每次更新的时候，需要测试就要执行这个指令
#import World.Define as A
#A.Web_Global_IP = A.Web_HouTai_IP
#A.Web_Global_Port = A.Web_HouTai_Port
#关于django时区
#http://en.wikipedia.org/wiki/List_of_tz_database_time_zones

if "_HasLoad" not in dir():
	DefaultCrossID = None
	CrossID_2 = None
	
def BuildProcessKey(ptype, pid):
	return "%s%s" % (ptype, pid)

def IsControlProcessKey(pkey):
	return pkey.startswith("C")


def GetDefaultCrossID():
	#获取默认的跨服ID
	global DefaultCrossID
	if DefaultCrossID is None:
		import cProcess
		if cProcess.ProcessID in TestWorldIDs:
			DefaultCrossID = DefaultCrossID_Test
		else:
			DefaultCrossID = DefaultCrossID_Normal
	return DefaultCrossID

def GetCrossID_2():
	#获取第二个跨服服务器ID
	global CrossID_2
	if CrossID_2 is None:
		import cProcess
		if cProcess.ProcessID in TestWorldIDs:
			CrossID_2 = CrossID_Test_2
		else:
			CrossID_2 = CrossID_Normal_2
	return CrossID_2

#游戏联盟特殊
Unoin_Web_Global_MySQL = ("1.4.14.176", 1026, "root", "3edc4rfv")

if Environment.IsDevelop:
	#开发环境
	#全局HTTP
	Web_Global_MySQL = ("192.168.8.108", 3306, "root", "^O$11;`)_FWz")
	Web_Global_IP = "192.168.8.110"
	Web_Global_Port = 8000
	#后台
	Web_HouTai_MySQL = ("192.168.8.108", 3306, "root", "^O$11;`)_FWz")
	Web_HouTai_IP = "192.168.8.110"
	Web_HouTai_Port = 8000
	#语言版本 默认， 北美英文， 繁体
	Language = ["default", "english", "ft", "rumsk", "tk", "pl", "fr", "en", "esp", "yy", "sasia", "rutt"]
	#测试服ID 
	TestWorldIDs = set(xrange(60000))
	
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30001
	#默认的跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30006
	CrossID_Normal_2 = 30006
	CrossWorlds = {30001 : ("192.168.8.108", 9004),
				30006 : ("192.168.8.108", 9006)}
	
	if Environment.IP == "192.168.8.167":
		pass
		DefaultCrossID_Test = 30167
		#默认的跨服服务器ID
		DefaultCrossID_Normal = 30167
		#第二组跨服服务器ID
		CrossID_Test_2 = 30002
		CrossID_Normal_2 = 30002
		CrossWorlds = {30167 : ("192.168.8.167", 10167)}
	elif Environment.IP == "192.168.8.157":
		DefaultCrossID_Test = 30030
		#默认的跨服服务器ID
		DefaultCrossID_Normal = 30030
		#第二组跨服服务器ID
		CrossID_Test_2 = 30011
		CrossID_Normal_2 = 30011
		CrossWorlds = {30030 : ("192.168.8.157",10011)}
	elif Environment.IP == "192.168.8.81":
		DefaultCrossID_Test = 30081
		#默认的跨服服务器ID
		DefaultCrossID_Normal = 30081
		#第二组跨服服务器ID
		CrossID_Test_2 = 30002
		CrossID_Normal_2 = 30002
		CrossWorlds = {30081 : ("192.168.8.81", 9081)}
	elif Environment.IP == "192.168.8.169":
		DefaultCrossID_Test = 30007
		#默认的跨服服务器ID
		DefaultCrossID_Normal = 30007
		#第二组跨服服务器ID
		CrossID_Test_2 = 30002
		CrossID_Normal_2 = 30002
		CrossWorlds = {30007 : ("192.168.8.169", 9007)}
	elif Environment.IP == "192.168.8.58":
		if Environment.EnvIsNA():
			DefaultCrossID_Test = 30188
			#默认的跨服服务器ID
			DefaultCrossID_Normal = 30188
			#第二组跨服服务器ID
			CrossID_Test_2 = 30002
			CrossID_Normal_2 = 30002
			CrossWorlds = {30188 : ("192.168.8.58", 9188)}
		else:
			DefaultCrossID_Test = 30189
			#默认的跨服服务器ID
			DefaultCrossID_Normal = 30189
			#第二组跨服服务器ID
			CrossID_Test_2 = 30189
			CrossID_Normal_2 = 30189
			CrossWorlds = {30189 : ("192.168.8.58", 30189)}
	elif Environment.IP == "192.168.8.25":
		if Environment.IsRUMSK:
			DefaultCrossID_Test = 31201
			#本地俄罗斯跨服
			DefaultCrossID_Normal = 31201
			#第二组跨服服务器ID
			CrossID_Test_2 = 31201
			CrossID_Normal_2 = 31201
			CrossWorlds = {31201 : ("192.168.8.25", 31201)}
		elif Environment.EnvIsPL():
			DefaultCrossID_Test = 31203
			#本地俄罗斯跨服
			DefaultCrossID_Normal = 31203
			#第二组跨服服务器ID
			CrossID_Test_2 = 31203
			CrossID_Normal_2 = 31203
			CrossWorlds = {31203 : ("192.168.8.25", 31203)}
		else:
			DefaultCrossID_Test = 30003
			#本地国服跨服
			DefaultCrossID_Normal = 30003
			#第二组跨服服务器ID
			CrossID_Test_2 = 30003
			CrossID_Normal_2 = 30003
			CrossWorlds = {30003 : ("192.168.8.25", 30003)}
	elif Environment.IP == "192.168.8.120":
		DefaultCrossID_Test = 30020
		#本地国服跨服
		DefaultCrossID_Normal = 30020
		#第二组跨服服务器ID
		CrossID_Test_2 = 30020
		CrossID_Normal_2 = 30020
		CrossWorlds = {30020 : ("192.168.8.120", 10086)}
	elif Environment.IP == "192.168.8.49":
		if Environment.EnvIsTK():
			DefaultCrossID_Test = 30035
			#本地土耳其跨服
			DefaultCrossID_Normal = 30035
			#第二组跨服服务器ID
			CrossID_Test_2 = 30035
			CrossID_Normal_2 = 30035
			CrossWorlds = {30035 : ("192.168.8.49", 10036)}
		elif Environment.EnvIsFT():
			DefaultCrossID_Test = 30025
			#本地繁体跨服
			DefaultCrossID_Normal = 30025
			#第二组跨服服务器ID
			CrossID_Test_2 = 30025
			CrossID_Normal_2 = 30025
			CrossWorlds = {30025 : ("192.168.8.49", 10026)}
		else:
			DefaultCrossID_Test = 30015
			#本地国服跨服
			DefaultCrossID_Normal = 30015
			#第二组跨服服务器ID
			CrossID_Test_2 = 30015
			CrossID_Normal_2 = 30015
			CrossWorlds = {30015 : ("192.168.8.49", 10016)}
	
	elif Environment.IP == "192.168.8.142":
		
		DefaultCrossID_Test = 30049
		#默认的跨服服务器ID
		DefaultCrossID_Normal = 30049
		#第二组跨服服务器ID
		CrossID_Test_2 = 30049
		CrossID_Normal_2 = 30049
		CrossWorlds = {30049 : ("192.168.8.142",10008)}
	#Django时区
	TimeZone = "Asia/Shanghai"
	#SQL时区修正
	SQL_TIME_ZONE = None
	SQL_TIME_ZONE_DST = None

elif Environment.IsQQ:
	#腾讯
	Web_Global_MySQL = ("1.4.14.176", 1026, "root", "3edc4rfv")
	Web_Global_IP = "10.207.150.240"
	Web_Global_Port = 9001
	Web_HouTai_MySQL = ("1.4.14.176", 1025, "root", "1qaz2wsx")
	Web_HouTai_IP = "10.207.149.29"
	Web_HouTai_Port = 8008
	Language = ["default"]
	TestWorldIDs = set([2, 3, 7, 30000, 30003])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30003
	CrossID_Normal_2 = 30002
	#跨服连接数据
	CrossWorlds = {30000 : ("kuafutest.app100718848.twsapp.com", 8002),
					30001 : ("kuafu.app100718848.twsapp.com", 8002),
					30002 : ("kuafu.app100718848.twsapp.com", 8003),
					30003 : ("kuafutest.app100718848.twsapp.com", 8003)
					}
	#Django时区
	TimeZone = "Asia/Shanghai"
	#SQL时区修正
	SQL_TIME_ZONE = None
	SQL_TIME_ZONE_DST = None

elif Environment.IsQQUnion:
	#腾讯游戏联盟(全局和后台用同一个) 修改是麻烦全局查询一下这些信息，因为idip写死了2个这样的接口
	Web_Global_MySQL = ("1.4.14.176", 1026, "root", "3edc4rfv")
	Web_Global_IP = "10.207.141.155"
	Web_Global_Port = 9001
	Web_HouTai_MySQL = ("1.4.14.176", 1025, "root", "1qaz2wsx")
	Web_HouTai_IP = "10.207.141.155"
	Web_HouTai_Port = 8008
	Language = ["default"]
	TestWorldIDs = set([2, 3, 7])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30000
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {30000:("kuafuunion.app100718848.twsapp.com", 8002),
					30002:("kuafuunion.app100718848.twsapp.com", 8003)
				}
	#Django时区
	TimeZone = "Asia/Shanghai"
	#SQL时区修正
	SQL_TIME_ZONE = None
	SQL_TIME_ZONE_DST = None

elif Environment.IsNA:
	#北美自营
	Web_Global_MySQL = ("legendknight-db-01.comcophxmzkh.us-west-2.rds.amazonaws.com", 3306, "lkService", "czuWj827ovq")
	Web_Global_IP = "172.31.45.107"
	Web_Global_Port = 9001 #内网可以访问  外网可以访问  http://global.legendknight.com:8000
	Web_HouTai_MySQL = ("legendknight-db-01.comcophxmzkh.us-west-2.rds.amazonaws.com", 3306, "lkService", "czuWj827ovq")
	Web_HouTai_IP = "172.31.39.96"
	Web_HouTai_Port = 8008
	Language = ["english"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {30000:("54.201.126.154", 8004),
					30001:("54.186.169.197", 8000)}
	#Django时区
	TimeZone = "America/Whitehorse"
	#SQL时区修正(注意北美有夏令时)
	SQL_TIME_ZONE = "set time_zone = '-8:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '-7:00';"


elif Environment.IsKGG:
	#北美联运kgg
	Web_Global_MySQL = ("legendknight-db-kgg-global.comcophxmzkh.us-west-2.rds.amazonaws.com", 3306, "lkRoot", "jEsm8K2eW708E9in")
	Web_Global_IP = "172.31.45.109"
	Web_Global_Port = 9001 
	Web_HouTai_MySQL = ("legendknight-db-kgg-global.comcophxmzkh.us-west-2.rds.amazonaws.com", 3306, "lkRoot", "jEsm8K2eW708E9in")
	Web_HouTai_IP = "172.31.45.110"
	Web_HouTai_Port = 8008
	Language = ["english"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {30001:("54.68.223.218", 8000)}
	#Django时区
	TimeZone = "America/Whitehorse"
	#SQL时区修正(注意北美有夏令时)
	SQL_TIME_ZONE = "set time_zone = '-8:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '-7:00';"

elif Environment.IsNAPLUS1:
	#北美plus1games联运
	Web_Global_MySQL = ("10.9.6.16", 3306, "root", "VFe6c7Cnaptest")
	Web_Global_IP = "lkna-global.plus1games.net"
	Web_Global_Port = 8008 
	Web_HouTai_MySQL = ("10.9.6.16", 3306, "root", "VFe6c7Cnaptest")
	Web_HouTai_IP = "lkna-global.plus1games.net"
	Web_HouTai_Port = 8008
	Language = ["english"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {30001:("54.68.223.218", 8000)}
	#Django时区
	TimeZone = "Turkey"
	#SQL时区修正(注意有夏令时)
	SQL_TIME_ZONE = "set time_zone = '+2:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+3:00';"
	
elif Environment.IsXP:
	#北美联运xp 伦敦
	Web_Global_MySQL = ("192.168.106.3", 3306, "root", "vaeTKS1101xp")
	Web_Global_IP = "na101xp-global.101xp.com"
	Web_Global_Port = 8008 
	Web_HouTai_MySQL = ("192.168.106.3", 3306, "root", "vaeTKS1101xp")
	Web_HouTai_IP = "na101xp-global.101xp.com"
	Web_HouTai_Port = 8008
	Language = ["english"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "Europe/London"
	#SQL时区修正(注意北美有夏令时)
	SQL_TIME_ZONE = "set time_zone = '+0:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+1:00';"


elif Environment.IsXPUSE:
	#北美联运xp 东部 
	Web_Global_MySQL = ("192.168.110.102", 3306, "root", "9WmVJANpqE")
	Web_Global_IP = "na101xp-use-global.101xp.com"
	Web_Global_Port = 8008 
	Web_HouTai_MySQL = ("192.168.110.102", 3306, "root", "9WmVJANpqE")
	Web_HouTai_IP = "na101xp-use-global.101xp.com"
	Web_HouTai_Port = 8008
	Language = ["english"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "America/New_York"
	#SQL时区修正(注意北美有夏令时)
	SQL_TIME_ZONE = "set time_zone = '-5:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '-4:00';"
	
elif Environment.IsXPUSW:
	#北美联运xp 西部
	Web_Global_MySQL = ("192.168.110.105", 3306, "root", "v72qGckCDgxpUSW")
	Web_Global_IP = "na101xp-usw-global.101xp.com"
	Web_Global_Port = 8008 
	Web_HouTai_MySQL = ("192.168.110.105", 3306, "root", "v72qGckCDgxpUSW")
	Web_HouTai_IP = "na101xp-usw-global.101xp.com"
	Web_HouTai_Port = 8008
	Language = ["english"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "America/Whitehorse"
	#SQL时区修正(注意北美有夏令时)
	SQL_TIME_ZONE = "set time_zone = '-8:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '-7:00';"

elif Environment.EnvIsFT():
	#繁体 都是内网地址 
	Web_Global_MySQL = ("192.168.11.149", 3306, "root", "tw2_J9_v&R_Em")
	Web_Global_IP = "192.168.11.149"
	Web_Global_Port = 9001
	Web_HouTai_MySQL = ("192.168.11.149", 3306, "root", "tw2_J9_v&R_Em")
	Web_HouTai_IP = "192.168.11.111"
	Web_HouTai_Port = 8008
	Language = ["ft"]
	
	TestWorldIDs = set([1002, 1003, 30000, 30003])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID 要外网ID，因为要发给客户端转登录
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30003
	CrossID_Normal_2 = 30002
	CrossWorlds = {30000 : ("220.130.123.111", 8003),
					30001 : ("220.130.123.148", 8000),
					30002:("220.130.123.148", 8002),
					30003:("220.130.123.111", 8005)}
	#Django时区
	TimeZone = "Asia/Shanghai"
	#SQL时区修正
	SQL_TIME_ZONE = None
	SQL_TIME_ZONE_DST = None


elif Environment.IsRUMSK:
	#俄罗斯莫斯科时区
	Web_Global_MySQL = ("192.168.137.3", 3306, "root", "YR6sxLMmsk1")
	Web_Global_IP = "msk-global.srv.dragonknight.ru"
	Web_Global_Port = 8008
	Web_HouTai_MySQL = ("192.168.137.3", 3306, "root", "YR6sxLMmsk1")
	Web_HouTai_IP = "msk-ver.srv.dragonknight.ru"
	Web_HouTai_Port = 8008
	Language = ["rumsk"]
	
	TestWorldIDs = set([1002, 1003, 1004, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID 要外网ID，因为要发给客户端转登录
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {30000 : ("92.222.103.1", 8003),
					30001 : ("178.33.25.220", 8001)}
	#Django时区
	TimeZone = "Europe/Moscow"
	#SQL时区修正
	SQL_TIME_ZONE = "set time_zone = '+3:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+3:00';"

elif Environment.IsRUSP:
	#俄罗斯(社交渠道)
	Web_Global_MySQL = ("192.168.137.5", 3306, "root", "KIueTg5Mh")
	Web_Global_IP = "sp-global.srv.dragonknight.ru"
	Web_Global_Port = 8008
	Web_HouTai_MySQL = ("192.168.137.5", 3306, "root", "KIueTg5Mh")
	Web_HouTai_IP = "92.222.103.7"
	Web_HouTai_Port = 8008
	Language = ["rumsk"]
	TestWorldIDs = set([1002, 1003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID 要外网ID，因为要发给客户端转登录
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {30001 : ("178.33.25.223", 8001)}
	#Django时区
	TimeZone = "Europe/Moscow"
	#SQL时区修正
	SQL_TIME_ZONE = "set time_zone = '+3:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+3:00';"


elif Environment.IsRUXP:
	#俄罗斯101xp
	Web_Global_MySQL = ("192.168.105.2", 3306, "root", "N92kMw3ruxp1")
	Web_Global_IP = "xp-global-srv.101xp.com"
	Web_Global_Port = 8008
	Web_HouTai_MySQL = ("192.168.105.2", 3306, "root", "N92kMw3ruxp1")
	Web_HouTai_IP = "xp-global-srv.101xp.com"
	Web_HouTai_Port = 8008
	Language = ["rumsk"]
	TestWorldIDs = set([1002, 1003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID 要外网ID，因为要发给客户端转登录
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {30001 : ("85.195.95.175", 8001)}
	#Django时区
	TimeZone = "Europe/Moscow"
	#SQL时区修正
	SQL_TIME_ZONE = "set time_zone = '+3:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+3:00';"

elif Environment.IsRURBK:
	#俄罗斯RBK
	Web_Global_MySQL = ("192.168.137.12", 3306, "root", "c8V5%m_rurbk1")
	Web_Global_IP = "192.168.137.12"
	Web_Global_Port = 9001
	Web_HouTai_MySQL = ("192.168.137.12", 3306, "root", "c8V5%m_rurbk1")
	Web_HouTai_IP = "192.168.137.12"
	Web_HouTai_Port = 9001
	Language = ["rumsk"]
	TestWorldIDs = set([1002, 1003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID 要外网ID，因为要发给客户端转登录
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {30001 : ("5.196.162.175", 8001)}
	#Django时区
	TimeZone = "Europe/Moscow"
	#SQL时区修正
	SQL_TIME_ZONE = "set time_zone = '+3:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+3:00';"

elif Environment.IsRUGN:
	#俄罗斯GameNet
	Web_Global_MySQL = ("192.168.137.22", 3306, "root", "Hab0og7irT2gn1")
	Web_Global_IP = "dkrugn-global.srv.dragonknight.ru"
	Web_Global_Port = 8008
	Web_HouTai_MySQL = ("192.168.137.22", 3306, "root", "Hab0og7irT2gn1")
	Web_HouTai_IP = "dkrugn-global.srv.dragonknight.ru"
	Web_HouTai_Port = 8008
	Language = ["rumsk"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID 要外网ID，因为要发给客户端转登录
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "Europe/Moscow"
	#SQL时区修正
	SQL_TIME_ZONE = "set time_zone = '+3:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+3:00';"
	
elif Environment.IsRUTT:
	#俄罗斯比赛服
	Web_Global_MySQL = ("192.168.137.30", 3306, "root", "iFyUZGXK3cYN")
	Web_Global_IP = "192.168.137.30"
	Web_Global_Port = 9001
	Web_HouTai_MySQL = ("192.168.137.30", 3306, "root", "iFyUZGXK3cYN")
	Web_HouTai_IP = "dkrutn-ver.srv.dragonknight.ru"
	Web_HouTai_Port = 8008
	Language = ["rutt"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID 要外网ID，因为要发给客户端转登录
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "Europe/Moscow"
	#SQL时区修正
	SQL_TIME_ZONE = "set time_zone = '+3:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+3:00';"
	
elif Environment.IsTK:
	#土耳其
	Web_Global_MySQL = ("192.168.107.3", 3306, "root", "Zgha2Mx6tur1")
	Web_Global_IP = "192.168.107.3"
	Web_Global_Port = 9001 
	Web_HouTai_MySQL = ("192.168.107.3", 3306, "root", "Zgha2Mx6tur1")
	Web_HouTai_IP = "beta01.salagame.com"
	Web_HouTai_Port = 8008
	Language = ["tk"]
	TestWorldIDs = set([10002, 10003, 10004, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {30000 : ("164.132.161.171", 8004),
					30001 : ("164.132.161.173", 8808)}
	#Django时区
	TimeZone = "Turkey"
	#SQL时区修正(注意有夏令时)
	SQL_TIME_ZONE = "set time_zone = '+2:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+3:00';"
elif Environment.IsTKPLUS1:
	#土耳其plus1联运
	Web_Global_MySQL = ("10.9.6.50", 3306, "root", "kE2nI8plus1_1")
	Web_Global_IP = "dkpl-global.plus1games.net"
	Web_Global_Port = 8008 
	Web_HouTai_MySQL = ("10.9.6.50", 3306, "root", "kE2nI8plus1_1")
	Web_HouTai_IP = "dkpl-global.plus1games.net"
	Web_HouTai_Port = 8008
	Language = ["tk"]
	TestWorldIDs = set([10002, 10003, 10004, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "Turkey"
	#SQL时区修正(注意有夏令时)
	SQL_TIME_ZONE = "set time_zone = '+2:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+3:00';"
elif Environment.IsTKESP:
	#土耳其Esprit联运
	Web_Global_MySQL = ("10.9.0.2", 3306, "root", "zE8KWb7tursp")
	Web_Global_IP = "dksp-tur-global.espritgames.com"
	Web_Global_Port = 8008 
	Web_HouTai_MySQL = ("10.9.0.2", 3306, "root", "zE8KWb7tursp")
	Web_HouTai_IP = "dksp-tur-global.espritgames.com"
	Web_HouTai_Port = 8008
	Language = ["tk"]
	TestWorldIDs = set([10002, 10003, 10004, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "Turkey"
	#SQL时区修正(注意有夏令时)
	SQL_TIME_ZONE = "set time_zone = '+2:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+3:00';"
	
elif Environment.IsPL:
	Web_Global_MySQL = ("192.168.32.170", 3306, "root", "K6s0IhaXpl1")
	Web_Global_IP = "192.168.32.170"
	Web_Global_Port = 9001 
	Web_HouTai_MySQL = ("192.168.32.170", 3306, "root", "K6s0IhaXpl1")
	Web_HouTai_IP = "dnpl-ver.salagame.com"
	Web_HouTai_Port = 8008
	Language = ["pl"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {30000:("164.132.161.169", 8806),
				30001:("46.105.116.222", 8808)}
	#Django时区
	TimeZone = "Poland"
	#SQL时区修正(注意有夏令时)
	SQL_TIME_ZONE = "set time_zone = '+1:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+2:00';"
	
elif Environment.IsPLXP:
	Web_Global_MySQL = ("192.168.115.3", 3306, "root", "ETy3qH7pK5@plxp")
	Web_Global_IP = "xp-dkpl-global.101xp.com"
	Web_Global_Port = 8008
	Web_HouTai_MySQL = ("192.168.115.3", 3306, "root", "ETy3qH7pK5@plxp")
	Web_HouTai_IP = "xp-dkpl-global.101xp.com"
	Web_HouTai_Port = 8008
	Language = ["pl"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "Poland"
	#SQL时区修正(注意有夏令时)
	SQL_TIME_ZONE = "set time_zone = '+1:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+2:00';"
	
elif Environment.IsFR:
	Web_Global_MySQL = ("10.127.120.100", 3306, "root", "Dyt1uC1lqfr")
	Web_Global_IP = "dkfr-ver.cdd.opogame.com"
	Web_Global_Port = 8008
	Web_HouTai_MySQL = ("10.127.120.100", 3306, "root", "Dyt1uC1lqfr")
	Web_HouTai_IP = "dkfr-ver.cdd.opogame.com"
	Web_HouTai_Port = 8008
	Language = ["fr"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "Europe/Paris"
	#SQL时区修正(注意有夏令时)
	SQL_TIME_ZONE = "set time_zone = '+1:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+2:00';"

elif Environment.IsESP:
	#西班牙
	Web_Global_MySQL = ("192.168.1.4", 3306, "root", "uJ9Iam8cYn7esp1")
	Web_Global_IP = "dkesp-ver.salagame.com"
	Web_Global_Port = 8008
	Web_HouTai_MySQL = ("192.168.1.4", 3306, "root", "uJ9Iam8cYn7esp1")
	Web_HouTai_IP = "dkesp-ver.salagame.com"
	Web_HouTai_Port = 8008
	Language = ["esp"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "Europe/Madrid"
	#SQL时区修正(注意有夏令时)
	SQL_TIME_ZONE = "set time_zone = '+1:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '+2:00';"

elif Environment.IsESPSA:
	#西班牙南美
	Web_Global_MySQL = ("192.168.1.3", 3306, "root", "wi2hiM0jaN2sa1")
	Web_Global_IP = "192.168.1.2"
	Web_Global_Port = 9001
	Web_HouTai_MySQL = ("192.168.1.3", 3306, "root", "wi2hiM0jaN2sa1")
	Web_HouTai_IP = "dkespsa-global.salagame.com"
	Web_HouTai_Port = 8008
	Language = ["esp"]
	TestWorldIDs = set([10002, 10003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "America/Bogota"
	#SQL时区修正(注意有夏令时)
	SQL_TIME_ZONE = "set time_zone = '-5:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '-5:00';"
	
elif Environment.IsEN:
	Web_Global_MySQL = ("192.168.110.105", 3306, "root", "sanarFtb7db1")
	Web_Global_IP = "dken-global.101xp.com"
	Web_Global_Port = 8008
	Web_HouTai_MySQL = ("192.168.110.105", 3306, "root", "sanarFtb7db1")
	Web_HouTai_IP = "dken-ver-version01.101xp.com"
	Web_HouTai_Port = 8008
	Language = ["en"]
	TestWorldIDs = set([1002, 1003, 30000])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30002
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "America/New_York"
	#SQL时区修正(注意北美有夏令时)
	SQL_TIME_ZONE = "set time_zone = '-5:00';"
	SQL_TIME_ZONE_DST = "set time_zone = '-4:00';"
elif Environment.IsYY:
	#YY
	Web_Global_MySQL = ("10.66.142.216", 3306, "root", "diC9Bop0Nem")
	Web_Global_IP = "lqyy-global.gamepf.com"
	Web_Global_Port = 8008
	Web_HouTai_MySQL = ("10.66.142.216", 3306, "root", "diC9Bop0Nem")
	Web_HouTai_IP = "lqyy-ver-bk.gamepf.com"
	Web_HouTai_Port = 80
	Language = ["yy"]
	TestWorldIDs = set([10002])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30003
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "Asia/Shanghai"
	#SQL时区修正
	SQL_TIME_ZONE = None
	SQL_TIME_ZONE_DST = None
	
elif Environment.IsSasia:
	#东南亚
	pass
elif Environment.Is7K:
	#7k7k
	Web_Global_MySQL = ("10.66.142.216", 3306, "root", "diC9Bop0Nem")
	Web_Global_IP = "10.104.102.30"
	Web_Global_Port = 9001
	Web_HouTai_MySQL = ("10.66.142.216", 3306, "root", "diC9Bop0Nem")
	Web_HouTai_IP = "lq7k-global.gamepf.com"
	Web_HouTai_Port = 8008
	Language = ["yy"]
	TestWorldIDs = set([10002])
	#测试服跨服服务器ID
	DefaultCrossID_Test = 30000
	#正式服默认跨服服务器ID
	DefaultCrossID_Normal = 30001
	#第二组跨服服务器ID
	CrossID_Test_2 = 30003
	CrossID_Normal_2 = 30002
	CrossWorlds = {}
	#Django时区
	TimeZone = "Asia/Shanghai"
	#SQL时区修正
	SQL_TIME_ZONE = None
	SQL_TIME_ZONE_DST = None
	
