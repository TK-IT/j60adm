from django.views.generic import FormView, ListView, TemplateView
from django.shortcuts import redirect
from django.db.models import Count

from j60adm.models import Registration, SurveyResponse, Person
from j60adm.forms import (
    RegistrationImportForm, SurveyResponseImportForm, PersonImportForm)


class PersonImport(FormView):
    form_class = PersonImportForm
    template_name = 'person_import.html'

    def form_valid(self, form):
        persons, objects = form.cleaned_data['persons']
        for p in persons:
            p.save()
        for o in objects:
            o.person = o.person  # Update o.person_id
            o.save()
        return redirect('person_list')


class PersonList(ListView):
    template_name = 'person_list.html'

    def get_queryset(self):
        qs = Person.objects.all()
        qs = qs.prefetch_related(
            'title_set', 'registration_set', 'surveyresponse_set',
            'emailaddress_set', 'emailmessage_set')
        return qs


class RegistrationImport(FormView):
    form_class = RegistrationImportForm
    template_name = 'registration_import.html'

    def form_valid(self, form):
        for reg in form.cleaned_data['registrations']:
            reg.save()
        return redirect('registration_list')


class RegistrationList(TemplateView):
    template_name = 'registration_list.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        qs = Registration.objects.all()
        qs = qs.order_by('person')
        context_data['object_list'] = qs
        qs = Person.objects.all()
        qs = qs.prefetch_related('title_set')
        context_data['person_list'] = qs
        return context_data

    def post(self, request):
        for r in Registration.objects.all():
            k = 'object_%s' % r.id
            if k in request.POST:
                v = request.POST[k]
                if v:
                    r.person_id = int(v)
                    r.save()
        return self.get(request)


class SurveyResponseImport(FormView):
    form_class = SurveyResponseImportForm
    template_name = 'survey_response_import.html'

    def form_valid(self, form):
        for reg in form.cleaned_data['responses']:
            reg.save()
        return redirect('survey_response_list')


class SurveyResponseList(TemplateView):
    template_name = 'survey_response_list.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        qs = SurveyResponse.objects.all()
        qs = qs.order_by('person')
        context_data['object_list'] = qs
        qs = Person.objects.all()
        qs = qs.prefetch_related('title_set')
        context_data['person_list'] = qs
        return context_data

    def post(self, request):
        for r in SurveyResponse.objects.all():
            k = 'object_%s' % r.id
            if k in request.POST:
                v = request.POST[k]
                if v:
                    r.person_id = int(v)
                    r.save()
        return self.get(request)


#class Email(TemplateView):
#    template_name = 'email.html'
#
#    def get_context_data(self, **kwargs):
#        context_data = super().get_context_data(**kwargs)
#        qs = EmailAddress.objects.all()
#        qs = qs.select_related('person')
#        addresses = {
#            e.address: dict(address=e, messages=[])
#            for e in qs}
#        for e in EmailMessage.objects.all():
#            addresses[e.recipient]['messages'].append(e)
#        context_data['address_list'] = addresses.values()
#        return context_data
