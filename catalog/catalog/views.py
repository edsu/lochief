from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.views.decorators.vary import vary_on_headers
from config import *
import urllib, pprint, time, re

facetCodes = [ f['code'] for f in FACETS ]
allFacets = FACETS

@vary_on_headers('accept-language', 'accept-encoding')
def index(req):
    return render_to_response("index.html", {} )

def makeSearchString(q, index, limits, sort):
    ret = '%s:%s' % (index, q) 
    for limitOn in limits:
        ret = """%s AND %s""" % (ret, limitOn)
    if sort is not None and len(sort) > 0:
        ret = """%s ; %s""" % (ret, sort) 
    return urllib.quote( ret )     # the quote() function is crucial to allow Unicode to work in URLs

@vary_on_headers('accept-language', 'accept-encoding')
def search(req):
    start = time.time()
    ctx = getResults(req)
    # render using appropriate format
    if ctx['format'] and ctx['format'] == "py": 
        resp = HttpResponse( pprint.pformat(ctx) )
        resp.headers['Content-Type'] = "text/plain" ; return resp
    else:
        ctx['response_time'] = "%.4f" % ( time.time() - start )
        return render_to_response("search.html", ctx )

def getResults(req): 
    q = req.GET.get('q', None) 
    searchString = q
    limits = []
    if not q:
        return HttpResponseRedirect("/catalog/")
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
    print ctx
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
        itemOn['count'] = count + startNum
        count += 1
        # Every item that we export, by definition, has a bib_num... but the
        # field might not be indexed in the proprietary ILS

        # {ckey} is the field to search for the catalog key in Unicorn
        ckey = re.compile('\s(.*)$')
        bib_num = ckey.search(itemOn['bib_num']).group(1)
        itemOn['full_bib_url'] = OPAC_FULL_BIB_URL % (bib_num, "ckey")

        # Another ILS may have to use a different field, such as the ones below
        # Uncomment the one(s) that works for your ILS
        if itemOn.has_key('isbn'):
            itemOn['isbn_numeric'] = ''.join( [ x for x in itemOn['isbn'] if ( x.isdigit() or x.lower() == "x" ) ] )
            # itemOn['full_bib_url'] = OPAC_FULL_BIB_URL % (itemOn['isbn_numeric'], "020")
        # 001 field is our best match option
        if itemOn.has_key('ctrl_num'):
            # itemOn['full_bib_url'] = OPAC_FULL_BIB_URL % (itemOn['ctrl_num'], "001")
            pass

        # Add the media format icons
        if itemOn.has_key('format'):
            formatIconURL = FORMAT_ICONS.get( itemOn['format'], None)
            if formatIconURL: itemOn['format_icon_url'] = formatIconURL
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
            for i in range(len(terms)):
                _facetOnTerms.append( dict( term=terms[i], count=counts[i]) )   
            if len( _facetOnTerms ) > MAX_FACET_TERMS_BASIC:
                facetOn['has_more'] = True
                facetOn['terms'] , facetOn['extended_terms'] = _facetOnTerms[:MAX_FACET_TERMS_BASIC], _facetOnTerms[MAX_FACET_TERMS_BASIC: ]
            else:
                facetOn['terms'] = _facetOnTerms 
        _facets.append( facetOn )
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
