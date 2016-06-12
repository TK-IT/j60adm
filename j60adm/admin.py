from django.contrib import admin
from j60adm.models import (
    Person, Title, EmailAddress, EmailMessage, Registration, SurveyResponse)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'street', 'city', 'country', 'dead',
                    'created_time')
    search_fields = ['name', 'street', 'city', 'country']


class TitleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'person', 'title', 'period')


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'person', 'source')


def get_message_person(message):
    return message.recipient.person


class EmailMessageAdmin(admin.ModelAdmin):
    list_filter = ['bounce']
    search_fields = ['recipient__person__name', 'recipient__address']
    list_display = ('recipient', get_message_person, 'bounce', 'created_time')
    list_select_related = ('recipient', 'recipient__person')


class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('name', 'time', 'title', 'email', 'newsletter', 'note')


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('survey_id', 'time', 'first_name', 'last_name',
                    'email', 'dietary', 'newsletter',
                    'transportation', 'show', 'webshop_show',
                    'note')


admin.site.register(Person, PersonAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(EmailAddress, EmailAddressAdmin)
admin.site.register(EmailMessage, EmailMessageAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(SurveyResponse, SurveyResponseAdmin)
