# vim: set fileencoding=utf8:
from __future__ import unicode_literals
import re
import csv
import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone


def parse_addresses_emails(csv_text):
    from j60adm.models import (
        Association, Person, Title, EmailAddress, EmailMessage)

    association = Association.get()
    reader = csv.reader(csv_text.splitlines(True), dialect='excel-tab')
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


def parse_survey_responses(csv_text):
    from j60adm.models import SurveyResponse
    reader = csv.reader(csv_text.splitlines(True), dialect='excel-tab')
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
        if not any(row):
            continue
        if len(row) < 6:
            raise ValidationError("Expected at least 6 cells: %r" % (row,))
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


def extract_registration_sections(csv_text):
    """
    >>> extract_registration_sections('''\\
    ... Arrangement:;Bla;
    ...
    ... A;B
    ... C;D
    ...
    ... Arrangement:;Hej;
    ... E;F;G
    ... ''')
    [('Bla', [['A', 'B'], ['C', 'D']]), ('Hej', [['E', 'F', 'G']])]
    """
    sections = []

    reader = csv.reader(csv_text.splitlines(True), delimiter=';')
    rows = iter(reader)
    row = next(rows)

    while row is not None:
        if len(row) != 3 or row != ['Arrangement:', row[1], '']:
            raise ValidationError("Unexpected row %r" % (row,))
        section_title = row[1]
        row = next(rows)
        while row == []:
            row = next(rows, None)
        section_rows = []
        while row:
            section_rows.append(row)
            row = next(rows, None)
        while row == []:
            row = next(rows, None)
        sections.append((section_title, section_rows))
    return sections


def get_registration_people(sections):
    shows = {
        'Jeg kan desværre ikke komme til revyen': 'none',
        'Revyforestillingen kl. 13.30': 'first',
        'Revyforestillingen kl. 16.00': 'second',
    }

    if len(sections) != 1 + len(shows):
        raise ValidationError("Expected %s sections, found %s" %
                              (1 + len(shows), len(sections)))
    name = sections[0][0]
    expected = 'TÅGEKAMMERETS 60 års jubilæumsfest'
    if name != expected:
        raise ValidationError("Expected %r, got %r" % (expected, name))

    header = ['ID', 'Fornavn', 'Efternavn', 'Adresse', 'Postnr/by',
              'Email', 'Ansættelsessted', 'Stilling', 'Tilmeldingsdato',
              'Antal', 'Stykpris', '', 'Rabat', 'Betalt', 'Markedsføring',
              'Note']
    first_row = sections[0][1][0]
    if first_row != header:
        raise ValidationError("Expected %r, got %r" % (header, first_row))

    by_id = {}
    for row in sections[0][1][1:]:
        id = row[0]
        by_id[id] = (row, {})

    for name, rows in sections[1:]:
        try:
            key = shows.pop(name)
        except KeyError:
            raise ValidationError("Unexpected %r, expected one of %r" %
                                  (key, sorted(shows.keys())))
        header = ['ID', 'Fornavn', 'Efternavn', 'Adresse', 'Postnr/by',
                  'Email', 'Ansættelsessted', 'Stilling', 'Tilmeldingsdato',
                  'Antal', 'Stykpris', '', 'Rabat', 'Betalt', 'Markedsføring',
                  # 'Er du vegetar, allergiker, eller lignende? ' +
                  # 'Hvis ja, anfør det her:',
                  # 'Er du gangbesværet, og har du ikke selv mulighed ' +
                  # 'for at transportere\ndig mellem Matematisk Institut ' +
                  # 'og Stakladen (ca. 650 m)?\nHvis ja, så anfør det her, ' +
                  # 'og så forsøger vi at arrangere transport:',
                  # '5. Ønsker du at modtage vores J60-nyhedsbrev og få ' +
                  # 'informationer om salg\naf merchandise, arrangementer i ' +
                  # 'jubilæumsugen, og lignende (maks. 1\nemail om måneden)?',
                  # 'Note',
                  ]
        first_row = rows[0]
        if first_row[:len(header)] != header:
            raise ValidationError("Expected %r, got %r" %
                                  (header, first_row[:len(header)]))
        if len(first_row) != len(header) + 4:
            raise ValidationError("Expected %s columns, got %s" %
                                  (len(header) + 4, len(first_row)))
        if first_row[-1] != 'Note':
            raise ValidationError("Expected 'Note', got %s" % (first_row[-1],))
        for row in rows[1:]:
            id = row[0]
            try:
                p = by_id[id]
            except KeyError:
                raise ValidationError("ID %r not in main list" % (id,))
            p[1][key] = row

    return by_id


def parse_registration_time_naive(time):
    """
    >>> parse_registration_time_naive("03-06-2016 22:38:50")
    datetime.datetime(2016, 6, 3, 22, 38, 50)
    """

    mo = re.match(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)', time)
    if mo is None:
        raise ValidationError("Invalid time: %s" % (time,))
    day, month, year, hour, minute, second = mo.groups()
    time = datetime.datetime(int(year), int(month), int(day),
                             int(hour), int(minute), int(second))
    return time


def parse_registration_time(time):
    dt = parse_registration_time_naive(time)
    return dt.replace(tzinfo=timezone.get_default_timezone())


def make_registration(data):
    from j60adm.models import Registration

    main_row, shows_rows = data
    if len(main_row) != 17:
        raise ValidationError("Expected 17 columns, got %s: %s" %
                              (len(main_row), main_row))
    (id, first_name, last_name, _1, _2, email, _3, _4, time,
     _5, _6, _7, _8, _9, _10, note, refund_note) = main_row[:17]
    if len(shows_rows) == 0:
        dietary = ''
        newsletter = False
        transportation = False
        if refund_note.startswith('Krediteret'):
            show = 'refund'
        else:
            raise ValidationError("No shows and no refund: %r" % (main_row[:16],))
    elif len(shows_rows) == 1:
        (show, show_row), = shows_rows.items()
        dietary, transportation, newsletter = show_row[15:18]
        transportation = (transportation == 'Ja')
        newsletter = (newsletter == 'Ja')
    time = parse_registration_time(time)
    return Registration(
        time=time, survey_id=id, first_name=first_name, last_name=last_name,
        email=email, dietary=dietary, newsletter=newsletter,
        transportation=transportation, show=show, webshop_show=show,
        note=note + refund_note)


def parse_registrations(csv_text):
    sections = extract_registration_sections(csv_text)
    people = get_registration_people(sections)
    registrations = [make_registration(d) for d in people.values()]
    return registrations
