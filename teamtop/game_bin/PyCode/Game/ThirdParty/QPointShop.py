#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.ThirdParty.QPointShop")
#===============================================================================
# Q点商店
#===============================================================================
import cRoleMgr
import Environment
import DynamicPath
from Util.File import TabFile
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog
from ComplexServer.API import FaHuoHttp, Define
from Game import RTF
from Game.Role import Event
from Game.Role.Data import EnumTempObj, EnumObj
from Game.ThirdParty import QPointDeliver


Tips = "无法连接至Q点支付平台，暂时无法处理这个订单，请刷新页面或者重新登录游戏后再试。"

class QQGoods(TabFile.TabLine):
	FilePath = DynamicPath.DynamicFolder(DynamicPath.ConfigPath).AppendPath("ThirdParty").FilePath("QGoods.txt")
	def __init__(self):
		self.goods_id = int
		self.goods_price = int
		self.goods_meta = str
		self.goods_url = str
		self.goods_deliver = self.GetGoodsDeliverFunByString
	
	def GetGoodsDeliverFunByString(self, s):
		return getattr(QPointDeliver, s)

@RTF.RegFunction
def LoadQQGoodsConfig(price = None):
	'''
	载入q点购物价格
	@param price:默认(0)配置表中价格，否则是传入价格
	'''
	for cfg in QQGoods.ToClassType():
		if cfg.goods_id in QQGoodss:
			print "GE_EXC LoadQQGoodsConfig repeat goods(%s)" % cfg.goods_id
		QQGoodss[cfg.goods_id] = cfg
		if price:
			cfg.goods_price = max(5, price)

def RequestBuyGoods(role, msg):
	'''
	客户端请求购买Q点货物
	@param role:
	@param msg:
	'''
	if not Environment.EnvIsQQ():
		return
	backid, (goods_id, cnt) = msg
	cfg = QQGoodss.get(goods_id)
	if cfg is None:
		print "GE_EXC, role(%s) buy unknown goods(%s)" % (role.GetRoleID(), msg)
		role.WPE(11)
		return
	login_info = role.GetTempObj(EnumTempObj.LoginInfo)
	openid = login_info["account"]
	openkey = login_info["openkey"]
	pf = login_info["pf"]
	create_pf = str(role.GetObj(EnumObj.Create_PF))
	from2 = login_info.get("app_custom", "")
	from3 = login_info.get("app_contract_id", "")
	pfkey = login_info["pfkey"]
	roleid = role.GetRoleID()
	payitem = "%s*%s*%s" % (goods_id, cfg.goods_price, cnt)
	goodsmeta = cfg.goods_meta
	goodsurl = cfg.goods_url
	level = role.GetLevel()
	FaHuoHttp.buy_goods(openid, openkey, pf, create_pf, from2, from3, pfkey, roleid, payitem, goodsmeta, goodsurl, level, OnGetToken, (backid, role))

def OnGetToken(response, regparam):
	backid, role = regparam
	code, body = response
	if code != 200:
		role.CallBackFunction(backid, None)
		print "GE_EXC buy_goods error code (%s) msg(%s)" % (code, body)
		return
	if body == Define.Error:
		role.CallBackFunction(backid, None)
		print "GE_EXC, buy_goods http has error."
		return
	body = eval(body)
	if body["ret"] != 0:
		role.CallBackFunction(backid, None)
		if body["ret"] == 1002:
			role.ClientCommand("QQGAME_RELOGIN")
		else:
			print "GE_EXC, buy_goods error ret (%s)" % body["ret"]
		return
	role.CallBackFunction(backid, body["url_params"])

def OnDeliverGoods(role, pay_item):
	'''
	Q点发货
	@param role:
	@param pay_item:
	'''
	lis = pay_item.split("*")
	goods_id = int(lis[0])
	goods_price = int(lis[1])
	goods_cnt = int(lis[2])
	cfg = QQGoodss.get(goods_id)
	if cfg is None:
		return "GE_EXC role(%s) can't find goods(%s) config on OnDeliverGoods" % (role.GetRoleID(), goods_id)
	with QGoods_Deliver:
		AutoLog.LogBase(role.GetRoleID(), AutoLog.eveQDeliver, pay_item)
		# Q点发货
		cfg.goods_deliver(role, goods_cnt)
		# 设置Q点消费(下次更新改一个函数)
		role.SetConsumeQPoint(role.GetConsumeQPoint() + goods_price * goods_cnt)
		# 触发事件
		Event.TriggerEvent(Event.Eve_GamePoint, role, (goods_id, goods_price, goods_cnt))

if "_HasLoad" not in dir() and Environment.HasLogic:
	QQGoodss = {}
	LoadQQGoodsConfig()
	if Environment.HasLogic and not Environment.IsCross:
		cRoleMgr.RegDistribute(AutoMessage.AllotMessage("QGoods_Buy", "请求Q点购物"), RequestBuyGoods)
	if Environment.HasLogic:
		QGoods_Deliver = AutoLog.AutoTransaction("QGoods_Deliver", "Q点发货")
		