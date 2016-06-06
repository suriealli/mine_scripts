#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 构建辅助Python代码
#===============================================================================
import os
import Auto_Nail
import Environment
import DynamicPath
from Util.C import CPY


PYHELP_FOLDER = Auto_Nail.PyHelpFloderPath
GAMEENGINE_FOLDER = DynamicPath.CFloderPath + "GameEngine" + os.sep
COMPLEXSERVER_FOLDER = DynamicPath.CFloderPath + "ComplexServer" + os.sep

def BuildOne(name, cpp_folder = COMPLEXSERVER_FOLDER):
	pb = CPY.PyHelp("c%s.py" % name, PYHELP_FOLDER, cpp_folder)
	pb.Append("Py%s.cpp" % name)
	pb.Parse()

def CPYBuild():
	# 只有Win下才需要运行此函数
	assert Environment.IsWindows
	BuildOne("Process", GAMEENGINE_FOLDER)
	BuildOne("DateTime", GAMEENGINE_FOLDER)
	BuildOne("NetEnv", GAMEENGINE_FOLDER)
	BuildOne("NetMessage", GAMEENGINE_FOLDER)
	
	pb = CPY.PyHelp("cRole.py", PYHELP_FOLDER, COMPLEXSERVER_FOLDER)
	pb.Append("PyRole.cpp")
	pb.Append("PyRoleArray.h")
	pb.Append("PyRoleArray.cpp")
	pb.Append("PyRoleGather.h")
	pb.Append("PyRoleGather.cpp")
	pb.Append("PyRoleContain.h")
	pb.Append("PyRoleContain.cpp")
	pb.Parse()
	
	BuildOne("ComplexServer")
	BuildOne("GatewayForward")
	BuildOne("RoleDataMgr")
	BuildOne("RoleMgr")
	BuildOne("SceneMgr")
	BuildOne("PublicScene")
	BuildOne("NPC")
	BuildOne("NPCMgr")
	BuildOne("ScriptMgr")
	BuildOne("LogTransaction")

	
if __name__ == "__main__":
	CPYBuild()
	print "--------------------------OK--------------------------"
