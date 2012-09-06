import sys
import os
from flask import Flask,render_template,request,session,redirect,url_for
import hn
# for user in ['patio11','tptacek','anigbrowl','pg','raganwald']:
# 	hn.updateuser(user)

# for x in hn.latestcomments(['patio11','tptacek']):
# 	print x['comment']
# 	print ' '

app = Flask(__name__)

@app.route('/threads')
def threads():
	if not 'id' in request.args:
		return 'nope'
	ids = request.args['id']
	print ids
	return '|'.join(ids.split(','))


if __name__ == '__main__':
	app.run(debug=True)