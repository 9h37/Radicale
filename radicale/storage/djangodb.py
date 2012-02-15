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

import os
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
from django_radicale.icalendar import vDatetime, vDDDTypes


class Collection(ical.Collection):
    @property
    def _path(self):
        return os.path.dirname(self.path)

    @property
    def _model(self):
        try:
            calendar = DjangoCalendar.objects.get(path = self._path)
        except DjangoCalendar.DoesNotExist:
            return None
        return calendar

    def save(self, text):
        ical = Calendar.from_ical(text)

        try:
            user = User.objects.get(username = self.owner)
        except User.DoesNotExist:
            raise User.DoesNotExist

        if self._model is not None:
            calendar = self._model
        else:
            calendar = DjangoCalendar()
            calendar.owner = user

        calendar.path = self._path
        calendar.prodid = ical['prodid']

        calendar.save()

        for icalevent in ical.walk('VEVENT'):
            try:
                event = DjangoEvent.objects.get(uid = icalevent['uid'])
            except DjangoEvent.DoesNotExist:
                event = DjangoEvent()
                event.creator = user

            event.uid = icalevent['uid']
            event.calendar = calendar
            event.start = vDatetime.from_ical(icalevent['dtstart'].to_ical())
            event.end = vDatetime.from_ical(icalevent['dtend'].to_ical())
            event.title = icalevent['summary']
            event.description = icalevent['description']

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
        print path
        return False # No collection, so always return false.

    @classmethod
    def is_item(cls, path):
        return True # No collection, so always return true.

    @property
    def last_modified(self):
        modification_time = self._model.last_modified
        return time.strftime("%a, %d, %b, %Y %H:%M:%S +0000", modification_time)

    @property
    @contextmanager
    def props(self):
        yield {}

ical.Collection = Collection
