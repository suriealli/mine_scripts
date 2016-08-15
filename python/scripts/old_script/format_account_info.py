#/usr/bin/env python
import pickle
account_info = {'Joklin':['Jal123',15000,15000],
		'Jal':['Joklin123',15000,15000],
		}
f=file('accout_info','wb')
pickle.dump(account_info,f)
f.close
