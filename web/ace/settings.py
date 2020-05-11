"""
Django settings for ace project.

Generated by 'django-admin startproject' using Django 3.0.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r#y4_mwy(0xuhb8xo2_))0dg8qhb@dnz1(!*@ac3tgrbl@^8q@'
GOOGLE_RECAPTCHA_SECRET_KEY = '6LcU4dQUAAAAAPuB2fRHexfmyTP8Gg52B87crNPD'
# TODO - Add Google maps API Key
GOOGLE_MAPS_API_KEY = None 

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = os.getenv('DEBUG', 'NO').lower() in ('on', 'true', 'y', 'yes')
DEBUG = False

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup', # Auto delete storage files upon model deletion
    'tinymce',
    'django_sendfile', # Secure file storage and retrieval
    'notifications', 
    # User apps
    'joblistings',
    'companies',
    'jobapplications',
    'accounts',
    'jobmatchings',
    'announcements',
    'ace',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'ace.urls'

AUTH_USER_MODEL = 'accounts.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ace.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }



DATABASES = {
'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'postgres',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'HOST': 'db',
    'PORT': 5432,
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'EST'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
     os.path.join(BASE_DIR, 'static_server'),
)
# print(STATICFILES_DIRS)
#STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_ROOT = os.path.join(BASE_DIR,"static")

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# SENDFILE settings
#SENDFILE_BACKEND = 'sendfile.backends.development'
#SENDFILE_BACKEND = 'sendfile.backends.xsendfile'
SENDFILE_BACKEND = 'sendfile.backends.nginx'
#SENDFILE_ROOT = os.path.join(BASE_DIR, 'protected')

SENDFILE_ROOT = '/media/'
SENDFILE_URL = '/media'

# Email notification settings
# SECURITY WARNING: Not prod ready. Do not used in prod
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'concordia.ace.coop@gmail.com'
EMAIL_HOST_PASSWORD = 'aceconcordiadev'
EMAIL_PORT = 587

# SECURITY WARNING: Uncomment below in production once certificate at hand to force HTTPS 
#SECURE_SSL_REDIRECT = True

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/ace.log',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}