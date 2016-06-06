#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.GlobalMessage")
#===============================================================================
# 全局消息定义, 一个消息用于多个模块，防止模块的循环引用
#===============================================================================
from Common.Message import AutoMessage


if "_HasLoad" not in dir():
	Msg_CaiJi_Jindu = AutoMessage.AllotMessage("Msg_CaiJi_Jindu", "显示采集进度条")
	Msg_PlayFilm 	= AutoMessage.AllotMessage("Msg_PlayFilm", "让客户端播放动画")
	Auto_Find_Path 	= AutoMessage.AllotMessage("Auto_Find_Path", "通知客户端自动寻路")
	
	#这个需要回调的哦
	Order_To_DoSomething = AutoMessage.AllotMessage("Order_To_DoSomething", "命令客户端做某些事情")
	#任务触发，不需要回调
	Order_Task_DoSomething = AutoMessage.AllotMessage("Order_Task_DoSomething", "任务触发命令客户端做某些事情(不需要回调)")
	
	
	NPC_Pos = AutoMessage.AllotMessage("NPC_Pos", "同步一个NPC出现在某个位置")
	NPC_Disappear = AutoMessage.AllotMessage("NPC_Disappear", "同步一个NPC消失")
	
	NPC_Special = AutoMessage.AllotMessage("NPC_Special", "特殊NPC(id, npctype, x, y, d, coding, app)")
	
	FB_S_SyncFBRound = AutoMessage.AllotMessage("FB_S_SyncFBRound", "同步副本回合数")
	
	Npc_TypeChange = AutoMessage.AllotMessage("Npc_TypeChange", "改变npc外形")
	
	Notify_PutOnEquipment = AutoMessage.AllotMessage("Notify_PutOnEquipment", "通知客户端检测一下当前背包是否有可以穿戴的装备")
	
	Msg_S_StarColorCode = AutoMessage.AllotMessage("Msg_S_StarColorCode", "同步主角历史神将星级对应的最大颜色编码")
	