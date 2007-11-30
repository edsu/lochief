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
    
