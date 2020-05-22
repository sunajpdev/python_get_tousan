import os

daemon = True
reload = True
bind = '127.0.0.1:' + str(os.getenv('PORT', 8000))
proc_name = 'Flask-tousan'
workers = 1