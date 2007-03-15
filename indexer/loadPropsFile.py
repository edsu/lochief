# simple utility which loads a Properties file and returns it as a 
# python dictionary.
# TODO: have it parse datatypes...

from java.lang import *
from java.io import *
from java.util import *


def allDigits( someString ):
	for letterOn in someString.strip():
		if( not letterOn.isdigit() ):
			return 0
	return 1

def loadPropsFile( propsFile):
	ret = {}
	props = Properties()
	try:
		fis = FileInputStream(propsFile)
		props.load( fis )
	except:
		print "problem loading %s!" % propsFile
		return ret
	propEnum= props.propertyNames()
	while( propEnum.hasNext()):
		propNameOn = propEnum.next()
		propOn = props.getProperty( propNameOn)
		if( allDigits(propOn) ):
			ret[propNameOn] = int(propOn)
		else:
			ret[propNameOn] = propOn
	fis.close()
	return ret
	
	
