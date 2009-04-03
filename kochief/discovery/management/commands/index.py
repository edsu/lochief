#! /usr/bin/python
# -*- coding: utf8 -*-

# Copyright 2009 Gabriel Sean Farrell
# Copyright 2008 Mark A. Matienzo
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

"""Indexes documents in a Solr instance."""

import os
import optparse
import sys
import time
import urllib
from optparse import make_option

try:
    from xml.etree import ElementTree as et  # builtin in Python 2.5
except ImportError:
    import elementtree.ElementTree as et

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

CSV_FILE = 'tmp.csv'

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-n', '--new', 
            action='store_true',
            dest='new',
            help='Create a new index.  If the index already exists, it will be replaced.'),
        make_option('-p', '--parser',
            dest='parser',
            metavar='PARSER', 
            help='Use PARSER (in kochief/parsers/) to parse files or urls for indexing'),
    )
    help = 'Indexes documents in a Solr instance.'
    args = '[file_or_url ...]'

    def handle(self, *file_or_urls, **options):
        new = options.get('new')
        if new:
            # create/replace index
            pass
        if file_or_urls:
            parser = options.get('parser')
            module = None
            if parser:
                if parser.endswith('.py'):
                    parser = parser[:-3]
                module = __import__('kochief.parsers.' + parser, globals(), 
                        locals(), [parser])
        for file_or_url in file_or_urls:
            if not module:
                # guess parser based on file extension
                if file_or_url.endswith('.mrc'):
                    from kochief.parsers import marc as module
            if not module:
                raise CommandError("Please specify a parser.")
            print "Converting %s to CSV ..." % file_or_url
            t1 = time.time()
            data_handle = urllib.urlopen(file_or_url)
            try:
                csv_handle = open(CSV_FILE, 'w')
                record_count = module.write_csv(data_handle, csv_handle)
            finally:
                csv_handle.close()
            t2 = time.time()
            self._load_solr(CSV_FILE)
            t3 = time.time()
            os.remove(CSV_FILE)
            p_time = (t2 - t1) / 60
            l_time = (t3 - t2) / 60
            t_time = p_time + l_time
            rate = record_count / (t3 - t1)
            print """Processing took %0.3f minutes.
Loading took %0.3f minutes.  
That's %0.3f minutes total for %d records, 
at a rate of %0.3f records per second.
""" % (p_time, l_time, t_time, record_count, rate)

    def _get_multi(self):
        """Inspect solr schema.xml for multivalue fields."""
        multivalue_fieldnames = []
        schema = et.parse(settings.SOLR_DIR + 'conf/schema.xml')
        fields_element = schema.find('fields')
        field_elements = fields_element.findall('field')
        for field in field_elements:
            if field.get('multiValued') == 'true':
                multivalue_fieldnames.append(field.get('name'))
        return multivalue_fieldnames

    def _load_solr(self, csv_file):
        """
        Load CSV file into Solr.  solr_params are a dictionary of parameters
        sent to solr on the index request.
        """
        file_path = os.path.abspath(csv_file)
        solr_params = {}
        for fieldname in self._get_multi():
            tag_split = "f.%s.split" % fieldname
            solr_params[tag_split] = 'true'
            tag_separator = "f.%s.separator" % fieldname
            solr_params[tag_separator] = '|'
        solr_params['stream.file'] = file_path
        solr_params['commit'] = 'true'
        params = urllib.urlencode(solr_params)
        update_url = settings.SOLR_URL + 'update/csv?%s'
        print "Loading records into Solr ..."
        try: 
            output = urllib.urlopen(update_url % params)
        except IOError:
            raise IOError, 'Unable to connect to the Solr instance.'
        print "Solr response:\n"
        print output.read()

