#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/GridApp/")
from GridApp import APP as application
application.secret_key = 'Add your secret key'
