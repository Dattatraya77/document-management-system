from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
import pytz

# ======================================================
# Timezone Choices (Dynamic & Standard)
# ======================================================

TZ_CHOICES = [(tz, tz) for tz in pytz.all_timezones]


# ======================================================
# Client / Tenant Model
# ======================================================

class Client(TenantMixin):
    """
    Represents a tenant (customer).
    Each client gets its own schema.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Schema name / tenant identifier"
    )

    page_title = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    client_tz = models.CharField(
        max_length=100,
        choices=TZ_CHOICES,
        default='Asia/Kolkata'
    )

    first_visit = models.BooleanField(default=True)

    send_email = models.EmailField(
        null=True,
        blank=True,
        help_text="Primary notification email"
    )

    logo = models.ImageField(
        upload_to="client_logos/",
        null=True,
        blank=True
    )

    client_company_name = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Soft disable tenant access"
    )

    # django-tenants requirement
    auto_create_schema = True

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


# ======================================================
# Domain Model
# ======================================================

class Domain(DomainMixin):
    """
    Maps domains/subdomains to tenants
    """
    class Meta:
        indexes = [
            models.Index(fields=["domain"]),
            models.Index(fields=["tenant"]),
        ]

    def __str__(self):
        return self.domain
