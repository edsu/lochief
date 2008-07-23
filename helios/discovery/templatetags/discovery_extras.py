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

import urllib

from django.template import Library
from django.utils.translation import ugettext as _

register = Library()

def title_link(context):
    new_context = {}
    new_context['record_url'] = context['doc']['record_url']
    try:
        full_title = context['doc']['full_title']
    except KeyError:
        full_title = _('Untitled')
    try:
        short_title = context['doc']['title']
    except KeyError:
        short_title = full_title
    new_context['short_title'] = short_title
    rest_of_title = full_title.replace(short_title, '', 1)
    new_context['rest_of_title'] = rest_of_title
    return new_context
register.inclusion_tag('discovery/snippets/result_title.html', 
        takes_context=True)(title_link)

def add_sort(context, sort_type):
    params = []
    query = context['query']
    if query:
        params.append(('q', query.encode('utf8')))
    limits_param = context['limits_param']
    if limits_param:
        params.append(('limits', limits_param.encode('utf8')))
    params.append(('sort', sort_type.encode('utf8')))
    return {'urlparams': urllib.urlencode(params)}
register.inclusion_tag('discovery/snippets/search_url.html', 
        takes_context=True)(add_sort)

def pagination_url(context, page):
    params = []
    query = context['query']
    if query:
        params.append(('q', query.encode('utf8')))
    limits_param = context['limits_param']
    if limits_param:
        params.append(('limits', limits_param.encode('utf8')))
    params.append(('sort', context['current_sort'].encode('utf8')))
    if page != 1:
        params.append(('page', page))
    return {'urlparams': urllib.urlencode(params)}
register.inclusion_tag('discovery/snippets/search_url.html', 
        takes_context=True)(pagination_url)

def new_limit(context, field, field_query):
    params = []
    limit = u'%s:"%s"' % (field, field_query)
    params.append(('limits', limit.encode('utf8')))
    return {'urlparams': urllib.urlencode(params)}
register.inclusion_tag('discovery/snippets/search_url.html', 
        takes_context=True)(new_limit)

def add_limit(context, field, field_query):
    params = []
    query = context['query']
    if query:
        params.append(('q', query.encode('utf8')))
    limits_param = context['limits_param']
    limit = u'%s:"%s"' % (field, field_query)
    limits = ' '.join((limits_param, limit))
    params.append(('limits', limits.encode('utf8')))
    params.append(('sort', context['current_sort'].encode('utf8')))
    return {'urlparams': urllib.urlencode(params)}
register.inclusion_tag('discovery/snippets/search_url.html', 
        takes_context=True)(add_limit)

def remove_limit(context):
    params = []
    query = context['query']
    if query:
        params.append(('q', query.encode('utf8')))
    current_limits = context['limits']
    this_limit = context['limit']
    limits = ' '.join([x for x in current_limits if x != this_limit])
    if limits:
        params.append(('limits', limits.encode('utf8')))
    return {'urlparams': urllib.urlencode(params)}
register.inclusion_tag('discovery/snippets/search_url.html', 
        takes_context=True)(remove_limit)

