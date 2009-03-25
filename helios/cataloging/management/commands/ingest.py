# Copyright 2009 Gabriel Sean Farrell
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

"""Ingests documents into the catalog."""

import optparse
from optparse import make_option
import urllib

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson

from helios.cataloging import models

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-p', '--parser',
            dest='parser',
            metavar='PARSER', 
            help='Use PARSER (relative path) to parse FILEs for indexing'),
    )
    help = 'Ingests documents into the catalog.'
    args = 'file_or_url [file_or_url ...]'

    def handle(self, *file_or_urls, **options):
        if file_or_urls:
            parser = options.get('parser')
            module = None
            if parser:
                if parser.endswith('.py'):
                    parser = parser[:-3]
                module = __import__('parsers.' + parser, globals(), locals(), 
                        [parser])
        for file_or_url in file_or_urls:
            data_handle = urllib.urlopen(file_or_url)
            # committer is "machine" from fixture
            committer = User.objects.get(id=2)
            if not module:
                # guess parser based on file extension
                if file_or_url.endswith('.mrc'):
                    from parsers import marc as module
            if not module:
                raise CommandError("Please specify a parser.")
            count = 0
            for record in module.record_generator(data_handle):
                count += 1
                db_record = models.Record()
                db_record.save()
                id = db_record.id
                print "Saving record %s" % id
                record['id'] = id
                db_record.version_set.create(
                    data=simplejson.dumps(record), 
                    message='record %s created by ingest' % id,
                    committer=committer,
                )
            print
            print "%s records saved" % count

