import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'gitpatron.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
sys.path.append('/home/ec2-user/sites/gitpatron')