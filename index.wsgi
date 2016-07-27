import os, sys
import sae
from manage import app, db
from sae.ext.shell import ShellMiddleware

import os, sys
app_root = os.path.dirname(os.path.abspath(__file__))
sp = os.path.join(app_root, 'venv', 'lib', 'python2.7', 'site-packages')
sys.path.insert(0, sp)
sae.add_vendor_dir(sp)

db.create_all()

def app(environ, start_response):
    status = ‘200 OK’
    response_headers = [(‘Content-type’, ‘text/plain’)]
    start_response(status, response_headers)
    return [“Hello, world!”]

application = sae.create_wsgi_app(ShellMiddleware(app))
