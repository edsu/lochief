"""Parser for http://www.slis.indiana.edu/faculty/meho/LIS-Directory/"""

import csv
from BeautifulSoup import BeautifulSoup

FIELDNAMES = [
    'id',
    'full_title',
    'personal_name',
    'url',
    'position',
    'email',
]
ID_SCHEMA = 'lf%04d'

class RowDict(dict):
    """
    A dictionary that prepares values for CSV import on get().
    """
    def get(self, key, *args):
        value = dict.get(self, key, *args)
        if not value:
            return ''
        if hasattr(value, '__iter__'):
            value = u'|'.join([x for x in value if x])
        return value.encode('utf8')

def get_row(tr):
    row = RowDict()
    td_list = tr.findAll('td')
    if td_list[0].strong or td_list[0].hr:
        return
    name, school, position, email = td_list
    name_text = name.string
    if name.a:
        website_text = name.a['href']
        row['url'] = website_text
        name_text = name.a.string
    if not name_text and name.p:
        name_text = name.p.string
    if not name_text and name.span:
        name_text = name.span.string
    name_text = name_text.replace('&nbsp;', ' ')
    name_text = name_text.replace('.', '')
    name_text = ' '.join(name_text.split())
    name_text = name_text.strip()
    row['personal_name'] = name_text
    row['full_title'] = name_text
    school_text = school.a.string
    if not school_text:
        a_list = school.findAll('a')
        school_text = a_list[1].string
    school_text = ' '.join(school_text.split())
    position_text = position.string
    if not position_text and position.p:
        position_text = position.p.string
    if not position_text:
        position_text = position.contents[0]
    position_text = ' '.join(position_text.split())
    row['position'] = '%s at %s' % (position_text, school_text)
    email_text = email.string
    if not email_text and email.span:
        email_text = email.span.string
    if not email_text and email.p:
        email_text = email.p.string
    if not email_text and email.span.span:
        email_text = email.span.span.string
    if not email_text:
        email_text = email.span.contents[-1]
    email_text = email_text.strip()
    row['email'] = email_text
    return row

def write_csv(in_handle, csv_file_handle):
    soup = BeautifulSoup(in_handle)
    tables = soup.findAll('table')
    name_tables = tables[1:]
    fieldname_dict = {}
    for fieldname in FIELDNAMES:
        fieldname_dict[fieldname] = fieldname
    count = 0
    try:
        writer = csv.DictWriter(csv_file_handle, FIELDNAMES)
        writer.writerow(fieldname_dict)
        for table in name_tables:
            tr_list = table.findAll('tr')
            for tr in tr_list:
                row = get_row(tr)
                if row:
                    count += 1
                    row['id'] = ID_SCHEMA % count
                    writer.writerow(row)
    finally:
        in_handle.close()
        csv_file_handle.close()
    return count

