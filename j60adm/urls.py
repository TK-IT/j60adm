"""j60adm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from j60adm.views import (
    PersonImport, PersonList,
    RegistrationImport, RegistrationList,
    SurveyResponseImport, SurveyResponseList,
)


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^person/import/$', PersonImport.as_view(),
        name='person_import'),
    url(r'^person/$', PersonList.as_view(),
        name='person_list'),
    url(r'^survey/import/$', SurveyResponseImport.as_view(),
        name='survey_response_import'),
    url(r'^survey/$', SurveyResponseList.as_view(),
        name='survey_response_list'),
    url(r'^registration/import/$', RegistrationImport.as_view(),
        name='registration_import'),
    url(r'^registration/$', RegistrationList.as_view(),
        name='registration_list'),
]
