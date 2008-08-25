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

"""Processes MARC data for importing."""

import csv
import optparse
import os
import pymarc
import re
import sys
import time
import urllib
#import unicodedata

try:
    set
except NameError:
    from sets import Set as set

## local libs
from lib import csv_index
from lib import marc_processing as mp

ILS = '' # Horizon, III, or Unicorn for specific record ID handling

def write_csv(marc_file_handle, csv_file_handle, ils=ILS):
    """
    Convert a MARC dump file to a CSV file.
    """
    # This doctest commented out until field names are stable.
    #>>> write_csv('test/marc.dat', 'test/records.csv')
    #>>> csv_records = open('test/records.csv').read()
    #>>> csv_measure = open('test/measure.csv').read()
    #>>> csv_records == csv_measure
    #True
    #>>> os.remove('test/records.csv')
    reader = pymarc.MARCReader(marc_file_handle)
    fieldname_dict = {}
    for fieldname in mp.FIELDNAMES:
        fieldname_dict[fieldname] = fieldname
    #for record in reader
    count = 0
    try:
        writer = csv.DictWriter(csv_file_handle, mp.FIELDNAMES)
        writer.writerow(fieldname_dict)
        for marc_record in reader:
            count += 1
            try:
                record = mp.get_record(marc_record, ils=ils)
                if record:  # skip when get_record returns None
                    row = mp.get_row(record)
                    writer.writerow(row)
            except:
                sys.stderr.write("\nError in MARC record #%s (%s):\n" % (count, 
                        marc_record.title()))
                raise
            else:
                if count % 1000:
                    sys.stderr.write(".")
                else:
                    sys.stderr.write(str(count))
    finally:
        marc_file_handle.close()
        csv_file_handle.close()
    sys.stderr.write("\nProcessed %s records.\n" % count)
    return count

def write_json(marc_file_handle, json_directory):
    """
    Convert a MARC dump file to a bunch of JSON files.
    """
    pass

if __name__ == '__main__':
    ils_choices = ('', 'III', 'Unicorn', 'Horizon')
    usage = "usage: %prog [options] FILE_OR_URL"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-i', '--ils', dest='ils', metavar='ILS', 
        help='ILS the MARC was exported from', choices=ils_choices, 
        default=ILS)
    parser.add_option('-o', '--output', dest='out_file', metavar='OUT_FILE', 
        help='output the CSV to OUT_FILE instead of loading it into a SOLR instance')
    parser.add_option('-s', '--solr', dest='solr', metavar='SOLR_URL', 
        help='URL for Solr, defaults to %s' % csv_index.SOLR_URL, 
        default=csv_index.SOLR_URL)
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
    else:
        file_or_url = args[0]
        in_handle = urllib.urlopen(file_or_url)
        csv_file = options.out_file or 'tmp.csv'
        csv_handle = open(csv_file, 'w')
        print "Converting %s to CSV ..." % file_or_url
        t1 = time.time()
        record_count = write_csv(in_handle, csv_handle, ils=options.ils)
        t2 = time.time()
        if not options.out_file:
            csv_index.load_solr(csv_file, options.solr)
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

