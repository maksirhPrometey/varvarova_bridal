from decouple import config

from .base import *  # noqa: F403

DEBUG = True

SECRET_KEY = config('SECRET_KEY', default='dev-only-insecure-key-do-not-use-in-prod')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

# Manifest storage — лише після collectstatic у prod-like середовищі

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
