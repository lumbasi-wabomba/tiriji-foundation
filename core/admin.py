from django.contrib import admin
from .models import program, volunteer, events, news, resources

class ProgramAdmin(admin.ModelAdmin):
    exclude = ('image',)

admin.site.register(program, ProgramAdmin)
admin.site.register(volunteer)
admin.site.register(events)
admin.site.register(news)
admin.site.register(resources)



