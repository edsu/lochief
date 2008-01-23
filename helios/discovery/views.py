# Copyright 2007 Casey Durfee
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
import pprint
import time
import re
import sys
import string

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.vary import vary_on_headers
from django.shortcuts import render_to_response
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.core.cache import cache
from django.template import RequestContext

from config import ITEMS_PER_PAGE, FACETS, SOLR_SERVER, MAX_FACET_TERMS_EXPANDED, SEARCH_CACHE_TIME, MAX_FACET_TERMS_BASIC, SEARCH_INDEXES, SORTS, LOCAL_LOGO_LOCATION, LOCAL_INSTITUTION_NAME, LOCAL_ITEM_DISPLAY, FORMAT_ICONS

facetCodes = [ f['code'] for f in FACETS ]
allFacets = FACETS

@vary_on_headers('accept-language', 'accept-encoding')
def index(request):
    context = {}
    context['LOCAL_LOGO_LOCATION'] = LOCAL_LOGO_LOCATION
    return render_to_response('index.html', context, 
            context_instance=RequestContext(request))

@vary_on_headers('accept-language', 'accept-encoding')
def search(request):
    start = time.time()
    context = getsearchresults(request)
    if context == None:
        return HttpResponseRedirect("/")
    context['LOCAL_LOGO_LOCATION'] = LOCAL_LOGO_LOCATION
    context['LOCAL_INSTITUTION_NAME'] = LOCAL_INSTITUTION_NAME
    # render using appropriate
    
    if context['format'] and context['format'] == "py": 
        resp = HttpResponse( pprint.pformat(context) )
        resp.headers['Content-Type'] = "text/plain" ; return resp
    else:
        context['response_time'] = "%.4f" % ( time.time() - start )
        return render_to_response("search.html", context,
                context_instance=RequestContext(request))

def makeSearchString(q, index, limits, sort):
    if q == "*":
        q = "[* TO *]"
    ret = '%s:%s' % (index, q) 
    for limitOn in limits:
        ret = """%s AND %s""" % (ret, limitOn)
    if sort is not None and len(sort) > 0:
        ret = """%s ; %s""" % (ret, sort) 
    return iri_to_uri(urlquote(ret))

def getsearchresults(request): 
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
    browserange = request.GET.get('browserange', None)
    if limit is not None and len(limit.strip()) > 0:
        limits = limit.split(",,")
    else:
        limits = []
    
        
    sort = request.GET.get('sort', None)        
    searchString = makeSearchString( q, index, limits, sort)
    cacheKey = "%s~%s" % (searchString, page)
    data = cache.get( cacheKey )
    if not data:
        #sort facets by name vs count as per the config.py file        
        facetsortTerm = ''
        for f in FACETS:
            if f['sortbycount'] == 'false':
                facetsortTerm = facetsortTerm + '&f.%s.facet.sort=%s' % (f['code'], f['sortbycount'])
        # end sort facets by name
        facetURLTerm = '&facet.field='.join(facetCodes)   
        urlToGet = "http://%s/solr/select?q=%s&wt=python&facet.field=%s%s&facet.zeros=false&facet=true&facet.limit=%s&start=%s" % ( SOLR_SERVER, searchString, facetURLTerm, facetsortTerm, MAX_FACET_TERMS_EXPANDED, startNumZeroIndex )
        
        try:
            data = urllib.urlopen( urlToGet ).read()
        except IOError:
            raise IOError, 'Unable to connect to the Solr instance.'
        cache.set( cacheKey, data, SEARCH_CACHE_TIME )
    context = eval(data) 
    context['format'] = format;
    context['limit']=limits
    context['searchstring']=searchString
    context['get'] = request.META['QUERY_STRING']
    numFound = context['response']['numFound']
    endNum = min( numFound, ITEMS_PER_PAGE * (page + 1) )
    context['q'] = q
    if limit is not None: context['currentLimit'] = limit.replace('"', '%22')
    if sort is not None: context['currentSort'] = sort
    if index is not None: context['currentIndex'] = index
    
    # augment item results.
    count = 0
    for itemOn in context['response']['docs']:
        itemOn['count'] = count + startNum
        count += 1
        
        #call number display

        if LOCAL_ITEM_DISPLAY == 1:
             # use the local facbackopac view   
            if itemOn.has_key('bib_num'):
                itemOn['full_bib_url'] = '/catalog/?q=%s&index=bib_num' % ('%22' + itemOn['bib_num'] + '%22')
                # Add the media format icons
                if itemOn.has_key('format'):
                    formatIconURL = FORMAT_ICONS.get( itemOn['format'], None)
                    if formatIconURL: itemOn['format_icon_url'] = formatIconURL
        else:
            # Every item that we export, by definition, has a bib_num... but the
            # field might not be indexed in the proprietary ILS

            # {ckey} is the field to search for the catalog key in Unicorn
            ckey = re.compile('\s(.*)$')
            bib_num = ckey.search(itemOn['bib_num']).group(1)
            itemOn['full_bib_url'] = OPAC_FULL_BIB_URL % (bib_num, "ckey")

            # Another ILS may have to use a different field, such as the ones below
            # Uncomment the one(s) that works for your ILS
            # itemOn['full_bib_url'] = OPAC_FULL_BIB_URL % (itemOn['isbn_numeric'], "020")

            #if itemOn.has_key('ctrl_num'):
            # itemOn['full_bib_url'] = OPAC_FULL_BIB_URL % (itemOn['ctrl_num'], "001")
            
            # Add the media format icons
            if itemOn.has_key('format'):
                    formatIconURL = FORMAT_ICONS.get( itemOn['format'], None)
                    if formatIconURL: itemOn['format_icon_url'] = formatIconURL
        #needed for amazon book covers and isbn to be displayable
        if itemOn.has_key('isbn'):
            itemOn['isbn_numeric'] = ''.join( [ x for x in itemOn['isbn'] if ( x.isdigit() or x.lower() == "x" ) ] )
        #make an array out of Serials Solutions Name and URL
        if itemOn.has_key('SSdata'):
            itemOn['SSurldetails']=[]
            for items in itemOn['SSdata']:
                SSurlitemdetails=items.split('|')
                itemOn['SSurldetails'].append(SSurlitemdetails)
                

            
    # re-majigger facets 
    facetCounts = context['facet_counts']
    del context['facet_counts']
    _facets = []   

    for facetCodeOn in allFacets:
        facetOn = {'terms' : [], 'extended_terms' : [], 'code' : facetCodeOn['code'], 'name' : facetCodeOn['name'], 'has_more' : False }
        if facetCounts['facet_fields'].has_key( facetCodeOn['code'] ):        
            facetCountList = facetCounts['facet_fields'][facetCodeOn['code'] ]    # this is a list of alternating facets/counts
            terms, counts = facetCountList[::2], facetCountList[1::2]
            _facetOnTerms = []
            #if the config files specifies a reverse sort, it sorts the dictionary in reverse aalphabetical order                
            if facetCodeOn['sortbycount'] == 'reverse':
                tempdict = {}
                reverseterms = []
                for i in range(len(terms)):
                    tempdict[terms[i]] = counts[i]
                reverseterms=reversesortDictValues(tempdict)
                if reverseterms:
                    for i in range(len(reverseterms)):
                        tmp = reverseterms[i]
                        _facetOnTerms.append( dict( term=reverseterms[i], count=tempdict[tmp]) )
            else:
                for i in range(len(terms)):
                    _facetOnTerms.append( dict( term=terms[i], count=counts[i]) )
            if len( _facetOnTerms ) > MAX_FACET_TERMS_BASIC:
                facetOn['has_more'] = True
                facetOn['terms'] , facetOn['extended_terms'] = _facetOnTerms[:MAX_FACET_TERMS_BASIC], _facetOnTerms[MAX_FACET_TERMS_BASIC: ]
            else:
                facetOn['terms'] = _facetOnTerms
            facetOn['allterms'] = _facetOnTerms
            facetOn['facetlocation'] = facetCodeOn['facetlocation']
            _facets.append( facetOn )
        
    #find out if callnumlayerone is a limit and remove it from the facets 
    #dictionary if it is so that only callnumlayer2 is displayed (i.e. if 
    #100's dewey is limited, display the 10's)
    callnumlayeronefound = 0
    callnumlayertwofound = 0
    if limits:
        for limitOn in limits:
            if limitOn[:15] == 'callnumlayerone':
                callnumlayeronefound = 1
        for limitOn in limits:
            if limitOn[:15] == 'callnumlayertwo':
                callnumlayertwofound = 1
    #if callnumlayerone was not found to be a limit, remove 
    #callnumlayertwo so that only callnumlayerone displays 
    #(ie, show the 100's dewey only instead of 100's and 10's)
    if callnumlayeronefound == 1 or (callnumlayeronefound == 0 and callnumlayertwofound == 1): 
        count = 0
        for f in _facets:
            if f['code'] == 'callnumlayerone':
                del _facets[count]
                break
            count += 1
    
    if callnumlayeronefound == 0 or (callnumlayeronefound == 1 and callnumlayertwofound == 1): 
        count = 0
        for f in _facets:
            if f['code'] == 'callnumlayertwo':
                del _facets[count]
                break
            count += 1
            
                    
    context['facets']  = _facets
    context['indexes'] = SEARCH_INDEXES
    context['startNum'] = startNum
    context['endNum'] = endNum
    _sorts = SORTS
    for sortOn in _sorts:
        sortOn['selected'] = ( sort == "%s %s" % ( sortOn['field'], sortOn['direction']) )
    context['sorts'] = _sorts
    context['pagination'] = doPagination( page, numFound, ITEMS_PER_PAGE)
    # put together "remove your limit" options
    if limits:
        _removeOptions = []
        for limitOn in limits:
            allOtherLimits = ",,".join( [x for x in limits if x != limitOn] )
            _removeOptions.append( { 'label' : limitOn.replace('"', ''), 'new_limit' : allOtherLimits} )
        context['removeLimits'] = _removeOptions
    return context

def reversesortDictValues(adict):
    #sorts dictionary keys in reverse alphabetical order. Done differently before pythin 2.4 hence
    #the version checks
    if sys.version_info[0] >= 2 and sys.version_info[1] >= 4:
        items = adict.keys()
        items.sort(reverse=True)
        return items
    else:
        items = adict.keys()
        items.sort
        items.reverse()
        return items
    

def doPagination( page, totalFound, numPerPage ):
    ret = []
    startNum = (page * numPerPage) + 1
    endNum = (page + 1) * numPerPage
    if page < 5:
        startPage = 0
    else:
        startPage = page - 5
    if totalFound % numPerPage:    
        lastPage = (totalFound // numPerPage) + 1
    else:
        lastPage = (totalFound // numPerPage)
    endPage = min( lastPage, page + 5)
    for i in range( startPage, endPage):
        ret.append( { 'selected' : (i == page) , 'start' : ( i * numPerPage) + 1, 'end' : min( totalFound, ( i + 1) * numPerPage), 'page' : i, 'pageLabel' : i+1 } )
    return {'pages' : ret , 'hasPrevious' : (page > 0), 'hasNext' : page < ( lastPage - 1 ), 'previousPage' : page-1, 'nextPage' : page+1 }

