#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#automatic_start
# 有17个Py函数定义

def Now( ):
	'''
	当前的本地时间
	@return: PyObject* 
			 line 11 return GEDateTime::Instance()->Now().GetObj_NewRef();
	@warning: return GEDateTime::Instance()->Now().GetObj_NewRef();
	@see : { "Now", Now, METH_NOARGS, "当前的本地时间 " },
	'''

def WeekDay( ):
	'''
	星期几（0，星期天；1，星期1 ...）
	@return: UI32 
			 line 16 return GEPython::PyObjFromUI32(GEDateTime::Instance()->WeekDay());
	@see : { "WeekDay", WeekDay, METH_NOARGS, "星期几（0，星期天；1，星期1 ...） " },
	'''

def Year( ):
	'''
	年（年份，如2011
	@return: UI32 
			 line 21 return GEPython::PyObjFromUI32(GEDateTime::Instance()->Year());
	@see : { "Year", Year, METH_NOARGS, "年（年份，如2011 " },
	'''

def Month( ):
	'''
	月（月份，1 -- 12
	@return: UI32 
			 line 26 return GEPython::PyObjFromUI32(GEDateTime::Instance()->Month());
	@see : { "Month", Month, METH_NOARGS, "月（月份，1 -- 12 " },
	'''

def Day( ):
	'''
	日（日期，1 -- 31
	@return: UI32 
			 line 31 return GEPython::PyObjFromUI32(GEDateTime::Instance()->Day());
	@see : { "Day", Day, METH_NOARGS, "日（日期，1 -- 31 " },
	'''

def Hour( ):
	'''
	时（小时，0 -- 23
	@return: UI32 
			 line 36 return GEPython::PyObjFromUI32(GEDateTime::Instance()->Hour());
	@see : { "Hour", Hour, METH_NOARGS, "时（小时，0 -- 23 " },
	'''

def Minute( ):
	'''
	分（分钟，0 -- 59
	@return: UI32 
			 line 41 return GEPython::PyObjFromUI32(GEDateTime::Instance()->Minute());
	@see : { "Minute", Minute, METH_NOARGS, "分（分钟，0 -- 59 " },
	'''

def Second( ):
	'''
	秒（0 -- 59）
	@return: UI32 
			 line 46 return GEPython::PyObjFromUI32(GEDateTime::Instance()->Second());
	@see : { "Second", Second, METH_NOARGS, "秒（0 -- 59） " },
	'''

def YearDay( ):
	'''
	今年的第几天
	@return: UI32 
			 line 51 return GEPython::PyObjFromUI32(GEDateTime::Instance()->YeayDay());
	@see : { "YearDay", YearDay, METH_NOARGS, "今年的第几天 " },
	'''

def Minutes( ):
	'''
	从1970元到现在的分钟数
	@return: UI32 
			 line 56 return GEPython::PyObjFromUI32(GEDateTime::Instance()->Minutes());
	@see : { "Minutes", Minutes, METH_NOARGS, "从1970元到现在的分钟数 " },
	'''

def Seconds( ):
	'''
	从1970元到现在的秒数
	@return: UI32 
			 line 61 return GEPython::PyObjFromUI32(GEDateTime::Instance()->Seconds());
	@see : { "Seconds", Seconds, METH_NOARGS, "从1970元到现在的秒数 " },
	'''

def Days( ):
	'''
	从1970元到现在的天数
	@return: UI32 
			 line 66 return GEPython::PyObjFromUI32(GEDateTime::Instance()->Days());
	@see : { "Days", Days, METH_NOARGS , "从1970元到现在的天数 " },
	'''

def Mseconds( ):
	'''
	进程启动到现在的毫秒数
	@return: UI64 
			 line 71 return GEPython::PyObjFromUI64(GEDateTime::Instance()->MSeconds());
	@see : { "Mseconds", Mseconds, METH_NOARGS , "进程启动到现在的毫秒数 " },
	'''

def TimeZoneSeconds( ):
	'''
	服务端当前进程所在计算机的时区
	@return: I32 
			 line 76 return GEPython::PyObjFromI32(GEDateTime::Instance()->TimeZoneSeconds());
	@see : { "TimeZoneSeconds", TimeZoneSeconds, METH_NOARGS , "服务端当前进程所在计算机的时区 " },
	'''

def GetDST( ):
	'''
	获取服务器是否是夏令时
	@return: I32 
			 line 81 return GEPython::PyObjFromI32(GEDateTime::Instance()->GetDST());
	@see : { "GetDST", GetDST, METH_NOARGS , "获取服务器是否是夏令时 " },
	'''

def SetUnixTime( uUnixTime):
	'''
	设置当前时间
	@param uUnixTime : UI32
	@return: None 
			 line 93 Py_RETURN_NONE;
	@see : { "SetUnixTime", SetUnixTime, METH_O , "设置当前时间 " },
	'''

def SetV( uV):
	'''
	设置时间速度
	@param uV : UI32
	@return: None 
			 line 104 Py_RETURN_NONE;
	@see : { "SetV", SetV, METH_O , "设置时间速度 " },
	'''

#automatic_end
def __Now():
	import datetime
	return datetime.datetime.now()
Now = __Now

def _Seconds():
	import time
	return int(time.time())
Seconds = _Seconds

def _GetDST():
	import time
	return time.localtime().tm_isdst
GetDST = _GetDST

def _Year():
	return 1991
Year=_Year

def _Month():
	return 1
Month = _Month

def _Day():
	return 1
Day = _Day

def _Hour():
	return 1
Hour = _Hour

def _Minute():
	return 1
Minute = _Minute

def _Second():
	return 1
Second = _Second
