# Copyright 2008 Gabriel Farrell
#
# This file is part of Helios.
# 
# Helios is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Helios is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Helios.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

class Record(models.Model):
    id = models.CharField(max_length=256, primary_key=True)

    def __unicode__(self):
        return self.id

class Version(models.Model):
    record = models.ForeignKey(Record)
    data = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=256)
    committer = models.ForeignKey(User)

    def __unicode__(self):
        return self.message

admin.site.register(Record)
admin.site.register(Version)
