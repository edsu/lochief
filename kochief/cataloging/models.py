# Copyright 2008 Gabriel Farrell
#
# This file is part of Kochief.
# 
# Kochief is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Kochief is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Kochief.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils import simplejson

class Record(models.Model):
    def __unicode__(self):
        return unicode(self.id)

    def get_current(self):
        return self.get_versions()[0]

    def get_versions(self):
        return self.version_set.order_by('-id')

class Version(models.Model):
    record = models.ForeignKey(Record)
    data = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=256)
    committer = models.ForeignKey(User)

    class Meta:
        ordering = ['-timestamp']

    def __unicode__(self):
        return self.message

    def get_data(self):
        return simplejson.loads(self.data)

class VersionInline(admin.TabularInline):
    model = Version
    extra = 1

class RecordAdmin(admin.ModelAdmin):
    inlines = [VersionInline]

admin.site.register(Record, RecordAdmin)
admin.site.register(Version)
