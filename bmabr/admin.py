from fixcity.bmabr.models import Rack, Comment, Neighborhoods, CommunityBoard, SubwayStations

from django.contrib.gis import admin

class SubwayAdmin(admin.GeoModelAdmin): 
    list_display = ('name','borough')
    search_fields = ('name','borough')
admin.site.register(SubwayStations,SubwayAdmin)

class CommentAdmin(admin.GeoModelAdmin): 
    list_display = ('rack','contact_email')
admin.site.register(Comment,CommentAdmin)

class RackAdmin(admin.GeoModelAdmin): 
    list_display = ('address','location')
admin.site.register(Rack, RackAdmin)


class NeighborhoodsAdmin(admin.GeoModelAdmin): 
    list_display = ('name','county')
admin.site.register(Neighborhoods,NeighborhoodsAdmin)


class CommunityBoardAdmin(admin.GeoModelAdmin): 
    list_display = ('name','gid')
admin.site.register(CommunityBoard,CommunityBoardAdmin)
