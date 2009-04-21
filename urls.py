from django.conf.urls.defaults import *

from fixcity.bmabr import views 
from django.conf import settings

# Uncomment the next two lines to enable the admin:

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    (r'^$', 'fixcity.bmabr.views.index'), 
    (r'assess/$','fixcity.bmabr.views.assess'),
    (r'^rack/(?P<rack_id>\d+)/$', 'fixcity.bmabr.views.rack'),                        
   

     # KML URL 

    (r'rack/all.kml$', 'fixcity.bmabr.views.rack_all_kml'),
    (r'rack/requested.kml$', 'fixcity.bmabr.views.rack_requested_kml'),
    (r'rack/requested.json$', 'fixcity.bmabr.views.rack_json'),
    (r'rack/pendding.kml$', 'fixcity.bmabr.views.rack_pendding_kml'),
    (r'rack/built.kml$', 'fixcity.bmabr.views.rack_pendding_kml'),
    (r'rack/(?P<rack_id>\d+).kml', 'fixcity.bmabr.views.rack_by_id_kml'),


    # different views for adding infomation, rack, comments. 

    (r'^rack/new/$', 'fixcity.bmabr.views.newrack_form'), # view for rack request form. 
    (r'^rack/add/$', 'fixcity.bmabr.views.add_rack'), 
    (r'^comment/add/$', 'fixcity.bmabr.views.add_comment'), 
                       
    # different ways of viewing information                   

    (r'^neighborhoods/$', 'fixcity.bmabr.views.neighborhoods'), 
    (r'^communityboard/$', 'fixcity.bmabr.views.communityboard'),


    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_DOC_ROOT,'show_indexes': True}),



    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
 #    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
)
