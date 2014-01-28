'''
Created on Jul 8, 2013

@author: taylorak
'''
from django.conf.urls import patterns, url
urlpatterns = patterns('',
    url(r'^$', 'hmmer.views.inputFormDisplay', name="form"),
    url(r'^error/$', 'hmmer.views.errorPage', name="error"),

    # index
    url(r'^(?P<id>\d+\.\d+\.\d+)/$', 'hmmer.views.index', name="index"),

    #clades
    url(r'^(?P<id>\d+\.\d+\.\d+)/clades$', 'hmmer.views.clades', name="clades"),

    #subtypes
    url(r'^(?P<id>\d+\.\d+\.\d+)/unique$', 'hmmer.views.unique', name="unique"),
    url(r'^(?P<id>\d+\.\d+\.\d+)/shortnew$', 'hmmer.views.shortnew', name="shortnew"),
    url(r'^(?P<id>\d+\.\d+\.\d+)/perfect$', 'hmmer.views.perfect', name="perfect"),
    #url(r'^(?P<id>\d+\.\d+\.\d+)/subtypes$', 'hmmer.views.subtypes', name="subtypes"),

    # multiples
    url(r'^(?P<id>\d+\.\d+\.\d+)/multiples/(?P<file>[A-I])/corrected$', 'hmmer.views.multiplesCorrected', name="corrected"),
    url(r'^(?P<id>\d+\.\d+\.\d+)/multiples/(?P<file>[A-I])/resolved$', 'hmmer.views.multiplesResolved', name="resolved"),

    # tree
    url(r'^(?P<id>\d+\.\d+\.\d+)/placementTree/(?P<file>[A-I])/$', 'hmmer.views.tree', name="tree"),

    # chart
    url(r'^(?P<id>\d+\.\d+\.\d+)/(?P<site>[A-Za-z]+\d+)/$', 'hmmer.views.chart', name="chart"),

    # stats                       
    url(r'^(?P<uid>\d+\.\d+\.\d+)/stats/', 'hmmer.views.descriptiveStats', name = 'descStats'),
    #############
    # DOWNLOADS #
    #############

    # clades
    url(r'^(?P<id>\d+\.\d+\.\d+)/dlClades/$', 'hmmer.views.dlClades', name="dlClades"),
    url(r'^(?P<id>\d+\.\d+\.\d+)/dlAll/$', 'hmmer.views.dlAll', name="dlAll"),
    url(r'^(?P<id>\d+\.\d+\.\d+)/dlDetailed/$', 'hmmer.views.dlDetailed', name="dlDetailed"),

    # subtypes
    url(r'^(?P<id>\d+\.\d+\.\d+)/dlSubtypes/$', 'hmmer.views.dlSubtypes', name="dlSubtypes"),
    url(r'^(?P<id>\d+\.\d+\.\d+)/dlPerfect/$', 'hmmer.views.dlPerfect', name="dlPerfect"),
    url(r'^(?P<id>\d+\.\d+\.\d+)/dlShortnew/$', 'hmmer.views.dlShortnew', name="dlShortnew"),
    url(r'^(?P<id>\d+\.\d+\.\d+)/dlUnique/$', 'hmmer.views.dlUnique', name="dlUnique"),

    # multiples
    url(r'^(?P<id>\d+\.\d+\.\d+)/dlMultiples/$', 'hmmer.views.dlMultiples', name="dlMultiples"),
    ##url(r'^status/(?P<id>\d+\.\d+\.\d+)/(?P<dir>[A-I])/dlMultiples/$','hmmer.views.dlMultiples',name="dlMultiples"),

    # tree
    url(r'^(?P<id>\d+\.\d+\.\d+)/dlTree/$', 'hmmer.views.dlTree', name="dlTree"),
    ##url(r'^status/(?P<id>\d+\.\d+\.\d+)/(?P<dir>[A-I])/dlTree/$','hmmer.views.dlTree',name="dlTree"),

    # all
    url(r'^(?P<id>\d+\.\d+\.\d+)/dlEverything/$', 'hmmer.views.dlEverything', name="dlEverything"),
    # url(r'^status/(?P<id>\d+\.\d+\.\d+)/(?P<filename>[A-Z]+\_[a-z]+\.tsv)/download/$','hmmer.views.download',name="download"),
)
