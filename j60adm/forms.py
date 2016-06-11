import re
from django import forms
from django.core.exceptions import ValidationError

from j60adm.parser import (
    parse_registrations, parse_survey_responses, parse_addresses_emails)


class PersonImportForm(forms.Form):
    persons = forms.CharField(widget=forms.Textarea, strip=False)

    def clean_persons(self):
        csv_text = self.cleaned_data['persons']
        return parse_addresses_emails(csv_text)


class RegistrationImportForm(forms.Form):
    registrations = forms.CharField(widget=forms.Textarea, strip=False)

    def clean_registrations(self):
        csv_text = self.cleaned_data['registrations']
        return parse_registrations(csv_text)


class SurveyResponseImportForm(forms.Form):
    responses = forms.CharField(widget=forms.Textarea, strip=False)

    def clean_responses(self):
        csv_text = self.cleaned_data['responses']
        return parse_survey_responses(csv_text)


class EmailAddressCreateForm(forms.Form):
    address = forms.EmailField()


class EmailMessageCreateForm(forms.Form):
    bounce = forms.BooleanField(required=False)


class EmailMessageBulkCreateForm(forms.Form):
    recipients = forms.CharField(widget=forms.Textarea, strip=False)

    def clean_recipients(self):
        r = self.cleaned_data['recipients']
        count = len(re.findall('<', r))
        matches = re.finditer(r'<([^>]+@[^>]+)>', r)
        addresses = [mo.group(1) for mo in matches]
        if not addresses:
            raise ValidationError("No recipients")
        if len(addresses) != count:
            raise ValidationError("Some recipients are invalid")
        return addresses
