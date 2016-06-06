#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# XRLAM("Util.Time")
#===============================================================================
# 时间辅助模块
#===============================================================================
import time
import datetime
from Common.Other import GlobalPrompt

#import Util.Time as A
#print A.UnixTime2DateTime()

def UnixTime2DateTime(unix_time):
	'''
	将一个Unix时间转换为date time
	@param unix_time:Unix时间
	'''
	tp = time.localtime(unix_time)
	return datetime.datetime(tp[0], tp[1], tp[2], tp[3], tp[4], tp[5])

def DateTime2UnitTime(dt):
	'''
	将一个date time转换为Unix时间
	@param dt:ate time
	'''
	return int(time.mktime(dt.timetuple()))

def DateTime2String(dt):
	'''
	将一个date time转换为字符串
	'''
	return dt.strftime("%Y-%m-%d %H:%M:%S")

def String2DateTime(s):
	'''
	将一个字符串转换为date time
	'''
	datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

def DeltaToString(delta):
	'''
	将一个time delta对象转换为字符串表示
	@param delta:time delta对象
	'''
	return DifToString(delta.total_seconds())

ONE_MINUTE = 60
ONE_HOUR = 3600
ONE_DAY = 24 * 3600
def DifToString(second):
	'''
	将一个相差的秒数转为字符串表示
	@param second:秒数
	'''
	l = []
	day, second = divmod(second, ONE_DAY)
	if day: l.append(GlobalPrompt.TIME_STRING_DAY_1 % day)
	hour, second = divmod(second, ONE_HOUR)
	if hour: l.append(GlobalPrompt.TIME_STRING_HOUR_1 % hour)
	minute, second = divmod(second, ONE_MINUTE)
	if minute: l.append(GlobalPrompt.TIME_STRING_MINUTE_1 % minute)
	if second: l.append(GlobalPrompt.TIME_STRING_SECOND_1 % second)
	return "".join(l)

def DifToString2(second):
	'''
	将一个相差的秒数转为字符串表示
	@param second:秒数
	'''
	day, second = divmod(second, ONE_DAY)
	if day:
		return GlobalPrompt.TIME_STRING_DAY_2 % day
	hour, second = divmod(second, ONE_HOUR)
	if hour:
		return GlobalPrompt.TIME_STRING_HOUR_2 % hour
	minute, second = divmod(second, ONE_MINUTE)
	if minute:
		return GlobalPrompt.TIME_STRING_MINUTE_2 % minute
	return GlobalPrompt.TIME_STRING_SECOND_2 % second

def GetYearWeek(dt):
	'''
	一年中的第几周（以星期一为一周的开始），类型为decimal number，范围[0,53]
	在度过新年时，直到一周的全部7天都在该年中时，才计算为第0周
	只当指定了年份才有效
	@param dt:日期
	'''
	return int(dt.strftime("%W"))

BASE_DATETIME = datetime.datetime(2013, 12, 23)
def GetAllDays(dt):
	'''
	返回天对应的一个整数（连续的）
	@param dt:日期
	'''
	delta = dt - BASE_DATETIME
	return delta.days

def GetAllWeeks(dt):
	'''
	返回周对应的一个整数（连续的）
	星期一作为一周的第一天
	@param dt:日期
	'''
	return GetAllDays(dt) / 7

def GetWeekDay(dt):
	'''
	返回该时间是这一周的第几天 [1, 7]
	星期一为1 ... 星期天为7
	@param dt:
	'''
	return dt.isoweekday()

if __name__ == "__main__":
	dt = datetime.datetime(2014, 1, 6)
	print GetAllDays(dt)
	print GetAllWeeks(dt)
