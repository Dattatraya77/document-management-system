# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
import dj_database_url
from decouple import config

# DATABASES = {
#     'default': {
#         'ENGINE': 'django_tenants.postgresql_backend',
#         "NAME": 'DMS_DB',
#         'USER': 'postgres',
#         'PASSWORD': 'root',
#     }
# }


DATABASES = {
    "default": dj_database_url.parse(
        config("DATABASE_URL"),
        engine="django_tenants.postgresql_backend"
    )
}

