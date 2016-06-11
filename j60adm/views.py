from django.views.generic import FormView, ListView
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
        qs = qs.prefetch_related('title_set')
        qs = qs.annotate(registration_count=Count('registration'))
        qs = qs.annotate(response_count=Count('surveyresponse'))
        return qs


class RegistrationImport(FormView):
    form_class = RegistrationImportForm
    template_name = 'registration_import.html'

    def form_valid(self, form):
        for reg in form.cleaned_data['registrations']:
            reg.save()
        return redirect('registration_list')


class RegistrationList(ListView):
    model = Registration
    queryset = Registration.objects.all()
    template_name = 'registration_list.html'


class SurveyResponseImport(FormView):
    form_class = SurveyResponseImportForm
    template_name = 'survey_response_import.html'

    def form_valid(self, form):
        for reg in form.cleaned_data['responses']:
            reg.save()
        return redirect('survey_response_list')


class SurveyResponseList(ListView):
    model = SurveyResponse
    queryset = SurveyResponse.objects.all()
    template_name = 'survey_response_list.html'
