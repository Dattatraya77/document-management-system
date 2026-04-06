# Render server Postgres Database settings

import dj_database_url
from decouple import config

# DATABASES = {
#     "default": dj_database_url.parse(
#         config("DATABASE_URL"),
#         engine="django_tenants.postgresql_backend"
#     )
# }

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        "NAME": 'DMS_DB',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': "localhost",
        'PORT': "5432",
    }
}

