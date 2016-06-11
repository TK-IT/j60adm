from django import forms

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
