from .models import *
from django.contrib import admin



# Register your models here.

admin.site.register(MetadataChoice)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('temp_id', 'temp_owner', 'temp_title', 'temp_description',
                    'temp_created_at', 'temp_edited_on', 'template', 'temp_status', 'display_group')


@admin.register(MetadataKey)
class MetadataKeyAdmin(admin.ModelAdmin):
    list_display = ('metadata_key', 'metadata_type', 'external_metadata')


@admin.register(CreatedDocument)
class CreatedDocumentAdmin(admin.ModelAdmin):
    list_display = ('doc_id', 'document', 'document_name', 'doc_type',
                    'doc_matched_template',
                    'doc_created_at', 'doc_created_by', 'status', 'display_group', 'doc_updated_on')
    list_per_page = 5


@admin.register(TemplateMetaData)
class TemplateMetaDataAdmin(admin.ModelAdmin):

    list_display = ('template',  'metadata_key')


@admin.register(MetadataValue)
class MetadataValueAdmin(admin.ModelAdmin):
    list_display = ('meta_value_id', 'meta_key', 'metadata_value_text', 'metadata_value_number', 'metadata_type', 'metadata_value_date',
                    'metadata_value_image', 'metadata_value_bool')



