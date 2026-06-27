from django.contrib import admin

from .models import Province, City, Neighborhood


class CityInline(admin.TabularInline):
    model = City
    extra = 0

class NeighborhoodInline(admin.TabularInline):
    model = Neighborhood
    extra = 0

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [CityInline]



@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [NeighborhoodInline]

@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    search_fields = ['name']
