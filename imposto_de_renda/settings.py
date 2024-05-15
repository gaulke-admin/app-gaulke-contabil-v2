
import json, os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

with open("config.json", "r") as f:
    configs = json.loads(f.read())

DEBUG = configs["SETTINGS"]["DEBUG"]
SECRET_KEY = configs["SETTINGS"]["SECRET_KEY"]
ALLOWED_HOSTS = configs["SETTINGS"]["ALLOWED_HOSTS"]
CSRF_TRUSTED_ORIGINS = configs["SETTINGS"]["CSRF_TRUSTED_ORIGINS"]
SECURE_CROSS_ORIGIN_OPENER_POLICY = configs["SETTINGS"]["SECURE_CROSS_ORIGIN_OPENER_POLICY"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'app_gaulke_contabil_v2',
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

ROOT_URLCONF = 'imposto_de_renda.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'imposto_de_renda.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


DATABASES = configs["database"]


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True



STATIC_URL = '/static_versao_2/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "base_statics/css"),
    os.path.join(BASE_DIR, "base_statics/img"),
    os.path.join(BASE_DIR, "base_statics/js"),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

app_gaulke_contabil_v2_USER_MODEL = "app_gaulke_contabil_v2.CustomUser"
AUTH_USER_MODEL = "app_gaulke_contabil_v2.CustomUser"


# AUTH_USER_MODEL = 'users.CustomUser'
# AUTHENTICATION_BACKENDS = ['app_gaulke_contabil_v2.backends.EmailBackend']
# AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
# AUTHENTICATION_BACKENDS = ('app_gaulke_contabil_v2.backends.EmailBackend',)

# AUTH_USER_MODEL = "app_gaulke_contabil_v2.User"
# AUTHENTICATION_BACKENDS = ["app_gaulke_contabil_v2.backends.CustomUserModelBackend"]

LOGIN_URL = "/login/"
