from django.contrib import admin
from .models import Tune, TuneFavori, TuneFavori_user, TuneFavori_group, Audio_clyp_tune, Audio_clyp_user_favori, Audio_clyp_group_favori, ABCTune, Title, Composer

# Register your models here.


class ABCInline(admin.TabularInline):
    model = ABCTune


class TuneAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'type', 'slug', 'nb_vues')
    list_filter = ('name', 'key', 'type')
    #  date_hierarchy = 'date'
    ordering = ('date_creation', )
    search_fields = ('name',)


class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    list_filter = ('name', )
    #  date_hierarchy = 'date'
    ordering = ('date_creation', )
    search_fields = ('name',)


class ABCAdmin(admin.ModelAdmin):
    list_display = ('T', 'version',)
    list_filter = ('T', )
    #  date_hierarchy = 'date'
    ordering = ('date_creation', )
    search_fields = ('T',)


admin.site.register(Tune, TuneAdmin)
admin.site.register(TuneFavori)
admin.site.register(TuneFavori_user)
admin.site.register(TuneFavori_group)
admin.site.register(Audio_clyp_group_favori)
admin.site.register(Audio_clyp_user_favori)
admin.site.register(Audio_clyp_tune)
admin.site.register(ABCTune, ABCAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Composer)
