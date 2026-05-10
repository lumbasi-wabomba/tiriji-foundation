from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('children/', views.children, name='children'),
    path('women/', views.women, name='women'),
    path('volunteer/', views.volunteer, name='volunteer'),
    path('programs/', views.programs, name='programs'),
    path('programs/<int:program_id>/', views.program_detail, name='program_detail'),
    path('volunteer/signup/', views.volunteer_signup, name='volunteer_signup'),
    path('donate/', views.donate, name='donate'),
    path('events/', views.events, name='events'),
    path('news/', views.news, name='news'),
    path('resources/', views.resources, name='resources'),
    path('faq/', views.faq, name='faq'),
    path('gallery/', views.gallery, name='gallery'),
    path('team/', views.team, name='team'), 
    path('partners/', views.partners, name='partners'),
    path('blog/', views.blog, name='blog'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('careers/', views.careers, name='careers'),
    path('careers/<int:career_id>/', views.career_detail, name='career_detail'),
    path('donate/success/', views.donate_success, name='donate_success'),
    path('feedback/', views.feedback, name='feedback'),

    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('admin-portal/', views.admin_portal, name='admin_portal'),
    path('admin-portal/programs/', views.admin_programs, name='admin_programs'),
    path('admin-portal/programs/add/', views.admin_program_add, name='admin_program_add'),
    path('admin-portal/programs/<int:program_id>/edit/', views.admin_program_edit, name='admin_program_edit'),
    path('admin-portal/programs/<int:program_id>/delete/', views.admin_program_delete, name='admin_program_delete'),

    path('admin-portal/events/', views.admin_events, name='admin_events'),
    path('admin-portal/events/add/', views.admin_event_add, name='admin_event_add'),
    path('admin-portal/events/<int:event_id>/edit/', views.admin_event_edit, name='admin_event_edit'),
    path('admin-portal/events/<int:event_id>/delete/', views.admin_event_delete, name='admin_event_delete'),

    path('admin-portal/news/', views.admin_news, name='admin_news'),
    path('admin-portal/news/add/', views.admin_news_add, name='admin_news_add'),
    path('admin-portal/news/<int:news_id>/edit/', views.admin_news_edit, name='admin_news_edit'),
    path('admin-portal/news/<int:news_id>/delete/', views.admin_news_delete, name='admin_news_delete'),

    path('admin-portal/resources/', views.admin_resources, name='admin_resources'),
    path('admin-portal/resources/add/', views.admin_resource_add, name='admin_resource_add'),
    path('admin-portal/resources/<int:resource_id>/edit/', views.admin_resource_edit, name='admin_resource_edit'),
    path('admin-portal/resources/<int:resource_id>/delete/', views.admin_resource_delete, name='admin_resource_delete'),

    #path('feedback/success/', views.feedback_success, name='feedback_success'), 
]
