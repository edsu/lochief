# Copyright 2007 Casey Durfee
# Copyright 2007 Gabriel Farrell
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

from django.conf.urls.defaults import *

urlpatterns = patterns('kochief.discovery.views',
    url(r'^$', 'index', name='discovery-index'),
    url(r'^record/(.+)$', 'record', name='discovery-record'),
    url(r'^search$', 'search', name='discovery-search'),
    
    url(r'^language/(?P<token>[\sa-zA-Z0-9:._-]+)$', 'language',
        name='language'),
    url(r'^subject/(?P<token>[\sa-zA-Z0-9:._-]+)$', 'subject',
        name='subject'),
    url(r'^personal_name/(?P<token>[\sa-zA-Z0-9:._-]+)$', 'personal_name',
        name='personal_name'),
        
        
    url(r'^unapi$', 'unapi', name='discovery-unapi'),
    #(r'^feed/atom/$', 'atomFeed'),
    #(r'^feed/rss/$', 'rssFeed'),
)
