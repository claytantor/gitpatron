import os

from ConfigParser import RawConfigParser

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(__file__)

here = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

# you will need to copy the example and make custom
# settings for the environment
config = RawConfigParser()
config.read('{0}/conf/settings.ini'.format(BASE_DIR))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('secrets','DJANGO_SECRET_KEY')
GITPATRON_PW_SECRET_KEY = config.get('secrets','GITPATRON_PW_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = config.get('debug','DEBUG')

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
        'NAME': config.get('database','DATABASE_NAME'),                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': config.get('database','DATABASE_USER'),
        'PASSWORD': config.get('database','DATABASE_PASSWORD'),
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

# GIT
GIT_APP_CLIENT_ID=config.get('git','GIT_APP_CLIENT_ID')
GIT_APP_CLIENT_SECRET=config.get('git','GIT_APP_CLIENT_SECRET')
GIT_APP_REDIRECT=config.get('git','GIT_APP_REDIRECT')
GIT_OAUTH_SCOPES='user:email,user,repo,notifications,read:repo_hook'

#COINBASE
COINBASE_SECRET=config.get('coinbase','COINBASE_SECRET')
COINBASE_API_KEY=config.get('coinbase','COINBASE_API_KEY')
COINBASE_API_SECRET=config.get('coinbase','COINBASE_API_SECRET')
COINBASE_OAUTH_CLIENT_APP=config.get('coinbase','COINBASE_OAUTH_CLIENT_APP')
COINBASE_OAUTH_CLIENT_ID=config.get('coinbase','COINBASE_OAUTH_CLIENT_ID')
COINBASE_OAUTH_CLIENT_SECRET=config.get('coinbase','COINBASE_OAUTH_CLIENT_SECRET')
COINBASE_OAUTH_CLIENT_CALLBACK=config.get('coinbase','COINBASE_OAUTH_CLIENT_CALLBACK')

#gitpatron
#http://local.gitpatron.com:8000
GITPATRON_APP_URL = config.get('gitpatron','GITPATRON_APP_URL')
