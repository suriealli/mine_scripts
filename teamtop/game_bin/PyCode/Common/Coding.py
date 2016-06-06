#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 全局数据编码范围
# 注意， 这个模块不能Reload
#===============================================================================
from Common import CValue

# 消息编码
CMessageRange = 0 * CValue.P2_8, 2 * CValue.P2_8				#C++中定义的消息[0, 512)
PyMessageRange = 2 * CValue.P2_8, 3 * CValue.P2_8				#Python中定义的消息[512, 768)
OtherMessageRange = 3 * CValue.P2_8, 4 * CValue.P2_8			#其他的消息[768, 1024)
AutoMessageRange = 4 * CValue.P2_8, 32 * CValue.P2_8			#角色和客户端通信消息[1024, 8192)

# 固定数值编码(SQL语句可以直接修改在MySQL中的存储)
RoleInt64Range = 32 * CValue.P2_8, 33 * CValue.P2_8				#Int64数组编码[8192, 8448)
RoleDisperseInt32Range = 33 * CValue.P2_8, 34 * CValue.P2_8		#Int32数组（离散）编码[8448, 8704)
RoleInt32Range = 34 * CValue.P2_8, 36 * CValue.P2_8				#Int32数组编码[8704, 9216)
RoleInt16Range = 36 * CValue.P2_8, 40 * CValue.P2_8				#Int16数组编码[9216, 10240)
RoleInt8Range = 40 * CValue.P2_8, 48 * CValue.P2_8				#Int8数组编码[10240, 12288)
RoleDayInt8Range = 48 * CValue.P2_8, 56 * CValue.P2_8			#Int8数组编码（每日清零）[12288, 14336)
RoleInt1Range = 56 * CValue.P2_8, 72 * CValue.P2_8				#Int1数组编码[14336, 18432)
RoleDayInt1Range = 72 * CValue.P2_8, 80 * CValue.P2_8			#Int1数组编码（每日清零）[18432, 20480)

# 非固定数值编码(SQL语句不能直接修改在MySQL中的存储，需要Python读取修改再写回数据库。 有时间限制和动态大小，可以节约存储空间)
RoleDynamicInt64Range = 80 * CValue.P2_8, 88 * CValue.P2_8		#Int64数组(动态存在)编码[20480, 22528)

# Python对象是否脏编码(存储结构化数据, 这里面的编码是用来标记Python对象的版本号的)
RoleObjFlagRange = 88 * CValue.P2_8, 89 * CValue.P2_8,			#Python对象数组编码[22528, 22784)

# 客户端数值编码
RoleClientInt8Range = 89 * CValue.P2_8, 90 * CValue.P2_8		#Int8数组（客户端）编码[22784, 23040)

# CD编码
RoleCDRange = 90 * CValue.P2_8, 92 * CValue.P2_8				#CD数组编码[23040, 23552)

# 临时数值编码(完全不持久化，内存数据)
RoleTempInt64Range = 92 * CValue.P2_8, 100 * CValue.P2_8		#Int64数组(临时存在)编码[23552, 25600)

RoleItemRange = 100 * CValue.P2_8, 140 * CValue.P2_8			#物品编码[25600, 35840)

RoleOtherRange = 140 * CValue.P2_8, 160 * CValue.P2_8			#其他对象编码[35840, 40960)

