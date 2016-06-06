#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Common.Message.OtherMessage")
#===============================================================================
# 其他的消息，取值范围[768, 1024)  [3 * 8bit, 4 * 8bit)
#===============================================================================
OMsg_Login = 768				#客户端请求登录
OMsg_LoginFail = 769			#告诉客户端登录失败
OMsg_RoleError = 770			#告诉客户端角色有问题(让客户端弹出创建角色面板)
OMsg_CreateRole = 771			#客户端请求创建角色
OMsg_ServerUnixTime = 772		#告诉客户端服务器时间（意味着登录OK）
OMsg_ClientOK = 773				#客户端准备OK（可以开始载入角色）
OMsg_Kick = 774					#告诉客户端你已经被T了
OMsg_ChechMsg = 775				#检测消息
OMsg_FirstCreateRole = 776		#第一次创建角色
OMsg_ClientStatus = 777			#客户端状态保存
