#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.append("/var/www/SoftDevProj0/app")

from app import app as application
