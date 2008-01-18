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

# this is where your custom processors go.  They must have record as required argument and
# marcMap and extractor as optional named arguments.  Don't like it?  Go write your own indexer.
from config.codes import *

def genreProcessor( record, marcMap=None, extractor=None):
    # todo: change to use extractor
    ret = None
    if record.has_key('655'):
        ret = []
        for recordOn in record['655']:
            if recordOn.has_key('2') and recordOn['2'].strip() == "gsafd" and recordOn.has_key('a'):
                genreOn =recordOn['a']
                if genreOn not in ret:
                    ret.append( genreOn )
    return ret

def deweyClassProcessor( record, marcMap=None, extractor=None):
    callNum = extractor.extract( marcMap )
    if len(callNum) > 0:
        callNum = callNum[0] # TODO: make it able to handle multiple call numbers
        words = callNum.split(" ")[:2]    # only look at the first "two" words of the call number to avoid getting the date.
        foundDeweyClass = 0
        for wordOn in words:
            # get all the digits from this word and see if they make up a dewey class.
            numsOn = ''.join( [x for x in wordOn if x.isdigit() ] )
            if len(numsOn) > 2:
                return numsOn[:3]
    return None

def isbnProcessor( record, marcMap=None, extractor=None):
    import re
    isbn = extractor.extract( marcMap )
    #if isbn <> []:
    #    print isbn
    ret = None
    found = 'false'
    resultOn = []
    isbnRegexes = [r"""\b\d{13}\b""",r"""\b\d{9}[X0-9]\b"""]

    for isbnOn in isbn:
        for regexOn in isbnRegexes:
            if found <> 'true':
                isbnOn.replace('-','')
                reresults = re.findall( regexOn, isbnOn )
                for result in reresults:
                    resultOn.append(result)
                    if result <> '':
                        found = 'true'
            
        if len(resultOn) >= 1:
            #print resultOn
            return resultOn
    if ret is None and isbn <> []:
        print "could not parse isbn from <<%s>> for isbn" % isbn
    return ret

def LCClassProcessor( record, marcMap=None, extractor=None):
    callNum = extractor.extract( marcMap )
    if len(callNum) > 0:
        callNum = callNum[0] # TODO: make it able to handle multiple call numbers
        return callNum
    return None

def pubdateProcessor( record, marcMap=None, extractor=None):
    import re
    pubdate = extractor.extract(marcMap)
    ret = None
    if type(pubdate) == type([]):
        if (len(pubdate) > 0):
            pubdate = pubdate[0]    # TODO: make it handle multiple pubdates, or pick the 'best' one or something
        else:
            return None    # empty list
    pubdateYearRegexes = [  r"""\[(\d{4})\]""", r"""[cp]{1}(\d{4})""", r"""([\d]{4})""",]

    for regexOn in pubdateYearRegexes:
        resultOn = re.findall( regexOn, pubdate )
        if len(resultOn) >= 1:
            # TODO: decide if there are > 1 viable results, if we should just take the 1st one like this...
            return resultOn[0]
    if ret is None:
        print "could not parse pubdate from <<%s>> for pubdate" % pubdate
    return ret

def pubdaterangeProcessor( record, marcMap=None, extractor=None):
    import re
    pubdate = extractor.extract(marcMap)
    if type(pubdate) == type([]):
        if (len(pubdate) > 0):
            pubdate = pubdate[0]    # TODO: make it handle multiple pubdates, or pick the 'best' one or something
        else:
            return None    # empty list
    pubdateYearRegexes = [  r"""\[(\d{4})\]""", r"""[cp]{1}(\d{4})""", r"""([\d]{4})""",]

    for regexOn in pubdateYearRegexes:
        resultOn = re.findall( regexOn, pubdate )
        if len(resultOn) >= 1:
            # TODO: decide if there are > 1 viable results, if we should just take the 1st one like this...
            count = 1
            dateranges = range(0,2050,10)
            for i in dateranges:
                if int(resultOn[0]) >= dateranges[count - 1] and int(resultOn[0]) < dateranges[count]:
                    return "%s-%s" % (dateranges[count - 1],(dateranges[count]-1))
                count += 1
    print "could not parse pubdate from <<%s>> for pubdaterange" % pubdate
    return None

def formatProcessor( record, marcMap=None, extractor=None):
    serialsFrequencies = [ 'b', 'c', 'd','e','f','i','j','m','q','s','t','w']
    marcRecord = record
    leader = marcRecord.get('000', None)
    if leader is None:
        return "Unknown"
    physDescr = marcRecord.get('007', [" ",] )[0]
    theFormat = "Unknown"
   
    if(len(leader) > 7):
        if( len(physDescr) > 5):
            if(physDescr[0] == "c"):            # electronic resource
                if( physDescr[1] == "r"):        # remote resource
                    if physDescr[5] == "a":     # has sound
                        theFormat = "eAudio"
                    else:
                        theFormat = "eBook"

                elif( physDescr[1] == "o"):        # optical disc
                    theFormat = "CD-ROM"
                  
            elif(physDescr[0] == "s"):            # sound recording
                if leader[6] == "i":            # nonmusical sound recording
                    if(physDescr[1] == "s"):    # sound cassette
                        theFormat = "Book On Cassette"

                    elif(physDescr[1] == "d"):    # sound disc
                        if( physDescr[6] == "g" or physDescr[6] == "z"):    # 4 3/4 inch or Other size
                            theFormat = "Book On CD"

                elif leader[6] == "j":        # musical sound recording
                    if(physDescr[1] == "s"):    # sound cassette
                        theFormat = "Cassette"

                    elif(physDescr[1] == "d"):    # sound disc
                        if( physDescr[6] == "g" or physDescr[6] == "z"):    # 4 3/4 inch or Other size
                            theFormat = "Music CD"

                        elif( physDescr[6] == "e" ):                # 12 inch
                            theFormat = "Phono Record"

            elif( physDescr[0] == "v"):            # videorecording
                if(physDescr[1] == "d"):        # videodisc
                    theFormat = "DVD"

                elif(physDescr[1] == "f"):        # videocassette
                    theFormat = "Videocassette"

    
        # now do guesses that are NOT based upon physical description 
        # (physical description is going to be the most reliable indicator, when it exists...) 
        elif leader[6] == "a":                # language material
            fixedLengthData = marcRecord.get("008", [" ",] )[0]
            if leader[7] == "m":            # monograph
                if( len(fixedLengthData) > 22 ):
                    if fixedLengthData[23] == "d":    # form of item = large print
                        theFormat = "Large Print Book"
                    elif fixedLengthData[23] == "s":    # form of item = electronic resource
                        theFormat = "eBook"
                    else:
                        theFormat = "Book"
                else:
                    theFormat = "Book"
            elif leader[7] == "s":            # serial
                if len(fixedLengthData) > 18:
                    if fixedLengthData[18] in serialsFrequencies:
                        theFormat = "Journal"
                    else:
                        # this is here to prevent stuff that librarians and nobody else
                        # would consider to be a serial from being labeled as a magazine.
                        theFormat = "Book"

        elif leader[6] == "e":
            theFormat = "Map"

        elif leader[6] == "c":
            theFormat = "Musical Score"

        
        if theFormat is "Unknown": 
            # We still haven't found a match.
            # as last resort, we'll try parsing 092 field, then possibly collection code, etc.
            callNum = " "
            text = marcRecord.get("092", None)
            if text is None:
                text = {}
            else:
                text = text[0]    # TODO make multivalued
            if text.has_key( 'a' ):
                callNum = text['a'].lower()
            if( callNum.startswith("cdrom") ):
                theFormat = "CD-ROM"
            elif( callNum.startswith("cd") ):
                # guess it is a musical CD
                ## update 9/12/2006 --> don't assume music CD
                try:
                    if leader[6] == "i":    # nonmusical sound recording; must be book on CD
                        theFormat = "Book On CD"
                    else:
                        theFormat = "Music CD"
                except:
                    theFormat = "Music CD"
            elif( callNum.startswith("vhs") ):
                theFormat = "Videocassette"
            elif( callNum.startswith("eaudio") ):
                theFormat = "eAudio"
            elif (callNum.startswith("ebook") ):
                theFormat = "eBook"
            elif( callNum.startswith("dvd") ):
                theFormat = "DVD"
            elif( callNum.startswith("emusic") ):
                theFormat = "Digital Music"
    return theFormat

def formatbylocProcessor( record, marcMap=None, extractor=None):
    serialsFrequencies = [ 'b', 'c', 'd','e','f','i','j','m','q','s','t','w']
    marcRecord = record
    leader = marcRecord.get('000', None)
    if leader is None:
        return "Unknown"
    physDescr = marcRecord.get('007', [" ",] )[0]
    theFormat = "Unknown"

    #Determine Item type from 999 field.Format Icons settings found in catalog/config.py
    itemType = marcRecord.get('999', None)
    count = 0
    for copies in itemType:
        count = count + 1
        for key, value in copies.items():
            if key == "t":
                if value == "BOOK":
                    theFormat = "Book"
                elif value == "AV":
                    theFormat = "Audio-Visual"
                elif value == "JOURNAL":
                    theFormat = "Journal"
                elif value == "LAPTOP":
                    theFormat == "Laptop"
                elif value == "EQUIP":
                    theFormat == "Equipment"
                elif value == "LOCAL_HIST":
                    theFormat == "Local_History"
                elif value == "REF_BOOK":
                    theFormat == "Reference"
                elif value == "RESERVE":
                    theFormat == "Reserve"
                elif value == "SOFTWARE":
                    theFormat == "Software"
                elif value == "VIDEO":
                    theFormat == "Video"
                elif value == "MAP":
                    theFormat == "Map"
                else:
                    theFormat == "Unknown"

        
    return theFormat

def CopyinfoProcessor( record, marcMap=None, extractor=None):
    copyinfoOn = None
    
    if record.has_key('999'):
        copyinfoOn = []
        tmpli=[]
        status = ''
        for recordOn in record['999']:
            
            #set availability status
            #%k = location if unavailable
            if not recordOn.has_key('k') and recordOn.has_key('l') and recordOn['l']!="DISCARD":
                status = "Available"
            else:
                status = "Unavailable"
       
            #%c= copy #    %l=location
            if recordOn.has_key('c') and recordOn.has_key('l'):
                if recordOn.has_key('k'):
                    copyinfoOn.append('%s|%s|%s|%s|%s' % (recordOn['c'], recordOn['a'], recordOn['k'], recordOn['t'], status))
                else:
                    copyinfoOn.append('%s|%s|%s|%s|%s' % (recordOn['c'],recordOn['a'], recordOn['l'], recordOn['t'], status))
                           
    return copyinfoOn


def AvailabilityProcessor( record, marcMap=None, extractor=None):
    availabilityOn = None
    status = None
    if record.has_key('999'):
        availabilityOn = []
        #unavailableflag = false
        availableflag = 0
        for recordOn in record['999']:
            
            #set availability status
            #%k = location if unavailable
         #   if recordOn.has_key('k'):
          #      unavailableflag = true
            if not recordOn.has_key('k') and recordOn.has_key('l') and recordOn['l']!="DISCARD":
                availableflag = 1

        if availableflag == 1:
            status = 'Available'
            
        if availableflag == 0:
            status = 'Unavailable'
           
        availabilityOn = ['%s' % status]
                           
    return availabilityOn

#used to create browse by call num functionality-layer 1 is 1st layer (ex. Dewey 000-100, 100-200, etc.)
def DeweyCallnumlayer1Processor( record, marcMap=None, extractor=None):
    #insert dewey processor here
    
    callNum = None
    recrodDeweyNum = None
    callNum = extractor.extract( marcMap )
    if callNum:
        callNum = str(callNum[0])
        deweyranges = range(0,900,100)
        recordDeweyNum = callNum[:3]
    #find the description for the dewey range
        if DEWEY_MAP.has_key(str(recordDeweyNum[:1] + '00')):
            deweydescription = DEWEY_MAP[str(recordDeweyNum[:1] + '00')]
    
    #write the dewey range and description to the index
        try:
            for i in deweyranges:
                if int(recordDeweyNum) >= i and int(recordDeweyNum) < i + 100:
                    return "%s-%s - %s" % (i,i+99,deweydescription.replace('&','and'))
        except:
            return None
                

#used to create browse by call num functionality-layer 2 is subset of 1st layer (ex. Dewey 100-110, 110-120, etc.)
def DeweyCallnumlayer2Processor( record, marcMap=None, extractor=None):
        #insert dewey processor here
        callNum = extractor.extract( marcMap )
        if callNum:
            callNum = str(callNum[0])
            deweyranges = range(0,990,10)
            recordDeweyNum = callNum[:3]
            #find the description for the dewey range
            if DEWEY_MAP.has_key(str(recordDeweyNum[:2] + '0')):
                deweydescription = DEWEY_MAP[str(recordDeweyNum[:2] + '0')]
            
            #write the dewey range and description to the index
            try:
                for i in deweyranges:
                    if int(recordDeweyNum) >= i and int(recordDeweyNum) < i + 10:
                        return "%s-%s - %s" % (i,i+9,deweydescription.replace('&','and'))
            except:
                return None
