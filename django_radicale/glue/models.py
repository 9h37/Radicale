from django.db import models
from django.contrib.auth.models import User
from django_radicale.icalendar import Calendar, Event

class DjangoCalendar(models.Model):
    owner = models.ForeignKey(User, null=True)
    path = models.CharField(max_length=250)
    prodid = models.CharField(max_length=250)

    def to_ical(self):
        ical = Calendar()
        ical.add('prodid', self.prodid)
        ical.add('version', '2.0')

        for e in DjangoEvent.objects.filter(calendar = self):
            event = Event()
            event.add('summary', e.title)
            event.add('description', e.description)
            event.add('dtstart', e.start)
            event.add('dtend', e.end)
            event.add('dtstamp', e.created)
            ical.add_component(event)

        return ical

class DjangoEvent(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    created = models.DateTimeField()
    allDay = models.BooleanField(default=False)
    creator = models.ForeignKey(User, null=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100, null=True)
    calendar = models.ForeignKey(DjangoCalendar)
    editable = models.BooleanField(default=False)
