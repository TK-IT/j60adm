from j60adm.models import Person


def synchronize_addresses(qs=None):
    if qs is None:
        qs = Person.objects.all()
        qs = qs.prefetch_related(
            'registration_set', 'surveyresponse_set', 'emailaddress_set')

    create = []
    for person in qs:
        addys = set(e.address for e in person.emailaddress_set)
        for r in person.registration_set.all():
            if r.email not in addys:
                create.append(EmailAddress(
                    person=person, address=r.email, source='Registration'))
                addys.add(r.email)
        for r in person.surveyresponse_set.all():
            if r.email not in addys:
                create.append(EmailAddress(
                    person=person, address=r.email, source='Survey'))
                addys.add(r.email)
    EmailAddress.objects.bulk_create(create)
