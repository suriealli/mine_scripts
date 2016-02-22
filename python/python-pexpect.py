#!/usr/bin/env python2.7
#encoding=utf8

from pexpect import *
import sys

#child = pexpect.spawn('ssh -o StrictHostKeyChecking=no -i /home/suriealli/.ssh/Identity -p62919 -lJoklin 121.42.214.133')
#fout = file('1.txt','w')
#child.logfile = fout
#child.expect("Identity\':")
#child.sendline("dazzleq")
###child.expect('\$')
#child.sendline("sudo su")
#child.expect('Joklin:')
#child.sendline('121212')
#child.expect('#')
#child.sendline('ls')
#child.expect('#')


run('ssh -o StrictHostKeyChecking=no -i /home/suriealli/.ssh/Identity -p62919 -lJoklin 121.42.214.133',events={'Identity\':':'dazzleq','\$':'ls'})
