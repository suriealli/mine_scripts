#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("ComplexServer.Plug.DB.Column")
#===============================================================================
# 列定义
#===============================================================================
from Util.MySQL import DynamicColumn

# 帐号
account = DynamicColumn.StringColumn("account", 60, "帐号")
# 用户ip
userip = DynamicColumn.StringColumn("userip", 60, "用户IP")
# 角色ID
role_id = DynamicColumn.IntColumn("role_id", "bigint", True, False, "角色ID")
# 角色名
role_name = DynamicColumn.StringColumn("role_name", 60, "角色名")
# 角色ObjId
obj_id = DynamicColumn.IntColumn("obj_id", "bigint", True, False, "对象全球ID")
# 角色Obj类型
obj_type = DynamicColumn.IntColumn("obj_type", "int", True, False, "对象类型")
# 角色Obj辅助整数
obj_int = DynamicColumn.IntColumn("obj_int", "int", False, False, "对象整数")
# 角色Obj数据
obj_data = DynamicColumn.ObjColumn("obj_data", "对象的数据")
# 来源1
from_1 = DynamicColumn.StringColumn("from_1", 60, "来源1")
# 来源2
from_2 = DynamicColumn.StringColumn("from_2", 60, "来源2")
# 来源3
from_3 = DynamicColumn.StringColumn("from_3", 60, "来源3")

obj_data_small = DynamicColumn.SmallObjColumn("obj_data", "对象的数据")