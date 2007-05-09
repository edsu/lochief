# this is where your custom processors go.  They must have record as required argument and
# marcMap and extractor as optional named arguments.  Don't like it?  Go write your own indexer.

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
        print "could not parse pubdate from <<%s>>" % pubdate
    return ret


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
