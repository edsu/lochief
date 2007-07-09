from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.views.decorators.vary import vary_on_headers
from config import *
import urllib, pprint, time, re, sys, string

facetCodes = [ f['code'] for f in FACETS ]
allFacets = FACETS

@vary_on_headers('accept-language', 'accept-encoding')
def index(req):
    return render_to_response("index.html", {} )

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
def search(req):
    start = time.time()
    ctx = getsearchresults(req)
    if ctx == None:
        return HttpResponseRedirect("/catalog/")
    ctx['LOCAL_LOGO_LOCATION'] = LOCAL_LOGO_LOCATION
    ctx['LOCAL_INSTITUTION_NAME'] = LOCAL_INSTITUTION_NAME
    # render using appropriate
    
    if ctx['format'] and ctx['format'] == "py": 
        resp = HttpResponse( pprint.pformat(ctx) )
        resp.headers['Content-Type'] = "text/plain" ; return resp
    else:
        ctx['response_time'] = "%.4f" % ( time.time() - start )
        return render_to_response("search.html", ctx )

def item(req):
    start = time.time()
    ctx = getitemresults(req)
    
    if ctx == None:
        return HttpResponseRedirect("/catalog/")
    
    ctx['LOCAL_LOGO_LOCATION'] = LOCAL_LOGO_LOCATION
    ctx['LOCAL_INSTITUTION_NAME'] = LOCAL_INSTITUTION_NAME
    # render using appropriate format
    if ctx['format'] and ctx['format'] == "py": 
        resp = HttpResponse( pprint.pformat(ctx) )
        resp.headers['Content-Type'] = "text/plain" ; return resp
    else:
        ctx['response_time'] = "%.4f" % ( time.time() - start )
        return render_to_response("item.html", ctx )

def feedCreator(ctx, feed):
    """Generates the list of items for the syndication feed for shared searches.
    
    Returns an XML string."""

    for itemOn in ctx['response']['docs']:
    	author = u""
        desc = u""
	title = u""

	if itemOn.has_key('title'):
            title = itemOn['title']

	if itemOn.has_key('author'):
            author = " / ".join(itemOn['author'])

    	if itemOn.has_key('summary'):
	    desc = " / ".join(itemOn['summary'])
	elif itemOn.has_key('contents'):
	    desc = " / ".join(itemOn['contents'])
	elif itemOn.has_key('topic'):
	    desc = " / ".join(itemOn['topic'])
    	feed.add_item(title, itemOn['full_bib_url'], desc, None, author)
    return HttpResponse(feed.writeString('utf8'))

def atomFeed(req):
    """Generates an Atom syndication feed for shared searches.
    
    Returns an XML string."""
    ctx = getsearchresults(req)
    feed = Atom1Feed(_('Search: ') + ctx['q'], u'/catalog/feed/atom/', _('Fac-Back-OPAC Search in Atom syndication'))
    return feedCreator(ctx, feed)

   
def rssFeed(req):
    """Generates an RSS2 syndication feed for shared searches.
    
    Returns an XML string."""
    ctx = getsearchresults(req)
    feed = Rss201rev2Feed(_('Search: ') + ctx['q'], u'/catalog/feed/rss/', _('Fac-Back-OPAC Search in RSS2 syndication'))
    return feedCreator(ctx, feed)

def getsearchresults(req): 
    q = req.GET.get('q', None)
    
    searchString = q
    limits = []
    if not q:
        return None
    index = req.GET.get('index', 'text')
    if len( index.strip() ) == 0: 
        index = 'text'
    format = req.GET.get('format', None)
    page = int( req.GET.get('page', 0) )
    startNumZeroIndex = (ITEMS_PER_PAGE * page )
    startNum = startNumZeroIndex + 1
    limit = req.GET.get('limit', None)
    browserange = req.GET.get('browserange', None)
    if limit is not None and len(limit.strip()) > 0:
        limits = limit.split(",,")
    else:
        limits = []
    
        
    sort = req.GET.get('sort', None)        
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
        
        data = urllib.urlopen( urlToGet ).read()
        cache.set( cacheKey, data, SEARCH_CACHE_TIME )
    ctx = eval(data) 
    ctx['format'] = format;
    ctx['limit']=limits
    ctx['searchstring']=searchString
    ctx['get'] = req.META['QUERY_STRING']
    numFound = ctx['response']['numFound']
    endNum = min( numFound, ITEMS_PER_PAGE * (page + 1) )
    ctx['q'] = q
    if limit is not None: ctx['currentLimit'] = limit.replace('"', '%22')
    if sort is not None: ctx['currentSort'] = sort
    if index is not None: ctx['currentIndex'] = index
    
    # augment item results.
    count = 0
    for itemOn in ctx['response']['docs']:
        itemOn['count'] = count + startNum
        count += 1
        
        #call number display

        if LOCAL_ITEM_DISPLAY == 1:
             # use the local facbackopac view   
            if itemOn.has_key('bib_num'):
                itemOn['full_bib_url'] = '/catalog/item/?q=%s&index=bib_num' % ('%22' + itemOn['bib_num'] + '%22')
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
    facetCounts = ctx['facet_counts']
    del ctx['facet_counts']
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
            
                    
    ctx['facets']  = _facets
    ctx['indexes'] = SEARCH_INDEXES
    ctx['startNum'] = startNum
    ctx['endNum'] = endNum
    _sorts = SORTS
    for sortOn in _sorts:
        sortOn['selected'] = ( sort == "%s %s" % ( sortOn['field'], sortOn['direction']) )
    ctx['sorts'] = _sorts
    ctx['pagination'] = doPagination( page, numFound, ITEMS_PER_PAGE)
    # put together "remove your limit" options
    if limits:
        _removeOptions = []
        for limitOn in limits:
            allOtherLimits = ",,".join( [x for x in limits if x != limitOn] )
            _removeOptions.append( { 'label' : limitOn.replace('"', ''), 'new_limit' : allOtherLimits} )
        ctx['removeLimits'] = _removeOptions
    return ctx

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


def getitemresults(req):
    start = time.time()
    q = req.GET.get('q', None) 
    searchString = q
    limits = []
    if not q:
        return None
    index = req.GET.get('index', 'text')
    if len( index.strip() ) == 0: 
        index = 'text'
    format = req.GET.get('format', None)
    page = int( req.GET.get('page', 0) )
    startNumZeroIndex = (ITEMS_PER_PAGE * page )
    startNum = startNumZeroIndex + 1
    limit = req.GET.get('limit', None)
    if limit is not None and len(limit.strip()) > 0:
        limits = limit.split(",,")
    else:
        limits = []
    sort = req.GET.get('sort', None)        
    searchString = makeSearchString( q, index, limits, sort)
    cacheKey = "%s~%s" % (searchString, page)
    data = cache.get( cacheKey )
    if not data:
        facetURLTerm = '&facet.field='.join(facetCodes)   
        urlToGet = "http://%s/solr/select?q=%s&wt=python&facet.field=%s&facet.zeros=false&facet=true&facet.limit=%s&start=%s" % ( SOLR_SERVER, searchString, facetURLTerm, MAX_FACET_TERMS_EXPANDED, startNumZeroIndex )
        data = urllib.urlopen( urlToGet ).read()
        cache.set( cacheKey, data, SEARCH_CACHE_TIME )
    ctx = eval(data)
    ctx['format'] = format;
    numFound = ctx['response']['numFound']
    endNum = min( numFound, ITEMS_PER_PAGE * (page + 1) )
    ctx['searchString'] = searchString
    ctx['q'] = q
    if limit is not None: ctx['currentLimit'] = limit.replace('"', '%22')
    if sort is not None: ctx['currentSort'] = sort
    if index is not None: ctx['currentIndex'] = index
    # augment item results.
    count = 0
    for itemOn in ctx['response']['docs']:
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

    return ctx
