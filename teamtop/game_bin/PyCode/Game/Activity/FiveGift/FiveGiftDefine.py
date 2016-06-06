#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Activity.FiveGift.FiveGiftDefine")
#===============================================================================
# 首充五重礼定义
#===============================================================================
from Game.Role.Data import EnumInt8

#五重礼礼包ID对应奖励枚举
GIFTID_TO_REWARD_ENUM = {1: EnumInt8.FiveGiftFirst, 2: EnumInt8.FiveGiftSecond, 
					3: EnumInt8.FiveGiftThird, 4: EnumInt8.FiveGiftForth, 
					5: EnumInt8.FiveGiftFifth}

#天数索引每日首充奖励枚举
DAY_TO_FIRST_PAY_REWARD_ENUM = {1: EnumInt8.DayFirstPayReward1, 2: EnumInt8.DayFirstPayReward2, 
						3: EnumInt8.DayFirstPayReward3, 4: EnumInt8.DayFirstPayReward4, 
						5: EnumInt8.DayFirstPayReward5}