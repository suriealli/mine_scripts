#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.API.Define")
#===============================================================================
# API的相关定义
#===============================================================================

# 如果是自己做的HTTP接口，有可能返回这个东西
Error = "error"					#普通错误
ErrorTime = "error_time"		#unixtime错误
ErrorSign = "error_sign"		#签名错误
Errorbillno = "error_billno"	#订单号错误
ErrorServer = "server_error"	#服信息错误

OK = repr({"ret":0, "msg":"OK"})
