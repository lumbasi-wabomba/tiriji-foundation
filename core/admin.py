from django.contrib import admin
from .models import program, volunteer, events, news, resources, employees, partners, gallery

class ProgramAdmin(admin.ModelAdmin):
    exclude = ('image',)

class EventsAdmin(admin.ModelAdmin):
    exclude = ('image',)

class NewsAdmin(admin.ModelAdmin):
    exclude = ('image',)

class ResourcesAdmin(admin.ModelAdmin):
    exclude = ('image', 'file')

class EmployeesAdmin(admin.ModelAdmin):
    exclude = ('profile_image',)

class PartnersAdmin(admin.ModelAdmin):
    exclude = ('profile_logo',)

class GalleryAdmin(admin.ModelAdmin):
    exclude = ('image',)

admin.site.register(program, ProgramAdmin)
admin.site.register(volunteer)
admin.site.register(events, EventsAdmin)
admin.site.register(news, NewsAdmin)
admin.site.register(resources, ResourcesAdmin)
admin.site.register(employees, EmployeesAdmin)
admin.site.register(partners, PartnersAdmin)
admin.site.register(gallery, GalleryAdmin)



