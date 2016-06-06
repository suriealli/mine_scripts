#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Item.ItemMsg")
#===============================================================================
# 物品消息模块
#===============================================================================
from Common.Message import AutoMessage


if "_HasLoad" not in dir():
	Item_SyncItem_Package = AutoMessage.AllotMessage("Item_SyncItem_Package", "更新一个物品移动到包裹")
	Item_SyncItemData = AutoMessage.AllotMessage("Item_SyncItemData", "同步单个物品数据")
	Item_SyncItemCnt = AutoMessage.AllotMessage("Item_SyncItemCnt", "同步更新一个物品数量")
	Item_SyncDel = AutoMessage.AllotMessage("Item_SyncDel", "同步删除一个物品")
