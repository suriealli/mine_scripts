#!/usr/bin/python

name=raw_input('Please input your username:')
while True:
 if name=='Joklin':
	passwd=raw_input('Please input your password:')
	if passwd!='123':
		print 'password incorrect!!!'
		
	else :
		print 'login successfully!!'
		break
 else:
	print 'unreconize username!!'
	name=raw_input('Please input your username:')

