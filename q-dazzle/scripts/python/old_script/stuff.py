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
             
while True: 
 user=raw_input('What user do you want to search?')
 U=file('user.txt') 
 match=0
 while True:  
        line=U.readline()
        if len(line) == 0:break
        if user=='':
                print '\033[1;31;40mPlease input the user your want to search!\033[0m'
                match = 1
		break
        if user in line:
                print line
                match = 1
                continue
        else:                               
                pass                        
 if match == 0:                      
	print '\033[1;36;40mNo user here!\033[0m'
