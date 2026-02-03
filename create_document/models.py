from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from django.db import connection
from urllib.parse import unquote
import os


# ======================================================
# Tenant-aware upload paths
# ======================================================

def get_tenant_specific_template(instance, filename):
    return f"{connection.tenant.name}/templates/{filename}"


def get_tenant_specific_new_document(instance, filename):
    return f"{connection.tenant.name}/created_documents/{filename}"


# ======================================================
# Template constants
# ======================================================

TEMPLATE_STATUS = (
    ('ac', 'Active'),
    ('ia', 'Inactive'),
    ('de', 'Deleted'),
    ('pe', 'Pending')
)

TEMPLATE_FLAG = (
    ('docx', 'docx'),
    ('xlsx', 'xlsx'),
    ('dlf-xlsx', 'dlf-xlsx'),
    ('dlf-docx', 'dlf-docx')
)


# ======================================================
# Template Model
# ======================================================

class Template(models.Model):
    temp_id = models.CharField(max_length=64, primary_key=True)
    template_flag = models.CharField(
        max_length=10,
        choices=TEMPLATE_FLAG,
        default='docx'
    )
    temp_status = models.CharField(
        max_length=2,
        choices=TEMPLATE_STATUS,
        default='pe'
    )
    temp_title = models.CharField(max_length=100)
    temp_description = models.CharField(max_length=400, blank=True)
    template = models.FileField(upload_to=get_tenant_specific_template, max_length=200)

    temp_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_templates"
    )
    temp_created_at = models.DateTimeField(auto_now_add=True)

    temp_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edited_templates"
    )
    temp_edited_on = models.DateTimeField(auto_now=True)

    temp_deleted_on = models.DateTimeField(null=True, blank=True)

    doc_group = models.ManyToManyField(Group, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["temp_status"]),
            models.Index(fields=["template_flag"]),
        ]

    def __str__(self):
        return self.temp_title[:50]

    def get_time_zone(self):
        return connection.tenant.client_tz

    def get_temp_name(self):
        return unquote(os.path.basename(self.template.name))

    def display_group(self):
        return ", ".join(group.name for group in self.doc_group.all())

    display_group.short_description = "Groups"


# ======================================================
# Created Document
# ======================================================

FILE_STATUS = (
    ('ac', 'Active'),
    ('ia', 'Inactive'),
    ('de', 'Deleted')
)

DOC_TYPE = (
    ('docx', 'docx'),
    ('pdf', 'pdf'),
    ('xlsx', 'xlsx'),
    ('dlf-xlsx', 'dlf-xlsx'),
    ('dlf-docx', 'dlf-docx')
)


class CreatedDocument(models.Model):
    doc_id = models.CharField(
        max_length=64,
        primary_key=True,
        verbose_name="Created Document ID"
    )

    document = models.FileField(
        upload_to=get_tenant_specific_new_document,
        max_length=200,
        null=True,
        blank=True
    )

    document_name = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    doc_matched_template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    doc_created_at = models.DateTimeField(auto_now_add=True)

    doc_created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_documents"
    )

    status = models.CharField(
        max_length=2,
        choices=FILE_STATUS,
        default='ac'
    )

    doc_group = models.ManyToManyField(Group, blank=True)

    doc_type = models.CharField(
        max_length=20,
        choices=DOC_TYPE,
        default='pdf'
    )

    doc_updated_on = models.DateTimeField(auto_now=True)
    doc_deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["doc_type"]),
            models.Index(fields=["doc_created_at"]),
        ]

    def __str__(self):
        return self.doc_id

    def get_document_name(self):
        if not self.document:
            return ""
        return unquote(os.path.basename(self.document.name))

    def get_file_ext(self):
        if not self.document:
            return ""
        return os.path.splitext(self.document.name)[1].replace(".", "")

    def display_group(self):
        return ", ".join(group.name for group in self.doc_group.all())

    display_group.short_description = "Groups"


# ======================================================
# Metadata Choices
# ======================================================

class MetadataChoice(models.Model):
    meta_choice = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.meta_choice


# ======================================================
# Metadata Keys
# ======================================================

METADATA_TYPE = (
    ('string', 'String'),
    ('number', 'Number'),
    ('date', 'Date'),
    ('boolean', 'Boolean'),
    ('choice', 'Choice'),
    ('textarea', 'TextArea'),
    ('image', 'Image'),
    ('signature', 'Signature')
)


class MetadataKey(models.Model):
    key_id = models.AutoField(primary_key=True)
    metadata_key = models.CharField(max_length=100)
    metadata_description = models.CharField(max_length=200, blank=True)
    metadata_type = models.CharField(max_length=10, choices=METADATA_TYPE)
    external_metadata = models.BooleanField(default=False)
    metadata_choice = models.ManyToManyField(
        MetadataChoice,
        blank=True
    )

    def __str__(self):
        return self.metadata_key


# ======================================================
# Template ↔ Metadata Mapping
# ======================================================

class TemplateMetaData(models.Model):
    temp_meta_id = models.AutoField(primary_key=True)

    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE
    )

    metadata_key = models.ForeignKey(
        MetadataKey,
        on_delete=models.CASCADE
    )

    temp_description = models.CharField(max_length=300)

    class Meta:
        unique_together = ("template", "metadata_key")

    def __str__(self):
        return self.temp_description


# ======================================================
# Metadata Values (Per Document)
# ======================================================

class MetadataValue(models.Model):
    meta_value_id = models.AutoField(primary_key=True)

    # Typed storage (recommended)
    metadata_value_text = models.TextField(null=True, blank=True)
    metadata_value_number = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True
    )
    metadata_value_date = models.DateField(null=True, blank=True)
    metadata_value_bool = models.BooleanField(null=True)
    metadata_value_image = models.ImageField(
        upload_to="metadata_images/",
        null=True,
        blank=True
    )

    meta_key = models.ForeignKey(
        MetadataKey,
        on_delete=models.CASCADE
    )

    meta_created_doc = models.ForeignKey(
        CreatedDocument,
        on_delete=models.CASCADE
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("meta_key", "meta_created_doc")
        indexes = [
            models.Index(fields=["meta_key"]),
            models.Index(fields=["meta_created_doc"]),
        ]

    def __str__(self):
        return self.metadata_value_text or ""

    def display_document(self):
        return self.meta_created_doc.get_document_name()

    def metadata_type(self):
        return self.meta_key.metadata_type

    display_document.short_description = "Document Name"
    metadata_type.short_description = "Metadata Type"
