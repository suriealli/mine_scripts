#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.WonderfulAct.WonderfulData")
#===============================================================================
# 精彩活动数据
#===============================================================================
import Environment
from Game.Persistence import BigTable


if "_HasLoad" not in dir():
	pass

###################################################################################
#外部访问数据接口
###################################################################################
def GetWAData(index):
	d = WA_BT.GetValue(index)
	if d is None:
		print "GE_EXC, WonderfulData GetWAData error index(%s)" % index
		return None
	return d["wonderful_data"]

def SetWAData(index, data):
	WA_BT.SetKeyValue(index, {"wonderful_index" : index, "wonderful_data" : data})
###################################################################################

class WABT(BigTable.BigTable):
	def SaveData(self):
		#每次都保存全部(暂时)
		if self.returnDB:
			for key in self.datas.iterkeys():
				self.changes.add(key)
		return BigTable.BigTable.SaveData(self)


def GetInitData():
	from Game.Activity.WonderfulAct import WonderfulActMgr
	return {WonderfulActMgr.WONDEFUL_INDEX_1: {},
			WonderfulActMgr.WONDEFUL_INDEX_2: 0,
			WonderfulActMgr.WONDEFUL_INDEX_3: 0,
			WonderfulActMgr.WONDEFUL_INDEX_4: {},
			WonderfulActMgr.WONDEFUL_INDEX_5: {},
			WonderfulActMgr.WONDEFUL_INDEX_6: {},
			WonderfulActMgr.WONDEFUL_INDEX_7: {},
			WonderfulActMgr.WONDEFUL_INDEX_8: {},
			WonderfulActMgr.WONDEFUL_INDEX_9: [],
			WonderfulActMgr.WONDEFUL_INDEX_10: {},
			WonderfulActMgr.WONDEFUL_INDEX_11: {},
			WonderfulActMgr.WONDEFUL_INDEX_12: {},
			WonderfulActMgr.WONDEFUL_INDEX_13: {},
			WonderfulActMgr.WONDEFUL_INDEX_14: {},
			WonderfulActMgr.WONDEFUL_INDEX_15: {},
			WonderfulActMgr.WONDEFUL_INDEX_16: {},
			WonderfulActMgr.WONDEFUL_INDEX_17: {},
			WonderfulActMgr.WONDEFUL_INDEX_18: 0,
			WonderfulActMgr.WONDEFUL_INDEX_19: [],
			WonderfulActMgr.WONDEFUL_INDEX_20: {}
			}

def InitBTData():
	from Game.Activity.WonderfulAct import WonderfulActMgr
	if WonderfulActMgr.WONDEFUL_INDEX_1 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_1, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_2 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_2, 0)
	
	if WonderfulActMgr.WONDEFUL_INDEX_3 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_3, 0)
		
	if WonderfulActMgr.WONDEFUL_INDEX_4 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_4, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_5 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_5, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_6 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_6, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_7 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_7, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_8 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_8, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_9 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_9, [])
		
	if WonderfulActMgr.WONDEFUL_INDEX_10 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_10, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_11 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_11, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_12 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_12, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_13 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_13, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_14 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_14, {})

	if WonderfulActMgr.WONDEFUL_INDEX_15 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_15, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_16 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_16, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_17 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_17, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_18 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_18, 0)
		
	if WonderfulActMgr.WONDEFUL_INDEX_19 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_19, [])
		
	if WonderfulActMgr.WONDEFUL_INDEX_20 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_20, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_21 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_21, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_22 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_22, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_23 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_23, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_24 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_24, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_25 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_25, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_26 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_26, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_27 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_27, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_28 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_28, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_29 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_29, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_30 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_30, {})
		
	if WonderfulActMgr.WONDEFUL_INDEX_31 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_31, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_32 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_32, {})
	
	if WonderfulActMgr.WONDEFUL_INDEX_33 not in WA_BT.datas:
		SetWAData(WonderfulActMgr.WONDEFUL_INDEX_33, {})
	#载入完成后处理
	WonderfulActMgr.SetVIPData()

def AfterLoadBT():
	InitBTData()
		
	
if "_HasLoad" not in dir():
	if Environment.HasLogic or Environment.HasWeb:
		WA_BT = WABT("sys_wonderfulactdata", 50, AfterLoadBT)

