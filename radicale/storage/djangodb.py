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
from icalendar import Calendar as iCalendar
from icalendar import Event as iEvent
from icalendar import vDatetime, vDDDTypes


class Collection(ical.Collection):
    @property
    def model(self):
        """Return the given django model for ``path``."""

        if Collection.is_leaf(self.path):
            try:
                return DjangoCalendar.objects.get(path=self.path)
            except DjangoCalendar.DoesNotExist:
                return None
        else:
            try:
                return DjangoEvent.objects.get(path=self.path)
            except DjangoEvent.DoesNotExist:
                return None

    def save(self, text):
        """Write ``text`` into the database."""

        user = User.objects.get(username = self.owner)

        try:
            calendar = DjangoCalendar.objects.get(path=self.path)
        except DjangoCalendar.DoesNotExist:
            calendar = DjangoCalendar()
            calendar.owner = user

        ical = iCalendar.from_ical(text)
        calendar.path    = self.path
        calendar.prodid  = ical['prodid']
        calendar.version = ical['version']
        calendar.save()

        for icalevent in ical.walk('VEVENT'):
            try:
                event = DjangoEvent.objects.get(uid = icalevent['uid'])
            except DjangoEvent.DoesNotExist:
                event = DjangoEvent()
                event.creator = user

            event.uid         = icalevent['uid']
            event.path        = self.path + "/" + icalevent['X-RADICALE-NAME']
            event.calendar    = calendar
            event.start       = vDatetime.from_ical(icalevent['dtstart'].to_ical())
            event.end         = vDatetime.from_ical(icalevent['dtend'].to_ical())
            event.title       = icalevent['summary']
            if 'description' in icalevent:
                event.description = icalevent['description']

            event.save()

    def delete(self):
        """Delete entry in the database."""
        if self.model is not None:
            self.model.delete()

    @property
    def text(self):
        if self.model is not None:
            ical = self.model.to_ical()
            return ical.to_ical()
        else:
            return ""

    @classmethod
    def children(cls, path):
        """Return every events contained in path ``path``."""
        if cls.is_node(path) or cls.is_leaf(path):
            events = DjangoEvent.objects.filter(path=path)
            for e in events:
                yield cls(e.path)

    @classmethod
    def is_node(cls, path):
        """
            Check if ``path`` is a collection of calendars.
            Equivalent to SQL query :
                SELECT * FROM calendar WHERE path LIKE "path%"
        """
        try:
            DjangoCalendar.objects.get(path__startswith=path)
        except DjangoCalendar.DoesNotExist:
            return False

        return True

    @classmethod
    def is_leaf(cls, path):
        """
            Check if ``path`` is a calendar.
            Equivalent to SQL query :
                SELECT * FROM calendar WHERE path = path
        """

        try:
            DjangoCalendar.objects.get(path=path)
        except DjangoCalendar.DoesNotExist:
            return False

        return True

    @property
    def last_modified(self):
        """Return the last modified property of a calendar, create it if it doesn't exist."""
        return time.strftime("%a, %d, %b, %Y %H:%M:%S +0000", self.model.last_modified.timetuple())

    @property
    @contextmanager
    def props(self):
        yield {}

ical.Collection = Collection
