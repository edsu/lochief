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
    def __unicode__(self):
        return unicode(self.id)
    def current_version(self):
        return self.version_set.order_by('-id')[0]

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

class VersionInline(admin.TabularInline):
    model = Version

class RecordAdmin(admin.ModelAdmin):
    inlines = [VersionInline]

admin.site.register(Record, RecordAdmin)
admin.site.register(Version)
