from google.appengine.ext import vendor

vendor.add('lib')

#############################################################################
# To handle the error "No module named msvcrt" when run googleAppEngine locally on Windows
# https://github.com/GoogleCloudPlatform/python-docs-samples/issues/1176

import os
import sys
on_appengine = os.environ.get('SERVER_SOFTWARE','').startswith('Development')

if on_appengine and os.name == 'nt':
	sys.platform = "Not Windows"

