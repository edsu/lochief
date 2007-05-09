SOLR_SERVER = "localhost:8983"
SEARCH_CACHE_TIME = 6000    # in seconds
ITEMS_PER_PAGE = 10
MAX_FACET_TERMS_BASIC = 4    # how many facet terms display by default
MAX_FACET_TERMS_EXPANDED = 25 # how many facet terms display when you hit "show more"
OPAC_FULL_BIB_URL = "http://sirsiweb.laurentian.ca/uhtbin/cgisirsi/x/x/x/57/5/?user_id=WEBSERVER&searchdata1=%s{%s}"
FACETS = [    { 'name' : _('Subject: Topic'), 'code' : 'topic' },    
              { 'name' : _('Subject: Genre'), 'code' : 'genre' },                            
              { 'name' : _('Format'), 'code' : 'format' },                        
              { 'name' : _('Library') , 'code' : 'location', 
               'maxItems' : 0 , 'translateFunction' : 'getLocationName'}, 
              { 'name' : _('Subject: Region'), 'code' : 'place' },    
              { 'name' : _('Language'), 'code' : 'language' }, 
              { 'name' : _('Author'), 'code' : 'author_exact'  },]

SEARCH_INDEXES = [ {'name' : _('Anywhere'), 'index': 'text'},
                  {'name' : _('Author'), 'index': 'author'} , { 'name' : _('Title'), 'index' : 'title' },
                  {'name' : _('Subject'), 'index': 'subject'}, { 'name' : _('ISBN'), 'index' : 'isbn' },]

SORTS = [{ 'name' : _('Pub. Date (newest first)'), 'direction' : 'desc', 'field' : 'pubdate' },
         { 'name' : _('Pub. Date (oldest first)'), 'direction' : 'asc', 'field' : 'pubdate' },
         { 'name' : _('Author A-Z'), 'direction' : 'asc', 'field' : 'author_exact' },]

FORMAT_ICONS = { 'eAudio' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-eaudio.gif" alt="eAudio" />',
                    'eBook' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-ebook.gif" alt="eBook" />',
                    'CD-ROM' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-cdrom.gif" alt="cd rom" />',
                    'Book On Cassette' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-bt.gif" alt="book on cassette" />',
                    'Book On CD' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-bkcd.gif" alt="book on CD" />',
                    'Cassette' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-audio.gif" alt="cassette" />',
                    'Music CD' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-cd.gif" alt="music cd" />',
                    'Phono Record' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-record.gif" alt="phono record" />',
                    'DVD' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-dvd.gif" alt="dvd" />',
                    'Videocassette' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-video.gif" alt="videocassette" />',
                    'Large Print Book' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-largeprint.gif" alt="large print book" />',
                    'Book' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-book.gif" alt="book" />',
                    'Magazine' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-magazine.gif" alt="magazine" />',
                    'Map' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-map.gif" alt="map" />',
                    'Musical Score' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-score.gif" alt="musical score" />',
                    'Digital Music' : '<img src="http://catalog.spl.org/hipres/images/formaticons/ipac-icon-digimusic.gif" alt="digital music" />',}
