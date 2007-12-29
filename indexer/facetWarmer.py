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

# facetWarmer warms up the facets by doing huge honkin' searches to populate the filterCache.

import urllib, time, sys
from loadPropsFile import *

indexerConfig = loadPropsFile("config/indexer.properties")

SOLR_SERVER = indexerConfig.get("SOLR_QUERY_URL")
WARMUP_QUERY = indexerConfig.get("WARMUP_QUERY")

_facets = indexerConfig.get("FACETS_TO_DO")
FACETS_TO_DO = _facets.split(",")


def warmFacets( server=SOLR_SERVER, warmupQuery=WARMUP_QUERY, facets =FACETS_TO_DO ):
    # 1. first we try and hit all records in the DB
    query = "%s?%s&fl=*&wt=python" % (server, warmupQuery )
    u= urllib.urlopen( query )
    data = u.read()
    u.close()
    # 2. now do a query on each facet parameter
    for facetOn in facets:
        query = "%s?%s&wt=python&facet=true&facet.field=%s&facet.zeros=true&rows=0&facet.limit=-1" % (server, warmupQuery, facetOn)
        start = time.time()
        u = urllib.urlopen( query )
        data = u.read()
        u.close()
        print "query on facet %s took %.4f" % (facetOn, time.time() - start)
        #print "\n%s\n" % query

if __name__ == '__main__':
    if len(sys.argv) > 1:
        server = sys.argv[1]
    else:
        server = SOLR_SERVER
    warmFacets( server, WARMUP_QUERY, FACETS_TO_DO )
    print "done!"
    
