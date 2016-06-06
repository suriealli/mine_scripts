#!/usr/bin/env python
# -*- coding:UTF-8 -*-
ProcessType = "All"
ProcessID = 1
ListenPort = 9000
#automatic_start
# 有13个Py函数定义

def write( carg):
	'''
	重定向Python输出
	@param carg : string
	@return: None 
			 line 109 Py_RETURN_NONE;
	@warning: if (!PyString_CheckExact(arg))
	@warning: GE::Uint16 uSize = static_cast<GE::Uint16>(PyObject_Length(arg));
	@see : { "write", write, METH_O, "重定向Python输出 "},
	'''

def RedirectOutBuf( carg):
	'''
	重定向进程输出和错误流
	@param carg : string
	@return: None 
			 line 124 Py_RETURN_NONE;
	@warning: if (!PyString_CheckExact(arg))
	@see : { "RedirectOutBuf", RedirectOutAndErrBuf, METH_O, "重定向进程输出和错误流 "},
	'''

def AllotGUID64( ):
	'''
	分配一个全球唯一ID
	@return: UI64 
			 line 129 return GEPython::PyObjFromUI64(GEGUID64::Instance()->AllotGUID());
	@see : { "AllotGUID64", AllotGUID64, METH_NOARGS, "分配一个全球唯一ID "},
	'''

def PackB8( uI32_1, uI32_0):
	'''
	将俩个B4打包成为B8，第一个参数是高位B4，第二个参数是低位B4
	@param uI32_1 : UI32
	@param uI32_0 : UI32
	@return: UI64 
			 line 141 return GEPython::PyObjFromUI64(b8.UI64());
	@see : { "PackB8", PackB8, METH_VARARGS, "将俩个B4打包成为B8，第一个参数是高位B4，第二个参数是低位B4 "},
	'''

def UnpackB8( ui64):
	'''
	将B8解包成两个B4，第一个结果是高位B4，第二个结果是低位B4
	@param ui64 : UI64
	@return: UI32,UI32 
			 line 152 return Py_BuildValue("II", b8.UI32_1(), b8.UI32_0());
	@see : { "UnpackB8", UnpackB8, METH_O, "将B8解包成两个B4，第一个结果是高位B4，第二个结果是低位B4 "},
	'''

def PackB4( uI16_1, uI16_0):
	'''
	将俩个Uint16打包成为B4，第一个参数是高位Uint16，第二个参数是低位Uint16
	@param uI16_1 : UI16
	@param uI16_0 : UI16
	@return: UI32 
			 line 164 return GEPython::PyObjFromUI32(b4.UI32());
	@see : { "PackB4", PackB4, METH_VARARGS, "将俩个Uint16打包成为B4，第一个参数是高位Uint16，第二个参数是低位Uint16 "},
	'''

def UnpackB4( ui32):
	'''
	将B4解包成两个Uint16，第一个结果是高位Uint16，第二个结果是低位Uint16
	@param ui32 : UI32
	@return: UI16,UI16 
			 line 175 return Py_BuildValue("HH", b4.UI16_1(), b4.UI16_0());
	@see : { "UnpackB4", UnpackB4, METH_O, "将B4解包成两个Uint16，第一个结果是高位Uint16，第二个结果是低位Uint16 "},
	'''

def UnpackB4ToUI8( ui32):
	'''
	将UI32解包成四个Uint8
	@param ui32 : UI32
	@return: UI8,UI8,UI8,UI8 
			 line 186 return Py_BuildValue("BBBB", b4.UI8_3(), b4.UI8_2(), b4.UI8_1(), b4.UI8_0());
	@see : { "UnpackB4ToUI8", UnpackB4ToUI8, METH_O, "将UI32解包成四个Uint8  "},
	'''

def PyObjPackSize( arg):
	'''
	计算Python对象打包长度
	@param arg : PyObject*
	@return: I32 
			 line 192 return GEPython::PyObjFromI32(Size);
	@warning: GE::Int32 Size = PackMessage::Instance()->PyObjSize(arg, MAX_UINT16);
	@see : { "PyObjPackSize", PyObjPackSize, METH_O, "计算Python对象打包长度 "},
	'''

def PyErrPrint( ):
	'''
	辅助寻找未捕获的异常
	@return: True 
			 line 200 Py_RETURN_TRUE;
	@return: False 
			 line 204 Py_RETURN_FALSE;
	@see : { "PyErrPrint", PyErrPrint, METH_NOARGS, "辅助寻找未捕获的异常 "},
	'''

def Crash( ):
	'''
	崩溃
	@return: None 
			 line 211 Py_RETURN_NONE;
	@see : { "Crash", Crash, METH_NOARGS, "崩溃 "},
	'''

def SetStackWarnFun( arg):
	'''
	设置打印Python堆栈函数
	@param arg : PyObject*
	@return: None 
			 line 217 Py_RETURN_NONE;
	@warning: GEProcess::Instance()->SetStackWarnFun(arg);
	@see : { "SetStackWarnFun", SetStackWarnFun, METH_O, "设置打印Python堆栈函数 "},
	'''

def MallocTrim( ):
	'''
	Linux下强制归还free了的内存
	@return: None 
			 line 225 Py_RETURN_NONE;
	@see : { "MallocTrim", MallocTrim, METH_NOARGS, "Linux下强制归还free了的内存 "},
	'''

#automatic_end


def MallocTrim():
	pass


