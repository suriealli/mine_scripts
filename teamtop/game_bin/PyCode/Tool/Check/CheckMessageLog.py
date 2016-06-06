#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 检测并整理自动生成的消息和日志
#===============================================================================
import Environment
from Util.PY import Load
from Common.Message import AutoMessage
from ComplexServer.Log import AutoLog

if __name__ == "__main__":
	Environment.HasLogic = True
	AutoMessage.SvnUp()
	AutoLog.SvnUp()
	Load.LoadPartModule("Common")
	Load.LoadPartModule("Global")
	Load.LoadPartModule("ComplexServer")
	Load.LoadPartModule("DB")
	Load.LoadPartModule("Game")
	Load.LoadPartModule("Control")
	AutoMessage.SvnCommitEx()
	AutoLog.SvnCommitEx()
	print "End"

