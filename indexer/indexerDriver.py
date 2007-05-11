## indexes records from solr
from java.io import *
from java.net import *
from org.marc4j import *
from org.marc4j.converter.impl import *
import time, sys, urllib

from indexer import *
from loadPropsFile import *

indexerConfig = loadPropsFile("config/indexer.properties")

SOLR_COMMIT_MESSAGE = indexerConfig.get( "SOLR_COMMIT_MESSAGE" )
SOLR_OPTIMIZE_MESSAGE = indexerConfig.get( "SOLR_OPTIMIZE_MESSAGE" )
SOLR_DELETE_ID_MESSAGE = indexerConfig.get("SOLR_DELETE_ID_MESSAGE" )
SOLR_BASE_URL = indexerConfig.get("SOLR_BASE_URL", "http://localhost:8888/solr" ) 
SOLR_UPDATE_URL = indexerConfig.get( "SOLR_UPDATE_URL" )
SOLR_QUERY_URL = indexerConfig.get( "SOLR_QUERY_URL" ) 
MAX_RECORDS_TO_ADD = indexerConfig.get("MAX_RECORDS_TO_ADD")
RECORDS_TO_SKIP = indexerConfig.get("RECORDS_TO_SKIP")
SOLR_INDEX_BATCH_SIZE = indexerConfig.get("SOLR_INDEX_BATCH_SIZE")
SOLR_COMMIT_BATCH_SIZE = indexerConfig.get("SOLR_COMMIT_BATCH_SIZE")
PRINT_SOLR_POST_DATA = indexerConfig.get("PRINT_SOLR_POST_DATA")
PRINT_SOLR_RESP_DATA = indexerConfig.get("PRINT_SOLR_RESP_DATA")
PROFILE = indexerConfig.get("PROFILE") 
DO_ACCESSION = indexerConfig.get("DO_ACCESSION") ## currently not used!

def postURL( url, data, contentType="""text/xml; charset="utf-8" """ ):
    """POSTs data to URL using utf-8"""
    u = URL( url )
    hu = u.openConnection()
    hu.setFollowRedirects(1)
    hu.setDoOutput(1)
    hu.setRequestMethod("POST")
    hu.setRequestProperty("Content-Type", contentType )
    osw = OutputStreamWriter( hu.getOutputStream(), "UTF8")
    osw.write( data )
    osw.flush()
    osw.close()
    lineOn = ""
    ret = ""
    try:
        br = BufferedReader( InputStreamReader( hu.getInputStream() ) )
	while lineOn is not None:
	    ret += lineOn
	    lineOn = br.readLine()
    except:
        print "Post failed for following record:\n%s" % data
    return ret

def optimize(url =SOLR_UPDATE_URL):
    postURL( url, SOLR_OPTIMIZE_MESSAGE )

def commit( url = SOLR_UPDATE_URL ):
    postURL( url, SOLR_COMMIT_MESSAGE )

def deleteRecord( recordID, url = SOLR_UPDATE_URL):
    postURL( url, SOLR_DELETE_ID_MESSAGE % locals() )

def processFile( filename, anselUnicodeConverter = None ):
    inStream = FileInputStream(filename)
    print "processing file <<%s>>" % filename
    marcReader = MarcStreamReader( inStream )
    data = ""
    count = 0
    lastCommitTime = None
    import time
    startTime = time.time()
    lastRecord = None
    m4j = None
    marcReaderTime = 0
    marcRecordToDictTime = 0
    extractorCreateTime = 0
    extractionTime = 0
    marcRecordForSolrTime = 0
    commitTime = 0
    updateTime = 0
    marcSerializeTime = 0
    
    indexesConfig = loadPropsFile("config/indexes.properties")
    
    accession = 0   # TODO: try and load pickled accession # from somewhere
    serializedRecord = None
    while marcReader.hasNext() and count < MAX_RECORDS_TO_ADD:
        print ".",
        accession += 1  
        count += 1
        try:
            mrTimeStart = time.time()                
            marc4jRecord = marcReader.next()
            marcReaderTime += ( time.time() - mrTimeStart )                
        except:
            print "last record indexed was %s " % serializedRecord
            import sys
            print "sys.exc_info is %s" % str(sys.exc_info())
            try:
                marc4jRecord = marcReader.next()    # unlikely to work but what the hey
            except:
                print "tried parsing again and failed. The lesson is, never try."
                sys.exit(1)
        mrsTime = time.time()
        if count < RECORDS_TO_SKIP:
            continue
        rec = recordForSolr( marc4jRecord, anselUnicodeConverter, config = indexesConfig )
        marcRecordForSolrTime += ( time.time() - mrsTime )
        extractionTime += rec._extractionTime
        extractorCreateTime += rec._extractorCreateTime
        marcRecordToDictTime += rec._marcRecordToDictTime
        mrserTime = time.time()            
        serializedRecord = rec.serialize()
        marcSerializeTime += ( time.time() - mrserTime )
        data += serializedRecord
            
        if( (count % SOLR_INDEX_BATCH_SIZE ) == 0):
           # nb. neither apache commons nor python urllib works right here!  Unicode gets mangled.  Must use postURL
            startUpdateTime = time.time()
            resp = postURL( SOLR_UPDATE_URL, "<add>%s</add>" % data)
            # TODO: put in retry/continue code here for failed updates/slowdowns on Solr
            updateTime += ( time.time() - startUpdateTime )
            print "*",
            if PRINT_SOLR_POST_DATA:
                print "\n\n<add>%s</add>\n\n" % data
            data = ""
        if( ( count % SOLR_COMMIT_BATCH_SIZE) == 0):
            try:
                print "committing..."
                beginCommitTime = time.time()
                resp = postURL( SOLR_UPDATE_URL, SOLR_COMMIT_MESSAGE)
                if PRINT_SOLR_RESP_DATA:
                    print resp
                commitTime += ( time.time() - beginCommitTime )
            except IOError:
                import time
                print "Connection reset when talking to Solr, skipping this commit and sleeping 10 sec."
                time.sleep(10)

            if lastCommitTime:
                thisBatchRate = ( ( 0.0 + SOLR_COMMIT_BATCH_SIZE) / (time.time() - lastCommitTime) )
                overallRate = ( ( 0.0 + count ) / ( time.time() - startTime) )
                print "[%s] %s records indexed\t| This Batch: %.4f records/sec|\tOverall: %.4f records/sec" % (time.ctime(), count, thisBatchRate, overallRate)
                if PROFILE:
                    print """\nfile->MARC: %.4f\nMARC->py: %.4f\npy->XML: %.4f\n""" % ( marcReaderTime, marcRecordForSolrTime, marcSerializeTime )
                    print """MARC to dict: %.4f\ncreate extractor: %.4f\nextraction: %.4f\n""" % ( marcRecordToDictTime, extractorCreateTime, extractionTime )
                    print """Solr Update: %.4f\nSolr Commit: %.4f\n""" % ( updateTime, commitTime )                          
            lastCommitTime = time.time()
            System.gc()
    # do last batch here
    if len(data) > 0:
        print "doing final POST"
        resp = postURL( SOLR_UPDATE_URL, "<add>%s</add>" % data)
        if PRINT_SOLR_RESP_DATA:
            print resp
    print "committing..."
    commit()
          
    inStream.close()

            
            
if __name__ == '__main__':
    anselUnicodeConverter = AnselToUnicode()
    # 2 arguments to command line are used to do a ran
    if len(sys.argv) == 2:
        processFile( sys.argv[1], anselUnicodeConverter )
    else:
        print "incorrect usage -- specify file to be processed."
        sys.exit(1)
    print "done indexing, now optimizing"
    optimize()
    print "done optimizing, now warming facets"
    from facetWarmer import *
    for i in range(3):
        # running warmFacets more than once appears to improve performance.
        warmFacets( server=SOLR_QUERY_URL )
    print "all done!"
