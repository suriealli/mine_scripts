#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 环境定义
#===============================================================================
# 是否是Window平台

IsWindows = None
# 本机IP
IP = "127.0.0.1"
# 是否跨服
IsCross = None

# 是否是内网测试环境、是否是外网正式环境（下面值必定只有1个为真）(开发环境下可以有2个为真)
IsDevelop = None
IsQQ = None			#国服空间朋友大厅
IsQQUnion = None	#国服游戏联盟
IsNA = None
IsWeb = None
IsFT = None			#繁体
IsRUMSK = None		#俄罗斯莫斯科版
IsRUVLA = None		#俄罗斯符拉迪沃斯托克(暂时未使用)
IsRUSP = None		#俄罗斯社交版本
IsRUXP = None		#俄罗斯101xp版本
IsRURBK = None		#俄罗斯RBK版本
IsRUGN = None		#俄罗斯GAMENET版本
IsRUTT = None		#俄罗斯比赛服
IsKGG = None		#北美kgg
IsXP = None			#北美101xp联运伦敦
IsXPUSE = None		#北美101xp联运us east
IsXPUSW = None		#北美101xp联运us west
IsNAPLUS1 = None	#北美plus1games联运

IsEN = None			#101xp英文版

IsTK = None			#土耳其
IsTKPLUS1 = None	#土耳其plus1联运
IsTKESP = None		#土耳其Esprite联运
IsTKSG = None		#土耳其SG联运

IsPL = None			#波兰
IsPLXP = None		#波兰101xp联运

IsFR = None			#法语

IsESP = None		#西班牙
IsESPSA = None		#西班牙南美联运

IsGER = None		#德语

IsYY = None			#YY

Is7K = None			#7k7k

IsSasia = None		#东南亚

#当前的语言环境
Language = None
# WEB管理
HasWeb = None
# 插件管理
HasControl = None
HasDB = None
HasGateway = None
HasHttp = None
HasLogic = None
# 当前环境
ENV = None

#===============================================================================
EnvTxt = 	["develop", 
			"web", \
			"qq", "qu", \
			"tw",\
			"na", "kgg", "xpuse", "xpusw", "xp", \
			"rumsk", "rusp", "ruxp", "rurbk", "rugn", \
			"tk", "tkplus1","tkesp","tksg",\
			"pl", "plxp", \
			"fr", \
			"en", \
			"ger",\
			"esp", "espsa",\
			"sasia",\
			"rutt",\
			]

#===============================================================================
def EnvIsQQ():
	#腾讯，包括空间，朋友，联盟等
	global IsQQ, IsQQUnion
	return IsQQ or IsQQUnion

def EnvIsQQUnion():
	#腾讯游戏联盟
	global IsQQUnion
	return IsQQUnion

def EnvIsFT():
	#繁体
	global IsFT
	return IsFT

def EnvIsNA():
	#北美
	global IsNA, IsKGG, IsXP, IsXPUSE, IsXPUSW, IsNAPLUS1
	return IsNA or IsKGG or IsXP or IsXPUSE or IsXPUSW or IsNAPLUS1

def EnvIsNAXP():
	#北美xp
	global IsXP, IsXPUSE, IsXPUSW
	return IsXP or IsXPUSE or IsXPUSW

def EnvIsRU():
	#俄罗斯
	global IsRUMSK, IsRUSP, IsRUXP, IsRURBK, IsRUGN
	return IsRUMSK or IsRUSP or IsRUXP or IsRURBK or IsRUGN

def EnvIsRUTT():
	#俄罗斯比赛服
	global IsRUTT
	return IsRUTT

def EnvIsTK():
	#土耳其
	global IsTK, IsTKPLUS1, IsTKESP, IsTKSG
	return IsTK or IsTKPLUS1 or IsTKESP or IsTKSG

def EnvIsPL():
	#波兰
	global IsPL, IsPLXP
	return IsPL or IsPLXP

def EnvIsFR():
	#法国
	global IsFR
	return IsFR

def EnvIsESP():
	#西班牙
	global IsESP, IsESPSA
	return IsESP or IsESPSA

def EnvIsEN():
	#英文101xp
	global IsEN
	return IsEN

def EnvIsGER():
	#德语
	global IsGER
	return IsGER

def EnvIsYY():
	#YY等国内联运
	global IsYY, Is7K
	return IsYY or Is7K

def EnvIsSasia():
	#东南亚
	global IsSasia
	return IsSasia

################################################################################
def ReadConfig():
	global ENV
	if ENV is None:
		f = open(__file__[:__file__.find("Environment")] + "ENV.txt")
		ENV = f.read()
		if ENV.endswith("\n"):
			ENV = ENV[:-1]
		if ENV.endswith("\r"):
			ENV = ENV[:-1]
		f.close()
		ENV = ENV.replace(" ", "")
	return ENV

def ReadDevelop():
	#开发环境下的子环境
	f = open(__file__[:__file__.find("Environment")] + "ENV_Develop.txt")
	develop_env = f.read()
	if develop_env.endswith("\n"):
		develop_env = develop_env[:-1]
	if develop_env.endswith("\r"):
		develop_env = develop_env[:-1]
	f.close()
	return develop_env

def WriteConfig(ENV):
	f = open(__file__[:__file__.find("Environment")] + "ENV.txt", "w")
	f.write(ENV)
	f.close()

def IP2Int(ip):
	lis = ip.split(".")
	return 256 ** 3 * int(lis[0]) + 256 ** 2 * int(lis[1]) + 256 * int(lis[2]) + int(lis[3])

# 构建当前机器环境
def BuildEnviroment():
	# 平台
	import platform
	global IsWindows, IP, IsDevelop, IsQQ, IsQQUnion, IsWeb
	global IsNA, IsFT, IsRUMSK, IsRUSP, IsRUXP, IsRURBK, IsRUGN, IsKGG, IsXP, IsTK, IsPL, IsPLXP
	global IsXPUSE, IsXPUSW, IsTKPLUS1, IsTKESP, IsTKSG, IsFR, IsNAPLUS1, IsEN, IsESP, IsGER, IsYY, Is7K
	global IsESPSA, IsSasia, IsRUTT
	
	if platform.system() == "Windows":
		IsWindows = True
	else:
		IsWindows = False
	# IP
	pid = 0
	if IsWindows:
		import socket
		IP = socket.gethostbyname(socket.gethostname())
		import cProcess
		pid = cProcess.ProcessID
	else:
		A_INNER_IP = [IP2Int("10.0.0.0"), IP2Int("10.255.255.255")]
		B_INNER_IP = [IP2Int("172.16.0.0"), IP2Int("172.31.255.255")]
		C_INNER_IP = [IP2Int("192.168.0.0"), IP2Int("192.168.255.255")]
		import os
		ips = os.popen("/sbin/ifconfig | grep 'inet addr' | awk '{print $2}'").read()
		for add in ips.split('\n'):
			if not add:
				continue
			ip = add[5:]
			if ip == "127.0.0.1":
				continue
			IP = ip
			ip_int = IP2Int(ip)
			if (A_INNER_IP[0] < ip_int < A_INNER_IP[1]) or (B_INNER_IP[0] < ip_int < B_INNER_IP[1]) or (C_INNER_IP[0] < ip_int < C_INNER_IP[1]):
				break
		else:
			assert IP != "127.0.0.1"
	# 设置功能
	IsDevelop = False
	IsQQ = False
	IsQQUnion = False
	IsWeb = False
	IsNA = False
	IsFT = False
	IsRUMSK = False
	IsRUSP = False
	IsRUXP = False
	IsRURBK = False
	IsRUGN = False
	IsRUTT = False
	IsKGG = False
	IsXP = False
	IsXPUSE = False
	IsXPUSW = False
	IsTK = False
	IsTKPLUS1 = False
	IsPL = False
	IsPLXP = False
	IsTKESP = False
	IsTKSG = False
	IsFR = False
	IsNAPLUS1 = False
	IsEN = False
	IsESP = False
	IsESPSA = False
	IsGER = False
	IsYY = False
	IsSasia = False
	Is7K = False
	
	ENV = ReadConfig()
	if ENV == "develop":
		IsDevelop = True
		de = ReadDevelop()
		de = eval(de)
		develop_env = de.get(pid, "")
		if develop_env == "na":
			IsNA = True
		elif develop_env == "tw":
			IsFT = True
		elif develop_env == "rumsk":
			IsRUMSK = True
		elif develop_env == "rusp":
			IsRUSP = True
		elif develop_env == "ruxp":
			IsRUXP = True
		elif develop_env == "rurbk":
			IsRURBK = True
		elif develop_env == "rugn":
			IsRUGN = True
		elif develop_env == "rutt":
			IsRUTT = True
		elif develop_env == "kgg":
			IsKGG = True
		elif develop_env == "xpuse":
			IsXPUSE = True
		elif develop_env == "xpusw":
			IsXPUSW = True
		elif develop_env == "xp":
			IsXP = True
		elif develop_env == "tk":
			IsTK = True
		elif develop_env == "tkplus1":
			IsTKPLUS1 = True
		elif develop_env == "tksg":
			IsTKSG = True
		elif develop_env == "pl":
			IsPL = True
		elif develop_env == "plxp":
			IsPLXP = True
		elif develop_env == "tkesp":
			IsTKESP = True
		elif develop_env == "fr":
			IsFR = True
		elif develop_env == "naplus1":
			IsNAPLUS1 = True
		elif develop_env == "en":
			IsEN = True
		elif develop_env == "esp":
			IsESP = True
		elif develop_env == "espsa":
			IsESPSA = True
		elif develop_env == "ger":
			IsGER = True
		elif develop_env == "yy":
			IsYY = True
		elif develop_env == "sasia":
			IsSasia = True
		elif develop_env == "7k":
			Is7K = True
		else:
			pass
	elif ENV == "qq":
		IsQQ = True
	elif ENV == "qu":
		IsQQUnion = True
	elif ENV == "web":
		IsWeb = True
	elif ENV == "na":
		IsNA = True
	elif ENV == "tw":
		IsFT = True
	elif ENV == "rumsk":
		IsRUMSK = True
	elif ENV == "rusp":
		IsRUSP = True
	elif ENV == "ruxp":
		IsRUXP = True
	elif ENV == "rurbk":
		IsRURBK = True
	elif ENV == "rugn":
		IsRUGN = True
	elif ENV == "rutt":
		IsRUTT = True
	elif ENV == "kgg":
		IsKGG = True
	elif ENV == "xpuse":
		IsXPUSE = True
	elif ENV == "xpusw":
		IsXPUSW = True
	elif ENV == "xp":
		IsXP = True
	elif ENV == "tk":
		IsTK = True
	elif ENV == "tkplus1":
		IsTKPLUS1 = True
	elif ENV == "tkesp":
		IsTKESP = True
	elif ENV == "tksg":
		IsTKSG = True
	elif ENV == "pl":
		IsPL = True
	elif ENV == "plxp":
		IsPLXP = True
	elif ENV == "fr":
		IsFR = True
	elif ENV == "naplus1":
		IsNAPLUS1 = True
	elif ENV == "en":
		IsEN = True
	elif ENV == "esp":
		IsESP =  True
	elif ENV == "espsa":
		IsESPSA = True
	elif ENV == "ger":
		IsGER = True
	elif ENV == "yy":
		IsYY = True
	elif ENV == "sasia":
		IsSasia = True
	elif ENV == "7k":
		Is7K = True
	else:
		raise Exception("unknown environment(%s)" % ENV)
###################################################################################
def LoadLanguage():
	#载入进程的语言版本
	global Language, Language

	import cProcess
	from ComplexServer.Plug.DB import DBHelp
	Language = DBHelp.LoadLanguageByZoneId(cProcess.ProcessID)
	if HasWeb and not Language:
		print "GE_EXC get language on define in ENV", Language, cProcess.ProcessID
		from World import Define
		Language = Define.Language[0]
		
def WebNoLanguageDo():
	global Language, HasWeb
	if HasWeb and not Language:
		from World import Define
		Language = Define.Language[0]

def LoadCross():
	global IsCross
	import cProcess
	from World import Define
	IsCross = cProcess.ProcessID in Define.CrossWorlds

def ShowEnvironment():
	print __file__[:__file__.find("Environment")] + "ENV.txt"
	print "ENV", ENV
	print "IsWindows", IsWindows
	print "IP", IP
	print "IsDevelop", IsDevelop
	print "IsQQ", IsQQ
	print "IsWeb", IsWeb
	print "HasHttp", HasHttp
	print "HasGateway", HasGateway
	print "HasLogic", HasLogic
	print "HasDB", HasDB

if "_HasLoad" not in dir():
	BuildEnviroment()
	WebNoLanguageDo()
	
if __name__ == "__main__":
	ShowEnvironment()
