#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# C中定义的消息，取值范围[0, 512)  [0 * 8bit, 2 * 8bit)
#===============================================================================
# MsgBegin
# C中消息定义
enGEMsg_None = 0		#无效的消息
enGEMsg_Ping = 1		#心跳包
enGEMsg_Forward_From = 2		#多合1，表明消息从哪儿来（用于网关重定向）
enGEMsg_Forward_To = 3		#1拆多，表明消息要到哪儿去（用于网关重定向）
enGEMsg_Forward_Other = 4		#1拆多，表明消息要到其他的连接中去
enGEMsg_AutoEnd = 5		#引擎层的最后一个消息类型
enGEMsg_End = 255		#引擎层的最后一个消息类型
enProcessMsg_Echo = 256		#回显消息
enProcessMsg_Who = 257		#表明身份的消息
enProcessMsg_ServerCallBack = 258		#进程间消息回调
enProcessMsg_OKClient = 259		#告诉客户端OK
enProcessMsg_NewClient = 260		#新的客户端
enProcessMsg_LostClient = 261		#失去客户端
enProcessMsg_KickClient = 262		#踢掉客户端
enProcessMsg_RoleCallBack = 263		#角色消息回调
enProcessMsg_RoleSyncInt64 = 264		#同步Int64数组
enProcessMsg_RoleSyncDisperseInt32 = 265		#同步DisperseInt32数组
enProcessMsg_RoleSyncInt32 = 266		#同步Int32数组
enProcessMsg_RoleSyncInt16 = 267		#同步Int16数组
enProcessMsg_RoleSyncInt8 = 268		#同步Int8数组
enProcessMsg_RoleSyncDayInt8 = 269		#同步DayInt8数组
enProcessMsg_RoleSyncInt1 = 270		#同步Int1数组
enProcessMsg_RoleSyncDayInt1 = 271		#同步DayInt1数组
enProcessMsg_RoleSyncDynamicInt64 = 272		#同步DynamicInt64数组
enProcessMsg_RoleSyncClientInt8 = 273		#同步ClientInt8数组
enProcessMsg_RoleSyncTempInt64 = 274		#同步TempInt64数组
enProcessMsg_RoleSyncCD = 275		#同步CD数组
enProcessMsg_RoleSyncDataBase = 276		#同步角色基础数据
enProcessMsg_RoleSyncOK = 277		#同步角色数据成功
enProcessMsg_RoleSyncProperty = 278		#同步角色属性
enProcessMsg_RoleSyncHeroProperty = 279		#同步英雄属性
enProcessMsg_RoleStartTransaction = 280		#开启事务
enProcessMsg_RoleEndTransaction = 281		#关闭事务
enRoleToTargetPos = 282		#客户端请求到达某个目标点
enRoleMovePos = 283		#客户端同步自己移动的位置
enSyncRoleTargerPos = 284		#向其他玩家同步一个玩家的目标点，当前点
enSyncRoleNowPos = 285		#向其他玩家同步一个玩家的当前点,(目标点默认0,0 即静止玩家)
enSyncRoleDisappear = 286		#同步一个玩家消失了
enSyncRoleIdle = 287		#服务器拉停玩家
enSyncRoleScenePos = 288		#通知客户端要到达哪个场景哪个坐标
enSyncRoleVersion = 289		#同步一个玩家的版本号
enSyncRoleAppreanceData = 290		#同步一个玩家外观数据
enCheckRoleAppearanceData = 291		#查看一个玩家外观数据
enSyncBroadcastNPC = 292		#同步广播的NPC消息
enNPCPos = 293		#同步一个NPC位置消息
enNPCMovingPos = 294		#同步一个移动中的NPC消息
enNPCDisappear = 295		#同步一个NPC消失了
enNPCClick = 296		#点击一个NPC
enRoleFlyState = 297		#同步飞行标志状态
enClientCharMsg = 298		#从客户端发来的字符消息
enServerCharMsg = 299		#由服务器发出的字符消息
enClientJoinSceneOK = 300		#客户端转场景成功了
enCheckRoleAppStatus = 301		#请求一个角色的外观状态
enSyncRoleAppStatus = 302		#同步一个角色的外观状态和相应的版本号
enSyncTime = 303		#同步客户端当前时间
enProcessMsg_AutoEnd = 304		#最后一个进程间消息
enProcessMsg_End = 511		#最后一个进程间消息
# MsgEnd