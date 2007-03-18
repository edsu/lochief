# Indexer for marc records
from java.io import *
from java.net import *
from org.marc4j import *
from org.marc4j.converter.impl import *

from loadPropsFile import *
from processors import *

import time

class MarcExtractor:
    '''
    This class extracts MARC records.
    '''

    def __init__(self, marcRecord):
        if type( marcRecord ) == type(""): marcRecord = eval(marcRecord)
        self.marcRecord = marcRecord

    def extract(self, extractString, dedupe=1, stripTrailingPunctuation = 1, trailingPunctuationToStrip = [".", ","], separator = " " ):
        '''
        Generic extractor of subfields from a MARC field.
        Returns an array of the subfields and their values.
        '''
        ret = []
        thingsToExtract = [x.strip() for x in extractString.split(",") ]
        for extractStringOn in thingsToExtract:
            if extractStringOn.find("$") > -1:
                tag, subfields = extractStringOn.split("$")
                if self.marcRecord.has_key(tag):
                    for fieldOn in self.marcRecord[tag]:
                        subfieldsToAdd = []
                        for subfieldOn in subfields:
                            if fieldOn.has_key( "%s" % subfieldOn ):
                                sfOn = fieldOn[subfieldOn].strip()
                                if stripTrailingPunctuation and sfOn and sfOn[-1] in trailingPunctuationToStrip:
                                    sfOn = sfOn[:-1]
                                subfieldsToAdd.append( sfOn )
                        if len(subfieldsToAdd) > 0:
                            if not dedupe:
                                ret.append( separator.join( subfieldsToAdd) )
                            else:
                                toAdd = separator.join(subfieldsToAdd)
                                if toAdd not in ret:
                                    ret.append( toAdd )
            elif extractStringOn.find("/") > -1:
                tag,positions = extractStringOn.split("/")
                if self.marcRecord.has_key(tag):
                    for fieldOn in self.marcRecord[tag]:
                        splitted = [int(x) for x in positions.split(":")]
                        if len(splitted) == 1:
                            try: 
                                ret.append( fieldOn[ splitted[0] ] )
                            except IndexError:
                                pass    # just ignore
                        elif len(splitted) == 2:
                            try: 
                                ret.append( fieldOn[ splitted[0] : splitted[1] ] )
                            except IndexError:
                                pass
        return ret 

def marcRecordToDict( marcRecord, converter ):
    """takes in a marc4j marc record and converts it to a python dict object"""
    controlFields = marcRecord.getControlFields() 
    dataFields = marcRecord.getDataFields() 
    leader = marcRecord.getLeader()
    ret = { '000' : leader.marshal() }
    for fieldOn in controlFields:
            tagOn = fieldOn.getTag()
            if ret.has_key( tagOn ): 
                ret[ tagOn ].append( fieldOn.getData() )
            else: 
                ret[tagOn] = [fieldOn.getData()]
    for fieldOn in dataFields:
        tagName = fieldOn.getTag() ; fieldAsDict = {}
        subfields = fieldOn.getSubfields()
        for subfieldOn in subfields:
            code = subfieldOn.getCode()
            fieldAsDict[code] = converter.convert( subfieldOn.getData().replace("\x1B", "") )
        if ret.has_key( tagName ): 
            ret[tagName].append( fieldAsDict )
        else: 
            ret[tagName] = [fieldAsDict]
    return ret

class recordForSolr:
    """takes a marc record in dict format and processes it using the configurations specified in 
    indexes.properties"""
    def __init__(self, marcRecord, anselUnicodeConverter = None, accession = None, config = None, indexerProperties="config/indexes.properties"):
        start = time.time()
        self._marcRecordToDictTime = 0
        self._extractionTime = 0
        self._extractorCreateTime = 0
        
        if anselUnicodeConverter is None: 
            anselUnicodeConverter = AnselToUnicode()
        record = marcRecordToDict( marcRecord, anselUnicodeConverter )
        self._marcRecordToDictTime = time.time() - start
        
        start = time.time()
        
        if config is None:
            config = loadPropsFile(indexerProperties)
        extractor = MarcExtractor( record )
        self._extractorCreateTime = (time.time() - start)
        
        self.marc_record = str( record )
        
        fieldsToDo = [x.strip() for x in config['active.fields'].split(",")]
        _processors = __import__('processors', {},{},[''])
        for fieldOn in fieldsToDo:
            start = time.time()
            processorNameOn = config.get( "%s.processor" % fieldOn, "standardProcessor" )
            marcMapOn = config.get("%s.marcMap" % fieldOn, None)
            # do processing
            if processorNameOn == "standardProcessor":    # then just use the MARC extractor
                separatorOn = config.get("%s.marcMap.separator" % fieldOn, " ")
                stripTrailingPunctuation = int( config.get("%s.stripTrailingPunctuation" % fieldOn, "0") )
                processedResult = extractor.extract( marcMapOn, separator = separatorOn, stripTrailingPunctuation = stripTrailingPunctuation )
                if ((processedResult == None) or len(processedResult) == 0) and config.has_key("%s.marcMap.lastResort" % fieldOn ):
                    marcMapOn = config.get("%s.marcMap.lastResort" % fieldOn, None)
                    processedResult = extractor.extract( marcMapOn, separator = separatorOn )
            else:
                processorOn = getattr( _processors, processorNameOn )    
                processedResult = processorOn( record, marcMap=marcMapOn, extractor=extractor )
            # do post-processing based upon type
            typeOn = config.get("%s.type" % fieldOn, "multi")
            if typeOn == "single" and ( type(processedResult) == type([])) and len(processedResult) > 0:
                postProcessedResult = processedResult[0]
            elif typeOn == "singleTranslation":
                if( type(processedResult) == type([]) ):
                    if len(processedResult) >= 1:
                        processedResult = processedResult[0]
                    else:
                        processedResult = None
                translationMapName = config.get("%s.translationMap" % fieldOn, None)
                if translationMapName is not None:
                    _translationMapModule = __import__( "config.codes" , {},{},[''] )
                    _translationMap = getattr( _translationMapModule, translationMapName)
                    postProcessedResult = _translationMap.get( processedResult, None)
            else:
                postProcessedResult = processedResult
            # set own attribute
            if postProcessedResult is not None and len(postProcessedResult) > 0:
                setattr( self, fieldOn, postProcessedResult )
            self._extractionTime += ( time.time() - start )
    def __str__(self):
        import pprint
        ret = []
        for attr in dir(self):
            ret.append( "%s -> %s" % ( attr, pprint.pformat( getattr(self, attr) ) ) )
        return "\n".join(ret)
    def serialize(self):
        out = "" 
        attrs = [ x for x in self.__dict__.keys() if not x.startswith("_") ]
        for attrOn in attrs:
            value = getattr( self, attrOn )
            if type(value) == type( [] ):
                for subvalueOn in value: 
                    subvalueOn = subvalueOn.replace("&", "&amp;").replace("<", "&amp;lt;").replace(">", "&amp;gt;") 
                    out += u"""<field name="%s">%s</field>""" % ( attrOn, subvalueOn)
            else:
                field = getattr(self, attrOn)
                if field: 
                    field = field.replace("&", "&amp;").replace("<", "&amp;lt;").replace(">", "&amp;gt;" ) 
                    out += u"""<field name="%s">%s</field>""" % ( attrOn, field )
                else: 
                    print "field %s was None!" % attrOn    # csdebug!!!
        return u"<doc>%s</doc>" % out
         
