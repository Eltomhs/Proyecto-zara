from pathlib import Path
import os

# === BASE DEL PROYECTO ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === CONFIGURACIÓN GENERAL ===
SECRET_KEY = 'django-insecure-)p&qj(254$+3vp0y3#bbw-1_o*cm7-m4_-v+2&iu1ngj+-flyv'
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.1.86']

CSRF_TRUSTED_ORIGINS = [
    'http://192.168.1.86:8080',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://0.0.0.0:8080',
]

# === PANEL STAFF ===
# Slug para el panel administrativo protegido
PANEL_SLUG = os.getenv("PANEL_SLUG", "panel-privado")

# === LOGIN / LOGOUT ===
# Uso de los "names" de las rutas definidas en zara/urls.py
LOGIN_URL = 'zara:login_cliente'           # URL de acceso al formulario de login
LOGIN_REDIRECT_URL = 'zara:administrativo' # Redirección tras autenticación exitosa
LOGOUT_REDIRECT_URL = 'zara:login_cliente' # Destino tras cerrar sesión

# === APLICACIONES INSTALADAS ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # Filtros adicionales (por ejemplo, intcomma)
    'zara',                     # Aplicación principal del proyecto
]

# === MIDDLEWARE ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === CONFIGURACIÓN DE URLS Y WSGI ===
ROOT_URLCONF = 'mi_sitio.urls'
WSGI_APPLICATION = 'mi_sitio.wsgi.application'

# === TEMPLATES ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Carpeta global de plantillas HTML
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# === BASE DE DATOS ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# === VALIDADORES DE CONTRASEÑA ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === LOCALIZACIÓN ===
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# === ARCHIVOS ESTÁTICOS Y MULTIMEDIA ===
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']   # Directorios locales de recursos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'     # Carpeta de recolección para despliegue

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# === CONFIGURACIÓN DE CAMPOS AUTO ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
