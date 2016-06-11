from django.contrib import admin
from j60adm.models import Registration, SurveyResponse


class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('name', 'time', 'title', 'email', 'newsletter', 'note')


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name',
                    'email', 'dietary', 'newsletter',
                    'transportation', 'show', 'webshop_show',
                    'note')


admin.site.register(Registration, RegistrationAdmin)
admin.site.register(SurveyResponse, SurveyResponseAdmin)
