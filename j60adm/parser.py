# vim: set fileencoding=utf8:
from __future__ import unicode_literals
import csv
from django.core.exceptions import ValidationError
from django.utils import timezone
from j60adm.models import (
    Association, Person, Title, EmailAddress, EmailMessage,
    SurveyResponse, Registration,
)


def parse_addresses_emails(s):
    association = Association.get()
    reader = csv.reader([s], dialect='excel-tab')
    rows = iter(reader)
    header = next(rows)
    expected_header = [
        'Navn', 'Titel (nyeste)', 'Grad', 'Email', 'Gade', 'By', 'Land',
        'Afdød', 'Modtager', 'Bounce?']
    if header[:len(expected_header)] != expected_header:
        raise ValidationError(
            "Header does not match expectation: %r is not a prefix of %r" %
            (expected_header, header))
    persons = []
    titles = []
    email_addresses = []
    email_messages = []
    for row in rows:
        (name, title, age, email, street, city, country,
         dead, _recipient, bounce) = row[:10]

        dead = (dead == 'ja')
        bounce = bool(bounce)
        period = association.current_period - age
        person = Person(
            name=name, street=street, city=city, country=country, dead=dead)
        persons.append(person)
        titles.append(Title(person=person, title=title, period=period))
        if email:
            email_addresses.append(EmailAddress(
                person=person, address=email, source='j60adr'))
            email_messages.append(EmailMessage(
                person=person, recipient=email, bounce=bounce))
    return persons, titles + email_addresses + email_messages


def parse_survey_responses(s):
    reader = csv.reader([s], dialect='excel-tab')
    rows = iter(reader)
    header = next(rows)
    expected_header = [
        'Timestamp', 'Navn', 'Titel og årgang', 'Email',
        'Vil du modtage vores nyhedsbrev?']
    if header[:len(expected_header)] != expected_header:
        raise ValidationError(
            "Header does not match expectation: %r is not a prefix of %r" %
            (expected_header, header))
    survey_responses = []
    for row in rows:
        time, name, title, email, newsletter, note = row[:6]
        mo = re.match(r'(\d+)/(\d+)/(\d+) (\d+):(\d+):(\d+)', time)
        month, day, year, hour, minute, second = mo.groups()
        tzinfo = timezone.get_default_timezone()
        time = datetime.datetime(int(year), int(month), int(day),
                                 int(hour), int(minute), int(second),
                                 tzinfo=tzinfo)
        newsletter = newsletter.startswith('Ja')
        survey_responses.append(SurveyResponse(
            time=time, name=name, title=title, email=email,
            newsletter=newsletter, note=note))
    return survey_responses


def parse_registration(s):
    reader = csv.reader([s], delimiter=';')
    rows = iter(reader)

    row = next(rows)
    expected_header = [
        'Arrangement:', 'TÅGEKAMMERETS 60 års jubilæumsfest', '']
    if row != expected_header:
        raise ValidationError(
            "Header does not match expectation: %r is not %r" %
            (expected_header, header))

    registrations = []
    ...
    return registrations
