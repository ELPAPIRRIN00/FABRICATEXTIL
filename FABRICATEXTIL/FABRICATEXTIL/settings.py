# *- coding: utf-8 -*-
import os

# Construye las rutas dentro del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SEGURIDAD: Clave secreta
# Usa una clave por defecto si no encuentra la variable de entorno
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-clave-secreta-desarrollo-12345')

# SEGURIDAD: DEBUG activado para ver errores
DEBUG = True

# --- CONFIGURACIÓN DE RED ---
# El '*' permite que entre tu celular y cualquier dispositivo de tu red local.
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.ngrok-free.app']

# Definición de Aplicaciones
INSTALLED_APPS = [
    'app',  # Tu aplicación
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'FABRICATEXTIL.urls'

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

WSGI_APPLICATION = 'FABRICATEXTIL.wsgi.application'

# Configuración de Base de Datos (Solo SQLite Local)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Validadores de contraseña
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

# Internacionalización
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Archivos Estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirección al iniciar sesión
LOGIN_REDIRECT_URL = '/inventario/productos/'   

# Ajuste de codificación