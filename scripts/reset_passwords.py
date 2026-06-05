import os, csv, secrets, sys
# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.getcwd()))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from accounts.models import User
rows=[('username','email','role','new_password')]
for u in User.objects.all():
    pwd = secrets.token_urlsafe(10)
    u.set_password(pwd)
    u.save()
    rows.append((u.username, u.email or '', u.role or '', pwd))
path = os.path.join(os.getcwd(),'accounts_export.csv')
with open(path,'w',newline='',encoding='utf-8') as f:
    csv.writer(f).writerows(rows)
print('Wrote', path)
