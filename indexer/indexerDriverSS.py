# Copyright 2007 Casey Durfee
# Copyright 2007 Michael Beccaria
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

## indexes records from solr
from java.io import *
from java.net import *
#from org.marc4j import *
#from org.marc4j.converter.impl import *
import time, sys, urllib
#import csv
#from indexer import *
from loadPropsFile import *

indexerConfig = loadPropsFile("config/indexer.properties")
SOLR_COMMIT_MESSAGE = indexerConfig.get( "SOLR_COMMIT_MESSAGE" )
SOLR_OPTIMIZE_MESSAGE = indexerConfig.get( "SOLR_OPTIMIZE_MESSAGE" )
SOLR_DELETE_ID_MESSAGE = indexerConfig.get("SOLR_DELETE_ID_MESSAGE" )
SOLR_BASE_URL = indexerConfig.get("SOLR_BASE_URL", "http://localhost:8983/solr" ) 
SOLR_UPDATE_URL = indexerConfig.get( "SOLR_UPDATE_URL" )
SOLR_QUERY_URL = indexerConfig.get( "SOLR_QUERY_URL" ) 
MAX_RECORDS_TO_ADD = indexerConfig.get("MAX_RECORDS_TO_ADD")
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
    br = BufferedReader( InputStreamReader( hu.getInputStream() ) )
    lineOn = ""
    ret = ""
    
    while lineOn is not None:
        ret += lineOn
        lineOn = br.readLine()
    return ret

def optimize(url =SOLR_UPDATE_URL):
    postURL( url, SOLR_OPTIMIZE_MESSAGE )

def commit( url = SOLR_UPDATE_URL ):
    postURL( url, SOLR_COMMIT_MESSAGE )
    
def deleteRecord( recordID, url = SOLR_UPDATE_URL):
    postURL( url, SOLR_DELETE_ID_MESSAGE % locals() )

def encode(text):
    text = text.replace("&", "&amp;") # must be first!
    text = text.replace("<", "&amp;lt;")
    text = text.replace(">", "&amp;gt;")
    text = text.replace("'", "&apos;")
    text = text.replace('"', "&quot;")
    return text


def csv2list(csvString):
    foundstartquote = 0
    foundendquote = 0
    joinstr = ''
    finalarray=[]
    finalarray.insert(0,[])
    count = 0
    if csvString [-1:] <> '\n':
        csvString = csvString + '\n'
    csvlist = [row.split(",") for row in csvString.split("\n")]
    csvlist.pop()
    beginquotecount = -1
    for t in csvlist[0]:
        if t[:1] == '"' and t<> '"':
            foundstartquote = 1
            beginquotecount = count
        if t[-1:] == '"' or t == '"':
            foundendquote = 1
            endquotecount = count
        if foundstartquote == 1 and foundendquote == 1:
            joinstr = ','.join(csvlist[0][beginquotecount:endquotecount + 1])
            foundstartquote = 0
            foundendquote = 0
            if joinstr[-1] == '"':
                joinstr = joinstr[:-1]
            if joinstr[0] == '"':
                joinstr = joinstr[1:]
                
            finalarray[0].append(joinstr)
        elif (foundstartquote == 1 and foundendquote == 0) or (foundstartquote == 0 and foundendquote == 1):
            tmp=''
        elif foundstartquote == 0 and foundendquote == 0:
            finalarray[0].append(t)
        count += 1
    joinstr = ''
    str=''
    return finalarray

def processFile( filename):
    import codecs
    input=open(filename,'r')  
    m=input.readlines()
    input.close
    
    #reader = csv.reader(open(filename))
    print "processing file <<%s>>" % filename
    out=[]
    count = 0
    lastCommitTime = None
    import time
    curdata=[]
    curtitle=''
    prevtitle=''
    rec={}
    rowcount = 0
    for li in m:
        if li <> '':
            reader = csv2list(li)
            rowcount +=1
            #print rowcount
            for item in reader:
                #index 0=title 1=issn 2=Start Date 3= End Date 4=Resource 5,6,7,8,9=subject 1-5 10=url
                curtitle=item[0]
            
                #if enddate field is empty, make it equal to 'present'
                if item[3] == '':
                    item[3] = "present"
                tmp = [encode((item[0])),encode((item[1])),encode((item[2])),encode((item[3])),encode((item[4])),encode((item[5])),encode((item[6])),encode((item[7])),encode((item[8])),encode((item[9])),encode((item[10]))]
            
                if rec.has_key(curtitle)==1:
                    rec[curtitle].append(tmp)
                else:
                    rec[curtitle]=[tmp]
                    doccount = 0       

    for k in rec.keys():
        doccount += 1
        out.append(u"<doc>")
        out.append(u"<field name=\"format\">%s</field>" % ('Journal'))
        out.append(u"<field name=\"bib_num\">SS%s</field>" % doccount)
        out.append(u"<field name=\"title\">%s</field>" % rec[k][0][0])
        out.append(u"<field name=\"issn\">%s</field>\n" % rec[k][0][1])

        #cycle through array items 5-9 to include subjects       
        for x in 5,6,7,8,9:
            if rec[k][0][x]:
                #rec[k][0][x] = rec[k][0][x].replace("\&","and")
                out.append(u"<field name=\"topic\">%s (journals)</field>\n" % (rec[k][0][x].replace("&amp;","and")))
                    
        #index startdate, enddate, resourcename and url- hopefully they stay in order
        for record in rec[k]:
            #if enddate is blank, assume it's 'present'
            if record[3] == '':
                record[3] = (u'Present')
            #in this order: url,resourcename,startdate,enddate
            out.append(u"<field name=\"SSdata\">%s|%s|%s|%s</field>\n" % (encode(record[10]),record[4],record[2],record[3]))
                
        out.append(u"</doc>")
            
        if( (doccount % SOLR_INDEX_BATCH_SIZE ) == 0):
            try:
                data = '\n'.join(out)
                data = ("<add>%s</add>" % data)
                resp = postURL( SOLR_UPDATE_URL, data)
                if PRINT_SOLR_RESP_DATA:
                    print resp
                print 'posted %s documents' % doccount
                data = ''
                out =[]
            except IOError:
                import time
                print "Connection reset when talking to Solr, skipping this commit and sleeping 10 sec."
                time.sleep(10)


        
    if len(out) > 0:
        #do the last batch
        print 'doing final post'
        data = '\n'.join(out)
        data = ("<add>%s</add>" % data)
        #data = encode(data)          
        resp = postURL( SOLR_UPDATE_URL, data)
        #print data
        #print resp
        resp = postURL( SOLR_UPDATE_URL, SOLR_COMMIT_MESSAGE)
        System.gc()
    print "committing..."
    commit()
    print "done"   
        

  
          
    

            
            
if __name__ == '__main__':
    if len(sys.argv) == 2:
        processFile( sys.argv[1])
    print "done indexing, now optimizing"
    optimize()
    print "done optimizing, now warming facets"
    from facetWarmer import *
    for i in range(3):
        # running warmFacets more than once appears to improve performance.
        warmFacets( server=SOLR_QUERY_URL )
    print "all done!"
