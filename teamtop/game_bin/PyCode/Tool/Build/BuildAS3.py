#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Tool.Build.BuildAS3")
#===============================================================================
# 构建AS3模块
#===============================================================================
import urllib

As3FileHead = '''package  common.Enum
{
	/**
	 * 所有程序中的常量在这里定义
	 * @author 自动生成
	 */
	public class %(classname)s
	{
'''
As3FileTail = '''
	}
}
'''
As3MsgDefine = '''		public static const %s:int = %s;	//%s\n'''

def BuildList(d, classname):
	fd = {"classname":classname}
	with open("%(classname)s.as" % fd, "w") as f:
		f.write(As3FileHead % fd)
		for info in d[classname]:
			f.write(As3MsgDefine % info)
		f.write(As3FileTail)

def BuildCodingRange(d, classname):
	fd = {"classname":classname}
	with open("%(classname)s.as" % fd, "w") as f:
		f.write(As3FileHead % fd)
		for k, v, z in d[classname]:
			k1 = k + "_Min"
			k2 = k + "_Max"
			z1 = z + " :Min"
			z2 = z + " : Max"
			f.write(As3MsgDefine % (k1, v[0], z1))
			f.write(As3MsgDefine % (k2, v[1], z2))
		f.write(As3FileTail)
	
if __name__ == "__main__":
	httpbody = urllib.urlopen("http://192.168.8.110:8000/Tool/SyncData/Reg_Interface/").read()
	d = eval(httpbody)
	BuildList(d, "MsgDefine")
	BuildCodingRange(d, "Coding")
	BuildList(d, "EnumI64")
	BuildList(d, "EnumI32")
	BuildList(d, "EnumI16")
	BuildList(d, "EnumI8")
	BuildList(d, "EnumI1")
	BuildList(d, "EnumDayInt1")
	BuildList(d, "EnumDayInt8")
	BuildList(d, "EnumDynamicInt64")
	BuildList(d, "EnumDisperseInt32")
	BuildList(d, "EnumObj")
	BuildList(d, "EnumTempInt64")
	BuildList(d, "EnumCD")
	BuildList(d, "EnumOdata")
	BuildList(d, "EnumPackage")
	BuildList(d, "PropertyEnum")
	BuildList(d, "Fight")
	BuildList(d, "EnumAppearance")
	BuildList(d, "Social")
	BuildList(d, "EnumRoleStatus")
	BuildList(d, "EnumSysData")
	BuildList(d, "EnumGameConfig")
	BuildList(d, "EnumTeamType")
	BuildList(d, "EnumNPCData")
	BuildList(d, "EnumMail")
	BuildList(d, "EnumFightStatistics")
	BuildList(d, "CircularDefine")
	BuildList(d, "EnumRNPC")
	BuildList(d, "EnumSuperCards")
	#修改了这个，记得运行 upload.bat
	print "BULID OK ......."

