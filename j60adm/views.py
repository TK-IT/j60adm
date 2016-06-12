import logging
from django.views.generic import FormView, ListView, TemplateView, View
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
import django.contrib.auth.decorators

from j60adm.models import (
    Registration, SurveyResponse, Person,
    EmailAddress, EmailMessage,
)
from j60adm.forms import (
    RegistrationImportForm, SurveyResponseImportForm, PersonImportForm,
    EmailAddressCreateForm, EmailMessageCreateForm, EmailMessageBulkCreateForm,
)
from j60adm.addresses import synchronize_addresses

logger = logging.getLogger('j60adm')

login_required = method_decorator(
    django.contrib.auth.decorators.login_required(login_url='/login/'),
    name='dispatch')


@login_required
class PersonImport(FormView):
    form_class = PersonImportForm
    template_name = 'person_import.html'

    def form_valid(self, form):
        persons, objects, messages = form.cleaned_data['persons']
        logger.info("PersonImport importing %s persons", len(persons),
                    extra=self.request.log_data)
        for p in persons:
            p.save()
        for o in objects:
            o.person = o.person  # Update o.person_id
            o.save()
        for m in messages:
            m.recipient = o.recipient  # Update o.recipient_id
            m.save()
        return redirect('person_list')


@login_required
class PersonList(ListView):
    template_name = 'person_list.html'

    def get_queryset(self):
        qs = Person.objects.all()
        qs = qs.prefetch_related('registration_set', 'surveyresponse_set',
                                 'title_set', 'emailaddress_set')
        qs = sorted(qs, key=lambda p: p.title_order_key())
        return qs


@login_required
class RegistrationImport(FormView):
    form_class = RegistrationImportForm
    template_name = 'registration_import.html'

    def form_valid(self, form):
        regs = form.cleaned_data['registrations']
        logger.info("RegistrationImport importing %s registrations", len(regs),
                    extra=self.request.log_data)
        for reg in regs:
            reg.save()
        return redirect('registration_list')


@login_required
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


@login_required
class SurveyResponseImport(FormView):
    form_class = SurveyResponseImportForm
    template_name = 'survey_response_import.html'

    def form_valid(self, form):
        resps = form.cleaned_data['responses']
        logger.info("SurveyResponseImport importing %s surveys", len(resps),
                    extra=self.request.log_data)
        for resp in resps:
            resp.save()
        return redirect('survey_response_list')


@login_required
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
                if v and int(v) != r.person_id:
                    logger.info("Set SurveyResponse(id=%s).person_id = %s",
                                r.id, v,
                                extra=self.request.log_data)
                    r.person_id = int(v)
                    r.save()
        return self.get(request)


@login_required
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
            any_sent = any(any(not message.bounce for message in message_set)
                           for message_set in message_sets)
            if any_sent:
                by_state['sent'].append(p)
            elif any_new:
                by_state['new'].append(p)
            else:
                by_state['bounce'].append(p)
        by_state['bounce'].sort(
            key=lambda p: next(
                a.address[a.address.index('@'):]
                for a in p.emailaddress_set.all()
                if any(m.bounce for m in a.emailmessage_set.all())))
        recipients = []
        for p in by_state['new']:
            emailaddress = next(
                a.address for a in p.emailaddress_set.all()
                if not list(a.emailmessage_set.all()))
            recipients.append('"%s" <%s>' % (p.name, emailaddress))
        context_data['recipients'] = ',\n'.join(recipients)
        context_data['n_new'] = len(by_state['new'])
        context_data['n_bounce'] = len(by_state['bounce'])
        context_data['n_none'] = len(by_state['none'])
        context_data['n_sent'] = len(by_state['sent'])
        context_data['person_list'] = (by_state['new'] + by_state['bounce'] +
                                       by_state['none'] + by_state['sent'])
        return context_data


@login_required
class EmailMessageCreate(FormView):
    form_class = EmailMessageCreateForm
    template_name = 'emailmessage_create.html'

    def get_emailaddress(self):
        return get_object_or_404(EmailAddress, pk=self.kwargs['address'])

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['emailaddress'] = self.get_emailaddress()
        return context_data

    def form_valid(self, form):
        logger.info("Create EmailMessage for %s", self.get_emailaddress(),
                    extra=self.request.log_data)
        EmailMessage(
            recipient=self.get_emailaddress(),
            bounce=form.cleaned_data['bounce']).save()
        return redirect('email')


@login_required
class EmailAddressCreate(FormView):
    form_class = EmailAddressCreateForm
    template_name = 'emailaddress_create.html'

    def get_person(self):
        return get_object_or_404(Person, pk=self.kwargs['person'])

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['person'] = self.get_person()
        return context_data

    def form_valid(self, form):
        person = self.get_person()
        address = form.cleaned_data['address']
        logger.info("Create EmailAddress %s for %s", address, person,
                    extra=self.request.log_data)
        EmailAddress(
            person=person,
            address=address,
            source='Manually entered').save()
        return redirect('email')


@login_required
class EmailMessageBulkCreate(FormView):
    form_class = EmailMessageBulkCreateForm
    template_name = 'emailmessage_bulkcreate.html'

    def form_valid(self, form):
        a = form.cleaned_data['recipients']
        qs = EmailAddress.objects.filter(address__in=a)
        o = {e.address: e for e in qs}
        m = []
        errors = 0
        for address in a:
            try:
                m.append(EmailMessage(
                    recipient=o.pop(address),
                    bounce=False))
            except KeyError:
                form.add_error('recipients',
                               'Jeg kender ikke adressen %s' % address)
                errors += 1
        if errors:
            return self.form_invalid(form)
        logger.info("Bulk create messages %s", m,
                    extra=self.request.log_data)
        EmailMessage.objects.bulk_create(m)
        return redirect('email')


@login_required
class EmailSynchronize(View):
    def post(self, request):
        logger.info("EmailSynchronize.post",
                    extra=self.request.log_data)
        synchronize_addresses()
        return redirect('email')
