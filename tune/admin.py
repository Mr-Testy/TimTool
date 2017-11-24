from django.contrib import admin
from .models import Tune, TuneFavori, TuneFavori_user, TuneFavori_group, Audio_clyp_tune, Audio_clyp_user_favori, Audio_clyp_group_favori

# Register your models here.


class TuneAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'type', 'slug', 'nb_vues')
    list_filter = ('name', 'key', 'type')
    #  date_hierarchy = 'date'
    ordering = ('date_creation', )
    search_fields = ('name',)


admin.site.register(Tune, TuneAdmin)
admin.site.register(TuneFavori)
admin.site.register(TuneFavori_user)
admin.site.register(TuneFavori_group)
admin.site.register(Audio_clyp_group_favori)
admin.site.register(Audio_clyp_user_favori)
admin.site.register(Audio_clyp_tune)
