# vim: set fileencoding=utf8:
from __future__ import unicode_literals
import re
import collections
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError


@python_2_unicode_compatible
class Association:
    def __init__(self, *, name, current_period):
        self.name = name
        self.current_period = current_period

    @classmethod
    def get(cls):
        return cls(name='TÅGEKAMMERET', current_period=2015)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Person(models.Model):
    name = models.CharField(max_length=200)
    street = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    dead = models.BooleanField(blank=True)

    letter_bounced = models.BooleanField(blank=True)

    created_time = models.DateTimeField(auto_now_add=True)

    note = models.TextField(blank=True)

    def __str__(self):
        if self.dead:
            return '\u271D%s' % (self.name,)
        else:
            return self.name

    class Meta:
        ordering = ['name']

    def title_order_key(self):
        """
        Order persons without title last (alphabetically by name).
        Order persons by their latest title by period,
        then by BEST < FU < EFU, and then alphabetically by title.
        """
        try:
            t = max(self.title_set.all(), key=lambda t: t.period)
            return (1, -t.period, t.title.startswith('EFU'),
                    t.title.startswith('FU'), t.title)
        except ValueError:
            # min() raised ValueError because of an empty sequence.
            # Order persons without a title after persons with a title.
            return (2, self.name)

    def title_and_name(self):
        p = [str(t) for t in self.title_set.all()]
        return ' '.join(p + [str(self)])

    def dump(self):
        """
        Information for client code in a dictionary.
        """
        return collections.OrderedDict([
            ('id', self.id),
            ('str', self.title_and_name()),
            ('name', self.name),
            ('titles', [t.dump() for t in self.title_set.all()]),
            ('street', self.street),
            ('city', self.city),
            ('country', self.country),
            ('dead', self.dead),
        ])


@python_2_unicode_compatible
class Title(models.Model):
    prefix_term_pattern = r'(?:[KGBTO]\d*)'
    prefix_pattern = '(?:%s)*' % (prefix_term_pattern,)
    canonical_prefix_pattern = '(?:|G|B|O|TO|T\d+O)'
    modern_title_pattern = (
        '(?:CERM|FORM|INKA|KASS|NF|PR|SEKR|VC|E?FU\w{2})')
    title_pattern = (
        '(?:%s|OFULD|BEST|FU|TVC)' % (modern_title_pattern,))
    pattern = canonical_prefix_pattern + title_pattern

    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    period = models.IntegerField()

    @property
    def association(self):
        return Association.get()

    @property
    def age(self):
        return self.association.current_period - self.period

    @classmethod
    def parse(cls, s):
        """
        >>> Title.parse('T40OSEKR').age
        43
        >>> Title.parse('T40OSEKR').title
        'SEKR'
        >>> Title.parse('T40OKASS').title
        'KASS'
        >>> Title.parse('OOFULD').title
        'OFULD'
        """
        i = 0
        age = 0
        prefixes = dict(zip('KGBOT', [-1, 1, 2, 3, 1]))
        p = '^(%s|%s)(%s)$' % (cls.canonical_prefix_pattern,
                               cls.prefix_pattern, cls.title_pattern)
        mo = re.match(p, s)
        if mo is None:
            raise ValidationError("Couldn't parse %r" % (s,))
        prefix_part = mo.group(1)
        title = mo.group(2)
        for mo in re.finditer(cls.prefix_term_pattern, prefix_part):
            p = mo.group(0)
            if len(p) == 1:
                age += prefixes[p]
            else:
                age += prefixes[p[0]] * int(p[1:])

        period = Association.get().current_period - age
        return cls(period=period, title=title)

    @staticmethod
    def sup(n):
        digits = '⁰¹²³⁴⁵⁶⁷⁸⁹'
        return ''.join(digits[int(i)] for i in str(n))

    @staticmethod
    def tk_prefix(age, sup_fn=None):
        if sup_fn is None:
            sup_fn = Title.sup
        prefix = ['', 'G', 'B', 'O', 'TO']
        if age < 0:
            return 'K%s' % sup_fn(-age)
        elif age < len(prefix):
            return prefix[age]
        else:
            return 'T%sO' % sup_fn(age - 3)

    @property
    def prefix(self):
        return self.tk_prefix(self.age)

    def __str__(self):
        return '%s%s' % (self.prefix, self.title)

    def dump(self):
        return collections.OrderedDict([
            ('id', self.id),
            ('age', self.age),
            ('prefix', self.tk_prefix(self.age)),
            ('title', self.title),
            ('period', self.period),
        ])

    class Meta:
        ordering = ['-period', 'title']


@python_2_unicode_compatible
class EmailAddress(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    source = models.CharField(max_length=200)

    def __str__(self):
        return self.address

    class Meta:
        ordering = ['address']


class EmailMessage(models.Model):
    recipient = models.ForeignKey(EmailAddress, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    bounce = models.BooleanField(blank=True)

    class Meta:
        ordering = ['recipient']


@python_2_unicode_compatible
class SurveyResponse(models.Model):
    person = models.ForeignKey(Person, on_delete=models.SET_NULL,
                               null=True, blank=True)
    time = models.DateTimeField()
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    newsletter = models.BooleanField(blank=True)
    note = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return '<SurveyResponse name=%s>' % (self.name,)

    class Meta:
        ordering = ['time']

    def dump(self):
        return collections.OrderedDict([
            ('name', self.name),
            ('title', self.title),
        ])


@python_2_unicode_compatible
class Registration(models.Model):
    SHOWS = [('first', 'Første'), ('second', 'Anden'), ('none', 'Ingen'),
             ('refund', 'Refunderet')]

    person = models.ForeignKey(Person, on_delete=models.SET_NULL,
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

    @property
    def name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def dump(self):
        return collections.OrderedDict([
            ('name', self.name),
        ])

    def __str__(self):
        repr_parts = [self.show, 'name=%s' % (self.name,)]
        if self.dietary:
            repr_parts.append('dietary=%r' % (self.dietary,))
        if self.transportation:
            repr_parts.append('transportation=%r' % (self.transportation,))
        return "<Registration %s>" % ' '.join(repr_parts)

    class Meta:
        ordering = ['time']
