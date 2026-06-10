
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.getenv('SECRET_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')


SECRET_KEY = 'django-insecure-pia_1hv^#715)2kq9==b!91o2#g@cfe$eiu&7le8)vsnbb_p&s'
DEBUG = True
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #     app
    'mainApp',

    'import_export',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_cleanup.apps.CleanupConfig',
    'ckeditor',

]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mainApp.middleware.ThreadLocalMiddleware',

]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'mainApp.context_processors.unread_messages',
                'mainApp.context_processors.online_appointments_count',
                'mainApp.context_processors.doctor_appointments_count',# <--- Oxiri bir xil bo'lishi shart
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2 hafta davomida eslab qoladi
SESSION_SAVE_EVERY_REQUEST = True


JAZZMIN_SETTINGS = {
    # Panel sarlavhasi (Rasm o'rniga matn chiqishi uchun)
    "site_title": "Bobur Doktor Shifo",
    "site_header": "Bobur Doktor Shifo",  # 2-rasmdagi kabi matn ko'rinishida chiqadi
    "site_brand": "Doktor Shifo Admin",

    # Logotiplarni umuman rasm qilmaymiz (None qilindi)
    "site_logo": None,
    "login_logo": None,
    "welcome_sign": "Bobur Doktor Shifo boshqaruv tizimiga xush kelibsiz",
    "copyright": "Bobur Doktor Shifo Ltd",

    # Foydalanuvchi qidiruvi (Bular o'chib ketmasligi kerak!)
    "search_model": ["mainApp.Patient", "mainApp.Staff"],

    # Menyular iyerarxiyasi
    "topmenu_links": [
        {"name": "Bosh sahifa", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "mainApp.Staff"},
        {"name": "Analitika", "url": "/admin/dashboard/"},
    ],

    # Modellar uchun ikonkalaringiz (Bular saqlanib qolishi shart)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "mainApp.Department": "fas fa-hospital",
        "mainApp.Service": "fas fa-concierge-bell",
        "mainApp.Staff": "fas fa-user-md",
        "mainApp.DoctorProfile": "fas fa-id-card-alt",
        "mainApp.Patient": "fas fa-wheelchair",
        "mainApp.OnlineAppointment": "fas fa-globe",
        "mainApp.Appointment": "fas fa-calendar-check",
        "mainApp.MedicalRecord": "fas fa-file-medical",
        "mainApp.LabTest": "fas fa-vials",
        "mainApp.LabReferral": "fas fa-microscope",
        "mainApp.Payment": "fas fa-money-bill-wave",
        "mainApp.News": "fas fa-newspaper",
    },

    "order_with_respect_to": ["mainApp", "auth"],
    "show_ui_builder": False,
}

# Bunga tegmaysiz, qanday bo'lsa shunday tursin
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",
    "theme_mode": "default",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

SESSION_SAVE_EVERY_REQUEST = True

# Agar brauzer oynasi (vkladka emas, butun brauzer) yopilsa, sessiya tugaydi.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Cookie fayllarining amal qilish muddati (ixtiyoriy, lekin xavfsizlik uchun yaxshi).
# Bu serverdagi sessiya muddatini belgilaydi.
SESSION_COOKIE_AGE = 3600
# LOGIN_URL = 'login'  # Login qilmaganlarni shu nomli urlga haydaydi
# LOGOUT_REDIRECT_URL = 'login'
#
# LOGIN_URL = 'doctor_dashboard_login'  # Sizning urls.py dagi name='doctor_dashboard_login' qismingiz
# LOGIN_REDIRECT_URL = 'doctor_dashboard'

# Asosiy (Reseption va boshqalar uchun) login manzili
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'reception_dash' # Standart kirish joyi


