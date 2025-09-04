from .devlopement import *
import os
from dotenv import load_dotenv
load_dotenv()

DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY_PROD')

ALLOWED_HOSTS = [ ]
# SITE_ID = 7


# CSRF_TRUSTED_ORIGINS = ['https://*.127.0.0.1']


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    #  Set this up if running in production enviournment.
    
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': os.getenv('DB_NAME'),
    #     'USER' : os.getenv('DB_USERNAME'),
    #     'PASSWORD' : os.getenv('DB_PASSWORD'),
    #     'HOST': os.getenv('DB_HOST'),
    #     'OPTIONS':{
    #          'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
    #         }
    # }
}


# HTTPS Security - Django (PCI DSS Compliance)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# HSTS Security - Django (Extended for PCI compliance)
SECURE_HSTS_SECONDS = 31536000  # 1 year - PCI DSS requirement
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Additional security headers for PCI compliance
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking on payment pages

# Cookie security (PCI DSS)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Session security
SESSION_COOKIE_AGE = 3600  # 1 hour for payment sessions
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


