#!/usr/bin/env python

import MySQLdb

try:
    conn = MySQLdb.connect(host='localhost',user='root',passwd='UQEnZcVXdjzA3uZC',db='mysql',port='4580')
    cursor = conn.cursor()
    cursor.excute('select user,host from user;')
    cursor.close()
    conn.close()
except MySQLdb.Error,e:
    print 'MySQLdb Error:' ,e
