#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 钉子，用于定位辅助目录的
#===============================================================================
import os

CurFloderPath = os.path.dirname(os.path.realpath(__file__)) + os.sep
PyHelpFloderPath = CurFloderPath

if __name__ == "__main__":
	print CurFloderPath
	print PyHelpFloderPath

