import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('/home/swdc/SWDCWebsite')
load_dotenv(os.path.join(project_folder, 'all_passwords.env'))


from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SWDCWebsite.settings')
application = get_wsgi_application()