from django.db import models
from django.contrib.auth.models import User
from django_radicale.icalendar import Calendar, Event, vDatetime

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

            event['dtstart'] = vDatetime(e.start)
            event['dtend'] = vDatetime(e.end)
            event['dtstamp'] = vDatetime(e.created)

            ical.add_component(event)

        return ical

class DjangoEvent(models.Model):
    uid = models.CharField(max_length=15)
    start = models.DateTimeField()
    end = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    allDay = models.BooleanField(default=False)
    creator = models.ForeignKey(User, null=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100, null=True)
    calendar = models.ForeignKey(DjangoCalendar)
    editable = models.BooleanField(default=False)
