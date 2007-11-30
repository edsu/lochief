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
	
	
