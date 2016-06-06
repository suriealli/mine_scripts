#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.Gateway.ClientConnect")
#===============================================================================
# 连接管理模块
#===============================================================================
import cGatewayForward
from Common.Connect import Who
from ComplexServer import Connect

if "_HasLoad" not in dir():
	Connect.NewConnectCallBack.RegCallbackFunction(Who.enWho_Client_, cGatewayForward.OnClient_New)
	Connect.LostConnectCallBack.RegCallbackFunction(Who.enWho_Client_, cGatewayForward.OnClient_Lost)


