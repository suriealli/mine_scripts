#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Game.Role.Data.Enum")
#===============================================================================
# 定义对角色数据的处理动作
#===============================================================================
from Common import Coding

# ActionBegin
# 角色数值超出范围处理
DoNothing = 0		#当超出范围时，啥也不做
DoIgnore = 1		#当超出范围时，忽视这次操作
DoRound = 2		#当超出范围时，截取超出范围的部分
DoKick = 3		#当超出范围时，忽视这次操作并踢掉角色
# ActionEnd


# 客户端数组长度(C++读取)
MaxClientInt8Size = 255
# 动态Int64数组长度
MaxDynamicInt64Size = Coding.RoleDynamicInt64Range[1] - Coding.RoleDynamicInt64Range[0]
# CD数组长度
MaxCDSize = Coding.RoleCDRange[1] - Coding.RoleCDRange[0]
# 临时对象数组长度
MaxTempObjSize = 80

