#   Copyright 2007 Casey Durfee
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from django.utils.translation import ugettext as _

SOLR_SERVER = "localhost:8983"
SEARCH_CACHE_TIME = 6000    # in seconds
ITEMS_PER_PAGE = 10
MAX_FACET_TERMS_BASIC = 4    # how many facet terms display by default
MAX_FACET_TERMS_EXPANDED = 25 # how many facet terms display when you hit "show more"
LOCAL_LOGO_LOCATION = 'http://www.laurentian.ca/Laurentian.WCMSPortal/Inc/images/logo_laurentian.jpg' #image with 177 x 54 pixels
LOCAL_INSTITUTION_NAME = 'University Library:'
# Horizon IPAC example
#OPAC_FULL_BIB_URL = "http://catalog.spl.org/ipac20/ipac.jsp?index=BIB&term=%(bib_num)s"
# Unicorn iBistro / iLink example
OPAC_FULL_BIB_URL = "http://sirsiweb.laurentian.ca/uhtbin/cgisirsi/x/x/x/57/5/?user_id=WEBSERVER&searchdata1=%s{%s}"
# LOCAL_ITEM_DISPLAY has two settings:
# 0 : Make item title a link to the detailed view in vendor catalog
# 1 : Make item title a link to the detailed view in fac-back-opac
LOCAL_ITEM_DISPLAY = 1

#FACETS has several settings.
#name = Display name on the opac
#code = solr field name
#sortbycount = whether you want the facets sorted by count. Values can be true, false, and reverse (for reverse alphabetical order)
#facetlocation =  can be used to display facets in different areas of the screen, as determined by your template. Was originally made to put dewey/lc callnum ranges on top of screen like NCSU
FACETS = [    { 'name' : _('Dewey Range'), 'code' : 'callnumlayerone', 'sortbycount' : 'false' , 'facetlocation' : 'sidebar'},
              { 'name' : _('Dewey Range'), 'code' : 'callnumlayertwo', 'sortbycount' : 'false' , 'facetlocation' : 'sidebar'}, 
              { 'name' : _('Topic'), 'code' : 'topic', 'sortbycount' : 'true', 'facetlocation' : 'sidebar' },    
              { 'name' : _('Genre'), 'code' : 'genre', 'sortbycount' : 'true' , 'facetlocation' : 'sidebar'},                            
              { 'name' : _('Format'), 'code' : 'format', 'sortbycount' : 'true', 'facetlocation' : 'sidebar' },                         
              { 'name' : _('Region'), 'code' : 'place' , 'sortbycount' : 'true', 'facetlocation' : 'sidebar'},    
              { 'name' : _('Language'), 'code' : 'language', 'sortbycount' : 'true' , 'facetlocation' : 'sidebar'}, 
              { 'name' : _('Author'), 'code' : 'author_exact','sortbycount' : 'false' , 'facetlocation' : 'sidebar' },
              { 'name' : _('Publication Date'), 'code' : 'pubdaterange', 'sortbycount' : 'reverse', 'facetlocation' : 'sidebar' },
              { 'name' : _('Availability'), 'code' : 'availability', 'sortbycount' : 'false' , 'facetlocation' : 'sidebar'},
              ]

#items listed in the search dropdown box
SEARCH_INDEXES = [ {'name' : _('Anywhere'), 'index': 'text'},
                  {'name' : _('Author'), 'index': 'author'} , { 'name' : _('Title'), 'index' : 'title' },
                  {'name' : _('Subject'), 'index': 'subject'}, { 'name' : _('ISBN'), 'index' : 'isbn' },]

#items to be listed in the "Sort By:" Dropdown box
SORTS = [{ 'name' : _('Pub. Date (newest first)'), 'direction' : 'desc', 'field' : 'pubdate' },
         { 'name' : _('Pub. Date (oldest first)'), 'direction' : 'asc', 'field' : 'pubdate' },
         { 'name' : _('Author A-Z'), 'direction' : 'desc', 'field' : 'author_exact' },]

#Icons corresponding to item type
FORMAT_ICONS = { 'eAudio' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-eaudio.gif" alt="eAudio" />',
                    'eBook' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-ebook.gif" alt="eBook" />',
                    'CD-ROM' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-cdrom.gif" alt="cd rom" />',
                    'Book On Cassette' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-bt.gif" alt="book on cassette" />',
                    'Book On CD' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-bkcd.gif" alt="book on CD" />',
                    'Cassette' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-audio.gif" alt="cassette" />',
                    'Music CD' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-cd.gif" alt="music cd" />',
                    'Phono Record' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-record.gif" alt="phono record" />',
                    'DVD' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-dvd.gif" alt="dvd" />',
                    'Videocassette' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-video.gif" alt="videocassette" />',
                    'Large Print Book' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-largeprint.gif" alt="large print book" />',
                    'Book' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-book.gif" alt="book" />',
                    'Journal' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-magazine.gif" alt="magazine" />',
                    'Map' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-map.gif" alt="map" />',
                    'Musical Score' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-score.gif" alt="musical score" />',
                    'Digital Music' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-digimusic.gif" alt="digital music" />',}
