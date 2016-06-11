from j60adm.models import Person, EmailAddress


def synchronize_addresses(qs=None):
    if qs is None:
        qs = Person.objects.all()
        qs = qs.prefetch_related(
            'registration_set', 'surveyresponse_set', 'emailaddress_set')

    create = []
    for person in qs:
        addys = set(e.address for e in person.emailaddress_set.all())
        for r in person.registration_set.all():
            a = r.email.lower().strip()
            if a not in addys:
                create.append(EmailAddress(
                    person=person, address=a, source='Registration'))
                addys.add(a)
        for r in person.surveyresponse_set.all():
            a = r.email.lower().strip()
            if a not in addys:
                create.append(EmailAddress(
                    person=person, address=a, source='Survey'))
                addys.add(a)
    EmailAddress.objects.bulk_create(create)
