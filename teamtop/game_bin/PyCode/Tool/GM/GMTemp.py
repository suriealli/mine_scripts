#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Tool.GM.GMTemp")
#===============================================================================
# 模块级GM工具
#===============================================================================
import sys
import StringIO
import Environment
from Tool.GM import GMCMD

ROLE_ID = None
ROLE_NAME = None

def set_role_id(role_id):
	global ROLE_ID
	ROLE_ID = role_id

def set_role_name(role_name):
	global ROLE_NAME
	ROLE_NAME = role_name

def handle(file_path):
	file_path = file_path if file_path.endswith(".py") else file_path[:-1]
	command = None
	with open(file_path) as f:
		for line in f:
			if command is None:
				if line.startswith("# you gm command"):
					command = []
					if ROLE_ID:
						command.append("role = GetRoleByRoleID(%s)\n" % ROLE_ID)
					elif ROLE_NAME:
						command.append("role = GetRoleByRoleName('%s')\n" % ROLE_NAME)
					else:
						command.append("role = GetRoleByIP('%s')\n" % Environment.IP)
					command.append("from Game.Role.Data import * \nfrom Common.Other import EnumGameConfig \nfrom Game.Role.RoleGM import *\n")
			else:
				command.append(line)
	gm = GMCMD.GMConnect(Environment.IP, 9000, True)
	gm.iamgm()
	gm.gmcommand("".join(command))
	OutBuff = StringIO.StringIO()
	sys.stdout = OutBuff


