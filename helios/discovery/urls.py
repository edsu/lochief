# Copyright 2007 Casey Durfee
# Copyright 2007 Gabriel Farrell
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

from django.conf.urls.defaults import *

urlpatterns = patterns('helios.discovery.views',
    url(r'^$', 'index', name='discovery-index'),
    url(r'^record/(.+)$', 'record', name='discovery-record'),
    url(r'^search$', 'search', name='discovery-search'),
    url(r'^unapi$', 'unapi', name='discovery-unapi'),
    #(r'^feed/atom/$', 'atomFeed'),
    #(r'^feed/rss/$', 'rssFeed'),
)
