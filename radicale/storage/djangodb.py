# -*- coding: utf-8 -*-
#
# This file is part of Radicale Server - Calendar Server
# Copyright © 2012 David Delassus
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radicale.  If not, see <http://www.gnu.org/licenses/>.

"""
Django/SQL storage backend.

"""

import time
from datetime import datetime
from contextlib import contextmanager

from radicale import config, ical

from django.core.management import setup_environ
from django_radicale import settings

setup_environ(settings)

from django_radicale.glue.models import *
from django_radicale.icalendar import Calendar
from django_radicale.icalendar import Event


class Collection(ical.Collection):
    @property
    def _model(self):
        try:
            calendar = DjangoCalendar.objects.get(path = self.path)
        except DjangoCalendar.DoesNotExist:
            return None
        return calendar

    def save(self, text):
        ical = Calendar.from_string(text)

        try:
            user = User.objects.get(username = self.owner)
        except User.DoesNotExist:
            return

        if self._model is not None:
            calendar = self._model
        else:
            calendar = DjangoCalendar()
            calendar.owner = user

        calendar.path = self.path
        calendar.prodid = ical.prodid

        calendar.save()

        for icalevent in ical.walk():
            try:
                event = DjangoEvent.objects.get(uid = icalevent.uid)
            except DoesNotExist:
                event = DjangoEvent()
                event.creator = user
                event.created = datetime.fromtimestamp(time.time())

            event.uid = icalevent.uid
            event.calendar = calendar
            event.start = icalevent.dtstart
            event.end = icalevent.dtend
            event.title = icalevent.summary
            event.description = icalevent.description

            event.save()

    def delete(self):
        if self._model is not None:
            calendar = self._model

            for event in Event.objects.filter(calendar = calendar):
                event.delete()

            calendar.delete()

    @property
    def text(self):
        if self._model is not None:
            ical = self._model.to_ical()
            return ical.to_ical()
        else:
            return ""

    @classmethod
    def children(cls, path):
        return []

    @classmethod
    def is_collection(cls, path):
        return False # No collection, so always return false.

    @classmethod
    def is_item(cls, path):
        return True # No collection, so always return true.

    @property
    @contextmanager
    def props(self):
        yield {}

ical.Collection = Collection
