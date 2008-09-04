# Copyright 2008 Gabriel Sean Farrell
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

from django.utils import simplejson
import optparse
import urllib

# needed for django environment -- helios imports are local
from django.core.management import setup_environ
from helios import settings
setup_environ(settings)

from django.contrib.auth.models import User
from helios.cataloging import models

if __name__ == '__main__':
    usage = "usage: %prog [options] FILE_OR_URL"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-p', '--parsing_module', dest='parsing_module', 
        metavar='PARSING_MODULE', 
        help='use PARSING_MODULE (relative path to the module) to parse FILE_OR_URL and convert to CSV')
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
    else:
        file_or_url = args[0]
        in_handle = urllib.urlopen(file_or_url)
        committer = User.objects.get(id=2)
        if options.parsing_module:
            mod_path = options.parsing_module
            if mod_path.endswith('.py'):
                mod_path = mod_path[:-3]
            module = __import__(mod_path)
            count = 0
            for record in module.record_generator(in_handle):
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
