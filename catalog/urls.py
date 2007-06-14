from django.conf.urls.defaults import *

urlpatterns = patterns( '',
    (r'^catalog/$', 'catalog.views.index'),
    (r'^catalog/search/$', 'catalog.views.search'),
    (r'^catalog/item/$', 'catalog.views.item'),
    (r'^catalog/feed/atom/$', 'catalog.views.atomFeed'),
    (r'^catalog/feed/rss/$', 'catalog.views.rssFeed'))
