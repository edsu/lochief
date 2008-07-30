import optparse
import doctest

## local libraries
from lib import marc

parser = optparse.OptionParser()
parser.add_option('-v', '--verbose', action='store_true', 
        dest='verbose', help = "Print more messages.")
options, args = parser.parse_args()

doctest.testmod(m=marc, verbose=options.verbose)
