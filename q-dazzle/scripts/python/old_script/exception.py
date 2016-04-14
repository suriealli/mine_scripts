#!/usr/bin/env python

import time
for i in range(1, 600):
 try:
	print  "the No. now is %s" % i
	time.sleep(0.01)
 except KeyboardInterrupt:
	print "please do not stop me"
	continue
