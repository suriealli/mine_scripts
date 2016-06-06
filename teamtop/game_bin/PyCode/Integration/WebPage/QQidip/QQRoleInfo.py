#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Integration.WebPage.QQidip.QQRoleInfo")
#===============================================================================
# 角色信息
#===============================================================================
import struct
from ComplexServer.Plug.DB import DBHelp
from Common import Serialize
from Game.Role.Data import EnumInt32, EnumInt16

#"RoleId" : "",		   /* 角色ID */
#"Level" : ,			  /* 等级 */
#"Reputation" : ,		 /* 声望 */
#"Physical" : ,		   /* 体力 */
#"Fight" : ,			  /* 战斗力 */
#"GuildId" : ,			/* 所属工会 */
#"Gender" : ,			 /* 性别 */
#"LastLoginTime" : "",	/* 最后登录时间 */
#"OnlineTime" : ,		 /* 在线时间 */
#"RegisterTime" : "",	 /* 注册时间 */
#"PayStone" : ,		   /* 充值神石数量 */
#"RewardStone" :		  /* 奖励神石数量 */

Column_RoleName = "role_name"
Column_NoActiveTime = "unix_timestamp(now()) - di32_0"
Column_Sex = "di32_7"
Column_Career = "di32_8"
Column_ZDL = "di32_9"
Column_Level = "di32_11"
Column_VIP = "di32_12"
Column_HuangZuan = "di32_17"
Column_lanZuan = "di32_18"
Column_Grade = "di32_19"
Column_MountID = "di32_20"
Column_FTVIP = "di32_21"

SQL = "select di32_11, di32_9, di32_7, di32_0, di32_1, di32_10, di32_13, di32_24, array from role_data where role_id = %s;"

#正式接口
def RoleInfo(request):
	serverid = request.BodyGet("AreaId")
	role_id = request.BodyGet("RoleId")
	
	con = DBHelp.ConnectMasterDBByID_HasExcept(serverid)
	if not con:
		con = DBHelp.ConnectMasterDBByID_Union_HasExcept(serverid)
		if not con:
			return request.ErrorResponse(-1007, "area error")
	with con as cur:
		cur.execute(SQL, role_id)
		result = cur.fetchall()
		if not result:
			return request.response({}, 1)
		
		# array  i64 i32 i16 i8  di8 i1  di1 di64 ci8 cd objs
		#Reputation, Physical, GuildId
		Level, Fight, Gender, LastLoginTime, OnlineTime, RegisterTime, PayStone, RewardStone, array = result[0]
		
		array = Serialize.String2PyObjEx(array)
		i32 = struct.unpack("i" * (len(array[1]) / 4), array[1])
		i16 = struct.unpack("h" * (len(array[2]) / 2), array[2])
		
		Reputation = i32[EnumInt32.enReputation]
		Physical = i16[EnumInt16.TiLi]
		GuildId = i32[EnumInt32.UnionID]
		
		return request.response({"RoleId" : str(role_id) , "Level" : Level, "Reputation" :Reputation, \
						"Physical" : Physical, "Fight" : Fight, "GuildId" : GuildId, \
						"Gender" : Gender, "LastLoginTime" : str(LastLoginTime), "OnlineTime" :OnlineTime,\
						"RegisterTime" : str(RegisterTime), "PayStone" : PayStone, "RewardStone" : RewardStone})
