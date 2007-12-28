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

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.views.decorators.vary import vary_on_headers
from config import *
import urllib, pprint, time

facetCodes = [ f['code'] for f in FACETS ]
allFacets = FACETS

def makeSearchString(q, index, limits, sort):
    if q == "*":
        q = "[* TO *]"
    ret = '%s:%s' % (index, q) 
    for limitOn in limits:
        ret = """%s AND %s""" % (ret, limitOn)
    if sort is not None and len(sort) > 0:
        ret = """%s ; %s""" % (ret, sort) 
    return iri_to_uri(urlquote(ret))

@vary_on_headers('accept-language', 'accept-encoding')
def item(request):
    start = time.time()
    context = getitemresults(request)
    
    if context == None:
        return HttpResponseRedirect("/")
    
    context['indexes'] = SEARCH_INDEXES
    context['LOCAL_LOGO_LOCATION'] = LOCAL_LOGO_LOCATION
    context['LOCAL_INSTITUTION_NAME'] = LOCAL_INSTITUTION_NAME
    # render using appropriate format
    if context['format'] and context['format'] == "py": 
        resp = HttpResponse( pprint.pformat(context) )
        resp.headers['Content-Type'] = "text/plain" ; return resp
    else:
        context['response_time'] = "%.4f" % ( time.time() - start )
        return render_to_response("item.html", context )

def getitemresults(request):
    start = time.time()
    q = request.GET.get('q', None) 
    searchString = q
    limits = []
    if not q:
        return None
    index = request.GET.get('index', 'text')
    if len( index.strip() ) == 0: 
        index = 'text'
    format = request.GET.get('format', None)
    page = int( request.GET.get('page', 0) )
    startNumZeroIndex = (ITEMS_PER_PAGE * page )
    startNum = startNumZeroIndex + 1
    limit = request.GET.get('limit', None)
    if limit is not None and len(limit.strip()) > 0:
        limits = limit.split(",,")
    else:
        limits = []
    sort = request.GET.get('sort', None)        
    searchString = makeSearchString( q, index, limits, sort)
    cacheKey = "%s~%s" % (searchString, page)
    data = cache.get( cacheKey )
    if not data:
        facetURLTerm = '&facet.field='.join(facetCodes)   
        urlToGet = "http://%s/solr/select?q=%s&wt=python&facet.field=%s&facet.zeros=false&facet=true&facet.limit=%s&start=%s" % ( SOLR_SERVER, searchString, facetURLTerm, MAX_FACET_TERMS_EXPANDED, startNumZeroIndex )
        data = urllib.urlopen( urlToGet ).read()
        cache.set( cacheKey, data, SEARCH_CACHE_TIME )
    context = eval(data)
    context['format'] = format;
    numFound = context['response']['numFound']
    endNum = min( numFound, ITEMS_PER_PAGE * (page + 1) )
    context['searchString'] = searchString
    context['q'] = q
    if limit is not None: context['currentLimit'] = limit.replace('"', '%22')
    if sort is not None: context['currentSort'] = sort
    if index is not None: context['currentIndex'] = index
    # augment item results.
    count = 0
    for itemOn in context['response']['docs']:
        itemOn['full_bib_url'] = 'http://%s/solr/select?q=bib_num:%s&version=2.2&start=0&rows=10&indent=on' % (SOLR_SERVER, "%22" + itemOn['bib_num'] + "%22")
        itemOn['count'] = count + startNum
        count += 1
        if itemOn.has_key('isbn'):
            itemOn['isbn_numeric'] = ''.join( [ x for x in itemOn['isbn'] if ( x.isdigit() or x.lower() == "x" ) ] )
        if itemOn.has_key('format'):
            formatIconURL = FORMAT_ICONS.get( itemOn['format'], None)
            if formatIconURL: itemOn['format_icon_url'] = formatIconURL
        
        #hack to put pipe delimited copy level data (location, call #, etc) into a list for each item. The list is looped through in the template
        if itemOn.has_key('copyinfo'):
            itemOn['copydetails']=[]
            for items in itemOn['copyinfo']:
                itemdetails=items.split('|')
                itemOn['copydetails'].append(itemdetails)
        
        
        #make an array out of Serials Solutions Name and URL
        if itemOn.has_key('SSdata'):
            itemOn['SSurldetails']=[]
            for items in itemOn['SSdata']:
                SSurlitemdetails=items.split('|')
                itemOn['SSurldetails'].append(SSurlitemdetails)

    return context
