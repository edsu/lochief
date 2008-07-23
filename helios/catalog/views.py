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

import urllib, pprint, time

from django.core.cache import cache
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.template.loader import get_template
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.views.decorators.vary import vary_on_headers
from django.conf import settings

from helios.discovery.views import get_solr_response

from config import *

facetCodes = [ f['code'] for f in FACETS ]
allFacets = FACETS

@vary_on_headers('accept-language', 'accept-encoding')
def record(request, record_id):
    context = RequestContext(request)
    id_query = 'id:%s' % record_id
    params = [
        ('q.alt', '*:*'),
        ('fq', id_query.encode('utf8')),
    ]
    solr_url, solr_response = get_solr_response(params)
    try:
        doc = solr_response['response']['docs'][0]
    except IndexError:
        raise Http404
    context['doc'] = doc
    if settings.DEBUG: 
        context['solr_url'] = solr_url
    template = get_template('catalog/record.html')
    return HttpResponse(template.render(context))

