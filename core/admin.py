from django.contrib import admin
from .models import program, volunteer, events, news, resources, employees, partners, gallery, BlogPost, ImpactMetric, FeaturedPerson, SuccessStory, InspirationVideo, PageMedia



class ImpactMetricAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'page', 'display_order', 'is_active')
    list_filter = ('page', 'is_active')
    search_fields = ('label', 'value')


class FeaturedPersonAdmin(admin.ModelAdmin):
    exclude = ('image_url',)
    list_display = ('name', 'feature_type', 'page', 'is_featured', 'created_at')
    list_filter = ('page', 'feature_type', 'is_featured')
    search_fields = ('name', 'headline', 'achievement')


class SuccessStoryAdmin(admin.ModelAdmin):
    exclude = ('image_url',)
    list_display = ('title', 'person_name', 'page', 'is_featured', 'created_at')
    list_filter = ('page', 'is_featured')
    search_fields = ('title', 'person_name', 'challenge', 'outcome')


class InspirationVideoAdmin(admin.ModelAdmin):
    exclude = ('thumbnail_url',)
    list_display = ('title', 'page', 'is_featured', 'created_at')
    list_filter = ('page', 'is_featured')
    search_fields = ('title', 'description')


class PageMediaAdmin(admin.ModelAdmin):
    exclude = ('image_url',)
    list_display = ('title', 'page', 'media_type', 'display_order', 'created_at')
    list_filter = ('page', 'media_type')
    search_fields = ('title', 'description')

class ProgramAdmin(admin.ModelAdmin):
    exclude = ('image',)

class EventsAdmin(admin.ModelAdmin):
    exclude = ('image',)

class NewsAdmin(admin.ModelAdmin):
    exclude = ('image',)

class BlogPostAdmin(admin.ModelAdmin):
    exclude = ('image',)
    list_display = ('title', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'excerpt', 'body')

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
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(resources, ResourcesAdmin)
admin.site.register(employees, EmployeesAdmin)
admin.site.register(partners, PartnersAdmin)
admin.site.register(gallery, GalleryAdmin)
admin.site.register(ImpactMetric, ImpactMetricAdmin)
admin.site.register(FeaturedPerson, FeaturedPersonAdmin)
admin.site.register(SuccessStory, SuccessStoryAdmin)
admin.site.register(InspirationVideo, InspirationVideoAdmin)
admin.site.register(PageMedia, PageMediaAdmin)
