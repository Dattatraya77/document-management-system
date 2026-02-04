from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import remove_www_and_dev, get_public_schema_name, get_tenant_domain_model


class TenantTutorialMiddleware(MiddlewareMixin):

    def process_request(self, request):
        connection.set_schema_to_public()

        hostname = remove_www_and_dev(request.get_host().split(':')[0])

        try:
            domain = get_tenant_domain_model().objects.get(domain=hostname)
            request.tenant = domain.tenant
        except get_tenant_domain_model().DoesNotExist:
            if hostname in (
                "127.0.0.1",
                "localhost",
                "reliance.local",
                "document-management-system-kib5.onrender.com",
            ):
                request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
                return
            raise Http404

        connection.set_tenant(request.tenant)
        ContentType.objects.clear_cache()

        if request.tenant.schema_name == get_public_schema_name():
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF
