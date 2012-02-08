from django_radicale.caldav.models import *
from django.contrib.auth.models import User

def test():
    linkdd = User.objects.get (pk = 1)

    c1 = Calendar.objects.get (pk = 1)
    c2 = Calendar.objects.get (pk = 2)

    print "Cal1"
    for e in Event.objects.filter (calendar = c1):
        print e.id

    print "Cal2"
    for e in Event.objects.filter (calendar = c2):
        print e.id
