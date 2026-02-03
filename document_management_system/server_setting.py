# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        "NAME": 'DMS_DB',
        'USER': 'dattatraya77',
        'PASSWORD': 'hello2020',
    }
}

