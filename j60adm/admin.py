from django.contrib import admin
from j60adm.models import (
    Person, Title, EmailAddress, EmailMessage, Registration, SurveyResponse)


class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'street', 'city', 'country', 'dead',
                    'created_time']
    search_fields = ['name', 'street', 'city', 'country']


class TitleFilter(admin.SimpleListFilter):
    title = 'title'
    parameter_name = 'title'

    def lookups(self, request, model_admin):
        return [(v, v) for v in ('CERM FORM INKA KASS NF PR ' +
                                 'SEKR VC FU EFU FUAN').split()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(title__startswith=self.value())


class TitleAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'person', 'title', 'period']
    list_filter = [TitleFilter, 'period']
    search_fields = ['title']


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ['address', 'person', 'source']
    search_fields = ['address']
    list_filter = ['source']


def get_message_person(message):
    return message.recipient.person


get_message_person.short_description = 'person'
get_message_person.admin_order_field = 'person'


class EmailMessageAdmin(admin.ModelAdmin):
    list_filter = ['bounce']
    search_fields = ['recipient__person__name', 'recipient__address']
    list_display = ['recipient', get_message_person, 'bounce', 'created_time']
    list_select_related = ['recipient', 'recipient__person']


class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['name', 'time', 'title', 'email', 'newsletter', 'note']
    list_filter = ['newsletter', 'note']
    search_fields = ['name', 'person__name']


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['survey_id', 'time', 'first_name', 'last_name',
                    'email', 'dietary', 'newsletter',
                    'transportation', 'show', 'webshop_show',
                    'note']
    list_filter = ['newsletter', 'transportation',
                   'show', 'webshop_show', 'dietary', 'note']
    search_fields = ['first_name', 'last_name', 'person__name']


admin.site.register(Person, PersonAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(EmailAddress, EmailAddressAdmin)
admin.site.register(EmailMessage, EmailMessageAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(SurveyResponse, SurveyResponseAdmin)
