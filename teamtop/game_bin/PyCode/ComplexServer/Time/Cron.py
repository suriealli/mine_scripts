#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 定时触发函数模块
#===============================================================================
import datetime
import traceback
import cDateTime
import cComplexServer
from ComplexServer import Init
from Util import Trace

if "_HasLoad" not in dir():
	# cron分配的Key
	CronKey = 0

def GetNewKey():
	'''
	获取一个新的Key
	'''
	global CronKey
	CronKey += 1
	return CronKey

def AsDatetime(arg):
	'''
	转化为datetime.datetime对象
	@param arg:参数
	'''
	if type(arg) == datetime.datetime:
		return arg
	else:
		return datetime.datetime(*arg)

class Cron(object):
	def __init__(self, fun):
		# 每个cron，必定有的key
		self.key = GetNewKey()
		# 回调函数
		self.fun = fun
		# 天匹配、小时匹配和时间匹配的py代码语义
		self.dayCodeList = []
		self.hourCodeList = []
		self.timeCodeList = []
		# 匹配项定义链
		self.chainIdx = 0
	
	def __ChainCheck(self, val):
		# 检测函数执行步骤是否正确
		if self.chainIdx >= val:
			raise Exception("you condition sequence is Error.the correct sequence is y m d H M S w W D T Driver*")
		self.chainIdx = val
	
	def __SafeCode(self, pyCode):
		# 安全的py代码语义
		return "(" + pyCode + ")"
	
	def __MatchOne(self, dic, name):
		# 从字典中找到一个匹配项，并定义匹配之
		if name in dic:
			getattr(self, name)(dic[name])
			del dic[name]
	
	def CompileCondition(self):
		# 修正
		if not self.dayCodeList:
			self.dayCodeList.append("True")
		if not self.hourCodeList:
			self.hourCodeList.append("True")
		if not self.timeCodeList:
			self.timeCodeList.append("True")
		# 编译py代码
		self.dayCode = compile(" and ".join(self.dayCodeList), "<string>", "eval")
		self.hourCode = compile(" and ".join(self.hourCodeList), "<string>", "eval")
		self.timeCode = compile(" and ".join(self.timeCodeList), "<string>", "eval")
	
	def y(self, pyCode):
		'''
		对年的匹配方式。内置符号：y 当前的年份[2000,2038]
		@param pyCode:简单py代码，如 y==2012
		'''
		self.__ChainCheck(1)
		y = 2012; _ = y
		eval(pyCode)
		self.dayCodeList.append(self.__SafeCode(pyCode))
		self.timeCodeList.append(self.__SafeCode(pyCode))
		return self
	
	def m(self, pyCode):
		'''
		对月的匹配方式。内置符号：m 当前的月份[1,12]
		@param pyCode:简单py代码，如 1<=m<=6
		'''
		self.__ChainCheck(2)
		m = 1; _ = m
		eval(pyCode)
		self.dayCodeList.append(self.__SafeCode(pyCode))
		self.timeCodeList.append(self.__SafeCode(pyCode))
		return self
	
	def d(self, pyCode):
		'''
		对天的匹配方式。内置符号：d 当前月的天[1,?]
		@param pyCode:简单py代码，如 d%3==0
		'''
		self.__ChainCheck(3)
		d = 1; _ = d
		eval(pyCode)
		self.dayCodeList.append(self.__SafeCode(pyCode))
		self.timeCodeList.append(self.__SafeCode(pyCode))
		return self
	
	def H(self, pyCode):
		'''
		对小时的匹配方式。内置符号：H 当前小时[0,23]
		@param pyCode:简单py代码，如 H==4
		'''
		self.__ChainCheck(4)
		H = 0; _ = H
		eval(pyCode)
		self.hourCodeList.append(self.__SafeCode(pyCode))
		self.timeCodeList.append(self.__SafeCode(pyCode))
		return self
	
	def M(self, pyCode):
		'''
		对分钟的匹配方式。内置符号：M 当前的分钟[0,59]
		@param pyCode:简单py代码，如 M==50 or M==55 or M==59
		'''
		self.__ChainCheck(5)
		M = 0; _ = M
		eval(pyCode)
		self.timeCodeList.append(self.__SafeCode(pyCode))
		return self
	
	def S(self, pyCode):
		'''
		对秒钟的匹配方式。内置符号：S 当前的秒钟[0,59]
		@param pyCode:简单py代码，如 d%30==0
		'''
		self.__ChainCheck(6)
		S = 0; _ = S
		eval(pyCode)
		self.timeCodeList.append(self.__SafeCode(pyCode))
		return self
	
	def w(self, pyCode):
		'''
		对星期几的匹配方式。内置符号：w 星期几[1, 7] 1表示星期一
		@param pyCode:简单py代码，如 w==6 or w==7
		'''
		self.__ChainCheck(7)
		w = 1; _ = w
		eval(pyCode)
		self.dayCodeList.append(self.__SafeCode(pyCode))
		self.timeCodeList.append(self.__SafeCode(pyCode))
		return self
	
	def W(self, pyCode):
		'''
		对星期数的匹配方式。内置符号：W 今年的第几周 [0, 53]
		@param pyCode:简单py代码，如 W%4==0
		'''
		self.__ChainCheck(8)
		W = 0; _ = W
		eval(pyCode)
		self.dayCodeList.append(self.__SafeCode(pyCode))
		self.timeCodeList.append(self.__SafeCode(pyCode))
		return self
	
	def D(self, pyCode):
		'''
		对日期(年, 月, 日)的匹配方式。内置符号：D 现在的日期（datetime.date对象）  _D datetime.date类
		@param pyCode:简单py代码，如 D<_D(2012,2,1)
		'''
		self.__ChainCheck(9)
		_D = datetime.date
		D = _D(2011, 1, 1); _ = D
		eval(pyCode)
		self.dayCodeList.append(self.__SafeCode(pyCode))
		self.timeCodeList.append(self.__SafeCode(pyCode))
		return self
	
	def T(self, pyCode):
		'''
		对某天时间(时, 分, 秒)的匹配方式。内置符号：T 现在的时间（datetime.time对象）  _T datetime.time类
		注意的是，如果有此匹配项会导致该cron按每小时分类失效
		@param pyCode:简单的py代码，如 T<_T(5,4,11)
		'''
		self.__ChainCheck(10)
		_T = datetime.time
		T = _T(0, 0, 0); _ = T
		eval(pyCode)
		self.hourCodeList = ["True"]
		self.timeCodeList.append(self.__SafeCode(pyCode))
		return self
	
	def MatchDictHour(self, **kw):
		'''
		将字典中无序的匹配项按照需求定义匹配之
		@param dic:
		'''
		self.__MatchOne(kw, "y")
		self.__MatchOne(kw, "m")
		self.__MatchOne(kw, "d")
		self.__MatchOne(kw, "H")
		#self.__MatchOne(kw, "M")
		#self.__MatchOne(kw, "S")
		self.__MatchOne(kw, "w")
		self.__MatchOne(kw, "W")
		self.__MatchOne(kw, "D")
		self.__MatchOne(kw, "T")
		if len(kw) != 0:
			for item in kw.iteritems():
				print ' %s = "%s";' % item,
			print "GE_EXC, cron unknown condition."
		return self
	
	def MatchDictMinute(self, **kw):
		'''
		将字典中无序的匹配项按照需求定义匹配之
		@param dic:
		'''
		self.__MatchOne(kw, "y")
		self.__MatchOne(kw, "m")
		self.__MatchOne(kw, "d")
		self.__MatchOne(kw, "H")
		self.__MatchOne(kw, "M")
		#self.__MatchOne(kw, "S")
		self.__MatchOne(kw, "w")
		self.__MatchOne(kw, "W")
		self.__MatchOne(kw, "D")
		self.__MatchOne(kw, "T")
		if len(kw) != 0:
			for item in kw.iteritems():
				print ' %s = "%s";' % item,
			print "GE_EXC, cron unknown condition"
		return self
	
	def MatchDictSecond(self, **kw):
		'''
		将字典中无序的匹配项按照需求定义匹配之
		@param dic:
		'''
		self.__MatchOne(kw, "y")
		self.__MatchOne(kw, "m")
		self.__MatchOne(kw, "d")
		self.__MatchOne(kw, "H")
		self.__MatchOne(kw, "M")
		self.__MatchOne(kw, "S")
		self.__MatchOne(kw, "w")
		self.__MatchOne(kw, "W")
		self.__MatchOne(kw, "D")
		self.__MatchOne(kw, "T")
		if len(kw) != 0:
			for item in kw.iteritems():
				print ' %s = "%s";' % item,
			print "GE_EXC, cron unknown condition"
		return self
	
	def IsMatchDay(self, now, localDict):
		'''
		判断在当前天中是否有可能匹配该cron
		'''
		return eval(self.dayCode, globals(), localDict)
	
	def IsMatchHour(self, now, localDict):
		'''
		判断当前小时中是否有可能匹配该cron
		'''
		return eval(self.hourCode, globals(), localDict)
	
	def IsMatchNow(self, now, localDict):
		'''
		判断当前时间是否匹配该cron
		'''
		return eval(self.timeCode, globals(), localDict)

class CronMgr(object):
	def __init__(self):
		# 保存的cron字典
		self.cronDict = {}
		# 标记是否已经分类
		self.hasSort = False
	
	def AppendCron(self, cron):
		# 编译
		cron.CompileCondition()
		# 添加一个cron
		self.cronDict[cron.key] = cron
		if self.hasSort:
			self.Sort(True)
			print "GE_EXC, append cron on server run."
			Trace.StackWarn("AppendCron")
		return cron.key
	
	def Sort(self, force = False):
		'''
		分类
		'''
		
		if self.hasSort and not force:
			return
		now = cDateTime.Now()
		new_day = datetime.datetime(now.year, now.month, now.day)
		localDict = {"y":new_day.year, "m":new_day.month, "d":new_day.day,
			"H":new_day.hour, "M": new_day.minute, "S":new_day.second,
			"w":new_day.isoweekday(), "W":int(new_day.strftime("%W")),
			"D":new_day.date(), "T":new_day.time(),
			"_D":datetime.date, "_T":datetime.time}
		self.OnNewDay(now, localDict)
		new_hour = datetime.datetime(now.year, now.month, now.day, now.hour)
		localDict = {"y":new_hour.year, "m":new_hour.month, "d":new_hour.day,
			"H":new_hour.hour, "M": new_hour.minute, "S":new_hour.second,
			"w":new_hour.isoweekday(), "W":int(new_hour.strftime("%W")),
			"D":new_hour.date(), "T":new_hour.time(),
			"_D":datetime.date, "_T":datetime.time}
		self.OnNewHour(now, localDict)
		#print "GREEN, sort cron."
		
	def OnNewDay(self, now, localDict):
		'''
		当新的一天了，需要驱动调用的函数。
		在这里会将今天有可能要调用的cron索取出来
		@param now:当前时间
		@param localDict:当前时间的符号字典
		'''
		self.cronDayDict = {}
		for key, cron in self.cronDict.iteritems():
			if cron.IsMatchDay(now, localDict):
				self.cronDayDict[key] = cron
	
	def OnNewHour(self, now, localDict):
		'''
		当新的一小时了，需要驱动调用的函数。
		在这里会将今天这个小时有可能要调用的cron索取出来
		@param now:当前时间
		@param localDict:当前时间的符号字典
		'''
		self.cronHourDict = {}
		for key, cron in self.cronDayDict.iteritems():
			if cron.IsMatchHour(now, localDict):
				self.cronHourDict[key] = cron
		# 此时cron都分类了
		self.hasSort = True
		# 返回该小时内可能需要调用的cron个数
		return len(self.cronHourDict)
	
	def OnMatch(self, now, localDict):
		'''
		当到了触发时间，需要驱动调用的函数。
		在这个函数中会匹配当前时间，触发回调函数
		'''
		# 保证是分好类了的
		self.Sort()
		# 出错误的key
		errorKeys = []
		# 触发回调函数
		for cron in self.cronHourDict.itervalues():
			if not cron.IsMatchNow(now, localDict):
				continue
			try:
				cron.fun()
			except:
				errorKeys.append(cron.key)
				traceback.print_exc()
		# 函数调用发送了错误，删除之
		if not errorKeys:
			return
		
#		for key in errorKeys:
#			if key in self.cronDict: del self.cronDict[key]
#			if key in self.cronHourDict: del self.cronHourDict[key]
#			if key in self.cronDayDict: del self.cronDayDict[key]

if "_HasLoad" not in dir():
	# 3个不同级别的cron
	CronMgrByHour = CronMgr()
	CronMgrByMinute = CronMgr()
	CronMgrBySecond = CronMgr()
	# 本地计算字典
	now = cDateTime.Now()
	localDict = {"y":now.year, "m":now.month, "d":now.day,
		"H":now.hour, "M": now.minute, "S":now.second,
		"w":now.isoweekday(), "W":int(now.strftime("%W")),
		"D":now.date(), "T":now.time(),
		"_D":datetime.date, "_T":datetime.time}

def BeforeNewDay():
	now = cDateTime.Now()
	localDict["y"] = now.year
	localDict["m"] = now.month
	localDict["d"] = now.day
	localDict["H"] = now.hour
	localDict["M"] = now.minute
	localDict["S"] = now.second
	localDict["w"] = now.isoweekday()
	localDict["W"] = int(now.strftime("%W"))
	localDict["D"] = now.date()
	localDict["T"] = now.time()
	# 按天分类
	CronMgrByHour.OnNewDay(now, localDict)
	CronMgrByMinute.OnNewDay(now, localDict)
	CronMgrBySecond.OnNewDay(now, localDict)

def BeforeNewHour():
	now = cDateTime.Now()
	localDict["H"] = now.hour
	localDict["M"] = now.minute
	localDict["S"] = now.second
	localDict["T"] = now.time()
	# 按小时分类
	CronMgrByHour.OnNewHour(now, localDict)
	CronMgrByMinute.OnNewHour(now, localDict)
	CronMgrBySecond.OnNewHour(now, localDict)
	# 触发小时级匹配
	CronMgrByHour.OnMatch(now, localDict)

def BeforeNewMinute():
	now = cDateTime.Now()
	localDict["M"] = now.minute
	localDict["S"] = now.second
	localDict["T"] = now.time()
	# 触发分钟级的匹配
	CronMgrByMinute.OnMatch(now, localDict)

def OnNewSecond():
	now = cDateTime.Now()
	localDict["S"] = now.second
	localDict["T"] = now.time()
	# 触发秒级的匹配
	CronMgrBySecond.OnMatch(now, localDict)

def OnInit():
	now = cDateTime.Now()
	localDict = {"y":now.year, "m":now.month, "d":now.day,
		"H":now.hour, "M": now.minute, "S":now.second,
		"w":now.isoweekday(), "W":int(now.strftime("%W")),
		"D":now.date(), "T":now.time(),
		"_D":datetime.date, "_T":datetime.time}
	CronMgrByHour.Sort(True)
	CronMgrByMinute.Sort(True)
	CronMgrBySecond.Sort(True)

if "_HasLoad" not in dir():
	# 注册驱动cron
	cComplexServer.RegBeforeNewDayCallFunction(BeforeNewDay)
	cComplexServer.RegBeforeNewHourCallFunction(BeforeNewHour)
	cComplexServer.RegBeforeNewMinuteCallFunction(BeforeNewMinute)
	cComplexServer.RegPerSecondCallFunction(OnNewSecond)
	Init.InitCallBack.RegCallbackFunction(OnInit)

def CronDirveByHour(overtime, fun, **kwgv):
	'''
	设置为小时级驱动
	在该驱动下，对于匹配的时间的分和秒必定是0
	kwgv如：d = "d%9==0", H = "H>=22"...
	
	@param overtime:过期时间
	@param fun:回调函数 def fun()
	'''
	if AsDatetime(overtime) < cDateTime.Now():
		return
	cron = Cron(fun)
	cron.MatchDictHour(**kwgv)
	CronMgrByHour.AppendCron(cron)

def CronDriveByMinute(overtime, fun, **kwgv):
	'''
	设置为分钟级驱动
	在该驱动下，对于匹配的时间的秒必定是0
	kwgv如：d = "d%9==0", H = "H>=22"...
	
	@param overtime:过期时间
	@param fun:回调函数 def fun()
	'''
	if AsDatetime(overtime) < cDateTime.Now():
		return
	cron = Cron(fun)
	cron.MatchDictMinute(**kwgv)
	CronMgrByMinute.AppendCron(cron)

def CronDriveBySecond(overtime, fun, **kwgv):
	'''
	设置为分钟级驱动
	kwgv如：d = "d%9==0", H = "H>=22"...
	
	@param overtime:过期时间
	@param fun:回调函数 def fun()
	'''
	if AsDatetime(overtime) < cDateTime.Now():
		return
	cron = Cron(fun)
	cron.MatchDictSecond(**kwgv)
	CronMgrBySecond.AppendCron(cron)

if __name__ == "__main__":
	import Environment
	Environment
	sec = datetime.timedelta(seconds=1)
	now = datetime.datetime(2012, 1, 1)
	edt = datetime.datetime(2013, 1, 1)
	def P():
		print cDateTime.Now()
	
	CronDriveBySecond((2013, 1, 1), P, m="m==1", d="1<d<=5", H="H%3==0", M="M>20", S="S%17==2", T="T<_T(15, 22, 38)")
	
	OnInit()
	
	print "Start", datetime.datetime.now()
	lday = now.day
	lhour = now.hour
	lminute = now.minute
	while now < edt:
		now += sec
		cDateTime.NDT = now
		if lminute != now.minute:
			if lhour != now.hour:
				if lday != now.day:
					lday = now.day
					BeforeNewDay()
				lhour = now.hour
				BeforeNewHour()
			lminute = now.minute
			BeforeNewMinute()
		OnNewSecond()
	
	print "End", datetime.datetime.now()

