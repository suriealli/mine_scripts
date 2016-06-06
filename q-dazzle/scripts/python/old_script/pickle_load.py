#!/usr/bin/env python
import pickle
file=open ('pkl.dmp','r')
var=pickle.load(file)
file.close()

var['Jal'][2]='Do not like Joklin'
var['Joklin'][2]='but loves Jal'

file=open('pkl.dmp','w')
pickle.dump(var,file)
file.close()
