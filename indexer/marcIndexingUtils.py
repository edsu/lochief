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

## some utilities for working with and indexing marc records
import marcConstants
import re


def extractISBNNumeric( rawISBN ):
    return ''.join( [ x for x in rawISBN if ( x.isdigit() or x.lower == "x") ] )

def processPubdate( pubdate ):
    """processes a publication date, normalizing it and so on."""
    # each regex is checked in turn until one that works is found.
    pubdateYearRegexes = [  r"""\[(\d+)\]""", r"""[cp]{1}(\d+)""", r"""([\d]{4})""",]
    ret = None
    for regexOn in pubdateYearRegexes:
        resultOn = re.findall( regexOn, pubdate )
        if len(resultOn) == 1:
            return resultOn[0]
    if ret is None:
        print "could not parse pubdate from %s" % pubdate
    return ret

def stripPunctuation( someString, side="trailing"):
    """strips all trailing punctuation from the string"""
    ret = someString
    if side == "trailing" or side == "both":
        keepGoing = 1
        while keepGoing and len(ret) > 0:
            if not (ret[-1].isdigit() or ret[-1].isalpha() ):
                ret = ret[:-1]
            else:
                keepGoing = 0
    if side == "leading" or side == "both":
        keepGoing = 1
        while keepGoing and len(ret) > 0:
            if not (ret[0].isdigit() or ret[0].isalpha() ):
                ret = ret[1:]
            else:
                keepGoing = 0       
    return ret

def stripTrailingPunctuation( someString ):
    return stripPunctuation( someString, "trailing")    

def guessFormat( marcRecord ):
    ## TODO: make handle multivalue fields
    """takes a marc record structured as a dictionary
    and returns a good guess for the physical format of the item."""
    
    # these are codes in the 008 pos. 18 that indicate a "genuine" serial (ie not Fodor's)
    serialsFrequencies = [ 'b', 'c', 'd','e','f','i','j','m','q','s','t','w']
    
    leader = marcRecord.get('000', None)
    if leader is None:
        return "Unknown"
    physDescr = marcRecord.get('007', [" ",] )[0]
    theFormat = "Unknown"
   
    if(len(leader) > 7):
        if( len(physDescr) > 5):
            if(physDescr[0] == "c"):			# electronic resource
                if( physDescr[1] == "r"):		# remote resource
                    if physDescr[5] == "a": 	# has sound
                        theFormat = "eAudio"
                    else:
                        theFormat = "eBook"

                elif( physDescr[1] == "o"):		# optical disc
                    theFormat = "CD-ROM"
                  
            elif(physDescr[0] == "s"):			# sound recording
                if leader[6] == "i":			# nonmusical sound recording
                    if(physDescr[1] == "s"):	# sound cassette
                        theFormat = "Book On Cassette"

                    elif(physDescr[1] == "d"):	# sound disc
                        if( physDescr[6] == "g" or physDescr[6] == "z"):	# 4 3/4 inch or Other size
                            theFormat = "Book On CD"

                elif leader[6] == "j":		# musical sound recording
                    if(physDescr[1] == "s"):	# sound cassette
                        theFormat = "Cassette"

                    elif(physDescr[1] == "d"):	# sound disc
                        if( physDescr[6] == "g" or physDescr[6] == "z"):	# 4 3/4 inch or Other size
                            theFormat = "Music CD"

                        elif( physDescr[6] == "e" ):				# 12 inch
                            theFormat = "Phono Record"

            elif( physDescr[0] == "v"):			# videorecording
                if(physDescr[1] == "d"):		# videodisc
                    theFormat = "DVD"

                elif(physDescr[1] == "f"):		# videocassette
                    theFormat = "Videocassette"

    
        # now do guesses that are NOT based upon physical description 
        # (physical description is going to be the most reliable indicator, when it exists...) 
        elif leader[6] == "a":				# language material
            fixedLengthData = marcRecord.get("008", [" ",] )[0]
            if leader[7] == "m":			# monograph
                if( len(fixedLengthData) > 22 ):
                    if fixedLengthData[23] == "d":	# form of item = large print
                        theFormat = "Large Print Book"
                    elif fixedLengthData[23] == "s":	# form of item = electronic resource
                        theFormat = "eBook"
                    else:
                        theFormat = "Book"
                else:
                    theFormat = "Book"
            elif leader[7] == "s":			# serial
                if len(fixedLengthData) > 18:
                    if fixedLengthData[18] in serialsFrequencies:
                        theFormat = "Magazine"
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
                    if leader[6] == "i":	# nonmusical sound recording; must be book on CD
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

def extractDeweyClass( callNum ):
#===============================================================================
#    try:
#        return ''.join( [x for x in callNum if x.isdigit() ] )[:3]
#    except:
#        return None
#===============================================================================
    # 1. extract only the 1st two "words" of the call number 
    words = callNum.split(" ")[:2]
    foundDeweyClass = 0
    for wordOn in words:
        # get all the digits from this word and see if they make up a dewey class.
        numsOn = ''.join( [x for x in wordOn if x.isdigit() ] )
        if len(numsOn) > 2:
            return numsOn[:3]
    return None
        


def processRating( rating ):
    return rating.split(";")[0]    # everything after semicolon is "for extreme language and being awesome" part.


def translateDeweyCall( callNum ):
    """strips out the general dewey class of a call number and returns what it means"""
    deweyClass = extractDeweyClass( callNum )
    return marcConstants.DEWEY_MAP.get( deweyClass, "Unknown")


    
