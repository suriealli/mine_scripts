#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.HalloweenNA.HalloweenNADefine")
#===============================================================================
# 北美通用活动定义
#===============================================================================

#需要清理的活动数据，一般指活动期间非每日活动
CLEAR_ACTID_LIST = [1,11,12,14,16,18,15,27,31,36,37]
#祝福活动列表
BLESS_ACTID_LIST = [15, 1015, 2015, 3015, 4015, 5015, 6015, 7015, 8015, 9015, 10015, 11015, 12015, 13015]
#每日首笔消费
DAY_COST_ACTID_LIST = [3, 1003]
#心魔挑战
PURGATORYPASS_ACTID_LIST = [10, 1010]
#挑战公会副本
UNION_FB_ACTID_LIST = [7, 1007]
#首充
FIRST_PAY_ACTID_LIST = [2, 1002]
#累计消费
TOTAL_COST_ACTID_LIST = [26, 1026, 2026]
#亲密派对
PARTY_ACTID_LIST = [39, 1039]
#婚礼
MARRY_ACTID_LIST = [38, 1038]
#情缘副本
COUPLESFB_ACTID_LIST = [40, 1040, 2040]
#挑战组队副本
GVEFB_ACTID_LIST = [4, 1004]
#英雄竞技
JJC_ACTID_LIST = [5, 1005]
#挑战副本
FB_ACTID_LIST = [6, 1006, 2006]
#恶魔深渊
EVILHOLE_ACTID_LIST = [19, 1019]

def GetClearDataActIDs():
	CLEAR_ACTID_LIST.extend(FIRST_PAY_ACTID_LIST)
	CLEAR_ACTID_LIST.extend(TOTAL_COST_ACTID_LIST)
	CLEAR_ACTID_LIST.extend(PARTY_ACTID_LIST)
	CLEAR_ACTID_LIST.extend(MARRY_ACTID_LIST)
	CLEAR_ACTID_LIST.extend(COUPLESFB_ACTID_LIST)
	return set(CLEAR_ACTID_LIST)
