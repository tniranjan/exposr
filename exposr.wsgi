#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/exposr.nrnjn.in/")

from exposr import app as application
application.secret_key = 'sleeponthefloor'
