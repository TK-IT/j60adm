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
        qs = qs.prefetch_related('registration_set', 'surveyresponse_set',
                                 'title_set', 'emailaddress_set')
        qs = sorted(qs, key=lambda p: p.title_order_key())
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


class Email(TemplateView):
    template_name = 'email.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        qs = Person.objects.all()
        qs = qs.prefetch_related('emailaddress',
                                 'emailaddress__emailmessage')
        by_state = dict(none=[], new=[], sent=[], bounce=[])
        for p in Person.objects.all():
            addresses = list(p.emailaddress_set.all())
            if not addresses:
                by_state['none'].append(p)
                continue
            message_sets = [list(a.emailmessage_set.all()) for a in addresses]
            any_new = any(not message_set for message_set in message_sets)
            any_sent = any(not message.bounce
                           for message_set in message_sets
                           for message in message_set)
            if any_new:
                by_state['new'].append(p)
            elif any_sent:
                by_state['sent'].append(p)
            else:
                by_state['bounce'].append(p)
        context_data['person_list'] = (by_state['new'] + by_state['bounce'] +
                                       by_state['none'] + by_state['sent'])
        return context_data
