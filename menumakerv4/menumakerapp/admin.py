from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from menumakerapp.models import Cuisine,cart,CustomAdmin,ObjCount
# Register your models here.

class CuisineAdmin(ImportExportModelAdmin):
    list_display = ['id','cuisine','item','role']

admin.site.register(Cuisine, CuisineAdmin)



class ObjCountAdmin(ImportExportModelAdmin):
    list_display = ['id','objuser','createDate','objcount','objlist']

admin.site.register(ObjCount, ObjCountAdmin)



class cartAdmin(admin.ModelAdmin):
    list_d = ['id','user','items']

class CustomAdminModel(admin.ModelAdmin):
    list_display = ['username', 'password']

admin.site.register(CustomAdmin , CustomAdminModel)

admin.site.register(cart, cartAdmin)
