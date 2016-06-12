"""
WSGI config for j60adm project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys
import site

prev_sys_path = list(sys.path)
site.addsitedir(
    '/home/rav/j60adm/venv/lib/python3.4/site-packages')
sys.path.append('/home/rav/j60adm')
# reorder sys.path so new directories from the addsitedir show up first
new_sys_path = [p for p in sys.path if p not in prev_sys_path]
for item in new_sys_path:
    sys.path.remove(item)
sys.path[:0] = new_sys_path

from django.core.wsgi import get_wsgi_application  # NOQA

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "j60adm.settings")

application = get_wsgi_application()
