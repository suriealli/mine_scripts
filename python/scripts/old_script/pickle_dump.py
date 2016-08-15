#!/usr/bin/env python

import pickle
var_info={
	'Jal':['who is a beauty','hate Joklin',''],
	'Joklin':['who is a poor','hate richer','']
	}
file=open('pkl.dmp','w+')
pickle.dump(var_info,file)
file.close()
