from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.urls import path
from create_document import views


urlpatterns = [
    url(r'^$', views.SearchDashboard.as_view(), name='search_dashboard'),
    url(r'^get-timezone/$', views.GetTimeZone.as_view(), name='search'),
    url(r'^train-docx-template/$', views.Index.as_view(), name='train-docx-template'),
    url(r'^add-temp-details/$', views.AddTemplateDetails.as_view(), name='AddTemplateDetails'),
    url(r'^training-metadata/(?P<template_id>.*)$', views.TrainingMetaData.as_view(), name='trainingMetaData'),
    url(r'^download-view-document/$', views.TrainingMetaData.as_view(), name='download-view-document'),
    url(r'^delete-template/(?P<template_id>.*)/$', views.DeleteTemplate.as_view(), name='delete-template'),
    url(r'^templates-to-doc/$', views.TemplatesToDoc.as_view(), name='templates-to-doc'),
    url(r'^create-document-template/(?P<template_id>.*)/$', views.CreateNewDocumentTemplate.as_view(), name='createDocumentTemplate'),
]


