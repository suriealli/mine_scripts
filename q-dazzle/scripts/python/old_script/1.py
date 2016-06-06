print '\033[1;31;40m'
print '*' * 50
#print '*HOST:\t', request.META.get('REMOTE_ADDR')
print '*URI:\t', request.path
#print '*ARGS:\t', QueryDict(request.body)
print '*TIME:\t', time.time() - request.start_time
print '*' * 50
print '\033[0m'
