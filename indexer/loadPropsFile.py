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
	
	
