

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(__file__)

here = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qaq3&+tcg_32dlsk7hn9^7$-l#e1@$)=-+3j_b90aa*(*h0#)l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'app',
    'markdown_deux',
)

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.request",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.tz",
                               "django.contrib.messages.context_processors.messages")

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'gitpatron.urls'

WSGI_APPLICATION = 'gitpatron.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'gitpatron',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'gitpatron',
        'PASSWORD': 'gitpatron',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''


# Additional locations of static files
# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, '..', 'static/'),
    )

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)




# app specific settings

FIXTURE_DIRS = (
   os.path.join(PROJECT_DIR, '.', 'fixtures/'),
)

# https://github.com/login/oauth/authorize?
#   client_id=...&
#   redirect_uri=http://www.example.com/oauth_redirect
#prod
GIT_APP_CLIENT_ID='f12cc86f9487e1d0ffde'
GIT_APP_CLIENT_SECRET='8cb875452af3a6bba056822fea24880c04c0b9eb'
GIT_APP_REDIRECT='http://local.gitpatron.com:8000/oauth_redirect'



LOGIN_URL = 'https://github.com/login/oauth/authorize?client_id={0}&redirect_uri={1}'.format(
            GIT_APP_CLIENT_ID, GIT_APP_REDIRECT)
GIT_OAUTH_SCOPES='user:email,user,repo,notifications,read:repo_hook'
COINBASE_SECRET='a8b693bf-668c-461d-9a91-78f4b083e288'

COINBASE_API_KEY='gDu7LYvG7GfxXPS4'
COINBASE_API_SECRET='1kkhWJEz9rr6MMFSJ9hyMhcFZjVYjhx4'

COINBASE_OAUTH_CLIENT_APP='gitpatron_dev'
COINBASE_OAUTH_CLIENT_ID='842f2bf8909aff0aebc677be937470d548a2ba6967a3a143b511c4511437b70a'
COINBASE_OAUTH_CLIENT_SECRET='db56a8cb4ffec09468559ba11bff69c5eea4476c8df75794b33fa5c45039c458'
COINBASE_OAUTH_CLIENT_CALLBACK='http://local.gitpatron.com:8000/coin_callback.html'