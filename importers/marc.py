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
from lib import csv_index, marc_maps

ILS = '' # Horizon, III, or Unicorn for specific record ID handling

FIELDNAMES = [
    'audience',
    'author',
    'bib_num',
    'contents',
    'corporate_name',
    'ctrl_num',
    'format',
    'full_title',
    'genre',
    'imprint',
    'title',
    'title_sort',
    'id',
    'isbn',
    'language',
    'language_dubbed', 
    'language_subtitles',
    'oclc_num',
    'personal_name',
    'place',
    'pubyear',
    'publisher',
    'series',
    'summary',
    'topic',
    'upc',
    'url',
]
NONINT_RE = re.compile(r'\D')
ISBN_RE = re.compile(r'(\b\d{10}\b|\b\d{13}\b)')
UPC_RE = re.compile(r'\b\d{12}\b')

class RowDict(dict):
    """
    Subclass of dict that joins sequences and encodes to utf-8 on get.
    Encoding to utf-8 is necessary for Python's csv library because it 
    can't handle unicode.
    >>> row = RowDict()
    >>> row['bob'] = ['Montalb\\xe2an, Ricardo', 'Roddenberry, Gene']
    >>> row.get('bob')
    'Montalb\\xc3\\xa1n, Ricardo|Roddenberry, Gene'
    >>> print row.get('bob')
    Montalbán, Ricardo|Roddenberry, Gene
    """
    def get(self, key, *args):
        value = dict.get(self, key, *args)
        if not value:
            return ''
        if hasattr(value, '__iter__'):
            value = '|'.join([x for x in value if x])
        return pymarc.marc8.marc8_to_unicode(value).encode('utf8')

def normalize(value):
    if value:
        return value.replace('.', '').strip(',:/; ')
  
def subfield_list(field, subfield_indicator):
    subfields = field.get_subfields(subfield_indicator)
    if subfields is not None:
        return [normalize(subfield) for subfield in subfields]
    else:
        return []

def multi_field_list(fields, indicators):
    values = []
    for f in fields:
        for i in indicators:
            values.extend(subfield_list(f, i))
    return set(values)

# Dragged over from Casey's processors.py.
def get_format(record):
    format = ''
    description = ''
    if record['007']:
        description = record['007'].value()
    leader = record.leader
    if len(leader) > 7:
        if len(description) > 5:
            if description[0] == 'c':            # electronic resource
                if description[1] == 'r':        # remote resource
                    if description[5] == 'a':    # has sound
                        format = 'eAudio'
                    else:
                        format = 'eBook'
                elif description[1] == 'o':      # optical disc
                    format = 'CD-ROM'
            elif description[0] == 's':          # sound recording
                if leader[6] == 'i':             # nonmusical sound recording
                    if description[1] == 's':   # sound cassette
                        format = 'Book On Cassette'
                    elif description[1] == 'd':    # sound disc
                        if description[6] == 'g' or description[6] == 'z':
                            # 4 3/4 inch or Other size
                            format = 'Book On CD'
                elif leader[6] == 'j':        # musical sound recording
                    if description[1] == 's':    # sound cassette
                        format = 'Cassette'
                    elif description[1] == 'd':    # sound disc
                        if description[6] == 'g' or description[6] == 'z':
                            # 4 3/4 inch or Other size
                            format = 'Music CD'
                        elif description[6] == 'e':   # 12 inch
                            format = 'Phono Record'
            elif description[0] == 'v':            # videorecording
                if description[1] == 'd':        # videodisc
                    format = 'DVD'
                elif description[1] == 'f':        # videocassette
                    format = 'Videocassette'
    # now do guesses that are NOT based upon physical description 
    # (physical description is going to be the most reliable indicator, 
    # when it exists...) 
    elif leader[6] == 'a':                # language material
        fixed = record['008'].value()
        if leader[7] == 'm':            # monograph
            if len(fixed) > 22:
                if fixed[23] == 'd':    # form of item = large print
                    format = 'Large Print Book'
                elif fixed[23] == 's':    # electronic resource
                    format = 'eBook'
                else:
                    format = 'Book'
            else:
                format = 'Book'
        elif leader[7] == 's':            # serial
            if len(fixed) > 18:
                frequencies = ['b', 'c', 'd', 'e', 'f', 'i', 'j', 
                        'm', 'q', 's', 't', 'w']
                if fixed[18] in frequencies:
                    format = 'Journal'
                else:
                    # this is here to prevent stuff that librarians 
                    # and nobody else would consider to be a serial 
                    # from being labeled as a magazine.
                    format = 'Book'
    elif leader[6] == 'e':
        format = 'Map'
    elif leader[6] == 'c':
        format = 'Musical Score'
    return format

def id_match(id_fields, id_re):
    id_list = []
    for field in id_fields:
        id_str = normalize(field['a'])
        if id_str:
            id_match = id_re.match(id_str)
            if id_match:
                id = id_match.group()
                id_list.append(id)
    return id_list

def get_languages(language_codes):
    split_codes = []
    for code in language_codes:
        code = code.lower()
        if len(code) > 3:
            split_code = [code[k:k+3] for k in range(0, len(code), 3)]
            split_codes.extend(split_code)
        else:
            split_codes.append(code)
    languages = []
    for code in split_codes:
        try:
            language = marc_maps.LANGUAGE_CODING_MAP[code]
        except KeyError:
            language = None
        if language:
            languages.append(language)
    return set(languages)

# Roles with names (i.e. "Glover, Crispin (Actor)") looks neat but is
# kind of useless from a searching point of view.  A search for "Law,
# Jude (Actor)" won't return plain old "Law, Jude".  I welcome other
# ideas for incorporating roles.
#def extract_name(field):
#    role_map = maps.ROLE_CODING_MAP
#    name = normalize(field['a'])
#    if name:
#        role_key = field['4']
#        if role_key:
#            try:
#                name = '%s (%s)' % (name, role_map[role_key])
#            except KeyError:
#                pass
#    return name
        
def get_row(record, count, ils=None):
    """
    Pulls the fields from a MARCReader record into a dictionary.
    >>> marc_file_handle = open('test/marc.dat')
    >>> reader = pymarc.MARCReader(marc_file_handle)
    >>> count = 0
    >>> for record in reader:
    ...     count += 1
    ...     row = get_row(record, count)
    ...     print row['author']
    ...     break
    ...
    George, Henry, 1839-1897.
    """
    row = RowDict()

    try:
        if ils == 'Horizon':
            row['id'] = record['999']['a']
        elif ils == 'III':
            # [1:-1] because that's how it's referred to in the opac
            row['id'] = record['907']['a'][1:-1]
        elif ils == 'Unicorn':
            row['id'] = record['35']['a']
        else:
            row['id'] = record['001'].value()
    except AttributeError:
        # try other fields for id?
        #sys.stderr.write(
        #        "\nRecord #%s: No value in ID field, leaving ID blank\n" 
        #        % count)
        #row['id'] = ''
        # if it has no id let's not include it
        return
    
    row['format'] = get_format(record)

    # should ctrl_num default to 001 or 035?
    if record['001']:
        row['ctrl_num'] = record['001'].value() 

    # there should be a test here for the 001 to start with 'oc'
    try:
        oclc_number = record['001'].value()
    except AttributeError:
        oclc_number = ''
    row['oclc_num'] = oclc_number

    if record['008']:
        field008 = record['008'].value()

        # "a" added for noninteger search to work
        dates = (field008[7:11] + 'a', field008[11:15] + 'a')
        # test for which date is more precise based on searching for
        # first occurence of nonintegers, i.e. 196u > 19uu
        occur0 = NONINT_RE.search(dates[0]).start()
        occur1 = NONINT_RE.search(dates[1]).start()
        # if both are specific to the year, pick the earlier of the two
        if occur0 == 4 and occur1 == 4:
            date = min(dates[0], dates[1])
        else:
            if occur0 >= occur1:
                date = dates[0]
            else:
                date = dates[1]
        # don't use it if it starts with a noninteger
        if NONINT_RE.match(date):
            row['pubyear'] = ''
        else:
            # substitute all nonints with dashes, chop off "a"
            date = NONINT_RE.sub('-', date[:4])
            row['pubyear'] = date
            # maybe try it as a solr.DateField at some point
            #row['pubyear'] = '%s-01-01T00:00:01Z' % date
    
        audience_code = field008[22]
        if audience_code != ' ':
            try:
                row['audience'] = marc_maps.AUDIENCE_CODING_MAP[audience_code]
            except KeyError, error:
            #    sys.stderr.write("\nRecord #%s: Illegal audience code: %s\n" 
            #            % (count, error))
                row['audience'] = ''

        language_code = field008[35:38]
        if language_code != '   ':
            try:
                row['language'] = marc_maps.LANGUAGE_CODING_MAP[language_code]
            except KeyError:
                row['language'] = ''

    isbn_fields = record.get_fields('020')
    row['isbn'] = id_match(isbn_fields, ISBN_RE)
        
    upc_fields = record.get_fields('024')
    row['upc'] = id_match(upc_fields, UPC_RE)

    if record['041']:
        language_dubbed_codes = record['041'].get_subfields('a')
        languages_dubbed = get_languages(language_dubbed_codes)
        row['language_dubbed'] = []
        for language in languages_dubbed:
            if language != row['language']:
                row['language_dubbed'].append(language)
        language_subtitles_codes = record['041'].get_subfields('b')
        languages_subtitles = get_languages(language_subtitles_codes)
        if languages_subtitles:
            row['language_subtitles'] = languages_subtitles

    # are there any subfields we don't want for the full_title?
    if record['245']:
        full_title = record['245'].format_field()
        try:
            nonfiling = int(record['245'].indicator2)
        except ValueError:
            nonfiling = 0
        row['full_title'] = full_title
        title_sort = full_title[nonfiling:].strip()
        # good idea, but need to convert to unicode first
        #title_sort = unicodedata.normalize('NFKD', title_sort)
        row['title_sort'] = title_sort
        row['title'] = record['245']['a'].strip(' /:;')
    
    if record['260']:
        row['imprint'] = record['260'].format_field()
        row['publisher'] = normalize(record['260']['b'])
        # grab date from 008
        #if record['260']['c']:
        #    date_find = DATE_RE.search(record['260']['c'])
        #    if date_find:
        #        row['date'] = date_find.group()
    
    row['author'] = record.author()

    series_fields = record.get_fields('440', '490')
    row['series'] = multi_field_list(series_fields, 'a')
    
    contents_fields = record.get_fields('505')
    row['contents'] = multi_field_list(contents_fields, 'a')
    
    summary_fields = record.get_fields('520')
    row['summary'] = multi_field_list(summary_fields, 'ab')
    
    subjname_fields = record.get_fields('600')
    subjectnames = multi_field_list(subjname_fields, 'a')
    
    subjentity_fields = record.get_fields('610')
    subjectentities = multi_field_list(subjentity_fields, 'ab')
    
    subject_fields = record.subjects()
    #topics = multi_field_list(subject_fields, 'avxyz')
    #row['topic'] = [x for x in topics if 
    #        x != 'Video recordings for the hearing impaired']
    genres = []
    topics = []
    places = []
    for field in subject_fields:
        genres.extend(subfield_list(field, 'v'))
        topics.extend(subfield_list(field, 'x'))
        places.extend(subfield_list(field, 'z'))
        if field.tag == '650':
            if field['a'] != 'Video recordings for the hearing impaired.':
                topics.append(normalize(field['a']))
        elif field.tag == '651':
            places.append(normalize(field['a']))
        elif field.tag == '655':
            if field['a'] != 'Video recordings for the hearing impaired.':
                genres.append(normalize(field['a']))
        #for subfield_indicator in ('a', 'v', 'x', 'y', 'z'):
        #    more_topics = subfield_list(subfield_indicator)
        #    topics.extend(more_topics)
    row['genre'] = set(genres)
    row['topic'] = set(topics)
    row['place'] = set(places)

    personal_name_fields = record.get_fields('700')
    row['personal_name'] = []
    for field in personal_name_fields:
        subfields = field.get_subfields('a', 'b', 'c', 'd')
        personal_name = ' '.join([x.strip() for x in subfields])
        row['personal_name'].append(personal_name)

    corporate_name_fields = record.get_fields('710')
    row['corporate_name'] = []
    for field in corporate_name_fields:
        subfields = field.get_subfields('a', 'b')
        corporate_name = ' '.join([x.strip() for x in subfields])
        row['corporate_name'].append(corporate_name)

    url_fields = record.get_fields('856')
    row['url'] = multi_field_list(url_fields, 'u')

    return row

def write_csv(marc_file_handle, csv_file_handle):
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
    for fieldname in FIELDNAMES:
        fieldname_dict[fieldname] = fieldname
    #for record in reader
    count = 0
    try:
        writer = csv.DictWriter(csv_file_handle, FIELDNAMES)
        writer.writerow(fieldname_dict)
        for record in reader:
            try:
                row = get_row(record, count, ils=ILS)
                if row:  # skip when get_record returns None
                    count += 1
                    writer.writerow(row)
            except:
                sys.stderr.write("\nError in MARC record #%s (%s):\n" % (count, 
                        record.title()))
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
    usage = "usage: %prog [options] FILE_OR_URL"
    parser = optparse.OptionParser(usage=usage)
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
        record_count = write_csv(in_handle, csv_handle)
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

