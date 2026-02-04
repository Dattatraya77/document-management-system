
# LOCAL Postgres Database settings

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        "NAME": 'DMS_DB',
        'USER': 'postgres',
        'PASSWORD': 'root',
    }
}




