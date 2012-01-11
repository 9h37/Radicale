# -*- coding: utf-8 -*-
#
# This file is part of Radicale Server - Calendar Server
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
Django ACL.

"""

from django.contrib.auth.models import User
from radicale import acl, config

DATABASE = config.get ("acl", "django_db")
DBPASSWD = config.get ("acl", "django_dbpasswd")

def has_right (owner, user, password):
    """Check if ``user``/``password`` couple is valid."""
    if not user or (owner not in acl.PRIVATE_USERS and user != owner):
        # No user given, or owner is not private and is not user, forbidden
        return False

    try:
        u = User.objects.get (username = user)
    except DoesNotExist:
        return False

    return u.check_password (password)

