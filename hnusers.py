import hn
# for user in ['patio11','tptacek','anigbrowl','pg','raganwald']:
# 	hn.updateuser(user)
for x in hn.latestcomments(['patio11','tptacek']):
	print x['comment']
	print ' '