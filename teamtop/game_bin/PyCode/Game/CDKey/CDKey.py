#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.CDKey.CDKey")
#===============================================================================
# CDKEY配置模块
#===============================================================================
import cRoleMgr
import DynamicPath
import Environment
from Util import Time
from Util.File import TabFile
from Common.Message import AutoMessage
from Common.Other import GlobalPrompt
from ComplexServer.API import GlobalHttp, QQHttp
from ComplexServer.Log import AutoLog
from Game.Role.Data import EnumTempObj
import cProcess
from World import Define


E_FF = "请输入正确的CDKEY"
E_CD = "你还需要等待%s才能再次激活此类CDKEY。"
E_HAS = "你已经激活过此类CDKEY了。"

E_TimeOver = "系统繁忙，请稍后再来领取CDKEY奖励!"
E_REPEAT = "你已经激活过此类CDKEY了！"
E_NO = "系统错误，请稍后再来领取CDKEY奖励!"
E_PASS = "CDKEY已经失效！"
E_E = "系统错误%s"

QQ_VAILD = "请使用领取cdkey兑换码的账号进行兑换"
#第三方特征码转为配置表特征码的配置
CDKey_Dict = {  "BENWL" : "a1", 
				"BENWH" : "a2", 
				"BKHLD" : "a13",	#全民中秋礼包
				"BKLFY" : "a19",	#白银新手卡礼包
				"BKHJS" : "a14",	#给力中秋礼包
				"BKNRR" : "a21",	#至尊卡
				"BKNRN" : "a20",	#黄金新手卡
				"QS" : "b24",		#OK獨家禮盒
				"SD" : "b25",		#全家獨家禮盒
				"BLTQH" : "a28",	#达人特权礼包
				"BLWZJ" : "a29",	#精英豪华大礼包
				"BPNLZ" : "a42",	#龙骑士达人特权礼包
				"DK" : "b57",		#精選好禮禮包
				"BQ" : "a43",		#圣诞活动礼包
				"BQZNM" : "a45",	#每日抽奖一星礼包
				"BQZNR" : "a46",	#每日抽奖二星礼包
				"BQZNZ" : "a47",	#每日抽奖三星礼包
				"BSMPP" : "a55",	#龙骑春节大人礼包
				"BSJZN" : "a56",	#龙骑签到5日礼包
				"BSJZX" : "a57",	#龙骑签到10日礼包
				"BSKAR" : "a58",	#龙骑签到15日礼包
				"BSKBA" : "a59",	#龙骑签到20日礼包
				"BENWL" : "a66",	#龙骑访客精英礼包
				"BENWH" : "a67",	#龙骑访客黄金礼包
				"BQZWA" : "a1",		#测试CDKEY
				"AENWL" : "d1",		#勇者礼包（土耳其）
				"BWYQD" : "a80",	#龙骑士传管家特权公测礼包
				"BYUWX" : "a84",	#普通黄钻礼包
				"BYUXA" : "a85",	#精致黄钻礼包
				"DAFAK" : "a87",	#普通黄钻礼包2
				"DAFAN" : "a88",	#精致黄钻礼包2
				"DASUU" : "a89",	#顶级黄钻礼包
				"DBKQZ" : "a90",	#普通黄钻礼包3
				"DBKRG" : "a91",	#精致黄钻礼包3
				"DBKRK" : "a92",	#顶级黄钻礼包3
				"BMMKD" : "a30",	#黄金挖掘机新手卡礼包
				"DBXWK" : "a93",	#初级黄钻大礼
				"DBXWN" : "a94",	#中级黄钻大礼
				"DBXWR" : "a95",	#高级黄钻大礼
				"DDNPX" : "a96",	#初级黄钻大礼2
				"DDNQD" : "a97",	#中级黄钻大礼2
				"DDNQJ" : "a98",	#高级黄钻大礼2
				"DEAEA" : "h1",	#初级黄钻大礼3
				"DEAEE" : "h2",	#中级黄钻大礼3
				"DEAEJ" : "h3",	#高级黄钻大礼3
				"DESTX" : "h5",	#初级黄钻大礼4
				"DESUA" : "h6",	#中级黄钻大礼4
				"DESUH" : "h7",	#高级黄钻大礼4
				"DFAQT" : "h8",	    #初级黄钻大礼5
				"DFAQW" : "h9",	    #中级黄钻大礼5
				"DFARA" : "h10",	#高级黄钻大礼5
				"DFPUE" : "h14",	#初级黄钻大礼6
				"DFPUH" : "h15",	#中级黄钻大礼6
				"DFPUM" : "h16",	#高级黄钻大礼6
				"DGDUW" : "h23",	#初级黄钻大礼7
				"DGDUZ" : "h24",	#中级黄钻大礼7
				"DGDVE" : "h25",	#高级黄钻大礼7
				"DGUBA" : "h31",	#初级黄钻大礼8
				"DGUBP" : "h32",	#中级黄钻大礼8
				"DGUDE" : "h33",	#高级黄钻大礼8
				"DHJVK" : "h34",	#初级黄钻大礼9
				"DHJVQ" : "h35",	#中级黄钻大礼9
				"DHJVU" : "h36",	#高级黄钻大礼9
				"DHWAM" : "h37",	#初级黄钻大礼10
				"DHWAR" : "h38",	#中级黄钻大礼10
				"DHWAV" : "h39",	#高级黄钻大礼10
				"DAQSL" : "a86"		#暑期礼包
				}


def GetSpecial(cdkey):
	'''
	获取CDKey的特征码
	@param cdkey:
	'''
	#需要判断CDKEY是哪一类型
	spe = cdkey[:5]
	ck = CDKey_Dict.get(spe)
	if ck:
		return ck
	else:
		spe = cdkey[:2]
		ck = CDKey_Dict.get(spe)
		if ck:
			return ck
		return cdkey[:cdkey.find('-')]

def GetSpecialStr(cdkey):
	#获取CDKEY特征码判断前缀字符串
	spe = cdkey[:5]
	ck = CDKey_Dict.get(spe)
	if ck:
		return spe
	else:
		spe = cdkey[:2]
		ck = CDKey_Dict.get(spe)
		if ck:
			return spe
		return cdkey[:cdkey.find('-')]

def IsQQ_CDKey(cdkey):
	spe = cdkey[:5]
	return spe in CDKey_Dict

def GetConfig(cdkey):
	return CKC.get(GetSpecial(cdkey))

class CDKeyConfig(TabFile.TabLine):
	FilePath = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).AppendPath("CDKey").FilePath("CDKey.txt")
	def __init__(self):
		self.special = str
		self.name = str
		self.b_idx = self.GetI1Index
		self.cd_idx = self.GetCDIndex
		self.cd = self.GetIntByString
		self.item = self.GetEvalByString

def LoadCDKeyConfig():
	for ck in CDKeyConfig.ToClassType(False):
		if ck.special in CKC:
			print "GE_EXC, repeat cdkey special(%s)" % ck.special
			continue
		CKC[ck.special] = ck


def RequestActityCDKey(role, msg):
	'''
	请求激活CDKEY
	@param role:
	@param msg: cdkey
	'''
	cdkey = msg
	config = GetConfig(cdkey)
	if config is None:
		role.Msg(2, 0, E_FF)
		return
	# 如果只能激活一次
	if config.b_idx:
		if role.GetI1(config.b_idx):
			role.Msg(2, 0, E_HAS)
			return
	# 冷却时间
	elif config.cd_idx > 0 and config.cd > 0:
		cd = role.GetCD(config.cd_idx)
		if cd > 0:
			role.Msg(2, 0, E_CD % Time.DifToString(cd))
			return
	if cProcess.ProcessID in Define.TestWorldIDs and Environment.EnvIsQQ() and IsQQ_CDKey(cdkey):
	#if Environment.EnvIsQQ() and IsQQ_CDKey(cdkey):
		login_info = role.GetTempObj(EnumTempObj.LoginInfo)
		openid = login_info["account"]
		openkey = login_info["openkey"]
		pf = login_info["pf"]
		userip = login_info["userip"]
		QQHttp.check_cdk(openid, openkey, pf, userip, cdkey, CheckCDKeyBack, (role, config, cdkey))
	else:
		# 激活
		GlobalHttp.CDKey(role.GetRoleID(), cdkey, OnActivateBack, (role, config))

def CheckCDKeyBack(response, regparam):
	role, config,cdkey = regparam
	if role.IsKick():
		return
	if not response:
		return
	code, body = response
	if code != 200:
		print "GE_EXC, CheckCDKeyBack code error (%s)" % code
		return
	
	result = eval(body)
	if  result.get("ret") != 0:
		print "GE_EXC CheckCDKeyBack ret error", response, result.get('msg')
		return
	
	valid = result.get("valid", 0)
	if not valid:
		role.Msg(2, 0, QQ_VAILD)
		return
	
	GlobalHttp.CDKey(role.GetRoleID(), cdkey, OnActivateBack, (role, config))


def OnActivateBack(response, regparam):
	role, config = regparam
	# 没有响应
	if response is None:
		role.Msg(2, 0, E_TimeOver)
		return
	code, body = response
	# 判断返回值
	if code != 200:
		role.Msg(2, 0, E_TimeOver)
		return
	if body == "0":
		with TraCDKEY:
			DoReward(role, config)
	elif body == "1":
		role.Msg(2, 0, E_NO)
		return
	elif body == "2":
		role.Msg(2, 0, E_PASS)
		return
	else:
		print "GE_EXC, %s" % body
		role.Msg(2, 0, E_NO)
		return

def DoReward(role, config):
	# 检测重复激活并且标记
	if config.b_idx:
		if role.GetI1(config.b_idx):
			role.Msg(2, 0, E_REPEAT)
			return
		else:
			role.SetI1(config.b_idx, True)
	elif config.cd_idx > 0 and config.cd > 0:
		cd = role.GetCD(config.cd_idx)
		if cd > 0:
			role.Msg(2, 0, E_CD % Time.DifToString(cd))
			return
		else:
			role.SetCD(config.cd_idx, config.cd)
	# 给奖励
	itemCoding, cnt = config.item
	role.AddItem(itemCoding, cnt)
	
	role.Msg(2, 0, GlobalPrompt.Item_Tips % (itemCoding, cnt))

if "_HasLoad" not in dir():
	CKC = {}
	LoadCDKeyConfig()
	
	TraCDKEY = AutoLog.AutoTransaction("TraCDKEY", "激活一个CDKEY")
	
	if Environment.HasLogic:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("ActiveCDKEY", "请求激活CDKEY"), RequestActityCDKey)

