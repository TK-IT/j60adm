# vim: set fileencoding=utf8:
from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User


@python_2_unicode_compatible
class Association:
    def __init__(self, *, name, current_period):
        self.name = name
        self.current_period = period

    @classmethod
    def get(cls):
        return cls(name='TÅGEKAMMERET', current_period=2015)

    def __str__(self):
        return self.name


# @python_2_unicode_compatible
class Person(models.Model):
    name = models.CharField(max_length=200)
    street = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    dead = models.BooleanField(blank=True)

    created_time = models.DateTimeField(auto_now_add=True)


@python_2_unicode_compatible
class Title(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    period = models.IntegerField()

    @property
    def association(self):
        return Association.get()

    @property
    def age(self):
        return self.association.current_period - self.period

    @staticmethod
    def sup(n):
        digits = '⁰¹²³⁴⁵⁶⁷⁸⁹'
        return ''.join(digits[int(i)] for i in str(n))

    @staticmethod
    def tk_prefix(age):
        prefix = ['', 'G', 'B', 'O', 'TO']
        if age < 0:
            return 'K%s' % Title.sup(-age)
        elif age < len(prefix):
            return prefix[age]
        else:
            return 'T%sO' % Title.sup(age - 3)

    def __str__(self):
        return '%s%s' % (self.tk_prefix(self.age), self.title)

    class Meta:
        ordering = ['period', 'title']


class EmailAddress(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    source = models.CharField(max_length=200)


class EmailMessage(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    recipient = models.CharField(max_length=200)
    created_time = models.DateTimeField(auto_now_add=True)
    bounce = models.BooleanField(blank=True)


class SurveyResponse(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE,
                               null=True, blank=True)
    time = models.DateTimeField()
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    newsletter = models.BooleanField(blank=True)
    note = models.CharField(max_length=200, blank=True)


"""
Arrangement:;"TÅGEKAMMERETS 60 års jubilæumsfest";
ID;Fornavn;Efternavn;Adresse;Postnr/by;Email;Ansættelsessted;Stilling;Tilmeldingsdato;Antal;Stykpris;;Rabat;Betalt;Markedsføring;Note
Arrangement:;"Jeg kan desværre ikke komme til revyen";
Arrangement:;"Revyforestillingen kl. 13.30";
Arrangement:;"Revyforestillingen kl. 16.00";
ID;Fornavn;Efternavn;Adresse;Postnr/by;Email;Ansættelsessted;Stilling;Tilmeldingsdato;Antal;Stykpris;;Rabat;Betalt;Markedsføring;"Er du vegetar";"Er du gangbesværet...";"5. Ønsker du at modtage vores J60-nyhedsbrev...";Note
"""


class Registration(models.Model):
    SHOWS = ['Første', 'Anden', 'Ingen']

    person = models.ForeignKey(Person, on_delete=models.CASCADE,
                               null=True, blank=True)
    time = models.DateTimeField()
    survey_id = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    dietary = models.CharField(max_length=200, blank=True)
    newsletter = models.BooleanField(blank=True)
    transportation = models.BooleanField(blank=True)

    show = models.CharField(max_length=200, choices=SHOWS)
    webshop_show = models.CharField(max_length=200, choices=SHOWS)

    note = models.CharField(max_length=200, blank=True)
