import os, sys
app_root = os.path.dirname(os.path.abspath(__file__)) 
p = os.path.join(app_root, 'venv', 'lib', 'python2.7', 'site-package')
print "app_root:%s, p:%s" % (app_root, p)

