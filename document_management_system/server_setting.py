# Render server Postgres Database settings

import dj_database_url
from decouple import config

DATABASES = {
    "default": dj_database_url.parse(
        config("DATABASE_URL"),
        engine="django_tenants.postgresql_backend"
    )
}

