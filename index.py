#! /usr/bin/python
# -*- coding: utf8 -*-

# Copyright 2008 Gabriel Sean Farrell
# Copyright 2008 Mark A. Matienzo
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

"""Imports CSV data into a Solr instance."""

import os
import optparse
import time
import urllib

## local libraries
#import lib

SOLR_URL = 'http://localhost:8983/solr/update/csv?%s'

MULTIVALUE_FIELDNAMES = [
    'contents',
    'corporate_name',
    'genre',
    'isbn',
    'language_dubbed',
    'language',
    'language_subtitles',
    'personal_name',
    'place',
    'position',
    'series',
    'summary',
    'topic',
    'url',
]

# summary causes an error in solr pre 2008/01/08 dev (for my data, at
# least -- gsf) -- see 
# http://mail-archives.apache.org/mod_mbox/lucene-solr-user/200801.mbox/%3cc68e39170801081009r18b024f9g4076a6333455463e@mail.gmail.com%3e

def load_solr(csv_file, solr_url):
    """
    Load CSV file into Solr.  solr_params are a dictionary of parameters
    sent to solr on the index request.
    """
    file_path = os.path.abspath(csv_file)
    solr_params = {}
    for fieldname in MULTIVALUE_FIELDNAMES:
        tag_split = "f.%s.split" % fieldname
        solr_params[tag_split] = 'true'
        tag_separator = "f.%s.separator" % fieldname
        solr_params[tag_separator] = '|'
    solr_params['stream.file'] = file_path
    solr_params['commit'] = 'true'
    params = urllib.urlencode(solr_params)
    print "Loading records into Solr ..."
    try: 
        output = urllib.urlopen(solr_url % params)
    except IOError:
        raise IOError, 'Unable to connect to the Solr instance.'
    print output.read()

if __name__ == '__main__':
    usage = "usage: %prog [options] FILE_OR_URL"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-o', '--output', dest='out_file', metavar='OUT_FILE', 
        help='output the CSV to OUT_FILE instead of loading it into a SOLR instance')
    parser.add_option('-p', '--parsing_module', dest='parsing_module', 
        metavar='PARSING_MODULE', 
        help='use PARSING_MODULE to parse FILE_OR_URL and convert to CSV')
    parser.add_option('-s', '--solr', dest='solr', metavar='SOLR_URL', 
        help='URL for Solr, defaults to %s' % SOLR_URL, default=SOLR_URL)
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
    else:
        file_or_url = args[0]
        in_handle = urllib.urlopen(file_or_url)
        csv_file = options.out_file or 'tmp.csv'
        t1 = time.time()
        if options.parsing_module:
            csv_handle = open(csv_file, 'w')
            mod_path = options.parsing_module
            if mod_path.endswith('.py'):
                mod_path = mod_path[:-3]
            #mod_path = 'lib.' + options.parsing_module
            module = __import__(mod_path, fromlist=[''])
            print "Converting %s to CSV ..." % file_or_url
            record_count = module.write_csv(in_handle, csv_handle)
        else:
            if file_or_url == csv_file:
                # check for equality here stops us from overwriting csv_file
                # if we're loading it again
                try:
                    record_count = -1  # start at -1 to account for fieldnames
                    for line in in_handle:
                        record_count += 1
                finally:
                    in_handle.close()
            else:
                csv_handle = open(csv_file, 'w')
                try:
                    record_count = -1
                    for line in in_handle:
                        record_count += 1
                        csv_handle.write()
                finally:
                    in_handle.close()
                    csv_handle.close()
        t2 = time.time()
        if not options.out_file:
            load_solr(csv_file, options.solr)
        t3 = time.time()
        p_time = (t2 - t1) / 60
        l_time = (t3 - t2) / 60
        t_time = p_time + l_time
        rate = record_count / (t3 - t1)
        print """Processing took %0.3f minutes.
Loading took %0.3f minutes.  
That's %0.3f minutes total for %d records, 
at a rate of %0.3f records per second.
""" % (p_time, l_time, t_time, record_count, rate)

