#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#===============================================================================
# 定义
#===============================================================================
# 角色数据水平分表个数（不能随便改的）
ROLE_HORIZONTAL_TABLE = 12
# 数据库线程数（不能随便改的）
DB_THREAD_NUM = 6
#===============================================================================
# 多线程的某个逻辑对表进行较长时间的操作（比如保存角色数据）的时候会导致数据库死锁（范围锁引起的）。
# 在这种情况下，可进行水平分表解决问题，使得每个分表只会由1个线程访问。
# 如果水平分表有12个，那么线程数就只能是1、2、3、4、6、12个才可以保证上述条件。
#===============================================================================
assert ROLE_HORIZONTAL_TABLE % DB_THREAD_NUM == 0

# 是否让服务器启动时串行载入数据
SERIAL_LOAD = False
